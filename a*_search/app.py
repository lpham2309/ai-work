from heapq import heappush, heappop
from collections import defaultdict
from haversine import haversine, Unit

import sys
import re

class TreeNode():
    def __init__(self, city, long=None, lat=None, state=None, cost=0.0, parent=None):
        self.cost = cost
        self.state = state
        self.city = city
        self.parent = parent
        self.long = long
        self.lat = lat

    def __lt__(self, next_node):
        return self.cost < next_node.cost
    
    def isGoal(self, goal_city):
        return str(self.city) == goal_city
class PriorityQueue:
    
    def __init__(self, iterable=None):
        iterable = [] if iterable is None else iterable
        self.heap = []
        for value in iterable:
            heappush(self.heap, (0, value))
    
    def add(self, value, priority=0):
        heappush(self.heap, (priority, value))
    
    def pop(self):
        priority, value = heappop(self.heap)
        return value
    
    def __len__(self):
        return len(self.heap)
    
    def includes(self, condition_1):
        return condition_1 in self.heap

def restructure_path(node, start_city, reached_node, frontier):
    '''
    Trace back the most optimal path, get nodes in frontier and totai nodes generated
    '''
    solution_path = [node]
    curr_city = node.city
    while curr_city != start_city:
        solution_path.insert(0, reached_node[curr_city])
        curr_city = reached_node[curr_city].city
    
    route = ""
    distance = 0.0
    for cities in range(len(solution_path)):
        route += solution_path[cities].city + " "
        distance += solution_path[cities].cost
    
    sys.stdout.write(f'Route found: {route}\n')
    sys.stdout.write(f'Distance: {distance} miles\n')
    sys.stdout.write(f'Total nodes generated: {len(reached_node)}\n')
    sys.stdout.write(f'Nodes left in frontier: {len(frontier)}\n')
    
def parse_city_distance(city_distances, node, sub_key):
    '''
    Parse a specific children city's distance by parent city's name
    '''
    curr_distance = city_distances.get(str(node), None)
    for distance in curr_distance:
        if sub_key in distance.keys():
            return distance[sub_key]

def calculate_optimal_path(start_state, start_point, destination_point, city_distance, city_location):
    sys.stdout.write(f'Search for a path from {start_point} to {destination_point}...\n')
    
    node = TreeNode(
        state=start_state, 
        city=start_point,
        long=city_location[start_point][1],
        lat=city_location[start_point][0],
        cost=0.0
    )
    visited = set()
    frontier = PriorityQueue()
    frontier.add(node)
    reached = {}
    cost = {node.city: 0}

    while frontier:
        node = frontier.pop()
        '''
        Note: Remove line 85-86 will result in inefficiency of the algorithm, which takes long time to find
        the optimal path with repeated nodes.
        '''
        if node.city in visited:
            continue
        if node.isGoal(destination_point):
            sys.stdout.write(f'Target found: {node.city} {node.lat} {node.long}\n')
            return restructure_path(node, start_point, reached, frontier)
        
        visited.add(node.city)
        sys.stdout.write(f'Expanding: {node.city})\n')
        for i in city_distance[node.city]:
            city_name = str(list(i.keys())[0])
            input_distance = parse_city_distance(city_distance, node.city, city_name)
            child = TreeNode(
                city_name, 
                lat=city_location[city_name][0], 
                long=city_location[city_name][1],
                cost = input_distance
            )
            
            child_cost = node.cost + haversine((node.lat, node.long), \
                (city_location[destination_point][0], city_location[destination_point][1]), unit=Unit.MILES)

            frontier.add(child, priority=child_cost)
            if child.city not in reached or child_cost < cost[child.city]:
                reached.update({child.city:node})
                cost[child.city] = child_cost
                
    return -1

def get_user_input(location):
    '''
    Prompt messages asking users for start and destination city.
    '''
    starting_point = ''
    destination_point = ''

    while starting_point != '0' and destination_point != '0':
        starting_point = input("Please enter name of start city (0 to quit): ")
        if starting_point != '0' and starting_point in location:
            destination_point = input("Please enter name of end city (0 to quit): ")
            if destination_point in location:
                return starting_point, destination_point
            elif destination_point != '0' and destination_point not in location:
                sys.stdout.write("No end city found!\n")
            else:
                sys.exit("Goodbye.\n")
        elif starting_point != '0' and starting_point not in location:
            sys.stdout.write("No start city found!\n")
        elif starting_point == '0' or destination_point == '0':
            sys.exit("Goodbye.\n")

def parse_city_data_file(data_file):
    city_data_regex = re.compile(r"(?P<city>^.+) "
                                 r"(?P<lat>-*\d+\.\d+) "
                                 r"(?P<lon>-*\d+\.\d+)"
                                 )

    city_distance_regex = re.compile(r"(?P<city1>^.+), "
                                     r"(?P<city2>.+): "
                                     r"(?P<dist>-?\d+.\d+)"
                                    )

    city_location = defaultdict(list)
    city_distance = defaultdict(list)
    city_count = 0
    with open(data_file) as city_file:
        for line in city_file.readlines():
            city_result = city_data_regex.search(line)
            city_distance_result = city_distance_regex.search(line)
            if city_result != None:
                city_name = city_result.group('city')
                latitude = float(city_result.group('lat'))
                longitude = float(city_result.group('lon'))
    
                city_count = city_count + 1
                city_location[city_name].append(latitude)
                city_location[city_name].append(longitude)
               
            elif city_distance_result != None:
                city1_name = city_distance_result.group('city1')
                city2_name = city_distance_result.group('city2')
                distance = float(city_distance_result.group('dist'))
                city_distance[city1_name].append({
                    city2_name: distance
                })
                city_distance[city2_name].append({
                    city1_name: distance
                })
    sys.stdout.write("Reading data .... Done\n")
    sys.stdout.write(f'Number of cities: {city_count}\n')
    return city_location, city_distance

def main():
    filename = sys.argv[1]
    city_location, city_distance = parse_city_data_file(filename)
    start_point, end_point = get_user_input(city_location)
    calculate_optimal_path((0,0), start_point, end_point, city_distance, city_location)

main()
    
