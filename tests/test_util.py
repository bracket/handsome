from handsome.util import parse_color

def test_parse_color():
    tests = [
        ('#f00',      (255, 0, 0, 255)),
        ('0f0',       (0, 255, 0, 255)),
        ('#00f0',     (0, 0, 255, 0)),
        ('7f00',      (119, 255, 0, 0)),
        ('#ff0000',   (255, 0, 0, 255)),
        ('00f800',    (0, 248, 0, 255)),
        ('#0000acac', (0, 0, 172, 172)),
        ('abcdef12',  (171, 205, 239, 18)),
    ]

    for input, expected in tests:
        assert parse_color(input) == expected
