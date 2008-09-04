from zope.interface import alsoProvides, noLongerProvides
from zope.annotation.interfaces import IAnnotations 

from collective.flowplayer.interfaces import IFLVVideo
from collective.flowplayer.flv import FLVHeader, FLVHeaderError

from Products.ATContentTypes.interface import IATFile
from Products.Archetypes.interfaces import IObjectInitializedEvent

ANNOTATIONS_KEY = "collective.flowplayer"

def remove_flv(object):
    if IFLVVideo.providedBy(object):
        noLongerProvides(object, IFLVVideo)
        object.reindexObject(idxs=['object_provides'])
        
def change_file_view(object, event):
    
    content = event.object
    if not IATFile.providedBy(content):
        return
    
    file = content.getField('file').getRaw(content)
    if file is None:
        remove_flv(content)
        return

    filename = file.filename
    if not filename or not filename.endswith('.flv'):
        remove_flv(content)
        return

    try:
        file = file.getIterator()
    except AttributeError:
        pass

    file.seek(0)
    
    flvparser = FLVHeader()
    try:
        flvparser.analyse(file.read(1024))
    except FLVHeaderError:
        remove_flv(content)
        return
    
    if IObjectInitializedEvent.providedBy(event):
        content.setLayout('flowplayer')
    
    if not IFLVVideo.providedBy(content):
        alsoProvides(content, IFLVVideo)
        object.reindexObject(idxs=['object_provides'])
    
    width = flvparser.getWidth()
    height = flvparser.getHeight()
    
    if height and width:
        annotations = IAnnotations(content)
        annotations["collective.flowplayer"] = {'height': height, 'width': width}