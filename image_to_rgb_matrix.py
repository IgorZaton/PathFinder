from PIL import Image
from numpy import asarray, delete


def image_to_rgb_matrix(image_name, delete_a_in_rgba=False):
    img = Image.open(image_name)
    matrix = asarray(img)
    if matrix.shape[2] == 4 and delete_a_in_rgba:
        rgb_matrix = delete(matrix, 3, 2)
        return rgb_matrix
    else:
        return matrix
