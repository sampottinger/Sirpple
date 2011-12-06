""" Module containing classes related to traversal of the model dependency tree """

import config_model
import backends

class ModelGraph:
	""" 
	Graph of model schema structure as loaded from configuration files

	Lazily loaded graph container that maintains dependencies between model
	 classes and other structural elements of the database / model schema
	"""

	@classmethod
	def get_current_graph(self):
		""" 
		Creates a new ModelGraph out of the current model factory state

		@return: Graph of current state of classes loaded from configuration
		@rtype: ModelGraph
		"""
		return ModelGraph(config_model.ConfigModelFactory.get_instance())

	def __init__(self, factory):
		"""
		Creates a new ModelGraph off of the current state of the given model factory

		@param factory: The factory to generate the graph off of
		@type factory: ConfigModelFactory
		"""
		self.__factory = factory
		self.__field_relationship_cache = {}
	
	def get_class_definition(self, class_name):
		"""
		Gets the definition of a class as loaded from a config file

		@param class_name: The name of the class to look up
		@type class_name: String
		@return: The definition corresponding to the class name specified
		@rtype: ClassDefinition
		"""
		return self.__factory.get_class(class_name)
	
	def get_children_classes(self, field_name, model_class):
		"""
		Determines the "children classes" for the given model class

		Finds all of the children clases for the given model class that establish
		that relationship through the field of the given name

		@param propert_name: The field establishing the parent-child relationship
		@type field_name: String
		@param model_class: The class to find children for
		@type model_class: Any registered (in config file) model class object
		@return: List of parent classes
		@rtype: List of ClassDefinitions
		"""
		model_class_name = model_class.__name__

		# Check cache for existing relationship
		if not field_name in self.__field_relationship_cache:
			self.__load_field_relationships(field_name)
		
		# Get existing relationships
		relationships = self.__field_relationship_cache[field_name]

		# Return children
		if not model_class_name in relationships:
			return []
		else:
			return relationships[model_class_name]
	
	def get_children(self, target_model, field_name):
		"""
		Get all of the immediate children of target_model

		@param target_model: The model instance to get the children for
		@type target_model: Any Model instance
		@param field_name: The name of the field to look for the parent-child 
		                   relationship
		@type field_name: String
		@return: List of immediate children of target_model
		@rtype: List of Model instances
		"""
		resolver = backends.DatabaseManager.get_instance().get_children_resolver()
		
		children = []
		for class_defn in self.get_children_classes(target_model, field_name):
			new_children = list(resolver.get_children(target_model, class_defn))
			children.extend(new_children)

		return children
	
	def __load_field_relationships(self, field_name):
		""" 
		Determine all of the relationships for the field of the given name

		Determine the graph of field to model class relationships for the 
		field of the given name

		@param field_name: The name of the field to load the relationship graph for
		@type field_name: String
		"""
		relationships = {}

		# Go through all of the available classes
		for class_def in self.__factory.get_classes():

			# Get all of the fields for this class
			field_defs = class_def.get_fields()

			# If this field is in this class, add its type to the set
			if field_name in field_defs:

				type_name = field_defs.get_field_type_name()

				# Set up a set in the dictionary if not already there
				if not type_name in relationships:
					relationships[type_name] = set([])
				
				# Add ourselves
				relationships[type_name].add(class_def.get_name())
			
		self.__field_relationship_cache[field_name] = relationships
