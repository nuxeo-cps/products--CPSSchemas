# Copyright (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Testing.ZopeTestCase import ZopeLite

from Products.CPSSchemas.DataModel import DataModel, ValidationError
from Products.CPSSchemas.StorageAdapter import BaseStorageAdapter
from Products.CPSSchemas.Schema import CPSSchema
from Products.CPSSchemas.BasicFields import CPSStringField
#from Products.CPSSchemas.Schema import Schema
#from Products.CPSSchemas.Fields.TextField import TextField
#from Products.CPSSchemas.Fields.SelectionField import SelectionField

class FakeDocument:
    f1 = CPSStringField('f1')
    f2 = CPSStringField('f2')
    f3 = CPSStringField('f3')
    _fields = {'f1': f1, 'f2': f2, 'f3': f3}
    schema = CPSSchema('s1', 'Schema1')
    for field_id, field in _fields.items():
        schema.addField(field_id, field.meta_type)
    adapter = BaseStorageAdapter(schema, _fields.keys())
    

# XXX: All these tests must be repared.
class TestDataModel(unittest.TestCase):

    def xxxsetUp(self):
        self.s1 = Schema('s1', 'Schema1')
        self.s1['f1'] = TextField('f1', 'Field1')
        f2 = TextField('f2', 'Field2')
        f2.setDefaultValue('Value2')
        self.s1['f2'] = f2
        f3 = SelectionField('f3', 'Field3')
        f3.setOptions(('Value1', 'Value5', 'Value3'))
        self.s1['f3'] = f3
        self.s2 = Schema('s2', 'Schema2')
        self.s2['f4'] = TextField('f4', 'Field4')
        f5 = SelectionField('f5', 'Field5')
        f5.setOptions(('Value1', 'Value5', 'Value3'))
        f5.setNotRequired()
        self.s2['f5'] = f5
        self.s2['f6'] = TextField('f6', 'Field6')
        self.dm = DataModel((self.s1, self.s2), None)

    def test1(self):
        dm = DataModel(FakeDocument())

    def testDirtyFields(self):
        """Test the dirty_fields_map attribute of the DataModel"""
        doc = FakeDocument()
        dm = DataModel(doc, (doc.adapter,))
        field_ids = ('f1', 'f3')
        for field_id in field_ids:
            dm[field_id] = 'XXX'

        # Test that after setting values in the datamodel,
        # each field is marked as dirty.
        for field_id in dm.keys():
            dirty = not not dm.isDirty(field_id)
            self.assertEquals(dirty, field_id in field_ids)

    def _testFieldIds(self):
        fields = self.dm.getFieldIds()
        fields.sort()
        self.failUnless(fields == ['f1', 'f2', 'f3', 'f4', 'f5', 'f6'])

    def _testSchemaIds(self):
        schemas = self.dm.getSchemaIds()
        schemas.sort()
        self.failUnless(schemas == ['s1', 's2'])

    def _testFindSchema(self):
        self.failUnless(self.dm.getSchemaId('f2') == 's1')
        self.failUnlessRaises(KeyError, self.dm.getSchemaId, 'f9')

    def _testGetSchema(self):
        self.failUnless(self.dm.getSchema('s2').id == 's2')

    def _testGetField(self):
        field = self.dm.getField('f5')
        self.failUnless(field.id == 'f5')
        field = self.dm.getField('f2')
        self.failUnless(isinstance(field, TextField))
        field = self.dm.getField('f2')

    def _testAccessData(self):
        self.failUnless(self.dm['f2'] == 'Value2', 
            'Default value not used when use with no document')

    def _testInitwithDoc(self):
        doc = FakeDocument()
        doc.f1 = 'Value1'
        doc.f5 = 'Value5'
        dm = DataModel((self.s1, self.s2), doc)
        self.failUnless(dm['f1'] == 'Value1')
        self.failUnless(dm['f2'] == 'Value2',   
            'Default value not used when loading from document')
        self.failUnless(dm['f5'] == 'Value5')

    def _testSetInvalidData(self):
        self.failUnlessRaises(ValueError, self.dm.__setitem__, 'f5', 'invalid')
        self.failUnlessRaises(ValueError, self.dm.update, {'f5': 'invalid'})

    def _testMakeDataStructure(self):
        doc = FakeDocument()
        dm = DataModel((self.s1, self.s2), doc)
        ds = dm.makeDataStructure()
        self.failUnless(ds['f1'] is None)
        self.failUnless(ds['f2'] == 'Value2')

    def _testValidateDataStructure(self):
        doc = FakeDocument()
        doc.f1 = 'Value1'
        doc.f4 = 'Value4'
        dm = DataModel((self.s1, self.s2), doc)
        ds = dm.makeDataStructure()
        ds['f1'] = 'NewValue1'
        ds['f3'] = 'Value3'
        # DataStructure now has None as value for 'f6'. 'f6' is required, and
        # Validation should fail:
        self.failIf(dm.validateDataStructure(ds)) # Fail if DOES validate
        # Make sure 'f6' has the correct error:
        self.failUnless(str(ds.getError('f6')) == 'This field is required') # Fail if DOES validate
        ds ['f6'] = 'NewValue6'
        self.failIf(not dm.validateDataStructure(ds)) # Fail if DOES NOT validate

    def _testSavedata(self):
        doc = FakeDocument()
        doc.f1 = 'Value1'
        doc.f4 = 'Value4'
        dm = DataModel((self.s1, self.s2), doc)
        ds = dm.makeDataStructure()
        ds['f1'] = 'NewValue1'
        ds['f3'] = 'Value3'
        # f6 is empty, commit should fail
        self.failUnlessRaises(ValidationError, dm.commitDataStructure, ds)
        # Make sure nothing actually got updated
        self.failIf(doc.f1 == 'NewValue1')
        # Set f6 and commit should succeed
        ds['f6'] = 'NewValue6'
        self.failIf(dm.commitDataStructure(ds))
        # Make sure the document is updated
        self.failUnless(doc.f1 == 'NewValue1')
        self.failUnless(doc.f6 == 'NewValue6')



def test_suite():
    return unittest.makeSuite(TestDataModel)

if __name__=="__main__":
    unittest.main(defaultTest)
