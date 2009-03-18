from zope.interface import Interface
from zope import schema

from collective.flowplayer import MessageFactory as _

class IFlowPlayerSite(Interface):
    """Marker interface for sites with this product installed"""

class IFlowPlayerView(Interface):
    """View for the flow player
    """
    
    def audio_only():
        """Return True if we are only showing audio files.
        """
    
    def scale():
        """Return a CSS/style snippet to encoding the height and width of
        the player.
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
    
class IMediaInfo(IVideo):
    """Information about a video object
    """
    
    audio_only = schema.Bool(title=u"Audio only?", required=True)
    
    width = schema.Int(title=_(u"Width"), required=False)
    height = schema.Int(title=_(u"Height"), required=False)