# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

from ZODB.PersistentMapping import PersistentMapping

from Products.CPSDocument.Template import Template
from Products.CPSDocument.DataStructure import DataStructure

class CPSDocument:
    """A document with a flexible data structure"""

    def __init__(self, id, title, template):
        self._data = PersistentMapping()
        self._data_structure = None
        self._layouts = None
        self.id = id
        self.title = title
        self._template = template

    def setStructure(self, data_structure):
        template = self.getTemplate()
        if template.isFixedValidation():
            raise LayoutValidationError("This document type does not allow \
                                        modifications to the structure")
        validation_error = self.validateStructure(data_structure)
        if validation_error:
            raise LayoutValidationError(validation_error) #Maybe the validation_method should raise this?
        self._structure = data_structure

    def getStructure(self):
        template = self.getTemplate()
        if template.isFixedValidation():
            return template.getStructure()
        else:
            return self._structure

    def setLayout(self, new_layout):
        template = self.getTemplate()
        if template.isFixedValidation():
            raise LayoutValidationError("This document type does not allow \
                                        modifications to the layout")
        validation_error = self.validateLayout(new_layout)
        if validation_error:
            raise LayoutValidationError(validation_error) #Maybe the validation_method should raise this?
        self._layout = new_layout

    def getLayout(self):
        """Returns a layout object"""
        template = self.getTemplate()
        if template.isFixedValidation() or self._layout is None:
            return template.getLayout(layout_id)
        else:
            return self._getLayout(layout_id)

    def render(self, layout_id):
        """Returns the rendrition of the document"""
        layout = self.getLayout(layout_id)
        template = self.getTemplate()
        data = template.getData(self)
        return layout.render(template, data)

    def setData(self, dict):
        """Sets the data of the object from a dictionary or dictionary-like object"""
        self._data.update(dict)

    def getData(self, id=None):
        if id is None: # return all data as dict
            self._data.copy() # Make a copy before returning
        if self._data.has_key(id):
            return self._data[id]
        else:
            return self.getStructure()[id].getDefaultValue()

    def setDocumentType(self, document_type):
        """Sets the document type of the document

        A document type is the name of a specific template"""
        return None

    def getDocumentType(self):
        """Gets the document type of the document"""
        return None

    def getTemplate(self):
        """Gets the Template of the document"""
        return self._template

    def validateLayout(self, layout=None):
        """Checks that the layout adheres to the layout

        If called without argument, checks the documents stored layout.
        """
        template = self.getTemplate()
        method = template.getValidationMethod()
        if layout is None:
            layout = self.getLayout()
        return method(template.getLayout(), layout)
