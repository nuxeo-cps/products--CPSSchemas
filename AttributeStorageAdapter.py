# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

from Products.CPSDocument.DataStructure import DataStructure
from Products.CPSDocument.BasicStorageAdapter import BasicStorageAdapter

class AttributeStorageAdapter(BasicStorageAdapter):

    def __init__(self, document, fields, namespace=''):
        BasicStorageAdapter.__init__(self, document, fields, namespace)
        if namespace:
            self._namespace = namespace
        else:
            self._namespace = ''

    def _set(self, field, data):
        if self._namespace:
            fsid = self._namespace + '_' + field.getStorageId()
        else:
            fsid = field.getStorageId()
        setattr(self._document, fsid, data)

    def _get(self, field):
        if self._namespace:
            fsid = self._namespace + '_' + field.getStorageId()
        else:
            fsid = field.getStorageId()
        data = getattr(self._document, fsid, None)
        if data is None:
            if field.isRequired():
                return field.getDefaultValue()
        return data

    def _delete(self, field):
        if self._namespace:
            fsid = self._namespace + '_' + field.getStorageId()
        else:
            fsid = field.getStorageId()
        if hasattr(self._document, fsid):
            delattr(self._document, fsid)


class AttributeStorageAdapterFactory:
    """The AdapterFactory creates StorageAdapters

    The Factory contains all settings used by the StorageAdapters. The
    AttributeStorage uses no settings at all. And the Factory is therefore
    only one method: the factory method.
    """

    def makeStorageAdapter(self, document, fields, namespace=''):
        return AttributeStorageAdapter(document, fields, namespace)


