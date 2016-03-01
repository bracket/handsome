from .Parser import register_class

@register_class
class Scene(object):
    def __init__(self, data):
        self.data = data
    
    @classmethod
    def convert_to_object(cls, data):
        return Scene(data)

    def convert_to_dict(self):
        out = {
            '__class__' : 'Scene',
            'canvas'    : self.data['canvas'],
            'top'       : self.data['top'].convert_to_dict(),
        }

        return out
