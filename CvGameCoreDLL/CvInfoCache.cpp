// InfoCache 10/2019 lfgr

#include "CvGameCoreDLL.h"

#include "CvInfoCache.h"

#include "BetterBTSAI.h"

CvInfoCache::CvInfoCache() {
}

CvInfoCache::~CvInfoCache() {
}

void CvInfoCache::init() {
	// AI_unitValue stuff
	m_aiUnitValueFromTraitCache.init( info_ai::AI_calcUnitValueFromTrait );
	m_aiUnitValueFromFreePromotionsCache.init( info_ai::AI_calcUnitValueFromFreePromotions );
	m_aiUnitAmphibCache.init( info_ai::AI_checkUnitAmphib );

	m_abUnitUpgradeCache.init( info::upgradeAvailable );

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

bool CvInfoCache::upgradeAvailable( CivilizationTypes eCivilization, UnitTypes eFromUnit, UnitClassTypes eToUnitClass ) const {
#ifdef NO_CACHING
	return info::upgradeAvailable( eCivilization, eFromUnit, eToUnitClass );
#else
	return m_abUnitUpgradeCache.at( eCivilization, eFromUnit, eToUnitClass );
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

	// Need this for function pointer usage
	bool upgradeAvailable( CivilizationTypes eCivilization, UnitTypes eFromUnit, UnitClassTypes eToUnitClass )
	{
		return upgradeAvailable( eCivilization, eFromUnit, eToUnitClass, 0 );
	}
}
