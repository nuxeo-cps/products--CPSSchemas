##parameters=mode, datastructure
# $Id$

if mode != 'validate':
    return

widget_href = context.widget_ids[0]

# check that we have a valid URL
from re import match
href = datastructure.get(widget_href, '')
if href and not match(
    r'^((http://)|/)?([\w\~](\:|\.|\-|\/|\?|\=|\&|\+)?){2,}$', href):
    datastructure.setError(widget_href, 'cpsschemas_err_url')
    return 0

return 1
