# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Products.NuxCPS3Document.DataModel import DataModel
from Products.NuxCPS3Document.Schema import Schema
from Products.NuxCPS3Document.Fields.TextField import TextField
from Products.NuxCPS3Document.Fields.SelectionField import SelectionField

class DataModelTests(unittest.TestCase):

    def setUp(self):
        self.dm = DataModel()
        s1 = Schema('s1', 'Schema1')
        s1['f1'] = TextField('f1', 'Field1')
        s1['f2'] = TextField('f2', 'Field2')
        s1['f3'] = SelectionField('f3', 'Field3')
        s2 = Schema('s2', 'Schema2')
        f2 = SelectionField('f2', 'Field2')
        f2.setOptions(('Value1', 'Value2', 'Value3'))
        f2.setNotRequired()
        s2['f2'] = f2
        s2['f3'] = TextField('f3', 'Field3')
        s2['f4'] = TextField('f4', 'Field4')
        self.dm.addSchema(s1)
        self.dm.addSchema(s2)

    def testFieldIds(self):
        fields = self.dm.getFieldIds()
        fields.sort()
        self.failUnless(fields == ['f1', 'f2', 'f3', 'f4'])

    def testSchemaIds(self):
        schemas = self.dm.getSchemaIds()
        schemas.sort()
        self.failUnless(schemas == ['s1', 's2'])

    def testFindSchema(self):
        self.failUnless('s1' in self.dm.getSchemasForFieldId('f2'))
        self.failUnless('s2' in self.dm.getSchemasForFieldId('f2'))
        self.failIf('s2' in self.dm.getSchemasForFieldId('f1'))
        self.failUnless(self.dm.getSchemasForFieldId('f5') == ())

    def testGetSchema(self):
        self.failUnless(self.dm.getSchema('s2').id == 's2')

    def testGetField(self):
        field = self.dm.getField('f1')
        self.failUnless(field.id == 'f1')
        field = self.dm.getField('f2')
        self.failUnless(field.id == 'f2')
        field = self.dm.getField('f2', 'Finbar')
        self.failUnless(isinstance(field, TextField))
        field = self.dm.getField('f2', None)
        self.failUnless(isinstance(field, SelectionField))
        self.failUnlessRaises(KeyError, self.dm.getField, 'f5')

def test_suite():
    return unittest.makeSuite(DataModelTests)

if __name__=="__main__":
    unittest.main(defaultTest)
