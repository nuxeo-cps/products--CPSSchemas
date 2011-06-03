# (C) Copyright 2005-2007 Nuxeo SAS <http://nuxeo.com>
# Authors:
# Florent Guillaume <fg@nuxeo.com>
# Georges Racinet <gracinet@nuxeo.com>
# M.-A. Darche <madarche@nuxeo.com>
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
"""Vocabulary Tool XML Adapter.
"""

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.CPSUtil.PropertiesPostProcessor import (
    PostProcessingPropertyManagerHelpers)
#XXX GR move this to some common place or when remove attribute bug is
# fixed in GenericSetup
from Products.CPSDocument.exportimport import CPSObjectManagerHelpers

from Products.CPSSchemas.interfaces import IVocabularyTool
from Products.CPSSchemas.interfaces import IPropertyVocabulary
from Products.CPSSchemas.interfaces import ICPSVocabulary


TOOL = 'portal_vocabularies'
NAME = 'vocabularies'

def exportVocabularyTool(context):
    """Export Vocabulary tool and vocabularies as a set of XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL, None)
    if tool is None:
        logger = context.getLogger(NAME)
        logger.info("Nothing to export.")
        return
    exportObjects(tool, '', context)

def importVocabularyTool(context):
    """Import Vocabulary tool and vocabularies from XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL)
    importObjects(tool, '', context)


class VocabularyToolXMLAdapter(XMLAdapterBase, CPSObjectManagerHelpers,
                               PropertyManagerHelpers):
    """XML importer and exporter for Vocabulary tool.
    """

    # BBB: use adapts() in 2.9
    __used_for__ = IVocabularyTool

    _LOGGER_ID = NAME
    name = NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractObjects())
        self._logger.info("Vocabulary tool exported.")
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgeObjects()
        self._initProperties(node)
        self._initObjects(node)
        self._logger.info("Vocabulary tool imported.")

class PropertyVocabularyXMLAdapter(XMLAdapterBase,
                                   PostProcessingPropertyManagerHelpers):
    """XML importer and exporter for a property-based vocabulary.
    """

    # BBB: use adapts() in 2.9
    __used_for__ = IPropertyVocabulary

    _LOGGER_ID = NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        self._logger.info("%r vocabulary exported." % self.context.getId())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
        self._initProperties(node)
        self._logger.info("%r vocabulary imported." % self.context.getId())

class CPSVocabularyXMLAdapter(XMLAdapterBase,
                              PostProcessingPropertyManagerHelpers):
    """XML importer and exporter for a CPS vocabulary.
    """

    __used_for__ = ICPSVocabulary

    _LOGGER_ID = NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractItems())
        self._logger.info("%r vocabulary exported." % self.context.getId())
        return node

    def _extractItems(self):
        vocab = self.context
        fragment = self._doc.createDocumentFragment()
        for key, value in vocab.items():
            key = str(key) # key should be ascii only
            child = self._doc.createElement('item')
            child.setAttribute('key', key)
            if isinstance(value, unicode):
                value = value.encode('utf-8') # default xml encoding
            child.appendChild(self._doc.createTextNode(value))
            msgid = vocab.getMsgid(key)
            if msgid is not None:
                child.setAttribute('msgid', msgid)
            fragment.appendChild(child)
        return fragment

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgeItems()
        self._initProperties(node)
        self._initItems(node)
        self._logger.info("%r vocabulary imported." % self.context.getId())

    def _purgeItems(self):
        self.context.clear()

    def _initItems(self, node):
        vocab = self.context
        for child in node.childNodes:
            if child.nodeName != 'item':
                continue
            key = child.getAttribute('key')
            key = str(key) # key should be ascii only
            value = self._getNodeText(child)
            if child.hasAttribute('msgid'):
                msgid = str(child.getAttribute('msgid'))
            else:
                msgid = None
            vocab.set(key, value, msgid)
