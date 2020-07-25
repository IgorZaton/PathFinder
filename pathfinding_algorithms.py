from numpy import Inf
from PIL import Image
from numpy import asarray, delete, zeros

'''
def image_to_matrix(image_name, add_cost_matrix=False, cost_val=255, delete_a_in_rgba=False):
    img = Image.open(image_name)
    data_matrix = asarray(img)
    data_matrix.setflags(write=1)
    if data_matrix.shape[2] == 4 and add_cost_matrix:
        for i in range(data_matrix.shape[0]):
            for j in range(data_matrix.shape[1]):
                data_matrix[i][j][3] = cost_val
    if data_matrix.shape[2] == 4 and delete_a_in_rgba and add_cost_matrix==False:
        data_matrix = delete(data_matrix, 3, 2)
        return data_matrix
    else:
        return data_matrix
'''


def image_to_matrix(image_name, delete_a_in_rgba=False):
    img = Image.open(image_name)
    data_matrix = asarray(img)
    data_matrix.setflags(write=True)
    if data_matrix.shape[2] == 4 and delete_a_in_rgba:
        data_matrix = delete(data_matrix, 3, 2)
        return data_matrix
    else:
        return data_matrix


def findPoint(data_matrix, coordinates):
    point = None
    for i in range(data_matrix.shape[0]):
        for j in range(data_matrix.shape[1]):
            if coordinates[0] == i and coordinates[1] == j:
                point = data_matrix[i][j][:]
    return point


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.d = float('inf')  # current distance from source data_matrix
        self.parent_x = None
        self.parent_y = None
        self.processed = False
        self.index_in_queue = None


def findNeighbourNodes(data_matrix, coordinates):

    neighbour_nodes = []
    x = coordinates[0]
    y = coordinates[1]

    if x > 0 and not data_matrix[x - 1][y].processed:
        neighbour_nodes.append(data_matrix[x - 1][y])
    if x < data_matrix.shape[0] - 1 and not data_matrix[x + 1][y].processed:
        neighbour_nodes.append(data_matrix[x + 1][y])
    if y > 0 and not data_matrix[x][y - 1].processed:
        neighbour_nodes.append(data_matrix[x][y - 1])
    if y < data_matrix.shape[1] - 1 and not data_matrix[x][y + 1].processed:
        neighbour_nodes.append(data_matrix[x][y + 1])
    if x < data_matrix.shape[0] - 1 and y < data_matrix.shape[1] - 1 and not data_matrix[x + 1][y + 1].processed:
        neighbour_nodes.append(data_matrix[x + 1][y + 1])
    if x > 0 and y < data_matrix.shape[1] - 1 and not data_matrix[x][y + 1].processed:
        neighbour_nodes.append(data_matrix[x - 1][y + 1])
    if x < data_matrix.shape[0] - 1 and y > 0 and not data_matrix[x][y + 1].processed:
        neighbour_nodes.append(data_matrix[x + 1][y - 1])
    if x > 0 and y > 0 and data_matrix[x - 1][y - 1].processed:
        neighbour_nodes.append(data_matrix[x - 1][y - 1])

    return neighbour_nodes


def dijkstra(data_matrix, start, end):
    shortest_distance = {}
    track = {}
    unseenNodes = []
    straight_cost = 1
    diagonal_cost = 1.41
    wall = (255, 255, 255)

    startpoint = findPoint(data_matrix, start)
    goal = findPoint(data_matrix, end)

    for k in range(data_matrix.shape[0]):
        for j in range(data_matrix.shape[1]):
            if data_matrix[k][j][:] != startpoint:
                unseenNodes.append(data_matrix[k][j][:])

    for node in unseenNodes:
        shortest_distance[node] = Inf
    shortest_distance[startpoint] = 0
