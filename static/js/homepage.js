var homePageView = {

	init: function() {
		this.bindNewPlaylistBtn();
		$('.request-feedback').html(response);
	},

	bindNewPlaylistBtn: function() {
		$('#new-playlist-btn').click(function(){
			window.location.href='/generate-playlist/'
		});
	},

}

homePageView.init();