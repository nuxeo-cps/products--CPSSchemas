# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Products.NuxCPS3Document.Schema import Schema
from Products.NuxCPS3Document.AttributeStorageAdapter import AttributeStorageAdapterFactory
from Products.NuxCPS3Document.Fields.TextField import TextField

class AttributeHolder:
    pass


class SchemaTests(unittest.TestCase):

    def testCreation(self):
        """Check that the schems sets up reasonable defaults"""
        schema = Schema('schema', 'Schema')
        self.failUnless(isinstance(schema.getStorageAdapterFactory(), AttributeStorageAdapterFactory), \
                        'Default adapter is not AttributeAdapter')

    def testSetGetAdapter(self):
        schema = Schema('schema', 'Schema')
        adapter = AttributeStorageAdapterFactory()
        schema.setStorageAdapterFactory(adapter)
        self.failUnless(schema.getStorageAdapterFactory() == adapter, 'Set or get adapter failed')

    #def testgetAllData(def):
    #   """Tests data retrieval"""
    #def testgetAllData(def):
    #   """Tests data retrieval"""

def test_suite():
    return unittest.makeSuite(SchemaTests)

if __name__=="__main__":
    unittest.main(defaultTest)
