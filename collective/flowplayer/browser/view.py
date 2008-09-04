from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from collective.flowplayer.utils import properties_to_javascript

from collective.flowplayer.interfaces import IFLVVideo

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
        self.properties = properties_to_javascript(flowplayer_properties, ignore=['title', 'player'])

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
    var config = %(properties)s;
    $(document).ready(function() { 
        $('a.flowplayer').each(function() {
            config.videoFile = $(this).attr("href");
            var player = flashembed(this, params, {config:config});
            $(this).append($("<div/>").addClass('playButton'));
        });
    });
})(jQuery);
""" % dict(player=self.player, properties=self.properties)

class File(Base):
    pass

class Folder(Base):

    def js(self):
        return """\
(function($) {
    
    var params = {src: "%(player)s"};
    var config = %(properties)s;
    var player = null;
    
    $(document).ready(function() { 
        $('a#player').each(function() {
            config.videoFile = $(this).attr("href");
            player = flashembed(this, params, {config:config});
            $(this).append($("<div/>").addClass('playButton'));
        });
        
        $('#playlist a').click(function() {
            player.DoStop();
            $('#playerTitle').html($(this).text());
            $('#player').attr('href', $(this).attr('href'));
            config.videoFile = $(this).attr('href');
            player.setConfig(config);
            player.DoPlay();
            
            return false;
        });
        
    });
})(jQuery);
""" % dict(player=self.player, properties=self.properties)
    
    def videos(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return list(catalog(object_provides=IFLVVideo.__identifier__,
                            path = {'depth': 1, 'query': '/'.join(self.context.getPhysicalPath())},
                            sort_on='getObjPositionInParent'))

class Topic(Folder):
    
    def videos(self):
        return list(self.context.queryCatalog())