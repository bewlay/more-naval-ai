"""
Refactor of RevIdx part of Revolution modcomp, for Fall from Heaven 2/MNAI

All calculations for local and national RevIdx will ultimately be moved here.
"""


from CvPythonExtensions import *

import itertools

from PyHelpers import getText, PyPlayer

import BugCore
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

# TODO: Move this code below. It's only used once.
def adjustedRevIdxAndFinalModifierHelp( iRawIdx, pPlayer, bColorFinalIdx = False ) :
	# type (int, CyPlayer) -> (int, unicode)
	"""
	Adjust given raw RevIdx for Game speed and other modifiers. Used for both local and national RevIdx.
	Help string documents changes and stars with "\n" if is not empty.

	bColorFinalIdx indicates whether the final adjusted index should be colored
	"""
	szHelp = u""

	# Adjust index accumulation for varying game speeds
	fGameSpeedMod = RevUtils.getGameSpeedMod() # TODO: Remove floating-point arithmetic
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
			szHelp += NL_SEPARATOR + u"\n" + getText( "Adjusted: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iAdjustedIdx ) )
		else :
			szHelp += NL_SEPARATOR + u"\n" + getText( "Adjusted: %D1[ICON_INSTABILITY]", iAdjustedIdx )

	return iAdjustedIdx, szHelp

def modAsPercent( fMod ) :
	""" Converts a modifier (such as 0.7) to a percentage (such as -30) """
	return int( ( fMod - 1 ) * 100 )

def computeInfoRevEffectsAndHelp( lpInfoList, valueFunc, szTemplate, bColor ) :
	# type: (List[CvInfoBase], Callable[[CvInfoBase], int], str, bool) -> Iterator[Tuple[int, unicode]]
	""" Generic function to compute and add up effects from a list of infos. """

	for pInfo in lpInfoList :
		iValue = valueFunc( pInfo )
		if iValue != 0 :
			if bColor :
				value = coloredRevIdxFactorStr( iValue )
			else :
				value = iValue
			yield ( iValue, getText( szTemplate, value, pInfo.getDescription() ) )

def sumValuesAndHelp( *ltValuesAndHelp ) :
	# type: (Tuple[int, unicode]) -> Tuple[int, unicode]
	""" Helper function for component-wise summing. """
	iValue = 0
	szHelp = u""
	for iLoopValue, szLoopHelp in ltValuesAndHelp :
		iValue += iLoopValue
		szHelp += u"\n" + szLoopHelp
	return iValue, szHelp


def playerCannotRevoltStr( pPlayer ) :
	# type: (CyPlayer) -> Optional[unicode]
	"""
	If cities of this player can (generally) revolt, return None. Otherwise, return a string explaining why they can't.
	"""

	if pPlayer.getSanctuaryTimer() > 0 :
		return "No revolutions (Sanctuary)"

	if pPlayer.getDisableProduction() > 0 :
		return "No revolutions (Stasis)"

	if pPlayer.getCivilizationType() == gc.getInfoTypeForString( "CIVILIZATION_INFERNAL") :
		return "Demons do not revolt" # TODO: Tie to demonic citizens via XML

	return None

def cityCannotRevoltStr( pCity ) :
	# type: (CyCity) -> Optional[unicode]
	"""
	If the city can accumulate RevIdx, return None. Otherwise, return a string explaining why it can't.
	"""
	if pCity.isSettlement() and pCity.getOwner() == pCity.getOriginalOwner() :
		return getText( "Settlements you founded cannot revolt" )

	szPlayerStr = playerCannotRevoltStr( gc.getPlayer( pCity.getOwner() ) )
	if szPlayerStr :
		return szPlayerStr

	return None


class NationalEffectBuildingsInfoCache :
	""" Caches all building(type)s that have an effect on all cities"""

	_instance = None

	def __init__( self ) :
		self._leBuildings = []
		for eBuilding in range( gc.getNumBuildingInfos() ) :
			kBuilding = gc.getBuildingInfo( eBuilding )
			if not kBuilding.getRevIdxEffectsAllCities().is_zero() :
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
			# TODO: Count and merge multiple instances of the same building?
			for pCity in PyPlayer( self._ePlayer ).iterCities() :
				if pCity.isHasBuilding( eBuilding ) :
					yield gc.getBuildingInfo( eBuilding )

	def buildingsWithNationalEffects( self ) :
		# type: () -> Sequence[Tuple[CvBuildingInfo, int]]
		"""
		Returns a collection of buildings that have a nationwide effect.
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


	### Generic RevIdx functions
	
	def computeCivicEffectsAndHelp( self, revEffectsFunc, szTemplate, bColor ) :
		# type: (Callable[[CvRevolutionEffects], int], str, bool) -> Iterator[Tuple[int, unicode]]
		return computeInfoRevEffectsAndHelp(
				self._pyOwner.iterCivicInfos(),
				lambda pCivic : revEffectsFunc( pCivic.getRevIdxEffects() ),
				szTemplate, bColor )
	
	def computeLocalBuildingEffectsAndHelp( self, revEffectsFunc, szTemplate, bColor ) :
		# type: (Callable[[CvRevolutionEffects], int], str, bool) -> Iterator[Tuple[int, unicode]]
		return computeInfoRevEffectsAndHelp(
				self._lpBuildings,
				lambda pBuilding : revEffectsFunc( pBuilding.getRevIdxEffects() ),
				szTemplate, bColor )
	
	def computeNationalBuildingEffectsAndHelp( self, revEffectsFunc, szTemplate, bColor ) :
		# type: (Callable[[CvRevolutionEffects], int], str, bool) -> Iterator[Tuple[int, unicode]]
		return computeInfoRevEffectsAndHelp(
			self._pPlayerCache.buildingsWithNationalEffects(),
			lambda pBuilding : revEffectsFunc( pBuilding.getRevIdxEffectsAllCities() ),
			szTemplate, bColor )
	
	def computeGenericEffectsAndHelp( self, revEffectsFunc, szCivicHelp, szLocalBuildingHelp, szNationalBuildingHelp, bColor ) :
		# type: (Callable[[CvRevolutionEffects], int], str, str, str, bool) -> Iterable[Tuple[int, unicode]]
		return itertools.chain( 
				self.computeCivicEffectsAndHelp( revEffectsFunc, szCivicHelp, bColor ),
				self.computeLocalBuildingEffectsAndHelp( revEffectsFunc, szLocalBuildingHelp, bColor ),
				self.computeNationalBuildingEffectsAndHelp( revEffectsFunc, szNationalBuildingHelp, bColor )
			)
		# TODO: religions, traits...?
	
	def computeGenericModifiersTimes100AndHelp( self, revEffectsFunc ) :
		# type: (Callable[[CvRevolutionEffects], int]) -> Tuple[int, unicode]
		return sumValuesAndHelp(
			*self.computeGenericEffectsAndHelp( revEffectsFunc,
				"[ICON_BULLET]%D1% from [COLOR_CIVIC_TEXT]%s2[COLOR_REVERT]",
				"[ICON_BULLET]%D1% from [COLOR_BUILDING_TEXT]%s2[COLOR_REVERT]",
				"[ICON_BULLET]%D1% from [COLOR_BUILDING_TEXT]%s2[COLOR_REVERT] (national)", False ) )
	
	def computeGenericCapChangeAndHelp( self, revEffectsFunc ) :
		# type: (Callable[[CvRevolutionEffects], int]) -> Tuple[int, unicode]
		return sumValuesAndHelp(
			*self.computeGenericEffectsAndHelp( revEffectsFunc,
				"[ICON_BULLET][COLOR_CIVIC_TEXT]%s2[COLOR_REVERT]: %D1",
				"[ICON_BULLET][COLOR_BUILDING_TEXT]%s2[COLOR_REVERT]: %D1",
				"[ICON_BULLET][COLOR_BUILDING_TEXT]%s2[COLOR_REVERT]: %D1 in all cities", False ) )
	
	def computeGenericPerTurnAndHelp( self, revEffectsFunc ) :
		# type: (Callable[[CvRevolutionEffects], int]) -> Tuple[int, unicode]
		return sumValuesAndHelp(
			*self.computeGenericEffectsAndHelp( revEffectsFunc,
				"[ICON_BULLET][COLOR_CIVIC_TEXT]%s2[COLOR_REVERT]: %s1[ICON_INSTABILITY]",
				"[ICON_BULLET][COLOR_BUILDING_TEXT]%s2[COLOR_REVERT]: %s1[ICON_INSTABILITY]",
				"[ICON_BULLET][COLOR_BUILDING_TEXT]%s2[COLOR_REVERT]: %s1[ICON_INSTABILITY] in all cities", True ) )

	def _modifiedCapAndHelp( self, iBaseCap, capChangeFunc ) :
		iCapChange, szCapChangeHelp = self.computeGenericCapChangeAndHelp( capChangeFunc )
		iCap = iBaseCap + iCapChange

		if szCapChangeHelp :
			szHelp = u"\n" + getText( "Base cap: %d1", iBaseCap ) + szCapChangeHelp
		else :
			szHelp = u"\n" + getText( "Cap: %d1", iBaseCap )

		return iCap, szHelp


	### Specific RevIdx functions
	
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
		
		if bUnhappiness :
			effectsFunc = CvRevolutionEffects.getRevIdxUnhappinessMod
		else :
			effectsFunc = CvRevolutionEffects.getRevIdxHappinessMod
		
		iExtraMod, szExtraHelp = self.computeGenericModifiersTimes100AndHelp( effectsFunc )
		iMod += iExtraMod
		szHelp += szExtraHelp

		return iMod, szHelp

	def computeHappinessRevIdxAndHelp( self ) :
		# type: () -> Tuple[int, unicode]

		szHelp = getText( "[COLOR_HIGHLIGHT_TEXT]Happiness/Unhappiness[COLOR_REVERT]" )

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

			# Base effect
			iUnhappyPerPopTimes100 = 100 * iNumUnhappy // self._pCity.getPopulation()
			szHelp += u"\n" + getText( "[ICON_UNHAPPY] per population: %s1", "%.2f" % ( iUnhappyPerPopTimes100 / 100. ) )
			iBaseHappyIdx = iUnhappyPerPopTimes100
			szHelp += u"\n"
			szHelp += getText( "Base effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iBaseHappyIdx ) )

			# Modifiers
			iModTimes100, szModHelp = self.computeHappinessModifiersTimes100AndHelp( bUnhappiness = True )
			iIdx = iBaseHappyIdx * max( 0, iModTimes100 ) // 100
			szHelp += szModHelp


			# Cap
			iCap = min( 100, 10 * self._pCity.getPopulation() )
			szHelp += NL_SEPARATOR
			szHelp += u"\n" + getText( "Cap from population: %d1", iCap )
			iIdx = min( iIdx, iCap )

			# Total
			szHelp += NL_SEPARATOR
			szHelp += u"\n"
			szHelp += getText( "From unhappiness: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iIdx ) )
			return iIdx, szHelp
		elif iNumUnhappy < 0 :
			szHelp += u"\n"
			szHelp += getText( "Excess happiness: %d1[ICON_HAPPY]", -iNumUnhappy )

			# Base effect
			iHappyPerPopTimes100 = 100 * -iNumUnhappy // self._pCity.getPopulation()
			szHelp += u"\n" + getText( "[ICON_HAPPY] per population: %s1", "%.2f" % ( iHappyPerPopTimes100 / 100. ) )
			iBaseHappyIdx = -iHappyPerPopTimes100 // 10

			# Subtotal
			szHelp += u"\n"
			szHelp += getText( "Base effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iBaseHappyIdx ) )

			# Modifiers
			iModTimes100, szModHelp = self.computeHappinessModifiersTimes100AndHelp( bUnhappiness = False )
			iIdx = iBaseHappyIdx * max( 0, iModTimes100 ) // 100
			szHelp += szModHelp

			# Cap
			iBaseCap = 10  # TODO: Make define
			iCap, szCapHelp = self._modifiedCapAndHelp( iBaseCap, CvRevolutionEffects.getRevIdxHappinessCapChange )
			iIdx = max( -iCap, iIdx )
			szHelp += NL_SEPARATOR
			szHelp += szCapHelp

			# Total
			szHelp += NL_SEPARATOR
			szHelp += u"\n"
			szHelp += getText( "From happiness: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iIdx ) )

			return iIdx, szHelp
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
			iAdjDistTimes100 = iCityDistRaw * iDistMod / iMaxPlotDist
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
		
		iGenMod, szGenHelp = self.computeGenericModifiersTimes100AndHelp( CvRevolutionEffects.getRevIdxLocationMod )
		iMod += iGenMod
		szModHelp += szGenHelp

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

	# TODO: Split into good and bad effects (+/- in table header)
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

			# Preparation: do we own the holy city?
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

			# Holy city ownership
			# TODO: Use helper functions
			# TODO: Should not benefit from religion modifiers. Maybe move to various effects?
			if bOwnHolyCity :
				iHolyCityIdx, szHolyCityHelp = sumValuesAndHelp( *itertools.chain(
					( ( pInfo.getRevIdxEffects().getRevIdxHolyCityOwned(),
						getText( "[ICON_BULLET][COLOR_CIVIC_TEXT]%s1[COLOR_REVERT], we own %F2: %s3[ICON_INSTABILITY]",
							pInfo.getDescription(), pStateReligion.getHolyCityChar(), coloredRevIdxFactorStr( pInfo.getRevIdxEffects().getRevIdxHolyCityOwned() ) ) )
						for pInfo in self._pyOwner.iterCivicInfos() if pInfo.getRevIdxEffects().getRevIdxHolyCityOwned() != 0 ),
					( ( pInfo.getRevIdxEffects().getRevIdxHolyCityOwned(),
						getText( "[ICON_BULLET][COLOR_BUILDING_TEXT]%s1[COLOR_REVERT], we own %F2: %s3[ICON_INSTABILITY] in all cities",
							pInfo.getDescription(), pStateReligion.getHolyCityChar(), coloredRevIdxFactorStr( pInfo.getRevIdxEffects().getRevIdxHolyCityOwned() ) ) )
						for pInfo in self._lpBuildings if pInfo.getRevIdxEffects().getRevIdxHolyCityOwned() != 0 ),
					( ( pInfo.getRevIdxEffects().getRevIdxHolyCityOwned(),
						getText( "[ICON_BULLET][COLOR_BUILDING_TEXT]%s1[COLOR_REVERT], we own %F2: %s3[ICON_INSTABILITY] in all cities",
							pInfo.getDescription(), pStateReligion.getHolyCityChar(), coloredRevIdxFactorStr( pInfo.getRevIdxEffects().getRevIdxHolyCityOwned() ) ) )
						for pInfo in self._pPlayerCache.buildingsWithNationalEffects() if pInfo.getRevIdxEffects().getRevIdxHolyCityOwned() != 0 )
				) )
				iGoodIdx += iHolyCityIdx
				lszGoodHelpLines.append( szHolyCityHelp )
			if bInfidelsOwnHolyCity :
				iHolyCityIdx, szHolyCityHelp = sumValuesAndHelp( *itertools.chain(
					( ( pInfo.getRevIdxEffects().getRevIdxHolyCityHeathenOwned(),
						getText( "[ICON_BULLET][COLOR_CIVIC_TEXT]%s1[COLOR_REVERT], infidels own %F2: %s3[ICON_INSTABILITY]",
							pInfo.getDescription(), pStateReligion.getHolyCityChar(), coloredRevIdxFactorStr( pInfo.getRevIdxEffects().getRevIdxHolyCityHeathenOwned() ) ) )
						for pInfo in self._pyOwner.iterCivicInfos() if pInfo.getRevIdxEffects().getRevIdxHolyCityOwned() != 0 ),
					( ( pInfo.getRevIdxEffects().getRevIdxHolyCityHeathenOwned(),
						getText( "[ICON_BULLET][COLOR_BUILDING_TEXT]%s1[COLOR_REVERT], infidels own %F2: %s3[ICON_INSTABILITY] in all cities",
							pInfo.getDescription(), pStateReligion.getHolyCityChar(), coloredRevIdxFactorStr( pInfo.getRevIdxEffects().getRevIdxHolyCityHeathenOwned() ) ) )
						for pInfo in self._lpBuildings if pInfo.getRevIdxEffects().getRevIdxHolyCityOwned() != 0 ),
					( ( pInfo.getRevIdxEffects().getRevIdxHolyCityHeathenOwned(),
						getText( "[ICON_BULLET][COLOR_BUILDING_TEXT]%s1[COLOR_REVERT], infidels own %F2: %s3[ICON_INSTABILITY] in all cities",
							pInfo.getDescription(), pStateReligion.getHolyCityChar(), coloredRevIdxFactorStr( pInfo.getRevIdxEffects().getRevIdxHolyCityHeathenOwned() ) ) )
						for pInfo in self._pPlayerCache.buildingsWithNationalEffects() if pInfo.getRevIdxEffects().getRevIdxHolyCityOwned() != 0 )
				) )
				iBadIdx += iHolyCityIdx
				lszBadHelpLines.append( szHolyCityHelp )

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
			iGoodMod, szGoodMod = self.computeGenericModifiersTimes100AndHelp( CvRevolutionEffects.getRevIdxGoodReligionMod )
			iBadMod, szBadMod = self.computeGenericModifiersTimes100AndHelp( CvRevolutionEffects.getRevIdxBadReligionMod )
			lszGoodHelpLines.append( szGoodMod.strip() ) # TODO: Not a line...
			lszBadHelpLines.append( szBadMod.strip() )

			# Apply mods
			iGoodIdx = iGoodIdx * ( iGoodMod + 100 ) // 100
			iBadIdx = iBadIdx * ( iBadMod + 100 ) // 100

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

		# TODO: Now only negative, update CvRevolutionEffects.getRevIdxNationalityMod help text

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
		iBaseIdx = (100 - iCulturePercent)**2 // 500

		# Modifiers
		iMod, szModHelp = self.computeGenericModifiersTimes100AndHelp( CvRevolutionEffects.getRevIdxNationalityMod )

		if szModHelp :
			szHelp += u"\n" + getText( "Base effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iBaseIdx ) )
			szHelp += szModHelp

		iNatIdx = iBaseIdx * max( 0, 100 + iMod ) // 100

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

		# Modifiers
		iMod, szModHelp = self.computeGenericModifiersTimes100AndHelp( CvRevolutionEffects.getRevIdxGarrisonMod )

		if szModHelp :
			szHelp += u"\n" + getText( "Base effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iBaseIdx ) )
			szHelp += szModHelp
		
		# Cap
		iBaseCap = 10 # TODO: Make define
		iCap, szCapHelp = self._modifiedCapAndHelp( iBaseCap, CvRevolutionEffects.getRevIdxGarrisonCapChange )
		szHelp += szCapHelp

		iGarIdx = max( -iCap, iBaseIdx * max( 0, 100 + iMod ) // 100 )
		szHelp += u"\n" + getText( "Garrison effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iGarIdx ) )

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
			
			iGenMod, szGenModHelp = self.computeGenericModifiersTimes100AndHelp( CvRevolutionEffects.getRevIdxDisorderMod )
			iModTimes100 += iGenMod
			szHelp += szGenModHelp

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
		""" RevIdx from crime; 0 to +10. """

		szHelp = getText( "[COLOR_HIGHLIGHT_TEXT]Crime[COLOR_REVERT]" )

		# LFGR_TODO: Make configurable
		iCrimeCap = 100  # No crime above this will be counted
		iCrimeFactorPercent = 10
		iCityCrime = min( self._pCity.getCrime(), iCrimeCap )

		iBaseCrimeIdx = iCityCrime * iCrimeFactorPercent // 100
		szHelp += u"\n" + getText( "Effective crime (max. %d2): %d1", iCityCrime, iCrimeCap )

		# Modifiers
		iMod, szModHelp = self.computeGenericModifiersTimes100AndHelp( CvRevolutionEffects.getRevIdxCrimeMod )
		# TODO: Un-hardcode
		eStateReligion = self._pOwner.getStateReligion()
		if eStateReligion == gc.getInfoTypeForString( "RELIGION_COUNCIL_OF_ESUS" ) :
			if self._pCity.isHasReligion( eStateReligion ) :
				iRelMod = -50
				iMod += iRelMod
				szModHelp += u"\n" + getText( "[ICON_BULLET]%D1% from %F2",
						iRelMod, gc.getReligionInfo( eStateReligion ).getChar() )

		iCrimeIdx = iBaseCrimeIdx * ( iMod + 100 ) // 100
		if szModHelp :
			szHelp += u"\n" + getText( "Base crime effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iCrimeIdx ) )
			szHelp += szModHelp
			szHelp += NL_SEPARATOR

		szHelp += u"\n" + getText( "Crime effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iCrimeIdx ) )

		return iCrimeIdx, szHelp

	def computeCrimeRevIdx( self ) :
		# type: () -> int
		return self.computeCrimeRevIdxAndHelp()[0]


	def computeCultureRateRevIdxAndHelp( self ) :
		# type: () -> (int, int)
		szHelp = getText( "[COLOR_HIGHLIGHT_TEXT]Culture Rate[COLOR_REVERT]" )

		iCultRate = self._pCity.getCommerceRate( CommerceTypes.COMMERCE_CULTURE )
		szHelp += u"\n" + getText( "%d1 [ICON_CULTURE]/Turn", iCultRate )

		iBaseIdx = -isqrt( 2 * iCultRate )
		szHelp += u"\n" + getText( "Base culture rate effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iBaseIdx ) )

		iMod, szModHelp = self.computeGenericModifiersTimes100AndHelp( CvRevolutionEffects.getRevIdxCultureRateMod )
		iIdx = iBaseIdx * ( iMod + 100 ) // 100
		szHelp += szModHelp

		iBaseCap = 10 # TODO: Define
		iCap, szCapHelp = self._modifiedCapAndHelp( iBaseCap, CvRevolutionEffects.getRevIdxCultureRateCapChange )
		szHelp += szCapHelp

		iIdx = max( iIdx, -iCap )
		szHelp += u"\n" + getText( "Culture Rate effect: %s1[ICON_INSTABILITY]", coloredRevIdxFactorStr( iIdx ) )

		return iIdx, szHelp


	def _computeHealthRevIdxAndCap( self ) :
		# type: () -> Tuple[int, int]
		iCap = 10 # TODO: Make define
		iNumUnhealthy = self._pCity.badHealth( False ) - self._pCity.goodHealth()
		if iNumUnhealthy > 0 :
			iHealthIdx = min( iCap, iNumUnhealthy )
		else :
			iHealthIdx = 0
		return iHealthIdx, iCap

	def _computeStarvingRevIdx( self ) :
		# type: () -> int
		if self._pCity.foodDifference( True ) < 0 and abs( self._pCity.foodDifference( True ) ) > self._pCity.getFood() :
			if not self._pCity.isSettlement() :
				return 100
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
		
		iBaseIdx = gc.getDefineINT( "BASE_REV_IDX" )
		yield "Base effect", iBaseIdx
		
		iStarvingIdx = self._computeStarvingRevIdx()
		if iStarvingIdx != 0 :
			yield "TXT_KEY_REV_WATCH_STARVATION", iStarvingIdx

		iGoldenAgeIdx = self._computeGoldenAgeRevIdx()
		if iGoldenAgeIdx != 0 :
			yield "Golden Age", iGoldenAgeIdx

		iSizeIdx = self._computeEmpireSizeRevIdx()
		if iSizeIdx < 0 :
			yield "Small empire", iSizeIdx
		elif iSizeIdx > 0 :
			yield "Large empire", iSizeIdx

	def computeVariousRevIdxAndHelp( self ) :
		iVariousIdx = 0
		szHelp = getText( "[COLOR_HIGHLIGHT_TEXT]Various effects[COLOR_REVERT]" )

		szVariousHelp = u""

		# Simple things
		for szDesc, iLoopIdx in self._computeSimpleFactorsWithEffect() :
			iVariousIdx += iLoopIdx
			szVariousHelp += u"\n" + getText( "[ICON_BULLET]%s1: %s2[ICON_INSTABILITY]",
					szDesc, coloredRevIdxFactorStr( iLoopIdx ) )

		# Health
		iHealthIdx, iCap = self._computeHealthRevIdxAndCap()
		if iHealthIdx != 0 :
			iVariousIdx += iHealthIdx
			szVariousHelp += u"\n" + getText( "[ICON_BULLET]Unhealthiness: %s1[ICON_INSTABILITY] (max: %d2)",
					coloredRevIdxFactorStr( iHealthIdx ), iCap )

		# Buildings/civics/... with local effects
		iGenIdx, szGenHelp = self.computeGenericPerTurnAndHelp( CvRevolutionEffects.getRevIdxPerTurn )
		iVariousIdx += iGenIdx
		if szGenHelp :
			szVariousHelp += szGenHelp

		if szVariousHelp :
			szHelp += szVariousHelp
		else :
			szHelp += getText( "(none)" ) # TODO?

		return iVariousIdx, szHelp


	def computeRevIdxAndFinalModifierHelp( self ) :
		# type () -> Tuple[int, unicode]
		""" The total RevIdx (per turn) of this city. The help string only contains final adjustments. """

		# Check whether city can revolt at all
		szCannotRevolt = cityCannotRevoltStr( self._pCity )
		if szCannotRevolt is not None :
			return 0, getText( "[COLOR_POSITIVE_TEXT]%s1[COLOR_REVERT]", szCannotRevolt )

		iIdxSum = sum( [ # TODO: Caching
			self.computeHappinessRevIdx(),
			self.computeLocationRevIdx(),
			self.computeReligionRevIdx(),
			self.computeNationalityRevIdx(),
			self.computeGarrisonRevIdx(),
			self.computeDisorderRevIdx(),
			self.computeCrimeRevIdx(),
			self.computeCultureRateRevIdxAndHelp()[0],
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
	
	def computeRevIdxPopupHelp( self ) :
		# type: () -> unicode

		# Check whether city can revolt at all
		szCannotRevolt = cityCannotRevoltStr()
		if szCannotRevolt is not None :
			return szCannotRevolt

		# Record lists of (#, string type) effects, seperate for positive and negative
		ltEffects = [
			( self.computeHappinessRevIdx(), getText( "TXT_KEY_REV_WATCH_HAPPINESS" ) ),
			( self.computeLocationRevIdx(), getText( "TXT_KEY_REV_WATCH_DISTANT" ) ),
			( self.computeReligionRevIdx(), getText( "Religion" ) ),
			( self.computeNationalityRevIdx(), getText( "TXT_KEY_REV_WATCH_NATIONALITY" ) ),
			( self.computeGarrisonRevIdx(), getText( "TXT_KEY_REV_WATCH_GARRISON" ) ),
			( self.computeDisorderRevIdx(), getText( "TXT_KEY_REV_WATCH_DISORDER" ) ),
			( self.computeCrimeRevIdx(), getText( "Crime" ) ),
			( self.computeCultureRateRevIdxAndHelp()[0], getText( "Culture Rate" ) )
		]
		
		ltEffects.extend( ( iEffect, getText( szDesc ) ) for szDesc, iEffect in self._computeSimpleFactorsWithEffect() )
		ltEffects.extend( self.computeGenericEffectsAndHelp( CvRevolutionEffects.getRevIdxPerTurn, "%s2", "%s2", "%s2 (national)", False ) )
		
		ltPosEffects = [ (iEffect, szDesc) for iEffect, szDesc in ltEffects if iEffect < 0]
		ltNegEffects = [ (iEffect, szDesc) for iEffect, szDesc in ltEffects if iEffect > 0]
		
		ltPosEffects.sort()
		ltNegEffects.sort( reverse = True )
		
		# Create text
		szTooltip = u""
		
		szTooltip += u"<color=0,230,0,255> " + getText( "TXT_KEY_REV_WATCH_POSITIVE" ) + u"<color=255,255,255,255> "
		szTooltip += ", ".join( "%s: %s" % ( szDesc, coloredRevIdxFactorStr( iEffect ) ) for iEffect, szDesc in ltPosEffects )

		szTooltip += u"\n<color=255,10,10,255> " + getText( "TXT_KEY_REV_WATCH_NEGATIVE" ) + u"<color=255,255,255,255> "
		szTooltip += ", ".join( "%s: %s" % ( szDesc, coloredRevIdxFactorStr( iEffect ) ) for iEffect, szDesc in ltNegEffects )
		
		szTooltip += u"\n\n" + self.computeRevIdxAndFinalModifierHelp()[1]
		
		return szTooltip
