//---------------------------------------------------------------------------------------
//
//  *****************   Civilization IV   ********************
//
//  FILE:    CvGameTextMgr.cpp
//
//  PURPOSE: Interfaces with GameText XML Files to manage the paths of art files
//
//---------------------------------------------------------------------------------------
//  Copyright (c) 2004 Firaxis Games, Inc. All rights reserved.
//---------------------------------------------------------------------------------------

#include "CvGameCoreDLL.h"
#include "CvGameTextMgr.h"
#include "CvGameCoreUtils.h"
#include "CvDLLUtilityIFaceBase.h"
#include "CvDLLInterfaceIFaceBase.h"
#include "CvDLLSymbolIFaceBase.h"
#include "CvInfos.h"
#include "CvXMLLoadUtility.h"
#include "CvCity.h"
#include "CvPlayerAI.h"
#include "CvTeamAI.h"
#include "CvGameAI.h"
#include "CvSelectionGroup.h"
#include "CvMap.h"
#include "CvArea.h"
#include "CvPlot.h"
#include "CvPopupInfo.h"
#include "FProfiler.h"
#include "CyArgsList.h"
#include "CvDLLPythonIFaceBase.h"

#include "CvInfoUtils.h" // lfgr 04/2020

// BUG - start
#include "CvBugOptions.h"
// BUG - end

// lfgr UI 11/2020: Allow cycling through units in plot help
#include "PlotHelpCycling.h"


int shortenID(int iId)
{
	return iId;
}

// For displaying Asserts and error messages
static char* szErrorMsg;

//----------------------------------------------------------------------------
//
//	FUNCTION:	GetInstance()
//
//	PURPOSE:	Get the instance of this class.
//
//----------------------------------------------------------------------------
CvGameTextMgr& CvGameTextMgr::GetInstance()
{
	static CvGameTextMgr gs_GameTextMgr;
	return gs_GameTextMgr;
}

//----------------------------------------------------------------------------
//
//	FUNCTION:	CvGameTextMgr()
//
//	PURPOSE:	Constructor
//
//----------------------------------------------------------------------------
CvGameTextMgr::CvGameTextMgr()
{

}

CvGameTextMgr::~CvGameTextMgr()
{
}

//----------------------------------------------------------------------------
//
//	FUNCTION:	Initialize()
//
//	PURPOSE:	Allocates memory
//
//----------------------------------------------------------------------------
void CvGameTextMgr::Initialize()
{

}

//----------------------------------------------------------------------------
//
//	FUNCTION:	DeInitialize()
//
//	PURPOSE:	Clears memory
//
//----------------------------------------------------------------------------
void CvGameTextMgr::DeInitialize()
{
	for(int i=0;i<(int)m_apbPromotion.size();i++)
	{
		delete [] m_apbPromotion[i];
	}
}

//----------------------------------------------------------------------------
//
//	FUNCTION:	Reset()
//
//	PURPOSE:	Accesses CvXMLLoadUtility to clean global text memory and
//				reload the XML files
//
//----------------------------------------------------------------------------
void CvGameTextMgr::Reset()
{
	CvXMLLoadUtility pXML;
	pXML.LoadGlobalText();
}


// Returns the current language
int CvGameTextMgr::getCurrentLanguage()
{
	return gDLL->getCurrentLanguage();
}

void CvGameTextMgr::setYearStr(CvWString& szString, int iGameTurn, bool bSave, CalendarTypes eCalendar, int iStartYear, GameSpeedTypes eSpeed)
{
	int iTurnYear = getTurnYearForGame(iGameTurn, iStartYear, eCalendar, eSpeed);

	if (bSave)
	{
		szString = gDLL->getText("TXT_KEY_TIME_TURN_SAVE", CvWString::format(L"%04d", iTurnYear).GetCString());
	}
	else
	{
		szString = gDLL->getText("TXT_KEY_TIME_TURN_STANDALONE", iTurnYear);
	}
}


void CvGameTextMgr::setDateStr(CvWString& szString, int iGameTurn, bool bSave, CalendarTypes eCalendar, int iStartYear, GameSpeedTypes eSpeed)
{
	CvWString szYearBuffer;
	CvWString szWeekBuffer;

	setYearStr(szYearBuffer, iGameTurn, bSave, eCalendar, iStartYear, eSpeed);

	switch (eCalendar)
	{
	case CALENDAR_DEFAULT:
		if (0 == (getTurnMonthForGame(iGameTurn + 1, iStartYear, eCalendar, eSpeed) - getTurnMonthForGame(iGameTurn, iStartYear, eCalendar, eSpeed)) % GC.getNumMonthInfos())
		{
			szString = szYearBuffer;
		}
		else
		{
			int iMonth = getTurnMonthForGame(iGameTurn, iStartYear, eCalendar, eSpeed);
			if (bSave)
			{
				szString = (szYearBuffer + "-" + GC.getMonthInfo((MonthTypes)(iMonth % GC.getNumMonthInfos())).getDescription());
			}
			else
			{
				szString = (GC.getMonthInfo((MonthTypes)(iMonth % GC.getNumMonthInfos())).getDescription() + CvString(", ") + szYearBuffer);
			}
		}
		break;
	case CALENDAR_YEARS:
	case CALENDAR_BI_YEARLY:
		szString = szYearBuffer;
		break;

	case CALENDAR_TURNS:
		szString = gDLL->getText("TXT_KEY_TIME_TURN", (iGameTurn + 1));
		break;

	case CALENDAR_SEASONS:
		if (bSave)
		{
			szString = (szYearBuffer + "-" + GC.getSeasonInfo((SeasonTypes)(iGameTurn % GC.getNumSeasonInfos())).getDescription());
		}
		else
		{
			szString = (GC.getSeasonInfo((SeasonTypes)(iGameTurn % GC.getNumSeasonInfos())).getDescription() + CvString(", ") + szYearBuffer);
		}
		break;

	case CALENDAR_MONTHS:
		if (bSave)
		{
			szString = (szYearBuffer + "-" + GC.getMonthInfo((MonthTypes)(iGameTurn % GC.getNumMonthInfos())).getDescription());
		}
		else
		{
			szString = (GC.getMonthInfo((MonthTypes)(iGameTurn % GC.getNumMonthInfos())).getDescription() + CvString(", ") + szYearBuffer);
		}
		break;

	case CALENDAR_WEEKS:
		szWeekBuffer = gDLL->getText("TXT_KEY_TIME_WEEK", ((iGameTurn % GC.getDefineINT("WEEKS_PER_MONTHS")) + 1));

		if (bSave)
		{
			szString = (szYearBuffer + "-" + GC.getMonthInfo((MonthTypes)((iGameTurn / GC.getDefineINT("WEEKS_PER_MONTHS")) % GC.getNumMonthInfos())).getDescription() + "-" + szWeekBuffer);
		}
		else
		{
			szString = (szWeekBuffer + ", " + GC.getMonthInfo((MonthTypes)((iGameTurn / GC.getDefineINT("WEEKS_PER_MONTHS")) % GC.getNumMonthInfos())).getDescription() + ", " + szYearBuffer);
		}
		break;

	default:
		FAssert(false);
	}
}


void CvGameTextMgr::setTimeStr(CvWString& szString, int iGameTurn, bool bSave)
{
	setDateStr(szString, iGameTurn, bSave, GC.getGameINLINE().getCalendar(), GC.getGameINLINE().getStartYear(), GC.getGameINLINE().getGameSpeedType());
}


void CvGameTextMgr::setInterfaceTime(CvWString& szString, PlayerTypes ePlayer)
{
	CvWString szTempBuffer;

	if (GET_PLAYER(ePlayer).isGoldenAge())
	{
		szString.Format(L"%c(%d) ", gDLL->getSymbolID(GOLDEN_AGE_CHAR), GET_PLAYER(ePlayer).getGoldenAgeTurns());
	}
	else
	{
		szString.clear();
	}

	setTimeStr(szTempBuffer, GC.getGameINLINE().getGameTurn(), false);
	szString += CvWString(szTempBuffer);
}


void CvGameTextMgr::setGoldStr(CvWString& szString, PlayerTypes ePlayer)
{
	if (GET_PLAYER(ePlayer).getGold() < 0)
	{
		szString.Format(L"%c: " SETCOLR L"%d" SETCOLR, GC.getCommerceInfo(COMMERCE_GOLD).getChar(), TEXT_COLOR("COLOR_NEGATIVE_TEXT"), GET_PLAYER(ePlayer).getGold());
	}
	else
	{
		szString.Format(L"%c: %d", GC.getCommerceInfo(COMMERCE_GOLD).getChar(), GET_PLAYER(ePlayer).getGold());
	}

	int iGoldRate = GET_PLAYER(ePlayer).calculateGoldRate();
	if (iGoldRate < 0)
	{
		szString += gDLL->getText("TXT_KEY_MISC_NEG_GOLD_PER_TURN", iGoldRate);
	}
	else if (iGoldRate > 0)
	{
		szString += gDLL->getText("TXT_KEY_MISC_POS_GOLD_PER_TURN", iGoldRate);
	}

	if (GET_PLAYER(ePlayer).isStrike())
	{
		szString += gDLL->getText("TXT_KEY_MISC_STRIKE");
	}
}


void CvGameTextMgr::setResearchStr(CvWString& szString, PlayerTypes ePlayer)
{
	CvWString szTempBuffer;

	szString = gDLL->getText("TXT_KEY_MISC_RESEARCH_STRING", GC.getTechInfo(GET_PLAYER(ePlayer).getCurrentResearch()).getTextKeyWide());

	if (GET_TEAM(GET_PLAYER(ePlayer).getTeam()).getTechCount(GET_PLAYER(ePlayer).getCurrentResearch()) > 0)
	{
		szTempBuffer.Format(L" %d", (GET_TEAM(GET_PLAYER(ePlayer).getTeam()).getTechCount(GET_PLAYER(ePlayer).getCurrentResearch()) + 1));
		szString+=szTempBuffer;
	}

	szTempBuffer.Format(L" (%d)", GET_PLAYER(ePlayer).getResearchTurnsLeft(GET_PLAYER(ePlayer).getCurrentResearch(), true));
	szString+=szTempBuffer;
}


void CvGameTextMgr::setOOSSeeds(CvWString& szString, PlayerTypes ePlayer)
{
	if (GET_PLAYER(ePlayer).isHuman())
	{
		int iNetID = GET_PLAYER(ePlayer).getNetID();
		if (gDLL->isConnected(iNetID))
		{
			szString = gDLL->getText("TXT_KEY_PLAYER_OOS", gDLL->GetSyncOOS(iNetID), gDLL->GetOptionsOOS(iNetID));
		}
	}
}

void CvGameTextMgr::setNetStats(CvWString& szString, PlayerTypes ePlayer)
{
	if (ePlayer != GC.getGameINLINE().getActivePlayer())
	{
		if (GET_PLAYER(ePlayer).isHuman())
		{
			if (gDLL->getInterfaceIFace()->isNetStatsVisible())
			{
				int iNetID = GET_PLAYER(ePlayer).getNetID();
				if (gDLL->isConnected(iNetID))
				{
					szString = gDLL->getText("TXT_KEY_MISC_NUM_MS", gDLL->GetLastPing(iNetID));
				}
				else
				{
					szString = gDLL->getText("TXT_KEY_MISC_DISCONNECTED");
				}
			}
		}
		else
		{
			szString = gDLL->getText("TXT_KEY_MISC_AI");
		}
	}
}


void CvGameTextMgr::setMinimizePopupHelp(CvWString& szString, const CvPopupInfo & info)
{
	CvCity* pCity;
	UnitTypes eTrainUnit;
	BuildingTypes eConstructBuilding;
	ProjectTypes eCreateProject;
	ReligionTypes eReligion;
	CivicTypes eCivic;

	switch (info.getButtonPopupType())
	{
	case BUTTONPOPUP_CHOOSEPRODUCTION:
		pCity = GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getCity(info.getData1());
		if (pCity != NULL)
		{
			eTrainUnit = NO_UNIT;
			eConstructBuilding = NO_BUILDING;
			eCreateProject = NO_PROJECT;

			switch (info.getData2())
			{
			case (ORDER_TRAIN):
				eTrainUnit = (UnitTypes)info.getData3();
				break;
			case (ORDER_CONSTRUCT):
				eConstructBuilding = (BuildingTypes)info.getData3();
				break;
			case (ORDER_CREATE):
				eCreateProject = (ProjectTypes)info.getData3();
				break;
			default:
				break;
			}

			if (eTrainUnit != NO_UNIT)
			{
				szString += gDLL->getText("TXT_KEY_MINIMIZED_CHOOSE_PRODUCTION_UNIT", GC.getUnitInfo(eTrainUnit).getTextKeyWide(), pCity->getNameKey());
			}
			else if (eConstructBuilding != NO_BUILDING)
			{
				szString += gDLL->getText("TXT_KEY_MINIMIZED_CHOOSE_PRODUCTION_BUILDING", GC.getBuildingInfo(eConstructBuilding).getTextKeyWide(), pCity->getNameKey());
			}
			else if (eCreateProject != NO_PROJECT)
			{
				szString += gDLL->getText("TXT_KEY_MINIMIZED_CHOOSE_PRODUCTION_PROJECT", GC.getProjectInfo(eCreateProject).getTextKeyWide(), pCity->getNameKey());
			}
			else
			{
				szString += gDLL->getText("TXT_KEY_MINIMIZED_CHOOSE_PRODUCTION", pCity->getNameKey());
			}
		}
		break;

	case BUTTONPOPUP_CHANGERELIGION:
		eReligion = ((ReligionTypes)(info.getData1()));
		if (eReligion != NO_RELIGION)
		{
			szString += gDLL->getText("TXT_KEY_MINIMIZED_CHANGE_RELIGION", GC.getReligionInfo(eReligion).getTextKeyWide());
		}
		break;

	case BUTTONPOPUP_CHOOSETECH:
		if (info.getData1() > 0)
		{
			szString += gDLL->getText("TXT_KEY_MINIMIZED_CHOOSE_TECH_FREE");
		}
		else
		{
			szString += gDLL->getText("TXT_KEY_MINIMIZED_CHOOSE_TECH");
		}
		break;

	case BUTTONPOPUP_CHANGECIVIC:
		eCivic = ((CivicTypes)(info.getData2()));
		if (eCivic != NO_CIVIC)
		{
			szString += gDLL->getText("TXT_KEY_MINIMIZED_CHANGE_CIVIC", GC.getCivicInfo(eCivic).getTextKeyWide());
		}
		break;
	}
}

void CvGameTextMgr::setEspionageMissionHelp(CvWStringBuffer &szBuffer, const CvUnit* pUnit)
{
	if (pUnit->isSpy())
	{
		PlayerTypes eOwner =  pUnit->plot()->getOwnerINLINE();
		if (NO_PLAYER != eOwner && GET_PLAYER(eOwner).getTeam() != pUnit->getTeam())
		{
			if (!pUnit->canEspionage(pUnit->plot()))
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_UNIT_HELP_NO_ESPIONAGE"));

				if (pUnit->hasMoved() || pUnit->isMadeAttack())
				{
					szBuffer.append(gDLL->getText("TXT_KEY_UNIT_HELP_NO_ESPIONAGE_REASON_MOVED"));
				}
				else if (!pUnit->isInvisible(GET_PLAYER(eOwner).getTeam(), false))
				{
					szBuffer.append(gDLL->getText("TXT_KEY_UNIT_HELP_NO_ESPIONAGE_REASON_VISIBLE", GET_PLAYER(eOwner).getNameKey()));
				}
			}
			else if (pUnit->getFortifyTurns() > 0)
			{
				int iModifier = -(pUnit->getFortifyTurns() * GC.getDefineINT("ESPIONAGE_EACH_TURN_UNIT_COST_DECREASE"));
				if (0 != iModifier)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_COST", iModifier));
				}
			}
		}
	}
}


void CvGameTextMgr::setUnitHelp(CvWStringBuffer &szString, const CvUnit* pUnit, bool bOneLine, bool bShort)
{
	PROFILE_FUNC();

	CvWString szTempBuffer;
	BuildTypes eBuild;
	int iCurrMoves;
	int iI;
	bool bFirst;
	bool bShift = gDLL->shiftKey();
	bool bAlt = gDLL->altKey();

	CvUnitInfo& kUnitInfo = GC.getUnitInfo(pUnit->getUnitType());

//FlavourMod: Added by Jean Elcard (display unit combat symbol in unit tool tip) - integrated into BUG by Tholal
	if (getBugOptionBOOL("MainInterface__UnitCombatIcons", true, "BUG_UNIT_COMBAT_ICONS"))
	{
		if (pUnit->getUnitCombatType() != NO_UNITCOMBAT)
		{
			szTempBuffer.Format(L"<img=%S size=16></img> ", GC.getUnitCombatInfo(pUnit->getUnitCombatType()).getButton());
			szString.append(szTempBuffer);
		}
	}
//FlavourMod: End

	szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_UNIT_TEXT"), pUnit->getName().GetCString());
	szString.append(szTempBuffer);

	szString.append(L", ");

	if (pUnit->getDomainType() == DOMAIN_AIR)
	{
		if (pUnit->airBaseCombatStr() > 0)
		{
			if (pUnit->isFighting())
			{
				szTempBuffer.Format(L"?/%d%c, ", pUnit->airBaseCombatStr(), gDLL->getSymbolID(STRENGTH_CHAR));
			}
			else if (pUnit->isHurt())
			{
				szTempBuffer.Format(L"%.1f/%d%c, ", (((float)(pUnit->airBaseCombatStr() * pUnit->currHitPoints())) / ((float)(pUnit->maxHitPoints()))), pUnit->airBaseCombatStr(), gDLL->getSymbolID(STRENGTH_CHAR));
			}
			else
			{
				szTempBuffer.Format(L"%d%c, ", pUnit->airBaseCombatStr(), gDLL->getSymbolID(STRENGTH_CHAR));
			}
			szString.append(szTempBuffer);
		}
	}
	else
	{
		if (pUnit->canFight())
		{

//FfH: Modified by Kael 08/18/2007
//			if (pUnit->isFighting())
//			{
//				szTempBuffer.Format(L"?/%d%c, ", pUnit->baseCombatStr(), gDLL->getSymbolID(STRENGTH_CHAR));
//			}
//			else if (pUnit->isHurt())
//			{
//				szTempBuffer.Format(L"%.1f/%d%c, ", (((float)(pUnit->baseCombatStr() * pUnit->currHitPoints())) / ((float)(pUnit->maxHitPoints()))), pUnit->baseCombatStr(), gDLL->getSymbolID(STRENGTH_CHAR));
//			}
//			else
//			{
//				szTempBuffer.Format(L"%d%c, ", pUnit->baseCombatStr(), gDLL->getSymbolID(STRENGTH_CHAR));
//			}
//			szString.append(szTempBuffer);

/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**																								**/
/*************************************************************************************************/
/** Orig
            int iDif = pUnit->getTotalDamageTypeCombat();
			if (pUnit->isFighting())
			{
				szTempBuffer.Format(L"?/%d", pUnit->baseCombatStr() - iDif);
			}
			else if (pUnit->isHurt())
			{
                if (pUnit->baseCombatStr() == pUnit->baseCombatStrDefense())
                {
                    szTempBuffer.Format(L"%.1f/%d", (((float)((pUnit->baseCombatStr() - iDif) * pUnit->currHitPoints())) / ((float)(pUnit->maxHitPoints()))), pUnit->baseCombatStr());
                }
                else
                {
                    szTempBuffer.Format(L"%.1f/%.lf", (((float)((pUnit->baseCombatStr() - iDif) * pUnit->currHitPoints())) / ((float)(pUnit->maxHitPoints()))), (((float)((pUnit->baseCombatStrDefense() - iDif) * pUnit->currHitPoints())) / ((float)(pUnit->maxHitPoints()))));
                }
			}
			else
			{
                if (pUnit->baseCombatStr() == pUnit->baseCombatStrDefense())
                {
    				szTempBuffer.Format(L"%d", pUnit->baseCombatStr() - iDif);
                }
                else
                {
                    szTempBuffer.Format(L"%d/%d", pUnit->baseCombatStr() - iDif, pUnit->baseCombatStrDefense() - iDif);
                }
			}
			szString.append(szTempBuffer);
            for (iI = 0; iI < GC.getNumDamageTypeInfos(); iI++)
            {
                if (pUnit->getDamageTypeCombat((DamageTypes)iI) != 0)
                {
                    szTempBuffer.Format(L" (+%d %s)", pUnit->getDamageTypeCombat((DamageTypes)iI), GC.getDamageTypeInfo((DamageTypes)iI).getDescription());
                    szString.append(szTempBuffer);
                }
            }
            szTempBuffer.Format(L"%c, ", gDLL->getSymbolID(STRENGTH_CHAR));
            szString.append(szTempBuffer);
**/
			const int iDif = pUnit->getTotalDamageTypeCombat();

			//wounded color
			const int iDmgLv = std::max(0, std::min(3, 4 * pUnit->getDamage() / pUnit->maxHitPoints()));
			const char* szColor[] =
			{
				"COLOR_WHITE",
				"COLOR_WHITE",
				"COLOR_PLAYER_LIGHT_ORANGE_TEXT",
				"COLOR_WARNING_TEXT",
			};

			if (pUnit->isFighting())
			{
				if (pUnit->baseCombatStr() == pUnit->baseCombatStrDefense())
				{
					szTempBuffer.Format(L"?(%d", pUnit->baseCombatStr() - iDif);
				}
				else
				{
					szTempBuffer.Format(L"?/?(%d/%d", pUnit->baseCombatStr() - iDif, pUnit->baseCombatStrDefense() - iDif);
				}
			}
			else if (pUnit->baseCombatStr() == pUnit->baseCombatStrDefense())
			{
				if (pUnit->isHurt())
				{
					const float fAttStr = (float)pUnit->baseCombatStr() * (float)pUnit->currHitPoints() / (float)pUnit->maxHitPoints();
					szTempBuffer.Format(SETCOLR L"%.1f" ENDCOLR L" (%d",
										TEXT_COLOR(szColor[iDmgLv]), fAttStr, pUnit->baseCombatStr() - iDif);
				}
				else
				{
					if (iDif != 0)
					{
						szTempBuffer.Format(L"%d(%d", pUnit->baseCombatStr(), pUnit->baseCombatStr() - iDif);
					}
					else
					{
						szTempBuffer.Format(L"%d", pUnit->baseCombatStr());
					}
				}
			}
			else
			{
				if (pUnit->isHurt())
				{
					const float fAttStr = (float)pUnit->baseCombatStr() * (float)pUnit->currHitPoints() / (float)pUnit->maxHitPoints();
					const float fDefStr = (float)pUnit->baseCombatStrDefense() * (float)pUnit->currHitPoints() / (float)pUnit->maxHitPoints();
					szTempBuffer.Format(SETCOLR L"%.1f" ENDCOLR L"/" SETCOLR L"%.1f" ENDCOLR L"(%d/%d",
										TEXT_COLOR(szColor[iDmgLv]), fAttStr, TEXT_COLOR(szColor[iDmgLv]), fDefStr, pUnit->baseCombatStr() - iDif, pUnit->baseCombatStrDefense() - iDif);
				}
				else
				{
					if (iDif != 0)
					{
						szTempBuffer.Format(L"%d/%d(%d/%d", pUnit->baseCombatStr(), pUnit->baseCombatStrDefense(), pUnit->baseCombatStr() - iDif, pUnit->baseCombatStrDefense() - iDif);
					}
					else
					{
						szTempBuffer.Format(L"%d/%d", pUnit->baseCombatStr(), pUnit->baseCombatStrDefense());
					}
				}
			}
			szString.append(szTempBuffer);
			for (iI = 0; iI < GC.getNumDamageTypeInfos(); iI++)
			{
				if (pUnit->getDamageTypeCombat((DamageTypes)iI) != 0)
				{
					szTempBuffer.Format(L", +%d %s", pUnit->getDamageTypeCombat((DamageTypes)iI), GC.getDamageTypeInfo((DamageTypes)iI).getDescription());
					szString.append(szTempBuffer);
				}
			}
			if (pUnit->isHurt() || iDif != 0)
			{
				szString.append(L")");
			}
			szTempBuffer.Format(L"%c, ", gDLL->getSymbolID(STRENGTH_CHAR));
			szString.append(szTempBuffer);
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/

//FfH: End Modify

		}
	}

	iCurrMoves = ((pUnit->movesLeft() / GC.getMOVE_DENOMINATOR()) + (((pUnit->movesLeft() % GC.getMOVE_DENOMINATOR()) > 0) ? 1 : 0));
	if ((pUnit->baseMoves() == iCurrMoves) || (pUnit->getTeam() != GC.getGameINLINE().getActiveTeam()))
	{
		szTempBuffer.Format(L"%d%c", pUnit->baseMoves(), gDLL->getSymbolID(MOVES_CHAR));
	}
	else
	{
		szTempBuffer.Format(L"%d/%d%c", iCurrMoves, pUnit->baseMoves(), gDLL->getSymbolID(MOVES_CHAR));
	}
	szString.append(szTempBuffer);

	if (pUnit->airRange() > 0)
	{
		szString.append(gDLL->getText("TXT_KEY_UNIT_HELP_AIR_RANGE", pUnit->airRange()));
	}

	eBuild = pUnit->getBuildType();

	if (eBuild != NO_BUILD)
	{
		szString.append(L", ");
		szTempBuffer.Format(L"%s (%d)", GC.getBuildInfo(eBuild).getDescription(), pUnit->plot()->getBuildTurnsLeft(eBuild, 0, 0));
		szString.append(szTempBuffer);
	}

	if (pUnit->getImmobileTimer() > 0)
	{
		szString.append(L", ");

//FfH: Modified by Kael 09/15/2008
//		szString.append(gDLL->getText("TXT_KEY_UNIT_HELP_IMMOBILE", pUnit->getImmobileTimer()));
        if (pUnit->isHeld())
        {
            szString.append(gDLL->getText("TXT_KEY_UNIT_HELP_HELD"));
        }
/*************************************************************************************************/
/**	Xienwolf Tweak							02/01/09											**/
/**	ADDON (reminder for spells being cast) merged Sephi											**/
/**						Reminds you what spell the unit is trying to cast						**/
/*************************************************************************************************/
		else if (pUnit->getDelayedSpell() != NO_SPELL)
		{
            szString.append(gDLL->getText("TXT_KEY_UNIT_HELP_DELAYED_CASTING", GC.getSpellInfo((SpellTypes)pUnit->getDelayedSpell()).getDescription(), pUnit->getImmobileTimer()));
		}
/*************************************************************************************************/
/**	Tweak									END													**/
/*************************************************************************************************/
        else
        {
            szString.append(gDLL->getText("TXT_KEY_UNIT_HELP_IMMOBILE", pUnit->getImmobileTimer()));
        }
//FfH: End Modify

	}

	/*if (!bOneLine)
	{
		if (pUnit->getUnitCombatType() != NO_UNITCOMBAT)
		{
			szTempBuffer.Format(L" (%s)", GC.getUnitCombatInfo(pUnit->getUnitCombatType()).getDescription());
			szString += szTempBuffer;
		}
	}*/

	if (GC.getGameINLINE().isDebugMode() && !bAlt && !bShift)
	{
		FAssertMsg(pUnit->AI_getUnitAIType() != NO_UNITAI, "pUnit's AI type expected to != NO_UNITAI");

// Better AI Debug (Skyre)
		/*
		szTempBuffer.Format(L" (%s)", GC.getUnitAIInfo(pUnit->AI_getUnitAIType()).getDescription());
		*/
		if (pUnit->AI_getGroupflag() != GROUPFLAG_NONE)
		{
			szTempBuffer.Format(L" (%s)", getGroupflagName(pUnit->AI_getGroupflag()));
		}
		else
		{
			szTempBuffer.Format(L" (%s)", GC.getUnitAIInfo(pUnit->AI_getUnitAIType()).getDescription());
		}
// End Better AI Debug
		szString.append(szTempBuffer);
	}

	if ((pUnit->getTeam() == GC.getGameINLINE().getActiveTeam()) || GC.getGameINLINE().isDebugMode())
	{
		if ((pUnit->getExperience() > 0) && !(pUnit->isFighting()))
		{
			szString.append(gDLL->getText("TXT_KEY_UNIT_HELP_LEVEL", pUnit->getExperience(), pUnit->experienceNeeded()));
		}
	}

//FfH: Modified by Kael 08/27/2007
//	if (pUnit->getOwnerINLINE() != GC.getGameINLINE().getActivePlayer() && !pUnit->isAnimal() && !pUnit->getUnitInfo().isHiddenNationality())
	if (pUnit->getOwnerINLINE() != GC.getGameINLINE().getActivePlayer() && !pUnit->isAnimal() && !pUnit->isHiddenNationality())
//FfH: End Modify

	{
		szString.append(L", ");
/************************************************************************************************/
/* REVOLUTION_MOD                         02/01/08                                jdog5000      */
/*                                                                                              */
/*                                                                                              */
/************************************************************************************************/
/* original code
		szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, GET_PLAYER(pUnit->getOwnerINLINE()).getPlayerTextColorR(), GET_PLAYER(pUnit->getOwnerINLINE()).getPlayerTextColorG(), GET_PLAYER(pUnit->getOwnerINLINE()).getPlayerTextColorB(), GET_PLAYER(pUnit->getOwnerINLINE()).getPlayerTextColorA(), GET_PLAYER(pUnit->getOwnerINLINE()).getName());
*/
		// For minor civs, display civ name instead of player name ... to differentiate
		// and help human recognize why they can't contact that player
		if( GET_PLAYER(pUnit->getOwnerINLINE()).isMinorCiv() )
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, GET_PLAYER(pUnit->getOwnerINLINE()).getPlayerTextColorR(), GET_PLAYER(pUnit->getOwnerINLINE()).getPlayerTextColorG(), GET_PLAYER(pUnit->getOwnerINLINE()).getPlayerTextColorB(), GET_PLAYER(pUnit->getOwnerINLINE()).getPlayerTextColorA(), GET_PLAYER(pUnit->getOwnerINLINE()).getCivilizationDescription());
		else
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, GET_PLAYER(pUnit->getOwnerINLINE()).getPlayerTextColorR(), GET_PLAYER(pUnit->getOwnerINLINE()).getPlayerTextColorG(), GET_PLAYER(pUnit->getOwnerINLINE()).getPlayerTextColorB(), GET_PLAYER(pUnit->getOwnerINLINE()).getPlayerTextColorA(), GET_PLAYER(pUnit->getOwnerINLINE()).getName());
/************************************************************************************************/
/* REVOLUTION_MOD                          END                                                  */
/************************************************************************************************/
		szString.append(szTempBuffer);
	}

	for (iI = 0; iI < GC.getNumPromotionInfos(); ++iI)
	{
		if (pUnit->isHasPromotion((PromotionTypes)iI))
		{
			szTempBuffer.Format(L"<img=%S size=16></img>", GC.getPromotionInfo((PromotionTypes)iI).getButton());
			szString.append(szTempBuffer);
		}
	}	

    if (bAlt && (gDLL->getChtLvl() > 0))
    {
		CvSelectionGroup* eGroup = pUnit->getGroup();
		if (eGroup != NULL)
		{
			if (pUnit->isGroupHead())
				szString.append(CvWString::format(L"\nLeading "));
			else
				szString.append(L"\n");

			szTempBuffer.Format(L"Group(%d), %d units", eGroup->getID(), eGroup->getNumUnits());
			szString.append(szTempBuffer);
		}
    }

	if (!bOneLine)
	{

//FfH: Added by Kael 07/23/2007
        if (pUnit->getReligion() != NO_RELIGION)
        {
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_RELIGION", GC.getReligionInfo((ReligionTypes)pUnit->getReligion()).getDescription()));
        }
        if (!pUnit->isAlive())
        {
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_NOT_ALIVE"));
			if (pUnit->getUnitInfo().isObject())
			{
				szString.append(" (object)");
			}
        }
		if (pUnit->isBlockading())
		{
			szString.append(NEWLINE);
            szString.append(CvWString::format(SETCOLR, TEXT_COLOR("COLOR_NEGATIVE_TEXT")));
			szString.append(gDLL->getText("TXT_KEY_MISSION_PLUNDER"));
            szString.append(CvWString::format(ENDCOLR));
		}
		if (pUnit->isHasCasted())
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_HAS_CASTED"));
		}
		if (pUnit->getDuration() != 0)
		{
			szString.append(NEWLINE);
            szString.append(CvWString::format(SETCOLR, TEXT_COLOR("COLOR_NEGATIVE_TEXT")));
			szString.append(gDLL->getText("TXT_KEY_UNIT_DURATION", pUnit->getDuration()));
            szString.append(CvWString::format(ENDCOLR));
		}
/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**	Moved to below(*1) by Denev 2009/09/05														**/
/*************************************************************************************************/
/**
        for (int iJ=0;iJ<GC.getNumPromotionInfos();iJ++)
        {
            if (pUnit->isHasPromotion((PromotionTypes)iJ) && GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod()>0)
            {
                szString.append(NEWLINE);
                szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod(), GC.getPromotionInfo((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatType()).getTextKeyWide()));
            }
        }
**/
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/
//FfH: End Add

		setEspionageMissionHelp(szString, pUnit);

		if (pUnit->cargoSpace() > 0)
		{
			if (pUnit->getTeam() == GC.getGameINLINE().getActiveTeam())
			{
				szTempBuffer = NEWLINE + gDLL->getText("TXT_KEY_UNIT_HELP_CARGO_SPACE", pUnit->getCargo(), pUnit->cargoSpace());
			}
			else
			{
				szTempBuffer = NEWLINE + gDLL->getText("TXT_KEY_UNIT_CARGO_SPACE", pUnit->cargoSpace());
			}
			szString.append(szTempBuffer);

			if (pUnit->specialCargo() != NO_SPECIALUNIT)
			{
				szString.append(gDLL->getText("TXT_KEY_UNIT_CARRIES", GC.getSpecialUnitInfo(pUnit->specialCargo()).getTextKeyWide()));
			}
		}

		if (pUnit->fortifyModifier() != 0)
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_HELP_FORTIFY_BONUS", pUnit->fortifyModifier()));
		}

/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**	Added by Denev 2009/09/06 get Abilities from promotions										**/
/*************************************************************************************************/
//BUGFfH: Added by Denev 2009/09/06
		int iTotalBetrayalChance = 0;
		std::vector<CvWString> aszPromotionRandomApply;
		std::vector<CvWString> aszPromotionImmune;
		std::vector<CvWString> aszPromotionSummonPerk;
		std::vector<CvWString> aszPromotionCombatApply;
		std::vector<CvWString> aszCaptureUnitCombat;

		int iTotalCombatCapturePercent = 0;
		int iTotalFreeXPFromCombat = 0;
		int iTotalGoldFromCombat = 0;
		int iTotalModifyGlobalCounter = 0;
		int iTotalModifyGlobalCounterOnCombat = 0;
		int iTotalFreeXPPerTurn = 0;
		std::vector<int> aiPromotionCombatMod;

		//Initialize
		for (int iPromotionCombatType = 0; iPromotionCombatType < GC.getNumPromotionInfos(); iPromotionCombatType++)
		{
			aiPromotionCombatMod.push_back(0);
		}

		//get ModifyGlobalCounter from UnitTypes
		iTotalModifyGlobalCounter += kUnitInfo.getModifyGlobalCounter();

		//get FreeXPFromCombat from Traits
		for (iI = 0; iI < GC.getNumTraitInfos(); iI++)
		{
			if (GET_PLAYER(pUnit->getOwnerINLINE()).hasTrait((TraitTypes) iI))
			{
				const int iFreeXPFromCombat = GC.getTraitInfo((TraitTypes) iI).getFreeXPFromCombat();
				if (iFreeXPFromCombat != 0)
				{
					iTotalFreeXPFromCombat += iFreeXPFromCombat;
				}
			}
		}

		//Whether the unit has summoning ability or not
		bool bSummoningAbility = false;
		if (pUnit->isHasPromotion((PromotionTypes) GC.getInfoTypeForString("PROMOTION_CHANNELING1")))
		{
			bSummoningAbility = true;
		}
		else
		{
			for (iI = 0; iI < GC.getNumSpellInfos(); ++iI)
			{
				if (GC.getSpellInfo((SpellTypes) iI).getUnitClassPrereq() == pUnit->getUnitClassType()
				 && GC.getSpellInfo((SpellTypes) iI).getCreateUnitType() != NO_UNIT)
				{
					bSummoningAbility = true;
					break;
				}
			}
		}

		for (iI = 0; iI < GC.getNumPromotionInfos(); iI++)
		{
			// XML_LISTS 07/2019 lfgr
			if( pUnit->isPromotionImmune( (PromotionTypes) iI ) ) {
				szTempBuffer = GC.getPromotionInfo( (PromotionTypes) iI ).getDescription();
				aszPromotionImmune.push_back(szTempBuffer);
			}
			// XML_LISTS end
			if (pUnit->isHasPromotion((PromotionTypes) iI))
			{
				if (GC.getPromotionInfo((PromotionTypes) iI).getBetrayalChance() != 0)
				{
					iTotalBetrayalChance += GC.getPromotionInfo((PromotionTypes) iI).getBetrayalChance();
				}

				const PromotionTypes ePromotionRandomApply = (PromotionTypes) GC.getPromotionInfo((PromotionTypes) iI).getPromotionRandomApply();
				if (ePromotionRandomApply != NO_PROMOTION)
				{
					szTempBuffer = GC.getPromotionInfo(ePromotionRandomApply).getDescription();
					aszPromotionRandomApply.push_back(szTempBuffer);
				}

				const PromotionTypes ePromotionSummonPerk = (PromotionTypes) GC.getPromotionInfo((PromotionTypes) iI).getPromotionSummonPerk();
				if (ePromotionSummonPerk != NO_PROMOTION)
				{
					szTempBuffer = GC.getPromotionInfo(ePromotionSummonPerk).getDescription();
					aszPromotionSummonPerk.push_back(szTempBuffer);
				}

				const PromotionTypes ePromotionCombatApply = (PromotionTypes) GC.getPromotionInfo((PromotionTypes) iI).getPromotionCombatApply();
				if (ePromotionCombatApply != NO_PROMOTION)
				{
					szTempBuffer = GC.getPromotionInfo(ePromotionCombatApply).getDescription();
					aszPromotionCombatApply.push_back(szTempBuffer);
				}

				const UnitCombatTypes eCaptureUnitCombat = (UnitCombatTypes) GC.getPromotionInfo((PromotionTypes) iI).getCaptureUnitCombat();
				if (eCaptureUnitCombat != NO_UNITCOMBAT)
				{
					szTempBuffer = GC.getUnitCombatInfo(eCaptureUnitCombat).getDescription();
					aszCaptureUnitCombat.push_back(szTempBuffer);
				}
				const int iCombatCapturePercent = GC.getPromotionInfo((PromotionTypes) iI).getCombatCapturePercent();
				if (iCombatCapturePercent != 0)
				{
					iTotalCombatCapturePercent += iCombatCapturePercent;
				}

				//get FreeXPFromCombat from Promotions
				const int iFreeXPFromCombat = GC.getPromotionInfo((PromotionTypes) iI).getFreeXPFromCombat();
				if (iFreeXPFromCombat != 0)
				{
					iTotalFreeXPFromCombat += iFreeXPFromCombat;
				}

				const int iPromotionCombatMod = GC.getPromotionInfo((PromotionTypes) iI).getPromotionCombatMod();
				if (iPromotionCombatMod > 0)
				{
					int iPromotionCombatType = GC.getPromotionInfo((PromotionTypes) iI).getPromotionCombatType();
					aiPromotionCombatMod[iPromotionCombatType] += iPromotionCombatMod;
				}

				//get ModifyGlobalCounter from Promotions
				const int iModifyGlobalCounter = GC.getPromotionInfo((PromotionTypes) iI).getModifyGlobalCounter();
				if (iModifyGlobalCounter != 0)
				{
					iTotalModifyGlobalCounter += iModifyGlobalCounter;
				}

				const int iModifyGlobalCounterOnCombat = GC.getPromotionInfo((PromotionTypes) iI).getModifyGlobalCounterOnCombat();
				if (iModifyGlobalCounterOnCombat != 0)
				{
					iTotalModifyGlobalCounterOnCombat += iModifyGlobalCounterOnCombat;
				}

				const int iFreeXPPerTurn = GC.getPromotionInfo((PromotionTypes) iI).getFreeXPPerTurn();
				if (iFreeXPPerTurn != 0)
				{
					iTotalFreeXPPerTurn += iFreeXPPerTurn;
				}
			}
		}
		//sort and erase repeated items
		std::sort(aszPromotionRandomApply.begin(), aszPromotionRandomApply.end());
		aszPromotionRandomApply.erase(std::unique(aszPromotionRandomApply.begin(), aszPromotionRandomApply.end()), aszPromotionRandomApply.end());
		std::sort(aszPromotionImmune.begin(), aszPromotionImmune.end());
		aszPromotionImmune.erase(std::unique(aszPromotionImmune.begin(), aszPromotionImmune.end()), aszPromotionImmune.end());
		std::sort(aszPromotionSummonPerk.begin(), aszPromotionSummonPerk.end());
		aszPromotionSummonPerk.erase(std::unique(aszPromotionSummonPerk.begin(), aszPromotionSummonPerk.end()), aszPromotionSummonPerk.end());
		std::sort(aszPromotionCombatApply.begin(), aszPromotionCombatApply.end());
		aszPromotionCombatApply.erase(std::unique(aszPromotionCombatApply.begin(), aszPromotionCombatApply.end()), aszPromotionCombatApply.end());
		std::sort(aszCaptureUnitCombat.begin(), aszCaptureUnitCombat.end());
		aszCaptureUnitCombat.erase(std::unique(aszCaptureUnitCombat.begin(), aszCaptureUnitCombat.end()), aszCaptureUnitCombat.end());
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/

		if (!bShort)
		{
/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**	Added by Denev 2009/09/05 about Unfavorable effect																	**/
/*************************************************************************************************/
			if (iTotalBetrayalChance != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_BETRAYAL_CHANCE", iTotalBetrayalChance));
			}
			for (std::vector<CvWString>::iterator it = aszPromotionRandomApply.begin(); it != aszPromotionRandomApply.end(); it++)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_RANDOM_APPLY", (*it).GetCString()));
			}
			if (pUnit->isOnlyDefensive())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_ONLY_DEFENSIVE"));
			}
			if (kUnitInfo.isNoCapture())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_CANNOT_CAPTURE"));
			}
			if (!kUnitInfo.isPillage())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_CANNOT_PILLAGE"));
			}
			if (!kUnitInfo.isMilitaryHappiness())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_CANNOT_PROTECT_CITY"));
			}
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/

			if (pUnit->nukeRange() >= 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_CAN_NUKE"));
			}

			if (pUnit->alwaysInvisible())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_INVISIBLE_ALL"));
			}
			else if (pUnit->getInvisibleType() != NO_INVISIBLE)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_INVISIBLE_MOST"));
			}

			for (iI = 0; iI < pUnit->getNumSeeInvisibleTypes(); ++iI)
			{
				if (pUnit->getSeeInvisibleType(iI) != pUnit->getInvisibleType())
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_UNIT_SEE_INVISIBLE", GC.getInvisibleInfo(pUnit->getSeeInvisibleType(iI)).getTextKeyWide()));
				}
			}
/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**																								**/
/*************************************************************************************************/
// Moved from below(*7) by Denev 2009/09/06
			if (pUnit->getExtraVisibilityRange() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_VISIBILITY_TEXT", pUnit->getExtraVisibilityRange()));
			}
//BUGFfH: End Move
//BUGFfH: Added by Denev 2009/09/07
			if (kUnitInfo.isInvestigate())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_INVESTIGATE_CITY"));
			}
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/

			if (pUnit->canMoveImpassable())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_CAN_MOVE_IMPASSABLE"));
			}

			if (pUnit->canMoveLimitedBorders())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_CAN_MOVE_LIMITED_BORDERS"));
			}
/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**																								**/
/*************************************************************************************************/
			if (kUnitInfo.isRivalTerritory())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_EXPLORE_RIVAL"));
			}

//BUGFfH: Moved from below(*2) by Denev 2009/09/06
			if (pUnit->flatMovementCost())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_FLAT_MOVEMENT"));
			}
			else
			{
				if (pUnit->ignoreTerrainCost())
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_UNIT_IGNORE_TERRAIN"));
				}
//BUGFfH: End Move

//BUGFfH: Moved from below(*8) by Denev 2009/09/06
				else if (pUnit->getExtraMoveDiscount() != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_PROMOTION_MOVE_DISCOUNT_TEXT", -(pUnit->getExtraMoveDiscount())));
				}
//BUGFfH: End Move

//BUGFfH: Moved from below(*5) by Denev 2009/09/06
				if (pUnit->isHillsDoubleMove())
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_PROMOTION_HILLS_MOVE_TEXT"));
				}
//BUGFfH: End Move

//BUGFfH: Moved from below(*6) by Denev 2009/09/06
				for (iI = 0; iI < GC.getNumTerrainInfos(); ++iI)
				{
					if (pUnit->isTerrainDoubleMove((TerrainTypes)iI))
					{
						szString.append(NEWLINE);
						szString.append(gDLL->getText("TXT_KEY_PROMOTION_DOUBLE_MOVE_TEXT", GC.getTerrainInfo((TerrainTypes) iI).getTextKeyWide()));
					}
				}

				for (iI = 0; iI < GC.getNumFeatureInfos(); ++iI)
				{
					if (pUnit->isFeatureDoubleMove((FeatureTypes)iI))
					{
						szString.append(NEWLINE);
						szString.append(gDLL->getText("TXT_KEY_PROMOTION_DOUBLE_MOVE_TEXT", GC.getFeatureInfo((FeatureTypes) iI).getTextKeyWide()));
					}
				}
//BUGFfH: End Move

//BUGFfH: Added by Denev 2009/09/07
				bFirst = true;
				for (iI = 0; iI < GC.getNumTerrainInfos(); ++iI)
				{
					if (kUnitInfo.getTerrainImpassable((TerrainTypes) iI))
					{
						const int iTerrainPassableTech = kUnitInfo.getTerrainPassableTech(iI);
						if (NO_TECH == (TechTypes) iTerrainPassableTech
						 || !GET_PLAYER(pUnit->getOwnerINLINE()).isHasTech(iTerrainPassableTech))
						{
							szTempBuffer.Format(L"%s%s ", NEWLINE, gDLL->getText("TXT_KEY_UNIT_CANNOT_ENTER").GetCString());
							setListHelp(szString, szTempBuffer, gDLL->getText(GC.getTerrainInfo((TerrainTypes) iI).getTextKeyWide()), L", ", bFirst);
							bFirst = false;

							//const char cBullet = gDLL->getSymbolID(BULLET_CHAR);
							//const wchar* szCantEnter = gDLL->getText("TXT_KEY_UNIT_CANNOT_ENTER").GetCString();
							//const wchar* szTerrain = GC.getTerrainInfo((TerrainTypes) iI).getTextKeyWide();
							//szTempBuffer.Format(L"\n%c%s <link=literal>%s</link>", cBullet, szCantEnter, szTerrain);
							//szTempBuffer.Format(L"\n %s %s", szCantEnter, szTerrain);
							//szString.append(szTempBuffer);
						}
					}
				}

				bFirst = true;
				for (iI = 0; iI < GC.getNumFeatureInfos(); ++iI)
				{
					if (kUnitInfo.getFeatureImpassable((FeatureTypes) iI))
					{
						const int iFeaturePassableTech = kUnitInfo.getFeaturePassableTech(iI);
						if (NO_TECH == (TechTypes) iFeaturePassableTech
						 || !GET_PLAYER(pUnit->getOwnerINLINE()).isHasTech(iFeaturePassableTech))
						{
							szTempBuffer.Format(L"%s%s ", NEWLINE, gDLL->getText("TXT_KEY_UNIT_CANNOT_ENTER").GetCString());
							setListHelp(szString, szTempBuffer, gDLL->getText(GC.getFeatureInfo((FeatureTypes) iI).getTextKeyWide()), L", ", bFirst);
							bFirst = false;
							//const char cBullet = gDLL->getSymbolID(BULLET_CHAR);
							//const wchar* szCantEnter = gDLL->getText("TXT_KEY_UNIT_CANNOT_ENTER").GetCString();
							//const wchar* szFeature = GC.getFeatureInfo((FeatureTypes) iI).getTextKeyWide();
							//szTempBuffer.Format(L"\n%c%s <link=literal>%s</link>", cBullet, szCantEnter, szFeature);
							//szString.append(szTempBuffer);
						}
					}
				}
			}
//BUGFfH: End Add

			if (pUnit->getUnitInfo().getCultureGarrisonValue() > 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_CULTURE_GARRISON_VALUE", pUnit->getUnitInfo().getCultureGarrisonValue()));
			}

//BUGFfH: Moved from below(*3) by Denev 2009/09/06
			if (pUnit->isEnemyRoute())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_ENEMY_ROADS_TEXT"));
			}
//BUGFfH: End Move

//BUGFfH: Added by Denev 2009/09/06
			if (pUnit->isWaterWalking())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_WATER_WALKING_PEDIA"));
			}
//BUGFfH: End Add
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/

			// MiscastPromotions 10/2019 lfgr
			if( pUnit->getMiscastChance() != 0 )
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_SPELL_MISCAST_CHANCE_MODIFY", pUnit->getMiscastChance()));
			}
			// MiscastPromotions end
		}

		if (pUnit->maxFirstStrikes() > 0)
		{
			if (pUnit->firstStrikes() == pUnit->maxFirstStrikes())
			{
				if (pUnit->firstStrikes() == 1)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_UNIT_ONE_FIRST_STRIKE"));
				}
				else
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_UNIT_NUM_FIRST_STRIKES", pUnit->firstStrikes()));
				}
			}
			else
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_FIRST_STRIKE_CHANCES", pUnit->firstStrikes(), pUnit->maxFirstStrikes()));
			}
		}

		if (pUnit->immuneToFirstStrikes())
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_IMMUNE_FIRST_STRIKES"));
		}
/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**	Added by Denev 2009/09/05																	**/
/*************************************************************************************************/
		if (pUnit->getDefensiveStrikeChance() == 0)
		{
			if (pUnit->getDefensiveStrikeDamage() > 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_DEFENSIVE_STRIKE_DAMAGE_PEDIA", pUnit->getDefensiveStrikeDamage()));
			}
		}
		else
		{
			if (pUnit->getDefensiveStrikeDamage() > 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_DEFENSIVE_STRIKE_PEDIA", pUnit->getDefensiveStrikeChance(), pUnit->getDefensiveStrikeDamage()));
			}
			else
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_DEFENSIVE_STRIKE_CHANCE_PEDIA", pUnit->getDefensiveStrikeChance()));
			}
		}

		if (pUnit->isImmuneToDefensiveStrike())
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_PROMOTION_IMMUNE_TO_DEFENSIVE_STRIKE_PEDIA"));
		}
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/

		if (!bShort)
		{
			if (pUnit->noDefensiveBonus())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_NO_DEFENSE_BONUSES"));
			}
/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**	Added by Denev 2009/09/05																	**/
/*************************************************************************************************/
			if (pUnit->isDoubleFortifyBonus())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_DOUBLE_FORTIFY_BONUS"));
			}
			if (pUnit->isTargetWeakestUnitCounter())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_TARGET_WEAKEST_UNIT_COUNTER"));
			}
			const int iDefaultPercent = 100;
			if (pUnit->getBetterDefenderThanPercent() != iDefaultPercent)
			{
				szString.append(NEWLINE);
				if (pUnit->getBetterDefenderThanPercent() < iDefaultPercent)
				{
					szString.append(gDLL->getText("TXT_KEY_PROMOTION_BETTER_DEFENDER_THAN_PERCENT_LESS"));
				}
				if (pUnit->getBetterDefenderThanPercent() > iDefaultPercent)
				{
					szString.append(gDLL->getText("TXT_KEY_PROMOTION_BETTER_DEFENDER_THAN_PERCENT_MORE"));
				}
			}

//BUGFfH: Moved to above(*2) by Denev 2009/09/06
/*
			if (pUnit->flatMovementCost())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_FLAT_MOVEMENT"));
			}

			if (pUnit->ignoreTerrainCost())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_IGNORE_TERRAIN"));
			}
*/
//BUGFfH: End Move
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/



			if (pUnit->isBlitz())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_BLITZ_TEXT"));
			}

			if (pUnit->isAmphib())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_AMPHIB_TEXT"));
			}

			if (pUnit->isRiver())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_RIVER_ATTACK_TEXT"));
			}

/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**																								**/
/*************************************************************************************************/
//BUGFfH: Moved to above(*3) by Denev 2009/09/06
/*
			if (pUnit->isEnemyRoute())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_ENEMY_ROADS_TEXT"));
			}
*/
//BUGFfH: End Move

//BUGFfH: Moved to below(*4) by Denev 2009/09/06
/*
			if (pUnit->isAlwaysHeal())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_ALWAYS_HEAL_TEXT"));
			}
*/
//BUGFfH: End Move

//BUGFfH: Moved to above(*5) by Denev 2009/09/06
/*
			if (pUnit->isHillsDoubleMove())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_HILLS_MOVE_TEXT"));
			}
*/
//BUGFfH: End Move
//BUGFfH: Added by Denev 2009/09/06
			if (pUnit->ignoreBuildingDefense())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_IGNORE_BUILDING_DEFENSE"));
			}
			if (pUnit->isBoarding())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_BOARDING_PEDIA"));
			}

			if (pUnit->isFear())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_FEAR_PEDIA"));
			}
			if (pUnit->isTargetWeakestUnit())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_TARGET_WEAKEST_UNIT"));
			}

		/********************************************************/
		/*	BUGFfH comment: about Immune ability				*/
		/********************************************************/
			if (pUnit->isImmuneToCapture())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_IMMUNE_TO_CAPTURE_PEDIA"));
			}
			if (pUnit->isImmuneToMagic())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_IMMUNE_TO_MAGIC_PEDIA"));
			}
			if (pUnit->isImmuneToFear())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_IMMUNE_TO_FEAR_PEDIA"));
			}
			for (std::vector<CvWString>::iterator it = aszPromotionImmune.begin(); it != aszPromotionImmune.end(); it++)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_IMMUNE", (*it).GetCString()));
			}

		/********************************************************/
		/*	BUGFfH comment: about Spell ability					*/
		/********************************************************/
			if (pUnit->getSpellDamageModify() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_SPELL_DAMAGE_MODIFY", pUnit->getSpellDamageModify()));
			}
			if (pUnit->getResistModify() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_CASTER_RESIST_MODIFY", pUnit->getResistModify()));
			}
			if (pUnit->getResist() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_RESIST", pUnit->getResist()));
			}
			if (pUnit->isCastingBlocked())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_CASTING_BLOCKED"));
			}
			if (pUnit->isUpgradeBlocked())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_UPGRADE_BLOCKED"));
			}
			if (pUnit->isGiftingBlocked())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_GIFTING_BLOCKED"));
			}
			if (pUnit->isUpgradeOutsideBorders())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_UPGRADE_OUTSIDE_BORDERS"));
			}
			if (bSummoningAbility)
			{
				if (pUnit->isTwincast())
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_PROMOTION_TWINCAST_PEDIA"));
				}
				bool bFirst = true;
				for (std::vector<CvWString>::iterator it = aszPromotionSummonPerk.begin(); it != aszPromotionSummonPerk.end(); it++)
				{
					if (bFirst)
					{
						bFirst = false;
						szString.append(NEWLINE);
						szString.append(gDLL->getText("TXT_KEY_PROMOTION_SUMMON_PERK_HEADER"));
					}
					szTempBuffer.Format(L"\n\t%c<link=literal>%s</link>", gDLL->getSymbolID(BULLET_CHAR), (*it).GetCString());
					szString.append(szTempBuffer);
				}
			}

		/********************************************************/
		/*	BUGFfH comment: about After combat					*/
		/********************************************************/
			for (std::vector<CvWString>::iterator it = aszPromotionCombatApply.begin(); it != aszPromotionCombatApply.end(); it++)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_COMBAT_APPLY", (*it).GetCString()));
			}
			for (std::vector<CvWString>::iterator it = aszCaptureUnitCombat.begin(); it != aszCaptureUnitCombat.end(); it++)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_CAPTURE_UNITCOMBAT", (*it).GetCString()));
			}
			if (iTotalCombatCapturePercent != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_COMBAT_CAPTURE_PERCENT", iTotalCombatCapturePercent));
			}
			if (pUnit->getGoldFromCombat() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_GOLD_FROM_COMBAT", pUnit->getGoldFromCombat()));
			}

			const UnitTypes eUnitConvertFromCombat = (UnitTypes) kUnitInfo.getUnitConvertFromCombat();
			const int iUnitConvertFromCombatChance = kUnitInfo.getUnitConvertFromCombatChance();
			if (eUnitConvertFromCombat != NO_UNIT)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_CONVERT_FROM_COMBAT", iUnitConvertFromCombatChance, GC.getUnitInfo(eUnitConvertFromCombat).getDescription()));
			}

			const UnitTypes eUnitCreateFromCombat = (UnitTypes) kUnitInfo.getUnitCreateFromCombat();
			const int iUnitCreateFromCombatChance = kUnitInfo.getUnitCreateFromCombatChance();
			if (eUnitCreateFromCombat != NO_UNIT)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_CREATE_FROM_COMBAT", iUnitCreateFromCombatChance, GC.getUnitInfo(eUnitCreateFromCombat).getDescription()));
			}

			int iEnslavementChance = 0;
			iEnslavementChance += kUnitInfo.getEnslavementChance();
			iEnslavementChance += GET_PLAYER(pUnit->getOwnerINLINE()).getEnslavementChance();
			if (iEnslavementChance > 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_ENSLAVEMENT_CHANCE", iEnslavementChance));
			}

			const PromotionTypes ePromotionFromCombat = (PromotionTypes) kUnitInfo.getPromotionFromCombat();
			if (ePromotionFromCombat != NO_PROMOTION)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_PROMOTION_FROM_COMBAT", GC.getPromotionInfo(ePromotionFromCombat).getDescription()));
			}

			if (kUnitInfo.isNoWarWeariness())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_NO_WAR_WEARINESS"));
			}
			if (kUnitInfo.isExplodeInCombat())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_EXPLODE_IN_COMBAT"));
			}
			if (pUnit->isImmortal())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_IMMORTAL_PEDIA"));
			}
			if (pUnit->getCombatHealPercent() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_COMBAT_HEAL_PERCENT", pUnit->getCombatHealPercent()));
			}
//BUGFfH: End Add

//BUGFfH: Moved to above(*6) by Denev 2009/09/06
/*
			for (iI = 0; iI < GC.getNumTerrainInfos(); ++iI)
			{
				if (pUnit->isTerrainDoubleMove((TerrainTypes)iI))
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_PROMOTION_DOUBLE_MOVE_TEXT", GC.getTerrainInfo((TerrainTypes) iI).getTextKeyWide()));
				}
			}

			for (iI = 0; iI < GC.getNumFeatureInfos(); ++iI)
			{
				if (pUnit->isFeatureDoubleMove((FeatureTypes)iI))
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_PROMOTION_DOUBLE_MOVE_TEXT", GC.getFeatureInfo((FeatureTypes) iI).getTextKeyWide()));
				}
			}
*/
//BUGFfH: End Move

//BUGFfH: Moved to above(*7) by Denev 2009/09/06
/*
			if (pUnit->getExtraVisibilityRange() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_VISIBILITY_TEXT", pUnit->getExtraVisibilityRange()));
			}
*/
//BUGFfH: End Move

//BUGFfH: Moved to above(*8) by Denev 2009/09/06
/*
			if (pUnit->getExtraMoveDiscount() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_MOVE_DISCOUNT_TEXT", -(pUnit->getExtraMoveDiscount())));
			}
*/
//BUGFfH: End Move

//BUGFfH: Moved from above(*4) by Denev 2009/09/06
			if (pUnit->isAlwaysHeal())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_ALWAYS_HEAL_TEXT"));
			}
//BUGFfH: End Move

//BUGFfH: Added by Denev 2009/09/06
			if (pUnit->getExtraEnemyHeal() == pUnit->getExtraNeutralHeal() && pUnit->getExtraNeutralHeal() == pUnit->getExtraFriendlyHeal())
			{
				if (pUnit->getExtraEnemyHeal() != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_PROMOTION_HEALS_EXTRA_TEXT", pUnit->getExtraEnemyHeal()) + gDLL->getText("TXT_KEY_PROMOTION_DAMAGE_TURN_TEXT"));
				}
			}
			else
			{
//BUGFfH: End Add
			if (pUnit->getExtraEnemyHeal() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_HEALS_EXTRA_TEXT", pUnit->getExtraEnemyHeal()) + gDLL->getText("TXT_KEY_PROMOTION_ENEMY_LANDS_TEXT"));
			}

			if (pUnit->getExtraNeutralHeal() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_HEALS_EXTRA_TEXT", pUnit->getExtraNeutralHeal()) + gDLL->getText("TXT_KEY_PROMOTION_NEUTRAL_LANDS_TEXT"));
			}

			if (pUnit->getExtraFriendlyHeal() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_HEALS_EXTRA_TEXT", pUnit->getExtraFriendlyHeal()) + gDLL->getText("TXT_KEY_PROMOTION_FRIENDLY_LANDS_TEXT"));
			}
//BUGFfH: Added by Denev 2009/09/06
}
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/

			if (pUnit->getSameTileHeal() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_HEALS_SAME_TEXT", pUnit->getSameTileHeal()) + gDLL->getText("TXT_KEY_PROMOTION_DAMAGE_TURN_TEXT"));
			}

			if (pUnit->getAdjacentTileHeal() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_HEALS_ADJACENT_TEXT", pUnit->getAdjacentTileHeal()) + gDLL->getText("TXT_KEY_PROMOTION_DAMAGE_TURN_TEXT"));
			}
		}

		if (pUnit->currInterceptionProbability() > 0)
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_INTERCEPT_AIRCRAFT", pUnit->currInterceptionProbability()));
		}

		if (pUnit->evasionProbability() > 0)
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_EVADE_INTERCEPTION", pUnit->evasionProbability()));
		}

		if (pUnit->withdrawalProbability() > 0)
		{
			if (bShort)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_WITHDRAWL_PROBABILITY_SHORT", pUnit->withdrawalProbability()));
			}
			else
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_WITHDRAWL_PROBABILITY", pUnit->withdrawalProbability()));
			}
		}

		if (pUnit->combatLimit() < GC.getMAX_HIT_POINTS() && pUnit->canAttack())
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_COMBAT_LIMIT", (100 * pUnit->combatLimit()) / GC.getMAX_HIT_POINTS()));
		}

		if (pUnit->collateralDamage() > 0)
		{
			szString.append(NEWLINE);
			if (pUnit->getExtraCollateralDamage() == 0)
			{
				szString.append(gDLL->getText("TXT_KEY_UNIT_COLLATERAL_DAMAGE", ( 100 * pUnit->getUnitInfo().getCollateralDamageLimit() / GC.getMAX_HIT_POINTS())));
			}
			else
			{
				szString.append(gDLL->getText("TXT_KEY_UNIT_COLLATERAL_DAMAGE_EXTRA", pUnit->getExtraCollateralDamage()));
			}
		}

		for (iI = 0; iI < GC.getNumUnitCombatInfos(); ++iI)
		{
			if (pUnit->getUnitInfo().getUnitCombatCollateralImmune(iI))
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_COLLATERAL_IMMUNE", GC.getUnitCombatInfo((UnitCombatTypes)iI).getTextKeyWide()));
			}
		}

		if (pUnit->getCollateralDamageProtection() > 0)
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_PROMOTION_COLLATERAL_PROTECTION_TEXT", pUnit->getCollateralDamageProtection()));
		}

		if (pUnit->getExtraCombatPercent() != 0)
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_PROMOTION_STRENGTH_TEXT", pUnit->getExtraCombatPercent()));
		}

		if (pUnit->cityAttackModifier() == pUnit->cityDefenseModifier())
		{
			if (pUnit->cityAttackModifier() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_CITY_STRENGTH_MOD", pUnit->cityAttackModifier()));
			}
		}
		else
		{
			if (pUnit->cityAttackModifier() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_CITY_ATTACK_TEXT", pUnit->cityAttackModifier()));
			}

			if (pUnit->cityDefenseModifier() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_CITY_DEFENSE_TEXT", pUnit->cityDefenseModifier()));
			}
		}

		if (pUnit->animalCombatModifier() != 0)
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_ANIMAL_COMBAT_MOD", pUnit->animalCombatModifier()));
		}

		if (pUnit->getDropRange() > 0)
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_PARADROP_RANGE", pUnit->getDropRange()));
		}

		if (pUnit->hillsAttackModifier() == pUnit->hillsDefenseModifier())
		{
			if (pUnit->hillsAttackModifier() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_HILLS_STRENGTH", pUnit->hillsAttackModifier()));
			}
		}
		else
		{
			if (pUnit->hillsAttackModifier() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_HILLS_ATTACK", pUnit->hillsAttackModifier()));
			}

			if (pUnit->hillsDefenseModifier() != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_HILLS_DEFENSE", pUnit->hillsDefenseModifier()));
			}
		}

		for (iI = 0; iI < GC.getNumTerrainInfos(); ++iI)
		{
			if (pUnit->terrainAttackModifier((TerrainTypes)iI) == pUnit->terrainDefenseModifier((TerrainTypes)iI))
			{
				if (pUnit->terrainAttackModifier((TerrainTypes)iI) != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_UNIT_STRENGTH", pUnit->terrainAttackModifier((TerrainTypes)iI), GC.getTerrainInfo((TerrainTypes) iI).getTextKeyWide()));
				}
			}
			else
			{
				if (pUnit->terrainAttackModifier((TerrainTypes)iI) != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_UNIT_ATTACK", pUnit->terrainAttackModifier((TerrainTypes)iI), GC.getTerrainInfo((TerrainTypes) iI).getTextKeyWide()));
				}

				if (pUnit->terrainDefenseModifier((TerrainTypes)iI) != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_UNIT_DEFENSE", pUnit->terrainDefenseModifier((TerrainTypes)iI), GC.getTerrainInfo((TerrainTypes) iI).getTextKeyWide()));
				}
			}
		}

		for (iI = 0; iI < GC.getNumFeatureInfos(); ++iI)
		{
			if (pUnit->featureAttackModifier((FeatureTypes)iI) == pUnit->featureDefenseModifier((FeatureTypes)iI))
			{
				if (pUnit->featureAttackModifier((FeatureTypes)iI) != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_UNIT_STRENGTH", pUnit->featureAttackModifier((FeatureTypes)iI), GC.getFeatureInfo((FeatureTypes) iI).getTextKeyWide()));
				}
			}
			else
			{
				if (pUnit->featureAttackModifier((FeatureTypes)iI) != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_UNIT_ATTACK", pUnit->featureAttackModifier((FeatureTypes)iI), GC.getFeatureInfo((FeatureTypes) iI).getTextKeyWide()));
				}

				if (pUnit->featureDefenseModifier((FeatureTypes)iI) != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_UNIT_DEFENSE", pUnit->featureDefenseModifier((FeatureTypes)iI), GC.getFeatureInfo((FeatureTypes) iI).getTextKeyWide()));
				}
			}
		}
/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**																								**/
/*************************************************************************************************/

//BUGFfH: Moved from above(*1) by Denev 2009/09/05
/*
		for (int iJ=0;iJ<GC.getNumPromotionInfos();iJ++)
		{
			if (pUnit->isHasPromotion((PromotionTypes)iJ) && GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod()>0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod(), GC.getPromotionInfo((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatType()).getTextKeyWide()));
			}
		}
*/
		for (int iPromotionCombatType = 0; iPromotionCombatType < GC.getNumPromotionInfos(); iPromotionCombatType++)
		{
			if (aiPromotionCombatMod[iPromotionCombatType] != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_MOD_VS_TYPE", aiPromotionCombatMod[iPromotionCombatType], GC.getPromotionInfo((PromotionTypes) iPromotionCombatType).getDescription()));
			}
		}
//BUGFfH: End Move
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/
		for (iI = 0; iI < GC.getNumUnitClassInfos(); ++iI)
		{
			if (pUnit->getUnitInfo().getUnitClassAttackModifier(iI) == kUnitInfo.getUnitClassDefenseModifier(iI))
			{
				if (pUnit->getUnitInfo().getUnitClassAttackModifier(iI) != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_UNIT_MOD_VS_TYPE", pUnit->getUnitInfo().getUnitClassAttackModifier(iI), GC.getUnitClassInfo((UnitClassTypes)iI).getTextKeyWide()));
				}
			}
			else
			{
				if (pUnit->getUnitInfo().getUnitClassAttackModifier(iI) != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_UNIT_ATTACK_MOD_VS_CLASS", pUnit->getUnitInfo().getUnitClassAttackModifier(iI), GC.getUnitClassInfo((UnitClassTypes)iI).getTextKeyWide()));
				}

				if (pUnit->getUnitInfo().getUnitClassDefenseModifier(iI) != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_UNIT_DEFENSE_MOD_VS_CLASS", pUnit->getUnitInfo().getUnitClassDefenseModifier(iI), GC.getUnitClassInfo((UnitClassTypes) iI).getTextKeyWide()));
				}
			}
		}

		for (iI = 0; iI < GC.getNumUnitCombatInfos(); ++iI)
		{
			if (pUnit->unitCombatModifier((UnitCombatTypes)iI) != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_MOD_VS_TYPE", pUnit->unitCombatModifier((UnitCombatTypes)iI), GC.getUnitCombatInfo((UnitCombatTypes) iI).getTextKeyWide()));
			}
		}

		for (iI = 0; iI < NUM_DOMAIN_TYPES; ++iI)
		{
			if (pUnit->domainModifier((DomainTypes)iI) != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_MOD_VS_TYPE", pUnit->domainModifier((DomainTypes)iI), GC.getDomainInfo((DomainTypes)iI).getTextKeyWide()));
			}
		}
/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**																								**/
/*************************************************************************************************/
//BUGFfH: Added by Denev 2009/09/05
		/********************************************************/
		/*	BUGFfH comment: about Damage types ability			*/
		/********************************************************/
		if (!bShort)
		{
			for (iI = 0; iI < GC.getNumDamageTypeInfos(); iI++)
			{
/*
				if (pUnit->getDamageTypeCombat((DamageTypes)iI) != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_DAMAGE_TYPE_COMBAT", pUnit->getDamageTypeCombat((DamageTypes)iI), GC.getDamageTypeInfo((DamageTypes)iI).getDescription()));
				}
*/
				if (pUnit->getDamageTypeResist((DamageTypes)iI) != 0)
				{
					szString.append(NEWLINE);
					if (pUnit->getDamageTypeResist((DamageTypes)iI) == 100)
					{
						szString.append(gDLL->getText("TXT_KEY_PROMOTION_DAMAGE_TYPE_IMMUNE", GC.getDamageTypeInfo((DamageTypes)iI).getDescription()));
					}
					else
					{
						szString.append(gDLL->getText("TXT_KEY_PROMOTION_DAMAGE_TYPE_RESIST", pUnit->getDamageTypeResist((DamageTypes)iI), GC.getDamageTypeInfo((DamageTypes)iI).getDescription()));
					}
				}
			}
			for (iI = 0; iI < GC.getNumBonusInfos(); iI++)
			{
				if (pUnit->getBonusAffinity((BonusTypes)iI) != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_BONUS_AFFINITY", pUnit->getBonusAffinity((BonusTypes)iI), GC.getBonusInfo((BonusTypes)iI).getDescription()));
				}
			}

		/********************************************************/
		/*	BUGFfH comment: about Armageddon counter ability	*/
		/********************************************************/
			if (iTotalModifyGlobalCounter != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_MESSAGE_MODIFY_GLOBAL_COUNTER", iTotalModifyGlobalCounter));
			}
			if (iTotalModifyGlobalCounterOnCombat != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_MESSAGE_MODIFY_GLOBAL_COUNTER_ON_COMBAT", iTotalModifyGlobalCounterOnCombat));
			}

		/********************************************************/
		/*	BUGFfH comment: about Miscellaneous					*/
		/********************************************************/
			if (pUnit->isHiddenNationality())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_ALWAYS_HOSTILE"));
			}
			if (iTotalFreeXPFromCombat != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_FREE_XP_FROM_COMBAT", iTotalFreeXPFromCombat));
			}
			if (iTotalFreeXPPerTurn != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_PROMOTION_FREE_XP_PER_TURN", iTotalFreeXPPerTurn, GC.getDefineINT("FREE_XP_MAX")));
			}
		}

//BUGFfH: Moved from below(*9) by Denev 2009/09/07
		if (pUnit->bombardRate() > 0)
		{
			if (bShort)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_BOMBARD_RATE_SHORT", ((pUnit->bombardRate() * 100) / GC.getMAX_CITY_DEFENSE_DAMAGE())));
			}
			else
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_BOMBARD_RATE", ((pUnit->bombardRate() * 100) / GC.getMAX_CITY_DEFENSE_DAMAGE())));
			}
		}
//BUGFfH: End Move

		/********************************************************/
		/*	BUGFfH comment: about Work rate modifier			*/
		/********************************************************/
		if (pUnit->getWorkRateModify() != 0)
		{
			for (iI = 0; iI < GC.getNumBuildInfos(); ++iI)
			{
				if (kUnitInfo.getBuilds(iI))
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_PROMOTION_WORK_RATE_MODIFY", pUnit->getWorkRateModify()));
					break;
				}
			}
		}
//BUGFfH: End Add
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/
		szTempBuffer.clear();
		bFirst = true;
		for (iI = 0; iI < GC.getNumUnitClassInfos(); ++iI)
		{
			if (pUnit->getUnitInfo().getTargetUnitClass(iI))
			{
				if (bFirst)
				{
					bFirst = false;
				}
				else
				{
					szTempBuffer += L", ";
				}

				szTempBuffer += CvWString::format(L"<link=literal>%s</link>", GC.getUnitClassInfo((UnitClassTypes)iI).getDescription());
			}
		}

		if (!bFirst)
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_TARGETS_UNIT_FIRST", szTempBuffer.GetCString()));
		}

		szTempBuffer.clear();
		bFirst = true;
		for (iI = 0; iI < GC.getNumUnitClassInfos(); ++iI)
		{
			if (pUnit->getUnitInfo().getDefenderUnitClass(iI))
			{
				if (bFirst)
				{
					bFirst = false;
				}
				else
				{
					szTempBuffer += L", ";
				}

				szTempBuffer += CvWString::format(L"<link=literal>%s</link>", GC.getUnitClassInfo((UnitClassTypes)iI).getDescription());
			}
		}

		if (!bFirst)
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_DEFENDS_UNIT_FIRST", szTempBuffer.GetCString()));
		}

		szTempBuffer.clear();
		bFirst = true;
		for (iI = 0; iI < GC.getNumUnitCombatInfos(); ++iI)
		{
			if (pUnit->getUnitInfo().getTargetUnitCombat(iI))
			{
				if (bFirst)
				{
					bFirst = false;
				}
				else
				{
					szTempBuffer += L", ";
				}

				szTempBuffer += CvWString::format(L"<link=literal>%s</link>", GC.getUnitCombatInfo((UnitCombatTypes)iI).getDescription());
			}
		}

		if (!bFirst)
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_TARGETS_UNIT_FIRST", szTempBuffer.GetCString()));
		}

		szTempBuffer.clear();
		bFirst = true;
		for (iI = 0; iI < GC.getNumUnitCombatInfos(); ++iI)
		{
			if (pUnit->getUnitInfo().getDefenderUnitCombat(iI))
			{
				if (bFirst)
				{
					bFirst = false;
				}
				else
				{
					szTempBuffer += L", ";
				}

				szTempBuffer += CvWString::format(L"<link=literal>%s</link>", GC.getUnitCombatInfo((UnitCombatTypes)iI).getDescription());
			}
		}

		if (!bFirst)
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_DEFENDS_UNIT_FIRST", szTempBuffer.GetCString()));
		}

		szTempBuffer.clear();
		bFirst = true;
		for (iI = 0; iI < GC.getNumUnitClassInfos(); ++iI)
		{
			if (pUnit->getUnitInfo().getFlankingStrikeUnitClass(iI) > 0)
			{
				if (bFirst)
				{
					bFirst = false;
				}
				else
				{
					szTempBuffer += L", ";
				}

				szTempBuffer += CvWString::format(L"<link=literal>%s</link>", GC.getUnitClassInfo((UnitClassTypes)iI).getDescription());
			}
		}

		if (!bFirst)
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_FLANKING_STRIKES", szTempBuffer.GetCString()));
		}

/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**																								**/
/*************************************************************************************************/
//BUGFfH: Moved to above(*9) by Denev 2009/09/07
/*

		if (pUnit->bombardRate() > 0)
		{
			if (bShort)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_BOMBARD_RATE_SHORT", ((pUnit->bombardRate() * 100) / GC.getMAX_CITY_DEFENSE_DAMAGE())));
			}
			else
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_UNIT_BOMBARD_RATE", ((pUnit->bombardRate() * 100) / GC.getMAX_CITY_DEFENSE_DAMAGE())));
			}
		}
*/
//BUGFfH: End Move
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/
		if (pUnit->isSpy())
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_IS_SPY"));
		}

		if (pUnit->getUnitInfo().isNoRevealMap())
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_UNIT_VISIBILITY_MOVE_RANGE"));
		}

		if (!CvWString(pUnit->getUnitInfo().getHelp()).empty())
		{
			szString.append(NEWLINE);
			szString.append(pUnit->getUnitInfo().getHelp());
		}

        if (bShift && (gDLL->getChtLvl() > 0))
        {
            szTempBuffer.Format(L"\nUnitAI Type = %s.", GC.getUnitAIInfo(pUnit->AI_getUnitAIType()).getDescription());
            szString.append(szTempBuffer);
            szTempBuffer.Format(L"\nSacrifice Value = %d.", pUnit->AI_sacrificeValue(NULL));
            szString.append(szTempBuffer);
        }
	}
}


void CvGameTextMgr::setPlotListHelp(CvWStringBuffer &szString, CvPlot* pPlot, bool bOneLine, bool bShort)
{
	PROFILE_FUNC();

	int numPromotionInfos = GC.getNumPromotionInfos();

	// if cheatmode and ctrl, display grouping info instead
	if ((gDLL->getChtLvl() > 0) && gDLL->ctrlKey())
	{
		if (pPlot->isVisible(GC.getGameINLINE().getActiveTeam(), GC.getGameINLINE().isDebugMode()))
		{
			CvWString szTempString;

			CLLNode<IDInfo>* pUnitNode = pPlot->headUnitNode();
			while(pUnitNode != NULL)
			{
				CvUnit* pHeadUnit = ::getUnit(pUnitNode->m_data);
				pUnitNode = pPlot->nextUnitNode(pUnitNode);

				// is this unit the head of a group, not cargo, and visible?
				if (pHeadUnit && pHeadUnit->isGroupHead() && !pHeadUnit->isCargo() && !pHeadUnit->isInvisible(GC.getGameINLINE().getActiveTeam(), GC.getGameINLINE().isDebugMode()))
				{
					// head unit name and unitai
					szString.append(CvWString::format(SETCOLR L"%s" ENDCOLR, 255,190,0,255, pHeadUnit->getName().GetCString()));
					szString.append(CvWString::format(L" (%d)", shortenID(pHeadUnit->getID())));
					getUnitAIString(szTempString, pHeadUnit->AI_getUnitAIType());
					szString.append(CvWString::format(SETCOLR L" %s " ENDCOLR, GET_PLAYER(pHeadUnit->getOwnerINLINE()).getPlayerTextColorR(), GET_PLAYER(pHeadUnit->getOwnerINLINE()).getPlayerTextColorG(), GET_PLAYER(pHeadUnit->getOwnerINLINE()).getPlayerTextColorB(), GET_PLAYER(pHeadUnit->getOwnerINLINE()).getPlayerTextColorA(), szTempString.GetCString()));

					// promotion icons
					for (int iPromotionIndex = 0; iPromotionIndex < numPromotionInfos; iPromotionIndex++)
					{
						PromotionTypes ePromotion = (PromotionTypes)iPromotionIndex;
						if (pHeadUnit->isHasPromotion(ePromotion))
						{
							szString.append(CvWString::format(L"<img=%S size=16></img>", GC.getPromotionInfo(ePromotion).getButton()));
						}
					}

					// group
					CvSelectionGroup* pHeadGroup = pHeadUnit->getGroup();
					FAssertMsg(pHeadGroup != NULL, "unit has NULL group");
					if (pHeadGroup->getNumUnits() > 0)
					{
						szString.append(CvWString::format(L"\nGroup:%d [%d units", shortenID(pHeadGroup->getID()), pHeadGroup->getNumUnits()));
						if( pHeadGroup->getCargo() > 0 )
						{
							szString.append(CvWString::format(L" + %d cargo", pHeadGroup->getCargo()));
						}
						szString.append(CvWString::format(L"] (%d power)", pHeadGroup->AI_GroupPower(pHeadGroup->plot(), true)));

						// get average damage
						int iAverageDamage = 0;
						CLLNode<IDInfo>* pUnitNode = pHeadGroup->headUnitNode();
						while (pUnitNode != NULL)
						{
							CvUnit* pLoopUnit = ::getUnit(pUnitNode->m_data);
							pUnitNode = pHeadGroup->nextUnitNode(pUnitNode);

							iAverageDamage += (pLoopUnit->getDamage() * pLoopUnit->maxHitPoints()) / 100;
						}
						iAverageDamage /= pHeadGroup->getNumUnits();
						if (iAverageDamage > 0)
						{
							szString.append(CvWString::format(L" %d%%", 100 - iAverageDamage));
						}
					}
					if (pHeadUnit->isBarbarian() && !pHeadUnit->isAnimal())
					{
						if (pHeadUnit->isGroupHead())
						{
							bool bRagingBarbs = GC.getGameINLINE().isOption(GAMEOPTION_RAGING_BARBARIANS);
							bool bBarbWorld = GC.getGameINLINE().isOption(GAMEOPTION_BARBARIAN_WORLD);
							bool bHero = pHeadUnit->AI_getUnitAIType() == UNITAI_HERO;
							int iCaution = 2;
							iCaution += pHeadUnit->AI_getBirthmark() % 7;
							if (bHero)
							{
								// Barbarian Heros hang back till they level up typically
								iCaution += 6 - pHeadUnit->getLevel();
							}
							// larger stacks more likely to attack civs
							iCaution -= (pHeadUnit->getGroup()->getNumUnits() - 1);
							// more aggressive (attack cities earlier) when raging barbarians is on
							if (bRagingBarbs)
							{
								iCaution -= 2;
							}
							else if (bBarbWorld)
							{
								iCaution -= 1;
							}

							if (!pHeadUnit->isAlive())
							{
								iCaution = 0;
							}

							iCaution = std::max(0, iCaution);
							
							szString.append(CvWString::format(L"Leadership: %d, Caution: %d", pHeadUnit->AI_getBarbLeadership(), iCaution));
						}
					}

					if( pHeadGroup->isStranded() )
					{
						szString.append(CvWString::format(SETCOLR L"\n***STRANDED***" ENDCOLR, TEXT_COLOR("COLOR_RED")));
					}

					/// Ctrl (w/o Alt) = mission/activity info
					if( !gDLL->altKey() )
					{
						// mission ai
						MissionAITypes eMissionAI = pHeadGroup->AI_getMissionAIType();
						if (eMissionAI != NO_MISSIONAI)
						{
							getMissionAIString(szTempString, eMissionAI);
							szString.append(CvWString::format(SETCOLR L"\n%s" ENDCOLR, TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), szTempString.GetCString()));
						}

						// mission
						MissionTypes eMissionType = (MissionTypes) pHeadGroup->getMissionType(0);
						if (eMissionType != NO_MISSION)
						{
							getMissionTypeString(szTempString, eMissionType);
							szString.append(CvWString::format(SETCOLR L"\n%s" ENDCOLR, TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), szTempString.GetCString()));
						}

						// mission unit
						CvUnit* pMissionUnit = pHeadGroup->AI_getMissionAIUnit();
						if (pMissionUnit != NULL && (eMissionAI != NO_MISSIONAI || eMissionType != NO_MISSION))
						{
							// mission unit
							szString.append(L"\n to ");
							szString.append(CvWString::format(SETCOLR L"%s" ENDCOLR, GET_PLAYER(pMissionUnit->getOwnerINLINE()).getPlayerTextColorR(), GET_PLAYER(pMissionUnit->getOwnerINLINE()).getPlayerTextColorG(), GET_PLAYER(pMissionUnit->getOwnerINLINE()).getPlayerTextColorB(), GET_PLAYER(pMissionUnit->getOwnerINLINE()).getPlayerTextColorA(), pMissionUnit->getName().GetCString()));
							szString.append(CvWString::format(L"(%d) G:%d", shortenID(pMissionUnit->getID()), shortenID(pMissionUnit->getGroupID())));
							getUnitAIString(szTempString, pMissionUnit->AI_getUnitAIType());
							szString.append(CvWString::format(SETCOLR L" %s" ENDCOLR, GET_PLAYER(pMissionUnit->getOwnerINLINE()).getPlayerTextColorR(), GET_PLAYER(pMissionUnit->getOwnerINLINE()).getPlayerTextColorG(), GET_PLAYER(pMissionUnit->getOwnerINLINE()).getPlayerTextColorB(), GET_PLAYER(pMissionUnit->getOwnerINLINE()).getPlayerTextColorA(), szTempString.GetCString()));
						}

						// mission plot
						if (eMissionAI != NO_MISSIONAI || eMissionType != NO_MISSION)
						{
							// first try the plot from the missionAI
							CvPlot* pMissionPlot = pHeadGroup->AI_getMissionAIPlot();

							// if MissionAI does not have a plot, get one from the mission itself
							if (pMissionPlot == NULL && eMissionType != NO_MISSION)
							{
								switch (eMissionType)
								{
								case MISSION_MOVE_TO:
								case MISSION_ROUTE_TO:
									pMissionPlot =  GC.getMapINLINE().plotINLINE(pHeadGroup->getMissionData1(0), pHeadGroup->getMissionData2(0));
									break;

								case MISSION_MOVE_TO_UNIT:
									if (pMissionUnit != NULL)
									{
										pMissionPlot = pMissionUnit->plot();
									}
									break;
								}
							}

							if (pMissionPlot != NULL)
							{
								szString.append(CvWString::format(L"\n [%d,%d]", pMissionPlot->getX_INLINE(), pMissionPlot->getY_INLINE()));

								CvCity* pCity = pMissionPlot->getWorkingCity();
								if (pCity != NULL)
								{
									szString.append(L" (");

									if (!pMissionPlot->isCity())
									{
										DirectionTypes eDirection = estimateDirection(dxWrap(pMissionPlot->getX_INLINE() - pCity->plot()->getX_INLINE()), dyWrap(pMissionPlot->getY_INLINE() - pCity->plot()->getY_INLINE()));

										getDirectionTypeString(szTempString, eDirection);
										szString.append(CvWString::format(L"%s of ", szTempString.GetCString()));
									}

									szString.append(CvWString::format(SETCOLR L"%s" ENDCOLR L")", GET_PLAYER(pCity->getOwnerINLINE()).getPlayerTextColorR(), GET_PLAYER(pCity->getOwnerINLINE()).getPlayerTextColorG(), GET_PLAYER(pCity->getOwnerINLINE()).getPlayerTextColorB(), GET_PLAYER(pCity->getOwnerINLINE()).getPlayerTextColorA(), pCity->getName().GetCString()));
								}
								else
								{
									if (pMissionPlot != pPlot)
									{
										DirectionTypes eDirection = estimateDirection(dxWrap(pMissionPlot->getX_INLINE() - pPlot->getX_INLINE()), dyWrap(pMissionPlot->getY_INLINE() - pPlot->getY_INLINE()));

										getDirectionTypeString(szTempString, eDirection);
										szString.append(CvWString::format(L" (%s)", szTempString.GetCString()));
									}

									PlayerTypes eMissionPlotOwner = pMissionPlot->getOwnerINLINE();
									if (eMissionPlotOwner != NO_PLAYER)
									{
										szString.append(CvWString::format(L", " SETCOLR L"%s" ENDCOLR, GET_PLAYER(eMissionPlotOwner).getPlayerTextColorR(), GET_PLAYER(eMissionPlotOwner).getPlayerTextColorG(), GET_PLAYER(eMissionPlotOwner).getPlayerTextColorB(), GET_PLAYER(eMissionPlotOwner).getPlayerTextColorA(), GET_PLAYER(eMissionPlotOwner).getName()));
									}
								}
							}
						}

						// activity
						ActivityTypes eActivityType = (ActivityTypes) pHeadGroup->getActivityType();
						if (eActivityType != NO_ACTIVITY)
						{
							getActivityTypeString(szTempString, eActivityType);
							szString.append(CvWString::format(SETCOLR L"\n%s" ENDCOLR, TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), szTempString.GetCString()));
						}
					}
					/// Ctrl (as long as both others aren't pressed) = Cargo & Group Units
					// ALN
					// if( !gDLL->altKey() && !gDLL->shiftKey() )
					{
						// display cargo for head unit
						std::vector<CvUnit*> aCargoUnits;
						pHeadUnit->getCargoUnits(aCargoUnits);
						for (uint i = 0; i < aCargoUnits.size(); ++i)
						{
							CvUnit* pCargoUnit = aCargoUnits[i];
							if (!pCargoUnit->isInvisible(GC.getGameINLINE().getActiveTeam(), GC.getGameINLINE().isDebugMode()))
							{
								// name and unitai
								szString.append(CvWString::format(SETCOLR L"\n %s" ENDCOLR, TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT"), pCargoUnit->getName().GetCString()));
								// szString.append(CvWString::format(L"(%d)", shortenID(pCargoUnit->getID())));
								getUnitAIString(szTempString, pCargoUnit->AI_getUnitAIType());
								szString.append(CvWString::format(SETCOLR L" %s " ENDCOLR, GET_PLAYER(pCargoUnit->getOwnerINLINE()).getPlayerTextColorR(), GET_PLAYER(pCargoUnit->getOwnerINLINE()).getPlayerTextColorG(), GET_PLAYER(pCargoUnit->getOwnerINLINE()).getPlayerTextColorB(), GET_PLAYER(pCargoUnit->getOwnerINLINE()).getPlayerTextColorA(), szTempString.GetCString()));

								// promotion icons
								for (int iPromotionIndex = 0; iPromotionIndex < numPromotionInfos; iPromotionIndex++)
								{
									PromotionTypes ePromotion = (PromotionTypes)iPromotionIndex;
									if (pCargoUnit->isHasPromotion(ePromotion))
									{
										szString.append(CvWString::format(L"<img=%S size=16></img>", GC.getPromotionInfo(ePromotion).getButton()));
									}
								}
							}
						}

						// display grouped units
						CLLNode<IDInfo>* pUnitNode3 = pPlot->headUnitNode();
						while(pUnitNode3 != NULL)
						{
							CvUnit* pUnit = ::getUnit(pUnitNode3->m_data);
							pUnitNode3 = pPlot->nextUnitNode(pUnitNode3);

							// is this unit not head, in head's group and visible?
							if (pUnit && (pUnit != pHeadUnit) && (pUnit->getGroupID() == pHeadUnit->getGroupID()) && !pUnit->isInvisible(GC.getGameINLINE().getActiveTeam(), GC.getGameINLINE().isDebugMode()))
							{
								FAssertMsg(!pUnit->isCargo(), "unit is cargo but head unit is not cargo");
								// name and unitai
								szString.append(CvWString::format(SETCOLR L"\n-%s" ENDCOLR, TEXT_COLOR("COLOR_UNIT_TEXT"), pUnit->getName().GetCString()));
								// szString.append(CvWString::format(L" (%d)", shortenID(pUnit->getID())));
								getUnitAIString(szTempString, pUnit->AI_getUnitAIType());
								szString.append(CvWString::format(SETCOLR L" %s " ENDCOLR, GET_PLAYER(pUnit->getOwnerINLINE()).getPlayerTextColorR(), GET_PLAYER(pUnit->getOwnerINLINE()).getPlayerTextColorG(), GET_PLAYER(pUnit->getOwnerINLINE()).getPlayerTextColorB(), GET_PLAYER(pUnit->getOwnerINLINE()).getPlayerTextColorA(), szTempString.GetCString()));

								// promotion icons
								for (int iPromotionIndex = 0; iPromotionIndex < numPromotionInfos; iPromotionIndex++)
								{
									PromotionTypes ePromotion = (PromotionTypes)iPromotionIndex;
									if (pUnit->isHasPromotion(ePromotion))
									{
										szString.append(CvWString::format(L"<img=%S size=16></img>", GC.getPromotionInfo(ePromotion).getButton()));
									}
								}

								// display cargo for loop unit
								std::vector<CvUnit*> aLoopCargoUnits;
								pUnit->getCargoUnits(aLoopCargoUnits);
								for (uint i = 0; i < aLoopCargoUnits.size(); ++i)
								{
									CvUnit* pCargoUnit = aLoopCargoUnits[i];
									if (!pCargoUnit->isInvisible(GC.getGameINLINE().getActiveTeam(), GC.getGameINLINE().isDebugMode()))

									{
										// name and unitai
										szString.append(CvWString::format(SETCOLR L"\n %s" ENDCOLR, TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT"), pCargoUnit->getName().GetCString()));
										szString.append(CvWString::format(L"(%d)", shortenID(pCargoUnit->getID())));
										getUnitAIString(szTempString, pCargoUnit->AI_getUnitAIType());
										szString.append(CvWString::format(SETCOLR L" %s " ENDCOLR, GET_PLAYER(pCargoUnit->getOwnerINLINE()).getPlayerTextColorR(), GET_PLAYER(pCargoUnit->getOwnerINLINE()).getPlayerTextColorG(), GET_PLAYER(pCargoUnit->getOwnerINLINE()).getPlayerTextColorB(), GET_PLAYER(pCargoUnit->getOwnerINLINE()).getPlayerTextColorA(), szTempString.GetCString()));
										// promotion icons
										for (int iPromotionIndex = 0; iPromotionIndex < numPromotionInfos; iPromotionIndex++)
										{
											PromotionTypes ePromotion = (PromotionTypes)iPromotionIndex;
											if (pCargoUnit->isHasPromotion(ePromotion))
											{
												szString.append(CvWString::format(L"<img=%S size=16></img>", GC.getPromotionInfo(ePromotion).getButton()));
											}
										}
									}
								}
							}
						}
					}
					
					if( !gDLL->altKey() )
					{
						if( pPlot->getTeam() == NO_TEAM || GET_TEAM(pHeadGroup->getTeam()).isAtWar(pPlot->getTeam()) )
						{
							szString.append(NEWLINE);
							CvWString szTempBuffer;

							//AI strategies
							if (GET_PLAYER(pHeadGroup->getOwner()).AI_isDoStrategy(AI_STRATEGY_DAGGER))
							{
								szTempBuffer.Format(L"Dagger, ");
								szString.append(szTempBuffer);
							}
							if (GET_PLAYER(pHeadGroup->getOwner()).AI_isDoStrategy(AI_STRATEGY_CRUSH))
							{
								szTempBuffer.Format(L"Crush, ");
								szString.append(szTempBuffer);
							}
							if (GET_PLAYER(pHeadGroup->getOwner()).AI_isDoStrategy(AI_STRATEGY_ALERT1))
							{
								szTempBuffer.Format(L"Alert1, ");
								szString.append(szTempBuffer);
							}
							if (GET_PLAYER(pHeadGroup->getOwner()).AI_isDoStrategy(AI_STRATEGY_ALERT2))
							{
								szTempBuffer.Format(L"Alert2, ");
								szString.append(szTempBuffer);
							}
							if (GET_PLAYER(pHeadGroup->getOwner()).AI_isDoStrategy(AI_STRATEGY_TURTLE))
							{
								szTempBuffer.Format(L"Turtle, ");
								szString.append(szTempBuffer);
							}
							if (GET_PLAYER(pHeadGroup->getOwner()).AI_isDoStrategy(AI_STRATEGY_LAST_STAND))
							{
								szTempBuffer.Format(L"Last Stand, ");
								szString.append(szTempBuffer);
							}
							if (GET_PLAYER(pHeadGroup->getOwner()).AI_isDoStrategy(AI_STRATEGY_FINAL_WAR))
							{
								szTempBuffer.Format(L"FinalWar, ");
								szString.append(szTempBuffer);
							}
							if (GET_PLAYER(pHeadGroup->getOwner()).AI_isDoStrategy(AI_STRATEGY_GET_BETTER_UNITS))
							{
								szTempBuffer.Format(L"GetBetterUnits, ");
								szString.append(szTempBuffer);
							}
							if (GET_PLAYER(pHeadGroup->getOwner()).AI_isDoStrategy(AI_STRATEGY_FASTMOVERS))
							{
								szTempBuffer.Format(L"FastMovers, ");
								szString.append(szTempBuffer);
							}
							if (GET_PLAYER(pHeadGroup->getOwner()).AI_isDoStrategy(AI_STRATEGY_LAND_BLITZ))
							{
								szTempBuffer.Format(L"LandBlitz, ");
								szString.append(szTempBuffer);
							}
							if (GET_PLAYER(pHeadGroup->getOwner()).AI_isDoStrategy(AI_STRATEGY_AIR_BLITZ))
							{
								szTempBuffer.Format(L"AirBlitz, ");
								szString.append(szTempBuffer);
							}
 							if (GET_PLAYER(pHeadGroup->getOwner()).AI_isDoStrategy(AI_STRATEGY_OWABWNW))
							{
								szTempBuffer.Format(L"OWABWNW, ");
								szString.append(szTempBuffer);
							}
							if (GET_PLAYER(pHeadGroup->getOwner()).AI_isDoStrategy(AI_STRATEGY_PRODUCTION))
							{
								szTempBuffer.Format(L"Production, ");
								szString.append(szTempBuffer);
							}
							if (GET_PLAYER(pHeadGroup->getOwner()).AI_isDoStrategy(AI_STRATEGY_MISSIONARY))
							{
								szTempBuffer.Format(L"Missionary, ");
								szString.append(szTempBuffer);
							}
							if (GET_PLAYER(pHeadGroup->getOwner()).AI_isDoStrategy(AI_STRATEGY_BIG_ESPIONAGE))
							{
								szTempBuffer.Format(L"BigEspionage, ");
								szString.append(szTempBuffer);
							}
							if (GET_PLAYER(pHeadGroup->getOwner()).AI_isDoStrategy(AI_STRATEGY_ECONOMY_FOCUS)) // K-Mod
							{
								szTempBuffer.Format(L"EconomyFocus, ");
								szString.append(szTempBuffer);
							}

							//Area battle plans.
							if (pPlot->area()->getAreaAIType(pHeadGroup->getTeam()) == AREAAI_OFFENSIVE)
							{
								szTempBuffer.Format(L"\n Area AI = OFFENSIVE");
							}
							else if (pPlot->area()->getAreaAIType(pHeadGroup->getTeam()) == AREAAI_DEFENSIVE)
							{
								szTempBuffer.Format(L"\n Area AI = DEFENSIVE");
							}
							else if (pPlot->area()->getAreaAIType(pHeadGroup->getTeam()) == AREAAI_MASSING)
							{
								szTempBuffer.Format(L"\n Area AI = MASSING");
							}
							else if (pPlot->area()->getAreaAIType(pHeadGroup->getTeam()) == AREAAI_ASSAULT)
							{
								szTempBuffer.Format(L"\n Area AI = ASSAULT");
							}
							else if (pPlot->area()->getAreaAIType(pHeadGroup->getTeam()) == AREAAI_ASSAULT_MASSING)
							{
								szTempBuffer.Format(L"\n Area AI = ASSAULT_MASSING");
							}
							else if (pPlot->area()->getAreaAIType(pHeadGroup->getTeam()) == AREAAI_NEUTRAL)
							{
								szTempBuffer.Format(L"\n Area AI = NEUTRAL");
							}

							CvCity* pTargetCity = pPlot->area()->getTargetCity(pHeadGroup->getOwner());
							if( pTargetCity )
							{
								szString.append(CvWString::format(L"\nTarget City: %s (%d)", pTargetCity->getName().c_str(), pTargetCity->getOwner()));
							}
							else
							{
								szString.append(CvWString::format(L"\nTarget City: None"));
							}
							
							/*
							if( gDLL->shiftKey() )
							{
								CvCity* pLoopCity;
								int iLoop = 0;
								int iBestTargetValue = (pTargetCity != NULL ? GET_PLAYER(pHeadGroup->getOwner()).AI_targetCityValue(pTargetCity,false,true) : 0);
								int iTargetValue = 0;
								szString.append(CvWString::format(L"\n\nTarget City values:\n"));
								for( int iPlayer = 0; iPlayer < MAX_PLAYERS; iPlayer++ )
								{
									if( GET_TEAM(pHeadGroup->getTeam()).AI_getWarPlan(GET_PLAYER((PlayerTypes)iPlayer).getTeam()) != NO_WARPLAN )
									{
										if( pPlot->area()->getCitiesPerPlayer((PlayerTypes)iPlayer) > 0 )
										{
											for (pLoopCity = GET_PLAYER((PlayerTypes)iPlayer).firstCity(&iLoop); pLoopCity != NULL; pLoopCity = GET_PLAYER((PlayerTypes)iPlayer).nextCity(&iLoop))
											{
												if( pLoopCity->area() == pPlot->area() )
												{
													iTargetValue = GET_PLAYER(pHeadGroup->getOwner()).AI_targetCityValue(pLoopCity,false,true);

													if( (GC.getMapINLINE().calculatePathDistance(pPlot, pLoopCity->plot()) < 20))
													{
														szString.append(CvWString::format(L"\n%s : %d + rand %d", pLoopCity->getName().c_str(), iTargetValue, (pLoopCity->getPopulation() / 2)));
													}
												}
											}
										}
									}
								}
							}
							*/
						}
					}
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                       END                                                  */
/************************************************************************************************/

					// double space non-empty groups
					/* if (pHeadGroup->getNumUnits() > 1 || pHeadUnit->hasCargo())
					{
						szString.append(NEWLINE);
					} */

					szString.append(NEWLINE);
				}
			}
		}

		return;
	}

	// lfgr UI 11/2020: Allow cycling through units in plot help
	PlotHelpCyclingManager::getInstance().updateCurrentPlot( GC.getMapINLINE().plotNumINLINE( pPlot->getX_INLINE(), pPlot->getY_INLINE() ) );
	
	CvUnit* pLoopUnit;
	uint iMaxNumUnits = getBugOptionINT( "FfHUI__PlotHelpNumUnits", 15 );
	static std::vector<CvUnit*> apUnits;
	static std::vector<int> aiUnitNumbers;
	static std::vector<int> aiUnitStrength;
	static std::vector<int> aiUnitMaxStrength;
	static std::vector<CvUnit *> plotUnits;

	GC.getGameINLINE().getPlotUnits(pPlot, plotUnits);

	int iNumVisibleUnits = 0;
	if (pPlot->isVisible(GC.getGameINLINE().getActiveTeam(), GC.getGameINLINE().isDebugMode()))
	{
		CLLNode<IDInfo>* pUnitNode5 = pPlot->headUnitNode();
		while(pUnitNode5 != NULL)
		{
			CvUnit* pUnit = ::getUnit(pUnitNode5->m_data);
			pUnitNode5 = pPlot->nextUnitNode(pUnitNode5);

			if (pUnit && !pUnit->isInvisible(GC.getGameINLINE().getActiveTeam(), GC.getGameINLINE().isDebugMode()))
			{
				++iNumVisibleUnits;
			}
		}
	}

	apUnits.erase(apUnits.begin(), apUnits.end());

	if (iNumVisibleUnits > iMaxNumUnits)
	{
		aiUnitNumbers.erase(aiUnitNumbers.begin(), aiUnitNumbers.end());
		aiUnitStrength.erase(aiUnitStrength.begin(), aiUnitStrength.end());
		aiUnitMaxStrength.erase(aiUnitMaxStrength.begin(), aiUnitMaxStrength.end());

		if (m_apbPromotion.size() == 0)
		{
			for (int iI = 0; iI < (GC.getNumUnitInfos() * MAX_PLAYERS); ++iI)
			{
				m_apbPromotion.push_back(new int[numPromotionInfos]);
			}
		}

		for (int iI = 0; iI < (GC.getNumUnitInfos() * MAX_PLAYERS); ++iI)
		{
			aiUnitNumbers.push_back(0);
			aiUnitStrength.push_back(0);
			aiUnitMaxStrength.push_back(0);
			for (int iJ = 0; iJ < numPromotionInfos; iJ++)
			{
				m_apbPromotion[iI][iJ] = 0;
			}
		}
	}

	int iCount = 0;
	for (int iI = iMaxNumUnits; iI < iNumVisibleUnits && iI < (int) plotUnits.size(); ++iI)
	{
		pLoopUnit = plotUnits[iI];

		if (pLoopUnit != NULL && pLoopUnit != pPlot->getCenterUnit())
		{
			apUnits.push_back(pLoopUnit);

			if (iNumVisibleUnits > iMaxNumUnits) // LFGR_TODO: Unnecessary
			{
				int iIndex = pLoopUnit->getUnitType() * MAX_PLAYERS + pLoopUnit->getOwner();
				if (aiUnitNumbers[iIndex] == 0)
				{
					++iCount;
				}
				++aiUnitNumbers[iIndex];

				int iBase = (DOMAIN_AIR == pLoopUnit->getDomainType() ? pLoopUnit->airBaseCombatStr() : pLoopUnit->baseCombatStr());
				if (iBase > 0 && pLoopUnit->maxHitPoints() > 0)
				{
					aiUnitMaxStrength[iIndex] += 100 * iBase;
					aiUnitStrength[iIndex] += (100 * iBase * pLoopUnit->currHitPoints()) / pLoopUnit->maxHitPoints();
				}

				for (int iJ = 0; iJ < numPromotionInfos; iJ++)
				{
					if (pLoopUnit->isHasPromotion((PromotionTypes)iJ))
					{
						++m_apbPromotion[iIndex][iJ];
					}
				}
			}
		}
	}


	if (iNumVisibleUnits > 0)
	{
		if (pPlot->getCenterUnit())
		{
			setUnitHelp(szString, pPlot->getCenterUnit(), iNumVisibleUnits > iMaxNumUnits, true);
		}

		uint iNumShown = std::min<uint>(iMaxNumUnits, iNumVisibleUnits);
		for (uint iI = 0; iI < iNumShown && iI < (int) plotUnits.size(); ++iI)
		{
			CvUnit* pLoopUnit = plotUnits[iI];
			if (pLoopUnit != pPlot->getCenterUnit())
			{
				szString.append(NEWLINE);
				setUnitHelp(szString, pLoopUnit, true, true);
			}
		}

		bool bFirst = true;
		if (iNumVisibleUnits > iMaxNumUnits)
		{
			for (int iI = 0; iI < GC.getNumUnitInfos(); ++iI)
			{
				for (int iJ = 0; iJ < MAX_PLAYERS; iJ++)
				{
					int iIndex = iI * MAX_PLAYERS + iJ;

					if (aiUnitNumbers[iIndex] > 0)
					{
						if (iCount < 5 || bFirst)
						{
							szString.append(NEWLINE);
							bFirst = false;
						}
						else
						{
							szString.append(L", ");
						}
						szString.append(CvWString::format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_UNIT_TEXT"), GC.getUnitInfo((UnitTypes)iI).getDescription()));

						szString.append(CvWString::format(L" (%d)", aiUnitNumbers[iIndex]));

						if (aiUnitMaxStrength[iIndex] > 0)
						{
							int iBase = (aiUnitMaxStrength[iIndex] / aiUnitNumbers[iIndex]) / 100;
							int iCurrent = (aiUnitStrength[iIndex] / aiUnitNumbers[iIndex]) / 100;
							int iCurrent100 = (aiUnitStrength[iIndex] / aiUnitNumbers[iIndex]) % 100;
							if (0 == iCurrent100)
							{
								if (iBase == iCurrent)
								{
									szString.append(CvWString::format(L" %d", iBase));
								}
								else
								{
									szString.append(CvWString::format(L" %d/%d", iCurrent, iBase));
								}
							}
							else
							{
								szString.append(CvWString::format(L" %d.%02d/%d", iCurrent, iCurrent100, iBase));
							}
							szString.append(CvWString::format(L"%c", gDLL->getSymbolID(STRENGTH_CHAR)));
						}


						for (int iK = 0; iK < numPromotionInfos; iK++)
						{
							if (m_apbPromotion[iIndex][iK] > 0)
							{
								szString.append(CvWString::format(L"%d<img=%S size=16></img>", m_apbPromotion[iIndex][iK], GC.getPromotionInfo((PromotionTypes)iK).getButton()));
							}
						}

						if (iJ != GC.getGameINLINE().getActivePlayer() && !GC.getUnitInfo((UnitTypes)iI).isAnimal() && !GC.getUnitInfo((UnitTypes)iI).isHiddenNationality())
						{
							szString.append(L", ");
/************************************************************************************************/
/* REVOLUTION_MOD                         02/01/08                                jdog5000      */
/*                                                                                              */
/* For BarbarianCiv and minor civs                                                              */
/************************************************************************************************/
/* original code
							szString.append(CvWString::format(SETCOLR L"%s" ENDCOLR, GET_PLAYER((PlayerTypes)iJ).getPlayerTextColorR(), GET_PLAYER((PlayerTypes)iJ).getPlayerTextColorG(), GET_PLAYER((PlayerTypes)iJ).getPlayerTextColorB(), GET_PLAYER((PlayerTypes)iJ).getPlayerTextColorA(), GET_PLAYER((PlayerTypes)iJ).getName()));
*/
							// For minor civs, display civ name instead of player name ... to differentiate
							// and help human recognize why they can't contact that player
							if( GET_PLAYER((PlayerTypes)iJ).isMinorCiv() )
								szString.append(CvWString::format(SETCOLR L"%s" ENDCOLR, GET_PLAYER((PlayerTypes)iJ).getPlayerTextColorR(), GET_PLAYER((PlayerTypes)iJ).getPlayerTextColorG(), GET_PLAYER((PlayerTypes)iJ).getPlayerTextColorB(), GET_PLAYER((PlayerTypes)iJ).getPlayerTextColorA(), GET_PLAYER((PlayerTypes)iJ).getCivilizationDescription()));
							else
								szString.append(CvWString::format(SETCOLR L"%s" ENDCOLR, GET_PLAYER((PlayerTypes)iJ).getPlayerTextColorR(), GET_PLAYER((PlayerTypes)iJ).getPlayerTextColorG(), GET_PLAYER((PlayerTypes)iJ).getPlayerTextColorB(), GET_PLAYER((PlayerTypes)iJ).getPlayerTextColorA(), GET_PLAYER((PlayerTypes)iJ).getName()));
/************************************************************************************************/
/* REVOLUTION_MOD                          END                                                  */
/************************************************************************************************/
						}
					}
				}
			}
		}
	}
}


// Returns true if help was given...
bool CvGameTextMgr::setCombatPlotHelp(CvWStringBuffer &szString, CvPlot* pPlot)
{
	PROFILE_FUNC();

/************************************************************************************************/
/* BETTER_BTS_AI_MOD                         05/22/08                             jdog5000      */
/*                                                                                              */
/* DEBUG                                                                                        */
/************************************************************************************************/
	if (gDLL->altKey() && (gDLL->getChtLvl() > 0))
	{
		setPlotHelp( szString, pPlot );
		return true;
	}
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                          END                                               */
/************************************************************************************************/
/*************************************************************************************************/
/** ADVANCED COMBAT ODDS                      3/11/09                           PieceOfMind      */
/** BEGIN                                                                       v2.0             */
/*************************************************************************************************/
/*
Note that due to the large amount of extra content added to this function (setCombatPlotHelp), this should never be used in any function that needs to be called repeatedly (e.g. hundreds of times) quickly.
It is fine for a human player mouse-over (which is what it is used for).
*/
/* New Code */
    bool ACO_enabled = getBugOptionBOOL("ACO__Enabled", true, "ACO_ENABLED");
    bool bShift = gDLL->shiftKey();
	int iView = bShift ? 2 : 1;
    if (getBugOptionBOOL("ACO__SwapViews", false, "ACO_SWAP_VIEWS"))
    {
        iView = 3 - iView; //swaps 1 and 2.
    }
	CvWString szTempBuffer2;
/*************************************************************************************************/
/** ADVANCED COMBAT ODDS                      3/11/09                           PieceOfMind      */
/** END                                                                         v2.0             */
/*************************************************************************************************/

	CvUnit* pAttacker;
	CvUnit* pDefender;
	CvWString szTempBuffer;
	CvWString szOffenseOdds;
	CvWString szDefenseOdds;
	bool bValid;
	int iModifier;

	if (gDLL->getInterfaceIFace()->getLengthSelectionList() == 0)
	{
		return false;
	}

	bValid = false;

//FfH: Added by Kael 12/23/2008
	int iOdds;
	pAttacker = gDLL->getInterfaceIFace()->getSelectionList()->AI_getBestGroupAttacker(pPlot, false, iOdds);
//FfH: End Add

	switch (gDLL->getInterfaceIFace()->getSelectionList()->getDomainType())
	{
	case DOMAIN_SEA:
		bValid = pPlot->isWater();
		break;

	case DOMAIN_AIR:
		bValid = true;
		break;

	case DOMAIN_LAND:
		bValid = !(pPlot->isWater());

//FfH: Added by Kael 12/23/2008
        if (pAttacker != NULL)
        {
            if (pAttacker->canMoveAllTerrain())
            {
                bValid = true;
            }
            if (pAttacker->isBoarding())
            {
                bValid = true;
            }
        }
//FfH: End Add

		break;

	case DOMAIN_IMMOBILE:
		break;

	default:
		FAssert(false);
		break;
	}

	if (!bValid)
	{
		return false;
	}

//FfH: Modified by Kael 12/23/2008 (moved up to earlier in this function)
//	int iOdds;
//	pAttacker = gDLL->getInterfaceIFace()->getSelectionList()->AI_getBestGroupAttacker(pPlot, false, iOdds);
//FfH: End Modify

	if (pAttacker == NULL)
	{
		pAttacker = gDLL->getInterfaceIFace()->getSelectionList()->AI_getBestGroupAttacker(pPlot, false, iOdds, true);
	}

	if (pAttacker != NULL)
	{

//FfH: Modified by Kael 03/29/2009
//		pDefender = pPlot->getBestDefender(NO_PLAYER, pAttacker->getOwnerINLINE(), pAttacker, false, NO_TEAM == pAttacker->getDeclareWarMove(pPlot));
        if (pAttacker->isAlwaysHostile(pPlot))
		{
			pDefender = pPlot->getBestDefender(NO_PLAYER, pAttacker->getOwnerINLINE(), pAttacker);
		}
		else
		{
			pDefender = pPlot->getBestDefender(NO_PLAYER, pAttacker->getOwnerINLINE(), pAttacker, !gDLL->altKey(), NO_TEAM == pAttacker->getDeclareWarMove(pPlot));
		}
//FfH: End Modify

		if (pDefender != NULL && pDefender != pAttacker && pDefender->canDefend(pPlot) && pAttacker->canAttack(*pDefender))
		{
			if (pAttacker->getDomainType() != DOMAIN_AIR)
			{
				int iCombatOdds = getCombatOdds(pAttacker, pDefender);

				if (pAttacker->combatLimit() >= GC.getMAX_HIT_POINTS())
				{
					if (iCombatOdds > 999)
					{
						szTempBuffer = L"&gt; 99.9";
					}
					else if (iCombatOdds < 1)
					{
						szTempBuffer = L"&lt; 0.1";
					}
					else
					{
						szTempBuffer.Format(L"%.1f", ((float)iCombatOdds) / 10.0f);
					}
/*************************************************************************************************/
/** ADVANCED COMBAT ODDS                      3/11/09                           PieceOfMind      */
/** BEGIN                                                                       v2.0             */
/*************************************************************************************************/
/* Old Code */
/*
					szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_ODDS", szTempBuffer.GetCString()));
*/
/* New Code */
					if ((!ACO_enabled) || (getBugOptionBOOL("ACO__ForceOriginalOdds", false, "ACO_FORCE_ORIGINAL_ODDS")))
					{
						szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_ODDS", szTempBuffer.GetCString()));
						szString.append( NEWLINE );
					}
/*************************************************************************************************/
/** ADVANCED COMBAT ODDS                      3/11/09                           PieceOfMind      */
/** END                                                                         v2.0             */
/*************************************************************************************************/
				}


				int iWithdrawal = 0;

				if (pAttacker->combatLimit() < GC.getMAX_HIT_POINTS())
				{
					iWithdrawal += 100 * iCombatOdds;
				}

				iWithdrawal += std::min(100, pAttacker->withdrawalProbability()) * (1000 - iCombatOdds);

				if (iWithdrawal > 0 || pAttacker->combatLimit() < GC.getMAX_HIT_POINTS())
				{
					if (iWithdrawal > 99900)
					{
						szTempBuffer = L"&gt; 99.9";
					}
					else if (iWithdrawal < 100)
					{
						szTempBuffer = L"&lt; 0.1";
					}
					else
					{
						szTempBuffer.Format(L"%.1f", iWithdrawal / 1000.0f);
					}

/*************************************************************************************************/
/** ADVANCED COMBAT ODDS                      3/11/09                           PieceOfMind      */
/** BEGIN                                                                       v2.0             */
/*************************************************************************************************/
/* Old Code */
/*
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_ODDS_RETREAT", szTempBuffer.GetCString()));
*/
/* New Code */
					if ((!ACO_enabled) || (getBugOptionBOOL("ACO__ForceOriginalOdds", false, "ACO_FORCE_ORIGINAL_ODDS")))
					{
						szString.append(NEWLINE);
						szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_ODDS_RETREAT", szTempBuffer.GetCString()));
                        if (ACO_enabled)
                        {
						szString.append(NEWLINE);
					}
                    }
/*************************************************************************************************/
/** ADVANCED COMBAT ODDS                      3/11/09                           PieceOfMind      */
/** END                                                                         v2.0             */
/*************************************************************************************************/
				}

				//szTempBuffer.Format(L"AI odds: %d%%", iOdds);
				//szString += NEWLINE + szTempBuffer;
/*************************************************************************************************/
/** ADVANCED COMBAT ODDS                      3/11/09                           PieceOfMind      */
/** BEGIN                                                                       v2.0             */
/*************************************************************************************************/
/* New Code */
				if (ACO_enabled)
				{

                    BOOL ACO_debug = false;
					//Change this to true when you need to spot errors, particular in the expected hit points calculations
					ACO_debug = getBugOptionBOOL("ACO__Debug", false, "ACO_DEBUG");

                    /** phungus sart **/
//					bool bctrl; bctrl = gDLL->ctrlKey();
//					if (bctrl)
//					{//SWITCHAROO IS DISABLED IN V1.0.  Hopefully it will be available in the next version. At the moment is has issues when modifiers are present.
//						CvUnit* swap = pAttacker;
//						pAttacker = pDefender;
//						pDefender = swap;
//
//						CvPlot* pAttackerPlot = pAttacker->plot();
//		                  CvPlot* pDefenderPlot = pDefender->plot();
//					}
					int iAttackerExperienceModifier = 0;
					int iDefenderExperienceModifier = 0;
					for (int ePromotion = 0; ePromotion < GC.getNumPromotionInfos(); ++ePromotion)
					{
						if (pAttacker->isHasPromotion((PromotionTypes)ePromotion) && GC.getPromotionInfo((PromotionTypes)ePromotion).getExperiencePercent() != 0)
						{
							iAttackerExperienceModifier += GC.getPromotionInfo((PromotionTypes)ePromotion).getExperiencePercent();
						}
					}

					for (int ePromotion = 0; ePromotion < GC.getNumPromotionInfos(); ++ePromotion)
					{
						if (pDefender->isHasPromotion((PromotionTypes)ePromotion) && GC.getPromotionInfo((PromotionTypes)ePromotion).getExperiencePercent() != 0)
						{
							iDefenderExperienceModifier += GC.getPromotionInfo((PromotionTypes)ePromotion).getExperiencePercent();
						}
					}
                    /** phungus end **/ //thanks to phungus420

					// LFGR_TODO: Immunity and resistance

					/** Many thanks to DanF5771 for some of these calculations! **/
					int iAttackerStrength  = pAttacker->currCombatStr(NULL, pDefender);
					int iAttackerFirepower = pAttacker->currFirepower(NULL, pDefender);
					int iDefenderStrength  = pDefender->currCombatStr(pPlot, pAttacker);
					int iDefenderFirepower = pDefender->currFirepower(pPlot, pAttacker);

					FAssert((iAttackerStrength + iDefenderStrength)*(iAttackerFirepower + iDefenderFirepower) > 0);

					int iStrengthFactor    = ((iAttackerFirepower + iDefenderFirepower + 1) / 2);
					int iDamageToAttacker  = std::max(1,((GC.getDefineINT("COMBAT_DAMAGE") * (iDefenderFirepower + iStrengthFactor)) / (iAttackerFirepower + iStrengthFactor)));
					int iDamageToDefender  = std::max(1,((GC.getDefineINT("COMBAT_DAMAGE") * (iAttackerFirepower + iStrengthFactor)) / (iDefenderFirepower + iStrengthFactor)));
					int iFlankAmount       = iDamageToAttacker;

					int iDefenderOdds = ((GC.getDefineINT("COMBAT_DIE_SIDES") * iDefenderStrength) / (iAttackerStrength + iDefenderStrength));
					int iAttackerOdds = GC.getDefineINT("COMBAT_DIE_SIDES") - iDefenderOdds;


                    // Barbarian related code.
                    if (getBugOptionBOOL("ACO__IgnoreBarbFreeWins", false, "ACO_IGNORE_BARB_FREE_WINS"))//Are we not going to ignore barb free wins?  If not, skip this section...
                    {    
                        if (pDefender->isBarbarian())
                        {
                            //defender is barbarian
                            if (!GET_PLAYER(pAttacker->getOwnerINLINE()).isBarbarian() && GET_PLAYER(pAttacker->getOwnerINLINE()).getWinsVsBarbs() < GC.getHandicapInfo(GET_PLAYER(pAttacker->getOwnerINLINE()).getHandicapType()).getFreeWinsVsBarbs())
                            {
                                //attacker is not barb and attacker player has free wins left
                                //I have assumed in the following code only one of the units (attacker and defender) can be a barbarian
                                iDefenderOdds = std::min((10 * GC.getDefineINT("COMBAT_DIE_SIDES")) / 100, iDefenderOdds);
                                iAttackerOdds = std::max((90 * GC.getDefineINT("COMBAT_DIE_SIDES")) / 100, iAttackerOdds);
                                szTempBuffer.Format(SETCOLR L"%d\n" ENDCOLR,
                                                    TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"),GC.getHandicapInfo(GET_PLAYER(pAttacker->getOwnerINLINE()).getHandicapType()).getFreeWinsVsBarbs()-GET_PLAYER(pAttacker->getOwnerINLINE()).getWinsVsBarbs());
                                szString.append(gDLL->getText("TXT_ACO_BarbFreeWinsLeft"));
                                szString.append(szTempBuffer.GetCString());
                            }
                        }
						else
                        {
                            //defender is not barbarian
                            if (pAttacker->isBarbarian())
                            {
                                //attacker is barbarian
                                if (!GET_PLAYER(pDefender->getOwnerINLINE()).isBarbarian() && GET_PLAYER(pDefender->getOwnerINLINE()).getWinsVsBarbs() < GC.getHandicapInfo(GET_PLAYER(pDefender->getOwnerINLINE()).getHandicapType()).getFreeWinsVsBarbs())
                                {
                                    //defender is not barbarian and defender has free wins left and attacker is barbarian
                                    iAttackerOdds = std::min((10 * GC.getDefineINT("COMBAT_DIE_SIDES")) / 100, iAttackerOdds);
                                    iDefenderOdds = std::max((90 * GC.getDefineINT("COMBAT_DIE_SIDES")) / 100, iDefenderOdds);
                                    szTempBuffer.Format(SETCOLR L"%d\n" ENDCOLR,
                                                        TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"),GC.getHandicapInfo(GET_PLAYER(pDefender->getOwnerINLINE()).getHandicapType()).getFreeWinsVsBarbs()-GET_PLAYER(pDefender->getOwnerINLINE()).getWinsVsBarbs());
                                    szString.append(gDLL->getText("TXT_ACO_BarbFreeWinsLeft"));
                                    szString.append(szTempBuffer.GetCString());
                                }
                            }
						}
					}


                    //XP calculations
					int iExperience;
					int iWithdrawXP;//thanks to phungus420
					iWithdrawXP = GC.getDefineINT("EXPERIENCE_FROM_WITHDRAWL");//thanks to phungus420

					if (pAttacker->combatLimit() < 100)
					{
						iExperience        = GC.getDefineINT("EXPERIENCE_FROM_WITHDRAWL");
					}
					else
					{
						iExperience        = (pDefender->attackXPValue() * iDefenderStrength) / iAttackerStrength;
						iExperience        = range(iExperience, GC.getDefineINT("MIN_EXPERIENCE_PER_COMBAT"), GC.getDefineINT("MAX_EXPERIENCE_PER_COMBAT"));
					}

					int iDefExperienceKill;
					if( iDefenderStrength != 0 ) {
						iDefExperienceKill = (pAttacker->defenseXPValue() * iAttackerStrength) / iDefenderStrength;
						iDefExperienceKill = range(iDefExperienceKill, GC.getDefineINT("MIN_EXPERIENCE_PER_COMBAT"), GC.getDefineINT("MAX_EXPERIENCE_PER_COMBAT"));
					}
					else {
						iDefExperienceKill = 0;
					}

					int iBonusAttackerXP = (iExperience * iAttackerExperienceModifier) / 100;
					int iBonusDefenderXP = (iDefExperienceKill * iDefenderExperienceModifier) / 100;
					int iBonusWithdrawXP = (GC.getDefineINT("EXPERIENCE_FROM_WITHDRAWL") * iAttackerExperienceModifier) / 100;


                    //The following code adjusts the XP for barbarian encounters.  In standard game, barb and animal xp cap is 10,5 respectively.
					/**Thanks to phungus420 for the following block of code! **/
					if(pDefender->isBarbarian())
					{
                        if (pDefender->isAnimal())
                        {
                            //animal
							int iMaxExtraAnimalXP = std::max( 0, GC.getDefineINT( "ANIMAL_MAX_XP_VALUE" ) - pAttacker->getExperience() );
							iExperience = range(iExperience,0,iMaxExtraAnimalXP);
							iWithdrawXP = range(iWithdrawXP,0,iMaxExtraAnimalXP);
							iBonusAttackerXP = range(iBonusAttackerXP,0,iMaxExtraAnimalXP + iExperience);
							iBonusWithdrawXP = range(iBonusWithdrawXP,0,iMaxExtraAnimalXP + iWithdrawXP);

                        }
                        else
                        {
                            //normal barbarian
							int iMaxExtraBarbXP = std::max( 0, GC.getDefineINT( "BARBARIAN_MAX_XP_VALUE" ) - pAttacker->getExperience() );
							iExperience = range(iExperience,0,iMaxExtraBarbXP);
							iWithdrawXP = range(iWithdrawXP,0,iMaxExtraBarbXP);
							iBonusAttackerXP = range(iBonusAttackerXP,0,iMaxExtraBarbXP + iExperience);
							iBonusWithdrawXP = range(iBonusWithdrawXP,0,iMaxExtraBarbXP + iWithdrawXP);
                        }
                    }

					int iNeededRoundsAttacker = (pDefender->currHitPoints() - pDefender->maxHitPoints() + pAttacker->combatLimit() - (((pAttacker->combatLimit())==pDefender->maxHitPoints())?1:0))/iDamageToDefender + 1;
					//The extra term introduced here was to account for the incorrect way it treated units that had combatLimits.
					//A catapult that deals 25HP per round, and has a combatLimit of 75HP must deal four successful hits before it kills the warrior -not 3.  This is proved in the way CvUnit::resolvecombat works
					// The old formula (with just a plain -1 instead of a conditional -1 or 0) was incorrectly saying three.

					// int iNeededRoundsDefender = (pAttacker->currHitPoints() + iDamageToAttacker - 1 ) / iDamageToAttacker;  //this is idential to the following line
					int iNeededRoundsDefender = (pAttacker->currHitPoints() - 1)/iDamageToAttacker + 1;

					//szTempBuffer.Format(L"iNeededRoundsAttacker = %d\niNeededRoundsDefender = %d",iNeededRoundsAttacker,iNeededRoundsDefender);
					//szString.append(NEWLINE);szString.append(szTempBuffer.GetCString());
					//szTempBuffer.Format(L"pDefender->currHitPoints = %d\n-pDefender->maxHitPOints = %d\n + pAttacker->combatLimit = %d\n - 1 if\npAttackercomBatlimit equals pDefender->maxHitpoints\n=(%d == %d)\nall over iDamageToDefender = %d\n+1 = ...",
					//pDefender->currHitPoints(),pDefender->maxHitPoints(),pAttacker->combatLimit(),pAttacker->combatLimit(),pDefender->maxHitPoints(),iDamageToDefender);
					//szString.append(NEWLINE);szString.append(szTempBuffer.GetCString());

					int iDefenderHitLimit = pDefender->maxHitPoints() - pAttacker->combatLimit();

					//NOW WE CALCULATE SOME INTERESTING STUFF :)

					float E_HP_Att = 0.0f;//expected damage dealt to attacker
					float E_HP_Def = 0.0f;
                    float E_HP_Att_Withdraw; //Expected hitpoints for attacker if attacker withdraws (not the same as retreat)
                    float E_HP_Att_Victory; //Expected hitpoints for attacker if attacker kills defender
					int E_HP_Att_Retreat = (pAttacker->currHitPoints()) - (iNeededRoundsDefender-1)*iDamageToAttacker;//this one is predetermined easily
					float E_HP_Def_Withdraw;
					float E_HP_Def_Defeat; // if attacker dies
					//Note E_HP_Def is the same for if the attacker withdraws or dies

					float AttackerUnharmed;
					float DefenderUnharmed;

					AttackerUnharmed = getCombatOddsSpecific(pAttacker,pDefender,0,iNeededRoundsAttacker);
					DefenderUnharmed = getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender,0);
					DefenderUnharmed += getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender-1,0);//attacker withdraws or retreats

					float prob_bottom_Att_HP; // The probability the attacker exits combat with min HP
					float prob_bottom_Def_HP; // The probability the defender exits combat with min HP

                    if (ACO_debug)
                    {
                        szTempBuffer.Format(L"E[HP ATTACKER]");
                        //szString.append(NEWLINE);
                        szString.append(szTempBuffer.GetCString());
                    }
                    // already covers both possibility of defender not being killed AND being killed
                    for (int n_A = 0; n_A < iNeededRoundsDefender; n_A++)
                    {
                        //prob_attack[n_A] = getCombatOddsSpecific(pAttacker,pDefender,n_A,iNeededRoundsAttacker);
                        E_HP_Att += ( (pAttacker->currHitPoints()) - n_A*iDamageToAttacker) * getCombatOddsSpecific(pAttacker,pDefender,n_A,iNeededRoundsAttacker);

                        if (ACO_debug)
                        {
                            szTempBuffer.Format(L"+%d * %.2f%%  (Def %d) (%d:%d)",
                                                ((pAttacker->currHitPoints()) - n_A*iDamageToAttacker),100.0f*getCombatOddsSpecific(pAttacker,pDefender,n_A,iNeededRoundsAttacker),iDefenderHitLimit,n_A,iNeededRoundsAttacker);
                            szString.append(NEWLINE);
                            szString.append(szTempBuffer.GetCString());
                        }
                    }
					E_HP_Att_Victory = E_HP_Att;//NOT YET NORMALISED
					E_HP_Att_Withdraw = E_HP_Att;//NOT YET NORMALIZED
					prob_bottom_Att_HP = getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender-1,iNeededRoundsAttacker);
					if((pAttacker->withdrawalProbability()) > 0)
                    {
                        // if withdraw odds involved
                        if (ACO_debug)
                        {
                            szTempBuffer.Format(L"Attacker retreat odds");
                            szString.append(NEWLINE);
                            szString.append(szTempBuffer.GetCString());
                        }
                        for (int n_D = 0; n_D < iNeededRoundsAttacker; n_D++)
                        {
                            E_HP_Att += ( (pAttacker->currHitPoints()) - (iNeededRoundsDefender-1)*iDamageToAttacker) * getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender-1,n_D);
                            prob_bottom_Att_HP += getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender-1,n_D);
                            if (ACO_debug)
                            {
                                szTempBuffer.Format(L"+%d * %.2f%%  (Def %d) (%d:%d)",
                                                    ( (pAttacker->currHitPoints()) - (iNeededRoundsDefender-1)*iDamageToAttacker),100.0f*getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender-1,n_D),(pDefender->currHitPoints())-n_D*iDamageToDefender,iNeededRoundsDefender-1,n_D);
                                szString.append(NEWLINE);
                                szString.append(szTempBuffer.GetCString());
                            }
                        }
                    }
                    // finished with the attacker HP I think.

                    if (ACO_debug)
                    {
                        szTempBuffer.Format(L"E[HP DEFENDER]\nOdds that attacker dies or retreats");
                        szString.append(NEWLINE);
                        szString.append(szTempBuffer.GetCString());
                    }
                    for (int n_D = 0; n_D < iNeededRoundsAttacker; n_D++)
                    {
                        //prob_defend[n_D] = getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender,n_D);//attacker dies
                        //prob_defend[n_D] += getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender-1,n_D);//attacker retreats
                        E_HP_Def += ( (pDefender->currHitPoints()) - n_D*iDamageToDefender) * (getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender,n_D)+getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender-1,n_D));
                        if (ACO_debug)
                        {
                            szTempBuffer.Format(L"+%d * %.2f%%  (Att 0 or %d) (%d:%d)",
                                                ( (pDefender->currHitPoints()) - n_D*iDamageToDefender),100.0f*(getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender,n_D)+getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender-1,n_D)),(pAttacker->currHitPoints())-(iNeededRoundsDefender-1)*iDamageToAttacker,iNeededRoundsDefender,n_D);
                            szString.append(NEWLINE);
                            szString.append(szTempBuffer.GetCString());
                        }
                    }
                    prob_bottom_Def_HP = getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender,iNeededRoundsAttacker-1);
                    //prob_bottom_Def_HP += getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender-1,iNeededRoundsAttacker-1);
                    E_HP_Def_Defeat = E_HP_Def;
                    E_HP_Def_Withdraw = 0.0f;

                    if (pAttacker->combatLimit() < (pDefender->maxHitPoints() ))//if attacker has a combatLimit (eg. catapult)
                    {
                        if (pAttacker->combatLimit() == iDamageToDefender*(iNeededRoundsAttacker-1) )
                        {
                            //Then we have an odd situation because the last successful hit by an attacker will do 0 damage, and doing either iNeededRoundsAttacker or iNeededRoundsAttacker-1 will cause the same damage
                            if (ACO_debug)
                            {
                                szTempBuffer.Format(L"Odds that attacker withdraws at combatLimit (abnormal)");
                                szString.append(NEWLINE);
                                szString.append(szTempBuffer.GetCString());
                            }
                            for (int n_A = 0; n_A < iNeededRoundsDefender; n_A++)
                            {
                                //prob_defend[iNeededRoundsAttacker-1] += getCombatOddsSpecific(pAttacker,pDefender,n_A,iNeededRoundsAttacker);//this is the defender at the combatLimit
                                E_HP_Def += (float)iDefenderHitLimit * getCombatOddsSpecific(pAttacker,pDefender,n_A,iNeededRoundsAttacker);
                                //should be the same as
                                //E_HP_Def += ( (pDefender->currHitPoints()) - (iNeededRoundsAttacker-1)*iDamageToDefender) * getCombatOddsSpecific(pAttacker,pDefender,n_A,iNeededRoundsAttacker);
                                E_HP_Def_Withdraw += (float)iDefenderHitLimit * getCombatOddsSpecific(pAttacker,pDefender,n_A,iNeededRoundsAttacker);
                                prob_bottom_Def_HP += getCombatOddsSpecific(pAttacker,pDefender,n_A,iNeededRoundsAttacker);
                                if (ACO_debug)
                                {
                                    szTempBuffer.Format(L"+%d * %.2f%%  (Att %d) (%d:%d)",
                                                        iDefenderHitLimit,100.0f*getCombatOddsSpecific(pAttacker,pDefender,n_A,iNeededRoundsAttacker),100-n_A*iDamageToAttacker,n_A,iNeededRoundsAttacker);
                                    szString.append(NEWLINE);
                                    szString.append(szTempBuffer.GetCString());
                                }
                            }
                        }
                        else // normal situation
                        {
                            if (ACO_debug)
                            {
                                szTempBuffer.Format(L"Odds that attacker withdraws at combatLimit (normal)",pAttacker->combatLimit());
                                szString.append(NEWLINE);
                                szString.append(szTempBuffer.GetCString());
                            }

                            for (int n_A = 0; n_A < iNeededRoundsDefender; n_A++)
                            {

                                E_HP_Def += (float)iDefenderHitLimit * getCombatOddsSpecific(pAttacker,pDefender,n_A,iNeededRoundsAttacker);
                                E_HP_Def_Withdraw += (float)iDefenderHitLimit * getCombatOddsSpecific(pAttacker,pDefender,n_A,iNeededRoundsAttacker);
                                prob_bottom_Def_HP += getCombatOddsSpecific(pAttacker,pDefender,n_A,iNeededRoundsAttacker);
                                if (ACO_debug)
                                {
                                    szTempBuffer.Format(L"+%d * %.2f%%  (Att %d) (%d:%d)",
                                                        iDefenderHitLimit,100.0f*getCombatOddsSpecific(pAttacker,pDefender,n_A,iNeededRoundsAttacker),GC.getMAX_HIT_POINTS()-n_A*iDamageToAttacker,n_A,iNeededRoundsAttacker);
                                    szString.append(NEWLINE);
                                    szString.append(szTempBuffer.GetCString());
                                }
                            }//for
                        }//else
                    }
                    if (ACO_debug)
                    {
                        szString.append(NEWLINE);
                    }

                    float Scaling_Factor = 1.6f;//how many pixels per 1% of odds

                    float AttackerKillOdds = 0.0f;
                    float PullOutOdds = 0.0f;//Withdraw odds
                    float RetreatOdds = 0.0f;
                    float DefenderKillOdds = 0.0f;

                    float CombatRatio = ((float)(pAttacker->currCombatStr(NULL, pDefender))) / ((float)(pDefender->currCombatStr(pPlot, pAttacker)));
                    // THE ALL-IMPORTANT COMBATRATIO

                    float AttXP = (pDefender->attackXPValue())/CombatRatio;
                    float DefXP = (pAttacker->defenseXPValue())*CombatRatio;// These two values are simply for the Unrounded XP display

                    // General odds
                    if (pAttacker->combatLimit() == (pDefender->maxHitPoints() )) //ie. we can kill the defender... I hope this is the most general form
                    {
                        //float AttackerKillOdds = 0.0f;
                        for (int n_A = 0; n_A < iNeededRoundsDefender; n_A++)
                        {
                            AttackerKillOdds += getCombatOddsSpecific(pAttacker,pDefender,n_A,iNeededRoundsAttacker);
                        }//for
                    }
                    else
                    {
                        // else we cannot kill the defender (eg. catapults attacking)
                        for (int n_A = 0; n_A < iNeededRoundsDefender; n_A++)
                        {
                            PullOutOdds += getCombatOddsSpecific(pAttacker,pDefender,n_A,iNeededRoundsAttacker);
                        }//for
                    }
                    if ((pAttacker->withdrawalProbability()) > 0)
                    {
                        for (int n_D = 0; n_D < iNeededRoundsAttacker; n_D++)
                        {
                            RetreatOdds += getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender-1,n_D);
                        }//for
                    }
                    for (int n_D = 0; n_D < iNeededRoundsAttacker; n_D++)
                    {
                        DefenderKillOdds += getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender,n_D);
                    }//for
                    //DefenderKillOdds = 1.0f - (AttackerKillOdds + RetreatOdds + PullOutOdds);//this gives slight negative numbers sometimes, I think

					szString.append(gDLL->getText("TXT_KEY_BUG_ACO__HEADER", pAttacker->getName().GetCString(), pDefender->getName().GetCString()));
					szString.append(NEWLINE);
					
                    if (iView & getBugOptionINT("ACO__ShowSurvivalOdds", 3, "ACO_SHOW_SURVIVAL_ODDS"))
                    {
                        szTempBuffer.Format(L"%.2f%%",100.0f*(AttackerKillOdds+RetreatOdds+PullOutOdds));
                        szTempBuffer2.Format(L"%.2f%%", 100.0f*(RetreatOdds+PullOutOdds+DefenderKillOdds));
                        szString.append(gDLL->getText("TXT_ACO_SurvivalOdds"));
                        szString.append(gDLL->getText("TXT_ACO_VS", szTempBuffer.GetCString(), szTempBuffer2.GetCString()));
                        szString.append(NEWLINE);
                    }

                    if (pAttacker->withdrawalProbability()>=100)
                    {
                        // a rare situation indeed

                        szString.append(NEWLINE);
                        szString.append(gDLL->getText("TXT_ACO_SurvivalGuaranteed"));
                    }

                    //CvWString szTempBuffer2; // moved to elsewhere in the code (earlier)
                    //CvWString szBuffer; // duplicate

                    float prob1 = 100.0f*(AttackerKillOdds + PullOutOdds);//up to win odds
                    float prob2 = prob1 + 100.0f*RetreatOdds;//up to retreat odds

                    float prob = 100.0f*(AttackerKillOdds+RetreatOdds+PullOutOdds);
                    int pixels_left = 199;// 1 less than 200 to account for right end bar
                    int pixels;
                    int fullBlocks;
                    int lastBlock;

                    pixels = (2 * ((int)(prob1 + 0.5)))-1;  // 1% per pixel // subtracting one to account for left end bar
                    fullBlocks = pixels / 10;
                    lastBlock = pixels % 10;

                    szString.append(L"<img=Art/ACO/green_bar_left_end.dds>");
                    for (int i = 0; i < fullBlocks; ++i)
                    {
                        szString.append(L"<img=Art/ACO/green_bar_10.dds>");
                        pixels_left -= 10;
                    }
                    if (lastBlock > 0)
                    {
                        szTempBuffer2.Format(L"<img=Art/ACO/green_bar_%d.dds>", lastBlock);
                        szString.append(szTempBuffer2);
                        pixels_left-= lastBlock;
                    }


                    pixels = 2 * ((int)(prob2 + 0.5)) - (pixels+1);//the number up to the next one...
                    fullBlocks = pixels / 10;
                    lastBlock = pixels % 10;
                    for (int i = 0; i < fullBlocks; ++i)
                    {
                        szString.append(L"<img=Art/ACO/yellow_bar_10.dds>");
                        pixels_left -= 10;
                    }
                    if (lastBlock > 0)
                    {
                        szTempBuffer2.Format(L"<img=Art/ACO/yellow_bar_%d.dds>", lastBlock);
                        szString.append(szTempBuffer2);
                        pixels_left-= lastBlock;
                    }

                    fullBlocks = pixels_left / 10;
                    lastBlock = pixels_left % 10;
                    for (int i = 0; i < fullBlocks; ++i)
                    {
                        szString.append(L"<img=Art/ACO/red_bar_10.dds>");
                    }
                    if (lastBlock > 0)
                    {
                        szTempBuffer2.Format(L"<img=Art/ACO/red_bar_%d.dds>", lastBlock);
                        szString.append(szTempBuffer2);
                    }

                    szString.append(L"<img=Art/ACO/red_bar_right_end.dds> ");


                    szString.append(NEWLINE);
                    if (pAttacker->combatLimit() == (pDefender->maxHitPoints() ))
                    {
                        szTempBuffer.Format(L": " SETCOLR L"%.2f%% " L"%d" ENDCOLR,
                                            TEXT_COLOR("COLOR_POSITIVE_TEXT"),100.0f*AttackerKillOdds,iExperience);
                        szString.append(gDLL->getText("TXT_ACO_Victory"));
                        szString.append(szTempBuffer.GetCString());
                        if (iAttackerExperienceModifier > 0)
                        {
                            szTempBuffer.Format(SETCOLR L"+%d" ENDCOLR,TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"),iBonusAttackerXP);
                            szString.append(szTempBuffer.GetCString());
                        }

                        szString.append(gDLL->getText("TXT_KEY_COLOR_POSITIVE"));
                        szString.append(gDLL->getText("TXT_ACO_XP"));
                        szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                        szString.append("  (");
                        szString.append(gDLL->getText("TXT_KEY_COLOR_POSITIVE"));
                        szTempBuffer.Format(L"%.1f",
                                            E_HP_Att_Victory/AttackerKillOdds);
                        szString.append(szTempBuffer.GetCString());
                        szString.append(gDLL->getText("TXT_ACO_HP"));
                        szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                    }
                    else
                    {
                        szTempBuffer.Format(L": " SETCOLR L"%.2f%% " L"%d" ENDCOLR,
                                            TEXT_COLOR("COLOR_POSITIVE_TEXT"),100.0f*PullOutOdds,GC.getDefineINT("EXPERIENCE_FROM_WITHDRAWL"));
                        //iExperience,TEXT_COLOR("COLOR_POSITIVE_TEXT"), E_HP_Att_Victory/AttackerKillOdds);
                        szString.append(gDLL->getText("TXT_ACO_Withdraw"));
                        szString.append(szTempBuffer.GetCString());
                        if (iAttackerExperienceModifier > 0)
                        {
                            szTempBuffer.Format(SETCOLR L"+%d" ENDCOLR,TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"),iBonusWithdrawXP);
                            szString.append(szTempBuffer.GetCString());
                        }

                        szString.append(gDLL->getText("TXT_KEY_COLOR_POSITIVE"));
                        szString.append(gDLL->getText("TXT_ACO_XP"));
                        szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                        szString.append("  (");
                        szString.append(gDLL->getText("TXT_KEY_COLOR_POSITIVE"));
                        szTempBuffer.Format(L"%.1f",E_HP_Att_Withdraw/PullOutOdds);
                        szString.append(szTempBuffer.GetCString());
                        szString.append(gDLL->getText("TXT_ACO_HP"));
                        szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                        szString.append(",");
                        szString.append(gDLL->getText("TXT_KEY_COLOR_NEGATIVE"));
                        szTempBuffer.Format(L"%d",iDefenderHitLimit);
                        szString.append(szTempBuffer.GetCString());
                        szString.append(gDLL->getText("TXT_ACO_HP"));
                        szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                    }
                    szString.append(")");

                    if (iDefenderOdds == 0)
                    {
                        szString.append(gDLL->getText("TXT_ACO_GuaranteedNoDefenderHit"));
                        DefenderKillOdds = 0.0f;
                    }

                    if ((pAttacker->withdrawalProbability()) > 0)//if there are retreat odds
                    {
                        szString.append(NEWLINE);
                        szTempBuffer.Format(L": " SETCOLR L"%.2f%% " ENDCOLR SETCOLR L"%d" ENDCOLR,
                                            TEXT_COLOR("COLOR_UNIT_TEXT"),100.0f*RetreatOdds,TEXT_COLOR("COLOR_POSITIVE_TEXT"),GC.getDefineINT("EXPERIENCE_FROM_WITHDRAWL"));
                        szString.append(gDLL->getText("TXT_ACO_Retreat"));
                        szString.append(szTempBuffer.GetCString());
                        if (iAttackerExperienceModifier > 0)
                        {
                            szTempBuffer.Format(SETCOLR L"+%d" ENDCOLR,TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"),iBonusWithdrawXP);
                            szString.append(szTempBuffer.GetCString());
                        }
                        szString.append(gDLL->getText("TXT_KEY_COLOR_POSITIVE"));
                        szString.append(gDLL->getText("TXT_ACO_XP"));
                        szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                        szString.append("  (");
                        szTempBuffer.Format(SETCOLR L"%d" ENDCOLR ,
                                            TEXT_COLOR("COLOR_UNIT_TEXT"),E_HP_Att_Retreat);
                        szString.append(szTempBuffer.GetCString());
                        szString.append(gDLL->getText("TXT_ACO_HP_NEUTRAL"));
                        szString.append(")");
                        //szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                    }

                    szString.append(NEWLINE);
                    szTempBuffer.Format(L": " SETCOLR L"%.2f%% " L"%d" ENDCOLR,
                                        TEXT_COLOR("COLOR_NEGATIVE_TEXT"),100.0f*DefenderKillOdds,iDefExperienceKill);
                    szString.append(gDLL->getText("TXT_ACO_Defeat"));
                    szString.append(szTempBuffer.GetCString());
                    if (iDefenderExperienceModifier > 0)
                    {
                        szTempBuffer.Format(SETCOLR L"+%d" ENDCOLR,TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"),iBonusDefenderXP);
                        szString.append(szTempBuffer.GetCString());
                    }
                    szString.append(gDLL->getText("TXT_KEY_COLOR_NEGATIVE"));
                    szString.append(gDLL->getText("TXT_ACO_XP"));
                    szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                    szString.append("  (");
                    szString.append(gDLL->getText("TXT_KEY_COLOR_NEGATIVE"));
                    szTempBuffer.Format(L"%.1f",
                                        (iDefenderOdds != 0 ? E_HP_Def_Defeat/(RetreatOdds+DefenderKillOdds):0.0));
                    szString.append(szTempBuffer.GetCString());
                    szString.append(gDLL->getText("TXT_ACO_HP"));
                    szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                    szString.append(")");


                    float HP_percent_cutoff = 0.5f; // Probabilities lower than this (in percent) will not be shown individually for the HP detail section.
                    if (!getBugOptionBOOL("ACO__MergeShortBars", true, "ACO_MERGE_SHORT_BARS"))
                    {
                        HP_percent_cutoff = 0.0f;
                    }
                    int first_combined_HP_Att = 0;
                    int first_combined_HP_Def = 0;
                    int last_combined_HP;
                    float combined_HP_sum = 0.0f;
                    BOOL bIsCondensed = false;



                    //START ATTACKER DETAIL HP HERE
                    // Individual bars for each attacker HP outcome.
                    if (iView & getBugOptionINT("ACO__ShowAttackerHealthBars", 2, "ACO_SHOW_ATTACKER_HEALTH_BARS"))
                    {
                        for (int n_A = 0; n_A < iNeededRoundsDefender-1; n_A++)
                        {
                            float prob = 100.0f*getCombatOddsSpecific(pAttacker,pDefender,n_A,iNeededRoundsAttacker);
                            if (prob > HP_percent_cutoff || n_A==0)
                            {
                                if (bIsCondensed) // then we need to print the prev ones
                                {
                                    int pixels = (int)(Scaling_Factor*combined_HP_sum + 0.5);  // 1% per pixel
                                    int fullBlocks = (pixels) / 10;
                                    int lastBlock = (pixels) % 10;
                                    //if(pixels>=2) {szString.append(L"<img=Art/ACO/green_bar_left_end.dds>");}
                                    szString.append(NEWLINE);
                                    szString.append(L"<img=Art/ACO/green_bar_left_end.dds>");
                                    for (int iI = 0; iI < fullBlocks; ++iI)
                                    {
                                        szString.append(L"<img=Art/ACO/green_bar_10.dds>");
                                    }
                                    if (lastBlock > 0)
                                    {
                                        szTempBuffer2.Format(L"<img=Art/ACO/green_bar_%d.dds>", lastBlock);
                                        szString.append(szTempBuffer2);
                                    }
                                    szString.append(L"<img=Art/ACO/green_bar_right_end.dds>");
                                    szString.append(L" ");

                                    szString.append(gDLL->getText("TXT_KEY_COLOR_POSITIVE"));
                                    if (last_combined_HP!=first_combined_HP_Att)
                                    {
                                        szTempBuffer.Format(L"%d",last_combined_HP);
                                        szString.append(szTempBuffer.GetCString());
                                        szString.append(gDLL->getText("TXT_ACO_HP"));
                                        szString.append(gDLL->getText("-"));
                                    }

                                    szTempBuffer.Format(L"%d",first_combined_HP_Att);
                                    szString.append(szTempBuffer.GetCString());
                                    szString.append(gDLL->getText("TXT_ACO_HP"));
                                    szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                                    szTempBuffer.Format(L" %.2f%%",combined_HP_sum);
                                    szString.append(szTempBuffer.GetCString());

                                    bIsCondensed = false;//resetting
                                    combined_HP_sum = 0.0f;//resetting this variable
                                    last_combined_HP = 0;
                                }

                                szString.append(NEWLINE);
                                int pixels = (int)(Scaling_Factor*prob + 0.5);  // 1% per pixel
                                int fullBlocks = (pixels) / 10;
                                int lastBlock = (pixels) % 10;
                                szString.append(L"<img=Art/ACO/green_bar_left_end.dds>");
                                for (int iI = 0; iI < fullBlocks; ++iI)
                                {
                                    szString.append(L"<img=Art/ACO/green_bar_10.dds>");
                                }
                                if (lastBlock > 0)
                                {
                                    szTempBuffer2.Format(L"<img=Art/ACO/green_bar_%d.dds>", lastBlock);
                                    szString.append(szTempBuffer2);
                                }
                                szString.append(L"<img=Art/ACO/green_bar_right_end.dds>");
                                szString.append(L" ");

                                szString.append(gDLL->getText("TXT_KEY_COLOR_POSITIVE"));
                                szTempBuffer.Format(L"%d",
                                                    ((pAttacker->currHitPoints()) - n_A*iDamageToAttacker));
                                szString.append(szTempBuffer.GetCString());
                                szString.append(gDLL->getText("TXT_ACO_HP"));
                                szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                                szTempBuffer.Format(L" %.2f%%",
                                                    prob);
                                szString.append(szTempBuffer.GetCString());
                            }
                            else // we add to the condensed list
                            {
                                bIsCondensed = true;
                                first_combined_HP_Att = std::max(first_combined_HP_Att,((pAttacker->currHitPoints()) - n_A*iDamageToAttacker));
                                last_combined_HP = ((pAttacker->currHitPoints()) - n_A*iDamageToAttacker);
                                combined_HP_sum += prob;
                            }
                        }

                        if (bIsCondensed) // then we need to print the prev ones
                        {
                            szString.append(NEWLINE);
                            int pixels = (int)(Scaling_Factor*combined_HP_sum + 0.5);  // 1% per pixel
                            int fullBlocks = (pixels) / 10;
                            int lastBlock = (pixels) % 10;

                            szString.append(L"<img=Art/ACO/green_bar_left_end.dds>");
                            for (int iI = 0; iI < fullBlocks; ++iI)
                            {
                                szString.append(L"<img=Art/ACO/green_bar_10.dds>");
                            }
                            if (lastBlock > 0)
                            {
                                szTempBuffer2.Format(L"<img=Art/ACO/green_bar_%d.dds>", lastBlock);
                                szString.append(szTempBuffer2);
                            }

                            szString.append(L"<img=Art/ACO/green_bar_right_end.dds>");
                            szString.append(L" ");

                            szString.append(gDLL->getText("TXT_KEY_COLOR_POSITIVE"));
                            if (last_combined_HP!=first_combined_HP_Att)
                            {
                                szTempBuffer.Format(L"%d",last_combined_HP);
                                szString.append(szTempBuffer.GetCString());
                                szString.append(gDLL->getText("TXT_ACO_HP"));
                                szString.append(gDLL->getText("-"));
                            }
                            szTempBuffer.Format(L"%d",first_combined_HP_Att);
                            szString.append(szTempBuffer.GetCString());
                            szString.append(gDLL->getText("TXT_ACO_HP"));
                            szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                            szTempBuffer.Format(L" %.2f%%",combined_HP_sum);
                            szString.append(szTempBuffer.GetCString());

                            bIsCondensed = false;//resetting
                            combined_HP_sum = 0.0f;//resetting this variable
                            last_combined_HP = 0;
                        }
                        // At the moment I am not allowing the lowest Attacker HP value to be condensed, as it would be confusing if it includes retreat odds
                        // I may include this in the future though, but probably only if retreat odds are zero.

                        float prob_victory = 100.0f*getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender-1,iNeededRoundsAttacker);
                        float prob_retreat = 100.0f*RetreatOdds;

                        szString.append(NEWLINE);
                        int green_pixels = (int)(Scaling_Factor*prob_victory + 0.5);
                        int yellow_pixels = (int)(Scaling_Factor*(prob_retreat+prob_victory) + 0.5) - green_pixels;//makes the total length of the bar more accurate - more important than the length of the pieces
                        green_pixels+=1;//we put an extra 2 on every one of the bar pixel counts
                        if (yellow_pixels>=1)
                        {
                            yellow_pixels+=1;
                        }
                        else
                        {
                            green_pixels+=1;
                        }
                        szString.append(L"<img=Art/ACO/green_bar_left_end.dds>");
                        green_pixels--;

                        green_pixels--;//subtracting off the right end
                        int fullBlocks = green_pixels / 10;
                        int lastBlock = green_pixels % 10;
                        for (int iI = 0; iI < fullBlocks; ++iI)
                        {
                            szString.append(L"<img=Art/ACO/green_bar_10.dds>");
                        }//for
                        if (lastBlock > 0)
                        {
                            szTempBuffer2.Format(L"<img=Art/ACO/green_bar_%d.dds>", lastBlock);
                            szString.append(szTempBuffer2);
                        }//if
                        if (yellow_pixels>=1)// then there will at least be a right end yellow pixel
                        {
                            yellow_pixels--;//subtracting off right end
                            fullBlocks = yellow_pixels / 10;
                            lastBlock = yellow_pixels % 10;
                            for (int iI = 0; iI < fullBlocks; ++iI)
                            {
                                szString.append(L"<img=Art/ACO/yellow_bar_10.dds>");
                            }//for
                            if (lastBlock > 0)
                            {
                                szTempBuffer2.Format(L"<img=Art/ACO/yellow_bar_%d.dds>", lastBlock);
                                szString.append(szTempBuffer2);
                            }
                            szString.append(L"<img=Art/ACO/yellow_bar_right_end.dds>");
                            //finished
                        }
                        else
                        {
                            szString.append(L"<img=Art/ACO/green_bar_right_end.dds>");
                            //finished
                        }//else if

                        szString.append(L" ");
                        szString.append(gDLL->getText("TXT_KEY_COLOR_POSITIVE"));
                        szTempBuffer.Format(L"%d",((pAttacker->currHitPoints()) - (iNeededRoundsDefender-1)*iDamageToAttacker));
                        szString.append(szTempBuffer.GetCString());
                        szString.append(gDLL->getText("TXT_ACO_HP"));
                        szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                        szTempBuffer.Format(L" %.2f%%",prob_victory+prob_retreat);
                        szString.append(szTempBuffer.GetCString());
                    }
                    //END ATTACKER DETAIL HP HERE



                    //START DEFENDER DETAIL HP HERE
                    first_combined_HP_Def = pDefender->currHitPoints();
                    if (iView & getBugOptionINT("ACO__ShowDefenderHealthBars", 2, "ACO_SHOW_DEFENDER_HEALTH_BARS"))
                    {
                        float prob = 0.0f;
                        int def_HP;
                        for (int n_D = iNeededRoundsAttacker; n_D >= 1; n_D--)//
                        {
                            if (pAttacker->combatLimit() >= pDefender->maxHitPoints())// a unit with a combat limit
                            {
                                if (n_D == iNeededRoundsAttacker)
                                {
                                    n_D--;//we don't need to do HP for when the unit is dead.
                                }
                            }

                            def_HP = std::max((pDefender->currHitPoints()) - n_D*iDamageToDefender,(pDefender->maxHitPoints()  - pAttacker->combatLimit()));

                            if ( (pDefender->maxHitPoints() - pAttacker->combatLimit() ) == pDefender->currHitPoints() - (n_D-1)*iDamageToDefender)
                            {
                                // if abnormal
                                if (n_D == iNeededRoundsAttacker)
                                {
                                    n_D--;
                                    def_HP = (pDefender->maxHitPoints()  - pAttacker->combatLimit());
                                    prob += 100.0f*PullOutOdds;
                                    prob += 100.0f*(getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender,n_D)+(getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender-1,n_D)));
                                }
                            }
                            else
                            {
                                //not abnormal
                                if (n_D == iNeededRoundsAttacker)
                                {
                                    prob += 100.0f*PullOutOdds;
                                }
                                else
                                {
                                    prob += 100.0f*(getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender,n_D)+(getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender-1,n_D)));
                                }
                            }

                            if (prob > HP_percent_cutoff || (pAttacker->combatLimit()<pDefender->maxHitPoints() && (n_D==iNeededRoundsAttacker)))
                            {
                                if (bIsCondensed) // then we need to print the prev ones
                                {
                                    szString.append(NEWLINE);

                                    int pixels = (int)(Scaling_Factor*combined_HP_sum + 0.5);  // 1% per pixel
                                    int fullBlocks = (pixels) / 10;
                                    int lastBlock = (pixels) % 10;
                                    szString.append(L"<img=Art/ACO/red_bar_left_end.dds>");
                                    for (int iI = 0; iI < fullBlocks; ++iI)
                                    {
                                        szString.append(L"<img=Art/ACO/red_bar_10.dds>");
                                    }
                                    if (lastBlock > 0)
                                    {
                                        szTempBuffer2.Format(L"<img=Art/ACO/red_bar_%d.dds>", lastBlock);
                                        szString.append(szTempBuffer2);
                                    }
                                    szString.append(L"<img=Art/ACO/red_bar_right_end.dds>");
                                    szString.append(L" ");
                                    szString.append(gDLL->getText("TXT_KEY_COLOR_NEGATIVE"));
                                    szTempBuffer.Format(L"%dHP",first_combined_HP_Def);
                                    szString.append(szTempBuffer.GetCString());
                                    szString.append(gDLL->getText("TXT_ACO_HP"));
                                    if (first_combined_HP_Def!=last_combined_HP)
                                    {
                                        szString.append("-");
                                        szTempBuffer.Format(L"%d",last_combined_HP);
                                        szString.append(szTempBuffer.GetCString());
                                        szString.append(gDLL->getText("TXT_ACO_HP"));
                                    }
                                    szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                                    szTempBuffer.Format(L" %.2f%%",
                                                        combined_HP_sum);
                                    szString.append(szTempBuffer.GetCString());

                                    bIsCondensed = false;//resetting
                                    combined_HP_sum = 0.0f;//resetting this variable
                                }

                                szString.append(NEWLINE);
                                int pixels = (int)(Scaling_Factor*prob + 0.5);  // 1% per pixel
                                int fullBlocks = (pixels) / 10;
                                int lastBlock = (pixels) % 10;
                                //if(pixels>=2) // this is now guaranteed by the way we define number of pixels
                                //{
                                    szString.append(L"<img=Art/ACO/red_bar_left_end.dds>");
                                    for (int iI = 0; iI < fullBlocks; ++iI)
                                    {
                                        szString.append(L"<img=Art/ACO/red_bar_10.dds>");
                                    }
                                    if (lastBlock > 0)
                                    {
                                        szTempBuffer2.Format(L"<img=Art/ACO/red_bar_%d.dds>", lastBlock);
                                        szString.append(szTempBuffer2);
                                    }
                                    szString.append(L"<img=Art/ACO/red_bar_right_end.dds>");
                                //}
                                szString.append(L" ");

                                szTempBuffer.Format(SETCOLR L"%d" ENDCOLR,
                                                    TEXT_COLOR("COLOR_NEGATIVE_TEXT"),def_HP);
                                szString.append(szTempBuffer.GetCString());
                                szString.append(gDLL->getText("TXT_KEY_COLOR_NEGATIVE"));
                                szString.append(gDLL->getText("TXT_ACO_HP"));
                                szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                                szTempBuffer.Format(L" %.2f%%",prob);
                                szString.append(szTempBuffer.GetCString());
                            }
                            else
                            {
                                bIsCondensed = true;
                                first_combined_HP_Def = (std::min(first_combined_HP_Def,def_HP));
                                last_combined_HP = std::max(((pDefender->currHitPoints()) - n_D*iDamageToDefender),pDefender->maxHitPoints()-pAttacker->combatLimit());
                                combined_HP_sum += prob;
                            }
                            prob = 0.0f;
                        }//for n_D


                        if (bIsCondensed && iNeededRoundsAttacker>1) // then we need to print the prev ones
                            // the reason we need iNeededRoundsAttacker to be greater than 1 is that if it's equal to 1 then we end up with the defender detailed HP bar show up twice, because it will also get printed below
                        {
                            szString.append(NEWLINE);
                            int pixels = (int)(Scaling_Factor*combined_HP_sum + 0.5);  // 1% per pixel
                            int fullBlocks = (pixels) / 10;
                            int lastBlock = (pixels) % 10;
                            //if(pixels>=2) {szString.append(L"<img=Art/ACO/green_bar_left_end.dds>");}
                            szString.append(L"<img=Art/ACO/red_bar_left_end.dds>");
                            for (int iI = 0; iI < fullBlocks; ++iI)
                            {
                                szString.append(L"<img=Art/ACO/red_bar_10.dds>");
                            }
                            if (lastBlock > 0)
                            {
                                szTempBuffer2.Format(L"<img=Art/ACO/red_bar_%d.dds>", lastBlock);
                                szString.append(szTempBuffer2);
                            }
                            szString.append(L"<img=Art/ACO/red_bar_right_end.dds>");
                            szString.append(L" ");
                            szString.append(gDLL->getText("TXT_KEY_COLOR_NEGATIVE"));
                            szTempBuffer.Format(L"%d",first_combined_HP_Def);
                            szString.append(szTempBuffer.GetCString());
                            szString.append(gDLL->getText("TXT_ACO_HP"));
                            if (first_combined_HP_Def != last_combined_HP)
                            {
                                szTempBuffer.Format(L"-%d",last_combined_HP);
                                szString.append(szTempBuffer.GetCString());
                                szString.append(gDLL->getText("TXT_ACO_HP"));
                            }
                            szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                            szTempBuffer.Format(L" %.2f%%",combined_HP_sum);
                            szString.append(szTempBuffer.GetCString());

                            bIsCondensed = false;//resetting
                            combined_HP_sum = 0.0f;//resetting this variable
                        }

                        //print the unhurt value...always

                        prob = 100.0f*(getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender,0)+(getCombatOddsSpecific(pAttacker,pDefender,iNeededRoundsDefender-1,0)));
                        int pixels = (int)(Scaling_Factor*prob + 0.5);  // 1% per pixel
                        int fullBlocks = (pixels) / 10;
                        int lastBlock = (pixels) % 10;

                        szString.append(NEWLINE);
                        szString.append(L"<img=Art/ACO/red_bar_left_end.dds>");
                        for (int iI = 0; iI < fullBlocks; ++iI)
                        {
                            szString.append(L"<img=Art/ACO/red_bar_10.dds>");
                        }
                        if (lastBlock > 0)
                        {
                            szTempBuffer2.Format(L"<img=Art/ACO/red_bar_%d.dds>", lastBlock);
                            szString.append(szTempBuffer2);
                        }
                        szString.append(L"<img=Art/ACO/red_bar_right_end.dds>");
                        szString.append(L" ");
                        szString.append(gDLL->getText("TXT_KEY_COLOR_NEGATIVE"));
                        szTempBuffer.Format(L"%d",pDefender->currHitPoints());
                        szString.append(szTempBuffer.GetCString());
                        szString.append(gDLL->getText("TXT_ACO_HP"));
                        szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                        szTempBuffer.Format(L" %.2f%%",prob);
                        szString.append(szTempBuffer.GetCString());
                    }
                    //END DEFENDER DETAIL HP HERE

                    szString.append(NEWLINE);

                    if (iView & getBugOptionINT("ACO__ShowBasicInfo", 3, "ACO_SHOW_BASIC_INFO"))
                    {
                        szTempBuffer.Format(SETCOLR L"%d" ENDCOLR L", " SETCOLR L"%d " ENDCOLR,
                                            TEXT_COLOR("COLOR_POSITIVE_TEXT"), iDamageToDefender, TEXT_COLOR("COLOR_NEGATIVE_TEXT"), iDamageToAttacker);
                        szString.append(NEWLINE);
                        szString.append(szTempBuffer.GetCString());
                        szString.append(gDLL->getText("TXT_ACO_HP"));
                        szString.append(" ");
                        szString.append(gDLL->getText("TXT_ACO_MULTIPLY"));
                        szTempBuffer.Format(L" " SETCOLR L"%d" ENDCOLR L", " SETCOLR L"%d " ENDCOLR,
                                            TEXT_COLOR("COLOR_POSITIVE_TEXT"),iNeededRoundsAttacker,TEXT_COLOR("COLOR_NEGATIVE_TEXT"),
                                            iNeededRoundsDefender);
                        szString.append(szTempBuffer.GetCString());
                        szString.append(gDLL->getText("TXT_ACO_HitsAt"));
                        szTempBuffer.Format(SETCOLR L" %.1f%%" ENDCOLR,
                                            TEXT_COLOR("COLOR_POSITIVE_TEXT"),float(iAttackerOdds)*100.0f / float(GC.getDefineINT("COMBAT_DIE_SIDES")));
                        szString.append(szTempBuffer.GetCString());
                    }
                    if (!(iView & getBugOptionINT("ACO__ShowExperienceRange", 2, "ACO_SHOW_EXPERIENCE_RANGE")) || (pAttacker->combatLimit() < (pDefender->maxHitPoints() ))) //medium and high only
                    {
                        if (iView & getBugOptionINT("ACO__ShowBasicInfo", 3, "ACO_SHOW_BASIC_INFO"))
                        {
                            szTempBuffer.Format(L". R=" SETCOLR L"%.2f" ENDCOLR,
                                                TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"),CombatRatio);
                            szString.append(szTempBuffer.GetCString());
                        }
                    }
                    else
                    {
                        //we do an XP range display
                        //This should hopefully now work for any max and min XP values.

                        if (pAttacker->combatLimit() == (pDefender->maxHitPoints() ))
                        {
                            FAssert(GC.getDefineINT("MAX_EXPERIENCE_PER_COMBAT") > GC.getDefineINT("MIN_EXPERIENCE_PER_COMBAT")); //ensuring the differences is at least 1
                            int size = GC.getDefineINT("MAX_EXPERIENCE_PER_COMBAT") - GC.getDefineINT("MIN_EXPERIENCE_PER_COMBAT");
                            float* CombatRatioThresholds = new float[size];

                            for (int i = 0; i < size; i++) //setup the array
                            {
                                CombatRatioThresholds[i] = ((float)(pDefender->attackXPValue()))/((float)(GC.getDefineINT("MAX_EXPERIENCE_PER_COMBAT")-i));
                                //For standard game, this is the list created:
                                //  {4/10, 4/9, 4/8,
                                //   4/7, 4/6, 4/5,
                                //   4/4, 4/3, 4/2}
                            }
                            for (int i = size-1; i >= 0; i--) // find which range we are in
                            {
                                //starting at i = 8, going through to i = 0
                                if (CombatRatio>CombatRatioThresholds[i])
                                {

                                    if (i== (size-1) )//highest XP value already
                                    {
                                        szString.append(NEWLINE);
                                        szTempBuffer.Format(L"(%.2f:%d",
                                                            CombatRatioThresholds[i],GC.getDefineINT("MIN_EXPERIENCE_PER_COMBAT")+1);
                                        szString.append(szTempBuffer.GetCString());
                                        szString.append(gDLL->getText("TXT_ACO_XP"));
                                        szTempBuffer.Format(L"), (R=" SETCOLR L"%.2f" ENDCOLR L":%d",
                                                            TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"),CombatRatio,iExperience);
                                        szString.append(szTempBuffer.GetCString());
                                        szString.append(gDLL->getText("TXT_ACO_XP"));
                                        szString.append(")");
                                    }
                                    else // normal situation
                                    {
                                        szString.append(NEWLINE);
                                        szTempBuffer.Format(L"(%.2f:%d",
                                                            CombatRatioThresholds[i],GC.getDefineINT("MAX_EXPERIENCE_PER_COMBAT")-i);
                                        szString.append(szTempBuffer.GetCString());
                                        szString.append(gDLL->getText("TXT_ACO_XP"));
                                        szTempBuffer.Format(L"), (R=" SETCOLR L"%.2f" ENDCOLR L":%d",
                                                            TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"),CombatRatio,GC.getDefineINT("MAX_EXPERIENCE_PER_COMBAT")-(i+1));
                                        szString.append(szTempBuffer.GetCString());
                                        szString.append(gDLL->getText("TXT_ACO_XP"));
                                        szTempBuffer.Format(L"), (>%.2f:%d",
                                                            CombatRatioThresholds[i+1],GC.getDefineINT("MAX_EXPERIENCE_PER_COMBAT")-(i+2));
                                        szString.append(szTempBuffer.GetCString());
                                        szString.append(gDLL->getText("TXT_ACO_XP"));
                                        szString.append(")");
                                    }
                                    break;

                                }
                                else//very rare (ratio less than or equal to 0.4)
                                {
                                    if (i==0)//maximum XP
                                    {
                                        szString.append(NEWLINE);
                                        szTempBuffer.Format(L"(R=" SETCOLR L"%.2f" ENDCOLR L":%d",
                                                            TEXT_COLOR("COLOR_POSITIVE_TEXT"),CombatRatio,GC.getDefineINT("MAX_EXPERIENCE_PER_COMBAT"));
                                        szString.append(szTempBuffer.GetCString());

                                        szTempBuffer.Format(L"), (>%.2f:%d",
                                                            CombatRatioThresholds[i],GC.getDefineINT("MAX_EXPERIENCE_PER_COMBAT")-1);
                                        szString.append(szTempBuffer.GetCString());
                                        szString.append(gDLL->getText("TXT_ACO_XP"));
                                        szString.append(")");
                                        break;
                                    }//if
                                }// else if
                            }//for
                            delete CombatRatioThresholds;
                            //throw away the array
                        }//if
                    } // else if
                    //Finished Showing XP range display


                    if (iView & getBugOptionINT("ACO__ShowAverageHealth", 2, "ACO_SHOW_AVERAGE_HEALTH"))
                    {
                        szTempBuffer.Format(L"%.1f",E_HP_Att);
                        szTempBuffer2.Format(L"%.1f",E_HP_Def);
                        szString.append(gDLL->getText("TXT_ACO_AverageHP"));
                        szString.append(gDLL->getText("TXT_ACO_VS", szTempBuffer.GetCString(), szTempBuffer2.GetCString()));
                    }

                    if (iView & getBugOptionINT("ACO__ShowUnharmedOdds", 2, "ACO_SHOW_UNHARMED_ODDS"))
                    {
                        szTempBuffer.Format(L"%.2f%%",100.0f*AttackerUnharmed);
                        szTempBuffer2.Format(L"%.2f%%",100.0f*DefenderUnharmed);
                        szString.append(gDLL->getText("TXT_ACO_Unharmed"));
                        szString.append(gDLL->getText("TXT_ACO_VS", szTempBuffer.GetCString(), szTempBuffer2.GetCString()));
                    }

                    if (iView & getBugOptionINT("ACO__ShowUnroundedExperience", 0, "ACO_SHOW_UNROUNDED_EXPERIENCE"))
                    {
                        szTempBuffer.Format(L"%.2f", AttXP);
                        szTempBuffer2.Format(L"%.2f", DefXP);
                        szString.append(gDLL->getText("TXT_ACO_UnroundedXP"));
                        szString.append(gDLL->getText("TXT_ACO_VS", szTempBuffer.GetCString(), szTempBuffer2.GetCString()));
                    }

                    szString.append(NEWLINE);
                    if (iView & getBugOptionINT("ACO__ShowShiftInstructions", 1, "ACO_SHOW_SHIFT_INSTRUCTIONS"))
                    {
                        szString.append(gDLL->getText("TXT_ACO_PressSHIFT"));
                        szString.append(NEWLINE);
                    }

                }//if ACO_enabled
/*************************************************************************************************/
/** ADVANCED COMBAT ODDS                      3/11/09                           PieceOfMind      */
/** END                                                                         v2.0             */
/*************************************************************************************************/
			}
/*************************************************************************************************/
/** ADVANCED COMBAT ODDS                      3/11/09                           PieceOfMind      */
/** BEGIN                                                                       v2.0             */
/*************************************************************************************************/
/* Old Code */
/*

*/
/* New Code */
            if (ACO_enabled)
            {
                szString.append(NEWLINE);

                szTempBuffer.Format(L"%.2f", ((pAttacker->getDomainType() == DOMAIN_AIR)
						? pAttacker->airCurrCombatStrFloat(pDefender)
						: pAttacker->currCombatStrFloat(NULL, pDefender)));

                if (pAttacker->isHurt())
                {
                    szTempBuffer.append(L" (");
                    szTempBuffer.append(gDLL->getText("TXT_ACO_INJURED_HP",
                                                    pAttacker->currHitPoints(),
                                                    pAttacker->maxHitPoints()));
                    szTempBuffer.append(L")");
                }


                szTempBuffer2.Format(L"%.2f",
                                    pDefender->currCombatStrFloat(pPlot, pAttacker)
                                    );

                if (pDefender->isHurt())
                {
                    szTempBuffer2.append(L" (");
                    szTempBuffer2.append(gDLL->getText("TXT_ACO_INJURED_HP",
                                                    pDefender->currHitPoints(),
                                                    pDefender->maxHitPoints()));
                    szTempBuffer2.append(L")");
                }

                szString.append(gDLL->getText("TXT_ACO_VS", szTempBuffer.GetCString(), szTempBuffer2.GetCString()));

                if (((!(pDefender->immuneToFirstStrikes())) && (pAttacker->maxFirstStrikes() > 0)) || (pAttacker->maxCombatStr(NULL,pDefender)!=pAttacker->baseCombatStr()*100))
                {
                    //if attacker uninjured strength is not the same as base strength (i.e. modifiers are in effect) or first strikes exist, then
                    if (getBugOptionBOOL("ACO__ShowModifierLabels", false, "ACO_SHOW_MODIFIER_LABELS"))
                    {
                        szString.append(gDLL->getText("TXT_ACO_AttackModifiers"));
                    }
                }//if
                if ((iView & getBugOptionINT("ACO__ShowAttackerInfo", 0, "ACO_SHOW_ATTACKER_INFO")))
                {
                    szString.append(NEWLINE);
                    setUnitHelp(szString, pAttacker, true, true);
                }

                szString.append(gDLL->getText("TXT_KEY_COLOR_POSITIVE"));
                szString.append(L' ');//XXX

                if (!(pDefender->immuneToFirstStrikes()))
                {
                    if (pAttacker->maxFirstStrikes() > 0)
                    {
                        if (pAttacker->firstStrikes() == pAttacker->maxFirstStrikes())
                        {
                            if (pAttacker->firstStrikes() == 1)
                            {
                                szString.append(NEWLINE);
                                szString.append(gDLL->getText("TXT_KEY_UNIT_ONE_FIRST_STRIKE"));
                            }
                            else
                            {
                                szString.append(NEWLINE);
                                szString.append(gDLL->getText("TXT_KEY_UNIT_NUM_FIRST_STRIKES", pAttacker->firstStrikes()));
                            }
                        }
                        else
                        {
                            szString.append(NEWLINE);
                            szString.append(gDLL->getText("TXT_KEY_UNIT_FIRST_STRIKE_CHANCES", pAttacker->firstStrikes(), pAttacker->maxFirstStrikes()));
                        }
                    }
                }

                iModifier = pAttacker->getExtraCombatPercent();

                if (iModifier != 0)
                {
                    szString.append(NEWLINE);
                    szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_EXTRA_STRENGTH", iModifier));
                }

                szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
                szString.append(L' ');//XXX

                if (((!(pAttacker->immuneToFirstStrikes())) && (pDefender->maxFirstStrikes() > 0)) || (pDefender->maxCombatStr(pPlot,pAttacker)!=pDefender->baseCombatStr()*100))
                {
                    //if attacker uninjured strength is not the same as base strength (i.e. modifiers are in effect) or first strikes exist, then
                    if (getBugOptionBOOL("ACO__ShowModifierLabels", false, "ACO_SHOW_MODIFIER_LABELS"))
                    {
                        szString.append(gDLL->getText("TXT_ACO_DefenseModifiers"));
                    }
                }//if
                if (iView & getBugOptionINT("ACO__ShowDefenderInfo", 3, "ACO_SHOW_DEFENDER_INFO"))
                {
                    szString.append(NEWLINE);
                    setUnitHelp(szString, pDefender, true, true);
                }

                if (iView & getBugOptionINT("ACO__ShowDefenseModifiers", 3, "ACO_SHOW_DEFENSE_MODIFIERS"))
                {
                    //if defense modifiers are enabled - recommend leaving this on unless Total defense Modifier is enabled
                    szString.append(gDLL->getText("TXT_KEY_COLOR_NEGATIVE"));

                    szString.append(L' ');//XXX

                    if (!(pAttacker->immuneToFirstStrikes()))
                    {
                        if (pDefender->maxFirstStrikes() > 0)
                        {
                            if (pDefender->firstStrikes() == pDefender->maxFirstStrikes())
                            {
                                if (pDefender->firstStrikes() == 1)
                                {
                                    szString.append(NEWLINE);
                                    szString.append(gDLL->getText("TXT_KEY_UNIT_ONE_FIRST_STRIKE"));
                                }
                                else
                                {
                                    szString.append(NEWLINE);
                                    szString.append(gDLL->getText("TXT_KEY_UNIT_NUM_FIRST_STRIKES", pDefender->firstStrikes()));
                                }
                            }
                            else
                            {
                                szString.append(NEWLINE);
                                szString.append(gDLL->getText("TXT_KEY_UNIT_FIRST_STRIKE_CHANCES", pDefender->firstStrikes(), pDefender->maxFirstStrikes()));
                            }
                        }
                    }

                    if (!(pAttacker->isRiver()))
                    {
                        if (pAttacker->plot()->isRiverCrossing(directionXY(pAttacker->plot(), pPlot)))
                        {
                            iModifier = GC.getRIVER_ATTACK_MODIFIER();

                            if (iModifier != 0)
                            {
                                szString.append(NEWLINE);
                                szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_RIVER_MOD", -(iModifier)));
                            }
                        }
                    }

                    if (!(pAttacker->isAmphib()))
                    {
                        if (!(pPlot->isWater()) && pAttacker->plot()->isWater())
                        {
                            iModifier = GC.getAMPHIB_ATTACK_MODIFIER();

                            if (iModifier != 0)
                            {
                                szString.append(NEWLINE);
                                szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_AMPHIB_MOD", -(iModifier)));
                            }
                        }
                    }

                    iModifier = pDefender->getExtraCombatPercent();

                    if (iModifier != 0)
                    {
                        szString.append(NEWLINE);
                        szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_EXTRA_STRENGTH", iModifier));
                    }

                    iModifier = pDefender->unitClassDefenseModifier(pAttacker->getUnitClassType());

                    if (iModifier != 0)
                    {
                        szString.append(NEWLINE);
                        szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", iModifier, GC.getUnitClassInfo(pAttacker->getUnitClassType()).getTextKeyWide()));
                    }

                    if (pAttacker->getUnitCombatType() != NO_UNITCOMBAT)
                    {
                        iModifier = pDefender->unitCombatModifier(pAttacker->getUnitCombatType());

                        if (iModifier != 0)
                        {
                            szString.append(NEWLINE);
                            szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", iModifier, GC.getUnitCombatInfo(pAttacker->getUnitCombatType()).getTextKeyWide()));
                        }
                    }

                    iModifier = pDefender->domainModifier(pAttacker->getDomainType());

                    if (iModifier != 0)
                    {
                        szString.append(NEWLINE);
                        szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", iModifier, GC.getDomainInfo(pAttacker->getDomainType()).getTextKeyWide()));
                    }

                    if (!(pDefender->noDefensiveBonus()))
                    {
                        iModifier = pPlot->defenseModifier(pDefender->getTeam(), (pAttacker != NULL) ? pAttacker->ignoreBuildingDefense() : true);

                        if (iModifier != 0)
                        {
                            szString.append(NEWLINE);
                            szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_TILE_MOD", iModifier));
                        }
                    }

                    iModifier = pDefender->fortifyModifier();

                    if (iModifier != 0)
                    {
                        szString.append(NEWLINE);
                        szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_FORTIFY_MOD", iModifier));
                    }

                    if (pPlot->isCity(true, pDefender->getTeam()))
                    {
                        iModifier = pDefender->cityDefenseModifier();

                        if (iModifier != 0)
                        {
                            szString.append(NEWLINE);
                            szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_CITY_MOD", iModifier));
                        }
                    }

                    if (pPlot->isHills())
                    {
                        iModifier = pDefender->hillsDefenseModifier();

                        if (iModifier != 0)
                        {
                            szString.append(NEWLINE);
                            szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_HILLS_MOD", iModifier));
                        }
                    }

                    if (pPlot->getFeatureType() != NO_FEATURE)
                    {
                        iModifier = pDefender->featureDefenseModifier(pPlot->getFeatureType());

                        if (iModifier != 0)
                        {
                            szString.append(NEWLINE);
                            szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_UNIT_MOD", iModifier, GC.getFeatureInfo(pPlot->getFeatureType()).getTextKeyWide()));
                        }
                    }
                    else
                    {
                        iModifier = pDefender->terrainDefenseModifier(pPlot->getTerrainType());

                        if (iModifier != 0)
                        {
                            szString.append(NEWLINE);
                            szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_UNIT_MOD", iModifier, GC.getTerrainInfo(pPlot->getTerrainType()).getTextKeyWide()));
                        }
                    }

					// MNAI Start - FfH Promotions: Added by Kael 0813/2007
					for (int iJ=0;iJ<GC.getNumPromotionInfos();iJ++)
					{
						if (pDefender->isHasPromotion((PromotionTypes)iJ) && GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod()>0)
						{
							if (pAttacker->isHasPromotion((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatType()))
							{
								szString.append(NEWLINE);
								szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod(), GC.getPromotionInfo((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatType()).getTextKeyWide()));
							}
						}
					}

					iModifier = GC.getGameINLINE().getGlobalCounter() * pDefender->getCombatPercentGlobalCounter() / 100;
					if (iModifier != 0)
					{
						szString.append(NEWLINE);
						szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_STIGMATA", iModifier));
					}
					//End MNAI

                    szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));

                    szString.append(L' ');//XXX

                    szString.append(gDLL->getText("TXT_KEY_COLOR_POSITIVE"));

                    szString.append(L' ');//XXX


                    iModifier = pAttacker->unitClassAttackModifier(pDefender->getUnitClassType());

                    if (iModifier != 0)
                    {
                        szString.append(NEWLINE);
                        szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", -iModifier, GC.getUnitClassInfo(pDefender->getUnitClassType()).getTextKeyWide()));
                    }

                    if (pDefender->getUnitCombatType() != NO_UNITCOMBAT)
                    {
                        iModifier = pAttacker->unitCombatModifier(pDefender->getUnitCombatType());

                        if (iModifier != 0)
                        {
                            szString.append(NEWLINE);
                            szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", -iModifier, GC.getUnitCombatInfo(pDefender->getUnitCombatType()).getTextKeyWide()));
                        }
                    }

                    iModifier = pAttacker->domainModifier(pDefender->getDomainType());

                    if (iModifier != 0)
                    {
                        szString.append(NEWLINE);
                        szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", -iModifier, GC.getDomainInfo(pDefender->getDomainType()).getTextKeyWide()));
                    }

                    if (pPlot->isCity(true, pDefender->getTeam()))
                    {
                        iModifier = pAttacker->cityAttackModifier();

                        if (iModifier != 0)
                        {
                            szString.append(NEWLINE);
                            szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_CITY_MOD", -iModifier));
                        }
                    }

                    if (pPlot->isHills())
                    {
                        iModifier = pAttacker->hillsAttackModifier();

                        if (iModifier != 0)
                        {
                            szString.append(NEWLINE);
                            szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_HILLS_MOD", -iModifier));
                        }
                    }

                    if (pPlot->getFeatureType() != NO_FEATURE)
                    {
                        iModifier = pAttacker->featureAttackModifier(pPlot->getFeatureType());

                        if (iModifier != 0)
                        {
                            szString.append(NEWLINE);
                            szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_UNIT_MOD", -iModifier, GC.getFeatureInfo(pPlot->getFeatureType()).getTextKeyWide()));
                        }
                    }
                    else
                    {
                        iModifier = pAttacker->terrainAttackModifier(pPlot->getTerrainType());

                        if (iModifier != 0)
                        {
                            szString.append(NEWLINE);
                            szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_UNIT_MOD", -iModifier, GC.getTerrainInfo(pPlot->getTerrainType()).getTextKeyWide()));
                        }
                    }
					// MNAI Start - FfH Promotions: Added by Kael 0813/2007 - Merged into ACO by MNAI
					for (int iJ=0; iJ < GC.getNumPromotionInfos(); iJ++)
					{
						if (pAttacker->isHasPromotion((PromotionTypes)iJ) && GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod()>0)
						{
							if (pDefender->isHasPromotion((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatType()))
							{
								szString.append(NEWLINE);
								szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod(), GC.getPromotionInfo((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatType()).getTextKeyWide()));
							}
						}
					}

					iModifier = GC.getGameINLINE().getGlobalCounter() * pAttacker->getCombatPercentGlobalCounter() / 100;
					if (iModifier != 0)
					{
						szString.append(NEWLINE);
						szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_STIGMATA", iModifier));
					}
					// End MNAI

                    iModifier = pAttacker->getKamikazePercent();
                    if (iModifier != 0)
                    {
                        szString.append(NEWLINE);
                        szString.append(gDLL->getText("TXT_KEY_COMBAT_KAMIKAZE_MOD", -iModifier));
                    }

                    if (pDefender->isAnimal())
                    {
                        iModifier = -GC.getHandicapInfo(GC.getGameINLINE().getHandicapType()).getAnimalCombatModifier();

                        iModifier += pAttacker->getUnitInfo().getAnimalCombatModifier();

                        if (iModifier != 0)
                        {
                            szString.append(NEWLINE);
                            szString.append(gDLL->getText("TXT_KEY_UNIT_ANIMAL_COMBAT_MOD", -iModifier));
                        }
                    }

                    if (pDefender->isBarbarian())
                    {
                        iModifier = -GC.getHandicapInfo(GC.getGameINLINE().getHandicapType()).getBarbarianCombatModifier();

                        if (iModifier != 0)
                        {
                            szString.append(NEWLINE);
                            szString.append(gDLL->getText("TXT_KEY_UNIT_BARBARIAN_COMBAT_MOD", -iModifier));
                        }
                    }
                }//if

                szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));

                szString.append(L' ');//XXX

                if (iView & getBugOptionINT("ACO__ShowTotalDefenseModifier", 2, "ACO_SHOW_TOTAL_DEFENSE_MODIFIER"))
                {
                    //szString.append(L' ');//XXX
                    if (pDefender->maxCombatStr(pPlot,pAttacker) > pDefender->baseCombatStr()*100) // modifier is positive
                    {
                        szTempBuffer.Format(SETCOLR L"%d%%" ENDCOLR,
							TEXT_COLOR("COLOR_NEGATIVE_TEXT"),(((pDefender->maxCombatStr(pPlot,pAttacker)))/(std::max(pDefender->baseCombatStr(), 1)))-100);
                    }
                    else   // modifier is negative
                    {
                        szTempBuffer.Format(SETCOLR L"%d%%" ENDCOLR,
							TEXT_COLOR("COLOR_POSITIVE_TEXT"),(100-((pDefender->baseCombatStr()*10000)/(std::max(pDefender->maxCombatStr(pPlot,pAttacker), 1)))));
                    }

                    szString.append(gDLL->getText("TXT_ACO_TotalDefenseModifier"));
                    szString.append(szTempBuffer.GetCString());
                }
            }//if

            /** What follows in the "else" block, is the original code **/
            else
			{
                //ACO is not enabled
/*************************************************************************************************/
/** ADVANCED COMBAT ODDS                      3/11/09                           PieceOfMind      */
/** END                                                                         v2.0             */
/*************************************************************************************************/
			szOffenseOdds.Format(L"%.2f", ((pAttacker->getDomainType() == DOMAIN_AIR) ? pAttacker->airCurrCombatStrFloat(pDefender) : pAttacker->currCombatStrFloat(NULL, pDefender)));
			szDefenseOdds.Format(L"%.2f", pDefender->currCombatStrFloat(pPlot, pAttacker));
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_ODDS_VS", szOffenseOdds.GetCString(), szDefenseOdds.GetCString()));

			szString.append(L' ');//XXX

			szString.append(gDLL->getText("TXT_KEY_COLOR_POSITIVE"));

			szString.append(L' ');//XXX

			iModifier = pAttacker->getExtraCombatPercent();

			if (iModifier != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_EXTRA_STRENGTH", iModifier));
			}

			iModifier = pAttacker->unitClassAttackModifier(pDefender->getUnitClassType());

			if (iModifier != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", iModifier, GC.getUnitClassInfo(pDefender->getUnitClassType()).getTextKeyWide()));
			}

			if (pDefender->getUnitCombatType() != NO_UNITCOMBAT)
			{
				iModifier = pAttacker->unitCombatModifier(pDefender->getUnitCombatType());

				if (iModifier != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", iModifier, GC.getUnitCombatInfo(pDefender->getUnitCombatType()).getTextKeyWide()));
				}
			}

			iModifier = pAttacker->domainModifier(pDefender->getDomainType());

			if (iModifier != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", iModifier, GC.getDomainInfo(pDefender->getDomainType()).getTextKeyWide()));
			}

			if (pPlot->isCity(true, pDefender->getTeam()))
			{
				iModifier = pAttacker->cityAttackModifier();

				if (iModifier != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_CITY_MOD", iModifier));
				}
			}

			if (pPlot->isHills())
			{
				iModifier = pAttacker->hillsAttackModifier();

				if (iModifier != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_HILLS_MOD", iModifier));
				}
			}

			if (pPlot->getFeatureType() != NO_FEATURE)
			{
				iModifier = pAttacker->featureAttackModifier(pPlot->getFeatureType());

				if (iModifier != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_UNIT_MOD", iModifier, GC.getFeatureInfo(pPlot->getFeatureType()).getTextKeyWide()));
				}
			}
			else
			{
				iModifier = pAttacker->terrainAttackModifier(pPlot->getTerrainType());

				if (iModifier != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_UNIT_MOD", iModifier, GC.getTerrainInfo(pPlot->getTerrainType()).getTextKeyWide()));
				}
			}
			
//FfH Promotions: Added by Kael 0813/2007
            for (int iJ=0; iJ < GC.getNumPromotionInfos(); iJ++)
            {
                if (pAttacker->isHasPromotion((PromotionTypes)iJ) && GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod()>0)
                {
                    if (pDefender->isHasPromotion((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatType()))
                    {
                        szString.append(NEWLINE);
                        szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod(), GC.getPromotionInfo((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatType()).getTextKeyWide()));
                    }
                }
            }

            iModifier = GC.getGameINLINE().getGlobalCounter() * pAttacker->getCombatPercentGlobalCounter() / 100;
            if (iModifier != 0)
            {
                szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_STIGMATA", iModifier));
            }
//FfH: End Add

			iModifier = pAttacker->getKamikazePercent();
			if (iModifier != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_COMBAT_KAMIKAZE_MOD", iModifier));
			}

			if (pDefender->isAnimal())
			{
				iModifier = -GC.getHandicapInfo(GC.getGameINLINE().getHandicapType()).getAnimalCombatModifier();

				iModifier += pAttacker->getUnitInfo().getAnimalCombatModifier();

				if (iModifier != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_UNIT_ANIMAL_COMBAT_MOD", iModifier));
				}
			}

			if (pDefender->isBarbarian())
			{
				iModifier = -GC.getHandicapInfo(GC.getGameINLINE().getHandicapType()).getBarbarianCombatModifier();

				if (iModifier != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_UNIT_BARBARIAN_COMBAT_MOD", iModifier));
				}
			}

			if (!(pDefender->immuneToFirstStrikes()))
			{
				if (pAttacker->maxFirstStrikes() > 0)
				{
					if (pAttacker->firstStrikes() == pAttacker->maxFirstStrikes())
					{
						if (pAttacker->firstStrikes() == 1)
						{
							szString.append(NEWLINE);
							szString.append(gDLL->getText("TXT_KEY_UNIT_ONE_FIRST_STRIKE"));
						}
						else
						{
							szString.append(NEWLINE);
							szString.append(gDLL->getText("TXT_KEY_UNIT_NUM_FIRST_STRIKES", pAttacker->firstStrikes()));
						}
					}
					else
					{
						szString.append(NEWLINE);
						szString.append(gDLL->getText("TXT_KEY_UNIT_FIRST_STRIKE_CHANCES", pAttacker->firstStrikes(), pAttacker->maxFirstStrikes()));
					}
				}
			}

			if (pAttacker->isHurt())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_HP", pAttacker->currHitPoints(), pAttacker->maxHitPoints()));
			}

			szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));

			szString.append(L' ');//XXX

			szString.append(gDLL->getText("TXT_KEY_COLOR_NEGATIVE"));

			szString.append(L' ');//XXX

			if (!(pAttacker->isRiver()))
			{
				if (pAttacker->plot()->isRiverCrossing(directionXY(pAttacker->plot(), pPlot)))
				{
					iModifier = GC.getRIVER_ATTACK_MODIFIER();

					if (iModifier != 0)
					{
						szString.append(NEWLINE);
						szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_RIVER_MOD", -(iModifier)));
					}
				}
			}

			if (!(pAttacker->isAmphib()))
			{
				if (!(pPlot->isWater()) && pAttacker->plot()->isWater())
				{
					iModifier = GC.getAMPHIB_ATTACK_MODIFIER();

					if (iModifier != 0)
					{
						szString.append(NEWLINE);
						szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_AMPHIB_MOD", -(iModifier)));
					}
				}
			}

			iModifier = pDefender->getExtraCombatPercent();

			if (iModifier != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_EXTRA_STRENGTH", iModifier));
			}

			iModifier = pDefender->unitClassDefenseModifier(pAttacker->getUnitClassType());

			if (iModifier != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", iModifier, GC.getUnitClassInfo(pAttacker->getUnitClassType()).getTextKeyWide()));
			}

			if (pAttacker->getUnitCombatType() != NO_UNITCOMBAT)
			{
				iModifier = pDefender->unitCombatModifier(pAttacker->getUnitCombatType());

				if (iModifier != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", iModifier, GC.getUnitCombatInfo(pAttacker->getUnitCombatType()).getTextKeyWide()));
				}
			}

			iModifier = pDefender->domainModifier(pAttacker->getDomainType());

			if (iModifier != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", iModifier, GC.getDomainInfo(pAttacker->getDomainType()).getTextKeyWide()));
			}

			for (int iJ=0; iJ < GC.getNumPromotionInfos(); iJ++)
            {
                if (pDefender->isHasPromotion((PromotionTypes)iJ) && GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod()>0)
                {
                    if (pAttacker->isHasPromotion((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatType()))
                    {
                        szString.append(NEWLINE);
                        szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod(), GC.getPromotionInfo((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatType()).getTextKeyWide()));
                    }
                }
            }

			if (!(pDefender->noDefensiveBonus()))
			{
				iModifier = pPlot->defenseModifier(pDefender->getTeam(), (pAttacker != NULL) ? pAttacker->ignoreBuildingDefense() : true);

				if (iModifier != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_TILE_MOD", iModifier));
				}
			}

			iModifier = pDefender->fortifyModifier();

			if (iModifier != 0)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_FORTIFY_MOD", iModifier));
			}

			if (pPlot->isCity(true, pDefender->getTeam()))
			{
				iModifier = pDefender->cityDefenseModifier();

				if (iModifier != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_CITY_MOD", iModifier));
				}
			}

			if (pPlot->isHills())
			{
				iModifier = pDefender->hillsDefenseModifier();

				if (iModifier != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_HILLS_MOD", iModifier));
				}
			}

			if (pPlot->getFeatureType() != NO_FEATURE)
			{
				iModifier = pDefender->featureDefenseModifier(pPlot->getFeatureType());

				if (iModifier != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_UNIT_MOD", iModifier, GC.getFeatureInfo(pPlot->getFeatureType()).getTextKeyWide()));
				}
			}
			else
			{
				iModifier = pDefender->terrainDefenseModifier(pPlot->getTerrainType());

				if (iModifier != 0)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_UNIT_MOD", iModifier, GC.getTerrainInfo(pPlot->getTerrainType()).getTextKeyWide()));
				}
			}

			// MNAI Start - FfH Promotions: Added by Kael 0813/2007
            for (int iJ=0;iJ<GC.getNumPromotionInfos();iJ++)
            {
                if (pDefender->isHasPromotion((PromotionTypes)iJ) && GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod()>0)
                {
                    if (pAttacker->isHasPromotion((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatType()))
                    {
                        szString.append(NEWLINE);
                        szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_MOD_VS_TYPE", GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatMod(), GC.getPromotionInfo((PromotionTypes)GC.getPromotionInfo((PromotionTypes)iJ).getPromotionCombatType()).getTextKeyWide()));
                    }
                }
            }

            iModifier = GC.getGameINLINE().getGlobalCounter() * pDefender->getCombatPercentGlobalCounter() / 100;
            if (iModifier != 0)
            {
                szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_STIGMATA", iModifier));
            }
			// End MNAI

			if (!(pAttacker->immuneToFirstStrikes()))
			{
				if (pDefender->maxFirstStrikes() > 0)
				{
					if (pDefender->firstStrikes() == pDefender->maxFirstStrikes())
					{
						if (pDefender->firstStrikes() == 1)
						{
							szString.append(NEWLINE);
							szString.append(gDLL->getText("TXT_KEY_UNIT_ONE_FIRST_STRIKE"));
						}
						else
						{
							szString.append(NEWLINE);
							szString.append(gDLL->getText("TXT_KEY_UNIT_NUM_FIRST_STRIKES", pDefender->firstStrikes()));
						}
					}
					else
					{
						szString.append(NEWLINE);
						szString.append(gDLL->getText("TXT_KEY_UNIT_FIRST_STRIKE_CHANCES", pDefender->firstStrikes(), pDefender->maxFirstStrikes()));
					}
				}
			}

			if (pDefender->isHurt())
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText("TXT_KEY_COMBAT_PLOT_HP", pDefender->currHitPoints(), pDefender->maxHitPoints()));
			}
/*************************************************************************************************/
/** ADVANCED COMBAT ODDS                      3/11/09                           PieceOfMind      */
/** BEGIN                                                                       v2.0             */
/*************************************************************************************************/
/* New Code */
			}
/*************************************************************************************************/
/** ADVANCED COMBAT ODDS                      3/11/09                           PieceOfMind      */
/** END                                                                         v2.0             */
/*************************************************************************************************/

/************************************************************************************************/
/* BETTER_BTS_AI_MOD                      06/20/08                                jdog5000      */
/*                                                                                              */
/* DEBUG                                                                                        */
/************************************************************************************************/
			szString.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));

/* original code
			if ((gDLL->getChtLvl() > 0))
*/
			// Only display this info in debug mode so game can be played with cheat code entered
			if( GC.getGameINLINE().isDebugMode() )
			{
				szTempBuffer.Format(L"\nStack Compare Value = %d",
					gDLL->getInterfaceIFace()->getSelectionList()->AI_compareStacks(pPlot, false));
				szString.append(szTempBuffer);

				if( pPlot->getPlotCity() != NULL )
				{
					szTempBuffer.Format(L"\nBombard turns = %d",
						gDLL->getInterfaceIFace()->getSelectionList()->getBombardTurns(pPlot->getPlotCity()));
					szString.append(szTempBuffer);
				}
				
				int iOurStrengthDefense = GET_PLAYER(GC.getGameINLINE().getActivePlayer()).AI_getOurPlotStrength(pPlot, 1, true, false);
				int iOurStrengthOffense = GET_PLAYER(GC.getGameINLINE().getActivePlayer()).AI_getOurPlotStrength(pPlot, 1, false, false);
				szTempBuffer.Format(L"\nPlot Strength(Ours)= d%d, o%d", iOurStrengthDefense, iOurStrengthOffense);
				szString.append(szTempBuffer);
				int iEnemyStrengthDefense = GET_PLAYER(GC.getGameINLINE().getActivePlayer()).AI_getEnemyPlotStrength(pPlot, 1, true, false);
				int iEnemyStrengthOffense = GET_PLAYER(GC.getGameINLINE().getActivePlayer()).AI_getEnemyPlotStrength(pPlot, 1, false, false);
				szTempBuffer.Format(L"\nPlot Strength(Enemy)= d%d, o%d", iEnemyStrengthDefense, iEnemyStrengthOffense);
				szString.append(szTempBuffer);
			}
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                       END                                                  */
/************************************************************************************************/

			return true;
		}
	}

	return false;
}

// DO NOT REMOVE - needed for font testing - Moose
void createTestFontString(CvWStringBuffer& szString)
{
	int iI;
	szString.assign(L"!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[�]^_`abcdefghijklmnopqrstuvwxyz\n");
	szString.append(L"{}~\\������������������������������ޟ�������������������������������������������������������");
	for (iI=0;iI<NUM_YIELD_TYPES;++iI)
		szString.append(CvWString::format(L"%c", GC.getYieldInfo((YieldTypes) iI).getChar()));

	szString.append(L"\n");
	for (iI=0;iI<NUM_COMMERCE_TYPES;++iI)
		szString.append(CvWString::format(L"%c", GC.getCommerceInfo((CommerceTypes) iI).getChar()));
	szString.append(L"\n");
	for (iI = 0; iI < GC.getNumReligionInfos(); ++iI)
	{
		szString.append(CvWString::format(L"%c", GC.getReligionInfo((ReligionTypes) iI).getChar()));
		szString.append(CvWString::format(L"%c", GC.getReligionInfo((ReligionTypes) iI).getHolyCityChar()));
	}
	for (iI = 0; iI < GC.getNumCorporationInfos(); ++iI)
	{
		szString.append(CvWString::format(L"%c", GC.getCorporationInfo((CorporationTypes) iI).getChar()));
		szString.append(CvWString::format(L"%c", GC.getCorporationInfo((CorporationTypes) iI).getHeadquarterChar()));
	}
	szString.append(L"\n");
	for (iI = 0; iI < GC.getNumBonusInfos(); ++iI)
		szString.append(CvWString::format(L"%c", GC.getBonusInfo((BonusTypes) iI).getChar()));
	for (iI=0; iI<MAX_NUM_SYMBOLS; ++iI)
		szString.append(CvWString::format(L"%c", gDLL->getSymbolID(iI)));
}

void CvGameTextMgr::setPlotHelp(CvWStringBuffer& szString, CvPlot* pPlot)
{
	PROFILE_FUNC();

	int iI;

	CvWString szTempBuffer;
	ImprovementTypes eImprovement;
	PlayerTypes eRevealOwner;
	BonusTypes eBonus;
	bool bShift;
	bool bAlt;
	bool bCtrl;
	bool bFound;
	int iDefenseModifier;
	int iYield;
	int iTurns;

	bShift = gDLL->shiftKey();
	bAlt = gDLL->altKey();
	bCtrl = gDLL->ctrlKey();

	if (bCtrl && (gDLL->getChtLvl() > 0))
	{
		if (bShift && pPlot->headUnitNode() != NULL)
		{
			return;
		}

		if (pPlot->getOwnerINLINE() != NO_PLAYER)
		{
			int iPlotDanger = GET_PLAYER(pPlot->getOwnerINLINE()).AI_getPlotDanger(pPlot, 2);
			if (iPlotDanger > 0)
			{
				szString.append(CvWString::format(L"Plot Danger = %d \n", iPlotDanger));
			}
		}

		CvCity* pPlotCity = pPlot->getPlotCity();
		if (pPlotCity != NULL)
		{
			PlayerTypes ePlayer = pPlot->getOwnerINLINE();
			CvPlayerAI& kPlayer = GET_PLAYER(ePlayer);

/************************************************************************************************/
/* REVOLUTION_MOD                         06/11/08                                jdog5000      */
/*                                                                                              */
/* DEBUG                                                                                        */
/************************************************************************************************/
			if (GC.getGameINLINE().isOption(GAMEOPTION_REVOLUTIONS))
			{
				szString.append(CvWString::format(L"\n\nRevIndex:%d, ", pPlotCity->getRevolutionIndex()));
				szString.append(CvWString::format(L"Avg:%d, ", pPlotCity->getRevIndexAverage()));
				szString.append(CvWString::format(L"Local:%d, ", pPlotCity->getLocalRevIndex()));
				szString.append(CvWString::format(L"Reinf:%d", pPlotCity->getReinforcementCounter()));
				szString.append(CvWString::format(L"\nRevIdxAnger:%d, ", pPlotCity->getRevIndexPercentAnger()));
				szString.append(CvWString::format(L"ReqAnger:%d, ", pPlotCity->getRevRequestPercentAnger()));
				szString.append(CvWString::format(L"RevSucHappy:%d\n", pPlotCity->getRevSuccessHappiness()));
			}
/************************************************************************************************/
/* REVOLUTION_MOD                          END                                                  */
/************************************************************************************************/
			int iCityDefenders = pPlot->plotCount(PUF_canDefendGroupHead, -1, -1, ePlayer, NO_TEAM, PUF_isCityAIType);
			int iAttackGroups = pPlot->plotCount(PUF_isUnitAIType, UNITAI_ATTACK, -1, ePlayer);
			szString.append(CvWString::format(L"\nDefenders [D+A]/N ([%d + %d] / %d)", iCityDefenders, iAttackGroups, pPlotCity->AI_neededDefenders()));

			szString.append(CvWString::format(L"\nFloating Defenders H/N (%d / %d)", kPlayer.AI_getTotalFloatingDefenders(pPlotCity->area()), kPlayer.AI_getTotalFloatingDefendersNeeded(pPlotCity->area())));
			szString.append(CvWString::format(L"\nAir Defenders H/N (%d / %d)", pPlotCity->plot()->plotCount(PUF_canAirDefend, -1, -1, pPlotCity->getOwnerINLINE(), NO_TEAM, PUF_isDomainType, DOMAIN_AIR), pPlotCity->AI_neededAirDefenders()));
//			int iHostileUnits = kPlayer.AI_countNumAreaHostileUnits(pPlotCity->area());
//			if (iHostileUnits > 0)
//			{
//				szString+=CvWString::format(L"\nHostiles = %d", iHostileUnits);
//			}

			int iWorkersHave = pPlotCity->AI_getWorkersHave();
			int iWorkersNeeded = pPlotCity->AI_getWorkersNeeded();
			szString.append(CvWString::format(L"\nWorkers H/N (%d , %d)", iWorkersHave, iWorkersNeeded));

			int iWorkBoatsNeeded = pPlotCity->AI_neededSeaWorkers();
			szString.append(CvWString::format(L"\nWorkboats Needed = %d", iWorkBoatsNeeded));

			szString.append(CvWString::format(L"\nThreat C/P (%d / %d)", pPlotCity->AI_cityThreat(), kPlayer.AI_getTotalAreaCityThreat(pPlotCity->area())));

			bool bFirst = true;
			for (int iI = 0; iI < MAX_PLAYERS; ++iI)
			{
				PlayerTypes eLoopPlayer = (PlayerTypes) iI;
				CvPlayerAI& kLoopPlayer = GET_PLAYER(eLoopPlayer);
				if ((eLoopPlayer != ePlayer) && kLoopPlayer.isAlive())
				{
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                      06/16/08                                jdog5000      */
/*                                                                                              */
/* DEBUG                                                                                        */
/************************************************************************************************/
/* original code
					int iCloseness = pPlotCity->AI_playerCloseness(eLoopPlayer, 7);
					if (iCloseness != 0)
					{
						if (bFirst)
						{
							bFirst = false;
						
							szString.append(CvWString::format(L"\n\nCloseness:"));
						}

						szString.append(CvWString::format(L"\n%s(7) : %d", kLoopPlayer.getName(), iCloseness));
						szString.append(CvWString::format(L" (%d, ", kPlayer.AI_playerCloseness(eLoopPlayer, 7)));
						if (kPlayer.getTeam() != kLoopPlayer.getTeam())
						{
							szString.append(CvWString::format(L"%d)", GET_TEAM(kPlayer.getTeam()).AI_teamCloseness(kLoopPlayer.getTeam(), 7)));
						}
						else
						{
							szString.append(CvWString::format(L"-)"));
						}
					}
*/
					if( pPlotCity->isCapital() )
					{
						if( true )
						{
							int iCloseness = pPlotCity->AI_playerCloseness(eLoopPlayer, DEFAULT_PLAYER_CLOSENESS);
							int iPlayerCloseness = kPlayer.AI_playerCloseness(eLoopPlayer, DEFAULT_PLAYER_CLOSENESS);

							if( GET_TEAM(kPlayer.getTeam()).isHasMet(kLoopPlayer.getTeam()) || iPlayerCloseness != 0 )
							{
								if (bFirst)
								{
									bFirst = false;
								
									szString.append(CvWString::format(L"\n\nCloseness + War: (in %d wars)", GET_TEAM(kPlayer.getTeam()).getAtWarCount(true)));
								}

								szString.append(CvWString::format(L"\n%s(%d) : %d ", kLoopPlayer.getName(), DEFAULT_PLAYER_CLOSENESS, iCloseness));
								szString.append(CvWString::format(L" [%d, ", iPlayerCloseness));
								if (kPlayer.getTeam() != kLoopPlayer.getTeam())
								{
									szString.append(CvWString::format(L"%d]", GET_TEAM(kPlayer.getTeam()).AI_teamCloseness(kLoopPlayer.getTeam(), DEFAULT_PLAYER_CLOSENESS)));
									if( GET_TEAM(kPlayer.getTeam()).isHasMet(kLoopPlayer.getTeam()) && GET_TEAM(kPlayer.getTeam()).AI_getAttitude(kLoopPlayer.getTeam()) != ATTITUDE_FRIENDLY )
									{
										int iStartWarVal = GET_TEAM(kPlayer.getTeam()).AI_startWarVal(kLoopPlayer.getTeam());

										if( GET_TEAM(kPlayer.getTeam()).isAtWar(kLoopPlayer.getTeam()) )
										{
											szString.append(CvWString::format(L"\n   At War:   "));
										}
										else if( GET_TEAM(kPlayer.getTeam()).AI_getWarPlan(kLoopPlayer.getTeam()) != NO_WARPLAN )
										{
											szString.append(CvWString::format(L"\n   Plan. War:"));
										}
										else if( !GET_TEAM(kPlayer.getTeam()).canDeclareWar(kLoopPlayer.getTeam()) )
										{
											szString.append(CvWString::format(L"\n   Can't War:"));
										}
										else
										{
											szString.append(CvWString::format(L"\n   No War:   "));
										}

										if( iStartWarVal > 1200 )
										{
											szString.append(CvWString::format(SETCOLR L" %d" ENDCOLR, TEXT_COLOR("COLOR_RED"), iStartWarVal));
										}
										else if( iStartWarVal > 600 )
										{
											szString.append(CvWString::format(SETCOLR L" %d" ENDCOLR, TEXT_COLOR("COLOR_YELLOW"), iStartWarVal));
										}
										else
										{
											szString.append(CvWString::format(L" %d", iStartWarVal));
										}
										
										szString.append(CvWString::format(L" (%d", GET_TEAM(kPlayer.getTeam()).AI_calculatePlotWarValue(kLoopPlayer.getTeam())));
										szString.append(CvWString::format(L", %d", GET_TEAM(kPlayer.getTeam()).AI_calculateBonusWarValue(kLoopPlayer.getTeam())));
										szString.append(CvWString::format(L", %d", GET_TEAM(kPlayer.getTeam()).AI_calculateCapitalProximity(kLoopPlayer.getTeam())));
										szString.append(CvWString::format(L", %4s", GC.getAttitudeInfo(GET_TEAM(kPlayer.getTeam()).AI_getAttitude(kLoopPlayer.getTeam())).getDescription(0)));
										szString.append(CvWString::format(L", %d%%)", 100-GET_TEAM(kPlayer.getTeam()).AI_noWarAttitudeProb(GET_TEAM(kPlayer.getTeam()).AI_getAttitude(kLoopPlayer.getTeam()))));
									}
								}
								else
								{
									szString.append(CvWString::format(L"-]"));
								}
							}
						}
					}
					else 
					{
						int iCloseness = pPlotCity->AI_playerCloseness(eLoopPlayer, DEFAULT_PLAYER_CLOSENESS);
						
						if (iCloseness != 0)
						{
							if (bFirst)
							{
								bFirst = false;
							
								szString.append(CvWString::format(L"\n\nCloseness:"));
							}

							szString.append(CvWString::format(L"\n%s(%d) : %d ", kLoopPlayer.getName(), DEFAULT_PLAYER_CLOSENESS, iCloseness));
							szString.append(CvWString::format(L" [%d, ", kPlayer.AI_playerCloseness(eLoopPlayer, DEFAULT_PLAYER_CLOSENESS)));
							if (kPlayer.getTeam() != kLoopPlayer.getTeam())
							{
								szString.append(CvWString::format(L"%d]", GET_TEAM(kPlayer.getTeam()).AI_teamCloseness(kLoopPlayer.getTeam(), DEFAULT_PLAYER_CLOSENESS)));
							}
							else
							{
								szString.append(CvWString::format(L"-]"));
							}
							
						}
					}
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                       END                                                  */
/************************************************************************************************/
				}
			}

			int iAreaSiteBestValue = 0;
			int iNumAreaCitySites = kPlayer.AI_getNumAreaCitySites(pPlot->getArea(), iAreaSiteBestValue);
			int iOtherSiteBestValue = 0;
			int iNumOtherCitySites = (pPlot->waterArea() == NULL) ? 0 : kPlayer.AI_getNumAdjacentAreaCitySites(pPlot->waterArea()->getID(), pPlot->getArea(), iOtherSiteBestValue);

			szString.append(CvWString::format(L"\n\nArea Sites = %d (%d)", iNumAreaCitySites, iAreaSiteBestValue));
			szString.append(CvWString::format(L"\nOther Sites = %d (%d)", iNumOtherCitySites, iOtherSiteBestValue));


		}
		else if (pPlot->getOwner() != NO_PLAYER)
		{
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                      11/30/08                                jdog5000      */
/*                                                                                              */
/* Debug                                                                                        */
/************************************************************************************************/
/* original code
			for (int iI = 0; iI < GC.getNumCivicInfos(); iI++)
			{
				szString.append(CvWString::format(L"\n %s = %d", GC.getCivicInfo((CivicTypes)iI).getDescription(), GET_PLAYER(pPlot->getOwner()).AI_civicValue((CivicTypes)iI)));			
			}
*/
			if( bShift && !bAlt)
			{
				int* paiBonusClassRevealed;
				int* paiBonusClassUnrevealed;
				int* paiBonusClassHave;
				
				// ALN AITechValues Start
				std::vector< std::pair<TechTypes, int> > aTechValues;
				std::vector< std::pair<TechTypes, int> >::iterator it;
				// ALN AITechValues End
				
				paiBonusClassRevealed = new int[GC.getNumBonusClassInfos()];
				paiBonusClassUnrevealed = new int[GC.getNumBonusClassInfos()];
				paiBonusClassHave = new int[GC.getNumBonusClassInfos()];
				
				for (int iI = 0; iI < GC.getNumBonusClassInfos(); iI++)
				{
					paiBonusClassRevealed[iI] = 0;
					paiBonusClassUnrevealed[iI] = 0;
					paiBonusClassHave[iI] = 0;	    
				}
				
				for (int iI = 0; iI < GC.getNumBonusInfos(); iI++)
				{
					TechTypes eRevealTech = (TechTypes)GC.getBonusInfo((BonusTypes)iI).getTechReveal();
					BonusClassTypes eBonusClass = (BonusClassTypes)GC.getBonusInfo((BonusTypes)iI).getBonusClassType();
					if (eRevealTech != NO_TECH)
					{
						if ((GET_TEAM(pPlot->getTeam()).isHasTech(eRevealTech)))
						{
							paiBonusClassRevealed[eBonusClass]++;
						}
						else
						{
							paiBonusClassUnrevealed[eBonusClass]++;
						}

						if (GET_PLAYER(pPlot->getOwner()).getNumAvailableBonuses((BonusTypes)iI) > 0)
						{
							paiBonusClassHave[eBonusClass]++;                
						}
						else if (GET_PLAYER(pPlot->getOwner()).countOwnedBonuses((BonusTypes)iI) > 0)
						{
							paiBonusClassHave[eBonusClass]++;
						}
					}
				}

				/*
				int iPathLength;
				bool bDummy;

				for (int iI = 0; iI < GC.getNumTechInfos(); iI++)
				{
					iPathLength = GET_PLAYER(pPlot->getOwner()).findPathLength(((TechTypes)iI), false);

					if( iPathLength <= 3 && !GET_TEAM(pPlot->getTeam()).isHasTech((TechTypes)iI) )
					{
						szString.append(CvWString::format(L"\n%s(%d)=%7d", GC.getTechInfo((TechTypes)iI).getDescription(), iPathLength, GET_PLAYER(pPlot->getOwner()).AI_techValue((TechTypes)iI, 1, false, false, paiBonusClassRevealed, paiBonusClassUnrevealed, paiBonusClassHave)));
						szString.append(CvWString::format(L" (bld:%5d, ", GET_PLAYER(pPlot->getOwner()).AI_techBuildingValue((TechTypes)iI, 1, bDummy)));
						szString.append(CvWString::format(L"unt:%5d)", GET_PLAYER(pPlot->getOwner()).AI_techUnitValue((TechTypes)iI, 1, bDummy)));
					}
				}
				*/
				
				// ALN AITechValues Start
				int iPathLength;
				// bool bDummy;
				bool bLastInLine;
				int iTechValue;
				TechTypes eLoopTech;
				for (int iI = 0; iI < GC.getNumTechInfos(); iI++)
				{
					
					iPathLength = GET_PLAYER(pPlot->getOwner()).findPathLength(((TechTypes)iI), false);

					if( iPathLength <= 3 && !GET_TEAM(pPlot->getTeam()).isHasTech((TechTypes)iI) && GET_PLAYER(pPlot->getOwner()).canEverResearch((TechTypes)iI))
					{
						iTechValue = GET_PLAYER(pPlot->getOwner()).AI_techValue((TechTypes)iI, iPathLength, false, false, paiBonusClassRevealed, paiBonusClassUnrevealed, paiBonusClassHave, false);
						// szString.append(CvWString::format(L"\n%s(%d)=%d", GC.getTechInfo((TechTypes)iI).getDescription(), iPathLength, iTechValue));
						if (aTechValues.empty())
						{
							aTechValues.push_back(std::make_pair((TechTypes)iI, iTechValue));
						}
						else
						{
							bLastInLine = true;
							for (it = aTechValues.begin(); it != aTechValues.end(); ++it)
							{
								if (it != NULL)
								{
									if (iTechValue > (*it).second)
									{
										aTechValues.insert(it, std::make_pair((TechTypes)iI, iTechValue));
										bLastInLine = false;
										break;
									}
								}
							}
							if (bLastInLine)
							{
								aTechValues.push_back(std::make_pair((TechTypes)iI, iTechValue));
							}
						}
					}
				}
				it = aTechValues.begin();
				if (it != NULL)
				{
					int iBestTechValue = (*it).second;
					int iCount = 0;
					for (it = aTechValues.begin(); it != aTechValues.end(); ++it)
					{
						if (it != NULL)
						{
							iCount++;
							eLoopTech = (*it).first;
							iTechValue = (*it).second * 1000 / iBestTechValue;
							if (iCount <= 24)
							{
								iPathLength = GET_PLAYER(pPlot->getOwner()).findPathLength((eLoopTech), false);
								szString.append(CvWString::format(SETCOLR L"\n%s(%d)" ENDCOLR L" = %d.%d", TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getTechInfo(eLoopTech).getDescription(), iPathLength, iTechValue / 10, iTechValue % 10));
								// szString.append(CvWString::format(L" (bld:%d, ", GET_PLAYER(pPlot->getOwner()).AI_techBuildingValue(eLoopTech, 1, bDummy)));
								// szString.append(CvWString::format(L"unt:%d)", GET_PLAYER(pPlot->getOwner()).AI_techUnitValue(eLoopTech, 1, bDummy)));
							}
						}
					}
				}
				SAFE_DELETE_ARRAY(paiBonusClassRevealed);
				SAFE_DELETE_ARRAY(paiBonusClassUnrevealed);
				SAFE_DELETE_ARRAY(paiBonusClassHave);
				// aTechValues.clear();
			}
			else if( bAlt && !bShift )
			{
				if( pPlot->isHasPathToEnemyCity(pPlot->getTeam()) )
				{
					szString.append(CvWString::format(L"\nCan reach an enemy city\n\n"));	
				}
				else 
				{
					szString.append(CvWString::format(L"\nNo reachable enemy cities\n\n"));	
				}
				for (int iI = 0; iI < MAX_PLAYERS; ++iI)
				{
					if( GET_PLAYER((PlayerTypes)iI).isAlive() )
					{
						if( pPlot->isHasPathToPlayerCity(pPlot->getTeam(),(PlayerTypes)iI) )
						{
							szString.append(CvWString::format(SETCOLR L"Can reach %s city" ENDCOLR, TEXT_COLOR("COLOR_GREEN"), GET_PLAYER((PlayerTypes)iI).getName()));
						}
						else
						{
							szString.append(CvWString::format(SETCOLR L"Cannot reach any %s city" ENDCOLR, TEXT_COLOR("COLOR_NEGATIVE_TEXT"), GET_PLAYER((PlayerTypes)iI).getName()));
						}

						if( GET_TEAM(pPlot->getTeam()).isAtWar(GET_PLAYER((PlayerTypes)iI).getTeam()) )
						{
							szString.append(CvWString::format(L" (enemy)"));
						}
						szString.append(CvWString::format(L"\n"));
					}
					// ALN AITechValues End
				}
			}
			else if( bShift && bAlt )
			{
				for (int iI = 0; iI < GC.getNumCivicInfos(); iI++)
				{
					szString.append(CvWString::format(L"\n %s = %d", GC.getCivicInfo((CivicTypes)iI).getDescription(), GET_PLAYER(pPlot->getOwner()).AI_civicValue((CivicTypes)iI)));
					if (GET_PLAYER(pPlot->getOwner()).isCivic((CivicTypes)iI))
					{
						szString.append(CvWString::format(SETCOLR L" (active)" ENDCOLR, TEXT_COLOR("COLOR_HIGHLIGHT_TEXT")));
					}
				}
			}
			else if( pPlot->headUnitNode() == NULL )
			{
				std::vector<UnitAITypes> vecUnitAIs;

				if (pPlot->isWater())
				{
					szString.append(CvWString::format(SETCOLR L"Sea Unit AI Values:\n" ENDCOLR, TEXT_COLOR("COLOR_HIGHLIGHT_TEXT")));
					vecUnitAIs.push_back(UNITAI_ATTACK_SEA);
					vecUnitAIs.push_back(UNITAI_ASSAULT_SEA);
					vecUnitAIs.push_back(UNITAI_ESCORT_SEA);
					vecUnitAIs.push_back(UNITAI_PIRATE_SEA);
				}
				else if( pPlot->getFeatureType() != NO_FEATURE )
				{
					szString.append(CvWString::format(SETCOLR L"Defense Unit AI Values:\n" ENDCOLR, TEXT_COLOR("COLOR_HIGHLIGHT_TEXT")));
					vecUnitAIs.push_back(UNITAI_CITY_DEFENSE);
					vecUnitAIs.push_back(UNITAI_COUNTER);
					vecUnitAIs.push_back(UNITAI_CITY_COUNTER);
				}
				else
				{
					szString.append(CvWString::format(SETCOLR L"Attack Unit AI Values:\n" ENDCOLR, TEXT_COLOR("COLOR_HIGHLIGHT_TEXT")));
					vecUnitAIs.push_back(UNITAI_ATTACK);
					vecUnitAIs.push_back(UNITAI_ATTACK_CITY);
					vecUnitAIs.push_back(UNITAI_COUNTER);
				}

				CvCity* pCloseCity = GC.getMapINLINE().findCity(pPlot->getX_INLINE(), pPlot->getY_INLINE(), pPlot->getOwner(), NO_TEAM, true);

				if( pCloseCity != NULL )
				{
					for( uint iI = 0; iI < vecUnitAIs.size(); iI++ )
					{
						CvWString szTempString;
						getUnitAIString(szTempString, vecUnitAIs[iI]);
						szString.append(CvWString::format(L"\n  %s  ", szTempString.GetCString()));
						for( int iJ = 0; iJ < GC.getNumUnitClassInfos(); iJ++ )
						{
							UnitTypes eUnit = (UnitTypes)GC.getCivilizationInfo(GET_PLAYER(pPlot->getOwner()).getCivilizationType()).getCivilizationUnits((UnitClassTypes)iJ);
							if( eUnit != NO_UNIT && pCloseCity->canTrain(eUnit) )
							{
								int iValue = GET_PLAYER(pPlot->getOwner()).AI_unitValue(eUnit, vecUnitAIs[iI], pPlot->area());
								if( iValue > 0 )
								{
									szString.append(CvWString::format(L"\n %s = %d", GC.getUnitInfo(eUnit).getDescription(), iValue));
								}
							}
						}
					}
				}
			}
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                       END                                                  */
/************************************************************************************************/
		}
		return;	
	}
	else if (bShift && !bAlt && (gDLL->getChtLvl() > 0))
	{
		szString.append(GC.getTerrainInfo(pPlot->getTerrainType()).getDescription());

		if (pPlot->getTempTerrainTimer() > 0)
		{
			szString.append(CvWString::format(L" (Temp Terrain: %d turns left)", pPlot->getTempTerrainTimer()));
			szString.append(CvWString::format(L"\n --Real Terrain: %s", GC.getTerrainInfo(pPlot->getRealTerrainType()).getDescription()));
		}
		if (pPlot->getTempBonusTimer() > 0)
		{
			if (pPlot->getBonusType() == NO_BONUS)
			{
				szString.append(CvWString::format(L"\n Temp Bonus: NO_BONUS (%d turns left)", pPlot->getTempBonusTimer()));
			}
			else
			{
				szString.append(CvWString::format(L"\n Temp Bonus: %s (%d turns left)", GC.getBonusInfo(pPlot->getBonusType()).getDescription(), pPlot->getTempBonusTimer()));
			}
			if (pPlot->getRealBonusType() != NO_BONUS)
			{
				szString.append(CvWString::format(L"\n --Real Bonus: %s", GC.getBonusInfo(pPlot->getRealBonusType()).getDescription()));
			}
		}
		if (pPlot->getTempFeatureTimer() > 0)
		{
			if (pPlot->getFeatureType() == NO_FEATURE)
			{
				szString.append(CvWString::format(L"\n Temp Feature: NO_FEATURE (%d turns left)", pPlot->getTempFeatureTimer()));
			}
			else
			{
				szString.append(CvWString::format(L"\n Temp Feature: %s (%d turns left)", GC.getFeatureInfo(pPlot->getFeatureType()).getDescription(), pPlot->getTempFeatureTimer()));
			}
			if (pPlot->getRealFeatureType() != NO_FEATURE)
			{
				szString.append(CvWString::format(L"\n --Real Feature: %s", GC.getFeatureInfo(pPlot->getRealFeatureType()).getDescription()));
			}
		}
		if (pPlot->getTempImprovementTimer() > 0)
		{
			if (pPlot->getImprovementType() == NO_IMPROVEMENT)
			{
				szString.append(CvWString::format(L"\n Temp Improvement: NO_IMPROVEMENT (%d turns left)", pPlot->getTempImprovementTimer()));
			}
			else
			{
				szString.append(CvWString::format(L"\n Temp Improvement: %s (%d turns left)", GC.getImprovementInfo(pPlot->getImprovementType()).getDescription(), pPlot->getTempImprovementTimer()));
			}
			if (pPlot->getRealImprovementType() != NO_IMPROVEMENT)
			{
				szString.append(CvWString::format(L"\n --Real Improvement: %s", GC.getImprovementInfo(pPlot->getRealImprovementType()).getDescription()));
			}
		}
		if (pPlot->getTempRouteTimer() > 0)
		{
			if (pPlot->getRouteType() == NO_ROUTE)
			{
				szString.append(CvWString::format(L"\n Temp Route: NO_ROUTE (%d turns left)", pPlot->getTempRouteTimer()));
			}
			else
			{
				szString.append(CvWString::format(L"\n Temp Route %s (%d turns left)", GC.getRouteInfo(pPlot->getRouteType()).getDescription(), pPlot->getTempRouteTimer()));
			}
			if (pPlot->getRealRouteType() != NO_ROUTE)
			{
				szString.append(CvWString::format(L"\n --Real Route: %s", GC.getRouteInfo(pPlot->getRealRouteType()).getDescription()));
			}
		}

		FAssert((0 < GC.getNumBonusInfos()) && "GC.getNumBonusInfos() is not greater than zero but an array is being allocated in CvInterface::updateHelpStrings");
		for (iI = 0; iI < GC.getNumBonusInfos(); ++iI)
		{
			if (pPlot->isPlotGroupConnectedBonus(GC.getGameINLINE().getActivePlayer(), ((BonusTypes)iI)))
			{
				szString.append(NEWLINE);
				szString.append(GC.getBonusInfo((BonusTypes)iI).getDescription());
				szString.append(CvWString::format(L" (%d)", GET_PLAYER(GC.getGameINLINE().getActivePlayer()).AI_bonusVal((BonusTypes)iI)));
			}
		}

		if (pPlot->getPlotGroup(GC.getGameINLINE().getActivePlayer()) != NULL)
		{
			szTempBuffer.Format(L"\n(%d, %d) group: %d", pPlot->getX_INLINE(), pPlot->getY_INLINE(), pPlot->getPlotGroup(GC.getGameINLINE().getActivePlayer())->getID());
		}
		else
		{
			szTempBuffer.Format(L"\n(%d, %d) group: (-1, -1)", pPlot->getX_INLINE(), pPlot->getY_INLINE());
		}
		szString.append(szTempBuffer);

		szTempBuffer.Format(L"\nArea: %d", pPlot->getArea());
		szString.append(szTempBuffer);

		char tempChar = 'x';
		if(pPlot->getRiverNSDirection() == CARDINALDIRECTION_NORTH)
		{
			tempChar = 'N';
		}
		else if(pPlot->getRiverNSDirection() == CARDINALDIRECTION_SOUTH)
		{
			tempChar = 'S';
		}
		szTempBuffer.Format(L"\nNSRiverFlow: %c", tempChar);
		szString.append(szTempBuffer);

		tempChar = 'x';
		if(pPlot->getRiverWEDirection() == CARDINALDIRECTION_WEST)
		{
			tempChar = 'W';
		}
		else if(pPlot->getRiverWEDirection() == CARDINALDIRECTION_EAST)
		{
			tempChar = 'E';
		}
		szTempBuffer.Format(L"\nWERiverFlow: %c", tempChar);
		szString.append(szTempBuffer);

		// Choke value
		szTempBuffer.Format(L"\nChoke Value: %d", pPlot->getChokeValue());
		szString.append(szTempBuffer);

		// Canal value
		szTempBuffer.Format(L"\nCanal Value: %d", pPlot->getCanalValue());
		szString.append(szTempBuffer);

		if(pPlot->getRouteType() != NO_ROUTE)
		{
			szTempBuffer.Format(L"\nRoute: %s", GC.getRouteInfo(pPlot->getRouteType()).getDescription());
			szString.append(szTempBuffer);
		}

		if(pPlot->getRouteSymbol() != NULL)
		{
			szTempBuffer.Format(L"\nConnection: %i", gDLL->getRouteIFace()->getConnectionMask(pPlot->getRouteSymbol()));
			szString.append(szTempBuffer);
		}

		for (iI = 0; iI < MAX_PLAYERS; ++iI)
		{
			if (GET_PLAYER((PlayerTypes)iI).isAlive())
			{
				if (pPlot->getCulture((PlayerTypes)iI) > 0)
				{
					szTempBuffer.Format(L"\n%s Culture: %d", GET_PLAYER((PlayerTypes)iI).getName(), pPlot->getCulture((PlayerTypes)iI));
					szString.append(szTempBuffer);
				}
			}
		}

		PlayerTypes eActivePlayer = GC.getGameINLINE().getActivePlayer();
		int iActualFoundValue = pPlot->getFoundValue(eActivePlayer);
		int iCalcFoundValue = GET_PLAYER(eActivePlayer).AI_foundValue(pPlot->getX_INLINE(), pPlot->getY_INLINE(), -1, false);
		int iStartingFoundValue = GET_PLAYER(eActivePlayer).AI_foundValue(pPlot->getX_INLINE(), pPlot->getY_INLINE(), -1, true);

		
		//szString.append(CvWString::format(L"\nCity Radius Count: %d", pPlot->getCityRadiusCount()));
		szTempBuffer.Format(L"\nFound Value: %d, (%d, %d)", iActualFoundValue, iCalcFoundValue, iStartingFoundValue);
		szString.append(szTempBuffer);

		CvCity* pWorkingCity = pPlot->getWorkingCity();
		if (NULL != pWorkingCity)
		{
		    int iPlotIndex = pWorkingCity->getCityPlotIndex(pPlot);
            int iBuildValue = pWorkingCity->AI_getBestBuildValue(iPlotIndex);
            BuildTypes eBestBuild = pWorkingCity->AI_getBestBuild(iPlotIndex);

/************************************************************************************************/
/* BETTER_BTS_AI_MOD                      06/25/09                                jdog5000      */
/*                                                                                              */
/* Debug                                                                                        */
/************************************************************************************************/
			szString.append(NEWLINE);

			int iFoodMultiplier, iProductionMultiplier, iCommerceMultiplier, iDesiredFoodChange;
			pWorkingCity->AI_getYieldMultipliers( iFoodMultiplier, iProductionMultiplier, iCommerceMultiplier, iDesiredFoodChange );

			szTempBuffer.Format(L"\n%s yield multipliers: ", pWorkingCity->getName().c_str() );
			szString.append(szTempBuffer);
			szTempBuffer.Format(L"\n   Food %d, Prod %d, Com %d, DesFoodChange %d", iFoodMultiplier, iProductionMultiplier, iCommerceMultiplier, iDesiredFoodChange );
			szString.append(szTempBuffer);
			szTempBuffer.Format(L"\nTarget pop: %d, (%d good tiles)", pWorkingCity->AI_getTargetPopulation(), pWorkingCity->AI_countGoodPlots() );
			szString.append(szTempBuffer);

			ImprovementTypes eImprovement = pPlot->getImprovementType();

            if (NO_BUILD != eBestBuild)
            {
				
				if( GC.getBuildInfo(eBestBuild).getImprovement() != NO_IMPROVEMENT && eImprovement != NO_IMPROVEMENT && eImprovement != GC.getBuildInfo(eBestBuild).getImprovement() )
				{
					szTempBuffer.Format(SETCOLR L"\nBest Build: %s (%d) replacing %s" ENDCOLR, TEXT_COLOR("COLOR_RED"), GC.getBuildInfo(eBestBuild).getDescription(), iBuildValue, GC.getImprovementInfo(eImprovement).getDescription());
				}
				else
				{
					szTempBuffer.Format(SETCOLR L"\nBest Build: %s (%d)" ENDCOLR, TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getBuildInfo(eBestBuild).getDescription(), iBuildValue);
				}
				
                szString.append(szTempBuffer);
			}

			szTempBuffer.Format(L"\nBuild Values: ");
			szString.append(szTempBuffer);

			for (iI = 0; iI < GC.getNumImprovementInfos(); iI++)
			{
				if( pPlot->canHaveImprovement((ImprovementTypes)iI, pWorkingCity->getOwnerINLINE()) )
				{
					int iBuildValue = pWorkingCity->AI_getImprovementValue( pPlot, (ImprovementTypes)iI, iFoodMultiplier, iProductionMultiplier, iCommerceMultiplier, iDesiredFoodChange);
					//int iOldValue = pWorkingCity->AI_getImprovementValue( pPlot, (ImprovementTypes)iI, iFoodMultiplier, iProductionMultiplier, iCommerceMultiplier, iDesiredFoodChange);

					//szTempBuffer.Format(L"\n   %s : %d  (old %d)", GC.getImprovementInfo((ImprovementTypes)iI).getDescription(), iOtherBuildValue, iOldValue );
					if (iBuildValue != 0)
					{
						szTempBuffer.Format(L"\n   %s : %d", GC.getImprovementInfo((ImprovementTypes)iI).getDescription(), iBuildValue );
						szString.append(szTempBuffer);
					}
				}
			}

			/*
			szTempBuffer.Format(L"\nStandard Build Values: ");
			szString.append(szTempBuffer);

			for (iI = 0; iI < GC.getNumImprovementInfos(); iI++)
			{
				int iOtherBuildValue = pWorkingCity->AI_getImprovementValue( pPlot, (ImprovementTypes)iI, 100, 100, 100, 0);
				if( iOtherBuildValue > 0 )
				{
					szTempBuffer.Format(L"\n   %s : %d", GC.getImprovementInfo((ImprovementTypes)iI).getDescription(), iOtherBuildValue);
					szString.append(szTempBuffer);
				}
			}
			*/

			szString.append(NEWLINE);
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                       END                                                  */
/************************************************************************************************/		

		}

		/*{
			szTempBuffer.Format(L"\nStack Str: land=%d(%d), sea=%d(%d), air=%d(%d)",
				pPlot->AI_sumStrength(NO_PLAYER, NO_PLAYER, DOMAIN_LAND, false, false, false),
				pPlot->AI_sumStrength(NO_PLAYER, NO_PLAYER, DOMAIN_LAND, true, false, false),
				pPlot->AI_sumStrength(NO_PLAYER, NO_PLAYER, DOMAIN_SEA, false, false, false),
				pPlot->AI_sumStrength(NO_PLAYER, NO_PLAYER, DOMAIN_SEA, true, false, false),
				pPlot->AI_sumStrength(NO_PLAYER, NO_PLAYER, DOMAIN_AIR, false, false, false),
				pPlot->AI_sumStrength(NO_PLAYER, NO_PLAYER, DOMAIN_AIR, true, false, false));
			szString.append(szTempBuffer);
		}*/

		if (pPlot->getPlotCity() != NULL)
		{
			PlayerTypes ePlayer = pPlot->getOwnerINLINE();
			CvPlayerAI& kPlayer = GET_PLAYER(ePlayer);

			szString.append(CvWString::format(L"\n\nAI unit class weights ..."));
			for (iI = 0; iI < GC.getNumUnitClassInfos(); ++iI)
			{
				if (kPlayer.AI_getUnitClassWeight((UnitClassTypes)iI) != 0)
				{
					szString.append(CvWString::format(L"\n%s = %d", GC.getUnitClassInfo((UnitClassTypes)iI).getDescription(), kPlayer.AI_getUnitClassWeight((UnitClassTypes)iI)));
				}
			}
			szString.append(CvWString::format(L"\n\nalso unit combat type weights..."));
			for (iI = 0; iI < GC.getNumUnitCombatInfos(); ++iI)
			{
				if (kPlayer.AI_getUnitCombatWeight((UnitCombatTypes)iI) != 0)
				{
					szString.append(CvWString::format(L"\n%s = % d", GC.getUnitCombatInfo((UnitCombatTypes)iI).getDescription(), kPlayer.AI_getUnitCombatWeight((UnitCombatTypes)iI)));
				}
			}
		}
	}
	else if (!bShift && bAlt && (gDLL->getChtLvl() > 0))
	{
	    if (pPlot->isOwned())
	    {
            szTempBuffer.Format(L"\nThis player has %d area cities", pPlot->area()->getCitiesPerPlayer(pPlot->getOwnerINLINE()));
            szString.append(szTempBuffer);
            for (int iI = 0; iI < GC.getNumReligionInfos(); ++iI)
            {
                int iNeededMissionaries = GET_PLAYER(pPlot->getOwnerINLINE()).AI_neededMissionaries(pPlot->area(), ((ReligionTypes)iI));
                if (iNeededMissionaries > 0)
                {
                    szTempBuffer.Format(L"\nNeeded %c missionaries = %d", GC.getReligionInfo((ReligionTypes)iI).getChar(), iNeededMissionaries);
                    szString.append(szTempBuffer);
                }

				// Tholal AI - display religion values
				int iReligionValue = GET_PLAYER(pPlot->getOwnerINLINE()).AI_religionValue((ReligionTypes)iI);
				szTempBuffer.Format(L"\nValue %c: %d", GC.getReligionInfo((ReligionTypes)iI).getChar(), iReligionValue);
                szString.append(szTempBuffer);
				// End Tholal AI
            }

			int iOurDefense = GET_PLAYER(pPlot->getOwnerINLINE()).AI_getOurPlotStrength(pPlot, 0, true, false);
			int iEnemyOffense = GET_PLAYER(pPlot->getOwnerINLINE()).AI_getEnemyPlotStrength(pPlot, 2, false, false);
			if (iEnemyOffense > 0)
			{
				szString.append(CvWString::format(SETCOLR L"\nDanger: %.2f (%d/%d)" ENDCOLR, TEXT_COLOR("COLOR_NEGATIVE_TEXT"),
					(iEnemyOffense * 1.0f) / std::max(1, iOurDefense), iEnemyOffense, iOurDefense));
			}

			CvCity* pCity = pPlot->getPlotCity();
            if (pCity != NULL)
            {
                szTempBuffer.Format(L"\n\nCulture Pressure Value = %d", pCity->AI_calculateCulturePressure());
                szString.append(szTempBuffer);

                szTempBuffer.Format(L"\nWater World Percent = %d", pCity->AI_calculateWaterWorldPercent());
                szString.append(szTempBuffer);

				CvPlayerAI& kPlayer = GET_PLAYER(pCity->getOwnerINLINE());
				int iUnitCost = kPlayer.calculateUnitCost();
				int iTotalCosts = kPlayer.calculatePreInflatedCosts();
				int iUnitCostPercentage = (iUnitCost * 100) / std::max(1, iTotalCosts);
				szString.append(CvWString::format(L"\nUnit cost percentage: %d (%d / %d)", iUnitCostPercentage, iUnitCost, iTotalCosts));

				szString.append(CvWString::format(L"\nUpgrade all units: %d gold", kPlayer.AI_goldToUpgradeAllUnits()));

				szString.append(CvWString::format(L"\n\nRanks:"));
				szString.append(CvWString::format(L"\nPopulation:%d", pCity->findPopulationRank()));

				szString.append(CvWString::format(L"\nFood:%d(%d), ", pCity->findYieldRateRank(YIELD_FOOD), pCity->findBaseYieldRateRank(YIELD_FOOD)));
				szString.append(CvWString::format(L"Prod:%d(%d), ", pCity->findYieldRateRank(YIELD_PRODUCTION), pCity->findBaseYieldRateRank(YIELD_PRODUCTION)));
				szString.append(CvWString::format(L"Commerce:%d(%d)", pCity->findYieldRateRank(YIELD_COMMERCE), pCity->findBaseYieldRateRank(YIELD_COMMERCE)));

				szString.append(CvWString::format(L"\nGold:%d, ", pCity->findCommerceRateRank(COMMERCE_GOLD)));
				szString.append(CvWString::format(L"Research:%d, ", pCity->findCommerceRateRank(COMMERCE_RESEARCH)));
				szString.append(CvWString::format(L"Culture:%d", pCity->findCommerceRateRank(COMMERCE_CULTURE)));
			}
            szString.append(NEWLINE);
/************************************************************************************************/
/* REVOLUTION_MOD                         06/11/08                                jdog5000      */
/*                                                                                              */
/* Debug                                                                                        */
/************************************************************************************************/
			if (GC.getGameINLINE().isOption(GAMEOPTION_REVOLUTIONS))
			{
				szTempBuffer.Format(L"Stability Index: %d, Trend: %d",GET_PLAYER(pPlot->getOwner()).getStabilityIndex(),GET_PLAYER(pPlot->getOwner()).getStabilityIndex()-GET_PLAYER(pPlot->getOwner()).getStabilityIndexAverage());
				szString.append(szTempBuffer);
				szString.append(NEWLINE);
			}
/************************************************************************************************/
/* REVOLUTION_MOD                          END                                                  */
/************************************************************************************************/

            //AI strategies
            if (GET_PLAYER(pPlot->getOwner()).AI_isDoStrategy(AI_STRATEGY_DAGGER))
            {
                szTempBuffer.Format(L"Dagger, ");
                szString.append(szTempBuffer);
            }
			if (GET_PLAYER(pPlot->getOwner()).AI_isDoStrategy(AI_STRATEGY_CRUSH))
            {
                szTempBuffer.Format(L"Crush, ");
                szString.append(szTempBuffer);
			}
			if (GET_PLAYER(pPlot->getOwner()).AI_isDoStrategy(AI_STRATEGY_ALERT1))
            {
                szTempBuffer.Format(L"Alert1, ");
                szString.append(szTempBuffer);
			}
			if (GET_PLAYER(pPlot->getOwner()).AI_isDoStrategy(AI_STRATEGY_ALERT2))
            {
                szTempBuffer.Format(L"Alert2, ");
                szString.append(szTempBuffer);
			}
			if (GET_PLAYER(pPlot->getOwner()).AI_isDoStrategy(AI_STRATEGY_TURTLE))
            {
                szTempBuffer.Format(L"Turtle, ");
                szString.append(szTempBuffer);
			}
			if (GET_PLAYER(pPlot->getOwner()).AI_isDoStrategy(AI_STRATEGY_LAST_STAND))
            {
                szTempBuffer.Format(L"LastStand, ");
                szString.append(szTempBuffer);
			}
			if (GET_PLAYER(pPlot->getOwner()).AI_isDoStrategy(AI_STRATEGY_FINAL_WAR))
            {
                szTempBuffer.Format(L"FinalWar, ");
                szString.append(szTempBuffer);
            }
            if (GET_PLAYER(pPlot->getOwner()).AI_isDoStrategy(AI_STRATEGY_GET_BETTER_UNITS))
            {
                szTempBuffer.Format(L"GetBetterUnits, ");
                szString.append(szTempBuffer);
            }
            if (GET_PLAYER(pPlot->getOwner()).AI_isDoStrategy(AI_STRATEGY_FASTMOVERS))
            {
                szTempBuffer.Format(L"FastMovers, ");
                szString.append(szTempBuffer);
            }
            if (GET_PLAYER(pPlot->getOwner()).AI_isDoStrategy(AI_STRATEGY_LAND_BLITZ))
            {
                szTempBuffer.Format(L"LandBlitz, ");
                szString.append(szTempBuffer);
            }
			if (GET_PLAYER(pPlot->getOwner()).AI_isDoStrategy(AI_STRATEGY_AIR_BLITZ))
            {
                szTempBuffer.Format(L"AirBlitz, ");
                szString.append(szTempBuffer);
            }                        
 			if (GET_PLAYER(pPlot->getOwner()).AI_isDoStrategy(AI_STRATEGY_OWABWNW))
            {
                szTempBuffer.Format(L"OWABWNW, ");
                szString.append(szTempBuffer);
            }
			if (GET_PLAYER(pPlot->getOwner()).AI_isDoStrategy(AI_STRATEGY_PRODUCTION))
            {
                szTempBuffer.Format(L"Production, ");
                szString.append(szTempBuffer);
            }
            if (GET_PLAYER(pPlot->getOwner()).AI_isDoStrategy(AI_STRATEGY_MISSIONARY))
            {
                szTempBuffer.Format(L"Missionary, ");
                szString.append(szTempBuffer);
            }
            if (GET_PLAYER(pPlot->getOwner()).AI_isDoStrategy(AI_STRATEGY_BIG_ESPIONAGE))
            {
                szTempBuffer.Format(L"BigEspionage, ");
                szString.append(szTempBuffer);
            }
			if (GET_PLAYER(pPlot->getOwner()).AI_isDoStrategy(AI_STRATEGY_ECONOMY_FOCUS)) // K-Mod
			{
				szTempBuffer.Format(L"EconomyFocus, ");
				szString.append(szTempBuffer);
			}
                       
            //Area battle plans.
            if (pPlot->area()->getAreaAIType(pPlot->getTeam()) == AREAAI_OFFENSIVE)
            {
				szTempBuffer.Format(L"\n Area AI = OFFENSIVE");
            }
            else if (pPlot->area()->getAreaAIType(pPlot->getTeam()) == AREAAI_DEFENSIVE)
            {
				szTempBuffer.Format(L"\n Area AI = DEFENSIVE");
            }
            else if (pPlot->area()->getAreaAIType(pPlot->getTeam()) == AREAAI_MASSING)
            {
            	szTempBuffer.Format(L"\n Area AI = MASSING");
            }
            else if (pPlot->area()->getAreaAIType(pPlot->getTeam()) == AREAAI_ASSAULT)
            {
				szTempBuffer.Format(L"\n Area AI = ASSAULT");
            }
			else if (pPlot->area()->getAreaAIType(pPlot->getTeam()) == AREAAI_ASSAULT_MASSING)
            {
				szTempBuffer.Format(L"\n Area AI = ASSAULT_MASSING");
            }
            else if (pPlot->area()->getAreaAIType(pPlot->getTeam()) == AREAAI_NEUTRAL)
            {
            	szTempBuffer.Format(L"\n Area AI = NEUTRAL");
            }
            
			szString.append(szTempBuffer);
			szString.append(CvWString::format(L"\n\nNum Wars: %d + %d minor", GET_TEAM(pPlot->getTeam()).getAtWarCount(true), GET_TEAM(pPlot->getTeam()).getAtWarCount(false) - GET_TEAM(pPlot->getTeam()).getAtWarCount(true)));
			szString.append(CvWString::format(L"\nWarplans:"));
			for (int iK = 0; iK < MAX_TEAMS; ++iK)
			{
				TeamTypes eTeam = (TeamTypes)iK;

				if( GET_TEAM(eTeam).isAlive() || GET_TEAM(eTeam).isBarbarian() )
				{
					if( GET_TEAM(pPlot->getTeam()).AI_getWarPlan(eTeam) == WARPLAN_ATTACKED )
					{
						szString.append(CvWString::format(L"\n%s: ATTACKED", GET_TEAM(eTeam).getName().c_str()));
					}
					else if( GET_TEAM(pPlot->getTeam()).AI_getWarPlan(eTeam) == WARPLAN_ATTACKED_RECENT )
					{
						szString.append(CvWString::format(L"\n%s: ATTACKED_RECENT", GET_TEAM(eTeam).getName().c_str()));
					}
					else if( GET_TEAM(pPlot->getTeam()).AI_getWarPlan(eTeam) == WARPLAN_PREPARING_LIMITED )
					{
						szString.append(CvWString::format(L"\n%s: PREP_LIM", GET_TEAM(eTeam).getName().c_str()));
					}
					else if( GET_TEAM(pPlot->getTeam()).AI_getWarPlan(eTeam) == WARPLAN_PREPARING_TOTAL )
					{
						szString.append(CvWString::format(L"\n%s: PREP_TOTAL", GET_TEAM(eTeam).getName().c_str()));
					}
					else if( GET_TEAM(pPlot->getTeam()).AI_getWarPlan(eTeam) == WARPLAN_LIMITED )
					{
						szString.append(CvWString::format(L"\n%s: LIMITED", GET_TEAM(eTeam).getName().c_str()));
					}
					else if( GET_TEAM(pPlot->getTeam()).AI_getWarPlan(eTeam) == WARPLAN_TOTAL )
					{
						szString.append(CvWString::format(L"\n%s: TOTAL", GET_TEAM(eTeam).getName().c_str()));
					}
					else if( GET_TEAM(pPlot->getTeam()).AI_getWarPlan(eTeam) == WARPLAN_DOGPILE )
					{
						szString.append(CvWString::format(L"\n%s: DOGPILE", GET_TEAM(eTeam).getName().c_str()));
					}
					else if( GET_TEAM(pPlot->getTeam()).AI_getWarPlan(eTeam) == NO_WARPLAN )
					{
						if( GET_TEAM(pPlot->getTeam()).isAtWar(eTeam) ) 
						{
							szString.append(CvWString::format(SETCOLR L"\n%s: NO_WARPLAN!" ENDCOLR, TEXT_COLOR("COLOR_WARNING_TEXT"), GET_TEAM(eTeam).getName().c_str()));
						}
					}
				}

				if( GET_TEAM(pPlot->getTeam()).isMinorCiv() || GET_TEAM(pPlot->getTeam()).isBarbarian() )
				{
					if( pPlot->getTeam() != eTeam && !GET_TEAM(pPlot->getTeam()).isAtWar(eTeam) )
					{
						szString.append(CvWString::format(SETCOLR L"\n%s: minor/barb not at war!" ENDCOLR, TEXT_COLOR("COLOR_WARNING_TEXT"), GET_TEAM(eTeam).getName().c_str()));
					}
				}
			}
			
			CvCity* pTargetCity = pPlot->area()->getTargetCity(pPlot->getOwner());
			if( pTargetCity )
			{
				szString.append(CvWString::format(L"\nTarget City: %s", pTargetCity->getName().c_str()));
			}
			else
			{
				szString.append(CvWString::format(L"\nTarget City: None"));
			}
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                       END                                                  */
/************************************************************************************************/
	    }

		bool bFirst = true;
        for (iI = 0; iI < MAX_PLAYERS; ++iI)
        {
            PlayerTypes ePlayer = (PlayerTypes)iI;
			CvPlayerAI& kPlayer = GET_PLAYER(ePlayer);

			if (kPlayer.isAlive())
            {
				int iActualFoundValue = pPlot->getFoundValue(ePlayer);
                int iCalcFoundValue = kPlayer.AI_foundValue(pPlot->getX_INLINE(), pPlot->getY_INLINE(), -1, false);
                int iStartingFoundValue = kPlayer.AI_foundValue(pPlot->getX_INLINE(), pPlot->getY_INLINE(), -1, true);
                int iBestAreaFoundValue = pPlot->area()->getBestFoundValue(ePlayer);
                int iCitySiteBestValue;
                int iNumAreaCitySites = kPlayer.AI_getNumAreaCitySites(pPlot->getArea(), iCitySiteBestValue);

				if ((iActualFoundValue > 0 || iCalcFoundValue > 0 || iStartingFoundValue > 0)
					|| ((pPlot->getOwner() == iI) && (iBestAreaFoundValue > 0)))
				{
					if (bFirst)
					{
						szString.append(CvWString::format(SETCOLR L"\nFound Values:" ENDCOLR, TEXT_COLOR("COLOR_UNIT_TEXT")));
						bFirst = false;
					}

					szString.append(NEWLINE);

					bool bIsRevealed = pPlot->isRevealed(kPlayer.getTeam(), false);

					szString.append(CvWString::format(SETCOLR, TEXT_COLOR(bIsRevealed ? (((iActualFoundValue > 0) && (iActualFoundValue == iBestAreaFoundValue)) ? "COLOR_UNIT_TEXT" : "COLOR_ALT_HIGHLIGHT_TEXT") : "COLOR_HIGHLIGHT_TEXT")));

					if (!bIsRevealed)
					{
						szString.append(CvWString::format(L"("));
					}

					szString.append(CvWString::format(L"%s: %d", kPlayer.getName(), iActualFoundValue));

					if (!bIsRevealed)
					{
						szString.append(CvWString::format(L")"));
					}

					szString.append(CvWString::format(ENDCOLR));

					if (iCalcFoundValue > 0 || iStartingFoundValue > 0)
					{
						szTempBuffer.Format(L" (%d,%ds)", iCalcFoundValue, iStartingFoundValue);
						szString.append(szTempBuffer);
					}

					int iDeadlockCount = kPlayer.AI_countDeadlockedBonuses(pPlot);
					if (iDeadlockCount > 0)
					{
						szTempBuffer.Format(L", " SETCOLR L"d=%d" ENDCOLR, TEXT_COLOR("COLOR_NEGATIVE_TEXT"), iDeadlockCount);
						szString.append(szTempBuffer);
					}

					if (kPlayer.AI_isPlotCitySite(pPlot))
					{
						szTempBuffer.Format(L", " SETCOLR L"X" ENDCOLR, TEXT_COLOR("COLOR_UNIT_TEXT"));
						szString.append(szTempBuffer);
					}

					if ((iBestAreaFoundValue > 0) || (iNumAreaCitySites > 0))
					{
						int iBestFoundValue = kPlayer.findBestFoundValue();

						szTempBuffer.Format(L"\n  Area Best = %d, Best = %d, Sites = %d", iBestAreaFoundValue, iBestFoundValue, iNumAreaCitySites);
						szString.append(szTempBuffer);
					}
                }
            }
        }
	}
	else if (bShift && bAlt && (gDLL->getChtLvl() > 0))
	{
		CvCity*	pCity = pPlot->getWorkingCity();
		if (pCity != NULL)
		{
			// some functions we want to call are not in CvCity, worse some are protected, so made us a friend
			CvCityAI* pCityAI = static_cast<CvCityAI*>(pCity);

			bool bAvoidGrowth = pCity->AI_avoidGrowth();
			bool bIgnoreGrowth = pCityAI->AI_ignoreGrowth();

			// if we over the city, then do an array of all the plots
			if (pPlot->getPlotCity() != NULL)
			{

				// check avoid growth
				if (bAvoidGrowth || bIgnoreGrowth)
				{
					// red color
					szString.append(CvWString::format(SETCOLR, TEXT_COLOR("COLOR_NEGATIVE_TEXT")));

					if (bAvoidGrowth)
					{
						szString.append(CvWString::format(L"AvoidGrowth"));

						if (bIgnoreGrowth)
							szString.append(CvWString::format(L", "));
					}

					if (bIgnoreGrowth)
						szString.append(CvWString::format(L"IgnoreGrowth"));

					// end color
					szString.append(CvWString::format( ENDCOLR L"\n" ));
				}

				// if control key is down, ignore food
				bool bIgnoreFood = gDLL->ctrlKey();

				// line one is: blank, 20, 9, 10, blank
				setCityPlotYieldValueString(szString, pCity, -1, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 20, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 9, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 10, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				szString.append(L"\n");

				// line two is: 19, 8, 1, 2, 11
				setCityPlotYieldValueString(szString, pCity, 19, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 8, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 1, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 2, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 11, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				szString.append(L"\n");

				// line three is: 18, 7, 0, 3, 12
				setCityPlotYieldValueString(szString, pCity, 18, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 7, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 0, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 3, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 12, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				szString.append(L"\n");

				// line four is: 17, 6, 5, 4, 13
				setCityPlotYieldValueString(szString, pCity, 17, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 6, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 5, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 4, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 13, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				szString.append(L"\n");

				// line five is: blank, 16, 15, 14, blank
				setCityPlotYieldValueString(szString, pCity, -1, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 16, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 15, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);
				setCityPlotYieldValueString(szString, pCity, 14, bAvoidGrowth, bIgnoreGrowth, bIgnoreFood);

				// show specialist values too
				for (int iI = 0; iI < GC.getNumSpecialistInfos(); ++iI)
				{
					int iMaxThisSpecialist = pCity->getMaxSpecialistCount((SpecialistTypes) iI);
					int iSpecialistCount = pCity->getSpecialistCount((SpecialistTypes) iI);
					bool bUsingSpecialist = (iSpecialistCount > 0);
					bool bIsDefaultSpecialist = (iI == GC.getDefineINT("DEFAULT_SPECIALIST"));

					// can this city have any of this specialist?
					if (iMaxThisSpecialist > 0 || bIsDefaultSpecialist)
					{
						// start color
						if (pCity->getForceSpecialistCount((SpecialistTypes) iI) > 0)
							szString.append(CvWString::format(L"\n" SETCOLR, TEXT_COLOR("COLOR_NEGATIVE_TEXT")));
						else if (bUsingSpecialist)
							szString.append(CvWString::format(L"\n" SETCOLR, TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT")));
						else
							szString.append(CvWString::format(L"\n" SETCOLR, TEXT_COLOR("COLOR_HIGHLIGHT_TEXT")));

						// add name
						szString.append(GC.getSpecialistInfo((SpecialistTypes) iI).getDescription());

						// end color
						szString.append(CvWString::format( ENDCOLR ));

						// add usage
						szString.append(CvWString::format(L": (%d/%d) ", iSpecialistCount, iMaxThisSpecialist));

						// add value
						int iValue = pCityAI->AI_specialistValue(((SpecialistTypes) iI), bAvoidGrowth, /*bRemove*/ bUsingSpecialist);
						setYieldValueString(szString, iValue, /*bActive*/ bUsingSpecialist);
					}
				}
				{
					int iFood = GET_PLAYER(pCity->getOwnerINLINE()).AI_averageYieldMultiplier(YIELD_FOOD);
					int iHammer = GET_PLAYER(pCity->getOwnerINLINE()).AI_averageYieldMultiplier(YIELD_PRODUCTION);
					int iCommerce = GET_PLAYER(pCity->getOwnerINLINE()).AI_averageYieldMultiplier(YIELD_COMMERCE);

					szString.append(CvWString::format(L"\nPlayer:(f%d, h%d, c%d)", iFood, iHammer, iCommerce));

					iFood = pCity->AI_yieldMultiplier(YIELD_FOOD);
					iHammer = pCity->AI_yieldMultiplier(YIELD_PRODUCTION);
					iCommerce = pCity->AI_yieldMultiplier(YIELD_COMMERCE);

					szString.append(CvWString::format(L"\nCityBa:(f%d, h%d, c%d)", iFood, iHammer, iCommerce));

					iFood = pCityAI->AI_specialYieldMultiplier(YIELD_FOOD);
					iHammer = pCityAI->AI_specialYieldMultiplier(YIELD_PRODUCTION);
					iCommerce = pCityAI->AI_specialYieldMultiplier(YIELD_COMMERCE);

					szString.append(CvWString::format(L"\nCitySp:(f%d, h%d, c%d)", iFood, iHammer, iCommerce));

					szString.append(CvWString::format(L"\nExchange"));
					for (int iI = 0; iI < NUM_COMMERCE_TYPES; ++iI)
					{
						iCommerce = GET_PLAYER(pCity->getOwnerINLINE()).AI_averageCommerceExchange((CommerceTypes)iI);
						szTempBuffer.Format(L", %d%c", iCommerce, GC.getCommerceInfo((CommerceTypes) iI).getChar());
						szString.append(szTempBuffer);
					}

					if (GET_PLAYER(pCity->getOwnerINLINE()).AI_isFinancialTrouble())
					{
						szTempBuffer.Format(L"$$$!!!");
						szString.append(szTempBuffer);
					}
				}
			}
			else
			{
				bool bWorkingPlot = pCity->isWorkingPlot(pPlot);

				if (bWorkingPlot)
					szTempBuffer.Format( SETCOLR L"%s is working" ENDCOLR, TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT"), pCity->getName().GetCString());
				else
					szTempBuffer.Format( SETCOLR L"%s not working" ENDCOLR, TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), pCity->getName().GetCString());
				szString.append(szTempBuffer);

				int iValue = pCityAI->AI_plotValue(pPlot, bAvoidGrowth, /*bRemove*/ bWorkingPlot, /*bIgnoreFood*/ false, bIgnoreGrowth);
				int iJuggleValue = pCityAI->AI_plotValue(pPlot, bAvoidGrowth, /*bRemove*/ bWorkingPlot, false, bIgnoreGrowth, true);
				int iMagicValue = pCityAI->AI_getPlotMagicValue(pPlot, pCityAI->healthRate() == 0);

				szTempBuffer.Format(L"\nvalue = %d\njuggle value = %d\nmagic value = %d", iValue, iJuggleValue, iMagicValue);
				szString.append(szTempBuffer);
			}
		}

		// calc some bonus info
		if (GC.getGameINLINE().isDebugMode())
		{
			eBonus = pPlot->getBonusType();
		}
		else
		{
			eBonus = pPlot->getBonusType(GC.getGameINLINE().getActiveTeam());
		}
		if (eBonus != NO_BONUS)
		{
			szString.append(CvWString::format(L"\n%s values:", GC.getBonusInfo(eBonus).getDescription()));

			for (int iPlayerIndex = 0; iPlayerIndex < MAX_PLAYERS; iPlayerIndex++)
			{
				CvPlayerAI& kLoopPlayer = GET_PLAYER((PlayerTypes) iPlayerIndex);
				if (kLoopPlayer.isAlive())
				{
					szString.append(CvWString::format(L"\n %s: %d", kLoopPlayer.getName(), kLoopPlayer.AI_bonusVal(eBonus)));
				}
			}

			// show valuation of different mana types when looking at rawmana
			if (GC.getBonusInfo(eBonus).getBonusClassType() == GC.getDefineINT("BONUSCLASS_MANA_RAW"))
			{
				szString.append(CvWString::format(SETCOLR L"\nMana upgrade values:" ENDCOLR, TEXT_COLOR("COLOR_HIGHLIGHT_TEXT")));
				for (int iBonus = 0; iBonus < GC.getNumBonusInfos(); ++iBonus)
				{
					if (GC.getBonusInfo((BonusTypes)iBonus).getBonusClassType() == (GC.getDefineINT("BONUSCLASS_MANA")))
					{
						if (pPlot->isOwned())
						{
							szString.append(NEWLINE);
							szString.append(GC.getBonusInfo((BonusTypes)iBonus).getDescription());
							szString.append(CvWString::format(L" (%d): %d", GET_PLAYER(pPlot->getOwner()).getNumAvailableBonuses((BonusTypes)iBonus) , GET_PLAYER(pPlot->getOwner()).AI_bonusVal((BonusTypes)iBonus))); // GET_PLAYER(GC.getGameINLINE().getActivePlayer())
						}
					}
				}
			}
		}
	}
	else
	{
		eRevealOwner = pPlot->getRevealedOwner(GC.getGameINLINE().getActiveTeam(), true);

		if (eRevealOwner != NO_PLAYER)
		{
			if (pPlot->isActiveVisible(true))
			{
				szTempBuffer.Format(L"%d%% " SETCOLR L"%s" ENDCOLR, pPlot->calculateCulturePercent(eRevealOwner), GET_PLAYER(eRevealOwner).getPlayerTextColorR(), GET_PLAYER(eRevealOwner).getPlayerTextColorG(), GET_PLAYER(eRevealOwner).getPlayerTextColorB(), GET_PLAYER(eRevealOwner).getPlayerTextColorA(), GET_PLAYER(eRevealOwner).getCivilizationAdjective());

// BUG - City Controlled Plots - start
				if (getBugOptionBOOL("MiscHover__PlotWorkingCity", true, "BUG_PLOT_HOVER_WORKING_CITY"))
				{
					CvCity* pWorkingCity = pPlot->getWorkingCity();

					if (pWorkingCity != NULL && pWorkingCity->getOwnerINLINE() == GC.getGameINLINE().getActivePlayer())
					{
						szTempBuffer.append(L", ");

						if (pWorkingCity->isWorkingPlot(pPlot))
						{
							szTempBuffer.append(CvWString::format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), pWorkingCity->getName().GetCString()));
						}
						else
						{
							szTempBuffer.append(CvWString::format(L"%s", pWorkingCity->getName().GetCString()));
						}
					}
				}
// BUG - City Controlled Plots - end

				szString.append(szTempBuffer);
				szString.append(NEWLINE);

				for (int iPlayer = 0; iPlayer < MAX_PLAYERS; ++iPlayer)
				{
					if (iPlayer != eRevealOwner)
					{
						CvPlayer& kPlayer = GET_PLAYER((PlayerTypes)iPlayer);
/************************************************************************************************/
/* DEAD_PLAYER_CULTURE                      11/01/12                                lfgr        */
/*                                                                                              */
/* Original by Chronis                                                                          */
/************************************************************************************************/
/*
						if (kPlayer.isAlive() && pPlot->getCulture((PlayerTypes)iPlayer) > 0)
*/
						if (pPlot->getCulture((PlayerTypes)iPlayer) > 0)
/************************************************************************************************/
/* DEAD_PLAYER_CULTURE                     END                                                  */
/************************************************************************************************/
						{
							szTempBuffer.Format(L"%d%% " SETCOLR L"%s" ENDCOLR, pPlot->calculateCulturePercent((PlayerTypes)iPlayer), kPlayer.getPlayerTextColorR(), kPlayer.getPlayerTextColorG(), kPlayer.getPlayerTextColorB(), kPlayer.getPlayerTextColorA(), kPlayer.getCivilizationAdjective());
							szString.append(szTempBuffer);
							szString.append(NEWLINE);
						}
					}
				}

			}
			else
			{
				szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, GET_PLAYER(eRevealOwner).getPlayerTextColorR(), GET_PLAYER(eRevealOwner).getPlayerTextColorG(), GET_PLAYER(eRevealOwner).getPlayerTextColorB(), GET_PLAYER(eRevealOwner).getPlayerTextColorA(), GET_PLAYER(eRevealOwner).getCivilizationDescription());
				szString.append(szTempBuffer);
				szString.append(NEWLINE);
			}
		}

		iDefenseModifier = pPlot->defenseModifier((eRevealOwner != NO_PLAYER ? GET_PLAYER(eRevealOwner).getTeam() : NO_TEAM), true, true);
/** BUGFIX SEPHI
/** Include Defense Modifier from Improvement
**/
        if (pPlot->getImprovementType()!=NO_IMPROVEMENT)
        {
            iDefenseModifier+=GC.getImprovementInfo(pPlot->getImprovementType()).getDefenseModifier();
        }
/** BUGFIX END **/
		if (iDefenseModifier != 0)
		{
			szString.append(gDLL->getText("TXT_KEY_PLOT_BONUS", iDefenseModifier));
			szString.append(NEWLINE);
		}

		if (pPlot->getTerrainType() != NO_TERRAIN)
		{
			if (pPlot->isPeak())
			{
				szString.append(gDLL->getText("TXT_KEY_PLOT_PEAK"));
			}
			else
			{
				if (pPlot->isWater())
				{
					szTempBuffer.Format(SETCOLR, TEXT_COLOR("COLOR_WATER_TEXT"));
					szString.append(szTempBuffer);
				}

				if (pPlot->isHills())
				{
					szString.append(gDLL->getText("TXT_KEY_PLOT_HILLS"));
				}

				if (pPlot->getFeatureType() != NO_FEATURE)
				{
					szTempBuffer.Format(L"%s/", GC.getFeatureInfo(pPlot->getFeatureType()).getDescription());
					szString.append(szTempBuffer);
				}

				szString.append(GC.getTerrainInfo(pPlot->getTerrainType()).getDescription());

				if (pPlot->isWater())
				{
					szString.append(ENDCOLR);
				}
			}
		}

		if (pPlot->hasYield())
		{
			for (iI = 0; iI < NUM_YIELD_TYPES; ++iI)
			{
				iYield = pPlot->calculateYield(((YieldTypes)iI), true);

				if (iYield != 0)
				{
					szTempBuffer.Format(L", %d%c", iYield, GC.getYieldInfo((YieldTypes) iI).getChar());
					szString.append(szTempBuffer);
				}
			}
		}

		if (pPlot->isFreshWater())
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_PLOT_FRESH_WATER"));
		}

		if (pPlot->isLake())
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_PLOT_FRESH_WATER_LAKE"));
		}

		if (pPlot->isImpassable())
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_PLOT_IMPASSABLE"));
		}

		if (GC.getGameINLINE().isDebugMode())
		{
			eBonus = pPlot->getBonusType();
		}
		else
		{
			eBonus = pPlot->getBonusType(GC.getGameINLINE().getActiveTeam());
		}

		if (eBonus != NO_BONUS)
		{
			szTempBuffer.Format(L"%c " SETCOLR L"%s" ENDCOLR, GC.getBonusInfo(eBonus).getChar(), TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getBonusInfo(eBonus).getDescription());
			szString.append(NEWLINE);
			szString.append(szTempBuffer);

			if (GC.getBonusInfo(eBonus).getHealth() != 0)
			{
				szTempBuffer.Format(L", +%d%c", abs(GC.getBonusInfo(eBonus).getHealth()), ((GC.getBonusInfo(eBonus).getHealth() > 0) ? gDLL->getSymbolID(HEALTHY_CHAR): gDLL->getSymbolID(UNHEALTHY_CHAR)));
				szString.append(szTempBuffer);
			}

			if (GC.getBonusInfo(eBonus).getHappiness() != 0)
			{
				szTempBuffer.Format(L", +%d%c", abs(GC.getBonusInfo(eBonus).getHappiness()), ((GC.getBonusInfo(eBonus).getHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR): gDLL->getSymbolID(UNHAPPY_CHAR)));
				szString.append(szTempBuffer);
			}

			// Bugfix: Display requirement technology for bonuses provided by unique features.
			if ((pPlot->getImprovementType() != NO_IMPROVEMENT) && GC.getImprovementInfo(pPlot->getImprovementType()).isUnique() && !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isHasTech((TechTypes)GC.getBonusInfo(eBonus).getTechCityTrade())))
			{
				szString.append(gDLL->getText("TXT_KEY_PLOT_RESEARCH", GC.getTechInfo((TechTypes) GC.getBonusInfo(eBonus).getTechCityTrade()).getTextKeyWide()));
			}

			if ((pPlot->getImprovementType() == NO_IMPROVEMENT) || !(GC.getImprovementInfo(pPlot->getImprovementType()).isImprovementBonusTrade(eBonus)))
			{
				if (!(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isHasTech((TechTypes)GC.getBonusInfo(eBonus).getTechCityTrade())))
				{
					szString.append(gDLL->getText("TXT_KEY_PLOT_RESEARCH", GC.getTechInfo((TechTypes) GC.getBonusInfo(eBonus).getTechCityTrade()).getTextKeyWide()));
				}

				if (!pPlot->isCity())
				{
					for (iI = 0; iI < GC.getNumBuildInfos(); ++iI)
					{
						if (GC.getBuildInfo((BuildTypes) iI).getImprovement() != NO_IMPROVEMENT)
						{
							CvImprovementInfo& kImprovementInfo = GC.getImprovementInfo((ImprovementTypes) GC.getBuildInfo((BuildTypes) iI).getImprovement());
							if (kImprovementInfo.isImprovementBonusTrade(eBonus))
							{
//>>>>Unofficial Bug Fix: Modified by Denev 2010/05/04
//								if (pPlot->canHaveImprovement(((ImprovementTypes)(GC.getBuildInfo((BuildTypes) iI).getImprovement())), GC.getGameINLINE().getActiveTeam(), true))
								if (pPlot->canHaveImprovement(((ImprovementTypes)(GC.getBuildInfo((BuildTypes) iI).getImprovement())), GC.getGameINLINE().getActivePlayer(), true))
//<<<<Unofficial Bug Fix: End Modify
								{
									if (GET_TEAM(GC.getGameINLINE().getActiveTeam()).isHasTech((TechTypes)GC.getBuildInfo((BuildTypes) iI).getTechPrereq()))
									{
										szString.append(gDLL->getText("TXT_KEY_PLOT_REQUIRES", kImprovementInfo.getTextKeyWide()));
									}
									else if (GC.getBonusInfo(eBonus).getTechCityTrade() != GC.getBuildInfo((BuildTypes) iI).getTechPrereq())
									{
										szString.append(gDLL->getText("TXT_KEY_PLOT_RESEARCH", GC.getTechInfo((TechTypes) GC.getBuildInfo((BuildTypes) iI).getTechPrereq()).getTextKeyWide()));
									}

									bool bFirst = true;

									for (int k = 0; k < NUM_YIELD_TYPES; k++)
									{
										int iYieldChange = kImprovementInfo.getImprovementBonusYield(eBonus, k) + kImprovementInfo.getYieldChange(k);
										if (iYieldChange != 0)
										{
											if (iYieldChange > 0)
											{
												szTempBuffer.Format(L"+%d%c", iYieldChange, GC.getYieldInfo((YieldTypes)k).getChar());
											}
											else
											{
												szTempBuffer.Format(L"%d%c", iYieldChange, GC.getYieldInfo((YieldTypes)k).getChar());
											}
											setListHelp(szString, L"\n", szTempBuffer, L", ", bFirst);
											bFirst = false;
										}
									}

									if (!bFirst)
									{
										szString.append(gDLL->getText("TXT_KEY_BONUS_WITH_IMPROVEMENT", kImprovementInfo.getTextKeyWide()));
									}

									break;
								}
							}
						}
					}
				}
			}
			else if (!(pPlot->isBonusNetwork(GC.getGameINLINE().getActiveTeam())))
			{
				szString.append(gDLL->getText("TXT_KEY_PLOT_REQUIRES_ROUTE"));
			}

			if (!CvWString(GC.getBonusInfo(eBonus).getHelp()).empty())
			{
				szString.append(NEWLINE);
				szString.append(GC.getBonusInfo(eBonus).getHelp());
			}
		}

		eImprovement = pPlot->getRevealedImprovementType(GC.getGameINLINE().getActiveTeam(), true);

		if (eImprovement != NO_IMPROVEMENT)
		{
			szString.append(NEWLINE);
			szString.append(GC.getImprovementInfo(eImprovement).getDescription());

			bFound = false;

			for (iI = 0; iI < NUM_YIELD_TYPES; ++iI)
			{
				if (GC.getImprovementInfo(eImprovement).getIrrigatedYieldChange(iI) != 0)
				{
					bFound = true;
					break;
				}
			}

			if (bFound)
			{
				if (pPlot->isIrrigationAvailable())
				{
					szString.append(gDLL->getText("TXT_KEY_PLOT_IRRIGATED"));
				}
				else
				{
					szString.append(gDLL->getText("TXT_KEY_PLOT_NOT_IRRIGATED"));
				}
			}

			if (GC.getImprovementInfo(eImprovement).getImprovementUpgrade() != NO_IMPROVEMENT)
			{

//FfH: Modified by Kael 05/24/2008
				// lfgr fix 04/2020: Removed commented out code, added pPlot->getOwner() check
                if (GC.getImprovementInfo((ImprovementTypes) GC.getImprovementInfo(eImprovement).getImprovementUpgrade()).getPrereqCivilization() == NO_CIVILIZATION ||
						pPlot->getOwner() == NO_PLAYER ||
						GET_PLAYER(pPlot->getOwner()).getCivilizationType() == GC.getImprovementInfo((ImprovementTypes) GC.getImprovementInfo(eImprovement).getImprovementUpgrade()).getPrereqCivilization())
                {
                    // Super Forts begin *text* *upgrade*
					if ((pPlot->getUpgradeProgress() > 0) || (pPlot->isBeingWorked() && !GC.getImprovementInfo(eImprovement).isUpgradeRequiresFortify()))
					// if ((pPlot->getUpgradeProgress() > 0) || pPlot->isBeingWorked()) - Original Code
					// Super Forts end
                    {
                        iTurns = pPlot->getUpgradeTimeLeft(eImprovement, eRevealOwner);
                        szString.append(gDLL->getText("TXT_KEY_PLOT_IMP_UPGRADE", iTurns, GC.getImprovementInfo((ImprovementTypes) GC.getImprovementInfo(eImprovement).getImprovementUpgrade()).getTextKeyWide()));
                    }
                    else
                    {
                        if (GC.getImprovementInfo((ImprovementTypes) GC.getImprovementInfo(eImprovement).getImprovementUpgrade()).getPrereqCivilization() != NO_CIVILIZATION)
                        {
							szString.append(gDLL->getText("TXT_KEY_PLOT_WORK_TO_UPGRADE_PREREQ_CIV", GC.getImprovementInfo((ImprovementTypes) GC.getImprovementInfo(eImprovement).getImprovementUpgrade()).getTextKeyWide(), GC.getCivilizationInfo((CivilizationTypes)GC.getImprovementInfo((ImprovementTypes)GC.getImprovementInfo(eImprovement).getImprovementUpgrade()).getPrereqCivilization()).getDescription()));
                        }
						// Super Forts begin *text* *upgrade*
						else if (GC.getImprovementInfo(eImprovement).isUpgradeRequiresFortify())
						{
							szString.append(gDLL->getText("TXT_KEY_PLOT_FORTIFY_TO_UPGRADE", GC.getImprovementInfo((ImprovementTypes) GC.getImprovementInfo(eImprovement).getImprovementUpgrade()).getTextKeyWide()));
						}
						// Super Forts end
                        else
                        {
							szString.append(gDLL->getText("TXT_KEY_PLOT_WORK_TO_UPGRADE", GC.getImprovementInfo((ImprovementTypes) GC.getImprovementInfo(eImprovement).getImprovementUpgrade()).getTextKeyWide()));
                        }
                    }
                }
//FfH: End Modify

			}
		}

		if (pPlot->getRevealedRouteType(GC.getGameINLINE().getActiveTeam(), true) != NO_ROUTE)
		{
			szString.append(NEWLINE);
			szString.append(GC.getRouteInfo(pPlot->getRevealedRouteType(GC.getGameINLINE().getActiveTeam(), true)).getDescription());
		}
		
// BUG - Lat/Long Coordinates - start
		if (GET_TEAM(GC.getGameINLINE().getActiveTeam()).isMapCentering() && getBugOptionBOOL("MiscHover__LatLongCoords", true, "BUG_PLOT_HOVER_LAT_LONG"))
		{
			int iLong = pPlot->getLongitudeMinutes();
			bool bWest = false;

			if (iLong < 0)
			{
				iLong = abs(iLong);
				bWest = true;
			}
			int iLongDeg = iLong / 60;
			int iLongMin = iLong % 60;
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_LATLONG", iLongDeg, iLongMin));
			if (bWest)
			{
				szString.append(gDLL->getText("TXT_KEY_LATLONG_WEST"));
			}
			else
			{
				szString.append(gDLL->getText("TXT_KEY_LATLONG_EAST"));
			}
			
			int iLat = pPlot->getLatitudeMinutes();
			bool bSouth = false;

			if (iLat < 0)
			{
				iLat = abs(iLat);
				bSouth = true;
			}
			int iLatDeg = iLat / 60;
			int iLatMin = iLat % 60;
			szString.append(L", ");
			szString.append(gDLL->getText("TXT_KEY_LATLONG", iLatDeg, iLatMin));
			if (bSouth)
			{
				szString.append(gDLL->getText("TXT_KEY_LATLONG_SOUTH"));
			}
			else
			{
				szString.append(gDLL->getText("TXT_KEY_LATLONG_NORTH"));
			}
		}
// BUG - Lat/Long Coordinates - end

// BUG - Recommended Build - start
		BuildTypes eBestBuild = NO_BUILD;
		bool bBestPartiallyBuilt = false;

		if (getBugOptionBOOL("MiscHover__PlotRecommendedBuild", true, "BUG_PLOT_HOVER_RECOMMENDED_BUILD"))
		{
			CvCity* pWorkingCity = pPlot->getWorkingCity();

			if (pWorkingCity != NULL && pWorkingCity->getOwnerINLINE() == GC.getGameINLINE().getActivePlayer())
			{
				eBestBuild = pWorkingCity->AI_getBestBuild(pWorkingCity->getCityPlotIndex(pPlot));

				if (eBestBuild != NO_BUILD)
				{
					CvBuildInfo& kBestBuild = GC.getBuildInfo(eBestBuild);
					ImprovementTypes ePlotImprovement = pPlot->getImprovementType();

					if (ePlotImprovement != NO_IMPROVEMENT && ePlotImprovement == kBestBuild.getImprovement())
					{
						eBestBuild = NO_BUILD;
					}
					else if (kBestBuild.getRoute() != NO_ROUTE && (pPlot->isWater() || kBestBuild.getRoute() == pPlot->getRouteType()))
					{
						eBestBuild = NO_BUILD;
					}
				}
			}
		}
// BUG - Recommended Build - end

// BUG - Partial Builds - start
		if (pPlot->hasAnyBuildProgress() && getBugOptionBOOL("MiscHover__PartialBuilds", true, "BUG_PLOT_HOVER_PARTIAL_BUILDS"))
		{
			PlayerTypes ePlayer = GC.getGameINLINE().getActivePlayer();

			for (int iI = 0; iI < GC.getNumBuildInfos(); iI++)
			{
				if (pPlot->getBuildProgress((BuildTypes)iI) > 0 && pPlot->canBuild((BuildTypes)iI, ePlayer))
				{
					int iTurns = pPlot->getBuildTurnsLeft((BuildTypes)iI, GC.getGame().getActivePlayer());
					
					if (iTurns > 0 && iTurns < MAX_INT)
					{
						szString.append(NEWLINE);
						szString.append(GC.getBuildInfo((BuildTypes)iI).getDescription());
						szString.append(L": ");
						szString.append(gDLL->getText("TXT_KEY_ACTION_NUM_TURNS", iTurns));
					}
				}
			}
		}
// BUG - Partial Builds - end


/************************************************************************************************/
/* BETTER_BTS_AI_MOD                      07/11/08                                jdog5000      */
/*                                                                                              */
/* DEBUG                                                                                        */
/************************************************************************************************/
/* original code
		if (pPlot->getBlockadedCount(GC.getGameINLINE().getActiveTeam()) > 0)
*/
		if( GC.getGameINLINE().isDebugMode() )
		{
			bool bFirst = true;
			for (int iK = 0; iK < MAX_TEAMS; ++iK)
			{
				TeamTypes eTeam = (TeamTypes)iK;
				if( pPlot->getBlockadedCount(eTeam) > 0 && GET_TEAM(eTeam).isAlive() )
				{
					if( bFirst )
					{
						szString.append(CvWString::format(SETCOLR, TEXT_COLOR("COLOR_NEGATIVE_TEXT")));
						szString.append(NEWLINE);
						szString.append(gDLL->getText("TXT_KEY_PLOT_BLOCKADED"));
						szString.append(CvWString::format( ENDCOLR));

						szString.append(CvWString::format(L"Teams:"));
						bFirst = false;
					}
					szString.append(CvWString::format(L" %s,", GET_TEAM(eTeam).getName().c_str()));
				}
			}
		}
		else if (pPlot->getBlockadedCount(GC.getGameINLINE().getActiveTeam()) > 0)
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                       END                                                  */
/************************************************************************************************/
		{
			szString.append(CvWString::format(SETCOLR, TEXT_COLOR("COLOR_NEGATIVE_TEXT")));
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_PLOT_BLOCKADED"));
			szString.append(CvWString::format( ENDCOLR));
		}

	}

	if (pPlot->getFeatureType() != NO_FEATURE)
	{
		int iDamage = GC.getFeatureInfo(pPlot->getFeatureType()).getTurnDamage();

		if (iDamage > 0)
		{
			szString.append(CvWString::format(SETCOLR, TEXT_COLOR("COLOR_NEGATIVE_TEXT")));
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_PLOT_DAMAGE", iDamage));
			szString.append(CvWString::format( ENDCOLR));
		}
/*************************************************************************************************/
/* UNOFFICIAL_PATCH                       06/02/10                           LunarMongoose       */
/*                                                                                               */
/* User interface                                                                                */
/*************************************************************************************************/
		// Mongoose FeatureDamageFix
		else if (iDamage < 0)
		{
			szString.append(CvWString::format(SETCOLR, TEXT_COLOR("COLOR_POSITIVE_TEXT")));
			szString.append(NEWLINE);
			szString.append(gDLL->getText("TXT_KEY_PLOT_DAMAGE", iDamage));
			szString.append(CvWString::format( ENDCOLR));
		}
/*************************************************************************************************/
/* UNOFFICIAL_PATCH                         END                                                  */
/*************************************************************************************************/
	}

//FfH: Added by Kael 05/10/2008 - Check for minimum level requirement (ie, Circle of Brigit)
	if (pPlot->getMinLevel() != 0)
	{
			szString.append(NEWLINE);
            szString.append(gDLL->getText("TXT_KEY_PLOT_MIN_LEVEL", pPlot->getMinLevel()));
	}
//FfH: End Add

}


void CvGameTextMgr::setCityPlotYieldValueString(CvWStringBuffer &szString, CvCity* pCity, int iIndex, bool bAvoidGrowth, bool bIgnoreGrowth, bool bIgnoreFood)
{
	PROFILE_FUNC();

	CvPlot* pPlot = NULL;

//>>>>Unofficial Bug Fix: Modified by Denev 2010/04/04
//	if (iIndex >= 0 && iIndex < NUM_CITY_PLOTS)
	if (iIndex >= 0 && iIndex < pCity->getNumCityPlots())
//<<<<Unofficial Bug Fix: End Modify
		pPlot = pCity->getCityIndexPlot(iIndex);
	
	if (pPlot != NULL && pPlot->getWorkingCity() == pCity)
	{
		CvCityAI* pCityAI = static_cast<CvCityAI*>(pCity);
		bool bWorkingPlot = pCity->isWorkingPlot(iIndex);

		int iValue = pCityAI->AI_plotValue(pPlot, bAvoidGrowth, /*bRemove*/ bWorkingPlot, bIgnoreFood, bIgnoreGrowth);

		setYieldValueString(szString, iValue, /*bActive*/ bWorkingPlot);
	}
	else
		setYieldValueString(szString, 0, /*bActive*/ false, /*bMakeWhitespace*/ true);
}

void CvGameTextMgr::setYieldValueString(CvWStringBuffer &szString, int iValue, bool bActive, bool bMakeWhitespace)
{
	PROFILE_FUNC();

	static bool bUseFloats = false;

	if (bActive)
		szString.append(CvWString::format(SETCOLR, TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT")));
	else
		szString.append(CvWString::format(SETCOLR, TEXT_COLOR("COLOR_HIGHLIGHT_TEXT")));

	if (!bMakeWhitespace)
	{
		if (bUseFloats)
		{
			float fValue = ((float) iValue) / 10000;
			szString.append(CvWString::format(L"%2.3f " ENDCOLR, fValue));
		}
		else
			szString.append(CvWString::format(L"%05d  " ENDCOLR, iValue/10));
	}
	else
		szString.append(CvWString::format(L"           " ENDCOLR));
}

void CvGameTextMgr::setCityBarHelp(CvWStringBuffer &szString, CvCity* pCity)
{
	PROFILE_FUNC();

	CvWString szTempBuffer;
	bool bFirst;
	int iFoodDifference;
	int iProductionDiffNoFood;
	int iProductionDiffJustFood;
	int iRate;
	int iI;
// BUG - Base Production and Commerce - start
	bool bBaseValues = (gDLL->ctrlKey() && getBugOptionBOOL("CityBar__BaseValues", true, "BUG_CITYBAR_BASE_VALUES"));
// BUG - Base Production and Commerce - end

	iFoodDifference = pCity->foodDifference();

	szString.append(pCity->getName());

// BUG - Health - start
	if (getBugOptionBOOL("CityBar__Health", true, "BUG_CITYBAR_HEALTH"))
	{
		iRate = pCity->goodHealth() - pCity->badHealth();
		if (iRate > 0)
		{
			szTempBuffer.Format(L", %d %c", iRate, gDLL->getSymbolID(HEALTHY_CHAR));
			szString.append(szTempBuffer);
		}
		else if (iRate < 0)
		{
			szTempBuffer.Format(L", %d %c", -iRate, gDLL->getSymbolID(UNHEALTHY_CHAR));
			szString.append(szTempBuffer);
		}
	}
// BUG - Health - end

// BUG - Happiness - start
	if (getBugOptionBOOL("CityBar__Happiness", true, "BUG_CITYBAR_HAPPINESS"))
	{
		if (pCity->isDisorder())
		{
			int iAngryPop = pCity->angryPopulation();
			if (iAngryPop > 0)
			{
				szTempBuffer.Format(L", %d %c", iAngryPop, gDLL->getSymbolID(ANGRY_POP_CHAR));
				szString.append(szTempBuffer);
			}
		}
		else
		{
			iRate = pCity->happyLevel() - pCity->unhappyLevel();
			if (iRate > 0)
			{
				szTempBuffer.Format(L", %d %c", iRate, gDLL->getSymbolID(HAPPY_CHAR));
				szString.append(szTempBuffer);
			}
			else if (iRate < 0)
			{
				szTempBuffer.Format(L", %d %c", -iRate, gDLL->getSymbolID(UNHAPPY_CHAR));
				szString.append(szTempBuffer);
			}
		}
	}
// BUG - Happiness - end

// BUG - Hurry Anger Turns - start
	if (getBugOptionBOOL("CityBar__HurryAnger", true, "BUG_CITYBAR_HURRY_ANGER") && pCity->getOwnerINLINE() == GC.getGameINLINE().getActivePlayer())
	{
		iRate = pCity->getHurryAngerTimer();
		if (iRate > 0)
		{
			int iPop = ((iRate - 1) / pCity->flatHurryAngerLength() + 1) * GC.getDefineINT("HURRY_POP_ANGER");
			szTempBuffer.Format(L" (%d %c %d)", iPop, gDLL->getSymbolID(ANGRY_POP_CHAR), iRate);
			szString.append(szTempBuffer);
		}
	}
// BUG - Anger Anger Turns - end

// BUG - Draft Anger Turns - start
	if (getBugOptionBOOL("CityBar__DraftAnger", true, "BUG_CITYBAR_DRAFT_ANGER") && pCity->getOwnerINLINE() == GC.getGameINLINE().getActivePlayer())
	{
		iRate = pCity->getConscriptAngerTimer();
		if (iRate > 0)
		{
			int iPop = ((iRate - 1) / pCity->flatConscriptAngerLength() + 1) * GC.getDefineINT("CONSCRIPT_POP_ANGER");
			szTempBuffer.Format(L" (%d %c %d)", iPop, gDLL->getSymbolID(CITIZEN_CHAR), iRate);
			szString.append(szTempBuffer);
		}
	}
// BUG - Draft Anger Turns - end

// BUG - Food Assist - start
	if ((iFoodDifference != 0 || !pCity->isFoodProduction()) && getBugOptionBOOL("CityBar__FoodAssist", true, "BUG_CITYBAR_FOOD_ASSIST"))
	{
		if (iFoodDifference > 0)
		{
			szString.append(gDLL->getText("TXT_KEY_CITY_BAR_FOOD_GROW", iFoodDifference, pCity->getFood(), pCity->growthThreshold(), pCity->getFoodTurnsLeft()));
		}
		else if (iFoodDifference == 0)
		{
			szString.append(gDLL->getText("TXT_KEY_CITY_BAR_FOOD_STAGNATE", pCity->getFood(), pCity->growthThreshold()));
		}
		else if (pCity->getFood() + iFoodDifference >= 0)
		{
			int iTurnsToStarve = pCity->getFood() / -iFoodDifference + 1;
			szString.append(gDLL->getText("TXT_KEY_CITY_BAR_FOOD_SHRINK", iFoodDifference, pCity->getFood(), pCity->growthThreshold(), iTurnsToStarve));
		}
		else
		{
			szString.append(gDLL->getText("TXT_KEY_CITY_BAR_FOOD_STARVE", iFoodDifference, pCity->getFood(), pCity->growthThreshold()));
		}
	}
	else
	{
		// unchanged
		if (iFoodDifference <= 0)
		{
			szString.append(gDLL->getText("TXT_KEY_CITY_BAR_GROWTH", pCity->getFood(), pCity->growthThreshold()));
		}
		else
		{
			szString.append(gDLL->getText("TXT_KEY_CITY_BAR_FOOD_GROWTH", iFoodDifference, pCity->getFood(), pCity->growthThreshold(), pCity->getFoodTurnsLeft()));
		}
	}
// BUG - Food Assist - end

	if (pCity->getProductionNeeded() != MAX_INT)
	{
// BUG - Base Production - start
		int iBaseProductionDiffNoFood;
		if (bBaseValues)
		{
			iBaseProductionDiffNoFood = pCity->getBaseYieldRate(YIELD_PRODUCTION);
		}
		else
		{
			iBaseProductionDiffNoFood = pCity->getCurrentProductionDifference(true, false);
		}
// BUG - Base Production - end

		iProductionDiffNoFood = pCity->getCurrentProductionDifference(true, true);
		iProductionDiffJustFood = (pCity->getCurrentProductionDifference(false, true) - iProductionDiffNoFood);

		if (iProductionDiffJustFood > 0)
		{
// BUG - Base Production - start
			if ((iProductionDiffNoFood != iBaseProductionDiffNoFood) && getBugOptionBOOL("CityBar__BaseProduction", true, "BUG_CITYBAR_BASE_PRODUCTION"))
			{
				szString.append(gDLL->getText("TXT_KEY_CITY_BAR_FOOD_HAMMER_PRODUCTION_WITH_BASE", iProductionDiffJustFood, iProductionDiffNoFood, pCity->getProductionName(), pCity->getProduction(), pCity->getProductionNeeded(), pCity->getProductionTurnsLeft(), iBaseProductionDiffNoFood));
			}
			else
			{
				// unchanged
				szString.append(gDLL->getText("TXT_KEY_CITY_BAR_FOOD_HAMMER_PRODUCTION", iProductionDiffJustFood, iProductionDiffNoFood, pCity->getProductionName(), pCity->getProduction(), pCity->getProductionNeeded(), pCity->getProductionTurnsLeft()));
			}
// BUG - Base Production - end
		}
		else if (iProductionDiffNoFood > 0)
		{
// BUG - Base Production - start
			if ((iProductionDiffNoFood != iBaseProductionDiffNoFood) && getBugOptionBOOL("CityBar__BaseProduction", true, "BUG_CITYBAR_BASE_PRODUCTION"))
			{
				szString.append(gDLL->getText("TXT_KEY_CITY_BAR_HAMMER_PRODUCTION_WITH_BASE", iProductionDiffNoFood, pCity->getProductionName(), pCity->getProduction(), pCity->getProductionNeeded(), pCity->getProductionTurnsLeft(), iBaseProductionDiffNoFood));
			}
			else
			{
				// unchanged
				szString.append(gDLL->getText("TXT_KEY_CITY_BAR_HAMMER_PRODUCTION", iProductionDiffNoFood, pCity->getProductionName(), pCity->getProduction(), pCity->getProductionNeeded(), pCity->getProductionTurnsLeft()));
			}
// BUG - Base Production - end
		}
		else
		{
			szString.append(gDLL->getText("TXT_KEY_CITY_BAR_PRODUCTION", pCity->getProductionName(), pCity->getProduction(), pCity->getProductionNeeded()));
		}

// BUG - Building Actual Effects - start
		if (pCity->getOwnerINLINE() == GC.getGame().getActivePlayer() && getBugOptionBOOL("CityBar__BuildingActualEffects", true, "BUG_CITYBAR_BUILDING_ACTUAL_EFFECTS"))
		{
			if (pCity->isProductionBuilding())
			{
				BuildingTypes eBuilding = pCity->getProductionBuilding();
				CvWString szStart;

				szStart.Format(NEWLINE L"<img=%S size=24></img>", GC.getBuildingInfo(eBuilding).getButton());
				setBuildingActualEffects(szString, szStart, eBuilding, pCity, false);
			}
		}
// BUG - Building Actual Effects - end
	}
// BUG - Base Production - start
	else if (getBugOptionBOOL("CityBar__BaseProduction", true, "BUG_CITYBAR_BASE_PRODUCTION"))
	{
		int iOverflow = pCity->getOverflowProduction();
		int iBaseProductionDiffNoFood;
		if (bBaseValues)
		{
			iBaseProductionDiffNoFood = pCity->getBaseYieldRate(YIELD_PRODUCTION);
		}
		else
		{
			iBaseProductionDiffNoFood = pCity->getCurrentProductionDifference(true, false);
		}
		if (iOverflow > 0 || iBaseProductionDiffNoFood > 0)
		{
			if (iOverflow > 0)
			{
				szString.append(gDLL->getText("TXT_KEY_CITY_BAR_BASE_PRODUCTION_WITH_OVERFLOW", iOverflow, iBaseProductionDiffNoFood));
			}
			else
			{
				szString.append(gDLL->getText("TXT_KEY_CITY_BAR_BASE_PRODUCTION", iBaseProductionDiffNoFood));
			}
		}
	}
// BUG - Base Production - end

// BUG - Hurry Assist - start
	if (getBugOptionBOOL("CityBar__HurryAssist", true, "BUG_CITYBAR_HURRY_ASSIST") && pCity->getOwnerINLINE() == GC.getGameINLINE().getActivePlayer())
	{
		bool bFirstHurry = true;
		for (iI = 0; iI < GC.getNumHurryInfos(); iI++)
		{
			if (pCity->canHurry((HurryTypes)iI))
			{
				if (bFirstHurry)
				{
					szString.append(NEWLINE);
					szString.append("Hurry:");
					bFirstHurry = false;
				}
				bFirst = true;
				szString.append(L" (");
				int iPopulation = pCity->hurryPopulation((HurryTypes)iI);
				if (iPopulation > 0)
				{
					szTempBuffer.Format(L"%d %c", -iPopulation, gDLL->getSymbolID(CITIZEN_CHAR));
					setListHelp(szString, NULL, szTempBuffer, L", ", bFirst);
					bFirst = false;
				}
				int iGold = pCity->hurryGold((HurryTypes)iI);
				if (iGold > 0)
				{
					szTempBuffer.Format(L"%d %c", -iGold, GC.getCommerceInfo(COMMERCE_GOLD).getChar());
					setListHelp(szString, NULL, szTempBuffer, L", ", bFirst);
					bFirst = false;
				}
				int iOverflowProduction = 0;
				int iOverflowGold = 0;
				if (pCity->hurryOverflow((HurryTypes)iI, &iOverflowProduction, &iOverflowGold, getBugOptionBOOL("CityBar__HurryAssistIncludeCurrent", false, "BUG_CITYBAR_HURRY_ASSIST_INCLUDE_CURRENT")))
				{
					if (iOverflowProduction > 0)
					{
						szTempBuffer.Format(L"%d %c", iOverflowProduction, GC.getYieldInfo(YIELD_PRODUCTION).getChar());
						setListHelp(szString, NULL, szTempBuffer, L", ", bFirst);
						bFirst = false;
					}
					if (iOverflowGold > 0)
					{
						szTempBuffer.Format(L"%d %c", iOverflowGold, GC.getCommerceInfo(COMMERCE_GOLD).getChar());
						setListHelp(szString, NULL, szTempBuffer, L", ", bFirst);
						bFirst = false;
					}
				}
				szString.append(L")");
			}
		}
	}
// BUG - Hurry Assist - end

// BUG - Trade Detail - start
	if (getBugOptionBOOL("CityBar__TradeDetail", true, "BUG_CITYBAR_TRADE_DETAIL"))
	{
		int iTotalTrade = 0;
		int iDomesticTrade = 0;
		int iDomesticRoutes = 0;
		int iForeignTrade = 0;
		int iForeignRoutes = 0;

// BUG - Fractional Trade Routes - start
		bool bFractions = true;
// BUG - Fractional Trade Routes - end

		pCity->calculateTradeTotals(YIELD_COMMERCE, iDomesticTrade, iDomesticRoutes, iForeignTrade, iForeignRoutes, NO_PLAYER, !bFractions, bBaseValues);
		iTotalTrade = iDomesticTrade + iForeignTrade;

		bFirst = true;
		if (iTotalTrade != 0)
		{
			if (bFractions)
			{
				szTempBuffer.Format(L"%c: %d.%02d %c", gDLL->getSymbolID(TRADE_CHAR), iTotalTrade / 100, iTotalTrade % 100, GC.getYieldInfo(YIELD_COMMERCE).getChar());
			}
			else
			{
				szTempBuffer.Format(L"%c: %d %c", gDLL->getSymbolID(TRADE_CHAR), iTotalTrade, GC.getYieldInfo(YIELD_COMMERCE).getChar());
			}
			setListHelp(szString, NEWLINE, szTempBuffer, L", ", bFirst);
			bFirst = false;
		}
		if (iDomesticTrade != 0)
		{
			if (bFractions)
			{
				szTempBuffer.Format(L"%c: %d.%02d %c", gDLL->getSymbolID(STAR_CHAR), iDomesticTrade / 100, iDomesticTrade % 100, GC.getYieldInfo(YIELD_COMMERCE).getChar());
			}
			else
			{
				szTempBuffer.Format(L"%c: %d %c", gDLL->getSymbolID(STAR_CHAR), iDomesticTrade, GC.getYieldInfo(YIELD_COMMERCE).getChar());
			}
			setListHelp(szString, NEWLINE, szTempBuffer, L", ", bFirst);
			bFirst = false;
		}
		if (iForeignTrade != 0)
		{
			if (bFractions)
			{
				szTempBuffer.Format(L"%c: %d.%02d %c", gDLL->getSymbolID(SILVER_STAR_CHAR), iForeignTrade / 100, iForeignTrade % 100, GC.getYieldInfo(YIELD_COMMERCE).getChar());
			}
			else
			{
				szTempBuffer.Format(L"%c: %d %c", gDLL->getSymbolID(SILVER_STAR_CHAR), iForeignTrade, GC.getYieldInfo(YIELD_COMMERCE).getChar());
			}
			setListHelp(szString, NEWLINE, szTempBuffer, L", ", bFirst);
			bFirst = false;
		}
	}
// BUG - Trade Detail - end

	bFirst = true;

// BUG - Commerce - start
	if (getBugOptionBOOL("CityBar__Commerce", true, "BUG_CITYBAR_COMMERCE"))
	{
		if (bBaseValues)
		{
			iRate = pCity->getBaseYieldRate(YIELD_COMMERCE);
		}
		else
		{
			iRate = pCity->getYieldRate(YIELD_COMMERCE);
		}
		if (iRate != 0)
		{
			szTempBuffer.Format(L"%d %c", iRate, GC.getYieldInfo(YIELD_COMMERCE).getChar());
			setListHelp(szString, NEWLINE, szTempBuffer, L", ", bFirst);
			bFirst = false;
		}
	}
// BUG - Commerce - end

	for (iI = 0; iI < NUM_COMMERCE_TYPES; ++iI)
	{
// BUG - Base Values - start
		if (bBaseValues)
		{
			iRate = pCity->getBaseCommerceRateTimes100((CommerceTypes)iI);
		}
		else
		{
			// unchanged
			iRate = pCity->getCommerceRateTimes100((CommerceTypes)iI);
		}
// BUG - Base Values - end

		if (iRate != 0)
		{
			szTempBuffer.Format(L"%d.%02d %c", iRate/100, iRate%100, GC.getCommerceInfo((CommerceTypes)iI).getChar());
			setListHelp(szString, NEWLINE, szTempBuffer, L", ", bFirst);
			bFirst = false;
		}
	}

// BUG - Base Values - start
	if (bBaseValues)
	{
		iRate = pCity->getBaseGreatPeopleRate();
	}
	else
	{
		// unchanged
		iRate = pCity->getGreatPeopleRate();
	}
// BUG - Base Values - end

	if (iRate != 0)
	{
		szTempBuffer.Format(L"%d%c", iRate, gDLL->getSymbolID(GREAT_PEOPLE_CHAR));
		setListHelp(szString, NEWLINE, szTempBuffer, L", ", bFirst);
		bFirst = false;
	}

	if (!bFirst)
	{
		szString.append(gDLL->getText("TXT_KEY_PER_TURN"));
	}

	szString.append(NEWLINE);
	szString.append(gDLL->getText("INTERFACE_CITY_MAINTENANCE"));
// BUG - Base Values - start
	int iMaintenance;
	if (bBaseValues)
	{
		iMaintenance = pCity->calculateBaseMaintenanceTimes100();
	}
	else
	{
		// unchanged
		iMaintenance = pCity->getMaintenanceTimes100();
	}
// BUG - Base Values - end
	szString.append(CvWString::format(L" -%d.%02d %c", iMaintenance/100, iMaintenance%100, GC.getCommerceInfo(COMMERCE_GOLD).getChar()));

// BUG - Building Icons - start
	if (getBugOptionBOOL("CityBar__BuildingIcons", true, "BUG_CITYBAR_BUILDING_ICONS"))
	{
		bFirst = true;
		for (iI = 0; iI < GC.getNumBuildingInfos(); ++iI)
		{
			if (pCity->getNumRealBuilding((BuildingTypes)iI) > 0)
			{
				if (bFirst)
				{
					szString.append(NEWLINE);
					bFirst = false;
				}
				szTempBuffer.Format(L"<img=%S size=24></img>", GC.getBuildingInfo((BuildingTypes)iI).getButton());
				szString.append(szTempBuffer);
			}
		}
	}
	else
	{
		// unchanged
		bFirst = true;
		for (iI = 0; iI < GC.getNumBuildingInfos(); ++iI)
		{
			if (pCity->getNumRealBuilding((BuildingTypes)iI) > 0)
			{
				setListHelp(szString, NEWLINE, GC.getBuildingInfo((BuildingTypes)iI).getDescription(), L", ", bFirst);
				bFirst = false;
			}
		}
	}
// BUG - Building Icons - end

// BUG - Culture Turns - start
	int iCultureRate = pCity->getCommerceRateTimes100(COMMERCE_CULTURE);
	if (iCultureRate > 0 && getBugOptionBOOL("CityBar__CultureTurns", true, "BUG_CITYBAR_CULTURE_TURNS"))
	{
		if (pCity->getCultureLevel() != NO_CULTURELEVEL)
		{
			szString.append(gDLL->getText("TXT_KEY_CITY_BAR_CULTURE", pCity->getCulture(pCity->getOwnerINLINE()), pCity->getCultureThreshold(), GC.getCultureLevelInfo(pCity->getCultureLevel()).getTextKeyWide()));
		}
		else
		{
			szString.append(gDLL->getText("TXT_KEY_CITY_BAR_CULTURE_NO_LEVEL", pCity->getCulture(pCity->getOwnerINLINE()), pCity->getCultureThreshold()));
		}
		// all values are *100
		int iCulture = pCity->getCultureTimes100(pCity->getOwnerINLINE());
		int iCultureLeft = 100 * pCity->getCultureThreshold() - iCulture;
		int iCultureTurns = (iCultureLeft + iCultureRate - 1) / iCultureRate;
		szString.append(L" ");
		szString.append(gDLL->getText("INTERFACE_CITY_TURNS", iCultureTurns));
	}
	else
	{
		// unchanged
		if (pCity->getCultureLevel() != NO_CULTURELEVEL)
		{
			szString.append(gDLL->getText("TXT_KEY_CITY_BAR_CULTURE", pCity->getCulture(pCity->getOwnerINLINE()), pCity->getCultureThreshold(), GC.getCultureLevelInfo(pCity->getCultureLevel()).getTextKeyWide()));
		}
	}
// BUG - Culture Turns - end

// BUG - Great Person Turns - start
	int iGppRate = pCity->getGreatPeopleRate();
	if (iGppRate > 0 && getBugOptionBOOL("CityBar__GreatPersonTurns", true, "BUG_CITYBAR_GREAT_PERSON_TURNS"))
	{
		int iGpp = pCity->getGreatPeopleProgress();
		int iGppTotal = GET_PLAYER(pCity->getOwnerINLINE()).greatPeopleThreshold(false);
		szString.append(gDLL->getText("TXT_KEY_CITY_BAR_GREAT_PEOPLE", iGpp, iGppTotal));
		int iGppLeft = iGppTotal - iGpp;
		int iGppTurns = (iGppLeft + iGppRate - 1) / iGppRate;
		szString.append(L" ");
		szString.append(gDLL->getText("INTERFACE_CITY_TURNS", iGppTurns));
	}
	else
	{
		// unchanged
		if (pCity->getGreatPeopleProgress() > 0)
		{
			szString.append(gDLL->getText("TXT_KEY_CITY_BAR_GREAT_PEOPLE", pCity->getGreatPeopleProgress(), GET_PLAYER(pCity->getOwnerINLINE()).greatPeopleThreshold(false)));
		}
	}
// BUG - Great Person Turns - end

// BUG - Specialists - start
	if (getBugOptionBOOL("CityBar__Specialists", true, "BUG_CITYBAR_SPECIALISTS"))
	{
		// regular specialists
		bFirst = true;
		for (int iI = 0; iI < GC.getNumSpecialistInfos(); ++iI)
		{
			int iCount = pCity->getSpecialistCount((SpecialistTypes)iI);
			if (iCount > 0)
			{
				if (bFirst)
				{
					szString.append(NEWLINE);
					bFirst = false;
				}
				CvSpecialistInfo& kSpecialistInfo = GC.getSpecialistInfo((SpecialistTypes)iI);
				for (int iJ = 0; iJ < iCount; ++iJ)
				{
					szTempBuffer.Format(L"<img=%S size=24></img>", kSpecialistInfo.getButton());
					szString.append(szTempBuffer);
				}
			}
		}

		// free specialists (ToA, GL) and settled great people
		bFirst = true;
		for (int iI = 0; iI < GC.getNumSpecialistInfos(); ++iI)
		{
			int iCount = pCity->getFreeSpecialistCount((SpecialistTypes)iI);
			if (iCount > 0)
			{
				if (bFirst)
				{
					szString.append(NEWLINE);
					bFirst = false;
				}
				CvSpecialistInfo& kSpecialistInfo = GC.getSpecialistInfo((SpecialistTypes)iI);
				for (int iJ = 0; iJ < iCount; ++iJ)
				{
					szTempBuffer.Format(L"<img=%S size=24></img>", kSpecialistInfo.getButton());
					szString.append(szTempBuffer);
				}
			}
		}
	}
// BUG - Specialists - end

	int iNumUnits = pCity->plot()->countNumAirUnits(GC.getGameINLINE().getActiveTeam());
	if (pCity->getAirUnitCapacity(GC.getGameINLINE().getActiveTeam()) > 0 && iNumUnits > 0)
	{
		szString.append(NEWLINE);
		szString.append(gDLL->getText("TXT_KEY_CITY_BAR_AIR_UNIT_CAPACITY", iNumUnits, pCity->getAirUnitCapacity(GC.getGameINLINE().getActiveTeam())));
	}

// BUG - Revolt Chance - start
	if (getBugOptionBOOL("CityBar__RevoltChance", true, "BUG_CITYBAR_REVOLT_CHANCE"))
	{
		PlayerTypes eCulturalOwner = pCity->plot()->calculateCulturalOwner();

		if (eCulturalOwner != NO_PLAYER)
		{
			if (GET_PLAYER(eCulturalOwner).getTeam() != pCity->getTeam())
			{
				int iCityStrength = pCity->cultureStrength(eCulturalOwner);
				int iGarrison = pCity->cultureGarrison(eCulturalOwner);

				if (iCityStrength > iGarrison)
				{
					szTempBuffer.Format(L"%.2f", std::max(0.0f, (1.0f - (float)iGarrison / (float)iCityStrength)) * std::min(100.0f, (float)pCity->getRevoltTestProbability()));
					szString.append(NEWLINE);
					szString.append(gDLL->getText("TXT_KEY_MISC_CHANCE_OF_REVOLT", szTempBuffer.GetCString()));
				}
			}
		}
	}
// BUG - Revolt Chance - end

/************************************************************************************************/
/* REVOLUTIONDCM_MOD                         08/09/09                            Glider1        */
/*                                                                                              */
/*                                                                                              */
/************************************************************************************************/
		// RevolutionDCM start - Citybar revolution info
		if (GC.getGameINLINE().isOption(GAMEOPTION_REVOLUTIONS))
		{
			szString.append(NEWLINE);
			szString.append(L"<img=Art/Interface/Buttons/revbtn.dds size=23></img>");
			szString.append(CvWString::format(L":%d", pCity->getRevolutionIndex()));
			szString.append(NEWLINE);
		}
		// RevolutionDCM end
/************************************************************************************************/
/* REVOLUTIONDCM_MOD                         END                                 Glider1        */
/************************************************************************************************/

//FfH: Added by Kael 12/02/2007
    szString.append(NEWLINE);
    szString.append(gDLL->getText("TXT_KEY_CITY_BAR_CRIME", pCity->getCrime()));
//FfH: End Add

	szString.append(NEWLINE);

// BUG - Hide UI Instructions - start
	if (!getBugOptionBOOL("CityBar__HideInstructions", true, "BUG_CITYBAR_HIDE_INSTRUCTIONS"))
	{
		if (getBugOptionBOOL("CityBar__BaseValues", true, "BUG_CITYBAR_BASE_VALUES"))
		{
			szString.append(gDLL->getText("TXT_KEY_CITY_BAR_CTRL_BASE_VALUES"));
		}
		// unchanged
		szString.append(gDLL->getText("TXT_KEY_CITY_BAR_SELECT", pCity->getNameKey()));
		szString.append(gDLL->getText("TXT_KEY_CITY_BAR_SELECT_CTRL"));
		szString.append(gDLL->getText("TXT_KEY_CITY_BAR_SELECT_ALT"));
	}
// BUG - Hide UI Instructions - end
}


void CvGameTextMgr::parseTraits(CvWStringBuffer &szHelpString, TraitTypes eTrait, CivilizationTypes eCivilization, bool bDawnOfMan)
{
	PROFILE_FUNC();

	CvWString szTempBuffer;
	BuildingTypes eLoopBuilding;
	UnitTypes eLoopUnit;
	int iLast;
	int iI, iJ;
	CvWString szText;

	CvTraitInfo& kTraitInfo = GC.getTraitInfo(eTrait);

	// Trait Name
	szText = kTraitInfo.getDescription();
	if (bDawnOfMan)
	{
		szTempBuffer.Format(L"%s", szText.GetCString());
	}
	else
	{
		szTempBuffer.Format(NEWLINE SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT"), szText.GetCString());
	}
	szHelpString.append(szTempBuffer);

	if (!bDawnOfMan)
	{
		if (!CvWString(kTraitInfo.getHelp()).empty())
		{
			szHelpString.append(kTraitInfo.getHelp());
		}

		// iHealth
		if (kTraitInfo.getHealth() != 0)
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_HEALTH", kTraitInfo.getHealth()));
		}

		// iHappiness
		if (kTraitInfo.getHappiness() != 0)
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_HAPPINESS", kTraitInfo.getHappiness()));
		}

		// iMaxAnarchy
		if (kTraitInfo.getMaxAnarchy() != -1)
		{
			if (kTraitInfo.getMaxAnarchy() == 0)
			{
				szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_NO_ANARCHY"));
			}
			else
			{
				szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_MAX_ANARCHY", kTraitInfo.getMaxAnarchy()));
			}
		}

		// iUpkeepModifier
		if (kTraitInfo.getUpkeepModifier() != 0)
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_CIVIC_UPKEEP_MODIFIER", kTraitInfo.getUpkeepModifier()));
		}

		// iLevelExperienceModifier
		if (kTraitInfo.getLevelExperienceModifier() != 0)
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_CIVIC_LEVEL_MODIFIER", kTraitInfo.getLevelExperienceModifier()));
		}

		// iGreatPeopleRateModifier
		if (kTraitInfo.getGreatPeopleRateModifier() != 0)
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_GREAT_PEOPLE_MODIFIER", kTraitInfo.getGreatPeopleRateModifier()));
		}

		// iGreatGeneralRateModifier
		if (kTraitInfo.getGreatGeneralRateModifier() != 0)
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_GREAT_GENERAL_MODIFIER", kTraitInfo.getGreatGeneralRateModifier()));
		}

		if (kTraitInfo.getDomesticGreatGeneralRateModifier() != 0)
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_DOMESTIC_GREAT_GENERAL_MODIFIER", kTraitInfo.getDomesticGreatGeneralRateModifier()));
		}

		// Wonder Production Effects
		if ((kTraitInfo.getMaxGlobalBuildingProductionModifier() != 0)
			|| (kTraitInfo.getMaxTeamBuildingProductionModifier() != 0)
			|| (kTraitInfo.getMaxPlayerBuildingProductionModifier() != 0))
		{
			if ((kTraitInfo.getMaxGlobalBuildingProductionModifier() == kTraitInfo.getMaxTeamBuildingProductionModifier())
				&& 	(kTraitInfo.getMaxGlobalBuildingProductionModifier() == kTraitInfo.getMaxPlayerBuildingProductionModifier()))
			{
				szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_WONDER_PRODUCTION_MODIFIER", kTraitInfo.getMaxGlobalBuildingProductionModifier()));
			}
			else
			{
				if (kTraitInfo.getMaxGlobalBuildingProductionModifier() != 0)
				{
					szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_WORLD_WONDER_PRODUCTION_MODIFIER", kTraitInfo.getMaxGlobalBuildingProductionModifier()));
				}

				if (kTraitInfo.getMaxTeamBuildingProductionModifier() != 0)
				{
					szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_TEAM_WONDER_PRODUCTION_MODIFIER", kTraitInfo.getMaxTeamBuildingProductionModifier()));
				}

				if (kTraitInfo.getMaxPlayerBuildingProductionModifier() != 0)
				{
					szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_NATIONAL_WONDER_PRODUCTION_MODIFIER", kTraitInfo.getMaxPlayerBuildingProductionModifier()));
				}
			}
		}

		// ExtraYieldThresholds
		for (iI = 0; iI < NUM_YIELD_TYPES; ++iI)
		{
			if (kTraitInfo.getExtraYieldThreshold(iI) > 0)
			{
				szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_EXTRA_YIELD_THRESHOLDS", GC.getYieldInfo((YieldTypes) iI).getChar(), kTraitInfo.getExtraYieldThreshold(iI), GC.getYieldInfo((YieldTypes) iI).getChar()));
			}
			// Trade Yield Modifiers
			if (kTraitInfo.getTradeYieldModifier(iI) != 0)
			{
				szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_TRADE_YIELD_MODIFIERS", kTraitInfo.getTradeYieldModifier(iI), GC.getYieldInfo((YieldTypes) iI).getChar(), "YIELD"));
			}
		}

		// CommerceChanges
		for (iI = 0; iI < NUM_COMMERCE_TYPES; ++iI)
		{
			if (kTraitInfo.getCommerceChange(iI) != 0)
			{
				szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_COMMERCE_CHANGES", 	kTraitInfo.getCommerceChange(iI), GC.getCommerceInfo((CommerceTypes) iI).getChar(), "COMMERCE"));
			}

			if (kTraitInfo.getCommerceModifier(iI) != 0)
			{
				szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_COMMERCE_MODIFIERS", kTraitInfo.getCommerceModifier(iI), GC.getCommerceInfo((CommerceTypes) iI).getChar(), "COMMERCE"));
			}
		}

		// Free Promotions
		bool bFoundPromotion = false;
		szTempBuffer.clear();
		for (iI = 0; iI < GC.getNumPromotionInfos(); ++iI)
		{
			if (kTraitInfo.isFreePromotion(iI))
			{
				if (bFoundPromotion)
				{
					szTempBuffer += L", ";
				}

				szTempBuffer += CvWString::format(L"<link=literal>%s</link>", GC.getPromotionInfo((PromotionTypes) iI).getDescription());
				bFoundPromotion = true;
			}
		}

		if (bFoundPromotion)
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_FREE_PROMOTIONS", szTempBuffer.GetCString()));

			for (iJ = 0; iJ < GC.getNumUnitCombatInfos(); iJ++)
			{
				if (kTraitInfo.isFreePromotionUnitCombat(iJ))
				{
					szTempBuffer.Format(L"\n        %c<link=literal>%s</link>", gDLL->getSymbolID(BULLET_CHAR), GC.getUnitCombatInfo((UnitCombatTypes)iJ).getDescription());
					szHelpString.append(szTempBuffer);
				}
			}
		}

		// No Civic Maintenance
		for (iI = 0; iI < GC.getNumCivicOptionInfos(); ++iI)
		{
			if (GC.getCivicOptionInfo((CivicOptionTypes) iI).getTraitNoUpkeep(eTrait))
			{
				szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_NO_UPKEEP", GC.getCivicOptionInfo((CivicOptionTypes)iI).getTextKeyWide()));
			}
		}

		// Increase Building/Unit Production Speeds
		iLast = 0;
		for (iI = 0; iI < GC.getNumSpecialUnitInfos(); ++iI)
		{
			if (GC.getSpecialUnitInfo((SpecialUnitTypes) iI).getProductionTraits(eTrait) != 0)
			{
				if (GC.getSpecialUnitInfo((SpecialUnitTypes) iI).getProductionTraits(eTrait) == 100)
				{
					szText = gDLL->getText("TXT_KEY_TRAIT_DOUBLE_SPEED");
				}
				else
				{
					szText = gDLL->getText("TXT_KEY_TRAIT_PRODUCTION_MODIFIER", GC.getSpecialUnitInfo((SpecialUnitTypes) iI).getProductionTraits(eTrait));
				}
				setListHelp(szHelpString, szText.GetCString(), GC.getSpecialUnitInfo((SpecialUnitTypes) iI).getDescription(), L", ", (GC.getSpecialUnitInfo((SpecialUnitTypes) iI).getProductionTraits(eTrait) != iLast));
				iLast = GC.getSpecialUnitInfo((SpecialUnitTypes) iI).getProductionTraits(eTrait);
			}
		}

		// Unit Classes
		iLast = 0;
		for (iI = 0; iI < GC.getNumUnitClassInfos();++iI)
		{
			if (eCivilization == NO_CIVILIZATION)
			{
				eLoopUnit = ((UnitTypes)(GC.getUnitClassInfo((UnitClassTypes)iI).getDefaultUnitIndex()));
			}
			else
			{
				eLoopUnit = ((UnitTypes)(GC.getCivilizationInfo(eCivilization).getCivilizationUnits(iI)));
			}

			if (eLoopUnit != NO_UNIT && !isWorldUnitClass((UnitClassTypes)iI))
			{
				if (GC.getUnitInfo(eLoopUnit).getProductionTraits(eTrait) != 0)
				{
					if (GC.getUnitInfo(eLoopUnit).getProductionTraits(eTrait) == 100)
					{
						szText = gDLL->getText("TXT_KEY_TRAIT_DOUBLE_SPEED");
					}
					else
					{
						szText = gDLL->getText("TXT_KEY_TRAIT_PRODUCTION_MODIFIER", GC.getUnitInfo(eLoopUnit).getProductionTraits(eTrait));
					}
					CvWString szUnit;
					szUnit.Format(L"<link=literal>%s</link>", GC.getUnitInfo(eLoopUnit).getDescription());
					setListHelp(szHelpString, szText.GetCString(), szUnit, L", ", (GC.getUnitInfo(eLoopUnit).getProductionTraits(eTrait) != iLast));
					iLast = GC.getUnitInfo(eLoopUnit).getProductionTraits(eTrait);
				}
			}
		}

		// SpecialBuildings
		iLast = 0;
		for (iI = 0; iI < GC.getNumSpecialBuildingInfos(); ++iI)
		{
			if (GC.getSpecialBuildingInfo((SpecialBuildingTypes) iI).getProductionTraits(eTrait) != 0)
			{
				if (GC.getSpecialBuildingInfo((SpecialBuildingTypes) iI).getProductionTraits(eTrait) == 100)
				{
					szText = gDLL->getText("TXT_KEY_TRAIT_DOUBLE_SPEED");
				}
				else
				{
					szText = gDLL->getText("TXT_KEY_TRAIT_PRODUCTION_MODIFIER", GC.getSpecialBuildingInfo((SpecialBuildingTypes) iI).getProductionTraits(eTrait));
				}
				setListHelp(szHelpString, szText.GetCString(), GC.getSpecialBuildingInfo((SpecialBuildingTypes) iI).getDescription(), L", ", (GC.getSpecialBuildingInfo((SpecialBuildingTypes) iI).getProductionTraits(eTrait) != iLast));
				iLast = GC.getSpecialBuildingInfo((SpecialBuildingTypes) iI).getProductionTraits(eTrait);
			}
		}

		// Buildings
		iLast = 0;
		for (iI = 0; iI < GC.getNumBuildingClassInfos(); ++iI)
		{
			if (eCivilization == NO_CIVILIZATION)
			{
				eLoopBuilding = ((BuildingTypes)(GC.getBuildingClassInfo((BuildingClassTypes)iI).getDefaultBuildingIndex()));
			}
			else
			{
				eLoopBuilding = ((BuildingTypes)(GC.getCivilizationInfo(eCivilization).getCivilizationBuildings(iI)));
			}

			if (eLoopBuilding != NO_BUILDING && !isWorldWonderClass((BuildingClassTypes)iI))
			{
				if (GC.getBuildingInfo(eLoopBuilding).getProductionTraits(eTrait) != 0)
				{
					if (GC.getBuildingInfo(eLoopBuilding).getProductionTraits(eTrait) == 100)
					{
						szText = gDLL->getText("TXT_KEY_TRAIT_DOUBLE_SPEED");
					}
					else
					{
						szText = gDLL->getText("TXT_KEY_TRAIT_PRODUCTION_MODIFIER", GC.getBuildingInfo(eLoopBuilding).getProductionTraits(eTrait));
					}

					CvWString szBuilding;
					szBuilding.Format(L"<link=literal>%s</link>", GC.getBuildingInfo(eLoopBuilding).getDescription());
					setListHelp(szHelpString, szText.GetCString(), szBuilding, L", ", (GC.getBuildingInfo(eLoopBuilding).getProductionTraits(eTrait) != iLast));
					iLast = GC.getBuildingInfo(eLoopBuilding).getProductionTraits(eTrait);
				}
			}
		}

		// Buildings
		iLast = 0;
		for (iI = 0; iI < GC.getNumBuildingClassInfos(); ++iI)
		{
			if (eCivilization == NO_CIVILIZATION)
			{
				eLoopBuilding = ((BuildingTypes)(GC.getBuildingClassInfo((BuildingClassTypes)iI).getDefaultBuildingIndex()));
			}
			else
			{
				eLoopBuilding = ((BuildingTypes)(GC.getCivilizationInfo(eCivilization).getCivilizationBuildings(iI)));
			}

			if (eLoopBuilding != NO_BUILDING && !isWorldWonderClass((BuildingClassTypes)iI))
			{
				int iHappiness = GC.getBuildingInfo(eLoopBuilding).getHappinessTraits(eTrait);
				if (iHappiness != 0)
				{
					if (iHappiness > 0)
					{
						szText = gDLL->getText("TXT_KEY_TRAIT_BUILDING_HAPPINESS", iHappiness, gDLL->getSymbolID(HAPPY_CHAR));
					}
					else
					{
						szText = gDLL->getText("TXT_KEY_TRAIT_BUILDING_HAPPINESS", -iHappiness, gDLL->getSymbolID(UNHAPPY_CHAR));
					}

					CvWString szBuilding;
					szBuilding.Format(L"<link=literal>%s</link>", GC.getBuildingInfo(eLoopBuilding).getDescription());
					setListHelp(szHelpString, szText.GetCString(), szBuilding, L", ", (iHappiness != iLast));
					iLast = iHappiness;
				}
			}
		}

//FfH: Added by Kael 08/02/2007
		if (kTraitInfo.isAdaptive())
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_ADAPTIVE_HELP"));
		}
		if (kTraitInfo.isAgnostic())
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_AGNOSTIC_HELP"));
		}
		if (kTraitInfo.isAssimilation())
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_ASSIMILATION_HELP"));
		}
		if (kTraitInfo.isBarbarianAlly())
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_BARBARIAN_ALLY_HELP"));
		}
		if (kTraitInfo.isIgnoreFood())
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_IGNORE_FOOD_HELP"));
		}
		if (kTraitInfo.isInsane())
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_INSANE_HELP"));
		}
		if (kTraitInfo.isSprawling())
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_SPRAWLING_HELP"));
		}
		if (kTraitInfo.getMaxCities() != -1)
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_MAX_CITIES_HELP", (kTraitInfo.getMaxCities() + GC.getWorldInfo(GC.getMapINLINE().getWorldSize()).getMaxCitiesMod())));
		}
		if (kTraitInfo.getFreeXPFromCombat() != 0)
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_FREE_XP_FROM_COMBAT_HELP", kTraitInfo.getFreeXPFromCombat()));
		}
		if (kTraitInfo.getPillagingGold() != 0)
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_PILLAGING_GOLD_HELP", kTraitInfo.getPillagingGold()));
		}
		if (kTraitInfo.getStartingGold() != 0)
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_STARTING_GOLD_HELP", kTraitInfo.getStartingGold()));
		}
		if (kTraitInfo.getSummonDuration() != 0)
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_SUMMON_DURATION_HELP", kTraitInfo.getSummonDuration()));
		}
		if (kTraitInfo.getUpgradeCostModifier() != 0)
		{
			szHelpString.append(gDLL->getText("TXT_KEY_TRAIT_UPGRADE_COST_MODIFIER_HELP", kTraitInfo.getUpgradeCostModifier()));
		}
//FfH: End Add

	}

//	return szHelpString;
}


//
// parseLeaderTraits - SimpleCivPicker							// LOCALIZATION READY
//
void CvGameTextMgr::parseLeaderTraits(CvWStringBuffer &szHelpString, LeaderHeadTypes eLeader, CivilizationTypes eCivilization, bool bDawnOfMan, bool bCivilopediaText)
{
	PROFILE_FUNC();

	CvWString szTempBuffer;	// Formatting
	int iI;

	//	Build help string
	if (eLeader != NO_LEADER)
	{
		if (!bDawnOfMan)// && !bCivilopediaText)
		{
			szTempBuffer.Format( SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getLeaderHeadInfo(eLeader).getDescription());
			szHelpString.append(szTempBuffer);
		}

		FAssert((GC.getNumTraitInfos() > 0) &&
			"GC.getNumTraitInfos() is less than or equal to zero but is expected to be larger than zero in CvSimpleCivPicker::setLeaderText");

//FfH: Added by Kael 11/03/2007
        if (!bDawnOfMan)
        {
            szHelpString.append(NEWLINE);
        }
        szHelpString.append(gDLL->getText("TXT_KEY_ALIGNMENT", GC.getAlignmentInfo((AlignmentTypes)GC.getLeaderHeadInfo(eLeader).getAlignment()).getDescription()));
        if (eCivilization != NO_CIVILIZATION)
        {
			if (!bCivilopediaText) // suppress hero and world spell info in sevopedia (these are attached to the civ, not the leader)
			{
				if (GC.getCivilizationInfo(eCivilization).getHero() != NO_UNIT)
				{
					szHelpString.append(NEWLINE);
					szHelpString.append(gDLL->getText("TXT_KEY_HERO", GC.getUnitInfo((UnitTypes)GC.getCivilizationInfo(eCivilization).getHero()).getDescription()));
				}
				for (iI = 0; iI < GC.getNumSpellInfos(); ++iI)
				{
					if (GC.getSpellInfo((SpellTypes)iI).isGlobal())
					{
						if (GC.getSpellInfo((SpellTypes)iI).getCivilizationPrereq() == eCivilization)
						{
							szHelpString.append(NEWLINE);
							szHelpString.append(gDLL->getText("TXT_KEY_GLOBAL_SPELL", GC.getSpellInfo((SpellTypes)iI).getDescription()));
						}
					}
				}
			}
            if (bDawnOfMan)
            {
                szHelpString.append(NEWLINE);
            }
        }
//FfH: End Add

		bool bFirst = true;
		for (iI = 0; iI < GC.getNumTraitInfos(); ++iI)
		{
			if (GC.getLeaderHeadInfo(eLeader).hasTrait(iI))
			{
				if (!bFirst)
				{
					if (bDawnOfMan)
					{
						szHelpString.append(L", ");
					}
				}
				else
				{
					bFirst = false;
				}
				parseTraits(szHelpString, ((TraitTypes)iI), eCivilization, bDawnOfMan);
			}
		}
	}
	else
	{
		//	Random leader
		szTempBuffer.Format( SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), gDLL->getText("TXT_KEY_TRAIT_PLAYER_UNKNOWN").c_str());
		szHelpString.append(szTempBuffer);
	}

//	return szHelpString;
}

//FfH: Added by Kael 08/08/2007
void CvGameTextMgr::parseLeaderTraits(CvWStringBuffer &szHelpString, PlayerTypes ePlayer)
{
//	CvWString szHelpString;		// Final String Storage
	wchar szTempBuffer[1024];	// Formatting
	int iI;
	LeaderHeadTypes eLeader;
	CivilizationTypes eCivilization;

	//	Build help string
	if (GET_PLAYER(ePlayer).getLeaderType() != NO_LEADER)
	{
		eLeader = GET_PLAYER(ePlayer).getLeaderType();
		eCivilization = GET_PLAYER(ePlayer).getCivilizationType();

		swprintf(szTempBuffer,  SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getLeaderHeadInfo(eLeader).getDescription());
        szHelpString.append(szTempBuffer);

		FAssert((GC.getNumTraitInfos() > 0) &&
			"GC.getNumTraitInfos() is less than or equal to zero but is expected to be larger than zero in CvSimpleCivPicker::setLeaderText");

		for (iI = 0; iI < GC.getNumTraitInfos(); iI++)
		{
			if (GET_PLAYER(ePlayer).hasTrait((TraitTypes)iI))
			{
				parseTraits(szHelpString, ((TraitTypes)iI), eCivilization, false);
			}
		}
	}
	else
	{
		//	Random leader
		swprintf(szTempBuffer,  SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), gDLL->getText("TXT_KEY_TRAIT_PLAYER_UNKNOWN").c_str());
        szHelpString.append(szTempBuffer);
	}

//	return szHelpString;
}
//FfH: End Add

//
// parseLeaderTraits - SimpleCivPicker							// LOCALIZATION READY
//
void CvGameTextMgr::parseLeaderShortTraits(CvWStringBuffer &szHelpString, LeaderHeadTypes eLeader)
{
	PROFILE_FUNC();

	int iI;

	//	Build help string
	if (eLeader != NO_LEADER)
	{
		FAssert((GC.getNumTraitInfos() > 0) &&
			"GC.getNumTraitInfos() is less than or equal to zero but is expected to be larger than zero in CvSimpleCivPicker::setLeaderText");

		bool bFirst = true;
		for (iI = 0; iI < GC.getNumTraitInfos(); ++iI)
		{
			if (GC.getLeaderHeadInfo(eLeader).hasTrait(iI))
			{
				if (!bFirst)
				{
					szHelpString.append(L"/");
				}
				szHelpString.append(gDLL->getText(GC.getTraitInfo((TraitTypes)iI).getShortDescription()));
				bFirst = false;
			}
		}
	}
	else
	{
		//	Random leader
		szHelpString.append(CvWString("???/???"));
	}

	//	return szHelpString;
}

//
// Build Civilization Info Help Text
//
void CvGameTextMgr::parseCivInfos(CvWStringBuffer &szInfoText, CivilizationTypes eCivilization, bool bDawnOfMan, bool bLinks)
{
	PROFILE_FUNC();

	CvWString szBuffer;
	CvWString szTempString;
	CvWString szText;
	UnitTypes eDefaultUnit;
	UnitTypes eUniqueUnit;
	BuildingTypes eDefaultBuilding;
	BuildingTypes eUniqueBuilding;

	if (eCivilization != NO_CIVILIZATION)
	{
		if (!bDawnOfMan)
		{
			// Civ Name
			szBuffer.Format(SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getCivilizationInfo(eCivilization).getDescription());
			szInfoText.append(szBuffer);

			// Free Techs
			szBuffer.Format(NEWLINE SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT"), gDLL->getText("TXT_KEY_FREE_TECHS").GetCString());
			szInfoText.append(szBuffer);

			bool bFound = false;
			for (int iI = 0; iI < GC.getNumTechInfos(); ++iI)
			{
				if (GC.getCivilizationInfo(eCivilization).isCivilizationFreeTechs(iI))
				{
					bFound = true;
					// Add Tech
					szText.Format((bLinks ? L"<link=literal>%s</link>" : L"%s"), GC.getTechInfo((TechTypes)iI).getDescription());
					szBuffer.Format(L"%s  %c%s", NEWLINE, gDLL->getSymbolID(BULLET_CHAR), szText.GetCString());
					szInfoText.append(szBuffer);
				}
			}

			if (!bFound)
			{
				szBuffer.Format(L"%s  %s", NEWLINE, gDLL->getText("TXT_KEY_FREE_TECHS_NO").GetCString());
				szInfoText.append(szBuffer);
			}
		}

//FfH: Added by Kael 09/02/2008
        //Civ Trait
        if (GC.getCivilizationInfo(eCivilization).getCivTrait() != NO_TRAIT)
        {
            szText = gDLL->getText("TXT_KEY_CIV_TRAIT");
            if (bDawnOfMan)
            {
                szTempString.Format(L"%s:", szText.GetCString());
                szInfoText.append(szTempString);
                szBuffer.Format(L" %s\n", GC.getTraitInfo((TraitTypes)GC.getCivilizationInfo(eCivilization).getCivTrait()).getDescription());
                szInfoText.append(szBuffer);
            }
            else
            {
                szBuffer.Format(NEWLINE SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT"), gDLL->getText("TXT_KEY_CIV_TRAIT").GetCString());
                szInfoText.append(szBuffer);
                szText.Format((bLinks ? L"%s" : L"%s"), GC.getTraitInfo((TraitTypes)GC.getCivilizationInfo(eCivilization).getCivTrait()).getDescription());
                szBuffer.Format(L"%s  %c%s", NEWLINE, gDLL->getSymbolID(BULLET_CHAR), szText.GetCString());
                szInfoText.append(szBuffer);
            }
        }

        //Civ Hero
        if (GC.getCivilizationInfo(eCivilization).getHero() != NO_UNIT)
        {
            szText = gDLL->getText("TXT_KEY_HERO_PEDIA");
            if (bDawnOfMan)
            {
                szTempString.Format(L"%s:", szText.GetCString());
                szInfoText.append(szTempString);
                szBuffer.Format(L" <link=literal>%s</link>\n", GC.getUnitInfo((UnitTypes)GC.getCivilizationInfo(eCivilization).getHero()).getDescription());
                szInfoText.append(szBuffer);
            }
            else
            {
                szBuffer.Format(NEWLINE SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT"), gDLL->getText("TXT_KEY_HERO_PEDIA").GetCString());
                szInfoText.append(szBuffer);
                szText.Format((bLinks ? L"<link=literal>%s</link>" : L"%s"), GC.getUnitInfo((UnitTypes)GC.getCivilizationInfo(eCivilization).getHero()).getDescription());
                szBuffer.Format(L"%s  %c%s", NEWLINE, gDLL->getSymbolID(BULLET_CHAR), szText.GetCString());
                szInfoText.append(szBuffer);
            }
        }

        //World Spell
        szText = gDLL->getText("TXT_KEY_GLOBAL_SPELL_PEDIA");
        if (bDawnOfMan)
        {
            szTempString.Format(L"%s:", szText.GetCString());
            szInfoText.append(szTempString);
            for (int iI = 0; iI < GC.getNumSpellInfos(); ++iI)
            {
                if (GC.getSpellInfo((SpellTypes)iI).isGlobal())
                {
                    if (GC.getSpellInfo((SpellTypes)iI).getCivilizationPrereq() == eCivilization)
                    {
                        szBuffer.Format(L" <link=literal>%s</link>\n", GC.getSpellInfo((SpellTypes)iI).getDescription());
                        szInfoText.append(szBuffer);
                    }
                }
            }
        }
        else
        {
			szBuffer.Format(NEWLINE SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT"), gDLL->getText("TXT_KEY_GLOBAL_SPELL_PEDIA").GetCString());
			szInfoText.append(szBuffer);
            for (int iI = 0; iI < GC.getNumSpellInfos(); ++iI)
            {
                if (GC.getSpellInfo((SpellTypes)iI).isGlobal())
                {
                    if (GC.getSpellInfo((SpellTypes)iI).getCivilizationPrereq() == eCivilization)
                    {
                        szText.Format((bLinks ? L"<link=literal>%s</link>" : L"%s"), GC.getSpellInfo((SpellTypes)iI).getDescription());
                        szBuffer.Format(L"%s  %c%s", NEWLINE, gDLL->getSymbolID(BULLET_CHAR), szText.GetCString());
                        szInfoText.append(szBuffer);
                    }
                }
            }
        }

		// Civilization Terrain Yield Changes
		bool bFirst = true;
		for (int iI = 0; iI < GC.getNumTerrainInfos(); iI++)
		{
			for (int iJ = 0; iJ < NUM_YIELD_TYPES; iJ++)
			{
				int iTerrainYieldChange = GC.getCivilizationInfo(eCivilization).getTerrainYieldChanges(iI, iJ, false);
				if (iTerrainYieldChange != 0) {
					if (bFirst)
					{
						szText = gDLL->getText("TXT_KEY_MISC_CIV_TERRAIN");
						if (bDawnOfMan)
						{
							szTempString.Format(L"%s:\n", szText.GetCString());
							szInfoText.append(szTempString);
						}
						else
						{
							szBuffer.Format(NEWLINE SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT"), gDLL->getText("TXT_KEY_MISC_CIV_TERRAIN").GetCString());
							szInfoText.append(szBuffer);
						}
						bFirst = false;
					}
					
					szText = gDLL->getText("TXT_KEY_MISC_CIV_TERRAIN_MOD", iTerrainYieldChange, GC.getYieldInfo((YieldTypes) iJ).getChar(), GC.getTerrainInfo((TerrainTypes) iI).getTextKeyWide());
					if (bDawnOfMan)
					{
						szBuffer.Format(L"    %s\n", szText.GetCString());
						szInfoText.append(szBuffer);
					}
					else
					{
						szBuffer.Format(L"%s  %c%s", NEWLINE, gDLL->getSymbolID(BULLET_CHAR), szText.GetCString());
						szInfoText.append(szBuffer);
					}
				}

				// River Yield changes
				int iTerrainRiverYieldChange = GC.getCivilizationInfo(eCivilization).getTerrainYieldChanges(iI, iJ, true);
				if (iTerrainRiverYieldChange != 0 && iTerrainRiverYieldChange != iTerrainYieldChange)
				{
					if (bFirst)
					{
						szText = gDLL->getText("TXT_KEY_MISC_CIV_TERRAIN");
						if (bDawnOfMan)
						{
							szTempString.Format(L"%s:", szText.GetCString());
							szInfoText.append(szTempString);
						}
						else
						{
							szBuffer.Format(NEWLINE SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT"), gDLL->getText("TXT_KEY_MISC_CIV_TERRAIN").GetCString());
							szInfoText.append(szBuffer);
						}
						bFirst = false;
					}
					szText = gDLL->getText("TXT_KEY_MISC_CIV_TERRAIN_RIVER_MOD", iTerrainRiverYieldChange, GC.getYieldInfo((YieldTypes) iJ).getChar(), GC.getTerrainInfo((TerrainTypes) iI).getTextKeyWide());
					if (bDawnOfMan)
					{
						szBuffer.Format(L"    %s\n", szText.GetCString());
						szInfoText.append(szBuffer);
					}
					else
					{
						szBuffer.Format(L"%s  %c%s", NEWLINE, gDLL->getSymbolID(BULLET_CHAR), szText.GetCString());
						szInfoText.append(szBuffer);
					}
				}
				// End River Yield
			}
		}

		// Free Units
		szText = gDLL->getText("TXT_KEY_FREE_UNITS");
		if (bDawnOfMan)
		{
			szTempString.Format(L"%s: ", szText.GetCString());
		}
		else
		{
			szTempString.Format(NEWLINE SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT"), szText.GetCString());
		}
		szInfoText.append(szTempString);

		bool bFound = false;
		for (int iI = 0; iI < GC.getNumUnitClassInfos(); ++iI)
		{
			eDefaultUnit = ((UnitTypes)(GC.getCivilizationInfo(eCivilization).getCivilizationUnits(iI)));
			eUniqueUnit = ((UnitTypes)(GC.getUnitClassInfo((UnitClassTypes) iI).getDefaultUnitIndex()));
			if ((eDefaultUnit != NO_UNIT) && (eUniqueUnit != NO_UNIT))
			{
				if (eDefaultUnit != eUniqueUnit

//FfH: Added by Kael 08/27/2009
                  || (!isWorldUnitClass((UnitClassTypes) iI)
                  && GC.getUnitInfo(eUniqueUnit).getPrereqCiv() == eCivilization)
//FfH: End Add

				)
				{
					// Add Unit
					if (bDawnOfMan)
					{
						if (bFound)
						{
							szInfoText.append(L", ");
						}

//FfH: Modified by Kael 08/27/2009
//						szBuffer.Format((bLinks ? L"<link=literal>%s</link> - (<link=literal>%s</link>)" : L"%s - (%s)"),
//							GC.getUnitInfo(eDefaultUnit).getDescription(),
//							GC.getUnitInfo(eUniqueUnit).getDescription());
                        if (eDefaultUnit != eUniqueUnit)
                        {
                            szBuffer.Format((bLinks ? L"<link=literal>%s</link> - (<link=literal>%s</link>)" : L"%s - (%s)"),
                                GC.getUnitInfo(eDefaultUnit).getDescription(),
                                GC.getUnitInfo(eUniqueUnit).getDescription());
                        }
                        else
                        {
                            szBuffer.Format((bLinks ? L"<link=literal>%s</link>" : L"%s"),
                                GC.getUnitInfo(eDefaultUnit).getDescription());
                        }
//FfH: End Modify

					}
					else
					{

//FfH: Modified by Kael 08/27/2009
//						szBuffer.Format(L"\n  %c%s - (%s)", gDLL->getSymbolID(BULLET_CHAR),
//							GC.getUnitInfo(eDefaultUnit).getDescription(),
//							GC.getUnitInfo(eUniqueUnit).getDescription());
                        if (eDefaultUnit != eUniqueUnit)
                        {
                            szBuffer.Format(L"\n  %c%s - (%s)", gDLL->getSymbolID(BULLET_CHAR),
                                GC.getUnitInfo(eDefaultUnit).getDescription(),
                                GC.getUnitInfo(eUniqueUnit).getDescription());
                        }
                        else
                        {
                            szBuffer.Format(L"\n  %c%s", gDLL->getSymbolID(BULLET_CHAR),
                                GC.getUnitInfo(eDefaultUnit).getDescription());
                        }
//FfH: End Modify

					}
					szInfoText.append(szBuffer);
					bFound = true;
				}
			}
		}

		if (!bFound)
		{
			szText = gDLL->getText("TXT_KEY_FREE_UNITS_NO");
			if (bDawnOfMan)
			{
				szTempString.Format(L"%s", szText.GetCString());
			}
			else
			{
				szTempString.Format(L"%s  %s", NEWLINE, szText.GetCString());
			}
			szInfoText.append(szTempString);
			bFound = true;
		}

//FfH: Added by Kael 08/27/2009
		// Blocked Units
		szText = gDLL->getText("TXT_KEY_MISC_CIV_BLOCKED_UNITS");
		if (bDawnOfMan)
		{
			if (bFound)
			{
				szInfoText.append(NEWLINE);
			}
			szTempString.Format(L"%s: ", szText.GetCString());
		}
		else
		{
			szTempString.Format(NEWLINE SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT"), szText.GetCString());
		}
		szInfoText.append(szTempString);

		bFound = false;
		for (int iI = 0; iI < GC.getNumUnitClassInfos(); ++iI)
		{
			eUniqueUnit = ((UnitTypes)(GC.getCivilizationInfo(eCivilization).getCivilizationUnits(iI)));
			eDefaultUnit = ((UnitTypes)(GC.getUnitClassInfo((UnitClassTypes) iI).getDefaultUnitIndex()));
			if (eDefaultUnit != NO_UNIT
			  && eUniqueUnit == NO_UNIT
			  && !isWorldUnitClass((UnitClassTypes) iI)
			  && GC.getUnitInfo(eDefaultUnit).getPrereqCiv() == NO_CIVILIZATION)
			{
                if (bDawnOfMan)
                {
                    if (bFound)
                    {
                        szInfoText.append(L", ");
                    }
                    szBuffer.Format((bLinks ? L"<link=literal>%s</link>" : L"%s"),
                        GC.getUnitInfo(eDefaultUnit).getDescription());
                }
                else
                {
                    szBuffer.Format(L"\n  %c%s", gDLL->getSymbolID(BULLET_CHAR),
                        GC.getUnitInfo(eDefaultUnit).getDescription());
                }
                szInfoText.append(szBuffer);
                bFound = true;
			}
		}

		if (!bFound)
		{
			szText = gDLL->getText("TXT_KEY_MISC_CIV_BLOCKED_UNITS_NO");
			if (bDawnOfMan)
			{
				szTempString.Format(L"%s", szText.GetCString());
			}
			else
			{
				szTempString.Format(L"%s  %s", NEWLINE, szText.GetCString());
			}
			szInfoText.append(szTempString);
			bFound = true;
		}
//FfH: End Add

		// Free Buildings
		szText = gDLL->getText("TXT_KEY_UNIQUE_BUILDINGS");
		if (bDawnOfMan)
		{
			if (bFound)
			{
				szInfoText.append(NEWLINE);
			}
			szTempString.Format(L"%s: ", szText.GetCString());
		}
		else
		{
			szTempString.Format(NEWLINE SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT"), szText.GetCString());
		}
		szInfoText.append(szTempString);

		bFound = false;
		for (int iI = 0; iI < GC.getNumBuildingClassInfos(); ++iI)
		{
			eDefaultBuilding = ((BuildingTypes)(GC.getCivilizationInfo(eCivilization).getCivilizationBuildings(iI)));
			eUniqueBuilding = ((BuildingTypes)(GC.getBuildingClassInfo((BuildingClassTypes) iI).getDefaultBuildingIndex()));

//FfH: Modified by Kael 08/27/2009
//			if ((eDefaultBuilding != NO_BUILDING) && (eUniqueBuilding != NO_BUILDING))
			if (eDefaultBuilding != NO_BUILDING
			  && (eUniqueBuilding != NO_BUILDING
              || GC.getBuildingInfo(eDefaultBuilding).getPrereqCiv() == eCivilization))
//FfH: End Modify

			{
				if (eDefaultBuilding != eUniqueBuilding)
				{
					// Add Building
					if (bDawnOfMan)
					{
						if (bFound)
						{
							szInfoText.append(L", ");
						}

//FfH: Modified by Kael 08/27/2009
//						szBuffer.Format((bLinks ? L"<link=literal>%s</link> - (<link=literal>%s</link>)" : L"%s - (%s)"),
//							GC.getBuildingInfo(eDefaultBuilding).getDescription(),
//							GC.getBuildingInfo(eUniqueBuilding).getDescription());
                        if (GC.getBuildingInfo(eDefaultBuilding).getPrereqCiv() != eCivilization)
                        {
                            szBuffer.Format((bLinks ? L"<link=literal>%s</link> - (<link=literal>%s</link>)" : L"%s - (%s)"),
                                GC.getBuildingInfo(eDefaultBuilding).getDescription(),
                                GC.getBuildingInfo(eUniqueBuilding).getDescription());
                        }
                        else
                        {
                            szBuffer.Format((bLinks ? L"<link=literal>%s</link>" : L"%s"),
                                GC.getBuildingInfo(eDefaultBuilding).getDescription());
                        }
//FfH: End Modify

					}
					else
					{

//FfH: Modified by Kael 08/27/2009
//						szBuffer.Format(L"\n  %c%s - (%s)", gDLL->getSymbolID(BULLET_CHAR),
//							GC.getBuildingInfo(eDefaultBuilding).getDescription(),
//							GC.getBuildingInfo(eUniqueBuilding).getDescription());
                        if (GC.getBuildingInfo(eDefaultBuilding).getPrereqCiv() != eCivilization)
                        {
                            szBuffer.Format(L"\n  %c%s - (%s)", gDLL->getSymbolID(BULLET_CHAR),
                                GC.getBuildingInfo(eDefaultBuilding).getDescription(),
                                GC.getBuildingInfo(eUniqueBuilding).getDescription());
                        }
                        else
                        {
                            szBuffer.Format(L"\n  %c%s", gDLL->getSymbolID(BULLET_CHAR),
                                GC.getBuildingInfo(eDefaultBuilding).getDescription());
                        }
//FfH: End Modify

					}
					szInfoText.append(szBuffer);
					bFound = true;
				}
			}
		}
		if (!bFound)
		{
			szText = gDLL->getText("TXT_KEY_UNIQUE_BUILDINGS_NO");
			if (bDawnOfMan)
			{
				szTempString.Format(L"%s", szText.GetCString());
			}
			else
			{
				szTempString.Format(L"%s  %s", NEWLINE, szText.GetCString());
			}
			szInfoText.append(szTempString);
		}

//FfH: Added by Kael 08/27/2009
		// Blocked Buildings
		szText = gDLL->getText("TXT_KEY_MISC_CIV_BLOCKED_BUILDINGS");
		if (bDawnOfMan)
		{
			if (bFound)
			{
				szInfoText.append(NEWLINE);
			}
			szTempString.Format(L"%s: ", szText.GetCString());
		}
		else
		{
			szTempString.Format(NEWLINE SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT"), szText.GetCString());
		}
		szInfoText.append(szTempString);
		bFound = false;
		for (int iI = 0; iI < GC.getNumBuildingClassInfos(); ++iI)
		{
			eDefaultBuilding = ((BuildingTypes)(GC.getCivilizationInfo(eCivilization).getCivilizationBuildings(iI)));
			eUniqueBuilding = ((BuildingTypes)(GC.getBuildingClassInfo((BuildingClassTypes) iI).getDefaultBuildingIndex()));
			if ((eDefaultBuilding == NO_BUILDING) && (eUniqueBuilding != NO_BUILDING))
			{
				if (eDefaultBuilding != eUniqueBuilding)
				{
					// Add Building
					if (bDawnOfMan)
					{
						if (bFound)
						{
							szInfoText.append(L", ");
						}
						szBuffer.Format((bLinks ? L"<link=literal>%s</link>" : L"%s"),
							GC.getBuildingInfo(eUniqueBuilding).getDescription());
					}
					else
					{
						szBuffer.Format(L"\n  %c%s", gDLL->getSymbolID(BULLET_CHAR),
							GC.getBuildingInfo(eUniqueBuilding).getDescription());
					}
					szInfoText.append(szBuffer);
					bFound = true;
				}
			}
		}
		if (!bFound)
		{
			szText = gDLL->getText("TXT_KEY_MISC_CIV_BLOCKED_BUILDINGS_NO");
			if (bDawnOfMan)
			{
				szTempString.Format(L"%s", szText.GetCString());
			}
			else
			{
				szTempString.Format(L"%s  %s", NEWLINE, szText.GetCString());
			}
			szInfoText.append(szTempString);
		}

        //Special Abilities
		if (!CvWString(GC.getCivilizationInfo(eCivilization).getHelp()).empty())
		{
            szText = gDLL->getText("TXT_KEY_MISC_CIV_SPECIAL_ABILITIES");
            if (bDawnOfMan)
            {
                szInfoText.append(NEWLINE);
                szTempString.Format(L"%s: ", szText.GetCString());
            }
            else
            {
                szTempString.Format(NEWLINE SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_ALT_HIGHLIGHT_TEXT"), szText.GetCString());
            }
            szInfoText.append(szTempString);
			if (bDawnOfMan)
			{
				szBuffer.Format((bLinks ? L"%s" : L"%s"),
					GC.getCivilizationInfo(eCivilization).getHelp());
			}
			else
			{
				szBuffer.Format(L"\n  %c%s", gDLL->getSymbolID(BULLET_CHAR),
					GC.getCivilizationInfo(eCivilization).getHelp());
			}
			szInfoText.append(szBuffer);
		}
//FfH: End Add

	}
	else
	{
		//	This is a random civ, let us know here...
		szInfoText.append(gDLL->getText("TXT_KEY_CIV_UNKNOWN"));
	}

//	return szInfoText;
}


// BUG - Specialist Actual Effects - start
void CvGameTextMgr::parseSpecialistHelp(CvWStringBuffer &szHelpString, SpecialistTypes eSpecialist, CvCity* pCity, bool bCivilopediaText)
{
	parseSpecialistHelpActual(szHelpString, eSpecialist, pCity, bCivilopediaText, 0);
}

void CvGameTextMgr::parseSpecialistHelpActual(CvWStringBuffer &szHelpString, SpecialistTypes eSpecialist, CvCity* pCity, bool bCivilopediaText, int iChange)
// BUG - Specialist Actual Effects - end
{
	PROFILE_FUNC();

	CvWString szText;
	int aiYields[NUM_YIELD_TYPES];
	int aiCommerces[NUM_COMMERCE_TYPES];
	int iI;

	if (eSpecialist != NO_SPECIALIST)
	{
		if (!bCivilopediaText)
		{
			szHelpString.append(GC.getSpecialistInfo(eSpecialist).getDescription());
		}

		for (iI = 0; iI < NUM_YIELD_TYPES; ++iI)
		{
			if (GC.getGameINLINE().getActivePlayer() == NO_PLAYER)
			{
				aiYields[iI] = GC.getSpecialistInfo(eSpecialist).getYieldChange(iI);
			}
			else
			{
				aiYields[iI] = GET_PLAYER((pCity != NULL) ? pCity->getOwnerINLINE() : GC.getGameINLINE().getActivePlayer()).specialistYield(eSpecialist, ((YieldTypes)iI));
			}
		}

		setYieldChangeHelp(szHelpString, L"", L"", L"", aiYields);

		for (iI = 0; iI < NUM_COMMERCE_TYPES; ++iI)
		{
			if (GC.getGameINLINE().getActivePlayer() == NO_PLAYER)
			{
				aiCommerces[iI] = GC.getSpecialistInfo(eSpecialist).getCommerceChange(iI);
			}
			else
			{
				aiCommerces[iI] = GET_PLAYER((pCity != NULL) ? pCity->getOwnerINLINE() : GC.getGameINLINE().getActivePlayer()).specialistCommerce(((SpecialistTypes)eSpecialist), ((CommerceTypes)iI));
			}
		}

		setCommerceChangeHelp(szHelpString, L"", L"", L"", aiCommerces);

		if (GC.getSpecialistInfo(eSpecialist).getExperience() > 0)
		{
			szHelpString.append(NEWLINE);
			szHelpString.append(gDLL->getText("TXT_KEY_SPECIALIST_EXPERIENCE", GC.getSpecialistInfo(eSpecialist).getExperience()));
		}

		if (GC.getSpecialistInfo(eSpecialist).getGreatPeopleRateChange() != 0)
		{
			szHelpString.append(NEWLINE);
			szHelpString.append(gDLL->getText("TXT_KEY_SPECIALIST_BIRTH_RATE", GC.getSpecialistInfo(eSpecialist).getGreatPeopleRateChange()));
		}

// BUG - Specialist Actual Effects - start
		if (iChange != 0 && NULL != pCity && pCity->getOwnerINLINE() == GC.getGame().getActivePlayer() && getBugOptionBOOL("MiscHover__SpecialistActualEffects", true, "BUG_MISC_SPECIALIST_HOVER_ACTUAL_EFFECTS"))
		{
			bool bStarted = false;
			CvWString szStart = gDLL->getText("TXT_KEY_ACTUAL_EFFECTS");

			// Yield
			int aiYields[NUM_YIELD_TYPES];
			for (int iI = 0; iI < NUM_YIELD_TYPES; ++iI)
			{
				aiYields[iI] = pCity->getAdditionalYieldBySpecialist((YieldTypes)iI, eSpecialist, iChange);
			}
			bStarted = setResumableYieldChangeHelp(szHelpString, szStart, L": ", L"", aiYields, false, true, bStarted);
			
			// Commerce
			int aiCommerces[NUM_COMMERCE_TYPES];
			for (int iI = 0; iI < NUM_COMMERCE_TYPES; ++iI)
			{
				aiCommerces[iI] = pCity->getAdditionalCommerceTimes100BySpecialist((CommerceTypes)iI, eSpecialist, iChange);
			}
			bStarted = setResumableCommerceTimes100ChangeHelp(szHelpString, szStart, L": ", L"", aiCommerces, true, bStarted);

			// Great People
			int iGreatPeopleRate = pCity->getAdditionalGreatPeopleRateBySpecialist(eSpecialist, iChange);
			bStarted = setResumableValueChangeHelp(szHelpString, szStart, L": ", L"", iGreatPeopleRate, gDLL->getSymbolID(GREAT_PEOPLE_CHAR), false, true, bStarted);
		}
// BUG - Specialist Actual Effects - end

/*************************************************************************************************/
/** Specialists Enhancements, by Supercheese 10/9/09                                                   */
/**                                                                                              */
/**                                                                                              */
/*************************************************************************************************/
		if (GC.getSpecialistInfo(eSpecialist).getHealth() > 0)
		{
			szHelpString.append(NEWLINE);
			szHelpString.append(gDLL->getText("TXT_KEY_SPECIALIST_HEALTHY", GC.getSpecialistInfo(eSpecialist).getHealth()));
		}
		if (GC.getSpecialistInfo(eSpecialist).getHealth() < 0)
		{
			szHelpString.append(NEWLINE);
			szHelpString.append(gDLL->getText("TXT_KEY_SPECIALIST_UNHEALTHY", -(GC.getSpecialistInfo(eSpecialist).getHealth())));
		}
		if (GC.getSpecialistInfo(eSpecialist).getHappiness() > 0)
		{
			szHelpString.append(NEWLINE);
			szHelpString.append(gDLL->getText("TXT_KEY_SPECIALIST_HAPPY", GC.getSpecialistInfo(eSpecialist).getHappiness()));
		}
		if (GC.getSpecialistInfo(eSpecialist).getHappiness() < 0)
		{
			szHelpString.append(NEWLINE);
			szHelpString.append(gDLL->getText("TXT_KEY_SPECIALIST_UNHAPPY", -(GC.getSpecialistInfo(eSpecialist).getHappiness())));
		}
/*************************************************************************************************/
/** Specialists Enhancements                          END                                              */
/*************************************************************************************************/

		if (!CvWString(GC.getSpecialistInfo(eSpecialist).getHelp()).empty() && !bCivilopediaText)
		{
			szHelpString.append(NEWLINE);
			szHelpString.append(GC.getSpecialistInfo(eSpecialist).getHelp());
		}
	}
}

void CvGameTextMgr::parseFreeSpecialistHelp(CvWStringBuffer &szHelpString, const CvCity& kCity)
{
	PROFILE_FUNC();

	for (int iLoopSpecialist = 0; iLoopSpecialist < GC.getNumSpecialistInfos(); iLoopSpecialist++)
	{
		SpecialistTypes eSpecialist = (SpecialistTypes)iLoopSpecialist;
		int iNumSpecialists = kCity.getFreeSpecialistCount(eSpecialist);

		if (iNumSpecialists > 0)
		{
			int aiYields[NUM_YIELD_TYPES];
			int aiCommerces[NUM_COMMERCE_TYPES];

			szHelpString.append(NEWLINE);
			szHelpString.append(CvWString::format(L"%s (%d): ", GC.getSpecialistInfo(eSpecialist).getDescription(), iNumSpecialists));

			for (int iI = 0; iI < NUM_YIELD_TYPES; ++iI)
			{
				aiYields[iI] = iNumSpecialists * GET_PLAYER(kCity.getOwnerINLINE()).specialistYield(eSpecialist, ((YieldTypes)iI));
			}

			CvWStringBuffer szYield;
			setYieldChangeHelp(szYield, L"", L"", L"", aiYields, false, false);
			szHelpString.append(szYield);

			for (int iI = 0; iI < NUM_COMMERCE_TYPES; ++iI)
			{
				aiCommerces[iI] = iNumSpecialists * GET_PLAYER(kCity.getOwnerINLINE()).specialistCommerce(eSpecialist, ((CommerceTypes)iI));
			}

			CvWStringBuffer szCommerceString;
			setCommerceChangeHelp(szCommerceString, L"", L"", L"", aiCommerces, false, false);
			if (!szYield.isEmpty() && !szCommerceString.isEmpty())
			{
				szHelpString.append(L", ");
			}
			szHelpString.append(szCommerceString);

			if (GC.getSpecialistInfo(eSpecialist).getExperience() > 0)
			{
				if (!szYield.isEmpty() || !szYield.isEmpty())
				{
					szHelpString.append(L", ");
				}
				szHelpString.append(gDLL->getText("TXT_KEY_SPECIALIST_EXPERIENCE_SHORT", iNumSpecialists * GC.getSpecialistInfo(eSpecialist).getExperience()));
			}
		}
	}
}


//
// Promotion Help
//
void CvGameTextMgr::parsePromotionHelp(CvWStringBuffer &szBuffer, PromotionTypes ePromotion, const wchar* pcNewline)
{
	PROFILE_FUNC();

	CvWString szText, szText2;
	int iI;

	if (NO_PROMOTION == ePromotion)
	{
		return;
	}

	CvPromotionInfo &kPromotionInfo = GC.getPromotionInfo(ePromotion);

	if (kPromotionInfo.isAllowsMoveImpassable())
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_CAN_MOVE_IMPASSABLE_TEXT"));
	}

	if (kPromotionInfo.isAllowsMoveLimitedBorders())
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_CAN_MOVE_LIMITED_BORDERS_TEXT"));
	}

	if (kPromotionInfo.isBlitz())
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_BLITZ_TEXT"));
	}

	if (kPromotionInfo.isAmphib())
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_AMPHIB_TEXT"));
	}

	if (kPromotionInfo.isRiver())
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_RIVER_ATTACK_TEXT"));
	}

	if (kPromotionInfo.isEnemyRoute())
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_ENEMY_ROADS_TEXT"));
	}

	if (kPromotionInfo.isAlwaysHeal())
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_ALWAYS_HEAL_TEXT"));
	}

	if (kPromotionInfo.isHillsDoubleMove())
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_HILLS_MOVE_TEXT"));
	}

	if (kPromotionInfo.isImmuneToFirstStrikes())
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_IMMUNE_FIRST_STRIKES_TEXT"));
	}

	for (iI = 0; iI < GC.getNumTerrainInfos(); ++iI)
	{
		if (kPromotionInfo.getTerrainDoubleMove(iI))
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_DOUBLE_MOVE_TEXT", GC.getTerrainInfo((TerrainTypes) iI).getTextKeyWide()));
		}
	}

	for (iI = 0; iI < GC.getNumFeatureInfos(); ++iI)
	{
		if (kPromotionInfo.getFeatureDoubleMove(iI))
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_DOUBLE_MOVE_TEXT", GC.getFeatureInfo((FeatureTypes) iI).getTextKeyWide()));
		}
	}

	if (kPromotionInfo.getVisibilityChange() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_VISIBILITY_TEXT", kPromotionInfo.getVisibilityChange()));
	}

	if (kPromotionInfo.getMovesChange() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_MOVE_TEXT", kPromotionInfo.getMovesChange()));
	}

	if (kPromotionInfo.getMoveDiscountChange() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_MOVE_DISCOUNT_TEXT", -(kPromotionInfo.getMoveDiscountChange())));
	}

	if (kPromotionInfo.getAirRangeChange() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_AIR_RANGE_TEXT", kPromotionInfo.getAirRangeChange()));
	}

	if (kPromotionInfo.getInterceptChange() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_INTERCEPT_TEXT", kPromotionInfo.getInterceptChange()));
	}

	if (kPromotionInfo.getEvasionChange() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_EVASION_TEXT", kPromotionInfo.getEvasionChange()));
	}

	if (kPromotionInfo.getWithdrawalChange() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_WITHDRAWAL_TEXT", kPromotionInfo.getWithdrawalChange()));
	}

	if (kPromotionInfo.getCargoChange() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_CARGO_TEXT", kPromotionInfo.getCargoChange()));
	}

	if (kPromotionInfo.getCollateralDamageChange() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_COLLATERAL_DAMAGE_TEXT", kPromotionInfo.getCollateralDamageChange()));
	}

	if (kPromotionInfo.getBombardRateChange() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_BOMBARD_TEXT", kPromotionInfo.getBombardRateChange()));
	}

	if (kPromotionInfo.getFirstStrikesChange() != 0)
	{
		if (kPromotionInfo.getFirstStrikesChange() == 1)
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_FIRST_STRIKE_TEXT", kPromotionInfo.getFirstStrikesChange()));
		}
		else
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_FIRST_STRIKES_TEXT", kPromotionInfo.getFirstStrikesChange()));
		}
	}

	if (kPromotionInfo.getChanceFirstStrikesChange() != 0)
	{
		if (kPromotionInfo.getChanceFirstStrikesChange() == 1)
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_FIRST_STRIKE_CHANCE_TEXT", kPromotionInfo.getChanceFirstStrikesChange()));
		}
		else
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_FIRST_STRIKES_CHANCE_TEXT", kPromotionInfo.getChanceFirstStrikesChange()));
		}
	}
/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**																								**/
/*************************************************************************************************/
//BUGFfH: Added by Denev 2009/09/06
	if (kPromotionInfo.getEnemyHealChange() == kPromotionInfo.getNeutralHealChange()
		&& kPromotionInfo.getEnemyHealChange() == kPromotionInfo.getFriendlyHealChange())
	{
		if (kPromotionInfo.getEnemyHealChange() != 0)
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_HEALS_EXTRA_TEXT", kPromotionInfo.getEnemyHealChange()) + gDLL->getText("TXT_KEY_PROMOTION_DAMAGE_TURN_TEXT"));
		}
	}
	else
	{
//BUGFfH: End Add
	if (kPromotionInfo.getEnemyHealChange() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_HEALS_EXTRA_TEXT", kPromotionInfo.getEnemyHealChange()) + gDLL->getText("TXT_KEY_PROMOTION_ENEMY_LANDS_TEXT"));
	}


	if (kPromotionInfo.getNeutralHealChange() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_HEALS_EXTRA_TEXT", kPromotionInfo.getNeutralHealChange()) + gDLL->getText("TXT_KEY_PROMOTION_NEUTRAL_LANDS_TEXT"));
	}

	if (kPromotionInfo.getFriendlyHealChange() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_HEALS_EXTRA_TEXT", kPromotionInfo.getFriendlyHealChange()) + gDLL->getText("TXT_KEY_PROMOTION_FRIENDLY_LANDS_TEXT"));
	}
//BUGFfH: Added by Denev 2009/09/06
	}
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/

	if (kPromotionInfo.getSameTileHealChange() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_HEALS_SAME_TEXT", kPromotionInfo.getSameTileHealChange()) + gDLL->getText("TXT_KEY_PROMOTION_DAMAGE_TURN_TEXT"));
	}

	if (kPromotionInfo.getAdjacentTileHealChange() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_HEALS_ADJACENT_TEXT", kPromotionInfo.getAdjacentTileHealChange()) + gDLL->getText("TXT_KEY_PROMOTION_DAMAGE_TURN_TEXT"));
	}

	if (kPromotionInfo.getCombatPercent() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_STRENGTH_TEXT", kPromotionInfo.getCombatPercent()));
	}

/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**																								**/
/*************************************************************************************************/
//BUGFfH: Added by Denev 2009/09/05
	if (kPromotionInfo.getCityAttackPercent() == kPromotionInfo.getCityDefensePercent())
	{
		if (kPromotionInfo.getCityAttackPercent() != 0)
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_CITY_STRENGTH_MOD", kPromotionInfo.getCityAttackPercent()));
		}
	}
	else
	{
//BUGFfH: End Add
		if (kPromotionInfo.getCityAttackPercent() != 0)
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_CITY_ATTACK_TEXT", kPromotionInfo.getCityAttackPercent()));
		}

		if (kPromotionInfo.getCityDefensePercent() != 0)
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_CITY_DEFENSE_TEXT", kPromotionInfo.getCityDefensePercent()));
		}
//BUGFfH: Added by Denev 2009/09/05
	}
//BUGFfH: End Add

//BUGFfH: Added by Denev 2009/09/05
	if (kPromotionInfo.getHillsAttackPercent() == kPromotionInfo.getHillsDefensePercent())
	{
		if (kPromotionInfo.getHillsAttackPercent() != 0)
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_HILLS_STRENGTH", kPromotionInfo.getHillsAttackPercent()));
		}
	}
	else
	{
//BUGFfH: End Add
		if (kPromotionInfo.getHillsAttackPercent() != 0)
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_HILLS_ATTACK", kPromotionInfo.getHillsAttackPercent()));
		}

		if (kPromotionInfo.getHillsDefensePercent() != 0)
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_HILLS_DEFENSE_TEXT", kPromotionInfo.getHillsDefensePercent()));
		}
//BUGFfH: Added by Denev 2009/09/05
	}
//BUGFfH: End Add
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/

	if (kPromotionInfo.getRevoltProtection() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_REVOLT_PROTECTION_TEXT", kPromotionInfo.getRevoltProtection()));
	}

	if (kPromotionInfo.getCollateralDamageProtection() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_COLLATERAL_PROTECTION_TEXT", kPromotionInfo.getCollateralDamageProtection()));
	}

	if (kPromotionInfo.getPillageChange() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_PILLAGE_CHANGE_TEXT", kPromotionInfo.getPillageChange()));
	}

	if (kPromotionInfo.getUpgradeDiscount() != 0)
	{
		if (100 == kPromotionInfo.getUpgradeDiscount())
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_UPGRADE_DISCOUNT_FREE_TEXT"));
		}
		else
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_UPGRADE_DISCOUNT_TEXT", kPromotionInfo.getUpgradeDiscount()));
		}
	}

	if (kPromotionInfo.getExperiencePercent() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_FASTER_EXPERIENCE_TEXT", kPromotionInfo.getExperiencePercent()));
	}

	if (kPromotionInfo.getKamikazePercent() != 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_KAMIKAZE_TEXT", kPromotionInfo.getKamikazePercent()));
	}

	for (iI = 0; iI < GC.getNumTerrainInfos(); ++iI)
	{
/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**																								**/
/*************************************************************************************************/
//BUGFfH: Added by Denev 2009/09/05
		if (kPromotionInfo.getTerrainAttackPercent(iI) == kPromotionInfo.getTerrainDefensePercent(iI))
		{
			if (kPromotionInfo.getTerrainAttackPercent(iI) != 0)
			{
				szBuffer.append(pcNewline);
				szBuffer.append(gDLL->getText("TXT_KEY_UNIT_STRENGTH", kPromotionInfo.getTerrainAttackPercent(iI), GC.getTerrainInfo((TerrainTypes) iI).getTextKeyWide()));
			}
		}
		else
		{
//BUGFfH: End Add
			if (kPromotionInfo.getTerrainAttackPercent(iI) != 0)
			{
				szBuffer.append(pcNewline);
				szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_ATTACK_TEXT", kPromotionInfo.getTerrainAttackPercent(iI), GC.getTerrainInfo((TerrainTypes) iI).getTextKeyWide()));
			}


			if (kPromotionInfo.getTerrainDefensePercent(iI) != 0)
			{
				szBuffer.append(pcNewline);
				szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_DEFENSE_TEXT", kPromotionInfo.getTerrainDefensePercent(iI), GC.getTerrainInfo((TerrainTypes) iI).getTextKeyWide()));
			}
//BUGFfH: Added by Denev 2009/09/05
		}
//BUGFfH: End Add
	}

	for (iI = 0; iI < GC.getNumFeatureInfos(); ++iI)
	{
/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**																								**/
/*************************************************************************************************/
//BUGFfH: Added by Denev 2009/09/05
		if (kPromotionInfo.getFeatureAttackPercent(iI) == kPromotionInfo.getFeatureDefensePercent(iI))
		{
			if (kPromotionInfo.getFeatureAttackPercent(iI) != 0)
			{
				szBuffer.append(pcNewline);
				szBuffer.append(gDLL->getText("TXT_KEY_UNIT_STRENGTH", kPromotionInfo.getFeatureAttackPercent(iI), GC.getFeatureInfo((FeatureTypes) iI).getTextKeyWide()));
			}
		}
		else
		{
//BUGFfH: End Add
		if (kPromotionInfo.getFeatureAttackPercent(iI) != 0)
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_ATTACK_TEXT", kPromotionInfo.getFeatureAttackPercent(iI), GC.getFeatureInfo((FeatureTypes) iI).getTextKeyWide()));
		}

		if (kPromotionInfo.getFeatureDefensePercent(iI) != 0)
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_DEFENSE_TEXT", kPromotionInfo.getFeatureDefensePercent(iI), GC.getFeatureInfo((FeatureTypes) iI).getTextKeyWide()));
		}
//BUGFfH: Added by Denev 2009/09/05
		}
//BUGFfH: End Add
	}
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/

	for (iI = 0; iI < GC.getNumUnitCombatInfos(); ++iI)
	{
		if (kPromotionInfo.getUnitCombatModifierPercent(iI) != 0)
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_VERSUS_TEXT", kPromotionInfo.getUnitCombatModifierPercent(iI), GC.getUnitCombatInfo((UnitCombatTypes)iI).getTextKeyWide()));
		}
	}

	for (iI = 0; iI < NUM_DOMAIN_TYPES; ++iI)
	{
		if (kPromotionInfo.getDomainModifierPercent(iI) != 0)
		{
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_VERSUS_TEXT", kPromotionInfo.getDomainModifierPercent(iI), GC.getDomainInfo((DomainTypes)iI).getTextKeyWide()));
		}
	}

//FfH: Added by Kael 07/30/2007
    if (kPromotionInfo.isRace())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_RACE_PEDIA", kPromotionInfo.getDescription()));
    }
	for (iI = 0; iI < GC.getNumDamageTypeInfos(); iI++)
	{
        if (kPromotionInfo.getDamageTypeCombat((DamageTypes)iI) != 0)
		{
            szBuffer.append(pcNewline);
            szBuffer.append(gDLL->getText("TXT_KEY_DAMAGE_TYPE_COMBAT", kPromotionInfo.getDamageTypeCombat((DamageTypes)iI), GC.getDamageTypeInfo((DamageTypes)iI).getDescription()));
		}
        if (kPromotionInfo.getDamageTypeResist((DamageTypes)iI) != 0)
		{
            szBuffer.append(pcNewline);
            if (kPromotionInfo.getDamageTypeResist((DamageTypes)iI) == 100)
            {
                szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_DAMAGE_TYPE_IMMUNE", GC.getDamageTypeInfo((DamageTypes)iI).getDescription()));
            }
            else
            {
                szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_DAMAGE_TYPE_RESIST", kPromotionInfo.getDamageTypeResist((DamageTypes)iI), GC.getDamageTypeInfo((DamageTypes)iI).getDescription()));
            }
		}
	}
	for (iI = 0; iI < GC.getNumBonusInfos(); iI++)
	{
        if (kPromotionInfo.getBonusAffinity((BonusTypes)iI) != 0)
		{
            szBuffer.append(NEWLINE);
            szBuffer.append(gDLL->getText("TXT_KEY_BONUS_AFFINITY", kPromotionInfo.getBonusAffinity((BonusTypes)iI), GC.getBonusInfo((BonusTypes)iI).getDescription()));
		}
	}
    if (kPromotionInfo.getDefensiveStrikeChance() == 0)
    {
        if (kPromotionInfo.getDefensiveStrikeDamage() > 0)
        {
            szBuffer.append(NEWLINE);
            szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_DEFENSIVE_STRIKE_DAMAGE_PEDIA", kPromotionInfo.getDefensiveStrikeDamage()));
        }
    }
    else
    {
        if (kPromotionInfo.getDefensiveStrikeDamage() > 0)
        {
            szBuffer.append(NEWLINE);
            szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_DEFENSIVE_STRIKE_PEDIA", kPromotionInfo.getDefensiveStrikeChance(), kPromotionInfo.getDefensiveStrikeDamage()));
        }
        else
        {
            szBuffer.append(NEWLINE);
            szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_DEFENSIVE_STRIKE_CHANCE_PEDIA", kPromotionInfo.getDefensiveStrikeChance()));
        }
    }
    if (kPromotionInfo.isImmuneToDefensiveStrike())
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_IMMUNE_TO_DEFENSIVE_STRIKE_PEDIA"));
    }
    if (kPromotionInfo.getCombatPercentInBorders() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_COMBAT_PERCENT_IN_BORDERS", kPromotionInfo.getCombatPercentInBorders()));
    }
	if (kPromotionInfo.getExtraCombatStr() == kPromotionInfo.getExtraCombatDefense())
	{
		if (kPromotionInfo.getExtraCombatStr() != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_EXTRA_COMBAT_STR", kPromotionInfo.getExtraCombatStr()));
		}
	}
	else
	{
        if (kPromotionInfo.getExtraCombatStr() != 0)
        {
            szBuffer.append(pcNewline);
            szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_EXTRA_COMBAT_STR_ATTACK", kPromotionInfo.getExtraCombatStr()));
        }
        if (kPromotionInfo.getExtraCombatDefense() != 0)
        {
            szBuffer.append(pcNewline);
            szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_EXTRA_COMBAT_STR_DEFENSE", kPromotionInfo.getExtraCombatDefense()));
        }
	}
    if (kPromotionInfo.isTargetWeakestUnit())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_TARGET_WEAKEST_UNIT"));
    }
    if (kPromotionInfo.isTargetWeakestUnitCounter())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_TARGET_WEAKEST_UNIT_COUNTER"));
    }
    if (kPromotionInfo.getBetterDefenderThanPercent() != 0)
    {
        szBuffer.append(pcNewline);
        if (kPromotionInfo.getBetterDefenderThanPercent() < 0)
        {
            szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_BETTER_DEFENDER_THAN_PERCENT_LESS"));
        }
        if (kPromotionInfo.getBetterDefenderThanPercent() > 0)
        {
            szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_BETTER_DEFENDER_THAN_PERCENT_MORE"));
        }
    }
    if (kPromotionInfo.getPromotionCombatApply() != NO_PROMOTION)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_COMBAT_APPLY", GC.getPromotionInfo((PromotionTypes)kPromotionInfo.getPromotionCombatApply()).getDescription()));
    }
    if (kPromotionInfo.getPromotionRandomApply() != NO_PROMOTION)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_RANDOM_APPLY", GC.getPromotionInfo((PromotionTypes)kPromotionInfo.getPromotionRandomApply()).getDescription()));
    }
    if (kPromotionInfo.isBoarding())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_BOARDING_PEDIA"));
    }
    if (kPromotionInfo.getCaptureUnitCombat() != NO_UNITCOMBAT)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_CAPTURE_UNITCOMBAT", GC.getUnitCombatInfo((UnitCombatTypes)kPromotionInfo.getCaptureUnitCombat()).getDescription()));
    }
    if (kPromotionInfo.getCombatCapturePercent() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_COMBAT_CAPTURE_PERCENT", kPromotionInfo.getCombatCapturePercent()));
    }
    if (kPromotionInfo.getCombatHealPercent() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_COMBAT_HEAL_PERCENT", kPromotionInfo.getCombatHealPercent()));
    }
    if (kPromotionInfo.getCombatLimit() != 0)
    {
        szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_COMBAT_LIMIT", (100 * kPromotionInfo.getCombatLimit()) / GC.getMAX_HIT_POINTS()));
    }
    if (kPromotionInfo.isFear())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_FEAR_PEDIA"));
    }
    if (kPromotionInfo.getFreeXPPerTurn() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_FREE_XP_PER_TURN", kPromotionInfo.getFreeXPPerTurn(), GC.getDefineINT("FREE_XP_MAX")));
    }
    if (kPromotionInfo.getFreeXPFromCombat() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_FREE_XP_FROM_COMBAT", kPromotionInfo.getFreeXPFromCombat()));
    }
    if (kPromotionInfo.getGoldFromCombat() != 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_UNIT_GOLD_FROM_COMBAT", kPromotionInfo.getGoldFromCombat()));
    }
    if (kPromotionInfo.getModifyGlobalCounter() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_MESSAGE_MODIFY_GLOBAL_COUNTER", kPromotionInfo.getModifyGlobalCounter()));
    }
    if (kPromotionInfo.getModifyGlobalCounterOnCombat() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_MESSAGE_MODIFY_GLOBAL_COUNTER_ON_COMBAT", kPromotionInfo.getModifyGlobalCounterOnCombat()));
    }
    if (kPromotionInfo.getSpellCasterXP() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_SPELL_CASTER_XP"));
    }
    if (kPromotionInfo.isFlying())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_FLYING_PEDIA"));
    }
    if (kPromotionInfo.isHeld())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_HELD_PEDIA"));
    }
	if (kPromotionInfo.isCastingBlocked())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_CASTING_BLOCKED_PEDIA"));
    }
	if (kPromotionInfo.isBlocksUpgrade())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_UPGRADE_BLOCKED_PEDIA"));
    }
	if (kPromotionInfo.isBlocksGifting())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_GIFTING_BLOCKED_PEDIA"));
    }
	if (kPromotionInfo.isUpgradeOutsideBorders())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_UPGRADE_OUTSIDE_BORDERS_PEDIA"));
    }
    if (kPromotionInfo.isHiddenNationality())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_HIDDEN_NATIONALITY_PEDIA"));
    }
    if (kPromotionInfo.isIgnoreBuildingDefense())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_IGNORE_BUILDING_DEFENSE"));
    }
    if (kPromotionInfo.isImmortal())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_IMMORTAL_PEDIA"));
    }
    if (kPromotionInfo.isImmuneToCapture())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_IMMUNE_TO_CAPTURE_PEDIA"));
    }
    if (kPromotionInfo.isImmuneToMagic())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_IMMUNE_TO_MAGIC_PEDIA"));
    }
    if (kPromotionInfo.isImmuneToFear())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_IMMUNE_TO_FEAR_PEDIA"));
    }
	// XML_LISTS 07/2019 lfgr
	for( int eImmunePromotion = 0; eImmunePromotion < GC.getNumPromotionInfos(); eImmunePromotion++ ) {
		if( kPromotionInfo.isPromotionImmune( eImmunePromotion ) ) {
			szBuffer.append(pcNewline);
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_IMMUNE",
					GC.getPromotionInfo((PromotionTypes) eImmunePromotion).getDescription()));
		}
	}
	// XML_LISTS end
    if (kPromotionInfo.isInvisible())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_INVISIBLE_PEDIA"));
    }
    if (kPromotionInfo.isSeeInvisible())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_SEE_INVISIBLE_PEDIA"));
    }
    if (kPromotionInfo.isDoubleFortifyBonus())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_DOUBLE_FORTIFY_BONUS"));
    }
    if (kPromotionInfo.isTwincast())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_TWINCAST_PEDIA"));
    }
    if (kPromotionInfo.isWaterWalking())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_WATER_WALKING_PEDIA"));
    }
    if (kPromotionInfo.isNotAlive())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_NOT_ALIVE"));
    }
    if (kPromotionInfo.getResistMagic() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_RESIST", kPromotionInfo.getResistMagic()));
    }
    if (kPromotionInfo.getSpellDamageModify() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_SPELL_DAMAGE_MODIFY", kPromotionInfo.getSpellDamageModify()));
    }
    if (kPromotionInfo.getCasterResistModify() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_CASTER_RESIST_MODIFY", kPromotionInfo.getCasterResistModify()));
    }
	// MiscastPromotions 10/2019 lfgr
    if (kPromotionInfo.getMiscastChance() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_MISCAST_CHANCE_MODIFY", kPromotionInfo.getMiscastChance()));
    }
	// MiscastPromotions end
	for (iI = 0; iI < GC.getNumSpellInfos(); iI++)
	{
	    if (GC.getSpellInfo((SpellTypes)iI).getPromotionPrereq1() == ePromotion)
		{
            if (!GC.getSpellInfo((SpellTypes)iI).isGraphicalOnly())
            {
                szBuffer.append(pcNewline);
                if (GC.getSpellInfo((SpellTypes)iI).getPromotionPrereq2() == NO_PROMOTION)
                {
                    szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_ALLOWS_TEXT", GC.getSpellInfo((SpellTypes)iI).getDescription()));
                }
                else
                {
                    szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_ALLOWS_WITH_TEXT", GC.getSpellInfo((SpellTypes)iI).getDescription(), GC.getPromotionInfo((PromotionTypes)GC.getSpellInfo((SpellTypes)iI).getPromotionPrereq2()).getDescription()));
                }
            }
		}
	}
    if (kPromotionInfo.getExpireChance() != 0)
    {
        szBuffer.append(pcNewline);
        // lfgr 02/2020: Better text for 100% expire chance
        if( kPromotionInfo.getExpireChance() == 100 ) {
			szBuffer.append( gDLL->getText( "TXT_KEY_PROMOTION_EXPIRES_END_OF_TURN" ) );
		}
		else {
			szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_EXPIRE_CHANCE", kPromotionInfo.getExpireChance()));
		}
    }
    if (kPromotionInfo.isRemovedByCasting())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_REMOVED_BY_CASTING"));
    }
    if (kPromotionInfo.isRemovedByCombat())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_REMOVED_BY_COMBAT"));
    }
    if (kPromotionInfo.isRemovedWhenHealed())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_REMOVED_WHEN_HEALED"));
    }
    if (kPromotionInfo.getPromotionSummonPerk() != NO_PROMOTION)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_SUMMON_PERK", GC.getPromotionInfo((PromotionTypes)kPromotionInfo.getPromotionSummonPerk()).getDescription()));
    }
    if (kPromotionInfo.getPromotionCombatMod() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_VERSUS_TEXT", kPromotionInfo.getPromotionCombatMod(), GC.getPromotionInfo((PromotionTypes)kPromotionInfo.getPromotionCombatType()).getTextKeyWide()));
    }
    if (kPromotionInfo.getBetrayalChance() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_BETRAYAL_CHANCE", kPromotionInfo.getBetrayalChance()));
    }
    if (kPromotionInfo.getWorkRateModify() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_WORK_RATE_MODIFY", kPromotionInfo.getWorkRateModify()));
    }
	if (kPromotionInfo.isPrereqAlive())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_PREREQ_ALIVE"));
    }
	if( kPromotionInfo.getMinLevel() > 0 ) { // lfgr 05/2020
		szBuffer.append( pcNewline );
		szBuffer.append( gDLL->getText( "TXT_KEY_PROMOTION_MIN_LEVEL", kPromotionInfo.getMinLevel() ) );
	}
//FfH: End Add

	if (wcslen(kPromotionInfo.getHelp()) > 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(kPromotionInfo.getHelp());
	}
}

//FfH: Added by Kael 07/23/2007
/********************************************************************************/
/* SpellPyHelp                        11/2013                           lfgr    */
/********************************************************************************/
/* old
void CvGameTextMgr::parseSpellHelp(CvWStringBuffer &szBuffer, SpellTypes eSpell, const wchar* pcNewline)
*/
void CvGameTextMgr::parseSpellHelp( CvWStringBuffer &szBuffer, SpellTypes eSpell, const wchar* pcNewline, std::vector<CvUnit*>* pvpUnits )
/********************************************************************************/
/* SpellPyHelp                                                          END     */
/********************************************************************************/
{
	PROFILE_FUNC();

	FAssert( pvpUnits == NULL || pvpUnits->size() > 0 );

	CvWString szText, szText2;

	if (NO_SPELL == eSpell)
	{
		return;
	}

	CvSpellInfo &kSpellInfo = GC.getSpellInfo(eSpell);

	// +++ Misc (important) +++
	
    if (kSpellInfo.isGlobal())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_GLOBAL"));
    }
    
    // lfgr 09/2019: Can be casted even after another spell has been casted this turn
    if (kSpellInfo.isIgnoreHasCasted())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_IGNORE_HAS_CASTED"));
    }

	// +++ Requirements +++
    
    // lfgr 09/2019: Caster must be alive
    if (kSpellInfo.isCasterMustBeAlive())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_PREREQ_CASTER_ALIVE"));
    }
    
    // lfgr 09/2019: Caster must not be temporary
    if (kSpellInfo.isCasterNoDuration())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_PREREQ_CASTER_NO_DURATION"));
    }
    
    if (kSpellInfo.getCasterMinLevel() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_CASTER_MIN_LEVEL", kSpellInfo.getCasterMinLevel()));
    }
    if (kSpellInfo.getBuildingPrereq() != NO_BUILDING)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_BUILDING_PREREQ", GC.getBuildingInfo((BuildingTypes)kSpellInfo.getBuildingPrereq()).getDescription()));
    }
    if (kSpellInfo.getBuildingClassOwnedPrereq() != NO_BUILDINGCLASS)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_BUILDINGCLASS_OWNED_PREREQ", GC.getBuildingClassInfo((BuildingClassTypes)kSpellInfo.getBuildingClassOwnedPrereq()).getDescription()));
    }
    if (kSpellInfo.getCivilizationPrereq() != NO_CIVILIZATION)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_CIVILIZATION_PREREQ", GC.getCivilizationInfo((CivilizationTypes)kSpellInfo.getCivilizationPrereq()).getDescription()));
    }
    if (kSpellInfo.getCorporationPrereq() != NO_CORPORATION)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_CORPORATION_PREREQ", GC.getCorporationInfo((CorporationTypes)kSpellInfo.getCorporationPrereq()).getDescription()));
    }
    if (kSpellInfo.getFeatureOrPrereq1() != NO_FEATURE)
    {
        if (kSpellInfo.getFeatureOrPrereq2() == NO_FEATURE)
        {
            szBuffer.append(pcNewline);
            szBuffer.append(gDLL->getText("TXT_KEY_SPELL_FEATURE_PREREQ", GC.getFeatureInfo((FeatureTypes)kSpellInfo.getFeatureOrPrereq1()).getDescription()));
        }
        else
        {
            szBuffer.append(pcNewline);
            szBuffer.append(gDLL->getText("TXT_KEY_SPELL_FEATURE2_PREREQ", GC.getFeatureInfo((FeatureTypes)kSpellInfo.getFeatureOrPrereq1()).getDescription(), GC.getFeatureInfo((FeatureTypes)kSpellInfo.getFeatureOrPrereq2()).getDescription()));
        }
    }
    if (kSpellInfo.getImprovementPrereq() != NO_IMPROVEMENT)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_IMPROVEMENT_PREREQ", GC.getImprovementInfo((ImprovementTypes)kSpellInfo.getImprovementPrereq()).getDescription()));
    }
    if (kSpellInfo.getPromotionInStackPrereq() != NO_PROMOTION)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_PROMOTION_IN_STACK_PREREQ", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getPromotionInStackPrereq()).getDescription()));
    }
    if (kSpellInfo.getReligionPrereq() != NO_RELIGION)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_RELIGION_PREREQ", GC.getReligionInfo((ReligionTypes)kSpellInfo.getReligionPrereq()).getDescription()));
    }
    if (kSpellInfo.getStateReligionPrereq() != NO_RELIGION)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_STATE_RELIGION_PREREQ", GC.getReligionInfo((ReligionTypes)kSpellInfo.getStateReligionPrereq()).getDescription()));
    }
	if (kSpellInfo.getTechPrereq() != NO_TECH)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_SPELL_TECH_PREREQ", GC.getTechInfo((TechTypes)kSpellInfo.getTechPrereq()).getDescription()));
	}
	if (kSpellInfo.getVotePrereq() != NO_VOTE) // lfgr VOTE_CLEANUP 04/2020
	{
		szBuffer.append(pcNewline);
		szBuffer.append( gDLL->getText("TXT_KEY_SPELL_VOTE_PREREQ", // LFGR_TODO
				GC.getVoteInfo( (VoteTypes) kSpellInfo.getVotePrereq() ).getDescription() ) );
	}
    if (kSpellInfo.getUnitPrereq() != NO_UNIT)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_UNIT_PREREQ", GC.getUnitInfo((UnitTypes)kSpellInfo.getUnitPrereq()).getDescription()));
    }
    if (kSpellInfo.getUnitCombatPrereq() != NO_UNITCOMBAT)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_UNIT_PREREQ", GC.getUnitCombatInfo((UnitCombatTypes)kSpellInfo.getUnitCombatPrereq()).getDescription()));
    }
    if (kSpellInfo.getUnitClassPrereq() != NO_UNITCLASS)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_UNIT_PREREQ", GC.getUnitClassInfo((UnitClassTypes)kSpellInfo.getUnitClassPrereq()).getDescription()));
    }
    if (kSpellInfo.getUnitInStackPrereq() != NO_UNIT)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_UNIT_IN_STACK_PREREQ", GC.getUnitInfo((UnitTypes)kSpellInfo.getUnitInStackPrereq()).getDescription()));
    }
    if (kSpellInfo.isAdjacentToWaterOnly()) // lfgr 09/2019: moved here
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_ADJACENT_TO_WATER_ONLY"));
    }
    if (kSpellInfo.isInBordersOnly() && kSpellInfo.isInCityOnly()) // lfgr 09/2019: moved here
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_IN_BORDERS_AND_CITY_ONLY"));
    }
    else
    {
        if (kSpellInfo.isInBordersOnly())
        {
            szBuffer.append(pcNewline);
            szBuffer.append(gDLL->getText("TXT_KEY_SPELL_IN_BORDERS_ONLY"));
        }
        if (kSpellInfo.isInCityOnly())
        {
            szBuffer.append(pcNewline);
            szBuffer.append(gDLL->getText("TXT_KEY_SPELL_IN_CITY_ONLY"));
        }
    }
    
    // lfgr 09/2019: Requires n+1 pop to remove n pop
	if( kSpellInfo.getChangePopulation() < 0 ) {
		szBuffer.append( pcNewline );
		szBuffer.append( gDLL->getText( "TXT_KEY_SPELL_PREREQ_POPULATION", 1 - kSpellInfo.getChangePopulation() ) );
	}

	// +++ Effects +++
	
    if (kSpellInfo.getCreateUnitType() != NO_UNIT)
    {
        szBuffer.append(pcNewline);
        if (kSpellInfo.getCreateUnitNum() == 1)
        {
            szBuffer.append(gDLL->getText("TXT_KEY_SPELL_SUMMON_UNIT", GC.getUnitInfo((UnitTypes)kSpellInfo.getCreateUnitType()).getDescription()));
        }
        else
        {
            szBuffer.append(gDLL->getText("TXT_KEY_SPELL_SUMMON_UNIT_MULTIPLE", kSpellInfo.getCreateUnitNum(), GC.getUnitInfo((UnitTypes)kSpellInfo.getCreateUnitType()).getDescription()));
        }
        if (kSpellInfo.isPermanentUnitCreate())
        {
            szBuffer.append(gDLL->getText("TXT_KEY_SPELL_SUMMON_UNIT_PERMANENT"));
        }
        if (kSpellInfo.isCopyCastersPromotions())
        {
            szBuffer.append(pcNewline);
            szBuffer.append(gDLL->getText("TXT_KEY_SPELL_COPY_CASTERS_PROMOTIONS"));
        }
    }
    if (kSpellInfo.getCreateUnitPromotion() != NO_PROMOTION)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_CREATE_UNIT_PROMOTION", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getCreateUnitPromotion()).getDescription()));
    }
    if (kSpellInfo.getDamage() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_DAMAGE", kSpellInfo.getDamage(), kSpellInfo.getDamageLimit()));
    }
    if (kSpellInfo.getAddPromotionType1() != NO_PROMOTION)
    {
        if (kSpellInfo.isBuffCasterOnly())
        {
            szBuffer.append(pcNewline);
            szBuffer.append(gDLL->getText("TXT_KEY_SPELL_ADD_PROMOTION_CASTER", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getAddPromotionType1()).getDescription()));
            if (kSpellInfo.getAddPromotionType2() != NO_PROMOTION)
            {
                szBuffer.append(pcNewline);
                szBuffer.append(gDLL->getText("TXT_KEY_SPELL_ADD_PROMOTION_CASTER", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getAddPromotionType2()).getDescription()));
            }
            if (kSpellInfo.getAddPromotionType3() != NO_PROMOTION)
            {
                szBuffer.append(pcNewline);
                szBuffer.append(gDLL->getText("TXT_KEY_SPELL_ADD_PROMOTION_CASTER", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getAddPromotionType3()).getDescription()));
            }
        }
        else
        {
            if (kSpellInfo.getRange() == 0)
            {
                szBuffer.append(pcNewline);
                szBuffer.append(gDLL->getText("TXT_KEY_SPELL_ADD_PROMOTION", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getAddPromotionType1()).getDescription()));
                if (kSpellInfo.getAddPromotionType2() != NO_PROMOTION)
                {
                    szBuffer.append(pcNewline);
                    szBuffer.append(gDLL->getText("TXT_KEY_SPELL_ADD_PROMOTION", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getAddPromotionType2()).getDescription()));
                }
                if (kSpellInfo.getAddPromotionType3() != NO_PROMOTION)
                {
                    szBuffer.append(pcNewline);
                    szBuffer.append(gDLL->getText("TXT_KEY_SPELL_ADD_PROMOTION", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getAddPromotionType3()).getDescription()));
                }
            }
            else
            {
                szBuffer.append(pcNewline);
                szBuffer.append(gDLL->getText("TXT_KEY_SPELL_ADD_PROMOTION_AT_RANGE", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getAddPromotionType1()).getDescription(), kSpellInfo.getRange()));
                if (kSpellInfo.getAddPromotionType2() != NO_PROMOTION)
                {
                    szBuffer.append(pcNewline);
                    szBuffer.append(gDLL->getText("TXT_KEY_SPELL_ADD_PROMOTION_AT_RANGE", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getAddPromotionType2()).getDescription(), kSpellInfo.getRange()));
                }
                if (kSpellInfo.getAddPromotionType3() != NO_PROMOTION)
                {
                    szBuffer.append(pcNewline);
                    szBuffer.append(gDLL->getText("TXT_KEY_SPELL_ADD_PROMOTION_AT_RANGE", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getAddPromotionType3()).getDescription(), kSpellInfo.getRange()));
                }
            }
        }
    }
    if (kSpellInfo.getRemovePromotionType1() != NO_PROMOTION)
    {
        if (kSpellInfo.isBuffCasterOnly())
        {
            szBuffer.append(pcNewline);
            szBuffer.append(gDLL->getText("TXT_KEY_SPELL_REMOVE_PROMOTION_CASTER", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getRemovePromotionType1()).getDescription()));
            if (kSpellInfo.getRemovePromotionType2() != NO_PROMOTION)
            {
                szBuffer.append(pcNewline);
                szBuffer.append(gDLL->getText("TXT_KEY_SPELL_REMOVE_PROMOTION_CASTER", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getRemovePromotionType2()).getDescription()));
            }
            if (kSpellInfo.getRemovePromotionType3() != NO_PROMOTION)
            {
                szBuffer.append(pcNewline);
                szBuffer.append(gDLL->getText("TXT_KEY_SPELL_REMOVE_PROMOTION_CASTER", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getRemovePromotionType3()).getDescription()));
            }
        }
        else
        {
            szBuffer.append(pcNewline);
            szBuffer.append(gDLL->getText("TXT_KEY_SPELL_REMOVE_PROMOTION", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getRemovePromotionType1()).getDescription()));
            if (kSpellInfo.getRemovePromotionType2() != NO_PROMOTION)
            {
                szBuffer.append(pcNewline);
                szBuffer.append(gDLL->getText("TXT_KEY_SPELL_REMOVE_PROMOTION", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getRemovePromotionType2()).getDescription()));
            }
            if (kSpellInfo.getRemovePromotionType3() != NO_PROMOTION)
            {
                szBuffer.append(pcNewline);
                szBuffer.append(gDLL->getText("TXT_KEY_SPELL_REMOVE_PROMOTION", GC.getPromotionInfo((PromotionTypes)kSpellInfo.getRemovePromotionType3()).getDescription()));
            }
        }
    }
    if (kSpellInfo.getRange() != 0 && kSpellInfo.getAddPromotionType1() == NO_PROMOTION)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_RANGE", kSpellInfo.getRange()));
    }
    if (kSpellInfo.getConvertUnitType() != NO_UNIT)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_CONVERT_UNIT", GC.getUnitInfo((UnitTypes)kSpellInfo.getConvertUnitType()).getDescription()));
    }
    if (kSpellInfo.getCreateBuildingType() != NO_BUILDING)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_CREATE_BUILDING", GC.getBuildingInfo((BuildingTypes)kSpellInfo.getCreateBuildingType()).getDescription()));
    }
    if (kSpellInfo.getCreateFeatureType() != NO_FEATURE)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_CREATE_FEATURE", GC.getFeatureInfo((FeatureTypes)kSpellInfo.getCreateFeatureType()).getDescription()));
    }
    if (kSpellInfo.getCreateImprovementType() != NO_IMPROVEMENT)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_CREATE_IMPROVEMENT", GC.getImprovementInfo((ImprovementTypes)kSpellInfo.getCreateImprovementType()).getDescription()));
    }
    if (kSpellInfo.getSpreadReligion() != NO_RELIGION)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_SPREAD_RELIGION", GC.getReligionInfo((ReligionTypes)kSpellInfo.getSpreadReligion()).getDescription()));
    }
    if (kSpellInfo.isDispel())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_DISPEL"));
    }
	if (wcslen(kSpellInfo.getHelp()) > 0)
	{
		szBuffer.append(pcNewline);
		szBuffer.append(kSpellInfo.getHelp());
	}
    if (kSpellInfo.isResistable())
    {
        if (kSpellInfo.getResistModify() != 0)
        {
            szBuffer.append(pcNewline);
            szBuffer.append(gDLL->getText("TXT_KEY_SPELL_RESIST_WITH_MODIFY", kSpellInfo.getResistModify()));
        }
        else
        {
            szBuffer.append(pcNewline);
            szBuffer.append(gDLL->getText("TXT_KEY_SPELL_RESIST"));
        }
    }
    if (kSpellInfo.isImmuneTeam() && !kSpellInfo.isImmuneNeutral() && !kSpellInfo.isImmuneEnemy())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_IMMUNE_TEAM"));
    }
    if (!kSpellInfo.isImmuneTeam() && kSpellInfo.isImmuneNeutral() && !kSpellInfo.isImmuneEnemy())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_IMMUNE_NEUTRAL"));
    }
    if (!kSpellInfo.isImmuneTeam() && !kSpellInfo.isImmuneNeutral() && kSpellInfo.isImmuneEnemy())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_IMMUNE_ENEMY"));
    }
    if (kSpellInfo.isImmuneTeam() && kSpellInfo.isImmuneNeutral() && !kSpellInfo.isImmuneEnemy())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_IMMUNE_TEAM_NEUTRAL"));
    }
    if (kSpellInfo.isImmuneTeam() && !kSpellInfo.isImmuneNeutral() && kSpellInfo.isImmuneEnemy())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_IMMUNE_TEAM_ENEMY"));
    }
    if (!kSpellInfo.isImmuneTeam() && kSpellInfo.isImmuneNeutral() && kSpellInfo.isImmuneEnemy())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_IMMUNE_NEUTRAL_ENEMY"));
    }
    if (kSpellInfo.isImmuneTeam() && kSpellInfo.isImmuneNeutral() && kSpellInfo.isImmuneEnemy())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_IMMUNE_TEAM_NEUTRAL_ENEMY"));
    }
    if (kSpellInfo.isImmuneFlying())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_IMMUNE_FLYING"));
    }
    if (kSpellInfo.isImmuneNotAlive())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_IMMUNE_NOT_ALIVE"));
    }
    if (kSpellInfo.isRemoveHasCasted())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_REMOVE_HAS_CASTED"));
    }

    int iCost;
	if( GC.getGameINLINE().getActivePlayer() != NO_PLAYER ) {
		iCost = info_utils::getRealSpellCost( GC.getGameINLINE().getActivePlayer(), eSpell );
	}
	else {
		iCost = kSpellInfo.getCost();
	}
	if( iCost > 0 ) {
		bool bCanPay = true;

		if( pvpUnits != NULL && pvpUnits->size() > 0 ) {
			// All selected units have the same owner
			bCanPay = GET_PLAYER( pvpUnits->at( 0 )->getOwnerINLINE() ).getGold() >= iCost;
		}

        szBuffer.append(pcNewline);
        if( bCanPay ) {
			szBuffer.append(gDLL->getText("TXT_KEY_SPELL_COST", iCost));
		}
		else {
			szBuffer.append(gDLL->getText("TXT_KEY_SPELL_COST_CANNOT_PAY", iCost));
		}
    }
	else if( iCost < 0 ) {
		szBuffer.append(pcNewline);
		szBuffer.append(gDLL->getText("TXT_KEY_SPELL_PROFIT", -iCost));
	}

    if (kSpellInfo.getDelay() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_DELAY", kSpellInfo.getDelay()));
    }

	
	// MiscastPromotions 10/2019 lfgr
	// If units are selected, possibly display a range of miscast chances
	int iMinMiscastChance = 100;
	int iMaxMiscastChance = 0;
	
	if( pvpUnits != NULL ) {
		for( size_t i = 0; i < pvpUnits->size(); i++ ) {
			int iUnitMiscastChance = pvpUnits->at( i )->getMiscastChance();
			iMinMiscastChance = std::min( iMinMiscastChance, kSpellInfo.getMiscastChance() + iUnitMiscastChance );
			iMaxMiscastChance = std::max( iMaxMiscastChance, kSpellInfo.getMiscastChance() + iUnitMiscastChance );
		}
	}
	else {
		iMinMiscastChance = std::min( 100, std::max( 0, kSpellInfo.getMiscastChance() ) );
		iMaxMiscastChance = iMinMiscastChance;
	}

	if( iMinMiscastChance != iMaxMiscastChance ) {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_MISCAST_CHANCE_RANGE", iMinMiscastChance, iMaxMiscastChance));
	}
	else if( iMinMiscastChance != 0 ) {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_MISCAST_CHANCE", iMinMiscastChance));
	}
	// MiscastPromotions end

    if (kSpellInfo.getImmobileTurns() != 0)
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_IMMOBILE_TURNS", kSpellInfo.getImmobileTurns()));
    }
    
    // lfgr 09/2019: Adds/removes n pop
	if( kSpellInfo.getChangePopulation() > 0 ) {
		szBuffer.append( pcNewline );
		szBuffer.append( gDLL->getText( "TXT_KEY_SPELL_ADD_POPULATION", kSpellInfo.getChangePopulation() ) );
	}
	else if( kSpellInfo.getChangePopulation() < 0 ) {
		szBuffer.append( pcNewline );
		szBuffer.append( gDLL->getText( "TXT_KEY_SPELL_REMOVE_POPULATION", -kSpellInfo.getChangePopulation() ) );
	}
    
/********************************************************************************/
/* SpellPyHelp                        11/2013                           lfgr    */
/********************************************************************************/
	if( pvpUnits != NULL && !CvString( GC.getSpellInfo( eSpell ).getPyHelp() ).empty() )
	{
		// Get owner of the units
		int iOwner = -1;
		int* aiUnitIDs = new int[pvpUnits->size()];
		for( uint i = 0; i < pvpUnits->size(); i++ )
		{
			if( iOwner == -1 )
				iOwner = pvpUnits->at( i )->getOwnerINLINE();
			else
				FAssertMsg( pvpUnits->at( i )->getOwnerINLINE() == iOwner, "Units with different onwers selected!" );
			aiUnitIDs[i] = pvpUnits->at( i )->getID();
		}

		if( iOwner != -1 )
		{
			CyArgsList argsList;
			argsList.add( (int) eSpell );
			argsList.add( (int) iOwner );
			argsList.add( aiUnitIDs, pvpUnits->size() );
		
			CvWString szHelp;
			gDLL->getPythonIFace()->callFunction(PYSpellModule, "getSpellHelp", argsList.makeFunctionArgs(), &szHelp);
		
			szBuffer.append( pcNewline );
			szBuffer.append( szHelp );
		}
	}
/********************************************************************************/
/* SpellPyHelp                                                          END     */
/********************************************************************************/
    if (kSpellInfo.isSacrificeCaster())
    {
        szBuffer.append(pcNewline);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_SACRIFICE_CASTER"));
    }
}
//FfH: End Add

// lfgr UI 11/2020: For "Allows civic" buttons in Tech tree.
void CvGameTextMgr::parseSingleCivicRevealHelp( CvWStringBuffer &szBuffer, CivicTypes eCivic )
{
	szBuffer.appendfmt( SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getCivicInfo( eCivic ).getDescription() );

	CvWStringBuffer szCivicHelpText;
	GAMETEXT.parseCivicInfo( szCivicHelpText, eCivic, true, true, true ); // bCiviliopedia=true to hide tech prereq
	szBuffer.append( szCivicHelpText );
}

//	Function:			parseCivicInfo()
//	Description:	Will parse the civic info help
//	Parameters:		szHelpText -- the text to put it into
//								civicInfo - what to parse
//	Returns:			nothing
void CvGameTextMgr::parseCivicInfo(CvWStringBuffer &szHelpText, CivicTypes eCivic, bool bCivilopediaText, bool bPlayerContext, bool bSkipName)
{
	PROFILE_FUNC();

	CvWString szFirstBuffer;
	bool bFound;
	bool bFirst;
	int iLast;
	int iI, iJ;

	if (NO_CIVIC == eCivic)
	{
		return;
	}

	szHelpText.clear();

	FAssert(GC.getGameINLINE().getActivePlayer() != NO_PLAYER || !bPlayerContext);

	CvCivicInfo& kCivic = GC.getCivicInfo(eCivic);

	if (!bSkipName)
	{
		szHelpText.append(kCivic.getDescription());
	}

	if (!bCivilopediaText)
	{
		if (!bPlayerContext || !(GET_PLAYER(GC.getGameINLINE().getActivePlayer()).canDoCivics(eCivic)))
		{
			if (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isHasTech((TechTypes)(kCivic.getTechPrereq()))))
			{
				if (kCivic.getTechPrereq() != NO_TECH)
				{
					szHelpText.append(NEWLINE);
					szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REQUIRES", GC.getTechInfo((TechTypes)kCivic.getTechPrereq()).getTextKeyWide()));
				}
			}
		}
	}

	// Special Building Not Required...
	for (iI = 0; iI < GC.getNumSpecialBuildingInfos(); ++iI)
	{
		if (kCivic.isSpecialBuildingNotRequired(iI))
		{
			// XXX "Missionaries"??? - Now in XML
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_BUILD_MISSIONARIES", GC.getSpecialBuildingInfo((SpecialBuildingTypes)iI).getTextKeyWide()));
		}
	}

	// Valid Specialists...

	bFirst = true;

	for (iI = 0; iI < GC.getNumSpecialistInfos(); ++iI)
	{
		if (kCivic.isSpecialistValid(iI))
		{
			szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_CIVIC_UNLIMTED").c_str());
			CvWString szSpecialist;
			szSpecialist.Format(L"<link=literal>%s</link>", GC.getSpecialistInfo((SpecialistTypes)iI).getDescription());
			setListHelp(szHelpText, szFirstBuffer, szSpecialist, L", ", bFirst);
			bFirst = false;
		}
	}

	//	Great People Modifier...
	if (kCivic.getGreatPeopleRateModifier() != 0)
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_GREAT_PEOPLE_MOD", kCivic.getGreatPeopleRateModifier()));
	}

	//	Great General Modifier...
	if (kCivic.getGreatGeneralRateModifier() != 0)
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_GREAT_GENERAL_MOD", kCivic.getGreatGeneralRateModifier()));
	}

	if (kCivic.getDomesticGreatGeneralRateModifier() != 0)
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_DOMESTIC_GREAT_GENERAL_MODIFIER", kCivic.getDomesticGreatGeneralRateModifier()));
	}

	//	State Religion Great People Modifier...
	if (kCivic.getStateReligionGreatPeopleRateModifier() != 0)
	{
		if (bPlayerContext && (GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getStateReligion() != NO_RELIGION))
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_GREAT_PEOPLE_MOD_RELIGION", kCivic.getStateReligionGreatPeopleRateModifier(), GC.getReligionInfo(GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getStateReligion()).getChar()));
		}
		else
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_GREAT_PEOPLE_MOD_STATE_RELIGION", kCivic.getStateReligionGreatPeopleRateModifier(), gDLL->getSymbolID(RELIGION_CHAR)));
		}
	}

	//	Distance Maintenance Modifer...
	if (kCivic.getDistanceMaintenanceModifier() != 0)
	{
		if (kCivic.getDistanceMaintenanceModifier() <= -100)
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_DISTANCE_MAINT"));
		}
		else
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_DISTANCE_MAINT_MOD", kCivic.getDistanceMaintenanceModifier()));
		}
	}

	//	Num Cities Maintenance Modifer...
	if (kCivic.getNumCitiesMaintenanceModifier() != 0)
	{
		if (kCivic.getNumCitiesMaintenanceModifier() <= -100)
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NO_MAINT_NUM_CITIES"));
		}
		else
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NO_MAINT_NUM_CITIES_MOD", kCivic.getNumCitiesMaintenanceModifier()));
		}
	}

	//	Corporations Maintenance Modifer...
	if (kCivic.getCorporationMaintenanceModifier() != 0)
	{
		if (kCivic.getCorporationMaintenanceModifier() <= -100)
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NO_MAINT_CORPORATION"));
		}
		else
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NO_MAINT_CORPORATION_MOD", kCivic.getCorporationMaintenanceModifier()));
		}
	}

	//	Extra Health
	if (kCivic.getExtraHealth() != 0)
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_EXTRA_HEALTH", abs(kCivic.getExtraHealth()), ((kCivic.getExtraHealth() > 0) ? gDLL->getSymbolID(HEALTHY_CHAR): gDLL->getSymbolID(UNHEALTHY_CHAR))));
	}

	//	Free Experience
	if (kCivic.getFreeExperience() != 0)
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_FREE_XP", kCivic.getFreeExperience()));
	}

	//	Worker speed modifier
	if (kCivic.getWorkerSpeedModifier() != 0)
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_WORKER_SPEED", kCivic.getWorkerSpeedModifier()));
	}

	//	Improvement upgrade rate modifier
	if (kCivic.getImprovementUpgradeRateModifier() != 0)
	{
		bFirst = true;

		for (iI = 0; iI < GC.getNumImprovementInfos(); ++iI)
		{
			if (GC.getImprovementInfo((ImprovementTypes)iI).getImprovementUpgrade() != NO_IMPROVEMENT)
			{
				szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_CIVIC_IMPROVEMENT_UPGRADE", kCivic.getImprovementUpgradeRateModifier()).c_str());
				CvWString szImprovement;
				szImprovement.Format(L"<link=literal>%s</link>", GC.getImprovementInfo((ImprovementTypes)iI).getDescription());
				setListHelp(szHelpText, szFirstBuffer, szImprovement, L", ", bFirst);
				bFirst = false;
			}
		}
	}

	//	Military unit production modifier
	if (kCivic.getMilitaryProductionModifier() != 0)
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_MILITARY_PRODUCTION", kCivic.getMilitaryProductionModifier()));
	}

	//	Free units population percent
	if ((kCivic.getBaseFreeUnits() != 0) || (kCivic.getFreeUnitsPopulationPercent() != 0))
	{
		if (bPlayerContext)
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_FREE_UNITS", (kCivic.getBaseFreeUnits() + ((GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getTotalPopulation() * kCivic.getFreeUnitsPopulationPercent()) / 100))));
		}
		else
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_UNIT_SUPPORT"));
		}
	}

	//	Free military units population percent
	if ((kCivic.getBaseFreeMilitaryUnits() != 0) || (kCivic.getFreeMilitaryUnitsPopulationPercent() != 0))
	{
		if (bPlayerContext)
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_FREE_MILITARY_UNITS", (kCivic.getBaseFreeMilitaryUnits() + ((GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getTotalPopulation() * kCivic.getFreeMilitaryUnitsPopulationPercent()) / 100))));
		}
		else
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_MILITARY_UNIT_SUPPORT"));
		}
	}

	//	Happiness per military unit
	if (kCivic.getHappyPerMilitaryUnit() != 0)
	{
		szHelpText.append(NEWLINE);
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       08/28/09                            jdog5000          */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_UNIT_HAPPINESS", kCivic.getHappyPerMilitaryUnit(), ((kCivic.getHappyPerMilitaryUnit() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR))));

*/
		// Use absolute value with unhappy face
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_UNIT_HAPPINESS", abs(kCivic.getHappyPerMilitaryUnit()), ((kCivic.getHappyPerMilitaryUnit() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR))));
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
	}

	//	Military units produced with food
	if (kCivic.isMilitaryFoodProduction())
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_MILITARY_FOOD"));
	}

	//	Conscription
	if (getWorldSizeMaxConscript(eCivic) != 0)
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_CONSCRIPTION", getWorldSizeMaxConscript(eCivic)));
	}

	//	Population Unhealthiness
	if (kCivic.isNoUnhealthyPopulation())
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NO_POP_UNHEALTHY"));
	}

	//	Building Unhealthiness
	if (kCivic.isBuildingOnlyHealthy())
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NO_BUILDING_UNHEALTHY"));
	}

	//	Population Unhealthiness
	if (0 != kCivic.getExpInBorderModifier())
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_EXPERIENCE_IN_BORDERS", kCivic.getExpInBorderModifier()));
	}
	
/************************************************************************************************/
/* REVDCM                                 02/16/10                                phungus420    */
/*                                                                                              */
/* RevCivic Effects                                                                             */
/************************************************************************************************/
	if (kCivic.isDisallowInquisitions())
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_DISALLOW_INQUISITONS"));
	}

	if (GC.getGameINLINE().isOption(GAMEOPTION_REVOLUTIONS))
	{
		//  Revolution Local Civic Index Modifiers
		if (0 != kCivic.getRevIdxLocal())
		{
			if ( kCivic.getRevIdxLocal() > 0 )
			{
				szHelpText.append(NEWLINE);
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_INDEX_LOCAL_PENALTY", kCivic.getRevIdxLocal()));
			}
			if ( kCivic.getRevIdxLocal() < 0 )
			{
				szHelpText.append(NEWLINE);
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_INDEX_LOCAL_BONUS", abs(kCivic.getRevIdxLocal())));
			}
		}
		
		//  Revolution National Civic Index Modifiers
		if (0 != kCivic.getRevIdxNational())
		{
			if ( kCivic.getRevIdxNational() > 0 )
			{
				szHelpText.append(NEWLINE);
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_INDEX_NATIONAL_PENALTY", kCivic.getRevIdxNational()));
			}
			if ( kCivic.getRevIdxNational() < 0 )
			{
				szHelpText.append(NEWLINE);
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_INDEX_NATIONAL_BONUS", abs(kCivic.getRevIdxNational())));
			}
		}
		
		//  Revolution City Distance Modifier
		if (0 != kCivic.getRevIdxDistanceModifier())
		{
			if ( kCivic.getRevIdxDistanceModifier() < 0 )
			{
				szHelpText.append(NEWLINE);
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_CITY_DISTANCE_GOOD_MOD", kCivic.getRevIdxDistanceModifier()));
			}
			if ( kCivic.getRevIdxDistanceModifier() > 0 )
			{
				szHelpText.append(NEWLINE);
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_CITY_DISTANCE_BAD_MOD", abs(kCivic.getRevIdxDistanceModifier())));
			}
		}
		
		//  Revolution Good Holy City Modifier
		if (0 != kCivic.getRevIdxHolyCityGood())
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_GOOD_HOLY_CITY", kCivic.getRevIdxHolyCityGood()));
		}
		
		//  Revolution Bad Holy City Modifier
		if (0 != kCivic.getRevIdxHolyCityBad())
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_BAD_HOLY_CITY", kCivic.getRevIdxHolyCityBad()));
		}
		
		//  Revolution Switch to Modifier
		/*
		if (0 != kCivic.getRevIdxSwitchTo())
		{
			if (kCivic.getRevIdxSwitchTo() < 0)
			{
				szHelpText.append(NEWLINE);
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_SWITCH_TO_BONUS", abs(kCivic.getRevIdxSwitchTo())));
			}
			if (kCivic.getRevIdxSwitchTo() > 0)
			{
				szHelpText.append(NEWLINE);
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_SWITCH_TO_PENALTY", kCivic.getRevIdxSwitchTo()));
			}
		}
		*/
		//  Revolution Nationality Modifier
		if (0 != kCivic.getRevIdxNationalityMod())
		{
			if ( kCivic.getRevIdxNationalityMod() < 0)
			{
				szHelpText.append(NEWLINE);
				CvWString szTempBuffer;
				szTempBuffer.Format(L"%.0f", 100 * kCivic.getRevIdxNationalityMod());
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_NATIONALITY_REDUCTION_MOD", szTempBuffer.GetCString()));
			}
			if ( kCivic.getRevIdxNationalityMod() > 0)
			{
				szHelpText.append(NEWLINE);
				CvWString szTempBuffer;
				szTempBuffer.Format(L"%.0f", 100 * kCivic.getRevIdxNationalityMod());
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_NATIONALITY_INCREASE_MOD", szTempBuffer.GetCString()));
			}
		}
		
		//  Revolution Bad Religion Modifier
		if (0 != kCivic.getRevIdxBadReligionMod())
		{
			szHelpText.append(NEWLINE);
			CvWString szTempBuffer;
			szTempBuffer.Format(L"%.0f", 100 * kCivic.getRevIdxBadReligionMod());
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_BAD_RELIGION_MOD", szTempBuffer.GetCString()));
		}
		
		//  Revolution Good Religion Modifier
		if (0 != kCivic.getRevIdxGoodReligionMod())
		{
			szHelpText.append(NEWLINE);
			CvWString szTempBuffer;
			szTempBuffer.Format(L"%.0f", 100 * kCivic.getRevIdxGoodReligionMod());
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_GOOD_RELIGION_MOD", szTempBuffer.GetCString()));
		}
		
		//  Revolution Religious Freedom Modifier
		/*
		if (0 != kCivic.getRevReligiousFreedom())
		{
			if ( kCivic.getRevReligiousFreedom() < 0 )
			{
				szHelpText.append(NEWLINE);
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_RELIGION_OPRESSION", kCivic.getRevReligiousFreedom()));
			}
			if ( kCivic.getRevReligiousFreedom() > 0 )
			{
				szHelpText.append(NEWLINE);
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_RELIGION_FREEDOM", kCivic.getRevReligiousFreedom()));
			}
		}
		*/
		/*
		//  Revolution Labor Modifier
		if (0 != kCivic.getRevLaborFreedom())
		{
				szHelpText.append(NEWLINE);
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_LABOR", kCivic.getRevLaborFreedom()));
		}
		*/
		/*
		//  Revolution Environment Modifier
		if (0 != kCivic.getRevEnvironmentalProtection())
		{
				szHelpText.append(NEWLINE);
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_ENVIRONMENT", kCivic.getRevEnvironmentalProtection()));
		}
		*/
		/*
		//  Revolution Democracy Modifier
		if (0 != kCivic.getRevDemocracyLevel())
		{
				szHelpText.append(NEWLINE);
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REV_DEMOCRACY", kCivic.getRevDemocracyLevel()));
		}
		*/
	}
/************************************************************************************************/
/* REVDCM                                  END                                                  */
/************************************************************************************************/

	//	War Weariness
	if (kCivic.getWarWearinessModifier() != 0)
	{
		if (kCivic.getWarWearinessModifier() <= -100)
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NO_WAR_WEARINESS"));
		}
		else
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_EXTRA_WAR_WEARINESS", kCivic.getWarWearinessModifier()));
		}
	}

	//	Free specialists
	if (kCivic.getFreeSpecialist() != 0)
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_FREE_SPECIALISTS", kCivic.getFreeSpecialist()));
	}

	//	Trade routes
	if (kCivic.getTradeRoutes() != 0)
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_TRADE_ROUTES", kCivic.getTradeRoutes()));
	}

	//	No Foreign Trade
	if (kCivic.isNoForeignTrade())
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NO_FOREIGN_TRADE"));
	}

	//	No Corporations
	if (kCivic.isNoCorporations())
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NO_CORPORATIONS"));
	}

	//	No Foreign Corporations
	if (kCivic.isNoForeignCorporations())
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NO_FOREIGN_CORPORATIONS"));
	}

	//	Freedom Anger
	if (kCivic.getCivicPercentAnger() != 0)
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_FREEDOM_ANGER", kCivic.getTextKeyWide()));
	}

	if (!(kCivic.isStateReligion()))
	{
		bFound = false;

		for (iI = 0; iI < GC.getNumCivicInfos(); ++iI)
		{
			if ((GC.getCivicInfo((CivicTypes) iI).getCivicOptionType() == kCivic.getCivicOptionType()) && (GC.getCivicInfo((CivicTypes) iI).isStateReligion()))
			{
				bFound = true;
			}
		}

		if (bFound)
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NO_STATE_RELIGION"));
		}
	}

	if (kCivic.getStateReligionHappiness() != 0)
	{
		if (bPlayerContext && (GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getStateReligion() != NO_RELIGION))
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_STATE_RELIGION_HAPPINESS", abs(kCivic.getStateReligionHappiness()), ((kCivic.getStateReligionHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)), GC.getReligionInfo(GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getStateReligion()).getChar()));
		}
		else
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_RELIGION_HAPPINESS", abs(kCivic.getStateReligionHappiness()), ((kCivic.getStateReligionHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR))));
		}
	}

	if (kCivic.getNonStateReligionHappiness() != 0)
	{
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       08/28/09                  EmperorFool & jdog5000      */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
		if (kCivic.isStateReligion())
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NON_STATE_REL_HAPPINESS_NO_STATE"));
		}
		else
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NON_STATE_REL_HAPPINESS_WITH_STATE", abs(kCivic.getNonStateReligionHappiness()), ((kCivic.getNonStateReligionHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR))));
		}
*/
		if (!kCivic.isStateReligion())
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NON_STATE_REL_HAPPINESS_NO_STATE", abs(kCivic.getNonStateReligionHappiness()), ((kCivic.getNonStateReligionHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR))));
		}
		else
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NON_STATE_REL_HAPPINESS_WITH_STATE", abs(kCivic.getNonStateReligionHappiness()), ((kCivic.getNonStateReligionHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR))));
		}
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
	}

	//	State Religion Unit Production Modifier
	if (kCivic.getStateReligionUnitProductionModifier() != 0)
	{
		if (bPlayerContext && (GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getStateReligion() != NO_RELIGION))
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REL_TRAIN_BONUS", GC.getReligionInfo(GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getStateReligion()).getChar(), kCivic.getStateReligionUnitProductionModifier()));
		}
		else
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_STATE_REL_TRAIN_BONUS", kCivic.getStateReligionUnitProductionModifier()));
		}
	}

	//	State Religion Building Production Modifier
	if (kCivic.getStateReligionBuildingProductionModifier() != 0)
	{
		if (bPlayerContext && (GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getStateReligion() != NO_RELIGION))
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REL_BUILDING_BONUS", GC.getReligionInfo(GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getStateReligion()).getChar(), kCivic.getStateReligionBuildingProductionModifier()));
		}
		else
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_STATE_REL_BUILDING_BONUS", kCivic.getStateReligionBuildingProductionModifier()));
		}
	}

	//	State Religion Free Experience
	if (kCivic.getStateReligionFreeExperience() != 0)
	{
		if (bPlayerContext && (GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getStateReligion() != NO_RELIGION))
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REL_FREE_XP", kCivic.getStateReligionFreeExperience(), GC.getReligionInfo(GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getStateReligion()).getChar()));
		}
		else
		{
			szHelpText.append(NEWLINE);
			szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_STATE_REL_FREE_XP", kCivic.getStateReligionFreeExperience()));
		}
	}

	if (kCivic.isNoNonStateReligionSpread())
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NO_NON_STATE_SPREAD"));
	}

	//	Yield Modifiers
	setYieldChangeHelp(szHelpText, L"", L"", gDLL->getText("TXT_KEY_CIVIC_IN_ALL_CITIES").GetCString(), kCivic.getYieldModifierArray(), true);

	//	Capital Yield Modifiers
	setYieldChangeHelp(szHelpText, L"", L"", gDLL->getText("TXT_KEY_CIVIC_IN_CAPITAL").GetCString(), kCivic.getCapitalYieldModifierArray(), true);

	//	Trade Yield Modifiers
	setYieldChangeHelp(szHelpText, L"", L"", gDLL->getText("TXT_KEY_CIVIC_FROM_TRADE_ROUTES").GetCString(), kCivic.getTradeYieldModifierArray(), true);

	//	Commerce Modifier
	setCommerceChangeHelp(szHelpText, L"", L"", gDLL->getText("TXT_KEY_CIVIC_IN_ALL_CITIES").GetCString(), kCivic.getCommerceModifierArray(), true);

	//	Capital Commerce Modifiers
	setCommerceChangeHelp(szHelpText, L"", L"", gDLL->getText("TXT_KEY_CIVIC_IN_CAPITAL").GetCString(), kCivic.getCapitalCommerceModifierArray(), true);

	//	Specialist Commerce
	setCommerceChangeHelp(szHelpText, L"", L"", gDLL->getText("TXT_KEY_CIVIC_PER_SPECIALIST").GetCString(), kCivic.getSpecialistExtraCommerceArray());

	//	Largest City Happiness
	if (kCivic.getLargestCityHappiness() != 0)
	{
		szHelpText.append(NEWLINE);
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       08/28/09                            jdog5000          */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_LARGEST_CITIES_HAPPINESS", kCivic.getLargestCityHappiness(), ((kCivic.getLargestCityHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)), GC.getWorldInfo(GC.getMapINLINE().getWorldSize()).getTargetNumCities()));
*/
		// Use absolute value with unhappy face
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_LARGEST_CITIES_HAPPINESS", abs(kCivic.getLargestCityHappiness()), ((kCivic.getLargestCityHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)), GC.getWorldInfo(GC.getMapINLINE().getWorldSize()).getTargetNumCities()));
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
	}

	//	Improvement Yields
	for (iI = 0; iI < NUM_YIELD_TYPES; ++iI)
	{
		iLast = 0;

		for (iJ = 0; iJ < GC.getNumImprovementInfos(); iJ++)
		{
			if (kCivic.getImprovementYieldChanges(iJ, iI) != 0)
			{
				szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_CIVIC_IMPROVEMENT_YIELD_CHANGE", kCivic.getImprovementYieldChanges(iJ, iI), GC.getYieldInfo((YieldTypes)iI).getChar()).c_str());
				CvWString szImprovement;
				szImprovement.Format(L"<link=literal>%s</link>", GC.getImprovementInfo((ImprovementTypes)iJ).getDescription());
				setListHelp(szHelpText, szFirstBuffer, szImprovement, L", ", (kCivic.getImprovementYieldChanges(iJ, iI) != iLast));
				iLast = kCivic.getImprovementYieldChanges(iJ, iI);
			}
		}
	}

	//	Building Happiness
	for (iI = 0; iI < GC.getNumBuildingClassInfos(); ++iI)
	{
		if (kCivic.getBuildingHappinessChanges(iI) != 0)
		{
			if (bPlayerContext && NO_PLAYER != GC.getGameINLINE().getActivePlayer())
			{
				BuildingTypes eBuilding = (BuildingTypes)GC.getCivilizationInfo(GC.getGameINLINE().getActiveCivilizationType()).getCivilizationBuildings(iI);
				if (NO_BUILDING != eBuilding)
				{
					szHelpText.append(NEWLINE);
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       08/28/09                            jdog5000          */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
					szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_BUILDING_HAPPINESS", kCivic.getBuildingHappinessChanges(iI), ((kCivic.getBuildingHappinessChanges(iI) > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)), GC.getBuildingInfo(eBuilding).getTextKeyWide()));
*/
					// Use absolute value with unhappy face
					szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_BUILDING_HAPPINESS", abs(kCivic.getBuildingHappinessChanges(iI)), ((kCivic.getBuildingHappinessChanges(iI) > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)), GC.getBuildingInfo(eBuilding).getTextKeyWide()));
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
				}
			}
			else
			{
				szHelpText.append(NEWLINE);
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       08/28/09                            jdog5000          */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_BUILDING_HAPPINESS", kCivic.getBuildingHappinessChanges(iI), ((kCivic.getBuildingHappinessChanges(iI) > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)), GC.getBuildingClassInfo((BuildingClassTypes)iI).getTextKeyWide()));
*/
				// Use absolute value with unhappy face
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_BUILDING_HAPPINESS", abs(kCivic.getBuildingHappinessChanges(iI)), ((kCivic.getBuildingHappinessChanges(iI) > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)), GC.getBuildingClassInfo((BuildingClassTypes)iI).getTextKeyWide()));
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
			}
		}

		if (kCivic.getBuildingHealthChanges(iI) != 0)
		{
			if (bPlayerContext && NO_PLAYER != GC.getGameINLINE().getActivePlayer())
			{
				BuildingTypes eBuilding = (BuildingTypes)GC.getCivilizationInfo(GC.getGameINLINE().getActiveCivilizationType()).getCivilizationBuildings(iI);
				if (NO_BUILDING != eBuilding)
				{
					szHelpText.append(NEWLINE);
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       08/28/09                             jdog5000         */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
					szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_BUILDING_HAPPINESS", kCivic.getBuildingHealthChanges(iI), ((kCivic.getBuildingHealthChanges(iI) > 0) ? gDLL->getSymbolID(HEALTHY_CHAR) : gDLL->getSymbolID(UNHEALTHY_CHAR)), GC.getBuildingInfo(eBuilding).getTextKeyWide()));
*/
					// Use absolute value with unhealthy symbol
					szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_BUILDING_HAPPINESS", abs(kCivic.getBuildingHealthChanges(iI)), ((kCivic.getBuildingHealthChanges(iI) > 0) ? gDLL->getSymbolID(HEALTHY_CHAR) : gDLL->getSymbolID(UNHEALTHY_CHAR)), GC.getBuildingInfo(eBuilding).getTextKeyWide()));
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
				}
			}
			else
			{
				szHelpText.append(NEWLINE);
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       08/28/09                             jdog5000         */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_BUILDING_HAPPINESS", kCivic.getBuildingHealthChanges(iI), ((kCivic.getBuildingHealthChanges(iI) > 0) ? gDLL->getSymbolID(HEALTHY_CHAR) : gDLL->getSymbolID(UNHEALTHY_CHAR)), GC.getBuildingClassInfo((BuildingClassTypes)iI).getTextKeyWide()));
*/
				// Use absolute value with unhealthy symbol
				szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_BUILDING_HAPPINESS", abs(kCivic.getBuildingHealthChanges(iI)), ((kCivic.getBuildingHealthChanges(iI) > 0) ? gDLL->getSymbolID(HEALTHY_CHAR) : gDLL->getSymbolID(UNHEALTHY_CHAR)), GC.getBuildingClassInfo((BuildingClassTypes)iI).getTextKeyWide()));
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
			}
		}
	}

	//	Feature Happiness
	iLast = 0;

	for (iI = 0; iI < GC.getNumFeatureInfos(); ++iI)
	{
		if (kCivic.getFeatureHappinessChanges(iI) != 0)
		{
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       08/28/09                             jdog5000         */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
			szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_CIVIC_FEATURE_HAPPINESS", kCivic.getFeatureHappinessChanges(iI), ((kCivic.getFeatureHappinessChanges(iI) > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR))).c_str());
*/
			// Use absolute value with unhappy face
			szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_CIVIC_FEATURE_HAPPINESS", abs(kCivic.getFeatureHappinessChanges(iI)), ((kCivic.getFeatureHappinessChanges(iI) > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR))).c_str());
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
			CvWString szFeature;
			szFeature.Format(L"<link=literal>%s</link>", GC.getFeatureInfo((FeatureTypes)iI).getDescription());
			setListHelp(szHelpText, szFirstBuffer, szFeature, L", ", (kCivic.getFeatureHappinessChanges(iI) != iLast));
			iLast = kCivic.getFeatureHappinessChanges(iI);
		}
	}

	//	Hurry types
	for (iI = 0; iI < GC.getNumHurryInfos(); ++iI)
	{
		if (kCivic.isHurry(iI))
		{
			szHelpText.append(CvWString::format(L"%s%c%s", NEWLINE, gDLL->getSymbolID(BULLET_CHAR), GC.getHurryInfo((HurryTypes)iI).getDescription()));
		}
	}

//FfH: Added by Kael 08/11/2007
    if (kCivic.isPrereqWar())
    {
        if (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).getAtWarCount(true) > 0))
        {
            szHelpText.append(NEWLINE);
            szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_PREREQ_WAR"));
        }
    }
    if (kCivic.getBlockAlignment() != NO_ALIGNMENT)
    {
        if (!bPlayerContext || GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getAlignment() == kCivic.getBlockAlignment())
        {
            szHelpText.append(NEWLINE);
            szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_BLOCKS", GC.getAlignmentInfo((AlignmentTypes)kCivic.getBlockAlignment()).getDescription()));
        }
    }
    if (kCivic.getPrereqAlignment() != NO_ALIGNMENT)
    {
        if (!bPlayerContext || GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getAlignment() != kCivic.getPrereqAlignment())
        {
            szHelpText.append(NEWLINE);
            szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REQUIRES", GC.getAlignmentInfo((AlignmentTypes)kCivic.getPrereqAlignment()).getDescription()));
        }
    }
    if (kCivic.getPrereqCivilization() != NO_CIVILIZATION)
    {
        if (!bPlayerContext || GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getCivilizationType() != kCivic.getPrereqCivilization())
        {
            szHelpText.append(NEWLINE);
            szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REQUIRES", GC.getCivilizationInfo((CivilizationTypes)kCivic.getPrereqCivilization()).getDescription()));
        }
    }
    if (kCivic.getPrereqReligion() != NO_RELIGION)
    {
        if (!bPlayerContext || GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getStateReligion() != kCivic.getPrereqReligion())
        {
            szHelpText.append(NEWLINE);
            szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_REQUIRES", GC.getReligionInfo((ReligionTypes)kCivic.getPrereqReligion()).getDescription()));
        }
    }
    if (kCivic.isNoDiplomacyWithEnemies())
    {
        szHelpText.append(NEWLINE);
        szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_NO_DIPLOMACY_WITH_ENEMIES"));
    }
    if (kCivic.getCoastalTradeRoutes() != 0)
    {
        szHelpText.append(NEWLINE);
        szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_COASTAL_TRADE_ROUTES", kCivic.getCoastalTradeRoutes()));
    }
    if (kCivic.getEnslavementChance() != 0)
    {
        szHelpText.append(NEWLINE);
        szHelpText.append(gDLL->getText("TXT_KEY_UNIT_ENSLAVEMENT_CHANCE", kCivic.getEnslavementChance()));
    }
    if (kCivic.getFoodConsumptionPerPopulation() != 0)
    {
        szHelpText.append(NEWLINE);
        szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_FOOD_CONSUMPTION_PER_POPULATION", kCivic.getFoodConsumptionPerPopulation(), GC.getFOOD_CONSUMPTION_PER_POPULATION()));
    }
//FfH: End Add

	//	Gold cost per unit
	if (kCivic.getGoldPerUnit() != 0)
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_SUPPORT_COSTS", (kCivic.getGoldPerUnit() > 0), GC.getCommerceInfo(COMMERCE_GOLD).getChar()));
	}

	//	Gold cost per military unit
	if (kCivic.getGoldPerMilitaryUnit() != 0)
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_MILITARY_SUPPORT_COSTS", (kCivic.getGoldPerMilitaryUnit() > 0), GC.getCommerceInfo(COMMERCE_GOLD).getChar()));
	}
/************************************************************************************************/
/* Advanced Diplomacy         START                                                               */
/************************************************************************************************/
	//Active Senate
	if (GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS) && GC.getCivicInfo(eCivic).isActiveSenate())
	{
		szHelpText.append(NEWLINE);
		szHelpText.append(gDLL->getText("TXT_KEY_CIVIC_ACTIVE_SENATE"));
	}
/************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/************************************************************************************************/

	if (!CvWString(kCivic.getHelp()).empty())
	{
		szHelpText.append(CvWString::format(L"%s%s", NEWLINE, kCivic.getHelp()).c_str());
	}
}

// VOTE_HELP 11/2019 lfgr
void CvGameTextMgr::parseVoteInfo( CvWStringBuffer &szHelpText, VoteTypes eVote,
		VoteSourceTypes eVoteSource, PlayerTypes ePlayer, int iCity, PlayerTypes eOtherPlayer,
		bool bRequirements ) {
	PROFILE_FUNC();

	if( eVote == NO_VOTE ) {
		return;
	}
	
	CvVoteInfo& kVote = GC.getVoteInfo( eVote );
	
	// Use first eligible vote source if none is specified
	// LFGR_TODO?
	if( eVoteSource == NO_VOTESOURCE ) {
		for( int eLoopVoteSource = 0; eLoopVoteSource < GC.getNumVoteSourceInfos(); eLoopVoteSource++ ) {
			if( kVote.isVoteSourceType( eLoopVoteSource ) ) {
				eVoteSource = (VoteSourceTypes) eLoopVoteSource;
				break;
			}
		}
	}

	ReligionTypes eVoteSourceReligion = NO_RELIGION;
	if( eVoteSource != NO_VOTESOURCE ) {
		eVoteSourceReligion = GC.getGameINLINE().getVoteSourceReligion( eVoteSource );
	}
	
	// Voting

	if( eVoteSource != NO_VOTESOURCE && GC.getGameINLINE().getActivePlayer() != NO_PLAYER ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_REQUIRED_VOTES",
			GC.getGameINLINE().getVoteRequired( eVote, eVoteSource ),
			GC.getGameINLINE().countPossibleVote( eVote, eVoteSource )) );
	}
	else if( kVote.getPopulationThreshold() != 50 ) {
		// Show percentage if no game is running or no vote source is specified.
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_POPULATION_THRESHOLD",
				kVote.getPopulationThreshold() ) );
	}
	
	if( kVote.getStateReligionVotePercent() != 0 ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_STATE_RELIGION_VOTE_PERCENT",
				kVote.getStateReligionVotePercent() ) );
	}
	
	// Minimum voters
	if( bRequirements && kVote.getMinVoters() > 0 ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_MIN_VOTERS", kVote.getMinVoters() ) );
	}

	// "All players have to be voters"
	if( bRequirements && kVote.isVictory() ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_ALL_PLAYERS" ) );
	}
	
	if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );

	if( kVote.isCivVoting() ) {
		if( eVoteSourceReligion == NO_RELIGION ) { // LFGR_TODO: What if vote source has religion, but we are in pedia?
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_CIV_VOTING" ) );
		}
		else {
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_CIV_VOTING_RELIGION",
				GC.getReligionInfo( eVoteSourceReligion ).getChar() ) );
		}
	}
	else if( kVote.isCityVoting() ) {
		if( eVoteSourceReligion == NO_RELIGION ) {
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_CITY_VOTING" ) );
		}
		else {
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_CITY_VOTING_RELIGION",
				GC.getReligionInfo( eVoteSourceReligion ).getChar() ) );
		}
	}
	else {
		if( eVoteSourceReligion == NO_RELIGION ) {
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_POP_VOTING" ) );
		}
		else {
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_POP_VOTING_RELIGION",
				GC.getReligionInfo( eVoteSourceReligion ).getChar() ) );
		}
	}
	
	// Special resolutions
	
	if( kVote.isSecretaryGeneral() && eVoteSource != NO_VOTESOURCE ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		
		CvWString szSecGenText = GC.getVoteSourceInfo( eVoteSource ).getSecretaryGeneralText();
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_SEC_GEN_ELECTION", szSecGenText.c_str() ) );
	}

	if( kVote.isVictory() ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_VICTORY" ) );
	}
	
	
	// Effects
	
	if( kVote.getTradeRoutes() != 0 ) { // LFGR_TODO: Only for members
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_TRADE_ROUTES", kVote.getTradeRoutes() ) );
	}
	
	if( kVote.isNoNukes() ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_NO_NUKES" ) );
	}
	
	if( kVote.isDefensivePact() ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_DEFENSIVE_PACT" ) );
	}

	// LFGR_TODO: Limited borders, embassies, non-agression pact (?)
	
	if( kVote.isOpenBorders() ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_OPEN_BORDERS" ) );
	}
	
	if( kVote.isForcePeace() ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );

		if( ePlayer != NO_PLAYER ) {
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_FORCE_PEACE",
					GET_PLAYER( ePlayer ).getNameKey() ) );
		}
		else {
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_FORCE_PEACE_SOMEONE" ) );
		}
	}
	
	if( kVote.isForceNoTrade() ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );

		if( ePlayer != NO_PLAYER ) {
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_FORCE_NO_TRADE",
					GET_PLAYER( ePlayer ).getNameKey() ) );
		}
		else {
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_FORCE_NO_TRADE_SOMEONE" ) );
		}
	}
	
	if( kVote.isForceWar() ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );

		if( ePlayer != NO_PLAYER ) {
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_FORCE_WAR",
					GET_PLAYER( ePlayer ).getNameKey() ) );
		}
		else {
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_FORCE_WAR_SOMEONE" ) );
		}
	}

	if( kVote.isFreeTrade() ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_FREE_TRADE" ) );
	}
	
	if( kVote.isNoOutsideTechTrades() ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_NO_OUTSIDE_TECH_TRADES" ) );
	}

	if( kVote.getFreeUnits() > 0 ) {
		FAssertMsg( kVote.getFreeUnitClass() != NO_UNITCLASS, "Cannot have iFreeUnits > 0, but no FreeUnitClass in VoteInfo" );
		
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		
		CvWString szUnit;
		if( kVote.getFreeUnits() == 1 ) {
			szUnit = gDLL->getText( "%s1",
				GC.getUnitClassInfo( (UnitClassTypes) kVote.getFreeUnitClass() ).getTextKeyWide() );
		}
		else {
			szUnit = gDLL->getText( "%d1 %s1", kVote.getFreeUnits(),
					GC.getUnitClassInfo( (UnitClassTypes) kVote.getFreeUnitClass() ).getTextKeyWide() );
		}

		if( kVote.getCost() > 0 ) {
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_RECEIVE_UNIT_COST",
				kVote.getCost(), GC.getCommerceInfo( COMMERCE_GOLD ).getChar(), szUnit.c_str() ) );
		}
		else {
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_RECEIVE_UNIT", szUnit.c_str() ) );
		}
	}

	if( kVote.getCrime() != 0 ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_CRIME", kVote.getCrime() ) );
	}

	if( kVote.getNoBonus() != NO_BONUS ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_NO_BONUS",
				GC.getBonusInfo( (BonusTypes) kVote.getNoBonus() ).getChar() ) );
	}

	if( kVote.isTradeMap() ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_TRADE_MAP" ) );
	}

	for( int eCivic = 0; eCivic < GC.getNumCivicInfos(); eCivic++ ) {
		if( kVote.isForceCivic( eCivic ) ) {
			if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_FORCE_CIVIC",
				GC.getCivicInfo( (CivicTypes) eCivic ).getTextKeyWide() ) );
		}
	}

	if( kVote.isAssignCity() ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		if( ePlayer != NO_PLAYER ) {
			FAssertMsg( iCity != -1 && eOtherPlayer != NO_PLAYER,
					"Invalid arguments to parseVoteInfo: iAssignCity, ePlayer != NO_PLAYER, but "
					"iCity == -1 or eOtherPlayer == NO_PLAYER" );
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_REASSIGN_CITY_FROM_TO",
					GET_PLAYER( ePlayer ).getCity( iCity )->getName(),
					GET_PLAYER( ePlayer ).getNameKey(),
					GET_PLAYER( eOtherPlayer ).getNameKey() ) );
		}
		else {
			szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_REASSIGN_CITY" ) );
		}
	}

	if( kVote.isCultureNeedsEmptyRadius() ) {
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_CULTURE_NEEDS_EMPTY_RADIUS" ) );
	}

	for( int iSpell = 0; iSpell < GC.getNumSpellInfos(); iSpell++ ) {
		CvSpellInfo& kSpell = GC.getSpellInfo( (SpellTypes) iSpell );
		if( kSpell.getVotePrereq() == eVote ) {
			if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
			if( kSpell.isAbility() ) {
				szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_ENABLES_ABILITY", kSpell.getDescription() ) );
			}
			else {
				szHelpText.append( gDLL->getText( "TXT_KEY_VOTE_HELP_ENABLES_SPELL", kSpell.getDescription() ) );
			}
		}
	}
	
	// Custom Help text
	if( !CvWString( kVote.getHelp()).empty() )
	{
		if( ! szHelpText.isEmpty() ) szHelpText.append( NEWLINE );
		szHelpText.append( kVote.getHelp() );
	}
}

// VOTE_HELP end

// BUG - Trade Denial - start
void CvGameTextMgr::setTechHelp(CvWStringBuffer &szBuffer, TechTypes eTech, bool bCivilopediaText, bool bPlayerContext, bool bStrategyText, bool bTreeInfo, TechTypes eFromTech)
{
	setTechTradeHelp(szBuffer, eTech, NO_PLAYER, bCivilopediaText, bPlayerContext, bStrategyText, bTreeInfo, eFromTech);
}

void CvGameTextMgr::setTechTradeHelp(CvWStringBuffer &szBuffer, TechTypes eTech, PlayerTypes eTradePlayer, bool bCivilopediaText, bool bPlayerContext, bool bStrategyText, bool bTreeInfo, TechTypes eFromTech)
// BUG - Trade Denial - end
{
	PROFILE_FUNC();

	CvWString szTempBuffer;
	CvWString szFirstBuffer;
	BuildingTypes eLoopBuilding;
	UnitTypes eLoopUnit;
	bool bFirst;
	int iI;

	// show debug info if cheat level > 0 and alt down
	bool bAlt = gDLL->altKey();
    if (bAlt && (gDLL->getChtLvl() > 0))
    {
		szBuffer.clear();

		for (int iI = 0; iI < MAX_PLAYERS; ++iI)
		{
			CvPlayerAI* playerI = &GET_PLAYER((PlayerTypes)iI);
			CvTeamAI* teamI = &GET_TEAM(playerI->getTeam());
			if (playerI->isAlive())
			{
				szTempBuffer.Format(L"%s: ", playerI->getName());
		        szBuffer.append(szTempBuffer);

				TechTypes ePlayerTech = playerI->getCurrentResearch();
				if (ePlayerTech == NO_TECH)
					szTempBuffer.Format(L"-\n");
				else
					szTempBuffer.Format(L"%s (%d->%dt)(%d/%d)\n", GC.getTechInfo(ePlayerTech).getDescription(), playerI->calculateResearchRate(ePlayerTech), playerI->getResearchTurnsLeft(ePlayerTech, true), teamI->getResearchProgress(ePlayerTech), teamI->getResearchCost(ePlayerTech));

		        szBuffer.append(szTempBuffer);
			}
		}

		return;
    }


	if (NO_TECH == eTech)
	{
		return;
	}

	//	Tech Name
	if (!bCivilopediaText && (!bTreeInfo || (NO_TECH == eFromTech)))
	{
		szTempBuffer.Format( SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_TECH_TEXT"), GC.getTechInfo(eTech).getDescription());
		szBuffer.append(szTempBuffer);
	}

	FAssert(GC.getGameINLINE().getActivePlayer() != NO_PLAYER || !bPlayerContext);

	if (bTreeInfo && (NO_TECH != eFromTech))
	{
		buildTechTreeString(szBuffer, eTech, bPlayerContext, eFromTech);
	}

	//	Obsolete Buildings
	for (iI = 0; iI < GC.getNumBuildingClassInfos(); ++iI)
	{
		if (!bPlayerContext || (GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getBuildingClassCount((BuildingClassTypes)iI) > 0))
		{
			if (GC.getGameINLINE().getActivePlayer() != NO_PLAYER)
			{
				eLoopBuilding = (BuildingTypes)GC.getCivilizationInfo(GC.getGameINLINE().getActiveCivilizationType()).getCivilizationBuildings(iI);
			}
			else
			{
				eLoopBuilding = (BuildingTypes)GC.getBuildingClassInfo((BuildingClassTypes)iI).getDefaultBuildingIndex();
			}

			if (eLoopBuilding != NO_BUILDING)
			{
				//	Obsolete Buildings Check...
				if (GC.getBuildingInfo(eLoopBuilding).getObsoleteTech() == eTech)
				{
					buildObsoleteString(szBuffer, eLoopBuilding, true);
				}
			}
		}
	}

	//	Obsolete Bonuses
	for (iI = 0; iI < GC.getNumBonusInfos(); ++iI)
	{
		if (GC.getBonusInfo((BonusTypes)iI).getTechObsolete() == eTech)
		{
			buildObsoleteBonusString(szBuffer, iI, true);
		}
	}

	//	Enable Bonuses
	for (iI = 0; iI < GC.getNumBonusInfos(); ++iI)
	{
		if (GC.getBonusInfo((BonusTypes)iI).getTechCityTrade() == eTech)
		{
			buildEnableBonusString(szBuffer, iI, true);
		}
	}

	for (iI = 0; iI < GC.getNumSpecialBuildingInfos(); ++iI)
	{
		if (GC.getSpecialBuildingInfo((SpecialBuildingTypes) iI).getObsoleteTech() == eTech)
		{
			buildObsoleteSpecialString(szBuffer, iI, true);
		}
	}

	//	Route movement change...
	buildMoveString(szBuffer, eTech, true, bPlayerContext);

	//	Creates a free unit...
	buildFreeUnitString(szBuffer, eTech, true, bPlayerContext);

	//	Increases feature production...
	buildFeatureProductionString(szBuffer, eTech, true, bPlayerContext);

	//	Increases worker build rate...
	buildWorkerRateString(szBuffer, eTech, true, bPlayerContext);

	//	Trade Routed per city change...
	buildTradeRouteString(szBuffer, eTech, true, bPlayerContext);

	//	Health increase...
	buildHealthRateString(szBuffer, eTech, true, bPlayerContext);

	//	Happiness increase...
	buildHappinessRateString(szBuffer, eTech, true, bPlayerContext);

	//	Free Techs...
	buildFreeTechString(szBuffer, eTech, true, bPlayerContext);

	//	Line of Sight Bonus across water...
	buildLOSString(szBuffer, eTech, true, bPlayerContext);

	//	Centers world map...
	buildMapCenterString(szBuffer, eTech, true, bPlayerContext);

	//	Reveals World Map...
	buildMapRevealString(szBuffer, eTech, true);

	//	Enables map trading...
	buildMapTradeString(szBuffer, eTech, true, bPlayerContext);

	//	Enables tech trading...
	buildTechTradeString(szBuffer, eTech, true, bPlayerContext);

	//	Enables gold trading...
	buildGoldTradeString(szBuffer, eTech, true, bPlayerContext);

	//	Enables open borders...
	buildOpenBordersString(szBuffer, eTech, true, bPlayerContext);

	//	Enables defensive pacts...
	buildDefensivePactString(szBuffer, eTech, true, bPlayerContext);

	//	Enables permanent alliances...
	buildPermanentAllianceString(szBuffer, eTech, true, bPlayerContext);
/************************************************************************************************/
/* Afforess	                  Start		 		                                                */
/* Advanced Diplomacy                                                                           */
/************************************************************************************************/
	//   Enables Embassies...
	buildEmbassyString(szBuffer, eTech, true, bPlayerContext);

	//   Enables Limited Borders...
	buildLimitedBordersString(szBuffer, eTech, true, bPlayerContext);

	//   Enables Free Trade...
	buildFreeTradeAgreementString(szBuffer, eTech, true, bPlayerContext);

	//   Enables Non Aggression Pact...
	buildNonAggressionString(szBuffer, eTech, true, bPlayerContext);

	//   Enables POW Exchange...
	buildPOWString(szBuffer, eTech, true, bPlayerContext);
/************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/************************************************************************************************/

	//	Enables bridge building...
	buildBridgeString(szBuffer, eTech, true, bPlayerContext);

	//	Can spread irrigation...
	buildIrrigationString(szBuffer, eTech, true, bPlayerContext);

	//	Ignore irrigation...
	buildIgnoreIrrigationString(szBuffer, eTech, true, bPlayerContext);

	//	Coastal work...
	buildWaterWorkString(szBuffer, eTech, true, bPlayerContext);

	//	Enables permanent alliances...
	buildVassalStateString(szBuffer, eTech, true, bPlayerContext);

	// MNAI - Puppet States
	//	Enables puppet states...
	buildPuppetStateString(szBuffer, eTech, true, bPlayerContext);
	// MNAI - End Puppet States

	//	Build farm, irrigation, etc...
	for (iI = 0; iI < GC.getNumBuildInfos(); ++iI)
	{
		buildImprovementString(szBuffer, eTech, iI, true, bPlayerContext);
	}

	//	Extra moves for certain domains...
	for (iI = 0; iI < NUM_DOMAIN_TYPES; ++iI)
	{
		buildDomainExtraMovesString(szBuffer, eTech, iI, true, bPlayerContext);
	}

	//	Adjusting culture, science, etc
	for (iI = 0; iI < NUM_COMMERCE_TYPES; ++iI)
	{
		buildAdjustString(szBuffer, eTech, iI, true, bPlayerContext);
	}

	//	Enabling trade routes on water...?
	for (iI = 0; iI < GC.getNumTerrainInfos(); ++iI)
	{
		buildTerrainTradeString(szBuffer, eTech, iI, true, bPlayerContext);
	}

	buildRiverTradeString(szBuffer, eTech, true, bPlayerContext);

	//	Special Buildings
	for (iI = 0; iI < GC.getNumSpecialBuildingInfos(); ++iI)
	{
		buildSpecialBuildingString(szBuffer, eTech, iI, true, bPlayerContext);
	}

	//	Build farm, mine, etc...
	for (iI = 0; iI < GC.getNumImprovementInfos(); ++iI)
	{
		buildYieldChangeString(szBuffer, eTech, iI, true, bPlayerContext);
	}

	bFirst = true;

	for (iI = 0; iI < GC.getNumBonusInfos(); ++iI)
	{
		bFirst = buildBonusRevealString(szBuffer, eTech, iI, bFirst, true, bPlayerContext);
	}

	bFirst = true;

	for (iI = 0; iI < GC.getNumCivicInfos(); ++iI)
	{
		bFirst = buildCivicRevealString(szBuffer, eTech, iI, bFirst, true, bPlayerContext);
	}

	if (!bCivilopediaText)
	{
		bFirst = true;

		for (iI = 0; iI < GC.getNumUnitClassInfos(); ++iI)
		{
			if (!bPlayerContext || !(GET_PLAYER(GC.getGameINLINE().getActivePlayer()).isProductionMaxedUnitClass((UnitClassTypes)iI)))
			{
				if (GC.getGameINLINE().getActivePlayer() != NO_PLAYER)
				{
					eLoopUnit = (UnitTypes)GC.getCivilizationInfo(GC.getGameINLINE().getActiveCivilizationType()).getCivilizationUnits(iI);
				}
				else
				{
					eLoopUnit = (UnitTypes)GC.getUnitClassInfo((UnitClassTypes)iI).getDefaultUnitIndex();
				}

				if (eLoopUnit != NO_UNIT)
				{
					if (!bPlayerContext || !(GET_PLAYER(GC.getGameINLINE().getActivePlayer()).canTrain(eLoopUnit)))
					{
						if (GC.getUnitInfo(eLoopUnit).getPrereqCiv() != NO_CIVILIZATION)
						{
							if (!bPlayerContext || (GC.getUnitInfo(eLoopUnit).getPrereqCiv() != GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getCivilizationType()))
							{
								continue;
							}
						}
						
						if (GC.getUnitInfo(eLoopUnit).getPrereqAndTech() == eTech)
						{
							szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_TECH_CAN_TRAIN").c_str());
							szTempBuffer.Format( SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_UNIT_TEXT"), GC.getUnitInfo(eLoopUnit).getDescription());
							setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", bFirst);
							bFirst = false;
						}
						else
						{
							for (int iJ = 0; iJ < GC.getNUM_UNIT_AND_TECH_PREREQS(); iJ++)
							{
								if (GC.getUnitInfo(eLoopUnit).getPrereqAndTechs(iJ) == eTech)
								{
									szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_TECH_CAN_TRAIN").c_str());
									szTempBuffer.Format( SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_UNIT_TEXT"), GC.getUnitInfo(eLoopUnit).getDescription());
									setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", bFirst);
									bFirst = false;
									break;
								}
							}
						}
					}
				}
			}
		}

		bFirst = true;

		for (iI = 0; iI < GC.getNumBuildingClassInfos(); ++iI)
		{
			if (!bPlayerContext || !(GET_PLAYER(GC.getGameINLINE().getActivePlayer()).isProductionMaxedBuildingClass((BuildingClassTypes)iI)))
			{
				if (GC.getGameINLINE().getActivePlayer() != NO_PLAYER)
				{
					eLoopBuilding = (BuildingTypes)GC.getCivilizationInfo(GC.getGameINLINE().getActiveCivilizationType()).getCivilizationBuildings(iI);
				}
				else
				{
					eLoopBuilding = (BuildingTypes)GC.getBuildingClassInfo((BuildingClassTypes)iI).getDefaultBuildingIndex();
				}

				if (eLoopBuilding != NO_BUILDING)
				{
					if (!bPlayerContext || !(GET_PLAYER(GC.getGameINLINE().getActivePlayer()).canConstruct(eLoopBuilding, false, true)))
					{
						if (GC.getBuildingInfo(eLoopBuilding).getPrereqAndTech() == eTech)
						{
							szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_TECH_CAN_CONSTRUCT").c_str());
							szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_BUILDING_TEXT"), GC.getBuildingInfo(eLoopBuilding).getDescription());
							setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", bFirst);
							bFirst = false;
						}
						else
						{
							for (int iJ = 0; iJ < GC.getNUM_BUILDING_AND_TECH_PREREQS(); iJ++)
							{
								if (GC.getBuildingInfo(eLoopBuilding).getPrereqAndTechs(iJ) == eTech)
								{
									szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_TECH_CAN_CONSTRUCT").c_str());
									szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_BUILDING_TEXT"), GC.getBuildingInfo(eLoopBuilding).getDescription());
									setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", bFirst);
									bFirst = false;
									break;
								}
							}
						}
					}
				}
			}
		}

		bFirst = true;

		for (iI = 0; iI < GC.getNumProjectInfos(); ++iI)
		{
			if (!bPlayerContext || !(GET_PLAYER(GC.getGameINLINE().getActivePlayer()).isProductionMaxedProject((ProjectTypes)iI)))
			{
				if (!bPlayerContext || !(GET_PLAYER(GC.getGameINLINE().getActivePlayer()).canCreate(((ProjectTypes)iI), false, true)))
				{
					if (GC.getProjectInfo((ProjectTypes)iI).getTechPrereq() == eTech)
					{

//FfH: Added by Kael 07/30/2009
//						szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_TECH_CAN_CREATE").c_str());
//						szTempBuffer.Format( SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_PROJECT_TEXT"), GC.getProjectInfo((ProjectTypes)iI).getDescription());
//						setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", bFirst);
//						bFirst = false;
                        if (!bPlayerContext ||
                          GC.getProjectInfo((ProjectTypes)iI).getPrereqCivilization() == NO_CIVILIZATION ||
                          GC.getProjectInfo((ProjectTypes)iI).getPrereqCivilization() == GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getCivilizationType())
                        {
                            szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_TECH_CAN_CREATE").c_str());
                            szTempBuffer.Format( SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_PROJECT_TEXT"), GC.getProjectInfo((ProjectTypes)iI).getDescription());
                            setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", bFirst);
                            bFirst = false;
                        }
//FfH: End Add

					}
				}
			}
		}
	}

	bFirst = true;
	for (iI = 0; iI < GC.getNumProcessInfos(); ++iI)
	{
		bFirst = buildProcessInfoString(szBuffer, eTech, iI, bFirst, true, bPlayerContext);
	}

	bFirst = true;
	for (iI = 0; iI < GC.getNumReligionInfos(); ++iI)
	{
		if (!bPlayerContext || !(GC.getGameINLINE().isReligionSlotTaken((ReligionTypes)iI)))
		{
			bFirst = buildFoundReligionString(szBuffer, eTech, iI, bFirst, true, bPlayerContext);
		}
	}

	bFirst = true;
	for (iI = 0; iI < GC.getNumCorporationInfos(); ++iI)
	{
		if (!bPlayerContext || !(GC.getGameINLINE().isCorporationFounded((CorporationTypes)iI)))
		{
			bFirst = buildFoundCorporationString(szBuffer, eTech, iI, bFirst, true, bPlayerContext);
		}
	}

	bFirst = true;
	for (iI = 0; iI < GC.getNumPromotionInfos(); ++iI)
	{
		bFirst = buildPromotionString(szBuffer, eTech, iI, bFirst, true, bPlayerContext);
	}

	if (bTreeInfo && NO_TECH == eFromTech)
	{
		buildSingleLineTechTreeString(szBuffer, eTech, bPlayerContext);
	}

	if (!CvWString(GC.getTechInfo(eTech).getHelp()).empty())
	{
		szBuffer.append(CvWString::format(L"%s%s", NEWLINE, GC.getTechInfo(eTech).getHelp()).c_str());
	}

	if (!bCivilopediaText)
	{
		if (GC.getGameINLINE().getActivePlayer() == NO_PLAYER)
		{
			szTempBuffer.Format(L"\n%d%c", GC.getTechInfo(eTech).getResearchCost(), GC.getCommerceInfo(COMMERCE_RESEARCH).getChar());
			szBuffer.append(szTempBuffer);
		}
		else if (GET_TEAM(GC.getGameINLINE().getActiveTeam()).isHasTech(eTech))
		{
			szTempBuffer.Format(L"\n%d%c", GET_TEAM(GC.getGameINLINE().getActiveTeam()).getResearchCost(eTech), GC.getCommerceInfo(COMMERCE_RESEARCH).getChar());
			szBuffer.append(szTempBuffer);
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_TECH_NUM_TURNS", GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getResearchTurnsLeft(eTech, (gDLL->ctrlKey() || !(gDLL->shiftKey())))));

			szTempBuffer.Format(L" (%d/%d %c)", GET_TEAM(GC.getGameINLINE().getActiveTeam()).getResearchProgress(eTech), GET_TEAM(GC.getGameINLINE().getActiveTeam()).getResearchCost(eTech), GC.getCommerceInfo(COMMERCE_RESEARCH).getChar());
			szBuffer.append(szTempBuffer);
		}
	}

	if (GC.getGameINLINE().getActivePlayer() != NO_PLAYER)
	{
		if (GET_PLAYER(GC.getGameINLINE().getActivePlayer()).canResearch(eTech))
		{
			for (iI = 0; iI < GC.getNumUnitInfos(); ++iI)
			{
				CvUnitInfo& kUnit = GC.getUnitInfo((UnitTypes)iI);

				if (kUnit.getBaseDiscover() > 0 || kUnit.getDiscoverMultiplier() > 0)
				{
					if (::getDiscoveryTech((UnitTypes)iI, GC.getGameINLINE().getActivePlayer()) == eTech)
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_TECH_GREAT_PERSON_DISCOVER", kUnit.getTextKeyWide()));
					}
				}
			}

			if (GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getCurrentEra() < GC.getTechInfo(eTech).getEra())
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_TECH_ERA_ADVANCE", GC.getEraInfo((EraTypes)GC.getTechInfo(eTech).getEra()).getTextKeyWide()));
			}
		}
	}

// BUG - Trade Denial - start
	if (eTradePlayer != NO_PLAYER && GC.getGameINLINE().getActivePlayer() != NO_PLAYER && getBugOptionBOOL("MiscHover__TechTradeDenial", true, "BUG_TECH_TRADE_DENIAL_HOVER"))
	{
		TradeData trade;
		trade.m_eItemType = TRADE_TECHNOLOGIES;
		trade.m_iData = eTech;

		if (GET_PLAYER(eTradePlayer).canTradeItem(GC.getGameINLINE().getActivePlayer(), trade, false))
		{
			DenialTypes eDenial = GET_PLAYER(eTradePlayer).getTradeDenial(GC.getGameINLINE().getActivePlayer(), trade);
			if (eDenial != NO_DENIAL)
			{
				szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_NEGATIVE_TEXT"), GC.getDenialInfo(eDenial).getDescription());
				szBuffer.append(NEWLINE);
				szBuffer.append(szTempBuffer);
			}
		}
	}
// BUG - Trade Denial - end
	
	
//FfH: Added by Kael 08/09/2007
    if (GC.getTechInfo(eTech).getPrereqReligion() != NO_RELIGION)
    {
        if (GC.getGameINLINE().getActivePlayer() == NO_PLAYER || GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getStateReligion() != GC.getTechInfo(eTech).getPrereqReligion())
        {
            szBuffer.append(CvWString::format(SETCOLR, TEXT_COLOR("COLOR_NEGATIVE_TEXT")));
            szBuffer.append(NEWLINE);
            szBuffer.append(gDLL->getText("TXT_KEY_TECH_PREREQ_RELIGION", GC.getReligionInfo((ReligionTypes)GC.getTechInfo(eTech).getPrereqReligion()).getDescription()));
            szBuffer.append(CvWString::format(ENDCOLR));
        }
    }
//FfH: End Add

	if (bStrategyText)
	{
		if (!CvWString(GC.getTechInfo(eTech).getStrategy()).empty())
		{
			if ((GC.getGameINLINE().getActivePlayer() == NO_PLAYER) || GET_PLAYER(GC.getGameINLINE().getActivePlayer()).isOption(PLAYEROPTION_ADVISOR_HELP))
			{
				szBuffer.append(SEPARATOR);
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_SIDS_TIPS"));
				szBuffer.append(L'\"');
				szBuffer.append(GC.getTechInfo(eTech).getStrategy());
				szBuffer.append(L'\"');
			}
		}
	}
}


void CvGameTextMgr::setBasicUnitHelp(CvWStringBuffer &szBuffer, UnitTypes eUnit, bool bCivilopediaText)
{
// BUG - Starting Experience - start
	setBasicUnitHelpWithCity(szBuffer, eUnit, bCivilopediaText);
}

void CvGameTextMgr::setBasicUnitHelpWithCity(CvWStringBuffer &szBuffer, UnitTypes eUnit, bool bCivilopediaText, CvCity* pCity, bool bConscript)
{
// BUG - Starting Experience - end
	PROFILE_FUNC();

	CvWString szTempBuffer;
	bool bFirst;
	int iCount;
	int iI;

	if (NO_UNIT == eUnit)
	{
		return;
	}

	CvUnitInfo& kUnitInfo = GC.getUnitInfo(eUnit);

	if (!bCivilopediaText)
	{
		szBuffer.append(NEWLINE);

		if (kUnitInfo.getDomainType() == DOMAIN_AIR)
		{
			if (kUnitInfo.getAirCombat() > 0)
			{
				szTempBuffer.Format(L"%d%c, ", kUnitInfo.getAirCombat(), gDLL->getSymbolID(STRENGTH_CHAR));
				szBuffer.append(szTempBuffer);
			}
		}
		else
		{
			if (kUnitInfo.getCombat() > 0)
			{
				if (kUnitInfo.getCombat() == kUnitInfo.getCombatDefense())
				{
					szTempBuffer.Format(L"%d%c, ", kUnitInfo.getCombat(), gDLL->getSymbolID(STRENGTH_CHAR));
					szBuffer.append(szTempBuffer);
				}
				else
				{
					szTempBuffer.Format(L"%d/%d%c, ", kUnitInfo.getCombat(), kUnitInfo.getCombatDefense(), gDLL->getSymbolID(STRENGTH_CHAR));
					szBuffer.append(szTempBuffer);
				}
			}
		}

		szTempBuffer.Format(L"%d%c", kUnitInfo.getMoves(), gDLL->getSymbolID(MOVES_CHAR));
		szBuffer.append(szTempBuffer);

		if (kUnitInfo.getAirRange() > 0)
		{
			szBuffer.append(L", ");
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_AIR_RANGE", kUnitInfo.getAirRange()));
		}
		
// BUG - Starting Experience - start
		if (pCity != NULL && getBugOptionBOOL("MiscHover__UnitExperience", true, "BUG_UNIT_EXPERIENCE_HOVER"))
		{
			setUnitExperienceHelp(szBuffer, L", ", eUnit, pCity, bConscript);
		}
// BUG - Starting Experience - end
	}

	// lfgr UI 11/2020: Show unit religion
	if( kUnitInfo.getReligionType() != NO_RELIGION )
	{
		szBuffer.append( NEWLINE );
		szBuffer.append( gDLL->getText( "TXT_KEY_UNIT_RELIGION", GC.getReligionInfo( (ReligionTypes) kUnitInfo.getReligionType() ).getDescription() ) );
	}

	if (kUnitInfo.isGoldenAge())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_GOLDEN_AGE"));
	}

	if (kUnitInfo.getLeaderExperience() > 0)
	{
		if (0 == GC.getDefineINT("WARLORD_EXTRA_EXPERIENCE_PER_UNIT_PERCENT"))
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_LEADER", kUnitInfo.getLeaderExperience()));
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_LEADER_EXPERIENCE", kUnitInfo.getLeaderExperience()));
		}
	}

	if (NO_PROMOTION != kUnitInfo.getLeaderPromotion())
	{
		szBuffer.append(CvWString::format(L"%s%c%s", NEWLINE, gDLL->getSymbolID(BULLET_CHAR), gDLL->getText("TXT_KEY_PROMOTION_WHEN_LEADING").GetCString()));
		parsePromotionHelp(szBuffer, (PromotionTypes)kUnitInfo.getLeaderPromotion(), L"\n   ");
	}

	if ((kUnitInfo.getBaseDiscover() > 0) || (kUnitInfo.getDiscoverMultiplier() > 0))
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_DISCOVER_TECH"));
	}

	if ((kUnitInfo.getBaseHurry() > 0) || (kUnitInfo.getHurryMultiplier() > 0))
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_HURRY_PRODUCTION"));
	}

	if ((kUnitInfo.getBaseTrade() > 0) || (kUnitInfo.getTradeMultiplier() > 0))
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_TRADE_MISSION"));
	}

	if (kUnitInfo.getGreatWorkCulture() > 0)
	{
		int iCulture = kUnitInfo.getGreatWorkCulture();
		if (NO_GAMESPEED != GC.getGameINLINE().getGameSpeedType())
		{
			iCulture *= GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getUnitGreatWorkPercent();
			iCulture /= 100;
		}

		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_GREAT_WORK", iCulture));
	}

	if (kUnitInfo.getEspionagePoints() > 0)
	{
		int iEspionage = kUnitInfo.getEspionagePoints();
		if (NO_GAMESPEED != GC.getGameINLINE().getGameSpeedType())
		{
			iEspionage *= GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getUnitGreatWorkPercent();
			iEspionage /= 100;
		}

		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_ESPIONAGE_MISSION", iEspionage));
	}

	bFirst = true;

	for (iI = 0; iI < GC.getNumReligionInfos(); ++iI)
	{
		if (kUnitInfo.getReligionSpreads(iI) > 0)
		{
			szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_UNIT_CAN_SPREAD").c_str());
			CvWString szReligion;
			szReligion.Format(L"<link=literal>%s</link>", GC.getReligionInfo((ReligionTypes) iI).getDescription());
			setListHelp(szBuffer, szTempBuffer, szReligion, L", ", bFirst);
			bFirst = false;
		}
	}

	bFirst = true;

	for (iI = 0; iI < GC.getNumCorporationInfos(); ++iI)
	{
		if (kUnitInfo.getCorporationSpreads(iI) > 0)
		{
			szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_UNIT_CAN_EXPAND").c_str());
			CvWString szCorporation;
			szCorporation.Format(L"<link=literal>%s</link>", GC.getCorporationInfo((CorporationTypes) iI).getDescription());
			setListHelp(szBuffer, szTempBuffer, szCorporation, L", ", bFirst);
			bFirst = false;
		}
	}

	bFirst = true;

	for (iI = 0; iI < GC.getNumSpecialistInfos(); ++iI)
	{
		if (kUnitInfo.getGreatPeoples(iI))
		{
			szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_UNIT_CAN_JOIN").c_str());
			CvWString szSpecialistLink = CvWString::format(L"<link=literal>%s</link>", GC.getSpecialistInfo((SpecialistTypes) iI).getDescription());
			setListHelp(szBuffer, szTempBuffer, szSpecialistLink.GetCString(), L", ", bFirst);
			bFirst = false;
		}
	}

	bFirst = true;

	for (iI = 0; iI < GC.getNumBuildingInfos(); ++iI)
	{
		if (kUnitInfo.getBuildings(iI) || kUnitInfo.getForceBuildings(iI))
		{
			szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_UNIT_CAN_CONSTRUCT").c_str());
			CvWString szBuildingLink = CvWString::format(L"<link=literal>%s</link>", GC.getBuildingInfo((BuildingTypes) iI).getDescription());
			setListHelp(szBuffer, szTempBuffer, szBuildingLink.GetCString(), L", ", bFirst);
			bFirst = false;
		}
	}

	if (kUnitInfo.getCargoSpace() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_CARGO_SPACE", kUnitInfo.getCargoSpace()));

		if (kUnitInfo.getSpecialCargo() != NO_SPECIALUNIT)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_CARRIES", GC.getSpecialUnitInfo((SpecialUnitTypes) kUnitInfo.getSpecialCargo()).getTextKeyWide()));
		}
	}

	szTempBuffer.Format(L"%s%s ", NEWLINE, gDLL->getText("TXT_KEY_UNIT_CANNOT_ENTER").GetCString());

	bFirst = true;

	for (iI = 0; iI < GC.getNumTerrainInfos(); ++iI)
	{
		if (kUnitInfo.getTerrainImpassable(iI))
		{
			CvWString szTerrain;
			TechTypes eTech = (TechTypes)kUnitInfo.getTerrainPassableTech(iI);
			if (NO_TECH == eTech)
			{
				szTerrain.Format(L"<link=literal>%s</link>", GC.getTerrainInfo((TerrainTypes)iI).getDescription());
			}
			else
			{
				szTerrain = gDLL->getText("TXT_KEY_TERRAIN_UNTIL_TECH", GC.getTerrainInfo((TerrainTypes)iI).getTextKeyWide(), GC.getTechInfo(eTech).getTextKeyWide());
			}
			setListHelp(szBuffer, szTempBuffer, szTerrain, L", ", bFirst);
			bFirst = false;
		}
	}

	for (iI = 0; iI < GC.getNumFeatureInfos(); ++iI)
	{
		if (kUnitInfo.getFeatureImpassable(iI))
		{
			CvWString szFeature;
			TechTypes eTech = (TechTypes)kUnitInfo.getFeaturePassableTech(iI); // lfgr bugfix 06/2019: "Feature" instead of "Terrain"
			if (NO_TECH == eTech)
			{
				szFeature.Format(L"<link=literal>%s</link>", GC.getFeatureInfo((FeatureTypes)iI).getDescription());
			}
			else
			{
				szFeature = gDLL->getText("TXT_KEY_TERRAIN_UNTIL_TECH", GC.getFeatureInfo((FeatureTypes)iI).getTextKeyWide(), GC.getTechInfo(eTech).getTextKeyWide());
			}
			setListHelp(szBuffer, szTempBuffer, szFeature, L", ", bFirst);
			bFirst = false;
		}
	}

	if (kUnitInfo.isInvisible())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_INVISIBLE_ALL"));
	}
	else if (kUnitInfo.getInvisibleType() != NO_INVISIBLE)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_INVISIBLE_MOST"));
	}

	for (iI = 0; iI < kUnitInfo.getNumSeeInvisibleTypes(); ++iI)
	{
		if (bCivilopediaText || (kUnitInfo.getSeeInvisibleType(iI) != kUnitInfo.getInvisibleType()))
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_SEE_INVISIBLE", GC.getInvisibleInfo((InvisibleTypes) kUnitInfo.getSeeInvisibleType(iI)).getTextKeyWide()));
		}
	}
/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**																								**/
/*************************************************************************************************/

//BUGFfH: Added by Denev 2009/09/08
	if (kUnitInfo.isInvestigate())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_INVESTIGATE_CITY"));
	}
//BUGFfH: End Add
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/
	if (kUnitInfo.isCanMoveImpassable())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_CAN_MOVE_IMPASSABLE"));
	}

	if (kUnitInfo.isCanMoveLimitedBorders())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_CAN_MOVE_LIMITED_BORDERS"));
	}

	if (kUnitInfo.isNoBadGoodies())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_NO_BAD_GOODIES"));
	}

	if (kUnitInfo.isHiddenNationality())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_HIDDEN_NATIONALITY"));
	}

	if (kUnitInfo.isAlwaysHostile())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_ALWAYS_HOSTILE"));
	}
	
/************************************************************************************************/
/* Afforess	                  Start		 07/29/10                                               */
/* Advanced Diplomacy                                                                           */
/************************************************************************************************/
	if (GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS) || bCivilopediaText)
	{
		if (kUnitInfo.isMilitaryTrade() || kUnitInfo.isWorkerTrade())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_TRADABLE_UNIT"));
		}
	}
/************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/************************************************************************************************/

	if (kUnitInfo.isOnlyDefensive())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_ONLY_DEFENSIVE"));
	}

	if (kUnitInfo.isNoCapture())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_CANNOT_CAPTURE"));
	}
/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**																								**/
/*************************************************************************************************/

//BUGFfH: Added by Denev 2009/09/08
	if (!kUnitInfo.isPillage())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_CANNOT_PILLAGE"));
	}

	if (!kUnitInfo.isMilitaryHappiness())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_CANNOT_PROTECT_CITY"));
	}
//BUGFfH: End Add
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/
	if (kUnitInfo.isRivalTerritory())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_EXPLORE_RIVAL"));
	}

	if (kUnitInfo.isFound())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_FOUND_CITY"));
	}

	iCount = 0;

	for (iI = 0; iI < GC.getNumBuildInfos(); ++iI)
	{
		if (kUnitInfo.getBuilds(iI))
		{
			iCount++;
		}
	}

	if (iCount > ((GC.getNumBuildInfos() * 3) / 4))
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_IMPROVE_PLOTS"));
	}
	else
	{
		bFirst = true;

		for (iI = 0; iI < GC.getNumBuildInfos(); ++iI)
		{
			if (kUnitInfo.getBuilds(iI))
			{
				szTempBuffer.Format(L"%s%s ", NEWLINE, gDLL->getText("TXT_KEY_UNIT_CAN").c_str());
				setListHelp(szBuffer, szTempBuffer, GC.getBuildInfo((BuildTypes) iI).getDescription(), L", ", bFirst);
				bFirst = false;
			}
		}
	}

	if (kUnitInfo.getNukeRange() != -1)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_CAN_NUKE"));
	}

	if (kUnitInfo.isCounterSpy())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_EXPOSE_SPIES"));
	}

	if ((kUnitInfo.getFirstStrikes() + kUnitInfo.getChanceFirstStrikes()) > 0)
	{
		if (kUnitInfo.getChanceFirstStrikes() == 0)
		{
			if (kUnitInfo.getFirstStrikes() == 1)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_UNIT_ONE_FIRST_STRIKE"));
			}
			else
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_UNIT_NUM_FIRST_STRIKES", kUnitInfo.getFirstStrikes()));
			}
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_FIRST_STRIKE_CHANCES", kUnitInfo.getFirstStrikes(), kUnitInfo.getFirstStrikes() + kUnitInfo.getChanceFirstStrikes()));
		}
	}

	if (kUnitInfo.isFirstStrikeImmune())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_IMMUNE_FIRST_STRIKES"));
	}

//FfH: Added by Kael 10/22/2008
    if (kUnitInfo.getDefensiveStrikeChance() > 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_DEFENSIVE_STRIKE_PEDIA", kUnitInfo.getDefensiveStrikeChance(), kUnitInfo.getDefensiveStrikeDamage()));
    }
    if (kUnitInfo.isImmuneToDefensiveStrike())
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_IMMUNE_TO_DEFENSIVE_STRIKE_PEDIA"));
    }
//FfH: End Add

	if (kUnitInfo.isNoDefensiveBonus())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_NO_DEFENSE_BONUSES"));
	}

	if (kUnitInfo.isFlatMovementCost())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_FLAT_MOVEMENT"));
	}

	if (kUnitInfo.isIgnoreTerrainCost())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_IGNORE_TERRAIN"));
	}

	if (kUnitInfo.getInterceptionProbability() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_INTERCEPT_AIRCRAFT", kUnitInfo.getInterceptionProbability()));
	}

	if (kUnitInfo.getEvasionProbability() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_EVADE_INTERCEPTION", kUnitInfo.getEvasionProbability()));
	}

	if (kUnitInfo.getWithdrawalProbability() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_WITHDRAWL_PROBABILITY", kUnitInfo.getWithdrawalProbability()));
	}

	if (kUnitInfo.getCombatLimit() < GC.getMAX_HIT_POINTS() && kUnitInfo.getCombat() > 0 && !kUnitInfo.isOnlyDefensive())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_COMBAT_LIMIT", (100 * kUnitInfo.getCombatLimit()) / GC.getMAX_HIT_POINTS()));
	}

	if (kUnitInfo.getCollateralDamage() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_COLLATERAL_DAMAGE", ( 100 * kUnitInfo.getCollateralDamageLimit() / GC.getMAX_HIT_POINTS())));
	}

	for (iI = 0; iI < GC.getNumUnitCombatInfos(); ++iI)
	{
		if (kUnitInfo.getUnitCombatCollateralImmune(iI))
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_COLLATERAL_IMMUNE", GC.getUnitCombatInfo((UnitCombatTypes)iI).getTextKeyWide()));
		}
	}

	if (kUnitInfo.getCityAttackModifier() == kUnitInfo.getCityDefenseModifier())
	{
		if (kUnitInfo.getCityAttackModifier() != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_CITY_STRENGTH_MOD", kUnitInfo.getCityAttackModifier()));
		}
	}
	else
	{
		if (kUnitInfo.getCityAttackModifier() != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_CITY_ATTACK_MOD", kUnitInfo.getCityAttackModifier()));
		}

		if (kUnitInfo.getCityDefenseModifier() != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_CITY_DEFENSE_MOD", kUnitInfo.getCityDefenseModifier()));
		}
	}

	if (kUnitInfo.getAnimalCombatModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_ANIMAL_COMBAT_MOD", kUnitInfo.getAnimalCombatModifier()));
	}

	if (kUnitInfo.getDropRange() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_PARADROP_RANGE", kUnitInfo.getDropRange()));
	}

	if (kUnitInfo.getHillsDefenseModifier() == kUnitInfo.getHillsAttackModifier())
	{
		if (kUnitInfo.getHillsAttackModifier() != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_HILLS_STRENGTH", kUnitInfo.getHillsAttackModifier()));
		}
	}
	else
	{
		if (kUnitInfo.getHillsAttackModifier() != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_HILLS_ATTACK", kUnitInfo.getHillsAttackModifier()));
		}

		if (kUnitInfo.getHillsDefenseModifier() != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_HILLS_DEFENSE", kUnitInfo.getHillsDefenseModifier()));
		}
	}

	for (iI = 0; iI < GC.getNumTerrainInfos(); ++iI)
	{
/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**																								**/
/*************************************************************************************************/

//BUGFfH: Added by Denev 2009/09/05
		if (kUnitInfo.getTerrainAttackModifier(iI) == kUnitInfo.getTerrainDefenseModifier(iI))
		{
			if (kUnitInfo.getTerrainAttackModifier(iI) != 0)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_UNIT_STRENGTH", kUnitInfo.getTerrainAttackModifier(iI), GC.getTerrainInfo((TerrainTypes) iI).getTextKeyWide()));
			}
		}
		else
		{
//BUGFfH: End Add

		if (kUnitInfo.getTerrainDefenseModifier(iI) != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_DEFENSE", kUnitInfo.getTerrainDefenseModifier(iI), GC.getTerrainInfo((TerrainTypes) iI).getTextKeyWide()));
		}

		if (kUnitInfo.getTerrainAttackModifier(iI) != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_ATTACK", kUnitInfo.getTerrainAttackModifier(iI), GC.getTerrainInfo((TerrainTypes) iI).getTextKeyWide()));
		}
//BUGFfH: Added by Denev 2009/09/05
		}
//BUGFfH: End Add
	}
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/

	for (iI = 0; iI < GC.getNumFeatureInfos(); ++iI)
	{
/*************************************************************************************************/
/**	FFHBUG denev																				**/
/**	ADDON (FFHBUG) merged Sephi																	**/
/**																								**/
/*************************************************************************************************/

//BUGFfH: Added by Denev 2009/09/05
		if (kUnitInfo.getFeatureAttackModifier(iI) == kUnitInfo.getFeatureDefenseModifier(iI))
		{
			if (kUnitInfo.getFeatureAttackModifier(iI) != 0)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_UNIT_STRENGTH", kUnitInfo.getFeatureAttackModifier(iI), GC.getFeatureInfo((FeatureTypes) iI).getTextKeyWide()));
			}
		}
		else
		{
//BUGFfH: End Add
		if (kUnitInfo.getFeatureDefenseModifier(iI) != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_DEFENSE", kUnitInfo.getFeatureDefenseModifier(iI), GC.getFeatureInfo((FeatureTypes) iI).getTextKeyWide()));
		}

		if (kUnitInfo.getFeatureAttackModifier(iI) != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_ATTACK", kUnitInfo.getFeatureAttackModifier(iI), GC.getFeatureInfo((FeatureTypes) iI).getTextKeyWide()));
		}
//BUGFfH: Added by Denev 2009/09/05
		}
//BUGFfH: End Add
	}
/*************************************************************************************************/
/**	END																							**/
/*************************************************************************************************/

	for (iI = 0; iI < GC.getNumUnitClassInfos(); ++iI)
	{
		if (kUnitInfo.getUnitClassAttackModifier(iI) == kUnitInfo.getUnitClassDefenseModifier(iI))
		{
			if (kUnitInfo.getUnitClassAttackModifier(iI) != 0)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_UNIT_MOD_VS_TYPE", kUnitInfo.getUnitClassAttackModifier(iI), GC.getUnitClassInfo((UnitClassTypes)iI).getTextKeyWide()));
			}
		}
		else
		{
			if (kUnitInfo.getUnitClassAttackModifier(iI) != 0)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_UNIT_ATTACK_MOD_VS_CLASS", kUnitInfo.getUnitClassAttackModifier(iI), GC.getUnitClassInfo((UnitClassTypes)iI).getTextKeyWide()));
			}

			if (kUnitInfo.getUnitClassDefenseModifier(iI) != 0)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_UNIT_DEFENSE_MOD_VS_CLASS", kUnitInfo.getUnitClassDefenseModifier(iI), GC.getUnitClassInfo((UnitClassTypes) iI).getTextKeyWide()));
			}
		}
	}

	for (iI = 0; iI < GC.getNumUnitCombatInfos(); ++iI)
	{
		if (kUnitInfo.getUnitCombatModifier(iI) != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_MOD_VS_TYPE", kUnitInfo.getUnitCombatModifier(iI), GC.getUnitCombatInfo((UnitCombatTypes) iI).getTextKeyWide()));
		}
	}

	for (iI = 0; iI < NUM_DOMAIN_TYPES; ++iI)
	{
		if (kUnitInfo.getDomainModifier(iI) != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_MOD_VS_TYPE_NO_LINK", kUnitInfo.getDomainModifier(iI), GC.getDomainInfo((DomainTypes)iI).getTextKeyWide()));
		}
	}

	szTempBuffer.clear();
	bFirst = true;
	for (iI = 0; iI < GC.getNumUnitClassInfos(); ++iI)
	{
		if (kUnitInfo.getTargetUnitClass(iI))
		{
			if (bFirst)
			{
				bFirst = false;
			}
			else
			{
				szTempBuffer += L", ";
			}

			szTempBuffer += CvWString::format(L"<link=literal>%s</link>", GC.getUnitClassInfo((UnitClassTypes)iI).getDescription());
		}
	}

	if (!bFirst)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_TARGETS_UNIT_FIRST", szTempBuffer.GetCString()));
	}

	szTempBuffer.clear();
	bFirst = true;
	for (iI = 0; iI < GC.getNumUnitClassInfos(); ++iI)
	{
		if (kUnitInfo.getDefenderUnitClass(iI))
		{
			if (bFirst)
			{
				bFirst = false;
			}
			else
			{
				szTempBuffer += L", ";
			}

			szTempBuffer += CvWString::format(L"<link=literal>%s</link>", GC.getUnitClassInfo((UnitClassTypes)iI).getDescription());
		}
	}

	if (!bFirst)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_DEFENDS_UNIT_FIRST", szTempBuffer.GetCString()));
	}

	szTempBuffer.clear();
	bFirst = true;
	for (iI = 0; iI < GC.getNumUnitCombatInfos(); ++iI)
	{
		if (kUnitInfo.getTargetUnitCombat(iI))
		{
			if (bFirst)
			{
				bFirst = false;
			}
			else
			{
				szTempBuffer += L", ";
			}

			szTempBuffer += CvWString::format(L"<link=literal>%s</link>", GC.getUnitCombatInfo((UnitCombatTypes)iI).getDescription());
		}
	}

	if (!bFirst)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_TARGETS_UNIT_FIRST", szTempBuffer.GetCString()));
	}

	szTempBuffer.clear();
	bFirst = true;
	for (iI = 0; iI < GC.getNumUnitCombatInfos(); ++iI)
	{
		if (kUnitInfo.getDefenderUnitCombat(iI))
		{
			if (bFirst)
			{
				bFirst = false;
			}
			else
			{
				szTempBuffer += L", ";
			}

			szTempBuffer += CvWString::format(L"<link=literal>%s</link>", GC.getUnitCombatInfo((UnitCombatTypes)iI).getDescription());
		}
	}

	if (!bFirst)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_DEFENDS_UNIT_FIRST", szTempBuffer.GetCString()));
	}

	szTempBuffer.clear();
	bFirst = true;
	for (iI = 0; iI < GC.getNumUnitClassInfos(); ++iI)
	{
		if (kUnitInfo.getFlankingStrikeUnitClass(iI) > 0)
		{
			if (bFirst)
			{
				bFirst = false;
			}
			else
			{
				szTempBuffer += L", ";
			}

			szTempBuffer += CvWString::format(L"<link=literal>%s</link>", GC.getUnitClassInfo((UnitClassTypes)iI).getDescription());
		}
	}

	if (!bFirst)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_FLANKING_STRIKES", szTempBuffer.GetCString()));
	}

	if (kUnitInfo.getBombRate() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_BOMB_RATE", ((kUnitInfo.getBombRate() * 100) / GC.getMAX_CITY_DEFENSE_DAMAGE())));
	}

	if (kUnitInfo.getBombardRate() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_BOMBARD_RATE", ((kUnitInfo.getBombardRate() * 100) / GC.getMAX_CITY_DEFENSE_DAMAGE())));
	}

	bFirst = true;

	for (iI = 0; iI < GC.getNumPromotionInfos(); ++iI)
	{
		if (kUnitInfo.getFreePromotions(iI))
		{
			szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_UNIT_STARTS_WITH").c_str());
			setListHelp(szBuffer, szTempBuffer, CvWString::format(L"<link=literal>%s</link>", GC.getPromotionInfo((PromotionTypes) iI).getDescription()), L", ", bFirst);
			bFirst = false;
		}
	}
		
// BUG - Starting Experience - start
	if (pCity != NULL && getBugOptionBOOL("MiscHover__UnitExperienceModifiers", true, "BUG_UNIT_EXPERIENCE_MODIFIERS_HOVER"))
	{
		CvUnitInfo& kUnit = kUnitInfo;
		CvPlayer& kPlayer = GET_PLAYER(pCity->getOwnerINLINE());
		CvCivilizationInfo& kCivilization = GC.getCivilizationInfo(kPlayer.getCivilizationType());

		UnitClassTypes eUnitClass = (UnitClassTypes)kUnit.getUnitClassType();
		UnitCombatTypes eCombatType = (UnitCombatTypes)kUnit.getUnitCombatType();
		DomainTypes eDomainType = (DomainTypes)kUnit.getDomainType();

		if ((UnitTypes)kCivilization.getCivilizationUnits(eUnitClass) == eUnit && kUnit.canAcquireExperience())
		{
			int iExperience;

			iExperience = pCity->getFreeExperience();
			if (iExperience != 0)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_CITY_FREE_EXPERIENCE", iExperience));
			}
			iExperience = pCity->getUnitCombatFreeExperience(eCombatType);
			if (iExperience != 0)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_CITY_UNITCOMBAT_FREE_EXPERIENCE", iExperience, GC.getUnitCombatInfo((UnitCombatTypes)eCombatType).getTextKeyWide()));
			}
			iExperience = kPlayer.getFreeExperience();
			if (iExperience != 0)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_PLAYER_FREE_EXPERIENCE", iExperience));
			}
			iExperience = pCity->getSpecialistFreeExperience();
			if (iExperience != 0)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_SPECIALIST_FREE_EXPERIENCE", iExperience));
			}

			for (int iI = 0; iI < GC.getNumBuildingClassInfos(); iI++)
			{
				BuildingTypes eLoopBuilding = (BuildingTypes)kCivilization.getCivilizationBuildings((BuildingClassTypes)iI);
				if (eLoopBuilding == NO_BUILDING)
				{
					continue;
				}
				CvBuildingInfo& kBuilding = GC.getBuildingInfo(eLoopBuilding);

				if (iExperience != 0)
				{
					if (pCity->getNumBuilding(eLoopBuilding) > 0)
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_FREE_EXPERIENCE", iExperience, kBuilding.getTextKeyWide()));
					}
					else if (pCity->canConstruct(eLoopBuilding, false, true))
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_NO_BUILDING_FREE_EXPERIENCE", iExperience, kBuilding.getTextKeyWide()));
					}
				}
			}

			if (kPlayer.getStateReligion() != NO_RELIGION)
			{
				iExperience = kPlayer.getStateReligionFreeExperience();
				if (iExperience != 0)
				{
					if (pCity->isHasReligion(kPlayer.getStateReligion()))
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_STATE_RELIGION_FREE_EXPERIENCE", iExperience));
					}
					else
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_NO_STATE_RELIGION_FREE_EXPERIENCE", iExperience));
					}
				}
			}
		}
	}
// BUG - Starting Experience - end

	if (kUnitInfo.getExtraCost() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_EXTRA_COST", kUnitInfo.getExtraCost()));
	}

	if (bCivilopediaText)
	{
		// Trait
		for (int i = 0; i < GC.getNumTraitInfos(); ++i)
		{
			if (kUnitInfo.getProductionTraits((TraitTypes)i) != 0)
			{
				if (kUnitInfo.getProductionTraits((TraitTypes)i) == 100)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_DOUBLE_SPEED_TRAIT", GC.getTraitInfo((TraitTypes)i).getTextKeyWide()));
				}
				else
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_PRODUCTION_MODIFIER_TRAIT", kUnitInfo.getProductionTraits((TraitTypes)i), GC.getTraitInfo((TraitTypes)i).getTextKeyWide()));
				}
			}
		}
	}
	
	// MiscastPromotions 10/2019 lfgr
    if (kUnitInfo.getMiscastChance() != 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_SPELL_MISCAST_CHANCE_MODIFY", kUnitInfo.getMiscastChance()));
    }
	// MiscastPromotions end

//FfH: Added by Kael 08/04/2007
	for (iI = 0; iI < GC.getNumDamageTypeInfos(); iI++)
	{
        if (kUnitInfo.getDamageTypeCombat((DamageTypes)iI) != 0)
		{
            szBuffer.append(NEWLINE);
            szBuffer.append(gDLL->getText("TXT_KEY_DAMAGE_TYPE_COMBAT", kUnitInfo.getDamageTypeCombat((DamageTypes)iI), GC.getDamageTypeInfo((DamageTypes)iI).getDescription()));
		}
	}
	for (iI = 0; iI < GC.getNumBonusInfos(); iI++)
	{
        if (kUnitInfo.getBonusAffinity((BonusTypes)iI) != 0)
		{
            szBuffer.append(NEWLINE);
            szBuffer.append(gDLL->getText("TXT_KEY_BONUS_AFFINITY", kUnitInfo.getBonusAffinity((BonusTypes)iI), GC.getBonusInfo((BonusTypes)iI).getDescription()));
		}
	}
    if (kUnitInfo.getMinLevel() > 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_UNIT_CANT_BUILD"));
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_UNIT_MIN_LEVEL", kUnitInfo.getMinLevel()));
    }
    if (kUnitInfo.isDisableUpgradeTo())
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_UNIT_DISABLE_UPGRADE_TO"));
    }
    if (kUnitInfo.getFreePromotionPick() > 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_UNIT_FREE_PROMOTION_PICK", kUnitInfo.getFreePromotionPick()));
    }
    if (kUnitInfo.getGoldFromCombat() != 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_UNIT_GOLD_FROM_COMBAT", kUnitInfo.getGoldFromCombat()));
    }
    if (kUnitInfo.getModifyGlobalCounter() != 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_MESSAGE_MODIFY_GLOBAL_COUNTER", kUnitInfo.getModifyGlobalCounter()));
    }
    if (kUnitInfo.getUnitConvertFromCombat() != NO_UNIT)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_UNIT_CONVERT_FROM_COMBAT", kUnitInfo.getUnitConvertFromCombatChance(), GC.getUnitInfo((UnitTypes)kUnitInfo.getUnitConvertFromCombat()).getDescription()));
    }
    if (kUnitInfo.getUnitCreateFromCombat() != NO_UNIT)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_UNIT_CREATE_FROM_COMBAT", kUnitInfo.getUnitCreateFromCombatChance(), GC.getUnitInfo((UnitTypes)kUnitInfo.getUnitCreateFromCombat()).getDescription()));
    }
    if (kUnitInfo.getEnslavementChance() != 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_UNIT_ENSLAVEMENT_CHANCE", kUnitInfo.getEnslavementChance()));
    }
    if (kUnitInfo.getPromotionFromCombat() != NO_PROMOTION)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_UNIT_PROMOTION_FROM_COMBAT", GC.getPromotionInfo((PromotionTypes)kUnitInfo.getPromotionFromCombat()).getDescription()));
    }
	if (kUnitInfo.getWeaponTier() > 0)
	{
        szBuffer.append(NEWLINE);
        if (kUnitInfo.getWeaponTier() == 1)
        {
            szBuffer.append(gDLL->getText("TXT_KEY_UNIT_WEAPON_TIER_1"));
        }
        if (kUnitInfo.getWeaponTier() == 2)
        {
            szBuffer.append(gDLL->getText("TXT_KEY_UNIT_WEAPON_TIER_2"));
        }
        if (kUnitInfo.getWeaponTier() == 3)
        {
            szBuffer.append(gDLL->getText("TXT_KEY_UNIT_WEAPON_TIER_3"));
        }
	}
    if (kUnitInfo.isImmortal())
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_PROMOTION_IMMORTAL_PEDIA"));
    }
    if (kUnitInfo.isNoWarWeariness())
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_UNIT_NO_WAR_WEARINESS"));
    }
    if (kUnitInfo.getDiploVoteType() != NO_VOTESOURCE)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_UNIT_DIPLO_VOTE_TYPE", GC.getVoteSourceInfo((VoteSourceTypes)kUnitInfo.getDiploVoteType()).getDescription()));
    }
    if (kUnitInfo.isAbandon())
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_UNIT_ABANDON"));
    }
    for (int iJ=0;iJ<GC.getNumSpellInfos();iJ++)
    {
        if (GC.getSpellInfo((SpellTypes)iJ).getCivilizationPrereq() == NO_CIVILIZATION)
        {
            if (GC.getSpellInfo((SpellTypes)iJ).getReligionPrereq() == NO_RELIGION)
            {
                if (GC.getSpellInfo((SpellTypes)iJ).getUnitPrereq() == eUnit)
                {
                    szBuffer.append(NEWLINE);
                    szBuffer.append(gDLL->getText("TXT_KEY_UNIT_SPELL_ABILITY", GC.getSpellInfo((SpellTypes)iJ).getDescription()));
                }
                if (GC.getSpellInfo((SpellTypes)iJ).getUnitClassPrereq() == kUnitInfo.getUnitClassType())
                {
                    szBuffer.append(NEWLINE);
                    szBuffer.append(gDLL->getText("TXT_KEY_UNIT_SPELL_ABILITY", GC.getSpellInfo((SpellTypes)iJ).getDescription()));
                }
            }
        }
    }
//FfH: End Add

	if (!CvWString(kUnitInfo.getHelp()).empty())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(kUnitInfo.getHelp());
	}
}


// BUG - Starting Experience - start
/*
 * Appends the starting experience and number of promotions the given unit will have
 * when trained or conscripted in the given city.
 */
void CvGameTextMgr::setUnitExperienceHelp(CvWStringBuffer &szBuffer, CvWString szStart, UnitTypes eUnit, CvCity* pCity, bool bConscript)
{
	if (GC.getUnitInfo(eUnit).canAcquireExperience())
	{
		int iExperience = pCity->getProductionExperience(eUnit) >> (bConscript ? 1 : 0);
		if (iExperience > 0)
		{
			szBuffer.append(szStart);
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_EXPERIENCE", iExperience));

			int iLevel = calculateLevel(iExperience, pCity->getOwnerINLINE());
			if (iLevel > 1)
			{
				szBuffer.append(L", ");
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_PROMOTIONS", iLevel - 1));
			}
		}
	}
}
// BUG - Starting Experience - end


void CvGameTextMgr::setUnitHelp(CvWStringBuffer &szBuffer, UnitTypes eUnit, bool bCivilopediaText, bool bStrategyText, bool bTechChooserText, CvCity* pCity)
{
	PROFILE_FUNC();

	CvWString szTempBuffer;
	PlayerTypes ePlayer;
	bool bFirst;
	int iProduction;
	int iI;

	if (NO_UNIT == eUnit)
	{
		return;
	}
	
	CvUnitInfo& kUnitInfo = GC.getUnitInfo(eUnit);

	if (pCity != NULL)
	{
		ePlayer = pCity->getOwnerINLINE();
	}
	else
	{
		ePlayer = GC.getGameINLINE().getActivePlayer();
	}

	if (!bCivilopediaText)
	{
		szTempBuffer.Format(SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_UNIT_TEXT"), kUnitInfo.getDescription());
		szBuffer.append(szTempBuffer);

		if (kUnitInfo.getUnitCombatType() != NO_UNITCOMBAT)
		{
			szTempBuffer.Format(L" (%s)", GC.getUnitCombatInfo((UnitCombatTypes) kUnitInfo.getUnitCombatType()).getDescription());
			szBuffer.append(szTempBuffer);
		}
	}

	// test for unique unit
	UnitClassTypes eUnitClass = (UnitClassTypes)kUnitInfo.getUnitClassType();
	UnitTypes eDefaultUnit = (UnitTypes)GC.getUnitClassInfo(eUnitClass).getDefaultUnitIndex();

//FfH: Modified by Kael 01/31/2009
//	if (NO_UNIT != eDefaultUnit && eDefaultUnit != eUnit)
//	{
//		for (iI  = 0; iI < GC.getNumCivilizationInfos(); ++iI)
//		{
//			UnitTypes eUniqueUnit = (UnitTypes)GC.getCivilizationInfo((CivilizationTypes)iI).getCivilizationUnits((int)eUnitClass);
//			if (eUniqueUnit == eUnit)
//			{
//				szBuffer.append(NEWLINE);
//				szBuffer.append(gDLL->getText("TXT_KEY_UNIQUE_UNIT", GC.getCivilizationInfo((CivilizationTypes)iI).getTextKeyWide()));
//			}
//		}
//		szBuffer.append(NEWLINE);
//		szBuffer.append(gDLL->getText("TXT_KEY_REPLACES_UNIT", GC.getUnitInfo(eDefaultUnit).getTextKeyWide()));
    bool bUnique = false;
    int iCount = 0;
	for (iI  = 0; iI < GC.getNumCivilizationInfos(); ++iI)
	{
		UnitTypes eUniqueUnit = (UnitTypes)GC.getCivilizationInfo((CivilizationTypes)iI).getCivilizationUnits((int)eUnitClass);
		if (eUniqueUnit == NO_UNIT)
		{
		    iCount += 1;
		}
	}
    if (iCount > 19)
    {
        bUnique = true;
    }
	if (bUnique || (NO_UNIT != eDefaultUnit && eDefaultUnit != eUnit))
	{
		for (iI  = 0; iI < GC.getNumCivilizationInfos(); ++iI)
		{
			UnitTypes eUniqueUnit = (UnitTypes)GC.getCivilizationInfo((CivilizationTypes)iI).getCivilizationUnits((int)eUnitClass);
			if (eUniqueUnit == eUnit)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_UNIQUE_UNIT", GC.getCivilizationInfo((CivilizationTypes)iI).getTextKeyWide()));
			}
		}

        if (!bUnique)
        {
            szBuffer.append(NEWLINE);
            szBuffer.append(gDLL->getText("TXT_KEY_REPLACES_UNIT", GC.getUnitInfo(eDefaultUnit).getTextKeyWide()));
        }
//FfH: End Modify

	}

	if (isWorldUnitClass(eUnitClass))
	{
		if (pCity == NULL)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_WORLD_UNIT_ALLOWED", GC.getUnitClassInfo(eUnitClass).getMaxGlobalInstances()));
		}
		else
		{
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_WORLD_UNIT_LEFT", (GC.getUnitClassInfo(eUnitClass).getMaxGlobalInstances() - (ePlayer != NO_PLAYER ? GC.getGameINLINE().getUnitClassCreatedCount(eUnitClass) + GET_TEAM(GET_PLAYER(ePlayer).getTeam()).getUnitClassMaking(eUnitClass) : 0))));
		}
	}

	if (isTeamUnitClass(eUnitClass))
	{
		if (pCity == NULL)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_TEAM_UNIT_ALLOWED", GC.getUnitClassInfo(eUnitClass).getMaxTeamInstances()));
		}
		else
		{
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_TEAM_UNIT_LEFT", (GC.getUnitClassInfo(eUnitClass).getMaxTeamInstances() - (ePlayer != NO_PLAYER ? GET_TEAM(GET_PLAYER(ePlayer).getTeam()).getUnitClassCountPlusMaking(eUnitClass) : 0))));
		}
	}

	if (isNationalUnitClass(eUnitClass))
	{
		if (pCity == NULL)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_NATIONAL_UNIT_ALLOWED", GC.getUnitClassInfo(eUnitClass).getMaxPlayerInstances()));
		}
		else
		{
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_NATIONAL_UNIT_LEFT", (GC.getUnitClassInfo(eUnitClass).getMaxPlayerInstances() - (ePlayer != NO_PLAYER ? GET_PLAYER(ePlayer).getUnitClassCountPlusMaking(eUnitClass) : 0))));
		}
	}

	if (0 != GC.getUnitClassInfo(eUnitClass).getInstanceCostModifier())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_INSTANCE_COST_MOD", GC.getUnitClassInfo(eUnitClass).getInstanceCostModifier()));
	}

// BUG - Starting Experience - start
	setBasicUnitHelpWithCity(szBuffer, eUnit, bCivilopediaText, pCity);
// BUG - Starting Experience - end

	if ((pCity == NULL) || !(pCity->canTrain(eUnit)))
	{
		if (pCity != NULL)
		{
			if (GC.getGameINLINE().isNoNukes())
			{
				if (kUnitInfo.getNukeRange() != -1)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_UNIT_NO_NUKES"));
				}
			}
		}

		if (kUnitInfo.getHolyCity() != NO_RELIGION)
		{
			if ((pCity == NULL) || !(pCity->isHolyCity((ReligionTypes)(kUnitInfo.getHolyCity()))))
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_UNIT_REQUIRES_HOLY_CITY", GC.getReligionInfo((ReligionTypes)(kUnitInfo.getHolyCity())).getChar()));
			}
		}

		bFirst = true;

		if (kUnitInfo.getSpecialUnitType() != NO_SPECIALUNIT)
		{
			if ((pCity == NULL) || !(GC.getGameINLINE().isSpecialUnitValid((SpecialUnitTypes)(kUnitInfo.getSpecialUnitType()))))
			{
				for (iI = 0; iI < GC.getNumProjectInfos(); ++iI)
				{
					if (GC.getProjectInfo((ProjectTypes)iI).getEveryoneSpecialUnit() == kUnitInfo.getSpecialUnitType())
					{
						szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_REQUIRES").c_str());
						CvWString szProject;
						szProject.Format(L"<link=literal>%s</link>", GC.getProjectInfo((ProjectTypes)iI).getDescription());
						setListHelp(szBuffer, szTempBuffer, szProject, gDLL->getText("TXT_KEY_OR").c_str(), bFirst);
						bFirst = false;
					}
				}
			}
		}

		if (!bFirst)
		{
			szBuffer.append(ENDCOLR);
		}

		bFirst = true;

		if (kUnitInfo.getNukeRange() != -1)
		{
			if (NULL == pCity || !GC.getGameINLINE().isNukesValid())
			{
				for (iI = 0; iI < GC.getNumProjectInfos(); ++iI)
				{
					if (GC.getProjectInfo((ProjectTypes)iI).isAllowsNukes())
					{
						szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_REQUIRES").c_str());
						CvWString szProject;
						szProject.Format(L"<link=literal>%s</link>", GC.getProjectInfo((ProjectTypes)iI).getDescription());
						setListHelp(szBuffer, szTempBuffer, szProject, gDLL->getText("TXT_KEY_OR").c_str(), bFirst);
						bFirst = false;
					}
				}

				for (iI = 0; iI < GC.getNumBuildingInfos(); ++iI)
				{
					if (GC.getBuildingInfo((BuildingTypes)iI).isAllowsNukes())
					{
						szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_REQUIRES").c_str());
						CvWString szBuilding;
						szBuilding.Format(L"<link=literal>%s</link>", GC.getBuildingInfo((BuildingTypes)iI).getDescription());
						setListHelp(szBuffer, szTempBuffer, szBuilding, gDLL->getText("TXT_KEY_OR").c_str(), bFirst);
						bFirst = false;
					}
				}
			}
		}

		if (!bFirst)
		{
			szBuffer.append(ENDCOLR);
		}

		if (!bCivilopediaText)
		{
			if (kUnitInfo.getPrereqBuilding() != NO_BUILDING)
			{
				if ((pCity == NULL) || (pCity->getNumBuilding((BuildingTypes)(kUnitInfo.getPrereqBuilding())) <= 0))
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_UNIT_REQUIRES_STRING", GC.getBuildingInfo((BuildingTypes)(kUnitInfo.getPrereqBuilding())).getTextKeyWide()));
				}
			}

//FfH: Added by Kael 08/04/2007
			if (kUnitInfo.getPrereqBuildingClass() != NO_BUILDINGCLASS)
			{
				if ((pCity == NULL) || (!pCity->isHasBuildingClass(kUnitInfo.getPrereqBuildingClass())))
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_UNIT_REQUIRES_STRING", GC.getBuildingClassInfo((BuildingClassTypes)(kUnitInfo.getPrereqBuildingClass())).getTextKeyWide()));
				}
			}
            if (kUnitInfo.getPrereqAlignment() != NO_ALIGNMENT)
            {
                if (GC.getGameINLINE().getActivePlayer() == NO_PLAYER || GET_PLAYER(ePlayer).getAlignment() !=  kUnitInfo.getPrereqAlignment())
                {
                    szBuffer.append(NEWLINE);
                    szBuffer.append(gDLL->getText("TXT_KEY_UNIT_PREREQ_ALIGNMENT", GC.getAlignmentInfo((AlignmentTypes)kUnitInfo.getPrereqAlignment()).getDescription()));
                }
            }
            if (kUnitInfo.getPrereqCivic() != NO_CIVIC)
            {
                bool bValid = false;
                if (GC.getGameINLINE().getActivePlayer() != NO_PLAYER)
                {
                    for (iI = 0; iI < GC.getDefineINT("MAX_CIVIC_OPTIONS"); iI++)
                    {
                        if (GET_PLAYER(ePlayer).getCivics((CivicOptionTypes)iI) == kUnitInfo.getPrereqCivic())
                        {
                            bValid = true;
                        }
                    }
                }
                if (bValid == false)
                {
                    szBuffer.append(NEWLINE);
                    szBuffer.append(gDLL->getText("TXT_KEY_UNIT_REQUIRES_STRING", GC.getCivicInfo((CivicTypes)(kUnitInfo.getPrereqCivic())).getTextKeyWide()));
                }
            }
            if (kUnitInfo.getPrereqGlobalCounter() != 0)
            {
                if (GC.getGameINLINE().getActivePlayer() == NO_PLAYER || GC.getGameINLINE().getGlobalCounter() < kUnitInfo.getPrereqGlobalCounter())
                {
                    szBuffer.append(NEWLINE);
                    szBuffer.append(gDLL->getText("TXT_KEY_UNIT_PREREQ_GLOBAL_COUNTER", kUnitInfo.getPrereqGlobalCounter()));
                }
            }
//FfH: End Add

			if (!bTechChooserText)
			{
				if (kUnitInfo.getPrereqAndTech() != NO_TECH)
				{
					if (GC.getGameINLINE().getActivePlayer() == NO_PLAYER || !(GET_TEAM(GET_PLAYER(ePlayer).getTeam()).isHasTech((TechTypes)(kUnitInfo.getPrereqAndTech()))))
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_UNIT_REQUIRES_STRING", GC.getTechInfo((TechTypes)(kUnitInfo.getPrereqAndTech())).getTextKeyWide()));
					}
				}
			}

			bFirst = true;

			for (iI = 0; iI < GC.getNUM_UNIT_AND_TECH_PREREQS(); ++iI)
			{
				if (kUnitInfo.getPrereqAndTechs(iI) != NO_TECH)
				{
					if (bTechChooserText || GC.getGameINLINE().getActivePlayer() == NO_PLAYER || !(GET_TEAM(GET_PLAYER(ePlayer).getTeam()).isHasTech((TechTypes)(kUnitInfo.getPrereqAndTechs(iI)))))
					{
						szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_REQUIRES").c_str());
						setListHelp(szBuffer, szTempBuffer, GC.getTechInfo(((TechTypes)(kUnitInfo.getPrereqAndTechs(iI)))).getDescription(), gDLL->getText("TXT_KEY_AND").c_str(), bFirst);
						bFirst = false;
					}
				}
			}

			if (!bFirst)
			{
				szBuffer.append(ENDCOLR);
			}

			if (kUnitInfo.getPrereqAndBonus() != NO_BONUS)
			{
				if ((pCity == NULL) || !(pCity->hasBonus((BonusTypes)kUnitInfo.getPrereqAndBonus())))
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_UNIT_REQUIRES_STRING", GC.getBonusInfo((BonusTypes)(kUnitInfo.getPrereqAndBonus())).getTextKeyWide()));
				}
			}

			bFirst = true;

			for (iI = 0; iI < GC.getNUM_UNIT_PREREQ_OR_BONUSES(); ++iI)
			{
				if (kUnitInfo.getPrereqOrBonuses(iI) != NO_BONUS)
				{
					if ((pCity == NULL) || !(pCity->hasBonus((BonusTypes)kUnitInfo.getPrereqOrBonuses(iI))))
					{
						szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_REQUIRES").c_str());
						setListHelp(szBuffer, szTempBuffer, GC.getBonusInfo((BonusTypes) kUnitInfo.getPrereqOrBonuses(iI)).getDescription(), gDLL->getText("TXT_KEY_OR").c_str(), bFirst);
						bFirst = false;
					}
				}
			}

			if (!bFirst)
			{
				szBuffer.append(ENDCOLR);
			}
		}
	}

	// lfgr 10/2019: UnitPyInfoHelp
	if( strlen( kUnitInfo.getPyInfoHelp() ) > 0 )
	{
		CyCity* pyCity = pCity ? new CyCity(pCity) : NULL;
		CyArgsList argsList;
		argsList.add( eUnit );
		argsList.add( bCivilopediaText );
		argsList.add( bStrategyText );
		argsList.add( bTechChooserText );
		argsList.add(gDLL->getPythonIFace()->makePythonObject(pyCity)); // Might be None
		
		CvWString szHelp;
		gDLL->getPythonIFace()->callFunction(PYSpellModule, "getUnitInfoHelp", argsList.makeFunctionArgs(), &szHelp);
		szBuffer.append( NEWLINE );
		szBuffer.append( szHelp );
		SAFE_DELETE( pyCity ); // python fxn must not hold on to this pointer
	}
	// lfgr end

	if (!bCivilopediaText && GC.getGameINLINE().getActivePlayer() != NO_PLAYER)
	{
		if (pCity == NULL)
		{
			szTempBuffer.Format(L"%s%d%c", NEWLINE, GET_PLAYER(ePlayer).getProductionNeeded(eUnit), GC.getYieldInfo(YIELD_PRODUCTION).getChar());
			szBuffer.append(szTempBuffer);
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_TURNS", pCity->getProductionTurnsLeft(eUnit, ((gDLL->ctrlKey() || !(gDLL->shiftKey())) ? 0 : pCity->getOrderQueueLength())), pCity->getProductionNeeded(eUnit), GC.getYieldInfo(YIELD_PRODUCTION).getChar()));

			iProduction = pCity->getUnitProduction(eUnit);

			if (iProduction > 0)
			{
				szTempBuffer.Format(L" - %d/%d%c", iProduction, pCity->getProductionNeeded(eUnit), GC.getYieldInfo(YIELD_PRODUCTION).getChar());
				szBuffer.append(szTempBuffer);

// BUG - Production Decay - start
				if (getBugOptionBOOL("CityScreen__ProductionDecayHover", true, "BUG_PRODUCTION_DECAY_HOVER"))
				{
					// lfgr 09/2019: Tweaked with DisableProduction (Stasis) effects.
					setProductionDecayHelp(szBuffer, pCity->getUnitProductionDecayTurns(eUnit),
							getBugOptionINT("CityScreen__ProductionDecayHoverUnitThreshold", 5, "BUG_PRODUCTION_DECAY_HOVER_UNIT_THRESHOLD"),
							pCity->getUnitProductionDecay(eUnit), pCity->getProductionUnit() == eUnit,
							GET_PLAYER(ePlayer).getDisableProduction() != 0);
				}
// BUG - Production Decay - end
			}
			else
			{
				szTempBuffer.Format(L" - %d%c", pCity->getProductionNeeded(eUnit), GC.getYieldInfo(YIELD_PRODUCTION).getChar());
				szBuffer.append(szTempBuffer);
			}
			// ALN - debug info (production unit UnitAI)
			if (GC.getGameINLINE().isDebugMode() && pCity->getProductionUnitAI() != NO_UNITAI)
			{
				szTempBuffer.Format(L"\n%s (value: %d (MCV: %d)(TCV: %d)", GC.getUnitAIInfo(pCity->getProductionUnitAI()).getDescription(), GET_PLAYER(pCity->getOwner()).AI_unitValue(eUnit, pCity->getProductionUnitAI(), pCity->area()), GET_PLAYER(pCity->getOwner()).AI_magicCombatValue(eUnit), GET_PLAYER(pCity->getOwner()).AI_combatValue(eUnit));
				szBuffer.append(szTempBuffer);
			}
			// ALN End
		}
	}

	for (iI = 0; iI < GC.getNumBonusInfos(); ++iI)
	{
		if (kUnitInfo.getBonusProductionModifier(iI) != 0)
		{
			if (pCity != NULL)
			{
				if (pCity->hasBonus((BonusTypes)iI))
				{
					szBuffer.append(gDLL->getText("TXT_KEY_COLOR_POSITIVE"));
				}
				else
				{
					szBuffer.append(gDLL->getText("TXT_KEY_COLOR_NEGATIVE"));
				}
			}
			if (!bCivilopediaText)
			{
				szBuffer.append(L" (");
			}
			else
			{
				szTempBuffer.Format(L"%s%c", NEWLINE, gDLL->getSymbolID(BULLET_CHAR), szTempBuffer);
				szBuffer.append(szTempBuffer);
			}
			if (kUnitInfo.getBonusProductionModifier(iI) == 100)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_UNIT_DOUBLE_SPEED", GC.getBonusInfo((BonusTypes)iI).getTextKeyWide()));
			}
			else
			{
				szBuffer.append(gDLL->getText("TXT_KEY_UNIT_BUILDS_FASTER", kUnitInfo.getBonusProductionModifier(iI), GC.getBonusInfo((BonusTypes)iI).getTextKeyWide()));
			}
			if (!bCivilopediaText)
			{
				szBuffer.append(L")");
			}
			if (pCity != NULL)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
			}
		}
	}

	if (bStrategyText)
	{
		if (!CvWString(kUnitInfo.getStrategy()).empty())
		{
			if ((ePlayer == NO_PLAYER) || GET_PLAYER(ePlayer).isOption(PLAYEROPTION_ADVISOR_HELP))
			{
				szBuffer.append(SEPARATOR);
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_SIDS_TIPS"));
				szBuffer.append(L'\"');
				szBuffer.append(kUnitInfo.getStrategy());
				szBuffer.append(L'\"');
			}
		}
	}

	if (bCivilopediaText)
	{
		if (eDefaultUnit == eUnit)
		{
			for (iI = 0; iI < GC.getNumUnitInfos(); ++iI)
			{
				if (iI != eUnit)
				{
					if (eUnitClass == GC.getUnitInfo((UnitTypes)iI).getUnitClassType())
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_REPLACED_BY_UNIT", GC.getUnitInfo((UnitTypes)iI).getTextKeyWide()));
					}
				}
			}
		}
	}

	if (pCity != NULL)
	{
		if ((gDLL->getChtLvl() > 0) && gDLL->ctrlKey())
		{
			szBuffer.append(NEWLINE);
			for (int iUnitAI = 0; iUnitAI < NUM_UNITAI_TYPES; iUnitAI++)
			{
				int iTempValue = GET_PLAYER(pCity->getOwner()).AI_unitValue(eUnit, (UnitAITypes)iUnitAI, pCity->area());
				if (iTempValue != 0)
				{
					CvWString szTempString;
					getUnitAIString(szTempString, (UnitAITypes)iUnitAI);
					szBuffer.append(CvWString::format(L"(%s : %d) ", szTempString.GetCString(), iTempValue));
				}
			}
		}
	}
}

// BUG - Building Actual Effects - start
/*
 * Adds the actual effects of adding a building to the city.
 */
void CvGameTextMgr::setBuildingActualEffects(CvWStringBuffer &szBuffer, CvWString& szStart, BuildingTypes eBuilding, CvCity* pCity, bool bNewLine)
{
	if (NULL != pCity)
	{
		bool bStarted = false;

		// Defense
		int iDefense = pCity->getAdditionalDefenseByBuilding(eBuilding);
		bStarted = setResumableValueChangeHelp(szBuffer, szStart, L": ", L"", iDefense, gDLL->getSymbolID(DEFENSE_CHAR), true, bNewLine, bStarted);
		
		// Happiness
		int iGood = 0;
		int iBad = 0;
		pCity->getAdditionalHappinessByBuilding(eBuilding, iGood, iBad);
		int iAngryPop = pCity->getAdditionalAngryPopuplation(iGood, iBad);
		bStarted = setResumableGoodBadChangeHelp(szBuffer, szStart, L": ", L"", iGood, gDLL->getSymbolID(HAPPY_CHAR), iBad, gDLL->getSymbolID(UNHAPPY_CHAR), false, bNewLine, bStarted);
		bStarted = setResumableValueChangeHelp(szBuffer, szStart, L": ", L"", iAngryPop, gDLL->getSymbolID(ANGRY_POP_CHAR), false, bNewLine, bStarted);

		// Health
		iGood = 0;
		iBad = 0;
		pCity->getAdditionalHealthByBuilding(eBuilding, iGood, iBad);
		int iSpoiledFood = pCity->getAdditionalSpoiledFood(iGood, iBad);
		int iStarvation = pCity->getAdditionalStarvation(iSpoiledFood);
		bStarted = setResumableGoodBadChangeHelp(szBuffer, szStart, L": ", L"", iGood, gDLL->getSymbolID(HEALTHY_CHAR), iBad, gDLL->getSymbolID(UNHEALTHY_CHAR), false, bNewLine, bStarted);
		bStarted = setResumableValueChangeHelp(szBuffer, szStart, L": ", L"", iSpoiledFood, gDLL->getSymbolID(EATEN_FOOD_CHAR), false, bNewLine, bStarted);
		bStarted = setResumableValueChangeHelp(szBuffer, szStart, L": ", L"", iStarvation, gDLL->getSymbolID(BAD_FOOD_CHAR), false, bNewLine, bStarted);

		// Yield
		int aiYields[NUM_YIELD_TYPES];
		for (int iI = 0; iI < NUM_YIELD_TYPES; ++iI)
		{
			aiYields[iI] = pCity->getAdditionalYieldByBuilding((YieldTypes)iI, eBuilding);
		}
		bStarted = setResumableYieldChangeHelp(szBuffer, szStart, L": ", L"", aiYields, false, bNewLine, bStarted);
		
		// Commerce
		int aiCommerces[NUM_COMMERCE_TYPES];
		for (int iI = 0; iI < NUM_COMMERCE_TYPES; ++iI)
		{
			aiCommerces[iI] = pCity->getAdditionalCommerceTimes100ByBuilding((CommerceTypes)iI, eBuilding);
		}
		// Maintenance - add to gold
		aiCommerces[COMMERCE_GOLD] += pCity->getSavedMaintenanceTimes100ByBuilding(eBuilding);
		bStarted = setResumableCommerceTimes100ChangeHelp(szBuffer, szStart, L": ", L"", aiCommerces, bNewLine, bStarted);

		// Great People
		int iGreatPeopleRate = pCity->getAdditionalGreatPeopleRateByBuilding(eBuilding);
		bStarted = setResumableValueChangeHelp(szBuffer, szStart, L": ", L"", iGreatPeopleRate, gDLL->getSymbolID(GREAT_PEOPLE_CHAR), false, bNewLine, bStarted);
	}
}

/*
 * Calls new function below without displaying actual effects.
 */
void CvGameTextMgr::setBuildingHelp(CvWStringBuffer &szBuffer, BuildingTypes eBuilding, bool bCivilopediaText, bool bStrategyText, bool bTechChooserText, CvCity* pCity)
{
	setBuildingHelpActual(szBuffer, eBuilding, bCivilopediaText, bStrategyText, bTechChooserText, pCity, false);
}

/*
 * Adds option to display actual effects.
 */
void CvGameTextMgr::setBuildingHelpActual(CvWStringBuffer &szBuffer, BuildingTypes eBuilding, bool bCivilopediaText, bool bStrategyText, bool bTechChooserText, CvCity* pCity, bool bActual)
// BUG - Building Actual Effects - end
{
	PROFILE_FUNC();

	CvWString szFirstBuffer;
	CvWString szTempBuffer;
	BuildingTypes eLoopBuilding;
	UnitTypes eGreatPeopleUnit;
	PlayerTypes ePlayer;
	bool bFirst;
	int iProduction;
	int iLast;
	int iI;

	if (NO_BUILDING == eBuilding)
	{
		return;
	}

	CvBuildingInfo& kBuilding = GC.getBuildingInfo(eBuilding);


	if (pCity != NULL)
	{
		ePlayer = pCity->getOwnerINLINE();
	}
	else
	{
		ePlayer = GC.getGameINLINE().getActivePlayer();
	}

	if (!bCivilopediaText)
	{
		szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_BUILDING_TEXT"), kBuilding.getDescription());
		szBuffer.append(szTempBuffer);

		int iHappiness;
		if (NULL != pCity)
		{
			iHappiness = pCity->getBuildingHappiness(eBuilding);
		}
		else
		{
			iHappiness = kBuilding.getHappiness();
		}

		if (iHappiness != 0)
		{
			szTempBuffer.Format(L", +%d%c", abs(iHappiness), ((iHappiness > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)));
			szBuffer.append(szTempBuffer);
		}

		int iHealth;
		if (NULL != pCity)
		{
			iHealth = pCity->getBuildingGoodHealth(eBuilding);
		}
		else
		{
			iHealth = kBuilding.getHealth();
			if (ePlayer != NO_PLAYER)
			{
				if (eBuilding == GC.getCivilizationInfo(GET_PLAYER(ePlayer).getCivilizationType()).getCivilizationBuildings(kBuilding.getBuildingClassType()))
				{
					iHealth += GET_PLAYER(ePlayer).getExtraBuildingHealth(eBuilding);
				}
			}
		}
		if (iHealth != 0)
		{
			szTempBuffer.Format(L", +%d%c", abs(iHealth), ((iHealth > 0) ? gDLL->getSymbolID(HEALTHY_CHAR): gDLL->getSymbolID(UNHEALTHY_CHAR)));
			szBuffer.append(szTempBuffer);
		}

		iHealth = 0;
		if (NULL != pCity)
		{
			iHealth = pCity->getBuildingBadHealth(eBuilding);
		}
		if (iHealth != 0)
		{
			szTempBuffer.Format(L", +%d%c", abs(iHealth), ((iHealth > 0) ? gDLL->getSymbolID(HEALTHY_CHAR): gDLL->getSymbolID(UNHEALTHY_CHAR)));
			szBuffer.append(szTempBuffer);
		}

		int aiYields[NUM_YIELD_TYPES];
		for (iI = 0; iI < NUM_YIELD_TYPES; ++iI)
		{
			aiYields[iI] = kBuilding.getYieldChange(iI);

			if (NULL != pCity)
			{
				aiYields[iI] += pCity->getBuildingYieldChange((BuildingClassTypes)kBuilding.getBuildingClassType(), (YieldTypes)iI);
			}
		}
		setYieldChangeHelp(szBuffer, L", ", L"", L"", aiYields, false, false);

		int aiCommerces[NUM_COMMERCE_TYPES];
		for (int iI = 0; iI < NUM_COMMERCE_TYPES; ++iI)
		{
			if ((NULL != pCity) && (pCity->getNumBuilding(eBuilding) > 0))
			{
				aiCommerces[iI] = pCity->getBuildingCommerceByBuilding((CommerceTypes)iI, eBuilding);
			}
			else
			{
				aiCommerces[iI] = kBuilding.getCommerceChange(iI);
				aiCommerces[iI] += kBuilding.getObsoleteSafeCommerceChange(iI);
/*
** K-Mod, 30/dec/10, karadoc
** added relgious building bonus info
*/
				if (ePlayer != NO_PLAYER &&
					kBuilding.getReligionType() != NO_RELIGION &&
					kBuilding.getReligionType() == GET_PLAYER(ePlayer).getStateReligion())
				{
					aiCommerces[iI] += GET_PLAYER(ePlayer).getStateReligionBuildingCommerce((CommerceTypes)iI);
				}
/*
** K-Mod end
*/
			}
		}
		setCommerceChangeHelp(szBuffer, L", ", L"", L"", aiCommerces, false, false);

		setYieldChangeHelp(szBuffer, L", ", L"", L"", kBuilding.getYieldModifierArray(), true, bCivilopediaText);
		setCommerceChangeHelp(szBuffer, L", ", L"", L"", kBuilding.getCommerceModifierArray(), true, bCivilopediaText);

		if (kBuilding.getGreatPeopleRateChange() != 0)
		{
			szTempBuffer.Format(L", %s%d%c", ((kBuilding.getGreatPeopleRateChange() > 0) ? "+" : ""), kBuilding.getGreatPeopleRateChange(), gDLL->getSymbolID(GREAT_PEOPLE_CHAR));
			szBuffer.append(szTempBuffer);

			if (kBuilding.getGreatPeopleUnitClass() != NO_UNITCLASS)
			{
				if (ePlayer != NO_PLAYER)
				{
					eGreatPeopleUnit = ((UnitTypes)(GC.getCivilizationInfo(GET_PLAYER(ePlayer).getCivilizationType()).getCivilizationUnits(kBuilding.getGreatPeopleUnitClass())));
				}
				else
				{
					eGreatPeopleUnit = (UnitTypes)GC.getUnitClassInfo((UnitClassTypes)kBuilding.getGreatPeopleUnitClass()).getDefaultUnitIndex();
				}

				if (eGreatPeopleUnit != NO_UNIT)
				{
					szTempBuffer.Format(L" (%s)", GC.getUnitInfo(eGreatPeopleUnit).getDescription());
					szBuffer.append(szTempBuffer);
				}
			}
		}

// BUG - Building Actual Effects - start
		if (bActual && NULL != pCity && pCity->getOwnerINLINE() == GC.getGame().getActivePlayer() && getBugOptionBOOL("MiscHover__BuildingActualEffects", true, "BUG_BUILDING_HOVER_ACTUAL_EFFECTS"))
		{
			CvWString szStart = gDLL->getText("TXT_KEY_ACTUAL_EFFECTS");
			setBuildingActualEffects(szBuffer, szStart, eBuilding, pCity);
		}
// BUG - Building Actual Effects - end
	}

	// test for unique building
	BuildingClassTypes eBuildingClass = (BuildingClassTypes)kBuilding.getBuildingClassType();
	BuildingTypes eDefaultBuilding = (BuildingTypes)GC.getBuildingClassInfo(eBuildingClass).getDefaultBuildingIndex();

	if (NO_BUILDING != eDefaultBuilding && eDefaultBuilding != eBuilding)
	{
		for (iI  = 0; iI < GC.getNumCivilizationInfos(); ++iI)
		{
			BuildingTypes eUniqueBuilding = (BuildingTypes)GC.getCivilizationInfo((CivilizationTypes)iI).getCivilizationBuildings((int)eBuildingClass);
			if (eUniqueBuilding == eBuilding)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_UNIQUE_BUILDING", GC.getCivilizationInfo((CivilizationTypes)iI).getTextKeyWide()));
			}
		}

		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_REPLACES_UNIT", GC.getBuildingInfo(eDefaultBuilding).getTextKeyWide()));
	}

	if (bCivilopediaText)
	{
		setYieldChangeHelp(szBuffer, L"", L"", L"", kBuilding.getYieldModifierArray(), true, bCivilopediaText);

		setCommerceChangeHelp(szBuffer, L"", L"", L"", kBuilding.getCommerceModifierArray(), true, bCivilopediaText);
	}
	else
	{
		if (isWorldWonderClass((BuildingClassTypes)(kBuilding.getBuildingClassType())))
		{
			if (pCity == NULL || ePlayer == NO_PLAYER)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_WORLD_WONDER_ALLOWED", GC.getBuildingClassInfo((BuildingClassTypes) kBuilding.getBuildingClassType()).getMaxGlobalInstances()));
			}
			else
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_WORLD_WONDER_LEFT", (GC.getBuildingClassInfo((BuildingClassTypes) kBuilding.getBuildingClassType()).getMaxGlobalInstances() - GC.getGameINLINE().getBuildingClassCreatedCount((BuildingClassTypes)(kBuilding.getBuildingClassType())) - GET_TEAM(GET_PLAYER(ePlayer).getTeam()).getBuildingClassMaking((BuildingClassTypes)(kBuilding.getBuildingClassType())))));
			}
		}

		if (isTeamWonderClass((BuildingClassTypes)(kBuilding.getBuildingClassType())))
		{
			if (pCity == NULL || ePlayer == NO_PLAYER)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_TEAM_WONDER_ALLOWED", GC.getBuildingClassInfo((BuildingClassTypes) kBuilding.getBuildingClassType()).getMaxTeamInstances()));
			}
			else
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_TEAM_WONDER_LEFT", (GC.getBuildingClassInfo((BuildingClassTypes) kBuilding.getBuildingClassType()).getMaxTeamInstances() - GET_TEAM(GET_PLAYER(ePlayer).getTeam()).getBuildingClassCountPlusMaking((BuildingClassTypes)(kBuilding.getBuildingClassType())))));
			}
		}

		if (isNationalWonderClass((BuildingClassTypes)(kBuilding.getBuildingClassType())))
		{
			if (pCity == NULL || ePlayer == NO_PLAYER)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_NATIONAL_WONDER_ALLOWED", GC.getBuildingClassInfo((BuildingClassTypes) kBuilding.getBuildingClassType()).getMaxPlayerInstances()));
			}
			else
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_NATIONAL_WONDER_LEFT", (GC.getBuildingClassInfo((BuildingClassTypes) kBuilding.getBuildingClassType()).getMaxPlayerInstances() - GET_PLAYER(ePlayer).getBuildingClassCountPlusMaking((BuildingClassTypes)(kBuilding.getBuildingClassType())))));
			}
		}
	}

	if (kBuilding.getGlobalReligionCommerce() != NO_RELIGION)
	{
		szFirstBuffer = gDLL->getText("TXT_KEY_BUILDING_PER_CITY_WITH", GC.getReligionInfo((ReligionTypes) kBuilding.getGlobalReligionCommerce()).getChar());
		setCommerceChangeHelp(szBuffer, L"", L"", szFirstBuffer, GC.getReligionInfo((ReligionTypes) kBuilding.getGlobalReligionCommerce()).getGlobalReligionCommerceArray());
	}

	if (NO_CORPORATION != kBuilding.getFoundsCorporation())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_FOUNDS_CORPORATION", GC.getCorporationInfo((CorporationTypes)kBuilding.getFoundsCorporation()).getTextKeyWide()));
	}

	if (kBuilding.getGlobalCorporationCommerce() != NO_CORPORATION)
	{
		szFirstBuffer = gDLL->getText("TXT_KEY_BUILDING_PER_CITY_WITH", GC.getCorporationInfo((CorporationTypes) kBuilding.getGlobalCorporationCommerce()).getChar());
		setCommerceChangeHelp(szBuffer, L"", L"", szFirstBuffer, GC.getCorporationInfo((CorporationTypes) kBuilding.getGlobalCorporationCommerce()).getHeadquarterCommerceArray());
	}

	if (kBuilding.getNoBonus() != NO_BONUS)
	{
		CvBonusInfo& kBonus = GC.getBonusInfo((BonusTypes) kBuilding.getNoBonus());
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_DISABLES", kBonus.getTextKeyWide(), kBonus.getChar()));
	}

	if (kBuilding.getFreeBonus() != NO_BONUS)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_PROVIDES", GC.getGameINLINE().getNumFreeBonuses(eBuilding), GC.getBonusInfo((BonusTypes) kBuilding.getFreeBonus()).getTextKeyWide(), GC.getBonusInfo((BonusTypes) kBuilding.getFreeBonus()).getChar()));

		if (GC.getBonusInfo((BonusTypes)(kBuilding.getFreeBonus())).getHealth() != 0)
		{
			szTempBuffer.Format(L", +%d%c", abs(GC.getBonusInfo((BonusTypes) kBuilding.getFreeBonus()).getHealth()), ((GC.getBonusInfo((BonusTypes)(kBuilding.getFreeBonus())).getHealth() > 0) ? gDLL->getSymbolID(HEALTHY_CHAR): gDLL->getSymbolID(UNHEALTHY_CHAR)));
			szBuffer.append(szTempBuffer);
		}

		if (GC.getBonusInfo((BonusTypes)(kBuilding.getFreeBonus())).getHappiness() != 0)
		{
			szTempBuffer.Format(L", +%d%c", abs(GC.getBonusInfo((BonusTypes) kBuilding.getFreeBonus()).getHappiness()), ((GC.getBonusInfo((BonusTypes)(kBuilding.getFreeBonus())).getHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)));
			szBuffer.append(szTempBuffer);
		}
	}

//FfH: Added by Kael 08/04/2007
	if (kBuilding.getFreeBonus2() != NO_BONUS)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_PROVIDES", GC.getGameINLINE().getNumFreeBonuses(eBuilding), GC.getBonusInfo((BonusTypes) kBuilding.getFreeBonus2()).getTextKeyWide(), GC.getBonusInfo((BonusTypes) kBuilding.getFreeBonus2()).getChar()));
		if (GC.getBonusInfo((BonusTypes)(kBuilding.getFreeBonus2())).getHealth() != 0)
		{
			szTempBuffer.Format(L", +%d%c", abs(GC.getBonusInfo((BonusTypes) kBuilding.getFreeBonus2()).getHealth()), ((GC.getBonusInfo((BonusTypes)(kBuilding.getFreeBonus2())).getHealth() > 0) ? gDLL->getSymbolID(HEALTHY_CHAR): gDLL->getSymbolID(UNHEALTHY_CHAR)));
			szBuffer.append(szTempBuffer);
		}
		if (GC.getBonusInfo((BonusTypes)(kBuilding.getFreeBonus2())).getHappiness() != 0)
		{
			szTempBuffer.Format(L", +%d%c", abs(GC.getBonusInfo((BonusTypes) kBuilding.getFreeBonus2()).getHappiness()), ((GC.getBonusInfo((BonusTypes)(kBuilding.getFreeBonus2())).getHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)));
			szBuffer.append(szTempBuffer);
		}
	}
	if (kBuilding.getFreeBonus3() != NO_BONUS)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_PROVIDES", GC.getGameINLINE().getNumFreeBonuses(eBuilding), GC.getBonusInfo((BonusTypes) kBuilding.getFreeBonus3()).getTextKeyWide(), GC.getBonusInfo((BonusTypes) kBuilding.getFreeBonus3()).getChar()));
		if (GC.getBonusInfo((BonusTypes)(kBuilding.getFreeBonus3())).getHealth() != 0)
		{
			szTempBuffer.Format(L", +%d%c", abs(GC.getBonusInfo((BonusTypes) kBuilding.getFreeBonus3()).getHealth()), ((GC.getBonusInfo((BonusTypes)(kBuilding.getFreeBonus3())).getHealth() > 0) ? gDLL->getSymbolID(HEALTHY_CHAR): gDLL->getSymbolID(UNHEALTHY_CHAR)));
			szBuffer.append(szTempBuffer);
		}
		if (GC.getBonusInfo((BonusTypes)(kBuilding.getFreeBonus3())).getHappiness() != 0)
		{
			szTempBuffer.Format(L", +%d%c", abs(GC.getBonusInfo((BonusTypes) kBuilding.getFreeBonus3()).getHappiness()), ((GC.getBonusInfo((BonusTypes)(kBuilding.getFreeBonus3())).getHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)));
			szBuffer.append(szTempBuffer);
		}
	}

    if (kBuilding.getCrime() != 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_CRIME", kBuilding.getCrime()));
    }
    if (kBuilding.getFreePromotionPick() > 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_FREE_PROMOTION_PICK", kBuilding.getFreePromotionPick()));
    }
    if (kBuilding.getModifyGlobalCounter() != 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_MESSAGE_MODIFY_GLOBAL_COUNTER", kBuilding.getModifyGlobalCounter()));
    }
    if (kBuilding.getRemovePromotion() > NO_PROMOTION)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_REMOVE_PROMOTION", GC.getPromotionInfo((PromotionTypes)kBuilding.getRemovePromotion()).getDescription()));
    }
    if (kBuilding.getResistMagic() != 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_RESIST_MAGIC", kBuilding.getResistMagic()));
    }
    if (kBuilding.getGlobalResistEnemyModify() != 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_GLOBAL_RESIST_ENEMY_MODIFY", kBuilding.getGlobalResistEnemyModify()));
    }
    if (kBuilding.getGlobalResistModify() != 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_GLOBAL_RESIST_MODIFY", kBuilding.getGlobalResistModify()));
    }
    if (kBuilding.isHideUnits())
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_HIDE_UNITS"));
    }
    if (kBuilding.isUnhappyProduction())
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_UNHAPPY_PRODUCTION"));
		if(GC.getGameINLINE().isOption(GAMEOPTION_REVOLUTIONS))
			szBuffer.append(L", reduces Revolution Penalty from Unhappiness");
    }
    if (kBuilding.isRequiresCaster())
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_REQUIRES_CASTER"));
    }
    if (kBuilding.isSeeInvisible())
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_SEE_INVISIBLE"));
    }
	for (iI = 0; iI < GC.getNumSpecialistInfos(); ++iI)
	{
		szFirstBuffer = gDLL->getText("TXT_KEY_BUILDING_FROM_IN_ALL_CITIES", GC.getSpecialistInfo((SpecialistTypes) iI).getTextKeyWide());
		setCommerceChangeHelp(szBuffer, L"", L"", szFirstBuffer, kBuilding.getSpecialistCommerceChangeArray(iI));
//        setCommerceChangeHelp(szHelpText, L"", L"", gDLL->getText("TXT_KEY_CIVIC_IN_ALL_CITIES").GetCString(), GC.getCivicInfo(eCivic).getCommerceModifierArray(), true);
    }
    if (kBuilding.isNoCivicAnger())
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_NO_CIVIC_ANGER"));
    }
    if (kBuilding.getPlotRadius() != 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_PLOT_RADIUS", kBuilding.getPlotRadius()));
    }
//FfH: End Add

	if (kBuilding.getFreeBuildingClass() != NO_BUILDINGCLASS)
	{
		BuildingTypes eFreeBuilding;
		if (ePlayer != NO_PLAYER)
		{
			eFreeBuilding = ((BuildingTypes)(GC.getCivilizationInfo(GET_PLAYER(ePlayer).getCivilizationType()).getCivilizationBuildings(kBuilding.getFreeBuildingClass())));
		}
		else
		{
			eFreeBuilding = (BuildingTypes)GC.getBuildingClassInfo((BuildingClassTypes)kBuilding.getFreeBuildingClass()).getDefaultBuildingIndex();
		}

		if (NO_BUILDING != eFreeBuilding)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_FREE_IN_CITY", GC.getBuildingInfo(eFreeBuilding).getTextKeyWide()));
		}
	}

	if (kBuilding.getFreePromotion() != NO_PROMOTION)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_FREE_PROMOTION", GC.getPromotionInfo((PromotionTypes)(kBuilding.getFreePromotion())).getTextKeyWide()));

//FfH: Added by Kael 08/04/2007
        if (kBuilding.isApplyFreePromotionOnMove())
        {
            szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_APPLY_FREE_PROMOTION_ON_MOVE"));
        }
//FfH: End Add

	}

	if (kBuilding.getCivicOption() != NO_CIVICOPTION)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_ENABLES_CIVICS", GC.getCivicOptionInfo((CivicOptionTypes)(kBuilding.getCivicOption())).getTextKeyWide()));
	}

	if (kBuilding.isPower())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_PROVIDES_POWER"));

		if (kBuilding.isDirtyPower() && (GC.getDefineINT("DIRTY_POWER_HEALTH_CHANGE") != 0))
		{
			szTempBuffer.Format(L" (+%d%c)", abs(GC.getDefineINT("DIRTY_POWER_HEALTH_CHANGE")), ((GC.getDefineINT("DIRTY_POWER_HEALTH_CHANGE") > 0) ? gDLL->getSymbolID(HEALTHY_CHAR): gDLL->getSymbolID(UNHEALTHY_CHAR)));
			szBuffer.append(szTempBuffer);
		}
	}

	if (kBuilding.isAreaCleanPower())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_PROVIDES_AREA_CLEAN_POWER"));
	}

	if (kBuilding.isAreaBorderObstacle())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_BORDER_OBSTACLE"));
	}

	for (iI = 0; iI < GC.getNumVoteSourceInfos(); ++iI)
	{
		if (kBuilding.getVoteSourceType() == (VoteSourceTypes)iI)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_DIPLO_VOTE", GC.getVoteSourceInfo((VoteSourceTypes)iI).getTextKeyWide()));
		}
	}

	if (kBuilding.isForceTeamVoteEligible())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_ELECTION_ELIGIBILITY"));
	}

	if (kBuilding.isCapital())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_CAPITAL"));
	}

	if (kBuilding.isGovernmentCenter())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_REDUCES_MAINTENANCE"));
	}

	if (kBuilding.isGoldenAge())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_GOLDEN_AGE"));
	}

	if (kBuilding.isAllowsNukes())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_ENABLES_NUKES"));
	}

	if (kBuilding.isMapCentering())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_CENTERS_MAP"));
	}

	if (kBuilding.isNoUnhappiness())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_NO_UNHAPPY"));
	}

	if (kBuilding.isNoUnhealthyPopulation())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_NO_UNHEALTHY_POP"));
	}

	if (kBuilding.isBuildingOnlyHealthy())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_NO_UNHEALTHY_BUILDINGS"));
	}

	if (kBuilding.getGreatPeopleRateModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_BIRTH_RATE_MOD", kBuilding.getGreatPeopleRateModifier()));
	}

	if (kBuilding.getGreatGeneralRateModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_GENERAL_RATE_MOD", kBuilding.getGreatGeneralRateModifier()));
	}

	if (kBuilding.getDomesticGreatGeneralRateModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_DOMESTIC_GREAT_GENERAL_MODIFIER", kBuilding.getDomesticGreatGeneralRateModifier()));
	}

	if (kBuilding.getGlobalGreatPeopleRateModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_BIRTH_RATE_MOD_ALL_CITIES", kBuilding.getGlobalGreatPeopleRateModifier()));
	}

	if (kBuilding.getAnarchyModifier() != 0)
	{
		if (-100 == kBuilding.getAnarchyModifier())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_NO_ANARCHY"));
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_ANARCHY_MOD", kBuilding.getAnarchyModifier()));

			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_ANARCHY_TIMER_MOD", kBuilding.getAnarchyModifier()));
		}
	}

	if (kBuilding.getGoldenAgeModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_GOLDENAGE_MOD", kBuilding.getGoldenAgeModifier()));
	}

	if (kBuilding.getGlobalHurryModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_HURRY_MOD", kBuilding.getGlobalHurryModifier()));
	}

	if (kBuilding.getFreeExperience() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_FREE_XP_UNITS", kBuilding.getFreeExperience()));
	}

	if (kBuilding.getGlobalFreeExperience() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_FREE_XP_ALL_CITIES", kBuilding.getGlobalFreeExperience()));
	}

	if (kBuilding.getFoodKept() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_STORES_FOOD", kBuilding.getFoodKept()));
	}

	if (kBuilding.getAirlift() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_AIRLIFT", kBuilding.getAirlift()));
	}

	if (kBuilding.getAirModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_AIR_DAMAGE_MOD", kBuilding.getAirModifier()));
	}

	if (kBuilding.getAirUnitCapacity() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_AIR_UNIT_CAPACITY", kBuilding.getAirUnitCapacity()));
	}

	if (kBuilding.getNukeModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_NUKE_DAMAGE_MOD", kBuilding.getNukeModifier()));
	}

	if (kBuilding.getNukeExplosionRand() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_NUKE_EXPLOSION_CHANCE"));
	}

	if (kBuilding.getFreeSpecialist() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_FREE_SPECIALISTS", kBuilding.getFreeSpecialist()));
	}

	if (kBuilding.getAreaFreeSpecialist() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_FREE_SPECIALISTS_CONT", kBuilding.getAreaFreeSpecialist()));
	}

	if (kBuilding.getGlobalFreeSpecialist() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_FREE_SPECIALISTS_ALL_CITIES", kBuilding.getGlobalFreeSpecialist()));
	}

	if (kBuilding.getMaintenanceModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_MAINT_MOD", kBuilding.getMaintenanceModifier()));
	}

	if (kBuilding.getHurryAngerModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_HURRY_ANGER_MOD", kBuilding.getHurryAngerModifier()));
	}

// Start Revolutions
	if (GC.getGameINLINE().isOption(GAMEOPTION_REVOLUTIONS))
	{
		//  Revolution Local Index Modifiers
		if (0 != kBuilding.getRevIdxLocal())
		{
			if ( kBuilding.getRevIdxLocal() > 0 )
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_REV_INDEX_LOCAL_PENALTY", kBuilding.getRevIdxLocal()));
			}
			if ( kBuilding.getRevIdxLocal() < 0 )
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_REV_INDEX_LOCAL_BONUS", abs(kBuilding.getRevIdxLocal())));
			}
		}
		
		//  Revolution National Index Modifiers
		if (0 != kBuilding.getRevIdxNational())
		{
			if ( kBuilding.getRevIdxNational() > 0 )
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_CIVIC_REV_INDEX_NATIONAL_PENALTY", kBuilding.getRevIdxNational()));
			}
			if ( kBuilding.getRevIdxNational() < 0 )
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_CIVIC_REV_INDEX_NATIONAL_BONUS", abs(kBuilding.getRevIdxNational())));
			}
		}
		
		//  Revolution City Distance Modifier
		if (0 != kBuilding.getRevIdxDistanceModifier())
		{
			if ( kBuilding.getRevIdxDistanceModifier() < 0 )
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_CIVIC_CITY_DISTANCE_GOOD_MOD", kBuilding.getRevIdxDistanceModifier()));
			}
			if ( kBuilding.getRevIdxDistanceModifier() > 0 )
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_CIVIC_CITY_DISTANCE_BAD_MOD", abs(kBuilding.getRevIdxDistanceModifier())));
			}
		}
	}
// End Revolutions



	if (kBuilding.getWarWearinessModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_WAR_WEAR_MOD", kBuilding.getWarWearinessModifier()));
	}

	if (kBuilding.getGlobalWarWearinessModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_WAR_WEAR_MOD_ALL_CITIES", kBuilding.getGlobalWarWearinessModifier()));
	}

	if (kBuilding.getEnemyWarWearinessModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_ENEMY_WAR_WEAR", kBuilding.getEnemyWarWearinessModifier()));
	}

	if (kBuilding.getHealRateChange() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_HEAL_MOD", kBuilding.getHealRateChange()));
	}

	if (kBuilding.getAreaHealth() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_HEALTH_CHANGE_CONT", abs(kBuilding.getAreaHealth()), ((kBuilding.getAreaHealth() > 0) ? gDLL->getSymbolID(HEALTHY_CHAR): gDLL->getSymbolID(UNHEALTHY_CHAR))));
	}

	if (kBuilding.getGlobalHealth() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_HEALTH_CHANGE_ALL_CITIES", abs(kBuilding.getGlobalHealth()), ((kBuilding.getGlobalHealth() > 0) ? gDLL->getSymbolID(HEALTHY_CHAR): gDLL->getSymbolID(UNHEALTHY_CHAR))));
	}

/************************************************************************************************/
/* UNOFFICIAL_PATCH                       08/28/09                             jdog5000         */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
	if (kBuilding.getAreaHappiness() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_HAPPY_CHANGE_CONT", kBuilding.getAreaHappiness(), ((kBuilding.getAreaHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR))));
	}

	if (kBuilding.getGlobalHappiness() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_HAPPY_CHANGE_ALL_CITIES", kBuilding.getGlobalHappiness(), ((kBuilding.getGlobalHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR))));
	}

	if (kBuilding.getStateReligionHappiness() > 0)
	{
		if (kBuilding.getReligionType() != NO_RELIGION)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_RELIGION_HAPPINESS", kBuilding.getStateReligionHappiness(), ((kBuilding.getStateReligionHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)), GC.getReligionInfo((ReligionTypes)(kBuilding.getReligionType())).getChar()));
		}
	}
*/
	// Use absolute value with unhappy face
	if (kBuilding.getAreaHappiness() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_HAPPY_CHANGE_CONT", abs(kBuilding.getAreaHappiness()), ((kBuilding.getAreaHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR))));
	}

	if (kBuilding.getGlobalHappiness() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_HAPPY_CHANGE_ALL_CITIES", abs(kBuilding.getGlobalHappiness()), ((kBuilding.getGlobalHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR))));
	}

	if (kBuilding.getStateReligionHappiness() != 0)
	{
		if (kBuilding.getReligionType() != NO_RELIGION)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_RELIGION_HAPPINESS", abs(kBuilding.getStateReligionHappiness()), ((kBuilding.getStateReligionHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)), GC.getReligionInfo((ReligionTypes)(kBuilding.getReligionType())).getChar()));
		}
	}
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/

	if (kBuilding.getWorkerSpeedModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_WORKER_MOD", kBuilding.getWorkerSpeedModifier()));
	}

	if (kBuilding.getMilitaryProductionModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_MILITARY_MOD", kBuilding.getMilitaryProductionModifier()));
	}

	if (kBuilding.getSpaceProductionModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_SPACESHIP_MOD", kBuilding.getSpaceProductionModifier()));
	}

	if (kBuilding.getGlobalSpaceProductionModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_SPACESHIP_MOD_ALL_CITIES", kBuilding.getGlobalSpaceProductionModifier()));
	}

	if (kBuilding.getTradeRoutes() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_TRADE_ROUTES", kBuilding.getTradeRoutes()));
	}

	if (kBuilding.getCoastalTradeRoutes() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_COASTAL_TRADE_ROUTES", kBuilding.getCoastalTradeRoutes()));
	}

	if (kBuilding.getGlobalTradeRoutes() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_TRADE_ROUTES_ALL_CITIES", kBuilding.getGlobalTradeRoutes()));
	}

	if (kBuilding.getTradeRouteModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_TRADE_ROUTE_MOD", kBuilding.getTradeRouteModifier()));
	}

	if (kBuilding.getForeignTradeRouteModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_FOREIGN_TRADE_ROUTE_MOD", kBuilding.getForeignTradeRouteModifier()));
	}

	if (kBuilding.getGlobalPopulationChange() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_GLOBAL_POP", kBuilding.getGlobalPopulationChange()));
	}

	if (kBuilding.getFreeTechs() != 0)
	{
		if (kBuilding.getFreeTechs() == 1)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_FREE_TECH"));
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_FREE_TECHS", kBuilding.getFreeTechs()));
		}
	}

	if (kBuilding.getDefenseModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_DEFENSE_MOD", kBuilding.getDefenseModifier()));
	}

	if (kBuilding.getBombardDefenseModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_BOMBARD_DEFENSE_MOD", -kBuilding.getBombardDefenseModifier()));
	}

	if (kBuilding.getAllCityDefenseModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_DEFENSE_MOD_ALL_CITIES", kBuilding.getAllCityDefenseModifier()));
	}

	if (kBuilding.getEspionageDefenseModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_ESPIONAGE_DEFENSE_MOD", kBuilding.getEspionageDefenseModifier()));
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       12/07/09                      Afforess & jdog5000     */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original BTS code
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_EXPOSE_SPIES"));
*/		
		if (kBuilding.getEspionageDefenseModifier() > 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_EXPOSE_SPIES"));
		}
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
	}

	setYieldChangeHelp(szBuffer, gDLL->getText("TXT_KEY_BUILDING_WATER_PLOTS").c_str(), L": ", L"", kBuilding.getSeaPlotYieldChangeArray());

	setYieldChangeHelp(szBuffer, gDLL->getText("TXT_KEY_BUILDING_RIVER_PLOTS").c_str(), L": ", L"", kBuilding.getRiverPlotYieldChangeArray());

	setYieldChangeHelp(szBuffer, gDLL->getText("TXT_KEY_BUILDING_WATER_PLOTS_ALL_CITIES").c_str(), L": ", L"", kBuilding.getGlobalSeaPlotYieldChangeArray());

	setYieldChangeHelp(szBuffer, L"", L"", gDLL->getText("TXT_KEY_BUILDING_WITH_POWER").c_str(), kBuilding.getPowerYieldModifierArray(), true);

	setYieldChangeHelp(szBuffer, L"", L"", gDLL->getText("TXT_KEY_BUILDING_ALL_CITIES_THIS_CONTINENT").c_str(), kBuilding.getAreaYieldModifierArray(), true);

	setYieldChangeHelp(szBuffer, L"", L"", gDLL->getText("TXT_KEY_BUILDING_ALL_CITIES").c_str(), kBuilding.getGlobalYieldModifierArray(), true);

	setCommerceChangeHelp(szBuffer, L"", L"", gDLL->getText("TXT_KEY_BUILDING_ALL_CITIES").c_str(), kBuilding.getGlobalCommerceModifierArray(), true);

	setCommerceChangeHelp(szBuffer, L"", L"", gDLL->getText("TXT_KEY_BUILDING_PER_SPECIALIST_ALL_CITIES").c_str(), kBuilding.getSpecialistExtraCommerceArray());

	if (ePlayer != NO_PLAYER && GET_PLAYER(ePlayer).getStateReligion() != NO_RELIGION)
	{
		szTempBuffer = gDLL->getText("TXT_KEY_BUILDING_FROM_ALL_REL_BUILDINGS", GC.getReligionInfo(GET_PLAYER(ePlayer).getStateReligion()).getChar());
	}
	else
	{
		szTempBuffer = gDLL->getText("TXT_KEY_BUILDING_STATE_REL_BUILDINGS");
	}
	setCommerceChangeHelp(szBuffer, L"", L"", szTempBuffer, kBuilding.getStateReligionCommerceArray());

	for (iI = 0; iI < NUM_COMMERCE_TYPES; ++iI)
	{
		if (kBuilding.getCommerceHappiness(iI) != 0)
		{
			szBuffer.append(NEWLINE);
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       08/28/09                             jdog5000         */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_PER_LEVEL", ((kBuilding.getCommerceHappiness(iI) > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)), (100 / kBuilding.getCommerceHappiness(iI)), GC.getCommerceInfo((CommerceTypes)iI).getChar()));
*/
			// Use absolute value with unhappy face
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_PER_LEVEL", ((kBuilding.getCommerceHappiness(iI) > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)), abs(100 / kBuilding.getCommerceHappiness(iI)), GC.getCommerceInfo((CommerceTypes)iI).getChar()));
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
		}

		if (kBuilding.isCommerceFlexible(iI) != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_ADJUST_COMM_RATE", GC.getCommerceInfo((CommerceTypes) iI).getChar()));
		}
	}

	for (iI = 0; iI < GC.getNumSpecialistInfos(); ++iI)
	{
		szFirstBuffer = gDLL->getText("TXT_KEY_BUILDING_FROM_IN_ALL_CITIES", GC.getSpecialistInfo((SpecialistTypes) iI).getTextKeyWide());
		setYieldChangeHelp(szBuffer, L"", L"", szFirstBuffer, kBuilding.getSpecialistYieldChangeArray(iI));
	}

	for (iI = 0; iI < GC.getNumBonusInfos(); ++iI)
	{
		szFirstBuffer = gDLL->getText("TXT_KEY_BUILDING_WITH_BONUS", GC.getBonusInfo((BonusTypes) iI).getTextKeyWide());
		setYieldChangeHelp(szBuffer, L"", L"", szFirstBuffer, kBuilding.getBonusYieldModifierArray(iI), true);
	}

	for (iI = 0; iI < GC.getNumReligionInfos(); ++iI)
	{
		if (kBuilding.getReligionChange(iI) > 0)
		{
			szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_BUILDING_SPREADS_RELIGION", GC.getReligionInfo((ReligionTypes) iI).getChar()).c_str());
			szBuffer.append(szTempBuffer);
		}
	}

	for (iI = 0; iI < GC.getNumSpecialistInfos(); ++iI)
	{
		if (kBuilding.getSpecialistCount(iI) > 0)
		{
			if (kBuilding.getSpecialistCount(iI) == 1)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_TURN_CITIZEN_INTO", GC.getSpecialistInfo((SpecialistTypes) iI).getTextKeyWide()));
			}
			else
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_TURN_CITIZENS_INTO", kBuilding.getSpecialistCount(iI), GC.getSpecialistInfo((SpecialistTypes) iI).getTextKeyWide()));
			}
		}

		if (kBuilding.getFreeSpecialistCount(iI) > 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_FREE_SPECIALIST", kBuilding.getFreeSpecialistCount(iI), GC.getSpecialistInfo((SpecialistTypes) iI).getTextKeyWide()));
		}
	}

	iLast = 0;

	for (iI = 0; iI < GC.getNumImprovementInfos(); ++iI)
	{
		if (kBuilding.getImprovementFreeSpecialist(iI) > 0)
		{
			szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_BUILDING_IMPROVEMENT_FREE_SPECIALISTS", kBuilding.getImprovementFreeSpecialist(iI)).GetCString() );
			szTempBuffer.Format(L"<link=literal>%s</link>", GC.getImprovementInfo((ImprovementTypes)iI).getDescription());
			setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", (kBuilding.getImprovementFreeSpecialist(iI) != iLast));
			iLast = kBuilding.getImprovementFreeSpecialist(iI);
		}
	}

	iLast = 0;

	for (iI = 0; iI < GC.getNumBonusInfos(); ++iI)
	{
		if (kBuilding.getBonusHealthChanges(iI) != 0)
		{
			szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_BUILDING_HEALTH_HAPPINESS_CHANGE", abs(kBuilding.getBonusHealthChanges(iI)), ((kBuilding.getBonusHealthChanges(iI) > 0) ? gDLL->getSymbolID(HEALTHY_CHAR): gDLL->getSymbolID(UNHEALTHY_CHAR))).c_str());
			szTempBuffer.Format(L"<link=literal>%s</link>", GC.getBonusInfo((BonusTypes)iI).getDescription());
			setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", (kBuilding.getBonusHealthChanges(iI) != iLast));
			iLast = kBuilding.getBonusHealthChanges(iI);
		}
	}

	iLast = 0;

	for (iI = 0; iI < GC.getNumCivicInfos(); ++iI)
	{
		int iChange = GC.getCivicInfo((CivicTypes)iI).getBuildingHealthChanges(kBuilding.getBuildingClassType());
		if (0 != iChange)
		{
			szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_BUILDING_CIVIC_HEALTH_HAPPINESS_CHANGE", abs(iChange), ((iChange > 0) ? gDLL->getSymbolID(HEALTHY_CHAR): gDLL->getSymbolID(UNHEALTHY_CHAR))).c_str());
			szTempBuffer.Format(L"<link=literal>%s</link>", GC.getCivicInfo((CivicTypes)iI).getDescription());
			setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", (iChange != iLast));
			iLast = iChange;
		}
	}

	iLast = 0;

	for (iI = 0; iI < GC.getNumBonusInfos(); ++iI)
	{
		if (kBuilding.getBonusHappinessChanges(iI) != 0)
		{
			szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_BUILDING_HEALTH_HAPPINESS_CHANGE", abs(kBuilding.getBonusHappinessChanges(iI)), ((kBuilding.getBonusHappinessChanges(iI) > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR))).c_str());
			szTempBuffer.Format(L"<link=literal>%s</link>", GC.getBonusInfo((BonusTypes)iI).getDescription());
			setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", (kBuilding.getBonusHappinessChanges(iI) != iLast));
			iLast = kBuilding.getBonusHappinessChanges(iI);
		}
	}

	iLast = 0;

	for (iI = 0; iI < GC.getNumCivicInfos(); ++iI)
	{
		int iChange = GC.getCivicInfo((CivicTypes)iI).getBuildingHappinessChanges(kBuilding.getBuildingClassType());
		if (0 != iChange)
		{
			szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_BUILDING_CIVIC_HEALTH_HAPPINESS_CHANGE", abs(iChange), ((iChange > 0) ? gDLL->getSymbolID(HAPPY_CHAR): gDLL->getSymbolID(UNHAPPY_CHAR))).c_str());
			szTempBuffer.Format(L"<link=literal>%s</link>", GC.getCivicInfo((CivicTypes)iI).getDescription());
			setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", (iChange != iLast));
			iLast = iChange;
		}
	}

	for (iI = 0; iI < GC.getNumUnitCombatInfos(); ++iI)
	{
		if (kBuilding.getUnitCombatFreeExperience(iI) != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_FREE_XP", GC.getUnitCombatInfo((UnitCombatTypes)iI).getTextKeyWide(), kBuilding.getUnitCombatFreeExperience(iI)));
		}
	}

	for (iI = 0; iI < NUM_DOMAIN_TYPES; ++iI)
	{
		if (kBuilding.getDomainFreeExperience(iI) != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_FREE_XP", GC.getDomainInfo((DomainTypes)iI).getTextKeyWide(), kBuilding.getDomainFreeExperience(iI)));
		}
	}

	for (iI = 0; iI < NUM_DOMAIN_TYPES; ++iI)
	{
		if (kBuilding.getDomainProductionModifier(iI) != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_BUILDS_FASTER_DOMAIN", GC.getDomainInfo((DomainTypes)iI).getTextKeyWide(), kBuilding.getDomainProductionModifier(iI)));
		}
	}

	bFirst = true;

//FfH: Modified by Kael 11/02/2006
//	for (iI = 0; iI < GC.getNumUnitInfos(); ++iI)
//	{
//		if (GC.getUnitInfo((UnitTypes)iI).getPrereqBuilding() == eBuilding)
//		{
//			szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_BUILDING_REQUIRED_TO_TRAIN").c_str());
//			szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_UNIT_TEXT"), GC.getUnitInfo((UnitTypes)iI).getDescription());
//			setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", bFirst);
//			bFirst = false;
//		}
//	}
	// lfgr UI 10/2020: If some player is active, don't show units that require a different civilization
	UnitTypes eLoopUnit;
	for (iI = 0; iI < GC.getNumUnitClassInfos(); iI++)
	{
		if (GC.getGameINLINE().getActivePlayer() != NO_PLAYER)
		{
			eLoopUnit = (UnitTypes)GC.getCivilizationInfo(GC.getGameINLINE().getActiveCivilizationType()).getCivilizationUnits(iI);
			if( eLoopUnit != NO_UNIT ) {
				CivilizationTypes ePrereqCiv = (CivilizationTypes) GC.getUnitInfo( eLoopUnit ).getPrereqCiv();
				if( ePrereqCiv != NO_CIVILIZATION && ePrereqCiv != GC.getGameINLINE().getActiveCivilizationType() )
				{
					continue;
				}
			}
		}
		else
		{
			eLoopUnit = (UnitTypes)GC.getUnitClassInfo((UnitClassTypes)iI).getDefaultUnitIndex();
		}
		if (eLoopUnit != NO_UNIT)
		{
    		if (GC.getUnitInfo(eLoopUnit).getPrereqBuilding() == eBuilding || GC.getUnitInfo(eLoopUnit).getPrereqBuildingClass() == eBuildingClass)
            {
                szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_BUILDING_REQUIRED_TO_TRAIN").c_str());
                szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_UNIT_TEXT"), GC.getUnitInfo(eLoopUnit).getDescription());
                setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", bFirst);
                bFirst = false;
            }
		}
	}
//FfH: End Modify

	bFirst = true;

	for (iI = 0; iI < GC.getNumUnitInfos(); ++iI)
	{
		if (GC.getUnitInfo((UnitTypes)iI).getBuildings(eBuilding) || GC.getUnitInfo((UnitTypes)iI).getForceBuildings(eBuilding))
		{
			szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_UNIT_REQUIRED_TO_BUILD").c_str());
			szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_UNIT_TEXT"), GC.getUnitInfo((UnitTypes)iI).getDescription());
			setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", bFirst);
			bFirst = false;
		}
	}

	iLast = 0;

	for (iI = 0; iI < GC.getNumBuildingClassInfos(); ++iI)
	{
		if (kBuilding.getBuildingHappinessChanges(iI) != 0)
		{
			szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_BUILDING_HAPPINESS_CHANGE", kBuilding.getBuildingHappinessChanges(iI),
				((kBuilding.getBuildingHappinessChanges(iI) > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR))).c_str());
			CvWString szBuilding;
			if (NO_PLAYER != ePlayer)
			{
				BuildingTypes ePlayerBuilding = ((BuildingTypes)(GC.getCivilizationInfo(GET_PLAYER(ePlayer).getCivilizationType()).getCivilizationBuildings(iI)));
				if (NO_BUILDING != ePlayerBuilding)
				{
					szBuilding.Format(L"<link=literal>%s</link>", GC.getBuildingClassInfo((BuildingClassTypes)iI).getDescription());
				}
			}
			else
			{
				szBuilding.Format(L"<link=literal>%s</link>", GC.getBuildingClassInfo((BuildingClassTypes)iI).getDescription());
			}
			setListHelp(szBuffer, szTempBuffer, szBuilding, L", ", (kBuilding.getBuildingHappinessChanges(iI) != iLast));
			iLast = kBuilding.getBuildingHappinessChanges(iI);
		}
	}

	if (kBuilding.getPowerBonus() != NO_BONUS)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_PROVIDES_POWER_WITH", GC.getBonusInfo((BonusTypes)kBuilding.getPowerBonus()).getTextKeyWide()));

		if (kBuilding.isDirtyPower() && (GC.getDefineINT("DIRTY_POWER_HEALTH_CHANGE") != 0))
		{
			szTempBuffer.Format(L" (+%d%c)", abs(GC.getDefineINT("DIRTY_POWER_HEALTH_CHANGE")), ((GC.getDefineINT("DIRTY_POWER_HEALTH_CHANGE") > 0) ? gDLL->getSymbolID(HEALTHY_CHAR): gDLL->getSymbolID(UNHEALTHY_CHAR)));
			szBuffer.append(szTempBuffer);
		}
	}

	bFirst = true;

	for (iI = 0; iI < GC.getNumBuildingClassInfos(); ++iI)
	{
		if (ePlayer != NO_PLAYER)
		{
			eLoopBuilding = ((BuildingTypes)(GC.getCivilizationInfo(GET_PLAYER(ePlayer).getCivilizationType()).getCivilizationBuildings(iI)));
		}
		else
		{
			eLoopBuilding = (BuildingTypes)GC.getBuildingClassInfo((BuildingClassTypes)iI).getDefaultBuildingIndex();
		}

		if (eLoopBuilding != NO_BUILDING)
		{
			if (GC.getBuildingInfo(eLoopBuilding).isBuildingClassNeededInCity(kBuilding.getBuildingClassType()))
			{
				if ((pCity == NULL) || pCity->canConstruct(eLoopBuilding, false, true))
				{
					szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_BUILDING_REQUIRED_TO_BUILD").c_str());
					szTempBuffer.Format(SETCOLR L"<link=literal>%s</link>" ENDCOLR, TEXT_COLOR("COLOR_BUILDING_TEXT"), GC.getBuildingInfo(eLoopBuilding).getDescription());
					setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", bFirst);
					bFirst = false;
				}
			}
		}
	}

	for (iI = 0; iI < GC.getNumSpellInfos(); ++iI)
	{
		if (GC.getSpellInfo((SpellTypes)iI).getBuildingPrereq() != NO_BUILDING)
		{
			if (GC.getSpellInfo((SpellTypes)iI).getBuildingPrereq() == eBuilding)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_ALLOWS_SPELL", GC.getSpellInfo((SpellTypes)iI).getDescription()));
			}
		}
	}

	if (bCivilopediaText)
	{
		// Trait
		for (int i = 0; i < GC.getNumTraitInfos(); ++i)
		{
			if (kBuilding.getProductionTraits((TraitTypes)i) != 0)
			{
				if (kBuilding.getProductionTraits((TraitTypes)i) == 100)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_DOUBLE_SPEED_TRAIT", GC.getTraitInfo((TraitTypes)i).getTextKeyWide()));
				}
				else
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_PRODUCTION_MODIFIER_TRAIT", kBuilding.getProductionTraits((TraitTypes)i), GC.getTraitInfo((TraitTypes)i).getTextKeyWide()));
				}
			}
		}

		for (int i = 0; i < GC.getNumTraitInfos(); ++i)
		{
			if (kBuilding.getHappinessTraits((TraitTypes)i) != 0)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_HAPPINESS_TRAIT", kBuilding.getHappinessTraits((TraitTypes)i), GC.getTraitInfo((TraitTypes)i).getTextKeyWide()));
			}
		}
	}

	if (bCivilopediaText)
	{
		if (kBuilding.getGreatPeopleUnitClass() != NO_UNITCLASS)
		{
			if (ePlayer != NO_PLAYER)
			{
				eGreatPeopleUnit = ((UnitTypes)(GC.getCivilizationInfo(GET_PLAYER(ePlayer).getCivilizationType()).getCivilizationUnits(kBuilding.getGreatPeopleUnitClass())));
			}
			else
			{
				eGreatPeopleUnit = (UnitTypes)GC.getUnitClassInfo((UnitClassTypes)kBuilding.getGreatPeopleUnitClass()).getDefaultUnitIndex();
			}

			if (eGreatPeopleUnit!= NO_UNIT)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_LIKELY_TO_GENERATE", GC.getUnitInfo(eGreatPeopleUnit).getTextKeyWide()));
			}
		}

		if (kBuilding.getFreeStartEra() != NO_ERA)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_FREE_START_ERA", GC.getEraInfo((EraTypes)kBuilding.getFreeStartEra()).getTextKeyWide()));
		}
	}

	if (!CvWString(kBuilding.getHelp()).empty())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(kBuilding.getHelp());
	}

	buildBuildingRequiresString(szBuffer, eBuilding, bCivilopediaText, bTechChooserText, pCity);

	if (pCity != NULL)
	{
// BUG - Building Double Commerce - start
		if (GC.getGameINLINE().getActivePlayer() != NO_PLAYER && pCity->getNumRealBuilding(eBuilding) > 0 && pCity->getBuildingOriginalOwner(eBuilding) == GC.getGameINLINE().getActivePlayer())
		{
			if (getBugOptionBOOL("CityScreen__BuildingDoubleCommerce", true, "BUG_BUILDING_DOUBLE_COMMERCE"))
			{
				int iYear = pCity->getBuildingOriginalTime(eBuilding);

				if (iYear != MIN_INT)
				{
					// year built
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_BUG_YEAR_BUILT", iYear));

					// double commerce
					if (pCity->getOwnerINLINE() == GC.getGameINLINE().getActivePlayer())
					{
						for (iI = 0; iI < NUM_COMMERCE_TYPES; iI++)
						{
							// Fix - display times as calculated by the Fix CommerceChangeDoubleTime addon by Sephi
							int iDoubleTime = kBuilding.getCommerceChangeDoubleTime(iI) * GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getConstructPercent();
							iDoubleTime /= 100;
							// Fix - End

							int iAge = GC.getGameINLINE().getGameTurnYear() - iYear;
							
							if (iAge < iDoubleTime)
							{
								szBuffer.append(NEWLINE);
								if (iAge - iDoubleTime == 1)
								{
									szBuffer.append(gDLL->getText("TXT_KEY_BUG_DOUBLE_COMMERCE_NEXT_YEAR", GC.getCommerceInfo((CommerceTypes)iI).getTextKeyWide()));
								}
								else
								{
									szBuffer.append(gDLL->getText("TXT_KEY_BUG_DOUBLE_COMMERCE_YEARS", GC.getCommerceInfo((CommerceTypes)iI).getTextKeyWide(), iDoubleTime - iAge));
								}
							}
						}
					}
				}
			}
		}
// BUG - Building Double Commerce - end

		if (!(GC.getBuildingClassInfo((BuildingClassTypes)(kBuilding.getBuildingClassType())).isNoLimit()))
		{
			if (isWorldWonderClass((BuildingClassTypes)(kBuilding.getBuildingClassType())))
			{
				if (pCity->isWorldWondersMaxed())
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_WORLD_WONDERS_PER_CITY", GC.getDefineINT("MAX_WORLD_WONDERS_PER_CITY")));
				}
			}
			else if (isTeamWonderClass((BuildingClassTypes)(kBuilding.getBuildingClassType())))
			{
				if (pCity->isTeamWondersMaxed())
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_TEAM_WONDERS_PER_CITY", GC.getDefineINT("MAX_TEAM_WONDERS_PER_CITY")));
				}
			}
			else if (isNationalWonderClass((BuildingClassTypes)(kBuilding.getBuildingClassType())))
			{
				if (pCity->isNationalWondersMaxed())
				{
					int iMaxNumWonders = (GC.getGameINLINE().isOption(GAMEOPTION_ONE_CITY_CHALLENGE) && GET_PLAYER(pCity->getOwnerINLINE()).isHuman()) ? GC.getDefineINT("MAX_NATIONAL_WONDERS_PER_CITY_FOR_OCC") : GC.getDefineINT("MAX_NATIONAL_WONDERS_PER_CITY");
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_NATIONAL_WONDERS_PER_CITY", iMaxNumWonders));
				}
			}
			else
			{
				if (pCity->isBuildingsMaxed())
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_NUM_PER_CITY", GC.getDefineINT("MAX_BUILDINGS_PER_CITY")));
				}
			}
		}
	}

	if ((pCity == NULL) || pCity->getNumRealBuilding(eBuilding) < GC.getCITY_MAX_NUM_BUILDINGS())
	{
		if (!bCivilopediaText)
		{
			if (pCity == NULL)
			{
				if (kBuilding.getProductionCost() > 0)
				{
					szTempBuffer.Format(L"\n%d%c", (ePlayer != NO_PLAYER ? GET_PLAYER(ePlayer).getProductionNeeded(eBuilding) : kBuilding.getProductionCost()), GC.getYieldInfo(YIELD_PRODUCTION).getChar());
					szBuffer.append(szTempBuffer);
				}
			}
			else
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_NUM_TURNS", pCity->getProductionTurnsLeft(eBuilding, ((gDLL->ctrlKey() || !(gDLL->shiftKey())) ? 0 : pCity->getOrderQueueLength()))));

				iProduction = pCity->getBuildingProduction(eBuilding);

				int iProductionNeeded = pCity->getProductionNeeded(eBuilding);
				if (iProduction > 0)
				{
					szTempBuffer.Format(L" - %d/%d%c", iProduction, iProductionNeeded, GC.getYieldInfo(YIELD_PRODUCTION).getChar());
					szBuffer.append(szTempBuffer);
				}
				else
				{
					szTempBuffer.Format(L" - %d%c", iProductionNeeded, GC.getYieldInfo(YIELD_PRODUCTION).getChar());
					szBuffer.append(szTempBuffer);
				}
// BUG - Production Decay - start
				if (getBugOptionBOOL("CityScreen__ProductionDecayHover", true, "BUG_PRODUCTION_DECAY_HOVER"))
				{
					// lfgr 09/2019: Tweaked with DisableProduction (Stasis) effects.
					setProductionDecayHelp(szBuffer, pCity->getBuildingProductionDecayTurns(eBuilding),
						getBugOptionINT("CityScreen__ProductionDecayHoverBuildingThreshold", 5, "BUG_PRODUCTION_DECAY_HOVER_BUILDING_THRESHOLD"),
						pCity->getBuildingProductionDecay(eBuilding), pCity->getProductionBuilding() == eBuilding,
							GET_PLAYER(ePlayer).getDisableProduction() != 0);
				}
// BUG - Production Decay - end
			}
		}

		for (int iI = 0; iI < GC.getNumBonusInfos(); ++iI)
		{
			if (kBuilding.getBonusProductionModifier(iI) != 0)
			{
				if (pCity != NULL)
				{
					if (pCity->hasBonus((BonusTypes)iI))
					{
						szBuffer.append(gDLL->getText("TXT_KEY_COLOR_POSITIVE"));
					}
					else
					{
						szBuffer.append(gDLL->getText("TXT_KEY_COLOR_NEGATIVE"));
					}
				}
				if (!bCivilopediaText)
				{
					szBuffer.append(L" (");
				}
				else
				{
					szTempBuffer.Format(L"\n%c", gDLL->getSymbolID(BULLET_CHAR), szTempBuffer);
					szBuffer.append(szTempBuffer);
				}
				if (kBuilding.getBonusProductionModifier(iI) == 100)
				{
					szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_DOUBLE_SPEED_WITH", GC.getBonusInfo((BonusTypes)iI).getTextKeyWide()));
				}
				else
				{
					szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_BUILDS_FASTER_WITH", kBuilding.getBonusProductionModifier(iI), GC.getBonusInfo((BonusTypes)iI).getTextKeyWide()));
				}
				if (!bCivilopediaText)
				{
					szBuffer.append(L')');
				}
				if (pCity != NULL)
				{
					szBuffer.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
				}
			}
		}

		if (kBuilding.getObsoleteTech() != NO_TECH)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_OBSOLETE_WITH", GC.getTechInfo((TechTypes) kBuilding.getObsoleteTech()).getTextKeyWide()));

			if (kBuilding.getDefenseModifier() != 0 || kBuilding.getBombardDefenseModifier() != 0)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_OBSOLETE_EXCEPT"));
			}
		}

		if (kBuilding.getSpecialBuildingType() != NO_SPECIALBUILDING)
		{
			if (GC.getSpecialBuildingInfo((SpecialBuildingTypes) kBuilding.getSpecialBuildingType()).getObsoleteTech() != NO_TECH)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_OBSOLETE_WITH", GC.getTechInfo((TechTypes) GC.getSpecialBuildingInfo((SpecialBuildingTypes) kBuilding.getSpecialBuildingType()).getObsoleteTech()).getTextKeyWide()));
			}
		}

		if ((gDLL->getChtLvl() > 0) && gDLL->ctrlKey() && (pCity != NULL))
		{
			int iBuildingValue = pCity->AI_buildingValue(eBuilding);
			szBuffer.append(CvWString::format(L"\nAI Building Value = %d", iBuildingValue));
		}
	}

	if (bStrategyText)
	{
		if (!CvWString(kBuilding.getStrategy()).empty())
		{
			if ((ePlayer == NO_PLAYER) || GET_PLAYER(ePlayer).isOption(PLAYEROPTION_ADVISOR_HELP))
			{
				szBuffer.append(SEPARATOR);
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_SIDS_TIPS"));
				szBuffer.append(L'\"');
				szBuffer.append(kBuilding.getStrategy());
				szBuffer.append(L'\"');
			}
		}
	}

	if (bCivilopediaText)
	{
		if (eDefaultBuilding == eBuilding)
		{
			for (iI = 0; iI < GC.getNumBuildingInfos(); ++iI)
			{
				if (iI != eBuilding)
				{
					if (eBuildingClass == GC.getBuildingInfo((BuildingTypes)iI).getBuildingClassType())
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_REPLACED_BY_BUILDING", GC.getBuildingInfo((BuildingTypes)iI).getTextKeyWide()));
					}
				}
			}
		}
	}

}

void CvGameTextMgr::buildBuildingRequiresString(CvWStringBuffer& szBuffer, BuildingTypes eBuilding, bool bCivilopediaText, bool bTechChooserText, const CvCity* pCity)
{
	bool bFirst;
	PlayerTypes ePlayer;
	CvWString szTempBuffer;
	CvWString szFirstBuffer;
	CvBuildingInfo& kBuilding = GC.getBuildingInfo(eBuilding);
	BuildingTypes eLoopBuilding;

	if (pCity != NULL)
	{
		ePlayer = pCity->getOwnerINLINE();
	}
	else
	{
		ePlayer = GC.getGameINLINE().getActivePlayer();
	}

	if (NULL == pCity || !pCity->canConstruct(eBuilding))
	{
		if (kBuilding.getHolyCity() != NO_RELIGION)
		{
			if (pCity == NULL || !pCity->isHolyCity((ReligionTypes)(kBuilding.getHolyCity())))
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_ACTION_ONLY_HOLY_CONSTRUCT", GC.getReligionInfo((ReligionTypes) kBuilding.getHolyCity()).getChar()));
			}
		}

		bFirst = true;

		if (kBuilding.getSpecialBuildingType() != NO_SPECIALBUILDING)
		{
			if ((pCity == NULL) || !(GC.getGameINLINE().isSpecialBuildingValid((SpecialBuildingTypes)(kBuilding.getSpecialBuildingType()))))
			{
				for (int iI = 0; iI < GC.getNumProjectInfos(); ++iI)
				{
					if (GC.getProjectInfo((ProjectTypes)iI).getEveryoneSpecialBuilding() == kBuilding.getSpecialBuildingType())
					{
						szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_REQUIRES").c_str());
						CvWString szProject;
						szProject.Format(L"<link=literal>%s</link>", GC.getProjectInfo((ProjectTypes)iI).getDescription());
						setListHelp(szBuffer, szTempBuffer, szProject, gDLL->getText("TXT_KEY_OR").c_str(), bFirst);
						bFirst = false;
					}
				}
			}
		}

		if (!bFirst)
		{
			szBuffer.append(ENDCOLR);
		}

		if (kBuilding.getSpecialBuildingType() != NO_SPECIALBUILDING)
		{
			if ((pCity == NULL) || !(GC.getGameINLINE().isSpecialBuildingValid((SpecialBuildingTypes)(kBuilding.getSpecialBuildingType()))))
			{
				TechTypes eTech = (TechTypes)GC.getSpecialBuildingInfo((SpecialBuildingTypes)kBuilding.getSpecialBuildingType()).getTechPrereqAnyone();
				if (NO_TECH != eTech)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_REQUIRES_TECH_ANYONE", GC.getTechInfo(eTech).getTextKeyWide()));
				}
			}
		}

		for (int iI = 0; iI < GC.getNumBuildingClassInfos(); ++iI)
		{
/*************************************************************************************************/
/* UNOFFICIAL_PATCH                       06/10/10                           EmperorFool         */
/*                                                                                               */
/* Bugfix                                                                                        */
/*************************************************************************************************/
			// EF: show "Requires Hospital" if "Requires Hospital (x/5)" requirement has been met
			bool bShowedPrereq = false;
			if (ePlayer == NO_PLAYER && kBuilding.getPrereqNumOfBuildingClass((BuildingClassTypes)iI) > 0)
			{
				eLoopBuilding = (BuildingTypes)GC.getBuildingClassInfo((BuildingClassTypes)iI).getDefaultBuildingIndex();
				szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_BUILDING_REQUIRES_NUM_SPECIAL_BUILDINGS_NO_CITY", GC.getBuildingInfo(eLoopBuilding).getTextKeyWide(), kBuilding.getPrereqNumOfBuildingClass((BuildingClassTypes)iI)).c_str());

				szBuffer.append(szTempBuffer);
				bShowedPrereq = true;
			}
			else if (ePlayer != NO_PLAYER && GET_PLAYER(ePlayer).getBuildingClassPrereqBuilding(eBuilding, ((BuildingClassTypes)iI)) > 0)
			{
				if ((pCity == NULL) || (GET_PLAYER(ePlayer).getBuildingClassCount((BuildingClassTypes)iI) < GET_PLAYER(ePlayer).getBuildingClassPrereqBuilding(eBuilding, ((BuildingClassTypes)iI))))
				{
					eLoopBuilding = ((BuildingTypes)(GC.getCivilizationInfo(GET_PLAYER(ePlayer).getCivilizationType()).getCivilizationBuildings(iI)));

					if (eLoopBuilding != NO_BUILDING)
					{
						if (pCity != NULL)
						{
							szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_BUILDING_REQUIRES_NUM_SPECIAL_BUILDINGS", GC.getBuildingInfo(eLoopBuilding).getTextKeyWide(), GET_PLAYER(ePlayer).getBuildingClassCount((BuildingClassTypes)iI), GET_PLAYER(ePlayer).getBuildingClassPrereqBuilding(eBuilding, ((BuildingClassTypes)iI))).c_str());
						}
						else
						{
							szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_BUILDING_REQUIRES_NUM_SPECIAL_BUILDINGS_NO_CITY", GC.getBuildingInfo(eLoopBuilding).getTextKeyWide(), GET_PLAYER(ePlayer).getBuildingClassPrereqBuilding(eBuilding, ((BuildingClassTypes)iI))).c_str());
						}

						szBuffer.append(szTempBuffer);
						bShowedPrereq = true;
					}
				}
			}
			
			if (!bShowedPrereq && kBuilding.isBuildingClassNeededInCity(iI))
			{
				if (NO_PLAYER != ePlayer)
				{
					eLoopBuilding = ((BuildingTypes)(GC.getCivilizationInfo(GET_PLAYER(ePlayer).getCivilizationType()).getCivilizationBuildings(iI)));
				}
				else
				{
					eLoopBuilding = (BuildingTypes)GC.getBuildingClassInfo((BuildingClassTypes)iI).getDefaultBuildingIndex();
				}

				if (eLoopBuilding != NO_BUILDING)
				{
					if ((pCity == NULL) || (pCity->getNumBuilding(eLoopBuilding) <= 0))
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_REQUIRES_STRING", GC.getBuildingInfo(eLoopBuilding).getTextKeyWide()));
					}
				}
			}
/*************************************************************************************************/
/* UNOFFICIAL_PATCH                         END                                                  */
/*************************************************************************************************/
		}

		if (kBuilding.isStateReligion())
		{
			if (NULL == pCity || NO_PLAYER == ePlayer || NO_RELIGION == GET_PLAYER(ePlayer).getStateReligion() || !pCity->isHasReligion(GET_PLAYER(ePlayer).getStateReligion()))
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_REQUIRES_STATE_RELIGION"));
			}
		}

		if (kBuilding.getNumCitiesPrereq() > 0)
		{
			if (NO_PLAYER == ePlayer || GET_PLAYER(ePlayer).getNumCities() < kBuilding.getNumCitiesPrereq())
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_REQUIRES_NUM_CITIES", kBuilding.getNumCitiesPrereq()));
			}
		}

		if (kBuilding.getUnitLevelPrereq() > 0)
		{
			if (NO_PLAYER == ePlayer || GET_PLAYER(ePlayer).getHighestUnitLevel() < kBuilding.getUnitLevelPrereq())
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_REQUIRES_UNIT_LEVEL", kBuilding.getUnitLevelPrereq()));
			}
		}

		if (kBuilding.getMinLatitude() > 0)
		{
			if (NULL == pCity || pCity->plot()->getLatitude() < kBuilding.getMinLatitude())
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_MIN_LATITUDE", kBuilding.getMinLatitude()));
			}
		}

		if (kBuilding.getMaxLatitude() < 90)
		{
			if (NULL == pCity || pCity->plot()->getLatitude() > kBuilding.getMaxLatitude())
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_MAX_LATITUDE", kBuilding.getMaxLatitude()));
			}
		}

		if (pCity != NULL)
		{
			if (GC.getGameINLINE().isNoNukes())
			{
				if (kBuilding.isAllowsNukes())
				{
					for (int iI = 0; iI < GC.getNumUnitInfos(); ++iI)
					{
						if (GC.getUnitInfo((UnitTypes)iI).getNukeRange() != -1)
						{
							szBuffer.append(NEWLINE);
							szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_NO_NUKES"));
							break;
						}
					}
				}
			}
		}

		if (bCivilopediaText)
		{
			if (kBuilding.getVictoryPrereq() != NO_VICTORY)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_REQUIRES_VICTORY", GC.getVictoryInfo((VictoryTypes)(kBuilding.getVictoryPrereq())).getTextKeyWide()));
			}

			if (kBuilding.getMaxStartEra() != NO_ERA)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_MAX_START_ERA", GC.getEraInfo((EraTypes)kBuilding.getMaxStartEra()).getTextKeyWide()));
			}

			if (kBuilding.getNumTeamsPrereq() > 0)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_REQUIRES_NUM_TEAMS", kBuilding.getNumTeamsPrereq()));
			}
		}
		else
		{
			if (!bTechChooserText)
			{
				if (kBuilding.getPrereqAndTech() != NO_TECH)
				{
					if (ePlayer == NO_PLAYER || !(GET_TEAM(GET_PLAYER(ePlayer).getTeam()).isHasTech((TechTypes)(kBuilding.getPrereqAndTech()))))
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_REQUIRES_STRING", GC.getTechInfo((TechTypes)(kBuilding.getPrereqAndTech())).getTextKeyWide()));
					}
				}
			}

			bFirst = true;

			for (int iI = 0; iI < GC.getNUM_BUILDING_AND_TECH_PREREQS(); ++iI)
			{
				if (kBuilding.getPrereqAndTechs(iI) != NO_TECH)
				{
					if (bTechChooserText || ePlayer == NO_PLAYER || !(GET_TEAM(GET_PLAYER(ePlayer).getTeam()).isHasTech((TechTypes)(kBuilding.getPrereqAndTechs(iI)))))
					{
						szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_REQUIRES").c_str());
						setListHelp(szBuffer, szTempBuffer, GC.getTechInfo(((TechTypes)(kBuilding.getPrereqAndTechs(iI)))).getDescription(), gDLL->getText("TXT_KEY_AND").c_str(), bFirst);
						bFirst = false;
					}
				}
			}

			if (!bFirst)
			{
				szBuffer.append(ENDCOLR);
			}

			if (kBuilding.getPrereqAndBonus() != NO_BONUS)
			{
				if ((pCity == NULL) || !(pCity->hasBonus((BonusTypes)kBuilding.getPrereqAndBonus())))
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_UNIT_REQUIRES_STRING", GC.getBonusInfo((BonusTypes)kBuilding.getPrereqAndBonus()).getTextKeyWide()));
				}
			}

			CvWStringBuffer szBonusList;
			bFirst = true;

			for (int iI = 0; iI < GC.getNUM_BUILDING_PREREQ_OR_BONUSES(); ++iI)
			{
				if (kBuilding.getPrereqOrBonuses(iI) != NO_BONUS)
				{
					if ((pCity == NULL) || !(pCity->hasBonus((BonusTypes)kBuilding.getPrereqOrBonuses(iI))))
					{
						szTempBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_REQUIRES").c_str());

//FfH: Modified by Kael 07/28/2008
//						setListHelp(szBonusList, szTempBuffer, GC.getBonusInfo((BonusTypes)kBuilding.getPrereqOrBonuses(iI)).getDescription(), gDLL->getText("TXT_KEY_OR").c_str(), bFirst);
//						bFirst = false;
//					}
//					else if (NULL != pCity)
//					{
//						bFirst = true;
//						break;
//					}
						setListHelp(szBonusList, szTempBuffer, GC.getBonusInfo((BonusTypes)kBuilding.getPrereqOrBonuses(iI)).getDescription(), gDLL->getText("TXT_KEY_AND").c_str(), bFirst);
						bFirst = false;
					}
//FfH: End Modify

				}
			}

//FfH: Added by Kael 08/04/2007
			if (kBuilding.getPrereqTrait() != NO_TRAIT)
			{
                if (NO_PLAYER == ePlayer || !GET_PLAYER(ePlayer).hasTrait((TraitTypes)kBuilding.getPrereqTrait()))
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_UNIT_REQUIRES_STRING", GC.getTraitInfo((TraitTypes)kBuilding.getPrereqTrait()).getTextKeyWide()));
				}
			}
//FfH: End Add

			if (!bFirst)
			{
				szBonusList.append(ENDCOLR);
				szBuffer.append(szBonusList);
			}

			if (NO_CORPORATION != kBuilding.getFoundsCorporation())
			{
				bFirst = true;
				szBonusList.clear();
				for (int iI = 0; iI < GC.getNUM_CORPORATION_PREREQ_BONUSES(); ++iI)
				{
					BonusTypes eBonus = (BonusTypes)GC.getCorporationInfo((CorporationTypes)kBuilding.getFoundsCorporation()).getPrereqBonus(iI);
					if (NO_BONUS != eBonus)
					{
						if ((pCity == NULL) || !(pCity->hasBonus(eBonus)))
						{
							szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_REQUIRES").c_str());
							szTempBuffer.Format(L"<link=literal>%s</link>", GC.getBonusInfo(eBonus).getDescription());
							setListHelp(szBonusList, szFirstBuffer, szTempBuffer, gDLL->getText("TXT_KEY_OR"), bFirst);
							bFirst = false;
						}
						else if (NULL != pCity)
						{
							bFirst = true;
							break;
						}
					}
				}

				if (!bFirst)
				{
					szBonusList.append(ENDCOLR);
					szBuffer.append(szBonusList);
				}
			}
		}
	}
}

// BUG - Production Decay - start
// lfgr 09/2019: Tweaked with DisableProduction (Stasis) effects.
void CvGameTextMgr::setProductionDecayHelp(CvWStringBuffer &szBuffer, int iTurnsLeft, int iThreshold, int iDecay,
		bool bProducing, bool bDisableProduction)
{
	if (iTurnsLeft <= 1)
	{
		if( bDisableProduction )
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_PRODUCTION_DECAY_PRODUCING_PRODUCTION_DISABLED", iDecay));
		}
		else if (bProducing)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_PRODUCTION_DECAY_PRODUCING", iDecay));
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_PRODUCTION_DECAY", iDecay));
		}
	}
	else if (iTurnsLeft <= iThreshold)
	{
		if( bDisableProduction )
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_PRODUCTION_DECAY_TURNS_PRODUCING_PRODUCTION_DISABLED", iDecay, iTurnsLeft));
		}
		else if (bProducing)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_PRODUCTION_DECAY_TURNS_PRODUCING", iDecay, iTurnsLeft));
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_PRODUCTION_DECAY_TURNS", iDecay, iTurnsLeft));
		}
	}
}
// BUG - Production Decay - end

void CvGameTextMgr::setProjectHelp(CvWStringBuffer &szBuffer, ProjectTypes eProject, bool bCivilopediaText, CvCity* pCity)
{
	PROFILE_FUNC();

	CvWString szTempBuffer;
	CvWString szFirstBuffer;
	PlayerTypes ePlayer;
	bool bFirst;
	int iProduction;
	int iI;

	if (NO_PROJECT == eProject)
	{
		return;
	}

	CvProjectInfo& kProject = GC.getProjectInfo(eProject);

	if (pCity != NULL)
	{
		ePlayer = pCity->getOwnerINLINE();
	}
	else
	{
		ePlayer = GC.getGameINLINE().getActivePlayer();
	}

	if (!bCivilopediaText)
	{
		szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_PROJECT_TEXT"), kProject.getDescription());
		szBuffer.append(szTempBuffer);

		if (isWorldProject(eProject))
		{
			if (pCity == NULL)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_WORLD_NUM_ALLOWED", kProject.getMaxGlobalInstances()));
			}
			else
			{
				szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_WORLD_NUM_LEFT", (kProject.getMaxGlobalInstances() - GC.getGameINLINE().getProjectCreatedCount(eProject) - GET_TEAM(GET_PLAYER(ePlayer).getTeam()).getProjectMaking(eProject))));
			}
		}

		if (isTeamProject(eProject))
		{
			if (pCity == NULL)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_TEAM_NUM_ALLOWED", kProject.getMaxTeamInstances()));
			}
			else
			{
                szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_TEAM_NUM_LEFT", (kProject.getMaxTeamInstances() - GET_TEAM(GET_PLAYER(ePlayer).getTeam()).getProjectCount(eProject) - GET_TEAM(GET_PLAYER(ePlayer).getTeam()).getProjectMaking(eProject))));
			}
		}
	}

	if (kProject.getNukeInterception() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_CHANCE_INTERCEPT_NUKES", kProject.getNukeInterception()));
	}

	if (kProject.getTechShare() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_TECH_SHARE", kProject.getTechShare()));
	}

	if (kProject.isAllowsNukes())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_ENABLES_NUKES"));
	}

	if (kProject.getEveryoneSpecialUnit() != NO_SPECIALUNIT)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_ENABLES_SPECIAL", GC.getSpecialUnitInfo((SpecialUnitTypes)(kProject.getEveryoneSpecialUnit())).getTextKeyWide()));
	}

	if (kProject.getEveryoneSpecialBuilding() != NO_SPECIALBUILDING)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_ENABLES_SPECIAL", GC.getSpecialBuildingInfo((SpecialBuildingTypes)(kProject.getEveryoneSpecialBuilding())).getTextKeyWide()));
	}

	for (iI = 0; iI < GC.getNumVictoryInfos(); ++iI)
	{
		if (kProject.getVictoryThreshold(iI) > 0)
		{
			if (kProject.getVictoryThreshold(iI) == kProject.getVictoryMinThreshold(iI))
			{
				szTempBuffer.Format(L"%d", kProject.getVictoryThreshold(iI));
			}
			else
			{
				szTempBuffer.Format(L"%d-%d", kProject.getVictoryMinThreshold(iI), kProject.getVictoryThreshold(iI));
			}

			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_REQUIRED_FOR_VICTORY", szTempBuffer.GetCString(), GC.getVictoryInfo((VictoryTypes)iI).getTextKeyWide()));
		}
	}

	bFirst = true;

	for (iI = 0; iI < GC.getNumProjectInfos(); ++iI)
	{
		if (GC.getProjectInfo((ProjectTypes)iI).getAnyoneProjectPrereq() == eProject)
		{
			szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_PROJECT_REQUIRED_TO_CREATE_ANYONE").c_str());
			szTempBuffer.Format(SETCOLR L"<link=literal>%s</link>" ENDCOLR, TEXT_COLOR("COLOR_PROJECT_TEXT"), GC.getProjectInfo((ProjectTypes)iI).getDescription());
			setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", bFirst);
			bFirst = false;
		}
	}

	bFirst = true;

	for (iI = 0; iI < GC.getNumProjectInfos(); ++iI)
	{
		if (GC.getProjectInfo((ProjectTypes)iI).getProjectsNeeded(eProject) > 0)
		{
			if ((pCity == NULL) || pCity->canCreate(((ProjectTypes)iI), false, true))
			{
				szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_PROJECT_REQUIRED_TO_CREATE").c_str());
				szTempBuffer.Format(SETCOLR L"<link=literal>%s</link>" ENDCOLR, TEXT_COLOR("COLOR_PROJECT_TEXT"), GC.getProjectInfo((ProjectTypes)iI).getDescription());
				setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", bFirst);
				bFirst = false;
			}
		}
	}

//FfH: Added by Kael 08/26/2008
    if (kProject.getModifyGlobalCounter() != 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_MESSAGE_MODIFY_GLOBAL_COUNTER", kProject.getModifyGlobalCounter()));
    }
    if (kProject.getPrereqCivilization() != NO_CIVILIZATION)
    {
        if (pCity == NULL || pCity->getCivilizationType() != kProject.getPrereqCivilization())
        {
            szBuffer.append(NEWLINE);
            szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_PREREQ_CIVILIZATION", GC.getCivilizationInfo((CivilizationTypes)kProject.getPrereqCivilization()).getDescription()));
        }
    }
    if (kProject.getPrereqGlobalCounter() != 0)
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_UNIT_PREREQ_GLOBAL_COUNTER", kProject.getPrereqGlobalCounter()));
    }
//FfH: End Add

	if ((pCity == NULL) || !(pCity->canCreate(eProject)))
	{
		if (pCity != NULL)
		{
			if (GC.getGameINLINE().isNoNukes())
			{
				if (kProject.isAllowsNukes())
				{
					for (iI = 0; iI < GC.getNumUnitInfos(); ++iI)
					{
						if (GC.getUnitInfo((UnitTypes)iI).getNukeRange() != -1)
						{
							szBuffer.append(NEWLINE);
							szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_NO_NUKES"));
							break;
						}
					}
				}
			}
		}

		if (kProject.getAnyoneProjectPrereq() != NO_PROJECT)
		{
			if ((pCity == NULL) || (GC.getGameINLINE().getProjectCreatedCount((ProjectTypes)(kProject.getAnyoneProjectPrereq())) == 0))
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_REQUIRES_ANYONE", GC.getProjectInfo((ProjectTypes)kProject.getAnyoneProjectPrereq()).getTextKeyWide()));
			}
		}

		for (iI = 0; iI < GC.getNumProjectInfos(); ++iI)
		{
			if (kProject.getProjectsNeeded(iI) > 0)
			{
				if ((pCity == NULL) || (GET_TEAM(GET_PLAYER(ePlayer).getTeam()).getProjectCount((ProjectTypes)iI) < kProject.getProjectsNeeded(iI)))
				{
					if (pCity != NULL)
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_REQUIRES", GC.getProjectInfo((ProjectTypes)iI).getTextKeyWide(), GET_TEAM(GET_PLAYER(ePlayer).getTeam()).getProjectCount((ProjectTypes)iI), kProject.getProjectsNeeded(iI)));
					}
					else
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_REQUIRES_NO_CITY", GC.getProjectInfo((ProjectTypes)iI).getTextKeyWide(), kProject.getProjectsNeeded(iI)));
					}
				}
			}
		}

		if (bCivilopediaText)
		{
			if (kProject.getVictoryPrereq() != NO_VICTORY)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_REQUIRES_STRING_VICTORY", GC.getVictoryInfo((VictoryTypes)(kProject.getVictoryPrereq())).getTextKeyWide()));
			}
		}
	}

	if (!bCivilopediaText)
	{
		if (pCity == NULL)
		{
			if (ePlayer != NO_PLAYER)
			{
				szTempBuffer.Format(L"\n%d%c", GET_PLAYER(ePlayer).getProductionNeeded(eProject), GC.getYieldInfo(YIELD_PRODUCTION).getChar());
			}
			else
			{
				szTempBuffer.Format(L"\n%d%c", kProject.getProductionCost(), GC.getYieldInfo(YIELD_PRODUCTION).getChar());
			}
			szBuffer.append(szTempBuffer);
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_NUM_TURNS", pCity->getProductionTurnsLeft(eProject, ((gDLL->ctrlKey() || !(gDLL->shiftKey())) ? 0 : pCity->getOrderQueueLength()))));

			iProduction = pCity->getProjectProduction(eProject);

			if (iProduction > 0)
			{
				szTempBuffer.Format(L" - %d/%d%c", iProduction, pCity->getProductionNeeded(eProject), GC.getYieldInfo(YIELD_PRODUCTION).getChar());
			}
			else
			{
				szTempBuffer.Format(L" - %d%c", pCity->getProductionNeeded(eProject), GC.getYieldInfo(YIELD_PRODUCTION).getChar());
			}
			szBuffer.append(szTempBuffer);
		}
	}

	for (iI = 0; iI < GC.getNumBonusInfos(); ++iI)
	{
		if (kProject.getBonusProductionModifier(iI) != 0)
		{
			if (pCity != NULL)
			{
				if (pCity->hasBonus((BonusTypes)iI))
				{
					szBuffer.append(gDLL->getText("TXT_KEY_COLOR_POSITIVE"));
				}
				else
				{
					szBuffer.append(gDLL->getText("TXT_KEY_COLOR_NEGATIVE"));
				}
			}
			if (!bCivilopediaText)
			{
				szBuffer.append(L" (");
			}
			else
			{
				szTempBuffer.Format(L"%s%c", NEWLINE, gDLL->getSymbolID(BULLET_CHAR), szTempBuffer);
				szBuffer.append(szTempBuffer);
			}
			if (kProject.getBonusProductionModifier(iI) == 100)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_DOUBLE_SPEED_WITH", GC.getBonusInfo((BonusTypes)iI).getTextKeyWide()));
			}
			else
			{
				szBuffer.append(gDLL->getText("TXT_KEY_PROJECT_BUILDS_FASTER_WITH", kProject.getBonusProductionModifier(iI), GC.getBonusInfo((BonusTypes)iI).getTextKeyWide()));
			}
			if (!bCivilopediaText)
			{
				szBuffer.append(L')');
			}
			if (pCity != NULL)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_COLOR_REVERT"));
			}
		}
	}

	// descriptive text for mouseovers
	if (!bCivilopediaText)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(kProject.getStrategy());
	}
}


void CvGameTextMgr::setProcessHelp(CvWStringBuffer &szBuffer, ProcessTypes eProcess)
{
	int iI;

	szBuffer.append(GC.getProcessInfo(eProcess).getDescription());

	for (iI = 0; iI < NUM_COMMERCE_TYPES; ++iI)
	{
		if (GC.getProcessInfo(eProcess).getProductionToCommerceModifier(iI) != 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_PROCESS_CONVERTS", GC.getProcessInfo(eProcess).getProductionToCommerceModifier(iI), GC.getYieldInfo(YIELD_PRODUCTION).getChar(), GC.getCommerceInfo((CommerceTypes) iI).getChar()));
		}
	}
}

void CvGameTextMgr::setBadHealthHelp(CvWStringBuffer &szBuffer, CvCity& city)
{
	CvPlot* pLoopPlot;
	FeatureTypes eFeature;
	int iHealth;
	int iI;

	if (city.badHealth() > 0)
	{
		iHealth = -(city.getFreshWaterBadHealth());
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_FROM_FRESH_WATER", iHealth));
			szBuffer.append(NEWLINE);
		}

		iHealth = -(city.getFeatureBadHealth());
		if (iHealth > 0)
		{
			eFeature = NO_FEATURE;

			//for (iI = 0; iI < NUM_CITY_PLOTS; ++iI)
			for (iI = 0; iI < city.getNumCityPlots(); ++iI)
			{
				pLoopPlot = plotCity(city.getX_INLINE(), city.getY_INLINE(), iI);

				if (pLoopPlot != NULL)
				{
					if (pLoopPlot->getFeatureType() != NO_FEATURE)
					{
						if (GC.getFeatureInfo(pLoopPlot->getFeatureType()).getHealthPercent() < 0)
						{
							if (eFeature == NO_FEATURE)
							{
								eFeature = pLoopPlot->getFeatureType();
							}
							else if (eFeature != pLoopPlot->getFeatureType())
							{
								eFeature = NO_FEATURE;
								break;
							}
						}
					}
				}
			}

			szBuffer.append(gDLL->getText("TXT_KEY_MISC_FEAT_HEALTH", iHealth, ((eFeature == NO_FEATURE) ? L"TXT_KEY_MISC_FEATURES" : GC.getFeatureInfo(eFeature).getTextKeyWide())));
			szBuffer.append(NEWLINE);
		}

/*************************************************************************************************/
/** Specialists Enhancements, by Supercheese 10/9/09                                                   */
/**                                                                                              */
/**                                                                                              */
/*************************************************************************************************/
		iHealth = -(city.getSpecialistBadHealth());
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_BAD_HEALTH_FROM_SPECIALISTS", iHealth));
			szBuffer.append(NEWLINE);
		}
/*************************************************************************************************/
/** Specialists Enhancements                          END                                              */
/*************************************************************************************************/
		iHealth = city.getEspionageHealthCounter();
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HEALTH_FROM_ESPIONAGE", iHealth));
			szBuffer.append(NEWLINE);
		}

		iHealth = -(city.getPowerBadHealth());
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HEALTH_FROM_POWER", iHealth));
			szBuffer.append(NEWLINE);
		}

		iHealth = -(city.getBonusBadHealth());
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HEALTH_FROM_BONUSES", iHealth));
			szBuffer.append(NEWLINE);
		}

		iHealth = -(city.totalBadBuildingHealth());
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HEALTH_FROM_BUILDINGS", iHealth));
			szBuffer.append(NEWLINE);
		}

		iHealth = -(GET_PLAYER(city.getOwnerINLINE()).getExtraHealth());
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HEALTH_FROM_CIV", iHealth));
			szBuffer.append(NEWLINE);
		}

		iHealth = -city.getExtraHealth();
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_UNHEALTH_EXTRA", iHealth));
			szBuffer.append(NEWLINE);
		}

		iHealth = -(GC.getHandicapInfo(city.getHandicapType()).getHealthBonus());
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HEALTH_FROM_HANDICAP", iHealth));
			szBuffer.append(NEWLINE);
		}

		iHealth = city.unhealthyPopulation();
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HEALTH_FROM_POP", iHealth));
			szBuffer.append(NEWLINE);
		}

		szBuffer.append(L"-----------------------\n");

		szBuffer.append(gDLL->getText("TXT_KEY_MISC_TOTAL_UNHEALTHY", city.badHealth()));
	}
}

void CvGameTextMgr::setGoodHealthHelp(CvWStringBuffer &szBuffer, CvCity& city)
{
	CvPlot* pLoopPlot;
	FeatureTypes eFeature;
	int iHealth;
	int iI;

	if (city.goodHealth() > 0)
	{
		iHealth = city.getFreshWaterGoodHealth();
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HEALTH_FROM_FRESH_WATER", iHealth));
			szBuffer.append(NEWLINE);
		}

		iHealth = city.getFeatureGoodHealth();
		if (iHealth > 0)
		{
			eFeature = NO_FEATURE;

			//for (iI = 0; iI < NUM_CITY_PLOTS; ++iI)
			for (iI = 0; iI < city.getNumCityPlots(); ++iI)
			{
				pLoopPlot = plotCity(city.getX_INLINE(), city.getY_INLINE(), iI);

				if (pLoopPlot != NULL)
				{
					if (pLoopPlot->getFeatureType() != NO_FEATURE)
					{
						if (GC.getFeatureInfo(pLoopPlot->getFeatureType()).getHealthPercent() > 0)
						{
							if (eFeature == NO_FEATURE)
							{
								eFeature = pLoopPlot->getFeatureType();
							}
							else if (eFeature != pLoopPlot->getFeatureType())
							{
								eFeature = NO_FEATURE;
								break;
							}
						}
					}
				}
			}

			szBuffer.append(gDLL->getText("TXT_KEY_MISC_FEAT_GOOD_HEALTH", iHealth, ((eFeature == NO_FEATURE) ? L"TXT_KEY_MISC_FEATURES" : GC.getFeatureInfo(eFeature).getTextKeyWide())));
			szBuffer.append(NEWLINE);
		}

/*************************************************************************************************/
/** Specialists Enhancements, by Supercheese 10/9/09                                                   */
/**                                                                                              */
/**                                                                                              */
/*************************************************************************************************/
		iHealth = city.getSpecialistGoodHealth();
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_GOOD_HEALTH_FROM_SPECIALISTS", iHealth));
			szBuffer.append(NEWLINE);
		}
/*************************************************************************************************/
/** Specialists Enhancements                          END                                              */
/*************************************************************************************************/
		iHealth = city.getPowerGoodHealth();
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_GOOD_HEALTH_FROM_POWER", iHealth));
			szBuffer.append(NEWLINE);
		}

		iHealth = city.getBonusGoodHealth();
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_GOOD_HEALTH_FROM_BONUSES", iHealth));
			szBuffer.append(NEWLINE);
		}

		iHealth = city.totalGoodBuildingHealth();
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_GOOD_HEALTH_FROM_BUILDINGS", iHealth));
			szBuffer.append(NEWLINE);
		}

		iHealth = GET_PLAYER(city.getOwnerINLINE()).getExtraHealth();
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_GOOD_HEALTH_FROM_CIV", iHealth));
			szBuffer.append(NEWLINE);
		}

		iHealth = city.getExtraHealth();
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HEALTH_EXTRA", iHealth));
			szBuffer.append(NEWLINE);
		}

		iHealth = GC.getHandicapInfo(city.getHandicapType()).getHealthBonus();
		if (iHealth > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_GOOD_HEALTH_FROM_HANDICAP", iHealth));
			szBuffer.append(NEWLINE);
		}

		szBuffer.append(L"-----------------------\n");

		szBuffer.append(gDLL->getText("TXT_KEY_MISC_TOTAL_HEALTHY", city.goodHealth()));
	}
}

// BUG - Building Additional Health - start
bool CvGameTextMgr::setBuildingAdditionalHealthHelp(CvWStringBuffer &szBuffer, const CvCity& city, const CvWString& szStart, bool bStarted)
{
	CvWString szLabel;
	CvCivilizationInfo& kCivilization = GC.getCivilizationInfo(GET_PLAYER(city.getOwnerINLINE()).getCivilizationType());

	for (int iI = 0; iI < GC.getNumBuildingClassInfos(); iI++)
	{
		BuildingTypes eBuilding = (BuildingTypes)kCivilization.getCivilizationBuildings((BuildingClassTypes)iI);

		if (eBuilding != NO_BUILDING && city.canConstruct(eBuilding, false, true, false))
		{
			int iGood = 0, iBad = 0;
			int iChange = city.getAdditionalHealthByBuilding(eBuilding, iGood, iBad);

			if (iGood != 0 || iBad != 0)
			{
				int iSpoiledFood = city.getAdditionalSpoiledFood(iGood, iBad);
				int iStarvation = city.getAdditionalStarvation(iSpoiledFood);

				if (!bStarted)
				{
					szBuffer.append(szStart);
					bStarted = true;
				}

				szLabel.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_BUILDING_TEXT"), GC.getBuildingInfo(eBuilding).getDescription());
				bool bStartedLine = setResumableGoodBadChangeHelp(szBuffer, szLabel, L": ", L"", iGood, gDLL->getSymbolID(HEALTHY_CHAR), iBad, gDLL->getSymbolID(UNHEALTHY_CHAR), false, true);
				setResumableValueChangeHelp(szBuffer, szLabel, L": ", L"", iSpoiledFood, gDLL->getSymbolID(EATEN_FOOD_CHAR), false, true, bStartedLine);
				setResumableValueChangeHelp(szBuffer, szLabel, L": ", L"", iStarvation, gDLL->getSymbolID(BAD_FOOD_CHAR), false, true, bStartedLine);
			}
		}
	}

	return bStarted;
}
// BUG - Building Additional Health - end

void CvGameTextMgr::setAngerHelp(CvWStringBuffer &szBuffer, CvCity& city)
{
	int iOldAngerPercent;
	int iNewAngerPercent;
	int iOldAnger;
	int iNewAnger;
	int iAnger;
	int iI;

	if (city.isOccupation())
	{
		szBuffer.append(gDLL->getText("TXT_KEY_ANGER_RESISTANCE"));
	}
	else if (GET_PLAYER(city.getOwnerINLINE()).isAnarchy())
	{
		szBuffer.append(gDLL->getText("TXT_KEY_ANGER_ANARCHY"));
	}
	else if (city.unhappyLevel() > 0)
	{
		iOldAngerPercent = 0;
		iNewAngerPercent = 0;

		iOldAnger = 0;
		iNewAnger = 0;

		// XXX decomp these???
		iNewAngerPercent += city.getOvercrowdingPercentAnger();
		iNewAnger += (((iNewAngerPercent * city.getPopulation()) / GC.getPERCENT_ANGER_DIVISOR()) - ((iOldAngerPercent * city.getPopulation()) / GC.getDefineINT("PERCENT_ANGER_DIVISOR")));
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_OVERCROWDING", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAngerPercent = iNewAngerPercent;
		iOldAnger = iNewAnger;

		iNewAngerPercent += city.getNoMilitaryPercentAnger();
		iNewAnger += (((iNewAngerPercent * city.getPopulation()) / GC.getPERCENT_ANGER_DIVISOR()) - ((iOldAngerPercent * city.getPopulation()) / GC.getDefineINT("PERCENT_ANGER_DIVISOR")));
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_MILITARY_PROTECTION", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAngerPercent = iNewAngerPercent;
		iOldAnger = iNewAnger;

		iNewAngerPercent += city.getCulturePercentAnger();
		iNewAnger += (((iNewAngerPercent * city.getPopulation()) / GC.getPERCENT_ANGER_DIVISOR()) - ((iOldAngerPercent * city.getPopulation()) / GC.getDefineINT("PERCENT_ANGER_DIVISOR")));
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_OCCUPIED", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAngerPercent = iNewAngerPercent;
		iOldAnger = iNewAnger;

		iNewAngerPercent += city.getReligionPercentAnger();
		iNewAnger += (((iNewAngerPercent * city.getPopulation()) / GC.getPERCENT_ANGER_DIVISOR()) - ((iOldAngerPercent * city.getPopulation()) / GC.getDefineINT("PERCENT_ANGER_DIVISOR")));
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_RELIGION_FIGHT", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAngerPercent = iNewAngerPercent;
		iOldAnger = iNewAnger;

		iNewAngerPercent += city.getHurryPercentAnger();
		iNewAnger += (((iNewAngerPercent * city.getPopulation()) / GC.getPERCENT_ANGER_DIVISOR()) - ((iOldAngerPercent * city.getPopulation()) / GC.getDefineINT("PERCENT_ANGER_DIVISOR")));
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_OPPRESSION", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAngerPercent = iNewAngerPercent;
		iOldAnger = iNewAnger;

/************************************************************************************************/
/* REVOLUTION_MOD                         04/26/08                                jdog5000      */
/*                                                                                              */
/*                                                                                              */
/************************************************************************************************/
		iNewAngerPercent += city.getRevRequestPercentAnger();
		iNewAnger += (((iNewAngerPercent * city.getPopulation()) / GC.getPERCENT_ANGER_DIVISOR()) - ((iOldAngerPercent * city.getPopulation()) / GC.getDefineINT("PERCENT_ANGER_DIVISOR")));
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_REV_REQUEST_ANGER", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAngerPercent = iNewAngerPercent;
		iOldAnger = iNewAnger;

		iNewAngerPercent += city.getRevIndexPercentAnger();
		iNewAnger += (((iNewAngerPercent * city.getPopulation()) / GC.getPERCENT_ANGER_DIVISOR()) - ((iOldAngerPercent * city.getPopulation()) / GC.getDefineINT("PERCENT_ANGER_DIVISOR")));
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_REV_INDEX_ANGER", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAngerPercent = iNewAngerPercent;
		iOldAnger = iNewAnger;
/************************************************************************************************/
/* REVOLUTION_MOD                          END                                                  */
/************************************************************************************************/
		iNewAngerPercent += city.getConscriptPercentAnger();
		iNewAnger += (((iNewAngerPercent * city.getPopulation()) / GC.getPERCENT_ANGER_DIVISOR()) - ((iOldAngerPercent * city.getPopulation()) / GC.getDefineINT("PERCENT_ANGER_DIVISOR")));
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_DRAFT", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAngerPercent = iNewAngerPercent;
		iOldAnger = iNewAnger;

		iNewAngerPercent += city.getDefyResolutionPercentAnger();
		iNewAnger += (((iNewAngerPercent * city.getPopulation()) / GC.getPERCENT_ANGER_DIVISOR()) - ((iOldAngerPercent * city.getPopulation()) / GC.getDefineINT("PERCENT_ANGER_DIVISOR")));
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_DEFY_RESOLUTION", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAngerPercent = iNewAngerPercent;
		iOldAnger = iNewAnger;

		iNewAngerPercent += city.getWarWearinessPercentAnger();
		iNewAnger += (((iNewAngerPercent * city.getPopulation()) / GC.getPERCENT_ANGER_DIVISOR()) - ((iOldAngerPercent * city.getPopulation()) / GC.getDefineINT("PERCENT_ANGER_DIVISOR")));
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_WAR_WEAR", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAngerPercent = iNewAngerPercent;
		iOldAnger = iNewAnger;

		iNewAnger += std::max(0, city.getVassalUnhappiness());
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_UNHAPPY_VASSAL", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAnger = iNewAnger;

		iNewAnger += std::max(0, city.getEspionageHappinessCounter());
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_ESPIONAGE", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAnger = iNewAnger;

		for (iI = 0; iI < GC.getNumCivicInfos(); ++iI)
		{
			iNewAngerPercent += GET_PLAYER(city.getOwnerINLINE()).getCivicPercentAnger((CivicTypes)iI);
			iNewAnger += (((iNewAngerPercent * city.getPopulation()) / GC.getPERCENT_ANGER_DIVISOR()) - ((iOldAngerPercent * city.getPopulation()) / GC.getDefineINT("PERCENT_ANGER_DIVISOR")));
			iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
			if (iAnger > 0)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_ANGER_DEMAND_CIVIC", iAnger, GC.getCivicInfo((CivicTypes) iI).getTextKeyWide()));
				szBuffer.append(NEWLINE);
			}
			iOldAngerPercent = iNewAngerPercent;
			iOldAnger = iNewAnger;
		}

		iNewAnger -= std::min(0, city.getLargestCityHappiness());
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_BIG_CITY", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAnger = iNewAnger;

		iNewAnger -= std::min(0, city.getMilitaryHappiness());
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_MILITARY_PRESENCE", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAnger = iNewAnger;

		iNewAnger -= std::min(0, city.getCurrentStateReligionHappiness());
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_STATE_RELIGION", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAnger = iNewAnger;

		iNewAnger -= std::min(0, (city.getBuildingBadHappiness() + city.getExtraBuildingBadHappiness()));
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_BUILDINGS", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAnger = iNewAnger;

		iNewAnger -= std::min(0, city.getFeatureBadHappiness());
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_FEATURES", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAnger = iNewAnger;

		iNewAnger -= std::min(0, city.getBonusBadHappiness());
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_BONUS", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAnger = iNewAnger;

/*************************************************************************************************/
/** Specialists Enhancements, by Supercheese 10/9/09                                                   */
/**                                                                                              */
/**                                                                                              */
/*************************************************************************************************/
		iNewAnger -= std::min(0, city.getSpecialistUnhappiness());
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_UNHAPPY_SPECIALISTS", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAnger = iNewAnger;
/*************************************************************************************************/
/** Specialists Enhancements                          END                                              */
/*************************************************************************************************/

		iNewAnger -= std::min(0, city.getReligionBadHappiness());
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_RELIGIOUS_FREEDOM", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAnger = iNewAnger;

		iNewAnger -= std::min(0, city.getCommerceHappiness());
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_BAD_ENTERTAINMENT", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAnger = iNewAnger;

		iNewAnger -= std::min(0, city.area()->getBuildingHappiness(city.getOwnerINLINE()));
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_BUILDINGS", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAnger = iNewAnger;

		iNewAnger -= std::min(0, GET_PLAYER(city.getOwnerINLINE()).getBuildingHappiness());
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_BUILDINGS", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAnger = iNewAnger;

		iNewAnger -= std::min(0, (city.getExtraHappiness() + GET_PLAYER(city.getOwnerINLINE()).getExtraHappiness()));
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_ARGH", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAnger = iNewAnger;

		iNewAnger -= std::min(0, GC.getHandicapInfo(city.getHandicapType()).getHappyBonus());
		iAnger = ((iNewAnger - iOldAnger) + std::min(0, iOldAnger));
		if (iAnger > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ANGER_HANDICAP", iAnger));
			szBuffer.append(NEWLINE);
		}
		iOldAnger = iNewAnger;

		szBuffer.append(L"-----------------------\n");

		szBuffer.append(gDLL->getText("TXT_KEY_ANGER_TOTAL_UNHAPPY", iOldAnger));

		FAssert(iOldAnger == city.unhappyLevel());
	}
}


void CvGameTextMgr::setHappyHelp(CvWStringBuffer &szBuffer, CvCity& city)
{
	int iHappy;
	int iTotalHappy = 0;

	if (city.isOccupation() || GET_PLAYER(city.getOwnerINLINE()).isAnarchy())
	{
		return;
	}
	if (city.happyLevel() > 0)
	{
/************************************************************************************************/
/* REVOLUTION_MOD                         04/28/08                                jdog5000      */
/*                                                                                              */
/*                                                                                              */
/************************************************************************************************/
		iHappy = city.getRevSuccessHappiness();
		if (iHappy > 0)
		{
			iTotalHappy += iHappy;
			szBuffer.append(gDLL->getText("TXT_KEY_REV_SUCCESS_HAPPINESS", iHappy));
			szBuffer.append(NEWLINE);
		}
/************************************************************************************************/
/* REVOLUTION_MOD                          END                                                  */
/************************************************************************************************/
		iHappy = city.getLargestCityHappiness();
		if (iHappy > 0)
		{
			iTotalHappy += iHappy;
			szBuffer.append(gDLL->getText("TXT_KEY_HAPPY_BIG_CITY", iHappy));
			szBuffer.append(NEWLINE);
		}

		iHappy = city.getMilitaryHappiness();
		if (iHappy > 0)
		{
			iTotalHappy += iHappy;
			szBuffer.append(gDLL->getText("TXT_KEY_HAPPY_MILITARY_PRESENCE", iHappy));
			szBuffer.append(NEWLINE);
		}

		iHappy = city.getVassalHappiness();
		if (iHappy > 0)
		{
			iTotalHappy += iHappy;
			szBuffer.append(gDLL->getText("TXT_KEY_HAPPY_VASSAL", iHappy));
			szBuffer.append(NEWLINE);
		}

		iHappy = city.getCurrentStateReligionHappiness();
		if (iHappy > 0)
		{
			iTotalHappy += iHappy;
			szBuffer.append(gDLL->getText("TXT_KEY_HAPPY_STATE_RELIGION", iHappy));
			szBuffer.append(NEWLINE);
		}

		iHappy = (city.getBuildingGoodHappiness() + city.getExtraBuildingGoodHappiness());
		if (iHappy > 0)
		{
			iTotalHappy += iHappy;
			szBuffer.append(gDLL->getText("TXT_KEY_HAPPY_BUILDINGS", iHappy));
			szBuffer.append(NEWLINE);
		}

		iHappy = city.getFeatureGoodHappiness();
		if (iHappy > 0)
		{
			iTotalHappy += iHappy;
			szBuffer.append(gDLL->getText("TXT_KEY_HAPPY_FEATURES", iHappy));
			szBuffer.append(NEWLINE);
		}

		iHappy = city.getBonusGoodHappiness();
		if (iHappy > 0)
		{
			iTotalHappy += iHappy;
			szBuffer.append(gDLL->getText("TXT_KEY_HAPPY_BONUS", iHappy));
			szBuffer.append(NEWLINE);
		}

/*************************************************************************************************/
/** Specialists Enhancements, by Supercheese 10/9/09                                                   */
/**                                                                                              */
/**                                                                                              */
/*************************************************************************************************/
		iHappy = city.getSpecialistHappiness();
		if (iHappy > 0)
		{
			iTotalHappy += iHappy;
			szBuffer.append(gDLL->getText("TXT_KEY_HAPPY_SPECIALISTS", iHappy));
			szBuffer.append(NEWLINE);
		}
/*************************************************************************************************/
/** Specialists Enhancements                          END                                              */
/*************************************************************************************************/

		iHappy = city.getReligionGoodHappiness();
		if (iHappy > 0)
		{
			iTotalHappy += iHappy;
			szBuffer.append(gDLL->getText("TXT_KEY_HAPPY_RELIGIOUS_FREEDOM", iHappy));
			szBuffer.append(NEWLINE);
		}

		iHappy = city.getCommerceHappiness();
		if (iHappy > 0)
		{
			iTotalHappy += iHappy;
			szBuffer.append(gDLL->getText("TXT_KEY_HAPPY_ENTERTAINMENT", iHappy));
			szBuffer.append(NEWLINE);
		}

		iHappy = city.area()->getBuildingHappiness(city.getOwnerINLINE());
		if (iHappy > 0)
		{
			iTotalHappy += iHappy;
			szBuffer.append(gDLL->getText("TXT_KEY_HAPPY_BUILDINGS", iHappy));
			szBuffer.append(NEWLINE);
		}

		iHappy = GET_PLAYER(city.getOwnerINLINE()).getBuildingHappiness();
		if (iHappy > 0)
		{
			iTotalHappy += iHappy;
			szBuffer.append(gDLL->getText("TXT_KEY_HAPPY_BUILDINGS", iHappy));
			szBuffer.append(NEWLINE);
		}

		iHappy = (city.getExtraHappiness() + GET_PLAYER(city.getOwnerINLINE()).getExtraHappiness());
		if (iHappy > 0)
		{
			iTotalHappy += iHappy;
			szBuffer.append(gDLL->getText("TXT_KEY_HAPPY_YEAH", iHappy));
			szBuffer.append(NEWLINE);
		}

		if (city.getHappinessTimer() > 0)
		{
			iHappy = GC.getDefineINT("TEMP_HAPPY");
			iTotalHappy += iHappy;
			szBuffer.append(gDLL->getText("TXT_KEY_HAPPY_TEMP", iHappy, city.getHappinessTimer()));
			szBuffer.append(NEWLINE);
		}

		iHappy = GC.getHandicapInfo(city.getHandicapType()).getHappyBonus();
		if (iHappy > 0)
		{
			iTotalHappy += iHappy;
			szBuffer.append(gDLL->getText("TXT_KEY_HAPPY_HANDICAP", iHappy));
			szBuffer.append(NEWLINE);
		}

		szBuffer.append(L"-----------------------\n");

		szBuffer.append(gDLL->getText("TXT_KEY_HAPPY_TOTAL_HAPPY", iTotalHappy));

		FAssert(iTotalHappy == city.happyLevel())
	}
}

// BUG - Building Additional Happiness - start
bool CvGameTextMgr::setBuildingAdditionalHappinessHelp(CvWStringBuffer &szBuffer, const CvCity& city, const CvWString& szStart, bool bStarted)
{
	CvWString szLabel;
	CvCivilizationInfo& kCivilization = GC.getCivilizationInfo(GET_PLAYER(city.getOwnerINLINE()).getCivilizationType());

	for (int iI = 0; iI < GC.getNumBuildingClassInfos(); iI++)
	{
		BuildingTypes eBuilding = (BuildingTypes)kCivilization.getCivilizationBuildings((BuildingClassTypes)iI);

		if (eBuilding != NO_BUILDING && city.canConstruct(eBuilding, false, true, false))
		{
			int iGood = 0, iBad = 0;
			int iChange = city.getAdditionalHappinessByBuilding(eBuilding, iGood, iBad);

			if (iGood != 0 || iBad != 0)
			{
				int iAngryPop = city.getAdditionalAngryPopuplation(iGood, iBad);

				if (!bStarted)
				{
					szBuffer.append(szStart);
					bStarted = true;
				}

				szLabel.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_BUILDING_TEXT"), GC.getBuildingInfo(eBuilding).getDescription());
				bool bStartedLine = setResumableGoodBadChangeHelp(szBuffer, szLabel, L": ", L"", iGood, gDLL->getSymbolID(HAPPY_CHAR), iBad, gDLL->getSymbolID(UNHAPPY_CHAR), false, true);
				setResumableValueChangeHelp(szBuffer, szLabel, L": ", L"", iAngryPop, gDLL->getSymbolID(ANGRY_POP_CHAR), false, true, bStartedLine);
			}
		}
	}

	return bStarted;
}
// BUG - Building Additional Happiness - end


// BUG - Resumable Value Change Help - start
void CvGameTextMgr::setYieldChangeHelp(CvWStringBuffer &szBuffer, const CvWString& szStart, const CvWString& szSpace, const CvWString& szEnd, const int* piYieldChange, bool bPercent, bool bNewLine)
{
	setResumableYieldChangeHelp(szBuffer, szStart, szSpace, szEnd, piYieldChange, bPercent, bNewLine);
}

/*
 * Adds the ability to pass in and get back the value of bStarted so that
 * it can be used with other setResumable<xx>ChangeHelp() calls on a single line.
 */
bool CvGameTextMgr::setResumableYieldChangeHelp(CvWStringBuffer &szBuffer, const CvWString& szStart, const CvWString& szSpace, const CvWString& szEnd, const int* piYieldChange, bool bPercent, bool bNewLine, bool bStarted)
{
	CvWString szTempBuffer;
//	bool bStarted;
	int iI;

//	bStarted = false;

	for (iI = 0; iI < NUM_YIELD_TYPES; ++iI)
	{
		if (piYieldChange[iI] != 0)
		{
			if (!bStarted)
			{
				if (bNewLine)
				{
					szTempBuffer.Format(L"\n%c", gDLL->getSymbolID(BULLET_CHAR));
				}
				szTempBuffer += CvWString::format(L"%s%s%s%d%s%c",
					szStart.GetCString(),
					szSpace.GetCString(),
					piYieldChange[iI] > 0 ? L"+" : L"",
					piYieldChange[iI],
					bPercent ? L"%" : L"",
					GC.getYieldInfo((YieldTypes)iI).getChar());
			}
			else
			{
				szTempBuffer.Format(L", %s%d%s%c",
					piYieldChange[iI] > 0 ? L"+" : L"",
					piYieldChange[iI],
					bPercent ? L"%" : L"",
					GC.getYieldInfo((YieldTypes)iI).getChar());
			}
			szBuffer.append(szTempBuffer);

			bStarted = true;
		}
	}

	if (bStarted)
	{
		szBuffer.append(szEnd);
	}

// added
	return bStarted;
}

void CvGameTextMgr::setCommerceChangeHelp(CvWStringBuffer &szBuffer, const CvWString& szStart, const CvWString& szSpace, const CvWString& szEnd, const int* piCommerceChange, bool bPercent, bool bNewLine)
{
	setResumableCommerceChangeHelp(szBuffer, szStart, szSpace, szEnd, piCommerceChange, bPercent, bNewLine);
}

/*
 * Adds the ability to pass in and get back the value of bStarted so that
 * it can be used with other setResumable<xx>ChangeHelp() calls on a single line.
 */
bool CvGameTextMgr::setResumableCommerceChangeHelp(CvWStringBuffer &szBuffer, const CvWString& szStart, const CvWString& szSpace, const CvWString& szEnd, const int* piCommerceChange, bool bPercent, bool bNewLine, bool bStarted)
{
	CvWString szTempBuffer;
//	bool bStarted;
	int iI;

//	bStarted = false;

	for (iI = 0; iI < NUM_COMMERCE_TYPES; ++iI)
	{
		if (piCommerceChange[iI] != 0)
		{
			if (!bStarted)
			{
				if (bNewLine)
				{
					szTempBuffer.Format(L"\n%c", gDLL->getSymbolID(BULLET_CHAR));
				}
				szTempBuffer += CvWString::format(L"%s%s%s%d%s%c", szStart.GetCString(), szSpace.GetCString(), ((piCommerceChange[iI] > 0) ? L"+" : L""), piCommerceChange[iI], ((bPercent) ? L"%" : L""), GC.getCommerceInfo((CommerceTypes) iI).getChar());
			}
			else
			{
				szTempBuffer.Format(L", %s%d%s%c", ((piCommerceChange[iI] > 0) ? L"+" : L""), piCommerceChange[iI], ((bPercent) ? L"%" : L""), GC.getCommerceInfo((CommerceTypes) iI).getChar());
			}
			szBuffer.append(szTempBuffer);

			bStarted = true;
		}
	}

	if (bStarted)
	{
		szBuffer.append(szEnd);
	}

// added
	return bStarted;
}

/*
 * Displays float values by dividing each value by 100.
 */
void CvGameTextMgr::setCommerceTimes100ChangeHelp(CvWStringBuffer &szBuffer, const CvWString& szStart, const CvWString& szSpace, const CvWString& szEnd, const int* piCommerceChange, bool bNewLine, bool bStarted)
{
	setResumableCommerceTimes100ChangeHelp(szBuffer, szStart, szSpace, szEnd, piCommerceChange, bNewLine);
}

/*
 * Adds the ability to pass in and get back the value of bStarted so that
 * it can be used with other setResumable<xx>ChangeHelp() calls on a single line.
 */
bool CvGameTextMgr::setResumableCommerceTimes100ChangeHelp(CvWStringBuffer &szBuffer, const CvWString& szStart, const CvWString& szSpace, const CvWString& szEnd, const int* piCommerceChange, bool bNewLine, bool bStarted)
{
	CvWString szTempBuffer;

	for (int iI = 0; iI < NUM_COMMERCE_TYPES; ++iI)
	{
		int iChange = piCommerceChange[iI];
		if (iChange != 0)
		{
			if (!bStarted)
			{
				if (bNewLine)
				{
					szTempBuffer.Format(L"\n%c", gDLL->getSymbolID(BULLET_CHAR));
				}
				szTempBuffer += CvWString::format(L"%s%s", szStart.GetCString(), szSpace.GetCString());
				bStarted = true;
			}
			else
			{
				szTempBuffer.Format(L", ");
			}
			szBuffer.append(szTempBuffer);

			if (iChange % 100 == 0)
			{
				szTempBuffer.Format(L"%+d%c", iChange / 100, GC.getCommerceInfo((CommerceTypes) iI).getChar());
			}
			else
			{
				if (iChange >= 0)
				{
					szBuffer.append(L"+");
				}
				else
				{
					iChange = - iChange;
					szBuffer.append(L"-");
				}
				szTempBuffer.Format(L"%d.%02d%c", iChange / 100, iChange % 100, GC.getCommerceInfo((CommerceTypes) iI).getChar());
			}
			szBuffer.append(szTempBuffer);
		}
	}

	if (bStarted)
	{
		szBuffer.append(szEnd);
	}

	return bStarted;
}

/*
 * Adds the ability to pass in and get back the value of bStarted so that
 * it can be used with other setResumable<xx>ChangeHelp() calls on a single line.
 */
bool CvGameTextMgr::setResumableGoodBadChangeHelp(CvWStringBuffer &szBuffer, const CvWString& szStart, const CvWString& szSpace, const CvWString& szEnd, int iGood, int iGoodSymbol, int iBad, int iBadSymbol, bool bPercent, bool bNewLine, bool bStarted)
{
	bStarted = setResumableValueChangeHelp(szBuffer, szStart, szSpace, szEnd, iGood, iGoodSymbol, bPercent, bNewLine, bStarted);
	bStarted = setResumableValueChangeHelp(szBuffer, szStart, szSpace, szEnd, iBad, iBadSymbol, bPercent, bNewLine, bStarted);

	return bStarted;
}

/*
 * Adds the ability to pass in and get back the value of bStarted so that
 * it can be used with other setResumable<xx>ChangeHelp() calls on a single line.
 */
bool CvGameTextMgr::setResumableValueChangeHelp(CvWStringBuffer &szBuffer, const CvWString& szStart, const CvWString& szSpace, const CvWString& szEnd, int iValue, int iSymbol, bool bPercent, bool bNewLine, bool bStarted)
{
	CvWString szTempBuffer;

	if (iValue != 0)
	{
		if (!bStarted)
		{
			if (bNewLine)
			{
				szTempBuffer.Format(L"\n%c", gDLL->getSymbolID(BULLET_CHAR));
			}
			szTempBuffer += CvWString::format(L"%s%s", szStart.GetCString(), szSpace.GetCString());
		}
		else
		{
			szTempBuffer = L", ";
		}
		szBuffer.append(szTempBuffer);

		szTempBuffer.Format(L"%+d%s%c", iValue, bPercent ? L"%" : L"", iSymbol);
		szBuffer.append(szTempBuffer);

		bStarted = true;
	}

	return bStarted;
}

/*
 * Adds the ability to pass in and get back the value of bStarted so that
 * it can be used with other setResumable<xx>ChangeHelp() calls on a single line.
 */
bool CvGameTextMgr::setResumableValueTimes100ChangeHelp(CvWStringBuffer &szBuffer, const CvWString& szStart, const CvWString& szSpace, const CvWString& szEnd, int iValue, int iSymbol, bool bNewLine, bool bStarted)
{
	CvWString szTempBuffer;

	if (iValue != 0)
	{
		if (!bStarted)
		{
			if (bNewLine)
			{
				szTempBuffer.Format(L"\n%c", gDLL->getSymbolID(BULLET_CHAR));
			}
			szTempBuffer += CvWString::format(L"%s%s", szStart.GetCString(), szSpace.GetCString());
		}
		else
		{
			szTempBuffer = L", ";
		}
		szBuffer.append(szTempBuffer);

		if (iValue % 100 == 0)
		{
			szTempBuffer.Format(L"%+d%c", iValue / 100, iSymbol);
		}
		else
		{
			if (iValue >= 0)
			{
				szBuffer.append(L"+");
			}
			else
			{
				iValue = - iValue;
				szBuffer.append(L"-");
			}
			szTempBuffer.Format(L"%d.%02d%c", iValue / 100, iValue % 100, iSymbol);
		}
		szBuffer.append(szTempBuffer);

		bStarted = true;
	}

	return bStarted;
}
// BUG - Resumable Value Change Help - end

// BUG - Trade Denial - start
void CvGameTextMgr::setBonusHelp(CvWStringBuffer &szBuffer, BonusTypes eBonus, bool bCivilopediaText)
{
	setBonusTradeHelp(szBuffer, eBonus, bCivilopediaText, NO_PLAYER);
}

void CvGameTextMgr::setBonusTradeHelp(CvWStringBuffer &szBuffer, BonusTypes eBonus, bool bCivilopediaText, PlayerTypes eTradePlayer)
// BUG - Trade Denial - end
{
	if (NO_BONUS == eBonus)
	{
		return;
	}

	if (!bCivilopediaText)
	{		
		szBuffer.append(CvWString::format( SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getBonusInfo(eBonus).getDescription()));

		if (NO_PLAYER != GC.getGameINLINE().getActivePlayer())
		{
			CvPlayer& kActivePlayer = GET_PLAYER(GC.getGameINLINE().getActivePlayer());
			szBuffer.append(gDLL->getText("TXT_KEY_BONUS_AVAILABLE_PLAYER", kActivePlayer.getNumAvailableBonuses(eBonus), kActivePlayer.getNameKey()));

			for (int iCorp = 0; iCorp < GC.getNumCorporationInfos(); ++iCorp)
			{
				bool bFound = false;
				if (kActivePlayer.isActiveCorporation((CorporationTypes)iCorp))
				{
					for (int i = 0; i < GC.getNUM_CORPORATION_PREREQ_BONUSES(); ++i)
					{
						if (eBonus == GC.getCorporationInfo((CorporationTypes)iCorp).getPrereqBonus(i))
						{
							int iLoop;
							for (CvCity* pCity = kActivePlayer.firstCity(&iLoop); NULL != pCity; pCity = kActivePlayer.nextCity(&iLoop))
							{
								if (pCity->isHasCorporation((CorporationTypes)iCorp))
								{
									bFound = true;
									break;
								}
							}
						}

						if (bFound)
						{
							break;
						}
					}
				}

				if (bFound)
				{
					szBuffer.append(GC.getCorporationInfo((CorporationTypes)iCorp).getChar());
				}
			}
		}

		setYieldChangeHelp(szBuffer, L"", L"", L"", GC.getBonusInfo(eBonus).getYieldChangeArray());

		if (GC.getBonusInfo(eBonus).getTechReveal() != NO_TECH)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BONUS_REVEALED_BY", GC.getTechInfo((TechTypes)GC.getBonusInfo(eBonus).getTechReveal()).getTextKeyWide()));
		}
	}

	ImprovementTypes eImprovement = NO_IMPROVEMENT;
	for (int iLoopImprovement = 0; iLoopImprovement < GC.getNumImprovementInfos(); iLoopImprovement++)
	{
		if (GC.getImprovementInfo((ImprovementTypes)iLoopImprovement).isImprovementBonusMakesValid(eBonus))
		{
			eImprovement = (ImprovementTypes)iLoopImprovement;
			break;
		}
	}
	
	if (GC.getBonusInfo(eBonus).getHealth() != 0)
	{
		if (GC.getBonusInfo(eBonus).getHealth() > 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BONUS_HEALTHY", GC.getBonusInfo(eBonus).getHealth()));
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BONUS_UNHEALTHY", -GC.getBonusInfo(eBonus).getHealth()));
		}

		if (eImprovement != NO_IMPROVEMENT)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_BONUS_WITH_IMPROVEMENT", GC.getImprovementInfo(eImprovement).getTextKeyWide()));
		}
	}

	if (GC.getBonusInfo(eBonus).getHappiness() != 0)
	{
		if (GC.getBonusInfo(eBonus).getHappiness() > 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BONUS_HAPPY", GC.getBonusInfo(eBonus).getHappiness()));
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BONUS_UNHAPPY", -GC.getBonusInfo(eBonus).getHappiness()));
		}

		if (eImprovement != NO_IMPROVEMENT)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_BONUS_WITH_IMPROVEMENT", GC.getImprovementInfo(eImprovement).getTextKeyWide()));
		}
	}

//FfH: Added by Kael 08/21/2007
	if (GC.getBonusInfo(eBonus).getDiscoverRandModifier() != 0)
	{
        szBuffer.append(NEWLINE);
        if (GC.getBonusInfo(eBonus).getDiscoverRandModifier() > 0)
        {
            szBuffer.append(gDLL->getText("TXT_KEY_BONUS_DISCOVER_RAND_MODIFIER_INCREASE"));
        }
        if (GC.getBonusInfo(eBonus).getDiscoverRandModifier() < 0)
        {
            szBuffer.append(gDLL->getText("TXT_KEY_BONUS_DISCOVER_RAND_MODIFIER_DECREASE"));
        }
	}
	if (GC.getBonusInfo(eBonus).getGreatPeopleRateModifier() != 0)
	{
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BONUS_GREAT_PEOPLE_RATE_MODIFIER", GC.getBonusInfo(eBonus).getGreatPeopleRateModifier()));
	}
	if (GC.getBonusInfo(eBonus).getHealChange() != 0)
	{
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BONUS_HEAL_CHANGE", GC.getBonusInfo(eBonus).getHealChange()));
	}
	if (GC.getBonusInfo(eBonus).getHealChangeEnemy() != 0)
	{
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BONUS_HEAL_CHANGE_ENEMY", GC.getBonusInfo(eBonus).getHealChangeEnemy()));
	}
	if (GC.getBonusInfo(eBonus).getMaintenanceModifier() != 0)
	{
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BONUS_MAINTENANCE_MODIFIER", GC.getBonusInfo(eBonus).getMaintenanceModifier()));
	}
	if (GC.getBonusInfo(eBonus).getResearchModifier() != 0)
	{
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BONUS_RESEARCH_MODIFIER", GC.getBonusInfo(eBonus).getResearchModifier()));
	}

// BonusPedia 08/2016 lfgr
	if( GC.getBonusInfo( eBonus ).getBadAttitude() < 0 )
	{
        szBuffer.append( NEWLINE );
        szBuffer.append( gDLL->getText( "TXT_KEY_BONUS_BAD_ATTITUDE" ) );
	}

	if( GC.getBonusInfo( eBonus ).getFreePromotion() != NO_PROMOTION )
	{
		CvPromotionInfo& kPromotion = GC.getPromotionInfo( (PromotionTypes) GC.getBonusInfo( eBonus ).getFreePromotion() );
        szBuffer.append( NEWLINE );
		szBuffer.append( gDLL->getText( "TXT_KEY_BONUS_FREE_PROMOTION", kPromotion.getDescription() ) );
	}

	if( GC.getBonusInfo( eBonus ).getMutateChance() != 0 )
	{
		szBuffer.append( NEWLINE );
		szBuffer.append( gDLL->getText( "TXT_KEY_BONUS_MUTATE_CHANCE", GC.getBonusInfo( eBonus ).getMutateChance() ) );
	}
// BonusPedia END

	if (GC.getBonusInfo(eBonus).isModifierPerBonus())
	{
        szBuffer.append(NEWLINE);
        szBuffer.append(gDLL->getText("TXT_KEY_BONUS_MODIFIER_PER_BONUS"));
	}
//FfH: End Add

	CivilizationTypes eCivilization = GC.getGameINLINE().getActiveCivilizationType();

	for (int i = 0; i < GC.getNumBuildingClassInfos(); i++)
	{
		BuildingTypes eLoopBuilding;
		if (eCivilization == NO_CIVILIZATION)
		{
			eLoopBuilding = ((BuildingTypes)(GC.getBuildingClassInfo((BuildingClassTypes)i).getDefaultBuildingIndex()));
		}
		else
		{
			eLoopBuilding = ((BuildingTypes)(GC.getCivilizationInfo(eCivilization).getCivilizationBuildings(i)));
		}

		if (eLoopBuilding != NO_BUILDING)
		{
			CvBuildingInfo& kBuilding = GC.getBuildingInfo(eLoopBuilding);
			if (kBuilding.getBonusHappinessChanges(eBonus) != 0)
			{
				if (kBuilding.getBonusHappinessChanges(eBonus) > 0)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_BONUS_HAPPY", kBuilding.getBonusHappinessChanges(eBonus)));
				}
				else
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_BONUS_UNHAPPY", -kBuilding.getBonusHappinessChanges(eBonus)));
				}

				szBuffer.append(gDLL->getText("TXT_KEY_BONUS_WITH_IMPROVEMENT", kBuilding.getTextKeyWide()));
			}

			if (kBuilding.getBonusHealthChanges(eBonus) != 0)
			{
				if (kBuilding.getBonusHealthChanges(eBonus) > 0)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_BONUS_HEALTHY", kBuilding.getBonusHealthChanges(eBonus)));
				}
				else
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_BONUS_UNHEALTHY", -kBuilding.getBonusHealthChanges(eBonus)));
				}

				szBuffer.append(gDLL->getText("TXT_KEY_BONUS_WITH_IMPROVEMENT", kBuilding.getTextKeyWide()));
			}
		}
	}

// BUG - Trade Denial - start
	if (eTradePlayer != NO_PLAYER && GC.getGameINLINE().getActivePlayer() != NO_PLAYER && getBugOptionBOOL("MiscHover__BonusTradeDenial", true, "BUG_BONUS_TRADE_DENIAL_HOVER"))
	{
		TradeData trade;
		trade.m_eItemType = TRADE_RESOURCES;
		trade.m_iData = eBonus;

		if (GET_PLAYER(eTradePlayer).canTradeItem(GC.getGameINLINE().getActivePlayer(), trade, false))
		{
			DenialTypes eDenial = GET_PLAYER(eTradePlayer).getTradeDenial(GC.getGameINLINE().getActivePlayer(), trade);
			if (eDenial != NO_DENIAL)
			{
				CvWString szTempBuffer;
				szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_NEGATIVE_TEXT"), GC.getDenialInfo(eDenial).getDescription());
				szBuffer.append(NEWLINE);
				szBuffer.append(szTempBuffer);
			}
		}
	}
// BUG - Trade Denial - end

	if (!CvWString(GC.getBonusInfo(eBonus).getHelp()).empty())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(GC.getBonusInfo(eBonus).getHelp());
	}
}

void CvGameTextMgr::setReligionHelp(CvWStringBuffer &szBuffer, ReligionTypes eReligion, bool bCivilopedia)
{
	UnitTypes eFreeUnit;

	if (NO_RELIGION == eReligion)
	{
		return;
	}
	CvReligionInfo& religion = GC.getReligionInfo(eReligion);

	if (!bCivilopedia)
	{
		szBuffer.append(CvWString::format(SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), religion.getDescription()));
	}

	setCommerceChangeHelp(szBuffer, gDLL->getText("TXT_KEY_RELIGION_HOLY_CITY").c_str(), L": ", L"", religion.getHolyCityCommerceArray());
	setCommerceChangeHelp(szBuffer, gDLL->getText("TXT_KEY_RELIGION_ALL_CITIES").c_str(), L": ", L"", religion.getStateReligionCommerceArray());

	if (!bCivilopedia)
	{
		if (religion.getTechPrereq() != NO_TECH)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_RELIGION_FOUNDED_FIRST", GC.getTechInfo((TechTypes)religion.getTechPrereq()).getTextKeyWide()));
		}
	}

	if (religion.getFreeUnitClass() != NO_UNITCLASS)
	{
		if (GC.getGameINLINE().getActivePlayer() != NO_PLAYER)
		{
			eFreeUnit = ((UnitTypes)(GC.getCivilizationInfo(GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getCivilizationType()).getCivilizationUnits(religion.getFreeUnitClass())));
		}
		else
		{
			eFreeUnit = (UnitTypes)GC.getUnitClassInfo((UnitClassTypes)religion.getFreeUnitClass()).getDefaultUnitIndex();
		}

		if (eFreeUnit != NO_UNIT)
		{
			if (religion.getNumFreeUnits() > 1)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_RELIGION_FOUNDER_RECEIVES_NUM", GC.getUnitInfo(eFreeUnit).getTextKeyWide(), religion.getNumFreeUnits()));
			}
			else if (religion.getNumFreeUnits() > 0)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_RELIGION_FOUNDER_RECEIVES", GC.getUnitInfo(eFreeUnit).getTextKeyWide()));
			}
		}
	}
}

void CvGameTextMgr::setReligionHelpCity(CvWStringBuffer &szBuffer, ReligionTypes eReligion, CvCity *pCity, bool bCityScreen, bool bForceReligion, bool bForceState, bool bNoStateReligion)
{
	int i;
	CvWString szTempBuffer;
	bool bHandled = false;
	int iCommerce;
	int iHappiness;
	int iProductionModifier;
	int iFreeExperience;
	int iGreatPeopleRateModifier;

	if (pCity == NULL)
	{
		return;
	}

	ReligionTypes eStateReligion = (bNoStateReligion ? NO_RELIGION : GET_PLAYER(pCity->getOwnerINLINE()).getStateReligion());

	if (bCityScreen)
	{
		szBuffer.append(CvWString::format(SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getReligionInfo(eReligion).getDescription()));
		szBuffer.append(NEWLINE);

		if (!(GC.getGameINLINE().isReligionFounded(eReligion)) && !GC.getGameINLINE().isOption(GAMEOPTION_PICK_RELIGION))
		{
			if (GC.getReligionInfo(eReligion).getTechPrereq() != NO_TECH)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_RELIGION_FOUNDED_FIRST", GC.getTechInfo((TechTypes)(GC.getReligionInfo(eReligion).getTechPrereq())).getTextKeyWide()));
			}
		}
	}

	if (!bForceReligion)
	{
		if (!(pCity->isHasReligion(eReligion)))
		{
			return;
		}
	}

	if (eStateReligion == eReligion || eStateReligion == NO_RELIGION || bForceState)
	{
		for (i = 0; i < NUM_COMMERCE_TYPES; i++)
		{
			iCommerce = GC.getReligionInfo(eReligion).getStateReligionCommerce((CommerceTypes)i);

			if (pCity->isHolyCity(eReligion))
			{
				iCommerce += GC.getReligionInfo(eReligion).getHolyCityCommerce((CommerceTypes)i);
			}

			if (iCommerce != 0)
			{
				if (bHandled)
				{
					szBuffer.append(L", ");
				}

				szTempBuffer.Format(L"%s%d%c", iCommerce > 0 ? "+" : "", iCommerce, GC.getCommerceInfo((CommerceTypes)i).getChar());
				szBuffer.append(szTempBuffer);
				bHandled = true;
			}
		}
	}

	if (eStateReligion == eReligion || bForceState)
	{
		iHappiness = (pCity->getStateReligionHappiness(eReligion) + GET_PLAYER(pCity->getOwnerINLINE()).getStateReligionHappiness());

		if (iHappiness != 0)
		{
			if (bHandled)
			{
				szBuffer.append(L", ");
			}

/************************************************************************************************/
/* UNOFFICIAL_PATCH                       08/28/09                             jdog5000         */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
			szTempBuffer.Format(L"%d%c", iHappiness, ((iHappiness > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)));
*/
			// Use absolute value with unhappy face
			szTempBuffer.Format(L"%d%c", abs(iHappiness), ((iHappiness > 0) ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR)));
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
			szBuffer.append(szTempBuffer);
			bHandled = true;
		}

		iProductionModifier = GET_PLAYER(pCity->getOwnerINLINE()).getStateReligionBuildingProductionModifier();
		if (iProductionModifier != 0)
		{
			if (bHandled)
			{
				szBuffer.append(L", ");
			}

			szBuffer.append(gDLL->getText("TXT_KEY_RELIGION_BUILDING_PROD_MOD", iProductionModifier));
			bHandled = true;
		}

		iProductionModifier = GET_PLAYER(pCity->getOwnerINLINE()).getStateReligionUnitProductionModifier();
		if (iProductionModifier != 0)
		{
			if (bHandled)
			{
				szBuffer.append(L", ");
			}

			szBuffer.append(gDLL->getText("TXT_KEY_RELIGION_UNIT_PROD_MOD", iProductionModifier));
			bHandled = true;
		}

		iFreeExperience = GET_PLAYER(pCity->getOwnerINLINE()).getStateReligionFreeExperience();
		if (iFreeExperience != 0)
		{
			if (bHandled)
			{
				szBuffer.append(L", ");
			}

			szBuffer.append(gDLL->getText("TXT_KEY_RELIGION_FREE_XP", iFreeExperience));
			bHandled = true;
		}

		iGreatPeopleRateModifier = GET_PLAYER(pCity->getOwnerINLINE()).getStateReligionGreatPeopleRateModifier();
		if (iGreatPeopleRateModifier != 0)
		{
			if (bHandled)
			{
				szBuffer.append(L", ");
			}

			szBuffer.append(gDLL->getText("TXT_KEY_RELIGION_BIRTH_RATE_MOD", iGreatPeopleRateModifier));
			bHandled = true;
		}
	}
}

void CvGameTextMgr::setCorporationHelp(CvWStringBuffer &szBuffer, CorporationTypes eCorporation, bool bCivilopedia)
{
	UnitTypes eFreeUnit;
	CvWString szTempBuffer;

	if (NO_CORPORATION == eCorporation)
	{
		return;
	}
	CvCorporationInfo& kCorporation = GC.getCorporationInfo(eCorporation);

	if (!bCivilopedia)
	{
		szBuffer.append(CvWString::format(SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), kCorporation.getDescription()));
	}

	szTempBuffer.clear();
	for (int iI = 0; iI < NUM_YIELD_TYPES; ++iI)
	{
		int iYieldProduced = GC.getCorporationInfo(eCorporation).getYieldProduced((YieldTypes)iI);
		if (NO_PLAYER != GC.getGameINLINE().getActivePlayer())
		{
			iYieldProduced *= GC.getWorldInfo(GC.getMapINLINE().getWorldSize()).getCorporationMaintenancePercent();
			iYieldProduced /= 100;
		}

		if (iYieldProduced != 0)
		{
			if (!szTempBuffer.empty())
			{
				szTempBuffer += L", ";
			}

			if (iYieldProduced % 100 == 0)
			{
				szTempBuffer += CvWString::format(L"%s%d%c",
					iYieldProduced > 0 ? L"+" : L"",
					iYieldProduced / 100,
					GC.getYieldInfo((YieldTypes)iI).getChar());
			}
			else
			{
				szTempBuffer += CvWString::format(L"%s%.2f%c",
					iYieldProduced > 0 ? L"+" : L"",
					0.01f * abs(iYieldProduced),
					GC.getYieldInfo((YieldTypes)iI).getChar());
			}
		}
	}

	if (!szTempBuffer.empty())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_CORPORATION_ALL_CITIES", szTempBuffer.GetCString()));
	}

	szTempBuffer.clear();
	for (int iI = 0; iI < NUM_COMMERCE_TYPES; ++iI)
	{
		int iCommerceProduced = GC.getCorporationInfo(eCorporation).getCommerceProduced((CommerceTypes)iI);
		if (NO_PLAYER != GC.getGameINLINE().getActivePlayer())
		{
			iCommerceProduced *= GC.getWorldInfo(GC.getMapINLINE().getWorldSize()).getCorporationMaintenancePercent();
			iCommerceProduced /= 100;
		}
		if (iCommerceProduced != 0)
		{
			if (!szTempBuffer.empty())
			{
				szTempBuffer += L", ";
			}

			if (iCommerceProduced % 100 == 0)
			{
				szTempBuffer += CvWString::format(L"%s%d%c",
					iCommerceProduced > 0 ? L"+" : L"",
					iCommerceProduced / 100,
					GC.getCommerceInfo((CommerceTypes)iI).getChar());
			}
			else
			{
				szTempBuffer += CvWString::format(L"%s%.2f%c",
					iCommerceProduced > 0 ? L"+" : L"",
					0.01f * abs(iCommerceProduced),
					GC.getCommerceInfo((CommerceTypes)iI).getChar());
			}

		}
	}

	if (!szTempBuffer.empty())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_CORPORATION_ALL_CITIES", szTempBuffer.GetCString()));
	}

	if (!bCivilopedia)
	{
		if (kCorporation.getTechPrereq() != NO_TECH)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_CORPORATION_FOUNDED_FIRST", GC.getTechInfo((TechTypes)kCorporation.getTechPrereq()).getTextKeyWide()));
		}
	}

	szBuffer.append(NEWLINE);
	szBuffer.append(gDLL->getText("TXT_KEY_CORPORATION_BONUS_REQUIRED"));
	bool bFirst = true;
	for (int i = 0; i < GC.getNUM_CORPORATION_PREREQ_BONUSES(); ++i)
	{
		if (NO_BONUS != kCorporation.getPrereqBonus(i))
		{
			if (bFirst)
			{
				bFirst = false;
			}
			else
			{
				szBuffer.append(L", ");
			}

			szBuffer.append(CvWString::format(L"%c", GC.getBonusInfo((BonusTypes)kCorporation.getPrereqBonus(i)).getChar()));
		}
	}

	if (kCorporation.getBonusProduced() != NO_BONUS)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_CORPORATION_BONUS_PRODUCED", GC.getBonusInfo((BonusTypes)kCorporation.getBonusProduced()).getChar()));
	}

	if (kCorporation.getFreeUnitClass() != NO_UNITCLASS)
	{
		if (GC.getGameINLINE().getActivePlayer() != NO_PLAYER)
		{
			eFreeUnit = ((UnitTypes)(GC.getCivilizationInfo(GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getCivilizationType()).getCivilizationUnits(kCorporation.getFreeUnitClass())));
		}
		else
		{
			eFreeUnit = (UnitTypes)GC.getUnitClassInfo((UnitClassTypes)kCorporation.getFreeUnitClass()).getDefaultUnitIndex();
		}

		if (eFreeUnit != NO_UNIT)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_RELIGION_FOUNDER_RECEIVES", GC.getUnitInfo(eFreeUnit).getTextKeyWide()));
		}
	}

	std::vector<CorporationTypes> aCompetingCorps;
	bFirst = true;
	for (int iCorporation = 0; iCorporation < GC.getNumCorporationInfos(); ++iCorporation)
	{
		if (iCorporation != eCorporation)
		{
			bool bCompeting = false;

			CvCorporationInfo& kLoopCorporation = GC.getCorporationInfo((CorporationTypes)iCorporation);	
			for (int i = 0; i < GC.getNUM_CORPORATION_PREREQ_BONUSES(); ++i)
			{
				if (kCorporation.getPrereqBonus(i) != NO_BONUS)
				{
					for (int j = 0; j < GC.getNUM_CORPORATION_PREREQ_BONUSES(); ++j)
					{
						if (kLoopCorporation.getPrereqBonus(j) == kCorporation.getPrereqBonus(i))
						{
							bCompeting = true;
							break;
						}
					}
				}

				if (bCompeting)
				{
					break;
				}
			}

			if (bCompeting)
			{
				CvWString szTemp = CvWString::format(L"<link=literal>%s</link>", kLoopCorporation.getDescription());
				setListHelp(szBuffer, gDLL->getText("TXT_KEY_CORPORATION_COMPETES").c_str(), szTemp.GetCString(), L", ", bFirst);
				bFirst = false;
			}
		}
	}
}

void CvGameTextMgr::setCorporationHelpCity(CvWStringBuffer &szBuffer, CorporationTypes eCorporation, CvCity *pCity, bool bCityScreen, bool bForceCorporation)
{
	if (pCity == NULL)
	{
		return;
	}

	CvCorporationInfo& kCorporation = GC.getCorporationInfo(eCorporation);

	if (bCityScreen)
	{
		szBuffer.append(CvWString::format(SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), kCorporation.getDescription()));
		szBuffer.append(NEWLINE);

		if (!(GC.getGameINLINE().isCorporationFounded(eCorporation)))
		{
			if (GC.getCorporationInfo(eCorporation).getTechPrereq() != NO_TECH)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_CORPORATION_FOUNDED_FIRST", GC.getTechInfo((TechTypes)(kCorporation.getTechPrereq())).getTextKeyWide()));
			}
		}
	}

	if (!bForceCorporation)
	{
		if (!(pCity->isHasCorporation(eCorporation)))
		{
			return;
		}
	}

	int iNumResources = 0;
	for (int i = 0; i < GC.getNUM_CORPORATION_PREREQ_BONUSES(); ++i)
	{
		BonusTypes eBonus = (BonusTypes)kCorporation.getPrereqBonus(i);
		if (NO_BONUS != eBonus)
		{
			iNumResources += pCity->getNumBonuses(eBonus);
		}
	}

	bool bActive = (pCity->isActiveCorporation(eCorporation) || (bForceCorporation && iNumResources > 0));
	
	bool bHandled = false;
	for (int i = 0; i < NUM_YIELD_TYPES; ++i)
	{
		int iYield = 0;

		if (bActive)
		{
			iYield += (kCorporation.getYieldProduced(i) * iNumResources * GC.getWorldInfo(GC.getMapINLINE().getWorldSize()).getCorporationMaintenancePercent()) / 100;
		}

		if (iYield != 0)
		{
			if (bHandled)
			{
				szBuffer.append(L", ");
			}

			CvWString szTempBuffer;
			szTempBuffer.Format(L"%s%d%c", iYield > 0 ? "+" : "", (iYield + 99) / 100, GC.getYieldInfo((YieldTypes)i).getChar());
			szBuffer.append(szTempBuffer);
			bHandled = true;
		}
	}

	bHandled = false;
	for (int i = 0; i < NUM_COMMERCE_TYPES; ++i)
	{
		int iCommerce = 0;
		
		if (bActive)
		{
			iCommerce += (kCorporation.getCommerceProduced(i) * iNumResources * GC.getWorldInfo(GC.getMapINLINE().getWorldSize()).getCorporationMaintenancePercent()) / 100;
		}

		if (iCommerce != 0)
		{
			if (bHandled)
			{
				szBuffer.append(L", ");
			}

			CvWString szTempBuffer;
			szTempBuffer.Format(L"%s%d%c", iCommerce > 0 ? "+" : "", (iCommerce + 99) / 100, GC.getCommerceInfo((CommerceTypes)i).getChar());
			szBuffer.append(szTempBuffer);
			bHandled = true;
		}
	}

	int iMaintenance = 0;
	
	if (bActive)
	{		
		iMaintenance += pCity->calculateCorporationMaintenanceTimes100(eCorporation);
		iMaintenance *= 100 + pCity->getMaintenanceModifier();
		iMaintenance /= 100;
	}

	if (0 != iMaintenance)
	{
		if (bHandled)
		{
			szBuffer.append(L", ");
		}

		CvWString szTempBuffer;
		szTempBuffer.Format(L"%d%c", -iMaintenance / 100, GC.getCommerceInfo(COMMERCE_GOLD).getChar());
		szBuffer.append(szTempBuffer);
		bHandled = true;
	}

	if (bCityScreen)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_CORPORATION_BONUS_REQUIRED"));
		bool bFirst = true;
		for (int i = 0; i < GC.getNUM_CORPORATION_PREREQ_BONUSES(); ++i)
		{
			if (NO_BONUS != kCorporation.getPrereqBonus(i))
			{
				if (bFirst)
				{
					bFirst = false;
				}
				else
				{
					szBuffer.append(L", ");
				}

				szBuffer.append(CvWString::format(L"%c", GC.getBonusInfo((BonusTypes)kCorporation.getPrereqBonus(i)).getChar()));
			}
		}

		if (bActive)
		{
			if (kCorporation.getBonusProduced() != NO_BONUS)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_CORPORATION_BONUS_PRODUCED", GC.getBonusInfo((BonusTypes)kCorporation.getBonusProduced()).getChar()));
			}
		}
	}
	else
	{
		if (kCorporation.getBonusProduced() != NO_BONUS)
		{
			if (bActive)
			{
				if (bHandled)
				{
					szBuffer.append(L", ");
				}

				szBuffer.append(CvWString::format(L"%c", GC.getBonusInfo((BonusTypes)kCorporation.getBonusProduced()).getChar()));
			}
		}
	}
}

void CvGameTextMgr::buildObsoleteString(CvWStringBuffer &szBuffer, int iItem, bool bList, bool bPlayerContext)
{
	CvWString szTempBuffer;

	if (bList)
	{
		szBuffer.append(NEWLINE);
	}
	szBuffer.append(gDLL->getText("TXT_KEY_TECH_OBSOLETES", GC.getBuildingInfo((BuildingTypes) iItem).getTextKeyWide()));
}

void CvGameTextMgr::buildObsoleteBonusString(CvWStringBuffer &szBuffer, int iItem, bool bList, bool bPlayerContext)
{
	CvWString szTempBuffer;

	if (bList)
	{
		szBuffer.append(NEWLINE);
	}
	szBuffer.append(gDLL->getText("TXT_KEY_TECH_OBSOLETES", GC.getBonusInfo((BonusTypes) iItem).getTextKeyWide()));
}

void CvGameTextMgr::buildEnableBonusString(CvWStringBuffer &szBuffer, int iItem, bool bList, bool bPlayerContext)
{
	CvWString szTempBuffer;

	if (bList)
	{
		szBuffer.append(NEWLINE);
	}
	szBuffer.append(gDLL->getText("TXT_KEY_TECH_ENABLES", GC.getBonusInfo((BonusTypes) iItem).getTextKeyWide()));
}

void CvGameTextMgr::buildObsoleteSpecialString(CvWStringBuffer &szBuffer, int iItem, bool bList, bool bPlayerContext)
{
	CvWString szTempBuffer;

	if (bList)
	{
		szBuffer.append(NEWLINE);
	}
	szBuffer.append(gDLL->getText("TXT_KEY_TECH_OBSOLETES_NO_LINK", GC.getSpecialBuildingInfo((SpecialBuildingTypes) iItem).getTextKeyWide()));
}

void CvGameTextMgr::buildMoveString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	int iI;
	int iMoveDiff;

	for (iI = 0; iI < GC.getNumRouteInfos(); ++iI)
	{
		iMoveDiff = ((GC.getMOVE_DENOMINATOR() / std::max(1, (GC.getRouteInfo((RouteTypes) iI).getMovementCost() + ((bPlayerContext) ? GET_TEAM(GC.getGameINLINE().getActiveTeam()).getRouteChange((RouteTypes)iI) : 0)))) - (GC.getMOVE_DENOMINATOR() / std::max(1, (GC.getRouteInfo((RouteTypes) iI).getMovementCost() + ((bPlayerContext) ? GET_TEAM(GC.getGameINLINE().getActiveTeam()).getRouteChange((RouteTypes)iI) : 0) + GC.getRouteInfo((RouteTypes) iI).getTechMovementChange(eTech)))));

		if (iMoveDiff != 0)
		{
			if (bList)
			{
				szBuffer.append(NEWLINE);
			}
			szBuffer.append(gDLL->getText("TXT_KEY_UNIT_MOVEMENT", -(iMoveDiff), GC.getRouteInfo((RouteTypes) iI).getTextKeyWide()));
			bList = true;
		}
	}
}

void CvGameTextMgr::buildFreeUnitString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	UnitTypes eFreeUnit = NO_UNIT;
	if (GC.getGameINLINE().getActivePlayer() != NO_PLAYER)
	{
		eFreeUnit = GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getTechFreeUnit(eTech);
	}
	else
	{
		if (GC.getTechInfo(eTech).getFirstFreeUnitClass() != NO_UNITCLASS)
		{
			eFreeUnit = (UnitTypes)GC.getUnitClassInfo((UnitClassTypes)GC.getTechInfo(eTech).getFirstFreeUnitClass()).getDefaultUnitIndex();
		}
	}

	if (eFreeUnit != NO_UNIT)
	{
		if (!bPlayerContext || (GC.getGameINLINE().countKnownTechNumTeams(eTech) == 0))
		{
			if (bList)
			{
				szBuffer.append(NEWLINE);
			}
			szBuffer.append(gDLL->getText("TXT_KEY_TECH_FIRST_RECEIVES", GC.getUnitInfo(eFreeUnit).getTextKeyWide()));
		}
	}
}

void CvGameTextMgr::buildFeatureProductionString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).getFeatureProductionModifier() != 0)
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_FEATURE_PRODUCTION_MODIFIER", GC.getTechInfo(eTech).getFeatureProductionModifier()));
	}
}

void CvGameTextMgr::buildWorkerRateString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).getWorkerSpeedModifier() != 0)
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_WORKERS_FASTER", GC.getTechInfo(eTech).getWorkerSpeedModifier()));
	}
}

void CvGameTextMgr::buildTradeRouteString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).getTradeRoutes() != 0)
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_TRADE_ROUTES", GC.getTechInfo(eTech).getTradeRoutes()));
	}
}

void CvGameTextMgr::buildHealthRateString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).getHealth() != 0)
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HEALTH_ALL_CITIES", abs(GC.getTechInfo(eTech).getHealth()), ((GC.getTechInfo(eTech).getHealth() > 0) ? gDLL->getSymbolID(HEALTHY_CHAR): gDLL->getSymbolID(UNHEALTHY_CHAR))));
	}
}

void CvGameTextMgr::buildHappinessRateString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).getHappiness() != 0)
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HAPPINESS_ALL_CITIES", abs(GC.getTechInfo(eTech).getHappiness()), ((GC.getTechInfo(eTech).getHappiness() > 0) ? gDLL->getSymbolID(HAPPY_CHAR): gDLL->getSymbolID(UNHAPPY_CHAR))));
	}
}

void CvGameTextMgr::buildFreeTechString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).getFirstFreeTechs() > 0)
	{
		if (!bPlayerContext || (GC.getGameINLINE().countKnownTechNumTeams(eTech) == 0))
		{
			if (bList)
			{
				szBuffer.append(NEWLINE);
			}

			if (GC.getTechInfo(eTech).getFirstFreeTechs() == 1)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_TECH_FIRST_FREE_TECH"));
			}
			else
			{
				szBuffer.append(gDLL->getText("TXT_KEY_TECH_FIRST_FREE_TECHS", GC.getTechInfo(eTech).getFirstFreeTechs()));
			}
		}
	}
}

void CvGameTextMgr::buildLOSString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isExtraWaterSeeFrom() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isExtraWaterSeeFrom())))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_UNIT_EXTRA_SIGHT"));
	}
}

void CvGameTextMgr::buildMapCenterString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isMapCentering() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isMapCentering())))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_CENTERS_MAP"));
	}
}

void CvGameTextMgr::buildMapRevealString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList)
{
	if (GC.getTechInfo(eTech).isMapVisible())
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_REVEALS_MAP"));
	}
}

void CvGameTextMgr::buildMapTradeString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isMapTrading() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isMapTrading())))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ENABLES_MAP_TRADING"));
	}
}

void CvGameTextMgr::buildTechTradeString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isTechTrading() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isTechTrading())))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ENABLES_TECH_TRADING"));
	}
}

void CvGameTextMgr::buildGoldTradeString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isGoldTrading() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isGoldTrading())))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ENABLES_GOLD_TRADING"));
	}
}

void CvGameTextMgr::buildOpenBordersString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isOpenBordersTrading() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isOpenBordersTrading())))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ENABLES_OPEN_BORDERS"));
	}
}

void CvGameTextMgr::buildDefensivePactString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isDefensivePactTrading() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isDefensivePactTrading())))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ENABLES_DEFENSIVE_PACTS"));
	}
}

void CvGameTextMgr::buildPermanentAllianceString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isPermanentAllianceTrading() && (!bPlayerContext || (!(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isPermanentAllianceTrading()) && GC.getGameINLINE().isOption(GAMEOPTION_PERMANENT_ALLIANCES))))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ENABLES_PERM_ALLIANCES"));
	}
}

void CvGameTextMgr::buildVassalStateString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isVassalStateTrading() && (!bPlayerContext || (!(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isVassalStateTrading()) && GC.getGameINLINE().isOption(GAMEOPTION_NO_VASSAL_STATES))))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ENABLES_VASSAL_STATES"));
	}
}

// MNAI - Puppet States
void CvGameTextMgr::buildPuppetStateString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isPuppetStateTrading() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isPuppetStateTrading()) || !(GC.getGameINLINE().isOption(GAMEOPTION_PUPPET_STATES))))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ENABLES_PUPPET_STATES"));
	}
}
// MNAI - End Puppet States


void CvGameTextMgr::buildBridgeString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isBridgeBuilding() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isBridgeBuilding())))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ENABLES_BRIDGE_BUILDING"));
	}
}

void CvGameTextMgr::buildIrrigationString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isIrrigation() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isIrrigation())))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_SPREAD_IRRIGATION"));
	}
}

void CvGameTextMgr::buildIgnoreIrrigationString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isIgnoreIrrigation() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isIgnoreIrrigation())))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_IRRIGATION_ANYWHERE"));
	}
}

void CvGameTextMgr::buildWaterWorkString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isWaterWork() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isWaterWork())))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_WATER_WORK"));
	}
}

void CvGameTextMgr::buildImprovementString(CvWStringBuffer &szBuffer, TechTypes eTech, int iImprovement, bool bList, bool bPlayerContext)
{
	bool bTechFound;
	int iJ;

	bTechFound = false;

	if (GC.getBuildInfo((BuildTypes) iImprovement).getTechPrereq() == NO_TECH)
	{
		for (iJ = 0; iJ < GC.getNumFeatureInfos(); iJ++)
		{
			if (GC.getBuildInfo((BuildTypes) iImprovement).getFeatureTech(iJ) == eTech)
			{
				bTechFound = true;
			}
		}
	}
	else
	{
		if (GC.getBuildInfo((BuildTypes) iImprovement).getTechPrereq() == eTech)
		{
			bTechFound = true;
		}
	}

	if (bTechFound)
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}

		szBuffer.append(gDLL->getText("TXT_KEY_MISC_CAN_BUILD_IMPROVEMENT", GC.getBuildInfo((BuildTypes) iImprovement).getTextKeyWide()));
	}
}

void CvGameTextMgr::buildDomainExtraMovesString(CvWStringBuffer &szBuffer, TechTypes eTech, int iDomainType, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).getDomainExtraMoves(iDomainType) != 0)
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}

		szBuffer.append(gDLL->getText("TXT_KEY_MISC_EXTRA_MOVES", GC.getTechInfo(eTech).getDomainExtraMoves(iDomainType), GC.getDomainInfo((DomainTypes)iDomainType).getTextKeyWide()));
	}
}

void CvGameTextMgr::buildAdjustString(CvWStringBuffer &szBuffer, TechTypes eTech, int iCommerceType, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isCommerceFlexible(iCommerceType) && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isCommerceFlexible((CommerceTypes)iCommerceType))))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ADJUST_COMMERCE_RATE", GC.getCommerceInfo((CommerceTypes) iCommerceType).getChar()));
	}
}

void CvGameTextMgr::buildTerrainTradeString(CvWStringBuffer &szBuffer, TechTypes eTech, int iTerrainType, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isTerrainTrade(iTerrainType) && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isTerrainTrade((TerrainTypes)iTerrainType))))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ENABLES_ON_TERRAIN", gDLL->getSymbolID(TRADE_CHAR), GC.getTerrainInfo((TerrainTypes) iTerrainType).getTextKeyWide()));
	}
}

void CvGameTextMgr::buildRiverTradeString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getTechInfo(eTech).isRiverTrade() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isRiverTrade())))
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ENABLES_ON_TERRAIN", gDLL->getSymbolID(TRADE_CHAR), gDLL->getText("TXT_KEY_MISC_RIVERS").GetCString()));
	}
}

void CvGameTextMgr::buildSpecialBuildingString(CvWStringBuffer &szBuffer, TechTypes eTech, int iBuildingType, bool bList, bool bPlayerContext)
{
	if (GC.getSpecialBuildingInfo((SpecialBuildingTypes)iBuildingType).getTechPrereq() == eTech)
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_CAN_CONSTRUCT_BUILDING", GC.getSpecialBuildingInfo((SpecialBuildingTypes) iBuildingType).getTextKeyWide()));
	}

	if (GC.getSpecialBuildingInfo((SpecialBuildingTypes)iBuildingType).getTechPrereqAnyone() == eTech)
	{
		if (bList)
		{
			szBuffer.append(NEWLINE);
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_CAN_CONSTRUCT_BUILDING_ANYONE", GC.getSpecialBuildingInfo((SpecialBuildingTypes) iBuildingType).getTextKeyWide()));
	}
}

void CvGameTextMgr::buildYieldChangeString(CvWStringBuffer &szBuffer, TechTypes eTech, int iYieldType, bool bList, bool bPlayerContext)
{
	CvWString szTempBuffer;
	if (bList)
	{
		szTempBuffer.Format(L"<link=literal>%s</link>", GC.getImprovementInfo((ImprovementTypes)iYieldType).getDescription());
	}
	else
	{
		szTempBuffer.Format(L"%c<link=literal>%s</link>", gDLL->getSymbolID(BULLET_CHAR), GC.getImprovementInfo((ImprovementTypes)iYieldType).getDescription());
	}

	setYieldChangeHelp(szBuffer, szTempBuffer, L": ", L"", GC.getImprovementInfo((ImprovementTypes)iYieldType).getTechYieldChangesArray(eTech), false, bList);
}

bool CvGameTextMgr::buildBonusRevealString(CvWStringBuffer &szBuffer, TechTypes eTech, int iBonusType, bool bFirst, bool bList, bool bPlayerContext)
{
	CvWString szTempBuffer;

	if (GC.getBonusInfo((BonusTypes) iBonusType).getTechReveal() == eTech)
	{
		if (bList && bFirst)
		{
			szBuffer.append(NEWLINE);
		}
		szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getBonusInfo((BonusTypes) iBonusType).getDescription());
		setListHelp(szBuffer, gDLL->getText("TXT_KEY_MISC_REVEALS").c_str(), szTempBuffer, L", ", bFirst);
		bFirst = false;
	}
	return bFirst;
}

bool CvGameTextMgr::buildCivicRevealString(CvWStringBuffer &szBuffer, TechTypes eTech, int iCivicType, bool bFirst, bool bList, bool bPlayerContext)
{
	CvWString szTempBuffer;

	if (GC.getCivicInfo((CivicTypes) iCivicType).getTechPrereq() == eTech)
	{

//FfH: Modified by Kael 07/30/2009
//		if (bList && bFirst)
//		{
//			szBuffer.append(NEWLINE);
//		}
//		szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getCivicInfo((CivicTypes) iCivicType).getDescription());
//		setListHelp(szBuffer, gDLL->getText("TXT_KEY_MISC_ENABLES").c_str(), szTempBuffer, L", ", bFirst);
//		bFirst = false;
        if (!bPlayerContext ||
          GC.getCivicInfo((CivicTypes)iCivicType).getPrereqCivilization() == NO_CIVILIZATION ||
          GC.getCivicInfo((CivicTypes)iCivicType).getPrereqCivilization() == GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getCivilizationType())
        {
            if (bList && bFirst)
            {
                szBuffer.append(NEWLINE);
            }
            szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getCivicInfo((CivicTypes) iCivicType).getDescription());
            setListHelp(szBuffer, gDLL->getText("TXT_KEY_MISC_ENABLES").c_str(), szTempBuffer, L", ", bFirst);
            bFirst = false;
        }
//FfH: End Modify

	}
	return bFirst;
}

bool CvGameTextMgr::buildProcessInfoString(CvWStringBuffer &szBuffer, TechTypes eTech, int iProcessType, bool bFirst, bool bList, bool bPlayerContext)
{
	CvWString szTempBuffer;

	if (GC.getProcessInfo((ProcessTypes) iProcessType).getTechPrereq() == eTech)
	{
		if (bList && bFirst)
		{
			szBuffer.append(NEWLINE);
		}
		szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getProcessInfo((ProcessTypes) iProcessType).getDescription());
		setListHelp(szBuffer, gDLL->getText("TXT_KEY_MISC_CAN_BUILD").c_str(), szTempBuffer, L", ", bFirst);
		bFirst = false;
	}
	return bFirst;
}

bool CvGameTextMgr::buildFoundReligionString(CvWStringBuffer &szBuffer, TechTypes eTech, int iReligionType, bool bFirst, bool bList, bool bPlayerContext)
{
	CvWString szTempBuffer;

	if (GC.getReligionInfo((ReligionTypes) iReligionType).getTechPrereq() == eTech)
	{
		if (!bPlayerContext || (GC.getGameINLINE().countKnownTechNumTeams(eTech) == 0))
		{
			if (bList && bFirst)
			{
				szBuffer.append(NEWLINE);
			}

			if (GC.getGameINLINE().isOption(GAMEOPTION_PICK_RELIGION))
			{
				szTempBuffer = gDLL->getText("TXT_KEY_RELIGION_UNKNOWN");
			}
			else
			{
				szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getReligionInfo((ReligionTypes) iReligionType).getDescription());
			}
			setListHelp(szBuffer, gDLL->getText("TXT_KEY_MISC_FIRST_DISCOVER_FOUNDS").c_str(), szTempBuffer, L", ", bFirst);
			bFirst = false;
		}
	}
	return bFirst;
}

bool CvGameTextMgr::buildFoundCorporationString(CvWStringBuffer &szBuffer, TechTypes eTech, int iCorporationType, bool bFirst, bool bList, bool bPlayerContext)
{
	CvWString szTempBuffer;

	if (GC.getCorporationInfo((CorporationTypes) iCorporationType).getTechPrereq() == eTech)
	{
		if (!bPlayerContext || (GC.getGameINLINE().countKnownTechNumTeams(eTech) == 0))
		{
			if (bList && bFirst)
			{
				szBuffer.append(NEWLINE);
			}
			szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getCorporationInfo((CorporationTypes) iCorporationType).getDescription());
			setListHelp(szBuffer, gDLL->getText("TXT_KEY_MISC_FIRST_DISCOVER_INCORPORATES").c_str(), szTempBuffer, L", ", bFirst);
			bFirst = false;
		}
	}
	return bFirst;
}

bool CvGameTextMgr::buildPromotionString(CvWStringBuffer &szBuffer, TechTypes eTech, int iPromotionType, bool bFirst, bool bList, bool bPlayerContext)
{
	CvWString szTempBuffer;

	if (GC.getPromotionInfo((PromotionTypes) iPromotionType).getTechPrereq() == eTech)
	{
		if (bList && bFirst)
		{
			szBuffer.append(NEWLINE);
		}
		szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getPromotionInfo((PromotionTypes) iPromotionType).getDescription());
		setListHelp(szBuffer, gDLL->getText("TXT_KEY_MISC_ENABLES").c_str(), szTempBuffer, L", ", bFirst);
		bFirst = false;
	}
	return bFirst;
}

// Displays a list of derived technologies - no distinction between AND/OR prerequisites
void CvGameTextMgr::buildSingleLineTechTreeString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bPlayerContext)
{
	CvWString szTempBuffer;	// Formatting

	if (NO_TECH == eTech)
	{
		// you need to specify a tech of origin for this method to do anything
		return;
	}
	
// BUG - Show Sped-Up Techs - start
	if (bPlayerContext && getBugOptionBOOL("MiscHover__SpedUpTechs", true, "BUG_SPED_UP_TECHS_HOVER"))
	{
		CvPlayer& player = GET_PLAYER(GC.getGameINLINE().getActivePlayer());

		// techs that speed this one up
		bool bFirst = true;
		for (int iJ = 0; iJ < GC.getNUM_OR_TECH_PREREQS(); iJ++)
		{
			TechTypes ePrereqTech = (TechTypes)GC.getTechInfo(eTech).getPrereqOrTechs(iJ);
			if (ePrereqTech != NO_TECH && player.canResearch(ePrereqTech))
			{
				szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_TECH_TEXT"), GC.getTechInfo(ePrereqTech).getDescription());
				setListHelp(szBuffer, gDLL->getText("TXT_KEY_MISC_SPED_UP_BY").c_str(), szTempBuffer, L", ", bFirst);
				bFirst = false;
			}
		}

		// techs sped up by this one
		bFirst = true;
		for (int iI = 0; iI < GC.getNumTechInfos(); ++iI)
		{
			if (player.canResearch((TechTypes)iI))
			{
				bool bTechFound = false;

				if (!bTechFound)
				{
					for (int iJ = 0; iJ < GC.getNUM_OR_TECH_PREREQS(); iJ++)
					{
						if (GC.getTechInfo((TechTypes) iI).getPrereqOrTechs(iJ) == eTech)
						{
							bTechFound = true;
							break;
						}
					}
				}

				if (!bTechFound)
				{
					for (int iJ = 0; iJ < GC.getNUM_AND_TECH_PREREQS(); iJ++)
					{
						if (GC.getTechInfo((TechTypes) iI).getPrereqAndTechs(iJ) == eTech)
						{
							bTechFound = true;
							break;
						}
					}
				}

				if (bTechFound)
				{
					szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_TECH_TEXT"), GC.getTechInfo((TechTypes) iI).getDescription());
					setListHelp(szBuffer, gDLL->getText("TXT_KEY_MISC_SPEEDS_UP").c_str(), szTempBuffer, L", ", bFirst);
					bFirst = false;
				}
			}
		}
	}
// BUG - Show Sped-Up Techs - end

	bool bFirst = true;
	for (int iI = 0; iI < GC.getNumTechInfos(); ++iI)
	{
		bool bTechAlreadyAccessible = false;
		if (bPlayerContext)
		{
			bTechAlreadyAccessible = (GET_TEAM(GC.getGameINLINE().getActiveTeam()).isHasTech((TechTypes)iI) || GET_PLAYER(GC.getGameINLINE().getActivePlayer()).canResearch((TechTypes)iI));
		}
		if (!bTechAlreadyAccessible)
		{
			bool bTechFound = false;

			if (!bTechFound)
			{
				for (int iJ = 0; iJ < GC.getNUM_OR_TECH_PREREQS(); iJ++)
				{
					if (GC.getTechInfo((TechTypes) iI).getPrereqOrTechs(iJ) == eTech)
					{
						bTechFound = true;
						break;
					}
				}
			}

			if (!bTechFound)
			{
				for (int iJ = 0; iJ < GC.getNUM_AND_TECH_PREREQS(); iJ++)
				{
					if (GC.getTechInfo((TechTypes) iI).getPrereqAndTechs(iJ) == eTech)
					{
						bTechFound = true;
						break;
					}
				}
			}

			if (bTechFound)
			{
				szTempBuffer.Format( SETCOLR L"<link=literal>%s</link>" ENDCOLR , TEXT_COLOR("COLOR_TECH_TEXT"), GC.getTechInfo((TechTypes) iI).getDescription());
				setListHelp(szBuffer, gDLL->getText("TXT_KEY_MISC_LEADS_TO").c_str(), szTempBuffer, L", ", bFirst);
				bFirst = false;
			}
		}
	}
}

// Information about other prerequisite technologies to eTech besides eFromTech
void CvGameTextMgr::buildTechTreeString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bPlayerContext, TechTypes eFromTech)
{
	CvWString szTempBuffer;	// Formatting

	if (NO_TECH == eTech || NO_TECH == eFromTech)
	{
		return;
	}

	szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_TECH_TEXT"), GC.getTechInfo(eTech).getDescription());
	szBuffer.append(szTempBuffer);

	// Loop through OR prerequisites to make list
	CvWString szOtherOrTechs;
	int nOtherOrTechs = 0;
	bool bOrTechFound = false;
	for (int iJ = 0; iJ < GC.getNUM_OR_TECH_PREREQS(); iJ++)
	{
		TechTypes eTestTech = (TechTypes)GC.getTechInfo(eTech).getPrereqOrTechs(iJ);
		if (eTestTech >= 0)
		{
			bool bTechAlreadyResearched = false;
			if (bPlayerContext)
			{
				bTechAlreadyResearched = GET_TEAM(GC.getGameINLINE().getActiveTeam()).isHasTech(eTestTech);
			}
			if (!bTechAlreadyResearched)
			{
				if (eTestTech == eFromTech)
				{
					bOrTechFound = true;
				}
				else
				{
					szTempBuffer.Format( SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_TECH_TEXT"), GC.getTechInfo(eTestTech).getDescription());
					setListHelp(szOtherOrTechs, L"", szTempBuffer, gDLL->getText("TXT_KEY_OR").c_str(), 0 == nOtherOrTechs);
					nOtherOrTechs++;
				}
			}
		}
	}

	// Loop through AND prerequisites to make list
	CvWString szOtherAndTechs;
	int nOtherAndTechs = 0;
	bool bAndTechFound = false;
	for (int iJ = 0; iJ < GC.getNUM_AND_TECH_PREREQS(); iJ++)
	{
		TechTypes eTestTech = (TechTypes)GC.getTechInfo(eTech).getPrereqAndTechs(iJ);
		if (eTestTech >= 0)
		{
			bool bTechAlreadyResearched = false;
			if (bPlayerContext)
			{
				bTechAlreadyResearched = GET_TEAM(GC.getGameINLINE().getActiveTeam()).isHasTech(eTestTech);
			}
			if (!bTechAlreadyResearched)
			{
				if (eTestTech == eFromTech)
				{
					bAndTechFound = true;
				}
				else
				{
					szTempBuffer.Format( SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_TECH_TEXT"), GC.getTechInfo(eTestTech).getDescription());
					setListHelp(szOtherAndTechs, L"", szTempBuffer, L", ", 0 == nOtherAndTechs);
					nOtherAndTechs++;
				}
			}
		}
	}

	if (bOrTechFound || bAndTechFound)
	{
		if (nOtherAndTechs > 0 || nOtherOrTechs > 0)
		{
			szBuffer.append(L' ');

			if (nOtherAndTechs > 0)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_WITH_SPACE"));
				szBuffer.append(szOtherAndTechs);
			}

			if (nOtherOrTechs > 0)
			{
				if (bAndTechFound)
				{
					if (nOtherAndTechs > 0)
					{
						szBuffer.append(gDLL->getText("TXT_KEY_AND_SPACE"));
					}
					else
					{
						szBuffer.append(gDLL->getText("TXT_KEY_WITH_SPACE"));
					}
					szBuffer.append(szOtherOrTechs);
				}
				else if (bOrTechFound)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_MISC_ALTERNATIVELY_DERIVED", GC.getTechInfo(eTech).getTextKeyWide(), szOtherOrTechs.GetCString()));
				}
			}
		}
	}
}

void CvGameTextMgr::setPromotionHelp(CvWStringBuffer &szBuffer, PromotionTypes ePromotion, bool bCivilopediaText)
{
	if (!bCivilopediaText)
	{
		CvWString szTempBuffer;

		if (NO_PROMOTION == ePromotion)
		{
			return;
		}
		CvPromotionInfo& promo = GC.getPromotionInfo(ePromotion);

		szTempBuffer.Format( SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), promo.getDescription());
		szBuffer.append(szTempBuffer);
	}

	parsePromotionHelp(szBuffer, ePromotion);
}

//FfH: Added by Kael 07/23/2007
void CvGameTextMgr::setSpellHelp(CvWStringBuffer &szBuffer, SpellTypes eSpell, bool bCivilopediaText)
{
	if (!bCivilopediaText)
	{
		CvWString szTempBuffer;

		if (NO_SPELL == eSpell)
		{
			return;
		}
		CvSpellInfo& spell = GC.getSpellInfo(eSpell);
		szTempBuffer.Format( SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), spell.getDescription());
		szBuffer.append(szTempBuffer);
	}

	parseSpellHelp(szBuffer, eSpell);
}
//FfH: End Add

void CvGameTextMgr::setUnitCombatHelp(CvWStringBuffer &szBuffer, UnitCombatTypes eUnitCombat)
{
	szBuffer.append(GC.getUnitCombatInfo(eUnitCombat).getDescription());
}

void CvGameTextMgr::setImprovementHelp(CvWStringBuffer &szBuffer, ImprovementTypes eImprovement, bool bCivilopediaText)
{
	CvWString szTempBuffer;
	CvWString szFirstBuffer;
	int iTurns;

	if (NO_IMPROVEMENT == eImprovement)
	{
		return;
	}

	CvImprovementInfo& info = GC.getImprovementInfo(eImprovement);
	if (!bCivilopediaText)
	{
		szTempBuffer.Format( SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), info.getDescription());
		szBuffer.append(szTempBuffer);

		setYieldChangeHelp(szBuffer, L", ", L"", L"", info.getYieldChangeArray(), false, false);

		setYieldChangeHelp(szBuffer, L"", L"", gDLL->getText("TXT_KEY_MISC_WITH_IRRIGATION").c_str(), info.getIrrigatedYieldChangeArray());
		setYieldChangeHelp(szBuffer, L"", L"", gDLL->getText("TXT_KEY_MISC_ON_HILLS").c_str(), info.getHillsYieldChangeArray());
		setYieldChangeHelp(szBuffer, L"", L"", gDLL->getText("TXT_KEY_MISC_ALONG_RIVER").c_str(), info.getRiverSideYieldChangeArray());

		for (int iTech = 0; iTech < GC.getNumTechInfos(); iTech++)
		{
			for (int iYield = 0; iYield < NUM_YIELD_TYPES; iYield++)
			{
				if (0 != info.getTechYieldChanges(iTech, iYield))
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_WITH_TECH", info.getTechYieldChanges(iTech, iYield), GC.getYieldInfo((YieldTypes)iYield).getChar(), GC.getTechInfo((TechTypes)iTech).getTextKeyWide()));
				}
			}
		}

		//	Civics
		for (int iYield = 0; iYield < NUM_YIELD_TYPES; iYield++)
		{
			for (int iCivic = 0; iCivic < GC.getNumCivicInfos(); iCivic++)
			{
				int iChange = GC.getCivicInfo((CivicTypes)iCivic).getImprovementYieldChanges(eImprovement, iYield);
				if (0 != iChange)
				{
					szTempBuffer.Format( SETCOLR L"%s" ENDCOLR , TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getCivicInfo((CivicTypes)iCivic).getDescription());
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_CIVIC_IMPROVEMENT_YIELD_CHANGE", iChange, GC.getYieldInfo((YieldTypes)iYield).getChar()));
					szBuffer.append(szTempBuffer);
				}
			}
		}
	}

	if (info.isRequiresRiverSide())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_REQUIRES_RIVER"));
	}
	if (info.isCarriesIrrigation())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_CARRIES_IRRIGATION"));
	}
	if (bCivilopediaText)
	{
		if (info.isNoFreshWater())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_NO_BUILD_FRESH_WATER"));
		}
		if (info.isWater())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_BUILD_ONLY_WATER"));
		}
		if (info.isRequiresFlatlands())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_ONLY_BUILD_FLATLANDS"));
		}
	}

	if (info.getImprovementUpgrade() != NO_IMPROVEMENT)
	{
		iTurns = GC.getGameINLINE().getImprovementUpgradeTime(eImprovement);

		szBuffer.append(NEWLINE);

//FfH: Modified by Kael 05/24/2008
//		szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_EVOLVES", GC.getImprovementInfo((ImprovementTypes) info.getImprovementUpgrade()).getTextKeyWide(), iTurns));
        if (GC.getImprovementInfo((ImprovementTypes) GC.getImprovementInfo(eImprovement).getImprovementUpgrade()).getPrereqCivilization() == NO_CIVILIZATION)
        {
            szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_EVOLVES", GC.getImprovementInfo((ImprovementTypes) info.getImprovementUpgrade()).getTextKeyWide(), iTurns));
        }
        else
        {
            szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_EVOLVES_PREREQ_CIV", GC.getImprovementInfo((ImprovementTypes) GC.getImprovementInfo(eImprovement).getImprovementUpgrade()).getTextKeyWide(), iTurns, GC.getCivilizationInfo((CivilizationTypes)GC.getImprovementInfo((ImprovementTypes)GC.getImprovementInfo(eImprovement).getImprovementUpgrade()).getPrereqCivilization()).getDescription()));
        }
//FfH: End Modify
		// Super Forts begin *text* *upgrade*
		if (info.isUpgradeRequiresFortify())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_FORTIFY_TO_UPGRADE"));
		}
		// Super Forts end
	}

	int iLast = -1;
	for (int iBonus = 0; iBonus < GC.getNumBonusInfos(); iBonus++)
	{
		int iRand = info.getImprovementBonusDiscoverRand(iBonus);
		if (iRand > 0)
		{

//FfH: Modified by Kael 1/27/2010
//			szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_IMPROVEMENT_CHANCE_DISCOVER").c_str());
			szFirstBuffer.Format(L"%s%s", NEWLINE, gDLL->getText("TXT_KEY_IMPROVEMENT_CHANCE_DISCOVER", iRand).c_str());
//FfH: End Modify

			szTempBuffer.Format(L"%c", GC.getBonusInfo((BonusTypes) iBonus).getChar());
			setListHelp(szBuffer, szFirstBuffer, szTempBuffer, L", ", iRand != iLast);
			iLast = iRand;
		}
	}

	if (0 != info.getDefenseModifier())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_DEFENSE_MODIFIER", info.getDefenseModifier()));
	}

	if (0 != info.getHappiness())
	{
		szBuffer.append(NEWLINE);
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       08/28/09                             jdog5000         */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ICON_CHANGE_NEARBY_CITIES", info.getHappiness(), (info.getHappiness() > 0 ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR))));
*/
		// Use absolute value with unhappy face
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ICON_CHANGE_NEARBY_CITIES", abs(info.getHappiness()), (info.getHappiness() > 0 ? gDLL->getSymbolID(HAPPY_CHAR) : gDLL->getSymbolID(UNHAPPY_CHAR))));
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
	}

	if (info.isActsAsCity())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_DEFENSE_MODIFIER_EXTRA"));
	}

	if (info.getFeatureGrowthProbability() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_MORE_GROWTH"));
	}
	else if (info.getFeatureGrowthProbability() < 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_LESS_GROWTH"));
	}

	// Super Forts begin *text* *bombard*
	if (info.isBombardable() && (info.getDefenseModifier() > 0))
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_BOMBARD"));
	}
	if (info.getUniqueRange() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_UNIQUE_RANGE", info.getUniqueRange()));
	}
	// Super Forts end

//FfH: Added by Kael 05/12/2008
	if (info.isUnique())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_UNIQUE"));
	}

	for (int iI = 0; iI < GC.getNumBonusInfos(); iI++)
	{
		if (GC.getBonusInfo((BonusTypes)iI).getBonusClassType() != GC.getInfoTypeForString("BONUSCLASS_RAWMANA"))
		{
			if (info.isImprovementBonusMakesValid(iI))
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_PEDIA_IMPROVEMENT_BONUS", GC.getBonusInfo((BonusTypes)iI).getTextKeyWide()));
			}
		}
	}
	
	if (info.getPrereqCivilization() != NO_CIVILIZATION)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_PREREQ_CIVILIZATION", GC.getCivilizationInfo((CivilizationTypes)info.getPrereqCivilization()).getDescription()));
	}
	if (info.getHealRateChange() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_HEAL_RATE_CHANGE", info.getHealRateChange()));
	}
	if (info.getRangeDefenseModifier() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_RANGE_DEFENSE_MODIFIER", info.getRangeDefenseModifier(), info.getRange()));
	}
	if (info.getVisibilityChange() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_VISIBILITY_CHANGE", info.getVisibilityChange()));
	}
	if (info.getSpawnUnitType() != NO_UNIT)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_SPAWN_UNIT_TYPE", GC.getUnitInfo((UnitTypes)info.getSpawnUnitType()).getDescription()));
	}
	if (!CvWString(info.getHelp()).empty())
    {
        szBuffer.append(NEWLINE);
        szBuffer.append(info.getHelp());
    }
//FfH: End Add

	if (bCivilopediaText)
	{
		// Super Forts begin *text*
		if (info.getCulture() > 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_PLOT_CULTURE", info.getCulture()));
		}
		if (info.getCultureRange() > 0 && ((info.getCulture() > 0) || info.isActsAsCity()))
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_CULTURE_RANGE", info.getCultureRange()));
		}
		if (info.getSeeFrom() > 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_SEE_FROM", info.getSeeFrom()));
		}
		// Super Forts end
		if (info.getPillageGold() > 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_IMPROVEMENT_PILLAGE_YIELDS", info.getPillageGold()));
		}
	}
}


void CvGameTextMgr::getDealString(CvWStringBuffer& szBuffer, CvDeal& deal, PlayerTypes ePlayerPerspective)
{
	PlayerTypes ePlayer1 = deal.getFirstPlayer();
	PlayerTypes ePlayer2 = deal.getSecondPlayer();

	const CLinkList<TradeData>* pListPlayer1 = deal.getFirstTrades();
	const CLinkList<TradeData>* pListPlayer2 = deal.getSecondTrades();

	getDealString(szBuffer, ePlayer1, ePlayer2, pListPlayer1,  pListPlayer2, ePlayerPerspective);
}

void CvGameTextMgr::getDealString(CvWStringBuffer& szBuffer, PlayerTypes ePlayer1, PlayerTypes ePlayer2, const CLinkList<TradeData>* pListPlayer1, const CLinkList<TradeData>* pListPlayer2, PlayerTypes ePlayerPerspective)
{
	if (NO_PLAYER == ePlayer1 || NO_PLAYER == ePlayer2)
	{
		FAssertMsg(false, "Deal needs two parties");
		return;
	}

	CvWStringBuffer szDealOne;
	if (NULL != pListPlayer1 && pListPlayer1->getLength() > 0)
	{
		CLLNode<TradeData>* pTradeNode;
		bool bFirst = true;
		for (pTradeNode = pListPlayer1->head(); pTradeNode; pTradeNode = pListPlayer1->next(pTradeNode))
		{
			CvWStringBuffer szTrade;
			getTradeString(szTrade, pTradeNode->m_data, ePlayer1, ePlayer2);
			setListHelp(szDealOne, L"", szTrade.getCString(), L", ", bFirst);
			bFirst = false;
		}
	}

	CvWStringBuffer szDealTwo;
	if (NULL != pListPlayer2 && pListPlayer2->getLength() > 0)
	{
		CLLNode<TradeData>* pTradeNode;
		bool bFirst = true;
		for (pTradeNode = pListPlayer2->head(); pTradeNode; pTradeNode = pListPlayer2->next(pTradeNode))
		{
			CvWStringBuffer szTrade;
			getTradeString(szTrade, pTradeNode->m_data, ePlayer2, ePlayer1);
			setListHelp(szDealTwo, L"", szTrade.getCString(), L", ", bFirst);
			bFirst = false;
		}
	}

	if (!szDealOne.isEmpty())
	{
		if (!szDealTwo.isEmpty())
		{
			if (ePlayerPerspective == ePlayer1)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_OUR_DEAL", szDealOne.getCString(), GET_PLAYER(ePlayer2).getNameKey(), szDealTwo.getCString()));
			}
			else if (ePlayerPerspective == ePlayer2)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_OUR_DEAL", szDealTwo.getCString(), GET_PLAYER(ePlayer1).getNameKey(), szDealOne.getCString()));
			}
			else
			{
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_DEAL", GET_PLAYER(ePlayer1).getNameKey(), szDealOne.getCString(), GET_PLAYER(ePlayer2).getNameKey(), szDealTwo.getCString()));
			}
		}
		else
		{
			if (ePlayerPerspective == ePlayer1)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_DEAL_ONESIDED_OURS", szDealOne.getCString(), GET_PLAYER(ePlayer2).getNameKey()));
			}
			else if (ePlayerPerspective == ePlayer2)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_DEAL_ONESIDED_THEIRS", szDealOne.getCString(), GET_PLAYER(ePlayer1).getNameKey()));
			}
			else
			{
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_DEAL_ONESIDED", GET_PLAYER(ePlayer1).getNameKey(), szDealOne.getCString(), GET_PLAYER(ePlayer2).getNameKey()));
			}
		}
	}
	else if (!szDealTwo.isEmpty())
	{
		if (ePlayerPerspective == ePlayer1)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_DEAL_ONESIDED_THEIRS", szDealTwo.getCString(), GET_PLAYER(ePlayer2).getNameKey()));
		}
		else if (ePlayerPerspective == ePlayer2)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_DEAL_ONESIDED_OURS", szDealTwo.getCString(), GET_PLAYER(ePlayer1).getNameKey()));
		}
		else
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_DEAL_ONESIDED", GET_PLAYER(ePlayer2).getNameKey(), szDealTwo.getCString(), GET_PLAYER(ePlayer1).getNameKey()));
		}
	}
}

void CvGameTextMgr::getWarplanString(CvWStringBuffer& szString, WarPlanTypes eWarPlan)
{
	switch (eWarPlan)
	{
		case WARPLAN_ATTACKED_RECENT: szString.assign(L"new defensive war"); break;
		case WARPLAN_ATTACKED: szString.assign(L"defensive war"); break;
		case WARPLAN_PREPARING_LIMITED: szString.assign(L"preparing limited war"); break;
		case WARPLAN_PREPARING_TOTAL: szString.assign(L"preparing total war"); break;
		case WARPLAN_LIMITED: szString.assign(L"limited war"); break;
		case WARPLAN_TOTAL: szString.assign(L"total war"); break;
		case WARPLAN_DOGPILE: szString.assign(L"dogpile war"); break;
		case NO_WARPLAN: szString.assign(L"unplanned war"); break;
		default:  szString.assign(L"unknown war"); break;
	}
}

void CvGameTextMgr::getAttitudeString(CvWStringBuffer& szBuffer, PlayerTypes ePlayer, PlayerTypes eTargetPlayer)
{
	CvWString szTempBuffer;
	int iAttitudeChange;
	int iPass;
	int iI;
	CvPlayerAI& kPlayer = GET_PLAYER(ePlayer);
	TeamTypes eTeam = (TeamTypes) kPlayer.getTeam();
	CvTeamAI& kTeam = GET_TEAM(eTeam);

	szBuffer.append(gDLL->getText("TXT_KEY_ATTITUDE_TOWARDS", GC.getAttitudeInfo(GET_PLAYER(ePlayer).AI_getAttitude(eTargetPlayer)).getTextKeyWide(), GET_PLAYER(eTargetPlayer).getNameKey()));

	for (int iTeam = 0; iTeam < MAX_TEAMS; iTeam++)
	{
		CvTeam& kLoopTeam = GET_TEAM((TeamTypes)iTeam);
		if (kLoopTeam.isAlive())
		{
			if (NO_PLAYER != eTargetPlayer)
			{
				CvTeam& kTargetTeam = GET_TEAM(GET_PLAYER(eTargetPlayer).getTeam());
				if (kTargetTeam.isHasMet((TeamTypes)iTeam))
				{
					if (kTeam.isVassal((TeamTypes)iTeam))
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_ATTITUDE_VASSAL_OF", kLoopTeam.getName().GetCString()));
						// MNAI - Puppet States
						if (GET_PLAYER(ePlayer).isPuppetState())
						{
							szBuffer.append(" (Puppet State)");
						}
						// MNAI - End Puppet States
						else
						{
							setVassalRevoltHelp(szBuffer, (TeamTypes)iTeam, kTeam.getID());
						}
					}
					else if (kLoopTeam.isVassal(kTeam.getID()))
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_ATTITUDE_MASTER_OF", kLoopTeam.getName().GetCString()));
					}
				}
			}
		}
	}

	for (iPass = 0; iPass < 2; iPass++)
	{
		iAttitudeChange = kPlayer.AI_getCloseBordersAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_LAND_TARGET", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

		iAttitudeChange = kPlayer.AI_getWarAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_WAR", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

		iAttitudeChange = kPlayer.AI_getPeaceAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_PEACE", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

		iAttitudeChange = kPlayer.AI_getSameReligionAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_SAME_RELIGION", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

		iAttitudeChange = kPlayer.AI_getDifferentReligionAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_DIFFERENT_RELIGION", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

		iAttitudeChange = kPlayer.AI_getBonusTradeAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_BONUS_TRADE", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

		iAttitudeChange = kPlayer.AI_getOpenBordersAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_OPEN_BORDERS", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

		iAttitudeChange = kPlayer.AI_getDefensivePactAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_DEFENSIVE_PACT", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

		iAttitudeChange = kPlayer.AI_getRivalDefensivePactAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_RIVAL_DEFENSIVE_PACT", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

		iAttitudeChange = kPlayer.AI_getRivalVassalAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_RIVAL_VASSAL", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

		iAttitudeChange = kPlayer.AI_getShareWarAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_SHARE_WAR", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

		iAttitudeChange = kPlayer.AI_getFavoriteCivicAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_FAVORITE_CIVIC", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

		iAttitudeChange = kPlayer.AI_getTradeAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_TRADE", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

		iAttitudeChange = kPlayer.AI_getRivalTradeAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_RIVAL_TRADE", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

		iAttitudeChange = GET_PLAYER(ePlayer).AI_getColonyAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_FREEDOM", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

		iAttitudeChange = GET_PLAYER(ePlayer).AI_getAttitudeExtra(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText(((iAttitudeChange > 0) ? "TXT_KEY_MISC_ATTITUDE_EXTRA_GOOD" : "TXT_KEY_MISC_ATTITUDE_EXTRA_BAD"), iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

/************************************************************************************************/
/* Advanced Diplomacy         START                                                             */
/************************************************************************************************/	
		/*
		for (iI = 0; iI < GC.getNumCivicInfos(); iI++)
		{
			iAttitudeChange = GET_PLAYER(ePlayer).AI_getCondemnCivicAttitude(eTargetPlayer, (CivicTypes)iI);
			if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
			{
				szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_CONDEMNED_CIVIC", iAttitudeChange, GC.getCivicInfo((CivicTypes)iI).getDescription()).GetCString());
				szBuffer.append(NEWLINE);
				szBuffer.append(szTempBuffer);
			}
		}
		*/
		
		iAttitudeChange = GET_PLAYER(ePlayer).AI_getSharedEnemyAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_SHARED_ENEMY", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}
		
		iAttitudeChange = GET_PLAYER(ePlayer).AI_getSharedFriendAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_SHARED_FRIEND", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}				
/************************************************************************************************/
/* Advanced Diplomacy         END                                                             */
/************************************************************************************************/

//FfH: Added by Kael 08/15/2007
		iAttitudeChange = kPlayer.AI_getAlignmentAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_ALIGNMENT", iAttitudeChange, GC.getAlignmentInfo((AlignmentTypes)GET_PLAYER(eTargetPlayer).getAlignment()).getDescription()).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}
        for (iI = 0; iI < GC.getNumBonusInfos(); iI++)
        {
            if (GET_PLAYER(eTargetPlayer).hasBonus((BonusTypes)iI))
            {
                iAttitudeChange = GC.getBonusInfo((BonusTypes)iI).getBadAttitude() * GC.getLeaderHeadInfo(kPlayer.getPersonalityType()).getAttitudeBadBonus();
                if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
                {
                    szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_BAD_BONUS", iAttitudeChange, GC.getBonusInfo((BonusTypes)iI).getDescription()).GetCString());
                    szBuffer.append(NEWLINE);
                    szBuffer.append(szTempBuffer);
                }
            }
        }
/************************************************************************************************/
/* Advanced Diplomacy         END                                                             */
/************************************************************************************************/
		/*
		for (iI = 0; iI < NUM_MEMORY_TYPES; ++iI)
		{
			iAttitudeChange = kPlayer.AI_getMemoryAttitude(eTargetPlayer, ((MemoryTypes)iI));
			if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
			{
				szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_MEMORY", iAttitudeChange, GC.getMemoryInfo((MemoryTypes)iI).getDescription()).GetCString());
				szBuffer.append(NEWLINE);
				szBuffer.append(szTempBuffer);
			}
		}
		*/
		
// FFH Start
		iAttitudeChange = GET_PLAYER(ePlayer).AI_getFavoriteWonderAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_FAVORITE_WONDER", iAttitudeChange, GC.getBuildingInfo((BuildingTypes)GC.getLeaderHeadInfo(GET_PLAYER(ePlayer).getPersonalityType()).getFavoriteWonder()).getTextKeyWide()).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}
		iAttitudeChange = GET_PLAYER(ePlayer).AI_getGenderAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText(((iAttitudeChange > 0) ? "TXT_KEY_MISC_ATTITUDE_GENDER_GOOD" : "TXT_KEY_MISC_ATTITUDE_GENDER_BAD"), iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}
		iAttitudeChange = GET_PLAYER(ePlayer).AI_getTrustAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_TRUST", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}
		iAttitudeChange = GET_PLAYER(ePlayer).AI_getCivicShareAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_CIVIC_SHARE", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}
//FfH: End Add

		// MNAI - Puppet States
		iAttitudeChange = GET_PLAYER(ePlayer).AI_getPuppetAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText(((iAttitudeChange > 0) ? "TXT_KEY_MISC_ATTITUDE_PUPPET_GOOD" : "TXT_KEY_MISC_ATTITUDE_PUPPET_BAD"), iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}
		// MNAI - End Puppet States

/*************************************************************************************************/
/** Advanced Diplomacy       START                                                  			 */
/*************************************************************************************************/
		// start bonus to Diplomacy from Limited Borders
		iAttitudeChange = kPlayer.AI_getLimitedBordersAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_RIGHT_PASSAGE", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}
		
		// start bonus to Diplomacy from Embassy
		iAttitudeChange = kPlayer.AI_getEmbassyAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_EMBASSY", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}

		// start bonus to Diplomacy from Free Trade Agreement
		iAttitudeChange = kPlayer.AI_getFreeTradeAgreementAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_FREE_TRADE_AGREEMENT", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}
		
		// start bonus to Diplomacy from NonAggression Pact
		iAttitudeChange = kPlayer.AI_getNonAggressionAttitude(eTargetPlayer);
		if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
		{
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_NON_AGGRESSION", iAttitudeChange).GetCString());
			szBuffer.append(NEWLINE);
			szBuffer.append(szTempBuffer);
		}
// END Advanced Diplomacy

		for (iI = 0; iI < NUM_MEMORY_TYPES; ++iI)
		{
			iAttitudeChange = kPlayer.AI_getMemoryAttitude(eTargetPlayer, ((MemoryTypes)iI));
//FfH Card Game: Added by Sto 08/17/2008
			if (iI == MEMORY_SOMNIUM_POSITIVE)
			{
				if ((iAttitudeChange > 0) && (iPass == 0))
				{
					szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_POSITIVE_TEXT"), gDLL->getText("TXT_KEY_MEMORY_SOMNIUM_POSITIVE", iAttitudeChange).GetCString());
					szBuffer.append(NEWLINE);
					szBuffer.append(szTempBuffer);
				}
			}
			else if (iI == MEMORY_SOMNIUM_NEGATIVE)
			{
				if ((iAttitudeChange < 0) && (iPass == 1))
				{
					szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MEMORY_SOMNIUM_NEGATIVE", iAttitudeChange).GetCString());
					szBuffer.append(NEWLINE);
					szBuffer.append(szTempBuffer);
				}
			}
			else if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
			//if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
//FfH: End Add
			{
				szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_MEMORY", iAttitudeChange, GC.getMemoryInfo((MemoryTypes)iI).getDescription()).GetCString());
				szBuffer.append(NEWLINE);
				szBuffer.append(szTempBuffer);
			}
		}

		// Hidden Attitude: Show additional attitude modifiers // glider1 02/10
		if (getBugOptionBOOL("MiscHover__LeaderheadHiddenAttitude", true, "BUG_LEADERHEAD_HOVER_HIDDEN_ATTITUDE"))
		{
			iAttitudeChange = kPlayer.AI_getBetterRankDifferenceAttitude(eTargetPlayer);
			if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
			{
				szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_BETTER_RANK", iAttitudeChange).GetCString());
				szBuffer.append(NEWLINE);
				szBuffer.append(szTempBuffer);
			}

			iAttitudeChange = kPlayer.AI_getWorseRankDifferenceAttitude(eTargetPlayer);
			if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
			{
				szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_WORSE_RANK", iAttitudeChange).GetCString());
				szBuffer.append(NEWLINE);
				szBuffer.append(szTempBuffer);
			}

			iAttitudeChange = kPlayer.AI_getLowRankAttitude(eTargetPlayer);
			if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
			{
				szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_LOW_RANK", iAttitudeChange).GetCString());
				szBuffer.append(NEWLINE);
				szBuffer.append(szTempBuffer);
			}

			iAttitudeChange = kPlayer.AI_getLostWarAttitude(eTargetPlayer);
			if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
			{
				szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_LOST_WAR", iAttitudeChange).GetCString());
				szBuffer.append(NEWLINE);
				szBuffer.append(szTempBuffer);
			}

			iAttitudeChange = kPlayer.AI_getTeamSizeAttitude(eTargetPlayer);
			if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
			{
				szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_TEAM_SIZE", iAttitudeChange).GetCString());
				szBuffer.append(NEWLINE);
				szBuffer.append(szTempBuffer);
			}

			iAttitudeChange = kPlayer.AI_getFirstImpressionAttitude(eTargetPlayer);
			if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
			{
				szTempBuffer.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR((iAttitudeChange > 0) ? "COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"), gDLL->getText("TXT_KEY_MISC_ATTITUDE_FIRST_IMPRESSION", iAttitudeChange).GetCString());
				szBuffer.append(NEWLINE);
				szBuffer.append(szTempBuffer);
			}
		} // End Hidden Attitude
	}

	if (NO_PLAYER != eTargetPlayer)
	{
		int iWarWeariness = GET_PLAYER(eTargetPlayer).getModifiedWarWearinessPercentAnger(GET_TEAM(GET_PLAYER(eTargetPlayer).getTeam()).getWarWeariness(eTeam) * std::max(0, 100 + kTeam.getEnemyWarWearinessModifier()));
		if (iWarWeariness / 10000 > 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_WAR_WEAR_HELP", iWarWeariness / 10000));
		}
	}
	
	// lfgr: Display no diplo (Crusade) info
	if( GET_TEAM( GET_PLAYER(ePlayer).getTeam() ).isAtWar( GET_PLAYER(eTargetPlayer).getTeam() ) )
	{
		if( GET_PLAYER( eTargetPlayer ).isNoDiplomacyWithEnemies() )
		{
			szBuffer.append( NEWLINE );
			if ( eTargetPlayer == GC.getGameINLINE().getActivePlayer() )
				szBuffer.append( gDLL->getText("TXT_KEY_MISC_NO_DIPLO_WITH_ENEMIES_YOU") );
			else
				szBuffer.append( gDLL->getText( "TXT_KEY_MISC_NO_DIPLO_WITH_ENEMIES_PLAYER", GET_PLAYER( eTargetPlayer ).getName() ) );
			
		}
		if( GET_PLAYER( ePlayer ).isNoDiplomacyWithEnemies() )
		{
			szBuffer.append( NEWLINE );
			szBuffer.append( gDLL->getText("TXT_KEY_MISC_NO_DIPLO_WITH_ENEMIES_OTHER") );
		}
	}
	// lfgr end
}

void CvGameTextMgr::getEspionageString(CvWStringBuffer& szBuffer, PlayerTypes ePlayer, PlayerTypes eTargetPlayer)
{
	if (!GC.getGameINLINE().isOption(GAMEOPTION_NO_ESPIONAGE))
	{
		CvPlayer& kPlayer = GET_PLAYER(ePlayer);
		TeamTypes eTeam = (TeamTypes) kPlayer.getTeam();
		CvTeam& kTeam = GET_TEAM(eTeam);
		CvPlayer& kTargetPlayer = GET_PLAYER(eTargetPlayer);

		szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_AGAINST_PLAYER", kTargetPlayer.getNameKey(), kTeam.getEspionagePointsAgainstTeam(kTargetPlayer.getTeam()), GET_TEAM(kTargetPlayer.getTeam()).getEspionagePointsAgainstTeam(kPlayer.getTeam())));
	}
}

void CvGameTextMgr::getTradeString(CvWStringBuffer& szBuffer, const TradeData& tradeData, PlayerTypes ePlayer1, PlayerTypes ePlayer2)
{
	switch (tradeData.m_eItemType)
	{
	case TRADE_GOLD:
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_GOLD", tradeData.m_iData));
		break;
	case TRADE_GOLD_PER_TURN:
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_GOLD_PER_TURN", tradeData.m_iData));
		break;
	case TRADE_MAPS:
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_WORLD_MAP"));
		break;
	case TRADE_SURRENDER:
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_CAPITULATE"));
		break;
	case TRADE_VASSAL:
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_VASSAL"));
		break;
	case TRADE_OPEN_BORDERS:
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_OPEN_BORDERS"));
		break;
	case TRADE_DEFENSIVE_PACT:
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_DEFENSIVE_PACT"));
		break;
/*************************************************************************************************/
/** Advanced Diplomacy       START                                                  			 */
/*************************************************************************************************/
	case TRADE_NON_AGGRESSION:
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_NON_AGGRESSION"));
		break;
	case TRADE_POW:
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_POW"));
		break;
/*************************************************************************************************/
/** Advanced Diplomacy       END	                                                  			 */
/*************************************************************************************************/
	case TRADE_PERMANENT_ALLIANCE:
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_PERMANENT_ALLIANCE"));
		break;
	case TRADE_PEACE_TREATY:
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_PEACE_TREATY", GC.getDefineINT("PEACE_TREATY_LENGTH")));
		break;
	case TRADE_TECHNOLOGIES:
		szBuffer.assign(CvWString::format(L"%s", GC.getTechInfo((TechTypes)tradeData.m_iData).getDescription()));
		break;
	case TRADE_RESOURCES:
		szBuffer.assign(CvWString::format(L"%s", GC.getBonusInfo((BonusTypes)tradeData.m_iData).getDescription()));
		break;
	case TRADE_CITIES:
		szBuffer.assign(CvWString::format(L"%s", GET_PLAYER(ePlayer1).getCity(tradeData.m_iData)->getName().GetCString()));
		break;
	case TRADE_PEACE:
	case TRADE_WAR:
/************************************************************************************************/
/* Afforess	                  Start		 06/16/10                                               */
/* Advanced Diplomacy                                                                           */
/************************************************************************************************/
	case TRADE_WAR_PREPARE:
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_PREPARE_WAR"));
		break;
	case TRADE_CONTACT:
/************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/************************************************************************************************/
	case TRADE_EMBARGO:
		szBuffer.assign(CvWString::format(L"%s", GET_TEAM((TeamTypes)tradeData.m_iData).getName().GetCString()));
		break;
	case TRADE_CIVIC:
		szBuffer.assign(CvWString::format(L"%s", GC.getCivicInfo((CivicTypes)tradeData.m_iData).getDescription()));
		break;
	case TRADE_RELIGION:
		szBuffer.assign(CvWString::format(L"%s", GC.getReligionInfo((ReligionTypes)tradeData.m_iData).getDescription()));
		break;
/************************************************************************************************/
/* Afforess	                  Start		 06/16/10                                               */
/* Advanced Diplomacy                                                                           */
/************************************************************************************************/
	case TRADE_WORKER:
	case TRADE_MILITARY_UNIT:
		szBuffer.assign(CvWString::format(L"%s", GET_PLAYER(ePlayer1).getUnit(tradeData.m_iData)->getName().GetCString()));
		break;
	case TRADE_EMBASSY:
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_EMBASSY"));
		break;
	case TRADE_CORPORATION:
		szBuffer.assign(CvWString::format(L"%s", GC.getCorporationInfo((CorporationTypes)tradeData.m_iData).getDescription()));
		break;
	case TRADE_SECRETARY_GENERAL_VOTE:
		szBuffer.assign(CvWString::format(L"%s", GC.getVoteSourceInfo((VoteSourceTypes)tradeData.m_iData).getDescription()));
		break;
	case TRADE_RIGHT_OF_PASSAGE:
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_LIMITED_BORDERS"));
		break;
	case TRADE_FREE_TRADE_ZONE:
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_FREE_TRADE_ZONE"));
		break;
	case TRADE_WAR_REPARATIONS:
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_WAR_REPARATIONS"));
		break;
/************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/************************************************************************************************/
	default:
		FAssert(false);
		break;
	}
}

void CvGameTextMgr::setFeatureHelp(CvWStringBuffer &szBuffer, FeatureTypes eFeature, bool bCivilopediaText)
{
	if (NO_FEATURE == eFeature)
	{
		return;
	}
	CvFeatureInfo& feature = GC.getFeatureInfo(eFeature);

	int aiYields[NUM_YIELD_TYPES];
	if (!bCivilopediaText)
	{
		szBuffer.append(feature.getDescription());

		for (int iI = 0; iI < NUM_YIELD_TYPES; ++iI)
		{
			aiYields[iI] = feature.getYieldChange(iI);
		}
		setYieldChangeHelp(szBuffer, L"", L"", L"", aiYields);
	}
	for (int iI = 0; iI < NUM_YIELD_TYPES; ++iI)
	{
		aiYields[iI] = feature.getRiverYieldChange(iI);
	}
	setYieldChangeHelp(szBuffer, L"", L"", gDLL->getText("TXT_KEY_TERRAIN_NEXT_TO_RIVER"), aiYields);

	for (int iI = 0; iI < NUM_YIELD_TYPES; ++iI)
	{
		aiYields[iI] = feature.getHillsYieldChange(iI);
	}
	setYieldChangeHelp(szBuffer, L"", L"", gDLL->getText("TXT_KEY_TERRAIN_ON_HILLS"), aiYields);

	if (feature.getMovementCost() != 1)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_TERRAIN_MOVEMENT_COST", feature.getMovementCost()));
	}

	CvWString szHealth;
	szHealth.Format(L"%.2f", 0.01f * abs(feature.getHealthPercent()));
	if (feature.getHealthPercent() > 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_FEATURE_GOOD_HEALTH", szHealth.GetCString()));
	}
	else if (feature.getHealthPercent() < 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_FEATURE_BAD_HEALTH", szHealth.GetCString()));
	}

	if (feature.getDefenseModifier() != 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_TERRAIN_DEFENSE_MODIFIER", feature.getDefenseModifier()));
	}

/*************************************************************************************************/
/* UNOFFICIAL_PATCH                       06/02/10                           LunarMongoose       */
/*                                                                                               */
/* Bugfix                                                                                        */
/*************************************************************************************************/
	// Mongoose FeatureDamageFix
	if (feature.getTurnDamage() > 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_TERRAIN_TURN_DAMAGE", feature.getTurnDamage()));
	}
	else if (feature.getTurnDamage() < 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_TERRAIN_TURN_HEALING", -feature.getTurnDamage()));
	}
/*************************************************************************************************/
/* UNOFFICIAL_PATCH                         END                                                  */
/*************************************************************************************************/


	if (feature.isAddsFreshWater())
	{
		szBuffer.append(gDLL->getText("TXT_KEY_FEATURE_ADDS_FRESH_WATER"));
	}

	if (feature.isImpassable())
	{
		szBuffer.append(gDLL->getText("TXT_KEY_TERRAIN_IMPASSABLE"));
	}

	if (feature.isNoCity())
	{
		szBuffer.append(gDLL->getText("TXT_KEY_TERRAIN_NO_CITIES"));
	}

	if (feature.isNoImprovement())
	{
		szBuffer.append(gDLL->getText("TXT_KEY_FEATURE_NO_IMPROVEMENT"));
	}

	if (feature.isFlammable())
	{
		szBuffer.append(gDLL->getText("TXT_KEY_FEATURE_FLAMMABLE"));
	}

}


void CvGameTextMgr::setTerrainHelp(CvWStringBuffer &szBuffer, TerrainTypes eTerrain, bool bCivilopediaText)
{
	if (NO_TERRAIN == eTerrain)
	{
		return;
	}
	CvTerrainInfo& terrain = GC.getTerrainInfo(eTerrain);

	int aiYields[NUM_YIELD_TYPES];
	if (!bCivilopediaText)
	{
		szBuffer.append(terrain.getDescription());

		for (int iI = 0; iI < NUM_YIELD_TYPES; ++iI)
		{
			aiYields[iI] = terrain.getYield(iI);
		}
		setYieldChangeHelp(szBuffer, L"", L"", L"", aiYields);
	}
	for (int iI = 0; iI < NUM_YIELD_TYPES; ++iI)
	{
		aiYields[iI] = terrain.getRiverYieldChange(iI);
	}
	setYieldChangeHelp(szBuffer, L"", L"", gDLL->getText("TXT_KEY_TERRAIN_NEXT_TO_RIVER"), aiYields);
	for (int iI = 0; iI < NUM_YIELD_TYPES; ++iI)
	{
		aiYields[iI] = terrain.getHillsYieldChange(iI);
	}
	setYieldChangeHelp(szBuffer, L"", L"", gDLL->getText("TXT_KEY_TERRAIN_ON_HILLS"), aiYields);

/*************************************************************************************************/
/**	CivPlotMods								03/23/09								Jean Elcard	**/
/**																								**/
/**				Terrain Help for Civilization-specific Terrain Yield Modifications.				**/
/*************************************************************************************************/
	for (int iCivilization = 0; iCivilization < GC.getNumCivilizationInfos(); iCivilization++)
	{
		for (int iYield = 0; iYield < NUM_YIELD_TYPES; iYield++)
		{
			int iChange = GC.getCivilizationInfo((CivilizationTypes)iCivilization).getTerrainYieldChanges(eTerrain, iYield, false);
			int iChangeRiver = GC.getCivilizationInfo((CivilizationTypes)iCivilization).getTerrainYieldChanges(eTerrain, iYield, true);

			if (iChange != 0)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_CIV_TERRAIN_MOD_PEDIA", iChange, GC.getYieldInfo((YieldTypes)iYield).getChar(), GC.getCivilizationInfo((CivilizationTypes)iCivilization).getDescription()));
			}
			if (iChangeRiver != 0 && iChangeRiver != iChange)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_CIV_TERRAIN_RIVER_MOD_PEDIA", iChangeRiver - iChange, GC.getYieldInfo((YieldTypes)iYield).getChar(), GC.getCivilizationInfo((CivilizationTypes)iCivilization).getDescription()));
			}
		}
	}
/*************************************************************************************************/
/**	CivPlotMods								END													**/
/*************************************************************************************************/
	if (terrain.getMovementCost() != 1)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_TERRAIN_MOVEMENT_COST", terrain.getMovementCost()));
	}

	if (terrain.getBuildModifier() != 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_TERRAIN_BUILD_MODIFIER", terrain.getBuildModifier()));
	}

	if (terrain.getDefenseModifier() != 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_TERRAIN_DEFENSE_MODIFIER", terrain.getDefenseModifier()));
	}

	if (terrain.isImpassable())
	{
		szBuffer.append(gDLL->getText("TXT_KEY_TERRAIN_IMPASSABLE"));
	}
	if (!terrain.isFound())
	{
		szBuffer.append(gDLL->getText("TXT_KEY_TERRAIN_NO_CITIES"));
		bool bFirst = true;
		if (terrain.isFoundCoast())
		{
			szBuffer.append(gDLL->getText("TXT_KEY_TERRAIN_COASTAL_CITIES"));
			bFirst = false;
		}
		if (!bFirst)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_OR"));
		}
		if (terrain.isFoundFreshWater())
		{
			szBuffer.append(gDLL->getText("TXT_KEY_TERRAIN_FRESH_WATER_CITIES"));
			bFirst = false;
		}
	}
}

// BUG - Finance Advisor - start
void CvGameTextMgr::buildFinanceSpecialistGoldString(CvWStringBuffer& szBuffer, PlayerTypes ePlayer)
{
	if (NO_PLAYER == ePlayer)
	{
		return;
	}
	CvPlayer& player = GET_PLAYER(ePlayer);

	int* iCounts = new int[GC.getNumSpecialistInfos()];
	for (int iI = 0; iI < GC.getNumSpecialistInfos(); iI++)
	{
		iCounts[iI] = 0;
	}
	int iIter;
	for (CvCity* pCity = player.firstCity(&iIter); NULL != pCity; pCity = player.nextCity(&iIter))
	{
		if (!pCity->isDisorder())
		{
			for (int iI = 0; iI < GC.getNumSpecialistInfos(); iI++)
			{
				iCounts[iI] += pCity->getSpecialistCount((SpecialistTypes)iI) + pCity->getFreeSpecialistCount((SpecialistTypes)iI);
			}
		}
	}
	
	bool bFirst = true;
	int iTotal = 0;
	for (int iI = 0; iI < GC.getNumSpecialistInfos(); iI++)
	{
		int iGold = iCounts[iI] * player.specialistCommerce((SpecialistTypes)iI, COMMERCE_GOLD);
		if (iGold != 0)
		{
			if (bFirst)
			{
				szBuffer.append(NEWLINE);
				bFirst = false;
			}
			szBuffer.append(gDLL->getText("TXT_KEY_BUG_FINANCIAL_ADVISOR_SPECIALIST_GOLD", iGold, iCounts[iI], GC.getSpecialistInfo((SpecialistTypes)iI).getDescription()));
			iTotal += iGold;
		}
	}

	szBuffer.append(gDLL->getText("TXT_KEY_BUG_FINANCIAL_ADVISOR_SPECIALIST_TOTAL_GOLD", iTotal));
	SAFE_DELETE_ARRAY(iCounts);
}
// BUG - Finance Advisor - end

void CvGameTextMgr::buildFinanceInflationString(CvWStringBuffer& szBuffer, PlayerTypes ePlayer)
{
	if (NO_PLAYER == ePlayer)
	{
		return;
	}
	CvPlayer& kPlayer = GET_PLAYER(ePlayer);

	int iInflationRate = kPlayer.calculateInflationRate();
	if (iInflationRate != 0)
	{
		int iPreInflation = kPlayer.calculatePreInflatedCosts();
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_FINANCE_ADVISOR_INFLATION", iPreInflation, iInflationRate, iInflationRate, iPreInflation, (iPreInflation * iInflationRate) / 100));
	}
}

void CvGameTextMgr::buildFinanceUnitCostString(CvWStringBuffer& szBuffer, PlayerTypes ePlayer)
{
	if (NO_PLAYER == ePlayer)
	{
		return;
	}
	CvPlayer& player = GET_PLAYER(ePlayer);

	int iFreeUnits = 0;
	int iFreeMilitaryUnits = 0;
	int iUnits = player.getNumUnits();
	int iMilitaryUnits = player.getNumMilitaryUnits();
	int iPaidUnits = iUnits;
	int iPaidMilitaryUnits = iMilitaryUnits;
	int iMilitaryCost = 0;
	int iBaseUnitCost = 0;
	int iExtraCost = 0;
	int iCost = player.calculateUnitCost(iFreeUnits, iFreeMilitaryUnits, iPaidUnits, iPaidMilitaryUnits, iBaseUnitCost, iMilitaryCost, iExtraCost);
	int iHandicap = iCost-iBaseUnitCost-iMilitaryCost-iExtraCost;

	szBuffer.append(NEWLINE);
	szBuffer.append(gDLL->getText("TXT_KEY_FINANCE_ADVISOR_UNIT_COST", iPaidUnits, iFreeUnits, iBaseUnitCost));

	if (iPaidMilitaryUnits != 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_FINANCE_ADVISOR_UNIT_COST_2", iPaidMilitaryUnits, iFreeMilitaryUnits, iMilitaryCost));
	}
	if (iExtraCost != 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_FINANCE_ADVISOR_UNIT_COST_3", iExtraCost));
	}
	if (iHandicap != 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_FINANCE_ADVISOR_HANDICAP_COST", iHandicap));
	}
	szBuffer.append(gDLL->getText("TXT_KEY_FINANCE_ADVISOR_UNIT_COST_4", iCost));
}

void CvGameTextMgr::buildFinanceAwaySupplyString(CvWStringBuffer& szBuffer, PlayerTypes ePlayer)
{
	if (NO_PLAYER == ePlayer)
	{
		return;
	}
	CvPlayer& player = GET_PLAYER(ePlayer);

	int iPaidUnits = 0;
	int iBaseCost = 0;
	int iCost = player.calculateUnitSupply(iPaidUnits, iBaseCost);
	int iHandicap = iCost - iBaseCost;

	CvWString szHandicap;
	if (iHandicap != 0)
	{
		szHandicap = gDLL->getText("TXT_KEY_FINANCE_ADVISOR_HANDICAP_COST", iHandicap);
	}

	szBuffer.append(NEWLINE);
	szBuffer.append(gDLL->getText("TXT_KEY_FINANCE_ADVISOR_SUPPLY_COST", iPaidUnits, GC.getDefineINT("INITIAL_FREE_OUTSIDE_UNITS"), iBaseCost, szHandicap.GetCString(), iCost));
}

void CvGameTextMgr::buildFinanceCityMaintString(CvWStringBuffer& szBuffer, PlayerTypes ePlayer)
{
	if (NO_PLAYER == ePlayer)
	{
		return;
	}
	int iLoop;
	int iDistanceMaint = 0;
	int iColonyMaint = 0;
	int iCorporationMaint = 0;

	CvPlayer& player = GET_PLAYER(ePlayer);
	for (CvCity* pLoopCity = player.firstCity(&iLoop); pLoopCity != NULL; pLoopCity = player.nextCity(&iLoop))
	{
		if (!pLoopCity->isDisorder() && !pLoopCity->isWeLoveTheKingDay() && (pLoopCity->getPopulation() > 0)) //Fix by karadoc
		{
			iDistanceMaint += (pLoopCity->calculateDistanceMaintenanceTimes100() * std::max(0, (pLoopCity->getMaintenanceModifier() + 100))) / 100;
			iColonyMaint += (pLoopCity->calculateColonyMaintenanceTimes100() * std::max(0, (pLoopCity->getMaintenanceModifier() + 100))) / 100;
			iCorporationMaint += (pLoopCity->calculateCorporationMaintenanceTimes100() * std::max(0, (pLoopCity->getMaintenanceModifier() + 100))) / 100;
		}
	}
	iDistanceMaint /= 100;
	iColonyMaint /= 100;
	iCorporationMaint /= 100;

	int iNumCityMaint = player.getTotalMaintenance() - iDistanceMaint - iColonyMaint - iCorporationMaint;

	szBuffer.append(NEWLINE);
	szBuffer.append(gDLL->getText("TXT_KEY_FINANCE_ADVISOR_CITY_MAINT_COST", iDistanceMaint, iNumCityMaint, iColonyMaint, iCorporationMaint, player.getTotalMaintenance()));
}

void CvGameTextMgr::buildFinanceCivicUpkeepString(CvWStringBuffer& szBuffer, PlayerTypes ePlayer)
{
	if (NO_PLAYER == ePlayer)
	{
		return;
	}
	CvPlayer& player = GET_PLAYER(ePlayer);
	CvWString szCivicOptionCosts;
	for (int iI = 0; iI < GC.getNumCivicOptionInfos(); ++iI)
	{
		CivicTypes eCivic = player.getCivics((CivicOptionTypes)iI);
		if (NO_CIVIC != eCivic)
		{
			CvWString szTemp;
			szTemp.Format(L"%d%c: %s", player.getSingleCivicUpkeep(eCivic), GC.getCommerceInfo(COMMERCE_GOLD).getChar(),  GC.getCivicInfo(eCivic).getDescription());
			szCivicOptionCosts += NEWLINE + szTemp;
		}
	}

	szBuffer.append(NEWLINE);
	szBuffer.append(gDLL->getText("TXT_KEY_FINANCE_ADVISOR_CIVIC_UPKEEP_COST", szCivicOptionCosts.GetCString(), player.getCivicUpkeep()));
}

void CvGameTextMgr::buildFinanceForeignIncomeString(CvWStringBuffer& szBuffer, PlayerTypes ePlayer)
{
	if (NO_PLAYER == ePlayer)
	{
		return;
	}
	CvPlayer& player = GET_PLAYER(ePlayer);

	CvWString szPlayerIncome;
	for (int iI = 0; iI < MAX_PLAYERS; ++iI)
	{
		CvPlayer& otherPlayer = GET_PLAYER((PlayerTypes)iI);
		if (otherPlayer.isAlive() && player.getGoldPerTurnByPlayer((PlayerTypes)iI) != 0)
		{
			CvWString szTemp;
			szTemp.Format(L"%d%c: %s", player.getGoldPerTurnByPlayer((PlayerTypes)iI), GC.getCommerceInfo(COMMERCE_GOLD).getChar(), otherPlayer.getCivilizationShortDescription());
			szPlayerIncome += NEWLINE + szTemp;
		}
	}
	if (!szPlayerIncome.empty())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_FINANCE_ADVISOR_FOREIGN_INCOME", szPlayerIncome.GetCString(), player.getGoldPerTurn()));
	}
}

// BUG - Food Rate Hover - start

/*
	+14 from Worked Tiles
	+2 from Specialists
	+5 from Corporations
	+1 from Buildings
	----------------------- |
	Base Food Produced: 22  |-- only if there are modifiers
	+25% from Buildings     |
	-----------------------
	Total Food Produced: 27
	=======================
	+16 for Population
	+2 for Health
	-----------------------
	Total Food Consumed: 18
	=======================
	Net Food: +9            or
	Net Food for Settler: 9
	=======================
	* Lighthouse: +3
	* Supermarket: +1
*/
void CvGameTextMgr::setFoodHelp(CvWStringBuffer &szBuffer, CvCity& city)
{
	FAssertMsg(NO_PLAYER != city.getOwnerINLINE(), "City must have an owner");

	CvYieldInfo& info = GC.getYieldInfo(YIELD_FOOD);
	bool bNeedSubtotal = false;
	int iBaseRate = 0;
	int i;

	// Worked Tiles
	int iTileFood = 0;
	//for (i = 0; i < NUM_CITY_PLOTS; i++)
	for (i = 0; i < city.getNumCityPlots(); i++)
	{
		if (city.isWorkingPlot(i))
		{
			CvPlot* pPlot = city.getCityIndexPlot(i);

			if (pPlot != NULL)
			{
				iTileFood += pPlot->getYield(YIELD_FOOD);
			}
		}
	}
	if (iTileFood != 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_WORKED_TILES_YIELD", iTileFood, info.getChar()));
		iBaseRate += iTileFood;
	}

	// Trade
	int iTradeFood = city.getTradeYield(YIELD_FOOD);
	if (iTradeFood != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_SPECIALIST_COMMERCE", iTradeFood, info.getChar(), L"TXT_KEY_HEADING_TRADEROUTE_LIST"));
		iBaseRate += iTradeFood;
		bNeedSubtotal = true;
	}

	// Specialists
	int iSpecialistFood = 0;
	for (i = 0; i < GC.getNumSpecialistInfos(); i++)
	{
		iSpecialistFood += GET_PLAYER(city.getOwnerINLINE()).specialistYield((SpecialistTypes)i, YIELD_FOOD) * (city.getSpecialistCount((SpecialistTypes)i) + city.getFreeSpecialistCount((SpecialistTypes)i));
	}
	if (iSpecialistFood != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_SPECIALIST_COMMERCE", iSpecialistFood, info.getChar(), L"TXT_KEY_CONCEPT_SPECIALISTS"));
		iBaseRate += iSpecialistFood;
		bNeedSubtotal = true;
	}

	// Corporations
	int iCorporationFood = city.getCorporationYield(YIELD_FOOD);
	if (iCorporationFood != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_CORPORATION_COMMERCE", iCorporationFood, info.getChar()));
		iBaseRate += iCorporationFood;
		bNeedSubtotal = true;
	}

	// Buildings
	int iBuildingFood = 0;
	for (i = 0; i < GC.getNumBuildingInfos(); i++)
	{
		int iCount = city.getNumActiveBuilding((BuildingTypes)i);
		if (iCount > 0)
		{
			CvBuildingInfo& kBuilding = GC.getBuildingInfo((BuildingTypes)i);
			iBuildingFood += iCount * (kBuilding.getYieldChange(YIELD_FOOD) + city.getBuildingYieldChange((BuildingClassTypes)kBuilding.getBuildingClassType(), YIELD_FOOD));
		}
	}
	if (iBuildingFood != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_BUILDING_COMMERCE", iBuildingFood, info.getChar()));
		iBaseRate += iBuildingFood;
		bNeedSubtotal = true;
	}

	// Base and modifiers (only if there are modifiers since total is always shown)
	if (city.getBaseYieldRateModifier(YIELD_FOOD) != 100)
	{
		szBuffer.append(SEPARATOR);
		szBuffer.append(NEWLINE);
		// shows Base Food and lists all modifiers
		setYieldHelp(szBuffer, city, YIELD_FOOD);
	}
	else
	{
		szBuffer.append(NEWLINE);
	}

	// Total Produced
	int iBaseModifier = city.getBaseYieldRateModifier(YIELD_FOOD);
	int iRate = iBaseModifier * iBaseRate / 100;
	szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_TOTAL_FOOD_PRODUCED", iRate));

	// ==========================
	szBuffer.append(DOUBLE_SEPARATOR);

	int iFoodConsumed = 0;

	// Eaten
	int iEatenFood = city.getPopulation() * GC.getFOOD_CONSUMPTION_PER_POPULATION();
	if (iEatenFood != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_EATEN_FOOD", iEatenFood));
		iFoodConsumed += iEatenFood;
	}

	// Health
	int iSpoiledFood = - city.healthRate();
	if (iSpoiledFood != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_SPOILED_FOOD", iSpoiledFood));
		iFoodConsumed += iSpoiledFood;
	}
	
	// Total Consumed
	szBuffer.append(NEWLINE);
	szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_TOTAL_FOOD_CONSUMED", iFoodConsumed));

	// ==========================
	szBuffer.append(DOUBLE_SEPARATOR NEWLINE);
	iRate -= iFoodConsumed;

	// Production
	if (city.isFoodProduction() && iRate > 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_NET_FOOD_PRODUCTION", iRate, city.getProductionNameKey()));
	}
	else
	{
		// cannot starve a size 1 city with no food in
		if (iRate < 0 && city.getPopulation() == 1 && city.getFood() == 0)
		{
			iRate = 0;
		}

		// Net Food
		if (iRate > 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_NET_FOOD_GROW", iRate));
		}
		else if (iRate < 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_NET_FOOD_SHRINK", iRate));
		}
		else
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_NET_FOOD_STAGNATE"));
		}
	}

	// ==========================

// BUG - Building Additional Food - start
	if (city.getOwnerINLINE() == GC.getGame().getActivePlayer() && getBugOptionBOOL("MiscHover__BuildingAdditionalFood", true, "BUG_BUILDING_ADDITIONAL_FOOD_HOVER"))
	{
		setBuildingAdditionalYieldHelp(szBuffer, city, YIELD_FOOD, DOUBLE_SEPARATOR);
	}
// BUG - Building Additional Food - end
}
// BUG - Food Rate Hover - end

// BUG - Building Additional Yield - start
bool CvGameTextMgr::setBuildingAdditionalYieldHelp(CvWStringBuffer &szBuffer, const CvCity& city, YieldTypes eIndex, const CvWString& szStart, bool bStarted)
{
	CvYieldInfo& info = GC.getYieldInfo(eIndex);
	CvWString szLabel;
	CvCivilizationInfo& kCivilization = GC.getCivilizationInfo(GET_PLAYER(city.getOwnerINLINE()).getCivilizationType());

	for (int iI = 0; iI < GC.getNumBuildingClassInfos(); iI++)
	{
		BuildingTypes eBuilding = (BuildingTypes)kCivilization.getCivilizationBuildings((BuildingClassTypes)iI);

		if (eBuilding != NO_BUILDING && city.canConstruct(eBuilding, false, true, false))
		{
			int iChange = city.getAdditionalYieldByBuilding(eIndex, eBuilding);

			if (iChange != 0)
			{
				if (!bStarted)
				{
					szBuffer.append(szStart);
					bStarted = true;
				}

				szLabel.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_BUILDING_TEXT"), GC.getBuildingInfo(eBuilding).getDescription());
				setResumableValueChangeHelp(szBuffer, szLabel, L": ", L"", iChange, info.getChar(), false, true);
			}
		}
	}

	return bStarted;
}
// BUG - Building Additional Yield - end

// BUG - Building Additional Commerce - start
bool CvGameTextMgr::setBuildingAdditionalCommerceHelp(CvWStringBuffer &szBuffer, const CvCity& city, CommerceTypes eIndex, const CvWString& szStart, bool bStarted)
{
	CvCommerceInfo& info = GC.getCommerceInfo(eIndex);
	CvWString szLabel;
	CvCivilizationInfo& kCivilization = GC.getCivilizationInfo(GET_PLAYER(city.getOwnerINLINE()).getCivilizationType());

	for (int iI = 0; iI < GC.getNumBuildingClassInfos(); iI++)
	{
		BuildingTypes eBuilding = (BuildingTypes)kCivilization.getCivilizationBuildings((BuildingClassTypes)iI);

		if (eBuilding != NO_BUILDING && city.canConstruct(eBuilding, false, true, false))
		{
			int iChange = city.getAdditionalCommerceTimes100ByBuilding(eIndex, eBuilding);

			if (iChange != 0)
			{
				if (!bStarted)
				{
					szBuffer.append(szStart);
					bStarted = true;
				}

				szLabel.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_BUILDING_TEXT"), GC.getBuildingInfo(eBuilding).getDescription());
				setResumableValueTimes100ChangeHelp(szBuffer, szLabel, L": ", L"", iChange, info.getChar(), true);
			}
		}
	}

	return bStarted;
}
// BUG - Building Additional Commerce - end

// BUG - Building Saved Maintenance - start
bool CvGameTextMgr::setBuildingSavedMaintenanceHelp(CvWStringBuffer &szBuffer, const CvCity& city, const CvWString& szStart, bool bStarted)
{
	CvCommerceInfo& info = GC.getCommerceInfo(COMMERCE_GOLD);
	CvWString szLabel;
	CvCivilizationInfo& kCivilization = GC.getCivilizationInfo(GET_PLAYER(city.getOwnerINLINE()).getCivilizationType());

	for (int iI = 0; iI < GC.getNumBuildingClassInfos(); iI++)
	{
		BuildingTypes eBuilding = (BuildingTypes)kCivilization.getCivilizationBuildings((BuildingClassTypes)iI);

		if (eBuilding != NO_BUILDING && city.canConstruct(eBuilding, false, true, false))
		{
			int iChange = city.getSavedMaintenanceTimes100ByBuilding(eBuilding);
			
			if (iChange != 0)
			{
				if (!bStarted)
				{
					szBuffer.append(szStart);
					bStarted = true;
				}

				szLabel.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_BUILDING_TEXT"), GC.getBuildingInfo(eBuilding).getDescription());
				setResumableValueTimes100ChangeHelp(szBuffer, szLabel, L": ", L"", iChange, info.getChar(), true);
			}
		}
	}

	return bStarted;
}
// BUG - Building Saved Maintenance - end

void CvGameTextMgr::setProductionHelp(CvWStringBuffer &szBuffer, CvCity& city)
{
	FAssertMsg(NO_PLAYER != city.getOwnerINLINE(), "City must have an owner");

	bool bIsProcess = city.isProductionProcess();
	int iPastOverflow = (bIsProcess ? 0 : city.getOverflowProduction());
	if (iPastOverflow != 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_OVERFLOW", iPastOverflow));
		szBuffer.append(NEWLINE);
	}

	int iFromChops = (city.isProductionProcess() ? 0 : city.getFeatureProduction());
	if (iFromChops != 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_CHOPS", iFromChops));
		szBuffer.append(NEWLINE);
	}

	//FfH: Added by Kael 10/13/2007
	int iUnhappyProd = (city.isUnhappyProduction() ? city.unhappyLevel(0) : 0);
	//FfH: End Add

// BUG - Building Additional Production - start
	bool bBuildingAdditionalYield = getBugOptionBOOL("MiscHover__BuildingAdditionalProduction", true, "BUG_BUILDING_ADDITIONAL_PRODUCTION_HOVER");
	if (city.getCurrentProductionDifference(false, true) == 0 && !bBuildingAdditionalYield)
// BUG - Building Additional Production - end
	{
		return;
	}

	setYieldHelp(szBuffer, city, YIELD_PRODUCTION);
// Bugfix: Unhappy production should be calculated in getBaseYieldRate to make sure that it is taken into account in all production related calculations.
// For the GUI, we calculate it separately in order to be able to show the effect of unhappy production.
//FfH: Modified by Kael 10/13/2007
	int iBaseProduction = city.getBaseYieldRate(YIELD_PRODUCTION, false) + iPastOverflow + iFromChops + iUnhappyProd;
//	int iBaseProduction = city.getBaseYieldRate(YIELD_PRODUCTION) + iPastOverflow + iFromChops + iUnhappyProd;
//FfH: End Modify
// Bugfix end

	int iBaseModifier = city.getBaseYieldRateModifier(YIELD_PRODUCTION);

	UnitTypes eUnit = city.getProductionUnit();
	if (NO_UNIT != eUnit)
	{
		CvUnitInfo& unit = GC.getUnitInfo(eUnit);

		// Domain
		int iDomainMod = city.getDomainProductionModifier((DomainTypes)unit.getDomainType());
		if (0 != iDomainMod)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_DOMAIN", iDomainMod, GC.getDomainInfo((DomainTypes)unit.getDomainType()).getTextKeyWide()));
			szBuffer.append(NEWLINE);
			iBaseModifier += iDomainMod;
		}

		// Military
		if (unit.isMilitaryProduction())
		{
			int iMilitaryMod = city.getMilitaryProductionModifier() + GET_PLAYER(city.getOwnerINLINE()).getMilitaryProductionModifier();
			if (0 != iMilitaryMod)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_MILITARY", iMilitaryMod));
				szBuffer.append(NEWLINE);
				iBaseModifier += iMilitaryMod;
			}
		}

		// Bonus
		for (int i = 0; i < GC.getNumBonusInfos(); i++)
		{
			if (city.hasBonus((BonusTypes)i))
			{
				int iBonusMod = unit.getBonusProductionModifier(i);
				if (0 != iBonusMod)
				{
					szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_MOD_BONUS", iBonusMod, unit.getTextKeyWide(), GC.getBonusInfo((BonusTypes)i).getTextKeyWide()));
					szBuffer.append(NEWLINE);
					iBaseModifier += iBonusMod;
				}
			}
		}

		// Trait
		for (int i = 0; i < GC.getNumTraitInfos(); i++)
		{
			if (city.hasTrait((TraitTypes)i))
			{
				int iTraitMod = unit.getProductionTraits(i);

				if (unit.getSpecialUnitType() != NO_SPECIALUNIT)
				{
					iTraitMod += GC.getSpecialUnitInfo((SpecialUnitTypes) unit.getSpecialUnitType()).getProductionTraits(i);
				}
				if (0 != iTraitMod)
				{
					szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_TRAIT", iTraitMod, unit.getTextKeyWide(), GC.getTraitInfo((TraitTypes)i).getTextKeyWide()));
					szBuffer.append(NEWLINE);
					iBaseModifier += iTraitMod;
				}
			}
		}

		// Religion
		if (NO_PLAYER != city.getOwnerINLINE() && NO_RELIGION != GET_PLAYER(city.getOwnerINLINE()).getStateReligion())
		{
			if (city.isHasReligion(GET_PLAYER(city.getOwnerINLINE()).getStateReligion()))
			{
				int iReligionMod = GET_PLAYER(city.getOwnerINLINE()).getStateReligionUnitProductionModifier();
				if (0 != iReligionMod)
				{
					szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_RELIGION", iReligionMod, GC.getReligionInfo(GET_PLAYER(city.getOwnerINLINE()).getStateReligion()).getTextKeyWide()));
					szBuffer.append(NEWLINE);
					iBaseModifier += iReligionMod;
				}
			}
		}
	}

	BuildingTypes eBuilding = city.getProductionBuilding();
	if (NO_BUILDING != eBuilding)
	{
		CvBuildingInfo& building = GC.getBuildingInfo(eBuilding);

		// Bonus
		for (int i = 0; i < GC.getNumBonusInfos(); i++)
		{
			if (city.hasBonus((BonusTypes)i))
			{
				int iBonusMod = building.getBonusProductionModifier(i);
				if (0 != iBonusMod)
				{
					szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_MOD_BONUS", iBonusMod, building.getTextKeyWide(), GC.getBonusInfo((BonusTypes)i).getTextKeyWide()));
					szBuffer.append(NEWLINE);
					iBaseModifier += iBonusMod;
				}
			}
		}

		// Trait
		for (int i = 0; i < GC.getNumTraitInfos(); i++)
		{
			if (city.hasTrait((TraitTypes)i))
			{
				int iTraitMod = building.getProductionTraits(i);

				if (building.getSpecialBuildingType() != NO_SPECIALBUILDING)
				{
					iTraitMod += GC.getSpecialBuildingInfo((SpecialBuildingTypes) building.getSpecialBuildingType()).getProductionTraits(i);
				}
				if (0 != iTraitMod)
				{
					szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_TRAIT", iTraitMod, building.getTextKeyWide(), GC.getTraitInfo((TraitTypes)i).getTextKeyWide()));
					szBuffer.append(NEWLINE);
					iBaseModifier += iTraitMod;
				}
			}
		}

		// Wonder
		if (isWorldWonderClass((BuildingClassTypes)(GC.getBuildingInfo(eBuilding).getBuildingClassType())) && NO_PLAYER != city.getOwnerINLINE())
		{
			int iWonderMod = GET_PLAYER(city.getOwnerINLINE()).getMaxGlobalBuildingProductionModifier();
			if (0 != iWonderMod)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_WONDER", iWonderMod));
				szBuffer.append(NEWLINE);
				iBaseModifier += iWonderMod;
			}
		}

		// Team Wonder
		if (isTeamWonderClass((BuildingClassTypes)(GC.getBuildingInfo(eBuilding).getBuildingClassType())) && NO_PLAYER != city.getOwnerINLINE())
		{
			int iWonderMod = GET_PLAYER(city.getOwnerINLINE()).getMaxTeamBuildingProductionModifier();
			if (0 != iWonderMod)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_TEAM_WONDER", iWonderMod));
				szBuffer.append(NEWLINE);
				iBaseModifier += iWonderMod;
			}
		}

		// National Wonder
		if (isNationalWonderClass((BuildingClassTypes)(GC.getBuildingInfo(eBuilding).getBuildingClassType())) && NO_PLAYER != city.getOwnerINLINE())
		{
			int iWonderMod = GET_PLAYER(city.getOwnerINLINE()).getMaxPlayerBuildingProductionModifier();
			if (0 != iWonderMod)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_NATIONAL_WONDER", iWonderMod));
				szBuffer.append(NEWLINE);
				iBaseModifier += iWonderMod;
			}
		}

		// Religion
		if (NO_PLAYER != city.getOwnerINLINE() && NO_RELIGION != GET_PLAYER(city.getOwnerINLINE()).getStateReligion())
		{
			if (city.isHasReligion(GET_PLAYER(city.getOwnerINLINE()).getStateReligion()))
			{
				int iReligionMod = GET_PLAYER(city.getOwnerINLINE()).getStateReligionBuildingProductionModifier();
				if (0 != iReligionMod)
				{
					szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_RELIGION", iReligionMod, GC.getReligionInfo(GET_PLAYER(city.getOwnerINLINE()).getStateReligion()).getTextKeyWide()));
					szBuffer.append(NEWLINE);
					iBaseModifier += iReligionMod;
				}
			}
		}
	}

	ProjectTypes eProject = city.getProductionProject();
	if (NO_PROJECT != eProject)
	{
		CvProjectInfo& project = GC.getProjectInfo(eProject);

		// Spaceship

//FfH: Modified by Kael 12/17/2008
//		if (project.isSpaceship())
//		{
//			int iSpaceshipMod = city.getSpaceProductionModifier();
//			if (NO_PLAYER != city.getOwnerINLINE())
//			{
//				iSpaceshipMod += GET_PLAYER(city.getOwnerINLINE()).getSpaceProductionModifier();
//			}
//			if (0 != iSpaceshipMod)
//			{
//				szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_SPACESHIP", iSpaceshipMod));
//				szBuffer.append(NEWLINE);
//				iBaseModifier += iSpaceshipMod;
//			}
//		}
		int iSpaceshipMod = city.getSpaceProductionModifier();
		if (NO_PLAYER != city.getOwnerINLINE())
		{
			iSpaceshipMod += GET_PLAYER(city.getOwnerINLINE()).getSpaceProductionModifier();
		}
		if (0 != iSpaceshipMod)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_SPACESHIP", iSpaceshipMod));
			szBuffer.append(NEWLINE);
			iBaseModifier += iSpaceshipMod;
		}
//FfH: End Modify

		// Bonus
		for (int i = 0; i < GC.getNumBonusInfos(); i++)
		{
			if (city.hasBonus((BonusTypes)i))
			{
				int iBonusMod = project.getBonusProductionModifier(i);
				if (0 != iBonusMod)
				{
					szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_MOD_BONUS", iBonusMod, project.getTextKeyWide(), GC.getBonusInfo((BonusTypes)i).getTextKeyWide()));
					szBuffer.append(NEWLINE);
					iBaseModifier += iBonusMod;
				}
			}
		}
	}

	int iFoodProduction = (city.isFoodProduction() ? std::max(0, (city.getYieldRate(YIELD_FOOD) - city.foodConsumption(true))) : 0);
	if (iFoodProduction > 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_FOOD", iFoodProduction, iFoodProduction));
		szBuffer.append(NEWLINE);
	}

	int iModProduction = iFoodProduction + (iBaseModifier * iBaseProduction) / 100;

	FAssertMsg(iModProduction == city.getCurrentProductionDifference(false, !bIsProcess), "Modified Production does not match actual value");

	szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PROD_FINAL_YIELD", iModProduction));
// BUG - Building Additional Production - start
	if (bBuildingAdditionalYield && city.getOwnerINLINE() == GC.getGame().getActivePlayer())
	{
		setBuildingAdditionalYieldHelp(szBuffer, city, YIELD_PRODUCTION, DOUBLE_SEPARATOR);
	}
// BUG - Building Additional Production - end
}


void CvGameTextMgr::parsePlayerTraits(CvWStringBuffer &szBuffer, PlayerTypes ePlayer)
{
	bool bFirst = true;

	for (int iTrait = 0; iTrait < GC.getNumTraitInfos(); ++iTrait)
	{
		if (GET_PLAYER(ePlayer).hasTrait((TraitTypes)iTrait))
		{
			if (bFirst)
			{
				szBuffer.append(L" (");
				bFirst = false;
			}
			else
			{
				szBuffer.append(L", ");
			}
			szBuffer.append(GC.getTraitInfo((TraitTypes)iTrait).getDescription());
		}
	}

	if (!bFirst)
	{
		szBuffer.append(L")");
	}
}

void CvGameTextMgr::parseLeaderHeadHelp(CvWStringBuffer &szBuffer, PlayerTypes eThisPlayer, PlayerTypes eOtherPlayer)
{
	if (NO_PLAYER == eThisPlayer)
	{
		return;
	}

/************************************************************************************************/
/* Advanced Diplomacy         START                                                               */
/************************************************************************************************/
	//Active Senate
	if (GET_PLAYER(GC.getGameINLINE().getActivePlayer()).isActiveSenate() && GET_TEAM(GC.getGameINLINE().getActiveTeam()).isWarPretextAgainst(GET_PLAYER(eThisPlayer).getTeam()))
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(CvWString::format(L"%c %s", gDLL->getSymbolID(OCCUPATION_CHAR), gDLL->getText("TXT_KEY_MISC_HELP_CURRENT_PRETEXT").c_str()));
	}
/************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/************************************************************************************************/

	szBuffer.append(CvWString::format(L"%s", GET_PLAYER(eThisPlayer).getName()));

	parsePlayerTraits(szBuffer, eThisPlayer);

	szBuffer.append(L"\n");

// BUG - Leaderhead Relations - start
	PlayerTypes eActivePlayer = GC.getGameINLINE().getActivePlayer();
	TeamTypes eThisTeam = GET_PLAYER(eThisPlayer).getTeam();
	CvTeam& kThisTeam = GET_TEAM(eThisTeam);

	if (eOtherPlayer == NO_PLAYER)
	{
		eOtherPlayer = eActivePlayer;
	}
	if (eThisPlayer != eOtherPlayer && kThisTeam.isHasMet(GET_PLAYER(eOtherPlayer).getTeam()))
	{
		getEspionageString(szBuffer, eThisPlayer, eOtherPlayer);

		getAttitudeString(szBuffer, eThisPlayer, eOtherPlayer);

		if (gDLL->ctrlKey())
		{
			getActiveDealsString(szBuffer, eThisPlayer, eOtherPlayer);
		}
	}

	getAllRelationsString(szBuffer, eThisTeam);
// BUG - Leaderhead Relations - end
}

// BUG - Leaderhead Relations - start
/*
 * Displays the relations between two leaders only. This is used by the F4:GLANCE and F5:SIT-REP tabs.
 */
void CvGameTextMgr::parseLeaderHeadRelationsHelp(CvWStringBuffer &szBuffer, PlayerTypes eThisPlayer, PlayerTypes eOtherPlayer)
{
	if (NO_PLAYER == eThisPlayer)
	{
		return;
	}
	if (NO_PLAYER == eOtherPlayer)
	{
		parseLeaderHeadHelp(szBuffer, eThisPlayer, NO_PLAYER);
		return;
	}

	szBuffer.append(CvWString::format(L"%s", GET_PLAYER(eThisPlayer).getName()));

	parsePlayerTraits(szBuffer, eThisPlayer);

	szBuffer.append(L"\n");

	PlayerTypes eActivePlayer = GC.getGameINLINE().getActivePlayer();
	TeamTypes eThisTeam = GET_PLAYER(eThisPlayer).getTeam();
	CvTeam& kThisTeam = GET_TEAM(eThisTeam);

	if (eThisPlayer != eOtherPlayer && kThisTeam.isHasMet(GET_PLAYER(eOtherPlayer).getTeam()))
	{

//FfH: Modified by Kael 06/25/2008
//			getEspionageString(szBuffer, eThisPlayer, eOtherPlayer);
//FfH: End Modify

		getAttitudeString(szBuffer, eThisPlayer, eOtherPlayer);

		getActiveDealsString(szBuffer, eThisPlayer, eOtherPlayer);

		if (eOtherPlayer == eActivePlayer)
		{
			getActiveTeamRelationsString(szBuffer, eThisTeam);
		}
		else
		{
			getOtherRelationsString(szBuffer, eThisPlayer, eOtherPlayer);
		}
	}
	else
	{
		getAllRelationsString(szBuffer, eThisTeam);
	}
}
// BUG - Leaderhead Relations - end

void CvGameTextMgr::parseLeaderLineHelp(CvWStringBuffer &szBuffer, PlayerTypes eThisPlayer, PlayerTypes eOtherPlayer)
{
	if (NO_PLAYER == eThisPlayer || NO_PLAYER == eOtherPlayer)
	{
		return;
	}
	CvTeam& thisTeam = GET_TEAM(GET_PLAYER(eThisPlayer).getTeam());
	CvTeam& otherTeam = GET_TEAM(GET_PLAYER(eOtherPlayer).getTeam());

	if (thisTeam.getID() == otherTeam.getID())
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_PERMANENT_ALLIANCE"));
		szBuffer.append(NEWLINE);
	}
	else if (thisTeam.isAtWar(otherTeam.getID()))
	{
		szBuffer.append(gDLL->getText("TXT_KEY_CONCEPT_WAR"));
		szBuffer.append(NEWLINE);
	}
	else
	{
		if (thisTeam.isDefensivePact(otherTeam.getID()))
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_DEFENSIVE_PACT"));
			szBuffer.append(NEWLINE);
		}
/*************************************************************************************************/
/** Advanced Diplomacy       START															     */
/*************************************************************************************************/
		if (thisTeam.isLimitedBorders(otherTeam.getID()) || otherTeam.isLimitedBorders(thisTeam.getID()))
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_RIGHT_PASSAGE"));
			szBuffer.append(NEWLINE);
		}

		if (thisTeam.isHasEmbassy(otherTeam.getID()) || otherTeam.isHasEmbassy(thisTeam.getID()))
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_EMBASSY"));
			szBuffer.append(NEWLINE);
		}

		if (thisTeam.isHasNonAggression(otherTeam.getID()) || otherTeam.isHasNonAggression(thisTeam.getID()))
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_NON_AGGRESSION"));
			szBuffer.append(NEWLINE);
		}
		
		if (thisTeam.isFreeTradeAgreement(otherTeam.getID()) || otherTeam.isFreeTradeAgreement(thisTeam.getID()))
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_FREE_TRADE"));
			szBuffer.append(NEWLINE);
		}
		
		if (thisTeam.isHasNonAggression(otherTeam.getID()) || otherTeam.isHasNonAggression(thisTeam.getID()))
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_NON_AGGRESSION"));
			szBuffer.append(NEWLINE);
		}

		if (thisTeam.isHasPOW(otherTeam.getID()) || otherTeam.isHasPOW(thisTeam.getID()))
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_POW"));
			szBuffer.append(NEWLINE);
		}
		
/*************************************************************************************************/
/** Advanced Diplomacy       END															     */
/*************************************************************************************************/
		if (thisTeam.isOpenBorders(otherTeam.getID()))
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_OPEN_BORDERS"));
			szBuffer.append(NEWLINE);
		}
		if (thisTeam.isVassal(otherTeam.getID()))
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_VASSAL"));
			szBuffer.append(NEWLINE);
		}
	}
}


void CvGameTextMgr::getActiveDealsString(CvWStringBuffer &szBuffer, PlayerTypes eThisPlayer, PlayerTypes eOtherPlayer)
{
	int iIndex;
	CvDeal* pDeal = GC.getGameINLINE().firstDeal(&iIndex);
	while (NULL != pDeal)
	{
		if ((pDeal->getFirstPlayer() == eThisPlayer && pDeal->getSecondPlayer() == eOtherPlayer)
			|| (pDeal->getFirstPlayer() == eOtherPlayer && pDeal->getSecondPlayer() == eThisPlayer))
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(CvWString::format(L"%c", gDLL->getSymbolID(BULLET_CHAR)));
			getDealString(szBuffer, *pDeal, eThisPlayer);
		}
		pDeal = GC.getGameINLINE().nextDeal(&iIndex);
	}
}

// BUG - Leaderhead Relations - start
/*
 * Shows the peace/war/enemy/pact status between eThisTeam and all rivals known to the active player.
 * Relations for the active player are shown first.
 */
void CvGameTextMgr::getAllRelationsString(CvWStringBuffer& szString, TeamTypes eThisTeam)
{
	getActiveTeamRelationsString(szString, eThisTeam);
	getOtherRelationsString(szString, eThisTeam, NO_TEAM, GC.getGameINLINE().getActiveTeam());
}

/*
 * Shows the peace/war/enemy/pact status between eThisTeam and the active player.
 */
void CvGameTextMgr::getActiveTeamRelationsString(CvWStringBuffer& szString, TeamTypes eThisTeam)
{
	CvTeamAI& kThisTeam = GET_TEAM(eThisTeam);
	TeamTypes eActiveTeam = GC.getGameINLINE().getActiveTeam();
	CvTeamAI& kActiveTeam = GET_TEAM(eActiveTeam);


	if (!kThisTeam.isHasMet(eActiveTeam))
	{
		return;
	}

	if (kThisTeam.isAtWar(eActiveTeam))
	{
		szString.append(NEWLINE);
		szString.append(gDLL->getText(L"TXT_KEY_AT_WAR_WITH_YOU"));
	}
	else if (kThisTeam.isForcePeace(eActiveTeam))
	{
		szString.append(NEWLINE);
		szString.append(gDLL->getText(L"TXT_KEY_PEACE_TREATY_WITH_YOU"));
	}

	if (!kThisTeam.isHuman() && kThisTeam.AI_getWorstEnemy() == eActiveTeam)
	{
		szString.append(NEWLINE);
		szString.append(gDLL->getText(L"TXT_KEY_WORST_ENEMY_IS_YOU"));
	}

	if (kThisTeam.isDefensivePact(eActiveTeam))
	{
		szString.append(NEWLINE);
		szString.append(gDLL->getText(L"TXT_KEY_DEFENSIVE_PACT_WITH_YOU"));
	}

	if (!kThisTeam.isAtWar(eActiveTeam))
	{

		if (kActiveTeam.AI_getWarPlan(eThisTeam) == WARPLAN_PREPARING_TOTAL)
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText(L"TXT_KEY_WARPLAN_TARGET_OF_YOU"));
		}

		if (GC.getGameINLINE().isDebugMode())
		{
			if (kThisTeam.AI_getWarPlan(eActiveTeam) == WARPLAN_PREPARING_TOTAL || kThisTeam.AI_getWarPlan(eActiveTeam) == WARPLAN_TOTAL)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText(L"TXT_KEY_WARPLAN_TARGET_IS_YOU"));
			}
			else if (kThisTeam.AI_getWarPlan(eActiveTeam) == WARPLAN_PREPARING_LIMITED || kThisTeam.AI_getWarPlan(eActiveTeam) == WARPLAN_LIMITED)
			{
				szString.append(NEWLINE);
				szString.append(gDLL->getText(L"TXT_KEY_WARPLAN_LIMITED_TARGET_IS_YOU"));
			}
		}
	}
}

/*
 * Shows the peace/war/enemy/pact status between eThisPlayer and eOtherPlayer (both must not be NO_PLAYER).
 * If eOtherTeam is not NO_TEAM, only relations between it and eThisTeam are shown.
 * if eSkipTeam is not NO_TEAM, relations involving it are not shown.
 */
void CvGameTextMgr::getOtherRelationsString(CvWStringBuffer& szString, PlayerTypes eThisPlayer, PlayerTypes eOtherPlayer)
{
	if (eThisPlayer == NO_PLAYER || eOtherPlayer == NO_PLAYER)
	{
		return;
	}

	getOtherRelationsString(szString, GET_PLAYER(eThisPlayer).getTeam(), GET_PLAYER(eOtherPlayer).getTeam(), NO_TEAM);
}

/*
 * Shows the peace/war/enemy/pact status between eThisPlayer and all rivals known to the active player.
 * If eOtherTeam is not NO_TEAM, only relations between it and eThisTeam are shown.
 * if eSkipTeam is not NO_TEAM, relations involving it are not shown.
 */
void CvGameTextMgr::getOtherRelationsString(CvWStringBuffer& szString, TeamTypes eThisTeam, TeamTypes eOtherTeam, TeamTypes eSkipTeam)
{
	if (eThisTeam == NO_TEAM)
	{
		return;
	}

	//CvPlayer& kThisPlayer = GET_PLAYER(eThisPlayer);
	//CvPlayer& kOtherPlayer = GET_PLAYER(eOtherPlayer);
	CvTeamAI& kThisTeam = GET_TEAM(eThisTeam);
	CvWString szWar, szPeace, szEnemy, szPact, szWarPlanTotal, szWarPlanLimited;
	bool bFirstWar = true, bFirstPeace = true, bFirstEnemy = true, bFirstPact = true, bFirstWarPlanTotal = true, bFirstWarPlanLimited = true;

	for (int iTeam = 0; iTeam < MAX_CIV_TEAMS; ++iTeam)
	{
		CvTeamAI& kTeam = GET_TEAM((TeamTypes) iTeam);
		if (kTeam.isAlive() && !kTeam.isMinorCiv() && iTeam != eThisTeam && iTeam != eSkipTeam && (eOtherTeam == NO_TEAM || iTeam == eOtherTeam))
		{
			if (kTeam.isHasMet(eThisTeam) && kTeam.isHasMet(GC.getGameINLINE().getActiveTeam()))
			{
				if (::atWar((TeamTypes) iTeam, eThisTeam))
				{
					setListHelp(szWar, L"", kTeam.getName().GetCString(), L", ", bFirstWar);
					bFirstWar = false;
				}
				else if (kTeam.isForcePeace(eThisTeam))
				{
					setListHelp(szPeace, L"", kTeam.getName().GetCString(), L", ", bFirstPeace);
					bFirstPeace = false;
				}

				if (!kTeam.isHuman() && kTeam.AI_getWorstEnemy() == eThisTeam)
				{
					setListHelp(szEnemy, L"", kTeam.getName().GetCString(), L", ", bFirstEnemy);
					bFirstEnemy = false;
				}

				if (kTeam.isDefensivePact(eThisTeam))
				{
					setListHelp(szPact, L"", kTeam.getName().GetCString(), L", ", bFirstPact);
					bFirstPact = false;
				}

				//Show own war plans
				if (eThisTeam == GC.getGameINLINE().getActiveTeam() || (GC.getGameINLINE().isDebugMode() && !(::atWar((TeamTypes) iTeam, eThisTeam))))
				{
					if (kThisTeam.AI_getWarPlan((TeamTypes)iTeam) == WARPLAN_PREPARING_TOTAL || kThisTeam.AI_getWarPlan((TeamTypes)iTeam) == WARPLAN_TOTAL)
					{
						setListHelp(szWarPlanTotal, L"", kTeam.getName().GetCString(), L", ", bFirstWarPlanTotal);
						bFirstWarPlanTotal = false;
					}
					else if (kThisTeam.AI_getWarPlan((TeamTypes)iTeam) == WARPLAN_PREPARING_LIMITED || kThisTeam.AI_getWarPlan((TeamTypes)iTeam) == WARPLAN_LIMITED || kThisTeam.AI_getWarPlan((TeamTypes)iTeam) == WARPLAN_DOGPILE)
					{
						setListHelp(szWarPlanLimited, L"", kTeam.getName().GetCString(), L", ", bFirstWarPlanLimited);
						bFirstWarPlanLimited = false;
					}
				}
/*************************************************************************************************/
/** Advanced Diplomacy       START															     */
/*************************************************************************************************/			
				if (!kTeam.isHuman() && kTeam.AI_getClosestAlly() == eThisTeam)
				{
					szString.append(NEWLINE);
					szString.append(gDLL->getText(L"TXT_KEY_CLOSEST_ALLY_OF", kTeam.getName().GetCString()));
				}
/*************************************************************************************************/
/** Advanced Diplomacy       END															     */
/*************************************************************************************************/

			}
		}
	}

	if (!szWar.empty())
	{
		szString.append(NEWLINE);
		szString.append(gDLL->getText(L"TXT_KEY_AT_WAR_WITH", szWar.GetCString()));
	}
	if (!kThisTeam.isHuman())
	{
		TeamTypes eWorstEnemy = kThisTeam.AI_getWorstEnemy();
		if (eWorstEnemy != NO_TEAM && eWorstEnemy != eSkipTeam && (eOtherTeam == NO_TEAM || eWorstEnemy == eOtherTeam) && GET_TEAM(eWorstEnemy).isHasMet(GC.getGameINLINE().getActiveTeam()))
		{
			szString.append(NEWLINE);
			szString.append(gDLL->getText(L"TXT_KEY_WORST_ENEMY_IS", GET_TEAM(eWorstEnemy).getName().GetCString()));
		}
	}
	if (!szEnemy.empty())
	{
		szString.append(NEWLINE);
		szString.append(gDLL->getText(L"TXT_KEY_WORST_ENEMY_OF", szEnemy.GetCString()));
	}
	if (!szPeace.empty())
	{
		szString.append(NEWLINE);
		szString.append(gDLL->getText(L"TXT_KEY_PEACE_TREATY_WITH", szPeace.GetCString()));
	}
	if (!szPact.empty())
	{
		szString.append(NEWLINE);
		szString.append(gDLL->getText(L"TXT_KEY_DEFENSIVE_PACT_WITH", szPact.GetCString()));
	}
	if (!szWarPlanTotal.empty())
	{
		szString.append(NEWLINE);
		szString.append(gDLL->getText(L"TXT_KEY_WARPLAN_TARGET_IS", szWarPlanTotal.GetCString()));
	}
	if (!szWarPlanLimited.empty())
	{
		szString.append(NEWLINE);
		szString.append(gDLL->getText(L"TXT_KEY_WARPLAN_LIMITED_TARGET_IS", szWarPlanLimited.GetCString()));
	}
}
// BUG - Leaderhead Relations - end


void CvGameTextMgr::buildHintsList(CvWStringBuffer& szBuffer)
{
	for (int i = 0; i < GC.getNumHints(); i++)
	{
		szBuffer.append(CvWString::format(L"%c%s", gDLL->getSymbolID(BULLET_CHAR), GC.getHints(i).getText()));
		szBuffer.append(NEWLINE);
		szBuffer.append(NEWLINE);
	}
}

void CvGameTextMgr::setCommerceHelp(CvWStringBuffer &szBuffer, CvCity& city, CommerceTypes eCommerceType)
{
// BUG - Building Additional Commerce - start
	bool bBuildingAdditionalCommerce = getBugOptionBOOL("MiscHover__BuildingAdditionalCommerce", true, "BUG_BUILDING_ADDITIONAL_COMMERCE_HOVER");
	if (NO_COMMERCE == eCommerceType || (0 == city.getCommerceRateTimes100(eCommerceType) && !bBuildingAdditionalCommerce))
// BUG - Building Additional Commerce - end
	{
		return;
	}
	CvCommerceInfo& info = GC.getCommerceInfo(eCommerceType);

	if (NO_PLAYER == city.getOwnerINLINE())
	{
		return;
	}
	CvPlayer& owner = GET_PLAYER(city.getOwnerINLINE());

	setYieldHelp(szBuffer, city, YIELD_COMMERCE);

	// Slider
	int iBaseCommerceRate = city.getCommerceFromPercent(eCommerceType, city.getYieldRate(YIELD_COMMERCE) * 100);
	CvWString szRate = CvWString::format(L"%d.%02d", iBaseCommerceRate/100, iBaseCommerceRate%100);
	szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_SLIDER_PERCENT_FLOAT", owner.getCommercePercent(eCommerceType), city.getYieldRate(YIELD_COMMERCE), szRate.GetCString(), info.getChar()));
	szBuffer.append(NEWLINE);

// BUG - Base Commerce - start
	bool bNeedSubtotal = false;
// BUG - Base Commerce - end

//FfH: Modified by Kael 12/19/2007
//	int iSpecialistCommerce = city.getSpecialistCommerce(eCommerceType) + (city.getSpecialistPopulation() + city.getNumGreatPeople()) * owner.getSpecialistExtraCommerce(eCommerceType);
    int iSpecialistCommerce = city.getSpecialistCommerce(eCommerceType) + city.getExtraSpecialistCommerce(eCommerceType) + (city.getSpecialistPopulation() + city.getNumGreatPeople()) * owner.getSpecialistExtraCommerce(eCommerceType);
//FfH: End Modify

	if (0 != iSpecialistCommerce)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_SPECIALIST_COMMERCE", iSpecialistCommerce, info.getChar(), L"TXT_KEY_CONCEPT_SPECIALISTS"));
		szBuffer.append(NEWLINE);
		iBaseCommerceRate += 100 * iSpecialistCommerce;
// BUG - Base Commerce - start
		bNeedSubtotal = true;
// BUG - Base Commerce - end
	}

	int iReligionCommerce = city.getReligionCommerce(eCommerceType);
	if (0 != iReligionCommerce)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_RELIGION_COMMERCE", iReligionCommerce, info.getChar()));
		szBuffer.append(NEWLINE);
		iBaseCommerceRate += 100 * iReligionCommerce;
// BUG - Base Commerce - start
		bNeedSubtotal = true;
// BUG - Base Commerce - end
	}

	int iCorporationCommerce = city.getCorporationCommerce(eCommerceType);
	if (0 != iCorporationCommerce)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_CORPORATION_COMMERCE", iCorporationCommerce, info.getChar()));
		szBuffer.append(NEWLINE);
		iBaseCommerceRate += 100 * iCorporationCommerce;
// BUG - Base Commerce - start
		bNeedSubtotal = true;
// BUG - Base Commerce - end
	}

	int iBuildingCommerce = city.getBuildingCommerce(eCommerceType);
	if (0 != iBuildingCommerce)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_BUILDING_COMMERCE", iBuildingCommerce, info.getChar()));
		szBuffer.append(NEWLINE);
		iBaseCommerceRate += 100 * iBuildingCommerce;
// BUG - Base Commerce - start
		bNeedSubtotal = true;
// BUG - Base Commerce - end
	}

	int iFreeCityCommerce = owner.getFreeCityCommerce(eCommerceType);
	if (0 != iFreeCityCommerce)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_FREE_CITY_COMMERCE", iFreeCityCommerce, info.getChar()));
		szBuffer.append(NEWLINE);
		iBaseCommerceRate += 100 * iFreeCityCommerce;
// BUG - Base Commerce - start
		bNeedSubtotal = true;
// BUG - Base Commerce - end
	}

// BUG - Base Commerce - start
		if (bNeedSubtotal && city.getCommerceRateModifier(eCommerceType) != 0 && getBugOptionBOOL("MiscHover__BaseCommerce", true, "BUG_CITY_SCREEN_BASE_COMMERCE_HOVER"))
		{
			CvWString szYield = CvWString::format(L"%d.%02d", iBaseCommerceRate/100, iBaseCommerceRate%100);
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_COMMERCE_SUBTOTAL_YIELD_FLOAT", info.getTextKeyWide(), szYield.GetCString(), info.getChar()));
			szBuffer.append(NEWLINE);
		}
// BUG - Base Commerce - end

	FAssertMsg(city.getBaseCommerceRateTimes100(eCommerceType) == iBaseCommerceRate, "Base Commerce rate does not agree with actual value");

	int iModifier = 100;

	// Buildings
	int iBuildingMod = 0;
	for (int i = 0; i < GC.getNumBuildingInfos(); i++)
	{
		CvBuildingInfo& infoBuilding = GC.getBuildingInfo((BuildingTypes)i);
		if (city.getNumBuilding((BuildingTypes)i) > 0 && !GET_TEAM(city.getTeam()).isObsoleteBuilding((BuildingTypes)i))
		{
			for (int iLoop = 0; iLoop < city.getNumBuilding((BuildingTypes)i); iLoop++)
			{
				iBuildingMod += infoBuilding.getCommerceModifier(eCommerceType);
			}
		}
		for (int j = 0; j < MAX_PLAYERS; j++)
		{
			if (GET_PLAYER((PlayerTypes)j).isAlive())
			{
				if (GET_PLAYER((PlayerTypes)j).getTeam() == owner.getTeam())
				{
					int iLoop;
					for (CvCity* pLoopCity = GET_PLAYER((PlayerTypes)j).firstCity(&iLoop); pLoopCity != NULL; pLoopCity = GET_PLAYER((PlayerTypes)j).nextCity(&iLoop))
					{
						if (pLoopCity->getNumBuilding((BuildingTypes)i) > 0 && !GET_TEAM(pLoopCity->getTeam()).isObsoleteBuilding((BuildingTypes)i))
						{
							for (int iLoop = 0; iLoop < pLoopCity->getNumBuilding((BuildingTypes)i); iLoop++)
							{
								iBuildingMod += infoBuilding.getGlobalCommerceModifier(eCommerceType);
							}
						}
					}
				}
			}
		}
	}
	if (0 != iBuildingMod)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_YIELD_BUILDINGS", iBuildingMod, info.getChar()));
		szBuffer.append(NEWLINE);
		iModifier += iBuildingMod;
	}


	// Trait
	for (int i = 0; i < GC.getNumTraitInfos(); i++)
	{
		if (city.hasTrait((TraitTypes)i))
		{
			CvTraitInfo& trait = GC.getTraitInfo((TraitTypes)i);
			int iTraitMod = trait.getCommerceModifier(eCommerceType);
			if (0 != iTraitMod)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_COMMERCE_TRAIT", iTraitMod, info.getChar(), trait.getTextKeyWide()));
				szBuffer.append(NEWLINE);
				iModifier += iTraitMod;
			}
		}
	}

	// Bonuses
	if (eCommerceType == COMMERCE_RESEARCH)
	{
		for (int i = 0; i < GC.getNumBonusInfos(); i++)
		{
			if (city.hasBonus((BonusTypes)i))
			{
				CvBonusInfo& bonus = GC.getBonusInfo((BonusTypes)i);
				int iBonusMod = bonus.getResearchModifier() * (bonus.isModifierPerBonus() ? city.getNumBonuses((BonusTypes)i) : 1);
				if (0 != iBonusMod)
				{

						szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_BONUS_RESEARCH", iBonusMod, bonus.getTextKeyWide()));
						szBuffer.append(NEWLINE);
						iModifier += iBonusMod;
				}
			}
		}
	}


	// Capital
	int iCapitalMod = city.isCapital() ? owner.getCapitalCommerceRateModifier(eCommerceType) : 0;
	if (iCapitalMod != 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_YIELD_CAPITAL", iCapitalMod, info.getChar()));
		szBuffer.append(NEWLINE);
		iModifier += iCapitalMod;
	}


	// Civics
	int iCivicMod = 0;
	for (int i = 0; i < GC.getNumCivicOptionInfos(); i++)
	{
		if (NO_CIVIC != owner.getCivics((CivicOptionTypes)i))
		{
			iCivicMod += GC.getCivicInfo(owner.getCivics((CivicOptionTypes)i)).getCommerceModifier(eCommerceType);
		}
	}
	if (0 != iCivicMod)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_YIELD_CIVICS", iCivicMod, info.getChar()));
		szBuffer.append(NEWLINE);
		iModifier += iCivicMod;
	}

	int iModYield = (iModifier * iBaseCommerceRate) / 100;

	int iProductionToCommerce = city.getProductionToCommerceModifier(eCommerceType) * city.getYieldRate(YIELD_PRODUCTION);
	if (0 != iProductionToCommerce)
	{
		if (iProductionToCommerce%100 == 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PRODUCTION_TO_COMMERCE", iProductionToCommerce/100, info.getChar()));
			szBuffer.append(NEWLINE);
		}
		else
		{
			szRate = CvWString::format(L"+%d.%02d", iProductionToCommerce/100, iProductionToCommerce%100);
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_PRODUCTION_TO_COMMERCE_FLOAT", szRate.GetCString(), info.getChar()));
			szBuffer.append(NEWLINE);
		}
		iModYield += iProductionToCommerce;
	}

	if (eCommerceType == COMMERCE_CULTURE && GC.getGameINLINE().isOption(GAMEOPTION_NO_ESPIONAGE))
	{
		int iEspionageToCommerce = city.getCommerceRateTimes100(COMMERCE_CULTURE) - iModYield;
		if (0 != iEspionageToCommerce)
		{
			if (iEspionageToCommerce%100 == 0)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_COMMERCE_TO_COMMERCE", iEspionageToCommerce/100, info.getChar(), GC.getCommerceInfo(COMMERCE_ESPIONAGE).getChar()));
				szBuffer.append(NEWLINE);
			}
			else
			{
				szRate = CvWString::format(L"+%d.%02d", iEspionageToCommerce/100, iEspionageToCommerce%100);
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_COMMERCE_TO_COMMERCE_FLOAT", szRate.GetCString(), info.getChar(), GC.getCommerceInfo(COMMERCE_ESPIONAGE).getChar()));
				szBuffer.append(NEWLINE);
			}
			iModYield += iEspionageToCommerce;
		}
	}

	FAssertMsg(iModYield == city.getCommerceRateTimes100(eCommerceType), "Commerce yield does not match actual value");

	CvWString szYield = CvWString::format(L"%d.%02d", iModYield/100, iModYield%100);
	szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_COMMERCE_FINAL_YIELD_FLOAT", info.getTextKeyWide(), szYield.GetCString(), info.getChar()));

// BUG - Building Additional Commerce - start
	if (bBuildingAdditionalCommerce && city.getOwnerINLINE() == GC.getGame().getActivePlayer())
	{
		setBuildingAdditionalCommerceHelp(szBuffer, city, eCommerceType, DOUBLE_SEPARATOR);
	}
// BUG - Building Additional Commerce - end
}

void CvGameTextMgr::setYieldHelp(CvWStringBuffer &szBuffer, CvCity& city, YieldTypes eYieldType)
{
	FAssertMsg(NO_PLAYER != city.getOwnerINLINE(), "City must have an owner");

	if (NO_YIELD == eYieldType)
	{
		return;
	}
	CvYieldInfo& info = GC.getYieldInfo(eYieldType);

	if (NO_PLAYER == city.getOwnerINLINE())
	{
		return;
	}
	CvPlayer& owner = GET_PLAYER(city.getOwnerINLINE());

	// Bugfix: Unhappy production should be calculated in getBaseYieldRate to make sure that it is taken into account in all production related calculations.
	// For the GUI, we calculate it separately in order to be able to show the effect of unhappy production.
	int iBaseProduction = city.getBaseYieldRate(eYieldType, false);
	// Bugfix end
	szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_BASE_YIELD", info.getTextKeyWide(), iBaseProduction, info.getChar()));
	szBuffer.append(NEWLINE);

	//FfH: Added by Kael 10/13/2007
	// Bugfix: Do not show unhappy production information for commerce and science.
	// int iUnhappyProd = (city.isUnhappyProduction() ? city.unhappyLevel(0) : 0);
	int iUnhappyProd = (eYieldType == YIELD_PRODUCTION && city.isUnhappyProduction() ? city.unhappyLevel(0) : 0);
	// Bugfix end
	if (iUnhappyProd != 0)
	{
		iBaseProduction += iUnhappyProd;
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_UNHAPPY_PROD", iUnhappyProd));
		szBuffer.append(NEWLINE);
	}
	//FfH: End Add

	int iBaseModifier = 100;

	// Buildings
	int iBuildingMod = 0;
	for (int i = 0; i < GC.getNumBuildingInfos(); i++)
	{
		CvBuildingInfo& infoBuilding = GC.getBuildingInfo((BuildingTypes)i);
		if (city.getNumBuilding((BuildingTypes)i) > 0 && !GET_TEAM(city.getTeam()).isObsoleteBuilding((BuildingTypes)i))
		{
			for (int iLoop = 0; iLoop < city.getNumBuilding((BuildingTypes)i); iLoop++)
			{
				iBuildingMod += infoBuilding.getYieldModifier(eYieldType);
			}
		}
		for (int j = 0; j < MAX_PLAYERS; j++)
		{
			if (GET_PLAYER((PlayerTypes)j).isAlive())
			{
				if (GET_PLAYER((PlayerTypes)j).getTeam() == owner.getTeam())
				{
					int iLoop;
					for (CvCity* pLoopCity = GET_PLAYER((PlayerTypes)j).firstCity(&iLoop); pLoopCity != NULL; pLoopCity = GET_PLAYER((PlayerTypes)j).nextCity(&iLoop))
					{
						if (pLoopCity->getNumBuilding((BuildingTypes)i) > 0 && !GET_TEAM(pLoopCity->getTeam()).isObsoleteBuilding((BuildingTypes)i))
						{
							for (int iLoop = 0; iLoop < pLoopCity->getNumBuilding((BuildingTypes)i); iLoop++)
							{
								iBuildingMod += infoBuilding.getGlobalYieldModifier(eYieldType);
							}
						}
					}
				}
			}
		}
	}
	if (NULL != city.area())
	{
		iBuildingMod += city.area()->getYieldRateModifier(city.getOwnerINLINE(), eYieldType);
	}
	if (0 != iBuildingMod)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_YIELD_BUILDINGS", iBuildingMod, info.getChar()));
		szBuffer.append(NEWLINE);
		iBaseModifier += iBuildingMod;
	}

	// Power
	if (city.isPower())
	{
		int iPowerMod = city.getPowerYieldRateModifier(eYieldType);
		if (0 != iPowerMod)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_YIELD_POWER", iPowerMod, info.getChar()));
			szBuffer.append(NEWLINE);
			iBaseModifier += iPowerMod;
		}
	}

	// Resources
	int iBonusMod = city.getBonusYieldRateModifier(eYieldType);
	if (0 != iBonusMod)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_YIELD_BONUS", iBonusMod, info.getChar()));
		szBuffer.append(NEWLINE);
		iBaseModifier += iBonusMod;
	}

	// Capital
	if (city.isCapital())
	{
		int iCapitalMod = owner.getCapitalYieldRateModifier(eYieldType);
		if (0 != iCapitalMod)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_YIELD_CAPITAL", iCapitalMod, info.getChar()));
			szBuffer.append(NEWLINE);
			iBaseModifier += iCapitalMod;
		}
	}

	// Civics
	int iCivicMod = 0;
	for (int i = 0; i < GC.getNumCivicOptionInfos(); i++)
	{
		if (NO_CIVIC != owner.getCivics((CivicOptionTypes)i))
		{
			iCivicMod += GC.getCivicInfo(owner.getCivics((CivicOptionTypes)i)).getYieldModifier(eYieldType);
		}
	}
	if (0 != iCivicMod)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_YIELD_CIVICS", iCivicMod, info.getChar()));
		szBuffer.append(NEWLINE);
		iBaseModifier += iCivicMod;
	}

	// MNAI - copied from getBaseYieldRateModifier()- code by Kael 11/08/2007
    if (city.isSettlement())
    {
        iBaseModifier -= 75;
    }
	// End MNAI

	FAssertMsg((iBaseModifier * iBaseProduction) / 100 == city.getYieldRate(eYieldType), "Yield Modifier in setProductionHelp does not agree with actual value");
}

void CvGameTextMgr::setConvertHelp(CvWStringBuffer& szBuffer, PlayerTypes ePlayer, ReligionTypes eReligion)
{
	CvWString szReligion = L"TXT_KEY_MISC_NO_STATE_RELIGION";

	if (eReligion != NO_RELIGION)
	{
		szReligion = GC.getReligionInfo(eReligion).getTextKeyWide();
	}

	szBuffer.assign(gDLL->getText("TXT_KEY_MISC_CANNOT_CONVERT_TO", szReligion.GetCString()));

	if (GET_PLAYER(ePlayer).isAnarchy())
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_WHILE_IN_ANARCHY"));
	}
	else if (GET_PLAYER(ePlayer).getStateReligion() == eReligion)
	{
		szBuffer.append(L". ");
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ALREADY_STATE_REL"));
	}
	else if (GET_PLAYER(ePlayer).getConversionTimer() > 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ANOTHER_REVOLUTION_RECENTLY"));
		szBuffer.append(L". ");
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_WAIT_MORE_TURNS", GET_PLAYER(ePlayer).getConversionTimer()));
	}
}

void CvGameTextMgr::setRevolutionHelp(CvWStringBuffer& szBuffer, PlayerTypes ePlayer)
{
	szBuffer.assign(gDLL->getText("TXT_KEY_MISC_CANNOT_CHANGE_CIVICS"));

	if (GET_PLAYER(ePlayer).isAnarchy())
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_WHILE_IN_ANARCHY"));
	}
	else if (GET_PLAYER(ePlayer).getRevolutionTimer() > 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_ANOTHER_REVOLUTION_RECENTLY"));
		szBuffer.append(L" : ");
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_WAIT_MORE_TURNS", GET_PLAYER(ePlayer).getRevolutionTimer()));
	}
}

void CvGameTextMgr::setVassalRevoltHelp(CvWStringBuffer& szBuffer, TeamTypes eMaster, TeamTypes eVassal)
{
	if (NO_TEAM == eMaster || NO_TEAM == eVassal)
	{
		return;
	}

	if (!GET_TEAM(eVassal).isCapitulated())
	{
		return;
	}

	if (GET_TEAM(eMaster).isParent(eVassal))
	{
		return;
	}

	CvTeam& kMaster = GET_TEAM(eMaster);
	CvTeam& kVassal = GET_TEAM(eVassal);

	int iMasterLand = kMaster.getTotalLand(false);
	int iVassalLand = kVassal.getTotalLand(false);
	if (iMasterLand > 0 && GC.getDefineINT("FREE_VASSAL_LAND_PERCENT") >= 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_VASSAL_LAND_STATS", (iVassalLand * 100) / iMasterLand, GC.getDefineINT("FREE_VASSAL_LAND_PERCENT")));
	}

	int iMasterPop = kMaster.getTotalPopulation(false);
	int iVassalPop = kVassal.getTotalPopulation(false);
	if (iMasterPop > 0 && GC.getDefineINT("FREE_VASSAL_POPULATION_PERCENT") >= 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_VASSAL_POPULATION_STATS", (iVassalPop * 100) / iMasterPop, GC.getDefineINT("FREE_VASSAL_POPULATION_PERCENT")));
	}

	if (GC.getDefineINT("VASSAL_REVOLT_OWN_LOSSES_FACTOR") > 0 && kVassal.getVassalPower() > 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_VASSAL_AREA_LOSS", (iVassalLand * 100) / kVassal.getVassalPower(), GC.getDefineINT("VASSAL_REVOLT_OWN_LOSSES_FACTOR")));
	}

	if (GC.getDefineINT("VASSAL_REVOLT_MASTER_LOSSES_FACTOR") > 0 && kVassal.getMasterPower() > 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_MASTER_AREA_LOSS", (iMasterLand * 100) / kVassal.getMasterPower(), GC.getDefineINT("VASSAL_REVOLT_MASTER_LOSSES_FACTOR")));
	}
}

void CvGameTextMgr::parseGreatPeopleHelp(CvWStringBuffer &szBuffer, CvCity& city)
{
	int iTotalGreatPeopleUnitProgress;
	int iI;

	if (NO_PLAYER == city.getOwnerINLINE())
	{
		return;
	}
	CvPlayer& owner = GET_PLAYER(city.getOwnerINLINE());

	szBuffer.assign(gDLL->getText("TXT_KEY_MISC_GREAT_PERSON", city.getGreatPeopleProgress(), owner.greatPeopleThreshold(false)));

	if (city.getGreatPeopleRate() > 0)
	{
		int iGPPLeft = owner.greatPeopleThreshold(false) - city.getGreatPeopleProgress();

		if (iGPPLeft > 0)
		{
			int iTurnsLeft = iGPPLeft / city.getGreatPeopleRate();

			if (iTurnsLeft * city.getGreatPeopleRate() <  iGPPLeft)
			{
				iTurnsLeft++;
			}

			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("INTERFACE_CITY_TURNS", std::max(1, iTurnsLeft)));
		}
	}

	iTotalGreatPeopleUnitProgress = 0;

	for (iI = 0; iI < GC.getNumUnitInfos(); ++iI)
	{
		iTotalGreatPeopleUnitProgress += city.getGreatPeopleUnitProgress((UnitTypes)iI);
	}

	if (iTotalGreatPeopleUnitProgress > 0)
	{
		szBuffer.append(SEPARATOR);
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_PROB"));

		std::vector< std::pair<UnitTypes, int> > aUnitProgress;
		int iTotalTruncated = 0;
		for (iI = 0; iI < GC.getNumUnitInfos(); ++iI)
		{
			int iProgress = ((city.getGreatPeopleUnitProgress((UnitTypes)iI) * 100) / iTotalGreatPeopleUnitProgress);
			if (iProgress > 0)
			{
				iTotalTruncated += iProgress;
				aUnitProgress.push_back(std::make_pair((UnitTypes)iI, iProgress));
			}
		}

		if (iTotalTruncated < 100 && aUnitProgress.size() > 0)
		{
			aUnitProgress[0].second += 100 - iTotalTruncated;
		}

		for (iI = 0; iI < (int)aUnitProgress.size(); ++iI)
		{
			szBuffer.append(CvWString::format(L"%s%s - %d%%", NEWLINE, GC.getUnitInfo(aUnitProgress[iI].first).getDescription(), aUnitProgress[iI].second));
		}
	}

// BUG - Building Additional Great People - start
	bool bBuildingAdditionalGreatPeople = getBugOptionBOOL("MiscHover__BuildingAdditionalGreatPeople", true, "BUG_BUILDING_ADDITIONAL_GREAT_PEOPLE_HOVER");
	if (city.getGreatPeopleRate() == 0 && !bBuildingAdditionalGreatPeople)
// BUG - Building Additional Great People - end
	{
		return;
	}

// BUG - Great People Rate Breakdown - start
	if (getBugOptionBOOL("MiscHover__GreatPeopleRateBreakdown", true, "BUG_GREAT_PEOPLE_RATE_BREAKDOWN_HOVER"))
	{
		bool bFirst = true;
		int iRate = 0;
		for (int i = 0; i < GC.getNumSpecialistInfos(); i++)
		{
			int iCount = city.getSpecialistCount((SpecialistTypes)i) + city.getFreeSpecialistCount((SpecialistTypes)i);
			if (iCount > 0)
			{
				iRate += iCount * GC.getSpecialistInfo((SpecialistTypes)i).getGreatPeopleRateChange();
			}
		}
		if (iRate > 0)
		{
			if (bFirst)
			{
				szBuffer.append(SEPARATOR);
				bFirst = false;
			}
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_SPECIALIST_COMMERCE", iRate, gDLL->getSymbolID(GREAT_PEOPLE_CHAR), L"TXT_KEY_CONCEPT_SPECIALISTS"));
		}
		
		iRate = 0;
		for (int i = 0; i < GC.getNumBuildingInfos(); i++)
		{
			int iCount = city.getNumBuilding((BuildingTypes)i);
			if (iCount > 0)
			{
				iRate += iCount * GC.getBuildingInfo((BuildingTypes)i).getGreatPeopleRateChange();
			}
		}
		if (iRate > 0)
		{
			if (bFirst)
			{
				szBuffer.append(SEPARATOR);
				bFirst = false;
			}
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_BUILDING_COMMERCE", iRate, gDLL->getSymbolID(GREAT_PEOPLE_CHAR)));
		}
	}
// BUG - Great People Rate Breakdown - end

	szBuffer.append(SEPARATOR);
	szBuffer.append(NEWLINE);
	szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_GREATPEOPLE_BASE_RATE", city.getBaseGreatPeopleRate()));
	szBuffer.append(NEWLINE);

	int iModifier = 100;

	// Buildings
	int iBuildingMod = 0;
	for (int i = 0; i < GC.getNumBuildingInfos(); i++)
	{
		CvBuildingInfo& infoBuilding = GC.getBuildingInfo((BuildingTypes)i);
		if (city.getNumBuilding((BuildingTypes)i) > 0 && !GET_TEAM(city.getTeam()).isObsoleteBuilding((BuildingTypes)i))
		{
			for (int iLoop = 0; iLoop < city.getNumBuilding((BuildingTypes)i); iLoop++)
			{
				iBuildingMod += infoBuilding.getGreatPeopleRateModifier();
			}
		}
		for (int j = 0; j < MAX_PLAYERS; j++)
		{
			if (GET_PLAYER((PlayerTypes)j).isAlive())
			{
				if (GET_PLAYER((PlayerTypes)j).getTeam() == owner.getTeam())
				{
					int iLoop;
					for (CvCity* pLoopCity = GET_PLAYER((PlayerTypes)j).firstCity(&iLoop); pLoopCity != NULL; pLoopCity = GET_PLAYER((PlayerTypes)j).nextCity(&iLoop))
					{
						if (pLoopCity->getNumBuilding((BuildingTypes)i) > 0 && !GET_TEAM(pLoopCity->getTeam()).isObsoleteBuilding((BuildingTypes)i))
						{
							for (int iLoop = 0; iLoop < pLoopCity->getNumBuilding((BuildingTypes)i); iLoop++)
							{
								iBuildingMod += infoBuilding.getGlobalGreatPeopleRateModifier();
							}
						}
					}
				}
			}
		}
	}
	if (0 != iBuildingMod)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_GREATPEOPLE_BUILDINGS", iBuildingMod));
		szBuffer.append(NEWLINE);
		iModifier += iBuildingMod;
	}

	// Civics
	int iCivicMod = 0;
	for (int i = 0; i < GC.getNumCivicOptionInfos(); i++)
	{
		if (NO_CIVIC != owner.getCivics((CivicOptionTypes)i))
		{
			iCivicMod += GC.getCivicInfo(owner.getCivics((CivicOptionTypes)i)).getGreatPeopleRateModifier();
			if (owner.getStateReligion() != NO_RELIGION && city.isHasReligion(owner.getStateReligion()))
			{
				iCivicMod += GC.getCivicInfo(owner.getCivics((CivicOptionTypes)i)).getStateReligionGreatPeopleRateModifier();
			}
		}
	}
	if (0 != iCivicMod)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_GREATPEOPLE_CIVICS", iCivicMod));
		szBuffer.append(NEWLINE);
		iModifier += iCivicMod;
	}

	// Trait
	for (int i = 0; i < GC.getNumTraitInfos(); i++)
	{
		if (city.hasTrait((TraitTypes)i))
		{
			CvTraitInfo& trait = GC.getTraitInfo((TraitTypes)i);
			int iTraitMod = trait.getGreatPeopleRateModifier();
			if (0 != iTraitMod)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_GREATPEOPLE_TRAIT", iTraitMod, trait.getTextKeyWide()));
				szBuffer.append(NEWLINE);
				iModifier += iTraitMod;
			}
		}
	}

	// Bonuses
	for (int i = 0; i < GC.getNumBonusInfos(); i++)
	{
		if (city.hasBonus((BonusTypes)i))
		{
			CvBonusInfo& bonus = GC.getBonusInfo((BonusTypes)i);
			int iBonusMod = bonus.getGreatPeopleRateModifier();
			if (0 != iBonusMod)
			{
				int iTotalBonusMod = iBonusMod;
				if (bonus.isModifierPerBonus())
				{
					iTotalBonusMod = iBonusMod * city.getNumBonuses((BonusTypes)i);
				}
				
				szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_GREATPEOPLE_BONUS", iTotalBonusMod, bonus.getTextKeyWide()));
				szBuffer.append(NEWLINE);
				iModifier += iTotalBonusMod;
			}
		}
	}

	if (owner.isGoldenAge())
	{
		int iGoldenAgeMod = GC.getDefineINT("GOLDEN_AGE_GREAT_PEOPLE_MODIFIER");

		if (0 != iGoldenAgeMod)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_GREATPEOPLE_GOLDEN_AGE", iGoldenAgeMod));
			szBuffer.append(NEWLINE);
			iModifier += iGoldenAgeMod;
		}
	}

	int iModGreatPeople = (iModifier * city.getBaseGreatPeopleRate()) / 100;

	FAssertMsg(iModGreatPeople == city.getGreatPeopleRate(), "Great person rate does not match actual value");

	szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_GREATPEOPLE_FINAL", iModGreatPeople));
// BUG - Building Additional Great People - start
	if (bBuildingAdditionalGreatPeople && city.getOwnerINLINE() == GC.getGame().getActivePlayer())
	{
		setBuildingAdditionalGreatPeopleHelp(szBuffer, city, DOUBLE_SEPARATOR);
	}
// BUG - Building Additional Great People - end
}

// BUG - Building Additional Great People - start
bool CvGameTextMgr::setBuildingAdditionalGreatPeopleHelp(CvWStringBuffer &szBuffer, const CvCity& city, const CvWString& szStart, bool bStarted)
{
	CvWString szLabel;
	CvCivilizationInfo& kCivilization = GC.getCivilizationInfo(GET_PLAYER(city.getOwnerINLINE()).getCivilizationType());

	for (int iI = 0; iI < GC.getNumBuildingClassInfos(); iI++)
	{
		BuildingTypes eBuilding = (BuildingTypes)kCivilization.getCivilizationBuildings((BuildingClassTypes)iI);

		if (eBuilding != NO_BUILDING && city.canConstruct(eBuilding, false, true, false))
		{
			int iChange = city.getAdditionalGreatPeopleRateByBuilding(eBuilding);
			
			if (iChange != 0)
			{
				if (!bStarted)
				{
					szBuffer.append(szStart);
					bStarted = true;
				}

				szLabel.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_BUILDING_TEXT"), GC.getBuildingInfo(eBuilding).getDescription());
				setResumableValueChangeHelp(szBuffer, szLabel, L": ", L"", iChange, gDLL->getSymbolID(GREAT_PEOPLE_CHAR), false, true);
			}
		}
	}

	return bStarted;
}
// BUG - Building Additional Great People - end

void CvGameTextMgr::parseGreatGeneralHelp(CvWStringBuffer &szBuffer, CvPlayer& kPlayer)
{
	szBuffer.assign(gDLL->getText("TXT_KEY_MISC_GREAT_GENERAL", kPlayer.getCombatExperience(), kPlayer.greatPeopleThreshold(true)));
}


//------------------------------------------------------------------------------------------------

void CvGameTextMgr::buildCityBillboardIconString( CvWStringBuffer& szBuffer, CvCity* pCity)
{
	szBuffer.clear();

	// government center icon
	if (pCity->isGovernmentCenter() && !(pCity->isCapital()))
	{
		szBuffer.append(CvWString::format(L"%c", gDLL->getSymbolID(SILVER_STAR_CHAR)));
	}

	// happiness, healthiness, superlative icons
	if (pCity->canBeSelected())
	{
		if (pCity->angryPopulation() > 0)
		{
			szBuffer.append(CvWString::format(L"%c", gDLL->getSymbolID(UNHAPPY_CHAR)));
		}

		if (pCity->healthRate() < 0)
		{
			szBuffer.append(CvWString::format(L"%c", gDLL->getSymbolID(UNHEALTHY_CHAR)));
		}

		if (gDLL->getGraphicOption(GRAPHICOPTION_CITY_DETAIL))
		{
			if (GET_PLAYER(pCity->getOwnerINLINE()).getNumCities() > 2)
			{
				if (pCity->findYieldRateRank(YIELD_PRODUCTION) == 1)
				{
					szBuffer.append(CvWString::format(L"%c", GC.getYieldInfo(YIELD_PRODUCTION).getChar()));
				}
				if (pCity->findCommerceRateRank(COMMERCE_GOLD) == 1)
				{
					szBuffer.append(CvWString::format(L"%c", GC.getCommerceInfo(COMMERCE_GOLD).getChar()));
				}
				if (pCity->findCommerceRateRank(COMMERCE_RESEARCH) == 1)
				{
					szBuffer.append(CvWString::format(L"%c", GC.getCommerceInfo(COMMERCE_RESEARCH).getChar()));
				}
			}
		}

		if (pCity->isConnectedToCapital())
		{
			if (GET_PLAYER(pCity->getOwnerINLINE()).countNumCitiesConnectedToCapital() > 1)
			{
				szBuffer.append(CvWString::format(L"%c", gDLL->getSymbolID(TRADE_CHAR)));
			}
		}

// BUG - Airport Icon - start
		if (getBugOptionBOOL("CityBar__AirportIcons", true, "BUG_CITYBAR_AIRPORT_ICONS"))
		{
			// Tholal ToDo - remove Hardcode and check getAirlift() instead
			int eAirportClass = GC.getInfoTypeForString("BUILDINGCLASS_OBSIDIAN_GATE");
			if (eAirportClass != -1)
			{
				int eAirport = GC.getCivilizationInfo(pCity->getCivilizationType()).getCivilizationBuildings(eAirportClass);
				if (eAirport != -1 && pCity->getNumBuilding((BuildingTypes)eAirport) > 0)
				{
					szBuffer.append(CvWString::format(L"%c", gDLL->getSymbolID(AIRPORT_CHAR)));
				}
			}
		}
// BUG - Airport Icon - start
	}

	// religion icons
	for (int iI = 0; iI < GC.getNumReligionInfos(); ++iI)
	{
		if (pCity->isHasReligion((ReligionTypes)iI))
		{

//FfH: Modified by Kael 11/03/2007
//			if (pCity->isHolyCity((ReligionTypes)iI))
//			{
//				szBuffer.append(CvWString::format(L"%c", GC.getReligionInfo((ReligionTypes) iI).getHolyCityChar()));
//			}
//			else
//			{
//				szBuffer.append(CvWString::format(L"%c", GC.getReligionInfo((ReligionTypes) iI).getChar()));
//			}
            if (GET_PLAYER(GC.getGameINLINE().getActivePlayer()).canSeeReligion(iI, pCity))
            {
                if (pCity->isHolyCity((ReligionTypes)iI))
                {
                    szBuffer.append(CvWString::format(L"%c", GC.getReligionInfo((ReligionTypes) iI).getHolyCityChar()));
                }
                else
                {
                    szBuffer.append(CvWString::format(L"%c", GC.getReligionInfo((ReligionTypes) iI).getChar()));
                }
            }
//FfH: End Modify

		}
	}

	// corporation icons
	for (int iI = 0; iI < GC.getNumCorporationInfos(); ++iI)
	{
		if (pCity->isHeadquarters((CorporationTypes)iI))
		{
			if (pCity->isHasCorporation((CorporationTypes)iI))
			{
				szBuffer.append(CvWString::format(L"%c", GC.getCorporationInfo((CorporationTypes) iI).getHeadquarterChar()));
			}
		}
		else
		{
			if (pCity->isActiveCorporation((CorporationTypes)iI))
			{
				szBuffer.append(CvWString::format(L"%c", GC.getCorporationInfo((CorporationTypes) iI).getChar()));
			}
		}
	}

	if (pCity->getTeam() == GC.getGameINLINE().getActiveTeam())
	{
		if (pCity->isPower())
		{
			szBuffer.append(CvWString::format(L"%c", gDLL->getSymbolID(POWER_CHAR)));
		}
	}

	// XXX out this in bottom bar???
	if (pCity->isOccupation())
	{
		szBuffer.append(CvWString::format(L" (%c:%d)", gDLL->getSymbolID(OCCUPATION_CHAR), pCity->getOccupationTimer()));
	}

	// defense icon and text
	//if (pCity->getTeam() != GC.getGameINLINE().getActiveTeam())
	{
		if (pCity->isVisible(GC.getGameINLINE().getActiveTeam(), true))
		{
			int iDefenseModifier = pCity->getDefenseModifier(GC.getGameINLINE().selectionListIgnoreBuildingDefense());

			if (iDefenseModifier != 0)
			{
				szBuffer.append(CvWString::format(L" %c:%s%d%%", gDLL->getSymbolID(DEFENSE_CHAR), ((iDefenseModifier > 0) ? "+" : ""), iDefenseModifier));
			}
		}
	}

//FfH: Added by Kael 07/02/2008
	if (pCity->getCivilizationType() != GET_PLAYER(pCity->getOwnerINLINE()).getCivilizationType())
	{
		szBuffer.append(CvWString::format(L" (%s)", GC.getCivilizationInfo(pCity->getCivilizationType()).getShortDescription()));
	}
//FfH: End Add

}

void CvGameTextMgr::buildCityBillboardCityNameString( CvWStringBuffer& szBuffer, CvCity* pCity)
{
	szBuffer.assign(pCity->getName());

	if (pCity->canBeSelected())
	{
		if (gDLL->getGraphicOption(GRAPHICOPTION_CITY_DETAIL))
		{
			if (pCity->foodDifference() > 0)
			{
				int iTurns = pCity->getFoodTurnsLeft();

				if ((iTurns > 1) || !(pCity->AI_isEmphasizeAvoidGrowth()))
				{
					if (iTurns < MAX_INT)
					{
						szBuffer.append(CvWString::format(L" (%d)", iTurns));
					}
				}
			}
// BUG - Starvation Turns - start
			else if (pCity->foodDifference() < 0 && getBugOptionBOOL("CityBar__StarvationTurns", true, "BUG_CITYBAR_STARVATION_TURNS"))
			{
				int iFoodDifference = pCity->foodDifference();
				if (pCity->getFood() + iFoodDifference >= 0)
				{
					int iTurns = pCity->getFood() / -iFoodDifference + 1;
					szBuffer.append(CvWString::format(L" (%d)", iTurns));
				}
				else
				{
					szBuffer.append(L" (!!!)");
				}
			}
// BUG - Starvation Turns - end
		}
	}
	
//FfH: Added by Kael 11/07/2007
    if (pCity->isSettlement())
    {
        szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_SETTLEMENT_TAG"));
    }
//FfH: End Add

}

void CvGameTextMgr::buildCityBillboardProductionString( CvWStringBuffer& szBuffer, CvCity* pCity)
{
	if (pCity->getOrderQueueLength() > 0)
	{
		szBuffer.assign(pCity->getProductionName());

		if (gDLL->getGraphicOption(GRAPHICOPTION_CITY_DETAIL))
		{
			int iTurns = pCity->getProductionTurnsLeft();

			if (iTurns < MAX_INT)
			{
				szBuffer.append(CvWString::format(L" (%d)", iTurns));
			}
		}
	}
	else
	{
		szBuffer.clear();
	}
}


void CvGameTextMgr::buildCityBillboardCitySizeString( CvWStringBuffer& szBuffer, CvCity* pCity, const NiColorA& kColor)
{
#define CAPARAMS(c) (int)((c).r * 255.0f), (int)((c).g * 255.0f), (int)((c).b * 255.0f), (int)((c).a * 255.0f)
	szBuffer.assign(CvWString::format(SETCOLR L"%d" ENDCOLR, CAPARAMS(kColor), pCity->getPopulation()));
#undef CAPARAMS
}

void CvGameTextMgr::getCityBillboardFoodbarColors(CvCity* pCity, std::vector<NiColorA>& aColors)
{
	aColors.resize(NUM_INFOBAR_TYPES);
	aColors[INFOBAR_STORED] = GC.getColorInfo((ColorTypes)(GC.getYieldInfo(YIELD_FOOD).getColorType())).getColor();
	aColors[INFOBAR_RATE] = aColors[INFOBAR_STORED];
	aColors[INFOBAR_RATE].a = 0.5f;
	aColors[INFOBAR_RATE_EXTRA] = GC.getColorInfo((ColorTypes)GC.getInfoTypeForString("COLOR_NEGATIVE_RATE")).getColor();
	aColors[INFOBAR_EMPTY] = GC.getColorInfo((ColorTypes)GC.getInfoTypeForString("COLOR_EMPTY")).getColor();
}

void CvGameTextMgr::getCityBillboardProductionbarColors(CvCity* pCity, std::vector<NiColorA>& aColors)
{
	aColors.resize(NUM_INFOBAR_TYPES);
	aColors[INFOBAR_STORED] = GC.getColorInfo((ColorTypes)(GC.getYieldInfo(YIELD_PRODUCTION).getColorType())).getColor();
	aColors[INFOBAR_RATE] = aColors[INFOBAR_STORED];
	aColors[INFOBAR_RATE].a = 0.5f;
	aColors[INFOBAR_RATE_EXTRA] = GC.getColorInfo((ColorTypes)(GC.getYieldInfo(YIELD_FOOD).getColorType())).getColor();
	aColors[INFOBAR_RATE_EXTRA].a = 0.5f;
	aColors[INFOBAR_EMPTY] = GC.getColorInfo((ColorTypes)GC.getInfoTypeForString("COLOR_EMPTY")).getColor();
}


void CvGameTextMgr::setScoreHelp(CvWStringBuffer &szString, PlayerTypes ePlayer)
{
	if (NO_PLAYER != ePlayer)
	{
		CvPlayer& player = GET_PLAYER(ePlayer);

		int iPop = player.getPopScore();
		int iMaxPop = GC.getGameINLINE().getMaxPopulation();
		int iPopScore = 0;
		if (iMaxPop > 0)
		{
			iPopScore = (GC.getDefineINT("SCORE_POPULATION_FACTOR") * iPop) / iMaxPop;
		}
		int iLand = player.getLandScore();
		int iMaxLand = GC.getGameINLINE().getMaxLand();
		int iLandScore = 0;
		if (iMaxLand > 0)
		{
			iLandScore = (GC.getDefineINT("SCORE_LAND_FACTOR") * iLand) / iMaxLand;
		}
		int iTech = player.getTechScore();
		int iMaxTech = GC.getGameINLINE().getMaxTech();
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                      02/24/10                                jdog5000      */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
		int iTechScore = 0;
		if( iMaxTech > 0 )
		{
			iTechScore = (GC.getDefineINT("SCORE_TECH_FACTOR") * iTech) / iMaxTech;
		}
		int iWonders = player.getWondersScore();
		int iMaxWonders = GC.getGameINLINE().getMaxWonders();
		int iWondersScore = 0;
		if( iMaxWonders > 0 )
		{
			iWondersScore = (GC.getDefineINT("SCORE_WONDER_FACTOR") * iWonders) / iMaxWonders;
		}
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                       END                                                  */
/************************************************************************************************/
		int iTotalScore = iPopScore + iLandScore + iTechScore + iWondersScore;
		int iVictoryScore = player.calculateScore(true, true);
		if (iTotalScore == player.calculateScore())
		{
			szString.append(gDLL->getText("TXT_KEY_SCORE_BREAKDOWN", iPopScore, iPop, iMaxPop, iLandScore, iLand, iMaxLand, iTechScore, iTech, iMaxTech, iWondersScore, iWonders, iMaxWonders, iTotalScore, iVictoryScore));
		}
	}
}

void CvGameTextMgr::setEventHelp(CvWStringBuffer& szBuffer, EventTypes eEvent, int iEventTriggeredId, PlayerTypes ePlayer)
{
	if (NO_EVENT == eEvent || NO_PLAYER == ePlayer)
	{
		return;
	}

	CvEventInfo& kEvent = GC.getEventInfo(eEvent);
	CvPlayer& kActivePlayer = GET_PLAYER(ePlayer);
	EventTriggeredData* pTriggeredData = kActivePlayer.getEventTriggered(iEventTriggeredId);

	if (NULL == pTriggeredData)
	{
		return;
	}

	CvCity* pCity = kActivePlayer.getCity(pTriggeredData->m_iCityId);
	CvCity* pOtherPlayerCity = NULL;
	CvPlot* pPlot = GC.getMapINLINE().plot(pTriggeredData->m_iPlotX, pTriggeredData->m_iPlotY);
	CvUnit* pUnit = kActivePlayer.getUnit(pTriggeredData->m_iUnitId);

	if (NO_PLAYER != pTriggeredData->m_eOtherPlayer)
	{
		pOtherPlayerCity = GET_PLAYER(pTriggeredData->m_eOtherPlayer).getCity(pTriggeredData->m_iOtherPlayerCityId);
	}

	CvWString szCity = gDLL->getText("TXT_KEY_EVENT_THE_CITY");
	if (NULL != pCity && kEvent.isCityEffect())
	{
		szCity = pCity->getNameKey();
	}
	else if (NULL != pOtherPlayerCity && kEvent.isOtherPlayerCityEffect())
	{
		szCity = pOtherPlayerCity->getNameKey();
	}

	CvWString szUnit = gDLL->getText("TXT_KEY_EVENT_THE_UNIT");
	if (NULL != pUnit)
	{
		szUnit = pUnit->getNameKey();
	}

	CvWString szReligion = gDLL->getText("TXT_KEY_EVENT_THE_RELIGION");
	if (NO_RELIGION != pTriggeredData->m_eReligion)
	{
		szReligion = GC.getReligionInfo(pTriggeredData->m_eReligion).getTextKeyWide();
	}

	eventGoldHelp(szBuffer, eEvent, ePlayer, pTriggeredData->m_eOtherPlayer);

	eventTechHelp(szBuffer, eEvent, kActivePlayer.getBestEventTech(eEvent, pTriggeredData->m_eOtherPlayer), ePlayer, pTriggeredData->m_eOtherPlayer);

	if (NO_PLAYER != pTriggeredData->m_eOtherPlayer && NO_BONUS != kEvent.getBonusGift())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_EVENT_GIFT_BONUS_TO_PLAYER", GC.getBonusInfo((BonusTypes)kEvent.getBonusGift()).getTextKeyWide(), GET_PLAYER(pTriggeredData->m_eOtherPlayer).getNameKey()));
	}

	if (kEvent.getHappy() != 0)
	{
		if (NO_PLAYER != pTriggeredData->m_eOtherPlayer)
		{
			if (kEvent.getHappy() > 0)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_HAPPY_FROM_PLAYER", kEvent.getHappy(), kEvent.getHappy(), GET_PLAYER(pTriggeredData->m_eOtherPlayer).getNameKey()));
			}
			else
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_HAPPY_TO_PLAYER", -kEvent.getHappy(), -kEvent.getHappy(), GET_PLAYER(pTriggeredData->m_eOtherPlayer).getNameKey()));
			}
		}
		else
		{
			if (kEvent.getHappy() > 0)
			{
				if (kEvent.isCityEffect() || kEvent.isOtherPlayerCityEffect())
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_HAPPY_CITY", kEvent.getHappy(), szCity.GetCString()));
				}
				else
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_HAPPY", kEvent.getHappy()));
				}
			}
			else
			{
				if (kEvent.isCityEffect() || kEvent.isOtherPlayerCityEffect())
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_UNHAPPY_CITY", -kEvent.getHappy(), szCity.GetCString()));
				}
				else
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_UNHAPPY", -kEvent.getHappy()));
				}
			}
		}
	}

	if (kEvent.getHealth() != 0)
	{
		if (NO_PLAYER != pTriggeredData->m_eOtherPlayer)
		{
			if (kEvent.getHealth() > 0)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_HEALTH_FROM_PLAYER", kEvent.getHealth(), kEvent.getHealth(), GET_PLAYER(pTriggeredData->m_eOtherPlayer).getNameKey()));
			}
			else
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_HEALTH_TO_PLAYER", -kEvent.getHealth(), -kEvent.getHealth(), GET_PLAYER(pTriggeredData->m_eOtherPlayer).getNameKey()));
			}
		}
		else
		{
			if (kEvent.getHealth() > 0)
			{
				if (kEvent.isCityEffect() || kEvent.isOtherPlayerCityEffect())
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_HEALTH_CITY", kEvent.getHealth(), szCity.GetCString()));
				}
				else
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_HEALTH", kEvent.getHealth()));
				}
			}
			else
			{
				if (kEvent.isCityEffect() || kEvent.isOtherPlayerCityEffect())
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_UNHEALTH_CITY", -kEvent.getHealth(), szCity.GetCString()));
				}
				else
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_UNHEALTH", -kEvent.getHealth()));
				}
			}
		}
	}

	if (kEvent.getHurryAnger() != 0)
	{
		if (kEvent.isCityEffect() || kEvent.isOtherPlayerCityEffect())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_HURRY_ANGER_CITY", kEvent.getHurryAnger(), szCity.GetCString()));
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_HURRY_ANGER", kEvent.getHurryAnger()));
		}
	}

	if (kEvent.getHappyTurns() > 0)
	{
		if (kEvent.isCityEffect() || kEvent.isOtherPlayerCityEffect())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_TEMP_HAPPY_CITY", GC.getDefineINT("TEMP_HAPPY"), kEvent.getHappyTurns(), szCity.GetCString()));
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_TEMP_HAPPY", GC.getDefineINT("TEMP_HAPPY"), kEvent.getHappyTurns()));
		}
	}

	if (kEvent.getFood() != 0)
	{
		if (kEvent.isCityEffect() || kEvent.isOtherPlayerCityEffect())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_FOOD_CITY", kEvent.getFood(), szCity.GetCString()));
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_FOOD", kEvent.getFood()));
		}
	}

	if (kEvent.getFoodPercent() != 0)
	{
		if (kEvent.isCityEffect() || kEvent.isOtherPlayerCityEffect())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_FOOD_PERCENT_CITY", kEvent.getFoodPercent(), szCity.GetCString()));
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_FOOD_PERCENT", kEvent.getFoodPercent()));
		}
	}

	if (kEvent.getRevoltTurns() > 0)
	{
		if (kEvent.isCityEffect() || kEvent.isOtherPlayerCityEffect())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_REVOLT_TURNS", kEvent.getRevoltTurns(), szCity.GetCString()));
		}
	}

	if (0 != kEvent.getSpaceProductionModifier())
	{
		if (kEvent.isCityEffect() || kEvent.isOtherPlayerCityEffect())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_SPACE_PRODUCTION_CITY", kEvent.getSpaceProductionModifier(), szCity.GetCString()));
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_SPACESHIP_MOD_ALL_CITIES", kEvent.getSpaceProductionModifier()));
		}
	}

	if (kEvent.getMaxPillage() > 0)
	{
		if (kEvent.isCityEffect() || kEvent.isOtherPlayerCityEffect())
		{
			if (kEvent.getMaxPillage() == kEvent.getMinPillage())
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_PILLAGE_CITY", kEvent.getMinPillage(), szCity.GetCString()));
			}
			else
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_PILLAGE_RANGE_CITY", kEvent.getMinPillage(), kEvent.getMaxPillage(), szCity.GetCString()));
			}
		}
		else
		{
			if (kEvent.getMaxPillage() == kEvent.getMinPillage())
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_PILLAGE", kEvent.getMinPillage()));
			}
			else
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_PILLAGE_RANGE", kEvent.getMinPillage(), kEvent.getMaxPillage()));
			}
		}
	}

	for (int i = 0; i < GC.getNumSpecialistInfos(); ++i)
	{
		if (kEvent.getFreeSpecialistCount(i) > 0)
		{
			if (kEvent.isCityEffect() || kEvent.isOtherPlayerCityEffect())
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_FREE_SPECIALIST", kEvent.getFreeSpecialistCount(i), GC.getSpecialistInfo((SpecialistTypes)i).getTextKeyWide(), szCity.GetCString()));
			}
		}
	}

	if (kEvent.getPopulationChange() != 0)
	{
		if (kEvent.isCityEffect() || kEvent.isOtherPlayerCityEffect())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_POPULATION_CHANGE_CITY", kEvent.getPopulationChange(), szCity.GetCString()));
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_POPULATION_CHANGE", kEvent.getPopulationChange()));
		}
	}

	if (kEvent.getCulture() != 0)
	{
		if (kEvent.isCityEffect() || kEvent.isOtherPlayerCityEffect())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_CULTURE_CITY", kEvent.getCulture(), szCity.GetCString()));
		}
		else
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_CULTURE", kEvent.getCulture()));
		}
	}

	if (kEvent.getUnitClass() != NO_UNITCLASS)
	{
		CivilizationTypes eCiv = kActivePlayer.getCivilizationType();
		if (NO_CIVILIZATION != eCiv)
		{
			UnitTypes eUnit = (UnitTypes)GC.getCivilizationInfo(eCiv).getCivilizationUnits(kEvent.getUnitClass());
			if (eUnit != NO_UNIT)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_BONUS_UNIT", kEvent.getNumUnits(), GC.getUnitInfo(eUnit).getTextKeyWide()));
			}
		}
	}

	if (kEvent.getBuildingClass() != NO_BUILDINGCLASS)
	{
		CivilizationTypes eCiv = kActivePlayer.getCivilizationType();
		if (NO_CIVILIZATION != eCiv)
		{
			BuildingTypes eBuilding = (BuildingTypes)GC.getCivilizationInfo(eCiv).getCivilizationBuildings(kEvent.getBuildingClass());
			if (eBuilding != NO_BUILDING)
			{
				if (kEvent.getBuildingChange() > 0)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_BONUS_BUILDING", GC.getBuildingInfo(eBuilding).getTextKeyWide()));
				}
				else if (kEvent.getBuildingChange() < 0)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_REMOVE_BUILDING", GC.getBuildingInfo(eBuilding).getTextKeyWide()));
				}
			}
		}
	}

	if (kEvent.getNumBuildingYieldChanges() > 0)
	{
		CvWStringBuffer szYield;
		for (int iBuildingClass = 0; iBuildingClass < GC.getNumBuildingClassInfos(); ++iBuildingClass)
		{
			CivilizationTypes eCiv = kActivePlayer.getCivilizationType();
			if (NO_CIVILIZATION != eCiv)
			{
				BuildingTypes eBuilding = (BuildingTypes)GC.getCivilizationInfo(eCiv).getCivilizationBuildings(iBuildingClass);
				if (eBuilding != NO_BUILDING)
				{
					int aiYields[NUM_YIELD_TYPES];
					for (int iYield = 0; iYield < NUM_YIELD_TYPES; ++iYield)
					{
						aiYields[iYield] = kEvent.getBuildingYieldChange(iBuildingClass, iYield);
					}

					szYield.clear();
					setYieldChangeHelp(szYield, L"", L"", L"", aiYields, false, false);
					if (!szYield.isEmpty())
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_EVENT_YIELD_CHANGE_BUILDING", GC.getBuildingInfo(eBuilding).getTextKeyWide(), szYield.getCString()));
					}
				}
			}
		}
	}

	if (kEvent.getNumBuildingCommerceChanges() > 0)
	{
		CvWStringBuffer szCommerce;
		for (int iBuildingClass = 0; iBuildingClass < GC.getNumBuildingClassInfos(); ++iBuildingClass)
		{
			CivilizationTypes eCiv = kActivePlayer.getCivilizationType();
			if (NO_CIVILIZATION != eCiv)
			{
				BuildingTypes eBuilding = (BuildingTypes)GC.getCivilizationInfo(eCiv).getCivilizationBuildings(iBuildingClass);
				if (eBuilding != NO_BUILDING)
				{
					int aiCommerces[NUM_COMMERCE_TYPES];
					for (int iCommerce = 0; iCommerce < NUM_COMMERCE_TYPES; ++iCommerce)
					{
						aiCommerces[iCommerce] = kEvent.getBuildingCommerceChange(iBuildingClass, iCommerce);
					}

					szCommerce.clear();
					setCommerceChangeHelp(szCommerce, L"", L"", L"", aiCommerces, false, false);
					if (!szCommerce.isEmpty())
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_EVENT_YIELD_CHANGE_BUILDING", GC.getBuildingInfo(eBuilding).getTextKeyWide(), szCommerce.getCString()));
					}
				}
			}
		}
	}

	if (kEvent.getNumBuildingHappyChanges() > 0)
	{
		for (int iBuildingClass = 0; iBuildingClass < GC.getNumBuildingClassInfos(); ++iBuildingClass)
		{
			CivilizationTypes eCiv = kActivePlayer.getCivilizationType();
			if (NO_CIVILIZATION != eCiv)
			{
				BuildingTypes eBuilding = (BuildingTypes)GC.getCivilizationInfo(eCiv).getCivilizationBuildings(iBuildingClass);
				if (eBuilding != NO_BUILDING)
				{
					int iHappy = kEvent.getBuildingHappyChange(iBuildingClass);
					if (iHappy > 0)
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_EVENT_HAPPY_BUILDING", GC.getBuildingInfo(eBuilding).getTextKeyWide(), iHappy, gDLL->getSymbolID(HAPPY_CHAR)));
					}
					else if (iHappy < 0)
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_EVENT_HAPPY_BUILDING", GC.getBuildingInfo(eBuilding).getTextKeyWide(), -iHappy, gDLL->getSymbolID(UNHAPPY_CHAR)));
					}
				}
			}
		}
	}

	if (kEvent.getNumBuildingHealthChanges() > 0)
	{
		for (int iBuildingClass = 0; iBuildingClass < GC.getNumBuildingClassInfos(); ++iBuildingClass)
		{
			CivilizationTypes eCiv = kActivePlayer.getCivilizationType();
			if (NO_CIVILIZATION != eCiv)
			{
				BuildingTypes eBuilding = (BuildingTypes)GC.getCivilizationInfo(eCiv).getCivilizationBuildings(iBuildingClass);
				if (eBuilding != NO_BUILDING)
				{
					int iHealth = kEvent.getBuildingHealthChange(iBuildingClass);
					if (iHealth > 0)
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_EVENT_HAPPY_BUILDING", GC.getBuildingInfo(eBuilding).getTextKeyWide(), iHealth, gDLL->getSymbolID(HEALTHY_CHAR)));
					}
					else if (iHealth < 0)
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_EVENT_HAPPY_BUILDING", GC.getBuildingInfo(eBuilding).getTextKeyWide(), -iHealth, gDLL->getSymbolID(UNHEALTHY_CHAR)));
					}
				}
			}
		}
	}

	if (kEvent.getFeatureChange() > 0)
	{
		if (kEvent.getFeature() != NO_FEATURE)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_FEATURE_GROWTH", GC.getFeatureInfo((FeatureTypes)kEvent.getFeature()).getTextKeyWide()));
		}
	}
	else if (kEvent.getFeatureChange() < 0)
	{
		if (NULL != pPlot && NO_FEATURE != pPlot->getFeatureType())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_FEATURE_REMOVE", GC.getFeatureInfo(pPlot->getFeatureType()).getTextKeyWide()));
		}
	}

	if (kEvent.getImprovementChange() > 0)
	{
		if (kEvent.getImprovement() != NO_IMPROVEMENT)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_IMPROVEMENT_GROWTH", GC.getImprovementInfo((ImprovementTypes)kEvent.getImprovement()).getTextKeyWide()));
		}
	}
	else if (kEvent.getImprovementChange() < 0)
	{
		if (NULL != pPlot && NO_IMPROVEMENT != pPlot->getImprovementType())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_IMPROVEMENT_REMOVE", GC.getImprovementInfo(pPlot->getImprovementType()).getTextKeyWide()));
		}
	}

	if (kEvent.getBonusChange() > 0)
	{
		if (kEvent.getBonus() != NO_BONUS)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_BONUS_GROWTH", GC.getBonusInfo((BonusTypes)kEvent.getBonus()).getTextKeyWide()));
		}
	}
	else if (kEvent.getBonusChange() < 0)
	{
		if (NULL != pPlot && NO_BONUS != pPlot->getBonusType())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_BONUS_REMOVE", GC.getBonusInfo(pPlot->getBonusType()).getTextKeyWide()));
		}
	}

	if (kEvent.getRouteChange() > 0)
	{
		if (kEvent.getRoute() != NO_ROUTE)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_ROUTE_GROWTH", GC.getRouteInfo((RouteTypes)kEvent.getRoute()).getTextKeyWide()));
		}
	}
	else if (kEvent.getRouteChange() < 0)
	{
		if (NULL != pPlot && NO_ROUTE != pPlot->getRouteType())
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_ROUTE_REMOVE", GC.getRouteInfo(pPlot->getRouteType()).getTextKeyWide()));
		}
	}

	int aiYields[NUM_YIELD_TYPES];
	for (int i = 0; i < NUM_YIELD_TYPES; ++i)
	{
		aiYields[i] = kEvent.getPlotExtraYield(i);
	}

	CvWStringBuffer szYield;
	setYieldChangeHelp(szYield, L"", L"", L"", aiYields, false, false);
	if (!szYield.isEmpty())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_EVENT_YIELD_CHANGE_PLOT", szYield.getCString()));
	}

	if (NO_BONUS != kEvent.getBonusRevealed())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_EVENT_BONUS_REVEALED", GC.getBonusInfo((BonusTypes)kEvent.getBonusRevealed()).getTextKeyWide()));
	}

	if (0 != kEvent.getUnitExperience())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_EVENT_UNIT_EXPERIENCE", kEvent.getUnitExperience(), szUnit.GetCString()));
	}

	if (0 != kEvent.isDisbandUnit())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_EVENT_UNIT_DISBAND", szUnit.GetCString()));
	}

	if (NO_PROMOTION != kEvent.getUnitPromotion())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_EVENT_UNIT_PROMOTION", szUnit.GetCString(), GC.getPromotionInfo((PromotionTypes)kEvent.getUnitPromotion()).getTextKeyWide()));
	}

	for (int i = 0; i < GC.getNumUnitCombatInfos(); ++i)
	{
		if (NO_PROMOTION != kEvent.getUnitCombatPromotion(i))
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_UNIT_COMBAT_PROMOTION", GC.getUnitCombatInfo((UnitCombatTypes)i).getTextKeyWide(), GC.getPromotionInfo((PromotionTypes)kEvent.getUnitCombatPromotion(i)).getTextKeyWide()));
		}
	}

	for (int i = 0; i < GC.getNumUnitClassInfos(); ++i)
	{
		if (NO_PROMOTION != kEvent.getUnitClassPromotion(i))
		{
			UnitTypes ePromotedUnit = ((UnitTypes)(GC.getCivilizationInfo(kActivePlayer.getCivilizationType()).getCivilizationUnits(i)));
			if (NO_UNIT != ePromotedUnit)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_UNIT_CLASS_PROMOTION", GC.getUnitInfo(ePromotedUnit).getTextKeyWide(), GC.getPromotionInfo((PromotionTypes)kEvent.getUnitClassPromotion(i)).getTextKeyWide()));
			}
		}
	}

	if (kEvent.getConvertOwnCities() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_EVENT_CONVERT_OWN_CITIES", kEvent.getConvertOwnCities(), szReligion.GetCString()));
	}

	if (kEvent.getConvertOtherCities() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_EVENT_CONVERT_OTHER_CITIES", kEvent.getConvertOtherCities(), szReligion.GetCString()));
	}

	if (NO_PLAYER != pTriggeredData->m_eOtherPlayer)
	{
		if (kEvent.getAttitudeModifier() > 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_ATTITUDE_GOOD", kEvent.getAttitudeModifier(), GET_PLAYER(pTriggeredData->m_eOtherPlayer).getNameKey()));
		}
		else if (kEvent.getAttitudeModifier() < 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_ATTITUDE_BAD", kEvent.getAttitudeModifier(), GET_PLAYER(pTriggeredData->m_eOtherPlayer).getNameKey()));
		}
	}

	if (NO_PLAYER != pTriggeredData->m_eOtherPlayer)
	{
		TeamTypes eWorstEnemy = GET_TEAM(GET_PLAYER(pTriggeredData->m_eOtherPlayer).getTeam()).AI_getWorstEnemy();
		if (NO_TEAM != eWorstEnemy)
		{
			if (kEvent.getTheirEnemyAttitudeModifier() > 0)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_ATTITUDE_GOOD", kEvent.getTheirEnemyAttitudeModifier(), GET_TEAM(eWorstEnemy).getName().GetCString()));
			}
			else if (kEvent.getTheirEnemyAttitudeModifier() < 0)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_ATTITUDE_BAD", kEvent.getTheirEnemyAttitudeModifier(), GET_TEAM(eWorstEnemy).getName().GetCString()));
			}
		}
	}

	if (NO_PLAYER != pTriggeredData->m_eOtherPlayer)
	{
		if (kEvent.getEspionagePoints() > 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_ESPIONAGE_POINTS", kEvent.getEspionagePoints(), GET_PLAYER(pTriggeredData->m_eOtherPlayer).getNameKey()));
		}
		else if (kEvent.getEspionagePoints() < 0)
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_EVENT_ESPIONAGE_COST", -kEvent.getEspionagePoints()));
		}
	}

	if (kEvent.isGoldenAge())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_EVENT_GOLDEN_AGE"));
	}

	if (0 != kEvent.getFreeUnitSupport())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_EVENT_FREE_UNIT_SUPPORT", kEvent.getFreeUnitSupport()));
	}

	if (0 != kEvent.getInflationModifier())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_EVENT_INFLATION_MODIFIER", kEvent.getInflationModifier()));
	}

	if (kEvent.isDeclareWar())
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_EVENT_DECLARE_WAR", GET_PLAYER(pTriggeredData->m_eOtherPlayer).getCivilizationAdjectiveKey()));
	}

	if (kEvent.getUnitImmobileTurns() > 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_EVENT_IMMOBILE_UNIT", kEvent.getUnitImmobileTurns(), szUnit.GetCString()));
	}

//FfH: Added by Kael 01/21/2008
	if (kEvent.getCrime() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_EVENT_CRIME", kEvent.getCrime()));
	}
	if (kEvent.getGlobalCounter() != 0)
	{
		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_EVENT_GLOBAL_COUNTER", kEvent.getGlobalCounter()));
	}
//FfH: End Add

	if (!CvWString(kEvent.getPythonHelp()).empty())
	{
		CvWString szHelp;
		CyArgsList argsList;
		argsList.add(eEvent);
		argsList.add(gDLL->getPythonIFace()->makePythonObject(pTriggeredData));

		gDLL->getPythonIFace()->callFunction(PYRandomEventModule, kEvent.getPythonHelp(), argsList.makeFunctionArgs(), &szHelp);

		szBuffer.append(NEWLINE);
		szBuffer.append(szHelp);
	}

	CvWStringBuffer szTemp;
	for (int i = 0; i < GC.getNumEventInfos(); ++i)
	{
		if (0 == kEvent.getAdditionalEventTime(i))
		{
			if (kEvent.getAdditionalEventChance(i) > 0)
			{
				if (GET_PLAYER(GC.getGameINLINE().getActivePlayer()).canDoEvent((EventTypes)i, *pTriggeredData))
				{
					szTemp.clear();
					setEventHelp(szTemp, (EventTypes)i, iEventTriggeredId, ePlayer);

					if (!szTemp.isEmpty())
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_EVENT_ADDITIONAL_CHANCE", kEvent.getAdditionalEventChance(i), L""));
						szBuffer.append(NEWLINE);
						szBuffer.append(szTemp);
					}
				}
			}
		}
		else
		{
			szTemp.clear();
			setEventHelp(szTemp, (EventTypes)i, iEventTriggeredId, ePlayer);

			if (!szTemp.isEmpty())
			{
				CvWString szDelay = gDLL->getText("TXT_KEY_EVENT_DELAY_TURNS", (GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getGrowthPercent() * kEvent.getAdditionalEventTime((EventTypes)i)) / 100);

				if (kEvent.getAdditionalEventChance(i) > 0)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_ADDITIONAL_CHANCE", kEvent.getAdditionalEventChance(i), szDelay.GetCString()));
				}
				else
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_DELAY", szDelay.GetCString()));
				}

				szBuffer.append(NEWLINE);
				szBuffer.append(szTemp);
			}
		}
	}

	if (NO_TECH != kEvent.getPrereqTech())
	{
		if (!GET_TEAM(kActivePlayer.getTeam()).isHasTech((TechTypes)kEvent.getPrereqTech()))
		{
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_REQUIRES_STRING", GC.getTechInfo((TechTypes)(kEvent.getPrereqTech())).getTextKeyWide()));
		}
	}

//FfH: Added by Kael 01/21/2008
	if (kEvent.getPrereqAlignment() != NO_ALIGNMENT)
	{
        if (kActivePlayer.getAlignment() != kEvent.getPrereqAlignment())
        {
            szBuffer.append(NEWLINE);
            szBuffer.append(gDLL->getText("TXT_KEY_CIVIC_REQUIRES", GC.getAlignmentInfo((AlignmentTypes)kEvent.getPrereqAlignment()).getDescription()));
        }
	}
	if (kEvent.getPrereqBonus() != NO_BONUS)
	{
        if (!kActivePlayer.hasBonus((BonusTypes)kEvent.getPrereqBonus()))
        {
            szBuffer.append(NEWLINE);
            szBuffer.append(gDLL->getText("TXT_KEY_CIVIC_REQUIRES", GC.getBonusInfo((BonusTypes)kEvent.getPrereqBonus()).getDescription()));
        }
	}
	if (kEvent.getPrereqCivilization() != NO_CIVILIZATION)
	{
        if (kActivePlayer.getCivilizationType() != kEvent.getPrereqCivilization())
        {
            szBuffer.append(NEWLINE);
            szBuffer.append(gDLL->getText("TXT_KEY_CIVIC_REQUIRES", GC.getCivilizationInfo((CivilizationTypes)kEvent.getPrereqCivilization()).getDescription()));
        }
	}
	if (kEvent.getPrereqCorporation() != NO_CORPORATION)
	{
		if (pCity != NULL)
		{
            if (!pCity->isHasCorporation((CorporationTypes)kEvent.getPrereqCorporation()))
            {
                szBuffer.append(NEWLINE);
                szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_REQUIRES_STRING", GC.getCorporationInfo((CorporationTypes)kEvent.getPrereqCorporation()).getDescription()));
            }
		}
	}
	if (kEvent.getPrereqReligion() != NO_RELIGION)
	{
		if (pCity != NULL)
		{
            if (!pCity->isHasReligion((ReligionTypes)kEvent.getPrereqReligion()))
            {
               szBuffer.append(NEWLINE);
                szBuffer.append(gDLL->getText("TXT_KEY_BUILDING_REQUIRES_STRING", GC.getReligionInfo((ReligionTypes)(kEvent.getPrereqReligion())).getDescription()));
            }
		}
	}
	if (kEvent.getPrereqStateReligion() != NO_RELIGION)
	{
        if (kActivePlayer.getStateReligion() != kEvent.getPrereqStateReligion())
        {
            szBuffer.append(NEWLINE);
            szBuffer.append(gDLL->getText("TXT_KEY_CIVIC_REQUIRES", GC.getReligionInfo((ReligionTypes)kEvent.getPrereqStateReligion()).getDescription()));
        }
    }
//FfH: End Add

	bool done = false;
	while(!done)
	{
		done = true;
		if(!szBuffer.isEmpty())
		{
			const wchar* wideChar = szBuffer.getCString();
			if(wideChar[0] == L'\n')
			{
				CvWString tempString(&wideChar[1]);
				szBuffer.clear();
				szBuffer.append(tempString);
				done = false;
			}
		}
	}
}

void CvGameTextMgr::eventTechHelp(CvWStringBuffer& szBuffer, EventTypes eEvent, TechTypes eTech, PlayerTypes eActivePlayer, PlayerTypes eOtherPlayer)
{
	CvEventInfo& kEvent = GC.getEventInfo(eEvent);

	if (eTech != NO_TECH)
	{
		if (100 == kEvent.getTechPercent())
		{
			if (NO_PLAYER != eOtherPlayer)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_TECH_GAINED_FROM_PLAYER", GC.getTechInfo(eTech).getTextKeyWide(), GET_PLAYER(eOtherPlayer).getNameKey()));
			}
			else
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_TECH_GAINED", GC.getTechInfo(eTech).getTextKeyWide()));
			}
		}
		else if (0 != kEvent.getTechPercent())
		{
			CvTeam& kTeam = GET_TEAM(GET_PLAYER(eActivePlayer).getTeam());
			int iBeakers = (kTeam.getResearchCost(eTech) * kEvent.getTechPercent()) / 100;
			if (kEvent.getTechPercent() > 0)
			{
				iBeakers = std::min(kTeam.getResearchLeft(eTech), iBeakers);
			}
			else if (kEvent.getTechPercent() < 0)
			{
				iBeakers = std::max(kTeam.getResearchLeft(eTech) - kTeam.getResearchCost(eTech), iBeakers);
			}

			if (NO_PLAYER != eOtherPlayer)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_TECH_GAINED_FROM_PLAYER_PERCENT", iBeakers, GC.getTechInfo(eTech).getTextKeyWide(), GET_PLAYER(eOtherPlayer).getNameKey()));
			}
			else
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_EVENT_TECH_GAINED_PERCENT", iBeakers, GC.getTechInfo(eTech).getTextKeyWide()));
			}
		}
	}
}

void CvGameTextMgr::eventGoldHelp(CvWStringBuffer& szBuffer, EventTypes eEvent, PlayerTypes ePlayer, PlayerTypes eOtherPlayer)
{
	CvEventInfo& kEvent = GC.getEventInfo(eEvent);
	CvPlayer& kPlayer = GET_PLAYER(ePlayer);

	int iGold1 = kPlayer.getEventCost(eEvent, eOtherPlayer, false);
	int iGold2 = kPlayer.getEventCost(eEvent, eOtherPlayer, true);

	if (0 != iGold1 || 0 != iGold2)
	{
		if (iGold1 == iGold2)
		{
			if (NO_PLAYER != eOtherPlayer && kEvent.isGoldToPlayer())
			{
				if (iGold1 > 0)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_GOLD_FROM_PLAYER", iGold1, GET_PLAYER(eOtherPlayer).getNameKey()));
				}
				else
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_GOLD_TO_PLAYER", -iGold1, GET_PLAYER(eOtherPlayer).getNameKey()));
				}
			}
			else
			{
				if (iGold1 > 0)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_GOLD_GAINED", iGold1));
				}
				else
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_GOLD_LOST", -iGold1));
				}
			}
		}
		else
		{
			if (NO_PLAYER != eOtherPlayer && kEvent.isGoldToPlayer())
			{
				if (iGold1 > 0)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_GOLD_RANGE_FROM_PLAYER", iGold1, iGold2, GET_PLAYER(eOtherPlayer).getNameKey()));
				}
				else
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_GOLD_RANGE_TO_PLAYER", -iGold1, -iGold2, GET_PLAYER(eOtherPlayer).getNameKey()));
				}
			}
			else
			{
				if (iGold1 > 0)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_GOLD_RANGE_GAINED", iGold1, iGold2));
				}
				else
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_EVENT_GOLD_RANGE_LOST", -iGold1, iGold2));
				}
			}
		}
	}
}

void CvGameTextMgr::setTradeRouteHelp(CvWStringBuffer &szBuffer, int iRoute, CvCity* pCity)
{
	if (NULL != pCity)
	{
		CvCity* pOtherCity = pCity->getTradeCity(iRoute);

		if (NULL != pOtherCity)
		{
			szBuffer.append(pOtherCity->getName());

			int iProfit = pCity->getBaseTradeProfit(pOtherCity);

			szBuffer.append(NEWLINE);
			CvWString szBaseProfit;
			szBaseProfit.Format(L"%d.%02d", iProfit/100, iProfit%100);
			szBuffer.append(gDLL->getText("TXT_KEY_TRADE_ROUTE_HELP_BASE", szBaseProfit.GetCString()));

			int iModifier = 100;
			int iNewMod;

			for (int iBuilding = 0; iBuilding < GC.getNumBuildingInfos(); ++iBuilding)
			{
				if (pCity->getNumActiveBuilding((BuildingTypes)iBuilding) > 0)
				{
					iNewMod = pCity->getNumActiveBuilding((BuildingTypes)iBuilding) * GC.getBuildingInfo((BuildingTypes)iBuilding).getTradeRouteModifier();
					if (0 != iNewMod)
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_TRADE_ROUTE_MOD_BUILDING", GC.getBuildingInfo((BuildingTypes)iBuilding).getTextKeyWide(), iNewMod));
						iModifier += iNewMod;
					}
				}
			}

			iNewMod = pCity->getPopulationTradeModifier();
			if (0 != iNewMod)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_TRADE_ROUTE_MOD_POPULATION", iNewMod));
				iModifier += iNewMod;
			}

			if (pCity->isConnectedToCapital())
			{
				iNewMod = GC.getDefineINT("CAPITAL_TRADE_MODIFIER");
				if (0 != iNewMod)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_TRADE_ROUTE_MOD_CAPITAL", iNewMod));
					iModifier += iNewMod;
				}
			}

			if (NULL != pOtherCity)
			{
				if (pCity->area() != pOtherCity->area())
				{
					iNewMod = GC.getDefineINT("OVERSEAS_TRADE_MODIFIER");
					if (0 != iNewMod)
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_TRADE_ROUTE_MOD_OVERSEAS", iNewMod));
						iModifier += iNewMod;
					}
				}

				if (pCity->getTeam() != pOtherCity->getTeam())
				{
					iNewMod = pCity->getForeignTradeRouteModifier();
					if (0 != iNewMod)
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_TRADE_ROUTE_MOD_FOREIGN", iNewMod));
						iModifier += iNewMod;
					}

					iNewMod = pCity->getPeaceTradeModifier(pOtherCity->getTeam());
					if (0 != iNewMod)
					{
						szBuffer.append(NEWLINE);
						szBuffer.append(gDLL->getText("TXT_KEY_TRADE_ROUTE_MOD_PEACE", iNewMod));
						iModifier += iNewMod;
					}
				}
			}

			FAssert(pCity->totalTradeModifier(pOtherCity) == iModifier);
			
			// lfgr 10/2019, BUG: Show final trade route yield; Fractional Trade Routes
			iProfit *= iModifier;
			iProfit /= 100;
			FAssert(iProfit == pCity->calculateTradeProfitTimes100(pOtherCity));

			// For some reason, trait and civic modifiers are applied later

			int iPlayerYieldModifier = 100; // Percent

			CvWStringBuffer szPlayerModBuffer;

			// Traits
			for( int eTrait = 0; eTrait < GC.getNumTraitInfos(); eTrait++ ) {
				if( GET_PLAYER( pCity->getOwnerINLINE() ).hasTrait( (TraitTypes) eTrait ) ) {
					CvTraitInfo& kTrait = GC.getTraitInfo( (TraitTypes) eTrait );
					int iMod = kTrait.getTradeYieldModifier( YIELD_COMMERCE );
					if( iMod != 0 ) {
						szPlayerModBuffer.append(NEWLINE);
						szPlayerModBuffer.append(gDLL->getText("TXT_KEY_TRADE_ROUTE_MOD_TRAIT", kTrait.getTextKeyWide(), iMod));
						iPlayerYieldModifier += iMod;
					}
				}
			}

			// Civics
			for( int eCivic = 0; eCivic < GC.getNumCivicInfos(); eCivic++ ) {
				if( GET_PLAYER( pCity->getOwnerINLINE() ).isCivic( (CivicTypes) eCivic ) ) {
					CvCivicInfo& kCivic = GC.getCivicInfo( (CivicTypes) eCivic );
					int iMod = kCivic.getTradeYieldModifier( YIELD_COMMERCE );
					if( iMod != 0 ) {
						szPlayerModBuffer.append(NEWLINE);
						szPlayerModBuffer.append(gDLL->getText("TXT_KEY_TRADE_ROUTE_MOD_CIVIC", kCivic.getTextKeyWide(), iMod));
						iPlayerYieldModifier += iMod;
					}
				}
			}

			int iYield = (std::max( 0, iProfit ) * std::max( 0, iPlayerYieldModifier )) / 100;
			FAssert( iPlayerYieldModifier == GET_PLAYER(pCity->getOwnerINLINE()).getTradeYieldModifier(YIELD_COMMERCE) );
			FAssert(iYield == pCity->calculateTradeYield(YIELD_COMMERCE, iProfit));

			if( ! szPlayerModBuffer.isEmpty() ) {
				szBuffer.append(SEPARATOR);
				szBuffer.append(NEWLINE);
				CvWString szProfit;
				szProfit.Format(L"%d.%02d", iProfit / 100, iProfit % 100);
				szBuffer.append(gDLL->getText("TXT_KEY_TRADE_ROUTE_TOTAL_FRACTIONAL_PROFIT", szProfit.GetCString()));

				szBuffer.append( szPlayerModBuffer );
			}

			szBuffer.append(SEPARATOR);
			szBuffer.append(NEWLINE);
			CvWString szYield;
			szYield.Format(L"%d.%02d", iYield / 100, iYield % 100);
			szBuffer.append(gDLL->getText("TXT_KEY_TRADE_ROUTE_TOTAL_FRACTIONAL", szYield.GetCString()));
			// lfgr, BUG end
		}
	}
}

void CvGameTextMgr::setEspionageCostHelp(CvWStringBuffer &szBuffer, EspionageMissionTypes eMission, PlayerTypes eTargetPlayer, const CvPlot* pPlot, int iExtraData, const CvUnit* pSpyUnit)
{
	CvPlayer& kPlayer = GET_PLAYER(GC.getGameINLINE().getActivePlayer());
	CvEspionageMissionInfo& kMission = GC.getEspionageMissionInfo(eMission);

	//szBuffer.assign(kMission.getDescription());

	int iMissionCost = kPlayer.getEspionageMissionBaseCost(eMission, eTargetPlayer, pPlot, iExtraData, pSpyUnit);

	if (kMission.isDestroyImprovement())
	{
		if (NULL != pPlot && NO_IMPROVEMENT != pPlot->getImprovementType())
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_DESTROY_IMPROVEMENT", GC.getImprovementInfo(pPlot->getImprovementType()).getTextKeyWide()));
			szBuffer.append(NEWLINE);
		}
	}

	if (kMission.getDestroyBuildingCostFactor() > 0)
	{
		BuildingTypes eTargetBuilding = (BuildingTypes)iExtraData;

		if (NULL != pPlot)
		{
			CvCity* pCity = pPlot->getPlotCity();

			if (NULL != pCity)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_DESTROY_IMPROVEMENT", GC.getBuildingInfo(eTargetBuilding).getTextKeyWide()));
				szBuffer.append(NEWLINE);
			}
		}
	}

	if (kMission.getDestroyProjectCostFactor() > 0)
	{
		ProjectTypes eTargetProject = (ProjectTypes)iExtraData;

		if (NULL != pPlot)
		{
			CvCity* pCity = pPlot->getPlotCity();

			if (NULL != pCity)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_DESTROY_IMPROVEMENT", GC.getProjectInfo(eTargetProject).getTextKeyWide()));
				szBuffer.append(NEWLINE);
			}
		}
	}

	if (kMission.getDestroyProductionCostFactor() > 0)
	{
		if (NULL != pPlot)
		{
			CvCity* pCity = pPlot->getPlotCity();

			if (NULL != pCity)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_DESTROY_PRODUCTION", pCity->getProduction()));
				szBuffer.append(NEWLINE);
			}
		}
	}

	if (kMission.getDestroyUnitCostFactor() > 0)
	{
		if (NO_PLAYER != eTargetPlayer)
		{
			int iTargetUnitID = iExtraData;

			CvUnit* pUnit = GET_PLAYER(eTargetPlayer).getUnit(iTargetUnitID);

			if (NULL != pUnit)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_DESTROY_UNIT", pUnit->getNameKey()));
				szBuffer.append(NEWLINE);
			}
		}
	}

	if (kMission.getBuyUnitCostFactor() > 0)
	{
		if (NO_PLAYER != eTargetPlayer)
		{
			int iTargetUnitID = iExtraData;

			CvUnit* pUnit = GET_PLAYER(eTargetPlayer).getUnit(iTargetUnitID);

			if (NULL != pUnit)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_BRIBE", pUnit->getNameKey()));
				szBuffer.append(NEWLINE);
			}
		}
	}

	if (kMission.getBuyCityCostFactor() > 0)
	{
		if (NULL != pPlot)
		{
			CvCity* pCity = pPlot->getPlotCity();

			if (NULL != pCity)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_BRIBE", pCity->getNameKey()));
				szBuffer.append(NEWLINE);
			}
		}
	}

	if (kMission.getCityInsertCultureCostFactor() > 0)
	{
		if (NULL != pPlot)
		{
			CvCity* pCity = pPlot->getPlotCity();

			if (NULL != pCity && pPlot->getCulture(GC.getGameINLINE().getActivePlayer()) > 0)
			{
				int iCultureAmount = kMission.getCityInsertCultureAmountFactor() *  pCity->countTotalCultureTimes100();
				iCultureAmount /= 10000;
				iCultureAmount = std::max(1, iCultureAmount);

				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_INSERT_CULTURE", pCity->getNameKey(), iCultureAmount, kMission.getCityInsertCultureAmountFactor()));
				szBuffer.append(NEWLINE);
			}
		}
	}

	if (kMission.getCityPoisonWaterCounter() > 0)
	{
		if (NULL != pPlot)
		{
			CvCity* pCity = pPlot->getPlotCity();

			if (NULL != pCity)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_POISON", kMission.getCityPoisonWaterCounter(), gDLL->getSymbolID(UNHEALTHY_CHAR), pCity->getNameKey(), kMission.getCityPoisonWaterCounter()));
				szBuffer.append(NEWLINE);
			}
		}
	}

	if (kMission.getCityUnhappinessCounter() > 0)
	{
		if (NULL != pPlot)
		{
			CvCity* pCity = pPlot->getPlotCity();

			if (NULL != pCity)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_POISON", kMission.getCityUnhappinessCounter(), gDLL->getSymbolID(UNHAPPY_CHAR), pCity->getNameKey(), kMission.getCityUnhappinessCounter()));
				szBuffer.append(NEWLINE);
			}
		}
	}

	if (kMission.getCityRevoltCounter() > 0)
	{
		if (NULL != pPlot)
		{
			CvCity* pCity = pPlot->getPlotCity();

			if (NULL != pCity)
			{
				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_REVOLT", pCity->getNameKey(), kMission.getCityRevoltCounter()));
				szBuffer.append(NEWLINE);
			}
		}
	}

	if (kMission.getStealTreasuryTypes() > 0)
	{
		if (NO_PLAYER != eTargetPlayer)
		{
			int iNumTotalGold = (GET_PLAYER(eTargetPlayer).getGold() * kMission.getStealTreasuryTypes()) / 100;

			if (NULL != pPlot)
			{
				CvCity* pCity = pPlot->getPlotCity();

				if (NULL != pCity)
				{
					iNumTotalGold *= pCity->getPopulation();
					iNumTotalGold /= std::max(1, GET_PLAYER(eTargetPlayer).getTotalPopulation());
				}
			}

			szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_STEAL_TREASURY", iNumTotalGold, GET_PLAYER(eTargetPlayer).getCivilizationAdjectiveKey()));
			szBuffer.append(NEWLINE);
		}
	}

	if (kMission.getBuyTechCostFactor() > 0)
	{
		szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_STEAL_TECH", GC.getTechInfo((TechTypes)iExtraData).getTextKeyWide()));
		szBuffer.append(NEWLINE);
	}

	if (kMission.getSwitchCivicCostFactor() > 0)
	{
		if (NO_PLAYER != eTargetPlayer)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_SWITCH_CIVIC", GET_PLAYER(eTargetPlayer).getNameKey(), GC.getCivicInfo((CivicTypes)iExtraData).getTextKeyWide()));
			szBuffer.append(NEWLINE);
		}
	}

	if (kMission.getSwitchReligionCostFactor() > 0)
	{
		if (NO_PLAYER != eTargetPlayer)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_SWITCH_CIVIC", GET_PLAYER(eTargetPlayer).getNameKey(), GC.getReligionInfo((ReligionTypes)iExtraData).getTextKeyWide()));
			szBuffer.append(NEWLINE);
		}
	}

	if (kMission.getPlayerAnarchyCounter() > 0)
	{
		if (NO_PLAYER != eTargetPlayer)
		{
			int iTurns = (kMission.getPlayerAnarchyCounter() * GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getAnarchyPercent()) / 100;
			szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_ANARCHY", GET_PLAYER(eTargetPlayer).getNameKey(), iTurns));
			szBuffer.append(NEWLINE);
		}
	}

	if (kMission.getCounterespionageNumTurns() > 0 && kMission.getCounterespionageMod() > 0)
	{
		if (NO_PLAYER != eTargetPlayer)
		{
			int iTurns = (kMission.getCounterespionageNumTurns() * GC.getGameSpeedInfo(GC.getGameINLINE().getGameSpeedType()).getResearchPercent()) / 100;

			szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_HELP_COUNTERESPIONAGE", kMission.getCounterespionageMod(), GET_PLAYER(eTargetPlayer).getCivilizationAdjectiveKey(), iTurns));
			szBuffer.append(NEWLINE);
		}
	}

	szBuffer.append(NEWLINE);
	szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_BASE_COST", iMissionCost));

	if (kPlayer.getEspionageMissionCost(eMission, eTargetPlayer, pPlot, iExtraData, pSpyUnit) > 0)
	{
		int iModifier = 100;
		int iTempModifier = 0;
		CvCity* pCity = NULL;
		if (NULL != pPlot)
		{
			pCity = pPlot->getPlotCity();
		}

		if (pCity != NULL && GC.getEspionageMissionInfo(eMission).isTargetsCity())
		{
			// City Population
			iTempModifier = (GC.getDefineINT("ESPIONAGE_CITY_POP_EACH_MOD") * (pCity->getPopulation() - 1));
			if (0 != iTempModifier)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_POPULATION_MOD", iTempModifier));
				iModifier *= 100 + iTempModifier;
				iModifier /= 100;
			}

			// Trade Route
			if (pCity->isTradeRoute(kPlayer.getID()))
			{
				iTempModifier = GC.getDefineINT("ESPIONAGE_CITY_TRADE_ROUTE_MOD");
				if (0 != iTempModifier)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_TRADE_ROUTE_MOD", iTempModifier));
					iModifier *= 100 + iTempModifier;
					iModifier /= 100;
				}
			}

			ReligionTypes eReligion = kPlayer.getStateReligion();
			if (NO_RELIGION != eReligion)
			{
				iTempModifier = 0;

				if (pCity->isHasReligion(eReligion))
				{
					if (GET_PLAYER(eTargetPlayer).getStateReligion() != eReligion)
					{
						iTempModifier += GC.getDefineINT("ESPIONAGE_CITY_RELIGION_STATE_MOD");
					}

					if (kPlayer.hasHolyCity(eReligion))
					{
						iTempModifier += GC.getDefineINT("ESPIONAGE_CITY_HOLY_CITY_MOD");
					}
				}

				if (0 != iTempModifier)
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_RELIGION_MOD", iTempModifier));
					iModifier *= 100 + iTempModifier;
					iModifier /= 100;
				}
			}

			// City's culture affects cost
			iTempModifier = - (pCity->getCultureTimes100(kPlayer.getID()) * GC.getDefineINT("ESPIONAGE_CULTURE_MULTIPLIER_MOD")) / std::max(1, pCity->getCultureTimes100(eTargetPlayer) + pCity->getCultureTimes100(kPlayer.getID()));
			if (0 != iTempModifier)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_CULTURE_MOD", iTempModifier));
				iModifier *= 100 + iTempModifier;
				iModifier /= 100;
			}

			iTempModifier = pCity->getEspionageDefenseModifier();
			if (0 != iTempModifier)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_DEFENSE_MOD", iTempModifier));
				iModifier *= 100 + iTempModifier;
				iModifier /= 100;
			}
		}

		// Distance mod
		if (pPlot != NULL)
		{
			int iDistance = GC.getMap().maxPlotDistance();

			CvCity* pOurCapital = kPlayer.getCapitalCity();
			if (NULL != pOurCapital)
			{
				if (kMission.isSelectPlot() || kMission.isTargetsCity())
				{
					iDistance = plotDistance(pOurCapital->getX_INLINE(), pOurCapital->getY_INLINE(), pPlot->getX_INLINE(), pPlot->getY_INLINE());
				}
				else
				{
					CvCity* pTheirCapital = GET_PLAYER(eTargetPlayer).getCapitalCity();
					if (NULL != pTheirCapital)
					{
						iDistance = plotDistance(pOurCapital->getX_INLINE(), pOurCapital->getY_INLINE(), pTheirCapital->getX_INLINE(), pTheirCapital->getY_INLINE());
					}
				}
			}

			iTempModifier = (iDistance + GC.getMapINLINE().maxPlotDistance()) * GC.getDefineINT("ESPIONAGE_DISTANCE_MULTIPLIER_MOD") / GC.getMapINLINE().maxPlotDistance() - 100;
			if (0 != iTempModifier)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_DISTANCE_MOD", iTempModifier));
				iModifier *= 100 + iTempModifier;
				iModifier /= 100;
			}
		}

		// Spy presence mission cost alteration
		if (NULL != pSpyUnit)
		{
			iTempModifier = -(pSpyUnit->getFortifyTurns() * GC.getDefineINT("ESPIONAGE_EACH_TURN_UNIT_COST_DECREASE"));
			if (0 != iTempModifier)
			{
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_SPY_STATIONARY_MOD", iTempModifier));
				iModifier *= 100 + iTempModifier;
				iModifier /= 100;
			}
		}

		// My points VS. Your points to mod cost
		iTempModifier = ::getEspionageModifier(kPlayer.getTeam(), GET_PLAYER(eTargetPlayer).getTeam()) - 100;
		if (0 != iTempModifier)
		{
			szBuffer.append(SEPARATOR);
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_EP_RATIO_MOD", iTempModifier));
			iModifier *= 100 + iTempModifier;
			iModifier /= 100;
		}

		// Counterespionage Mission Mod
		CvTeam& kTargetTeam = GET_TEAM(GET_PLAYER(eTargetPlayer).getTeam());
		if (kTargetTeam.getCounterespionageModAgainstTeam(kPlayer.getTeam()) > 0)
		{
			iTempModifier = kTargetTeam.getCounterespionageModAgainstTeam(kPlayer.getTeam()) - 100;
			if (0 != iTempModifier)
			{
				szBuffer.append(SEPARATOR);
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_COUNTERESPIONAGE_MOD", iTempModifier));
				iModifier *= 100 + iTempModifier;
				iModifier /= 100;
			}
		}
/************************************************************************************************/
/* Afforess	                  Start		 07/29/10                                               */
/* Advanced Diplomacy                                                                           */
/************************************************************************************************/
		if (pCity != NULL)
		{
			if (pCity == GET_PLAYER(pCity->getOwnerINLINE()).getCapitalCity() && kTargetTeam.isHasEmbassy(kPlayer.getTeam()))
			{
				szBuffer.append(SEPARATOR);
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_EMBASSY_MOD", -GC.getDefineINT("EMBASSY_ESPIONAGE_MISSION_COST_MODIFIER")));

				iModifier *= 100 - GC.getDefineINT("EMBASSY_ESPIONAGE_MISSION_COST_MODIFIER");
				iModifier /= 100;
			}
			if (kTargetTeam.isFreeTradeAgreement(kPlayer.getTeam()))
			{
				szBuffer.append(SEPARATOR);
				szBuffer.append(NEWLINE);
				szBuffer.append(gDLL->getText("TXT_KEY_FREE_TRADE_AGREEMENT_MOD", -GC.getDefineINT("FREE_TRADE_AGREEMENT_ESPIONAGE_MISSION_COST_MODIFIER")));

				iModifier *= 100 - GC.getDefineINT("FREE_TRADE_AGREEMENT_ESPIONAGE_MISSION_COST_MODIFIER");
				iModifier /= 100;
			}
		}
/************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/************************************************************************************************/
		FAssert(iModifier == kPlayer.getEspionageMissionCostModifier(eMission, eTargetPlayer, pPlot, iExtraData, pSpyUnit));

		iMissionCost *= iModifier;
		iMissionCost /= 100;

		FAssert(iMissionCost == kPlayer.getEspionageMissionCost(eMission, eTargetPlayer, pPlot, iExtraData, pSpyUnit));

		szBuffer.append(SEPARATOR);

		szBuffer.append(NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_COST_TOTAL", iMissionCost));


		if (NULL != pSpyUnit)
		{
			int iInterceptChance = (pSpyUnit->getSpyInterceptPercent(GET_PLAYER(eTargetPlayer).getTeam()) * (100 + kMission.getDifficultyMod())) / 100;

			szBuffer.append(NEWLINE);
			szBuffer.append(NEWLINE);
			szBuffer.append(gDLL->getText("TXT_KEY_ESPIONAGE_CHANCE_OF_SUCCESS", std::min(100, std::max(0, 100 - iInterceptChance))));
		}
	}
}

void CvGameTextMgr::getTradeScreenTitleIcon(CvString& szButton, CvWidgetDataStruct& widgetData, PlayerTypes ePlayer)
{
	szButton.clear();

	ReligionTypes eReligion = GET_PLAYER(ePlayer).getStateReligion();
	if (eReligion != NO_RELIGION)
	{
		szButton = GC.getReligionInfo(eReligion).getButton();
		widgetData.m_eWidgetType = WIDGET_HELP_RELIGION;
		widgetData.m_iData1 = eReligion;
		widgetData.m_iData2 = -1;
		widgetData.m_bOption = false;
	}
}

void CvGameTextMgr::getTradeScreenIcons(std::vector< std::pair<CvString, CvWidgetDataStruct> >& aIconInfos, PlayerTypes ePlayer)
{
	aIconInfos.clear();
	for (int i = 0; i < GC.getNumCivicOptionInfos(); i++)
	{
		CivicTypes eCivic = GET_PLAYER(ePlayer).getCivics((CivicOptionTypes)i);
		CvWidgetDataStruct widgetData;
		widgetData.m_eWidgetType = WIDGET_PEDIA_JUMP_TO_CIVIC;
		widgetData.m_iData1 = eCivic;
		widgetData.m_iData2 = -1;
		widgetData.m_bOption = false;
		aIconInfos.push_back(std::make_pair(GC.getCivicInfo(eCivic).getButton(), widgetData));
	}

}

void CvGameTextMgr::getTradeScreenHeader(CvWString& szHeader, PlayerTypes ePlayer, PlayerTypes eOtherPlayer, bool bAttitude)
{
	CvPlayer& kPlayer = GET_PLAYER(ePlayer);
	szHeader.Format(L"%s - %s", CvWString(kPlayer.getName()).GetCString(), CvWString(kPlayer.getCivilizationDescription()).GetCString());
	if (bAttitude)
	{
		szHeader += CvWString::format(L" (%s)", GC.getAttitudeInfo(kPlayer.AI_getAttitude(eOtherPlayer)).getDescription());
	}
}

// BUG - Trade Hover - start
void CvGameTextMgr::buildDomesticTradeString(CvWStringBuffer& szBuffer, PlayerTypes ePlayer)
{
	buildTradeString(szBuffer, ePlayer, NO_PLAYER, true, false, false);
}

void CvGameTextMgr::buildForeignTradeString(CvWStringBuffer& szBuffer, PlayerTypes ePlayer)
{
	buildTradeString(szBuffer, ePlayer, NO_PLAYER, false, true, false);
}

void CvGameTextMgr::buildTradeString(CvWStringBuffer& szBuffer, PlayerTypes ePlayer, PlayerTypes eWithPlayer, bool bDomestic, bool bForeign, bool bHeading)
{
	if (NO_PLAYER == ePlayer)
	{
		return;
	}

	CvPlayer& player = GET_PLAYER(ePlayer);
	if (bHeading)
	{
		if (ePlayer == eWithPlayer)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_BUG_DOMESTIC_TRADE_HEADING"));
		}
		else if (NO_PLAYER != eWithPlayer)
		{
			if (player.canHaveTradeRoutesWith(eWithPlayer))
			{
				szBuffer.append(gDLL->getText("TXT_KEY_BUG_FOREIGN_TRADE_HEADING", GET_PLAYER(eWithPlayer).getNameKey(), GET_PLAYER(eWithPlayer).getCivilizationShortDescription()));
			}
			else
			{
				szBuffer.append(gDLL->getText("TXT_KEY_BUG_CANNOT_TRADE_HEADING", GET_PLAYER(eWithPlayer).getNameKey(), GET_PLAYER(eWithPlayer).getCivilizationShortDescription()));
			}
		}
		else
		{
			szBuffer.append(gDLL->getText("TXT_KEY_BUG_TRADE_HEADING"));
		}
		szBuffer.append(NEWLINE);
	}

	if (NO_PLAYER != eWithPlayer)
	{
		bDomestic = ePlayer == eWithPlayer;
		bForeign = ePlayer != eWithPlayer;

		if (bForeign && !player.canHaveTradeRoutesWith(eWithPlayer))
		{
			CvPlayer& withPlayer = GET_PLAYER(eWithPlayer);
			bool bCanTrade = true;
			if (!GET_PLAYER(eWithPlayer).isAlive())
			{
				szBuffer.append(gDLL->getText("TXT_KEY_BUG_CANNOT_TRADE_DEAD"));
				return;
			}
			if (!player.canTradeNetworkWith(eWithPlayer))
			{
				szBuffer.append(gDLL->getText("TXT_KEY_BUG_CANNOT_TRADE_NETWORK_NOT_CONNECTED"));
				bCanTrade = false;
			}
			if (!GET_TEAM(player.getTeam()).isFreeTrade(withPlayer.getTeam()))
			{
				szBuffer.append(gDLL->getText("TXT_KEY_BUG_CANNOT_TRADE_CLOSED_BORDERS"));
				bCanTrade = false;
			}
			if (player.isNoForeignTrade())
			{
				szBuffer.append(gDLL->getText("TXT_KEY_BUG_CANNOT_TRADE_FOREIGN_YOU"));
				bCanTrade = false;
			}
			if (withPlayer.isNoForeignTrade())
			{
				szBuffer.append(gDLL->getText("TXT_KEY_BUG_CANNOT_TRADE_FOREIGN_THEM"));
				bCanTrade = false;
			}

			if (!bCanTrade)
			{
				return;
			}
		}
	}

	int iDomesticYield = 0;
	int iDomesticRoutes = 0;
	int iForeignYield = 0;
	int iForeignRoutes = 0;

	player.calculateTradeTotals(YIELD_COMMERCE, iDomesticYield, iDomesticRoutes, iForeignYield, iForeignRoutes, eWithPlayer, false);

	int iTotalYield = 0;
	int iTotalRoutes = 0;
	if (bDomestic)
	{
		iTotalYield += iDomesticYield;
		iTotalRoutes += iDomesticRoutes;
	}
	if (bForeign)
	{
		iTotalYield += iForeignYield;
		iTotalRoutes += iForeignRoutes;
	}

	CvWString szYield;
// BUG - Fractional Trade Routes - start
	szYield.Format(L"%d.%02d", iTotalYield / 100, iTotalYield % 100);
// BUG - Fractional Trade Routes - end
	szBuffer.append(gDLL->getText("TXT_KEY_BUG_TOTAL_TRADE_YIELD", szYield.GetCString()));
	szBuffer.append(gDLL->getText("TXT_KEY_BUG_TOTAL_TRADE_ROUTES", iTotalRoutes));

	if (iTotalRoutes > 0)
	{
// BUG - Fractional Trade Routes - start
		int iAverage = iTotalYield / iTotalRoutes;
// BUG - Fractional Trade Routes - end
		CvWString szAverage;
		szAverage.Format(L"%d.%02d", iAverage / 100, iAverage % 100);
		szBuffer.append(gDLL->getText("TXT_KEY_BUG_AVERAGE_TRADE_YIELD", szAverage.GetCString()));
	}
}
// BUG - Trade Hover - end

void CvGameTextMgr::getGlobeLayerName(GlobeLayerTypes eType, int iOption, CvWString& strName)
{
	switch (eType)
	{
	case GLOBE_LAYER_STRATEGY:
		switch(iOption)
		{
		case 0:
			strName = gDLL->getText("TXT_KEY_GLOBELAYER_STRATEGY_VIEW");
			break;
		case 1:
			strName = gDLL->getText("TXT_KEY_GLOBELAYER_STRATEGY_NEW_LINE");
			break;
		case 2:
			strName = gDLL->getText("TXT_KEY_GLOBELAYER_STRATEGY_NEW_SIGN");
			break;
		case 3:
			strName = gDLL->getText("TXT_KEY_GLOBELAYER_STRATEGY_DELETE");
			break;
		case 4:
			strName = gDLL->getText("TXT_KEY_GLOBELAYER_STRATEGY_DELETE_LINES");
			break;
		}
		break;
	case GLOBE_LAYER_UNIT:
		switch(iOption)
		{
		case SHOW_ALL_MILITARY:
			strName = gDLL->getText("TXT_KEY_GLOBELAYER_UNITS_ALLMILITARY");
			break;
		case SHOW_TEAM_MILITARY:
			strName = gDLL->getText("TXT_KEY_GLOBELAYER_UNITS_TEAMMILITARY");
			break;
		case SHOW_ENEMIES_IN_TERRITORY:
			strName = gDLL->getText("TXT_KEY_GLOBELAYER_UNITS_ENEMY_TERRITORY_MILITARY");
			break;
		case SHOW_ENEMIES:
			strName = gDLL->getText("TXT_KEY_GLOBELAYER_UNITS_ENEMYMILITARY");
			break;
		case SHOW_PLAYER_DOMESTICS:
			strName = gDLL->getText("TXT_KEY_GLOBELAYER_UNITS_DOMESTICS");
			break;
		}
		break;
	case GLOBE_LAYER_RESOURCE:
		switch(iOption)
		{
		case SHOW_ALL_RESOURCES:
			strName = gDLL->getText("TXT_KEY_GLOBELAYER_RESOURCES_EVERYTHING");
			break;
		case SHOW_STRATEGIC_RESOURCES:
			strName = gDLL->getText("TXT_KEY_GLOBELAYER_RESOURCES_GENERAL");
			break;
		case SHOW_HAPPY_RESOURCES:
			strName = gDLL->getText("TXT_KEY_GLOBELAYER_RESOURCES_LUXURIES");
			break;
		case SHOW_HEALTH_RESOURCES:
			strName = gDLL->getText("TXT_KEY_GLOBELAYER_RESOURCES_FOOD");
			break;
		}
		break;
	case GLOBE_LAYER_RELIGION:
		// Hide Council of Esus in the Religion globe layer START
		// strName = GC.getReligionInfo((ReligionTypes) iOption).getDescription();
		{
			int realNumber = 0;
			int optionNumber = 0;
			while (realNumber < GC.getNumReligionInfos())
			{
				if (GET_PLAYER(GC.getGameINLINE().getActivePlayer()).canSeeReligion((ReligionTypes) realNumber, NULL))
				{
					if (optionNumber == iOption) {
						break;
					}
					optionNumber++;
				}
				realNumber++;
			}
			strName = GC.getReligionInfo((ReligionTypes) realNumber).getDescription();
		}
		// Hide Council of Esus in the Religion globe layer END
		break;
	case GLOBE_LAYER_CULTURE:
	case GLOBE_LAYER_TRADE:
		// these have no sub-options
		strName.clear();
		break;
	}
}

void CvGameTextMgr::getPlotHelp(CvPlot* pMouseOverPlot, CvCity* pCity, CvPlot* pFlagPlot, bool bAlt, CvWStringBuffer& strHelp)
{
	if (gDLL->getInterfaceIFace()->isCityScreenUp())
	{
		if (pMouseOverPlot != NULL)
		{
			CvCity* pHeadSelectedCity = gDLL->getInterfaceIFace()->getHeadSelectedCity();
			if (pHeadSelectedCity != NULL)
			{
				if (pMouseOverPlot->getWorkingCity() == pHeadSelectedCity)
				{
					if (pMouseOverPlot->isRevealed(GC.getGameINLINE().getActiveTeam(), true))
					{
						setPlotHelp(strHelp, pMouseOverPlot);
					}
				}
			}
		}
	}
	else
	{
		if (pCity != NULL)
		{
			setCityBarHelp(strHelp, pCity);
		}
		else if (pFlagPlot != NULL)
		{
			setPlotListHelp(strHelp, pFlagPlot, false, true);
		}

		if (strHelp.isEmpty())
		{
			if (pMouseOverPlot != NULL)
			{
				if ((pMouseOverPlot == gDLL->getInterfaceIFace()->getGotoPlot()) || bAlt)
				{
					if (pMouseOverPlot->isActiveVisible(true))
					{
						setCombatPlotHelp(strHelp, pMouseOverPlot);
					}
				}
			}
		}

		if (strHelp.isEmpty())
		{
			if (pMouseOverPlot != NULL)
			{
				if (pMouseOverPlot->isRevealed(GC.getGameINLINE().getActiveTeam(), true))
				{
					if (pMouseOverPlot->isActiveVisible(true))
					{
						setPlotListHelp(strHelp, pMouseOverPlot, true, false);

						if (!strHelp.isEmpty())
						{
							strHelp.append(L"\n");
						}
					}

					setPlotHelp(strHelp, pMouseOverPlot);
				}
			}
		}

		InterfaceModeTypes eInterfaceMode = gDLL->getInterfaceIFace()->getInterfaceMode();
		if (eInterfaceMode != INTERFACEMODE_SELECTION)
		{
			CvWString szTempBuffer;
			szTempBuffer.Format(SETCOLR L"%s" ENDCOLR NEWLINE, TEXT_COLOR("COLOR_HIGHLIGHT_TEXT"), GC.getInterfaceModeInfo(eInterfaceMode).getDescription());

			switch (eInterfaceMode)
			{
			case INTERFACEMODE_REBASE:
				getRebasePlotHelp(pMouseOverPlot, szTempBuffer);
				break;

			case INTERFACEMODE_NUKE:
				getNukePlotHelp(pMouseOverPlot, szTempBuffer);
				break;

			default:
				break;
			}

			szTempBuffer += strHelp.getCString();
			strHelp.assign(szTempBuffer);
		}
	}
}

void CvGameTextMgr::getRebasePlotHelp(CvPlot* pPlot, CvWString& strHelp)
{
	if (NULL != pPlot)
	{
		CvUnit* pHeadSelectedUnit = gDLL->getInterfaceIFace()->getHeadSelectedUnit();
		if (NULL != pHeadSelectedUnit)
		{
			if (pPlot->isFriendlyCity(*pHeadSelectedUnit, true))
			{
				CvCity* pCity = pPlot->getPlotCity();
				if (NULL != pCity)
				{
					int iNumUnits = pCity->plot()->countNumAirUnits(GC.getGameINLINE().getActiveTeam());
					bool bFull = (iNumUnits >= pCity->getAirUnitCapacity(GC.getGameINLINE().getActiveTeam()));

					if (bFull)
					{
						strHelp += CvWString::format(SETCOLR, TEXT_COLOR("COLOR_WARNING_TEXT"));
					}

					strHelp +=  NEWLINE + gDLL->getText("TXT_KEY_CITY_BAR_AIR_UNIT_CAPACITY", iNumUnits, pCity->getAirUnitCapacity(GC.getGameINLINE().getActiveTeam()));

					if (bFull)
					{
						strHelp += ENDCOLR;
					}

					strHelp += NEWLINE;
				}
			}
		}
	}
}

void CvGameTextMgr::getNukePlotHelp(CvPlot* pPlot, CvWString& strHelp)
{
	if (NULL != pPlot)
	{
		CvUnit* pHeadSelectedUnit = gDLL->getInterfaceIFace()->getHeadSelectedUnit();

		if (NULL != pHeadSelectedUnit)
		{
			for (int iI = 0; iI < MAX_TEAMS; iI++)
			{
				if (pHeadSelectedUnit->isNukeVictim(pPlot, ((TeamTypes)iI)))
				{
					if (!pHeadSelectedUnit->isEnemy((TeamTypes)iI))
					{
						strHelp +=  NEWLINE + gDLL->getText("TXT_KEY_CANT_NUKE_FRIENDS");
						break;
					}
				}
			}
		}
	}
}

void CvGameTextMgr::getInterfaceCenterText(CvWString& strText)
{
	strText.clear();
	if (!gDLL->getInterfaceIFace()->isCityScreenUp())
	{
		if (GC.getGameINLINE().getWinner() != NO_TEAM)
		{
			strText = gDLL->getText("TXT_KEY_MISC_WINS_VICTORY", GET_TEAM(GC.getGameINLINE().getWinner()).getName().GetCString(), GC.getVictoryInfo(GC.getGameINLINE().getVictory()).getTextKeyWide());
		}
		else if (!(GET_PLAYER(GC.getGameINLINE().getActivePlayer()).isAlive()))
		{
			strText = gDLL->getText("TXT_KEY_MISC_DEFEAT");
		}
	}
}

void CvGameTextMgr::getTurnTimerText(CvWString& strText)
{
	strText.clear();
	if (gDLL->getInterfaceIFace()->getShowInterface() == INTERFACE_SHOW || gDLL->getInterfaceIFace()->getShowInterface() == INTERFACE_ADVANCED_START)
	{
		if (GC.getGameINLINE().isMPOption(MPOPTION_TURN_TIMER))
		{
			// Get number of turn slices remaining until end-of-turn
			int iTurnSlicesRemaining = GC.getGameINLINE().getTurnSlicesRemaining();

			if (iTurnSlicesRemaining > 0)
			{
				// Get number of seconds remaining
				int iTurnSecondsRemaining = ((int)floorf((float)(iTurnSlicesRemaining-1) * ((float)gDLL->getMillisecsPerTurn()/1000.0f)) + 1);
				int iTurnMinutesRemaining = (int)(iTurnSecondsRemaining/60);
				iTurnSecondsRemaining = (iTurnSecondsRemaining%60);
				int iTurnHoursRemaining = (int)(iTurnMinutesRemaining/60);
				iTurnMinutesRemaining = (iTurnMinutesRemaining%60);

				// Display time remaining
				CvWString szTempBuffer;
				szTempBuffer.Format(L"%d:%02d:%02d", iTurnHoursRemaining, iTurnMinutesRemaining, iTurnSecondsRemaining);
				strText += szTempBuffer;
			}
			else
			{
				// Flash zeroes
				if (iTurnSlicesRemaining % 2 == 0)
				{
					// Display 0
					strText+=L"0:00";
				}
			}
		}

		if (GC.getGameINLINE().getGameState() == GAMESTATE_ON)
		{
			int iMinVictoryTurns = MAX_INT;
			for (int i = 0; i < GC.getNumVictoryInfos(); ++i)
			{
				TeamTypes eActiveTeam = GC.getGameINLINE().getActiveTeam();
				if (NO_TEAM != eActiveTeam)
				{
					int iCountdown = GET_TEAM(eActiveTeam).getVictoryCountdown((VictoryTypes)i);
					if (iCountdown > 0 && iCountdown < iMinVictoryTurns)
					{
						iMinVictoryTurns = iCountdown;
					}
				}
			}

			if (GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_START) && !GC.getGameINLINE().isOption(GAMEOPTION_ALWAYS_WAR) && GC.getGameINLINE().getElapsedGameTurns() <= GC.getDefineINT("PEACE_TREATY_LENGTH"))
			{
				if (!strText.empty())
				{
					strText += L" -- ";
				}

				strText += gDLL->getText("TXT_KEY_MISC_ADVANCED_START_PEACE_REMAINING", GC.getDefineINT("PEACE_TREATY_LENGTH") - GC.getGameINLINE().getElapsedGameTurns());
			}
			else if (iMinVictoryTurns < MAX_INT)
			{
				if (!strText.empty())
				{
					strText += L" -- ";
				}

				strText += gDLL->getText("TXT_KEY_MISC_TURNS_LEFT_TO_VICTORY", iMinVictoryTurns);
			}
			else if (GC.getGameINLINE().getMaxTurns() > 0)
			{
				if ((GC.getGameINLINE().getElapsedGameTurns() >= (GC.getGameINLINE().getMaxTurns() - 100)) && (GC.getGameINLINE().getElapsedGameTurns() < GC.getGameINLINE().getMaxTurns()))
				{
					if (!strText.empty())
					{
						strText += L" -- ";
					}

					strText += gDLL->getText("TXT_KEY_MISC_TURNS_LEFT", (GC.getGameINLINE().getMaxTurns() - GC.getGameINLINE().getElapsedGameTurns()));
				}
			}
		}
	}
}


void CvGameTextMgr::getFontSymbols(std::vector< std::vector<wchar> >& aacSymbols, std::vector<int>& aiMaxNumRows)
{
	aacSymbols.push_back(std::vector<wchar>());
	aiMaxNumRows.push_back(1);
	for (int iI = 0; iI < NUM_YIELD_TYPES; iI++)
	{
		aacSymbols[aacSymbols.size() - 1].push_back((wchar) GC.getYieldInfo((YieldTypes) iI).getChar());
	}

	aacSymbols.push_back(std::vector<wchar>());
	aiMaxNumRows.push_back(2);
	for (int iI = 0; iI < NUM_COMMERCE_TYPES; iI++)
	{
		aacSymbols[aacSymbols.size() - 1].push_back((wchar) GC.getCommerceInfo((CommerceTypes) iI).getChar());
	}

	aacSymbols.push_back(std::vector<wchar>());
	aiMaxNumRows.push_back(2);
	for (int iI = 0; iI < GC.getNumReligionInfos(); iI++)
	{
		aacSymbols[aacSymbols.size() - 1].push_back((wchar) GC.getReligionInfo((ReligionTypes) iI).getChar());
		aacSymbols[aacSymbols.size() - 1].push_back((wchar) GC.getReligionInfo((ReligionTypes) iI).getHolyCityChar());
	}
	for (int iI = 0; iI < GC.getNumCorporationInfos(); iI++)
	{
		aacSymbols[aacSymbols.size() - 1].push_back((wchar) GC.getCorporationInfo((CorporationTypes) iI).getChar());
		aacSymbols[aacSymbols.size() - 1].push_back((wchar) GC.getCorporationInfo((CorporationTypes) iI).getHeadquarterChar());
	}

	aacSymbols.push_back(std::vector<wchar>());
	aiMaxNumRows.push_back(3);
	for (int iI = 0; iI < GC.getNumBonusInfos(); iI++)
	{
		aacSymbols[aacSymbols.size() - 1].push_back((wchar) GC.getBonusInfo((BonusTypes) iI).getChar());
	}

	aacSymbols.push_back(std::vector<wchar>());
	aiMaxNumRows.push_back(3);
	for (int iI = 0; iI < MAX_NUM_SYMBOLS; iI++)
	{
		aacSymbols[aacSymbols.size() - 1].push_back((wchar) gDLL->getSymbolID(iI));
	}
}

void CvGameTextMgr::assignFontIds(int iFirstSymbolCode, int iPadAmount)
{
	int iCurSymbolID = iFirstSymbolCode;

	// set yield symbols
	for (int i = 0; i < NUM_YIELD_TYPES; i++)
	{
		GC.getYieldInfo((YieldTypes) i).setChar(iCurSymbolID);
		++iCurSymbolID;
	}

	do
	{
		++iCurSymbolID;
	} while (iCurSymbolID % iPadAmount != 0);

	// set commerce symbols
	for (i=0;i<GC.getNUM_COMMERCE_TYPES();i++)
	{
		GC.getCommerceInfo((CommerceTypes) i).setChar(iCurSymbolID);
		++iCurSymbolID;
	}

	do
	{
		++iCurSymbolID;
	} while (iCurSymbolID % iPadAmount != 0);

	if (NUM_COMMERCE_TYPES < iPadAmount)
	{
		do
		{
			++iCurSymbolID;
		} while (iCurSymbolID % iPadAmount != 0);
	}

	for (int i = 0; i < GC.getNumReligionInfos(); i++)
	{
		GC.getReligionInfo((ReligionTypes) i).setChar(iCurSymbolID);
		++iCurSymbolID;
		GC.getReligionInfo((ReligionTypes) i).setHolyCityChar(iCurSymbolID);
		++iCurSymbolID;
	}
	for (i = 0; i < GC.getNumCorporationInfos(); i++)
	{
		GC.getCorporationInfo((CorporationTypes) i).setChar(iCurSymbolID);
		++iCurSymbolID;
		GC.getCorporationInfo((CorporationTypes) i).setHeadquarterChar(iCurSymbolID);
		++iCurSymbolID;
	}

	do
	{
		++iCurSymbolID;
	} while (iCurSymbolID % iPadAmount != 0);

	if (2 * (GC.getNumReligionInfos() + GC.getNumCorporationInfos()) < iPadAmount)
	{
		do
		{
			++iCurSymbolID;
		} while (iCurSymbolID % iPadAmount != 0);
	}

	// set bonus symbols
	int bonusBaseID = iCurSymbolID;
/*************************************************************************************************/
/* UNOFFICIAL_PATCH                       06/02/10                           LunarMongoose       */
/*                                                                                               */
/* Bugfix                                                                                        */
/*************************************************************************************************/
/* original bts code
			++iCurSymbolID;
*/
			// Mongoose GameFontFix
			// removes an erroneous extra increment command that was breaking GameFont.tga files when using exactly 49 or 74 resource types in a mod
/*************************************************************************************************/
/* UNOFFICIAL_PATCH                         END                                                  */
/*************************************************************************************************/
	for (int i = 0; i < GC.getNumBonusInfos(); i++)
	{
		int bonusID = bonusBaseID + GC.getBonusInfo((BonusTypes) i).getArtInfo()->getFontButtonIndex();
		GC.getBonusInfo((BonusTypes) i).setChar(bonusID);
		++iCurSymbolID;
	}

	do
	{
		++iCurSymbolID;
	} while (iCurSymbolID % iPadAmount != 0);

	if(GC.getNumBonusInfos() < iPadAmount)
	{
		do
		{
			++iCurSymbolID;
		} while (iCurSymbolID % iPadAmount != 0);
	}

	if(GC.getNumBonusInfos() < 2 * iPadAmount)
	{
		do
		{
			++iCurSymbolID;
		} while (iCurSymbolID % iPadAmount != 0);
	}

	// set extra symbols
	for (int i=0; i < MAX_NUM_SYMBOLS; i++)
	{
		gDLL->setSymbolID(i, iCurSymbolID);
		++iCurSymbolID;
	}
}

void CvGameTextMgr::getCityDataForAS(std::vector<CvWBData>& mapCityList, std::vector<CvWBData>& mapBuildingList, std::vector<CvWBData>& mapAutomateList)
{
	CvPlayer& kActivePlayer = GET_PLAYER(GC.getGameINLINE().getActivePlayer());

	CvWString szHelp;
	int iCost = kActivePlayer.getAdvancedStartCityCost(true);
	if (iCost > 0)
	{
		szHelp = gDLL->getText("TXT_KEY_CITY");
		szHelp += gDLL->getText("TXT_KEY_AS_UNREMOVABLE");
		mapCityList.push_back(CvWBData(0, szHelp, ARTFILEMGR.getInterfaceArtInfo("INTERFACE_BUTTONS_CITYSELECTION")->getPath()));
	}

	iCost = kActivePlayer.getAdvancedStartPopCost(true);
	if (iCost > 0)
	{
		szHelp = gDLL->getText("TXT_KEY_WB_AS_POPULATION");
		mapCityList.push_back(CvWBData(1, szHelp, ARTFILEMGR.getInterfaceArtInfo("INTERFACE_ANGRYCITIZEN_TEXTURE")->getPath()));
	}

	iCost = kActivePlayer.getAdvancedStartCultureCost(true);
	if (iCost > 0)
	{
		szHelp = gDLL->getText("TXT_KEY_ADVISOR_CULTURE");
		szHelp += gDLL->getText("TXT_KEY_AS_UNREMOVABLE");
		mapCityList.push_back(CvWBData(2, szHelp, ARTFILEMGR.getInterfaceArtInfo("CULTURE_BUTTON")->getPath()));
	}

	CvWStringBuffer szBuffer;
	for(int i = 0; i < GC.getNumBuildingClassInfos(); i++)
	{
		BuildingTypes eBuilding = (BuildingTypes) GC.getCivilizationInfo(kActivePlayer.getCivilizationType()).getCivilizationBuildings(i);

		if (eBuilding != NO_BUILDING)
		{
			if (GC.getBuildingInfo(eBuilding).getFreeStartEra() == NO_ERA || GC.getGameINLINE().getStartEra() < GC.getBuildingInfo(eBuilding).getFreeStartEra())
			{
				// Building cost -1 denotes unit which may not be purchased
				iCost = kActivePlayer.getAdvancedStartBuildingCost(eBuilding, true);
				if (iCost > 0)
				{
					szBuffer.clear();
					setBuildingHelp(szBuffer, eBuilding);
					mapBuildingList.push_back(CvWBData(eBuilding, szBuffer.getCString(), GC.getBuildingInfo(eBuilding).getButton()));
				}
			}
		}
	}

	szHelp = gDLL->getText("TXT_KEY_ACTION_AUTOMATE_BUILD");
	mapAutomateList.push_back(CvWBData(0, szHelp, ARTFILEMGR.getInterfaceArtInfo("INTERFACE_AUTOMATE")->getPath()));
}

void CvGameTextMgr::getUnitDataForAS(std::vector<CvWBData>& mapUnitList)
{
	CvPlayer& kActivePlayer = GET_PLAYER(GC.getGameINLINE().getActivePlayer());

	CvWStringBuffer szBuffer;
	for(int i = 0; i < GC.getNumUnitClassInfos(); i++)
	{
		UnitTypes eUnit = (UnitTypes) GC.getCivilizationInfo(kActivePlayer.getCivilizationType()).getCivilizationUnits(i);
		if (eUnit != NO_UNIT)
		{
			// Unit cost -1 denotes unit which may not be purchased
			int iCost = kActivePlayer.getAdvancedStartUnitCost(eUnit, true);
			if (iCost > 0)
			{
				szBuffer.clear();
				setUnitHelp(szBuffer, eUnit);

				int iMaxUnitsPerCity = GC.getDefineINT("ADVANCED_START_MAX_UNITS_PER_CITY");
				if (iMaxUnitsPerCity >= 0 && GC.getUnitInfo(eUnit).isMilitarySupport())
				{
					szBuffer.append(NEWLINE);
					szBuffer.append(gDLL->getText("TXT_KEY_WB_AS_MAX_UNITS_PER_CITY", iMaxUnitsPerCity));
				}
				mapUnitList.push_back(CvWBData(eUnit, szBuffer.getCString(), kActivePlayer.getUnitButton(eUnit)));
			}
		}
	}
}

void CvGameTextMgr::getImprovementDataForAS(std::vector<CvWBData>& mapImprovementList, std::vector<CvWBData>& mapRouteList)
{
	CvPlayer& kActivePlayer = GET_PLAYER(GC.getGameINLINE().getActivePlayer());

	for (int i = 0; i < GC.getNumRouteInfos(); i++)
	{
		RouteTypes eRoute = (RouteTypes) i;
		if (eRoute != NO_ROUTE)
		{
			// Route cost -1 denotes route which may not be purchased
			int iCost = kActivePlayer.getAdvancedStartRouteCost(eRoute, true);
			if (iCost > 0)
			{
				mapRouteList.push_back(CvWBData(eRoute, GC.getRouteInfo(eRoute).getDescription(), GC.getRouteInfo(eRoute).getButton()));
			}
		}
	}

	CvWStringBuffer szBuffer;
	for (int i = 0; i < GC.getNumImprovementInfos(); i++)
	{
		ImprovementTypes eImprovement = (ImprovementTypes) i;
		if (eImprovement != NO_IMPROVEMENT)
		{
			// Improvement cost -1 denotes Improvement which may not be purchased
			int iCost = kActivePlayer.getAdvancedStartImprovementCost(eImprovement, true);
			if (iCost > 0)
			{
				szBuffer.clear();
				setImprovementHelp(szBuffer, eImprovement);
				mapImprovementList.push_back(CvWBData(eImprovement, szBuffer.getCString(), GC.getImprovementInfo(eImprovement).getButton()));
			}
		}
	}
}

void CvGameTextMgr::getVisibilityDataForAS(std::vector<CvWBData>& mapVisibilityList)
{
	// Unit cost -1 denotes unit which may not be purchased
	int iCost = GET_PLAYER(GC.getGameINLINE().getActivePlayer()).getAdvancedStartVisibilityCost(true);
	if (iCost > 0)
	{
		CvWString szHelp = gDLL->getText("TXT_KEY_WB_AS_VISIBILITY");
		szHelp += gDLL->getText("TXT_KEY_AS_UNREMOVABLE", iCost);
		mapVisibilityList.push_back(CvWBData(0, szHelp, ARTFILEMGR.getInterfaceArtInfo("INTERFACE_TECH_LOS")->getPath()));
	}
}

void CvGameTextMgr::getTechDataForAS(std::vector<CvWBData>& mapTechList)
{
	mapTechList.push_back(CvWBData(0, gDLL->getText("TXT_KEY_WB_AS_TECH"), ARTFILEMGR.getInterfaceArtInfo("INTERFACE_BTN_TECH")->getPath()));
}

void CvGameTextMgr::getUnitDataForWB(std::vector<CvWBData>& mapUnitData)
{
	CvWStringBuffer szBuffer;
	for (int i = 0; i < GC.getNumUnitInfos(); i++)
	{
		szBuffer.clear();
		setUnitHelp(szBuffer, (UnitTypes)i);
		mapUnitData.push_back(CvWBData(i, szBuffer.getCString(), GC.getUnitInfo((UnitTypes)i).getButton()));
	}
}

void CvGameTextMgr::getBuildingDataForWB(bool bStickyButton, std::vector<CvWBData>& mapBuildingData)
{
	int iCount = 0;
	if (!bStickyButton)
	{
		mapBuildingData.push_back(CvWBData(iCount++, GC.getMissionInfo(MISSION_FOUND).getDescription(), GC.getMissionInfo(MISSION_FOUND).getButton()));
	}

	CvWStringBuffer szBuffer;
	for (int i=0; i < GC.getNumBuildingInfos(); i++)
	{
		szBuffer.clear();
		setBuildingHelp(szBuffer, (BuildingTypes)i);
		mapBuildingData.push_back(CvWBData(iCount++, szBuffer.getCString(), GC.getBuildingInfo((BuildingTypes)i).getButton()));
	}
}

void CvGameTextMgr::getTerrainDataForWB(std::vector<CvWBData>& mapTerrainData, std::vector<CvWBData>& mapFeatureData, std::vector<CvWBData>& mapPlotData, std::vector<CvWBData>& mapRouteData)
{
	CvWStringBuffer szBuffer;

	for (int i = 0; i < GC.getNumTerrainInfos(); i++)
	{
		if (!GC.getTerrainInfo((TerrainTypes)i).isGraphicalOnly())
		{
			szBuffer.clear();
			setTerrainHelp(szBuffer, (TerrainTypes)i);
			mapTerrainData.push_back(CvWBData(i, szBuffer.getCString(), GC.getTerrainInfo((TerrainTypes)i).getButton()));
		}
	}

	for (int i = 0; i < GC.getNumFeatureInfos(); i++)
	{
		for (int k = 0; k < GC.getFeatureInfo((FeatureTypes)i).getArtInfo()->getNumVarieties(); k++)
		{
			szBuffer.clear();
			setFeatureHelp(szBuffer, (FeatureTypes)i);
			mapFeatureData.push_back(CvWBData(i + GC.getNumFeatureInfos() * k, szBuffer.getCString(), GC.getFeatureInfo((FeatureTypes)i).getArtInfo()->getVariety(k).getVarietyButton()));
		}
	}

	mapPlotData.push_back(CvWBData(0, gDLL->getText("TXT_KEY_WB_PLOT_TYPE_MOUNTAIN"), ARTFILEMGR.getInterfaceArtInfo("WORLDBUILDER_PLOT_TYPE_MOUNTAIN")->getPath()));
	mapPlotData.push_back(CvWBData(1, gDLL->getText("TXT_KEY_WB_PLOT_TYPE_HILL"), ARTFILEMGR.getInterfaceArtInfo("WORLDBUILDER_PLOT_TYPE_HILL")->getPath()));
	mapPlotData.push_back(CvWBData(2, gDLL->getText("TXT_KEY_WB_PLOT_TYPE_PLAINS"), ARTFILEMGR.getInterfaceArtInfo("WORLDBUILDER_PLOT_TYPE_PLAINS")->getPath()));
	mapPlotData.push_back(CvWBData(3, gDLL->getText("TXT_KEY_WB_PLOT_TYPE_OCEAN"), ARTFILEMGR.getInterfaceArtInfo("WORLDBUILDER_PLOT_TYPE_OCEAN")->getPath()));

	for (int i = 0; i < GC.getNumRouteInfos(); i++)
	{
		mapRouteData.push_back(CvWBData(i, GC.getRouteInfo((RouteTypes)i).getDescription(), GC.getRouteInfo((RouteTypes)i).getButton()));
	}
	mapRouteData.push_back(CvWBData(GC.getNumRouteInfos(), gDLL->getText("TXT_KEY_WB_RIVER_PLACEMENT"), ARTFILEMGR.getInterfaceArtInfo("WORLDBUILDER_RIVER_PLACEMENT")->getPath()));
}

void CvGameTextMgr::getTerritoryDataForWB(std::vector<CvWBData>& mapTerritoryData)
{
	for (int i = 0; i <= MAX_CIV_PLAYERS; i++)
	{
		CvWString szName = gDLL->getText("TXT_KEY_MAIN_MENU_NONE");
		CvString szButton = GC.getCivilizationInfo(GET_PLAYER(BARBARIAN_PLAYER).getCivilizationType()).getButton();

		if (GET_PLAYER((PlayerTypes) i).isEverAlive())
		{
			szName = GET_PLAYER((PlayerTypes)i).getName();
			szButton = GC.getCivilizationInfo(GET_PLAYER((PlayerTypes)i).getCivilizationType()).getButton();
		}
		mapTerritoryData.push_back(CvWBData(i, szName, szButton));
	}
}


void CvGameTextMgr::getTechDataForWB(std::vector<CvWBData>& mapTechData)
{
	CvWStringBuffer szBuffer;
	for (int i=0; i < GC.getNumTechInfos(); i++)
	{
		szBuffer.clear();
		setTechHelp(szBuffer, (TechTypes) i);
		mapTechData.push_back(CvWBData(i, szBuffer.getCString(), GC.getTechInfo((TechTypes) i).getButton()));
	}
}

void CvGameTextMgr::getPromotionDataForWB(std::vector<CvWBData>& mapPromotionData)
{
	CvWStringBuffer szBuffer;
	for (int i=0; i < GC.getNumPromotionInfos(); i++)
	{
		szBuffer.clear();
		setPromotionHelp(szBuffer, (PromotionTypes) i, false);
		mapPromotionData.push_back(CvWBData(i, szBuffer.getCString(), GC.getPromotionInfo((PromotionTypes) i).getButton()));
	}
}

void CvGameTextMgr::getBonusDataForWB(std::vector<CvWBData>& mapBonusData)
{
	CvWStringBuffer szBuffer;
	for (int i=0; i < GC.getNumBonusInfos(); i++)
	{
		szBuffer.clear();
		setBonusHelp(szBuffer, (BonusTypes)i);
		mapBonusData.push_back(CvWBData(i, szBuffer.getCString(), GC.getBonusInfo((BonusTypes) i).getButton()));
	}
}

void CvGameTextMgr::getImprovementDataForWB(std::vector<CvWBData>& mapImprovementData)
{
	CvWStringBuffer szBuffer;
	for (int i=0; i < GC.getNumImprovementInfos(); i++)
	{
		CvImprovementInfo& kInfo = GC.getImprovementInfo((ImprovementTypes) i);
		if (!kInfo.isGraphicalOnly())
		{
			szBuffer.clear();
			setImprovementHelp(szBuffer, (ImprovementTypes) i);
			mapImprovementData.push_back(CvWBData(i, szBuffer.getCString(), kInfo.getButton()));
		}
	}
}

void CvGameTextMgr::getReligionDataForWB(bool bHolyCity, std::vector<CvWBData>& mapReligionData)
{
	for (int i = 0; i < GC.getNumReligionInfos(); ++i)
	{
		CvReligionInfo& kInfo = GC.getReligionInfo((ReligionTypes) i);
		CvWString strDescription = kInfo.getDescription();
		if (bHolyCity)
		{
			strDescription = gDLL->getText("TXT_KEY_WB_HOLYCITY", strDescription.GetCString());
		}
		mapReligionData.push_back(CvWBData(i, strDescription, kInfo.getButton()));
	}
}


void CvGameTextMgr::getCorporationDataForWB(bool bHeadquarters, std::vector<CvWBData>& mapCorporationData)
{
	for (int i = 0; i < GC.getNumCorporationInfos(); ++i)
	{
		CvCorporationInfo& kInfo = GC.getCorporationInfo((CorporationTypes) i);
		CvWString strDescription = kInfo.getDescription();
		if (bHeadquarters)
		{
			strDescription = gDLL->getText("TXT_KEY_CORPORATION_HEADQUARTERS", strDescription.GetCString());
		}
		mapCorporationData.push_back(CvWBData(i, strDescription, kInfo.getButton()));
	}
}
// Better AI Debug (Skyre)

const wchar* CvGameTextMgr::getGroupflagName(int iGroupflag) const
{
	FAssert(iGroupflag != GROUPFLAG_NONE);

	switch (iGroupflag)
	{
	case GROUPFLAG_PERMDEFENSE:
		return L"GROUPFLAG_PERMDEFENSE";

	case GROUPFLAG_PATROL:
		return L"GROUPFLAG_PATROL";

	case GROUPFLAG_PATROL_NEW:
		return L"GROUPFLAG_PATROL_NEW";

	case GROUPFLAG_DEFENSE:
		return L"GROUPFLAG_DEFENSE";

	case GROUPFLAG_HERO:
		return L"GROUPFLAG_HERO";

	case GROUPFLAG_CONQUEST:
		return L"GROUPFLAG_CONQUEST";

	case GROUPFLAG_HNGROUP:
		return L"GROUPFLAG_HNGROUP";

	case GROUPFLAG_SVARTALFAR_KIDNAP:
		return L"GROUPFLAG_SVARTALFAR_KIDNAP";

    case GROUPFLAG_SUICIDE_SUMMON:
        return L"GROUPFLAG_SUICIDE_SUMMON";

	default:
		return L"GROUPFLAG_NONE";
	}
}

// End Better AI Debug

// BUG - Defense Help - start

/*
	Defense = max(building, culture) + player

	+50% from Buildings
	+10% from Culture (60%)
	+25% from Wonders
	-----------------------
	Total Defense: 85%
	-----------------------
	-37% from Bombardment
	-----------------------
	Net Defense: 48%
	=======================
	* Castle: +50%
	=======================
	+50% from Buildings
	-----------------------
	Total Bombard Defense: 50%
	=======================
	* Castle: +25%
*/
void CvGameTextMgr::setDefenseHelp(CvWStringBuffer &szBuffer, CvCity& city)
{
	FAssertMsg(NO_PLAYER != city.getOwnerINLINE(), "City must have an owner");

	bool bFirst = true;

	// Buildings
	int iBuildingDefense = city.getBuildingDefense();
	if (iBuildingDefense != 0)
	{
		bFirst = false;
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_BUILDING_DEFENSE", iBuildingDefense));
	}

	// Culture
	int iCultureDefense = city.getNaturalDefense();
	if (iCultureDefense != 0)
	{
		if (!bFirst)
		{
			szBuffer.append(NEWLINE);
		}
		else
		{
			bFirst = false;
		}
		if (iBuildingDefense == 0)
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_CULTURE_DEFENSE", iCultureDefense));
		}
		else
		{
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_CULTURE_DEFENSE_PARTIAL", std::max(iCultureDefense, iBuildingDefense) - iBuildingDefense, iCultureDefense));
		}
	}

	// Wonders (or other player sources in mods)
	int iWonderDefense = GET_PLAYER(city.getOwnerINLINE()).getCityDefenseModifier();
	if (iWonderDefense != 0)
	{
		if (!bFirst)
		{
			szBuffer.append(NEWLINE);
		}
		else
		{
			bFirst = false;
		}
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_WONDER_DEFENSE", iWonderDefense));
	}

	// Total
	int iDefense = city.getTotalDefense(false);
	if (!bFirst)
	{
		szBuffer.append(SEPARATOR NEWLINE);
	}
	szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_TOTAL_DEFENSE", iDefense));

	// Damage and Net
	int iDamage = GC.getMAX_CITY_DEFENSE_DAMAGE() * city.getDefenseDamage() / GC.getMAX_CITY_DEFENSE_DAMAGE();
	if (iDamage != 0)
	{
		szBuffer.append(SEPARATOR NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_DEFENSE_DAMAGE", -iDamage));
		szBuffer.append(SEPARATOR NEWLINE);
		szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_NET_DEFENSE", std::max(0, iDefense - iDamage)));
	}

// BUG - Building Additional Defense - start
	if (city.getOwnerINLINE() == GC.getGame().getActivePlayer() && getBugOptionBOOL("MiscHover__BuildingAdditionalDefense", true, "BUG_BUILDING_ADDITIONAL_DEFENSE_HOVER"))
	{
		setBuildingAdditionalDefenseHelp(szBuffer, city, SEPARATOR);
	}
// BUG - Building Additional Defense - end

	// ==========================
	// Bombardment Defense

	szBuffer.append(DOUBLE_SEPARATOR NEWLINE);
	szBuffer.append(gDLL->getText("TXT_KEY_MISC_HELP_TOTAL_BOMBARD_DEFENSE", city.getBuildingBombardDefense()));

// BUG - Building Additional Bombard Defense - start
	if (city.getOwnerINLINE() == GC.getGame().getActivePlayer() && getBugOptionBOOL("MiscHover__BuildingAdditionalDefense", true, "BUG_BUILDING_ADDITIONAL_DEFENSE_HOVER"))
	{
		setBuildingAdditionalBombardDefenseHelp(szBuffer, city, SEPARATOR);
	}
// BUG - Building Additional Bombard Defense - end

	// ==========================
	// Air Defense - not worth it for just one building
}
// BUG - Defense Help - end

// BUG - Building Additional Defense - start
bool CvGameTextMgr::setBuildingAdditionalDefenseHelp(CvWStringBuffer &szBuffer, const CvCity& city, const CvWString& szStart, bool bStarted)
{
	CvWString szLabel;

	CvCivilizationInfo& kCivilization = GC.getCivilizationInfo((GET_PLAYER(city.getOwnerINLINE())).getCivilizationType());

	int iI;

	for (iI = 0; iI < GC.getNumBuildingClassInfos(); iI++)
	{
		BuildingTypes eLoopBuilding = (BuildingTypes)kCivilization.getCivilizationBuildings((BuildingClassTypes)iI);
		if (eLoopBuilding == NO_BUILDING)
		{
			continue;
		}
		if (city.canConstruct(eLoopBuilding, false, true, false))
		{
			int iChange = city.getAdditionalDefenseByBuilding(eLoopBuilding);

			if (iChange != 0)
			{
				if (!bStarted)
				{
					szBuffer.append(szStart);
					bStarted = true;
				}

				szLabel.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_BUILDING_TEXT"), GC.getBuildingInfo(eLoopBuilding).getDescription());
				setResumableValueChangeHelp(szBuffer, szLabel, L": ", L"", iChange, gDLL->getSymbolID(DEFENSE_CHAR), true, true);
			}
		}
	}

	return bStarted;
}
// BUG - Building Additional Defense - end

// BUG - Building Additional Bombard Defense - start
bool CvGameTextMgr::setBuildingAdditionalBombardDefenseHelp(CvWStringBuffer &szBuffer, const CvCity& city, const CvWString& szStart, bool bStarted)
{
	CvWString szLabel;

	CvCivilizationInfo& kCivilization = GC.getCivilizationInfo((GET_PLAYER(city.getOwnerINLINE())).getCivilizationType());

	int iI;

	for (iI = 0; iI < GC.getNumBuildingClassInfos(); iI++)
	{
		BuildingTypes eLoopBuilding = (BuildingTypes)kCivilization.getCivilizationBuildings((BuildingClassTypes)iI);
		if (eLoopBuilding == NO_BUILDING)
		{
			continue;
		}
		if (city.canConstruct(eLoopBuilding, false, true, false))
		{
			int iChange = city.getAdditionalBombardDefenseByBuilding(eLoopBuilding);

			if (iChange != 0)
			{
				if (!bStarted)
				{
					szBuffer.append(szStart);
					bStarted = true;
				}

				szLabel.Format(SETCOLR L"%s" ENDCOLR, TEXT_COLOR("COLOR_BUILDING_TEXT"), GC.getBuildingInfo(eLoopBuilding).getDescription());
				setResumableValueChangeHelp(szBuffer, szLabel, L": ", L"", iChange, gDLL->getSymbolID(DEFENSE_CHAR), true, true);
			}
		}
	}

	return bStarted;
}
// BUG - Building Additional Bombard Defense - end
/************************************************************************************************/
/* Afforess	                  Start		 07/29/10                                               */
/* Advanced Diplomacy                                                                           */
/************************************************************************************************/
void CvGameTextMgr::buildLimitedBordersString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS))
	{
		if (GC.getTechInfo(eTech).isLimitedBordersTrading() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isLimitedBordersTrading())))
		{
			if (bList)
			{
				szBuffer.append(NEWLINE);
			}
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_ENABLES_LIMITED_BORDERS"));
		}
	}
}

void CvGameTextMgr::buildEmbassyString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS))
	{
		if (GC.getTechInfo(eTech).isEmbassyTrading() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isEmbassyTrading())))
		{
			if (bList)
			{
				szBuffer.append(NEWLINE);
			}
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_ENABLES_EMBASSIES"));
		}
	}
}

void CvGameTextMgr::buildFreeTradeAgreementString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS))
	{
		if (GC.getTechInfo(eTech).isFreeTradeAgreementTrading() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isFreeTradeAgreementTrading())))
		{
			if (bList)
			{
				szBuffer.append(NEWLINE);
			}
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_ENABLES_FREE_TRADE_AGREEMENT"));
		}
	}
}

void CvGameTextMgr::buildNonAggressionString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS))
	{
		if (GC.getTechInfo(eTech).isNonAggressionTrading() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isNonAggressionTrading())))
		{
			if (bList)
			{
				szBuffer.append(NEWLINE);
			}
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_ENABLES_NON_AGGRESSION"));
		}
	}
}

void CvGameTextMgr::buildPOWString(CvWStringBuffer &szBuffer, TechTypes eTech, bool bList, bool bPlayerContext)
{
	if (GC.getGameINLINE().isOption(GAMEOPTION_ADVANCED_TACTICS))
	{
		if (GC.getTechInfo(eTech).isPOWTrading() && (!bPlayerContext || !(GET_TEAM(GC.getGameINLINE().getActiveTeam()).isPOWTrading())))
		{
			if (bList)
			{
				szBuffer.append(NEWLINE);
			}
			szBuffer.append(gDLL->getText("TXT_KEY_MISC_ENABLES_POW_EXCHANGE"));
		}
	}
}

/*
void CvGameTextMgr::setCondemnCivicHelp(CvWStringBuffer& szBuffer, PlayerTypes ePlayer, CivicTypes eCivic)
{
	CvWString szTempBuffer;

	if (GC.getGameINLINE().isCondemnCivic(eCivic))
	{
		szTempBuffer.clear();
		szTempBuffer = gDLL->getText("TXT_KEY_MISC_CIVIC_IS_COND_BY_ONU");
	}
	{
		szBuffer.assign(NEWLINE);
		szBuffer.append(szTempBuffer);
	}
}
*/
/************************************************************************************************/
/* Advanced Diplomacy         END                                                               */
/************************************************************************************************/
