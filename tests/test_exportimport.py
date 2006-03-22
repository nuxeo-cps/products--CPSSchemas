# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Author: Georges Racinet <gracinet@nuxeo.com>
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

from Products.CPSUtil.testing.genericsetup import TestXMLAdapter
from Products.CPSDefault.tests.CPSTestCase import CPSZCMLLayer

from Products.CPSSchemas.exportimport.schema import SchemaXMLAdapter
from Products.CPSSchemas.Schema import CPSSchema
from Products.CPSSchemas.BasicFields import CPSStringField
from Products.CPSSchemas.Layout import CPSLayout
from Products.CPSSchemas.BasicWidgets import CPSStringWidget
from Products.CPSSchemas.BasicWidgets import CPSLinesWidget
from Products.CPSSchemas.VocabulariesTool import VocabulariesTool


class TestSchemaXMLAdapter(TestXMLAdapter):
    #XXX we shouldn't depend on CPSDefault here
    layer = CPSZCMLLayer

    def buildObject(self):
        return CPSSchema('the_schema')

    def test_initFields_transtyping(self):
        self.setPurge(False)
        field = CPSStringField('the_field')

        field.manage_changeProperties(default_expr='string:abc')
        self.object.addSubObject(field)
        field = self.object['the_field']
        self.assertEquals(field.meta_type, 'CPS String Field')

        self.importString('<?xml version="1.0"?>'
                          ' <object name="the_schema">'
                          '  <field name="the_field"'
                          '         meta_type="CPS Int Field"/>'
                          ' </object>')

        field = self.object['the_field']
        self.assertEquals(field.meta_type, 'CPS Int Field')
        # pre-transtyping attributes are kept
        self.assertEquals(field.default_expr, 'string:abc')

    def test_initFields_notranstyping(self):
        # See #1526: no meta_type doesn't mean we want to transtype to ''
        self.setPurge(False)

        field = CPSStringField('the_field')
        field.manage_changeProperties(acl_write_roles='SomeRole')
        self.object.addSubObject(field)
        field = self.object['the_field']
        self.assertEquals(field.meta_type, 'CPS String Field')

        self.importString('<?xml version="1.0"?>'
                          ' <object name="the_schema">'
                          '  <field name="the_field">'
                          '   <property name="default_expr">'
                                'string:def'
                             '</property>'
                          '  </field>'
                          ' </object>')

        field = self.object['the_field']
        self.assertEquals(field.meta_type, 'CPS String Field')
        self.assertEquals(field.default_expr, 'string:def')
        # properties were merged
        self.assertEquals(field.acl_write_roles, 'SomeRole')

class TestLayoutXMLAdapter(TestXMLAdapter):
    layer = CPSZCMLLayer

    def buildObject(self):
        return CPSLayout('the_layout')

    def test_initWidgets_transtyping(self):
        self.setPurge(False)
        widget = CPSStringWidget('the_widget')

        widget.manage_changeProperties(label='abc')
        self.object.addSubObject(widget)
        widget = self.object['the_widget']
        self.assertEquals(widget.meta_type, 'String Widget')

        self.importString('<?xml version="1.0"?>'
                          ' <object name="the_layout">'
                          '  <widget name="the_widget"'
                          '         meta_type="Lines Widget"/>'
                          ' </object>')

        widget = self.object['the_widget']
        self.assertEquals(widget.meta_type, 'Lines Widget')
        # pre-transtyping attributes are kept
        self.assertEquals(widget.label, 'abc')

    def test_initWidgets_notranstyping(self):
        # See #1526: no meta_type doesn't mean we want to transtype to ''
        self.setPurge(False)

        widget = CPSStringWidget('the_widget')
        widget.manage_changeProperties(label='abc')
        self.object.addSubObject(widget)
        widget = self.object['the_widget']
        self.assertEquals(widget.meta_type, 'String Widget')

        self.importString('<?xml version="1.0"?>'
                          ' <object name="the_layout">'
                          '  <widget name="the_widget">'
                          '   <property name="label_edit">'
                                'def'
                              '</property>'
                          '  </widget>'
                          ' </object>')

        widget = self.object['the_widget']
        self.assertEquals(widget.meta_type, 'String Widget')
        self.assertEquals(widget.label_edit, 'def')
        # properties were merged
        self.assertEquals(widget.label, 'abc')

class TestVocabulariesToolXMLAdapter(TestXMLAdapter):
    layer = CPSZCMLLayer

    def buildObject(self):
        return VocabulariesTool('voc_tool')

    def test_remove_non_existent(self):
        # don't fail if trying to remove a non-existent sub-object
        self.importString('<?xml version="1.0"?>'
                          ' <object name="voc_tool">'
                          '   <object name="non-ex" remove="True"/>'
                          ' </object>')

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestSchemaXMLAdapter),
        unittest.makeSuite(TestLayoutXMLAdapter),
        unittest.makeSuite(TestVocabulariesToolXMLAdapter),
        ))

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())




