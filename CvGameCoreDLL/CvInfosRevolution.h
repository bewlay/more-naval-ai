#pragma once

// lfgr Revolution effects 04/2023

#ifndef CV_INFOS_REVOLUTION_H
#define CV_INFOS_REVOLUTION_H

// Revolution-related city effects.
class CvRevolutionEffects
{
public :
	CvRevolutionEffects();
	virtual ~CvRevolutionEffects();

	bool is_zero() const;
	bool read( CvXMLLoadUtility* pXML );

	void operator+=( const CvRevolutionEffects& other );
	void operator-=( const CvRevolutionEffects& other );

	int getRevIdxPerTurn() const;
	int getRevIdxHolyCityOwned() const;
	int getRevIdxHolyCityHeathenOwned() const;

	int getRevIdxHappinessMod() const;
	int getRevIdxHappinessCapChange() const;
	int getRevIdxUnhappinessMod() const;

	int getRevIdxLocationMod() const;

	int getRevIdxBadReligionMod() const;
	int getRevIdxGoodReligionMod() const;

	int getRevIdxNationalityMod() const;

	int getRevIdxGarrisonMod() const;
	int getRevIdxGarrisonCapChange() const;

	int getRevIdxDisorderMod() const;

	int getRevIdxCrimeMod() const;

	int getRevIdxCultureRateMod() const;
	int getRevIdxCultureRateCapChange() const;

private :
	int m_iRevIdxPerTurn;
	int m_iRevIdxHolyCityOwned;
	int m_iRevIdxHolyCityHeathenOwned;

	int m_iRevIdxHappinessMod;
	int m_iRevIdxHappinessCapChange;
	int m_iRevIdxUnhappinessMod;

	int m_iRevIdxLocationMod;

	int m_iRevIdxBadReligionMod;
	int m_iRevIdxGoodReligionMod;

	int m_iRevIdxNationalityMod;

	int m_iRevIdxGarrisonMod;
	int m_iRevIdxGarrisonCapChange;

	int m_iRevIdxDisorderMod;

	int m_iRevIdxCrimeMod;

	int m_iRevIdxCultureRateMod;
	int m_iRevIdxCultureRateCapChange;
};

#endif // CV_INFOS_REVOLUTION_H
