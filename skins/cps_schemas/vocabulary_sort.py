##parameters=voc_id=None, msgid=0
# $Id$
"""Return vocabulary keys sorted by label or by msgid"""

if voc_id is None:
    return None

cpsmcat = context.translation_service
voc = context.portal_vocabularies[voc_id]

voc_items = voc.items()
if msgid == 0:
    items = [ (x[1], x[0]) for x in voc_items]
elif msgid == 1:
    items = [ (cpsmcat(voc.getMsgid(x[0])), x[0]) for x in voc_items]
items.sort()

return [x[1] for x in items]


