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
from Products.CMFCore.Expression import SecureModuleImporter
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.utils import getToolByName

from Products.CPSUtil.PropertiesPostProcessor import PropertiesPostProcessor
from Products.CPSSchemas.DataModel import DEFAULT_VALUE_MARKER
from Products.CPSSchemas.DataModel import ReadAccessError
from Products.CPSSchemas.DataModel import WriteAccessError
from Products.CPSSchemas.DataModel import ValidationError # used by cpsdir
from Products.CPSSchemas.FieldNamespace import fieldStorageNamespace

from zope.interface import implements
from zope.interface import implementedBy
from Products.CPSSchemas.interfaces import IField


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
        {'id': 'write_process_dependent_fields', 'type': 'tokens', 'mode': 'w',
         'label': "Write: expression dependent fields"},
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
    read_process_dependent_fields = ()
    write_ignore_storage = 0
    write_process_expr = ''
    # BBB, remove in CPS 3.5 (this is used only if there is a write expr)
    write_process_dependent_fields = ('*',)

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
    def getDefault(self, datamodel=None):
        """Get the default value for this field."""
        if not self.default_expr_c:
            return None
        expr_context = self._createDefaultExpressionContext(datamodel)
        __traceback_info__ = self.default_expr
        return self.default_expr_c(expr_context)

    def _createDefaultExpressionContext(self, datamodel):
        """Create an expression context for default value evaluation."""

        portal = getToolByName(self, 'portal_url').getPortalObject()
        util = fieldStorageNamespace.__of__(portal)
        mapping = {
            'field': self,
            'datamodel': datamodel,
            'user': getSecurityManager().getUser(),
            'portal': portal,
            'modules': SecureModuleImporter,
            'DateTime': DateTime,
            'nothing': None,
            'util': util,
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

    security.declarePrivate('getDependantFieldsIds')
    def _getAllDependantFieldIds(self):
        """Provides the list of all *possible* dependent fields.

        If in this list, a field will be considered as dependent. This doesn't
        mean that all the fields from the list do exist.

        This is useful for exporters to avoid exporting dependent fields.
        """

        return ()

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
    def _createStorageExpressionContext(self, value, data, context, proxy):
        """Create an expression context for field storage process."""
        # Put all the names in the data in the namespace.
        mapping = data.copy() # XXX there may be DEFAULT_VALUE_MARKER here
        # XXX hack replace DEFAULT_VALUE_MARKER
        for k, v in mapping.items():
            if v is DEFAULT_VALUE_MARKER:
                mapping[k] = '' # XXX should be field's default
        portal = getToolByName(self, "portal_url").getPortalObject()
        # Wrapping util in the current acquisition context
        util = fieldStorageNamespace.__of__(portal)
        mapping.update({
            'value': value,
            'data': data,
            'field': self,
            'user': getSecurityManager().getUser(),
            'portal': portal,
            'modules': SecureModuleImporter,
            'DateTime': DateTime,
            'nothing': None,
            # Useful for objects
            'object': context,
            'proxy': proxy,
            # Deprecated: use the 'object' name instead
            'context': context,
            # Methods registry
            'util': util,
            })
        return getEngine().getContext(mapping)

    security.declarePrivate('processValueAfterRead')
    def processValueAfterRead(self, value, data, context, proxy):
        """Process value after read from storage."""
        if not self.read_process_expr_c:
            return value
        expr_context = self._createStorageExpressionContext(value, data,
                                                            context, proxy)
        __traceback_info__ = self.read_process_expr
        return self.read_process_expr_c(expr_context)

    security.declarePrivate('processValueBeforeWrite')
    def processValueBeforeWrite(self, value, data, context, proxy):
        """Process value before write to storage."""
        if not self.write_process_expr_c:
            return value
        expr_context = self._createStorageExpressionContext(value, data,
                                                            context, proxy)
        __traceback_info__ = self.write_process_expr
        return self.write_process_expr_c(expr_context)

    #
    # ACLs
    #
    def _createAclExpressionContext(self, datamodel):
        """Create an expression context for ACL evaluation."""
        context = datamodel.getContext()
        mapping = {
            'field': self,
            'datamodel': datamodel,
            'user': datamodel._acl_cache_user,
            'roles': datamodel._acl_cache_user_roles,
            'nothing': None,
            # Useful for objects
            'context': context,
            'proxy': datamodel.getProxy(),
            # Useful for directories
            'dir': context,
            }
        return getEngine().getContext(mapping)

    def _checkAccess(self, datamodel, context,
                     acl_permissions, acl_roles, acl_expr_c,
                     exception):
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
                    if isinstance(roles, str):
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

    # Conversion

    security.declarePublic('convertToLDAP')
    def convertToLDAP(self, value):
        """Convert a value to LDAP attribute values.

        Returns a list of strings.
        """
        raise NotImplementedError

    security.declarePublic('convertFromLDAP')
    def convertFromLDAP(self, values):
        """Convert a value from LDAP attribute values.

        Returns the converted value or raises an error.
        """
        raise NotImplementedError

InitializeClass(Field)


class CPSField(Field):
    """CPS Field."""

    implements(IField)

    meta_type = "CPS Field"

    security = ClassSecurityInfo()
    security.declareObjectProtected(View) # XXX correct ?

    #
    # ZMI
    #

    manage_options = SimpleItemWithProperties.manage_options + (
        {'label': 'Export',
         'action': 'manage_genericSetupExport.html',
         },
        )

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
        if field_type in self._field_types:
            return
        # Avoid duplicate registrations during convoluted imports
        # GR TODO: test if that's ok with ZCML override logic
        self._field_types.append(field_type)
        self._field_classes[field_type] = cls

        # Five-like registration, will move to ZCML later
        import Products
        info = {'name': cls.meta_type,
                'action': '', # addview and ('+/%s' % addview) or '',
                'product': 'CPSSchemas', # Five
                'permission': ManagePortal,
                'visibility': None,
                'interfaces': tuple(implementedBy(cls)),
                'instance': cls,
                'container_filter': None}
        Products.meta_types += (info,)

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

# ZCML handler
def register_field_class(_context, class_):
    meta_type = class_.meta_type
    _context.action(discriminator=('Field', meta_type,),
                    callable=FieldRegistry.register,
                    args=(class_,))

