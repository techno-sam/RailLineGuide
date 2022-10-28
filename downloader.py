import sys
import typing
import json
from pwiki.wiki import Wiki, WikiText, Session, Path, NSManager, OQuery
from pwiki.wparser import WikiTemplate, WParser
import pwiki.mquery

from common import StationPart, Link


class CustomizableEndpointWiki(Wiki):
    def __init__(self, domain: str = "en.wikipedia.org", api_endpoint: str = None, username: str = None,  # noqa
                 password: str = None, cookie_jar: Path = Path(".")):
        """Initializer, creates a new Wiki object.

                Args:
                    domain (str): The shorthand domain of the Wiki to target (e.g. "en.wikipedia.org")
                    username (str, optional): The username to login as. Does nothing if `password` is not set.  Defaults to None.
                    password (str, optional): The password to use when logging in. Does nothing if `username` is not set.  Defaults to None.
                    cookie_jar (Path, optional): The directory to save/read cookies to/from.  Disable by setting this to `None`.  Note that in order to save cookies you still have to call `self.save_cookies()`. Defaults to Path(".").
                """
        if api_endpoint is None:
            self.endpoint: str = f"https://{domain}/w/api.php"
        else:
            self.endpoint: str = api_endpoint
        self.domain: str = domain
        self.client: Session = Session()
        self.client.headers.update({"User-Agent": "pwiki"})

        self.username: str = None  # noqa
        self.cookie_jar: Path = cookie_jar
        self.is_logged_in: bool = False
        self.csrf_token: str = "+\\"

        self._refresh_rights()

        if not self._load_cookies(username):
            self.login(username, password)

        self.ns_manager: NSManager = OQuery.fetch_namespaces(self)


api_path = "http://wiki.linux-forks.de/mediawiki/api.php"
lw_wiki = CustomizableEndpointWiki(domain="wiki.linux-forks.de",
                                   api_endpoint="https://wiki.linux-forks.de/mediawiki/api.php",
                                   cookie_jar=Path("./cookies"),
                                   username="Apprentice")  # make username lowercase to login, uppercase to use cookies
lw_wiki.save_cookies()


def clean_stations(a: list) -> list:
    return [v for v in a if "Category:" not in v]


ignored_systems = ["Cato's Rail"]

stations_cat_path = "cached_data/stations.json"
try:
    with open(stations_cat_path) as f:
        stations_list: typing.List[str] = clean_stations(json.load(f))
        print("Loaded cached stations...")
except (FileNotFoundError, json.JSONDecodeError):
    print("Requesting stations from wiki...")
    stations_list: typing.List[str] = clean_stations(lw_wiki.category_members("Category:Stations"))
    print("Received stations from wiki...")
    with open(stations_cat_path, "w") as f:
        json.dump(stations_list, f, indent=4)
    print("Saved stations to cache...")

stations_list.remove("Forks:Example Station")
print(stations_list)

##############################
# Download All Station Pages #
##############################
stations_data_path = "cached_data/station_pages.json"
try:
    with open(stations_data_path) as f:
        stations_data = json.load(f)
        print("Loaded cached station data...")
except (FileNotFoundError, json.JSONDecodeError):
    print("Requesting station data from wiki...")
    stations_data = pwiki.mquery.MQuery.page_text(lw_wiki, stations_list)
    print("Received station data from wiki...")
    with open(stations_data_path, "w") as f:
        json.dump(stations_data, f, indent=4)
    print("Saved station data to cache...")

try:
    del stations_data["Forks:Example Station"]
except KeyError:
    pass

##############
# Parse Data #
##############
test_station = "Hardware Store Subway Station"
# print(stations_data[test_station])

# print(len(stations_data), len(stations_data)**2)
print()
print()

closed_stations = set()

# Use this where it is impossible/impractical to add transfer data, and it needs to be ignored therefore
skip_transfer_param = [  # ("Station Name", "System Name", "Line Name")
    ("Shore Station", "OTL", "Ice")
]


def strip_whitespace_around(text: str, symbol: str) -> str:
    while " " + symbol in text:
        text = text.replace(" " + symbol, symbol)

    while symbol + " " in text:
        text = text.replace(symbol + " ", symbol)

    return text


def s_line_to_dict(stat_name: str, s_line: str):
    # print("s_line:", s_line)
    pieces = strip_whitespace_around(s_line.removeprefix("{{s-line|").removesuffix("}}"), "|").split("|")
    # print("pieces:", pieces)
    out = {}
    for piece in pieces:
        if piece == "transfer" and (stat_name, out["system"], out["line"]) in skip_transfer_param:
            continue
        if "=" not in piece:
            raise ValueError(f"'{piece}' for {s_line}")
        else:
            k, v = strip_whitespace_around(piece, "=").split("=")
            out[k] = v
    return out


