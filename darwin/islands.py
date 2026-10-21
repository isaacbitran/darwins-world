"""The seven islands. `env` is the Jev state; `season` names the harsh season; xy/r place the island on the map."""

ISLANDS = [
 {"key": "tundra", "name": "Frostholm", "color": "#9fd8ff", "xy": [0.50, 0.15], "r": 0.11,
  "env": "Frostholm, a frozen tundra island near the pole. Winter lasts nine months at -40 C with blizzards and deep snow. "
         "The ground is permafrost. The only plants are moss, lichen and low shrubs. Lemmings live under the snow, and the "
         "coast has fish and seals under the sea ice. There are almost no trees.",
  "season": "the nine-month polar winter at -40 C"},
 {"key": "ocean", "name": "The Shelf", "color": "#3f8cff", "xy": [0.83, 0.32], "r": 0.12,
  "env": "The Shelf, a deep ocean shelf with no dry land at all: only open cold sea water, kelp forests, and the dark sea floor. "
         "There are schools of fish, plankton, crabs and squid. Anything that cannot swim and breathe at sea drowns.",
  "season": "the winter storm season with huge waves and freezing water"},
 {"key": "rainforest", "name": "Verdance", "color": "#4be38a", "xy": [0.80, 0.72], "r": 0.11,
  "env": "Verdance, a hot, humid rainforest island. Giant trees form a canopy 50 meters up where most fruit, flowers and insects are. "
         "The forest floor is dark, wet and muddy. It rains every day. There are many snakes, birds and big cats.",
  "season": "the monsoon, with months of flooding rain"},
 {"key": "grassland", "name": "Sedge Plains", "color": "#e8d36a", "xy": [0.50, 0.86], "r": 0.12,
  "env": "Sedge Plains, a wide open grassland savanna with very few trees and nowhere to hide. Grass and seeds are everywhere. "
         "Fast predators chase grazing herds across the open ground. Wildfires sweep the grass in the dry season.",
  "season": "the dry season with grass fires"},
 {"key": "desert", "name": "Ashara", "color": "#ff9a4d", "xy": [0.19, 0.72], "r": 0.11,
  "env": "Ashara, a scorching sand desert island. Daytime is 50 C with no shade, nights are cold. It rains once every few years "
         "and there is no standing water. Plants are only cactus, dry seeds and thorny scrub. Insects and lizards hide in the sand.",
  "season": "a two-year drought with no rain at all"},
 {"key": "volcanic", "name": "Cinder", "color": "#ff5468", "xy": [0.17, 0.32], "r": 0.10,
  "env": "Cinder, an active volcanic island of black lava rock. Hot vents release toxic gas, the ground is hot enough to burn feet, "
         "and ash falls often. Almost nothing grows except bacteria mats around hot springs and a few hardy ferns. "
         "Insects and seabirds visit the coast.",
  "season": "an eruption that buries the island in ash"},
 {"key": "cave", "name": "Hollowdeep", "color": "#b48cff", "xy": [0.50, 0.50], "r": 0.10,
  "env": "Hollowdeep, a huge cave system with no light at all. It is always pitch dark, cool and damp, with underground rivers and narrow "
         "tunnels. Food is fungus, cave insects, blind fish and bat droppings. Eyes are useless here.",
  "season": "a lean year when the bat colony leaves and food runs out"},
]
KEYS = [i["key"] for i in ISLANDS]
# migration neighbors (rare boats of driftwood / storms)
NEIGHBORS = {"tundra": ["ocean", "volcanic", "cave"], "ocean": ["tundra", "rainforest", "cave"],
             "rainforest": ["ocean", "grassland", "cave"], "grassland": ["rainforest", "desert", "cave"],
             "desert": ["grassland", "volcanic", "cave"], "volcanic": ["desert", "tundra", "cave"],
             "cave": ["tundra", "ocean", "rainforest", "grassland", "desert", "volcanic"]}
