#
#	FILE:	 Sea_Highlands_mst.py
#	AUTHOR:  Bob Thomas (Sirian)
#	PURPOSE: Regional map script - mountainous terrain
#-----------------------------------------------------------------------------
#	Copyright (c) 2005 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#   MODIFIED BY: vbraun
#   PURPOSE: Added a 4th sea option, because Gogf wanted the ability to
#            have naval battles in a highland game.
#
#   MODIFIED BY: Temudjin (2010)
#   PURPOSE:    - compatibility with 'Fall from Heaven', 'Planetfall', 'Mars Now!'
#               - add Marsh terrain, if supported by mod
#               - better balanced resources
#               - print stats of mod and map
#               - and more ...
#   DEPENDENCY: - needs MapScriptTools.py
#------------------------------------------------------------------------------
#   1.24    Terkhen   12.Sep.2016
#        - changed, use grid definitions from the active mod instead of using hardcoded ones.
#   1.23    Terkhen   17.Aug.2016
#        - fixed, use terrain, feature and improvement definitions from MST.
#   1.22    Terkhen   08.Dic.2014
#        - added, save/load map options.
#        - added, compatibility with RandomMap.
#        - added, resource balance option.
#        - changed, use TXT strings instead of hardcoded ones.
#   1.21    Temudjin  15.Mar.2011
#        - fixed compatibility to Planetfalls 'Scattered Pods' mod option
#        - fixed compatibility with some mods having neither whales nor pearls
#        - fixed [Mars Now!], team start normalization
#        - added, new map option: expanded coastal waters (like Civ5)
#        - added [Mars Now!], new map option: 'Sands of Mars'/'Terraformed Mars'
#        - changed, stratified custom map option process
#        - changed, stratified normalization process
#        - changed, reorganised function call sequence within map building process
#        - changed [Mars Now!], using dedicated terrain generator
#   1.20    Temudjin  15.Jul.2010  ( use MapScriptTools )
#        - allow more than 18 players
#        - adjust lake density and size
#        - compatibility with 'Planetfall'
#        - compatibility with 'Mars Now!'
#        - add Map Option: TeamStart
#        - add Marsh terrain, if supported by mod
#        - add Deep Ocean terrain, if supported by mod
#        - add rivers on islands
#        - allow more world sizes, if supported by mod
#        - add Map Features ( Kelp, HauntedLands, CrystalPlains )
#        - add Map Regions ( BigDent, BigBog, ElementalQuarter, LostIsle )
#        - better balanced resources
#        - print stats of mod and map
#        - add getVersion(), change getDescription()
#   1.10    vbraun
#        - 4th sea option
#


def getVersion():
	return "1.24_mst"

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_SEA_HIGHLANDS_DESCR"


from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from math import sqrt


map = CyMap()
gc = CyGlobalContext()
dice = gc.getGame().getMapRand()

################################################################
## MapScriptTools Interface by Temudjin
################################################################
import MapScriptTools as mst
balancer = mst.bonusBalancer

# #################################################################################################
# ######## randomMapBeforeInit() - Starts the map-generation process, called by RandomMap to set
# ######## the map options
# #################################################################################################
def randomMapBeforeInit(moWorldShape, moResources, moCoastalWaters, moTeamStart, moMarsTheme):
	print "-- randomMapBeforeInit()"

	# Avoid errors while printing custom options.
	global op
	op = {}

	# Map options of this script
	global mapOptionRidgelines, mapOptionPeaks, mapOptionLakes, mapOptionResources
	global mapOptionCoastalWaters, mapOptionTeamStart, mapOptionMarsTheme

	# Options chosen in Random Map
	mapOptionWorldShape = moWorldShape
	mapOptionResources = moResources
	mapOptionCoastalWaters = moCoastalWaters
	mapOptionTeamStart = moTeamStart
	mapOptionMarsTheme = moMarsTheme

	# All other options are chosen randomly.
	mapOptionRidgelines = dice.get(3, "Sea_Highlands.randomMapBeforeInit(), mapOptionRidgelines")
	mapOptionPeaks = dice.get(3, "Sea_Highlands.randomMapBeforeInit(), mapOptionPeaks")
	mapOptionLakes = dice.get(4, "Sea_Highlands.randomMapBeforeInit(), mapOptionLakes")

	# Roll a dice to determine if the cold region will be in north or south.
	global shiftMultiplier
	shiftRoll = mst.choose(50, True, False)
	if shiftRoll:	# Cold in north
		shiftMultiplier = 0.0
	else:			# Cold in south
		shiftMultiplier = 1.0

# #######################################################################################
# ######## beforeInit() - Called after the map options are known
# ######## - starts the map-generation process
# ######## - map dimensions, latitudes and wrapping status are not known yet
# ######## - handle map specific options
# ######## - determine where the cold comes from
# #######################################################################################
def beforeInit():
	print "-- beforeInit()"
	# Selected map options
	global mapOptionRidgelines, mapOptionPeaks, mapOptionLakes, mapOptionResources
	global mapOptionCoastalWaters, mapOptionTeamStart, mapOptionMarsTheme
	mapOptionResources = map.getCustomMapOption(0)
	mapOptionRidgelines = map.getCustomMapOption(1)
	mapOptionPeaks = map.getCustomMapOption(2)
	mapOptionLakes = map.getCustomMapOption(3)
	mapOptionCoastalWaters = mst.iif(mst.bPfall, None, map.getCustomMapOption(4))
	mapOptionTeamStart = mst.iif(mst.bMars, None, map.getCustomMapOption( mst.iif(mst.bPfall,4,5) ))
	mapOptionMarsTheme = mst.iif(mst.bMars, map.getCustomMapOption(5), None)

	# Roll a dice to determine if the cold region will be in north or south.
	global shiftMultiplier
	shiftRoll = mst.choose(50, True, False)
	if shiftRoll:	# Cold in north
		shiftMultiplier = 0.0
	else:			# Cold in south
		shiftMultiplier = 1.0

