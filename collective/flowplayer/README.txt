.. -*-doctest-*-

=====================
collective.flowplayer
=====================

Open a browser and log in as a normal user.

    >>> from Products.Five.testbrowser import Browser
    >>> from Products.PloneTestCase import ptc
    >>> browser = Browser()
    >>> browser.handleErrors = False
    >>> browser.open(portal.absolute_url())
    >>> browser.getLink('Log in').click()
    >>> browser.getControl('Login Name').value = ptc.default_user
    >>> browser.getControl(
    ...     'Password').value = ptc.default_password
    >>> browser.getControl('Log in').click()

FLV Files
=========

Add an empty FLV file to a folder.

    >>> import os
    >>> from collective.flowplayer import tests
    >>> browser.open(folder.absolute_url())
    >>> browser.getLink('File').click()
    >>> ctrl = browser.getControl(name="file_file")
    >>> opened = open(
    ...     os.path.join(os.path.dirname(tests.__file__), 'foo.flv'))
    >>> ctrl.add_file(opened, 'video/x-flv', 'foo.flv')
    >>> browser.getControl('Save').click()
    >>> opened.close()
    >>> print browser.contents
    <...
    ...Changes saved...

The file now provides IVideo and the display layout has automatically
been set to the flowplayer view.

    >>> from collective.flowplayer import interfaces
    >>> interfaces.IVideo.providedBy(folder['foo.flv'])
    True
    >>> folder['foo.flv'].getLayout()
    'flowplayer'
    >>> print browser.contents
    <...
    <script type="text/javascript"
    src="http://nohost/plone/portal_javascripts/Plone%20Default/resourcecollective.flowplayerflashembed.min-cachekey....js">
    </script>...
    <style type="text/css"><!-- @import
    url(http://nohost/plone/portal_css/Plone%20Default/resourcecollective.flowplayer.cssflowplayer-cachekey....css);
    --></style>...
    class="autoFlowPlayer...
    href="http://nohost/plone/Members/test_user_1_/foo.flv...

The generated JavaScript includes the appropriate metadata.

    >>> browser.open(folder['foo.flv'].absolute_url()+'/collective.flowplayer.js')
    >>> print browser.contents
    (...
    var params = {src:
    "/plone/++resource++collective.flowplayer/FlowPlayerDark.swf"};...
    var config = { controlsOverVideo:'ease',
        controlBarBackgroundColor:-1,
        showVolumeSlider:false,
        controlBarGloss:'low',
        useNativeFullScreen:true,
        autoBuffering:false,
        initialVolumePercentage:50,
        initialScale:'fit',
        usePlayOverlay:true,
        loop:false,
        autoPlay:false };...

FLV Links
=========

Add a link to an FLV file to the folder.

    >>> import os
    >>> from collective.flowplayer import tests
    >>> browser.open(folder.absolute_url())
    >>> browser.getLink('Link').click()
    >>> browser.getControl('Title').value = 'Foo Link Title'
    >>> browser.getControl(
    ...     'URL').value = folder['foo.flv'].absolute_url()
    >>> browser.getControl('Save').click()
    >>> opened.close()
    >>> print browser.contents
    <...
    ...Changes saved...

The link now provides IVideo and the display layout has automatically
been set to the flowplayer view.  The player is pointed to the FLV
file that the link points to.

    >>> from collective.flowplayer import interfaces
    >>> interfaces.IVideo.providedBy(folder['foo-link-title'])
    True
    >>> folder['foo-link-title'].getLayout()
    'flowplayer'
    >>> print browser.contents
    <...
    <script type="text/javascript"
    src="http://nohost/plone/portal_javascripts/Plone%20Default/resourcecollective.flowplayerflashembed.min-cachekey....js">
    </script>...
    <style type="text/css"><!-- @import
    url(http://nohost/plone/portal_css/Plone%20Default/resourcecollective.flowplayer.cssflowplayer-cachekey....css);
    --></style>...
    class="autoFlowPlayer...
    href="http://nohost/plone/Members/test_user_1_/foo.flv...

The generated JavaScript includes the appropriate metadata.

    >>> browser.open(folder['foo-link-title'].absolute_url()+'/collective.flowplayer.js')
    >>> print browser.contents
    (...
    var params = {src:
    "/plone/++resource++collective.flowplayer/FlowPlayerDark.swf"};...
    var config = { controlsOverVideo:'ease',
        controlBarBackgroundColor:-1,
        showVolumeSlider:false,
        controlBarGloss:'low',
        useNativeFullScreen:true,
        autoBuffering:false,
        initialVolumePercentage:50,
        initialScale:'fit',
        usePlayOverlay:true,
        loop:false,
        autoPlay:false };...

Folders
=======

A folder can be used as a playlist for the player if the flowplayer
layout is selected.

    >>> browser.open(folder.absolute_url())
    >>> browser.getLink('flowplayer').click()
    >>> print browser.contents
    <...
    ...View changed...

The view renders the playlist with all the necessary JavaScript.  This
playlist will list the foo.flv file twice since the link points to the
same file.

    >>> print browser.contents
    <...
    <script type="text/javascript"
    src="http://nohost/plone/portal_javascripts/Plone%20Default/resourcecollective.flowplayerflashembed.min-cachekey....js">
    </script>...
    <style type="text/css"><!-- @import
    url(http://nohost/plone/portal_css/Plone%20Default/resourcecollective.flowplayer.cssflowplayer-cachekey....css);
    --></style>...
    class="playListFlowPlayer...
    href="http://nohost/plone/Members/test_user_1_/foo.flv...
    href="http://nohost/plone/Members/test_user_1_/foo.flv...

    >>> browser.open(folder.absolute_url()+'/collective.flowplayer.js')
    >>> print browser.contents
    (...
    var params = {src:
    "/plone/++resource++collective.flowplayer/FlowPlayerDark.swf"};...
    var config = { controlsOverVideo:'ease',
        controlBarBackgroundColor:-1,
        showVolumeSlider:false,
        controlBarGloss:'low',
        useNativeFullScreen:true,
        autoBuffering:false,
        initialVolumePercentage:50,
        initialScale:'fit',
        usePlayOverlay:true,
        loop:false,
        autoPlay:false };...
