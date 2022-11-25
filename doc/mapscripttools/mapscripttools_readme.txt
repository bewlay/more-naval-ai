MapScriptTools v1.06 Readme
====================================================================================================

Forum thread: http://forums.civfanatics.com/showthread.php?t=540261
Source code repository: https://bitbucket.org/Terkhen/mapscripttools-for-civilization-iv/
Issue tracker: https://bitbucket.org/Terkhen/mapscripttools-for-civilization-iv/issues

MapScriptTools provides tools to facilitate the creation of MapScripts and adapting existing ones
for Civilization IV Beyond the Sword. It helps on making MapScripts compatible for 'Normal',
'Fall from Heaven 2', 'Planetfall' and 'Mars Now!' mods. It is not intented to work with 'Final
Frontier' based mods.

It also includes a selection of MapScripts already adapted to make use of these features. All
included MapScripts can be used with the mods mentioned before, and they have a detailed changelog
in the initial part of each file that explains all changes and new features.

MapScriptTools was originally created by Temudjin. This new version has been made in order to
incorporate bugfixes and some new features to these excellent tools. The original version can be
found here: http://forums.civfanatics.com/showthread.php?t=371816


Installation
====================================================================================================

Put the files contained in the zip file in the root of the mod you want to use with MapScriptTools.
Assets should be merged with the mod's Assets folder, and PrivateMaps should be merged with the
mod's PrivateMaps folder. Bear in mind that if you are a player you should only use MapScriptTools
with supported mods.


MapScriptTools Features
====================================================================================================

MapScriptTools provides the tools to include the following features in existing MapScripts. All
included MapScripts also include these features.

- Easily adapt maps for Planetfall or Mars Now!

- Produce maps with special features for Fall from Heaven 2.

- Add Marsh terrain, if the mod supports it.

- Add Deep Ocean terrain, if the mod supports it.

- Make the map look prettier and more realistic.

- Add special regions to the map, such as big dents, big bogs, the lost isle or the elemental
  quarter. These region names are translatable.

- Replaced and expanded bonus balancer (from Warlords)

- Manipulate river creation: (starting from lakes, on islands...)

- Handle starting-positions for teams.

- Store used map options for future map generation.

- Print various sorts of maps to the log file for testing.

- Print stats about mod and map.

- Find the path for Civ4, Mod or Log files.

- Prevent triggering assertions when possible.


Included MapScripts
====================================================================================================

The following MapScripts have been modified to be supported by MapScriptTools. They also include
additional features, and can also be used as an example to adapt new maps to make use of
MapScriptTools' features.

Archipelago_mst by Bob Thomas (Sirian) (Civilization IV)
The ultimate water map for Civilization IV. Powerful navies not optional!

