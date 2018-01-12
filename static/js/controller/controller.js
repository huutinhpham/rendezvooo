var controller = {

	init: function() {
		this.youtube_key = 'AIzaSyB-fC4XB3x1GXFoNY-4yTYzatwd4iEYX3M'
	},

	getYtKey: function() {
		return this.youtube_key;
	}, 

	postRequest: function(ytId) {
		var key = this.getYtKey();
		$.getJSON("https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id="+ytId+"&key="+key, function(data){
			if (!data.items[0].contentDetails.licensedContent) {
				$.post("/playlist/", {
			    	yt_id: ytId
				}, function(data) {
					$('.request-feedback').html(data.error);
				})
			} else {
				$('.request-feedback').html("That video has copyright issues, please try a different link.")
			}
		})
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