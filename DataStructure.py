# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

# TODO: Ponder this
# Should the data structure always contain all defined fields in the model
# both for data and errors? That would be the easiest, but it's not possible
# to do any checks for this in the DataStructure itself. It's also not possible
# to let the DataStructure get default values from the DataModel, unless it has
# a reference to the DataModel. This means, that trying to get data that doesn't
# exist in the DataStructure will raise a key-error. If that is acceptable, the
# current basic structure with only two dicts as attributes will do well.
# If it's not acceptable, a much more complicated data model is needed.


class DataStructure:
    """Used for passing a documents data and validation errors around"""

    def __init__(self, data={}, errors={}):
        self.data = data
        self.errors = errors



