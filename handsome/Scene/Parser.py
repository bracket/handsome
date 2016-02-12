import yaml

__all__ = [
    'parse_scene',
    'register_class',
]


def parse_scene(file_or_path):
    yl = parse_scene_yaml(file_or_path)
    return convert_to_object(yl)


def convert_to_object(parsed):
    if isinstance(parsed, dict):
        parsed = { key : convert_to_object(value) for key, value in parsed.items() }

        cls = parser_classes.get(parsed.get('__class__', None), None)

        if cls is None:
            return parsed
        else:
            return cls.convert_to_object(parsed)
    elif isinstance(parsed, (tuple, list)):
        return (type(parsed))(convert_to_object(p) for p in parsed)
    else:
        return parsed


def parse_scene_yaml(file_or_path):
    if isinstance(file_or_path, str):
        with open(file_or_path) as fd:
            return yaml.load(fd)
    else:
        return yaml.load(file_or_path)


def register_class(cls):
    parser_classes[cls.__name__] = cls
    return cls


parser_classes = { }
