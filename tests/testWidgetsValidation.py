# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
import unittest
from Testing.ZopeTestCase import ZopeLite

from Products.CPSSchemas.DataModel import DataModel
from Products.CPSSchemas.DataStructure import DataStructure
from Products.CPSSchemas.Schema import CPSSchema
from Products.CPSSchemas.BasicFields import CPSStringField
from Products.CPSSchemas.BasicWidgets import CPSStringWidget

class TestWidgetsValidation(unittest.TestCase):
    """Tests validate method of widgets"""

    def _makeStringWidget(self, id, properties):
        widget = CPSStringWidget(id, "String Widget")
        widget.manage_changeProperties(**properties)
        return widget

    def _makeDataStructure(self, data):
        return DataStructure(data, datamodel={})

    def _validateString(self, properties, value):
        ds = self._makeDataStructure({'f': value})
        properties.update({'fields': 'f'})
        widget = self._makeStringWidget('f', properties)
        ret = widget.validate(ds)
        err = ds.getError('f')
        return ret, err, ds

    def test_string_ok_1(self):
        ret, err, ds = self._validateString({}, '12345')
        self.failUnless(ret, err)

    def test_string_ok_2(self):
        ret, err, ds = self._validateString({}, '')
        self.failUnless(ret, err)

    def test_string_ok_3(self):
        ret, err, ds = self._validateString({}, None)
        self.failUnless(ret, err)
        # check convertion None into ''
        self.failUnless(ds.getDataModel().values()[0] == '')

    def test_string_nok_1(self):
        ret, err, ds = self._validateString({}, {'a':1} )
        self.failUnless(err == 'cpsschemas_err_string')

    def test_string_size_max_ok_1(self):
        ret, err, ds = self._validateString({'size_max': 10}, '12345')
        self.failUnless(ret)

    def test_string_size_max_ok_2(self):
        ret, err, ds = self._validateString({'size_max': 10}, None)
        self.failUnless(ret)

    def test_string_size_max_ok_3(self):
        ret, err, ds = self._validateString({'size_max': 10}, '')
        self.failUnless(ret)

    def test_string_size_max_ok_4(self):
        ret, err, ds = self._validateString({'size_max': 10}, '1234567890')
        self.failUnless(ret)

    def test_string_size_max_nok_1(self):
        ret, err, ds = self._validateString({'size_max': 10}, '12345678901')
        self.failUnless(err=='cpsschemas_err_string_too_long')

    def test_string_size_max_nok_2(self):
        ret, err, ds  = self._validateString({'size_max': 10},
                                             '1234567890azerz')
        self.failUnless(err == 'cpsschemas_err_string_too_long')

    def test_string_required_ok_1(self):
        ret, err, ds = self._validateString({'is_required': 1}, '123')
        self.failUnless(ret)

    def test_string_required_nok_1(self):
        ret, err, ds = self._validateString({'is_required': 1}, '')
        self.failUnless(err == 'cpsschemas_err_required')

    def test_string_required_nok_2(self):
        ret, err, ds = self._validateString({'is_required': 1}, None)
        self.failUnless(err == 'cpsschemas_err_required')


def test_suite():
    return unittest.makeSuite(TestWidgetsValidation)

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
