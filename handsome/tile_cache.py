from .Coordinate import Coordinate
from .Pixel import Pixel
from .Tile import Tile

class TileCache:
    def __init__(self, tile_shape, sample_rate=1, dtype=Pixel):
        self.tiles = { }

        self.tile_shape = tile_shape
        self.sample_rate = sample_rate
        self.dtype = dtype


    def tile_origin_for_coordinate(self, coordinate):
        width, height = self.tile_shape

        return (
            int(coordinate[0] // width * width),
            int(coordinate[1] // height * height)
        )


    def get_tile(self, coordinate):
        origin = self.tile_origin_for_coordinate(coordinate)
        tile = self.tiles.get(origin)

        if tile is not None:
            return tile

        tile = Tile(origin, self.tile_shape, self.sample_rate, self.dtype)

        self.tiles[origin] = tile
        return tile


    def get_tiles_for_bounds(self, bounds):
        width, height = self.tile_shape

        left, bottom = self.tile_origin_for_coordinate((bounds.left, bounds.bottom))
        right, top   = self.tile_origin_for_coordinate((bounds.right + width, bounds.top + height))

        for x in range(left, right, width):
            for y in range(bottom, top, height):
                yield self.get_tile((x, y))


    def composite_into(self, target):
        for source in self.tiles.values():
            target.composite_from(source)
