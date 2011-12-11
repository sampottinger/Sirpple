"""
Set of classes to build an Abstract Syntax Tree for the game compiler 
"""
from serialization import model_graph

class Node(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def __str__(self):
        return repr(vars(self))
    
    def __repr__(self):
        return str(self)
    

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
            NodeFactory.__instance = NodeFactory()
        
        return NodeFactory.__instance
    
    def __init__(self):

        self.__graph = model_graph.ModelGraph.get_current_graph()
        self.__node_cache = {}
    
    def get_collection_name(self, name):
        name = ''.join([c if c.islower() else '_'+c.lower() for c in name])
        return name.lstrip('_')+'s'
    
    def clear_node_cache(self):
        self.__node_cache = {}
    
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

        class_name = target_model.__class__.__name__
        
        cache_id = (class_name,target_model.get_id())
        
        if cache_id in self.__node_cache:
            return self.__node_cache[cache_id]
        
        # Get class definition
        class_definition = self.__graph.get_class_definition(class_name)

        node_fields = {}

        for field_defn in class_definition.get_fields().values():
            node_fields[field_defn.get_name()] = self.__create_tree_representation(target_model, field_defn)
        
        for class_defn,models in self.__graph.get_children(target_model).items():
            
            collection_name = self.get_collection_name(class_defn.get_name())
            
            collection = [self.create_tree(model) for model in models]
            
            node_fields[collection_name] = collection
        
        node = Node(**node_fields)
        self.__node_cache[cache_id] = node
        
        return node
    
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

        field_type = field_definition.get_field_type()

        # Make node for pointer or collection
        if field_type.is_reference():
            
            field_name = field_definition.get_name()
            
            # save as pointer
            return self.create_tree(getattr(target_model, field_name))
        
        # Get value for primitive
        else:   
            return getattr(target_model, field_definition.get_name())
