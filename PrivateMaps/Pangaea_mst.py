#
#	FILE:	 Pangaea_mst.py
#	AUTHOR:  Bob Thomas (Sirian)
#	CONTRIB: Soren Johnson, Andy Szybalski
#	PURPOSE: Global map script - Simulates a Pan-Earth SuperContinent
#-----------------------------------------------------------------------------
#	Copyright (c) 2005 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#   Script modified for compatibility with MapScriptTools.
#
#   1.1.0    Terkhen   12/10/2016
#   - Added, compatibility with MapScriptTools
#   - Added, compatibility with 'Planetfall'
#   - Added, compatibility with 'Mars Now!'
#   - Added, save/load map options.
#   - Added, compatibility with RandomMap.
#   - Added, tubular wrapping.
#   - Added, resource balancement map option.
#   - Added, expanded coastal waters map option (like in Civilization V)
#   - Added, team start map option
#   - Added [Mars Now!], new map option: 'Sands of Mars'/'Terraformed Mars'
#   - Added, Marsh terrain, if supported by mod
#   - Added, Deep Ocean terrain, if supported by mod
#   - Added, rivers from lakes
#   - Added, Map Regions ( BigDent, BigBog, ElementalQuarter, LostIsle )
#   - Added, Map Features ( Kelp, HauntedLands, CrystalPlains )
#   - Changed, use TXT strings instead of hardcoded ones.
#   - Changed, use grid definitions from the active mod instead of using hardcoded ones.


from CvPythonExtensions import *
import CvMapGeneratorUtil
from CvMapGeneratorUtil import HintedWorld
import math

map = CyMap()
gc = CyGlobalContext()


################################################################
## MapScriptTools Interface by Temudjin                    START
################################################################

import MapScriptTools as mst
balancer = mst.bonusBalancer

def getVersion():
	return "1.1.0_mst"

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_PANGAEA_DESCR"


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
	global mapOptionShoreline, mapOptionResources
	global mapOptionWorldShape, mapOptionCoastalWaters, mapOptionTeamStart, mapOptionMarsTheme

	# Options chosen in Random Map
	mapOptionWorldShape = moWorldShape
	mapOptionResources = moResources
	mapOptionCoastalWaters = moCoastalWaters
	mapOptionTeamStart = moTeamStart
	mapOptionMarsTheme = moMarsTheme

	# All other options are chosen randomly.
	mapOptionShoreline = 0 # 0 means random for this game option.

# #################################################################################################
# ######## beforeInit() - Starts the map-generation process, called after the map-options are known
# ######## - map dimensions, latitudes and wrapping status are not known yet
# ######## - handle map specific options
# #################################################################################################
def beforeInit():
	print "-- beforeInit()"
	# Selected map options
	global mapOptionShoreline, mapOptionResources
	global mapOptionWorldShape, mapOptionCoastalWaters, mapOptionTeamStart, mapOptionMarsTheme
	mapOptionShoreline = map.getCustomMapOption(2)
	mapOptionWorldShape = map.getCustomMapOption(0)
	mapOptionResources = map.getCustomMapOption(1)
	mapOptionCoastalWaters = mst.iif(mst.bPfall, None, map.getCustomMapOption(3))
	mapOptionTeamStart = mst.iif(mst.bMars, None, map.getCustomMapOption( mst.iif(mst.bPfall, 3, 4) ))
	mapOptionMarsTheme = mst.iif(mst.bMars, map.getCustomMapOption(4), None)

# #######################################################################################
# ######## beforeGeneration() - Called from system after user input is finished
# ######## - define your latitude formula, get the map-version
# ######## - create map options info string
# ######## - initialize the MapScriptTools
# ######## - initialize MapScriptTools.BonusBalancer
# #######################################################################################
def beforeGeneration():
	print "-- beforeGeneration()"
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
	mst.getModInfo( getVersion(), None, mapInfo )
	# Initialize bonus balancing
	balancer.initialize( mapOptionResources == 1 ) # balance boni if desired, place missing boni, move minerals

	# Determine global Mars Theme
	mst.bSandsOfMars = (mapOptionMarsTheme == 0)

	# from original beforeGeneration():
	# Detect whether this game is primarily a team game or not. (1v1 treated as a team game!)
	# Team games, everybody starts on the coast. Otherwise, start anywhere on the pangaea.
	global isTeamGame
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	iTeams = gc.getGame().countCivTeamsEverAlive()
	if iPlayers >= iTeams * 2 or iPlayers == 2:
		isTeamGame = True
	else:
		isTeamGame = False


