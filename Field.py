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
from AccessControl import ClassSecurityInfo
from Persistence import Persistent

from Products.CMFCore.CMFCorePermissions import View, ManagePortal
from Products.CMFCore.utils import SimpleItemWithProperties


class ValidationError(ValueError):
    """Raised by a widget or a field when user input is incorrect."""
    pass


class Field(SimpleItemWithProperties):
    """Basic Field.

    A field is part of a schema and describes a type of data that
    can be stored.

    A field does not describe graphical rendering, it only hints
    at what is the preferred method for rendering.
    """

    security = ClassSecurityInfo()

    default = ''
    allow_none = 0
    is_indexed = 0
    #is_subschema = 0
    #is_multi_valued = 0
    #vocabulary = None
    #read_permission = 'View'
    #write_permission = 'Modify portal content'
    #append_permission = 'Modify portal content'

    def __init__(self, id, **kw):
        self.id = id
        if kw.has_key('default'):
            self.default = kw['default']
        if kw.has_key('allow_none'):
            self.allow_none = kw['allow_none']
        if kw.has_key('is_indexed'):
            self.is_indexed = kw['is_indexed']
        #if kw.has_key('is_subschema'):
        #    self.is_subschema = kw['is_subschema']
        #if kw.has_key('is_multi_valued'):
        #    self.is_multi_valued = kw['is_multi_valued']
        #if kw.has_key('vocabulary'):
        #    self.vocabulary = kw['vocabulary']
        #if kw.has_key('read_permission'):
        #    self.read_permission = kw['read_permission']
        #if kw.has_key('write_permission'):
        #    self.write_permission = kw['write_permission']

    security.declarePrivate('getDefault')
    def getDefault(self):
        """Get the default value for this field."""
        return self.default

    security.declarePrivate('computeDependantFields')
    def computeDependantFields(self, schema, data):
        """Compute dependant fields.

        Has access to the current schema, and may update the data from
        the datamodel.

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

    #
    # ZMI
    #

    _properties = (
        {'id': 'getFieldIdProperty', 'type': 'string', 'mode': '',
         'label': 'Id'},
        {'id': 'default', 'type': 'string', 'mode': 'w',
         'label': 'Default'},
        {'id': 'allow_none', 'type': 'boolean', 'mode': 'w',
         'label': 'Allow None'},
        {'id': 'is_indexed', 'type': 'boolean', 'mode': 'w',
         'label': 'Is Indexed'},
        #{'id': 'is_subschema', 'type': 'boolean', 'mode': 'w',
        # 'label': 'Is Subschema'},
        #{'id': 'is_multi_valued', 'type': 'boolean', 'mode': 'w',
        # 'label': 'Is Multi-Valued'},
        #{'id': 'vocabulary', 'type': 'string', 'mode': 'w',
        # 'label': 'Vocabulary'},
        #{'id': 'read_permission', 'type': 'string', 'mode': 'w',
        # 'label': 'Read Permission'},
        #{'id': 'write_permission', 'type': 'string', 'mode': 'w',
        # 'label': 'Write Permission'},
        )

    def _getFieldIdMethod(self):
        return self.getFieldId()
    getFieldIdProperty = ComputedAttribute(_getFieldIdMethod, 1)

    manage_options = (
#        {'label': 'Field',
#         'action': 'manage_editField',
#         },
        ) + SimpleItemWithProperties.manage_options

#    security.declareProtected(ManagePortal, 'manage_editField')
#    manage_editField = DTMLFile('zmi/field_editform', globals())

#    security.declareProtected(ManagePortal, 'manage_main')
#    manage_main = manage_propertiesForm

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
