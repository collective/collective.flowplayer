from Products.CMFCore.utils import getToolByName
from collective.flowplayer.interfaces import IFlowPlayerSite
from zope.interface.interfaces import IInterface
from zope.component import getSiteManager

def uninstall(self):
    portal = self
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-collective.flowplayer:uninstall')


    # Remove portal properties
    ptool = getToolByName(portal, 'portal_properties')
    if ptool.get('flowplayer_properties', None):
        del ptool['flowplayer_properties']

    kupu = getToolByName(portal, 'kupu_library_tool', None)
    if kupu is not None:
        paragraph_styles = list(kupu.getParagraphStyles())
    
        new_styles = [('autoFlowPlayer video', 'Video|div'),
                      ('autoFlowPlayer video image-left', 'Video (left)|div'),
                      ('autoFlowPlayer video image-right', 'Video (right)|div'),
                      ('autoFlowPlayer audio', 'Audio|div'),
                      ('autoFlowPlayer audio image-left', 'Audio (left)|div'),
                      ('autoFlowPlayer audio image-right', 'Audio (right)|div')]
        fp_styles = dict(new_styles)
        fixed_styles = []
        for style in paragraph_styles:
            css_class = style.split('|')[-1]
            if css_class not in fp_styles:
                fixed_styles.append(style)

        kupu.configure_kupu(parastyles=fixed_styles)
        
    # remove collective.flowplayer.interfaces.IFlowPlayerSite utility
    sm = getSiteManager(context=portal)
    if sm.queryUtility(IInterface, name=u'collective.flowplayer.interfaces.IFlowPlayerSite', default=False):
        sm.unregisterUtility(component=IFlowPlayerSite, provided=IInterface, name=u'collective.flowplayer.interfaces.IFlowPlayerSite')
    return "Ran all uninstall steps."
