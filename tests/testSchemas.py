# Copyright (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
import CPSSchemasTestCase

from testdata import metadata_schema


class TestSchemas(CPSSchemasTestCase.CPSSchemasTestCase):

    def afterSetUp(self):
        self.tool = self.portal.portal_schemas

        # Delete widget types that has already been set up by the CPSDocument
        # installer.
        self.tool.manage_delObjects(ids=list(self.tool.objectIds()))

        # Refill the tool with only the metadata schema.
        schema = self.tool.manage_addCPSSchema('metadata')
        self.assert_(self.tool.metadata)
        for field_id, field_info in metadata_schema.items():
            schema.manage_addField(
                field_id, field_info['type'], **field_info['data'])

    def testTool(self):
        tool = self.tool
        d = tool.all_meta_types()[0]
        self.assertEquals(d['name'], 'CPS Schema')

        self.assertEquals(len(tool.objectIds()), 1)

        # ZMI
        self.assert_(tool.manage_addCPSSchemaForm)

    def testSchema(self):
        schema = self.tool.metadata
        self.assertEquals(schema.getId(), 'metadata')

        # ZMI
        self.assert_(schema.manage_editSchema)
        self.assert_(schema.manage_main)
        self.assert_(schema.manage_addField)


def test_suite():
    suites = [unittest.makeSuite(TestSchemas)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
