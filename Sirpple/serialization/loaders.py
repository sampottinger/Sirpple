"""
Module containing classes for serialzation between JSON and Python classes defined by configuration files
"""
from glob import glob
import os
import logging
import backends

from configparser import get_parser
import model_spec
import config_model

class PropertyDefinitionLoader:
    """ Factory that creates PropertyDefinition """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this PropertyDefinitionLoader singleton

        @return: Shared PropertyDefinitionLoader instance
        @rtype: PropertyDefinitionLoader
        """
        if PropertyDefinitionLoader.__instance == None:
            PropertyDefinitionLoader.__instance = PropertyDefinitionLoader()
        
        return PropertyDefinitionLoader.__instance
    
    def get_properties(self, sources):
        """
        Create PropertyDefinitions from a list of source dictionaries

        @param sources: Dictionaries used to create these definitions
        @type sources: List of dictionaries
        @return: Newly created definitions in dictionary mapping configuration name to definition
        @rtype: Dictionary of PropertyDefinitions
        """
        ret_dict = {}

        for source in sources:
            ret_dict[source] = self.get_property(source, sources[source])
        
        return ret_dict
    
    def get_property(self, config_name, source):
        """
        Loads a property from the given dictionary or string representation of it

        @param config_name: The name that this property is given in configuration files
        @type config_name: String
        @param source: Dictionary or String describing this property
        @type source: Dictinonary or String
        @return: The property extracted from the given dictionary
        @rtype: PropertyDefinition or None if property should be ignored (built-in)
        """
        if isinstance(source, str):
            db_class_name = source
            parameters = {}
        else:
            db_class_name = source["db_type"]
            parameters = source["parameters"]
        
        factory = backends.DatabaseManager.get_instance().get_property_definition_factory()
        return factory.get_definition(config_name, db_class_name, parameters)

class FieldDefinitionFactory:
    """ 
    Factory that creates field definitions from dictionaries
    """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this FieldDefinitionFactory singleton

        @return: Shared FieldDefinitionFactory instance
        @rtype: FieldDefinitionFactory
        """
        if FieldDefinitionFactory.__instance == None:
            FieldDefinitionFactory.__instance = FieldDefinitionFactory()
        
        return FieldDefinitionFactory.__instance
    
    def get_field(self, name, source):
        """
        Converts the dictionary in source to a field definition

        @param name: The name of this new field
        @type name: String
        @param source: The dictionary or String to convert from
        @type source: Dictionary or String
        @return: Instantiated field definition
        @rtype: FieldDefinition
        """

        field_type = source

        return model_spec.FieldDefinition(name, field_type)
    
    def get_fields(self, sources, inc_builtins=False):
        """
        Converts the list of dictionaries in sources to fields

        @param sources: List of dictionaries to convert from
        @type sources: List of Dictionary
        @keyword inc_builtins: If True, reported builtins will be converted
        @type inc_builtins: Boolean
        @return: Dictionary of instantiated fields
        @rtype: Dictionary from String to field
        """
        ret_val = {}

        for source in sources:
            new_field = self.get_field(source, sources[source])
            ret_val[source] = new_field
        
        return ret_val

