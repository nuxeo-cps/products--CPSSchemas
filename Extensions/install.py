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
from App.Extensions import getPath
from re import match
from zLOG import LOG, INFO, DEBUG

def install(self):

    _log = []
    def pr(bla, zlog=1, _log=_log):
        if bla == 'flush':
            return '<html><head><title>CPSSchemas Update</title></head><body><pre>'+ \
                   '\n'.join(_log) + \
                   '</pre></body></html>'

        _log.append(bla)
        if (bla and zlog):
            LOG('CPSSchemas install:', INFO, bla)

    def prok(pr=pr):
        pr(" Already correctly installed")

    pr("Starting CPSSchemas install")

    portal = self.portal_url.getPortalObject()

    def portalhas(id, portal=portal):
        return id in portal.objectIds()


    # skins
    skins = ('cps_schemas', 'cps_jscalendar')
    paths = {
        'cps_schemas': 'Products/CPSSchemas/skins/cps_schemas',
        'cps_jscalendar': 'Products/CPSSchemas/skins/cps_jscalendar',
    }
    skin_installed = 0
    for skin in skins:
        path = paths[skin]
        path = path.replace('/', os.sep)
        pr(" FS Directory View '%s'" % skin)
        if skin in portal.portal_skins.objectIds():
            dv = portal.portal_skins[skin]
            oldpath = dv.getDirPath()
            if oldpath == path:
                prok()
            else:
                pr("  Correctly installed, correcting path")
                dv.manage_properties(dirpath=path)
        else:
            skin_installed = 1
            portal.portal_skins.manage_addProduct['CMFCore'].manage_addDirectoryView(filepath=path, id=skin)
            pr("  Creating skin")
    if skin_installed:
        allskins = portal.portal_skins.getSkinPaths()
        for skin_name, skin_path in allskins:
            if skin_name != 'Basic':
                continue
            path = [x.strip() for x in skin_path.split(',')]
            path = [x for x in path if x not in skins] # strip all
            if path and path[0] == 'custom':
                path = path[:1] + list(skins) + path[1:]
            else:
                path = list(skins) + path
            npath = ', '.join(path)
            portal.portal_skins.addSkinSelection(skin_name, npath)
            pr(" Fixup of skin %s" % skin_name)
        pr(" Resetting skin cache")
        portal._v_skindata = None
        portal.setupCurrentSkin()

    if portalhas('portal_schemas'):
        prok()
    else:
        pr(" Creating portal_schemas")
        portal.manage_addProduct["CPSSchemas"].manage_addTool(
            'CPS Schemas Tool')
    if portalhas('portal_widget_types'):
        prok()
    else:
        pr(" Creating portal_widget_types")
        portal.manage_addProduct["CPSSchemas"].manage_addTool(
            'CPS Widget Types Tool')
    if portalhas('portal_layouts'):
        prok()
    else:
        pr(" Creating portal_layouts")
        portal.manage_addProduct["CPSSchemas"].manage_addTool(
            'CPS Layouts Tool')
    if portalhas('portal_vocabularies'):
        prok()
    else:
        pr(" Creating portal_vocabularies")
        portal.manage_addProduct["CPSSchemas"].manage_addTool(
            'CPS Vocabularies Tool')

    # portal_transforms
    pr("Verifying Portal Transforms tool")

    if portalhas('portal_transforms'):
        pt = portal.portal_transforms
        if pt.portal_type == ' Portal Transforms':
            prok()
        else:
            portal.manage_delObjects(['portal_transforms'])

    if not portalhas('portal_transforms'):
        pr(" Creating Portal Transforms Tool")
        if not portalhas('portal_transforms_installer'):
            from Products.ExternalMethod.ExternalMethod import ExternalMethod
            pr('  Adding Portal Transforms Installer')
            try:
                installer = ExternalMethod('portal_transforms_installer',
                                           'Portal Transforms Installer',
                                           'PortalTransforms.Install',
                                           'install')
                portal._setObject('portal_transforms_installer', installer)
            except:
                pr(' ERROR: Missing product PortalTransforms !')
                raise "Missing Product", "not found PortalTransforms !"
        portal.portal_transforms_installer()
        pr("   done")


    # Old stuff (UPGRADES)
    if portalhas('portal_widgets'):
        portal.manage_delObjects('portal_widgets')
        pr(" Deleting old portal_widgets")


    # widgets
    pr("Verifiying widgets")
    widgets = self.getDocumentWidgets()

    wtool = portal.portal_widget_types
    for id, info in widgets.items():
        pr(" Widget %s" % id)
        if id in wtool.objectIds():
            pr("  Deleting.")
            wtool.manage_delObjects([id])
        pr("  Installing.")
        widget = wtool.manage_addCPSWidgetType(id, info['type'])
        widget.manage_changeProperties(**info['data'])

    # schemas
    pr("Verifiying schemas")
    schemas = self.getDocumentSchemas()

    stool = portal.portal_schemas
    for id, info in schemas.items():
        pr(" Schema %s" % id)
        if id in stool.objectIds():
            pr("  Deleting.")
            stool.manage_delObjects([id])
        pr("  Installing.")
        schema = stool.manage_addCPSSchema(id)
        for field_id, fieldinfo in info.items():
            pr("   Field %s." % field_id)
            schema.manage_addField(field_id, fieldinfo['type'],
                                   **fieldinfo['data'])

    # layouts
    pr("Verifiying layouts")
    layouts = self.getDocumentLayouts()

    ltool = portal.portal_layouts
    for id, info in layouts.items():
        pr(" Layout %s" % id)
        if id in ltool.objectIds():
            pr("  Deleting.")
            ltool.manage_delObjects([id])
        pr("  Installing.")
        layout = ltool.manage_addCPSLayout(id)
        for widget_id, widgetinfo in info['widgets'].items():
            pr("   Widget %s" % widget_id)
            widget = layout.manage_addCPSWidget(widget_id, widgetinfo['type'],
                                                **widgetinfo['data'])
        layout.setLayoutDefinition(info['layout'])

    # vocabularies
    pr("Verifiying vocabularies")
    vocabularies = self.getDocumentVocabularies()

    vtool = portal.portal_vocabularies
    for id, info in vocabularies.items():
        pr(" Vocabulary %s" % id)
        if id in vtool.objectIds():
            pr("  Deleting.")
            vtool.manage_delObjects([id])
        pr("  Installing.")
        ddict = info['data']['dict']
        dlist = info['data']['list']
        vtool.manage_addCPSVocabulary(id, dict=ddict, list=dlist)

    # importing .po files
    mcat = portal['Localizer']['default']
    pr(" Checking available languages")
    podir = os.path.join('Products', 'CPSSchemas')
    popath = getPath(podir, 'i18n')
    if popath is None:
        pr(" !!! Unable to find .po dir")
    else:
        pr("  Checking installable languages")
        langs = []
        avail_langs = mcat.get_languages()
        pr("    Available languages: %s" % str(avail_langs))
        for file in os.listdir(popath):
            if file.endswith('.po'):
                m = match('^.*([a-z][a-z])\.po$', file)
                if m is None:
                    pr( '    Skipping bad file %s' % file)
                    continue
                lang = m.group(1)
                if lang in avail_langs:
                    lang_po_path = os.path.join(popath, file)
                    lang_file = open(lang_po_path)
                    pr("    Importing %s into '%s' locale" % (file, lang))
                    mcat.manage_import(lang, lang_file)
                else:
                    pr( '    Skipping not installed locale for file %s' % file)


    pr("End of specific CPSSchemas install")
    return pr('flush')