# #######################################################################################
# ######## beforeGeneration() - Called from system after user input is finished
# ######## - define your latitude formula, get the map-version
# ######## - create map options info string
# ######## - initialize the MapScriptTools
# ######## - initialize MapScriptTools.BonusBalancer
# #######################################################################################
def beforeGeneration():
	print "--- beforeGeneration()"

	# Create evaluation string for getLatitude(x,y); vars can be x or y
	cStep = "(y/%5.1f) - %3.1f" % ( map.getGridHeight()-1, shiftMultiplier )
	cDiff = map.getTopLatitude() - map.getBottomLatitude()
	cBott = map.getBottomLatitude()
	compGetLat = "abs(%s) * (%i) + (%i)" % ( cStep, cDiff, cBott )
	# Create mapInfo string
	mapInfo = ""

	# Backup current language
	iLanguage = CyGame().getCurrentLanguage()
	# Force english language for logs
	CyGame().setCurrentLanguage(0)

	for opt in range( getNumCustomMapOptions() ):
		nam = getCustomMapOptionName( [opt] )
		sel = map.getCustomMapOption( opt )
		txt = getCustomMapOptionDescAt( [opt,sel] )
		mapInfo += "%27s:   %s\n" % ( nam, txt )

	# Restore current language
	CyGame().setCurrentLanguage(iLanguage)

	# Obtain the map options in use.
	lMapOptions = []
	for opt in range( getNumCustomMapOptions() ):
		iValue = 0 + map.getCustomMapOption( opt )
		lMapOptions.append( iValue )

	# Save used map options.
	mst.mapOptionsStorage.writeConfig(lMapOptions)

	# Initialize MapScriptTools
	mst.getModInfo( getVersion(), compGetLat, mapInfo )

	# Determine global Mars Theme
	mst.bSandsOfMars = (mapOptionMarsTheme == 0)

	# Initialize bonus balancer
	balancer.initialize( mapOptionResources == 1 ) # balance boni if desired, place missing boni, move minerals

# #######################################################################################
# ######## generateTerrainTypes() - Called from system
# ######## - SECOND STAGE in 'Generate Map'
# ######## - creates an array of terrains (desert,plains,grass,...) in the map dimensions
# #######################################################################################
def generateTerrainTypes():
	print "-- generateTerrainTypes()"

	# Planetfall: more highlands
	mst.planetFallMap.buildPfallHighlands()
	# Prettify map: Connect small islands
	# mst.mapPrettifier.bulkifyIslands()
	# Prettify map: most coastal peaks -> hills
	mst.mapPrettifier.hillifyCoast()

	# Choose terrainGenerator
	if mst.bPfall:
		terraingen = mst.MST_TerrainGenerator()
	elif mst.bMars:
		terraingen = mst.MST_TerrainGenerator_Mars()
	else:
		terraingen = HighlandsTerrainGenerator()
	# Generate terrain
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

# #######################################################################################
# ######## addRivers() - Called from system
# ######## - THIRD STAGE in 'Generate Map'
# ######## - puts rivers on the map
# #######################################################################################
def addRivers():
	print "-- addRivers()"

	# Make marsh terrain
	mst.marshMaker.convertTerrain()

	# Expand coastal waters
	if CyMap().getCustomMapOption(2) == 1:
		mst.mapPrettifier.expandifyCoast()

	# Build between 0..2 mountain-ranges.
	mst.mapRegions.buildBigDents()
	# Build between 0..2 bog-regions.
	mst.mapRegions.buildBigBogs()

	# Generate DeepOcean-terrain if mod allows for it
	mst.deepOcean.buildDeepOcean()

	# Create connected deserts and plains
	if not mst.bPfall:
		mst.mapPrettifier.lumpifyTerrain( mst.etDesert, mst.etPlains, mst.etGrass )
		if mst.bMars:
			mst.mapPrettifier.lumpifyTerrain( mst.etPlains, mst.etDesert, mst.etGrass )
			mst.mapPrettifier.lumpifyTerrain( mst.etGrass, mst.etDesert, mst.etPlains )
			mst.mapPrettifier.lumpifyTerrain( mst.etDesert, mst.etPlains, mst.etGrass )
		else:
			mst.mapPrettifier.lumpifyTerrain( mst.etGrass, mst.etTundra, mst.etPlains )
			mst.mapPrettifier.lumpifyTerrain( mst.etPlains, mst.etDesert, mst.etGrass )

	# No standard rivers on Mars
	if not mst.bMars:
		# Put rivers on the map.
		CyPythonMgr().allowDefaultImpl()

	# Put rivers on small islands
	mst.riverMaker.islandRivers()

# #######################################################################################
# ######## addLakes() - Called from system
# ######## - FOURTH STAGE in 'Generate Map'
# ######## - puts lakes on the map
# #######################################################################################
def addLakes():
	print "-- addLakes()"
	if not mst.bSandsOfMars:
		CyPythonMgr().allowDefaultImpl()

