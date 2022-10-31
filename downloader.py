import os
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
try:
    # make username lowercase to log in, uppercase to use cookies (e.g. "log_me_in" "Using_cookies"
    lw_wiki = CustomizableEndpointWiki(domain="wiki.linux-forks.de",
                                       api_endpoint="https://wiki.linux-forks.de/mediawiki/api.php",
                                       cookie_jar=Path("./cookies"),
                                       username="Apprentice")  # Replace username here
    lw_wiki.save_cookies()
except OSError:  # If we have no internet, try to function anyway - only works if all data is cached
    lw_wiki = None


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
    stations_list.extend(['42069 Mountain Station', "AHRAZHUL's Station", 'Ackermann Avenue Subway Station', 'Adorno Boulevard Subway Station', 'After Bridge Station', 'Agbar Subway Station', 'Aliane Valley Station', 'Anju Crossing Central', 'Apple Grove Station', 'Apple Plains Subway Station', 'Arcadius Station', 'Archangel Subway Station', "Ashstar's Station", 'Azena Transirejo Station', 'BHS10 Subway Station', 'Babbage Road Subway Station', 'Baka North Station', 'Bamboo Bay South Station', 'Bamboo Bay Village Station', 'Bamboo Bay West Station', 'Bamboo Hills Station', 'Bambus Station', 'Banach Forest Station', 'Banana Forest Station', 'Banana Junction Station', 'Banana Place Central Station', 'Banana Place Market Station', 'Bananame Subway Station', 'Bananawood Station', 'Beach Subway Station', "Beethoven's Valley Station", 'Bicycle Shop Station (Personhood)', 'BigFishCity Station', 'Birch Bay East Subway Station', 'Birch Bay Station', 'BlackDog Subway Station', 'Booze Grove Subway Station', 'Brimstone Station (Neverbuild)', 'C&C Annoying Yard', 'C&C Farm Station', "CalebJ's Factory Station (Personhood)", 'Canyon City Station', 'Caratheodory Street Subway Station', 'Cathedral Subway Station', "Cato's Village Station", 'Chainsaw Wood Station (Personhood)', 'Chasm of Segfault Station', 'Church Station', 'Church of Emacs Station (Personhood)', 'Churchill Street Subway Station', "Château d'Erstazi Station", 'Citrus Bridge Station', 'Clive Sinclair Station', 'Cobble Garden Station (Personhood)', 'Collis Hills Station', 'Colored Grasses Station', 'Community of Laza Station', 'Corona Canyon', 'Coulomb Street Subway Station', 'Cow Bridge Subway Station', 'Cross Bay Station', "Crossroads ARSE7's Shop Station", 'Crossroads City Hall South Station', 'Crossroads City Hall Station', "Crossroads Smacker's Station", 'Crossroads Station St. West Station', 'Crossroads West Mountains Station', 'Crystal Farms Station', 'Darwin Road Subway Station', 'Deep Valley Mountain Station', 'Desert Canyon Subway Station', 'Desert Junction Station', 'Desert Mountain Subway Station', 'Desert View Subway Station', 'Djungle City Subway Station', 'Dodemo-iisk Station', 'Dry Hills Station', 'EVO', 'East Origin Station (ATL)', 'Edenwood Beach Subway Station', 'Edenwood Subway Station', 'Ehlodex Station', 'Eiffel Street Station', 'Elders Valley Beach Station', 'Elders Valley North West Station', 'Elders Valley Northwest Station', 'Elders Valley South Station', 'Elderwood River Station', 'Erdős Street Subway Station', 'Erstaziland-Salt Factory Station', 'Eternal Ice Subway Station', 'Euler Street Station', 'Final Frontier Station', 'Flying Vine Station (Personhood)', 'Franklin Road Subway Station', 'Frege Street Subway Station', 'Freya Woods Station (Trisiston)', 'Fun Park Subway Station', 'Fungal Hills Station', 'GRUB Valley Station', 'Gabriel Plaza Subway Station', 'Garden of Eden Ferry Station', 'Gardon Street Station', 'Goldmann Street Station (Personhood)', 'Gpersonhood Station', 'Gram-Schmidt Street Subway Station', 'Green Edge Station', 'Green Hope Station', 'Greener Pastures Station', 'Greybush Plains Subway Station', 'Grootshad-X Nihilo Station', 'Half-Mile Island Subway Station', 'Happysmash Station', 'Hardware Store Subway Station', 'Haskell Curry Street Subway Station', 'Hippodrome Station', 'Holiday Beach Station', 'Hotel Shanielle Subway Station', 'Hühnerkopf Station (Trisiston)', 'INTERCAL Station', 'Ice Mountain Subway Station', 'Iceberg on Bamboo Station', 'Island Station', 'John Horton Conway Street Subway Station', 'Jungle Subway Station', 'KDW Station', 'Kangasvarkaan Rautatieasema', 'Kernighan & Ritchie Street Subway Station', 'Kindergarten', 'Knuth Avenue Subway Station', 'Koshahood Station', 'Krasnograd-FTNT Station', 'Lambda Bay Station', "Land's End (Planetarium) Station", "Land's End West Station", 'Large Beach', "Laza's City Subway Station", "Laza's Field Station", 'Leekston East Station', 'Leekston Ferry Station', 'Leekston Jungle Station', 'Leekston Station', 'Lesnoi Industrial Area Subway Station', 'Lesnoi North Station', 'Lesnoi South Station', 'Levenshtein Canyon Subway Station', 'Lighthouse Station', 'Lumpenproletariat Prairie Station', 'Lusin Street Station', 'Main Page', 'Manaugh Memorial Station', 'Mapgen Error Station (Personhood)', 'Marcuse Street Station', 'Market Subway Station', 'Marnack Mills Station', "Mary4's Mistake Station", 'Maxwell Street Subway Station', 'McFly Street Subway Station', 'Melinka Town Station', 'Memorial Mountain', 'Memory Station', 'Midway Cliff Station', 'MinerLand Subway Station', 'Minio Subway Station', 'Ministry of Transport Subway Station', 'Minkovsky Street Station', 'Mirzakhani Street Subway Station', 'Mom Junction', 'Montpellier Station', 'Morija Center Station', 'Morija South Station', 'Most! Station', 'Mountain Hotel Station (Personhood)', 'Mountain South Station', 'Mountain Valley Subway Station', 'Mountain View Subway Station', 'Musa Island Station', 'Mushroom Coast Station', 'Mushroom Hill Station (Personhood)', 'Mushroom Hills Station', 'Mushroom Land Station', 'NYE Square Subway Station', 'Namespace Mountains East Station', 'Neverbuild Old Terminus Station', 'Neverbuild Outskirts Station', 'Neverbuild Station', 'Neverbuild West Station', 'New Roses Gardens South Station', 'New Years Eve Square Station', 'No Idea', 'North Harbour Station', 'North Onionland Station', 'Northlands Interchange', 'OCP Showroom Subway Station', 'Ocean City Outskirts Station', 'Ocean City Station', "Och Noe's Lake", 'Old Cross Subway Station', 'Onionland Beach Station', 'Onionland Station', 'Onionland Subway Station', 'Orange Lake Subway Station', 'Origin Berton Street Station', 'Origin Sands Subway Station', 'Origin Subway Station', 'Outlet Store Station', 'PK Factory Station (Personhood)', 'Padrana Peninsula Station', 'Palm Bay Subway Station', 'Pancake Jungle Subway Station', 'Panda Reserve Station', 'Patch of Fire Station', 'Perelman Street Subway Station', 'Perl Prospect Station', 'Person Bridge Station (Personhood)', 'Personhood Main Station', 'Personhood South Station', 'Personhood Town Hall Station', 'Personhood West Station', 'Phawksden Station (Personhood)', 'Piet Station (Neverbuild)', 'Plantain Hills Station', 'Plantation Station', 'Poposchmerz Station', 'Populus Hills Station', 'Proletarian Station', 'Pyramid Station', 'Pythagoras Road Subway Station', 'Ramanujan Street Subway Station', 'Reactor Subway Station', 'Redwood Forest Subway Station', 'Redwood Island Station', 'Ritchie Memorial Station', 'Riverside Station', 'Robert Koch Boulevard Subway Station', 'Rockefeller Runway Subway Station', 'Roses Gardens East Station (Personhood)', 'Sakharov Street Subway Station', 'Sakura Gaps Station', 'Sakura Village Marina Station', 'Sakura Village Station', 'Sand Ora Station', 'Sandy Point Station', 'Schwarzschild Passing Track', 'Schwarzschild Street Station', "ScottishLion's City Subway Station", 'Shanielle City Center Subway Station', 'Shanielle City Subway Station', 'Shanielle Park Station', 'Shikatanaevo Station', 'Shoot Hills Station', 'Shore LTBAG Station', 'Shore Station', 'Silver Coast Central Station', 'Silver Coast North Station', 'Silver Coast South Station', 'Sinensis Plains Station', "Smacker's Land of Hope and Glory Subway Station", 'Smacker Station (Piet Rail)', 'Smith Street Subway Station', 'Snake Bend Subway Station', 'Snow Town Station', 'Snowland Subway Station', 'Snowy Peak Subway Station', "Someone's Crap Station", 'South Forest Station', 'Spawn Library Station', 'Spawn Main Station', 'Spawn Main Station (Subway)', 'Spawn Main Station (underground)', 'Spawn Station', 'Spawn Subway Station', "Sraczka2's Village Station", 'St-15-0 Station', 'Stallman Square Subway Station', 'Stallmangrad Main Station', 'Stone Beach Subway Station', 'Sulfur Hills Station', 'Swimming Rabbit Street Subway Station', "Szymon's Dam", 'Südkreuz Station (Personhood)', 'Tanh Cliffs Station', 'Testing Area 1 Subway Station', 'Testing Area 2 Subway Station', 'The Cube', 'The Cube Valley Station (Neverbuild)', 'The Road Station (Neverbuild)', 'Theodor Adorno Street Subway Station', 'Tom Lehrer Street Subway Station', 'Trap City Central Train Station', 'Treehouse Hotel Subway Station', 'Trisiston Station', 'Trojan Hills Station (Trisiston)', 'Trump Park Subway Station', 'University', 'V Tecta Union Station', 'Volcano Cliffs Subway Station', 'Warmoneaye Station', 'Water Pyramid Subway Station', 'Watson-Crick Street Subway Station', 'West Riverside Station', 'Windy Mountains Subway Station', 'Windy Mountains Valley 1 Subway Station', 'Windy Mountains Valley 2 Subway Station', 'Windy Mountains Valley 3 Subway Station', 'Wolf Rock Station', 'X Nihilo Main Station', 'X Nihilo Regional', 'Yoshi Island Subway Station', 'Zoo Subway Station'])  # noqa
    stations_list = list(set(stations_list))
    stations_list.sort()
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

