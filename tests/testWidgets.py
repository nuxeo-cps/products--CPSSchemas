# -*- coding: iso-8859-15 -*-
# Copyright (c) 2004-2006 Nuxeo SAS <http://nuxeo.com>
# Authors: Florent Guillaume <fg@nuxeo.com>
#          Anahide Tchertchian <at@nuxeo.com>
#          Georges Racinet <georges@racinet.fr>
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
from zope.testing import doctest

from DateTime.DateTime import DateTime
from ZODB.tests.warnhook import WarningsHook
from Acquisition import Implicit
from cStringIO import StringIO
from OFS.Image import File
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
from ZPublisher.HTTPRequest import FileUpload

from Products.CPSSchemas.DataModel import DataModel
from Products.CPSSchemas.Widget import Widget
from Products.CPSSchemas.Widget import widgetRegistry


DUMMY_DICT = {'a': 'ZZZ', 'b': 'YYY', 'c': 'XXX'}

TEST_IMAGE = ('\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00 '
'\x04\x03\x00\x00\x00\x81Tg\xc7\x00\x00\x00\x18PLTE\x8e\x0b\x08\x00\x00\x00'
'\x99\x99\x99\xcc\xcc\xccfff333\x99\x99f\xff\xff\xff\x15E\xae\xa3\x00\x00\x00'
'\x01tRNS\x00@\xe6\xd8f\x00\x00\x00\x01bKGD\x00\x88\x05\x1dH\x00\x00\x00\tpHYs'
'\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\xdbIDATx\xda'
'\x8d\x92\xb1\x92\x820\x10\x86\xb1\xb8>\xeb\xe1X\x1b`RK`\xd2\x1a4\xfdq#/\xe0'
'\x1b\x98Mf__@\x17\x04\x8b\xbb\xbf\xcb7_6\xc9n\x92\xe43\x1b\x18\xb3;1\xf8\xa61'
'\xa6f\xb0\x7f\x82\x0c\x7f\x18x\xd9G):,\x8d\x03\xc0\xd2\xd0\x8d}3\xca\xaek\xb4'
'\x9d\x8d\xe2"e\xf1;\xd7\xc0\xab1:\xb3\xb3Qd\xfd.\xac\xa6\xa2\xe8\xb4\xa4\x90c'
';\x81\xce\xa3Q!\x1c\x19T\x85\'\xd5\x83(^ \xe6\x9e\x06C3\xb8_PR\x99\xe3\x95'
'\xc1q8\x84\x02\xe1\xb4\xa5\xe9\xd7\xfeL\x8eA\xd5\x98\xf1yS\xd12\xd5\xcag1\xde'
'\xb9c\xd8\xe5\x86b4|\xf5\xed\xcd:S\xb9\x18\xe0\xad\xc9\xfa\\\xc7\x16\xe6\xc6C'
'\xea\xac\x15\x00\x8bQ\x88\xe4\x0b\xc4j@\x0eV#\xdb\xb6\x7f*\xe9\x7f\x94\xf5O'
'\x10\x0f\x1a\xadA\xb9\xc2\xaa\xf96\x00\x00\x00\x00IEND\xaeB`\x82')


class FakePortal(Implicit):
    default_charset = 'unicode'
    def unrestrictedTraverse(self, rpath):
        rpath = rpath.split('/')
        ob = self
        for segment in rpath:
            ob = getattr(ob, segment)
        return ob

fakePortal = FakePortal()

class FakeUrlTool(Implicit):
    def getPortalObject(self):
        return fakePortal
    def __call__(self):
        return '/fake_portal'

class FakeVocabulariesTool(Implicit):
    def getPortalObject(self):
        return fakePortal
    def getVocabularyFor(self, vocabulary_id, context):
        """Returns always the same vocabulary.
        """
        from Products.CPSSchemas.Vocabulary import Vocabulary
        vocabulary = Vocabulary()
        vocabulary.meta_type = 'dummy'
        for k, v in DUMMY_DICT.items():
            vocabulary.set(k, v)
        return vocabulary

_marker = object()

class FakeTranslationService:
    def getSelectedLanguage(self):
        return 'fr'

    def __init__(self):
        self._map = {}

    def addMsgid(self, msgid, xlated):
        self._map[msgid] = xlated

    def __call__(self, msgid, default=_marker):
        res = self._map.get(msgid)
        if res is None:
            return default is _marker and msgid or default
        return res

class FakeWidget(SimpleItem):

    hidden_empty = False
    def __init__(self, id, field_ids):
        self.id = id
        self.field_ids = field_ids

    def getWidgetId(self):
        return self.id

    def render(self, widget_mode, ds, **kw):
        return 'FakeWidget %s mode=%s val=%s' % (self.id, widget_mode,
                                                 ds[self.field_ids[0]])
    def prepare(self, ds, **kw):
        ds[self.id] = ds.getDataModel()[self.field_ids[0]]

    def validate(self, ds, **kw):
        ds.getDataModel()[self.field_ids[0]] = ds[self.id]
        return True # TODO provide return of False


class FakeLayout(Folder):
    def __getitem__(self, k):
        """ObjectManagers plays with REQUEST and doesn't like the fake."""
        try:
            return self._getOb(k)
        except AttributeError:
            raise KeyError(k)

fakePortal.portal_url = FakeUrlTool()
fakePortal.portal_workflow = None
fakePortal.translation_service = FakeTranslationService()

class FakeDataStructure(dict):
    def __init__(self, datamodel):
        self.errs = {}
        self.datamodel = datamodel
        self.errs_mapping = {}

    def getDataModel(self):
        return self.datamodel

    def setError(self, key, message, mapping=None):
        self.errs[key] = message
        self.errs_mapping[key] = mapping

class FakeAdapter(object):
    def __init__(self, schema):
        self.schema = schema
    def getSchema(self):
        return self.schema

