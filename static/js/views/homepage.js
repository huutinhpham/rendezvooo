var homePageView = {

	init: function() {
		this.bindPidSubmitBtn();
		this.bindNewPlaylistBtn();
	},

	bindNewPlaylistBtn: function() {
		$('#new-playlist-btn').click(function(){
			window.location.href='/generate-playlist/'
		});
	},

	bindPidSubmitBtn: function() {
		$('#pid-submit-btn').click(function(){
			var pid = $('#pid-input').val();
			$.post('/', {
			    pid: pid
			}, function(response) {
				console.log(response)
				if (response.redirect !== undefined && response.redirect_url) {
					window.location.href = response.redirect_url
				} else {
					$('.request-feedback').html(response);
				}
			})
		});
	}
}

homePageView.init();