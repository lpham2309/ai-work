import sys
import re
from collections import defaultdict

def calculate_optimal_path(start_point, destination_point):
    sys.write.stdout(f'Search for a path from {start_point} to {destination_point}...')


def get_user_input(location):
    starting_point = ''
    destination_point = ''

    while starting_point != '0':
        starting_point = input("Please enter name of start city (0 to quit): ")
        if starting_point != '0' and starting_point in location:
            destination_point = input("Please enter name of end city (0 to quit): ")
            if destination_point in location:
                return starting_point, destination_point
            else:
                sys.stdout.write("No end city found!\n")
        elif starting_point != '0' and starting_point not in location:
            sys.stdout.write("No start city found!\n")


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
    city_distance = {}
    city_count = 0
    city_file = open(data_file)
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
            city_distance[(city1_name, city2_name)] = distance

    sys.stdout.write("Reading data .... Done\n")
    sys.stdout.write(f'Number of cities: {city_count}\n')
    return city_location, city_distance

def main():
    filename = sys.argv[1]
    city_location, city_distance = parse_city_data_file(filename)

    try:
        start_point, end_point = get_user_input(city_location)
    except Exception as e:
        sys.stdout.write("Goodbye.\n")

    # optimal_path = calculate_optimal_path(start_point, end_point)



main()
    