# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Products.NuxCPS3Document.DataModel import DataModel
from Products.NuxCPS3Document.Schema import Schema
from Products.NuxCPS3Document.Fields.TextField import TextField
from Products.NuxCPS3Document.Fields.SelectionField import SelectionField

class FakeDocument:
    pass

class DataModelTests(unittest.TestCase):

    def setUp(self):
        self.dm = DataModel(FakeDocument())
        s1 = Schema('s1', 'Schema1')
        s1['f1'] = TextField('f1', 'Field1')
        s1['f2'] = TextField('f2', 'Field2')
        s1['f3'] = SelectionField('f3', 'Field3')
        s2 = Schema('s2', 'Schema2')
        s2['f4'] = TextField('f4', 'Field4')
        f5 = SelectionField('f5', 'Field5')
        f5.setOptions(('Value1', 'Value5', 'Value3'))
        f5.setNotRequired()
        s2['f5'] = f5
        s2['f6'] = TextField('f6', 'Field6')
        self.dm.addSchema(s1)
        self.dm.addSchema(s2)

    def testFieldIds(self):
        fields = self.dm.getFieldIds()
        fields.sort()
        self.failUnless(fields == ['f1', 'f2', 'f3', 'f4', 'f5', 'f6'])

    def testSchemaIds(self):
        schemas = self.dm.getSchemaIds()
        schemas.sort()
        self.failUnless(schemas == ['s1', 's2'])

    def testFindSchema(self):
        self.failUnless(self.dm.getSchemaId('f2') == 's1')
        self.failUnlessRaises(KeyError, self.dm.getSchemaId, 'f9')

    def testGetSchema(self):
        self.failUnless(self.dm.getSchema('s2').id == 's2')

    def testGetField(self):
        field = self.dm.getField('f5')
        self.failUnless(field.id == 'f5')
        field = self.dm.getField('f2')
        self.failUnless(isinstance(field, TextField))
        field = self.dm.getField('f2')

def test_suite():
    return unittest.makeSuite(DataModelTests)

if __name__=="__main__":
    unittest.main(defaultTest)
