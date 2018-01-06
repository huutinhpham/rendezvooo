var playlistView = {

	init: function() {
		this.renderPlayer();
		this.renderPlaylist();
		this.bindRequestBtn();
	},
	
	renderPlayer: function() {
		var player = document.createElement('player');
		player.id = 'player'
		$('body').append(player);
	},

	renderPlaylist: function() {
		$.get("/_get_all_songs", function(songs){
			var playlistContainer = document.createElement('div');
			playlistContainer.id = 'playlist-container';
			songs = songs.result;
			for (var i = 1; i < songs.length; i++) {
				console.log(songs[i]);
				var songView = playlistView.renderSongThumbnail(songs[i][1]);
				playlistContainer.append(songView);
			}

			$('body').append(playlistContainer);

		})
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

	bindRequestBtn: function() {
		$('#request-btn').click(function(){
			var ytId = controller.parseYTurl($('#request-url').val());
			$.post("/playlist/", {
			    yt_id: ytId
			}, function(data) {
				console.log(data.result)
				$('#request-feedback').html(data.result);
			})
		});
	}

}

playlistView.init();