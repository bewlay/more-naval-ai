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
SEPARATOR = u"\n-----------------------"


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
	# type: ( Iterable[Tuple[CvInfoBase, int]] ) -> Tuple[int, List[Tuple[int, unicode]], List[Tuple[int, unicode]]]
	""" Aggregate a set of (info, iEffect) tuples into a total effect, a positive list, and negative list. """
	iTotal = 0
	posList = []
	negList = []
	for info, iRevIdx in effects :
		iTotal += iRevIdx
		if iRevIdx > 0 :
			negList.append( (iRevIdx, info.getDescription()) )
		else :
			posList.append( (iRevIdx, info.getDescription()) )
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
		szHelp += u"\n" + getText( "[ICON_BULLET]Offset: %D1", iOffset )

	iAdjustedIdx = int( fGameSpeedMod * fMod * iRawIdx + iOffset + .5 )

	if szHelp != u"" :
		if bColorFinalIdx :
			szHelp += SEPARATOR + u"\n" + getText( "Adjusted: %s1", coloredRevIdxFactorStr( iAdjustedIdx ) )
		else :
			szHelp += SEPARATOR + u"\n" + getText( "Adjusted: %D1", iAdjustedIdx )

	return iAdjustedIdx, szHelp

def modAsPercent( fMod ) :
	""" Converts a modifier such as 0.7 to a percentage such as -30 """
	return int( ( fMod - 1 ) * 100 )

def canRevolt( pCity ) :
	# type: ( CyCity ) -> bool
	if pCity.isSettlement() and pCity.getOwner() == pCity.getOriginalOwner() :
		return False

	return True


