from zope.cachedescriptors import property
from zope.interface import alsoProvides, noLongerProvides
from zope.interface.interfaces import IInterface
from zope.component import getSiteManager

from collective.flowplayer.interfaces import IMediaInfo, IAudio, IVideo
from collective.flowplayer.metadata_extraction import parse_raw
from collective.flowplayer.metadata_extraction import scale_from_metadata

from Products.ATContentTypes import interface
from Products.Archetypes.interfaces import IObjectInitializedEvent

import urllib2
from StringIO import StringIO

VIDEO_EXTENSIONS = ['.f4b', '.f4p', '.f4v', '.flv', '.mp4', '.m4v', '.jpg', '.gif', '.png', '.mov']
AUDIO_EXTENSIONS = ['.mp3']

def is_flowplayer_installed(object):
    sm = getSiteManager(context=object)
    return sm.queryUtility(IInterface, name=u'collective.flowplayer.interfaces.IFlowPlayerSite', default=False)

def remove_marker(object):
    changed = False
    if IAudio.providedBy(object):
        noLongerProvides(object, IAudio)
        changed = True
    if IVideo.providedBy(object):
        noLongerProvides(object, IVideo)
        changed = True
    if changed:
        object.reindexObject(idxs=['object_provides'])

class ChangeView(object):

    interface = None
    value = None
    file_handle = None

    def __init__(self, object, event):
        self.object = object
        # TODO: do we really need this different from object?
        self.content = content = event.object

        if not is_flowplayer_installed(content): return
        if not self.interface.providedBy(content): return
        if self.value is None:
            remove_marker(content)
            return

        ext = self.check_extension()
        if ext is None:
            remove_marker(content)
            return

        # set the view to flowplayer view
        # TODO: give up automatic view changing - it causes problems when
        #       product is deinstalled. instead provide default views for
        #       the interfaces IAudio and IVideo in combination with
        #       IFileContent and IATLink
        if IObjectInitializedEvent.providedBy(event):
            content.setLayout('flowplayer')

        if ext in AUDIO_EXTENSIONS:
            self.handleAudio()
        elif ext in VIDEO_EXTENSIONS:
            self.handleVideo()

    def check_extension(self):
        for ext in AUDIO_EXTENSIONS + VIDEO_EXTENSIONS:
            if self.filename.endswith(ext):
                return ext
        return None

    def handleAudio(self):
        if not IAudio.providedBy(self.content):
            alsoProvides(self.content, IAudio)
            self.object.reindexObject(idxs=['object_provides'])

    def handleVideo(self):
        metadata = parse_raw(self.file_handle)
        height, width = scale_from_metadata(metadata)

        if not IVideo.providedBy(self.content):
            alsoProvides(self.content, IVideo)
            self.object.reindexObject(idxs=['object_provides'])

        if height and width:
            info = IMediaInfo(self.content)
            info.height = height
            info.width = width


class ChangeFileView(ChangeView):

    interface = interface.IFileContent

    @property.Lazy
    def value(self):
        return self.content.getField('file').getRaw(self.content)

    @property.Lazy
    def filename(self):
        filename = self.value.filename
        if isinstance(filename, basestring):
            filename = filename.lower()
        return filename

    @property.Lazy
    def file_handle(self):
        file_object = self.value
        try:
            # For blobs
            file_handle = file_object.getIterator()
        except AttributeError:
            file_handle = StringIO(str(file_object.data))
        return file_handle


class ChangeLinkView(ChangeView):

    interface = interface.IATLink

    @property.Lazy
    def value(self):
        return self.content.getRemoteUrl()

    @property.Lazy
    def filename(self):
        return self.value.lower()

    @property.Lazy
    def file_handle(self):
        try:
            file_handle = StringIO(str(urllib2.urlopen(self.value).read()))
        except IOError:
            file_handle = StringIO()
        return file_handle

