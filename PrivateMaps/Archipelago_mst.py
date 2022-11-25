#
#	FILE:	 Archipelago_mst.py
#	AUTHOR:  Bob Thomas (Sirian)
#	CONTRIB: Soren Johnson
#	PURPOSE: Global map script - Generates a world full of random islands.
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
#   - Added, rivers on islands and from lakes
#   - Added, Map Regions ( BigDent, BigBog, ElementalQuarter, LostIsle )
#   - Added, Map Features ( Kelp, HauntedLands, CrystalPlains )
#   - Changed, use TXT strings instead of hardcoded ones.


from CvPythonExtensions import *
import CvMapGeneratorUtil

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
	return "TXT_KEY_MAP_SCRIPT_ARCHIPELAGO_DESCR"

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
	global mapOptionLandmass, mapOptionResources
	global mapOptionWorldShape, mapOptionCoastalWaters, mapOptionTeamStart, mapOptionMarsTheme

	# Options chosen in Random Map
	mapOptionWorldShape = moWorldShape
	mapOptionResources = moResources
	mapOptionCoastalWaters = moCoastalWaters
	mapOptionTeamStart = moTeamStart
	mapOptionMarsTheme = moMarsTheme

	# All other options are chosen randomly.
	mapOptionLandmass = gc.getGame().getMapRand().get(3, "Archipelago.randomMapBeforeInit(), mapOptionLandmass")

# #################################################################################################
# ######## beforeInit() - Starts the map-generation process, called after the map-options are known
# ######## - map dimensions, latitudes and wrapping status are not known yet
# ######## - handle map specific options
# #################################################################################################
def beforeInit():
	print "-- beforeInit()"
	# Selected map options
	global mapOptionLandmass, mapOptionResources
	global mapOptionWorldShape, mapOptionCoastalWaters, mapOptionTeamStart, mapOptionMarsTheme
	mapOptionLandmass = map.getCustomMapOption(2)
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

# #######################################################################################
# ######## generatePlotTypes() - Called from system after beforeGeneration()
# ######## - FIRST STAGE in 'Generate Map'
# ######## - creates an array of plots (ocean, land, hills, peak) in the map dimensions
# #######################################################################################
def generatePlotTypes():
	"Generates a very grainy world so we get lots of islands."
	fractal_world = ArchipelagoFractalWorld()
	NiTextOut("Setting Plot Types (Python Archipelago) ...")

	# Get user input.
	userInputLandmass = mapOptionLandmass

	if userInputLandmass == 2: # Tiny Islands
		fractal_world.initFractal(continent_grain = 5, rift_grain = -1, has_center_rift = False, polar = True)
		return fractal_world.generatePlotTypes(grain_amount = 4)

	elif userInputLandmass == 0: # Snaky Continents
		fractal_world.initFractal(continent_grain = 3, rift_grain = -1, has_center_rift = False, polar = True)
		return fractal_world.generatePlotTypes(grain_amount = 4)

	else: # Archipelago
		fractal_world.initFractal(continent_grain = 4, rift_grain = -1, has_center_rift = False, polar = True)
		return fractal_world.generatePlotTypes(grain_amount = 4)

