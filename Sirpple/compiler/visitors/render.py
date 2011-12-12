#!/usr/bin/env python

from . import Visitor
from ..ast import Node

import pyyaml

from google.appengine.ext.webapp import template

def indent(string):
    return string.replace('\n','\n    ')

class RenderVisitor(Visitor):
    
    def visit_Project(self, project):
        worlds = ''
        for world in project.worlds:
            worlds += self.visit(world)
        
        game_objs=''
        for game_obj in project.game_objects:
            game_objs += self.visit(game_obj)
        
        project_context = {}
        project_context['worlds'] = worlds
        project_context['game_objects'] = game_objs
        project_context['starting_world'] = project.starting_world.name
        project_js = template.render('compiler/runtime/project.js', project_context)
        
        return project_js
    
    def visit_World(self, world):
        body = ''
        for method in world.world_methods:
            method.is_constructor = method == obj.constructor
            
            method_txt = self.visit(method)
            if method.is_constructor:
                constructor_context={}
                constructor_context['method'] = method_txt
                constructor_context['child'] = world.name
                constructor_context['parent'] = 'lime.Scene'
                
                body += template.render('compiler/runtime/constructor.js', constructor_context)
            else:
                body += world.name +'.'+method_txt
        return body
    
    def visit_WorldMethod(self, method):
        return self.visit_Method(method)
    
    def visit_Method(self, method):
        
        signature_dict = pyyaml.load(method.signature)
        args = ', '.join(map(str, signature_dict.keys()))
        
        method_context = {}
        method_context['name'] = method.name
        method_context['args'] = args
        
        if method.body_type == 'raw':
            body = method.body.strip()
            if method.is_constructor:
                body = 'goog.base(this)\n' + body
            method_context['body'] = indent(body)
        
        return template.render('compiler/runtime/method.js', method_context)
    
    def default_visit(self, target):
        print 'default visit', target
        
