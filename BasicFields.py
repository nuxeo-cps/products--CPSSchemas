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
from Globals import InitializeClass
from DateTime.DateTime import DateTime

from OFS.Image import File
from OFS.Image import Image

from Products.CPSDocument.Field import CPSField, FieldRegistry
from Products.CPSDocument.Field import propertiesWithType


def _isinstance(ob, cls):
    try:
        return isinstance(ob, cls)
    except TypeError:
        # In python 2.1 isinstance() raises TypeError
        # instead of returning 0 for ExtensionClasses.
        return 0


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

class CPSPwdField(CPSField):
    """Password field."""
    meta_type = "CPS Password Field"
    #_properties = propertiesWithType(CPSField._properties, 'default', 'string')

    def validate(self, value):
        if isinstance(value, StringType):
            return value
        raise ValidationError('Not a string: %s' % repr(value))

InitializeClass(CPSPwdField)


class CPSDateTimeField(CPSField):
    """DateTime field."""
    meta_type = "CPS DateTime Field"
    _properties = CPSField._properties + (
        {'id': 'allow_none', 'type': 'boolean', 'mode': 'w',
         'label': 'Allow None'},
        )
    default = ''
    allow_none = 1

    def getDefault(self):
        """Get the default datetime."""
        default = self.default
        if self.allow_none:
            if not default or default in ('None', 'none'):
                return None
        try:
            return DateTime(default)
        except (ValueError, TypeError, DateTime.DateTimeError,
                DateTime.SyntaxError, DateTime.DateError):
            return DateTime('1970-01-01')

    def validate(self, value):
        if self.allow_none and not value:
            return None
        if isinstance(value, DateTime):
            return value
        raise ValidationError('Not a datetime: %s' % repr(value))

InitializeClass(CPSDateTimeField)


class CPSFileField(CPSField):
    """File field."""
    meta_type = "CPS File Field"

    def getDefault(self):
        """Get the default file object."""
        return None

    def validate(self, value):
        if not value:
            return None
        if _isinstance(value, File):
            return value
        raise ValidationError('Not a file: %s' % repr(value))

InitializeClass(CPSFileField)


class CPSImageField(CPSField):
    """Image field."""
    meta_type = "CPS Image Field"

    def getDefault(self):
        """Get the default file object."""
        return None

    def validate(self, value):
        if not value:
            return None
        if _isinstance(value, Image):
            return value
        raise ValidationError('Not an image: %s' % repr(value))

InitializeClass(CPSImageField)

# Register field classes

FieldRegistry.register(CPSStringField)
FieldRegistry.register(CPSPwdField)
FieldRegistry.register(CPSIntField)
FieldRegistry.register(CPSDateTimeField)
FieldRegistry.register(CPSFileField)
FieldRegistry.register(CPSImageField)
