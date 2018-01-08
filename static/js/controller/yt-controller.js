var player;

var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

function onYouTubeIframeAPIReady() {
	var DOMplayer = document.getElementById('player');
	player = new YT.Player('player', {
       	events: {
       	  'onReady': playlistView.playFirst,
       	  'onStateChange': playlistView.playNext
       	}
   	});
}

// function playVideo(event) {
// 	event.target.playVideo();
// }
