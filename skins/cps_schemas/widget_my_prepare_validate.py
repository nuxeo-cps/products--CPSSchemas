##parameters=mode, datastructure

datamodel = datastructure.getDataModel()

widget_id = context.getWidgetId()
field_id = context.fields[0]

if mode == 'prepare':
    datastructure.set(widget_id, datamodel[field_id])
    return
else: # Validate
    value = datastructure.get(widget_id, '')
    if not value.startswith('my'):
        datastructure.setError(widget_id,
                               "Argh error, doit commencer par 'my'")
        ok = 0
    else:
        datamodel.set(field_id, value)
        ok = 1
    return ok
