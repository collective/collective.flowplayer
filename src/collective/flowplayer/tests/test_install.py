# -*- coding: utf-8 -*-
from collective.flowplayer.testing import \
    COLLECTIVE_FLOWPLAYER_INTEGRATION_TESTING

import pkg_resources
import unittest2 as unittest


class InstallationTestCase(unittest.TestCase):

    layer = COLLECTIVE_FLOWPLAYER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.types = self.portal.portal_types

    def test_css_registered(self):
        css_registry = self.portal['portal_css']
        stylesheets_ids = css_registry.getResourceIds()

        base = "++resource++collective.flowplayer"
        self.assertIn(base + '.css/flowplayer.css', stylesheets_ids)
        self.assertIn(base + '.css/flowplayer-horizontal.css', stylesheets_ids)

    def test_js_registered(self):
        js_registry = self.portal['portal_javascripts']
        javascript_ids = js_registry.getResourceIds()

        base = "++resource++collective.flowplayer"
        self.assertIn(base + '/flowplayer.min.js', javascript_ids)
        self.assertIn(base + '/flowplayer.playlist.min.js', javascript_ids)
        self.assertIn(base + '.js/init.js', javascript_ids)

    def test_collection_or_topic_view_registered(self):
        try:
            pkg_resources.get_distribution('plone.app.collection')
        except pkg_resources.DistributionNotFound:
            HAS_COLLECTION = False
        else:
            HAS_COLLECTION = True

        if HAS_COLLECTION:
            self.assertIn('flowplayer', self.types['Collection'].view_methods)
        else:
            self.assertIn('flowplayer', self.types['Topic'].view_methods)
