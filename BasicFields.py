# (C) Copyright 2003-2006 Nuxeo SAS <http://nuxeo.com>
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

from logging import getLogger

import sys
import warnings
import re
from Globals import InitializeClass
from DateTime.DateTime import DateTime

from OFS.Image import cookId, File, Image

from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName

from Products.CPSSchemas.Field import CPSField, FieldRegistry
from Products.CPSSchemas.Field import ValidationError
from Products.CPSSchemas.FileUtils import convertFileToHtml
from Products.CPSSchemas.FileUtils import convertFileToText
from Products.CPSSchemas.FileUtils import FileObjectFactory
from Products.CPSSchemas.DiskFile import DiskFile

from zope.interface import implements
from Products.CPSSchemas.interfaces import IFileField
from Products.CPSSchemas.interfaces import IImageField
from Products.CPSSchemas.interfaces import IFieldNodeIO

from Products.CPSUtil.text import OLD_CPS_ENCODING

logger = getLogger(__name__)

#
# UTF-8
#

def toUTF8(s):
    if not isinstance(s, unicode):
        # GR all internal non ASCII strings must be unicode now
        s = unicode(s)
    return s.encode('utf-8')

def fromUTF8(s):
    try:
        return unicode(s, 'utf-8')
    except UnicodeError:
        logger.warning('convertFromLDAP: Problem recoding %r', s, exc_info=True)
        return s.decode('utf-8', 'replace')

class CPSIntField(CPSField):
    """Integer field."""
    meta_type = "CPS Int Field"

    implements(IFieldNodeIO)

    default_expr = 'python:0'
    default_expr_c = Expression(default_expr)

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

LDAP_FALSE = 'FALSE'
LDAP_TRUE = 'TRUE'

class CPSBooleanField(CPSField):
    """Boolean field."""
    meta_type = "CPS Boolean Field"

    implements(IFieldNodeIO)

    default_expr = 'python:False'
    default_expr_c = Expression(default_expr)

    def validate(self, value):
        """Accept booleans and None, meaning : not known."""
        if isinstance(value, bool) or value is None:
            return value
        raise ValidationError('Not a boolean: %s' % repr(value))

    @classmethod
    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values."""
        if value is None:
            # GR: evaluating to False means missing attribute
            # see LDAPBackingDirectory#convertDataToLDAP
            return
        return value and [LDAP_TRUE] or [LDAP_FALSE]

    @classmethod
    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        if len(values) != 1:
            raise ValueError
        v = values[0]

        if v == LDAP_FALSE:
            return False
        elif v == LDAP_TRUE:
            return True
        else:
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

    def validate(self, value):
        # None is accepted to represent a missing value
        if value is None or isinstance(value, float):
            return value
        raise ValidationError('Not a real number: %s' % repr(value))

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

    _properties = CPSField._properties + (
        dict(id="validate_none", mode="w", type="boolean",
             label="Accept None as a correct value"), )

    default_expr = 'string:'
    default_expr_c = Expression(default_expr)
    validate_none = False

    logger = getLogger(__name__)

    def validate(self, value):
        if value is None and self.validate_none:
            return value
        if isinstance(value, unicode):
            return value
        elif isinstance(value, basestring):
            try:
                unicode(value, OLD_CPS_ENCODING) # To be removed in CPS 3.5.2
            except UnicodeError:
                ValidationError('Invalid encoding: %s' % repr(value))
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
            self.logger.warning('convertFromLDAP: Multi-valued field, '
                                'cutting: %r', values)
            values = values[:1]
        return fromUTF8(values[0])

    def setNodeValue(self, node, value, context):
        """See IFieldNodeIO.
        """
        context.setNodeValue(node, value)

    def getNodeValue(self, node, context):
        """See IFieldNodeIO.
        """
        return context.getNodeValue(node)

InitializeClass(CPSStringField)


class CPSAsciiStringField(CPSField):
    """Ascii String field.


    The value is str, encoded with the 'ascii' codec, meaning that
    going from and to unicode without specifying any encoding is error-free.
    """
    meta_type = "CPS Ascii String Field"

    implements(IFieldNodeIO)

    _properties = CPSField._properties + (
        dict(id="validate_none", mode="w", type="boolean",
             label="Accept None as a correct value"),
        )

    default_expr = 'string:'
    default_expr_c = Expression(default_expr)
    validate_none = False

    logger = getLogger("CPSSchemas.BasicFields.CPSAsciiStringField")

    def validate(self, value):
        if value is None and self.validate_none:
            return value
        if isinstance(value, str):
            try:
                u = unicode(value, 'ascii')
                return value
            except UnicodeError:
                raise ValidationError('Not an ASCII string: %r' % value)
        elif isinstance(value, unicode):
            try:
                return str(value)
            except UnicodeError:
                raise ValidationError('Not an ASCII string: %r' % value)
        else:
            raise ValidationError('Not a string at all: %r' % value)

    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values."""
        if not value:
            return []
        return [value]

    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        if not values:
            return ''
        if len(values) != 1:
            self.logger.warning('convertFromLDAP: Multi-valued field, '
                                'cutting: %r', values)
        return values[0]

    def setNodeValue(self, node, value, context):
        """See IFieldNodeIO.
        """
        context.setNodeValue(node, value)

    def getNodeValue(self, node, context):
        """See IFieldNodeIO.
        """
        return str(context.getNodeValue(node))

