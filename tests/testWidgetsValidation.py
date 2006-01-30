# -*- coding: iso-8859-15 -*-
# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import os
import unittest

from Acquisition import Implicit
from OFS.Image import File

from Products.CPSSchemas.DataStructure import DataStructure
from Products.CPSSchemas.BasicWidgets import CPSStringWidget, \
     CPSBooleanWidget, CPSURLWidget, CPSEmailWidget, CPSPasswordWidget, \
     CPSIdentifierWidget, CPSFloatWidget
from Products.CPSSchemas.ExtendedWidgets import CPSRangeListWidget, \
     CPSTextWidget

from Products.CPSSchemas.ExtendedWidgets import CPSFlashWidget
from Products.CPSSchemas import tests as cpsschemas_tests
TEST_SWF = os.path.join(cpsschemas_tests.__path__[0], 'test.swf')

from Products.CPSSchemas.ExtendedWidgets import CPSDateTimeWidget

class FakePortal(Implicit):
    pass
fakePortal = FakePortal()

class FakeTranslationService:
    def getSelectedLanguage(self):
        return 'fr'
fakePortal.translation_service = FakeTranslationService()

class WidgetValidationTest(unittest.TestCase):
    """Tests validate method of widgets"""
    widget_type = None
    default_value = None

    def _validate(self, properties, value):
        id = 'ff'
        data = {id: value}
        ds = DataStructure(data, datamodel=data)
        properties.update({'fields': (id,)})
        widget = self.widget_type(id, **properties).__of__(fakePortal)

        ret = widget.validate(ds)
        err = ds.getError(id)
        return ret, err, ds

    def test_widget_ok_required_1(self):
        ret, err, ds = self._validate({'is_required': 0}, self.default_value)
        self.assertEquals(err, None)

    def test_widget_nok_required_1(self):
        ret, err, ds = self._validate({'is_required': 1}, self.default_value)
        self.assertEquals(err, 'cpsschemas_err_required')



class FloatWidgetValidationTest(WidgetValidationTest):
    widget_type = CPSFloatWidget

    def test_float_ok_1(self):
        ret, err, ds = self._validate({}, '12345.803')
        self.assert_(ret, err)

    def test_float_ok_2(self):
        ret, err, ds = self._validate({}, '12345')
        self.assert_(ret, err)

    def test_float_ok_3(self):
        ret, err, ds = self._validate({'decimals_separator': ','}, '12345,803')
        self.assert_(ret, err)

    def test_float_nok_1(self):
        ret, err, ds = self._validate({}, '12345,803')
        self.assert_(err)

    def test_float_nok_2(self):
        ret, err, ds = self._validate({'decimals_separator': ','}, '12345.803')
        self.assert_(ret, err)

    def test_widget_ok_required_1(self):
        ret, err, ds = self._validate({'is_required': 0}, '0.0')
        self.assertEquals(err, None)

    def test_widget_nok_required_1(self):
        ret, err, ds = self._validate({'is_required': 1}, '')
        self.assertEquals(err, 'cpsschemas_err_required')


class StringWidgetValidationTest(WidgetValidationTest):
    widget_type = CPSStringWidget

    def test_string_ok_1(self):
        ret, err, ds = self._validate({}, '12345')
        self.assert_(ret, err)

    def test_string_ok_2(self):
        ret, err, ds = self._validate({}, '')
        self.assert_(ret, err)

    def test_string_ok_3(self):
        ret, err, ds = self._validate({}, None)
        self.assert_(ret, err)
        # check convertion None into ''
        self.assertEquals(ds.getDataModel().values()[0], '')

    def test_string_nok_1(self):
        ret, err, ds = self._validate({}, {'a': 1} )
        self.assertEquals(err, 'cpsschemas_err_string')

    def test_string_size_max_ok_1(self):
        ret, err, ds = self._validate({'size_max': 10}, '12345')
        self.assert_(ret)

    def test_string_size_max_ok_2(self):
        ret, err, ds = self._validate({'size_max': 10}, None)
        self.assert_(ret, err)

    def test_string_size_max_ok_3(self):
        ret, err, ds = self._validate({'size_max': 10}, '')
        self.assert_(ret)

    def test_string_size_max_ok_4(self):
        ret, err, ds = self._validate({'size_max': 10}, '1234567890')
        self.assert_(ret)

    def test_string_size_max_nok_1(self):
        ret, err, ds = self._validate({'size_max': 10}, '12345678901')
        self.assertEquals(err, 'cpsschemas_err_string_too_long')

    def test_string_size_max_nok_2(self):
        ret, err, ds = self._validate({'size_max': 10}, '1234567890azerz')
        self.assertEquals(err, 'cpsschemas_err_string_too_long')

    def test_string_required_ok_1(self):
        ret, err, ds = self._validate({'is_required': 1}, '123')
        self.assert_(ret)

    def test_string_required_nok_1(self):
        ret, err, ds = self._validate({'is_required': 1}, '')
        self.assertEquals(err, 'cpsschemas_err_required')

    def test_string_required_nok_2(self):
        ret, err, ds = self._validate({'is_required': 1}, None)
        self.assertEquals(err, 'cpsschemas_err_required')

