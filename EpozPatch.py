# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$
from Products import Epoz
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zLOG import LOG, INFO

LOG('EpozPatch', INFO, 'Patching epoz_blank_iframe.html')
# override to load all css
Epoz.methods.update({'epoz_blank_iframe.html':
                     PageTemplateFile(
    'skins/cps_schemas/epoz_blank_iframe.html.pt',
    globals())})
