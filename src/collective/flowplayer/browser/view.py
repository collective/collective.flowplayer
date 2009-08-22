from zope import interface
from zope import component
from Acquisition import aq_inner
import simplejson
import urllib

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from collective.flowplayer.utils import properties_to_dict

from collective.flowplayer.interfaces import IFlowPlayable
from collective.flowplayer.interfaces import IMediaInfo, IFlowPlayerView

from plone.memoize.instance import memoize

class JavaScript(BrowserView):
    
    def update(self):
        portal_url = getToolByName(self.context, 'portal_url')
        portal = portal_url.getPortalObject()
        
        properties_tool = getToolByName(self.context, 'portal_properties')
        flowplayer_properties = getattr(properties_tool, 'flowplayer_properties', None)
        
        portal_url = portal.absolute_url()
        self.portal_url = portal_url
        self.player = flowplayer_properties.getProperty('player') \
                         .replace('${portal_url}', portal_url) \
                         .replace('${portal_path}', portal_url)
        self.properties = properties_to_dict(flowplayer_properties, 
                                             self.portal_url, 
                                             ignore=['title', 'player'])

    
    """
    Why there are two JS configuration files ? 
    We'd like to support flowplayer events in the future and events cannot be
    passed through flashvars (at least I don't know how). 
    Global configuration file is used to supply global player configuration
    including events (e.g. onBeforeFinish to support loop) but runtime
    configuration is used to fine-tune the particular player config, 
    eg. minimal or audio-only setup.
    """

    def global_config(self, request=None, response=None):
        """ Returns global configuration of the Flowplayer taken from portal_properties.
            If you want to customize flowplayer behaviour, override 
            collective.flowplayer.config.js from your product and return 
            flowplayer_config variable set to yoyr needs.
            Please note, runtime_config (collective.flowplayer.js) will be processed
            as well and config will be overriden (updated) - eg. playlist or clip url """
        self.update()
        self.request.response.setHeader("Content-type", "text/javascript")
        return """var flowplayer_config = %(properties)s
               """ % dict(properties=simplejson.dumps(self.properties, indent=4))

    def runtime_config(self, request=None, response=None):
        """ Returns global configuration of the Flowplayer taken from portal_properties """
        self.update()
        self.request.response.setHeader("Content-type", "text/javascript")
        return """(function($) {
        $(function() { 

        function randomOrder() { return (Math.round(Math.random())-0.5); }
        
        // thanks: http://keithdevens.com/weblog/archive/2007/Jun/07/javascript.clone
        function clone(obj) {   
            if (!obj || typeof obj != 'object') { return obj; }     
            var temp = new obj.constructor();   
            for (var key in obj) {  
                if (obj.hasOwnProperty(key)) {
                    temp[key] = clone(obj[key]);
                }
            }       
            return temp;
        }
        function updateConfig(config, minimal, audio) {
            if(minimal) {
                config.plugins.controls = null;
            } else if(audio) {
                config.plugins.controls = { fullscreen: false,
                                               width: 500 };
            }
        }
        $('.autoFlowPlayer').each(function() {
            var config = clone(flowplayer_config);
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
            
            updateConfig(config, minimal, audio);
            if (!config.clip) {
                config.clip = {}
            }
            config.clip.url = $(aTag).attr('href');
                        
            updateConfig(config, minimal, audio);
            flowplayer(aTag, "%(player)s", config);
            $('.flowPlayerMessage').remove();
        });
        
        $('.playListFlowPlayer').each(function() {
            var config = clone(flowplayer_config);
            var minimal = $(this).is('.minimal');
            var audio = $(this).is('.audio');
            var random = $(this).is('.random');
            var splash = null;
            
            var playList = new Array();
            $(this).find('a.playListItem').each(function() {
                playList.push({url: $(this).attr('href')});
                $(this).remove()  // player container must be empty or contain image only
            });
            
            if(random) playList.sort(randomOrder);
            
            updateConfig(config, minimal, audio);
            if (playList.length > 1) {
                config.plugins.controls.playlist = true
            }
            config.playlist = playList;
            flowplayer(this, "%(player)s", config);
            $(this).show();
            $('.flowPlayerMessage').remove();
        });
    });
})(jQuery);
""" % dict(player = self.player)


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
