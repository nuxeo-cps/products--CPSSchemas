# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Products.NuxCPS3Document.AttributeStorageAdapter import AttributeStorageAdapter
from Products.NuxCPS3Document.DataStructure import DataStructure
from Products.NuxCPS3Document.DataModel import DataModel
from Products.NuxCPS3Document.Schema import Schema
from Products.NuxCPS3Document.Fields.BasicField import BasicField
from Products.NuxCPS3Document.Fields.TextField import TextField
from Products.NuxCPS3Document.Fields.SelectionField import SelectionField


def makeDataModel():
    dm = DataModel()
    schema = Schema('schema', 'Schema')
    f1 = TextField('f1', 'Field1')
    f2 = TextField('f2', 'Field2')
    f3 = SelectionField('f3', 'Field3')
    f3.setOptions( ['Value1', 'Value2', 'Value3'])
    f3.setDefaultValue('Value3')
    schema['f1'] = f1
    schema['f2'] = f2
    schema['f3'] = f3
    dm.addSchema(schema)
    return dm

class AttributeHolder:
    pass



class AttributeAdapterTests(unittest.TestCase):

    def testSet(self):
        """Set Data"""
        h = AttributeHolder()
        a = AttributeStorageAdapter(h)
        a.set('data', 'value')
        self.failUnless(h.data == 'value', 'Set failed')

    def testGet(self):
        """Get Data"""
        h = AttributeHolder()
        a = AttributeStorageAdapter(h)
        a.set('data', 'value')
        self.failUnless(a.get('data') == 'value', 'Get failed')
        self.failUnless(a.get('nodata') is None, 'Get default failed')

    def testDel(self):
        """Delete Data"""
        h = AttributeHolder()
        a = AttributeStorageAdapter(h)
        a.set('data', 'value')
        a.del_key('data')
        self.failUnlessRaises(AttributeError, getattr, a, 'data')

    def testHas(self):
        """Has Data"""
        h = AttributeHolder()
        a = AttributeStorageAdapter(h)
        a.set('data', 'value')
        self.failUnless(a.has_key('data'), 'HasData failed')
        self.failIf(a.has_key('nodata'), 'HasData did not fail when it should')

    def testMakeStructure(self):
        """Tests the creation of a DataStructure"""
        h = AttributeHolder()
        a = AttributeStorageAdapter(h)
        h.f1 = 'Value1'
        h.f2 = 'Value2'
        h.f3 = 'Value3'
        dm = makeDataModel()
        ds = a.makeDataStructure(dm)
        self.failUnless( ds.data == {'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3' })

    def testWriteStructure(self):
        h = AttributeHolder()
        a = AttributeStorageAdapter(h)
        dm = makeDataModel()
        ds = a.makeDataStructure(dm)
        ds.update({'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3' })
        a.writeDataStructure(ds)
        self.failUnless( h.f1 == 'Value1' and h.f2 == 'Value2' and h.f3 == 'Value3')


def test_suite():
    return unittest.makeSuite(AttributeAdapterTests)

if __name__=="__main__":
    unittest.main(defaultTest)
