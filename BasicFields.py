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
"""BasicFields

Definition of standard field types.
"""

from zLOG import LOG, DEBUG
from types import IntType, StringType
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from DateTime.DateTime import DateTime

from Products.CPSDocument.Field import CPSField, FieldRegistry
from Products.CPSDocument.Field import propertiesWithType


class ValidationError(ValueError):
    pass


class CPSIntField(CPSField):
    """Integer field."""
    meta_type = "CPS Int Field"
    _properties = propertiesWithType(CPSField._properties, 'default', 'int')
    default = 0

    def validate(self, value):
        if isinstance(value, IntType):
            return value
        raise ValidationError('Not an integer: %s' % repr(value))

InitializeClass(CPSIntField)


class CPSStringField(CPSField):
    """String field."""
    meta_type = "CPS String Field"
    #_properties = propertiesWithType(CPSField._properties, 'default', 'string')

    def validate(self, value):
        if isinstance(value, StringType):
            return value
        raise ValidationError('Not a string: %s' % repr(value))


InitializeClass(CPSStringField)


class CPSDateTimeField(CPSField):
    """DateTime field."""
    meta_type = "CPS DateTime Field"
    _properties = CPSField._properties + (
        {'id': 'allow_none', 'type': 'boolean', 'mode': 'w',
         'label': 'Allow None'},
        },
        )
    _properties = propertiesWithType(_properties, 'default', 'date')
    allow_none = 1

    def validate(self, value):
        if self.allow_none and not value:
            return None
        if isinstance(value, DateTime):
            return value
        raise ValidationError('Not a datetime: %s' % repr(value))

InitializeClass(CPSDateTimeField)


# Register field classes

FieldRegistry.register(CPSStringField)
FieldRegistry.register(CPSIntField)
FieldRegistry.register(CPSDateTimeField)
