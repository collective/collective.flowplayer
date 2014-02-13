from Products.CMFCore.utils import getToolByName
from zope.interface.interfaces import IInterface
from zope.component import getSiteManager
from collective.flowplayer.interfaces import IFlowPlayerSite
from collective.flowplayer.interfaces import IAudio, IVideo
from collective.flowplayer.events import remove_marker


def profile(context):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile(
        'profile-collective.flowplayer:uninstall')


def properties(context):
    ptool = getToolByName(context, 'portal_properties')
    if ptool.get('flowplayer_properties', None):
        del ptool['flowplayer_properties']


def kupu(context):
    kupu = getToolByName(context, 'kupu_library_tool', None)
    if kupu is not None:
        paragraph_styles = list(kupu.getParagraphStyles())

        new_styles = [
            ('autoFlowPlayer video', 'Video|div'),
            ('autoFlowPlayer video image-left', 'Video (left)|div'),
            ('autoFlowPlayer video image-right', 'Video (right)|div'),
            ('autoFlowPlayer audio', 'Audio|div'),
            ('autoFlowPlayer audio image-left', 'Audio (left)|div'),
            ('autoFlowPlayer audio image-right', 'Audio (right)|div')
        ]
        fp_styles = dict(new_styles)
        fixed_styles = []
        for style in paragraph_styles:
            css_class = style.split('|')[-1]
            if css_class not in fp_styles:
                fixed_styles.append(style)

        kupu.configure_kupu(parastyles=fixed_styles)


def utility(portal):
    sm = getSiteManager(context=portal)
    name = u'collective.flowplayer.interfaces.IFlowPlayerSite'
    if sm.queryUtility(IInterface, name=name, default=False):
        sm.unregisterUtility(component=IFlowPlayerSite, provided=IInterface,
                             name=name)


def views(portal):
    catalog = getToolByName(portal, 'portal_catalog')
    types = getToolByName(portal, 'portal_types')
    for brain in catalog(object_provides=[
            IAudio.__identifier__, IVideo.__identifier__]):
        ob = brain.getObject()
        if ob.getLayout() == 'flowplayer':
            type_ = types[ob.portal_type]
            ob.setLayout(type_.default_view)

    for type_name in ('File', 'Link', 'Folder', 'Topic', 'Collection'):
        if type_name in types.objectIds():
            type_ = types[type_name]
            view_methods = list(type_.view_methods)
            if 'flowplayer' in view_methods:
                view_methods.remove('flowplayer')
                type_.view_methods = tuple(view_methods)


def interfaces(portal):
    catalog = getToolByName(portal, 'portal_catalog')
    for brain in catalog(object_provides=[
            IAudio.__identifier__, IVideo.__identifier__]):
        ob = brain.getObject()
        remove_marker(ob)


def all(portal):
    profile(portal)
    properties(portal)
    kupu(portal)
    utility(portal)
    views(portal)
    interfaces(portal)
