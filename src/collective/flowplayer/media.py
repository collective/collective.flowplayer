from persistent import Persistent

from zope.interface import implements
from zope.component import adapts

from zope.annotation.interfaces import IAnnotatable
from zope.annotation import factory

from collective.flowplayer.interfaces import IVideo, IAudio, IMediaInfo

class VideoInfo(Persistent):
    implements(IMediaInfo)
    adapts(IVideo)
    
    def __init__(self):
        self.height = None
        self.width = None
        self.audio_only = False

VideoInfoAdapter = factory(VideoInfo)

class AudioInfo(object):
    implements(IMediaInfo)
    adapts(IAudio)
    
    def __init__(self, context):
        self.audio_only = True
        self.width = None
        self.height = None