class CityRevIdxHelper :
	"""
	Helper class to calculate a city's RevIdx (per turn).
	WARNING: Only use temporarily, should not be stored, as some caching happens.
	"""
	def __init__( self, pCity ) :
		# type: (CyCity) -> None
		self._pCity = pCity

		# Player stuff
		self._eOwner = self._pCity.getOwner()
		self._pOwner = gc.getPlayer( self._eOwner )
		self._eOwnerTeam = self._pOwner.getTeam()
		self._pOwnerTeam = gc.getTeam( self._eOwnerTeam )
		self._bRecentlyAcquired = \
				(game.getGameTurn() - pCity.getGameTurnAcquired() < 12 * RevUtils.getGameSpeedMod())

		self._fCivSizeRawVal, _ = RevUtils.computeCivSizeRaw( self._eOwner )
		self._fCivSizeRawVal *= RevOpt.getCivSizeModifier()

		# Find cultural owner
		# TODO: This seems weirdly calculated
		self._iCulturePercent = 0
		maxCult = 0
		self._eMaxCultPlayer = -1  # Player with highest plot culture
		for idx in range( 0, gc.getMAX_CIV_PLAYERS() ) :
			if self._pOwner.getTeam() == gc.getPlayer( idx ).getTeam() :
				self._iCulturePercent += pCity.plot().calculateCulturePercent( idx )
			if pCity.plot().calculateCulturePercent( idx ) > maxCult :
				maxCult = pCity.plot().calculateCulturePercent( idx )
				self._eMaxCultPlayer = idx

		if self._eMaxCultPlayer == -1 :
			self._eMaxCultPlayer = self._eOwner

		eMaxCultTeam = gc.getPlayer( self._eMaxCultPlayer ).getTeam()
		self._bWarWithMaxCult  = self._pOwnerTeam.isAtWar( eMaxCultTeam )
		self._bMaxCultIsVassal = gc.getTeam( eMaxCultTeam ).isVassal( self._eOwnerTeam )

		# Caching
		self._fCacheCityDistModifier = None # type: Optional[float]
	
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

	def computeHappinessRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]

		szHelp = u""

		# TODO: Remove all the floating point arithmetic, maybe simplify
		iNumUnhappy = RevUtils.getModNumUnhappy( self._pCity, RevOpt.getWarWearinessMod() )

		if iNumUnhappy > 0 :
			szHelp += getText( "[ICON_UNHAPPY] City is unhappy" )

			if self._pCity.getOccupationTimer() > 0 :
				szHelp += u"\n"
				szHelp += getText( "No effect while in disorder" )
				return 0, szHelp

			# Base unhappiness
			# TODO: Calculate this more elegantly (?)
			iNumUnhappy = max( iNumUnhappy
					- (self._pCity.getRevIndexPercentAnger() * self._pCity.getPopulation()) / 1000, 0 )
			if self._pCity.getEspionageHappinessCounter() > 0 :
				# Reduce effect if unhappiness is from spy mission
				iNumUnhappy -= self._pCity.getEspionageHappinessCounter()
			iNumUnhappy = max( 0, iNumUnhappy )

			szHelp += u"\n"
			szHelp += getText( "Base unhappiness (ignoring some factors): %d1", iNumUnhappy )

			# TODO: Remove float arithmetic
			iHappyIdxTimes100 = int( 15 * RevOpt.getHappinessModifier() * pow( iNumUnhappy, .8 ) * 100 )

			szHelp += u"\n"
			szHelp += getText( "Base instability from unhappiness: %s1",
					"%.2f" % ( iHappyIdxTimes100 / 100. ) )

			# Compute modifiers
			iHappyIdxModTimes100 = 100

			# Bonus if population is larger than unhappiness
			# TODO: Somehow work this in earlier. Maybe generally use unhappiness/pop
			iAdjPopulation = min( 12, self._pCity.getPopulation() ) # TODO: Do this?
			if iNumUnhappy < iAdjPopulation :
				iPopMod = 100 * iNumUnhappy // iAdjPopulation - 100
				if iPopMod != 0 :
					szHelp += u"\n"
					szHelp += getText( "[ICON_BULLET] %D1% from large population compared to unhappiness level", iPopMod )
					iHappyIdxModTimes100 += iPopMod

			if self._bRecentlyAcquired :
				iRecentlyAcquiredHappyIdxMod = -30 # TODO
				szHelp += u"\n"
				szHelp += getText( "[ICON_BULLET] %D1% from recent acquisition", iRecentlyAcquiredHappyIdxMod )
				iHappyIdxModTimes100 += iRecentlyAcquiredHappyIdxMod

			if self._pCity.isUnhappyProduction() :
				iUnhappyProduction = -30 # TODO
				szHelp += u"\n"
				szHelp += getText( "[ICON_BULLET] %D1% from unhappiness production", iUnhappyProduction ) # TODO: say Building
				iHappyIdxModTimes100 += iUnhappyProduction

			iHappyIdxModTimes100 = max( 0, iHappyIdxModTimes100 )
			iHappyIdx = iHappyIdxTimes100 * iHappyIdxModTimes100 // 10000
			
			szHelp += SEPARATOR
			szHelp += u"\n"
			szHelp += getText( "Final instability from unhappiness: %s1", coloredRevIdxFactorStr( iHappyIdx ) )

			return iHappyIdx, szHelp
		elif iNumUnhappy < 0 :
			szHelp += getText( "[ICON_HAPPY] City is happy" )

			# Weird way of writing min( abs( iNumUnhappy ), 10, self._pCity.getPopulation() ), to get correct text
			iNumHappy = abs( iNumUnhappy )
			if self._pCity.getPopulation() < 10 and  iNumHappy > self._pCity.getPopulation() :
				iNumHappy = self._pCity.getPopulation()
				szHelp += u"\n"
				szHelp += getText( "Base happiness (capped by population): %d1", iNumHappy )
			elif iNumHappy > 10 :
				iNumHappy = 10
				szHelp += u"\n"
				szHelp += getText( "Base happiness (capped at 10): %d1", iNumHappy )
			else :
				szHelp += u"\n"
				szHelp += getText( "Base happiness: %d1", iNumHappy )

			iNegHappyIdxTimes100 = int( 100 * RevOpt.getHappinessModifier()
					* (1.2 + iNumHappy / self._pCity.getPopulation()) * pow( iNumHappy, .6 ) + 0.5 )
			szHelp += u"\n"
			szHelp += getText( "Base happiness effect (adj. to pop.): %s1",
					"%.2f" % ( -iNegHappyIdxTimes100 / 100. ) )

			# Compute modifiers
			iHappyIdxModTimes100 = 100
			if self._bWarWithMaxCult and self._pOwner.isRebel() :
				iRebelWarWithMaxCultMod = -50
				szHelp += u"\n"
				szHelp += getText( "[ICON_BULLET] %D1% from being a rebel at war with the cultural owner", iRebelWarWithMaxCultMod )
				iHappyIdxModTimes100 += iRebelWarWithMaxCultMod

			iHappyIdxModTimes100 = max( 0, iHappyIdxModTimes100 )

			iNegHappyIdx = iNegHappyIdxTimes100 * ( iHappyIdxModTimes100 ) // 10000
			
			szHelp += SEPARATOR
			szHelp += u"\n"
			szHelp += getText( "Final happiness effect: %s1", coloredRevIdxFactorStr( -iNegHappyIdx ) )

			return -iNegHappyIdx, szHelp
		else :
			return 0, getText( "City is neither happy nor unhappy" )


	def _computeAdjustedCityDistance( self ) :
		# type: () -> float

		# LFGR_TODO: This seems overly complicated

		if self._fCacheCityDistModifier is None :
			# Some useful vars/abbreviations
			pCapital = self._pOwner.getCapitalCity()

			# Compute simple distances
			# LFGR_TODO: Use actual map distances instead of euclidean? Should not affect performance to much.
			map = CyMap()
			deltaX = abs( self._pCity.getX() - pCapital.getX() )
			if map.isWrapX() :
				deltaX = min( deltaX, map.getGridWidth() - deltaX )
			deltaY = abs( self._pCity.getY() - pCapital.getY() )
			if map.isWrapY() :
				deltaY = min( deltaY, map.getGridWidth() - deltaY )
			fCityDistRaw = (deltaX ** 2 + deltaY ** 2) ** 0.5 # Euclidean distance from capital
			fCityDistMapModifier = (map.getGridWidth() ** 2 + map.getGridHeight() ** 2) ** 0.5 # Map diagonal

			### Compute "Communication bonus"
			cityDistCommBonus = 0
			pTeam = gc.getTeam( self._pOwner.getTeam() )
			bCanTradeOverCoast = False
			bCanTradeOverOcean = False
			iTerrainCoast = gc.getInfoTypeForString( RevDefs.sXMLCoast )
			iTerrainOcean = gc.getInfoTypeForString( RevDefs.sXMLOcean )
			for i in range( gc.getNumTechInfos() ) :
				tech = gc.getTechInfo( i )
				if tech.isTerrainTrade( iTerrainCoast ) :
					if pTeam.isHasTech( i ) :
						bCanTradeOverCoast = True
				if tech.isTerrainTrade( iTerrainOcean ) :
					if pTeam.isHasTech( i ) :
						bCanTradeOverOcean = True

			# +50 if we can trade over ocean
			if bCanTradeOverOcean :
				cityDistCommBonus += 50

			# +17 for each trade route but the first
			iCityTradeRoutes = self._pCity.getTradeRoutes()
			if iCityTradeRoutes > 1 :
				cityDistCommBonus += (iCityTradeRoutes - 1) * 17

			# Some extra boni if we are connected...
			bCityIsConnected = self._pCity.isConnectedTo( pCapital )
			if bCityIsConnected :
				bTechRouteModifier = False
				for i in range( gc.getNumTechInfos() ) :
					for j in range( gc.getNumRouteInfos() ) :
						if gc.getRouteInfo( j ).getTechMovementChange( i ) != 0 and pTeam.isHasTech( i ) :
							bTechRouteModifier = True
							break
					if bTechRouteModifier :
						break
				if bTechRouteModifier :
					# (FfH) ... if we have engineering, +100-(30-10)*1.67 = +66.6
					cityDistCommBonus += 100 - ( gc.getRouteInfo( self._pCity.plot().getRouteType() ).getFlatMovementCost()
							+ gc.getRouteInfo( self._pCity.plot().getRouteType() ).getTechMovementChange( i ) ) * 1.67
				else :
					# (FfH) ... if we have engineering, +100-30*1.67 = +49.9
					cityDistCommBonus += 100 - (gc.getRouteInfo( self._pCity.plot().getRouteType() ).getFlatMovementCost()) * 1.67
				if self._pCity.isCoastal( -1 ) :
					# Coastal cities: +25, or +50 if we can trade over ocean
					if bCanTradeOverOcean :
						cityDistCommBonus += 50
					elif bCanTradeOverCoast :
						cityDistCommBonus += 25
				# +TradeRouteMod, +CultureMod, +GoldMod/2
				iTradeRouteModifier = self._pCity.getTradeRouteModifier()
				iCityCultureModifier = self._pCity.getCommerceRateModifier( CommerceTypes.COMMERCE_CULTURE )
				iCityGoldModifier = self._pCity.getCommerceRateModifier( CommerceTypes.COMMERCE_GOLD )
				cityDistCommBonus += iTradeRouteModifier
				cityDistCommBonus += iCityCultureModifier
				cityDistCommBonus += iCityGoldModifier / 2

			# -MaintainanceMod
			iCityMaintenanceModifier = self._pCity.getMaintenanceModifier()
			cityDistCommBonus -= iCityMaintenanceModifier

			# +150 if we have power
			bCityisPower = self._pCity.isPower()
			if bCityisPower :
				cityDistCommBonus += 150

			# +100 per airlift capacity
			iCityAirlift = self._pCity.getMaxAirlift()
			cityDistCommBonus += 100 * iCityAirlift

			# Finally: First, distance as fraction of maxdist, times 307 (?)
			# Divide by (100+CommBonus)/100
			# Subtract 666 / maxdist (?)
			# In other words: ( 307*dist / ((100+CommBonus)/100) - 666 ) / maxdist
			# LFGR_TODO: Could this even be negative?
			self._fCacheCityDistModifier = (307.0 * fCityDistRaw / fCityDistMapModifier) / (1.0 + (cityDistCommBonus / 100.0))
			self._fCacheCityDistModifier -= int( 666 / fCityDistMapModifier )
		return self._fCacheCityDistModifier

	def _computeDistModifier( self ) :
		# type: () -> float
		# LFGR_TODO: Caching?
		# Modifiers from civics, traits (LFGR_TODO), buildings
		# Does not work the way it would seem if smaller than 0.
		CivicsDistModifier = RevUtils.getCivicsDistanceMod( self._eOwner )
		#			TraitsDistModifier = RevUtils.getTraitsDistanceMod( iPlayer )
		TraitsDistModifier = 0
		BuildingsDistModifier = RevUtils.getBuildingsDistanceMod( self._pCity )
		DistModifier = (CivicsDistModifier + TraitsDistModifier + BuildingsDistModifier) / 100.0
		fDistModAlt = 1.0
		if DistModifier < 0 :
			fDistModAlt /= (1.0 - DistModifier)
		elif DistModifier > 0 :
			fDistModAlt += DistModifier

		fDistModAlt *= RevOpt.getDistanceToCapitalModifier()
		if self._pCity.isGovernmentCenter() :
			fDistModAlt *= 0.5
		return fDistModAlt

	def computeLocationRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]
		# By phungus
		# Distance to capital City Distance modified by communication techs and structures

		fCityDist = self._computeAdjustedCityDistance() * self._computeDistModifier()

		iLocationRevIdx = 0

		if self._fCivSizeRawVal > 2.0 :
			iLocationRevIdx += int( math.floor( 2.0 * fCityDist + .5 ) )
		elif self._fCivSizeRawVal > 1.6 :
			iLocationRevIdx += int( math.floor( 1.65 * fCityDist + .5 ) )
		elif self._fCivSizeRawVal > 1.4 :
			iLocationRevIdx += int( math.floor( 1.45 * fCityDist + .5 ) )
		elif self._fCivSizeRawVal > 1.2 :
			iLocationRevIdx += int( math.floor( 1.25 * fCityDist + .5 ) )
		elif self._fCivSizeRawVal > 1.0 :
			iLocationRevIdx += int( math.floor( fCityDist + .5 ) )
		elif self._fCivSizeRawVal > .7 :
			iLocationRevIdx += int( math.floor( .75 * fCityDist + .5 ) )
		else :
			iLocationRevIdx += int( math.floor( .5 * fCityDist + .5 ) )


		pCapital = self._pOwner.getCapitalCity()
		if pCapital is not None and not self._pCity.isConnectedTo( pCapital ) :
			if self._bRecentlyAcquired or self._pOwner.isRebel() :
				iDisconnectedIdx = 3
			else :
				iDisconnectedIdx = min( 5 + self._pOwner.getCurrentRealEra() + self._pCity.getPopulation() / 3, 10 )
			szHelp = getText( "Location: %D1", iLocationRevIdx )
			iLocationRevIdx += iDisconnectedIdx
			szHelp += u"\n" + getText( "Not connected to capital: %D1", iDisconnectedIdx)
			szHelp += SEPARATOR + u"\n" + getText( "Full effect: %s1", coloredRevIdxFactorStr( iLocationRevIdx ) )
		else :
			szHelp = getText( "Location: %s1", coloredRevIdxFactorStr( iLocationRevIdx ) )

		return iLocationRevIdx, szHelp

	def computeLocationRevIdx( self ) :
		# type: () -> int
		return self.computeLocationRevIdxAndHelp()[0]


	def computeReligionRevIndicesAndHelp( self ) :
		# type: () -> Tuple[int, int, unicode]
		# Returns (goodIdx, badIdx), where goodIdx is idx based on state religion in city, and
		#   badIdx is based on non-state religion in city
		eStateReligion = self._pOwner.getStateReligion()
		if self._pOwner.isStateReligion() and eStateReligion != -1 : # LFGR_TODO: Necessary?
			# LFGR_TODO: Take religion type into account

			# Preparation
			# TODO: Compute civics effects and show them (?)
			iCivicsHolyCityGood, iCivicsHolyCityBad = RevUtils.getCivicsHolyCityEffects( self._eOwner )
			fCivicsGoodMod, fCivicsBadMod = RevUtils.getCivicsReligionMods( self._eOwner )

			# GOOD STUFF
			iRelGoodIdx = 0
			szGoodHelp = u""

			# State religion in city
			if self._pCity.isHasReligion( eStateReligion ) :
				# Basic bonus
				iRelGoodIdx -= 4
				if len( szGoodHelp ) > 0 : szGoodHelp += u"\n"
				szGoodHelp += getText( "State religion in city: %d1", -4 )

				# Our holy city
				if self._pCity.isHolyCityByType( eStateReligion ) :
					iRelGoodIdx += -5 - iCivicsHolyCityGood
					szGoodHelp += u"\n" + getText( "Holy city: %d1", -5 - iCivicsHolyCityGood ) # LFGR_TODO: Add symbol
				else :
					# Do we own the holy city?
					pStateHolyCity = game.getHolyCity( eStateReligion )
					if not pStateHolyCity.isNone() :
						eHolyCityOwner = pStateHolyCity.getOwner()
						if eHolyCityOwner == self._eOwner :
							iRelGoodIdx -= iCivicsHolyCityGood # We own the holy city
							szGoodHelp += u"\n" + getText( "We own the holy city: %d1", -iCivicsHolyCityGood )

			if iRelGoodIdx != 0 : # Compute modifiers
				szModHelp = u""

				# General modifier
				fMod = RevOpt.getReligionModifier()
				if fMod != 1 :
					szModHelp += u"\n" + getText( "[ICON_BULLET]General religion modifier: %D1%", int( fMod * 100 ) - 100 )

				# War bonus
				if self._pOwnerTeam.getAtWarCount( True ) > 1 :
					# God is on your side =P
					fWarExtraMod = 0.5
					fMod += fWarExtraMod
					szModHelp += u"\n" + getText( "[ICON_BULLET]War bonus: %D1%", int( fWarExtraMod * 100 ) )

				# Civics
				if fCivicsGoodMod != 0 :
					fMod += fCivicsGoodMod
					szModHelp += u"\n" + getText( "[ICON_BULLET]Civics: %D1%", int( fCivicsGoodMod * 100 ) )

				if szModHelp != u"" :
					if "\n" in szGoodHelp : # More than one line
						szGoodHelp += u"\n" + getText( "Base good effect: %d1", iRelGoodIdx )
					szGoodHelp += szModHelp

				iRelGoodIdx = int( math.floor( fMod * iRelGoodIdx + .5 ) )
				szGoodHelp += u"\n" + getText( "Good effect: %s1", coloredRevIdxFactorStr( iRelGoodIdx ) )

			# BAD STUFF
			fRelBadIdx = 0
			szBadHelp = u""

			# Non-state religions
			for eReligion in range( 0, gc.getNumReligionInfos() ) :
				if self._pCity.isHasReligion( eReligion ) :
					if eReligion != eStateReligion :
						if fRelBadIdx > 4 :
							fRelBadIdx += 1
						else :
							fRelBadIdx += 2.5
			if fRelBadIdx > 0 :
				szBadHelp += getText( "Non-state religions: %s1", u"%.2f" % fRelBadIdx )

			# Holy city ownership
			pStateHolyCity = game.getHolyCity( eStateReligion )
			if not pStateHolyCity.isNone() :
				if gc.getPlayer( pStateHolyCity.getOwner() ).getStateReligion() != eStateReligion :
					fRelBadIdx += iCivicsHolyCityBad # Heathens own the holy city!
					if szBadHelp != u"" : szBadHelp += u"\n"
					szBadHelp += getText( "Heathens own the holy city: %d1", iCivicsHolyCityBad )

			# Infidel's holy city
			if self._pCity.isHolyCity() :
				if not self._pCity.isHolyCityByType( eStateReligion ) :
					fRelBadIdx += 4
					if szBadHelp != u"" : szBadHelp += u"\n"
					szBadHelp += getText( "Infidel's holy city: %d1", 4 )

			if fRelBadIdx != 0 : # Compute modifiers
				szModHelp = u""

				# General modifier
				fMod = RevOpt.getReligionModifier()
				if fMod != 1 :
					szModHelp += u"\n" + getText( "[ICON_BULLET]General religion modifier: %D1%", int( fMod * 100 ) - 100 )

				# Civics
				if fCivicsBadMod != 0 :
					fMod += fCivicsBadMod
					szModHelp += u"\n" + getText( "[ICON_BULLET]Civics: %D1%", int( fCivicsBadMod * 100 ) )

				if szModHelp != u"" :
					if "\n" in szBadHelp : # More than one line
						szBadHelp += u"\n" + getText( "Base bad effect: %s1", u"%.2f" % fRelBadIdx )
					szBadHelp += szModHelp

				iRelBadIdx = int( math.floor( fMod * fRelBadIdx + .5 ) )
				szBadHelp += u"\n" + getText( "Bad effect: %s1", coloredRevIdxFactorStr( iRelBadIdx  ) )
			else :
				iRelBadIdx = 0

			# Put everything together
			if szGoodHelp != u"" and szBadHelp != u"" :
				szHelp = szGoodHelp + SEPARATOR + u"\n" + szBadHelp
			elif szGoodHelp != u"" :
				szHelp = szGoodHelp
			elif szBadHelp != u"" :
				szHelp = szBadHelp
			else :
				szHelp = getText( "(No religions in city)" )
			return iRelGoodIdx, iRelBadIdx, szHelp

		return 0, 0, getText( "(No state religion)" )

	def computeReligionRevIndices( self ) :
		# type: () -> Tuple[int, int]
		return self.computeReligionRevIndicesAndHelp()[:2]

	def computeReligionRevIdx( self ) :
		# type: () -> int
		return sum( self.computeReligionRevIndicesAndHelp()[:2] )

	def computeReligionRevIdxHelp( self ) :
		# type: () -> unicode
		return self.computeReligionRevIndicesAndHelp()[2]


	def computeCultureRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]
		iCultRate = self._pCity.getCommerceRate( CommerceTypes.COMMERCE_CULTURE )
		szHelp = getText( "Culture rate: %d1 [ICON_CULTURE]", iCultRate )

		if iCultRate == 0 :
			return iCultRate, szHelp

		fEraMod = 1 / (1.5 + self._pOwner.getCurrentRealEra() / 2.0) # Era divisor adjusted to FfH
		szHelp += u"\n"
		szHelp += getText( "Era modifier: %d1%", int( fEraMod * 100 ) - 100 )

		fAdjCultRate = iCultRate * fEraMod
		szHelp += SEPARATOR
		szHelp += u"\n"
		sAdjCultRate = u"%.2f" % fAdjCultRate
		szHelp += getText( "Adjusted culture rate: %s1", sAdjCultRate )

		iCultureIdx = - min( int( pow( fAdjCultRate, .7 ) + 0.5 ), 10 )

		# Compute further modifications
		fCultureIdx = float( iCultureIdx )
		szModHelp = u""
		if self._bWarWithMaxCult and not self._pOwner.isRebel() : # TODO: Move to nationality stuff?
			fCultureIdx *= 0.5
			szModHelp += u"\n"
			szModHelp += getText( "War with majority culture: %d1%", int( 0.5 * 100 ) - 100 )

		fMod = RevOpt.getCultureRateModifier()
		if fMod != 1 :
			fCultureIdx *= fMod
			szModHelp += u"\n"
			szModHelp += getText( "General culture rate modifier: %d1%", int( fMod * 100 ) - 100 )

		# Final effect
		if szModHelp == u"" :
			szHelp += u"\n"
			szHelp += getText( "Culture rate effect: %s1", coloredRevIdxFactorStr( iCultureIdx ) )
		else :
			szHelp += u"\n"
			szHelp += getText( "Base effect: %d1", iCultureIdx )
			szHelp += szModHelp

			iCultureIdx = int( math.floor( fCultureIdx + .5 ) )
			szHelp += SEPARATOR
			szHelp += u"\n"
			szHelp += getText( "Culture rate effect: %s1", coloredRevIdxFactorStr( iCultureIdx ) )
		return iCultureIdx, szHelp

	def computeCultureRevIdx( self ) :
		# type: () -> int
		return self.computeCultureRevIdxAndHelp()[0]


	def computeNationalityRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]

		szHelp = getText( "Foreign nationality: %d1%", 100 - self._iCulturePercent )
		if self._iCulturePercent <= 60 :
			iBadPercent = ( 60 - self._iCulturePercent )
			iPreNatIdx = min( 13, ( iBadPercent ** 2 ) // 200 )
			szHelp += u"\n"
			szHelp += getText( "Raw effect (capped at 13): %d1", iPreNatIdx )

			iLowerCap = iBadPercent // 10
			szHelp += u"\n"
			szHelp += getText( "[ICON_BULLET]Minimum base instability: %d1", iLowerCap )

			iCultureRate = self._pCity.getCommerceRate( CommerceTypes.COMMERCE_CULTURE )
			iCultureRateBonus = -iCultureRate # TODO?
			if iCultureRateBonus != 0 :
				szHelp += u"\n"
				szHelp += getText( "[ICON_BULLET]Culture rate bonus: %D1", iCultureRateBonus )

			iBaseNatIdx = max( iLowerCap, iPreNatIdx + iCultureRateBonus )
		else :
			iBaseNatIdx = -( self._iCulturePercent - 60 ) // 8

		szModHelp = u""
		if iBaseNatIdx > 0 :
			iCap = 1000 # float("inf") does not seem to work in python 2.4
			iModTimes100 = 100

			if self._bRecentlyAcquired :
				iRecAqModPercent = -40
				iRecAqCap = 6
				iModTimes100 += iRecAqModPercent
				iCap = min( iCap, iRecAqCap )
				szModHelp += u"\n"
				szModHelp += getText( "[ICON_BULLET]Recently acquired: %D1%, capped at %d2", iRecAqModPercent, iRecAqCap )

			if self._bWarWithMaxCult and not self._pOwner.isRebel() :
				iWarModTimes100 = 50
				iModTimes100 += iWarModTimes100
				szModHelp += u"\n"
				szModHelp += getText( "[ICON_BULLET]War with majority culture: %D1%", iWarModTimes100 )
			elif self._bMaxCultIsVassal :
				iVassalModTimes100 = -30
				iVassalCap = 5
				iModTimes100 += iVassalModTimes100
				iCap = min( iCap, iVassalCap )
				szModHelp += u"\n"
				szModHelp += getText( "[ICON_BULLET]Majority culture is vassal: %D1%, capped at %d2", iVassalModTimes100, iVassalCap )

			for i in range( 0, gc.getNumCivicOptionInfos() ) :
				iCivic = self._pOwner.getCivics( i )
				if iCivic >= 0 :
					kCivic = gc.getCivicInfo( iCivic )
					fCivicMod = kCivic.getRevIdxNationalityMod() # TODO: Make Integer
					if fCivicMod != 0 :
						iCivicModTimes100 = int( fCivicMod * 100 )
						iModTimes100 += iCivicModTimes100
						szModHelp += u"\n"
						szModHelp += getText( "[ICON_BULLET][COLOR_HIGHLIGHT_TEXT]%s1[COLOR_REVERT]: %D2%", kCivic.getDescription(), iCivicModTimes100 )

			iNatIdx = min( iCap, iBaseNatIdx * max( 0, iModTimes100 ) // 100 )
		else :
			iNatIdx = iBaseNatIdx


		if szModHelp == u"" :
			if iNatIdx != 0 :
				szHelp += u"\n"
				szHelp += getText( "Nationality effect: %s1", coloredRevIdxFactorStr( iNatIdx ) )
		else :
			szHelp += u"\n" + getText( "Base Effect: %d1", iBaseNatIdx )
			szHelp += szModHelp
			szHelp += u"\n" + getText( "Nationality effect: %s1", coloredRevIdxFactorStr( iNatIdx ) )

		# TODO: Ignores RevOpt.getNationalityModifier()

		return iNatIdx, szHelp

	def computeNationalityRevIdx( self ) :
		# type: () -> int
		return self.computeNationalityRevIdxAndHelp()[0]


	def computeHealthRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]
		iNumUnhealthy = self._pCity.badHealth( False ) - self._pCity.goodHealth()
		if iNumUnhealthy > 0 :
			szHelp = getText( "Excess [ICON_UNHEALTHY]: %D1", iNumUnhealthy )

			iTempUnhealthy = min( self._pCity.getEspionageHealthCounter(), iNumUnhealthy )
			if iTempUnhealthy > 0 :
				szHelp += u"\n" + getText( "[ICON_BULLET]Only 50% weight for temporary %D1 [ICON_UNHEALTHY]", iTempUnhealthy )
				iNumUnhealthy -= iTempUnhealthy // 2

			iHealthIdx = int( math.floor( 2 * pow( iNumUnhealthy, .6 ) + .5 ) )

			if self._pOwner.isRebel() :
				szHelp += u"\n" + getText( "Base instability from [ICON_UNHEALTHY]: %D1", iHealthIdx )
				szHelp += u"\n" + getText( "[ICON_BULLET]Rebel bonus: %D1%", -66 )
				iHealthIdx //= 3

			szHelp += SEPARATOR
			szHelp += u"\n" + getText( "[ICON_UNHEALTHY] effect: %s1", coloredRevIdxFactorStr( iHealthIdx ) )
			return iHealthIdx, szHelp
		else :
			return 0, getText( "(No excess [ICON_UNHEALTHY])" )

	def computeHealthRevIdx( self ) :
		# type: () -> int
		return self.computeHealthRevIdxAndHelp()[0]


	def computeGarrisonRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]

		# if hasLiberalism :
		#	garIdx = -int( 2*pow(pCity.plot().getNumDefenders(iPlayer)/2.0, .5) - .5 )
		iNumDefenders = self._pCity.plot().getNumDefenders( self._eOwner )
		szHelp = getText( "Number of defenders: %d1", iNumDefenders )

		fDefendersEffect = 2 * pow( iNumDefenders / 2.0, .6 )

		iDefenseMod = min( 100, self._pCity.getBuildingDefense() )
		if iDefenseMod != 0 :
			sDefendersEffect = "%.2f" % fDefendersEffect
			szHelp += u"\n" + getText( "Base effect: %s1", sDefendersEffect )
			szHelp += u"\n" + getText( "[ICON_BULLET]City defense bonus: %D1%", iDefenseMod )

		iGarIdx = -int( fDefendersEffect * ( 100 + iDefenseMod ) ) / 100
		iGarIdx = max( iGarIdx, -8 )
		szHelp += u"\n" + getText( "Garrison effect (capped at -8): %s1", coloredRevIdxFactorStr( iGarIdx ) )
		return iGarIdx, szHelp

	def computeGarrisonRevIdx( self ) :
		# type: () -> int
		return self.computeGarrisonRevIdxAndHelp()[0]


	def computeSizeRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]
		""" Bonus due to small size. Between 0 and -5 """
		iPop = self._pCity.getPopulation()
		iEraBonus = -3 - min( 3, self._pOwner.getCurrentRealEra() )
		szHelp = getText( "City size: %d1", iPop )
		szHelp += u"\n" + getText( "Era bonus: %D1", iEraBonus )
		iSizeRevIdx = min( 0, iPop + iEraBonus )

		szHelp += SEPARATOR
		if iSizeRevIdx != 0 :
			szHelp += u"\n" + getText( "Small city bonus: %s1", coloredRevIdxFactorStr( iSizeRevIdx ) )
		else :
			szHelp += u"\n" + getText( "No small city bonus" )
		return iSizeRevIdx, szHelp

	def computeSizeRevIdx( self ) :
		# type: () -> int
		return self.computeSizeRevIdxAndHelp()[0]


	def computeStarvingRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]

		if self._pCity.foodDifference( True ) < 0 and abs( self._pCity.foodDifference( True ) ) > self._pCity.getFood() :
			iStarvingIdx = 100
			return iStarvingIdx, getText( "City is starving: %D1", iStarvingIdx )
		else :
			return 0, getText( "(City is not starving)" )

	def computeStarvingRevIdx( self ) :
		# type: () -> int
		return self.computeStarvingRevIdxAndHelp()[0]


	def computeDisorderRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]

		if self._pCity.getOccupationTimer() > 0 :
			iDisorderIdx = 75
			szHelp = u""

			iModTimes100 = 100
			if self._bRecentlyAcquired or self._pOwner.isRebel() :
				# Give recently acquired cities a break
				iModTimes100 = 15
				szHelp += getText( "Base disorder effect: %D1", iDisorderIdx )
				szHelp += u"\n" + getText( "[ICON_BULLET]Recently acquired: %D1%", iModTimes100 - 100 )
			elif self._pCity.getRevolutionCounter() > 0 :
				iModTimes100 = 20
				szHelp += getText( "Base disorder effect: %D1", iDisorderIdx )
				szHelp += u"\n" + getText( "[ICON_BULLET]Past revolutions: %D1%", iModTimes100 - 100 )

			if iModTimes100 != 100 :
				iDisorderIdx = iDisorderIdx * iModTimes100 // 100

			if len( szHelp ) > 0 : szHelp += u"\n"
			szHelp += getText( "Disorder effect: %s1", coloredRevIdxFactorStr( iDisorderIdx ) )

			return iDisorderIdx, szHelp

		return 0, getText( "(No disorder)" )

	def computeDisorderRevIdx( self ) :
		# type: () -> int
		return self.computeDisorderRevIdxAndHelp()[0]


	def computeCrimeRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]
		""" RevIdx from crime; -2 to +8. """

		# LFGR_TODO: Make configurable
		iUsualCityCrime = 20  # This crime level means no stability bonus/malus
		iCrimeCap = 100  # No crime above this will be counted
		iCrimeFactorPercent = 10
		iCityCrime = min( self._pCity.getCrime(), iCrimeCap )
		szHelp = getText( "Effective city crime (capped at 100): %d1", iCityCrime )

		iCrimeIdx = (iCityCrime - iUsualCityCrime) * iCrimeFactorPercent // 100
		szHelp += u"\n" + getText( "Crime effect: %s1", coloredRevIdxFactorStr( iCrimeIdx ) )

		return iCrimeIdx, szHelp

	def computeCrimeRevIdx( self ) :
		# type: () -> int
		return self.computeCrimeRevIdxAndHelp()[0]


	def civicsWithLocalEffect( self ) :
		# type: () -> Iterator[Tuple[CvCivicInfo, int]]
		""" Iterates over tuples (eCivic, iRevIdx) """
		for eCivicOption in range( 0,gc.getNumCivicOptionInfos() ) :
			eCivic = self._pOwner.getCivics( eCivicOption )
			if eCivic >= 0  :
				info = gc.getCivicInfo( eCivic )
				iRevIdx = info.getRevIdxLocal()
				# Note: Don't increase effect with other civics with higher LaborFreedon/DemocracyLevel are available.
				if iRevIdx != 0 :
					yield info, iRevIdx

	def computeCivicsRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]
		return effectsToIdxAndHelp( self.civicsWithLocalEffect() )

	def getRevWatchCivicsIdxData( self ) : # TODO: Deprecated
		# type: () -> Tuple[int, List[Tuple[int, unicode]], List[Tuple[int, unicode]]]
		""" Special function for RevWatchAdvisor """
		return effectsToRevWatchData( self.civicsWithLocalEffect() )


	def buildingsWithEffects( self ) :
		for eBuilding in range( gc.getNumBuildingInfos() ) :
			if self._pCity.getNumRealBuilding( eBuilding ) > 0 :
				info = gc.getBuildingInfo( eBuilding )
				iRevIdx = info.getRevIdxLocal()
				if iRevIdx != 0 :
					yield info, iRevIdx

	def computeBuildingsRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]
		return effectsToIdxAndHelp( self.buildingsWithEffects() )

	def getRevWatchBuildingsIdxData( self ) : # TODO: Deprecated
		# type: () -> Tuple[int, List[Tuple[int, unicode]], List[Tuple[int, unicode]]]
		""" Special function for RevWatchAdvisor """
		return effectsToRevWatchData( self.buildingsWithEffects() )


	def computeLocalRevIdxAndFinalModifierHelp( self ) :
		# type () -> Tuple[int, unicode]
		""" The total RevIdx (per turn) of this city. The help string only contains final adjustments. """
		iIdxSum = sum( [ # TODO: Caching
			self.computeHappinessRevIdx(),
			self.computeLocationRevIdx(),
			self.computeReligionRevIdx(),
			self.computeCultureRevIdx(),
			self.computeNationalityRevIdx(),
			self.computeHealthRevIdx(),
			self.computeGarrisonRevIdx(),
			self.computeSizeRevIdx(),
			self.computeStarvingRevIdx(),
			self.computeDisorderRevIdx(),
			self.computeCrimeRevIdx(),
			self.computeCivicsRevIdxAndHelp()[0],
			self.computeBuildingsRevIdxAndHelp()[0]
		] )
		szHelp = getText( "Sum of all effects: %D1", iIdxSum )

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
				szHelp += u"\n" + getText( "[ICON_BULLET]Recent improvements: %D1", iFeedback )
			iAdjustedIdx += iFeedback

		return iAdjustedIdx, szHelp

	def computeLocalRevIdx( self ) :
		# type: () -> int
		return self.computeLocalRevIdxAndFinalModifierHelp()[0]


