##parameters=REQUEST=None, **kw
"""
Action called when something is changed in the flexible part of a document.
"""

# XXX PROTOTYPE


if REQUEST is not None:
    kw.update(REQUEST.form)

if kw.has_key('addtxt_button'):
    layout = 'dummy2'
    context.flexibleAddWidget(layout, 'TextArea Widget', width=20)

if REQUEST is not None:
    REQUEST.RESPONSE.redirect(context.absolute_url()+'/cpsdocument_flex_form')
