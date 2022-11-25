#
#	FILE:	 Medium_and_Small.py
#	AUTHOR:  Bob Thomas (Sirian)
#	PURPOSE: Global map script - Mixed islands and continents.
#-----------------------------------------------------------------------------
#	Copyright (c) 2007 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#   1.12    Terkhen   08.Dic.2014
#   - added, save/load map options.
#   - added, compatibility with RandomMap.
#   - added, resource balancement option.
#   - changed, reordered options to have a similar order than the one used in other MapScripts.
#   - changed, use TXT strings instead of hardcoded ones.
#
#	1.11	Temudjin  15.Mar.11
#   - fixed, mixup with custom options
#   - fixed [Mars Now!], team start normalization
#   - added, new map option: expanded coastal waters (like Civ5)
#   - added [Mars Now!], new map option: 'Sands of Mars'/'Terraformed Mars'
#   - changed, stratified custom map option process
#   - changed, stratified normalization process
#   - changed, reorganised function call sequence within map building process
#   - changed [Mars Now!], using dedicated terrain generator
#
#	1.10	Temudjin  15.Jul.10  ( uses MapScriptTools )
#   - compatibility with 'Planetfall'
#   - compatibility with 'Mars Now!'
#   - add Map Option: World Shape
#   - add Map Option: TeamStart
#   - add Marsh terrain, if supported by mod
#   - add Deep Ocean terrain, if supported by mod
#   - add rivers on islands and from lakes
#   - add Map Regions ( BigDent, BigBog, ElementalQuarter, LostIsle )
#   - add Map Features ( Kelp, HauntedLands, CrystalPlains )
#   - better balanced resources
#   - print stats of mod and map
#   - add getVersion()

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
#from CvMapGeneratorUtil import FractalWorld
#from CvMapGeneratorUtil import TerrainGenerator
#from CvMapGeneratorUtil import FeatureGenerator


map = CyMap()

################################################################
## MapScriptTools Interface by Temudjin                    START
################################################################
import MapScriptTools as mst
balancer = mst.bonusBalancer

def getVersion():
	return "1.12_mst"
def getDescription():
	return "TXT_KEY_MAP_SCRIPT_MEDIUM_AND_SMALL_DESCR"

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
	global mapOptionContinents, mapOptionIslands, mapOptionOverlap, mapOptionResources
	global mapOptionWorldShape, mapOptionCoastalWaters, mapOptionTeamStart, mapOptionMarsTheme

	# Options chosen in Random Map
	mapOptionWorldShape = moWorldShape
	mapOptionResources = moResources
	mapOptionCoastalWaters = moCoastalWaters
	mapOptionTeamStart = moTeamStart
	mapOptionMarsTheme = moMarsTheme

	# All other options are chosen randomly.
	mapOptionContinents = CyGlobalContext().getGame().getMapRand().get(4, "Medium_And_Small.randomMapBeforeInit(), mapOptionContinents")
	mapOptionIslands = CyGlobalContext().getGame().getMapRand().get(2, "Medium_And_Small.randomMapBeforeInit(), mapOptionIslands")
	mapOptionOverlap = CyGlobalContext().getGame().getMapRand().get(2, "Medium_And_Small.randomMapBeforeInit(), mapOptionOverlap")

# #################################################################################################
# ######## beforeInit() - Starts the map-generation process, called after the map-options are known
# ######## - map dimensions, latitudes and wrapping status are not known yet
# ######## - handle map specific options
# #################################################################################################
def beforeInit():
	print "-- beforeInit()"
	# Selected map options
	global mapOptionContinents, mapOptionIslands, mapOptionOverlap, mapOptionResources
	global mapOptionWorldShape, mapOptionCoastalWaters, mapOptionTeamStart, mapOptionMarsTheme
	mapOptionContinents = map.getCustomMapOption(2)
	mapOptionIslands = map.getCustomMapOption(3)
	mapOptionOverlap = map.getCustomMapOption(4)
	mapOptionWorldShape = map.getCustomMapOption(0)
	mapOptionResources = map.getCustomMapOption(1)
	mapOptionCoastalWaters = mst.iif(mst.bPfall, None, map.getCustomMapOption(5))
	mapOptionTeamStart = mst.iif(mst.bMars, None, map.getCustomMapOption( mst.iif(mst.bPfall,5,6) ))
	mapOptionMarsTheme = mst.iif(mst.bMars, map.getCustomMapOption(6), None)

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

	# from original beforeGeneration()
	global yShiftRoll1, yShiftRoll2
	yShiftRoll1 = mst.choose(50, True, False)	# West Region Shift, Vertical
	yShiftRoll2 = mst.choose(50, True, False)	# East Region Shift, Vertical