InitializeClass(CPSAsciiStringField)


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

    def validate(self, value):
        is_list = isinstance(value, list)
        if is_list or isinstance(value, tuple):
            for v in value:
                if not self.verifyType(v):
                    raise ValidationError(self.validation_error_msg +
                                          repr(value) + "=>" + repr(v))
            # GR at the time of actually hooking this method, tuple
            # were not allowed. I guess the contract of this field
            # is that the dm value must be mutable. OTOH there are a few
            # datamodel writes with tuple arguments in the current CPSDefault
            # base profile. Therefore it is too risky to forbid tuples.
            # Here's the compromise:
            if not is_list:
                return list(value)

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

    logger = getLogger("CPSSchemas.BasicFields.CPSStringListField")

    def verifyType(self, value):
        """Verify the type of *one value( of the list
        """
        if isinstance(value, unicode):
            return True
        elif isinstance(value, basestring):
            try:
                unicode(value, OLD_CPS_ENCODING)
            except UnicodeError:
                return False
            return True
        return False

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
                self.logger.warning('convertFromLDAP: problem recoding %r', v)
                pass
            res.append(v)
        return res

    def setNodeValue(self, node, value, context):
        """See IFieldNodeIO.
        """
        for v in value:
            child = context.createStrictTextElement('e')
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
            res.append(v)
        return res

InitializeClass(CPSStringListField)

