steal(
	'./sirpple.css', 			// application CSS file
	'./css/awesome-buttons.css',
	'./models/models.js',		// steals all your models
	'./fixtures/fixtures.js',	// sets up fixtures for your models
	'sirpple/project/create',
	'sirpple/project/list',
	'sirpple/game_object/create',
	'sirpple/game_object/list',
	'./css/start/jquery-ui-1.8.16.custom.css',
	'./js/jquery-ui.js',
	function(){					// configure your application
		
		$('#projects').sirpple_project_list();
		$('#create').sirpple_project_create();
});