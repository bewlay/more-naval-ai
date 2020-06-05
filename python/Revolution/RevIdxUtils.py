"""
Refactor of RevIdx part of Revolution modcomp, for Fall from Heaven 2/MNAI
Changes:
* Removed effects of hardcoded "Nationalism", "Liberalism" and "Scientific Method" techs.
* Instability from nationality no longer reduces the garrison RevIdx cap
* Removed small capital malus in later eras ("To help remove late game tiny civs" -- we don't want that)
* Removed malus for small cities that used to be large
* Streamlined small city bonus
* No unhappiness malus in city with disorder.
* Simplified unhappiness malus
"""


from CvPythonExtensions import *

# Just for IDE, does only work with python 2.7
try : from typing import *
except ImportError : pass

import math

from PyHelpers import getText

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
		# type: (CityRevIdxHelper, CyCity) -> None
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

	def cannotRevoltStr( self ) :
		# type: (CityRevIdxHelper) -> Optional[str]
		"""
		If the city can (generally) revolt, returns None. Otherwise, returns a string explaining why it can't.
		"""
		if self._pCity.isSettlement() and self._pCity.getOwner() == self._pCity.getOriginalOwner() :
			return "Settlements you founded cannot revolt" # TODO: Translation
		return None


	def computeHappinessRevIdx( self ) :
		return self.computeHappinessRevIdxAndHelp()[0]

	def computeHappinessRevIdxHelp( self ) :
		return self.computeHappinessRevIdxAndHelp()[1]

	def computeHappinessRevIdxAndHelp( self ) :
		# type: (CityRevIdxHelper) -> Tuple[int, unicode]

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
			szHelp += getText( "Final instability from unhappiness: %d1", iHappyIdx )

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
			szHelp += getText( "Base stability from happiness (adj. to pop.): %s1",
					"%.2f" % ( iNegHappyIdxTimes100 / 100. ) )

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
			szHelp += getText( "Final stability from happiness: %d1", iNegHappyIdx )

			return -iNegHappyIdx, szHelp

		return 0, u""

	def computeAdjustedCityDistance( self ) :
		# type: (CityRevIdxHelper) -> float

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

	def computeDistModifier( self ) :
		# type: (CityRevIdxHelper) -> float
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

	def computeLocationRevIdx( self ) :
		# type: (CityRevIdxHelper) -> int
		# By phungus
		# Distance to capital City Distance modified by communication techs and structures

		fCityDist = self.computeAdjustedCityDistance() * self.computeDistModifier()

		locationRevIdx = 0

		if self._fCivSizeRawVal > 2.0 :
			locationRevIdx += int( math.floor( 2.0 * fCityDist + .5 ) )
		elif self._fCivSizeRawVal > 1.6 :
			locationRevIdx += int( math.floor( 1.65 * fCityDist + .5 ) )
		elif self._fCivSizeRawVal > 1.4 :
			locationRevIdx += int( math.floor( 1.45 * fCityDist + .5 ) )
		elif self._fCivSizeRawVal > 1.2 :
			locationRevIdx += int( math.floor( 1.25 * fCityDist + .5 ) )
		elif self._fCivSizeRawVal > 1.0 :
			locationRevIdx += int( math.floor( fCityDist + .5 ) )
		elif self._fCivSizeRawVal > .7 :
			locationRevIdx += int( math.floor( .75 * fCityDist + .5 ) )
		else :
			locationRevIdx += int( math.floor( .5 * fCityDist + .5 ) )

		return int( math.floor( locationRevIdx + .5 ) )

	def computeColonyRevIdx( self ) :
		# type: (CityRevIdxHelper) -> int

		pCapital = self._pOwner.getCapitalCity() # TODO: Make obj var

		if self._pCity.area().getID() == pCapital.area().getID() :
			return 0 # Not a colony

		fCityDistModifier = self.computeAdjustedCityDistance()
		fDistModAlt = self.computeDistModifier()
		colonyModifier = RevOpt.getColonyModifier() # LFGR_TODO: type?

		# Base colony
		fColBase = min( fCityDistModifier * self._pCity.getPopulation() / 3.0 + 0.5, 10 )

		"""
		# Effect of nationality increased if Nationalism tech is known
		# LFGR_TODO: Use this in some other way? Techs seems a really bad trigger, as they are hard to avoid.
		# LFGR_TODO: Use self._iCulturePercent (adds team)?
		fNationalityMod = 1.0
		if self._bHasNationalism :
			if self._pCity.getCultureLevel() > 2 :
				if self._pCity.plot().calculateCulturePercent( self._eOwner ) > 90 :
					fNationalityMod = 0.5
				elif self._pCity.plot().calculateCulturePercent( self._eOwner ) <= 70 :
					fNationalityMod = 1.2
			else :
				fNationalityMod = 1.5
		"""
		#iColonyIdx = int( math.floor( colonyModifier * fDistModAlt * fNationalityMod * fColBase + .5 ) )
		iColonyIdx = int( math.floor( colonyModifier * fDistModAlt * fColBase + .5 ) )

		# If single colony, bonus from high cultures, small island, and closeness to capital.
		if self._pCity.area().getNumCities() == 1 :
			if self._iCulturePercent > 90 :
				if plotDistance( self._pCity.getX(), self._pCity.getY(), pCapital.getX(),
								  pCapital.getY() ) < 2.0 * RevOpt.getCloseRadius() :
					iColonyIdx = 0
				elif plotDistance( self._pCity.getX(), self._pCity.getY(), pCapital.getX(),
									pCapital.getY() ) < 4.0 * RevOpt.getCloseRadius() :
					iColonyIdx /= 3
				else :
					iColonyIdx /= 2
			elif self._pCity.area().getNumTiles() < 5 :
				iColonyIdx /= 2
		return iColonyIdx

	def computeConnectionRevIdx( self ) :
		# type: (CityRevIdxHelper) -> int

		pCapital = self._pOwner.getCapitalCity()

		if pCapital is not None and not self._pCity.isConnectedTo( pCapital ) :
			if self._bRecentlyAcquired or self._pOwner.isRebel() :
				return 3
			else :
				return min( 5 + self._pOwner.getCurrentRealEra() + self._pCity.getPopulation() / 3, 10 )

		return 0

	def computeHolyCityOwnershipRevIdx( self ) :
		# type: (CityRevIdxHelper) -> int
		# LFGR_TODO: Should this be National idx?
		eStateReligion = self._pOwner.getStateReligion()
		if self._pOwner.isStateReligion() and eStateReligion != -1 : # LFGR_TODO: Necessary?
			iHolyCityGood, iHolyCityBad = RevUtils.getCivicsHolyCityEffects( self._eOwner )
			if self._pCity.isHasReligion( eStateReligion ) :
				pStateHolyCity = game.getHolyCity( eStateReligion )
				if not pStateHolyCity.isNone() :
					eHolyCityOwner = pStateHolyCity.getOwner()
					if eHolyCityOwner == self._eOwner :
						#posList.append( (-iHolyCityGood, localText.getText( "TXT_KEY_REV_WATCH_HOLY_CITY", () )) )
						return -iHolyCityGood # We own the holy city
					elif gc.getPlayer( eHolyCityOwner ).getStateReligion() != eStateReligion :
						return iHolyCityBad # Heathens own the holy city!
						#negList.append( (iHolyCityBad, localText.getText( "TXT_KEY_REV_WATCH_HEATHENS", () )) )

		return 0

	def computeReligionRevIndices( self ) :
		# type: (CityRevIdxHelper) -> Tuple[int, int]
		# Returns (goodIdx, badIdx), where goodIdx is idx based on state religion in city, and
		#   badIdx is based on non-state religion in city
		eStateReligion = self._pOwner.getStateReligion()
		if self._pOwner.isStateReligion() and eStateReligion != -1 : # LFGR_TODO: Necessary?
			# LFGR_TODO: Take religion type into account
			iRelGoodIdx = 0
			fRelBadIdx = 0
			for eReligion in range( 0, gc.getNumReligionInfos() ) :
				if self._pCity.isHasReligion( eReligion ) :
					if eReligion == eStateReligion :
						iRelGoodIdx += 4
					else :
						if fRelBadIdx > 4 :
							fRelBadIdx += 1
						else :
							fRelBadIdx += 2.5

			# Holy city
			if self._pCity.isHolyCity() :
				if self._pCity.isHolyCityByType( eStateReligion ) :
					iRelGoodIdx += 5
				else :
					fRelBadIdx += 4


			# LFGR_TODO: This is not used at all!
			relGoodMod, relBadMod = RevUtils.getCivicsReligionMods( self._eOwner )
			if self._pOwnerTeam.getAtWarCount( True ) > 1 :
				# God is on your side =P
				iRelGoodIdx = int( math.floor( iRelGoodIdx * 1.5 + .5 ) )

			fMod = RevOpt.getReligionModifier()

			iRelGoodIdx = - int( math.floor( fMod * iRelGoodIdx + .5 ) )
			iRelBadIdx = int( math.floor( fMod * fRelBadIdx + .5 ) )
			return iRelGoodIdx, iRelBadIdx

		return 0, 0

	def computeCultureRevIdx( self ) :
		# type: (CityRevIdxHelper) -> int
		# LFGR_TODO: Subtracting era probably doesn't have much of an effect; should increase this effect or remove it.
		iAdjCultRate = max( self._pCity.getCommerceRate( CommerceTypes.COMMERCE_CULTURE ) - self._pOwner.getCurrentRealEra(), 0 )
		# LFGR_TODO: Why the hell take abs, and not max(0,...)?
		iCultureIdx = - min( int( pow( abs( iAdjCultRate / (1.5 + self._pOwner.getCurrentRealEra() / 3.0) ), .7 ) + 0.5 ), 10 )
		iCultureIdx = int( math.floor( RevOpt.getCultureRateModifier() * iCultureIdx + .5 ) )
		if self._bWarWithMaxCult and not self._pOwner.isRebel() :
			iCultureIdx /= 2
		return iCultureIdx

	def computeNationalityRevIdx( self ) :
		# type: (CityRevIdxHelper) -> int

		iCultureRate = self._pCity.getCommerceRate( CommerceTypes.COMMERCE_CULTURE )

		iNatIdx = 0
		# LFGR_TODO: This scaling is kind of weird
		if self._iCulturePercent > 90 :
			iNatIdx = -4
		elif self._iCulturePercent > 70 :
			iNatIdx = -2
		elif self._iCulturePercent < 20 :
			iNatIdx = 26
			iNatIdx -= iCultureRate
			iNatIdx = max( iNatIdx, 9 )
		elif self._iCulturePercent < 40 :
			iNatIdx = 15
			iNatIdx -= iCultureRate
			iNatIdx = max( iNatIdx, 6 )
		elif self._iCulturePercent < 50 :
			iNatIdx = 8
			iNatIdx -= iCultureRate / 2
			iNatIdx = max( iNatIdx, 3 )
		elif self._iCulturePercent < 60 :
			iNatIdx = 3
			iNatIdx -= iCultureRate / 2
			iNatIdx = max( iNatIdx, 0 )

		if self._bRecentlyAcquired :
			iNatIdx = min( iNatIdx * 3 / 5, 12 )

		if self._bWarWithMaxCult and not self._pOwner.isRebel() and iNatIdx > 0 :
			iNatIdx = (3 * iNatIdx) / 2
		elif self._bMaxCultIsVassal and iNatIdx > 0 :
			iNatIdx = min( [(2 * iNatIdx) / 3, 10] )

		#if not hasNationalism :
		iNatIdx = int( math.floor( (1 * iNatIdx) / 2.0 + .5 ) )

		# Civic nationality effects (only for bad nationality mod)
		if iNatIdx > 0 :
			natMod = RevUtils.getCivicsNationalityMod( self._eOwner )
			iNatIdx = int( math.floor( iNatIdx * (1.0 + natMod) + .5 ) )

		return int( math.floor( RevOpt.getNationalityModifier() * iNatIdx + .5 ) )

	def getHealthRevIdx( self ) :
		# type: (CityRevIdxHelper) -> int
		iNumUnhealthy = self._pCity.badHealth( False ) - self._pCity.goodHealth()
		if iNumUnhealthy > 0 :
			iHealthIdx = int( math.floor( 2 * pow( iNumUnhealthy, .6 ) + .5 ) )
			if self._pCity.getEspionageHealthCounter() > 0 or self._pOwner.isRebel() :
				iHealthIdx = iHealthIdx / 3
			return iHealthIdx
		else :
			return 0

	def getGarrisonRevIdx( self ) :
		# type: (CityRevIdxHelper) -> int

		# if hasLiberalism :
		#	garIdx = -int( 2*pow(pCity.plot().getNumDefenders(iPlayer)/2.0, .5) - .5 )
		iNumDefenders = self._pCity.plot().getNumDefenders( self._eOwner )
		fDefendersEffect = pow( iNumDefenders / 2.0, .6 )
		if self._pCity.getBuildingDefense() > 75 :
			garIdx = -int( 3 * fDefendersEffect + .5 )
		elif self._pCity.getBuildingDefense() > 25 :
			garIdx = -int( 2.5 * fDefendersEffect )
		else :
			garIdx = -int( 2 * fDefendersEffect - .5 )

		# LFGR_TODO: This seems somewhat low (in absolute)
		return max( garIdx, -8 )

	def getSpiritRevIdx( self ) :
		# type: (CityRevIdxHelper) -> int
		# LFGR_TODO: Not sure if this is really necessary

		if self._pCity.getNumRevolts( self._eOwner ) > 2 :
			# LFGR_TODO: This seems bad, because it gets updated even on graphical revIdx calculations.
			iPrevRevIdx = self._pCity.getRevolutionIndex()
			# LFGR_TODO: Why HumanWarnFrac?
			if iPrevRevIdx > RevOpt.getHumanWarnFrac() * RevDefs.revInstigatorThreshold :
				return self._pCity.getNumRevolts( self._eOwner ) / 2

		return 0

	def getSizeRevIdx( self ) :
		# type: (CityRevIdxHelper) -> int
		""" Bonus due to small size. Between 0 and -5 """
		return min( 0, -3 + self._pCity.getPopulation() - min( self._pOwner.getCurrentRealEra(), 3 ) )

	def getStarvingRevIdx( self ) :
		# type: (CityRevIdxHelper) -> int

		if self._pCity.foodDifference( True ) < 0 :
			if abs( self._pCity.foodDifference( True ) ) > self._pCity.getFood() :
				iStarvingIdx = 100
			else :
				# LFGR_TODO: This is problematic, as a negative food difference can be useful and is probably used by the AI
				iStarvingIdx = min( 4 * abs( self._pCity.foodDifference( True ) ), 20 )

			if self._pCity.getEspionageHealthCounter() > 0 or self._pOwner.isRebel() :
				# LFGR_TODO: Why does EspionageHealthCounter reduce this? Because the espHealthCounter would be too good otherwise?
				iStarvingIdx = max( iStarvingIdx / 5, min( iStarvingIdx, 10 ) )
			return iStarvingIdx
		return 0

	def getDisorderRevIdx( self ) :
		# type: (CityRevIdxHelper) -> int

		if self._pCity.getOccupationTimer() > 0 :
			if self._bRecentlyAcquired or self._pOwner.isRebel() :
				# Give recently acquired cities a break
				return 10
			elif self._pCity.getRevolutionCounter() > 0 :
				return 15
			else :
				return 75
		return 0

	def getCrimeRevIdx( self ) :
		# type: (CityRevIdxHelper) -> int
		""" RevIdx from crime; -2 to +8. """

		# LFGR_TODO: Make configurable
		iUsualCityCrime = 20  # This crime level means no stability bonus/malus
		iCrimeCap = 100  # No crime above this will be counted
		iCrimeFactorPercent = 10
		iCityCrime = min( self._pCity.getCrime(), iCrimeCap )
		return (iCityCrime - iUsualCityCrime) * iCrimeFactorPercent // 100