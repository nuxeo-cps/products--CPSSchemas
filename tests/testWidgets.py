# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
import CPSSchemasTestCase

from Products.CPSSchemas.WidgetTypesTool import WidgetTypeRegistry

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
            self.tool.manage_addCPSWidgetType(id, swt)


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
