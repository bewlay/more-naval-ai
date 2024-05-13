"""
Defines and utilities related to spawning rebel units.
"""

from CvPythonExtensions import *

import itertools

from PyHelpers import all, any, sorenRandChoice
# import BugCore
import CvUtil


# 0: no logging, 1 : normal logging, 2+: verbose logging
LOG_LEVEL = 5 # TODO

gc = CyGlobalContext()
# RevOpt = BugCore.game.Revolution


### Generic Utility

def log( s ) :
	# type: ( str ) -> None
	CvUtil.pyPrint( "  RevUnits - %s" % s )

def emptyPrereq( *args, **kwargs ) :
	return True

def emptyGenerator( *args, **kwargs ) :
	return ()

def chainGenerators( *lCallables ) :
	# type: ( Callable[..., Iterable[...]] ) -> Callable[..., Iterable[...]]
	def func( *args, **kwargs ) :
		for callable in lCallables :
			for x in callable( *args, **kwargs ) :
				yield x
	return func

def fixedValue( value ) :
	def func( *args, **kwargs ) :
		return value
	return func


### Civ-replated utility

def canPlayerTrain( pPlayer, eUnit ) :
	# type: ( CyPlayer, int ) -> bool
	return pPlayer.canTrain( eUnit, False, False ) # bContinue, bTestVisible

def getPlayerUnit( pPlayer, eClass ) :
	return gc.getCivilizationInfo( pPlayer.getCivilizationType() ).getCivilizationUnits( eClass )

def spawnUnit( pPlayer, eUnit, iX, iY ) :
	# type: ( CyPlayer, int, int, int ) -> CyUnit
	if LOG_LEVEL >= 2 : log( "  Spawning unit %s for %s at %d|%d" % ( gc.getUnitInfo( eUnit ).getType(), pPlayer.getName(), iX, iY ) )
	return pPlayer.initUnit( eUnit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH )


### Unit Rules backend

class UnitDesc( object ) :
	""" Abstract class.
	A description of a rebel unit that may spawn. Should fix unit type and some promotions, may give some random
		or context-dependent promotions when spawning. UnitAI may be fixed or decided when spawning.
	"""
	def spawn( self, pCity, pRevPlayer, iX, iY, idx, iRebelsHere, iRebelsIn3 = 0, iRebelsIn6 = 0 ) :
		# type: ( CyCity, CyPlayer, int, int, int, int, int, int ) -> CyUnit
		raise NotImplementedError()

class UnitRule( object ) :
	""" Abstract class.
	A generator for UnitDescs matching a certain role; chooses a list of best UnitDesc that fit that role.
	"""
	def findBest( self, pCity, pRevPlayer ) :
		# type: ( CyCity, CyPlayer ) -> Iterable[UnitDesc]
		raise NotImplementedError()


### Rule implementations

class ComplexUnitDesc( UnitDesc ) :
	def __init__( self,
			eUnitType, # type: int
			promotionGenerator, # type: Callable[[CyUnit, CyCity], Iterable[int]]
			unitAIGenerator # type: Callable[[CyUnit, int, int, int, int], UnitAITypes]
			) : # type: (...) -> None
		self._eUnitType = eUnitType
		self._promotionGenerator = promotionGenerator
		self._unitAIGenerator = unitAIGenerator

	def spawn( self, pCity, pRevPlayer, iX, iY, idx, iRebelsHere, iRebelsIn3=0, iRebelsIn6=0 ) :
		pUnit = spawnUnit( pRevPlayer, self._eUnitType, iX, iY )
		for ePromo in self._promotionGenerator( pUnit, pCity ) :
			pUnit.setHasPromotion( ePromo, True )
		if pUnit.canFight() :
			eOldUnitAI = pUnit.getUnitAIType()
			eNewUnitAI = self._unitAIGenerator( pUnit, idx, iRebelsHere, iRebelsIn3, iRebelsIn6 )
			if eOldUnitAI != eNewUnitAI :
				pUnit.setUnitAIType( eNewUnitAI )
				if LOG_LEVEL >= 1 : log( "%s changing AI type: %s -> %s" % (
					pUnit.getName(), gc.getUnitAIInfo( eOldUnitAI ).getType(), gc.getUnitAIInfo( eNewUnitAI ).getType() ) )
		
		return pUnit
	
	def __str__( self ) : # For debug output
		return "ComplexUnitDesc[%s]" % gc.getUnitInfo( self._eUnitType ).getType()


