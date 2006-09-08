# -*- coding: ISO-8859-15 -*-
# Copyright (c) 2004-2006 Nuxeo SAS <http://nuxeo.com>
# Authors: Florent Guillaume <fg@nuxeo.com>
#          Anahide Tchertchian <at@nuxeo.com>
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
from ZODB.tests.warnhook import WarningsHook
from Acquisition import Implicit
from cStringIO import StringIO
from OFS.Image import File
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
from ZPublisher.HTTPRequest import FileUpload

from Products.CPSSchemas.DataModel import DataModel
from Products.CPSSchemas.Widget import Widget


DUMMY_DICT = {'a': 'ZZZ', 'b': 'YYY', 'c': 'XXX'}

class FakePortal(Implicit):
    pass
fakePortal = FakePortal()

class FakeUrlTool(Implicit):
    def getPortalObject(self):
        return fakePortal

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

class FakeTranslationService:
    def getSelectedLanguage(self):
        return 'fr'

class FakeWidget(SimpleItem):
    hidden_empty = False
    def __init__(self, id, field_ids):
        self.id = id
        self.field_ids = field_ids
    def render(self, widget_mode, ds, **kw):
        return 'FakeWidget %s mode=%s val=%s' % (self.id, widget_mode,
                                                 ds[self.field_ids[0]])

class FakeLayout(Folder):
    pass

fakePortal.portal_url = FakeUrlTool()
fakePortal.portal_workflow = None
fakePortal.translation_service = FakeTranslationService()

class FakeDataStructure(dict):
    def __init__(self, datamodel):
        self.errs = {}
        self.datamodel = datamodel
    def getDataModel(self):
        return self.datamodel
    def setError(self, id, err):
        self.errs[id] = err

class FakeAdapter(object):
    def __init__(self, schema):
        self.schema = schema
    def getSchema(self):
        return self.schema
    def _getContentUrl(self, a, b, c=None):
        return 'http://url for %s %s %s' % (a, b, c)

class FakeDataModel(dict):
    _adapters = None
    proxy = None
    context = None
    def __init__(self, dm=None):
        if dm is not None:
            self.update(dm)
    def getProxy(self):
        return self.proxy
    def getObject(self):
        return self.proxy
    def getContext(self):
        return self.context

class FakeMimeTypeRegistry(Implicit):
    def lookupExtension(self, name):
        return 'testlookup/'+name[name.rfind('.')+1:].upper()

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
        self.assertEquals(res, "<img title='\xe0 doubl\xe9 \" quote' />")

        res = renderHtmlTag('img', title="a single ' quote")
        self.assertEquals(res, '<img title="a single \' quote" />')

    def testStringWidget(self):
        from Products.CPSSchemas.BasicWidgets import CPSStringWidget
        widget = CPSStringWidget('foo')
        self.assertEquals(widget.getWidgetId(), 'foo')
        self.assertEquals(widget.getFieldTypes(), ('CPS String Field',))

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
        expected = '<input type="hidden" name="widget__foo:tokens:default" value="" /><select multiple="multiple" name="widget__foo:list" id="widget__foo"><option selected="selected" value="a">ZZZ</option><option selected="selected" value="c">XXX</option><option selected="selected" value="b">YYY</option></select>'
        self.assertEquals(res, expected)

        kw = {'sorted': True}
        widget.manage_changeProperties(**kw)
        res = widget.render('view', ds)
        self.assertEquals(res, 'XXX, YYY, ZZZ')
        res = widget.render('edit', ds)
        expected = '<input type="hidden" name="widget__foo:tokens:default" value="" /><select multiple="multiple" name="widget__foo:list" id="widget__foo"><option selected="selected" value="c">XXX</option><option selected="selected" value="b">YYY</option><option selected="selected" value="a">ZZZ</option></select>'
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
        # XXX: add more tests here

    def test_CPSSearchLanguageWidget(self):
        from Products.CPSSchemas.SearchWidgets import CPSSearchLanguageWidget
        widget = CPSSearchLanguageWidget('foo').__of__(fakePortal)
        # XXX: add more tests here

    def test_CPSSearchSortWidget(self):
        from Products.CPSSchemas.SearchWidgets import CPSSearchSortWidget
        widget = CPSSearchSortWidget('foo').__of__(fakePortal)
        # XXX: add more tests here

    def test_CPSCompoundWidget(self):
        from Products.CPSSchemas.BasicWidgets import CPSCompoundWidget
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
            'size': len('thefilecontent'),
            'last_modified': '',
            'content_url': 'http://url for someproxy bar thefilename.txt',
            'mimetype': 'testlookup/TXT',
            })
        # Now without proxy nor object, for directory adapters
        dm.proxy = None
        context = Folder()
        context.id_field = 'hah'
        ds['hah'] = 'someentry'
        dm.context = context
        file_info = widget.getFileInfo(ds)
        self.assertEquals(file_info, {
            'empty_file': False,
            'session_file': False,
            'current_filename': 'thefilename.txt',
            'size': len('thefilecontent'),
            'last_modified': '',
            'content_url': 'http://url for someentry bar None',
            'mimetype': 'testlookup/TXT',
            })

        return

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


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestWidgets),
        ))

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
