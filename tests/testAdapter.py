# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Products.NuxCPS3Document.AttributeStorageAdapter import AttributeStorageAdapter
from Products.NuxCPS3Document.Fields.TextField import TextField
from Products.NuxCPS3Document.Fields.SelectionField import SelectionField


class AttributeHolder:
    pass



class AttributeAdapterTests(unittest.TestCase):

    def setUp(self):
        self.h = AttributeHolder()
        f1 = TextField('f1', 'Field1')
        f2 = TextField('f2', 'Field2')
        f3 = SelectionField('f3', 'Field3')
        f3.setOptions( ['Value1', 'Value2', 'Value3'])
        f3.setDefaultValue('Value3')
        fielddict = {}
        fielddict['f1'] = f1
        fielddict['f2'] = f2
        fielddict['f3'] = f3
        self.a = AttributeStorageAdapter(self.h, fielddict)


    def testSet(self):
        """Set Data"""
        self.a.set('f1', 'value')
        self.failUnless(self.h.f1 == 'value', 'Set failed')

    def testGet(self):
        """Get Data"""
        self.a.set('f1', 'value')
        self.failUnless(self.a.get('f1') == 'value', 'Get failed')
        self.failUnlessRaises(KeyError, self.a.get, 'nodata')

    def testDel(self):
        """Delete Data"""
        self.a.set('f1', 'value')
        self.a.delete('f1')
        self.failUnlessRaises(AttributeError, getattr, self.a, 'data')

    def testHas(self):
        """Has Data"""
        self.a.set('f1', 'value')
        self.failUnless(self.a.has_data('f1'), 'HasData failed')
        self.a.delete('f1')
        self.failIf(self.a.has_data('f1'), 'HasData failed')

    def testReadWriteData(self):
        self.failUnless(self.a.readData() == {'f1': None, 'f2': None, 'f3': None})
        self.a.writeData({'f1': 'Value1', 'f2': 'Value2', 'f3': None})
        self.failUnless(self.a.readData() == {'f1': 'Value1', 'f2': 'Value2', 'f3': None})



def test_suite():
    return unittest.makeSuite(AttributeAdapterTests)

if __name__=="__main__":
    unittest.main(defaultTest)
