// InfoCache 10/2019 lfgr

#include "CvGameCoreDLL.h"

#include "CvInfoCache.h"

#include <algorithm>
#include <set>

#include "BetterBTSAI.h"

// Uncomment to enable regression testing and a tweak to restore behavior of previous versions (at little cost)
//#define INFOCACHE_TESTING

CvInfoCache::CvInfoCache() {
}

CvInfoCache::~CvInfoCache() {
}

// Regression testing
void test_CvInfoCache() {
	for( int iUnit = 0; iUnit < GC.getNumUnitInfos(); iUnit++ ) {
		for( int iCiv = 0; iCiv < GC.getNumCivilizationInfos(); iCiv++ ) {
			// Get cached upgrade list
			std::vector<UnitTypes> dest;
			getInfoCache().computeAvailableUpgrades( (CivilizationTypes) iCiv, (UnitTypes) iUnit, dest );

			// Make it into a bool vector
			std::vector<bool> abUpgrades( GC.getNumUnitInfos() );
			for( size_t i = 0; i < dest.size(); i++ ) {
				abUpgrades[dest[i]] = true;
			}

			// Now check against old method
			for( int iUnitClass = 0; iUnitClass < GC.getNumUnitClassInfos(); iUnitClass++ ) {
				int iUpgradeUnit = GC.getCivilizationInfo( (CivilizationTypes) iCiv ).getCivilizationUnits( iUnitClass );
				if( iUpgradeUnit != NO_UNIT ) {
					FAssert( info::upgradeAvailable( (CivilizationTypes) iCiv, (UnitTypes) iUnit, (UnitClassTypes) iUnitClass ) == abUpgrades[iUpgradeUnit] )
				}
			}
		}
	}
	logBBAI( "CvInfoCache regression testing finished successfully" );
}

void CvInfoCache::init() {
	PROFILE_FUNC();
	// AI_unitValue stuff
	m_aiUnitValueFromTraitCache.init( info_ai::AI_calcUnitValueFromTrait );
	m_aiUnitValueFromFreePromotionsCache.init( info_ai::AI_calcUnitValueFromFreePromotions );
	m_aiUnitAmphibCache.init( info_ai::AI_checkUnitAmphib );

	// Unit prereqs
	for( int iUnit = 0; iUnit < GC.getNumUnitInfos(); iUnit++ ) {
		UnitTypes eUnit = (UnitTypes) iUnit;
		CvUnitInfo& kUnit = GC.getUnitInfo( eUnit );
		BuildingTypes ePrereqBuilding = (BuildingTypes) kUnit.getPrereqBuilding();
		BuildingClassTypes ePrereqBuildingClass = (BuildingClassTypes) kUnit.getPrereqBuildingClass();
		if( ePrereqBuilding != NO_BUILDING ) {
			m_vtUnitBuildingPrereqCache.push_back( BuildingUnitPair( ePrereqBuilding, eUnit ) );
			//logBBAI( "CACHE: %s requires %s", kUnit.getType(), GC.getBuildingInfo( ePrereqBuilding ).getType() );
		}
		if( ePrereqBuildingClass != NO_BUILDINGCLASS ) {
			m_vtUnitBuildingClassPrereqCache.push_back( BuildingClassUnitPair( ePrereqBuildingClass, eUnit ) );
			//logBBAI( "CACHE: %s requires %s", kUnit.getType(), GC.getBuildingClassInfo( ePrereqBuildingClass ).getType() );
		}
	}

	// Compute all unit upgrades as lists
	for( int iUnit = 0; iUnit < GC.getNumUnitInfos(); iUnit++ ) {
		m_aeUnitClassUpgradesByUnit.push_back( std::vector<UnitClassTypes>() );
		for( int iUnitClass = 0; iUnitClass < GC.getNumUnitClassInfos(); iUnitClass++ ) {
			if( GC.getUnitInfo( (UnitTypes) iUnit ).getUpgradeUnitClass( (UnitClassTypes) iUnitClass ) ) {
				m_aeUnitClassUpgradesByUnit.back().push_back( (UnitClassTypes) iUnitClass );
			}
		}
	}

#ifdef INFOCACHE_TESTING
	test_CvInfoCache();
#endif
}


