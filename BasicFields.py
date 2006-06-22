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
import warnings
from Globals import InitializeClass
from DateTime.DateTime import DateTime

from OFS.Image import cookId, File, Image

from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName

from Products.CPSSchemas.Field import CPSField, FieldRegistry
from Products.CPSSchemas.Field import ValidationError
from Products.CPSSchemas.FileUtils import convertFileToHtml
from Products.CPSSchemas.FileUtils import convertFileToText
from Products.CPSSchemas.DiskFile import DiskFile

from zope.interface import implements
from Products.CPSSchemas.interfaces import IFileField
from Products.CPSSchemas.interfaces import IFieldNodeIO


def _isinstance(ob, cls):
    warnings.warn("_isinstance() is deprecated and will be removed in "
                  "CPS 3.4.1. Use isinstance() instead.",
                  DeprecationWarning, stacklevel=2)
    return isinstance(ob, cls)

#
# UTF-8
#

default_encoding = sys.getdefaultencoding()
if default_encoding == 'ascii':
    default_encoding = 'iso-8859-15'

def toUTF8(s):
    if not isinstance(s, unicode):
        s = unicode(s, default_encoding)
    return s.encode('utf-8')

def fromUTF8(s):
    return unicode(s, 'utf-8').encode(default_encoding)


class CPSIntField(CPSField):
    """Integer field."""
    meta_type = "CPS Int Field"

    implements(IFieldNodeIO)

    default_expr = 'python:0'
    default_expr_c = Expression(default_expr)

    # XXX this is never called yet.
    def validate(self, value):
        if isinstance(value, int):
            return value
        if isinstance(value, bool):
            return int(value)
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

    def setNodeValue(self, node, value, context):
        """See IFieldNodeIO.
        """
        context.setNodeValue(node, str(int(value)))

    def getNodeValue(self, node, context):
        """See IFieldNodeIO.
        """
        text = context.getNodeValue(node)
        return int(text)

InitializeClass(CPSIntField)


class CPSBooleanField(CPSField):
    """Boolean field."""
    meta_type = "CPS Boolean Field"

    implements(IFieldNodeIO)

    default_expr = 'python:False'
    default_expr_c = Expression(default_expr)

    # XXX this is never called yet.
    def validate(self, value):
        if isinstance(value, bool):
            return value
        raise ValidationError('Not a boolean: %s' % repr(value))

    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values."""
        return [str(value)]

    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        try:
            if len(values) != 1:
                raise ValueError
            return bool(values[0])
        except (ValueError, TypeError):
            raise ValidationError("Incorrect Boolean value from LDAP: %s"
                                  % `values`)

    def setNodeValue(self, node, value, context):
        """See IFieldNodeIO.
        """
        context.setNodeValue(node, str(bool(value)))

    def getNodeValue(self, node, context):
        """See IFieldNodeIO.
        """
        text = context.getNodeValue(node)
        return context._convertToBoolean(text)

InitializeClass(CPSBooleanField)


class CPSLongField(CPSIntField):
    """Long field

    This field is DEPRECATED, use the identical Int Field instead.
    """
    meta_type = "CPS Long Field"
    def __init__(self, id, **kw):
        warnings.warn("The Long Field (%s) is deprecated and will be "
                      "removed in CPS 3.5.0. Use a Int Field instead" %
                      id, DeprecationWarning)
        CPSIntField.__init__(self, id, **kw)

InitializeClass(CPSLongField)


class CPSFloatField(CPSField):
    """Float field."""
    meta_type = "CPS Float Field"

    implements(IFieldNodeIO)

    default_expr = 'python:0.0'
    default_expr_c = Expression(default_expr)

    # XXX this is never called yet.
    def validate(self, value):
        if isinstance(value, float):
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

    def setNodeValue(self, node, value, context):
        """See IFieldNodeIO.
        """
        if value is None:
            value = ""
        else:
            value = str(value)
        context.setNodeValue(node, value)

    def getNodeValue(self, node, context):
        """See IFieldNodeIO.
        """
        text = context.getNodeValue(node)
        if text:
            return float(text)
        return None

InitializeClass(CPSFloatField)


class CPSStringField(CPSField):
    """String field."""
    meta_type = "CPS String Field"

    implements(IFieldNodeIO)

    default_expr = 'string:'
    default_expr_c = Expression(default_expr)

    # XXX this is never called yet.
    def validate(self, value):
        if isinstance(value, str):
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

    def setNodeValue(self, node, value, context):
        """See IFieldNodeIO.
        """
        context.setNodeValue(node, str(value).decode(default_encoding))

    def getNodeValue(self, node, context):
        """See IFieldNodeIO.
        """
        text = context.getNodeValue(node)
        return text.encode(default_encoding)

InitializeClass(CPSStringField)


class CPSPasswordField(CPSStringField):
    """Password field."""
    meta_type = "CPS Password Field"

InitializeClass(CPSPasswordField)


class CPSListField(CPSField):
    """Meta list Field"""
    meta_type = "CPS List Field"

    default_expr = 'python:[]'
    default_expr_c = Expression(default_expr)
    validation_error_msg = 'Not a list: '

    # XXX this is never called yet.
    def validate(self, value):
        if isinstance(value, list):
            for v in value:
                if not self.verifyType(v):
                    raise ValidationError(self.validation_error_msg +
                                          repr(value) + "=>" + repr(v))
            return value
        raise ValidationError(self.validation_error_msg + repr(value))

    def verifyType(self, value):
        """Verify the type of the value"""
        return 1

    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values."""
        # Empty values are not allowed in LDAP
        return value

    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        res = []
        for v in values:
            res.append(v)
        return res

