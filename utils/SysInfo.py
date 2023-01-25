class InfoCache:
    importErrors: list[Exception] = []

    @staticmethod
    def getImportErrors() -> list[Exception]:
        return InfoCache.importErrors
