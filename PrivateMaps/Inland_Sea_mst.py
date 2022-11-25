#
#	FILE:	 Inland_Sea.py
#	AUTHOR:  Bob Thomas (Sirian)
#	CONTRIB: Soren Johnson, Andy Szybalski
#	PURPOSE: Regional map script - Loosely simulates a Mediterranean type
#	         temperate zone with civs ringing a central sea.
#-----------------------------------------------------------------------------
#	Copyright (c) 2005 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#       MODIFIED BY: Temudjin
#       PURPOSE:    - compatibility with 'Planetfall' and 'Mars Now!'
#                   - add Marsh terrain, if supported by mod
#                   - print stats of mod and map
#                   - much more ...
#       DEPENDENCY: - needs MapScriptTools.py
#-----------------------------------------------------------------------------
#
#  1.33  Terkhen      12.Sep.16
#        - changed, use grid definitions from the active mod instead of using hardcoded ones.
#  1.32  Terkhen      08.Dic.14
#        - added, save/load map options.
#        - added, compatibility with RandomMap.
#        - changed, use default resource placement by default instead of balanced.
#        - changed, use TXT strings instead of hardcoded ones.
#  1.31  Temudjin     15.Mar.11
#        - fixed compatibility to Planetfalls 'Scattered Pods' mod option
#        - fixed (maybe) occational empty sea problem
#        - fixed latitude evaluation
#        - fixed [Mars Now!], team start normalization
#        - added, new map option for expanded coastal waters (like Civ5)
#        - added [Mars Now!], new map option: 'Sands of Mars'/'Terraformed Mars'
#        - changed (rewrote) assignStartingPlots()/findStartingPlot() system
#        - changed, slightly adjusted top and bottom latitude to climate
#        - changed, stratified custom map option process
#        - changed, stratified normalization process
#        - changed, reorganised function call sequence within map building process
#        - changed [Mars Now!] now using dedicated terrain generator
#  1.30  Temudjin     15.Jul.10
#        - utilizes MapScriptTools
#        - add Team Start option
#        - allow all map-wrapping
#        - allow any number of civs
#        - allow more world sizes, if supported by mod
#        - add Marsh terrain, if supported by mod
#        - add Deep Ocean terrain, if supported by mod
#        - add Map Regions ( BigDent, BigBog, ElementalQuarter, LostIsle )
#        - add Map Features ( Kelp, HauntedLands, CrystalPlains )
#        - better balanced resources
#        - compatibility with 'Mars Now!'
#  1.20  Temudjin     29.Mar.09
#        - utilizes mapTools( Ringworld2 )
#  1.10  Jean Elcard   4.Feb.09
#        - works with 'Giant' map in FlavourMod
#

from CvPythonExtensions import *
import CvMapGeneratorUtil
import math

gc = CyGlobalContext()
map = CyMap()

################################################################
## MapScriptTools by Temudjin
################################################################
import MapScriptTools as mst
balancer = mst.bonusBalancer

def getVersion():
	return "1.33_mst"

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_INLAND_SEA_DESCR"

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
	global mapOptionWorldShape, mapOptionResources
	global mapOptionCoastalWaters, mapOptionTeamStart, mapOptionMarsTheme

	# Options chosen in Random Map
	mapOptionWorldShape = moWorldShape
	mapOptionResources = moResources
	mapOptionCoastalWaters = moCoastalWaters
	mapOptionTeamStart = moTeamStart
	mapOptionMarsTheme = moMarsTheme

# #################################################################################################
# ######## beforeInit() - Starts the map-generation process, called after the map-options are known
# ######## - map dimensions, latitudes and wrapping status are not known yet
# ######## - handle map specific options
# #################################################################################################
def beforeInit():
	print "-- beforeInit()"

	# Selected map options
	global mapOptionWorldShape, mapOptionResources
	global mapOptionCoastalWaters, mapOptionTeamStart, mapOptionMarsTheme
	mapOptionWorldShape = map.getCustomMapOption(0)
	mapOptionResources = map.getCustomMapOption(1)
	mapOptionCoastalWaters = mst.iif(mst.bPfall, None, map.getCustomMapOption(2))
	mapOptionTeamStart = mst.iif(mst.bMars, None, map.getCustomMapOption( mst.iif(mst.bPfall,2,3) ))
	mapOptionMarsTheme = mst.iif(mst.bMars, map.getCustomMapOption(3), None)

# #######################################################################################
# ######## beforeGeneration() - Called from system after user input is finished
# ######## - create map options info string
# ######## - initialize the MapScriptTools
# ######## - initialize MapScriptTools.BonusBalancer
# #######################################################################################
def beforeGeneration():
	print "[InSea] -- beforeGeneration()"

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

	# Determine global Mars Theme
	mst.bSandsOfMars = (mapOptionMarsTheme == 0)

	# Initialize bonus balancing
	balancer.initialize( mapOptionResources == 1 )	# balance boni if desired, place missing boni, move minerals