# Use this where it is impossible/impractical to add transfer data to the wiki, and it therefore needs to be ignored
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
        if piece == "":
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


station_coordinates = {}

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
        if line.replace(" ", "").startswith("|coordinates="):  # parse mediawiki coordinates
            crds_line = line.replace(" ", "").removeprefix("|coordinates=").lower()
            if "{{co" in crds_line:
                crds_line = crds_line[crds_line.index("{{co"):crds_line.index("}}") + 2]

                crds_line = crds_line.removeprefix("{{co|").removesuffix("}}")

                coordinates = tuple(int(v) for v in crds_line.split("|")[:3])

                if len(coordinates) != 3:
                    raise Exception(f"Invalid coordinates: {coordinates}")
                station_coordinates[station_name] = coordinates

        if line.startswith("{{s-line"):
            '''if station_name == "Shore Station":
                wt = WParser.parse(wiki=lw_wiki, text=line)
                template = wt.templates[0]
                print(template)
                print(template.keys())
                print(template.values())'''
            # print(station_name)
            #            if "branch" in line or "type" in line:
            #                input(line)
            line_dict = s_line_to_dict(station_name, line)
            # print(line_dict)
            train_system = line_dict["system"]
            train_line = line_dict["line"]
            previous_station = line_dict.get("previous", None)
            next_station = line_dict.get("next", None)
            if next_station == "":
                next_station = None
            if previous_station == "":
                previous_station = None
            if train_system in ignored_systems:
                continue
            if previous_station == "???" or next_station == "???":
                continue
            part = StationPart(station_name, train_system, train_line,
                               previous_station, next_station,
                               transfer_station=line_dict.get("transfer", None),
                               oneway_prev=param_truthy(line_dict.get("oneway1", "false")),
                               oneway_next=param_truthy(line_dict.get("oneway2", "false"))
                               )
            part.branch = line_dict.get("branch", None)
            part.type = line_dict.get("type", None)
            part.type2 = line_dict.get("type2", None)
