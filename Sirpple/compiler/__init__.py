#!/usr/bin/env python

from ast import NodeFactory
from visitors.rename import RenameVisitor
from visitors.render import RenderVisitor

class Compiler(object):
    
    def compile(self, project):
        
        node_factory = NodeFactory.get_instance()
        
        project = node_factory.create_tree(project)
        
        project = RenameVisitor().visit(project)
        
        project_txt = RenderVisitor().visit(project)
        node_factory.clear_node_cache()
        return project_txt
        
