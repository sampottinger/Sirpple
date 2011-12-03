/**
 * Factory to create novel instances of models and to perform lookups
 * @author Sam Pottinger
**/

$.include('jslibs/base.js');
$.include('jslibs/yaml.js');

var modelfactory = {

	/**
	 * Factory to create new model factories from YAML server
	 * config files
	**/
	var ModelFactoryConstructor = Base.extend({

		/**
		 * Create a new factory from the YAML config files on the server
		**/
		createFactory: function()
		{
			
		}

	},
	{
		__instance = null,

		/**
		 * Gets a shared instance of this constructor singleton,
		 * creating it if necessary
		 * @returns {ModelFactoryConstructor} Shared ModelFactoryConstructor
		**/
		getInstance: function()
		{
			if(ModelFactory.__instance == null)
				ModelFactory.__instance = ModelFactory();
			
			return ModelFactory.__instance;
		}
	});

}