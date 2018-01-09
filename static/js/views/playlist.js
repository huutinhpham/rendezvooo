var playlistView = {

	init: function() {
		this.renderPlayer();
		this.renderPlaylist();
		this.bindRequestBtn();
		this.songIndex = 0;
	},

	bindRequestBtn: function() {
		$('#request-btn').click(function(){
			var ytId = controller.parseYTurl($('#request-url').val());
			console.log(ytId);
			$.post("/playlist/", {
			    yt_id: ytId
			}, function(data) {
				$('.request-feedback').html(data.error);
				//render and bind thumbnail if success
			})
		});
	},
	
	renderPlayer: function() {
		var player = document.createElement('player');
		player.id = 'player'
		$('body').append(player);
	},

	playFirst: function(event) {
		$.get("/get_top_song/", function(song){
			player.loadVideoById(song[1]);
			event.target.playVideo();
		})    
	},

	playNext: function(event) {
		if(event.data === 0) {
			$.get("/get_all_songs_sorted/", function(songs){
				playlistView.songIndex += 1;
				player.loadVideoById(songs[playlistView.songIndex][1]);
			})    
    	}
	},

	renderPlaylist: function() {
		$.get("/get_all_songs_sorted/", function(songs){
			var playlistContainer = document.createElement('div');
			playlistContainer.id = 'playlist-container';
			for (var i = 0; i < songs.length; i++) {
				var songView = playlistView.renderSongThumbnail(songs[i][1], songs[i][2]);
				playlistContainer.append(songView);
			}

			$('body').append(playlistContainer);

		})
	},

	renderSongThumbnail: function(songId, likes) {
		var key = 'AIzaSyB-fC4XB3x1GXFoNY-4yTYzatwd4iEYX3M'
		var songContainer = document.createElement('div');
		songContainer.className = 'song-container';
		songContainer.id = songId

		$.getJSON('https://www.googleapis.com/youtube/v3/videos?key='+key+'&part=snippet&id='+songId, function(data) {

			var thumbnail = document.createElement('img');
			thumbnail.className = 'thumbnail';
			thumbnail.id = songId
			thumbnail.src = data.items[0].snippet.thumbnails.medium.url;

			var songTitle = document.createElement('p');
			songTitle.className='song-title';
			songTitle.innerHTML = data.items[0].snippet.title;

			var songLikes = document.createElement('p')
			songLikes.className='song-likes'
			songLikes.innerHTML = likes;

			songContainer.append(songTitle);
			songContainer.append(thumbnail);
			songContainer.append(songLikes);

			playlistView.bindThumbnail(songId);
		});

		return songContainer;
	},

	bindThumbnail: function(songId) {
		$('#' + songId + ' img').dblclick(function(songId){
			return function() {
				$.post("/liked/", {
					yt_id: songId
				}, function(data) {
					console.log(data.response == 'success')
					if (data.response == 'success') {
						var likes = parseInt($('#' + songId + ' .song-likes').html())
						$('#' + songId + ' .song-likes').html(likes += 1)
					}
				});
			}
		}(songId));
	}

}

playlistView.init();