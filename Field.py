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
"""Field

Base classes for fields, the individual parts of a schema.
"""

from zLOG import LOG, DEBUG
from copy import deepcopy
from ComputedAttribute import ComputedAttribute
from Globals import InitializeClass, DTMLFile
from DateTime.DateTime import DateTime

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from AccessControl.PermissionRole import rolesForPermissionOn

from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import getEngine
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.utils import getToolByName

from Products.CPSSchemas.PropertiesPostProcessor import PropertiesPostProcessor


class AccessError(ValueError):
    """Raised by a field when access is denied."""
    def __init__(self, field, message=''):
        self.field = field
        self.message = message
    def __str__(self):
        s = "%s access to %s denied" % (self.type, self.field)
        if self.message:
            s += " ("+self.message+") "
        return s

class ReadAccessError(AccessError):
    type = "Read"

class WriteAccessError(AccessError):
    type = "Write"

class ValidationError(ValueError):
    """Raised by a widget or a field when user input is incorrect."""
    pass


class Field(PropertiesPostProcessor, SimpleItemWithProperties):
    """Basic Field.

    A field is part of a schema and describes a type of data that
    can be stored.

    A field does not describe graphical rendering, it only hints
    at what is the preferred method for rendering.
    """

    security = ClassSecurityInfo()

    _propertiesBaseClass = SimpleItemWithProperties
    _properties = (
        {'id': 'getFieldIdProperty', 'type': 'string', 'mode': '',
         'label': "Id"},
        {'id': 'default_expr', 'type': 'string', 'mode': 'w',
         'label': "Default value expression"},
        {'id': 'is_searchabletext', 'type': 'boolean', 'mode': 'w',
         'label': "Indexed by SearchableText"},
        {'id': 'acl_read_permissions', 'type': 'string', 'mode': 'w',
         'label': "ACL: read permissions"},
        {'id': 'acl_read_roles', 'type': 'string', 'mode': 'w',
         'label': "ACL: read roles"},
        {'id': 'acl_read_expr', 'type': 'string', 'mode': 'w',
         'label': "ACL: read expression"},
        {'id': 'acl_write_permissions', 'type': 'string', 'mode': 'w',
         'label': "ACL: write permission"},
        {'id': 'acl_write_roles', 'type': 'string', 'mode': 'w',
         'label': "ACL: write roles"},
        {'id': 'acl_write_expr', 'type': 'string', 'mode': 'w',
         'label': "ACL: write expression"},
        #{'id': 'is_subschema', 'type': 'boolean', 'mode': 'w',
        # 'label': 'Is Subschema'},
        #{'id': 'is_multi_valued', 'type': 'boolean', 'mode': 'w',
        # 'label': 'Is Multi-Valued'},
        #{'id': 'vocabulary', 'type': 'string', 'mode': 'w',
        # 'label': 'Vocabulary'},
        {'id': 'read_ignore_storage', 'type': 'boolean', 'mode': 'w',
         'label': "Read: ignore storage"},
        {'id': 'read_process_expr', 'type': 'string', 'mode': 'w',
         'label': "Read: expression"},
        {'id': 'read_process_dependent_fields', 'type': 'tokens', 'mode': 'w',
         'label': "Read: expression dependent fields"},
        {'id': 'write_ignore_storage', 'type': 'boolean', 'mode': 'w',
         'label': "Write: ignore storage"},
        {'id': 'write_process_expr', 'type': 'string', 'mode': 'w',
         'label': "Write: expression"},
        )

    default_expr = 'string:'
    is_searchabletext = 0
    acl_read_permissions = ''
    acl_read_roles = ''
    acl_read_expr = ''
    acl_write_permissions = ''
    acl_write_roles = ''
    acl_write_expr = ''
    #is_subschema = 0
    #is_multi_valued = 0
    #vocabulary = None
    read_ignore_storage = 0
    read_process_expr = ''
    read_process_dependent_fields = []
    write_ignore_storage = 0
    write_process_expr = ''

    default_expr_c = Expression(default_expr)
    acl_read_permissions_c = []
    acl_read_roles_c = []
    acl_read_expr_c = None
    acl_write_permissions_c = []
    acl_write_roles_c = []
    acl_write_expr_c = None
    read_process_expr_c = None
    write_process_expr_c = None

    _properties_post_process_split = (
        ('acl_read_permissions', 'acl_read_permissions_c', ',;'),
        ('acl_read_roles', 'acl_read_roles_c', ',; '),
        ('acl_write_permissions', 'acl_write_permissions_c', ',;'),
        ('acl_write_roles', 'acl_write_roles_c', ',; '),
        )

    _properties_post_process_tales = (
        ('default_expr', 'default_expr_c'),
        ('acl_read_expr', 'acl_read_expr_c'),
        ('acl_write_expr', 'acl_write_expr_c'),
        ('read_process_expr', 'read_process_expr_c'),
        ('write_process_expr', 'write_process_expr_c'),
        )

    def __init__(self, id, **kw):
        self.id = id
        self.manage_changeProperties(**kw)

    security.declarePrivate('getDefault')
    def getDefault(self):
        """Get the default value for this field."""
        if not self.default_expr_c:
            return None
        expr_context = self._createDefaultExpressionContext()
        return self.default_expr_c(expr_context)

    def _createDefaultExpressionContext(self):
        """Create an expression context for default value evaluation."""
        mapping = {
            'field': self,
            'user': getSecurityManager().getUser(),
            'portal': getToolByName(self, 'portal_url').getPortalObject(),
            'DateTime': DateTime,
            'nothing': None,
            }
        return getEngine().getContext(mapping)

    security.declarePrivate('computeDependantFields')
    def computeDependantFields(self, schemas, data, context=None):
        """Compute dependant fields.

        Has access to the current schemas, and may update the data from
        the datamodel.

        The context argument is passed to look for placeful information.

        This is used for fields that update other fields when they are
        themselves updated.
        """
        pass

    security.declarePublic('getFieldId')
    def getFieldId(self):
        """Get this field's id."""
        id = self.getId()
        if hasattr(self, 'getIdUnprefixed'):
            # Inside a FolderWithPrefixedIds.
            return self.getIdUnprefixed(id)
        else:
            # Standalone field.
            return id

    getFieldIdProperty = ComputedAttribute(getFieldId, 1)

    #
    # Import/export
    #
    def _exportValue(self, value):
        """Export this field's value as a string.

        Returns the string and a dict with any info needed if it makes
        sense and will be needed for import.

        Called by the datamodel during export.
        """
        # Default implementation suitable for simple fields.
        if value is None:
            return '', {'none': 'true'}
        else:
            return str(value), {}

    def _importValue(self, svalue, info):
        """Import field value.

        Returns a value.

        Receives a string and additional info as arguments.
        """
        # TODO
        if info and info['none'] == 'true':
            return None
        raise NotImplementedError

    #
    # Storage interaction
    #
    def _createStorageExpressionContext(self, value, data):
        """Create an expression context for field storage process."""
        # Put all the names in the data in the namespace.
        mapping = data.copy()
        mapping.update({
            'value': value,
            'data': data,
            'field': self,
            'user': getSecurityManager().getUser(),
            'portal': getToolByName(self, 'portal_url').getPortalObject(),
            'DateTime': DateTime,
            'nothing': None,
            })
        return getEngine().getContext(mapping)

    security.declarePrivate('processValueAfterRead')
    def processValueAfterRead(self, value, data):
        """Process value after read from storage."""
        if not self.read_process_expr_c:
            return value
        expr_context = self._createStorageExpressionContext(value, data)
        return self.read_process_expr_c(expr_context)

    security.declarePrivate('processValueBeforeWrite')
    def processValueBeforeWrite(self, value, data):
        """Process value before write to storage."""
        if not self.write_process_expr_c:
            return value
        expr_context = self._createStorageExpressionContext(value, data)
        return self.write_process_expr_c(expr_context)

    #
    # ACLs
    #
    def _createAclExpressionContext(self, datamodel):
        """Create an expression context for ACL evaluation."""
        context = datamodel._context
        mapping = {
            'field': self,
            'datamodel': datamodel,
            'user': datamodel._acl_cache_user,
            'roles': datamodel._acl_cache_user_roles,
            'nothing': None,
            # Useful for objects
            'context': context,
            'proxy': datamodel._proxy,
            # Useful for directories
            'dir': context,
            }
        return getEngine().getContext(mapping)

    def _checkAccess(self, datamodel, context,
                     acl_permissions, acl_roles, acl_expr_c,
                     exception,
                     StringType=type('')):
        """Check that field can be accesed.

        Raises an exception if not.

        The datamodel is used to cache often used things.
        """
        user = datamodel._acl_cache_user
        if acl_permissions:
            perms_cache = datamodel._acl_cache_permissions
            ok = 0
            for perm in acl_permissions:
                ok = perms_cache.get(perm)
                if ok is None:
                    roles = rolesForPermissionOn(perm, context)
                    if type(roles) is StringType:
                        roles = [roles]
                    ok = user.allowed(context, roles)
                    perms_cache[perm] = ok
                if ok:
                    break
            if not ok:
                raise exception(self.getFieldId(), 'permissions')
        if acl_roles:
            user_roles = datamodel._acl_cache_user_roles
            ok = 0
            for role in acl_roles:
                if role in user_roles:
                    ok = 1
                    break
            if not ok:
                raise exception(self.getFieldId(), 'roles')
        if acl_expr_c:
            expr_context = self._createAclExpressionContext(datamodel)
            if not acl_expr_c(expr_context):
                raise exception(self.getFieldId(), 'expression')

    def checkReadAccess(self, datamodel, context):
        """Check that field can be read.

        Raises an exception if not.

        The datamodel is used to cache often used things.
        """
        self._checkAccess(datamodel, context,
                          self.acl_read_permissions_c, self.acl_read_roles_c,
                          self.acl_read_expr_c, ReadAccessError)

    def checkWriteAccess(self, datamodel, context):
        """Check that field can be written.

        Raises an exception if not.
        """
        self._checkAccess(datamodel, context,
                          self.acl_write_permissions_c, self.acl_write_roles_c,
                          self.acl_write_expr_c, WriteAccessError)

    #
    # Validation
    #

    # XXX this is never called yet.
    security.declarePublic('validate')
    def validate(self, value):
        """Validate a value."""
        raise NotImplementedError

