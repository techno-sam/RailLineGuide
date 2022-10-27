import json
import time
from common import Link, Station, StationGraph
from colorama import Fore, Style


# Load links from saves/all_links.json
with open("saves/all_links.json", "r") as f:
    all_links_data = json.load(f)
all_links: list[Link] = []
for dat in all_links_data:
    all_links.append(Link.load(dat))

station_graph = StationGraph()
# Add all links to graph
for link in all_links:
    station_graph.add_link(link)


def print_all_stations():
    print("All stations:")
    for name in station_graph.all_station_names():
        print(f"\t{name}")


print_all_stations()
# input("Press [Enter] to continue...")


def find_and_print_route():
#    from_name = input("From: ")
#    to_name = input("To: ")
    from_name = "Koshahood Station"
    to_name = "CXC Station"  # About 12 seconds w/o threading
    print("Solving...\n")
    pre = time.perf_counter()
    routes = station_graph.find_route(from_name, to_name, change_weight=0.1, strategy=100)
    post = time.perf_counter()
    print(f"\n{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}Time taken: {post - pre:.3f}s{Style.RESET_ALL}")
    # print("Done solving...")
    if len(routes) == 0:
        print("No routes found")
    else:
        print()
        routes[0].print_test(False)
        input("Press [Enter] to continue...")
        print_all_stations()


while True:
    try:
        find_and_print_route()
    except Exception as e:
        raise

"""
test_routes = station_graph.find_route("Wolf Rock Station", "Zoo Subway Station", change_weight=0.1)
for i in range(50):
    rt = test_routes[i]
    print(f"Route {i}: {rt} {rt.cost(0)} (Merged: {rt.merged().cost(0)})")

try:
    while True:
        index = int(input(f"Enter route index (0-{len(test_routes)-1}): "))
        rt1 = test_routes[index]
        '''valid = rt1.is_valid(True)
        print(f"Route {index}: {rt1} {rt1.cost(0)} (Merged: {rt1.merge().cost(0)}) (Valid: {valid})")
        for link in rt1.links:
            print(f"\t{link}")
        print("\nMerged:")
        for link in rt1.merge().links:
            print(f"\t{link}")'''
        print(f"Route {index}: ", end="")
        rt1.print_test()
except (TypeError, IndexError):
    print("Ok, done...")"""