int CvInfoCache::AI_getUnitValueFromTrait( UnitCombatTypes eUnitCombat, TraitTypes eTrait ) const {
#ifdef NO_CACHING
	return info_ai::AI_calcUnitValueFromTrait( eUnitCombat, eTrait );
#else
	return m_aiUnitValueFromTraitCache.at( eUnitCombat, eTrait );
#endif
}

int CvInfoCache::AI_getUnitValueFromFreePromotions( UnitTypes eUnit, UnitAITypes eUnitAI ) const {
#ifdef NO_CACHING
	return info_ai::AI_calcUnitValueFromFreePromotions( eUnit, eUnitAI );
#else
	return m_aiUnitValueFromFreePromotionsCache.at( eUnit, eUnitAI );
#endif
}

bool CvInfoCache::AI_isUnitAmphib( UnitTypes eUnit ) const {
#ifdef NO_CACHING
	return info_ai::AI_checkUnitAmphib( eUnit );
#else
	return m_aiUnitAmphibCache.at( eUnit );
#endif
}


// Comparison function to sort units by unitclass. Used only for compatibility with old behavior.
struct cmp_units_by_class {
	bool operator()( const UnitTypes& a, const UnitTypes& b ) {
		return GC.getUnitInfo( a ).getUnitClassType() < GC.getUnitInfo( b ).getUnitClassType();
	}
};

void CvInfoCache::computeAvailableUpgrades( CivilizationTypes eCivilization, UnitTypes eFromUnit, std::vector<UnitTypes>& result )
{
	CvCivilizationInfo& kCiv = GC.getCivilizationInfo( eCivilization );

	// lfgr: Uncomment this to revert to the original implementation
	//for( int eClass = 0; eClass < GC.getNumUnitClassInfos(); eClass++ ) {
	//	if( info::upgradeAvailable( eCivilization, eFromUnit, (UnitClassTypes) eClass ) ) {
	//		UnitTypes eUnit = (UnitTypes) GC.getCivilizationInfo( eCivilization ).getCivilizationUnits( eClass );
	//		if( eUnit != NO_UNIT ) {
	//			result.push_back( eUnit );
	//		}
	//	}
	//}

	// Find all updates via graph traversal, using cached upgrades ("edges") from precomputation
	std::vector<UnitTypes> unit_queue;
	unit_queue.push_back( eFromUnit );
	std::set<UnitTypes> found; // lfgr: Does not seem to compile with unordered_set
	while( unit_queue.size() > 0 ) {
		UnitTypes eUnit = unit_queue.back();
		unit_queue.pop_back();
		const std::vector<UnitClassTypes>& veUpgrades = m_aeUnitClassUpgradesByUnit[eUnit];
		for( size_t i = 0; i < veUpgrades.size(); i++ ) {
			UnitTypes eUpgradeUnit = (UnitTypes) kCiv.getCivilizationUnits( veUpgrades[i] );
			if( eUpgradeUnit != NO_UNIT && found.find( eUpgradeUnit ) == found.end() ) {
				result.push_back( eUpgradeUnit );
				found.insert( eUpgradeUnit );
				unit_queue.push_back( eUpgradeUnit );
			}
		}
	}

#ifdef INFOCACHE_TESTING
	std::sort( result.begin(), result.end(), cmp_units_by_class() );
#endif
}



// Static instance
CvInfoCache instance;

CvInfoCache& getInfoCache() {
	return instance;
}

