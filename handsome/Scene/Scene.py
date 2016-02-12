from .Parser import register_class

@register_class
class Scene(object):
    def __init__(self, data):
        self.data = data
    
    @classmethod
    def convert_to_object(cls, data):
        return Scene(data)
