# Fields and widgets registration
# this is suboptimal because it's a side effect, but that's good enough for now
# most tests in there aren't ZopeTestCase, so they can't profit from
# CPSZCMLLayer

from Products.CPSSchemas.Field import FieldRegistry
from Products.CPSSchemas.BasicFields import CPSStringField
from Products.CPSSchemas.BasicFields import CPSFileField
from Products.CPSSchemas.BasicFields import CPSDateTimeField
from Products.CPSSchemas.BasicFields import CPSAsciiStringField
from Products.CPSSchemas.BasicFields import CPSImageField
from Products.CPSSchemas.BasicFields import CPSIntField
from Products.CPSSchemas.Widget import widgetRegistry
from Products.CPSSchemas.BasicWidgets import CPSIntWidget
from Products.CPSSchemas.BasicWidgets import CPSStringWidget

for cls in (CPSStringField, CPSFileField, CPSDateTimeField,
            CPSAsciiStringField, CPSImageField, CPSIntField):
    FieldRegistry.register(cls)

for cls in (CPSIntWidget, CPSStringWidget):
    widgetRegistry.register(cls)
