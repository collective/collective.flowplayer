from zope import interface
from zope import component
from Acquisition import aq_inner
import urllib
import os

try:
    # python2.6
    import json
except ImportError:
    # python2.4
    import simplejson as json

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

    def __call__(self, request=None, response=None):
        """ Returns global configuration of the Flowplayer taken from portal_properties """
        self.request.response.setHeader("Content-type", "text/javascript")
        data = dict(
            config=self.flowplayer_properties_as_dict,
            params=self.flash_properties_as_dict,
            loop=bool(self.flowplayer_properties.getProperty('loop')),
            )
        volume = self.flowplayer_properties.getProperty('initialVolumePercentage')
        if volume:
            data['initialVolumePercentage'] = int(volume)
        else:
            data['initialVolumePercentage'] = None
        return "var collective_flowplayer = %s;" % json.dumps(data, indent=2)


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

    def getFilename(self):
        context = aq_inner(self.context)
        return context.getFilename()

    def href(self):
        context = aq_inner(self.context)
        ext = ''
        url = self.context.absolute_url()
        filename = self.getFilename()
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
