from Testing import ZopeTestCase

from Products.ExternalMethod.ExternalMethod import ExternalMethod

ZopeTestCase.installProduct('CPSSchemas')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('Epoz')

try:
    from Products.CPSDefault.tests import CPSTestCase
    IS_CPS3 = 1
except ImportError:
    from Products.CPSSchemas.tests import CMFTestCase
    IS_CPS3 = 0

# CPS3 or stock CMF
# Use a different installer class
if IS_CPS3:
    CPSTestCase.setupPortal()
    CPSSchemasTestCase = CPSTestCase.CPSTestCase
else:
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
