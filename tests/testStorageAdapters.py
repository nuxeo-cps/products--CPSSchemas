# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Testing.ZopeTestCase import ZopeLite

from Products.CPSDocument.BasicStorageAdapter import BasicStorageAdapter
from Products.CPSDocument.AttributeStorageAdapter import AttributeStorageAdapter
from Products.CPSDocument.Fields.TextField import TextField
from Products.CPSDocument.Fields.SelectionField import SelectionField


class AttributeHolder:
    pass


class BasicStorageAdapterTests(unittest.TestCase):

    def testWithNoneDocument(self):
        """Tests that creation with no document loads defaults"""
        f1 = TextField('f1', 'Field1')
        f3 = SelectionField('f3', 'Field3')
        f3.setOptions( ['Value1', 'Value2', 'Value3'])
        f3.setDefaultValue('Value3')
        fielddict = {}
        fielddict['f1'] = f1
        fielddict['f3'] = f3
        a = BasicStorageAdapter(None, fielddict)
        self.failUnless(a.get('f1') == None)
        self.failUnless(a.get('f3') == 'Value3')

    def testPythonBehavior(self):
        """Make sure it really is the real references that are stored"""
        # Yes, python does behave like I expected it to. :)
        # I wrote these tests when I couldn't find a strange fault, to make
        # sure that Python behaved as I thought it did. And it did. These
        # tests are strictly not nessecary, but I like keeping tests around.
        # Of course, it's quite unlikely that Python ever changes this behaviour. :)
        f1 = TextField('f1', 'Field1')
        f3 = SelectionField('f3', 'Field3')
        f3.setOptions( ['Value1', 'Value2', 'Value3'])
        f3.setDefaultValue('Value3')
        fielddict = {}
        fielddict['f1'] = f1
        fielddict['f3'] = f3
        a = BasicStorageAdapter(None, fielddict)
        self.failUnless(a._fields['f1'] is f1)
        self.failUnless(a._fields['f3'].getDefaultValue() == 'Value3')


class AttributeAdapterTests(unittest.TestCase):

    # These tests tests the specific behaviour of the AttributeStorageAdapter
    # It therefore looks and changes directly with the attributes on the
    # AttributeHolder object
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
        self.h.f1 = 'value'
        self.failUnless(self.a.get('f1') == 'value', 'Get failed')
        self.failUnlessRaises(KeyError, self.a.get, 'nodata')

    def testGetWithDefaults(self):
        """Get with default"""
        self.failUnless(self.a.get('f3') == 'Value3')

    def testDel(self):
        """Delete Data"""
        self.h.f1 = 'value'
        self.a.delete('f1')
        self.failUnlessRaises(AttributeError, getattr, self.a, 'data')

    def testHas(self):
        """Has Data"""
        self.h.f1 = 'value'
        self.failUnless(self.a.has_data('f1'), 'HasData failed')
        del self.h.f1
        self.failIf(self.a.has_data('f1'), 'HasData failed')

    def testReadWriteData(self):
        """Get and set with a dict"""
        self.failUnless(self.a.readData() == {'f1': None, 'f2': None, 'f3': 'Value3'})
        self.a.writeData({'f1': 'Value1', 'f2': 'Value2', 'f3': None})
        self.failUnless(self.a.readData() == {'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'})

    def testNameSpace(self):
        self.a._namespace = 'Lespacedenom'
        self.a.set('f1', 'datadata')
        self.failUnless(hasattr(self.h, 'Lespacedenom_f1'))


def test_suite():
    tests = [unittest.makeSuite(BasicStorageAdapterTests),
             unittest.makeSuite(AttributeAdapterTests)]
    return unittest.TestSuite( tests)

if __name__=="__main__":
    unittest.main(defaultTest)