InitializeClass(CPSListField)


class CPSStringListField(CPSListField):
    """String List field."""
    meta_type = "CPS String List Field"

    implements(IFieldNodeIO)

    validation_error_msg = 'Not a string list: '

    def verifyType(self, value):
        """Verify the type of the value"""
        return isinstance(value, str)

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

    def setNodeValue(self, node, value, context):
        """See IFieldNodeIO.
        """
        for v in value:
            child = context.createStrictTextElement('e')
            v = v.decode(default_encoding)
            context.setNodeValue(child, v)
            node.appendChild(child)

    def getNodeValue(self, node, context):
        """See IFieldNodeIO.
        """
        res = []
        for child in node.childNodes:
            if child.nodeName != 'e':
                continue
            v = context.getNodeValue(child)
            v = v.encode(default_encoding)
            res.append(v)
        return res

InitializeClass(CPSStringListField)

class CPSListListField(CPSListField):
    """List of List field.

    This doesn't give enough type information so is not really
    registered as a field type. This is an abstract base class.
    """
    meta_type = "CPS List List Field"

    validation_error_msg = 'Not a list of list: '

    # XXX this is never called yet.
    def validate(self, value):
        if isinstance(value, list):
            for l in value:
                if isinstance(l, list):
                    for e in l:
                        if not self.verifyType(e):
                            raise ValidationError(self.validation_error_msg +
                                            repr(value) + '=>' + repr(e))
                else:
                    raise ValidationError(self.validation_error_msg +
                                          repr(value) + '=>' + repr(l))
            return value
        raise ValidationError(self.validation_error_msg + repr(value))

    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values."""
        # Empty values are not allowed in LDAP
        if value:
            return value

    def convertFromLDAP(self, value):
        """Convert a value from LDAP attribute values."""
        return value

InitializeClass(CPSListListField)

class CPSIntListListField(CPSListListField):
    """List of List field."""
    meta_type = "CPS Int List List Field"

    validation_error_msg = 'Not a list of integer list: '

    def verifyType(self, value):
        """Verify the type of the value"""
        return isinstance(value, int)

InitializeClass(CPSIntListListField)

class CPSDateTimeField(CPSField):
    """DateTime field."""
    meta_type = "CPS DateTime Field"

    implements(IFieldNodeIO)

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

    def setNodeValue(self, node, value, context):
        """See IFieldNodeIO.
        """
        v = self.convertToLDAP(value)
        if v:
            v = v[0]
        else:
            v = ''
        context.setNodeValue(node, v)

    def getNodeValue(self, node, context):
        """See IFieldNodeIO.
        """
        v = context.getNodeValue(node)
        if v:
            value = self.convertFromLDAP([v])
        else:
            value = None
        return value

InitializeClass(CPSDateTimeField)


class CPSFileField(CPSField):
    """File field."""
    meta_type = "CPS File Field"

    implements(IFieldNodeIO, IFileField)

    default_expr = 'nothing'
    default_expr_c = Expression(default_expr)

    _properties = CPSField._properties + (
        {'id': 'suffix_text', 'type': 'string', 'mode': 'w',
         'label': 'Suffix for field containing Text conversion'},
        {'id': 'suffix_html', 'type': 'string', 'mode': 'w',
         'label': 'Suffix for field containing HTML conversion'},
        {'id': 'suffix_html_subfiles', 'type': 'string', 'mode': 'w',
         'label': 'Suffix for field containing HTML conversion subobjects'},
        )
    suffix_text = ''
    suffix_html = ''
    suffix_html_subfiles = ''

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
        """Compute dependant fields.

        schemas is the list of schemas

        data is the dictionnary of the datamodel
        """
        field_id = self.getFieldId()
        file = data[field_id] # May be None.

        text_field_id = self._getDependantFieldId(schemas, self.suffix_text)
        if text_field_id is not None:
            data[text_field_id] = convertFileToText(file, context=context)

        html_field_id = self._getDependantFieldId(schemas, self.suffix_html)
        html_subfiles_field_id = self._getDependantFieldId(
            schemas,
            self.suffix_html_subfiles)
        if html_field_id is not None:
            html_conversion = convertFileToHtml(file, context=context)
            if html_conversion is not None:
                html_string = html_conversion.getData()
                fileid = cookId('', '', file)[0]
                if '.' in fileid:
                    fileid = fileid[:fileid.rfind('.')]
                if not fileid:
                    fileid = 'document'
                fileid = fileid + '.html'
                html_file = File(fileid, '', html_string,
                                 content_type='text/html')

                # getSubObjects returns a dict of sub-objects, each sub-object
                # being a file but described as a string.
                subobjects_dict = html_conversion.getSubObjects()
                files_dict = {}
                #LOG('BasicFields', DEBUG, "subobjects = %s" % `subobjects_dict`)
                for k, v in subobjects_dict.items():
                    files_dict[k] = File(k, k, v)
                #LOG('BasicFields', DEBUG, "files_dict = %s" % `files_dict`)
            else:
                html_file = None
                files_dict = {}
            data[html_field_id] = html_file
            data[html_subfiles_field_id] = files_dict

    # XXX this is never called yet.
    def validate(self, value):
        if not value:
            return None
        if isinstance(value, File):
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

    def setNodeValue(self, node, value, context):
        """See IFieldNodeIO.
        """
        return

    def getNodeValue(self, node, context):
        """See IFieldNodeIO.
        """
        # Will be later initialized as a subobject.
        return None

InitializeClass(CPSFileField)

class CPSDiskFileField(CPSFileField):
    """File field."""
    meta_type = "CPS Disk File Field"

    _properties = CPSFileField._properties + (
        {'id': 'disk_storage_path', 'type': 'string', 'mode': 'w',
         'label': 'Storage path'},
        )
    disk_storage_path = ''

    def getStoragePath(self):
        if self.disk_storage_path:
            return self.disk_storage_path
        else:
            portal_schemas = getToolByName(self, 'portal_schemas')
            storage_path = getattr(portal_schemas, 'disk_storage_path', '')
            if storage_path:
                return storage_path
            return 'var/files'

    def computeDependantFields(self, schemas, data, context=None):
        """Compute dependant fields.

        schemas is the list of schemas

        data is the dictionnary of the datamodel
        """
        field_id = self.getFieldId()
        file = data[field_id] # May be None.
        if isinstance(file, File) and not isinstance(file, DiskFile):
            file = DiskFile(file.getId(), file.title, file.data,
                            file.content_type, self.getStoragePath())
            data[field_id] = file
        text_field_id = self._getDependantFieldId(schemas, self.suffix_text)
        if text_field_id is not None:
            data[text_field_id] = convertFileToText(file, context=context)

        html_field_id = self._getDependantFieldId(schemas, self.suffix_html)
        html_subfiles_field_id = self._getDependantFieldId(
            schemas,
            self.suffix_html_subfiles)
        if html_field_id is not None:
            html_conversion = convertFileToHtml(file, context=context)
            if html_conversion is not None:
                html_string = html_conversion.getData()
                fileid = cookId('', '', file)[0]
                if '.' in fileid:
                    fileid = fileid[:fileid.rfind('.')]
                if not fileid:
                    fileid = 'document'
                fileid = fileid + '.html'
                html_file = File(fileid, '', html_string,
                                 content_type='text/html')

                # getSubObjects returns a dict of sub-objects, each sub-object
                # being a file but described as a string.
                subobjects_dict = html_conversion.getSubObjects()
                files_dict = {}
                #LOG('BasicFields', DEBUG, "subobjects = %s" % `subobjects_dict`)
                for k, v in subobjects_dict.items():
                    files_dict[k] = File(k, k, v)
                #LOG('BasicFields', DEBUG, "files_dict = %s" % `files_dict`)
            else:
                html_file = None
                files_dict = {}
            data[html_field_id] = html_file
            data[html_subfiles_field_id] = files_dict

    def validate(self, value):
        if not value:
            return None
        if isinstance(value, File):
            return value
        raise ValidationError('Not a file: %s' % repr(value))

    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values."""
        raise TypeError("DiskFile does not yet support LDAP directories")
