# Copyright (c) 2005 Nuxeo SARL <http://nuxeo.com>
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
"""Layouts tool import/export for CMFSetup.
"""

import os
from Globals import package_home
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName

from Products.CMFSetup.utils import ImportConfiguratorBase
from Products.CMFSetup.utils import ExportConfiguratorBase
from Products.CMFSetup.utils import CONVERTER, DEFAULT, KEY

_pkgdir = package_home(globals())
_xmldir = os.path.join(_pkgdir, 'xml')


_FILENAME = 'layouts.xml'


def importLayoutTool(context):
    """Import layouts."""
    site = context.getSite()
    encoding = context.getEncoding()
    tool = getToolByName(site, 'portal_layouts')

    if context.shouldPurge():
        for layout_id in tool.objectIds():
            tool._delObject(layout_id)

    text = context.readDataFile(_FILENAME)
    if text is None:
        return "Layouts: nothing to import."

    ltconf = LayoutToolImportConfigurator(site, encoding)
    lconf = LayoutImportConfigurator(site, encoding)

    tool_info = ltconf.parseXML(text)

    for layout_info in tool_info['layouts']:
        layout_id = str(layout_info['id'])
        filename = layout_info['filename']
        sep = filename.rfind( '/' )
        if sep == -1:
            layout_text = context.readDataFile(filename)
        else:
            layout_text = context.readDataFile(filename[sep+1:],
                                               filename[:sep])
        layout_info = lconf.parseXML(layout_text)

        layout = tool.manage_addCPSLayout(layout_id)

        # Widgets
        for widget_info in layout_info['widgets']:
            id = widget_info['id']
            type = widget_info['type']
            widget = layout.addWidget(id, type)
            for prop_info in widget_info['properties']:
                lconf.initProperty(widget, prop_info)
            widget._postProcessProperties()

        # Layout properties
        for prop_info in layout_info['properties']:
            lconf.initProperty(layout, prop_info)
        layout._postProcessProperties()

        # Layout table
        rows = []
        for rowinfo in layout_info['table']['rows']:
            row = []
            for cellinfo in rowinfo['cells']:
                row.append({'widget_id': cellinfo['id'],
                            'ncols': cellinfo['ncols']})
            rows.append(row)
        layout.setLayoutDefinition({'rows': rows})

    return "Layouts imported."


def exportLayoutTool(context):
    """Export layouts as a set of XML files."""
    site = context.getSite()
    tool = getToolByName(site, 'portal_layouts')

    ltconf = LayoutToolExportConfigurator(site).__of__(site)
    lconf = LayoutExportConfigurator(site).__of__(site)

    tool_xml = ltconf.generateXML()
    context.writeDataFile(_FILENAME, tool_xml, 'text/xml')

    for info in ltconf.getLayoutToolInfo():
        layout_id = info['id']
        layout = tool[layout_id]
        lconf.setContext(layout)
        xml = lconf.generateXML()
        context.writeDataFile(_getLayoutFilename(layout_id),
                              xml, 'text/xml',
                              _getLayoutDir(layout_id))
    return "Layouts exported."


class LayoutToolImportConfigurator(ImportConfiguratorBase):
    def _getImportMapping(self):
        return {
            'layout-tool': {
                'layout': {KEY: 'layouts', DEFAULT: (),
                           CONVERTER: self._convertLayouts},},
            'layout': {
                'id': {},
                'filename': {DEFAULT: ''},},
            }

    def _convertLayouts(self, val):
        for layout in val:
            if not layout['filename']:
                layout['filename'] = _getLayoutPath(layout['id'])
        return val

InitializeClass(LayoutToolImportConfigurator)


class LayoutToolExportConfigurator(ExportConfiguratorBase):
    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'getLayoutToolInfo')
    def getLayoutToolInfo(self):
        """Return a list of mappings for layouts in the site."""
        result = []
        tool = getToolByName(self._site, 'portal_layouts')
        ids = tool.objectIds()
        ids.sort()
        for dir_id in ids:
            info = {'id': dir_id}
            # filename?
            result.append(info)
        return result

    def _getExportTemplate(self):
        return PageTemplateFile('layoutToolExport.xml', _xmldir)

