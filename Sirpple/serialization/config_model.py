"""
Classes for the management of model specifications and classes loaded from configuration files
"""

import backends
import model_spec

class ConfigModelFactory:
    """ Factory that produces model classes and instances from configuration specs """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this ConfigModelFactory singleton

        @return: Shared ConfigModelFactory instance
        @rtype: ConfigModelFactory
        """
        if ConfigModelFactory.__instance == None:
            ConfigModelFactory.__instance = ConfigModelFactory()
        
        return ConfigModelFactory.__instance
    
    def __init__(self):
        """
        Constructor for ConfigModelFactory that lazily loads class constants
        """
        self.reset()
        default_class = backends.DatabaseManager.get_instance().get_default_base_class()
        ConfigModelFactory.DEFAULT_PARENT_CLASS_DEFINTION = model_spec.WrappedClassDefinition(default_class, [])
    	ConfigModelFactory.DEFAULT_PARENT_CLASS_DESCRIPTOR = "DefaultBase"
    
    def reset(self):
        """
        Resets this factory back to its original state before added classes
        """

        self.__class_definitions = {}
        self.__property_definitions = {}

    def add_class_definitions(self, class_definitions):
        """
        Establishes additional class definitions in use by this application

        @param class_definitions: New class names to map to ClassDefinitions
        @type class_definitions: Dictionary from String to ClassDefinition
        """
        self.__class_definitions.update(class_definitions)
    
    def add_property_definitions(self, property_definitions):
        """
        Establishes additional property definitions in use by this application

        @param property_definitions: Dictionary of additional property names to use in configuration and those in use in the target database
        @type property_definitions: Dictionary from String to PropertyDefinition
        """
        self.__property_definitions.update(property_definitions)
    
    def get_class_definition(self, name):
        """
        Gets a registered model by name

        @param name: The name of the class definition to lookup
        @type name: String
        @return: The requested class definition
        @rtype: ClassDefinition
        """
        
        if name == ConfigModelFactory.DEFAULT_PARENT_CLASS_DESCRIPTOR:
            return ConfigModelFactory.DEFAULT_PARENT_CLASS_DEFINTION
        
        if not name in self.__class_definitions:
            raise ValueError(name + " has not been registered as model")

        return self.__class_definitions[name]
    
    def get_class_definitions(self):
        """
        Determines all of the class definitions defined in this factory

        @return: A dictionary of class definitions defined in this factory with the model names as keys
        @rtype: Dictionary of String to ClassDefinitions
        """
        ret_dict = {}
        ret_dict.update(self.__class_definitions)
        
        return ret_dict
    
    def get_model(self, name):
        """
        Gets a registered model by name

        @param name: The name of the model to lookup
        @type name: String
        @return: The requested model
        @rtype: Class
        """
        
        return self.get_class_definition(name).get_class()
    
    def get_models(self):
        """
        Determines all of the model classes defined in this factory

        @return: A dictionary of model classes defined in this factory with the model names as keys
        @rtype: Dictionary of String to Class
        """
        ret_dict = {}
        for model_name in self.__class_definitions:
            ret_dict[model_name] = self.__class_definitions[model_name].get_class()
        
        return ret_dict
    
    def is_property_built_in(self, class_name, field_name):
        """
        Determines if a property is built-in or if it needs to be added explicitly

        @param class_name: The name of the class to look up as defined in configuration
        @type class_name: String
        @param field_name: The name of this field this property would be called (used by some backends)
        @type field_name: String
        @return: True if it is a built-in and False otherwise
        @rtype: Boolean
        """
        if not class_name in self.__property_definitions:
            raise ValueError(class_name + " does not have a corresponding database property registered. Check your types yaml file.")
        return self.__property_definitions[class_name].is_built_int(field_name)
    
    def get_property_instance(self, class_name, field_name):
        """
        Get an instance of the class corresponding to the provided class name for a property

        @param class_name: The name of the class to look up as defined in configuration
        @type class_name: String
        @param field_name: The name of this field this property will be called (used by some backends)
        @type field_name: String
        @return: Property corresponding to the provided name
        @rtype: Class
        """
        if not class_name in self.__property_definitions:
            raise ValueError(class_name + " does not have a corresponding database property registered. Check your types yaml file.")
        return self.__property_definitions[class_name].get_property(field_name)
    
    def get_property_definition(self, class_name):
    	"""
    	Find the definition of type corresponding to the given property name

    	@param class_name: The name of the class to look up as defined in configuration
        @type class_name: String
        @return: Property definitions corresponding to the provided name
        @rtype: PropertyDefinition
        """
        if not class_name in self.__property_definitions:
            raise ValueError(class_name + " does not have a corresponding database property registered. Check your types yaml file.")
        return self.__property_definitions[class_name]
    
    def to_python(self, foreign_object, class_name):
        """
        Converts the client provided foreign_object to a native Python model

        @param foreign_object: The object to parse
        @type foreign_object: Dictionary of String property names to values
        @param class_name: The name of the class the provided foreign object will be parse to
        @type class_name: String
        @return: Python native instance
        @rtype: instance
        """
        class_definition = self.__class_definitions[model_name]
        target_class = class_definition.get_class()
        return target_class(**foreign_object)
