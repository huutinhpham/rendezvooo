var controller = {

	init: function() {
		this.playlist = this.updatePlaylist();
	},

	getAppInfo: function() {
		return appInfo;
	},

	updatePlaylist: function() {
		var ytLinks = model.ytLinks;
		for (var i = 0; i < ytLinks.length; i++) {
			ytLinks[i].url = this.parseYTurl(ytLinks[i].url);
		}
		return ytLinks;
	},

	getPlaylist: function() {
		return this.playlist;
	},

	getTopSong: function() {
		return this.getPlaylist()[2].url;
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
playlistView.init();