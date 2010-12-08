# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
# $Id$

import unittest

from copy import deepcopy

from Acquisition import Implicit
from OFS.Image import File

from Products.CPSSchemas.DataModel import DataModel, ValidationError
from Products.CPSSchemas.DataModel import ProtectedFile
from Products.CPSSchemas.StorageAdapter import AttributeStorageAdapter
from Products.CPSSchemas.Schema import CPSSchema
from Products.CPSSchemas.BasicFields import CPSStringField
from Products.CPSSchemas.BasicFields import CPSAsciiStringField
from Products.CPSSchemas.BasicFields import ValidationError
from Products.CPSSchemas.FieldNamespace import fieldStorageNamespace
#from Products.CPSSchemas.Schema import Schema
#from Products.CPSSchemas.Fields.TextField import TextField
#from Products.CPSSchemas.Fields.SelectionField import SelectionField

try:
    True
except NameError:
    True = 1
    False = 0

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
    def Language(self):
        return ''
    def _setObject(self, oid, obj):
        setattr(self, oid, obj)

class FakeProxy:
    def __init__(self, default='en', **kw):
        self.docs = kw
        self.default = default
    def getEditableContent(self, lang=None):
        if not lang: # includes '' and None
            lang = self.default
        return self.docs.get(lang)

    def absolute_url_path(self):
        return '/path/to/proxy'

    def absolute_url(self):
        return 'http://cps.example' + self.absolute_url_path()