class FakeDataModel(dict):
    _adapters = None
    proxy = None
    context = None
    _acl_cache_user = None
    def __init__(self, dm=None):
        if dm is not None:
            self.update(dm)
    def getProxy(self):
        return self.proxy
    def getObject(self):
        return self.proxy
    def getContext(self):
        return self.context
    def fileUri(self, *a, **kw):
        # GR too much faking does not test much, but oh well
        return "dm.fileUri args=%r, kwargs=%r" % (a, kw)
    def imageUri(self, *a, **kw):
        # GR too much faking does not test much, but oh well
        return "dm.imageUri args=%r, kwargs=%r" % (a, kw)

class FakeMimeTypeRegistry(Implicit):
    def lookupExtension(self, name):
        ext = name[name.rfind('.')+1:]
        if ext == 'png':
            return 'image/png'
        return 'testlookup/' + ext.upper()

class FakeFieldStorage:
    def __init__(self, file, filename, headers=None):
        self.file = file
        self.filename = filename
        self.headers = headers or {}
    def read(self, n):
        return self.file.read(n)
    def seek(self, n):
        return self.file.seek(n)

class FakeUser(object):
    __allow_access_to_unprotected_subobjects__ = True
    def __init__(self, id, roles):
        self.id = id
        self.roles = set(roles)
    def has_role(self, roles, context=None):
        if isinstance(roles, basestring):
            roles = [roles]
        return bool(self.roles & set(roles))
    def getId(self):
        return self.id
    def getUserName(self):
        return self.id

