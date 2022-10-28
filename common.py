__all__ = ["StationPart", "Link", "Station", "StationGraph"]

import time
import typing
import queue
import threading
from colorama import Fore, Style

_opt_str = typing.Optional[str]


class Link:
    def __init__(self, from_name: str, to_name: str, rail_system: _opt_str, rail_line: _opt_str,
                 is_transfer: bool = False):
        """One-way link between two stations

        :param from_name: Station of Origin
        :param to_name: Destination Station
        :param rail_system: Route's System (ignored for transfers)
        :param rail_line: Route's Line (ignored for transfers)
        :param is_transfer: If this route is a transfer on foot (recommended to use Link.transfer)
        """
        self.from_name = from_name
        """Station of Origin"""

        self.to_name = to_name
        """Destination Station"""

        self.rail_system = None if is_transfer else rail_system
        """Absent if transfer"""

        self.rail_line = None if is_transfer else rail_line
        """Absent if transfer"""

        self.is_transfer = is_transfer
        """Rather than taking a train, transfer on foot between stations"""

        self.is_manual = False
        """If this link was manually added"""

    def manual(self):
        """Mark this link as manually added"""
        self.is_manual = True
        return self

    @staticmethod
    def transfer(from_name: str, to_name: str):
        """Quick utility to build a transfer between two nearby stations"""
        return Link(from_name, to_name, None, None, True)

    def __repr__(self) -> str:
        return f"Link [{str(self)}]"

    def __str__(self) -> str:
        out = f"{self.from_name} -> {self.to_name} "
        if self.is_transfer:
            out += "(Transfer on foot)"
        else:
            out += f"(Along `{self.rail_system}` Line `{self.rail_line}`)"
        if self.is_manual:
            out += " (Manual)"
        return out

    def __hash__(self) -> int:
        return hash(str(self))  # Our string method is built using all our attributes

    def __eq__(self, other):
        return isinstance(other, Link) and str(self) == str(other)

    def save(self) -> dict[str, str]:
        d = {
            "from": self.from_name,
            "to": self.to_name
        }
        if self.is_transfer:
            d["is_transfer"] = True
        else:
            d.update({
                "system": self.rail_system,
                "line": self.rail_line
            })
        if self.is_manual:
            d["manual"] = True
        return d

    @staticmethod
    def load(data: dict[str, str]):
        frm = data["from"]
        to = data["to"]
        system = data.get("system", None)
        line = data.get("line", None)
        is_transfer = data.get("transfer", False)
        link = Link(frm, to, system, line, is_transfer)
        if data.get("manual", False):
            link.manual()
        return link

    def copy(self) -> "Link":
        return Link.load(self.save())


class Station:
    def __init__(self, name: str, *links: Link):
        """A station with a name and a list of links to other stations

        :param name: Station name
        :param links: Links to other stations"""
        self.name = name
        """Station name"""

        self.links: typing.List[Link] = list(links)
        """Links departing from this station"""

    def __repr__(self) -> str:
        return f"Station [{self.name}]"

    def links_on_system(self, system: str, line: str = None) -> typing.List[Link]:
        """Limit number of transfers required for a route"""
        out = []
        for link in self.links:
            if link.rail_system == system and (line is None or link.rail_line == line):
                out.append(link)
        return out

    def copy(self):
        return Station(self.name, *self.links)


