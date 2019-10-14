// InfoCache 10/2019 lfgr

#ifndef CVINFOCACHE_H_
#define CVINFOCACHE_H_

#pragma once

#include "CvInfos.h"

class CvInfoCache {
public :
	CvInfoCache();
	virtual ~CvInfoCache();

	void init(); // TODO: Call!
	
	int AI_getUnitValueFromTrait( UnitCombatTypes eUnitCombat, TraitTypes eTrait ) const;
	int AI_getUnitValueFromFreePromotions( UnitTypes eUnit, UnitAITypes eUnitAI ) const;
	bool AI_isUnitAmphib( UnitTypes eUnit ) const;

private :
	int* m_aiUnitValueFromTraitCache;
	int* m_aiUnitValueFromFreePromotionsCache;
	int* m_aiUnitAmphibCache;
};

void initInfoCache();

CvInfoCache& getInfoCache();

// AI calculations that are based solely on InfoTypes and do not depend on the game state
namespace info_ai {
	int AI_calcUnitValueFromTrait( UnitCombatTypes eUnitCombat, TraitTypes eTrait );
	int AI_calcUnitValueFromFreePromotions( UnitTypes eUnit, UnitAITypes eUnitAI );
	bool AI_checkUnitAmphib( UnitTypes eUnit );
}

#endif /* CVINFOCACHE_H_ */