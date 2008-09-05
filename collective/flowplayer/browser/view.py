from zope.interface import implements
from zope.annotation.interfaces import IAnnotations

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from collective.flowplayer.utils import properties_to_javascript

from collective.flowplayer.interfaces import IFlowPlayable, IVideo, IAudio
from collective.flowplayer.interfaces import IVideoInfo, IFlowPlayerView

class Base(BrowserView):
    
    def update(self):
        portal_url = getToolByName(self.context, 'portal_url')
        portal = portal_url.getPortalObject()
        
        properties_tool = getToolByName(self.context, 'portal_properties')
        flowplayer_properties = getattr(properties_tool, 'flowplayer_properties', None)
        
        portal_path = portal.absolute_url_path()
        if portal_path.endswith('/'):
            portal_path = portal_path[:-1]
        
        self.player = "%s/%s" % (portal_path, flowplayer_properties.getProperty('player'),)
        self.properties = properties_to_javascript(flowplayer_properties, portal, ignore=['title', 'player'])

    def __call__(self):
        self.update()
        return self.index()

class JavaScript(Base):
    
    def __call__(self):
        self.update()
        self.request.response.setHeader("Content-type", "text/javascript")
        return """
(function($) {
    var params = {src: "%(player)s"};
    function randomOrder() { return (Math.round(Math.random())-0.5); }
    $(function() { 
        $('.autoFlowPlayer').each(function() {
            var config = %(properties)s;
            var aTag = this;
            if(!$(aTag).is("a"))
                aTag = $(this).find("a").get(0);
            config.videoFile = aTag.href;
            var img = $(this).find("img").get(0);
            if(img != null) {
                $(this).height($(img).height());
                $(this).width($(img).width());
                config.splashImageFile = $(img).attr('src');
            }
            flashembed(this, params, {config:config});
            $('.flowPlayerMessage').remove();
        });
        $('.playListFlowPlayer').each(function() {
            var config = %(properties)s;
            var playList = new Array();
            var size = null;
            $('a.playListItem', this).each(function() {
                playList.push({url: $(this).attr('href')});
                if(!size) size = $(this).attr('style');
            });
            if($(this).is(".random")) playList.sort(randomOrder);
            if(size) $(this).attr('style', size);
            if($(this).is(".minimal")) {
                if(playList.length == 1) {
                    config.hideControls = true;
                } else {
                    config.showFullScreenButton = false;
                    config.showStopButton = false;
                    config.showVolumeSlider = false;
                    config.showScrubber = false;
                    config.showMenu = false;
                    config.usePlayOverlay = false;
                }
            }
            config.playList = playList;
            flashembed(this, params, {config:config});
            $(this).show();
            $('.flowPlayerMessage').remove();
        });
    });
})(jQuery);
""" % dict(player=self.player, properties=self.properties)

class File(Base):
    implements(IFlowPlayerView)
    
    def videos(self):
        return[dict(url=self.context.absolute_url(),
                    title=self.context.Title(),
                    description=self.context.Description(),
                    scale=self.scale())]
    
    def scale(self):
        info = IVideoInfo(self.context, None)
        if info is None:
            return None
        height, width = info.height, info.width
        if not height or not width:
            return None
        return "height: %dpx; width: %dpx;" % (height, width)

class Folder(Base):
    implements(IFlowPlayerView)

    def videos(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        results = []
        for brain in catalog(object_provides=IFlowPlayable.__identifier__,
                             path = {'depth': 1, 'query': '/'.join(self.context.getPhysicalPath())},
                             sort_on='getObjPositionInParent'):
            video = brain.getObject()
            info = IVideoInfo(video, None)
            scale = None
            if info is not None and info.height and info.width:
                scale = "height: %dpx; width: %dpx;" % (info.height, info.width)
            results.append(dict(url=brain.getURL(),
                                title=brain.Title,
                                description=brain.Description,
                                scale=scale))
        return results

class Topic(Folder):
    implements(IFlowPlayerView)
    
    def videos(self):
        results = []
        for brain in self.context.queryCatalog():
            video = brain.getObject()
            if not IFlowPlayable.providedBy(video):
                continue
            info = IVideoInfo(video, None)
            scale = None
            if info is not None and info.height and info.width:
                scale = "height: %dpx; width: %dpx;" % (info.height, info.width)
            results.append(dict(url=brain.getURL(),
                                title=brain.Title,
                                description=brain.Description,
                                scale=scale))
        return results