# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com>
# Author: M.-A. DARCHE <madarche@nuxeo.com>
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

"""
"""

from Products.CMFCore.interfaces.DublinCore import DublinCore, MutableDublinCore
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from zLOG import LOG, DEBUG

LOG('DublinCorePatch', DEBUG, "Patching DublinCore...")


def Coverage(self):
    """
    """

def Source(self):
    """
    """

def Relation(self):
    """
    """

DublinCore.Coverage = Coverage
DublinCore.Source = Source
DublinCore.Relation = Relation
InitializeClass(DublinCore)


def setCoverage(self, coverage):
    """
    """

def setSource(self, source):
    """
    """

def setRelation(self, relation):
    """
    """

MutableDublinCore.setCoverage = setCoverage
MutableDublinCore.setSource = setSource
MutableDublinCore.setRelation = setRelation
InitializeClass(MutableDublinCore)


security = ClassSecurityInfo()

security.declarePublic('Coverage')
def Coverage(self):
    return self.coverage

security.declareProtected(ModifyPortalContent, 'setCoverage')
def setCoverage(self, coverage):
    self.coverage = coverage

security.declarePublic('Source')
def Source(self):
    return self.source

security.declareProtected(ModifyPortalContent, 'setSource')
def setSource(self, source):
    self.source = source

security.declarePublic('Relation')
def Relation(self):
    return self.relation

security.declareProtected(ModifyPortalContent, 'setRelation')
def setRelation(self, relation):
    self.relation = relation

DefaultDublinCoreImpl.Coverage = Coverage
DefaultDublinCoreImpl.setCoverage = setCoverage
DefaultDublinCoreImpl.Source = Source
DefaultDublinCoreImpl.setSource = setSource
DefaultDublinCoreImpl.Relation = Relation
DefaultDublinCoreImpl.setRelation = setRelation

# Setting default values for the new metadata
DefaultDublinCoreImpl.coverage = ''
DefaultDublinCoreImpl.source = ''
DefaultDublinCoreImpl.relation = ''

DefaultDublinCoreImpl.security = security
InitializeClass(DefaultDublinCoreImpl)


LOG('DublinCorePatch', DEBUG, "Patching DublinCore done.")
