# (C) Copyright 2004-2005 Nuxeo SARL <http://nuxeo.com>
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
from DateTime.DateTime import DateTime
from Products.CPSSchemas.StorageAdapter import AttributeStorageAdapter
from Products.CPSSchemas.StorageAdapter import MetaDataStorageAdapter
from Products.CPSSchemas.StorageAdapter import MappingStorageAdapter
from Products.CPSSchemas.Schema import CPSSchema



def sorted(l):
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


class FakeProxy:
    def __init__(self, document):
        self.document = document


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
        self.doc_proxy = FakeProxy(doc)

        adapter = AttributeStorageAdapter(schema, doc, field_ids=schema.keys())
        self.adapter = adapter

    def testAccessors(self):
        adapter = self.adapter

        ok_ids = ['f1', 'f2', 'f3', 'f4', 'f5']
        self.assertEquals(sorted(adapter.getFieldIds()), ok_ids)

        ok_writable = ['f1', 'f2', 'f3', 'f4', 'f5']
        self.assertEquals(sorted([i[0]
                                  for i in adapter.getWritableFieldItems()]),
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

        # Checking that the adapter accepts both an object and a proxy as an
        # argument.
        self.adapter.setContextObject(self.doc)
        self.adapter.setContextObject(self.doc, self.doc_proxy)
        context_object = self.adapter.getContextObject()
        self.assertNotEquals(context_object, None)


class TestMetaDataStorageAdapter(ZopeTestCase):
    def afterSetUp(self):
        from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
        class FakeDCDocument(DefaultDublinCoreImpl, FakeDocument):
            pass

        doc = FakeDCDocument()
        self.doc = doc
        doc.creation_date = DateTime('2005-09-01')
        doc.setModificationDate(DateTime('2005-09-02'))
        doc.setEffectiveDate(DateTime('2005-09-03'))
        doc.setExpirationDate(DateTime('2005-09-04'))
        self.doc_proxy = FakeProxy(doc)

        schema = CPSSchema('s1', 'Schema1').__of__(fakePortal)
        self.schema = schema
        schema.addField('CreationDate', 'CPS DateTime Field',
                        write_ignore_storage=True)
        schema.addField('ModificationDate', 'CPS DateTime Field')
        schema.addField('EffectiveDate', 'CPS DateTime Field')
        schema.addField('ExpirationDate', 'CPS DateTime Field')

        self.adapter = MetaDataStorageAdapter(self.schema, self.doc)

    def testDCAccessors(self):
        adapter = self.adapter

        ok_ids = ['CreationDate', 'EffectiveDate', 'ExpirationDate',
                  'ModificationDate']
        self.assertEquals(sorted(adapter.getFieldIds()), ok_ids)

        ok_writable = ['EffectiveDate', 'ExpirationDate', 'ModificationDate']
        self.assertEquals(sorted([i[0]
                                  for i in adapter.getWritableFieldItems()]),
                          ok_writable)

        ok_data = {'CreationDate': DateTime('2005-09-01'),
                   'ModificationDate': DateTime('2005-09-02'),
                   'EffectiveDate': DateTime('2005-09-03'),
                   'ExpirationDate': DateTime('2005-09-04'),
                   }
        data = adapter.getData()
        adapter.finalizeDefaults(data)
        self.assertEquals(data, ok_data)

    def testDCMutators(self):
        adapter = self.adapter
        doc = self.doc
        data = {'CreationDate': DateTime('2005-10-01'),
                'ModificationDate': DateTime('2005-10-02'),
                'EffectiveDate': DateTime('2005-10-03'),
                'ExpirationDate': DateTime('2005-10-04'),
                }
        adapter.setData(data)
        self.assertEquals(doc.created(), DateTime('2005-09-01'))
        self.assertEquals(doc.modified(), DateTime('2005-10-02'))
        self.assertEquals(doc.effective(), DateTime('2005-10-03'))
        self.assertEquals(doc.expires(), DateTime('2005-10-04'))

        # Now try with string-dates
        data = {'CreationDate': '2005-11-01',
                'ModificationDate': '2005-11-02',
                'EffectiveDate': '2005-11-03',
                'ExpirationDate': '2005-11-04',
                }
        adapter.setData(data)
        self.assertEquals(doc.created(), DateTime('2005-09-01'))
        self.assertEquals(doc.modified(), DateTime('2005-11-02'))
        self.assertEquals(doc.effective(), DateTime('2005-11-03'))
        self.assertEquals(doc.expires(), DateTime('2005-11-04'))

        # Checking that the adapter accepts both an object and a proxy as an
        # argument.
        self.adapter.setContextObject(self.doc)
        self.adapter.setContextObject(self.doc, self.doc_proxy)
        context_object = self.adapter.getContextObject()
        self.assertNotEquals(context_object, None)


class TestMappingStorageAdapter(TestStorageAdapter):
    def afterSetUp(self):
        doc = FakeDocument()
        self.doc = doc
        self.doc_proxy = FakeProxy(doc)

        TestStorageAdapter.afterSetUp(self)
        self.adapter = MappingStorageAdapter(self.schema, self.doc)

    def testAccessors(self):
        # TODO: Later
        pass

    def testMutators(self):
        # Checking that the adapter accepts both an object and a proxy as an
        # argument.
        self.adapter.setContextObject(self.doc)
        self.adapter.setContextObject(self.doc, self.doc_proxy)
        context_object = self.adapter.getContextObject()
        self.assertNotEquals(context_object, None)


def test_suite():
    suites = [unittest.makeSuite(TestAttributeStorageAdapter),
              unittest.makeSuite(TestMetaDataStorageAdapter),
              unittest.makeSuite(TestMappingStorageAdapter),
              ]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
