from zope.cachedescriptors import property
from zope.interface import alsoProvides, noLongerProvides
from zope.interface.interfaces import IInterface
from zope.component import getSiteManager

from collective.flowplayer.interfaces import IMediaInfo, IAudio, IVideo
from collective.flowplayer.flv import FLVHeader, FLVHeaderError

from Products.ATContentTypes import interface
from Products.Archetypes.interfaces import IObjectInitializedEvent

import urllib2
from StringIO import StringIO

VIDEO_EXTENSIONS = ['.f4b', '.f4p', '.f4v', '.flv', '.mp4', '.m4v', '.jpg', '.gif', '.png']
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

    @property.Lazy
    def value(self):
        return self.content.getField('file').getRaw(self.content)

    def handleAudio(self):
        if not IAudio.providedBy(self.content):
            alsoProvides(self.content, IAudio)
            self.object.reindexObject(idxs=['object_provides'])

    def __init__(self, object, event):
        self.object = object
        # TODO: do we really need this different from object?
        self.content = content = event.object

        if not is_flowplayer_installed(content):
            return

        if not self.interface.providedBy(content):
            return

        if self.value is None:
            remove_marker(content)
            return

        ext = self.check_extension()
        if ext is None:
            remove_marker(content)
            return

        if IObjectInitializedEvent.providedBy(event):
            content.setLayout('flowplayer')

        if ext in AUDIO_EXTENSIONS:
            self.handleAudio()
        elif ext in VIDEO_EXTENSIONS:
            self.handleVideo()

    def handleVideo(self):
        if not IVideo.providedBy(self.content):
            alsoProvides(self.content, IVideo)
            self.object.reindexObject(idxs=['object_provides'])

class ChangeFileView(ChangeView):

    interface = interface.IFileContent

    def check_extension(self):
        filename = self.value.filename.lower()
        for ext in AUDIO_EXTENSIONS + VIDEO_EXTENSIONS:
            if filename.endswith(ext):
                return ext
        return None

    def handleVideo(self):
        file_object = self.value
        try:
            # For blobs
            file_handle = file_object.getIterator()
        except AttributeError:
            file_handle = StringIO(str(file_object.data))

        file_handle.seek(0)
        height = width = None
        flvparser = FLVHeader()
        try:
            flvparser.analyse(file_handle.read(1024))
            width = flvparser.getWidth()
            height = flvparser.getHeight()
        except FLVHeaderError:
            # Do not remove marker interface. MP4 files can't be parsed 
            # but works fine. Any file which extension is in allowed 
            # extensions should be playable (hopefully)
            # remove_marker(self.content)
            # return
            pass

        super(ChangeFileView, self).handleVideo()

        if height and width:
            info = IMediaInfo(self.content)
            info.height = height
            info.width = width

class ChangeLinkView(ChangeView):

    interface = interface.IATLink

    @property.Lazy
    def value(self):
        return self.content.getField('remoteUrl').getRaw(self.content)

    def check_extension(self):
        filename = self.value.lower()
        for ext in AUDIO_EXTENSIONS + VIDEO_EXTENSIONS:
            if filename.endswith(ext):
                return ext
        return None

    def handleVideo(self):
        try:
            file_handle = urllib2.urlopen(self.content.getRemoteUrl())
        except IOError:
            file_handle = StringIO()
        height = width = None
        flvparser = FLVHeader()
        try:
            flvparser.analyse(file_handle.read(1024))
            width = flvparser.getWidth()
            height = flvparser.getHeight()
        except FLVHeaderError:
            # Do not remove marker interface. MP4 files can't be parsed 
            # but works fine. Any file which extension is in allowed 
            # extensions should be playable (hopefully)
            # remove_marker(self.content)
            # return
            pass

        super(ChangeLinkView, self).handleVideo()

        if height and width:
            info = IMediaInfo(self.content)
            info.height = height
            info.width = width