def get_stations_text_for_systems(*system_names: str) -> typing.Dict[str, str]:
    needs_downloading = []
    out = {}
    for system_name in system_names:
        system_name = system_name + " stations"
        functional_name = system_name.replace(" ", "_")
        file_path = "cached_data/line_stations/" + functional_name + ".txt"
        try:
            with open(file_path) as file:
                out[system_name] = file.read()
        except FileNotFoundError:
            print(f"Will download `Template:{functional_name}`")
            needs_downloading.append("Template:" + functional_name)

    out.update(pwiki.mquery.MQuery.page_text(lw_wiki, needs_downloading))
    for name, contents in out.items():
        file_path = "cached_data/line_stations/" + name.replace(" ", "_").replace("Template:", "") + ".txt"
        with open(file_path, "w") as file:
            file.write(contents)
    return out


open_station_parts: typing.List[StationPart] = []


def param_truthy(param: str) -> bool:
    return param in ["true", "yes", "y", "t", "on", "1"]


for station_name, page_contents in stations_data.items():
    station_name: str
    page_contents: str
    lines: typing.List[str] = page_contents.split("\n")
    print()
    print()
    print(station_name)
    for line in lines:
        if line.startswith("| closed"):
            closed_stations.add(station_name)
            print(f"\tCLOSED!!!: {line}")
            break
        if line.startswith("{{s-line"):
            '''if station_name == "Shore Station":
                wt = WParser.parse(wiki=lw_wiki, text=line)
                template = wt.templates[0]
                print(template)
                print(template.keys())
                print(template.values())'''
            # print(station_name)
            line_dict = s_line_to_dict(station_name, line)
            # print(line_dict)
            train_system = line_dict["system"]
            train_line = line_dict["line"]
            previous_station = line_dict.get("previous",
                                             None)  # Need parsing with page "System_Name_stations" to get full page name. Do this now
            next_station = line_dict.get("next", None)
            if next_station == "":
                next_station = None
            if previous_station == "":
                previous_station = None
            if train_system in ignored_systems:
                continue
            if previous_station == "???" or next_station == "???":
                continue
            open_station_parts.append(StationPart(station_name, train_system, train_line, previous_station, next_station,
                                                  transfer_station=line_dict.get("transfer", None),
                                                  oneway_prev=param_truthy(line_dict.get("oneway1", "false")),
                                                  oneway_next=param_truthy(line_dict.get("oneway2", "false"))
                                                  ))
            if "transfer" in line_dict:
                print(f"\tTransfer from `{station_name}` to `{line_dict['transfer']}`")
            print(f"\t{station_name}: {line_dict}")
            print()

all_systems: typing.Set[str] = set()
for station_part in open_station_parts:
    all_systems.add(station_part.system)

if input("Download all system station templates? (y/n) ") == "y":
    get_stations_text_for_systems(*all_systems)

def_stat = "$ Station"
def_raw = "$"
def_sub = "$ Subway Station"

