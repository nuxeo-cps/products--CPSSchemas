# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Testing.ZopeTestCase import ZopeLite

from Products.CPSDocument.Schema import CPSSchema
from Products.CPSDocument.AttributeStorageAdapter import \
    AttributeStorageAdapterFactory
from Products.CPSDocument.Fields.TextField import TextField

class AttributeHolder:
    pass


class SchemaTests(unittest.TestCase):

    def testCreation(self):
        # Check that the schems sets up reasonable defaults
        schema = CPSSchema('schema', 'Schema')
        self.assert_(
            isinstance(schema.getStorageAdapterFactory(), 
                       AttributeStorageAdapterFactory),
            'Default adapter is not AttributeAdapter')

    def testSetGetAdapter(self):
        schema = CPSSchema('schema', 'Schema')
        adapter = AttributeStorageAdapterFactory()
        schema.setStorageAdapterFactory(adapter)
        self.assertEquals(schema.getStorageAdapterFactory(), adapter,
            'Set or get adapter failed')


def test_suite():
    return unittest.makeSuite(SchemaTests)

if __name__=="__main__":
    unittest.main(defaultTest)
