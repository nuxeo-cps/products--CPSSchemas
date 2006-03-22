# (C) Copyright 2005 Nuxeo SAS <http://nuxeo.com>
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
"""Schema Tool XML Adapter.
"""

from Acquisition import aq_base
from zope.app import zapi
from zope.component import adapts
from zope.interface import implements
import Products
from ZODB.loglevels import BLATHER as VERBOSE
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.CPSUtil.PropertiesPostProcessor import (
    PostProcessingPropertyManagerHelpers)

from Products.GenericSetup.interfaces import INode
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron

from Products.CPSSchemas.interfaces import ISchemaTool
from Products.CPSSchemas.interfaces import ISchema
from Products.CPSSchemas.interfaces import IField


_marker = object()

TOOL = 'portal_schemas'
NAME = 'schemas'

def exportSchemaTool(context):
    """Export Schema tool, schemas and fields as a set of XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL, None)
    if tool is None:
        logger = context.getLogger(NAME)
        logger.info("Nothing to export.")
        return
    exportObjects(tool, '', context)

def importSchemaTool(context):
    """Import Schema tool, schemas and fields from XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL)
    importObjects(tool, '', context)


class SchemaToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers,
                           PropertyManagerHelpers):
    """XML importer and exporter for Schema tool.
    """

    adapts(ISchemaTool, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = NAME
    name = NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractSchemas())
        self._logger.info("Schema tool exported.")
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgeSchemas()
        self._initProperties(node)
        self._initSchemas(node)
        self._logger.info("Schema tool imported.")

    node = property(_exportNode, _importNode)

    def _extractSchemas(self):
        fragment = self._doc.createDocumentFragment()
        items = self.context.objectItems()
        items.sort()
        for id, ob in items:
            exporter = zapi.queryMultiAdapter((ob, self.environ), INode)
            if not exporter:
                raise ValueError("Schema %s cannot be adapted to INode" % ob)
            child = exporter._getObjectNode('object', False)
            fragment.appendChild(child)
        return fragment

    def _purgeSchemas(self):
        self._purgeObjects()

    def _initSchemas(self, node):
        self._initObjects(node)


class SchemaXMLAdapter(XMLAdapterBase, PostProcessingPropertyManagerHelpers):
    """XML importer and exporter for a schema.
    """

    adapts(ISchema, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractFields())
        self._logger.info("%s schema exported." % self.context.getId())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeFields()
        self._initFields(node)
        self._logger.info("%s schema imported." % self.context.getId())

    node = property(_exportNode, _importNode)

    def _extractFields(self):
        schema = self.context
        fragment = self._doc.createDocumentFragment()
        items = schema.items()
        items.sort()
        for field_id, field in items:
            exporter = zapi.queryMultiAdapter((field, self.environ), INode)
            if not exporter:
                raise ValueError("Field %s cannot be adapted to INode" % field)
            child = exporter.node
            fragment.appendChild(child)
        return fragment

    def _purgeFields(self):
        schema = self.context
        for id in list(schema.objectIds()):
            schema._delObject(id)

    def _initFields(self, node):
        schema = self.context
        for child in node.childNodes:
            if child.nodeName != 'field':
                continue
            field_id = str(child.getAttribute('name'))
            meta_type = child.getAttribute('meta_type')

            if child.hasAttribute('remove'):
                if schema.has_key(field_id):
                    schema.delSubObject(field_id)
                    msg = "Field %s removed"
                    self._logger.log(VERBOSE, msg)
                else:
                    msg = "Attempt of removing non-existent field %s" % field_id
                    self._logger.warning(msg)
                continue

            old_state = None
            if schema.has_key(field_id) and meta_type:
                field = schema[field_id]
                if field.meta_type != str(meta_type):
                    # Need to transtype the field
                    old_state = field.__dict__.copy()
                    schema.delSubObject(field_id)

            if not schema.has_key(field_id):
                meta_type = str(meta_type)
                for mt in Products.meta_types:
                    if mt['name'] == meta_type:
                        break
                else:
                    raise ValueError("Unknown meta_type %r" % meta_type)

                klass = mt['instance']
                field = klass(field_id)

                field = schema.addSubObject(field)
            else:
                field = schema[field_id]

            if old_state:
                # Transtyping: copy previous state
                field.__dict__.update(old_state)

            importer = zapi.queryMultiAdapter((field, self.environ), INode)
            if not importer:
                raise ValueError("Field %s cannot be adapted to INode" % field)

            importer.node = child # calls _importNode


class FieldXMLAdapter(XMLAdapterBase, PostProcessingPropertyManagerHelpers):
    """XML importer and exporter for a field.
    """

    adapts(IField, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        name = self.context.getFieldId()
        node = self._getObjectNode('field')
        node.setAttribute('name', name)
        node.appendChild(self._extractProperties(skip_defaults=True))
        msg = "Field %r exported." % name
        self._logger.log(VERBOSE, msg)
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
        self._initProperties(node)
        msg = "Field %r imported." % self.context.getFieldId()
        self._logger.log(VERBOSE, msg)

    node = property(_exportNode, _importNode)

    def _exportBody(self):
        """Export the object as a file body.
        """
        # We don't want file body export, just nodes.
        return None

    def _importBody(self, node):
        """Import the object from the file body.
        """
        return

    body = property(_exportBody, _importBody)

    # customized from default
    def _purgeProperties(self):
        ob = self.context
        for prop_map in ob._propertyMap():
            mode = prop_map.get('mode', 'wd')
            if 'w' not in mode:
                continue
            prop_id = prop_map['id']
            if 'd' in mode and not prop_id == 'title':
                ob._delProperty(prop_id)
            else:
                # reset to default
                if prop_id in ob.__dict__:
                    delattr(ob, prop_id)

    # customized from default
    def _extractProperties(self, skip_defaults=False):
        ob = self.context
        fragment = self._doc.createDocumentFragment()

        for prop_map in ob._propertyMap():
            prop_id = prop_map['id']
            if prop_id == 'i18n_domain':
                continue

            # Local customization: don't export read-only nodes
            if 'w' not in prop_map.get('mode', 'wd'):
                continue

            prop = ob.getProperty(prop_id)

            # Local customization:
            # don't export nodes with values equal to default
            if skip_defaults:
                cls_prop = getattr(ob.__class__, prop_id, _marker)
                if prop == cls_prop:
                    continue
                if (prop_map['type'] == 'boolean'
                    and bool(prop) == bool(cls_prop)):
                    continue

            node = self._doc.createElement('property')
            node.setAttribute('name', prop_id)

            if isinstance(prop, (tuple, list)):
                for value in prop:
                    child = self._doc.createElement('element')
                    child.setAttribute('value', value)
                    node.appendChild(child)
            else:
                if prop_map.get('type') == 'boolean':
                    prop = str(bool(prop))
                elif not isinstance(prop, basestring):
                    prop = str(prop)
                child = self._doc.createTextNode(prop)
                node.appendChild(child)

            if 'd' in prop_map.get('mode', 'wd') and not prop_id == 'title':
                type = prop_map.get('type', 'string')
                node.setAttribute('type', type)
                select_variable = prop_map.get('select_variable', None)
                if select_variable is not None:
                    node.setAttribute('select_variable', select_variable)

            if hasattr(self, '_i18n_props') and prop_id in self._i18n_props:
                node.setAttribute('i18n:translate', '')

            fragment.appendChild(node)

        return fragment
