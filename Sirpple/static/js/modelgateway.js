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
		 * @param {String} modelName The name of the model class this
		 *                           gateway will provide access to
		**/
		constructor: function(modelName)
		{
			this.modelName = modelName;
		}

	})

}