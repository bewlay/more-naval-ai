#include "CvGameCoreDLL.h"

#include "CvInfosRevolution.h"

#include "CvXMLLoadUtility.h"


CvRevolutionEffects::CvRevolutionEffects() :
	m_iRevIdxPerTurn( 0 ),
	m_iRevIdxHolyCityOwned( 0 ),
	m_iRevIdxHolyCityHeathenOwned( 0 ),
	m_iRevIdxHappinessMod( 0 ),
	m_iRevIdxHappinessCapChange( 0 ),
	m_iRevIdxUnhappinessMod( 0 ),
	m_iRevIdxLocationMod( 0 ),
	m_iRevIdxBadReligionMod( 0 ),
	m_iRevIdxGoodReligionMod( 0 ),
	m_iRevIdxNationalityMod( 0 ),
	m_iRevIdxGarrisonMod( 0 ),
	m_iRevIdxGarrisonCapChange( 0 ),
	m_iRevIdxDisorderMod( 0 ),
	m_iRevIdxCrimeMod( 0 ),
	m_iRevIdxCultureRateMod( 0 ),
	m_iRevIdxCultureRateCapChange( 0 )
{}

CvRevolutionEffects::~CvRevolutionEffects() {}

bool CvRevolutionEffects::is_zero() const {
	if( m_iRevIdxPerTurn != 0 ) {
		return false;
	}
	if( m_iRevIdxHolyCityOwned != 0 ) {
		return false;
	}
	if( m_iRevIdxHolyCityHeathenOwned != 0 ) {
		return false;
	}
	if( m_iRevIdxHappinessMod != 0 ) {
		return false;
	}
	if( m_iRevIdxHappinessCapChange != 0 ) {
		return false;
	}
	if( m_iRevIdxUnhappinessMod != 0 ) {
		return false;
	}
	if( m_iRevIdxLocationMod != 0 ) {
		return false;
	}
	if( m_iRevIdxBadReligionMod != 0 ) {
		return false;
	}
	if( m_iRevIdxGoodReligionMod != 0 ) {
		return false;
	}
	if( m_iRevIdxNationalityMod != 0 ) {
		return false;
	}
	if( m_iRevIdxGarrisonMod != 0 ) {
		return false;
	}
	if( m_iRevIdxGarrisonCapChange != 0 ) {
		return false;
	}
	if( m_iRevIdxDisorderMod != 0 ) {
		return false;
	}
	if( m_iRevIdxCrimeMod != 0 ) {
		return false;
	}
	if( m_iRevIdxCultureRateMod != 0 ) {
		return false;
	}
	if( m_iRevIdxCultureRateCapChange != 0 ) {
		return false;
	}

	return true;
}


bool CvRevolutionEffects::read( CvXMLLoadUtility* pXML ) {
	// Skip any comments and stop at the next value we might want
	if (!pXML->SkipToNextVal()) {
		return false;
	}

	pXML->MapChildren(); // try to hash children for fast lookup by name

	pXML->GetChildXmlValByName( &m_iRevIdxPerTurn, "iRevIdxPerTurn" );
	pXML->GetChildXmlValByName( &m_iRevIdxHolyCityOwned, "iRevIdxHolyCityOwned" );
	pXML->GetChildXmlValByName( &m_iRevIdxHolyCityHeathenOwned, "iRevIdxHolyCityHeathenOwned" );
	pXML->GetChildXmlValByName( &m_iRevIdxHappinessMod, "iRevIdxHappinessMod" );
	pXML->GetChildXmlValByName( &m_iRevIdxHappinessCapChange, "iRevIdxHappinessCapChange" );
	pXML->GetChildXmlValByName( &m_iRevIdxUnhappinessMod, "iRevIdxUnhappinessMod" );
	pXML->GetChildXmlValByName( &m_iRevIdxLocationMod, "iRevIdxLocationMod" );
	pXML->GetChildXmlValByName( &m_iRevIdxBadReligionMod, "iRevIdxBadReligionMod" );
	pXML->GetChildXmlValByName( &m_iRevIdxGoodReligionMod, "iRevIdxGoodReligionMod" );
	pXML->GetChildXmlValByName( &m_iRevIdxNationalityMod, "iRevIdxNationalityMod" );
	pXML->GetChildXmlValByName( &m_iRevIdxGarrisonMod, "iRevIdxGarrisonMod" );
	pXML->GetChildXmlValByName( &m_iRevIdxGarrisonCapChange, "iRevIdxGarrisonCapChange" );
	pXML->GetChildXmlValByName( &m_iRevIdxDisorderMod, "iRevIdxDisorderMod" );
	pXML->GetChildXmlValByName( &m_iRevIdxCrimeMod, "iRevIdxCrimeMod" );
	pXML->GetChildXmlValByName( &m_iRevIdxCultureRateMod, "iRevIdxCultureRateMod" );
	pXML->GetChildXmlValByName( &m_iRevIdxCultureRateCapChange, "iRevIdxCultureRateCapChange" );

	return true;
}

