/**
 * Factory to create novel instances of models and to perform lookups
 * @author Sam Pottinger
**/

$.include('/static/jslibs/base2.js');
$.include('/static/jslibs/js-yaml.min.js');
$.include('/static/js/model.js');

var modelfactory
{
    CLASS_SPECIFICATION_URL = "/configuration/models/models.yaml";

    $(document).ready(function() {

        /**
         * Factory to create new model gateways from YAML server
         * config files
        **/
        var ModelFactory = new base2.Base;
        ModelFactory.extend({

            instance: null,

            /**
             * Gets a shared instance of this constructor singleton,
             * creating it if necessary
             * @returns {ModelFactoryConstructor} Shared ModelFactoryConstructor
            **/
            getInstance: function()
            {
                if(this.instance == null)
                    this.instance = new ModelFactory();
                
                return this;
            }

        },
        {
            
            /**
             * Creates a new model factory that has all of the class
             * definitions available
             * @param {function} readyFunction The function to call when this factory is ready
            **/
            constructor: function(readyFunction) {

                this.readyFunction = readyFunction;
                this.waitingRequests = 1;
                
                // Ask server for model definitions
                $.ajax({
                    url: CLASS_SPECIFICATION_URL,
                    success: this.loadClassSpecification
                });

            },

            /**
             * Save the class specification 
            **/
            loadClassSpecification: function(data, textStatus, jqXHR)
            {
                this.classSpecification = jsyaml.safeLoad(data);
            }

        });

    });

}