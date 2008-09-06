Introduction
============

collective.flowplayer integrates the GPL version of Flowplayer
(http://www.flowplayer.org) with Plone 3.x. It can play .flv Flash Video files
as well as .mp3 files.

Installation
============

Add collective.flowplayer to your buildout as normal. See
http://plone.org/documentation/tutorial/buildout. Don't forget to load the
configure.zcml file!

Then install the product via Plone's Add-on products control panel.

Usage
=====

collective.flowplayer offers several different usage modes:

Standalone player
----------------

To get a standalone video or audio player, simply add a standard Plone File
anywhere in your site and upload a .flv or .mp3 file. The 'flowplayer' view
will automatically be selected in the 'display' menu, which will show a 
video/audio player.

You can also do this manually, of course.

Playlist
--------

Create a Folder with several .mp3 or .flv files, or create a Collection that
lists such files. Then 'flowplayer' from the 'display' drop-down at the
Folder/Collection level.

This will show a video/audio player that will loop through the media files in
the Folder/Collection (unknown file formats will be ignored) in order. The
video player will be sized to fit the largest video file in the playlist.

Portlet
-------

To place a video or audio player in a portlet, use the Video Player portlet
that is installed with this product. You can choose a Folder, Collection or
File to display. When displaying a Folder or Collection, you will get a 
playlist much like the one described above.

Note that the player in the portlet has got a fixed size, set with CSS.

Inline
------

In each of the cases above, the video player is actually created with
JavaScript as the page is loaded. This allows some degree of graceful 
degradation for browsers without Flash or JavaScript, but, more importantly,
makes it easy to insert a video player anywhere, including in your content
pages.

To create a standalone player, you would use markup like this::

    <a class="autoFlowPlayer href="path/to/video-file.flv">
        <img src="path/to/splashscreen.jpg" />
    </a>
    
You can also use a <div class="autoFlowPlayer" /> around the <a /> tag if
you prefer.

This would be replaced by a video player showing the video in video-file.flv,
starting with a splash screen image from splashscreen.jpg. The image is
optional, but if it is specified, the player will be sized to be identical
to the image.

You can also get a more stripped-down player by using::

    <a class="autoFlowPlayer minimal" href="path/to/video-file.flv">
        <img src="path/to/splashscreen.jpg" />
    </a>
    
For an audio player, you can use::

    <a class="autoFlowPlayer audio" href="path/to/audio-file.mp3">
        This text is replaced.
    </a>

You can also use class="autoFlowPlayer minimal audio" to get a very small
audio player (essentially just a play button).

To get a playlist, you can use markup like this::

    <div class="playListFlowPlayer">
        <a class="playListItem" href="path/to/video.flv">Video one</a>
        <a class="playListItem" href="path/to/video.flv">Video two</a>
        <img src="splash.jpg" />
    </div>
    
You can also add 'minimal' and/or 'audio' to the list of classes for the
outer <div /> to change the appearance of the player, or add 'random' to
get a randomised playlist. The splash image is optional.

Kupu integration
================

To make it easier to use the type of markup outlined above to insert a video
or audio player into a Plone content item, this product installs a few
Kupu paragraph styles.  You can use them like this:

Video
-----

 1. Insert the image you want to use as a splash image. You should insert this
    "inline" (rather than left/right floating), preferably in its own
    paragraph.
    
 2. Select on the image, and make it link to the .flv or .mp3 file you want
    to play.
    
 3. Select one of the Video or Audio styles from the styles drop-down.
 
Audio
-----

 1. Create a link to an mp3 file, e.g. out of some text. Again, place it in
    its own paragraph.
    
 2. Select one of the "Audio" styles from the styles drop-down. The "left"
    and "right" styles will produce a small player floating to the left or
    right. The "Audio" style will produce a larger player on its own line.
    
Configuration
=============

Flowplayer supports a large number of configuration options. A few of these
will be set based on the markup used to render the player (e.g. the playlist
buttons will only be rendered if there is a playlist, and most controls will
be hidden in 'minimal' mode). Most other options can be set in the ZMI.

In portal_properties, there should be a new stylesheet called
flowplayer_properties. Options set here are passed through to the player's
JavaScript configuration (make sure you use the right property type). For
string properties, you can use the placeholder ${portal_path} to refer to
the path to the portal root. This is useful for things like watermark images.

You can also use the 'player' property to change the player SWF file that's
used, e.g. to switch to FlowPlayerLight.swf, or use the commercial version if
you have this installed.