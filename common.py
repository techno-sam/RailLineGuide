__all__ = ["StationPart", "Link"]

import typing
import json

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
        return d

    @staticmethod
    def load(data: dict[str, str]):
        frm = data["from"]
        to = data["to"]
        system = data.get("system", None)
        line = data.get("line", None)
        is_transfer = data.get("transfer", False)
        return Link(frm, to, system, line, is_transfer)


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
