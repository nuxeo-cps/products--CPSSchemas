# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Products.NuxCPS3Document.Layout import BasicLayout
from Products.NuxCPS3Document.Fields.TextField import TextField, TextFieldWidget
from Products.NuxCPS3Document.Fields.SelectionField import SelectionField, SelectionFieldWidget

class LayoutTests(unittest.TestCase):

    def testRendering(self):
        layout = BasicLayout('id', 'title')
        f1 = TextField('f1', 'Field1')
        f2 = TextField('f2', 'Field2')
        f3 = SelectionField('f3', 'Field3')
        f3.setValues( ['Value1', 'Value2', 'Value3'])

        layout['f1'] = TextFieldWidget(f1)
        layout['f2'] = TextFieldWidget(f2)
        layout['f3'] = SelectionFieldWidget(f3)
        data = {'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'}

        render = layout.render(data)
        self.failUnless(render == 'Value1\nValue2\nValue3\n', 'View render failed')

        layout['f1'].setRenderMode('edit')
        layout['f2'].setRenderMode('edit')
        layout['f3'].setRenderMode('edit')
        render = layout.render(data)
        self.failUnless(render == '[Value1]\n[Value2]\n Value1\n Value2\n*Value3\n',\
                        'Edit render failed')

# Test TODO:
# Making sure only widgets connected to fields can be added.


def test_suite():
    return unittest.makeSuite(LayoutTests)

if __name__=="__main__":
    unittest.main(defaultTest)
