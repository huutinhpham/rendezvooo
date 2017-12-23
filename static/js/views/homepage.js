var homePageView = {

	init: function() {
		this.appInfo = controller.getAppInfo();
		this.render();
	},

	render: function() {
		this.renderTitleField();
		this.renderFormField();
	},

	renderTitleField: function() {
		var nameField = document.createElement('h1');
		nameField.className += "app-name";
		nameField.innerHTML = this.appInfo.appName;
		$('body').append(nameField);
	},

	renderFormField: function() {
		var linkForm = document.createElement('form');

		var linkInput = document.createElement('input');
		linkInput.type = 'text';
		linkInput.name = 'playlist-link';

		var submitLinkBtn = document.createElement('input');
		submitLinkBtn.type = 'submit';
		submitLinkBtn.name = 'submit-link-btn';

		var newLinkBtn = document.createElement('button');
		newLinkBtn.type = 'button';
		newLinkBtn.innerHTML = 'New Playlist';

		linkForm.append(linkInput);
		linkForm.append(newLinkBtn);
		linkForm.append(submitLinkBtn);

		$('body').append(linkForm);		
	},
}

homePageView.init();