class PriorityUnitRule( UnitRule ) :
	""" Chooses the latest valid unit given. """
	def __init__( self,
			lsClasses,  # type: Sequence[str]
			promotionGenerator,  # type: Callable[[CyUnit], Iterable[int]]
			unitAIGenerator  # type: Callable[[CyUnit, int, int, int, int], UnitAITypes]
			) :  # type: ( ... ) -> None
		self._leClasses = [CvUtil.findUnitClassNum( sClass ) for sClass in reversed( lsClasses )]
		self._promotionGenerator = promotionGenerator
		self._unitAIGenerator = unitAIGenerator

	def findBest( self, pCity, pRevPlayer ) :
		# type: ( CyCity, CyPlayer ) -> Iterable[UnitDesc]
		for eClass in self._leClasses :
			eUnit = getPlayerUnit( pRevPlayer, eClass )
			if eUnit != -1 and canPlayerTrain( pRevPlayer, eUnit ) :
				yield ComplexUnitDesc( eUnit, self._promotionGenerator, self._unitAIGenerator )
				return


class ScoreUnitRule( UnitRule ) :
	""" Helper Superclass for unit rules that are based on generating UnitDescs with scores. """
	
	def unitsWithScore( self, pCity, pRevPlayer ) :
		# type: ( CyCity, CyPlayer ) -> Iterable[Tuple[UnitDesc, int]]
		raise NotImplementedError()
	
	def findBest( self, pCity, pRevPlayer ) :
		# type: ( CyCity, CyPlayer ) -> Iterable[UnitDesc]
		if LOG_LEVEL >= 1 : log( "Find best unit for %s (%s)" % (pCity.getName(), pRevPlayer.getName()) )
		ltBest = []
		iBestScore = 0
		for unitDesc, iScore in self.unitsWithScore( pCity, pRevPlayer ) :
			if LOG_LEVEL >= 2 : log( "  Score for %s : %d" % ( unitDesc, iScore ) )
			if iScore > iBestScore :
				ltBest = [unitDesc]
				iBestScore = iScore
			elif iScore == iBestScore :
				ltBest.append( unitDesc )
		return ltBest


class FixedScoreRule( ScoreUnitRule ) :
	""" Generates UnitDescs with score solely depending on the unit class """
	def __init__( self,
			ltClassesWithValue,  # type: Sequence[Tuple[str, int]]
			promotionGenerator,  # type: Callable[[CyUnit, CyCity], Iterable[int]]
			unitAIGenerator  # type: Callable[[CyUnit, int, int, int, int], UnitAITypes]
			) :  # type: ( ... ) -> None
		self._ltClassesWithValue = [( CvUtil.findUnitClassNum( sClass ), iValue ) for sClass, iValue in ltClassesWithValue]
		self._promotionGenerator = promotionGenerator
		self._unitAIGenerator = unitAIGenerator

	def unitsWithScore( self, pCity, pRevPlayer ) :
		# type: ( CyCity, CyPlayer ) -> Iterable[Tuple[UnitDesc, int]]
		for eClass, iValue in self._ltClassesWithValue :
			eUnit = getPlayerUnit( pRevPlayer, eClass )
			if eUnit != -1 and canPlayerTrain( pRevPlayer, eUnit ) :
				yield ComplexUnitDesc( eUnit, self._promotionGenerator, self._unitAIGenerator ), iValue


