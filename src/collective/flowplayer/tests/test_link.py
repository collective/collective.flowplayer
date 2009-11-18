import unittest
import os.path

import zope.interface

from Products.PloneTestCase import ptc

from collective.flowplayer import testing
from collective.flowplayer.interfaces import IMediaInfo, IVideo
from collective.flowplayer.events import ChangeLinkView

from Products.CMFPlone.utils import _createObjectByType

class StubEvent(object):

    def __init__(self, object):
        self.object = object

class ScalableLinkTest(ptc.PloneTestCase):
    """ Test fetching of metadata of remote videos """

    layer = testing.Layer

    def test_link_dimensions(self):
        _createObjectByType('Link', self.folder, 'my-video-link')
        link = self.folder['my-video-link']
        link.setRemoteUrl('file://%s' % os.path.join(os.path.dirname(__file__),
                                                    'barsandtone.flv'))
        zope.interface.alsoProvides(link, IVideo)

        self.failUnless(IMediaInfo(link).width is None)
        self.failUnless(IMediaInfo(link).height is None)

        ChangeLinkView(link, StubEvent(link))

        self.failUnlessEqual(IMediaInfo(link).width, 360)
        self.failUnlessEqual(IMediaInfo(link).height, 288)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