# Helper method for checking if the Pangaea is cohesive enough or not.
def isCohesive():
	cohesionConstant = 0.99
	biggest_area = map.findBiggestArea(false)
	iTotalLandPlots = map.getLandPlots()
	iBiggestAreaPlots = biggest_area.getNumTiles()
	return iBiggestAreaPlots >= cohesionConstant * iTotalLandPlots

# #######################################################################################
# ######## generatePlotTypes() - Called from system after beforeGeneration()
# ######## - FIRST STAGE in 'Generate Map'
# ######## - creates an array of plots (ocean, land, hills, peak) in the map dimensions
# #######################################################################################
def generatePlotTypes():
	'''
	Regional Variables Key:

	iWaterPercent,
	iRegionWidth, iRegionHeight,
	iRegionWestX, iRegionSouthY,
	iRegionGrain, iRegionHillsGrain,
	iRegionPlotFlags, iRegionTerrainFlags,
	iRegionFracXExp, iRegionFracYExp,
	bStrip, strip,
	rift_grain, has_center_rift,
	invert_heights
	'''
	NiTextOut("Setting Plot Types (Python Pangaea) ...")
	global pangaea_type
	mapgen = CyMapGenerator()
	dice = gc.getGame().getMapRand()
	hinted_world = PangaeaHintedWorld()
	fractal_world = PangaeaMultilayeredFractal()

	# Get user input.
	userInputLandmass = mapOptionShoreline

	# Implement Pangaea by Type
	if userInputLandmass == 3: # Solid
		# Roll for type selection.
		typeRoll = dice.get(3, "PlotGen Chooser - Pangaea PYTHON")
		# Solid Shoreline cohesion check and catch - patched Dec 30, 2005 - Sirian
		# Error catching for non-cohesive results.
		cohesive = False
		while not cohesive:
			plotTypes = []
			if typeRoll == 2:
				plotTypes = hinted_world.generateAndysHintedPangaea()
			else:
				plotTypes = hinted_world.generateSorensHintedPangaea()
			mapgen.setPlotTypes(plotTypes)
			cohesive = isCohesive()
		return plotTypes

	elif userInputLandmass == 2: # Pressed
		# Roll for type selection.
		typeRoll = dice.get(3, "PlotGen Chooser - Pangaea PYTHON")
		if typeRoll == 1:
			pangaea_type = 1
		else:
			pangaea_type = 2
		return fractal_world.generatePlotsByRegion(pangaea_type)

	elif userInputLandmass == 1: # Natural
		pangaea_type = 0
		return fractal_world.generatePlotsByRegion(pangaea_type)

	else: # Random
		global terrainRoll
		terrainRoll = dice.get(10, "PlotGen Chooser - Pangaea PYTHON")
		# 0-3 = Natural
		# 4 = Pressed, Equatorial
		# 5,6 = Pressed, Polar
		# 7,8 = Solid, Irregular
		# 9 = Solid, Round

		if terrainRoll > 6:
			# Solid Shoreline cohesion check and catch - patched Dec 30, 2005 - Sirian
			cohesive = False
			while not cohesive:
				plotTypes = []
				if terrainRoll == 9:
					plotTypes = hinted_world.generateAndysHintedPangaea()
				else:
					plotTypes = hinted_world.generateSorensHintedPangaea()
				mapgen.setPlotTypes(plotTypes)
				cohesive = isCohesive()
			return plotTypes

		elif terrainRoll == 5 or terrainRoll == 6:
			pangaea_type = 2
			return fractal_world.generatePlotsByRegion(pangaea_type)
		elif terrainRoll == 4:
			pangaea_type = 1
			return fractal_world.generatePlotsByRegion(pangaea_type)
		else:
			pangaea_type = 0
			return fractal_world.generatePlotsByRegion(pangaea_type)

