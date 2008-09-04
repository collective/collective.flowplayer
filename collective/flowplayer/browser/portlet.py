import random

from zope.interface import implements
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from plone.memoize.instance import memoize
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from Products.ATContentTypes.interface import IATTopic, IATFolder
from collective.flowplayer.interfaces import IFLVVideo

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
                                                                                   IFLVVideo.__identifier__]},
                                                               default_query='path:'))

    random = schema.Bool(title=_(u"Select random items"),
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
    target =None
    random = False
    show_more = True

    def __init__(self, header=u"", target=None, random=False, show_more=True):
        self.header = header
        self.target = target
        self.random = random
        self.show_more = show_more

    @property
    def title(self):
        return self.header


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('portlet.pt')

    @property
    def available(self):
        return self.results() is not None

    def target_url(self):
        target = self.target()
        if target is None:
            return None
        else:
            return target.absolute_url()

    @memoize
    def results(self):
        target = self.target()
        catalog = getToolByName(self.context, 'portal_catalog')
        
        if target is None:
            return None
        
        results = []
        
        if IATTopic.providedBy(target):
            results = [dict(url=x.getURL(), title=x.Title, description=x.Description)
                        for x in target.queryCatalog()]
        elif IATFolder.providedBy(target):
            results = [dict(url=x.getURL(), title=x.Title, description=x.Description)
                        for x in catalog(object_provides=IFLVVideo.__identifier__,
                                 path = '/'.join(target.getPhysicalPath()),
                                 sort_on='getObjPositionInParent')]
            
        if results and self.data.random:
            return random.choice(results)
        elif results:
            return results[0]
    
        if not IFLVVideo.providedBy(target):
            return None
    
        return dict(url=target.absolute_url(),
                    title=target.Title(),
                    description=target.Description())
        
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
    
    label = _(u"Add Video Portlet")
    description = _(u"This portlet display a Flash Video")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(IVideoPortlet)
    form_fields['target'].custom_widget = UberSelectionWidget

    label = _(u"Edit Video Portlet")
    description = _(u"This portlet display a Flash video.")
