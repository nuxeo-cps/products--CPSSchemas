import unittest
from Products.NuxCPS3Document.FlexibleLayout import FlexibleLayout
from Products.NuxCPS3Document.LayoutFields import LayoutField


class LayoutTests(unittest.TestCase):

    def testAddRemoveFields(self):
        """Make sure fields can be added and removed in the right order"""
        layout = FlexibleLayout()
        field1 = LayoutField(id='firstfield')
        field2 = LayoutField(id='secondfield')
        field3 = LayoutField(id='thirdfield')
        field4 = LayoutField(id='fourthfield')
        field5 = LayoutField(id='fifthfield')

        # Single fields as well as tuples and lists of fields
        # can be added.
        layout.addFields(field1)
        layout.addFields((field2, field3,))
        layout.addFields([field4, field5])

        fieldids = layout.getFieldIds()
        self.failUnless(fieldids == ['firstfield', 'secondfield', \
                                       'thirdfield', 'fourthfield', \
                                       'fifthfield' ], \
                                      'Fields were not added correctly' )

        layout.removeFields('secondfield' )
        fieldids = layout.getFieldIds()
        self.failUnless(fieldids == ['firstfield', 'thirdfield', \
                                       'fourthfield','fifthfield'],
                                      'Removal of field "secondfield" failed')

        layout.removeFields(('firstfield', 'fifthfield',))
        fieldids = layout.getFieldIds()
        self.failUnless(fieldids == ['thirdfield', 'fourthfield'], \
                                      'Removal of field tuple failed')

        layout.removeFields(['thirdfield', 'fourthfield'])
        fieldids = layout.getFieldIds()
        self.failIf(fieldids, 'Removal of field list failed')

    def testAddConflictingField(self):
        """Adding a field with an id that exists should fail"""
        layout = FlexibleLayout()
        field1 = LayoutField(id='firstfield')
        field2 = LayoutField(id='firstfield')
        self.assertRaises(KeyError, layout.addFields, (field1, field2,))

    def testRemovingNonExistandFields(self):
        """Removing a field that does not exist should fail"""
        layout = FlexibleLayout()
        field1 = LayoutField(id='firstfield')
        field2 = LayoutField(id='secondfield')
        layout.addFields((field1, field2,))
        self.assertRaises(KeyError, layout.removeFields, 'thirdfield')

    def testReorderFields(self):
        """Reordering fields"""
        layout = FlexibleLayout()
        field1 = LayoutField(id='firstfield')
        field2 = LayoutField(id='secondfield')
        field3 = LayoutField(id='thirdfield')
        field4 = LayoutField(id='fourthfield')
        field5 = LayoutField(id='fifthfield')
        layout.addFields( [field1, field2, field3, field4, field5])

        fieldids = layout.getFieldIds()
        self.failUnless(fieldids == ['firstfield', 'secondfield', \
                                       'thirdfield', 'fourthfield', \
                                       'fifthfield' ], \
                                      'Fields were not added correctly' )

        layout.setFieldOrder('fourthfield', -1)
        fieldids = layout.getFieldIds()
        self.failUnless(fieldids == ['firstfield', 'secondfield', \
                                       'thirdfield', 'fifthfield', \
                                       'fourthfield' ], \
                                      'SeFieldOrder to last failed' )

        layout.setFieldOrder('fourthfield', 6)
        fieldids = layout.getFieldIds()
        self.failUnless(fieldids == ['firstfield', 'secondfield', \
                                       'thirdfield', 'fifthfield', \
                                       'fourthfield' ], \
                                      'SeFieldOrder to after last failed' )

        layout.setFieldOrder('fourthfield', 1)
        fieldids = layout.getFieldIds()
        self.failUnless(fieldids == ['firstfield', 'fourthfield', \
                                       'secondfield', 'thirdfield', \
                                       'fifthfield' ], \
                                      'SeFieldOrder failed' )


        layout.moveField('thirdfield', -2)
        fieldids = layout.getFieldIds()
        self.failUnless(fieldids == ['firstfield', 'thirdfield', \
                                       'fourthfield', 'secondfield', \
                                       'fifthfield' ], \
                                      'Negative moveField failed' )

        layout.moveField('firstfield', 2)
        fieldids = layout.getFieldIds()
        self.failUnless(fieldids == ['thirdfield', 'fourthfield', \
                                       'firstfield', 'secondfield', \
                                       'fifthfield' ], \
                                      'Positive moveField failed' )

        layout.moveField('firstfield', 7)
        fieldids = layout.getFieldIds()
        self.failUnless(fieldids == ['thirdfield', 'fourthfield', \
                                       'secondfield', 'fifthfield', \
                                       'firstfield' ], \
                                      'Beyond end moveField failed' )

        layout.moveField('secondfield', -7)
        fieldids = layout.getFieldIds()
        self.failUnless(fieldids == ['secondfield', 'thirdfield', \
                                       'fourthfield', 'fifthfield', \
                                       'firstfield' ], \
                                      'Beyond beginning moveField failed' )

        layout.setFieldOrder('fourthfield', 0)
        fieldids = layout.getFieldIds()
        self.failUnless(fieldids == ['fourthfield', 'secondfield', \
                                       'thirdfield', 'fifthfield', \
                                       'firstfield' ], \
                                      'setFieldOrder first failed' )

    def testReorderNonExistingFields(self):
        """Reordering fields that does not exist should raise errors"""
        layout = FlexibleLayout()
        field1 = LayoutField(id='firstfield')
        field2 = LayoutField(id='secondfield')
        layout.addFields((field1, field2,))
        self.assertRaises(ValueError, layout.setFieldOrder, 'thirdfield', 7)
        self.assertRaises(ValueError, layout.moveField, 'thirdfield', -2)

    def testAccessFields(self):
        layout = FlexibleLayout()
        field1 = LayoutField(id='firstfield')
        field2 = LayoutField(id='secondfield')
        field3 = LayoutField(id='thirdfield')
        layout.addFields((field1, field2, field3,))

        self.failUnlessEqual(layout.getField('secondfield').id(), 'secondfield', \
                             'Failed to retreive field "seconfield" by id' )

        fields = layout.getFields()
        fieldids = []
        for field in fields:
            fieldids.append(field.id())
        self.failUnlessEqual(fieldids, ['firstfield', 'secondfield', 'thirdfield'], \
                             'Retreived field list does not match actual field list')




def test_suite():
    return unittest.makeSuite(LayoutTests)

if __name__=="__main__":
    unittest.main(defaultTest)
