# -*- coding: iso-8859-15 -*-
# (C) Copyright 2003-2004 Nuxeo SARL <http://nuxeo.com>
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

from zLOG import LOG, INFO

# PATCH For Plone

try:
    from Products.CMFPlone.Portal import PloneSite
    import PlacelessTranslationServicePatch
    LOG("Patch PlacelessTranslationService for CPS compatiblity",
        INFO,
        "translate() accessible through restricted code on PLTS"
        "Patch CMF / Plone portal to have a fake Localizer access point")
except ImportError:
    # CMF / CPS instance
    pass

# EOF

from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.CMFCorePermissions import ManagePortal

import Field
import Schema
import Layout

import VocabulariesTool
from VocabulariesTool import VocabularyTypeRegistry
from Vocabulary import CPSVocabulary
from MethodVocabulary import MethodVocabulary

import SchemasTool
import LayoutsTool
import WidgetTypesTool

import BasicFields
import BasicWidgets
import ExtendedWidgets

import DublinCorePatch
import EpozPatch
import DiskFile

tools = (
    VocabulariesTool.VocabulariesTool,
    SchemasTool.SchemasTool,
    LayoutsTool.LayoutsTool,
    WidgetTypesTool.WidgetTypesTool,
    )

registerDirectory('skins', globals())

def initialize(registrar):
    registrar.registerClass(
        Schema.CPSSchema,
        permission=ManagePortal,
        constructors=(Schema.addCPSSchemaForm,
                      Schema.addCPSSchema,),
        )
# Registering the DiskFile so it can be added through the ZMI is really
# useful only for debugging.
#     registrar.registerClass(
#         DiskFile.DiskFile,
#         constructors=(DiskFile.addDiskFileForm,
#                       DiskFile.addDiskFile,)
#         )
    utils.ToolInit(
        'CPS Document Tools',
        tools = tools,
        product_name = 'CPSSchemas',
        icon = 'tool.png',
        ).initialize(registrar)
    VocabularyTypeRegistry.register(CPSVocabulary)
    VocabularyTypeRegistry.register(MethodVocabulary)
