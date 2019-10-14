// InfoCache 10/2019 lfgr

#include "CvGameCoreDLL.h"

#include "CvInfoCache.h"

CvInfoCache::CvInfoCache() :
		m_aiUnitValueFromTraitCache( NULL ),
		m_aiUnitValueFromFreePromotionsCache( NULL ),
		m_aiUnitAmphibCache( NULL )
{}

CvInfoCache::~CvInfoCache() {
	SAFE_DELETE_ARRAY( m_aiUnitValueFromTraitCache );
	SAFE_DELETE_ARRAY( m_aiUnitValueFromFreePromotionsCache );
	SAFE_DELETE_ARRAY( m_aiUnitAmphibCache );
}

void CvInfoCache::init() {
	FAssertMsg( m_aiUnitValueFromTraitCache == NULL, "CvInfoCache already initialized!" );
	if( m_aiUnitValueFromTraitCache != NULL ) {
		return;
	}

	// TODO: Use something like Nightingale's template info arrays here

	m_aiUnitValueFromTraitCache = new int[GC.getNumUnitCombatInfos() * GC.getNumTraitInfos()];
	for( int eUnitCombat = 0; eUnitCombat < GC.getNumUnitCombatInfos(); eUnitCombat++ ) {
		for( int eTrait = 0; eTrait < GC.getNumTraitInfos(); eTrait++ ) {
			m_aiUnitValueFromTraitCache[eUnitCombat * GC.getNumTraitInfos() + eTrait] \
				= info_ai::AI_calcUnitValueFromTrait( (UnitCombatTypes) eUnitCombat, (TraitTypes) eTrait );
		}
	}

	m_aiUnitValueFromFreePromotionsCache = new int[GC.getNumUnitInfos() * NUM_UNITAI_TYPES];
	for( int eUnit = 0; eUnit < GC.getNumUnitInfos(); eUnit++ ) {
		for( int eUnitAI = 0; eUnitAI < NUM_UNITAI_TYPES; eUnitAI++ ) {
			m_aiUnitValueFromFreePromotionsCache[eUnit * NUM_UNITAI_TYPES + eUnitAI] \
				= info_ai::AI_calcUnitValueFromFreePromotions( (UnitTypes) eUnit, (UnitAITypes) eUnitAI );
		}
	}

	m_aiUnitAmphibCache = new int[GC.getNumUnitInfos()];
	for( int eUnit = 0; eUnit < GC.getNumUnitInfos(); eUnit++ ) {
		m_aiUnitAmphibCache[eUnit] = false;
	}
}


int CvInfoCache::AI_getUnitValueFromTrait( UnitCombatTypes eUnitCombat, TraitTypes eTrait ) const {
#ifdef NO_CACHING
	return info_ai::AI_calcUnitValueFromTrait( eUnitCombat, eTrait );
#else
	return m_aiUnitValueFromTraitCache[eUnitCombat * GC.getNumTraitInfos() + eTrait];
#endif
}

int CvInfoCache::AI_getUnitValueFromFreePromotions( UnitTypes eUnit, UnitAITypes eUnitAI ) const {
#ifdef NO_CACHING
	return info_ai::AI_calcUnitValueFromFreePromotions( eUnit, eUnitAI );
#else
	return m_aiUnitValueFromFreePromotionsCache[eUnit * NUM_UNITAI_TYPES + eUnitAI];
#endif
}

bool CvInfoCache::AI_isUnitAmphib( UnitTypes eUnit ) const {
#ifdef NO_CACHING
	return info_ai::AI_checkUnitAmphib; // TODO
#else
	return m_aiUnitAmphibCache[eUnit];
#endif
}



// Static instance
CvInfoCache instance;

void initInfoCache() {
	instance.init();
}

CvInfoCache& getInfoCache() {
	return instance;
}

// AI calculations that are based solely on InfoTypes and do not depend on the game state
namespace info_ai {
	int AI_calcUnitValueFromTrait( UnitCombatTypes eUnitCombat, TraitTypes eTrait ) {
		if( eUnitCombat == NO_UNITCOMBAT ) {
			return 0;
		}

		int iTraitMod = 0;
		for (int iK = 0; iK < GC.getNumPromotionInfos(); iK++)
		{
			if (GC.getTraitInfo(eTrait).isFreePromotion(iK))
			{
				if (GC.getTraitInfo(eTrait).isFreePromotionUnitCombat(eUnitCombat))
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