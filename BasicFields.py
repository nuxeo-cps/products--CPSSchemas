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
from types import IntType, StringType, ListType, FloatType, LongType
from Globals import InitializeClass
from DateTime.DateTime import DateTime

from OFS.Image import cookId, File, Image

from Products.CMFCore.Expression import Expression

from Products.CPSSchemas.Field import CPSField, FieldRegistry
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

    default_expr = 'python:0'
    default_expr_c = Expression(default_expr)

    # XXX this is never called yet.
    def validate(self, value):
        if isinstance(value, IntType):
            return value
        raise ValidationError('Not an integer: %s' % repr(value))

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

InitializeClass(CPSStringField)

class CPSPasswordField(CPSField):
    """Password field."""
    meta_type = "CPS Password Field"

    default_expr = 'string:'
    default_expr_c = Expression(default_expr)

    # XXX this is never called yet.
    def validate(self, value):
        if isinstance(value, StringType):
            return value
        raise ValidationError('Not a string: %s' % repr(value))

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
