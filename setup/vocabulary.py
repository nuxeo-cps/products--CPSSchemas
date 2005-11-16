# Copyright (c) 2005 Nuxeo SAS <http://nuxeo.com>
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
# $Id:$
"""Vocabulary tool import/export for CMFSetup.
"""

import os
from Globals import package_home
from Globals import InitializeClass
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName

from Products.CMFSetup.utils import ExportConfiguratorBase
from Products.CMFSetup.utils import ImportConfiguratorBase
from Products.CMFSetup.utils import CONVERTER, DEFAULT, KEY

from Products.CPSSchemas.VocabulariesTool import VocabularyTypeRegistry
from Products.CPSSchemas.Vocabulary import CPSVocabulary
from Products.CPSSchemas.MethodVocabulary import MethodVocabulary

_pkgdir = package_home(globals())
_xmldir = os.path.join(_pkgdir, 'xml')


_FILENAME = 'vocabularies.xml'


def exportVocabularyTool(context):
    """Export vocabularies as a set of XML files."""
    site = context.getSite()
    tool = getToolByName(site, 'portal_vocabularies')

    vtconf = VocabularyToolExportConfigurator(site).__of__(site)

    tool_xml = vtconf.generateXML()
    context.writeDataFile(_FILENAME, tool_xml, 'text/xml')

    for info in vtconf.getVocabularyToolInfo():
        vocab_id = info['id']
        __traceback_info__ = vocab_id
        vocab = tool[vocab_id]
        exporter = VocabularyTypeRegistry.getExporter(vocab.meta_type)
        if exporter is None:
            exporter = PropertiesVocabularyExportConfigurator
        vconf = exporter(site).__of__(site)
        vconf.setObject(vocab)
        xml = vconf.generateXML()
        context.writeDataFile(_getVocabularyFilename(vocab_id),
                              xml, 'text/xml',
                              _getVocabularyDir(vocab_id))
    return "Vocabularies exported."


def importVocabularyTool(context):
    """Import vocabularies."""
    site = context.getSite()
    encoding = 'ISO-8859-15' # context.getEncoding()
    tool = getToolByName(site, 'portal_vocabularies')

    if context.shouldPurge():
        for vocab_id in tool.objectIds():
            tool._delObject(vocab_id)

    text = context.readDataFile(_FILENAME)
    if text is None:
        return "Vocabularies: nothing to import."

    vtconf = VocabularyToolImportConfigurator(site, encoding)

    tool_info = vtconf.parseXML(text)

    for vocab_info in tool_info['vocabularies']:
        vconf = VocabularyImportConfigurator(site, encoding)
        vocab_id = str(vocab_info['id'])
        filename = vocab_info['filename']
        sep = filename.rfind( '/' )
        if sep == -1:
            vocab_text = context.readDataFile(filename)
        else:
            vocab_text = context.readDataFile(filename[sep+1:],
                                              filename[:sep])
        vocab_info = vconf.parseXML(vocab_text)
        vconf.create(tool, vocab_id, vocab_info)

    return "Vocabularies imported."


class VocabularyToolExportConfigurator(ExportConfiguratorBase):
    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'getVocabularyToolInfo')
    def getVocabularyToolInfo(self):
        """Return a list of mappings for vocabularies in the site."""
        tool = getToolByName(self._site, 'portal_vocabularies')
        ids = tool.objectIds()
        ids.sort()
        return [{'id': dir_id} for dir_id in ids]

    def _getExportTemplate(self):
        return PageTemplateFile('vocabularyToolExport.xml', _xmldir)

InitializeClass(VocabularyToolExportConfigurator)


class VocabularyToolImportConfigurator(ImportConfiguratorBase):
    """Vocabulary tool import configurator.
    """
    def _getImportMapping(self):
        return {
            'vocabulary-tool': {
                'vocabulary': {KEY: 'vocabularies', DEFAULT: (),
                               CONVERTER: self._convertVocabularies},
                },
            'vocabulary': {
                'id': {},
                'filename': {DEFAULT: ''},
                },
            }

    def _convertVocabularies(self, val):
        for vocab in val:
            if not vocab['filename']:
                vocab['filename'] = _getVocabularyPath(vocab['id'])
        return val

