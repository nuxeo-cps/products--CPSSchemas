# -*- coding: iso-8859-15 -*-
# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com>
# Author: Julien Anguenot <ja@nuxeo.com>
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
"""Placeless Translation Patch for CMF / Plone

Patch the portal to fake Localizer presence while waiting for the use of
PlacelessTranslationService within CPS.

Just a temporarly solution until CPS will be shipped wih
PlacelessTranslationService
"""

import Acquisition
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.PlacelessTranslationService.Negotiator import negotiator

##################################################################
# PATCH the Plone Portal to fake Localizer
##################################################################

class LocalizerCls(Acquisition.Implicit):
    """Fake the Localizer
    """

    security = ClassSecurityInfo()

    security.declarePublic('default')
    def default(self, msgid):
        """Call translation"""

        # Indirect to PlacelessTranslationService
        ts = self.Control_Panel.TranslationService

        # Negotiate language
        target = self.get_selected_language()
        translation = ts.translate('default',
                                   msgid,
                                   target_language=target,
                                   as_unicode=True)

        # Translation may not exist. Don't return None
        if not translation:
            translation = ''
        return translation

    security.declarePublic('get_selected_language')
    def get_selected_language(self):
        """Negotiate language
        """
        _fallback = 'en'

        ts = self.Control_Panel.TranslationService
        plone_langs = ts.getLanguages('plone')
        lang = ts.negotiate_language(self.REQUEST, 'plone')
        if lang not in plone_langs:
            return _fallback
        return lang

InitializeClass(LocalizerCls)

Localizer = LocalizerCls()
from Products.CMFPlone.Portal import PloneSite

if not hasattr(PloneSite, 'Localizer'):
    # patchin an instance into a class !!!
    PloneSite.Localizer = Localizer
