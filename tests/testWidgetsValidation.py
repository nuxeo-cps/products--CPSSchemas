# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$
import unittest
from Testing.ZopeTestCase import ZopeLite

from Products.CPSSchemas.DataStructure import DataStructure
from Products.CPSSchemas.BasicWidgets import CPSStringWidget
from Products.CPSSchemas.BasicWidgets import CPSBooleanWidget
from Products.CPSSchemas.BasicWidgets import CPSURLWidget
from Products.CPSSchemas.BasicWidgets import CPSEmailWidget
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
        elif type == 'URL':
            widget = CPSURLWidget(id, '')
        elif type == 'Email':
            widget = CPSEmailWidget(id, '')
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
        self.failUnless(ret, err)

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
        self.failUnless(err == 'cpsschemas_err_required', err)

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
        ret, err, ds = self._validate('Text', {}, '12345')
        self.failUnless(ret, err)

    def test_text_ok_2(self):
        ret, err, ds = self._validate('Text', {}, '')
        self.failUnless(ret, err)

    def test_text_ok_3(self):
        ret, err, ds = self._validate('Text', {}, None)
        self.failUnless(ret, err)
        # check convertion None into ''
        self.failUnless(ds.getDataModel().values()[0] == '')

    def test_text_nok_1(self):
        ret, err, ds = self._validate('Text', {}, {'a':1} )
        self.failUnless(err == 'cpsschemas_err_string', err)

    def test_text_size_max_ok_1(self):
        ret, err, ds = self._validate('Text', {'size_max': 10}, '12345')
        self.failUnless(ret)

    def test_text_size_max_ok_2(self):
        ret, err, ds = self._validate('Text', {'size_max': 10}, None)
        self.failUnless(ret)

    def test_text_size_max_ok_3(self):
        ret, err, ds = self._validate('Text', {'size_max': 10}, '')
        self.failUnless(ret)

    def test_text_size_max_ok_4(self):
        ret, err, ds = self._validate('Text', {'size_max': 10}, '1234567890')
        self.failUnless(ret)

    def test_text_size_max_nok_1(self):
        ret, err, ds = self._validate('Text', {'size_max': 10}, '12345678901')
        self.failUnless(err=='cpsschemas_err_string_too_long', err)

    ############################################################
    # URLWidget

    def test_url_ok_1(self):
        ret, err, ds = self._validate('URL', {},
                                      'http://www.nuxeo.com/')
        self.failUnless(ret, err)

    def test_url_ok_2(self):
        ret, err, ds = self._validate('URL', {},
                                      'http://www.nuxeo.com')
        self.failUnless(ret, err)
    def test_url_ok_3(self):
        ret, err, ds = self._validate('URL', {},
                                      'http://www.nuxeo.com/index.html')
        self.failUnless(ret, err)

    def test_url_ok_4(self):
        ret, err, ds = self._validate('URL', {}, '/foo')
        self.failUnless(ret, err)

    def test_url_ok_5(self):
        ret, err, ds = self._validate('URL', {}, '/foo#AZE')
        self.failUnless(ret, err)

    def test_url_ok_6(self):
        ret, err, ds = self._validate('URL', {}, 'HTtp://foo/#AZE')
        self.failUnless(ret, err)

    def test_url_ok_7(self):
        ret, err, ds = self._validate('URL', {},
                                      'http://www.google.fr/search?hl=fr&ie=UTF-8&oe=UTF-8&q=%40%5E%C3%A7%C3%A9%C3%A0%29%3F&btnG=Recherche+Google&meta=')
        self.failUnless(ret, err)

    def test_url_ok_8(self):
        ret, err, ds = self._validate('URL', {},
                                      '../index.html')
        self.failUnless(ret, err)

    def test_url_nok_1(self):
        ret, err, ds = self._validate('URL', {}, 'a space')
        self.failUnless(err == 'cpsschemas_err_url')

    def test_url_nok_2(self):
        ret, err, ds = self._validate('URL', {}, '[abraket')
        self.failUnless(err == 'cpsschemas_err_url')

    def test_url_nok_3(self):
        ret, err, ds = self._validate('URL', {}, 'a??dlk')
        self.failUnless(err == 'cpsschemas_err_url')

    def test_url_nok_4(self):
        ret, err, ds = self._validate('URL', {}, 'http://www./')
        self.failUnless(err == 'cpsschemas_err_url')

# XXX make it pass !
#    def test_url_nok_5(self):
#        ret, err, ds = self._validate('URL', {}, '/ww..com')
#        self.failUnless(err == 'cpsschemas_err_url')


    ############################################################
    # EmailWidget

    def test_email_ok_1(self):
        ret, err, ds = self._validate('Email', {}, 'root@nuxeo.com')
        self.failUnless(ret, err)

    def test_email_ok_2(self):
        ret, err, ds = self._validate('Email', {},
                                      'r0Ot-me@nuxeo.foo-bar.fr')
        self.failUnless(ret, err)

    def test_email_ok_3(self):
        ret, err, ds = self._validate('Email', {},
                                      'r-12@1.gouv')
        self.failUnless(ret, err)

    def test_email_nok_1(self):
        ret, err, ds = self._validate('Email', {}, 'root')
        self.failUnless(err == 'cpsschemas_err_email')

    def test_email_nok_2(self):
        ret, err, ds = self._validate('Email', {}, 'root@azer')
        self.failUnless(err == 'cpsschemas_err_email', err)

    def test_email_nok_3(self):
        ret, err, ds = self._validate('Email', {}, 'root@foo--')
        self.failUnless(err == 'cpsschemas_err_email', err)

    def test_email_nok_4(self):
        ret, err, ds = self._validate('Email', {}, '@foo')
        self.failUnless(err == 'cpsschemas_err_email', err)

    def test_email_nok_5(self):
        ret, err, ds = self._validate('Email', {}, 'foo bar@foo.com')
        self.failUnless(err == 'cpsschemas_err_email', err)

    def test_email_nok_6(self):
        ret, err, ds = self._validate('Email', {}, 'é@à.fr')
        self.failUnless(err == 'cpsschemas_err_email', err)

    def test_email_nok_7(self):
        ret, err, ds = self._validate('Email', {}, 'a@foo..fr')
        self.failUnless(err == 'cpsschemas_err_email', err)

#  XXX should fail
#    def test_email_nok_8(self):
#        ret, err, ds = self._validate('Email', {}, 'a@foo.france')
#        self.failUnless(err == 'cpsschemas_err_email', err)



def test_suite():
    return unittest.makeSuite(TestWidgetsValidation)

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
