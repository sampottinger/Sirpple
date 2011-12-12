#!/usr/bin/env python

from ..ast import Node
from . import Visitor

def clean_name(name):
    return name.replace(' ','_')

class RenameVisitor(Visitor):
    
    def visit_Project(self, project):
        for world in project.worlds:
            self.visit(world)
        
        for game_obj in project.game_objects:
            self.visit(game_obj)
        return project
    
    def visit_World(self, world):
        world.name = 'World_'+clean_name(world.name)
        for method in world.world_methods:
            self.visit(method)
        world.constructor.name = world.name
        return world
    
    def visit_GameObject(self, game_obj):
        game_obj.name = 'GameObject_'+clean_name(world.name)
        for method in game_obj.game_object_methods:
            self.visit(method)
        game_obj.init.name = game_obj.name
        return game_obj
    
    def visit_WorldMethod(self, method):
        return self.visit_Method(method)
        
    def visit_GameObjectMethod(self, method):
        return self.visit_Method(method)
    
    def visit_Method(self, method):
        method.name = 'method_'+clean_name(method.name)
        return method
    
    def default_visit(self, target):
        print 'default visit', target
