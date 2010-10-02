# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
# Author: Georges Racinet <georges@racinet.fr>
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

import logging

from Acquisition import aq_base
from OFS.Image import File
from OFS.SimpleItem import Item

from Products.CPSUtil.text import OLD_CPS_ENCODING, upgrade_string_unicode
from Vocabulary import Vocabulary, CPSVocabulary


def fix_338_340_attached_files(portal):
    """Fix attached files' and images' names

    Before 3.4.0, the File object stored the filename in the File id and
    a title in the File title.

    But in Zope there is a constraint that a contained object's id is
    the one sees by the container. This is important for exports, where
    adapters on the object itself have to know the correct id.

    So in 3.4.0, the File id is whatever the container decides, and the
    File title is used to store the filename.
    """

    starts = [
        'portal_repository',
        'portal_cpsportlets',
        'portal_themes',
        '.cps_portlets',
        ]

    n = 0
    for rootid in starts:
        if getattr(aq_base(portal), rootid, None) is None:
            continue
        root = getattr(portal, rootid)
        for ob in root.objectValues():
            n += _fix_attached_recurse(ob)
    msg = "Fixed %d files." % n
    # FIXME: should be logged by CPSCore upgrade engine
    logging.getLogger('CPSSchemas.upgrade').debug(msg)
    return msg

def _fix_attached_recurse(ob):
    n = 0
    ob.getId() # unghostify, so that __dict__ is fetched
    for key, value in ob.__dict__.items():
        if isinstance(value, Item):
            subob = getattr(ob, key) # get acquisition wrappers
            n += _fix_attached_one(key, subob)
            n += _fix_attached_recurse(subob)
    return n

def _fix_attached_one(id, ob):
    if not isinstance(ob, File):
        return 0
    if ob.getId() == id:
        return 0
    title = ob.getId()
    old_title = ob.title
    ob._setId(id)
    ob.title = title
    if old_title != title:
        # Keep this so that no information is lost, in case we later
        # want to migrate to a widget with an 'alt' field
        #ob._alt_title = old_title
        pass
    return 1

def fix_voc_unicode(voc):
    if not isinstance(voc, CPSVocabulary):
        raise ValueError(
            "Upgrade routine works on CPSSchemas.Vocabulary.CPSVocabulary instances")

    def decode_needed(s):
        if isinstance(s, unicode):
            return s
        return s.decode(OLD_CPS_ENCODING)

    voc.title = decode_needed(voc.title)
    voc.description = decode_needed(voc.description)

    for k, v in voc.items():
        voc.set(k, decode_needed(v), msgid=voc.getMsgid(k))

def upgrade_voctool_unicode(portal):
    vtool = portal.portal_vocabularies
    logger = logging.getLogger(
        'Products.CPSSchemas.upgrade::upgrade_vocs_unicode')
    for voc in vtool.objectValues():
        if not isinstance(voc, CPSVocabulary):
            logger.warn("Not upgradeable : %s, check manually", voc)
            continue
        logger.info("Converting vocabulary %s to unicode", voc.getId())
        fix_voc_unicode(voc)
    logger.info("Finished to convert vocabularies found in tool.")

def upgrade_datamodel_unicode(dm):
    """Upgrade the datamodel to unicode strings and commits its content.

    Dependent fields and new revision spawning are *not* executed
    """
    sfields = []
    slfields = []
    for f_id, f in dm._fields.items():
        if f.write_ignore_storage:
            continue

        try:
            if f.meta_type == 'CPS String Field':
                dm[f_id] = upgrade_string_unicode(dm[f_id])
            elif f.meta_type == 'CPS String List Field':
                lv = dm[f_id]
                if not lv:
                    continue
                dm[f_id] = [upgrade_string_unicode(v) for v in lv]
            elif f.meta_type == 'CPS Ascii String Field':
                v = dm[f_id]
                try:
                    dm[f_id] = str(v)
                except UnicodeError:
                    logger.error("Non ascii content for CPS Ascii String Field"
                                 " in %s", doc.getId())
            elif f.meta_type == 'CPS Ascii String List Field':
                lv = dm[f_id]
                if not lv:
                    continue
                try:
                    dm[f_id] = [str(v) for v in lv]
                except UnicodeError:
                    logger.error("Non ascii content for CPS Ascii String List "
                                 "Field in %s", doc.getId())
        except WriteAccessError:
            # no write_ignore, but even Manager can't write to it ?
            # not this step's job to guess what this means
            pass

    dm._commitData() # avoid _commit() (see docstring)
    return True

