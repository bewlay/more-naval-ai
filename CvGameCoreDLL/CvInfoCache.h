// InfoCache 10/2019 lfgr

#ifndef CVINFOCACHE_H_
#define CVINFOCACHE_H_

#pragma once

#include "CvInfos.h"

// enumLength function, adapted from Nightinggale's EnumMap
// enumLength(x) returns the number of entries for the (enum) type of x. Note that x is not used.
// ENUM_LENGTH(EnumType) is a macro where only the type has to be supplied
#define ENUM_LENGTH(EnumType) enumLength( (EnumType) 0)

// More to be added if necessary
inline int enumLength( CivilizationTypes x ) { return GC.getNumCivilizationInfos(); }
inline int enumLength( TraitTypes x ) { return GC.getNumTraitInfos(); }
inline int enumLength( UnitAITypes x ) { return NUM_UNITAI_TYPES; }
inline int enumLength( UnitClassTypes x ) { return GC.getNumUnitClassInfos(); }
inline int enumLength( UnitCombatTypes x ) { return GC.getNumUnitCombatInfos(); }
inline int enumLength( UnitTypes x ) { return GC.getNumUnitInfos(); }


// Utility cache classes

// Data structure mapping each KeyEnumType to some ValType
// Must call init() exactly once after construction, after that the data structure doesn't change
// Warning: does not support keys NO_XXX, i.e. -1
template<class KeyEnumType, class ValType>
class FixedEnumMap {
public :
	FixedEnumMap() :
		m_aMap( NULL )
	{}

	inline void init( ValType calcFunc(KeyEnumType) ) {
		FAssertMsg( m_aMap == NULL, "FixedEnumMap already initialized!" );
		if( m_aMap != NULL ) {
			return;
		}

		m_aMap = new ValType[ENUM_LENGTH(KeyEnumType)];
		for( int i = 0; i < ENUM_LENGTH(KeyEnumType); i++ ) {
			m_aMap[i] = calcFunc( (KeyEnumType) i );
		}
	}

	~FixedEnumMap() {
		SAFE_DELETE_ARRAY( m_aMap );
	}

	ValType at( const KeyEnumType e ) const {
		FAssert( m_aMap != NULL );
		FAssert( 0 <= e );
		FAssert( e <= ENUM_LENGTH(KeyEnumType) );
		return m_aMap[e];
	}

private :
	ValType* m_aMap;
};

// Data structure mapping each pair of KeyEnumType1, KeyEnumType2 to some ValType
// Must call init() exactly once after construction, after that the data structure doesn't change
// Warning: does not support keys NO_XXX, i.e. -1
template<class KeyEnumType1, class KeyEnumType2, class ValType>
class Fixed2DEnumMap {
public :
	Fixed2DEnumMap() :
		m_aMap( NULL )
	{}

	inline void init( ValType (*calcFunc)(KeyEnumType1, KeyEnumType2) ) {
		FAssertMsg( m_aMap == NULL, "Fixed2DEnumMap already initialized!" );
		if( m_aMap != NULL ) {
			return;
		}

		m_aMap = new ValType[ENUM_LENGTH(KeyEnumType1) * ENUM_LENGTH(KeyEnumType2)];
		for( int i = 0; i < ENUM_LENGTH(KeyEnumType1); i++ ) {
			for( int j = 0; j < ENUM_LENGTH(KeyEnumType2); j++ ) {
				m_aMap[i * ENUM_LENGTH(KeyEnumType2) + j] = calcFunc( (KeyEnumType1) i, (KeyEnumType2) j );
			}
		}
	}

	~Fixed2DEnumMap() {
		SAFE_DELETE_ARRAY( m_aMap );
	}

	ValType at( const KeyEnumType1 i, const KeyEnumType2 j ) const {
		FAssert( m_aMap != NULL );
		FAssert( 0 <= i );
		FAssert( i < ENUM_LENGTH(KeyEnumType1) );
		FAssert( 0 <= j );
		FAssert( j < ENUM_LENGTH(KeyEnumType2) );
		return m_aMap[i * ENUM_LENGTH(KeyEnumType2) + j];
	}

private :
	ValType* m_aMap;
};

// Data structure mapping each pair of KeyEnumType1, KeyEnumType2, KeyEnumType3 to some ValType
// Must call init() exactly once after construction, after that the data structure doesn't change
// Warning: does not support keys NO_XXX, i.e. -1
template<class KeyEnumType1, class KeyEnumType2, class KeyEnumType3, class ValType>
class Fixed3DEnumMap {
public :
	Fixed3DEnumMap() :
		m_aMap( NULL )
	{}

