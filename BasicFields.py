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
from types import IntType, StringType, ListType, FloatType
from Globals import InitializeClass
from DateTime.DateTime import DateTime

from OFS.Image import File
from OFS.Image import Image

from Products.CPSSchemas.Field import CPSField, FieldRegistry
from Products.CPSSchemas.Field import propertiesWithType
from Products.CPSSchemas.FileUtils import convertFileToHtml
from Products.CPSSchemas.FileUtils import convertFileToText


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


class CPSFloatField(CPSField):
    """Integer field."""
    meta_type = "CPS Float Field"
    _properties = propertiesWithType(CPSField._properties, 'default', 'float')
    default = 0.0

    def validate(self, value):
        if isinstance(value, FloatType):
            return value
        raise ValidationError('Not an real number: %s' % repr(value))

InitializeClass(CPSFloatField)


class CPSStringField(CPSField):
    """String field."""
    meta_type = "CPS String Field"
    #_properties = propertiesWithType(CPSField._properties, 'default', 'string')

    def validate(self, value):
        if isinstance(value, StringType):
            return value
        raise ValidationError('Not a string: %s' % repr(value))

InitializeClass(CPSStringField)

class CPSPasswordField(CPSField):
    """Password field."""
    meta_type = "CPS Password Field"
    #_properties = propertiesWithType(CPSField._properties, 'default', 'string')

    def validate(self, value):
        if isinstance(value, StringType):
            return value
        raise ValidationError('Not a string: %s' % repr(value))

InitializeClass(CPSPasswordField)


class CPSStringListField(CPSField):
    """String List field."""
    meta_type = "CPS String List Field"
    _properties = propertiesWithType(CPSField._properties, 'default', 'lines')

    def validate(self, value):
        if isinstance(value, ListType):
            ok = 1
            for v in value:
                # XXX Deal with Unicode.
                if not isinstance(value, StringType):
                    ok = 0
                    break
            if ok:
                return value
        raise ValidationError('Not a string list: %s' % repr(value))

InitializeClass(CPSStringListField)


class CPSDateTimeField(CPSField):
    """DateTime field."""
    meta_type = "CPS DateTime Field"
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
    _properties = CPSField._properties + (
        {'id': 'suffix_html', 'type': 'string', 'mode': 'w',
         'label': 'Suffix for field containing HTML conversion'},
        {'id': 'suffix_text', 'type': 'string', 'mode': 'w',
         'label': 'Suffix for field containing Text conversion'},
        )
    suffix_html = ''
    suffix_text = ''

    def getDefault(self):
        """Get the default file object."""
        return None

    def _getDependantFieldId(self, schemas, suffix):
        """Get a dependant field id described by the suffix."""
        if not suffix:
            return None
        id = self.getFieldId() + suffix
        for schema in schemas:
            if schema.has_key(id):
                return id
        return None

    def computeDependantFields(self, schemas, data):
        """Compute dependant fields."""
        field_id = self.getFieldId()
        value = data[field_id] # May be None.
        html_field_id = self._getDependantFieldId(schemas, self.suffix_html)
        if html_field_id is not None:
            html = convertFileToHtml(value)
            data[html_field_id] = html
        text_field_id = self._getDependantFieldId(schemas, self.suffix_text)
        if text_field_id is not None:
            text = convertFileToText(value)
            data[text_field_id] = text

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
FieldRegistry.register(CPSPasswordField)
FieldRegistry.register(CPSStringListField)
FieldRegistry.register(CPSIntField)
FieldRegistry.register(CPSFloatField)
FieldRegistry.register(CPSDateTimeField)
FieldRegistry.register(CPSFileField)
FieldRegistry.register(CPSImageField)
