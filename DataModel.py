# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

# The DataModel is a transient object that holds information about a
# Particular documents data structure, including schemas and storage

class DataModel:

    def __init__(self, document):
        self._document = document
        self._fields = {}
        self._schemas = {}
        self._adapters = {}

    def addSchema(self, schema):
        for fieldid in schema.keys():
            if self._fields.has_key(fieldid):
                raise KeyError('There two Schemas with field ' + fieldid + \
                               ' but field ids must be unique')
            else:
                self._fields[fieldid] = schema.id

        self._schemas[schema.id] = schema
        self._adapters[schema.id] = schema.makeStorageAdapter(self._document)
        
    def getFieldIds(self):
        return self._fields.keys()

    def getAdapter(self, schemaid):
        return self._adapters[schemaid]

    def getSchemaId(self, fieldid):
        return self._fields[fieldid]

    def getSchemaIds(self):
        return self._schemas.keys()

    def getSchema(self, schemaid):
        return self._schemas[schemaid]

    def getField(self, fieldid):
        schemaid = self.getSchemaId(fieldid)
        schema = self.getSchema(schemaid)
        return schema[fieldid]

    def makeDataStructure(self, datamodel):
        """Returns a DataStructure with all the data"""
        data = {}
        for schemaid in self.getSchemaIds():
            adapter = self.getAdapter(schemaid)
            data.update(adapter.readData())

        ds = DataStructure(data)
        return ds

    def writeDataStructure(self, datastructure):
        """Updates the content of a storage from a DataStructure

        Will clear the DataStructures modifiedFlags after writing, so
        the DataStructure can continue to be used. The validation may
        modify the datastructures data.
        """
        if not self.validateDataStructure(datastructure):
            raise ValidationError('Data structure contains invalid data')

        # First sort the data to be written into different
        # dicts, one for each schema.
        changed_data = {}
        for fieldid in datastructure.getModifiedFlags():
            schemaid = self.getSchemaId(fieldid)
            if not changed_data.has_key(schemaid):
                changed_data[schemaid] = {}
            changed_data[schemaid][fieldid] = datastructure[fieldid]

        # Now take the changed data per schema, and write it to the
        # DataAdapter correleating to that schema
        for schemaid in changed_data.keys():
            adapter = getAdapter(schemaid)
            adapter.writeData(changed_data[schemaid])
        # It's now stored, so clear the modify flags
        datastructure.clearAllModifiedFlags()

    def validateDataStructure(self, datastructure):
        """Will validate the datastructure and set any errors

        Returns 1 if validation suceeded, 0 if it failed on any field.
        Please not that this method most likely WILL modify the DataStructure
        """
        has_errors = 0
        for schemaid in self.getSchemaIds():
            for fieldid in self.getSchema(schemaid):
                field = self.getField(fieldid)
                try:
                    self[fieldid] = field.validate(datastructure[fieldid])
                    datastructure.delerrors(fieldid)
                except (TypeError, ValueError), errormsg:
                    self.errors[fieldid] = errormsg
                    has_errors = 1
        return not has_errors

