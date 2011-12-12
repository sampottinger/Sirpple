/**
 * Factory to create novel instances of models and to perform lookups
 * @author Sam Pottinger
**/

CLASS_SPECIFICATION_URL = "/configuration/models/models.yaml";

/**
 * Factory to create new model gateways from YAML server
 * config files
**/
var ModelFactory = function()
{
    
    /**
     * Creates a new model factory that has all of the class
     * definitions available
     * @param {Function} readyFunction The function to call when this factory is ready
    **/
    this.waitingRequests = 1;

    /**
     * Save the class specification 
    **/
    this.loadClassSpecification = function(data, textStatus, jqXHR)
    {
        this.classSpecification = jsyaml.safeLoad(data);
        alert(this.classSpecification);
    };

    this.getModelGateway = function(name)
    {
        
    };

    // Ask server for model definitions
    $.ajax({
        url: CLASS_SPECIFICATION_URL,
        success: this.loadClassSpecification
    });
};