class PlayerRevIdxHelper :
	"""
	Helper for national RevIdx.
	WARNING: Uses caching, so do not re-use after revolution-relevant events!
	"""
	def __init__( self, ePlayer ) :
		self._ePlayer = ePlayer
		self._pPlayer = gc.getPlayer( ePlayer )
		self._buildingsCache = None

	def computeSizeRevIdxAndHelp( self, bForceText = False ) :
		# type: ( bool ) -> Tuple[int, unicode]
		""" If bForceText, also outputs text if there is no effect. """ # LFGR_TODO: needed?
		fCivSizeValue = RevOpt.getCivSizeModifier() * RevUtils.computeCivSize( self._ePlayer )[0]
		if (fCivSizeValue > 2.0) :
			iSizeIdx = 4
		elif (fCivSizeValue > 1.6) :
			iSizeIdx = 3
		elif (fCivSizeValue > 1.4) :
			iSizeIdx = 2
		elif (fCivSizeValue > 1.2) :
			iSizeIdx = 1
		elif (fCivSizeValue > 1.0) :
			iSizeIdx = 0
		elif (fCivSizeValue > .7) :
			iSizeIdx = -1
		else :
			iSizeIdx = -2

		if iSizeIdx < 0 :
			szHelp = getText( "Small empire: %s1", coloredRevIdxFactorStr( iSizeIdx ) )
		elif iSizeIdx > 0 :
			szHelp = getText( "Large empire: %s1", coloredRevIdxFactorStr( iSizeIdx ) )
		else :
			if bForceText :
				szHelp = getText( "Medium empire: 0" )
			else :
				szHelp = u""

		return iSizeIdx, szHelp


	def computeCultureSpendingRevIdxAndHelp( self ) : # LFGR_TODO: bForceText?
		# type: () -> Tuple[int, unicode]
		szHelp = u""

		iCultPerc = self._pPlayer.getCommercePercent( CommerceTypes.COMMERCE_CULTURE )
		iCultIdx = isqrt( iCultPerc )

		iExtraPercent = 0
		szExtraText = u""
		if self._pPlayer.hasTrait( gc.getInfoTypeForString( "TRAIT_CREATIVE" ) ) : # LFGR_TODO: Make TraitInfo property
			iExtraPercent += 70
			szExtraText += getText( "[ICON_BULLET][COLOR_HIGHLIGHT_TEXT]Creative[COLOR_REVERT]: %d1%", 70 ) + u"\n"

		if szExtraText != u"" :
			szHelp += getText( "Raw culture spending effect: %d1", iCultIdx )
			szHelp += szExtraText # Has a newline at end!
			iCultIdx += iCultPerc * iExtraPercent // 100

		szHelp += getText( "Culture spending effect: %s1", coloredRevIdxFactorStr( iCultIdx ) )

		return iCultIdx, szHelp

	def computeGoldenAgeRevIdxAndHelp( self ) :
		if self._pPlayer.isGoldenAge() :
			iIdx = -20
			return iIdx, getText( "Golden age: %s1", coloredRevIdxFactorStr( iIdx ) )
		return 0, getText( "(No golden age)" )

	def civicsWithNationalEffect( self ) :
		# type: () -> Iterator[Tuple[CvCivicInfo, int]]
		""" Iterates over tuples (pCivic, iRevIdx) """
		for eCivicOption in range( 0,gc.getNumCivicOptionInfos() ) :
			eCivic = self._pPlayer.getCivics( eCivicOption )
			if eCivic >= 0  :
				info = gc.getCivicInfo( eCivic )
				iRevIdx = info.getRevIdxNational()
				# Note: Don't increase effect with other civics with higher LaborFreedon/DemocracyLevel are available.
				if iRevIdx != 0 :
					yield info, iRevIdx

	def computeCivicsRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]
		return effectsToIdxAndHelp( self.civicsWithNationalEffect() )

	def getRevWatchCivicsIdxData( self ) : # TODO: Deprecated
		# type: () -> Tuple[int, List[Tuple[int, unicode]], List[Tuple[int, unicode]]]
		""" Special function for RevWatchAdvisor """
		return effectsToRevWatchData( self.civicsWithNationalEffect() )

	def _buildingsWithNationalEffects( self ) :
		""" Un-cached function"""
		for eBuilding in range( gc.getNumBuildingInfos() ) :
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

	def computeBuildingsRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]
		return effectsToIdxAndHelp( self.buildingsWithNationalEffects() )

	def getRevWatchBuildingsIdxData( self ) : # TODO: Deprecated
		# type: () -> Tuple[int, List[Tuple[int, unicode]], List[Tuple[int, unicode]]]
		""" Special function for RevWatchAdvisor """
		return effectsToRevWatchData( self.buildingsWithNationalEffects() )

	def computeNationalRevIdxAndFinalModifierHelp( self ) :
		# type () -> Tuple[int, unicode]
		""" The total RevIdx (per turn) of this city. The help string only contains final adjustments. """
		iIdxSum = sum( [ # TODO: Caching
			self.computeSizeRevIdxAndHelp()[0],
			self.computeCultureSpendingRevIdxAndHelp()[0],
			self.computeGoldenAgeRevIdxAndHelp()[0],
			self.computeCivicsRevIdxAndHelp()[0],
			self.computeBuildingsRevIdxAndHelp()[0]
		] )

		iAdjustedIdx, szAdjustHelp = adjustedRevIdxAndFinalModifierHelp( iIdxSum, self._pPlayer, bColorFinalIdx = True )

		if szAdjustHelp == u"" :
			szHelp = getText( "Sum of all effects: %s1", coloredRevIdxFactorStr( iIdxSum ) )
		else :
			szHelp = getText( "Sum of all effects: %D1", iIdxSum ) + szAdjustHelp

		# LFGR_TODO: Feedback?

		return iAdjustedIdx, szHelp