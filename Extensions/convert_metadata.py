# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
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
"""
Convert some metadata from old storage adapter to the new one.
This does conversion of Coverage, Source and Relation.
"""

from zLOG import LOG, DEBUG
from AccessControl import getSecurityManager
from AccessControl import Unauthorized

from Products.CMFCore.utils import getToolByName


conversions = (('Coverage', 'coverage'),
               ('Source', 'source'),
               ('Relation', 'relation'),
               )

def convert_metadata(self):
    if not getSecurityManager().getUser().has_role('Manager'):
        raise Unauthorized('Must be a Manager')
    context = self
    repotool = getToolByName(self, 'portal_repository')
    log = []
    for id, ob in repotool.objectItems():
        # Unghostify object to have its dict loaded.
        ob.getId()
        done = []
        for oldattr, newattr in conversions:
            if ob.__dict__.has_key(oldattr):
                v = getattr(ob, oldattr)
                delattr(ob, oldattr)
                setattr(ob, newattr, v)
                done.append(oldattr)
        if done:
            msg = '%s (%s): %s' % (id, ob.title_or_id(),
                                   ' '.join(done))
            LOG('convert_metadata', DEBUG, msg)
            log.append(msg)
    return ('Done (%d conversions).\n%s' %
            (len(log), '\n'.join(log)))