class BooleanWidgetValidationTest(WidgetValidationTest):
    widget_type = CPSBooleanWidget
    default_value = 0

    def test_widget_nok_required_1(self):
        pass

    def test_boolean_ok_1(self):
        ret, err, ds = self._validate({}, 0)
        self.assert_(ret, err)

    def test_boolean_ok_2(self):
        ret, err, ds = self._validate({}, 1)
        self.assert_(ret, err)

    def test_boolean_ok_3(self):
        ret, err, ds = self._validate({}, False)
        self.assert_(ret, err)

    def test_boolean_ok_4(self):
        ret, err, ds = self._validate({}, True)
        self.assert_(ret, err)

    def test_boolean_ok_5(self):
        ret, err, ds = self._validate({}, 2)
        self.assert_(ret, err)

    def test_boolean_ok_6(self):
        ret, err, ds = self._validate({}, -1)
        self.assert_(ret, err)

    def test_boolean_ok_7(self):
        ret, err, ds = self._validate({}, '')
        self.assert_(ret, err)

    def test_boolean_ok_8(self):
        ret, err, ds = self._validate({}, None)
        self.assert_(ret, err)

    def test_boolean_ok_9(self):
        ret, err, ds = self._validate({}, 'foo')
        self.assert_(ret, err)

    def test_boolean_ok_10(self):
        ret, err, ds = self._validate({}, {'foo': 'sk'})
        self.assert_(ret, err)

class TextWidgetValidationTest(WidgetValidationTest):
    widget_type = CPSTextWidget

    def test_text_ok_1(self):
        ret, err, ds = self._validate({}, '12345')
        self.assert_(ret, err)

    def test_text_ok_2(self):
        ret, err, ds = self._validate({}, '')
        self.assert_(ret, err)

    def test_text_ok_3(self):
        ret, err, ds = self._validate({}, None)
        self.assert_(ret, err)
        # check convertion None into ''
        self.assertEquals(ds.getDataModel().values()[0], '')

    def test_text_ok_4(self):
        text = r""" a strange text
	"[\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\'bof\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\',
	\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\'pic\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\r\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\nmqskldj
&amlzk; &nbsp; 	\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\r\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\nmqslk\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\']"]\\\\\\\\\\\\\\\',
	\\\\\\\\\\\\\\\'["[\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\'bof\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\',
	\\\\\\\_\\\\\\\\\\\\\\\\\\\\\\\\'pic\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\r\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\nmqskldj
	\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\r\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\nmqslk\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\']",
	"[\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\'bof\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\',
	\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\'pic\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\r\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\nmqskldj
)	\\\\\\\&piséoçç_sd)\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\r\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\nmqslk\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\']"]\\\\\\\\\\\\\\\',
	\\\\\\\\\\\\\\\'["[\\\\\\\\\\\\\\\\\\\\\\\
    """
        ret, err, ds = self._validate({}, text)
        self.assert_(ret, err)

    def test_text_nok_1(self):
        ret, err, ds = self._validate({}, {'a':1} )
        self.assertEquals(err, 'cpsschemas_err_string')

    def test_text_size_max_ok_1(self):
        ret, err, ds = self._validate({'size_max': 10}, '12345')
        self.assert_(ret)

    def test_text_size_max_ok_2(self):
        ret, err, ds = self._validate({'size_max': 10}, None)
        self.assert_(ret)

    def test_text_size_max_ok_3(self):
        ret, err, ds = self._validate({'size_max': 10}, '')
        self.assert_(ret)

    def test_text_size_max_ok_4(self):
        ret, err, ds = self._validate({'size_max': 10}, '1234567890')
        self.assert_(ret)

    def test_text_size_max_nok_1(self):
        ret, err, ds = self._validate({'size_max': 10}, '12345678901')
        self.assertEquals(err, 'cpsschemas_err_string_too_long')