class TestWidgets(unittest.TestCase):

    def test_renderHtmlTag(self):
        from Products.CPSSchemas.BasicWidgets import renderHtmlTag

        res = renderHtmlTag('img', title='à doublé " quote')
        self.assertEquals(res, '<img title="\xe0 doubl\xe9 &quot; quote" />')

        res = renderHtmlTag('img', title="a single ' quote")
        self.assertEquals(res, '<img title="a single \' quote" />')

    def testStringWidget(self):
        from Products.CPSSchemas.BasicWidgets import CPSStringWidget
        widget = CPSStringWidget('foo', fields=('foo',))
        self.assertEquals(widget.getWidgetId(), 'foo')
        self.assertEquals(widget.getFieldTypes(), ('CPS String Field',))

        dm = {}
        ds = FakeDataStructure(dm)

        ds['foo'] = 'abc '
        res = widget.validate(ds)
        self.assertEquals(res, True)
        self.assertEquals(dm['foo'], 'abc') # stripped

        # Testing #2013
        widget.must_regexp = r'\d\d-\d+'

        ds['foo'] = '12-345' # passes
        res = widget.validate(ds)
        self.assertEquals(res, True)
        self.assertEquals(dm['foo'], '12-345')

        dm['foo'] = 'before'
        ds['foo'] = '12-345a' # partial match
        res = widget.validate(ds)
        self.assertEquals(res, False)
        self.assertEquals(dm['foo'], 'before')

        ds['foo'] = 'abc' # no match at all
        res = widget.validate(ds)
        self.assertEquals(res, False)
        self.assertEquals(dm['foo'], 'before')

    def testIntWidget(self):
        from Products.CPSSchemas.BasicWidgets import CPSIntWidget
        widget = CPSIntWidget('foo')
        widget.fields = ['foo']
        self.assertEquals(widget.getWidgetId(), 'foo')
        self.assertEquals(widget.getFieldTypes(), ('CPS Int Field',))
        dm = {}
        ds = FakeDataStructure(dm)

        ds['foo'] = '123 '
        res = widget.validate(ds)
        self.assertEquals(res, True)
        self.assertEquals(dm['foo'], 123)

        ds['foo'] = ' 0 '
        res = widget.validate(ds)
        self.assertEquals(res, True)
        self.assertEquals(dm['foo'], 0)

        ds['foo'] = '0ab '
        res = widget.validate(ds)
        self.assertEquals(res, False)
        self.assertEquals(ds['foo'], '0ab')

        widget.is_required = False
        ds['foo'] = ' '
        res = widget.validate(ds)
        self.assertEquals(res, True)
        self.assertEquals(ds['foo'], '')
        self.assertEquals(dm['foo'], None)

        widget.is_required = True
        ds['foo'] = ' '
        res = widget.validate(ds)
        self.assertEquals(res, False)
        self.assertEquals(ds['foo'], '')

        widget.is_limited = True
        widget.min_value = 10
        widget.max_value = 20
        ds['foo'] = '123'
        res = widget.validate(ds)
        self.assertEquals(res, False)
        ds['foo'] = '15'
        res = widget.validate(ds)
        self.assertEquals(res, True)
        self.assertEquals(dm['foo'], 15)

        # prepare

        dm['foo'] = 12345678901234567890
        widget.prepare(ds)
        self.assertEquals(ds['foo'], '12345678901234567890')

        widget.thousands_separator = ','
        widget.prepare(ds)
        self.assertEquals(ds['foo'], '12,345,678,901,234,567,890')

        dm['foo'] = 0
        widget.prepare(ds)
        self.assertEquals(ds['foo'], '0')

        dm['foo'] = None
        widget.prepare(ds)
        self.assertEquals(ds['foo'], '')

    def testLongWidget(self):
        from Products.CPSSchemas.BasicWidgets import CPSLongWidget
        widget = CPSLongWidget('foo')
        self.assertEquals(widget.getWidgetId(), 'foo')

    def testFloatWidget(self):
        from Products.CPSSchemas.BasicWidgets import CPSFloatWidget
        widget = CPSFloatWidget('foo')
        widget.fields = ['foo']
        self.assertEquals(widget.getWidgetId(), 'foo')
        self.assertEquals(widget.getFieldTypes(), ('CPS Float Field',))

        dm = {}
        ds = FakeDataStructure(dm)

        ds['foo'] = '123 '
        res = widget.validate(ds)
        self.assertEquals(res, True)
        self.assertEquals(dm['foo'], 123.0)

        ds['foo'] = ' 0 '
        res = widget.validate(ds)
        self.assertEquals(res, True)
        self.assertEquals(dm['foo'], 0.0)

        ds['foo'] = '12.34'
        res = widget.validate(ds)
        self.assertEquals(res, True)
        self.assertEquals(dm['foo'], 12.34)

        ds['foo'] = '0ab '
        res = widget.validate(ds)
        self.assertEquals(res, False)
        self.assertEquals(ds['foo'], '0ab')

        widget.is_required = False
        ds['foo'] = ' '
        res = widget.validate(ds)
        self.assertEquals(res, True)
        self.assertEquals(ds['foo'], '')
        self.assertEquals(dm['foo'], None)

        widget.is_required = True
        ds['foo'] = ' '
        res = widget.validate(ds)
        self.assertEquals(res, False)
        self.assertEquals(ds['foo'], '')

        widget.is_limited = True
        widget.min_value = 10.0
        widget.max_value = 20.0
        ds['foo'] = '123.5'
        res = widget.validate(ds)
        self.assertEquals(res, False)
        ds['foo'] = '12.5'
        res = widget.validate(ds)
        self.assertEquals(res, True)
        self.assertEquals(dm['foo'], 12.5)

        # prepare

        dm['foo'] = 123456
        widget.prepare(ds)
        self.assertEquals(ds['foo'], '123456')

        widget.decimals_number = 2
        widget.decimals_separator = '.'
        dm['foo'] = 123456
        widget.prepare(ds)
        self.assertEquals(ds['foo'], '123456.00')

        widget.thousands_separator = ','
        dm['foo'] = 123456
        widget.prepare(ds)
        self.assertEquals(ds['foo'], '123,456.00')

        dm['foo'] = 0
        widget.prepare(ds)
        self.assertEquals(ds['foo'], '0.00')

        dm['foo'] = None
        widget.prepare(ds)
        self.assertEquals(ds['foo'], '')

    def testBooleanWidget(self):
        from Products.CPSSchemas.BasicWidgets import CPSBooleanWidget
        widget = CPSBooleanWidget('foo')
        widget.fields = ['foo']
        self.assertEquals(widget.getWidgetId(), 'foo')
        self.assertEquals(widget.getFieldTypes(), ('CPS Int Field',))
        dm = {}
        ds = FakeDataStructure(dm)

        ds['foo'] = 0
        res = widget.validate(ds)
        self.assertEquals(res, True)
        self.assert_(isinstance(dm['foo'], bool))
        self.assertEquals(dm['foo'], 0)

        ds['foo'] = 1
        res = widget.validate(ds)
        self.assertEquals(res, True)
        self.assert_(isinstance(dm['foo'], bool))
        self.assertEquals(dm['foo'], 1)

        ds['foo'] = False
        res = widget.validate(ds)
        self.assertEquals(res, True)
        self.assert_(isinstance(dm['foo'], bool))
        self.assertEquals(ds['foo'], 0)

        ds['foo'] = True
        res = widget.validate(ds)
        self.assertEquals(res, True)
        self.assert_(isinstance(dm['foo'], bool))
        self.assertEquals(dm['foo'], 1)

        # prepare

        dm['foo'] = 0
        widget.prepare(ds)
        self.assert_(isinstance(ds['foo'], bool))
        self.assertEquals(ds['foo'], False)

        dm['foo'] = 1
        widget.prepare(ds)
        self.assert_(isinstance(ds['foo'], bool))
        self.assertEquals(ds['foo'], True)

        dm['foo'] = False
        widget.prepare(ds)
        self.assert_(isinstance(ds['foo'], bool))
        self.assertEquals(ds['foo'], False)

        dm['foo'] = True
        widget.prepare(ds)
        self.assert_(isinstance(ds['foo'], bool))
        self.assertEquals(ds['foo'], True)

    def testTextWidget(self):
        from Products.CPSSchemas.ExtendedWidgets import CPSTextWidget
        widget = CPSTextWidget('foo').__of__(fakePortal)
        def meth(*args, **kwargs):
            """fake render method"""

        fakePortal.widget_text_render = meth
        widget.manage_changeProperties(hidden_empty=True, fields=['f'])
        dm = FakeDataModel()
        ds = FakeDataStructure(dm)

        dm['f'] = ''
        widget.prepare(ds)
        self.assertEquals(widget.render('view', ds), '')
        self.failIfEqual(widget.render('edit', ds), '')

        dm['f'] = '  '
        widget.prepare(ds)
        self.assertEquals(widget.render('view', ds), '')

    def testDateTimeWidget_getDateTimeInfo(self):
        from Products.CPSSchemas.ExtendedWidgets import CPSDateTimeWidget
        from DateTime.DateTime import DateTime
        widget = CPSDateTimeWidget('foo').__of__(fakePortal)

        #
        # None value
        #
        value = None

        # None mode
        mode = None
        self.assertEqual(widget.getDateTimeInfo(value, mode),
                         (None, '', '12', '00'))
        # None value, view mode
        mode = 'view'
        self.assertEqual(widget.getDateTimeInfo(value, mode),
                         (None, '', '12', '00'))
        mode = 'edit'
        # None value, edit mode -> defaults to current time if required
        self.assertEqual(widget.getDateTimeInfo(value, mode),
                         (None, '', '12', '00'))
        widget.manage_changeProperties(is_required=1)
        self.assertNotEqual(widget.getDateTimeInfo(value, mode),
                            (None, '', '12', '00'))

        #
        # not None value
        #
        value = DateTime(year=2005, month=4, day=1, hour=3, minutes=14)
        # not None value, None mode
        # suppose selected language is English
        self.assertNotEqual(widget.getDateTimeInfo(value, mode),
                            (value, '04/01/2005', '3', '14'))
        # not None value, view mode
        self.assertNotEqual(widget.getDateTimeInfo(value, mode),
                            (value, '04/01/2005', '3', '14'))
        # not None value, edit mode
        self.assertNotEqual(widget.getDateTimeInfo(value, mode),
                            (value, '04/01/2005', '3', '14'))

    def testSelectWidget(self):
        from Products.CPSSchemas.BasicWidgets import CPSSelectWidget
        fakePortal.portal_vocabularies = FakeVocabulariesTool()
        widget = CPSSelectWidget('foo').__of__(fakePortal)
        widget.fields = ['foo']
        self.assertEquals(widget.getWidgetId(), 'foo')
        self.assertEquals(widget.getFieldTypes(), ('CPS String Field',))

        dm = FakeDataModel()
        dm['foo'] = None
        ds = FakeDataStructure(dm)
        ds['foo'] = 'a'
        res = widget.validate(ds)
        self.assert_(widget.validate(ds))

        widget.add_empty_key = True
        widget.empty_key_value = 'Choose one'
        widget.empty_key_value_i18n = 'label_choose_one'
        fakePortal.translation_service.addMsgid('label_choose_one',
                                                u'S\xe9lectionnez')

        ds['foo'] = ''
        widget.is_required = False
        self.assert_(widget.validate(ds))

        self.assertEquals(widget.render('view', ds), 'Choose one')
        res = widget.render('edit', ds)
        # regression test
        self.assertEquals(res, '<select name="widget__foo:utf8:ustring" id="widget__foo"><option selected="selected" value="">Choose one</option><option value="a">ZZZ</option><option value="c">XXX</option><option value="b">YYY</option></select>')
        widget.translated = True
        self.assertEquals(widget.render('view', ds), unicode('S\xe9lectionnez',
                                                             'latin-1'))

    def testMultiSelectWidget(self):
        from Products.CPSSchemas.BasicWidgets import CPSMultiSelectWidget
        fakePortal.portal_vocabularies = FakeVocabulariesTool()
        widget = CPSMultiSelectWidget('foo').__of__(fakePortal)
        widget.fields = ['foo']
        self.assertEquals(widget.getWidgetId(), 'foo')
        self.assertEquals(widget.getFieldTypes(), ('CPS String List Field',))

        dm = FakeDataModel()
        dm['foo'] = None
        ds = FakeDataStructure(dm)
        ds['foo'] = ['a', 'b', 'c']
        res = widget.validate(ds)
        self.assertEquals(res, True)

        res = widget.render('view', ds)
        self.assertEquals(res, 'ZZZ, YYY, XXX')
        res = widget.render('edit', ds)
        expected = '<input type="hidden" name="widget__foo:utf8:utokens:default" value="" /><select multiple="multiple" name="widget__foo:utf8:ulist" id="widget__foo"><option selected="selected" value="a">ZZZ</option><option selected="selected" value="c">XXX</option><option selected="selected" value="b">YYY</option></select>'
        self.assertEquals(res, expected)

        kw = {'sorted': True}
        widget.manage_changeProperties(**kw)
        res = widget.render('view', ds)
        self.assertEquals(res, 'XXX, YYY, ZZZ')
        res = widget.render('edit', ds)
        expected = '<input type="hidden" name="widget__foo:utf8:utokens:default" value="" /><select multiple="multiple" name="widget__foo:utf8:ulist" id="widget__foo"><option selected="selected" value="c">XXX</option><option selected="selected" value="b">YYY</option><option selected="selected" value="a">ZZZ</option></select>'
        self.assertEquals(res, expected)

    def testFlashWidget(self):
        from Products.CPSSchemas.ExtendedWidgets import CPSFlashWidget
        widget = CPSFlashWidget('foo')
        self.assertEquals(widget.getWidgetId(), 'foo')
        self.assertEquals(widget.getFieldTypes(), ('CPS File Field',
                                                   'CPS String Field',
                                                   'CPS File Field'))

    def test_getCssClass(self):
        # create a bare widget, and set it in the portal to be able to create
        # the expression namespace
        widget = Widget('widget_id').__of__(fakePortal)
        dm = DataModel(ob=None, proxy=None)

        # just use css_class
        self.assertEquals(widget.getCssClass('view', dm), '')
        kw = {'css_class': 'stringClass'}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.getCssClass('view', dm), 'stringClass')
        self.assertEquals(widget.getCssClass('create', dm), 'stringClassEdit')
        self.assertEquals(widget.getCssClass('edit', dm), 'stringClassEdit')

        # just use css_class_expr
        kw = {'css_class': '',
              'css_class_expr': 'string:exprClass'}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.getCssClass('view', dm), 'exprClass')
        self.assertEquals(widget.getCssClass('edit', dm), 'exprClass')

        # use both properties
        kw = {'css_class': 'stringClass',
              'css_class_expr': 'string:exprClass'}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.getCssClass('view', dm), 'exprClass')
        self.assertEquals(widget.getCssClass('edit', dm), 'exprClass')

        kw = {'css_class': 'stringClass',
              'css_class_expr': 'nothing'}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.getCssClass('view', dm), '')
        self.assertEquals(widget.getCssClass('edit', dm), '')

        # use non dummy expressions :)
        kw = {'css_class': 'stringClass',
              'css_class_expr': "python:layout_mode == 'view' "
                                "and 'viewExprClass' or nothing"}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.getCssClass('view', dm), 'viewExprClass')
        self.assertEquals(widget.getCssClass('edit', dm), '')

        kw = {'css_class': 'stringClass',
              'css_class_expr': "python:layout_mode == 'search' "
                                "and 'searchExprClass' or nothing"}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.getCssClass('view', dm), '')
        self.assertEquals(widget.getCssClass('edit', dm), '')
        self.assertEquals(widget.getCssClass('search', dm), 'searchExprClass')

    def test_readOnly(self):
        widget = Widget('widget_id').__of__(fakePortal)
        dm = DataModel(ob=None, proxy=None)

        self.assertEquals(widget.isReadOnly(dm, 'view'), False)

        kw = {'readonly_if_expr': "python:True"}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.isReadOnly(dm, 'view'), True)

        kw = {'readonly_if_expr': "python:layout_mode == 'edit'"}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.isReadOnly(dm, 'create'), False)
        self.assertEquals(widget.isReadOnly(dm, 'edit'), True)

        # XXX GR: this doesn't work with security implementation
        # (TypeError: 'bool' object is not callable)
        kw = {'readonly_if_expr':
              "python:  not user.has_role(('Manager', 'Member'), proxy)"}
        widget.manage_changeProperties(**kw)
        dm._acl_cache_user = FakeUser('bob', ['Dummy'])
        self.assertEquals(widget.isReadOnly(dm, 'edit'), True)
        dm._acl_cache_user = FakeUser('bob', ['Member'])
        self.assertEquals(widget.isReadOnly(dm, 'edit'), False)

    def test_getJavaScriptCode(self):
        # create a bare widget, and set it in the portal to be able to create
        # the expression namespace
        widget = Widget('widget_id').__of__(fakePortal)
        dm = DataModel(ob=None, proxy=None)

        # dummy tests, sorry, no JavaScript inspiration :)
        kw = {'javascript_expr': ''}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.getJavaScriptCode('view', dm), '')

        js_code = """
function getSelectedRadioId(buttonGroup) {
  var i = getSelectedRadio(buttonGroup);
  if (i == -1) {
    return "";
  } else {
    if (buttonGroup[i]) {
      return buttonGroup[i].id;
    } else {
      return buttonGroup.id;
    }
  }
}
"""
        kw = {'javascript_expr': 'string:' + js_code}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.getJavaScriptCode('view', dm).strip(),
                          js_code.strip())

        js_code = """
function getLayoutMode() {
  return 'view';
}
"""
        kw = {
            'javascript_expr': """string:function getLayoutMode() {
  return '${layout_mode}';
}"""}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.getJavaScriptCode('view', dm).strip(),
                          js_code.strip())

    def test_CPSIdentifierWidget(self):
       from Products.CPSSchemas.BasicWidgets import CPSIdentifierWidget
       wi = CPSIdentifierWidget('widget_id')
       self.assert_(not wi._checkIdentifier('136ll'))
       self.assert_(not wi._checkIdentifier('é"136ll'))
       wi.id_pat = r'[a-zA-Z0-9@\-\._]*$'
       self.assert_(wi._checkIdentifier('136ll'))
       self.assert_(not wi._checkIdentifier('é"136ll'))

    def test_CPSSearchZCTextWidget(self):
        from Products.CPSSchemas.SearchWidgets import CPSSearchZCTextWidget
        widget = CPSSearchZCTextWidget('foo').__of__(fakePortal)
        # XXX: add more tests here

    def test_CPSSearchModifiedWidget(self):
        from Products.CPSSchemas.SearchWidgets import CPSSearchModifiedWidget
        widget = CPSSearchModifiedWidget('foo').__of__(fakePortal)
        widget.fields = ('foo', )
        wid = widget.getWidgetId()
        dm = FakeDataModel()
        ds = FakeDataStructure(dm)
        widget.prepare(ds)
        self.assertTrue(widget.validate(ds))
        self.assertEquals(dm['foo'], None)
        ds[wid] = 'not a int'
        self.assertFalse(widget.validate(ds))

    def test_CPSSearchLanguageWidget(self):
        from Products.CPSSchemas.SearchWidgets import CPSSearchLanguageWidget
        widget = CPSSearchLanguageWidget('foo').__of__(fakePortal)
        # XXX: add more tests here

    def test_CPSSearchSortWidget(self):
        from Products.CPSSchemas.SearchWidgets import CPSSearchSortWidget
        widget = CPSSearchSortWidget('foo').__of__(fakePortal)
        # XXX: add more tests here

    def test_CPSCompoundWidget(self):
        from Products.CPSSchemas.widgets.compound import CPSCompoundWidget
        widget = CPSCompoundWidget('foo')
        widget.widget_ids = ['w1', 'w2']
        widget.field_ids = [] # some widgets are badly configured
        w1 = FakeWidget('w1', ['f1'])
        w2 = FakeWidget('w2', ['f2'])
        layout = FakeLayout('layout')
        layout._setObject('w1', w1)
        layout._setObject('w2', w2)
        def render_method(mode=None, datastructure=None, cells=None, **kw):
            s = ['mode %s' % mode]
            for cell in cells:
                s.append(cell['widget_rendered'])
            return '|'.join(s)
        widget.widget_compound_default_render = render_method
        layout = layout.__of__(fakePortal)
        widget = widget.__of__(layout)
        widget_infos = {
            'w1': {'widget': w1, 'widget_mode': 'view', 'css_class': ''},
            'w2': {'widget': w2, 'widget_mode': 'view', 'css_class': ''},
            }
        ds = {'f1': 'Foo',
              'f2': 'Bar'}
        self.assertFalse(widget.isHidden())

        rendered = widget.render('view', ds, widget_infos=widget_infos)
        self.assertEquals(rendered,
                          'mode view|'
                          'FakeWidget w1 mode=view val=Foo|'
                          'FakeWidget w2 mode=view val=Bar')

        # If a subwidget is hidden, we don't see it in the output
        widget_infos['w2']['widget_mode'] = 'hidden'
        rendered = widget.render('view', ds, widget_infos=widget_infos)
        self.assertEquals(rendered,
                          'mode view|FakeWidget w1 mode=view val=Foo')

        # Now test prepare
        dm = FakeDataModel()
        ds = FakeDataStructure(dm)
        dm['f1'] = 'Spam'
        dm['f2'] = 'Eggs'
        widget.prepare(ds)
        self.assertEquals(ds, dict(w1='Spam', w2='Eggs'))

        # Now test validate
        ds['w1'] = 'Foo'
        ds['w2'] = 'Bar'
        widget.validate(ds)
        self.assertEquals(dm, dict(f1='Foo', f2='Bar'))

    def test_CPSCompoundWidget_missing(self):
        # #2394: don't break if a subwidget is missing
        from Products.CPSSchemas.widgets.compound import CPSCompoundWidget
        layout = FakeLayout('layout')
        widget = CPSCompoundWidget('foo').__of__(layout)
        widget.widget_ids = ['w1', 'w2']
        w1 = FakeWidget('w1', ['f1'])
        layout._setObject('w1', w1)

        self.assertEquals(widget._getSubWidgets(), ())
        self.assertTrue(widget.isHidden())

        w2 = FakeWidget('w2', ['f2'])
        layout._setObject('w2', w2)
        widget = CPSCompoundWidget('foo').__of__(layout)
        widget.widget_ids = ['w1', 'w2']

        sws = widget._getSubWidgets()
        self.assertEquals([sw.getWidgetId() for sw in sws], ['w1', 'w2'])

    def test_CPSDateTimeRangeWidget_validation(self):
        from Products.CPSSchemas.ExtendedWidgets import CPSDateTimeWidget
        from Products.CPSSchemas.ExtendedWidgets import CPSDateTimeRangeWidget

        widget = CPSDateTimeRangeWidget('foo')
        widget.widget_ids = ['w_begin', 'w_end']
        widget.field_ids = [] # some widgets are badly configured

        layout = FakeLayout('layout')
        layout = layout.__of__(fakePortal)
        widget = widget.__of__(layout)

        def make_sub(wid, fid):
            w = CPSDateTimeWidget(wid)
            w.fields = (fid,)
            layout._setObject(wid, w)
            return layout._getOb(wid)

        bwidget = make_sub('w_begin', 'f_begin')
        ewidget = make_sub('w_end', 'f_end')

        dm = FakeDataModel()
        ds = FakeDataStructure(dm)

        def prepare_subs():
            "This is also the simplest way to put something in data structure"
            bwidget.prepare(ds)
            ewidget.prepare(ds)

        def ds_put_for(subwidget, dt):
            """Put dt in datastructure for widget by using preparation.

            dm value is restored
            """
            if dt is None:
                ds[subwidget.getWidgetId()] = ''
            fid = subwidget.fields[0]
            prev = dm.get(fid)
            dm[fid] = dt
            subwidget.prepare(ds)
            dm[fid] = prev

        # validation of sub-widget fails
        ds_put_for(bwidget, DateTime('2010/01/01'))
        ds['w_begin_date'] = 'garbage'
        self.assertFalse(widget.validate(ds))

        # All empty, range widget not required
        ds_put_for(bwidget, None)
        ds_put_for(ewidget, None)
        self.assertTrue(widget.validate(ds))

        # now range widget is required
        widget.is_required = True
        self.assertFalse(widget.validate(ds))

        # still required, providing just the end
        ds_put_for(bwidget, None)
        dt = DateTime('2010/01/01')
        ds_put_for(ewidget, dt)
        self.assertTrue(dm['f_end'] is None) # to be sure of test itself
        self.assertTrue(widget.validate(ds))
        self.assertEquals(dm['f_end'], dt)

        # still required, providing just the beginning
        ds_put_for(ewidget, None)
        dt = DateTime('2010/01/01')
        ds_put_for(bwidget, dt)
        self.assertTrue(dm['f_begin'] is None) # to be sure of test itself
        self.assertTrue(widget.validate(ds))
        self.assertEquals(dm['f_begin'], dt)

        # checking the range with two values
        begin = DateTime('2010/01/01')
        end = DateTime('2010/01/02')
        ds_put_for(bwidget, begin)
        ds_put_for(ewidget, end)
        self.assertTrue(widget.validate(ds))
        self.assertEquals(dm['f_begin'], begin)
        self.assertEquals(dm['f_end'], end)

        # the other way round fails, but no need to test that
        # values are unchanged in dm : datamodel are meant to be transient,
        # and ds validation failure should be enough so that downstream
        # doesn't commit the datamodel
        ds_put_for(bwidget, end)
        ds_put_for(ewidget, begin)
        self.assertFalse(widget.validate(ds))

        # Testing the skip expression. First evaluates to false
        widget.manage_changeProperties(
            is_required=True,
            skip_validate_if_expr="python: False")
        ds_put_for(bwidget, None)
        ds_put_for(ewidget, None)
        self.assertFalse(widget.validate(ds))

        # fresh objects to be sure dm isn't touched
        dm = FakeDataModel()
        ds = FakeDataStructure(dm)

        # now evaluates to True and validation should have written to dm
        widget.manage_changeProperties(skip_validate_if_expr="python: True")
        ds_put_for(bwidget, begin)
        ds_put_for(ewidget, end)
        del dm['f_begin']         # avoid side-effects
        del dm['f_end']
        self.assertEquals(dm, {})
        self.assertTrue(widget.validate(ds))
        self.assertEquals(dm, {})

        # getting back to normal
        widget.manage_changeProperties(skip_validate_if_expr="")
        self.assertTrue(widget.validate(ds))
        self.assertEquals(dm, dict(f_begin=begin, f_end=end))

    def test_CPSCompoundWidget_old_LinkWidget(self):
        from Products.CPSSchemas.BasicWidgets import CPSCompoundWidget
        widget = CPSCompoundWidget('foo')
        widget.widget_type = 'Link Widget'
        widget.widget_ids = ['w1', 'w2', 'w3']
        widget.field_ids = [] # some widgets were badly configured
        w1 = FakeWidget('w1', ['f1'])
        w2 = FakeWidget('w2', ['f2'])
        w3 = FakeWidget('w3', ['f3'])
        layout = FakeLayout('layout')
        layout._setObject('w1', w1)
        layout._setObject('w2', w2)
        layout._setObject('w3', w3)
        def render_method(mode=None, datastructure=None, cells=None, **kw):
            s = ['mode %s' % mode]
            for cell in cells:
                s.append(cell['widget_rendered'])
            return '|'.join(s)
        widget.widget_link_render = render_method
        layout = layout.__of__(fakePortal)
        widget = widget.__of__(layout)
        widget_infos = {
            'w1': {'widget': w1, 'widget_mode': 'view', 'css_class': ''},
            'w2': {'widget': w2, 'widget_mode': 'view', 'css_class': ''},
            'w3': {'widget': w3, 'widget_mode': 'view', 'css_class': ''},
            }
        ds = {'f1': 'http://foo',
              'f2': 'Foo',
              'f3': "The foo."}
        rendered = widget.render('view', ds, widget_infos=widget_infos)
        self.assertEquals(rendered,
                          'mode view|'
                          'FakeWidget w1 mode=view val=http://foo|'
                          'FakeWidget w2 mode=view val=Foo|'
                          'FakeWidget w3 mode=view val=The foo.')

    def test_BBB_register_old_widget(self):
        # Simulate code that was deriving from old widgets.
        from Products.CPSSchemas.Widget import CPSWidget
        from Products.CPSSchemas.Widget import CPSWidgetType
        from Products.CPSSchemas.WidgetTypesTool import WidgetTypeRegistry
        class MyWidget(CPSWidget):
            meta_type = 'My Widget'
        class MyWidgetType(CPSWidgetType):
            meta_type = 'My Widget Type'
            cls = MyWidget
        hook = WarningsHook()
        hook.install()
        try:
            WidgetTypeRegistry.register(MyWidgetType)
        finally:
            hook.uninstall()
        self.assertEquals(len(hook.warnings), 1)

        # Now deriving from an existing widget type
        from Products.CPSSchemas.BasicWidgets import CPSURLWidget
        # Here CPSURLWidgetType is dynamically generated by
        # BBB registration code in WidgetRegistry.
        widgetRegistry.register(CPSURLWidget)
        from Products.CPSSchemas.BasicWidgets import CPSURLWidgetType
        class OtherWidget(CPSURLWidget):
            meta_type = 'Other Widget'
        class OtherWidgetType(CPSURLWidgetType):
            meta_type = 'Other Widget Type'
            cls = OtherWidget
        hook.clear()
        hook.install()
        try:
            WidgetTypeRegistry.register(OtherWidgetType)
        finally:
            hook.uninstall()
        self.assertEquals(len(hook.warnings), 1)

    def test_CPSRevisionWidget(self):
        from Products.CPSSchemas.BasicWidgets import CPSRevisionWidget
        folder = Folder()
        widget = CPSRevisionWidget('foo').__of__(folder)

        dm = FakeDataModel()
        class FakeProxy(Folder):
            def getRevision(self):
                return 1
        dm.proxy = FakeProxy().__of__(folder)
        ds = FakeDataStructure(dm)

        self.assertEquals(widget.prepare(ds), None)
        self.assert_(widget.validate(ds))
        for mode in ('view', 'edit'):
            self.assertEquals(widget.render(mode, ds), '1')

        # Now without proxy
        dm.proxy = None

        self.assertEquals(widget.prepare(ds), None)
        self.assert_(widget.validate(ds))
        for mode in ('view', 'edit'):
            self.assertEquals(widget.render(mode, ds), '')

    def test_CPSFileWidget_getFileInfo(self):
        from Products.CPSSchemas.BasicWidgets import CPSFileWidget
        folder = Folder()
        widget = CPSFileWidget('foo').__of__(folder)
        folder.mimetypes_registry = FakeMimeTypeRegistry()
        widget.fields = ['bar']
        dm = FakeDataModel()
        dm._adapters = [FakeAdapter({'bar': 'thatsme'})]
        dm.proxy = 'someproxy'
        dm['bar'] = None
        ds = FakeDataStructure(dm)
        f = StringIO('thefilecontent')
        fu = FileUpload(FakeFieldStorage(f, 'thefilename.txt'))
        ds['foo'] = fu
        ds['foo_title'] = 'thetitle'
        file_info = widget.getFileInfo(ds)
        self.assertEquals(file_info, {
            'empty_file': False,
            'session_file': False,
            'current_filename': 'thefilename.txt',
            'title': 'thetitle',
            'size': len('thefilecontent'),
            'last_modified': '',
            'content_url': "dm.fileUri args=('bar',), kwargs={}",
            'mimetype': 'testlookup/TXT',
            })

    def test_CPSFileWidget_utf8_filename(self):
        from Products.CPSSchemas.BasicWidgets import CPSFileWidget
        folder = Folder()
        widget = CPSFileWidget('foo').__of__(folder)
        folder.mimetypes_registry = FakeMimeTypeRegistry()
        widget.fields = ['bar']
        dm = FakeDataModel()
        dm._adapters = [FakeAdapter({'bar': 'thatsme'})]
        dm.proxy = 'someproxy'
        dm['bar'] = None
        ds = FakeDataStructure(dm)
        f = StringIO('thefilecontent')
        fu = FileUpload(FakeFieldStorage(f, 'thefilename.txt'))
        ds['foo'] = fu
        ds['foo_title'] = 'th\xc3\xa9title'
        file_info = widget.getFileInfo(ds)
        self.assertEquals(file_info, {
            'empty_file': False,
            'session_file': False,
            'current_filename': 'thefilename.txt',
            'title': 'th\xc3\xa9title',
            'size': len('thefilecontent'),
            'last_modified': '',
            'content_url': "dm.fileUri args=('bar',), kwargs={}",
            'mimetype': 'testlookup/TXT',
            })

    def test_CPSFileWidget_validate(self):
        from Products.CPSSchemas.BasicWidgets import CPSFileWidget
        from Products.CPSUtil.file import makeFileUploadFromOFSFile
        from Products.CPSUtil.file import persistentFixup

        folder = Folder()
        widget = CPSFileWidget('foo').__of__(folder)
        folder.mimetypes_registry = FakeMimeTypeRegistry()

        widget.fields = ['bar']
        dm = {}
        ds = FakeDataStructure(dm)

        # Initial upload
        dm['bar'] = None
        ds['foo_choice'] = 'change'
        f = StringIO('filecontent')
        fu = FileUpload(FakeFieldStorage(f, 'thefilename.txt'))
        ds['foo'] = fu
        ds['foo_filename'] = 'somefilename.txt'
        res = widget.validate(ds)
        self.assert_(res)
        self.assertEquals(dm.keys(), ['bar'])
        self.assertEquals(type(dm['bar']), File)
        self.assertEquals(dm['bar'].getId(), 'bar')
        self.assertEquals(dm['bar'].title, 'somefilename.txt')
        self.assertEquals(str(dm['bar']), 'filecontent')

        # Change filename (stored in File title)
        ds['foo'] = makeFileUploadFromOFSFile(dm['bar']) # prepare
        ds['foo_choice'] = 'keep'
        ds['foo_filename'] = 'newfilename.doc'
        res = widget.validate(ds)
        self.assert_(res)
        self.assertEquals(dm.keys(), ['bar'])
        self.assertEquals(type(dm['bar']), File)
        self.assertEquals(dm['bar'].title, 'newfilename.doc')
        self.assertEquals(str(dm['bar']), 'filecontent')
        # datastructure doesn't retain the fileupload, which we don't need
        # to save in session as it's unchanged from ZODB data
        self.failIf('foo' in ds, ds.keys())

        # Change filename (stored in File title) after validation error
        # which kept the file in the session
        ds['foo'] = makeFileUploadFromOFSFile(dm['bar']) # prepare
        persistentFixup(ds) # prepare was from session
        ds['foo_choice'] = 'keep'
        ds['foo_filename'] = 'okfilename.doc'
        res = widget.validate(ds)
        self.assert_(res)
        self.assertEquals(dm.keys(), ['bar'])
        self.assertEquals(type(dm['bar']), File)
        self.assertEquals(dm['bar'].title, 'okfilename.doc')
        self.assertEquals(str(dm['bar']), 'filecontent')
        # datastructure has the fileupload, which is not the same
        # as ZODB data so has to be saved in session if needed
        self.assert_('foo' in ds, ds.keys())

        # Upload new file without filename change
        ds['foo_choice'] = 'change'
        f = StringIO('tous les hommes naissent...')
        fu = FileUpload(FakeFieldStorage(f, 'declaration.txt'))
        ds['foo'] = fu
        ds['foo_filename'] = 'okfilename.txt' # unchanged from previous
        res = widget.validate(ds)
        self.assert_(res)
        self.assertEquals(dm.keys(), ['bar'])
        self.assertEquals(type(dm['bar']), File)
        self.assertEquals(dm['bar'].title, 'okfilename.txt')
        self.assertEquals(str(dm['bar']), 'tous les hommes naissent...')

        # Delete
        ds['foo_choice'] = 'delete'
        ds['foo'] = None
        res = widget.validate(ds)
        self.assert_(res)
        self.assertEquals(dm.keys(), ['bar'])
        self.assertEquals(dm['bar'], None)

    def test_CPSImageWidget_validate_email_render(self):
        from Products.CPSSchemas.widgets.image import CPSImageWidget
        from Products.CPSSchemas.BasicWidgets import CPSStringWidget
        from Products.CPSSchemas.Layout import Layout
        layout = Layout()
        layout.mimetypes_registry = FakeMimeTypeRegistry()
        layout.addSubObject(CPSImageWidget('foo'))
        layout.addSubObject(CPSStringWidget('foo_size'))
        widget = layout['foo']
        size_widget = layout['foo_size']
        widget.fields = ['bar']
        widget.widget_ids = ['foo_size']
        size_widget.fields = ['size']

        dm = FakeDataModel()
        dm._adapters = [FakeAdapter({'bar': 'thatsme', 'size': 'w480'})]
        dm.proxy = 'someproxy'
        dm['bar'] = None
        dm['size'] = 'w480'
        ds = FakeDataStructure(dm)
        f = StringIO(TEST_IMAGE)
        fu = FileUpload(FakeFieldStorage(f, 'search_popup.png'))
        ds['foo'] = fu
        ds['foo_title'] = 'im.png'
        ds['foo_choice'] = 'change'
        ds['foo_filename'] = 'search_popup.png'
        ds['foo_size'] = 'full' # easy first round

        # now validate in order to put something appropriate in datamodel
        self.assertTrue(widget.validate(ds))
        self.assertEquals(dm['bar'].data, TEST_IMAGE)
        self.assertEquals(dm['size'], 'full')

        # using a fake render method and having it return a dict, not an str !
        def widget_image_render(mode='', ds=None, **img_info):
            return img_info
        widget.widget_image_render = widget_image_render
        from Products.CPSSchemas.Widget import EMAIL_LAYOUT_MODE
        from Products.CPSSchemas.Widget import CIDPARTS_KEY

        # start with a fresh datastructure and render for email
        ds = FakeDataStructure(dm)
        widget.prepare(ds)
        rendered = widget.render('view', ds, layout_mode=EMAIL_LAYOUT_MODE)

        # Extraction and assertions
        # image properly dumped in dict for cid parts
        parts = ds.get(CIDPARTS_KEY)
        self.assertFalse(parts is None)
        self.assertEquals(len(parts), 1)
        cid, part = parts.items()[0]
        self.assertEquals(part['content'], TEST_IMAGE)
        self.assertEquals(part['content-type'], 'image/png')

        # URL for final rendering is consistent
        self.assertEquals(rendered,
                          '<img src="cid:%s" alt="" />' % cid)

        # Now intercept the call to image.resize() to check with a less trivial
        # size spec
        from Products.CPSSchemas.widgets import image
        orig_resize = image.image_resize
        def resize(src, width, height, resized_id, raw=False):
            return 'Resized w=%d, h=%d' % (width, height)
        image.image_resize = resize
        dm['size'] = '320x200'
        ds = FakeDataStructure(dm)
        widget.prepare(ds)

        rendered = widget.render('view', ds, layout_mode=EMAIL_LAYOUT_MODE)
        parts = ds.get(CIDPARTS_KEY)
        self.assertFalse(parts is None)
        self.assertEquals(len(parts), 1)
        cid, part = parts.items()[0]
        self.assertEquals(part['content'], 'Resized w=320, h=200')

        # cleanup
        image.resize = orig_resize

        # delete image from datastructure and check that we can still render
        ds['foo'] = None
        del ds[CIDPARTS_KEY]
        rendered = widget.render('view', ds, layout_mode=EMAIL_LAYOUT_MODE)
        parts = ds.get(CIDPARTS_KEY)
        self.assertTrue(parts is None or cid not in parts)

    def testSubjectWidget(self):
        from Products.CPSSchemas.ExtendedWidgets import CPSSubjectWidget
        folder = Folder()
        fakePortal.default_charset = 'unicode'
        wid = CPSSubjectWidget('foo').__of__(fakePortal)
        link = wid.getSubjectSearchLink(u'events', '\xc3\x89v\xc3\xa9nements')

doctest_globs=dict(portal=fakePortal)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestWidgets),
        doctest.DocTestSuite('Products.CPSSchemas.ExtendedWidgets'),
        doctest.DocFileTest('doc/developer/indirect_widget.txt',
                            package='Products.CPSSchemas',
                            globs=doctest_globs,
                            optionflags=(doctest.NORMALIZE_WHITESPACE|
                                         doctest.ELLIPSIS)),
        ))


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