class Route:
    def __init__(self, station_graph: "StationGraph", start: Station, goal: str, *links: Link):
        self.links: list[Link] = list(links)
        self._traveled_station_names: set[str] = {start.name}
        self.start = start
        self.current_end = start.name
        self.goal = goal
        self.station_graph = station_graph

    def is_valid(self, dbg=False) -> bool:
        prev_station = None
        for link in self.links:
            if dbg:
                print("Link:", link, ", prev:", prev_station)
            if prev_station is not None and prev_station != link.from_name:
                print(prev_station, "|", link)
                return False
            prev_station = link.to_name
        return True

    def print_test(self, verbose=True):
        if verbose:
            print(f"{self} Cost: {self.cost(0)} (Merged cost: {self.merged().cost(0)}) (Valid: {self.is_valid()})")
            for link in self.links:
                print(f"\t{link}")
            print("\nMerged:")
        else:
            print(f"{Fore.BLUE}{Style.BRIGHT}{self.start.name} -> {self.goal}{Style.NORMAL}{Fore.CYAN} | Cost:"
                  f" {self.cost(0)} | Merged: {self.merged().cost(0)}{Style.RESET_ALL}")
        alternate = False
        for link in self.merged().links:
            alternate = not alternate
            print(f"\t{Fore.GREEN if alternate else Fore.LIGHTGREEN_EX}{link}{Style.RESET_ALL}")

    def add_link(self, link: Link) -> "Route":
        if link.to_name in self._traveled_station_names:
            raise ValueError("Cannot create a loop")
        self._traveled_station_names.add(link.to_name)

        new_route = Route(self.station_graph, self.start, self.goal, *self.links)
        for tsn in self._traveled_station_names:
            new_route._traveled_station_names.add(tsn)
        if link.from_name != self.current_end:
            raise Exception(f"{link} does not originate at {self.current_end}")
        if new_route.links and new_route.links[-1].to_name != link.from_name:
            raise Exception(f"{new_route.links} incompatible with {link}")
        new_route.links.append(link)
        new_route.current_end = link.to_name
        return new_route

    def merged(self) -> "Route":
        """Merge all links in this route along the same line and system into one"""
        new_route = Route(self.station_graph, self.start, self.goal)
        for link in self.links:
            if new_route.links:
                last_link = new_route.links[-1]
                if last_link.rail_system == link.rail_system and last_link.rail_line == link.rail_line\
                        and not last_link.is_transfer and not link.is_transfer:
                    new_route.links[-1].to_name = link.to_name
                else:
                    new_route.links.append(link.copy())
            else:
                new_route.links.append(link.copy())
        new_route.current_end = self.current_end
        for tsn in self._traveled_station_names:
            new_route._traveled_station_names.add(tsn)
        return new_route

    def is_complete(self) -> bool:
        return self.current_end == self.goal

    def cost(self, change_weight: float) -> int:
        cost = 0
        previous_system = None
        previous_line = None
        for link in self.links:
            if previous_system is not None and previous_system is not None:
                if link.rail_system != previous_system or link.rail_line != previous_line:
                    cost += change_weight
            cost += 1
            previous_system = link.rail_system
            previous_line = link.rail_line
        return cost

    def __repr__(self) -> str:
        return f"Route [{self.start.name} -> {self.current_end} (Goal: {self.goal})]"

    def __len__(self) -> int:
        return len(self.links)

    def __lt__(self, other):
        if isinstance(other, Route):
            return self.cost(0) > other.cost(0)
        else:
            raise TypeError(f"< not supported between instances of 'Route' and {other.__class__}")


# manage stations and build routes
class StationGraph:
    def __init__(self):
        self._stations: typing.Dict[str, Station] = {}

    def add_station(self, station: Station):
        self._stations[station.name] = station

    def add_station_name(self, name: str):
        self._stations[name] = Station(name)

    def add_link(self, link: Link):
        if link.from_name not in self._stations:
            self.add_station_name(link.from_name)

        self._stations[link.from_name].links.append(link)

    def all_station_names(self) -> typing.List[str]:
        ret = list(self._stations.keys())
        ret.sort()
        return ret

    def find_route(self, from_name: str, to_name: str, strategy: int = 10, change_weight: float = 0.4,
                   max_iters: int = -1) -> list[Route]:
        """Find a route between two stations

        :param from_name: Station of Origin
        :param to_name: Destination Station
        :param strategy: -1 for perfect: brute force all possible routes; 0: return first route found
        1 - infinity: make random routes until `strategy` routes have been found
        :param change_weight: How much to penalize changing trains, ex 1.0 means changing trains is as bad as an extra
        station traveled
        :param max_iters: if > 0, force stop after `max_iters` iterations
        """
        for name, stat in self._stations.items():
            if name != stat.name:
                raise ValueError(f"Name {name} doesn't match station {stat.name}| {stat}")
        if from_name not in self._stations or to_name not in self._stations:
            return []

        # Setup route solving
        start = time.time()

        solved_routes: list[Route] = []

        route_queue: queue.Queue[Route] = queue.PriorityQueue()
        route_queue.put(Route(self, self._stations[from_name], to_name))

        def solver(solved_routes_list: list[Route]):
            best_merged_hops = float("inf")
            iters = 0
            route_queue_private: queue.Queue[Route] = queue.Queue()
            while True:
                if 0 < max_iters < iters:
                    break
                if True:
                    if strategy == -1:
                        if (len(solved_routes_list) > 500) or (best_merged_hops <= 3 and len(solved_routes_list) > 5)\
                                or (len(solved_routes_list) > 0 and time.time()-start > 50)\
                                or (time.time()-start > 30 and best_merged_hops <= 6):
                            break
                    elif strategy == 0:
                        if len(solved_routes_list) > 0:
                            break
                    else:
                        if len(solved_routes_list) >= strategy:
                            break
                iters += 1
                if iters % 5000 == 0:
                    print("Queue size:", route_queue_private.qsize(), "Solved routes:", len(solved_routes_list), "Iters:", iters)
                if iters % 1700 == 0:  # Best: 1700
                    #print(f"{Fore.GREEN}Queue size: {route_queue_private.qsize()} Solved routes: {len(solved_routes_list)} Iters: {iters}{Style.RESET_ALL}")
                    #print(f"{Style.BRIGHT}{Fore.YELLOW}[{threading.current_thread().name}] Pushing items{Style.RESET_ALL}")
                    while True:
                        try:
                            val = route_queue_private.get(block=False)
                            route_queue.put(val)
                        except queue.Empty:
                            break
                try:
                    rt = route_queue_private.get(block=False)
                except queue.Empty:
#                    print(f"{Style.BRIGHT}{Fore.LIGHTBLUE_EX}[{threading.current_thread().name}] Private queue empty, "
#                          f"getting new items...{Style.RESET_ALL}")
                    for _ in range(10):  # Best: 10
                        try:
                            route_queue_private.put(route_queue.get(block=False))
                        except queue.Empty:
                            break
#                    print(f"{threading.current_thread().name} Got.")
                    try:
                        rt = route_queue_private.get(block=False)
                    except queue.Empty:
                        print("Didn't find any, sleeping")
                        time.sleep(1)
                        continue
                # print(f"Got route {rt}")
                # print(f"{rt}: {len(rt)}")
                end_station = self._stations[rt.current_end]

                # If we can stay on the same train to get to a station, do so
                only_acceptable = {}
                if rt.links:
                    system, line = rt.links[-1].rail_system, rt.links[-1].rail_line
                    for on_system in end_station.links_on_system(system, line):
                        only_acceptable[on_system.to_name] = on_system

                to_append = []

                for link in end_station.links:
                    try:
                        dst = link.to_name
                        if dst in only_acceptable and only_acceptable[dst] != link:
                            continue
                        new_rt = rt.add_link(link)
                        if not new_rt.is_valid():
                            raise Exception(f"Invalid route built from: {rt}, es: {end_station}, new: {new_rt}, link: {link}")
                        if new_rt.is_complete():
                            # with solved_routes_mut:
                            #    solved_routes_list.append(new_rt)
                            to_append.append(new_rt)
                            merged_cost = new_rt.merged().cost(0)
                            if merged_cost < best_merged_hops:
                                best_merged_hops = merged_cost
                                print(f"{Fore.RED}New best merged hops: {best_merged_hops}{Style.RESET_ALL}")
                        else:
                            route_queue_private.put(new_rt)
                    except ValueError as e:
                        pass  # print(f"Error adding link {link} to route {rt}: {e}")

                for ta in to_append:
                    solved_routes_list.append(ta)
            print(f"{Style.BRIGHT}{Fore.CYAN}{threading.current_thread().name} exited...")

        solver(solved_routes)

        # Koshahood Station -> CXC Station
        print("Returning...")
        solved_routes.sort(key=lambda x: x.cost(change_weight))
        return solved_routes


DISABLED_LINKS: typing.List[Link] = [

]


class StationPart:
    def __init__(self, name: str, system: str, sub_line: str, previous_station_name: typing.Optional[str],
                 next_station_name: typing.Optional[str], transfer_station: str = None, oneway_prev: bool = False,
                 oneway_next: bool = False):
        """Store all data for a station

        :param name: Full name of current station (Derived from page title)
        :param system: Name of system this route is on
        :param sub_line: Line within system this route is
        :param previous_station_name: Partial name of next station, will need to be qualified later with the help of get_stations_text_for_systems
        :param next_station_name: Partial name of previous station, see above
        :param transfer_station: Partial name of station to transfer to, see above
        :param oneway_prev: Trains do not operate towards previous station
        :param oneway_next: Trains do not operate towards next station (NOTE: If oneway_prev is True, oneway_next will be forced False)
        """
        self.name = name
        """The name of the current station"""

        self.system = system
        """What rail system is this route on"""

        self.sub_line = sub_line
        """What line of the system is this route on"""

        self.previous_station_name = previous_station_name
        """Name of previous station in route"""

        self.next_station_name = next_station_name
        """Name of next station in route"""

        self.transfer_station = transfer_station
        """Station one must transfer to for this route"""

        self.oneway_prev = oneway_prev
        """Trains do not operate towards previous station"""

        self.oneway_next = oneway_next and not oneway_prev
        """Trains do not operate towards next station"""

    def __str__(self) -> str:
        out = "["
        if self.previous_station_name is not None:
            out += self.previous_station_name + " "
            if not self.oneway_prev:
                out += "<"
            out += "-> "
        out += "{" + self.name + "}"
        if self.next_station_name is not None:
            out += " <-"
            if not self.oneway_next:
                out += ">"
            out += " " + self.next_station_name
        out += f"] along <{self.system} ({self.sub_line})>"
        if self.transfer_station is not None:
            out += f" (Transfer to {self.transfer_station})"
        return out

    def to_links(self) -> typing.List[Link]:
        out: typing.List[Link] = []

        route_src = self.name

        if self.transfer_station is not None:
            route_src = self.transfer_station
            out.append(Link.transfer(self.name, self.transfer_station))
            out.append(Link.transfer(self.transfer_station, self.name))

        if self.previous_station_name is not None:
            out.append(Link(self.previous_station_name, route_src, self.system, self.sub_line))
            if not self.oneway_prev:
                out.append(Link(route_src, self.previous_station_name, self.system, self.sub_line))

        if self.next_station_name is not None:
            out.append(Link(self.next_station_name, route_src, self.system, self.sub_line))
            if not self.oneway_next:
                out.append(Link(route_src, self.next_station_name, self.system, self.sub_line))

        for disabled in DISABLED_LINKS:
            try:
                out.remove(disabled)
            except ValueError:
                pass

        return out
