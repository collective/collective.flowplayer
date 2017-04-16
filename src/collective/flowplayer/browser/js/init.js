/*global jQuery, flowplayer, window */
(function($) {
    function initialVolume() {
        var volume = window.collective_flowplayer.initialVolumePercentage;
        if (volume !== null) {
            this.setVolume(volume);
        }
    }

    function loop() {
        return !window.collective_flowplayer.loop;
    }

    initFlowplayer = function(area) {
        if (area === undefined) {
            area = $('body');
        }
        $('.autoFlowPlayer', area).each(function() {
            // Take a copy of the global config
            var config = jQuery.extend(true, {}, window.collective_flowplayer.config);
            var $self = $(this);
            if ($self.is('.minimal')) {
                config.plugins.controls = null;
            }
            var audio = $self.is('.audio');
            if (audio && !$self.is('.minimal')) {
                config.plugins.controls.all = false;
                config.plugins.controls.play = true;
                config.plugins.controls.scrubber = true;
                config.plugins.controls.mute = true;
                config.plugins.controls.volume = true;
                config.plugins.controls.time = true;
                config.plugins.controls.autoHide = false;
            }
            if ($self.is('div')) {
                // comming from Kupu, there are relative urls
                config.clip.baseUrl = $('base').attr('href');
                config.clip.url = $self.find('a').attr('href');
                if (audio) {
                    // force .mp3 extension
                    config.clip.url = config.clip.url + '?e=.mp3';
                }
                // Ignore global autoplay settings
                if ($self.find('img').length === 0) {
                    // no image. Don't autoplay, remove all elements inside the div to show player directly.
                    config.clip.autoPlay = false;
                    $self.empty();
                } else {
                    // Clip is probably linked as image, so autoplay the clip after image is clicked
                    config.clip.autoPlay = true;
                    // If we know there is splash image, we could at least try to match this size
                    $(window).load(function(){
                        $self.css("width", $self.find('img').width());
                        $self.css("height", $self.find('img').height());
                    });
                }
            }
            flowplayer(this, window.collective_flowplayer.params, config).onLoad(initialVolume).onBeforeFinish(loop);
            $('.flowPlayerMessage').remove();
        });
        $('.playListFlowPlayer').each(function() {
            // Take a copy of the global config
            var config = jQuery.extend(true, {}, window.collective_flowplayer.config);
            var $self = $(this);
            var audio = $self.is('.audio');
            if (audio) {
                config.plugins.controls.fullscreen = false;
            }
            if ($self.is('.minimal')) {
                config.plugins.controls = null;
            }
            if ($self.find('img').length > 0) {
                // has splash
                config.clip.autoPlay = true;
            }
            var portlet_parents = $self.parents('.portlet');
            var playlist_selector = 'div#flowPlaylist';
            var portlet;
            if (portlet_parents.length > 0) {
                portlet = true;
                // playlist has to be bound to unique item
                var playlist_selector_id = portlet_parents.parent().attr('id') + '-playlist';
                $self.parent().find('.flowPlaylist-portlet-marker').attr('id', playlist_selector_id);
                playlist_selector = '#' + playlist_selector_id;
                if (audio && !$self.is('.minimal')) {
                    config.plugins.controls.all = false;
                    config.plugins.controls.play = true;
                    config.plugins.controls.scrubber = true;
                    config.plugins.controls.mute = true;
                    config.plugins.controls.volume = false;
                }
            } else {
                portlet = false;
            }
            if (!portlet) {
                $("#pl").scrollable({
                    items: playlist_selector,
                    size: 4,
                    clickable: false,
                    prev: 'a.prevPage',
                    next: 'a.nextPage'
                });
            }
            // manual = playlist is setup using HTML tags, not using playlist array in config
            flowplayer(this, window.collective_flowplayer.params, config).playlist(playlist_selector, {
                loop: true,
                manual: true
            }).onLoad(initialVolume).onBeforeFinish(loop);
            $self.show();
            $('.flowPlayerMessage').remove();

        });
    };
    $(window).load(function(){
        initFlowplayer();
    });
}(jQuery));