class ComplexUnitRule( ScoreUnitRule ) :
	"""
	Chooses the best valid unit based on an evaluation function. May specify a function that gives a non-random set
	  of promotions that the evaluation function takes into consideration.
	"""
	def __init__( self,
			lsClasses, # type: Sequence[str]
			prereq, # type: Callable[[int, CyCity, CyPlayer], bool]
			basicPromotionGenerator, # type: Callable[[int, CyCity, CyPlayer], Iterable[int]]
			unitEvaluator, # type: Callable[[CyCity, CyPlayer, int, Iterable[int]], int]
			randomPromotionGenerator, # type: Callable[[CyUnit, CyCity], Iterable[int]]
			unitAIGenerator # type: Callable[[CyUnit, int, int, int, int], UnitAITypes]
			) :
		"""
		:param lsClasses: Unit classes that this rule may generate
		:param prereq: Prereq function. Only unit types satisfying it may be generated.
				Signature: ( UnitTypes, CyCity, pRevPlayer : CyPlayer ) -> bool
		:param basicPromotionGenerator: Function to generate basic promotions.
				Must be deterministic, as it is used in evaluating which unit to pick.
				Signature: ( UnitTypes, CyCity, pRevPlayer : CyPlayer ) -> Iterable[PromotionTypes]
		:param unitEvaluator: Function that assigns a score to each possible unit type.
				Only the best units according to this score are generated.
				Signature: ( CyCity, CyPlayer, UnitTypes, Iterable[PromotionTypes] ) -> int
		:param randomPromotionGenerator: Function to generate promotion for individual spawned units. Usually randomized.
				Signature: ( CyUnit ) -> Iterable[PromotionTypes]
		:param unitAIGenerator: Function to generate appropriate UnitAIs to individual spawned units
				Signature: ( CyUnit, idx : int, iRebelsHere : int, iRebelsIn3 : int, iRebelsIn6 : int ) -> UnitAITypes
		"""
		self._leClasses = [CvUtil.findUnitClassNum( sClass ) for sClass in lsClasses]
		self._prereq = prereq
		self._basicPromotionGenerator = basicPromotionGenerator
		self._randomPromotionGenerator = randomPromotionGenerator
		self._unitEvaluator = unitEvaluator
		self._unitAIGenerator = unitAIGenerator
	
	def _promotionGenerator( self, pUnit, pCity ) :
		# type: (CyUnit, CyCity) -> Iterable[int]
		return itertools.chain( self._basicPromotionGenerator( pUnit.getUnitType(), pCity, gc.getPlayer( pUnit.getOwner() ) ),
				self._randomPromotionGenerator( pUnit, pCity ) )
	
	def _makeDesc( self, eUnit ) :
		# type: ( int ) -> UnitDesc
		return ComplexUnitDesc( eUnit, self._promotionGenerator, self._unitAIGenerator )
	
	def unitsWithScore( self, pCity, pRevPlayer ) :
		# type: ( CyCity, CyPlayer ) -> Iterable[UnitDesc]
		if LOG_LEVEL >= 1 : log( "Generate units for %s in %s" % (pRevPlayer.getName(), pCity.getName()) )
		for eUnitClass in self._leClasses :
			eUnit = gc.getCivilizationInfo( pRevPlayer.getCivilizationType() ).getCivilizationUnits( eUnitClass )
			if eUnit != -1 and self._prereq( eUnit, pCity, pRevPlayer ) :
				lePromos = list( self._basicPromotionGenerator( eUnit, pCity, pRevPlayer ) )
				iScore = self._unitEvaluator( pCity, pRevPlayer, eUnit, lePromos )
				yield self._makeDesc( eUnit ), iScore


class MageUnitRule( ScoreUnitRule ) :
	"""
	Generate possible mage units based on available mana.
	  Specifies which magic promotions may be given to mage units of a certain tier, if the associated mana is available.
	  Score is based on the highest-value magic promotion.
	  Units that would get no magic promotions are not generated.
	"""
	def __init__( self, lsClasses, dilManaPromotionByMagicTier ) :
		# type: ( List[str], Dict[int, List[Tuple[str, int]]] ) -> None
		"""
		dilsManaPromotionByMagicTier[i] is a list of tuples ("MANA_NAME", iValue)
		"""
		self._leClasses = [CvUtil.findUnitClassNum( sClass ) for sClass in reversed( lsClasses )]
		self._dilsManaPromotionByMagicTier = dilManaPromotionByMagicTier
		self._dChannelingPromos = {} # No dict comprehension in py2.4 :(
		for i in [1, 2, 3] :
			self._dChannelingPromos[i] = CvUtil.findPromotionNum( "PROMOTION_CHANNELING" + str( i ) )

	def unitsWithScore( self, pCity, pRevPlayer ) :
		# type: ( CyCity, CyPlayer ) -> Iterable[Tuple[UnitDesc, int]]
		manaTypes = getManaTypes( pCity, pRevPlayer )
		if LOG_LEVEL >= 2 : log( "Mana types: %s" % ", ".join( gc.getBonusInfo( eMana ).getType() for eMana in sorted( manaTypes ) ) )
		for eClass in self._leClasses :
			eUnit = getPlayerUnit( pRevPlayer, eClass )
			if eUnit != -1 and canPlayerTrain( pRevPlayer, eUnit ) :
				unitInfo = gc.getUnitInfo( eUnit )
				for iTier in [3,2,1] :
					if unitInfo.getFreePromotions( self._dChannelingPromos[iTier] ) :
						ltAvailableManaWithPrio = [(sMana, iPrio) for sMana, iPrio in self._dilsManaPromotionByMagicTier[iTier]
								if CvUtil.findBonusNum( "BONUS_MANA_%s" % sMana ) in manaTypes]
						if len( ltAvailableManaWithPrio ) > 0 :
							iPrio = max( iPrio for _, iPrio in ltAvailableManaWithPrio )
							lPromotions = [ "PROMOTION_%s%d" % ( sMana, j )
									for j in range( 1, iTier+1 )
									for sMana, _ in ltAvailableManaWithPrio]
							# TODO: Appropriate UnitAI?
							yield ComplexUnitDesc( eUnit, FixedPromotionGenerator( *lPromotions ).for_spawned_unit,
												   SimpleUnitAIGenerator( UnitAITypes.UNITAI_WARWIZARD ) ), iPrio