# ######################################################################################
# ######## generateTerrainTypes() - Called from system after generatePlotTypes()
# ######## - SECOND STAGE in 'Generate Map'
# ######## - creates an array of terrains (desert,plains,grass,...) in the map dimensions
# #######################################################################################
def generateTerrainTypes():
	# Run a check for cohesion failure.
	# If the largest land area contains less than 80% of the land (Natural/Pressed),
	# or less than 90% of the land (Solid), add a third layer of fractal terrain
	# to try to link the main landmasses in to a true Pangaea.
	dice = gc.getGame().getMapRand()
	iHorzFlags = CyFractal.FracVals.FRAC_WRAP_X + CyFractal.FracVals.FRAC_POLAR
	biggest_area = map.findBiggestArea(false)
	global terrainRoll
	userInputShoreline = mapOptionShoreline
	iTotalLandPlots = map.getLandPlots()
	iBiggestAreaPlots = biggest_area.getNumTiles()
	#print("Total Land: ", iTotalLandPlots, " Main Landmass Plots: ", iBiggestAreaPlots)
	if (userInputShoreline == 1 or userInputShoreline == 2 or (userInputShoreline == 0 and terrainRoll < 7)) and iBiggestAreaPlots < 0.8 * iTotalLandPlots:
		global pangaea_type
		print("Total Land: ", iTotalLandPlots, " Main Landmass Plots: ", iBiggestAreaPlots)
		print "Cohesion failure! Attempting to remedy..."
		#print("Pangaea Type: ", pangaea_type)
		iW = map.getGridWidth()
		iH = map.getGridHeight()
		iWestX = int(0.3 * iW)
		eastX = int(0.7 * iW)
		southLat = 0.4
		northLat = 0.6
		if pangaea_type == 0: # Natural
			global shiftRoll
			#print("Shift Roll: ", shiftRoll)
			if shiftRoll == 1:
				southLat += 0.075
				northLat += 0.075
			else:
				southLat -= 0.075
				northLat -= 0.075
		elif pangaea_type == 2: # Pressed Polar
			global polarShiftRoll
			#print("Polar Shift Roll: ", polarShiftRoll)
			if polarShiftRoll == 1:
				southLat += 0.175
				northLat += 0.175
			else:
				southLat -= 0.175
				northLat -= 0.175
		else: # Pressed Equatorial
			pass
		iSouthY = int(southLat * iH)
		northY = int(northLat * iH)
		iRegionWidth = eastX - iWestX + 1
		iRegionHeight = northY - iSouthY + 1

		# Init the plot types array and the regional fractals
		plotTypes = [] # reinit the array for each pass
		plotTypes = [PlotTypes.PLOT_OCEAN] * (iRegionWidth*iRegionHeight)
		regionContinentsFrac = CyFractal()
		regionHillsFrac = CyFractal()
		regionPeaksFrac = CyFractal()
		regionContinentsFrac.fracInit(iRegionWidth, iRegionHeight, 1, dice, iHorzFlags, 7, 5)
		regionHillsFrac.fracInit(iRegionWidth, iRegionHeight, 3, dice, iHorzFlags, 7, 5)
		regionPeaksFrac.fracInit(iRegionWidth, iRegionHeight, 4, dice, iHorzFlags, 7, 5)

		iWaterThreshold = regionContinentsFrac.getHeightFromPercent(40)
		iHillsBottom1 = regionHillsFrac.getHeightFromPercent(20)
		iHillsTop1 = regionHillsFrac.getHeightFromPercent(30)
		iHillsBottom2 = regionHillsFrac.getHeightFromPercent(70)
		iHillsTop2 = regionHillsFrac.getHeightFromPercent(80)
		iPeakThreshold = regionPeaksFrac.getHeightFromPercent(25)

		# Loop through the region's plots
		for x in range(iRegionWidth):
			for y in range(iRegionHeight):
				i = y*iRegionWidth + x
				val = regionContinentsFrac.getHeight(x,y)
				if val <= iWaterThreshold: pass
				else:
					hillVal = regionHillsFrac.getHeight(x,y)
					if ((hillVal >= iHillsBottom1 and hillVal <= iHillsTop1) or (hillVal >= iHillsBottom2 and hillVal <= iHillsTop2)):
						peakVal = regionPeaksFrac.getHeight(x,y)
						if (peakVal <= iPeakThreshold):
							plotTypes[i] = PlotTypes.PLOT_PEAK
						else:
							plotTypes[i] = PlotTypes.PLOT_HILLS
					else:
						plotTypes[i] = PlotTypes.PLOT_LAND

		for x in range(iRegionWidth):
			wholeworldX = x + iWestX
			for y in range(iRegionHeight):
				i = y*iRegionWidth + x
				if plotTypes[i] == PlotTypes.PLOT_OCEAN: continue # Not merging water!
				wholeworldY = y + iSouthY
				# print("Changing water plot at ", wholeworldX, wholeworldY, " to ", plotTypes[i])
				iWorld = wholeworldY*iW + wholeworldX
				pPlot = map.plotByIndex(iWorld)
				if pPlot.isWater():	# Only merging new land plots over old water plots.
					pPlot.setPlotType(plotTypes[i], true, true)

		# Smooth any graphical glitches these changes may have produced.
		map.recalculateAreas()

	# Planetfall: more highlands
	mst.planetFallMap.buildPfallHighlands()
	# Prettify map: Connect small islands
	mst.mapPrettifier.bulkifyIslands()
	# Prettify map: most coastal peaks -> hills
	mst.mapPrettifier.hillifyCoast()
	# Now generate Terrain.
	NiTextOut("Generating Terrain (Python Pangaea) ...")
	if mst.bMars:
		# There are two possible scenarios for 'Mars Now!':
		# either water is converted to desert or not
		iDesert = mst.iif( mst.bSandsOfMars, 16, 32 )
		terrainGen = mst.MST_TerrainGenerator_Mars( iDesert )
	else:
		terrainGen = mst.MST_TerrainGenerator()
	terrainTypes = terrainGen.generateTerrain()
	return terrainTypes

