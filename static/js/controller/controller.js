var controller = {

	init: function() {
		this.songs = this.updateSongs();
	},

	getAppName: function() {
		return model.appName;
	},

	updateSongs: function() {
		$.get("/_get_all_songs/", function(songs){
			this.songs = songs;
		});
	},

	getSongs: function() {
		return this.songs;
	},

	getTopSong: function() {
		return this.getPlaylist()[2].url;
	},

	removeTopSong: function() {

	},

	generatePid: function() {

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