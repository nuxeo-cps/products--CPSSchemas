##parameters=datastructure, datamodel

id = context.getWidgetId()
value = datastructure.get(id, '')
if not value.startswith('my'):
    datastructure.setError(id, "Argh error, doit commencer par 'my'")
    ok = 0
else:
    datamodel.set(context.fields[0], value)
    ok = 1

return ok
