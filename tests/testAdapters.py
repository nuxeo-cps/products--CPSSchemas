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
from Testing.ZopeTestCase import ZopeTestCase

from Acquisition import Implicit
from Products.CPSSchemas.StorageAdapter import AttributeStorageAdapter
from Products.CPSSchemas.Schema import CPSSchema


def sort(l):
    l = list(l)
    l.sort()
    return l


class FakePortal(Implicit):
    pass
fakePortal = FakePortal()

class FakeUrlTool(Implicit):
    def getPortalObject(self):
        return fakePortal
fakeUrlTool = FakeUrlTool()

fakePortal.portal_url = fakeUrlTool


class FakeDocument:
    f1 = 'f1class'


class TestStorageAdapter(ZopeTestCase):
    def afterSetUp(self):
        # Acquisition is needed for expression context computation during fetch
        schema = CPSSchema('s1', 'Schema1').__of__(fakePortal)
        schema.addField('f1', 'CPS String Field')
        schema.addField('f2', 'CPS String Field')
        schema.addField('f3', 'CPS String Field', default_expr='string:f3def')
        schema.addField('f4', 'CPS String Field')
        schema.addField('f5', 'CPS String Field',
                        read_ignore_storage=True,
                        read_process_expr='python: f2+"_yo"',
                        read_process_dependent_fields='f2',
                        )
        self.schema = schema

class TestAttributeStorageAdapter(TestStorageAdapter):
    def afterSetUp(self):
        TestStorageAdapter.afterSetUp(self)
        schema = self.schema

        doc = FakeDocument()
        doc.f2 = 'f2inst'
        self.doc = doc

        adapter = AttributeStorageAdapter(schema, doc, field_ids=schema.keys())
        self.adapter = adapter

    def testAccessors(self):
        adapter = self.adapter

        ok_ids = ['f1', 'f2', 'f3', 'f4', 'f5']
        self.assertEquals(sort(adapter.getFieldIds()), ok_ids)

        ok_writable = ['f1', 'f2', 'f3', 'f4', 'f5']
        self.assertEquals(sort([i[0] for i in adapter.getWritableFieldItems()]),
                          ok_writable)

        ok_default = {'f1': '',
                      'f2': '',
                      'f3': 'f3def',
                      'f4': '',
                      'f5': '',
                      }
        data = adapter.getDefaultData()
        adapter.finalizeDefaults(data)
        self.assertEquals(data, ok_default)

        ok_data = {'f1': 'f1class',
                   'f2': 'f2inst',
                   'f3': 'f3def',
                   'f4': '',
                   'f5': 'f2inst_yo',
                   }
        data = adapter.getData()
        adapter.finalizeDefaults(data)
        self.assertEquals(data, ok_data)

    def testMutators(self):
        adapter = self.adapter
        doc = self.doc
        data = {'f4': 'f4changed'}
        adapter.setData(data)
        self.assertEquals(doc.f1, 'f1class')
        self.assertEquals(doc.f2, 'f2inst')
        self.assertRaises(AttributeError, getattr, doc, 'f3')
        self.assertEquals(doc.f4, 'f4changed')
        self.assertRaises(AttributeError, getattr, doc, 'f5')

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