class URLWidgetValidationTest(WidgetValidationTest):
    widget_type = CPSURLWidget

    def test_url_ok_1(self):
        ret, err, ds = self._validate({}, 'http://www.nuxeo.com/')
        self.assert_(ret, err)

    def test_url_ok_2(self):
        ret, err, ds = self._validate({}, 'http://www.nuxeo.com')
        self.assert_(ret, err)

    def test_url_ok_3(self):
        ret, err, ds = self._validate({}, 'http://www.nuxeo.com/index.html')
        self.assert_(ret, err)

    def test_url_ok_4(self):
        ret, err, ds = self._validate({}, '/foo')
        self.assert_(ret, err)

    def test_url_ok_5(self):
        ret, err, ds = self._validate({}, '/foo#AZE')
        self.assert_(ret, err)

    def test_url_ok_6(self):
        ret, err, ds = self._validate({}, 'HTtp://foo/#AZE')
        self.assert_(ret, err)

    def test_url_ok_7(self):
        ret, err, ds = self._validate({},
                                      'http://www.google.fr/search?hl=fr&ie=UTF-8&oe=UTF-8&q=%40%5E%C3%A7%C3%A9%C3%A0%29%3F&btnG=Recherche+Google&meta=')
        self.assert_(ret, err)

    def test_url_ok_8(self):
        ret, err, ds = self._validate({}, '../index.html')
        self.assert_(ret, err)

    def test_url_ok_9(self):
        ret, err, ds = self._validate({}, '')
        self.assert_(ret, err)

    def test_url_ok_10(self):
        ret, err, ds = self._validate({}, 'tooo-%20oo')
        self.assert_(ret, err)

    def test_url_ok_11(self):
        ret, err, ds = self._validate({}, 'ftp://toto.com/')
        self.assert_(ret, err)

    def test_url_ok_12(self):
        ret, err, ds = self._validate({}, 'http://toto:toto@toto.com/')
        self.assert_(ret, err)

    def test_url_ok_13(self):
        ret, err, ds = self._validate({}, 'http://toto.com:8080/')
        self.assert_(ret, err)

    def test_url_ok_14(self):
        ret, err, ds = self._validate({}, '/ww..com')
        self.assert_(ret, err)

    def test_url_ok_15(self):
        ret, err, ds = self._validate({}, 'http://nuxeo.com/~fermigier/')
        self.assert_(ret, err)

    def test_url_ok_16(self):
        ret, err, ds = self._validate({}, 'file:///etc/passwords')
        self.assert_(ret, err)

    def test_url_nok_1(self):
        ret, err, ds = self._validate({}, 'a space')
        self.assertEquals(err, 'cpsschemas_err_url')

    def test_url_nok_2(self):
        ret, err, ds = self._validate({}, '[abraket')
        self.assertEquals(err, 'cpsschemas_err_url')

    def test_url_nok_3(self):
        ret, err, ds = self._validate({}, 'http://www./')
        self.assertEquals(err, 'cpsschemas_err_url')


class EmailWidgetValidationTest(WidgetValidationTest):
    widget_type = CPSEmailWidget

    def test_email_ok_1(self):
        ret, err, ds = self._validate({}, 'root@nuxeo.com')
        self.assert_(ret, err)

    def test_email_ok_2(self):
        ret, err, ds = self._validate({}, 'r0Ot-me@nuxeo.foo-bar.fr')
        self.assert_(ret, err)

    def test_email_ok_3(self):
        ret, err, ds = self._validate({}, 'r-12@1.gouv')
        self.assert_(ret, err)

    def test_email_ok_4(self):
        ret, err, ds = self._validate({}, 'f+bar@be.bo.ba')
        self.assert_(ret, err)

    def test_email_nok_1(self):
        ret, err, ds = self._validate({}, 'root')
        self.assertEquals(err, 'cpsschemas_err_email')

    def test_email_nok_2(self):
        ret, err, ds = self._validate({}, 'root@azer')
        self.assertEquals(err, 'cpsschemas_err_email')

    def test_email_nok_3(self):
        ret, err, ds = self._validate({}, 'root@foo--')
        self.assertEquals(err, 'cpsschemas_err_email')

    def test_email_nok_4(self):
        ret, err, ds = self._validate({}, '@foo')
        self.assertEquals(err, 'cpsschemas_err_email')

    def test_email_nok_5(self):
        ret, err, ds = self._validate({}, 'foo bar@foo.com')
        self.assertEquals(err, 'cpsschemas_err_email')

    def test_email_nok_6(self):
        ret, err, ds = self._validate({}, 'é@à.fr')
        self.assertEquals(err, 'cpsschemas_err_email')

    def test_email_nok_7(self):
        ret, err, ds = self._validate({}, 'a@foo..fr')
        self.assertEquals(err, 'cpsschemas_err_email')

