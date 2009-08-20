import unittest
from Testing import ZopeTestCase

from collective.flowplayer.utils import properties_to_javascript

class MockPortal(object):
    def absolute_url_path(self):
        return '/portal'

class MockPropertySheet(object):
    _items = dict()
    
    def propertyItems(self):
        return self._items.items()

class TestUtils(ZopeTestCase.ZopeTestCase):
    
    def afterSetUp(self):
        self.props = MockPropertySheet()
        self.props._items['title'] = 'Player properties'
        self.props._items['player'] = 'flowplayer.swf'
        self.props._items['plugins/controls/url'] = '${portal_path}flowplayer.controls.swf'
        self.props._items['plugins/controls/all'] = False
        self.props._items['plugins/controls/play'] = True
        self.props._items['plugins/controls/scrubber'] = True
        self.props._items['plugins/controls/tooltips/fullscreen'] = 'Enter fullscreen mode'
        self.props._items['plugins/controls/tooltips/buttons'] = True
        self.props._items['plugins/audio/url'] = '++resource++collective.flowplayer/flowplayer.audio.swf'
        self.props._items['clip/autoPlay'] = False
        self.props._items['clip/autoBuffering'] = True
    
    def test_parsing(self):
        portal = MockPortal()
        parsed = properties_to_javascript(self.props, portal, ignore=['title', 'player'], as_json_string=False)
        self.assertEqual(len(parsed.keys()), 2) # plugins, clip
        self.assertEqual(len(parsed['plugins'].keys()), 2) # controls, audio
        self.assertEqual(parsed['plugins']['controls']['all'], False) 
        self.assertEqual(parsed['plugins']['controls']['scrubber'], True) 
        self.assertEqual(parsed['plugins']['controls']['url'], r'/portal/flowplayer.controls.swf') 
        self.assertEqual(parsed['plugins']['audio']['url'], r'%2B%2Bresource%2B%2Bcollective.flowplayer/flowplayer.audio.swf') 
        self.assertEqual(parsed['clip']['autoBuffering'], True) 
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtils))
    return suite