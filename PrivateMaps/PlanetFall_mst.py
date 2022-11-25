#--------------------------------------------------------------------------------
#	FILE:	   Planetfall_mst.py
#	AUTHOR:  Oleg Giwodiorow / Refar (--> lord_refar@yahoo.de)
#  CONTRIB: Examples and Code Snipplets from original CivIV scripts
#	PURPOSE: Map Script for Civ4 Planetfall Mod.
#	with some minor modifications by Maniac
#
#--------------------------------------------------------------------------------
#  MODIFIED BY: Temudjin (2011)
#  PURPOSE:    - compatibility with 'Fall from Heaven', 'Planetfall', 'Mars Now!'
#              - diverse options and extensions
#  DEPENDENCY: - needs MapScriptTools.py
#
#---------------------------------------------------------------------------------
#	1.04	Terkhen  12.Sep.2016
#        - changed, use grid definitions from the active mod instead of using hardcoded ones.
#
#	1.03	Terkhen  17.Aug.2016
#        - fixed, use terrain, feature and improvement definitions from MST.
#
#	1.02	Terkhen  08.Dic.2014
#        - added, save/load map options.
#        - added, compatibility with RandomMap.
#        - added, resource balancement option.
#        - changed, reordered options to have a similar order than the one used in other MapScripts.
#        - changed, use TXT strings instead of hardcoded ones.
#
#	1.01	Temudjin  29.Jul.2011  ( use MapScriptTools )
#        - compatibility with 'Vanilla BtS'
#        - compatibility with 'FFH'
#        - compatibility with 'Mars Now!'
#        - add Map Options: Wrapping, TeamStart, CoastalWaters, MarsTheme
#        - add Marsh terrain, if supported by mod
#        - add Deep Ocean terrain, if supported by mod
#        - add rivers on islands and from bigger lakes
#        - allow more world sizes, if supported by mod
#        - add Map Features ( Kelp, HauntedLands, CrystalPlains )
#        - add Map Regions ( BigDent, BigBog, ElementalQuarter, LostIsle )
#        - better balanced resources
#        - print stats of mod and map
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
#
from CvPythonExtensions import *
import CvMapGeneratorUtil

########## Temudjin START
#import CvUtil
#import random
#import sys
#from math import sqrt
#from CvMapGeneratorUtil import MultilayeredFractal
#from CvMapGeneratorUtil import FractalWorld
#from CvMapGeneratorUtil import TerrainGenerator
#from CvMapGeneratorUtil import FeatureGenerator
#from CvMapGeneratorUtil import BonusBalancer

#balancer = BonusBalancer()
########## Temudjin END


#---------------------------------------------------------------------------------
# Finetuning Constants
#
# Amount of Highlands.
# Range [1, 100] (I think)
# Higher number means LESS.
h_highlands = 60
# Lower grain will i.g. produce more coherent areas.
# Range [1, ->].
# Values below 4 are likey to produce just one big blobb...
h_grain = 4
# Amount of Peaks. Is derived from amount of highlands, hence as fraction
# Range [0, 1]
# 0 ~ no Peaks. 1 will probably cover all the map with them.
# Here more means more. Sorry.
h_peaks = 0.25
#-------------------------------------------------------------------------


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
	return "1.04_mst"

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_GLOBAL_HIGHLANDS_DESCR"

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
	global mapOptionShape, mapOptionCoastalWaters, mapOptionTeamStart, mapOptionTheme, mapOptionResources

	# Options chosen in Random Map
	mapOptionShape = moWorldShape
	mapOptionResources = moResources
	mapOptionCoastalWaters = moCoastalWaters
	mapOptionTeamStart = moTeamStart
	mapOptionTheme = moMarsTheme

# #################################################################################################
# ######## beforeInit() - Starts the map-generation process, called after the map-options are known
# ########              - map dimensions, latitudes and wrapping status are not known yet
# ######## - handle map specific options
# #################################################################################################
# usually you don't need this, but sometimes it makes things easier
def beforeInit():
	print "-- beforeInit()"

	global mapOptionShape, mapOptionCoastalWaters, mapOptionTeamStart, mapOptionTheme, mapOptionResources
	mapOptionShape = map.getCustomMapOption(0)
	mapOptionResources = map.getCustomMapOption(1)
	mapOptionTeamStart = mst.iif( mst.bMars, None, map.getCustomMapOption( mst.iif(mst.bPfall,2,3) ) )
	mapOptionCoastalWaters = mst.iif(mst.bPfall, None, map.getCustomMapOption(2))
	mapOptionTheme = mst.iif(mst.bMars, map.getCustomMapOption(3), None)

	# allow default pre initialization
	CyPythonMgr().allowDefaultImpl()


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
	mst.getModInfo( getVersion(), None, mapInfo, bNoSigns=False )

	# Determine global Mars Theme
	mst.bSandsOfMars = (mapOptionTheme == 0)

	# Initialize MapScriptTools.BonusBalancer
	# - balance boni, place missing boni, move minerals, longer balancing range
	balancer.initialize( mapOptionResources == 1, True, True, True )

