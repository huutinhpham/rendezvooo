var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

function onYouTubeIframeAPIReady() {
	var DOMplayer = document.getElementById('player');
	playlistView.player = new YT.Player('player', {
       	events: {
       	  'onReady': playlistView.loadCurrentSong,
       	  'onStateChange': playlistView.playNextSong,
       	}
   	});


	var DOMpreview = document.getElementById('requestValidator')
	playlistView.requestValidator = new YT.Player('requestValidator', {
		height: 0.001,
		width: 0.001,
		playerVars: { 'autoplay': 1, 'controls': 0, 'showinfo':0, 'autohide': 1 },
       	events: {
       	  'onReady': playlistView.loadValidator,
       	  'onError': playlistView.onRequestError
       	}
   	});
}

// function playVideo(event) {
// 	event.target.playVideo();
// }