// AI calculations that are based solely on InfoTypes and do not depend on the game state
namespace info_ai {
	int AI_calcUnitValueFromTrait( UnitCombatTypes eUnitCombat, TraitTypes eTrait ) {
		int iTraitMod = 0;
		for (int iK = 0; iK < GC.getNumPromotionInfos(); iK++)
		{
			if (GC.getTraitInfo(eTrait).isFreePromotion(iK))
			{
				if( GC.getTraitInfo( eTrait ).isAllUnitsFreePromotion() ||
						GC.getTraitInfo(eTrait ).isFreePromotionUnitCombat(eUnitCombat ) )
				{
					iTraitMod += 10;
				}
			}
		}

		return iTraitMod;
	}

	int AI_calcUnitValueFromFreePromotions(UnitTypes eUnit, UnitAITypes eUnitAI) {
		CvUnitInfo& kUnitInfo = GC.getUnitInfo( eUnit );

		int iPromotionMod = 0;
		for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
		{
			if (kUnitInfo.getFreePromotions(iI))
			{
				CvPromotionInfo& kPromotionInfo = GC.getPromotionInfo((PromotionTypes)iI);

				if (eUnitAI == UNITAI_CITY_DEFENSE || eUnitAI == UNITAI_CITY_COUNTER || eUnitAI == UNITAI_COUNTER)
				{
					iPromotionMod += (kPromotionInfo.getBetterDefenderThanPercent() / 5);
					if (kPromotionInfo.isTargetWeakestUnitCounter())
					{
						iPromotionMod += 20;
					}
					iPromotionMod += kPromotionInfo.getFriendlyHealChange();
				}

				if (eUnitAI == UNITAI_ATTACK || eUnitAI == UNITAI_ATTACK_CITY || eUnitAI == UNITAI_COUNTER)
				{
					iPromotionMod += kPromotionInfo.getEnemyHealChange();
					iPromotionMod += kPromotionInfo.getNeutralHealChange();
					iPromotionMod += kPromotionInfo.getCombatPercent();
					if (kPromotionInfo.isBlitz() || kPromotionInfo.isWaterWalking() || kPromotionInfo.isTargetWeakestUnit())
					{
						iPromotionMod += (kUnitInfo.getMoves() * 10);
					}
				}
			}
		}

		return iPromotionMod;
	}

	bool AI_checkUnitAmphib( UnitTypes eUnit ) {
		int iPromotionMod = 0;
		for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
		{
			if( GC.getUnitInfo( eUnit ).getFreePromotions(iI))
			{
				if( GC.getPromotionInfo((PromotionTypes)iI).isAmphib() ) {
					return true;
				}
			}
		}
		return false;
	}
}

// Other calculations that do not depend on game state
namespace info {
	// Whether a unit of the given type can upgrade to the given class for a player of the given civ.
	// Old implementation, replaced with CvInfoCache::computeAvailableUpgrades in most places, and also used for regression testing
	// Mostly copied from CvUnit::upgradeAvailable
	bool upgradeAvailable( CivilizationTypes eCivilization, UnitTypes eFromUnit, UnitClassTypes eToUnitClass, int iCount )
	{
		UnitTypes eLoopUnit;
		int iI;
		int numUnitClassInfos = GC.getNumUnitClassInfos();

		if (iCount > numUnitClassInfos)
		{
			return false;
		}

		CvUnitInfo &fromUnitInfo = GC.getUnitInfo(eFromUnit);

		if (fromUnitInfo.getUpgradeUnitClass(eToUnitClass))
		{
			return true;
		}

		for (iI = 0; iI < numUnitClassInfos; iI++)
		{
			if (fromUnitInfo.getUpgradeUnitClass(iI))
			{
				eLoopUnit = ((UnitTypes)(GC.getCivilizationInfo(eCivilization).getCivilizationUnits(iI)));

				if (eLoopUnit != NO_UNIT)
				{
					if (upgradeAvailable(eCivilization, eLoopUnit, eToUnitClass, (iCount + 1)))
					{
						return true;
					}
				}
			}
		}
		return false;
	}
}
