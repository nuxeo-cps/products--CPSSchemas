##parameters=mode, datastructure
# $Id$

datamodel = datastructure.getDataModel()

widget_id = context.getWidgetId()
field_id = context.fields[0]

if mode == 'prepare':
    datastructure.set(widget_id, datamodel[field_id])
    return

if mode == 'validate':
    value = datastructure.get(widget_id, '')
    if not value.startswith('dummy'):
        datastructure.setError(widget_id,
                               "Must begin with 'dummy'")
        ok = 0
    else:
        datamodel.set(field_id, value)
        ok = 1
    return ok
