"""
Module containing classes for serialzation between JSON and Python classes defined by configuration files
"""
from glob import glob
from configparser import get_parser
import os
import logging
import backends

class ConfigModelFactory:
    """ Factory that produces model classes and instances from configuration specs """

    DEFAULT_PARENT_CLASS = backends.DatabaseManager.get_instance().get_default_base_class()
    DEFAULT_PARENT_CLASS_DESCRIPTOR = "DefaultBase"

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
        Constructor for ConfigModelFactory

        @param class_definitions: The classes to run through this factory
        @type class_definitions: Dictionary of String to ClassDefinition
        @param property_definitions: The properties these classes use
        @type property_definitions: Dictionary of String to PropertyDefinition
        """
        self.reset()
    
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
    
    def get_class(self, name):
        """
        Gets a registered model by name

        @param name: The name of the model to lookup
        @type name: String
        @return: The requested model
        @rtype: ClassDefinition
        """
        
        if name == ConfigModelFactory.DEFAULT_PARENT_CLASS_DESCRIPTOR:
            return ConfigModelFactory.DEFAULT_PARENT_CLASS
        
        if not name in self.__class_definitions:
            raise ValueError(name + " has not been registered as model")

        return self.__class_definitions[name]
    
    def get_classes(self):
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

        return FieldDefinition(name, field_type)
    
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

class FieldDefinition:
    """ Definition of a field as part of a database model """

    def __init__(self, name, field_type):
        """
        Constructor for a Field

        @param name: The name of this field
        @type name: String
        @param field_type: Description of this field's type as indicated in the configuration file
        @type field_type: String
        """
        self.__name = name
        self.__field_type = field_type
    
    def get_name(self):
        """
        Get the database-recognized name of this field

        @return: String name of this field
        @rtype: String
        """
        return self.__name
    
    def get_field(self):
        """
        Generates a Python native field for this field definition

        @return: Python native field to use
        @rtype: Python native field
        """
        factory = ConfigModelFactory.get_instance()
        field = factory.get_property_instance(self.__field_type, self.__name)
        return field

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
            parent_class_name = ConfigModelFactory.DEFAULT_PARENT_CLASS_DESCRIPTOR
        class_factory = ConfigModelFactory.get_instance()

        return ClassDefinition(name, fields, parent_class_name)
    
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

class ClassDefinition:
    """ Definition of a model loaded through a configuration secification """

    def __init__(self, name, fields, parent_class):
        """
        Constructor for ClassDefintion

        @param name: The name of this class
        @type name: String
        @param fields: Dictionary of fields from field names to actual fields
        @type fields: Dictionary from String to FieldDefinition
        @param parent_class: The name of the class to use as this class' parent
        @type parent_class: String
        """
        self.__fields = fields
        self.__name = name
        self.__parent_class_name = parent_class
    
    def get_name(self):
        """
        Determine which class this definition goes with

        @return: The name of the class corresponding to this definition
        @rtype: String
        """
        return self.__name

    def get_fields(self):
        """
        Returns all of the fields / properties this class definition currently has

        @return: Dicationary of fields
        @rtype: Dictionary from String to FieldDefition
        """
        return self.__fields
    
    def get_class(self):
        """
        Gets the Python version of this class

        @return: The Python native copy of this loaded class
        @rtype: Class which is a child of PARENT_CLASS
        """

        python_fields = {}

        for field_name in self.__fields:
            python_fields[field_name] = self.__fields[field_name].get_field()
        
        class_factory = ConfigModelFactory.get_instance()

        parent_class = class_factory.get_class(self.__parent_class_name)

        return type(self.__name, (parent_class,), python_fields)

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
        return ConfigModelFactory.get_instance()
    
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
        factory = ConfigModelFactory.get_instance()
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
        factory = ConfigModelFactory.get_instance()
        factory.add_property_definitions(property_definitions)

        return factory