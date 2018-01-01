var playlistView = {

	init: function() {
		this.playlist = controller.getPlaylist();
		this.renderPlayer();
		this.renderPlaylist();
	},

	renderPlayer: function() {
		var player = document.createElement('player');
		player.id = 'player'
		$('body').append(player);
	},

	renderPlaylist: function() {
		var playlistContainer = document.createElement('div');
		playlistContainer.id = 'playlist-container'

		for (var i = 1; i < this.playlist.length; i++) {
			var songView = this.renderSongThumbnail(this.playlist[i].url);
			playlistContainer.append(songView);
		}
		$('body').append(playlistContainer);

	},

	renderSongThumbnail: function(songId) {
		var key = 'AIzaSyB-fC4XB3x1GXFoNY-4yTYzatwd4iEYX3M'
		var songContainer = document.createElement('div');
		songContainer.className = 'song-container';
		$.getJSON('https://www.googleapis.com/youtube/v3/videos?key='+key+'&part=snippet&id='+songId, function(data) {

			var thumbnail = document.createElement('img');
			thumbnail.className = 'thumbnail';
			thumbnail.src = data.items[0].snippet.thumbnails.medium.url;

			var songTitle = document.createElement('p');
			songTitle.className = 'song-title';
			songTitle.innerHTML = data.items[0].snippet.title;

			songContainer.append(thumbnail);
			songContainer.append(songTitle);
		});

		return songContainer;
	},

	playVideo: function(event) {
		event.target.playVideo();
	}

}