# #######################################################################################
# ######## generateTerrainTypes() - Called from system after generatePlotTypes()
# ######## - SECOND STAGE in 'Generate Map'
# ######## - creates an array of terrains (desert,plains,grass,...) in the map dimensions
# #######################################################################################
def generateTerrainTypes():
	print "[InSea] -- generateTerrainTypes()"

	# Planetfall: more highlands
	mst.planetFallMap.buildPfallHighlands()
	# Prettify map: Connect small islands
	mst.mapPrettifier.bulkifyIslands()
	# Prettify map: most coastal peaks -> hills
	mst.mapPrettifier.hillifyCoast()

	# Choose terrainGenerator
	if mst.bPfall:
		terraingen = mst.MST_TerrainGenerator()		# for Planetfall use MST_TerrainGenerator()
	elif mst.bMars:
		# There are two possible scenarios for 'Mars Now!':
		# either water is converted to desert or not
		iDesert = mst.iif( mst.bSandsOfMars, 15, 30 )
		terraingen = mst.MST_TerrainGenerator_Mars( iDesert )
	else:
		terraingen = ISTerrainGenerator()
	# Generate terrain
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

# #######################################################################################
# ######## addRivers() - Called from system after generateTerrainTypes()
# ######## - THIRD STAGE in 'Generate Map'
# ######## - puts rivers on the map
# #######################################################################################
def addRivers():
	print "[InSea] -- addRivers()"

	# Generate marsh-terrain
	mst.marshMaker.convertTerrain()

	# Expand coastal waters
	if mapOptionCoastalWaters == 1:
		mst.mapPrettifier.expandifyCoast()

	# Build between 0..2 mountain-ranges.
	mst.mapRegions.buildBigDents()
	# Build between 0..2 bog-regions.
	mst.mapRegions.buildBigBogs()

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
	print "[InSea] -- addLakes()"
	if not mst.bMars:
		CyPythonMgr().allowDefaultImpl()

# #######################################################################################
# ######## addFeatures() - Called from system after addLakes()
# ######## - FIFTH STAGE in 'Generate Map'
# ######## - puts features on the map
# #######################################################################################
def addFeatures():
	print "[InSea] -- addFeatures()"

	# Kill of spurious lakes
	mst.mapPrettifier.connectifyLakes( 33 )
	# Sprout rivers from lakes - 60% chance each for up to 1 rivers per lake with >= 2 tiles
	mst.riverMaker.buildRiversFromLake( None, 60, 1, 2 )

	if mst.bMars:
		featuregen = mst.MST_FeatureGenerator()
	else:
		featuregen = ISFeatureGenerator()
	featuregen.addFeatures()

	# Prettify the map - transform coastal volcanos; default: 66% chance
	mst.mapPrettifier.beautifyVolcanos()
	# Mars Now!: lumpify sandstorms
	if mst.bMars: mst.mapPrettifier.lumpifyTerrain( mst.efSandStorm, FeatureTypes.NO_FEATURE )
	# Planetfall: handle shelves and trenches
	if mst.bPfall: mst.planetFallMap.buildPfallOcean()
	# FFH: build ElementalQuarter; default: 5% chance
	mst.mapRegions.buildElementalQuarter()


# ######################################################################################################
# ######## assignStartingPlots() - Called from system
# ######## - assign starting positions for each player after the map is generated
# ######################################################################################################
def assignStartingPlots():
	print "[InSea] -- assignStartingPlots()"
	map.recalculateAreas()
	coordList = calcCoordinates()
	mst.randomList.shuffle( coordList )
	iW = mst.iNumPlotsX
	iH = mst.iNumPlotsY
	maxPlayers = gc.getGame().countCivPlayersEverAlive()

	# iterate each player
	for playerID in range( maxPlayers ):
		player = gc.getPlayer( playerID )
		player.AI_updateFoundValues( True )
		iRange = player.startingPlotRange()
		# get starting-plot area for player
		x0, y0 = coordList[playerID]
		varX = max( int( iW * 0.05 ), 3 )
		varY = max( int( iH * 0.05 ), 3 )
		print "[InSea] x,y (%i,%i) - dx,dy (%i,%i)" % (x0, y0, varX, varY)

		# Now get area-range
		westX = mst.iif( map.isWrapX(), x0 - varX, max(2, x0 - varX) )
		eastX = mst.iif( map.isWrapX(), x0 + varX, min(iW - 3, x0 + varX) )
		southY = mst.iif( map.isWrapY(), y0 - varY, max(2, y0 - varY) )
		northY = mst.iif( map.isWrapY(), y0 + varY, min(iH - 3, y0 + varY) )
		print "[InSea] Ranges: WE (%i - %i), SN (%i - %i)" % (westX,eastX,southY,northY)

		# calc best place; add outer ring and try again if not found in area
		valid = False
		passes = 0
		maxpasses = 30
		while not valid:
			iBestValue = 0
			pBestPlot = None
			s="[InSea] Plot-Values: "
			for x in range( westX-passes, eastX+passes ):
				for y in range( southY-passes, northY+passes ):
					pPlot = mst.GetPlot(x,y)
					if pPlot.isWater(): continue
					if pPlot.isPeak(): continue
					ok = True
					for i in range( maxPlayers ):
						if (i != playerID):
							if gc.getPlayer(i).startingPlotWithinRange(pPlot, playerID, iRange, passes):
								ok = False
								break
					if ok:
						val = pPlot.getFoundValue( playerID )
						s += "(%i,%i)%i, " % (x,y,val)
						if val > iBestValue:
							valid = True
							iBestValue = val
							pBestPlot = pPlot
			if valid and (iBestValue < 300):
				passes += 1
				print s
				print "[InSea] Passes: %i" % passes
				maxpasses = passes
			elif not valid:
				passes += 1
				print s
				print "[InSea] Passes: %i" % passes
				if passes>maxpasses: break
		print s
		# save new starting-plot
		print "[InSea] Starting-Plot( %r ) = %r, Value:%i" % ( playerID, mst.coordByPlot(pBestPlot), iBestValue )
		player.setStartingPlot( pBestPlot, True )