InitializeClass(VocabularyToolImportConfigurator)


class PropertiesVocabularyExportConfigurator(ExportConfiguratorBase):
    """Export configurator for vocabulary based on properties.
    """
    security = ClassSecurityInfo()

    def _getExportTemplate(self):
        return PageTemplateFile('propsvocabularyExport.xml', _xmldir)

    def setObject(self, object):
        self.object = object

    def reindent(self, s, indent='  '):
        lines = s.splitlines()
        lines = [l for l in lines if l.strip()]
        if lines:
            # Take indentation of first line from including template
            lines[0] = lines[0].strip()
        return ('\n'+indent).join(lines)

    security.declareProtected(ManagePortal, 'getVocabularyPropsXML')
    def getVocabularyPropsXML(self):
        """Return info about the properties."""
        vocab = self.object
        prop_infos = [self._extractProperty(vocab, prop_map)
                      for prop_map in vocab._propertyMap()]
        propsXML = self.generatePropertyNodes(prop_infos)
        propsXML = self.reindent(propsXML, '')
        return propsXML

    security.declareProtected(ManagePortal, 'getType')
    def getType(self):
        """Get the vocabulary type."""
        return self.object.meta_type


InitializeClass(PropertiesVocabularyExportConfigurator)


class CPSVocabularyExportConfigurator(ExportConfiguratorBase):
    """Vocabulary export configurator.
    """
    security = ClassSecurityInfo()

    def _getExportTemplate(self):
        return PageTemplateFile('cpsvocabularyExport.xml', _xmldir)

    def setObject(self, object):
        self.object = object

    security.declareProtected(ManagePortal, 'getVocabularyInfo')
    def getVocabularyInfo(self):
        """Get info about this vocabulary
        """
        vocitems = []
        vocab = self.object
        for key, value in vocab.items():
            __traceback_info__ = (key, value, vocab.getMsgid(key))
            vocitem = {'key': unicode(key, 'ISO-8859-15'),
                       'value': unicode(value, 'ISO-8859-15')}
            msgid = vocab.getMsgid(key)
            if msgid is not None:
                vocitem['msgid'] = unicode(msgid, 'ISO-8859-15')
            vocitems.append(vocitem)
        return {'type': vocab.meta_type,
                'vocitems': vocitems}

InitializeClass(CPSVocabularyExportConfigurator)


class VocabularyImportConfigurator(ImportConfiguratorBase):
    """Vocabulary import configurator.

    The import mapping has to be able to read all vocabularies
    possible, otherwise we'd have to sniff the type before parsing.
    """
    def _getImportMapping(self):
        return {
            'vocabulary': {
                'type': {},
                'property': {KEY: 'properties', DEFAULT: ()},
                'item': {KEY: 'items', DEFAULT: ()},
                },
            'item': {
                'key': {},
                'value': {},
                'msgid': {DEFAULT: None},
                },
            }

    def create(self, tool, id, info):
        # Items
        if info['items']:
            tuples = [(vocitem['key'], vocitem['value'], vocitem['msgid'])
                      for vocitem in info['items']]
            kw = {'tuples': tuples}
        else:
            kw = {}
        voc = tool.manage_addCPSVocabulary(id, info['type'], **kw)
        # Properties
        for prop_info in info['properties']:
            self.initProperty(voc, prop_info)
        if getattr(aq_base(voc), '_postProcessProperties', None) is not None:
            voc._postProcessProperties()


VocabularyTypeRegistry.register(CPSVocabulary,
                                CPSVocabularyExportConfigurator)


def _getVocabularyDir(dir_id):
    """Return the folder name for the vocabularies files."""
    return 'vocabularies'

def _getVocabularyFilename(dir_id):
    """Return the file name holding info for a given vocabulary."""
    return dir_id.replace(' ', '_') + '.xml'

def _getVocabularyPath(dir_id):
    """Return the file path holding info for a given vocabulary."""
    base = _getVocabularyDir(dir_id)
    file = _getVocabularyFilename(dir_id)
    if base:
        return base+'/'+file
    else:
        return file
