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

from zLOG import LOG, DEBUG, WARNING
import sys
from types import IntType, StringType, ListType, FloatType, LongType
from Globals import InitializeClass
from DateTime.DateTime import DateTime

from OFS.Image import cookId, File, Image

from Products.CMFCore.Expression import Expression

from Products.CPSSchemas.Field import CPSField, FieldRegistry
from Products.CPSSchemas.Field import ValidationError
from Products.CPSSchemas.FileUtils import convertFileToHtml
from Products.CPSSchemas.FileUtils import convertFileToText


def _isinstance(ob, cls):
    try:
        return isinstance(ob, cls)
    except TypeError:
        # In python 2.1 isinstance() raises TypeError
        # instead of returning 0 for ExtensionClasses.
        return 0

#
# UTF-8
#

default_encoding = sys.getdefaultencoding()
if default_encoding == 'ascii':
    default_encoding = 'latin1'

def toUTF8(s):
    return unicode(s, default_encoding).encode('utf-8')

def fromUTF8(s):
    return unicode(s, 'utf-8').encode(default_encoding)


class CPSIntField(CPSField):
    """Integer field."""
    meta_type = "CPS Int Field"

    default_expr = 'python:0'
    default_expr_c = Expression(default_expr)

    # XXX this is never called yet.
    def validate(self, value):
        if isinstance(value, IntType):
            return value
        raise ValidationError('Not an integer: %s' % repr(value))

    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values."""
        return [str(value)]

    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        try:
            if len(values) != 1:
                raise ValueError
            return int(values[0])
        except (ValueError, TypeError):
            raise ValidationError("Incorrect Int value from LDAP: %s"
                                  % `values`)

InitializeClass(CPSIntField)


class CPSLongField(CPSField):
    """Long field."""
    meta_type = "CPS Long Field"

    default_expr = 'python:0L'
    default_expr_c = Expression(default_expr)

    # XXX this is never called yet.
    def validate(self, value):
        if isinstance(value, LongType):
            return value
        raise ValidationError('Not an long integer: %s' % repr(value))

    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values."""
        return [str(value)]

    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        try:
            if len(values) != 1:
                raise ValueError
            return long(values[0])
        except (ValueError, TypeError):
            raise ValidationError("Incorrect Long value from LDAP: %s"
                                  % `values`)

InitializeClass(CPSLongField)


class CPSFloatField(CPSField):
    """Float field."""
    meta_type = "CPS Float Field"

    default_expr = 'python:0.0'
    default_expr_c = Expression(default_expr)

    # XXX this is never called yet.
    def validate(self, value):
        if isinstance(value, FloatType):
            return value
        raise ValidationError('Not an real number: %s' % repr(value))

    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values."""
        return [str(value)]

    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        try:
            if len(values) != 1:
                raise ValueError
            return float(values[0])
        except (ValueError, TypeError):
            raise ValidationError("Incorrect Float value from LDAP: %s"
                                  % `values`)

InitializeClass(CPSFloatField)


class CPSStringField(CPSField):
    """String field."""
    meta_type = "CPS String Field"

    default_expr = 'string:'
    default_expr_c = Expression(default_expr)

    # XXX this is never called yet.
    def validate(self, value):
        if isinstance(value, StringType):
            return value
        raise ValidationError('Not a string: %s' % repr(value))

    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values."""
        if not value:
            return []
        return [toUTF8(value)]

    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        if not values:
            return ''
        if len(values) != 1:
            LOG('CPSStringField.convertFromLDAP', WARNING,
                'Multi-valued field, cutting: %s' % `values`)
            values = values[:1]
        value = values[0]
        try:
            value = fromUTF8(value)
        except UnicodeError:
            LOG('CPSStringField.convertFromLDAP', WARNING,
                'Problem recoding %s' % `value`)
            pass
        return value

InitializeClass(CPSStringField)


class CPSPasswordField(CPSStringField):
    """Password field."""
    meta_type = "CPS Password Field"

InitializeClass(CPSPasswordField)


