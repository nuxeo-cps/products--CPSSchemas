# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# (c) 2003 Alexandre Fernandez <mailto:alex@nuxeo.com>
# (c) 2003 Sebastien Migniot <sm@nuxeo.om>
# $Id$


#from Products.CMFCore.DirectoryView import registerDirectory
#from Products.CMFCore import utils
#from Products.CMFCore.CMFCorePermissions import AddPortalContent

#import FlexibleDocument2
#import Data
#import Layer

import PatchTypesTool

#contentClasses = (
#    FlexibleDocument2.FlexibleDocument2,
#    Data.Data,
#    Layer.Layer
#)

#contentConstructors = (
#    FlexibleDocument2.addFlexibleDocument2,
#    Data.addData,
#    Layer.addLayer
#)

#fti = (
#    FlexibleDocument2.factory_type_information +
#    Data.factory_type_information +
#    Layer.factory_type_information +
#    ()
#)

#registerDirectory('skins', globals())

#def initialize(registrar):
#    utils.ContentInit(
#        'CPS Flexible Document',
#        content_types = contentClasses,
#        permission = AddPortalContent,
#        extra_constructors = contentConstructors,
#        fti = fti,
#    ).initialize(registrar)