# ######################################################################################
# ######## generateTerrainTypes() - Called from system after generatePlotTypes()
# ######## - SECOND STAGE in 'Generate Map'
# ######## - creates an array of terrains (desert,plains,grass,...) in the map dimensions
# #######################################################################################
def generateTerrainTypes():
	# Planetfall: more highlands
	mst.planetFallMap.buildPfallHighlands()
	# Prettify map: Connect small islands
	mst.mapPrettifier.bulkifyIslands()
	# Prettify map: most coastal peaks -> hills < Archipelago has its own methods for removing peaks on coast.
	# mst.mapPrettifier.hillifyCoast()
	# Generate terrain
	if mst.bMars:
		# There are two possible scenarios for 'Mars Now!': either water is converted to desert or not
		iDesert = mst.iif(mst.bSandsOfMars, 16, 32)
		terrainGen = mst.MST_TerrainGenerator_Mars(iDesert)
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

	# Build big dents with very small probability.
	mst.mapRegions.buildBigDents(1, 20)
	# Build big bogs with very small probability.
	mst.mapRegions.buildBigBogs(1, 20)

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
	NiTextOut("Adding Features (Python Archipelago) ...")
	# Original addFeatures:
	# Remove all peaks along the coasts, before adding Features, Bonuses, Goodies, etc.
	# The peaks were bisecting too many islands.
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	for plotIndex in range(iW * iH):
		pPlot = map.plotByIndex(plotIndex)
		if pPlot.isPeak() and pPlot.isCoastalLand():
			# If a peak is along the coast, change to hills and recalc.
			pPlot.setPlotType(PlotTypes.PLOT_HILLS, true, true)

	# Rest of the code:
	# connectifyLakes takes a lot of time due to Archipelago being mostly water. Given that it will not be useful in
	# nearly all cases, it has just been removed.
	# mst.mapPrettifier.connectifyLakes()
	# Sprout rivers from lakes.
	mst.riverMaker.buildRiversFromLake( None, 40, 1, 2 )	# all lakes, 40% chance, 1 rivers, lakesize>=2

	featuregen = mst.MST_FeatureGenerator()
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
	# - this region needs to be placed after starting-plots are first assigned. Chance increased in Archipelago to 66%.
	mst.mapRegions.buildLostIsle(chance = 66, minDist  =7, bAliens = mst.choose(33, True, False))

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
	global op  # { optionID: Name, OptionList, Default, RandomOpt }

	# Initialize options to the default values.
	lMapOptions = [1, 0, 1, 0, 0]

	# Try to read map options from the cfgFile.
	mst.mapOptionsStorage.initialize(lMapOptions, 'Archipelago')
	lMapOptions = mst.mapOptionsStorage.readConfig()

	optionLandmass = ["TXT_KEY_MAP_ARCHIPELAGO_LANDMASS_SNAKY", "TXT_KEY_MAP_ARCHIPELAGO_LANDMASS_ARCHIPELAGO", "TXT_KEY_MAP_ARCHIPELAGO_LANDMASS_TINY_ISLANDS"]
	optionShape = ["TXT_KEY_MAP_SCRIPT_WORLD_WRAP_FLAT", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_CYLINDRICAL", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_TUBULAR", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_TOROIDAL"]
	op = {
		0: ["TXT_KEY_MAP_SCRIPT_WORLD_WRAP", optionShape, lMapOptions[0], True],
		1: ["TXT_KEY_MAP_RESOURCES", ["TXT_KEY_MAP_RESOURCES_STANDARD", "TXT_KEY_MAP_RESOURCES_BALANCED"], lMapOptions[1], True],
		2: ["TXT_KEY_MAP_ARCHIPELAGO_LANDMASS_TYPE", optionLandmass, lMapOptions[2], False],
		3: ["TXT_KEY_MAP_COASTS", ["TXT_KEY_MAP_COASTS_STANDARD", "TXT_KEY_MAP_COASTS_EXPANDED"], lMapOptions[3], True],
		"Hidden": 2
	}
	if mst.bPfall:
		op[3] = ["TXT_KEY_MAP_TEAM_START", ["TXT_KEY_MAP_TEAM_START_NEIGHBORS", "TXT_KEY_MAP_TEAM_START_SEPARATED", "TXT_KEY_MAP_TEAM_START_RANDOM"], lMapOptions[3], False]
	elif mst.bMars:
		op[4] = ["TXT_KEY_MAP_MARS_THEME", ["TXT_KEY_MAP_MARS_THEME_SANDS_OF_MARS", "TXT_KEY_MAP_MARS_THEME_TERRAFORMED_MARS"], lMapOptions[4], False]
	else:
		op[4] = ["TXT_KEY_MAP_TEAM_START", ["TXT_KEY_MAP_TEAM_START_NEIGHBORS", "TXT_KEY_MAP_TEAM_START_SEPARATED", "TXT_KEY_MAP_TEAM_START_RANDOM"], lMapOptions[4], False]
	mst.printDict(op, "Archipelago Map Options:")


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
'''
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
'''
def getWrapX():
	return ( mapOptionWorldShape in [1,3] )

def getWrapY():
	return ( mapOptionWorldShape in [2,3] )

##########

class ArchipelagoFractalWorld(CvMapGeneratorUtil.FractalWorld):
	def checkForOverrideDefaultUserInputVariances(self):
		# Overriding peak value to counterbalance not having any peaks along the coasts.
		extraPeaks = 1 + mapOptionLandmass
		self.peakPercent = min(100, self.peakPercent + (15 * extraPeaks))
		self.peakPercent = max(0, self.peakPercent)
		# Note, the peaks along the coast are not removed until addFeatures()
		return

def assignStartingPlots():
	# Custom start plot finder for Archipelago (high grain) maps.
	# Set up start plot data for all players then access later.
	dice = gc.getGame().getMapRand()
	iW = map.getGridWidth()
	iH = map.getGridHeight()

	# Success flag. Set to false if regional assignment fails or is not to be used.
	global bSuccessFlag
	global start_plots
	bSuccessFlag = True

	# Check for Snaky Continents user option or invalid number of players. If found, use normal start plot finder!
	userInputLandmass = mapOptionLandmass
	iPlayers = gc.getGame().countCivPlayersEverAlive()
	if userInputLandmass == 0:
		CyPythonMgr().allowDefaultImpl()
		return
	if iPlayers < 2 or iPlayers > 18:
		bSuccessFlag = False
		CyPythonMgr().allowDefaultImpl()
		return

	# List of number of regions to be used, indexed by number of players.
	if userInputLandmass == 2: # Tiny Islands will have fewer "dud" regions.
		configs = [0, 3, 3, 3, 6, 6, 8, 8, 12, 12, 12, 15, 15, 15, 20, 20, 20, 20, 24]
	else: # Standard Archipelago needs to account for regions that may be duds.
		configs = [0, 3, 3, 6, 6, 8, 8, 12, 12, 15, 15, 15, 20, 20, 20, 24, 24, 24, 24]
	iNumRegions = configs[iPlayers]

	# Obtain the minimum crow-flies distance figures [minX, minY] for this map size and number of players.
	minimums = {3: [0.1, 0.2],
				6: [0.1, 0.125],
				8: [0.07, 0.125],
				12: [0.07, 0.1],
				15: [0.06, 0.1],
				20: [0.06, 0.06],
				24: [0.05, 0.05]}
	[minLon, minLat] = minimums[iNumRegions]
	minX = max(3, int(minLon * iW))
	minY = max(3, int(minLat * iH))
	#print "minimums", minX, minY, "-o-o-"

	# Templates are nested by keys: {NumRegions: {RegionID: [WestLon, EastLon, SouthLat, NorthLat]}}
	templates = {3: {0: [0.0, 0.333, 0.0, 1.0],
					 1: [0.333, 0.667, 0.0, 1.0],
					 2: [0.667, 1.0, 0.0, 1.0]},
				 6: {0: [0.0, 0.333, 0.0, 0.5],
					 1: [0.333, 0.667, 0.0, 0.5],
					 2: [0.667, 1.0, 0.0, 0.5],
					 3: [0.0, 0.333, 0.5, 1.0],
					 4: [0.333, 0.667, 0.5, 1.0],
					 5: [0.667, 1.0, 0.5, 1.0]},
				 8: {0: [0.0, 0.25, 0.0, 0.5],
					 1: [0.25, 0.5, 0.0, 0.5],
					 2: [0.5, 0.75, 0.0, 0.5],
					 3: [0.75, 1.0, 0.0, 0.5],
					 4: [0.0, 0.25, 0.5, 1.0],
					 5: [0.25, 0.5, 0.5, 1.0],
					 6: [0.5, 0.75, 0.5, 1.0],
					 7: [0.75, 1.0, 0.5, 1.0]},
				 12: {0: [0.0, 0.25, 0.0, 0.35],
					  1: [0.25, 0.5, 0.0, 0.35],
					  2: [0.5, 0.75, 0.0, 0.35],
					  3: [0.75, 1.0, 0.0, 0.35],
					  4: [0.0, 0.25, 0.35, 0.63],
					  5: [0.25, 0.5, 0.35, 0.63],
					  6: [0.5, 0.75, 0.35, 0.63],
					  7: [0.75, 1.0, 0.35, 0.63],
					  8: [0.0, 0.25, 0.63, 1.0],
					  9: [0.25, 0.5, 0.63, 1.0],
					  10: [0.5, 0.75, 0.63, 1.0],
					  11: [0.75, 1.0, 0.63, 1.0]},
				 15: {0: [0.0, 0.2, 0.0, 0.35],
					  1: [0.2, 0.4, 0.0, 0.35],
					  2: [0.4, 0.6, 0.0, 0.35],
					  3: [0.6, 0.8, 0.0, 0.35],
					  4: [0.8, 1.0, 0.0, 0.35],
					  5: [0.0, 0.2, 0.35, 0.63],
					  6: [0.2, 0.4, 0.35, 0.63],
					  7: [0.4, 0.6, 0.35, 0.63],
					  8: [0.6, 0.8, 0.35, 0.63],
					  9: [0.8, 1.0, 0.35, 0.63],
					  10: [0.0, 0.2, 0.63, 1.0],
					  11: [0.2, 0.4, 0.63, 1.0],
					  12: [0.4, 0.6, 0.63, 1.0],
					  13: [0.6, 0.8, 0.63, 1.0],
					  14: [0.8, 1.0, 0.63, 1.0]},
				 20: {0: [0.0, 0.2, 0.0, 0.3],
					  1: [0.2, 0.4, 0.0, 0.3],
					  2: [0.4, 0.6, 0.0, 0.3],
					  3: [0.6, 0.8, 0.0, 0.3],
					  4: [0.8, 1.0, 0.0, 0.3],
					  5: [0.0, 0.2, 0.3, 0.5],
					  6: [0.2, 0.4, 0.3, 0.5],
					  7: [0.4, 0.6, 0.3, 0.5],
					  8: [0.6, 0.8, 0.3, 0.5],
					  9: [0.8, 1.0, 0.3, 0.5],
					  10: [0.0, 0.2, 0.5, 0.7],
					  11: [0.2, 0.4, 0.5, 0.7],
					  12: [0.4, 0.6, 0.5, 0.7],
					  13: [0.6, 0.8, 0.5, 0.7],
					  14: [0.8, 1.0, 0.5, 0.7],
					  15: [0.0, 0.2, 0.7, 1.0],
					  16: [0.2, 0.4, 0.7, 1.0],
					  17: [0.4, 0.6, 0.7, 1.0],
					  18: [0.6, 0.8, 0.7, 1.0],
					  19: [0.8, 1.0, 0.7, 1.0]},
				 24: {0: [0.0, 0.167, 0.0, 0.3],
					  1: [0.167, 0.333, 0.0, 0.3],
					  2: [0.333, 0.5, 0.0, 0.3],
					  3: [0.5, 0.667, 0.0, 0.3],
					  4: [0.667, 0.833, 0.0, 0.3],
					  5: [0.833, 1.0, 0.0, 0.3],
					  6: [0.0, 0.167, 0.3, 0.5],
					  7: [0.167, 0.333, 0.3, 0.5],
					  8: [0.333, 0.5, 0.3, 0.5],
					  9: [0.5, 0.667, 0.3, 0.5],
					  10: [0.667, 0.833, 0.3, 0.5],
					  11: [0.833, 1.0, 0.3, 0.5],
					  12: [0.0, 0.167, 0.5, 0.7],
					  13: [0.167, 0.333, 0.5, 0.7],
					  14: [0.333, 0.5, 0.5, 0.7],
					  15: [0.5, 0.667, 0.5, 0.7],
					  16: [0.667, 0.833, 0.5, 0.7],
					  17: [0.833, 1.0, 0.5, 0.7],
					  18: [0.0, 0.167, 0.7, 1.0],
					  19: [0.167, 0.333, 0.7, 1.0],
					  20: [0.333, 0.5, 0.7, 1.0],
					  21: [0.5, 0.667, 0.7, 1.0],
					  22: [0.667, 0.833, 0.7, 1.0],
					  23: [0.833, 1.0, 0.7, 1.0]}
	}
	# End of template data.

	# region_data: [WestX, EastX, SouthY, NorthY,
	# numLandPlotsinRegion, numCoastalPlotsinRegion,
	# numOceanPlotsinRegion, iRegionNetYield,
	# iNumLandAreas, iNumPlotsinRegion]
	region_data = []
	region_best_areas = []
	region_yields = []
	sorting_regions = []
	for regionLoop in range(iNumRegions):
		# Region dimensions
		[iWestLon, iEastLon, iSouthLat, iNorthLat] = templates[iNumRegions][regionLoop]
		iWestX = int(iW * iWestLon)
		iEastX = int(iW * iEastLon) - 1
		iSouthY = int(iH * iSouthLat)
		iNorthY = int(iH * iNorthLat) -1
		# Plot and Area info.
		iNumLandPlots = 0
		iNumCoastalPlots = 0
		iNumOceanPlots = 0
		iRegionNetYield = 0
		iNumLandAreas = 0
		iNumPlotsinRegion = 0
		land_areas = []
		land_area_plots = {}
		land_area_yield = {}
		# Cycle through all plots in the region.
		for x in range(iWestX, iEastX + 1):
			for y in range(iSouthY, iNorthY + 1):
				iNumPlotsinRegion += 1
				i = y * iW + x
				pPlot = map.plot(x, y)
				if pPlot.getBonusType(-1) != -1: # Count any bonus resource as added value
					iRegionNetYield += 2
				if pPlot.isWater(): # Water plot
					iFertileCheck = mst.calculateBestNatureYield(pPlot, YieldTypes.YIELD_FOOD)
					if iFertileCheck > 1: # If the plot has extra food, count it.
						iRegionNetYield += (2 * (iFertileCheck - 1))
					if pPlot.isAdjacentToLand(): # Coastal plot
						if pPlot.isFreshWater:
							iNumCoastalPlots += 1
							iRegionNetYield += 2
						else:
							iNumCoastalPlots += 1
							iRegionNetYield += 1
					else:
						iNumOceanPlots += 1
				else: # Land plot
					iNumLandPlots += 1
					iArea = pPlot.getArea()
					iPlotYield = mst.calculateTotalBestNatureYield(pPlot)
					iFertileCheck = mst.calculateBestNatureYield(pPlot, YieldTypes.YIELD_FOOD)
					if iFertileCheck > 1: # If the plot has extra food, count the extra as double value!
						iPlotYield += (iFertileCheck - 1)
					iRegionNetYield += iPlotYield
					if pPlot.isHills(): iRegionNetYield += 1 # Add a bonus point for Hills plots.
					if not iArea in land_areas: # This plot is the first detected in its AreaID.
						iNumLandAreas += 1
						land_areas.append(iArea)
						land_area_plots[iArea] = 1
						land_area_yield[iArea] = iPlotYield
					else: # This AreaID already known.
						land_area_plots[iArea] += 1
						land_area_yield[iArea] += iPlotYield
		# Sort areas, achieving a list of AreaIDs with best areas first.
		area_yields = land_area_yield.values()
		area_yields.sort()
		area_yields.reverse()
		best_areas = []
		for areaTestLoop in range(iNumLandAreas):
			for landLoop in range(len(land_areas)):
				if area_yields[areaTestLoop] == land_area_yield[land_areas[landLoop]]:
					best_areas.append(land_areas[landLoop])
					del land_areas[landLoop]
					break
		# Store infos to regional lists.
		region_data.append([iWestX, iEastX, iSouthY, iNorthY,
							iNumLandPlots, iNumCoastalPlots,
							iNumOceanPlots, iRegionNetYield,
							iNumLandAreas, iNumPlotsinRegion])
		region_best_areas.append(best_areas)
		region_yields.append(iRegionNetYield)
		sorting_regions.append(iRegionNetYield)

	#print region_data
	#print "---"
	#print region_best_areas
	#print "+++"
	#print region_yields

	# Now sort the regions
	best_regions = []
	region_numbers = range(iNumRegions)
	#print "reg #s", region_numbers
	sorting_regions.sort()
	sorting_regions.reverse()
	#print "---"
	#print "sorted regions"
	#print sorting_regions
	#print "---"
	for regionTestLoop in range(iNumRegions):
		#print "region test", regionTestLoop
		for yieldLoop in range(len(region_numbers)):
			#print "yield loop", yieldLoop, region_yields[yieldLoop]
			if sorting_regions[regionTestLoop] == region_yields[yieldLoop]:
				#print "--"
				#print region_numbers[yieldLoop]
				#print "++"
				best_regions.append(region_numbers[yieldLoop])
				del region_numbers[yieldLoop]
				del region_yields[yieldLoop]
				#print region_numbers
				#print region_yields
				#print "--"
				break
			#print "x-x"
		#print "-x-"

	# Need to discard the worst regions and then reverse the region order.
	# Of the regions that will be used, the worst will be assigned first.
	#
	# This means the civ with the poorest region will get best pick of its
	# lands without MinDistance concerns. Richer regions will have to obey
	# MinDistances in regard to poorer regions already assigned. This instead
	# of giving the richest region pick of its lands and making poorer regions
	# even worse off by pushing them around with MinDistances.
	best_regions[iPlayers:] = []
	best_regions.reverse()
	#print "----"
	#print best_regions
	#print "----"

	# Obtain player numbers. (Account for possibility of Open slots!)
	player_list = []
	for plrCheckLoop in range(18):
		if gc.getPlayer(plrCheckLoop).isEverAlive():
			player_list.append(plrCheckLoop)
	#print "***"
	#print "Player ID#s", player_list
	#print "***"

	# Shuffle start points so that players are assigned regions at random.
	shuffledPlayers = []
	for playerLoopTwo in range(gc.getGame().countCivPlayersEverAlive()):
		iChoosePlayer = dice.get(len(player_list), "Shuffling Regions - Archipelago PYTHON")
		shuffledPlayers.append(player_list[iChoosePlayer])
		del player_list[iChoosePlayer]
	#print "Shuffled Player List:", shuffledPlayers
	#print "---"

	# Find the oceans. We want all civs to start along the coast of a salt water body.
	oceans = []
	for i in range(map.getIndexAfterLastArea()):
		area = map.getArea(i)
		if not area.isNone():
			if area.isWater() and not area.isLake():
				oceans.append(area)
	#print("Oceans: ", oceans)

	# Now assign the start plots!
	plot_assignments = {}
	min_dist = []
	# Loop through players/regions.
	for assignLoop in range(iPlayers):
		playerID = shuffledPlayers[assignLoop]
		reg = best_regions[assignLoop]
		[westX, eastX, southY, northY] = region_data[reg][0:4]
		iNumAreas = region_data[reg][8]
		area_list = region_best_areas[reg]
		# print Data for debugging
		#print "-+-+-"
		#print iNumAreas
		#print region_data[reg][0:4]
		#print area_list
		#print "+-+-+"
		# Error Handling (if valid start plot not found, reduce MinDistance)
		iPass = 0
		while (true):
			iBestValue = 0
			pBestPlot = None
			# Loop through best areas in this region
			for areaLoop in range(iNumAreas):
				areaID = area_list[areaLoop]
				#print "!!!"
				player = gc.getPlayer(playerID)
				#print "-!-"
				player.AI_updateFoundValues(True)
				#print "!-!"
				iRange = player.startingPlotRange()
				validFn = None
				# Loop through all plots in the region.
				for iX in range(westX, eastX + 1):
					for iY in range(southY, northY + 1):
						pPlot = map.plot(iX, iY)
						if pPlot.isWater(): continue
						if areaID != pPlot.getArea(): continue
						if validFn != None and not validFn(playerID, iX, iY): continue
						val = pPlot.getFoundValue(playerID)
						if val > iBestValue:
							valid = True
							for invalid in min_dist:
								[invalidX, invalidY] = invalid
								if abs(invalidX - iX) < minX and abs(invalidY - iY) < minY:
									valid = False
									break
							if valid:
								oceanside = False
								for ocean in oceans:
									if pPlot.isAdjacentToArea(ocean):
										oceanside = True
										break
								if not oceanside:
									valid = False # Not valid unless adjacent to an ocean!
							if valid:
								for iI in range(gc.getMAX_CIV_PLAYERS()):
									if (gc.getPlayer(iI).isAlive()):
										if (iI != playerID):
											if gc.getPlayer(iI).startingPlotWithinRange(pPlot, playerID, iRange, iPass):
												valid = False
												break
							if valid:
								iBestValue = val
								pBestPlot = pPlot

				if pBestPlot != None:
					min_dist.append([pBestPlot.getX(), pBestPlot.getY()])
					sPlot = map.plot(pBestPlot.getX(), pBestPlot.getY())
					plrID = gc.getPlayer(playerID)
					plrID.setStartingPlot(sPlot, true)
					#print "- - - - -"
					#print "player"
					#print playerID
					#print "Plot Coords"
					#print pBestPlot.getX()
					#print pBestPlot.getY()
					#print "Plot Index", sPlot
					#print "- - - - -"
					break # Valid start found, stop checking areas and plots.
				else: pass # This area too close to somebody, try the next area.

			# Check to see if a valid start was found in ANY areaID.
			if pBestPlot == None:
				print("player", playerID, "pass", iPass, "failed")
				iPass += 1
				if iPass <= max(player.startingPlotRange() + eastX - westX, player.startingPlotRange() + northY - southY):
					continue
				else: # A region has failed to produce any valid starts!
					bSuccessFlag = False
					print "---"
					print "A region has failed"
					print "---"
					# Regional start plot assignment has failed. Reverting to default.
					CyPythonMgr().allowDefaultImpl()
					return
			else: break # This player has been assigned a start plot.

	#print plot_assignments
	#print "..."

	# Successfully assigned start plots, continue back to C++
	return None

def findStartingPlot(argsList):
	# This function is only called for Snaky Continents (or if an entire region should fail to produce a valid start plot via the regional method).
	[playerID] = argsList

	# Check to see if a region failed. If so, try the default implementation. (The rest of this process could get stuck in an infinite loop, so don't risk it!)
	global bSuccessFlag
	if bSuccessFlag == False:
		CyPythonMgr().allowDefaultImpl()
		return

	# Identify the best land area available to this player.
	global areas
	global area_values
	global iBestArea
	iBestValue = 0
	iBestArea = -1
	areas = CvMapGeneratorUtil.getAreas()

	for area in areas:
		if area.isWater(): continue # Don't want to start "in the drink"!
		iNumPlayersOnArea = area.getNumStartingPlots() + 1 # Number of players starting on the area, plus this player.

		iTileValue = area.calculateTotalBestNatureYield() + area.getNumRiverEdges() + 2 * area.countCoastalLand() + 3 * area.countNumUniqueBonusTypes()
		iValue = iTileValue / iNumPlayersOnArea
		if (iNumPlayersOnArea == 1):
			iValue *= 4; iValue /= 3
		if (iValue > iBestValue):
			iBestValue = iValue
			iBestArea = area.getID()

	# Ensure that starting plot is in chosen Area and is along the coast.
	def isValid(playerID, x, y):
		global iBestArea
		pPlot = map.plot(x, y)
		if pPlot.getArea() != iBestArea:
			return false
		pWaterArea = pPlot.waterArea()
		if (pWaterArea.isNone()):
			return false
		return not pWaterArea.isLake()

	return CvMapGeneratorUtil.findStartingPlot(playerID, isValid)
