#!/usr/bin/env python

import sys

from serialization.config_model import ConfigModelFactory
from serialization import model_graph
from google.appengine.ext.db import Query
#from compiler import astbuilder

import yamlmodels

globals().update(yamlmodels.load())

def populate_db():
    proj = Project()
    proj.name = 'Test Project'
    proj.put()
    
    world = World(parent=proj)
    world.name = 'World 1'
    world.put()
    
    proj.starting_world = world
    proj.put()
    
    cons = WorldMethod(parent=world)
    cons.name = 'World 1 constructor'
    cons.signature = '{}'
    cons.body_type = 'raw'
    cons.body = 'document.write("hello Sirpple")'
    cons.put()
    
    world.constructor = cons
    world.put()

def setup_db():
    factory = ConfigModelFactory.get_instance()
    project_model = factory.get_model('Project')
    
    projects = project_model.all()
    if not projects.get():
        populate_db()

def children():

    setup_db()

    factory = ConfigModelFactory.get_instance()
    project_model = factory.get_model('Project')
    
    projects = project_model.all()
    project = projects.get()
    
    children = model_graph.ModelGraph.get_current_graph().get_children(project)
    print 'Children test passed'

