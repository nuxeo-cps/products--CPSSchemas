# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

from OrderedDictionary import OrderedDictionary
from AttributeStorageAdapter import AttributeStorageAdapterFactory

class Schema(OrderedDictionary):
    """Defines fields used in a document"""

    # It doesn't really have to be ordered, I think a pure
    # PersistentMapping would work. But then again, it can't hurt...

    def __init__(self, id, title, adapter=None):
        OrderedDictionary.__init__(self)
        self.id = id
        self.title = title
        if not adapter:
            self._adapter = AttributeStorageAdapterFactory()
        self._namespace = ''

    def setStorageAdapterFactory(self, adapter):
        self._adapter = adapter

    def getStorageAdapterFactory(self):
        return self._adapter

    def makeStorageAdapter(self, document):
        return self._adapter.makeStorageAdapter(document, \
                                 self.getFieldDictionary, self._namespace)

    def setNamespace(self, namespace):
        self._namespace = namespace

    def getNamespace(self):
        return self._namespace

    def getFieldStorageId(self, fieldid):
        if self._namespace:
            ns = self._namespace + '_'
        else:
            ns = ''
        return ns + self[fieldid].getStorageId()

    def getFieldDictionary(self):
        """Returns all the fields as a dictionary"""
        return self.data
