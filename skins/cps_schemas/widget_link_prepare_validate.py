##parameters=mode, datastructure, post_validate=1
# $Id$

if mode != 'validate':
    # we handle only validation
    return

if not post_validate:
    # we do nothing on pre validation
    return 1

widget_href = context.widget_ids[0]

# check that we have a valid URL
from re import match
href = datastructure.get(widget_href, '')
if href and not match(
    r'^((http://)|/)?([\w\~](\:|\.|\-|\/|\?|\=|\&|\+)?){2,}$', href):
    datastructure.setError(widget_href, 'cpsschemas_err_url')
    return 0

return 1
