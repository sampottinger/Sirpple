/**
 * Javascript representation / wrapper of server REST API for 
 * transfer of model data
 * @author Sam Pottinger
**/

function ModelGateway(modelName, parentName)
{

	/**
	 * Gets all of the instances of this gateway's model that have
	 * a parent with the provided ID
	 * @param {Integer} parentID The id of the parent whose children
	 *                           are desired
	 * @param {Function} callback The function to call after finishing
	 * @returns {List} List of models retrieved from the server
	**/
	this.getAll = function(parentID, callback)
	{
		var url = sprintf("/%s/%d/%ss", this.parentName, parentID, this.modelName);
		$.getJSON(url, callback);
	}

	/**
	 * Gets an instance of this gateway's model by id
	 * @param {Integer} parentID The id of the instance desired
	 * @param {Function} callback THe function to call after finishing
	 * @param {Object} instance retrieved from server
	**/
	this.get = function(targetID, callback)
	{
		var url = sprintf("/%s/%d", this.modelName, targetID);
		$.getJSON(url, callback);
	},

	/**
	 * Update an existing model
	 * @param {Object} target The object to update
	 * @param {Function} callback The function to call after finishing
	**/
	this.put = function(target, callback)
	{
		var url = sprintf("/%s/%d", this.modelName, targetID);
		var data = {"instid": target.instid, "method": "put", "payload": JSON.stringify(target)}
		$.ajax({
			type: 'POST',
			url: url,
			data: data,
			success: callback,
			dataType: "json"
		});
	},

	/**
	 * Creates a new instance of this gateway's model
	 * @param {Integer} parentID The id of the parent for this new model
	 * @param {Object} target The object to upload
	 * @param {Function} callback The function to call after finishing
	**/
	this.post = function(parentID, target, callback)
	{
		var url = sprintf("/%s/%d/%ss", this.parentName, targetID, this.modelName);
		var data = {"instid": target.instid, "method": "post", "payload": JSON.stringify(target)}
		$.ajax({
			type: 'POST',
			url: url,
			data: data,
			success: callback,
			dataType: "json"
		});
	},

	/**
	 * Deletes an instance of this gateway's model class
	 * @param {Object} target The object to delete from the server
	 * @param {Function} callback The function to call after finishing
	**/
	this.del = function(target, callback)
	{
		var url = sprintf("/%s/%d", this.modelName, targetID);
		var data = {"instid": target.instid, "method": "delete", "payload": JSON.stringify(target)}
		$.ajax({
			type: 'POST',
			url: url,
			data: data,
			success: callback,
			dataType: "json"
		});
	}

}
