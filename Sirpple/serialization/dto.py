""" Mechanisms for supporting data transfer objects """

import logging
import type_converters
import model_graph

class DTOBuilder:
    """ Builder that produces and reads data transfer objects """

    CLASS_IDENTIFIER = "__class__"
    CHILDREN_PREFIX = "children_"

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this DTOFactory singleton

        @return: Shared DTOFactory instance
        @rtype: DTOFactory
        """
        if DTOFactory.__instance == None:
            DTOFactory.__instance = DTOFactory()
        
        return DTOFactory.__instance
    
    def create_dto(self, target):
        """
        Creates a new data transfer object (dict) from the given target

        @param target: Instance of class loaded from configuration files
        @type target: Python native instance
        @return: Organized contents of target including ids of children
        @rtype: Dictionary
        """
        converter = type_converters.TypeConverter.get_instance()

        graph = model_graph.ModelGraph.get_current_graph()

        class_name = target.__class__.__name__
        class_definition =  graph.get_class_definition(class_name)

        ret_dict = {}

        # Include class name
        ret_dict[DTOBuilder.CLASS_IDENTIFIER] = class_name

        # Handle basic attributes
        for field in filter(lambda x: x.is_exposed(), class_definition.get_fields()):
            field_name = field.get_name()
            ret_dict[field_name] = getattr(target, field_name)
        
        # Handle children
        children = graph.get_children(target)
        
        # Fill in the children instances
        for defn, instance in children.items():
            pointers = map(lambda x: converter.convert_for_dto(x.__class__.__name__, x))
            ret_dict[DTOBuilder.CHILDREN_PREFIX + defn.get_name().lower()] = pointers
        
        return ret_dict
    
    def read_dto(self, source, class_definition, target=None):
        """
        Reads out from a DTO to generate a fully instantiated instance

        @param source: The dictionary to parse out
        @type source: Dictionary
        @param class_definition: The definition of the class to read from
        @type class_definition: ClassDefinition
        @keyword target: The instance to read into (update). If None, will
                         create a new instance. Defaults to None.
        @type target: Boolean
        @return: Fully instantiated (but not saved)
        @rtype: Instance of the class class_defn represents or None on fail
        """

        # TODO: Might the method of using a dict for attributes cause
        # issues for other backends?

        # Get actual class
        target_class = class_defn.get_class()

        # Get field definitions from class defintion
        field_definitions = class_definition.get_fields()

        # Create structue to hold cleaned fields
        cleaned_foreign_entries = {}

        # If we are writing into a new instance, create temp dict
        if target == None:
            target_dict = {}

        # Clean and check for editing non-exposed fields
        for foreign_field, foreign_value in source:

            # Check that the field is available
            if not foriegn_field in field_definitions:
                logging.error("Invalid field " + foreign_field + " passed to " + target_class.get_name())
                return None
            
            # Check that the field is exposed
            field_defintion = field_defintions[foreign_field]
            if not field_definition.is_exposed():
                logging.error("Attempted to write non-exposed field " + field_defintion.get_name() + " for " + target_class.get_name() + " through REST API")
            
            # Convert and clean
            type_name = field_definition.get_field_type_name()
            new_value = converter.convert_from_dto(type_name, source)
        
            # If we are writing into an existing instance
            if target:
                setattr(target, field_definition.get_name(), new_value)
            
            # Put it in in the dict for real initalization later
            else:
                target_dict[field_definition.get_name()] = new_value
        
        # Create instance if necessary
        if target == None:
            return target_class(target_dict) # TODO: Non-GAE / Django backends?
        else:
            return target
