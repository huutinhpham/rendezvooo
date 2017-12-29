var playlist = {

	init: function() {
		this.playlist = controller.getPlaylist();
		this.renderPlayer();
		this.renderSong(this.playlist[0].url);
	},

	renderPlayer: function() {
		var playerElmt = document.createElement('div');
		playerElmt.id = 'player'
		$('body').append(playerElmt);
		ytController.loadPlayer(this.playlist[0].url);
	},

	renderPlaylist: function() {

	},

	renderSong: function(songId) {
		var key = 'AIzaSyB-fC4XB3x1GXFoNY-4yTYzatwd4iEYX3M'
		console.log(songId);
		$.getJSON('https://www.googleapis.com/youtube/v3/videos?key='+key+'&part=snippet&id='+songId, function(data) {
			console.log(data.items[0].snippet.title);
		});
	}

}

playlist.init();