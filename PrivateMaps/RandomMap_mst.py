#
#	FILE:	    RandomMap_mst.py
#	AUTHOR:     Terkhen (based on Sansimap by sansi)
#	PURPOSE:    Generate random maps following certain map options by randomly selecting a MapScript from a list.
#   DEPENDENCY: Needs MapScriptTools.py
#-----------------------------------------------------------------------------
# CHANGELOG
#-----------------------------------------------------------------------------
#
#  1.1_mst       Terkhen  12.Sep.2016
#     Added, compatibility with Pangaea.
#     Added, compatibility with Archipelago.
#     Added, RandomMap no longer requires all compatible mapscripts to work. If some are missing, it will only list the existing ones.
#     Fixed, RandomMap will use default grid sizes if the mapscript misses the getGridSize method.
#
#  1.0_mst       Terkhen  08.Dic.2014  ( uses MapScriptTools )
#     Added, RandomMap will try to avoid launching exceptions when the chosen mapscript lacks a certain method.
#     Added, save/load map options.
#     Added, weighted randomization of scenarios.
#     Added, support for Earth3, Erebus, Fractured World, Inland Sea, Medium and Small, Planetfall, Sea Highlands and Tectonics.
#     Added, initial version.
#-----------------------------------------------------------------------------

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil

# Universal constants
map = CyMap()

# Helper class which tests if supported MapScripts are present and stores them.
class RMSupportedMapScripts(object):
	def __init__(self):
		# Includes one tuple for each supported MapScript, in the format name, txtId, module, weight.
		self.__mapscripts = list()


	def addMapScript(self, txt, module, weight):
		# Try to get the module.
		importedModule = None
		try:
			importedModule = __import__(module, globals(), locals(), [])
			self.__mapscripts.append([module, txt, importedModule, weight])
		except ImportError:
			print "[RandomMap] Warning: Module for supported MapScript %s not found." % module


	def getNumMapScripts(self):
		return len(self.__mapscripts)


	def getName(self, index):
		return self.__mapscripts[index][0]


	def getTxt(self, index):
		return self.__mapscripts[index][1]


	def getModule(self, index):
		return self.__mapscripts[index][2]


	def getWeight(self, index):
		return self.__mapscripts[index][3]


	def setWeight(self, index, weight):
		self.__mapscripts[index][3] = weight


supportedMapscripts = RMSupportedMapScripts()
# Append any supported MapScripts here, in the format [textID, moduleName, defaultWeight]
supportedMapscripts.addMapScript("TXT_KEY_MAP_SCRIPT_RANDOM_ARCHIPELAGO", "Archipelago_mst", 2)
supportedMapscripts.addMapScript("TXT_KEY_MAP_SCRIPT_RANDOM_EARTH3", "Earth3_mst", 1)
supportedMapscripts.addMapScript("TXT_KEY_MAP_SCRIPT_RANDOM_EREBUS", "Erebus_mst", 2)
supportedMapscripts.addMapScript("TXT_KEY_MAP_SCRIPT_RANDOM_FRACTURED_WORLD", "FracturedWorld_mst", 2)
supportedMapscripts.addMapScript("TXT_KEY_MAP_SCRIPT_RANDOM_INLAND_SEA", "Inland_Sea_mst", 2)
supportedMapscripts.addMapScript("TXT_KEY_MAP_SCRIPT_RANDOM_MEDIUM_AND_SMALL", "Medium_and_Small_mst", 2)
supportedMapscripts.addMapScript("TXT_KEY_MAP_SCRIPT_RANDOM_PANGAEA", "Pangaea_mst", 2)
supportedMapscripts.addMapScript("TXT_KEY_MAP_SCRIPT_RANDOM_PLANETFALL", "PlanetFall_mst", 2)
supportedMapscripts.addMapScript("TXT_KEY_MAP_SCRIPT_RANDOM_SEA_HIGHLANDS", "Sea_Highlands_mst", 2)
supportedMapscripts.addMapScript("TXT_KEY_MAP_SCRIPT_RANDOM_TECTONICS", "Tectonics_mst", 2)


# MapScriptTools Interface by Temudjin.
import MapScriptTools as mst

# Text information about the map script.
def getVersion():
	"""	Returns the version of the map script """
	return "1.1_mst"

def getDescription():
	"""	Returns the description of the map script """
	return "TXT_KEY_MAP_SCRIPT_RANDOM_DESCR"

# Methods called while we are still choosing the map options prior to map generation.