#         if not value:
#             return []
#         return [str(value)]

    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        raise TypeError("DiskFile does not yet support LDAP directories")
#         if not values:
#             return None
#         if len(values) != 1:
#             raise ValidationError("Incorrect File value from LDAP: "
#                                   "(%d-element list)" % len(values))
#         return File(self.getFieldId(), '', values[0])

InitializeClass(CPSDiskFileField)


class CPSSubObjectsField(CPSField):
    """Sub-objects field."""
    meta_type = "CPS SubObjects Field"

    default_expr = 'python:{}'
    default_expr_c = Expression(default_expr)

    def getFromAttribute(self, ob, field_id):
        value = {}
        for k in getattr(ob, field_id, ()):
            if k.startswith('_'):
                continue
            value[k] = getattr(ob, k, None)
        return value

    def setAsAttribute(self, ob, field_id, value):
        for k in getattr(ob, field_id, ()):
            if k.startswith('_'):
                continue
            try:
                delattr(ob, k)
            except (AttributeError, KeyError):
                pass
        setattr(ob, field_id, tuple(value.keys()))
        for k, v in value.items():
            if k.startswith('_'):
                continue
            setattr(ob, k, v)

    # XXX this is never called yet.
    def validate(self, value):
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        raise ValidationError('Not SubObjects: %s' % repr(value))


