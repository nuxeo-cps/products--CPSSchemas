##parameters=voc_id, REQUEST

# Parameters:
#
# voc_id - id of the vocabulary object to update.
# REQUEST - the request object is mandatory.
#
# values are taken from the 'form' dictionary and parsed by
# the 'manage_changeVocabulary' method.

vocabulary = context.portal_vocabularies[voc_id]
vocabulary.manage_changeVocabulary(form=REQUEST.form)

psm = 'cpsschemas_psm_vocabulary_updated'
action_path = 'vocab_edit_form'
REQUEST.RESPONSE.redirect('%s/%s?voc_id=%s&portal_status_message=%s' %
                          (context.absolute_url(), action_path, voc_id, psm))