#            if part.type is not None or part.type2 is not None:
#                input(line+" "+str(part.branch))
            open_station_parts.append(part)
            if "transfer" in line_dict:
                print(f"\tTransfer from `{station_name}` to `{line_dict['transfer']}`")
            print(f"\t{station_name}: {line_dict}")
            print()

# print("SEARCH:", list(pwiki.gquery.GQuery.search(lw_wiki, '[[Category:Stations]]')))
all_systems: typing.Set[str] = set()
all_system_lines: typing.Set[typing.Tuple[str, str]] = set()
for station_part in open_station_parts:
    all_systems.add(station_part.system)
    all_system_lines.add((station_part.system, station_part.sub_line))

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
    "BPTL": {
        "#default": def_stat
    },
    "C&C Rail": {
        "#default": def_stat
    },
    "Cat-o-land Local Lines": {
        "Bamboo Hotel": "Bamboo Hotel Station (Cat-o-land)",
        "#default": def_stat
    },
    "DTL": {
        "Market": "Banana Place Market Station",
        "#default": "$ Station"
    },
    "Eden Ferries": {
        "Shanielle Inlet": "Shanielle Inlet Station",
        "#default": "$ Ferry Station"
    },
    "Express Lines": {
        "Spawn": "Spawn Main Station",
        "Origin": "Marcuse Street Station",
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
    "Origin Tram Lines": {
        "#default": "$ Station (Origin Tram Lines)"
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
    if name == "":
        raise Exception
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


def extract_name_from_terminus_page(terminus_page: str) -> str:
    if "<noinclude>" in terminus_page:
        return terminus_page.split("<noinclude>")[0].strip()
    else:
        return terminus_page.strip()


def get_stations_termini_for_system_lines(*system_line_names: tuple[str, str]) -> dict[tuple[str, str], dict[str, str]]:
    needs_downloading = []
    out: dict[tuple[str, str], dict[str, str]] = {}

    should_be_returned: dict[tuple[str, str], tuple[str, str]] = {}
    for system_name, line_name in system_line_names:
        file_path = f"cached_data/termini/{system_name.replace(' ', '_')}/{line_name.replace(' ', '_')}.json"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path) as file:
                out[(system_name, line_name)] = json.load(file)
        except FileNotFoundError:
            template_name_left = f"Template:S-line/{system_name} left/{line_name}"
            template_name_right = f"Template:S-line/{system_name} right/{line_name}"
            should_be_returned[(system_name, line_name)] = (template_name_left, template_name_right)
            print(f"Will download `{template_name_left}` and `{template_name_right}`")
            needs_downloading.append(template_name_left)
            needs_downloading.append(template_name_right)

    pages = pwiki.mquery.MQuery.page_text(lw_wiki, needs_downloading)
    print("\n\n")
    for system_name, line_name in should_be_returned:
        left_path, right_path = should_be_returned[(system_name, line_name)]
        left_page = pages[left_path]
        right_page = pages[right_path]

        left_name = extract_name_from_terminus_page(left_page)
        right_name = extract_name_from_terminus_page(right_page)

        out[(system_name, line_name)] = {}
        if left_name == "" and right_name == "":
            print(f"Both termini of `{system_name} {line_name}` are empty")
        if left_name != "":
            out[(system_name, line_name)]["left"] = fill_in_station_name(system_name, left_name)
        if right_name != "":
            out[(system_name, line_name)]["right"] = fill_in_station_name(system_name, right_name)
        file_path = f"cached_data/termini/{system_name.replace(' ', '_')}/{line_name.replace(' ', '_')}.json"
        print(f"Saving `{system_name} {line_name}` to `{file_path}`")
        with open(file_path, "w") as file:
            json.dump(out[(system_name, line_name)], file, indent=4)
    print()
    return out


if input("Get terminus data? (y/n) ") == "y":
    get_stations_termini_for_system_lines(*all_system_lines)

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

try:
    with open("cached_data/redirects.json") as f:
        redirects, no_redirect = json.load(f)
except FileNotFoundError:
    input("No cached_data/redirects.json found. Press [Enter] to continue...")
    redirects = {}
    no_redirect = []

redirects: dict[str, str]
no_redirect: list[str]

needed_redirects = []

if lw_wiki is not None:
    for link in all_links:
        if link.to_name not in redirects.keys() and link.to_name not in no_redirect:
            needed_redirects.append(link.to_name)
        if link.from_name not in redirects.keys() and link.from_name not in no_redirect:
            needed_redirects.append(link.from_name)

needed_redirects = list(set(needed_redirects))
print(f"Number of uncached redirect checks: {len(needed_redirects)}")
for needed_redirect in needed_redirects:
    print(f"Redirect not cached: {needed_redirect}, will request...")
for i, needed_redirect in enumerate(needed_redirects):
    print(f"Percent done: {i / len(needed_redirects) * 100:.2f}%", end="\n")
    new_title = lw_wiki.resolve_redirect(needed_redirect)
    if new_title != needed_redirect:
        redirects[needed_redirect] = new_title
    else:
        no_redirect.append(needed_redirect)

no_redirect = list(set(no_redirect))
with open("cached_data/redirects.json", "w") as f:
    json.dump([redirects, no_redirect], f, indent=4)

pre = len(all_links)
all_links = list(set(all_links))
post = len(all_links)
for link in all_links:
    if link.to_name in redirects.keys():
        link.to_name = redirects[link.to_name]
    if link.from_name in redirects.keys():
        link.from_name = redirects[link.from_name]
all_links = list(set(all_links))
post2 = len(all_links)
print(f"Number of links: {pre}")
print(f"Number of (deduplicated) links: {post}, difference: {pre - post}")
print(f"Number of (further deduplicated) links: {post2}, difference: {post - post2}")
print(f"Number of open stations: {len(stations_data) - len(closed_stations)}")

all_links.sort(key=lambda x: str(x))
print("Saving links...")
with open("saves/all_links.json", "w") as f:
    json.dump([v.save() for v in all_links], f, indent=4)

with open("saves/station_coordinates.json", "w") as f:
    json.dump(station_coordinates, f, indent=4)
print("Done.")
