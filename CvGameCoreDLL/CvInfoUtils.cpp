// InfoUtils 04/2020 lfgr

#include "CvGameCoreDLL.h"

#include "CvInfoUtils.h"

namespace info_utils {
	
	int getRealSpellCost( PlayerTypes ePlayer, SpellTypes eSpell ) {
		CvSpellInfo& kSpellInfo = GC.getSpellInfo( eSpell );
		int iCost = kSpellInfo.getCost();

		// scale costs by gamespeed
		iCost *= GC.getGameSpeedInfo( GC.getGameINLINE().getGameSpeedType() ).getTrainPercent();
		iCost /= 100;

		if (kSpellInfo.getConvertUnitType() != NO_UNIT) {
			iCost += (iCost * GET_PLAYER( ePlayer ).getUpgradeCostModifier()) / 100;
		}

		return iCost;
	}

}