class CombinedScoreUnitRule( ScoreUnitRule ) :
	def __init__( self, *lRules ) :
		# type: ( ScoreUnitRule ) -> None
		self._lRules = lRules
	
	def unitsWithScore( self, pCity, pRevPlayer ) :
		# type: ( CyCity, CyPlayer ) -> Iterable[Tuple[UnitDesc, int]]
		for rule in self._lRules :
			for unitDesc, iScore in rule.unitsWithScore( pCity, pRevPlayer ) :
				yield unitDesc, iScore


### Generic prereq functions

def _prereqPlayerCanTrain( eUnit, _pCity, pRevPlayer ) :
	# type: ( int, CyCity, CyPlayer ) -> bool
	return canPlayerTrain( pRevPlayer, eUnit )

def _prereqMatchReligion( eUnit, _pCity, pRevPlayer ) :
	# type: ( int, CyCity, CyPlayer ) -> bool
	ePrereqReligion = gc.getUnitInfo( eUnit ).getPrereqReligion()
	return ePrereqReligion in ( -1, pRevPlayer.getStateReligion() )

def allPrereqs( *lPrereqFuncs ) :
	# type: ( Callable[..., bool] ) -> Callable[..., bool]
	def result( *args, **kwargs ) :
		return all( func( *args, **kwargs ) for func in lPrereqFuncs )
	return result


### Generic basic promotion functions

def _getBestWeaponPromotion( eUnit, pCity ) :
	# type: (int, CyCity) -> Optional[int]
	iMaxWeaponTier = gc.getUnitInfo( eUnit).getWeaponTier()
	for i in range( iMaxWeaponTier, 0, -1 ) :
		eBonus = gc.getDefineINT( "WEAPON_REQ_BONUS_TIER%d" % i )
		if pCity.hasBonus( eBonus ) :
			return gc.getDefineINT( "WEAPON_PROMOTION_TIER%d" % i )
	return None

def generateWeaponPromotions( eUnit, pCity, _pRevPlayer ) :
	# type: ( int, CyCity, CyPlayer ) -> Iterator[int]
	ePromo = _getBestWeaponPromotion( eUnit, pCity )
	if ePromo is not None :
		yield ePromo

class FixedPromotionGenerator :
	def __init__( self, *lsPromotions ) :
		# type: ( str ) -> None
		self._lePromotions = [ CvUtil.findPromotionNum( sPromo ) for sPromo in lsPromotions ]
	
	def generate( self, eUnit ) :
		# type: ( int ) -> Iterator[int]
		for ePromo in self._lePromotions :
			if isPromotionValid( ePromo, eUnit, True ) : # bLeader = True (allow leader promotions)
				yield ePromo
	
	def __call__( self, eUnit, _pCity, _pRevPlayer ) :
		# type: ( int, CyCity, CyPlayer ) -> Iterator[int]
		return self.generate( eUnit )
	
	def for_spawned_unit( self, pUnit, _pCity ) :
		# type: ( CyUnit, CyCity ) -> Iterator[int]
		""" Conversion to spawned-unit promotion generator. """
		return self.generate( pUnit.getUnitType() )

