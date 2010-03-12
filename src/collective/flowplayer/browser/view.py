from zope import interface
from zope import component
from Acquisition import aq_inner
import simplejson
import urllib
import os 

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from collective.flowplayer.utils import properties_to_dict, \
                                        flash_properties_to_dict

from collective.flowplayer.interfaces import IFlowPlayable
from collective.flowplayer.interfaces import IMediaInfo, IFlowPlayerView

from plone.memoize.instance import memoize
from plone.memoize import view

class JavaScript(BrowserView):
    
    @view.memoize_contextless
    def portal_state(self):
        """ returns 
            http://dev.plone.org/plone/browser/plone.app.layout/trunk/plone/app/layout/globals/portal.py
        """
        return component.getMultiAdapter((self.context, self.request), name=u"plone_portal_state")

    @property
    def flowplayer_properties(self):
        properties_tool = getToolByName(self.context, 'portal_properties')
        return getattr(properties_tool, 'flowplayer_properties', None)

    @property
    def flowplayer_properties_as_dict(self):
        portal_url = self.portal_state().portal_url()
        return properties_to_dict(self.flowplayer_properties, 
                                  portal_url, 
                                  ignore=['title', 
                                          'loop',
                                          'initialVolumePercentage',
                                          'showPlaylist',])

    @property
    def flash_properties_as_dict(self):
        portal_url = self.portal_state().portal_url()
        return flash_properties_to_dict(self.flowplayer_properties, 
                                        portal_url)

    def update(self):
        portal_url = self.portal_state().portal_url()
        if not portal_url.endswith('/'):
            portal_url += '/'

        # if showPlaylist is True, do not show playlist buttons on controlbar
        self.show_cb_playlist_buttons = not self.flowplayer_properties.getProperty('showPlaylist')
        # build string in Javascript format which is appended to the player
        # It contains javascript events which can't be configured in the 
        # self.properties, because simplejson can't handle them
        self.events = ''
        volume = self.flowplayer_properties.getProperty('initialVolumePercentage')
        if volume:
            self.events += '.onLoad( function() { this.setVolume(%d); })' % volume
        if self.flowplayer_properties.getProperty('loop'):
            self.events += '.onBeforeFinish( function() { return false; })'

        
    def __call__(self, request=None, response=None):
        """ Returns global configuration of the Flowplayer taken from portal_properties """
        self.update()
        self.request.response.setHeader("Content-type", "text/javascript")
            
        return """(function($) {
        $(function() { 
            $('.autoFlowPlayer').each(function() {
                var config = %(config)s;
                var $self = $(this);
                if ($self.is('.minimal')) { 
                    config.plugins.controls = null; 
                };
                var audio = $self.is('.audio');
                if (audio && !$self.is('.minimal')) {
                    if ($self.is('.image-left') || $self.is('.image-right'))
                        $self.width(230)
                    else
                        $self.width(500);
                    config.plugins.controls.all = false;
                    config.plugins.controls.play = true;
                    config.plugins.controls.scrubber = true;
                    config.plugins.controls.mute = true;
                    config.plugins.controls.volume = true;
                    config.plugins.controls.time = true;
                }
                if ($self.is('div')) {
                    // comming from Kupu, there are relative urls
                    config.clip.baseUrl = $('base').attr('href');
                    config.clip.url = $self.find('a').attr('href');
                    if (audio) {
                      // force .mp3 extension
                      config.clip.url = config.clip.url + '?e=.mp3';
                    };
                    // Ignore global autoplay settings
                    if ($self.find('img').length == 0) {
                        // no image. Don't autoplay, remove all elements inside the div to show player directly.
                        config.clip.autoPlay = false;
                        $self.empty();
                    } else {
                        // Clip is probably linked as image, so autoplay the clip after image is clicked
                        config.clip.autoPlay = true;
                    }
                }
                flowplayer(this, %(params)s, config)%(events)s;
                $('.flowPlayerMessage').remove();
            });
            $('.playListFlowPlayer').each(function() {
                var config = %(config)s;
                var $self = $(this);
                var audio = $self.is('.audio');
                if (audio) { config.plugins.controls.fullscreen = false; }
                if ($self.is('.minimal')) { config.plugins.controls = null; }
                if ($self.find('img').length > 0) { 
                    // has splash
                    config.clip.autoPlay = true;
                }
                portlet_parents = $self.parents('.portlet');
                var playlist_selector = 'div#flowPlaylist';
                if (portlet_parents.length > 0) {
                    var portlet = true;
                    // playlist has to be bound to unique item
                    playlist_selector_id = portlet_parents.parent().attr('id')+'-playlist';
                    $self.parent().find('.flowPlaylist-portlet-marker').attr('id', playlist_selector_id);
                    playlist_selector = '#'+playlist_selector_id;
                    if (audio && !$self.is('.minimal')) {
                        config.plugins.controls.all = false;
                        config.plugins.controls.play = true;
                        config.plugins.controls.scrubber = true;
                        config.plugins.controls.mute = true;
                        config.plugins.controls.volume = false;
                    }
                } else {
                    var portlet = false;
                }
                if (!portlet) {
                    $("#pl").scrollable({items:playlist_selector, size:4, clickable:false});
                }
                // manual = playlist is setup using HTML tags, not using playlist array in config
                flowplayer(this, %(params)s, config).playlist(playlist_selector, {loop: true, manual: true})%(events)s;
                $self.show();
                $('.flowPlayerMessage').remove();

            });
        });
})(jQuery);
""" % dict(params = simplejson.dumps(self.flash_properties_as_dict),
           config = simplejson.dumps(self.flowplayer_properties_as_dict, indent=4),
           events = self.events,
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
        return[dict(url=self.href(),
                    title=self.context.Title(),
                    description=self.context.Description(),
                    height=self.height,
                    width=self.width,
                    audio_only=self._audio_only)]

    def href(self):
        context = aq_inner(self.context)
        ext = ''
        url = self.context.absolute_url()
        filename = context.getFilename()
        if filename:
            extension = os.path.splitext(filename)[1]
            if not url.endswith(extension):
                ext = "?e=%s" % extension
        return self.context.absolute_url()+ext

class Link(File):

    def href(self):
        return self.context.getRemoteUrl()

class Folder(BrowserView):
    interface.implements(IFlowPlayerView)
    
    @memoize
    def playlist_class(self):
        properties_tool = getToolByName(self.context, 'portal_properties')
        props = getattr(properties_tool, 'flowplayer_properties', None)
        return props.getProperty('showPlaylist') and 'flowPlaylistVisible' or 'flowPlaylistHidden'
        
    @memoize
    def audio_only(self):
        return len([v for v in self.videos() if not v['audio_only']]) == 0
    
    @memoize
    def scale(self):
        height = 0
        width = 0
        if self.audio_only():
            height = 27
            width = 400
        
        for video in self.videos():
            if video['height'] > height or video['width'] > width:
                height = video['height']
                width = video['width']
                
        if height and width:
            return "height: %dpx; width: %dpx;" % (height, width)
    
    @memoize
    def videos(self):
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

    def first_clip_url(self):
        """ Clip must be quoted to playlist is able to find it in the flowplayer-playlist onBegin/getEl method call """
        videos = self.videos()
        if videos:
            return urllib.quote(videos[0].get('url'))
        else:
            return None
    
    def _query(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(object_provides=IFlowPlayable.__identifier__,
                       path = {'depth': 1, 'query': '/'.join(self.context.getPhysicalPath())},
                       sort_on='getObjPositionInParent')

class Topic(Folder):
    interface.implements(IFlowPlayerView)
    
    def _query(self):
        return self.context.queryCatalog()
