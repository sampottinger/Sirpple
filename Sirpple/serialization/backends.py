"""
Module that abstracts away the backend database / framework
"""

from uac import uac_checker
import adapted_models
import model_spec

try:
    from google.appengine.ext import db
except ImportError:
    db = None # dont fail for on-the-ground testing

# TODO: This is probably going to need to get pushed into another module

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
    
    def get_collection_field_names(self):
        """
        Gets the field that require collections in parsing

        @return: List of field names that should become collections
        @rtype: Tuple of field names
        """
        return ("parent",)
    
    def get_children_resolver(self):
        """
        Gets the db-specific resolver of children entities

        @return: ChildrenResolver implementor for the current db
        @rtyep: Instance of a subclass of ChildrenResovler
        """
        # TODO: Switch on backend
        return GAEChildrenResolver.get_instance()
    
    def get_uac_checker(self):
        """
        Gets the db-specific construct for checking user access controls

        @return: DB-speific rights management construct
        @rtype: Implementor of UACChecker
        """
        # TODO: Switch on backend
        return uac_checker.GAEUACChecker.get_instance()

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
    
    def is_reference(self):
        return True
    
    def get_definition(self, config_name, db_class_name, parameters):
        if db_class_name == "ReferenceProperty":
            return GAEReferencePropertyDefinition(config_name, db_class_name, parameters)
        else:
            return SimplePropertyDefinition(config_name, db_class_name, parameters)

class SimplePropertyDefinition(model_spec.PropertyDefinition):
    """
    Definition of a property as a database model that does not require any special parameters
    """

    def get_property(self, field_name):
        return DatabaseManager.get_instance().get_property_class(self.db_class_name, self.parameters)

class GAEReferencePropertyDefinition(model_spec.PropertyDefinition):
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

class EmptyReferenePropertyDefinition(model_spec.PropertyDefinition):
    """
    Reference property definitions that should not actually be properties (built-ins)
    """

    def get_property(self, field_name):
        return None
    
    def is_built_in(self, field_name):
        return False