# ###################################################################################
# ######## generatePlotTypes() - Called from system
# ######## - FIRST STAGE in building the map
# ######## - creates an array of plots (ocean,hills,peak,land) in the map dimensions
# ###################################################################################
def generatePlotTypes():
	print "-- generatePlotTypes()"

	gc = CyGlobalContext()
	map = CyMap()
	dice = gc.getGame().getMapRand()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	plotTypes = [PlotTypes.PLOT_OCEAN] * (iW*iH)
	terrainFrac = CyFractal()

	fractal_world = PFHL_MultilayeredFractal()
	plotTypes = fractal_world.generatePlotsByRegion()
	terrainFrac.fracInit(iW, iH, h_grain, dice, 0, -1, -1)

	iHighlandThreshold = terrainFrac.getHeightFromPercent(h_highlands)
	iPeaksThreshold = iHighlandThreshold - (iHighlandThreshold * h_peaks)

	# Now the main loop, which will assign the plot types.
	for x in range(iW):
		for y in range(iH):
			i = y*iW + x
			val = terrainFrac.getHeight(x,y)
			if plotTypes[i] == PlotTypes.PLOT_OCEAN:
				continue # Water plots already set.
			if val >= iHighlandThreshold:
				plotTypes[i] = PlotTypes.PLOT_HILLS
			elif val >= iPeaksThreshold and val < iHighlandThreshold:
				plotTypes[i] = PlotTypes.PLOT_PEAK
			else:
				pass

	return plotTypes

# #######################################################################################
# ######## generateTerrainTypes() - Called from system after generatePlotTypes()
# ######## - SECOND STAGE in 'Generate Map'
# ######## - creates an array of terrains (desert,plains,grass,...) in the map dimensions
# #######################################################################################
def generateTerrainTypes():
	print "-- generateTerrainTypes()"
	#mst.mapPrint.buildPlotMap( True, "generateTerrainTypes()" )

	# Prettify the map - you may not want this
	if not mst.bPfall:
		mst.mapPrettifier.hillifyCoast()
		mst.mapPrettifier.bulkifyIslands()

	# Call native funtion
	return generateTerrainTypes2()

# #######################################################################################
# ######## addRivers() - Called from system after generateTerrainTypes()
# ######## - THIRD STAGE in 'Generate Map'
# ######## - puts rivers on the map
# #######################################################################################
def addRivers():
	print "-- addRivers()"
	#mst.mapPrint.buildTerrainMap( False, "addRivers()" )

	# Generate marsh terrain
	mst.marshMaker.convertTerrain()

	# Create map-regions
	mst.mapRegions.buildBigBogs(1)								# build BigBog
	mst.mapRegions.buildBigDents()								# build BigDents

	# Expand coastal waters - you may not want this
	if mapOptionCoastalWaters: mst.mapPrettifier.expandifyCoast()
	# Generate DeepOcean-terrain if mod allows for it
	mst.deepOcean.buildDeepOcean()

	# Some scripts produce more chaotic terrain than others. You can create more connected
	# (bigger) deserts by converting surrounded plains and grass.
	# Prettify the map - create better connected deserts and plains
	if not (mst.bPfall or mst.bMars):
		mst.mapPrettifier.lumpifyTerrain( mst.etDesert, mst.etPlains, mst.etGrass )
		mst.mapPrettifier.lumpifyTerrain( mst.etPlains, mst.etDesert, mst.etGrass )

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
	#mst.mapPrint.buildRiverMap( False, "addRivers()" )

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
	#mst.mapPrint.buildRiverMap( False, "addFeatures()" )

	# Prettify map - connect some small adjacent lakes
	mst.mapPrettifier.connectifyLakes()
	# Sprout rivers from lakes
	# - all lakes, 40% chance for each of a maximum of two rivers, from lakes of minimum size 3
	mst.riverMaker.buildRiversFromLake( None, 40, 2, 3 )

	featureGen = mst.MST_FeatureGenerator()		# 'Mars Now!' needs this generator
	featureGen.addFeatures()

	# Planetfall: handle shelves and trenches
	#mst.planetFallMap.buildPfallOcean()
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
	#mst.mapPrint.buildFeatureMap( False, "addBonuses()" )

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
	#print "-- addGoodies()"
	#if mst.bPfall:								# Planetfall has it's own way
		#CyPythonMgr().allowDefaultImpl()
	#else:
		#myAddGoodies()							# adjust for map-script Goody Hut generator

