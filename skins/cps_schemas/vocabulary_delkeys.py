##parameters=voc_id, REQUEST, keys=[]

# Parameters:
#
# voc_id - the id of the vocabulary object to clean
# REQUEST - the request object is mandatory.
# keys - the list of entry ids to delete

if keys:
    vocabulary = context.portal_vocabularies[voc_id]
    vocabulary.manage_delVocabularyItems(keys)
    psm = "cpsschemas_psm_vocabulary_entries_deleted"
else:
    psm = "cpsschemas_psm_vocabulary_no_entries_selected"

action_path = 'vocabulary_edit_form'
REQUEST.RESPONSE.redirect('%s/%s?voc_id=%s&portal_status_message=%s' %
                          (context.absolute_url(), action_path, voc_id, psm))
