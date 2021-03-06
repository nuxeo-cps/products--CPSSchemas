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
"""Obsolete Widget Types Tool

Kept to avoid breaking existing instances.
"""

from Globals import InitializeClass
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import SimpleItemWithProperties

from Products.CPSSchemas.Widget import widgetRegistry

class WidgetTypesTool(UniqueObject, SimpleItemWithProperties):
    """Obsolete Widget Types Tool
    """
    id = 'portal_widget_types'
    meta_type = 'Obsolete CPS Widget Types Tool'
    title = "Obsolete Tool, remove this"

InitializeClass(WidgetTypesTool)


# BBB compatibility code, will be removed in CPS 3.4.1
class WidgetTypeRegistryClass(object):
    def register(self, tcls, cls=None):
        import warnings
        if cls is None:
            cls = tcls.cls
        # Hack around changes between type registration and meta_type
        if cls.meta_type.startswith('CPS '):
            cls.meta_type = cls.meta_type[4:]
        widgetRegistry.register(cls)
        warnings.warn("WidgetTypeRegistry.register for %r is deprecated, "
                      "please use widgetRegistry.register instead" %
                      cls.meta_type, DeprecationWarning, stacklevel=2)
WidgetTypeRegistry = WidgetTypeRegistryClass()
