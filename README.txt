Introduction
============

collective.flowplayer integrates the GPL version of `Flowplayer`_ with Plone
3.x. It can play .flv Flash Video files, mp4 files or links as well as .mp3
files or links.

Installation
------------

Add collective.flowplayer to your buildout as normal. See
http://plone.org/documentation/tutorial/buildout. Don't forget to load the
configure.zcml file!

Then install the product via Plone's Add-on products control panel.

Usage
-----

collective.flowplayer offers several different usage modes:

Standalone player
~~~~~~~~~~~~~~~~~

To get a standalone video or audio player, simply add a standard Plone
File anywhere in your site and upload a .flv or .mp3 file. You can
also add a Plone Link whose URL points to an .flv or .mp3 URL.  The
'flowplayer' view will automatically be selected in the 'display'
menu, which will show a video/audio player.

You can also do this manually, of course.

Playlist
~~~~~~~~

Create a Folder with several .mp3 or .flv files or links, or create a
Collection that lists such files or links. Then 'flowplayer' from the
'display' drop-down at the Folder/Collection level.

This will show a video/audio player that will loop through the media
in the Folder/Collection (unknown file formats will be ignored) in
order. The video player will be sized to fit the largest video in
the playlist.

There is horizontal scrollable playlist displayed under the player by default.
If you don't want to display the playlist, switch off "showPlaylist" property in
flowplayer's configuration.

Portlet
~~~~~~~

To place a video or audio player in a portlet, use the Video Player portlet
that is installed with this product. You can choose a Folder, Collection or
File to display. When displaying a Folder or Collection, you will get a 
playlist much like the one described above.

Note that the player in the portlet has got a fixed size, set with CSS.

Inline
~~~~~~

In each of the cases above, the video player is actually created with
JavaScript as the page is loaded. This allows some degree of graceful 
degradation for browsers without Flash or JavaScript, but, more importantly,
makes it easy to insert a video player anywhere, including in your content
pages.

To create a standalone player, you would use markup like this::

    <a class="autoFlowPlayer" href="path/to/video-file.flv">
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
----------------

To make it easier to use the type of markup outlined above to insert a video
or audio player into a Plone content item, this product installs a few
Kupu paragraph styles.  You can use them like this:

Video
~~~~~

 1. Insert the image you want to use as a splash image. You should insert this
    "inline" (rather than left/right floating), preferably in its own
    paragraph.
    
 2. Select on the image, and make it link to the .flv or .mp3 file you want
    to play.
    
 3. Select one of the Video or Audio styles from the styles drop-down.
 
Audio
~~~~~

 1. Create a link to an mp3 file, e.g. out of some text. Again, place it in
    its own paragraph.
    
 2. Select one of the "Audio" styles from the styles drop-down. The "left"
    and "right" styles will produce a small player floating to the left or
    right. The "Audio" style will produce a larger player on its own line.
    
Notes
~~~~~

    * it is not possible to detect clip width/height from the mp4 file now

    * if your player is not displayed on the page load, but is displayed after
      you click somewhere to the player container area, be sure there is no
      HTML code nor text inside the player container HTML tag. Such code/text
      is considered as player splash screen and player is waiting for click to
      the splash.

    * player is correctly created only if player container is < div >
      element (Kupu does it automatically if Audio and Video styles are used).
      Using other containers (eg. p) is not supported currently.

Configuration
-------------

Flowplayer supports a large number of configuration options. A few of these
will be set based on the markup used to render the player (e.g. the playlist
buttons will only be rendered if there is a playlist, and most controls will
be hidden in 'minimal' mode). Most other options can be set in the ZMI.

In portal_properties, there should be a new propertysheet called
flowplayer_properties. Options set here are passed through to the player's
JavaScript configuration (make sure you use the right property type). For
string properties, you can use the placeholder ${portal_url} to refer to
the URL of the portal root. This is useful for things like watermark images or 
player plugins. 

Properties starting with word "param/" are considered as Flash configuration
properties. You may set properties like src (player flash file), wmode,
quality, allowscriptaccess etc. Just use eg. param/wmode as property name and
eg. 'opaque' as property value.

