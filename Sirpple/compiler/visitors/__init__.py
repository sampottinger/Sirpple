#!/usr/bin/env python

class Visitor(object):
    visit_method_prefix = 'visit_'
    def __init__(self):
        self.__method_table = {}
        
        for attr in dir(self):
            if attr.startswith(Visitor.visit_method_prefix):
                target_type = attr.partition(Visitor.visit_method_prefix)[-1]
                self.__method_table[target_type] = getattr(self,attr)
    
    def visit(self,target):
        target_type = target.get_type()
        
        if target_type in self.__method_table:
            return self.__method_table[target_type](target)
        else:
            return self.default_visit(target)
    
    def default_visit(self, target):
        raise NotImplementedError("Need to use subclass of this abstract superclass")
