from .Parser import parse_scene

# these need to be imported to register their class dispatchers to the parser
from .Scene import Scene
from .Group import Group
from .MicropolygonMesh import MicropolygonMesh
