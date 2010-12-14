# (C) Copyright 2010 CPS-CMS Community <http://cps-cms.org/>
# Authors:
#     G. Racinet <georges@racinet.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Test CPSSchemas' zcml directives."""

import unittest
from zope.app.testing import placelesssetup
from Products.Five import zcml

import Products.CPSSchemas
from Products.CPSSchemas.Widget import Widget
from Products.CPSSchemas.Widget import widgetRegistry
from Products.CPSSchemas.Field import Field
from Products.CPSSchemas.Field import FieldRegistry

class FakeWidget(Widget):
    meta_type = "Fake Widget"

class FakeField(Field):
    meta_type = "Fake Field"

class WidgetDirectiveTestCase(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp()

    def tearDown(self):
        placelesssetup.tearDown()

    def test_registration(self):
        zcml.load_config('meta.zcml', Products.CPSSchemas)
        zcml.load_string(
            '<configure xmlns="http://namespaces.nuxeo.org/cps">'
            ' <widget'
            '  class="Products.CPSSchemas.tests.test_directives.FakeWidget"/>'
            '</configure>')
        self.assertEquals(widgetRegistry.getClass('Fake Widget'), FakeWidget)

class FieldDirectiveTestCase(unittest.TestCase):

    def setUp(self):
        placelesssetup.setUp()

    def tearDown(self):
        placelesssetup.tearDown()

    def test_registration(self):
        zcml.load_config('meta.zcml', Products.CPSSchemas)
        zcml.load_string(
            '<configure xmlns="http://namespaces.nuxeo.org/cps">'
            ' <field'
            '  class="Products.CPSSchemas.tests.test_directives.FakeField"/>'
            '</configure>')
        field = FieldRegistry.makeField('Fake Field', 'fid')
        self.assertEquals(field.__class__, FakeField)
        self.assertEquals(field.getId(), 'fid')

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(WidgetDirectiveTestCase),
        unittest.makeSuite(FieldDirectiveTestCase),
        ))
