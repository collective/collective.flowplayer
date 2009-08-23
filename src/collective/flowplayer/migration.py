# Migration utilities and migration steps
from Products.CMFCore.utils import getToolByName

# oldProperty: newProperty. do not properties which name is not changed (e.g. player)
V30_PROPERTIES_MAPPING = {
    'autoPlay'          : 'clip/autoPlay',
    'autoBuffering'     : 'clip/autoBuffering',
    'initialScale'      : 'clip/scaling',
    'showVolumeSlider'  : 'plugins/controls/volume',
    'controlBarBackgroundColor' : 'plugins/controls/backgroundColor',
}

def migrateTo30(context):
    properties_tool = getToolByName(context, 'portal_properties', None)
    if properties_tool is not None:
        flowplayer_properties = getattr(properties_tool, 'flowplayer_properties', None)
        if flowplayer_properties:
            for k, v in V30_PROPERTIES_MAPPING.items():
                if flowplayer_properties.hasProperty(k) and flowplayer_properties.hasProperty(v):
                        # has both old and new property. This is after installation, without
                        # migration run. Migrate!
                        flowplayer_properties._updateProperty(v, flowplayer_properties.getProperty(k))
                        flowplayer_properties.manage_delProperties([k])
                # ignore any other combinations, because these are not expected

# <!-- NOT YET FIXED properties
# <property name="usePlayOverlay" type="boolean">True</property>
# <property name="useNativeFullScreen" type="boolean">True</property>
# <property name="controlsOverVideo" type="string">ease</property>
# <property name="controlBarGloss" type="string">low</property> -->            