# #######################################################################################
# ######## addFeatures() - Called from system after addLakes()
# ######## - FIFTH STAGE in 'Generate Map'
# ######## - puts features on the map
# #######################################################################################
def addFeatures():
	print "-- addFeatures()"

	# Prettify map - connect some small adjacent lakes
	mst.mapPrettifier.connectifyLakes()
	# Sprout rivers from lakes.
	mst.riverMaker.buildRiversFromLake( None, 33, 2, 3 )

	# Choose featureGenerator
	if mst.bPfall or mst.bMars:
		featuregen = mst.MST_FeatureGenerator()
	else:
		featuregen = HighlandsFeatureGenerator()
	# Generate features
	featuregen.addFeatures()

	# Prettify the map - transform coastal volcanos; default: 66% chance
	mst.mapPrettifier.beautifyVolcanos()
	# Mars Now!: lumpify sandstorms
	if mst.bMars: mst.mapPrettifier.lumpifyTerrain( mst.efSandStorm, FeatureTypes.NO_FEATURE )
	# Planetfall: handle shelves and trenches
	if mst.bPfall: mst.planetFallMap.buildPfallOcean()
	# FFH: build ElementalQuarter; default: 5% chance
	mst.mapRegions.buildElementalQuarter()


# ############################################################################################
# ######## normalizeStartingPlotLocations() - Called from system after starting-plot selection
# ######## - FIRST STAGE in 'Normalize Starting-Plots'
# ######## - change assignments to starting-plots
# ############################################################################################
def normalizeStartingPlotLocations():
	print "-- normalizeStartingPlotLocations()"

	# build Lost Isle
	# - this region needs to be placed after starting-plots are first assigned
	mst.mapRegions.buildLostIsle( chance=33, minDist=7, bAliens=mst.choose(33,True,False) )

	if mst.bMars:
		# Mars Now! uses no teams
		CyPythonMgr().allowDefaultImpl()
	elif mapOptionTeamStart == 0:
		CyPythonMgr().allowDefaultImpl()					# by default civ places teams near to each other
		# mst.teamStart.placeTeamsTogether( True, True )	# use teamStart to place teams near to each other
	elif mapOptionTeamStart == 1:
		mst.teamStart.placeTeamsTogether( False, True )		# shuffle starting-plots to separate teams
	elif mapOptionTeamStart == 2:
		mst.teamStart.placeTeamsTogether( True, True )		# randomize starting-plots (may be near or not)
	else:
		mst.teamStart.placeTeamsTogether( False, False )	# leave starting-plots alone

# ############################################################################################
# ######## normalizeAddRiver() - Called from system after normalizeStartingPlotLocations()
# ######## - SECOND STAGE in 'Normalize Starting-Plots'
# ######## - add some rivers if needed
# ############################################################################################
def normalizeAddRiver():
	print "-- normalizeAddRiver()"
	return None

# ############################################################################################
# ######## normalizeRemovePeaks() - Called from system after normalizeAddRiver()
# ######## - THIRD STAGE in 'Normalize Starting-Plots'
# ######## - remove some peaks if needed
# ############################################################################################
def normalizeRemovePeaks():
	print "-- normalizeRemovePeaks()"
	return None

# ############################################################################################
# ######## normalizeAddLakesRiver() - Called from system after normalizeRemovePeaks()
# ######## - FOURTH STAGE in 'Normalize Starting-Plots'
# ######## - add some lakes if needed
# ############################################################################################
def normalizeAddLakes():
	print "-- normalizeAddLakes()"
	if not (mst.bMars and mst.bSandsOfMars):
		CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeRemoveBadFeatures() - Called from system after normalizeAddLakes()
# ######## - FIFTH STAGE in 'Normalize Starting-Plots'
# ######## - remove bad features if needed
# ############################################################################################
def normalizeRemoveBadFeatures():
	print "-- normalizeRemoveBadFeatures()"
	return None

# ############################################################################################
# ######## normalizeRemoveBadTerrain() - Called from system after normalizeRemoveBadFeatures()
# ######## - SIXTH STAGE in 'Normalize Starting-Plots'
# ######## - change bad terrain if needed
# ############################################################################################
def normalizeRemoveBadTerrain():
	print "-- normalizeRemoveBadTerrain()"
	return None

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
	return None

# ############################################################################################
# ######## normalizeAddExtras() - Called from system after normalizeAddGoodTerrain()
# ######## - NINTH and LAST STAGE in 'Normalize Starting-Plots'
# ######## - last chance to adjust starting-plots
# ######## - called before startHumansOnSameTile(), which is the last map-function so called
# ############################################################################################
def normalizeAddExtras():
	print "-- normalizeAddExtras()"
	# Balance boni, place missing boni, move minerals
	balancer.normalizeAddExtras( '-BONUS_WHALE', '-BONUS_PEARL', '-BONUS_PEARLS' )

	# Do the default housekeeping
	# CyPythonMgr().allowDefaultImpl()

	# Make sure marshes are on flatlands
	mst.marshMaker.normalizeMarshes()
	# Give extras to special regions
	mst.mapRegions.addRegionExtras()
	# Place special features on map
	mst.featurePlacer.placeFeatures()
	# Kill ice on warm edges
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
	mst.mapPrint.buildBonusMap( False, "normalizeAddExtras()" )
	# Print manaMap if FFH
	if mst.bFFH: mst.mapPrint.buildBonusMap( False, "normalizeAddExtras():Mana", None, mst.mapPrint.manaDict )
	# Print riverMap
	mst.mapPrint.buildRiverMap( True, "normalizeAddExtras()" )
	# Print mod and map statistics
	mst.mapStats.mapStatistics()

# ############################################################################################
# ######## startHumansOnSameTile() - Called from system at the end of the map making process
# ######## - LAST FUNCTION to be called ba the 'Map Making Process'
# ######## - start with all units on the same plot
# ############################################################################################
#def startHumansOnSameTile():
#	print "-- startHumansOnSameTile()"
#	return False