# ######################################################################################################
# ######## assignStartingPlots() - Called from system
# ######## - assign starting positions for each player after the map is generated
# ######## - Planetfall has GameOption 'SCATTERED_LANDING_PODS' - use mods default implementation
# ######## - Mars Now! has an odd resource system and maybe no water - use mods default implementation
# ######################################################################################################
def assignStartingPlots():
	print "-- assignStartingPlots()"
	#mst.mapPrint.buildBonusMap( False, "assignStartingPlots()" )

	CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeStartingPlotLocations() - Called from system after starting-plot selection
# ######## - FIRST STAGE in 'Normalize Starting-Plots'
# ######## - change assignments to starting-plots
# ############################################################################################
def normalizeStartingPlotLocations():
	print "-- normalizeStartingPlotLocations()"
	#mst.mapPrint.buildRiverMap( False, "addRivers()" )		# river-map also shows starting-plots

	# build Lost Isle
	# - this region needs to be placed after starting-plots are first assigned
	# - 33% chance to build and 33% chance for hightech
	mst.mapRegions.buildLostIsle( 40, bAliens=mst.choose(33,True,False) )

	# shuffle starting-plots for teams
	if mapOptionTeamStart == 0:
		CyPythonMgr().allowDefaultImpl()							# by default civ places teams near to each other
		# mst.teamStart.placeTeamsTogether( True, True )	# use teamStart to place teams near to each other
	elif mapOptionTeamStart == 1:
		mst.teamStart.placeTeamsTogether( False, True )		# shuffle starting-plots to separate team players
	elif mapOptionTeamStart == 2:
		mst.teamStart.placeTeamsTogether( True, True )		# randomize starting-plots (may be near or not)
	else:
		mst.teamStart.placeTeamsTogether( False, False )	# leave starting-plots alone

	# comment this out if team option exists
	#CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeAddRiver() - Called from system after normalizeStartingPlotLocations()
# ######## - SECOND STAGE in 'Normalize Starting-Plots'
# ######## - add some rivers if needed
# ############################################################################################
def normalizeAddRiver():
	print "-- normalizeAddRiver()"

	if not (mst.bPfall or mst.bSandsOfMars):					# No additional rivers on Mars/Planetfall
		CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeRemovePeaks() - Called from system after normalizeAddRiver()
# ######## - THIRD STAGE in 'Normalize Starting-Plots'
# ######## - remove some peaks if needed
# ############################################################################################
def normalizeRemovePeaks():
	print "-- normalizeRemovePeaks()"

	if not mst.bPfall:
		CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeAddLakesRiver() - Called from system after normalizeRemovePeaks()
# ######## - FOURTH STAGE in 'Normalize Starting-Plots'
# ######## - add some lakes if needed
# ############################################################################################
def normalizeAddLakes():
	print "-- normalizeAddLakes()"

	if not (mst.bPfall or mst.bSandsOfMars):					# No additional lakes on Mars/Planetfall
		CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeRemoveBadFeatures() - Called from system after normalizeAddLakes()
# ######## - FIFTH STAGE in 'Normalize Starting-Plots'
# ######## - remove bad features if needed
# ############################################################################################
def normalizeRemoveBadFeatures():
	print "-- normalizeRemoveBadFeatures()"

	if not mst.bPfall:
		CyPythonMgr().allowDefaultImpl()

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
	if not mst.bPfall: mst.mapPrettifier.deIcifyEdges()

	# Print maps and stats
	mst.mapStats.statPlotCount( "" )
	# Print plotMap
	mst.mapPrint.buildPlotMap( True, "normalizeAddExtras()" )
	# Print areaMap
	mst.mapPrint.buildAreaMap( True, "normalizeAddExtras()" )
	# Print terrainMap
	mst.mapPrint.buildTerrainMap( False, "normalizeAddExtras()" )
	# Print featureMap
	mst.mapPrint.buildFeatureMap( False, "normalizeAddExtras()" )
	# Print bonusMap
	mst.mapPrint.buildBonusMap( False, "normalizeAddExtras()" )
	# Print manaMap if FFH
	if mst.bFFH: mst.mapPrint.buildBonusMap( False, "normalizeAddExtras():Mana", None, mst.mapPrint.manaDict )
	# Print riverMap
	mst.mapPrint.buildRiverMap( False, "normalizeAddExtras()" )
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

