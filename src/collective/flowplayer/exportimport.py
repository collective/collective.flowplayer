from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPropertiesTool

# Properties are defined here, because if they are defined in propertiestool.xml,
# all properties are re-set the their initial state if you reinstall product
# in the quickinstaller.

_PROPERTIES = [
    dict(name='player', type_='string', value='${portal_url}/++resource++collective.flowplayer/flowplayer-3.1.2.swf'),
    dict(name='loop', type_='boolean', value=False),
    dict(name='initialVolumePercentage', type_='integer', value=50),
    dict(name='plugins/controls/url', type_='string', value='${portal_url}/++resource++collective.flowplayer/flowplayer.controls-3.1.2.swf'),
    dict(name='plugins/audio/url', type_='string', value='${portal_url}/++resource++collective.flowplayer/flowplayer.audio-3.1.0.swf'),
    dict(name='clip/autoPlay', type_='boolean', value=False),
    dict(name='clip/autoBuffering', type_='boolean', value=False),
    dict(name='clip/scaling', type_='string', value='fit'),
    dict(name='plugins/controls/volume', type_='boolean', value=True),
]

def import_various(context):
    
    if not context.readDataFile('collective.flowplayer.txt'):
        return
        
    site = context.getSite()
    kupu = getToolByName(site, 'kupu_library_tool')
    
    paragraph_styles = list(kupu.getParagraphStyles())
    
    new_styles = [('autoFlowPlayer video', 'Video|div'),
                  ('autoFlowPlayer video image-left', 'Video (left)|div'),
                  ('autoFlowPlayer video image-right', 'Video (right)|div'),
                  ('autoFlowPlayer audio', 'Audio|div'),
                  ('autoFlowPlayer audio image-left', 'Audio (left)|div'),
                  ('autoFlowPlayer audio image-right', 'Audio (right)|div')]
    to_add = dict(new_styles)
    
    for style in paragraph_styles:
        css_class = style.split('|')[-1]
        if css_class in to_add:
            del to_add[css_class]

    if to_add:
        paragraph_styles += ['%s|%s' % (v, k) for k,v in new_styles if k in to_add]
        kupu.configure_kupu(parastyles=paragraph_styles)
        
    # Define portal properties
    ptool = getToolByName(site, 'portal_properties')
    props = ptool.flowplayer_properties

    for prop in _PROPERTIES:
        if not props.hasProperty(prop['name']):
            props.manage_addProperty(prop['name'], prop['value'], prop['type_'])
    
