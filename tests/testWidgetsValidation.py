# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
import unittest
from Testing.ZopeTestCase import ZopeLite

from Products.CPSSchemas.DataStructure import DataStructure
from Products.CPSSchemas.BasicWidgets import CPSStringWidget
from Products.CPSSchemas.BasicWidgets import CPSBooleanWidget
from Products.CPSSchemas.ExtendedWidgets import CPSTextWidget

class TestWidgetsValidation(unittest.TestCase):
    """Tests validate method of widgets"""

    def _makeStringWidget(self, id, properties):
        widget = CPSStringWidget(id, "String Widget")
        widget.manage_changeProperties(**properties)
        return widget

    def _makeDataStructure(self, data):
        return DataStructure(data, datamodel={})

    def _validate(self, type, properties, value):
        id = 'f'
        ds = self._makeDataStructure({id: value})
        properties.update({'fields': id})
        if type == 'String':
            widget = CPSStringWidget(id, '')
        elif type == 'Boolean':
            widget = CPSBooleanWidget(id, '')
        elif type == 'Text':
            widget = CPSTextWidget(id, '')
        widget.manage_changeProperties(**properties)
        ret = widget.validate(ds)
        err = ds.getError(id)
        return ret, err, ds


    ############################################################
    # StringWidget

    def test_string_ok_1(self):
        ret, err, ds = self._validate('String', {}, '12345')
        self.failUnless(ret, err)

    def test_string_ok_2(self):
        ret, err, ds = self._validate('String', {}, '')
        self.failUnless(ret, err)

    def test_string_ok_3(self):
        ret, err, ds = self._validate('String', {}, None)
        self.failUnless(ret, err)
        # check convertion None into ''
        self.failUnless(ds.getDataModel().values()[0] == '')

    def test_string_nok_1(self):
        ret, err, ds = self._validate('String', {}, {'a':1} )
        self.failUnless(err == 'cpsschemas_err_string')

    def test_string_size_max_ok_1(self):
        ret, err, ds = self._validate('String', {'size_max': 10}, '12345')
        self.failUnless(ret)

    def test_string_size_max_ok_2(self):
        ret, err, ds = self._validate('String', {'size_max': 10}, None)
        self.failUnless(ret)

    def test_string_size_max_ok_3(self):
        ret, err, ds = self._validate('String', {'size_max': 10}, '')
        self.failUnless(ret)

    def test_string_size_max_ok_4(self):
        ret, err, ds = self._validate('String', {'size_max': 10}, '1234567890')
        self.failUnless(ret)

    def test_string_size_max_nok_1(self):
        ret, err, ds = self._validate('String', {'size_max': 10}, '12345678901')
        self.failUnless(err=='cpsschemas_err_string_too_long')

    def test_string_size_max_nok_2(self):
        ret, err, ds  = self._validate('String', {'size_max': 10},
                                             '1234567890azerz')
        self.failUnless(err == 'cpsschemas_err_string_too_long')

    def test_string_required_ok_1(self):
        ret, err, ds = self._validate('String', {'is_required': 1}, '123')
        self.failUnless(ret)

    def test_string_required_nok_1(self):
        ret, err, ds = self._validate('String', {'is_required': 1}, '')
        self.failUnless(err == 'cpsschemas_err_required')

    def test_string_required_nok_2(self):
        ret, err, ds = self._validate('String', {'is_required': 1}, None)
        self.failUnless(err == 'cpsschemas_err_required')

    ############################################################
    # BooleanWidget

    def test_boolean_ok_1(self):
        ret, err, ds = self._validate('Boolean', {}, 0)
        self.failUnless(ret, err)

    def test_boolean_ok_2(self):
        ret, err, ds = self._validate('Boolean', {}, 1)
        self.failUnless(ret, err)

    def test_boolean_nok_1(self):
        ret, err, ds = self._validate('Boolean', {}, 2)
        self.failUnless(err == 'cpsschemas_err_boolean')

    def test_boolean_nok_2(self):
        ret, err, ds = self._validate('Boolean', {}, -1)
        self.failUnless(err == 'cpsschemas_err_boolean')

    def test_boolean_nok_3(self):
        ret, err, ds = self._validate('Boolean', {}, '')
        self.failUnless(err == 'cpsschemas_err_boolean')

    def test_boolean_nok_4(self):
        ret, err, ds = self._validate('Boolean', {}, None)
        self.failUnless(err == 'cpsschemas_err_boolean')

    def test_boolean_nok_5(self):
        ret, err, ds = self._validate('Boolean', {}, 'foo')
        self.failUnless(err == 'cpsschemas_err_boolean')

    def test_boolean_nok_5(self):
        ret, err, ds = self._validate('Boolean', {}, {'foo': 'sk'})
        self.failUnless(err == 'cpsschemas_err_boolean')

    ############################################################
    # TextWidget

    def test_text_ok_1(self):
        ret, err, ds = self._validate('String', {}, '12345')
        self.failUnless(ret, err)


def test_suite():
    return unittest.makeSuite(TestWidgetsValidation)

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