InitializeClass(Field)


class CPSField(Field):
    """Persistent Field."""

    meta_type = "CPS Field"

    security = ClassSecurityInfo()
    security.declareObjectProtected(View) # XXX correct ?

InitializeClass(CPSField)


addCPSFieldForm = DTMLFile('zmi/field_addform', globals())

def addCPSField(container, id, REQUEST=None):
    """Add a CPS Field."""
    ob = CPSField(id)
    container._setObject(id, ob)
    ob = container._getOb(id)
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(ob.absolute_url() + "/manage_main")


def propertiesWithType(properties, id, type):
    properties = deepcopy(properties)
    for prop in properties:
        if prop['id'] == id:
            prop['type'] = type
    return properties


class FieldRegistry:
    """Registry of the available field types."""

    def __init__(self):
        self._field_types = []
        self._field_classes = {}

    def register(self, cls):
        """Register a class for a field."""
        field_type = cls.meta_type
        self._field_types.append(field_type)
        self._field_classes[field_type] = cls

    def listFieldTypes(self):
        """Return the list of field types."""
        return self._field_types[:]

    def makeField(self, field_type, id, **kw):
        """Factory to make a field of the given type."""
        try:
            cls = self._field_classes[field_type]
        except KeyError:
            raise KeyError("No field type '%s'" % field_type)
        return cls(id, **kw)

# Singleton
FieldRegistry = FieldRegistry()