################################################################
## Custom Map Option Interface by Temudjin                 START
################################################################
def setCustomOptions():
	""" Loads custom map options from a cfg file (when possible) and configures all of them in a single place. """
	global op	# { optionID: Name, OptionList, Default, RandomOpt }

	# Initialize options to the default values.
	lMapOptions = list()
	# World wrap.
	lMapOptions.append(1)
	# Resources.
	lMapOptions.append(0)
	# Weights for all present MapScripts.
	for i in range(0, supportedMapscripts.getNumMapScripts()):
		lMapOptions.append(supportedMapscripts.getWeight(i))
	# Coasts / team start
	lMapOptions.append(0)
	# Mars theme / team start
	lMapOptions.append(0)

	# Try to read map options from the cfgFile.
	mst.mapOptionsStorage.initialize(lMapOptions, 'RandomMap')
	lMapOptions = mst.mapOptionsStorage.readConfig()

	# Weight option used for all supported MapScripts.
	optionWeights = [ "TXT_KEY_MAP_SCRIPT_RANDOM_NO", "1", "2", "3", "4" ]

	op = dict()
	# World wrap.
	op[0] = ["TXT_KEY_MAP_SCRIPT_WORLD_WRAP", ["TXT_KEY_MAP_SCRIPT_WORLD_WRAP_FLAT", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_CYLINDRICAL", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_TUBULAR", "TXT_KEY_MAP_SCRIPT_WORLD_WRAP_TOROIDAL"], lMapOptions[0], True]
	# Resources.
	op[1] = ["TXT_KEY_MAP_RESOURCES", ["TXT_KEY_MAP_RESOURCES_STANDARD", "TXT_KEY_MAP_RESOURCES_BALANCED"], lMapOptions[1], True]
	# All present MapScripts.
	for i in range(0, supportedMapscripts.getNumMapScripts()):
		op[i + 2] = [supportedMapscripts.getTxt(i), optionWeights, lMapOptions[i + 2], True]
	# Coasts / team start
	if mst.bPfall:
		op[supportedMapscripts.getNumMapScripts() + 2] = [
			"TXT_KEY_MAP_TEAM_START", ["TXT_KEY_MAP_TEAM_START_NEIGHBORS", "TXT_KEY_MAP_TEAM_START_SEPARATED", "TXT_KEY_MAP_TEAM_START_RANDOM"], lMapOptions[10], False
		]
	else:
		op[supportedMapscripts.getNumMapScripts() + 2] = [
			"TXT_KEY_MAP_COASTS", ["TXT_KEY_MAP_COASTS_STANDARD", "TXT_KEY_MAP_COASTS_EXPANDED"], lMapOptions[10], False
		]
	# Mars theme / team start
	if mst.bMars:
		op[supportedMapscripts.getNumMapScripts() + 3] = [
			"TXT_KEY_MAP_MARS_THEME", ["TXT_KEY_MAP_MARS_THEME_SANDS_OF_MARS", "TXT_KEY_MAP_MARS_THEME_TERRAFORMED_MARS"], lMapOptions[11], False
		]
	elif not mst.bPfall:
		op[supportedMapscripts.getNumMapScripts() + 3] = [
			"TXT_KEY_MAP_TEAM_START", ["TXT_KEY_MAP_TEAM_START_NEIGHBORS", "TXT_KEY_MAP_TEAM_START_SEPARATED", "TXT_KEY_MAP_TEAM_START_RANDOM"], lMapOptions[10], False
		]

	op["Hidden"] = 10

	mst.printDict(op,"Random Map Options:")

def isAdvancedMap():
	""" This map should not show up in simple mode """
	return 1

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
	"""	Indicates if this map script uses the Climate options. """
	# At this point of map generation we still don't know if the map script to be chosen randomly
	# will require this option, so we always request it.
	return True

def isSeaLevelMap():
	"""	Indicates if this map script uses the Sea Level options. """
	# At this point of map generation we still don't know if the map script to be chosen randomly
	# will require this option, so we always request it.
	return True

# Methods called before map generation is initialized.

