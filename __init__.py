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

from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.CMFCorePermissions import ManagePortal

import Vocabulary
import Field
import Schema
import Layout

import VocabulariesTool
import SchemasTool
import LayoutsTool
import WidgetTypesTool

import BasicFields
import BasicWidgets

tools = (
    VocabulariesTool.VocabulariesTool,
    SchemasTool.SchemasTool,
    LayoutsTool.LayoutsTool,
    WidgetTypesTool.WidgetTypesTool,
    )

registerDirectory('skins/cps_schemas', globals())

def initialize(registrar):
    registrar.registerClass(
        Vocabulary.CPSVocabulary,
        permission=ManagePortal,
        constructors=(Vocabulary.addCPSVocabularyForm,
                      Vocabulary.addCPSVocabulary,),
        )
    registrar.registerClass(
        Schema.CPSSchema,
        permission=ManagePortal,
        constructors=(Schema.addCPSSchemaForm,
                      Schema.addCPSSchema,),
        )
    utils.ToolInit(
        'CPS Document Tools',
        tools = tools,
        product_name = 'CPSSchemas',
        icon = 'tool.gif',
        ).initialize(registrar)
