from types import ListType, TupleType

class FlexibleLayout:
    """Defines the layout of a document

    The layout is a list of fields"""

    def __init__(self):
        self._field_list = [] # An ordered list of the field ids
        self._fields = {} # The fields

    def getFieldIds(self):
        """Returns the ordered list of field ids"""
        return self._field_list

    def getField(self, fieldid):
        """Returns the field object with id fieldid"""
        return self._fields[fieldid]

    def getFields(self):
        """Returns a list of all fields"""
        fields = []
        for fieldid in self.getFieldIds():
            fields.append(self.getField(fieldid))
        return fields

    def addFields(self, fields):
        """Adds a field or a list of fields to the end of the field list"""
        if type(fields) is ListType or type(fields) is TupleType:
            for field in fields:
                self._addField(field)
        else:
            self._addField(fields)

    def _addField(self, field):
        """Adds one field to the end of the field-list"""
        fieldid = field.id()
        if self._fields.has_key(fieldid):
            raise KeyError("A Field with the id '%s' already exists" % fieldid)
        self._fields[fieldid] = field
        self._field_list.append(fieldid)

    def removeFields(self, fields):
        """Removes a field or a list of fields by id"""
        if type(fields) is ListType or type(fields) is TupleType:
            for field in fields:
                self._removeField(field)
        else:
            self._removeField(fields)

    def _removeField(self, fieldid):
        """Removes a field by id"""
        del self._fields[fieldid]
        self._field_list.remove(fieldid)


    def setFieldOrder(self, fieldid, order ):
        """Sets the specified field at the specifed position

        0 is first, -1 is last, no other negativ numbers are supported (at least not yet)
        """
        self._field_list.remove(fieldid)
        if order == -1 or order >= len(self._field_list):
            self._field_list.append(fieldid)
        else:
            self._field_list.insert(order, fieldid)

    def moveField(self, fieldid, distance):
        """Moves the specified field a number of positions

        Positive numbers move to higher index numbers, negavtive to lower index numbers"""
        oldpos = self._field_list.index(fieldid)
        newpos = oldpos + distance
        if newpos < 0:
            newpos = 0
        self.setFieldOrder(fieldid, newpos)




