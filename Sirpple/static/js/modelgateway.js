/**
 * Javascript representation / wrapper of server REST API for 
 * transfer of model data
 * @author Sam Pottinger
**/

$.include('/static/jslibs/base2.js');

var modelgateway
{

	/**
	 * Client-side model wrapper around REST API for a model
	**/
	var ModelGateway = new base2.Base;
	Model.extend({
		
		/**
		 * Creates a new model gateway around the given model class name
		 * @param {String} fullName The full name of the model class this
		 *                          gateway will provide access to,
		 *                          including 
		 * @param {String} parentName The name of the parent class of this class 
		**/
		constructor: function(fullName, parentName)
		{
			this.parentName = parentName
			this.fullName = fullName;
			parts = this.fullName.split(".")
			if(parts.length == 1)
				this.modelName = parts[0]
			else
				this.modelName = parts[1]
		},

		/**
		 * Gets all of the instances of this gateway's model that have
		 * a parent with the provided ID
		 * @param {Integer} parentID The id of the parent whose children
		 *                           are desired
		 * @param {Function} callback The function to call after finishing
		 * @returns {List} List of models retrieved from the server
		**/
		getAll: function(parentID, callback)
		{
			var url = sprintf("/%s/%d/%ss", this.parentName, parentID, this.modelName);
			$.getJSON(url, callback);
		},

		/**
		 * Gets an instance of this gateway's model by id
		 * @param {Integer} parentID The id of the instance desired
		 * @param {Function} callback THe function to call after finishing
		 * @param {Object} instance retrieved from server
		**/
		get: function(targetID, callback)
		{
			var url = sprintf("/%s/%d", this.modelName, targetID);
			$.getJSON(url, callback);
		},

		/**
		 * Update an existing model
		 * @param {Object} target The object to update
		 * @param {Function} callback The function to call after finishing
		**/
		put: function(target, callback)
		{
			
		},

		/**
		 * Creates a new instance of this gateway's model
		 * @param {Integer} parentID The id of the parent for this new model
		 * @param {Object} target The object to upload
		 * @param {Function} callback The function to call after finishing
		**/
		post: function(parentID, target, callback)
		{
			
		},

		/**
		 * Deletes an instance of this gateway's model class
		 * @param {Object} target The object to delete from the server
		 * @param {Function} callback The function to call after finishing
		**/
		del: function(target, callback)
		{
			
		}

	})

}