class TestDataModel(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def makeOne(self, with_language=False):
        doc = self.doc = FakeDocument()
        doc.f2 = 'f2inst'
        # Acquisition is needed for expression context computation during fetch
        self.schema = schema = CPSSchema('s1', 'Schema1').__of__(fakePortal)
        schema.addField('f1', 'CPS String Field')
        schema.addField('f2', 'CPS String Field')
        schema.addField('f3', 'CPS String Field', default_expr='string:f3def')
        schema.addField('f4', 'CPS String Field',
                        default_expr="python:datamodel.getProxy() is not None "
                        "and datamodel.getProxy() is not None and "
                        "'proxy found' or ''")
        schema.addField('f5', 'CPS String Field',
                        read_ignore_storage=True,
                        read_process_expr='python: f2+"_yo"',
                        read_process_dependent_fields='f2',
                        )
        schema.addField('f6', 'CPS String Field',
                        read_ignore_storage=True,
                        read_process_expr='python: proxy',
                        )
        def dummyMethod(self, text):
            return self.portal_url and text or "failed acquisition"
        fieldStorageNamespace.register('dummy', dummyMethod)
        schema.addField('f7', 'CPS String Field',
                        read_ignore_storage=True,
                        read_process_expr='python:util.dummy("some text")',
                        )
        self.schema.addField('f8', 'CPS String Field',
                             write_process_expr='python: f2+"_ja"',
                             write_process_dependent_fields=('f2',),
                             )

        self.schema.addField('f9', 'CPS String Field',
                             write_process_expr='python: value+f2',
                             )
        self.schema.addField('fA', 'CPS Ascii String Field')
        self.schema.addField('file', 'CPS File Field')

        if with_language:
            schema.addField('Language', 'CPS String Field')
        adapter = AttributeStorageAdapter(schema, doc, field_ids=schema.keys())
        dm = DataModel(doc, (adapter,))
        return dm

    def testAPI(self):
        dm = self.makeOne()
        dm._fetch()
        dm['f4'] = 'f4changed'
        ok = {'f1': 'f1class',
              'f2': 'f2inst',
              'f3': 'f3def',
              'f4': 'f4changed',
              'f5': 'f2inst_yo',
              'f6': None,
              'f7': 'some text',
              'f8': '',
              'f9': '',
              'fA': '',
              'file': None,
              }
        self.assertEquals(sort(dm.keys()), sort(ok.keys()))
        self.assertEquals(dm['f1'], ok['f1'])
        self.assertEquals(dm['f2'], ok['f2'])
        self.assertEquals(dm['f3'], ok['f3'])
        self.assertEquals(dm['f4'], ok['f4'])
        self.assertEquals(dm['f5'], ok['f5'])
        self.assertEquals(dm['f6'], ok['f6'])
        self.assertEquals(dm['f7'], ok['f7'])
        self.assertEquals(dm['f8'], ok['f8'])
        self.assertEquals(dm.getContext(), self.doc)
        self.assertEquals(dm.getProxy(), None)

        # Test has_key and __contains__
        self.assert_(dm.has_key('f1'))
        self.assert_('f1' in dm)
        self.failIf(dm.has_key('lol'))
        self.failIf('lol' in dm)

    def testCreation(self):
        dm = self.makeOne()
        dm._setObject(None) # What we have for creation
        dm._fetch()
        ok = {'f1': '',
              'f2': '',
              'f3': 'f3def',
              'f4': '',
              'f5': '_yo',
              'f6': None,
              'f7': 'some text',
              'f8': '',
              'f9': '',
              'fA': '',
              'file': None,
              }
        self.assertEquals(sort(dm.keys()), sort(ok.keys()))
        self.assertEquals(dm['f1'], ok['f1'])
        self.assertEquals(dm['f2'], ok['f2'])
        self.assertEquals(dm['f3'], ok['f3'])
        self.assertEquals(dm['f4'], ok['f4'])
        self.assertEquals(dm['f5'], ok['f5'])
        self.assertEquals(dm['f6'], ok['f6'])
        self.assertEquals(dm['f7'], ok['f7'])
        self.assertEquals(dm.getContext(), self.doc)
        self.assertEquals(dm.getProxy(), None)

    def testCommitDirty(self):
        dm = self.makeOne()
        doc = self.doc
        dm._fetch()
        dm['f2'] = 'f2changed'
        dm['f4'] = 'f4changed'
        doc.f5 = "unchanged stored value"

        # Unchanged field with class value is not dirty
        self.assertEquals(dm.isDirty('f1'), False)
        # Changed field with old value is dirty
        self.assertEquals(dm.isDirty('f2'), True)
        # Unchanged field with default is dirty
        self.assertEquals(dm.isDirty('f3'), True)
        # Changed field is dirty
        self.assertEquals(dm.isDirty('f4'), True)
        # Computed field is not dirty
        self.assertEquals(dm.isDirty('f5'), False)

        # Now commit
        dm._commit(check_perms=0)
        self.assertEquals(doc.f1, 'f1class')
        self.assertEquals(doc.f2, 'f2changed')
        self.assertEquals(doc.f3, 'f3def')
        self.assertEquals(doc.f4, 'f4changed')
        self.assertEquals(doc.f5, "unchanged stored value")

        # Nothing is dirty anymore
        self.assertEquals(dm.isDirty('f1'), False)
        self.assertEquals(dm.isDirty('f2'), False)
        self.assertEquals(dm.isDirty('f3'), False)
        self.assertEquals(dm.isDirty('f4'), False)
        self.assertEquals(dm.isDirty('f5'), False)

    def testValidation(self):
        # Test that validation methods are being called by using the
        # Ascii String Field
        dm = self.makeOne()
        def assert_kept(v):
            kept = dm['fA']
            self.assertTrue(isinstance(kept, str))
            self.assertEquals(kept, v)

        dm['fA'] = u'abc'
        assert_kept('abc')

        dm.set('fA', u'def')
        assert_kept('def')

        # update
        upd = dict(fA=u'xyz')
        dm.update(upd)
        assert_kept('xyz')
        in_upd = upd['fA']
        # no side effects
        self.assertTrue(isinstance(in_upd, unicode))
        self.assertEquals(in_upd, u'xyz')

        # setdefault
        del dm.data['fA']
        dm.setdefault('fA', u'tuv')
        assert_kept('tuv')

        # now with an error
        self.assertRaises(ValidationError, dm.set, 'fA', u'\xe9')

    def testWriteDependencies(self):
        # We will change f2, and expect f8 to be updated because it has
        # a write dependency on f2
        dm = self.makeOne()
        doc = self.doc
        self.doc.f8 = 'previous_f8'
        dm._fetch()
        dm['f2'] = 'f2changed'
        dm._commit(check_perms=0)
        self.assertEquals(doc.f8, 'f2changed_ja')

    def testWriteDependencies2(self):
        # We will change f9, that depends on itself and f2.
        # Although unchanged, the latter is available for write_exprs
        # no matter what the conf says.
        # Used to break in some directory use-cases where f2 is an id, and
        # therefore discarded in writes. This is reproduced by not indicating
        # the dependency of f9 upon f2.
        dm = self.makeOne()
        doc = self.doc
        self.doc.f2 = 'f2'
        dm._fetch()
        dm['f9'] = 'f9changed'
        self.failIf(dm.isDirty('f2'))
        dm._commit(check_perms=0)
        self.assertEquals(doc.f9, 'f9changedf2')

    def test_commit_with_proxy(self):
        # Test that editable content is correctly retrieved.
        # Modern object creation in FlexibleTypeInformation > 1.120
        # set the proxy in the datamodel before commit.
        # In this case an editable version can be retrieved.
        dm = self.makeOne()
        doc = self.doc
        dm._setObject(doc, proxy=FakeProxy(en=doc))
        dm._fetch()
        dm['f2'] = 'batman'
        dm._commit(check_perms=0)

    def test_commit_with_language(self):
        # Test that commit's editable content gets the correct language.
        # On first commit, language comes from the datamodel itself.
        #
        # Simulate committing a 'fr' datamodel on a new proxy that
        # holds two languages, 'en' being the default.
        dm = self.makeOne(with_language=True)
        doc = self.doc
        doc_en = FakeDocument()
        proxy = FakeProxy(fr=doc, en=doc_en, default='en')
        dm._setObject(doc, proxy=proxy)
        dm._fetch()
        dm['Language'] = 'fr'
        dm._commit(check_perms=0)
        self.assertEquals(dm.getObject(), doc)

    def TODO_testFieldProcessing(self):
        pass

    def test_getSubContentUri(self):
        # this also depends on the fact that AttributeStorageAdapter is working
        dm = self.makeOne()
        dm._setObject(self.doc, proxy=FakeProxy(en=self.doc))
        dm._fetch()

        fobj = File('file', 'original', 'spam')
        dm['file'] = fobj
        dm._commit(check_perms=0)

        self.assertEquals(dm.getSubContentUri('file'),
                          '/path/to/proxy/downloadFile/file/original')
        self.assertEquals(
            dm.getSubContentUri('file', absolute=True),
            'http://cps.example/path/to/proxy/downloadFile/file/original')

    def test_fileProtection(self):
        dm = self.makeOne()
        dm._setObject(self.doc, proxy=FakeProxy(en=self.doc))
        dm._fetch()

        fobj = File('file', 'original', 'spam')
        dm['file'] = fobj
        dm._commit(check_perms=0)

        self.assertEquals(self.doc.file, fobj)
        self.assertTrue(isinstance(dm['file'], ProtectedFile))

        dm['file'].title = 'changed'
        self.assertEquals(dm.getObject().file.title, 'original')
        self.assertEquals(dm['file'].title, 'changed')

        # enhance FakeProxy to simulate getEditableContent for frozen proxy
        def getEditableContent(lang=None):
            self = dm.getProxy()
            if lang is None:
                lang = self.default
            doc = self.docs[lang]
            doc = self.docs[lang] = deepcopy(doc)
            return doc
        dm.getProxy().getEditableContent = getEditableContent

        dm._commit(check_perms=0)

        # unfreeze worked
        self.assertFalse(dm.getObject() is self.doc)
        self.assertFalse(dm.getObject().file is fobj)
        # original file is unchanged
        self.assertEquals(fobj.title, 'original')
        # file in new doc has been changed
        self.assertEquals(dm.getObject().file.title, 'changed')

    def test_fileProtectionCopy(self):
        # See #2218
        dm = self.makeOne()
        dm._setObject(self.doc, proxy=FakeProxy(en=self.doc))
        dm._fetch()

        fobj = File('file', 'original', 'spam')
        dm['file'] = fobj
        dm._commit(check_perms=0)

        dm2 = self.makeOne()
        dm2['file'] = dm['file']


def test_suite():
    return unittest.makeSuite(TestDataModel)

if __name__=="__main__":
    unittest.main(defaultTest)
