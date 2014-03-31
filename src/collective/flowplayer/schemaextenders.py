from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes.public import IntegerField, IntegerWidget
from collective.flowplayer.interfaces import IVideo
from collective.flowplayer import MessageFactory as _
from collective.flowplayer.interfaces import IMediaInfo


class _ExtensionWidthField(ExtensionField, IntegerField):
    def getAccessor(self, instance):
        def accessor(**kw):
            return IMediaInfo(instance).width
        return accessor

    def getEditAccessor(self, instance):
        def edit_accessor(**kw):
            return IMediaInfo(instance).width
        return edit_accessor

    def getMutator(self, instance):
        def mutator(value, **kw):
            try:
                value = int(value)
            except:
                value = None
            IMediaInfo(instance).width = value
        return mutator


class _ExtensionHeightField(ExtensionField, IntegerField):
    def getAccessor(self, instance):
        def accessor(**kw):
            return IMediaInfo(instance).height
        return accessor

    def getEditAccessor(self, instance):
        def edit_accessor(**kw):
            return IMediaInfo(instance).height
        return edit_accessor

    def getMutator(self, instance):
        def mutator(value, **kw):
            try:
                value = int(value)
            except:
                value = None
            IMediaInfo(instance).height = value
        return mutator


class VideoParameters(object):
    adapts(IVideo)
    implements(IOrderableSchemaExtender)

    fields = [
        _ExtensionWidthField(
            'width',
            schemata = 'Video',
            widget = IntegerWidget(
                label=_(u'Width'),
                description=_(u'You can override video width detected in video metadata. Leave empty to retreive width from metadata.'),
                size=6,
            ),
        ),
        _ExtensionHeightField(
            'height',
            schemata = 'Video',
            widget = IntegerWidget(
                label=_(u'Height'),
                description=_(u'You can override video height detected in video metadata. Leave empty to retreive height from metadata.'),
                size=6,
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, order):
        #default = order['default']
        #default.remove('queryParameters')
        #default.insert(default.index('remoteUrl')+1, 'queryParameters')
        return order
