#include "CvGameCoreDLL.h"
#include "CyPlayer.h"
#include "CyUnit.h"
#include "CyCity.h"
#include "CyPlot.h"
#include "CySelectionGroup.h"
#include "CyArea.h"
//# include <boost/python/manage_new_object.hpp>
//# include <boost/python/return_value_policy.hpp>
//# include <boost/python/scope.hpp>

//
// published python interface for CyPlayer
//

void CyPlayerPythonInterface2(python::class_<CyPlayer>& x)
{
	OutputDebugString("Python Extension Module - CyPlayerPythonInterface2\n");

	// set the docstring of the current module scope
	python::scope().attr("__doc__") = "Civilization IV Player Class";
	x
		.def("AI_updateFoundValues", &CyPlayer::AI_updateFoundValues, "void (bool bStartingLoc)")
		.def("AI_foundValue", &CyPlayer::AI_foundValue, "int (int, int, int, bool)")
		.def("AI_isFinancialTrouble", &CyPlayer::AI_isFinancialTrouble, "bool ()")
		.def("AI_demandRebukedWar", &CyPlayer::AI_demandRebukedWar, "bool (int /*PlayerTypes*/)")
		.def("AI_getAttitude", &CyPlayer::AI_getAttitude, "AttitudeTypes (int /*PlayerTypes*/) - Gets the attitude of the player towards the player passed in")
		.def("AI_unitValue", &CyPlayer::AI_unitValue, "int (int /*UnitTypes*/ eUnit, int /*UnitAITypes*/ eUnitAI, CyArea* pArea)")
		.def("AI_civicValue", &CyPlayer::AI_civicValue, "int (int /*CivicTypes*/ eCivic)")
		.def("AI_totalUnitAIs", &CyPlayer::AI_totalUnitAIs, "int (int /*UnitAITypes*/ eUnitAI)")
		.def("AI_totalAreaUnitAIs", &CyPlayer::AI_totalAreaUnitAIs, "int (CyArea* pArea, int /*UnitAITypes*/ eUnitAI)")
		.def("AI_totalWaterAreaUnitAIs", &CyPlayer::AI_totalWaterAreaUnitAIs, "int (CyArea* pArea, int /*UnitAITypes*/ eUnitAI)")
		.def("AI_getNumAIUnits", &CyPlayer::AI_getNumAIUnits, "int (UnitAIType) - Returns # of UnitAITypes the player current has of UnitAIType")
		.def("AI_getAttitudeExtra", &CyPlayer::AI_getAttitudeExtra, "int (int /*PlayerTypes*/ eIndex) - Returns the extra attitude for this player - usually scenario specific")
		.def("AI_setAttitudeExtra", &CyPlayer::AI_setAttitudeExtra, "void (int /*PlayerTypes*/ eIndex, int iNewValue) - Sets the extra attitude for this player - usually scenario specific")
		.def("AI_changeAttitudeExtra", &CyPlayer::AI_changeAttitudeExtra, "void (int /*PlayerTypes*/ eIndex, int iChange) - Changes the extra attitude for this player - usually scenario specific")
		.def("AI_getMemoryCount", &CyPlayer::AI_getMemoryCount, "int (/*PlayerTypes*/ eIndex1, /*MemoryTypes*/ eIndex2)")
		.def("AI_changeMemoryCount", &CyPlayer::AI_changeMemoryCount, "void (/*PlayerTypes*/ eIndex1, /*MemoryTypes*/ eIndex2, int iChange)")
		.def("AI_getExtraGoldTarget", &CyPlayer::AI_getExtraGoldTarget, "int ()")
		.def("AI_setExtraGoldTarget", &CyPlayer::AI_setExtraGoldTarget, "void (int)")

		.def("getScoreHistory", &CyPlayer::getScoreHistory, "int (int iTurn)")
		.def("getEconomyHistory", &CyPlayer::getEconomyHistory, "int (int iTurn)")
		.def("getIndustryHistory", &CyPlayer::getIndustryHistory, "int (int iTurn)")
		.def("getAgricultureHistory", &CyPlayer::getAgricultureHistory, "int (int iTurn)")
		.def("getPowerHistory", &CyPlayer::getPowerHistory, "int (int iTurn)")
		.def("getCultureHistory", &CyPlayer::getCultureHistory, "int (int iTurn)")
		.def("getEspionageHistory", &CyPlayer::getEspionageHistory, "int (int iTurn)")

		.def("getScriptData", &CyPlayer::getScriptData, "str () - Get stored custom data (via pickle)")
		.def("setScriptData", &CyPlayer::setScriptData, "void (str) - Set stored custom data (via pickle)")

		.def("chooseTech", &CyPlayer::chooseTech, "void (int iDiscover, wstring szText, bool bFront)")

		.def("AI_maxGoldTrade", &CyPlayer::AI_maxGoldTrade, "int (int)")
		.def("AI_maxGoldPerTurnTrade", &CyPlayer::AI_maxGoldPerTurnTrade, "int (int)")

		.def("splitEmpire", &CyPlayer::splitEmpire, "bool (int iAreaId)")
		.def("canSplitEmpire", &CyPlayer::canSplitEmpire, "bool ()")
		.def("canSplitArea", &CyPlayer::canSplitArea, "bool (int)")
//>>>>Unofficial Bug Fix: Added by Denev 2010/02/20
//*** Fix Basium empire can not receive Forge from Guild of Hammers.
		.def("getOpenPlayer", &CyPlayer::getOpenPlayer, "int /*PlayerTypes*/ ()")
		.def("initNewEmpire", &CyPlayer::initNewEmpire, "int /*PlayerTypes*/ (int /*LeaderHeadTypes*/ eNewLeader, int /*CivilizationTypes*/ eNewCiv)")
		.def("setParent", &CyPlayer::setParent, "void (int /*PlayerTypes*/ eParent)")
//<<<<Unofficial Bug Fix: End Add
		.def("canHaveTradeRoutesWith", &CyPlayer::canHaveTradeRoutesWith, "bool (int)")
		.def("forcePeace", &CyPlayer::forcePeace, "void (int)")

//FfH Alignment: Added by Kael 08/09/2007
		.def("canSeeCivic", &CyPlayer::canSeeCivic, "void (int iCivic)")
		.def("canSeeReligion", &CyPlayer::canSeeReligion, "void (int iReligion)")
		.def("changeSanctuaryTimer", &CyPlayer::changeSanctuaryTimer, "void (int iChange)")
		.def("getAlignment", &CyPlayer::getAlignment, "int ()")
        .def("setAlignment", &CyPlayer::setAlignment, "AlignmentTypes (iAlignment)")
		.def("changeDisableProduction", &CyPlayer::changeDisableProduction, "void (int iChange)")
		.def("getDisableProduction", &CyPlayer::getDisableProduction, "int ()")
		.def("changeDisableResearch", &CyPlayer::changeDisableResearch, "void (int iChange)")
		.def("getDisableResearch", &CyPlayer::getDisableResearch, "int ()")
		.def("changeDisableSpellcasting", &CyPlayer::changeDisableSpellcasting, "void (int iChange)")
		.def("getDisableSpellcasting", &CyPlayer::getDisableSpellcasting, "int ()")
		.def("getMaxCities", &CyPlayer::getMaxCities, "int ()")
		.def("changeNoDiplomacyWithEnemies", &CyPlayer::changeNoDiplomacyWithEnemies, "void (int iChange)")
		.def("getNumBuilding", &CyPlayer::getNumBuilding, "int (int iBuilding)")
		.def("getNumSettlements", &CyPlayer::getNumSettlements, "int ()")
		.def("getPlayersKilled", &CyPlayer::getPlayersKilled, "int ()")
		.def("isGamblingRing", &CyPlayer::isGamblingRing, "bool ()")
		.def("isHasTech", &CyPlayer::isHasTech, "bool (int iTech)")
		.def("isSlaveTrade", &CyPlayer::isSlaveTrade, "bool ()")
		.def("isSmugglingRing", &CyPlayer::isSmugglingRing, "bool ()")
        .def("setAlive", &CyPlayer::setAlive, "void (bool bNewValue)")
        .def("setFoundedFirstCity", &CyPlayer::setFoundedFirstCity, "void (bool bNewValue)")
		.def("setGreatPeopleCreated", &CyPlayer::setGreatPeopleCreated, "void (int iNewValue)")
		.def("setGreatPeopleThresholdModifier", &CyPlayer::setGreatPeopleThresholdModifier, "void (int iNewValue)")
        .def("setHasTrait", &CyPlayer::setHasTrait, "TraitTypes (eTrait), bool (bNewValue)")
//FfH: End Add

/*************************************************************************************************/
/**	BETTER AI (New Functions Definition) Sephi                                 					**/
/**																								**/
/**						                                            							**/
/*************************************************************************************************/
        .def("getFavoriteReligion",&CyPlayer::getFavoriteReligion, "int ()")
        .def("setFavoriteReligion",&CyPlayer::setFavoriteReligion, "void (ReligionTypes (newvalue))")
        .def("getArcaneTowerVictoryFlag",&CyPlayer::getArcaneTowerVictoryFlag, "int ()")
        .def("countGroupFlagUnits",&CyPlayer::countGroupFlagUnits, "int (int)")
/*************************************************************************************************/
/**	END	                                        												**/
/*************************************************************************************************/

		;
}
