import unittest
from Testing import ZopeTestCase

from OFS.PropertyManager import PropertyManager
from collective.flowplayer.utils import properties_to_dict

class TestUtils(ZopeTestCase.ZopeTestCase):
    
    def afterSetUp(self):
        self.props = PropertyManager()
        # PropertyManager has title property already
        self.props.manage_changeProperties(title = 'Player properties')
        self.props.manage_addProperty('player', 'flowplayer.swf', 'string')
        self.props.manage_addProperty('plugins/controls/url', '${portal_path}flowplayer.controls.swf', 'string')
        self.props.manage_addProperty('plugins/controls/all', False, 'boolean')
        self.props.manage_addProperty('plugins/controls/play', True, 'boolean')
        self.props.manage_addProperty('plugins/controls/scrubber', True, 'boolean')
        self.props.manage_addProperty('plugins/controls/tooltips/fullscreen', 'Enter fullscreen mode', 'string')
        self.props.manage_addProperty('plugins/controls/tooltips/buttons', True, 'boolean')
        self.props.manage_addProperty('plugins/audio/url', '${portal_url}++resource++collective.flowplayer/flowplayer.audio.swf', 'string')
        self.props.manage_addProperty('clip/autoPlay',False, 'boolean')
        self.props.manage_addProperty('clip/autoBuffering', True, 'boolean')
    
    def test_parsing(self):
        parsed = properties_to_dict(self.props, 'http://localhost', ignore=['title', 'player'])
        self.assertEqual(len(parsed.keys()), 2) # plugins, clip
        self.assertEqual(len(parsed['plugins'].keys()), 2) # controls, audio
        self.assertEqual(parsed['plugins']['controls']['all'], False) 
        self.assertEqual(parsed['plugins']['controls']['scrubber'], True) 
        self.assertEqual(parsed['plugins']['controls']['url'], r'http%3A//localhost/flowplayer.controls.swf') 
        self.assertEqual(parsed['plugins']['audio']['url'], r'http%3A//localhost/%2B%2Bresource%2B%2Bcollective.flowplayer/flowplayer.audio.swf') 
        self.assertEqual(parsed['clip']['autoBuffering'], True) 
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtils))
    return suite