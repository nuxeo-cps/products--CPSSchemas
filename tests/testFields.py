# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
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
from OFS.Image import Image, File
from DateTime.DateTime import DateTime
from Products.CPSSchemas import BasicFields
from Products.CPSSchemas.Field import FieldRegistry


class FakePortal(Implicit):
    pass
fakePortal = FakePortal()

class FakeUrlTool(Implicit):
    def getPortalObject(self):
        return fakePortal
fakeUrlTool = FakeUrlTool()

fakePortal.portal_url = fakeUrlTool


class BasicFieldTests(unittest.TestCase):

    def makeOne(self, cls):
        field = cls('the_id')
        # Acquisition is needed for expression context computation
        # during fetch
        field = field.__of__(fakePortal)
        self.assertEquals(field.getFieldId(), 'the_id')
        return field

    def testCreation(self):
        for field_type in FieldRegistry.listFieldTypes():
            field_id = field_type.lower().replace(" ", "")
            field = FieldRegistry.makeField(field_type, field_id)
            # Acquisition is needed for expression context computation
            # during fetch
            field = field.__of__(fakePortal)

            self.assertEquals(field.getId(), field_id)

            # Default values (0, 0.0, None, ""...) all have false boolean
            # value
            default = field.getDefault()
            self.assert_(not default)

            # Check that default is valid
            self.assertEquals(field.validate(default), default)

    def testIntField(self):
        field = self.makeOne(BasicFields.CPSIntField)
        self.assertEquals(field.getDefault(), 0)
        self.assertEquals(field.validate(121), 121)
        self.assertRaises(ValueError, field.validate, "1")

    def testLongField(self):
        field = self.makeOne(BasicFields.CPSLongField)
        self.assertEquals(field.getDefault(), 0L)
        self.assertEquals(field.validate(121L), 121L)
        self.assertRaises(ValueError, field.validate, "1")
        self.assertRaises(ValueError, field.validate, 1) # XXX

    def testFloatField(self):
        field = self.makeOne(BasicFields.CPSFloatField)
        self.assertEquals(field.getDefault(), 0.0)
        self.assertEquals(field.validate(1.0), 1.0)
        self.assertRaises(ValueError, field.validate, 1)

    def testStringField(self):
        field = self.makeOne(BasicFields.CPSStringField)
        self.assertEquals(field.getDefault(), '')
        self.assertEquals(field.validate('bimbo'), 'bimbo')
        self.assertRaises(ValueError, field.validate, 0)
        self.assertRaises(ValueError, field.validate, None)

    def testPasswordField(self):
        # XXX So what's specific about password vs string ?
        field = self.makeOne(BasicFields.CPSPasswordField)
        self.assertEquals(field.getDefault(), '')
        self.assertEquals(field.validate('bimbo'), 'bimbo')
        self.assertRaises(ValueError, field.validate, 0)
        self.assertRaises(ValueError, field.validate, None)

    def testListField(self):
        field = self.makeOne(BasicFields.CPSListField)
        self.assertEquals(field.getDefault(), [])
        self.assertEquals(field.validate(['a', 'b']), ['a', 'b'])
        self.assertRaises(ValueError, field.validate, None)
        self.assertRaises(ValueError, field.validate, 1)
        self.assertRaises(ValueError, field.validate, (2,))

    def testStringListField(self):
        field = self.makeOne(BasicFields.CPSStringListField)
        self.assertEquals(field.getDefault(), [])
        self.assertEquals(field.validate(['a', 'b']), ['a', 'b'])
        self.assertRaises(ValueError, field.validate, None)
        self.assertRaises(ValueError, field.validate, [1])
        self.assertRaises(ValueError, field.validate, ('a',))

    def testListListField(self):
        field = self.makeOne(BasicFields.CPSListListField)
        self.assertEquals(field.getDefault(), [])
        self.assertEquals(field.validate([['a', 'b'], [1,3]]),
                          [['a', 'b'], [1,3]])
        self.assertRaises(ValueError, field.validate, None)
        self.assertRaises(ValueError, field.validate, [1])
        self.assertRaises(ValueError, field.validate, [(1,)])

    def testIntListListField(self):
        field = self.makeOne(BasicFields.CPSIntListListField)
        self.assertEquals(field.getDefault(), [])
        self.assertEquals(field.validate([[1, 3], [2]]), [[1, 3], [2]])
        self.assertRaises(ValueError, field.validate, None)
        self.assertRaises(ValueError, field.validate, [1])
        self.assertRaises(ValueError, field.validate, [(1,)])
        self.assertRaises(ValueError, field.validate, [['a']])

    def testDateTimeField(self):
        field = self.makeOne(BasicFields.CPSDateTimeField)
        self.assertEquals(field.getDefault(), None)
        self.assertEquals(field.validate(None), None)
        self.assertEquals(field.validate(""), None) # XXX
        now = DateTime()
        self.assertEquals(field.validate(now), now)
        self.assertRaises(ValueError, field.validate, [1])
        self.assertRaises(ValueError, field.validate, 'blob')

    def testFileField(self):
        field = self.makeOne(BasicFields.CPSFileField)
        self.assertEquals(field.getDefault(), None)
        self.assertEquals(field.validate(None), None)
        self.assertEquals(field.validate(""), None) # XXX
        file = File("", "", "")
        self.assertEquals(field.validate(file), file)
        self.assertRaises(ValueError, field.validate, [1])
        self.assertRaises(ValueError, field.validate, 'zzz')
        # TODO: add test for "dependant fields" there.

    def testImageField(self):
        field = self.makeOne(BasicFields.CPSImageField)
        self.assertEquals(field.getDefault(), None)
        self.assertEquals(field.validate(None), None)
        self.assertEquals(field.validate(""), None) # XXX
        image = Image("", "", "")
        self.assertEquals(field.validate(image), image)
        self.assertRaises(ValueError, field.validate, 'zzz')

    def testRangeListField(self):
        field = self.makeOne(BasicFields.CPSRangeListField)
        self.assertEquals(field.getDefault(), [])
        self.assertEquals(field.validate([(1,), (2, 5)]), [(1,), (2, 5)])
        self.assertRaises(ValueError, field.validate, None)
        self.assertRaises(ValueError, field.validate, [1])
        self.assertRaises(ValueError, field.validate, [()])
        self.assertRaises(ValueError, field.validate, [(1, 2, 3)])
        self.assertRaises(ValueError, field.validate, [[1], (2, 5)])
        self.assertRaises(ValueError, field.validate, [1, (2, 5)])

    def testCoupleField(self):
        field = self.makeOne(BasicFields.CPSCoupleField)
        self.assertEquals(field.getDefault(), [])
        self.assertEquals(field.validate([1,2]), [1,2])
        self.assertEquals(field.validate(['a','b']), ['a','b'])
        self.assertEquals(field.validate(['abc','bca']), ['abc','bca'])
        self.assertEquals(field.validate([['abc'],['bca']]), [['abc'],['bca']])
        self.assertRaises(ValueError, field.validate, None)
        self.assertRaises(ValueError, field.validate, 1)
        self.assertRaises(ValueError, field.validate, (1,2)) # XXX
        self.assertRaises(ValueError, field.validate, [1])
        self.assertRaises(ValueError, field.validate, ['a'])

def test_suite():
    suites = [unittest.makeSuite(BasicFieldTests)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
