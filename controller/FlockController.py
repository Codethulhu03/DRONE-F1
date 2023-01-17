from communication.Command import Command
from communication.CommandData import CommandData
from compatibility.Bisect import insort
from compatibility.Itertools import combinations
from compatibility.Typing import Any, List, Union
from compatibility.Math import exp, acos, sin
from controller.Controller import Controller
from drone.DroneData import DroneData
from drone.PartialDroneData import PartialDroneData
from utils.ConfigurationData import ConfigurationData
from utils.Logger import Logger
from utils.events.EventDecorators import evaluate, process
from utils.events.EventType import EventType
from utils.events.Mediator import Mediator
from utils.math.Vector import Vector3


class FlockController(Controller):
    """ Controller class for flocking/collision avoidance """
    
    ARGS: dict[str, Any] = {**Controller.ARGS,
            "flockGroup"         : 1,
            "filterSimilarity"   : True,
            "membersFilter"      : True,
            "UAVMaxSpeed"        : 2.0,
            "PositionTolerance"  : 1.0,
            "flockArea"          : 200.0,
            "similarityThreshold": 25,
            "membersLimit"       : 2,
            "ownVelocityWeight"  : 0.5,
            "flockDistance"      : 8.6,
            "flockHysteresis"    : 0.0,
            "flockMinDistance"   : 5.0,
            "flockMaxDistance"   : 12.2,
            "potFieldWidth"      : 20.0,
            "flightStep"         : 10.0,
            }
    """ Arguments for the configuration file """
    
    def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData):
        """
        Constructor of the FlockController class
        
        :param mediator: Mediator instance for event handling
        :param logger: Logger instance
        :param configData: ConfigurationData of loaded config file
        """
        super().__init__(mediator, logger, configData)
        
        self.__filterSimilarity: bool = configData.ownArguments["filterSimilarity"]
        self.__membersFilter: bool = configData.ownArguments["membersFilter"]
        self.__flockArea: float = configData.ownArguments["flockArea"]
        self.__uavSpeedMax: float = configData.ownArguments["UAVMaxSpeed"]
        self.__similarityThreshold: float = configData.ownArguments["similarityThreshold"]
        self.__membersLimit: int = configData.ownArguments["membersLimit"]
        self.__ownVelWeight: float = configData.ownArguments["ownVelocityWeight"]
        self.__flockWeightRange: float = 1 - self.__ownVelWeight
        self.__flockDistance: float = configData.ownArguments["flockDistance"]
        self.__flockHysteresis: float = configData.ownArguments["flockHysteresis"]
        self.__flockMinDistance: float = configData.ownArguments["flockMinDistance"]
        self.__flockMaxDistance: float = configData.ownArguments["flockMaxDistance"]
        self.__positionTolerance: float = configData.ownArguments["PositionTolerance"]
        self.__potFieldWidth: float = configData.ownArguments["potFieldWidth"]
        self.__flightStep: float = configData.ownArguments["flightStep"]
        self.__flockGroup: int = configData.ownArguments["flockGroup"]
        
        self.__members: List[DroneData] = []
        self.__membersForces: List[Vector3] = []
        self.__flockSpeed: float = 0
        self.__vfTarget: Vector3 = Vector3()
        self.__vfFlock: Vector3 = Vector3()
        self.__vfFlockVel: Vector3 = Vector3()
        self.__vfOwnVel: Vector3 = Vector3()
        self.__vfTotal: Vector3 = Vector3()
        self.__vNewPos: Vector3 = Vector3()
        self.__minDistFlock: float = 1000
        self.__maxDistFlock: float = -1000

        self.__oldData: dict[int, PartialDroneData] = {}

    def buildFlock(self):
        """
        Create the flock
        """
        self.__members.clear()
        for neighbour in self._data.neighbours.values():
            if (neighbour["flockGroup"] == self.__flockGroup
                    and self.getVectorToNeighbour(neighbour).magnitude < self.__flockArea):
                insort(self.__members, neighbour, key=lambda x: self.getVectorToNeighbour(x).magnitude)
        if not self.__membersFilter or len(self.__members) <= 2:
            return
        elif self.__filterSimilarity:
            while True:
                for m, n in combinations(self.__members, 2):
                    nedI: Vector3 = self.getVectorToNeighbour(m)
                    nedJ: Vector3 = self.getVectorToNeighbour(n)
                    if nedI.similarity(nedJ) > self.__similarityThreshold:
                        self.__members.remove(m if nedI.magnitude > nedJ.magnitude else n)
                        break
                else:
                    break
        self.__members = self.__members[:self.__membersLimit] # list is sorted for now, but might not be later if flock is moving
    
    def getVectorToNeighbour(self, neighbour: Union[DroneData, dict]) -> Vector3:
        """
        Returns the vector from the current drone to the neighbour drone
        
        :param neighbour: neighbour drone data
        
        :return: A vector from the drone to the neighbour
        """
        return self._data.position - neighbour.get("position", Vector3())
    
    def minMaxDstUpdate(self):
        """
        Updates the min and max distances of the drone to the flock
        """
        self.__minDistFlock = 1000
        self.__maxDistFlock = -1000
        for member in self.__members: # might not be sorted anymore if flock is moving
            dst: float = self.getVectorToNeighbour(member).magnitude
            self.__minDistFlock = min(dst, self.__minDistFlock)
            self.__maxDistFlock = max(dst, self.__maxDistFlock)
    
    def flyFlock(self, goal: Vector3) -> tuple[Vector3, float]:
        """
        Calculates the velocity vector for the flocking algorithm
        
        :param goal: The goal position of the flock
        :return: The velocity vector and the speed
        """
        self.__clearFlockVar()
        vectorToGoal: Vector3 = self._data.position - goal
        position: Vector3 = self._data.position
        velocityNed: Vector3 = self._data.velocity
        vfFlock, flockWeight = self.getFlockForce(position, velocityNed)
        targetWeight: float = 1 - flockWeight
        vfTarget: Vector3 = self.calcPotField(goal, vectorToGoal)
        vfOwnVel: Vector3 = velocityNed
        
        # CALCULATE TOTAL FORCE DIRECTION ( D = Kc*(fw*F+tw*T)+Kp*V)
        ownVelWeight: float = self.__ownVelWeight
        tarFlockWeight: float = 1 - ownVelWeight
        simFlock2Target: float = vfFlock.similarity(vfTarget)
        vfFlockD: Vector3 = vfFlock
        self.__flockSpeed = abs(self.__uavSpeedMax)
        if simFlock2Target < 0 < vfTarget.magnitude:
            vfFlockD -= vfFlock.projectOn(vfTarget)
            self.__flockSpeed *= abs(1 + simFlock2Target)
        
        vfFlockD = vfFlockD.normalize()
        self.__vfFlock = vfFlockD * (flockWeight * tarFlockWeight)
        self.__vfTarget = vfTarget * (targetWeight * tarFlockWeight)
        self.__vfOwnVel = vfOwnVel.normalize() * ownVelWeight
        # self.__vfTotal = (self.__vfTarget + self.__vfFlock) * tarFlockWeight + self.__vfOwnVel
        self.__vfTotal = (self.__vfTarget + self.__vfFlock) + self.__vfOwnVel
        self.__vNewPos = self.calcNewPosition(self.__vfTotal, position)
        return self.__vNewPos, self.__flockSpeed

    def getFlockForce(self) -> tuple[Vector3, float]:  # dst_mag < (b-tolerance)
        """
        Calculates the flock force vector
        
        :return: The flock force vector and the flock weight
        """
        vfFlock: Vector3 = Vector3()
        vMemberForceRep: list[Vector3] = []
        vMemberForceAtt: list[Vector3] = []
        self.__membersForces.clear()
        for m in self.__members:
            (v_member_force, force_type) = self.getSigmoidForce(self.getVectorToNeighbour(m))
            if force_type == "att":
                vMemberForceAtt.append(v_member_force)
            elif force_type == "rep":
                vMemberForceRep.append(v_member_force)
            else:
                continue
            vfFlock += v_member_force
            self.__membersForces.append(v_member_force)
        return vfFlock, self.getFlockWeight(self.__membersForces, vMemberForceRep, vMemberForceAtt)
    
    def getFlockWeight(self, membersForces: List[Vector3], repForces: List[Vector3], attForces: List[Vector3]) -> float:
        """
        Calculates the flock weight
        
        * repForces is subset of membersForces
        * attForces is subset of membersForces
        * repForces + attForces = membersForces
        * repForces and attr_forces are disjoint
        
        :param membersForces: The forces of the flock members
        :param repForces: The repulsive forces of the flock members
        :param attForces: The attractive forces of the flock members
        :return:
        """
        if not membersForces:
            return 0.0
        # Option 1  all members Forces
        # average force * flockWeightRange
        weight_1: float = self.__flockWeightRange * sum(map(lambda x: x.magnitude, membersForces),
                                                        Vector3()) / len(membersForces)
        # Option 2 repForces
        # average repulsive force
        weight_2: float = sum(map(lambda x: x.magnitude, repForces), Vector3()) / min(1, len(repForces))
        # Option 3 attForces
        # average attractive force
        weight_3: float = sum(map(lambda x: x.magnitude, attForces), Vector3()) / min(1, len(attForces))
        """ Old code -- but why?
        weight_3 = 0.60 * weight_2 + 0.40 * weight_3    # weight_3 is never used??  ~ Lars
        weight = weight_1                               # Actually only weight_1 is used lol ~ Fishboy
        """
        # slightly more weight to repulsive forces
        # return (weight_1 + 0.60 * weight_2 + 0.40 * weight_3) / 2.0  # I added this: code might be wrong ~ Fishboy
        return weight_1
    
    def getSigmoidForce(self, vDistToMember: Vector3) -> tuple[Vector3, str]:
        """
        Calculates the sigmoid force vector
        
        :param vDistToMember: The distance vector to the flock member
        :return: The sigmoid force vector and the force type
        """
        # f_s=2(1/(1+e^(-a(x-b))-0.5), where "b" is the intersection with x axis and "a" the gradient
        idealDistance: float = self.__flockDistance
        hysteresis: float = self.__flockHysteresis
        minDist: float = self.__flockMinDistance
        maxDist: float = self.__flockMaxDistance
        distToMember: float = vDistToMember.magnitude
        uDistToMember: Vector3 = vDistToMember.normalize()
        b: float = idealDistance - hysteresis
        a: float = 4.
        if distToMember < b:  # Repulsion
            forceType: str = "rep"
            a /= minDist
        elif distToMember > idealDistance + hysteresis:
            forceType: str = "att"  # attraction
            a /= maxDist
        else:
            return Vector3(), "none"
        return uDistToMember * (2 * ((1 / (1 + exp(-a * (distToMember - b)))) - 0.5)), forceType
    
    def getFlockVelForce(self, velocity: Vector3) -> Vector3:
        """
        Calculates the flock velocity force vector

        :param velocity: The velocity vector of the flock
        :return: The flock velocity force vector
        """
        return velocity + sum(map(lambda x: x["velocity"].normalize(), self.__members), Vector3())
    
    def calcPotField(self, goal, vTarget) -> Vector3:
        """
        Calculates the potential field vector
        
        :param goal: The goal position
        :param vTarget: The target position
        :return: The potential field vector
        """
        if vTarget.magnitude < self.__positionTolerance:
            return Vector3()
        line_vec = sum(map(lambda m: goal - m.position, self.__members), Vector3())
        return line_vec.normalize() if (
                vTarget.magnitude * sin(acos(line_vec.similarity(vTarget))) < self.__potFieldWidth
            ) else vTarget.normalize()

    def calcNewPosition(self, vfTotal: Vector3, position: Vector3) -> Vector3:
        """
        Calculates the new position vector
        
        :param vfTotal: The total force vector
        :param position: The position vector
        :return: The new position vector
        """
        return (vfTotal.normalize() * self.__flightStep) + position
    
    def __clearFlockVar(self):
        """ Clears the flock variables """
        self.__flockSpeed = 0
        self.__vfTarget = Vector3()
        self.__vfFlock = Vector3()
        self.__vfFlockVel = Vector3()
        self.__vfTotal = Vector3()
    
    def calculateVelocity2(self, vfFlock, vfTarget, vfOwnVel) -> Vector3:
        """
        Calculates the velocity vector
        
        :param vfFlock: The flock force vector
        :param vfTarget: The target force vector
        :param vfOwnVel: The own velocity force vector
        :return: The velocity vector
        """
        mfTarget: float = vfTarget.magnitude
        if vfFlock.similarity(vfTarget) < 0 < mfTarget:
            mfFlock: float = vfFlock.magnitude
            cond: bool = mfFlock < mfTarget
            speed: float = ((self.__uavSpeedMax * (1 - mfFlock)) * cond) + (not cond)
            # vfFlock = vfFlock - vfFlock.projectOn(vfTarget)
        else:
            speed: float = self.__uavSpeedMax
        return (speed + vfOwnVel.magnitude) / 2


    # VV Decorator for event-handling if applicable VV
    # @process(EventType.***)
    @process(EventType.DRONE_DATA_UPDATE)
    @evaluate(EventType.COMMAND_CHANGE_COURSE)
    def doStuff(self, data: PartialDroneData) -> CommandData:
        cond: bool = "neighbours" in data and str(data["neighbours"]) != str(self.__oldData)
        """ condition to prevent infinite 'recursion' ~ Fishboy """
        if not cond:
            return None

        self.__oldData = data["neighbours"]
        for neighbour in data["neighbours"].values():
            if (neighbour["position"] - self._data["position"]).magnitude < self.__flockMaxDistance:
                # distanz des nachbarn im flock bereich
                self._logger.print(f"Flock: neighbour-ids in flock range: {neighbour['id']}")

        newPosition: Vector3 = Vector3()
        """ New position to go to """
        speed: float = 1.0
        """ Speed to go at (might need to be magnitude of Vector)"""
        self._logger.print(f"Neighbours: {data['neighbours']}")
        # VV Your code below VV
        # self.buildFlock()
        # newPosition, speed = self.flyFlock()
        # ^^ Your code above ^^

        # return CommandData(cmd=Command.CHANGE_COURSE, msg={"target": newPosition, "speed": speed})
        return None

    # Method for interval-based calls (e.g. every second)
    def _asyncProcess(self):
        # self.doStuff()
        pass
