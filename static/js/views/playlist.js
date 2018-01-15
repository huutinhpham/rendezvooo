var playlistView = {

	init: function() {
		this.renderRequestBar();
		this.renderPlayer();
		this.renderPlaylist();
		this.bindRequestBtn();
		this.requestValidator;
		this.player;
	},

	renderRequestBar: function() {
		var requestBar = document.createElement('div');
		requestBar.id = 'request-bar'

		var previewElm = document.createElement('requestValidator');
		previewElm.id = 'requestValidator';

		requestInput = this.renderRequestInput();
		requestBtn = this.renderRequestBtn();

		requestBar.append(previewElm);
		requestBar.append(requestInput);
		requestBar.append(requestBtn);
		$('#content').append(requestBar);
	},

	renderRequestInput: function() {
		var requestInput = document.createElement('input');
		requestInput.id = 'request-input'
		requestInput.type = "text"
		requestInput.placeholder = "YouTube Url Here";

		return requestInput;		
	},

	renderRequestBtn: function() {

		var requestBtn = document.createElement('button');
		requestBtn.id = 'request-btn'
		requestBtn.innerHTML = 'Submit Url'

		return requestBtn;

	},

	bindRequestBtn: function() {
		$('#request-btn').click(function(){
			var ytId = controller.parseYTurl($('#request-input').val());
			playlistView.validateRequest(ytId);
			controller.postSongRequest(ytId);
			$.get('/get_collaborator/', function(collaborator) {
				$("#content").append(playlistView.renderSongThumbnail(ytId, 0, collaborator));
			})
		});
	},
	

	loadValidator: function(event) {
		event.target.mute();
	},

	validateRequest: function(songId) {
		this.requestValidator.loadVideoById(songId);
		this.requestValidator.pauseVideo();
	},

	onRequestError: function(event) {
		console.log(event.data);
		if (event.data == 150 || event.data == 101) {
			ytId = controller.parseYTurl($('#request-input').val())
			controller.invalidSongRequest(ytId);
			playlistView.deleteSongThumbnail(ytId);
		}
	},

	renderPlayer: function() {
		var playerContainer = document.createElement('div')
		playerContainer.id = "player-container"
		var playerElm = document.createElement('player');
		playerElm.id = 'player'
		playerContainer.append(playerElm);
		$('#content').append(playerContainer);
	},

	loadCurrentSong: function(event) {
		$.get("/load_first_song/", function(song){
			event.target.cueVideoById(song);
			$("#" + song).addClass('current-song');
			// if (song == null) {
			// 	playlistView.renderEmptyPlaylist();
			// }
		}) 
	},

	playNextSong: function(event) {
		if(event.data === 0) {
			playlistView.reRenderPlaylist();
			$.get("/next_song/", function(songs){
				event.target.loadVideoById(songs[1]);
				playlistView.updateCurrentSong(songs[0], songs[1]);
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

			$('#content').append(playlistContainer);

		})
	},

	reRenderPlaylist: function() {
		$('#playlist-container').remove();
		this.renderPlaylist();
	},

	updateCurrentSong: function(previousSong, currentSong) {
		$("#" + previousSong).removeClass('current-song');
		$("#" + currentSong).addClass('current-song');
	},

	// renderEmptyPlaylist: function() {
	// 	var emptyPlaylist = document.createElement('p')
	// 	emptyPlaylist.className = 'intro'
	// 	emptyPlaylist.innerHTML = 'Request a song to your new playlist!'

	// 	("#request-bar").before(emptyPlaylist);
	// },

	renderSongThumbnail: function(songId, likes, requester) {
		var key = controller.getYtKey();
		var songContainer = document.createElement('div');
		var songContent = document.createElement('div')
		songContent.className = 'song-content'
		songContainer.className = 'song-container';
		songContainer.id = songId

		$.getJSON('https://www.googleapis.com/youtube/v3/videos?key='+key+'&part=snippet&id='+songId, function(data) {

			var thumbnail = document.createElement('img');
			thumbnail.className = 'thumbnail';
			thumbnail.src = data.items[0].snippet.thumbnails.medium.url;

			var songInfo= data.items[0].snippet;

			var descriptionContainer = playlistView.renderSongDescription(songId, likes, songInfo, requester)
			var deleteBtn = playlistView.renderDeleteBtn();

			songContent.append(thumbnail);
			songContent.append(descriptionContainer);
			songContent.append(deleteBtn);

			playlistView.bindDeleteBtn(songId);
			playlistView.bindPlayBtn(songId);
			playlistView.bindThumbnail(songId);
			playlistView.loadLikeFeatures(songId, likes)
		});

		songContainer.append(songContent);
		return songContainer;
	},

	deleteSongThumbnail: function(songId) {
		$("#" + songId).remove();
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

		var songBtns = playlistView.renderSongBtns();

		descriptionContainer.append(songTitle);
		descriptionContainer.append(requesterElm);
		descriptionContainer.append(channelElm);
		descriptionContainer.append(publishElm);
		descriptionContainer.append(songBtns);

		return descriptionContainer;
	},

	renderSongBtns: function() {
		var songBtns = document.createElement('div')
		songBtns.className = 'song-btns'

		var likeBtn = this.renderLikeBtn(0);
		var playBtn = this.renderPlayBtn();

		songBtns.append(likeBtn);
		songBtns.append(playBtn);

		return songBtns;
	},

	renderChannelInfo: function(channelTitle){
		var channelElm = document.createElement('p');
		channelElm.className="info-button";
		channelElm.innerHTML = 'From: ' + channelTitle;
		return channelElm;
	},

	renderPublishDate: function(date){
		var publishElm = document.createElement('p');
		var date = new Date(date).toDateString();
		publishElm.className="info-button";
		publishElm.innerHTML = 'Published On ' + date;
		return publishElm;
	},

	bindThumbnail: function(songId) {
		$('#' + songId + ' .thumbnail').click(function(songId){
			return function() {
				$.post("/change_current_song/", {
					yt_id: songId
				}, function(previousSong) {
					playlistView.updateCurrentSong(previousSong, songId);
					playlistView.player.loadVideoById(songId);
				})
			}
		}(songId));
	},

	renderDeleteBtn: function() {
		var deleteBtn = document.createElement('button')
		deleteBtn.className = 'delete-btn'
		deleteBtn.innerHTML = "&#x2613"

		return deleteBtn;
	},

	bindDeleteBtn: function(songId) {
		$('#' + songId + ' .delete-btn').click(function(songId){
			return function() {
				$('#' + songId + ' .delete-btn').replaceWith(playlistView.renderDeleteConfirmBtns());
				playlistView.bindDeleteConfirmBtn(songId);
				playlistView.bindCancelDeleteBtn(songId);
			}
		}(songId));
	},

	renderDeleteConfirmBtns: function() {
		var confirmDiv = document.createElement('div')
		confirmDiv.className = 'confirm-div'

		var deleteConfirmBtn = document.createElement('button')
		deleteConfirmBtn.className = 'delete-confirm-btn'
		deleteConfirmBtn.innerHTML = "DELETE SONG"

		var cancelDeleteBtn = document.createElement('button')
		cancelDeleteBtn.className = 'cancel-delete-btn'
		cancelDeleteBtn.innerHTML = "Cancel"

		confirmDiv.append(cancelDeleteBtn);
		confirmDiv.append(deleteConfirmBtn);

		return confirmDiv;
	},

	bindDeleteConfirmBtn: function(songId) {
		$('#' + songId + ' .delete-confirm-btn').click(function(songId) {
			return function() {
				$.post('/delete_song/', {
					yt_id: songId
				}, function() {
					playlistView.deleteSongThumbnail(songId);
				})
			}
		}(songId));
	},

	bindCancelDeleteBtn: function(songId) {
		$("#" + songId + ' .cancel-delete-btn').click(function(songId) {
			return function() {
				console.log('hello')
				$('#' + songId + ' .confirm-div').replaceWith(playlistView.renderDeleteBtn());
				playlistView.bindDeleteBtn(songId);
			}
		}(songId));
	},

	loadLikeFeatures: function(songId, likes) {
		$.post('/is_liked/', {
			yt_id: songId
		}, function(is_liked) {
			if (is_liked != true) {
				$('#' + songId + ' .like-btn').replaceWith(playlistView.renderLikeBtn(likes))
				playlistView.bindLikeBtn(songId)
			} else {
				$('#' + songId + ' .like-btn').replaceWith(playlistView.renderUnlikeBtn(likes))
				playlistView.bindUnlikeBtn(songId)
			}
		})
	},

	renderLikeBtn: function(likes) {
		var likeBtn = document.createElement('button');
		likeBtn.className = "like-btn"
		likeBtn.innerHTML = "&#x2661" + " " + likes;

		return likeBtn;
	},

	renderUnlikeBtn: function(likes) {
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
					$('#' + songId + ' .like-btn').replaceWith(playlistView.renderUnlikeBtn(likes));
					playlistView.bindUnlikeBtn(songId);
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
					$('#' + songId + ' .like-btn').replaceWith(playlistView.renderLikeBtn(likes));
					playlistView.bindLikeBtn(songId)
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
				}, function(previousSong) {
					$("#" + previousSong).removeClass('current-song');
					$("#" + songId).addClass('current-song');
					playlistView.player.loadVideoById(songId);
				})
			}
		}(songId));
	},
}

playlistView.init();