class CPSAsciiStringListField(CPSListField):
    """Ascii String List field."""
    meta_type = "CPS Ascii String List Field"

    implements(IFieldNodeIO)

    validation_error_msg = 'Not an ASCII string list: '

    logger = getLogger("CPSSchemas.BasicFields.CPSAsciiStringListField")

    element_validator = CPSAsciiStringField('validator')

    def verifyType(self, value):
        """Verify the type of one list value
        """
        self.element_validator.validate(value)
        return True

    def validate(self, values):
        CPSListField.validate(self, values)
        return [str(v) for v in values] # TODO refactor a bit verifyType etc.

    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values."""
        # Empty values are not allowed in LDAP
        return [v for v in value if v]

    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        res = []
        for v in values:
            try:
                u = unicode(v, 'ascii')
            except UnicodeError:
                self.logger.warning('convertFromLDAP: %r is not ASCII', v)
                pass
            res.append(v) # keep str
        return res

    def setNodeValue(self, node, value, context):
        """See IFieldNodeIO.
        """
        for v in value:
            child = context.createStrictTextElement('e')
            context.setNodeValue(child, v)
            node.appendChild(child)

    def getNodeValue(self, node, context):
        """See IFieldNodeIO.
        """
        res = []
        for child in node.childNodes:
            if child.nodeName != 'e':
                continue
            v = str(context.getNodeValue(child))
            res.append(v)
        return res

InitializeClass(CPSAsciiStringListField)

class CPSListListField(CPSListField):
    """List of List field.

    This doesn't give enough type information so is not really
    registered as a field type. This is an abstract base class.
    """
    meta_type = "CPS List List Field"

    validation_error_msg = 'Not a list of list: '

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
        return [self._toLDAPFormat(value)]

    @classmethod
    def _toLDAPFormat(self, value):
        """Does the actual conversion job, not the list wrapping."""

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
        return v

    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        if not values:
            return None
        try:
            if len(values) != 1:
                raise ValueError
            return self._fromLDAPFormat(values[0])
        except (ValueError, TypeError):
            raise ValidationError("Incorrect DateTime value from LDAP: %s" %
                                  `values`)

    @classmethod
    def _fromLDAPFormat(self, v):
            """Does the actual conversion job, not the list wrapping."""
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

class CPSDateTimeListField(CPSListField):
    """DateTime List field."""
    meta_type = "CPS DateTime List Field"

    implements(IFieldNodeIO)

    validation_error_msg = 'Not a list of DateTime objects: '

    logger = getLogger('.'.join((__name__, 'CPSDateTimeListField')))

    element_validator = CPSDateTimeField('validator')

    def verifyType(self, value):
        """Verify the type of one list value
        """
        self.element_validator.validate(value)
        return True

    def validate(self, values):
        CPSListField.validate(self, values)
        return [v for v in values]

    def convertToLDAP(self, values):
        """Convert a value to LDAP attribute values."""
        # Empty values are not allowed in LDAP
        return [CPSDateTimeField._toLDAPFormat(v) for v in values if v]

    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values."""
        return [CPSDateTimeField._fromLDAPFormat(v) for v in values]

    def setNodeValue(self, node, value, context):
        """See IFieldNodeIO.
        """
        for v in value:
            child = context.createStrictTextElement('e')
            context.setNodeValue(
                child, v and CPSDateTimeField._toLDAPFormat(v) or None)
            node.appendChild(child)

    def getNodeValue(self, node, context):
        """See IFieldNodeIO.
        """
        res = []
        for child in node.childNodes:
            if child.nodeName != 'e':
                continue
            v = CPSDateTimeField._fromLDAPFormat(context.getNodeValue(child))
            res.append(v)
        return res

InitializeClass(CPSDateTimeListField)

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


    def _getDependantFieldsBaseId(self):
        return re.sub(r'_f\d+$', '', self.getFieldId())

    def _getDependantFieldId(self, schemas, suffix):
        """Get a dependant field id described by the suffix.

        Takes flexible situation into account"""
        if not suffix:
            return None
        fid = self._getDependantFieldsBaseId() + suffix
        for schema in schemas:
            if schema.has_key(fid):
                return fid
        return None

    def _getAllDependantFieldIds(self):
        base_id = self._getDependantFieldsBaseId()
        suffixes = (self.suffix_html, self.suffix_text,
                    self.suffix_html_subfiles)
        return tuple(base_id + suffix for suffix in suffixes if suffix)

    def computeDependantFields(self, schemas, data, context=None):
        """Compute dependant fields.

        schemas is the list of schemas

        data is the dictionnary of the datamodel
        """
        field_id = self.getFieldId()
        file = data[field_id] # May be None.
        
        if file is None:
            return

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
                for k, v in subobjects_dict.items():
                    files_dict[k] = File(k, k, v)
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
FileObjectFactory.methods[CPSFileField.meta_type] = (File, {})

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

        In particular this method handles the conversion from File to DiskFile
        
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
                for k, v in subobjects_dict.items():
                    files_dict[k] = File(k, k, v)
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
FileObjectFactory.methods[CPSDiskFileField.meta_type] = (DiskFile, {})


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
        if value is None:
            # for leftover wrong values of default_expr (#1943)
            value = {}
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

    implements(IFieldNodeIO, IImageField)

    default_expr = 'nothing'
    default_expr_c = Expression(default_expr)

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
FileObjectFactory.methods[CPSImageField.meta_type] = (Image, {})

class CPSRangeListField(CPSListField):
    """Meta list Field"""
    meta_type = "CPS Range List Field"

    validation_error_msg = 'Not a range list: '

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
