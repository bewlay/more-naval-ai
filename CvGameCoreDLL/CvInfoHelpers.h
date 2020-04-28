// lfgr 10/2019

// Functions/classes to help in the implementation of CvInfo classes


#ifndef CVINFOHELPERS_H_
#define CVINFOHELPERS_H_

#pragma once


#include "CvGlobals.h"
#include "CvString.h"
#include "CvXMLLoadUtility.h"

class CvXMLLoadUtility;


template<class IDType>
class LazyInfoTypeStore { // Reads info type string and parses it later
public :
	LazyInfoTypeStore();
	LazyInfoTypeStore( const char* szType );

	IDType getInfoType() const;

	void read( CvXMLLoadUtility* pXML, const char* szText );
	void readPass3(); // To be called when all info types are read
private :
	CvString m_szType;
	IDType m_eType;
#ifdef FASSERT_ENABLE
	bool m_bReadPass3Complete;
#endif
};

template<class IDType>
LazyInfoTypeStore<IDType>::LazyInfoTypeStore()
	: m_eType( (IDType) -1 )
#ifdef FASSERT_ENABLE
	, m_bReadPass3Complete( false )
#endif
{}

template<class IDType>
LazyInfoTypeStore<IDType>::LazyInfoTypeStore( const char* szType )
	: m_eType( (IDType) -1 ), m_szType( szType )
#ifdef FASSERT_ENABLE
	, m_bReadPass3Complete( false )
#endif
{}

template<class IDType>
IDType LazyInfoTypeStore<IDType>::getInfoType() const {
#ifdef FASSERT_ENABLE
	FAssert( m_bReadPass3Complete );
#endif
	return m_eType;
}

template<class IDType>
void LazyInfoTypeStore<IDType>::read( CvXMLLoadUtility* pXML, const char* szText ) {
#ifdef FASSERT_ENABLE
	FAssert( !m_bReadPass3Complete );
#endif
	pXML->GetChildXmlValByName( m_szType, szText );
}

template<class IDType>
void LazyInfoTypeStore<IDType>::readPass3() {
#ifdef FASSERT_ENABLE
	FAssert( !m_bReadPass3Complete );
#endif
	if( !m_szType.empty() ) {
		// LFGR_TODO: Sanity check
		m_eType = (IDType) GC.getInfoTypeForString( m_szType.c_str() );
		m_szType.clear();
	}
#ifdef FASSERT_ENABLE
	m_bReadPass3Complete = true;
#endif
}


#endif /* CVINFOHELPERS_H_ */