Earth3_mst by jkp1187 (http://forums.civfanatics.com/showthread.php?t=253927)
Derivative map generator that simulates a randomized Earth.

Erebus_mst by Cephalo (http://forums.civfanatics.com/showthread.php?t=261688)
Random map that creates a region of a fantasy type world where much of the world is unknown and
irrelevant. It allows terrain to be created on a smaller, more detailed scale than planetary maps.

FracturedWorld_mst by Temudjin (http://forums.civfanatics.com/showthread.php?t=371842)
Evolving plate tectonics map. When the eons come and go, the world slowly changes as the continents
drift and break apart, and new islands are created that may be driven into the continents.

Inland_Sea_mst by Bob Thomas (Sirian) (Civilization IV)
A large sea inhabits the center, surrounded by a thick ring of land.

Medium_and_Small_mst by Bob Thomas (Sirian) (Civilization IV)
Realistic world with highly random landmasses, medium and small. East and west hemispheres are
divided by ocean, although rarely an island chain may connect them.

Pangaea_mst by Bob Thomas (Sirian) (Civilization IV)
Pan-Gaia: "One Earth," a massive single continent.

PerfectWorld_mst by Cephalo (http://forums.civfanatics.com/showthread.php?t=310891)
Random map that simulates earth-like plate tectonics, geostrophic and monsoon winds and rainfall.

Planetfall_mst by Maniac (http://forums.civfanatics.com/showthread.php?t=252829)
Creates few landmasses with many hilly regions and mountain ranges. Small islands surround them.

RandomMap_mst by Terkhen (https://bitbucket.org/Terkhen/mapscripttools-for-civilization-iv)
MapScript which allows to randomly select a map script between Earth3, Erebus, Fractured World,
Inland Sea, Medium and Small, PlanetFall, Sea Highlands and Tectonics.

Ringworld3_mst by Temudjin (http://forums.civfanatics.com/showthread.php?t=371831)
Random map based on Larry Niven's famous 'Ringworld' novel. It creates a thin (16 tiles wide) but
long map with artificial landmasses and climate.

Sea_Highlands_mst by Bob Thomas (Sirian) (Civilization IV)
Highlands, valleys and mountain ranges with several bigger lakes.

SmartMap_mst by surt (http://forums.civfanatics.com/showthread.php?t=154989)
This highly customizable map script can create an incredible assortment of gameplay experiences.

Tectonics_mst by Laurent Di Cesare (http://forums.civfanatics.com/showthread.php?t=149278)
Produces mountain ranges, and simulates plate tectonics, giving more realistic/earthlike terrain
(mountain ranges, mountains near coasts like the Andes, or between subcontinents like the Himalaia).


MapScript features
====================================================================================================

When using mods based on Fall from Heaven 2, all maps will generate a small number of city ruins along with some roads.

All maps will store used map options, and restore them the next time they are loaded.

All maps can (and will) produce Marsh terrain, if the mod supports it.

All maps can (and will) produce Deep Ocean terrain, if the mod supports it.

Supported maps look prettier and more realistic.

All maps support any number of map sizes supported by the mod.

All maps support the expanded coastal water option.

All maps may add big dents, a special mountainous map region.

All maps may add big bogs, a special map region consisting on a great swamp that may also contain a
lake. This region is not used in Mars Now! maps.

All maps may add the lost isle, a small and isolated island with city ruins, roads and perhaps some
intact improvements. Other goodies may also appear.

When using mods based on Fall from Heaven 2, all maps may add the Elemental Quarter, the place
where elemental mana nodes meet.

Most maps give random names to their Special Regions. These names can be translated.

All maps may add map features such as Kelp, Haunted Lands or Crystal Plains, if supported by the mod
being used.

All maps may add Map Features ( Kelp, HauntedLands, CrystalPlains ), if supported by mod (FFH only).

All maps may add some rivers on small islands and from lakes.

All maps support Mars Theme options, if 'Mars Now!' is the active mod.

All maps support Team Start options (neighbours, separated, random). This option does not appear
when using 'Mars Now!'.

All maps support any number of players, depending on the mod.

All maps produce printed maps in "My Documents\My Games\Beyond the Sword\Logs\PythonDbg.log"

All maps produce printed statistics in "My Documents\My Games\Beyond the Sword\Logs\PythonDbg.log"

If 'Planetfall' is the active mod, usually the planetfall-default starting plot finder will be used.

If 'Mars Now!' is the active mod, oceans and lakes are converted to desert (Sands of Mars), except
if Terraformed Mars is choosen in the Mars Theme options.

All maps allow to use balanced resources, add missing boni and try to move some minerals to nearby
hills.


MapScriptTools Credits
====================================================================================================

Temudjin: Creation of MapScriptTools.

Terkhen: Tweaks, improvements, fixes.


MapScript Credits
====================================================================================================

Archipelago: Bob Thomas (Sirian), Terkhen (MapScriptTools adaptation, improvements, fixes)

Earth3: Bob Thomas (Sirian) (Terra), GRM7584 (Earth2), jkp1187 (Terra3), Temudjin (Earth3, MapScriptTools
adaptation, improvements, fixes), Terkhen (improvements, fixes).

Erebus: Cephalo, Temudjin (MapScriptTools adaptation, improvements, fixes), Terkhen (improvements,
fixes).

FracturedWorld: Temudjin, Terkhen (improvements and fixes)

Inland_Sea: Bob Thomas (Sirian), Soren Johnson, Andy Szybalski, Temudjin (MapScriptTools adaptation,
improvements, fixes), Terkhen (improvements, fixes).

Medium_and_Small: Bob Thomas (Sirian), Temudjin (MapScriptTools adaptation, improvements, fixes), Terkhen
(improvements, fixes).

Pangaea: Bob Thomas (Sirian), Soren Johnson, Andy Szybalski, Terkhen (MapScriptTools adaptation, improvements, fixes)

PerfectWorld2: Cephalo, Temudjin (MapScriptTools adaptation, improvements, fixes), Terkhen
(improvements, fixes).

PlanetFall: Maniac, Oleg Giwodiorow / Refar, Temudjin (MapScriptTools adaptation, improvements,
fixes), Terkhen (improvements, fixes).

RandomMap: Terkhen (based on Sansimap by sansi)

Ringworld3: Ruff_Hi (Ringworld2), Temudjin (Ringworld3, MapScriptTools adaptation, improvements,
fixes), Terkhen (improvements, fixes).

Sea_Highlands: Bob Thomas (Sirian), vbraun, Temudjin (MapScriptTools adaptation, improvements, fixes), Terkhen
(improvements, fixes).

SmartMap: Doug McCreary, Keldath, Mrgenie, TAfirehawk, Temudjin (MapScriptTools adaptation,
improvements, fixes), Terkhen (fixes).

Tectonics: LDiCesare, Temudjin (MapScriptTools adaptation, improvements, fixes), Terkhen
(improvements, fixes).