#
# CPSTestCase
#

import os, tempfile
from Testing import ZopeTestCase
import Products

ZopeTestCase.installProduct('CMFCalendar', quiet=1)
ZopeTestCase.installProduct('CMFCore', quiet=1)
ZopeTestCase.installProduct('CMFDefault', quiet=1)
ZopeTestCase.installProduct('CMFTopic', quiet=1)
ZopeTestCase.installProduct('DCWorkflow', quiet=1)
ZopeTestCase.installProduct('Localizer', quiet=1)
ZopeTestCase.installProduct('MailHost', quiet=1)
ZopeTestCase.installProduct('TranslationService', quiet=1)
ZopeTestCase.installProduct('SiteAccess', quiet=1)
ZopeTestCase.installProduct('CPSSchemas', quiet=1)
ZopeTestCase.installProduct('PortalTransforms', quiet=1)
ZopeTestCase.installProduct('Epoz', quiet=1)
ZopeTestCase.installProduct('CMFPlone', quiet=1)

from AccessControl.SecurityManagement \
    import newSecurityManager, noSecurityManager

import time

# The folowing are patches needed because Localizer doesn't work
# well within ZTC

# This one is needed by ProxyTool.
def get_selected_language(self):
    """ """
    return self._default_language

from Products.Localizer.Localizer import Localizer
Localizer.get_selected_language = get_selected_language

# Dummy portal_catalog.

from OFS.SimpleItem import SimpleItem
class DummyTranslationService(SimpleItem):
    meta_type = 'Translation Service'
    id = 'translation_service'
    def translate(self, domain, msgid, *args, **kw):
        return msgid

    def getDomainInfo(self):
        return [(None, 'Localizer/default')]

    def manage_addDomainInfo(self, domain, path, REQUEST=None, **kw):
        pass

# Dummy MessageCatalog
class DummyMessageCatalog:
    def __call__(self, message, *args, **kw):
        return message

    def get_selected_language(self):
        "xxx"
        return 'fr'


    def get_languages(self):
        return ['en', 'fr']

    def manage_import(self, *args, **kw):
        pass

    def wl_isLocked(self):
        return None # = False


from StringIO import StringIO
from Products.Localizer import LocalizerStringIO
from types import UnicodeType
# Un-patch LocalizerStringIO
def LocalizerStringIO_write(self, s):
    StringIO.write(self, s)
# Hack around Unicode problem
def LocalizerStringIO_getvalue(self):
    if self.buflist:
        for buf in self.buflist:
            if type(buf) == UnicodeType:
                self.buf += buf.encode('latin-1')
            else:
                self.buf += buf
        self.buflist = []
    return self.buf
LocalizerStringIO.write = LocalizerStringIO_write
LocalizerStringIO.getvalue = LocalizerStringIO_getvalue

class PloneTestCase(ZopeTestCase.PortalTestCase):

    def isValidXML(self, xml):
        filename = tempfile.mktemp()
        fd = open(filename, "wc")
        fd.write(xml)
        fd.close()
        status = os.system("xmllint --noout %s" % filename)
        os.unlink(filename)
        return status == 0

    # XXX: unfortunately, the W3C checker sometime fails for no apparent
    # reason.
    def isValidCSS(self, css):
        """Check if <css> is valid CSS2 using W3C css-checker"""

        import urllib2, urllib, re
        CHECKER_URL = 'http://jigsaw.w3.org/css-validator/validator'
        data = urllib.urlencode({
            'text': css,
            'warning': '1',
            'profile': 'css2',
            'usermedium': 'all',
        })
        url = urllib2.urlopen(CHECKER_URL + '?' + data)
        result = url.read()

        is_valid = not re.search('<div id="errors">', result)
        # debug
        if not is_valid:
            print result
        return is_valid


class PloneInstaller:
    def __init__(self, app, quiet=0):
        if not quiet:
            ZopeTestCase._print('Adding Portal Site ... ')
        self.app = app
        self._start = time.time()
        self._quiet = quiet

    def install(self, portal_id):
        self.addUser()
        self.login()
        self.addPortal(portal_id)
        self.installLocalizer()
        self.fixupTranslationServices(portal_id)
        self.logout()

    def addUser(self):
        uf = self.app.acl_users
        uf._doAddUser('CPSTestCase', '', ['Manager'], [])

    def login(self):
        uf = self.app.acl_users
        user = uf.getUserById('CPSTestCase').__of__(uf)
        newSecurityManager(None, user)

    def addPortal(self, portal_id):
        factory = self.app.manage_addProduct['CMFDefault']
        factory.manage_addCMFSite(portal_id)

    def installLocalizer(self):
        """ Install Localizer and Translation service for the tests

        Mandatory products for the tests and the component right now.
        """

        # Localizer
        if 'Localizer' not in self.app.portal.objectIds():
            languages = ('en',)
            self.app.portal.manage_addProduct['Localizer'].manage_addLocalizer(
                title='',
                languages=languages)

        localizer = self.app.portal.Localizer
        catalog_id = 'default'
        title = 'Default messages'

        # Default MessageCatalog
        if catalog_id not in localizer.objectIds():
            languages = localizer.get_supported_languages()
            localizer.manage_addProduct['Localizer'].manage_addMessageCatalog(
                id=catalog_id,
                title=title,
                languages=languages)

        if catalog_id.lower() != 'default':
            translation_service = self.app.portal.translation_service
            domains = [info[0] for info in translation_service.getDomainInfo()]
            if not catalog_id in domains:
                translation_service.manage_addDomainInfo(catalog_id,
                    'Localizer/' + catalog_id)

        # translation_service
        if 'translation_service' not in self.app.portal.objectIds():
            self.app.portal.manage_addProduct[
                'TranslationService'].addPlacefulTranslationService(
                id='translation_service')
            translation_service = self.app.portal.translation_service
            translation_service.manage_setDomainInfo(path_0='Localizer/default')

    # Change translation_service to DummyTranslationService
    def fixupTranslationServices(self, portal_id):
        portal = getattr(self.app, portal_id)
        portal.translation_service = DummyTranslationService()
        localizer = portal.Localizer
        for domain in localizer.objectIds():
            setattr(localizer, domain, DummyMessageCatalog())

    def logout(self):
        noSecurityManager()
        get_transaction().commit()
        if not self._quiet:
            ZopeTestCase._print('done (%.3fs)\n'
                % (time.time() - self._start,))

def optimize():
    '''Significantly reduces portal creation time.'''
    def __init__(self, text):
        # Don't compile expressions on creation
        self.text = text
    from Products.CMFCore.Expression import Expression
    Expression.__init__ = __init__

    def _cloneActions(self):
        # Don't clone actions but convert to list only
        return list(self._actions)
    from Products.CMFCore.ActionProviderBase import ActionProviderBase
    ActionProviderBase._cloneActions = _cloneActions

optimize()

def setupPortal(PortalInstaller=PloneInstaller):
    # Create a CPS site in the test (demo-) storage
    app = ZopeTestCase.app()
    # PortalTestCase expects object to be called "portal", not "cps"
    if hasattr(app, 'portal'):
        app.manage_delObjects(['portal'])
    PortalInstaller(app).install('portal')
    ZopeTestCase.close(app)
