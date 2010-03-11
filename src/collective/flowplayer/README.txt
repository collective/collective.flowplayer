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
    >>> contents = browser.contents
    >>> '++resource++collective.flowplayer/flowplayer.min.js">' in contents
    True
    >>> '++resource++collective.flowplayer.css/flowplayer.css)' in contents
    True
    >>> 'href="http://nohost/plone/Members/test_user_1_/foo.flv"' in contents
    True

The generated JavaScript includes the appropriate metadata.

    >>> browser.open(folder['foo.flv'].absolute_url()+'/collective.flowplayer.js')
    >>> print browser.contents
    (...
    var config = {
        "clip": {
            "scaling": "fit",
            "autoBuffering": false,
            "autoPlay": false
            },
        "plugins": {
             "audio": {
                 "url": "http%3A//nohost/plone//%2B%2Bresource%2B%2Bcollective.flowplayer/flowplayer.audio.swf"
             },
             "controls": {
                 "url": "http%3A//nohost/plone//%2B%2Bresource%2B%2Bcollective.flowplayer/flowplayer.controls.swf",
                 "volume": true
             }
         }
    }...
    flowplayer(this, {"src": "http://nohost/plone//++resource++collective.flowplayer/flowplayer.swf"}, config).onLoad( function() { this.setVolume(50); });...

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
    >>> contents = browser.contents
    >>> '++resource++collective.flowplayer/flowplayer.min.js">' in contents
    True
    >>> '++resource++collective.flowplayer.css/flowplayer.css)' in contents
    True
    >>> 'href="http://nohost/plone/Members/test_user_1_/foo.flv"' in contents
    True

The generated JavaScript includes the appropriate metadata.

    >>> browser.open(folder['foo-link-title'].absolute_url()+'/collective.flowplayer.js')
    >>> print browser.contents
    (...
    var config = {
        "clip": {...
    flowplayer(this, {"src": "http://nohost/plone//++resource++collective.flowplayer/flowplayer.swf"}, config).onLoad( function() { this.setVolume(50); });...

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

    >>> contents = browser.contents
    >>> '++resource++collective.flowplayer/flowplayer.playlist.min.js">' in contents
    True
    >>> 'class="playListFlowPlayer' in contents
    True

    >>> browser.open(folder.absolute_url()+'/collective.flowplayer.js')
    >>> print browser.contents
    (...
    var config = {
        "clip": {...
    flowplayer(this, {"src": "http://nohost/plone//++resource++collective.flowplayer/flowplayer.swf"}, config).onLoad( function() { this.setVolume(50); });...

Let's try to change some flowplayer properties.

    >>> props = portal.portal_properties.flowplayer_properties
    >>> props.getProperty('clip/autoPlay')
    False
    >>> props._updateProperty('clip/autoPlay', True)
    >>> browser.open(folder['foo.flv'].absolute_url()+'/collective.flowplayer.js')
    >>> print browser.contents
    (...
    var config = {
        "clip": {...
            "autoPlay": true
            },...
            
Try to add new property.
    
    >>> not not props.hasProperty('plugins/controls/backgroundColor')
    False
    >>> props.manage_addProperty('plugins/controls/backgroundColor', '#000000', 'string')
    >>> props.getProperty('plugins/controls/backgroundColor')
    '#000000'
    >>> browser.open(folder['foo.flv'].absolute_url()+'/collective.flowplayer.js')
    >>> print browser.contents
    (...
    var config = {...
        "plugins": {...
            "controls": {...
                "backgroundColor": "#000000"...

Modify flash params
    
    >>> not not props.hasProperty('param/wmode')
    False
    >>> props.manage_addProperty('param/wmode', 'opaque', 'string')
    >>> browser.open(folder['foo.flv'].absolute_url()+'/collective.flowplayer.js')
    >>> print browser.contents
    (...
    flowplayer(this, {"src": "http://nohost/plone//++resource++collective.flowplayer/flowplayer.swf", "wmode": "opaque"}...

Check playlist 

    >>> props.getProperty('showPlaylist')
    True
    >>> browser.open(folder['foo.flv'].absolute_url()+'/view')
    >>> 'playListFlowPlayer' in browser.contents
    False
    >>> folder.setLayout('flowplayer')
    >>> folder.getLayout()
    'flowplayer'
    >>> browser.open(folder.absolute_url())
    >>> 'playListFlowPlayer' in browser.contents
    True
    >>> 'flowPlaylistVisible' in browser.contents
    True
    >>> props._updateProperty('showPlaylist', False)
    >>> browser.open(folder.absolute_url())
    >>> 'playListFlowPlayer' in browser.contents
    True
    >>> 'flowPlaylistHidden' in browser.contents
    True
    

Rename foo.flv to 'foo' only and check generated code. Since foo does not end
with the same suffix as included file ('flv'), append the suffix as argument
of generated href.

    >>> browser.open(folder['foo.flv'].absolute_url()+'/view')
    >>> print browser.contents
    <... <a style="" href="http://nohost/plone/Members/test_user_1_/foo.flv" class="autoFlowPlayer video"></a>...
    
    >>> folder.manage_renameObjects(['foo.flv',], ['foo'])
    >>> folder['foo'].absolute_url()
    'http://nohost/plone/Members/test_user_1_/foo'
    >>> browser.open(folder['foo'].absolute_url()+'/view')
    >>> print browser.contents
    <... <a style="" href="http://nohost/plone/Members/test_user_1_/foo?e=.flv" class="autoFlowPlayer video"></a>...

Make sure we don't leak into sites where we're not installed
============================================================

If the product is uninstalled, new items should no longer get subtyped.

    >>> portal.portal_quickinstaller.uninstallProducts(products=['collective.flowplayer'])
    >>> folder.manage_delObjects(['foo'])
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
    >>> interfaces.IVideo.providedBy(folder['foo.flv'])
    False
