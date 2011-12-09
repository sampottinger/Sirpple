""" Data transfer strctures for serialization """

from serialization import model_graph

class DTOBuilder:
    """ Builder that produces data transfer objects """

    CLASS_IDENTIFIER = "__class__"

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

        graph = model_graph.ModelGraph.get_current_graph()

        class_name = target.__class__.__name__
        class_definition =  graph.get_class_definition(class_name)

        ret_dict = {}

        # Include class name
        ret_dict[DTOBuilder.CLASS_IDENTIFIER] = class_name

        # Handle basic attributes
        for field in class_definition.get_fields():
            field_name = field.get_name()
            ret_dict[field_name] = getattr(target, field_name)
        
        # Handle children
        graph.get_children()
