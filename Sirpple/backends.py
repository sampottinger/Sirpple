"""
Module that abstracts away the backend database / framework
"""

import adapted_models

try:
    from google.appengine.ext import db
except ImportError:
    db = None # dont fail for on-the-ground testing

# TODO: Push this out to a config file, scoping is important
BACKEND = "GAE"

class DatabaseManager:
    """
    Database manager that resolves names of property classes to actual property classes
    """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this DatabaseManager singleton

        @return: Shared DatabaseManager instance
        @rtype: DatabaseManager
        """
        if DatabaseManager.__instance == None:
            DatabaseManager.__instance = DatabaseManager()
        
        return DatabaseManager.__instance

    def __init__(self):
        pass

    def get_property_definition_factory(self):
        """
        Gets the database specific property definition factory

        @return: PropertyDefinitionFactory implementor
        @rtype: Subclass of PropertyDefinitionFactory
        """
        # TODO: Switch on this, scoping is important
        return GAEPropertyDefinitionFactory.get_instance()

    def get_property_class(self, name, params):
        """
        Gets the database specific property class given the name of that property

        @param name: The name of the property to resolve
        @type name: String
        @param params: List of parameters to pass to the constructor of this property
        @type params: List
        @return: Database specific property class 
        @rtype: Class
        """
        # TODO: Switch on backend, scoping is important
        return getattr(db, name)(**params)
    
    def get_default_base_class(self):
        """
        Gets the database specific base class for models

        @return: Backend specific base class
        @rtype: Python class
        """
        # TODO: Switch on backend
        return adapted_models.GAEAdaptedModel

class PropertyDefinitionFactory:
    """
    Factory that produces database specific property definitions

    @note: Abstract class, must use implementor
    """

    def __init__(self):
        pass
    
    def get_definition(self, config_name, db_class_name, parameters):
        """
        Gets the appropriate definition for the given type of property

        @param config_name: The name of the property in the configuration file
        @type config_name: String
        @param parameters: The parameters used to initalize this property
        @type parameters: Dictionary
        @param db_class_name: The property class in the database
        @type db_class_name: Class
        """
        raise NotImplementedError("Must use implementor of this PropertyDefintionFactory")

class GAEPropertyDefinitionFactory(PropertyDefinitionFactory):
    """ Google App Engine specific property definition factory """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this GAEPropertyDefinitionFactory singleton

        @return: Shared GAEPropertyDefinitionFactory instance
        @rtype: GAEPropertyDefinitionFactory
        """
        if GAEPropertyDefinitionFactory.__instance == None:
            GAEPropertyDefinitionFactory.__instance = GAEPropertyDefinitionFactory()
        
        return GAEPropertyDefinitionFactory.__instance

    def __init__(self):
        PropertyDefinitionFactory.__init__(self)
    
    def get_definition(self, config_name, db_class_name, parameters):
        if db_class_name == "ReferenceProperty":
            return GAEReferencePropertyDefinition(config_name, db_class_name, parameters)
        else:
            return SimplePropertyDefinition(config_name, db_class_name, parameters)

class PropertyDefinition:
    """ 
    Definition of a property as part of a database model 

    @note: Abstract class, must use implementor
    """

    def __init__(self, config_name, db_class_name, parameters):
        """ 
        Conversion between a property type name in a configuration file and a property as defined by the underlying database

        @param config_name: The name of the property in the configuration file
        @type config_name: String
        @param parameters: The parameters used to initalize this property
        @type parameters: Dictionary
        @param db_class_name: The property class in the database
        @type db_class_name: Class
        """
        # Shameless TODO: These are effectively private . . . getters would be nice. Setting is evil.
        self.config_name = config_name
        self.db_class_name = db_class_name
        self.parameters = parameters
    
    def is_actual_property(self):
        """
        Inidicates if a property should be ignored because it is a built-in

        @return: True if this should be added to the property. False if it should be ignored.
        @rtye: Boolean
        """
        return True
    
    def is_built_in(self, field_name):
        """
        Determines if this property is a built-in or if it is an actual model property to be added

        @param field_name: The name of the field in the model this property type would be used for
        @type field_name: String
        @return: True if built-in (and should not be created) and False if it should be added to the model
        @rtype: Boolean
        """
        return True
    
    def get_property(self, field_name):
        """
        Gets the db class this property defintion encloses

        @param field_name: What this property will be called on the final model
        @type field_name: String
        @return: Instance of the property this definition encloses
        @rtype: Python instance or None if a built-in
        """
        raise NotImplementedError("Must use implementor of PropertyDefinition")

class SimplePropertyDefinition(PropertyDefinition):
    """
    Definition of a property as a database model that does not require any special parameters
    """

    def get_property(self, field_name):
        return DatabaseManager.get_instance().get_property_class(self.db_class_name, self.parameters)

class GAEReferencePropertyDefinition(PropertyDefinition):
    """
    Reference property definitions that require a collection name
    """

    def get_property(self, field_name):
        if self.is_built_in(field_name):
            return None
        else:
            params = self.parameters
            params["collection_name"] = field_name + "_collection"
            return DatabaseManager.get_instance().get_property_class(self.db_class_name, self.parameters)
    
    def is_built_in(self, field_name):
        return field_name == "parent";

class EmptyReferenePropertyDefinition(PropertyDefinition):
    """
    Reference property definitions that should not actually be properties (built-ins)
    """

    def get_property(self, field_name):
        return None
    
    def is_actual_property(self):
        return False