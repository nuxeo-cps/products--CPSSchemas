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

from logging import getLogger

import Products.CMFCore
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.permissions import ManagePortal

import Field
import Schema
import Layout

import VocabulariesTool

import SchemasTool
import LayoutsTool
import WidgetTypesTool

import DublinCorePatch

import LocalVocabulary

logger = getLogger(__name__)

import DiskFile

import utils

tools = (
    VocabulariesTool.VocabulariesTool,
    SchemasTool.SchemasTool,
    LayoutsTool.LayoutsTool,
    )

registerDirectory('skins', globals())

def initialize(registrar):
    registrar.registerClass(
        Schema.CPSSchema,
        permission=ManagePortal,
        constructors=(Schema.addCPSSchemaForm,
                      Schema.addCPSSchema,),
        )
    registrar.registerClass(
        LocalVocabulary.LocalVocabularyContainer,
        permission=ManagePortal,
        constructors=(LocalVocabulary.addLocalVocabularyContainer,),
        )

# Registering the DiskFile so it can be added through the ZMI is really
# useful only for debugging.
#     registrar.registerClass(
#         DiskFile.DiskFile,
#         constructors=(DiskFile.addDiskFileForm,
#                       DiskFile.addDiskFile,)
#         )
    Products.CMFCore.utils.ToolInit(
        'CPS Document Tools',
        tools = tools,
        icon = 'tool.png',
        ).initialize(registrar)
