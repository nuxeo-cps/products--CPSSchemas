# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

import os
from zLOG import LOG, INFO, DEBUG

# XXX I think that as long as you don't run any CPSSpecific methods,
# this should still work under pure CMF. This needs to be tested though.
from Products.CPSInstaller.CPSInstaller import CPSInstaller

class CPSSchemasInstaller(CPSInstaller):

    def installPortalTransforms(self):
        self.log("Verifying Portal Transforms tool")

        if self.portalHas('portal_transforms'):
            pt = self.portal.portal_transforms
            if pt.meta_type == 'Portal Transforms':
                self.logOK()
            else:
                self.portal.manage_delObjects(['portal_transforms'])

        if not self.portalHas('portal_transforms'):
            self.runExternalUpdater('portal_transforms_installer',
                                    'Portal Transforms Installer',
                                    'PortalTransforms',
                                    'Install',
                                    'install')

            self.log("Adding additional mime types")
            mimetypesRegistry = self.portal.mimetypes_registry
            for extension, mimetype in (
                ('sxw', 'application/vnd.sun.xml.writer'),
                ('stw', 'application/vnd.sun.xml.writer.template'),
                ('sxg', 'application/vnd.sun.xml.writer.global'),
                ('sxc', 'application/vnd.sun.xml.calc'),
                ('stc', 'application/vnd.sun.xml.calc.template'),
                ('sxi', 'application/vnd.sun.xml.impress'),
                ('sti', 'application/vnd.sun.xml.impress.template'),
                ('sxd', 'application/vnd.sun.xml.draw'),
                ('std', 'application/vnd.sun.xml.draw.template'),
                ('sxm', 'application/vnd.sun.xml.math')):
                if not mimetypesRegistry.extensions.has_key(extension):
                    mimetypesRegistry.manage_addMimeType(mimetype, [mimetype],
                                                         [extension], '', 1)
                else:
                    self.log("We already have a registration for "
                             "extension '%s'" % extension)
            self.log("   done")


def install(self):

    installer = CPSSchemasInstaller(self, 'CPSSchemas')
    installer.log("Starting CPSSchemas install")

    # skins
    skins = {
        'cps_schemas': 'Products/CPSSchemas/skins/cps_schemas',
        'cps_jscalendar': 'Products/CPSSchemas/skins/cps_jscalendar',
    }
    installer.verifySkins(skins)

    # Tools
    installer.verifyTool('portal_schemas', 'CPSSchemas',
                         'CPS Schemas Tool')
    installer.verifyTool('portal_widget_types', 'CPSSchemas',
                         'CPS Widget Types Tool')
    installer.verifyTool('portal_layouts', 'CPSSchemas',
                         'CPS Layouts Tool')
    installer.verifyTool('portal_vocabularies', 'CPSSchemas',
                         'CPS Vocabularies Tool')

    # portal_transforms
    installer.installPortalTransforms()

    # Old stuff (UPGRADES)
    if installer.portalHas('portal_widgets'):
        installer.portal.manage_delObjects('portal_widgets')
        installer.log(" Deleting old portal_widgets")

    # importing .po files
    # Non CPS installation may not have Localizer.
    if installer.portalHas('Localizer'):
        installer.setupTranslations()

    installer.log("")
    installer.log("### Epoz Installer")
    installer.runExternalUpdater('epoz_installer', 'Epoz Installer',
                                 'Epoz','Install', 'install')
    installer.log("### End of Epoz install")
    installer.log("")

    installer.finalize()
    installer.log("End of specific CPSSchemas install")
    return installer.logResult()
