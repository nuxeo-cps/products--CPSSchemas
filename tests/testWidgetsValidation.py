# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import unittest
from Testing.ZopeTestCase import ZopeLite

from Products.CPSSchemas.DataStructure import DataStructure
from Products.CPSSchemas.BasicWidgets import CPSStringWidget, \
     CPSBooleanWidget, CPSURLWidget, CPSEmailWidget, CPSPasswordWidget, \
     CPSIdentifierWidget
from Products.CPSSchemas.ExtendedWidgets import CPSTextWidget

class WidgetValidationTest(unittest.TestCase):
    """Tests validate method of widgets"""

    def _validate(self, properties, value):
        id = 'ff'
        data = {id: value}
        ds = DataStructure(data, datamodel=data)
        properties.update({'fields': (id,)})
        widget = self.widget_type(id, '')
        widget.manage_changeProperties(**properties)

        ret = widget.validate(ds)
        err = ds.getError(id)
        return ret, err, ds

class StringWidgetValidationTest(WidgetValidationTest):
    widget_type = CPSStringWidget

    def test_string_ok_1(self):
        ret, err, ds = self._validate({}, '12345')
        self.failUnless(ret, err)

    def test_string_ok_2(self):
        ret, err, ds = self._validate({}, '')
        self.failUnless(ret, err)

    def test_string_ok_3(self):
        ret, err, ds = self._validate({}, None)
        self.failUnless(ret, err)
        # check convertion None into ''
        self.assertEquals(ds.getDataModel().values()[0], '')

    def test_string_nok_1(self):
        ret, err, ds = self._validate({}, {'a': 1} )
        self.assertEquals(err, 'cpsschemas_err_string')

    def test_string_size_max_ok_1(self):
        ret, err, ds = self._validate({'size_max': 10}, '12345')
        self.failUnless(ret)

    def test_string_size_max_ok_2(self):
        ret, err, ds = self._validate({'size_max': 10}, None)
        self.failUnless(ret, err)

    def test_string_size_max_ok_3(self):
        ret, err, ds = self._validate({'size_max': 10}, '')
        self.failUnless(ret)

    def test_string_size_max_ok_4(self):
        ret, err, ds = self._validate({'size_max': 10}, '1234567890')
        self.failUnless(ret)

    def test_string_size_max_nok_1(self):
        ret, err, ds = self._validate({'size_max': 10}, '12345678901')
        self.assertEquals(err, 'cpsschemas_err_string_too_long')

    def test_string_size_max_nok_2(self):
        ret, err, ds = self._validate({'size_max': 10}, '1234567890azerz')
        self.assertEquals(err, 'cpsschemas_err_string_too_long')

    def test_string_required_ok_1(self):
        ret, err, ds = self._validate({'is_required': 1}, '123')
        self.failUnless(ret)

    def test_string_required_nok_1(self):
        ret, err, ds = self._validate({'is_required': 1}, '')
        self.assertEquals(err, 'cpsschemas_err_required')

    def test_string_required_nok_2(self):
        ret, err, ds = self._validate({'is_required': 1}, None)
        self.assertEquals(err, 'cpsschemas_err_required')

class BooleanWidgetValidationTest(WidgetValidationTest):
    widget_type = CPSBooleanWidget

    def test_boolean_ok_1(self):
        ret, err, ds = self._validate({}, 0)
        self.failUnless(ret, err)

    def test_boolean_ok_2(self):
        ret, err, ds = self._validate({}, 1)
        self.failUnless(ret, err)

    def test_boolean_nok_1(self):
        ret, err, ds = self._validate({}, 2)
        self.assertEquals(err, 'cpsschemas_err_boolean')

    def test_boolean_nok_2(self):
        ret, err, ds = self._validate({}, -1)
        self.assertEquals(err, 'cpsschemas_err_boolean')

    def test_boolean_nok_3(self):
        ret, err, ds = self._validate({}, '')
        self.assertEquals(err, 'cpsschemas_err_boolean')

    def test_boolean_nok_4(self):
        ret, err, ds = self._validate({}, None)
        self.assertEquals(err, 'cpsschemas_err_boolean')

    def test_boolean_nok_5(self):
        ret, err, ds = self._validate({}, 'foo')
        self.assertEquals(err, 'cpsschemas_err_boolean')

    def test_boolean_nok_5(self):
        ret, err, ds = self._validate({}, {'foo': 'sk'})
        self.assertEquals(err, 'cpsschemas_err_boolean')

class TextWidgetValidationTest(WidgetValidationTest):
    widget_type = CPSTextWidget

    def test_text_ok_1(self):
        ret, err, ds = self._validate({}, '12345')
        self.failUnless(ret, err)

    def test_text_ok_2(self):
        ret, err, ds = self._validate({}, '')
        self.failUnless(ret, err)

    def test_text_ok_3(self):
        ret, err, ds = self._validate({}, None)
        self.failUnless(ret, err)
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
        self.failUnless(ret, err)

    def test_text_nok_1(self):
        ret, err, ds = self._validate({}, {'a':1} )
        self.assertEquals(err, 'cpsschemas_err_string')

    def test_text_size_max_ok_1(self):
        ret, err, ds = self._validate({'size_max': 10}, '12345')
        self.failUnless(ret)

    def test_text_size_max_ok_2(self):
        ret, err, ds = self._validate({'size_max': 10}, None)
        self.failUnless(ret)

    def test_text_size_max_ok_3(self):
        ret, err, ds = self._validate({'size_max': 10}, '')
        self.failUnless(ret)

    def test_text_size_max_ok_4(self):
        ret, err, ds = self._validate({'size_max': 10}, '1234567890')
        self.failUnless(ret)

    def test_text_size_max_nok_1(self):
        ret, err, ds = self._validate({'size_max': 10}, '12345678901')
        self.assertEquals(err, 'cpsschemas_err_string_too_long')


