#
# XXX Fix the mess
# Think about clean way to handle mutliple envirronnements
#

from Testing import ZopeTestCase

from Products.ExternalMethod.ExternalMethod import ExternalMethod

ZopeTestCase.installProduct('CPSSchemas')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('Epoz')

IS_CPS3   = 0
IS_PLONE2 = 0
IS_CMF    = 0

try:
    from Products.CPSDefault.Portal import CPSDefaultSite
    IS_CPS3 = 1
except ImportError:
    try:
        from Products.CMFPlone.Portal import PloneSite
        IS_PLONE2 = 1
    except ImportError:
        from Products.CMFDefault.Portal import CMFSite
        IS_CMF = 1

# CPS3 or stock CMF
# Use a different installer class
if IS_CPS3:
    from Products.CPSDefault.tests import CPSTestCase
    CPSTestCase.setupPortal()
    CPSSchemasTestCase = CPSTestCase.CPSTestCase
elif IS_PLONE2:
    ZopeTestCase.installProduct('CMFPlone')
    from Products.CPSSchemas.tests import PloneTestCase
    class CPSSchemasInstaller(PloneTestCase.PloneInstaller):
        def addPortal(self, id):
            """Override the Default addPortal method installing
            a Default CMF Site

            Will launch the external method for CPSSchemas
            """

            # Plone Default Site
            PloneTestCase.PloneInstaller.addPortal(self, id)
            portal = getattr(self.app, id)

            # Install the CPSSchema product
            if 'cpsschemas_installer' not in portal.objectIds():
                cpsschemas_installer = ExternalMethod('cpsschemas_installer',
                                                      '',
                                                      'CPSSchemas.install',
                                                      'install')
                portal._setObject('cpsschemas_installer', cpsschemas_installer)
            portal.cpsschemas_installer()

    PloneTestCase.setupPortal(PortalInstaller=CPSSchemasInstaller)
    CPSSchemasTestCase = PloneTestCase.PloneTestCase
elif IS_CMF:
    from Products.CPSSchemas.tests import CMFTestCase
    class CPSSchemasInstaller(CMFTestCase.CMFInstaller):
        def addPortal(self, id):
            """Override the Default addPortal method installing
            a Default CMF Site

            Will launch the external method for CPSSchemas
            """

            # CMF Default Site
            CMFTestCase.CMFInstaller.addPortal(self, id)
            portal = getattr(self.app, id)

            # Install the CPSSchema product
            if 'cpsschemas_installer' not in portal.objectIds():
                cpsschemas_installer = ExternalMethod('cpsschemas_installer',
                                                      '',
                                                      'CPSSchemas.install',
                                                      'install')
                portal._setObject('cpsschemas_installer', cpsschemas_installer)
            portal.cpsschemas_installer()

    CMFTestCase.setupPortal(PortalInstaller=CPSSchemasInstaller)
    CPSSchemasTestCase = CMFTestCase.CMFTestCase
else:
    raise "No Portal component found !"
