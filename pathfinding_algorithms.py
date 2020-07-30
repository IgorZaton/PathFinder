import math
from PIL import Image
from numpy import asarray, delete, zeros, full, array
import sys
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


def find_neighbour_nodes(data_matrix, coordinates, diagonal_nodes=False):
    neighbour_nodes = []
    y = int(coordinates[1])
    x = int(coordinates[0])

    #print(data_matrix[x][y-1].y)

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
    '''
    return 0.1 + (float(img[neighbour_coord][0]) - float(img[node_coord][0])) ** 2 + (float(img[neighbour_coord][1]) - float(img[node_coord][1])) ** 2 + (
                float(img[neighbour_coord][2]) - float(img[node_coord][2])) ** 2
    '''
    wall = array([255, 255, 255])
    if diagonal_move:
        if ((node_coord[0] == neighbour_coord[0] + 1 and node_coord[1] == neighbour_coord[1] + 1) or (node_coord[0] == neighbour_coord[0] - 1 and node_coord[1] == neighbour_coord[1] - 1) or (
                node_coord[0] == neighbour_coord[0] - 1 and node_coord[1] == neighbour_coord[1] + 1) or (node_coord[0] == neighbour_coord[0] + 1 and node_coord[1] == neighbour_coord[1] - 1)) and (
                img[neighbour_coord].all() != wall.all()):
            return 1.41
    if (int(node_coord[0]) == int(neighbour_coord[0]) + 1 or int(node_coord[0]) == int(neighbour_coord[0]) - 1 or int(node_coord[1]) == int(neighbour_coord[1]) + 1 or int(node_coord[1]) == int(neighbour_coord[1]) - 1) and (img[int(neighbour_coord[0]), int(neighbour_coord[1])].all() != wall.all()):
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

class AstarNode():
    def __init__(self, coord, end, parent_node):     #coord = (y, x)     #end = (y, x)
        self.x = int(coord[1])
        self.y = int(coord[0])
        self.current_cost = None
        self.h = self.heuristic_cost(end)
        self.g = 0
        self.f = self.h + self.g
        self.processed = False
        #parent info
        self.parent_node = parent_node

    def set_parent_info(self, node):
        self.parent_node = node

    def set_current_cost(self, cc):
        self.current_cost = cc

    def set_g(self, g):
        self.g = g

    def get_f(self):
        return self.f

    def get_g(self):
        return self.g

    def get_h(self):
        return self.h

    def get_coord(self):
        return (int(self.x), int(self.y))

    def get_parent_coord(self):
        return (int(self.parent_x), int(self.parent_y))

    def heuristic_cost(self, end):  #end = (y, x)
        cost_x = abs(self.x - end[1])
        cost_y = abs(self.y - end[0])
        return math.sqrt(cost_x ** 2 + cost_y ** 2)


def get_distance_to_start(data_matrix, start, node, diagonal_move):

    dist = 0
    curr_node = copy.deepcopy(node)
    while curr_node.get_coord() != start:
        dist += get_neighbour_distance(data_matrix, (curr_node.y, curr_node.x), (curr_node.parent_node.y, curr_node.parent_node.x), diagonal_move=diagonal_move)
        curr_node = curr_node.parent_node
    return dist


def astar(data_matrix, start, end, diagonal_move=False):

    opens = []  # visited but not processed
    close = []  # visited and processed

    rows, cols = data_matrix.shape[0], data_matrix.shape[1] #rows = y, cols = x
    matrix = full((rows, cols), None)  # access by matrix[row][col]

    start_x = start[0]
    start_y = start[1]
    end_x = end[0]
    end_y = end[1]

    for y in range(rows):
        for x in range(cols):
            matrix[y][x] = AstarNode((y, x), (end_y, end_x), None)


    node_start = AstarNode(coord=(start_y, start_x), end=(end_y, end_x), parent_node=None)
    node_start.set_parent_info(node_start)
    opens.append(node_start)

    while len(opens) > 0:
        opens.sort(key=AstarNode.get_f)
        node_current = opens.pop()

        if node_current.get_coord() == end:
            break

        neighbours = find_neighbour_nodes(matrix, (node_current.y, node_current.x), diagonal_move)
        for n in range(len(neighbours)):
            neighbours[n].set_parent_info(node_current)
            neighbours[n].set_g(get_distance_to_start(data_matrix, start, neighbours[n], diagonal_move))
            neighbours[n].set_current_cost(node_current.get_g()
                                           + get_neighbour_distance(data_matrix, (neighbours[n].parent_node.y, neighbours[n].parent_node.x), (neighbours[n].y, neighbours[n].x),
                                                                    diagonal_move))
            if neighbours[n] in opens:
                if neighbours[n].get_g() <= neighbours[n].__getattribute__('current_cost'):
                    continue
            elif neighbours[n] in close:
                if neighbours[n].get_g() <= neighbours[n].__getattribute__('current_cost'):
                    continue
                else:
                    close.remove(neighbours[n])
                    opens.append(neighbours[n])
                    neighbours[n].processed = True
            else:
                opens.append(neighbours[n])
            neighbours[n].g = neighbours[n].current_cost

        node_current.processed = True
        close.append(node_current)

    #if node_current.get_coord() != end:
    #    sys.exit("No path found")

    path = []
    while (node_current.x, node_current.y) != (start[0], start[1]):
        path.append((node_current.x, node_current.y))
        node_current = node_current.parent_node

    return path