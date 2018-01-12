var playlistView = {

	init: function() {
		this.renderPlayer();
		this.renderPlaylist();
		this.bindRequestBtn();
		this.player = player;
	},

	bindRequestBtn: function() {
		$('#request-btn').click(function(){
			var ytId = controller.parseYTurl($('#request-url').val());
			controller.postRequest(ytId);
		});
	},
	
	renderPlayer: function() {
		var playerElm = document.createElement('player');
		playerElm.id = 'player'
		$('body').append(playerElm);
	},

	loadCurrentSong: function(event) {
		$.get("/get_current_song/", function(song){
			event.target.cueVideoById(song[1]);
		}) 
	},

	playNextSong: function(event) {
		if(event.data === 0) {
			$.get("/get_next_song/", function(song){
				event.target.loadVideoById(song[1]);
			})    
    	}
	},

	renderPlaylist: function() {
		$.get("/get_all_songs/", function(songs){
			var playlistContainer = document.createElement('div');
			playlistContainer.id = 'playlist-container';
			for (var i = 0; i < songs.length; i++) {
				var songView = playlistView.renderSongThumbnail(songs[i][1], songs[i][2], songs[i][3]);
				playlistContainer.append(songView);
			}

			$('body').append(playlistContainer);

		})
	},

	renderSongThumbnail: function(songId, likes, requester) {
		var key = controller.getYtKey();
		var songContainer = document.createElement('div');
		songContainer.className = 'song-container';
		songContainer.id = songId

		$.getJSON('https://www.googleapis.com/youtube/v3/videos?key='+key+'&part=snippet&id='+songId, function(data) {

			var thumbnail = document.createElement('img');
			thumbnail.className = 'thumbnail';
			thumbnail.src = data.items[0].snippet.thumbnails.medium.url;

			var songInfo= data.items[0].snippet;

			var descriptionContainer = playlistView.renderSongDescription(songId, likes, songInfo, requester)

			songContainer.append(thumbnail);
			songContainer.append(descriptionContainer);

			playlistView.bindPlayBtn(songId);
			playlistView.loadLikeFeatures(songId, likes)
		});

		return songContainer;
	},

	renderSongDescription: function(songId, likes, songInfo, requester) {
		var descriptionContainer=document.createElement('div')
		descriptionContainer.className='description-container'

		var songTitle = document.createElement('p');
		songTitle.className='song-title';
		songTitle.innerHTML = songInfo.title;

		var requesterElm = document.createElement('p')
		requesterElm.className='requester'
		requesterElm.innerHTML="Requested By: " + requester

		var channelElm = this.renderChannelInfo(songInfo.channelTitle)
		var publishElm = this.renderPublishDate(songInfo.publishedAt)

		var likeBtn = document.createElement('button')
		likeBtn.className = "like-btn"

		var playBtn = this.renderPlayBtn();

		descriptionContainer.append(songTitle);
		descriptionContainer.append(requesterElm);
		descriptionContainer.append(channelElm);
		descriptionContainer.append(publishElm);
		descriptionContainer.append(likeBtn);
		descriptionContainer.append(playBtn);

		return descriptionContainer;
	},

	renderChannelInfo: function(channelTitle){
		var channelElm = document.createElement('p')
		channelElm.className="info-button"
		channelElm.innerHTML = 'From: ' + channelTitle
		return channelElm
	},

	renderPublishDate: function(date){
		var publishElm = document.createElement('p')
		var date = new Date(date).toDateString()
		publishElm.className="info-button"
		publishElm.innerHTML = 'Published On ' + date
		return publishElm
	},


	bindLikeFeatures: function(songId) {
		this.bindLikeThumbnail(songId);
		this.bindLikeBtn(songId);
	},

	bindUnlikeFeatures: function(songId) {
		this.bindUnlikeThumbnail(songId)
		this.bindUnlikeBtn(songId);
	},


	loadLikeFeatures: function(songId, likes) {
		$.post('/is_liked/', {
			yt_id: songId
		}, function(is_liked) {
			if (is_liked != true) {
				$('#' + songId + ' .like-btn').replaceWith(playlistView.renderLikeBtn(songId, likes))
				playlistView.bindLikeFeatures(songId)
			} else {
				$('#' + songId + ' .like-btn').replaceWith(playlistView.renderUnlikeBtn(songId, likes))
				playlistView.bindUnlikeFeatures(songId)
			}
		})
	},

	bindLikeThumbnail: function(songId) {
		$('#' + songId + ' .thumbnail').unbind().dblclick(function(songId){
			return function() {
				$.post("/liked/", {
					yt_id: songId
				}, function(likes) {
					$('#' + songId + ' .like-btn').replaceWith(playlistView.renderUnlikeBtn(songId, likes));
					playlistView.bindUnlikeFeatures(songId);
				});
			}
		}(songId));
	},

	bindUnlikeThumbnail: function(songId) {
		$('#' + songId + ' .thumbnail').unbind().dblclick(function(songId){
			return function() {
				$.post("/unliked/", {
					yt_id: songId
				}, function(likes) {
					$('#' + songId + ' .like-btn').replaceWith(playlistView.renderLikeBtn(songId, likes));
					playlistView.bindLikeFeatures(songId);
				});
			}
		}(songId));
	},

	renderLikeBtn: function(songId, likes) {
		var likeBtn = document.createElement('button');
		likeBtn.className = "like-btn"
		likeBtn.innerHTML = "&#x2661" + " " + likes;

		return likeBtn;
	},

	renderUnlikeBtn: function(songId, likes) {
		var likeBtn = document.createElement('button');
		likeBtn.className = "like-btn"
		likeBtn.innerHTML = "&#x2764" + " " + likes;

		return likeBtn;
	},


	bindLikeBtn: function(songId) {
		$('#' + songId + ' .like-btn').click(function(songId){
			return function() {
				$.post("/liked/", {
					yt_id: songId
				}, function(likes) {
					$('#' + songId + ' .like-btn').replaceWith(playlistView.renderUnlikeBtn(songId, likes));
					playlistView.bindUnlikeFeatures(songId);
				});
			}
		}(songId));
	},

	bindUnlikeBtn: function(songId) {
		$('#' + songId + ' .like-btn').click(function(songId){
			return function() {
				$.post("/unliked/", {
					yt_id: songId
				}, function(likes) {
					$('#' + songId + ' .like-btn').replaceWith(playlistView.renderLikeBtn(songId, likes));
					playlistView.bindLikeFeatures(songId)
				});
			}
		}(songId));
	},

	renderPlayBtn: function() {
		var playBtn = document.createElement('button')
		playBtn.className = 'play-btn fa'
		playBtn.innerHTML = "&#xf144"
		return playBtn;
	},

	bindPlayBtn: function(songId) {
		$('#' + songId + ' .play-btn').click(function(songId){
			return function() {
				$.post("/change_current_song/", {
					yt_id: songId
				}, function() {
					playlistView.player.loadVideoById(songId);
				})
			}
		}(songId));
	},
}

playlistView.init();