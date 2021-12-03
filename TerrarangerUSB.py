from typing import Callable
from serial import Serial
from threading import Thread
    
## -inf = -1
## +inf = -2    

class TerraRanger:
    """
    This class serves as an example at how to convert the serial
    usb output into usable distance data.
    
    Args:
            port (str): The COM port the TerraRanger is connected to, eg: "COM4" or "/dev/ttyUSB0"
    """
    
    # Markers in the bytestream:    
    NEW_LINE = bytes.fromhex('0A')
    TABULATION = bytes.fromhex('09')
    CARRIAGE_RETURN = bytes.fromhex('0D')
    # Commands to the TerraRanger
    ACTIVATE_STREAMING = bytes.fromhex('00 52 02 01 DF')
    TEXT_MODE = bytes.fromhex('00 11 01 45')
    
    __running = False
    
    def __init__(self, port : str) -> None:
        
        self.__port = port
        
    def connect(self, callback : Callable):
        """Connect to the serial device with a given callback function.
        The callback function MUST accept a list as its first argument where the indexes 
        correspond to the sensor ID. If it exceeds the maximum distance -2 is passed, if its closer than the 
        minimal distance -1 is passed.

        Args:
            callback (Callable): The function you want to be called every time new data arrives.
        """
        self.__running = True
        # Create a serial device
        self.__device = Serial(port=self.__port, baudrate=115200)
        # Switch into correct mode
        self.__device.write(self.ACTIVATE_STREAMING)
        self.__device.write(self.TEXT_MODE)
        # Create listener Thread
        Thread(target=self.__run,args = [callback],daemon=True).start()

        
    def __run(self, callback : Callable):
        """Private function

        Args:
            callback (Callable): The passed callback
        """
        
        while self.__running:
            # Read the serial buffer:
            # !!! THE DATA CAN BECOME ASYNC WITH THIS METHOD IF NOT READ FAST ENOUGH !!!
            # To avoid this problem one might create a thread for every line of data
            line = self.__device.read_until(expected=self.NEW_LINE)
            # Prepare Data for use:
            values = line.split(self.TABULATION)
            values[-1] = values[-1].split(self.CARRIAGE_RETURN)[0]
            valuesInt = []
            for value in values[1:]:
                if value == b'+inf':
                    valuesInt.append(-2)
                elif value == b'-inf':
                    valuesInt.append(-1)
                else:
                    valuesInt.append(int.from_bytes(value))
            # Call the given Callback Method
            callback(valuesInt)   
            
        self.__device.close()
        
    def disconnect(self):
        """Terminate the serial connection, the callback wont be called anymore
        """
        self.__running = False
        

if __name__ == "__main__":

    def printData(lst : list):
        print(lst)


    terra = TerraRanger("COM9")
    terra.connect(callback=printData)
    input()
