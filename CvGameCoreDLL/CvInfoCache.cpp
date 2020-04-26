// InfoCache 10/2019 lfgr

#include "CvGameCoreDLL.h"

#include "CvInfoCache.h"

#include "BetterBTSAI.h"

CvInfoCache::CvInfoCache() {
}

CvInfoCache::~CvInfoCache() {
}

void CvInfoCache::init() {
	m_aiUnitValueFromTraitCache.init( info_ai::AI_calcUnitValueFromTrait );
	m_aiUnitValueFromFreePromotionsCache.init( info_ai::AI_calcUnitValueFromFreePromotions );
	m_aiUnitAmphibCache.init( info_ai::AI_checkUnitAmphib );
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
	return info_ai::AI_checkUnitAmphib; // TODO
#else
	return m_aiUnitAmphibCache.at( eUnit );
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