# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

# Data structures are classes that hold the content of a document while it is
# being used. It is NOT a storage, it's not persistent at all. It's purpose is:
# - Keeping track of which fields have changed, so that StorageAdapters only
#   need to update fields/tables that have been modified.
#
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
    - __setitem__ only updates the data, the errors will stay unchanged,
      no validation will occur. We COULD change this so validation occurs
      with setitem, and to set without validation you operate directly on
      DataStructure.data. It's mostly a matter of tatse, and I can't decide. :)"""

    def __init__(self, data={}, errors={}):
        self.data = {}
        self.data.update(data)
        self.errors = {}
        self.errors.update(errors)
        self.modified_fields = []

    # Override standard dictionary stuff:
    def clear(self, clear_modified_flags=0):
        if clear_modified_flags:
            self.modified_fields = []
        else:
            self.setModifiedFlags(self.data.keys())
        self.data.clear()
        self.errors.clear()

    def __setitem__(self, key, item):
        if item != self.data[key]: # Only change if it actually is different
            self.data[key] = item
            self.setModifiedFlag(key)

    def __delitem__(self, key):
        del self.data[key]
        if self.errors.has_key(key):
            del self.errors[key]
        self.setModifiedFlag(key)

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

    def update(self, dict):
        if isinstance(dict, UserDict):
            self.data.update(dict.data)
            self.setModifiedKeys(dict.keys())
        elif isinstance(dict, type(self.data)):
            self.data.update(dict)
            self.setModifiedFlags(dict.keys())
        else:
            for k, v in dict.items():
                self.data[k] = v
                self.setModifiedKey(k)

    def updateFromRequest(self, REQUEST):
        """Updates and validates field data from a REQUEST object

        This method (unlike the standard update method) will only update
        existing fields. It is used to set the data from request (or indeed
        any other object with a mapping-interface). No validation is done,
        the validation is instead done when storing the data via the DataModel.
        """
        for fieldid in self.keys():
            if REQUEST.has_key('field_'+fieldid): # The field_ syntax is used by formulator etc.
                self[fieldid] = REQUEST['field_'+fieldid]
            elif REQUEST.has_key(fieldid):
                self[fieldid] = REQUEST[fieldid] # Will return None if it doesn't exist

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

    def setModifiedFlag(self, key):
        if key not in self.modified_fields:
            self.modified_fields.append(key)

    def setModifiedFlags(self, keys):
        for key in keys:
            self.setModifiedFlag(key)

    def clearModifiedFlag(self, key):
        if key in self.modified_fields:
            self.modified_fields.remove(key)

    def clearModifiedFlags(self, keys):
        for key in keys:
            self.clearModifiedFlag(key)

    def clearAllModifiedFlags(self):
        self.modified_flags = []

    def getModifiedFlags(self):
        return self.modified_fields


