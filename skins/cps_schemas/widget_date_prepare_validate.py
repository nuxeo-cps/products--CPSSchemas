##parameters=mode, datastructure, datamodel

from string import split

widget_id = context.getWidgetId()
field_id = context.fields[0]

if mode == 'prepare':
    datastructure.set(widget_id, datamodel[field_id])
    return
else: # Validate
    value = datastructure.get(widget_id, '')
    date = split(value,'/')
    if len(date) != 3:
        datastructure.setError(widget_id,
                               "Must have day/month/year")
        ok = 0
    else:
        datamodel.set(field_id, value)
        ok = 1
    return ok
