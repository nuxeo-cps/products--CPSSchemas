# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
import CPSSchemasTestCase

from DateTime.DateTime import DateTime
from OFS.Folder import Folder
from OFS.Image import Image, File
from Products.CPSSchemas import BasicFields
from Products.CPSSchemas.Field import FieldRegistry


class BasicFieldTests(CPSSchemasTestCase.CPSSchemasTestCase):

    def afterSetUp(self):
        fields = Folder('fields')
        self.portal._setObject('fields', fields)
        self.fields = self.portal.fields

    def testCreationThroughRegistry(self):
        for field_type in FieldRegistry.listFieldTypes():
            field_id = field_type.lower().replace(" ", "")
            field = FieldRegistry.makeField(field_type, field_id)
            self.fields._setObject(field_id, field)
            field = getattr(self.fields, field_id)

            self.assertEquals(field.getId(), field_id)

            # Default values (0, 0.0, None, ""...) all have false boolean
            # value
            default = field.getDefault()
            self.assert_(not default)

            self.assertEquals(field.validate(default), default)


    def testIntField(self):
        field = BasicFields.CPSIntField('the_id')
        self.fields._setObject('the_id', field)
        field = getattr(self.fields, 'the_id')

        self.assertEquals(field.id, 'the_id')
        self.assertEquals(field.getFieldId(), 'the_id')

        self.assertEquals(field.getDefault(), 0)

        # Basic validation
        self.assertEquals(field.validate(121), 121)
        self.assertRaises(ValueError, field.validate, "1")

    def testLongField(self):
        field = BasicFields.CPSLongField('the_id')
        self.fields._setObject('the_id', field)
        field = getattr(self.fields, 'the_id')

        self.assertEquals(field.getDefault(), 0L)
        self.assertEquals(field.validate(121L), 121L)
        self.assertRaises(ValueError, field.validate, 1)

    def testFloatField(self):
        field = BasicFields.CPSFloatField('the_id')
        self.fields._setObject('the_id', field)
        field = getattr(self.fields, 'the_id')

        self.assertEquals(field.getDefault(), 0.0)
        self.assertEquals(field.validate(1.0), 1.0)
        self.assertRaises(ValueError, field.validate, 1)

    def testStringField(self):
        field = BasicFields.CPSStringField('the_id')
        self.fields._setObject('the_id', field)
        field = getattr(self.fields, 'the_id')

        self.assertEquals(field.getDefault(), "")
        self.assertEquals(field.validate('bimbo'), 'bimbo')
        self.assertRaises(ValueError, field.validate, None)

    # XXX: no difference between a StringField and a PasswordField.
    # Strange, no ?
    def testPasswordField(self):
        field = BasicFields.CPSPasswordField('the_id')
        self.fields._setObject('the_id', field)
        field = getattr(self.fields, 'the_id')

        self.assertEquals(field.getDefault(), "")
        self.assertEquals(field.validate('bimbo'), 'bimbo')
        self.assertRaises(ValueError, field.validate, None)

    def testStringListField(self):
        field = BasicFields.CPSStringListField('the_id')
        self.fields._setObject('the_id', field)
        field = getattr(self.fields, 'the_id')

        self.assertEquals(field.getDefault(), [])
        self.assertEquals(field.validate(['a', 'b']), ['a', 'b'])
        self.assertRaises(ValueError, field.validate, None)
        self.assertRaises(ValueError, field.validate, [1])

    def testDateTimeField(self):
        field = BasicFields.CPSDateTimeField('the_id')
        self.fields._setObject('the_id', field)
        field = getattr(self.fields, 'the_id')

        self.assertEquals(field.getDefault(), None)

        # XXX: A bit strange. Do we really want that one ?
        self.assertEquals(field.validate(""), None)

        self.assertEquals(field.validate(None), None)
        now = DateTime()
        self.assertEquals(field.validate(now), now)
        self.assertRaises(ValueError, field.validate, [1])

    def testFileField(self):
        field = BasicFields.CPSFileField('the_id')
        self.fields._setObject('the_id', field)
        field = getattr(self.fields, 'the_id')

        self.assertEquals(field.getDefault(), None)

        # XXX: A bit strange. Do we really want this behaviour ?
        self.assertEquals(field.validate(""), None)

        self.assertEquals(field.validate(None), None)

        file = File("", "", "")
        self.assertEquals(field.validate(file), file)
        self.assertRaises(ValueError, field.validate, [1])

        # TODO: add test for "dependant fields" there.


    def testImageField(self):
        field = BasicFields.CPSImageField('the_id')
        self.fields._setObject('the_id', field)
        field = getattr(self.fields, 'the_id')

        self.assertEquals(field.getDefault(), None)

        # XXX: A bit strange. Do we really want is behaviour ?
        self.assertEquals(field.validate(""), None)

        self.assertEquals(field.validate(None), None)

        image = Image("", "", "")
        self.assertEquals(field.validate(image), image)
        self.assertRaises(ValueError, field.validate, [1])

def test_suite():
    suites = [unittest.makeSuite(BasicFieldTests)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