# ############################################################################################
# ######## minStartingDistanceModifier() - Called from system at various times
# ######## - FIRST STAGE in 'Select Starting-Plots'
# ######## - adjust starting-plot distances
# ############################################################################################
def minStartingDistanceModifier():
	if mst.bPfall: return -25
	if mst.bMars: return -15
	return -35

################################################################
## Custom Map Option Interface by Temudjin                 START
################################################################
def setCustomOptions():
	""" Set all custom options in one place """
	global op	# { optionID: Name, OptionList, Default, RandomOpt }

	# Initialize options to the default values.
	lMapOptions = [0, 1, 1, 3, 0, 0]

	# Try to read map options from the cfgFile.
	mst.mapOptionsStorage.initialize(lMapOptions, 'Sea_Highlands')
	lMapOptions = mst.mapOptionsStorage.readConfig()

	optionPattern = ["TXT_KEY_MAP_SCRIPT_SCATTERED", "TXT_KEY_MAP_SCRIPT_RIDGELINES", "TXT_KEY_MAP_SCRIPT_CLUSTERED"]
	optionDensity = ["TXT_KEY_MAP_SCRIPT_DENSE_PEAKS", "TXT_KEY_MAP_SCRIPT_NORMAL_PEAKS", "TXT_KEY_MAP_SCRIPT_THIN_PEAKS"]
	optionLakes =   ["TXT_KEY_MAP_SCRIPT_SMALL_LAKES", "TXT_KEY_MAP_SCRIPT_LARGE_LAKES",
	                 "TXT_KEY_MAP_SCRIPT_SEAS", "TXT_KEY_MAP_SCRIPT_LARGE_SEAS"]
	op = {
		   0: ["TXT_KEY_MAP_RESOURCES", ["TXT_KEY_MAP_RESOURCES_STANDARD", "TXT_KEY_MAP_RESOURCES_BALANCED"], lMapOptions[0], True],
	       1: ["TXT_KEY_MAP_SCRIPT_MOUNTAIN_PATTERN", optionPattern, lMapOptions[1], True],
	       2: ["TXT_KEY_MAP_SCRIPT_MOUNTAIN_DENSITY", optionDensity, lMapOptions[2], True],
	       3: ["TXT_KEY_MAP_SCRIPT_WATER_SETTING",    optionLakes,   lMapOptions[3], True],
	       4: ["TXT_KEY_MAP_COASTS", ["TXT_KEY_MAP_COASTS_STANDARD", "TXT_KEY_MAP_COASTS_EXPANDED"], lMapOptions[4], True],
	       "Hidden": 3
	     }
	if mst.bPfall:
	    op[4] = ["TXT_KEY_MAP_TEAM_START", ["TXT_KEY_MAP_TEAM_START_NEIGHBORS", "TXT_KEY_MAP_TEAM_START_SEPARATED", "TXT_KEY_MAP_TEAM_START_RANDOM"], lMapOptions[4], False]
	elif mst.bMars:
		op[5] = ["TXT_KEY_MAP_MARS_THEME", ["TXT_KEY_MAP_MARS_THEME_SANDS_OF_MARS", "TXT_KEY_MAP_MARS_THEME_TERRAFORMED_MARS"], lMapOptions[5], False]
	else:
	    op[5] = ["TXT_KEY_MAP_TEAM_START", ["TXT_KEY_MAP_TEAM_START_NEIGHBORS", "TXT_KEY_MAP_TEAM_START_SEPARATED", "TXT_KEY_MAP_TEAM_START_RANDOM"], lMapOptions[5], False]

	mst.printDict(op,"SeaHighlands Map Options:")

def isAdvancedMap():
	""" This map should show up in simple mode """
	return 0

# first function to be called by the map building process
def getNumHiddenCustomMapOptions():
	""" Default is used for the last n custom-options in 'Play Now' mode. """
	setCustomOptions()						# Define Options
	return op["Hidden"]

def getNumCustomMapOptions():
	""" Number of different user-defined options for this map """
	return len( op ) - 1

def getCustomMapOptionName(argsList):
	""" Returns name of specified option """
	optionID = argsList[0]
	translated_text = unicode(CyTranslator().getText(op[optionID][0], ()))
	return translated_text

def getNumCustomMapOptionValues(argsList):
	"""	Number of different choices for a particular setting """
	optionID = argsList[0]
	return len( op[optionID][1] )

def getCustomMapOptionDescAt(argsList):
	""" Returns name of value of option at specified row """
	optionID = argsList[0]
	valueID = argsList[1]
	translated_text = unicode(CyTranslator().getText(op[optionID][1][valueID], ()))
	return translated_text

def getCustomMapOptionDefault(argsList):
	"""	Returns default value of specified option """
	optionID = argsList[0]
	return op[optionID][2]

def isRandomCustomMapOption(argsList):
	"""	Returns a flag indicating whether a random option should be provided """
	optionID = argsList[0]
	return op[optionID][3]

################################################################
## Interfaces by Temudjin                                    END
################################################################

def isClimateMap():
	"""	Uses the Climate options """
	return False
def isSeaLevelMap():
	"""	Uses the Sea Level options """
	return False

def getTopLatitude():
	global shiftMultiplier
	if shiftMultiplier == 0.0:
		return 85
	else:
		return 10
def getBottomLatitude():
	global shiftMultiplier
	if shiftMultiplier == 0.0:
		return -10
	else:
		return -85

def getWrapX():
	return False
def getWrapY():
	return False

def isBonusIgnoreLatitude():
	return False

##########

