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
import CPSSchemasTestCase

from Products.CPSSchemas.WidgetTypesTool import WidgetTypeRegistry
from Products.CPSSchemas.Widget import Widget
from Products.CPSSchemas.DataModel import DataModel

class TestWidgetTypesTool(CPSSchemasTestCase.CPSSchemasTestCase):

    def afterSetUp(self):
        self.tool = self.portal.portal_widget_types

        # Delete widget types that has already been set up by the CPSDocument
        # installer.
        self.tool.manage_delObjects(ids=list(self.tool.objectIds()))

        # Refill the tool with the widgets using only default values.
        amt = self.tool.all_meta_types()
        for d in amt:
            widget_type = d['name']
            swt = widget_type.replace(" ", "")
            id = widget_type[len("CPS "):-len(" Type")]
            # XXX AT: tests fail using zopectl. It seems like all_meta_types
            # returns the meta_type list twice. Did not investigate further to
            # see if this is because widget types are registered twice.
            self.tool.manage_addCPSWidgetType(id, swt)


    def test_getCssClass(self):
        # create a bare widget, and set it in the portal to be able to create
        # the expression namespace
        widget = Widget('widget_id', widgettype='dummy_type')
        self.portal._setOb('widget_id', widget)
        widget = self.portal._getOb('widget_id')
        # dummy datamodel to be passed to the expression
        dm = DataModel(ob=self.portal, proxy=None)
        layout_mode = 'view'

        # just use css_class
        self.assertEquals(widget.getCssClass('view', dm), '')
        kw = {'css_class': 'stringClass'}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.getCssClass('view', dm), 'stringClass')
        self.assertEquals(widget.getCssClass('create', dm), 'stringClassEdit')
        self.assertEquals(widget.getCssClass('edit', dm), 'stringClassEdit')

        # just use css_class_expr
        kw = {'css_class': '', 'css_class_expr': 'string:exprClass'}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.getCssClass('view', dm), 'exprClass')
        self.assertEquals(widget.getCssClass('edit', dm), 'exprClass')

        # use both properties
        kw = {'css_class': 'stringClass', 'css_class_expr': 'string:exprClass'}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.getCssClass('view', dm), 'exprClass')
        self.assertEquals(widget.getCssClass('edit', dm), 'exprClass')

        kw = {'css_class': 'stringClass', 'css_class_expr': 'nothing'}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.getCssClass('view', dm), '')
        self.assertEquals(widget.getCssClass('edit', dm), '')

        # use non dummy expressions :)
        kw = {'css_class': 'stringClass',
              'css_class_expr': "python:layout_mode == 'view' and 'viewExprClass' or nothing"}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.getCssClass('view', dm), 'viewExprClass')
        self.assertEquals(widget.getCssClass('edit', dm), '')

        kw = {'css_class': 'stringClass',
              'css_class_expr': "python:layout_mode == 'search' and 'searchExprClass' or nothing"}
        widget.manage_changeProperties(**kw)
        self.assertEquals(widget.getCssClass('view', dm), '')
        self.assertEquals(widget.getCssClass('edit', dm), '')
        self.assertEquals(widget.getCssClass('search', dm), 'searchExprClass')


    def testRegistry(self):
        registry = WidgetTypeRegistry

        for widget_type in registry.listWidgetTypes():
            widget_class = registry.getClass(widget_type)

            # There is a naming pattern here. Someone may want to break
            # it though, but I don't know why someone would want to do it.
            self.assertEquals(widget_class.meta_type + " Type", widget_type)

            widget_type_instance = \
                registry.makeWidgetTypeInstance(widget_type, "widget_type_id")

            self.assertEquals(widget_type_instance.meta_type, 
                widget_class.meta_type + " Type")

            widget = widget_type_instance.makeInstance("widget_id")
            self.assert_(isinstance(widget, widget_class))

            # XXX: doesn't work if the widget type doesn't live in
            # portal_widget_types
            # field_types = widget.getFieldTypes()


    def testStringWidget(self):
        widget = self.tool["String Widget"].makeInstance("widget_id")
        self.assertEquals(widget.getWidgetId(), "widget_id")
        self.assertEquals(widget.getFieldTypes(), ('CPS String Field',))

    def testIntWidget(self):
        widget = self.tool["Int Widget"].makeInstance("widget_id")
        self.assertEquals(widget.getWidgetId(), "widget_id")
        self.assertEquals(widget.getFieldTypes(), ('CPS Int Field',))

    def testLongWidget(self):
        widget = self.tool["Long Widget"].makeInstance("widget_id")
        self.assertEquals(widget.getWidgetId(), "widget_id")
        self.assertEquals(widget.getFieldTypes(), ('CPS Long Field',))

    def testFloatWidget(self):
        widget = self.tool["Float Widget"].makeInstance("widget_id")
        self.assertEquals(widget.getWidgetId(), "widget_id")
        self.assertEquals(widget.getFieldTypes(), ('CPS Float Field',))


def test_suite():
    suites = [unittest.makeSuite(TestWidgetTypesTool)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
