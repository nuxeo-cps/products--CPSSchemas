##parameters=voc_id, new_key, new_label, new_msgid, REQUEST

# Parameters:
#
# voc_id - id of the vocabulary object to complete.
# new_key, new_label, new_msgid - properties of the new entry
# REQUEST - the request object is mandatory.

vocabulary = context.portal_vocabularies[voc_id]
vocabulary.manage_addVocabularyItem(new_key, new_label, new_msgid)

psm = 'cpsschemas_psm_vocabulary_key_added'
action_path = 'vocab_edit_form'
REQUEST.RESPONSE.redirect('%s/%s?voc_id=%s&portal_status_message=%s' %
                          (context.absolute_url(), action_path, voc_id, psm))
