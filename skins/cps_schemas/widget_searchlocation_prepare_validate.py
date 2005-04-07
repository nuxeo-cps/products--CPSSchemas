##parameters=mode, datastructure
# $Id$
"""Prepare and Validate SearchLocation widget.

Init value with current path.
"""

datamodel = datastructure.getDataModel()
widget_id = context.getWidgetId()
field_id = context.fields[0]
purl = context.portal_url
portal_path = '/'.join(purl.getPhysicalPath()[:-1])

if mode == 'prepare':
    proxy = datamodel.getProxy()
    rpath = proxy.absolute_url(relative=1)[len(portal_path):]
    datastructure.set(widget_id, rpath)
    datastructure.set(widget_id+'_select', 'site')
    return
else:
    # Validate
    ret = 1
    value = datastructure.get(widget_id, '')
    value_select = datastructure.get(widget_id+'_select', '')
    if value_select == 'here':
        value = '/'.join([portal_path, value])
        # check that value is valid
        # datastructure.setError(widget_id, '')
        datamodel.set(field_id, value)
    return ret
