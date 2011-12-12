""" Tests for the REST API machinery """

# NOTE: This only tests supporting classes and not the REST API itself

import yamlmodels
from serialization import dto
from serialization import model_graph

globals().update(yamlmodels.load())

def dto_tests():

    proj = Project()
    proj.name = 'Test Project'
    proj.put()
    
    world = World(parent=proj)
    world.name = 'World 1'
    world.put()

    cons = WorldMethod(parent=world)
    cons.name = 'World 1 constructor'
    cons.signature = '{}'
    cons.body_type = 'raw'
    cons.body = 'document.write("hello Sirpple")'
    cons.put()

    dto_builder = dto.DTOBuilder.get_instance()

    cons_dto = dto_builder.create_dto(cons)

    assert "parent" in cons_dto, "Ensure parent made it into DTO"
    assert "name" in cons_dto, "Ensure name made it into DTO"
    assert "signature" in cons_dto, "Ensure signature made it into DTO"
    assert "body_type" in cons_dto, "Ensure body_type made it into DTO"
    assert "body" in cons_dto, "Ensure body made it into DTO"

    graph = model_graph.ModelGraph.get_current_graph()
    world_method_definition = graph.get_class_definition("WorldMethod")

    cons_read = dto_builder.read_dto(cons_dto, world_method_definition)

    assert cons_read.name == "World 1 constructor", "Ensure name parsing"
    assert cons_read.signature == "{}", "Ensure signature parsing"
    assert cons_read.body_type == "raw", "Ensure body type parsing"
    assert cons_read.body == "document.write(\"hello Sirpple\")", "Ensure body parsing"

