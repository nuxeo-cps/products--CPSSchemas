##parameters=voc_id=None, msgid=0
# $Id$
"""Return vocabulary keys sorted by label or by msgid"""

if voc_id is None:
    return None

cpsmcat = context.translation_service
voc = context.portal_vocabularies[voc_id]

voc_items = voc.items()
if msgid == 0:
    l = [ (x[1], x[0]) for x in voc_items]
    l.sort()
    return [x[1] for x in l]
else:
    l = [ (cpsmcat(voc.getMsgid(x[0])), x[0]) for x in voc_items]
    l.sort()
    return [x[1] for x in l]


