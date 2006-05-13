##parameters=proxy, fileName, widgetId
# $Id$

portal = context.portal_url.getPortalObject()
portalAbsoluteUrl = portal.absolute_url()
proxyPhysicalPath = '/'.join(proxy.getPhysicalPath())

# Here we might use a special prefix to use special rewrite rules with
# Apache httpd.
#prefix = 'ooossl/'
prefix = ''

# The generated path should have one of the following forms depending on whether
# there are virtual host monster and httpd virtual hosting is used or not:
# /externalEdit_?path=/website/workspaces/folder/test/downloadFile/file/ooofile.sxw
# /website/externalEdit_?path=/website/workspaces/folder/test/downloadFile/file/ooofile.sxw
external_editor_path = ('%s/%sexternalEdit_?path=%s/downloadFile/%s/%s' %
                        (portalAbsoluteUrl, prefix, proxyPhysicalPath,
                         widgetId, fileName))

return external_editor_path
