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

from xml.dom.minidom import Document
from xml.dom.minidom import Element
from xml.dom.minidom import parseString

from zope.app import zapi

from Products.GenericSetup.testing import DummySetupEnviron
from Products.GenericSetup.testing import DummyLogger
from Products.GenericSetup.testing import _AdapterTestCaseBase
from Products.CPSDefault.tests.CPSTestCase import CPSZCMLLayer

from Products.CPSSchemas.exportimport.schema import SchemaXMLAdapter
from Products.CPSSchemas.Schema import CPSSchema
from Products.CPSSchemas.BasicFields import CPSStringField
from Products.CPSSchemas.Layout import CPSLayout
from Products.CPSSchemas.BasicWidgets import CPSStringWidget
from Products.CPSSchemas.BasicWidgets import CPSLinesWidget

from Products.GenericSetup.interfaces import IBody

#monkey patching because CPSSchema's I/O likes BLATHER
#should end up in GenericSetup.testing at some point

def log(self, level, msg, *args, **kwargs):
    self._messages.append((level, self._id, msg))
DummyLogger.log = log


class TestSchemaXMLAdapter(unittest.TestCase):
    layer = CPSZCMLLayer

    def setUp(self):
        self.schema = CPSSchema('the_schema')
        self.environ = DummySetupEnviron()

        self.adapted = zapi.getMultiAdapter((self.schema, self.environ), IBody)

    def test_initFields_transtyping(self):
        field = CPSStringField('the_field')

        field.manage_changeProperties(default_expr='string:abc')
        self.schema.addSubObject(field)
        field = self.schema['the_field']
        self.assertEquals(field.meta_type, 'CPS String Field')

        root = parseString('<?xml version="1.0"?>'
                           ' <object name="the_schema">'
                           '  <field name="the_field"'
                           '         meta_type="CPS Int Field"/>'
                           ' </object>').documentElement
        self.adapted.node = root

        field = self.schema['the_field']
        self.assertEquals(field.meta_type, 'CPS Int Field')
        self.failIfEqual(field.default_expr, 'string:abc')

    def test_initFields_notranstyping(self):
        # See #1526: no meta_type doesn't mean we want to transtype to ''
        self.environ._should_purge = False

        field = CPSStringField('the_field')
        field.manage_changeProperties(acl_write_roles='SomeRole')
        self.schema.addSubObject(field)
        field = self.schema['the_field']
        self.assertEquals(field.meta_type, 'CPS String Field')

        root = parseString('<?xml version="1.0"?>'
                           ' <object name="the_schema">'
                           '  <field name="the_field">'
                           '   <property name="default_expr">'
                                'string:def'
                              '</property>'
                           '  </field>'
                           ' </object>').documentElement
        self.adapted.node = root

        field = self.schema['the_field']
        self.assertEquals(field.meta_type, 'CPS String Field')
        self.assertEquals(field.default_expr, 'string:def')
        # properties were merged
        self.assertEquals(field.acl_write_roles, 'SomeRole')

class TestLayoutXMLAdapter(unittest.TestCase):
    layer = CPSZCMLLayer

    def setUp(self):
        self.layout = CPSLayout('the_layout')
        self.environ = DummySetupEnviron()

        self.adapted = zapi.getMultiAdapter((self.layout, self.environ), IBody)

    def test_initWidgets_transtyping(self):
        widget = CPSStringWidget('the_widget')

        widget.manage_changeProperties(label='abc')
        self.layout.addSubObject(widget)
        widget = self.layout['the_widget']
        self.assertEquals(widget.meta_type, 'String Widget')

        root = parseString('<?xml version="1.0"?>'
                           ' <object name="the_layout">'
                           '  <widget name="the_widget"'
                           '         meta_type="Lines Widget"/>'
                           ' </object>').documentElement
        self.adapted.node = root

        widget = self.layout['the_widget']
        self.assertEquals(widget.meta_type, 'Lines Widget')
        self.failIfEqual(widget.label, 'abc')

    def test_initWidgets_notranstyping(self):
        # See #1526: no meta_type doesn't mean we want to transtype to ''
        self.environ._should_purge = False

        widget = CPSStringWidget('the_widget')
        widget.manage_changeProperties(label='abc')
        self.layout.addSubObject(widget)
        widget = self.layout['the_widget']
        self.assertEquals(widget.meta_type, 'String Widget')

        root = parseString('<?xml version="1.0"?>'
                           ' <object name="the_layout">'
                           '  <widget name="the_widget">'
                           '   <property name="label_edit">'
                                'def'
                              '</property>'
                           '  </widget>'
                           ' </object>').documentElement
        self.adapted.node = root

        widget = self.layout['the_widget']
        self.assertEquals(widget.meta_type, 'String Widget')
        self.assertEquals(widget.label_edit, 'def')
        # properties were merged
        self.assertEquals(widget.label, 'abc')

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestSchemaXMLAdapter),
        unittest.makeSuite(TestLayoutXMLAdapter),
        ))

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())