#  XXX should fail
#    def test_email_nok_8(self):
#        ret, err, ds = self._validate('Email', {}, 'a@foo.france')
#        self.assert_(err == 'cpsschemas_err_email', err)

class IdentifierWidgetValidationTest(WidgetValidationTest):
    widget_type = CPSIdentifierWidget

    def test_identifier_ok_1(self):
        ret, err, ds = self._validate({}, 'POM')
        self.assert_(ret, err)

    def test_identifier_ok_2(self):
        ret, err, ds = self._validate({},
                                      'azermaozeiurpoiuwmfvljwxcvn12345678790')
        self.assert_(ret, err)

    def test_identifier_ok_3(self):
        ret, err, ds = self._validate({}, 'a_1234@12.zz')
        self.assert_(ret, err)

    def test_identifier_ok_4(self):
        ret, err, ds = self._validate({}, 'a_1.2')
        self.assert_(ret, err)

    def test_identifier_ok_5(self):
        ret, err, ds = self._validate({}, 'fbar@be.bo.ba')
        self.assert_(ret, err)

    def test_identifier_ok_5(self):
        ret, err, ds = self._validate({}, 'foo-bar')
        self.assert_(ret, err)

    def test_identifier_nok_1(self):
        ret, err, ds = self._validate({}, '1234')
        self.assertEquals(err, 'cpsschemas_err_identifier')

    def test_identifier_nok_2(self):
        ret, err, ds = self._validate({}, 'élskjd')
        self.assertEquals(err, 'cpsschemas_err_identifier')

    def test_identifier_nok_3(self):
        ret, err, ds = self._validate({}, 'boaz mlskjr ')
        self.assertEquals(err, 'cpsschemas_err_identifier')

    def test_identifier_nok_4(self):
        ret, err, ds = self._validate({}, 'foo\tzie')
        self.assertEquals(err, 'cpsschemas_err_identifier')

    def test_identifier_nok_5(self):
        ret, err, ds = self._validate({}, '_foo')
        self.assertEquals(err, 'cpsschemas_err_identifier')


class PasswordWidgetValidationTest(WidgetValidationTest):
    widget_type = CPSPasswordWidget
    default_value = 'xxxxx'

    def test_widget_nok_required_1(self):
        pass

    def test_password_ok_required_1(self):
        # default value for size_min is 5
        ret, err, ds = self._validate({'is_required': 0, 'size_min': 0}, '')
        self.assertEquals(err, None)

    def test_password_ok_required_2(self):
        # default value for size_min is 5
        ret, err, ds = self._validate({'is_required': 0, 'size_min': 0}, 'here')
        self.assertEquals(err, None)

    def test_password_ok_required_3(self):
        # Even if there is a size_min, this should not fail
        ret, err, ds = self._validate({'is_required': 0, 'size_min': 5}, '')
        self.assertEquals(err, None)

    def test_password_nok_required_1(self):
        ret, err, ds = self._validate({'is_required': 1}, '')
        self.assertEquals(err, 'cpsschemas_err_required')

    def test_password_ok_size_1(self):
        ret, err, ds = self._validate({'size_min': 5}, 'fooba')
        self.assertEquals(err, None)

    def test_password_ok_size_2(self):
        ret, err, ds = self._validate({'size_max': 8}, 'foobarfo')
        self.assertEquals(err, None)

    def test_password_ok_size_3(self):
        # Non-required password fields should not raise an error if empty,
        # even if min size is set.
        ret, err, ds = self._validate({'size_min': 5}, '')
        self.assertEquals(err, None)

    def test_password_nok_size_1(self):
        ret, err, ds = self._validate({'size_min': 5}, 'foob')
        self.assertEquals(err, 'cpsschemas_err_password_size_min')

    def test_password_nok_size_2(self):
        ret, err, ds = self._validate({'size_max': 8}, 'foobarfoo')
        self.assertEquals(err, 'cpsschemas_err_string_too_long')

    def test_password_nok_size_3(self):
        ret, err, ds = self._validate({'size_min': 5}, 'four')
        self.assertEquals(err, 'cpsschemas_err_password_size_min')

    def test_password_ok_lower_1(self):
        ret, err, ds = self._validate({'check_lower': 1}, 'FoE1.A')
        self.assertEquals(err, None)

    def test_password_nok_lower_1(self):
        ret, err, ds = self._validate({'check_lower': 1}, 'FFFFF')
        self.assertEquals(err, 'cpsschemas_err_password_lower')

    def test_password_ok_upper_1(self):
        ret, err, ds = self._validate({'check_upper': 1}, 'F....')
        self.assertEquals(err, None)

    def test_password_nok_upper_1(self):
        ret, err, ds = self._validate({'check_upper': 1}, 'azert')
        self.assertEquals(err, 'cpsschemas_err_password_upper')

    def test_password_ok_extra_1(self):
        ret, err, ds = self._validate({'check_extra': 1}, 'azert*')
        self.assertEquals(err, None)

    def test_password_nok_extra_1(self):
        ret, err, ds = self._validate({'check_extra': 1}, 'aze12')
        self.assertEquals(err, 'cpsschemas_err_password_extra')

