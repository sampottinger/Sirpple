"""
Classes containing structural information about models loaded from configuration files
"""

from backends import platform_manager
import config_model

class FieldDefinition:
    """
    Definition of a field as part of a database model
    
    @note: For the types in use in fields, see properties 
    """

    def __init__(self, name, field_type, exposed):
        """
        Constructor for a Field

        @param name: The name of this field
        @type name: String
        @param field_type: Description of this field's type as indicated in the configuration file
        @type field_type: String
        @param exposed: Specifies if this field is available through the REST API
        @type exposed: Boolean
        """
        if name.find(".") != -1:
            raise ValueError("Invalid name of property " + config_name)

        self.__name = name
        self.__field_type = field_type
        self.__exposed = exposed
    
    def get_name(self):
        """
        Get the database-recognized name of this field

        @return: String name of this field
        @rtype: String
        """
        return self.__name
    
    def get_field_type_name(self):
        """
        Get the name of the type associated with this field

        @return: Name of this field's type as indicated in the config file
        @rtype: String
        """
        return self.__field_type
    
    def get_field_type(self):
        """
        Get the definition of this field's type

        @return: Description of this field's type
        @rtype: PropertyDefinition
        """
        factory = config_model.ConfigModelFactory.get_instance()
        return factory.get_property_definition(self.__field_type)
    
    def get_field(self):
        """
        Generates a Python native field for this field definition

        @return: Python native field to use
        @rtype: Python native field
        """
        factory = config_model.ConfigModelFactory.get_instance()
        field = factory.get_property_instance(self.__field_type, self.__name)
        return field
    
    def is_exposed(self):
        """
        Determine if this field is exposed through the REST API

        @return: True if this field is exposed through REST and False otherwise
        @rtype: Boolean
        """
        return self.__exposed
    
    def is_built_in(self):
        """
        Determine if this field is one provided by the framework

        @return: True if this is built in or False otherwise
        @rtype: Boolean
        """
        platform = platform_manager.PlatformManager.get_instance()
        return self.get_name() in platform.get_built_in_field_names()

class ClassDefinition:
    """ Definition of a model loaded through a configuration secification """

    DEFAULT_PARENT_FIELD = "parent" # This is db independent

    def __init__(self, name, fields, parent_class, parent_field):
        """
        Constructor for ClassDefintion

        @param name: The name of this class
        @type name: String
        @param fields: Dictionary of fields from field names to actual fields
        @type fields: Dictionary from String to FieldDefinition
        @param parent_class: The name of the class to use as this class' parent
        @type parent_class: String
        @param parent_field: The definition of the field that contains parent information
        @type pareent_field: FieldDefinition
        """
        self.__fields = fields
        self.__name = name
        self.__parent_class_name = parent_class
        self.__class = None
        self.__parent_field = parent_field
    
    def get_name(self):
        """
        Determine which class this definition goes with

        @return: The name of the class corresponding to this definition
        @rtype: String
        """
        return self.__name

    def get_fields(self, include_built_in=False):
        """
        Returns all of the fields / properties this class definition currently has

        @keyword include_built_in: If true, include built in properties. Defaults to False.
        @type include_built_in: Boolean
        @return: Dicationary of fields
        @rtype: Dictionary from String to FieldDefition
        """
        if include_built_in:
            return self.__fields
        else:
            def builtin_filter(item):
                return not item[1].is_built_in()
            
            fields = filter(builtin_filter, self.__fields.items())
            return dict(fields)
    
    def get_class(self):
        """
        Gets the Python version of this class

        @return: The Python native copy of this loaded class
        @rtype: Class which is a child of PARENT_CLASS
        """

        if self.__class == None:

            python_fields = {}

            #for field_name in self.get_fields():
            #    python_fields[field_name] = self.__fields[field_name].get_field()
            
            class_factory = config_model.ConfigModelFactory.get_instance()

            parent_class = class_factory.get_model(self.__parent_class_name)

            self.__class = type(self.__name, (parent_class,), python_fields)
        
        return self.__class
    
    def get_parent_field(self):
        """
        Gets the name of the field that contains a reference to this instance's parent

        @return: The definition of the property of this model that contains
                 a reference property / foreign key to its parent
        @rtype: FieldDefinition
        """
        return self.__parent_field

class WrappedClassDefinition(ClassDefinition):
    """
    Definition that wraps an already existing class
    """

    def __init__(self, inner_class, functions, parent_field):
        """
        Create a new wrapper around the given class

        @param inner_class: The actual Python class to wrap
        @type inner_class: Python Class object
        @param functions: List of function definitions to report
        @type functions: List to FunctionDefintions
        @param parent_field: The definition of the field that contains parent information
        @type pareent_field: FieldDefinition
        """
        self.__class = inner_class
        self.__fields = functions
        self.__parent_field = parent_field
    
    def get_name(self):
        return self.__class.__name__
    
    def get_fields(self):
        return self.__fields
    
    def get_class(self):
        return self.__class
    
    def get_parent_field(self):
        return self.__parent_field

class PropertyDefinition:
    """ 
    Definition of a property *type* as part of a database model 

    @note: Abstract class, must use implementor
    @note: For actual instance variables on a model, see fields
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
    
    def is_reference(self):
        """
        Determines if this property is a primitive or not

        @return: True if a reference property (non-primitive) and False otherwise
        @rtype: Boolean
        """
        return False
    
    def get_property(self, field_name):
        """
        Gets the db class this property defintion encloses

        @param field_name: What this property will be called on the final model
        @type field_name: String
        @return: Instance of the property this definition encloses
        @rtype: Python instance or None if a built-in
        """
        raise NotImplementedError("Must use implementor of PropertyDefinition")
