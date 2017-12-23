var controller = {

	init: function() {

	},

	getAppInfo: function() {
		return appInfo;
	},

	getPlaylist: function() {
		var ytLinks = model.ytLinks;
		for (var i = 0; i < ytLinks.length; i++) {
			ytLinks[i].url = this.parseYTurl(ytLinks[i].url);
		}
		return ytLinks;
	},

	loadPlayer: function(songId) { 
	  	if (typeof(YT) == 'undefined' || typeof(YT.Player) == 'undefined') {
	  		var player;
	    	var tag = document.createElement('script');
	    	tag.src = "https://www.youtube.com/iframe_api";
	    	var firstScriptTag = document.getElementsByTagName('script')[0];
	    	firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

	    	window.onYouTubePlayerAPIReady = function() {
	    		controller.onYouTubeIframeAPIReady(songId);
	    	};

	  	} else {
	    	controller.onYouTubeIframeAPIReady(songId);
	  	}
	},

	onYouTubeIframeAPIReady: function(songId) {
		var DOMplayer = document.getElementById('player');
        var player = new YT.Player(DOMplayer, {
          	videoId: songId,
          	events: {
            	'onReady': this.onSongReady,
            	'onStateChange': this.onSongFinished
          	}
        });
    },

    onSongReady: function(event) {
    	event.target.playVideo();
    },

    onSongFinished: function(event) {        
        if(event.data === 0) {            
            alert('done');
        }
    },

	parseYTurl: function(url) {
		var ytID = '';
		url = url.replace(/(>|<)/gi,'').split(/(vi\/|v=|\/v\/|youtu\.be\/|\/embed\/)/);
		if(url[2] !== undefined) {
			ytID = url[2].split(/[^0-9a-z_\-]/i);
		    ytID = ytID[0];
		}
		else {
		    ytID = url;
		}
		    return ytID;
	},
}

controller.init();