InitializeClass(LayoutToolExportConfigurator)


class LayoutImportConfigurator(ImportConfiguratorBase):
    """Layout import configurator.
    """
    def _getImportMapping(self):
        return {
            'layout': {
                'widget': {KEY: 'widgets', DEFAULT: ()},
                'table': {CONVERTER: self._convertToUnique},
                'property': {KEY: 'properties', DEFAULT: ()},
                },
            'widget': {
                'id': {},
                'type': {},
                'property': {KEY: 'properties', DEFAULT: ()},
                },
            'table': {
                'row': {KEY: 'rows', DEFAULT: ()},
                },
            'row': {
                'cell': {KEY: 'cells', DEFAULT: ()},
                },
            'cell': {
                'id': {},
                'ncols': {CONVERTER: self._convertToInt, DEFAULT: 1},
                },
            }

    def _convertToInt(self, val):
        return int(val)

InitializeClass(LayoutImportConfigurator)


class LayoutExportConfigurator(ExportConfiguratorBase):
    """Layout export configurator for a given layout.
    """
    security = ClassSecurityInfo()

    def _getExportTemplate(self):
        return PageTemplateFile('layoutExport.xml', _xmldir)

    def setContext(self, object):
        self.object = object

    def getNonDefaultProperties(self, ob, skip=()):
        marker = object()
        res = []
        for prop_map in ob._propertyMap():
            prop_id = prop_map['id']
            if prop_id in skip:
                continue
            value = ob.getProperty(prop_id)
            class_value = getattr(ob.__class__, prop_id, marker)
            if value == class_value:
                continue
            if (prop_map['type'] == 'boolean'
                and bool(value) == bool(class_value)):
                continue
            info = self._extractProperty(ob, prop_map)
            res.append((prop_id, info))
        res.sort()
        res = [t[1] for t in res]
        return res

    def reindent(self, s, indent='  '):
        lines = s.splitlines()
        lines = [l for l in lines if l.strip()]
        if lines:
            # Take indentation of first line from including template
            lines[0] = lines[0].strip()
        return ('\n'+indent).join(lines)

    security.declareProtected(ManagePortal, 'listLayoutPropsXML')
    def listLayoutPropsXML(self):
        """Return info about the layout."""
        layout = self.object
        prop_infos = [self._extractProperty(layout, prop_map)
                      for prop_map in layout._propertyMap()]
        propsXML = self.generatePropertyNodes(prop_infos)
        propsXML = self.reindent(propsXML, '')
        return propsXML

    security.declareProtected(ManagePortal, 'getLayoutDefinition')
    def getLayoutDefinition(self):
        """Return info about the layout table (layoutdef)."""
        return self.object.getLayoutDefinition()

    security.declareProtected(ManagePortal, 'listWidgetInfos')
    def listWidgetInfos(self):
        """Return a list of mappings for widgets in the layout."""
        result = []
        layout = self.object
        widget_ids = layout.keys()
        widget_ids.sort()
        for widget_id in widget_ids:
            widget = layout[widget_id]
            prop_infos = self.getNonDefaultProperties(widget)
            propsXML = self.generatePropertyNodes(prop_infos)
            propsXML = self.reindent(propsXML, '  ')
            info = {
                'id': widget_id,
                'type': widget.meta_type,
                'propsXML': propsXML,
                }
            result.append(info)
        return result

InitializeClass(LayoutExportConfigurator)


def _getLayoutDir(dir_id):
    """Return the folder name for the layouts files."""
    return 'layouts'

def _getLayoutFilename(dir_id):
    """Return the file name holding info for a given layout."""
    return dir_id.replace(' ', '_') + '.xml'

def _getLayoutPath(dir_id):
    """Return the file path holding info for a given layout."""
    base = _getLayoutDir(dir_id)
    file = _getLayoutFilename(dir_id)
    if base:
        return base+'/'+file
    else:
        return file