InitializeClass(CPSSubObjectsField)


class CPSImageField(CPSField):
    """Image field."""
    meta_type = "CPS Image Field"

    implements(IFieldNodeIO, IFileField)

    default_expr = 'nothing'
    default_expr_c = Expression(default_expr)

    # XXX this is never called yet.
    def validate(self, value):
        if not value:
            return None
        if isinstance(value, Image):
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

    def setNodeValue(self, node, value, context):
        """See IFieldNodeIO.
        """
        return

    def getNodeValue(self, node, context):
        """See IFieldNodeIO.
        """
        # Will be later initialized as a subobject.
        return None

InitializeClass(CPSImageField)

class CPSRangeListField(CPSListField):
    """Meta list Field"""
    meta_type = "CPS Range List Field"

    validation_error_msg = 'Not a range list: '

    # XXX this is never called yet.
    def validate(self, value):
        if isinstance(value, list):
            for v in value:
                if not isinstance(v, tuple):
                    raise ValidationError(self.validation_error_msg +
                                          "%s is not a tuple in %s" %
                                          (repr(v),
                                           repr(value)))
                if len(v) not in (1, 2):
                    raise ValidationError(self.validation_error_msg +
                                          "bad length for %s in %s" %
                                          (repr(v),
                                           repr(value)))
                for e in v:
                    if not self.verifyType(e):
                        raise ValidationError(self.validation_error_msg +
                                              "%s is not an integer in %s" %
                                              (repr(e),
                                               repr(value)))
            return value
        raise ValidationError(self.validation_error_msg + repr(value))

    def verifyType(self, value):
        """Verify the type of the value"""
        return isinstance(value, int)

InitializeClass(CPSRangeListField)

class CPSCoupleField(CPSListField):
    """CPS Couple Field

    Holds two non-negative integers within a list. The order matters.

    XXX should be relaxed to allow a tuple (safer), see CPSPortlets.
    """
    meta_type = "CPS Couple Field"

    implements(IFieldNodeIO)

    validation_error_message = "Not a couple : "

    def _getValidationErrorMessage(self, value):
        return self.validation_error_message + repr(value)

    # XXX not called yet but should be done...
    def validate(self, value):
        """Validate the value

        Has to be a list of 2 integer values within a list
        """

        if (isinstance(value, list) and
            len(value) == 2):
            return value

        # Default case
        elif (isinstance(value, list) and
              len(value) == 0):
            return value

        raise ValidationError(self._getValidationErrorMessage(value))

    def setNodeValue(self, node, value, context):
        """See IFieldNodeIO.
        """
        context.setNodeValue(node, '%d-%d' % (value[0], value[1]))

    def getNodeValue(self, node, context):
        """See IFieldNodeIO.
        """
        text = context.getNodeValue(node)
        v0, v1 = text.split('-', 1)
        return [int(v0), int(v1)]

InitializeClass(CPSCoupleField)



# Register field classes

FieldRegistry.register(CPSBooleanField)
FieldRegistry.register(CPSStringField)
FieldRegistry.register(CPSPasswordField)
#FieldRegistry.register(CPSListListField) # Not registered on purpose
FieldRegistry.register(CPSIntListListField)
FieldRegistry.register(CPSStringListField)
FieldRegistry.register(CPSIntField)
FieldRegistry.register(CPSLongField) # deprecated
FieldRegistry.register(CPSFloatField)
FieldRegistry.register(CPSDateTimeField)
FieldRegistry.register(CPSFileField)
FieldRegistry.register(CPSDiskFileField)
FieldRegistry.register(CPSSubObjectsField)
FieldRegistry.register(CPSImageField)
FieldRegistry.register(CPSRangeListField)
FieldRegistry.register(CPSCoupleField)
