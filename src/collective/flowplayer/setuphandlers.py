from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPropertiesTool

# Properties are defined here, because if they are defined in propertiestool.xml,
# all properties are re-set the their initial state if you reinstall product
# in the quickinstaller.

_PROPERTIES = [
    dict(name='player', type_='string', value='${portal_url}/++resource++collective.flowplayer/flowplayer-3.1.2.swf'),
    dict(name='plugins/controls/url', type_='string', value='${portal_url}/++resource++collective.flowplayer/flowplayer.controls-3.1.2.swf'),
    dict(name='plugins/audio/url', type_='string', value='${portal_url}/++resource++collective.flowplayer/flowplayer.audio-3.1.0.swf'),
    dict(name='clip/autoPlay', type_='boolean', value=False),
    dict(name='clip/autoBuffering', type_='boolean', value=False),
    dict(name='clip/scaling', type_='string', value='fit'),
    dict(name='plugins/controls/volume', type_='boolean', value=True),
]

def importVarious(self):
    if self.readDataFile('collective.flowplayer.txt') is None:
        return

    portal = self.getSite()
    ptool = getToolByName(portal, 'portal_properties')
    props = ptool.flowplayer_properties

    for prop in _PROPERTIES:
        if not props.hasProperty(prop['name']):
            props.manage_addProperty(prop['name'], prop['value'], prop['type_'])
    
