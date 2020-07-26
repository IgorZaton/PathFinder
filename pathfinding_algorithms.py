import math
from PIL import Image
from numpy import asarray, delete, zeros, full

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


def find_point(data_matrix, coordinates):
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
        self.d = math.inf  # current distance from source data_matrix
        self.parent_x = None
        self.parent_y = None
        self.processed = False
        self.index_in_queue = None


def find_neighbour_nodes(data_matrix, coordinates):

    neighbour_nodes = []
    y = coordinates[1]
    x = coordinates[0]

    if y > 0 and not data_matrix[x][y - 1].processed:
        neighbour_nodes.append(data_matrix[x][y - 1])
    if y < data_matrix.shape[1] - 1 and not data_matrix[x][y + 1].processed:
        neighbour_nodes.append(data_matrix[x][y + 1])
    if x > 0 and not data_matrix[x - 1][y].processed:
        neighbour_nodes.append(data_matrix[x - 1][y])
    if x < data_matrix.shape[0] - 1 and not data_matrix[x + 1][y].processed:
        neighbour_nodes.append(data_matrix[x + 1][y])
    if y < data_matrix.shape[1] - 1 and x < data_matrix.shape[0] - 1 and not data_matrix[x + 1][y + 1].processed:
        neighbour_nodes.append(data_matrix[x + 1][y + 1])
    if y > 0 and x < data_matrix.shape[0] - 1 and not data_matrix[x + 1][y - 1].processed:
        neighbour_nodes.append(data_matrix[x + 1][y - 1])
    if y < data_matrix.shape[1] - 1 and x > 0 and not data_matrix[x - 1][y + 1].processed:
        neighbour_nodes.append(data_matrix[x - 1][y + 1])
    if y > 0 and x > 0 and data_matrix[x - 1][y - 1].processed:
        neighbour_nodes.append(data_matrix[x - 1][y - 1])

    return neighbour_nodes


def bubble_up(queue, index):
    if index <= 0:
        return queue
    p_index = (index - 1) // 2
    if queue[index].d < queue[p_index].d:
        queue[index], queue[p_index] = queue[p_index], queue[index]
        queue[index].index_in_queue = index
        queue[p_index].index_in_queue = p_index
        queue = bubble_up(queue, p_index)
    return queue


def bubble_down(queue, index):
    length = len(queue)
    lc_index = 2 * index + 1
    rc_index = lc_index + 1
    if lc_index >= length:
        return queue
    if lc_index < length and rc_index >= length:  # just left child
        if queue[index].d > queue[lc_index].d:
            queue[index], queue[lc_index] = queue[lc_index], queue[index]
            queue[index].index_in_queue = index
            queue[lc_index].index_in_queue = lc_index
            queue = bubble_down(queue, lc_index)
    else:
        small = lc_index
        if queue[lc_index].d > queue[rc_index].d:
            small = rc_index
        if queue[small].d < queue[index].d:
            queue[index], queue[small] = queue[small], queue[index]
            queue[index].index_in_queue = index
            queue[small].index_in_queue = small
            queue = bubble_down(queue, small)
    return queue


def get_distance(img, u, v):
    return 0.1 + (float(img[v][0]) - float(img[u][0])) ** 2 + (float(img[v][1]) - float(img[u][1])) ** 2 + (
                float(img[v][2]) - float(img[u][2])) ** 2


def dijkstra(data_matrix, start, end):

    priority_queue = []
    start_x = int(start[0])
    start_y = int(start[1])

    goal_x = int(end[0])
    goal_y = int(end[1])

    rows, cols = data_matrix.shape[0], data_matrix.shape[1]
    matrix = full((rows, cols), None)  # access by matrix[row][col]

    for x in range(rows):
        for y in range(cols):
            matrix[x][y] = Node(y, x)
            matrix[x][y].index_in_queue = len(priority_queue)
            priority_queue.append(matrix[x][y])

    matrix[start_y][start_x].d = 0
    priority_queue = bubble_up(priority_queue, matrix[start_y][start_x].index_in_queue)

    while len(priority_queue) > 0:
        u = priority_queue[0]
        u.processed = True
        priority_queue[0] = priority_queue[-1]
        priority_queue[0].index_in_queue = 0
        priority_queue.pop()
        priority_queue = bubble_down(priority_queue, 0)
        neighbors = find_neighbour_nodes(matrix, (u.y, u.x))
        for v in neighbors:
            dist = get_distance(data_matrix, (u.y, u.x), (v.y, v.x))
            if u.d + dist < v.d:
                v.d = u.d + dist
                v.parent_x = u.x
                v.parent_y = u.y
                idx = v.index_in_queue
                priority_queue = bubble_down(priority_queue, idx)
                priority_queue = bubble_up(priority_queue, idx)

    path = []
    iter_v = matrix[goal_y][goal_x]
    path.append((goal_x, goal_y))
    while (iter_v.y != start_y or iter_v.x != start_x):
        path.append((iter_v.x, iter_v.y))
        iter_v = matrix[iter_v.parent_y][iter_v.parent_x]

    path.append((start_x, start_y))
    return path

def paint_path(data_matrix, path):

    for i in range(len(path)):
        data_matrix[path[i][1]][path[i][0]] = (0, 0, 255)
    return data_matrix

    