##parameters=input_id=None, **kw
# $Id$
"""
Hack Epoz init to setup data from opener/input_id
"""

jspatch = """
<!--
var data;
data = opener.document.getElementById("%s").value;
"""

name = kw.get('name')
del kw['name']
del kw['data']
jsepoz = context.Epoz(name=name, data='data', css='nuxeo_css2.css', **kw)
jsepoz = jsepoz.replace('<!--', jspatch % input_id)
jsepoz = jsepoz.replace("'data'", 'data')

return jsepoz
