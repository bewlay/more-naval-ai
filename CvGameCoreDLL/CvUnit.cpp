// unit.cpp

#include "CvGameCoreDLL.h"
#include "CvUnit.h"
#include "CvArea.h"
#include "CvPlot.h"
#include "CvCity.h"
#include "CvGlobals.h"
#include "CvGameCoreUtils.h"
#include "CvGameAI.h"
#include "CvMap.h"
#include "CvPlayerAI.h"
#include "CvRandom.h"
#include "CvTeamAI.h"
#include "CvGameCoreUtils.h"
#include "CyUnit.h"
#include "CyArgsList.h"
#include "CyPlot.h"
#include "CvDLLEntityIFaceBase.h"
#include "CvDLLInterfaceIFaceBase.h"
#include "CvDLLEngineIFaceBase.h"
#include "CvEventReporter.h"
#include "CvDLLPythonIFaceBase.h"
#include "CvDLLFAStarIFaceBase.h"
#include "CvInfos.h"
#include "FProfiler.h"
#include "CvPopupInfo.h"
#include "CvArtFileMgr.h"

#include "CvInfoCache.h" // lfgr 05/2024
#include "CvInfoUtils.h" // lfgr 04/2020

// BUG - start
#include "CvBugOptions.h"
// BUG - end

/************************************************************************************************/
/* BETTER_BTS_AI_MOD                      02/24/10                                jdog5000      */
/*                                                                                              */
/* AI logging                                                                                   */
/************************************************************************************************/
#include "BetterBTSAI.h"
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                       END                                                  */
/************************************************************************************************/

// Public Functions...


CvUnit::CvUnit()
{
	m_aiExtraDomainModifier = new int[NUM_DOMAIN_TYPES];

//FfH Damage Types: Added by Kael 08/23/2007
	m_paiBonusAffinity = NULL;
	m_paiBonusAffinityAmount = NULL;
	m_paiDamageTypeCombat = NULL;
	m_paiDamageTypeResist = NULL;
//FfH: End Add

	m_pabHasPromotion = NULL;

	m_paiTerrainDoubleMoveCount = NULL;
	m_paiFeatureDoubleMoveCount = NULL;
	m_paiExtraTerrainAttackPercent = NULL;
	m_paiExtraTerrainDefensePercent = NULL;
	m_paiExtraFeatureAttackPercent = NULL;
	m_paiExtraFeatureDefensePercent = NULL;
	m_paiExtraUnitCombatModifier = NULL;

	m_paiPromotionImmune = NULL; // XML_LISTS 07/2019 lfgr: cache CvPromotionInfo::isPromotionImmune

	CvDLLEntity::createUnitEntity(this);		// create and attach entity to unit

	reset(0, NO_UNIT, NO_PLAYER, true);
}


CvUnit::~CvUnit()
{
	if (!gDLL->GetDone() && GC.IsGraphicsInitialized())						// don't need to remove entity when the app is shutting down, or crash can occur
	{
		gDLL->getEntityIFace()->RemoveUnitFromBattle(this);
		CvDLLEntity::removeEntity();		// remove entity from engine
	}

	CvDLLEntity::destroyEntity();			// delete CvUnitEntity and detach from us

	uninit();

	SAFE_DELETE_ARRAY(m_aiExtraDomainModifier);
}

void CvUnit::reloadEntity()
{

//FfH: Added by Kael 07/05/2009 (fixes a crash when promotions are applid before the game is loaded)
	bool bSelected = IsSelected();
//FfH: End Add

	//destroy old entity
	if (!gDLL->GetDone() && GC.IsGraphicsInitialized())						// don't need to remove entity when the app is shutting down, or crash can occur
	{
		gDLL->getEntityIFace()->RemoveUnitFromBattle(this);
		CvDLLEntity::removeEntity();		// remove entity from engine
	}

	CvDLLEntity::destroyEntity();			// delete CvUnitEntity and detach from us

	//creat new one
	CvDLLEntity::createUnitEntity(this);		// create and attach entity to unit
	setupGraphical();


//FfH: Added by Kael 07/05/2009 (fixes a crash when promotions are applid before the game is loaded)
	if (bSelected)
	{
		gDLL->getInterfaceIFace()->selectUnit(this, false, false, false);
	}
//FfH: End Add

}


//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/22
//void CvUnit::init(int iID, UnitTypes eUnit, UnitAITypes eUnitAI, PlayerTypes eOwner, int iX, int iY, DirectionTypes eFacingDirection)
// lfgr 04/2014 bugfix
//void CvUnit::init(int iID, UnitTypes eUnit, UnitAITypes eUnitAI, PlayerTypes eOwner, int iX, int iY, DirectionTypes eFacingDirection, bool bPushOutExistingUnit)
void CvUnit::init(int iID, UnitTypes eUnit, UnitAITypes eUnitAI, PlayerTypes eOwner, int iX, int iY, DirectionTypes eFacingDirection, bool bPushOutExistingUnit, bool bGift)
// lfgr end
//<<<<Unofficial Bug Fix: End Modify
{
	CvWString szBuffer;
	int iUnitName;
	int iI, iJ;

	FAssert(NO_UNIT != eUnit);

	//--------------------------------
	// Init saved data
	reset(iID, eUnit, eOwner);

	if(eFacingDirection == NO_DIRECTION)
		m_eFacingDirection = DIRECTION_SOUTH;
	else
		m_eFacingDirection = eFacingDirection;

	//--------------------------------
	// Init containers

	//--------------------------------
	// Init pre-setup() data
// Denev 02/2010, lfgr 09/2019: Unofficial Bug Fix (added bPushOutExistingUnit), added bUnitCreation
	setXY(iX, iY, false, false, false, false, bPushOutExistingUnit, true);

	//--------------------------------
	// Init non-saved data
	setupGraphical();

	//--------------------------------
	// Init other game data
	plot()->updateCenterUnit();

	plot()->setFlagDirty(true);

	iUnitName = GC.getGameINLINE().getUnitCreatedCount(getUnitType());
	int iNumNames = m_pUnitInfo->getNumUnitNames();
	if (iUnitName < iNumNames)
	{
		int iOffset = GC.getGameINLINE().getSorenRandNum(iNumNames, "Unit name selection");

		for (iI = 0; iI < iNumNames; iI++)
		{
			int iIndex = (iI + iOffset) % iNumNames;
			CvWString szName = gDLL->getText(m_pUnitInfo->getUnitNames(iIndex));
			if (!GC.getGameINLINE().isGreatPersonBorn(szName))
			{
				setName(szName);
				GC.getGameINLINE().addGreatPersonBornName(szName);
				break;
			}
		}
	}

	setGameTurnCreated(GC.getGameINLINE().getGameTurn());

	if (m_pUnitInfo->isCanMoveImpassable())
	{
		changeCanMoveImpassable(1);
	}

	if (m_pUnitInfo->isCanMoveLimitedBorders())
	{
		changeCanMoveLimitedBorders(1);
	}

	GC.getGameINLINE().incrementUnitCreatedCount(getUnitType());

	GC.getGameINLINE().incrementUnitClassCreatedCount((UnitClassTypes)(m_pUnitInfo->getUnitClassType()));
	GET_TEAM(getTeam()).changeUnitClassCount(((UnitClassTypes)(m_pUnitInfo->getUnitClassType())), 1);
	GET_PLAYER(getOwnerINLINE()).changeUnitClassCount(((UnitClassTypes)(m_pUnitInfo->getUnitClassType())), 1);

	GET_PLAYER(getOwnerINLINE()).changeExtraUnitCost(m_pUnitInfo->getExtraCost());

	if (m_pUnitInfo->getNukeRange() != -1)
	{
		GET_PLAYER(getOwnerINLINE()).changeNumNukeUnits(1);
	}

	if (m_pUnitInfo->isMilitarySupport())
	{
		GET_PLAYER(getOwnerINLINE()).changeNumMilitaryUnits(1);
	}

	GET_PLAYER(getOwnerINLINE()).changeAssets(m_pUnitInfo->getAssetValue());

	//GET_PLAYER(getOwnerINLINE()).changePower(m_pUnitInfo->getPowerValue());
	GET_PLAYER(getOwnerINLINE()).changePower(getTruePower()); // MNAI - True Power calculations

	for (iI = 0; iI < GC.getNumPromotionInfos(); iI++)
	{
		if (m_pUnitInfo->getFreePromotions(iI))
		{
			setHasPromotion(((PromotionTypes)iI), true);
		}
	}

	FAssertMsg((GC.getNumTraitInfos() > 0), "GC.getNumTraitInfos() is less than or equal to zero but is expected to be larger than zero in CvUnit::init");
	for (iI = 0; iI < GC.getNumTraitInfos(); iI++)
	{
		if (GET_PLAYER(getOwnerINLINE()).hasTrait((TraitTypes)iI))
		{
			for (iJ = 0; iJ < GC.getNumPromotionInfos(); iJ++)
			{
				if (GC.getTraitInfo((TraitTypes) iI).isFreePromotion(iJ))
				{
					if ( GC.getTraitInfo((TraitTypes) iI).isAllUnitsFreePromotion() ||
						((getUnitCombatType() != NO_UNITCOMBAT) && GC.getTraitInfo((TraitTypes) iI).isFreePromotionUnitCombat(getUnitCombatType())))
					{
						setHasPromotion(((PromotionTypes)iJ), true);
					}
				}
			}
		}
	}

	if (NO_UNITCOMBAT != getUnitCombatType())
	{
		for (iJ = 0; iJ < GC.getNumPromotionInfos(); iJ++)
		{
			if (GET_PLAYER(getOwnerINLINE()).isFreePromotion(getUnitCombatType(), (PromotionTypes)iJ))
			{
				setHasPromotion(((PromotionTypes)iJ), true);
			}
		}
	}

	if (NO_UNITCLASS != getUnitClassType())
	{
		for (iJ = 0; iJ < GC.getNumPromotionInfos(); iJ++)
		{
			if (GET_PLAYER(getOwnerINLINE()).isFreePromotion(getUnitClassType(), (PromotionTypes)iJ))
			{
				setHasPromotion(((PromotionTypes)iJ), true);
			}
		}
	}

	if (getDomainType() == DOMAIN_LAND)
	{
		if (baseCombatStr() > 0)
		{
			if ((GC.getGameINLINE().getBestLandUnit() == NO_UNIT) || (baseCombatStr() > GC.getGameINLINE().getBestLandUnitCombat()))
			{
				GC.getGameINLINE().setBestLandUnit(getUnitType());
			}
		}
	}

	if (getOwnerINLINE() == GC.getGameINLINE().getActivePlayer())
	{
		gDLL->getInterfaceIFace()->setDirty(GameData_DIRTY_BIT, true);
	}

	if (isWorldUnitClass((UnitClassTypes)(m_pUnitInfo->getUnitClassType()))

//FfH: Added by Kael 11/05/2007
      && GC.getGameINLINE().getUnitClassCreatedCount((UnitClassTypes)(m_pUnitInfo->getUnitClassType())) == 1
//FfH: End Add

	)
	{
		for (iI = 0; iI < MAX_PLAYERS; iI++)
		{
			if (GET_PLAYER((PlayerTypes)iI).isAlive())
			{
				if (GET_TEAM(getTeam()).isHasMet(GET_PLAYER((PlayerTypes)iI).getTeam()))
				{
					szBuffer = gDLL->getText("TXT_KEY_MISC_SOMEONE_CREATED_UNIT", GET_PLAYER(getOwnerINLINE()).getNameKey(), getNameKey());
					gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)iI), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_WONDER_UNIT_BUILD", MESSAGE_TYPE_MAJOR_EVENT, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_UNIT_TEXT"), getX_INLINE(), getY_INLINE(), true, true);
				}
				else
				{
					szBuffer = gDLL->getText("TXT_KEY_MISC_UNKNOWN_CREATED_UNIT", getNameKey());
					gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)iI), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_WONDER_UNIT_BUILD", MESSAGE_TYPE_MAJOR_EVENT, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_UNIT_TEXT"));
				}
			}
		}

		szBuffer = gDLL->getText("TXT_KEY_MISC_SOMEONE_CREATED_UNIT", GET_PLAYER(getOwnerINLINE()).getNameKey(), getNameKey());
		GC.getGameINLINE().addReplayMessage(REPLAY_MESSAGE_MAJOR_EVENT, getOwnerINLINE(), szBuffer, getX_INLINE(), getY_INLINE(), (ColorTypes)GC.getInfoTypeForString("COLOR_UNIT_TEXT"));
	}

	AI_init(eUnitAI);

//FfH Units: Added by Kael 04/18/2008
// lfgr 04/2014 bugfix
//	if (m_pUnitInfo->getFreePromotionPick() > 0)
	if ( !bGift && m_pUnitInfo->getFreePromotionPick() > 0)
// lfgr end
	{
	    changeFreePromotionPick(m_pUnitInfo->getFreePromotionPick());
        setPromotionReady(true);
    }
    GC.getGameINLINE().changeGlobalCounter(m_pUnitInfo->getModifyGlobalCounter());
	m_iReligion = m_pUnitInfo->getReligionType();
    for (iI = 0; iI < GC.getNumBonusInfos(); iI++)
    {
        changeBonusAffinity((BonusTypes)iI, m_pUnitInfo->getBonusAffinity((BonusTypes)iI));
    }

    if (m_pUnitInfo->isMechUnit())
    {
        changeAlive(1);
    }
    if (GC.getCivilizationInfo(getCivilizationType()).getDefaultRace() != NO_PROMOTION)
    {
        if (getRace() == NO_PROMOTION)
        {
            if (!::isWorldUnitClass(getUnitClassType()) && !isAnimal() && isAlive() && getDomainType() == DOMAIN_LAND)
            {
                setHasPromotion((PromotionTypes)GC.getCivilizationInfo(getCivilizationType()).getDefaultRace(), true);
            }
        }
    }

	updateTerraformer(); // lfgr 05/2022
//FfH: End Add

	CvEventReporter::getInstance().unitCreated(this);
}


void CvUnit::uninit()
{

//FfH Damage Types: Added by Kael 08/23/2007
	SAFE_DELETE_ARRAY(m_paiBonusAffinity);
	SAFE_DELETE_ARRAY(m_paiBonusAffinityAmount);
	SAFE_DELETE_ARRAY(m_paiDamageTypeCombat);
	SAFE_DELETE_ARRAY(m_paiDamageTypeResist);
//FfH: End Add

	SAFE_DELETE_ARRAY(m_pabHasPromotion);

	SAFE_DELETE_ARRAY(m_paiTerrainDoubleMoveCount);
	SAFE_DELETE_ARRAY(m_paiFeatureDoubleMoveCount);
	SAFE_DELETE_ARRAY(m_paiExtraTerrainAttackPercent);
	SAFE_DELETE_ARRAY(m_paiExtraTerrainDefensePercent);
	SAFE_DELETE_ARRAY(m_paiExtraFeatureAttackPercent);
	SAFE_DELETE_ARRAY(m_paiExtraFeatureDefensePercent);
	SAFE_DELETE_ARRAY(m_paiExtraUnitCombatModifier);

	SAFE_DELETE_ARRAY(m_paiPromotionImmune);// XML_LISTS 07/2019 lfgr: cache CvPromotionInfo::isPromotionImmune
}


// FUNCTION: reset()
// Initializes data members that are serialized.
void CvUnit::reset(int iID, UnitTypes eUnit, PlayerTypes eOwner, bool bConstructorCall)
{
	int iI;

	//--------------------------------
	// Uninit class
	uninit();

	m_iID = iID;
	m_iGroupID = FFreeList::INVALID_INDEX;
	m_iHotKeyNumber = -1;
	m_iX = INVALID_PLOT_COORD;
	m_iY = INVALID_PLOT_COORD;
	m_iLastMoveTurn = 0;
	m_iReconX = INVALID_PLOT_COORD;
	m_iReconY = INVALID_PLOT_COORD;
	m_iGameTurnCreated = 0;
	m_iDamage = 0;
	m_iMoves = 0;
	m_iExperience = 0;
	m_iLevel = 1;
	m_iCargo = 0;
	m_iAttackPlotX = INVALID_PLOT_COORD;
	m_iAttackPlotY = INVALID_PLOT_COORD;
	m_iCombatTimer = 0;
	m_iCombatFirstStrikes = 0;
	m_iFortifyTurns = 0;
	m_iBlitzCount = 0;
	m_iAmphibCount = 0;
	m_iRiverCount = 0;
	m_iEnemyRouteCount = 0;
	m_iAlwaysHealCount = 0;
	m_iHillsDoubleMoveCount = 0;
	m_iImmuneToFirstStrikesCount = 0;
	m_iExtraVisibilityRange = 0;
	m_iExtraMoves = 0;
	m_iExtraMoveDiscount = 0;
	m_iExtraAirRange = 0;
	m_iExtraIntercept = 0;
	m_iExtraEvasion = 0;
	m_iExtraFirstStrikes = 0;
	m_iExtraChanceFirstStrikes = 0;
	m_iExtraWithdrawal = 0;
	m_iExtraCollateralDamage = 0;
	m_iExtraBombardRate = 0;
	m_iExtraEnemyHeal = 0;
	m_iExtraNeutralHeal = 0;
	m_iExtraFriendlyHeal = 0;
	m_iSameTileHeal = 0;
	m_iAdjacentTileHeal = 0;
	m_iExtraCombatPercent = 0;
	m_iExtraCityAttackPercent = 0;
	m_iExtraCityDefensePercent = 0;
	m_iExtraHillsAttackPercent = 0;
	m_iExtraHillsDefensePercent = 0;
	m_iRevoltProtection = 0;
	m_iCollateralDamageProtection = 0;
	m_iPillageChange = 0;
	m_iUpgradeDiscount = 0;
	m_iExperiencePercent = 0;
	m_iKamikazePercent = 0;
	m_eFacingDirection = DIRECTION_SOUTH;
	m_iImmobileTimer = 0;

	m_bMadeAttack = false;
	m_bMadeInterception = false;
	m_bPromotionReady = false;
	m_bDeathDelay = false;
	m_bCombatFocus = false;
	m_bInfoBarDirty = false;
	m_bBlockading = false;
	m_bAirCombat = false;

	m_eOwner = eOwner;
	m_eCapturingPlayer = NO_PLAYER;
	m_eUnitType = eUnit;
	m_pUnitInfo = (NO_UNIT != m_eUnitType) ? &GC.getUnitInfo(m_eUnitType) : NULL;
	m_iBaseCombat = (NO_UNIT != m_eUnitType) ? m_pUnitInfo->getCombat() : 0;
	m_eLeaderUnitType = NO_UNIT;
	m_iCargoCapacity = (NO_UNIT != m_eUnitType) ? m_pUnitInfo->getCargoSpace() : 0;
/************************************************************************************************/
/* Afforess	                  Start		 07/29/10                                               */
/* Advanced Diplomacy                                                                           */
/************************************************************************************************/
	m_eOriginalOwner = eOwner;
/************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/************************************************************************************************/

//FfH Spell System: Added by Kael 07/23/2007
	m_bFleeWithdrawl = false;
	m_bHasCasted = false;
	m_bIgnoreHide = false;
	m_bTerraformer = false;
	m_iAlive = 0;
	m_iAIControl = 0;
	m_iBoarding = 0;
	m_iDefensiveStrikeChance = (NO_UNIT != m_eUnitType) ? m_pUnitInfo->getDefensiveStrikeChance() : 0;
	m_iDefensiveStrikeDamage = (NO_UNIT != m_eUnitType) ? m_pUnitInfo->getDefensiveStrikeDamage() : 0;
	m_iDoubleFortifyBonus = 0;
	m_iFear = 0;
	m_iFlying = 0;
	m_iHeld = 0;
	m_iHiddenNationality = (NO_UNIT != m_eUnitType) ? m_pUnitInfo->isHiddenNationality() : 0;
	m_iIgnoreBuildingDefense = (NO_UNIT != m_eUnitType) ? m_pUnitInfo->isIgnoreBuildingDefense() : 0;
	m_iImmortal = (NO_UNIT != m_eUnitType) ? m_pUnitInfo->isImmortal() : 0;
	m_iImmuneToCapture = 0;
	m_iImmuneToDefensiveStrike = (NO_UNIT != m_eUnitType) ? m_pUnitInfo->isImmuneToDefensiveStrike() : 0;
	m_iImmuneToFear = 0;
	m_iImmuneToMagic = 0;
	m_iInvisible = 0;
	m_iOnlyDefensive = 0;
	m_iSeeInvisible = 0;
	m_iTargetWeakestUnit = 0;
	m_iTargetWeakestUnitCounter = 0;
	m_iTwincast = 0;
	m_iWaterWalking = 0;
	m_iBaseCombatDefense = (NO_UNIT != m_eUnitType) ? m_pUnitInfo->getCombatDefense() : 0;
	m_iBetterDefenderThanPercent = 100;
	m_iCombatHealPercent = 0;
	m_iCombatLimit = (NO_UNIT != m_eUnitType) ? m_pUnitInfo->getCombatLimit() : 0;
	m_iCombatPercentInBorders = 0;
	m_iCombatPercentGlobalCounter = 0;
	m_iDelayedSpell = NO_SPELL;
	m_iDuration = 0;
	m_iFreePromotionPick = 0;
	m_iGoldFromCombat = (NO_UNIT != m_eUnitType) ? m_pUnitInfo->getGoldFromCombat() : 0;
	m_iGroupSize = (NO_UNIT != m_eUnitType) ? m_pUnitInfo->getGroupSize() : 0;
//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/24
//	m_iInvisibleType = (NO_UNIT != m_eUnitType) ? m_pUnitInfo->getInvisibleType() : 0;
	m_iInvisibleType = (NO_UNIT != m_eUnitType) ? m_pUnitInfo->getInvisibleType() : NO_INVISIBLE;
//<<<<Unofficial Bug Fix: End Add
	m_iRace = NO_PROMOTION;
    m_iReligion = NO_RELIGION;
	m_iResist = 0;
	m_iResistModify = 0;
	m_iScenarioCounter = -1;
	m_iSpellCasterXP = 0;
	m_iSpellDamageModify = 0;
	m_iSummoner = -1;
	m_iTotalDamageTypeCombat = 0;
    m_iUnitArtStyleType = NO_UNIT_ARTSTYLE;
	m_iWorkRateModify = 0;

	m_iCanMoveImpassable = 0;
	m_iCanMoveLimitedBorders = 0;
	m_iCastingBlocked = 0;
	m_iUpgradeBlocked = 0;
	m_iGiftingBlocked = 0;
	m_iUpgradeOutsideBorders = 0;
//>>>>Unofficial Bug Fix: Added by Denev 2010/02/22
	m_bAvatarOfCivLeader = false;
//<<<<Unofficial Bug Fix: End Add

	if (!bConstructorCall)
	{
        m_paiDamageTypeCombat = new int[GC.getNumDamageTypeInfos()];
        m_paiDamageTypeResist = new int[GC.getNumDamageTypeInfos()];
        for (iI = 0; iI < GC.getNumDamageTypeInfos(); iI++)
        {
            int iChange = (NO_UNIT != m_eUnitType) ? m_pUnitInfo->getDamageTypeCombat(iI) : 0;
            m_paiDamageTypeCombat[iI] = iChange;
            m_paiDamageTypeResist[iI] = 0;
            m_iTotalDamageTypeCombat += iChange;
        }
        m_paiBonusAffinity = new int[GC.getNumBonusInfos()];
        m_paiBonusAffinityAmount = new int[GC.getNumBonusInfos()];
        for (iI = 0; iI < GC.getNumBonusInfos(); iI++)
        {
            m_paiBonusAffinity[iI] = 0;
            m_paiBonusAffinityAmount[iI] = 0;
        }
		
		// XML_LISTS 07/2019 lfgr: cache CvPromotionInfo::isPromotionImmune
		m_paiPromotionImmune = new int[GC.getNumPromotionInfos()];
        for (iI = 0; iI < GC.getNumPromotionInfos(); iI++)
        {
            m_paiPromotionImmune[iI] = 0;
        }
		// XML_LISTS end
	}
//FfH: End Add
	m_combatUnit.reset();
	m_transportUnit.reset();

	for (iI = 0; iI < NUM_DOMAIN_TYPES; iI++)
	{
		m_aiExtraDomainModifier[iI] = 0;
	}

	m_szName.clear();
	m_szScriptData ="";

	if (!bConstructorCall)
	{
		FAssertMsg((0 < GC.getNumPromotionInfos()), "GC.getNumPromotionInfos() is not greater than zero but an array is being allocated in CvUnit::reset");
		m_pabHasPromotion = new bool[GC.getNumPromotionInfos()];
		for (iI = 0; iI < GC.getNumPromotionInfos(); iI++)
		{
			m_pabHasPromotion[iI] = false;
		}

		FAssertMsg((0 < GC.getNumTerrainInfos()), "GC.getNumTerrainInfos() is not greater than zero but a float array is being allocated in CvUnit::reset");
		m_paiTerrainDoubleMoveCount = new int[GC.getNumTerrainInfos()];
		m_paiExtraTerrainAttackPercent = new int[GC.getNumTerrainInfos()];
		m_paiExtraTerrainDefensePercent = new int[GC.getNumTerrainInfos()];
		for (iI = 0; iI < GC.getNumTerrainInfos(); iI++)
		{
			m_paiTerrainDoubleMoveCount[iI] = 0;
			m_paiExtraTerrainAttackPercent[iI] = 0;
			m_paiExtraTerrainDefensePercent[iI] = 0;
		}

		FAssertMsg((0 < GC.getNumFeatureInfos()), "GC.getNumFeatureInfos() is not greater than zero but a float array is being allocated in CvUnit::reset");
		m_paiFeatureDoubleMoveCount = new int[GC.getNumFeatureInfos()];
		m_paiExtraFeatureDefensePercent = new int[GC.getNumFeatureInfos()];
		m_paiExtraFeatureAttackPercent = new int[GC.getNumFeatureInfos()];
		for (iI = 0; iI < GC.getNumFeatureInfos(); iI++)
		{
			m_paiFeatureDoubleMoveCount[iI] = 0;
			m_paiExtraFeatureAttackPercent[iI] = 0;
			m_paiExtraFeatureDefensePercent[iI] = 0;
		}

		FAssertMsg((0 < GC.getNumUnitCombatInfos()), "GC.getNumUnitCombatInfos() is not greater than zero but an array is being allocated in CvUnit::reset");
		m_paiExtraUnitCombatModifier = new int[GC.getNumUnitCombatInfos()];
		for (iI = 0; iI < GC.getNumUnitCombatInfos(); iI++)
		{
			m_paiExtraUnitCombatModifier[iI] = 0;
		}

		AI_reset();
	}
}


//////////////////////////////////////
// graphical only setup
//////////////////////////////////////
void CvUnit::setupGraphical()
{
	if (!GC.IsGraphicsInitialized())
	{
		return;
	}

	CvDLLEntity::setup();

	if (getGroup()->getActivityType() == ACTIVITY_INTERCEPT)
	{
		airCircle(true);
	}
}


// This adopts properties of pUnit. Kills pUnit.
void CvUnit::convert(CvUnit* pUnit)
{
	CvPlot* pPlot = plot();

//FfH: Modified by Kael 08/21/2008
//	for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
//	{
//		setHasPromotion(((PromotionTypes)iI), (pUnit->isHasPromotion((PromotionTypes)iI) || m_pUnitInfo->getFreePromotions(iI)));
//  }
    if (getRace() != NO_PROMOTION)
    {
		if (!m_pUnitInfo->getFreePromotions(getRace()))
        {
            setHasPromotion(((PromotionTypes)getRace()), false);
        }
        else
        {
            pUnit->setHasPromotion(((PromotionTypes)getRace()), true);
        }
    }
    if (pUnit->isHasPromotion((PromotionTypes)GC.defines.iHIDDEN_NATIONALITY_PROMOTION))
    {
        CvUnit* pLoopUnit;
        CLLNode<IDInfo>* pUnitNode;
        pUnitNode = pPlot->headUnitNode();
        while (pUnitNode != NULL)
        {
            pLoopUnit = ::getUnit(pUnitNode->m_data);
            pUnitNode = pPlot->nextUnitNode(pUnitNode);
            if (pLoopUnit->getTeam() != getTeam())
            {
                pUnit->setHasPromotion((PromotionTypes)GC.defines.iHIDDEN_NATIONALITY_PROMOTION, false);
            }
        }
    }

	bool bHero = false;
	for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
	{
        if (pUnit->isHasPromotion((PromotionTypes)iI))
        {
            if (iI == GC.defines.iMUTATED_PROMOTION)
            {
                m_pabHasPromotion[iI] = pUnit->isHasPromotion((PromotionTypes)iI);
            }
            else
            {
                setHasPromotion(((PromotionTypes)iI), true);
                if (GC.getPromotionInfo((PromotionTypes)iI).isEquipment())
                {
                    pUnit->setHasPromotion((PromotionTypes)iI, false);
                }
			    if (GC.getPromotionInfo((PromotionTypes)iI).getFreeXPPerTurn() != 0)
			    {
					bHero = true;
				}
            }
            if (GC.getPromotionInfo((PromotionTypes)iI).isValidate())
            {
				if (getUnitCombatType() == NO_UNITCOMBAT)
				{
                    setHasPromotion(((PromotionTypes)iI), false);
				}
                else if (!GC.getPromotionInfo((PromotionTypes)iI).getUnitCombat(getUnitCombatType()))
                {
                    setHasPromotion(((PromotionTypes)iI), false);
                }
            }
        }
    }
    if (GC.defines.iWEAPON_PROMOTION_TIER1 != -1 && isHasPromotion((PromotionTypes)GC.defines.iWEAPON_PROMOTION_TIER1))
    {
        if (m_pUnitInfo->getWeaponTier() < 1 || isHasPromotion((PromotionTypes)GC.defines.iWEAPON_PROMOTION_TIER2) || isHasPromotion((PromotionTypes)GC.defines.iWEAPON_PROMOTION_TIER3))
        {
            setHasPromotion((PromotionTypes)GC.defines.iWEAPON_PROMOTION_TIER1, false);
        }
    }
    if (GC.defines.iWEAPON_PROMOTION_TIER2 != -1 && isHasPromotion((PromotionTypes)GC.defines.iWEAPON_PROMOTION_TIER2))
    {
        if (m_pUnitInfo->getWeaponTier() < 2 || isHasPromotion((PromotionTypes)GC.defines.iWEAPON_PROMOTION_TIER3))
        {
            setHasPromotion((PromotionTypes)GC.defines.iWEAPON_PROMOTION_TIER2, false);
        }
    }
    if (GC.defines.iWEAPON_PROMOTION_TIER3 != -1 && isHasPromotion((PromotionTypes)GC.defines.iWEAPON_PROMOTION_TIER3))
    {
        if (m_pUnitInfo->getWeaponTier() < 3)
        {
            setHasPromotion((PromotionTypes)GC.defines.iWEAPON_PROMOTION_TIER3, false);
        }
    }
// lfgr 04/2014 bugfix
/* old
    if (m_pUnitInfo->getFreePromotionPick() > 0 && getGameTurnCreated() == GC.getGameINLINE().getGameTurn())
	{
        setPromotionReady(true);
    }
*/
	if( pUnit->getFreePromotionPick() > 0 )
	{
		changeFreePromotionPick( pUnit->getFreePromotionPick() );
	}
// lfgr end

    setDuration(pUnit->getDuration());
    if (pUnit->getReligion() != NO_RELIGION && getReligion() == NO_RELIGION)
    {
        setReligion(pUnit->getReligion());
    }
    if (pUnit->isImmortal())
    {
        pUnit->makeMortal(); // lfgr fix 01/2021: Reliably set counter to 0.
    }
    if (pUnit->isHasCasted())
    {
        setHasCasted(true);
    }
    if (pUnit->getScenarioCounter() != -1)
    {
        setScenarioCounter(pUnit->getScenarioCounter());
    }
//FfH: End Modify

/************************************************************************************************/
/* Afforess	                  Start		 07/29/10                                               */
/* Advanced Diplomacy                                                                           */
/************************************************************************************************/
	m_eOriginalOwner = pUnit->getOriginalOwner();
/************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/************************************************************************************************/

	setGameTurnCreated(pUnit->getGameTurnCreated());
	setDamage(pUnit->getDamage());
	setMoves(pUnit->getMoves());
//>>>>Advanced Rules: Added by Denev 2010/02/04
	setMadeAttack(pUnit->isMadeAttack());
	setImmobileTimer(pUnit->getImmobileTimer());
	setIgnoreHide(pUnit->isIgnoreHide());
	if (getOwnerINLINE() == pUnit->getOwnerINLINE())
	{
		setSummoner(pUnit->getSummoner());

		int iLoop;
		for (CvUnit* pLoopUnit = GET_PLAYER(getOwnerINLINE()).firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = GET_PLAYER(getOwnerINLINE()).nextUnit(&iLoop))
		{
			if (pLoopUnit->getSummoner() == pUnit->getID())
			{
				pLoopUnit->setSummoner(getID());
			}
		}
	}

	if (bHero || isWorldUnitClass((UnitClassTypes)getUnitInfo().getUnitClassType()))
	{
		AI_setUnitAIType(UNITAI_HERO);
	}
//<<<<Advanced Rules: End Add

	setLevel(pUnit->getLevel());
	int iOldModifier = std::max(1, 100 + GET_PLAYER(pUnit->getOwnerINLINE()).getLevelExperienceModifier());
	int iOurModifier = std::max(1, 100 + GET_PLAYER(getOwnerINLINE()).getLevelExperienceModifier());
	setExperience(std::max(0, (pUnit->getExperience() * iOurModifier) / iOldModifier));

// lfgr 04/2014 bugfix
    testPromotionReady();
// lfgr end

	setName(pUnit->getNameNoDesc());
// BUG - Unit Name - start
	if (pUnit->isDescInName() && getBugOptionBOOL("MiscHover__UpdateUnitNameOnUpgrade", true, "BUG_UPDATE_UNIT_NAME_ON_UPGRADE"))
	{
		CvWString szUnitType(pUnit->m_pUnitInfo->getDescription());

		//szUnitType.Format(L"%s", pUnit->m_pUnitInfo->getDescription());
		m_szName.replace(m_szName.find(szUnitType), szUnitType.length(), m_pUnitInfo->getDescription());
	}
// BUG - Unit Name - end
	setLeaderUnitType(pUnit->getLeaderUnitType());

//FfH: Added by Kael 10/03/2008
	if (!isWorldUnitClass((UnitClassTypes)(m_pUnitInfo->getUnitClassType())) && isWorldUnitClass((UnitClassTypes)(pUnit->getUnitClassType())))
	{
	    setName(pUnit->getName());
	}

	// lfgr UnitArtstyle
	bool bArtStyleFound = false;
	if ( pUnit->getUnitArtStyleType() != NO_UNIT_ARTSTYLE )
	{
		setUnitArtStyleType( pUnit->getUnitArtStyleType() );
		bArtStyleFound = true;
	}
	else if (pUnit->getRace() != NO_PROMOTION)
	{
		int iUnitArtStyle = NO_UNIT_ARTSTYLE;
		iUnitArtStyle = GC.getPromotionInfo((PromotionTypes)pUnit->getRace()).getUnitArtStyleType();
		if (iUnitArtStyle != NO_UNIT_ARTSTYLE)
		{
			setUnitArtStyleType(iUnitArtStyle);
			bArtStyleFound = true;
		}
	}

	if (!bArtStyleFound)
	{
		setUnitArtStyleType( GC.getCivilizationInfo( GET_PLAYER( pUnit->getOwnerINLINE() ).getCivilizationType() ).getUnitArtStyleType() );
	}

	reloadEntity();
	// lfgr end

	// Avatars
	if (pUnit->isAvatarOfCivLeader())
	{
		pUnit->setAvatarOfCivLeader(false);
		setAvatarOfCivLeader(true);
	}

//FfH: End Add

	CvUnit* pTransportUnit = pUnit->getTransportUnit();
	if (pTransportUnit != NULL)
	{
		pUnit->setTransportUnit(NULL);
		setTransportUnit(pTransportUnit);
	}

	std::vector<CvUnit*> aCargoUnits;
	pUnit->getCargoUnits(aCargoUnits);
	for (uint i = 0; i < aCargoUnits.size(); ++i)
	{
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       10/30/09                     Mongoose & jdog5000      */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original BTS code
		aCargoUnits[i]->setTransportUnit(this);
*/
		// From Mongoose SDK
		// Check cargo types and capacity when upgrading transports
		if (cargoSpaceAvailable(aCargoUnits[i]->getSpecialUnitType(), aCargoUnits[i]->getDomainType()) > 0)
		{
			aCargoUnits[i]->setTransportUnit(this);
		}
		else
		{
			aCargoUnits[i]->setTransportUnit(NULL);
			aCargoUnits[i]->jumpToNearestValidPlot();
		}
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
	}
	
	logBBAI("    Killing %S (delayed) -- Converted (Unit %d - plot: %d, %d)",
			pUnit->getName().GetCString(), pUnit->getID(), pUnit->getX(), pUnit->getY());
	pUnit->kill(true, NO_PLAYER, true);
}


void CvUnit::kill(bool bDelay, PlayerTypes ePlayer, bool bConvert)
{
	PROFILE_FUNC();
	
	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pTransportUnit;
	CvUnit* pLoopUnit;
	CvPlot* pPlot;
	CvWString szBuffer;
	PlayerTypes eOwner;
	PlayerTypes eCapturingPlayer;
	UnitTypes eCaptureUnitType;

	//bool bIsIllusion = isHasPromotion((PromotionTypes) GC.getInfoTypeForString("PROMOTION_ILLUSION"));
	bool bIllusion = isIllusionary();

	pPlot = plot();
	FAssertMsg(pPlot != NULL, "Plot is not assigned a valid value");

	static std::vector<IDInfo> oldUnits;
	oldUnits.clear();
	pUnitNode = pPlot->headUnitNode();

	while (pUnitNode != NULL)
	{
		oldUnits.push_back(pUnitNode->m_data);
		pUnitNode = pPlot->nextUnitNode(pUnitNode);
	}

	for (uint i = 0; i < oldUnits.size(); i++)
	{
		pLoopUnit = ::getUnit(oldUnits[i]);

		if (pLoopUnit != NULL)
		{
			if (pLoopUnit->getTransportUnit() == this)
			{
				//save old units because kill will clear the static list
				std::vector<IDInfo> tempUnits = oldUnits;

				if (pPlot->isValidDomainForLocation(*pLoopUnit))
				{
					pLoopUnit->setCapturingPlayer(NO_PLAYER);
				}
				
				logBBAI("    Killing %S -- Transporting unit killed (Unit %d - plot: %d, %d)",
						pLoopUnit->getName().GetCString(), pLoopUnit->getID(), pLoopUnit->getX(), pLoopUnit->getY());
				pLoopUnit->kill(false, ePlayer);

				oldUnits = tempUnits;
			}
		}
	}

	if (ePlayer != NO_PLAYER)
	{
		if (!bConvert)
		{
			logBBAI("    %S Slain! (Unit %d - plot: %d, %d)", getName().GetCString(), getID(), getX(), getY());
		}
				
//FfH: Modified by Kael 02/05/2009
//		CvEventReporter::getInstance().unitKilled(this, ePlayer);
        if (!isImmortal())
        {
			CvEventReporter::getInstance().unitKilled(this, ePlayer);
        }
//FfH: End Modify
		else
		{
			logBBAI("    Immortal Rebirth!");
		}

		if (NO_UNIT != getLeaderUnitType())
		{
			for (int iI = 0; iI < MAX_PLAYERS; iI++)
			{
				if (GET_PLAYER((PlayerTypes)iI).isAlive())
				{
					// lfgr 04/2020: Removed irritating "unit defeated" sound effect
					szBuffer = gDLL->getText("TXT_KEY_MISC_GENERAL_KILLED");
					gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)iI), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, NULL, MESSAGE_TYPE_MAJOR_EVENT);
				}
			}
		}
	}

	if (bDelay)
	{
		startDelayedDeath();
		return;
	}

//FfH: Added by Kael 07/23/2008
    if (isImmortal() && !bIllusion && !isCargo())
    {
		if (GET_PLAYER(getOwnerINLINE()).getCapitalCity() != NULL)
		{
			m_bDeathDelay = false;
			doImmortalRebirth();
			return;
		}
    }

    GC.getGameINLINE().changeGlobalCounter(-1 * m_pUnitInfo->getModifyGlobalCounter());

	if (bIllusion) // Make sure that we properly adjust the stats when an Illusionary unit is removed from the game
	{
		GC.getGameINLINE().decrementUnitCreatedCount(getUnitType());
		GC.getGameINLINE().decrementUnitClassCreatedCount((UnitClassTypes)(m_pUnitInfo->getUnitClassType()));
	}

	for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
	{
	    if (isHasPromotion((PromotionTypes)iI))
	    {
            GC.getGameINLINE().changeGlobalCounter(-1 * GC.getPromotionInfo((PromotionTypes)iI).getModifyGlobalCounter());
            if (GC.getPromotionInfo((PromotionTypes)iI).isEquipment() && !bIllusion) // LFGR_TODO: Move bIllusion check up
            {
                for (int iJ = 0; iJ < GC.getNumUnitInfos(); iJ++)
                {
                    if (GC.getUnitInfo((UnitTypes)iJ).getEquipmentPromotion() == iI)
                    {
                        GET_PLAYER(getOwnerINLINE()).initUnit((UnitTypes)iJ, getX_INLINE(), getY_INLINE(), AI_getUnitAIType());
                        setHasPromotion((PromotionTypes)iI, false);
						break;
                    }
                }
            }
	    }
	}
	if (isWorldUnitClass((UnitClassTypes)(m_pUnitInfo->getUnitClassType())) && GC.getGameINLINE().getUnitClassCreatedCount((UnitClassTypes)(m_pUnitInfo->getUnitClassType())) == 1
		&& !m_pUnitInfo->isObject() && !bIllusion)
	{
		for (int iI = 0; iI < MAX_PLAYERS; iI++)
		{
			if (GET_PLAYER((PlayerTypes)iI).isAlive() && GET_PLAYER((PlayerTypes)iI).isHuman() && getOwner() != iI)
			{
                szBuffer = gDLL->getText("TXT_KEY_MISC_SOMEONE_KILLED_UNIT", getNameKey());
                gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)iI), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_WONDER_UNIT_BUILD", MESSAGE_TYPE_MAJOR_EVENT, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_UNIT_TEXT"), getX_INLINE(), getY_INLINE(), true, true);
			}
		}
	}
	int iLoop;
    for (pLoopUnit = GET_PLAYER(getOwnerINLINE()).firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = GET_PLAYER(getOwnerINLINE()).nextUnit(&iLoop))
    {
        if (pLoopUnit->getSummoner() == getID())
        {
            pLoopUnit->setSummoner(-1);
        }
    }
//FfH: End Add

	if (isMadeAttack() && nukeRange() != -1)
	{
		CvPlot* pTarget = getAttackPlot();
		if (pTarget)
		{
			pTarget->nukeExplosion(nukeRange(), this);
			setAttackPlot(NULL, false);
		}
	}

	finishMoves();

	if (IsSelected())
	{
		if (gDLL->getInterfaceIFace()->getLengthSelectionList() == 1)
		{
			if (!(gDLL->getInterfaceIFace()->isFocused()) && !(gDLL->getInterfaceIFace()->isCitySelection()) && !(gDLL->getInterfaceIFace()->isDiploOrPopupWaiting()))
			{
				GC.getGameINLINE().updateSelectionList();
			}

			if (IsSelected())
			{
				gDLL->getInterfaceIFace()->setCycleSelectionCounter(1);
			}
			else
			{
				gDLL->getInterfaceIFace()->setDirty(SelectionCamera_DIRTY_BIT, true);
			}
		}
	}

	gDLL->getInterfaceIFace()->removeFromSelectionList(this);

	// XXX this is NOT a hack, without it, the game crashes.
	gDLL->getEntityIFace()->RemoveUnitFromBattle(this);

	FAssertMsg(!isCombat(), "isCombat did not return false as expected");

	pTransportUnit = getTransportUnit();

	if (pTransportUnit != NULL)
	{
		setTransportUnit(NULL);
	}

	setReconPlot(NULL);
	setBlockading(false);

	FAssertMsg(getAttackPlot() == NULL, "The current unit instance's attack plot is expected to be NULL");
	FAssertMsg(getCombatUnit() == NULL, "The current unit instance's combat unit is expected to be NULL");

	GET_TEAM(getTeam()).changeUnitClassCount((UnitClassTypes)m_pUnitInfo->getUnitClassType(), -1);
	GET_PLAYER(getOwnerINLINE()).changeUnitClassCount((UnitClassTypes)m_pUnitInfo->getUnitClassType(), -1);

	GET_PLAYER(getOwnerINLINE()).changeExtraUnitCost(-(m_pUnitInfo->getExtraCost()));

	if (m_pUnitInfo->getNukeRange() != -1)
	{
		GET_PLAYER(getOwnerINLINE()).changeNumNukeUnits(-1);
	}

	if (m_pUnitInfo->isMilitarySupport())
	{
		GET_PLAYER(getOwnerINLINE()).changeNumMilitaryUnits(-1);
	}

	GET_PLAYER(getOwnerINLINE()).changeAssets(-(m_pUnitInfo->getAssetValue()));

	//GET_PLAYER(getOwnerINLINE()).changePower(-(m_pUnitInfo->getPowerValue()));
	GET_PLAYER(getOwnerINLINE()).changePower(-(getTruePower())); // MNAI - True Power calculations

	GET_PLAYER(getOwnerINLINE()).AI_changeNumAIUnits(AI_getUnitAIType(), -1);

	eOwner = getOwnerINLINE();
	eCapturingPlayer = getCapturingPlayer();

//FfH: Modified by Kael 09/01/2007
//	eCaptureUnitType = ((eCapturingPlayer != NO_PLAYER) ? getCaptureUnitType(GET_PLAYER(eCapturingPlayer).getCivilizationType()) : NO_UNIT);
    eCaptureUnitType = ((eCapturingPlayer != NO_PLAYER) ? getCaptureUnitType(GET_PLAYER(getOwnerINLINE()).getCivilizationType()) : NO_UNIT);
    if (m_pUnitInfo->getUnitCaptureClassType() == getUnitClassType())
    {
        eCaptureUnitType = (UnitTypes)getUnitType();
    }
    int iRace = getRace();
//FfH: End Modify

// BUG - Unit Captured Event - start
	PlayerTypes eFromPlayer = getOwner();
	UnitTypes eCapturedUnitType = getUnitType();
// BUG - Unit Captured Event - end


//>>>>Unofficial Bug Fix: Added by Denev 2010/02/22
	if (isAvatarOfCivLeader())
	{
		if (!bConvert)
		{
			CvLeaderHeadInfo& kLeaderHeadInfo = GC.getLeaderHeadInfo(GET_PLAYER(getOwnerINLINE()).getLeaderType());
			const TraitTypes eCivTrait = (TraitTypes)GC.getCivilizationInfo(GET_PLAYER(getOwnerINLINE()).getCivilizationType()).getCivTrait();

			for (int iTrait = 0; iTrait < GC.getNumTraitInfos(); iTrait++)
			{
				if (kLeaderHeadInfo.hasTrait(iTrait))
				{
					if (iTrait != eCivTrait)
					{
						GET_PLAYER(getOwnerINLINE()).setHasTrait((TraitTypes)iTrait, false);
					}
				}
			}
		}
	}
//<<<<Unofficial Bug Fix: End Add

	if (!bConvert)
	{
		CvEventReporter::getInstance().unitLost(this);
	}
	
	joinGroup(NULL, false, false);
	
	setXY(INVALID_PLOT_COORD, INVALID_PLOT_COORD, true);

	// lfgr fix 07/2019: retain name of captured unit: store name before deleting
	CvWString szName = m_szName;
	// lfgr end

	GET_PLAYER(getOwnerINLINE()).deleteUnit(getID());

//FfH: Modified by Kael 01/19/2008
//	if ((eCapturingPlayer != NO_PLAYER) && (eCaptureUnitType != NO_UNIT) && !(GET_PLAYER(eCapturingPlayer).isBarbarian()))
	if ((eCapturingPlayer != NO_PLAYER) && (eCaptureUnitType != NO_UNIT))
//FfH: End Modify

	{
		if (GET_PLAYER(eCapturingPlayer).isHuman() || GET_PLAYER(eCapturingPlayer).AI_captureUnit(eCaptureUnitType, pPlot) || 0 == GC.defines.iAI_CAN_DISBAND_UNITS)
		{
			CvUnit* pkCapturedUnit = GET_PLAYER(eCapturingPlayer).initUnit(eCaptureUnitType, pPlot->getX_INLINE(), pPlot->getY_INLINE());

//FfH: Added by Kael 08/18/2008; LFGR_TODO: move into pkCaptureUnit != NULL ?
            if (pkCapturedUnit->getRace() != NO_PROMOTION) // LFGR_TODO: Unnecessary?
            {
                pkCapturedUnit->setHasPromotion((PromotionTypes)pkCapturedUnit->getRace(), false);
            }
            if (iRace != NO_PROMOTION)
            {
                pkCapturedUnit->setHasPromotion((PromotionTypes)iRace, true);
            }
//FfH: End Add

			if (pkCapturedUnit != NULL)
			{
// BUG - Unit Captured Event - start
				CvEventReporter::getInstance().unitCaptured(eFromPlayer, eCapturedUnitType, pkCapturedUnit);
// BUG - Unit Captured Event - end

				szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_CAPTURED_UNIT", GC.getUnitInfo(eCaptureUnitType).getTextKeyWide());
				gDLL->getInterfaceIFace()->addMessage(eCapturingPlayer, true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_UNITCAPTURE", MESSAGE_TYPE_INFO, pkCapturedUnit->getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE());

				// lfgr fix 07/2019: retain name of captured unit
				pkCapturedUnit->setName( szName );
				// lfgr end

				// Add a captured mission
				CvMissionDefinition kMission;
				kMission.setMissionTime(GC.getMissionInfo(MISSION_CAPTURED).getTime() * gDLL->getSecsPerTurn());
				kMission.setUnit(BATTLE_UNIT_ATTACKER, pkCapturedUnit);
				kMission.setUnit(BATTLE_UNIT_DEFENDER, NULL);
				kMission.setPlot(pPlot);
				kMission.setMissionType(MISSION_CAPTURED);
				gDLL->getEntityIFace()->AddMission(&kMission);

				pkCapturedUnit->finishMoves();

				if (!GET_PLAYER(eCapturingPlayer).isHuman())
				{
					CvPlot* pPlot = pkCapturedUnit->plot();
					if (pPlot && !pPlot->isCity(false))
					{
						if (GET_PLAYER(eCapturingPlayer).AI_getPlotDanger(pPlot) && GC.defines.iAI_CAN_DISBAND_UNITS

//FfH: Added by Kael 12/02/2007
                          && pkCapturedUnit->canScrap()
//FfH: End Add

						  )
						{
							logBBAI("    Killing %S -- AI kills captured units (Unit %d - plot: %d, %d)",
									pkCapturedUnit->getName().GetCString(), pkCapturedUnit->getID(), pkCapturedUnit->getX(), pkCapturedUnit->getY());
							pkCapturedUnit->kill(false);
						}
					}
				}
			}
		}
	}
}


void CvUnit::NotifyEntity(MissionTypes eMission)
{
	gDLL->getEntityIFace()->NotifyEntity(getUnitEntity(), eMission);
}


void CvUnit::doTurn()
{
	PROFILE("CvUnit::doTurn()")

	FAssertMsg(!isDead(), "isDead did not return false as expected");
	FAssertMsg(getGroup() != NULL, "getGroup() is not expected to be equal with NULL");

//FfH Spell System: Added by Kael 07/23/2007
    int iI;
    CvPlot* pPlot = plot();
	if (hasMoved())
	{
		if (isAlwaysHeal() || isBarbarian())
		{
			doHeal();
		}
	}
	else
	{
		if (isHurt())
		{
			doHeal();
		}

		if (!isCargo())
		{
			changeFortifyTurns(1);
		}
	}
    if (m_pUnitInfo->isAbandon())
    {
        if (!isBarbarian())
        {
            bool bValid = true;
            if (m_pUnitInfo->getPrereqCivic() != NO_CIVIC)
            {
                bValid = false;
                for (int iI = 0; iI < GC.defines.iMAX_CIVIC_OPTIONS; iI++)
                {
                    if (GET_PLAYER(getOwnerINLINE()).getCivics((CivicOptionTypes)iI) == m_pUnitInfo->getPrereqCivic())
                    {
                        bValid = true;
                    }
                }
                if (GET_PLAYER(getOwnerINLINE()).isAnarchy())
                {
                    bValid = true;
                }
            }
            if (bValid == true)
            {
                if (m_pUnitInfo->getStateReligion() != NO_RELIGION)
                {
                    bValid = false;
                    if (GET_PLAYER(getOwnerINLINE()).getStateReligion() == m_pUnitInfo->getStateReligion())
                    {
                        bValid = true;
                    }
                }
            }
            if (bValid == false)
            {
				if( isImmortal() )
				{
					makeMortal(); // lfgr fix 01/2021: Reliably set counter to 0.
				}
                gDLL->getInterfaceIFace()->addMessage((PlayerTypes)getOwnerINLINE(), true, GC.defines.iEVENT_MESSAGE_TIME, gDLL->getText("TXT_KEY_MESSAGE_UNIT_ABANDON", getNameKey()), GC.getEraInfo(GC.getGameINLINE().getCurrentEra()).getAudioUnitDefeatScript(), MESSAGE_TYPE_INFO, m_pUnitInfo->getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), plot()->getX_INLINE(), plot()->getY_INLINE());
				logBBAI("    Killing %S (delayed) -- abandoned owner (Unit %d - plot: %d, %d)",
						getName().GetCString(), getID(), getX(), getY());
                kill(true);
                GC.getGameINLINE().decrementUnitCreatedCount(getUnitType());
                GC.getGameINLINE().decrementUnitClassCreatedCount((UnitClassTypes)(m_pUnitInfo->getUnitClassType()));

				/* - Tholal AI - these functions are already handled in the kill section
                GET_TEAM(getTeam()).changeUnitClassCount(((UnitClassTypes)(m_pUnitInfo->getUnitClassType())), -1);
                GET_PLAYER(getOwnerINLINE()).changeUnitClassCount(((UnitClassTypes)(m_pUnitInfo->getUnitClassType())), -1);
                GET_PLAYER(getOwnerINLINE()).changeExtraUnitCost(m_pUnitInfo->getExtraCost() * -1);
				*/
            }
        }
    }
	for (iI = 0; iI < GC.getNumPromotionInfos(); iI++)
	{
		if (isHasPromotion((PromotionTypes)iI))
		{
		    if (GC.getPromotionInfo((PromotionTypes)iI).getFreeXPPerTurn() != 0)
		    {
                if (getExperience() < GC.defines.iFREE_XP_MAX)
                {
                    changeExperience(GC.getPromotionInfo((PromotionTypes)iI).getFreeXPPerTurn(), -1, false, false, false);
                }
		    }
		    if (GC.getPromotionInfo((PromotionTypes)iI).getPromotionRandomApply() != NO_PROMOTION)
		    {
                if (!isHasPromotion((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iI).getPromotionRandomApply()))
                {
                    if (GC.getGameINLINE().getSorenRandNum(100, "Promotion Random Apply") <= 3)
                    {
                        setHasPromotion(((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iI).getPromotionRandomApply()), true);
                    }
                }
		    }
		    if (GC.getPromotionInfo((PromotionTypes)iI).getBetrayalChance() != 0)
		    {
                if (!isImmuneToCapture() && !isBarbarian() && !GC.getGameINLINE().isOption(GAMEOPTION_NO_BARBARIANS))
                {
                    if (GC.getGameINLINE().getSorenRandNum(100, "Betrayal Chance") <= GC.getPromotionInfo((PromotionTypes)iI).getBetrayalChance())
                    {
                        betray(BARBARIAN_PLAYER);
                    }
                }
		    }
            if (!CvString(GC.getPromotionInfo((PromotionTypes)iI).getPyPerTurn()).empty())
            {
                CyUnit* pyUnit = new CyUnit(this);
                CyArgsList argsList;
                argsList.add(gDLL->getPythonIFace()->makePythonObject(pyUnit));	// pass in unit class
                argsList.add(iI);//the promotion #
                gDLL->getPythonIFace()->callFunction(PYSpellModule, "effect", argsList.makeFunctionArgs()); //, &lResult
                delete pyUnit; // python fxn must not hold on to this pointer
            }
		    if (GC.getPromotionInfo((PromotionTypes)iI).getExpireChance() != 0)
		    {
                if (GC.getGameINLINE().getSorenRandNum(100, "Promotion Expire") <= GC.getPromotionInfo((PromotionTypes)iI).getExpireChance())
                {
                    setHasPromotion(((PromotionTypes)iI), false);
                }
		    }
            if (!isHurt())
            {
                if (GC.getPromotionInfo((PromotionTypes)iI).isRemovedWhenHealed())
                {
                    setHasPromotion(((PromotionTypes)iI), false);
                }
		    }
		}
	}

	setHasCasted(false);

    if (getSpellCasterXP() > 0)
    {
		int iGameSpeedMod = GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getTrainPercent();

        if (((GC.getGameINLINE().getSorenRandNum(100, "SpellCasterXP") * iGameSpeedMod) / 100) < getSpellCasterXP() - getExperience())
        {
            changeExperience(1, -1, false, false, false);
        }
    }
	if (getDuration() > 0)
	{
	    changeDuration(-1);
	    if (getDuration() == 0)
	    {
	        if (isImmortal())
	        {
	            makeMortal(); // lfgr fix 01/2021: Reliably set counter to 0.
	        }

			// summoned transport units unload cargo when they expire
			if (getCargo() > 0)
			{
				unloadAll();
			}
			
			logBBAI("    Killing %S (delayed) -- Duration over (Unit %d - plot: %d, %d)",
					getName().GetCString(), getID(), getX(), getY());
            kill(true);
	    }
	}
    if (pPlot->isCity())
    {
        if (m_pUnitInfo->getWeaponTier() > 0)
        {
            setWeapons();
        }
        if (isBarbarian())
        {
            if (m_pUnitInfo->isAutoRaze())
            {
                if (pPlot->getOwner() == getOwnerINLINE())
                {
                    pPlot->getPlotCity()->kill(true);
                }
            }
        }
    }
	// lfgr fix 01/2021: Don't revive units that are already dead.
    if( m_pUnitInfo->isImmortal() && !isDelayedDeath() )
    {
        if (!isImmortal())
        {
            changeImmortal(1);
        }
    }
//FfH: End Add

	testPromotionReady();

	if (isBlockading())
	{
		collectBlockadeGold();
	}

//FfH: Modified by Kael 02/03/2009 (spy intercept and feature damage commented out for performance, healing moved to earlier in the function)
//	if (isSpy() && isIntruding() && !isCargo())
//	{
//		TeamTypes eTeam = plot()->getTeam();
//		if (NO_TEAM != eTeam)
//		{
//			if (GET_TEAM(getTeam()).isOpenBorders(eTeam))
//			{
//				testSpyIntercepted(plot()->getOwnerINLINE(), GC.defines.iESPIONAGE_SPY_NO_INTRUDE_INTERCEPT_MOD);
//			}
//			else
//			{
//				testSpyIntercepted(plot()->getOwnerINLINE(), GC.defines.iESPIONAGE_SPY_INTERCEPT_MOD);
//			}
//		}
//	}
//	if (baseCombatStr() > 0)
//	{
//		FeatureTypes eFeature = plot()->getFeatureType();
//		if (NO_FEATURE != eFeature)
//		{
//			if (0 != GC.getFeatureInfo(eFeature).getTurnDamage())
//			{
//				changeDamage(GC.getFeatureInfo(eFeature).getTurnDamage(), NO_PLAYER);
//			}
//		}
//	}
//	if (hasMoved())
//	{
//		if (isAlwaysHeal())
//		{
//			doHeal();
//		}
//	}
//	else
//	{
//		if (isHurt())
//		{
//			doHeal();
//		}
//		if (!isCargo())
//		{
//			changeFortifyTurns(1);
//		}
//	}
//FfH:End Modify

	changeImmobileTimer(-1);

	setMadeAttack(false);
	setMadeInterception(false);

	setReconPlot(NULL);

	setMoves(0);

/*************************************************************************************************/
/**	BETTER AI (Choose Groupflag) Sephi                             					            **/
/**																								**/
/**						                                            							**/
/*************************************************************************************************/
	
    if (!GET_PLAYER(getOwnerINLINE()).isHuman())
    {
        if (!isBarbarian())
        {
			if (AI_getGroupflag() == GROUPFLAG_NONE && (getGroup()->getNumUnits() < 3))
			{
				switch (AI_getUnitAIType())
				{
					case UNITAI_ATTACK:
					case UNITAI_ATTACK_CITY:
					case UNITAI_COUNTER:
					case UNITAI_CITY_COUNTER:
					case UNITAI_CITY_DEFENSE:
					case UNITAI_HERO:
					case UNITAI_WARWIZARD:
					case UNITAI_MAGE:
					case UNITAI_MEDIC:
					case UNITAI_COLLATERAL:
						AI_chooseGroupflag();
						break;
					default:
						break;
				}
			}
        }
    }
	
/*************************************************************************************************/
/**	END	                                        												**/
/*************************************************************************************************/

}


void CvUnit::updateAirStrike(CvPlot* pPlot, bool bQuick, bool bFinish)
{
	bool bVisible = false;

	if (!bFinish)
	{
		if (isFighting())
		{
			return;
		}

		if (!bQuick)
		{
			bVisible = isCombatVisible(NULL);
		}

		if (!airStrike(pPlot))
		{
			return;
		}

		if (bVisible)
		{
			CvAirMissionDefinition kAirMission;
			kAirMission.setMissionType(MISSION_AIRSTRIKE);
			kAirMission.setUnit(BATTLE_UNIT_ATTACKER, this);
			kAirMission.setUnit(BATTLE_UNIT_DEFENDER, NULL);
			kAirMission.setDamage(BATTLE_UNIT_DEFENDER, 0);
			kAirMission.setDamage(BATTLE_UNIT_ATTACKER, 0);
			kAirMission.setPlot(pPlot);
			setCombatTimer(GC.getMissionInfo(MISSION_AIRSTRIKE).getTime());
			GC.getGameINLINE().incrementTurnTimer(getCombatTimer());
			kAirMission.setMissionTime(getCombatTimer() * gDLL->getSecsPerTurn());

			if (pPlot->isActiveVisible(false))
			{
				gDLL->getEntityIFace()->AddMission(&kAirMission);
			}

			return;
		}
	}

	CvUnit *pDefender = getCombatUnit();
	if (pDefender != NULL)
	{
		pDefender->setCombatUnit(NULL);
	}
	setCombatUnit(NULL);
	setAttackPlot(NULL, false);

	getGroup()->clearMissionQueue();

	if (isSuicide() && !isDead())
	{
		logBBAI("    Killing %S (delayed) -- suicide air strike (Unit %d - plot: %d, %d)",
			getName().GetCString(), getID(), getX(), getY());
		kill(true);
	}
}

void CvUnit::resolveAirCombat(CvUnit* pInterceptor, CvPlot* pPlot, CvAirMissionDefinition& kBattle)
{
	CvWString szBuffer;

	int iTheirStrength = (DOMAIN_AIR == pInterceptor->getDomainType() ? pInterceptor->airCurrCombatStr(this) : pInterceptor->currCombatStr(NULL, NULL));
	int iOurStrength = (DOMAIN_AIR == getDomainType() ? airCurrCombatStr(pInterceptor) : currCombatStr(NULL, NULL)); // LFGR_TODO: ( NULL, pDefender )?
	int iTotalStrength = iOurStrength + iTheirStrength;
	if (0 == iTotalStrength)
	{
		FAssert(false);
		return;
	}

	int iOurOdds = (100 * iOurStrength) / std::max(1, iTotalStrength);

	int iOurRoundDamage = (pInterceptor->currInterceptionProbability() * GC.defines.iMAX_INTERCEPTION_DAMAGE) / 100;
	int iTheirRoundDamage = (currInterceptionProbability() * GC.defines.iMAX_INTERCEPTION_DAMAGE) / 100;
	if (getDomainType() == DOMAIN_AIR)
	{
		iTheirRoundDamage = std::max(GC.defines.iMIN_INTERCEPTION_DAMAGE, iTheirRoundDamage);
	}

	int iTheirDamage = 0;
	int iOurDamage = 0;

	for (int iRound = 0; iRound < GC.defines.iINTERCEPTION_MAX_ROUNDS; ++iRound)
	{
		if (GC.getGameINLINE().getSorenRandNum(100, "Air combat") < iOurOdds)
		{
			if (DOMAIN_AIR == pInterceptor->getDomainType())
			{
				iTheirDamage += iTheirRoundDamage;
				pInterceptor->changeDamage(iTheirRoundDamage, getOwnerINLINE());
				if (pInterceptor->isDead())
				{
					break;
				}
			}
		}
		else
		{
			iOurDamage += iOurRoundDamage;
			changeDamage(iOurRoundDamage, pInterceptor->getOwnerINLINE());
			if (isDead())
			{
				break;
			}
		}
	}

	if (isDead())
	{
		if (iTheirRoundDamage > 0)
		{
			int iExperience = attackXPValue();
			iExperience = (iExperience * iOurStrength) / std::max(1, iTheirStrength);
			iExperience = range(iExperience, GC.defines.iMIN_EXPERIENCE_PER_COMBAT, GC.defines.iMAX_EXPERIENCE_PER_COMBAT);
			pInterceptor->changeExperience(iExperience, maxXPValue(), true, pPlot->getOwnerINLINE() == pInterceptor->getOwnerINLINE(), !isBarbarian());
		}
	}
	else if (pInterceptor->isDead())
	{
		int iExperience = pInterceptor->defenseXPValue();
		iExperience = (iExperience * iTheirStrength) / std::max(1, iOurStrength);
		iExperience = range(iExperience, GC.defines.iMIN_EXPERIENCE_PER_COMBAT, GC.defines.iMAX_EXPERIENCE_PER_COMBAT);
		changeExperience(iExperience, pInterceptor->maxXPValue(), true, pPlot->getOwnerINLINE() == getOwnerINLINE(), !pInterceptor->isBarbarian());
	}
	else if (iOurDamage > 0)
	{
		if (iTheirRoundDamage > 0)
		{
			pInterceptor->changeExperience(GC.defines.iEXPERIENCE_FROM_WITHDRAWL, maxXPValue(), true, pPlot->getOwnerINLINE() == pInterceptor->getOwnerINLINE(), !isBarbarian());
		}
	}
	else if (iTheirDamage > 0)
	{
		changeExperience(GC.defines.iEXPERIENCE_FROM_WITHDRAWL, pInterceptor->maxXPValue(), true, pPlot->getOwnerINLINE() == getOwnerINLINE(), !pInterceptor->isBarbarian());
	}

	kBattle.setDamage(BATTLE_UNIT_ATTACKER, iOurDamage);
	kBattle.setDamage(BATTLE_UNIT_DEFENDER, iTheirDamage);
}


void CvUnit::updateAirCombat(bool bQuick)
{
	CvUnit* pInterceptor = NULL;
	bool bFinish = false;

	FAssert(getDomainType() == DOMAIN_AIR || getDropRange() > 0);

	if (getCombatTimer() > 0)
	{
		changeCombatTimer(-1);

		if (getCombatTimer() > 0)
		{
			return;
		}
		else
		{
			bFinish = true;
		}
	}

	CvPlot* pPlot = getAttackPlot();
	if (pPlot == NULL)
	{
		return;
	}

	if (bFinish)
	{
		pInterceptor = getCombatUnit();
	}
	else
	{
		pInterceptor = bestInterceptor(pPlot);
	}


	if (pInterceptor == NULL)
	{
		setAttackPlot(NULL, false);
		setCombatUnit(NULL);

		getGroup()->clearMissionQueue();

		return;
	}

	//check if quick combat
	bool bVisible = false;
	if (!bQuick)
	{
		bVisible = isCombatVisible(pInterceptor);
	}

	//if not finished and not fighting yet, set up combat damage and mission
	if (!bFinish)
	{
		if (!isFighting())
		{
			if (plot()->isFighting() || pPlot->isFighting())
			{
				return;
			}

			setMadeAttack(true);

			setCombatUnit(pInterceptor, true);
			pInterceptor->setCombatUnit(this, false);
		}

		FAssertMsg(pInterceptor != NULL, "Defender is not assigned a valid value");

		FAssertMsg(plot()->isFighting(), "Current unit instance plot is not fighting as expected");
		FAssertMsg(pInterceptor->plot()->isFighting(), "pPlot is not fighting as expected");

		CvAirMissionDefinition kAirMission;
		if (DOMAIN_AIR != getDomainType())
		{
			kAirMission.setMissionType(MISSION_PARADROP);
		}
		else
		{
			kAirMission.setMissionType(MISSION_AIRSTRIKE);
		}
		kAirMission.setUnit(BATTLE_UNIT_ATTACKER, this);
		kAirMission.setUnit(BATTLE_UNIT_DEFENDER, pInterceptor);

		resolveAirCombat(pInterceptor, pPlot, kAirMission);

		if (!bVisible)
		{
			bFinish = true;
		}
		else
		{
			kAirMission.setPlot(pPlot);
			kAirMission.setMissionTime(GC.getMissionInfo(MISSION_AIRSTRIKE).getTime() * gDLL->getSecsPerTurn());
			setCombatTimer(GC.getMissionInfo(MISSION_AIRSTRIKE).getTime());
			GC.getGameINLINE().incrementTurnTimer(getCombatTimer());

			if (pPlot->isActiveVisible(false))
			{
				gDLL->getEntityIFace()->AddMission(&kAirMission);
			}
		}

		changeMoves(GC.getMOVE_DENOMINATOR());
		if (DOMAIN_AIR != pInterceptor->getDomainType())
		{
			pInterceptor->setMadeInterception(true);
		}

		if (isDead())
		{
			CvWString szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_SHOT_DOWN_ENEMY", pInterceptor->getNameKey(), getNameKey(), getVisualCivAdjective(pInterceptor->getTeam()));
			gDLL->getInterfaceIFace()->addMessage(pInterceptor->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_INTERCEPT", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE(), true, true);

			szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_UNIT_SHOT_DOWN", getNameKey(), pInterceptor->getNameKey());
			gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_INTERCEPTED", MESSAGE_TYPE_INFO, pInterceptor->getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
		}
		else if (kAirMission.getDamage(BATTLE_UNIT_ATTACKER) > 0)
		{
			CvWString szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_HURT_ENEMY_AIR", pInterceptor->getNameKey(), getNameKey(), -(kAirMission.getDamage(BATTLE_UNIT_ATTACKER)), getVisualCivAdjective(pInterceptor->getTeam()));
			gDLL->getInterfaceIFace()->addMessage(pInterceptor->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_INTERCEPT", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE(), true, true);

			szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_AIR_UNIT_HURT", getNameKey(), pInterceptor->getNameKey(), -(kAirMission.getDamage(BATTLE_UNIT_ATTACKER)));
			gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_INTERCEPTED", MESSAGE_TYPE_INFO, pInterceptor->getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
		}

		if (pInterceptor->isDead())
		{
			CvWString szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_SHOT_DOWN_ENEMY", getNameKey(), pInterceptor->getNameKey(), pInterceptor->getVisualCivAdjective(getTeam()));
			gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_INTERCEPT", MESSAGE_TYPE_INFO, pInterceptor->getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE(), true, true);

			szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_UNIT_SHOT_DOWN", pInterceptor->getNameKey(), getNameKey());
			gDLL->getInterfaceIFace()->addMessage(pInterceptor->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_INTERCEPTED", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
		}
		else if (kAirMission.getDamage(BATTLE_UNIT_DEFENDER) > 0)
		{
			CvWString szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_DAMAGED_ENEMY_AIR", getNameKey(), pInterceptor->getNameKey(), -(kAirMission.getDamage(BATTLE_UNIT_DEFENDER)), pInterceptor->getVisualCivAdjective(getTeam()));
			gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_INTERCEPT", MESSAGE_TYPE_INFO, pInterceptor->getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE(), true, true);

			szBuffer = gDLL->getText("TXT_KEY_MISC_YOUR_AIR_UNIT_DAMAGED", pInterceptor->getNameKey(), getNameKey(), -(kAirMission.getDamage(BATTLE_UNIT_DEFENDER)));
			gDLL->getInterfaceIFace()->addMessage(pInterceptor->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_INTERCEPTED", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
		}

		if (0 == kAirMission.getDamage(BATTLE_UNIT_ATTACKER) + kAirMission.getDamage(BATTLE_UNIT_DEFENDER))
		{
			CvWString szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_ABORTED_ENEMY_AIR", pInterceptor->getNameKey(), getNameKey(), getVisualCivAdjective(getTeam()));
			gDLL->getInterfaceIFace()->addMessage(pInterceptor->getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_INTERCEPT", MESSAGE_TYPE_INFO, pInterceptor->getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE(), true, true);

			szBuffer = gDLL->getText("TXT_KEY_MISC_YOUR_AIR_UNIT_ABORTED", getNameKey(), pInterceptor->getNameKey());
			gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_INTERCEPTED", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
		}
	}

	if (bFinish)
	{
		setAttackPlot(NULL, false);
		setCombatUnit(NULL);
		pInterceptor->setCombatUnit(NULL);

		if (!isDead() && isSuicide())
		{
			logBBAI("    Killing %S (delayed) -- suicide air combad (Unit %d - plot: %d, %d)",
				getName().GetCString(), getID(), getX(), getY());
			kill(true);
		}
	}
}

void CvUnit::resolveCombat(CvUnit* pDefender, CvPlot* pPlot, CvBattleDefinition& kBattle)
{
	CombatDetails cdAttackerDetails;
	CombatDetails cdDefenderDetails;

//FfH: Modified by Kael 01/14/2009
//	int iAttackerStrength = currCombatStr(NULL, NULL, &cdAttackerDetails);
//	int iAttackerFirepower = currFirepower(NULL, NULL);
	int iAttackerStrength = currCombatStr(NULL, pDefender, &cdAttackerDetails);
	int iAttackerFirepower = currFirepower(NULL, pDefender);
//FfH: End Modify

	int iDefenderStrength;
	int iAttackerDamage;
	int iDefenderDamage;
	int iDefenderOdds;

	getDefenderCombatValues(*pDefender, pPlot, iAttackerStrength, iAttackerFirepower, iDefenderOdds, iDefenderStrength, iAttackerDamage, iDefenderDamage, &cdDefenderDetails);
	int iAttackerKillOdds = iDefenderOdds * (100 - withdrawalProbability()) / 100;

//FfH: Modified by Kael 08/02/2008
//	if (isHuman() || pDefender->isHuman())
//	{
//		//Added ST
//		CyArgsList pyArgsCD;
//		pyArgsCD.add(gDLL->getPythonIFace()->makePythonObject(&cdAttackerDetails));
//		pyArgsCD.add(gDLL->getPythonIFace()->makePythonObject(&cdDefenderDetails));
//		pyArgsCD.add(getCombatOdds(this, pDefender));
//		gDLL->getEventReporterIFace()->genericEvent("combatLogCalc", pyArgsCD.makeFunctionArgs());
//	}
    if(GC.getUSE_COMBAT_RESULT_CALLBACK())
    {
        if (isHuman() || pDefender->isHuman())
        {
            CyArgsList pyArgsCD;
            pyArgsCD.add(gDLL->getPythonIFace()->makePythonObject(&cdAttackerDetails));
            pyArgsCD.add(gDLL->getPythonIFace()->makePythonObject(&cdDefenderDetails));
            pyArgsCD.add(getCombatOdds(this, pDefender));
			CvEventReporter::getInstance().genericEvent("combatLogCalc", pyArgsCD.makeFunctionArgs());
        }
	}
//FfH: End Modify

	collateralCombat(pPlot, pDefender);

	while (true)
	{
		if (GC.getGameINLINE().getSorenRandNum(GC.defines.iCOMBAT_DIE_SIDES, "Combat") < iDefenderOdds)
		{
			if (getCombatFirstStrikes() == 0)
			{
				if (getDamage() + iAttackerDamage >= maxHitPoints() && GC.getGameINLINE().getSorenRandNum(100, "Withdrawal") < withdrawalProbability())
				{
					flankingStrikeCombat(pPlot, iAttackerStrength, iAttackerFirepower, iAttackerKillOdds, iDefenderDamage, pDefender);

					changeExperience(GC.defines.iEXPERIENCE_FROM_WITHDRAWL, pDefender->maxXPValue(), true, pPlot->getOwnerINLINE() == getOwnerINLINE(), !pDefender->isBarbarian());
// BUG - Combat Events - start
					CvEventReporter::getInstance().combatRetreat(this, pDefender);
// BUG - Combat Events - end
//FfH Promotions: Added by Kael 08/12/2007
                    setFleeWithdrawl(true);
//FfH: End Add

					break;
				}

				changeDamage(iAttackerDamage, pDefender->getOwnerINLINE());

				if (pDefender->getCombatFirstStrikes() > 0 && pDefender->isRanged())
				{
					kBattle.addFirstStrikes(BATTLE_UNIT_DEFENDER, 1);
					kBattle.addDamage(BATTLE_UNIT_ATTACKER, BATTLE_TIME_RANGED, iAttackerDamage);
				}

				cdAttackerDetails.iCurrHitPoints = currHitPoints();

//FfH: Modified by Kael 08/02/2008
//				if (isHuman() || pDefender->isHuman())
//				{
//					CyArgsList pyArgs;
//					pyArgs.add(gDLL->getPythonIFace()->makePythonObject(&cdAttackerDetails));
//					pyArgs.add(gDLL->getPythonIFace()->makePythonObject(&cdDefenderDetails));
//					pyArgs.add(1);
//					pyArgs.add(iAttackerDamage);
//					gDLL->getEventReporterIFace()->genericEvent("combatLogHit", pyArgs.makeFunctionArgs());
//				}
                if(GC.getUSE_COMBAT_RESULT_CALLBACK())
                {
                    if (isHuman() || pDefender->isHuman())
                    {
                        CyArgsList pyArgs;
                        pyArgs.add(gDLL->getPythonIFace()->makePythonObject(&cdAttackerDetails));
                        pyArgs.add(gDLL->getPythonIFace()->makePythonObject(&cdDefenderDetails));
                        pyArgs.add(1);
                        pyArgs.add(iAttackerDamage);
						CvEventReporter::getInstance().genericEvent("combatLogHit", pyArgs.makeFunctionArgs());
                    }
				}
//FfH: End Modify

			}
		}
		else
		{
			if (pDefender->getCombatFirstStrikes() == 0)
			{
                if (pDefender->getDamage() + iDefenderDamage >= pDefender->maxHitPoints())
                {
                    if (!pPlot->isCity())
                    {
                        if (GC.getGameINLINE().getSorenRandNum(100, "Withdrawal") < pDefender->getWithdrawlProbDefensive())
						{
							// lfgr 09/2019: Added combatDefenderRetreat to BUG Combat Events
							CvEventReporter::getInstance().combatDefenderRetreat(this, pDefender);

                            pDefender->setFleeWithdrawl(true);
                            break;
                        }
                    }
                }
//FfH: End Add

				if (std::min(GC.getMAX_HIT_POINTS(), pDefender->getDamage() + iDefenderDamage) > combatLimit())
				{
					changeExperience(GC.defines.iEXPERIENCE_FROM_WITHDRAWL, pDefender->maxXPValue(), true, pPlot->getOwnerINLINE() == getOwnerINLINE(), !pDefender->isBarbarian());
					pDefender->setDamage(combatLimit(), getOwnerINLINE());
// BUG - Combat Events - start
					CvEventReporter::getInstance().combatWithdrawal(this, pDefender);
// BUG - Combat Events - end
//FfH: Added by Kael 05/27/2008
                    setMadeAttack(true);
                    changeMoves(std::max(GC.getMOVE_DENOMINATOR(), pPlot->movementCost(this, plot())));
					//FfH Promotions: Added by Kael 08/12/2007
                    setFleeWithdrawl(true);
					//FfH: End Add
//FfH: End Add

					break;
				}

				pDefender->changeDamage(iDefenderDamage, getOwnerINLINE());

				if (getCombatFirstStrikes() > 0 && isRanged())
				{
					kBattle.addFirstStrikes(BATTLE_UNIT_ATTACKER, 1);
					kBattle.addDamage(BATTLE_UNIT_DEFENDER, BATTLE_TIME_RANGED, iDefenderDamage);
				}

				cdDefenderDetails.iCurrHitPoints=pDefender->currHitPoints();

//FfH: Modified by Kael 08/02/2008
//				if (isHuman() || pDefender->isHuman())
//				{
//					CyArgsList pyArgs;
//					pyArgs.add(gDLL->getPythonIFace()->makePythonObject(&cdAttackerDetails));
//					pyArgs.add(gDLL->getPythonIFace()->makePythonObject(&cdDefenderDetails));
//					pyArgs.add(0);
//					pyArgs.add(iDefenderDamage);
//					CvEventReporter::getInstance().genericEvent("combatLogHit", pyArgs.makeFunctionArgs());
//				}
                if(GC.getUSE_COMBAT_RESULT_CALLBACK())
                {
                    if (isHuman() || pDefender->isHuman())
                    {
                        CyArgsList pyArgs;
                        pyArgs.add(gDLL->getPythonIFace()->makePythonObject(&cdAttackerDetails));
                        pyArgs.add(gDLL->getPythonIFace()->makePythonObject(&cdDefenderDetails));
                        pyArgs.add(0);
                        pyArgs.add(iDefenderDamage);
                        CvEventReporter::getInstance().genericEvent("combatLogHit", pyArgs.makeFunctionArgs());
                    }
				}
//FfH: End Modify

			}
		}

		if (getCombatFirstStrikes() > 0)
		{
			changeCombatFirstStrikes(-1);
		}

		if (pDefender->getCombatFirstStrikes() > 0)
		{
			pDefender->changeCombatFirstStrikes(-1);
		}

		if (isDead() || pDefender->isDead())
		{
			if (isDead())
			{
				int iExperience = defenseXPValue();
				if (iExperience > 0)
				{
					iExperience = ((iExperience * iAttackerStrength) / iDefenderStrength);
					iExperience = range(iExperience, GC.defines.iMIN_EXPERIENCE_PER_COMBAT, GC.defines.iMAX_EXPERIENCE_PER_COMBAT);
					pDefender->changeExperience(iExperience, maxXPValue(), true, pPlot->getOwnerINLINE() == pDefender->getOwnerINLINE(), !isBarbarian());
				}
			}
			else
			{
				flankingStrikeCombat(pPlot, iAttackerStrength, iAttackerFirepower, iAttackerKillOdds, iDefenderDamage, pDefender);

				int iExperience = pDefender->attackXPValue();
				if (iExperience > 0)
				{
					iExperience = ((iExperience * iDefenderStrength) / iAttackerStrength);
					iExperience = range(iExperience, GC.defines.iMIN_EXPERIENCE_PER_COMBAT, GC.defines.iMAX_EXPERIENCE_PER_COMBAT);
					changeExperience(iExperience, pDefender->maxXPValue(), true, pPlot->getOwnerINLINE() == getOwnerINLINE(), !pDefender->isBarbarian());
				}
			}

			break;
		}
	}
}


void CvUnit::updateCombat(bool bQuick)
{
	CvWString szBuffer;

	bool bFinish = false;
	bool bVisible = false;

	if (getCombatTimer() > 0)
	{
		changeCombatTimer(-1);

		if (getCombatTimer() > 0)
		{
			return;
		}
		else
		{
			bFinish = true;
		}
	}

	CvPlot* pPlot = getAttackPlot();

	if (pPlot == NULL)
	{
		return;
	}

	if (getDomainType() == DOMAIN_AIR)
	{
		updateAirStrike(pPlot, bQuick, bFinish);
		return;
	}

	CvUnit* pDefender = NULL;
	if (bFinish)
	{
		pDefender = getCombatUnit();
	}
	else
	{
		pDefender = pPlot->getBestDefender(NO_PLAYER, getOwnerINLINE(), this, true);
	}

	if (pDefender == NULL)
	{
		setAttackPlot(NULL, false);
		setCombatUnit(NULL);

		getGroup()->groupMove(pPlot, true, ((canAdvance(pPlot, 0)) ? this : NULL));

		getGroup()->clearMissionQueue();

		return;
	}

	//check if quick combat
	if (!bQuick)
	{
		bVisible = isCombatVisible(pDefender);
	}

	//FAssertMsg((pPlot == pDefender->plot()), "There is not expected to be a defender or the defender's plot is expected to be pPlot (the attack plot)");

//FfH: Added by Kael 07/30/2007
	if (pDefender->isFear())
	{
		if (!isImmuneToFear())
		{
			int iChance = baseCombatStr() + 20 + getLevel() - pDefender->baseCombatStr() - pDefender->getLevel();
			if (iChance < 4)
			{
				iChance = 4;
			}
			if (GC.getGameINLINE().getSorenRandNum(40, "Im afeared!") > iChance)
			{
				setMadeAttack(true);
				changeMoves(std::max(GC.getMOVE_DENOMINATOR(), pPlot->movementCost(this, plot())));
				szBuffer = gDLL->getText("TXT_KEY_MESSAGE_IM_AFEARED", getNameKey());
				// lfgr 01/2021: Force message to appear immediately
				gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)getOwner()), true, GC.defines.iEVENT_MESSAGE_TIME, szBuffer, "AS2D_DISCOVERBONUS",
						MESSAGE_TYPE_MAJOR_EVENT, "Art/Interface/Buttons/Promotions/Fear.dds", (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), getX_INLINE(), getY_INLINE(), true, true);
				bFinish = true;
				checkRemoveSelectionAfterAttack(); // lfgr 01/2021: Remove unit from selection if it can't attack again
			}
		}
	}
//FfH: End Add

	//if not finished and not fighting yet, set up combat damage and mission
	if (!bFinish)
	{
		if (!isFighting())
		{
			if (plot()->isFighting() || pPlot->isFighting())
			{
				return;
			}

			setMadeAttack(true);

			//rotate to face plot
			DirectionTypes newDirection = estimateDirection(this->plot(), pDefender->plot());
			if (newDirection != NO_DIRECTION)
			{
				setFacingDirection(newDirection);
			}

			//rotate enemy to face us
			newDirection = estimateDirection(pDefender->plot(), this->plot());
			if (newDirection != NO_DIRECTION)
			{
				pDefender->setFacingDirection(newDirection);
			}

			setCombatUnit(pDefender, true);
			pDefender->setCombatUnit(this, false);

		//FfH: Added by Kael 07/30/2007, moved here by Tholal
		    if (!isImmuneToDefensiveStrike())
		    {
				logBBAI("    %S (%d)checking for defensive strike against %S (%d)!", pDefender->getName().GetCString(), pDefender->getID(), getName().GetCString(), getID());
		        pDefender->doDefensiveStrike(this);
		    }
		//FfH: End Add


			pDefender->getGroup()->clearMissionQueue();

			bool bFocused = (bVisible && isCombatFocus() && gDLL->getInterfaceIFace()->isCombatFocus());

			if (bFocused)
			{
				DirectionTypes directionType = directionXY(plot(), pPlot);
				//								N			NE				E				SE					S				SW					W				NW
				NiPoint2 directions[8] = {NiPoint2(0, 1), NiPoint2(1, 1), NiPoint2(1, 0), NiPoint2(1, -1), NiPoint2(0, -1), NiPoint2(-1, -1), NiPoint2(-1, 0), NiPoint2(-1, 1)};
				NiPoint3 attackDirection = NiPoint3(directions[directionType].x, directions[directionType].y, 0);
				float plotSize = GC.getPLOT_SIZE();
				NiPoint3 lookAtPoint(plot()->getPoint().x + plotSize / 2 * attackDirection.x, plot()->getPoint().y + plotSize / 2 * attackDirection.y, (plot()->getPoint().z + pPlot->getPoint().z) / 2);
				attackDirection.Unitize();
				gDLL->getInterfaceIFace()->lookAt(lookAtPoint, (((getOwnerINLINE() != GC.getGameINLINE().getActivePlayer()) || gDLL->getGraphicOption(GRAPHICOPTION_NO_COMBAT_ZOOM)) ? CAMERALOOKAT_BATTLE : CAMERALOOKAT_BATTLE_ZOOM_IN), attackDirection);
			}
			else
			{
				PlayerTypes eAttacker = getVisualOwner(pDefender->getTeam());
				CvWString szMessage;
				if (BARBARIAN_PLAYER != eAttacker)
				{
					szMessage = gDLL->getText("TXT_KEY_MISC_YOU_UNITS_UNDER_ATTACK", GET_PLAYER(getOwnerINLINE()).getNameKey());
				}
				else
				{
					szMessage = gDLL->getText("TXT_KEY_MISC_YOU_UNITS_UNDER_ATTACK_UNKNOWN");
				}

				gDLL->getInterfaceIFace()->addMessage(pDefender->getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szMessage, "AS2D_COMBAT", MESSAGE_TYPE_DISPLAY_ONLY, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE(), true);
			}
		}

		FAssertMsg(pDefender != NULL, "Defender is not assigned a valid value");

		FAssertMsg(plot()->isFighting(), "Current unit instance plot is not fighting as expected");
		FAssertMsg(pPlot->isFighting(), "pPlot is not fighting as expected");

		if (!pDefender->canDefend())
		{
			if (!bVisible)
			{
				bFinish = true;
			}
			else
			{
				CvMissionDefinition kMission;
				kMission.setMissionTime(getCombatTimer() * gDLL->getSecsPerTurn());
				kMission.setMissionType(MISSION_SURRENDER);
				kMission.setUnit(BATTLE_UNIT_ATTACKER, this);
				kMission.setUnit(BATTLE_UNIT_DEFENDER, pDefender);
				kMission.setPlot(pPlot);
				gDLL->getEntityIFace()->AddMission(&kMission);

				// Surrender mission
				setCombatTimer(GC.getMissionInfo(MISSION_SURRENDER).getTime());

				GC.getGameINLINE().incrementTurnTimer(getCombatTimer());
			}

			// Kill them!
			pDefender->setDamage(GC.getMAX_HIT_POINTS());
		}
		else
		{
			CvBattleDefinition kBattle;
			kBattle.setUnit(BATTLE_UNIT_ATTACKER, this);
			kBattle.setUnit(BATTLE_UNIT_DEFENDER, pDefender);
			kBattle.setDamage(BATTLE_UNIT_ATTACKER, BATTLE_TIME_BEGIN, getDamage());
			kBattle.setDamage(BATTLE_UNIT_DEFENDER, BATTLE_TIME_BEGIN, pDefender->getDamage());

			resolveCombat(pDefender, pPlot, kBattle);

			if (!bVisible)
			{
				bFinish = true;
			}
			else
			{
				kBattle.setDamage(BATTLE_UNIT_ATTACKER, BATTLE_TIME_END, getDamage());
				kBattle.setDamage(BATTLE_UNIT_DEFENDER, BATTLE_TIME_END, pDefender->getDamage());
				kBattle.setAdvanceSquare(canAdvance(pPlot, 1));

				if (isRanged() && pDefender->isRanged())
				{
					kBattle.setDamage(BATTLE_UNIT_ATTACKER, BATTLE_TIME_RANGED, kBattle.getDamage(BATTLE_UNIT_ATTACKER, BATTLE_TIME_END));
					kBattle.setDamage(BATTLE_UNIT_DEFENDER, BATTLE_TIME_RANGED, kBattle.getDamage(BATTLE_UNIT_DEFENDER, BATTLE_TIME_END));
				}
				else
				{
					kBattle.addDamage(BATTLE_UNIT_ATTACKER, BATTLE_TIME_RANGED, kBattle.getDamage(BATTLE_UNIT_ATTACKER, BATTLE_TIME_BEGIN));
					kBattle.addDamage(BATTLE_UNIT_DEFENDER, BATTLE_TIME_RANGED, kBattle.getDamage(BATTLE_UNIT_DEFENDER, BATTLE_TIME_BEGIN));
				}

				int iTurns = planBattle( kBattle);
				kBattle.setMissionTime(iTurns * gDLL->getSecsPerTurn());
				setCombatTimer(iTurns);

				GC.getGameINLINE().incrementTurnTimer(getCombatTimer());

				if (pPlot->isActiveVisible(false))
				{
					ExecuteMove(0.5f, true);
					gDLL->getEntityIFace()->AddMission(&kBattle);
				}
			}
		}
	}

	if (bFinish)
	{
		if (bVisible)
		{
			if (isCombatFocus() && gDLL->getInterfaceIFace()->isCombatFocus())
			{
				if (getOwnerINLINE() == GC.getGameINLINE().getActivePlayer())
				{
					gDLL->getInterfaceIFace()->releaseLockedCamera();
				}
			}
		}

		//end the combat mission if this code executes first
		gDLL->getEntityIFace()->RemoveUnitFromBattle(this);
		gDLL->getEntityIFace()->RemoveUnitFromBattle(pDefender);
		setAttackPlot(NULL, false);
		setCombatUnit(NULL);
		pDefender->setCombatUnit(NULL);
		NotifyEntity(MISSION_DAMAGE);
		pDefender->NotifyEntity(MISSION_DAMAGE);

		// Bugfix: Defenders that flee can be killed after combat
		bool pDefenderCannotFlee = false;
		if (pDefender->isFleeWithdrawl())
		{
			pDefender->joinGroup(NULL);
			pDefenderCannotFlee = !pDefender->withdrawlToNearestValidPlot(false); // LFGR_TODO: bDefenderCannotFlee
		}
		// Bugfix end

		if (isDead())
		{
			if (isBarbarian())
			{
				GET_PLAYER(pDefender->getOwnerINLINE()).changeWinsVsBarbs(1);
			}

//FfH Hidden Nationality: Modified by Kael 08/27/2007
//			if (!m_pUnitInfo->isHiddenNationality() && !pDefender->getUnitInfo().isHiddenNationality())
			if (!isHiddenNationality() && !pDefender->isHiddenNationality() && getDuration() == 0 && !m_pUnitInfo->isNoWarWeariness())
//FfH: End Modify

			{
				GET_TEAM(getTeam()).changeWarWeariness(pDefender->getTeam(), *pPlot, GC.defines.iWW_UNIT_KILLED_ATTACKING);
				GET_TEAM(pDefender->getTeam()).changeWarWeariness(getTeam(), *pPlot, GC.defines.iWW_KILLED_UNIT_DEFENDING);
				GET_TEAM(pDefender->getTeam()).AI_changeWarSuccess(getTeam(), GC.defines.iWAR_SUCCESS_DEFENDING);
			}

			if (getCaptureUnitType(GET_PLAYER(pDefender->getOwner()).getCivilizationType()) == NO_UNIT || isHiddenNationality())
			{
				szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_UNIT_DIED_ATTACKING", getNameKey(), pDefender->getNameKey());
				gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, GC.getEraInfo(GC.getGameINLINE().getCurrentEra()).getAudioUnitDefeatScript(), MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
				if (isHiddenNationality())
				{
					szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_KILLED_ENEMY_UNIT_HN", pDefender->getNameKey(), getNameKey());
				}
				else
				{
					szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_KILLED_ENEMY_UNIT", pDefender->getNameKey(), getNameKey(), getVisualCivAdjective(pDefender->getTeam()));
				}
				gDLL->getInterfaceIFace()->addMessage(pDefender->getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, GC.getEraInfo(GC.getGameINLINE().getCurrentEra()).getAudioUnitVictoryScript(), MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
			}

//FfH: Added by Kael 07/30/2007
            pDefender->combatWon(this, false);
//FfH: End Add

			// report event to Python, along with some other key state

//FfH: Modified by Kael 08/02/2008
//			CvEventReporter::getInstance().combatResult(pDefender, this);
            if(GC.getUSE_COMBAT_RESULT_CALLBACK())
            {
				CvEventReporter::getInstance().combatResult(pDefender, this);
            }
//FfH: End Modify

		}
		else if (pDefenderCannotFlee || pDefender->isDead())
		{
			if (pDefender->isBarbarian())
			{
				GET_PLAYER(getOwnerINLINE()).changeWinsVsBarbs(1);
			}

//FfH Hidden Nationality: Modified by Kael 08/27/2007
//			if (!m_pUnitInfo->isHiddenNationality() && !pDefender->getUnitInfo().isHiddenNationality())
			if (!isHiddenNationality() && !pDefender->isHiddenNationality() && pDefender->getDuration() == 0 && !pDefender->getUnitInfo().isNoWarWeariness())
//FfH: End Modify

			{
				GET_TEAM(pDefender->getTeam()).changeWarWeariness(getTeam(), *pPlot, GC.defines.iWW_UNIT_KILLED_DEFENDING);
				GET_TEAM(getTeam()).changeWarWeariness(pDefender->getTeam(), *pPlot, GC.defines.iWW_KILLED_UNIT_ATTACKING);
				GET_TEAM(getTeam()).AI_changeWarSuccess(pDefender->getTeam(), GC.defines.iWAR_SUCCESS_ATTACKING);
			}

			if (pDefender->getCaptureUnitType(GET_PLAYER(getOwnerINLINE()).getCivilizationType()) == NO_UNIT || isHiddenNationality())
			{
				szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_UNIT_DESTROYED_ENEMY", getNameKey(), pDefender->getNameKey());
				gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, GC.getEraInfo(GC.getGameINLINE().getCurrentEra()).getAudioUnitVictoryScript(), MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
				if (getVisualOwner(pDefender->getTeam()) != getOwnerINLINE())
				{
					szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_UNIT_WAS_DESTROYED_UNKNOWN", pDefender->getNameKey(), getNameKey());
				}
				else if (isHiddenNationality())
				{
					szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_UNIT_WAS_DESTROYED_HN", pDefender->getNameKey(), getNameKey());
				}
				else
				{
					szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_UNIT_WAS_DESTROYED", pDefender->getNameKey(), getNameKey(), getVisualCivAdjective(pDefender->getTeam()));
				}
				gDLL->getInterfaceIFace()->addMessage(pDefender->getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer,GC.getEraInfo(GC.getGameINLINE().getCurrentEra()).getAudioUnitDefeatScript(), MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
			}

//FfH: Added by Kael 05/15/2007
            combatWon(pDefender, true);
//FfH: End Add

			// report event to Python, along with some other key state

//FfH: Modified by Kael 08/02/2008
//			CvEventReporter::getInstance().combatResult(this, pDefender);
            if(GC.getUSE_COMBAT_RESULT_CALLBACK())
            {
				CvEventReporter::getInstance().combatResult(this, pDefender);
            }
//FfH: End Modify

			bool bAdvance = false;

			if (isSuicide())
			{
				logBBAI("    Killing %S (delayed) -- performed suicide attack (Unit %d - plot: %d, %d)",
						getName().GetCString(), getID(), getX(), getY());
				kill(true);
				
				logBBAI("    Killing %S -- slain by suicide attack (Unit %d - plot: %d, %d)",
					pDefender->getName().GetCString(), pDefender->getID(), pDefender->getX(), pDefender->getY());
				pDefender->kill(false);
				pDefender = NULL;
			}
			else
			{
				bAdvance = canAdvance(pPlot, ((pDefender->canDefend()) ? 1 : 0));

				if (bAdvance)
				{
					if (!isNoCapture()

//FfH: Added by Kael 11/14/2007
					 || GC.getUnitInfo((UnitTypes)pDefender->getUnitType()).getEquipmentPromotion() != NO_PROMOTION
//FfH: End Add

					 )
					{
						pDefender->setCapturingPlayer(getOwnerINLINE());
					}
				}
				
				logBBAI("    Killing %S -- slain by attack (Unit %d - plot: %d, %d)",
					pDefender->getName().GetCString(), pDefender->getID(), pDefender->getX(), pDefender->getY());
				pDefender->kill(false);
				pDefender = NULL;

//FfH Fear: Added by Kael 07/30/2007
                if (isFear() && pPlot->isCity() == false)
                {
                    CvUnit* pLoopUnit;
                    CLLNode<IDInfo>* pUnitNode;
                    pUnitNode = pPlot->headUnitNode();
                    while (pUnitNode != NULL)
                    {
                        pLoopUnit = ::getUnit(pUnitNode->m_data);
                        pUnitNode = pPlot->nextUnitNode(pUnitNode);
                        if (pLoopUnit->isEnemy(getTeam()))
                        {
							if (!pLoopUnit->isImmuneToFear() && !pLoopUnit->isCargo())
                            {
                                if (GC.getGameINLINE().getSorenRandNum(20, "Im afeared!") <= (baseCombatStr() + 10 - pLoopUnit->baseCombatStr()))
                                {
                                    pLoopUnit->joinGroup(NULL);
                                    pLoopUnit->withdrawlToNearestValidPlot();
                                }
                            }
                        }
                    }
                }
                bAdvance = canAdvance(pPlot, 0);
//FfH: End Add

				if (!bAdvance)
				{
					changeMoves(std::max(GC.getMOVE_DENOMINATOR(), pPlot->movementCost(this, plot())));
					checkRemoveSelectionAfterAttack();
				}
			}

			if (pPlot->getNumVisibleEnemyDefenders(this) == 0)
			{
				if( !atPlot( pPlot ) ) { // Unit might have already fled to this plot when it became visible after combat
					getGroup()->groupMove(pPlot, true, ((bAdvance) ? this : NULL));
				}
			}

			// This is is put before the plot advancement, the unit will always try to walk back
			// to the square that they came from, before advancing.
			getGroup()->clearMissionQueue();
		}
		else
		{

//FfH Promotions: Modified by Kael 08/12/2007
//			szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_UNIT_WITHDRAW", getNameKey(), pDefender->getNameKey());
//			gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_OUR_WITHDRAWL", MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
//			szBuffer = gDLL->getText("TXT_KEY_MISC_ENEMY_UNIT_WITHDRAW", getNameKey(), pDefender->getNameKey());
//			gDLL->getInterfaceIFace()->addMessage(pDefender->getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_THEIR_WITHDRAWL", MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
//
//			changeMoves(std::max(GC.getMOVE_DENOMINATOR(), pPlot->movementCost(this, plot())));
//			checkRemoveSelectionAfterAttack();
//
//			getGroup()->clearMissionQueue();
            if (pDefender->isFleeWithdrawl())
            {
				// Bugfix: Defenders that flee can be killed after combat
                // pDefender->joinGroup(NULL);
                pDefender->setFleeWithdrawl(false);
                // pDefender->withdrawlToNearestValidPlot();
				// Bugfix end

//>>>>BUGFfH: Modified by Denev 10/14/2009 (0.41k)
/*	When defender fleed, attacker loses movement point as same as wining	*/
/*
				checkRemoveSelectionAfterAttack();
				if (pPlot->getNumVisibleEnemyDefenders(this) == 0)
				{
					getGroup()->groupMove(pPlot, true, ((canAdvance(pPlot, 0)) ? this : NULL));
				}
*/
				if (canAdvance(pPlot, 0))
				{
					getGroup()->groupMove(pPlot, true, this);
				}
				else
				{
					changeMoves(std::max(GC.getMOVE_DENOMINATOR(), pPlot->movementCost(this, plot())));
					checkRemoveSelectionAfterAttack();
				}
//<<<<BUGFfH: End Modify

                getGroup()->clearMissionQueue();
                szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_UNIT_FLED", pDefender->getNameKey(), getNameKey());
                gDLL->getInterfaceIFace()->addMessage(pDefender->getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_OUR_WITHDRAWL", MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
                szBuffer = gDLL->getText("TXT_KEY_MISC_ENEMY_UNIT_FLED", pDefender->getNameKey(), getNameKey());
                gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_THEIR_WITHDRAWL", MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE());

				logBBAI("    %S withdraws from combat! (Unit %d - plot: %d, %d)", pDefender->getName().GetCString(), pDefender->getID(), pDefender->getX(), pDefender->getY());
            }
            if (isFleeWithdrawl())
            {
                joinGroup(NULL);
                setFleeWithdrawl(false);
                szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_UNIT_WITHDRAW", getNameKey(), pDefender->getNameKey());
                gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_OUR_WITHDRAWL", MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
                szBuffer = gDLL->getText("TXT_KEY_MISC_ENEMY_UNIT_WITHDRAW", getNameKey(), pDefender->getNameKey());
                gDLL->getInterfaceIFace()->addMessage(pDefender->getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_THEIR_WITHDRAWL", MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
                changeMoves(std::max(GC.getMOVE_DENOMINATOR(), pPlot->movementCost(this, plot())));
                checkRemoveSelectionAfterAttack();
                getGroup()->clearMissionQueue();

				logBBAI("    %S withdraws from combat! (Unit %d - plot: %d, %d)", getName().GetCString(), getID(), getX(), getY());
            }
//FfH: End Modify

		}
	}
}

void CvUnit::checkRemoveSelectionAfterAttack()
{
	if (!canMove() || !isBlitz())
	{
		if (IsSelected())
		{
			if (gDLL->getInterfaceIFace()->getLengthSelectionList() > 1)
			{
				gDLL->getInterfaceIFace()->removeFromSelectionList(this);
			}
		}
	}
}


bool CvUnit::isActionRecommended(int iAction)
{
	CvCity* pWorkingCity;
	CvPlot* pPlot;
	ImprovementTypes eImprovement;
	ImprovementTypes eFinalImprovement;
	BuildTypes eBuild;
	RouteTypes eRoute;
	BonusTypes eBonus;
	int iIndex;

	if (getOwnerINLINE() != GC.getGameINLINE().getActivePlayer())
	{
		return false;
	}

	if (GET_PLAYER(getOwnerINLINE()).isOption(PLAYEROPTION_NO_UNIT_RECOMMENDATIONS))
	{
		return false;
	}

	CyUnit* pyUnit = new CyUnit(this);
	CyArgsList argsList;
	argsList.add(gDLL->getPythonIFace()->makePythonObject(pyUnit));	// pass in unit class
	argsList.add(iAction);
	long lResult=0;
	gDLL->getPythonIFace()->callFunction(PYGameModule, "isActionRecommended", argsList.makeFunctionArgs(), &lResult);
	delete pyUnit;	// python fxn must not hold on to this pointer
	if (lResult == 1)
	{
		return true;
	}

	pPlot = gDLL->getInterfaceIFace()->getGotoPlot();

	if (pPlot == NULL)
	{
		if (gDLL->shiftKey())
		{
			pPlot = getGroup()->lastMissionPlot();
		}
	}

	if (pPlot == NULL)
	{
		pPlot = plot();
	}

// BUFFY - Don't Recommend Actions in Fog of War - start
#ifdef _BUFFY
	// from HOF Mod - Denniz
	if (!pPlot->isVisible(GC.getGameINLINE().getActiveTeam(), false))
	{
		return false;
	}
#endif
// BUFFY - Don't Recommend Actions in Fog of War - end

	if (GC.getActionInfo(iAction).getMissionType() == MISSION_FORTIFY)
	{
		if (pPlot->isCity(true, getTeam()))
		{
			if (canDefend(pPlot))
			{
				if (pPlot->getNumDefenders(getOwnerINLINE()) < ((atPlot(pPlot)) ? 2 : 1))
				{
					return true;
				}
			}
		}
	}

	if (GC.getActionInfo(iAction).getMissionType() == MISSION_HEAL)
	{
		if (isHurt())
		{
			if (!hasMoved())
			{
				if ((pPlot->getTeam() == getTeam()) || (healTurns(pPlot) < 4))
				{
					return true;
				}
			}
		}
	}

	if (GC.getActionInfo(iAction).getMissionType() == MISSION_FOUND)
	{
		if (canFound(pPlot))
		{
			if (pPlot->isBestAdjacentFound(getOwnerINLINE()))
			{
				return true;
			}
		}
	}

	if (GC.getActionInfo(iAction).getMissionType() == MISSION_BUILD)
	{
		if (pPlot->getOwnerINLINE() == getOwnerINLINE())
		{
			eBuild = ((BuildTypes)(GC.getActionInfo(iAction).getMissionData()));
			FAssert(eBuild != NO_BUILD);
			FAssertMsg(eBuild < GC.getNumBuildInfos(), "Invalid Build");

			if (canBuild(pPlot, eBuild))
			{
				eImprovement = ((ImprovementTypes)(GC.getBuildInfo(eBuild).getImprovement()));
				eRoute = ((RouteTypes)(GC.getBuildInfo(eBuild).getRoute()));
				eBonus = pPlot->getBonusType(getTeam());
				pWorkingCity = pPlot->getWorkingCity();

				if (pPlot->getImprovementType() == NO_IMPROVEMENT)
				{
					if (pWorkingCity != NULL)
					{
						iIndex = pWorkingCity->getCityPlotIndex(pPlot);

						if (iIndex != -1)
						{
							if (pWorkingCity->AI_getBestBuild(iIndex) == eBuild)
							{
								return true;
							}
						}
					}

					if (eImprovement != NO_IMPROVEMENT)
					{
						if (eBonus != NO_BONUS)
						{
							if (GC.getImprovementInfo(eImprovement).isImprovementBonusTrade(eBonus))
							{
								return true;
							}
						}

						if (pPlot->getImprovementType() == NO_IMPROVEMENT)
						{
							if (!(pPlot->isIrrigated()) && pPlot->isIrrigationAvailable(true))
							{
								if (GC.getImprovementInfo(eImprovement).isCarriesIrrigation())
								{
									return true;
								}
							}

							if (pWorkingCity != NULL)
							{
								if (GC.getImprovementInfo(eImprovement).getYieldChange(YIELD_FOOD) > 0)
								{
									return true;
								}

								if (pPlot->isHills())
								{
									if (GC.getImprovementInfo(eImprovement).getYieldChange(YIELD_PRODUCTION) > 0)
									{
										return true;
									}
								}
								else
								{
									if (GC.getImprovementInfo(eImprovement).getYieldChange(YIELD_COMMERCE) > 0)
									{
										return true;
									}
								}
							}
						}
					}
				}

				if (eRoute != NO_ROUTE)
				{
					if (!(pPlot->isRoute()))
					{
						if (eBonus != NO_BONUS)
						{
							return true;
						}

						if (pWorkingCity != NULL)
						{
							if (pPlot->isRiver())
							{
								return true;
							}
						}
					}

					eFinalImprovement = eImprovement;

					if (eFinalImprovement == NO_IMPROVEMENT)
					{
						eFinalImprovement = pPlot->getImprovementType();
					}

					if (eFinalImprovement != NO_IMPROVEMENT)
					{
						if ((GC.getImprovementInfo(eFinalImprovement).getRouteYieldChanges(eRoute, YIELD_FOOD) > 0) ||
							(GC.getImprovementInfo(eFinalImprovement).getRouteYieldChanges(eRoute, YIELD_PRODUCTION) > 0) ||
							(GC.getImprovementInfo(eFinalImprovement).getRouteYieldChanges(eRoute, YIELD_COMMERCE) > 0))
						{
							return true;
						}
					}
				}
			}
		}
	}

	if (GC.getActionInfo(iAction).getCommandType() == COMMAND_PROMOTION)
	{
		return true;
	}

	return false;
}


bool CvUnit::isBetterDefenderThan(const CvUnit* pDefender, const CvUnit* pAttacker) const
{
	int iOurDefense;
	int iTheirDefense;

	if (pDefender == NULL)
	{
		return true;
	}

	TeamTypes eAttackerTeam = NO_TEAM;
	if (NULL != pAttacker)
	{
		eAttackerTeam = pAttacker->getTeam();
	}

	if (canCoexistWithEnemyUnit(eAttackerTeam))
	{
		return false;
	}

	if (!canDefend())
	{
		return false;
	}

	if (canDefend() && !(pDefender->canDefend()))
	{
		return true;
	}

	if (pAttacker)
	{
		if (isTargetOf(*pAttacker) && !pDefender->isTargetOf(*pAttacker))
		{
			return true;
		}

		if (!isTargetOf(*pAttacker) && pDefender->isTargetOf(*pAttacker))
		{
			return false;
		}

		if (pAttacker->canAttack(*pDefender) && !pAttacker->canAttack(*this))
		{
			return false;
		}

		if (pAttacker->canAttack(*this) && !pAttacker->canAttack(*pDefender))
		{
			return true;
		}
	}

	iOurDefense = currCombatStr(plot(), pAttacker);
	if (::isWorldUnitClass(getUnitClassType()))
	{
		iOurDefense /= 2;
	}

	if (NULL == pAttacker)
	{
		if (pDefender->collateralDamage() > 0)
		{
			iOurDefense *= (100 + pDefender->collateralDamage());
			iOurDefense /= 100;
		}

		if (pDefender->currInterceptionProbability() > 0)
		{
			iOurDefense *= (100 + pDefender->currInterceptionProbability());
			iOurDefense /= 100;
		}
	}
	else
	{
		if (!(pAttacker->immuneToFirstStrikes()))
		{
			iOurDefense *= ((((firstStrikes() * 2) + chanceFirstStrikes()) * ((GC.defines.iCOMBAT_DAMAGE * 2) / 5)) + 100);
			iOurDefense /= 100;
		}

		if (immuneToFirstStrikes())
		{
			iOurDefense *= ((((pAttacker->firstStrikes() * 2) + pAttacker->chanceFirstStrikes()) * ((GC.defines.iCOMBAT_DAMAGE * 2) / 5)) + 100);
			iOurDefense /= 100;
		}
	}

	int iAssetValue = std::max(1, getUnitInfo().getAssetValue());
	int iCargoAssetValue = 0;
	std::vector<CvUnit*> aCargoUnits;
	getCargoUnits(aCargoUnits);
	for (uint i = 0; i < aCargoUnits.size(); ++i)
	{
		iCargoAssetValue += aCargoUnits[i]->getUnitInfo().getAssetValue();
	}
	iOurDefense = iOurDefense * iAssetValue / std::max(1, iAssetValue + iCargoAssetValue);

	iTheirDefense = pDefender->currCombatStr(plot(), pAttacker);
	if (::isWorldUnitClass(pDefender->getUnitClassType()))
	{
		iTheirDefense /= 2;
	}

	if (NULL == pAttacker)
	{
		if (collateralDamage() > 0)
		{
			iTheirDefense *= (100 + collateralDamage());
			iTheirDefense /= 100;
		}

		if (currInterceptionProbability() > 0)
		{
			iTheirDefense *= (100 + currInterceptionProbability());
			iTheirDefense /= 100;
		}
	}
	else
	{
		if (!(pAttacker->immuneToFirstStrikes()))
		{
			iTheirDefense *= ((((pDefender->firstStrikes() * 2) + pDefender->chanceFirstStrikes()) * ((GC.defines.iCOMBAT_DAMAGE * 2) / 5)) + 100);
			iTheirDefense /= 100;
		}

		if (pDefender->immuneToFirstStrikes())
		{
			iTheirDefense *= ((((pAttacker->firstStrikes() * 2) + pAttacker->chanceFirstStrikes()) * ((GC.defines.iCOMBAT_DAMAGE * 2) / 5)) + 100);
			iTheirDefense /= 100;
		}
	}

	iAssetValue = std::max(1, pDefender->getUnitInfo().getAssetValue());
	iCargoAssetValue = 0;
	pDefender->getCargoUnits(aCargoUnits);
	for (uint i = 0; i < aCargoUnits.size(); ++i)
	{
		iCargoAssetValue += aCargoUnits[i]->getUnitInfo().getAssetValue();
	}
	iTheirDefense = iTheirDefense * iAssetValue / std::max(1, iAssetValue + iCargoAssetValue);

//FfH Promotions: Added by Kael 07/30/2007
    iOurDefense *= getBetterDefenderThanPercent();
    iOurDefense /= 100;
    iTheirDefense *= pDefender->getBetterDefenderThanPercent();
    iTheirDefense /= 100;
//FfH Promotions: End Add

	if (iOurDefense == iTheirDefense)
	{
		if (NO_UNIT == getLeaderUnitType() && NO_UNIT != pDefender->getLeaderUnitType())
		{
			++iOurDefense;
		}
		else if (NO_UNIT != getLeaderUnitType() && NO_UNIT == pDefender->getLeaderUnitType())
		{
			++iTheirDefense;
		}
		else if (isBeforeUnitCycle(this, pDefender))
		{
			++iOurDefense;
		}
	}

	return (iOurDefense > iTheirDefense);
}


bool CvUnit::canDoCommand(CommandTypes eCommand, int iData1, int iData2, bool bTestVisible, bool bTestBusy)
{
	CvUnit* pUnit;

	if (bTestBusy && getGroup()->isBusy())
	{
		return false;
	}

	switch (eCommand)
	{
	case COMMAND_PROMOTION:
		if (canPromote((PromotionTypes)iData1, iData2))
		{
			return true;
		}
		break;

	case COMMAND_UPGRADE:
		if (canUpgrade(((UnitTypes)iData1), bTestVisible))
		{
			return true;
		}
		break;

	case COMMAND_AUTOMATE:
		if (canAutomate((AutomateTypes)iData1))
		{
			return true;
		}
		break;

	case COMMAND_WAKE:
		if (!isAutomated() && isWaiting())
		{
			return true;
		}
		break;

	case COMMAND_CANCEL:
	case COMMAND_CANCEL_ALL:
		if (!isAutomated() && (getGroup()->getLengthMissionQueue() > 0))
		{
			return true;
		}
		break;

	case COMMAND_STOP_AUTOMATION:
		if (isAutomated())
		{
			return true;
		}
		break;

	case COMMAND_DELETE:
		if (canScrap())
		{
			return true;
		}
		break;

	case COMMAND_GIFT:
		if (canGift(bTestVisible))
		{
			return true;
		}
		break;

	case COMMAND_LOAD:
		if (canLoad(plot()))
		{
			return true;
		}
		break;

	case COMMAND_LOAD_UNIT:
		pUnit = ::getUnit(IDInfo(((PlayerTypes)iData1), iData2));
		if (pUnit != NULL)
		{
			if (canLoadUnit(pUnit, plot()))
			{
				return true;
			}
		}
		break;

	case COMMAND_UNLOAD:
		if (canUnload())
		{
			return true;
		}
		break;

	case COMMAND_UNLOAD_ALL:
		if (canUnloadAll())
		{
			return true;
		}
		break;

	case COMMAND_HOTKEY:
		if (isGroupHead())
		{
			return true;
		}
		break;

//FfH Spell System: Added by Kael 07/23/2007
	case COMMAND_CAST:{
		if(canCast(iData1, bTestVisible))
		{
			return true;
		}
		break;
	}
//FfH: End Add

	default:
		FAssert(false);
		break;
	}

	return false;
}


void CvUnit::doCommand(CommandTypes eCommand, int iData1, int iData2)
{
	CvUnit* pUnit;
	bool bCycle;

	bCycle = false;

	FAssert(getOwnerINLINE() != NO_PLAYER);

	if (canDoCommand(eCommand, iData1, iData2))
	{
		switch (eCommand)
		{
		case COMMAND_PROMOTION:
			promote((PromotionTypes)iData1, iData2);
			break;

		case COMMAND_UPGRADE:
			upgrade((UnitTypes)iData1);
			bCycle = true;
			break;

		case COMMAND_AUTOMATE:
			automate((AutomateTypes)iData1);
			bCycle = true;
			break;

		case COMMAND_WAKE:
			getGroup()->setActivityType(ACTIVITY_AWAKE);
			break;

		case COMMAND_CANCEL:
			getGroup()->popMission();
			break;

		case COMMAND_CANCEL_ALL:
			getGroup()->clearMissionQueue();
			break;

		case COMMAND_STOP_AUTOMATION:
			getGroup()->setAutomateType(NO_AUTOMATE);
			break;

		case COMMAND_DELETE:
			scrap();
			bCycle = true;
			break;

		case COMMAND_GIFT:
			gift();
			bCycle = true;
			break;

		case COMMAND_LOAD:
			load();
			bCycle = true;
			break;

		case COMMAND_LOAD_UNIT:
			pUnit = ::getUnit(IDInfo(((PlayerTypes)iData1), iData2));
			if (pUnit != NULL)
			{
				loadUnit(pUnit);
				bCycle = true;
			}
			break;

		case COMMAND_UNLOAD:
			unload();
			bCycle = true;
			break;

		case COMMAND_UNLOAD_ALL:
			unloadAll();
			bCycle = true;
			break;

		case COMMAND_HOTKEY:
			setHotKeyNumber(iData1);
			break;

//FfH Spell System: Added by Kael 07/23/2007
		case COMMAND_CAST:{
			cast(iData1);
			break;
		}
//FfH: End Add

		default:
			FAssert(false);
			break;
		}
	}

	if (bCycle)
	{
		if (IsSelected())
		{
			gDLL->getInterfaceIFace()->setCycleSelectionCounter(1);
		}
	}

	if (!isDead() && isDelayedDeath())
	{
		getGroup()->doDelayedDeath();
	}
}


FAStarNode* CvUnit::getPathLastNode() const
{
	return getGroup()->getPathLastNode();
}


CvPlot* CvUnit::getPathEndTurnPlot() const
{
	return getGroup()->getPathEndTurnPlot();
}


bool CvUnit::generatePath(const CvPlot* pToPlot, int iFlags, bool bReuse, int* piPathTurns) const
{
	return getGroup()->generatePath(plot(), pToPlot, iFlags, bReuse, piPathTurns);
}


bool CvUnit::canEnterTerritory(TeamTypes eTeam, bool bIgnoreRightOfPassage) const
{
	if (GET_TEAM(getTeam()).isFriendlyTerritory(eTeam))
	{
		return true;
	}

	if (eTeam == NO_TEAM)
	{
		return true;
	}

	if (isEnemy(eTeam))
	{
		return true;
	}

	if (isRivalTerritory())
	{
		return true;
	}

	if (alwaysInvisible())
	{
		return true;
	}

	if (!bIgnoreRightOfPassage)
	{
		if (GET_TEAM(getTeam()).isOpenBorders(eTeam))
		{
			return true;
		}
/************************************************************************************************/
/* Afforess	                  Start		 08/01/10                                               */
/* Advanced Diplomacy                                                                           */
/************************************************************************************************/
		if (GET_TEAM(getTeam()).isLimitedBorders(eTeam))
		{
			if (canMoveLimitedBorders())
			{
				return true;
			}
		}
/************************************************************************************************/
/* Afforess	                     END                                                            */
/************************************************************************************************/
	}

//FfH: Added by Kael 09/02/2007 (so hidden nationality units can enter all territories)
    if (isHiddenNationality())
    {
        return true;
    }
    if (GET_TEAM(eTeam).isBarbarian()) // (so barbarians can enter player areas they are at peace with an vice versa)
    {
        return true;
    }
    if (GET_TEAM(getTeam()).isBarbarian())
    {
        return true;
    }
    if (GET_PLAYER(getOwnerINLINE()).isDeclaringWar())
    {
        if (GET_PLAYER(getOwnerINLINE()).getStateReligion() != NO_RELIGION)
        {
            if (GC.getReligionInfo(GET_PLAYER(getOwnerINLINE()).getStateReligion()).isSneakAttack())
            {
                return true;
            }
        }
    }
//FfH: End Add

	return false;
}


bool CvUnit::canEnterArea(TeamTypes eTeam, const CvArea* pArea, bool bIgnoreRightOfPassage) const
{
	if (!canEnterTerritory(eTeam, bIgnoreRightOfPassage))
	{
		return false;
	}

	if (isBarbarian() && DOMAIN_LAND == getDomainType())
	{
		if (eTeam != NO_TEAM && eTeam != getTeam())
		{
			if (pArea && pArea->isBorderObstacle(eTeam))
			{
				return false;
			}
		}
	}

	return true;
}


// Returns the ID of the team to declare war against
TeamTypes CvUnit::getDeclareWarMove(const CvPlot* pPlot) const
{
	CvUnit* pUnit;
	TeamTypes eRevealedTeam;

	FAssert(isHuman());

	if (getDomainType() != DOMAIN_AIR)
	{
		eRevealedTeam = pPlot->getRevealedTeam(getTeam(), false);

		if (eRevealedTeam != NO_TEAM)
		{
			if (!canEnterArea(eRevealedTeam, pPlot->area()) || (getDomainType() == DOMAIN_SEA && !canCargoEnterArea(eRevealedTeam, pPlot->area(), false) && getGroup()->isAmphibPlot(pPlot)))
			{

//FfH: Modified by Kael 03/29/2009
//				if (GET_TEAM(getTeam()).canDeclareWar(pPlot->getTeam()))
				if (isAlwaysHostile(pPlot) || GET_TEAM(getTeam()).canDeclareWar(pPlot->getTeam()))
//FfH: End Modify

				{
					return eRevealedTeam;
				}
			}
		}
		else
		{
			if (pPlot->isActiveVisible(false))
			{
				//if (canMoveInto(pPlot, true, true, true))
				if (canMoveInto(pPlot, true, true, true) && !canMoveInto(pPlot))
				{
					pUnit = pPlot->plotCheck(PUF_canDeclareWar, getOwnerINLINE(), isAlwaysHostile(pPlot), NO_PLAYER, NO_TEAM, PUF_isVisible, getOwnerINLINE());

					if (pUnit != NULL)
					{
						return pUnit->getTeam();
					}
				}
			}
		}
	}

	return NO_TEAM;
}

bool CvUnit::willRevealByMove(const CvPlot* pPlot) const
{
	int iRange = visibilityRange() + 1;
	for (int i = -iRange; i <= iRange; ++i)
	{
		for (int j = -iRange; j <= iRange; ++j)
		{
			CvPlot* pLoopPlot = ::plotXY(pPlot->getX_INLINE(), pPlot->getY_INLINE(), i, j);
			if (NULL != pLoopPlot)
			{
				if (!pLoopPlot->isRevealed(getTeam(), false) && pPlot->canSeePlot(pLoopPlot, getTeam(), visibilityRange(), NO_DIRECTION))
				{
					return true;
				}
			}
		}
	}

	return false;
}

bool CvUnit::canMoveInto(const CvPlot* pPlot, bool bAttack, bool bDeclareWar, bool bIgnoreLoad) const
{
	PROFILE_FUNC();

	FAssertMsg(pPlot != NULL, "Plot is not assigned a valid value");

	if (atPlot(pPlot))
	{
		return false;
	}

	if (pPlot->isImpassable())
	{
		if (!canMoveImpassable())
		{
			return false;
		}
	}

	// Cannot move around in unrevealed land freely
	if (m_pUnitInfo->isNoRevealMap() && willRevealByMove(pPlot))
	{
		return false;
	}

	// lfgr 11/2022: Barbarian Animal AI units can never enter foreign (non-barbarian) cities
	if (isBarbarian() && AI_getUnitAIType() == UNITAI_ANIMAL && pPlot->isCity() && pPlot->getOwnerINLINE() != getOwnerINLINE())
	{
		return false;
	}

	if (GC.getUSE_SPIES_NO_ENTER_BORDERS())
	{
		if (isSpy() && NO_PLAYER != pPlot->getOwnerINLINE())
		{
			if (!GET_PLAYER(getOwnerINLINE()).canSpiesEnterBorders(pPlot->getOwnerINLINE()))
			{
				return false;
			}
		}
	}

	CvArea *pPlotArea = pPlot->area();
	TeamTypes ePlotTeam = pPlot->getTeam();
	bool bCanEnterArea = canEnterArea(ePlotTeam, pPlotArea);
	if (bCanEnterArea)
	{
		if (pPlot->getFeatureType() != NO_FEATURE)
		{
			if (m_pUnitInfo->getFeatureImpassable(pPlot->getFeatureType()))
			{
				TechTypes eTech = (TechTypes)m_pUnitInfo->getFeaturePassableTech(pPlot->getFeatureType());
				if (NO_TECH == eTech || !GET_TEAM(getTeam()).isHasTech(eTech))
				{
					if (DOMAIN_SEA != getDomainType() || pPlot->getTeam() != getTeam())  // sea units can enter impassable in own cultural borders
					{
						return false;
					}
				}
			}
		}
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       09/17/09                         TC01 & jdog5000      */
/*                                                                                              */
/* Bugfix				                                                                        */
/************************************************************************************************/
/* original bts code
		else
*/
		// always check terrain also
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
		{
			if (m_pUnitInfo->getTerrainImpassable(pPlot->getTerrainType()))
			{
				TechTypes eTech = (TechTypes)m_pUnitInfo->getTerrainPassableTech(pPlot->getTerrainType());
				if (NO_TECH == eTech || !GET_TEAM(getTeam()).isHasTech(eTech))
				{
					if (DOMAIN_SEA != getDomainType() || pPlot->getTeam() != getTeam())  // sea units can enter impassable in own cultural borders
					{
						if (bIgnoreLoad || !canLoad(pPlot)) 
						{ 
							return false;
						}
					}
				}
			}
		}
	}

	switch (getDomainType())
	{
	case DOMAIN_SEA:
		if (!pPlot->isWater() && !canMoveAllTerrain())
		{
			if (!pPlot->isFriendlyCity(*this, true) || !pPlot->isCoastalLand()) 
			{
				return false;
			}
		}
		break;

	case DOMAIN_AIR:
		if (!bAttack)
		{
			bool bValid = false;

			if (pPlot->isFriendlyCity(*this, true))
			{
				bValid = true;

				if (m_pUnitInfo->getAirUnitCap() > 0)
				{
					if (pPlot->airUnitSpaceAvailable(getTeam()) <= 0)
					{
						bValid = false;
					}
				}
			}

			if (!bValid)
			{
				if (bIgnoreLoad || !canLoad(pPlot))
				{
					return false;
				}
			}
		}

		break;

	case DOMAIN_LAND:
		if (pPlot->isWater() && !canMoveAllTerrain()

//FfH: Added by Kael 08/27/2007 (for boarding)
              && !(bAttack && isBoarding())
//FfH: End Add

		)
		{
			if (!pPlot->isCity() || 0 == GC.defines.iLAND_UNITS_CAN_ATTACK_WATER_CITIES)
			{
				if (bIgnoreLoad || !isHuman() || plot()->isWater() || !canLoad(pPlot))
				{
					return false;
				}
			}
		}
		break;

	case DOMAIN_IMMOBILE:
		return false;
		break;

	default:
		FAssert(false);
		break;
	}

//FfH: Modified by Kael 08/04/2007 (So owned animals dont have limited movement)
//	if (isAnimal())
	if (isAnimal() && isBarbarian()
		// Tholal AI (by Red Key) - allow Barbarian animals to move out of Barbarian territory
		&& (!pPlot->isBarbarian() || pPlot->isCity()))
		// End Tholal AI
//FfH: End Add

	{
		if (pPlot->isOwned())
		{
			return false;
		}

		if (!bAttack)
		{
			if (pPlot->getBonusType() != NO_BONUS)
			{
				return false;
			}

			if (pPlot->getImprovementType() != NO_IMPROVEMENT)
			{
				return false;
			}

			if (pPlot->getNumUnits() > 0)
			{
				return false;
			}
		}
	}

	if (isNoCapture())
	{
		if (!bAttack)
		{
			if (pPlot->isEnemyCity(*this) && !isHiddenNationality())
			{
				return false;
			}
		}
	}

/************************************************************************************************/
/* UNOFFICIAL_PATCH                       07/23/09                                jdog5000      */
/*                                                                                              */
/* Consistency                                                                                  */
/************************************************************************************************/
/* original bts code
	if (bAttack)
	{
		if (isMadeAttack() && !isBlitz())
		{
			return false;
		}
	}
*/
	// The following change makes capturing an undefended city like a attack action, it
	// cannot be done after another attack or a paradrop
	/*
	if (bAttack || (pPlot->isEnemyCity(*this) && !canCoexistWithEnemyUnit(NO_TEAM)) )
	{
		if (isMadeAttack() && !isBlitz())
		{
			return false;
		}
	}
	*/

	// The following change makes it possible to capture defenseless units after having 
	// made a previous attack or paradrop
	if( bAttack )
	{
		if (isMadeAttack() && !isBlitz() && (pPlot->getNumVisibleEnemyDefenders(this) > 0))
		{
			return false;
		}
	}
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/

	if (getDomainType() == DOMAIN_AIR)
	{
		if (bAttack)
		{
			if (!canAirStrike(pPlot))
			{
				return false;
			}
		}
	}
	else
	{
		if (canAttack())
		{
			if (bAttack || !canCoexistWithEnemyUnit(NO_TEAM))
			{
				if (!isHuman() || (pPlot->isVisible(getTeam(), false)))
				{
					if (pPlot->isVisibleEnemyUnit(this) != bAttack)
					{
						//FAssertMsg(isHuman() || (!bDeclareWar || (pPlot->isVisibleOtherUnit(getOwnerINLINE()) != bAttack)), "hopefully not an issue, but tracking how often this is the case when we dont want to really declare war");
						if (!bDeclareWar || (pPlot->isVisibleOtherUnit(getOwnerINLINE()) != bAttack && !(bAttack && pPlot->getPlotCity() && !isNoCapture())))
						{
							return false;
						}
					}
				}
			}

			if (bAttack)
			{
				CvUnit* pDefender = pPlot->getBestDefender(NO_PLAYER, getOwnerINLINE(), this, true);
				if (NULL != pDefender)
				{
					if (!canAttack(*pDefender))
					{
						return false;
					}
				}
			}
		}
		else
		{
			if (bAttack)
			{
				return false;
			}

			if (!canCoexistWithEnemyUnit(NO_TEAM))
			{
				if (!isHuman() || pPlot->isVisible(getTeam(), false))
				{
					if (pPlot->isEnemyCity(*this))
					{
						return false;
					}

					if (pPlot->isVisibleEnemyUnit(this))
					{
						return false;
					}
				}
			}
		}

		if (isHuman())
		{
			ePlotTeam = pPlot->getRevealedTeam(getTeam(), false);
			bCanEnterArea = canEnterArea(ePlotTeam, pPlotArea);
		}

		if (!bCanEnterArea)
		{
			FAssert(ePlotTeam != NO_TEAM);

			if (!(GET_TEAM(getTeam()).canDeclareWar(ePlotTeam)))
			{
				return false;
			}

			if (isHuman())
			{
				if (!bDeclareWar)
				{
					return false;
				}
			}
			else
			{
				if (GET_TEAM(getTeam()).AI_isSneakAttackReady(ePlotTeam))
				{
					if (!(getGroup()->AI_isDeclareWar(pPlot)))
					{
						return false;
					}
				}
				else
				{
					return false;
				}
			}
		}
	}

//FfH: Added by Kael 09/02/2007
    if (pPlot->getFeatureType() != NO_FEATURE)
    {
        if (GC.getFeatureInfo((FeatureTypes)pPlot->getFeatureType()).getRequireResist() != NO_DAMAGE)
        {
            if (getDamageTypeResist((DamageTypes)GC.getFeatureInfo((FeatureTypes)pPlot->getFeatureType()).getRequireResist()) < GC.defines.iFEATURE_REQUIRE_RESIST_AMOUNT)
            {
                return false;
            }
        }
    }
    if (pPlot->isOwned())
    {
        if (pPlot->getTeam() != getTeam())
        {
            if (GET_PLAYER(pPlot->getOwnerINLINE()).getSanctuaryTimer() != 0)
            {
                return false;
            }
        }
    }
    if (getLevel() < pPlot->getMinLevel())
    {
        return false;
    }
    if (pPlot->isMoveDisabledHuman())
    {
        if (isHuman())
        {
            return false;
        }
    }
    if (pPlot->isMoveDisabledAI())
    {
        if (!isHuman())
        {
            return false;
        }
    }
//FfH: End Add

	if (GC.getUSE_UNIT_CANNOT_MOVE_INTO_CALLBACK())
	{
		// Python Override
		CyArgsList argsList;
		argsList.add(getOwnerINLINE());	// Player ID
		argsList.add(getID());	// Unit ID
		argsList.add(pPlot->getX());	// Plot X
		argsList.add(pPlot->getY());	// Plot Y
		long lResult=0;
		gDLL->getPythonIFace()->callFunction(PYGameModule, "unitCannotMoveInto", argsList.makeFunctionArgs(), &lResult);

		if (lResult != 0)
		{
			return false;
		}
	}

	return true;
}


bool CvUnit::canMoveOrAttackInto(const CvPlot* pPlot, bool bDeclareWar) const
{
	return (canMoveInto(pPlot, false, bDeclareWar) || canMoveInto(pPlot, true, bDeclareWar));
}


bool CvUnit::canMoveThrough(const CvPlot* pPlot) const
{
	return canMoveInto(pPlot, false, false, true);
}


void CvUnit::attack(CvPlot* pPlot, bool bQuick)
{
	FAssert(canMoveInto(pPlot, true));
	FAssert(getCombatTimer() == 0);

	setAttackPlot(pPlot, false);

	updateCombat(bQuick);
}

void CvUnit::fightInterceptor(const CvPlot* pPlot, bool bQuick)
{
	FAssert(getCombatTimer() == 0);

	setAttackPlot(pPlot, true);

	updateAirCombat(bQuick);
}

void CvUnit::attackForDamage(CvUnit *pDefender, int attackerDamageChange, int defenderDamageChange)
{
	FAssert(getCombatTimer() == 0);
	FAssert(pDefender != NULL);
	FAssert(!isFighting());

	if(pDefender == NULL)
	{
		return;
	}

	setAttackPlot(pDefender->plot(), false);

	CvPlot* pPlot = getAttackPlot();
	if (pPlot == NULL)
	{
		return;
	}

	//rotate to face plot
	DirectionTypes newDirection = estimateDirection(this->plot(), pDefender->plot());
	if(newDirection != NO_DIRECTION)
	{
		setFacingDirection(newDirection);
	}

	//rotate enemy to face us
	newDirection = estimateDirection(pDefender->plot(), this->plot());
	if(newDirection != NO_DIRECTION)
	{
		pDefender->setFacingDirection(newDirection);
	}

	//check if quick combat
	bool bVisible = isCombatVisible(pDefender);

	//if not finished and not fighting yet, set up combat damage and mission
	if (!isFighting())
	{
		if (plot()->isFighting() || pPlot->isFighting())
		{
			return;
		}

		setCombatUnit(pDefender, true);
		pDefender->setCombatUnit(this, false);

		pDefender->getGroup()->clearMissionQueue();

		bool bFocused = (bVisible && isCombatFocus() && gDLL->getInterfaceIFace()->isCombatFocus());

		if (bFocused)
		{
			DirectionTypes directionType = directionXY(plot(), pPlot);
			//								N			NE				E				SE					S				SW					W				NW
			NiPoint2 directions[8] = {NiPoint2(0, 1), NiPoint2(1, 1), NiPoint2(1, 0), NiPoint2(1, -1), NiPoint2(0, -1), NiPoint2(-1, -1), NiPoint2(-1, 0), NiPoint2(-1, 1)};
			NiPoint3 attackDirection = NiPoint3(directions[directionType].x, directions[directionType].y, 0);
			float plotSize = GC.getPLOT_SIZE();
			NiPoint3 lookAtPoint(plot()->getPoint().x + plotSize / 2 * attackDirection.x, plot()->getPoint().y + plotSize / 2 * attackDirection.y, (plot()->getPoint().z + pPlot->getPoint().z) / 2);
			attackDirection.Unitize();
			gDLL->getInterfaceIFace()->lookAt(lookAtPoint, (((getOwnerINLINE() != GC.getGameINLINE().getActivePlayer()) || gDLL->getGraphicOption(GRAPHICOPTION_NO_COMBAT_ZOOM)) ? CAMERALOOKAT_BATTLE : CAMERALOOKAT_BATTLE_ZOOM_IN), attackDirection);
		}
		else
		{
			PlayerTypes eAttacker = getVisualOwner(pDefender->getTeam());
			CvWString szMessage;
			if (BARBARIAN_PLAYER != eAttacker)
			{
				szMessage = gDLL->getText("TXT_KEY_MISC_YOU_UNITS_UNDER_ATTACK", GET_PLAYER(getOwnerINLINE()).getNameKey());
			}
			else
			{
				szMessage = gDLL->getText("TXT_KEY_MISC_YOU_UNITS_UNDER_ATTACK_UNKNOWN");
			}

			gDLL->getInterfaceIFace()->addMessage(pDefender->getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szMessage, "AS2D_COMBAT", MESSAGE_TYPE_DISPLAY_ONLY, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE(), true);
		}
	}

	FAssertMsg(plot()->isFighting(), "Current unit instance plot is not fighting as expected");
	FAssertMsg(pPlot->isFighting(), "pPlot is not fighting as expected");

	//setup battle object
	CvBattleDefinition kBattle;
	kBattle.setUnit(BATTLE_UNIT_ATTACKER, this);
	kBattle.setUnit(BATTLE_UNIT_DEFENDER, pDefender);
	kBattle.setDamage(BATTLE_UNIT_ATTACKER, BATTLE_TIME_BEGIN, getDamage());
	kBattle.setDamage(BATTLE_UNIT_DEFENDER, BATTLE_TIME_BEGIN, pDefender->getDamage());

	changeDamage(attackerDamageChange, pDefender->getOwnerINLINE());
	pDefender->changeDamage(defenderDamageChange, getOwnerINLINE());

	if (bVisible)
	{
		kBattle.setDamage(BATTLE_UNIT_ATTACKER, BATTLE_TIME_END, getDamage());
		kBattle.setDamage(BATTLE_UNIT_DEFENDER, BATTLE_TIME_END, pDefender->getDamage());
		kBattle.setAdvanceSquare(canAdvance(pPlot, 1));

		kBattle.addDamage(BATTLE_UNIT_ATTACKER, BATTLE_TIME_RANGED, kBattle.getDamage(BATTLE_UNIT_ATTACKER, BATTLE_TIME_BEGIN));
		kBattle.addDamage(BATTLE_UNIT_DEFENDER, BATTLE_TIME_RANGED, kBattle.getDamage(BATTLE_UNIT_DEFENDER, BATTLE_TIME_BEGIN));

		int iTurns = planBattle( kBattle);
		kBattle.setMissionTime(iTurns * gDLL->getSecsPerTurn());
		setCombatTimer(iTurns);

		GC.getGameINLINE().incrementTurnTimer(getCombatTimer());

		if (pPlot->isActiveVisible(false))
		{
			ExecuteMove(0.5f, true);
			gDLL->getEntityIFace()->AddMission(&kBattle);
		}
	}
	else
	{
		setCombatTimer(1);
	}
}


void CvUnit::move(CvPlot* pPlot, bool bShow)
{
	FAssert(canMoveOrAttackInto(pPlot) || isMadeAttack());

	CvPlot* pOldPlot = plot();

	changeMoves(pPlot->movementCost(this, plot()));

	setXY(pPlot->getX_INLINE(), pPlot->getY_INLINE(), true, true, bShow && pPlot->isVisibleToWatchingHuman(), bShow);

	//change feature
	FeatureTypes featureType = pPlot->getFeatureType();
	if(featureType != NO_FEATURE)
	{
		// lfgr_todo: read to int in pass2
		CvString featureString(GC.getFeatureInfo(featureType).getOnUnitChangeTo());
		if(!featureString.IsEmpty())
		{
			FeatureTypes newFeatureType = (FeatureTypes) GC.getInfoTypeForString(featureString);
			pPlot->setFeatureType(newFeatureType);
		}
	}

	if (getOwnerINLINE() == GC.getGameINLINE().getActivePlayer())
	{
		if (!(pPlot->isOwned()))
		{
			//spawn birds if trees present - JW
			if (featureType != NO_FEATURE)
			{
				if (GC.getASyncRand().get(100) < GC.getFeatureInfo(featureType).getEffectProbability())
				{
					EffectTypes eEffect = (EffectTypes)GC.getInfoTypeForString(GC.getFeatureInfo(featureType).getEffectType());
					gDLL->getEngineIFace()->TriggerEffect(eEffect, pPlot->getPoint(), (float)(GC.getASyncRand().get(360)));
					gDLL->getInterfaceIFace()->playGeneralSound("AS3D_UN_BIRDS_SCATTER", pPlot->getPoint());
				}
			}
		}
	}

//FfH: Modified by Kael 08/02/2008
//	CvEventReporter::getInstance().unitMove(pPlot, this, pOldPlot);
	if(GC.getUSE_ON_UNIT_MOVE_CALLBACK())
	{
		CvEventReporter::getInstance().unitMove(pPlot, this, pOldPlot);
	}
//FfH: End Modify

}

// false if unit is killed
bool CvUnit::jumpToNearestValidPlot()
{
	CvCity* pNearestCity;
	CvPlot* pLoopPlot;
	CvPlot* pBestPlot;
	int iValue;
	int iBestValue;
	int iI;

	FAssertMsg(!isAttacking(), "isAttacking did not return false as expected");
	FAssertMsg(!isFighting(), "isFighting did not return false as expected");

	pNearestCity = GC.getMapINLINE().findCity(getX_INLINE(), getY_INLINE(), getOwnerINLINE());

	iBestValue = MAX_INT;
	pBestPlot = NULL;

	for (iI = 0; iI < GC.getMapINLINE().numPlotsINLINE(); iI++)
	{
		pLoopPlot = GC.getMapINLINE().plotByIndexINLINE(iI);

		if (pLoopPlot->isValidDomainForLocation(*this))
		{
			if (canMoveInto(pLoopPlot))
			{
				if (canEnterArea(pLoopPlot->getTeam(), pLoopPlot->area()) && !isEnemy(pLoopPlot->getTeam(), pLoopPlot))
				{
					FAssertMsg(!atPlot(pLoopPlot), "atPlot(pLoopPlot) did not return false as expected");

					if ((getDomainType() != DOMAIN_AIR) || pLoopPlot->isFriendlyCity(*this, true))
					{
						if (pLoopPlot->isRevealed(getTeam(), false))
						{
							iValue = (plotDistance(getX_INLINE(), getY_INLINE(), pLoopPlot->getX_INLINE(), pLoopPlot->getY_INLINE()) * 2);

							if (pNearestCity != NULL)
							{
								iValue += plotDistance(pLoopPlot->getX_INLINE(), pLoopPlot->getY_INLINE(), pNearestCity->getX_INLINE(), pNearestCity->getY_INLINE());
							}

							if (getDomainType() == DOMAIN_SEA && !plot()->isWater())
							{
								if (!pLoopPlot->isWater() || !pLoopPlot->isAdjacentToArea(area()))
								{
									iValue *= 3;
								}
							}
							else
							{
								if (pLoopPlot->area() != area())
								{
									iValue *= 3;
								}
							}

							if (iValue < iBestValue)
							{
								iBestValue = iValue;
								pBestPlot = pLoopPlot;
							}
						}
					}
				}
			}
		}
	}

	bool bValid = true;
	if (pBestPlot != NULL)
	{
		setXY(pBestPlot->getX_INLINE(), pBestPlot->getY_INLINE());
	}
	else
	{
		logBBAI("    Killing %S -- Cannot jumpToNearestValidPlot, no valid plot (Unit %d - plot: %d, %d)",
				getName().GetCString(), getID(), getX(), getY());
		kill(false);
		bValid = false;
	}

	return bValid;
}


bool CvUnit::canAutomate(AutomateTypes eAutomate) const
{
	if (eAutomate == NO_AUTOMATE)
	{
		return false;
	}

	if (!isGroupHead())
	{
		return false;
	}

	switch (eAutomate)
	{
	case AUTOMATE_BUILD:
		if ((AI_getUnitAIType() != UNITAI_WORKER) && (AI_getUnitAIType() != UNITAI_WORKER_SEA))
		{
			return false;
		}
		break;

	case AUTOMATE_NETWORK:
		if ((AI_getUnitAIType() != UNITAI_WORKER) || !canBuildRoute())
		{
			return false;
		}
		break;

	case AUTOMATE_CITY:
		if (AI_getUnitAIType() != UNITAI_WORKER)
		{
			return false;
		}
		break;

	case AUTOMATE_EXPLORE:
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                      04/25/10                                jdog5000      */
/*                                                                                              */
/* Player Interface                                                                             */
/************************************************************************************************/
		if ( !canFight() )
		{
			// Enable exploration for air units
			if((getDomainType() != DOMAIN_SEA) && (getDomainType() != DOMAIN_AIR))
			{
				if( !(alwaysInvisible()) || !(isSpy()) )
				{
					return false;
				}
			}
		}

		if( (getDomainType() == DOMAIN_IMMOBILE) )
		{
			return false;
		}

		if( getDomainType() == DOMAIN_AIR && !canRecon(NULL) )
		{
			return false;
		}
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                       END                                                  */
/************************************************************************************************/		

		break;

	case AUTOMATE_RELIGION:
		if (AI_getUnitAIType() != UNITAI_MISSIONARY)
		{
			return false;
		}
		break;
/*************************************************************************************************/
/**	ADDON (automatic terraforming) Sephi                                     					**/
/**																								**/
/**						                                            							**/
/*************************************************************************************************/

	case AUTOMATE_TERRAFORMING:
		if (!isTerraformer())
		{
			return false;
		}
		break;
/*************************************************************************************************/
/**	END	                                        												**/
/*************************************************************************************************/

	default:
		FAssert(false);
		break;
	}

	return true;
}

void CvUnit::automate(AutomateTypes eAutomate)
{
	if (!canAutomate(eAutomate))
	{
		return;
	}

	getGroup()->setAutomateType(eAutomate);
}


bool CvUnit::canScrap() const
{
	if (plot()->isFighting())
	{
		return false;
	}

//FfH: Added by Kael 11/06/2007
    if (GET_PLAYER(getOwnerINLINE()).getTempPlayerTimer() > 0)
    {
        return false;
    }
    //if (m_pUnitInfo->getEquipmentPromotion() != NO_PROMOTION)
	if (m_pUnitInfo->isObject())
    {
        return false;
    }
//FfH: End Add

	return true;
}


void CvUnit::scrap()
{
	if (!canScrap())
	{
		return;
	}

//FfH: Added by Kael 11/04/2007
	for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
	{
	    if (isHasPromotion((PromotionTypes)iI))
	    {
            if (GC.getPromotionInfo((PromotionTypes)iI).getBetrayalChance() != 0)
            {
                betray(BARBARIAN_PLAYER);
            }
        }
	}
//FfH: End Add
	
	logBBAI("    Killing %S (delayed) -- scrapped (Unit %d - plot: %d, %d)",
			getName().GetCString(), getID(), getX(), getY());
	kill(true);
}


bool CvUnit::canGift(bool bTestVisible, bool bTestTransport)
{

	if (!GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS))
	{
//FfH: Added by Kael 04/22/2008 (to disable gifting)
		return false;
//FfH: End Add
	}

	if (isGiftingBlocked())
	{
		return false;
	}

	if (isAvatarOfCivLeader())
	{
		return false;
	}

	if (m_pUnitInfo->isAbandon())
	{
		return false;
	}

	if (isLimitedUnitClass(getUnitClassType()))
	{
		return false;
	}

	if (getDuration() > 0 || isPermanentSummon())
	{
		return false;
	}

	if (isHiddenNationality())
	{
		return false;
	}

	CvPlot* pPlot = plot();
	CvUnit* pTransport = getTransportUnit();

	if (!(pPlot->isOwned()))
	{
		return false;
	}

	if (pPlot->getOwnerINLINE() == getOwnerINLINE())
	{
		return false;
	}

	if (pPlot->isVisibleEnemyUnit(this))
	{
		return false;
	}

	if (pPlot->isVisibleEnemyUnit(pPlot->getOwnerINLINE()))
	{
		return false;
	}

	if (!pPlot->isValidDomainForLocation(*this) && NULL == pTransport)
	{
		return false;
	}

	for (int iCorp = 0; iCorp < GC.getNumCorporationInfos(); ++iCorp)
	{
		if (m_pUnitInfo->getCorporationSpreads(iCorp) > 0)
		{
			return false;
		}
	}

	if (bTestTransport)
	{
		if (pTransport && pTransport->getTeam() != pPlot->getTeam())
		{
			return false;
		}
	}

	if (!bTestVisible)
	{
		if (GET_TEAM(pPlot->getTeam()).isUnitClassMaxedOut(getUnitClassType(), GET_TEAM(pPlot->getTeam()).getUnitClassMaking(getUnitClassType())))
		{
			return false;
		}

		if (GET_PLAYER(pPlot->getOwnerINLINE()).isUnitClassMaxedOut(getUnitClassType(), GET_PLAYER(pPlot->getOwnerINLINE()).getUnitClassMaking(getUnitClassType())))
		{
			return false;
		}

		if (!(GET_PLAYER(pPlot->getOwnerINLINE()).AI_acceptUnit(this)))
		{
			return false;
		}
	}

//FfH: Added by Kael 11/06/2007
    if (GET_PLAYER(getOwnerINLINE()).getTempPlayerTimer() > 0)
    {
        return false;
    }

	if (m_pUnitInfo->getPrereqCiv() != NO_CIVILIZATION)
	{
		if (m_pUnitInfo->getPrereqCiv() != GET_PLAYER(pPlot->getOwner()).getCivilizationType())
		{
			return false;
		}
	}

	if (m_pUnitInfo->getStateReligion() != NO_RELIGION)
	{
		if (m_pUnitInfo->getStateReligion() != GET_PLAYER(pPlot->getOwner()).getStateReligion())
		{
			return false;
		}
	}

	if (m_pUnitInfo->getPrereqAlignment() != NO_ALIGNMENT)
	{
		if (m_pUnitInfo->getPrereqAlignment() != GET_PLAYER(pPlot->getOwner()).getAlignment())
		{
			return false;
		}
	}
//FfH: End Add

	return !atWar(pPlot->getTeam(), getTeam());
}


void CvUnit::gift(bool bTestTransport)
{
	CvUnit* pGiftUnit;
	CvWString szBuffer;
	PlayerTypes eOwner;

	if (!canGift(false, bTestTransport))
	{
		return;
	}

	std::vector<CvUnit*> aCargoUnits;
	getCargoUnits(aCargoUnits);
	for (uint i = 0; i < aCargoUnits.size(); ++i)
	{
		aCargoUnits[i]->gift(false);
	}

	FAssertMsg(plot()->getOwnerINLINE() != NO_PLAYER, "plot()->getOwnerINLINE() is not expected to be equal with NO_PLAYER");
// lfgr 04/2014 bugfix
//	pGiftUnit = GET_PLAYER(plot()->getOwnerINLINE()).initUnit(getUnitType(), getX_INLINE(), getY_INLINE(), AI_getUnitAIType());
	pGiftUnit = GET_PLAYER(plot()->getOwnerINLINE()).initUnit(getUnitType(), getX_INLINE(), getY_INLINE(), AI_getUnitAIType(), NO_DIRECTION, true, true);
// lfgr end

	FAssertMsg(pGiftUnit != NULL, "GiftUnit is not assigned a valid value");

	eOwner = getOwnerINLINE();

	pGiftUnit->convert(this);

	int iUnitGiftValue = 0;
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                      10/03/09                                jdog5000      */
/*                                                                                              */
/* General AI                                                                                   */
/************************************************************************************************/
	//GET_PLAYER(pGiftUnit->getOwnerINLINE()).AI_changePeacetimeGrantValue(eOwner, (pGiftUnit->getUnitInfo().getProductionCost() / 5));
	//if( pGiftUnit->isCombat() )
	if (pGiftUnit->canDefend())
	{
		//GET_PLAYER(pGiftUnit->getOwnerINLINE()).AI_changePeacetimeGrantValue(eOwner, (pGiftUnit->getUnitInfo().getProductionCost() * 3 * GC.getGameINLINE().AI_combatValue(pGiftUnit->getUnitType()))/100);
		//GET_PLAYER(pGiftUnit->getOwnerINLINE()).AI_changePeacetimeGrantValue(eOwner, (3 * GET_PLAYER(plot()->getOwnerINLINE()).AI_trueCombatValue(pGiftUnit->getUnitType()))/100);
		iUnitGiftValue = pGiftUnit->getUnitInfo().getProductionCost() * 3 * GET_PLAYER(plot()->getOwnerINLINE()).AI_trueCombatValue(pGiftUnit->getUnitType()) / 100;
	}
	else
	{
		int productionCost = pGiftUnit->getUnitInfo().getProductionCost();
		if (productionCost > 0) 
		{
			iUnitGiftValue = pGiftUnit->getUnitInfo().getProductionCost();
			//GET_PLAYER(pGiftUnit->getOwnerINLINE()).AI_changePeacetimeGrantValue(eOwner, (pGiftUnit->getUnitInfo().getProductionCost()));
		} 
		else 
		{
			// ToDo: The AI should probably evaluate the gift instead of giving them fixed values.
			bool isValuedUnit = false;

			if (pGiftUnit->getUnitInfo().getFreePromotions((PromotionTypes)GC.defines.iPROMOTION_HERO)) {
				// Hardcode: Adventurers
				isValuedUnit = true;
			} else if (pGiftUnit->getUnitInfo().getLeaderPromotion() != NO_PROMOTION) {
				isValuedUnit = true;
			} else {
				for (int iI = 0; iI < GC.getNumSpecialistInfos(); iI++)
				{
					SpecialistTypes eSpecialist = (SpecialistTypes)iI;
					if (m_pUnitInfo->getGreatPeoples(eSpecialist))
					{
						isValuedUnit = true;
						iUnitGiftValue = 240;
						break;
					}
				}
			
			}
		}
	}

	if (gUnitLogLevel > 2) logBBAI("   Unit %S (%d) gifted to %S (value: %d)", pGiftUnit->getName().GetCString(), getID(), GET_PLAYER(pGiftUnit->getOwnerINLINE()).getCivilizationDescription(0), iUnitGiftValue);
	GET_PLAYER(pGiftUnit->getOwnerINLINE()).AI_changePeacetimeGrantValue(eOwner, iUnitGiftValue);
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                       END                                                  */
/************************************************************************************************/

	szBuffer = gDLL->getText("TXT_KEY_MISC_GIFTED_UNIT_TO_YOU", GET_PLAYER(eOwner).getNameKey(), pGiftUnit->getNameKey());
	gDLL->getInterfaceIFace()->addMessage(pGiftUnit->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_UNITGIFTED", MESSAGE_TYPE_INFO, pGiftUnit->getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_WHITE"), pGiftUnit->getX_INLINE(), pGiftUnit->getY_INLINE(), true, true);

	// Python Event
	CvEventReporter::getInstance().unitGifted(pGiftUnit, getOwnerINLINE(), plot());
}


bool CvUnit::canLoadUnit(const CvUnit* pUnit, const CvPlot* pPlot) const
{
	FAssert(pUnit != NULL);
	FAssert(pPlot != NULL);

	if (pUnit == this)
	{
		return false;
	}

	if (pUnit->getTeam() != getTeam())
	{
		return false;
	}

	if (isHeld())
	{
		return false;
	}

/************************************************************************************************/
/* UNOFFICIAL_PATCH                       06/23/10                     Mongoose & jdog5000      */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
	// From Mongoose SDK
	if (isCargo() && getTransportUnit() == pUnit)
	{
		return false;
	}
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/

	if (getCargo() > 0)
	{
		return false;
	}

	if (pUnit->isCargo())
	{
		return false;
	}

	if (!(pUnit->cargoSpaceAvailable(getSpecialUnitType(), getDomainType())))
	{
		return false;
	}

	if (!(pUnit->atPlot(pPlot)))
	{
		return false;
	}

//FfH Hidden Nationality: Modified by Kael 08/27/2007
//	if (!m_pUnitInfo->isHiddenNationality() && pUnit->getUnitInfo().isHiddenNationality())
	if (isHiddenNationality() != pUnit->isHiddenNationality())
//FfH: End Modify

	{
		return false;
	}

	if (NO_SPECIALUNIT != getSpecialUnitType())
	{
		if (GC.getSpecialUnitInfo(getSpecialUnitType()).isCityLoad())
		{
			if (!pPlot->isCity(true, getTeam()))
			{
				return false;
			}
		}
	}

//>>>>Unofficial Bug Fix: Added by Denev 2009/12/08
//*** Tweak for FfH rules (to prevent airship loads other airship).
	if (cargoSpace() > 0)
	{
		if (specialCargo() == pUnit->specialCargo() && domainCargo() == pUnit->domainCargo())
		{
			return false;
		}
	}
//<<<<Unofficial Bug Fix: End Add

	return true;
}


void CvUnit::loadUnit(CvUnit* pUnit)
{
	if (!canLoadUnit(pUnit, plot()))
	{
		return;
	}

	setTransportUnit(pUnit);
}

bool CvUnit::shouldLoadOnMove(const CvPlot* pPlot) const
{
	if (isCargo())
	{
		return false;
	}

	switch (getDomainType())
	{
	case DOMAIN_LAND:
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       10/30/09                     Mongoose & jdog5000      */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
		if (pPlot->isWater())
*/
		// From Mongoose SDK
		if (pPlot->isWater() && !canMoveAllTerrain())
		{
			return true;
		}
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
		break;
	case DOMAIN_AIR:
		if (!pPlot->isFriendlyCity(*this, true))
		{
			return true;
		}

		if (m_pUnitInfo->getAirUnitCap() > 0)
		{
			if (pPlot->airUnitSpaceAvailable(getTeam()) <= 0)
			{
				return true;
			}
		}
		break;
	default:
		break;
	}

	if (m_pUnitInfo->getTerrainImpassable(pPlot->getTerrainType()))
	{
		TechTypes eTech = (TechTypes)m_pUnitInfo->getTerrainPassableTech(pPlot->getTerrainType());
		if (NO_TECH == eTech || !GET_TEAM(getTeam()).isHasTech(eTech))
		{
			return true;
		}
	}

	return false;
}


bool CvUnit::canLoad(const CvPlot* pPlot) const
{
	PROFILE_FUNC();

	FAssert(pPlot != NULL);

	CLLNode<IDInfo>* pUnitNode = pPlot->headUnitNode();
	while (pUnitNode != NULL)
	{
		CvUnit* pLoopUnit = ::getUnit(pUnitNode->m_data);
		pUnitNode = pPlot->nextUnitNode(pUnitNode);

		if (canLoadUnit(pLoopUnit, pPlot))
		{
			return true;
		}
	}

	return false;
}


void CvUnit::load()
{
	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pLoopUnit;
	CvPlot* pPlot;
	int iPass;

	if (!canLoad(plot()))
	{
		return;
	}

	pPlot = plot();

	for (iPass = 0; iPass < 2; iPass++)
	{
		pUnitNode = pPlot->headUnitNode();

		while (pUnitNode != NULL)
		{
			pLoopUnit = ::getUnit(pUnitNode->m_data);
			pUnitNode = pPlot->nextUnitNode(pUnitNode);

			if (canLoadUnit(pLoopUnit, pPlot))
			{
				if ((iPass == 0) ? (pLoopUnit->getOwnerINLINE() == getOwnerINLINE()) : (pLoopUnit->getTeam() == getTeam()))
				{
					setTransportUnit(pLoopUnit);
					break;
				}
			}
		}

		if (isCargo())
		{
			break;
		}
	}
}


bool CvUnit::canUnload() const
{
	CvPlot& kPlot = *(plot());

	if (getTransportUnit() == NULL)
	{
		return false;
	}

	if (!kPlot.isValidDomainForLocation(*this))
	{
		return false;
	}

	if (getDomainType() == DOMAIN_AIR)
	{
		if (kPlot.isFriendlyCity(*this, true))
		{
			int iNumAirUnits = kPlot.countNumAirUnits(getTeam());
			CvCity* pCity = kPlot.getPlotCity();
			if (NULL != pCity)
			{
				if (iNumAirUnits >= pCity->getAirUnitCapacity(getTeam()))
				{
					return false;
				}
			}
			else
			{
				if (iNumAirUnits >= GC.defines.iCITY_AIR_UNIT_CAPACITY)
				{
					return false;
				}
			}
		}
	}

	return true;
}


void CvUnit::unload()
{
	if (!canUnload())
	{
		return;
	}

	setTransportUnit(NULL);
}


bool CvUnit::canUnloadAll() const
{
	if (getCargo() == 0)
	{
		return false;
	}

	return true;
}


void CvUnit::unloadAll()
{
	if (!canUnloadAll())
	{
		return;
	}

	std::vector<CvUnit*> aCargoUnits;
	getCargoUnits(aCargoUnits);
	for (uint i = 0; i < aCargoUnits.size(); ++i)
	{
		CvUnit* pCargo = aCargoUnits[i];
		if (pCargo->canUnload())
		{
			pCargo->setTransportUnit(NULL);
		}
		else
		{
			FAssert(isHuman() || pCargo->getDomainType() == DOMAIN_AIR);
			pCargo->getGroup()->setActivityType(ACTIVITY_AWAKE);
		}
	}
}


bool CvUnit::canHold(const CvPlot* pPlot) const
{
	return true;
}


bool CvUnit::canSleep(const CvPlot* pPlot) const
{
	if (isFortifyable())
	{
		return false;
	}

	if (isWaiting())
	{
		return false;
	}

	return true;
}


bool CvUnit::canFortify(const CvPlot* pPlot) const
{
	if (!isFortifyable())
	{
		return false;
	}

	if (isWaiting())
	{
		return false;
	}

	return true;
}


bool CvUnit::canAirPatrol(const CvPlot* pPlot) const
{
	if (getDomainType() != DOMAIN_AIR)
	{
		return false;
	}

	if (!canAirDefend(pPlot))
	{
		return false;
	}

	if (isWaiting())
	{
		return false;
	}

	return true;
}


bool CvUnit::canSeaPatrol(const CvPlot* pPlot) const
{
	if (!pPlot->isWater())
	{
		return false;
	}

	if (getDomainType() != DOMAIN_SEA)
	{
		return false;
	}

	if (!canFight() || isOnlyDefensive())
	{
		return false;
	}

	if (isWaiting())
	{
		return false;
	}

	return true;
}


void CvUnit::airCircle(bool bStart)
{
	if (!GC.IsGraphicsInitialized())
	{
		return;
	}

	if ((getDomainType() != DOMAIN_AIR) || (maxInterceptionProbability() == 0))
	{
		return;
	}

	//cancel previos missions
	gDLL->getEntityIFace()->RemoveUnitFromBattle( this );

	if (bStart)
	{
		CvAirMissionDefinition kDefinition;
		kDefinition.setPlot(plot());
		kDefinition.setUnit(BATTLE_UNIT_ATTACKER, this);
		kDefinition.setUnit(BATTLE_UNIT_DEFENDER, NULL);
		kDefinition.setMissionType(MISSION_AIRPATROL);
		kDefinition.setMissionTime(1.0f); // patrol is indefinite - time is ignored

		gDLL->getEntityIFace()->AddMission( &kDefinition );
	}
}


bool CvUnit::canHeal(const CvPlot* pPlot) const
{
	if (!isHurt())
	{
		return false;
	}

	if (isWaiting())
	{
		return false;
	}

/*************************************************************************************************/
/* UNOFFICIAL_PATCH                       06/30/10                           LunarMongoose       */
/*                                                                                               */
/* Bugfix                                                                                        */
/*************************************************************************************************/
/* original bts code
	if (healRate(pPlot) <= 0)
	{
		return false;
	}
*/
	// Mongoose FeatureDamageFix
	if (healTurns(pPlot) == MAX_INT)
	{
		return false;
	}
/*************************************************************************************************/
/* UNOFFICIAL_PATCH                         END                                                  */
/*************************************************************************************************/

	return true;
}


bool CvUnit::canSentry(const CvPlot* pPlot) const
{
	if (!canDefend(pPlot))
	{
		return false;
	}

	if (isWaiting())
	{
		return false;
	}

	return true;
}


int CvUnit::healRate(const CvPlot* pPlot) const
{
	PROFILE_FUNC();

	CLLNode<IDInfo>* pUnitNode;
	CvCity* pCity;
	CvUnit* pLoopUnit;
	CvPlot* pLoopPlot;
	int iTotalHeal;
	int iHeal;
	int iBestHeal;
	int iI;

//FfH: Added by Kael 11/05/2008
    if (GC.getGameINLINE().isOption(GAMEOPTION_NO_HEALING_FOR_HUMANS))
    {
        if (isHuman())
        {
            if (isAlive())
            {
                return 0;
            }
        }
    }
//FfH: End Add

	pCity = pPlot->getPlotCity();

	iTotalHeal = 0;

	if (pPlot->isCity(true, getTeam()))
	{
		iTotalHeal += GC.defines.iCITY_HEAL_RATE + (GET_TEAM(getTeam()).isFriendlyTerritory(pPlot->getTeam()) ? getExtraFriendlyHeal() : getExtraNeutralHeal());
		if (pCity && !pCity->isOccupation())
		{
			iTotalHeal += pCity->getHealRate();
		}
	}
	else
	{
		if (!GET_TEAM(getTeam()).isFriendlyTerritory(pPlot->getTeam()))
		{
			if (isEnemy(pPlot->getTeam(), pPlot))
			{
				iTotalHeal += (GC.defines.iENEMY_HEAL_RATE + getExtraEnemyHeal());

//FfH Mana Effects: Added by Kael 08/21/2007
				if (pPlot->getOwnerINLINE() != NO_PLAYER)
				{
                    iTotalHeal += GET_PLAYER(pPlot->getOwnerINLINE()).getHealChangeEnemy();
				}
//FfH: End Add

			}
			else
			{
				iTotalHeal += (GC.defines.iNEUTRAL_HEAL_RATE + getExtraNeutralHeal());
			}
		}
		else
		{
			iTotalHeal += (GC.defines.iFRIENDLY_HEAL_RATE + getExtraFriendlyHeal());

//FfH Mana Effects: Added by Kael 08/21/2007
            iTotalHeal += GET_PLAYER(getOwnerINLINE()).getHealChange();
//FfH: End Add

		}
	}

	// XXX optimize this (save it?)
	iBestHeal = 0;

	pUnitNode = pPlot->headUnitNode();

	while (pUnitNode != NULL)
	{
		pLoopUnit = ::getUnit(pUnitNode->m_data);
		pUnitNode = pPlot->nextUnitNode(pUnitNode);

		if (pLoopUnit->getTeam() == getTeam()) // XXX what about alliances?
		{
			iHeal = pLoopUnit->getSameTileHeal();

			if (iHeal > iBestHeal)
			{
				iBestHeal = iHeal;
			}
		}
	}

	for (iI = 0; iI < NUM_DIRECTION_TYPES; iI++)
	{
		pLoopPlot = plotDirection(pPlot->getX_INLINE(), pPlot->getY_INLINE(), ((DirectionTypes)iI));

		if (pLoopPlot != NULL)
		{
			if (pLoopPlot->area() == pPlot->area())
			{
				pUnitNode = pLoopPlot->headUnitNode();

				while (pUnitNode != NULL)
				{
					pLoopUnit = ::getUnit(pUnitNode->m_data);
					pUnitNode = pLoopPlot->nextUnitNode(pUnitNode);

					if (pLoopUnit->getTeam() == getTeam()) // XXX what about alliances?
					{
						iHeal = pLoopUnit->getAdjacentTileHeal();

						if (iHeal > iBestHeal)
						{
							iBestHeal = iHeal;
						}
					}
				}
			}
		}
	}

	iTotalHeal += iBestHeal;
	// XXX


//FfH: Added by Kael 10/29/2007
    if (pPlot->getImprovementType() != NO_IMPROVEMENT)
    {
        iTotalHeal += GC.getImprovementInfo((ImprovementTypes)pPlot->getImprovementType()).getHealRateChange();
    }
    if (iTotalHeal < 0)
    {
        iTotalHeal = 0;
    }
//FfH: End Add

	return iTotalHeal;
}


int CvUnit::healTurns(const CvPlot* pPlot) const
{
	int iHeal;
	int iTurns;

	if (!isHurt())
	{
		return 0;
	}

	iHeal = healRate(pPlot);

/*************************************************************************************************/
/* UNOFFICIAL_PATCH                       06/02/10                           LunarMongoose       */
/*                                                                                               */
/* Bugfix                                                                                        */
/*************************************************************************************************/
	// Mongoose FeatureDamageFix
	FeatureTypes eFeature = pPlot->getFeatureType();
	if (eFeature != NO_FEATURE)
	{
		iHeal -= GC.getFeatureInfo(eFeature).getTurnDamage();
	}
/*************************************************************************************************/
/* UNOFFICIAL_PATCH                         END                                                  */
/*************************************************************************************************/

	if (iHeal > 0)
	{
		iTurns = (getDamage() / iHeal);

		if ((getDamage() % iHeal) != 0)
		{
			iTurns++;
		}

		return iTurns;
	}
	else
	{
		return MAX_INT;
	}
}


void CvUnit::doHeal()
{
	changeDamage(-(healRate(plot())));
}


bool CvUnit::canAirlift(const CvPlot* pPlot) const
{
	CvCity* pCity;

	if (getDomainType() != DOMAIN_LAND)
	{
		return false;
	}

	if (hasMoved())
	{
		return false;
	}

	pCity = pPlot->getPlotCity();

	if (pCity == NULL)
	{
		return false;
	}

	if (pCity->getCurrAirlift() >= pCity->getMaxAirlift())
	{
		return false;
	}

	if (pCity->getTeam() != getTeam())
	{
		return false;
	}

	return true;
}


bool CvUnit::canAirliftAt(const CvPlot* pPlot, int iX, int iY) const
{
	CvPlot* pTargetPlot;
	CvCity* pTargetCity;

	if (!canAirlift(pPlot))
	{
		return false;
	}

	pTargetPlot = GC.getMapINLINE().plotINLINE(iX, iY);

	if (!canMoveInto(pTargetPlot))
	{
		return false;
	}

	// Super Forts begin *airlift*
	if (pTargetPlot->getTeam() != NO_TEAM)
	{
		if (pTargetPlot->getTeam() == getTeam() || GET_TEAM(pTargetPlot->getTeam()).isVassal(getTeam()))
		{
			if (pTargetPlot->getImprovementType() != NO_IMPROVEMENT)
			{
				if (GC.getImprovementInfo(pTargetPlot->getImprovementType()).isActsAsCity())
				{
					return true;
				}
			}
		}
	}
	// Super Forts end

	pTargetCity = pTargetPlot->getPlotCity();

	if (pTargetCity == NULL)
	{
		return false;
	}

	if (pTargetCity->isAirliftTargeted())
	{
		return false;
	}

	if (pTargetCity->getTeam() != getTeam() && !GET_TEAM(pTargetCity->getTeam()).isVassal(getTeam()))
	{
		return false;
	}

	return true;
}


bool CvUnit::airlift(int iX, int iY)
{
	CvCity* pCity;
	CvCity* pTargetCity;
	CvPlot* pTargetPlot;

	if (!canAirliftAt(plot(), iX, iY))
	{
		return false;
	}

	pCity = plot()->getPlotCity();
	FAssert(pCity != NULL);
	pTargetPlot = GC.getMapINLINE().plotINLINE(iX, iY);
	FAssert(pTargetPlot != NULL);
	// Super Forts begin *airlift* - added if statement to allow airlifts to plots that aren't cities
	if (pTargetPlot->isCity())
	{
		pTargetCity = pTargetPlot->getPlotCity();
		FAssert(pTargetCity != NULL);
		FAssert(pCity != pTargetCity);

		if (pTargetCity->getMaxAirlift() == 0)
		{
			pTargetCity->setAirliftTargeted(true);
		}
	}
	pCity->changeCurrAirlift(1);
	// Super Forts end

	finishMoves();

	setXY(pTargetPlot->getX_INLINE(), pTargetPlot->getY_INLINE());

	logBBAI("    %S (%d) airlifting to plot %d, %d", getName().GetCString(), getID(), pTargetPlot->getX_INLINE(), pTargetPlot->getY_INLINE());    

	return true;
}


bool CvUnit::isNukeVictim(const CvPlot* pPlot, TeamTypes eTeam) const
{
	CvPlot* pLoopPlot;
	int iDX, iDY;

	if (!(GET_TEAM(eTeam).isAlive()))
	{
		return false;
	}

	if (eTeam == getTeam())
	{
		return false;
	}

	for (iDX = -(nukeRange()); iDX <= nukeRange(); iDX++)
	{
		for (iDY = -(nukeRange()); iDY <= nukeRange(); iDY++)
		{
			pLoopPlot	= plotXY(pPlot->getX_INLINE(), pPlot->getY_INLINE(), iDX, iDY);

			if (pLoopPlot != NULL)
			{
				if (pLoopPlot->getTeam() == eTeam)
				{
					return true;
				}

				if (pLoopPlot->plotCheck(PUF_isCombatTeam, eTeam, getTeam()) != NULL)
				{
					return true;
				}
			}
		}
	}

	return false;
}


bool CvUnit::canNuke(const CvPlot* pPlot) const
{
	if (nukeRange() == -1)
	{
		return false;
	}

	return true;
}


bool CvUnit::canNukeAt(const CvPlot* pPlot, int iX, int iY) const
{
	CvPlot* pTargetPlot;
	int iI;

	if (!canNuke(pPlot))
	{
		return false;
	}

	int iDistance = plotDistance(pPlot->getX_INLINE(), pPlot->getY_INLINE(), iX, iY);
	if (iDistance <= nukeRange())
	{
		return false;
	}

	if (airRange() > 0 && iDistance > airRange())
	{
		return false;
	}

	pTargetPlot = GC.getMapINLINE().plotINLINE(iX, iY);

	for (iI = 0; iI < MAX_TEAMS; iI++)
	{
		if (isNukeVictim(pTargetPlot, ((TeamTypes)iI)))
		{
			if (!isEnemy((TeamTypes)iI, pPlot))
			{
				return false;
			}
		}
	}

	return true;
}


bool CvUnit::nuke(int iX, int iY)
{
	CvPlot* pPlot;
	CvWString szBuffer;
	bool abTeamsAffected[MAX_TEAMS];
	TeamTypes eBestTeam;
	int iBestInterception;
	int iI, iJ, iK;

	if (!canNukeAt(plot(), iX, iY))
	{
		return false;
	}

	pPlot = GC.getMapINLINE().plotINLINE(iX, iY);

	for (iI = 0; iI < MAX_TEAMS; iI++)
	{
		abTeamsAffected[iI] = isNukeVictim(pPlot, ((TeamTypes)iI));
	}

	for (iI = 0; iI < MAX_TEAMS; iI++)
	{
		if (abTeamsAffected[iI])
		{
/*************************************************************************************************/
/* Advanced Diplomacy         START                                                               */
/*************************************************************************************************/
			if ((TeamTypes)iI != getTeam() && !GET_TEAM(getTeam()).isAtWar((TeamTypes)iI))
			{
				GET_TEAM((TeamTypes)iI).changeWarPretextAgainstCount(getTeam(), 1);
			}
/*************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/*************************************************************************************************/
			if (!isEnemy((TeamTypes)iI))
			{
				GET_TEAM(getTeam()).declareWar(((TeamTypes)iI), false, WARPLAN_LIMITED);
			}
		}
	}

	iBestInterception = 0;
	eBestTeam = NO_TEAM;

	for (iI = 0; iI < MAX_TEAMS; iI++)
	{
		if (abTeamsAffected[iI])
		{
			if (GET_TEAM((TeamTypes)iI).getNukeInterception() > iBestInterception)
			{
				iBestInterception = GET_TEAM((TeamTypes)iI).getNukeInterception();
				eBestTeam = ((TeamTypes)iI);
			}
		}
	}

	iBestInterception *= (100 - m_pUnitInfo->getEvasionProbability());
	iBestInterception /= 100;

	setReconPlot(pPlot);

	if (GC.getGameINLINE().getSorenRandNum(100, "Nuke") < iBestInterception)
	{
		for (iI = 0; iI < MAX_PLAYERS; iI++)
		{
			if (GET_PLAYER((PlayerTypes)iI).isAlive())
			{
				szBuffer = gDLL->getText("TXT_KEY_MISC_NUKE_INTERCEPTED", GET_PLAYER(getOwnerINLINE()).getNameKey(), getNameKey(), GET_TEAM(eBestTeam).getName().GetCString());
				gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)iI), (((PlayerTypes)iI) == getOwnerINLINE()), GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_NUKE_INTERCEPTED", MESSAGE_TYPE_MAJOR_EVENT, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE(), true, true);
			}
		}

		if (pPlot->isActiveVisible(false))
		{
			// Nuke entity mission
			CvMissionDefinition kDefiniton;
			kDefiniton.setMissionTime(GC.getMissionInfo(MISSION_NUKE).getTime() * gDLL->getSecsPerTurn());
			kDefiniton.setMissionType(MISSION_NUKE);
			kDefiniton.setPlot(pPlot);
			kDefiniton.setUnit(BATTLE_UNIT_ATTACKER, this);
			kDefiniton.setUnit(BATTLE_UNIT_DEFENDER, this);

			// Add the intercepted mission (defender is not NULL)
			gDLL->getEntityIFace()->AddMission(&kDefiniton);
		}
		
		logBBAI("    Killing %S (delayed) -- nuke intercepted (Unit %d - plot: %d, %d)",
				getName().GetCString(), getID(), getX(), getY());
		kill(true);
		return true; // Intercepted!!! (XXX need special event for this...)
	}

	if (pPlot->isActiveVisible(false))
	{
		// Nuke entity mission
		CvMissionDefinition kDefiniton;
		kDefiniton.setMissionTime(GC.getMissionInfo(MISSION_NUKE).getTime() * gDLL->getSecsPerTurn());
		kDefiniton.setMissionType(MISSION_NUKE);
		kDefiniton.setPlot(pPlot);
		kDefiniton.setUnit(BATTLE_UNIT_ATTACKER, this);
		kDefiniton.setUnit(BATTLE_UNIT_DEFENDER, NULL);

		// Add the non-intercepted mission (defender is NULL)
		gDLL->getEntityIFace()->AddMission(&kDefiniton);
	}

	setMadeAttack(true);
	setAttackPlot(pPlot, false);

	for (iI = 0; iI < MAX_TEAMS; iI++)
	{
		if (abTeamsAffected[iI])
		{
			GET_TEAM((TeamTypes)iI).changeWarWeariness(getTeam(), 100 * GC.defines.iWW_HIT_BY_NUKE);
			GET_TEAM(getTeam()).changeWarWeariness(((TeamTypes)iI), 100 * GC.defines.iWW_ATTACKED_WITH_NUKE);
			GET_TEAM(getTeam()).AI_changeWarSuccess(((TeamTypes)iI), GC.defines.iWAR_SUCCESS_NUKE);
		}
	}

	for (iI = 0; iI < MAX_TEAMS; iI++)
	{
		if (GET_TEAM((TeamTypes)iI).isAlive())
		{
			if (iI != getTeam())
			{
				if (abTeamsAffected[iI])
				{
					for (iJ = 0; iJ < MAX_PLAYERS; iJ++)
					{
						if (GET_PLAYER((PlayerTypes)iJ).isAlive())
						{
							if (GET_PLAYER((PlayerTypes)iJ).getTeam() == ((TeamTypes)iI))
							{
								GET_PLAYER((PlayerTypes)iJ).AI_changeMemoryCount(getOwnerINLINE(), MEMORY_NUKED_US, 1);
							}
						}
					}
				}
				else
				{
					for (iJ = 0; iJ < MAX_TEAMS; iJ++)
					{
						if (GET_TEAM((TeamTypes)iJ).isAlive())
						{
							if (abTeamsAffected[iJ])
							{
								if (GET_TEAM((TeamTypes)iI).isHasMet((TeamTypes)iJ))
								{
									if (GET_TEAM((TeamTypes)iI).AI_getAttitude((TeamTypes)iJ) >= ATTITUDE_CAUTIOUS)
									{
										for (iK = 0; iK < MAX_PLAYERS; iK++)
										{
											if (GET_PLAYER((PlayerTypes)iK).isAlive())
											{
												if (GET_PLAYER((PlayerTypes)iK).getTeam() == ((TeamTypes)iI))
												{
													GET_PLAYER((PlayerTypes)iK).AI_changeMemoryCount(getOwnerINLINE(), MEMORY_NUKED_FRIEND, 1);
												}
											}
										}
										break;
									}
								}
							}
						}
					}
				}
			}
		}
	}

	// XXX some AI should declare war here...

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			szBuffer = gDLL->getText("TXT_KEY_MISC_NUKE_LAUNCHED", GET_PLAYER(getOwnerINLINE()).getNameKey(), getNameKey());
			gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)iI), (((PlayerTypes)iI) == getOwnerINLINE()), GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_NUKE_EXPLODES", MESSAGE_TYPE_MAJOR_EVENT, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE(), true, true);
		}
	}

	if (isSuicide())
	{
		logBBAI("    Killing %S (delayed) -- suicide nuking (Unit %d - plot: %d, %d)",
				getName().GetCString(), getID(), getX(), getY());
		kill(true);
	}

	return true;
}


bool CvUnit::canRecon(const CvPlot* pPlot) const
{
	if (getDomainType() != DOMAIN_AIR)
	{
		return false;
	}

	if (airRange() == 0)
	{
		return false;
	}

	if (m_pUnitInfo->isSuicide())
	{
		return false;
	}

	if (getImmobileTimer() > 0)
	{
		return false;
	}

	return true;
}



bool CvUnit::canReconAt(const CvPlot* pPlot, int iX, int iY) const
{
	if (!canRecon(pPlot))
	{
		return false;
	}

	int iDistance = plotDistance(pPlot->getX_INLINE(), pPlot->getY_INLINE(), iX, iY);
	if (iDistance > airRange() || 0 == iDistance)
	{
		return false;
	}

	return true;
}


bool CvUnit::recon(int iX, int iY)
{
	CvPlot* pPlot;

	if (!canReconAt(plot(), iX, iY))
	{
		return false;
	}

	pPlot = GC.getMapINLINE().plotINLINE(iX, iY);

	setReconPlot(pPlot);

	finishMoves();

	if (pPlot->isActiveVisible(false))
	{
		CvAirMissionDefinition kAirMission;
		kAirMission.setMissionType(MISSION_RECON);
		kAirMission.setUnit(BATTLE_UNIT_ATTACKER, this);
		kAirMission.setUnit(BATTLE_UNIT_DEFENDER, NULL);
		kAirMission.setDamage(BATTLE_UNIT_DEFENDER, 0);
		kAirMission.setDamage(BATTLE_UNIT_ATTACKER, 0);
		kAirMission.setPlot(pPlot);
		kAirMission.setMissionTime(GC.getMissionInfo((MissionTypes)MISSION_RECON).getTime() * gDLL->getSecsPerTurn());
		gDLL->getEntityIFace()->AddMission(&kAirMission);
	}

	return true;
}


bool CvUnit::canParadrop(const CvPlot* pPlot) const
{
	if (getDropRange() <= 0)
	{
		return false;
	}

	if (hasMoved())
	{
		return false;
	}

	if (!pPlot->isFriendlyCity(*this, true))
	{
		return false;
	}

	return true;
}



bool CvUnit::canParadropAt(const CvPlot* pPlot, int iX, int iY) const
{
	if (!canParadrop(pPlot))
	{
		return false;
	}

	CvPlot* pTargetPlot = GC.getMapINLINE().plotINLINE(iX, iY);
	if (NULL == pTargetPlot || pTargetPlot == pPlot)
	{
		return false;
	}

	if (!pTargetPlot->isVisible(getTeam(), false))
	{
		return false;
	}

	if (!canMoveInto(pTargetPlot, false, false, true))
	{
		return false;
	}

	if (plotDistance(pPlot->getX_INLINE(), pPlot->getY_INLINE(), iX, iY) > getDropRange())
	{
		return false;
	}

	if (!canCoexistWithEnemyUnit(NO_TEAM))
	{
		if (pTargetPlot->isEnemyCity(*this))
		{
			return false;
		}

		if (pTargetPlot->isVisibleEnemyUnit(this))
		{
			return false;
		}
	}

	return true;
}


bool CvUnit::paradrop(int iX, int iY)
{
	if (!canParadropAt(plot(), iX, iY))
	{
		return false;
	}

	CvPlot* pPlot = GC.getMapINLINE().plotINLINE(iX, iY);

	changeMoves(GC.getMOVE_DENOMINATOR() / 2);
	setMadeAttack(true);

	setXY(pPlot->getX_INLINE(), pPlot->getY_INLINE());

	//check if intercepted
	if(interceptTest(pPlot))
	{
		return true;
	}

	//play paradrop animation by itself
	if (pPlot->isActiveVisible(false))
	{
		CvAirMissionDefinition kAirMission;
		kAirMission.setMissionType(MISSION_PARADROP);
		kAirMission.setUnit(BATTLE_UNIT_ATTACKER, this);
		kAirMission.setUnit(BATTLE_UNIT_DEFENDER, NULL);
		kAirMission.setDamage(BATTLE_UNIT_DEFENDER, 0);
		kAirMission.setDamage(BATTLE_UNIT_ATTACKER, 0);
		kAirMission.setPlot(pPlot);
		kAirMission.setMissionTime(GC.getMissionInfo((MissionTypes)MISSION_PARADROP).getTime() * gDLL->getSecsPerTurn());
		gDLL->getEntityIFace()->AddMission(&kAirMission);
	}

	return true;
}


bool CvUnit::canAirBomb(const CvPlot* pPlot) const
{
	if (getDomainType() != DOMAIN_AIR)
	{
		return false;
	}

	if (airBombBaseRate() == 0)
	{
		return false;
	}

	if (isMadeAttack())
	{
		return false;
	}

	return true;
}


bool CvUnit::canAirBombAt(const CvPlot* pPlot, int iX, int iY) const
{
	CvCity* pCity;
	CvPlot* pTargetPlot;

	if (!canAirBomb(pPlot))
	{
		return false;
	}

	pTargetPlot = GC.getMapINLINE().plotINLINE(iX, iY);

	if (plotDistance(pPlot->getX_INLINE(), pPlot->getY_INLINE(), pTargetPlot->getX_INLINE(), pTargetPlot->getY_INLINE()) > airRange())
	{
		return false;
	}

	if (pTargetPlot->isOwned())
	{
		if (!potentialWarAction(pTargetPlot))
		{
			return false;
		}
	}

	pCity = pTargetPlot->getPlotCity();

	if (pCity != NULL)
	{
		if (!(pCity->isBombardable(this)))
		{
			return false;
		}
	}
	else
	{
		if (pTargetPlot->getImprovementType() == NO_IMPROVEMENT)
		{
			return false;
		}

		if (GC.getImprovementInfo(pTargetPlot->getImprovementType()).isPermanent())
		{
			return false;
		}

		if (GC.getImprovementInfo(pTargetPlot->getImprovementType()).getAirBombDefense() == -1)
		{
			return false;
		}
	}

	return true;
}


bool CvUnit::airBomb(int iX, int iY)
{
	CvCity* pCity;
	CvPlot* pPlot;
	CvWString szBuffer;

	if (!canAirBombAt(plot(), iX, iY))
	{
		return false;
	}

	pPlot = GC.getMapINLINE().plotINLINE(iX, iY);
	
/*************************************************************************************************/
/* Advanced Diplomacy         START                                                               */
/*************************************************************************************************/
	if (pPlot->isOwned() && pPlot->getTeam() != getTeam() && !GET_TEAM(getTeam()).isAtWar(pPlot->getTeam()))
	{
		GET_TEAM(pPlot->getTeam()).changeWarPretextAgainstCount(getTeam(), 1);
	}
/*************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/*************************************************************************************************/

	if (!isEnemy(pPlot->getTeam()))
	{
		getGroup()->groupDeclareWar(pPlot, true);
	}

	if (!isEnemy(pPlot->getTeam()))
	{
		return false;
	}

	if (interceptTest(pPlot))
	{
		return true;
	}

	pCity = pPlot->getPlotCity();

	if (pCity != NULL)
	{
		pCity->changeDefenseModifier(-airBombCurrRate());

		szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_DEFENSES_REDUCED_TO", pCity->getNameKey(), pCity->getDefenseModifier(false), getNameKey());
		gDLL->getInterfaceIFace()->addMessage(pCity->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BOMBARDED", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pCity->getX_INLINE(), pCity->getY_INLINE(), true, true);

		szBuffer = gDLL->getText("TXT_KEY_MISC_ENEMY_DEFENSES_REDUCED_TO", getNameKey(), pCity->getNameKey(), pCity->getDefenseModifier(false));
		gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BOMBARD", MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pCity->getX_INLINE(), pCity->getY_INLINE());
	}
	else
	{
		if (pPlot->getImprovementType() != NO_IMPROVEMENT)
		{
			if (GC.getGameINLINE().getSorenRandNum(airBombCurrRate(), "Air Bomb - Offense") >=
					GC.getGameINLINE().getSorenRandNum(GC.getImprovementInfo(pPlot->getImprovementType()).getAirBombDefense(), "Air Bomb - Defense"))
			{
				szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_UNIT_DESTROYED_IMP", getNameKey(), GC.getImprovementInfo(pPlot->getImprovementType()).getTextKeyWide());
				gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_PILLAGE", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE());

				if (pPlot->isOwned())
				{
					szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_IMP_WAS_DESTROYED", GC.getImprovementInfo(pPlot->getImprovementType()).getTextKeyWide(), getNameKey(), getVisualCivAdjective(pPlot->getTeam()));
					gDLL->getInterfaceIFace()->addMessage(pPlot->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_PILLAGED", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE(), true, true);
				}

				pPlot->setImprovementType((ImprovementTypes)(GC.getImprovementInfo(pPlot->getImprovementType()).getImprovementPillage()));
			}
			else
			{
				szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_UNIT_FAIL_DESTROY_IMP", getNameKey(), GC.getImprovementInfo(pPlot->getImprovementType()).getTextKeyWide());
				gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BOMB_FAILS", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
			}
		}
	}

	setReconPlot(pPlot);

	setMadeAttack(true);
	changeMoves(GC.getMOVE_DENOMINATOR());

	if (pPlot->isActiveVisible(false))
	{
		CvAirMissionDefinition kAirMission;
		kAirMission.setMissionType(MISSION_AIRBOMB);
		kAirMission.setUnit(BATTLE_UNIT_ATTACKER, this);
		kAirMission.setUnit(BATTLE_UNIT_DEFENDER, NULL);
		kAirMission.setDamage(BATTLE_UNIT_DEFENDER, 0);
		kAirMission.setDamage(BATTLE_UNIT_ATTACKER, 0);
		kAirMission.setPlot(pPlot);
		kAirMission.setMissionTime(GC.getMissionInfo((MissionTypes)MISSION_AIRBOMB).getTime() * gDLL->getSecsPerTurn());

		gDLL->getEntityIFace()->AddMission(&kAirMission);
	}

	if (isSuicide())
	{
		logBBAI("    Killing %S (delayed) -- suicide air bomb (Unit %d - plot: %d, %d)",
				getName().GetCString(), getID(), getX(), getY());
		kill(true);
	}

	return true;
}


CvCity* CvUnit::bombardTarget(const CvPlot* pPlot) const
{
	int iBestValue = MAX_INT;
	CvCity* pBestCity = NULL;

	for (int iI = 0; iI < NUM_DIRECTION_TYPES; iI++)
	{
		CvPlot* pLoopPlot = plotDirection(pPlot->getX_INLINE(), pPlot->getY_INLINE(), ((DirectionTypes)iI));

		if (pLoopPlot != NULL)
		{
			CvCity* pLoopCity = pLoopPlot->getPlotCity();

			if (pLoopCity != NULL)
			{
				if (pLoopCity->isBombardable(this))
				{
					int iValue = pLoopCity->getDefenseDamage();

					// always prefer cities we are at war with
					if (isEnemy(pLoopCity->getTeam(), pPlot))
					{
						iValue *= 128;
					}

					if (iValue < iBestValue)
					{
						iBestValue = iValue;
						pBestCity = pLoopCity;
					}
				}
			}
		}
	}

	return pBestCity;
}

// Super Forts begin *bombard*
CvPlot* CvUnit::bombardImprovementTarget(const CvPlot* pPlot) const
{
	int iBestValue = MAX_INT;
	CvPlot* pBestPlot = NULL;

	if (!GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS))
	{
		return pBestPlot;
	}

	for (int iI = 0; iI < NUM_DIRECTION_TYPES; iI++)
	{
		CvPlot* pLoopPlot = plotDirection(pPlot->getX_INLINE(), pPlot->getY_INLINE(), ((DirectionTypes)iI));

		if (pLoopPlot != NULL)
		{
			if (pLoopPlot->isBombardable(this))
			{
				int iValue = pLoopPlot->getDefenseDamage();

				// always prefer cities we are at war with
				if (isEnemy(pLoopPlot->getTeam(), pPlot))
				{
					iValue *= 128;
				}

				if (iValue < iBestValue)
				{
					iBestValue = iValue;
					pBestPlot = pLoopPlot;
				}
			}
		}
	}

	return pBestPlot;
}
// Super Forts end

bool CvUnit::canBombard(const CvPlot* pPlot) const
{
	if (bombardRate() <= 0)
	{
		return false;
	}

	if (isMadeAttack())
	{
		return false;
	}

	if (isCargo())
	{
		return false;
	}

	// Super Forts begin *bombard*
	if (bombardTarget(pPlot) == NULL && bombardImprovementTarget(pPlot) == NULL)
	//if (bombardTarget(pPlot) == NULL) - Original Code
	// Super Forts end
	{
		return false;
	}

	return true;
}


bool CvUnit::bombard()
{
	CvPlot* pPlot = plot();
	if (!canBombard(pPlot))
	{
		return false;
	}

	CvCity* pBombardCity = bombardTarget(pPlot);
	// Super Forts begin *bombard*
	//FAssertMsg(pBombardCity != NULL, "BombardCity is not assigned a valid value"); - Removed for Super Forts

	CvPlot* pTargetPlot;
	//CvPlot* pTargetPlot = pBombardCity->plot(); - Original Code
	if(pBombardCity != NULL)
	{
		pTargetPlot = pBombardCity->plot();
	}
	else
	{
		pTargetPlot = bombardImprovementTarget(pPlot);
	}
	// Super Forts end
	
/*************************************************************************************************/
/* Advanced Diplomacy         START                                                               */
/*************************************************************************************************/
	if (pTargetPlot->isOwned() && pTargetPlot->getTeam() != getTeam() && !GET_TEAM(getTeam()).isAtWar(pTargetPlot->getTeam()))
	{
		GET_TEAM(pTargetPlot->getTeam()).changeWarPretextAgainstCount(getTeam(), 1);
	}
/*************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/*************************************************************************************************/

	if (!isEnemy(pTargetPlot->getTeam()))
	{
		getGroup()->groupDeclareWar(pTargetPlot, true);
	}

	if (!isEnemy(pTargetPlot->getTeam()))
	{
		return false;
	}

	int iBombardModifier = 0;
	// Super Forts begin *bombard* *text*
	if(pBombardCity != NULL)
	{
		if (!ignoreBuildingDefense())
		{
			iBombardModifier -= pBombardCity->getBuildingBombardDefense();
		}

		int iTotalBombard = (-(bombardRate() * std::max(0, 100 + iBombardModifier)) / 100);
		pBombardCity->changeDefenseModifier(iTotalBombard);

		//CvWString szBuffer = gDLL->getText("TXT_KEY_MISC_DEFENSES_IN_CITY_REDUCED_TO", pBombardCity->getNameKey(), pBombardCity->getDefenseModifier(false), GET_PLAYER(getOwnerINLINE()).getNameKey());
		CvWString szBuffer = gDLL->getText("TXT_KEY_MISC_DEFENSES_IN_CITY_REDUCED_TO", pBombardCity->getNameKey(), pBombardCity->getDefenseModifier(false), getNameKey());
		gDLL->getInterfaceIFace()->addMessage(pBombardCity->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BOMBARDED", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pBombardCity->getX_INLINE(), pBombardCity->getY_INLINE(), true, true);
	
		szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_REDUCE_CITY_DEFENSES", getNameKey(), pBombardCity->getNameKey(), pBombardCity->getDefenseModifier(false));
		gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BOMBARD", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pBombardCity->getX_INLINE(), pBombardCity->getY_INLINE());
	
		// Start Advanced Tactics - Bombarding can grant experience
		if (GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS))
		{
			if ((iTotalBombard) > GC.getGameINLINE().getSorenRandNum(100, "Bombard Experience"))
			{
				changeExperience(1);
			}
		}
		// End Advanced Tactics
	}
	else
	{
		pTargetPlot->changeDefenseDamage(bombardRate());

		CvWString szBuffer = gDLL->getText("TXT_KEY_MISC_DEFENSES_IN_CITY_REDUCED_TO", GC.getImprovementInfo(pTargetPlot->getImprovementType()).getText(),
			(GC.getImprovementInfo(pTargetPlot->getImprovementType()).getDefenseModifier()-pTargetPlot->getDefenseDamage()), GET_PLAYER(getOwnerINLINE()).getNameKey());
		gDLL->getInterfaceIFace()->addMessage(pTargetPlot->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BOMBARDED", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pTargetPlot->getX_INLINE(), pTargetPlot->getY_INLINE(), true, true);

		szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_REDUCE_CITY_DEFENSES", getNameKey(), GC.getImprovementInfo(pTargetPlot->getImprovementType()).getText(), 
			(GC.getImprovementInfo(pTargetPlot->getImprovementType()).getDefenseModifier()-pTargetPlot->getDefenseDamage()));
		gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BOMBARD", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pTargetPlot->getX_INLINE(), pTargetPlot->getY_INLINE());
	}
	// Super Forts end

	setMadeAttack(true);
	changeMoves(GC.getMOVE_DENOMINATOR());

	if (pPlot->isActiveVisible(false))
	{
		// Super Forts begin *bombard*
		CvUnit *pDefender = pTargetPlot->getBestDefender(NO_PLAYER, getOwnerINLINE(), this, true);
		//CvUnit *pDefender = pBombardCity->plot()->getBestDefender(NO_PLAYER, getOwnerINLINE(), this, true); - Original Code
		// Super Forts end

		// Bombard entity mission
		CvMissionDefinition kDefiniton;
		kDefiniton.setMissionTime(GC.getMissionInfo(MISSION_BOMBARD).getTime() * gDLL->getSecsPerTurn());
		kDefiniton.setMissionType(MISSION_BOMBARD);
		// Super Forts begin *bombard*
		kDefiniton.setPlot(pTargetPlot);
		//kDefiniton.setPlot(pBombardCity->plot()); - Original Code
		// Super Forts end
		kDefiniton.setUnit(BATTLE_UNIT_ATTACKER, this);
		kDefiniton.setUnit(BATTLE_UNIT_DEFENDER, pDefender);
		gDLL->getEntityIFace()->AddMission(&kDefiniton);
	}

//FfH: Added by Kael 08/30/2007
    if (isSuicide())
    {
		logBBAI("    Killing %S (delayed) -- suicide bombard (Unit %d - plot: %d, %d)",
				getName().GetCString(), getID(), getX(), getY());
        kill(true);
    }
//FfH: End Add

	return true;
}


bool CvUnit::canPillage(const CvPlot* pPlot) const
{
	if (!(m_pUnitInfo->isPillage()))
	{
		return false;
	}

	if (pPlot->isCity())
	{
		return false;
	}

/************************************************************************************************/
/* UNOFFICIAL_PATCH                       06/23/10                     Mongoose & jdog5000      */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
	// From Mongoose SDK
	if (isCargo())
	{
		return false;
	}
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/

	if (pPlot->getImprovementType() == NO_IMPROVEMENT)
	{
		if (!(pPlot->isRoute()))
		{
			return false;
		}
	}
	else
	{
		if (GC.getImprovementInfo(pPlot->getImprovementType()).isPermanent())
		{
			return false;
		}
	}

	if (pPlot->isOwned())
	{
		if (!potentialWarAction(pPlot))
		{
			if (GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS) && pPlot->getOwnerINLINE() == getOwnerINLINE())
			{
				 //  Advanced Tactics - can pillage own plots
				return true;
			}
			else
			{
				if ((pPlot->getImprovementType() == NO_IMPROVEMENT) || (pPlot->getOwnerINLINE() != getOwnerINLINE()))
				{
					return false;
				}
			}
		}
	}

	if (!(pPlot->isValidDomainForAction(*this)))
	{
		return false;
	}

//FfH: Added by Kael 03/24/2009
    if (isBarbarian())
    {
        if (pPlot->getImprovementType() != NO_IMPROVEMENT)
        {
            if (GC.getImprovementInfo(pPlot->getImprovementType()).getSpawnUnitType() != NO_UNIT)
            {
                return false;
            }
        }
		//added Sephi
		if (pPlot->isGoody())
		{
			return false;
		}
    }
//FfH: End Add

	return true;
}


bool CvUnit::pillage()
{
	CvWString szBuffer;
	int iPillageGold;
	long lPillageGold;
	ImprovementTypes eTempImprovement = NO_IMPROVEMENT;
	RouteTypes eTempRoute = NO_ROUTE;

	CvPlot* pPlot = plot();

	if (!canPillage(pPlot))
	{
		return false;
	}

	if (pPlot->isOwned() && pPlot->getOwner() != getOwner())
	{
		// we should not be calling this without declaring war first, so do not declare war here
		if (!isEnemy(pPlot->getTeam(), pPlot))
		{
			if ((pPlot->getImprovementType() == NO_IMPROVEMENT) || (pPlot->getOwnerINLINE() != getOwnerINLINE()))
			{
				return false;
			}
		}
	}

	if (pPlot->isWater())
	{
		CvUnit* pInterceptor = bestSeaPillageInterceptor(this, GC.defines.iCOMBAT_DIE_SIDES / 2);
		if (NULL != pInterceptor)
		{
			setMadeAttack(false);

			int iWithdrawal = withdrawalProbability();
			changeExtraWithdrawal(-iWithdrawal); // no withdrawal since we are really the defender
			attack(pInterceptor->plot(), false);
			changeExtraWithdrawal(iWithdrawal);

			return false;
		}
	}

	// Advanced Tactics - Pillaging reduces Culture
	if (GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS))
	{
		for (int iPlayer = 0; iPlayer < MAX_CIV_PLAYERS; ++iPlayer)
		{
			CvPlayer& kLoopPlayer = GET_PLAYER((PlayerTypes)iPlayer);
			if (kLoopPlayer.isAlive())
			{
				int iLoopPlayerPlotCulture = pPlot->getCulture((PlayerTypes)iPlayer);
				if (iLoopPlayerPlotCulture > 0)
				{
					int iCultureChange = 100;// * pPlot->getImprovementDuration();

					 // extra loss for pillaging unit's culture
					if (getOwner() == iPlayer)
					{
						// unless it's Hidden Nationality
						if (!isHiddenNationality())
						{
							iCultureChange *= 2;
						}
					}

					// lfgr 09/2019: Cannot reduce culture to 0 (otherwise plot may become unowned)
					if (iCultureChange >= iLoopPlayerPlotCulture)
					{
						iCultureChange = iLoopPlayerPlotCulture - 1;
					}

					pPlot->changeCulture((PlayerTypes)iPlayer, -iCultureChange, true);
				}
			}
		}
	}
	// End Advanced Tactics

	if (pPlot->getImprovementType() != NO_IMPROVEMENT)
	{
		eTempImprovement = pPlot->getImprovementType();

		if (pPlot->getTeam() != getTeam())
		{
			// Use python to determine pillage amounts...
			lPillageGold = 0;

			CyPlot* pyPlot = new CyPlot(pPlot);
			CyUnit* pyUnit = new CyUnit(this);

			CyArgsList argsList;
			argsList.add(gDLL->getPythonIFace()->makePythonObject(pyPlot));	// pass in plot class
			argsList.add(gDLL->getPythonIFace()->makePythonObject(pyUnit));	// pass in unit class

			gDLL->getPythonIFace()->callFunction(PYGameModule, "doPillageGold", argsList.makeFunctionArgs(),&lPillageGold);

			delete pyPlot;	// python fxn must not hold on to this pointer
			delete pyUnit;	// python fxn must not hold on to this pointer

			iPillageGold = (int)lPillageGold;

			if (iPillageGold > 0)
			{

//FfH Traits: Added by Kael 08/02/2007
                iPillageGold += (iPillageGold * GET_PLAYER(getOwnerINLINE()).getPillagingGold()) / 100;
//FfH: End Add

				GET_PLAYER(getOwnerINLINE()).changeGold(iPillageGold);

				szBuffer = gDLL->getText("TXT_KEY_MISC_PLUNDERED_GOLD_FROM_IMP", iPillageGold, GC.getImprovementInfo(pPlot->getImprovementType()).getTextKeyWide());
				gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_PILLAGE", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE());

				if (pPlot->isOwned())
				{
					// Tholal AI - pillaging affects War Success
					// lfgr fix 03/2021: Only for non-HN units
					if( !isHiddenNationality() && ( iPillageGold > 10 || pPlot->getBonusType() != NO_BONUS ) )
					{
						GET_TEAM(getTeam()).AI_changeWarSuccess(pPlot->getTeam(), 1);
					}
					// End Tholal AI

					// Start Advanced Tactics - Pillaging can grant experience
					if (GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS))
					{
						if ((iPillageGold * 3) > GC.getGameINLINE().getSorenRandNum(100, "Pillage Experience"))
						{
							changeExperience(1);
						}
					}
					// End Advanced Tactics

					szBuffer = gDLL->getText("TXT_KEY_MISC_IMP_DESTROYED", GC.getImprovementInfo(pPlot->getImprovementType()).getTextKeyWide(), getNameKey(), getVisualCivAdjective(pPlot->getTeam()));
					gDLL->getInterfaceIFace()->addMessage(pPlot->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_PILLAGED", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE(), true, true);
				}
			}
		}

		pPlot->setImprovementType((ImprovementTypes)(GC.getImprovementInfo(pPlot->getImprovementType()).getImprovementPillage()));
	}
	else if (pPlot->isRoute())
	{
		eTempRoute = pPlot->getRouteType();
		pPlot->setRouteType(NO_ROUTE, true); // XXX downgrade rail???

		// Show messages when roads are pillaged. Based on code by The_J.
		szBuffer = gDLL->getText("TXT_KEY_MISC_IMP_DESTROYED", GC.getRouteInfo(eTempRoute).getTextKeyWide(), getNameKey(), getVisualCivAdjective(pPlot->getTeam()));
		gDLL->getInterfaceIFace()->addMessage(pPlot->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_PILLAGED", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE(), true, true);
		// Show messages when roads are pillaged END
	}

	changeMoves(GC.getMOVE_DENOMINATOR());

	if (pPlot->isActiveVisible(false))
	{
		// Pillage entity mission
		CvMissionDefinition kDefiniton;
		kDefiniton.setMissionTime(GC.getMissionInfo(MISSION_PILLAGE).getTime() * gDLL->getSecsPerTurn());
		kDefiniton.setMissionType(MISSION_PILLAGE);
		kDefiniton.setPlot(pPlot);
		kDefiniton.setUnit(BATTLE_UNIT_ATTACKER, this);
		kDefiniton.setUnit(BATTLE_UNIT_DEFENDER, NULL);
		gDLL->getEntityIFace()->AddMission(&kDefiniton);
	}

	if (eTempImprovement != NO_IMPROVEMENT || eTempRoute != NO_ROUTE)
	{
		CvEventReporter::getInstance().unitPillage(this, eTempImprovement, eTempRoute, getOwnerINLINE());
	}

//FfH: Added by Kael 03/02/2009
    for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
    {
        if (isHasPromotion((PromotionTypes)iI))
        {
            if (GC.getPromotionInfo((PromotionTypes)iI).isRemovedByCombat())
            {
                setHasPromotion(((PromotionTypes)iI), false);
		    }
        }
    }
//FfH: End Add

	return true;
}


bool CvUnit::canPlunder(const CvPlot* pPlot, bool bTestVisible) const
{
	if (getDomainType() != DOMAIN_SEA)
	{
		return false;
	}

	if (!(m_pUnitInfo->isPillage()))
	{
		return false;
	}

	if (!pPlot->isWater())
	{
		return false;
	}

	if (pPlot->isFreshWater())
	{
		return false;
	}

	if (!pPlot->isValidDomainForAction(*this))
	{
		return false;
	}

	if (!bTestVisible)
	{
		if (pPlot->getTeam() == getTeam())
		{
			return false;
		}
	}

	return true;
}


bool CvUnit::plunder()
{
	CvPlot* pPlot = plot();

	if (!canPlunder(pPlot))
	{
		return false;
	}

	setBlockading(true);

	finishMoves();
	
/*************************************************************************************************/
/* Advanced Diplomacy         START                                                               */
/*************************************************************************************************/
	if (pPlot->isOwned() && pPlot->getTeam() != getTeam() && !GET_TEAM(getTeam()).isAtWar(pPlot->getTeam()))
	{
		GET_TEAM(pPlot->getTeam()).changeWarPretextAgainstCount(getTeam(), 1);
	}
/*************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/*************************************************************************************************/

	return true;
}


void CvUnit::updatePlunder(int iChange, bool bUpdatePlotGroups)
{
	int iBlockadeRange = GC.defines.iSHIP_BLOCKADE_RANGE;

	bool bOldTradeNet;
	bool bChanged = false;

	for (int iTeam = 0; iTeam < MAX_TEAMS; ++iTeam)
	{
		if (isEnemy((TeamTypes)iTeam))
		{
			for (int i = -iBlockadeRange; i <= iBlockadeRange; ++i)
			{
				for (int j = -iBlockadeRange; j <= iBlockadeRange; ++j)
				{
					CvPlot* pLoopPlot = ::plotXY(getX_INLINE(), getY_INLINE(), i, j);

					if (NULL != pLoopPlot && pLoopPlot->isWater() && pLoopPlot->area() == area())
					{
						if (!bChanged)
						{
							bOldTradeNet = pLoopPlot->isTradeNetwork((TeamTypes)iTeam);
						}

						pLoopPlot->changeBlockadedCount((TeamTypes)iTeam, iChange);

						if (!bChanged)
						{
							bChanged = (bOldTradeNet != pLoopPlot->isTradeNetwork((TeamTypes)iTeam));
						}
					}
				}
			}
		}
	}

	if (bChanged)
	{
		gDLL->getInterfaceIFace()->setDirty(BlockadedPlots_DIRTY_BIT, true);

		if (bUpdatePlotGroups)
		{
			GC.getGameINLINE().updatePlotGroups();
		}
	}
}


int CvUnit::sabotageCost(const CvPlot* pPlot) const
{
	return GC.defines.iBASE_SPY_SABOTAGE_COST;
}


// XXX compare with destroy prob...
int CvUnit::sabotageProb(const CvPlot* pPlot, ProbabilityTypes eProbStyle) const
{
	CvPlot* pLoopPlot;
	int iDefenseCount;
	int iCounterSpyCount;
	int iProb;
	int iI;

	iProb = 0; // XXX

	if (pPlot->isOwned())
	{
		iDefenseCount = pPlot->plotCount(PUF_canDefend, -1, -1, NO_PLAYER, pPlot->getTeam());
		iCounterSpyCount = pPlot->plotCount(PUF_isCounterSpy, -1, -1, NO_PLAYER, pPlot->getTeam());

		for (iI = 0; iI < NUM_DIRECTION_TYPES; iI++)
		{
			pLoopPlot = plotDirection(pPlot->getX_INLINE(), pPlot->getY_INLINE(), ((DirectionTypes)iI));

			if (pLoopPlot != NULL)
			{
				iCounterSpyCount += pLoopPlot->plotCount(PUF_isCounterSpy, -1, -1, NO_PLAYER, pPlot->getTeam());
			}
		}
	}
	else
	{
		iDefenseCount = 0;
		iCounterSpyCount = 0;
	}

	if (eProbStyle == PROBABILITY_HIGH)
	{
		iCounterSpyCount = 0;
	}

	iProb += (40 / (iDefenseCount + 1)); // XXX

	if (eProbStyle != PROBABILITY_LOW)
	{
		iProb += (50 / (iCounterSpyCount + 1)); // XXX
	}

	return iProb;
}


bool CvUnit::canSabotage(const CvPlot* pPlot, bool bTestVisible) const
{
	if (!(m_pUnitInfo->isSabotage()))
	{
		return false;
	}

	if (pPlot->getTeam() == getTeam())
	{
		return false;
	}

	if (pPlot->isCity())
	{
		return false;
	}

	if (pPlot->getImprovementType() == NO_IMPROVEMENT)
	{
		return false;
	}

	if (!bTestVisible)
	{
		if (GET_PLAYER(getOwnerINLINE()).getGold() < sabotageCost(pPlot))
		{
			return false;
		}
	}

	return true;
}


bool CvUnit::sabotage()
{
	CvCity* pNearestCity;
	CvPlot* pPlot;
	CvWString szBuffer;
	bool bCaught;

	if (!canSabotage(plot()))
	{
		return false;
	}

	pPlot = plot();

	bCaught = (GC.getGameINLINE().getSorenRandNum(100, "Spy: Sabotage") > sabotageProb(pPlot));

	GET_PLAYER(getOwnerINLINE()).changeGold(-(sabotageCost(pPlot)));

	if (!bCaught)
	{
		pPlot->setImprovementType((ImprovementTypes)(GC.getImprovementInfo(pPlot->getImprovementType()).getImprovementPillage()));

		finishMoves();

		pNearestCity = GC.getMapINLINE().findCity(pPlot->getX_INLINE(), pPlot->getY_INLINE(), pPlot->getOwnerINLINE(), NO_TEAM, false);

		if (pNearestCity != NULL)
		{
			szBuffer = gDLL->getText("TXT_KEY_MISC_SPY_SABOTAGED", getNameKey(), pNearestCity->getNameKey());
			gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_SABOTAGE", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE());

			if (pPlot->isOwned())
			{
				szBuffer = gDLL->getText("TXT_KEY_MISC_SABOTAGE_NEAR", pNearestCity->getNameKey());
				gDLL->getInterfaceIFace()->addMessage(pPlot->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_SABOTAGE", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE(), true, true);
			}
		}

		if (pPlot->isActiveVisible(false))
		{
			NotifyEntity(MISSION_SABOTAGE);
		}
	}
	else
	{
		if (pPlot->isOwned())
		{
			szBuffer = gDLL->getText("TXT_KEY_MISC_SPY_CAUGHT_AND_KILLED", GET_PLAYER(getOwnerINLINE()).getCivilizationAdjective(), getNameKey());
			gDLL->getInterfaceIFace()->addMessage(pPlot->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_EXPOSE", MESSAGE_TYPE_INFO);
		}

		szBuffer = gDLL->getText("TXT_KEY_MISC_YOUR_SPY_CAUGHT", getNameKey());
		gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_EXPOSED", MESSAGE_TYPE_INFO);

		if (plot()->isActiveVisible(false))
		{
			NotifyEntity(MISSION_SURRENDER);
		}

		if (pPlot->isOwned())
		{
			if (!isEnemy(pPlot->getTeam(), pPlot))
			{
				GET_PLAYER(pPlot->getOwnerINLINE()).AI_changeMemoryCount(getOwnerINLINE(), MEMORY_SPY_CAUGHT, 1);
			}
		}
		
		logBBAI("    Killing %S (delayed) -- did sabotage (Unit %d - plot: %d, %d)",
				getName().GetCString(), getID(), getX(), getY());
		kill(true, pPlot->getOwnerINLINE());
	}

	return true;
}


int CvUnit::destroyCost(const CvPlot* pPlot) const
{
	CvCity* pCity;
	bool bLimited;

	pCity = pPlot->getPlotCity();

	if (pCity == NULL)
	{
		return 0;
	}

	bLimited = false;

	if (pCity->isProductionUnit())
	{
		bLimited = isLimitedUnitClass((UnitClassTypes)(GC.getUnitInfo(pCity->getProductionUnit()).getUnitClassType()));
	}
	else if (pCity->isProductionBuilding())
	{
		bLimited = isLimitedWonderClass((BuildingClassTypes)(GC.getBuildingInfo(pCity->getProductionBuilding()).getBuildingClassType()));
	}
	else if (pCity->isProductionProject())
	{
		bLimited = isLimitedProject(pCity->getProductionProject());
	}

	return (GC.defines.iBASE_SPY_DESTROY_COST + (pCity->getProduction() * ((bLimited) ? GC.defines.iSPY_DESTROY_COST_MULTIPLIER_LIMITED : GC.defines.iSPY_DESTROY_COST_MULTIPLIER)));
}


int CvUnit::destroyProb(const CvPlot* pPlot, ProbabilityTypes eProbStyle) const
{
	CvCity* pCity;
	CvPlot* pLoopPlot;
	int iDefenseCount;
	int iCounterSpyCount;
	int iProb;
	int iI;

	pCity = pPlot->getPlotCity();

	if (pCity == NULL)
	{
		return 0;
	}

	iProb = 0; // XXX

	iDefenseCount = pPlot->plotCount(PUF_canDefend, -1, -1, NO_PLAYER, pPlot->getTeam());

	iCounterSpyCount = pPlot->plotCount(PUF_isCounterSpy, -1, -1, NO_PLAYER, pPlot->getTeam());

	for (iI = 0; iI < NUM_DIRECTION_TYPES; iI++)
	{
		pLoopPlot = plotDirection(pPlot->getX_INLINE(), pPlot->getY_INLINE(), ((DirectionTypes)iI));

		if (pLoopPlot != NULL)
		{
			iCounterSpyCount += pLoopPlot->plotCount(PUF_isCounterSpy, -1, -1, NO_PLAYER, pPlot->getTeam());
		}
	}

	if (eProbStyle == PROBABILITY_HIGH)
	{
		iCounterSpyCount = 0;
	}

	iProb += (25 / (iDefenseCount + 1)); // XXX

	if (eProbStyle != PROBABILITY_LOW)
	{
		iProb += (50 / (iCounterSpyCount + 1)); // XXX
	}

	iProb += std::min(25, pCity->getProductionTurnsLeft()); // XXX

	return iProb;
}


bool CvUnit::canDestroy(const CvPlot* pPlot, bool bTestVisible) const
{
	CvCity* pCity;

	if (!(m_pUnitInfo->isDestroy()))
	{
		return false;
	}

	if (pPlot->getTeam() == getTeam())
	{
		return false;
	}

	pCity = pPlot->getPlotCity();

	if (pCity == NULL)
	{
		return false;
	}

	if (pCity->getProduction() == 0)
	{
		return false;
	}

	if (!bTestVisible)
	{
		if (GET_PLAYER(getOwnerINLINE()).getGold() < destroyCost(pPlot))
		{
			return false;
		}
	}

	return true;
}


bool CvUnit::destroy()
{
	CvCity* pCity;
	CvWString szBuffer;
	bool bCaught;

	if (!canDestroy(plot()))
	{
		return false;
	}

	bCaught = (GC.getGameINLINE().getSorenRandNum(100, "Spy: Destroy") > destroyProb(plot()));

	pCity = plot()->getPlotCity();
	FAssertMsg(pCity != NULL, "City is not assigned a valid value");

	GET_PLAYER(getOwnerINLINE()).changeGold(-(destroyCost(plot())));

	if (!bCaught)
	{
		pCity->setProduction(pCity->getProduction() / 2);

		finishMoves();

		szBuffer = gDLL->getText("TXT_KEY_MISC_SPY_DESTROYED_PRODUCTION", getNameKey(), pCity->getProductionNameKey(), pCity->getNameKey());
		gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_DESTROY", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pCity->getX_INLINE(), pCity->getY_INLINE());

		szBuffer = gDLL->getText("TXT_KEY_MISC_CITY_PRODUCTION_DESTROYED", pCity->getProductionNameKey(), pCity->getNameKey());
		gDLL->getInterfaceIFace()->addMessage(pCity->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_DESTROY", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pCity->getX_INLINE(), pCity->getY_INLINE(), true, true);

		if (plot()->isActiveVisible(false))
		{
			NotifyEntity(MISSION_DESTROY);
		}
	}
	else
	{
		szBuffer = gDLL->getText("TXT_KEY_MISC_SPY_CAUGHT_AND_KILLED", GET_PLAYER(getOwnerINLINE()).getCivilizationAdjective(), getNameKey());
		gDLL->getInterfaceIFace()->addMessage(pCity->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_EXPOSE", MESSAGE_TYPE_INFO);

		szBuffer = gDLL->getText("TXT_KEY_MISC_YOUR_SPY_CAUGHT", getNameKey());
		gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_EXPOSED", MESSAGE_TYPE_INFO);

		if (plot()->isActiveVisible(false))
		{
			NotifyEntity(MISSION_SURRENDER);
		}

		if (!isEnemy(pCity->getTeam()))
		{
			GET_PLAYER(pCity->getOwnerINLINE()).AI_changeMemoryCount(getOwnerINLINE(), MEMORY_SPY_CAUGHT, 1);
		}
		
		logBBAI("    Killing %S (delayed) -- destroyed (by espionage?) (Unit %d - plot: %d, %d)",
				getName().GetCString(), getID(), getX(), getY());
		kill(true, pCity->getOwnerINLINE());
	}

	return true;
}


int CvUnit::stealPlansCost(const CvPlot* pPlot) const
{
	CvCity* pCity;

	pCity = pPlot->getPlotCity();

	if (pCity == NULL)
	{
		return 0;
	}

	return (GC.defines.iBASE_SPY_STEAL_PLANS_COST + ((GET_TEAM(pCity->getTeam()).getTotalLand() + GET_TEAM(pCity->getTeam()).getTotalPopulation()) * GC.defines.iSPY_STEAL_PLANS_COST_MULTIPLIER));
}


// XXX compare with destroy prob...
int CvUnit::stealPlansProb(const CvPlot* pPlot, ProbabilityTypes eProbStyle) const
{
	CvCity* pCity;
	CvPlot* pLoopPlot;
	int iDefenseCount;
	int iCounterSpyCount;
	int iProb;
	int iI;

	pCity = pPlot->getPlotCity();

	if (pCity == NULL)
	{
		return 0;
	}

	iProb = ((pCity->isGovernmentCenter()) ? 20 : 0); // XXX

	iDefenseCount = pPlot->plotCount(PUF_canDefend, -1, -1, NO_PLAYER, pPlot->getTeam());

	iCounterSpyCount = pPlot->plotCount(PUF_isCounterSpy, -1, -1, NO_PLAYER, pPlot->getTeam());

	for (iI = 0; iI < NUM_DIRECTION_TYPES; iI++)
	{
		pLoopPlot = plotDirection(pPlot->getX_INLINE(), pPlot->getY_INLINE(), ((DirectionTypes)iI));

		if (pLoopPlot != NULL)
		{
			iCounterSpyCount += pLoopPlot->plotCount(PUF_isCounterSpy, -1, -1, NO_PLAYER, pPlot->getTeam());
		}
	}

	if (eProbStyle == PROBABILITY_HIGH)
	{
		iCounterSpyCount = 0;
	}

	iProb += (20 / (iDefenseCount + 1)); // XXX

	if (eProbStyle != PROBABILITY_LOW)
	{
		iProb += (50 / (iCounterSpyCount + 1)); // XXX
	}

	return iProb;
}


bool CvUnit::canStealPlans(const CvPlot* pPlot, bool bTestVisible) const
{
	CvCity* pCity;

	if (!(m_pUnitInfo->isStealPlans()))
	{
		return false;
	}

	if (pPlot->getTeam() == getTeam())
	{
		return false;
	}

	pCity = pPlot->getPlotCity();

	if (pCity == NULL)
	{
		return false;
	}

	if (!bTestVisible)
	{
		if (GET_PLAYER(getOwnerINLINE()).getGold() < stealPlansCost(pPlot))
		{
			return false;
		}
	}

	return true;
}


bool CvUnit::stealPlans()
{
	CvCity* pCity;
	CvWString szBuffer;
	bool bCaught;

	if (!canStealPlans(plot()))
	{
		return false;
	}

	bCaught = (GC.getGameINLINE().getSorenRandNum(100, "Spy: Steal Plans") > stealPlansProb(plot()));

	pCity = plot()->getPlotCity();
	FAssertMsg(pCity != NULL, "City is not assigned a valid value");

	GET_PLAYER(getOwnerINLINE()).changeGold(-(stealPlansCost(plot())));

	if (!bCaught)
	{
		GET_TEAM(getTeam()).changeStolenVisibilityTimer(pCity->getTeam(), 2);

		finishMoves();

		szBuffer = gDLL->getText("TXT_KEY_MISC_SPY_STOLE_PLANS", getNameKey(), pCity->getNameKey());
		gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_STEALPLANS", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pCity->getX_INLINE(), pCity->getY_INLINE());

		szBuffer = gDLL->getText("TXT_KEY_MISC_PLANS_STOLEN", pCity->getNameKey());
		gDLL->getInterfaceIFace()->addMessage(pCity->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_STEALPLANS", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pCity->getX_INLINE(), pCity->getY_INLINE(), true, true);

		if (plot()->isActiveVisible(false))
		{
			NotifyEntity(MISSION_STEAL_PLANS);
		}
	}
	else
	{
		szBuffer = gDLL->getText("TXT_KEY_MISC_SPY_CAUGHT_AND_KILLED", GET_PLAYER(getOwnerINLINE()).getCivilizationAdjective(), getNameKey());
		gDLL->getInterfaceIFace()->addMessage(pCity->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_EXPOSE", MESSAGE_TYPE_INFO);

		szBuffer = gDLL->getText("TXT_KEY_MISC_YOUR_SPY_CAUGHT", getNameKey());
		gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_EXPOSED", MESSAGE_TYPE_INFO);

		if (plot()->isActiveVisible(false))
		{
			NotifyEntity(MISSION_SURRENDER);
		}

		if (!isEnemy(pCity->getTeam()))
		{
			GET_PLAYER(pCity->getOwnerINLINE()).AI_changeMemoryCount(getOwnerINLINE(), MEMORY_SPY_CAUGHT, 1);
		}
		
		logBBAI("    Killing %S (delayed) -- stole plans (Unit %d - plot: %d, %d)",
			getName().GetCString(), getID(), getX(), getY());
		kill(true, pCity->getOwnerINLINE());
	}

	return true;
}


bool CvUnit::canFound(const CvPlot* pPlot, bool bTestVisible) const
{
	if (!isFound())
	{
		return false;
	}

	if (!(GET_PLAYER(getOwnerINLINE()).canFound(pPlot->getX_INLINE(), pPlot->getY_INLINE(), bTestVisible)))
	{
		return false;
	}

//FfH: Added by Kael 05/06/2010
    if (pPlot->isFoundDisabled())
    {
        return false;
    }
    if (isHasCasted())
    {
        return false;
    }
//FfH: End Add

	return true;
}


bool CvUnit::found()
{
	if (!canFound(plot()))
	{
		return false;
	}

	if (GC.getGameINLINE().getActivePlayer() == getOwnerINLINE())
	{
		gDLL->getInterfaceIFace()->lookAt(plot()->getPoint(), CAMERALOOKAT_NORMAL);
	}

	GET_PLAYER(getOwnerINLINE()).found(getX_INLINE(), getY_INLINE());

	if (plot()->isActiveVisible(false))
	{
		NotifyEntity(MISSION_FOUND);
	}
	
	logBBAI("    Killing %S (delayed) -- founded city (Unit %d - plot: %d, %d)",
			getName().GetCString(), getID(), getX(), getY());
	kill(true);

	return true;
}


bool CvUnit::canSpread(const CvPlot* pPlot, ReligionTypes eReligion, bool bTestVisible) const
{
	CvCity* pCity;

/************************************************************************************************/
/* UNOFFICIAL_PATCH                       08/19/09                                jdog5000      */
/*                                                                                              */
/* Efficiency                                                                                   */
/************************************************************************************************/
/* orginal bts code
	if (GC.getUSE_USE_CANNOT_SPREAD_RELIGION_CALLBACK())
	{
		CyArgsList argsList;
		argsList.add(getOwnerINLINE());
		argsList.add(getID());
		argsList.add((int) eReligion);
		argsList.add(pPlot->getX());
		argsList.add(pPlot->getY());
		long lResult=0;
		gDLL->getPythonIFace()->callFunction(PYGameModule, "cannotSpreadReligion", argsList.makeFunctionArgs(), &lResult);
		if (lResult > 0)
		{
			return false;
		}
	}
*/
				// UP efficiency: Moved below faster calls
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/

	if (eReligion == NO_RELIGION)
	{
		return false;
	}

	if (m_pUnitInfo->getReligionSpreads(eReligion) <= 0)
	{
		return false;
	}

	pCity = pPlot->getPlotCity();

	if (pCity == NULL)
	{
		return false;
	}

	if (pCity->isBarbarian())
	{
		return false;
	}

	if (pCity->isHasReligion(eReligion))
	{
		return false;
	}

	if (!canEnterArea(pPlot->getTeam(), pPlot->area()))
	{
		return false;
	}

	if (!bTestVisible)
	{
		if (pCity->getTeam() != getTeam())
		{
			if (GET_PLAYER(pCity->getOwnerINLINE()).isNoNonStateReligionSpread())
			{
				if (eReligion != GET_PLAYER(pCity->getOwnerINLINE()).getStateReligion())
				{
					return false;
				}
			}
		}
	}

/************************************************************************************************/
/* UNOFFICIAL_PATCH                       08/19/09                                jdog5000      */
/*                                                                                              */
/* Efficiency                                                                                   */
/************************************************************************************************/
	if (GC.getUSE_USE_CANNOT_SPREAD_RELIGION_CALLBACK())
	{
		CyArgsList argsList;
		argsList.add(getOwnerINLINE());
		argsList.add(getID());
		argsList.add((int) eReligion);
		argsList.add(pPlot->getX());
		argsList.add(pPlot->getY());
		long lResult=0;
		gDLL->getPythonIFace()->callFunction(PYGameModule, "cannotSpreadReligion", argsList.makeFunctionArgs(), &lResult);
		if (lResult > 0)
		{
			return false;
		}
	}
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/

	return true;
}


bool CvUnit::spread(ReligionTypes eReligion)
{
	CvCity* pCity;
	CvWString szBuffer;
	int iSpreadProb;

	if (!canSpread(plot(), eReligion))
	{
		return false;
	}

	pCity = plot()->getPlotCity();

	if (pCity != NULL)
	{
		iSpreadProb = m_pUnitInfo->getReligionSpreads(eReligion);

		if (pCity->getTeam() != getTeam())
		{
			iSpreadProb /= 2;
		}

		bool bSuccess;

		iSpreadProb += (((GC.getNumReligionInfos() - pCity->getReligionCount()) * (100 - iSpreadProb)) / GC.getNumReligionInfos());

		if (GC.getGameINLINE().getSorenRandNum(100, "Unit Spread Religion") < iSpreadProb)
		{

//FfH: Modified by Kael 10/04/2008
//			pCity->setHasReligion(eReligion, true, true, false);
            if (GC.getGameINLINE().isReligionFounded(eReligion))
            {
                pCity->setHasReligion(eReligion, true, true, false);
            }
            else
            {
                pCity->setHasReligion(eReligion, true, true, false);
                GC.getGameINLINE().setHolyCity(eReligion, pCity, true);
                GC.getGameINLINE().setReligionSlotTaken(eReligion, true);
            }
//FfH: End Modify

			bSuccess = true;
		}
		else
		{
			szBuffer = gDLL->getText("TXT_KEY_MISC_RELIGION_FAILED_TO_SPREAD", getNameKey(), GC.getReligionInfo(eReligion).getChar(), pCity->getNameKey());
			gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_NOSPREAD", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pCity->getX_INLINE(), pCity->getY_INLINE());
			bSuccess = false;
		}

		// Python Event
		CvEventReporter::getInstance().unitSpreadReligionAttempt(this, eReligion, bSuccess);
	}

	if (plot()->isActiveVisible(false))
	{
		NotifyEntity(MISSION_SPREAD);
	}
	
	logBBAI("    Killing %S (delayed) -- spread religion (Unit %d - plot: %d, %d)",
		getName().GetCString(), getID(), getX(), getY());
	kill(true);

	return true;
}


bool CvUnit::canSpreadCorporation(const CvPlot* pPlot, CorporationTypes eCorporation, bool bTestVisible) const
{
	if (NO_CORPORATION == eCorporation)
	{
		return false;
	}

	if (!GET_PLAYER(getOwnerINLINE()).isActiveCorporation(eCorporation))
	{
		return false;
	}

	if (m_pUnitInfo->getCorporationSpreads(eCorporation) <= 0)
	{
		return false;
	}

	CvCity* pCity = pPlot->getPlotCity();

	if (NULL == pCity)
	{
		return false;
	}

	if (pCity->isHasCorporation(eCorporation))
	{
		return false;
	}

	if (!canEnterArea(pPlot->getTeam(), pPlot->area()))
	{
		return false;
	}

	if (!bTestVisible)
	{
		if (!GET_PLAYER(pCity->getOwnerINLINE()).isActiveCorporation(eCorporation))
		{
			return false;
		}

		for (int iCorporation = 0; iCorporation < GC.getNumCorporationInfos(); ++iCorporation)
		{
			if (pCity->isHeadquarters((CorporationTypes)iCorporation))
			{
				if (GC.getGameINLINE().isCompetingCorporation((CorporationTypes)iCorporation, eCorporation))
				{
					return false;
				}
			}
		}

		bool bValid = false;

//FfH: Added by Kael 10/21/2007 (So that corporations can be made to not require bonuses)
        if (GC.getCorporationInfo(eCorporation).getPrereqBonus(0) == NO_BONUS)
        {
            bValid = true;
        }
//FfH: End Add

		for (int i = 0; i < GC.getNUM_CORPORATION_PREREQ_BONUSES(); ++i)
		{
			BonusTypes eBonus = (BonusTypes)GC.getCorporationInfo(eCorporation).getPrereqBonus(i);
			if (NO_BONUS != eBonus)
			{
				if (pCity->hasBonus(eBonus))
				{
					bValid = true;
					break;
				}
			}
		}

		if (!bValid)
		{
			return false;
		}

		if (GET_PLAYER(getOwnerINLINE()).getGold() < spreadCorporationCost(eCorporation, pCity))
		{
			return false;
		}
	}

	return true;
}

int CvUnit::spreadCorporationCost(CorporationTypes eCorporation, CvCity* pCity) const
{
	int iCost = std::max(0, GC.getCorporationInfo(eCorporation).getSpreadCost() * (100 + GET_PLAYER(getOwnerINLINE()).calculateInflationRate()));
	iCost /= 100;

	if (NULL != pCity)
	{
		if (getTeam() != pCity->getTeam() && !GET_TEAM(pCity->getTeam()).isVassal(getTeam()))
		{
			iCost *= GC.defines.iCORPORATION_FOREIGN_SPREAD_COST_PERCENT;
			iCost /= 100;
		}

		for (int iCorp = 0; iCorp < GC.getNumCorporationInfos(); ++iCorp)
		{
			if (iCorp != eCorporation)
			{
				if (pCity->isActiveCorporation((CorporationTypes)iCorp))
				{
					if (GC.getGameINLINE().isCompetingCorporation(eCorporation, (CorporationTypes)iCorp))
					{
						iCost *= 100 + GC.getCorporationInfo((CorporationTypes)iCorp).getSpreadFactor();
						iCost /= 100;
					}
				}
			}
		}
	}

	return iCost;
}

bool CvUnit::spreadCorporation(CorporationTypes eCorporation)
{
	int iSpreadProb;

	if (!canSpreadCorporation(plot(), eCorporation))
	{
		return false;
	}

	CvCity* pCity = plot()->getPlotCity();

	if (NULL != pCity)
	{
		GET_PLAYER(getOwnerINLINE()).changeGold(-spreadCorporationCost(eCorporation, pCity));

		iSpreadProb = m_pUnitInfo->getCorporationSpreads(eCorporation);

		if (pCity->getTeam() != getTeam())
		{
			iSpreadProb /= 2;
		}

		iSpreadProb += (((GC.getNumCorporationInfos() - pCity->getCorporationCount()) * (100 - iSpreadProb)) / GC.getNumCorporationInfos());

		if (GC.getGameINLINE().getSorenRandNum(100, "Unit Spread Corporation") < iSpreadProb)
		{
			pCity->setHasCorporation(eCorporation, true, true, false);
		}
		else
		{
			CvWString szBuffer = gDLL->getText("TXT_KEY_MISC_CORPORATION_FAILED_TO_SPREAD", getNameKey(), GC.getCorporationInfo(eCorporation).getChar(), pCity->getNameKey());
			gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_NOSPREAD", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pCity->getX_INLINE(), pCity->getY_INLINE());
		}
	}

	if (plot()->isActiveVisible(false))
	{
		NotifyEntity(MISSION_SPREAD_CORPORATION);
	}
	
	logBBAI("    Killing %S (delayed) -- spread corporation (Unit %d - plot: %d, %d)",
		getName().GetCString(), getID(), getX(), getY());
	kill(true);

	return true;
}


bool CvUnit::canJoin(const CvPlot* pPlot, SpecialistTypes eSpecialist) const
{
	if (isHasPromotion((PromotionTypes) GC.getInfoTypeForString("PROMOTION_ILLUSION")))
	{
		return false;
	}

	CvCity* pCity;

	if (eSpecialist == NO_SPECIALIST)
	{
		return false;
	}

	if (!(m_pUnitInfo->getGreatPeoples(eSpecialist)))
	{
		return false;
	}

	pCity = pPlot->getPlotCity();

	if (pCity == NULL)
	{
		return false;
	}

	if (!(pCity->canJoin()))
	{
		return false;
	}

	if (pCity->getTeam() != getTeam())
	{
		return false;
	}

	if (isDelayedDeath())
	{
		return false;
	}

//FfH: Added by Kael 08/18/2008
    if (isHasCasted())
    {
        return false;
    }
//FfH: End Add

	return true;
}


bool CvUnit::join(SpecialistTypes eSpecialist)
{
	CvCity* pCity;

	if (!canJoin(plot(), eSpecialist))
	{
		return false;
	}

	pCity = plot()->getPlotCity();

	if (pCity != NULL)
	{
		pCity->changeFreeSpecialistCount(eSpecialist, 1);
	}

	if (plot()->isActiveVisible(false))
	{
		NotifyEntity(MISSION_JOIN);
	}
	
	logBBAI("    Killing %S (delayed) -- joined city as a specialist (Unit %d - plot: %d, %d)",
			getName().GetCString(), getID(), getX(), getY());
	kill(true);

	return true;
}


bool CvUnit::canConstruct(const CvPlot* pPlot, BuildingTypes eBuilding, bool bTestVisible) const
{
	CvCity* pCity;

	if (eBuilding == NO_BUILDING)
	{
		return false;
	}

	if (isHasPromotion((PromotionTypes) GC.getInfoTypeForString("PROMOTION_ILLUSION")))
	{
		return false;
	}

//FfH: Added by Kael 08/18/2008
    if (isHasCasted())
    {
        return false;
    }
//FfH: End Add

	pCity = pPlot->getPlotCity();

	if (pCity == NULL)
	{
		return false;
	}

	if (getTeam() != pCity->getTeam())
	{
		return false;
	}

	if (pCity->getNumRealBuilding(eBuilding) > 0)
	{
		return false;
	}

	if (!(m_pUnitInfo->getForceBuildings(eBuilding)))
	{
		if (!(m_pUnitInfo->getBuildings(eBuilding)))
		{
			return false;
		}

		if (!(pCity->canConstruct(eBuilding, false, bTestVisible, true)))
		{
			return false;
		}
	}

	if (isDelayedDeath())
	{
		return false;
	}

	return true;
}


bool CvUnit::construct(BuildingTypes eBuilding)
{
	CvCity* pCity;

	if (!canConstruct(plot(), eBuilding))
	{
		return false;
	}

	pCity = plot()->getPlotCity();

	if (pCity != NULL)
	{
		pCity->setNumRealBuilding(eBuilding, pCity->getNumRealBuilding(eBuilding) + 1);

		CvEventReporter::getInstance().buildingBuilt(pCity, eBuilding);
	}

	if (plot()->isActiveVisible(false))
	{
		NotifyEntity(MISSION_CONSTRUCT);
	}
	
	logBBAI("    Killing %S (delayed) -- constructed building (Unit %d - plot: %d, %d)",
			getName().GetCString(), getID(), getX(), getY());
	kill(true);

	return true;
}


TechTypes CvUnit::getDiscoveryTech() const
{
	return ::getDiscoveryTech(getUnitType(), getOwnerINLINE());
}


int CvUnit::getDiscoverResearch(TechTypes eTech) const
{

//FfH: Added by Kael 08/18/2008
    if (isHasCasted())
    {
        return 0;
    }
//FfH: End Add

	int iResearch = (m_pUnitInfo->getBaseDiscover() + (m_pUnitInfo->getDiscoverMultiplier() * GET_TEAM(getTeam()).getTotalPopulation()));
	if (iResearch > 0) {
		iResearch *= GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getUnitDiscoverPercent();
		iResearch /= 100;
		if (eTech != NO_TECH)
		{
			iResearch = std::min(GET_TEAM(getTeam()).getResearchLeft(eTech), iResearch);
		}
	} else if (iResearch < 0) {
		iResearch = 0;
	}

	return iResearch;
}


bool CvUnit::canDiscover(const CvPlot* pPlot) const
{
	// The TechTypes parameter is only used for checking the maximum value that the discover research can take.
	// In this case we only want to check if the unit can make any research at all, so the parameter is not needed.
	if (getDiscoverResearch(NO_TECH) == 0)
	{
		return false;
	}

	TechTypes eTech;

	eTech = getDiscoveryTech();

	if (eTech == NO_TECH)
	{
		return false;
	}

	if (isDelayedDeath())
	{
		return false;
	}

	return true;
}


bool CvUnit::discover()
{
	TechTypes eDiscoveryTech;

	if (!canDiscover(plot()))
	{
		return false;
	}

	eDiscoveryTech = getDiscoveryTech();
	FAssertMsg(eDiscoveryTech != NO_TECH, "DiscoveryTech is not assigned a valid value");

	GET_TEAM(getTeam()).changeResearchProgress(eDiscoveryTech, getDiscoverResearch(eDiscoveryTech), getOwnerINLINE());

	if (plot()->isActiveVisible(false))
	{
		NotifyEntity(MISSION_DISCOVER);
	}
	
	// lfgr 07/2019: transport units unload cargo when they discover a technology
	if (getCargo() > 0)
	{
		unloadAll();
	}
	
	logBBAI("    Killing %S (delayed) -- discovered tech (Unit %d - plot: %d, %d)",
			getName().GetCString(), getID(), getX(), getY());
	kill(true);

	return true;
}


int CvUnit::getMaxHurryProduction(CvCity* pCity) const
{
	int iProduction;

	iProduction = (m_pUnitInfo->getBaseHurry() + (m_pUnitInfo->getHurryMultiplier() * pCity->getPopulation()));

	iProduction *= GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getUnitHurryPercent();
	iProduction /= 100;

//FfH: Added by Kael 08/18/2008
    if (isHasCasted())
    {
        return 0;
    }
//FfH: End Add

	return std::max(0, iProduction);
}


int CvUnit::getHurryProduction(const CvPlot* pPlot) const
{
	CvCity* pCity;
	int iProduction;

	pCity = pPlot->getPlotCity();

	if (pCity == NULL)
	{
		return 0;
	}

	iProduction = getMaxHurryProduction(pCity);

	iProduction = std::min(pCity->productionLeft(), iProduction);

	return std::max(0, iProduction);
}


bool CvUnit::canHurry(const CvPlot* pPlot, bool bTestVisible) const
{
	if (isHasPromotion((PromotionTypes) GC.getInfoTypeForString("PROMOTION_ILLUSION")))
	{
		return false;
	}

	if (isDelayedDeath())
	{
		return false;
	}

	CvCity* pCity;

	if (getHurryProduction(pPlot) == 0)
	{
		return false;
	}

	pCity = pPlot->getPlotCity();

	if (pCity == NULL)
	{
		return false;
	}

	if (pCity->getProductionTurnsLeft() == 1)
	{
		return false;
	}

	if (!bTestVisible)
	{
		if (!(pCity->isProductionBuilding()))
		{
			return false;
		}
	}

	return true;
}


bool CvUnit::hurry()
{
	CvCity* pCity;

	if (!canHurry(plot()))
	{
		return false;
	}

	pCity = plot()->getPlotCity();

	if (pCity != NULL)
	{
		pCity->changeProduction(getHurryProduction(plot()));
	}

	if (plot()->isActiveVisible(false))
	{
		NotifyEntity(MISSION_HURRY);
	}

	// lfgr 07/2019: transport units unload cargo when they hurry production
	if (getCargo() > 0)
	{
		unloadAll();
	}
	
	logBBAI("    Killing %S (delayed) -- Hurried production (Unit %d - plot: %d, %d)",
			getName().GetCString(), getID(), getX(), getY());
	kill(true);

	return true;
}


int CvUnit::getTradeGold(const CvPlot* pPlot) const
{
	CvCity* pCapitalCity;
	CvCity* pCity;
	int iGold;

	pCity = pPlot->getPlotCity();
	pCapitalCity = GET_PLAYER(getOwnerINLINE()).getCapitalCity();

	if (pCity == NULL)
	{
		return 0;
	}

	iGold = (m_pUnitInfo->getBaseTrade() + (m_pUnitInfo->getTradeMultiplier() * ((pCapitalCity != NULL) ? pCity->calculateTradeProfit(pCapitalCity) : 0)));

	iGold *= GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getUnitTradePercent();
	iGold /= 100;
	
/************************************************************************************************/
/* Stolenrays	              Start		 		                                                */
/* Advanced Diplomacy                                                                           */
/************************************************************************************************/
	//More Gold From Free Trade Agreement Trade Missions
	PlayerTypes eTargetPlayer = pPlot->getOwnerINLINE();

	if (GET_TEAM(getTeam()).isFreeTradeAgreement(GET_PLAYER(eTargetPlayer).getTeam()))
	{
		iGold *= 100 + GC.defines.iFREE_TRADE_AGREEMENT_TRADE_MODIFIER;
		iGold /= 100;
	}
	
	//Gold Sound 
	if (plot()->isActiveVisible(false))
	{
		gDLL->getInterfaceIFace()->playGeneralSound("AS2D_COINS");
	}	
/************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/************************************************************************************************/	

//FfH: Added by Kael 08/18/2008
    if (isHasCasted())
    {
        return 0;
    }
//FfH: End Add

	return std::max(0, iGold);
}


bool CvUnit::canTrade(const CvPlot* pPlot, bool bTestVisible) const
{
	if (isDelayedDeath())
	{
		return false;
	}

	CvCity* pCity = pPlot->getPlotCity();

	if (pCity == NULL)
	{
		return false;
	}

	if (getTradeGold(pPlot) == 0)
	{
		return false;
	}

	if (!canEnterArea(pPlot->getTeam(), pPlot->area()))
	{
		return false;
	}

	if (!bTestVisible)
	{
		if (pCity->getTeam() == getTeam())
		{
			return false;
		}
	}

	return true;
}


bool CvUnit::trade()
{
	if (!canTrade(plot()))
	{
		return false;
	}

	GET_PLAYER(getOwnerINLINE()).changeGold(getTradeGold(plot()));

	if (plot()->isActiveVisible(false))
	{
		NotifyEntity(MISSION_TRADE);
	}

	// lfgr 07/2019: transport units unload cargo when they trade
	if (getCargo() > 0)
	{
		unloadAll();
	}
	
	logBBAI("    Killing %S (delayed) -- traded (Unit %d - plot: %d, %d)",
		getName().GetCString(), getID(), getX(), getY());
	kill(true);

	return true;
}


int CvUnit::getGreatWorkCulture(const CvPlot* pPlot) const
{
	int iCulture;

	iCulture = m_pUnitInfo->getGreatWorkCulture();

	iCulture *= GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getUnitGreatWorkPercent();
	iCulture /= 100;

//FfH: Added by Kael 08/18/2008
    if (isHasCasted())
    {
        return 0;
    }
//FfH: End Add

	return std::max(0, iCulture);
}


bool CvUnit::canGreatWork(const CvPlot* pPlot) const
{
	if (isHasPromotion((PromotionTypes) GC.getInfoTypeForString("PROMOTION_ILLUSION")))
	{
		return false;
	}

	if (isDelayedDeath())
	{
		return false;
	}

	CvCity* pCity = pPlot->getPlotCity();

	if (pCity == NULL)
	{
		return false;
	}

	if (pCity->getOwnerINLINE() != getOwnerINLINE())
	{
		return false;
	}

	if (getGreatWorkCulture(pPlot) == 0)
	{
		return false;
	}

	return true;
}


bool CvUnit::greatWork()
{
	if (!canGreatWork(plot()))
	{
		return false;
	}

	CvCity* pCity = plot()->getPlotCity();

	if (pCity != NULL)
	{
		pCity->setCultureUpdateTimer(0);
		pCity->setOccupationTimer(0);

		int iCultureToAdd = 100 * getGreatWorkCulture(plot());
		int iNumTurnsApplied = (GC.defines.iGREAT_WORKS_CULTURE_TURNS * GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getUnitGreatWorkPercent()) / 100;

		for (int i = 0; i < iNumTurnsApplied; ++i)
		{
			pCity->changeCultureTimes100(getOwnerINLINE(), iCultureToAdd / iNumTurnsApplied, true, true);
		}

		if (iNumTurnsApplied > 0)
		{
			pCity->changeCultureTimes100(getOwnerINLINE(), iCultureToAdd % iNumTurnsApplied, false, true);
		}
	}

	if (plot()->isActiveVisible(false))
	{
		NotifyEntity(MISSION_GREAT_WORK);
	}

	// lfgr 07/2019: transport units unload cargo when they create a great work
	if (getCargo() > 0)
	{
		unloadAll();
	}
	
	logBBAI("    Killing %S (delayed) -- created great work (Unit %d - plot: %d, %d)",
			getName().GetCString(), getID(), getX(), getY());
	kill(true);

	return true;
}


int CvUnit::getEspionagePoints(const CvPlot* pPlot) const
{
	int iEspionagePoints;

	iEspionagePoints = m_pUnitInfo->getEspionagePoints();

	iEspionagePoints *= GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getUnitGreatWorkPercent();
	iEspionagePoints /= 100;

	return std::max(0, iEspionagePoints);
}

bool CvUnit::canInfiltrate(const CvPlot* pPlot, bool bTestVisible) const
{
	if (isDelayedDeath())
	{
		return false;
	}

	if (GC.getGameINLINE().isOption(GAMEOPTION_NO_ESPIONAGE))
	{
		return false;
	}

	if (getEspionagePoints(NULL) == 0)
	{
		return false;
	}

	CvCity* pCity = pPlot->getPlotCity();
	if (pCity == NULL || pCity->isBarbarian())
	{
		return false;
	}

	if (!bTestVisible)
	{
		if (NULL != pCity && pCity->getTeam() == getTeam())
		{
			return false;
		}
	}

	return true;
}


bool CvUnit::infiltrate()
{
	if (!canInfiltrate(plot()))
	{
		return false;
	}

	int iPoints = getEspionagePoints(NULL);
	GET_TEAM(getTeam()).changeEspionagePointsAgainstTeam(GET_PLAYER(plot()->getOwnerINLINE()).getTeam(), iPoints);
	GET_TEAM(getTeam()).changeEspionagePointsEver(iPoints);

	if (plot()->isActiveVisible(false))
	{
		NotifyEntity(MISSION_INFILTRATE);
	}
	
	logBBAI("    Killing %S (delayed) -- infiltrated (Unit %d - plot: %d, %d)",
			getName().GetCString(), getID(), getX(), getY());
	kill(true);

	return true;
}


bool CvUnit::canEspionage(const CvPlot* pPlot, bool bTestVisible) const
{
	if (isDelayedDeath())
	{
		return false;
	}

	if (!isSpy())
	{
		return false;
	}

	if (GC.getGameINLINE().isOption(GAMEOPTION_NO_ESPIONAGE))
	{
		return false;
	}

	PlayerTypes ePlotOwner = pPlot->getOwnerINLINE();
	if (NO_PLAYER == ePlotOwner)
	{
		return false;
	}

	CvPlayer& kTarget = GET_PLAYER(ePlotOwner);

	if (kTarget.isBarbarian())
	{
		return false;
	}

	if (kTarget.getTeam() == getTeam())
	{
		return false;
	}

	if (GET_TEAM(getTeam()).isVassal(kTarget.getTeam()))
	{
		return false;
	}

	if (!bTestVisible)
	{
		if (isMadeAttack())
		{
			return false;
		}

		if (hasMoved())
		{
			return false;
		}

		if (kTarget.getTeam() != getTeam() && !isInvisible(kTarget.getTeam(), false))
		{
			return false;
		}
	}

	return true;
}

bool CvUnit::espionage(EspionageMissionTypes eMission, int iData)
{
	if (!canEspionage(plot()))
	{
		return false;
	}

	PlayerTypes eTargetPlayer = plot()->getOwnerINLINE();

	if (NO_ESPIONAGEMISSION == eMission)
	{
		FAssert(GET_PLAYER(getOwnerINLINE()).isHuman());
		CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_DOESPIONAGE);
		if (NULL != pInfo)
		{
			gDLL->getInterfaceIFace()->addPopup(pInfo, getOwnerINLINE(), true);
		}
	}
	else if (GC.getEspionageMissionInfo(eMission).isTwoPhases() && -1 == iData)
	{
		FAssert(GET_PLAYER(getOwnerINLINE()).isHuman());
		CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_DOESPIONAGE_TARGET);
		if (NULL != pInfo)
		{
			pInfo->setData1(eMission);
			gDLL->getInterfaceIFace()->addPopup(pInfo, getOwnerINLINE(), true);
		}
	}
	else
	{
		if (testSpyIntercepted(eTargetPlayer, GC.getEspionageMissionInfo(eMission).getDifficultyMod()))
		{
			return false;
		}

		if (GET_PLAYER(getOwnerINLINE()).doEspionageMission(eMission, eTargetPlayer, plot(), iData, this))
		{
			if (plot()->isActiveVisible(false))
			{
				NotifyEntity(MISSION_ESPIONAGE);
			}

			if (!testSpyIntercepted(eTargetPlayer, GC.defines.iESPIONAGE_SPY_MISSION_ESCAPE_MOD))
			{
				setFortifyTurns(0);
				setMadeAttack(true);
				finishMoves();

				CvCity* pCapital = GET_PLAYER(getOwnerINLINE()).getCapitalCity();
				if (NULL != pCapital)
				{
					setXY(pCapital->getX_INLINE(), pCapital->getY_INLINE(), false, false, false);

					CvWString szBuffer = gDLL->getText("TXT_KEY_ESPIONAGE_SPY_SUCCESS", getNameKey(), pCapital->getNameKey());
					gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_POSITIVE_DINK", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_WHITE"), pCapital->getX_INLINE(), pCapital->getY_INLINE(), true, true);
				}
			}

			return true;
		}
	}

	return false;
}

bool CvUnit::testSpyIntercepted(PlayerTypes eTargetPlayer, int iModifier)
{
	CvPlayer& kTargetPlayer = GET_PLAYER(eTargetPlayer);

	if (kTargetPlayer.isBarbarian())
	{
		return false;
	}

	if (GC.getGameINLINE().getSorenRandNum(10000, "Spy Interception") >= getSpyInterceptPercent(kTargetPlayer.getTeam()) * (100 + iModifier))
	{
		return false;
	}

	CvString szFormatNoReveal;
	CvString szFormatReveal;

	if (GET_TEAM(kTargetPlayer.getTeam()).getCounterespionageModAgainstTeam(getTeam()) > 0)
	{
		szFormatNoReveal = "TXT_KEY_SPY_INTERCEPTED_MISSION";
		szFormatReveal = "TXT_KEY_SPY_INTERCEPTED_MISSION_REVEAL";
	}
	else if (plot()->isEspionageCounterSpy(kTargetPlayer.getTeam()))
	{
		szFormatNoReveal = "TXT_KEY_SPY_INTERCEPTED_SPY";
		szFormatReveal = "TXT_KEY_SPY_INTERCEPTED_SPY_REVEAL";
	}
	else
	{
		szFormatNoReveal = "TXT_KEY_SPY_INTERCEPTED";
		szFormatReveal = "TXT_KEY_SPY_INTERCEPTED_REVEAL";
	}

	CvWString szCityName = kTargetPlayer.getCivilizationShortDescription();
	CvCity* pClosestCity = GC.getMapINLINE().findCity(getX_INLINE(), getY_INLINE(), eTargetPlayer, kTargetPlayer.getTeam(), true, false);
	if (pClosestCity != NULL)
	{
		szCityName = pClosestCity->getName();
	}

	CvWString szBuffer = gDLL->getText(szFormatReveal.GetCString(), GET_PLAYER(getOwnerINLINE()).getCivilizationAdjectiveKey(), getNameKey(), kTargetPlayer.getCivilizationAdjectiveKey(), szCityName.GetCString());
	gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_EXPOSED", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), getX_INLINE(), getY_INLINE(), true, true);

	if (GC.getGameINLINE().getSorenRandNum(100, "Spy Reveal identity") < GC.defines.iESPIONAGE_SPY_REVEAL_IDENTITY_PERCENT)
	{
		if (!isEnemy(kTargetPlayer.getTeam()))
		{
			GET_PLAYER(eTargetPlayer).AI_changeMemoryCount(getOwnerINLINE(), MEMORY_SPY_CAUGHT, 1);
		}

		gDLL->getInterfaceIFace()->addMessage(eTargetPlayer, true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_EXPOSE", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), getX_INLINE(), getY_INLINE(), true, true);
	}
	else
	{
		szBuffer = gDLL->getText(szFormatNoReveal.GetCString(), getNameKey(), kTargetPlayer.getCivilizationAdjectiveKey(), szCityName.GetCString());
		gDLL->getInterfaceIFace()->addMessage(eTargetPlayer, true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_EXPOSE", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), getX_INLINE(), getY_INLINE(), true, true);
	}

	if (plot()->isActiveVisible(false))
	{
		NotifyEntity(MISSION_SURRENDER);
	}

	
	logBBAI("    Killing %S (delayed) -- spy intercepted (Unit %d - plot: %d, %d)",
		getName().GetCString(), getID(), getX(), getY());
	kill(true);
	
/*************************************************************************************************/
/* Advanced Diplomacy         START                                                               */
/*************************************************************************************************/

	if (GET_PLAYER(eTargetPlayer).getTeam() != getTeam() && !GET_TEAM(getTeam()).isAtWar(GET_PLAYER(eTargetPlayer).getTeam()))
	{
		GET_TEAM(GET_PLAYER(eTargetPlayer).getTeam()).changeWarPretextAgainstCount(getTeam(), 1);
	}
/*************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/*************************************************************************************************/

	return true;
}

int CvUnit::getSpyInterceptPercent(TeamTypes eTargetTeam) const
{
	FAssert(isSpy());
	FAssert(getTeam() != eTargetTeam);

	int iSuccess = 0;

	int iTargetPoints = GET_TEAM(eTargetTeam).getEspionagePointsEver();
	int iOurPoints = GET_TEAM(getTeam()).getEspionagePointsEver();
	iSuccess += (GC.defines.iESPIONAGE_INTERCEPT_SPENDING_MAX * iTargetPoints) / std::max(1, iTargetPoints + iOurPoints);

	if (plot()->isEspionageCounterSpy(eTargetTeam))
	{
		iSuccess += GC.defines.iESPIONAGE_INTERCEPT_COUNTERSPY;
	}

	if (GET_TEAM(eTargetTeam).getCounterespionageModAgainstTeam(getTeam()) > 0)
	{
		iSuccess += GC.defines.iESPIONAGE_INTERCEPT_COUNTERESPIONAGE_MISSION;
	}

	if (0 == getFortifyTurns() || plot()->plotCount(PUF_isSpy, -1, -1, NO_PLAYER, getTeam()) > 1)
	{
		iSuccess += GC.defines.iESPIONAGE_INTERCEPT_RECENT_MISSION;
	}

	return std::min(100, std::max(0, iSuccess));
}

bool CvUnit::isIntruding() const
{
	TeamTypes eLocalTeam = plot()->getTeam();
	
	if (NO_TEAM == eLocalTeam || eLocalTeam == getTeam())
	{
		return false;
	}

	// UNOFFICIAL_PATCH Start
	// * Vassal's spies no longer caught in master's territory
	//if (GET_TEAM(eLocalTeam).isVassal(getTeam()))
	if (GET_TEAM(eLocalTeam).isVassal(getTeam()) || GET_TEAM(getTeam()).isVassal(eLocalTeam))
	// UNOFFICIAL_PATCH End
	{
		return false;
	}

	return true;
}

bool CvUnit::canGoldenAge(const CvPlot* pPlot, bool bTestVisible) const
{
	if (!isGoldenAge())
	{
		return false;
	}

	if (isHasPromotion((PromotionTypes) GC.getInfoTypeForString("PROMOTION_ILLUSION")))
	{
		return false;
	}

	if (!bTestVisible)
	{
		if (GET_PLAYER(getOwnerINLINE()).unitsRequiredForGoldenAge() > GET_PLAYER(getOwnerINLINE()).unitsGoldenAgeReady())
		{
			return false;
		}
	}

	return true;
}


bool CvUnit::goldenAge()
{
	if (!canGoldenAge(plot()))
	{
		return false;
	}

	GET_PLAYER(getOwnerINLINE()).killGoldenAgeUnits(this);

	GET_PLAYER(getOwnerINLINE()).changeGoldenAgeTurns(GET_PLAYER(getOwnerINLINE()).getGoldenAgeLength());
	GET_PLAYER(getOwnerINLINE()).changeNumUnitGoldenAges(1);

	if (plot()->isActiveVisible(false))
	{
		NotifyEntity(MISSION_GOLDEN_AGE);
	}

	// lfgr 07/2019: transport units unload cargo when they start a golden age
	if (getCargo() > 0)
	{
		unloadAll();
	}
	
	logBBAI("    Killing %S (delayed) -- started golden age (Unit %d - plot: %d, %d)",
			getName().GetCString(), getID(), getX(), getY());
	kill(true);

	return true;
}


bool CvUnit::canBuild(const CvPlot* pPlot, BuildTypes eBuild, bool bTestVisible) const
{
    FAssertMsg(eBuild < GC.getNumBuildInfos(), "Index out of bounds");
	if (!(m_pUnitInfo->getBuilds(eBuild)))
	{
		return false;
	}

	if (!(GET_PLAYER(getOwnerINLINE()).canBuild(pPlot, eBuild, false, bTestVisible)))
	{
		return false;
	}

	if (!pPlot->isValidDomainForAction(*this))
	{
		return false;
	}

/*************************************************************************************************/
/**	ADDON (stop automated workers from building forts) Sephi                                    **/
/**	                																			**/
/**						                                            							**/
/*************************************************************************************************/
    if (isAutomated())
    {
        if (eBuild == GC.defines.iBUILD_FORT)
        {
            return false;
        }
    }
/*************************************************************************************************/
/**	END                                                                  						**/
/*************************************************************************************************/

	return true;
}

// Returns true if build finished...
bool CvUnit::build(BuildTypes eBuild)
{
	bool bFinished;

	FAssertMsg(eBuild < GC.getNumBuildInfos(), "Invalid Build");

	if (!canBuild(plot(), eBuild))
	{
		return false;
	}

	// Note: notify entity must come before changeBuildProgress - because once the unit is done building,
	// that function will notify the entity to stop building.
	NotifyEntity((MissionTypes)GC.getBuildInfo(eBuild).getMissionType());

	GET_PLAYER(getOwnerINLINE()).changeGold(-(GET_PLAYER(getOwnerINLINE()).getBuildCost(plot(), eBuild)));

	bFinished = plot()->changeBuildProgress(eBuild, workRate(false), getTeam());

	finishMoves(); // needs to be at bottom because movesLeft() can affect workRate()...

	if (bFinished)
	{
		// Super Forts begin *culture*
		if (GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS) && GC.getBuildInfo(eBuild).getImprovement() != NO_IMPROVEMENT)
		{
			if(GC.getImprovementInfo((ImprovementTypes)GC.getBuildInfo(eBuild).getImprovement()).isActsAsCity())
			{
				if(plot()->getOwner() == NO_PLAYER)
				{
					plot()->setOwner(getOwnerINLINE(),true,true);
				}
			}
		}
		// Super Forts end

		if (GC.getBuildInfo(eBuild).isKill())
		{
			logBBAI("    Killing %S (delayed) -- building improvement (Unit %d - plot: %d, %d)",
					getName().GetCString(), getID(), getX(), getY());
			kill(true);
		}

/************************************************************************************************/
/* Advanced Diplomacy         START                                                              */
/************************************************************************************************/
		if (GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS))
		{
			int iI = 0;
		
			if (plot()->getOwnerINLINE() != NO_PLAYER && plot()->getOwnerINLINE() != getOwnerINLINE())
			{
				GET_PLAYER((PlayerTypes)iI).AI_changeMemoryCount(getOwnerINLINE(), MEMORY_WORKED_PLOT, 1);
			}
		}
/************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/************************************************************************************************/
	}

	// Python Event
	CvEventReporter::getInstance().unitBuildImprovement(this, eBuild, bFinished);

	return bFinished;
}


bool CvUnit::canPromote(PromotionTypes ePromotion, int iLeaderUnitId) const
{
	if (iLeaderUnitId >= 0)
	{
		if (iLeaderUnitId == getID())
		{
			return false;
		}

		// The command is always possible if it's coming from a Warlord unit that gives just experience points
		CvUnit* pWarlord = GET_PLAYER(getOwnerINLINE()).getUnit(iLeaderUnitId);
		if (pWarlord &&
			NO_UNIT != pWarlord->getUnitType() &&
			pWarlord->getUnitInfo().getLeaderExperience() > 0 &&
			NO_PROMOTION == pWarlord->getUnitInfo().getLeaderPromotion() &&
			canAcquirePromotionAny())
		{
			return true;
		}
	}

	if (ePromotion == NO_PROMOTION)
	{
		return false;
	}

	// MNAI - moved from canAcquirePromotion()
	if (GC.getPromotionInfo(ePromotion).getMinLevel() == -1)
	{
	    return false;
	}
	// MNAI End

	if (!canAcquirePromotion(ePromotion))
	{
		return false;
	}

	if (GC.getPromotionInfo(ePromotion).isLeader())
	{
		if (iLeaderUnitId >= 0)
		{
			CvUnit* pWarlord = GET_PLAYER(getOwnerINLINE()).getUnit(iLeaderUnitId);
			if (pWarlord && NO_UNIT != pWarlord->getUnitType())
			{
				return (pWarlord->getUnitInfo().getLeaderPromotion() == ePromotion);
			}
		}
		return false;
	}
	else
	{
		if (!isPromotionReady())
		{
			return false;
		}
	}

	return true;
}

void CvUnit::promote(PromotionTypes ePromotion, int iLeaderUnitId)
{
	if (!canPromote(ePromotion, iLeaderUnitId))
	{
		return;
	}

	if (iLeaderUnitId >= 0)
	{
		CvUnit* pWarlord = GET_PLAYER(getOwnerINLINE()).getUnit(iLeaderUnitId);
		if (pWarlord)
		{
			pWarlord->giveExperience();
			if (!pWarlord->getNameNoDesc().empty())
			{
				setName(pWarlord->getNameKey());
			}

			//update graphics models
			// Set civ-specific art here
			m_eLeaderUnitType = pWarlord->getUnitType();
			reloadEntity();
		}
	}

//FfH Units: Modified by Kael 08/04/2007
//	if (!GC.getPromotionInfo(ePromotion).isLeader())
	if ((!GC.getPromotionInfo(ePromotion).isLeader()) && !(getFreePromotionPick() > 0))
//FfH: End Modify

	{
		changeLevel(1);
		changeDamage(-(getDamage() / 2));
	}

//FfH: Added by Kael 01/09/2008
    if (getFreePromotionPick() > 0)
    {
        changeFreePromotionPick(-1);
    }
//FfH: End Add

	setHasPromotion(ePromotion, true);

	testPromotionReady();

	if (IsSelected())
	{
		gDLL->getInterfaceIFace()->playGeneralSound(GC.getPromotionInfo(ePromotion).getSound());

		gDLL->getInterfaceIFace()->setDirty(UnitInfo_DIRTY_BIT, true);

// BUG - Update Plot List - start
		gDLL->getInterfaceIFace()->setDirty(PlotListButtons_DIRTY_BIT, true);
// BUG - Update Plot List - end
	}
	else
	{
		setInfoBarDirty(true);
	}

	CvEventReporter::getInstance().unitPromoted(this, ePromotion);
}

bool CvUnit::lead(int iUnitId)
{
	if (!canLead(plot(), iUnitId))
	{
		return false;
	}

	PromotionTypes eLeaderPromotion = (PromotionTypes)m_pUnitInfo->getLeaderPromotion();

	if (-1 == iUnitId)
	{
		CvPopupInfo* pInfo = new CvPopupInfo(BUTTONPOPUP_LEADUNIT, eLeaderPromotion, getID());
		if (pInfo)
		{
			gDLL->getInterfaceIFace()->addPopup(pInfo, getOwnerINLINE(), true);
		}
		return false;
	}
	else
	{
		CvUnit* pUnit = GET_PLAYER(getOwnerINLINE()).getUnit(iUnitId);
		if (!pUnit || !pUnit->canPromote(eLeaderPromotion, getID()))	
		{
			return false;
		}

		pUnit->joinGroup(NULL, true, true);

		pUnit->promote(eLeaderPromotion, getID());

		if (plot()->isActiveVisible(false))
		{
			NotifyEntity(MISSION_LEAD);
		}
		
		logBBAI("    Killing %S (delayed) -- starting to lead (Unit %d - plot: %d, %d)",
				getName().GetCString(), getID(), getX(), getY());
		kill(true);

		return true;
	}
}


int CvUnit::canLead(const CvPlot* pPlot, int iUnitId) const
{
	PROFILE_FUNC();

	if (isHasPromotion((PromotionTypes) GC.getInfoTypeForString("PROMOTION_ILLUSION")))
	{
		return false;
	}

	if (isDelayedDeath())
	{
		return 0;
	}

	if (NO_UNIT == getUnitType())
	{
		return 0;
	}

	// Advanced Tactics - Great Generals
	if (isHasCasted())
	{
		return 0;
	}
	// End Advanced Tactics

	int iNumUnits = 0;
	CvUnitInfo& kUnitInfo = getUnitInfo();

	if (-1 == iUnitId)
	{
		CLLNode<IDInfo>* pUnitNode = pPlot->headUnitNode();
		while(pUnitNode != NULL)
		{
			CvUnit* pUnit = ::getUnit(pUnitNode->m_data);
			pUnitNode = pPlot->nextUnitNode(pUnitNode);

			if (pUnit && pUnit != this && pUnit->getOwnerINLINE() == getOwnerINLINE() && pUnit->canPromote((PromotionTypes)kUnitInfo.getLeaderPromotion(), getID()))
			{
				++iNumUnits;
			}
		}
	}
	else
	{
		CvUnit* pUnit = GET_PLAYER(getOwnerINLINE()).getUnit(iUnitId);
		if (pUnit && pUnit != this && pUnit->canPromote((PromotionTypes)kUnitInfo.getLeaderPromotion(), getID()))
		{
			iNumUnits = 1;
		}
	}
	return iNumUnits;
}


int CvUnit::canGiveExperience(const CvPlot* pPlot) const
{
	int iNumUnits = 0;

	if (NO_UNIT != getUnitType() && m_pUnitInfo->getLeaderExperience() > 0)
	{
		CLLNode<IDInfo>* pUnitNode = pPlot->headUnitNode();
		while(pUnitNode != NULL)
		{
			CvUnit* pUnit = ::getUnit(pUnitNode->m_data);
			pUnitNode = pPlot->nextUnitNode(pUnitNode);

			if (pUnit && pUnit != this && pUnit->getOwnerINLINE() == getOwnerINLINE() && pUnit->canAcquirePromotionAny())
			{
				++iNumUnits;
			}
		}
	}

	return iNumUnits;
}

bool CvUnit::giveExperience()
{
	CvPlot* pPlot = plot();

	if (pPlot)
	{
		int iNumUnits = canGiveExperience(pPlot);
		if (iNumUnits > 0)
		{
			int iTotalExperience = getStackExperienceToGive(iNumUnits);

			int iMinExperiencePerUnit = iTotalExperience / iNumUnits;
			int iRemainder = iTotalExperience % iNumUnits;

			CLLNode<IDInfo>* pUnitNode = pPlot->headUnitNode();
			int i = 0;
			while(pUnitNode != NULL)
			{
				CvUnit* pUnit = ::getUnit(pUnitNode->m_data);
				pUnitNode = pPlot->nextUnitNode(pUnitNode);

				if (pUnit && pUnit != this && pUnit->getOwnerINLINE() == getOwnerINLINE() && pUnit->canAcquirePromotionAny())
				{
					pUnit->changeExperience(i < iRemainder ? iMinExperiencePerUnit+1 : iMinExperiencePerUnit);
					pUnit->testPromotionReady();
				}

				i++;
			}

			return true;
		}
	}

	return false;
}

int CvUnit::getStackExperienceToGive(int iNumUnits) const
{
	return (m_pUnitInfo->getLeaderExperience() * (100 + std::min(50, (iNumUnits - 1) * GC.defines.iWARLORD_EXTRA_EXPERIENCE_PER_UNIT_PERCENT))) / 100;
}

int CvUnit::upgradePrice(UnitTypes eUnit) const
{
	int iPrice;

/*************************************************************************************************/
/**	SPEEDTWEAK (Block Python) Sephi                                               	            **/
/**																								**/
/**						                                            							**/
/*************************************************************************************************/
    if(GC.defines.iUSE_UPGRADEPRICEOVERRIDE_CALLBACK==1)
    {
        CyArgsList argsList;
        argsList.add(getOwnerINLINE());
        argsList.add(getID());
        argsList.add((int) eUnit);
        long lResult=0;
        gDLL->getPythonIFace()->callFunction(PYGameModule, "getUpgradePriceOverride", argsList.makeFunctionArgs(), &lResult);
        if (lResult >= 0)
        {
            return lResult;
        }
    }
/*************************************************************************************************/
/**	END	                                        												**/
/*************************************************************************************************/

	if (isBarbarian())
	{
		return 0;
	}

	iPrice = GC.defines.iBASE_UNIT_UPGRADE_COST;

	iPrice += (std::max(0, (GET_PLAYER(getOwnerINLINE()).getProductionNeeded(eUnit) - GET_PLAYER(getOwnerINLINE()).getProductionNeeded(getUnitType()))) * GC.defines.iUNIT_UPGRADE_COST_PER_PRODUCTION);

	if (!isHuman() && !isBarbarian())
	{
		iPrice *= GC.getHandicapInfo(GC.getGameINLINE().getHandicapType()).getAIUnitUpgradePercent();
		iPrice /= 100;

		iPrice *= std::max(0, ((GC.getHandicapInfo(GC.getGameINLINE().getHandicapType()).getAIPerEraModifier() * GC.getGameINLINE().getCurrentEra()) + 100));
		iPrice /= 100;
	}

	iPrice -= (iPrice * getUpgradeDiscount()) / 100;

//FfH Traits: Added by Kael 08/02/2007
    iPrice += (iPrice * GET_PLAYER(getOwnerINLINE()).getUpgradeCostModifier()) / 100;
//FfH: End Add

	return std::max( 0, iPrice ); // lfgr fix 06/2020: No gold earned from upgrades
}


// LFGR_TODO: Cache this? Could be slow for deep upgrade trees.
bool CvUnit::upgradeAvailable(UnitTypes eFromUnit, UnitClassTypes eToUnitClass, int iCount) const
{
	PROFILE_FUNC()
	
	return getInfoCache().upgradeAvailable( getCivilizationType(), eFromUnit, eToUnitClass );
}


bool CvUnit::canUpgrade(UnitTypes eUnit, bool bTestVisible) const
{
	if (eUnit == NO_UNIT)
	{
		return false;
	}

	if (isUpgradeBlocked())
	{
		return false;
	}

	if(!isReadyForUpgrade())
	{
		return false;
	}

	if (!bTestVisible)
	{
		if (GET_PLAYER(getOwnerINLINE()).getGold() < upgradePrice(eUnit))
		{
			return false;
		}
	}

	CvUnitInfo& kUnitInfo = GC.getUnitInfo(eUnit);

	// no cross-religion upgrades for religious units
	if (getReligion() != NO_RELIGION)
	{
		if (kUnitInfo.getReligionType() != NO_RELIGION)
		{
			if (getReligion() != kUnitInfo.getReligionType())
			{
				return false;
			}
		}
	}

	// check to see if this is a religion or alignment -specific upgrade
	// if so, we can skip the racial check - these special upgrades trump the laws of nature
	bool bSpecialUpgrade = false;
	if (kUnitInfo.getPrereqReligion() != NO_RELIGION)
	{
		bSpecialUpgrade = true;
	}

	if (kUnitInfo.getPrereqAlignment() != NO_ALIGNMENT)
	{
		bSpecialUpgrade = true;
	}

	if (!bSpecialUpgrade)
	{
		// make sure we dont cross racial boundaries during upgrades
		for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
		{
			if (kUnitInfo.getFreePromotions(iI))
			{
				if (GC.getPromotionInfo((PromotionTypes)iI).isRace())
				{
					if (!GC.getPromotionInfo((PromotionTypes)iI).isNotAlive()) // exception for upgrades to not-alive races
					{
						if (getRace() == NO_PROMOTION)
						{
							return false;
						}
						else
						{
							if (getRace() != iI)
							{
								return false;
							}
						}
					}
				}
			}
		}
	}

//FfH Units: Added by Kael 05/24/2008
    if (getLevel() < kUnitInfo.getMinLevel())
	{
        if (isHuman() || !GC.getGameINLINE().isOption(GAMEOPTION_AI_NO_MINIMUM_LEVEL))
        {
            return false;
        }
	}
    if (kUnitInfo.isDisableUpgradeTo())
    {
        return false;
    }
	if (GET_PLAYER(getOwnerINLINE()).isUnitClassMaxedOut((UnitClassTypes)kUnitInfo.getUnitClassType()))
	{
		return false;
	}
	if (!isHuman()) //added so the AI wont spam UNTIAI_MISSIONARY priests by upgrading disciples
	{
        if (AI_getUnitAIType() == UNITAI_MISSIONARY && getLevel() < 3)
        {
            return false;
        }
	}
//FfH: End Add

	if (hasUpgrade(eUnit))
	{
		return true;
	}

	return false;
}

bool CvUnit::isReadyForUpgrade() const
{
	if (!canMove())
	{
		return false;
	}

	if (plot()->getTeam() != getTeam() && !isUpgradeOutsideBorders())
	{
		return false;
	}

	return true;
}

// has upgrade is used to determine if an upgrade is possible,
// it specifically does not check whether the unit can move, whether the current plot is owned, enough gold
// those are checked in canUpgrade()
// does not search all cities, only checks the closest one
bool CvUnit::hasUpgrade(bool bSearch) const
{
	return (getUpgradeCity(bSearch) != NULL);
}

// has upgrade is used to determine if an upgrade is possible,
// it specifically does not check whether the unit can move, whether the current plot is owned, enough gold
// those are checked in canUpgrade()
// does not search all cities, only checks the closest one
bool CvUnit::hasUpgrade(UnitTypes eUnit, bool bSearch) const
{
	return (getUpgradeCity(eUnit, bSearch) != NULL);
}

// finds the 'best' city which has a valid upgrade for the unit,
// it specifically does not check whether the unit can move, or if the player has enough gold to upgrade
// those are checked in canUpgrade()
// if bSearch is true, it will check every city, if not, it will only check the closest valid city
// NULL result means the upgrade is not possible
CvCity* CvUnit::getUpgradeCity(bool bSearch) const
{
	CvPlayerAI& kPlayer = GET_PLAYER(getOwnerINLINE());
	UnitAITypes eUnitAI = AI_getUnitAIType();
	CvArea* pArea = area();

	int iCurrentValue = kPlayer.AI_unitValue(getUnitType(), eUnitAI, pArea, true);

	int iBestSearchValue = MAX_INT;
	CvCity* pBestUpgradeCity = NULL;

	for (int iI = 0; iI < GC.getNumUnitInfos(); iI++)
	{
		int iNewValue = kPlayer.AI_unitValue(((UnitTypes)iI), eUnitAI, pArea, true);
		if (iNewValue > iCurrentValue)
		{
			int iSearchValue;
			CvCity* pUpgradeCity = getUpgradeCity((UnitTypes)iI, bSearch, &iSearchValue);
			if (pUpgradeCity != NULL)
			{
				// if not searching or close enough, then this match will do
				if (!bSearch || iSearchValue < 16)
				{
					return pUpgradeCity;
				}

				if (iSearchValue < iBestSearchValue)
				{
					iBestSearchValue = iSearchValue;
					pBestUpgradeCity = pUpgradeCity;
				}
			}
		}
	}

	return pBestUpgradeCity;
}

// finds the 'best' city which has a valid upgrade for the unit, to eUnit type
// it specifically does not check whether the unit can move, or if the player has enough gold to upgrade
// those are checked in canUpgrade()
// if bSearch is true, it will check every city, if not, it will only check the closest valid city
// if iSearchValue non NULL, then on return it will be the city's proximity value, lower is better
// NULL result means the upgrade is not possible
CvCity* CvUnit::getUpgradeCity(UnitTypes eUnit, bool bSearch, int* iSearchValue) const
{
	if (eUnit == NO_UNIT)
	{
		return false;
	}

	CvPlayerAI& kPlayer = GET_PLAYER(getOwnerINLINE());
	CvUnitInfo& kUnitInfo = GC.getUnitInfo(eUnit);

//FfH: Modified by Kael 05/09/2008
//	if (GC.getCivilizationInfo(kPlayer.getCivilizationType()).getCivilizationUnits(kUnitInfo.getUnitClassType()) != eUnit)
//	{
//		return false;
//	}
    if (m_pUnitInfo->getUpgradeCiv() == NO_CIVILIZATION)
    {
        if (!kPlayer.isAssimilation())
		{
            if (GC.getCivilizationInfo(kPlayer.getCivilizationType()).getCivilizationUnits(kUnitInfo.getUnitClassType()) != eUnit)
			{
                return false;
			}
		}
    }
    else
    {
        if (GC.getCivilizationInfo((CivilizationTypes)m_pUnitInfo->getUpgradeCiv()).getCivilizationUnits(kUnitInfo.getUnitClassType()) != eUnit)
        {
            return false;
        }
    }
//FfH: End Modify

	if (!upgradeAvailable(getUnitType(), ((UnitClassTypes)(kUnitInfo.getUnitClassType()))))
	{
		return false;
	}

	if (kUnitInfo.getCargoSpace() < getCargo())
	{
		return false;
	}

	CLLNode<IDInfo>* pUnitNode = plot()->headUnitNode();
	while (pUnitNode != NULL)
	{
		CvUnit* pLoopUnit = ::getUnit(pUnitNode->m_data);
		pUnitNode = plot()->nextUnitNode(pUnitNode);

		if (pLoopUnit->getTransportUnit() == this)
		{
			if (kUnitInfo.getSpecialCargo() != NO_SPECIALUNIT)
			{
				if (kUnitInfo.getSpecialCargo() != pLoopUnit->getSpecialUnitType())
				{
					return false;
				}
			}

			if (kUnitInfo.getDomainCargo() != NO_DOMAIN)
			{
				if (kUnitInfo.getDomainCargo() != pLoopUnit->getDomainType())
				{
					return false;
				}
			}
		}
	}

	// sea units must be built on the coast
	bool bCoastalOnly = (getDomainType() == DOMAIN_SEA);

	// results
	int iBestValue = MAX_INT;
	CvCity* pBestCity = NULL;

	// if search is true, check every city for our team
	if (bSearch || isUpgradeOutsideBorders())
	{
		// air units can travel any distance
		bool bIgnoreDistance = ((getDomainType() == DOMAIN_AIR) || isUpgradeOutsideBorders());

		TeamTypes eTeam = getTeam();
		int iArea = getArea();
		int iX = getX_INLINE(), iY = getY_INLINE();

		// check every player on our team's cities
		for (int iI = 0; iI < MAX_PLAYERS; iI++)
		{
			// is this player on our team?
			CvPlayerAI& kLoopPlayer = GET_PLAYER((PlayerTypes)iI);
			if (kLoopPlayer.isAlive() && kLoopPlayer.getTeam() == eTeam)
			{
				int iLoop;
				for (CvCity* pLoopCity = kLoopPlayer.firstCity(&iLoop); pLoopCity != NULL; pLoopCity = kLoopPlayer.nextCity(&iLoop))
				{
					// if coastal only, then make sure we are coast
					CvArea* pWaterArea = NULL;
					if (!bCoastalOnly || ((pWaterArea = pLoopCity->waterArea()) != NULL && !pWaterArea->isLake()))
					{
						// can this city tran this unit?

//FfH Units: Modified by Kael 05/24/2008
//						if (pLoopCity->canTrain(eUnit, false, false, true))
						if (pLoopCity->canUpgrade(eUnit, false, false, true))
//FfH: End Modify

						{
							// if we do not care about distance, then the first match will do
							if (bIgnoreDistance)
							{
								// if we do not care about distance, then return 1 for value
								if (iSearchValue != NULL)
								{
									*iSearchValue = 1;
								}

								return pLoopCity;
							}

							int iValue = plotDistance(iX, iY, pLoopCity->getX_INLINE(), pLoopCity->getY_INLINE());

							// if not same area, not as good (lower numbers are better)
							if (iArea != pLoopCity->getArea() && (!bCoastalOnly || iArea != pWaterArea->getID()))
							{
								iValue *= 16;
							}

							// if we cannot path there, not as good (lower numbers are better)
/*************************************************************************************************/
/**	SPEED TWEAK  Sephi                                                             				**/
/**	We only check for cities not that far away										            **/
/**	                                                                 							**/
/*************************************************************************************************/

/** Start Orig Code
							if (!generatePath(pLoopCity->plot(), 0, true))
							{
								iValue *= 16;
							}
/** End Orig Code **/
                            int XDist=pLoopCity->plot()->getX_INLINE() - plot()->getX_INLINE();
                            int YDist=pLoopCity->plot()->getY_INLINE() - plot()->getY_INLINE();
                            if (((XDist*XDist)+(YDist*YDist))<10)
                            {
                                if (!generatePath(pLoopCity->plot(), 0, true))
                                {
                                    iValue *= 16;
                                }
                            }
                            else
                            {
                                    iValue *= 16;
                            }
/*************************************************************************************************/
/**	END                                                                  						**/
/*************************************************************************************************/

							if (iValue < iBestValue)
							{
								iBestValue = iValue;
								pBestCity = pLoopCity;
							}
						}
					}
				}
			}
		}
	}
	else
	{
		// find the closest city
		CvCity* pClosestCity = GC.getMapINLINE().findCity(getX_INLINE(), getY_INLINE(), NO_PLAYER, getTeam(), true, bCoastalOnly);
		if (pClosestCity != NULL)
		{
			// if we can train, then return this city (otherwise it will return NULL)

//FfH Units: Modified by Kael 08/07/2007
//			if (pClosestCity->canTrain(eUnit, false, false, true))
			if (kPlayer.isAssimilation() && (m_pUnitInfo->getUpgradeCiv() == NO_CIVILIZATION))
			{
				if (GC.getCivilizationInfo(pClosestCity->getCivilizationType()).getCivilizationUnits(kUnitInfo.getUnitClassType()) != eUnit && GC.getCivilizationInfo(kPlayer.getCivilizationType()).getCivilizationUnits(kUnitInfo.getUnitClassType()) != eUnit)
				{
					return false;
				}
			}
			if (pClosestCity->canUpgrade(eUnit, false, false, true))
//FfH: End Add

			{
				// did not search, always return 1 for search value
				iBestValue = 1;

				pBestCity = pClosestCity;
			}
		}
	}

	// return the best value, if non-NULL
	if (iSearchValue != NULL)
	{
		*iSearchValue = iBestValue;
	}

	return pBestCity;
}

CvUnit* CvUnit::upgrade(UnitTypes eUnit) // K-Mod: this now returns the new unit.
{
	CvUnit* pUpgradeUnit;

	if (!canUpgrade(eUnit))
	{
		return this;
	}

// BUG - Upgrade Unit Event - start
	int iPrice = upgradePrice(eUnit);
	GET_PLAYER(getOwnerINLINE()).changeGold(-iPrice);
// BUG - Upgrade Unit Event - end

//FfH: Modified by Kael 04/18/2009
//	pUpgradeUnit = GET_PLAYER(getOwnerINLINE()).initUnit(eUnit, getX_INLINE(), getY_INLINE(), AI_getUnitAIType());
	UnitAITypes eUnitAI = AI_getUnitAIType();
//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/23
/*
	if (eUnitAI == UNITAI_MISSIONARY)
	{
		ReligionTypes eReligion = GET_PLAYER(getOwnerINLINE()).getStateReligion();
		if (eReligion == NO_RELIGION || GC.getUnitInfo(eUnit).getReligionSpreads(eReligion) == 0)
		{
			eUnitAI = UNITAI_RESERVE;
		}
	}
*/
	if (!GC.getUnitInfo(eUnit).getUnitAIType(eUnitAI))
	{
		eUnitAI = (UnitAITypes)GC.getUnitInfo(eUnit).getDefaultUnitAIType();
	}
//<<<<Unofficial Bug Fix: End Modify
	pUpgradeUnit = GET_PLAYER(getOwnerINLINE()).initUnit(eUnit, getX_INLINE(), getY_INLINE(), eUnitAI);
//FfH: End Modify

	FAssertMsg(pUpgradeUnit != NULL, "UpgradeUnit is not assigned a valid value");

	pUpgradeUnit->convert(this);
	pUpgradeUnit->joinGroup(getGroup()); // K-Mod, swapped order with convert. (otherwise units on boats would be ungrouped.)

	pUpgradeUnit->finishMoves();

	if (pUpgradeUnit->getLeaderUnitType() == NO_UNIT)
	{
		if (pUpgradeUnit->getExperience() > GC.defines.iMAX_EXPERIENCE_AFTER_UPGRADE)
		{
			pUpgradeUnit->setExperience(GC.defines.iMAX_EXPERIENCE_AFTER_UPGRADE);
		}
	}

// BUG - Upgrade Unit Event - start
	CvEventReporter::getInstance().unitUpgraded(this, pUpgradeUnit, iPrice);
// BUG - Upgrade Unit Event - end

/************************************************************************************************/
/* BETTER_BTS_AI_MOD                      02/24/10                                jdog5000      */
/*                                                                                              */
/* AI Logging                                                                                   */
/************************************************************************************************/
	if( gUnitLogLevel > 2 )
	{
		CvWString szString;
		getUnitAIString(szString, AI_getUnitAIType());
		logBBAI("      ...spending %d to upgrade %S to %S, unit AI %S", upgradePrice(eUnit), getName(0).GetCString(), pUpgradeUnit->getName(0).GetCString(), szString.GetCString());
	}
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                       END                                                  */
/************************************************************************************************/
	return pUpgradeUnit; // K-Mod
}


HandicapTypes CvUnit::getHandicapType() const
{
	return GET_PLAYER(getOwnerINLINE()).getHandicapType();
}


CivilizationTypes CvUnit::getCivilizationType() const
{
	return GET_PLAYER(getOwnerINLINE()).getCivilizationType();
}

const wchar* CvUnit::getVisualCivAdjective(TeamTypes eForTeam) const
{
	if (getVisualOwner(eForTeam) == getOwnerINLINE())
	{
		return GC.getCivilizationInfo(getCivilizationType()).getAdjectiveKey();
	}

	return L"";
}

SpecialUnitTypes CvUnit::getSpecialUnitType() const
{
	return ((SpecialUnitTypes)(m_pUnitInfo->getSpecialUnitType()));
}


UnitTypes CvUnit::getCaptureUnitType(CivilizationTypes eCivilization) const
{
	FAssert(eCivilization != NO_CIVILIZATION);
	return ((m_pUnitInfo->getUnitCaptureClassType() == NO_UNITCLASS) ? NO_UNIT : (UnitTypes)GC.getCivilizationInfo(eCivilization).getCivilizationUnits(m_pUnitInfo->getUnitCaptureClassType()));
}


UnitCombatTypes CvUnit::getUnitCombatType() const
{
	return ((UnitCombatTypes)(m_pUnitInfo->getUnitCombatType()));
}


DomainTypes CvUnit::getDomainType() const
{
	return ((DomainTypes)(m_pUnitInfo->getDomainType()));
}


InvisibleTypes CvUnit::getInvisibleType() const
{

//FfH: Modified by Kael 11/11/2008
//	return ((InvisibleTypes)(m_pUnitInfo->getInvisibleType()));
	if (m_iInvisibleType == NO_INVISIBLE)
	{
//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/22
//*** CtD caused by Hidden Nationality unit (or co-existing with enemy unit with the same tile) is fixed completely.
//		if (plot()->isOwned())
		if (plot() != NULL && plot()->isOwned())
//<<<<Unofficial Bug Fix: End Modify
		{
			if (GET_PLAYER(plot()->getOwnerINLINE()).isHideUnits() && !isIgnoreHide())
			{
				if (plot()->getTeam() == getTeam())
				{
					if (!plot()->isCity(GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS))) // Super Forts *custom*
					{
						return ((InvisibleTypes)GC.defines.iINVISIBLE_TYPE);
					}
				}
			}
		}
	}
	if (isInvisibleFromPromotion())
	{
		if (m_pUnitInfo->getEquipmentPromotion() != NO_PROMOTION)
		{
			return ((InvisibleTypes)2); // HARD CODE !!!
		}
		else
		{
			return ((InvisibleTypes)GC.defines.iINVISIBLE_TYPE);
		}
	}
	return ((InvisibleTypes)m_iInvisibleType);
//FfH: End Modify

}

int CvUnit::getNumSeeInvisibleTypes() const
{

//FfH: Added by Kael 12/07/2008 (Modified by Red Key 2012)
    if (isSeeInvisible())
    {
		return GC.getNumInvisibleInfos();
		//return 1;
    }
//FfH: End Add

	return m_pUnitInfo->getNumSeeInvisibleTypes();
}

InvisibleTypes CvUnit::getSeeInvisibleType(int i) const
{

//FfH: Added by Kael 12/07/2008 (Modified by Red Key 2012)
    if (isSeeInvisible())
    {
		FAssertMsg(i >= 0, "i is expected to be non-negative (invalid Index)");
		FAssertMsg(i < GC.getNumInvisibleInfos(), "i is expected to be within maximum bounds (invalid Index)");
        return (InvisibleTypes)i;
		//return ((InvisibleTypes)GC.defines.iINVISIBLE_TYPE);
    }
//FfH: End Add

	return (InvisibleTypes)(m_pUnitInfo->getSeeInvisibleType(i));
}


int CvUnit::flavorValue(FlavorTypes eFlavor) const
{
	return m_pUnitInfo->getFlavorValue(eFlavor);
}


bool CvUnit::isBarbarian() const
{
	return GET_PLAYER(getOwnerINLINE()).isBarbarian();
}


bool CvUnit::isHuman() const
{
	return GET_PLAYER(getOwnerINLINE()).isHuman();
}

int CvUnit::visibilityRange() const
{
	if (getUnitInfo().isObject())
	{
		return 0;
	}

//FfH: Modified by Kael 08/10/2007
//	return (GC.defines.iUNIT_VISIBILITY_RANGE + getExtraVisibilityRange());
    int iRange = GC.defines.iUNIT_VISIBILITY_RANGE;
    iRange += getExtraVisibilityRange();
    if (plot()->getImprovementType() != NO_IMPROVEMENT)
    {
        iRange += GC.getImprovementInfo((ImprovementTypes)plot()->getImprovementType()).getVisibilityChange();
    }
	return iRange;
//FfH: End Modify

}


int CvUnit::baseMoves() const
{
	return (m_pUnitInfo->getMoves() + getExtraMoves() + GET_TEAM(getTeam()).getExtraMoves(getDomainType()));
}


int CvUnit::maxMoves() const
{
	return (baseMoves() * GC.getMOVE_DENOMINATOR());
}


int CvUnit::movesLeft() const
{
	return std::max(0, (maxMoves() - getMoves()));
}


bool CvUnit::canMove() const
{
	if (isDead())
	{
		return false;
	}

	if (getMoves() >= maxMoves())
	{
		return false;
	}

	if (getImmobileTimer() > 0)
	{
		return false;
	}

	return true;
}


bool CvUnit::hasMoved()	const
{
	return (getMoves() > 0);
}


int CvUnit::airRange() const
{
	return (m_pUnitInfo->getAirRange() + getExtraAirRange());
}


int CvUnit::nukeRange() const
{
	return m_pUnitInfo->getNukeRange();
}


// XXX should this test for coal?
bool CvUnit::canBuildRoute() const
{
	int iI;

	for (iI = 0; iI < GC.getNumBuildInfos(); iI++)
	{
		if (GC.getBuildInfo((BuildTypes)iI).getRoute() != NO_ROUTE)
		{
			if (m_pUnitInfo->getBuilds(iI))
			{
				if (GET_TEAM(getTeam()).isHasTech((TechTypes)(GC.getBuildInfo((BuildTypes)iI).getTechPrereq())))
				{
					return true;
				}
			}
		}
	}

	return false;
}

BuildTypes CvUnit::getBuildType() const
{
	BuildTypes eBuild;

	if (getGroup()->headMissionQueueNode() != NULL)
	{
		switch (getGroup()->headMissionQueueNode()->m_data.eMissionType)
		{
		case MISSION_MOVE_TO:
			break;

		case MISSION_ROUTE_TO:
			if (getGroup()->getBestBuildRoute(plot(), &eBuild) != NO_ROUTE)
			{
				return eBuild;
			}
			break;

		case MISSION_MOVE_TO_UNIT:
		case MISSION_SKIP:
		case MISSION_SLEEP:
		case MISSION_FORTIFY:
		case MISSION_PLUNDER:
		case MISSION_AIRPATROL:
		case MISSION_SEAPATROL:
		case MISSION_HEAL:
		case MISSION_SENTRY:
		case MISSION_AIRLIFT:
		case MISSION_NUKE:
		case MISSION_RECON:
		case MISSION_PARADROP:
		case MISSION_AIRBOMB:
		case MISSION_BOMBARD:
		case MISSION_RANGE_ATTACK:
		case MISSION_PILLAGE:
		case MISSION_SABOTAGE:
		case MISSION_DESTROY:
		case MISSION_STEAL_PLANS:
		case MISSION_FOUND:
		case MISSION_SPREAD:
		case MISSION_SPREAD_CORPORATION:
		case MISSION_JOIN:
		case MISSION_CONSTRUCT:
		case MISSION_DISCOVER:
		case MISSION_HURRY:
		case MISSION_TRADE:
		case MISSION_GREAT_WORK:
		case MISSION_INFILTRATE:
		case MISSION_GOLDEN_AGE:
		case MISSION_LEAD:
		case MISSION_ESPIONAGE:
		case MISSION_DIE_ANIMATION:
			break;

		case MISSION_BUILD:
			return (BuildTypes)getGroup()->headMissionQueueNode()->m_data.iData1;
			break;

		default:
			FAssert(false);
			break;
		}
	}

	return NO_BUILD;
}


int CvUnit::workRate(bool bMax) const
{
	int iRate;

	if (!bMax)
	{
		if (!canMove())
		{
			return 0;
		}
	}

	iRate = m_pUnitInfo->getWorkRate();

//FfH: Added by Kael 08/13/2008
    iRate += getWorkRateModify();
//FfH: End Add

	iRate *= std::max(0, (GET_PLAYER(getOwnerINLINE()).getWorkerSpeedModifier() + 100));
	iRate /= 100;

	if (!isHuman() && !isBarbarian())
	{
		iRate *= std::max(0, (GC.getHandicapInfo(GC.getGameINLINE().getHandicapType()).getAIWorkRateModifier() + 100));
		iRate /= 100;
	}

	return iRate;
}


bool CvUnit::isAnimal() const
{
	return m_pUnitInfo->isAnimal();
}


bool CvUnit::isNoBadGoodies() const
{
	return m_pUnitInfo->isNoBadGoodies();
}


bool CvUnit::isOnlyDefensive() const
{

//FfH Promotions: Added by Kael 08/14/2007
    if (m_iOnlyDefensive > 0)
    {
        return true;
    }
//FfH: End Add

	return m_pUnitInfo->isOnlyDefensive();
}


bool CvUnit::isNoCapture() const
{

//FfH: Added by Kael 10/25/2007
    if (isHiddenNationality())
    {
        return true;
    }
//FfH: End Add

	return m_pUnitInfo->isNoCapture();
}


bool CvUnit::isRivalTerritory() const
{
	return m_pUnitInfo->isRivalTerritory();
}


bool CvUnit::isMilitaryHappiness() const
{
	return m_pUnitInfo->isMilitaryHappiness();
}


bool CvUnit::isInvestigate() const
{
	return m_pUnitInfo->isInvestigate();
}


bool CvUnit::isCounterSpy() const
{
	return m_pUnitInfo->isCounterSpy();
}


bool CvUnit::isSpy() const
{
	return m_pUnitInfo->isSpy();
}


bool CvUnit::isFound() const
{
	return m_pUnitInfo->isFound();
}


bool CvUnit::isGoldenAge() const
{
	if (isDelayedDeath())
	{
		return false;
	}

	return m_pUnitInfo->isGoldenAge();
}

bool CvUnit::canCoexistWithEnemyUnit(TeamTypes eTeam) const
{
	if (NO_TEAM == eTeam)
	{
		if(alwaysInvisible())
		{
			return true;
		}

		return false;
	}

	if(isInvisible(eTeam, false))
	{
		return true;
	}

	return false;
}

bool CvUnit::isFighting() const
{
	return (getCombatUnit() != NULL);
}


bool CvUnit::isAttacking() const
{
	return (getAttackPlot() != NULL && !isDelayedDeath());
}


bool CvUnit::isDefending() const
{
	return (isFighting() && !isAttacking());
}


bool CvUnit::isCombat() const
{
	return (isFighting() || isAttacking());
}


int CvUnit::maxHitPoints() const
{
	return GC.getMAX_HIT_POINTS();
}


int CvUnit::currHitPoints()	const
{
	return (maxHitPoints() - getDamage());
}


bool CvUnit::isHurt() const
{
	return (getDamage() > 0);
}


bool CvUnit::isDead() const
{
	return (getDamage() >= maxHitPoints());
}


void CvUnit::setBaseCombatStr(int iCombat)
{
	m_iBaseCombat = iCombat;
}

int CvUnit::baseCombatStr() const
{

//FfH Damage Types: Modified by Kael 10/26/2007
//    return m_iBaseCombat;
    int iStr = m_iBaseCombat + m_iTotalDamageTypeCombat;
    if (iStr < 0)
    {
        iStr = 0;
    }
    return iStr;
//FfH: End Add

}

//FfH Defense Str: Added by Kael 10/26/2007
void CvUnit::setBaseCombatStrDefense(int iCombat)
{
	m_iBaseCombatDefense = iCombat;
}

int CvUnit::baseCombatStrDefense() const
{
    int iStr = m_iBaseCombatDefense + m_iTotalDamageTypeCombat;
    if (iStr < 0)
    {
        iStr = 0;
    }
    return iStr;
}
//FfH: End Add

// maxCombatStr can be called in four different configurations
//		pPlot == NULL, pAttacker == NULL for combat when this is the attacker
//		pPlot valid, pAttacker valid for combat when this is the defender
//		pPlot valid, pAttacker == NULL (new case), when this is the defender, attacker unknown
//		pPlot valid, pAttacker == this (new case), when the defender is unknown, but we want to calc approx str
//			note, in this last case, it is expected pCombatDetails == NULL, it does not have to be, but some
//			values may be unexpectedly reversed in this case (iModifierTotal will be the negative sum)
// lfgr note 05/2020: In FfH, we have this:
//		pPlot == NULL, pAttacher != NULL - This is the attacker, pAttacker is the defender.
//		pPlot == NULL, pAttacker == NULL should probably not be used anymore, as the defender can influence strength via damage resistance/immunity
int CvUnit::maxCombatStr(const CvPlot* pPlot, const CvUnit* pAttacker, CombatDetails* pCombatDetails) const
{
	int iCombat;

//FfH Damage Types: Added by Kael 09/02/2007
    const CvUnit* pDefender = NULL;
    if (pPlot == NULL)
    {
        if (pAttacker != NULL)
        {
            pDefender = pAttacker;
            pAttacker = NULL;
        }
    }
//FfH: End Add

	FAssertMsg((pPlot == NULL) || (pPlot->getTerrainType() != NO_TERRAIN), "(pPlot == NULL) || (pPlot->getTerrainType() is not expected to be equal with NO_TERRAIN)");

	// handle our new special case
	const	CvPlot*	pAttackedPlot = NULL;
	bool	bAttackingUnknownDefender = false;
	if (pAttacker == this)
	{
		bAttackingUnknownDefender = true;
		pAttackedPlot = pPlot;

		// reset these values, we will fiddle with them below
		pPlot = NULL;
		pAttacker = NULL;
	}
	// otherwise, attack plot is the plot of us (the defender)
	else if (pAttacker != NULL)
	{
		pAttackedPlot = plot();
	}

	// lfgr note 05/2020: from now on, pAttacker != this

	if (pCombatDetails != NULL)
	{
		pCombatDetails->iExtraCombatPercent = 0;
		pCombatDetails->iAnimalCombatModifierTA = 0;
		pCombatDetails->iAIAnimalCombatModifierTA = 0;
		pCombatDetails->iAnimalCombatModifierAA = 0;
		pCombatDetails->iAIAnimalCombatModifierAA = 0;
		pCombatDetails->iBarbarianCombatModifierTB = 0;
		pCombatDetails->iAIBarbarianCombatModifierTB = 0;
		pCombatDetails->iBarbarianCombatModifierAB = 0;
		pCombatDetails->iAIBarbarianCombatModifierAB = 0;
		pCombatDetails->iPlotDefenseModifier = 0;
		pCombatDetails->iFortifyModifier = 0;
		pCombatDetails->iCityDefenseModifier = 0;
		pCombatDetails->iHillsAttackModifier = 0;
		pCombatDetails->iHillsDefenseModifier = 0;
		pCombatDetails->iFeatureAttackModifier = 0;
		pCombatDetails->iFeatureDefenseModifier = 0;
		pCombatDetails->iTerrainAttackModifier = 0;
		pCombatDetails->iTerrainDefenseModifier = 0;
		pCombatDetails->iCityAttackModifier = 0;
		pCombatDetails->iDomainDefenseModifier = 0;
		pCombatDetails->iCityBarbarianDefenseModifier = 0;
		pCombatDetails->iClassDefenseModifier = 0;
		pCombatDetails->iClassAttackModifier = 0;
		pCombatDetails->iCombatModifierA = 0;
		pCombatDetails->iCombatModifierT = 0;
		pCombatDetails->iDomainModifierA = 0;
		pCombatDetails->iDomainModifierT = 0;
		pCombatDetails->iAnimalCombatModifierA = 0;
		pCombatDetails->iAnimalCombatModifierT = 0;
		pCombatDetails->iRiverAttackModifier = 0;
		pCombatDetails->iAmphibAttackModifier = 0;
		pCombatDetails->iKamikazeModifier = 0;
		pCombatDetails->iModifierTotal = 0;
		pCombatDetails->iBaseCombatStr = 0;
		pCombatDetails->iCombat = 0;
		pCombatDetails->iMaxCombatStr = 0;
		pCombatDetails->iCurrHitPoints = 0;
		pCombatDetails->iMaxHitPoints = 0;
		pCombatDetails->iCurrCombatStr = 0;
		pCombatDetails->eOwner = getOwnerINLINE();
		pCombatDetails->eVisualOwner = getVisualOwner();
		pCombatDetails->sUnitName = getName().GetCString();
	}

//FfH Defense Str: Modified by Kael 08/18/2007
//	if (baseCombatStr() == 0)
//	{
//		return 0;
//	}
    int iStr;
    if ((pAttacker == NULL && pPlot == NULL) || pAttacker == this)
    {
        iStr = baseCombatStr();
    }
    else
    {
        iStr = baseCombatStrDefense();
    }

	if (iStr == 0)
	{
		return 0;
	}
//FfH: End Modify

	int iModifier = 0;
	int iExtraModifier;

	iExtraModifier = getExtraCombatPercent();
	iModifier += iExtraModifier;
	if (pCombatDetails != NULL)
	{
		pCombatDetails->iExtraCombatPercent = iExtraModifier;
	}

	// do modifiers for animals and barbarians (leaving these out for bAttackingUnknownDefender case)
	if (pAttacker != NULL)
	{
		if (isAnimal())
		{
			if (pAttacker->isHuman())
			{
				iExtraModifier = GC.getHandicapInfo(GC.getGameINLINE().getHandicapType()).getAnimalCombatModifier();
				iModifier += iExtraModifier;
				if (pCombatDetails != NULL)
				{
					pCombatDetails->iAnimalCombatModifierTA = iExtraModifier;
				}
			}
			else
			{
				iExtraModifier = GC.getHandicapInfo(GC.getGameINLINE().getHandicapType()).getAIAnimalCombatModifier();
				iModifier += iExtraModifier;
				if (pCombatDetails != NULL)
				{
					pCombatDetails->iAIAnimalCombatModifierTA = iExtraModifier;
				}
			}
		}

		if (pAttacker->isAnimal())
		{
			if (isHuman())
			{
				iExtraModifier = -GC.getHandicapInfo(GC.getGameINLINE().getHandicapType()).getAnimalCombatModifier();
				iModifier += iExtraModifier;
				if (pCombatDetails != NULL)
				{
					pCombatDetails->iAnimalCombatModifierAA = iExtraModifier;
				}
			}
			else
			{
				iExtraModifier = -GC.getHandicapInfo(GC.getGameINLINE().getHandicapType()).getAIAnimalCombatModifier();
				iModifier += iExtraModifier;
				if (pCombatDetails != NULL)
				{
					pCombatDetails->iAIAnimalCombatModifierAA = iExtraModifier;
				}
			}
		}

		if (isBarbarian())
		{
			if (pAttacker->isHuman())
			{
				iExtraModifier = GC.getHandicapInfo(GC.getGameINLINE().getHandicapType()).getBarbarianCombatModifier();
				iModifier += iExtraModifier;
				if (pCombatDetails != NULL)
				{
					pCombatDetails->iBarbarianCombatModifierTB = iExtraModifier;
				}
			}
			else
			{
				iExtraModifier = GC.getHandicapInfo(GC.getGameINLINE().getHandicapType()).getAIBarbarianCombatModifier();
				iModifier += iExtraModifier;
				if (pCombatDetails != NULL)
				{
					pCombatDetails->iAIBarbarianCombatModifierTB = iExtraModifier;
				}
			}
		}

		if (pAttacker->isBarbarian())
		{
			if (isHuman())
			{
				iExtraModifier = -GC.getHandicapInfo(GC.getGameINLINE().getHandicapType()).getBarbarianCombatModifier();
				iModifier += iExtraModifier;
				if (pCombatDetails != NULL)
				{
					pCombatDetails->iBarbarianCombatModifierAB = iExtraModifier;
				}
			}
			else
			{
				iExtraModifier = -GC.getHandicapInfo(GC.getGameINLINE().getHandicapType()).getAIBarbarianCombatModifier();
				iModifier += iExtraModifier;
				if (pCombatDetails != NULL)
				{

//FfH: Modified by Kael 07/31/2008
//					pCombatDetails->iAIBarbarianCombatModifierTB = iExtraModifier;
					pCombatDetails->iAIBarbarianCombatModifierAB = iExtraModifier;
//FfH: End Modify

				}
			}
		}
	}

	// add defensive bonuses (leaving these out for bAttackingUnknownDefender case)
	if (pPlot != NULL)
	{
//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/20
//*** Negative defense modifier from plot can apply to any units.
/*
		if (!noDefensiveBonus())
		{
			iExtraModifier = pPlot->defenseModifier(getTeam(), (pAttacker != NULL) ? pAttacker->ignoreBuildingDefense() : true);
*/
		iExtraModifier = pPlot->defenseModifier(getTeam(), (pAttacker != NULL) ? pAttacker->ignoreBuildingDefense() : true);
		if (!noDefensiveBonus() || iExtraModifier < 0)
		{
//<<<<Unofficial Bug Fix: End Modify
			iModifier += iExtraModifier;
			if (pCombatDetails != NULL)
			{
				pCombatDetails->iPlotDefenseModifier = iExtraModifier;
			}
		}

		iExtraModifier = fortifyModifier();
		iModifier += iExtraModifier;
		if (pCombatDetails != NULL)
		{
			pCombatDetails->iFortifyModifier = iExtraModifier;
		}

		if (pPlot->isCity(true, getTeam()))
		{
			iExtraModifier = cityDefenseModifier();
			iModifier += iExtraModifier;
			if (pCombatDetails != NULL)
			{
				pCombatDetails->iCityDefenseModifier = iExtraModifier;
			}
		}

		if (pPlot->isHills())
		{
			iExtraModifier = hillsDefenseModifier();
			iModifier += iExtraModifier;
			if (pCombatDetails != NULL)
			{
				pCombatDetails->iHillsDefenseModifier = iExtraModifier;
			}
		}

		if (pPlot->getFeatureType() != NO_FEATURE)
		{
			iExtraModifier = featureDefenseModifier(pPlot->getFeatureType());
			iModifier += iExtraModifier;
			if (pCombatDetails != NULL)
			{
				pCombatDetails->iFeatureDefenseModifier = iExtraModifier;
			}
		}
		else
		{
			iExtraModifier = terrainDefenseModifier(pPlot->getTerrainType());
			iModifier += iExtraModifier;
			if (pCombatDetails != NULL)
			{
				pCombatDetails->iTerrainDefenseModifier = iExtraModifier;
			}
		}
	}

	// if we are attacking to an plot with an unknown defender, the calc the modifier in reverse
	if (bAttackingUnknownDefender)
	{
		pAttacker = this;
	}

	// calc attacker bonueses
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       09/20/09                                jdog5000      */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original code
	if (pAttacker != NULL)
*/
	if (pAttacker != NULL && pAttackedPlot != NULL)
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
	{
		int iTempModifier = 0;		

		if (pAttackedPlot->isCity(true, getTeam()))
		{
			iExtraModifier = -pAttacker->cityAttackModifier();
			iTempModifier += iExtraModifier;
			if (pCombatDetails != NULL)
			{
				pCombatDetails->iCityAttackModifier = iExtraModifier;
			}

			if (pAttacker->isBarbarian())
			{
				iExtraModifier = GC.defines.iCITY_BARBARIAN_DEFENSE_MODIFIER;
				iTempModifier += iExtraModifier;
				if (pCombatDetails != NULL)
				{
					pCombatDetails->iCityBarbarianDefenseModifier = iExtraModifier;
				}
			}
		}

		if (pAttackedPlot->isHills())
		{
			iExtraModifier = -pAttacker->hillsAttackModifier();
			iTempModifier += iExtraModifier;
			if (pCombatDetails != NULL)
			{
				pCombatDetails->iHillsAttackModifier = iExtraModifier;
			}
		}

		if (pAttackedPlot->getFeatureType() != NO_FEATURE)
		{
			iExtraModifier = -pAttacker->featureAttackModifier(pAttackedPlot->getFeatureType());
			iTempModifier += iExtraModifier;
			if (pCombatDetails != NULL)
			{
				pCombatDetails->iFeatureAttackModifier = iExtraModifier;
			}
		}
		else
		{
			iExtraModifier = -pAttacker->terrainAttackModifier(pAttackedPlot->getTerrainType());
			iModifier += iExtraModifier;
			if (pCombatDetails != NULL)
			{
				pCombatDetails->iTerrainAttackModifier = iExtraModifier;
			}
		}

		// only compute comparisions if we are the defender with a known attacker
		if (!bAttackingUnknownDefender)
		{
			FAssertMsg(pAttacker != this, "pAttacker is not expected to be equal with this");

//FfH Promotions: Added by Kael 08/13/2007
            for (int iJ=0;iJ<GC.getNumPromotionInfos();iJ++)
            {
                if ((isHasPromotion((PromotionTypes)iJ)) && (GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod()>0))
                {
                    if (pAttacker->isHasPromotion((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatType()))
                    {
                        iModifier += GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod();
                    }
                }
                if ((pAttacker->isHasPromotion((PromotionTypes)iJ)) && (GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod() > 0))
                {
                    if (isHasPromotion((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatType()))
                    {
                        iModifier -= GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod();
                    }
                }
            }
            if (GC.getGameINLINE().getGlobalCounter() * getCombatPercentGlobalCounter() / 100 != 0)
            {
                iModifier += GC.getGameINLINE().getGlobalCounter() * getCombatPercentGlobalCounter() / 100;
            }
            if (GC.getGameINLINE().getGlobalCounter() * pAttacker->getCombatPercentGlobalCounter() / 100 != 0)
            {
                iModifier -= GC.getGameINLINE().getGlobalCounter() * pAttacker->getCombatPercentGlobalCounter() / 100;
            }
//FfH: End Add

			iExtraModifier = unitClassDefenseModifier(pAttacker->getUnitClassType());
			iTempModifier += iExtraModifier;
			if (pCombatDetails != NULL)
			{
				pCombatDetails->iClassDefenseModifier = iExtraModifier;
			}

			iExtraModifier = -pAttacker->unitClassAttackModifier(getUnitClassType());
			iTempModifier += iExtraModifier;
			if (pCombatDetails != NULL)
			{
				pCombatDetails->iClassAttackModifier = iExtraModifier;
			}

			if (pAttacker->getUnitCombatType() != NO_UNITCOMBAT)
			{
				iExtraModifier = unitCombatModifier(pAttacker->getUnitCombatType());
				iTempModifier += iExtraModifier;
				if (pCombatDetails != NULL)
				{
					pCombatDetails->iCombatModifierA = iExtraModifier;
				}
			}
			if (getUnitCombatType() != NO_UNITCOMBAT)
			{
				iExtraModifier = -pAttacker->unitCombatModifier(getUnitCombatType());
				iTempModifier += iExtraModifier;
				if (pCombatDetails != NULL)
				{
					pCombatDetails->iCombatModifierT = iExtraModifier;
				}
			}

			iExtraModifier = domainModifier(pAttacker->getDomainType());
			iTempModifier += iExtraModifier;
			if (pCombatDetails != NULL)
			{
				pCombatDetails->iDomainModifierA = iExtraModifier;
			}

			iExtraModifier = -pAttacker->domainModifier(getDomainType());
			iTempModifier += iExtraModifier;
			if (pCombatDetails != NULL)
			{
				pCombatDetails->iDomainModifierT = iExtraModifier;
			}

			if (pAttacker->isAnimal())
			{
				iExtraModifier = animalCombatModifier();
				iTempModifier += iExtraModifier;
				if (pCombatDetails != NULL)
				{
					pCombatDetails->iAnimalCombatModifierA = iExtraModifier;
				}
			}

			if (isAnimal())
			{
				iExtraModifier = -pAttacker->animalCombatModifier();
				iTempModifier += iExtraModifier;
				if (pCombatDetails != NULL)
				{
					pCombatDetails->iAnimalCombatModifierT = iExtraModifier;
				}
			}
		}

		if (!(pAttacker->isRiver()))
		{
			if (pAttacker->plot()->isRiverCrossing(directionXY(pAttacker->plot(), pAttackedPlot)))
			{
				iExtraModifier = -GC.getRIVER_ATTACK_MODIFIER();
				iTempModifier += iExtraModifier;
				if (pCombatDetails != NULL)
				{
					pCombatDetails->iRiverAttackModifier = iExtraModifier;
				}
			}
		}

		if (!(pAttacker->isAmphib()))
		{
			if (!(pAttackedPlot->isWater()) && pAttacker->plot()->isWater())
			{
				iExtraModifier = -GC.getAMPHIB_ATTACK_MODIFIER();
				iTempModifier += iExtraModifier;
				if (pCombatDetails != NULL)
				{
					pCombatDetails->iAmphibAttackModifier = iExtraModifier;
				}
			}
		}

		if (pAttacker->getKamikazePercent() != 0)
		{
			iExtraModifier = pAttacker->getKamikazePercent();
			iTempModifier += iExtraModifier;
			if (pCombatDetails != NULL)
			{
				pCombatDetails->iKamikazeModifier = iExtraModifier;
			}
		}

		// if we are attacking an unknown defender, then use the reverse of the modifier
		if (bAttackingUnknownDefender)
		{
			iModifier -= iTempModifier;
		}
		else
		{
			iModifier += iTempModifier;
		}
	}

//FfH Defense Str: Modified by Kael 08/18/2007
//	if (pCombatDetails != NULL)
//	{
//		pCombatDetails->iModifierTotal = iModifier;
//		pCombatDetails->iBaseCombatStr = baseCombatStr();
//	}
//
//	if (iModifier > 0)
//	{
//		iCombat = (baseCombatStr() * (iModifier + 100));
//	}
//	else
//	{
//		iCombat = ((baseCombatStr() * 10000) / (100 - iModifier));
//  }
    if (pCombatDetails != NULL)
    {
        pCombatDetails->iModifierTotal = iModifier;
        pCombatDetails->iBaseCombatStr = iStr;
    }

    iStr *= 100;
    if (pAttacker != NULL)
    {
        for (int iI = 0; iI < GC.getNumDamageTypeInfos(); iI++)
        {
            if (getDamageTypeCombat((DamageTypes) iI) != 0)
            {
                if (pAttacker->getDamageTypeResist((DamageTypes) iI) != 0)
                {
                    iStr -= getDamageTypeCombat((DamageTypes) iI) * 100;
                    iStr += getDamageTypeCombat((DamageTypes) iI) * (100 - pAttacker->getDamageTypeResist((DamageTypes) iI));
                }
            }
        }
    }
    if (pDefender != NULL)
    {
        for (int iI = 0; iI < GC.getNumDamageTypeInfos(); iI++)
        {
            if (getDamageTypeCombat((DamageTypes) iI) != 0)
            {
                if (pDefender->getDamageTypeResist((DamageTypes) iI) != 0)
                {
                    iStr -= getDamageTypeCombat((DamageTypes) iI) * 100;
                    iStr += getDamageTypeCombat((DamageTypes) iI) * (100 - pDefender->getDamageTypeResist((DamageTypes) iI));
                }
            }
        }
    }

    if (iModifier > 0)
    {
        iCombat = (iStr * (iModifier + 100)) / 100;
    }
    else
    {
        iCombat = ((iStr * 100) / (100 - iModifier));
    }
//FfH: End Modify

	if (pCombatDetails != NULL)
	{
		pCombatDetails->iCombat = iCombat;
		pCombatDetails->iMaxCombatStr = std::max(1, iCombat);
		pCombatDetails->iCurrHitPoints = currHitPoints();
		pCombatDetails->iMaxHitPoints = maxHitPoints();
		pCombatDetails->iCurrCombatStr = ((pCombatDetails->iMaxCombatStr * pCombatDetails->iCurrHitPoints) / pCombatDetails->iMaxHitPoints);
	}

	return std::max(1, iCombat);
}


int CvUnit::currCombatStr(const CvPlot* pPlot, const CvUnit* pAttacker, CombatDetails* pCombatDetails) const
{
	return ((maxCombatStr(pPlot, pAttacker, pCombatDetails) * currHitPoints()) / maxHitPoints());
}


int CvUnit::currFirepower(const CvPlot* pPlot, const CvUnit* pAttacker) const
{
	return ((maxCombatStr(pPlot, pAttacker) + currCombatStr(pPlot, pAttacker) + 1) / 2);
}

// this nomalizes str by firepower, useful for quick odds calcs
// the effect is that a damaged unit will have an effective str lowered by firepower/maxFirepower
// doing the algebra, this means we mulitply by 1/2(1 + currHP)/maxHP = (maxHP + currHP) / (2 * maxHP)
int CvUnit::currEffectiveStr(const CvPlot* pPlot, const CvUnit* pAttacker, CombatDetails* pCombatDetails) const
{
	int currStr = currCombatStr(pPlot, pAttacker, pCombatDetails);

	currStr *= (maxHitPoints() + currHitPoints());
	currStr /= (2 * maxHitPoints());

	return currStr;
}

float CvUnit::maxCombatStrFloat(const CvPlot* pPlot, const CvUnit* pAttacker) const
{
	return (((float)(maxCombatStr(pPlot, pAttacker))) / 100.0f);
}


float CvUnit::currCombatStrFloat(const CvPlot* pPlot, const CvUnit* pAttacker) const
{
	return (((float)(currCombatStr(pPlot, pAttacker))) / 100.0f);
}


bool CvUnit::canFight() const
{

//FfH: Modified by Kael 10/31/2007
//	return (baseCombatStr() > 0);
    if (baseCombatStr() == 0 && baseCombatStrDefense() == 0)
    {
        return false;
    }
	return true;
//FfH: End Modify

}


bool CvUnit::canAttack() const
{
	if (!canFight())
	{
		return false;
	}

	if (isOnlyDefensive())
	{
		return false;
	}

//FfH: Added by Kael 04/25/2010
    if (baseCombatStr() == 0)
    {
        return false;
    }

    if (getImmobileTimer() != 0)
    {
        return false;
    }
//FfH: End Add

	return true;
}
bool CvUnit::canAttack(const CvUnit& defender) const
{
	if (!canAttack())
	{
		return false;
	}

	if (defender.getDamage() >= combatLimit())
	{
		return false;
	}

	// Artillery can't amphibious attack
	if (plot()->isWater() && !defender.plot()->isWater())
	{
//>>>>Unofficial Bug Fix: Modified by Denev 2009/11/07
//*** Illusions can amphibious attack from ships.
//		if (combatLimit() < 100)
		if (combatLimit() < 100 && collateralDamage() > 0)
//<<<<Unofficial Bug Fix: End Modify
		{
			return false;
		}
	}

	return true;
}

bool CvUnit::canDefend(const CvPlot* pPlot) const
{
	if (pPlot == NULL)
	{
		pPlot = plot();
	}

	if (!canFight())
	{
		return false;
	}

	if (!pPlot->isValidDomainForAction(*this))
	{
		if (GC.defines.iLAND_UNITS_CAN_ATTACK_WATER_CITIES == 0)
		{
			return false;
		}
	}

//FfH: Added by Kael 10/31/2007
    if (baseCombatStrDefense() == 0)
    {
        return false;
    }
//FfH: End Add

	return true;
}


bool CvUnit::canSiege(TeamTypes eTeam) const
{
	if (!canDefend())
	{
		return false;
	}

	if (!isEnemy(eTeam))
	{
		return false;
	}

	if (!isNeverInvisible())
	{
		return false;
	}

	return true;
}


int CvUnit::airBaseCombatStr() const
{
	return m_pUnitInfo->getAirCombat();
}


int CvUnit::airMaxCombatStr(const CvUnit* pOther) const
{
	int iModifier;
	int iCombat;

	if (airBaseCombatStr() == 0)
	{
		return 0;
	}

	iModifier = getExtraCombatPercent();

	if (getKamikazePercent() != 0)
	{
		iModifier += getKamikazePercent();
	}

	if (getExtraCombatPercent() != 0)
	{
		iModifier += getExtraCombatPercent();
	}

	if (NULL != pOther)
	{
		if (pOther->getUnitCombatType() != NO_UNITCOMBAT)
		{
			iModifier += unitCombatModifier(pOther->getUnitCombatType());
		}

		iModifier += domainModifier(pOther->getDomainType());

		if (pOther->isAnimal())
		{
			iModifier += animalCombatModifier();
		}
	}

	if (iModifier > 0)
	{
		iCombat = (airBaseCombatStr() * (iModifier + 100));
	}
	else
	{
		iCombat = ((airBaseCombatStr() * 10000) / (100 - iModifier));
	}

	return std::max(1, iCombat);
}


int CvUnit::airCurrCombatStr(const CvUnit* pOther) const
{
	return ((airMaxCombatStr(pOther) * currHitPoints()) / maxHitPoints());
}


float CvUnit::airMaxCombatStrFloat(const CvUnit* pOther) const
{
	return (((float)(airMaxCombatStr(pOther))) / 100.0f);
}


float CvUnit::airCurrCombatStrFloat(const CvUnit* pOther) const
{
	return (((float)(airCurrCombatStr(pOther))) / 100.0f);
}


int CvUnit::combatLimit() const
{

//FfH: Modified by Kael 04/26/2008
//	return m_pUnitInfo->getCombatLimit();
    return m_iCombatLimit;
//FfH: End Modify

}


int CvUnit::airCombatLimit() const
{
	return m_pUnitInfo->getAirCombatLimit();
}


bool CvUnit::canAirAttack() const
{
	return (airBaseCombatStr() > 0);
}


bool CvUnit::canAirDefend(const CvPlot* pPlot) const
{
	if (pPlot == NULL)
	{
		pPlot = plot();
	}

	if (maxInterceptionProbability() == 0)
	{
		return false;
	}

	if (getDomainType() != DOMAIN_AIR)
	{
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       10/30/09                     Mongoose & jdog5000      */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
		if (!pPlot->isValidDomainForLocation(*this))
*/
		// From Mongoose SDK
		// Land units which are cargo cannot intercept
		if (!pPlot->isValidDomainForLocation(*this) || isCargo())
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
		{
			return false;
		}
	}

	return true;
}


int CvUnit::airCombatDamage(const CvUnit* pDefender) const
{
	CvCity* pCity;
	CvPlot* pPlot;
	int iOurStrength;
	int iTheirStrength;
	int iStrengthFactor;
	int iDamage;

	pPlot = pDefender->plot();

	iOurStrength = airCurrCombatStr(pDefender);
	FAssertMsg(iOurStrength > 0, "Air combat strength is expected to be greater than zero");
	iTheirStrength = pDefender->maxCombatStr(pPlot, this);

	iStrengthFactor = ((iOurStrength + iTheirStrength + 1) / 2);

	iDamage = std::max(1, ((GC.defines.iAIR_COMBAT_DAMAGE * (iOurStrength + iStrengthFactor)) / (iTheirStrength + iStrengthFactor)));

	pCity = pPlot->getPlotCity();

	if (pCity != NULL)
	{
		iDamage *= std::max(0, (pCity->getAirModifier() + 100));
		iDamage /= 100;
	}

	return iDamage;
}


int CvUnit::rangeCombatDamage(const CvUnit* pDefender) const
{
	CvPlot* pPlot;
	int iOurStrength;
	int iTheirStrength;
	int iStrengthFactor;
	int iDamage;

	pPlot = pDefender->plot();

	iOurStrength = airCurrCombatStr(pDefender);
	FAssertMsg(iOurStrength > 0, "Combat strength is expected to be greater than zero");
	iTheirStrength = pDefender->maxCombatStr(pPlot, this);

	iStrengthFactor = ((iOurStrength + iTheirStrength + 1) / 2);

	iDamage = std::max(1, ((GC.defines.iRANGE_COMBAT_DAMAGE * (iOurStrength + iStrengthFactor)) / (iTheirStrength + iStrengthFactor)));

	return iDamage;
}


CvUnit* CvUnit::bestInterceptor(const CvPlot* pPlot) const
{
	CvUnit* pLoopUnit;
	CvUnit* pBestUnit;
	int iValue;
	int iBestValue;
	int iLoop;
	int iI;

	iBestValue = 0;
	pBestUnit = NULL;

	for (iI = 0; iI < MAX_PLAYERS; iI++)
	{
		if (GET_PLAYER((PlayerTypes)iI).isAlive())
		{
			if (isEnemy(GET_PLAYER((PlayerTypes)iI).getTeam()) && !isInvisible(GET_PLAYER((PlayerTypes)iI).getTeam(), false, false))
			{
				for(pLoopUnit = GET_PLAYER((PlayerTypes)iI).firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = GET_PLAYER((PlayerTypes)iI).nextUnit(&iLoop))
				{
					if (pLoopUnit->canAirDefend())
					{
						if (!pLoopUnit->isMadeInterception())
						{
							if ((pLoopUnit->getDomainType() != DOMAIN_AIR) || !(pLoopUnit->hasMoved()))
							{
								if ((pLoopUnit->getDomainType() != DOMAIN_AIR) || (pLoopUnit->getGroup()->getActivityType() == ACTIVITY_INTERCEPT))
								{
									if (plotDistance(pLoopUnit->getX_INLINE(), pLoopUnit->getY_INLINE(), pPlot->getX_INLINE(), pPlot->getY_INLINE()) <= pLoopUnit->airRange())
									{
										iValue = pLoopUnit->currInterceptionProbability();

										if (iValue > iBestValue)
										{
											iBestValue = iValue;
											pBestUnit = pLoopUnit;
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}

	return pBestUnit;
}


CvUnit* CvUnit::bestSeaPillageInterceptor(CvUnit* pPillager, int iMinOdds) const
{
	CvUnit* pBestUnit = NULL;

	for (int iDX = -1; iDX <= 1; ++iDX)
	{
		for (int iDY = -1; iDY <= 1; ++iDY)
		{
			CvPlot* pLoopPlot = plotXY(pPillager->getX_INLINE(), pPillager->getY_INLINE(), iDX, iDY);

			if (NULL != pLoopPlot)
			{
				CLLNode<IDInfo>* pUnitNode = pLoopPlot->headUnitNode();

				while (NULL != pUnitNode)
				{
					CvUnit* pLoopUnit = ::getUnit(pUnitNode->m_data);
					pUnitNode = pLoopPlot->nextUnitNode(pUnitNode);

					if (NULL != pLoopUnit)
					{
						if (pLoopUnit->area() == pPillager->plot()->area())
						{
							if (!pLoopUnit->isInvisible(getTeam(), false))
							{
								if (isEnemy(pLoopUnit->getTeam()))
								{
									if (DOMAIN_SEA == pLoopUnit->getDomainType())
									{
										if (ACTIVITY_PATROL == pLoopUnit->getGroup()->getActivityType())
										{
											if (NULL == pBestUnit || pLoopUnit->isBetterDefenderThan(pBestUnit, this))
											{
												if (getCombatOdds(pPillager, pLoopUnit) < iMinOdds)
												{
													pBestUnit = pLoopUnit;
												}
											}
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}

	return pBestUnit;
}


bool CvUnit::isAutomated() const
{
	return getGroup()->isAutomated();
}


bool CvUnit::isWaiting() const
{
	return getGroup()->isWaiting();
}


bool CvUnit::isFortifyable() const
{
	if (!canFight() || noDefensiveBonus() || ((getDomainType() != DOMAIN_LAND) && (getDomainType() != DOMAIN_IMMOBILE)))
	{
		return false;
	}

	return true;
}


int CvUnit::fortifyModifier() const
{
	if (!isFortifyable())
	{
		return 0;
	}

//FfH: Modified by Kael 10/26/2007
//	return (getFortifyTurns() * GC.getFORTIFY_MODIFIER_PER_TURN());
   	int i = getFortifyTurns() * GC.getFORTIFY_MODIFIER_PER_TURN();
    if (isDoubleFortifyBonus())
    {
        i *= 2;
    }
    return i;
//FfH: End Modify

}


int CvUnit::experienceNeeded() const
{
// BUG - Unit Experience - start
	return calculateExperience(getLevel(), getOwnerINLINE());
// BUG - Unit Experience - end
}


int CvUnit::attackXPValue() const
{

//FfH: Modified by Kael 02/12/2009
//	return m_pUnitInfo->getXPValueAttack();
    int iXP = m_pUnitInfo->getXPValueAttack();
	if (isAnimal() || isBarbarian())
	{
	    iXP = iXP * GC.defines.iBARBARIAN_EXPERIENCE_MODIFIER / 100;
	}
	return iXP;
//FfH: End Modify

}


int CvUnit::defenseXPValue() const
{

//FfH: Modified by Kael 02/12/2009
//	return m_pUnitInfo->getXPValueDefense();
    int iXP = m_pUnitInfo->getXPValueDefense();
	if (isAnimal() || isBarbarian())
	{
	    iXP = iXP * GC.defines.iBARBARIAN_EXPERIENCE_MODIFIER / 100;
	}
	return iXP;
//FfH: End Modify

}


int CvUnit::maxXPValue() const
{
	int iMaxValue;

	iMaxValue = MAX_INT;

//FfH: Modified by Kael 02/12/2009
//	if (isAnimal())
//	{
//		iMaxValue = std::min(iMaxValue, GC.defines.iANIMAL_MAX_XP_VALUE);
//	}
//	if (isBarbarian())
//	{
//		iMaxValue = std::min(iMaxValue, GC.defines.iBARBARIAN_MAX_XP_VALUE);
//	}
	if (!::isWorldUnitClass(getUnitClassType()))
	{
        if (isAnimal())
        {
            iMaxValue = std::min(iMaxValue, GC.defines.iANIMAL_MAX_XP_VALUE);
        }
        if (isBarbarian())
        {
            iMaxValue = std::min(iMaxValue, GC.defines.iBARBARIAN_MAX_XP_VALUE);
        }
	}
//FfH: End Modify

	return iMaxValue;
}


int CvUnit::firstStrikes() const
{
	return std::max(0, (m_pUnitInfo->getFirstStrikes() + getExtraFirstStrikes()));
}


int CvUnit::chanceFirstStrikes() const
{
	return std::max(0, (m_pUnitInfo->getChanceFirstStrikes() + getExtraChanceFirstStrikes()));
}


int CvUnit::maxFirstStrikes() const
{
	return (firstStrikes() + chanceFirstStrikes());
}


bool CvUnit::isRanged() const
{
	int i;
	CvUnitInfo * pkUnitInfo = &getUnitInfo();
	for ( i = 0; i < pkUnitInfo->getGroupDefinitions(); i++ )
	{
		if ( !getArtInfo(i, GET_PLAYER(getOwnerINLINE()).getCurrentRealEra())->getActAsRanged() )
		{
			return false;
		}
	}
	return true;
}


bool CvUnit::alwaysInvisible() const
{
	return m_pUnitInfo->isInvisible();
}


bool CvUnit::immuneToFirstStrikes() const
{
	return (m_pUnitInfo->isFirstStrikeImmune() || (getImmuneToFirstStrikesCount() > 0));
}


bool CvUnit::noDefensiveBonus() const
{
	return m_pUnitInfo->isNoDefensiveBonus();
}


bool CvUnit::ignoreBuildingDefense() const
{

//FfH: Modifed by Kael 11/17/2007
//	return m_pUnitInfo->isIgnoreBuildingDefense();
    if (m_pUnitInfo->isIgnoreBuildingDefense())
    {
        return true;
    }
	return m_iIgnoreBuildingDefense == 0 ? false : true;
//FfH: End Modify

}


bool CvUnit::canMoveImpassable() const
{

//FfH Flying: Added by Kael 07/30/2007
    if (isFlying())
    {
        return true;
    }
//FfH: End Add
	return m_iCanMoveImpassable == 0 ? false : true;
	//return m_pUnitInfo->isCanMoveImpassable();
}

bool CvUnit::canMoveAllTerrain() const
{

//FfH Flying: Added by Kael 07/30/2007
    if (isFlying() || isWaterWalking())
    {
        return true;
    }
//FfH: End Add

	return m_pUnitInfo->isCanMoveAllTerrain();
}

bool CvUnit::canMoveLimitedBorders() const
{
	return m_iCanMoveLimitedBorders == 0 ? false : true;
}

bool CvUnit::flatMovementCost() const
{

//FfH Flying: Added by Kael 07/30/2007
    if (isFlying())
    {
        return true;
    }
//FfH: End Add

	return m_pUnitInfo->isFlatMovementCost();
}


bool CvUnit::ignoreTerrainCost() const
{

//FfH Flying: Added by Kael 07/30/2007
    if (isFlying())
    {
        return true;
    }
//FfH: End Add

	return m_pUnitInfo->isIgnoreTerrainCost();
}


bool CvUnit::isNeverInvisible() const
{
	return (!alwaysInvisible() && (getInvisibleType() == NO_INVISIBLE));
}


bool CvUnit::isInvisible(TeamTypes eTeam, bool bDebug, bool bCheckCargo) const
{
	if (bDebug && GC.getGameINLINE().isDebugMode())
	{
		return false;
	}

	if (getTeam() == eTeam)
	{
		return false;
	}

//>>>>Unofficial Bug Fix: Moved from below(*2) by Denev 2009/10/19
//*** Cargo checking should be placed before invisibile check, because cargo checking doesn't relate invisibility.
//*** This is not a visibility matter, but a sytem rule. Even Dies Diei can't reveal units which loaded on.
	if (alwaysInvisible())
	{
		return true;
	}

	if (bCheckCargo && isCargo())
	{
		return true;
	}
//<<<<Unofficial Bug Fix: End Move

//FfH: Added by Kael 04/11/2008
    if (plot() != NULL)
    {
        if (plot()->isCity(GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS))) // Super Forts *custom*
        {
            if (getTeam() == plot()->getTeam())
            {
                return false;
            }
        }
        if (plot()->isOwned())
        {
            if (plot()->getTeam() != getTeam())
            {
                if (GET_PLAYER(plot()->getOwnerINLINE()).isSeeInvisible())
                {
                    return false;
                }
            }
            /* Redundant Code removed by Red Key... see also CvUnit::getInvisibleType
			if (plot()->getTeam() == getTeam())
            {
                if (GET_PLAYER(plot()->getOwnerINLINE()).isHideUnits() && !isIgnoreHide())
                {
                    return true;
                }
            }*/
        }
    }
//FfH: End Add

//>>>>Unofficial Bug Fix: Moved to above(*2) by Denev 2009/10/19
/*
	if (alwaysInvisible())
	{
		return true;
	}

	if (bCheckCargo && isCargo())
	{
		return true;
	}
*/
//<<<<Unofficial Bug Fix: End Move

	if (getInvisibleType() == NO_INVISIBLE)
	{
		return false;
	}

//FfH: Added by Kael 01/16/2009
    if (plot() == NULL)
    {
        return false;
    }
//FfH: End Add

	return !(plot()->isInvisibleVisible(eTeam, getInvisibleType()));
}


bool CvUnit::isNukeImmune() const
{
	return m_pUnitInfo->isNukeImmune();
}


int CvUnit::maxInterceptionProbability() const
{
	return std::max(0, m_pUnitInfo->getInterceptionProbability() + getExtraIntercept());
}


int CvUnit::currInterceptionProbability() const
{
	if (getDomainType() != DOMAIN_AIR)
	{
		return maxInterceptionProbability();
	}
	else
	{
		return ((maxInterceptionProbability() * currHitPoints()) / maxHitPoints());
	}
}


int CvUnit::evasionProbability() const
{
	return std::max(0, m_pUnitInfo->getEvasionProbability() + getExtraEvasion());
}


int CvUnit::withdrawalProbability() const
{
	if (getDomainType() == DOMAIN_LAND && plot()->isWater())
	{
		return 0;
	}

//FfH: Added by Kael 04/06/2009
    if (getImmobileTimer() > 0)
    {
        return 0;
    }
//FfH: End Add

	// Advanced Tactics - all units have an inherent 10% withdrawal chance
	int iWithDrawalBonus = 0;
	if (GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS))
	{
		if ((getDuration() == 0) && !m_pUnitInfo->isObject())
		{
			iWithDrawalBonus += 10;
		}
	}

	return std::max(0, (m_pUnitInfo->getWithdrawalProbability() + getExtraWithdrawal() + iWithDrawalBonus));
}


int CvUnit::collateralDamage() const
{
	return std::max(0, (m_pUnitInfo->getCollateralDamage()));
}


int CvUnit::collateralDamageLimit() const
{
	return std::max(0, m_pUnitInfo->getCollateralDamageLimit() * GC.getMAX_HIT_POINTS() / 100);
}


int CvUnit::collateralDamageMaxUnits() const
{
	return std::max(0, m_pUnitInfo->getCollateralDamageMaxUnits());
}


int CvUnit::cityAttackModifier() const
{
	return (m_pUnitInfo->getCityAttackModifier() + getExtraCityAttackPercent());
}


int CvUnit::cityDefenseModifier() const
{
	return (m_pUnitInfo->getCityDefenseModifier() + getExtraCityDefensePercent());
}


int CvUnit::animalCombatModifier() const
{
	return m_pUnitInfo->getAnimalCombatModifier();
}


int CvUnit::hillsAttackModifier() const
{
	return (m_pUnitInfo->getHillsAttackModifier() + getExtraHillsAttackPercent());
}


int CvUnit::hillsDefenseModifier() const
{
	return (m_pUnitInfo->getHillsDefenseModifier() + getExtraHillsDefensePercent());
}


int CvUnit::terrainAttackModifier(TerrainTypes eTerrain) const
{
	FAssertMsg(eTerrain >= 0, "eTerrain is expected to be non-negative (invalid Index)");
	FAssertMsg(eTerrain < GC.getNumTerrainInfos(), "eTerrain is expected to be within maximum bounds (invalid Index)");
	return (m_pUnitInfo->getTerrainAttackModifier(eTerrain) + getExtraTerrainAttackPercent(eTerrain));
}


int CvUnit::terrainDefenseModifier(TerrainTypes eTerrain) const
{
	FAssertMsg(eTerrain >= 0, "eTerrain is expected to be non-negative (invalid Index)");
	FAssertMsg(eTerrain < GC.getNumTerrainInfos(), "eTerrain is expected to be within maximum bounds (invalid Index)");
	return (m_pUnitInfo->getTerrainDefenseModifier(eTerrain) + getExtraTerrainDefensePercent(eTerrain));
}


int CvUnit::featureAttackModifier(FeatureTypes eFeature) const
{
	FAssertMsg(eFeature >= 0, "eFeature is expected to be non-negative (invalid Index)");
	FAssertMsg(eFeature < GC.getNumFeatureInfos(), "eFeature is expected to be within maximum bounds (invalid Index)");
	return (m_pUnitInfo->getFeatureAttackModifier(eFeature) + getExtraFeatureAttackPercent(eFeature));
}

int CvUnit::featureDefenseModifier(FeatureTypes eFeature) const
{
	FAssertMsg(eFeature >= 0, "eFeature is expected to be non-negative (invalid Index)");
	FAssertMsg(eFeature < GC.getNumFeatureInfos(), "eFeature is expected to be within maximum bounds (invalid Index)");
	return (m_pUnitInfo->getFeatureDefenseModifier(eFeature) + getExtraFeatureDefensePercent(eFeature));
}

int CvUnit::unitClassAttackModifier(UnitClassTypes eUnitClass) const
{
	FAssertMsg(eUnitClass >= 0, "eUnitClass is expected to be non-negative (invalid Index)");
	FAssertMsg(eUnitClass < GC.getNumUnitClassInfos(), "eUnitClass is expected to be within maximum bounds (invalid Index)");
	return m_pUnitInfo->getUnitClassAttackModifier(eUnitClass);
}


int CvUnit::unitClassDefenseModifier(UnitClassTypes eUnitClass) const
{
	FAssertMsg(eUnitClass >= 0, "eUnitClass is expected to be non-negative (invalid Index)");
	FAssertMsg(eUnitClass < GC.getNumUnitClassInfos(), "eUnitClass is expected to be within maximum bounds (invalid Index)");
	return m_pUnitInfo->getUnitClassDefenseModifier(eUnitClass);
}


int CvUnit::unitCombatModifier(UnitCombatTypes eUnitCombat) const
{
	FAssertMsg(eUnitCombat >= 0, "eUnitCombat is expected to be non-negative (invalid Index)");
	FAssertMsg(eUnitCombat < GC.getNumUnitCombatInfos(), "eUnitCombat is expected to be within maximum bounds (invalid Index)");
	return (m_pUnitInfo->getUnitCombatModifier(eUnitCombat) + getExtraUnitCombatModifier(eUnitCombat));
}


int CvUnit::domainModifier(DomainTypes eDomain) const
{
	FAssertMsg(eDomain >= 0, "eDomain is expected to be non-negative (invalid Index)");
	FAssertMsg(eDomain < NUM_DOMAIN_TYPES, "eDomain is expected to be within maximum bounds (invalid Index)");
	return (m_pUnitInfo->getDomainModifier(eDomain) + getExtraDomainModifier(eDomain));
}


int CvUnit::bombardRate() const
{
	return (m_pUnitInfo->getBombardRate() + getExtraBombardRate());
}


int CvUnit::airBombBaseRate() const
{
	return m_pUnitInfo->getBombRate();
}


int CvUnit::airBombCurrRate() const
{
	return ((airBombBaseRate() * currHitPoints()) / maxHitPoints());
}


SpecialUnitTypes CvUnit::specialCargo() const
{
	return ((SpecialUnitTypes)(m_pUnitInfo->getSpecialCargo()));
}


DomainTypes CvUnit::domainCargo() const
{
	return ((DomainTypes)(m_pUnitInfo->getDomainCargo()));
}


int CvUnit::cargoSpace() const
{
	return m_iCargoCapacity;
}

void CvUnit::changeCargoSpace(int iChange)
{
	if (iChange != 0)
	{
		m_iCargoCapacity += iChange;
// Tholal AI - ship crew promotions can cause a negative cargo value
//		FAssert(m_iCargoCapacity >= 0);
		setInfoBarDirty(true);
	}
}

bool CvUnit::isFull() const
{
	return (getCargo() >= cargoSpace());
}


int CvUnit::cargoSpaceAvailable(SpecialUnitTypes eSpecialCargo, DomainTypes eDomainCargo) const
{
	if (specialCargo() != NO_SPECIALUNIT)
	{
		if (specialCargo() != eSpecialCargo)
		{
			return 0;
		}
	}

	if (domainCargo() != NO_DOMAIN)
	{
		if (domainCargo() != eDomainCargo)
		{
			return 0;
		}
	}

	return std::max(0, (cargoSpace() - getCargo()));
}


bool CvUnit::hasCargo() const
{
	return (getCargo() > 0);
}


bool CvUnit::canCargoAllMove() const
{
	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pLoopUnit;
	CvPlot* pPlot;

	pPlot = plot();

	pUnitNode = pPlot->headUnitNode();

	while (pUnitNode != NULL)
	{
		pLoopUnit = ::getUnit(pUnitNode->m_data);
		pUnitNode = pPlot->nextUnitNode(pUnitNode);

		if (pLoopUnit->getTransportUnit() == this)
		{
			if (pLoopUnit->getDomainType() == DOMAIN_LAND)
			{
				if (!(pLoopUnit->canMove()))
				{
					return false;
				}
			}
		}
	}

	return true;
}

bool CvUnit::canCargoEnterArea(TeamTypes eTeam, const CvArea* pArea, bool bIgnoreRightOfPassage) const
{
	CvPlot* pPlot = plot();

	CLLNode<IDInfo>* pUnitNode = pPlot->headUnitNode();

	while (pUnitNode != NULL)
	{
		CvUnit* pLoopUnit = ::getUnit(pUnitNode->m_data);
		pUnitNode = pPlot->nextUnitNode(pUnitNode);

		if (pLoopUnit->getTransportUnit() == this)
		{
			if (!pLoopUnit->canEnterArea(eTeam, pArea, bIgnoreRightOfPassage))
			{
				return false;
			}
		}
	}

	return true;
}

int CvUnit::getUnitAICargo(UnitAITypes eUnitAI) const
{
	int iCount = 0;

	std::vector<CvUnit*> aCargoUnits;
	getCargoUnits(aCargoUnits);
	for (uint i = 0; i < aCargoUnits.size(); ++i)
	{
		if (aCargoUnits[i]->AI_getUnitAIType() == eUnitAI)
		{
			++iCount;
		}
	}

	return iCount;
}


int CvUnit::getID() const
{
	return m_iID;
}


int CvUnit::getIndex() const
{
	return (getID() & FLTA_INDEX_MASK);
}


IDInfo CvUnit::getIDInfo() const
{
	IDInfo unit(getOwnerINLINE(), getID());
	return unit;
}


void CvUnit::setID(int iID)
{
	m_iID = iID;
}


int CvUnit::getGroupID() const
{
	return m_iGroupID;
}


bool CvUnit::isInGroup() const
{
	return(getGroupID() != FFreeList::INVALID_INDEX);
}


bool CvUnit::isGroupHead() const // XXX is this used???
{
	return (getGroup()->getHeadUnit() == this);
}


CvSelectionGroup* CvUnit::getGroup() const
{
	return GET_PLAYER(getOwnerINLINE()).getSelectionGroup(getGroupID());
}


bool CvUnit::canJoinGroup(const CvPlot* pPlot, CvSelectionGroup* pSelectionGroup) const
{
	CvUnit* pHeadUnit;

	// do not allow someone to join a group that is about to be split apart
	// this prevents a case of a never-ending turn
	if (pSelectionGroup->AI_isForceSeparate())
	{
		return false;
	}

	if (pSelectionGroup->getOwnerINLINE() == NO_PLAYER)
	{
		pHeadUnit = pSelectionGroup->getHeadUnit();

		if (pHeadUnit != NULL)
		{
			if (pHeadUnit->getOwnerINLINE() != getOwnerINLINE())
			{
				return false;
			}
		}
	}
	else
	{
		if (pSelectionGroup->getOwnerINLINE() != getOwnerINLINE())
		{
			return false;
		}
	}

	if (pSelectionGroup->getNumUnits() > 0)
	{
		if (!(pSelectionGroup->atPlot(pPlot)))
		{
			return false;
		}

		if (pSelectionGroup->getDomainType() != getDomainType())
		{
			return false;
		}

/*************************************************************************************************/
/**	Xienwolf Tweak							01/04/09											**/
/**	ADDON (Allow HN units to group) merged Sephi									            **/
/**							Allows HN units to group with each other							**/
/*************************************************************************************************/
/**								---- Start Original Code ----									**
//FfH: Added by Kael 11/14/2007
        if (isAIControl())
        {
            return false;
        }
        if (isHiddenNationality())
        {
            return false;
        }
        pHeadUnit = pSelectionGroup->getHeadUnit();
        if (pHeadUnit != NULL)
        {
            if (pHeadUnit->isHiddenNationality())
            {
                return false;
            }
            if (pHeadUnit->isAIControl())
            {
                return false;
            }
		}
//FfH: End Add
/**								----  End Original Code  ----									**/
        pHeadUnit = pSelectionGroup->getHeadUnit();
        if (pHeadUnit != NULL)
	    {
			if (pHeadUnit->isHiddenNationality() != isHiddenNationality())
			{
                return false;
			}
            if (pHeadUnit->isAIControl() != isAIControl())
			{
                return false;
			}
		}
/*************************************************************************************************/
/**	Tweak									END													**/
/*************************************************************************************************/

	}

	return true;
}

// K-Mod has edited this function to increase readability and robustness

void CvUnit::joinGroup(CvSelectionGroup* pSelectionGroup, bool bRemoveSelected, bool bRejoin)
{
	CvSelectionGroup* pOldSelectionGroup = GET_PLAYER(getOwnerINLINE()).getSelectionGroup(getGroupID());

	if (pOldSelectionGroup && pSelectionGroup == pOldSelectionGroup)
		return; // attempting to join the group we are already in

	CvPlot* pPlot = plot();
	CvSelectionGroup* pNewSelectionGroup = pSelectionGroup;

	if (pNewSelectionGroup == NULL && bRejoin)
	{
		pNewSelectionGroup = GET_PLAYER(getOwnerINLINE()).addSelectionGroup();
		pNewSelectionGroup->init(pNewSelectionGroup->getID(), getOwnerINLINE());
	}

	if (pNewSelectionGroup == NULL || canJoinGroup(pPlot, pNewSelectionGroup))
	{
		if (pOldSelectionGroup != NULL)
		{
			bool bWasHead = false;
			if (!isHuman())
			{
				if (pOldSelectionGroup->getNumUnits() > 1)
				{
					if (pOldSelectionGroup->getHeadUnit() == this)
					{
						bWasHead = true;
					}
				}
			}

			pOldSelectionGroup->removeUnit(this);

			// if we were the head, if the head unitAI changed, then force the group to separate (non-humans)
			if (bWasHead)
			{
				FAssert(pOldSelectionGroup->getHeadUnit() != NULL);
				if (pOldSelectionGroup->getHeadUnit()->AI_getUnitAIType() != AI_getUnitAIType())
				{
						pOldSelectionGroup->AI_makeForceSeparate();
				}
			}
		}

		if ((pNewSelectionGroup != NULL) && pNewSelectionGroup->addUnit(this, false))
		{
			m_iGroupID = pNewSelectionGroup->getID();
		}
		else
		{
			m_iGroupID = FFreeList::INVALID_INDEX;
		}

		if (getGroup() != NULL)
		{
			// K-Mod
			if (isGroupHead())
				GET_PLAYER(getOwnerINLINE()).updateGroupCycle(this);
			// K-Mod end
			if (getGroup()->getNumUnits() > 1)
			{
				// K-Mod
				// For the AI, only wake the group in particular circumstances. This is to avoid AI deadlocks where they just keep grouping and ungroup indefinitely.
				// If the activity type is not changed at all, then that would enable exploits such as adding new units to air patrol groups to bypass the movement conditions.
				if (isHuman())
				{
					getGroup()->setAutomateType(NO_AUTOMATE);
					getGroup()->setActivityType(ACTIVITY_AWAKE);
					getGroup()->clearMissionQueue();
					// K-Mod note. the mission queue has to be cleared, because when the shift key is released, the exe automatically sends the autoMission net message.
					// (if the mission queue isn't cleared, the units will immediately begin their message whenever units are added using shift.)
				}
				else if (getGroup()->AI_getMissionAIType() == MISSIONAI_GROUP || getLastMoveTurn() == GC.getGameINLINE().getTurnSlice())
					getGroup()->setActivityType(ACTIVITY_AWAKE);
				else if (getGroup()->getActivityType() != ACTIVITY_AWAKE)
					getGroup()->setActivityType(ACTIVITY_HOLD); // don't let them cheat.
				// K-Mod end
			}
		}

		if (getTeam() == GC.getGameINLINE().getActiveTeam())
		{
			if (pPlot != NULL)
			{
				pPlot->setFlagDirty(true);
			}
		}

		if (pPlot == gDLL->getInterfaceIFace()->getSelectionPlot())
		{
			gDLL->getInterfaceIFace()->setDirty(PlotListButtons_DIRTY_BIT, true);
		}
	}

	if (bRemoveSelected && IsSelected())
	{
		gDLL->getInterfaceIFace()->removeFromSelectionList(this);
	}
}

/*
void CvUnit::joinGroup(CvSelectionGroup* pSelectionGroup, bool bRemoveSelected, bool bRejoin)
{
	CvSelectionGroup* pOldSelectionGroup;
	CvSelectionGroup* pNewSelectionGroup;
	CvPlot* pPlot;

	pOldSelectionGroup = GET_PLAYER(getOwnerINLINE()).getSelectionGroup(getGroupID());

	if ((pSelectionGroup != pOldSelectionGroup) || (pOldSelectionGroup == NULL))
	{
		pPlot = plot();

		if (pSelectionGroup != NULL)
		{
			pNewSelectionGroup = pSelectionGroup;
		}
		else
		{
			if (bRejoin)
			{
				pNewSelectionGroup = GET_PLAYER(getOwnerINLINE()).addSelectionGroup();
				pNewSelectionGroup->init(pNewSelectionGroup->getID(), getOwnerINLINE());
			}
			else
			{
				pNewSelectionGroup = NULL;
			}
		}

		if ((pNewSelectionGroup == NULL) || canJoinGroup(pPlot, pNewSelectionGroup))
		{
			if (pOldSelectionGroup != NULL)
			{
				bool bWasHead = false;
				if (!isHuman())
				{
					if (pOldSelectionGroup->getNumUnits() > 1)
					{
						if (pOldSelectionGroup->getHeadUnit() == this)
						{
							bWasHead = true;
						}
					}
				}

				pOldSelectionGroup->removeUnit(this);

				// if we were the head, if the head unitAI changed, then force the group to separate (non-humans)


                bool bValid = true;
                if (pSelectionGroup != NULL && pSelectionGroup->getHeadUnit())
                {
                    if (AI_getGroupflag() == GROUPFLAG_CONQUEST && pSelectionGroup->getHeadUnit()->AI_getGroupflag() == GROUPFLAG_CONQUEST)
                    {
                        bValid = false;
                    }
                }

                if (pSelectionGroup!=NULL && pSelectionGroup->getHeadUnit())
                {
                    if (AI_getGroupflag()==GROUPFLAG_PATROL && pSelectionGroup->getHeadUnit()->AI_getGroupflag()==GROUPFLAG_PATROL)
                    {
                        bValid=false;
                    }
                }

                if (bWasHead && bValid)
                {
					FAssert(pOldSelectionGroup->getHeadUnit() != NULL);
					if (pOldSelectionGroup->getHeadUnit()->AI_getUnitAIType() != AI_getUnitAIType())
					{
						pOldSelectionGroup->AI_makeForceSeparate();
					}
				}
			}

			if ((pNewSelectionGroup != NULL) && pNewSelectionGroup->addUnit(this, false))
			{
				m_iGroupID = pNewSelectionGroup->getID();
			}
			else
			{
				m_iGroupID = FFreeList::INVALID_INDEX;
			}

			if (getGroup() != NULL)
			{
				if (getGroup()->getNumUnits() > 1)
				{
					getGroup()->setActivityType(ACTIVITY_AWAKE);
				}
				else
				{
					GET_PLAYER(getOwnerINLINE()).updateGroupCycle(this);
				}
			}

			if (getTeam() == GC.getGameINLINE().getActiveTeam())
			{
				if (pPlot != NULL)
				{
					pPlot->setFlagDirty(true);
				}
			}

			if (pPlot == gDLL->getInterfaceIFace()->getSelectionPlot())
			{
				gDLL->getInterfaceIFace()->setDirty(PlotListButtons_DIRTY_BIT, true);
			}
		}

		if (bRemoveSelected)
		{
			if (IsSelected())
			{
				gDLL->getInterfaceIFace()->removeFromSelectionList(this);
			}
		}
	}
}
*/

int CvUnit::getHotKeyNumber()
{
	return m_iHotKeyNumber;
}


void CvUnit::setHotKeyNumber(int iNewValue)
{
	CvUnit* pLoopUnit;
	int iLoop;

	FAssert(getOwnerINLINE() != NO_PLAYER);

	if (getHotKeyNumber() != iNewValue)
	{
		if (iNewValue != -1)
		{
			for(pLoopUnit = GET_PLAYER(getOwnerINLINE()).firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = GET_PLAYER(getOwnerINLINE()).nextUnit(&iLoop))
			{
				if (pLoopUnit->getHotKeyNumber() == iNewValue)
				{
					pLoopUnit->setHotKeyNumber(-1);
				}
			}
		}

		m_iHotKeyNumber = iNewValue;

		if (IsSelected())
		{
			gDLL->getInterfaceIFace()->setDirty(InfoPane_DIRTY_BIT, true);
		}
	}
}


int CvUnit::getX() const
{
	return m_iX;
}


int CvUnit::getY() const
{
	return m_iY;
}


// Denev 02/2010, lfgr 09/2019: Unofficial Bug Fix (added bPushOutExistingUnit), added bUnitCreation
void CvUnit::setXY(int iX, int iY, bool bGroup, bool bUpdate, bool bShow, bool bCheckPlotVisible,
		bool bPushOutExistingUnit, bool bUnitCreation)
{
	CLLNode<IDInfo>* pUnitNode;
	CvCity* pOldCity;
	CvCity* pNewCity;
	CvCity* pWorkingCity;
	CvUnit* pTransportUnit;
	CvUnit* pLoopUnit;
	CvPlot* pOldPlot;
	CvPlot* pNewPlot;
	CvPlot* pLoopPlot;
	CLinkList<IDInfo> oldUnits;
	ActivityTypes eOldActivityType;
	int iI;

	// OOS!! Temporary for Out-of-Sync madness debugging...
	if (GC.getLogging())
	{
		if (gDLL->getChtLvl() > 0)
		{
			char szOut[1024];
			sprintf(szOut, "Player %d Unit %d (%S's %S) moving from %d:%d to %d:%d\n", getOwnerINLINE(), getID(), GET_PLAYER(getOwnerINLINE()).getName(), getName().GetCString(), getX_INLINE(), getY_INLINE(), iX, iY);
			gDLL->messageControlLog(szOut);
		}
	}

	FAssert(!at(iX, iY));
	FAssert(!isFighting());
	FAssert((iX == INVALID_PLOT_COORD) || (GC.getMapINLINE().plotINLINE(iX, iY)->getX_INLINE() == iX));
	FAssert((iY == INVALID_PLOT_COORD) || (GC.getMapINLINE().plotINLINE(iX, iY)->getY_INLINE() == iY));

	if (getGroup() != NULL)
	{
		eOldActivityType = getGroup()->getActivityType();
	}
	else
	{
		eOldActivityType = NO_ACTIVITY;
	}

	setBlockading(false);

	if (!bGroup || isCargo())
	{
		joinGroup(NULL, true);
		bShow = false;
	}

	pNewPlot = GC.getMapINLINE().plotINLINE(iX, iY);

	if (pNewPlot != NULL)
	{
		pTransportUnit = getTransportUnit();

		if (pTransportUnit != NULL)
		{
			if (!(pTransportUnit->atPlot(pNewPlot)))
			{
				setTransportUnit(NULL);
			}
		}

//>>>>Unofficial Bug Fix: Added by Denev 2010/02/22
		if (bPushOutExistingUnit)
		{
//<<<<Unofficial Bug Fix: End Modify
		if (canFight())
		{
			oldUnits.clear();

			pUnitNode = pNewPlot->headUnitNode();

			while (pUnitNode != NULL)
			{
				oldUnits.insertAtEnd(pUnitNode->m_data);
				pUnitNode = pNewPlot->nextUnitNode(pUnitNode);
			}

			pUnitNode = oldUnits.head();

			while (pUnitNode != NULL)
			{
				pLoopUnit = ::getUnit(pUnitNode->m_data);
				pUnitNode = oldUnits.next(pUnitNode);

				if (pLoopUnit != NULL)
				{
					if (isEnemy(pLoopUnit->getTeam(), pNewPlot) || pLoopUnit->isEnemy(getTeam()))
					{
						if (!pLoopUnit->canCoexistWithEnemyUnit(getTeam()))
						{
							if (NO_UNITCLASS == pLoopUnit->getUnitInfo().getUnitCaptureClassType() && pLoopUnit->canDefend(pNewPlot))
							{

//FfH: Modified by Kael 04/25/2010
//								pLoopUnit->jumpToNearestValidPlot(); // can kill unit
                                if (pLoopUnit->plot() != NULL)
                                {
                                    if (!isInvisible(pLoopUnit->getTeam(), false))
                                    {
                                        pLoopUnit->withdrawlToNearestValidPlot(); // can kill unit
                                    }
                                }
//FfH: End Modify

							}
							else
							{

//FfH Hidden Nationality: Modified by Kael 08/27/2007
//								if (!m_pUnitInfo->isHiddenNationality() && !pLoopUnit->getUnitInfo().isHiddenNationality())
								if (!isHiddenNationality() && !pLoopUnit->isHiddenNationality())
//FfH: End Modify

								{
									GET_TEAM(pLoopUnit->getTeam()).changeWarWeariness(getTeam(), *pNewPlot, GC.defines.iWW_UNIT_CAPTURED);
									GET_TEAM(getTeam()).changeWarWeariness(pLoopUnit->getTeam(), *pNewPlot, GC.defines.iWW_CAPTURED_UNIT);
									GET_TEAM(getTeam()).AI_changeWarSuccess(pLoopUnit->getTeam(), GC.defines.iWAR_SUCCESS_UNIT_CAPTURING);
								}

//FfH: Modified by Kael 12/30/2207
//								if (!isNoCapture())
//								{
//									pLoopUnit->setCapturingPlayer(getOwnerINLINE());
//								}
								if (!isNoCapture() || GC.getUnitInfo((UnitTypes)pLoopUnit->getUnitType()).getEquipmentPromotion() != NO_PROMOTION)
								{
								    if (!pLoopUnit->isHiddenNationality())
								    {
                                        pLoopUnit->setCapturingPlayer(getOwnerINLINE());
                                    }
								}
//FfH: End Modify
								
								logBBAI("    Killing %S -- can't defend, enemy unit moved on it (Unit %d - plot: %d, %d)",
									pLoopUnit->getName().GetCString(), pLoopUnit->getID(), pLoopUnit->getX(), pLoopUnit->getY());
								pLoopUnit->kill(false, getOwnerINLINE());
							}
						}
					}
				}
			}
		}
//>>>>Unofficial Bug Fix: Added by Denev 2010/02/22
		}
//<<<<Unofficial Bug Fix: End Modify

		if (pNewPlot->isGoody(getTeam()))
		{
			GET_PLAYER(getOwnerINLINE()).doGoody(pNewPlot, this);
		}
	}

	pOldPlot = plot();

	if (pOldPlot != NULL)
	{
		pOldPlot->removeUnit(this, bUpdate && !hasCargo());

		pOldPlot->changeAdjacentSight(getTeam(), visibilityRange(), false, this, true);

		pOldPlot->area()->changeUnitsPerPlayer(getOwnerINLINE(), -1);
		//pOldPlot->area()->changePower(getOwnerINLINE(), -(m_pUnitInfo->getPowerValue()));
		pOldPlot->area()->changePower(getOwnerINLINE(), -(getTruePower()));

		if (AI_getUnitAIType() != NO_UNITAI)
		{
			pOldPlot->area()->changeNumAIUnits(getOwnerINLINE(), AI_getUnitAIType(), -1);
		}

		if (isAnimal())
		{
			pOldPlot->area()->changeAnimalsPerPlayer(getOwnerINLINE(), -1);
		}

		if (pOldPlot->getTeam() != getTeam() && (pOldPlot->getTeam() == NO_TEAM || !GET_TEAM(pOldPlot->getTeam()).isVassal(getTeam())))
		{

//FfH: Modified by Kael 04/19/2009
//			GET_PLAYER(getOwnerINLINE()).changeNumOutsideUnits(-1);
            if (getDuration() == 0)
            {
                GET_PLAYER(getOwnerINLINE()).changeNumOutsideUnits(-1);
            }
//FfH: End Modify

		}

		setLastMoveTurn(GC.getGameINLINE().getTurnSlice());

		pOldCity = pOldPlot->getPlotCity();

		if (pOldCity != NULL)
		{
			if (isMilitaryHappiness())
			{
				pOldCity->changeMilitaryHappinessUnits(-1);
			}
		}

		pWorkingCity = pOldPlot->getWorkingCity();

		if (pWorkingCity != NULL)
		{
			if (canSiege(pWorkingCity->getTeam()))
			{
				pWorkingCity->AI_setAssignWorkDirty(true);
			}
		}

		if (pOldPlot->isWater())
		{
			for (iI = 0; iI < NUM_DIRECTION_TYPES; iI++)
			{
				pLoopPlot = plotDirection(pOldPlot->getX_INLINE(), pOldPlot->getY_INLINE(), ((DirectionTypes)iI));

				if (pLoopPlot != NULL)
				{
					if (pLoopPlot->isWater())
					{
						pWorkingCity = pLoopPlot->getWorkingCity();

						if (pWorkingCity != NULL)
						{
							if (canSiege(pWorkingCity->getTeam()))
							{
								pWorkingCity->AI_setAssignWorkDirty(true);
							}
						}
					}
				}
			}
		}

		if (pOldPlot->isActiveVisible(true))
		{
			pOldPlot->updateMinimapColor();
		}

		if (pOldPlot == gDLL->getInterfaceIFace()->getSelectionPlot())
		{
			gDLL->getInterfaceIFace()->verifyPlotListColumn();

			gDLL->getInterfaceIFace()->setDirty(PlotListButtons_DIRTY_BIT, true);
		}
	}

	if (pNewPlot != NULL)
	{
		m_iX = pNewPlot->getX_INLINE();
		m_iY = pNewPlot->getY_INLINE();
	}
	else
	{
		m_iX = INVALID_PLOT_COORD;
		m_iY = INVALID_PLOT_COORD;
	}

	FAssertMsg(plot() == pNewPlot, "plot is expected to equal pNewPlot");

	if (pNewPlot != NULL)
	{
		pNewCity = pNewPlot->getPlotCity();

		if (pNewCity != NULL)
		{
			if (isEnemy(pNewCity->getTeam()) && !canCoexistWithEnemyUnit(pNewCity->getTeam()) && canFight())
			{
				if (isHiddenNationality())
				{
					//pNewCity->kill(true);
					//gDLL->getInterfaceIFace()->addMessage(getID(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_CITYRAZE", MESSAGE_TYPE_MAJOR_EVENT, ARTFILEMGR.getInterfaceArtInfo("WORLDBUILDER_CITY_EDIT")->getPath(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pNewCity->getX_INLINE(), pNewCity->getY_INLINE(), true, true);
					pNewCity->doTask(TASK_RAZE);
				}
				else
				{
					GET_TEAM(getTeam()).changeWarWeariness(pNewCity->getTeam(), *pNewPlot, GC.defines.iWW_CAPTURED_CITY);
	/************************************************************************************************/
	/* BETTER_BTS_AI_MOD                      06/14/09                                jdog5000      */
	/*                                                                                              */
	/* General AI                                                                                   */
	/************************************************************************************************/
	/* original bts code
					GET_TEAM(getTeam()).AI_changeWarSuccess(pNewCity->getTeam(), GC.defines.iWAR_SUCCESS_CITY_CAPTURING);
	*/
					// Double war success if capturing capital city, always a significant blow to enemy
					// pNewCity still points to old city here, hasn't been acquired yet
					//GET_TEAM(getTeam()).AI_changeWarSuccess(pNewCity->getTeam(), (pNewCity->isCapital() ? 2 : 1)*GC.getWAR_SUCCESS_CITY_CAPTURING());
					GET_TEAM(getTeam()).AI_changeWarSuccess(pNewCity->getTeam(), (pNewCity->getPopulation() * 2) + (pNewCity->getNumActiveWorldWonders() * 5));
	/************************************************************************************************/
	/* BETTER_BTS_AI_MOD                       END                                                  */
	/************************************************************************************************/

					PlayerTypes eNewOwner = GET_PLAYER(getOwnerINLINE()).pickConqueredCityOwner(*pNewCity);

					if (NO_PLAYER != eNewOwner)
					{
						GET_PLAYER(eNewOwner).acquireCity(pNewCity, true, false, true); // will delete the pointer
						pNewCity = NULL;
					}
				}
			}
		}

		// Super Forts begin *culture* *text*
		ImprovementTypes eImprovement = pNewPlot->getImprovementType();
		if(GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS) && eImprovement != NO_IMPROVEMENT)
		{
			if(GC.getImprovementInfo(eImprovement).isActsAsCity() && !isNoCapture())
			{
				if(pNewPlot->getOwner() != NO_PLAYER)
				{
					if(isEnemy(pNewPlot->getTeam()) && !canCoexistWithEnemyUnit(pNewPlot->getTeam()) && canFight())
					{
						CvWString szBuffer = gDLL->getText("TXT_KEY_MISC_CITY_CAPTURED_BY", GC.getImprovementInfo(eImprovement).getTextKeyWide(), GET_PLAYER(getOwnerINLINE()).getCivilizationDescriptionKey());
						gDLL->getInterfaceIFace()->addMessage(pNewPlot->getOwner(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_CITYCAPTURED", MESSAGE_TYPE_MAJOR_EVENT, GC.getImprovementInfo(eImprovement).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pNewPlot->getX_INLINE(), pNewPlot->getY_INLINE(), true, true);
						pNewPlot->setOwner(getOwnerINLINE(),true,true);
					}
				}
				else
				{
					pNewPlot->setOwner(getOwnerINLINE(),true,true);
				}
			}
		}
		// Super Forts end

		//update facing direction
		if(pOldPlot != NULL)
		{
			DirectionTypes newDirection = estimateDirection(pOldPlot, pNewPlot);
			if(newDirection != NO_DIRECTION)
				m_eFacingDirection = newDirection;
		}

		//update cargo mission animations
		if (isCargo())
		{
			if (eOldActivityType != ACTIVITY_MISSION)
			{
				getGroup()->setActivityType(eOldActivityType);
			}
		}

		setFortifyTurns(0);

		pNewPlot->changeAdjacentSight(getTeam(), visibilityRange(), true, this, true); // needs to be here so that the square is considered visible when we move into it...

		pNewPlot->addUnit(this, bUpdate && !hasCargo());

		pNewPlot->area()->changeUnitsPerPlayer(getOwnerINLINE(), 1);
		//pNewPlot->area()->changePower(getOwnerINLINE(), m_pUnitInfo->getPowerValue());
		pNewPlot->area()->changePower(getOwnerINLINE(), getTruePower());

		if (AI_getUnitAIType() != NO_UNITAI)
		{
			pNewPlot->area()->changeNumAIUnits(getOwnerINLINE(), AI_getUnitAIType(), 1);
		}

		if (isAnimal())
		{
			pNewPlot->area()->changeAnimalsPerPlayer(getOwnerINLINE(), 1);
		}

		if (pNewPlot->getTeam() != getTeam() && (pNewPlot->getTeam() == NO_TEAM || !GET_TEAM(pNewPlot->getTeam()).isVassal(getTeam())))
		{

//FfH: Modified by Kael 04/19/2009
//			GET_PLAYER(getOwnerINLINE()).changeNumOutsideUnits(1);
            if (getDuration() == 0)
            {
                GET_PLAYER(getOwnerINLINE()).changeNumOutsideUnits(1);
            }
//FfH: End Modify

		}

		if (shouldLoadOnMove(pNewPlot))
		{
			load();
		}

		if (!getUnitInfo().isObject() && !isHiddenNationality()) // Tholal AI - Objects and HN units shouldnt trigger contacts
		{
			for (iI = 0; iI < MAX_CIV_TEAMS; iI++)
			{
				if (GET_TEAM((TeamTypes)iI).isAlive())
				{
					if (!isInvisible(((TeamTypes)iI), false))
					{
						if (pNewPlot->isVisible((TeamTypes)iI, false))
						{
							GET_TEAM((TeamTypes)iI).meet(getTeam(), true);
						}
					}
				}
			}
		}

		pNewCity = pNewPlot->getPlotCity();

		if (pNewCity != NULL)
		{
			if (isMilitaryHappiness())
			{
				pNewCity->changeMilitaryHappinessUnits(1);
			}
		}

		pWorkingCity = pNewPlot->getWorkingCity();

		if (pWorkingCity != NULL)
		{
			if (canSiege(pWorkingCity->getTeam()))
			{
				pWorkingCity->verifyWorkingPlot(pWorkingCity->getCityPlotIndex(pNewPlot));
			}
		}

		if (pNewPlot->isWater())
		{
			for (iI = 0; iI < NUM_DIRECTION_TYPES; iI++)
			{
				pLoopPlot = plotDirection(pNewPlot->getX_INLINE(), pNewPlot->getY_INLINE(), ((DirectionTypes)iI));

				if (pLoopPlot != NULL)
				{
					if (pLoopPlot->isWater())
					{
						pWorkingCity = pLoopPlot->getWorkingCity();

						if (pWorkingCity != NULL)
						{
							if (canSiege(pWorkingCity->getTeam()))
							{
								pWorkingCity->verifyWorkingPlot(pWorkingCity->getCityPlotIndex(pLoopPlot));
							}
						}
					}
				}
			}
		}

		if (pNewPlot->isActiveVisible(true))
		{
			pNewPlot->updateMinimapColor();
		}

		if (GC.IsGraphicsInitialized())
		{
			//override bShow if check plot visible
			if(bCheckPlotVisible && pNewPlot->isVisibleToWatchingHuman())
				bShow = true;

			if (bShow)
			{
				QueueMove(pNewPlot);
			}
			else
			{
				SetPosition(pNewPlot);
			}
		}

		if (pNewPlot == gDLL->getInterfaceIFace()->getSelectionPlot())
		{
			gDLL->getInterfaceIFace()->verifyPlotListColumn();

			gDLL->getInterfaceIFace()->setDirty(PlotListButtons_DIRTY_BIT, true);
		}
	}

	if (pOldPlot != NULL)
	{
		if (hasCargo())
		{
			pUnitNode = pOldPlot->headUnitNode();

			while (pUnitNode != NULL)
			{
				pLoopUnit = ::getUnit(pUnitNode->m_data);
				pUnitNode = pOldPlot->nextUnitNode(pUnitNode);

				if (pLoopUnit->getTransportUnit() == this)
				{
					pLoopUnit->setXY(iX, iY, bGroup, false);
				}
			}
		}
	}

	if (bUpdate && hasCargo())
	{
		if (pOldPlot != NULL)
		{
			pOldPlot->updateCenterUnit();
			pOldPlot->setFlagDirty(true);
		}

		if (pNewPlot != NULL)
		{
			pNewPlot->updateCenterUnit();
			pNewPlot->setFlagDirty(true);
		}
	}

//FfH Units: Added by Kael 11/10/2008
	if (pNewPlot != NULL)
	{
        int iImprovement = pNewPlot->getImprovementType();
        if (iImprovement != NO_IMPROVEMENT)
        {
			CvImprovementInfo& kImprovementInfo = GC.getImprovementInfo((ImprovementTypes)iImprovement);

            if (kImprovementInfo.getSpawnUnitType() != NO_UNIT)
            {
				bool bAnimalLair = false;

				if (GC.getUnitInfo((UnitTypes)kImprovementInfo.getSpawnUnitType()).isAnimal())
				{
					bAnimalLair = true;
				}

                if (kImprovementInfo.isPermanent() == false)
                {
                    if (atWar(getTeam(), GET_PLAYER(BARBARIAN_PLAYER).getTeam()) || (bAnimalLair && !isBarbarian()))
                    {
                        if (isHuman())
                        {
                            gDLL->getInterfaceIFace()->addMessage(getOwner(), false, GC.defines.iEVENT_MESSAGE_TIME, gDLL->getText("TXT_KEY_MESSAGE_LAIR_DESTROYED"), "AS2D_CITYRAZE", MESSAGE_TYPE_MAJOR_EVENT, GC.getImprovementInfo((ImprovementTypes)iImprovement).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pNewPlot->getX(), pNewPlot->getY(), true, true);
                        }
                        pNewPlot->setImprovementType(NO_IMPROVEMENT);
                    }
                }
            }
        }
        iImprovement = pNewPlot->getImprovementType(); // rechecking because the previous function may have deleted the improvement
        if (iImprovement != NO_IMPROVEMENT)
        {
            if (!CvString(GC.getImprovementInfo((ImprovementTypes)iImprovement).getPythonOnMove()).empty())
            {
                if (pNewPlot->isPythonActive())
                {
                    CyUnit* pyUnit = new CyUnit(this);
                    CyPlot* pyPlot = new CyPlot(pNewPlot);
                    CyArgsList argsList;
                    argsList.add(gDLL->getPythonIFace()->makePythonObject(pyUnit));	// pass in unit class
                    argsList.add(gDLL->getPythonIFace()->makePythonObject(pyPlot));	// pass in plot class
                    argsList.add(iImprovement);//the improvement #
                    gDLL->getPythonIFace()->callFunction(PYSpellModule, "onMove", argsList.makeFunctionArgs()); //, &lResult
                    delete pyUnit; // python fxn must not hold on to this pointer
                    delete pyPlot;	// python fxn must not hold on to this pointer
                }
            }
        }
        for (int iI = 0; iI < NUM_DIRECTION_TYPES; iI++)
        {
            pLoopPlot = plotDirection(pNewPlot->getX_INLINE(), pNewPlot->getY_INLINE(), ((DirectionTypes)iI));
            if (pLoopPlot != NULL)
            {
                if (pLoopPlot->getImprovementType() != NO_IMPROVEMENT)
                {
                    if (!CvString(GC.getImprovementInfo((ImprovementTypes)pLoopPlot->getImprovementType()).getPythonAtRange()).empty())
                    {
                        if (pLoopPlot->isPythonActive())
                        {
                            CyUnit* pyUnit = new CyUnit(this);
                            CyPlot* pyPlot = new CyPlot(pLoopPlot);
                            CyArgsList argsList;
                            argsList.add(gDLL->getPythonIFace()->makePythonObject(pyUnit));	// pass in unit class
                            argsList.add(gDLL->getPythonIFace()->makePythonObject(pyPlot));	// pass in plot class
                            argsList.add(pLoopPlot->getImprovementType());
                            gDLL->getPythonIFace()->callFunction(PYSpellModule, "atRange", argsList.makeFunctionArgs()); //, &lResult
                            delete pyUnit; // python fxn must not hold on to this pointer
                            delete pyPlot;	// python fxn must not hold on to this pointer
                        }
                    }
                }
            }
        }
        if (pNewPlot->getFeatureType() != NO_FEATURE)
        {
            if (!CvString(GC.getFeatureInfo((FeatureTypes)pNewPlot->getFeatureType()).getPythonOnMove()).empty())
            {
                CyUnit* pyUnit = new CyUnit(this);
                CyPlot* pyPlot = new CyPlot(pNewPlot);
                CyArgsList argsList;
                argsList.add(gDLL->getPythonIFace()->makePythonObject(pyUnit));	// pass in unit class
                argsList.add(gDLL->getPythonIFace()->makePythonObject(pyPlot));	// pass in plot class
                argsList.add(pNewPlot->getFeatureType());
				// lfgr 09/2019: Add bUnitCreation, to indicated whether unit was just created
				argsList.add(bUnitCreation);
                gDLL->getPythonIFace()->callFunction(PYSpellModule, "onMoveFeature", argsList.makeFunctionArgs()); //, &lResult
                delete pyUnit; // python fxn must not hold on to this pointer
                delete pyPlot;	// python fxn must not hold on to this pointer
            }
        }
        if (pNewPlot->isCity() && m_pUnitInfo->getWeaponTier() > 0)
        {
            if (getOwner() == pNewPlot->getOwner())
            {
                setWeapons();
            }
        }
        if (m_pUnitInfo->isAutoRaze())
        {
            if (pNewPlot->isOwned())
            {
                if (pNewPlot->getImprovementType() != NO_IMPROVEMENT)
                {
                    if (!GC.getImprovementInfo((ImprovementTypes)pNewPlot->getImprovementType()).isPermanent())
                    {
                        if (atWar(getTeam(), GET_PLAYER(pNewPlot->getOwner()).getTeam()))
                        {
                            pNewPlot->setImprovementType(NO_IMPROVEMENT);
                        }
                    }
                }
            }
            pNewPlot->setFeatureType(NO_FEATURE, -1);
        }
	}
//FfH: End Add

	FAssert(pOldPlot != pNewPlot);
	//GET_PLAYER(getOwnerINLINE()).updateGroupCycle(this);
	// K-Mod. Only update the group cycle here if we are placing this unit on the map for the first time.
	if (!pOldPlot)
		GET_PLAYER(getOwnerINLINE()).updateGroupCycle(this);
	// K-Mod end

	setInfoBarDirty(true);

	if (IsSelected())
	{
		if (isFound())
		{
			gDLL->getInterfaceIFace()->setDirty(GlobeLayer_DIRTY_BIT, true);
			gDLL->getEngineIFace()->updateFoundingBorder();
		}

		gDLL->getInterfaceIFace()->setDirty(ColoredPlots_DIRTY_BIT, true);
	}

	//update glow
	if (pNewPlot != NULL)
	{
		gDLL->getEntityIFace()->updateEnemyGlow(getUnitEntity());
	}

	// report event to Python, along with some other key state

//FfH: Modified by Kael 10/15/2008
//	CvEventReporter::getInstance().unitSetXY(pNewPlot, this);
	if(GC.getUSE_ON_UNIT_MOVE_CALLBACK())
	{
		CvEventReporter::getInstance().unitSetXY(pNewPlot, this);
	}
//FfH: End Modify

}


bool CvUnit::at(int iX, int iY) const
{
	return((getX_INLINE() == iX) && (getY_INLINE() == iY));
}


bool CvUnit::atPlot(const CvPlot* pPlot) const
{
	return (plot() == pPlot);
}


CvPlot* CvUnit::plot() const
{
	return GC.getMapINLINE().plotSorenINLINE(getX_INLINE(), getY_INLINE());
}


int CvUnit::getArea() const
{
	return plot()->getArea();
}


CvArea* CvUnit::area() const
{
	return plot()->area();
}


bool CvUnit::onMap() const
{
	return (plot() != NULL);
}


int CvUnit::getLastMoveTurn() const
{
	return m_iLastMoveTurn;
}


void CvUnit::setLastMoveTurn(int iNewValue)
{
	m_iLastMoveTurn = iNewValue;
	FAssert(getLastMoveTurn() >= 0);
}


CvPlot* CvUnit::getReconPlot() const
{
	return GC.getMapINLINE().plotSorenINLINE(m_iReconX, m_iReconY);
}


void CvUnit::setReconPlot(CvPlot* pNewValue)
{
	CvPlot* pOldPlot;

	pOldPlot = getReconPlot();

	if (pOldPlot != pNewValue)
	{
		if (pOldPlot != NULL)
		{
			pOldPlot->changeAdjacentSight(getTeam(), GC.defines.iRECON_VISIBILITY_RANGE, false, this, true);
			pOldPlot->changeReconCount(-1); // changeAdjacentSight() tests for getReconCount()
		}

		if (pNewValue == NULL)
		{
			m_iReconX = INVALID_PLOT_COORD;
			m_iReconY = INVALID_PLOT_COORD;
		}
		else
		{
			m_iReconX = pNewValue->getX_INLINE();
			m_iReconY = pNewValue->getY_INLINE();

			pNewValue->changeReconCount(1); // changeAdjacentSight() tests for getReconCount()
			pNewValue->changeAdjacentSight(getTeam(), GC.defines.iRECON_VISIBILITY_RANGE, true, this, true);
		}
	}
}


int CvUnit::getGameTurnCreated() const
{
	return m_iGameTurnCreated;
}


void CvUnit::setGameTurnCreated(int iNewValue)
{
	m_iGameTurnCreated = iNewValue;
	FAssert(getGameTurnCreated() >= 0);
}


int CvUnit::getDamage() const
{
	return m_iDamage;
}


void CvUnit::setDamage(int iNewValue, PlayerTypes ePlayer, bool bNotifyEntity)
{
	int iOldValue;

	iOldValue = getDamage();

	m_iDamage = range(iNewValue, 0, maxHitPoints());

	FAssertMsg(currHitPoints() >= 0, "currHitPoints() is expected to be non-negative (invalid Index)");

	if (iOldValue != getDamage())
	{
		if (GC.getGameINLINE().isFinalInitialized() && bNotifyEntity)
		{
			NotifyEntity(MISSION_DAMAGE);
		}

		setInfoBarDirty(true);

		if (IsSelected())
		{
			gDLL->getInterfaceIFace()->setDirty(InfoPane_DIRTY_BIT, true);
		}

		if (plot() == gDLL->getInterfaceIFace()->getSelectionPlot())
		{
			gDLL->getInterfaceIFace()->setDirty(PlotListButtons_DIRTY_BIT, true);
		}
	}

	if (isDead())
	{
		logBBAI("    Killing %S (delayed) -- received deadly damage (Unit %d - plot: %d, %d)",
				getName().GetCString(), getID(), getX(), getY());
		kill(true, ePlayer);
	}
}


void CvUnit::changeDamage(int iChange, PlayerTypes ePlayer)
{
	setDamage((getDamage() + iChange), ePlayer);
}


int CvUnit::getMoves() const
{
	return m_iMoves;
}


void CvUnit::setMoves(int iNewValue)
{
	CvPlot* pPlot;

	if (getMoves() != iNewValue)
	{
		pPlot = plot();

		m_iMoves = iNewValue;

		FAssert(getMoves() >= 0);

		if (getTeam() == GC.getGameINLINE().getActiveTeam())
		{
			if (pPlot != NULL)
			{
				pPlot->setFlagDirty(true);
			}
		}

		if (IsSelected())
		{
			gDLL->getFAStarIFace()->ForceReset(&GC.getInterfacePathFinder());

			gDLL->getInterfaceIFace()->setDirty(InfoPane_DIRTY_BIT, true);
		}

		if (pPlot == gDLL->getInterfaceIFace()->getSelectionPlot())
		{
			gDLL->getInterfaceIFace()->setDirty(PlotListButtons_DIRTY_BIT, true);
		}
	}
}


void CvUnit::changeMoves(int iChange)
{
	setMoves(getMoves() + iChange);
}


void CvUnit::finishMoves()
{
	setMoves(maxMoves());
}


int CvUnit::getExperience() const
{
	return m_iExperience;
}

void CvUnit::setExperience(int iNewValue, int iMax)
{
	if ((getExperience() != iNewValue) && (getExperience() < ((iMax == -1) ? MAX_INT : iMax)))
	{
		m_iExperience = std::min(((iMax == -1) ? MAX_INT : iMax), iNewValue);
		FAssert(getExperience() >= 0);

		if (IsSelected())
		{
			gDLL->getInterfaceIFace()->setDirty(InfoPane_DIRTY_BIT, true);
		}
	}
}

void CvUnit::changeExperience(int iChange, int iMax, bool bFromCombat, bool bInBorders, bool bUpdateGlobal)
{
	// dont bother changing experience if the unit cant use it
	bool bHero = false;
	for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
	{
		if (isHasPromotion((PromotionTypes)iI))
		{
		    if (GC.getPromotionInfo((PromotionTypes)iI).getFreeXPPerTurn() != 0)
		    {
				bHero = true;
				break;
			}
		}
	}

	if (getUnitCombatType() == NO_UNITCOMBAT && !bHero)
	{
		return;
	}

	int iUnitExperience = iChange;

	if (bFromCombat)
	{
		CvPlayer& kPlayer = GET_PLAYER(getOwnerINLINE());

		int iCombatExperienceMod = 100 + kPlayer.getGreatGeneralRateModifier();

		if (bInBorders)
		{
			iCombatExperienceMod += kPlayer.getDomesticGreatGeneralRateModifier() + kPlayer.getExpInBorderModifier();
			iUnitExperience += (iChange * kPlayer.getExpInBorderModifier()) / 100;
		}

		// Great General experience - limit this to the Advanced Tactics option
		if (bUpdateGlobal && GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS))
		//if (bUpdateGlobal)
		{
			kPlayer.changeCombatExperience((iChange * iCombatExperienceMod) / 100);
		}

		if (getExperiencePercent() != 0)
		{
			iUnitExperience *= std::max(0, 100 + getExperiencePercent());
			iUnitExperience /= 100;
		}

//FfH: Added by Kael 05/17/2008
        if (GC.getGameINLINE().isOption(GAMEOPTION_SLOWER_XP))
        {
            iUnitExperience += 1;
            iUnitExperience /= 2;
        }
//FfH: End Add

	}

	setExperience((getExperience() + iUnitExperience), iMax);
}

int CvUnit::getLevel() const
{
	return m_iLevel;
}

void CvUnit::setLevel(int iNewValue)
{
	if (getLevel() != iNewValue)
	{
		// MORE_ASSERTS 07/2019 lfgr: Check that level is positive
		FAssertMsg(iNewValue > 0, "New level must be greater than zero");
		// MORE_ASSERTS end

		// MNAI - True Power calculations
		int iNetPowerChange = iNewValue - getLevel();
		GET_PLAYER(getOwnerINLINE()).changePower(iNetPowerChange);
		area()->changePower(getOwnerINLINE(), iNetPowerChange);
		// MNAI End

		m_iLevel = iNewValue;
		FAssert(getLevel() >= 0);

		if (getLevel() > GET_PLAYER(getOwnerINLINE()).getHighestUnitLevel())
		{
			GET_PLAYER(getOwnerINLINE()).setHighestUnitLevel(getLevel());
		}

		if (IsSelected())
		{
			gDLL->getInterfaceIFace()->setDirty(InfoPane_DIRTY_BIT, true);
		}
	}
}

void CvUnit::changeLevel(int iChange)
{
	setLevel(getLevel() + iChange);
}

int CvUnit::getCargo() const
{
	return m_iCargo;
}

void CvUnit::changeCargo(int iChange)
{
	m_iCargo += iChange;
	FAssert(getCargo() >= 0);
}

void CvUnit::getCargoUnits(std::vector<CvUnit*>& aUnits) const
{
	aUnits.clear();

	if (hasCargo())
	{
		CvPlot* pPlot = plot();
		CLLNode<IDInfo>* pUnitNode = pPlot->headUnitNode();
		while (pUnitNode != NULL)
		{
			CvUnit* pLoopUnit = ::getUnit(pUnitNode->m_data);
			pUnitNode = pPlot->nextUnitNode(pUnitNode);
			if (pLoopUnit->getTransportUnit() == this)
			{
				aUnits.push_back(pLoopUnit);
			}
		}
	}

	// lfgr 04/2021: Commented out
	//FAssertMsg(getCargo() == aUnits.size(), "(May occur erroneously when moving a ship containing some unit that can see some invisible type)");
}

CvPlot* CvUnit::getAttackPlot() const
{
	return GC.getMapINLINE().plotSorenINLINE(m_iAttackPlotX, m_iAttackPlotY);
}


void CvUnit::setAttackPlot(const CvPlot* pNewValue, bool bAirCombat)
{
	if (getAttackPlot() != pNewValue)
	{
		if (pNewValue != NULL)
		{
			m_iAttackPlotX = pNewValue->getX_INLINE();
			m_iAttackPlotY = pNewValue->getY_INLINE();
		}
		else
		{
			m_iAttackPlotX = INVALID_PLOT_COORD;
			m_iAttackPlotY = INVALID_PLOT_COORD;
		}
	}

	m_bAirCombat = bAirCombat;
}

bool CvUnit::isAirCombat() const
{
	return m_bAirCombat;
}

int CvUnit::getCombatTimer() const
{
	return m_iCombatTimer;
}

void CvUnit::setCombatTimer(int iNewValue)
{
	m_iCombatTimer = iNewValue;
	FAssert(getCombatTimer() >= 0);
}

void CvUnit::changeCombatTimer(int iChange)
{
	setCombatTimer(getCombatTimer() + iChange);
}

int CvUnit::getCombatFirstStrikes() const
{
	return m_iCombatFirstStrikes;
}

void CvUnit::setCombatFirstStrikes(int iNewValue)
{
	m_iCombatFirstStrikes = iNewValue;
	FAssert(getCombatFirstStrikes() >= 0);
}

void CvUnit::changeCombatFirstStrikes(int iChange)
{
	setCombatFirstStrikes(getCombatFirstStrikes() + iChange);
}

int CvUnit::getFortifyTurns() const
{
	return m_iFortifyTurns;
}

void CvUnit::setFortifyTurns(int iNewValue)
{
	iNewValue = range(iNewValue, 0, GC.defines.iMAX_FORTIFY_TURNS);

	if (iNewValue != getFortifyTurns())
	{
		m_iFortifyTurns = iNewValue;
		setInfoBarDirty(true);
	}
}

void CvUnit::changeFortifyTurns(int iChange)
{
	setFortifyTurns(getFortifyTurns() + iChange);
}

int CvUnit::getBlitzCount() const
{
	return m_iBlitzCount;
}

bool CvUnit::isBlitz() const
{
	return (getBlitzCount() > 0);
}

void CvUnit::changeBlitzCount(int iChange)
{
	m_iBlitzCount += iChange;
	FAssert(getBlitzCount() >= 0);
}

int CvUnit::getAmphibCount() const
{
	return m_iAmphibCount;
}

bool CvUnit::isAmphib() const
{
	return (getAmphibCount() > 0);
}

void CvUnit::changeAmphibCount(int iChange)
{
	m_iAmphibCount += iChange;
	FAssert(getAmphibCount() >= 0);
}

int CvUnit::getRiverCount() const
{
	return m_iRiverCount;
}

bool CvUnit::isRiver() const
{
	return (getRiverCount() > 0);
}

void CvUnit::changeRiverCount(int iChange)
{
	m_iRiverCount += iChange;
	FAssert(getRiverCount() >= 0);
}

int CvUnit::getEnemyRouteCount() const
{
	return m_iEnemyRouteCount;
}

bool CvUnit::isEnemyRoute() const
{
	return (getEnemyRouteCount() > 0);
}

void CvUnit::changeEnemyRouteCount(int iChange)
{
	m_iEnemyRouteCount += iChange;
	FAssert(getEnemyRouteCount() >= 0);
}

int CvUnit::getAlwaysHealCount() const
{
	return m_iAlwaysHealCount;
}

bool CvUnit::isAlwaysHeal() const
{
	return (getAlwaysHealCount() > 0);
}

void CvUnit::changeAlwaysHealCount(int iChange)
{
	m_iAlwaysHealCount += iChange;
	FAssert(getAlwaysHealCount() >= 0);
}

int CvUnit::getHillsDoubleMoveCount() const
{
	return m_iHillsDoubleMoveCount;
}

bool CvUnit::isHillsDoubleMove() const
{
	return (getHillsDoubleMoveCount() > 0);
}

void CvUnit::changeHillsDoubleMoveCount(int iChange)
{
	m_iHillsDoubleMoveCount += iChange;
	FAssert(getHillsDoubleMoveCount() >= 0);
}

int CvUnit::getImmuneToFirstStrikesCount() const
{
	return m_iImmuneToFirstStrikesCount;
}

void CvUnit::changeImmuneToFirstStrikesCount(int iChange)
{
	m_iImmuneToFirstStrikesCount += iChange;
	FAssert(getImmuneToFirstStrikesCount() >= 0);
}


int CvUnit::getExtraVisibilityRange() const
{
	return m_iExtraVisibilityRange;
}

void CvUnit::changeExtraVisibilityRange(int iChange)
{
	if (iChange != 0)
	{
		plot()->changeAdjacentSight(getTeam(), visibilityRange(), false, this, true);

		m_iExtraVisibilityRange += iChange;
//		FAssert(getExtraVisibilityRange() >= 0);	some promotions can reduce visibility modified Sephi 0.41k

		plot()->changeAdjacentSight(getTeam(), visibilityRange(), true, this, true);
	}
}

int CvUnit::getExtraMoves() const
{
	return m_iExtraMoves;
}


void CvUnit::changeExtraMoves(int iChange)
{
	m_iExtraMoves += iChange;
//	FAssert(getExtraMoves() >= 0); mutations can make this negative modified Sephi 0.41k
}


int CvUnit::getExtraMoveDiscount() const
{
	return m_iExtraMoveDiscount;
}


void CvUnit::changeExtraMoveDiscount(int iChange)
{
	m_iExtraMoveDiscount += iChange;
//	FAssert(getExtraMoveDiscount() >= 0); //mutate can give negative value Sephi 0.41k
}

int CvUnit::getExtraAirRange() const
{
	return m_iExtraAirRange;
}

void CvUnit::changeExtraAirRange(int iChange)
{
	m_iExtraAirRange += iChange;
}

int CvUnit::getExtraIntercept() const
{
	return m_iExtraIntercept;
}

void CvUnit::changeExtraIntercept(int iChange)
{
	m_iExtraIntercept += iChange;
}

int CvUnit::getExtraEvasion() const
{
	return m_iExtraEvasion;
}

void CvUnit::changeExtraEvasion(int iChange)
{
	m_iExtraEvasion += iChange;
}

int CvUnit::getExtraFirstStrikes() const
{
	return m_iExtraFirstStrikes;
}

void CvUnit::changeExtraFirstStrikes(int iChange)
{
	m_iExtraFirstStrikes += iChange;
	FAssert(getExtraFirstStrikes() >= 0);
}

int CvUnit::getExtraChanceFirstStrikes() const
{
	return m_iExtraChanceFirstStrikes;
}

void CvUnit::changeExtraChanceFirstStrikes(int iChange)
{
	m_iExtraChanceFirstStrikes += iChange;
	FAssert(getExtraChanceFirstStrikes() >= 0);
}


int CvUnit::getExtraWithdrawal() const
{
	return m_iExtraWithdrawal;
}


void CvUnit::changeExtraWithdrawal(int iChange)
{
	m_iExtraWithdrawal += iChange;

	// make sure we don't end up with a negative withdrawal rate due to promotions
	if (m_iExtraWithdrawal < 0)
	{
		m_iExtraWithdrawal = 0;
	}

	FAssert(getExtraWithdrawal() >= 0);
}

int CvUnit::getExtraCollateralDamage() const
{
	return m_iExtraCollateralDamage;
}

void CvUnit::changeExtraCollateralDamage(int iChange)
{
	m_iExtraCollateralDamage += iChange;
	FAssert(getExtraCollateralDamage() >= 0);
}

int CvUnit::getExtraBombardRate() const
{
	return m_iExtraBombardRate;
}

void CvUnit::changeExtraBombardRate(int iChange)
{
	m_iExtraBombardRate += iChange;
	FAssert(getExtraBombardRate() >= 0);
}

int CvUnit::getExtraEnemyHeal() const
{
	return m_iExtraEnemyHeal;
}

void CvUnit::changeExtraEnemyHeal(int iChange)
{
	m_iExtraEnemyHeal += iChange;
//	FAssert(getExtraEnemyHeal() >= 0); Modified by Kael 11/13/2009 0.41k
}

int CvUnit::getExtraNeutralHeal() const
{
	return m_iExtraNeutralHeal;
}

void CvUnit::changeExtraNeutralHeal(int iChange)
{
	m_iExtraNeutralHeal += iChange;
//	FAssert(getExtraNeutralHeal() >= 0); Modified by Kael 11/13/2009 0.41k
}

int CvUnit::getExtraFriendlyHeal() const
{
	return m_iExtraFriendlyHeal;
}


void CvUnit::changeExtraFriendlyHeal(int iChange)
{
	m_iExtraFriendlyHeal += iChange;
//	FAssert(getExtraFriendlyHeal() >= 0); Modified by Kael 0.41k
}

int CvUnit::getSameTileHeal() const
{
	return m_iSameTileHeal;
}

void CvUnit::changeSameTileHeal(int iChange)
{
	m_iSameTileHeal += iChange;
	FAssert(getSameTileHeal() >= 0);
}

int CvUnit::getAdjacentTileHeal() const
{
	return m_iAdjacentTileHeal;
}

void CvUnit::changeAdjacentTileHeal(int iChange)
{
	m_iAdjacentTileHeal += iChange;
	FAssert(getAdjacentTileHeal() >= 0);
}

int CvUnit::getExtraCombatPercent() const
{

//FfH: Modified by Kael 10/26/2007
//	return m_iExtraCombatPercent;
	int i = m_iExtraCombatPercent;
    if (plot()->getOwnerINLINE() == getOwnerINLINE())
    {
        i += getCombatPercentInBorders();
    }
	return i;
//FfH: End Modify

}

void CvUnit::changeExtraCombatPercent(int iChange)
{
	if (iChange != 0)
	{
		m_iExtraCombatPercent += iChange;

		setInfoBarDirty(true);
	}
}

int CvUnit::getExtraCityAttackPercent() const
{
	return m_iExtraCityAttackPercent;
}

void CvUnit::changeExtraCityAttackPercent(int iChange)
{
	if (iChange != 0)
	{
		m_iExtraCityAttackPercent += iChange;

		setInfoBarDirty(true);
	}
}

int CvUnit::getExtraCityDefensePercent() const
{
	return m_iExtraCityDefensePercent;
}

void CvUnit::changeExtraCityDefensePercent(int iChange)
{
	if (iChange != 0)
	{
		m_iExtraCityDefensePercent += iChange;

		setInfoBarDirty(true);
	}
}

int CvUnit::getExtraHillsAttackPercent() const
{
	return m_iExtraHillsAttackPercent;
}

void CvUnit::changeExtraHillsAttackPercent(int iChange)
{
	if (iChange != 0)
	{
		m_iExtraHillsAttackPercent += iChange;

		setInfoBarDirty(true);
	}
}

int CvUnit::getExtraHillsDefensePercent() const
{
	return m_iExtraHillsDefensePercent;
}

void CvUnit::changeExtraHillsDefensePercent(int iChange)
{
	if (iChange != 0)
	{
		m_iExtraHillsDefensePercent += iChange;

		setInfoBarDirty(true);
	}
}

int CvUnit::getRevoltProtection() const
{
	return m_iRevoltProtection;
}

void CvUnit::changeRevoltProtection(int iChange)
{
	if (iChange != 0)
	{
		m_iRevoltProtection += iChange;

		setInfoBarDirty(true);
	}
}

int CvUnit::getCollateralDamageProtection() const
{
	return m_iCollateralDamageProtection;
}

void CvUnit::changeCollateralDamageProtection(int iChange)
{
	if (iChange != 0)
	{
		m_iCollateralDamageProtection += iChange;

		setInfoBarDirty(true);
	}
}

int CvUnit::getPillageChange() const
{
	return m_iPillageChange;
}

void CvUnit::changePillageChange(int iChange)
{
	if (iChange != 0)
	{
		m_iPillageChange += iChange;

		setInfoBarDirty(true);
	}
}

int CvUnit::getUpgradeDiscount() const
{
	return m_iUpgradeDiscount;
}

void CvUnit::changeUpgradeDiscount(int iChange)
{
	if (iChange != 0)
	{
		m_iUpgradeDiscount += iChange;

		setInfoBarDirty(true);
	}
}

int CvUnit::getExperiencePercent() const
{
	return m_iExperiencePercent;
}

void CvUnit::changeExperiencePercent(int iChange)
{
	if (iChange != 0)
	{
		m_iExperiencePercent += iChange;

		setInfoBarDirty(true);
	}
}

int CvUnit::getKamikazePercent() const
{
	return m_iKamikazePercent;
}

void CvUnit::changeKamikazePercent(int iChange)
{
	if (iChange != 0)
	{
		m_iKamikazePercent += iChange;

		setInfoBarDirty(true);
	}
}

DirectionTypes CvUnit::getFacingDirection(bool checkLineOfSightProperty) const
{
	if (checkLineOfSightProperty)
	{
		if (m_pUnitInfo->isLineOfSight())
		{
			return m_eFacingDirection; //only look in facing direction
		}
		else
		{
			return NO_DIRECTION; //look in all directions
		}
	}
	else
	{
		return m_eFacingDirection;
	}
}

void CvUnit::setFacingDirection(DirectionTypes eFacingDirection)
{
	if (eFacingDirection != m_eFacingDirection)
	{
		if (m_pUnitInfo->isLineOfSight())
		{
			//remove old fog
			plot()->changeAdjacentSight(getTeam(), visibilityRange(), false, this, true);

			//change direction
			m_eFacingDirection = eFacingDirection;

			//clear new fog
			plot()->changeAdjacentSight(getTeam(), visibilityRange(), true, this, true);

			gDLL->getInterfaceIFace()->setDirty(ColoredPlots_DIRTY_BIT, true);
		}
		else
		{
			m_eFacingDirection = eFacingDirection;
		}

		//update formation
		NotifyEntity(NO_MISSION);
	}
}

void CvUnit::rotateFacingDirectionClockwise()
{
	//change direction
	DirectionTypes eNewDirection = (DirectionTypes) ((m_eFacingDirection + 1) % NUM_DIRECTION_TYPES);
	setFacingDirection(eNewDirection);
}

void CvUnit::rotateFacingDirectionCounterClockwise()
{
	//change direction
	DirectionTypes eNewDirection = (DirectionTypes) ((m_eFacingDirection + NUM_DIRECTION_TYPES - 1) % NUM_DIRECTION_TYPES);
	setFacingDirection(eNewDirection);
}

int CvUnit::getImmobileTimer() const
{

//FfH: Added by Kael 09/15/2008
    if (isHeld())
    {
        return 999;
    }
//FfH: End Add

	return m_iImmobileTimer;
}

void CvUnit::setImmobileTimer(int iNewValue)
{

//FfH: Modified by Kael 09/15/2008
//	if (iNewValue != getImmobileTimer())
//	{
//		m_iImmobileTimer = iNewValue;
//		setInfoBarDirty(true);
	if (iNewValue != getImmobileTimer() && !isHeld())
	{
		m_iImmobileTimer = iNewValue;
		setInfoBarDirty(true);
        if (getImmobileTimer() == 0)
        {
            if (getDelayedSpell() != NO_SPELL)
            {
                cast(getDelayedSpell());
            }
        }
//FfH: End Modify

	}
}

void CvUnit::changeImmobileTimer(int iChange)
{
	if (iChange != 0)
	{
		setImmobileTimer(std::max(0, getImmobileTimer() + iChange));
	}
}

bool CvUnit::isMadeAttack() const
{
	return m_bMadeAttack;
}


void CvUnit::setMadeAttack(bool bNewValue)
{
	m_bMadeAttack = bNewValue;
}


bool CvUnit::isMadeInterception() const
{
	return m_bMadeInterception;
}


void CvUnit::setMadeInterception(bool bNewValue)
{
	m_bMadeInterception = bNewValue;
}


bool CvUnit::isPromotionReady() const
{
// lfgr 04/2014 bugfix
// Commented out: now handled in testPromotionReady()
/*
	//FfH - Free Promotions (Kael 08/04/2007)
    if (getFreePromotionPick() > 0)
    {
        return true;
    }
	//End FfH
*/
// lfgr end

	return m_bPromotionReady;
}


void CvUnit::setPromotionReady(bool bNewValue)
{
	if (isPromotionReady() != bNewValue)
	{
		m_bPromotionReady = bNewValue;

/*************************************************************************************************/
/**	ADDON (automatic terraforming) Sephi                                     					**/
/**																								**/
/**						                                            							**/
/*************************************************************************************************/
//        if (m_bPromotionReady)
		if ((m_bPromotionReady && AI_getUnitAIType() != UNITAI_TERRAFORMER))
/*************************************************************************************************/
/**	END                                                                  						**/
/*************************************************************************************************/

		{
			getGroup()->setAutomateType(NO_AUTOMATE);
			getGroup()->clearMissionQueue();
			getGroup()->setActivityType(ACTIVITY_AWAKE);
		}

		gDLL->getEntityIFace()->showPromotionGlow(getUnitEntity(), bNewValue);

		if (IsSelected())
		{
			gDLL->getInterfaceIFace()->setDirty(SelectionButtons_DIRTY_BIT, true);
		}
	}
}


void CvUnit::testPromotionReady()
{
// lfgr 04/2014 bugfix
/* old
	setPromotionReady((getExperience() >= experienceNeeded()) && canAcquirePromotionAny());
*/
	setPromotionReady( getFreePromotionPick() > 0 || (getExperience() >= experienceNeeded() ) && canAcquirePromotionAny());
// lfgr end
}


bool CvUnit::isDelayedDeath() const
{
	return m_bDeathDelay;
}


void CvUnit::startDelayedDeath()
{
	m_bDeathDelay = true;
}


// Returns true if killed...
bool CvUnit::doDelayedDeath()
{
	if (m_bDeathDelay && !isFighting())
	{
		logBBAI("    Killing %S -- delayed death (Unit %d - plot: %d, %d)",
				getName().GetCString(), getID(), getX(), getY());
		kill(false);
		return true;
	}

	return false;
}


bool CvUnit::isCombatFocus() const
{
	return m_bCombatFocus;
}


bool CvUnit::isInfoBarDirty() const
{
	return m_bInfoBarDirty;
}


void CvUnit::setInfoBarDirty(bool bNewValue)
{
	m_bInfoBarDirty = bNewValue;
}

bool CvUnit::isBlockading() const
{
	return m_bBlockading;
}

void CvUnit::setBlockading(bool bNewValue)
{
	if (bNewValue != isBlockading())
	{
		m_bBlockading = bNewValue;

		updatePlunder(isBlockading() ? 1 : -1, true);
	}
}

void CvUnit::collectBlockadeGold()
{
	if (plot()->getTeam() == getTeam())
	{
		return;
	}

	int iBlockadeRange = GC.defines.iSHIP_BLOCKADE_RANGE;

	for (int i = -iBlockadeRange; i <= iBlockadeRange; ++i)
	{
		for (int j = -iBlockadeRange; j <= iBlockadeRange; ++j)
		{
			CvPlot* pLoopPlot = ::plotXY(getX_INLINE(), getY_INLINE(), i, j);

			if (NULL != pLoopPlot && pLoopPlot->isRevealed(getTeam(), false))
			{
				CvCity* pCity = pLoopPlot->getPlotCity();

				if (NULL != pCity && !pCity->isPlundered() && isEnemy(pCity->getTeam()) && !atWar(pCity->getTeam(), getTeam()))
				{
					if (pCity->area() == area() || pCity->plot()->isAdjacentToArea(area()))
					{
						int iGold = pCity->calculateTradeProfit(pCity) * pCity->getTradeRoutes();
						if (iGold > 0)
						{
							pCity->setPlundered(true);
							GET_PLAYER(getOwnerINLINE()).changeGold(iGold);
							GET_PLAYER(pCity->getOwnerINLINE()).changeGold(-iGold);

							CvWString szBuffer = gDLL->getText("TXT_KEY_MISC_TRADE_ROUTE_PLUNDERED", getNameKey(), pCity->getNameKey(), iGold);
							gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BUILD_BANK", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), getX_INLINE(), getY_INLINE());

							szBuffer = gDLL->getText("TXT_KEY_MISC_TRADE_ROUTE_PLUNDER", getNameKey(), pCity->getNameKey(), iGold);
							gDLL->getInterfaceIFace()->addMessage(pCity->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BUILD_BANK", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pCity->getX_INLINE(), pCity->getY_INLINE());
						}
					}
				}
			}
		}
	}
}


PlayerTypes CvUnit::getOwner() const
{
	return getOwnerINLINE();
}

PlayerTypes CvUnit::getVisualOwner(TeamTypes eForTeam) const
{
	if (NO_TEAM == eForTeam)
	{
		eForTeam = GC.getGameINLINE().getActiveTeam();
	}

	if (getTeam() != eForTeam && eForTeam != BARBARIAN_TEAM)
	{

//FfH Hidden Nationality: Modified by Kael 08/27/2007
//		if (m_pUnitInfo->isHiddenNationality())
		if (isHiddenNationality())
//FfH: End Modify

		{
			if (!plot()->isCity(true, getTeam()))
			{
				return BARBARIAN_PLAYER;
			}
		}
	}

	return getOwnerINLINE();
}


PlayerTypes CvUnit::getCombatOwner(TeamTypes eForTeam, const CvPlot* pPlot) const
{
	if (eForTeam != NO_TEAM && getTeam() != eForTeam && eForTeam != BARBARIAN_TEAM)
	{
		if (isAlwaysHostile(pPlot))
		{
			return BARBARIAN_PLAYER;
		}
	}

	return getOwnerINLINE();
}


/************************************************************************************************/
/* Advanced Diplomacy         START                                                              */
/************************************************************************************************/
/*void CvUnit::setOriginalOwner(PlayerTypes ePlayer)
{
	if (ePlayer != m_eOriginalOwner)
	{
		m_eOriginalOwner = ePlayer;
	}
}
/************************************************************************************************/
/* Advanced Diplomacy        END                                                             */
/************************************************************************************************/


TeamTypes CvUnit::getTeam() const
{
	return GET_PLAYER(getOwnerINLINE()).getTeam();
}


PlayerTypes CvUnit::getCapturingPlayer() const
{
	return m_eCapturingPlayer;
}


void CvUnit::setCapturingPlayer(PlayerTypes eNewValue)
{

//FfH: Modified by Kael 08/12/2007
//	m_eCapturingPlayer = eNewValue;
    if (!isImmuneToCapture())
    {
        m_eCapturingPlayer = eNewValue;
    }
//FfH: End Add

}


const UnitTypes CvUnit::getUnitType() const
{
	return m_eUnitType;
}

CvUnitInfo &CvUnit::getUnitInfo() const
{
	return *m_pUnitInfo;
}


UnitClassTypes CvUnit::getUnitClassType() const
{
	return (UnitClassTypes)m_pUnitInfo->getUnitClassType();
}

const UnitTypes CvUnit::getLeaderUnitType() const
{
	return m_eLeaderUnitType;
}

void CvUnit::setLeaderUnitType(UnitTypes leaderUnitType)
{
	if(m_eLeaderUnitType != leaderUnitType)
	{
		m_eLeaderUnitType = leaderUnitType;
		reloadEntity();
	}
}

CvUnit* CvUnit::getCombatUnit() const
{
	return getUnit(m_combatUnit);
}


void CvUnit::setCombatUnit(CvUnit* pCombatUnit, bool bAttacking)
{
	if (isCombatFocus())
	{
		gDLL->getInterfaceIFace()->setCombatFocus(false);
	}

	if (pCombatUnit != NULL)
	{
		if (bAttacking)
		{
			if( gUnitLogLevel > 0 ) 
			{
				logBBAI("      *** KOMBAT! ***\n                    ATTACKER: %S (Unit %d), CombatStrength=%d\n                    DEFENDER: Player %d Unit %d (%S's %S), CombatStrength=%d\n",
						getName().GetCString(), getID(), currCombatStr(NULL, pCombatUnit), // lfgr fix 05/2020
						pCombatUnit->getOwnerINLINE(), pCombatUnit->getID(), GET_PLAYER(pCombatUnit->getOwnerINLINE()).getNameKey(), pCombatUnit->getName().GetCString(), pCombatUnit->currCombatStr(pCombatUnit->plot(), this));
			}

			if (getDomainType() == DOMAIN_LAND
				&& !m_pUnitInfo->isIgnoreBuildingDefense()
				&& pCombatUnit->plot()->getPlotCity()
				&& pCombatUnit->plot()->getPlotCity()->getBuildingDefense() > 0
				&& cityAttackModifier() >= GC.defines.iMIN_CITY_ATTACK_MODIFIER_FOR_SIEGE_TOWER)
			{
				CvDLLEntity::SetSiegeTower(true);
			}
		}

		FAssertMsg(getCombatUnit() == NULL, "Combat Unit is not expected to be assigned");
		FAssertMsg(!(plot()->isFighting()), "(plot()->isFighting()) did not return false as expected");
		m_bCombatFocus = (bAttacking && !(gDLL->getInterfaceIFace()->isFocusedWidget()) && ((getOwnerINLINE() == GC.getGameINLINE().getActivePlayer()) || ((pCombatUnit->getOwnerINLINE() == GC.getGameINLINE().getActivePlayer()) && !(GC.getGameINLINE().isMPOption(MPOPTION_SIMULTANEOUS_TURNS)))));
		m_combatUnit = pCombatUnit->getIDInfo();
		setCombatFirstStrikes((pCombatUnit->immuneToFirstStrikes()) ? 0 : (firstStrikes() + GC.getGameINLINE().getSorenRandNum(chanceFirstStrikes() + 1, "First Strike")));
	}
	else
	{
		if(getCombatUnit() != NULL)
		{
			FAssertMsg(getCombatUnit() != NULL, "getCombatUnit() is not expected to be equal with NULL");
			FAssertMsg(plot()->isFighting(), "plot()->isFighting is expected to be true");
			m_bCombatFocus = false;
			m_combatUnit.reset();
			setCombatFirstStrikes(0);

			if (IsSelected())
			{
				gDLL->getInterfaceIFace()->setDirty(InfoPane_DIRTY_BIT, true);
			}

			if (plot() == gDLL->getInterfaceIFace()->getSelectionPlot())
			{
				gDLL->getInterfaceIFace()->setDirty(PlotListButtons_DIRTY_BIT, true);
			}

			CvDLLEntity::SetSiegeTower(false);
		}
	}

	setCombatTimer(0);
	setInfoBarDirty(true);

	if (isCombatFocus())
	{
		gDLL->getInterfaceIFace()->setCombatFocus(true);
	}
}


CvUnit* CvUnit::getTransportUnit() const
{
	return getUnit(m_transportUnit);
}


bool CvUnit::isCargo() const
{
	return (getTransportUnit() != NULL);
}


void CvUnit::setTransportUnit(CvUnit* pTransportUnit)
{
	CvUnit* pOldTransportUnit;

	pOldTransportUnit = getTransportUnit();

	if (pOldTransportUnit != pTransportUnit)
	{
		if (pOldTransportUnit != NULL)
		{
			pOldTransportUnit->changeCargo(-1);
		}

		if (pTransportUnit != NULL)
		{
			FAssertMsg(pTransportUnit->cargoSpaceAvailable(getSpecialUnitType(), getDomainType()) > 0, "Cargo space is expected to be available");

			joinGroup(NULL, true); // Because what if a group of 3 tries to get in a transport which can hold 2...

			m_transportUnit = pTransportUnit->getIDInfo();

			if (getDomainType() != DOMAIN_AIR)
			{
				getGroup()->setActivityType(ACTIVITY_SLEEP);
			}

			if (GC.getGameINLINE().isFinalInitialized())
			{
				finishMoves();
			}

			pTransportUnit->changeCargo(1);
			pTransportUnit->getGroup()->setActivityType(ACTIVITY_AWAKE);
		}
		else
		{
			m_transportUnit.reset();

			getGroup()->setActivityType(ACTIVITY_AWAKE);
		}

#ifdef _DEBUG
		std::vector<CvUnit*> aCargoUnits;
		if (pOldTransportUnit != NULL)
		{
			pOldTransportUnit->getCargoUnits(aCargoUnits);
		}
		if (pTransportUnit != NULL)
		{
			pTransportUnit->getCargoUnits(aCargoUnits);
		}
#endif

	}
}


int CvUnit::getExtraDomainModifier(DomainTypes eIndex) const
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < NUM_DOMAIN_TYPES, "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_aiExtraDomainModifier[eIndex];
}


void CvUnit::changeExtraDomainModifier(DomainTypes eIndex, int iChange)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < NUM_DOMAIN_TYPES, "eIndex is expected to be within maximum bounds (invalid Index)");
	m_aiExtraDomainModifier[eIndex] = (m_aiExtraDomainModifier[eIndex] + iChange);
}


const CvWString CvUnit::getName(uint uiForm) const
{
	CvWString szBuffer;

	if (m_szName.empty())
	{
		return m_pUnitInfo->getDescription(uiForm);
	}
// BUG - Unit Name - start
	else if (isDescInName())
	{
		return m_szName;
	}
// BUG - Unit Name - end

	szBuffer.Format(L"%s (%s)", m_szName.GetCString(), m_pUnitInfo->getDescription(uiForm));

	return szBuffer;
}

// BUG - Unit Name - start
bool CvUnit::isDescInName() const
{
	return (m_szName.find(m_pUnitInfo->getDescription()) != -1);
}
// BUG - Unit Name - end


const wchar* CvUnit::getNameKey() const
{
	if (m_szName.empty())
	{
		return m_pUnitInfo->getTextKeyWide();
	}
	else
	{
		return m_szName.GetCString();
	}
}


const CvWString& CvUnit::getNameNoDesc() const
{
	return m_szName;
}


void CvUnit::setName(CvWString szNewValue)
{
	gDLL->stripSpecialCharacters(szNewValue);

	m_szName = szNewValue;

	if (IsSelected())
	{
		gDLL->getInterfaceIFace()->setDirty(InfoPane_DIRTY_BIT, true);
	}
}


std::string CvUnit::getScriptData() const
{
	return m_szScriptData;
}


void CvUnit::setScriptData(std::string szNewValue)
{
	m_szScriptData = szNewValue;
}


int CvUnit::getTerrainDoubleMoveCount(TerrainTypes eIndex) const
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumTerrainInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_paiTerrainDoubleMoveCount[eIndex];
}


bool CvUnit::isTerrainDoubleMove(TerrainTypes eIndex) const
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumTerrainInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return (getTerrainDoubleMoveCount(eIndex) > 0);
}


void CvUnit::changeTerrainDoubleMoveCount(TerrainTypes eIndex, int iChange)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumTerrainInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	m_paiTerrainDoubleMoveCount[eIndex] = (m_paiTerrainDoubleMoveCount[eIndex] + iChange);
	FAssert(getTerrainDoubleMoveCount(eIndex) >= 0);
}


int CvUnit::getFeatureDoubleMoveCount(FeatureTypes eIndex) const
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumFeatureInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_paiFeatureDoubleMoveCount[eIndex];
}


bool CvUnit::isFeatureDoubleMove(FeatureTypes eIndex) const
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumFeatureInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return (getFeatureDoubleMoveCount(eIndex) > 0);
}


void CvUnit::changeFeatureDoubleMoveCount(FeatureTypes eIndex, int iChange)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumFeatureInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	m_paiFeatureDoubleMoveCount[eIndex] = (m_paiFeatureDoubleMoveCount[eIndex] + iChange);
	FAssert(getFeatureDoubleMoveCount(eIndex) >= 0);
}


int CvUnit::getExtraTerrainAttackPercent(TerrainTypes eIndex) const
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumTerrainInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_paiExtraTerrainAttackPercent[eIndex];
}


void CvUnit::changeExtraTerrainAttackPercent(TerrainTypes eIndex, int iChange)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumTerrainInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");

	if (iChange != 0)
	{
		m_paiExtraTerrainAttackPercent[eIndex] += iChange;

		setInfoBarDirty(true);
	}
}

int CvUnit::getExtraTerrainDefensePercent(TerrainTypes eIndex) const
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumTerrainInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_paiExtraTerrainDefensePercent[eIndex];
}


void CvUnit::changeExtraTerrainDefensePercent(TerrainTypes eIndex, int iChange)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumTerrainInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");

	if (iChange != 0)
	{
		m_paiExtraTerrainDefensePercent[eIndex] += iChange;

		setInfoBarDirty(true);
	}
}

int CvUnit::getExtraFeatureAttackPercent(FeatureTypes eIndex) const
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumFeatureInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_paiExtraFeatureAttackPercent[eIndex];
}


void CvUnit::changeExtraFeatureAttackPercent(FeatureTypes eIndex, int iChange)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumFeatureInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");

	if (iChange != 0)
	{
		m_paiExtraFeatureAttackPercent[eIndex] += iChange;

		setInfoBarDirty(true);
	}
}

int CvUnit::getExtraFeatureDefensePercent(FeatureTypes eIndex) const
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumFeatureInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_paiExtraFeatureDefensePercent[eIndex];
}


void CvUnit::changeExtraFeatureDefensePercent(FeatureTypes eIndex, int iChange)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumFeatureInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");

	if (iChange != 0)
	{
		m_paiExtraFeatureDefensePercent[eIndex] += iChange;

		setInfoBarDirty(true);
	}
}

int CvUnit::getExtraUnitCombatModifier(UnitCombatTypes eIndex) const
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumUnitCombatInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_paiExtraUnitCombatModifier[eIndex];
}


void CvUnit::changeExtraUnitCombatModifier(UnitCombatTypes eIndex, int iChange)
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumUnitCombatInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	m_paiExtraUnitCombatModifier[eIndex] = (m_paiExtraUnitCombatModifier[eIndex] + iChange);
}


bool CvUnit::canAcquirePromotion(PromotionTypes ePromotion) const
{
	FAssertMsg(ePromotion >= 0, "ePromotion is expected to be non-negative (invalid Index)");
	FAssertMsg(ePromotion < GC.getNumPromotionInfos(), "ePromotion is expected to be within maximum bounds (invalid Index)");

	if (isHasPromotion(ePromotion))
	{
		return false;
	}

	CvPromotionInfo &kPromotion = GC.getPromotionInfo(ePromotion);

	if (kPromotion.getPrereqPromotion() != NO_PROMOTION)
	{
		if (!isHasPromotion((PromotionTypes)(kPromotion.getPrereqPromotion())))
		{
			return false;
		}
	}

//FfH: Modified by Kael 07/30/2007
//	if (kPromotion.getPrereqOrPromotion1() != NO_PROMOTION)
//	{
//		if (!isHasPromotion((PromotionTypes)(kPromotion.getPrereqOrPromotion1())))
//		{
//			if ((kPromotion.getPrereqOrPromotion2() == NO_PROMOTION) || !isHasPromotion((PromotionTypes)(kPromotion.getPrereqOrPromotion2())))
//			{
//				return false;
//			}
//		}
//	}
	/* MNAI Note - this section was moved to canPromote()
	if (kPromotion.getMinLevel() == -1)
	{
	    return false;
	}
	*/

	if (kPromotion.isRace())
	{
	    return false;
	}
	if (kPromotion.isEquipment())
	{
	    return false;
	}
	if (kPromotion.getMinLevel() > getLevel())
	{
	    return false;
	}
	if (kPromotion.getPromotionPrereqAnd() != NO_PROMOTION)
	{
		if (!isHasPromotion((PromotionTypes)(kPromotion.getPromotionPrereqAnd())))
		{
			return false;
		}
	}
	if (kPromotion.getPrereqOrPromotion1() != NO_PROMOTION)
	{
	    bool bValid = false;
		if (isHasPromotion((PromotionTypes)(GC.getPromotionInfo(ePromotion).getPrereqOrPromotion1())))
		{
		    bValid = true;
		}
        if (GC.getPromotionInfo(ePromotion).getPrereqOrPromotion2() != NO_PROMOTION)
        {
            if (isHasPromotion((PromotionTypes)(kPromotion.getPrereqOrPromotion2())))
            {
                bValid = true;
            }
        }
        if (kPromotion.getPromotionPrereqOr3() != NO_PROMOTION)
        {
            if (isHasPromotion((PromotionTypes)(kPromotion.getPromotionPrereqOr3())))
            {
                bValid = true;
            }
        }
        if (kPromotion.getPromotionPrereqOr4() != NO_PROMOTION)
        {
            if (isHasPromotion((PromotionTypes)(kPromotion.getPromotionPrereqOr4())))
            {
                bValid = true;
            }
        }
        if (!bValid)
        {
            return false;
        }
	}
	if (kPromotion.getBonusPrereq() != NO_BONUS)
	{
	    if (!GET_PLAYER(getOwnerINLINE()).hasBonus((BonusTypes)kPromotion.getBonusPrereq()))
	    {
	        return false;
	    }
	}

	// XML_LISTS 07/2019 lfgr
	if( isPromotionImmune( ePromotion ) ) {
		return false;
	}
	// XML_LISTS end

	if (kPromotion.isPrereqAlive())
	{
	    if (!isAlive())
	    {
	        return false;
	    }
	}
//FfH: End Add

	if (kPromotion.getTechPrereq() != NO_TECH)
	{
		if (!(GET_TEAM(getTeam()).isHasTech((TechTypes)(kPromotion.getTechPrereq()))))
		{
			return false;
		}
	}

	if (kPromotion.getStateReligionPrereq() != NO_RELIGION)
	{
		if (GET_PLAYER(getOwnerINLINE()).getStateReligion() != kPromotion.getStateReligionPrereq())
		{
			return false;
		}
	}

	if (kPromotion.getUnitReligionPrereq() != NO_RELIGION)
	{
		if (getReligion() != kPromotion.getUnitReligionPrereq())
		{
			return false;
		}
	}

	if (!isPromotionValid(ePromotion))
	{
		return false;
	}

	return true;
}

bool CvUnit::isPromotionValid(PromotionTypes ePromotion) const
{
	if (!::isPromotionValid(ePromotion, getUnitType(), true))
	{
		return false;
	}

	CvPromotionInfo& promotionInfo = GC.getPromotionInfo(ePromotion);

	if (promotionInfo.isPrereqAlive() && !isAlive())
	{
		return false;
	}

//FfH: Modified by Kael 10/28/2008
//	if (promotionInfo.getWithdrawalChange() + m_pUnitInfo->getWithdrawalProbability() + getExtraWithdrawal() > GC.defines.iMAX_WITHDRAWAL_PROBABILITY)
//	{
//		return false;
//	}
    if (promotionInfo.getWithdrawalChange() > 0)
    {
        if (promotionInfo.getWithdrawalChange() + m_pUnitInfo->getWithdrawalProbability() + getExtraWithdrawal() > GC.defines.iMAX_WITHDRAWAL_PROBABILITY)
        {
            return false;
        }
    }
//FfH: End Modify

	if (promotionInfo.getInterceptChange() + maxInterceptionProbability() > GC.defines.iMAX_INTERCEPTION_PROBABILITY)
	{
		return false;
	}

	if (promotionInfo.getEvasionChange() + evasionProbability() > GC.defines.iMAX_EVASION_PROBABILITY)
	{
		return false;
	}

	return true;
}


bool CvUnit::canAcquirePromotionAny() const
{
	int iI;

	for (iI = 0; iI < GC.getNumPromotionInfos(); iI++)
	{
		if (canAcquirePromotion((PromotionTypes)iI))
		{
			return true;
		}
	}

	return false;
}


bool CvUnit::isHasPromotion(PromotionTypes eIndex) const
{
	FAssertMsg(eIndex >= 0, "eIndex is expected to be non-negative (invalid Index)");
	FAssertMsg(eIndex < GC.getNumPromotionInfos(), "eIndex is expected to be within maximum bounds (invalid Index)");
	return m_pabHasPromotion[eIndex];
}


void CvUnit::setHasPromotion(PromotionTypes eIndex, bool bNewValue)
{
	int iChange;
	int iI;

//FfH: Added by Kael 07/28/2008
    if (bNewValue)
    {
		// XML_LISTS 07/2019 lfgr
		// lfgr_todo: Maybe remove this
		if( isPromotionImmune( eIndex ) ) {
			return;
		}
		// XML_LISTS end
    }
//FfH: End Add

	if (isHasPromotion(eIndex) != bNewValue)
	{
		m_pabHasPromotion[eIndex] = bNewValue;

		iChange = ((isHasPromotion(eIndex)) ? 1 : -1);

		CvPromotionInfo& kPromotionInfo = GC.getPromotionInfo(eIndex);

		changeBlitzCount((kPromotionInfo.isBlitz()) ? iChange : 0);
		changeAmphibCount((kPromotionInfo.isAmphib()) ? iChange : 0);
		changeRiverCount((kPromotionInfo.isRiver()) ? iChange : 0);
		changeEnemyRouteCount((kPromotionInfo.isEnemyRoute()) ? iChange : 0);
		changeAlwaysHealCount((kPromotionInfo.isAlwaysHeal()) ? iChange : 0);
		changeHillsDoubleMoveCount((kPromotionInfo.isHillsDoubleMove()) ? iChange : 0);
		changeImmuneToFirstStrikesCount((kPromotionInfo.isImmuneToFirstStrikes()) ? iChange : 0);

		changeExtraVisibilityRange(kPromotionInfo.getVisibilityChange() * iChange);
		changeExtraMoves(kPromotionInfo.getMovesChange() * iChange);
		changeExtraMoveDiscount(kPromotionInfo.getMoveDiscountChange() * iChange);
		changeExtraAirRange(kPromotionInfo.getAirRangeChange() * iChange);
		changeExtraIntercept(kPromotionInfo.getInterceptChange() * iChange);
		changeExtraEvasion(kPromotionInfo.getEvasionChange() * iChange);
		changeExtraFirstStrikes(kPromotionInfo.getFirstStrikesChange() * iChange);
		changeExtraChanceFirstStrikes(kPromotionInfo.getChanceFirstStrikesChange() * iChange);
		changeExtraWithdrawal(kPromotionInfo.getWithdrawalChange() * iChange);
		changeExtraCollateralDamage(kPromotionInfo.getCollateralDamageChange() * iChange);
		changeExtraBombardRate(kPromotionInfo.getBombardRateChange() * iChange);
		changeExtraEnemyHeal(kPromotionInfo.getEnemyHealChange() * iChange);
		changeExtraNeutralHeal(kPromotionInfo.getNeutralHealChange() * iChange);
		changeExtraFriendlyHeal(kPromotionInfo.getFriendlyHealChange() * iChange);
		changeSameTileHeal(kPromotionInfo.getSameTileHealChange() * iChange);
		changeAdjacentTileHeal(kPromotionInfo.getAdjacentTileHealChange() * iChange);
		changeExtraCombatPercent(kPromotionInfo.getCombatPercent() * iChange);
		changeExtraCityAttackPercent(kPromotionInfo.getCityAttackPercent() * iChange);
		changeExtraCityDefensePercent(kPromotionInfo.getCityDefensePercent() * iChange);
		changeExtraHillsAttackPercent(kPromotionInfo.getHillsAttackPercent() * iChange);
		changeExtraHillsDefensePercent(kPromotionInfo.getHillsDefensePercent() * iChange);
		changeRevoltProtection(kPromotionInfo.getRevoltProtection() * iChange);
		changeCollateralDamageProtection(kPromotionInfo.getCollateralDamageProtection() * iChange);
		changePillageChange(kPromotionInfo.getPillageChange() * iChange);
		changeUpgradeDiscount(kPromotionInfo.getUpgradeDiscount() * iChange);
		changeExperiencePercent(kPromotionInfo.getExperiencePercent() * iChange);
		changeKamikazePercent((kPromotionInfo.getKamikazePercent()) * iChange);
		changeCargoSpace(kPromotionInfo.getCargoChange() * iChange);

//FfH: Added by Kael 07/30/2007
        if (kPromotionInfo.isAIControl() && bNewValue)
        {
            joinGroup(NULL);
        }
        changeAIControl((kPromotionInfo.isAIControl()) ? iChange : 0);
		changeAlive((kPromotionInfo.isNotAlive()) ? iChange : 0);
		changeBaseCombatStr(kPromotionInfo.getExtraCombatStr() * iChange);
		changeBaseCombatStrDefense(kPromotionInfo.getExtraCombatDefense() * iChange);
		changeBetterDefenderThanPercent(kPromotionInfo.getBetterDefenderThanPercent() * iChange);
		changeBoarding((kPromotionInfo.isBoarding()) ? iChange : 0);
		changeCombatHealPercent(kPromotionInfo.getCombatHealPercent() * iChange);
		changeCombatPercentInBorders(kPromotionInfo.getCombatPercentInBorders() * iChange);
		changeCombatPercentGlobalCounter(kPromotionInfo.getCombatPercentGlobalCounter() * iChange);
		changeDefensiveStrikeChance(kPromotionInfo.getDefensiveStrikeChance() * iChange);
		changeDefensiveStrikeDamage(kPromotionInfo.getDefensiveStrikeDamage() * iChange);
		changeDoubleFortifyBonus((kPromotionInfo.isDoubleFortifyBonus()) ? iChange : 0);
		changeFear((kPromotionInfo.isFear()) ? iChange : 0);
		changeFlying((kPromotionInfo.isFlying()) ? iChange : 0);
		changeGoldFromCombat(kPromotionInfo.getGoldFromCombat() * iChange);
		changeHeld((kPromotionInfo.isHeld()) ? iChange : 0);
		changeHiddenNationality((kPromotionInfo.isHiddenNationality()) ? iChange : 0);
		changeIgnoreBuildingDefense((kPromotionInfo.isIgnoreBuildingDefense()) ? iChange : 0);
		changeImmortal((kPromotionInfo.isImmortal()) ? iChange : 0);
		changeImmuneToCapture((kPromotionInfo.isImmuneToCapture()) ? iChange : 0);
		changeImmuneToDefensiveStrike((kPromotionInfo.isImmuneToDefensiveStrike()) ? iChange : 0);
		changeImmuneToFear((kPromotionInfo.isImmuneToFear()) ? iChange : 0);
		changeImmuneToMagic((kPromotionInfo.isImmuneToMagic()) ? iChange : 0);
		changeInvisibleFromPromotion((kPromotionInfo.isInvisible()) ? iChange : 0);
		changeOnlyDefensive((kPromotionInfo.isOnlyDefensive()) ? iChange : 0);
		changeResist(kPromotionInfo.getResistMagic() * iChange);
		changeResistModify(kPromotionInfo.getCasterResistModify() * iChange);
		changeSeeInvisible((kPromotionInfo.isSeeInvisible()) ? iChange : 0);
		changeSpellCasterXP(kPromotionInfo.getSpellCasterXP() * iChange);
		changeSpellDamageModify(kPromotionInfo.getSpellDamageModify() * iChange);
		changeTargetWeakestUnit((kPromotionInfo.isTargetWeakestUnit()) ? iChange : 0);
		changeTargetWeakestUnitCounter((kPromotionInfo.isTargetWeakestUnitCounter()) ? iChange : 0);
		changeTwincast((kPromotionInfo.isTwincast()) ? iChange : 0);
		changeWaterWalking((kPromotionInfo.isWaterWalking()) ? iChange : 0);
		changeWorkRateModify(kPromotionInfo.getWorkRateModify() * iChange);
        GC.getGameINLINE().changeGlobalCounter(kPromotionInfo.getModifyGlobalCounter() * iChange);
        if (kPromotionInfo.getCombatLimit() != 0)
        {
            calcCombatLimit();
        }
        if (eIndex == GC.defines.iMUTATED_PROMOTION && bNewValue)
        {
            mutate();
        }
        if (kPromotionInfo.isRace())
        {
            if (bNewValue)
            {
                setRace(eIndex);
            }
            else
            {
                setRace(NO_PROMOTION);
            }
        }
		for (iI = 0; iI < GC.getNumDamageTypeInfos(); iI++)
		{
			changeDamageTypeCombat(((DamageTypes)iI), (kPromotionInfo.getDamageTypeCombat(iI) * iChange));
		}
		for (iI = 0; iI < GC.getNumBonusInfos(); iI++)
		{
			changeBonusAffinity(((BonusTypes)iI), (kPromotionInfo.getBonusAffinity(iI) * iChange));
		}
		for (iI = 0; iI < GC.getNumDamageTypeInfos(); iI++)
		{
			changeDamageTypeResist(((DamageTypes)iI), (kPromotionInfo.getDamageTypeResist(iI) * iChange));
		}
//FfH: End Add
		// MNAI - additional promotion tags
		changeCanMoveImpassable((kPromotionInfo.isAllowsMoveImpassable()) ? iChange : 0);
		changeCanMoveLimitedBorders((kPromotionInfo.isAllowsMoveLimitedBorders()) ? iChange : 0);
		changeCastingBlocked((kPromotionInfo.isCastingBlocked()) ? iChange : 0);
		changeUpgradeBlocked((kPromotionInfo.isBlocksUpgrade()) ? iChange : 0);
		changeGiftingBlocked((kPromotionInfo.isBlocksGifting()) ? iChange : 0);
		changeUpgradeOutsideBorders((kPromotionInfo.isUpgradeOutsideBorders()) ? iChange : 0);
		// End MNAI
		
		// XML_LISTS 07/2019 lfgr: cache CvPromotionInfo::isPromotionImmune
		for( int ePromotion = 0; ePromotion < GC.getNumPromotionInfos(); ePromotion++ ) {
			changePromotionImmune( (PromotionTypes) ePromotion, kPromotionInfo.isPromotionImmune( ePromotion ) ? iChange : 0);
		}
		// XML_LISTS end

		for (iI = 0; iI < GC.getNumTerrainInfos(); iI++)
		{
			changeExtraTerrainAttackPercent(((TerrainTypes)iI), (kPromotionInfo.getTerrainAttackPercent(iI) * iChange));
			changeExtraTerrainDefensePercent(((TerrainTypes)iI), (kPromotionInfo.getTerrainDefensePercent(iI) * iChange));
			changeTerrainDoubleMoveCount(((TerrainTypes)iI), ((kPromotionInfo.getTerrainDoubleMove(iI)) ? iChange : 0));
		}

		for (iI = 0; iI < GC.getNumFeatureInfos(); iI++)
		{
			changeExtraFeatureAttackPercent(((FeatureTypes)iI), (kPromotionInfo.getFeatureAttackPercent(iI) * iChange));
			changeExtraFeatureDefensePercent(((FeatureTypes)iI), (kPromotionInfo.getFeatureDefensePercent(iI) * iChange));
			changeFeatureDoubleMoveCount(((FeatureTypes)iI), ((kPromotionInfo.getFeatureDoubleMove(iI)) ? iChange : 0));
		}

		for (iI = 0; iI < GC.getNumUnitCombatInfos(); iI++)
		{
			changeExtraUnitCombatModifier(((UnitCombatTypes)iI), (kPromotionInfo.getUnitCombatModifierPercent(iI) * iChange));
		}

		for (iI = 0; iI < NUM_DOMAIN_TYPES; iI++)
		{
			changeExtraDomainModifier(((DomainTypes)iI), (kPromotionInfo.getDomainModifierPercent(iI) * iChange));
		}

		if (!bNewValue && kPromotionInfo.isLeader())
		{
			//update graphics models
			m_eLeaderUnitType = NO_UNIT;
			reloadEntity();
		}

		if (IsSelected())
		{
			gDLL->getInterfaceIFace()->setDirty(SelectionButtons_DIRTY_BIT, true);
			gDLL->getInterfaceIFace()->setDirty(InfoPane_DIRTY_BIT, true);
		}

		//update graphics
		gDLL->getEntityIFace()->updatePromotionLayers(getUnitEntity());

//FfH: Added by Kael 07/04/2009
		if (kPromotionInfo.getUnitArtStyleType() != NO_UNIT_ARTSTYLE)
		{
//>>>>Unofficial Bug Fix: Modified by Denev 2009/10/25
//*** Prevent to destroy artstyle
/*
			if (iChange > 0)
			{
				setUnitArtStyleType(kPromotionInfo.getUnitArtStyleType());
			}
			else
			{
				if (kPromotionInfo.getUnitArtStyleType() == getUnitArtStyleType())
				{
					setUnitArtStyleType(NO_UNIT_ARTSTYLE);
				}
			}
*/
			CvWStringBuffer szArtDefineTag;
			UnitArtStyleTypes eUnitArtStyleType = NO_UNIT_ARTSTYLE;

			if (NO_PROMOTION != getRace())
			{
				eUnitArtStyleType = (UnitArtStyleTypes)GC.getPromotionInfo((PromotionTypes)getRace()).getUnitArtStyleType();
				if (NO_UNIT_ARTSTYLE != eUnitArtStyleType)
				{
					szArtDefineTag.assign(GC.getUnitArtStyleTypeInfo(eUnitArtStyleType).getEarlyArtDefineTag(0, getUnitType()));
				}
			}
			if (szArtDefineTag.isEmpty())
			{
				for (int iPromotion = 0; iPromotion < GC.getNumPromotionInfos(); iPromotion++)
				{
					if (isHasPromotion((PromotionTypes)iPromotion))
					{
						eUnitArtStyleType = (UnitArtStyleTypes)GC.getPromotionInfo((PromotionTypes)iPromotion).getUnitArtStyleType();
						if (NO_UNIT_ARTSTYLE != eUnitArtStyleType)
						{
							szArtDefineTag.assign(GC.getUnitArtStyleTypeInfo(eUnitArtStyleType).getEarlyArtDefineTag(0, getUnitType()));
							if (!szArtDefineTag.isEmpty())
							{
								break;
							}
						}
					}
				}
			}

			setUnitArtStyleType(eUnitArtStyleType);
//<<<<Unofficial Bug Fix: End Modify
			reloadEntity();
		}
		if (kPromotionInfo.getGroupSize() != 0)
		{
			if (bNewValue)
			{
				setGroupSize(kPromotionInfo.getGroupSize());
			}
			else
			{
				setGroupSize(0);
			}
			reloadEntity();
		}
		updateTerraformer();
//FfH: End Add

	}
}


int CvUnit::getSubUnitCount() const
{
	return m_pUnitInfo->getGroupSize();
}


int CvUnit::getSubUnitsAlive() const
{
	return getSubUnitsAlive( getDamage());
}


int CvUnit::getSubUnitsAlive(int iDamage) const
{
	if (iDamage >= maxHitPoints())
	{
		return 0;
	}
	else
	{

//FfH: Modified by Kael 10/26/2007
//		return std::max(1, (((m_pUnitInfo->getGroupSize() * (maxHitPoints() - iDamage)) + (maxHitPoints() / ((m_pUnitInfo->getGroupSize() * 2) + 1))) / maxHitPoints()));
		return std::max(1, (((getGroupSize() * (maxHitPoints() - iDamage)) + (maxHitPoints() / ((getGroupSize() * 2) + 1))) / maxHitPoints()));
//FfH: End Modify
	}
}
// returns true if unit can initiate a war action with plot (possibly by declaring war)
bool CvUnit::potentialWarAction(const CvPlot* pPlot) const
{
	TeamTypes ePlotTeam = pPlot->getTeam();
	TeamTypes eUnitTeam = getTeam();

	if (ePlotTeam == NO_TEAM)
	{
		return false;
	}

	if (isEnemy(ePlotTeam, pPlot))
	{
		return true;
	}

	if (getGroup()->AI_isDeclareWar(pPlot) && GET_TEAM(eUnitTeam).AI_getWarPlan(ePlotTeam) != NO_WARPLAN)
	{
		return true;
	}

	return false;
}



void CvUnit::collateralCombat(const CvPlot* pPlot, CvUnit* pSkipUnit)
{
	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pLoopUnit;
	CvUnit* pBestUnit;
	CvWString szBuffer;
	int iTheirStrength;
	int iStrengthFactor;
	int iCollateralDamage;
	int iUnitDamage;
	int iDamageCount;
	int iPossibleTargets;
	int iCount;
	int iValue;
	int iBestValue;
	std::map<CvUnit*, int> mapUnitDamage;
	std::map<CvUnit*, int>::iterator it;

	int iCollateralStrength = (getDomainType() == DOMAIN_AIR ? airBaseCombatStr() : baseCombatStr()) * collateralDamage() / 100;
	// UNOFFICIAL_PATCH Start
	// * Barrage promotions made working again on Tanks and other units with no base collateral ability
	if (iCollateralStrength == 0 && getExtraCollateralDamage() == 0)
	// UNOFFICIAL_PATCH End
	{
		return;
	}

	iPossibleTargets = std::min((pPlot->getNumVisibleEnemyDefenders(this) - 1), collateralDamageMaxUnits());

	pUnitNode = pPlot->headUnitNode();

	while (pUnitNode != NULL)
	{
		pLoopUnit = ::getUnit(pUnitNode->m_data);
		pUnitNode = pPlot->nextUnitNode(pUnitNode);

		if (pLoopUnit != pSkipUnit)
		{
			if (isEnemy(pLoopUnit->getTeam(), pPlot))
			{
				if (!(pLoopUnit->isInvisible(getTeam(), false)))
				{
					if (pLoopUnit->canDefend())
					{
						iValue = (1 + GC.getGameINLINE().getSorenRandNum(10000, "Collateral Damage"));

						iValue *= pLoopUnit->currHitPoints();

						mapUnitDamage[pLoopUnit] = iValue;
					}
				}
			}
		}
	}

	CvCity* pCity = NULL;
	if (getDomainType() == DOMAIN_AIR)
	{
		pCity = pPlot->getPlotCity();
	}

	iDamageCount = 0;
	iCount = 0;

	while (iCount < iPossibleTargets)
	{
		iBestValue = 0;
		pBestUnit = NULL;

		for (it = mapUnitDamage.begin(); it != mapUnitDamage.end(); it++)
		{
			if (it->second > iBestValue)
			{
				iBestValue = it->second;
				pBestUnit = it->first;
			}
		}

		if (pBestUnit != NULL)
		{
			mapUnitDamage.erase(pBestUnit);

			if (NO_UNITCOMBAT == getUnitCombatType() || !pBestUnit->getUnitInfo().getUnitCombatCollateralImmune(getUnitCombatType()))
			{
				iTheirStrength = pBestUnit->baseCombatStr();

				iStrengthFactor = ((iCollateralStrength + iTheirStrength + 1) / 2);

				iCollateralDamage = (GC.defines.iCOLLATERAL_COMBAT_DAMAGE * (iCollateralStrength + iStrengthFactor)) / (iTheirStrength + iStrengthFactor);

				iCollateralDamage *= 100 + getExtraCollateralDamage();

				iCollateralDamage *= std::max(0, 100 - pBestUnit->getCollateralDamageProtection());
				iCollateralDamage /= 100;

				if (pCity != NULL)
				{
					iCollateralDamage *= 100 + pCity->getAirModifier();
					iCollateralDamage /= 100;
				}

				iCollateralDamage /= 100;

				iCollateralDamage = std::max(0, iCollateralDamage);

				int iMaxDamage = std::min(collateralDamageLimit(), (collateralDamageLimit() * (iCollateralStrength + iStrengthFactor)) / (iTheirStrength + iStrengthFactor));
				iUnitDamage = std::max(pBestUnit->getDamage(), std::min(pBestUnit->getDamage() + iCollateralDamage, iMaxDamage));

				if (pBestUnit->getDamage() != iUnitDamage)
				{
// BUG - Combat Events - start
					int iDamageDone = iUnitDamage - pBestUnit->getDamage();
					pBestUnit->setDamage(iUnitDamage, getOwnerINLINE());
					CvEventReporter::getInstance().combatLogCollateral(this, pBestUnit, iDamageDone);
// BUG - Combat Events - end
					iDamageCount++;
				}
			}

			iCount++;
		}
		else
		{
			break;
		}
	}

	if (iDamageCount > 0)
	{
		szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_SUFFER_COL_DMG", iDamageCount);
		gDLL->getInterfaceIFace()->addMessage(pSkipUnit->getOwnerINLINE(), (pSkipUnit->getDomainType() != DOMAIN_AIR), GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_COLLATERAL", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pSkipUnit->getX_INLINE(), pSkipUnit->getY_INLINE(), true, true);

		szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_INFLICT_COL_DMG", getNameKey(), iDamageCount);
		gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_COLLATERAL", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pSkipUnit->getX_INLINE(), pSkipUnit->getY_INLINE());
	}
}


void CvUnit::flankingStrikeCombat(const CvPlot* pPlot, int iAttackerStrength, int iAttackerFirepower, int iDefenderOdds, int iDefenderDamage, CvUnit* pSkipUnit)
{
	if (pPlot->isCity(true, pSkipUnit->getTeam()))
	{
		return;
	}

	CLLNode<IDInfo>* pUnitNode = pPlot->headUnitNode();

	std::vector< std::pair<CvUnit*, int> > listFlankedUnits;
	while (NULL != pUnitNode)
	{
		CvUnit* pLoopUnit = ::getUnit(pUnitNode->m_data);
		pUnitNode = pPlot->nextUnitNode(pUnitNode);

		if (pLoopUnit != pSkipUnit)
		{
			if (!pLoopUnit->isDead() && isEnemy(pLoopUnit->getTeam(), pPlot))
			{
				if (!(pLoopUnit->isInvisible(getTeam(), false)))
				{
					if (pLoopUnit->canDefend())
					{
						int iFlankingStrength = m_pUnitInfo->getFlankingStrikeUnitClass(pLoopUnit->getUnitClassType());

						if (iFlankingStrength > 0)
						{
							int iFlankedDefenderStrength;
							int iFlankedDefenderOdds;
							int iAttackerDamage;
							int iFlankedDefenderDamage;

							getDefenderCombatValues(*pLoopUnit, pPlot, iAttackerStrength, iAttackerFirepower, iFlankedDefenderOdds, iFlankedDefenderStrength, iAttackerDamage, iFlankedDefenderDamage);

							if (GC.getGameINLINE().getSorenRandNum(GC.defines.iCOMBAT_DIE_SIDES, "Flanking Combat") >= iDefenderOdds)
							{
								int iCollateralDamage = (iFlankingStrength * iDefenderDamage) / 100;
								int iUnitDamage = std::max(pLoopUnit->getDamage(), std::min(pLoopUnit->getDamage() + iCollateralDamage, collateralDamageLimit()));

								if (pLoopUnit->getDamage() != iUnitDamage)
								{
									listFlankedUnits.push_back(std::make_pair(pLoopUnit, iUnitDamage));
								}
							}
						}
					}
				}
			}
		}
	}

	int iNumUnitsHit = std::min((int)listFlankedUnits.size(), collateralDamageMaxUnits());

	for (int i = 0; i < iNumUnitsHit; ++i)
	{
		int iIndexHit = GC.getGameINLINE().getSorenRandNum(listFlankedUnits.size(), "Pick Flanked Unit");
		CvUnit* pUnit = listFlankedUnits[iIndexHit].first;
		int iDamage = listFlankedUnits[iIndexHit].second;
// BUG - Combat Events - start
		int iDamageDone = iDamage - pUnit->getDamage();
// BUG - Combat Events - end
		pUnit->setDamage(iDamage, getOwnerINLINE());
		if (pUnit->isDead())
		{
			CvWString szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_KILLED_UNIT_BY_FLANKING", getNameKey(), pUnit->getNameKey(), pUnit->getVisualCivAdjective(getTeam()));
			gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, GC.getEraInfo(GC.getGameINLINE().getCurrentEra()).getAudioUnitVictoryScript(), MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
			szBuffer = gDLL->getText("TXT_KEY_MISC_YOUR_UNIT_DIED_BY_FLANKING", pUnit->getNameKey(), getNameKey(), getVisualCivAdjective(pUnit->getTeam()));
			gDLL->getInterfaceIFace()->addMessage(pUnit->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, GC.getEraInfo(GC.getGameINLINE().getCurrentEra()).getAudioUnitDefeatScript(), MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
			
			logBBAI("    Killing %S -- Unit killed by flanking damage (Unit %d - plot: %d, %d)",
					getName().GetCString(), getID(), getX(), getY());
			pUnit->kill(false);
		}
// BUG - Combat Events - start
		CvEventReporter::getInstance().combatLogFlanking(this, pUnit, iDamageDone);
// BUG - Combat Events - end
		
		listFlankedUnits.erase(std::remove(listFlankedUnits.begin(), listFlankedUnits.end(), listFlankedUnits[iIndexHit]));
	}

	if (iNumUnitsHit > 0)
	{
		CvWString szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_DAMAGED_UNITS_BY_FLANKING", getNameKey(), iNumUnitsHit);
		gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, GC.getEraInfo(GC.getGameINLINE().getCurrentEra()).getAudioUnitVictoryScript(), MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE());

		if (NULL != pSkipUnit)
		{
			szBuffer = gDLL->getText("TXT_KEY_MISC_YOUR_UNITS_DAMAGED_BY_FLANKING", getNameKey(), iNumUnitsHit);
			gDLL->getInterfaceIFace()->addMessage(pSkipUnit->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, GC.getEraInfo(GC.getGameINLINE().getCurrentEra()).getAudioUnitDefeatScript(), MESSAGE_TYPE_INFO, NULL, (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE());
		}
	}
}


// Returns true if we were intercepted...
bool CvUnit::interceptTest(const CvPlot* pPlot)
{
	if (GC.getGameINLINE().getSorenRandNum(100, "Evasion Rand") >= evasionProbability())
	{
		CvUnit* pInterceptor = bestInterceptor(pPlot);

		if (pInterceptor != NULL)
		{
			if (GC.getGameINLINE().getSorenRandNum(100, "Intercept Rand (Air)") < pInterceptor->currInterceptionProbability())
			{
				fightInterceptor(pPlot, false);

				return true;
			}
		}
	}

	return false;
}


CvUnit* CvUnit::airStrikeTarget(const CvPlot* pPlot) const
{
	CvUnit* pDefender;

	pDefender = pPlot->getBestDefender(NO_PLAYER, getOwnerINLINE(), this, true);

	if (pDefender != NULL)
	{
		if (!pDefender->isDead())
		{
			if (pDefender->canDefend())
			{
				return pDefender;
			}
		}
	}

	return NULL;
}


bool CvUnit::canAirStrike(const CvPlot* pPlot) const
{
	if (getDomainType() != DOMAIN_AIR)
	{
		return false;
	}

	if (!canAirAttack())
	{
		return false;
	}

	if (pPlot == plot())
	{
		return false;
	}

	if (!pPlot->isVisible(getTeam(), false))
	{
		return false;
	}

	if (plotDistance(getX_INLINE(), getY_INLINE(), pPlot->getX_INLINE(), pPlot->getY_INLINE()) > airRange())
	{
		return false;
	}

	if (airStrikeTarget(pPlot) == NULL)
	{
		return false;
	}

	return true;
}


bool CvUnit::airStrike(CvPlot* pPlot)
{
	if (!canAirStrike(pPlot))
	{
		return false;
	}

	if (interceptTest(pPlot))
	{
		return false;
	}

	CvUnit* pDefender = airStrikeTarget(pPlot);

	FAssert(pDefender != NULL);
	FAssert(pDefender->canDefend());

	setReconPlot(pPlot);

	setMadeAttack(true);
	changeMoves(GC.getMOVE_DENOMINATOR());

	int iDamage = airCombatDamage(pDefender);

	int iUnitDamage = std::max(pDefender->getDamage(), std::min((pDefender->getDamage() + iDamage), airCombatLimit()));

	CvWString szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_ARE_ATTACKED_BY_AIR", pDefender->getNameKey(), getNameKey(), -(((iUnitDamage - pDefender->getDamage()) * 100) / pDefender->maxHitPoints()));
	gDLL->getInterfaceIFace()->addMessage(pDefender->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_AIR_ATTACK", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pPlot->getX_INLINE(), pPlot->getY_INLINE(), true, true);

	szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_ATTACK_BY_AIR", getNameKey(), pDefender->getNameKey(), -(((iUnitDamage - pDefender->getDamage()) * 100) / pDefender->maxHitPoints()));
	gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_AIR_ATTACKED", MESSAGE_TYPE_INFO, pDefender->getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE());

	collateralCombat(pPlot, pDefender);

	pDefender->setDamage(iUnitDamage, getOwnerINLINE());

	return true;
}

bool CvUnit::canRangeStrike() const
{
	if (getDomainType() == DOMAIN_AIR)
	{
		return false;
	}

	if (airRange() <= 0)
	{
		return false;
	}

	if (airBaseCombatStr() <= 0)
	{
		return false;
	}

	if (!canFight())
	{
		return false;
	}

	if (isMadeAttack() && !isBlitz())
	{
		return false;
	}

	if (!canMove() && getMoves() > 0)
	{
		return false;
	}

	return true;
}

bool CvUnit::canRangeStrikeAt(const CvPlot* pPlot, int iX, int iY) const
{
	if (!canRangeStrike())
	{
		return false;
	}

	CvPlot* pTargetPlot = GC.getMapINLINE().plotINLINE(iX, iY);

	if (NULL == pTargetPlot)
	{
		return false;
	}

	if (!pPlot->isVisible(getTeam(), false))
	{
		return false;
	}

/************************************************************************************************/
/* UNOFFICIAL_PATCH                       05/10/10                             jdog5000         */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
	// Need to check target plot too
	if (!pTargetPlot->isVisible(getTeam(), false))
	{
		return false;
	}
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/

	if (plotDistance(pPlot->getX_INLINE(), pPlot->getY_INLINE(), pTargetPlot->getX_INLINE(), pTargetPlot->getY_INLINE()) > airRange())
	{
		return false;
	}

	CvUnit* pDefender = airStrikeTarget(pTargetPlot);
	if (NULL == pDefender)
	{
		return false;
	}

	if (!pPlot->canSeePlot(pTargetPlot, getTeam(), airRange(), getFacingDirection(true)))
	{
		return false;
	}
	
	return true;
}


bool CvUnit::rangeStrike(int iX, int iY)
{
	CvUnit* pDefender;
	CvWString szBuffer;
	int iUnitDamage;
	int iDamage;

	CvPlot* pPlot = GC.getMapINLINE().plot(iX, iY);
	if (NULL == pPlot)
	{
		return false;
	}

/************************************************************************************************/
/* UNOFFICIAL_PATCH                       05/10/10                             jdog5000         */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
	if (!canRangeStrikeAt(pPlot, iX, iY))
	{
		return false;
	}
*/
	if (!canRangeStrikeAt(plot(), iX, iY))
	{
		return false;
	}
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/

	pDefender = airStrikeTarget(pPlot);

	FAssert(pDefender != NULL);
	FAssert(pDefender->canDefend());

	if (GC.defines.iRANGED_ATTACKS_USE_MOVES == 0)
	{
		setMadeAttack(true);
	}
	changeMoves(GC.getMOVE_DENOMINATOR());

	iDamage = rangeCombatDamage(pDefender);

	iUnitDamage = std::max(pDefender->getDamage(), std::min((pDefender->getDamage() + iDamage), airCombatLimit()));

	szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_ARE_ATTACKED_BY_AIR", pDefender->getNameKey(), getNameKey(), -(((iUnitDamage - pDefender->getDamage()) * 100) / pDefender->maxHitPoints()));
	//red icon over attacking unit
	gDLL->getInterfaceIFace()->addMessage(pDefender->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_COMBAT", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), this->getX_INLINE(), this->getY_INLINE(), true, true);
	//white icon over defending unit
	gDLL->getInterfaceIFace()->addMessage(pDefender->getOwnerINLINE(), false, 0, L"", "AS2D_COMBAT", MESSAGE_TYPE_DISPLAY_ONLY, pDefender->getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_WHITE"), pDefender->getX_INLINE(), pDefender->getY_INLINE(), true, true);

	szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_ATTACK_BY_AIR", getNameKey(), pDefender->getNameKey(), -(((iUnitDamage - pDefender->getDamage()) * 100) / pDefender->maxHitPoints()));
	gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_COMBAT", MESSAGE_TYPE_INFO, pDefender->getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pPlot->getX_INLINE(), pPlot->getY_INLINE());

	collateralCombat(pPlot, pDefender);

	//set damage but don't update entity damage visibility
	pDefender->setDamage(iUnitDamage, getOwnerINLINE(), false);

	if (pPlot->isActiveVisible(false))
	{
		// Range strike entity mission
		CvMissionDefinition kDefiniton;
		kDefiniton.setMissionTime(GC.getMissionInfo(MISSION_RANGE_ATTACK).getTime() * gDLL->getSecsPerTurn());
		kDefiniton.setMissionType(MISSION_RANGE_ATTACK);
		kDefiniton.setPlot(pDefender->plot());
		kDefiniton.setUnit(BATTLE_UNIT_ATTACKER, this);
		kDefiniton.setUnit(BATTLE_UNIT_DEFENDER, pDefender);
		gDLL->getEntityIFace()->AddMission(&kDefiniton);

		//delay death
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       05/10/10                             jdog5000         */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
		pDefender->getGroup()->setMissionTimer(GC.getMissionInfo(MISSION_RANGE_ATTACK).getTime());
*/
		// mission timer is not used like this in any other part of code, so it might cause OOS
		// issues ... at worst I think unit dies before animation is complete, so no real
		// harm in commenting it out.
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
	}
/*************************************************************************************************/
/* Advanced Diplomacy         START                                                               */
/*************************************************************************************************/
	if (pDefender->getTeam() != getTeam() && pDefender->getTeam() != NO_TEAM && !GET_TEAM(getTeam()).isAtWar(pDefender->getTeam()))
	{
		GET_TEAM(pDefender->getTeam()).changeWarPretextAgainstCount(getTeam(), 1);
	}
/*************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/*************************************************************************************************/

	return true;
}

//------------------------------------------------------------------------------------------------
// FUNCTION:    CvUnit::planBattle
//! \brief      Determines in general how a battle will progress.
//!
//!				Note that the outcome of the battle is not determined here. This function plans
//!				how many sub-units die and in which 'rounds' of battle.
//! \param      kBattleDefinition The battle definition, which receives the battle plan.
//! \retval     The number of game turns that the battle should be given.
//------------------------------------------------------------------------------------------------
int CvUnit::planBattle( CvBattleDefinition & kBattleDefinition ) const
{
#define BATTLE_TURNS_SETUP 4
#define BATTLE_TURNS_ENDING 4
#define BATTLE_TURNS_MELEE 6
#define BATTLE_TURNS_RANGED 6
#define BATTLE_TURN_RECHECK 4

	int								aiUnitsBegin[BATTLE_UNIT_COUNT];
	int								aiUnitsEnd[BATTLE_UNIT_COUNT];
	int								aiToKillMelee[BATTLE_UNIT_COUNT];
	int								aiToKillRanged[BATTLE_UNIT_COUNT];
	CvBattleRoundVector::iterator	iIterator;
	int								i, j;
	bool							bIsLoser;
	int								iRoundIndex;
	int								iTotalRounds = 0;
	int								iRoundCheck = BATTLE_TURN_RECHECK;

	// Initial conditions
	kBattleDefinition.setNumRangedRounds(0);
	kBattleDefinition.setNumMeleeRounds(0);

	int iFirstStrikesDelta = kBattleDefinition.getFirstStrikes(BATTLE_UNIT_ATTACKER) - kBattleDefinition.getFirstStrikes(BATTLE_UNIT_DEFENDER);
	if (iFirstStrikesDelta > 0) // Attacker first strikes
	{
		int iKills = computeUnitsToDie( kBattleDefinition, true, BATTLE_UNIT_DEFENDER );
		kBattleDefinition.setNumRangedRounds(std::max(iFirstStrikesDelta, iKills / iFirstStrikesDelta));
	}
	else if (iFirstStrikesDelta < 0) // Defender first strikes
	{
		int iKills = computeUnitsToDie( kBattleDefinition, true, BATTLE_UNIT_ATTACKER );
		iFirstStrikesDelta = -iFirstStrikesDelta;
		kBattleDefinition.setNumRangedRounds(std::max(iFirstStrikesDelta, iKills / iFirstStrikesDelta));
	}
	increaseBattleRounds( kBattleDefinition);


	// Keep randomizing until we get something valid
	do
	{
		iRoundCheck++;
		if ( iRoundCheck >= BATTLE_TURN_RECHECK )
		{
			increaseBattleRounds( kBattleDefinition);
			iTotalRounds = kBattleDefinition.getNumRangedRounds() + kBattleDefinition.getNumMeleeRounds();
			iRoundCheck = 0;
		}

		// Make sure to clear the battle plan, we may have to do this again if we can't find a plan that works.
		kBattleDefinition.clearBattleRounds();

		// Create the round list
		CvBattleRound kRound;
		kBattleDefinition.setBattleRound(iTotalRounds, kRound);

		// For the attacker and defender
		for ( i = 0; i < BATTLE_UNIT_COUNT; i++ )
		{
			// Gather some initial information
			BattleUnitTypes unitType = (BattleUnitTypes) i;
			aiUnitsBegin[unitType] = kBattleDefinition.getUnit(unitType)->getSubUnitsAlive(kBattleDefinition.getDamage(unitType, BATTLE_TIME_BEGIN));
			aiToKillRanged[unitType] = computeUnitsToDie( kBattleDefinition, true, unitType);
			aiToKillMelee[unitType] = computeUnitsToDie( kBattleDefinition, false, unitType);
			aiUnitsEnd[unitType] = aiUnitsBegin[unitType] - aiToKillMelee[unitType] - aiToKillRanged[unitType];

			// Make sure that if they aren't dead at the end, they have at least one unit left
			if ( aiUnitsEnd[unitType] == 0 && !kBattleDefinition.getUnit(unitType)->isDead() )
			{
				aiUnitsEnd[unitType]++;
				if ( aiToKillMelee[unitType] > 0 )
				{
					aiToKillMelee[unitType]--;
				}
				else
				{
					aiToKillRanged[unitType]--;
				}
			}

			// If one unit is the loser, make sure that at least one of their units dies in the last round
			if ( aiUnitsEnd[unitType] == 0 )
			{
				kBattleDefinition.getBattleRound(iTotalRounds - 1).addNumKilled(unitType, 1);
				if ( aiToKillMelee[unitType] > 0)
				{
					aiToKillMelee[unitType]--;
				}
				else
				{
					aiToKillRanged[unitType]--;
				}
			}

			// Randomize in which round each death occurs
			bIsLoser = aiUnitsEnd[unitType] == 0;

			// Randomize the ranged deaths
			for ( j = 0; j < aiToKillRanged[unitType]; j++ )
			{
				iRoundIndex = GC.getGameINLINE().getSorenRandNum( range( kBattleDefinition.getNumRangedRounds(), 0, kBattleDefinition.getNumRangedRounds()), "Ranged combat death");
				kBattleDefinition.getBattleRound(iRoundIndex).addNumKilled(unitType, 1);
			}

			// Randomize the melee deaths
			for ( j = 0; j < aiToKillMelee[unitType]; j++ )
			{
				iRoundIndex = GC.getGameINLINE().getSorenRandNum( range( kBattleDefinition.getNumMeleeRounds() - (bIsLoser ? 1 : 2 ), 0, kBattleDefinition.getNumMeleeRounds()), "Melee combat death");
				kBattleDefinition.getBattleRound(kBattleDefinition.getNumRangedRounds() + iRoundIndex).addNumKilled(unitType, 1);
			}

			// Compute alive sums
			int iNumberKilled = 0;
			for(int j=0;j<kBattleDefinition.getNumBattleRounds();j++)
			{
				CvBattleRound &round = kBattleDefinition.getBattleRound(j);
				round.setRangedRound(j < kBattleDefinition.getNumRangedRounds());
				iNumberKilled += round.getNumKilled(unitType);
				round.setNumAlive(unitType, aiUnitsBegin[unitType] - iNumberKilled);
			}
		}

		// Now compute wave sizes
		for(int i=0;i<kBattleDefinition.getNumBattleRounds();i++)
		{
			CvBattleRound &round = kBattleDefinition.getBattleRound(i);
			round.setWaveSize(computeWaveSize(round.isRangedRound(), round.getNumAlive(BATTLE_UNIT_ATTACKER) + round.getNumKilled(BATTLE_UNIT_ATTACKER), round.getNumAlive(BATTLE_UNIT_DEFENDER) + round.getNumKilled(BATTLE_UNIT_DEFENDER)));
		}

		if ( iTotalRounds > 400 )
		{
			kBattleDefinition.setNumMeleeRounds(1);
			kBattleDefinition.setNumRangedRounds(0);
			break;
		}
	}
	while ( !verifyRoundsValid( kBattleDefinition ));

	//add a little extra time for leader to surrender
	bool attackerLeader = false;
	bool defenderLeader = false;
	bool attackerDie = false;
	bool defenderDie = false;
	int lastRound = kBattleDefinition.getNumBattleRounds() - 1;
	if(kBattleDefinition.getUnit(BATTLE_UNIT_ATTACKER)->getLeaderUnitType() != NO_UNIT)
		attackerLeader = true;
	if(kBattleDefinition.getUnit(BATTLE_UNIT_DEFENDER)->getLeaderUnitType() != NO_UNIT)
		defenderLeader = true;
	if(kBattleDefinition.getBattleRound(lastRound).getNumAlive(BATTLE_UNIT_ATTACKER) == 0)
		attackerDie = true;
	if(kBattleDefinition.getBattleRound(lastRound).getNumAlive(BATTLE_UNIT_DEFENDER) == 0)
		defenderDie = true;

	int extraTime = 0;
	if((attackerLeader && attackerDie) || (defenderLeader && defenderDie))
		extraTime = BATTLE_TURNS_MELEE;
	if(gDLL->getEntityIFace()->GetSiegeTower(kBattleDefinition.getUnit(BATTLE_UNIT_ATTACKER)->getUnitEntity()) || gDLL->getEntityIFace()->GetSiegeTower(kBattleDefinition.getUnit(BATTLE_UNIT_DEFENDER)->getUnitEntity()))
		extraTime = BATTLE_TURNS_MELEE;

	return BATTLE_TURNS_SETUP + BATTLE_TURNS_ENDING + kBattleDefinition.getNumMeleeRounds() * BATTLE_TURNS_MELEE + kBattleDefinition.getNumRangedRounds() * BATTLE_TURNS_MELEE + extraTime;
}

//------------------------------------------------------------------------------------------------
// FUNCTION:	CvBattleManager::computeDeadUnits
//! \brief		Computes the number of units dead, for either the ranged or melee portion of combat.
//! \param		kDefinition The battle definition.
//! \param		bRanged true if computing the number of units that die during the ranged portion of combat,
//!					false if computing the number of units that die during the melee portion of combat.
//! \param		iUnit The index of the unit to compute (BATTLE_UNIT_ATTACKER or BATTLE_UNIT_DEFENDER).
//! \retval		The number of units that should die for the given unit in the given portion of combat
//------------------------------------------------------------------------------------------------
int CvUnit::computeUnitsToDie( const CvBattleDefinition & kDefinition, bool bRanged, BattleUnitTypes iUnit ) const
{
	FAssertMsg( iUnit == BATTLE_UNIT_ATTACKER || iUnit == BATTLE_UNIT_DEFENDER, "Invalid unit index");

	BattleTimeTypes iBeginIndex = bRanged ? BATTLE_TIME_BEGIN : BATTLE_TIME_RANGED;
	BattleTimeTypes iEndIndex = bRanged ? BATTLE_TIME_RANGED : BATTLE_TIME_END;
	return kDefinition.getUnit(iUnit)->getSubUnitsAlive(kDefinition.getDamage(iUnit, iBeginIndex)) -
		kDefinition.getUnit(iUnit)->getSubUnitsAlive( kDefinition.getDamage(iUnit, iEndIndex));
}

//------------------------------------------------------------------------------------------------
// FUNCTION:    CvUnit::verifyRoundsValid
//! \brief      Verifies that all rounds in the battle plan are valid
//! \param      vctBattlePlan The battle plan
//! \retval     true if the battle plan (seems) valid, false otherwise
//------------------------------------------------------------------------------------------------
bool CvUnit::verifyRoundsValid( const CvBattleDefinition & battleDefinition ) const
{
	for(int i=0;i<battleDefinition.getNumBattleRounds();i++)
	{
		if(!battleDefinition.getBattleRound(i).isValid())
			return false;
	}
	return true;
}

//------------------------------------------------------------------------------------------------
// FUNCTION:    CvUnit::increaseBattleRounds
//! \brief      Increases the number of rounds in the battle.
//! \param      kBattleDefinition The definition of the battle
//------------------------------------------------------------------------------------------------
void CvUnit::increaseBattleRounds( CvBattleDefinition & kBattleDefinition ) const
{
	if ( kBattleDefinition.getUnit(BATTLE_UNIT_ATTACKER)->isRanged() && kBattleDefinition.getUnit(BATTLE_UNIT_DEFENDER)->isRanged())
	{
		kBattleDefinition.addNumRangedRounds(1);
	}
	else
	{
		kBattleDefinition.addNumMeleeRounds(1);
	}
}

//------------------------------------------------------------------------------------------------
// FUNCTION:    CvUnit::computeWaveSize
//! \brief      Computes the wave size for the round.
//! \param      bRangedRound true if the round is a ranged round
//! \param		iAttackerMax The maximum number of attackers that can participate in a wave (alive)
//! \param		iDefenderMax The maximum number of Defenders that can participate in a wave (alive)
//! \retval     The desired wave size for the given parameters
//------------------------------------------------------------------------------------------------
int CvUnit::computeWaveSize( bool bRangedRound, int iAttackerMax, int iDefenderMax ) const
{
	FAssertMsg( getCombatUnit() != NULL, "You must be fighting somebody!" );
	int aiDesiredSize[BATTLE_UNIT_COUNT];
	if ( bRangedRound )
	{
		aiDesiredSize[BATTLE_UNIT_ATTACKER] = getUnitInfo().getRangedWaveSize();
		aiDesiredSize[BATTLE_UNIT_DEFENDER] = getCombatUnit()->getUnitInfo().getRangedWaveSize();
	}
	else
	{
		aiDesiredSize[BATTLE_UNIT_ATTACKER] = getUnitInfo().getMeleeWaveSize();
		aiDesiredSize[BATTLE_UNIT_DEFENDER] = getCombatUnit()->getUnitInfo().getMeleeWaveSize();
	}

	aiDesiredSize[BATTLE_UNIT_DEFENDER] = aiDesiredSize[BATTLE_UNIT_DEFENDER] <= 0 ? iDefenderMax : aiDesiredSize[BATTLE_UNIT_DEFENDER];
	aiDesiredSize[BATTLE_UNIT_ATTACKER] = aiDesiredSize[BATTLE_UNIT_ATTACKER] <= 0 ? iDefenderMax : aiDesiredSize[BATTLE_UNIT_ATTACKER];
	return std::min( std::min( aiDesiredSize[BATTLE_UNIT_ATTACKER], iAttackerMax ), std::min( aiDesiredSize[BATTLE_UNIT_DEFENDER],
		iDefenderMax) );
}

bool CvUnit::isTargetOf(const CvUnit& attacker) const
{
	CvUnitInfo& attackerInfo = attacker.getUnitInfo();
	CvUnitInfo& ourInfo = getUnitInfo();

	if (!plot()->isCity(true, getTeam()))
	{
		if (NO_UNITCLASS != getUnitClassType() && attackerInfo.getTargetUnitClass(getUnitClassType()))
		{
			return true;
		}

		if (NO_UNITCOMBAT != getUnitCombatType() && attackerInfo.getTargetUnitCombat(getUnitCombatType()))
		{
			return true;
		}
	}

	if (NO_UNITCLASS != attackerInfo.getUnitClassType() && ourInfo.getDefenderUnitClass(attackerInfo.getUnitClassType()))
	{
		return true;
	}

	if (NO_UNITCOMBAT != attackerInfo.getUnitCombatType() && ourInfo.getDefenderUnitCombat(attackerInfo.getUnitCombatType()))
	{
		return true;
	}

	return false;
}

bool CvUnit::isEnemy(TeamTypes eTeam, const CvPlot* pPlot) const
{
	if (NULL == pPlot)
	{
		pPlot = plot();
	}

//FfH: Added by Kael 10/26/2007 (to prevent spinlocks when always hostile units attack barbarian allied teams)
    if (isAlwaysHostile(pPlot))
    {
        if (getTeam() != eTeam)
        {
            return true;
        }
    }
//FfH: End Add

	return (atWar(GET_PLAYER(getCombatOwner(eTeam, pPlot)).getTeam(), eTeam));
}

bool CvUnit::isPotentialEnemy(TeamTypes eTeam, const CvPlot* pPlot) const
{
	if (NULL == pPlot)
	{
		pPlot = plot();
	}

	// lfgr fix 03/2021: See isEnemy()
	if (isAlwaysHostile(pPlot))
	{
		if (getTeam() != eTeam)
		{
			return true;
		}
	}

	return (::isPotentialEnemy(GET_PLAYER(getCombatOwner(eTeam, pPlot)).getTeam(), eTeam));
}

bool CvUnit::isSuicide() const
{
	return (m_pUnitInfo->isSuicide() || getKamikazePercent() != 0);
}

int CvUnit::getDropRange() const
{
	return (m_pUnitInfo->getDropRange());
}

void CvUnit::getDefenderCombatValues(CvUnit& kDefender, const CvPlot* pPlot, int iOurStrength, int iOurFirepower, int& iTheirOdds, int& iTheirStrength, int& iOurDamage, int& iTheirDamage, CombatDetails* pTheirDetails) const
{
	iTheirStrength = kDefender.currCombatStr(pPlot, this, pTheirDetails);
	int iTheirFirepower = kDefender.currFirepower(pPlot, this);

	FAssert((iOurStrength + iTheirStrength) > 0);
	FAssert((iOurFirepower + iTheirFirepower) > 0);

	iTheirOdds = ((GC.defines.iCOMBAT_DIE_SIDES * iTheirStrength) / (iOurStrength + iTheirStrength));

	if (kDefender.isBarbarian())
	{
		if (GET_PLAYER(getOwnerINLINE()).getWinsVsBarbs() < GC.getHandicapInfo(GET_PLAYER(getOwnerINLINE()).getHandicapType()).getFreeWinsVsBarbs())
		{
			iTheirOdds = std::min((10 * GC.defines.iCOMBAT_DIE_SIDES) / 100, iTheirOdds);
		}
	}
	if (isBarbarian())
	{
		if (GET_PLAYER(kDefender.getOwnerINLINE()).getWinsVsBarbs() < GC.getHandicapInfo(GET_PLAYER(kDefender.getOwnerINLINE()).getHandicapType()).getFreeWinsVsBarbs())
		{
			iTheirOdds =  std::max((90 * GC.defines.iCOMBAT_DIE_SIDES) / 100, iTheirOdds);
		}
	}

	int iStrengthFactor = ((iOurFirepower + iTheirFirepower + 1) / 2);

	iOurDamage = std::max(1, ((GC.defines.iCOMBAT_DAMAGE * (iTheirFirepower + iStrengthFactor)) / (iOurFirepower + iStrengthFactor)));
	iTheirDamage = std::max(1, ((GC.defines.iCOMBAT_DAMAGE * (iOurFirepower + iStrengthFactor)) / (iTheirFirepower + iStrengthFactor)));
}

int CvUnit::getTriggerValue(EventTriggerTypes eTrigger, const CvPlot* pPlot, bool bCheckPlot) const
{
	CvEventTriggerInfo& kTrigger = GC.getEventTriggerInfo(eTrigger);
	if (kTrigger.getNumUnits() <= 0)
	{
		return MIN_INT;
	}

	if (isDead())
	{
		return MIN_INT;
	}

	if (!CvString(kTrigger.getPythonCanDoUnit()).empty())
	{
		long lResult;

		CyArgsList argsList;
		argsList.add(eTrigger);
		argsList.add(getOwnerINLINE());
		argsList.add(getID());

		gDLL->getPythonIFace()->callFunction(PYRandomEventModule, kTrigger.getPythonCanDoUnit(), argsList.makeFunctionArgs(), &lResult);

		if (0 == lResult)
		{
			return MIN_INT;
		}
	}

	if (kTrigger.getNumUnitsRequired() > 0)
	{
		bool bFoundValid = false;
		for (int i = 0; i < kTrigger.getNumUnitsRequired(); ++i)
		{
			if (getUnitClassType() == kTrigger.getUnitRequired(i))
			{
				bFoundValid = true;
				break;
			}
		}

		if (!bFoundValid)
		{
			return MIN_INT;
		}
	}

	if (bCheckPlot)
	{
		if (kTrigger.isUnitsOnPlot())
		{
			if (!plot()->canTrigger(eTrigger, getOwnerINLINE()))
			{
				return MIN_INT;
			}
		}
	}

	int iValue = 0;

	if (0 == getDamage() && kTrigger.getUnitDamagedWeight() > 0)
	{
		return MIN_INT;
	}

	iValue += getDamage() * kTrigger.getUnitDamagedWeight();

	iValue += getExperience() * kTrigger.getUnitExperienceWeight();

	if (NULL != pPlot)
	{
		iValue += plotDistance(getX_INLINE(), getY_INLINE(), pPlot->getX_INLINE(), pPlot->getY_INLINE()) * kTrigger.getUnitDistanceWeight();
	}

	return iValue;
}

bool CvUnit::canApplyEvent(EventTypes eEvent) const
{
	CvEventInfo& kEvent = GC.getEventInfo(eEvent);

	int iEventExperience = kEvent.getUnitExperience();
	if (0 != iEventExperience)
	{
		if (!canAcquirePromotionAny())
		{
			return false;
		}

		if ((iEventExperience + getExperience()) < 0)
		{
			return false;
		}
	}

	if (NO_PROMOTION != kEvent.getUnitPromotion())
	{

//FfH: Modified by Kael 10/29/2007
//		if (!canAcquirePromotion((PromotionTypes)kEvent.getUnitPromotion()))
//		{
//			return false;
//		}
        if (isHasPromotion((PromotionTypes)kEvent.getUnitPromotion()))
        {
            return false;
        }
//FfH: End Modify

	}

	if (kEvent.getUnitImmobileTurns() > 0)
	{
		if (!canAttack())
		{
			return false;
		}
	}

	return true;
}

void CvUnit::applyEvent(EventTypes eEvent)
{
	if (!canApplyEvent(eEvent))
	{
		return;
	}

	CvEventInfo& kEvent = GC.getEventInfo(eEvent);

	if (0 != kEvent.getUnitExperience())
	{
		setDamage(0);
		changeExperience(kEvent.getUnitExperience());
	}

	if (NO_PROMOTION != kEvent.getUnitPromotion())
	{

//FfH: Modified by Kael 02/02/2009 (if we spawn a new unit the promotion goes to the spawned unit, not to the eventtrigger target)
//		setHasPromotion((PromotionTypes)kEvent.getUnitPromotion(), true);
        if (kEvent.getUnitClass() == NO_UNITCLASS || kEvent.getNumUnits() == 0)
        {
            setHasPromotion((PromotionTypes)kEvent.getUnitPromotion(), true);
        }
//FfH: End Modify

	}

	if (kEvent.getUnitImmobileTurns() > 0)
	{
		changeImmobileTimer(kEvent.getUnitImmobileTurns());
		CvWString szText = gDLL->getText("TXT_KEY_EVENT_UNIT_IMMOBILE", getNameKey(), kEvent.getUnitImmobileTurns());
		gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szText, "AS2D_UNITGIFTED", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_UNIT_TEXT"), getX_INLINE(), getY_INLINE(), true, true);
	}

	CvWString szNameKey(kEvent.getUnitNameKey());

	if (!szNameKey.empty())
	{
		setName(gDLL->getText(kEvent.getUnitNameKey()));
	}

	if (kEvent.isDisbandUnit())
	{
		logBBAI("    Killing %S -- disbanded from event (Unit %d - plot: %d, %d)",
				getName().GetCString(), getID(), getX(), getY());
		kill(false);
	}
}

const CvArtInfoUnit* CvUnit::getArtInfo(int i, EraTypes eEra) const
{

//FfH: Added by Kael 10/26/2007
    if (getUnitArtStyleType() != NO_UNIT_ARTSTYLE)
    {
        return m_pUnitInfo->getArtInfo(i, eEra, (UnitArtStyleTypes) getUnitArtStyleType());
    }
//FfH: End Add

	return m_pUnitInfo->getArtInfo(i, eEra, (UnitArtStyleTypes) GC.getCivilizationInfo(getCivilizationType()).getUnitArtStyleType());
}

const TCHAR* CvUnit::getButton() const
{
	const CvArtInfoUnit* pArtInfo = getArtInfo(0, GET_PLAYER(getOwnerINLINE()).getCurrentRealEra());

	if (NULL != pArtInfo)
	{
		return pArtInfo->getButton();
	}

	return m_pUnitInfo->getButton();
}

//FfH: Modified by Kael 06/17/2009
//int CvUnit::getGroupSize() const
//{
//	return m_pUnitInfo->getGroupSize();
//}
int CvUnit::getGroupSize() const
{
    if (GC.getGameINLINE().isOption(GAMEOPTION_ADVENTURE_MODE))
    {
        return 1;
    }
	return m_iGroupSize;
}
//FfH: End Modify

int CvUnit::getGroupDefinitions() const
{
	return m_pUnitInfo->getGroupDefinitions();
}

int CvUnit::getUnitGroupRequired(int i) const
{
	return m_pUnitInfo->getUnitGroupRequired(i);
}

bool CvUnit::isRenderAlways() const
{
	return m_pUnitInfo->isRenderAlways();
}

float CvUnit::getAnimationMaxSpeed() const
{
	return m_pUnitInfo->getUnitMaxSpeed();
}

float CvUnit::getAnimationPadTime() const
{
	return m_pUnitInfo->getUnitPadTime();
}

const char* CvUnit::getFormationType() const
{
	return m_pUnitInfo->getFormationType();
}

bool CvUnit::isMechUnit() const
{
	return m_pUnitInfo->isMechUnit();
}

bool CvUnit::isRenderBelowWater() const
{
	return m_pUnitInfo->isRenderBelowWater();
}

int CvUnit::getRenderPriority(UnitSubEntityTypes eUnitSubEntity, int iMeshGroupType, int UNIT_MAX_SUB_TYPES) const
{
	if (eUnitSubEntity == UNIT_SUB_ENTITY_SIEGE_TOWER)
	{
		return (getOwner() * (GC.getNumUnitInfos() + 2) * UNIT_MAX_SUB_TYPES) + iMeshGroupType;
	}
	else
	{
		return (getOwner() * (GC.getNumUnitInfos() + 2) * UNIT_MAX_SUB_TYPES) + m_eUnitType * UNIT_MAX_SUB_TYPES + iMeshGroupType;
	}
}

bool CvUnit::isAlwaysHostile(const CvPlot* pPlot) const
{

//FfH: Added by Kael 09/15/2007
    if (isHiddenNationality())
    {
        return true;
    }
//FfH: End Add

	if (!m_pUnitInfo->isAlwaysHostile())
	{
		return false;
	}

	if (NULL != pPlot && pPlot->isCity(true, getTeam()))
	{
		return false;
	}

	return true;
}

bool CvUnit::verifyStackValid()
{
	if (!alwaysInvisible())
	{
		if (plot()->isVisibleEnemyUnit(this))
		{
			return jumpToNearestValidPlot();
		}
	}

	return true;
}


// Private Functions...

//check if quick combat
bool CvUnit::isCombatVisible(const CvUnit* pDefender) const
{
	bool bVisible = false;

	if (!m_pUnitInfo->isQuickCombat())
	{
		if (NULL == pDefender || !pDefender->getUnitInfo().isQuickCombat())
		{
			if (isHuman())
			{
				if (!GET_PLAYER(getOwnerINLINE()).isOption(PLAYEROPTION_QUICK_ATTACK))
				{
					bVisible = true;
				}
			}
			else if (NULL != pDefender && pDefender->isHuman())
			{
				if (!GET_PLAYER(pDefender->getOwnerINLINE()).isOption(PLAYEROPTION_QUICK_DEFENSE))
				{
					bVisible = true;
				}
			}
		}
	}

	return bVisible;
}

// used by the executable for the red glow and plot indicators
bool CvUnit::shouldShowEnemyGlow(TeamTypes eForTeam) const
{
	if (isDelayedDeath())
	{
		return false;
	}

	if (getDomainType() == DOMAIN_AIR)
	{
		return false;
	}

	if (!canFight())
	{
		return false;
	}

	CvPlot* pPlot = plot();
	if (pPlot == NULL)
	{
		return false;
	}

	TeamTypes ePlotTeam = pPlot->getTeam();
	if (ePlotTeam != eForTeam)
	{
		return false;
	}

	if (!isEnemy(ePlotTeam))
	{
		return false;
	}

	return true;
}

bool CvUnit::shouldShowFoundBorders() const
{
	return isFound();
}


void CvUnit::cheat(bool bCtrl, bool bAlt, bool bShift)
{
	if (gDLL->getChtLvl() > 0)
	{
		if (bCtrl)
		{
			setPromotionReady(true);
		}
	}
}

float CvUnit::getHealthBarModifier() const
{
	return (GC.getDefineFLOAT("HEALTH_BAR_WIDTH") / (GC.getGameINLINE().getBestLandUnitCombat() * 2));
}

void CvUnit::getLayerAnimationPaths(std::vector<AnimationPathTypes>& aAnimationPaths) const
{
	for (int i=0; i < GC.getNumPromotionInfos(); ++i)
	{
		PromotionTypes ePromotion = (PromotionTypes) i;
		if (isHasPromotion(ePromotion))
		{
			AnimationPathTypes eAnimationPath = (AnimationPathTypes) GC.getPromotionInfo(ePromotion).getLayerAnimationPath();
			if(eAnimationPath != ANIMATIONPATH_NONE)
			{
				aAnimationPaths.push_back(eAnimationPath);
			}
		}
	}
}

int CvUnit::getSelectionSoundScript() const
{
	int iScriptId = getArtInfo(0, GET_PLAYER(getOwnerINLINE()).getCurrentRealEra())->getSelectionSoundScriptId();
	if (iScriptId == -1)
	{
		iScriptId = GC.getCivilizationInfo(getCivilizationType()).getSelectionSoundScriptId();
	}
	return iScriptId;
}

//FfH Spell System: Added by Kael 07/23/2007
bool CvUnit::canCastWithCurrentPromotions( SpellTypes eSpell ) const // lfgr fix 03/2021
{
	// LFGR_TODO: Cache this?
	CvSpellInfo& kSpell = GC.getSpellInfo(eSpell);

	if (isCastingBlocked())
	{
		return false;
	}

	// objects cant cast spells
	if (getUnitInfo().isObject())
	{
		// unless the spell is designed for that object (ie. Golden Hammer)
		if (kSpell.getUnitPrereq() != NO_UNIT)
		{
			if (kSpell.getUnitPrereq() != getUnitType())
			{
				return false;
			}
		}
		else
		{
			return false;
		}
	}

	if (kSpell.getPromotionPrereq1() != NO_PROMOTION)
	{
		if (!isHasPromotion((PromotionTypes)kSpell.getPromotionPrereq1()))
		{
			return false;
		}
	}
	if (kSpell.getPromotionPrereq2() != NO_PROMOTION)
	{
		if (!isHasPromotion((PromotionTypes)kSpell.getPromotionPrereq2()))
		{
			return false;
		}
	}
	if (kSpell.getUnitClassPrereq() != NO_UNITCLASS)
	{
		if (getUnitClassType() != (UnitClassTypes)kSpell.getUnitClassPrereq())
		{
			return false;
		}
	}
	if (kSpell.getUnitPrereq() != NO_UNIT)
	{
		if (getUnitType() != (UnitTypes)kSpell.getUnitPrereq())
		{
			return false;
		}
	}
	if (kSpell.getUnitCombatPrereq() != NO_UNITCOMBAT)
	{
		if (getUnitCombatType() != (UnitCombatTypes)kSpell.getUnitCombatPrereq())
		{
			return false;
		}
	}
	if (kSpell.getCivilizationPrereq() != NO_CIVILIZATION)
	{
		if (getCivilizationType() != (CivilizationTypes)kSpell.getCivilizationPrereq())
		{
			return false;
		}
	}

	if (kSpell.getConvertUnitType() != NO_UNIT)
	{
		if (getUnitType() == (UnitTypes)kSpell.getConvertUnitType())
		{
			return false;
		}
	}

	if (kSpell.isCasterMustBeAlive())
	{
		if (!isAlive())
		{
			return false;
		}
	}

	if (kSpell.getReligionPrereq() != NO_RELIGION)
	{
		if (getReligion() != (ReligionTypes)kSpell.getReligionPrereq())
		{
			return false;
		}
	}

	if (kSpell.getCasterMinLevel() != 0)
	{
		if (getLevel() < kSpell.getCasterMinLevel())
		{
			return false;
		}
	}

	return true;
}

bool CvUnit::canCast(int spell, bool bTestVisible)
{
    SpellTypes eSpell = (SpellTypes)spell;
	CvSpellInfo& kSpell = GC.getSpellInfo(eSpell);
    CvPlot* pPlot = plot();
    CvUnit* pLoopUnit;
    CLLNode<IDInfo>* pUnitNode;
    bool bValid = false;

	// lfgr 03/2021: Moved some stuff to canCastWithCurrentPromotions

	if( !canCastWithCurrentPromotions( eSpell ) ) {
		return false;
	}

	if (getImmobileTimer() > 0 && !isHeld())
	{
		return false;
	}

	if (kSpell.isGlobal())
    {
        if (GC.getGameINLINE().isOption(GAMEOPTION_NO_WORLD_SPELLS))
        {
            return false;
        }
        if (GET_PLAYER(getOwnerINLINE()).isFeatAccomplished(FEAT_GLOBAL_SPELL))
        {
            return false;
        }
		
		// MNAI
		// Revolutions - Rebels cant cast World spells
		if (GET_PLAYER(getOwnerINLINE()).isRebel())
		{
			return false;
		}

		// Puppet States - Puppet States cant cast World spells
		if (GET_PLAYER(getOwnerINLINE()).isPuppetState())
		{
			return false;
		}
		// End MNAI
    }

	if (GET_PLAYER(getOwnerINLINE()).getDisableSpellcasting() > 0)
    {
        if (!kSpell.isAbility())
        {
            return false;
        }
    }

	// Illusions cannot pickup or take equipment; they also cannot Add to Flesh Golem or Wolf Pack
	if (isIllusionary())
	{ // LFGR_TODO: This should not be "hardcoded"
		if (kSpell.getUnitInStackPrereq() != NO_UNIT)
		{
			return false;
		}

		if (kSpell.getPromotionInStackPrereq() != NO_PROMOTION)
		{
			return false;
		}
	}

    if (kSpell.getBuildingPrereq() != NO_BUILDING)
    {
        if (!pPlot->isCity())
        {
            return false;
        }
        if (pPlot->getPlotCity()->getNumBuilding((BuildingTypes)kSpell.getBuildingPrereq()) == 0)
        {
            return false;
        }
    }
    if (kSpell.getBuildingClassOwnedPrereq() != NO_BUILDINGCLASS)
    {
        //if (GET_PLAYER(getOwnerINLINE()).getBuildingClassCount((BuildingClassTypes)kSpell.getBuildingClassOwnedPrereq())  == 0)
		if (GET_TEAM(getTeam()).getBuildingClassCount((BuildingClassTypes)kSpell.getBuildingClassOwnedPrereq()) == 0)
        {
            return false;
        }
    }
    if (kSpell.getCorporationPrereq() != NO_CORPORATION)
    {
        if (!pPlot->isCity())
        {
            return false;
        }
        if (!pPlot->getPlotCity()->isHasCorporation((CorporationTypes)kSpell.getCorporationPrereq()))
        {
            return false;
        }
    }
    if (kSpell.getImprovementPrereq() != NO_IMPROVEMENT)
    {
        if (pPlot->getImprovementType() != kSpell.getImprovementPrereq())
        {
            return false;
        }
    }
    if (kSpell.getStateReligionPrereq() != NO_RELIGION)
    {
        if (GET_PLAYER(getOwnerINLINE()).getStateReligion() != (ReligionTypes)kSpell.getStateReligionPrereq())
        {
            return false;
        }
    }
    if (kSpell.getTechPrereq() != NO_TECH)
    {
        if (!GET_TEAM(getTeam()).isHasTech((TechTypes)kSpell.getTechPrereq()))
        {
            return false;
        }
    }

	// VOTE_CLEANUP 04/2020 lfgr
	if( kSpell.getVotePrereq() != NO_VOTE ) {
		bool bValid = false;

		// Vote must be passed
		VoteTypes eVote = (VoteTypes) kSpell.getVotePrereq();
		if( GC.getGameINLINE().getVoteOutcome( eVote ) == PLAYER_VOTE_YES ) {
			CvVoteInfo& kVoteInfo = GC.getVoteInfo( eVote );

			// Player must be on a council that provides the vote
			for( int iVoteSource = 0; iVoteSource < GC.getNumVoteSourceInfos(); iVoteSource++ ) {
				if( kVoteInfo.isVoteSourceType( iVoteSource )
					&& GET_PLAYER( getOwnerINLINE() ).isFullMember( (VoteSourceTypes) iVoteSource ) ) {
					bValid = true;
				}
			}
		}

		if( !bValid ) {
			return false;
		}
	}
	// VOTE_CLEANUP end
	/*
    if (GC.getUnitInfo((UnitTypes)getUnitType()).getEquipmentPromotion() != NO_PROMOTION)
    {
        if (kSpell.getUnitClassPrereq() != NO_UNITCLASS)
		{
			if (kSpell.getUnitClassPrereq() != getUnitClassType())
	        {
		        return false;
			}
		}
    }
	*/
    if (kSpell.isCasterNoDuration())
    {
        if (getDuration() != 0)
        {
            return false;
        }
    }
    if (kSpell.getPromotionInStackPrereq() != NO_PROMOTION)
    {
        if (isHasPromotion((PromotionTypes)kSpell.getPromotionInStackPrereq()))
        {
            return false;
        }
        bValid = false;
        pUnitNode = pPlot->headUnitNode();
        while (pUnitNode != NULL)
        {
            pLoopUnit = ::getUnit(pUnitNode->m_data);
            pUnitNode = pPlot->nextUnitNode(pUnitNode);
            if (pLoopUnit->isHasPromotion((PromotionTypes)kSpell.getPromotionInStackPrereq()))
            {
                if (getOwner() == pLoopUnit->getOwner())
                {
                    bValid = true;
                }
            }
        }
        if (bValid == false)
        {
            return false;
        }
    }
    if (kSpell.getUnitInStackPrereq() != NO_UNIT)
    {
        if (getUnitType() == kSpell.getUnitInStackPrereq())
        {
            return false;
        }
        bValid = false;
        pUnitNode = pPlot->headUnitNode();
        while (pUnitNode != NULL)
        {
            pLoopUnit = ::getUnit(pUnitNode->m_data);
            pUnitNode = pPlot->nextUnitNode(pUnitNode);
            if (pLoopUnit->getUnitType() == (UnitTypes)kSpell.getUnitInStackPrereq())
            {
                if (getOwner() == pLoopUnit->getOwner())
                {
					if (!pLoopUnit->isDelayedDeath())
					{
						bValid = true;
						break;
					}
				}
			}
		}
		if (bValid == false)
		{
			return false;
		}
	}
	if (bTestVisible)
	{
		if (kSpell.isDisplayWhenDisabled())
		{
			return true;
		}
	}
	if (!kSpell.isIgnoreHasCasted())
	{
		if (isHasCasted())
		{
			return false;
		}
	}
	// MNAI begin - eveything before this point (right after the check to bTestVisible and isHasCasted()) shall be considered
	// a hard requirement that PyAlternateReq cannot get around. Consider carefully what should go before or after this.
	if (!CvString(kSpell.getPyAlternateReq()).empty())
    {
        CyUnit* pyUnit = new CyUnit(this);
        CyArgsList argsList;
        argsList.add(gDLL->getPythonIFace()->makePythonObject(pyUnit));	// pass in unit class
        argsList.add(spell);//the spell #
        long lResult=0;
        gDLL->getPythonIFace()->callFunction(PYSpellModule, "canCastAlternate", argsList.makeFunctionArgs(), &lResult);
        delete pyUnit; // python fxn must not hold on to this pointer
        if (lResult != 0)
        {
            return true;
        }
    }
	// MNAI end
	if (kSpell.getFeatureOrPrereq1() != NO_FEATURE)
	{
		if (pPlot->getFeatureType() != kSpell.getFeatureOrPrereq1())
		{
			if (kSpell.getFeatureOrPrereq2() == NO_FEATURE || pPlot->getFeatureType() != kSpell.getFeatureOrPrereq2())
			{
				return false;
			}
		}
	}
	if (kSpell.isAdjacentToWaterOnly())
	{
		if (!pPlot->isAdjacentToWater())
		{
			return false;
		}
	}
	if (kSpell.isInBordersOnly())
	{
		if (pPlot->getOwner() != getOwner())
		{
			return false;
		}
	}
	if (kSpell.isInCityOnly())
	{
		if (!pPlot->isCity())
		{
			return false;
		}
	}
	if (kSpell.getChangePopulation() != 0)
	{
		if (!pPlot->isCity())
		{
			return false;
		}
		if (pPlot->getPlotCity()->getPopulation() <= (-1 * kSpell.getChangePopulation()))
		{
			return false;
		}
	}
	if( !bTestVisible &&
			GET_PLAYER(getOwnerINLINE()).getGold() < info_utils::getRealSpellCost( getOwnerINLINE(), eSpell ) )
	{
		return false; // Disable, but don't hide if not enough gold.
	}
	if (kSpell.isRemoveHasCasted())
	{
		if (!isHasCasted())
		{
			return false;
		}
		if (getDuration() > 0)
		{
			return false;
		}
	}

//>>>>Unofficial Bug Fix: Added by Denev 2009/12/03
//*** Team Unit or National Unit is limited.
	if (kSpell.getConvertUnitType() != NO_UNIT)
	{
		const UnitClassTypes eUnitClass = (UnitClassTypes)GC.getUnitInfo((UnitTypes)kSpell.getConvertUnitType()).getUnitClassType();
		const int iTeamLimit	= GC.getUnitClassInfo(eUnitClass).getMaxTeamInstances();
		const int iPlayerLimit	= GC.getUnitClassInfo(eUnitClass).getMaxPlayerInstances();
		if (iTeamLimit != -1)
		{
			if (iTeamLimit <= GET_TEAM(getTeam()).getUnitClassCount(eUnitClass))
			{
				return false;
			}
		}
		if (iPlayerLimit != -1)
		{
			if (iPlayerLimit <= GET_PLAYER(getOwnerINLINE()).getUnitClassCount(eUnitClass))
			{
				return false;
			}
		}
	}
//<<<<Unofficial Bug Fix: End Add
	if (kSpell.getCreateUnitType() != NO_UNIT)
	{
		if (!canCreateUnit(spell))
		{
			return false;
		}
	}
	if (kSpell.getCreateBuildingType() != NO_BUILDING)
	{
		if (!canCreateBuilding(spell))
		{
			return false;
		}
	}
	// MNAI begin
	/*
	if (pPlot->getFeatureType() != NO_FEATURE)
	{
		if (kSpell.isFeatureInvalid(pPlot->getFeatureType()))
		{
			return false;
		}
	}
	*/
	// MNAI end
	if (!CvString(kSpell.getPyRequirement()).empty())
    {
        CyUnit* pyUnit = new CyUnit(this);
        CyArgsList argsList;
        argsList.add(gDLL->getPythonIFace()->makePythonObject(pyUnit));	// pass in unit class
        argsList.add(spell);//the spell #
        long lResult=0;
        gDLL->getPythonIFace()->callFunction(PYSpellModule, "canCast", argsList.makeFunctionArgs(), &lResult);
        delete pyUnit; // python fxn must not hold on to this pointer
        if (lResult == 0)
        {
            return false;
        }
        return true;
    }

	// From here on, we only check if the spell does something at all.

	if( kSpell.getCost() < 0 ) {
		return true; // Gives gold
	}

    if (kSpell.isRemoveHasCasted())
    {
        if (isHasCasted())
        {
            return true;
        }
    }
    if (kSpell.getAddPromotionType1() != NO_PROMOTION)
    {
        if (canAddPromotion(spell))
        {
            return true;
        }
    }
    if (kSpell.getRemovePromotionType1() != NO_PROMOTION)
    {
        if (canRemovePromotion(spell))
        {
            return true;
        }
    }
    if (kSpell.getConvertUnitType() != NO_UNIT)
    {
        return true;
    }
	// MNAI begin
	/*
	if (canTerraform(spell, pPlot))
	{
		return true;
	}
	*/
	// MNAI end
    if (kSpell.getCreateFeatureType() != NO_FEATURE)
    {
        if (canCreateFeature(spell))
        {
            return true;
        }
    }
    if (kSpell.getCreateImprovementType() != NO_IMPROVEMENT)
    {
        if (canCreateImprovement(spell))
        {
            return true;
        }
    }
    if (kSpell.getSpreadReligion() != NO_RELIGION)
    {
        if (canSpreadReligion(spell))
        {
            return true;
        }
    }
    if (kSpell.getCreateBuildingType() != NO_BUILDING)
    {
        return true;
    }
    if (kSpell.getCreateUnitType() != NO_UNIT)
    {
        return true;
    }
    if (kSpell.getDamage() != 0)
    {
        return true;
    }
    if (kSpell.isDispel())
    {
        if (canDispel(spell))
        {
            return true;
        }
    }
    if (kSpell.getImmobileTurns() > 0)
    {
        if (canImmobile(spell))
        {
            return true;
        }
    }
    if (kSpell.isPush())
    {
        if (canPush(spell))
        {
            return true;
        }
    }
    if (kSpell.getChangePopulation() > 0)
    {
        return true;
    }
	if (!CvString(kSpell.getPyResult()).empty() && CvString(kSpell.getPyAlternateReq()).empty())
    {
        return true;
    }

    return false;
}

bool CvUnit::hasActiveSummon( UnitClassTypes eUnitClass ) const
{
	int iLoop;
	CvUnit* pLoopUnit;
	CvPlayer& kPlayer = GET_PLAYER(getOwnerINLINE());
	for( pLoopUnit = kPlayer.firstUnit(&iLoop); pLoopUnit != NULL; pLoopUnit = kPlayer.nextUnit(&iLoop) )
	{
		if( pLoopUnit->getUnitClassType() == eUnitClass && pLoopUnit->getSummoner() == getID() )
		{
			return true;
		}
	}

	return false;
}

bool CvUnit::canCreateUnit(int spell) const
{
	if (getDuration() > 0) // to prevent summons summoning spinlocks
	{
		if (GC.getSpellInfo((SpellTypes)spell).getCreateUnitType() == getUnitType())
		{
			return false;
		}
	}
//>>>>Unofficial Bug Fix: Deleted by Denev 2010/02/22
/*
	if (plot()->isVisibleEnemyUnit(getOwnerINLINE())) // keeps invisible units from CtDing summoning on top of enemies
	{
		return false;
	}
*/
//<<<<Unofficial Bug Fix: End Delete
	if (GC.getSpellInfo((SpellTypes)spell).isPermanentUnitCreate())
	{
		UnitClassTypes eCreatedUnitClass = (UnitClassTypes)GC.getUnitInfo((UnitTypes)GC.getSpellInfo((SpellTypes)spell).getCreateUnitType()).getUnitClassType();
		if( GC.defines.iCOUNT_SUMMONS_PER_CASTER )
		{
			// lfgr 11/2021: Only allow one summon (of each unitclass) per caster
			if( hasActiveSummon( eCreatedUnitClass ) )
			{
				return false;
			}
		}
		else
		{
			// lfgr 11/2021: Count number of summons (of correct unitclass) against number of eligible summoners (original behavior)
			CvPlayer& kPlayer = GET_PLAYER(getOwnerINLINE());
			if( kPlayer.getCasterCount( (SpellTypes) spell ) <= kPlayer.getUnitClassCount( eCreatedUnitClass ) )
			{
				return false;
			}
		}
	}
	return true;
}

bool CvUnit::canAddPromotion(int spell)
{
   	PromotionTypes ePromotion1 = (PromotionTypes)GC.getSpellInfo((SpellTypes)spell).getAddPromotionType1();
   	PromotionTypes ePromotion2 = (PromotionTypes)GC.getSpellInfo((SpellTypes)spell).getAddPromotionType2();
   	PromotionTypes ePromotion3 = (PromotionTypes)GC.getSpellInfo((SpellTypes)spell).getAddPromotionType3();
    if (GC.getSpellInfo((SpellTypes)spell).isBuffCasterOnly())
    {
		if( ePromotion1 != NO_PROMOTION && canBeGrantedPromotion( ePromotion1 ) ) {
			return true;
		}
		if( ePromotion2 != NO_PROMOTION && canBeGrantedPromotion( ePromotion2 ) ) {
			return true;
		}
		if( ePromotion3 != NO_PROMOTION && canBeGrantedPromotion( ePromotion3 ) ) {
			return true;
		}
        return false;
    }
	CvUnit* pLoopUnit;
    CvPlot* pLoopPlot;
    int iRange = GC.getSpellInfo((SpellTypes)spell).getRange();
    for (int i = -iRange; i <= iRange; ++i)
    {
        for (int j = -iRange; j <= iRange; ++j)
        {
            pLoopPlot = ::plotXY(plot()->getX_INLINE(), plot()->getY_INLINE(), i, j);
            if (NULL != pLoopPlot)
            {
                CLLNode<IDInfo>* pUnitNode = pLoopPlot->headUnitNode();
                while (pUnitNode != NULL)
                {
                    pLoopUnit = ::getUnit(pUnitNode->m_data);
                    pUnitNode = pLoopPlot->nextUnitNode(pUnitNode);
                    if (!pLoopUnit->isImmuneToSpell(this, spell))
                    {
						if( ePromotion1 != NO_PROMOTION && pLoopUnit->canBeGrantedPromotion( ePromotion1, true ) ) {
							return true;
						}
						if( ePromotion2 != NO_PROMOTION && pLoopUnit->canBeGrantedPromotion( ePromotion2, true ) ) {
							return true;
						}
						if( ePromotion3 != NO_PROMOTION && pLoopUnit->canBeGrantedPromotion( ePromotion3, true ) ) {
							return true;
						}
                    }
                }
            }
		}
	}
	return false;
}

bool CvUnit::canCreateBuilding(int spell) const
{
    if (!plot()->isCity())
    {
        return false;
    }
    if (plot()->getPlotCity()->getNumBuilding((BuildingTypes)GC.getSpellInfo((SpellTypes)spell).getCreateBuildingType()) > 0)
    {
        return false;
    }
    return true;
}

bool CvUnit::canCreateFeature(int spell) const
{
    if (plot()->isCity())
    {
        return false;
    }
    if (!plot()->canHaveFeature((FeatureTypes)GC.getSpellInfo((SpellTypes)spell).getCreateFeatureType()))
    {
        return false;
    }
    if (plot()->getFeatureType() != NO_FEATURE)
    {
        return false;
    }
    if (plot()->getImprovementType() != NO_IMPROVEMENT)
    {
        if (!GC.getCivilizationInfo(getCivilizationType()).isMaintainFeatures(GC.getSpellInfo((SpellTypes)spell).getCreateFeatureType()))
        {
            return false;
        }
    }
    return true;
}

bool CvUnit::canCreateImprovement(int spell) const
{
    if (plot()->isCity())
    {
        return false;
    }
    if (!plot()->canHaveImprovement((ImprovementTypes)GC.getSpellInfo((SpellTypes)spell).getCreateImprovementType()))
    {
        return false;
    }
    if (plot()->getImprovementType() != NO_IMPROVEMENT)
    {
        return false;
    }
    return true;
}

bool CvUnit::canDispel(int spell)
{
    int iRange = GC.getSpellInfo((SpellTypes)spell).getRange();
	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pLoopUnit;
	CvPlot* pLoopPlot;
    for (int i = -iRange; i <= iRange; ++i)
    {
        for (int j = -iRange; j <= iRange; ++j)
        {
            pLoopPlot = ::plotXY(plot()->getX_INLINE(), plot()->getY_INLINE(), i, j);
            if (NULL != pLoopPlot)
            {
                pUnitNode = pLoopPlot->headUnitNode();
                while (pUnitNode != NULL)
                {
                    pLoopUnit = ::getUnit(pUnitNode->m_data);
                    pUnitNode = pLoopPlot->nextUnitNode(pUnitNode);
                    if (!pLoopUnit->isImmuneToSpell(this, spell))
                    {
                        for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
                        {
                            if (pLoopUnit->isHasPromotion((PromotionTypes)iI))
                            {
                                if (GC.getPromotionInfo((PromotionTypes)iI).isDispellable())
                                {
                                    if ((GC.getPromotionInfo((PromotionTypes)iI).getAIWeight() < 0 && pLoopUnit->getTeam() == getTeam())
                                    || (GC.getPromotionInfo((PromotionTypes)iI).getAIWeight() > 0 && pLoopUnit->isEnemy(getTeam())))
                                    {
                                        return true;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return false;
}

bool CvUnit::canImmobile(int spell)
{
    int iRange = GC.getSpellInfo((SpellTypes)spell).getRange();
	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pLoopUnit;
	CvPlot* pLoopPlot;
    for (int i = -iRange; i <= iRange; ++i)
    {
        for (int j = -iRange; j <= iRange; ++j)
        {
            pLoopPlot = ::plotXY(plot()->getX_INLINE(), plot()->getY_INLINE(), i, j);
            if (NULL != pLoopPlot)
            {
                pUnitNode = pLoopPlot->headUnitNode();
                while (pUnitNode != NULL)
                {
                    pLoopUnit = ::getUnit(pUnitNode->m_data);
                    pUnitNode = pLoopPlot->nextUnitNode(pUnitNode);
                    if (!pLoopUnit->isImmuneToSpell(this, spell))
                    {
                        return true;
                    }
                }
            }
        }
    }
    return false;
}

bool CvUnit::canPush(int spell)
{
    int iRange = GC.getSpellInfo((SpellTypes)spell).getRange();
	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pLoopUnit;
	CvPlot* pLoopPlot;
    for (int i = -iRange; i <= iRange; ++i)
    {
        for (int j = -iRange; j <= iRange; ++j)
        {
            pLoopPlot = ::plotXY(plot()->getX_INLINE(), plot()->getY_INLINE(), i, j);
            if (NULL != pLoopPlot)
            {
                if (!pLoopPlot->isCity())
                {
                    pUnitNode = pLoopPlot->headUnitNode();
                    while (pUnitNode != NULL)
                    {
                        pLoopUnit = ::getUnit(pUnitNode->m_data);
                        pUnitNode = pLoopPlot->nextUnitNode(pUnitNode);
                        if (!pLoopUnit->isImmuneToSpell(this, spell))
                        {
                            return true;
                        }
                    }
                }
            }
        }
    }
    return false;
}

bool CvUnit::canRemovePromotion(int spell)
{
   	PromotionTypes ePromotion1 = (PromotionTypes)GC.getSpellInfo((SpellTypes)spell).getRemovePromotionType1();
   	PromotionTypes ePromotion2 = (PromotionTypes)GC.getSpellInfo((SpellTypes)spell).getRemovePromotionType2();
   	PromotionTypes ePromotion3 = (PromotionTypes)GC.getSpellInfo((SpellTypes)spell).getRemovePromotionType3();
    if (plot()->isVisibleEnemyUnit(getOwnerINLINE()))
    {
        if (ePromotion1 == (PromotionTypes)GC.defines.iHIDDEN_NATIONALITY_PROMOTION)
        {
            return false;
        }
        if (ePromotion2 == (PromotionTypes)GC.defines.iHIDDEN_NATIONALITY_PROMOTION)
        {
            return false;
        }
        if (ePromotion3 == (PromotionTypes)GC.defines.iHIDDEN_NATIONALITY_PROMOTION)
        {
            return false;
        }
    }
    if (GC.getSpellInfo((SpellTypes)spell).isBuffCasterOnly())
    {
        if (ePromotion1 != NO_PROMOTION)
        {
            if (isHasPromotion(ePromotion1))
            {
                return true;
            }
        }
        if (ePromotion2 != NO_PROMOTION)
        {
            if (isHasPromotion(ePromotion2))
            {
                return true;
            }
        }
        if (ePromotion3 != NO_PROMOTION)
        {
            if (isHasPromotion(ePromotion3))
            {
                return true;
            }
        }
        return false;
    }
	CvUnit* pLoopUnit;
    CvPlot* pLoopPlot;
    int iRange = GC.getSpellInfo((SpellTypes)spell).getRange();
    for (int i = -iRange; i <= iRange; ++i)
    {
        for (int j = -iRange; j <= iRange; ++j)
        {
            pLoopPlot = ::plotXY(plot()->getX_INLINE(), plot()->getY_INLINE(), i, j);
            if (NULL != pLoopPlot)
            {
                CLLNode<IDInfo>* pUnitNode = pLoopPlot->headUnitNode();
                while (pUnitNode != NULL)
                {
                    pLoopUnit = ::getUnit(pUnitNode->m_data);
                    pUnitNode = pLoopPlot->nextUnitNode(pUnitNode);
                    if (!pLoopUnit->isImmuneToSpell(this, spell))
                    {
                        if (ePromotion1 != NO_PROMOTION)
                        {
                            if (pLoopUnit->isHasPromotion(ePromotion1))
                            {
                                return true;
                            }
                        }
                        if (ePromotion2 != NO_PROMOTION)
                        {
                            if (pLoopUnit->isHasPromotion(ePromotion2))
                            {
                                return true;
                            }
                        }
                        if (ePromotion3 != NO_PROMOTION)
                        {
                            if (pLoopUnit->isHasPromotion(ePromotion3))
                            {
                                return true;
                            }
                        }
                    }
                }
            }
		}
	}
	return false;
}

bool CvUnit::canSpreadReligion(int spell) const
{
   	ReligionTypes eReligion = (ReligionTypes)GC.getSpellInfo((SpellTypes)spell).getSpreadReligion();
	if (eReligion == NO_RELIGION)
	{
		return false;
	}
	CvCity* pCity = plot()->getPlotCity();
	if (pCity == NULL)
	{
		return false;
	}
	if (pCity->isHasReligion(eReligion))
	{
		return false;
	}
	return true;
}

// lfgr 04/2021
// lfgr TODO: Cache?
bool CvUnit::canCastAnything()
{
	for( int eSpell = 0; eSpell < GC.getNumSpellInfos(); eSpell++ )
	{
		if( canCast( eSpell, false ) )
		{
			return true;
		}
	}
	return false;
}

// MNAI begin
/*
bool CvUnit::canTerraform(int spell, const CvPlot* pPlot) const
{
	CvSpellInfo& kSpell = GC.getSpellInfo((SpellTypes) spell);
	int iRange = kSpell.getRange();
	for (int iDX = -iRange; iDX <= iRange; ++iDX)
	{
		for (int iDY = -iRange; iDY <= iRange; ++iDY)
		{
			CvPlot* pLoopPlot = plotXY(pPlot->getX_INLINE(), pPlot->getY_INLINE(), iDX, iDY);
			if (pLoopPlot != NULL)
			{
				FeatureTypes eFeature = pLoopPlot->getFeatureType();
				if (eFeature != NO_FEATURE)
				{
					if (kSpell.isFeatureInvalid(eFeature))
					{
						continue;
					}
					if (kSpell.getFeatureConvert(eFeature) != eFeature)
					{
						return true;
					}
				}
				if (kSpell.getTerrainConvert(pLoopPlot->getTerrainType()) != NO_TERRAIN)
				{
					return true;
				}
			}
		}
	}
	return false;
}
*/
// MNAI end

bool CvUnit::canBeGrantedPromotion( PromotionTypes ePromotion, bool bCheckUnitCombat ) const {
	FAssert( 0 <= ePromotion );
	FAssert( ePromotion <= GC.getNumPromotionInfos() );

	if( isHasPromotion( ePromotion ) ) {
		return false;
	}

	if( isPromotionImmune( ePromotion ) ) {
		return false;
	}

	if( getDamage() == 0 && GC.getPromotionInfo( ePromotion ).isRemovedWhenHealed() ) {
		return false;
	}

	if( bCheckUnitCombat ) {
		if( getUnitCombatType() == NO_UNITCOMBAT ) {
			return false;
		}

		if( ! GC.getPromotionInfo( ePromotion ).getUnitCombat( getUnitCombatType() ) ) {
			return false;
		}
	}

	return true;
}

void CvUnit::cast(int spell)
{
	CvWString szBuffer;

	CvSpellInfo &kSpellInfo = GC.getSpellInfo((SpellTypes)spell);

	if( gUnitLogLevel > 2 )
	{
		logBBAI("     %S (%d) casting %S (plot %d, %d)\n",  getName().GetCString(), getID(), kSpellInfo.getDescription(), getX(), getY());
	}

    if (kSpellInfo.isHasCasted())
    {
        setHasCasted(true);
    }
    for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
    {
        if (isHasPromotion((PromotionTypes)iI))
        {
            if (GC.getPromotionInfo((PromotionTypes)iI).isRemovedByCasting())
            {
                setHasPromotion((PromotionTypes)iI, false);
            }
        }
    }
    if (kSpellInfo.isGlobal())
    {
        GET_PLAYER(getOwnerINLINE()).setFeatAccomplished(FEAT_GLOBAL_SPELL, true);
		for (int iPlayer = 0; iPlayer < MAX_CIV_PLAYERS; ++iPlayer)
		{
		    if (GET_PLAYER((PlayerTypes)iPlayer).isAlive())
		    {
                gDLL->getInterfaceIFace()->addMessage((PlayerTypes)iPlayer, false, GC.getEVENT_MESSAGE_TIME(), gDLL->getText("TXT_KEY_MESSAGE_GLOBAL_SPELL", kSpellInfo.getDescription()), "AS2D_CIVIC_ADOPT", MESSAGE_TYPE_MINOR_EVENT);
		    }
		}
    }
    int iMiscastChance = kSpellInfo.getMiscastChance() + getMiscastChance(); // MiscastPromotions 10/2019 lfgr
    if (iMiscastChance > 0)
    {
        if (GC.getGameINLINE().getSorenRandNum(100, "Miscast") < iMiscastChance)
        {
            if (!CvString(kSpellInfo.getPyMiscast()).empty())
            {
                CyUnit* pyUnit = new CyUnit(this);
                CyArgsList argsList;
                argsList.add(gDLL->getPythonIFace()->makePythonObject(pyUnit));	// pass in unit class
                argsList.add(spell);//the spell #
                gDLL->getPythonIFace()->callFunction(PYSpellModule, "miscast", argsList.makeFunctionArgs()); //, &lResult
                delete pyUnit; // python fxn must not hold on to this pointer
            }
			// MiscastPromotions 10/2019 lfgr: fixed message
            gDLL->getInterfaceIFace()->addMessage((PlayerTypes)getOwner(), true, GC.getEVENT_MESSAGE_TIME(),
					gDLL->getText("TXT_KEY_MESSAGE_SPELL_MISCAST", getName().GetCString(), kSpellInfo.getDescription()),
					"AS2D_WONDER_UNIT_BUILD", MESSAGE_TYPE_MAJOR_EVENT, "art/interface/buttons/spells/miscast.dds",
					(ColorTypes)GC.getInfoTypeForString("COLOR_RED"), getX_INLINE(), getY_INLINE(), true, true);
            gDLL->getInterfaceIFace()->setDirty(SelectionButtons_DIRTY_BIT, true);
            return;
        }
    }
    if (kSpellInfo.getDelay() > 0)
    {
        if (getDelayedSpell() == NO_SPELL)
        {
            changeImmobileTimer(kSpellInfo.getDelay());
            setDelayedSpell(spell);
            gDLL->getInterfaceIFace()->setDirty(SelectionButtons_DIRTY_BIT, true);
            gDLL->getInterfaceIFace()->changeCycleSelectionCounter((GET_PLAYER(getOwnerINLINE()).isOption(PLAYEROPTION_QUICK_MOVES)) ? 1 : 2);
            return;
        }
        setDelayedSpell(NO_SPELL);
    }
    if (kSpellInfo.getCreateUnitType() != -1)
    {
        int iUnitNum = kSpellInfo.getCreateUnitNum();
        if (isTwincast())
        {
            iUnitNum *= 2;
        }
        for (int i=0; i < iUnitNum; ++i)
        {
            castCreateUnit(spell);
        }
    }
    if (kSpellInfo.getAddPromotionType1() != -1)
    {
        castAddPromotion(spell);
    }
    if (kSpellInfo.getRemovePromotionType1() != -1)
    {
        castRemovePromotion(spell);
    }
    if (kSpellInfo.getConvertUnitType() != NO_UNIT)
    {
        castConvertUnit(spell);
    }
    if (kSpellInfo.getCreateBuildingType() != NO_BUILDING)
    {
        if (canCreateBuilding(spell))
        {
            plot()->getPlotCity()->setNumRealBuilding((BuildingTypes)kSpellInfo.getCreateBuildingType(), true);
        }
    }
	// MNAI begin
	/*
	if (canTerraform(spell, plot()))
	{
		castTerraform(spell);
	}
	*/
	// MNAI end
    if (kSpellInfo.getCreateFeatureType() != NO_FEATURE)
    {
        if (canCreateFeature(spell))
        {
            plot()->setFeatureType((FeatureTypes)kSpellInfo.getCreateFeatureType(), -1);
        }
    }
    if (kSpellInfo.getCreateImprovementType() != NO_IMPROVEMENT)
    {
        if (canCreateImprovement(spell))
        {
            plot()->setImprovementType((ImprovementTypes)kSpellInfo.getCreateImprovementType());
        }
    }
    if (kSpellInfo.getSpreadReligion() != NO_RELIGION)
    {
        if (canSpreadReligion(spell))
        {
            plot()->getPlotCity()->setHasReligion((ReligionTypes)kSpellInfo.getSpreadReligion(), true, true, true);
        }
    }
    if (kSpellInfo.getDamage() != 0)
    {
        castDamage(spell);
    }
    if (kSpellInfo.getImmobileTurns() != 0)
    {
        castImmobile(spell);
    }
    if (kSpellInfo.isPush())
    {
        castPush(spell);
    }
    if (kSpellInfo.isRemoveHasCasted())
    {
        if (getDuration() == 0)
        {
            setHasCasted(false);
        }
    }

	GET_PLAYER(getOwnerINLINE()).changeGold( - info_utils::getRealSpellCost( getOwnerINLINE(), (SpellTypes) spell ) );

    if (kSpellInfo.getChangePopulation() != 0)
    {
        plot()->getPlotCity()->changePopulation(kSpellInfo.getChangePopulation());
    }
    if (kSpellInfo.isDispel())
    {
        castDispel(spell);
    }
    if (plot()->isVisibleToWatchingHuman())
    {
        if (kSpellInfo.getEffect() != -1)
        {
            gDLL->getEngineIFace()->TriggerEffect(kSpellInfo.getEffect(), plot()->getPoint(), (float)(GC.getASyncRand().get(360)));
        }
        if (kSpellInfo.getSound() != NULL)
        {
            gDLL->getInterfaceIFace()->playGeneralSound(kSpellInfo.getSound(), plot()->getPoint());
        }
		szBuffer = gDLL->getText("TXT_KEY_MESSAGE_SPELL_CAST", getName().GetCString(), kSpellInfo.getDescription());
        gDLL->getInterfaceIFace()->addMessage((PlayerTypes)getOwner(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_WONDER_UNIT_BUILD", MESSAGE_TYPE_MAJOR_EVENT, kSpellInfo.getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_UNIT_TEXT"), getX_INLINE(), getY_INLINE(), true, true);
    }
	if (!CvString(kSpellInfo.getPyResult()).empty())
    {
        CyUnit* pyUnit = new CyUnit(this);
        CyArgsList argsList;
        argsList.add(gDLL->getPythonIFace()->makePythonObject(pyUnit));	// pass in unit class
        argsList.add(spell);//the spell #
        gDLL->getPythonIFace()->callFunction(PYSpellModule, "cast", argsList.makeFunctionArgs()); //, &lResult
        delete pyUnit; // python fxn must not hold on to this pointer
    }

//>>>>Spell Interrupt Unit Cycling: Added by Denev 2009/10/17
/*	Casting spell triggers unit cycling	*/
	if (isInGroup() && !getGroup()->readyToSelect(true) && !getGroup()->isBusy())
	{
//		gDLL->getInterfaceIFace()->setDirty(SelectionButtons_DIRTY_BIT, true);
//		gDLL->getInterfaceIFace()->changeCycleSelectionCounter((GET_PLAYER(getOwnerINLINE()).isOption(PLAYEROPTION_QUICK_MOVES)) ? 1 : 2);
		GC.getGameINLINE().updateSelectionList();
	}
//<<<<Spell Interrupt Unit Cycling: End Add

	gDLL->getInterfaceIFace()->setDirty(SelectionButtons_DIRTY_BIT, true);
	if (kSpellInfo.isSacrificeCaster())
	{
		logBBAI("    Killing %S -- Sacrificed for spell (Unit %d - plot: %d, %d)",
				getName().GetCString(), getID(), getX(), getY());
		kill(false);
	}
}

void CvUnit::castAddPromotion(int spell)
{
   	PromotionTypes ePromotion1 = (PromotionTypes)GC.getSpellInfo((SpellTypes)spell).getAddPromotionType1();
   	PromotionTypes ePromotion2 = (PromotionTypes)GC.getSpellInfo((SpellTypes)spell).getAddPromotionType2();
   	PromotionTypes ePromotion3 = (PromotionTypes)GC.getSpellInfo((SpellTypes)spell).getAddPromotionType3();

    if (GC.getSpellInfo((SpellTypes)spell).isBuffCasterOnly())
    {
        if( ePromotion1 != NO_PROMOTION && canBeGrantedPromotion( ePromotion1 ) )
        {
            setHasPromotion(ePromotion1, true);
        }
        if( ePromotion2 != NO_PROMOTION && canBeGrantedPromotion( ePromotion2 ) )
        {
            setHasPromotion(ePromotion2, true);
        }
        if( ePromotion3 != NO_PROMOTION && canBeGrantedPromotion( ePromotion3 ) )
        {
            setHasPromotion(ePromotion3, true);
        }
    }
    else
    {
        int iRange = GC.getSpellInfo((SpellTypes)spell).getRange();
        bool bResistable = GC.getSpellInfo((SpellTypes)spell).isResistable();
        CLLNode<IDInfo>* pUnitNode;
        CvUnit* pLoopUnit;
        CvPlot* pLoopPlot;
        for (int i = -iRange; i <= iRange; ++i)
        {
            for (int j = -iRange; j <= iRange; ++j)
            {
                pLoopPlot = ::plotXY(plot()->getX_INLINE(), plot()->getY_INLINE(), i, j);
                if (NULL != pLoopPlot)
                {
                    pUnitNode = pLoopPlot->headUnitNode();
                    while (pUnitNode != NULL)
                    {
                        pLoopUnit = ::getUnit(pUnitNode->m_data);
                        pUnitNode = pLoopPlot->nextUnitNode(pUnitNode);
                        if (!pLoopUnit->isImmuneToSpell(this, spell))
                        {
							// MNAI - don't try and put this spell effect on units already affected by it
							// (avoid them trying to resist it)
							bool bValid = false;
							if (ePromotion1 != NO_PROMOTION)
                            {
								if (!pLoopUnit->isHasPromotion(ePromotion1))
								{
									bValid = true;
								}
							}

							if (ePromotion2 != NO_PROMOTION)
                            {
								if (!pLoopUnit->isHasPromotion(ePromotion2))
								{
									bValid = true;
								}
							}

							if (ePromotion3 != NO_PROMOTION)
                            {
								if (!pLoopUnit->isHasPromotion(ePromotion3))
								{
									bValid = true;
								}
							}
							// MNAI End

							if( bValid && bResistable && pLoopUnit->isResisted(this, spell) ) {
								bValid = false;
							}

							if( bValid ) {
								if( ePromotion1 != NO_PROMOTION && pLoopUnit->canBeGrantedPromotion( ePromotion1, true ) ) {
									pLoopUnit->setHasPromotion(ePromotion1, true);
								}
								if( ePromotion2 != NO_PROMOTION && pLoopUnit->canBeGrantedPromotion( ePromotion2, true ) ) {
									pLoopUnit->setHasPromotion(ePromotion2, true);
								}
								if( ePromotion3 != NO_PROMOTION && pLoopUnit->canBeGrantedPromotion( ePromotion3, true ) ) {
									pLoopUnit->setHasPromotion(ePromotion3, true);
								}
							}
                        }
                    }
                }
            }
        }
    }
}

void CvUnit::castDamage(int spell)
{
    bool bResistable = GC.getSpellInfo((SpellTypes)spell).isResistable();
    int iDmg = GC.getSpellInfo((SpellTypes)spell).getDamage();
    int iDmgLimit = GC.getSpellInfo((SpellTypes)spell).getDamageLimit();
    int iDmgType = GC.getSpellInfo((SpellTypes)spell).getDamageType();
    int iRange = GC.getSpellInfo((SpellTypes)spell).getRange();
	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pLoopUnit;
	CvPlot* pLoopPlot;
	for (int i = -iRange; i <= iRange; ++i)
	{
		for (int j = -iRange; j <= iRange; ++j)
		{
			pLoopPlot = ::plotXY(plot()->getX_INLINE(), plot()->getY_INLINE(), i, j);
			if (NULL != pLoopPlot)
			{
				if (pLoopPlot->getX() != plot()->getX() || pLoopPlot->getY() != plot()->getY())
				{
					pUnitNode = pLoopPlot->headUnitNode();
					while (pUnitNode != NULL)
					{
						pLoopUnit = ::getUnit(pUnitNode->m_data);
						pUnitNode = pLoopPlot->nextUnitNode(pUnitNode);
						if (!pLoopUnit->isImmuneToSpell(this, spell))
						{
							if (bResistable)
							{
								if (!pLoopUnit->isResisted(this, spell))
								{
//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/14
//*** delete redundant randomization.
//									pLoopUnit->doDamage((iDmg / 2) + GC.getGameINLINE().getSorenRandNum(iDmg, "doDamage"), iDmgLimit, this, iDmgType, true);
									pLoopUnit->doDamage(iDmg, iDmgLimit, this, iDmgType, true);
//<<<<Unofficial Bug Fix: End Modify
								}
							}
							else
							{
//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/14
//*** delete redundant randomization.
//								pLoopUnit->doDamage((iDmg / 2) + GC.getGameINLINE().getSorenRandNum(iDmg, "doDamage"), iDmgLimit, this, iDmgType, true);
								pLoopUnit->doDamage(iDmg, iDmgLimit, this, iDmgType, true);
//<<<<Unofficial Bug Fix: End Modify
							}
						}
					}
				}
			}
		}
	}
}

void CvUnit::castDispel(int spell)
{
    bool bResistable = GC.getSpellInfo((SpellTypes)spell).isResistable();
    int iRange = GC.getSpellInfo((SpellTypes)spell).getRange();
	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pLoopUnit;
	CvPlot* pLoopPlot;
    for (int i = -iRange; i <= iRange; ++i)
    {
        for (int j = -iRange; j <= iRange; ++j)
        {
            pLoopPlot = ::plotXY(plot()->getX_INLINE(), plot()->getY_INLINE(), i, j);
            if (NULL != pLoopPlot)
            {
                pUnitNode = pLoopPlot->headUnitNode();
                while (pUnitNode != NULL)
                {
                    pLoopUnit = ::getUnit(pUnitNode->m_data);
                    pUnitNode = pLoopPlot->nextUnitNode(pUnitNode);
                    if (!pLoopUnit->isImmuneToSpell(this, spell))
                    {
                        if (pLoopUnit->isEnemy(getTeam()))
                        {
                            if (bResistable)
                            {
                                if (pLoopUnit->isResisted(this, spell))
                                {
                                    continue;
                                }
                            }
                            for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
                            {
                                if (GC.getPromotionInfo((PromotionTypes)iI).isDispellable() && GC.getPromotionInfo((PromotionTypes)iI).getAIWeight() > 0)
                                {
                                    pLoopUnit->setHasPromotion((PromotionTypes)iI, false);
                                }
                            }
                        }
                        else
                        {
                            for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
                            {
                                if (GC.getPromotionInfo((PromotionTypes)iI).isDispellable() && GC.getPromotionInfo((PromotionTypes)iI).getAIWeight() < 0)
                                {
                                    pLoopUnit->setHasPromotion((PromotionTypes)iI, false);
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

void CvUnit::castImmobile(int spell)
{
    bool bResistable = GC.getSpellInfo((SpellTypes)spell).isResistable();
    int iImmobileTurns = GC.getSpellInfo((SpellTypes)spell).getImmobileTurns();
    int iRange = GC.getSpellInfo((SpellTypes)spell).getRange();
	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pLoopUnit;
	CvPlot* pLoopPlot;
    for (int i = -iRange; i <= iRange; ++i)
    {
        for (int j = -iRange; j <= iRange; ++j)
        {
            pLoopPlot = ::plotXY(plot()->getX_INLINE(), plot()->getY_INLINE(), i, j);
            if (NULL != pLoopPlot)
            {
                if (pLoopPlot->getX() != plot()->getX() || pLoopPlot->getY() != plot()->getY())
                {
                    pUnitNode = pLoopPlot->headUnitNode();
                    while (pUnitNode != NULL)
                    {
                        pLoopUnit = ::getUnit(pUnitNode->m_data);
                        pUnitNode = pLoopPlot->nextUnitNode(pUnitNode);
                        if (!pLoopUnit->isImmuneToSpell(this, spell) && pLoopUnit->getImmobileTimer() == 0)
                        {
                            if (bResistable)
                            {
                                if (!pLoopUnit->isResisted(this, spell))
                                {
                                    pLoopUnit->changeImmobileTimer(iImmobileTurns);
									gDLL->getInterfaceIFace()->addMessage((PlayerTypes)pLoopUnit->getOwner(), true, GC.getEVENT_MESSAGE_TIME(), gDLL->getText("TXT_KEY_MESSAGE_SPELL_IMMOBILE", pLoopUnit->getName().GetCString()), "AS2D_DISCOVERBONUS", MESSAGE_TYPE_MAJOR_EVENT, GC.getSpellInfo((SpellTypes)spell).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), getX_INLINE(), getY_INLINE(), true, true);
									gDLL->getInterfaceIFace()->addMessage((PlayerTypes)getOwner(), true, GC.getEVENT_MESSAGE_TIME(), gDLL->getText("TXT_KEY_MESSAGE_SPELL_IMMOBILE", pLoopUnit->getName().GetCString()), "AS2D_DISCOVERBONUS", MESSAGE_TYPE_MAJOR_EVENT, GC.getSpellInfo((SpellTypes)spell).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), getX_INLINE(), getY_INLINE(), true, true);
                                }
                            }
                            else
                            {
                                pLoopUnit->changeImmobileTimer(iImmobileTurns);
                                gDLL->getInterfaceIFace()->addMessage((PlayerTypes)pLoopUnit->getOwner(), true, GC.getEVENT_MESSAGE_TIME(), gDLL->getText("TXT_KEY_MESSAGE_SPELL_IMMOBILE", pLoopUnit->getName().GetCString()), "AS2D_DISCOVERBONUS", MESSAGE_TYPE_MAJOR_EVENT, GC.getSpellInfo((SpellTypes)spell).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), getX_INLINE(), getY_INLINE(), true, true);
                                gDLL->getInterfaceIFace()->addMessage((PlayerTypes)getOwner(), true, GC.getEVENT_MESSAGE_TIME(), gDLL->getText("TXT_KEY_MESSAGE_SPELL_IMMOBILE", pLoopUnit->getName().GetCString()), "AS2D_DISCOVERBONUS", MESSAGE_TYPE_MAJOR_EVENT, GC.getSpellInfo((SpellTypes)spell).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), getX_INLINE(), getY_INLINE(), true, true);
                            }
                        }
                    }
                }
            }
        }
    }
}

void CvUnit::castPush(int spell)
{
    bool bResistable = GC.getSpellInfo((SpellTypes)spell).isResistable();
    int iRange = GC.getSpellInfo((SpellTypes)spell).getRange();
	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pLoopUnit;
	CvPlot* pLoopPlot;
	CvPlot* pPushPlot;
    for (int i = -iRange; i <= iRange; ++i)
    {
        for (int j = -iRange; j <= iRange; ++j)
        {
            int iPushY = plot()->getY_INLINE() + (i*2);
            pLoopPlot = ::plotXY(plot()->getX_INLINE(), plot()->getY_INLINE(), i, j);
            pPushPlot = ::plotXY(plot()->getX_INLINE(), plot()->getY_INLINE(), i*2, j*2);
            if (!pLoopPlot->isCity())
            {
                if (NULL != pLoopPlot)
                {
                    if (NULL != pPushPlot)
                    {
                        if (pLoopPlot->getX() != plot()->getX() || pLoopPlot->getY() != plot()->getY())
                        {
                            pUnitNode = pLoopPlot->headUnitNode();
                            while (pUnitNode != NULL)
                            {
                                pLoopUnit = ::getUnit(pUnitNode->m_data);
                                pUnitNode = pLoopPlot->nextUnitNode(pUnitNode);
                                if (pLoopUnit->canMoveInto(pPushPlot, false, false, false))
                                {
                                    if (!pLoopUnit->isImmuneToSpell(this, spell))
                                    {
                                        if (bResistable)
                                        {
                                            if (!pLoopUnit->isResisted(this, spell))
                                            {
                                                pLoopUnit->setXY(pPushPlot->getX(),pPushPlot->getY(),false,true,true);
                                                gDLL->getInterfaceIFace()->addMessage((PlayerTypes)pLoopUnit->getOwner(), false, GC.getEVENT_MESSAGE_TIME(), gDLL->getText("TXT_KEY_MESSAGE_SPELL_PUSH", pLoopUnit->getName().GetCString()), "AS2D_DISCOVERBONUS", MESSAGE_TYPE_MAJOR_EVENT, GC.getSpellInfo((SpellTypes)spell).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), getX_INLINE(), getY_INLINE(), true, true);
                                                gDLL->getInterfaceIFace()->addMessage((PlayerTypes)getOwner(), false, GC.getEVENT_MESSAGE_TIME(), gDLL->getText("TXT_KEY_MESSAGE_SPELL_PUSH", pLoopUnit->getName().GetCString()), "AS2D_DISCOVERBONUS", MESSAGE_TYPE_MAJOR_EVENT, GC.getSpellInfo((SpellTypes)spell).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), getX_INLINE(), getY_INLINE(), true, true);
                                            }
                                        }
                                        else
                                        {
                                            pLoopUnit->setXY(pPushPlot->getX(),pPushPlot->getY(),false,true,true);
                                            gDLL->getInterfaceIFace()->addMessage((PlayerTypes)pLoopUnit->getOwner(), false, GC.getEVENT_MESSAGE_TIME(), gDLL->getText("TXT_KEY_MESSAGE_SPELL_PUSH", pLoopUnit->getName().GetCString()), "AS2D_DISCOVERBONUS", MESSAGE_TYPE_MAJOR_EVENT, GC.getSpellInfo((SpellTypes)spell).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), getX_INLINE(), getY_INLINE(), true, true);
                                            gDLL->getInterfaceIFace()->addMessage((PlayerTypes)getOwner(), false, GC.getEVENT_MESSAGE_TIME(), gDLL->getText("TXT_KEY_MESSAGE_SPELL_PUSH", pLoopUnit->getName().GetCString()), "AS2D_DISCOVERBONUS", MESSAGE_TYPE_MAJOR_EVENT, GC.getSpellInfo((SpellTypes)spell).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), getX_INLINE(), getY_INLINE(), true, true);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

void CvUnit::castRemovePromotion(int spell)
{
	bool bNotAffected;

   	PromotionTypes ePromotion1 = (PromotionTypes)GC.getSpellInfo((SpellTypes)spell).getRemovePromotionType1();
   	PromotionTypes ePromotion2 = (PromotionTypes)GC.getSpellInfo((SpellTypes)spell).getRemovePromotionType2();
   	PromotionTypes ePromotion3 = (PromotionTypes)GC.getSpellInfo((SpellTypes)spell).getRemovePromotionType3();
    if (GC.getSpellInfo((SpellTypes)spell).isBuffCasterOnly())
    {
        if (ePromotion1 != NO_PROMOTION)
        {
            setHasPromotion(ePromotion1, false);
        }
        if (ePromotion2 != NO_PROMOTION)
        {
            setHasPromotion(ePromotion2, false);
        }
        if (ePromotion3 != NO_PROMOTION)
        {
            setHasPromotion(ePromotion3, false);
        }
    }
    else
    {
        int iRange = GC.getSpellInfo((SpellTypes)spell).getRange();
        bool bResistable = GC.getSpellInfo((SpellTypes)spell).isResistable();
        CLLNode<IDInfo>* pUnitNode;
        CvUnit* pLoopUnit;
        CvPlot* pLoopPlot;
        for (int i = -iRange; i <= iRange; ++i)
        {
            for (int j = -iRange; j <= iRange; ++j)
            {
                pLoopPlot = ::plotXY(plot()->getX_INLINE(), plot()->getY_INLINE(), i, j);
                if (NULL != pLoopPlot)
                {
                    pUnitNode = pLoopPlot->headUnitNode();
                    while (pUnitNode != NULL)
                    {
                        pLoopUnit = ::getUnit(pUnitNode->m_data);
                        pUnitNode = pLoopPlot->nextUnitNode(pUnitNode);
                        if (!pLoopUnit->isImmuneToSpell(this, spell))
                        {
							bNotAffected = true;

							if (ePromotion1 != NO_PROMOTION)
                            {
								if (pLoopUnit->isHasPromotion(ePromotion1))
								{
									bNotAffected = false;
								}
							}

							if (ePromotion2 != NO_PROMOTION)
                            {
								if (pLoopUnit->isHasPromotion(ePromotion2))
								{
									bNotAffected = false;
								}
							}

							if (ePromotion3 != NO_PROMOTION)
                            {
								if (pLoopUnit->isHasPromotion(ePromotion3))
								{
									bNotAffected = false;
								}
							}

                            if (bResistable && !bNotAffected)
                            {
                                if (!pLoopUnit->isResisted(this, spell))
                                {
                                    if (ePromotion1 != NO_PROMOTION)
                                    {
                                        pLoopUnit->setHasPromotion(ePromotion1, false);
                                    }
                                    if (ePromotion2 != NO_PROMOTION)
                                    {
                                        pLoopUnit->setHasPromotion(ePromotion2, false);
                                    }
                                    if (ePromotion3 != NO_PROMOTION)
                                    {
                                        pLoopUnit->setHasPromotion(ePromotion3, false);
                                    }
                                }
                            }
                            else
                            {
                                if (ePromotion1 != NO_PROMOTION)
                                {
                                    pLoopUnit->setHasPromotion(ePromotion1, false);
                                }
                                if (ePromotion2 != NO_PROMOTION)
                                {
                                    pLoopUnit->setHasPromotion(ePromotion2, false);
                                }
                                if (ePromotion3 != NO_PROMOTION)
                                {
                                    pLoopUnit->setHasPromotion(ePromotion3, false);
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

void CvUnit::castConvertUnit(int spell)
{
	CvUnit* pUnit;
   	pUnit = GET_PLAYER(getOwnerINLINE()).initUnit((UnitTypes)GC.getSpellInfo((SpellTypes)spell).getConvertUnitType(), getX_INLINE(), getY_INLINE(), AI_getUnitAIType());
   	pUnit->convert(this);
    pUnit->changeImmobileTimer(1);
/*************************************************************************************************/
/**	BETTER AI (Doviello Worker needs decent UNITAI after upgrade) Sephi            	            **/
/*************************************************************************************************/
	// ALN !!ToDo!! - this is just pretty sloppy, look for best unit AI?
    if(pUnit->AI_getUnitAIType()==UNITAI_WORKER)
    {
        int iWorkerClass = GC.getInfoTypeForString("UNITCLASS_WORKER");

        if (iWorkerClass != NO_UNITCLASS && pUnit->getUnitClassType()!=iWorkerClass)
        {
            pUnit->AI_setUnitAIType(UNITAI_ATTACK_CITY);
            if (!isHuman())
            {
                pUnit->AI_setGroupflag(GROUPFLAG_CONQUEST);
            }
        }
    }
	if (pUnit->getUnitClassType() == GC.getInfoTypeForString("UNITCLASS_SHADE"))
	{
		pUnit->joinGroup(NULL);
		pUnit->AI_setGroupflag(GROUPFLAG_NONE);
	}

/*************************************************************************************************/
/**	END	                                        												**/
/*************************************************************************************************/
}

void CvUnit::castCreateUnit(int spell)
{
    int iI;
	CvUnit* pUnit;
//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/22
//*** summoned unit is pushed out if enemy unit exists in the same tile.
//	pUnit = GET_PLAYER(getOwnerINLINE()).initUnit((UnitTypes)GC.getSpellInfo((SpellTypes)spell).getCreateUnitType(), getX_INLINE(), getY_INLINE(), UNITAI_ATTACK);
	pUnit = GET_PLAYER(getOwnerINLINE()).initUnit((UnitTypes)GC.getSpellInfo((SpellTypes)spell).getCreateUnitType(), getX_INLINE(), getY_INLINE(), NO_UNITAI, DIRECTION_SOUTH, false);
//<<<<Unofficial Bug Fix: End Modify
	pUnit->setSummoner(getID());
/*************************************************************************************************/
/**	BETTER AI (Flag for Permanent Summons) Sephi                                  	            **/
/*************************************************************************************************/
   	if (GC.getSpellInfo((SpellTypes)spell).isPermanentUnitCreate())
    {
        pUnit->setPermanentSummon(true);
    }
/*************************************************************************************************/
/**	END	                                        												**/
/*************************************************************************************************/
	// lfgr 11/2021: Decouple permanent and immobile summons
	if (GC.getSpellInfo((SpellTypes)spell).isImmobileUnitCreate())
	{
		pUnit->changeImmobileTimer(2);
	}
	if( ! GC.getSpellInfo((SpellTypes)spell).isPermanentUnitCreate() )
	{
		pUnit->changeDuration(2);
		if (pUnit->getSpecialUnitType() != GC.defines.iSPECIALUNIT_SPELL)
		{
			pUnit->changeDuration(GET_PLAYER(getOwnerINLINE()).getSummonDuration());
		}
		if (plot()->getTeam() != getTeam())
		{
			GET_PLAYER(getOwnerINLINE()).changeNumOutsideUnits(-1);
		}
	}
	for (iI = 0; iI < GC.getNumPromotionInfos(); iI++)
	{
	    if (isHasPromotion((PromotionTypes)iI))
	    {
            if (GC.getSpellInfo((SpellTypes)spell).isCopyCastersPromotions())
            {
                if (!GC.getPromotionInfo((PromotionTypes)iI).isEquipment() && !GC.getPromotionInfo((PromotionTypes)iI).isRace() && iI != GC.defines.iGREAT_COMMANDER_PROMOTION)
                {
                    pUnit->setHasPromotion((PromotionTypes)iI, true);
                }
            }
//>>>>BUGFfH: Modified by Denev 2009/10/08
/*	if summoning action is not a spell (e.g. Hire Goblin), summoner's promotion doesn't affect to summoned creature.	*/
//			else
			else if (!GC.getSpellInfo((SpellTypes)spell).isAbility())
//<<<<BUGFfH: End Modify
            {
                if (GC.getPromotionInfo((PromotionTypes)iI).getPromotionSummonPerk() != NO_PROMOTION)
                {
                    pUnit->setHasPromotion((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iI).getPromotionSummonPerk(), true);
                }
            }
	    }
	}
   	if (GC.getSpellInfo((SpellTypes)spell).getCreateUnitPromotion() != NO_PROMOTION)
   	{
        pUnit->setHasPromotion((PromotionTypes)GC.getSpellInfo((SpellTypes)spell).getCreateUnitPromotion(), true);
   	}
   	pUnit->doTurn();
   	if (!isHuman())
   	{
/*************************************************************************************************/
/**	BETTER AI (Better use of Summons) Sephi                                       	            **/
/**																								**/
/**						                                            							**/
/*************************************************************************************************/
        //Tholal AI - change AI type
        if(pUnit->isAnimal())
        {
			pUnit->AI_setUnitAIType(UNITAI_COUNTER);
        }

		if (pUnit->getDuration() > 0)
        {
			if (pUnit->canMove())
			{
				pUnit->AI_setGroupflag(GROUPFLAG_SUICIDE_SUMMON);
				pUnit->setSuicideSummon(true);
				pUnit->AI_update();
			}
        }
	
/*************************************************************************************************/
/**	END	                                        												**/
/*************************************************************************************************/
	}
//>>>>Unofficial Bug Fix: Added by Denev 2010/02/22
//*** summoned unit is pushed out if enemy unit exists in the same tile.
	if (pUnit->plot()->isVisibleEnemyUnit(getOwnerINLINE()))
	{
		pUnit->withdrawlToNearestValidPlot(); // Note: Can kill unit. Do not do anything else with this unit afterwards!
	}
//<<<<Unofficial Bug Fix: End Add
}

// MNAI begin
/*
void CvUnit::castTerraform(int spell)
{
	CvSpellInfo& kSpellInfo = GC.getSpellInfo((SpellTypes) spell);
	CvPlot* pPlot = plot();
	int iRange = kSpellInfo.getRange();

	for (int iDX = -iRange; iDX <= iRange; ++iDX)
	{
		for (int iDY = -iRange; iDY <= iRange; ++iDY)
		{
			CvPlot* pLoopPlot = plotXY(pPlot->getX_INLINE(), pPlot->getY_INLINE(), iDX, iDY);
			if (pLoopPlot != NULL)
			{
				FeatureTypes eFeature = pLoopPlot->getFeatureType();
				if (eFeature != NO_FEATURE)
				{
					if (kSpellInfo.isFeatureInvalid(eFeature))
					{
						continue;
					}
					if (kSpellInfo.getFeatureConvert(eFeature) != eFeature)
					{
						pLoopPlot->setFeatureType((FeatureTypes) kSpellInfo.getFeatureConvert(eFeature));
					}
				}
				if (kSpellInfo.getTerrainConvert(pLoopPlot->getTerrainType()) != NO_TERRAIN)
				{
					pLoopPlot->setTerrainType((TerrainTypes) kSpellInfo.getTerrainConvert(pLoopPlot->getTerrainType()));
					if (kSpellInfo.isRemoveInvalidFeature() && pLoopPlot->getFeatureType() != NO_FEATURE)
					{
						if (!GC.getFeatureInfo(pLoopPlot->getFeatureType()).isTerrain(pLoopPlot->getTerrainType()))
						{
							pLoopPlot->setFeatureType(NO_FEATURE);
						}
					}
				}
			}
		}
	}

	if (kSpellInfo.isCausesWar())
	{
		if (pPlot->getTeam() != getTeam() && pPlot->getTeam() != NO_TEAM)
		{
			if (!isHiddenNationality())
			{
				if (!GET_TEAM(getTeam()).isPermanentWarPeace(pPlot->getTeam()))
                {
                    GET_TEAM(getTeam()).declareWar(pPlot->getTeam(), false, WARPLAN_TOTAL);
                }
			}
		}
	}
}
*/
// MNAI end

bool CvUnit::isHasCasted() const
{
	return m_bHasCasted;
}

void CvUnit::setHasCasted(bool bNewValue)
{
	m_bHasCasted = bNewValue;
}

bool CvUnit::isIgnoreHide() const
{
	return m_bIgnoreHide;
}

void CvUnit::setIgnoreHide(bool bNewValue)
{
	m_bIgnoreHide = bNewValue;
}

bool CvUnit::isImmuneToSpell(CvUnit* pCaster, int spell) const
{
	// objects are immune to spell effects
	if (getUnitInfo().isObject())
	{
		return true;
	}

    if (isImmuneToMagic())
    {
        if (!GC.getSpellInfo((SpellTypes)spell).isAbility())
        {
            return true;
        }
    }
   	if (GC.getSpellInfo((SpellTypes)spell).isImmuneTeam())
   	{
   	    if (getTeam() == pCaster->getTeam())
   	    {
   	        return true;
   	    }
   	}
   	if (GC.getSpellInfo((SpellTypes)spell).isImmuneNeutral())
   	{
   	    if (getTeam() != pCaster->getTeam())
   	    {
   	        if (!isEnemy(pCaster->getTeam()))
            {
                return true;
            }
        }
   	}
   	if (GC.getSpellInfo((SpellTypes)spell).isImmuneEnemy())
   	{
        if (isEnemy(pCaster->getTeam()))
        {
            return true;
        }
   	}
   	if (GC.getSpellInfo((SpellTypes)spell).isImmuneFlying())
   	{
   	    if (isFlying())
   	    {
   	        return true;
   	    }
   	}
   	if (GC.getSpellInfo((SpellTypes)spell).isImmuneNotAlive())
   	{
   	    if (!isAlive())
   	    {
   	        return true;
   	    }
   	}
    return false;
}

int CvUnit::getDelayedSpell() const
{
	return m_iDelayedSpell;
}

void CvUnit::setDelayedSpell(int iNewValue)
{
	m_iDelayedSpell = iNewValue;
}

int CvUnit::getDuration() const
{
	return m_iDuration;
}

void CvUnit::setDuration(int iNewValue)
{
	/*
	* Bugfix: If a unit is made temporary or permanent in a place in which units must pay supply costs,
	* the NumOutsideUnits variable must be updated accordingly.
	*/
	if (m_iDuration != iNewValue && plot()->getTeam() != getTeam() && (plot()->getTeam() == NO_TEAM || !GET_TEAM(plot()->getTeam()).isVassal(getTeam()))) {
		   if (m_iDuration == 0) {
				   // The unit is now temporary.
				   GET_PLAYER(getOwnerINLINE()).changeNumOutsideUnits(-1);
		   } else if (iNewValue == 0) {
				   // The unit is now permanent.
				   GET_PLAYER(getOwnerINLINE()).changeNumOutsideUnits(1);
		   }
	}

	m_iDuration = iNewValue;
}

void CvUnit::changeDuration(int iChange)
{
	setDuration(getDuration() + iChange);
}

bool CvUnit::isFleeWithdrawl() const
{
	return m_bFleeWithdrawl;
}

void CvUnit::setFleeWithdrawl(bool bNewValue)
{
    m_bFleeWithdrawl = bNewValue;
}

bool CvUnit::isAlive() const
{
	return m_iAlive == 0 ? true : false;
}

void CvUnit::changeAlive(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iAlive += iNewValue;
    }
}

bool CvUnit::isAIControl() const
{
	return m_iAIControl == 0 ? false : true;
}

void CvUnit::changeAIControl(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iAIControl += iNewValue;
    }
}

bool CvUnit::isBoarding() const
{
	return m_iBoarding == 0 ? false : true;
}

void CvUnit::changeBoarding(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iBoarding += iNewValue;
    }
}

int CvUnit::getDefensiveStrikeChance() const
{
	return m_iDefensiveStrikeChance;
}

void CvUnit::changeDefensiveStrikeChance(int iChange)
{
	if (iChange != 0)
	{
		m_iDefensiveStrikeChance += iChange;
	}
}

int CvUnit::getDefensiveStrikeDamage() const
{
	return m_iDefensiveStrikeDamage;
}

void CvUnit::changeDefensiveStrikeDamage(int iChange)
{
	if (iChange != 0)
	{
		m_iDefensiveStrikeDamage += iChange;
	}
}

bool CvUnit::isDoubleFortifyBonus() const
{
	return m_iDoubleFortifyBonus == 0 ? false : true;
}

void CvUnit::changeDoubleFortifyBonus(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iDoubleFortifyBonus += iNewValue;
    }
}

bool CvUnit::isFear() const
{
	return m_iFear == 0 ? false : true;
}

void CvUnit::changeFear(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iFear += iNewValue;
    }
}

bool CvUnit::isFlying() const
{
	return m_iFlying == 0 ? false : true;
}

void CvUnit::changeFlying(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iFlying += iNewValue;
    }
}

bool CvUnit::isHeld() const
{
	return m_iHeld == 0 ? false : true;
}

void CvUnit::changeHeld(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iHeld += iNewValue;
    }
}

bool CvUnit::isHiddenNationality() const
{
    if (isCargo())
    {
        if (!getTransportUnit()->isHiddenNationality())
        {
            return false;
        }
    }
	return m_iHiddenNationality == 0 ? false : true;
}

void CvUnit::changeHiddenNationality(int iNewValue)
{
    if (iNewValue != 0)
    {
        if (m_iHiddenNationality + iNewValue == 0)
        {
            //updatePlunder(-1, false);
			setBlockading(false);
            m_iHiddenNationality += iNewValue;
			if (getGroup()->getNumUnits() > 1)
			{
	            joinGroup(NULL, true);
			}
            //updatePlunder(1, false);
        }
        else
        {
            m_iHiddenNationality += iNewValue;
        }
    }
}

void CvUnit::changeIgnoreBuildingDefense(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iIgnoreBuildingDefense += iNewValue;
    }
}

bool CvUnit::isImmortal() const
{
	return m_iImmortal == 0 ? false : true;
}

void CvUnit::changeImmortal(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iImmortal += iNewValue;
        if (m_iImmortal < 0)
        {
            m_iImmortal = 0;
        }
    }
}

// lfgr fix 01/2021: Reliably set the immortality counter to 0
void CvUnit::makeMortal()
{
	m_iImmortal = 0;
}

bool CvUnit::isImmuneToCapture() const
{
	return m_iImmuneToCapture == 0 ? false : true;
}

void CvUnit::changeImmuneToCapture(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iImmuneToCapture += iNewValue;
    }
}

bool CvUnit::isImmuneToDefensiveStrike() const
{
	return m_iImmuneToDefensiveStrike == 0 ? false : true;
}

void CvUnit::changeImmuneToDefensiveStrike(int iChange)
{
    if (iChange != 0)
    {
        m_iImmuneToDefensiveStrike += iChange;
    }
}

bool CvUnit::isImmuneToFear() const
{
    if(!isAlive())
    {
        return true;
    }
	return m_iImmuneToFear == 0 ? false : true;
}

void CvUnit::changeImmuneToFear(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iImmuneToFear += iNewValue;
    }
}

bool CvUnit::isImmuneToMagic() const
{
	return m_iImmuneToMagic == 0 ? false : true;
}

void CvUnit::changeImmuneToMagic(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iImmuneToMagic += iNewValue;
    }
}

bool CvUnit::isInvisibleFromPromotion() const
{
	return m_iInvisible == 0 ? false : true;
}

void CvUnit::changeInvisibleFromPromotion(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iInvisible += iNewValue;
        if (!isInvisibleFromPromotion() && plot()->isVisibleEnemyUnit(this))
        {
            if (getDomainType() != DOMAIN_IMMOBILE)
            {
				// lfgr fix 01/2021: Do not kill the unit, since this function might be called from anywhere.
                withdrawlToNearestValidPlot( false );
            }
        }
    }
}

bool CvUnit::isSeeInvisible() const
{
	return m_iSeeInvisible == 0 ? false : true;
}

void CvUnit::changeSeeInvisible(int iNewValue)
{
    if (iNewValue != 0)
    {
		// Tholal AI - Bugfix for seeInvisible promotions (by Red Key)
		plot()->changeAdjacentSight(getTeam(), visibilityRange(), false, this, true);

        m_iSeeInvisible += iNewValue;

		plot()->changeAdjacentSight(getTeam(), visibilityRange(), true, this, true);
		// End Tholal AI
    }
}

void CvUnit::changeOnlyDefensive(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iOnlyDefensive += iNewValue;
    }
}

bool CvUnit::isTargetWeakestUnit() const
{
	return m_iTargetWeakestUnit == 0 ? false : true;
}

void CvUnit::changeTargetWeakestUnit(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iTargetWeakestUnit += iNewValue;
    }
}

bool CvUnit::isTargetWeakestUnitCounter() const
{
	return m_iTargetWeakestUnitCounter == 0 ? false : true;
}

void CvUnit::changeTargetWeakestUnitCounter(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iTargetWeakestUnitCounter += iNewValue;
    }
}

bool CvUnit::isTwincast() const
{
	return m_iTwincast == 0 ? false : true;
}

void CvUnit::changeTwincast(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iTwincast += iNewValue;
    }
}

bool CvUnit::isWaterWalking() const
{
	return m_iWaterWalking == 0 ? false : true;
}

void CvUnit::changeWaterWalking(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iWaterWalking += iNewValue;
    }
}

int CvUnit::getBetterDefenderThanPercent() const
{
	return m_iBetterDefenderThanPercent;
}

void CvUnit::changeBetterDefenderThanPercent(int iChange)
{
	if (iChange != 0)
	{
		m_iBetterDefenderThanPercent = (m_iBetterDefenderThanPercent + iChange);
	}
}

int CvUnit::getCombatHealPercent() const
{
	return m_iCombatHealPercent;
}

void CvUnit::changeCombatHealPercent(int iChange)
{
	if (iChange != 0)
	{
		m_iCombatHealPercent = (m_iCombatHealPercent + iChange);
	}
}

void CvUnit::calcCombatLimit()
{
    int iBestValue = m_pUnitInfo->getCombatLimit();
    int iValue = 0;
   	for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
	{
		if (isHasPromotion((PromotionTypes)iI))
		{
		    iValue = GC.getPromotionInfo((PromotionTypes)iI).getCombatLimit();
            if (iValue != 0)
            {
                if (iValue < iBestValue)
                {
                    iBestValue = iValue;
                }
            }
		}
	}
	m_iCombatLimit = iBestValue;
}

int CvUnit::getCombatPercentInBorders() const
{
	return m_iCombatPercentInBorders;
}

void CvUnit::changeCombatPercentInBorders(int iChange)
{
	if (iChange != 0)
	{
		m_iCombatPercentInBorders = (m_iCombatPercentInBorders + iChange);
		setInfoBarDirty(true);
	}
}

int CvUnit::getCombatPercentGlobalCounter() const
{
	return m_iCombatPercentGlobalCounter;
}

void CvUnit::changeCombatPercentGlobalCounter(int iChange)
{
	if (iChange != 0)
	{
		m_iCombatPercentGlobalCounter = (m_iCombatPercentGlobalCounter + iChange);
		setInfoBarDirty(true);
	}
}

int CvUnit::getFreePromotionPick() const
{
	return m_iFreePromotionPick;
}

void CvUnit::changeFreePromotionPick(int iChange)
{
    if (iChange != 0)
    {
        m_iFreePromotionPick = getFreePromotionPick() + iChange;
    }
}

int CvUnit::getGoldFromCombat() const
{
	return m_iGoldFromCombat;
}

void CvUnit::changeGoldFromCombat(int iChange)
{
    if (iChange != 0)
    {
        m_iGoldFromCombat = getGoldFromCombat() + iChange;
    }
}

void CvUnit::setGroupSize(int iNewValue)
{
    m_iGroupSize = iNewValue;
}

void CvUnit::mutate()
{
    int iMutationChance = GC.defines.iMUTATION_CHANCE;
   	for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
	{
		if (GC.getPromotionInfo((PromotionTypes)iI).isMutation())
		{
//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/14
//			if (GC.getGameINLINE().getSorenRandNum(100, "Mutation") <= iMutationChance)
			if (GC.getGameINLINE().getSorenRandNum(100, "Mutation") < iMutationChance)
//<<<<Unofficial Bug Fix: End Modify
			{
				setHasPromotion(((PromotionTypes)iI), true);
			}
		}
	}
}

int CvUnit::getWithdrawlProbDefensive() const
{
    if (getImmobileTimer() > 0)
    {
        return 0;
    }

	return std::max(0, (m_pUnitInfo->getWithdrawlProbDefensive() + getExtraWithdrawal()));
}

void CvUnit::setInvisibleType(int iNewValue)
{
    m_iInvisibleType = iNewValue;
}

int CvUnit::getRace() const
{
	return m_iRace;
}

void CvUnit::setRace(int iNewValue)
{
    if (m_iRace != NO_PROMOTION)
    {
        setHasPromotion((PromotionTypes)m_iRace, false);
    }
	m_iRace = iNewValue;
}

int CvUnit::getReligion() const
{
	return m_iReligion;
}

void CvUnit::setReligion(int iReligion)
{
	m_iReligion = iReligion;

	updateTerraformer(); // lfgr 05/2022
}

int CvUnit::getResist() const
{
	return m_iResist;
}

void CvUnit::setResist(int iNewValue)
{
	m_iResist = iNewValue;
}

void CvUnit::changeResist(int iChange)
{
	setResist(getResist() + iChange);
}

int CvUnit::getResistModify() const
{
	return m_iResistModify;
}

void CvUnit::setResistModify(int iNewValue)
{
	m_iResistModify = iNewValue;
}

void CvUnit::changeResistModify(int iChange)
{
	setResistModify(getResistModify() + iChange);
}

int CvUnit::getScenarioCounter() const
{
	return m_iScenarioCounter;
}

void CvUnit::setScenarioCounter(int iNewValue)
{
	m_iScenarioCounter = iNewValue;
}

int CvUnit::getSpellCasterXP() const
{
    if (!m_pUnitInfo->isFreeXP())
    {
        return 0;
    }
	return m_iSpellCasterXP;
}

void CvUnit::changeSpellCasterXP(int iChange)
{
    if (iChange != 0)
    {
        m_iSpellCasterXP += iChange;
    }
}

int CvUnit::getSpellDamageModify() const
{
	return m_iSpellDamageModify;
}

void CvUnit::changeSpellDamageModify(int iChange)
{
    if (iChange != 0)
    {
        m_iSpellDamageModify += iChange;
    }
}

int CvUnit::getSummoner() const
{
	return m_iSummoner;
}

void CvUnit::setSummoner(int iNewValue)
{
    m_iSummoner = iNewValue;
}

int CvUnit::getWorkRateModify() const
{
	return m_iWorkRateModify;
}

void CvUnit::changeWorkRateModify(int iChange)
{
    if (iChange != 0)
    {
        m_iWorkRateModify += iChange;
    }
}

bool CvUnit::isResisted(CvUnit* pCaster, int iSpell) const
{
//>>>>Unofficial Bug Fix: Modified by Denev 2009/11/15
//	if (GC.getGameINLINE().getSorenRandNum(100, "is Resisted") <= getResistChance(pCaster, iSpell))
	if (GC.getGameINLINE().getSorenRandNum(100, "is Resisted") < getResistChance(pCaster, iSpell))
//<<<<Unofficial Bug Fix: End Modify
	{
		gDLL->getInterfaceIFace()->addMessage(getOwner(), true, GC.getEVENT_MESSAGE_TIME(), gDLL->getText("TXT_KEY_MESSAGE_SPELL_RESISTED", getName().GetCString(), GC.getSpellInfo((SpellTypes)iSpell).getDescription()), "", MESSAGE_TYPE_MAJOR_EVENT, "art/interface/buttons/promotions/magicresistance.dds", (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), getX_INLINE(), getY_INLINE(), true, true);
		gDLL->getInterfaceIFace()->addMessage(pCaster->getOwner(), true, GC.getEVENT_MESSAGE_TIME(), gDLL->getText("TXT_KEY_MESSAGE_SPELL_RESISTED", getName().GetCString(), GC.getSpellInfo((SpellTypes)iSpell).getDescription()), "", MESSAGE_TYPE_MAJOR_EVENT, "art/interface/buttons/promotions/magicresistance.dds", (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), getX_INLINE(), getY_INLINE(), true, true);
		gDLL->getInterfaceIFace()->playGeneralSound("AS3D_RESIST", plot()->getPoint());
		return true;
	}
	return false;
}

int CvUnit::getResistChance(CvUnit* pCaster, int iSpell) const
{
    if (isImmuneToSpell(pCaster, iSpell))
    {
        return 100;
    }
    int iResist = GC.defines.iSPELL_RESIST_CHANCE_BASE;
	iResist += getLevel() * 5;
    iResist += getResist();
    iResist += pCaster->getResistModify();
    iResist += GC.getSpellInfo((SpellTypes)iSpell).getResistModify();
    iResist += GET_PLAYER(getOwnerINLINE()).getResistModify();
    iResist += GET_PLAYER(pCaster->getOwnerINLINE()).getResistEnemyModify();
    if (plot()->isCity())
    {
        iResist += 10;
        iResist += plot()->getPlotCity()->getResistMagic();
    }
	if (iResist >= GC.defines.iSPELL_RESIST_CHANCE_MAX)
	{
		iResist = GC.defines.iSPELL_RESIST_CHANCE_MAX;
	}
	if (iResist <= GC.defines.iSPELL_RESIST_CHANCE_MIN)
	{
		iResist = GC.defines.iSPELL_RESIST_CHANCE_MIN;
	}
	return iResist;
}

void CvUnit::changeBaseCombatStr(int iChange)
{
	setBaseCombatStr(m_iBaseCombat + iChange);
}

void CvUnit::changeBaseCombatStrDefense(int iChange)
{
	setBaseCombatStrDefense(m_iBaseCombatDefense + iChange);
}

int CvUnit::getUnitArtStyleType() const
{
	return m_iUnitArtStyleType;
}

void CvUnit::setUnitArtStyleType(int iNewValue)
{
	m_iUnitArtStyleType = iNewValue;
}

int CvUnit::chooseSpell()
{
    int iBestSpell = -1;
    int iRange;
    int iTempValue;
    int iValue;
    int iBestSpellValue = 0;
    CvPlot* pLoopPlot;
    CvUnit* pLoopUnit;
    CLLNode<IDInfo>* pUnitNode;

    for (int iSpell = 0; iSpell < GC.getNumSpellInfos(); iSpell++)
    {
        iValue = 0;
        if (canCast(iSpell, false))
        {
			CvSpellInfo& kSpellInfo = GC.getSpellInfo((SpellTypes)iSpell);

			if (kSpellInfo.isAllowAI())
			{
				iRange = kSpellInfo.getRange();
				if (kSpellInfo.getCreateUnitType() != NO_UNIT)
				{
					CvUnitInfo& kUnitInfo = GC.getUnitInfo((UnitTypes)kSpellInfo.getCreateUnitType());

					int iMoveRange = kUnitInfo.getMoves() + getExtraSpellMove();
					bool bPermSummon = kSpellInfo.isPermanentUnitCreate();
					bool bEnemy = false;
					bool isBombardSummon = false;
					if (kUnitInfo.getBombardRate() > 0)
					{
						isBombardSummon = true;
					}

					//check promotions for movement bonus
					for (int iPromotions = 0; iPromotions < GC.getNumPromotionInfos(); iPromotions++)
					{
						if (kUnitInfo.getFreePromotions(iPromotions))
						{
							CvPromotionInfo& kSummonPromotionInfo =  GC.getPromotionInfo((PromotionTypes)iPromotions);
							// mainly to account for the Flying promo but will catch other changes to movement
							iMoveRange += kSummonPromotionInfo.getMovesChange();

							// ToDo - any other useful info we can get from a summoned unit based on the free promotions it receives?
						}
					}

					for (int i = -iMoveRange; i <= iMoveRange; ++i)
					{
						for (int j = -iMoveRange; j <= iMoveRange; ++j)
						{
							pLoopPlot = ::plotXY(plot()->getX_INLINE(), plot()->getY_INLINE(), i, j);
							if (NULL != pLoopPlot)
							{
								if (pLoopPlot->isVisibleEnemyUnit(this))
								{
									bEnemy = true;
								}
								if (pLoopPlot->isCity() && GET_TEAM(pLoopPlot->getTeam()).isAtWar(getTeam()))
								{
									if (isBombardSummon)
									{
										bEnemy = true;
									}
								}
							}
						}
					}
					if (bEnemy || bPermSummon)
					{
						iTempValue = GC.getUnitInfo((UnitTypes)kSpellInfo.getCreateUnitType()).getCombat();
						for (int iI = 0; iI < GC.getNumDamageTypeInfos(); iI++)
						{
							iTempValue += GC.getUnitInfo((UnitTypes)kSpellInfo.getCreateUnitType()).getDamageTypeCombat(iI);
						}

						iTempValue += (GC.getUnitInfo((UnitTypes)kSpellInfo.getCreateUnitType()).getCollateralDamage() / 10);

						iTempValue *= 100;
						iTempValue *= kSpellInfo.getCreateUnitNum();

						if (bPermSummon)
						{
							iTempValue *= 2;
						}

						if (isTwincast())
						{
							iTempValue *= 2;
						}
						if (gUnitLogLevel > 3) logBBAI("      ....spell %S (summon value: %d)", kSpellInfo.getDescription(), iTempValue); 
						iValue += iTempValue;
					}
					// Severed Souls & Floating Eyes
					if ((GC.getUnitInfo((UnitTypes)kSpellInfo.getCreateUnitType()).getInvisibleType() != NO_INVISIBLE) ||
						(GC.getUnitInfo((UnitTypes)kSpellInfo.getCreateUnitType()).getNumSeeInvisibleTypes() > 0))
					{
						iValue += 25;
					}
				}

				// extra code for Tsunami since all of its effects are hidden in python
				bool bIsCoastalSpell = kSpellInfo.isAdjacentToWaterOnly();

				if (kSpellInfo.getDamage() != 0 || (bIsCoastalSpell))// && !bPermSummon))
				{
					int iDmg = kSpellInfo.getDamage();
					int iDmgLimit = kSpellInfo.getDamageLimit();

					if (bIsCoastalSpell)
					{
						iDmg = 30;
						iDmgLimit = 75;
					}

					bool bIsCityPlot = false;
					
					for (int i = -iRange; i <= iRange; ++i)
					{
						for (int j = -iRange; j <= iRange; ++j)
						{
							pLoopPlot = ::plotXY(plot()->getX_INLINE(), plot()->getY_INLINE(), i, j);

							if (NULL != pLoopPlot)
							{
								bIsCityPlot = pLoopPlot->isCity();

								if (bIsCoastalSpell && !pLoopPlot->isAdjacentToWater())
								{
									//do nothing - spell doesn't apply to this plot (Tsunami)
								}
								else
								{
									if (pLoopPlot->getX() != plot()->getX() || pLoopPlot->getY() != plot()->getY())
									{
										pUnitNode = pLoopPlot->headUnitNode();
										while (pUnitNode != NULL)
										{
											pLoopUnit = ::getUnit(pUnitNode->m_data);
											pUnitNode = pLoopPlot->nextUnitNode(pUnitNode);
											if (!pLoopUnit->isImmuneToSpell(this, iSpell))
											{
												if (pLoopUnit->isEnemy(getTeam()))
												{
													if (pLoopUnit->getDamage() < iDmgLimit)
													{
														iValue += iDmg * (10 + pLoopUnit->getLevel());
													}
												}
												if (pLoopUnit->getTeam() == getTeam())
												{
													if (bIsCityPlot)
													{
														iValue -= iDmg * 5;
													}
													else
													{
														iValue -= iDmg * (10 + pLoopUnit->getLevel());
													}
												}
												if (pLoopUnit->getTeam() != getTeam() && pLoopUnit->isEnemy(getTeam()) == false)
												{
													iValue -= 1000;
												}
											}
										}
									}
								}
							}
						}
					}
				}
				
				// Tholal ToDo - fix this. AI_promotionValue gives a value for the promotion for this unit
				// some spells buff only this unit, some team units, some also include allied units - add code to sort that out here
				
				// Tholal ToDo - use the range of the spell for this check - use range check above - maybe even move it further up and gather data about all enemies, friends, etc
				CvPlot* pAdjacentPlot = NULL;
				int iAdjacentEnemyCount = 0;
				for (int iI = 0; iI < NUM_DIRECTION_TYPES; iI++)
				{
					pAdjacentPlot = plotDirection(getX_INLINE(), getY_INLINE(), ((DirectionTypes)iI));
					if( pAdjacentPlot != NULL )
					{
						iAdjacentEnemyCount += pAdjacentPlot->getNumVisibleEnemyDefenders(this);
					}
				}

				if (gUnitLogLevel > 3) logBBAI("      ....iAdjacentEnemyCount: %d", iAdjacentEnemyCount);  //MNAI - level 4 logging
				bool isImmuneTeamSpell = kSpellInfo.isImmuneTeam();  // this means it affects enemies
				if (kSpellInfo.getAddPromotionType1() != NO_PROMOTION)
				{
					if (isImmuneTeamSpell)
					{
						iValue -= AI_promotionValue((PromotionTypes)kSpellInfo.getAddPromotionType1()) * iAdjacentEnemyCount;
					}
					else
					{
						iValue += AI_promotionValue((PromotionTypes)kSpellInfo.getAddPromotionType1());
					}
				}
				if (kSpellInfo.getAddPromotionType2() != NO_PROMOTION)
				{
					iValue += AI_promotionValue((PromotionTypes)kSpellInfo.getAddPromotionType2());
				}
				if (kSpellInfo.getAddPromotionType3() != NO_PROMOTION)
				{
					iValue += AI_promotionValue((PromotionTypes)kSpellInfo.getAddPromotionType3());
				}
				if (kSpellInfo.getRemovePromotionType1() != NO_PROMOTION)
				{
					if (isImmuneTeamSpell)
					{
						iValue += AI_promotionValue((PromotionTypes)kSpellInfo.getRemovePromotionType1());
					}
					else
					{
						iValue -= AI_promotionValue((PromotionTypes)kSpellInfo.getRemovePromotionType1()) * iAdjacentEnemyCount;
					}
				}
				if (kSpellInfo.getRemovePromotionType2() != NO_PROMOTION)
				{
					if (isImmuneTeamSpell) // affects enemies
					{
						//ToDo - actually check for the promotions in nearby enemies
						iValue += AI_promotionValue((PromotionTypes)kSpellInfo.getRemovePromotionType2()) * iAdjacentEnemyCount;
					}
					else
					{
						//ToDo - actually check for the promotions in nearby friends
						iValue -= AI_promotionValue((PromotionTypes)kSpellInfo.getRemovePromotionType2()) * plot()->getNumDefenders(getOwner());
					}
				}
				if (kSpellInfo.getRemovePromotionType3() != NO_PROMOTION)
				{
					if (isImmuneTeamSpell)
					{
						iValue += AI_promotionValue((PromotionTypes)kSpellInfo.getRemovePromotionType3());
					}
					else
					{
						iValue -= AI_promotionValue((PromotionTypes)kSpellInfo.getRemovePromotionType3()) * iAdjacentEnemyCount;
					}
				}

				if (kSpellInfo.getConvertUnitType() != NO_UNIT)
				{
					iValue += GET_PLAYER(getOwnerINLINE()).AI_unitValue((UnitTypes)kSpellInfo.getConvertUnitType(), UNITAI_ATTACK, area());
					iValue -= GET_PLAYER(getOwnerINLINE()).AI_unitValue((UnitTypes)getUnitType(), UNITAI_ATTACK, area());
				}

				if (kSpellInfo.getCreateBuildingType() != NO_BUILDING)
				{
					iValue += plot()->getPlotCity()->AI_buildingValue((BuildingTypes)kSpellInfo.getCreateBuildingType()) * (AI_getUnitAIType() == UNITAI_MAGE ? 10 : 2);
				}

				if (kSpellInfo.getCreateFeatureType() != NO_FEATURE)
				{
					iValue += 10;
				}

				if (kSpellInfo.getCreateImprovementType() != NO_IMPROVEMENT)
				{
					iValue += 10;
				}

				if (kSpellInfo.isDispel())
				{
					if (AI_getUnitAIType() != UNITAI_MANA_UPGRADE)
					{
						iValue += 25 * (iRange + 1) * (iRange + 1);
					}
				}

				if (kSpellInfo.isPush())
				{
					iValue += 20 * (iRange + 1) * (iRange + 1);
					if (plot()->isCity())
					{
						iValue *= 3;
					}
				}

				if (kSpellInfo.getSpreadReligion() != NO_RELIGION)
				{
					if (!GC.getGameINLINE().isReligionFounded(ReligionTypes(kSpellInfo.getSpreadReligion())))
					{
						iValue += 500;
					}
					else if (kSpellInfo.getSpreadReligion() == GET_PLAYER(getOwner()).getStateReligion())
					{
						iValue += 100;
					}
				}

				if (kSpellInfo.getChangePopulation() != 0)
				{
					// ToDo - make this actually look at the city and see if it needs population (check health, happy)
					// also need to make sure we dont break spells that reduce pop
					iValue += (500 * kSpellInfo.getChangePopulation() - (plot()->getPlotCity()->getPopulation() * 5));
				}

				if (kSpellInfo.getCost() != 0)
				{
					int iCost = info_utils::getRealSpellCost( getOwnerINLINE(), (SpellTypes) iSpell );
					iValue += (GET_PLAYER(getOwner()).getGold() - GET_PLAYER(getOwner()).AI_getGoldTreasury(true, true, true, true)) - iCost;
				}

				if (kSpellInfo.getImmobileTurns() != 0)
				{
					iValue += 20 * kSpellInfo.getImmobileTurns() * (iRange + 1) * (iRange + 1);
				}

				if (kSpellInfo.isSacrificeCaster()) // TODO - add a check for financial trouble and/or overabundance of troops
				{
					if (kSpellInfo.getChangePopulation() == 0) // Tholal AI - temporary gate to make sure Manes use the Add to City ability
					{
						iValue -= (getLevel() * 20) * GET_PLAYER(getOwnerINLINE()).AI_unitValue((UnitTypes)getUnitType(), AI_getUnitAIType(), area());
					}
				}

				if (kSpellInfo.isResistable())
				{
					iValue /= 2 + std::max( 0, kSpellInfo.getResistModify() / 10 );
				}

				iValue += kSpellInfo.getAIWeight();

				if (gUnitLogLevel > 3) logBBAI("      ...spell %S (value: %d)", kSpellInfo.getDescription(), iValue); //MNAI - level 4 logging
				if (iValue > iBestSpellValue)
				{
					iBestSpellValue = iValue;
					iBestSpell = iSpell;
				}
			}
        }
    }
	
	if( gUnitLogLevel > 2 && (iBestSpell != -1))
	{
		logBBAI("    %S (Unit %d - %S) Best Spell - %S (value: %d) \n",  getName().GetCString(), getID(), GC.getUnitAIInfo(AI_getUnitAIType()).getDescription(), GC.getSpellInfo((SpellTypes)iBestSpell).getDescription(), iBestSpellValue);
	}

    return iBestSpell;
}

int CvUnit::getExtraSpellMove() const
{
    int iCount = 0;
	for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
	{
	    if (isHasPromotion((PromotionTypes)iI))
	    {
	        if (GC.getPromotionInfo((PromotionTypes)iI).getPromotionSummonPerk() != NO_PROMOTION)
	        {
	            iCount += GC.getPromotionInfo((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iI).getPromotionSummonPerk()).getMovesChange();
	        }
	    }
	}
	return iCount;
}

void CvUnit::doDamage(int iDmg, int iDmgLimit, CvUnit* pAttacker, int iDmgType, bool bStartWar)
{
    CvWString szMessage;
    int iResist;

    iResist = baseCombatStrDefense() *2;
    iResist += getLevel() * 2;
	if (plot()->getPlotCity() != NULL)
	{
		iResist += (plot()->getPlotCity()->getDefenseModifier(false) / 4);
	}
	if (iDmgType != -1)
	{
		iResist += getDamageTypeResist((DamageTypes)iDmgType);
	}
//>>>>Unofficial Bug Fix:  Modified by Denev 2010/01/07
//	if (pAttacker != NULL && iDmgType != DAMAGE_PHYSICAL)
    if (pAttacker != NULL && iDmgType != GC.getInfoTypeForString("DAMAGE_PHYSICAL"))
//<<<<Unofficial Bug Fix:  End Modify
	{
		iDmg += pAttacker->getSpellDamageModify();
	}
	if (iResist < 100)
	{
		iDmg = GC.getGameINLINE().getSorenRandNum(iDmg, "Damage") + GC.getGameINLINE().getSorenRandNum(iDmg, "Damage");
		iDmg = iDmg * (100 - iResist) / 100;

		if (iDmg + getDamage() > iDmgLimit)
		{
			iDmg = iDmgLimit - getDamage();
		}
		if (iDmg > 0)
		{
			if (iDmg + getDamage() >= GC.getMAX_HIT_POINTS())
			{
				szMessage = gDLL->getText("TXT_KEY_MESSAGE_KILLED_BY", m_pUnitInfo->getDescription(), GC.getDamageTypeInfo((DamageTypes)iDmgType).getDescription());
			}
			else
			{
				szMessage = gDLL->getText("TXT_KEY_MESSAGE_DAMAGED_BY", m_pUnitInfo->getDescription(), iDmg, GC.getDamageTypeInfo((DamageTypes)iDmgType).getDescription());
			}
			gDLL->getInterfaceIFace()->addMessage((getOwnerINLINE()), true, GC.getEVENT_MESSAGE_TIME(), szMessage, "", MESSAGE_TYPE_MAJOR_EVENT, GC.getDamageTypeInfo((DamageTypes)iDmgType).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), getX_INLINE(), getY_INLINE(), true, true);
			if (pAttacker != NULL && pAttacker != this)
			{
				gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)pAttacker->getOwner()), true, GC.getEVENT_MESSAGE_TIME(), szMessage, "", MESSAGE_TYPE_MAJOR_EVENT, GC.getDamageTypeInfo((DamageTypes)iDmgType).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), getX_INLINE(), getY_INLINE(), true, true);
				changeDamage(iDmg, pAttacker->getOwner());
				if (getDamage() >= GC.getMAX_HIT_POINTS())
				{
					logBBAI("    Killing %S (delayed) -- received deadly damage from attacker in doDamage() (Unit %d - plot: %d, %d)",
							getName().GetCString(), getID(), getX(), getY());
					kill(true,pAttacker->getOwner());
				}
				if (bStartWar)
				{
					if (!(pAttacker->isHiddenNationality()) && !(isHiddenNationality()))
					{
/*************************************************************************************************/
/**	GAMECHANGE (Different condition for Areaspells to trigger war) Sephi       					**/
/**																								**/
/**						                                            							**/
/*************************************************************************************************/
/** orig
                        if (getTeam() != pAttacker->getTeam())
                        {
                            if (!GET_TEAM(pAttacker->getTeam()).isPermanentWarPeace(getTeam()))
                            {
                                GET_TEAM(pAttacker->getTeam()).declareWar(getTeam(), false, WARPLAN_TOTAL);
                            }
                        }
**/
                        if (getTeam()==plot()->getTeam())
                        {
                            if (!GET_TEAM(getTeam()).isVassal(pAttacker->getTeam()) && !GET_TEAM(pAttacker->getTeam()).isVassal(getTeam()))
                            {
                                if (getTeam() != pAttacker->getTeam())
                                {
                                    if (!GET_TEAM(pAttacker->getTeam()).isPermanentWarPeace(getTeam()))
                                    {
                                        GET_TEAM(pAttacker->getTeam()).declareWar(getTeam(), false, WARPLAN_TOTAL);
                                    }
                                }
                            }
                        }
/*************************************************************************************************/
/**	END	                                        												**/
/*************************************************************************************************/
                    }
                }
            }
            else
            {
                changeDamage(iDmg, NO_PLAYER);
                if (getDamage() >= GC.getMAX_HIT_POINTS())
                {
					logBBAI("    Killing %S (delayed) -- received deadly damage in doDamage() (Unit %d - plot: %d, %d)",
							getName().GetCString(), getID(), getX(), getY());
                    kill(true,NO_PLAYER);
                }
            }
        }
    }
}

void CvUnit::doDefensiveStrike(CvUnit* pAttacker)
{
    CvUnit* pBestUnit;
    int iBestDamage = 0;
	CvPlot* pPlot = plot();
	CLLNode<IDInfo>* pUnitNode = pPlot->headUnitNode();
	while (pUnitNode != NULL)
	{
		CvUnit* pLoopUnit = ::getUnit(pUnitNode->m_data);
		pUnitNode = pPlot->nextUnitNode(pUnitNode);
        if (pLoopUnit->getDefensiveStrikeChance() > 0)
        {
            if (atWar(pLoopUnit->getTeam(), pAttacker->getTeam()))
            {
                if (pLoopUnit->isBlitz() || !pLoopUnit->isMadeAttack())
                {
                    if (GC.getGameINLINE().getSorenRandNum(100, "Defensive Strike") < pLoopUnit->getDefensiveStrikeChance())
                    {
                        if (pLoopUnit->getDefensiveStrikeDamage() > iBestDamage)
                        {
                            iBestDamage = pLoopUnit->getDefensiveStrikeDamage();
                            pBestUnit = pLoopUnit;
                        }
                    }
                }
            }
        }
	}
	if (iBestDamage > 0)
	{
	    if (!pBestUnit->isBlitz())
	    {
	        pBestUnit->setMadeAttack(true);
	    }
	    int iDmg = 0;
	    iDmg += GC.getGameINLINE().getSorenRandNum(pBestUnit->getDefensiveStrikeDamage(), "Defensive Strike 1");
	    iDmg += GC.getGameINLINE().getSorenRandNum(pBestUnit->getDefensiveStrikeDamage(), "Defensive Strike 2");
        iDmg -= pAttacker->baseCombatStrDefense() * 2;
        iDmg -= pAttacker->getLevel();
        if (iDmg + pAttacker->getDamage() > 95)
        {
            iDmg = 95 - pAttacker->getDamage();
        }
	    if (iDmg > 0)
	    {
			if (gUnitLogLevel >= 4) logBBAI("    %S (%d) takes %d damage from a defensive strike from %S (Unit %d)", pAttacker->getName().GetCString(), pAttacker->getID(), iDmg, pBestUnit->getName().GetCString(), pBestUnit->getID());
            pAttacker->changeDamage(iDmg, pBestUnit->getOwner());
            CvWString szMessage = gDLL->getText("TXT_KEY_MESSAGE_DEFENSIVE_STRIKE_BY", GC.getUnitInfo((UnitTypes)pAttacker->getUnitType()).getDescription(), iDmg, GC.getUnitInfo((UnitTypes)pBestUnit->getUnitType()).getDescription());
            gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)pAttacker->getOwner()), true, GC.defines.iEVENT_MESSAGE_TIME, szMessage, "", MESSAGE_TYPE_MAJOR_EVENT, GC.getUnitInfo((UnitTypes)pBestUnit->getUnitType()).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pAttacker->getX(), pAttacker->getY(), true, true);
            szMessage = gDLL->getText("TXT_KEY_MESSAGE_DEFENSIVE_STRIKE", GC.getUnitInfo((UnitTypes)pBestUnit->getUnitType()).getDescription(), GC.getUnitInfo((UnitTypes)pAttacker->getUnitType()).getDescription(), iDmg);
            gDLL->getInterfaceIFace()->addMessage(((PlayerTypes)pBestUnit->getOwner()), true, GC.defines.iEVENT_MESSAGE_TIME, szMessage, "", MESSAGE_TYPE_MAJOR_EVENT, GC.getUnitInfo((UnitTypes)pBestUnit->getUnitType()).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pAttacker->getX(), pAttacker->getY(), true, true);
            pBestUnit->changeExperience(1, 100, true, false, false);
	    }
	}
}

void CvUnit::doEscape()
{
	CvCity* pCapital = GET_PLAYER(getOwnerINLINE()).getCapitalCity();

    //if (GET_PLAYER(getOwnerINLINE()).getCapitalCity() != NULL)
	if (NULL != pCapital)
    {
		// Tholal AI - catch for Immortal units being killed in their capitol (no need to reset their XY position and it causes an assert when you do so)
		if (pCapital->plot() != plot())
		{
	        setXY(GET_PLAYER(getOwnerINLINE()).getCapitalCity()->getX(), GET_PLAYER(getOwnerINLINE()).getCapitalCity()->getY(), false, true, true);
		}
    }
}

void CvUnit::doImmortalRebirth()
{
    joinGroup(NULL);
    setDamage(75, NO_PLAYER);
    bool bFromProm = false;
   	for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
	{
        if (isHasPromotion((PromotionTypes)iI))
        {
            if (GC.getPromotionInfo((PromotionTypes)iI).isImmortal())
            {
                setHasPromotion(((PromotionTypes)iI), false);
                bFromProm = true;
                break;
            }
		}
	}

	if (!bFromProm)
	{
        changeImmortal(-1);
	}

    doEscape();

	// Sephi AI (Immortal Units heal)
    if (!isHuman())
    {
        getGroup()->pushMission(MISSION_HEAL);
    }
	// Sephi AI End
}

void CvUnit::combatWon(CvUnit* pLoser, bool bAttacking)
{
	PromotionTypes ePromotion;
	bool bConvert = false;
	int iUnit = NO_UNIT; // The unit the winning player gets (capture slave, convert, ...)
	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pLoopUnit;
	CvPlot* pPlot;
//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/22
//*** spawned unit is pushed out if enemy unit exists in the same tile.
//	CvUnit* pUnit;
	CvUnit* pUnit = NULL;
//<<<<Unofficial Bug Fix: End Modify

	// set this to True if the losing unit is auto-captured (ie Worker or Settler for example)
	// we use this to make sure we dont get double units from enslavement or other capture effects
	bool bUnitAutoCapture = (pLoser->getCaptureUnitType(GET_PLAYER(getOwnerINLINE()).getCivilizationType()) != NO_UNIT);

	for (int iI = 0; iI < GC.getNumPromotionInfos(); iI++)
	{
		CvPromotionInfo& kPromotionInfo = GC.getPromotionInfo((PromotionTypes)iI);

		if (isHasPromotion((PromotionTypes)iI))
		{
			if (kPromotionInfo.getFreeXPFromCombat() != 0)
			{
				changeExperience(kPromotionInfo.getFreeXPFromCombat(), -1, false, false, false);
			}
			if (kPromotionInfo.getModifyGlobalCounterOnCombat() != 0)
			{
				if (pLoser->isAlive())
				{
					GC.getGameINLINE().changeGlobalCounter(kPromotionInfo.getModifyGlobalCounterOnCombat());
				}
			}
			if (kPromotionInfo.isRemovedByCombat())
			{
				setHasPromotion(((PromotionTypes)iI), false);
			}
			if (kPromotionInfo.getPromotionCombatApply() != NO_PROMOTION)
			{
				ePromotion = (PromotionTypes)kPromotionInfo.getPromotionCombatApply();
				pPlot = pLoser->plot();
				pUnitNode = pPlot->headUnitNode();
				while (pUnitNode != NULL)
				{
					pLoopUnit = ::getUnit(pUnitNode->m_data);
					pUnitNode = pPlot->nextUnitNode(pUnitNode);
					if (pLoopUnit->isHasPromotion(ePromotion) == false)
					{
						if (isEnemy(pLoopUnit->getTeam()))
						{
							if (pLoopUnit->canAcquirePromotion(ePromotion))
							{
//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/14
//									if (GC.getGameINLINE().getSorenRandNum(100, "Combat Apply") <= GC.defines.iCOMBAT_APPLY_CHANCE)
								if (GC.getGameINLINE().getSorenRandNum(100, "Combat Apply") < GC.defines.iCOMBAT_APPLY_CHANCE)
//<<<<Unofficial Bug Fix: End Modify
								{
									pLoopUnit->setHasPromotion(ePromotion, true);
									gDLL->getInterfaceIFace()->addMessage((PlayerTypes)pLoopUnit->getOwner(), true, GC.getEVENT_MESSAGE_TIME(), GC.getPromotionInfo(ePromotion).getDescription(), "", MESSAGE_TYPE_INFO, GC.getPromotionInfo(ePromotion).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), getX_INLINE(), getY_INLINE(), true, true);
									gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), GC.getPromotionInfo(ePromotion).getDescription(), "", MESSAGE_TYPE_INFO, GC.getPromotionInfo(ePromotion).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), getX_INLINE(), getY_INLINE(), true, true);
								}
							}
						}
					}
				}
			}
			if (kPromotionInfo.getCombatCapturePercent() != 0 && !bUnitAutoCapture)
			{
				if (iUnit == NO_UNIT && pLoser->isAlive())
				{
//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/14
//					if (GC.getGameINLINE().getSorenRandNum(100, "Combat Capture") <= kPromotionInfo.getCombatCapturePercent())
					if (GC.getGameINLINE().getSorenRandNum(100, "Combat Capture") < kPromotionInfo.getCombatCapturePercent())
//<<<<Unofficial Bug Fix: End Modify
					{
						iUnit = pLoser->getUnitType();
						bConvert = true;
					}
				}
			}
			if (kPromotionInfo.getCaptureUnitCombat() != NO_UNITCOMBAT && !bUnitAutoCapture)
			{
				if (iUnit == NO_UNIT && pLoser->getUnitCombatType() == kPromotionInfo.getCaptureUnitCombat())
				{
					iUnit = pLoser->getUnitType();
					bConvert = true;
				}
			}
		}
		if (pLoser->isHasPromotion((PromotionTypes)iI))
		{
			if (kPromotionInfo.getPromotionCombatApply() != NO_PROMOTION)
			{
				ePromotion = (PromotionTypes)kPromotionInfo.getPromotionCombatApply();
				if (isHasPromotion(ePromotion) == false)
				{
					if (pLoser->isEnemy(getTeam()))
					{
						if (canAcquirePromotion(ePromotion))
						{
							//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/14
							//if (GC.getGameINLINE().getSorenRandNum(100, "Combat Apply") <= GC.defines.iCOMBAT_APPLY_CHANCE)
							if (GC.getGameINLINE().getSorenRandNum(100, "Combat Apply") < GC.defines.iCOMBAT_APPLY_CHANCE)
							//<<<<Unofficial Bug Fix: End Modify
							{
								setHasPromotion(ePromotion, true);
								gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), GC.getPromotionInfo(ePromotion).getDescription(), "", MESSAGE_TYPE_INFO, GC.getPromotionInfo(ePromotion).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), getX_INLINE(), getY_INLINE(), true, true);
								gDLL->getInterfaceIFace()->addMessage((PlayerTypes)pLoser->getOwner(), true, GC.getEVENT_MESSAGE_TIME(), GC.getPromotionInfo(ePromotion).getDescription(), "", MESSAGE_TYPE_INFO, GC.getPromotionInfo(ePromotion).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), getX_INLINE(), getY_INLINE(), true, true);
							}
						}
					}
				}
			}
		}
	}
	if (GET_PLAYER(getOwnerINLINE()).getFreeXPFromCombat() != 0)
	{
		changeExperience(GET_PLAYER(getOwnerINLINE()).getFreeXPFromCombat(), -1, false, false, false);
	}
	if (getCombatHealPercent() != 0)
	{
		if (pLoser->isAlive())
		{
			int i = getCombatHealPercent();
			if (i > getDamage())
			{
				i = getDamage();
			}
			if (i != 0)
			{
				changeDamage(-1 * i, NO_PLAYER);
			}
		}
	}
	if (m_pUnitInfo->isExplodeInCombat() && m_pUnitInfo->isSuicide())
	{
		if (bAttacking)
		{
			pPlot = pLoser->plot();
		}
		else
		{
			pPlot = plot();
		}
		if (plot()->isVisibleToWatchingHuman())
		{
			gDLL->getEngineIFace()->TriggerEffect((EffectTypes)GC.getInfoTypeForString("EFFECT_ARTILLERY_SHELL_EXPLODE"), pPlot->getPoint(), (float)(GC.getASyncRand().get(360)));
			gDLL->getInterfaceIFace()->playGeneralSound("AS3D_UN_GRENADE_EXPLODE", pPlot->getPoint());
		}
	}
	if (GC.getUnitInfo(pLoser->getUnitType()).isExplodeInCombat())
	{
		if (plot()->isVisibleToWatchingHuman())
		{
			gDLL->getEngineIFace()->TriggerEffect((EffectTypes)GC.getInfoTypeForString("EFFECT_ARTILLERY_SHELL_EXPLODE"), plot()->getPoint(), (float)(GC.getASyncRand().get(360)));
			gDLL->getInterfaceIFace()->playGeneralSound("AS3D_UN_GRENADE_EXPLODE", plot()->getPoint());
		}
	}
	if (!bUnitAutoCapture) // Tholal Bugfix - we dont also get slaves from units we capture
	{
		if ((m_pUnitInfo->getEnslavementChance() + GET_PLAYER(getOwnerINLINE()).getEnslavementChance()) > 0)
		{
			// Summons, non-Alive units, Animals and World class units cannot become slaves
			if (getDuration() == 0 && pLoser->isAlive() && !pLoser->isAnimal() && iUnit == NO_UNIT && !isWorldUnitClass((UnitClassTypes)pLoser->getUnitClassType()))
			{
				if (GC.getGameINLINE().getSorenRandNum(100, "Enslavement") < (m_pUnitInfo->getEnslavementChance() + GET_PLAYER(getOwnerINLINE()).getEnslavementChance()))
				{
					iUnit = GC.defines.iSLAVE_UNIT;
				}
			}
		}
	}
	if (m_pUnitInfo->getPromotionFromCombat() != NO_PROMOTION)
	{
		if (pLoser->isAlive())
		{
			setHasPromotion((PromotionTypes)m_pUnitInfo->getPromotionFromCombat(), true);
		}
	}
	if (getGoldFromCombat() != 0)
	{
		// doesnt work on animals or temporary summons
		if (!pLoser->isAnimal() && !(pLoser->getDuration() > 0))
		{
			// also wont work on angels, avatars, demons, elementals, golem, illusions, puppets, undead
			if (pLoser->isAlive() || (pLoser->getUnitCombatType() == GC.getInfoTypeForString("UNITCOMBAT_NAVAL")))
			{
				GET_PLAYER(getOwnerINLINE()).changeGold(getGoldFromCombat());
				CvWString szBuffer = gDLL->getText("TXT_KEY_MESSAGE_GOLD_FROM_COMBAT", getGoldFromCombat()).GetCString();
				gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_GOODY_GOLD", MESSAGE_TYPE_INFO, getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_WHITE"), getX_INLINE(), getY_INLINE(), true, true);
			}
		}
	}
	if (getDuration() > 0)
	{
		changeDuration(m_pUnitInfo->getDurationFromCombat());
	}
//>>>>Unofficial Bug Fix:  Modified by Denev 2010/01/07
//	if (pLoser->getDamageTypeCombat(DAMAGE_POISON) > 0 && GC.defines.iPOISONED_PROMOTION != -1)
	if (pLoser->getDamageTypeCombat((DamageTypes)GC.getInfoTypeForString("DAMAGE_POISON")) > 0 && GC.defines.iPOISONED_PROMOTION != -1)
//<<<<Unofficial Bug Fix:  End Modify
	{
		if (isAlive() && getDamage() > 0)
		{
			if (GC.getGameINLINE().getSorenRandNum(100, "Poisoned") >= getDamageTypeResist((DamageTypes)GC.getInfoTypeForString("DAMAGE_POISON")))
			{
				setHasPromotion((PromotionTypes)GC.defines.iPOISONED_PROMOTION, true);
			}
		}
	}
	if (m_pUnitInfo->getUnitCreateFromCombat() != NO_UNIT)
	{
		if (!pLoser->isImmuneToCapture() && pLoser->isAlive() && GC.getUnitInfo((UnitTypes)pLoser->getUnitType()).getEquipmentPromotion() == NO_PROMOTION)
		{
			if (GC.getGameINLINE().getSorenRandNum(100, "Create Unit from Combat") < m_pUnitInfo->getUnitCreateFromCombatChance())
			{
//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/22
//*** spawned unit is pushed out if enemy unit exists in the same tile.
//				pUnit = GET_PLAYER(getOwnerINLINE()).initUnit((UnitTypes)m_pUnitInfo->getUnitCreateFromCombat(), plot()->getX_INLINE(), plot()->getY_INLINE());
				pUnit = GET_PLAYER(getOwnerINLINE()).initUnit((UnitTypes)m_pUnitInfo->getUnitCreateFromCombat(), plot()->getX_INLINE(), plot()->getY_INLINE(), NO_UNITAI, DIRECTION_SOUTH, false);
//<<<<Unofficial Bug Fix: End Modify
				pUnit->setDuration(getDuration());
				if (isHiddenNationality())
				{
					pUnit->setHasPromotion((PromotionTypes)GC.defines.iHIDDEN_NATIONALITY_PROMOTION, true);
				}
//>>>>Unofficial Bug Fix: Added by Denev 2010/02/22
//*** spawned unit is pushed out if enemy unit exists in the same tile.
				if (pUnit->plot()->isVisibleEnemyUnit(getOwnerINLINE()))
				{
					pUnit->withdrawlToNearestValidPlot();
				}
//<<<<Unofficial Bug Fix: End Add
				iUnit = NO_UNIT;
			}
		}
	}
	
	CvWString szBuffer;
	
	if (iUnit != NO_UNIT)
	{ // We will create a unit from combat (e.g. by converting the old one)
		if ((!pLoser->isImmuneToCapture() && !isNoCapture() && !pLoser->isImmortal())
		  || GC.getUnitInfo((UnitTypes)pLoser->getUnitType()).getEquipmentPromotion() != NO_PROMOTION)
		{
//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/22
//*** captured or enslaved  unit is pushed out if enemy unit exists in the same tile.
//			pUnit = GET_PLAYER(getOwnerINLINE()).initUnit((UnitTypes)iUnit, plot()->getX_INLINE(), plot()->getY_INLINE());

			bool bActsAsCity = false; // check for fort improvements
			if (pLoser->plot()->getImprovementType() != NO_IMPROVEMENT)
			{
				CvImprovementInfo &kImprovementInfo = GC.getImprovementInfo(pLoser->plot()->getImprovementType());
				if (kImprovementInfo.isActsAsCity())
				{
					bActsAsCity = true;
				}
			}

			if (isBoarding() && !pLoser->plot()->isCity() && !bActsAsCity)
			{
				// boarded ships stay in their plot
				// lfgr 09/2019: Don't push out existing units (i.e. the loser!)
				pUnit = GET_PLAYER(getOwnerINLINE()).initUnit((UnitTypes)iUnit, pLoser->plot()->getX_INLINE(), pLoser->plot()->getY_INLINE(), NO_UNITAI, DIRECTION_SOUTH, false);
				pUnit->load();
			}
			else
			{
				pUnit = GET_PLAYER(getOwnerINLINE()).initUnit((UnitTypes)iUnit, plot()->getX_INLINE(), plot()->getY_INLINE(), NO_UNITAI, DIRECTION_SOUTH, false);
			}
//<<<<Unofficial Bug Fix: End Modify
			if (getDuration() != 0)
			{
				pUnit->setDuration(getDuration());
			}
			if (iUnit == GC.defines.iSLAVE_UNIT)
			{
				pUnit->setRace(NO_PROMOTION); // We clear Race to make sure Slaves dont end up with the incorrect Race
				if (pLoser->getRace() != NO_PROMOTION)
				{
					pUnit->setHasPromotion((PromotionTypes)pLoser->getRace(), true);
				}
			}

			// Tholal AI - captured animals
			if (pUnit->isAnimal())
            {
                pUnit->AI_setUnitAIType(UNITAI_COUNTER);
            }
			// End Tholal AI

			if (bConvert)
			{
				pLoser->setDamage(75, NO_PLAYER, false);
				pUnit->convert(pLoser);
			}
//>>>>Unofficial Bug Fix: Added by Denev 2010/02/22
//*** captured or enslaved  unit is pushed out if enemy unit exists in the same tile.
				if (pUnit->plot()->isVisibleEnemyUnit(getOwnerINLINE()))
				{
					pUnit->withdrawlToNearestValidPlot();
				}
//<<<<Unofficial Bug Fix: End Add
			szBuffer = gDLL->getText("TXT_KEY_MISC_YOU_CAPTURED_UNIT", pUnit->getNameKey());
			gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_UNITCAPTURE", MESSAGE_TYPE_INFO, pUnit->getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), pUnit->getX_INLINE(), pUnit->getY_INLINE());

			szBuffer = gDLL->getText("TXT_KEY_MISC_YOUR_UNIT_CAPTURED", pUnit->getNameKey());
			gDLL->getInterfaceIFace()->addMessage(pLoser->getOwner(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_UNITCAPTURE", MESSAGE_TYPE_INFO, pUnit->getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pUnit->getX_INLINE(), pUnit->getY_INLINE());

		}
	}
	else if (bUnitAutoCapture) // text message for captured workers
	{
		szBuffer = gDLL->getText("TXT_KEY_MISC_YOUR_UNIT_CAPTURED", pLoser->getNameKey());
		gDLL->getInterfaceIFace()->addMessage(pLoser->getOwner(), true, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_UNITCAPTURE", MESSAGE_TYPE_INFO, pLoser->getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"), pLoser->getX_INLINE(), pLoser->getY_INLINE());
	}

	if (!CvString(GC.getUnitInfo(getUnitType()).getPyPostCombatWon()).empty())
    {
        CyUnit* pyCaster = new CyUnit(this);
        CyUnit* pyOpponent = new CyUnit(pLoser);
        CyArgsList argsList;
        argsList.add(gDLL->getPythonIFace()->makePythonObject(pyCaster));	// pass in unit class
        argsList.add(gDLL->getPythonIFace()->makePythonObject(pyOpponent));	// pass in unit class
        gDLL->getPythonIFace()->callFunction(PYSpellModule, "postCombatWon", argsList.makeFunctionArgs()); //, &lResult
        delete pyCaster; // python fxn must not hold on to this pointer
        delete pyOpponent; // python fxn must not hold on to this pointer
    }
	if (!CvString(GC.getUnitInfo(pLoser->getUnitType()).getPyPostCombatLost()).empty())
	{
		CyUnit* pyCaster = new CyUnit(pLoser);
		CyUnit* pyOpponent = new CyUnit(this);
		CyArgsList argsList;
		argsList.add(gDLL->getPythonIFace()->makePythonObject(pyCaster));	// pass in unit class
		argsList.add(gDLL->getPythonIFace()->makePythonObject(pyOpponent));	// pass in unit class
		gDLL->getPythonIFace()->callFunction(PYSpellModule, "postCombatLost", argsList.makeFunctionArgs()); //, &lResult
		delete pyCaster; // python fxn must not hold on to this pointer
		delete pyOpponent; // python fxn must not hold on to this pointer
	}
	if (m_pUnitInfo->getUnitConvertFromCombat() != NO_UNIT)
	{
//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/14
//		if (GC.getGameINLINE().getSorenRandNum(100, "Convert Unit from Combat") <= m_pUnitInfo->getUnitConvertFromCombatChance())
		if (GC.getGameINLINE().getSorenRandNum(100, "Convert Unit from Combat") < m_pUnitInfo->getUnitConvertFromCombatChance())
//<<<<Unofficial Bug Fix: End Modify
		{
			pUnit = GET_PLAYER(getOwnerINLINE()).initUnit((UnitTypes)m_pUnitInfo->getUnitConvertFromCombat(), getX_INLINE(), getY_INLINE(), AI_getUnitAIType());
			pUnit->convert(this);
		}
	}
}

void CvUnit::setWeapons()
{
	CvPlot* pPlot;
	CvCity* pCity;
    if (GC.defines.iWEAPON_PROMOTION_TIER1 == -1)
    {
        return;
    }
	pPlot = plot();
    if (pPlot->isCity())
    {
        pCity = pPlot->getPlotCity();
        if (pCity->getOwner() == getOwner())
        {
            PromotionTypes ePromT1 = (PromotionTypes)GC.defines.iWEAPON_PROMOTION_TIER1;
            PromotionTypes ePromT2 = (PromotionTypes)GC.defines.iWEAPON_PROMOTION_TIER2;
            PromotionTypes ePromT3 = (PromotionTypes)GC.defines.iWEAPON_PROMOTION_TIER3;
            if (isHasPromotion(ePromT3) == false)
            {
                if (pCity->hasBonus((BonusTypes)GC.defines.iWEAPON_REQ_BONUS_TIER3) &&
                  m_pUnitInfo->getWeaponTier() >= 3)
                {
                    setHasPromotion(ePromT3, true);
                    gDLL->getInterfaceIFace()->addMessage(getOwner(), true, GC.defines.iEVENT_MESSAGE_TIME, gDLL->getText("TXT_KEY_MESSAGE_WEAPONS_MITHRIL"), "AS2D_REPAIR", MESSAGE_TYPE_MAJOR_EVENT, GC.getPromotionInfo(ePromT3).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), getX(), getY(), true, true);
                    setHasPromotion(ePromT2, false);
                    setHasPromotion(ePromT1, false);
                }
                else
                {
                    if (isHasPromotion(ePromT2) == false)
                    {
                        if (pCity->hasBonus((BonusTypes)GC.defines.iWEAPON_REQ_BONUS_TIER2) &&
                          m_pUnitInfo->getWeaponTier() >= 2)
                        {
                            setHasPromotion(ePromT2, true);
                            gDLL->getInterfaceIFace()->addMessage(getOwner(), true, GC.defines.iEVENT_MESSAGE_TIME, gDLL->getText("TXT_KEY_MESSAGE_WEAPONS_IRON"), "AS2D_REPAIR", MESSAGE_TYPE_MAJOR_EVENT, GC.getPromotionInfo(ePromT2).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), getX(), getY(), true, true);
                            setHasPromotion(ePromT1, false);
                        }
                        else
                        {
                            if (isHasPromotion(ePromT1) == false)
                            {
                                if (pCity->hasBonus((BonusTypes)GC.defines.iWEAPON_REQ_BONUS_TIER1) &&
                                  m_pUnitInfo->getWeaponTier() >= 1)
                                {
                                    gDLL->getInterfaceIFace()->addMessage(getOwner(), true, GC.defines.iEVENT_MESSAGE_TIME, gDLL->getText("TXT_KEY_MESSAGE_WEAPONS_BRONZE"), "AS2D_REPAIR", MESSAGE_TYPE_MAJOR_EVENT, GC.getPromotionInfo(ePromT1).getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_GREEN"), getX(), getY(), true, true);
                                    setHasPromotion(ePromT1, true);
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

void CvUnit::changeBonusAffinity(BonusTypes eIndex, int iChange)
{
    if (iChange != 0)
    {
        m_paiBonusAffinity[eIndex] += iChange;
    }
    updateBonusAffinity(eIndex);
}

int CvUnit::getBonusAffinity(BonusTypes eIndex) const
{
	return m_paiBonusAffinity[eIndex];
}

void CvUnit::updateBonusAffinity(BonusTypes eIndex)
{
    int iNew = GET_PLAYER(getOwnerINLINE()).getNumAvailableBonuses(eIndex) * getBonusAffinity(eIndex);
    int iOld = m_paiBonusAffinityAmount[eIndex];
    if (GC.getBonusInfo(eIndex).getDamageType() == NO_DAMAGE)
    {
        m_iBaseCombat += iNew - iOld;
        m_iBaseCombatDefense += iNew - iOld;
    }
    else
    {
        m_paiDamageTypeCombat[GC.getBonusInfo(eIndex).getDamageType()] += iNew - iOld;
        m_iTotalDamageTypeCombat += iNew - iOld;
    }
    m_paiBonusAffinityAmount[eIndex] = iNew;
}

void CvUnit::changeDamageTypeCombat(DamageTypes eIndex, int iChange)
{
    if (iChange != 0)
    {
        m_paiDamageTypeCombat[eIndex] = (m_paiDamageTypeCombat[eIndex] + iChange);
        m_iTotalDamageTypeCombat = (m_iTotalDamageTypeCombat + iChange);
    }
}

int CvUnit::getDamageTypeCombat(DamageTypes eIndex) const
{
	return m_paiDamageTypeCombat[eIndex];
}

int CvUnit::getTotalDamageTypeCombat() const
{
    return m_iTotalDamageTypeCombat;
}

int CvUnit::getDamageTypeResist(DamageTypes eIndex) const
{
    int i = m_paiDamageTypeResist[eIndex];
    if (i <= -100)
    {
        return -100;
    }
    if (i >= 100)
    {
        return 100;
    }
	return i;
}

void CvUnit::changeDamageTypeResist(DamageTypes eIndex, int iChange)
{
    if (iChange != 0)
    {
        m_paiDamageTypeResist[eIndex] = (m_paiDamageTypeResist[eIndex] + iChange);
    }
}

int CvUnit::countUnitsWithinRange(int iRange, bool bEnemy, bool bNeutral, bool bTeam)
{
    CLLNode<IDInfo>* pUnitNode;
    CvUnit* pLoopUnit;
    CvPlot* pLoopPlot;
    int iCount = 0;
    for (int i = -iRange; i <= iRange; ++i)
    {
        for (int j = -iRange; j <= iRange; ++j)
        {
            pLoopPlot = ::plotXY(plot()->getX_INLINE(), plot()->getY_INLINE(), i, j);
            if (NULL != pLoopPlot)
            {
                pUnitNode = pLoopPlot->headUnitNode();
                while (pUnitNode != NULL)
                {
                    pLoopUnit = ::getUnit(pUnitNode->m_data);
                    pUnitNode = pLoopPlot->nextUnitNode(pUnitNode);
                    if (bTeam && pLoopUnit->getTeam() == getTeam())
                    {
                        iCount += 1;
                    }
                    if (bEnemy && atWar(pLoopUnit->getTeam(), getTeam()))
                    {
                        iCount += 1;
                    }
                    if (bNeutral && pLoopUnit->getTeam() != getTeam() && !atWar(pLoopUnit->getTeam(), getTeam()))
                    {
                        iCount += 1;
                    }
                }
            }
        }
    }
    return iCount;
}

CvPlot* CvUnit::getOpenPlot() const
{
	CvPlot* pLoopPlot;
	CvPlot* pBestPlot = NULL;
	int iValue;
	int iBestValue = MAX_INT;
	bool bEquipment = false;
	if (m_pUnitInfo->getEquipmentPromotion() != NO_PROMOTION)
	{
	    bEquipment = true;
	}
	for (int iI = 0; iI < GC.getMapINLINE().numPlotsINLINE(); iI++)
	{
		pLoopPlot = GC.getMapINLINE().plotByIndexINLINE(iI);
		if (pLoopPlot->isValidDomainForLocation(*this))
		{
			if (canMoveInto(pLoopPlot) || bEquipment)
			{
				if (pLoopPlot->getNumUnits() == 0)
				{
                    iValue = plotDistance(getX_INLINE(), getY_INLINE(), pLoopPlot->getX_INLINE(), pLoopPlot->getY_INLINE()) * 2;
                    if (pLoopPlot->area() != area())
                    {
                        iValue *= 3;
                    }
                    if (iValue < iBestValue)
                    {
                        iBestValue = iValue;
                        pBestPlot = pLoopPlot;
					}
				}
			}
		}
	}
	return pBestPlot;
}

void CvUnit::betray(PlayerTypes ePlayer)
{
   	if (getOwnerINLINE() == ePlayer)
	{
		return;
	}
    CvPlot* pNewPlot = getOpenPlot();
    if (pNewPlot != NULL)
    {
        CvUnit* pUnit = GET_PLAYER(ePlayer).initUnit((UnitTypes)getUnitType(), pNewPlot->getX(), pNewPlot->getY(), AI_getUnitAIType());
        pUnit->convert(this);
        if (pUnit->getDuration() > 0)
        {
            pUnit->setDuration(0);
        }
    }
}

void CvUnit::updateTerraformer()
{
    m_bTerraformer = false;
    for (int iSpell = 0; iSpell < GC.getNumSpellInfos(); iSpell++)
    {
        if (GC.getSpellInfo((SpellTypes)iSpell).isAllowAutomateTerrain())
        {
            if (canCastWithCurrentPromotions( (SpellTypes) iSpell )) // lfgr fix 03/2021
            {
                m_bTerraformer = true;
                return;
            }
        }
    }
    return;
}

bool CvUnit::isTerraformer() const
{
	return m_bTerraformer;
}

bool CvUnit::withdrawlToNearestValidPlot(bool bKillUnit)
{
	CvPlot* pLoopPlot;
	CvPlot* pBestPlot = NULL;
	int iValue;
	int iBestValue = MAX_INT;
	for (int iI = -1; iI <= 1; ++iI)
	{
		for (int iJ = -1; iJ <= 1; ++iJ)
		{
			pLoopPlot = ::plotXY(getX_INLINE(), getY_INLINE(), iI, iJ);
			if (NULL != pLoopPlot)
			{
                if (pLoopPlot->isValidDomainForLocation(*this))
                {
                    if (canMoveInto(pLoopPlot))
                    {
                        iValue = (plotDistance(getX_INLINE(), getY_INLINE(), pLoopPlot->getX_INLINE(), pLoopPlot->getY_INLINE()) * 2);
                        if (getDomainType() == DOMAIN_SEA && !plot()->isWater())
                        {
                            if (!pLoopPlot->isWater() || !pLoopPlot->isAdjacentToArea(area()))
                            {
                                iValue *= 3;
                            }
                        }
                        else
                        {
                            if (pLoopPlot->area() != area())
                            {
                                iValue *= 3;
                            }
                        }
                        if (iValue < iBestValue)
                        {
                            iBestValue = iValue;
                            pBestPlot = pLoopPlot;
                        }
					}
				}
			}
		}
	}
	bool bValid = true;
	if (pBestPlot != NULL)
	{
//>>>>Unofficial Bug Fix: Modified by Denev 2010/02/22
//*** show moving animation
//		setXY(pBestPlot->getX_INLINE(), pBestPlot->getY_INLINE());
		setXY(pBestPlot->getX_INLINE(), pBestPlot->getY_INLINE(), false, true, false, true);
//<<<<Unofficial Bug Fix: End Modify
	}
	else
	{
		// Bugfix: Defenders that flee can be killed after combat
		// lfgr 10/2019: Kill delayed, as withdrawlToNearestValidPlot() might be called in all sorts of situations
		if (bKillUnit) {
			if( !isDelayedDeath() ) {
				// Show message
				gDLL->getInterfaceIFace()->addMessage(getOwnerINLINE(), true, GC.getEVENT_MESSAGE_TIME(),
						gDLL->getText( "TXT_KEY_MESSAGE_UNIT_KILLED_CANNOT_WITHDRAW", getNameKey() ),
						GC.getEraInfo(GC.getGameINLINE().getCurrentEra()).getAudioUnitDefeatScript(),
						MESSAGE_TYPE_INFO, m_pUnitInfo->getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_RED"),
						getX_INLINE(), getY_INLINE(), false, false);
				
				logBBAI("    Killing %S (delayed) -- cannot withdraw to nearest valid plot (Unit %d - plot: %d, %d)",
						getName().GetCString(), getID(), getX(), getY());
				kill(true);
			}
		}
		// Bugfix end
		bValid = false;
	}
	return bValid;
}
//FfH: End Add

// MNAI - additional promotion tags
void CvUnit::changeCanMoveImpassable(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iCanMoveImpassable += iNewValue;
    }
}

void CvUnit::changeCanMoveLimitedBorders(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iCanMoveLimitedBorders += iNewValue;
    }
}

bool CvUnit::isCastingBlocked() const
{
	return m_iCastingBlocked == 0 ? false : true;
}

void CvUnit::changeCastingBlocked(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iCastingBlocked += iNewValue;
    }
}

bool CvUnit::isUpgradeBlocked() const
{
	return m_iUpgradeBlocked == 0 ? false : true;
}

void CvUnit::changeUpgradeBlocked(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iUpgradeBlocked += iNewValue;
    }
}

bool CvUnit::isGiftingBlocked() const
{
	return m_iGiftingBlocked == 0 ? false : true;
}

void CvUnit::changeGiftingBlocked(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iGiftingBlocked += iNewValue;
    }
}

bool CvUnit::isUpgradeOutsideBorders() const
{
	return m_iUpgradeOutsideBorders == 0 ? false : true;
}

void CvUnit::changeUpgradeOutsideBorders(int iNewValue)
{
    if (iNewValue != 0)
    {
        m_iUpgradeOutsideBorders += iNewValue;
    }
}
// End MNAI

// XML_LISTS 07/2019 lfgr: cache CvPromotionInfo::isPromotionImmune
bool CvUnit::isPromotionImmune( PromotionTypes ePromotion ) const
{
    FAssertMsg(ePromotion >= 0, "Index out of bounds");
    FAssertMsg(ePromotion < GC.getNumPromotionInfos(), "Index out of bounds");
	return m_paiPromotionImmune[ePromotion] > 0;
}

void CvUnit::changePromotionImmune( PromotionTypes ePromotion, int iChange )
{
    FAssertMsg(ePromotion >= 0, "Index out of bounds");
    FAssertMsg(ePromotion < GC.getNumPromotionInfos(), "Index out of bounds");
	m_paiPromotionImmune[ePromotion] += iChange;
}
// XML_LISTS end

// MiscastPromotions 10/2019 lfgr
int CvUnit::getMiscastChance() const {
	int iMiscastChance = GC.getUnitInfo( getUnitType() ).getMiscastChance();

	// LFGR_TODO: Make more efficient for next savegame-breaking release
	for( int ePromotion = 0; ePromotion < GC.getNumPromotionInfos(); ePromotion++ ) {
		if( isHasPromotion( (PromotionTypes) ePromotion ) ) {
			iMiscastChance += GC.getPromotionInfo( (PromotionTypes) ePromotion ).getMiscastChance();
		}
	}

	return std::max( 0, iMiscastChance );
}

// lfgr 09/2023 Extra revolution tags
int CvUnit::getRevGarrisonValue() const
{
	int iGarrisonValue = 1;

	// LFGR_TODO: Make more efficient for next savegame-breaking release
	for( int ePromotion = 0; ePromotion < GC.getNumPromotionInfos(); ePromotion++ ) {
		if( isHasPromotion( (PromotionTypes) ePromotion ) ) {
			iGarrisonValue += GC.getPromotionInfo( (PromotionTypes) ePromotion ).getRevGarrisonValue();
		}
	}

	return iGarrisonValue;
}

// lfgr 01/2022: Refactoring
bool CvUnit::isNoUpkeep() const
{
	return getDuration() > 0 || getUnitInfo().isNoUpkeep();
}

void CvUnit::read(FDataStreamBase* pStream)
{
	// Init data before load
	reset();

	uint uiFlag=0;
	pStream->Read(&uiFlag);	// flags for expansion

	pStream->Read(&m_iID);
	pStream->Read(&m_iGroupID);
	pStream->Read(&m_iHotKeyNumber);
	pStream->Read(&m_iX);
	pStream->Read(&m_iY);
	pStream->Read(&m_iLastMoveTurn);
	pStream->Read(&m_iReconX);
	pStream->Read(&m_iReconY);
	pStream->Read(&m_iGameTurnCreated);
	pStream->Read(&m_iDamage);
	pStream->Read(&m_iMoves);
	pStream->Read(&m_iExperience);
	pStream->Read(&m_iLevel);
	pStream->Read(&m_iCargo);
	pStream->Read(&m_iCargoCapacity);
	pStream->Read(&m_iAttackPlotX);
	pStream->Read(&m_iAttackPlotY);
	pStream->Read(&m_iCombatTimer);
	pStream->Read(&m_iCombatFirstStrikes);
	if (uiFlag < 2)
	{
		int iCombatDamage;
		pStream->Read(&iCombatDamage);
	}
	pStream->Read(&m_iFortifyTurns);
	pStream->Read(&m_iBlitzCount);
	pStream->Read(&m_iAmphibCount);
	pStream->Read(&m_iRiverCount);
	pStream->Read(&m_iEnemyRouteCount);
	pStream->Read(&m_iAlwaysHealCount);
	pStream->Read(&m_iHillsDoubleMoveCount);
	pStream->Read(&m_iImmuneToFirstStrikesCount);
	pStream->Read(&m_iExtraVisibilityRange);
	pStream->Read(&m_iExtraMoves);
	pStream->Read(&m_iExtraMoveDiscount);
	pStream->Read(&m_iExtraAirRange);
	pStream->Read(&m_iExtraIntercept);
	pStream->Read(&m_iExtraEvasion);
	pStream->Read(&m_iExtraFirstStrikes);
	pStream->Read(&m_iExtraChanceFirstStrikes);
	pStream->Read(&m_iExtraWithdrawal);
	pStream->Read(&m_iExtraCollateralDamage);
	pStream->Read(&m_iExtraBombardRate);
	pStream->Read(&m_iExtraEnemyHeal);
	pStream->Read(&m_iExtraNeutralHeal);
	pStream->Read(&m_iExtraFriendlyHeal);
	pStream->Read(&m_iSameTileHeal);
	pStream->Read(&m_iAdjacentTileHeal);
	pStream->Read(&m_iExtraCombatPercent);
	pStream->Read(&m_iExtraCityAttackPercent);
	pStream->Read(&m_iExtraCityDefensePercent);
	pStream->Read(&m_iExtraHillsAttackPercent);
	pStream->Read(&m_iExtraHillsDefensePercent);
	pStream->Read(&m_iRevoltProtection);
	pStream->Read(&m_iCollateralDamageProtection);
	pStream->Read(&m_iPillageChange);
	pStream->Read(&m_iUpgradeDiscount);
	pStream->Read(&m_iExperiencePercent);
	pStream->Read(&m_iKamikazePercent);
	pStream->Read(&m_iBaseCombat);
	pStream->Read((int*)&m_eFacingDirection);
	pStream->Read(&m_iImmobileTimer);
/************************************************************************************************/
/* Afforess	                  Start		 07/29/10                                               */
/* Advanced Diplomacy                                                                           */
/************************************************************************************************/
	pStream->Read((int*)&m_eOriginalOwner);
/************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/************************************************************************************************/
	pStream->Read(&m_bMadeAttack);
	pStream->Read(&m_bMadeInterception);
	pStream->Read(&m_bPromotionReady);
	pStream->Read(&m_bDeathDelay);
	pStream->Read(&m_bCombatFocus);
	// m_bInfoBarDirty not saved...
	pStream->Read(&m_bBlockading);
	if (uiFlag > 0)
	{
		pStream->Read(&m_bAirCombat);
	}

//FfH Spell System: Added by Kael 07/23/2007
	pStream->Read(&m_bFleeWithdrawl);
	pStream->Read(&m_bHasCasted);
	pStream->Read(&m_bIgnoreHide);
	pStream->Read(&m_bTerraformer);
	pStream->Read(&m_iAlive);
	pStream->Read(&m_iAIControl);
	pStream->Read(&m_iBoarding);
	pStream->Read(&m_iDefensiveStrikeChance);
	pStream->Read(&m_iDefensiveStrikeDamage);
	pStream->Read(&m_iDoubleFortifyBonus);
	pStream->Read(&m_iFear);
	pStream->Read(&m_iFlying);
	pStream->Read(&m_iHeld);
	pStream->Read(&m_iHiddenNationality);
	pStream->Read(&m_iIgnoreBuildingDefense);
	pStream->Read(&m_iImmortal);
	pStream->Read(&m_iImmuneToCapture);
	pStream->Read(&m_iImmuneToDefensiveStrike);
	pStream->Read(&m_iImmuneToFear);
	pStream->Read(&m_iImmuneToMagic);
	pStream->Read(&m_iInvisible);
	pStream->Read(&m_iSeeInvisible);
	pStream->Read(&m_iOnlyDefensive);
	pStream->Read(&m_iTargetWeakestUnit);
	pStream->Read(&m_iTargetWeakestUnitCounter);
	pStream->Read(&m_iTwincast);
	pStream->Read(&m_iWaterWalking);
	pStream->Read(&m_iBaseCombatDefense);
	pStream->Read(&m_iBetterDefenderThanPercent);
	pStream->Read(&m_iCombatHealPercent);
	pStream->Read(&m_iCombatLimit);
	pStream->Read(&m_iCombatPercentInBorders);
	pStream->Read(&m_iCombatPercentGlobalCounter);
	pStream->Read(&m_iDelayedSpell);
	pStream->Read(&m_iDuration);
	pStream->Read(&m_iFreePromotionPick);
	pStream->Read(&m_iGoldFromCombat);
	pStream->Read(&m_iGroupSize);
	pStream->Read(&m_iInvisibleType);
	pStream->Read(&m_iRace);
	pStream->Read(&m_iReligion);
	pStream->Read(&m_iResist);
	pStream->Read(&m_iResistModify);
	pStream->Read(&m_iScenarioCounter);
	pStream->Read(&m_iSpellCasterXP);
	pStream->Read(&m_iSpellDamageModify);
	pStream->Read(&m_iSummoner);
	pStream->Read(&m_iTotalDamageTypeCombat);
	pStream->Read(&m_iUnitArtStyleType);
	pStream->Read(&m_iWorkRateModify);
	pStream->Read(GC.getNumBonusInfos(), m_paiBonusAffinity);
	pStream->Read(GC.getNumBonusInfos(), m_paiBonusAffinityAmount);
	pStream->Read(GC.getNumDamageTypeInfos(), m_paiDamageTypeCombat);
	pStream->Read(GC.getNumDamageTypeInfos(), m_paiDamageTypeResist);
//FfH: End Add

	// MNAI - additional promotion tags
	pStream->Read(&m_iCanMoveImpassable);
	pStream->Read(&m_iCanMoveLimitedBorders);
	pStream->Read(&m_iCastingBlocked);
	pStream->Read(&m_iUpgradeBlocked);
	pStream->Read(&m_iGiftingBlocked);
	pStream->Read(&m_iUpgradeOutsideBorders);
	// End MNAI

	//>>>>Unofficial Bug Fix: Added by Denev 2010/02/22
	pStream->Read(&m_bAvatarOfCivLeader);
	//<<<<Unofficial Bug Fix: End Add

	pStream->Read((int*)&m_eOwner);
	pStream->Read((int*)&m_eCapturingPlayer);
	pStream->Read((int*)&m_eUnitType);
	FAssert(NO_UNIT != m_eUnitType);
	m_pUnitInfo = (NO_UNIT != m_eUnitType) ? &GC.getUnitInfo(m_eUnitType) : NULL;
	pStream->Read((int*)&m_eLeaderUnitType);

	pStream->Read((int*)&m_combatUnit.eOwner);
	pStream->Read(&m_combatUnit.iID);
	pStream->Read((int*)&m_transportUnit.eOwner);
	pStream->Read(&m_transportUnit.iID);

	pStream->Read(NUM_DOMAIN_TYPES, m_aiExtraDomainModifier);

	pStream->ReadString(m_szName);
	pStream->ReadString(m_szScriptData);

	pStream->Read(GC.getNumPromotionInfos(), m_pabHasPromotion);

	pStream->Read(GC.getNumTerrainInfos(), m_paiTerrainDoubleMoveCount);
	pStream->Read(GC.getNumFeatureInfos(), m_paiFeatureDoubleMoveCount);
	pStream->Read(GC.getNumTerrainInfos(), m_paiExtraTerrainAttackPercent);
	pStream->Read(GC.getNumTerrainInfos(), m_paiExtraTerrainDefensePercent);
	pStream->Read(GC.getNumFeatureInfos(), m_paiExtraFeatureAttackPercent);
	pStream->Read(GC.getNumFeatureInfos(), m_paiExtraFeatureDefensePercent);
	pStream->Read(GC.getNumUnitCombatInfos(), m_paiExtraUnitCombatModifier);
	
	pStream->Read(GC.getNumPromotionInfos(), m_paiPromotionImmune); // XML_LISTS 07/2019 lfgr: cache CvPromotionInfo::isPromotionImmune
}


void CvUnit::write(FDataStreamBase* pStream)
{
	uint uiFlag=2;
	pStream->Write(uiFlag);		// flag for expansion

	pStream->Write(m_iID);
	pStream->Write(m_iGroupID);
	pStream->Write(m_iHotKeyNumber);
	pStream->Write(m_iX);
	pStream->Write(m_iY);
	pStream->Write(m_iLastMoveTurn);
	pStream->Write(m_iReconX);
	pStream->Write(m_iReconY);
	pStream->Write(m_iGameTurnCreated);
	pStream->Write(m_iDamage);
	pStream->Write(m_iMoves);
	pStream->Write(m_iExperience);
	pStream->Write(m_iLevel);
	pStream->Write(m_iCargo);
	pStream->Write(m_iCargoCapacity);
	pStream->Write(m_iAttackPlotX);
	pStream->Write(m_iAttackPlotY);
	pStream->Write(m_iCombatTimer);
	pStream->Write(m_iCombatFirstStrikes);
	pStream->Write(m_iFortifyTurns);
	pStream->Write(m_iBlitzCount);
	pStream->Write(m_iAmphibCount);
	pStream->Write(m_iRiverCount);
	pStream->Write(m_iEnemyRouteCount);
	pStream->Write(m_iAlwaysHealCount);
	pStream->Write(m_iHillsDoubleMoveCount);
	pStream->Write(m_iImmuneToFirstStrikesCount);
	pStream->Write(m_iExtraVisibilityRange);
	pStream->Write(m_iExtraMoves);
	pStream->Write(m_iExtraMoveDiscount);
	pStream->Write(m_iExtraAirRange);
	pStream->Write(m_iExtraIntercept);
	pStream->Write(m_iExtraEvasion);
	pStream->Write(m_iExtraFirstStrikes);
	pStream->Write(m_iExtraChanceFirstStrikes);
	pStream->Write(m_iExtraWithdrawal);
	pStream->Write(m_iExtraCollateralDamage);
	pStream->Write(m_iExtraBombardRate);
	pStream->Write(m_iExtraEnemyHeal);
	pStream->Write(m_iExtraNeutralHeal);
	pStream->Write(m_iExtraFriendlyHeal);
	pStream->Write(m_iSameTileHeal);
	pStream->Write(m_iAdjacentTileHeal);
	pStream->Write(m_iExtraCombatPercent);
	pStream->Write(m_iExtraCityAttackPercent);
	pStream->Write(m_iExtraCityDefensePercent);
	pStream->Write(m_iExtraHillsAttackPercent);
	pStream->Write(m_iExtraHillsDefensePercent);
	pStream->Write(m_iRevoltProtection);
	pStream->Write(m_iCollateralDamageProtection);
	pStream->Write(m_iPillageChange);
	pStream->Write(m_iUpgradeDiscount);
	pStream->Write(m_iExperiencePercent);
	pStream->Write(m_iKamikazePercent);
	pStream->Write(m_iBaseCombat);
	pStream->Write(m_eFacingDirection);
	pStream->Write(m_iImmobileTimer);
/************************************************************************************************/
/* Afforess	                  Start		 07/29/10                                               */
/* Advanced Diplomacy                                                                           */
/************************************************************************************************/
	pStream->Write(m_eOriginalOwner);
/************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/************************************************************************************************/
	pStream->Write(m_bMadeAttack);
	pStream->Write(m_bMadeInterception);
	pStream->Write(m_bPromotionReady);
	pStream->Write(m_bDeathDelay);
	pStream->Write(m_bCombatFocus);
	// m_bInfoBarDirty not saved...
	pStream->Write(m_bBlockading);
	pStream->Write(m_bAirCombat);

//FfH Spell System: Added by Kael 07/23/2007
	pStream->Write(m_bFleeWithdrawl);
	pStream->Write(m_bHasCasted);
	pStream->Write(m_bIgnoreHide);
	pStream->Write(m_bTerraformer);
	pStream->Write(m_iAlive);
	pStream->Write(m_iAIControl);
	pStream->Write(m_iBoarding);
	pStream->Write(m_iDefensiveStrikeChance);
	pStream->Write(m_iDefensiveStrikeDamage);
	pStream->Write(m_iDoubleFortifyBonus);
	pStream->Write(m_iFear);
	pStream->Write(m_iFlying);
	pStream->Write(m_iHeld);
	pStream->Write(m_iHiddenNationality);
	pStream->Write(m_iIgnoreBuildingDefense);
	pStream->Write(m_iImmortal);
	pStream->Write(m_iImmuneToCapture);
	pStream->Write(m_iImmuneToDefensiveStrike);
	pStream->Write(m_iImmuneToFear);
	pStream->Write(m_iImmuneToMagic);
	pStream->Write(m_iInvisible);
	pStream->Write(m_iSeeInvisible);
	pStream->Write(m_iOnlyDefensive);
	pStream->Write(m_iTargetWeakestUnit);
	pStream->Write(m_iTargetWeakestUnitCounter);
	pStream->Write(m_iTwincast);
	pStream->Write(m_iWaterWalking);
	pStream->Write(m_iBaseCombatDefense);
	pStream->Write(m_iBetterDefenderThanPercent);
	pStream->Write(m_iCombatHealPercent);
	pStream->Write(m_iCombatLimit);
	pStream->Write(m_iCombatPercentInBorders);
	pStream->Write(m_iCombatPercentGlobalCounter);
	pStream->Write(m_iDelayedSpell);
	pStream->Write(m_iDuration);
	pStream->Write(m_iFreePromotionPick);
	pStream->Write(m_iGoldFromCombat);
	pStream->Write(m_iGroupSize);
	pStream->Write(m_iInvisibleType);
	pStream->Write(m_iRace);
	pStream->Write(m_iReligion);
	pStream->Write(m_iResist);
	pStream->Write(m_iResistModify);
	pStream->Write(m_iScenarioCounter);
	pStream->Write(m_iSpellCasterXP);
	pStream->Write(m_iSpellDamageModify);
	pStream->Write(m_iSummoner);
	pStream->Write(m_iTotalDamageTypeCombat);
	pStream->Write(m_iUnitArtStyleType);
	pStream->Write(m_iWorkRateModify);
	pStream->Write(GC.getNumBonusInfos(), m_paiBonusAffinity);
	pStream->Write(GC.getNumBonusInfos(), m_paiBonusAffinityAmount);
	pStream->Write(GC.getNumDamageTypeInfos(), m_paiDamageTypeCombat);
	pStream->Write(GC.getNumDamageTypeInfos(), m_paiDamageTypeResist);
//FfH: End Add

	// MNAI - additional promotion tags
	pStream->Write(m_iCanMoveImpassable);
	pStream->Write(m_iCanMoveLimitedBorders);
	pStream->Write(m_iCastingBlocked);
	pStream->Write(m_iUpgradeBlocked);
	pStream->Write(m_iGiftingBlocked);
	pStream->Write(m_iUpgradeOutsideBorders);
	// End MNAI

	//>>>>Unofficial Bug Fix: Added by Denev 2010/02/22
	pStream->Write(m_bAvatarOfCivLeader);
	//<<<<Unofficial Bug Fix: End Add

	pStream->Write(m_eOwner);
	pStream->Write(m_eCapturingPlayer);
	pStream->Write(m_eUnitType);
	pStream->Write(m_eLeaderUnitType);

	pStream->Write(m_combatUnit.eOwner);
	pStream->Write(m_combatUnit.iID);
	pStream->Write(m_transportUnit.eOwner);
	pStream->Write(m_transportUnit.iID);

	pStream->Write(NUM_DOMAIN_TYPES, m_aiExtraDomainModifier);

	pStream->WriteString(m_szName);
	pStream->WriteString(m_szScriptData);

	pStream->Write(GC.getNumPromotionInfos(), m_pabHasPromotion);

	pStream->Write(GC.getNumTerrainInfos(), m_paiTerrainDoubleMoveCount);
	pStream->Write(GC.getNumFeatureInfos(), m_paiFeatureDoubleMoveCount);
	pStream->Write(GC.getNumTerrainInfos(), m_paiExtraTerrainAttackPercent);
	pStream->Write(GC.getNumTerrainInfos(), m_paiExtraTerrainDefensePercent);
	pStream->Write(GC.getNumFeatureInfos(), m_paiExtraFeatureAttackPercent);
	pStream->Write(GC.getNumFeatureInfos(), m_paiExtraFeatureDefensePercent);
	pStream->Write(GC.getNumUnitCombatInfos(), m_paiExtraUnitCombatModifier);

	pStream->Write(GC.getNumPromotionInfos(), m_paiPromotionImmune); // XML_LISTS 07/2019 lfgr: cache CvPromotionInfo::isPromotionImmune
}

// Protected Functions...

bool CvUnit::canAdvance(const CvPlot* pPlot, int iThreshold) const
{
	FAssert(canFight());
//	FAssert(!(isAnimal() && pPlot->isCity())); //modified animals Sephi
	FAssert(getDomainType() != DOMAIN_AIR);
	FAssert(getDomainType() != DOMAIN_IMMOBILE);

	if (pPlot->getNumVisibleEnemyDefenders(this) > iThreshold)
	{
		return false;
	}

	if (isNoCapture())
	{
		if (pPlot->isEnemyCity(*this))
		{
			return false;
		}
	}

	return true;
}

//Unlike CvUnit::canJoinGroup this Function doesn't check for atPlot(), so we can use it to plan AI moves ahead of time
bool CvUnit::AI_canJoinGroup(CvSelectionGroup* pSelectionGroup) const
{
	CvUnit* pHeadUnit;

	if (pSelectionGroup->getOwnerINLINE() == NO_PLAYER)
	{
		pHeadUnit = pSelectionGroup->getHeadUnit();

		if (pHeadUnit != NULL)
		{
			if (pHeadUnit->getOwnerINLINE() != getOwnerINLINE())
			{
				return false;
			}
		}
	}
	else
	{
		if (pSelectionGroup->getOwnerINLINE() != getOwnerINLINE())
		{
			return false;
		}
	}

	if (pSelectionGroup->getNumUnits() > 0)
	{
		if (pSelectionGroup->getDomainType() != getDomainType())
		{
			return false;
		}

        pHeadUnit = pSelectionGroup->getHeadUnit();
        if (pHeadUnit != NULL)
	    {
			if (pHeadUnit->isHiddenNationality() != isHiddenNationality())
			{
                return false;
			}
            if (pHeadUnit->isAIControl() != isAIControl())
			{
                return false;
			}
		}
	}

	return true;
}
bool CvUnit::isAvatarOfCivLeader() const
{
	return m_bAvatarOfCivLeader;
}

void CvUnit::setAvatarOfCivLeader(bool bNewValue)
{
	m_bAvatarOfCivLeader = bNewValue;
}
//<<<<Unofficial Bug Fix: End Add

 // MNAI - True Power calculations
int CvUnit::getTruePower() const
{
	//Tholal note: units start at level 1
	return (m_pUnitInfo->getPowerValue() + (getLevel() - 1));
}

 // MNAI - Identify Units with Ranged Collateral Damage ability
bool CvUnit::isRangedCollateral()
{
    for (int iSpell = 0; iSpell < GC.getNumSpellInfos(); iSpell++)
    {
        if (canCast(iSpell, false))
        {
			CvSpellInfo kSpell = GC.getSpellInfo((SpellTypes)iSpell);
			{
				if (kSpell.getDamage() > 0 && kSpell.getRange() > 0)
				{
					return true;
				}

				if (kSpell.getCreateUnitType() != NO_UNIT)
				{
					if (GC.getUnitInfo((UnitTypes)kSpell.getCreateUnitType()).getCollateralDamage() > 0)
					{
						return true;
					}
				}
			}
		}
	}
	return false;
}
// MNAI End

/************************************************************************************************/
/* Afforess	                  Start		 07/29/10                                               */
/*                                                                                              */
/* Advanced Diplomacy                                                                           */
/************************************************************************************************/
bool CvUnit::canTradeUnit(PlayerTypes eReceivingPlayer)
{
	CvArea* pWaterArea = NULL;
	CvCity* pCapitalCity;
	int iLoop;
	bool bShip = false;
	bool bCoast = false;

	pCapitalCity = GET_PLAYER(eReceivingPlayer).getCapitalCity();

	if (eReceivingPlayer == NO_PLAYER || eReceivingPlayer > MAX_PLAYERS)
	{
		return false;
	}

	if (!(m_pUnitInfo->isMilitaryTrade() || m_pUnitInfo->isWorkerTrade()))
	{
		return false;
	}
	
	if (m_pUnitInfo->isAbandon())
	{
		return false;
	}

	if (getDuration() > 0 || isPermanentSummon())
	{
		return false;
	}
	
	if (isWorldUnitClass((UnitClassTypes)(m_pUnitInfo->getUnitClassType())))
	{
		return false;
	}
	
	if (getCargo() > 0)
	{
		return false;
	}
	
	if (getDomainType() == DOMAIN_SEA)
	{
		bShip = true;
		for (CvCity* pLoopCity = GET_PLAYER(eReceivingPlayer).firstCity(&iLoop); pLoopCity != NULL; pLoopCity = GET_PLAYER(eReceivingPlayer).nextCity(&iLoop))
		{
			if (((pWaterArea = pLoopCity->waterArea()) != NULL && !pWaterArea->isLake()))
			{
				bCoast = true;
			}
		}
	}
	
	if (bShip && !bCoast)
	{
		return false;
	}

	return true;
}
	
void CvUnit::tradeUnit(PlayerTypes eReceivingPlayer)
{
	CvUnit* pTradeUnit;
	CvWString szBuffer;
	CvCity* pBestCity;
	//CvArea* pWaterArea = NULL;
	PlayerTypes eOwner;
	int iLoop;
	
	eOwner = getOwnerINLINE();
	
	if (eReceivingPlayer != NO_PLAYER)
	{
		pBestCity = GET_PLAYER(eReceivingPlayer).getCapitalCity();
		
		if (getDomainType() == DOMAIN_SEA)
		//Find the first coastal city, and put the ship there
		{
			for (CvCity* pLoopCity = GET_PLAYER(eReceivingPlayer).firstCity(&iLoop); pLoopCity != NULL; pLoopCity = GET_PLAYER(eReceivingPlayer).nextCity(&iLoop))
			{
				if (pLoopCity->isCoastal(GC.getMIN_WATER_SIZE_FOR_OCEAN()))
				{
					pBestCity = pLoopCity;
					break;
				}
			}
		}
		
		pTradeUnit = GET_PLAYER(eReceivingPlayer).initUnit(getUnitType(), pBestCity->getX_INLINE(), pBestCity->getY_INLINE(), AI_getUnitAIType());

		pTradeUnit->convert(this);

		pTradeUnit->setImmobileTimer(10); //ToDo - better way to decide how long the unit should be immobile; scale by gamespeed
		
		szBuffer = gDLL->getText("TXT_KEY_MISC_TRADED_UNIT_TO_YOU", GET_PLAYER(eOwner).getNameKey(), pTradeUnit->getNameKey());
		gDLL->getInterfaceIFace()->addMessage(pTradeUnit->getOwnerINLINE(), false, GC.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_UNITGIFTED", MESSAGE_TYPE_INFO, pTradeUnit->getButton(), (ColorTypes)GC.getInfoTypeForString("COLOR_WHITE"), pTradeUnit->getX_INLINE(), pTradeUnit->getY_INLINE(), true, true); 
	 }
}

PlayerTypes CvUnit::getOriginalOwner() const
{
	return m_eOriginalOwner;
}

/************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/************************************************************************************************/
