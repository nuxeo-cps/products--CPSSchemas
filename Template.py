# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

import inspect

from ZODB.PersistentMapping import PersistentMapping

from Products.CPSDocument.Layout import HtmlLayout
from Products.CPSDocument.Schema import Schema
from Products.CPSDocument.DataModel import DataModel
from Products.CPSDocument.OrderedDictionary import OrderedDictionary


# Global Validation methods
# Validation methods take two arguments, the template_layout to validate against,
# and the document layout to validate. It should return the reason why the
# validation failed, or if the validation succeded, it should return None.
def _flexibleValidationMethod(template_layout, document_layout):
    """Used with flexible layouts, always returns None"""
    return None

def _fixedValidationMethod(template_layout, document_layout):
    """Used with fixed validations"""
    if template_layout is document_layout:
        return None #They are not just equal, but the same!
    return "The documents Layout is not the same as the templates Layout"

_fixed_validation = 'fixed_validation_marker'


class Template:
    """Defines the behaviour of a document, including layout"""

    _validation_method = '_fixed'

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self._schemas = PersistentMapping()
        self._layouts = PersistentMapping()
        self.addLayout(HtmlLayout('view', 'View'))
        self.addLayout(HtmlLayout('edit', 'Edit'))
        self.addSchema(Schema('default', 'Default'))

    def setValidationMethod(self, validation_method):
        """Sets a method that validates the layout of a document

        There are two built-in validations, No validation (always returns true),
        and fixed (makes sure it's the same as the type layouts
        """
        if not validation_method:
            self._validation_method = None
            return None

        if validation_method is _fixed_validation:
            self._validation_method = '_fixed'
            return None

        argnames = inspect.getargspec(validation_method)[0]
        if argnames != [template_layout, document_layout]:
            raise TypeError('The supplied method does not have the correct signature')
        self._validation_method = validation_method

    def getValidationMethod(self):
        """Returns the validation method"""
        if self._validation_method is None:
            return _flexibleValidationMethod
        if self._validation_method == '_fixed':
            return _fixedValidationMethod
        return self._validation_method

    def isFixedValidation(self):
        if self._validation_method == '_fixed':
            return 1
        else:
            return 0

    def addLayout(self, layout):
        self._layouts[layout.id] = layout

    def removeLayout(self, layout_id):
        del self._layouts[layout_id]

    def getLayoutIds(self):
        return self._layouts.keys()

    def getLayout(self, layout_id):
        return self._layouts[layout_id]

    def addSchema(self, schema):
        self._schemas[schema.id] = schema

    def removeSchema(self, schema_id):
        del self._schemas[schema_id]

    def getSchemaIds(self):
        return self._schemas.keys()

    def getSchema(self, schema_id):
        return self._schemas[schema_id]

    def getDataModel(self):
        # TODO: fetch the global schemas too.
        schemas = self.getSchemaIds()
        dm = DataModel()
        for schema in schemas:
            # The schemas can appear in any order, meaning this if there is
            # colliding field names, which field will "win" is completely random.
            dm.addSchema(self.getSchema(schema))
        # TODO: Also get global schemas.
        return dm

    def getSchemaForFieldId(self, fieldid):
        for schemaid, schema in self._schemas.items():
            if schema.has_key(fieldid):
                return schema
        raise KeyError('No field named %s found' % str(fieldid))

