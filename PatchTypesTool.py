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

from Products.CMFCore.TypesTool import TypesTool, typeClasses
from AccessControl.PermissionRole import PermissionRole

from Products.CMFCore.CMFCorePermissions import ManagePortal


from Products.CPSDocument.FlexibleTypeInformation import FlexibleTypeInformation
from Products.CPSDocument.FlexibleTypeInformation import addFlexibleTypeInformationForm
from Products.CPSDocument.FlexibleTypeInformation import addFlexibleTypeInformation


#
# Add Flexible Type Information to Types Tool
#

addflex = 1
for tc in typeClasses:
    if tc['name'] == FlexibleTypeInformation.meta_type:
        addflex = 0
        break
if addflex:
    typeClasses.append(
        {'class': FlexibleTypeInformation,
         'name': FlexibleTypeInformation.meta_type,
         'action': 'addFlexibleTypeInformationForm',
         'permission': ManagePortal,
        })

TypesTool.addFlexibleTypeInformationForm = addFlexibleTypeInformationForm
TypesTool.addFlexibleTypeInformationForm__roles__ = PermissionRole(ManagePortal)
TypesTool.addFlexibleTypeInformation = addFlexibleTypeInformation
TypesTool.addFlexibleTypeInformationForm__roles__ = PermissionRole(ManagePortal)
