from zope.interface import implements
from zope.component import getMultiAdapter, queryMultiAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
import urllib
import random
from zope import schema
from zope.formlib import form

from plone.memoize.instance import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from Products.ATContentTypes.interface import IATTopic, IATFolder, IATImage

from collective.flowplayer.interfaces import IFlowPlayable
from collective.flowplayer.interfaces import IFlowPlayerView
from collective.flowplayer import MessageFactory as _

from Products.CMFCore.utils import getToolByName

class IVideoPortlet(IPortletDataProvider):
    """A portlet which can display videos
    """

    header = schema.TextLine(title=_(u"Portlet header"),
                             description=_(u"Title of the rendered portlet"),
                             required=True)

    target = schema.Choice(title=_(u"Target object"),
                           description=_(u"This can be a file containing an FLV file, or a folder or collection containing FLV files"),
                           required=True,
                           source=SearchableTextSourceBinder({'object_provides' : [IATTopic.__identifier__,
                                                                                   IATFolder.__identifier__,
                                                                                   IFlowPlayable.__identifier__]},
                                                               default_query='path:'))
                                                               
    splash = schema.Choice(title=_(u"Splash image"),
                           description=_(u"An image file to use as a splash image"),
                           required=False,
                           source=SearchableTextSourceBinder({'object_provides' : [IATImage.__identifier__, IATFolder.__identifier__,]},
                                                               default_query='path:'))

    limit = schema.Int(title=_(u"Number of videos to show"),
                       description=_(u"Enter a number greater than 0 to limit the number of items displayed"),
                       required=False)
    
    random = schema.Bool(title=_(u"Randomise the playlist"),
                         description=_(u"If enabled, a random video from the selection will be played."),
                         required=True,
                         default=False)
                       
    show_more = schema.Bool(title=_(u"Show more... link"),
                       description=_(u"If enabled, a more... link will appear in the footer of the portlet, "
                                      "linking to the underlying data."),
                       required=True,
                       default=True)

class Assignment(base.Assignment):
    implements(IVideoPortlet)

    header = u""
    target = None
    splash = None
    limit = None
    random = False
    show_more = True

    def __init__(self, header=u"", target=None, splash=None, limit=None, random=False, show_more=True):
        self.header = header
        self.target = target
        self.splash = splash
        self.limit = limit
        self.random = random
        self.show_more = show_more

    @property
    def title(self):
        return self.header

class Renderer(base.Renderer):
    render = ViewPageTemplateFile('portlet.pt')

    @property
    def available(self):
        return len(self.videos()) > 0

    def target_url(self):
        target = self.target()
        if target is None:
            return None
        else:
            return target.absolute_url()
    
    @memoize
    def splash(self):
        splash_path = self.data.splash
        if not splash_path:
            return None

        if splash_path.startswith('/'):
            splash_path = splash_path[1:]
        
        if not splash_path:
            return None

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        splash = portal.restrictedTraverse(splash_path, default=None)
        
        if splash is not None and not IATImage.providedBy(splash):
            return None
        
        return splash

    @memoize
    def videos(self):
        
        target = self.target()
        catalog = getToolByName(self.context, 'portal_catalog')
        
        if target is None:
            return []
        
        view = queryMultiAdapter((target, self.request), name=u"flowplayer")
        if view is None or not IFlowPlayerView.providedBy(view):
            return []
            
        videos = view.videos()
        
        limit = self.data.limit
        if limit:
            result = videos[:limit]
        else:
            result = videos

        if self.data.random:
            random.shuffle(result)
        return result


    def first_clip_url(self):
        """ Clip must be quoted to playlist is able to find it in the flowplayer-playlist onBegin/getEl method call """
        videos = self.videos()
        if videos:
            return urllib.quote(videos[0].get('url'))
        else:
            return None
            
    @memoize
    def audio_only(self):
        target = self.target()
        view = queryMultiAdapter((target, self.request), name=u"flowplayer")
        if view is None or not IFlowPlayerView.providedBy(view):
            return False
        return view.audio_only()
        
    @memoize
    def scale(self):
        target = self.target()
        view = queryMultiAdapter((target, self.request), name=u"flowplayer")
        if view is None or not IFlowPlayerView.providedBy(view):
            return False
        return view.scale()

    @memoize
    def target(self):
        target_path = self.data.target
        if not target_path:
            return None

        if target_path.startswith('/'):
            target_path = target_path[1:]
        
        if not target_path:
            return None

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        return portal.restrictedTraverse(target_path, default=None)
        
class AddForm(base.AddForm):
    form_fields = form.Fields(IVideoPortlet)
    form_fields['target'].custom_widget = UberSelectionWidget
    form_fields['splash'].custom_widget = UberSelectionWidget
    
    label = _(u"Add Video Portlet")
    description = _(u"This portlet display a Flash Video")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(IVideoPortlet)
    form_fields['target'].custom_widget = UberSelectionWidget
    form_fields['splash'].custom_widget = UberSelectionWidget

    label = _(u"Edit Video Portlet")
    description = _(u"This portlet display a Flash video.")
