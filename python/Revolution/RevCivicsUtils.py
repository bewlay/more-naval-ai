# Civics functions for Revolution Mod
#
# by jdog5000
# Version 1.5

from CvPythonExtensions import *
import CvUtil
import PyHelpers
import pickle
# --------- Revolution mod -------------
import RevDefs
import RevData
import SdToolKitCustom
import RevInstances


# globals
gc = CyGlobalContext()
PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo
game = CyGame()
localText = CyTranslator()

LOG_DEBUG = True

# civicsList[0] is a list of all civics of option type 0
civicsList = list()


def initCivicsList( ) :

	CvUtil.pyPrint("  Revolt - Initializing Civics List")

	global civicsList
	
	civicsList = list()

	for i in range(0,gc.getNumCivicOptionInfos()) :
		civicsList.append(list())

	for i in range(0,gc.getNumCivicInfos()) :
		kCivic = gc.getCivicInfo(i)
		civicsList[kCivic.getCivicOptionType()].append(i)


########################## Civics effect helper functions #####################


def getCivicsHolyCityEffects( iPlayer ) :

	pPlayer = gc.getPlayer(iPlayer)

	if( pPlayer.isNone() ) :
		return [0,0]

	if( pPlayer.getNumCities() == 0 ) :
		return [0,0]

	goodEffect = 0
	badEffect = 0

	for i in range(0,gc.getNumCivicOptionInfos()) :
		iCivic = pPlayer.getCivics(i)
		if( iCivic >= 0 ) :
			kCivic = gc.getCivicInfo(iCivic)
			goodEffect += kCivic.getRevIdxEffects().getRevIdxHolyCityOwned()
			badEffect += kCivic.getRevIdxEffects().getRevIdxHolyCityHeathenOwned()

	return [goodEffect,badEffect]

def canDoCommunism( iPlayer ) :
	pPlayer = gc.getPlayer(iPlayer)

	if( pPlayer.isNone() or not pPlayer.isAlive() ) :
		return [False,None]

	for i in range(0,gc.getNumCivicInfos()) :
		kCivic = gc.getCivicInfo(i)
		if( kCivic.isCommunism() and pPlayer.canDoCivics(i) ) :
			if( not pPlayer.isCivic(i) ) :
				return [True,i]

	return [False,None]

def isCommunism( iPlayer ) :
	pPlayer = gc.getPlayer(iPlayer)

	if( pPlayer.isNone() or not pPlayer.isAlive() ) :
		return False

	for i in range(0,gc.getNumCivicInfos()) :
		kCivic = gc.getCivicInfo(i)
		if( kCivic.isCommunism() and pPlayer.isCivic(i) ) :
				return True

	return False

def canDoFreeSpeech( iPlayer ) :
	pPlayer = gc.getPlayer(iPlayer)

	if( pPlayer.isNone() or not pPlayer.isAlive() ) :
		return [False,None]

	for i in range(0,gc.getNumCivicInfos()) :
		kCivic = gc.getCivicInfo(i)
		if( kCivic.isFreeSpeech() and pPlayer.canDoCivics(i) ) :
			if( not pPlayer.isCivic(i) ) :
				return [True,i]

	return [False,None]

def isFreeSpeech( iPlayer ) :
	pPlayer = gc.getPlayer(iPlayer)

	if( pPlayer.isNone() or not pPlayer.isAlive() ) :
		return False

	for i in range(0,gc.getNumCivicInfos()) :
		kCivic = gc.getCivicInfo(i)
		if( kCivic.isFreeSpeech() and pPlayer.isCivic(i) ) :
				return True

	return False

def isCanDoElections( iPlayer ) :
	pPlayer = gc.getPlayer(iPlayer)

	if( pPlayer.isNone() or not pPlayer.isAlive() or pPlayer.isBarbarian() ) :
		return False

	for i in range(0,gc.getNumCivicOptionInfos()) :
		iCivic = pPlayer.getCivics(i)
		if( iCivic >= 0 ) :
			kCivic = gc.getCivicInfo(iCivic)
			if( kCivic.isCanDoElection() ) :
				return True


	return False

def getReligiousFreedom( iPlayer ) : # LFGR_TODO: This potentially only looks at a single category
	# Returns [freedom level, option type]

	pPlayer = gc.getPlayer(iPlayer)

	if( pPlayer.isNone() or not pPlayer.isAlive() ) :
		return [0,None]

	for i in range(0,gc.getNumCivicOptionInfos()) :
		iCivic = pPlayer.getCivics(i)
		if( iCivic >= 0 ) :
			kCivic = gc.getCivicInfo(iCivic)
			if( not kCivic.getRevReligiousFreedom() == 0 ) :
				return [kCivic.getRevReligiousFreedom(),i]

	return [0,None]