# ############################################################################################
# ######## normalizeStartingPlotLocations() - Called from system after starting-plot selection
# ######## - FIRST STAGE in 'Normalize Starting-Plots'
# ######## - change assignments to starting-plots
# ############################################################################################
# shuffle starting-plots for teams
def normalizeStartingPlotLocations():
	print "[InSea] -- normalizeStartingPlotLocations()"

	# build Lost Isle
	# - this region needs to be placed after starting-plots are first assigned
	mst.mapRegions.buildLostIsle( bAliens = mst.choose(33,True,False) )

	if mst.bMars:
		# Mars Now! uses no teams
		CyPythonMgr().allowDefaultImpl()
	elif mapOptionTeamStart == 0:
		# by default civ places teams near to each other
		CyPythonMgr().allowDefaultImpl()
	elif mapOptionTeamStart == 1:
		# shuffle starting-plots to separate teams
		mst.teamStart.placeTeamsTogether( False, True )
	else:
		# randomize starting-plots to ignore teams
		mst.teamStart.placeTeamsTogether( True, True )

# ############################################################################################
# ######## normalizeAddRiver() - Called from system after normalizeStartingPlotLocations()
# ######## - SECOND STAGE in 'Normalize Starting-Plots'
# ######## - add some rivers if needed
# ############################################################################################
def normalizeAddRiver():
	print "[InSea] -- normalizeAddRiver()"
	if not mst.bMars:
		CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeRemovePeaks() - Called from system after normalizeAddRiver()
# ######## - THIRD STAGE in 'Normalize Starting-Plots'
# ######## - remove some peaks if needed
# ############################################################################################
def normalizeRemovePeaks():
	print "[InSea] -- normalizeRemovePeaks()"
	return None

# ############################################################################################
# ######## normalizeAddLakesRiver() - Called from system after normalizeRemovePeaks()
# ######## - FOURTH STAGE in 'Normalize Starting-Plots'
# ######## - add some lakes if needed
# ############################################################################################
def normalizeAddLakes():
	print "[InSea] -- normalizeAddLakes()"
	if not (mst.bMars and mst.bSandsOfMars):
		CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeRemoveBadFeatures() - Called from system after normalizeAddLakes()
# ######## - FIFTH STAGE in 'Normalize Starting-Plots'
# ######## - remove bad features if needed
# ############################################################################################
def normalizeRemoveBadFeatures():
	print "[InSea] -- normalizeRemoveBadFeatures()"
	return None

# ############################################################################################
# ######## normalizeRemoveBadTerrain() - Called from system after normalizeRemoveBadFeatures()
# ######## - SIXTH STAGE in 'Normalize Starting-Plots'
# ######## - change bad terrain if needed
# ############################################################################################
def normalizeRemoveBadTerrain():
	print "[InSea] -- normalizeRemoveBadTerrain()"
	if not (mst.bPfall or mst.bMars):
		CyPythonMgr().allowDefaultImpl()

# ############################################################################################
# ######## normalizeAddFoodBonuses() - Called from system after normalizeRemoveBadTerrain()
# ######## - SEVENTH STAGE in 'Normalize Starting-Plots'
# ######## - add food if needed
# ############################################################################################
def normalizeAddFoodBonuses():
	print "[InSea] -- normalizeAddFoodBonuses()"
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

def normalizeAddExtras():
	print "[InSea] -- normalizeAddExtras()"
	# Balance boni, place missing boni, move minerals
	balancer.normalizeAddExtras()

	# Do the default housekeeping
