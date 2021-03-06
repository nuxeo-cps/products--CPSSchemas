##parameters=path_list=[]
portal_url = context.portal_url
portal = portal_url.getPortalObject()

returned_list = []
mtool = context.portal_membership
checkPerm = mtool.checkPermission

for path in path_list:
    try:
        if path.startswith('/'):
            path = path[1:]
        object = portal.restrictedTraverse(path)
        if not checkPerm('View', object):
            continue
        returned_list.append(object)
    except:
        pass


return returned_list
