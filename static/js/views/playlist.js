var playlist = {

	init: function() {
		this.renderPlayer();
		this.playlist = controller.getPlaylist();
		console.log(this.playlist);
		controller.loadPlayer(this.playlist[0].url);
	},

	renderPlayer: function() {
		var playerElmt = document.createElement('div');
		playerElmt.id = 'player'
		$('body').append(playerElmt);
	},

	renderPlaylist: function() {

	}
}

playlist.init();