#	normalizeAddExtras2()						# call renamed script function
	CyPythonMgr().allowDefaultImpl()

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
	lMapOptions = [0, 0, 0, 0]

	# Try to read map options from the cfgFile.
	mst.mapOptionsStorage.initialize(lMapOptions, 'Inland_Sea')
	lMapOptions = mst.mapOptionsStorage.readConfig()

	optionShape = [ "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_FLAT", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_CYLINDRICAL", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_TUBULAR", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_TOROIDAL" ]
	op = {
	       0: ["TXT_KEY_MAP_SCRIPT_WORLD_WRAP", optionShape, lMapOptions[0], True],
	       1: ["TXT_KEY_MAP_RESOURCES", ["TXT_KEY_MAP_RESOURCES_STANDARD", "TXT_KEY_MAP_RESOURCES_BALANCED"], lMapOptions[1], True],
	       2: ["TXT_KEY_MAP_COASTS", ["TXT_KEY_MAP_COASTS_STANDARD", "TXT_KEY_MAP_COASTS_EXPANDED"], lMapOptions[2], True],
	       "Hidden": 2
	     }
	if mst.bPfall:
	    op[2] = ["TXT_KEY_MAP_TEAM_START", ["TXT_KEY_MAP_TEAM_START_NEIGHBORS", "TXT_KEY_MAP_TEAM_START_SEPARATED", "TXT_KEY_MAP_TEAM_START_RANDOM"], lMapOptions[2], False]
	elif mst.bMars:
		op[3] = ["TXT_KEY_MAP_MARS_THEME", ["TXT_KEY_MAP_MARS_THEME_SANDS_OF_MARS", "TXT_KEY_MAP_MARS_THEME_TERRAFORMED_MARS"], lMapOptions[3], False]
	else:
	    op[3] = ["TXT_KEY_MAP_TEAM_START", ["TXT_KEY_MAP_TEAM_START_NEIGHBORS", "TXT_KEY_MAP_TEAM_START_SEPARATED", "TXT_KEY_MAP_TEAM_START_RANDOM"], lMapOptions[3], False]

	mst.printDict(op,"InlandSea Map Options:")

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

# randomize latitude range - take climate into account
def calcLatitudes():
	print "[InSea] -- calcLatitudes()"
	rng = 50 + mst.chooseNumber(80)
	top = mst.iif(map.getClimate()==1, 45, 55)			# tropical
	top = mst.iif(map.getClimate()==4, 65, top)			# cold
	bot = max( top - rng, -65 )
	return top, bot
latTop, latBottom = calcLatitudes()
def getTopLatitude():
	# return 60
	return latTop
def getBottomLatitude():
	# return -60
	return latBottom

def getWrapX():
	return ( mapOptionWorldShape in [1,3] )
def getWrapY():
	return ( mapOptionWorldShape in [2,3] )

def isBonusIgnoreLatitude():
	return False

##########

def getGridSize(argsList):
	"Because this is such a land-heavy map, override getGridSize() to make the map smaller"
	if (argsList[0] == -1): return []			# (-1,) is passed to function on loads

	[eWorldSize] = argsList
	iWidth = 0
	iHeight = 0
	if eWorldSize >= 2:
		iWidth = CyGlobalContext().getWorldInfo(eWorldSize - 2).getGridWidth()
		iHeight = CyGlobalContext().getWorldInfo(eWorldSize - 2).getGridHeight()
	else:
		iScale = 0.6
		if eWorldSize == 1:
			iScale = 0.8
		# Scale down the smallest world size
		iWidth = int(math.ceil(CyGlobalContext().getWorldInfo(0).getGridWidth() * iScale))
		iHeight = int(math.ceil(CyGlobalContext().getWorldInfo(0).getGridHeight() * iScale))

	return iWidth, iHeight

############### Temudjin START - not needed as original bonusBalancer has been replaced
#def normalizeAddExtras():
#	if (mapOptionResources == 1):
#		balancer.normalizeAddExtras()
#	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride

#def addBonusType(argsList):
#	[iBonusType] = argsList
#	gc = CyGlobalContext()
#	type_string = gc.getBonusInfo(iBonusType).getType()
#
#	if (mapOptionResources == 1):
#		if (type_string in balancer.resourcesToBalance) or (type_string in balancer.resourcesToEliminate):
#			return None # don't place any of this bonus randomly
#
#	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way
############### Temudjin END

# Set up list of coordinates for starting-plots
def calcCoordinates():
	print "[InSea] -- calcCoordinates()"
	# templates are nested by keys: {(NumPlayers, TemplateID): {PlayerID: [relX, relX]} }
	templates = {
					(1,0): {	0: [0.5, 0.5]},
					(2,0): {	0: [0.1, 0.5],
								1: [0.9, 0.5]},
					(2,1): {	0: [0.5, 0.167],
								1: [0.5, 0.833]},
					(2,2): {	0: [0.3, 0.167],
								1: [0.7, 0.833]},
					(2,3): {	0: [0.7, 0.167],
								1: [0.3, 0.833]},
					(2,4): {	0: [0.2, 0.333],
								1: [0.8, 0.667]},
					(2,5): {	0: [0.8, 0.333],
								1: [0.2, 0.677]},
					(3,0): {	0: [0.1, 0.5],
								1: [0.7, 0.167],
								2: [0.7, 0.833]},
					(3,1): {	0: [0.9, 0.5],
								1: [0.3, 0.167],
								2: [0.3, 0.833]},
					(3,2): {	0: [0.5, 0.167],
								1: [0.1, 0.833],
								2: [0.9, 0.833]},
					(3,3): {	0: [0.5, 0.833],
								1: [0.1, 0.167],
								2: [0.9, 0.167]},
					(4,0): {	0: [0.1, 0.5],
								1: [0.5, 0.167],
								2: [0.9, 0.5],
								3: [0.5, 0.833]},
					(4,1): {	0: [0.1, 0.167],
								1: [0.7, 0.167],
								2: [0.9, 0.833],
								3: [0.3, 0.833]},
					(4,2): {	0: [0.1, 0.833],
								1: [0.7, 0.833],
								2: [0.9, 0.167],
								3: [0.3, 0.167]},
					(5,0): {	0: [0.5, 0.167],
								1: [0.125, 0.333],
								2: [0.25, 0.833],
								3: [0.75, 0.833],
								4: [0.875, 0.333]},
					(5,1): {	0: [0.5, 0.833],
								1: [0.125, 0.667],
								2: [0.25, 0.167],
								3: [0.75, 0.167],
								4: [0.875, 0.667]},
					(6,0): {	0: [0.1, 0.5],
								1: [0.3, 0.167],
								2: [0.7, 0.167],
								3: [0.9, 0.5],
								4: [0.7, 0.833],
								5: [0.3, 0.833]},
					(6,1): {	0: [0.1, 0.167],
								1: [0.5, 0.167],
								2: [0.9, 0.167],
								3: [0.9, 0.833],
								4: [0.5, 0.833],
								5: [0.1, 0.833]},
					(7,0): {	0: [0.1, 0.5],
								1: [0.2, 0.125],
								2: [0.6, 0.125],
								3: [0.9, 0.25],
								4: [0.9, 0.75],
								5: [0.6, 0.875],
								6: [0.2, 0.875]},
					(7,1): {	0: [0.9, 0.5],
								1: [0.8, 0.125],
								2: [0.4, 0.125],
								3: [0.1, 0.25],
								4: [0.1, 0.75],
								5: [0.4, 0.875],
								6: [0.8, 0.875]},
					(8,0): {	0: [0.583, 0.125],
								1: [0.25, 0.125],
								2: [0.083, 0.375],
								3: [0.083, 0.875],
								4: [0.417, 0.875],
								5: [0.75, 0.875],
								6: [0.917, 0.625],
								7: [0.917, 0.125]},
					(8,1): {	0: [0.417, 0.125],
								1: [0.083, 0.125],
								2: [0.083, 0.625],
								3: [0.25, 0.875],
								4: [0.583, 0.875],
								5: [0.917, 0.875],
								6: [0.917, 0.375],
								7: [0.75, 0.125]},
					(8,2): {	0: [0.1, 0.5],
								1: [0.2, 0.125],
								2: [0.5, 0.125],
								3: [0.8, 0.125],
								4: [0.9, 0.5],
								5: [0.8, 0.875],
								6: [0.5, 0.875],
								7: [0.2, 0.875]},
					(8,3): {	0: [0.1, 0.75],
								1: [0.1, 0.25],
								2: [0.333, 0.125],
								3: [0.667, 0.125],
								4: [0.9, 0.25],
								5: [0.9, 0.75],
								6: [0.667, 0.875],
								7: [0.333, 0.875]},
					(9,0): {	0: [0.833, 0.15],
								1: [0.5, 0.15],
								2: [0.167, 0.15],
								3: [0.08, 0.412],
								4: [0.08, 0.775],
								5: [0.35, 0.85],
								6: [0.65, 0.85],
								7: [0.92, 0.775],
								8: [0.92, 0.412]},
					(9,1): {	0: [0.833, 0.85],
								1: [0.5, 0.85],
								2: [0.167, 0.85],
								3: [0.08, 0.588],
								4: [0.08, 0.225],
								5: [0.35, 0.15],
								6: [0.65, 0.15],
								7: [0.92, 0.225],
								8: [0.92, 0.588]},
					(10,0): {0: [0.875, 0.15],
								1: [0.625, 0.15],
								2: [0.375, 0.15],
								3: [0.125, 0.15],
								4: [0.08, 0.5],
								5: [0.125, 0.85],
								6: [0.375, 0.85],
								7: [0.625, 0.85],
								8: [0.875, 0.85],
								9: [0.92, 0.5]},
					(10,1): {0: [0.75, 0.15],
								1: [0.5, 0.15],
								2: [0.25, 0.15],
								3: [0.08, 0.33],
								4: [0.08, 0.67],
								5: [0.25, 0.85],
								6: [0.5, 0.85],
								7: [0.75, 0.85],
								8: [0.92, 0.67],
								9: [0.92, 0.33]},
					(11,0): {0: [0.875, 0.15],
								1: [0.625, 0.15],
								2: [0.375, 0.15],
								3: [0.125, 0.15],
								4: [0.08, 0.45],
								5: [0.08, 0.75],
								6: [0.28, 0.85],
								7: [0.5, 0.85],
								8: [0.72, 0.85],
								9: [0.92, 0.75],
								10:[0.92, 0.45]},
					(11,1): {0: [0.875, 0.85],
								1: [0.625, 0.85],
								2: [0.375, 0.85],
								3: [0.125, 0.85],
								4: [0.08, 0.55],
								5: [0.08, 0.25],
								6: [0.28, 0.15],
								7: [0.5, 0.15],
								8: [0.72, 0.15],
								9: [0.92, 0.25],
								10:[0.92, 0.55]},
					(12,0): {0: [0.7, 0.15],
								1: [0.5, 0.15],
								2: [0.3, 0.15],
								3: [0.1, 0.15],
								4: [0.08, 0.5],
								5: [0.1, 0.85],
								6: [0.3, 0.85],
								7: [0.5, 0.85],
								8: [0.7, 0.85],
								9: [0.9, 0.85],
								10:[0.92, 0.5],
								11:[0.9, 0.15]},
					(13,0): {0: [0.7, 0.125],
								1: [0.5, 0.125],
								2: [0.3, 0.125],
								3: [0.1, 0.125],
								4: [0.08, 0.425],
								5: [0.08, 0.725],
								6: [0.2, 0.875],
								7: [0.4, 0.875],
								8: [0.6, 0.875],
								9: [0.8, 0.875],
								10:[0.92, 0.725],
								11:[0.92, 0.425],
								12:[0.9, 0.125]},
					(13,1): {0: [0.7, 0.875],
								1: [0.5, 0.875],
								2: [0.3, 0.875],
								3: [0.1, 0.875],
								4: [0.08, 0.575],
								5: [0.08, 0.275],
								6: [0.2, 0.125],
								7: [0.4, 0.125],
								8: [0.6, 0.125],
								9: [0.8, 0.125],
								10:[0.92, 0.275],
								11:[0.92, 0.575],
								12:[0.9, 0.875]},
					(14,0): {0: [0.7, 0.125],
								1: [0.5, 0.125],
								2: [0.3, 0.125],
								3: [0.1, 0.125],
								4: [0.08, 0.375],
								5: [0.08, 0.625],
								6: [0.1, 0.875],
								7: [0.3, 0.875],
								8: [0.5, 0.875],
								9: [0.7, 0.875],
								10:[0.9, 0.875],
								11:[0.92, 0.625],
								12:[0.92, 0.375],
								13:[0.9, 0.125]},
					(15,0): {0: [0.583, 0.125],
								1: [0.417, 0.125],
								2: [0.25, 0.125],
								3: [0.083, 0.125],
								4: [0.083, 0.4],
								5: [0.083, 0.65],
								6: [0.1, 0.9],
								7: [0.3, 0.875],
								8: [0.5, 0.875],
								9: [0.7, 0.875],
								10:[0.9, 0.9],
								11:[0.917, 0.65],
								12:[0.917, 0.4],
								13:[0.917, 0.125],
								14:[0.75, 0.125]},
					(15,1): {0: [0.583, 0.875],
								1: [0.417, 0.875],
								2: [0.25, 0.875],
								3: [0.083, 0.875],
								4: [0.083, 0.6],
								5: [0.083, 0.35],
								6: [0.1, 0.1],
								7: [0.3, 0.125],
								8: [0.5, 0.125],
								9: [0.7, 0.125],
								10:[0.9, 0.1],
								11:[0.917, 0.35],
								12:[0.917, 0.6],
								13:[0.917, 0.875],
								14:[0.75, 0.875]},
					(16,0): {0: [0.583, 0.125],
								1: [0.417, 0.125],
								2: [0.25, 0.125],
								3: [0.083, 0.125],
								4: [0.083, 0.375],
								5: [0.083, 0.625],
								6: [0.083, 0.875],
								7: [0.25, 0.875],
								8: [0.417, 0.875],
								9: [0.583, 0.875],
								10:[0.75, 0.875],
								11:[0.917, 0.875],
								12:[0.917, 0.625],
								13:[0.917, 0.375],
								14:[0.917, 0.125],
								15:[0.75, 0.125]},
					(17,0): {0: [0.5, 0.125],
								1: [0.35, 0.125],
								2: [0.2, 0.125],
								3: [0.05, 0.175],
								4: [0.083, 0.45],
								5: [0.083, 0.7],
								6: [0.083, 0.95],
								7: [0.25, 0.875],
								8: [0.417, 0.875],
								9: [0.583, 0.875],
								10:[0.75, 0.875],
								11:[0.917, 0.95],
								12:[0.917, 0.7],
								13:[0.917, 0.45],
								14:[0.95, 0.175],
								15:[0.8, 0.125],
								16:[0.65, 0.125]},
					(17,1): {0: [0.5, 0.875],
								1: [0.35, 0.875],
								2: [0.2, 0.875],
								3: [0.05, 0.825],
								4: [0.083, 0.65],
								5: [0.083, 0.3],
								6: [0.083, 0.05],
								7: [0.25, 0.125],
								8: [0.417, 0.125],
								9: [0.583, 0.125],
								10:[0.75, 0.125],
								11:[0.917, 0.05],
								12:[0.917, 0.3],
								13:[0.917, 0.65],
								14:[0.95, 0.825],
								15:[0.8, 0.875],
								16:[0.65, 0.875]},
					(18,0): {0: [0.5, 0.125],
								1: [0.35, 0.125],
								2: [0.2, 0.125],
								3: [0.05, 0.125],
								4: [0.075, 0.375],
								5: [0.075, 0.625],
								6: [0.05, 0.875],
								7: [0.2, 0.875],
								8: [0.35, 0.875],
								9: [0.5, 0.875],
								10:[0.65, 0.875],
								11:[0.8, 0.875],
								12:[0.95, 0.875],
								13:[0.925, 0.625],
								14:[0.925, 0.375],
								15:[0.95, 0.125],
								16:[0.8, 0.125],
								17:[0.65, 0.125]}
					}
	# List of number of template instances, indexed by number of players.
	configs = [0, 1, 6, 4, 3, 2, 2, 2, 4, 2, 2, 2, 1, 2, 1, 2, 1, 2, 1]
	iW = mst.iNumPlotsX
	iH = mst.iNumPlotsY

	iPlayers = gc.getGame().countCivPlayersEverAlive()
	# if Planetfall simulate additional players
	if mst.bPfall:
		if not mst.bPfall_Scattered:
			ipl = min(iPlayers + iPlayers/2 + 2, 18)
		else:
			ipl = min(iPlayers + 1, 18)
		print "ipl / iPlayers - %i / %i" % (ipl,iPlayers)
	else:
		ipl = iPlayers

	# if more than 18 players calculate starting-positions, otherwise use template
	if ipl > 18:
		cList = getStartPositions( iPlayers )
	else:
		t = mst.chooseNumber( configs[ipl] )
		cDict = templates[ (ipl,t) ]
		print cDict
		cList = cDict.values()
	cList = [ [ int(iW * cList[i][0]), int(iH * cList[i][1]) ] for i in range( len(cList) ) ]

	# if Planetfall select real starting-positions from those generated
	if mst.bPfall:
		cList.sort()
		inx = mst.choose( 50, 0, -1 )
		x0,y0 = cList[inx][0], cList[inx][1]
		nList = mst.getNearestPlots( x0, y0, cList, iPlayers )
		mst.printList( cList, "cList:", rows=18 )
		mst.printList( nList, "nList:", rows=18 )
		cList = [ [ cList[i][0], cList[i][1] ] for i in range( len(cList) ) if i in nList ]

	mst.printList( cList, "CoordList:", rows=18 )
	return cList

def getStartPositions( iPlayers ):
	print "[InSea] -- getStartPositions( %i )" % iPlayers
	coord = []
	for i in range( iPlayers + iPlayers%2 ): coord.append( [] )

	if iPlayers >10: yAdd = 2
	elif iPlayers > 24: yAdd = 3
	elif iPlayers > 40: yAdd = 4
	else: yAdd = 0

	pl = (iPlayers - yAdd + 1) / 2
	for i in range( pl ):
		dx1 = -0.025
		dx2 = +0.025
		if i>0 and i<(pl-1) and ((i%2)==0):
			dx1 = -0.05
			dx2 = +0.05
		elif i>0 and i<(pl-1) and ((i%2)==1):
			dx1 = 0
			dx2 = 0
		coord[2*i] = [ 0.05 + (0.9 * i) / (pl-1), 0.15 + dx1 ]
		coord[2*i+1] = [ 0.05 + (0.9 * i) / (pl-1), 0.85 + dx2 ]

	for j in range ( yAdd ):
		dy = j * 0.5 / yAdd + 0.25 + 0.25 / yAdd
		coord[2*(pl-1)+2*j]   = [ 0.075, dy ]
		coord[2*(pl-1)+2*j+1] = [ 0.925, dy ]

	if len(coord) > iPlayers:
		inx = mst.chooseListIndex( coord )
		del coord[ inx ]
	return coord

# Subclasses to fix the FRAC_POLAR zero row bugs.
class ISFractalWorld(CvMapGeneratorUtil.FractalWorld):
	def generatePlotTypes(self, water_percent=78, shift_plot_types=True,
	                      grain_amount=3):
		# Check for changes to User Input variances.
		self.checkForOverrideDefaultUserInputVariances()

		self.hillsFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount, self.mapRand, 0, self.fracXExp, self.fracYExp)
		self.peaksFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount+1, self.mapRand, 0, self.fracXExp, self.fracYExp)

		water_percent += self.seaLevelChange
		water_percent = min(water_percent, self.seaLevelMax)
		water_percent = max(water_percent, self.seaLevelMin)

		iWaterThreshold = self.continentsFrac.getHeightFromPercent(water_percent)
		iHillsBottom1 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupOneBase - self.hillGroupOneRange), 0))
		iHillsTop1 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupOneBase + self.hillGroupOneRange), 100))
		iHillsBottom2 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupTwoBase - self.hillGroupTwoRange), 0))
		iHillsTop2 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupTwoBase + self.hillGroupTwoRange), 100))
		iPeakThreshold = self.peaksFrac.getHeightFromPercent(self.peakPercent)

		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				i = y*self.iNumPlotsX + x
				val = self.continentsFrac.getHeight(x,y)
				if val <= iWaterThreshold:
					self.plotTypes[i] = PlotTypes.PLOT_OCEAN
				else:
					hillVal = self.hillsFrac.getHeight(x,y)
					if ((hillVal >= iHillsBottom1 and hillVal <= iHillsTop1) or (hillVal >= iHillsBottom2 and hillVal <= iHillsTop2)):
						peakVal = self.peaksFrac.getHeight(x,y)
						if (peakVal <= iPeakThreshold):
							self.plotTypes[i] = PlotTypes.PLOT_PEAK
						else:
							self.plotTypes[i] = PlotTypes.PLOT_HILLS
					else:
						self.plotTypes[i] = PlotTypes.PLOT_LAND

		if shift_plot_types:
			self.shiftPlotTypes()

		return self.plotTypes

