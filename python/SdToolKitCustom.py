## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
##
## sdToolKit by Stone-D (Laga Mahesa)
## Copyright Laga Mahesa 2005
##
## laga@tbi.co.id
## lmahesa@(yahoo|hotmail|gmail).com
##
## Version 1.22


from CvPythonExtensions import *
import CvUtil
import sys
import cPickle as pickle

gc = CyGlobalContext()
CyGameInstance = gc.getGame()

################# SD-UTILITY-PACK ###################
#-=-=-=-=-=-=-=-= BASIC-UTILITIES =-=-=-=-=-=-=-=-=-#
def sdEcho( echoString ):
	printToScr = True
	printToLog = True
	message = "%s" %(echoString)
	if (printToScr):
		CyInterface().addImmediateMessage(message,"")
	if (printToLog):
		CvUtil.pyPrint(message)
	return 0

def sdGetTimeInt( turn ):
	TurnTable = CyGameTextMgr().getTimeStr(turn, false).split(' ')
	TurnInt   = int(TurnTable[0])
	if (TurnTable[1] == 'BC'):
		TurnInt = 0 - TurnInt
	return TurnInt

def sdGameYearsInt():
	yearsBC = sdGetTimeInt(gc.getGame().getStartTurn())
	if (yearsBC < 0):
		yearsBC = yearsBC - (yearsBC * 2)
	else:
		yearsBC = 0
	yearsAD = 0
	for i in range(gc.getGameSpeedInfo(gc.getGame().getGameSpeedType()).getNumTurnIncrements()):
		yearsAD += gc.getGameSpeedInfo(gc.getGame().getGameSpeedType()).getGameTurnInfo(i).iNumGameTurnsPerIncrement
	yearsAD = sdGetTimeInt(yearsAD)
	if (yearsAD < sdGetTimeInt(gc.getGame().getGameTurn())):
		yearsAD = sdGetTimeInt(gc.getGame().getGameTurn())
	yearsAL = yearsBC + yearsAD
#	sdEcho('yearsBC : %d, yearsAD : %d, All Years : %d' %(yearsBC, yearsAD, yearsAL))
	return yearsAL


#-=-=-=-=-=-=-=-= SD-DATA-STORAGE =-=-=-=-=-=-=-=-=-#
# Every variable is a string, except for the actual
# value you want to store, which can be anything.

#--------------- INTERNAL USE ONLY -----------------#

#   Initializes a central reservoir of custom variables for your mod's use. 'ModID' should be your mod's name.
def sdModInit( ModID ):
	try:
		cyTable = pickle.loads( CyGameInstance.getScriptData() )
	except:
		cyTable = {}
	if ( not cyTable.has_key(ModID) ):
		cyTable = sdModFixCase(ModID, cyTable) # Check for capitalization difference and fix in case of permanent change.
	if ( not cyTable.has_key(ModID) ):
		cyTable[ModID] = pickle.dumps({})	  # Initialize with an empty table.
		sdEcho('Mod Data Initialized : %s %s' %(ModID, cyTable.has_key(ModID)))
	CyGameInstance.setScriptData( pickle.dumps(cyTable) )
	return {}

#   For internal use. You should not use this function.
def sdModFixCase( ModID, cyTable ):
	for i, k in enumerate(cyTable):
		if (k.upper() == ModID.upper()):
			szStringData = cyTable[k]
			cyTable[ModID] = szStringData
			del cyTable[k]
			sdEcho('Mod Data Fixed : %s : %s (was %s)' %(ModID, cyTable.has_key(ModID), k))
			break
	return cyTable

#   Loads previously initialized data from the central reservoir.
def sdModLoad( ModID ):
	try:
		cyTable = pickle.loads( CyGameInstance.getScriptData() )
		mTable  = pickle.loads(cyTable[ModID])
	except:
		mTable  = sdModInit(ModID)
	return mTable

#   Saves a mod's entire variable data to the central reservoir.
def sdModSave( ModID, mTable ):
	try:
		cyTable = pickle.loads( CyGameInstance.getScriptData() )
	except:
		cyTable = sdModInit(ModID)
	cyTable[ModID] = pickle.dumps(mTable)
	CyGameInstance.setScriptData( pickle.dumps(cyTable) )
	return 0


#----------------- MOD FUNCTIONS -------------------#

#   sdEntityInit( 'MyModName', 'UniqueName', Template_dictionary )
#   Initializes a unique data entity (city, unit, plot).
def sdEntityInit( ModID, entity, eTable ):
	mTable = sdModLoad(ModID)
	mTable[entity] = pickle.dumps(eTable)
	sdModSave(ModID, mTable)
	return 0

