# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Testing.ZopeTestCase import ZopeLite

from Products.CPSDocument.Layout import BasicLayout
#from Products.CPSDocument.CPSDocument import CPSDocument
#from Products.CPSDocument.Template import Template
from Products.CPSDocument.DataModel import DataModel
from Products.CPSDocument.Schema import Schema
from Products.CPSDocument.DataStructure import DataStructure
from Products.CPSDocument.Renderer import BasicRenderer
from Products.CPSDocument.Fields.BasicField import BasicField, BasicFieldWidget
from Products.CPSDocument.Fields.TextField import TextField, TextFieldWidget
from Products.CPSDocument.Fields.SelectionField import SelectionField, SelectionFieldWidget

class RenderingTests(unittest.TestCase):
    """Rendering tests

    Not strictly unit tests, since they involve many units, but there you go...
    That's also why I have it in one separate test module.
    Very handy and practical to have in any case.
    The tests are numbered so they are executed in sequentially higher levels
    of complexity. This is to ensure that the first error points as closely
    as possible to the source of the error.

    """

    # The 01 to 49 tests: Test fields with a BasicRenderer.
    def test_01_BasicFieldRendering(self):
        f1 = BasicField('f1', 'Field1')
        fw1 = BasicFieldWidget(f1)
        renderer = BasicRenderer
        res = fw1.render(renderer, f1, 'Field1', None)
        self.failUnless(res == 'Field1 None', 'BasicField view render failed')
        fw1.setRenderMode('edit')
        res = fw1.render(renderer, f1, 'Field1', None)
        self.failUnless(res == '[Field1] None', 'BasicField edit render failed')

    def test_02_TextFieldRendering(self):
        f1 = TextField('f1', 'Field1')
        fw1 = TextFieldWidget(f1)
        renderer = BasicRenderer
        res = fw1.render(renderer, f1, 'Field1', None)
        self.failUnless(res == 'Field1\n', 'TextField view render failed')
        fw1.setRenderMode('edit')
        res = fw1.render(renderer, f1, 'Field1', None)
        self.failUnless(res == '[Field1]\n', 'TextField edit render failed')

    def test_03_SelectionFieldRendering(self):
        f1 = SelectionField('f1', 'Field1')
        f1.setOptions( ['Field1', 'Field2', 'Field3'] )
        fw1 = SelectionFieldWidget(f1)
        renderer = BasicRenderer
        res = fw1.render(renderer, f1, 'Field1', None)
        self.failUnless(res == 'Field1\n', 'TextField view render failed')
        fw1.setRenderMode('edit')
        res = fw1.render(renderer, f1, 'Field1', None)
        self.failUnless(res == '*Field1\n Field2\n Field3\n', 
            'TextField edit render failed')


    # The 50 to 99 test: Tests rendering of complete layouts and documents
    def test_50_LayoutRendering(self):
        layout = BasicLayout('id', 'title')
        schema = Schema('schema', 'Schema')
        f1 = TextField('f1', 'Field1')
        f2 = TextField('f2', 'Field2')
        f3 = SelectionField('f3', 'Field3')
        f3.setOptions( ['Value1', 'Value2', 'Value3'])
        schema['f1'] = f1
        schema['f2'] = f2
        schema['f3'] = f3
        model = DataModel()
        model.addSchema(schema)
        layout['f1'] = TextFieldWidget(f1)
        layout['f2'] = TextFieldWidget(f2)
        layout['f3'] = SelectionFieldWidget(f3)
        data = DataStructure({'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'},  \
                             {'f1': None, 'f2': 'An error', 'f3': None})

        render = layout.render(model, data)
        self.failUnless(render == 'Value1\nValue2\nValue3\n', 'View render failed')

        layout['f1'].setRenderMode('edit')
        layout['f2'].setRenderMode('edit')
        layout['f3'].setRenderMode('edit')
        render = layout.render(model, data)
        self.failUnless(render == '[Value1]\n[Value2]\n Value1\n Value2\n*Value3\n',\
                        'Edit render failed')


def test_suite():
    return unittest.makeSuite(RenderingTests)

if __name__=="__main__":
    unittest.main(defaultTest)
