from zope.interface import Interface
from zope import schema

from collective.flowplayer import MessageFactory as _

class IFlowPlayerView(Interface):
    """View for the flow player
    """
    
    def videos():
        """Return a list of dicts for videos to play, with keys url, title,
        description and scale.
        """

class IFlowPlayable(Interface):
    """A file playable in the flowplayer
    """

class IVideo(IFlowPlayable):
    """Marker interface for files that contain FLV content
    """
    
class IAudio(IFlowPlayable):
    """Marker interface for files that contain audio content
    """
    
class IVideoInfo(IVideo):
    """Information about a video object
    """
    
    width = schema.Int(title=_(u"Width"), required=False)
    height = schema.Int(title=_(u"Height"), required=False)