def beforeInit():
	"""	Obtains a map chosen randomly from the weights given by the user and initializes it. """

	# Map script to be chosen randomly.
	global cms

	# Calculate weights for each map
	pMapScripts = []
	print "[RandomMap] Calculating map script weights..."
	iTotalWeight = 0
	for i in range(0, supportedMapscripts.getNumMapScripts()):
		iWeight = map.getCustomMapOption(i + 2)
		if iWeight > 0:
			pMapScripts.append((iWeight, i))
			iTotalWeight += iWeight
			print "[RandomMap] %s weight: %i (Total weight: %i)" % (supportedMapscripts.getName(i), iWeight, iTotalWeight)

	# If the user chose no map scripts, we will choose a random one between all supported map scripts.
	if len(pMapScripts) == 0:
		print "[RandomMap] No MapScripts selected. Using default list..."
		for i in range(0, supportedMapscripts.getNumMapScripts()):
			iWeight = supportedMapscripts.getWeight(i)
			pMapScripts.append((iWeight, i))
			iTotalWeight += iWeight

	# Choose randomly between all supported mapscripts, taking into account their weights.
	iRand = CyGlobalContext().getGame().getMapRand().get(iTotalWeight, "RandomMap.beforeInit()")
	iCurrentWeight = 0
	iChosenMapScript = -1
	for index in range( len(pMapScripts) ):
		iWeight, iMapScriptIndex = pMapScripts[index]
		iCurrentWeight = iCurrentWeight + iWeight
		sMapScript = supportedMapscripts.getName(iMapScriptIndex)
		print "[RandomMap] %s current weight: %i (Random value: %i)" % (sMapScript, iCurrentWeight, iRand)
		if iRand < iCurrentWeight:
			iChosenMapScript = iMapScriptIndex
			print "[RandomMap] %s has been chosen" % sMapScript
			break

	# Initialize the chosen map script.
	cms = supportedMapscripts.getModule(iChosenMapScript)

	# Map options to be transferred to the chosen map script.
	mapOptionWorldShape = map.getCustomMapOption(0)
	mapOptionResources = map.getCustomMapOption(1)
	mapOptionCoastalWaters = mst.iif(mst.bPfall, None, map.getCustomMapOption(10))
	mapOptionTeamStart = mst.iif(mst.bMars, None, map.getCustomMapOption( mst.iif(mst.bPfall, 10, 11) ))
	mapOptionMarsTheme = mst.iif(mst.bMars, map.getCustomMapOption(11), None)

	# The chosen map script will initialize its map options with these values. All other map options will be set randomly.
	try:
		cmsMethod = getattr(cms, "randomMapBeforeInit")
	except AttributeError:
		print "[RandomMap] Fatal error: %s is not compatible with RandomMap" % sChosenMapScript
	else:
		cmsMethod(mapOptionWorldShape, mapOptionResources, mapOptionCoastalWaters, mapOptionTeamStart, mapOptionMarsTheme)

def getGridSize(argsList):
	"""	Returns the chosen grid size. """
	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	try:
		cmsMethod = getattr(cms, "method")
	except AttributeError:
		[eWorldSize] = argsList
		return  CyGlobalContext().getWorldInfo(eWorldSize).getGridWidth(),\
		        CyGlobalContext().getWorldInfo(eWorldSize).getGridHeight()
	else:
		return cmsMethod(argsList)

def getTopLatitude():
	""" Returns the maximum latitude. This value must be in a [-90, 90] interval. """
	try:
		cmsMethod = getattr(cms, "getTopLatitude")
	except AttributeError:
		return 90
	else:
		return cmsMethod()

def getBottomLatitude():
	""" Returns the minimum latitude. This value must be in a [-90, 90] interval. """
	try:
		cmsMethod = getattr(cms, "getBottomLatitude")
	except AttributeError:
		return -90
	else:
		return cmsMethod()

def getWrapX():
	""" Returns if the map should wrap in the X axis. """
	try:
		cmsMethod = getattr(cms, "getWrapX")
	except AttributeError:
		return False
	else:
		return cmsMethod()

def getWrapY():
	""" Returns if the map should wrap in the Y axis. """
	try:
		cmsMethod = getattr(cms, "getWrapY")
	except AttributeError:
		return False
	else:
		return cmsMethod()

# Methods called before map generation.

def beforeGeneration():
	""" Saves the map options used for this generation and calls beforeGeneration() in the chosen map script. """

	# Obtain the map options in use by RandomMap.
	lMapOptions = []
	for opt in range( getNumCustomMapOptions() ):
		iValue = 0 + map.getCustomMapOption( opt )
		lMapOptions.append( iValue )

	# Save used RandomMap map options.
	mst.mapOptionsStorage.writeConfig(lMapOptions)

	# Call beforeGeneration() in the chosen map script.
	try:
		cmsMethod = getattr(cms, "beforeGeneration")
	except AttributeError:
		return False
	else:
		return cmsMethod()

# Methods called during map generation.

