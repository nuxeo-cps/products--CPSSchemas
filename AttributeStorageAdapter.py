# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

from DataStructure import DataStructure
from BasicStorageAdapter import BasicStorageAdapter

class AttributeStorageAdapter(BasicStorageAdapter):

    def __init__(self, document, fields, namespace=''):
        BasicStorageAdapter.__init__(self, document, fields, namespace)
        if namespace:
            self._namespace = namespace + '_'
        else:
            self._namespace = ''

    def set(self, field_id, data):
        fsid = self._namespace + self.getFieldStorageId(field_id)
        setattr(self._document, fsid, data)

    def get(self, field_id):
        fsid = self._namespace + self.getFieldStorageId(field_id)
        return getattr(self._document, fsid, None)

    def delete(self, field_id):
        fsid = self._namespace + self.getFieldStorageId(field_id)
        delattr(self._document, fsid)


class AttributeStorageAdapterFactory:
    """The AdapterFactory creates StorageAdapters

    The Factory contains all settings used by the StorageAdapters. The
    AttributeStorage uses no settings at all. And the Factory is therefore
    only one method: the factory method.
    """

    def makeStorageAdapter(self, document, fields, namespace=''):
        return AttributeStorageAdapter(document, fields, namespace)


