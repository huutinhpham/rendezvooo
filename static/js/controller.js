var controller = {

	init: function() {

	},

	getAppInfo: function() {
		return appInfo;
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
		    return ID;
	}
}

controller.init();