class RandomPromotionGenerator :
	def __init__( self, *ltPromotionsWithOdds ) :
		# type: ( Tuple[str, int] ) -> None
		self._ltPromotionsWithOdds = [ ( CvUtil.findPromotionNum( sPromo ), iOdds ) for sPromo, iOdds in ltPromotionsWithOdds ]
	
	def __call__( self, pUnit, _pCity ) :
		# type: ( CyUnit, ... ) -> Iterator[int]
		for ePromo, iOdds in self._ltPromotionsWithOdds :
			if iOdds >= 100 or gc.getGame().getSorenRandNum( 100, "Give rebel promotion" ) < iOdds :
				if pUnit.canAcquirePromotion( ePromo ) :
					yield ePromo


### Generic evaluation functions

def valueByTier( _pCity, _pRevPlayer, eUnit, _lePromos ) :
	# type: (CyCity, CyPlayer, int, Iterable[int]) -> int
	return gc.getUnitInfo( eUnit ).getTier()

class UnitStrengthEvaluator :
	def __init__( self, bAttack, bCity = False ) :
		# type: (bool, bool) -> None
		""" bAttack: Check attack combat (defense otherwise); bCity: Check city combat modifiers """
		self._bAttack = bAttack
		self._bCity = bCity
	
	def __call__( self, _pCity, pRevPlayer, eUnit, lePromos ) :
		# type: (CyCity, CyPlayer, int, Iterable[int]) -> int
		
		# Find player bonus amounts for affinity
		ltBoniWithCounts = []
		for eBonus in xrange( gc.getNumBonusInfos() ) :
			iCount = pRevPlayer.getNumAvailableBonuses( eBonus )
			if iCount > 0 :
				ltBoniWithCounts.append( (eBonus, iCount) )
		
		# Stuff from unit info
		unitInfo = gc.getUnitInfo( eUnit )
		iCombat = self._bAttack and unitInfo.getCombat() or unitInfo.getCombatDefense()
		iCombat += sum( unitInfo.getDamageTypeCombat( eDmg ) for eDmg in xrange( gc.getNumDamageTypeInfos() ) )
		for eBonus, iCount in ltBoniWithCounts :
			iCombat += iCount * unitInfo.getBonusAffinity( eBonus )
		iMod = 100
		if self._bCity :
			iMod += self._bAttack and unitInfo.getCityAttackModifier() or unitInfo.getCityDefenseModifier()
		if not self._bAttack and not unitInfo.isNoDefensiveBonus() :
			iMod += 20
		
		# Add free promotions
		lePromos = list( lePromos )
		for ePromotion in xrange( gc.getNumPromotionInfos() ) :
			if unitInfo.getFreePromotions( ePromotion ) :
				lePromos.append( ePromotion )
		
		# Stuff from promotions
		for ePromo in lePromos :
			promotionInfo = gc.getPromotionInfo( ePromo )
			iCombat += self._bAttack and promotionInfo.getExtraCombatStr() or promotionInfo.getExtraCombatDefense()
			iCombat += sum( promotionInfo.getDamageTypeCombat( eDmg ) for eDmg in xrange( gc.getNumDamageTypeInfos() ) )
			for eBonus, iCount in ltBoniWithCounts :
				iCombat += iCount * promotionInfo.getBonusAffinity( eBonus )
			iMod += promotionInfo.getCombatPercent()
			if self._bCity :
				iMod += self._bAttack and promotionInfo.getCityAttackPercent() or promotionInfo.getCityDefensePercent()
		
		return iCombat * iMod


### Generic UnitAI functions

def _unitAIValue( pUnit, eUnitAI ) :
	# type: (CyUnit, Union[int, UnitAITypes]) -> int
	return gc.getPlayer( pUnit.getOwner() ).AI_unitValue( pUnit.getUnitType(), eUnitAI, pUnit.area(), False )

class SimpleUnitAIGenerator :
	def __init__( self, *leUnitAIs ) :
		# type: ( UnitAITypes ) -> None
		self._leUnitAIs = leUnitAIs

	def __call__( self, pUnit, _idx, _iRebelsHere, _iRebelsIn3, _iRebelsIn6 ) :
		# type: ( CyUnit, int, int, int, int ) -> UnitAITypes
		for eUnitAI in self._leUnitAIs :
			if _unitAIValue( pUnit, eUnitAI ) > 0 :
				return eUnitAI
		return pUnit.getUnitAIType()


### Magic Utility

