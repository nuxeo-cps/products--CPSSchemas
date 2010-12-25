# Copyright (c) 2003-2005 Nuxeo SARL <http://nuxeo.com>
# Authors: Tarek Ziade <tz@nuxeo.com>
#          Florent Guillaume <fg@nuxeo.com>
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
from Products.CPSSchemas.Layout import CPSLayout
from Products.CPSSchemas.Schema import CPSSchema
from Products.CPSSchemas.DataStructure import DataStructure
from Products.CPSSchemas.DataModel import DataModel
from Products.CPSSchemas.StorageAdapter import AttributeStorageAdapter


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


class LayoutTests(unittest.TestCase):

    def makeLayoutOnlyWidgets(self):
        layout = CPSLayout('my_layout').__of__(fakePortal)
        layout.addWidget('my_int', 'Int Widget', fields=['my_int'])
        layout.addWidget('my_int2', 'Int Widget', fields=['my_int2'])
        layout.addWidget('my_string', 'String Widget', fields=['my_string'])
        return layout

    def makeLayout(self):
        layout = self.makeLayoutOnlyWidgets()
        layoutdef = {'ncols': 1, 'rows': [
            [{'widget_id': 'my_int', 'ncols': 1},],
            [{'widget_id': 'my_int2', 'ncols': 1},],
            [{'widget_id': 'my_string', 'ncols': 1},]]}
        layout.setLayoutDefinition(layoutdef)
        return layout

    def makeDataModelWithSchema(self):
        doc = FakeDocument()
        schema = CPSSchema('s1', 'Schema1').__of__(fakePortal)
        schema.addField('my_int', 'CPS Int Field')
        schema.addField('my_int2', 'CPS Int Field')
        schema.addField('my_string', 'CPS String Field')
        adapter = AttributeStorageAdapter(schema, doc, field_ids=schema.keys())
        dm = DataModel(doc, (adapter,))
        dm['my_int'] = 13
        dm['my_int2'] = 23
        dm['my_string'] = 'sdfgtyhjkl'
        return dm

    def makeDataStructure(self, dm):
        ds = DataStructure(datamodel=dm)
        return ds


    def test_InstanciateCPSLayout(self):
        ob = CPSLayout('my_layout')
        self.assertNotEquals(ob, None)

    def test_addingWidgets(self):
        layout = self.makeLayoutOnlyWidgets()
        self.assertEquals(layout.keys(), ['my_int', 'my_int2', 'my_string'])

    def test_setLayoutDefinition(self):
        layout = self.makeLayout()
        layoutdef = layout.getLayoutDefinition()
        self.assertEquals(layoutdef['ncols'], 1)
        self.assertEquals(layoutdef['rows'],
                          [[{'widget_id': 'my_int', 'ncols': 1},],
                           [{'widget_id': 'my_int2', 'ncols': 1},],
                           [{'widget_id': 'my_string', 'ncols': 1},]])

    def test_prepareLayoutWidgets(self):
        layout = self.makeLayout()
        dm = self.makeDataModelWithSchema()
        ds = self.makeDataStructure(dm)
        self.assertEquals(ds.get('my_int', 'none'), 'none')
        self.assertEquals(ds.get('my_int2', 'none'), 'none')
        self.assertEquals(ds.get('my_string', 'none'), 'none')
        self.failIf(ds.getError('my_int'))
        self.failIf(ds.getError('my_int2'))
        self.failIf(ds.getError('my_string'))
        layout.prepareLayoutWidgets(ds)
        self.assertEquals(ds['my_int'], '13')
        self.assertEquals(ds['my_int2'], '23')
        self.assertEquals(ds['my_string'], 'sdfgtyhjkl')
        self.failIf(ds.getError('my_int'))
        self.failIf(ds.getError('my_int2'))
        self.failIf(ds.getError('my_string'))

        # TODO should test widgets with errors

    def test_computeLayoutStructure(self):
        layout = self.makeLayout()
        dm = self.makeDataModelWithSchema()
        ds = self.makeDataStructure(dm)
        layout.prepareLayoutWidgets(ds)

        ls = layout.computeLayoutStructure('edit', dm)
        self.assertEquals(ls['widgets'].has_key('my_int'), True)
        self.assertEquals(ls['widgets'].has_key('my_string'), True)

    def test_computeLayoutStructure_missing(self):
        # test case where the table references a widget that's missing
        layout = self.makeLayout()
        layoutdef = {'ncols': 1, 'rows': [
            [{'widget_id': 'missing', 'ncols': 1},],
            [{'widget_id': 'my_int2', 'ncols': 1},],
            [{'widget_id': 'my_string', 'ncols': 1},]]}
        layout.setLayoutDefinition(layoutdef)
        dm = self.makeDataModelWithSchema()
        ds = self.makeDataStructure(dm)
        layout.prepareLayoutWidgets(ds)

        ls = layout.computeLayoutStructure('edit', dm)
        self.assertEquals(ls['widgets'].has_key('my_int'), True)
        self.assertEquals(ls['widgets'].has_key('my_string'), True)

    def test_validateLayoutStructure(self):
        layout = self.makeLayout()
        dm = self.makeDataModelWithSchema()
        ds = self.makeDataStructure(dm)
        layout.prepareLayoutWidgets(ds)
        ls = layout.computeLayoutStructure('edit', dm)

        validation = layout.validateLayoutStructure(ls, ds)
        self.assert_(validation)

        # TODO test a validation that fails because of a widget

    def test_validateLayoutStructure_global_validation(self):
        layout = self.makeLayout()
        dm = self.makeDataModelWithSchema()
        ds = self.makeDataStructure(dm)
        layout.prepareLayoutWidgets(ds)
        ls = layout.computeLayoutStructure('edit', dm)
        setlayprop = layout.manage_changeProperties

        setlayprop(validate_values_expr="python:1")
        validation = layout.validateLayoutStructure(ls, ds)
        self.assert_(validation, 1)

        setlayprop(validate_values_expr="python:0")
        validation = layout.validateLayoutStructure(ls, ds)
        self.failIf(validation)

        setlayprop(validate_values_expr=
               "python:datastructure['my_int'] > datastructure['my_int2']")
        validation = layout.validateLayoutStructure(ls, ds)
        self.failIf(validation)

        setlayprop(validate_values_expr=
               "python:datastructure['my_int'] < datastructure['my_int2']")
        validation = layout.validateLayoutStructure(ls, ds)
        self.assert_(validation)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LayoutTests),
        ))

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
