""" Mechanisms to safely read user input / foreign values and produce serializable output values """

import cgi
from serialization import model_graph
from backends import platform_manager

class TypeConverter:
    """ Facade that converts a foreign value for a model field to a cleaned native value """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this TypeConverter singleton

        @return: Shared TypeConverter instance
        @rtype: TypeConverter
        """
        if TypeConverter.__instance == None:
            TypeConverter.__instance = TypeConverter()
        
        return TypeConverter.__instance

    def __init__(self):
        """ Constructor that loads strategies for this TypeConverter """
        self.__conversion_strategies = {"Text": TextConversionStrategy,
                                        "String": StringConversionStrategy,
                                        "Integer": IntegerConversionStrategy,
                                        "GameObject": SimpleReferenceConversionStrategy,
                                        "GameObjectMethod": SimpleReferenceConversionStrategy,
                                        "WorldMethod": SimpleReferenceConversionStrategy,
                                        "Event": SimpleReferenceConversionStrategy,
                                        "Project": SimpleReferenceConversionStrategy,
                                        "World": SimpleReferenceConversionStrategy,
                                        "User": UserReferenceConversionStrategy}
    
    def add_conversion_strategy(self, type_name, strategy):
        """
        Adds a new conversion strategy to this overall converter facade

        @param type_name: The name of the type (from config file not db)
                          that this strategy will convert from and to
        @type type_name: String
        @param strategy: The new strategy to add
        @type strategy: Implementor of TypeConversionStrategy
        """
        self.__conversion_strategies[type_name] = strategy
    
    def convert_from_dto(self, type_name, value):
        """
        Convert a foriegn value to a native Python value appropriate for the given field

        @param type_name: The config file (not db specific) type name for which this 
                          conversion is being performed
        @type type_name: String
        @param value: The foreign "serializable" value
        @type value: String
        @return: The converted native Python value
        @rtype: Object
        """
        strategy = self.__conversion_strategies[type_name].get_instance()
        return strategy.convert_from_dto(value)

    def convert_for_dto(self, type_name, value):
        """
        Convert a Python native value to a value appropriate for a data transfer object

        @param type_name: The config file (not db specific) type name for which this 
                          conversion is being performed
        @type type_name: String
        @param value: The native value
        @type value: Object
        @return: The converted serialization-ready value
        @rtype: Object with serializable type
        """
        strategy = self.__conversion_strategies[type_name].get_instance()
        return strategy.convert_for_dto(value)

class TypeConversionStrategy:
    """ 
    Strategy interface for objects that convert between serializable and native values

    Interface for strategies that can convert between the representations of model field
    values. These should be able to produce serialization ready values and also the 
    "native" representations of the same values, watching to clean appropriately.
    """

    def __init__(self):
        pass
    
    def convert_from_dto(self, value):
        """
        Convert a foriegn value to a native Python value appropriate for the given field

        @param value: The foreign "serializable" value
        @type value: String
        @return: The converted native Python value
        @rtype: Object
        """
        raise NotImplementedError("Must use implementor of this interface")

    def convert_for_dto(self, type_name, value):
        """
        Convert a Python native value to a value appropriate for a data transfer object

        @param value: The native value
        @type value: Object
        @return: The converted serialization-ready value
        @rtype: Object with serializable type
        """
        raise NotImplementedError("Must use implementor of this interface")

class SimpleReferenceConversionStrategy(TypeConversionStrategy):
    """ 
    Strategy for converting simple reference properties

    Strategy that produces and reads from typed serializable pointer like structures
    """

    CLASS_NAME_PARAM = "class_name"
    INSTANCE_ID_PARAM = "id"

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this SimpleReferenceConvserionStrategy singleton

        @return: Shared SimpleReferenceConvserionStrategy instance
        @rtype: SimpleReferenceConvserionStrategy
        """
        if SimpleReferenceConvserionStrategy.__instance == None:
            SimpleReferenceConvserionStrategy.__instance = SimpleReferenceConvserionStrategy()
        
        return SimpleReferenceConvserionStrategy.__instance

    def __init__(self):
        TypeConvserionStrategy.__init__(self)
    
    def convert_from_dto(self, pointer_struct):
        # Get graph of models
        graph = model_graph.ModelGraph.get_current_graph()

        # Read out values necessary to resolve the "pointer"
        class_name = pointer_struct[SimpleReferenceConversionStrategy.CLASS_NAME_PARAM]
        instance_id = int(pointer_struct[SimpleReferenceConversionStrategy.INSTANCE_ID_PARAM])

        # Find class
        target_class = graph.get_class_definition(class_name).get_class()

        # Get the desired instance
        return target_class.get_by_id(instance_id)
    
    def convert_for_dto(self, target):
        pointer_struct = {}
        pointer_struct[SimpleReferenceConversionStrategy.CLASS_NAME_PARAM] = target.__class__.__name__
        pointer_struct[SimpleReferenceConversionStrategy.INSTANCE_ID_PARAM] = target.get_id()

class IntegerConversionStrategy(TypeConversionStrategy):
    """ Strategy that converts integer primitives """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this IntegerConvserionStrategy singleton

        @return: Shared IntegerConvserionStrategy instance
        @rtype: IntegerConvserionStrategy
        """
        if IntegerConvserionStrategy.__instance == None:
            IntegerConvserionStrategy.__instance = IntegerConvserionStrategy()
        
        return IntegerConvserionStrategy.__instance

    def convert_from_dto(self, value):
        return int(value)
    
    def convert_for_dto(self, value):
        return value

class StringConversionStrategy(TypeConversionStrategy):
    """ Strategy for string conversion with cleaning for security """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this StringConversionStrategy singleton

        @return: Shared StringConversionStrategy instance
        @rtype: StringConversionStrategy
        """
        if StringConversionStrategy.__instance == None:
            StringConversionStrategy.__instance = StringConversionStrategy()
        
        return StringConversionStrategy.__instance

    def convert_from_dto(self, value):
        return cgi.escape(value)
    
    def convert_for_dto(self, value):
        return value

class TextConversionStrategy(TypeConversionStrategy):
    """ Strategy for string conversion without cleaning (for code) """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this TextConversionStrategy singleton

        @return: Shared TextConversionStrategy instance
        @rtype: TextConversionStrategy
        """
        if TextConversionStrategy.__instance == None:
            TextConversionStrategy.__instance = TextConversionStrategy()
        
        return TextConversionStrategy.__instance

    def convert_from_dto(self, value):
        return cgi.escape(value, quote=False)
    
    def convert_for_dto(self, value):
        return value

class UserReferenceConversionStrategy(TypeConversionStrategy):
    """ Strategy for converting db-specific user constructs """

    __instance = None

    @classmethod
    def get_instance(self):
        """
        Get a shared instance of this UserReferenceConversionStrategy singleton

        @return: Shared UserReferenceConversionStrategy instance
        @rtype: UserReferenceConversionStrategy
        """
        if UserReferenceConversionStrategy.__instance == None:
            UserReferenceConversionStrategy.__instance = UserReferenceConversionStrategy()
        
        return StringConversionStrategy.__instance

    def convert_from_dto(self, value):
        platform = platform_manager.PlatformManager.get_instance()
        wrapped_user = platform.get_adapted_user(value)
        return wrapped_user.get_username()
    
    def convert_for_dto(self, value):
        platform = platform_manager.PlatformManager.get_instance()
        return platform.get_adapted_user_class().get_by_username(value)
