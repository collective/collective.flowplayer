from zope.interface import alsoProvides, noLongerProvides

from collective.flowplayer.interfaces import IMediaInfo, IAudio, IVideo
from collective.flowplayer.flv import FLVHeader, FLVHeaderError

from Products.ATContentTypes.interface import IATFile
from Products.Archetypes.interfaces import IObjectInitializedEvent

from StringIO import StringIO

EXTENSIONS = ['.flv',
              '.mp3']

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

def check_extension(filename):
    filename = filename.lower()
    for ext in EXTENSIONS:
        if filename.endswith(ext):
            return ext
    return None

def change_file_view(object, event):
    
    content = event.object
    if not IATFile.providedBy(content):
        return
    
    file_object = content.getField('file').getRaw(content)
    if file_object is None:
        remove_marker(content)
        return
    
    ext = check_extension(file_object.filename)
    if ext is None:
        remove_marker(content)
        return

    if IObjectInitializedEvent.providedBy(event):
        content.setLayout('flowplayer')

    if ext == '.mp3':
        if not IAudio.providedBy(content):
            alsoProvides(content, IAudio)
            object.reindexObject(idxs=['object_provides'])
    elif ext == '.flv':
        
        try:
            # For blobs
            file_handle = file_object.getIterator()
        except AttributeError:
            file_handle = StringIO(str(file_object.data))

        file_handle.seek(0)
        flvparser = FLVHeader()
        try:
            flvparser.analyse(file_handle.read(1024))
        except FLVHeaderError:
            remove_marker(content)
            return
    
        if not IVideo.providedBy(content):
            alsoProvides(content, IVideo)
            object.reindexObject(idxs=['object_provides'])

        width = flvparser.getWidth()
        height = flvparser.getHeight()
    
        if height and width:
            info = IMediaInfo(content)
            info.height = height
            info.width = width