class ClassDefinitionFactory:
    """ Factory that creates class definitions from dictionaries """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this ClassDefinitionFactory singleton

        @return: Shared ClassDefinitionFactory instance
        @rtype: ClassDefinitionFactory
        """
        if ClassDefinitionFactory.__instance == None:
            ClassDefinitionFactory.__instance = ClassDefinitionFactory()
        
        return ClassDefinitionFactory.__instance
    
    def get_class(self, full_name, source):
        """
        Creates a new definition from the provided source dictionary

        @param full_name: The name (along with its parent class) of this new class
        @type full_name: String
        @param source: The dictionary to load this class definition from
        @type source: Dictionary
        @return: New class definition
        @rtype: ClassDefinition
        """
        
        # Construct fields
        field_factory = FieldDefinitionFactory.get_instance()
        fields = field_factory.get_fields(source)

        name_parts = full_name.split(".")
        if len(name_parts) == 2:
            parent_class_name = name_parts[0]
            name = name_parts[1]
        else:
            name = name_parts[0]
            parent_class_name = config_model.ConfigModelFactory.get_instance().DEFAULT_PARENT_CLASS_DESCRIPTOR
        class_factory = config_model.ConfigModelFactory.get_instance()

        return model_spec.ClassDefinition(name, fields, parent_class_name)
    
    def get_classes(self, sources):
        """
        Creates new definitions from the list of provided source dictionaries

        @param sources: The sources to create the definitions from
        @type sources: List of dictionaries
        @return: Dictionary of new class definitions
        @rtype: Dictionary
        """
        ret_val = {}

        for source in sources:
            definition = self.get_class(source, sources[source])
            ret_val[source] = definition
        
        return ret_val

class ConfigModelFactoryMechanic:
    """
    ConfigModelFactory factory that produces ConfigModelFactory driven by values loaded from configuration files
    """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this ConfigModelFactoryMechanic singleton

        @return: Shared ConfigModelFactoryMechanic instance
        @rtype: ConfigModelFactoryMechanic
        """
        if ConfigModelFactoryMechanic.__instance == None:
            ConfigModelFactoryMechanic.__instance = ConfigModelFactoryMechanic()
        
        return ConfigModelFactoryMechanic.__instance
    
    def __init__(self):
        """
        Constructor for ConfigModelFactory

        @note: This is a singleton and this should not be called externally
        """
        pass
    
    def __get_files_from_dir(self, directory, extension):
        """
        Generates a list of all the files in a folder ending in the given extension

        @param directory: Path to the directory to look through
        @type directory: String
        @param extension: The extension to look for in file names (ie yaml). Do not include "dot" or "."
        @type extension: String
        """
        glob_path = os.path.normpath(os.path.join(directory,'*.' + extension))
        return glob(glob_path)
    
    def load_factory_from_config(self, language, guiding_configuration):
        """
        Loads a single configuration to drive the creation of a ConfigModelFactory

        @param guiding_configuration: Encoded string with configuration containing other configuration files to use
        @type guiding_configuration: String
        @return: Modified shared instance of ConfigModelFactory
        @rtype: ConfigModelFactory
        """
        parser = get_parser(language)

        overall_configuration = parser.loads(guiding_configuration)

        # Check for desired properties
        if not "classes" in overall_configuration:
            raise ValueError("No classes configuration specified")
        if not "properties" in overall_configuration:
            raise ValueError("No properties configuration specified")
        
        # Find directories
        class_definition_dir = overall_configuration["classes"]
        properties_definition_dir = overall_configuration["properties"]

        # Load files
        # WARNING: language name passed as file extension (yaml -> .yaml)
        for filename in self.__get_files_from_dir(class_definition_dir, language):

            with open(filename) as f:
                self.configure_factory_classes(language, f.read())
        
        for filename in self.__get_files_from_dir(properties_definition_dir, language):

            with open(filename) as f:
                self.configure_factory_properties(language, f.read())

        # Create factory
        return config_model.ConfigModelFactory.get_instance()
    
    def configure_factory_classes(self, language, class_definition_str):
        """
        Configures ConfigModelFactory models from the provided configuration formatted strings

        @param language: The language the config files are written in
        @type language: String
        @param class_definition_str: The string containing information about class definitions
        @type class_definition_str: String
        @return: Modified shared instance of ConfigModelFactory
        @rtype: ConfigModelFactory
        """

        parser = get_parser(language)
        class_definitions_raw = parser.loads(class_definition_str)
        
        # Convert dictionaries to class definitions and property definitions
        class_factory = ClassDefinitionFactory.get_instance()
        class_defintions = class_factory.get_classes(class_definitions_raw)
        
        # Get the current factory 
        factory = config_model.ConfigModelFactory.get_instance()
        factory.add_class_definitions(class_defintions)

        return factory
    
    def configure_factory_properties(self, language, property_definition_str):
        """
        Configures ConfigModelFactory type mapping from the provided configuration formatted strings

        @param property_definition_str: The string containing information about class definitions
        @type property_definition_str: String
        @return: Modified shared instance of ConfigModelFactory
        @rtype: ConfigModelFactory
        """

        parser = get_parser(language)
        property_definitions_raw = parser.loads(property_definition_str)

        # Convert dictionaries to class definitions and property definitions
        property_factory = PropertyDefinitionLoader.get_instance()
        property_definitions = property_factory.get_properties(property_definitions_raw)

        # Get the current factory 
        factory = config_model.ConfigModelFactory.get_instance()
        factory.add_property_definitions(property_definitions)

        return factory