system_namings = {  # TODO Pull this automatically from files (at least where not using Adjacent Stations)
    "ATL": {
        "East Origin": "East Origin Station (ATL)",
        "Südkreuz": "Südkreuz Station (Personhood)",
        "#default": "$ Station"
    },
    "Birch Bay": {
        "Large Beach": "Large Beach Subway Station",
        "Residential Area": "Residential Area",
        "#default": "$ Station (Birch Bay)"
    },
    "DTL": {
        "Market": "Banana Place Market Station",
        "#default": "$ Station"
    },
    "Eden Ferries": {
        "Shanielle Inlet": "Shanielle Inlet Station",
        "#default": "$Ferry  Station"
    },
    "Express Lines": {
        "Spawn": "Spawn Main Station",
        "Origin": "Marcus Street Station",
        "Stallmangrad": "Stallmangrad Central Station",
        "Nadinetopia": "Nadinetopia Station (Personhood)",
        "Northlands Interchange": "Northlands Interchange",
        "Sra/Gef": "Sraczka2's Village Station / Garden of Eden Ferry Station",
        "#default": "$ Station"
    },
    "Ferry Network": {
        "#default": "$ Ferry Station"
    },
    "Local Lines": {
        "Spawn": "Spawn Main Station",
        "Origin": "Marcuse Street Station",
        "Schwarzschild Passing Track": "Schwarzschild Passing Track",
        "#default": "$ Station"
    },
    "LTBAG": {
        "Anju Crossing Central": "Anju Crossing Central",
        "Canyon": "Canyon City Station",
        "Shore": "Shore LTBAG Station",
        "#default": "$ Station"
    },
    "Origin Ring Lines": {
        "Origin": "Origin Subway Station",
        "Marcus Street": "Marcuse Street Station",
        "#default": "$ Station (Origin Ring Lines)"
    },
    "OTL": {
        "The Cube": "The Cube Station",
        "Cube": "The Cube Station",
        "cube": "The Cube Station",

        "Neverbuild West": "Neverbuild West Station",
        "West": "Neverbuild West Station",
        "west": "Neverbuild West Station",

        "Personhood": "Personhood Main Station",
        "personhood": "Personhood Main Station",

        "central": "Neverbuild Station",
        "Bamboo Bridge": "Bamboo Bridge Station (OTL)",

        "island": "Island Station",
        "shore": "Shore Station",
        "bananawood": "Bananawood Station",
        "shikatanaevo": "Shikatanaevo Station",
        "dodemo-iisk": "Dodemo-iisk Station",

        "North harbour": "North Harbour Station",
        "north harbour": "North Harbour Station",
        "North Harbor": "North Harbour Station",
        "North harbor": "North Harbour Station",
        "north harbor": "North Harbour Station",

        "proletarian": "Proletarian Station",

        "Bambus": "Bambus Station",
        "bambus": "Bambus Station",

        "#default": "$ Station (Neverbuild)"
    },
    "Personhood": {
        "Personhood West": "Personhood West Station",
        "west": "Personhood West Station",
        "Personhood South": "Personhood South Station",
        "south": "Personhood South Station",
        "Personhood Main Station": "Personhood Main Station",
        "Main": "Personhood Main Station",
        "shore": "Shore Station",
        "Shore": "Shore Station",
        "Marnack Mills": "Marnack Mills Station",
        "Shoot Hills": "Shoot Hills Station",
        "Panda Reserve": "Panda Reserve Station",
        "Bamboo Bay Village": "Bamboo Bay Village Station",
        "Bamboo Bay South": "Bamboo Bay South Station",
        "Bamboo Bay West": "Bamboo Bay West Station",
        "Deep Valley Mountain": "Deep Valley Mountain Station",
        "Memory": "Memory Station",
        "Plantain Hills": "Plantain Hills Station",
        "#default": "$ Station (Personhood)"
    },
    "Piet": {
        "Smacker": "Smacker Station (Piet Rail)",
        "#default": "$ Station"
    },
    "Railway 56": {
        "lighthouse": "Lighthouse Station",
        "#default": "$ Station (Railway 56)"
    },
    "South Forest Subway": {
        "South Forest": "South Forest Station",
        "#default": "$ Subway Station"
    },
    "Spawn Subway": {
        "AHRAZHUL": "AHRAZHUL's Station",
        "slohag": "Smacker's Land of Hope and Glory Subway Station",
        "Eiffel Street": def_stat,
        "Perl Prospect": def_stat,
        "Apple Grove": def_stat,
        "Leekston": def_stat,
        "Leekston Jungle": def_stat,
        "Leekston East": def_stat,
        "Leekston Ferry": def_stat,
        "Land's End (Planetarium)": def_stat,
        "Birch Bay": def_stat,
        "Banana Forest": def_stat,
        "Anju Crossing Central": def_stat,
        "Szymon's Dam": def_raw,
        "Marcuse Street": def_stat,
        "Spawn Main": "Spawn Main Station (Subway)",
        "Pierre Berton Street": "Origin Berton Street Station",
        "Land's End": "Land's End (Planetarium) Station",
        "#default": def_sub
    },
    "Stallmangrad": {
        "Stallmangrad": "Stallmangrad Central Station",
        "Banana Junction": "Banana Junction Station",
        "Ray City": def_stat,
        "#default": "$ Subway Station (Stallmangrad)"
    },
    "Trap City": {
        "central": "Trap City Central Station",
        "north": "Trap City North Station",
        "#default": def_stat
    },
    "Trisiston": {
        "Trisiston": def_stat,
        "Elders Valley": def_stat,
        "Elders Valley Northwest": def_stat,
        "Elders Valley Beach": def_stat,
        "Elders Valley West": def_stat,
        "Elders Valley South": def_stat,
        "iceberg on bamboo": "Iceberg on Bamboo Station",
        "iceberg": "Iceberg on Bamboo Station",
        "Cato's Village": def_stat,
        "Iceberg on Bamboo": def_stat,
        "#default": "$ Station (Trisiston)"
    },
    "Veaca": {
        "V Tecta": "V Tecta Union Station",
        "PWH": "Personhood West Station",
        "#default": def_stat
    }
}


def fill_in_station_name(system: str, name: typing.Optional[str]) -> typing.Optional[str]:
    if name is None:
        return name
    try:
        s = system_namings[system]
        try:
            ret = s[name]
        except KeyError:
            ret = s["#default"]
    except KeyError as e:
        print(repr(e), file=sys.stderr)
        ret = name
    return ret.replace("$", name)


for station_part in open_station_parts:
    if station_part.transfer_station is not None:
        station_part.transfer_station = fill_in_station_name(station_part.system, station_part.transfer_station)
    station_part.previous_station_name = fill_in_station_name(station_part.system, station_part.previous_station_name)
    station_part.next_station_name = fill_in_station_name(station_part.system, station_part.next_station_name)


print("Closed Stations:")
for cs in closed_stations:
    print(f"\t{cs}")
input("\nPress [Enter] to continue...")

print("Converting StationParts to Links")
all_links = []
for station_part in open_station_parts:
    all_links.extend(station_part.to_links())

pre = len(all_links)
all_links = list(set(all_links))
post = len(all_links)
print(f"Number of links: {pre}")
print(f"Number of (deduplicated) links: {post}, difference: {pre-post}")
print(f"Number of open stations: {len(stations_data)-len(closed_stations)}")

all_links.sort(key=lambda x: str(x))
print("Saving links...")
with open("saves/all_links.json", "w") as f:
    val = [v.save() for v in all_links]
    json.dump(val, f, indent=4)
print("Done.")
