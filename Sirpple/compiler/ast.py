"""
Set of classes to build an Abstract Syntax Tree for the game compiler 
"""
from serialization import model_graph
from serialization import backends

class Node(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

# Singleton might make sense here since graph is actually a bit intensive to load
class NodeFactory:
    """ Factory to build the nodes of the AST """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this NodeFactory singleton

        @return: Shared NodeFactory instance
        @rtype: NodeFactory
        """
        if NodeFactory.__instance == None:
            NodeFactory.__instance = ConfigModelFactory()
        
        return NodeFactory.__instance
    
    def __init__(self):

        self.__graph = model_graph.ModelGraph.get_current_graph()

        db_manager = backends.DatabaseManager.get_instance()
        self.__collection_types = db_manager.get_collection_property_names()
    
    def get_collection_name(self, name):
        name = ''.join([c if c.islower() else '_'+c.lower() for c in name])
        return name.lstrip('_')+'s'
    
    # TODO: Remove this if no longer necessary
    def create_class_tree(self, target_model):
        """
        Create a new AST containing class information from the given class

        @param target_model_class: The model class at the root of the tree
        @type target_model: Any model class object
        @return: Root of AST that corresponds to the given target_model
        @rtype: Node
        """
        raise NotImplementedError("Stub for future functionality")
    
    def create_tree(self, target_model):
        """
        Create a new AST rooted at the specified model instance

        @param target_model: The instance to build the AST form
        @type target_model: Any model instance
        @return: Root of AST that corresponds to the given target_model
        @rtype: Node
        """

        # Get class definition
        class_name = target_model.__class__.__name__
        class_definition = self.__graph.get_class_definition(class_name)

        node_fields = {}

        for field_defn in class_definition.get_fields().vals():
            node_fields[field_defn.get_name()] = self.__create_tree_representation(target_model, field_defn)
    
    def __create_tree_representation(self, target_model, field_definition):
        """
        Determines the appropriate representation for the given field

        @param target_model: The model from which the target field came
        @type target_model: Any model instance
        @param field_definition: The definition of the field to create a 
                                 representation for in the target tree
        @type field_definition: FieldDefinition
        @return: The appropriate representation and data for given model instance
        @rtype: Node, Collection, or primitive
        """

        field_type = field_defn.get_field_type()

        # Make node for pointer or collection
        if field_type.is_reference():

            field_name = field_defn.get_name()

            # Check to see if it should become a collection
            if field_name in self.__collection_types:
                collection = []
                for child_model in graph.get_children(target_model):
                    collection.append(self.create_node(child_model))
                return collection
            
            # Otherwise save as pointer
            else:
                return self.create_tree(getattr(target_model, field_name))
        
        # Get value for primitive
        else:   
            return getattr(target_model, field_name)
