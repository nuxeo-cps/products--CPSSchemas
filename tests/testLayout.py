# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest, os
from Products.CPSSchemas.Layout import Layout, CPSLayout
from Products.CPSSchemas.Schema import CPSSchema
from Products.CPSSchemas.DataStructure import DataStructure
from Products.CPSSchemas.DataModel import DataModel
from Products.CPSSchemas.StorageAdapter import AttributeStorageAdapter
from Acquisition import Implicit
from Testing.ZopeTestCase import ZopeTestCase
from Products.CPSSchemas.BasicWidgets import CPSStringWidgetType, \
     CPSIntWidgetType

from Products.CPSSchemas.tests import __file__ as landmark


class FakePortal(Implicit):
    pass
fakePortal = FakePortal()

class FakeUrlTool(Implicit):
    def getPortalObject(self):
        return fakePortal
fakeUrlTool = FakeUrlTool()
fakePortal.portal_url = fakeUrlTool

class FakeWidgetTypesTool(Implicit):
    def __getitem__(self,name):
        if name == 'Int Widget':
            return CPSIntWidgetType('int_factory')
        elif name == 'String Widget':
            return CPSStringWidgetType('string_factory')
        else:
            return None

fakeWidgetTypeTool = FakeWidgetTypesTool()
fakePortal.portal_widget_types = fakeWidgetTypeTool

class FakeDocument:
    f1 = 'f1class'

def openfile(filename, mode='r'):
    path = os.path.join(os.path.dirname(landmark), 'scripts', filename)
    return open(path, mode)

class LayoutTests(ZopeTestCase):

    def test_InstanciateLayout(self):
        """ simple Layout instanciation
        """
        ob = Layout()
        self.assertNotEquals(ob, None)

    def test_InstanciateCPSLayout(self):
        """ simple CPSLayout instanciation
        """
        ob = CPSLayout('my_layout')
        self.assertNotEquals(ob, None)

    def test_addingWidgets(self):
        """ adding a few widgets
        """
        ob = CPSLayout('my_layout').__of__(fakePortal)
        ob.addWidget('my_int', 'Int Widget')
        ob.addWidget('my_int2', 'Int Widget')
        ob.addWidget('my_string', 'String Widget')
        return ob

    def test_setLayoutDefinition(self):
        """ Validate setLayoutDefinition
        """
        layout = self.test_addingWidgets()

        # setting the layout definition
        layoutdef = layout.getLayoutDefinition()

        layoutdef['rows']= [[{'widget_id': 'my_int', 'ncols': 1},],
               [{'widget_id': 'my_int2', 'ncols': 1},],
               [{'widget_id': 'my_string', 'ncols': 1},]]

        layout.setLayoutDefinition(layoutdef)
        layoutdef = layout.getLayoutDefinition()
        layoutdef = layout.getLayoutDefinition()
        self.assertEquals(layoutdef['rows'],  [[{'widget_id': 'my_int', 'ncols': 1},],
                [{'widget_id': 'my_int2', 'ncols': 1},],
               [{'widget_id': 'my_string', 'ncols': 1},]])
        return layout

    def test_prepareLayoutWidgets(self):
        """ test prepareLayoutWidgets
        """
        doc = FakeDocument()
        layout = self.test_setLayoutDefinition()

        # settingup fields
        layout['my_int'].fields = ['my_int']
        layout['my_int2'].fields = ['my_int2']
        layout['my_string'].fields = ['my_string']

        # Acquisition is needed for expression context computation during fetch
        schema = CPSSchema('s1', 'Schema1').__of__(fakePortal)
        schema.addField('my_int', 'CPS Int Field')
        schema.addField('my_int2', 'CPS Int Field')
        schema.addField('my_string', 'CPS String Field')
        adapter = AttributeStorageAdapter(schema, doc, field_ids=schema.keys())
        dm = DataModel(doc, (adapter,))
        datastructure = DataStructure(datamodel=dm)
        dm['my_int'] = 13
        dm['my_int2'] = 23
        dm['my_string'] = 'sdfgtyhjkl'
        layout.prepareLayoutWidgets(datastructure)
        return layout, dm, datastructure

    def test_computeLayoutStructure(self):
        """ test computeLayoutStructure
        """
        layout_plus = self.test_prepareLayoutWidgets()
        layout = layout_plus[0]
        dm = layout_plus[1]
        ds = layout_plus[2]

        ls = layout.computeLayoutStructure('edit', dm)
        self.assertEquals(ls['widgets'].has_key('my_int'), True)
        self.assertEquals(ls['widgets'].has_key('my_string'), True)
        return layout, ls, dm, ds

    def test_validateLayoutStructure(self):
        """ test validateLayoutStructure
        """
        layout_plus = self.test_computeLayoutStructure()
        layout = layout_plus[0]
        ds = layout_plus[3]
        ls = layout_plus[1]

        validation = layout.validateLayoutStructure(ls, ds)
        self.assertEquals(validation, 1)


    def test_validateLayoutStructureWithScripting(self):
        """ test validateLayoutStructure with scripting
        """
        layout_plus = self.test_computeLayoutStructure()
        layout = layout_plus[0]
        ds = layout_plus[3]
        ls = layout_plus[1]

        layout.validate_values_expr = "python:1"
        validation = layout.validateLayoutStructure(ls, ds)
        self.assertEquals(validation, 1)

        layout.validate_values_expr = "python:0"
        validation = layout.validateLayoutStructure(ls, ds)
        self.assertEquals(validation, 0)

        my_script = openfile('validateLayout.py')
        my_script_content = my_script.readlines()
        my_script_content = ''.join(my_script_content)

        layout.validate_values_expr = "python:datastructure['my_int'] > datastructure['my_int2']"
        validation = layout.validateLayoutStructure(ls, ds)
        self.assertEquals(validation, False)

        layout.validate_values_expr = "python:datastructure['my_int'] < datastructure['my_int2']"
        validation = layout.validateLayoutStructure(ls, ds)
        self.assertEquals(validation, True)

def test_suite():
    return unittest.makeSuite(LayoutTests)

if __name__=="__main__":
    unittest.main(defaultTest)
