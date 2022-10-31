import json
import math
import time
import os
from common import Link, Station, StationGraph
from colorama import Fore, Style


# Load links from saves/all_links.json
with open("saves/all_links.json", "r") as f:
    all_links_data = json.load(f)
all_links: list[Link] = []
for dat in all_links_data:
    all_links.append(Link.load(dat))

# Load station coordinates from saves/station_coordinates.json
with open("saves/station_coordinates.json", "r") as f:
    station_coordinates: dict[str, list[int]] = json.load(f)

station_graph = StationGraph()
# Add all links to graph
for link in all_links:
    link.calculate_distance(station_coordinates)
    station_graph.add_link(link)


def print_all_stations():
    print(f"All stations ({len(station_graph.all_station_names())} total):")
    alternate = False
    for name in station_graph.all_station_names():
        alternate = not alternate
        print(f"\t{Fore.BLUE if alternate else Fore.CYAN}{name}{Style.RESET_ALL}")


print_all_stations()
# input("Press [Enter] to continue...")


def time_format(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds//60}m {seconds%60}s"
    else:
        return f"{seconds//3600}h {seconds//60%60}m {seconds%60}s"


termini: dict[tuple[str, str], dict[str, str | list]] = {}
for system_dir in os.listdir("cached_data/termini"):
    for line_file in os.listdir("cached_data/termini/" + system_dir):
        with open(f"cached_data/termini/{system_dir}/{line_file}", "r") as f:
            termini[(system_dir.replace("_", " "), line_file.replace("_", " ").replace(".json", ""))] = json.load(f)


def find_and_print_route():
    from_name = input("From: ")
    if " -> " in from_name:
        to_name = from_name.split(" -> ")[1]
        from_name = from_name.split(" -> ")[0]
    else:
        to_name = input("To: ")
#    from_name = "Koshahood Station"
#    to_name = "CXC Station"  # About 13 seconds w/o threading and strategy=100
    print("Solving...\n")
    pre = time.perf_counter()
    routes = station_graph.find_route(from_name, to_name, change_weight=0.1, strategy=500, max_iters=200000)
    post = time.perf_counter()
    print(f"\n{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}Time taken: {post - pre:.3f}s{Style.RESET_ALL}")
    # print("Done solving...")
    if len(routes) == 0:
        print("No routes found")
    else:
        walk_speed = 2.5  # m/s
        train_speed = 12  # m/s
        print()
        try:
            from_pos = station_coordinates[from_name]
            to_pos = station_coordinates[to_name]

            dist = math.sqrt((from_pos[0] - to_pos[0]) ** 2
                             + (from_pos[1] - to_pos[1]) ** 2
                             + (from_pos[2] - to_pos[2]) ** 2)
            print(f"{Fore.LIGHTWHITE_EX}Distance (as the crow walks): {dist/1000:.2f} km  {Fore.LIGHTYELLOW_EX}"
                  f"Should take: {time_format(round(dist/walk_speed))}{Style.RESET_ALL}")
        except KeyError:
            print(f"{Fore.LIGHTWHITE_EX}Distance (as the crow walks): Unknown{Style.RESET_ALL}")

        train_dist = routes[0].distance_cost()
        print(f"{Fore.LIGHTWHITE_EX}Distance (riding on a train): {train_dist/1000:.2f} km  {Fore.LIGHTYELLOW_EX}"
              f"Should take: {time_format(round(train_dist/train_speed))}{Style.RESET_ALL}")
        routes[0].print_test(termini, verbose=False, unmerged=True)
        input("Press [Enter] to continue...")
        print("\n\n\n")
        print_all_stations()


while True:
    try:
        find_and_print_route()
    except Exception as e:
        raise