def _getManaTypes( pCity, pPlayer ) :
	# type: ( CyCity, CyPlayer ) -> Iterator[BonusTypes]
	
	# Pretend player has a palace
	ePalace = gc.getCivilizationInfo( pPlayer.getCivilizationType() ).getCivilizationBuildings(
			CvUtil.findBuildingClassNum( "BUILDINGCLASS_PALACE" ) )
	if ePalace is not None :
		palaceInfo = gc.getBuildingInfo( ePalace )
		yield palaceInfo.getFreeBonus()
		yield palaceInfo.getFreeBonus2()
		yield palaceInfo.getFreeBonus3()
	
	# Bonuses the player or the city actually has
	for eBonus in xrange( gc.getNumBonusInfos() ) :
		bonus = gc.getBonusInfo( eBonus )
		if bonus.isMana() :
			if pPlayer.getNumAvailableBonuses( eBonus ) > 0 or pCity.hasBonus( eBonus ) :
				yield eBonus

def getManaTypes( pCity, pPlayer ) :
	# type: ( CyCity, CyPlayer ) -> Set[BonusTypes]
	return set( filter( lambda e : e != -1, _getManaTypes( pCity, pPlayer ) ) )

### Unit Rule ATTACK

# lfgr: extracted from Revolution.py
def computeAttackUnitAI( pUnit, idx, iRebelsHere, iRebelsIn3, iRebelsIn6 ) :
	# type: ( CyUnit, int, int, int, int ) -> UnitAITypes
	
	bAllowAttackCity = idx < 2 and iRebelsHere + iRebelsIn3 > 2 
	bAllowPillage = iRebelsHere == 1 and iRebelsIn6 < 3
	
	if pUnit.isBarbarian() :
		if _unitAIValue( pUnit, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING ) > 0 :
			return UnitAITypes.UNITAI_ATTACK_CITY_LEMMING
		else :
			return UnitAITypes.UNITAI_ATTACK
	else :
		if bAllowAttackCity and _unitAIValue( pUnit, UnitAITypes.UNITAI_ATTACK_CITY ) > 0 :
			return UnitAITypes.UNITAI_ATTACK_CITY
		elif bAllowPillage and gc.getGame().getSorenRandNum( 2, 'Revolt - Pillage' ) == 0 \
				and _unitAIValue( pUnit, UnitAITypes.UNITAI_PILLAGE ) > 0 :
			return UnitAITypes.UNITAI_PILLAGE
		else :
			iniAI = pUnit.getUnitAIType()
			if not (iniAI == UnitAITypes.UNITAI_COUNTER or iniAI == UnitAITypes.UNITAI_ATTACK_CITY) :
				return UnitAITypes.UNITAI_ATTACK
	return pUnit.getUnitAIType()

def makeRule_ATTACK() :
	return ComplexUnitRule( [
			"UNITCLASS_WARRIOR",
			"UNITCLASS_AXEMAN",
			"UNITCLASS_CHAMPION",
			"UNITCLASS_HORSEMAN",
			"UNITCLASS_CHARIOT",
			"UNITCLASS_HORSE_ARCHER",
			"UNITCLASS_ARQUEBUS"
		],
		_prereqPlayerCanTrain,
		chainGenerators( generateWeaponPromotions, FixedPromotionGenerator( "PROMOTION_COMBAT1" ) ),
		UnitStrengthEvaluator( bAttack = True, bCity = True ),
		RandomPromotionGenerator( # 2 free promotions on average
			( "PROMOTION_COMBAT2", 20 ),
				( "PROMOTION_SHOCK", 20 ),
				( "PROMOTION_COVER", 20 ),
				( "PROMOTION_DRILL1", 20 ),
				( "PROMOTION_CITY_RAIDER1", 20 )
		),
		computeAttackUnitAI )


### Unit Rule CITY_DEFENSE

# LFGR_TODO: Nightwatch would be nice, but probably doesn't work, since hidden nationality messes up placement
def makeRule_CITY_DEFENSE() :
	return ComplexUnitRule( [
				"UNITCLASS_WARRIOR",
				"UNITCLASS_AXEMAN",
				"UNITCLASS_CHAMPION",
				"UNITCLASS_ARCHER",
				"UNITCLASS_LONGBOWMAN",
				"UNITCLASS_HORSEMAN",
				"UNITCLASS_HORSE_ARCHER",
				"UNITCLASS_ARQUEBUS"
			],
			_prereqPlayerCanTrain,
			chainGenerators( generateWeaponPromotions, FixedPromotionGenerator( "PROMOTION_CITY_GARRISON1" ) ),
			UnitStrengthEvaluator( bAttack = False, bCity = True ),
			RandomPromotionGenerator( # 1.5 free promotions on average
				( "PROMOTION_CITY_GARRISON2", 25 ),
				( "PROMOTION_COMBAT1", 25 )
			),
			SimpleUnitAIGenerator( UnitAITypes.UNITAI_CITY_DEFENSE, UnitAITypes.UNITAI_COUNTER ) )