'''Important note''' Since playlist configuration is a generated javascript file
included in portal_javascript, you must reload portal_javascript after global
player configuration is changed or portal_javascript must be running in debug
mode (not reccommended for production sites). Go to ZMI/portal_javascript,
scroll down and pres "Save" button after your flowplayer_properties are set.

Since FlowPlayer3 uses more complex properties and plugins infrastructure, most
of visual properties are defined as a plugin configuration (e.g. control bar is
separate plugin with own set of properties). If you want to configure
FlowPlayer3 plugin, you should define it's flash file using property syntax eg.
plugins/controls/url which generates configuration item in form::

    {
     plugins : {
               controls : {
                            url : 'VALUE OF PROPERTY'
                          }
               }
    }
    
To configure color of control bar volumeSliderColor, define property: 
plugins/controls/volumeSliderColor set to value 'lime', which generates 
the following config::

    { 
     plugins : {
               controls : {
                            url : 'VALUE OF PROPERTY',
                            volumeSliderColor: 'lime'
                          }
               }
    }

All control bar configuration properties are described on `Controlbar plugin
documentation`_ page.

General informations about the configuration options may be found at the
`FlowPlayer configuration`_ page. Please note, it is not possible to specify
events in the Plone's flowplayer_properties sheet now (eg. onBeforeFinish
event).

Useful configuration examples from http://flowplayer.org:

 * `Custom tooltips and texts`_
 
 * `Controlbar color generator`_

Extending player runtime
------------------------

It is possible to extend player configuration or modify player behaviour runtime
using javascript plugins. Collective.flowplayer uses flowplayer.js for embedding
player into page. It is the most general version of embedding which allows all
kinds of configuration of the player. Please read `Documentation of Flowplayer
JS API`_ for more details. The most important for player extension is `Player
retrieval`_ part and description of `Player configuration`_ and `Clip
configuration`_. A lot of player scripting examples may be found at `Scripting
demo`_ page and `Scripting documentation`_

Extending example
-----------------

collective.flowplayer creates Flowplayer instance from all .autoFlowPlayer and
.playListFlowPlayer containers on the page. You may retrieve first player
eg. by::

    $f()  or flowplayer()
    
or iterate through all players on page using:: 

    $f("*").each
    
To be able to configure player runtime, you must first create custom javascript 
file and include this file to page or add it to portal_javascripts registry.
Since flowplayer uses jQuery to initialize itself, you must use jQuery syntax
as well. Example of js skeleton::

    jq(function () {

        // your javascript code goes here

    })
    
Let's create concerete example. The most visible one is Javascript alert::

    jq(function () {

        $f().onPause(function() { alert("Don't pause me!")})

    })

or (for all players on the page)::

    jq(function () {

        $f("*").each( function() { 
                        this.onPause(function() { alert("Don't pause me!")}) 
                      })

    })

TIP: If you are using Firefox and have the Firebug Add-on installed, then you
can try the examples yourself against every possible Flowplayer demo on
flowplayer.org or your own site. Activate Firebug console and enter::

    $f().onPause(function() { alert("Don't pause me!")})
    
Try to start/pause player now. Alert window should be displayed.

.. _Flowplayer: http://www.flowplayer.org
.. _`Controlbar plugin documentation`: http://flowplayer.org/plugins/flash/controlbar.html
.. _`Flowplayer configuration`: http://flowplayer.org/documentation/configuration/
.. _`Custom tooltips and texts`: http://flowplayer.org/demos/skinning/tooltips.html
.. _`Controlbar color generator`: http://flowplayer.org/documentation/skinning/controlbar.html
.. _`Documentation of Flowplayer JS API`: http://flowplayer.org/documentation/api/index.html
.. _`Player retrieval`: http://flowplayer.org/documentation/api/flowplayer.html#playerretrieval
.. _`Player configuration`: http://flowplayer.org/documentation/api/player.html 
.. _`Clip configuration`: http://flowplayer.org/documentation/api/clip.html
.. _`Scripting demo`: http://flowplayer.org/demos/index.html#scripting
.. _`Scripting documentation`: http://flowplayer.org/documentation/scripting.html
