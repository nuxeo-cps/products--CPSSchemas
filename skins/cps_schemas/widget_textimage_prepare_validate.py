##parameters=mode, datastructure, post_validate=1
# $Id$

if mode != 'validate':
    # we handle only validation
    return

if post_validate:
    # we do nothing on post validation
    return 1

# changing position of text if there is 2 column
content_wid = context.widget_ids[1]
content_right_wid = context.widget_ids[2]
if len(datastructure[content_right_wid]):
    # column mode
    datastructure.set(content_wid + '_rposition', 'col_left')
    datastructure.set(content_right_wid + '_rposition', 'col_right')
else:
    # only one block of text
    datastructure.set(content_wid + '_rposition', 'normal')
    datastructure.set(content_right_wid + '_rposition', 'normal')

return 1
