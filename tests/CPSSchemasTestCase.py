from Testing import ZopeTestCase

ZopeTestCase.installProduct('CPSSchemas')
# XXX: needed ?
#ZopeTestCase.installProduct('PortalTransforms')
#ZopeTestCase.installProduct('Epoz')

# XXX: change this later so that we try the tool inside a 
# CMF site, not a CPS.
from Products.CPSDefault.tests import CPSTestCase

CPSTestCase.setupPortal()

CPSSchemasTestCase = CPSTestCase.CPSTestCase


