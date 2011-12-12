#!/usr/bin/env python

import sys

from serialization.config_model import ConfigModelFactory
from serialization import model_graph
from google.appengine.ext.db import Query
from google.appengine.ext.webapp import template
from compiler import ast
from compiler import Compiler

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
    cons.body = """
        this.setPosition(512,384);
        var obj = new Game_object_1();
        this.appendChild(obj);
        """
    cons.put()
    
    world.constructor = cons
    world.put()
    
    game_obj = GameObject(parent=proj)
    game_obj.name='Game object 1'
    game_obj.type = 0
    game_obj.put()
    
    gcons = GameObjectMethod(parent=game_obj)
    gcons.name = 'Game object 1 method'
    gcons.signature='{}'
    gcons.body_type='raw'
    gcons.body="""
        this.setSize(150,150);
        this.setFill("/static/images/brick.png");
        """
    gcons.put()
    
    game_obj.init = gcons
    game_obj.put()
    
    g_onntsep = GameObjectMethod(parent=game_obj)
    g_onntsep.name = 'Game object 1 onStep'
    g_onntsep.signature='{}'
    g_onntsep.body_type='raw'
    g_onntsep.body="""
        var position = this.getPosition();
        this.setPosition(position.x+1,position.y);
        """
    g_onntsep.put()
    
    onstep_event = Event(parent=proj)
    onstep_event.name = 'onStep'
    onstep_event.put()
    
    g_onntsep_subsc = GameObjectSubscription(parent=g_onntsep)
    g_onntsep_subsc.event = onstep_event
    g_onntsep_subsc.put()
    

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
    
    return model_graph.ModelGraph.get_current_graph().get_children(project)
    #print 'Children test passed'

def tree():
    
    setup_db()
    
    factory = ConfigModelFactory.get_instance()
    project_model = factory.get_model('Project')
    
    projects = project_model.all()
    project = projects.get()
    
    tree = ast.NodeFactory.get_instance().create_tree(project)
    return tree

def compiler(project_id = None):
    
    factory = ConfigModelFactory.get_instance()
    project_model = factory.get_model('Project')
    
    if project_id:
        project = project_model.get_by_id(int(project_id))
    else:
        setup_db()
        projects = project_model.all()
        project = projects.get()
    
    output = Compiler().compile(project)
    print '/*'
    return '*/'+output

def project():
    
    setup_db()

    factory = ConfigModelFactory.get_instance()
    project_model = factory.get_model('Project')
    
    projects = project_model.all()
    project = projects.get()
    
    project_context = {}
    project_context['project_js_url'] = '/test?module=dj&test=compiler&format=text/javascript&project_id='+str(project.key().id())
    
    page = template.render('compiler/runtime/project.html', project_context)
    print '<!--'
    return '-->\n'+page
    
