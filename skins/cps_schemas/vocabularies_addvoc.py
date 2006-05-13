##parameters=new_vocid, REQUEST

# Parameters:
#
# new_vocid - id of the new vocabulary object to create.
# REQUEST - the request object is mandatory.

if new_vocid:
    if new_vocid in context.portal_vocabularies.objectIds():
        psm = "cpsschemas_psm_vocabulary_id_exists"
        action_path = 'vocabularies_manage_form'
        REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' %
                                  (context.absolute_url(), action_path, psm))
    else:
        context.portal_vocabularies.manage_addCPSVocabulary(new_vocid)
        psm = "cpsschemas_psm_vocabulary_created"
        action_path = 'vocabulary_edit_form'
        REQUEST.RESPONSE.redirect('%s/%s?voc_id=%s&portal_status_message=%s' %
                                  (context.absolute_url(), action_path,
                                   new_vocid, psm))
else:
    psm = "cpsschemas_psm_vocabulary_id_missing"
    action_path = 'vocabularies_manage_form'
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' %
                              (context.absolute_url(), action_path, psm))