class ISHintedWorld(CvMapGeneratorUtil.HintedWorld, ISFractalWorld):
	def __doInitFractal(self):
		self.shiftHintsToMap()

		# don't call base method, this overrides it.
		size = len(self.data)
		minExp = min(self.fracXExp, self.fracYExp)
		iGrain = None
		for i in range(minExp):
			width = (1 << (self.fracXExp - minExp + i))
			height = (1 << (self.fracYExp - minExp + i))
			if not self.iFlags & CyFractal.FracVals.FRAC_WRAP_X:
				width += 1
			if not self.iFlags & CyFractal.FracVals.FRAC_WRAP_Y:
				height += 1
			if size == width*height:
				iGrain = i
		assert(iGrain != None)
		iFlags = self.map.getMapFractalFlags()
		self.continentsFrac.fracInitHints(self.iNumPlotsX, self.iNumPlotsY, iGrain, self.mapRand, iFlags, self.data, self.fracXExp, self.fracYExp)

	def generatePlotTypes(self, water_percent=-1, shift_plot_types=False):
		for i in range(len(self.data)):
			if self.data[i] == None:
				self.data[i] = self.mapRand.get(48, "Generate Plot Types PYTHON")

		self.__doInitFractal()
		if (water_percent == -1):
			numPlots = len(self.data)
			numWaterPlots = 0
			for val in self.data:
				if val < 192:
					numWaterPlots += 1
			water_percent = int(100*numWaterPlots/numPlots)
