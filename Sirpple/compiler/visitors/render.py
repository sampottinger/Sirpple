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
        
        events = ''
        setup = ''
        if project.events:
            events = 'var eventManager = new goog.events.EventTarget();\n'
        
        for event in project.events:
            events += 'var %sEvent = "%s";\n'%(event.name,event.name)
            if event.name == 'onStep':
                events += 'var onStep_leftover = 0;\n'
                events += template.render('compiler/runtime/onstep.js', {'target':'eventManager'})
                setup += 'lime.scheduleManager.scheduleWithDelay(onStep,null,30);'
                pass
        
        project_context = {}
        project_context['events'] = events
        project_context['worlds'] = worlds
        project_context['game_objects'] = game_objs
        project_context['starting_world'] = project.starting_world.name
        project_context['setup'] = setup
        project_js = template.render('compiler/runtime/project.js', project_context)
        
        return project_js
    
    def visit_World(self, world):
        world.methods = world.world_methods
            
        return self.render_js_class(world, 'lime.Layer')
    
    def visit_GameObject(self, game_obj):
        
        game_obj.constructor = game_obj.init
        game_obj.methods = game_obj.game_object_methods
        
        parent_class = 'lime.Sprite' # default
        if game_obj.parent_class:
            parent_class = game_obj.parent_class.name
        
        return self.render_js_class(game_obj, parent_class)
    
    def render_js_class(self, obj, parent_class):
        body = ''
        events={}
        for method in obj.methods:
            if not method == obj.constructor:
                method.is_constructor = False
                method_txt,method_events = self.visit(method)
                events[method.name] = method_events
                body += obj.name +'.prototype.'+method_txt
        
        for method,event_list in events.items():
            for event in event_list:
                fields = (event.name,'this.'+method)
                obj.constructor.body += '\ngoog.events.listen(eventManager, %sEvent, %s, false, this);'%fields
        
        obj.constructor.is_constructor = True
        method_txt,_ = self.visit(obj.constructor)
        
        constructor_context={}
        constructor_context['method'] = method_txt
        constructor_context['child'] = obj.name
        constructor_context['parent'] = parent_class
        
        body = template.render('compiler/runtime/constructor.js', constructor_context)+body
            
        return body
    
    def visit_WorldMethod(self, method):
        method.subscriptions = method.world_subscriptions
        return self.visit_Method(method)
    
    def visit_GameObjectMethod(self, method):
        method.subscriptions = method.game_object_subscriptions
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
        
        events = [s.event for s in method.subscriptions]
        return template.render('compiler/runtime/method.js', method_context), events
    
    def default_visit(self, target):
        print 'default visit', target
        
