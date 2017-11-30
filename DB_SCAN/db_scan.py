import numpy as np
import math

NOISE = -1
UNCLASSIFIED = 0
CLASSIFIED = 1

class DataPoint:
    def __init__(self, data, index, type = UNCLASSIFIED, cluster_index = -1):
        self.data = data
        self.index = index
        self.type = UNCLASSIFIED
        self.cluster_index = cluster_index
        
def normalize_data(data):
    attribute_count = data.shape[1] - 1
    mean = np.mean(data[ : , :-1], axis = 0)
    standard_deviation = np.std(data[ : , :-1], axis = 0)
    for j in range(attribute_count):
        data[ : j] = ( (data[ : j] - mean[j]) / standard_deviation[j])

    return data

def load_data():
    file_pointer = open('iris.data.txt','r')
    class_dictionary = {'Iris-versicolor' : 0, 'Iris-setosa' : 1, 'Iris-virginica' : 2}
    dataset = []
    for s in file_pointer.readlines():
        s_list = s.split(',')[0:len(s)]
        #print(len(s_list))
        tmp = list(map(float, s_list[ : len(s_list) - 1]))
        str = s_list[ len(s_list) - 1 ].strip()
        #print(str)
        tmp.append(int(class_dictionary[str]))
        dataset.append(tmp)

    return np.array(dataset, float)

def euclidean_distance(data_point1, data_point2):
    return math.sqrt(np.sum((data_point1 - data_point2)**2))

def get_neighbours(index, data_points, epsilon):
    neighbours = []
    core = data_points[index]
    for i in range(data_points.shape[0]):
        if( i == index or data_points[i].type == CLASSIFIED ):
            continue
        else:
            distance = euclidean_distance(core.data[ : -1], data_points[i].data[: -1])
            if(distance <= epsilon):
                neighbours.append(data_points[i])

    
    return neighbours

def db_scan(data, minimum_points, epsilon):
    current_cluster_number = 1
    data_points = []
    row_count = data.shape[0]

    for i in range (0, row_count):
        data_points.append(DataPoint(data[i], i))

    data_points = np.array(data_points)

    for i in range(0, row_count):
        if(data_points[i].type != UNCLASSIFIED):
            continue

        seeds = get_neighbours(i, data_points, epsilon)

        if( (len(seeds) + 1) < minimum_points):
            data_points[i].type = NOISE
            continue

        checked_points_set = {i}
        
        for seed in seeds:
            checked_points_set.add(seed)

        core_point = data_points[i]
        core_point.type = CLASSIFIED
        core_point.cluster_index = current_cluster_number

        j = 0

        while( j < len(seeds)):
            if(seeds[j].type in [UNCLASSIFIED, NOISE]):

                seeds[j].type = CLASSIFIED
                seeds[j].cluster_index = current_cluster_number
                
                seed_neighbours = get_neighbours(seeds[j].index, data_points, epsilon)

                if( (len(seed_neighbours) + 1 ) <= minimum_points):
                    
                    for new_seed_neighbour in seed_neighbours:

                        if(checked_points_set.__contains__(new_seed_neighbour.index)):
                            seeds.append(new_seed_neighbour)
                            checked_points_set.add(new_seed_neighbour.index)
                    
            j = j + 1

        current_cluster_number = current_cluster_number + 1
            
    clusters = [0 for j in range(0,current_cluster_number)]
    noise_count = 0

    for point in data_points:
        if(point.type != NOISE):
            clusters[point.cluster_index] = clusters[point.cluster_index] + 1
        else:
            noise_count = noise_count + 1
            

    for i in range(1, len(clusters)):
        print('Cluster : ', i, '-->', clusters[i])

    print('Noise', noise_count)

    
if(__name__ == '__main__'):
    data = normalize_data(load_data())
    np.random.shuffle(data)
    clusters = db_scan(data, 10, 0.5)