########## Temudjin START
			# to avoid occational empty sea - not really sure if this works
			if water_percent < 15: water_percent = mst.chooseNumber( 15, 30 )
########## Temudjin END
		# Call superclass
		return ISFractalWorld.generatePlotTypes(self, water_percent, shift_plot_types)

def generatePlotTypes():
#	global hinted_world
	mapRand = gc.getGame().getMapRand()

	NiTextOut("Setting Plot Types (Python Inland Sea) ...")

	hinted_world = ISHintedWorld(4,2)
	area = hinted_world.w * hinted_world.h

	for y in range(hinted_world.h):
		for x in range(hinted_world.w):
			if x in (0, hinted_world.w-1) or y in (0, hinted_world.h-1):
				hinted_world.setValue(x, y, 200 + mapRand.get(55, "Plot Types - Inland Sea PYTHON"))
			else:
				hinted_world.setValue(x, y, 0)

	hinted_world.buildAllContinents()
	return hinted_world.generatePlotTypes()

# subclass TerrainGenerator to eliminate arctic, equatorial latitudes
class ISTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
	def getLatitudeAtPlot(self, iX, iY):
		"returns 0.0 for tropical, up to 1.0 for polar"
########## Temudjin START
		lat = abs(float((self.iHeight-1)/2 - iY)/float((self.iHeight-1)/2)) # 0.0 = equator, 1.0 = pole
		# Adjust latitude using self.variation fractal, to mix things up:
		lat += (128 - self.variation.getHeight(iX, iY))/(255.0 * 5.0)
		# Limit to the range [0, 1]:
		lat = max(0, lat)
		lat = min(lat, 1)
		# Limit to range [0.07, 0.63]
