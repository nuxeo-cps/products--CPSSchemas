import Persistence
from ExtensionClass import Base
from Acquisition import Implicit

class BasicStorage(Base, Persistence.Persistent, Implicit):
    """A small storage for storing things persistently in ZODB

    It's just a persistent object with a generic interface for setting data.
    Other objects with the same interface can then be used to store the data
    somewhere else, like in a RDBMS, or perhaps making in-memory objects that
    store data intermittently, to reduce the number of ZODB commits needed.
    """

    def setData(self, name, data):
        setattr(self, name, data)

    def getData(self, name):
        return getattr(self, name)

    def delData(self, name):
        delattr(self, name)
