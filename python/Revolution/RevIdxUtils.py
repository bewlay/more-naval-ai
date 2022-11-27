"""
Refactor of RevIdx part of Revolution modcomp, for Fall from Heaven 2/MNAI

All calculations for local and national RevIdx will ultimately be moved here.

Below are changes made, most here, some still in Revolution.py.

Local rev idx changes:
* Removed effects of hardcoded "Nationalism", "Liberalism" and "Scientific Method" techs.
* Instability from nationality no longer reduces the garrison RevIdx cap
* Removed small capital malus in later eras ("To help remove late game tiny civs" -- we don't want that)
* Removed malus for small cities that used to be large
* Streamlined small city bonus
* No unhappiness malus in city with disorder.
* Removed colony malus, "revolutionary spirit
* Current era not subtracted from culture rate
* Removed malus from negative food per turn
* Simplified and streamlined unhealthiness, nationality, health and garrison indices
* No increased civic malus if "better" civics are available
* Building effects not disabled from wrong PrereqCiv or PrereqTrait
* Slightly changed combination of final general and human modifiers (does nothing by default)
* Slightly changed the religion bonus when at war
* Slightly changed the unhappiness malus, now uses the new DLL method CyCity.unhappyLevelForRevIdx()
* Route bonus in location RevIdx now considers all technology changes to the city's actual route
* Location rev idx incorporates civ size more smoothly
* Civic/Building location rev idx boni now do what they seem
* Location rev idx calculates distance from nearest gov. center, not only capital
* Location rev idx can't be negative (a good comm bonus otherwise makes the bonus worse)
* Settlements do not get RevIdx from starvation (since they always starve down to 1 pop after conquest)

National rev idx changes:
* Removed distinction between RevIdx and Stability. The latter was almost, but not quite, the negation of the former.
	Stability seemed to have no effect other than for display purposes. Now Stability = -RevIdx.
* Streamlined small empire bonus and apply it to RevIdx (not just stability)
* Culture spending is now actually added to the national RevIdx
* Removed wonky "financial trouble" factor.
* No increased civic malus if "better" civics are available
* Civics now added to national RevIdx (instead of only "stability")
* Building effects not disabled from wrong PrereqCiv or PrereqTrait
* Removed late-game penalty for players with large military
* Removed (only partly working) anarchy penalty of 100 (40 for rebels) (LFGR_TODO: Should be added as an RevIdx-changing event)
* Slightly changed combination of final general and human modifiers (does nothing by default)
"""


from CvPythonExtensions import *

# Just for IDE, does only work with python 2.7
try : from typing import *
except ImportError : pass

import math

from PyHelpers import getText, PyPlayer

import BugCore
import CvUtil
#import GCUtils
import RevDefs
import RevUtils


# Globals
RevOpt = BugCore.game.Revolution
gc = CyGlobalContext()
#gcu = GCUtils.GCUtils()
game = CyGame()


# Constants
SEPARATOR = u"-----------------------"
NL_SEPARATOR = u"\n" + SEPARATOR