# #######################################################################################
# ######## generatePlotTypes() - Called from system after beforeGeneration()
# ######## - FIRST STAGE in 'Generate Map'
# ######## - creates an array of plots (ocean, land, hills, peak) in the map dimensions
# #######################################################################################
def generatePlotTypes():
	print "-- generatePlotTypes()"
	fractal_world = MnSMultilayeredFractal()
	plotTypes = fractal_world.generatePlotsByRegion()
	return plotTypes

# #######################################################################################
# ######## generateTerrainTypes() - Called from system after generatePlotTypes()
# ######## - SECOND STAGE in 'Generate Map'
# ######## - creates an array of terrains (desert,plains,grass,...) in the map dimensions
# #######################################################################################
def generateTerrainTypes():
	print "-- generateTerrainTypes()"

	# Planetfall: more highlands
	mst.planetFallMap.buildPfallHighlands()
	# Prettify map: Connect small islands
	mst.mapPrettifier.bulkifyIslands()
	# Prettify map: most coastal peaks -> hills
	mst.mapPrettifier.hillifyCoast()
	# Generate terrain
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
	print "-- addFeatures()"

	# Prettify map - connect some small adjacent lakes
	mst.mapPrettifier.connectifyLakes()
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
	lMapOptions = [1, 0, 0, 0, 1, 0, 0]

	# Try to read map options from the cfgFile.
	mst.mapOptionsStorage.initialize(lMapOptions, 'Medium_and_Small')
	lMapOptions = mst.mapOptionsStorage.readConfig()

	optionContinents = [ "TXT_KEY_MAP_SCRIPT_NORMAL_CONTINENTS", "TXT_KEY_MAP_SCRIPT_UNPREDICTABLE",
	                     "TXT_KEY_MAP_SCRIPT_SNAKY_CONTINENTS", "TXT_KEY_MAP_SCRIPT_ISLANDS" ]
	optionIslands =    [ "TXT_KEY_MAP_SCRIPT_ISLANDS", "TXT_KEY_MAP_SCRIPT_TINY_ISLANDS" ]
	optionOverlap =    [ "TXT_KEY_MAP_SCRIPT_ISLAND_REGION_SEPARATE", "TXT_KEY_MAP_SCRIPT_ISLANDS_MIXED_IN" ]
	optionShape =      [ "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_FLAT", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_CYLINDRICAL", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_TUBULAR", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_TOROIDAL" ]
	op = {
	       0: ["TXT_KEY_MAP_SCRIPT_WORLD_WRAP", optionShape, lMapOptions[0], True],
		   1: ["TXT_KEY_MAP_RESOURCES", ["TXT_KEY_MAP_RESOURCES_STANDARD", "TXT_KEY_MAP_RESOURCES_BALANCED"], lMapOptions[1], True],
	       2: ["TXT_KEY_MAP_SCRIPT_CONTINENTS_SIZE", optionContinents, lMapOptions[2], True],
	       3: ["TXT_KEY_MAP_SCRIPT_ISLANDS_SIZE",    optionIslands, lMapOptions[3], True],
	       4: ["TXT_KEY_MAP_SCRIPT_ISLAND_OVERLAP",  optionOverlap, lMapOptions[4], True],
	       5: ["TXT_KEY_MAP_COASTS",  ["TXT_KEY_MAP_COASTS_STANDARD", "TXT_KEY_MAP_COASTS_EXPANDED"], lMapOptions[5], True],
	       "Hidden": 2
	     }
	if mst.bPfall:
	    op[5] = ["TXT_KEY_MAP_TEAM_START", ["TXT_KEY_MAP_TEAM_START_NEIGHBORS", "TXT_KEY_MAP_TEAM_START_SEPARATED", "TXT_KEY_MAP_TEAM_START_RANDOM"], lMapOptions[5], False]
	elif mst.bMars:
		op[6] = ["TXT_KEY_MAP_MARS_THEME", ["TXT_KEY_MAP_MARS_THEME_SANDS_OF_MARS", "TXT_KEY_MAP_MARS_THEME_TERRAFORMED_MARS"], lMapOptions[6], False]
	else:
	    op[6] = ["TXT_KEY_MAP_TEAM_START", ["TXT_KEY_MAP_TEAM_START_NEIGHBORS", "TXT_KEY_MAP_TEAM_START_SEPARATED", "TXT_KEY_MAP_TEAM_START_RANDOM"], lMapOptions[6], False]
	mst.printDict(op,"MediumAndSmall Map Options:")

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


class MnSMultilayeredFractal(CvMapGeneratorUtil.MultilayeredFractal):
	def generatePlotsByRegion(self):
		# Sirian's MultilayeredFractal class, controlling function.
		# You -MUST- customize this function for each use of the class.
		global yShiftRoll1
		global yShiftRoll2
		if self.map.getCustomMapOption(0) != 4:
			iContinentsGrainWest = 1 + self.map.getCustomMapOption(0)
			iContinentsGrainEast = 1 + self.map.getCustomMapOption(0)
		else:
			iContinentsGrainWest = 1 + self.dice.get(4, "West Continent Grain - Medium and Small PYTHON")
			iContinentsGrainEast = 1 + self.dice.get(4, "East Continent Grain - Medium and Small PYTHON")
		iIslandsGrain = 4 + self.map.getCustomMapOption(1)
		userInputOverlap = self.map.getCustomMapOption(2)

		# Add a few random patches of Tiny Islands first.
		numTinies = 1 + self.dice.get(4, "Tiny Islands - Medium and Small PYTHON")
		print("Patches of Tiny Islands: ", numTinies)
		if numTinies:
			for tiny_loop in range(numTinies):
				tinyWestLon = 0.01 * self.dice.get(85, "Tiny Longitude - Medium and Small PYTHON")
				tinyWestX = int(self.iW * tinyWestLon)
				tinySouthLat = 0.01 * self.dice.get(85, "Tiny Latitude - Medium and Small PYTHON")
				tinySouthY = int(self.iH * tinyWestLon)
				tinyWidth = int(self.iW * 0.15)
				tinyHeight = int(self.iH * 0.15)

				self.generatePlotsInRegion(80,
				                           tinyWidth, tinyHeight,
				                           tinyWestX, tinySouthY,
				                           4, 3,
				                           0, self.iTerrainFlags,
				                           6, 5,
				                           True, 3,
				                           -1, False,
				                           False
				                           )

		# Add the contental regions.

		# Add the Western Continent(s).
		iSouthY = 0
		iNorthY = self.iH - 1
		iHeight = iNorthY - iSouthY + 1
		iWestX = int(self.iW / 20)
		iEastX = int(self.iW * 0.45) - 1
		iWidth = iEastX - iWestX + 1
		print("Cont West: ", iWestX, "Cont East: ", iEastX, "Cont Width: ", iWidth)

		# Vertical dimensions may be affected by overlap and/or shift.
		if userInputOverlap: # Then both layers fill the entire region and overlap each other.
			# The north and south boundaries are already set (to max values).
			# Set Y exponent:
			yExp = 5
			# Also need to reduce amount of land plots, since there will be two layers in all areas.
			iWater = 80
		else: # The regions are separate, with continents only in one part, islands only in the other.
			iWater = 74
			# Set X exponent to square setting:
			yExp = 6
			# Handle horizontal shift for the Continents layer.
			# (This will choose one side or the other for this region then fit it properly in its space).
			if yShiftRoll1:
				southShift = int(0.4 * self.iH)
				northShift = 0
			else:
				southShift = 0
				northShift = int(0.4 * self.iH)

			iSouthY += southShift
			iNorthY -= northShift
			iHeight = iNorthY - iSouthY + 1
		print("Cont South: ", iSouthY, "Cont North: ", iNorthY, "Cont Height: ", iHeight)

		self.generatePlotsInRegion(iWater,
		                           iWidth, iHeight,
		                           iWestX, iSouthY,
		                           iContinentsGrainWest, 4,
		                           self.iRoundFlags, self.iTerrainFlags,
		                           6, yExp,
		                           True, 15,
		                           -1, False,
		                           False
		                           )

		# Add the Western Islands.
		iWestX = int(self.iW * 0.12)
		iEastX = int(self.iW * 0.38) - 1
		iWidth = iEastX - iWestX + 1
		iSouthY = 0
		iNorthY = self.iH - 1
		iHeight = iNorthY - iSouthY + 1

		# Vertical dimensions may be affected by overlap and/or shift.
		if userInputOverlap: # Then both layers fill the entire region and overlap each other.
			# The north and south boundaries are already set (to max values).
			# Set Y exponent:
			yExp = 5
			# Also need to reduce amount of land plots, since there will be two layers in all areas.
			iWater = 80
		else: # The regions are separate, with continents only in one part, islands only in the other.
			iWater = 74
			# Set X exponent to square setting:
			yExp = 6
			# Handle horizontal shift for the Continents layer.
			# (This will choose one side or the other for this region then fit it properly in its space).
			if yShiftRoll1:
				southShift = 0
				northShift = int(0.4 * self.iH)
			else:
				southShift = int(0.4 * self.iH)
				northShift = 0

			iSouthY += southShift
			iNorthY -= northShift
			iHeight = iNorthY - iSouthY + 1
		print("Cont South: ", iSouthY, "Cont North: ", iNorthY, "Cont Height: ", iHeight)


		self.generatePlotsInRegion(iWater,
		                           iWidth, iHeight,
		                           iWestX, iSouthY,
		                           iIslandsGrain, 5,
		                           self.iRoundFlags, self.iTerrainFlags,
		                           6, yExp,
		                           True, 15,
		                           -1, False,
		                           False
		                           )

		# Add the Eastern Continent(s).
		iSouthY = 0
		iNorthY = self.iH - 1
		iHeight = iNorthY - iSouthY + 1
		iWestX = int(self.iW * 0.55)
		iEastX = int(self.iW * 0.95) - 1
		iWidth = iEastX - iWestX + 1
		print("Cont West: ", iWestX, "Cont East: ", iEastX, "Cont Width: ", iWidth)

		# Vertical dimensions may be affected by overlap and/or shift.
		if userInputOverlap: # Then both layers fill the entire region and overlap each other.
			# The north and south boundaries are already set (to max values).
			# Set Y exponent:
			yExp = 5
			# Also need to reduce amount of land plots, since there will be two layers in all areas.
			iWater = 80
		else: # The regions are separate, with continents only in one part, islands only in the other.
			iWater = 74
			# Set X exponent to square setting:
			yExp = 6
			# Handle horizontal shift for the Continents layer.
			# (This will choose one side or the other for this region then fit it properly in its space).
			if yShiftRoll2:
				southShift = int(0.4 * self.iH)
				northShift = 0
			else:
				southShift = 0
				northShift = int(0.4 * self.iH)

			iSouthY += southShift
			iNorthY -= northShift
			iHeight = iNorthY - iSouthY + 1
		print("Cont South: ", iSouthY, "Cont North: ", iNorthY, "Cont Height: ", iHeight)

		self.generatePlotsInRegion(iWater,
		                           iWidth, iHeight,
		                           iWestX, iSouthY,
		                           iContinentsGrainWest, 4,
		                           self.iRoundFlags, self.iTerrainFlags,
		                           6, yExp,
		                           True, 15,
		                           -1, False,
		                           False
		                           )

		# Add the Eastern Islands.
		iWestX = int(self.iW * 0.62)
		iEastX = int(self.iW * 0.88) - 1
		iWidth = iEastX - iWestX + 1
		iSouthY = 0
		iNorthY = self.iH - 1
		iHeight = iNorthY - iSouthY + 1

		# Vertical dimensions may be affected by overlap and/or shift.
		if userInputOverlap: # Then both layers fill the entire region and overlap each other.
			# The north and south boundaries are already set (to max values).
			# Set Y exponent:
			yExp = 5
			# Also need to reduce amount of land plots, since there will be two layers in all areas.
			iWater = 80
		else: # The regions are separate, with continents only in one part, islands only in the other.
			iWater = 74
			# Set X exponent to square setting:
			yExp = 6
			# Handle horizontal shift for the Continents layer.
			# (This will choose one side or the other for this region then fit it properly in its space).
			if yShiftRoll2:
				southShift = 0
				northShift = int(0.4 * self.iH)
			else:
				southShift = int(0.4 * self.iH)
				northShift = 0

			iSouthY += southShift
			iNorthY -= northShift
			iHeight = iNorthY - iSouthY + 1
		print("Cont South: ", iSouthY, "Cont North: ", iNorthY, "Cont Height: ", iHeight)


		self.generatePlotsInRegion(iWater,
		                           iWidth, iHeight,
		                           iWestX, iSouthY,
		                           iIslandsGrain, 5,
		                           self.iRoundFlags, self.iTerrainFlags,
		                           6, yExp,
		                           True, 15,
		                           -1, False,
		                           False
		                           )

		# All regions have been processed. Plot Type generation completed.
		print "Done"
		return self.wholeworldPlotTypes

'''
Regional Variables Key:

iWaterPercent,
iRegionWidth, iRegionHeight,
iRegionWestX, iRegionSouthY,
iRegionGrain, iRegionHillsGrain,
iRegionPlotFlags, iRegionTerrainFlags,
iRegionFracXExp, iRegionFracYExp,
bShift, iStrip,
rift_grain, has_center_rift,
invert_heights
'''
