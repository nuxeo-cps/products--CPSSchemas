# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

# Required vs non-required fields and default data behaviour
# ==========================================================
# That a field is required mean that it must have some data and that this data
# may not be None. So, None and non-existing means the same thing (this may
# seem obvious, but it isn't). An empty string and None is NOT the same however,
# which means that string fields will have to have separate settings for if it
# is required and if an empty string is allowed.
# A field may have default data. In fact, all fields have a default setting,
# but it is set to None by default. We find that there are four combinations
# of these settings:
# a: A required field with no default value
# b: A required field with default value
# c: A non-required field with no default value
# d: A non-required field with default value
# There are two different cases when both these settings in combination modify
# the fields behaviour:
# 1. When a field is set/validated with None
# 2. When a fields create view is displayed
#
# a: It is clear that if the field is required and no default is set, data must
# be submitted when the field is set/validated, or an validation error should
# occur.
# b: A required field that has a default value should return the default value
# when validation occurs with None or non-existant values.
# c. A non-required field with no default value and no requested value should
# not exist. If such a field exists, and is then set to None, it should be
# removed, or in cases where removing is not possible (such as in SQL tables) it
# should be set to None/NULL/NIL.
# d. This is less clear, but it should reasonably be set to None, or it will be
# impossible to set it to None, thereby in effect making it required. However,
# this field behaves differently from fields of type c when created, since the
# initial value shown in the creation form will contain the default value. It
# also behaves differently from type b fields, since you can remove the value
# before creation.
#
# This is all quite simple, but it took me a whole afternoon to get it straight,
# so the text should stay, so I don't get confused once again. :) /regebro


from UserDict import UserDict

class DataStructure(UserDict):
    """Used for passing a documents data and validation errors around

    It's basically two dictionaries, one for data and one for errors.
    The data dictionary is exposed through the standard dictionary interface,
    while the error dictionary is exposed through a set of methods.
    Bugs/features:
    - comparisons will not take errors into account
   -  __setitem__ only updates the data, the errors will stay unchanged"""

    def __init__(self, data={}, errors={}):
        self.data = {}
        if data is not None: self.update(data)
        self.errors = errors

    # Override standard dictionary stuff:
    def clear(self):
        self.data.clear()
        self.errors.clear()

    def __delitem__(self, key):
        del self.data[key]
        if self.errors.has_key(key):
            del self.errors[key]

    def copy(self):
        if self.__class__ is DataStructure:
            return DataStructure(self.data, self.errors)
        # Some kind of subclass. Just return a dict with data.
        # If more is needed, override copy() in the subclass.
        return self.data.copy()

    def popitem(self):
        key, val = self.data.popitem()
        if self.errors.has_key(key):
            del self.errors[key]
        return key, val

    # update methods. Standard update() still exists, and will
    # update the data, but not change the errors at all.
    def updateFromDictionaries(self, data, errors):
        self.update(data)
        self.errors = errors

    def makeDefault(self, datamodel):
        """Creates a DataStructure with the defaults from the data model"""
        self.clear()
        for fieldid in datamodel.keys():
            data = datamodel[fieldid].getDefaultValue()
            if data is not None:
                self[fieldid] = data

    def updateFromRequest(self, datamodel, REQUEST):
        """Updates and validates field data from a REQUEST object"""
        self.clear()
        for fieldid in datamodel.getFieldIds():
            field = datamodel.getField(fieldid)
            if REQUEST.has_key('field_'+fieldid): # The field_ syntax is used by formulator etc.
                data = REQUEST['field_'+fieldid]
            else:
                data = REQUEST.get(fieldid) # Will return None if it doesn't exist
            try:
                self[fieldid] = field.validate(data)
                self.errors[fieldid] = None
            except (TypeError, ValueError), errormsg:
                self.errors[fieldid] = errormsg
                self[fieldid] = data

    def updateFromDocument(self, template, document):
        self.clear()
        datamodel = template.getDatamodel()
        for fieldid in datamodel.keys():
            self.errors[fieldid] = None #  the data to be validated.
            self[fieldid] = template.getFieldValue(fieldid)

    # Expose the errors dictionary.
    def getError(self, key):
        return self.errors.get(key)

    def hasError(self, key):
        return self.errors.has_key(key)

    def setError(self, key, message):
        self.errors[key] = message

    def delError(self, key):
        """Removes an error"""
        if self.errors.has_key(key):
            del self.errors[key]

    def getErrorsFields(self):
        return self.errors.keys()

    def getErrors(self):
        return errors # TODO: Should it return the original or a copy?