# Source: https://stackoverflow.com/questions/15390807/integer-square-root-in-python
def isqrt( n ) :
	"""
	Newton's method for exact integer square root.
	Avoids floating-point arithmetic for multiplayer
	"""
	x = n
	y = (x + 1) // 2
	while y < x:
		x = y
		y = (x + n // x) // 2
	return x


def coloredRevIdxFactorStr( iRevIdx ) :
	""" Color a single factor with green to red. For, e.g., help text """
	if iRevIdx < -10 :
		sColor = "<color=20,230,20,255>"
	elif iRevIdx < -5 :
		sColor = "<color=50,230,50,255>"
	elif iRevIdx < -2 :
		sColor = "<color=100,230,100,255>"
	elif iRevIdx < 0 :
		sColor = "<color=150,230,150,255>"
	elif iRevIdx == 0 :
		sColor = None
	elif iRevIdx <= 2 :
		sColor = "<color=225,150,150,255>"
	elif iRevIdx <= 5 :
		sColor = "<color=225,100,100,255>"
	elif iRevIdx <= 10 :
		sColor = "<color=225,75,75,255>"
	elif iRevIdx <= 20 :
		sColor = "<color=225,50,50,255>"
	else :
		sColor = "<color=255,10,10,255>"

	if iRevIdx != 0 :
		sRevIdx = ("%+d" % iRevIdx)  # Show + or minus sign
	else :
		sRevIdx = str( iRevIdx )
	if sColor is not None :
		return sColor + sRevIdx + "</color>"
	else :
		return sRevIdx

def effectsToIdxAndHelp( effects ) :
	# type: ( Iterable[Tuple[CvInfoBase, int]] ) -> Tuple[int, unicode]
	""" Aggregate a set of (info, iEffect) tuples into a total effect and help text. """
	iTotalIdx = 0
	szHelp = u""
	for info, iRevIdx in effects :
		iTotalIdx += iRevIdx
		if szHelp != u"" : szHelp += u"\n"
		szHelp += getText( "[ICON_BULLET]%s1: %s2", info.getTextKey(), coloredRevIdxFactorStr( iRevIdx ) )
	return iTotalIdx, szHelp

def effectsToRevWatchData( effects ) : # TODO: Deprecated
	# type: ( Iterable[Tuple[Union[CvInfoBase, unicode], int]] ) -> Tuple[int, List[Tuple[int, unicode]], List[Tuple[int, unicode]]]
	""" Aggregate a set of (info, iEffect) tuples into a total effect, a positive list, and negative list. """
	iTotal = 0
	posList = []
	negList = []
	for cause, iRevIdx in effects :
		iTotal += iRevIdx
		if isinstance( cause, CvInfoBase ) :
			desc = cause.getDescription()
		else :
			desc = cause
		if iRevIdx > 0 :
			negList.append( (iRevIdx, desc) )
		else :
			posList.append( (iRevIdx, desc) )
	return iTotal, posList, negList

def adjustedRevIdxAndFinalModifierHelp( iRawIdx, pPlayer, bColorFinalIdx = False ) :
	# type (int, CyPlayer) -> (int, unicode)
	"""
	Adjust given raw RevIdx for Game speed and other modifiers. Used for both local and national RevIdx.
	Help string documents changes and stars with "\n" if is not empty.

	bColorFinalIdx indicates whether the final adjusted index should be colored
	"""
	szHelp = u""

	# Adjust index accumulation for varying game speeds
	fGameSpeedMod = RevUtils.getGameSpeedMod()
	if fGameSpeedMod != 1 :
		szHelp += u"\n" + getText( "[ICON_BULLET]Game speed modifier: %D1%", modAsPercent( fGameSpeedMod ) )

	fMod = RevOpt.getIndexModifier()  # TODO: Make constant
	if pPlayer.isHuman() :
		fMod *= RevOpt.getHumanIndexModifier()  # TODO: Make constant
	if fMod != 1 :
		szHelp += u"\n" + getText( "[ICON_BULLET]Modifier: %D1%", modAsPercent( fMod ) )

	iOffset = int( RevOpt.getIndexOffset() )  # TODO: Make int constant
	if pPlayer.isHuman() :
		iOffset += int( RevOpt.getHumanIndexOffset() )  # TODO: Make int constant
	if iOffset != 0 :
		szHelp += u"\n" + getText( "[ICON_BULLET]Offset: %D1[ICON_INSTABILITY]", iOffset )

	iAdjustedIdx = int( fGameSpeedMod * fMod * iRawIdx + iOffset + .5 )

	if szHelp != u"" :
		if bColorFinalIdx :
			szHelp += NL_SEPARATOR + u"\n" + getText( "Adjusted: %s1", coloredRevIdxFactorStr( iAdjustedIdx ) )
		else :
			szHelp += NL_SEPARATOR + u"\n" + getText( "Adjusted: %D1", iAdjustedIdx )

	return iAdjustedIdx, szHelp

def modAsPercent( fMod ) :
	""" Converts a modifier such as 0.7 to a percentage such as -30 """
	return int( ( fMod - 1 ) * 100 )

def canRevolt( pCity ) :
	# type: ( CyCity ) -> bool
	if pCity.isSettlement() and pCity.getOwner() == pCity.getOriginalOwner() :
		return False

	return True



class NationalEffectBuildingsInfoCache :
	""" Caches all building(type)s that have an effect on all cities"""

	_instance = None

	def __init__( self ) :
		self._leBuildings = []
		for eBuilding in range( gc.getNumBuildingInfos() ) :
			kBuilding = gc.getBuildingInfo( eBuilding )
			if kBuilding.getRevIdxNational() != 0 :
				self._leBuildings.append( eBuilding )

	def __iter__( self ) :
		return iter( self._leBuildings )

	@staticmethod
	def getInstance() :
		# type: () -> NationalEffectBuildingsInfoCache
		if NationalEffectBuildingsInfoCache._instance is None :
			NationalEffectBuildingsInfoCache._instance = NationalEffectBuildingsInfoCache()
		return NationalEffectBuildingsInfoCache._instance


class PlayerRevIdxCache :
	""" Caches buildings with national rev effect for a single player. """
	def __init__( self, ePlayer ) :
		# type : (int) -> None
		self._ePlayer = ePlayer
		self._pPlayer = gc.getPlayer( ePlayer )
		self._buildingsCache = None

	def _buildingsWithNationalEffects( self ) :
		""" Un-cached function"""
		for eBuilding in NationalEffectBuildingsInfoCache.getInstance() :
			iCount = 0
			for pCity in PyPlayer( self._ePlayer ).iterCities() :
				if pCity.isHasBuilding( eBuilding ) :
					iCount += 1

			if iCount > 0 :
				kBuilding = gc.getBuildingInfo( eBuilding )
				iRevIdx = kBuilding.getRevIdxNational()
				if iRevIdx != 0 :
					yield kBuilding, iRevIdx * iCount

	def buildingsWithNationalEffects( self ) :
		# type: () -> Sequence[Tuple[CvBuildingInfo, int]]
		"""
		Returns a collection of buildings and associated RevIndices that have a nationwide effect.
		"""
		if self._buildingsCache is None :
			self._buildingsCache = tuple( self._buildingsWithNationalEffects() )
		return self._buildingsCache


class CityRevIdxHelper :
	"""
	Helper class to calculate a city's RevIdx (per turn).
	WARNING: Only use temporarily, should not be stored, as some caching happens.
	"""
	def __init__( self, pCity, pPlayerCache ) :
		# type: (CyCity, PlayerRevIdxCache) -> None
		self._pCity = pCity
		self._pPlayerCache = pPlayerCache

		# Player stuff
		self._eOwner = self._pCity.getOwner()
		self._pOwner = gc.getPlayer( self._eOwner ) # type: CyPlayer
		self._pyOwner = PyPlayer( self._eOwner )
		self._eOwnerTeam = self._pOwner.getTeam()
		self._pOwnerTeam = gc.getTeam( self._eOwnerTeam )
		self._iTurnsSinceAcquisition = game.getGameTurn() - pCity.getGameTurnAcquired()

		# self._leBuildings = []
		self._lpBuildings = []
		for eBuilding in xrange( gc.getNumBuildingInfos() ) :
			if self._pCity.isHasBuilding( eBuilding ) :
				# self._leBuildings.append( eBuilding )
				self._lpBuildings.append( gc.getBuildingInfo( eBuilding ) )

		# Caching
		self._dCacheStateReligionConflict = None # type: Optional[Dict[Tuple[int, int], int]]
		self._dCachePresentReligionConflict = None # type: Optional[Dict[Tuple[int, int], int]]
	
	def getCity( self ) :
		# type: () -> CyCity
		return self._pCity

	def cannotRevoltStr( self ) :
		# type: () -> Optional[str]
		"""
		If the city can (generally) revolt, returns None. Otherwise, returns a string explaining why it can't.
		"""
		if self._pCity.isSettlement() and self._pCity.getOwner() == self._pCity.getOriginalOwner() :
			return "Settlements you founded cannot revolt" # TODO: Translation
		return None


	def computeHappinessRevIdx( self ) :
		return self.computeHappinessRevIdxAndHelp()[0]

	def computeHappinessModifiersTimes100AndHelp( self, bUnhappiness ) :
		# type: (bool) -> Tuple[int, unicode]
		iMod = 100
		szHelp = u""

		if bUnhappiness :
			iRecentAcquisitionMod = min( 2*(self._iTurnsSinceAcquisition - 15), 0 ) # TODO: Make this a general effect for all instability?
			if iRecentAcquisitionMod < 0 :
				iMod += iRecentAcquisitionMod
				szHelp += u"\n"
				szHelp += getText( "[ICON_BULLET]%D1% from recent acquisition (%d2 turns)",
						iRecentAcquisitionMod, self._iTurnsSinceAcquisition )

		if self._pCity.isUnhappyProduction() :
			iUnhappyProduction = -50 # TODO: Separate into new tag?
			szHelp += u"\n"
			szHelp += getText( "[ICON_BULLET]%D1% from unhappiness production", iUnhappyProduction ) # TODO: say Building
			iMod += iUnhappyProduction

		return iMod, szHelp

	def computeHappinessRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]

		szHelp = getText( "[COLOR_HIGHLIGHT_TEXT]Happiness/Unhappiness[COLOR_REVERT]" )

		# TODO: Remove all the floating point arithmetic, maybe simplify
		iNumUnhappy = self._pCity.unhappyLevel(0) - self._pCity.happyLevel()
		#iNumUnhappy = RevUtils.getModNumUnhappy( self._pCity, RevOpt.getWarWearinessMod() )

		if iNumUnhappy > 0 :
			if self._pCity.getOccupationTimer() > 0 :
				szHelp += u"\n"
				szHelp += getText( "(No effect while in disorder)" )
				return 0, szHelp

			# Base unhappiness, recalculated
			iNumUnhappy = max( 0, self._pCity.unhappyLevelForRevIdx( 0 ) - self._pCity.happyLevel() )

			szHelp += u"\n"
			szHelp += getText( "Ignoring some factors: %d1[ICON_UNHAPPY]", iNumUnhappy )

			iBaseHappyIdx = 100 * iNumUnhappy // self._pCity.getPopulation()

			# Cap
			iCap = min( 100, 10 * self._pCity.getPopulation() )
			if iBaseHappyIdx > iCap :
				iCappedHappyIdx = iCap
				szCapHelp = u"\n" + getText( "[ICON_BULLET]Max. from population: %D1[ICON_INSTABILITY]", iCap )
			else :
				iCappedHappyIdx = iBaseHappyIdx
				szCapHelp = u""

			# Modifiers
			iModTimes100, szModHelp = self.computeHappinessModifiersTimes100AndHelp( bUnhappiness = True )
			iHappyIdx = iCappedHappyIdx * max( 0, iModTimes100 ) // 100

			# Possibly add subtotal
			if szCapHelp or szModHelp :
				szHelp += u"\n"
				szHelp += getText( "Base effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iBaseHappyIdx ) )
				szHelp += szCapHelp
				szHelp += szModHelp

			szHelp += NL_SEPARATOR
			szHelp += u"\n"
			szHelp += getText( "From unhappiness: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iHappyIdx ) )
			return iHappyIdx, szHelp
		elif iNumUnhappy < 0 :
			szHelp += u"\n"
			szHelp += getText( "Excess happiness: %d1[ICON_HAPPY]", -iNumUnhappy )

			iBaseHappyIdx = min( 10, 10 * iNumUnhappy // self._pCity.getPopulation() )

			# Modifiers
			iModTimes100, szModHelp = self.computeHappinessModifiersTimes100AndHelp( bUnhappiness = False )
			iHappyIdx = iBaseHappyIdx * max( 0, iModTimes100 ) // 100

			# Possibly add subtotal
			if szModHelp :
				szHelp += u"\n"
				szHelp += getText( "Base effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iBaseHappyIdx ) )
				szHelp += szModHelp
			
			szHelp += NL_SEPARATOR
			szHelp += u"\n"
			szHelp += getText( "From happiness: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iHappyIdx ) )

			return iHappyIdx, szHelp
		else :
			return 0, szHelp + u"\n" + getText( "City is neither happy nor unhappy" )


	def _cityDistance(self, pOtherCity ) :
		# type: (CyCity) -> int
		return plotDistance( self._pCity.getX(), self._pCity.getY(), pOtherCity.getX(), pOtherCity.getY() )

	def computeLocationRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]

		szHelp = getText( "[COLOR_HIGHLIGHT_TEXT]Location[COLOR_REVERT]" )

		# Raw distance to government center
		iCityDistRaw = None
		for pyCity in self._pyOwner.iterCities() :
			if pyCity.isGovernmentCenter() :
				fDist = self._cityDistance( pyCity.GetCy() )
				if iCityDistRaw is None or iCityDistRaw > fDist :
					iCityDistRaw = fDist

		if iCityDistRaw is not None :
			iDistMod = gc.getWorldInfo( CyMap().getWorldSize() ).getDistanceMaintenancePercent()
			iMaxPlotDist = CyMap().maxPlotDistance()
			iAdjDistTimes100 = iCityDistRaw * (100 + iDistMod) / iMaxPlotDist
			szHelp += u"\n" + getText( "Distance to palace: %d1", iAdjDistTimes100 )
		else :
			iAdjDistTimes100 = 100
			szHelp += u"\n" + getText( "You don't have a palace!" )

		# Base instability
		iBaseIdx = 135 * iAdjDistTimes100 * ( 7 + self._pCity.getPopulation() ) // 1000

		# Modifiers
		iMod = 100
		szModHelp = u""

		pCapital = self._pOwner.getCapitalCity()
		if pCapital is not None and not pCapital.isNone() and not self._pCity.isConnectedTo( pCapital ) :
			iDisconnectMod = +100 # TODO: Make setting
			iMod += iDisconnectMod
			szModHelp += u"\n" + getText( "[ICON_BULLET]%D1% since disconnected from capital", iDisconnectMod )

		if self._pCity.getMaxAirlift() > 0 :
			iAirliftMod = -50 # TODO: Make setting
			iMod += iAirliftMod
			szModHelp += u"\n" + getText( "[ICON_BULLET]%D1% from teleportation", iAirliftMod )

		for pCivic in self._pyOwner.iterCivicInfos() :
			iCivicMod = pCivic.getRevIdxDistanceModifier()
			if iCivicMod != 0 :
				iMod += iCivicMod
				szModHelp += u"\n"
				szModHelp += getText( "[ICON_BULLET]%D1% from [COLOR_CIVIC_TEXT]%s2[COLOR_REVERT]",
						iCivicMod, pCivic.getDescription() )

		if szModHelp :
			szHelp += u"\n" + getText( "Base effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iBaseIdx ) )
			szHelp += szModHelp

		iLocationRevIdx = iBaseIdx * max( 0, iMod ) // 100

		# Cap
		iCap = 100 # TODO: Make setting
		iLocationRevIdx = min( iCap, iLocationRevIdx )

		szHelp += NL_SEPARATOR
		szHelp += u"\n" + getText( "Location effect: %s1[ICON_INSTABILITY] (max: %d2)", coloredRevIdxFactorStr( iLocationRevIdx ), iCap )

		return iLocationRevIdx, szHelp

	def computeLocationRevIdx( self ) :
		# type: () -> int
		return self.computeLocationRevIdxAndHelp()[0]


	def _computeReligionConflictCache( self ) :
		# type: () -> None
		# TODO: Make this XML?
		leGoods = [gc.getInfoTypeForString( "RELIGION_THE_ORDER" )]
		leGoodNeutrals = [gc.getInfoTypeForString( "RELIGION_RUNES_OF_KILMORPH" ),
				gc.getInfoTypeForString( "RELIGION_THE_EMPYREAN" )]
		leEvilNeutrals = [gc.getInfoTypeForString( "RELIGION_OCTOPUS_OVERLORDS" ),
				gc.getInfoTypeForString( "RELIGION_COUNCIL_OF_ESUS" )]
		leEvils = [gc.getInfoTypeForString( "RELIGION_THE_ASHEN_VEIL" )]

		self._dCacheStateReligionConflict = {}
		self._dCachePresentReligionConflict = {}

		for eGRel in leGoods :
			for eENRel in leEvilNeutrals :
				self._dCacheStateReligionConflict[eGRel, eENRel] = 3
				self._dCacheStateReligionConflict[eENRel, eGRel] = 3
			for eERel in leEvils :
				self._dCacheStateReligionConflict[eGRel, eERel] = 5
				self._dCacheStateReligionConflict[eERel, eGRel] = 5
				self._dCachePresentReligionConflict[eGRel, eERel] = 1
				self._dCachePresentReligionConflict[eERel, eGRel] = 1
		for eGNRel in leGoodNeutrals :
			for eENRel in leEvilNeutrals :
				self._dCacheStateReligionConflict[eGNRel, eENRel] = 2
				self._dCacheStateReligionConflict[eENRel, eGNRel] = 2
			for eERel in leEvils :
				self._dCacheStateReligionConflict[eGNRel, eERel] = 3
				self._dCacheStateReligionConflict[eERel, eGNRel] = 3

	def getStateReligionConflict( self, eReligion ) :
		# type: (int) -> int
		eStateReligion = self._pOwner.getStateReligion()
		if eStateReligion != -1 :
			if self._dCacheStateReligionConflict is None :
				self._computeReligionConflictCache()
			return self._dCacheStateReligionConflict.get( (eStateReligion, eReligion), 1 )
		else :
			return 0

	def getPresentReligionsConflict( self, eReligion1, eReligion2 ) :
		# type: (int, int) -> int
		if self._dCachePresentReligionConflict is None :
			self._computeReligionConflictCache()
		return self._dCachePresentReligionConflict.get( (eReligion1, eReligion2), 0 )

	def computeReligionRevIndexAndHelp( self ) :
		# type: () -> Tuple[int, unicode]
		eStateReligion = self._pOwner.getStateReligion()

		lszHelpLines = [getText( "[COLOR_HIGHLIGHT_TEXT]Religions[COLOR_REVERT]" )]

		if eStateReligion != -1 :
			iGoodIdx = 0
			iBadIdx = 0
			lszGoodHelpLines = [] # type: List[unicode]
			lszBadHelpLines = [] # type: List[unicode]

			pStateReligion = gc.getReligionInfo( eStateReligion )

			# Prepartion: do we own the holy city?
			bOwnHolyCity = False
			bInfidelsOwnHolyCity = False
			pStateHolyCity = game.getHolyCity( eStateReligion )
			if not pStateHolyCity.isNone() :
				eHolyCityOwner = pStateHolyCity.getOwner()
				if eHolyCityOwner == self._eOwner :
					bOwnHolyCity = True
				elif gc.getPlayer( eHolyCityOwner ).getStateReligion() != eStateReligion :
					bInfidelsOwnHolyCity = True

			# State religion in city
			if self._pCity.isHasReligion( eStateReligion ) :
				if self._pCity.isHolyCityByType( eStateReligion ) :
					iStateHolyCityBonus = -8 # TODO
					iGoodIdx += iStateHolyCityBonus
					lszGoodHelpLines.append( getText( "%F2 in city: %D1[ICON_INSTABILITY]", iStateHolyCityBonus, pStateReligion.getHolyCityChar() ) )
				else :
					iStateRelBonus = -4 # TODO
					iGoodIdx += iStateRelBonus
					lszGoodHelpLines.append( getText( "%F2 in city: %D1[ICON_INSTABILITY]", iStateRelBonus, pStateReligion.getChar() ) )

				# War bonus: Half of usual religion bonus
				iBestWarConflict = 0
				for pyPlayer in self._pyOwner.iterCivPyPlayersAtWar() :
					iBestWarConflict = max( iBestWarConflict,
							self.getStateReligionConflict( pyPlayer.getStateReligion() ) )
				iHolyWarIdx = - iBestWarConflict // 2
				if iHolyWarIdx != 0 :
					iGoodIdx += iHolyWarIdx
					lszGoodHelpLines.append( getText( "War against infidels: %D1[ICON_INSTABILITY]", iHolyWarIdx ) )

			# Holy city bonus
			for pCivic in self._pyOwner.iterCivicInfos() :
				iGoodHCIdx = - pCivic.getRevIdxHolyCityGood()
				iBadHCIdx = pCivic.getRevIdxHolyCityBad()
				if bOwnHolyCity and iGoodHCIdx != 0 :
					iGoodIdx += iGoodHCIdx
					lszGoodHelpLines.append( getText(
							"[COLOR_CIVIC_TEXT]%s1[COLOR_REVERT], we own the %F2 holy city: %D3[ICON_INSTABILITY]",
							pCivic.getDescription(), pStateReligion.getChar(), iGoodHCIdx ) )
				elif bInfidelsOwnHolyCity and iBadHCIdx :
					iBadIdx += iBadHCIdx
					lszBadHelpLines.append( getText(
							"[COLOR_CIVIC_TEXT]%s1[COLOR_REVERT], infidels own the %F2 holy city: %D3[ICON_INSTABILITY]",
							pCivic.getDescription(), pStateReligion.getChar(), iBadHCIdx ) )

			# Non-state rels in city
			leReligionsInCity = []
			for eReligion in xrange( gc.getNumReligionInfos() ) :
				if self._pCity.isHasReligion( eReligion ) :
					leReligionsInCity.append( eReligion )
					if eReligion != eStateReligion :
						iConflict = self.getStateReligionConflict( eReligion )
						if self._pCity.isHolyCityByType( eReligion ) :
							iConflict *= 2
							iChar = gc.getReligionInfo( eReligion ).getHolyCityChar()
						else :
							iChar = gc.getReligionInfo( eReligion ).getChar()
						iBadIdx += iConflict
						lszBadHelpLines.append( getText( "%F1 in city: %D2[ICON_INSTABILITY]", iChar, iConflict ) )

			# Religion conflict
			for i, eRel1 in enumerate( leReligionsInCity ) :
				for eRel2 in leReligionsInCity[i+1:] :
					iConflict = self.getPresentReligionsConflict( eRel1, eRel2 )
					if iConflict > 0 :
						iBadIdx += iConflict
						lszBadHelpLines.append( getText( "Conflict between %F1 and %F2: %D3[ICON_INSTABILITY]",
								gc.getReligionInfo( eRel1 ).getChar(), gc.getReligionInfo( eRel2 ).getChar(), iConflict ) )

			# Subtotals
			lszGoodHelpLines.append( getText( "Good effects: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iGoodIdx ) ) )
			lszBadHelpLines.append( getText( "Bad effects: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iBadIdx ) ) )

			# Civic mods
			iGoodMod = 100
			iBadMod = 100
			for pCivic in self._pyOwner.iterCivicInfos() :
				iCivicGoodMod = pCivic.getRevIdxGoodReligionMod()
				iCivicBadMod = pCivic.getRevIdxBadReligionMod()
				if iCivicGoodMod != 0 :
					iGoodMod += iCivicGoodMod
					lszGoodHelpLines.append( getText( "[ICON_BULLET]%D1% from [COLOR_CIVIC_TEXT]%s2_civic[COLOR_REVERT]",
							iCivicGoodMod, pCivic.getDescription() ) )
				if iCivicBadMod != 0 :
					iBadMod += iCivicBadMod
					lszGoodHelpLines.append( getText( "[ICON_BULLET]%D1% from [COLOR_CIVIC_TEXT]%s2_civic[COLOR_REVERT]",
							iCivicBadMod, pCivic.getDescription() ) )

			# Apply mods
			iGoodIdx = iGoodIdx * iGoodMod // 100
			iBadIdx = iBadIdx * iBadMod // 100

			lszHelpLines.extend( lszGoodHelpLines )
			if len( lszGoodHelpLines ) > 0 :
				lszHelpLines.append( SEPARATOR )
			lszHelpLines.extend( lszBadHelpLines )
			if len( lszBadHelpLines ) > 0 :
				lszHelpLines.append( SEPARATOR )

			iRelIdx = iGoodIdx + iBadIdx
			lszHelpLines.append( getText( "Religion effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iRelIdx ) ) )
		else :
			iRelIdx = 0
			lszHelpLines.append( getText( "(No state religion)" ) )

		return iRelIdx, u"\n".join( lszHelpLines )

	def computeReligionRevIdx( self ) :
		# type: () -> int
		return self.computeReligionRevIndexAndHelp()[0]

	def computeReligionRevIdxHelp( self ) :
		# type: () -> unicode
		return self.computeReligionRevIndexAndHelp()[1]


	def computeNationalityRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]

		szHelp = getText( "[COLOR_HIGHLIGHT_TEXT]Nationality[COLOR_REVERT]")

		# Calculate adjusted culture percent
		iCulturePercent = 0
		for ePlayer in xrange( gc.getMAX_CIV_PLAYERS() ) :
			pPlayer = gc.getPlayer( ePlayer )
			iPlayerPercent = self._pCity.plot().calculateCulturePercent( ePlayer )
			if iPlayerPercent > 0 :
				if self._eOwnerTeam == pPlayer.getTeam() :
					iCultMod = 100
				else :
					iCultMod = 0
					if gc.getTeam( pPlayer.getTeam() ).isVassal( self._eOwnerTeam ) :
						iCultMod += 30
					if not self._pOwnerTeam.isAtWar( pPlayer.getTeam() ) \
							and self._pOwner.getCivilizationType() == pPlayer.getCivilizationType() :
						iCultMod += 50
				iCulturePercent += iPlayerPercent * iCultMod // 100

		szHelp += u"\n" + getText( "Foreign nationality (adj.): %d1%", 100 - iCulturePercent )

		# Base idx
		iBaseIdx = (100 - iCulturePercent)**2 // 500 - 3

		# Modifiers (only for instability, TODO?)
		if iBaseIdx > 0 :
			iMod = 100
			szModHelp = u""
			for pCivic in self._pyOwner.iterCivicInfos() :
				iCivicMod = pCivic.getRevIdxNationalityMod()
				if iCivicMod != 0 :
					iMod += iCivicMod
					szModHelp += u"\n"
					szModHelp += getText( "[ICON_BULLET]%D1% from [COLOR_CIVIC_TEXT]%s2[COLOR_REVERT]", iCivicMod, pCivic.getDescription() )

			if szModHelp :
				szHelp += u"\n" + getText( "Base effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iBaseIdx ) )
				szHelp += szModHelp

			iNatIdx = iBaseIdx * max( 0, iMod ) // 100
		else :
			iNatIdx = iBaseIdx

		szHelp += NL_SEPARATOR
		szHelp += u"\n" + getText( "Nationality effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iNatIdx ) )

		return iNatIdx, szHelp

	def computeNationalityRevIdx( self ) :
		# type: () -> int
		return self.computeNationalityRevIdxAndHelp()[0]


	def computeGarrisonRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]

		szHelp = getText( "[COLOR_HIGHLIGHT_TEXT]Garrison[COLOR_REVERT]" )

		iNumDefenders = self._pCity.plot().getNumDefenders( self._eOwner )
		szHelp += u"\n" + getText( "Number of defenders: %d1", iNumDefenders )

		iPopPenalty = self._pCity.getPopulation() // 5
		if iPopPenalty > 0 :
			szHelp += u"\n" + getText( "Size penalty: %d1", iPopPenalty )

		iBaseIdx = min( 0, iPopPenalty - iNumDefenders )

		# Modifiers and cap
		iMod = 100
		szModHelp = u""
		iCap = 10 # TODO: Make define
		for pCivic in self._pyOwner.iterCivicInfos() :
			iCivicMod = 0 # TODO
			if iCivicMod != 0 :
				iMod += iCivicMod
				szModHelp += u"\n" + getText( "[ICON_BULLET]%D1% from [COLOR_CIVIC_TEXT]%s2[COLOR_REVERT]",
						iCivicMod, pCivic.getDescription() )

			# TODO: cap change from civic

		for pBuilding in self._lpBuildings :
			iBuildingMod = pBuilding.getDefenseModifier() # TODO: Use separate tag
			if iBuildingMod != 0 :
				iMod += iBuildingMod
				szModHelp += u"\n" + getText( "[ICON_BULLET]%D1% from [COLOR_BUILDING_TEXT]%s2[COLOR_REVERT]",
						iBuildingMod, pBuilding.getDescription() )

		if szModHelp :
			szHelp += u"\n" + getText( "Base effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iBaseIdx ) )
			szHelp += szModHelp

		iGarIdx = min( iCap, iBaseIdx * max( 0, iMod ) // 100 )
		szHelp += u"\n" + getText( "Garrison effect: %s1[ICON_INSTABILITY] (max: %d2)",
				coloredRevIdxFactorStr( iGarIdx ), iCap )

		return iGarIdx, szHelp

	def computeGarrisonRevIdx( self ) :
		# type: () -> int
		return self.computeGarrisonRevIdxAndHelp()[0]


	def computeDisorderRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]

		szHelp = getText( "[COLOR_HIGHLIGHT_TEXT]Disorder[COLOR_REVERT]" )

		if self._pCity.getOccupationTimer() > 0 :

			iTurns = min( 15, self._iTurnsSinceAcquisition )
			iDisorderIdx = 5 * iTurns
			if iTurns < 15 :
				szHelp += u"\n" + getText( "Disorder (acquired %D1 [NUM1:turn:turns] ago): %s2[ICON_INSTABILITY]",
						iTurns, coloredRevIdxFactorStr( iDisorderIdx ) )
			else :
				szHelp += u"\n" + getText( "Disorder: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iDisorderIdx ) )

			# Modifiers
			iModTimes100 = 100
			if self._pOwner.isRebel() :
				iRebelMod = -90 # TODO: Make define
				iModTimes100 += iRebelMod
				szHelp += u"\n" + getText( "[ICON_BULLET]%D1% since we are rebels", iRebelMod )
			elif self._pCity.getRevolutionCounter() > 0 :
				iPastRevoltMod = -90 # TODO: Make define
				iModTimes100 += iPastRevoltMod
				szHelp += u"\n" + getText( "[ICON_BULLET]%D1% from past revolutions", iPastRevoltMod )

			if iModTimes100 != 100 :
				iDisorderIdx = iDisorderIdx * iModTimes100 // 100

				szHelp += NL_SEPARATOR
				szHelp += u"\n" + getText( "Disorder effect: %s1", coloredRevIdxFactorStr( iDisorderIdx ) )
		else :
			iDisorderIdx = 0
			szHelp += u"\n" + getText( "(No disorder)" )

		return iDisorderIdx, szHelp

	def computeDisorderRevIdx( self ) :
		# type: () -> int
		return self.computeDisorderRevIdxAndHelp()[0]


	def computeCrimeRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]
		""" RevIdx from crime; -2 to +8. """

		szHelp = getText( "[COLOR_HIGHLIGHT_TEXT]Crime[COLOR_REVERT]" )

		# LFGR_TODO: Make configurable
		iUsualCityCrime = 20  # This crime level means no stability bonus/malus
		iCrimeCap = 100  # No crime above this will be counted
		iCrimeFactorPercent = 10
		iCityCrime = min( self._pCity.getCrime(), iCrimeCap )

		iBaseCrimeIdx = (iCityCrime - iUsualCityCrime) * iCrimeFactorPercent // 100

		# Modifiers
		iMod = 100
		szModHelp = u""
		# TODO: Un-hardcode
		eStateReligion = self._pOwner.getStateReligion()
		if eStateReligion == gc.getInfoTypeForString( "RELIGION_COUNCIL_OF_ESUS" ) :
			if self._pCity.isHasReligion( self._pOwner.getStateReligion() ) :
				iRelMod = -50
				iMod += iRelMod
				szModHelp += u"\n" + getText( "[ICON_BULLET]%D1% from %F2",
						iRelMod, gc.getReligionInfo( eStateReligion ).getChar() )

		iCrimeIdx = iBaseCrimeIdx * iMod // 100
		if szModHelp :
			szHelp += u"\n" + getText( "Base crime effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iCrimeIdx ) )
			szHelp += szModHelp
			szHelp += NL_SEPARATOR

		szHelp += u"\n" + getText( "Crime effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iCrimeIdx ) )

		return iCrimeIdx, szHelp

	def computeCrimeRevIdx( self ) :
		# type: () -> int
		return self.computeCrimeRevIdxAndHelp()[0]


	def _computeHealthRevIdxAndCap( self ) :
		# type: () -> Tuple[int, int]
		iCap = 10 # TODO: Make define
		iNumUnhealthy = self._pCity.badHealth( False ) - self._pCity.goodHealth()
		if iNumUnhealthy > 0 :
			iHealthIdx = min( iCap, iNumUnhealthy )
		else :
			iHealthIdx = 0
		return iHealthIdx, iCap

	def _computeCultureRateAndRevIdx( self ) :
		# type: () -> (int, int)
		iCultRate = self._pCity.getCommerceRate( CommerceTypes.COMMERCE_CULTURE )
		iCultIdx = -isqrt( 2 * iCultRate )
		return iCultRate, iCultIdx

	def _computeStarvingRevIdx( self ) :
		# type: () -> int
		if self._pCity.foodDifference( True ) < 0 and abs( self._pCity.foodDifference( True ) ) > self._pCity.getFood() :
			if not self._pCity.isSettlement() :
				return 100
		else :
			return 0

	def _computeGoldenAgeRevIdx( self ) :
		# type: () -> int
		if self._pOwner.isGoldenAge() :
			return -20
		else :
			return 0

	def _computeEmpireSizeRevIdx( self ) :
		# type: () -> int
		iNumCitiesTimes4 = 0
		for pyCity in self._pyOwner.iterCities() :
			if pyCity.isSettlement() :
				iNumCitiesTimes4 += 1
			else :
				iNumCitiesTimes4 += 4
		iTargetNumCities = gc.getWorldInfo( CyMap().getWorldSize() ).getTargetNumCities()

		return max( -2, iNumCitiesTimes4 // iTargetNumCities - 4 )

	def _computeSimpleFactorsWithEffect( self ) :
		# type: () -> Generator[Tuple[str, int]]
		""" Returns various simple factors with description and RevIdx. """
		iStarvingIdx = self._computeStarvingRevIdx()
		if iStarvingIdx != 0 :
			yield "TXT_KEY_REV_WATCH_STARVATION", iStarvingIdx

		iGoldenAgeIdx = self._computeGoldenAgeRevIdx()
		if iGoldenAgeIdx != 0 :
			yield "Golden Age", iGoldenAgeIdx

		iCultureRate, iCultureRevIdx = self._computeCultureRateAndRevIdx()
		if iCultureRevIdx != 0 :
			yield getText( "%d1 [ICON_CULTURE]/Turn", iCultureRate ), iCultureRevIdx

		iSizeIdx = self._computeEmpireSizeRevIdx()
		if iSizeIdx < 0 :
			yield "Small empire", iSizeIdx
		elif iSizeIdx > 0 :
			yield "Large empire", iSizeIdx

	def _buildingsWithEffect( self ) :
		# type: () -> Iterator[Tuple[CvBuildingInfo, int]]
		for pBuilding in self._lpBuildings :
			iRevIdx = pBuilding.getRevIdxLocal()
			if iRevIdx != 0 :
				yield pBuilding, iRevIdx

	def _civicsWithEffect( self ) :
		# type: () -> Iterator[Tuple[CvCivicInfo, int]]
		""" Iterates over tuples (eCivic, iRevIdx) """
		for pCivic in self._pyOwner.iterCivicInfos() :
			iRevIdx = pCivic.getRevIdxLocal() + pCivic.getRevIdxNational() # TODO
			if iRevIdx != 0 :
				yield pCivic, iRevIdx

	def computeVariousRevIdxAndHelp( self ) :
		iVariousIdx = 0
		szHelp = u""

		szVariousHelp = u""

		# Health
		iHealthIdx, iCap = self._computeHealthRevIdxAndCap()
		if iHealthIdx != 0 :
			iVariousIdx += iHealthIdx
			szVariousHelp += u"\n" + getText( "[ICON_BULLET]Unhealthiness: %s1[ICON_INSTABILITY] (max: %d2)",
					coloredRevIdxFactorStr( iHealthIdx ), iCap )

		# Simple things
		for szDesc, iLoopIdx in self._computeSimpleFactorsWithEffect() :
			iVariousIdx += iLoopIdx
			szVariousHelp += u"\n" + getText( "[ICON_BULLET]%s1: %s2[ICON_INSTABILITY]",
					szDesc, coloredRevIdxFactorStr( iLoopIdx ) )

		if szVariousHelp :
			if szHelp : szHelp += u"\n"
			szHelp += getText( "[COLOR_HIGHLIGHT_TEXT]Various effects[COLOR_REVERT]" )
			szHelp += szVariousHelp

		# Buildings with local effects
		szLocalBuildingsHelp = u""
		for pInfo, iLoopIdx in self._buildingsWithEffect() :
			iVariousIdx += iLoopIdx
			szLocalBuildingsHelp += u"\n" + getText( "[ICON_BULLET][COLOR_BUILDING_TEXT]%s1[COLOR_REVERT]: %s2[ICON_INSTABILITY]",
				pInfo.getTextKey(), coloredRevIdxFactorStr( iLoopIdx ) )
		if szLocalBuildingsHelp :
			if szHelp : szHelp += u"\n"
			szHelp += getText( "[COLOR_HIGHLIGHT_TEXT]Local Buildings[COLOR_REVERT]" )
			szHelp += szLocalBuildingsHelp

		# Buildings with national effects
		szNationalBuildingsHelp = u""
		for pInfo, iLoopIdx in self._pPlayerCache.buildingsWithNationalEffects() :
			iVariousIdx += iLoopIdx
			szNationalBuildingsHelp += u"\n" + getText( "[ICON_BULLET][COLOR_BUILDING_TEXT]%s1[COLOR_REVERT]: %s2[ICON_INSTABILITY]",
				pInfo.getTextKey(), coloredRevIdxFactorStr( iLoopIdx ) )
		if szNationalBuildingsHelp :
			if szHelp : szHelp += u"\n"
			szHelp += getText( "[COLOR_HIGHLIGHT_TEXT]National Buildings[COLOR_REVERT]" )
			szHelp += szNationalBuildingsHelp

		# Civics
		szCivicHelp = u""
		for pInfo, iLoopIdx in self._civicsWithEffect() :
			iVariousIdx += iLoopIdx
			szCivicHelp += u"\n" + getText( "[ICON_BULLET][COLOR_CIVIC_TEXT]%s1[COLOR_REVERT]: %s2[ICON_INSTABILITY]",
				pInfo.getTextKey(), coloredRevIdxFactorStr( iLoopIdx ) )
		if szCivicHelp :
			if szHelp : szHelp += u"\n"
			szHelp += getText( "[COLOR_HIGHLIGHT_TEXT]Civics[COLOR_REVERT]" )
			szHelp += szCivicHelp


		return iVariousIdx, szHelp

	def computeVariousTooltipData( self ) :
		# type: () -> Tuple[int, List[Tuple[int, unicode]], List[Tuple[int, unicode]]]
		""" Special function for city tooltip """

		ltEffects = []

		# Simple things
		for szDesc, iLoopIdx in self._computeSimpleFactorsWithEffect() :
			ltEffects.append( ( getText( szDesc ), iLoopIdx ) )

		# Civics, buildings
		ltEffects.extend( self._buildingsWithEffect() )
		ltEffects.extend( self._pPlayerCache.buildingsWithNationalEffects() )
		ltEffects.extend( self._civicsWithEffect() )

		return effectsToRevWatchData( ltEffects )


	def computeRevIdxAndFinalModifierHelp( self ) :
		# type () -> Tuple[int, unicode]
		""" The total RevIdx (per turn) of this city. The help string only contains final adjustments. """
		iIdxSum = sum( [ # TODO: Caching
			self.computeHappinessRevIdx(),
			self.computeLocationRevIdx(),
			self.computeReligionRevIdx(),
			self.computeNationalityRevIdx(),
			self.computeGarrisonRevIdx(),
			self.computeDisorderRevIdx(),
			self.computeCrimeRevIdx(),
			self.computeVariousRevIdxAndHelp()[0]
		] )
		szHelp = getText( "Sum of all effects: %D1[ICON_INSTABILITY]", iIdxSum )

		iAdjustedIdx, szAdjustHelp = adjustedRevIdxAndFinalModifierHelp( iIdxSum, self._pOwner, bColorFinalIdx = True )
		szHelp += szAdjustHelp

		# Feedback
		iPrevRevIdx = max( 0, self._pCity.getRevolutionIndex() ) # Just in case
		if iAdjustedIdx < 0 :
			if iPrevRevIdx > RevDefs.alwaysViolentThreshold :
				# Very angry locals forgive very quickly if things begin improving
				iFeedback = -min( iPrevRevIdx // 170, 10 )
			elif iPrevRevIdx > RevDefs.revInstigatorThreshold :
				# Angry locals forgive quickly if things are improving
				iFeedback = -min( iPrevRevIdx // 230, 8 )
			else :
				iFeedback = -min( iPrevRevIdx // 300, 6 )
			if iFeedback != 0 :
				szHelp += u"\n" + getText( "[ICON_BULLET]Recent improvements: %D1[ICON_INSTABILITY]", iFeedback )
			iAdjustedIdx += iFeedback

		return iAdjustedIdx, szHelp

	def computeRevIdx( self ) :
		# type: () -> int
		return self.computeRevIdxAndFinalModifierHelp()[0]