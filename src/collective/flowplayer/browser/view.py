from zope import interface
from zope import component
import simplejson
import urllib

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from collective.flowplayer.utils import properties_to_javascript

from collective.flowplayer.interfaces import IFlowPlayable
from collective.flowplayer.interfaces import IMediaInfo, IFlowPlayerView

from plone.memoize.instance import memoize

class JavaScript(BrowserView):
    
    def update(self):
        portal_url = getToolByName(self.context, 'portal_url')
        portal = portal_url.getPortalObject()
        
        properties_tool = getToolByName(self.context, 'portal_properties')
        flowplayer_properties = getattr(properties_tool, 'flowplayer_properties', None)
        
        portal_path = portal.absolute_url_path()
        if portal_path.endswith('/'):
            portal_path = portal_path[:-1]
        
        self.player = urllib.quote("%s/%s" % (portal_path, flowplayer_properties.getProperty('player'),))
        self.properties = properties_to_javascript(flowplayer_properties, portal, ignore=['title', 'player'], as_json_string=False)
    
    def __call__(self, request=None, response=None):
        self.update()
        self.request.response.setHeader("Content-type", "text/javascript")
        return """(function($) {
    var params = {src: "%(player)s"};
    function randomOrder() { return (Math.round(Math.random())-0.5); }
    function updateConfig(config, minimal, audio, splash) {
        if(minimal) {
            config.plugins.controls = null;
        } else if(audio) {
            config.plugins.controls = { fullscreen: false,
                                           width: 500 };
        }
        if(splash) {
            config.splashImageFile = splash;
        }
    }
    $(function() { 
        
        $('.autoFlowPlayer').each(function() {
            var config = %(properties)s;
            var minimal = $(this).is('.minimal');
            var audio = $(this).is('.audio');
            if (audio) {
                $(this).width(500);
            }
            var splash = null;
            
            var aTag = this;
            if(!$(aTag).is("a"))
                aTag = $(this).find("a").get(0);
            if(aTag == null)
                return;
            
            var img = $(this).find("img").get(0);
            if(img != null) {
                $(this).height($(img).height());
                $(this).width($(img).width());
                splash = $(img).attr('src');
            }
            
            updateConfig(config, minimal, audio, splash);
            if (!config.clip) {
                config.clip = {}
            }
            config.clip.url = $(aTag).attr('href');
            flashembed(this, params, {config:config});
            $('.flowPlayerMessage').remove();
        });
        
        $('.playListFlowPlayer').each(function() {
            var config = %(properties)s;
            var minimal = $(this).is('.minimal');
            var audio = $(this).is('.audio');
            var random = $(this).is('.random');
            var splash = null;
            
            var playList = new Array();
            $(this).find('a.playListItem').each(function() {
                playList.push({url: $(this).attr('href')});
            });
            
            var img = $(this).find("img").get(0);
            if(img != null) {
                splash = $(img).attr('src');
            }
            
            if(random) playList.sort(randomOrder);
            
            updateConfig(config, minimal, audio, splash);
            if (playList.length > 1) {
                config.plugins.controls.playlist = true
            }
            config.playlist = playList;
            flashembed(this, params, {config:config});
            $(this).show();
            $('.flowPlayerMessage').remove();
        });
    });
})(jQuery);
""" % dict(player=self.player, 
           properties=simplejson.dumps(self.properties, indent=4)
           )

class File(BrowserView):
    interface.implements(IFlowPlayerView)
    
    def __init__(self, context, request):
        super(File, self).__init__(context, request)
        
        self.info = IMediaInfo(self.context, None)
        
        self.height = self.info is not None and self.info.height or None
        self.width = self.info is not None and self.info.width or None
        self._audio_only = self.info is not None and self.info.audio_only or None
        
        if self.height and self.width:
            self._scale = "height: %dpx; width: %dpx;" % (self.height, self.width)
        else:
            self._scale = ""
    
    def audio_only(self):
        return self._audio_only
    
    def scale(self):
        return self._scale
    
    def videos(self):
        return[dict(url=self.context.absolute_url(),
                    title=self.context.Title(),
                    description=self.context.Description(),
                    height=self.height,
                    width=self.width,
                    audio_only=self._audio_only)]

    def href(self):
        return self.context.absolute_url()

class Link(File):

    def href(self):
        return self.context.getRemoteUrl()

class Folder(BrowserView):
    interface.implements(IFlowPlayerView)

    @memoize
    def audio_only(self):
        return len([v for v in self.videos() if not v['audio_only']]) == 0
    
    @memoize
    def scale(self):
        height = 0
        width = 0
        
        for video in self.videos():
            if video['height'] > height or video['width'] > width:
                height = video['height']
                width = video['width']
                
        if height and width:
            return "height: %dpx; width: %dpx;" % (height, width)
    
    @memoize
    def videos(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        results = []
        for brain in self._query():
            video = brain.getObject()
            if not IFlowPlayable.providedBy(video):
                continue
            view = component.getMultiAdapter(
                (video, self.request), interface.Interface, 'flowplayer')
            results.append(dict(url=view.href(),
                                title=brain.Title,
                                description=brain.Description,
                                height=view.height,
                                width=view.width,
                                audio_only=view.audio_only()))
        return results

    def _query(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(object_provides=IFlowPlayable.__identifier__,
                       path = {'depth': 1, 'query': '/'.join(self.context.getPhysicalPath())},
                       sort_on='getObjPositionInParent')

class Topic(Folder):
    interface.implements(IFlowPlayerView)
    
    def _query(self):
        return self.context.queryCatalog()