### Unit Rule COUNTER_DEFENSE

def makeRule_COUNTER_DEFENSE() :
	return ComplexUnitRule( [
				"UNITCLASS_WARRIOR",
				"UNITCLASS_AXEMAN",
				"UNITCLASS_CHAMPION",
				"UNITCLASS_ARCHER",
				"UNITCLASS_LONGBOWMAN",
				"UNITCLASS_HUNTER",
				"UNITCLASS_RANGER",
				"UNITCLASS_HORSEMAN",
				"UNITCLASS_HORSE_ARCHER",
				"UNITCLASS_ARQUEBUS"
			],
			_prereqPlayerCanTrain,
			chainGenerators( generateWeaponPromotions, FixedPromotionGenerator( "PROMOTION_COMBAT1" ) ),
			UnitStrengthEvaluator( bAttack = False ),
			RandomPromotionGenerator( # 2 free promotions on average
				( "PROMOTION_SHOCK", 25 ),
				( "PROMOTION_COVER", 25 ),
				( "PROMOTION_FORMATION", 25 ),
				( "PROMOTION_SENTRY", 25 )
			),
			SimpleUnitAIGenerator( UnitAITypes.UNITAI_COUNTER ) )


### Unit Rule HEALER

def makeRule_HEALER() :
	return ComplexUnitRule( [
				"UNITCLASS_DISCIPLE_EMPYREAN",
				"UNITCLASS_PRIEST_OF_THE_EMPYREAN",
				"UNITCLASS_DISCIPLE_FELLOWSHIP_OF_LEAVES",
				"UNITCLASS_PRIEST_OF_LEAVES",
				"UNITCLASS_DISCIPLE_OCTOPUS_OVERLORDS",
				"UNITCLASS_PRIEST_OF_THE_OVERLORDS",
				"UNITCLASS_DISCIPLE_RUNES_OF_KILMORPH",
				"UNITCLASS_PRIEST_OF_KILMORPH",
				"UNITCLASS_DISCIPLE_THE_ASHEN_VEIL",
				"UNITCLASS_PRIEST_OF_THE_VEIL",
				"UNITCLASS_DISCIPLE_THE_ORDER",
				"UNITCLASS_PRIEST_OF_THE_ORDER",
				"UNITCLASS_GRIGORI_MEDIC"
			],
			allPrereqs( _prereqPlayerCanTrain, _prereqMatchReligion ),
			generateWeaponPromotions,
			valueByTier,
			emptyGenerator,
			SimpleUnitAIGenerator( UnitAITypes.UNITAI_MEDIC ) )


### Unit Rule COLLATERAL

def makeRule_COLLATERAL() :
	return CombinedScoreUnitRule(
			# Siege
			FixedScoreRule( [("UNITCLASS_CATAPULT", 2), ("UNITCLASS_CANNON", 5)],
				RandomPromotionGenerator(
					("PROMOTION_CITY_RAIDER1", 35),
					("PROMOTION_BARRAGE1", 35),
					("PROMOTION_ACCURACY", 30)
				), SimpleUnitAIGenerator( UnitAITypes.UNITAI_COLLATERAL ) ),
			
			# Debuff/Mass-damage mage
			MageUnitRule( ["UNITCLASS_ADEPT", "UNITCLASS_MAGE", "UNITCLASS_MOBIUS_WITCH"],
				{  # By magic tier
					1 : [("ENTROPY", 1)],
					2 : [("AIR", 4), ("FIRE", 3)]
				} ),
			
			# Ritualist
			FixedScoreRule( [("UNITCLASS_PRIEST_OF_THE_VEIL", 4)],
				RandomPromotionGenerator( ( "PROMOTION_COMBAT1", 50 ) ),
				SimpleUnitAIGenerator( UnitAITypes.UNITAI_COLLATERAL ) )
	)


### Unit Rule SUPPORT