	inline void init( ValType (*calcFunc)(KeyEnumType1, KeyEnumType2, KeyEnumType3) ) {
		FAssertMsg( m_aMap == NULL, "Fixed3DEnumMap already initialized!" );
		if( m_aMap != NULL ) {
			return;
		}

		m_aMap = new ValType[ENUM_LENGTH(KeyEnumType1) * ENUM_LENGTH(KeyEnumType2) * ENUM_LENGTH(KeyEnumType3)];
		for( int i = 0; i < ENUM_LENGTH(KeyEnumType1); i++ ) {
			for( int j = 0; j < ENUM_LENGTH(KeyEnumType2); j++ ) {
				for( int k = 0; k < ENUM_LENGTH(KeyEnumType3); k++ ) {
					m_aMap[i * ENUM_LENGTH(KeyEnumType2) * ENUM_LENGTH(KeyEnumType3) + j * ENUM_LENGTH(KeyEnumType3) + k] = calcFunc( (KeyEnumType1) i, (KeyEnumType2) j, (KeyEnumType3) k );
				}
			}
		}
	}

	~Fixed3DEnumMap() {
		SAFE_DELETE_ARRAY( m_aMap );
	}

	ValType at( const KeyEnumType1 i, const KeyEnumType2 j, const KeyEnumType3 k ) const {
		FAssert( m_aMap != NULL );
		FAssert( 0 <= i );
		FAssert( i < ENUM_LENGTH(KeyEnumType1) );
		FAssert( 0 <= j );
		FAssert( j < ENUM_LENGTH(KeyEnumType2) );
		FAssert( 0 <= k );
		FAssert( k < ENUM_LENGTH(KeyEnumType3) );
		return m_aMap[i * ENUM_LENGTH(KeyEnumType2) * ENUM_LENGTH(KeyEnumType3) + j * ENUM_LENGTH(KeyEnumType3) + k];
	}

private :
	ValType* m_aMap;
};


typedef std::pair<BuildingTypes, UnitTypes> BuildingUnitPair;
typedef std::pair<BuildingClassTypes, UnitTypes> BuildingClassUnitPair;

class CvInfoCache {
public :
	CvInfoCache();
	virtual ~CvInfoCache();

	void init();
	
	int AI_getUnitValueFromTrait( UnitCombatTypes eUnitCombat, TraitTypes eTrait ) const;
	int AI_getUnitValueFromFreePromotions( UnitTypes eUnit, UnitAITypes eUnitAI ) const;
	bool AI_isUnitAmphib( UnitTypes eUnit ) const;

	bool upgradeAvailable( CivilizationTypes eCivilization, UnitTypes eFromUnit, UnitClassTypes eToUnitClass ) const;

	const std::vector<BuildingUnitPair>& getUnitsWithBuildingPrereqs() const {
		return m_vtUnitBuildingPrereqCache;
	}
	const std::vector<BuildingClassUnitPair>& getUnitsWithBuildingClassPrereqs() const{
		return m_vtUnitBuildingClassPrereqCache;
	}

private :
	Fixed2DEnumMap<UnitCombatTypes, TraitTypes, int> m_aiUnitValueFromTraitCache;
	Fixed2DEnumMap<UnitTypes, UnitAITypes, int> m_aiUnitValueFromFreePromotionsCache;
	FixedEnumMap<UnitTypes, bool> m_aiUnitAmphibCache;

	Fixed3DEnumMap<CivilizationTypes, UnitTypes, UnitClassTypes, bool> m_abUnitUpgradeCache;

	// Buildings and building classes that enable units
	std::vector<BuildingUnitPair> m_vtUnitBuildingPrereqCache;
	std::vector<BuildingClassUnitPair> m_vtUnitBuildingClassPrereqCache;
};

CvInfoCache& getInfoCache();

// AI calculations that are based solely on InfoTypes and do not depend on the game state
namespace info_ai {
	int AI_calcUnitValueFromTrait( UnitCombatTypes eUnitCombat, TraitTypes eTrait );
	int AI_calcUnitValueFromFreePromotions( UnitTypes eUnit, UnitAITypes eUnitAI );
	bool AI_checkUnitAmphib( UnitTypes eUnit );
}


// Other calculations that do not depend on game state
namespace info {
	// Whether a unit of the given type can upgrade to the given class for a player of the given civ.
	bool upgradeAvailable( CivilizationTypes eCivilization, UnitTypes eFromUnit, UnitClassTypes eToUnitClass );
}

#endif /* CVINFOCACHE_H_ */