#   sdEntityWipe( 'MyModName', 'UniqueName' )
#   Removes an entity that has been previously initialized by sdEntityInit.
#   Returns int 0 on failure, int 1 on success.
def sdEntityWipe( ModID, entity ):
	mTable = sdModLoad(ModID)
	if ( mTable.has_key(entity) ):
		del mTable[entity]
		sdModSave(ModID, mTable)
		# sdEcho('Entity Wiped : %s' %(entity))
		return 1
	# sdEcho('Entity Wipe FAILED : %s. Did it exist?' %(entity))
	return 0

#   sdEntityExists( 'MyModName', 'UniqueName' )
#   Checks whether or not an entity has been initialized by sdEntityInit.
#   Returns bool False on failure, bool True on success.
def sdEntityExists( ModID, entity ):
	mTable = sdModLoad(ModID)
	if ( mTable.has_key(entity) ):
		return True
	return False

#   sdGetVal( 'MyModName', 'UniqueName', 'VariableName' )
#   Fetches a specific variable's value from the entity's data set.
def sdGetVal( ModID, entity, var ):
	mTable = sdModLoad(ModID)
	eTable = pickle.loads(mTable[entity])
#	sdEcho('%s : Load : %s, %s = %d' %(ModID, entity, var, eTable[var]))
	return eTable[var]

#   sdSetVal( 'MyModName', 'UniqueName', 'VariableName', any_value )
#   Stores a specific variable's value within the entity's data set.
#   Returns bool False on failure, bool True on success.
def sdSetVal( ModID, entity, var, val ):
	mTable = sdModLoad(ModID)
	if ( mTable.has_key(entity) ):
		eTable		 = pickle.loads(mTable[entity])
		eTable[var]	= val
		mTable[entity] = pickle.dumps(eTable)
		sdModSave(ModID, mTable)
		# sdEcho('%s : sdSetVal : %s, %s = %d' %(ModID, entity, var, eTable[var]))
		return True
	return False

#   sdDelVal( 'MyModName', 'UniqueName', 'VariableName' )
#   Removes a specific variable from the entity's data set.
#   Returns bool False on failure, bool True on success.
def sdDelVal( ModID, entity, var ):
	mTable = sdModLoad(ModID)
	if ( mTable.has_key(entity) ):
		eTable		 = pickle.loads(mTable[entity])
		if ( eTable.has_key(var) ):
			del eTable[var]
			mTable[entity] = pickle.dumps(eTable)
			sdModSave(ModID, mTable)
			# sdEcho('%s : sdDelVal : %s, %s' %(ModID, entity, var))
			return True
	return False

#   sdGetGlobal( 'MyModName', 'GlobalVariableName' )
#   Fetches a specific variable's value from the mod's global data set.
def sdGetGlobal( ModID, var ):
	szGlobal = 'Global'
	mTable   = sdModLoad(ModID)
	if ( mTable.has_key(szGlobal) ):
		eTable	= pickle.loads(mTable[szGlobal])
		if ( eTable.has_key(var) ):
			# sdEcho('%s : sdGetGlobal : %s, %s = %d' %(ModID, szGlobal, var, eTable[var]))
			return eTable[var]

#   sdSetGlobal( 'MyModName', 'GlobalVariableName', any_value )
#   Stores a specific variable's value within the mod's global data set.
def sdSetGlobal( ModID, var, val ):
	szGlobal = 'Global'
	mTable		   = sdModLoad(ModID)
	if ( mTable.has_key(szGlobal) ):
		eTable   = pickle.loads(mTable[szGlobal])
	else:
		eTable   = {}
	eTable[var]	  = val
	mTable[szGlobal] = pickle.dumps(eTable)
	sdModSave(ModID, mTable)

#   sdDelGlobal( 'MyModName', 'GlobalVariableName' )
#   Removes a specific variable from the mod's global data set.
#   Returns bool False on failure, bool True on success.
def sdDelGlobal( ModID, var ):
	szGlobal = 'Global'
	mTable		   = sdModLoad(ModID)
	if ( mTable.has_key(szGlobal) ):
		eTable		   = pickle.loads(mTable[szGlobal])
		if ( eTable.has_key(var) ):
			del eTable[var]
			mTable[szGlobal] = pickle.dumps(eTable)
			sdModSave(ModID, mTable)
			return True
	return False


## Modification by Teg Navanis. While SD-DATA-STORAGE stores
## values in the GameInstance - scriptdata, these functions can be used to store data
## in the scriptdata of an object (for instance a unit, a city or a plot)

## Further modifications by jdog5000

