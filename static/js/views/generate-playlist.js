var newPlaylistView = {

	init: function() {
		this.render();
	},

	render: function() {
		this.renderTitleField();
		this.renderFormField();
	},

	renderTitleField: function() {
		var titleField = document.createElement('h1');
		titleField.innerHTML = "Create New Playlist";
		$('body').append(titleField);
	},

	renderFormField: function() {
		var registerForm = document.createElement('form');

		var emailInput = document.createElement('input');
		emailInput.type = 'text';
		emailInput.name = 'email';
		emailInput.placeholder = 'Email';

		var pwInput = document.createElement('input');
		pwInput.type = 'password';
		pwInput.name = 'password';
		pwInput.placeholder = 'Password';

		var confirmPwInput = document.createElement('input');
		confirmPwInput.type = 'password';
		confirmPwInput.name = 'confirm-password';
		confirmPwInput.placeholder = 'Confirm Password';

		var submitBtn = document.createElement('input');
		submitBtn.type = 'submit';
		submitBtn.name = 'submit-link-btn';
		submitBtn.innerHTML = "Create New Playlist";

		registerForm.append(emailInput);
		registerForm.append(pwInput);
		registerForm.append(confirmPwInput);
		registerForm.append(submitBtn);

		$('body').append(registerForm);		
	},
}

newPlaylistView.init();