##parameters=mode, datastructure
# $Id$
"""
XXX add docstring
"""

if mode == 'prepare':

    # Changing position of text if there are 2 column
    content_wid = context.widget_ids[0]
    if len(context.widget_ids) > 1:
        # Schema can handle either 1 block or 2 blocks of text
        content_right_wid = context.widget_ids[1]
    else:
        content_right_wid = ''

    if content_right_wid and len(datastructure[content_right_wid]):
        # Column mode
        datastructure.set(content_wid + '_rposition', 'col_left')
        datastructure.set(content_right_wid + '_rposition', 'col_right')
    else:
        # Only one block of text
        datastructure.set(content_wid + '_rposition', 'normal')
        datastructure.set(content_right_wid + '_rposition', 'normal')

    return

if mode == 'prevalidate':
    # nothing more to do
    return True

if mode == 'validate':
    # We do nothing on post validation
    return True
