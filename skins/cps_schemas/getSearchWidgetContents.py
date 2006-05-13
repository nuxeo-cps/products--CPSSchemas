##parameters=dm

from Products.CMFCore.utils import getToolByName
from ZTUtils import make_query
from zLOG import LOG, DEBUG

def getContents(dm):
    wfolder = dm.get('folder', '')
    sort_and_direction = dm.get('sort_by', '').split('_', 1)
    if len(sort_and_direction) != 2:
        wsort_by = wdirection = ''
    else:
        wsort_by = sort_and_direction[0]
        wdirection = sort_and_direction[1]
    wnb_items = dm.get('nb_items', 0)
    wtitle = dm.get('title', '')

    """Get a sorted list of contents object"""
    utool = getToolByName(context, 'portal_url')
    folder = getFolderObject(wfolder)
    items = []
    link_more = ''
    if folder:
        query = buildQuery(dm)
        if len(query):
            # search
            folder_prefix = ''
            if wfolder:
                folder_prefix = utool.getRelativeUrl(folder)
            items = folder.search(query=query,
                                  sort_by=wsort_by,
                                  direction=wdirection,
                                  hide_folder=0,
                                  folder_prefix=folder_prefix)
        else:
            # this is a folder content box
            displayed = context.REQUEST.get('displayed', [''])
            items = folder.getFolderContents(sort_by=wsort_by,
                                                 direction=wdirection,
                                                 hide_folder=1,
                                                 displayed=displayed)
        
        if wnb_items and len(items) > wnb_items:
            items = items[:wnb_items]
            if len(query):
                if query.has_key('modified'):
                    # Use argument marshalling
                    query['modified:date'] = query['modified']
                    del query['modified']
                q = make_query(sort_by=wsort_by,
                               direction=wdirection,
                               hide_folder=1,
                               folder_prefix=folder_prefix,
                               title_search=wtitle,
                               search_within_results=1,
                               **query)
                link_more = './advanced_search_form?%s' % q
            else:
                link_more = utool.getRelativeUrl(folder)
    return (items, link_more)

def getFolderObject(wfolder):
    obj = None
    if not wfolder:
        obj = context
    else:
        container = context
        folder = wfolder
        # if folder path start with a '/' then
        #     we 're expecting an absolute path
        # else
        #     folder must be an attribute of context,
        #     because we don't want any acquisition
        if wfolder[0]=='/':
            container = context.portal_url.getPortalObject()
            folder = wfolder[1:]
        # setting folder to '.' allow a contextual search
        elif wfolder == '.':
            return context
        elif not hasattr(aq_base(container), folder):
            return obj
        try:
            obj = container.restrictedTraverse(folder)
        except KeyError:
            pass
    return obj

def buildQuery(dm):
    """Build a query for search.py """
    query = {}
    wquery_fulltext = dm.get('query_fulltext', '')
    if wquery_fulltext:
        query['SearchableText'] = wquery_fulltext
    wquery_title = dm.get('query_title', '')
    if wquery_title:
        query['Title'] = wquery_title
    wquery_portal_type = dm.get('query_portal_type', '')
    if wquery_portal_type and filter(None, wquery_portal_type):
        query['portal_type'] = list(wquery_portal_type)
    wquery_description = dm.get('query_description', '')
    if wquery_description:
        query['Description'] = wquery_description
    wquery_status = dm.get('query_status', '')
    if wquery_status:
        query['review_state'] = wquery_status
    wquery_modified = dm.get('query_modified', '')
    if wquery_modified:
        modified = None
        if wquery_modified == 'time_last_login':
            mtool = getToolByName(context, 'portal_membership')
            member = mtool.getAuthenticatedMember()
            if hasattr(aq_base(member), 'last_login_time'):
                modified = member.last_login_time
        else:
            today = DateTime()
            if wquery_modified == 'time_yesterday':
                modified = (today - 1).Date()
            elif wquery_modified == 'time_last_week':
                modified = (today - 7).Date()
            elif wquery_modified == 'time_last_month':
                modified = (today - 31).Date()
        if modified:
            query['modified'] = modified
            query['modified_usage'] = "range:min"
    return query

return getContents(dm)