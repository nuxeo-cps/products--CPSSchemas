##parameters=del_vocid, REQUEST

# Parameters:
#
# del_vocid - id of the vocabulary object to delete.
# REQUEST - the request object is mandatory.

if del_vocid:
    context.portal_vocabularies.manage_delObjects([del_vocid])
    psm = 'cpsschemas_psm_vocabulary_deleted'
    action_path = 'vocab_manage_form'
else:
    psm = "cpsschemas_psm_vocabulary_id_missing"
    action_path = 'vocab_manage_form'

REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' %
                          (context.absolute_url(), action_path, psm))
