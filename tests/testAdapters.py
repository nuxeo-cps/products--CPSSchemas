# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
import CPSSchemasTestCase

from Products.CPSSchemas.StorageAdapter import AttributeStorageAdapter
from Products.CPSSchemas.Schema import CPSSchema

from testdata import metadata_schema

class FakeDocument:
    pass

class TestStorageAdapter(CPSSchemasTestCase.CPSSchemasTestCase):
    def afterSetUp(self):
        stool = self.portal.portal_schemas
        stool.manage_delObjects(ids=list(stool.objectIds()))
        self.schema = stool.manage_addCPSSchema('metadata')
        for field_id, field_info in metadata_schema.items():
            self.schema.manage_addField(
                field_id, field_info['type'], **field_info['data'])
        self.document = FakeDocument()


class TestAttributeStorageAdapter(TestStorageAdapter):
    def afterSetUp(self):
        TestStorageAdapter.afterSetUp(self)
        self.adapter = AttributeStorageAdapter(self.schema, self.document)

    def testAccessors(self):
        reference_field_ids = ['Subject', 'Creator', 'CreationDate',
            'ModificationDate', 'ExpirationDate', 'Format', 'Contributors',
            'EffectiveDate', 'Rights', 'Language', 'Description', 'Title']
        reference_field_ids.sort()
        field_ids = [item[0] for item in self.adapter.getFieldItems()]
        field_ids.sort()
        self.assertEquals(field_ids, reference_field_ids)

        reference_writable_field_ids = ['Subject', 'ExpirationDate',
            'Contributors', 'EffectiveDate', 'Rights', 'Description', 'Title']
        reference_writable_field_ids.sort()
        writable_field_ids = [
            item[0] for item in self.adapter.getWritableFieldItems()]
        writable_field_ids.sort()
        self.assertEquals(writable_field_ids, reference_writable_field_ids)

        default_data = {'Subject': [], 'Creator': '', 'CreationDate': None,
            'ModificationDate': None, 'ExpirationDate': None, 'Format': '',
            'Contributors': [], 'EffectiveDate': None, 'Rights': '', 
            'Language': '', 'Description': '', 'Title': ''}
        self.assertEquals(self.adapter.getDefaultData(), default_data)
        self.assertEquals(self.adapter.getData(), default_data)

    def testMutators(self):
        data = {}
        for item in self.adapter.getWritableFieldItems():
            data[item[0]] = 'YYY'
        self.adapter.setData(data)
        for attr_name in data.keys():
            self.assertEquals(getattr(self.document, attr_name), 'YYY')


class TestMetadataStorageAdapter(TestStorageAdapter):
    def afterSetUp(self):
        TestStorageAdapter.afterSetUp(self)
        self.adapter = MetadataStorageAdapter(self.schema, self.document)

    def testAccessors(self):
        # TODO: Later
        pass

    def testMutators(self):
        # TODO: Later
        pass


def test_suite():
    suites = [unittest.makeSuite(TestAttributeStorageAdapter)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
