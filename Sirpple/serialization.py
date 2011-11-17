"""
Module containing classes for serialzation between JSON and Python classes defined by configuration files
"""

from google.appengine.ext import db

class ParserAdapter:
    """ Fully abstract parser interface """

    def loads(self, source):
        """
        Loads the data saved in the provided string

        @param source: The sourceing to load form
        @type source: String
        @return: Dictionary loaded from string
        @rtype: Dictionary
        """
        raise NotImplementedError("Need to use subclass of this interface")

class YamlAdapter(ParserAdapter):
    """ Adapts the pyyaml YAML parser to the generic parser """

    def __init__(self):
        ParserWrapper.__init__(self)
    
    def loads(self, source):
        """
        Loads the data saved in the provided string

        @param source: The string to load form
        @type source: String
        @return: Dictionary loaded from string
        @rtype: Dictionary
        """
        return pyyaml.load(source)

class PropertyDefinitionFactory:
    """ Factory that creates PropertyDefinition """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this PropertyDefinitionFactory singleton

        @return: Shared PropertyDefinitionFactory instance
        @rtype: PropertyDefinitionFactory
        """
        if PropertyDefinitionFactory.__instance == None:
            PropertyDefinitionFactory.__instance = PropertyDefinitionFactory()
        
        return PropertyDefinitionFactory.__instance
    
    def get_property(self, source):
        """
        Create a PropertyDefinition from the source dictionary

        @param source: The dictionary to use to create this definition
        @type source: Dictionary
        @return: Newly created definition
        @rtype: PropertyDefinition
        """

        # Ensure necessary key values 
        if not "config_name" in source:
            raise ValueError("Property definition did not contain a config_name")

        if not "db_class_name" in source:
            raise ValueError("Property definition did not contain a db_class_name")
        
        # Construct properties
        config_name = source["config_name"]
        db_class_name = source["db_class_name"]

        # Create definition
        return PropertyDefinition(config_name, db_class_name)
    
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
            definition = self.get_property(source)
            ret_dict[definition.get_name()] = definition
        
        return ret_dict

class PropertyDefinition:
    """ Definition of a property as part of a database model """

    def __init__(self, config_name, db_class_name):
        """ 
        Conversion between a property type name in a configuration file and a property as defined by the underlying database

        @param config_name: The name of the property in the configuration file
        @type config_name: String
        @param db_class_name: The property class in the database
        @type db_class_name: Class
        """
        self.__config_name = config_name
        self.__db_class_name = db_class_name
    
    def get_property(self):
        """
        Gets the db class this property defintion encloses

        @return: Class for the property this definition encloses
        @rtype: Class
        """
        return getattr(db, self.__db_class_name)

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
    
    def get_field(self, source):
        """
        Converts the dictionary in source to a field definition

        @param source: The dictionary to convert from
        @type source: Dictionary
        @return: Instantiated field definition
        @rtype: FieldDefinition
        """

        # Make sure expected properties are present
        if not "name" in source:
            raise ValueError("Expected name in field definition but not found")

        if not "field_type" in source:
            raise ValueError("Expected field_type in field definition but not found")

        if not "parameters" in source:
            raise ValueError("Expected parameters in field definition but not found")
        
        # Construct parameters
        name = source["name"]
        field_type = source["field_type"]
        parameters = source["parameters"]

        return FieldDefinition( name, field_type, parameters)
    
    def get_fields(self, sources):
        """
        Converts the list of dictionaries in sources to fields

        @param sources: List of dictionaries to convert from
        @type sources: List of Dictionary
        @return: Dictionary of instantiated fields
        @rtype: Dictionary from String to field
        """
        ret_val = {}

        for source in sources:
            new_field = self.get_field(source)
            ret_val[new_field.get_name()] = new_field
        
        return ret_val

class FieldDefintion:
    """ Definition of a field as part of a database model """

    def __init__(self, name, field_type, parameters):
        """
        Constructor for a Field

        @param name: The name of this field
        @type name: String
        @param field_type: Description of this field's type as indicated in the configuration file
        @type field_type: String
        @param parameters: The parameters used to initalize this field
        @type parameters: Dictionary
        """
        self.__name = name
        self.__field_type = field_type
        self.__parameters = parameters
    
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
        field_class = factory.get_property_class(self.__field_type)
        return field_class(**self.__parameters)

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
    
    def get_class(self, source):
        """
        Creates a new definition from the provided source dictionary

        @param source: The dictionary to load this class definition from
        @type source: Dictionary
        @return: New class definition
        @rtype: ClassDefinition
        """

        # Make sure desired fields are availble
        if not "name" in source:
            raise ValueError("Expected name in this class definition but not found")

        if not "fields" in source:
            raise ValueError("Expected fields in this class definition but not found")

        if not "parent_class" in source:
            raise ValueError("Expected parent_class in this class definition but not found")
        
        # Construct fields
        field_factory = FieldDefinitionFactory.get_instance()
        fields = field_factory.get_fields(source["fields"])

        name = source["name"]
        class_factory = ConfigModelFactory.get_instance()
        parent_class = class_factory.get_class(source["parent_class"])

        return ClassDefinition(name, fields, parent_class)
    
    def get_classes(self, sources):
        """
        Creates new definitions from the list of provided source dictionaries

        @param sources: The sources to create the definitions from
        @type sources: List of dictionaries
        @return: List of new class definitions
        @rtype: List of ClassDefinition
        """
        ret_val = {}

        for source in sources:
            definition = self.get_class(source)
            ret_val[definition.get_name()] = definition
        
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

        return type(self.__name, (parentClass,), python_fields)

class ConfigModelFactoryMechanic:
    """
    ConfigModelFactory factory that produces ConfigModelFactory driven by values loaded from configuration files
    """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this ConfigModelFactoryConstructor singleton

        @return: Shared ConfigModelFactoryConstructor instance
        @rtype: ConfigModelFactoryConstructor
        """
        if ConfigModelFactoryConstructor.__instance == None:
            ConfigModelFactoryConstructor.__instance = ConfigModelFactoryConstructor()
        
        return ConfigModelFactoryConstructor.__instance
    
    def __init__(self):
        """
        Constructor for ConfigModelFactory

        @note: This is a singleton and this should not be called externally
        """
        self.__parsers = {"yaml" : YamlAdapter()}
    
    def create_factory(self, language, class_definition_str, property_definition_str):
        """
        Creates a new ConfigModelFactory from the provided configuration formatted strings

        @param language: The language the config files are written in
        @type language: String
        @param class_definition_str: The string containing information about class definitions
        @type class_definition_str: String
        @param property_definition_str: The string containing information about class definitions
        @type property_definition_str: String
        """

        parser = self.__parsers[language]
        class_definitions_raw = parser.loads(class_definition_str)
        property_definitions_raw = parser.loads(property_definition_str)

        # Convert dictionaries to class definitions and property definitions
        class_factory = ClassDefinitionFactory.get_instance()
        class_defintions = class_factory.get_classes(class_definitions_raw)
        
        property_factory = PropertyDefinitionFactory.get_instance()
        property_definitions = property_factory.get_properties(property_definitions_raw)

        # Get the current factory 
        factory = ConfigModelFactory.get_instance()
        factory.reset()
        factory.add_class_definitions(class_defintions)
        factory.add_property_definitions(property_definitions)

class ConfigModelFactory:
    """ Factory that produces model classes and instances from configuration specs """

    DEFAULT_PARENT_CLASS = db.Model
    DEFAULT_PARENT_CLASS_DESCRIPTOR = "DefaultBase"

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this ConfigModelFactoryConstructor singleton

        @return: Shared ConfigModelFactoryConstructor instance
        @rtype: ConfigModelFactoryConstructor
        """
        if ConfigModelFactoryConstructor.__instance == None:
            ConfigModelFactoryConstructor.__instance = ConfigModelFactoryConstructor()
        
        return ConfigModelFactoryConstructor.__instance
    
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

        self.__class_definitions = {
            ConfigModelFactory.DEFAULT_PARENT_CLASS_DESCRIPTOR : 
            ConfigModelFactory.DEFAULT_PARENT_CLASS
        }
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
    
    def get_property_class(self, class_name):
        """
        Get the class corresponding to the provided class name for a property

        @param class_name: The name of the class to look up as defined in configuration
        @type class_name: String
        @return: Property corresponding to the provided name
        @rtype: Class
        """
        return self.__property_definitions[class_name].get_property()
    
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