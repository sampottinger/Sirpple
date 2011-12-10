""" Database specific property definitions and the classes that support them """

from serialization import model_spec

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
            if config_name == "parent":
                return GAEParentPropertyDefinition(config_name, db_class_name, parameters)
            else:
                return GAEReferencePropertyDefinition(config_name, db_class_name, parameters)
        else:
            return SimplePropertyDefinition(config_name, db_class_name, parameters)

class SimplePropertyDefinition(model_spec.PropertyDefinition):
    """
    Definition of a property as a database model that does not require any special parameters
    """

    def get_property(self, field_name):
        return PlatformManager.get_instance().get_property_class(self.db_class_name, self.parameters)

class EmptyReferenePropertyDefinition(model_spec.PropertyDefinition):
    """
    Reference property definitions that should not actually be properties (built-ins)
    """

    def get_property(self, field_name):
        return None
    
    def is_built_in(self, field_name):
        return True

class GAEReferencePropertyDefinition(model_spec.PropertyDefinition):
    """
    Reference property definitions that require a collection name
    """

    def get_property(self, field_name):
        if self.is_built_in():
            return None
        else:
            params = self.parameters
            params["collection_name"] = field_name + "_collection"
            return PlatformManager.get_instance().get_property_class(self.db_class_name, self.parameters)
    
    def is_reference(self):
        return True

class GAEParentPropertyDefinition(GAEReferencePropertyDefinition):
    """
    Reference property definitions for parent relationships
    """

    def is_built_in(self):
        return True
