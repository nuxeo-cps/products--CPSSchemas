##parameters=REQUEST=None, **kw
"""
Action called when something is changed in the flexible part of a document.
"""

layout = 'dummy2' # XXX

# XXX PROTOTYPE


if REQUEST is not None:
    kw.update(REQUEST.form)

up_row = None
down_row = None
delete_rows = []
for k in kw.keys():
    if k.startswith('uprow_'):
        up_row = int(k[len('uprow_'):])
    if k.startswith('downrow_'):
        down_row = int(k[len('downrow_'):])
    if k.startswith('deleterow_'):
        delete_rows.append(int(k[len('deleterow_'):]))
if up_row is not None or down_row is not None:
    context.flexibleChangeLayout(layout, up_row=up_row, down_row=down_row)
if delete_rows:
    context.flexibleDelWidgetRows(layout, delete_rows)

if kw.has_key('addtxt_button'):
    context.flexibleAddWidget(layout, 'TextArea Widget', width=20)


if REQUEST is not None:
    REQUEST.RESPONSE.redirect(context.absolute_url()+'/cpsdocument_flex_form')