def generatePlotTypes():
	""" FIRST stage in map generation. Calls generatePlotTypes() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "generatePlotTypes")
	except AttributeError:
		return CyPythonMgr().allowDefaultImpl()
	else:
		return cmsMethod()

def generateTerrainTypes():
	""" SECOND stage in map generation. Calls generateTerrainTypes() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "generateTerrainTypes")
	except AttributeError:
		return CyPythonMgr().allowDefaultImpl()
	else:
		return cmsMethod()

def addRivers():
	""" THIRD stage in map generation. Calls addRivers() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "addRivers")
	except AttributeError:
		CyPythonMgr().allowDefaultImpl()
	else:
		cmsMethod()

def addLakes():
	""" FOURTH stage in map generation. Calls addLakes() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "addLakes")
	except AttributeError:
		CyPythonMgr().allowDefaultImpl()
	else:
		cmsMethod()

def addFeatures():
	""" FIFTH stage in map generation. Calls addFeatures() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "addFeatures")
	except AttributeError:
		CyPythonMgr().allowDefaultImpl()
	else:
		cmsMethod()

def addBonuses():
	""" SIXTH stage in map generation. Calls addBonuses() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "addBonuses")
	except AttributeError:
		CyPythonMgr().allowDefaultImpl()
	else:
		cmsMethod()

def isBonusIgnoreLatitude():
	""" Defines if bonus placement should ignore map latitude. Used by the default implementation of addBonuses(), normalizeAddFoodBonuses() and normalizeAddExtras(). Calls isBonusIgnoreLatitude() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "isBonusIgnoreLatitude")
	except AttributeError:
		return False
	else:
		return cmsMethod()

def addGoodies():
	""" SEVENTH stage in map generation. Calls addGoodies() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "addGoodies")
	except AttributeError:
		CyPythonMgr().allowDefaultImpl()
	else:
		cmsMethod()

# Methods called during starting plot normalization.

def normalizeStartingPlotLocations():
	""" FIRST stage in the normalization of starting plots. Calls normalizeStartingPlotLocations() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "normalizeStartingPlotLocations")
	except AttributeError:
		CyPythonMgr().allowDefaultImpl()
	else:
		cmsMethod()

def normalizeAddRiver():
	""" SECOND stage in the normalization of starting plots. Calls normalizeAddRiver() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "normalizeAddRiver")
	except AttributeError:
		CyPythonMgr().allowDefaultImpl()
	else:
		cmsMethod()

def normalizeRemovePeaks():
	""" THIRD stage in the normalization of starting plots. Calls normalizeRemovePeaks() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "normalizeRemovePeaks")
	except AttributeError:
		return CyPythonMgr().allowDefaultImpl()
	else:
		return cmsMethod()

def normalizeAddLakes():
	""" FOURTH stage in the normalization of starting plots. Calls normalizeAddLakes() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "normalizeAddLakes")
	except AttributeError:
		CyPythonMgr().allowDefaultImpl()
	else:
		cmsMethod()

def normalizeRemoveBadFeatures():
	""" FIFTH stage in the normalization of starting plots. Calls normalizeRemoveBadFeatures() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "normalizeRemoveBadFeatures")
	except AttributeError:
		return CyPythonMgr().allowDefaultImpl()
	else:
		return cmsMethod()

def normalizeRemoveBadTerrain():
	""" SIXTH stage in the normalization of starting plots. Calls normalizeRemoveBadTerrain() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "normalizeRemoveBadTerrain")
	except AttributeError:
		CyPythonMgr().allowDefaultImpl()
	else:
		cmsMethod()

def normalizeAddFoodBonuses():
	""" SEVENTH stage in the normalization of starting plots. Calls normalizeAddFoodBonuses() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "normalizeAddFoodBonuses")
	except AttributeError:
		CyPythonMgr().allowDefaultImpl()
	else:
		cmsMethod()

def normalizeAddGoodTerrain():
	""" EIGHT stage in the normalization of starting plots. Calls normalizeAddGoodTerrain() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "normalizeAddGoodTerrain")
	except AttributeError:
		CyPythonMgr().allowDefaultImpl()
	else:
		cmsMethod()

def normalizeAddExtras():
	""" NINTH and last stage in the normalization of starting plots. Calls normalizeAddExtras() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "normalizeAddExtras")
	except AttributeError:
		CyPythonMgr().allowDefaultImpl()
	else:
		cmsMethod()

def minStartingDistanceModifier():
	""" FIRST stage in the selection of starting plots. Calls minStartingDistanceModifier() in the chosen map script. """
	try:
		cmsMethod = getattr(cms, "minStartingDistanceModifier")
	except AttributeError:
			if mst.bPfall: return -25
			if mst.bMars: return -15
			return 0
	else:
		return cmsMethod()

##########