class RangeListWidgetValidationTest(WidgetValidationTest):
    widget_type = CPSRangeListWidget
    default_value = []

    def test_rangelist_ok_0(self):
        ret, err, ds = self._validate({}, [])
        self.assert_(ret, err)
        # check convertion
        self.assertEquals(ds.getDataModel().values()[0], [])

    def test_rangelist_ok_1(self):
        ret, err, ds = self._validate({}, ['1', '2-3'])
        self.assert_(ret, err)
        # check convertion
        self.assertEquals(ds.getDataModel().values()[0], [(1,), (2,3)])

    def test_rangelist_nok_0(self):
        ret, err, ds = self._validate({}, '')
        self.assertEquals(err, 'cpsschemas_err_rangelist')

    def test_rangelist_nok_1(self):
        ret, err, ds = self._validate({}, ['1', '2,3'])
        self.assertEquals(err, 'cpsschemas_err_rangelist')

    def test_rangelist_nok_2(self):
        ret, err, ds = self._validate({}, ['1', 'a'])
        self.assertEquals(err, 'cpsschemas_err_rangelist')

    def test_rangelist_nok_3(self):
        ret, err, ds = self._validate({}, ['a'])
        self.assertEquals(err, 'cpsschemas_err_rangelist')

    def test_rangelist_nok_4(self):
        ret, err, ds = self._validate({}, ('1', '2-3'))
        self.assertEquals(err, 'cpsschemas_err_rangelist')

class FlashWidgetValidationTest(WidgetValidationTest):

    widget_type = CPSFlashWidget

    folder = Folder()
    folder.mimetypes_registry = FakeMimeTypeRegistry()

    data = open(TEST_SWF, 'r').read()
    default_value = File('fake', '', data)
    # XXX: this should be changed as it's no longer the way FlashWidget 
    # checks the content_type
    default_value.content_type = 'application/x-shockwave-flash'

    def _validate(self, properties, value):
        id = 'ff'
        data = {id: value}
        ds = DataStructure(data, datamodel=data)
        properties.update({'fields': (id,),})
        widget = self.widget_type(id, **properties).__of__(folder)

        # Just test the internal validation related to swf
        ret = widget._flash_validate(ds)
        err = ds.getError(id)
        return ret, err, ds

    def test_widget_nok_required_1(self):
        pass

class DateTimeWidgetValidationTest(WidgetValidationTest):
    widget_type = CPSDateTimeWidget
    default_value = ''

    # base class validation method is not compatible with this widget
    def _validate(self, properties, value):
        id = 'ff'
        data = {
            id + '_date': value,
            # dummy values for hour and minute, they're not tested here
            id + '_hour': '3',
            id + '_minute': '38',
            }
        ds = DataStructure(data, datamodel=data)
        properties.update({'fields': (id,)})
        widget = self.widget_type(id, **properties).__of__(fakePortal)
        ret = widget.validate(ds)
        err = ds.getError(id)
        return ret, err, ds

    def test_datetime_ok_1(self):
        ret, err, ds = self._validate({}, '27/06/2005')
        self.assertEquals(ret, 1)

    def test_datetime_nok_1(self):
        ret, err, ds = self._validate({}, '26/27/2005')
        self.assertEquals(ret, 0)
        self.assertEquals(err, 'cpsschemas_err_date')

    def test_datetime_nok_2(self):
        ret, err, ds = self._validate({}, '26/2705k')
        self.assertEquals(ret, 0)
        self.assertEquals(err, 'cpsschemas_err_date')


# XXX: test more widget types here

def test_suite():
    from inspect import isclass
    from types import ClassType
    tests = []
    for obj in globals().values():
        if obj is WidgetValidationTest:
            continue
        if type(obj) is ClassType and issubclass(obj, WidgetValidationTest):
            # python 2.1
            tests.append(unittest.makeSuite(obj))
        elif isclass(obj) and issubclass(obj, WidgetValidationTest):
            # python 2.3
            tests.append(unittest.makeSuite(obj))
    return unittest.TestSuite(tests)

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
