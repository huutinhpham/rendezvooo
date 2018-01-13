var controller = {

	init: function() {
		this.youtube_key = 'AIzaSyB-fC4XB3x1GXFoNY-4yTYzatwd4iEYX3M'
	},

	getYtKey: function() {
		return this.youtube_key;
	}, 

	postSongRequest: function(ytId) {
		$.post("/playlist/", {
			yt_id: ytId
		}, function(data) {
			$('.request-feedback').html(data.error);
		})
	},

	invalidSongRequest: function(ytId) {
		$.post('/delete_song/', {
			yt_id: ytId
		})
		$('.request-feedback').html("That video has copyright issues, please try a different link.")
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