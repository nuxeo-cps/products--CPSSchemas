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
"""Schemas tool import/export for CMFSetup.
"""

import os
from Globals import package_home
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName

from Products.CMFSetup.utils import ConfiguratorBase
from Products.CMFSetup.utils import CONVERTER, DEFAULT, KEY

_pkgdir = package_home(globals())
_xmldir = os.path.join(_pkgdir, 'setupxml')


_FILENAME = 'schemas.xml'


def importSchemaTool(context):
    """Import schemas."""
    site = context.getSite()
    encoding = context.getEncoding()
    tool = getToolByName(site, 'portal_schemas')

    if context.shouldPurge():
        for schema_id in tool.objectIds():
            tool._delObject(schema_id)

    text = context.readDataFile(_FILENAME)
    if text is None:
        return "Schemas: nothing to import."

    stconf = SchemaToolImportConfigurator(site, encoding)
    sconf = SchemaImportConfigurator(site, encoding)

    tool_info = stconf.parseXML(text)

    for schema_info in tool_info['schemas']:
        schema_id = str(schema_info['id'])
        filename = schema_info['filename']
        sep = filename.rfind( '/' )
        if sep == -1:
            schema_text = context.readDataFile(filename)
        else:
            schema_text = context.readDataFile(filename[sep+1:],
                                               filename[:sep])
        schema_info = sconf.parseXML(schema_text)

        schema = tool.manage_addCPSSchema(schema_id)

        for field_info in schema_info['fields']:
            id = field_info['id']
            kind = field_info['kind']
            field = schema.manage_addField(id, kind)
            for prop_info in field_info['properties']:
                sconf.initProperty(field, prop_info)
            field._postProcessProperties()

    return "Schemas imported."


def exportSchemaTool(context):
    """Export schemas as a set of XML files."""
    site = context.getSite()
    tool = getToolByName(site, 'portal_schemas')

    stconf = SchemaToolExportConfigurator(site).__of__(site)
    sconf = SchemaExportConfigurator(site).__of__(site)

    tool_xml = stconf.generateXML()
    context.writeDataFile(_FILENAME, tool_xml, 'text/xml')

    for info in stconf.getSchemaToolInfo():
        schema_id = info['id']
        schema = tool[schema_id]
        sconf.setObject(schema)
        xml = sconf.generateXML()
        context.writeDataFile(_getSchemaFilename(schema_id),
                              xml, 'text/xml',
                              _getSchemaDir(schema_id))
    return "Schemas exported."


class SchemaToolImportConfigurator(ConfiguratorBase):
    security = ClassSecurityInfo()

    def _getExportTemplate(self): # XXX artefact
        return None

    def _getImportMapping(self):
        return {
            'schema-tool': {
                'schema': {KEY: 'schemas', DEFAULT: (),
                           CONVERTER: self._convertSchemas},},
            'schema': {
                'id': {},
                'filename': {DEFAULT: ''},},
            }

    def _convertSchemas(self, val):
        for schema in val:
            if not schema['filename']:
                schema['filename'] = _getSchemaPath(schema['id'])
        return val

InitializeClass(SchemaToolImportConfigurator)


class SchemaToolExportConfigurator(ConfiguratorBase):
    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'getSchemaToolInfo')
    def getSchemaToolInfo(self):
        """Return a list of mappings for schemas in the site."""
        result = []
        tool = getToolByName(self._site, 'portal_schemas')
        ids = tool.objectIds()
        ids.sort()
        for dir_id in ids:
            info = {'id': dir_id}
            # filename?
            result.append(info)
        return result

    def _getExportTemplate(self):
        return PageTemplateFile('schemaToolExport.xml', _xmldir)

InitializeClass(SchemaToolExportConfigurator)


class SchemaImportConfigurator(ConfiguratorBase):
    """Schema import configurator.
    """
    def _getExportTemplate(self): # XXX artefact
        return None

    def _getImportMapping(self):
        return {
            'schema': {
                'field': {KEY: 'fields', DEFAULT: ()},
                },
            'field': {
                'id': {},
                'kind': {},
                'property': {KEY: 'properties', DEFAULT: ()},
                },
            }

InitializeClass(SchemaImportConfigurator)


class SchemaExportConfigurator(ConfiguratorBase):
    """Schema export configurator for a given schema.
    """
    security = ClassSecurityInfo()

    def _getExportTemplate(self):
        return PageTemplateFile('schemaExport.xml', _xmldir)

    def setObject(self, object):
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
            # Old Zopes stored lists, not tuples
            #if isinstance(class_value, list):
            #    class_value = tuple(class_value)
            #if isinstance(value, list):
            #    value = tuple(value)
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

    security.declareProtected(ManagePortal, 'listFieldInfos')
    def listFieldInfos(self):
        """Return a list of mappings for fields in the schema."""
        result = []
        schema = self.object
        field_ids = schema.keys()
        field_ids.sort()
        for field_id in field_ids:
            field = schema[field_id]
            prop_infos = self.getNonDefaultProperties(field,
                                            skip=('getFieldIdProperty',))
            propsXML = self.generatePropertyNodes(prop_infos)
            propsXML = self.reindent(propsXML, '  ')
            info = {
                'id': field_id,
                'kind': field.meta_type,
                'propsXML': propsXML,
                }
            result.append(info)
        return result

InitializeClass(SchemaExportConfigurator)


def _getSchemaDir(dir_id):
    """Return the folder name for the schemas files."""
    return 'schemas'

def _getSchemaFilename(dir_id):
    """Return the file name holding info for a given schema."""
    return dir_id.replace(' ', '_') + '.xml'

def _getSchemaPath(dir_id):
    """Return the file path holding info for a given schema."""
    base = _getSchemaDir(dir_id)
    file = _getSchemaFilename(dir_id)
    if base:
        return base+'/'+file
    else:
        return file
