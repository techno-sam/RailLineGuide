local dsformat = "[[%1 Station|%1]]"
local atlformat = "[[%1 Station (ATL)|%1]]"
local phformat = "[[%1 Station (Personhood)|%1]]"
local hlformat = "[[%1|%1]]"

local p = {
  ["system title"] = "[[Arse Train Lines]]",
  ["system icon"] = "",
  ["station format"] = {dsformat, --default
    ["East Origin"] = atlformat,
    ["Südkreuz"] = phformat,
  },
}

p.lines = {
  ["_default"] = {
    title = "[[Arse Train Lines]]",
    color = "000000",
    ["left terminus"] = "",
    ["right terminus"] = "",
    route = { -- Used for special (unlisted) places
      ["Closed"] = {"Silver Coast East", "Südkreuz"},
      ["Demolished"] = {"Someone's Crap"},
    },
  },
  ["Blue Marble"] = {
    title = "[[ATL Blue Marble Line]]",
    ["short name"] = "ATL-Bm",
    ["icon format"] = "croute",
    color = "87ceeb",
    route = {
      [true] = {"Crossroads City Hall", "New Crossroads Terminal"}
    },
  },
  Bronze = {
    title = "[[ATL Bronze Line]]",
    ["short name"] = "ATL-B",
    ["icon format"] = "xroute",
    color = "a52a2a",
    route = {
      [true] = {"Crossroads City Hall", "Silver Coast South", "Silver Coast Central", "Silver Coast North", "Colored Grasses", "The Cube", "Grassy Scarp", "Personhood West"},
      ["Express"] = {"Crossroads City Hall", "Silver Coast Central", "Colored Grasses", "The Cube", "Personhood West"},
    },
  },
  Gold = {
    title = "[[ATL Gold Line]]",
    ["short name"] = "ATL-G",
    ["icon format"] = "croute",
    color = "ffd700",
    route = {
      [true] = {"Neverbuild Central", "Neverbuild Old Terminus", "Mushroom Land", "Neverbuild Outskirts", "Ocean City Outskirts", "Ocean City"},
    },
  },
  Mithril = {
    title = "[[ATL Mithril Line]]",
    ["short name"] = "ATL-M",
    ["icon format"] = "xroute",
    color = "0000cd",
    route = {
      [true] = {"Ehlodex", "Silver Coast Central"},
    },
  },
  Zinc = {
    title = "[[ATL Zinc Line]]",
    ["short name"] = "ATL-Z",
    ["icon format"] = "croute",
    color = "48d1cc",
    route = {
      [true] = {"Berton Street", "East Origin", {"New Years Eve Square", note="(30 December - 2 January)"}, "Leekston", "Leekston Jungle", "EVO", "Silver Coast South", "Silver Coast Central", "Silver Coast North", "Ocean City", "Greener Pastures", "Erstaziland-Salt Factory", "Château d'Erstazi"},
    },
  }
}

return p