#-=-=-=-=-=-=-=-= SD-OBJECT-DATA-STORAGE =-=-=-=-=-=-=-=-=-#
# Every variable is a string, except for 'object' and the actual
# value you want to store, which can be anything.
# object can be one of the following:
# - CyCity object
# - CyGame object
# - CyPlayer object
# - CyPlot object
# - CyUnit object
# - PyCity object

#--------------- INTERNAL USE ONLY -----------------#

#   Loads previously initialized data from the central reservoir. If no data is found, init it.
def sdLoad( object ):
	try:
		cyTable = pickle.loads(object.getScriptData())
	except:
		cyTable = {}

	if (cyTable == ""):
		cyTable = {}

	return cyTable

#   Loads previously initialized data from the central reservoir. If no data is found, init it.
def sdObjectGetDict( ModID, object ):
	cyTable = sdLoad( object )
	if( cyTable.has_key(ModID) ) :
			return cyTable[ModID]
	else :
			return {}

#   Loads previously initialized data from the central reservoir. If no data is found, init it.
def sdObjectSetDict( ModID, object, VarDictionary ):
	cyTable = sdLoad( object )
	cyTable[ModID] = VarDictionary
	object.setScriptData(pickle.dumps(cyTable))


#----------------- OBJECT FUNCTIONS -------------------#

#   sdObjectInit ( 'MyModName', object, Template_dictionary )
#   Fetches a specific variable's value from the object's data set.
def sdObjectInit (ModID, object, VarDictionary):
	cyTable = sdLoad(object)
	if ( not cyTable.has_key(ModID) ):
		cyTable[ModID] = VarDictionary
		object.setScriptData(pickle.dumps(cyTable))
	return 0


#   sdObjectWipe( 'MyModName', object )
#   Removes an entity that has been previously initialized by sdObjectInit.
#   Returns False on failure, True on success.
def sdObjectWipe( ModID, object ):
	cyTable = sdLoad(object)
	if ( cyTable.has_key(ModID) ):
		del cyTable[ModID]
		object.setScriptData(pickle.dumps(cyTable))
		return True
	return False


#   sdObjectExists( 'MyModName', object )
#   Checks whether or not an object has been initialized by sdObjectInit.
#   Returns bool False on failure, bool True on success.
def sdObjectExists( ModID, object ):
	cyTable = sdLoad(object)
	if ( cyTable.has_key(ModID) ):
		return True
	return False


#   sdObjectGetVal( 'MyModName', object, 'VariableName' )
#   Fetches a specific variable's value from the object's data set.
## Modded by jdog5000: returns None if not found
def sdObjectGetVal( ModID, object, var ):
	cyTable = sdLoad(object)
	try:
		mTable = cyTable[ModID]
		if( var in mTable ) :
			return mTable[var]
		else :
			return None
	except:
		print "Error: initialize object first (getval)!"
		#assert False
		return None

#   sdObjectSetVal( 'MyModName', object, 'VariableName', any_value )
#   Stores a specific variable's value within the object's data set.
#   Returns bool False on failure, bool True on success.
## Modded by jdog5000 to allow creation of new dict elements
def sdObjectSetVal( ModID, object, var, val ):
	cyTable = sdLoad( object )
	try:
		mTable = cyTable[ModID]
	except:
		print "Error: initialize object first (setval on %s)!"%(var)
		return False
	if ( mTable.has_key(var) ):
		mTable[var]	= val
		object.setScriptData(pickle.dumps(cyTable))
		return True
	else :
		mTable[var] = val
		object.setScriptData(pickle.dumps(cyTable))
		return True

#   sdObjectChangeVal( 'MyModName', object, 'VariableName', change_in_value )
#   Updates an existing variable's value within the object's data set.
#   Returns bool False on failure, bool True on success.
def sdObjectChangeVal( ModID, object, var, delta ):
	cyTable = sdLoad( object )
	try:
		mTable = cyTable[ModID]
	except:
		print "Error: initialize object first (changeval)!"
		return False
	prevVal = sdObjectGetVal( ModID, object, var )
	if ( mTable.has_key(var) and not prevVal == None ):
		mTable[var]	= prevVal + delta
		object.setScriptData(pickle.dumps(cyTable))
		return True
	return False

#   sdObjectUpdateVal( 'MyModName', object, 'VariableName', any_value )
#   Updates an existing variable's value within the object's data set.
#   Returns bool False on failure, bool True on success.
def sdObjectUpdateVal( ModID, object, var, val ):
	cyTable = sdLoad( object )
	try:
		mTable = cyTable[ModID]
	except:
		print "Error: initialize object first (updateval)!"
		return False
	if ( mTable.has_key(var) ):
		mTable[var]	= val
		object.setScriptData(pickle.dumps(cyTable))
		return True
	else :
		print 'Error: object not initialized with var: %s'%(var)
	return False