class URLWidgetValidationTest(WidgetValidationTest):
    widget_type = CPSURLWidget

    def test_url_ok_1(self):
        ret, err, ds = self._validate({}, 'http://www.nuxeo.com/')
        self.failUnless(ret, err)

    def test_url_ok_2(self):
        ret, err, ds = self._validate({}, 'http://www.nuxeo.com')
        self.failUnless(ret, err)
    def test_url_ok_3(self):
        ret, err, ds = self._validate({}, 'http://www.nuxeo.com/index.html')
        self.failUnless(ret, err)

    def test_url_ok_4(self):
        ret, err, ds = self._validate({}, '/foo')
        self.failUnless(ret, err)

    def test_url_ok_5(self):
        ret, err, ds = self._validate({}, '/foo#AZE')
        self.failUnless(ret, err)

    def test_url_ok_6(self):
        ret, err, ds = self._validate({}, 'HTtp://foo/#AZE')
        self.failUnless(ret, err)

    def test_url_ok_7(self):
        ret, err, ds = self._validate({},
                                      'http://www.google.fr/search?hl=fr&ie=UTF-8&oe=UTF-8&q=%40%5E%C3%A7%C3%A9%C3%A0%29%3F&btnG=Recherche+Google&meta=')
        self.failUnless(ret, err)

    def test_url_ok_8(self):
        ret, err, ds = self._validate({}, '../index.html')
        self.failUnless(ret, err)

    def test_url_ok_9(self):
        ret, err, ds = self._validate({}, '')
        self.failUnless(ret, err)

    def test_url_ok_10(self):
        ret, err, ds = self._validate({}, 'tooo-%20oo')
        self.failUnless(ret, err)

    def test_url_nok_1(self):
        ret, err, ds = self._validate({}, 'a space')
        self.assertEquals(err, 'cpsschemas_err_url')

    def test_url_nok_2(self):
        ret, err, ds = self._validate({}, '[abraket')
        self.assertEquals(err, 'cpsschemas_err_url')

    def test_url_nok_3(self):
        ret, err, ds = self._validate({}, 'a??dlk')
        self.assertEquals(err, 'cpsschemas_err_url')

    def test_url_nok_4(self):
        ret, err, ds = self._validate({}, 'http://www./')
        self.assertEquals(err, 'cpsschemas_err_url')

# XXX make it pass !
#    def test_url_nok_5(self):
#        ret, err, ds = self._validate('URL', {}, '/ww..com')
#        self.failUnless(err == 'cpsschemas_err_url')


class EmailWidgetValidationTest(WidgetValidationTest):
    widget_type = CPSEmailWidget

    def test_email_ok_1(self):
        ret, err, ds = self._validate({}, 'root@nuxeo.com')
        self.failUnless(ret, err)

    def test_email_ok_2(self):
        ret, err, ds = self._validate({}, 'r0Ot-me@nuxeo.foo-bar.fr')
        self.failUnless(ret, err)

    def test_email_ok_3(self):
        ret, err, ds = self._validate({}, 'r-12@1.gouv')
        self.failUnless(ret, err)

    def test_email_ok_4(self):
        ret, err, ds = self._validate({}, 'f+bar@be.bo.ba')
        self.failUnless(ret, err)

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
#        self.failUnless(err == 'cpsschemas_err_email', err)

class IdentifierWidgetValidationTest(WidgetValidationTest):
    widget_type = CPSIdentifierWidget

    def test_identifier_ok_1(self):
        ret, err, ds = self._validate({}, 'POM')
        self.failUnless(ret, err)

    def test_identifier_ok_2(self):
        ret, err, ds = self._validate({},
                                      'azermaozeiurpoiuwmfvljwxcvn12345678790')
        self.failUnless(ret, err)

    def test_identifier_ok_3(self):
        ret, err, ds = self._validate({}, 'a_1234@12.zz')
        self.failUnless(ret, err)

    def test_identifier_ok_4(self):
        ret, err, ds = self._validate({}, 'a_1.2')
        self.failUnless(ret, err)

    def test_identifier_ok_5(self):
        ret, err, ds = self._validate({}, 'fbar@be.bo.ba')
        self.failUnless(ret, err)

    def test_identifier_ok_5(self):
        ret, err, ds = self._validate({}, 'foo-bar')
        self.failUnless(ret, err)

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

    def test_password_ok_required_1(self):
        ret, err, ds = self._validate({'is_required': 0}, '')
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

    def test_password_nok_size_1(self):
        ret, err, ds = self._validate({'size_min': 5}, 'foob')
        self.assertEquals(err, 'cpsschemas_err_password_size_min')

    def test_password_nok_size_2(self):
        ret, err, ds = self._validate({'size_max': 8}, 'foobarfoo')
        self.assertEquals(err, 'cpsschemas_err_string_too_long')

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

# XXX: test more widget types here

def test_suite():
    from types import ClassType
    tests = []
    for obj in globals().values():
        if type(obj) is ClassType and issubclass(obj, WidgetValidationTest):
            tests.append(unittest.makeSuite(obj))
    return unittest.TestSuite(tests)

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
