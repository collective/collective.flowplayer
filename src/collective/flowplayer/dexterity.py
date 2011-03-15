from zope.annotation import IAnnotations
from zope.interface import implements
from zope.interface import implementer
from plone.rfc822.interfaces import IPrimaryFieldInfo
from collective.flowplayer.browser.view import File as FileViewBase
from collective.flowplayer.events import VIDEO_EXTENSIONS
from collective.flowplayer.events import AUDIO_EXTENSIONS
from collective.flowplayer.metadata_extraction import parse_raw
from collective.flowplayer.metadata_extraction import scale_from_metadata
from collective.flowplayer.interfaces import IMediaInfo

MEDIA_INFO_KEY = "collective.flowplayer:mediainfo"

class MediaInfo(object):
    implements(IMediaInfo)

    def __init__(self, width=None, height=None, audio_only=True, **kw):
        self.width = width
        self.height = height
        self.audio_only = audio_only


@implementer(IMediaInfo)
def get_media_info(context):
    anno = IAnnotations(context)
    data = anno.get(MEDIA_INFO_KEY)
    if data is None:
        return None
    return MediaInfo(**data)

def update_media_info(context, event):
    info = IPrimaryFieldInfo(context)
    anno = IAnnotations(context)
    ext = None
    if info.value is not None:
        parts = info.value.filename.rsplit('.', 1)
        if len(parts) == 2:
            ext = '.' + parts[1]
    if ext in AUDIO_EXTENSIONS:
        anno[MEDIA_INFO_KEY] = dict(audio_only=True)
    elif ext in VIDEO_EXTENSIONS:
        f = info.value.open()
        metadata = parse_raw(f)
        height, width = scale_from_metadata(metadata)
        anno[MEDIA_INFO_KEY] = dict(audio_only=False, width=width, height=height)
        f.close()
    else:
        if MEDIA_INFO_KEY in anno:
            del anno[MEDIA_INFO_KEY]


class FlowplayerFileView(FileViewBase):
    def getFilename(self):
        info = IPrimaryFieldInfo(self.context)
        return info.value.filename