def getGridSize(argsList):
	print " -- getGridSize()"
	if (argsList[0] == -1): return []			# (-1,) is passed to function on loads

	# Reduce grid sizes by one level.
	[eWorldSize] = argsList
	if eWorldSize >= 1:
		iWidth = CyGlobalContext().getWorldInfo(eWorldSize - 1).getGridWidth()
		iHeight = CyGlobalContext().getWorldInfo(eWorldSize - 1).getGridHeight()
	else:
		# Scale down the smallest world size
		iScale = 0.8
		iWidth = int(math.ceil(CyGlobalContext().getWorldInfo(0).getGridWidth() * iScale))
		iHeight = int(math.ceil(CyGlobalContext().getWorldInfo(0).getGridHeight() * iScale))

	return iWidth, iHeight

##########


def generatePlotTypes():
	print "-- generatePlotTypes()"
	NiTextOut("Setting Plot Types (Python Highlands) ...")
	gc = CyGlobalContext()
	map = CyMap()
	dice = gc.getGame().getMapRand()
	iFlags = 0  # Disallow FRAC_POLAR flag, to prevent "zero row" problems.
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	plotTypes = [PlotTypes.PLOT_LAND] * (iW*iH)
	terrainFrac = CyFractal()
	lakesFrac = CyFractal()

	# Varying grains for hills/peaks per map size and Mountain Ranges setting.
	# [clustered_grain, ridgelines_grain, scattered_grain]
	worldsizes = {
		WorldSizeTypes.WORLDSIZE_DUEL:      [3,4,5],
		WorldSizeTypes.WORLDSIZE_TINY:      [3,4,5],
		WorldSizeTypes.WORLDSIZE_SMALL:     [4,5,6],
		WorldSizeTypes.WORLDSIZE_STANDARD:  [4,5,6],
		WorldSizeTypes.WORLDSIZE_LARGE:     [4,5,6],
		WorldSizeTypes.WORLDSIZE_HUGE:      [4,5,6]
		}
########## Temudjin START
	worldsizes[6] = [4,5,6]
	worldsizes[7] = [4,5,6]
########## Temudjin END

	grain_list = worldsizes[map.getWorldSize()]
	grain_list.reverse()
	grain = grain_list[mapOptionRidgelines]

	# Peak density
	peak_list = [70, 77, 83]
	hill_list = [40, 45, 50]
	peaks = peak_list[mapOptionPeaks]
	hills = hill_list[mapOptionPeaks]

	# Lake density
	lake_list   = [6, 12, 17, 21]    #vbraun changed, temudjin changed 12,18,24->12,17,21
	lake_grains = [5,  4,  3,  2]    #vbraun changed, temudjin changed 1->2
	lakes = lake_list[mapOptionLakes]
	lake_grain = lake_grains[mapOptionLakes]

	terrainFrac.fracInit(iW, iH, grain, dice, 0, -1, -1)
	lakesFrac.fracInit(iW, iH, lake_grain, dice, 0, -1, -1)

	iLakesThreshold = lakesFrac.getHeightFromPercent(lakes)
	iHillsThreshold = terrainFrac.getHeightFromPercent(hills)
	iPeaksThreshold = terrainFrac.getHeightFromPercent(peaks)

	# Now the main loop, which will assign the plot types.
	for x in range(iW):
		for y in range(iH):
			i = y*iW + x
			lakeVal = lakesFrac.getHeight(x,y)
			val = terrainFrac.getHeight(x,y)
			if lakeVal <= iLakesThreshold:
				plotTypes[i] = PlotTypes.PLOT_OCEAN
			elif val >= iPeaksThreshold:
				plotTypes[i] = PlotTypes.PLOT_PEAK
			elif val >= iHillsThreshold and val < iPeaksThreshold:
				plotTypes[i] = PlotTypes.PLOT_HILLS
			else:
				plotTypes[i] = PlotTypes.PLOT_LAND

	return plotTypes

