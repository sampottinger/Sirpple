/**
 * Javascript representation / wrapper of server REST API for 
 * transfer of model data
 * @author Sam Pottinger
**/

$.include('jslibs/base.js');

var model = {

	var Model = Base.extend({

		/**
		 * Constructor for model
		 * @param url The REST URL for this model
		 * @type url String
		 * @param spec The description of this model.
		 *             Contains keys of property names and values of types
		 * @type spec Javascript Object / Dict
		 */
		constructor: function(url, spec) {
			this.url = url;
			this.spec = spec
		},
		
		url: "",
		
		/**
		 * Pushes this model instance to the server
		**/
		create: function() {

			this.__pushToServer("POST");

		},
		
		/**
		 * Reads the updated state of this instance
		**/
		read: function() {
			$.ajaxSetup({async:false});
			$.ajax({
				type: "GET",
				url: this.url,
				dataType: json,
				success: this.__update
			});
			$.ajaxSetup({async:true});
		},

		/**
		 * Pushes the current state of this instance back to the server
		**/
		update: function() {

			this.__pushToServer("PUT");

		},

		/**
		 * Deletes this instance from the server's database
		**/
		delete: function() 
		{

			this.__pushToServer("DELETE");

		},

		/**
		 * Update the internals of this object from state recieved from
		 * server
		 * @param state The state recieved from the server
		 * @type state Dict
		**/
		__update: function(state)
		{
			// Create list of values to send back to the server
			var vals = this.__toDict();

			// Indicate real method use
			vals["__method"] = "PUT";

			for(property in this.spec)
				this[property] = state[property];
		},

		/**
		 * Create a dictionary representation (DTO) for this model
		 * @returns {Dict} DTO version of this model instance
		**/
		__toDict: function() {

			// Associative array to hold serializable properties
			var vals = Array(); 

			// Iterate through spec to build DTO
			for(property in this.spec)
				vals[property] = this[property];
			
			return vals;
		},

		/**
		 * Pushes the state of this model instance to the server
		 * @param method The method to use to push this model to the server
		 * @type method String
		**/
		__pushToServer: function(method) {
			// Create list of values to send back to the server
			var vals = this.__toDict();

			// Indicate real method use
			vals["__method"] = method;

			for(property in this.spec)
				this[property] = state[property];
		}
	});

}