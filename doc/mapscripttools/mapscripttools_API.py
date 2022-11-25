'''
MapScriptTools Manual and API  Ver.: 1.06
=========================================

Introduction:
-------------
If you're a modder working (or playing!) with map-scripts, this is for you!

The tools in MapScriptTools allow you to:
 1) Transform any map-script into one suitable for 'Fall from Heaven', 'Planetfall' or 'Mars Now!'.
    1a) Use a template that for most mapscripts has to be only moderately adjusted.
 2) Introduce new terrains into any map-script.
    2a) Put Marsh Terrain on the map, if the mod supports it.
    2b) Put Deep Ocean Terrain on the map, if the mod supports it.
 3) Create odd regions on the map:
    3a) 'The Big Bog', a flat, marshy, somewhat round region, probably with a lake and some rivers within it.
    3b) 'The Big Dent', a mountainous, somewhat oval region, probably with a volcano and several
        rivers flowing from it.
    3c) 'Elemental Quarter', the place where elemental mana nodes meet. Earth, Water, Air and Fire nodes
        influence the quarter of featureless terrain behind them. (For FFH only)
    3d) The lost 'Isle Of Atlantis' / 'Numenor Island', a small, isolated island with city-ruins, roads,
        and perhaps some intact improvements. If allowed by the mod, some other goodies may also appear.
    3z) Name region in Planetfall: 'The Great Dunes'.
 4) Put mod-dependent features on the map:
    4a) Kelp on coastal plots
    4b) Haunted Lands in deep forest, deep desert, within and around marshes, near ruins and mountain passes.
    4c) Crystal Plains on snowy flatland plots.
 5) Greatly expand upon the BonusBalancer class from Warlords in CyMapGeneratorUtil.py.
    Allows for mod-specific bonus-lists (currenty only Civ and FFH, but you can supply your own).
    5a) Gives each player a fair chance to find the neccessary resources within a reasonable radius.
        If that radius overlaps with your neighbors, you may have to fight over that resource anyway.
    5b) Places missing boni (those boni which should have been but for some reason weren't placed by addBonus()).
    5c) Moves some minerals [Copper,Iron,Mithril,Uranium,Silver] placed on flatlands to nearby hills.
        Create those hills if necessary and wanted.
 6) Place rivers on the map.
    6a) Enable building rivers starting at the sea and moving upriver.
    6b) Put a river (or two) on smaller islands.
    6c) Automatically start river(s) from lake(s).
    6d) Produce river-lists. Print their coordinates. (As yet only of those rivers created by buildRiver())
 7) Allow teams to have nearby, separated or random starting-plots.
 8) Print maps to the Python log at "...\My Documents\My Games\Beyond the Sword\Logs\PythonDbg.log":
    8a) Area-Maps
    8b) Plot-Maps
    8c) Terrain-Maps (Normal and Planetfall) - allow user supplied list of terrain.
    8d) Feature-Maps (Normal and Planetfall) - allow user supplied list of features.
    8e) Bonus-Maps (Normal and Planetfall) - allow user supplied list of boni.
x   8f) Improvement-Maps (Normal and Planetfall) - allow user supplied list of improvements.
    8g) River-Maps (plots,river-flows and starting-plots)
    8h) Difference-Maps of an earlier map and the actual map can be produced to
        document the different stages of map building.
 9) Print stats of map and mod to the Python log at "...\My Documents\My Games\Beyond the Sword\Logs\PythonDbg.log".
10) Prettify maps:
   10a) Connect small lakes.
   10b) Connect small islands.
   10c) Connect small terrain patches.
   10d) Remove ice from edge of map.
   10e) Adjust plot / terrain frequency to given percentage.
   10f) Reduce peaks and volcanos for graphical beautification.
   10g) Expand coastal waters
11) Find the path for Civ4, Mod or Log files
12) Groups of single funtion helpers:
   12a) Deal with areas.
   12b) Deal with (cardinal) directions.
   12c) Choose randomly - don't deal with dices anymore.
   12d) Convert between plot, index and coordinates.
   12e) Check numbers of neighbor plot-types, terrains, features.
x  12f) Validate and assign starting-plots
   12z) A whole lot of other goodies.
-----
x  Not implemented yet.


Installation:
-------------
Put the file MapScriptTools.py into the ...\Beyond the Sword\Assets\Python folder. (NOT CustomAssets!)
If you don't mind to see it as an option in the map selection of 'Custom Game', you can put it
into the ...\Beyond the Sword\PublicMaps folder, but that's the second best solution, as it won't work
if the mod disallows public maps in its ini-file (it may have other quirks - this isn't well tested).
'Planetfall' uses the PrivateMaps folder, here you whould either have to put it into the Python
folder, or change the ini-file to allow 'Planetfall' to use the PublicMaps folder.


Compatibility:
--------------
The 'MapScriptTools' are compatible with BtS 3.19.
I've run a short test with Warlords 2.13 and that worked fine too.
The above statements seem to imply compatibility to BtS 3.13 / 3.17, but this isn't tested.


Import MapScriptTools:
----------------------
Before using the MapScriptTools (MST), they have to be imported by the script.
Use 'import MapScriptTools as mst' somewhere at the beginning of your file.


Output:
-------
All reports go to the Python log normally at "...\My Documents\My Games\Beyond the Sword\Logs\PythonDbg.log".
You may have to enable logging by making sure the following option is set to 1 in
"...\My Documents\My Games\Beyond the Sword\civilization.ini":

; Enable the logging system
LoggingEnabled = 1


Initialization:
---------------
To use most of the goodies within the MapScriptTools, they have to be initialized.
The getModInfo() function is used for this purpose. It should be the first
MST function executed. Putting 'mst.getModInfo()' first into
beforeGeneration() seems like a good idea. Actually the function has optional
parameters which you probably want to use.


Functions:
----------

getModInfo( mapVersion=None, defLatitude=None, sMapInfo=None, bNoSigns=False )
..............................................................................
  Function: Initialize MapScriptTools and print basic map parameters to the log. Identify mod if possible.

  Parameter: mapVersion    string or None   Version of map-script
                                            default: None - version will not be printed.
             defLatitude   string or None   String to be evaluated by evalLatitude(). The string-function can
                                              only see x and y as variables and should return the latitude of
                                              a plot at coordinates x,y as a value between 0 .. 90.
                                            default: None - noPolesGetLatitude(x,y) will be used as default
             sMapInfo      string or None   String to be printed into the log with infos about the
                                              selected map parameters.
                                            default: None - no info will be printed
             bNoSigns      bool             Suppress names for special map-regions
                                            default: False - use signs for regions
  Return: -


evalLatitude( plot, bDegrees=True )
...................................
  Function: Evaluate defLatitude given in getModInfo(), to give the latitude for any plot.
            ( MapScriptTools doesn't know how latitudes are calculated in each different map-script.
              This is the mechanism to enable the internal functions to get the latitude for their
              climate calculations. )

  Parameter: plot       plot   Plot on the map for which the latitude is sought.
             bDegrees   bool   If True the result will be an integer between 0 .. 90,
                               else the result will be floating-point beween 0.0 .. 1.0, equator is zero.
  Return: Latitude of plot in the form indicated by bDegrees.


Instantiated Classes:
---------------------

class CivFolders:
instance: civFolders
.............................
Find out where the files are.
.............................
getModPaths()             Example:
--- vars ---              --------
civFolders.appName        Beyond the Sword
civFolders.userDir        ....\My Documents\My Games
civFolders.rootDir        ....\My Documents\My Games\Beyond the Sword
civFolders.logDir         ....\My Documents\My Games\Beyond the Sword\Logs
civFolders.appDir         ..\Civilization 4\Beyond the Sword
civFolders.modName        MyMod
civFolders.modFolder      Mods\MyMod
civFolders.modDir         ..\Civilization 4\Beyond the Sword\Mods\MyMod


class DeepOcean:
instance: deepOcean
.......................................................
put 'Deep Ocean' terrain into the middle of the oceans.
.......................................................
buildDeepOcean( dist=3, chDeep=80 )


class PlanetFallMap:
instance: planetFallMap
........................................................
All that's needed to change maps into 'Planetfall' maps.
........................................................
buildPfallOcean()
pFallTerrain = mapPfallTerrain( eTerrain, terList, plot, terrainGen=None )
data = buildPfallHighlands( iBaseChance=None, data=None )


class MapPrettifier:
instance: mapPrettifier
......................................
Something to make maps look beautiful.
......................................
connectifyLakes( chConnect=75 )
deIcifyEdges( iLat=66 )
hillifyCoast( chHills=50 )
expandifyCoast( ch=15, passes=4 )
beautifyVolcanos( chHills=66 )
lumpifyTerrain( targetTerrain, sourceTer1, sourceTer2=None )
lumpifyFeature( targetFeature, sourceFeat1, sourceFeat2=None, passes=1 )
bulkifyIslands( chConnect=66, maxIsle=4 )
percentifyTerrain( targetTerTuple, *sourceTerTuples )
percentifyPlots( targetPlotType, fTargetPlotPercent, data=None, terGenerator=None )


class MarshMaker:
instance: marshMaker
.....................................................
If the mod allows marsh-terrain, it can be made here.
.....................................................
bModHasMarsh = initialize( iGrassChance=5, iTundraChance=10, tMarshHotRange=(0,18), tMarshColdRange=(45,63) )
convertTerrain( tAreaRange=None, areaID=None )
iArid = getAridity()
normalizeMarshes()


class MapRegions:
instance: mapRegions
.................................................................
Some regions on the map can be distinctive (and may have a name).
Notes: Elemental Quarter only on magic worlds.
		 Lost Isles on alien planets are allways hightech.
.................................................................
initialize( regDist=15, noSigns=False )
buildLostIsle( chance=33, minDist=7, bAliens=False )
centerPlot = theLostIsle( pCenterPlot, pList, bAliens )
buildBigBogs( iBogs=None, chDent=66 )
namePlot = theBigBog( pCenterPlot, bBigBog=True, bBogLake=True )
buildBigDents( iDents=None, chDent=66 )
namePlot = theBigDent( pCenterPlot, bSideways=None, chAccess=66 )
buildElementalQuarter( chEQ=66 )
namePlot = theElementalQuarter( pCenterPlot, temp )
addRegionExtras()
bValid = regionCheck( plot, regionDistance=None )
--- vars ---
mapRegions.noSigns        a toggle to determine if landmark signs should show
mapRegions.regionList     a list of coordinates for the different regions,
                          one [x,y] per region.


class FeaturePlacer:
instance: featurePlacer
..................................................
Put some common mod-dependent features on the map.
..................................................
placeFeatures()
placeReefs( chReef=3, chExpand=20, maxLatitude=None )
placeScrub( chScrub=10 )
placeKelp( chKelp=20, bAll=False, bLakes=False )
placeHauntedLands( chHaunted=6 )
placeCrystalPlains( chCrystal=20 )


class BonusBalancer:
instance: bonusBalancer
.........................................................................................
Deal with resources. Balance them and make sure all are on the map and where they belong.
.........................................................................................
initialize( bBalanceOnOff=True, bMissingOnOff=True, bMineralsOnOff=True, bWideRange=False )
normalizeAddExtras( *lResources )
bSkip = isSkipBonus( iBonusType )
bValid = isBonusValid( eBonus, pPlot, bIgnoreUniqueRange, bIgnoreOneArea, bIgnoreAdjacent )
addMissingBoni()
moveMinerals( lMineralsToMove=None )


class RiverMaker:
instance: riverMaker
.............................................................................................
Build rivers coming either down from the mountains or up from the sea. Put rivers on islands.
.............................................................................................
buildRiver( pStartPlot, bDownFlow=True, ecNext=None, ecOri=None, iThisRiverID=None, riverList=None )
islandRivers( minIsle=6, maxIsle=50, areaID=None )
buildRiversFromLake( lakeAreaID=None, chRiver=66, nRivers=1, minLake=1 )
sList = outRiverList( riverList )
bEdge = isEdgeDirection( self, plot, ecDir )
bRiver =  hasRiverAtPlot( plot )
bCorner = hasRiverAtSECorner( plot )
bCorner = hasCoastAtSECorner( plot )
bCorner = hasPlotTypeAtSECorner( plot, plotType )
eCard = getBestFlowDir( plot, bDownFlow=True, bShort=False, eForbiddenList=[] )


class TeamStart:
instance: teamStart
.........................................................
Put starting-plots of team members together or separated.
.........................................................
placeTeamsTogether( bTogether=False, bSeparated=False )
bTeams = getTeams()


class MapPrint:
instance: mapPrint
.................................
Have a look at what you've built.
.................................
initialize()
definePrintMap( lines, charsPerPlot, linesPerPlot, mapTitle="", region=None, offset=None, mapLegend="" )
printMap( diffDict=None )
bSuccess = buildDiffMap( newDict, oldDict )
buildAreaMap( bDiffDict=False, sTitle=None, region=None, areaID=None, areaDict=None )
buildPlotMap( bDiffDict=False, sTitle=None, region=None, data=None )
buildTerrainMap( bDiffDict=False, sTitle=None, region=None, terrainDict=None, showPlots=False )
buildFeatureMap( bDiffDict=False, sTitle=None, region=None, featureDict=None, showPlots=False )
buildBonusMap( bDiffDict=False, sTitle=None, region=None, bonusDict=None, showPlots=False )
buildRiverMap( bDiffDict=False, sTitle=None, region=None )


class MapStats:
instance: mapStats
...............................
Don't you just love statistics?
...............................
mapStatistics( bFullVersion=True )
tPlotStats = statPlotCount( txt=None, data=None )
showContinents( txt=None, minPlots=3, bWater=False )
sTechs = getTechList( prefix = "", bTechLevels=True )
listPlayers = getCivPlayerList()
sprint = sprintActiveCivs( showTeams=False, showTraits=False, showHumans=False )


class RandomList:
instance: randomList
.......................................
Just little helpers to randomize lists.
.......................................
newlist = xshuffle( oriList )
shuffle( oriList )
countList = randomList.randomCountList( count )


Uninstantiated Classes:
-----------------------

class MST_TerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
................................................................
Make sure the right latitudes are used when generating terrain.
................................................................
lat = getLatitudeAtPlot( iX, iY )


class MST_TerrainGenerator_Mars(MST_TerrainGenerator):
......................................................
Generate terrain for 'Mars Now!'.
......................................................
terrainVal = generateTerrainAtPlot( iX, iY ):


class MST_FeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
................................................................
Make sure the right latitudes are used when generating features.
................................................................
lat = getLatitudeAtPlot( iX, iY )


Useful Functions:
-----------------
There are quite a few little 'helper' files near the top of this file,
which may well be usefull to you. If you used 'import MapScriptTools as mst',
you can use them all by putting 'mst.' before the call.
Have a look and feel free to do with them what you want.


Useful Constants:
-----------------
mst.bPfall   True,False
             indicates if this mod is 'Planetfall' or a modmod
             ( checks for BONUS_FUNGICIDE )

mst.bPfall_Scattered   True,False - ONLY for Planetfall
             indicates if mod-option 'Scarrered Landing Pods' is active

mst.bMars    True,False
             indicates if this mod is 'Mars Now!' or a modmod
             ( checks for 'Mars, Now!' in pedia )

mst.bSandsOfMars   True,False - default is False, except on Mars where the default if True.
             indicates if 'Sands of Mars' theme is used, where open water is converted to desert.

mst.bFFH     True,False
             indicates if this mod is 'Fall From Heaven 2' or a modmod
             ( checks for BONUS_MANA )

mst.bFFront  True,False
             indicates if this mod is 'Final Frontier' or a modmod
             ( checks for FEATURE_SOLAR_SYSTEM )

mst.bPatch   True,False
             indicates if the 'CvGameCoreDLL.dll' of this mod incorporates the 'Unofficial Patch'
             ( checks results of plot.getLatitude() )

mst.bRev     True,False
             indicates if this mod is or incorporates the RevolutionDCM-Mod

mst.bBUG     True,False
             indicates if this mod is or incorporates the BUG-Mod

mst.bBBAI    True,False
             indicates if this mod is or incorporates the BBAI-Mod

mst.bAIAuto  True,False
             indicates if this mod incorporates 'AI AutoPlay'

Notes:
------
These tools are for the english version.
Several tests depend on text found in various xml-files. To be more precise:
The english text! Of the checks mentioned that would be bBUG, bBBAI and bAIAuto
together with most other mod-recognition checks.
Any failure of the tests will probably just affect the stats though.

Python 2.4 doesn't really have much of a concept for private data. The
class methods below the ---private--- line are as readily accessible as
the others, but they are not part of the API and thus subject to change
without notice.
( Just like anything else really - I'm giving no guarantees, but I might think twice.)


Included Mapscripts:
--------------------
To use the MapScriptTools with existing mapscripts, just put the included template-script
into them and modify as needed. To demonstarte how it is done I've included several altered
mapscripts. Some mapscripts required additional changes - sorry, but it's not quite automated (yet)
and you still need some understanding of what you are doing.

All maps can be used with 'Fall from Heaven', 'Planetfall' or 'Mars Now!'.
All maps can (and will) produce Marsh terrain, if the mod supports it.
All maps can (and will) produce Deep Ocean terrain, if the mod supports it.
All maps allow for at least two more map sizes beyond 'Huge', if the mod supports them
All maps may add Map Regions ( BigDent, BigBog (not Mars), ElementalQuarter (FFH only), LostIsle ).
All maps may add Map Features ( Reef, Scrub, Kelp, HauntedLands, CrystalPlains ), if supported by mod.
All maps add some rivers on small islands and from lakes
All maps support Coastal Waters options. (Allow expanded coast like Civ5)
All maps support Team Start options. (Choose to find your teammate either near or far)
All maps support Mars Theme options, if 'Mars Now!' is the active mod.
All maps support any number of players, depending on the mod.
All maps produce printed maps in "...\My Documents\My Games\Beyond the Sword\Logs\PythonDbg.log"
All maps produce printed statistics in "...\My Documents\My Games\Beyond the Sword\Logs\PythonDbg.log"
If 'Planetfall' is the active mod, usually the planetfall-default starting plot finder will be used.
If 'Mars Now!' is the active mod, the Team Start option will be suppressed.
If 'Mars Now!' is the active mod, oceans and lakes are converted to desert (Sands of Mars),
   except if Terraformed Mars is choosen in the Mars Theme options.
Most maps use balanced resources, add missing boni and try to move some minerals to nearby hills.
Most maps give names to their Special Regions.

There is a detailed description of all included MapScripts in the readme file. Each MapScript also
includes a changelog which lists all changes made to it.

****************************************************************************************************
**  Thanks:                                                                                       **
**  -------                                                                                       **
**  I've looked into a lot of map-scripts and mod-code and learned much from the authors. I also  **
**  stole ideas and sometimes even parts of code, which I found useful. I'm sorry to say that     **
**  I don't remember all of my sources - my apologies and thank you all for your efforts.         **
**  Specifically I'd like to thank:                                                               **
**                                                                                                **
**  Ruff_Hi                                                                                       **
**   - Your 'Ring World' induced me into a deeper investigation of maps.                          **
**                                                                                                **
**  The CivFanatics Community                                                                     **
**   - For making all those wonderful maps and mods and                                           **
**     for providing the opportunity to have a look at how it's done.                             **
**                                                                                                **
**  The Civ4 Design Team                                                                          **
**   - By opening your game-engine, you really opend the world(s).                                **
****************************************************************************************************


For Reference:
----------------------------------------------------------------
The Map Building Process according to Temudjin
    --> also see Bob Thomas in "CvMapScriptInterface.py"
    (in ..\Assets\Python\EntryPoints)
----------------------------------------------------------------
0)     - Get Map-Options
0.1)     getNumHiddenCustomMapOptions()
0.2)     getNumCustomMapOptions()
0.3)     getCustomMapOptionDefault()
0.4)     isAdvancedMap()
0.5)     getCustomMapOptionName()
0.6)     getNumCustomMapOptionValues()
0.7)     isRandomCustomMapOption()
0.8)     getCustomMapOptionDescAt()
0.9)     - Get Map-Types
0.9.1)     isClimateMap()
0.9.2)     isSeaLevelMap()
1)     beforeInit()
2)     - Initialize Map
2.1)     getGridSize()
2.2.1)   getTopLatitude()					# always use both
2.2.2)   getBottomLatitude()				# always use both
2.3.1)   getWrapX()							# always use both
2.3.2)   getWrapY()							# always use both
3)     beforeGeneration()
4)     - Generate Map
4.1)     generatePlotTypes()
4.2)     generateTerrainTypes()
4.3)     addRivers()
4.4)     addLakes()
4.5)     addFeatures()
4.6)     addBonuses()
4.6.1)     isBonusIgnoreLatitude()*
4.7)     addGoodies()
5)     afterGeneration()
6)     - Select Starting-Plots
6.1)     minStartingDistanceModifier()
6.2)     assignStartingPlots()
7)     - Normalize Starting-Plots
7.1)     normalizeStartingPlotLocations()
7.2)     normalizeAddRiver()
7.3)     normalizeRemovePeaks()
7.4)     normalizeAddLakes()
7.5)     normalizeRemoveBadFeatures()
7.6)     normalizeRemoveBadTerrain()
7.7)     normalizeAddFoodBonuses()
7.7.1)     isBonusIgnoreLatitude()*
7.8)     normalizeGoodTerrain()
7.9)     normalizeAddExtras()
7.9.1)     isBonusIgnoreLatitude()*
8 )    startHumansOnSameTile()

* used by default 'CyPythonMgr().allowDefaultImpl()' in:
  addBonuses(), normalizeAddFoodBonuses(), normalizeAddExtras()
------------------------------------------------------------------


##################################################################################
## How To Guide to transform a 'normal' map-script for MapScriptTools
##################################################################################
 - Make sure MapScriptTools.py is in the appropiate ...\Assets\Python folder:
      '..\Beyond the Sword\Assets\Python' seems to be best as you need it only once.
 - Put the following 'MapScriptTools Interface Template' into your map-script after the import statements.
 - Comment-out / delete what you don't want.
 - Make the necessary adjustments.
 - For Planetfall and Mars use CyPythonMgr().allowDefaultImpl() for the default starting-plot finder.
 - For Planetfall and Mars use mst.MST_FeatureGenerator() to generate features
 - For Planetfall use mst.MST_TerrainGenerator() to generate terrain.
 - For Mars use mst.MST_TerrainGenerator_Mars() to generate terrain.
 - Use the bMars and bPfall globals to distinguish the above.
 - Have a care where (or if at all) you place the CyPythonMgr().allowDefaultImpl() statements.
      In assignStartingPlots(): CyPythonMgr().allowDefaultImpl() must be the last statement executed!
 - Check for normalize...() functions in the map-script. Use those as a guideline
      for which normalizations to allow or not.
 - Some map-scripts use the Warlords bonus balancer
      Delete the lines:
         from CvMapGeneratorUtil import BonusBalancer
         balancer = BonusBalancer()
      The balancer is then used within normalizeAddExtras() and addBonusType(). If that's the only
         thing that's done in these functions, just delete them too.
      You may also adjust the mst.bonusBalancer call at the end of beforeGeneration().
 - Some map-scripts use separate lists to manipulate terrain/rivers. See Erebus or PerfectWorld2
      for a possible if imperfect way to handle that.
 - You probably have to rename some of your functions too.
      If you find functions in the map-script with the same name as the newly inserted ones,
      check if you can just delete them too, or rename then and call them from within the new
      functions.
      Take some care as some actually return a value, which needs to be returned or assigned somewhere.
 - Rename the new map-script to: yourmapname_mst.py
 NOTE:
 - There are always some adjustments to make.
 - There is always an adjustment that's more complicated than anticipated.
 - There may be a lot adjustments - not usually though.
 - Placing bad code into minStartingDistanceModifier() may crash your computer.
 - Feel free to delete any superfluous comments if they distract too much.

##################################################################################
## MapScriptTools Interface Template
##################################################################################
import MapScriptTools as mst
balancer = mst.bonusBalancer

# The following global constants are not neccessary,
# but they are widely used and make reading the code easier.
# (Yes I know thet local variables are faster, but that's only appreciable
#  within deeply nested loops, and the script runs only once per game anyway.)
# ----------------------------------------------------------------------------
gc = CyGlobalContext()
map = CyMap()

# The following two functions are not exactly neccessary either, but they should be
# in all map-scripts. Just comment them out if they are already in the script.
# ---------------------------------------------------------------------------------
def getVersion():
	return "1.20a"
def getDescription():
	return "MyMapScript - looks like a game world. Ver." + getVersion()


# #################################################################################################
# ######## beforeInit() - Starts the map-generation process, called after the map-options are known
# ########              - map dimensions, latitudes and wrapping status are not known yet
# ######## - handle map specific options
# #################################################################################################
# usually you don't need this, but sometimes it makes things easier
"""
def beforeInit():
	print "-- beforeInit()"

	#Selected map options
	# global myOption
	# myOption = map.getCustomMapOption(0)

	# allow default pre initialization
	CyPythonMgr().allowDefaultImpl()
"""

# #######################################################################################
# ######## beforeGeneration() - Called from system after all map parameter are known
# ######## - define your latitude formula, get the map-version
# ######## - create map options info string
# ######## - initialize the MapScriptTools
# ######## - initialize MapScriptTools.BonusBalancer
# #######################################################################################
def beforeGeneration():
	print "-- beforeGeneration()"

	# Create mapInfo string - this should work for all maps
	mapInfo = ""
	for opt in range( getNumCustomMapOptions() ):
		nam = getCustomMapOptionName( [opt] )
		sel = map.getCustomMapOption( opt )
		txt = getCustomMapOptionDescAt( [opt,sel] )
		mapInfo += "%27s:   %s\n" % ( nam, txt )

	# Create function for mst.evalLatitude - here Ringworld3
	#if mapOptions.Polar == 0:
	#	compGetLat = "int(round([0.95,0.80,0.64,0.60,0.52,0.40,0.24,0.04,0.04,0.24,0.40,0.52,0.60,0.64,0.80,0.95][y]*80))"
	#elif mapOptions.Polar == 1:
	#	compGetLat = "int(round([0.98,0.86,0.75,0.65,0.56,0.48,0.41,0.34,0.27,0.21,0.16,0.12,0.09,0.06,0.03,0.00][y]*80))"
	#elif mapOptions.Polar == 2:
	#	compGetLat = "int(round([0.00,0.03,0.06,0.09,0.12,0.16,0.21,0.27,0.34,0.41,0.48,0.56,0.65,0.75,0.86,0.98][y]*80))"
	#elif mapOptions.Polar == 3:
	#	compGetLat = "int(round([0.70,0.57,0.47,0.37,0.28,0.20,0.13,0.08,0.03,0.00,0.03,0.08,0.13,0.20,0.28,0.37][y]*90))"

	# Initialize MapScriptTools
	mst.getModInfo( getVersion(), None, mapInfo, bNoSigns=False )

	# Initialize MapScriptTools.BonusBalancer
	# - balance boni, place missing boni, move minerals, longer balancing range
	balancer.initialize( True, True, True, True )

	# Initialize MapScriptTools.MapRegions, don't use landmarks for FFH or Planetfall
	#mst.mapRegions.initialize( noSigns = (mst.bFFH or bPfall) )

# #######################################################################################
# ######## generateTerrainTypes() - Called from system after generatePlotTypes()
# ######## - SECOND STAGE in 'Generate Map'
# ######## - creates an array of terrains (desert,plains,grass,...) in the map dimensions
# #######################################################################################
def generateTerrainTypes():
	print "-- generateTerrainTypes()"
	mst.mapPrint.buildPlotMap( True, "generateTerrainTypes()" )

	# Planetfall: build more highlands and ridges
	mst.planetFallMap.buildPfallHighlands()

	# Prettify the map - you may not want this
	mst.mapPrettifier.hillifyCoast()
	mst.mapPrettifier.bulkifyIslands()

	# Choose terrainGenerator
	if mst.bPfall:
		terrainGen = mst.MST_TerrainGenerator()
	elif mst.bMars:
		# There are two possible scenarios for 'Mars Now!':
		# either water is converted to desert or not
		iDesert = mst.iif( mst.bSandsOfMars, 16, 32 )	# already enough desert with 'Sands of Mars'
		terrainGen = mst.MST_TerrainGenerator_Mars( iDesertPercent=iDesert )
	else:
		terrainGen = mst.MST_TerrainGenerator()			# this is the default
		# terrainGen = MyTerrainGenerator() 			# better is the terrain generator of the map-script
	# Generate terrain
	terrainTypes = terrainGen.generateTerrain()
	return terrainTypes

# #######################################################################################
# ######## addRivers() - Called from system after generateTerrainTypes()
# ######## - THIRD STAGE in 'Generate Map'
# ######## - puts rivers on the map
# #######################################################################################
def addRivers():
	print "-- addRivers()"
	mst.mapPrint.buildTerrainMap( True, "addRivers()" )

	# Generate marsh terrain
	mst.marshMaker.convertTerrain()

	# Create map-regions
	mst.mapRegions.buildBigBogs()									# build BigBogs
	mst.mapRegions.buildBigDents()									# build BigDents

	# Expand coastal waters - you may not want this
	mst.mapPrettifier.expandifyCoast()
	# Generate DeepOcean-terrain if mod allows for it
	mst.deepOcean.buildDeepOcean()

	# Some scripts produce more chaotic terrain than others. You can create more connected
	# (bigger) deserts by converting surrounded plains and grass.
	# Prettify the map - create better connected deserts and plains
	if not mst.bPfall:
		mst.mapPrettifier.lumpifyTerrain( mst.etDesert, mst.etPlains, mst.etGrass )
		mst.mapPrettifier.lumpifyTerrain( mst.etPlains, mst.etDesert, mst.etGrass )

	# No standard rivers for 'SandsOfMars'
	if not mst.bSandsOfMars:
		CyPythonMgr().allowDefaultImpl()							# don't forget this

		# Put rivers on small islands
		mst.riverMaker.islandRivers()

# #######################################################################################
# ######## addLakes() - Called from system after addRivers()
# ######## - FOURTH STAGE in 'Generate Map'
# ######## - puts lakes on the map
# #######################################################################################
# if the map-script disallows lakes, then just comment this out
def addLakes():
	print "-- addLakes()"
	mst.mapPrint.buildRiverMap( True, "addRivers()" )

	# No lakes on desertified Mars
	if not mst.bSandsOfMars:
		CyPythonMgr().allowDefaultImpl()

# #######################################################################################
# ######## addFeatures() - Called from system after addLakes()
# ######## - FIFTH STAGE in 'Generate Map'
# ######## - puts features on the map
# #######################################################################################
def addFeatures():
	print "-- addFeatures()"
	mst.mapPrint.buildRiverMap( True, "addFeatures()" )

	# Prettify map - connect some small adjacent lakes
	mst.mapPrettifier.connectifyLakes()
	# Sprout rivers from lakes
	# - all lakes, 33% chance for each of a maximum of two rivers, from lakes of minimum size 2
	mst.riverMaker.buildRiversFromLake( None, 33, 2, 2 )

	featureGen = mst.MST_FeatureGenerator()		# 'Mars Now!' needs this generator
	featureGen.addFeatures()

	# Planetfall: handle shelves and trenches
	mst.planetFallMap.buildPfallOcean()
	# Prettify the map - transform coastal volcanos; default: 66% chance
	mst.mapPrettifier.beautifyVolcanos()
	# Build ElementalQuarter; default: 33% chance
	mst.mapRegions.buildElementalQuarter()

# #######################################################################################
# ######## addBonuses() - Called from system after addFeatures()
# ######## - SIXTH STAGE in 'Generate Map'
# ######## - puts boni on the map
# #######################################################################################
# usually just comment this out
def addBonuses():
	print "-- addBonuses()"
	mst.mapPrint.buildFeatureMap( True, "addBonuses()" )

	# if the script handles boni itself, insert the function here
	CyPythonMgr().allowDefaultImpl()

# #######################################################################################
# ######## addGoodies() - Called from system after addBonuses()
# ######## - SEVENTH STAGE in 'Generate Map'
# ######## - puts Goody Huts on the map
# ######## - Note: FFH mods call this function 3 times and adjust between calls
# #######################################################################################
# usually just comment this out
#def addGoodies():
#	print "-- addGoodies()"
#	if mst.bPfall:									# Planetfall has it's own way
#		CyPythonMgr().allowDefaultImpl()
#	else:
#		myAddGoodies()								# adjust for map-script Goody Hut generator

# ######################################################################################################
# ######## assignStartingPlots() - Called from system
# ######## - assign starting positions for each player after the map is generated
# ######## - Planetfall has GameOption 'SCATTERED_LANDING_PODS' - use mods default implementation
# ######## - Mars Now! has an odd resource system and maybe no water - use mods default implementation
# ######################################################################################################
def assignStartingPlots():
	print "-- assignStartingPlots()"
	mst.mapPrint.buildBonusMap( True, "assignStartingPlots()" )

	if mst.bPfall or mst.bMars:					# for Planetfall and Mars you need this
		CyPythonMgr().allowDefaultImpl()
	else:
		CyPythonMgr().allowDefaultImpl()
		myAssignStartingPlots()						# adjust for map-script starting-plot generator

# ############################################################################################
# ######## normalizeStartingPlotLocations() - Called from system after starting-plot selection
# ######## - FIRST STAGE in 'Normalize Starting-Plots'
# ######## - change assignments to starting-plots
# ############################################################################################
def normalizeStartingPlotLocations():
	print "-- normalizeStartingPlotLocations()"
	mst.mapPrint.buildRiverMap( True, "addRivers()" )		# river-map also shows starting-plots

	# build Lost Isle
	# - this region needs to be placed after starting-plots are first assigned
	# - 33% chance to build and 33% chance for hightech
	mst.mapRegions.buildLostIsle( 40, bAliens=mst.choose(33,True,False) )

	# shuffle starting-plots for teams
	#opt = map.getCustomMapOption(3)						# assuming the 4th map-option is for teams
	#if opt == 0:
	#	CyPythonMgr().allowDefaultImpl()					# by default civ places teams near to each other
	#	# mst.teamStart.placeTeamsTogether( True, True )	# use teamStart to place teams near to each other
	#elif opt == 1:
	#	mst.teamStart.placeTeamsTogether( False, True )		# shuffle starting-plots to separate team players
	#elif opt == 2:
	#	mst.teamStart.placeTeamsTogether( True, True )		# randomize starting-plots (may be near or not)
	#else:
	#	mst.teamStart.placeTeamsTogether( False, False )	# leave starting-plots alone

	# comment this out if team option exists
	CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeAddRiver() - Called from system after normalizeStartingPlotLocations()
# ######## - SECOND STAGE in 'Normalize Starting-Plots'
# ######## - add some rivers if needed
# ############################################################################################
def normalizeAddRiver():
	print "-- normalizeAddRiver()"

	if not mst.bSandsOfMars:					# No additional rivers on desertified Mars
		CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeRemovePeaks() - Called from system after normalizeAddRiver()
# ######## - THIRD STAGE in 'Normalize Starting-Plots'
# ######## - remove some peaks if needed
# ############################################################################################
#def normalizeRemovePeaks():
#	print "-- normalizeRemovePeaks()"
#	CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeAddLakesRiver() - Called from system after normalizeRemovePeaks()
# ######## - FOURTH STAGE in 'Normalize Starting-Plots'
# ######## - add some lakes if needed
# ############################################################################################
def normalizeAddLakes():
	print "-- normalizeAddLakes()"

	if not mst.bSandsOfMars:					# No additional lakes on desertified Mars
		CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeRemoveBadFeatures() - Called from system after normalizeAddLakes()
# ######## - FIFTH STAGE in 'Normalize Starting-Plots'
# ######## - remove bad features if needed
# ############################################################################################
#def normalizeRemoveBadFeatures():
#	print "-- normalizeRemoveBadFeatures()"
#	CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeRemoveBadTerrain() - Called from system after normalizeRemoveBadFeatures()
# ######## - SIXTH STAGE in 'Normalize Starting-Plots'
# ######## - change bad terrain if needed
# ############################################################################################
def normalizeRemoveBadTerrain():
	print "-- normalizeRemoveBadTerrain()"
	if not (mst.bPfall or mst.bMars):		# On Planetfall and Mars leave bad terrain alone
		CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeAddFoodBonuses() - Called from system after normalizeRemoveBadTerrain()
# ######## - SEVENTH STAGE in 'Normalize Starting-Plots'
# ######## - add food if needed
# ############################################################################################
def normalizeAddFoodBonuses():
	print "-- normalizeAddFoodBonuses()"
	if mst.bMars:
		CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeAddGoodTerrain() - Called from system after normalizeAddFoodBonuses()
# ######## - EIGHTH STAGE in 'Normalize Starting-Plots'
# ######## - add good terrain if needed
# ############################################################################################
def normalizeAddGoodTerrain():
	print "-- normalizeAddGoodTerrain()"
	if not (mst.bPfall or mst.bMars):		# On Planetfall and Mars don't add good terrain
		CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeAddExtras() - Called from system after normalizeAddGoodTerrain()
# ######## - NINTH and LAST STAGE in 'Normalize Starting-Plots'
# ######## - last chance to adjust starting-plots
# ######## - called before startHumansOnSameTile(), which is the last map-function so called
# ############################################################################################
def normalizeAddExtras():
	print "-- normalizeAddExtras()"

	# Balance boni, place missing boni and move minerals
	balancer.normalizeAddExtras()

	# Do the default housekeeping
	CyPythonMgr().allowDefaultImpl()

	# Make sure marshes are on flatlands
	mst.marshMaker.normalizeMarshes()

	# Give extras to special regions
	mst.mapRegions.addRegionExtras()

	# Place special features on map (like Reefs, Kelp, Scrub, Haunted Lands, etc.)
	mst.featurePlacer.placeFeatures()

	# Kill ice on hot edges
	mst.mapPrettifier.deIcifyEdges()

	# Print maps and stats
	mst.mapStats.statPlotCount( "" )
	# Print plotMap
	mst.mapPrint.buildPlotMap( True, "normalizeAddExtras()" )
	# Print areaMap
	mst.mapPrint.buildAreaMap( True, "normalizeAddExtras()" )
	# Print terrainMap
	mst.mapPrint.buildTerrainMap( True, "normalizeAddExtras()" )
	# Print featureMap
	mst.mapPrint.buildFeatureMap( True, "normalizeAddExtras()" )
	# Print bonusMap
	mst.mapPrint.buildBonusMap( True, "normalizeAddExtras()" )
	# Print manaMap if FFH
	if mst.bFFH: mst.mapPrint.buildBonusMap( True, "normalizeAddExtras():Mana", None, mst.mapPrint.manaDict )
	# Print riverMap
	mst.mapPrint.buildRiverMap( True, "normalizeAddExtras()" )
	# Print mod and map statistics
	mst.mapStats.mapStatistics()

# ############################################################################
# ######## minStartingDistanceModifier() - Called from system at various times
# ######## - FIRST STAGE in 'Select Starting-Plots'
# ######## - adjust starting-plot distances
# ############################################################################
def minStartingDistanceModifier():
#	print "-- minStartingDistanceModifier()"
	if mst.bPfall: return -25
	if mst.bMars: return -15
	return 0
################################################################################

'''