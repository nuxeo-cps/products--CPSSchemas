# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
import CPSSchemasTestCase

from Products.CPSSchemas.WidgetTypesTool import WidgetTypeRegistry

class TestWidgetTypesTool(CPSSchemasTestCase.CPSSchemasTestCase):

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

    def testTool(self):
        tool = self.portal.portal_widget_types
        amt = tool.all_meta_types()

    def _makeWidget(self, widget_id, widget_type):
        widget_type_instance = WidgetTypeRegistry.makeWidgetTypeInstance(
            widget_type, "widget_type_id")
        widget = widget_type_instance.makeInstance(widget_id)
        return widget

    def testStringWidget(self):
        widget = self._makeWidget("widget_id", "CPS String Widget Type")
        self.assertEquals(widget.getWidgetId(), "widget_id")


def test_suite():
    suites = [unittest.makeSuite(TestWidgetTypesTool)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
