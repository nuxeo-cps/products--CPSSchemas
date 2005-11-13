# -*- coding: ISO-8859-15 -*-
# Copyright (c) 2004-2005 Nuxeo SARL <http://nuxeo.com>
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
from Acquisition import Implicit
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem

from Products.CPSSchemas.DataModel import DataModel
from Products.CPSSchemas.Widget import Widget


class FakePortal(Implicit):
    pass
fakePortal = FakePortal()

class FakeUrlTool(Implicit):
    def getPortalObject(self):
        return fakePortal

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

class TestWidgets(unittest.TestCase):

    def testStringWidget(self):
        from Products.CPSSchemas.BasicWidgets import CPSStringWidget
        widget = CPSStringWidget('foo')
        self.assertEquals(widget.getWidgetId(), 'foo')
        self.assertEquals(widget.getFieldTypes(), ('CPS String Field',))

    def testIntWidget(self):
        from Products.CPSSchemas.BasicWidgets import CPSIntWidget
        widget = CPSIntWidget('foo')
        self.assertEquals(widget.getWidgetId(), 'foo')
        self.assertEquals(widget.getFieldTypes(), ('CPS Int Field',))

    def testLongWidget(self):
        from Products.CPSSchemas.BasicWidgets import CPSLongWidget
        widget = CPSLongWidget('foo')
        self.assertEquals(widget.getWidgetId(), 'foo')
        self.assertEquals(widget.getFieldTypes(), ('CPS Long Field',))

    def testFloatWidget(self):
        from Products.CPSSchemas.BasicWidgets import CPSFloatWidget
        widget = CPSFloatWidget('foo')
        self.assertEquals(widget.getWidgetId(), 'foo')
        self.assertEquals(widget.getFieldTypes(), ('CPS Float Field',))

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

    def testFlashWidget(self):
        from Products.CPSSchemas.ExtendedWidgets import CPSFlashWidget
        widget = CPSFlashWidget('foo')
        self.assertEquals(widget.getWidgetId(), 'foo')
        self.assertEquals(widget.getFieldTypes(), ('CPS File Field',))

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




def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestWidgets),
        ))

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