class CPSStringListField(CPSField):
    """String List field."""
    meta_type = "CPS String List Field"

    default_expr = 'python:[]'
    default_expr_c = Expression(default_expr)

    # XXX this is never called yet.
    def validate(self, value):
        if isinstance(value, ListType):
            ok = 1
            for v in value:
                # XXX Deal with Unicode.
                if not isinstance(v, StringType):
                    ok = 0
                    break
            if ok:
                return value
        raise ValidationError('Not a string list: %s' % repr(value))

    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values."""
        # Empty values are not allowed in LDAP
        return [toUTF8(v) for v in value if v]

    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        res = []
        for v in values:
            try:
                v = fromUTF8(v)
            except UnicodeError:
                LOG('CPSStringListField.convertFromLDAP', WARNING,
                    'problem recoding %s' % `v`)
                pass
            res.append(v)
        return res

InitializeClass(CPSStringListField)


class CPSDateTimeField(CPSField):
    """DateTime field."""
    meta_type = "CPS DateTime Field"

    default_expr = 'nothing'
    default_expr_c = Expression(default_expr)

    # XXX this is never called yet.
    def validate(self, value):
        if not value:
            return None
        if isinstance(value, DateTime):
            return value
        raise ValidationError('Not a datetime: %s' % repr(value))

    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values."""
        if not value:
            return []
        # The recommended time format for LDAP is
        # "Generalized Time", see rfc2252.
        if value.Time() == "00:00:00":
            # If a date without time is stored, ignore the timezone XXX
            pass
        else:
            # GMT is strongly recommended
            value = value.toZone('GMT')
        v = '%04d%02d%02d%02d%02d%02dZ' % (
            value.year(), value.month(), value.day(),
            value.hour(), value.minute(), value.second())
        return [v]

    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        if not values:
            return None
        try:
            if len(values) != 1:
                raise ValueError
            v = values[0]
            # strptime is not available on Windows, so do this the
            # hard way:
            year = int(v[0:4])
            month = int(v[4:6])
            day = int(v[6:8])
            hour = int(v[8:10])
            minute = int(v[10:12])
            second = int(v[12:14])
            # Timezones are in ISO spec. Examples:
            # GMT: 'Z'
            # CET: '+0100'
            # EST: '-0600'
            tz = v[14:]
            if tz[0] in ('+', '-'): # There is a timezone specified.
                tz = 'GMT' + tz
            else:
                tz = 'GMT'
            value = DateTime(year, month, day, hour, minute, second, tz)
            # Convert to local zone if there is a time XXX
            if v[8:14] != '000000':
                value = value.toZone(value.localZone())
            return  value
        except (ValueError, TypeError):
            raise ValidationError("Incorrect DateTime value from LDAP: %s" %
                                  `values`)

InitializeClass(CPSDateTimeField)


class CPSFileField(CPSField):
    """File field."""
    meta_type = "CPS File Field"

    default_expr = 'nothing'
    default_expr_c = Expression(default_expr)

    _properties = CPSField._properties + (
        {'id': 'suffix_text', 'type': 'string', 'mode': 'w',
         'label': 'Suffix for field containing Text conversion'},
        {'id': 'suffix_html', 'type': 'string', 'mode': 'w',
         'label': 'Suffix for field containing HTML conversion'},
        )
    suffix_text = ''
    suffix_html = ''

    def _getDependantFieldId(self, schemas, suffix):
        """Get a dependant field id described by the suffix."""
        if not suffix:
            return None
        id = self.getFieldId() + suffix
        for schema in schemas:
            if schema.has_key(id):
                return id
        return None

    def computeDependantFields(self, schemas, data, context=None):
        """Compute dependant fields."""
        field_id = self.getFieldId()
        file = data[field_id] # May be None.
        text_field_id = self._getDependantFieldId(schemas, self.suffix_text)
        if text_field_id is not None:
            data[text_field_id] = convertFileToText(file, context=context)
        html_field_id = self._getDependantFieldId(schemas, self.suffix_html)
        if html_field_id is not None:
            html_string = convertFileToHtml(file, context=context)
            if html_string is not None:
                fileid = cookId('', '', file)[0]
                if '.' in fileid:
                    fileid = fileid[:fileid.rfind('.')]
                if not fileid:
                    fileid = 'document'
                fileid = fileid + '.html'
                html_file = File(fileid, '', html_string,
                                 content_type='text/html')
            else:
                html_file = None
            data[html_field_id] = html_file

    # XXX this is never called yet.
    def validate(self, value):
        if not value:
            return None
        if _isinstance(value, File):
            return value
        raise ValidationError('Not a file: %s' % repr(value))

    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values."""
        if not value:
            return []
        return [str(value)]

    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        if not values:
            return None
        if len(values) != 1:
            raise ValidationError("Incorrect File value from LDAP: "
                                  "(%d-element list)" % len(values))
        return File(self.getFieldId(), '', values[0])

InitializeClass(CPSFileField)


class CPSImageField(CPSField):
    """Image field."""
    meta_type = "CPS Image Field"

    default_expr = 'nothing'
    default_expr_c = Expression(default_expr)

    # XXX this is never called yet.
    def validate(self, value):
        if not value:
            return None
        if _isinstance(value, Image):
            return value
        raise ValidationError('Not an image: %s' % repr(value))

    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values."""
        if not value:
            return []
        return [str(value.data)]

    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        if not values:
            return None
        if len(values) != 1:
            raise ValidationError("Incorrect Image value from LDAP: "
                                  "(%d-element list)" % len(values))
        return Image(self.getFieldId(), '', values[0])

InitializeClass(CPSImageField)

# Register field classes

FieldRegistry.register(CPSStringField)
FieldRegistry.register(CPSPasswordField)
FieldRegistry.register(CPSStringListField)
FieldRegistry.register(CPSIntField)
FieldRegistry.register(CPSLongField)
FieldRegistry.register(CPSFloatField)
FieldRegistry.register(CPSDateTimeField)
FieldRegistry.register(CPSFileField)
FieldRegistry.register(CPSImageField)
