# (c) 2003 Nuxeo SARL <http://nuxeo.com>
# $Id$

# The DataModel is a transient object that holds info about the schemas.

_marker = 'marker'

class DataModel:

    def __init__(self):
        self._fields = {}
        self._schemas = {}

    def addSchema(self, schema):
        for fieldid in schema.keys():
            if self._fields.has_key(fieldid):
                self._fields[fieldid] = self._fields[fieldid] + (schema.id,)
            else:
                self._fields[fieldid] = (schema.id,)

        self._schemas[schema.id] = schema

    def getFieldIds(self):
        return self._fields.keys()

    def getSchemasForFieldId(self, fieldid):
        if self._fields.has_key(fieldid):
            return self._fields[fieldid]
        return ()

    def getSchemaIds(self):
        return self._schemas.keys()

    def getSchema(self, schemaid):
        return self._schemas[schemaid]

    def getBestSchemaForField(self, fieldid, data=_marker):
        schemas = self.getSchemasForFieldId(fieldid)
        if len(schemas) == 1:
            return schemas[0]
        if len(schemas) > 0: # Several schemas has a field with this id.
            for schema in schemas:
                if data is _marker: # Just return first schema
                    return schema
                # We have example data to use in finding the field.
                # Try an validate that with the field to find a match
                field = self.getSchema(schema)[fieldid]
                try:
                    vdata = field.validate(data)
                    if vdata == data:
                        return schema
                except ValueError:
                    continue # Try next schema
        return None # No schemas would validate this field. Skip it.
        # Maybe raise an error instead?

    def getField(self, fieldid, data=_marker):
        schemaid = self.getBestSchemaForField(fieldid, data)
        schema = self.getSchema(schemaid)
        return schema[fieldid]