# subclass TerrainGenerator to redefine everything. This is a regional map.
class HighlandsTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
	def __init__(self, fracXExp=-1, fracYExp=-1):
		# Note: If you change longitude values here, then you will...
		# ...need to change them elsewhere in the script, as well.
		self.gc = CyGlobalContext()
		self.map = CyMap()

		self.grain_amount = 4 + self.gc.getWorldInfo(self.map.getWorldSize()).getTerrainGrainChange()

		self.iWidth = self.map.getGridWidth()
		self.iHeight = self.map.getGridHeight()

		self.mapRand = self.gc.getGame().getMapRand()

		self.iFlags = 0  # Disallow FRAC_POLAR flag, to prevent "zero row" problems.

		self.cold=CyFractal()
		self.cool=CyFractal()
		self.temp=CyFractal()
		self.hot=CyFractal()
		self.variation=CyFractal()

		self.iColdIBottomPercent = 75
		self.iColdTBottomPercent = 20
		self.iCoolTBottomPercent = 85
		self.iCoolPBottomPercent = 45
		self.iTempDBottomPercent = 90
		self.iTempPBottomPercent = 65
		self.iHotDBottomPercent = 70
		self.iHotPBottomPercent = 60

		self.fColdLatitude = 0.8
		self.fCoolLatitude = 0.6
		self.fHotLatitude = 0.2

		self.fracXExp = fracXExp
		self.fracYExp = fracYExp

		self.initFractals()

	def initFractals(self):
		self.cold.fracInit(self.iWidth, self.iHeight, self.grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.iColdIBottom = self.cold.getHeightFromPercent(self.iColdIBottomPercent)
		self.iColdTBottom = self.cold.getHeightFromPercent(self.iColdTBottomPercent)

		self.cool.fracInit(self.iWidth, self.iHeight, self.grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.iCoolTBottom = self.cool.getHeightFromPercent(self.iCoolTBottomPercent)
		self.iCoolPBottom = self.cool.getHeightFromPercent(self.iCoolPBottomPercent)

		self.temp.fracInit(self.iWidth, self.iHeight, self.grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.iTempDBottom = self.temp.getHeightFromPercent(self.iTempDBottomPercent)
		self.iTempPBottom = self.temp.getHeightFromPercent(self.iTempPBottomPercent)

		self.hot.fracInit(self.iWidth, self.iHeight, self.grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.iHotDBottom = self.hot.getHeightFromPercent(self.iHotDBottomPercent)
		self.iHotPBottom = self.hot.getHeightFromPercent(self.iHotPBottomPercent)

		self.variation.fracInit(self.iWidth, self.iHeight, self.grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)

		self.terrainDesert = mst.etDesert
		self.terrainPlains = mst.etPlains
		self.terrainGrass = mst.etGrass
		self.terrainIce = mst.etSnow
		self.terrainTundra = mst.etTundra
		self.terrainMarsh = mst.etMarsh


	def getLatitudeAtPlot(self, iX, iY):
		lat = iY/float(self.iHeight) # 0.0 = south

		# Adjust latitude using self.variation fractal, to mix things up:
		lat += (128 - self.variation.getHeight(iX, iY))/(255.0 * 5.0)

		# Limit to the range [0, 1]:
		if lat < 0:
			lat = 0.0
		if lat > 1:
			lat = 1.0

		# Flip terrain if southward shift was rolled.
		global shiftMultiplier
		fLatitude = abs(lat - shiftMultiplier)

		return fLatitude

	def generateTerrainAtPlot(self,iX,iY):
		lat = self.getLatitudeAtPlot(iX,iY)

		if (self.map.plot(iX, iY).isWater()):
			return self.map.plot(iX, iY).getTerrainType()

		if lat >= self.fColdLatitude:
			val = self.cold.getHeight(iX, iY)
			if val >= self.iColdIBottom:
				terrainVal = self.terrainIce
			elif val >= self.iColdTBottom and val < self.iColdIBottom:
				terrainVal = self.terrainTundra
			else:
				terrainVal = self.terrainPlains
		elif lat < self.fColdLatitude and lat >= self.fCoolLatitude:
			val = self.cool.getHeight(iX, iY)
			if val >= self.iCoolTBottom:
				terrainVal = self.terrainTundra
			elif val >= self.iCoolPBottom and val < self.iCoolTBottom:
				terrainVal = self.terrainPlains
			else:
				terrainVal = self.terrainGrass
		elif lat < self.fHotLatitude:
			val = self.hot.getHeight(iX, iY)
			if val >= self.iHotDBottom:
				terrainVal = self.terrainDesert
			elif val >= self.iHotPBottom and val < self.iHotDBottom:
				terrainVal = self.terrainPlains
			else:
				terrainVal = self.terrainGrass
		else:
			val = self.temp.getHeight(iX, iY)
			if val >= self.iTempDBottom:
				terrainVal = self.terrainDesert
			elif val < self.iTempDBottom and val >= self.iTempPBottom:
				terrainVal = self.terrainPlains
			else:
				terrainVal = self.terrainGrass

		if (terrainVal == TerrainTypes.NO_TERRAIN):
			return self.map.plot(iX, iY).getTerrainType()

		return terrainVal

class HighlandsFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def __init__(self, iJunglePercent=60, iForestPercent=45, iHotForestPercent = 25,
					 forest_grain=6, fracXExp=-1, fracYExp=-1):
		self.gc = CyGlobalContext()
		self.map = CyMap()
		self.mapRand = self.gc.getGame().getMapRand()
		self.forests = CyFractal()

		self.iFlags = 0  # Disallow FRAC_POLAR flag, to prevent "zero row" problems.

		self.iGridW = self.map.getGridWidth()
		self.iGridH = self.map.getGridHeight()

		self.iJunglePercent = iJunglePercent
		self.iForestPercent = iForestPercent
		self.iHotForestPercent = iHotForestPercent

		self.forest_grain = forest_grain + self.gc.getWorldInfo(self.map.getWorldSize()).getFeatureGrainChange()

		self.fracXExp = fracXExp
		self.fracYExp = fracYExp

		self.__initFractals()
		self.__initFeatureTypes()

	def __initFractals(self):
		self.forests.fracInit(self.iGridW, self.iGridH, self.forest_grain, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)

		self.iJungleLevel = self.forests.getHeightFromPercent(100 - self.iJunglePercent)
		self.iForestLevel = self.forests.getHeightFromPercent(self.iForestPercent)
		self.iHotForestLevel = self.forests.getHeightFromPercent(self.iHotForestPercent)

	def __initFeatureTypes(self):
		self.featureJungle = mst.efJungle
		self.featureForest = mst.efForest
		self.featureOasis = mst.efOasis

	def getLatitudeAtPlot(self, iX, iY):
		lat = iY/float(self.iGridH) # 0.0 = south
		# Flip terrain if southward shift was rolled.
		global shiftMultiplier
		return abs(lat - shiftMultiplier)

	def addFeaturesAtPlot(self, iX, iY):
		lat = self.getLatitudeAtPlot(iX, iY)
		pPlot = self.map.sPlot(iX, iY)

		for iI in range(self.gc.getNumFeatureInfos()):
			if pPlot.canHaveFeature(iI):
				if self.mapRand.get(10000, "Add Feature PYTHON") < self.gc.getFeatureInfo(iI).getAppearanceProbability():
					pPlot.setFeatureType(iI, -1)

		if (pPlot.getFeatureType() == FeatureTypes.NO_FEATURE):
			self.addJunglesAtPlot(pPlot, iX, iY, lat)

		if (pPlot.getFeatureType() == FeatureTypes.NO_FEATURE):
			self.addForestsAtPlot(pPlot, iX, iY, lat)

	def addIceAtPlot(self, pPlot, iX, iY, lat):
		# We don' need no steeking ice. M'kay? Alrighty then.
		ice = 0

	def addJunglesAtPlot(self, pPlot, iX, iY, lat):
		# Warning: this version of JunglesAtPlot is using the forest fractal!
		if lat < 0.17 and pPlot.canHaveFeature(self.featureJungle):
			if (self.forests.getHeight(iX, iY) >= self.iJungleLevel):
				pPlot.setFeatureType(self.featureJungle, -1)

	def addForestsAtPlot(self, pPlot, iX, iY, lat):
		if lat > 0.2:
			if pPlot.canHaveFeature(self.featureForest):
				if self.forests.getHeight(iX, iY) <= self.iForestLevel:
					pPlot.setFeatureType(self.featureForest, -1)
		else:
			if pPlot.canHaveFeature(self.featureForest):
				if self.forests.getHeight(iX, iY) <= self.iHotForestLevel:
					pPlot.setFeatureType(self.featureForest, -1)

def assignStartingPlots():
######### Temudjin START
	if mst.bPfall:
		CyPythonMgr().allowDefaultImpl()
	else:
######### Temudjin END

		# In order to prevent "pockets" from forming, where civs can be blocked in
		# by Peaks or lakes, causing a "dud" map, pathing must be checked for each
		# new start plot before it hits the map. Any pockets that are detected must
		# be opened. The following process takes care of this need. Soren created a
		# useful function that already lets you know how far a given plot is from
		# the closest nearest civ already on the board. MinOriginalStartDist is that
		# function. You can get-- or setMinoriginalStartDist() as a value attached
		# to each plot. Any value of -1 means no valid land-hills-only path exists to
		# a civ already placed. For Highlands, that means we have found a pocket
		# and it must be opened. A valid legal path from all civs to all other civs
		# is required for this map to deliver reliable, fun games every time.
		#
		# - Sirian
		#
		iW = map.getGridWidth()
		iH = map.getGridHeight()
		iPlayers = gc.getGame().countCivPlayersEverAlive()
		iNumStartsAllocated = 0
		start_plots = []
		#print "==="
		#print "Number of players:", iPlayers
		#print "==="

		terrainPlains = mst.etPlains

		# Obtain player numbers. (Account for possibility of Open slots!)
######### Temudjin START
		shuffledPlayers = []
		player_list = mst.mapStats.getCivPlayerList()
		for ply in player_list: shuffledPlayers.append( ply.getID() )
		mst.randomList.shuffle( shuffledPlayers )
#		player_list = []
#		for plrCheckLoop in range(18):
#			if CyGlobalContext().getPlayer(plrCheckLoop).isEverAlive():
#				player_list.append(plrCheckLoop)
#		# Shuffle players so that who goes first (and gets the best start location) is randomized.
#		for playerLoopTwo in range(gc.getGame().countCivPlayersEverAlive()):
#			iChoosePlayer = dice.get(len(player_list), "Shuffling Players - Highlands PYTHON")
#			shuffledPlayers.append(player_list[iChoosePlayer])
#			del player_list[iChoosePlayer]
######### Temudjin END

		# Loop through players, assigning starts for each.
		for assign_loop in range(iPlayers):
			playerID = shuffledPlayers[assign_loop]
			player = gc.getPlayer(playerID)

			# Use the absolute approach for findStart from CvMapGeneratorUtil, which
			# ignores areaID quality and finds the best local situation on the board.
			findstart = CvMapGeneratorUtil.findStartingPlot(playerID)
			sPlot = map.plotByIndex(findstart)

			# Record the plot number to the data array for use if needed to open a "pocket".
			iStartX = sPlot.getX()
			iStartY = sPlot.getY()

			# If first player placed, no need to check for pathing yet.
			if assign_loop == 0:
				start_plots.append([iStartX, iStartY])
				player.setStartingPlot(sPlot, true) # True flag causes data to be refreshed for MinOriginalStartDist data cells in plots on the same land mass.
				#print "-+-+-"
				print "Player"
				print playerID
				print "First player assigned."
				print "-+-+-"
				continue

			# Check the pathing in the start plot.
			if sPlot.getMinOriginalStartDist() != -1:
				start_plots.append([iStartX, iStartY])
				player.setStartingPlot(sPlot, true)
				#print "-+-+-"
				print "Player"
				print playerID
				print "Open Path, no problems."
				print "-+-+-"
				continue

			# If the process has reached this point, then this player is stuck
			# in a "pocket". This could be an island, a valley surrounded by peaks,
			# or an area blocked off by peaks. Could even be that a major line
			# of peaks and lakes combined is bisecting the entire map.
			#print "-----"
			print "Player"
			print playerID
			print "Pocket detected, attempting to resolve..."
			#print "-----"
			#
			# First step is to identify which existing start plot is closest.
			#print "Pocket Plot"
			#print iStartX, iStartY
			#print "---"
			[iEndX, iEndY] = start_plots[0]
			fMinDistance = sqrt(((iStartX - iEndX) ** 2) + ((iStartY - iEndY) ** 2))
			for check_loop in range(1, len(start_plots)):
				[iX, iY] = start_plots[check_loop]
				if fMinDistance > sqrt(((iStartX - iX) ** 2) + ((iStartY - iY) ** 2)):
					# Closer start plot found!
					[iEndX, iEndY] = start_plots[check_loop]
					fMinDistance = sqrt(((iStartX - iX) ** 2) + ((iStartY - iY) ** 2))
			#print "Nearest player (path destination)"
			#print iEndX, iEndY
			#print "---"
			#print "Absolute distance:"
			#print fMinDistance
			#print "-----"

			# Now we draw an invisible line, plot by plot, one plot wide, from
			# the current start to the nearest start, converting peaks along the
			# way in to hills, and lakes in to flatlands, until a path opens.

			# Bulldoze the path until it opens!
			startPlot = map.plot(iStartX, iStartY)
			endPlot = map.plot(iEndX, iEndY)
			if abs(iEndY-iStartY) < abs(iEndX-iStartX):
				# line is closer to horizontal
				if iStartX > iEndX:
					startX, startY, endX, endY = iEndX, iEndY, iStartX, iStartY # swap start and end
					bReverseFlag = True
					#print "Path reversed, working from the end plot."
				else: # don't swap
					startX, startY, endX, endY = iStartX, iStartY, iEndX, iEndY
					bReverseFlag = False
					#print "Path not reversed."
				dx = endX-startX
				dy = endY-startY
				if dx == 0 or dy == 0:
					slope = 0
				else:
					slope = float(dy)/float(dx)
				#print("Slope: ", slope)
				y = startY
				for x in range(startX, endX):
					#print "Checking plot"
					#print x, int(round(y))
					#print "---"
					if map.isPlot(x, int(round(y))):
						i = map.plotNum(x, int(round(y)))
						pPlot = map.plotByIndex(i)
						y += slope
						#print("y plus slope: ", y)
						if pPlot.isHills() or pPlot.isFlatlands(): continue # on to next plot!
						if pPlot.isPeak():
							print "Peak found! Bulldozing this plot."
							#print "---"
							pPlot.setPlotType(PlotTypes.PLOT_HILLS, true, true)
							if bReverseFlag:
								currentDistance = map.calculatePathDistance(pPlot, startPlot)
							else:
								currentDistance = map.calculatePathDistance(pPlot, endPlot)
							if currentDistance != -1: # The path has been opened!
								print "Pocket successfully opened!"
								print "-----"
								break
						elif pPlot.isWater():
							print "Lake found! Filling in this plot."
							#print "---"
							pPlot.setPlotType(PlotTypes.PLOT_LAND, true, true)
							pPlot.setTerrainType(terrainPlains, true, true)
							if pPlot.getBonusType(-1) != -1:
								#print "########################"
								#print "A sea-based Bonus is now present on the land! EEK!"
								#print "########################"
								pPlot.setBonusType(-1)
								#print "OK, nevermind. The resource has been removed."
								#print "########################"
							if bReverseFlag:
								currentDistance = map.calculatePathDistance(pPlot, startPlot)
							else:
								currentDistance = map.calculatePathDistance(pPlot, endPlot)
							if currentDistance != -1: # The path has been opened!
								print "Pocket successfully opened!"
								print "-----"
								break

			else:
				# line is closer to vertical
				if iStartY > iEndY:
					startX, startY, endX, endY = iEndX, iEndY, iStartX, iStartY # swap start and end
					bReverseFlag = True
					#print "Path reversed, working from the end plot."
				else: # don't swap
					startX, startY, endX, endY = iStartX, iStartY, iEndX, iEndY
					bReverseFlag = False
					#print "Path not reversed."
				dx, dy = endX-startX, endY-startY
				if dx == 0 or dy == 0:
					slope = 0
				else:
					slope = float(dx)/float(dy)
				#print("Slope: ", slope)
				x = startX
				for y in range(startY, endY+1):
					#print "Checking plot"
					#print int(round(x)), y
					#print "---"
					if map.isPlot(int(round(x)), y):
						i = map.plotNum(int(round(x)), y)
						pPlot = map.plotByIndex(i)
						x += slope
						#print("x plus slope: ", x)
						if pPlot.isHills() or pPlot.isFlatlands(): continue # on to next plot!
						if pPlot.isPeak():
							print "Peak found! Bulldozing this plot."
							#print "---"
							pPlot.setPlotType(PlotTypes.PLOT_HILLS, true, true)
							if bReverseFlag:
								currentDistance = map.calculatePathDistance(pPlot, startPlot)
							else:
								currentDistance = map.calculatePathDistance(pPlot, endPlot)
							if currentDistance != -1: # The path has been opened!
								print "Pocket successfully opened!"
								print "-----"
								break
						elif pPlot.isWater():
							print "Lake found! Filling in this plot."
							#print "---"
							pPlot.setPlotType(PlotTypes.PLOT_LAND, true, true)
							pPlot.setTerrainType(terrainPlains, true, true)
							if pPlot.getBonusType(-1) != -1:
								#print "########################"
								#print "A sea-based Bonus is now present on the land! EEK!"
								#print "########################"
								pPlot.setBonusType(-1)
								#print "OK, nevermind. The resource has been removed."
								#print "########################"
							if bReverseFlag:
								currentDistance = map.calculatePathDistance(pPlot, startPlot)
							else:
								currentDistance = map.calculatePathDistance(pPlot, endPlot)
							if currentDistance != -1: # The path has been opened!
								print "Pocket successfully opened!"
								print "-----"
								break

			# Now that all the pathing for this player is resolved, set the start plot.
			start_plots.append([iStartX, iStartY])
			player.setStartingPlot(sPlot, true)

		# All done!
		print "**********"
		print "All start plots assigned!"
		print "**********"
		return None