# #######################################################################################
# ######## addRivers() - Called from system after generateTerrainTypes()
# ######## - THIRD STAGE in 'Generate Map'
# ######## - puts rivers on the map
# #######################################################################################
def addRivers():
	print "-- addRivers()"
	# Generate marsh-terrain
	mst.marshMaker.convertTerrain()

	# Expand coastal waters
	if mapOptionCoastalWaters == 1:
		mst.mapPrettifier.expandifyCoast()

	# Build between 0..2 mountain-ranges.
	mst.mapRegions.buildBigDents()
	# Build between 0..2 bog-regions.
	mst.mapRegions.buildBigBogs()

	# Generate DeepOcean-terrain if mod allows for it
	mst.deepOcean.buildDeepOcean()

	# Prettify the map - create better connected deserts and plains
	if not mst.bPfall:
		mst.mapPrettifier.lumpifyTerrain( mst.etDesert, mst.etPlains, mst.etGrass )
		if not mst.bMars:
			mst.mapPrettifier.lumpifyTerrain( mst.etPlains, mst.etDesert, mst.etGrass )

	# No standard rivers on Mars
	if not mst.bMars:
		# Put rivers on the map.
		CyPythonMgr().allowDefaultImpl()

	# Put rivers on small islands
	mst.riverMaker.islandRivers()

# #######################################################################################
# ######## addLakes() - Called from system after addRivers()
# ######## - FOURTH STAGE in 'Generate Map'
# ######## - puts lakes on the map
# #######################################################################################
def addLakes():
	print "-- addLakes()"
	if not mst.bMars:
		CyPythonMgr().allowDefaultImpl()

# #######################################################################################
# ######## addFeatures() - Called from system after addLakes()
# ######## - FIFTH STAGE in 'Generate Map'
# ######## - puts features on the map
# #######################################################################################
def addFeatures():
	NiTextOut("Adding Features (Python Pangaea) ...")
	# Prettify map - connect some small adjacent lakes
	mst.mapPrettifier.connectifyLakes()
	# Sprout rivers from lakes.
	mst.riverMaker.buildRiversFromLake(None, 40, 1, 2)  # all lakes, 40% chance, 1 rivers, lakesize>=2

	featuregen = mst.MST_FeatureGenerator()
	featuregen.addFeatures()

	# Prettify the map - transform coastal volcanos; default: 66% chance
	mst.mapPrettifier.beautifyVolcanos()
	# Mars Now!: lumpify sandstorms
	if mst.bMars: mst.mapPrettifier.lumpifyTerrain(mst.efSandStorm, FeatureTypes.NO_FEATURE)
	# Planetfall: handle shelves and trenches
	if mst.bPfall: mst.planetFallMap.buildPfallOcean()

	# FFH: build ElementalQuarter; default: 5% chance
	mst.mapRegions.buildElementalQuarter()

	return 0