def getBestReligiousFreedom( iPlayer, relOptionType ) :
	# Returns [best level, civic type]

	pPlayer = gc.getPlayer(iPlayer)

	if( pPlayer.isNone() or not pPlayer.isAlive() or relOptionType == None ) :
		return [0,None]

	bestFreedom = -11
	bestCivic = None

	for i in civicsList[relOptionType] :
		kCivic = gc.getCivicInfo(i)
		civicFreedom = kCivic.getRevReligiousFreedom()
		if( pPlayer.canDoCivics(i) and not civicFreedom == 0 ) : # LFGR_TODO: This may prefer negative over 0...
			if( kCivic.getRevReligiousFreedom() > bestFreedom ) :
				bestFreedom = civicFreedom
				bestCivic = i

	return [bestFreedom, bestCivic]

def getDemocracyLevel( iPlayer ) :
	# Returns [level, option type]

	pPlayer = gc.getPlayer(iPlayer)

	if( pPlayer.isNone() or not pPlayer.isAlive() ) :
		return [0,None]

	for i in range(0,gc.getNumCivicOptionInfos()) :
		iCivic = pPlayer.getCivics(i)
		if( iCivic >= 0 ) :
			kCivic = gc.getCivicInfo(iCivic)
			if( not kCivic.getRevDemocracyLevel() == 0 ) :
				return [kCivic.getRevDemocracyLevel(),i]

	return [0,None]


def getBestDemocracyLevel( iPlayer, optionType ) :
	# Returns [best level, civic type]

	pPlayer = gc.getPlayer(iPlayer)

	if( pPlayer.isNone() or not pPlayer.isAlive() or optionType == None ) :
		return [0,None]

	bestLevel = -11
	bestCivic = None

	for i in civicsList[optionType] :
		kCivic = gc.getCivicInfo(i)
		civicLevel = kCivic.getRevDemocracyLevel()
		if( pPlayer.canDoCivics(i) and not civicLevel == 0 ) :
			if( civicLevel > bestLevel ) :
				bestLevel = civicLevel
				bestCivic = i

	return [bestLevel, bestCivic]

def getLaborFreedom( iPlayer ) :
	# Returns [level, option type]

	pPlayer = gc.getPlayer(iPlayer)

	if( pPlayer.isNone() or not pPlayer.isAlive() ) :
		return [0,None]

	for i in range(0,gc.getNumCivicOptionInfos()) :
		iCivic = pPlayer.getCivics(i)
		if( iCivic >= 0 ) :
			kCivic = gc.getCivicInfo(iCivic)
			if( not kCivic.getRevLaborFreedom() == 0 ) :
				return [kCivic.getRevLaborFreedom(),i]

	return [0,None]


def getBestLaborFreedom( iPlayer, optionType ) :
	# Returns [best level, civic type]

	pPlayer = gc.getPlayer(iPlayer)

	if( pPlayer.isNone() or not pPlayer.isAlive() or optionType == None ) :
		return [0,None]

	bestLevel = -11
	bestCivic = None

	for i in civicsList[optionType] :
		kCivic = gc.getCivicInfo(i)
		civicLevel = kCivic.getRevLaborFreedom()
		if( pPlayer.canDoCivics(i) and not civicLevel == 0 ) :
			if( civicLevel > bestLevel ) :
				bestLevel = civicLevel
				bestCivic = i

	return [bestLevel, bestCivic]

def getEnvironmentalProtection( iPlayer ) :
	# Returns [level, option type]

	pPlayer = gc.getPlayer(iPlayer)

	if( pPlayer.isNone() or not pPlayer.isAlive() ) :
		return [0,None]

	for i in range(0,gc.getNumCivicOptionInfos()) :
		iCivic = pPlayer.getCivics(i)
		if( iCivic >= 0 ) :
			kCivic = gc.getCivicInfo(iCivic)
			if( not kCivic.getRevEnvironmentalProtection() == 0 ) :
				return [kCivic.getRevEnvironmentalProtection(),i]

	return [0,None]


def getBestEnvironmentalProtection( iPlayer, optionType ) :
	# Returns [best level, civic type]

	pPlayer = gc.getPlayer(iPlayer)

	if( pPlayer.isNone() or not pPlayer.isAlive() or optionType == None ) :
		return [0,None]

	bestLevel = -11
	bestCivic = None

	for i in civicsList[optionType] :
		kCivic = gc.getCivicInfo(i)
		civicLevel = kCivic.getRevEnvironmentalProtection()
		if( pPlayer.canDoCivics(i) and not civicLevel == 0 ) :
			if( civicLevel > bestLevel ) :
				bestLevel = civicLevel
				bestCivic = i

	return [bestLevel, bestCivic]