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
from Products.CMFCore.CMFCorePermissions import AddPortalContent, ManagePortal

import PatchTypesTool

import Vocabulary
import Field
import Schema
import Layout

import SchemasTool
import VocabulariesTool
import LayoutsTool

import BasicFields
import BasicWidgets

import CPSDocument

tools = (
    SchemasTool.SchemasTool,
    VocabulariesTool.VocabulariesTool,
    LayoutsTool.LayoutsTool,
    )


#from FieldsTypes import FieldsTypes


contentClasses = (
    CPSDocument.CPSDocument,
)

contentConstructors = (
    CPSDocument.addCPSDocument,
)

fti = (
#    CPSDocument.factory_type_information +
#    ()
)

registerDirectory('skins', globals())

def initialize(registrar):
    #FieldsTypes.registerFieldType('string', StringField())
    #FieldsTypes.registerFieldType('int', IntField())

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
        product_name = 'CPSDocument',
        icon = 'tool.gif',
        ).initialize(registrar)

    utils.ContentInit(
        'CPS Document Types',
        content_types = contentClasses,
        permission = AddPortalContent,
        extra_constructors = contentConstructors,
        fti = fti,
    ).initialize(registrar)
