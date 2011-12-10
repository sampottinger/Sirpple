""" Tests to check loaded class definitions """

from serialization import model_graph

def check_inheritance():

	graph = model_graph.ModelGraph.get_current_graph()

	world_subscription_defn = graph.get_class_definition("WorldSubscription")

	fields = world_subscription_defn.get_fields(include_built_in = True, include_inherited=True)

	print fields

	assert "parent" in fields, "parent field added by subclass" 
	assert "event" in fields, "event field added by superclass"