########## Temudjin END
		lat = 0.07 + 0.56*lat
		return lat

# subclass FeatureGenerator to eliminate arctic, equatorial latitudes
class ISFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def getLatitudeAtPlot(self, iX, iY):
		"returns 0.0 for tropical, up to 1.0 for polar"
########## Temudjin START
		lat = abs(float((self.iGridH-1)/2) - iY)/float((self.iGridH-1)/2) 	# range [0,1]
		# Limit to range [0.07, 0.63]
########## Temudjin END
		lat = 0.07 + 0.56*lat
		return lat

def getRiverStartCardinalDirection(argsList):
	pPlot = argsList[0]

	if (pPlot.getY() > ((map.getGridHeight() * 2) / 3)):
		return CardinalDirectionTypes.CARDINALDIRECTION_SOUTH

	if (pPlot.getY() < (map.getGridHeight() / 3)):
		return CardinalDirectionTypes.CARDINALDIRECTION_NORTH

	if (pPlot.getX() > (map.getGridWidth() / 2)):
		return CardinalDirectionTypes.CARDINALDIRECTION_WEST

	return CardinalDirectionTypes.CARDINALDIRECTION_EAST

def getRiverAltitude(argsList):
	pPlot = argsList[0]

	CyPythonMgr().allowDefaultImpl()
	return ((abs(pPlot.getX() - (map.getGridWidth() / 2)) + abs(pPlot.getY() - (map.getGridHeight() / 2))) * 20)
