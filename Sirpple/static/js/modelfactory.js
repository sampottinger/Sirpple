/**
 * Factory to create novel instances of models and to perform lookups
 * @author Sam Pottinger
**/

CLASS_SPECIFICATION_URL = "/configuration/models/models.yaml";

window.modelFactory = null;

/**
 * Factory to create new model gateways from YAML server
 * config files
**/
function ModelFactory(spec)
{
    
    this.spec = spec;
    this.gateways = {};

    for(var fullName in spec)
    {
        if("parent" in spec[fullName])
            parentName = spec[fullName]["parent"]
        else if(".parent" in spec[fullName])
            parentName = spec[fullName][".parent"]
        else
            parentName = "none"

        parts = fullName.split(".")
        if(parts.length == 1)
            modelName = parts[0]
        else
            modelName = parts[1]
        
        this.gateways[modelName] = new ModelGateway(modelName, parentName);
    }

    this.getModelGateway = function(name)
    {
        return this.gateways[name];
    }

};

function buildFactory(data, textStatus, jqXHR)
{
    var parsedData = jsyaml.safeLoad(data);
    window.modelFactory = new ModelFactory(parsedData);
}

// Ask server for model definitions
$.ajax({
    url: CLASS_SPECIFICATION_URL,
    success: buildFactory
});