################################################################
## Custom Map Option Interface by Temudjin                 START
################################################################
def setCustomOptions():
	""" Set all custom options in one place """
	global op	# { optionID: Name, OptionList, Default, RandomOpt }

	# Initialize options to the default values.
	lMapOptions = [1, 0, 0, 0]

	# Try to read map options from the cfgFile.
	mst.mapOptionsStorage.initialize(lMapOptions, 'PlanetFall')
	lMapOptions = mst.mapOptionsStorage.readConfig()

	optionShape = [ "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_FLAT", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_CYLINDRICAL", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_TUBULAR", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_TOROIDAL" ]

	op = {
	       0: ["TXT_KEY_MAP_SCRIPT_WORLD_WRAP", optionShape, lMapOptions[0],   True],
		   1: ["TXT_KEY_MAP_RESOURCES", ["TXT_KEY_MAP_RESOURCES_STANDARD", "TXT_KEY_MAP_RESOURCES_BALANCED"], lMapOptions[1], True],
		   2: ["TXT_KEY_MAP_COASTS",  ["TXT_KEY_MAP_COASTS_STANDARD", "TXT_KEY_MAP_COASTS_EXPANDED"], lMapOptions[2], True],
	       "Hidden": 2
	     }
	if mst.bPfall:
	    op[2] = ["TXT_KEY_MAP_TEAM_START", ["TXT_KEY_MAP_TEAM_START_NEIGHBORS", "TXT_KEY_MAP_TEAM_START_SEPARATED", "TXT_KEY_MAP_TEAM_START_RANDOM"], lMapOptions[2], False]
	elif mst.bMars:
		op[3] = ["TXT_KEY_MAP_MARS_THEME", ["TXT_KEY_MAP_MARS_THEME_SANDS_OF_MARS", "TXT_KEY_MAP_MARS_THEME_TERRAFORMED_MARS"], lMapOptions[3], False]
	else:
		op[3] = ["TXT_KEY_MAP_TEAM_START", ["TXT_KEY_MAP_TEAM_START_NEIGHBORS", "TXT_KEY_MAP_TEAM_START_SEPARATED", "TXT_KEY_MAP_TEAM_START_RANDOM"], lMapOptions[3], False]

	mst.printDict(op,"Planetfall Map Options:")

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
#	print "[Pfall] -- isClimateMap()"
	return True
def isSeaLevelMap():
#	print "[Pfall] -- isSeaLevelMap()"
	return True

def getTopLatitude():
#	print "[Pfall] -- getTopLatitude()"
	return 90
def getBottomLatitude():
#	print "[Pfall] -- getBottomLatitude()"
	return -90


#	print "[Pfall] -- getWrapX()"
	return ( mapOptionShape in [1,3] )
def getWrapY():
#	print "[Pfall] -- getWrapY()"
	return ( mapOptionShape in [2,3] )

def isBonusIgnoreLatitude():
#	print "[Pfall] -- isBonusIgnoreLatitude()"
	return False

##########

def getGridSize(argsList):
	print " -- getGridSize()"
	if argsList[0] == -1: return []  # (-1,) is passed to function on loads

	[eWorldSize] = argsList
	iWidth = CyGlobalContext().getWorldInfo(eWorldSize).getGridWidth()
	iHeight = CyGlobalContext().getWorldInfo(eWorldSize).getGridHeight()

	return iWidth, iHeight

##########


#-----------------------------------------------------------------------------
# AUTHORS: Oleg Giwodiorow (Refar)
# Subclassing Multilayered fractal, in order to overwrite the
# generatePlotsInRegion() method, so thait it uses the Rift_Grain
# parameter now.
# The goal is being able to create regions usig the same settings, as
# the normal fractal map genetaror does.
# This to be able to make one layer covering all map, and being the same
# as the normal 'Fractal' map type, but with the possibility to add
# more layers for islands or specific features.
#-----------------------------------------------------------------------------
class PFHL_MultilayeredFractal(CvMapGeneratorUtil.MultilayeredFractal):
	#-------------------------------------------------------------------------
	# Overwriting to include Wrap Check - better results if one Region
	# covers the entire map.
	#
	def shiftRegionPlots(self, iRegionWidth, iRegionHeight, iStrip=15):
		stripRadius = min(15, iStrip)
		stripRadius = max(3, iStrip)
		best_split_x = 0
		best_split_y = 0

		if self.map.isWrapX() :
			best_split_x = self.findBestRegionSplitX(iRegionWidth, iRegionHeight, stripRadius)
		if self.map.isWrapY() :
			best_split_y = self.findBestRegionSplitY(iRegionWidth, iRegionHeight, stripRadius)

		self.shiftRegionPlotsBy(best_split_x, best_split_y, iRegionWidth,	iRegionHeight)

	#-------------------------------------------------------------------------
	# Overwriting to change the parameters of the regional fractals.
	# Main Change - the RegionalFractal now can have a RiftFractal
	def generatePlotsInRegion(self, iWaterPercent, iRegionWidth, iRegionHeight, iRegionWestX, iRegionSouthY,
	iRegionGrain, iRegionHillsGrain, iRegionPlotFlags, iRegionTerrainFlags, iRegionFracXExp = -1, iRegionFracYExp = -1,
	bShift = True, iStrip = 15, rift_grain = -1, has_center_rift = False, invert_heights = False):
		# This is the code to generate each fractal.
		#
		# Init local variables
		water = iWaterPercent
		iWestX = iRegionWestX
		# Note: Do not pass bad regional dimensions so that iEastX > self.iW
		iSouthY = iRegionSouthY
		# Init the plot types array and the regional fractals
		self.plotTypes = [] # reinit the array for each pass
		self.plotTypes = [PlotTypes.PLOT_OCEAN] * (iRegionWidth*iRegionHeight)
		regionContinentsFrac = CyFractal()
		regionHillsFrac = CyFractal()
		regionPeaksFrac = CyFractal()
		if (rift_grain >= 0) :
			rFrac = CyFractal()
			rFrac.fracInit(iRegionWidth, iRegionHeight, rift_grain, self.dice, 0, iRegionFracXExp, iRegionFracYExp )
			if has_center_rift:
				iRegionPlotFlags += CyFractal.FracVals.FRAC_CENTER_RIFT
			regionContinentsFrac.fracInitRifts(iRegionWidth, iRegionHeight, iRegionGrain, self.dice, iRegionPlotFlags,
			rFrac, iRegionFracXExp, iRegionFracYExp )
		else :
			regionContinentsFrac.fracInit(iRegionWidth, iRegionHeight,
										  iRegionGrain, self.dice,
										  iRegionPlotFlags, iRegionFracXExp,
										  iRegionFracYExp)

		regionHillsFrac.fracInit(iRegionWidth, iRegionHeight,
								 iRegionHillsGrain, self.dice,
								 iRegionTerrainFlags, iRegionFracXExp,
								 iRegionFracYExp)
		regionPeaksFrac.fracInit(iRegionWidth, iRegionHeight,
								 iRegionHillsGrain+1, self.dice,
								 iRegionTerrainFlags, iRegionFracXExp,
								 iRegionFracYExp)

		iWaterThreshold = regionContinentsFrac.getHeightFromPercent(water)
		iHillsBottom1 = regionHillsFrac.getHeightFromPercent(max((25 - self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 0))
		iHillsTop1 = regionHillsFrac.getHeightFromPercent(min((25 + self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 100))
		iHillsBottom2 = regionHillsFrac.getHeightFromPercent(max((75 - self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 0))
		iHillsTop2 = regionHillsFrac.getHeightFromPercent(min((75 + self.gc.getClimateInfo(self.map.getClimate()).getHillRange()), 100))
		iPeakThreshold = regionPeaksFrac.getHeightFromPercent(self.gc.getClimateInfo(self.map.getClimate()).getPeakPercent())

		# Loop through the region's plots
		for x in range(iRegionWidth):
			for y in range(iRegionHeight):
				i = y*iRegionWidth + x
				val = regionContinentsFrac.getHeight(x,y)
				if val <= iWaterThreshold:
					self.plotTypes[i] = PlotTypes.PLOT_OCEAN
				else:
					self.plotTypes[i] = PlotTypes.PLOT_LAND

		if bShift :
			# Shift plots to obtain a more natural shape.
			self.shiftRegionPlots(iRegionWidth, iRegionHeight, iStrip)

		# Once the plot types for the region have been generated, they must be
		# applied to the global plot array.
		# Default approach is to ignore water and layer the lands over
		for x in range(iRegionWidth):
			wholeworldX = x + iWestX
			for y in range(iRegionHeight):
				i = y*iRegionWidth + x
				if self.plotTypes[i] == PlotTypes.PLOT_OCEAN: continue
				wholeworldY = y + iSouthY
				iWorld = wholeworldY*self.iW + wholeworldX
				self.wholeworldPlotTypes[iWorld] = self.plotTypes[i]

		# This region is done.
		return

	#-------------------------------------------------------------------------
	# MultilayeredFractal class, controlling function.
	#
	def generatePlotsByRegion(self):
		global xShiftRoll
		xShiftRoll = self.dice.get(2, "Python, PlanetFallHighlands Map")
#		iCGrain = 1 + self.dice.get(4, "Python, PlanetFallHighlands Map")
#		if (iCGrain > 2): iCGrain = 2
		iCGrain = 2
		iIGrain = 4
		cPart = 1.0
		cShift = 0.0
		if (iCGrain == 1):
			cPart = 0.45 + 0.01 * self.dice.get(21, "Python, PlanetFall Map")
			cShift = 0.0 + 0.01 * self.dice.get(100, "Python, PlanetFall Map")
			if ( cShift >= 0.69 ) :
				cShift = cShift - 0.69
			if ( cPart + cShift > 0.98) :
				cShift = 0.98 - cPart

			print("PlanetFall Highlands: Continental Rate: ", cPart,
			  " Continental Shift, West Boundary: ", cShift,
				  " Continent Grain, Island Grain: ", iCGrain, iIGrain)

		# Since there will be two layers in all areas, reduce the amount of Land Plots
		sea = self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()
		sea = min(sea, 5)
		sea = max(sea, -5)
		iWater = 80 + sea

		sizekey = self.map.getWorldSize()
		if ( sizekey > 3 ) :
			xExp = 7
			yExp = 7
		else :
			xExp = 7
			yExp = 6

		# Add the Islands.
		iSouthY = int(self.iH * 0.08)
		iNorthY = int(self.iH * 0.92)
		iHeight = iNorthY - iSouthY + 1
		iWestX = 0
		iEastX = self.iW - 1
		iWidth = iEastX - iWestX + 1
		self.generatePlotsInRegion(min(iWater+5, 90), iWidth, iHeight, iWestX, iSouthY, iIGrain, 5, self.iRoundFlags,
		self.iTerrainFlags, xExp, yExp, True, 15, -1, False, False)

		#Main Landmasses
		iSouthY = int(self.iH * 0.03)
		iNorthY = int(self.iH * 0.97)
		iHeight = iNorthY - iSouthY + 1
		iWestX = 0
		iEastX = self.iW - 1
		iWidth = iEastX - iWestX + 1
		rGrain = 5
		hasRift = True
		if ( iCGrain == 1 ) :
			iSouthY = int(self.iH * 0.05)
			iNorthY = int(self.iH * 0.95)
			iHeight = iNorthY - iSouthY + 1
			iWidth = int(self.iW * cPart)
			iWestX = int(self.iW * cShift)
			rGrain = -1
			hasRift = False
		self.generatePlotsInRegion(iWater, iWidth, iHeight, iWestX, iSouthY, iCGrain, 4, self.iRoundFlags,
		self.iTerrainFlags, xExp, yExp, True, 15, rGrain, hasRift, False)

		# All regions have been processed. Plot Type generation completed.
		return self.wholeworldPlotTypes
#
#END class PFHL_MultilayeredFractal
#

#-------------------------------------------------------------------------
#
#
def generateTerrainTypes2():
	NiTextOut("Generating Terrain (Python PlanetFall Highlands) ...")

	if mst.bPfall:							# Temudjin
		gc = CyGlobalContext()
		map = CyMap()
		iW = map.getGridWidth()
		iH = map.getGridHeight()
		dice = gc.getGame().getMapRand()

		iCoast = mst.etCoast
		iShelf = mst.etShelf
		iOcean = mst.etOcean
		iIce = mst.efIce
		iTrench = mst.efTrench
		iTrenchImp = mst.eiTrench

		prob_base = 1.00
		prob_shelf = 0
		prob_mod = 0.30
		prob_spawn = -0.30
		prob_trench = 0.45

		for x in range(iW):
			for y in range(iH):
				if ( y < 2 or y > (iH-2) or x == 0 or x == iW ) :
					continue
				pPlot = map.plot(x, y)
				if pPlot.getTerrainType() != iCoast:
					continue

				ocean_counter = 0
				trench_counter = 0
				highland_counter = 0
				prob_drop = 0.0

				pP1 = map.plot(x-1, y)
				if pP1.getTerrainType() == iOcean:
					ocean_counter += 1
				if pP1.getPlotType() == PlotTypes.PLOT_HILLS or pP1.getPlotType() == PlotTypes.PLOT_PEAK:
					highland_counter += 1
				if pP1.getFeatureType() == iTrench or pP1.getImprovementType() == iTrenchImp:
					trench_counter += 1
				if pP1.getTerrainType() == iCoast:
					prob_drop = prob_drop * prob_mod + prob_mod
				pP1 = map.plot(x-1, y-1)
				if pP1.getTerrainType() == iOcean:
					ocean_counter += 1
				if pP1.getPlotType() == PlotTypes.PLOT_HILLS or pP1.getPlotType() == PlotTypes.PLOT_PEAK:
					highland_counter += 1
				if pP1.getFeatureType() == iTrench or pP1.getImprovementType() == iTrenchImp:
					trench_counter += 1
				if pP1.getTerrainType() == iCoast:
					prob_drop = prob_drop * prob_mod + prob_mod
				pP1 = map.plot(x, y-1)
				if pP1.getTerrainType() == iOcean:
					ocean_counter += 1
				if pP1.getPlotType() == PlotTypes.PLOT_HILLS or pP1.getPlotType() == PlotTypes.PLOT_PEAK:
					highland_counter += 1
				if pP1.getFeatureType() == iTrench or pP1.getImprovementType() == iTrenchImp:
					trench_counter += 1
				if pP1.getTerrainType() == iCoast:
					prob_drop = prob_drop * prob_mod + prob_mod
				pP1 = map.plot(x+1, y)
				if pP1.getTerrainType() == iOcean:
					ocean_counter += 1
				if pP1.getPlotType() == PlotTypes.PLOT_HILLS or pP1.getPlotType() == PlotTypes.PLOT_PEAK:
					highland_counter += 1
				if pP1.getFeatureType() == iTrench or pP1.getImprovementType() == iTrenchImp:
					trench_counter += 1
				if pP1.getTerrainType() == iCoast:
					prob_drop = prob_drop * prob_mod + prob_mod
				pP1 = map.plot(x+1, y-1)
				if pP1.getTerrainType() == iOcean:
					ocean_counter += 1
				if pP1.getPlotType() == PlotTypes.PLOT_HILLS or pP1.getPlotType() == PlotTypes.PLOT_PEAK:
					highland_counter += 1
				if pP1.getFeatureType() == iTrench or pP1.getImprovementType() == iTrenchImp:
					trench_counter += 1
				if pP1.getTerrainType() == iCoast:
					prob_drop = prob_drop * prob_mod + prob_mod
				pP1 = map.plot(x+1, y+1)
				if pP1.getTerrainType() == iOcean:
					ocean_counter += 1
				if pP1.getPlotType() == PlotTypes.PLOT_HILLS or pP1.getPlotType() == PlotTypes.PLOT_PEAK:
					highland_counter += 1
				if pP1.getFeatureType() == iTrench or pP1.getImprovementType() == iTrenchImp:
					trench_counter += 1
				if pP1.getTerrainType() == iCoast:
					prob_drop = prob_drop * prob_mod + prob_mod
				pP1 = map.plot(x, y+1)
				if pP1.getTerrainType() == iOcean:
					ocean_counter += 1
				if pP1.getPlotType() == PlotTypes.PLOT_HILLS or pP1.getPlotType() == PlotTypes.PLOT_PEAK:
					highland_counter += 1
				if pP1.getFeatureType() == iTrench or pP1.getImprovementType() == iTrenchImp:
					trench_counter += 1
				if pP1.getTerrainType() == iCoast:
					prob_drop = prob_drop * prob_mod + prob_mod
				pP1 = map.plot(x-1, y+1)
				if pP1.getTerrainType() == iOcean:
					ocean_counter += 1
				if pP1.getPlotType() == PlotTypes.PLOT_HILLS or pP1.getPlotType() == PlotTypes.PLOT_PEAK:
					highland_counter += 1
				if pP1.getFeatureType() == iTrench or pP1.getImprovementType() == iTrenchImp:
					trench_counter += 1
				if pP1.getTerrainType() == iCoast:
					prob_drop = prob_drop * prob_mod + prob_mod

				prob = prob_base - prob_drop
				if( trench_counter == 0 ):
					prob = prob + prob_spawn
				if( trench_counter == 1 ):
					prob = prob + prob_trench
				if( trench_counter > 2 ):
					prob = 0
				if( ocean_counter == 0 ):
					prob = 0
				if( highland_counter == 0 ):
					prob = 0

				if prob * 100 > dice.get(100, "trench lines"):
					if pPlot.getFeatureType() == iIce:
						pPlot.setImprovementType(iTrenchImp)
					else :
						pPlot.setFeatureType(iTrench, 0 )

		for x in range(iW):
			for y in range(iH):
				if ( y < 2 or y > (iH-2) or x == 0 or x == iW ) :
					continue
				pPlot = map.plot(x, y)
				if pPlot.getTerrainType() != iOcean:
					continue

				prob_shelf = 0

				pP1 = map.plot(x-1, y)
				if pP1.getPlotType() != PlotTypes.PLOT_OCEAN:
					continue
				if pP1.getTerrainType() == iShelf or (pP1.getTerrainType() == iCoast and not (pP1.getFeatureType() == iTrench or pP1.getImprovementType() == iTrenchImp)):
					prob_shelf = 50
				pP1 = map.plot(x-1, y-1)
				if pP1.getPlotType() != PlotTypes.PLOT_OCEAN:
					continue
				if pP1.getTerrainType() == iShelf or (pP1.getTerrainType() == iCoast and not (pP1.getFeatureType() == iTrench or pP1.getImprovementType() == iTrenchImp)):
					prob_shelf = 50
				pP1 = map.plot(x, y-1)
				if pP1.getPlotType() != PlotTypes.PLOT_OCEAN:
					continue
				if pP1.getTerrainType() == iShelf or (pP1.getTerrainType() == iCoast and not (pP1.getFeatureType() == iTrench or pP1.getImprovementType() == iTrenchImp)):
					prob_shelf = 50
				pP1 = map.plot(x+1, y-1)
				if pP1.getPlotType() != PlotTypes.PLOT_OCEAN:
					continue
				if pP1.getTerrainType() == iShelf or (pP1.getTerrainType() == iCoast and not (pP1.getFeatureType() == iTrench or pP1.getImprovementType() == iTrenchImp)):
					prob_shelf = 50
				pP1 = map.plot(x+1, y)
				if pP1.getPlotType() != PlotTypes.PLOT_OCEAN:
					continue
				if pP1.getTerrainType() == iShelf or (pP1.getTerrainType() == iCoast and not (pP1.getFeatureType() == iTrench or pP1.getImprovementType() == iTrenchImp)):
					prob_shelf = 50
				pP1 = map.plot(x+1, y+1)
				if pP1.getPlotType() != PlotTypes.PLOT_OCEAN:
					continue
				if pP1.getTerrainType() == iShelf or (pP1.getTerrainType() == iCoast and not (pP1.getFeatureType() == iTrench or pP1.getImprovementType() == iTrenchImp)):
					prob_shelf = 50
				pP1 = map.plot(x, y+1)
				if pP1.getPlotType() != PlotTypes.PLOT_OCEAN:
					continue
				if pP1.getTerrainType() == iShelf or (pP1.getTerrainType() == iCoast and not (pP1.getFeatureType() == iTrench or pP1.getImprovementType() == iTrenchImp)):
					prob_shelf = 50
				pP1 = map.plot(x-1, y+1)
				if pP1.getPlotType() != PlotTypes.PLOT_OCEAN:
					continue
				if pP1.getTerrainType() == iShelf or (pP1.getTerrainType() == iCoast and not (pP1.getFeatureType() == iTrench or pP1.getImprovementType() == iTrenchImp)):
					prob_shelf = 50

				if prob_shelf > dice.get(100, "Shelf extension"):
					pPlot.setTerrainType(iShelf, True, True )

	########## Temudjin START
	# Choose terrainGenerator
	# terrainGen = TerrainGenerator()
	if mst.bMars:
		# There are two possible scenarios for 'Mars Now!':
		# either water is converted to desert or not
		iDesert = mst.iif( mst.bSandsOfMars, 16, 32 )	# already enough desert with 'Sands of Mars'
		terrainGen = mst.MST_TerrainGenerator_Mars( iDesertPercent=iDesert )
	else:
		terrainGen = mst.MST_TerrainGenerator()			# this is the default
	########## Temudjin END

	# Generate terrain
	terrainTypes = terrainGen.generateTerrain()
	return terrainTypes

#-------------------------------------------------------------------------
#
########## Temudjin START
"""
def addFeatures():

	# Turning some Highlands into unpassable Terrain
	# This runs after the actual Terrain generation, so this
	# is only good to add impassable Terrain, over the terrain that was there
	# before.
	gc = CyGlobalContext()
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	dice = gc.getGame().getMapRand()

#	newTerrain = gc.getInfoTypeForString("TERRAIN_PEAKTERRAIN")
#	newPlot = PlotTypes.PLOT_PEAK

#	for x in range(iW):
#		for y in range(iH):
#			pPlot = map.plot(x, y)
#			if ( pPlot.getPlotType() != PlotTypes.PLOT_PEAK ) :
#				continue

#			pPlot.setPlotType(newPlot, True, True)
#			pPlot.setTerrainType(newTerrain, True, True )

	NiTextOut("Adding Features (Python PlanetFall Highlands) ...")
	featuregen = FeatureGenerator()
	featuregen.addFeatures()
	return 0

def normalizeAddRiver():
	return None

def normalizeRemovePeaks():
	return None

def normalizeAddLakes():
	return None

def normalizeRemoveBadFeatures():
	return None

def normalizeRemoveBadTerrain():
	return None

def normalizeAddFoodBonuses():
	return None

def normalizeAddGoodTerrain():
	return None
"""
########## Temudjin END
