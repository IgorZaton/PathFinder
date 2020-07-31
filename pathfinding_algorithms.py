import math
from PIL import Image
from numpy import asarray, delete, full, array
import copy


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


def heuristic_cost(node, end):
    goal_x = int(end[0])
    goal_y = int(end[1])
    return math.sqrt(abs(node.x - goal_x) ** 2 + abs(node.y - goal_y) ** 2)


def find_neighbour_nodes(data_matrix, coordinates, diagonal_nodes=False):
    neighbour_nodes = []
    y = int(coordinates[1])
    x = int(coordinates[0])

    if y > 0 and not data_matrix[x][y - 1].processed:
        neighbour_nodes.append(data_matrix[x][y - 1])
    if y < data_matrix.shape[1] - 1 and not data_matrix[x][y + 1].processed:
        neighbour_nodes.append(data_matrix[x][y + 1])
    if x > 0 and not data_matrix[x - 1][y].processed:
        neighbour_nodes.append(data_matrix[x - 1][y])
    if x < data_matrix.shape[0] - 1 and not data_matrix[x + 1][y].processed:
        neighbour_nodes.append(data_matrix[x + 1][y])
    if diagonal_nodes:
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


def get_neighbour_distance(img, node_coord, neighbour_coord, diagonal_move=False):

    # distance is 1 up, down, left, right, sqrt(2)~1.41 if diagonal,
    # 0 if the same spot and infinity if next node is a wall
    wall = array([255, 255, 255])
    if diagonal_move:
        if ((node_coord[0] == neighbour_coord[0] + 1 and node_coord[1] == neighbour_coord[1] + 1) or (
                node_coord[0] == neighbour_coord[0] - 1 and node_coord[1] == neighbour_coord[1] - 1) or (
                    node_coord[0] == neighbour_coord[0] - 1 and node_coord[1] == neighbour_coord[1] + 1) or (
                    node_coord[0] == neighbour_coord[0] + 1 and node_coord[1] == neighbour_coord[1] - 1)) and (
                img[neighbour_coord].all() != wall.all()):
            return 1.41
    if (int(node_coord[0]) == int(neighbour_coord[0]) + 1 or int(node_coord[0]) == int(neighbour_coord[0]) - 1 or
        int(node_coord[1]) == int(neighbour_coord[1]) + 1 or int(node_coord[1]) == int(neighbour_coord[1]) - 1) and \
            (img[int(neighbour_coord[0]), int(neighbour_coord[1])].all() != wall.all()):
        return 1
    elif int(node_coord[0]) == int(neighbour_coord[0]) and int(node_coord[1]) == int(neighbour_coord[1]):
        return 0
    elif img[int(neighbour_coord[0]), int(neighbour_coord[1])].all() == wall.all():
        return math.inf


def dijkstra(data_matrix, start, end, diagonal_move=False):
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
        neighbors = find_neighbour_nodes(matrix, (u.y, u.x), diagonal_move)
        for v in neighbors:
            dist = get_neighbour_distance(data_matrix, (u.y, u.x), (v.y, v.x), diagonal_move)
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

# *********ASTAR*********


def paint_astar_path(data_matrix, path):    #path is AstarNode's list
    for i in range(len(path)):
        data_matrix[path[i].y][path[i].x] = (0, 0, 255)
    return data_matrix


class AstarNode():
    def __init__(self, coord, parent_node):  # coord = (y, x)     #end = (y, x)
        self.x = int(coord[1])
        self.y = int(coord[0])
        self.current_cost = None
        self.h = 0
        self.g = 0
        self.processed = False
        # parent info
        self.parent_node = parent_node

    def set_parent_info(self, parent):
        self.parent_node = parent

    def get_f(self):
        return self.f

    def get_coord(self):
        return self.x, self.y

    def set_f(self):
        self.f = self.h + self.g


def get_distance_to_start(data_matrix, start, node, diagonal_move):
    dist = 0
    curr_node = copy.deepcopy(node)
    while curr_node.get_coord() != start:
        dist += get_neighbour_distance(data_matrix, (curr_node.y, curr_node.x),
                                       (curr_node.parent_node.y, curr_node.parent_node.x), diagonal_move=diagonal_move)
        curr_node = copy.deepcopy(curr_node.parent_node)
    return dist


def astar(data_matrix, start, end, diagonal_move=False):

    openset = []  # visited but not processed
    closeset = []  # visited and processed

    rows, cols = data_matrix.shape[0], data_matrix.shape[1]  # rows = y, cols = x
    matrix = full((rows, cols), None)  # access by matrix[row][col]

    start_x = start[0]
    start_y = start[1]

    for y in range(rows):
        for x in range(cols):
            matrix[y][x] = AstarNode((y, x), None)

    node_start = AstarNode(coord=(start_y, start_x), parent_node=None)
    openset.append(node_start)

    while openset:
        node_current = min(openset, key=lambda o: o.g + o.h)

        if (node_current.x, node_current.y) == end:
            path = []
            while node_current.parent_node:
                path.append(node_current)
                node_current = node_current.parent_node
            path.append(node_current)
            return path[::-1]

        openset.remove(node_current)
        closeset.append(node_current)

        neighbours = find_neighbour_nodes(matrix, (node_current.y, node_current.x), diagonal_move)
        for n in neighbours:
            if n in closeset:
                continue
            if n in openset:
                new_g = node_current.g + get_neighbour_distance(data_matrix,
                                            (node_current.y, node_current.x),
                                            (n.y, n.x),
                                            diagonal_move)
                if n.g > new_g:
                    n.g = new_g
                    n.parent_node = node_current
            else:
                    n.g = node_current.g + get_neighbour_distance(data_matrix,
                                            (node_current.y, node_current.x),
                                            (n.y, n.x),
                                            diagonal_move)
                    n.h = heuristic_cost(n, end)
                    n.parent_node = node_current
                    openset.append(n)
    raise ValueError('No Path Found')
