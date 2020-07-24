from numpy import Inf

def findPoint(data_matrix, coordinates):

    point = None
    for i in range(data_matrix.shape[0]):
        for j in range(data_matrix.shape[1]):
            if coordinates[0] == i and coordinates[1] == j:
                point = data_matrix[i][j][:]
    return point



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


