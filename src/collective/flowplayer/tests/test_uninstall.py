# -*- coding: utf-8 -*-
from collective.flowplayer.testing import \
    COLLECTIVE_FLOWPLAYER_INTEGRATION_TESTING

import unittest2 as unittest
from zope.interface.interfaces import IInterface
from zope.component import getSiteManager


class InstallationTestCase(unittest.TestCase):

    layer = COLLECTIVE_FLOWPLAYER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.types = self.portal.portal_types

    def test_profile_uninstall(self):
        from collective.flowplayer import uninstall
        uninstall.profile(self.portal)

        css_registry = self.portal['portal_css']
        stylesheets_ids = css_registry.getResourceIds()

        base = "++resource++collective.flowplayer"
        self.assertNotIn(base + '.css/flowplayer.css', stylesheets_ids)
        self.assertNotIn(base + '.css/flowplayer-horizontal.css',
                         stylesheets_ids)

        js_registry = self.portal['portal_javascripts']
        javascript_ids = js_registry.getResourceIds()

        base = "++resource++collective.flowplayer"
        self.assertNotIn(base + '/flowplayer.min.js', javascript_ids)
        self.assertNotIn(base + '/flowplayer.playlist.min.js', javascript_ids)
        self.assertNotIn(base + '.js/init.js', javascript_ids)

    def test_properties_uninstall(self):
        from collective.flowplayer import uninstall
        uninstall.properties(self.portal)
        ptool = self.portal.portal_properties
        self.assertEquals(ptool.get('flowplayer_properties', None), None)

    def test_utility_uninstall(self):
        from collective.flowplayer import uninstall
        uninstall.utility(self.portal)
        sm = getSiteManager(context=self.portal)
        name = u'collective.flowplayer.interfaces.IFlowPlayerSite'
        self.assertEquals(
            sm.queryUtility(IInterface, name=name, default=None),
            None)

    def test_interfaces_uninstall(self):
        from collective.flowplayer import uninstall
        from collective.flowplayer.events import ChangeFileView
        from collective.flowplayer.interfaces import IAudio
        self.portal.invokeFactory(id='file', type_name='File')
        fileOb = self.portal.file

        class FakeEvent(object):

            def __init__(self, object):
                self.object = object

        handler = ChangeFileView(fileOb, FakeEvent(fileOb))
        handler.handleAudio()
        self.assertTrue(IAudio.providedBy(fileOb))

        uninstall.interfaces(self.portal)
        self.assertFalse(IAudio.providedBy(fileOb))

    def test_views_uninstall(self):
        from collective.flowplayer import uninstall
        from collective.flowplayer.interfaces import IAudio
        from zope.interface import alsoProvides

        self.portal.invokeFactory(id='file', type_name='File')
        fileOb = self.portal.file
        alsoProvides(fileOb, IAudio)
        fileOb.reindexObject(idxs=['object_provides'])
        fileOb.setLayout('flowplayer')

        uninstall.views(self.portal)
        self.assertNotEquals(fileOb.getLayout(), 'flowplayer')

        file_type = self.types.File
        self.assertNotIn('flowplayer', file_type.view_methods)