void CvRevolutionEffects::operator+=( const CvRevolutionEffects& other ) {
	this->m_iRevIdxPerTurn += other.m_iRevIdxPerTurn;
	this->m_iRevIdxHolyCityOwned += other.m_iRevIdxHolyCityOwned;
	this->m_iRevIdxHolyCityHeathenOwned += other.m_iRevIdxHolyCityHeathenOwned;
	this->m_iRevIdxHappinessMod += other.m_iRevIdxHappinessMod;
	this->m_iRevIdxHappinessCapChange += other.m_iRevIdxHappinessCapChange;
	this->m_iRevIdxUnhappinessMod += other.m_iRevIdxUnhappinessMod;
	this->m_iRevIdxLocationMod += other.m_iRevIdxLocationMod;
	this->m_iRevIdxBadReligionMod += other.m_iRevIdxBadReligionMod;
	this->m_iRevIdxGoodReligionMod += other.m_iRevIdxGoodReligionMod;
	this->m_iRevIdxNationalityMod += other.m_iRevIdxNationalityMod;
	this->m_iRevIdxGarrisonMod += other.m_iRevIdxGarrisonMod;
	this->m_iRevIdxGarrisonCapChange += other.m_iRevIdxGarrisonCapChange;
	this->m_iRevIdxDisorderMod += other.m_iRevIdxDisorderMod;
	this->m_iRevIdxCrimeMod += other.m_iRevIdxCrimeMod;
	this->m_iRevIdxCultureRateMod += other.m_iRevIdxCultureRateMod;
	this->m_iRevIdxCultureRateCapChange += other.m_iRevIdxCultureRateCapChange;

}


void CvRevolutionEffects::operator-=( const CvRevolutionEffects& other ) {
	this->m_iRevIdxPerTurn -= other.m_iRevIdxPerTurn;
	this->m_iRevIdxHolyCityOwned -= other.m_iRevIdxHolyCityOwned;
	this->m_iRevIdxHolyCityHeathenOwned -= other.m_iRevIdxHolyCityHeathenOwned;
	this->m_iRevIdxHappinessMod -= other.m_iRevIdxHappinessMod;
	this->m_iRevIdxHappinessCapChange -= other.m_iRevIdxHappinessCapChange;
	this->m_iRevIdxUnhappinessMod -= other.m_iRevIdxUnhappinessMod;
	this->m_iRevIdxLocationMod -= other.m_iRevIdxLocationMod;
	this->m_iRevIdxBadReligionMod -= other.m_iRevIdxBadReligionMod;
	this->m_iRevIdxGoodReligionMod -= other.m_iRevIdxGoodReligionMod;
	this->m_iRevIdxNationalityMod -= other.m_iRevIdxNationalityMod;
	this->m_iRevIdxGarrisonMod -= other.m_iRevIdxGarrisonMod;
	this->m_iRevIdxGarrisonCapChange -= other.m_iRevIdxGarrisonCapChange;
	this->m_iRevIdxDisorderMod -= other.m_iRevIdxDisorderMod;
	this->m_iRevIdxCrimeMod -= other.m_iRevIdxCrimeMod;
	this->m_iRevIdxCultureRateMod -= other.m_iRevIdxCultureRateMod;
	this->m_iRevIdxCultureRateCapChange -= other.m_iRevIdxCultureRateCapChange;

}


int CvRevolutionEffects::getRevIdxPerTurn() const {
	return m_iRevIdxPerTurn;
}

int CvRevolutionEffects::getRevIdxHolyCityOwned() const {
	return m_iRevIdxHolyCityOwned;
}

int CvRevolutionEffects::getRevIdxHolyCityHeathenOwned() const {
	return m_iRevIdxHolyCityHeathenOwned;
}

int CvRevolutionEffects::getRevIdxHappinessMod() const {
	return m_iRevIdxHappinessMod;
}

int CvRevolutionEffects::getRevIdxHappinessCapChange() const {
	return m_iRevIdxHappinessCapChange;
}

int CvRevolutionEffects::getRevIdxUnhappinessMod() const {
	return m_iRevIdxUnhappinessMod;
}

int CvRevolutionEffects::getRevIdxLocationMod() const {
	return m_iRevIdxLocationMod;
}

int CvRevolutionEffects::getRevIdxBadReligionMod() const {
	return m_iRevIdxBadReligionMod;
}

int CvRevolutionEffects::getRevIdxGoodReligionMod() const {
	return m_iRevIdxGoodReligionMod;
}

int CvRevolutionEffects::getRevIdxNationalityMod() const {
	return m_iRevIdxNationalityMod;
}

int CvRevolutionEffects::getRevIdxGarrisonMod() const {
	return m_iRevIdxGarrisonMod;
}

int CvRevolutionEffects::getRevIdxGarrisonCapChange() const {
	return m_iRevIdxGarrisonCapChange;
}

int CvRevolutionEffects::getRevIdxDisorderMod() const {
	return m_iRevIdxDisorderMod;
}

int CvRevolutionEffects::getRevIdxCrimeMod() const {
	return m_iRevIdxCrimeMod;
}

int CvRevolutionEffects::getRevIdxCultureRateMod() const {
	return m_iRevIdxCultureRateMod;
}

int CvRevolutionEffects::getRevIdxCultureRateCapChange() const {
	return m_iRevIdxCultureRateCapChange;
}