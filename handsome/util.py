import numpy as np

def save_array_as_image(array, path, mode):
    from PIL import Image
    image = Image.frombuffer(mode, array.shape, np.ascontiguousarray(array.T).data, 'raw', mode, 0, 1)
    image.save(path)