# ############################################################################################
# ######## normalizeStartingPlotLocations() - Called from system after starting-plot selection
# ######## - FIRST STAGE in 'Normalize Starting-Plots'
# ######## - change assignments to starting-plots
# ############################################################################################
def normalizeStartingPlotLocations():
	print "-- normalizeStartingPlotLocations()"

	# build Lost Isle
	# - this region needs to be placed after starting-plots are first assigned. Chance increased in Pangaea to 40%.
	mst.mapRegions.buildLostIsle( chance=40, minDist=7, bAliens=mst.choose(33,True,False) )

	if mst.bMars or mapOptionTeamStart == 0:
		# Mars Now! uses no teams. by default civ places teams near to each other
		CyPythonMgr().allowDefaultImpl()
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
	if not mst.bMars:
		CyPythonMgr().allowDefaultImpl()

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
	if not (mst.bPfall or mst.bMars):
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
	if not (mst.bPfall or mst.bMars):
		CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeAddExtras() - Called from system after normalizeAddGoodTerrain()
# ######## - NINTH and LAST STAGE in 'Normalize Starting-Plots'
# ######## - last chance to adjust starting-plots
# ######## - called before startHumansOnSameTile(), which is the last map-function so called
# ############################################################################################
def normalizeAddExtras():
	print "-- normalizeAddExtras()"
	# Balance boni, place missing boni, move minerals
	balancer.normalizeAddExtras()

	# Do the default housekeeping
	CyPythonMgr().allowDefaultImpl()

	# Make sure marshes are on flatlands
	mst.marshMaker.normalizeMarshes()
	# Give extras to special regions
	mst.mapRegions.addRegionExtras()
	# Place special features on map
	mst.featurePlacer.placeFeatures()
	# Kill ice on warm edges
	mst.mapPrettifier.deIcifyEdges()

	# Print plotMap and differencePlotMap
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

# ############################################################################
# ######## minStartingDistanceModifier() - Called from system at various times
# ######## - FIRST STAGE in 'Select Starting-Plots'
# ######## - adjust starting-plot distances
# ############################################################################
def minStartingDistanceModifier():
	if mst.bPfall: return -25
	return 0

