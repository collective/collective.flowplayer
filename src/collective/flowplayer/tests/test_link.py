# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import _createObjectByType

from collective.flowplayer.events import ChangeLinkView
from collective.flowplayer.interfaces import IMediaInfo, IVideo
from collective.flowplayer.testing import \
    COLLECTIVE_FLOWPLAYER_INTEGRATION_TESTING

import unittest
import os.path
import zope.interface


class StubEvent(object):

    def __init__(self, object):
        self.object = object


class ScalableLinkTest(unittest.TestCase):
    """ Test fetching of metadata of remote videos """

    layer = COLLECTIVE_FLOWPLAYER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal['test-folder']

    def test_link_dimensions(self):
        _createObjectByType('Link', self.folder, 'my-video-link')
        link = self.folder['my-video-link']
        link.setRemoteUrl('file://{0}'.format(
            os.path.join(os.path.dirname(__file__), 'barsandtone.flv')))
        zope.interface.alsoProvides(link, IVideo)

        self.assertEqual(IMediaInfo(link).width, None)
        self.assertEqual(IMediaInfo(link).height, None)

        ChangeLinkView(link, StubEvent(link))

        self.assertEqual(IMediaInfo(link).width, 360)
        self.assertEqual(IMediaInfo(link).height, 288)
