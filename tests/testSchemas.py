# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

import unittest

from Products.CPSSchemas.SchemasTool import SchemasTool
from Products.CPSSchemas.Schema import CPSSchema
from Products.CPSSchemas.StorageAdapter import MetaDataStorageAdapter
from Products.CPSSchemas.StorageAdapter import AttributeStorageAdapter


class TestSchemas(unittest.TestCase):

    def testTool(self):
        tool = SchemasTool()
        schema1 = CPSSchema('s1', 'Schema1')
        tool.addSchema('s1', schema1)
        schema2 = CPSSchema('s2', 'Schema2')
        tool.addSchema('s2', schema2)
        self.assertEquals(tool.objectIds(), ['s1', 's2'])
        self.assertEquals(tool['s1'], schema1)
        self.assertEquals(tool['s2'], schema2)

    def testSchema(self):
        schema = CPSSchema('s1', 'Schema1')
        self.assertEquals(schema.getId(), 's1')
        schema.addField('f1', 'CPS String Field')
        schema.addField('f2', 'CPS Int Field')
        self.assertEquals(schema.keys(), ['f1', 'f2'])
        self.assertEquals(schema['f1'].getFieldId(), 'f1')
        self.assertEquals(schema['f2'].getFieldId(), 'f2')

    def testSchemaAdapter(self):
        schema = CPSSchema('s1', 'Schema1')
        self.assertEquals(isinstance(schema.getStorageAdapter(object()),
                                     AttributeStorageAdapter),
                          True)
        mschema = CPSSchema('metadata')
        self.assertEquals(isinstance(mschema.getStorageAdapter(object()),
                                     MetaDataStorageAdapter),
                          True)
        omschema = CPSSchema('metadata_shmurk')
        self.assertEquals(isinstance(omschema.getStorageAdapter(object()),
                                     MetaDataStorageAdapter),
                          True)


def test_suite():
    suites = [unittest.makeSuite(TestSchemas)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
