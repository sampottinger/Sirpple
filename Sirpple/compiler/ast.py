#!/usr/bin/env python

import runtime
sys.path.append('..')
from configparser import get_parser

class Node(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def get_collection_name(class_name):
    name = ''.join([c if c.islower() else '_'+c.lower() for c in s])
    return name.lstrip('_')+'s'

def build(project):
    
    parser = get_parser('yaml')
    app_config = parser.load_file('app_config.yaml')
    classes = parser.load_dir(app_config['classes'])
    
    return build_node(project)

def build_node(model, classes):
    name = model.__class__.__name__
    fields={}
    
    for class_name, class_body in classes.items():
        if class_body['parent'] == name # Can give DJ this 
        
        field = get_collection_name(class_name)
        model_class = globals()[class_name] # Give DJ real class
        
        collection = []
        for child_model in model.get_children(model_class):
            collection.append(build_node(child_model))
        
        fields[field] = collection
    
    # use Sam's stuff for this
    for field, value in model.__dict__.items():
        
        if value is ReferenceProperty:
            fields[field] = build_node(something)
        else:
            fields[field] = value
    # end use Sam's stuff for this
    
    retrun Node(**fields)