################################################################
## Custom Map Option Interface by Temudjin                 START
################################################################
def setCustomOptions():
	""" Set all custom options in one place """
	global op	# { optionID: Name, OptionList, Default, RandomOpt }

	# Initialize options to the default values.
	lMapOptions = [1, 0, 0, 0, 0]

	# Try to read map options from the cfgFile.
	mst.mapOptionsStorage.initialize(lMapOptions, 'Pangaea')
	lMapOptions = mst.mapOptionsStorage.readConfig()

	optionShorelines = [ "TXT_KEY_MAP_PANGAEA_RANDOM", "TXT_KEY_MAP_PANGAEA_NATURAL",
	                     "TXT_KEY_MAP_PANGAEA_PRESSED", "TXT_KEY_MAP_PANGAEA_SOLID" ]
	optionShape =      [ "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_FLAT", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_CYLINDRICAL", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_TUBULAR", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_TOROIDAL" ]
	op = {
		0: ["TXT_KEY_MAP_SCRIPT_WORLD_WRAP", optionShape, lMapOptions[0], True],
		1: ["TXT_KEY_MAP_RESOURCES", ["TXT_KEY_MAP_RESOURCES_STANDARD", "TXT_KEY_MAP_RESOURCES_BALANCED"], lMapOptions[1], True],
		2: ["TXT_KEY_MAP_PANGAEA_SHORELINE", optionShorelines, lMapOptions[2], False],
		3: ["TXT_KEY_MAP_COASTS",  ["TXT_KEY_MAP_COASTS_STANDARD", "TXT_KEY_MAP_COASTS_EXPANDED"], lMapOptions[3], True],
		"Hidden": 2
	}
	if mst.bPfall:
		op[3] = ["TXT_KEY_MAP_TEAM_START", ["TXT_KEY_MAP_TEAM_START_NEIGHBORS", "TXT_KEY_MAP_TEAM_START_SEPARATED", "TXT_KEY_MAP_TEAM_START_RANDOM"], lMapOptions[3], False]
	elif mst.bMars:
		op[4] = ["TXT_KEY_MAP_MARS_THEME", ["TXT_KEY_MAP_MARS_THEME_SANDS_OF_MARS", "TXT_KEY_MAP_MARS_THEME_TERRAFORMED_MARS"], lMapOptions[4], False]
	else:
		op[4] = ["TXT_KEY_MAP_TEAM_START", ["TXT_KEY_MAP_TEAM_START_NEIGHBORS", "TXT_KEY_MAP_TEAM_START_SEPARATED", "TXT_KEY_MAP_TEAM_START_RANDOM"], lMapOptions[4], False]
	mst.printDict(op,"Pangaea Map Options:")

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
	return True

def isSeaLevelMap():
	"""	Uses the Sea Level options """
	return True

def getTopLatitude():
	""" Default is 90. 75 is past the Arctic Circle """
	return 90

def getBottomLatitude():
	""" Default is -90. -75 is past the Antartic Circle """
	return -90

def getWrapX():
	return mapOptionWorldShape in [1, 3]

def getWrapY():
	return mapOptionWorldShape in [2, 3]

##########

def getGridSize(argsList):
	if (argsList[0] == -1): return []			# (-1,) is passed to function on loads

	# Reduce grid sizes by one level.
	[eWorldSize] = argsList
	iWidth = 0
	iHeight = 0
	if eWorldSize >= 1:
		iWidth = CyGlobalContext().getWorldInfo(eWorldSize - 1).getGridWidth()
		iHeight = CyGlobalContext().getWorldInfo(eWorldSize - 1).getGridHeight()
	else:
		# Scale down the smallest world size
		iScale = 0.8
		iWidth = int(math.ceil(CyGlobalContext().getWorldInfo(0).getGridWidth() * iScale))
		iHeight = int(math.ceil(CyGlobalContext().getWorldInfo(0).getGridHeight() * iScale))

	return iWidth, iHeight

class PangaeaHintedWorld:
	def generateSorensHintedPangaea(self):
		NiTextOut("Setting Plot Types (Python Pangaea) ...")
		global hinted_world
		hinted_world = HintedWorld(8,4)

		mapRand = gc.getGame().getMapRand()

		for y in range(hinted_world.h):
			for x in range(hinted_world.w):
				if x in (0, hinted_world.w-1) or y in (0, hinted_world.h-1):
					hinted_world.setValue(x,y,0)
				else:
					hinted_world.setValue(x,y,200 + mapRand.get(55, "Plot Types - Pangaea PYTHON"))

		hinted_world.setValue(1, 1 + mapRand.get(3, "Plot Types - Pangaea PYTHON"), mapRand.get(64, "Plot Types - Pangaea PYTHON"))
		hinted_world.setValue(2 + mapRand.get(2, "Plot Types - Pangaea PYTHON"), 1 + mapRand.get(3, "Plot Types - Pangaea PYTHON"), mapRand.get(64, "Plot Types - Pangaea PYTHON"))
		hinted_world.setValue(4 + mapRand.get(2, "Plot Types - Pangaea PYTHON"), 1 + mapRand.get(3, "Plot Types - Pangaea PYTHON"), mapRand.get(64, "Plot Types - Pangaea PYTHON"))
		hinted_world.setValue(6, 1 + mapRand.get(3, "Plot Types - Pangaea PYTHON"), mapRand.get(64, "Plot Types - Pangaea PYTHON"))
		if (mapRand.get(2, "Plot Types - Pangaea PYTHON") == 0):
			hinted_world.setValue(2, 1 + mapRand.get(3, "Plot Types - Pangaea PYTHON"), mapRand.get(64, "Plot Types - Pangaea PYTHON"))
		else:
			hinted_world.setValue(5, 1 + mapRand.get(3, "Plot Types - Pangaea PYTHON"), mapRand.get(64, "Plot Types - Pangaea PYTHON"))

		hinted_world.buildAllContinents()
		return hinted_world.generatePlotTypes(shift_plot_types=True)

	def generateAndysHintedPangaea(self):
		NiTextOut("Setting Plot Types (Python Pangaea Hinted) ...")
		global hinted_world
		hinted_world = HintedWorld(16,8)

		mapRand = gc.getGame().getMapRand()

		numBlocks = hinted_world.w * hinted_world.h
		numBlocksLand = int(numBlocks*0.33)
		cont = hinted_world.addContinent(numBlocksLand,mapRand.get(5, "Generate Plot Types PYTHON")+4,mapRand.get(3, "Generate Plot Types PYTHON")+2)
		if not cont:
			# Couldn't create continent! Reverting to Soren's Hinted Pangaea
			return self.generateSorensHintedPangaea()
		else:
			for x in range(hinted_world.w):
				for y in (0, hinted_world.h - 1):
					hinted_world.setValue(x,y, 1) # force ocean at poles
			hinted_world.buildAllContinents()
			return hinted_world.generatePlotTypes(shift_plot_types=True)

class PangaeaMultilayeredFractal(CvMapGeneratorUtil.MultilayeredFractal):
	# Subclass. Only the controlling function overridden in this case.
	def generatePlotsByRegion(self, pangaea_type):
		# Sirian's MultilayeredFractal class, controlling function.
		# You -MUST- customize this function for each use of the class.
		#
		# The following grain matrix is specific to Pangaea.py
		sizekey = self.map.getWorldSize()
		sizevalues = {
			WorldSizeTypes.WORLDSIZE_DUEL:      3,
			WorldSizeTypes.WORLDSIZE_TINY:      3,
			WorldSizeTypes.WORLDSIZE_SMALL:     4,
			WorldSizeTypes.WORLDSIZE_STANDARD:  4,
			WorldSizeTypes.WORLDSIZE_LARGE:     4,
			WorldSizeTypes.WORLDSIZE_HUGE:      5
			}
		grain = sizevalues[sizekey]

		# Sea Level adjustment (from user input), limited to value of 5%.
		sea = self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()
		sea = min(sea, 5)
		sea = max(sea, -5)

		# The following regions are specific to Pangaea.py
		mainWestLon = 0.2
		mainEastLon = 0.8
		mainSouthLat = 0.2
		mainNorthLat = 0.8
		subcontinentDimension = 0.4
		bSouthwardShift = False

		# Define the three types.
		if pangaea_type == 2: # Pressed Polar
			numSubcontinents = 3
			# Place mainland near north or south pole?
			global polarShiftRoll
			polarShiftRoll = self.dice.get(2, "Shift - Pangaea PYTHON")
			if polarShiftRoll == 1:
				mainNorthLat += 0.175
				mainSouthLat += 0.175
				# Define potential subcontinent slots (regional definitions).
				# List values: [westLon, southLat, vertRange, horzRange, southShift]
				scValues = [[0.05, 0.375, 0.2, 0.0, 0],
				            [0.55, 0.375, 0.2, 0.0, 0],
				            [0.1, 0.225, 0.0, 0.15, 0],
				            [0.3, 0.225, 0.0, 0.15, 0]
				            ]
			else:
				mainNorthLat -= 0.175
				mainSouthLat -= 0.175
				# List values: [westLon, southLat, vertRange, horzRange, southShift]
				scValues = [[0.05, 0.025, 0.2, 0.0, 0],
				            [0.55, 0.025, 0.2, 0.0, 0],
				            [0.1, 0.375, 0.0, 0.15, 0],
				            [0.3, 0.375, 0.0, 0.15, 0]
				            ]
		elif pangaea_type == 1: # Pressed Equatorial
			# Define potential subcontinent slots (regional definitions).
			equRoll = self.dice.get(4, "Subcontinents - Pangaea PYTHON")
			if equRoll == 3: equRoll = 1 # 50% chance result = 1
			numSubcontinents = 2 + equRoll
			# List values: [westLon, southLat, vertRange, horzRange, southShift]
			scValues = [[0.05, 0.2, 0.2, 0.0, 0.0],
			            [0.55, 0.2, 0.2, 0.0, 0.0],
			            [0.2, 0.05, 0.0, 0.2, 0.0],
			            [0.2, 0.55, 0.0, 0.2, 0.0]
			            ]
		else: # Natural
			subcontinentDimension = 0.3
			# Shift mainland north or south?
			global shiftRoll
			shiftRoll = self.dice.get(2, "Shift - Pangaea PYTHON")
			if shiftRoll == 1:
				mainNorthLat += 0.075
				mainSouthLat += 0.075
			else:
				mainNorthLat -= 0.075
				mainSouthLat -= 0.075
				bSouthwardShift = True
			# Define potential subcontinent slots (regional definitions).
			numSubcontinents = 4 + self.dice.get(3, "Subcontinents - Pangaea PYTHON")
			# List values: [westLon, southLat, vertRange, horzRange, southShift]
			scValues = [[0.05, 0.575, 0.0, 0.0, 0.15],
			            [0.05, 0.275, 0.0, 0.0, 0.15],
			            [0.2, 0.175, 0.0, 0.0, 0.15],
			            [0.5, 0.175, 0.0, 0.0, 0.15],
			            [0.65, 0.575, 0.0, 0.0, 0.15],
			            [0.65, 0.275, 0.0, 0.0, 0.15],
			            [0.2, 0.675, 0.0, 0.0, 0.15],
			            [0.5, 0.675, 0.0, 0.0, 0.15]
			            ]

		# Generate the main land mass, first pass (to vary shape).
		mainWestX = int(self.iW * mainWestLon)
		mainEastX = int(self.iW * mainEastLon)
		mainNorthY = int(self.iH * mainNorthLat)
		mainSouthY = int(self.iH * mainSouthLat)
		mainWidth = mainEastX - mainWestX + 1
		mainHeight = mainNorthY - mainSouthY + 1

		mainWater = 55+sea

		self.generatePlotsInRegion(mainWater,
		                           mainWidth, mainHeight,
		                           mainWestX, mainSouthY,
		                           2, grain,
		                           self.iHorzFlags, self.iTerrainFlags,
		                           -1, -1,
		                           True, 15,
		                           2, False,
		                           False
		                           )

		# Second pass (to ensure cohesion).
		second_layerHeight = mainHeight/2
		second_layerWestX = mainWestX + mainWidth/10
		second_layerEastX = mainEastX - mainWidth/10
		second_layerWidth = second_layerEastX - second_layerWestX + 1
		second_layerNorthY = mainNorthY - mainHeight/4
		second_layerSouthY = mainSouthY + mainHeight/4

		second_layerWater = 60+sea

		self.generatePlotsInRegion(second_layerWater,
		                           second_layerWidth, second_layerHeight,
		                           second_layerWestX, second_layerSouthY,
		                           1, grain,
		                           self.iHorzFlags, self.iTerrainFlags,
		                           -1, -1,
		                           True, 15,
		                           2, False,
		                           False
		                           )

		# Add subcontinents.
		# Subcontinents can be akin to India/Alaska, Europe, or the East Indies.
		while numSubcontinents > 0:
			# Choose a slot for this subcontinent.
			if len(scValues) > 1:
				scIndex = self.dice.get(len(scValues), "Subcontinent Placement - Pangaea PYTHON")
			else:
				scIndex = 0
			[scWestLon, scSouthLat, scVertRange, scHorzRange, scSouthShift] = scValues[scIndex]
			scWidth = int(subcontinentDimension * self.iW)
			scHeight = int(subcontinentDimension * self.iH)
			scHorzShift = 0; scVertShift = 0
			if scHorzRange > 0.0:
				scHorzShift = self.dice.get(int(self.iW * scHorzRange), "Subcontinent Variance - Terra PYTHON")
			if scVertRange > 0.0:
				scVertShift = self.dice.get(int(self.iW * scVertRange), "Subcontinent Variance - Terra PYTHON")
			scWestX = int(self.iW * scWestLon) + scHorzShift
			scEastX = scWestX + scWidth
			if scEastX >= self.iW: # Trouble! Off the right hand edge!
				while scEastX >= self.iW:
					scWidth -= 1
					scEastX = scWestX + scWidth
			scSouthY = int(self.iH * scSouthLat) + scVertShift
			# Check for southward shift.
			if bSouthwardShift:
				scSouthY -= int(self.iH * scSouthShift)
			scNorthY = scSouthY + scHeight
			if scNorthY >= self.iH: # Trouble! Off the top edge!
				while scNorthY >= self.iH:
					scHeight -= 1
					scNorthY = scSouthY + scHeight

			scShape = self.dice.get(5, "Subcontinent Shape - Terra PYTHON")
			if scShape > 1: # Regular subcontinent.
				scWater = 55+sea; scGrain = 1; scRift = -1
			elif scShape == 1: # Irregular subcontinent.
				scWater = 66+sea; scGrain = 2; scRift = 2
			else: # scShape == 0, Archipelago subcontinent.
				scWater = 77+sea; scGrain = grain; scRift = -1

			self.generatePlotsInRegion(scWater,
			                           scWidth, scHeight,
			                           scWestX, scSouthY,
			                           scGrain, grain,
			                           self.iRoundFlags, self.iTerrainFlags,
			                           6, 6,
			                           True, 7,
			                           scRift, False,
			                           False
			                           )

			del scValues[scIndex]
			numSubcontinents -= 1

		# All regions have been processed. Plot Type generation completed.
		return self.wholeworldPlotTypes


def findStartingPlot(argsList):
	[playerID] = argsList

	def isValid(playerID, x, y):
		global isTeamGame
		pPlot = map.plot(x, y)

		if (pPlot.getArea() != map.findBiggestArea(False).getID()):
			return false

		if isTeamGame:
			pWaterArea = pPlot.waterArea()
			if (pWaterArea.isNone()):
				return false
			return not pWaterArea.isLake()
		else:
			return true

	return CvMapGeneratorUtil.findStartingPlot(playerID, isValid)
