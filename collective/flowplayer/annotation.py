from persistent import Persistent

from zope.interface import implements
from zope.component import adapts

from zope.annotation.interfaces import IAnnotatable
from zope.annotation import factory

from collective.flowplayer.interfaces import IVideo, IVideoInfo

class VideoInfo(Persistent):
    implements(IVideoInfo)
    adapts(IVideo)
    
    def __init__(self):
        self.height = None
        self.width = None

VideoInfoAdapter = factory(VideoInfo)