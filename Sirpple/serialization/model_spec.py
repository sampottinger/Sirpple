"""
Classes containing structural information about models loaded from configuration files
"""

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
        return factory.get_property_instance(self.__field_type)
    
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
        self.__class = None
    
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

        if self.__class == None:

            python_fields = {}

            for field_name in self.__fields:
                python_fields[field_name] = self.__fields[field_name].get_field()
            
            class_factory = config_model.ConfigModelFactory.get_instance()

            parent_class = class_factory.get_class(self.__parent_class_name).get_class()

            self.__class = type(self.__name, (parent_class,), python_fields)
        
        return self.__class

class WrappedClassDefinition(ClassDefinition):
    """
    Definition that wraps an already existing class
    """

    def __init__(self, inner_class, functions):
        """
        Create a new wrapper around the given class

        @param inner_class: The actual Python class to wrap
        @type inner_class: Python Class object
        @param functions: List of function definitions to report
        @type functions: List to FunctionDefintions
        """
        self.__class = inner_class
        self.__fields = functions
    
    def get_name(self):
        """
        Determine which class this definition goes with

        @return: The name of the class corresponding to this definition
        @rtype: String
        """
        return self.__class.__name__
    
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
        return self.__class

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