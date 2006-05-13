##parameters=mode, datastructure
# $Id$
"""Prepare and Validate SearchLocation widget.

Init value with current relative path. Relative path does not take care of
virtual hosting since catalog does not take care of it.
"""
from Products.CMFCore.utils import getToolByName

utool = getToolByName(context, 'portal_url')

datamodel = datastructure.getDataModel()
widget_id = context.getWidgetId()
field_id = context.fields[0]

portal_path = utool.getPortalPath()

if mode == 'prepare':
    proxy = datamodel.getProxy()
    ppath = '/'.join(proxy.getPhysicalPath())
    rpath = ppath[len(portal_path)+1:]
    datastructure.set(widget_id, rpath)
    datastructure.set(widget_id+'_select', 'site')
    return

if mode == 'validate':
    value = datastructure.get(widget_id, '')
    value_select = datastructure.get(widget_id+'_select', '')
    if value_select == 'here' and value:
        value = '/'.join([portal_path, value])
        # check that value is valid
        # datastructure.setError(widget_id, '')
        datamodel.set(field_id, value)
    return True
