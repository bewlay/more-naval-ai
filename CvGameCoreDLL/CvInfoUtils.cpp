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

	CvWString getParametrizedVoteDescription( VoteTypes eVote,
			PlayerTypes ePlayer, int iCity, PlayerTypes eOtherPlayer ) {
		CvVoteInfo& kVote = GC.getVoteInfo( eVote );
		if( wcslen( kVote.getParamDescriptionKey() ) == 0 ) {
			return kVote.getDescription();
		}

		CvWString szPlayerName;
		if( ePlayer != NO_PLAYER ) {
			szPlayerName = GET_PLAYER( ePlayer ).getNameKey();
		}

		CvWString szCityName;
		if( ePlayer != NO_PLAYER && iCity != -1 ) {
			szCityName = GET_PLAYER( ePlayer ).getCity( iCity )->getNameKey();
		}

		CvWString szOtherPlayerName;
		if( eOtherPlayer != NO_PLAYER ) {
			szOtherPlayerName = GET_PLAYER( eOtherPlayer ).getNameKey();
		}

		return gDLL->getText( kVote.getParamDescriptionKey(),
				szPlayerName.c_str(), szCityName.c_str(), szOtherPlayerName.c_str() );
	}

	void setParametrizedVoteDescription( VoteSelectionSubData& kData ) {
		kData.szText = getParametrizedVoteDescription( kData.eVote,
				kData.ePlayer, kData.iCityId, kData.eOtherPlayer );
	}
}