# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Products.NuxCPS3Document.Layout import BasicLayout
from Products.NuxCPS3Document.NuxCPS3Document import NuxCPS3Document
from Products.NuxCPS3Document.Template import Template
from Products.NuxCPS3Document.Fields.TextField import TextField, TextFieldWidget
from Products.NuxCPS3Document.Fields.SelectionField import SelectionField, SelectionFieldWidget

class RenderingTests(unittest.TestCase):
    """Rendering tests

    Not strictly unit tests, since they involve many units, but there you go...
    Very handy and practical to have in any case.
    """

    def testRendering(self):
        template = Template('id', 'title')
        layout = BasicLayout('id', 'title')

        f1 = TextField('f1', 'Field1')
        f2 = TextField('f2', 'Field2')
        f3 = SelectionField('f3', 'Field3')
        f3.setValues( ['Value1', 'Value2', 'Value3'])

        struct = template.getStructure()
        struct['f1'] = f1
        struct['f2'] = f2
        struct['f3'] = f3
        layout['f1'] = TextFieldWidget(f1)
        layout['f2'] = TextFieldWidget(f2)
        layout['f3'] = SelectionFieldWidget(f3)

        doc = NuxCPS3Document('id', 'title', template )
        doc.setData( {'f1': 'Value1', 'f2': 'Value2', 'f3': 'Value3'} )

        render = layout.render(doc)
        self.failUnless(render == 'Value1\nValue2\nValue3\n', 'View render failed')

        layout['f1'].setRenderMode('edit')
        layout['f2'].setRenderMode('edit')
        layout['f3'].setRenderMode('edit')
        render = layout.render(doc)
        self.failUnless(render == '[Value1]\n[Value2]\n Value1\n Value2\n*Value3\n',\
                        'Edit render failed')

# Test TODO:
# Making sure only widgets connected to fields can be added.


def test_suite():
    return unittest.makeSuite(RenderingTests)

if __name__=="__main__":
    unittest.main(defaultTest)