def makeRule_SUPPORT() :
	return CombinedScoreUnitRule(
		# Buff/Control mage
		MageUnitRule( ["UNITCLASS_ADEPT", "UNITCLASS_MAGE", "UNITCLASS_MOBIUS_WITCH"],
		{  # By magic tier
			1 : [
				("ICE", 1), # Slow
				("SPIRIT", 1), # Courage
				("BODY", 2), # Haste
				("CHAOS", 2), # Dance of Blades
				("SHADOW", 2) # Blur
			],
			2 : [
				("BODY", 3), # Regeneration # TODO: Also as healer?
				("SHADOW", 3) # Shadowwalk
			]
		} ),
		ComplexUnitRule( ["UNITCLASS_PRIEST_OF_THE_ORDER"],
			allPrereqs( _prereqPlayerCanTrain, _prereqMatchReligion ),
			FixedPromotionGenerator( "PROMOTION_COMBAT1" ),
			lambda *args : 2, # Value
			emptyGenerator,
			SimpleUnitAIGenerator( UnitAITypes.UNITAI_MAGE ) # TODO: Correct UnitAI?
		)
	)

# LFGR_TODO: Extra unit rules: ATTACK_RELIGIOUS, COUNTER_RELIGIOUS for religions revolutions -> CombinedScoreUnitRule
#   or handle this via a special parameter? Maybe allow passing a parameter dict to everything?

### Unit Rule Store

class UnitRuleStore :
	_instance = None # type: Optional[UnitRuleStore]
	
	def __init__( self ) :
		self.RULES = {
			"ATTACK" : makeRule_ATTACK(),
			"CITY_DEFENSE" : makeRule_CITY_DEFENSE(),
			"COUNTER_DEFENSE" : makeRule_COUNTER_DEFENSE(),
			"HEALER" : makeRule_HEALER(),
			"COLLATERAL" : makeRule_COLLATERAL(),
			"SUPPORT" : makeRule_SUPPORT(),
			"WORKER" : PriorityUnitRule( ["UNITCLASS_WORKER"], emptyGenerator, SimpleUnitAIGenerator( UnitAITypes.UNITAI_WORKER ) )
		} # type: Mapping[str, ComplexUnitRule]
	
	@staticmethod
	def getInstance() :
		if UnitRuleStore._instance is None :
			UnitRuleStore._instance = UnitRuleStore()
		return UnitRuleStore._instance

class CitySpawnCache :
	""" Utility class to spawn rebels in a revolting city. """
	def __init__( self, pCity, pRevPlayer, iRebelsHere, iRebelsIn3 = 0, iRebelsIn6 = 0 ) :
		# type: ( CyCity, CyPlayer, int, int, int ) -> None
		self._pCity = pCity
		self._pRevPlayer = pRevPlayer
		self._iRebelsHere = iRebelsHere
		self._iRebelsIn3 = iRebelsIn3
		self._iRebelsIn6 = iRebelsIn6
		self._unitsCache = {} # type: Dict[str, Sequence[Tuple[int, Sequence[int]]]]
	
	def _getRuleUnits( self, sRule ) :
		# type: ( str ) -> Sequence[UnitDesc]
		if sRule not in self._unitsCache :
			self._unitsCache[sRule] = list( UnitRuleStore.getInstance().RULES[sRule].findBest( self._pCity, self._pRevPlayer ) )
		return self._unitsCache[sRule]
	
	def _spawnUnitsByRule( self, iNumUnits, sRule, iX, iY, bOptional ) :
		# type: ( int, str, int, int, bool ) -> Iterator[CyUnit]
		if iNumUnits <= 0 :
			return
		if LOG_LEVEL >= 2 : log( "Spawning %d units with rule %s at %d|%d" % ( iNumUnits, sRule, iX, iY ) )
		units = self._getRuleUnits( sRule )
		if len( units ) > 0 :
			for idx in xrange( iNumUnits ) :
				unit = sorenRandChoice( units ) # type: UnitDesc
				yield unit.spawn( self._pCity, self._pRevPlayer, iX, iY, idx, self._iRebelsHere, self._iRebelsIn3, self._iRebelsIn6 )
		elif not bOptional :
			log( "ERROR: No units generated by %s" % sRule )
	
	def spawnUnitsByRule( self, iNumUnits, sRule, iX, iY, bOptional = False ) :
		# type: ( int, str, int, int, bool ) -> Sequence[CyUnit]
		""" Spawn units, apply promotions, and set UnitAI. """
		return list( self._spawnUnitsByRule( iNumUnits, sRule, iX, iY, bOptional ) )
