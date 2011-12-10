"""
Module with facades that abstract away the backend database / framework
"""

from uac import uac_checker
from serialization import adapted_models

try:
    from google.appengine.ext import db
except ImportError:
    db = None # dont fail for on-the-ground testing

# TODO: This is probably going to need to get pushed into another module

# TODO: Push this out to a config file, scoping is important
BACKEND = "GAE"

class PlatformManager:
    """
    Database manager that resolves names of property classes to actual property classes
    """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this PlatformManager singleton

        @return: Shared PlatformManager instance
        @rtype: PlatformManager
        """
        if PlatformManager.__instance == None:
            PlatformManager.__instance = PlatformManager()
        
        return PlatformManager.__instance

    def __init__(self):
        pass

    def get_property_definition_factory(self):
        """
        Gets the database specific property definition factory

        @return: PropertyDefinitionFactory implementor
        @rtype: Subclass of PropertyDefinitionFactory
        """
        # TODO: This is messy
        import property_definitions

        # TODO: Switch on this, scoping is important
        return property_definitions.GAEPropertyDefinitionFactory.get_instance()

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
        Gets the field that require collections in parsing (changes between db)

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
    
    def get_parent_field_name(self):
        """
        Gets the db-specific field name containing information about the parent of an instance

        @return: The name of the field that contains parent information in this
                 database's models
        @rtype: String
        """
        # TODO: Switch on backend
        return "parent"
    
    def get_built_in_field_names(self):
        """
        Determines all of the fields that are provided by the specific backend in use

        @return: List of names of fields that are provided by the current framework
        @rtype: List of Strings
        """
        # TODO: Switch on backend
        return ["parent"]
