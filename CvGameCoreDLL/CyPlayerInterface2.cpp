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
		.def("AI_unitValue", &CyPlayer::AI_unitValue, "int (int /*UnitTypes*/ eUnit, int /*UnitAITypes*/ eUnitAI, CyArea* pArea, bool bUpgrade)")
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
// BUG - Refuses to Talk - start
		.def("AI_isWillingToTalk", &CyPlayer::AI_isWillingToTalk, "bool (int /*PlayerTypes*/)")
// BUG - Refuses to Talk - end

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

		/*** PUPPET STATES 04/21/08 by DPII ***/
		.def("makePuppet", &CyPlayer::makePuppet, "bool (int /*PlayerTypes*/ eSplitPlayer, int (CyCity* pVassalCapital)")
		.def("canMakePuppet", &CyPlayer::canMakePuppet, "bool (int /*PlayerTypes*/ eFromPlayer)")
		/*************************************/
/************************************************************************************************/
/* REVOLUTION_MOD                         11/15/08                                jdog5000      */
/*                                                                                              */
/*                                                                                              */
/************************************************************************************************/
		.def("assimilatePlayer", &CyPlayer::assimilatePlayer, "bool ( int iPlayer ) - acquire iPlayer's units and cities")
/************************************************************************************************/
/* REVOLUTION_MOD                          END                                                  */
/************************************************************************************************/
		.def("canHaveTradeRoutesWith", &CyPlayer::canHaveTradeRoutesWith, "bool (int)")
		.def("forcePeace", &CyPlayer::forcePeace, "void (int)")

/************************************************************************************************/
/* REVOLUTION_MOD                         06/11/08                                jdog5000      */
/*                                                                                              */
/*                                                                                              */
/************************************************************************************************/

// BUG - Reminder Mod - start
		.def("addReminder", &CyPlayer::addReminder, "void (int iGameTurn, string szMessage)")
// BUG - Reminder Mod - end
		.def("setFoundedFirstCity", &CyPlayer::setFoundedFirstCity, "void (bool bNewValue)")
		.def("setAlive", &CyPlayer::setAlive, "void (bool bNewValue)")
		.def("setNewPlayerAlive", &CyPlayer::setNewPlayerAlive, "void (bool bNewValue) - like setAlive, but without firing turn logic")
		.def("changeTechScore", &CyPlayer::changeTechScore, "void (int iChange)" )
		.def("getStabilityIndex", &CyPlayer::getStabilityIndex, "int ( )")
		.def("setStabilityIndex", &CyPlayer::setStabilityIndex, "void ( int iNewValue )")
		.def("changeStabilityIndex", &CyPlayer::changeStabilityIndex, "void ( int iChange )")
		.def("getStabilityIndexAverage", &CyPlayer::getStabilityIndexAverage, "int ( )")
		.def("setStabilityIndexAverage", &CyPlayer::setStabilityIndexAverage, "void ( int iNewValue )")
		.def("updateStabilityIndexAverage", &CyPlayer::updateStabilityIndexAverage, "void ( )")
/************************************************************************************************/
/* LoR                                        11/03/10                          phungus420      */
/*                                                                                              */
/* Colonists                                                                                    */
/************************************************************************************************/
		.def("getBestUnitType", &CyPlayer::getBestUnitType, "int ()")
/************************************************************************************************/
/* LoR                            END                                                           */
/************************************************************************************************/
/************************************************************************************************/
/* REVDCM                                 09/02/10                                phungus420    */
/*                                                                                              */
/* Player Functions                                                                             */
/************************************************************************************************/
		.def("isNonStateReligionCommerce", &CyPlayer::isNonStateReligionCommerce, "bool ()")
		.def("isUpgradeAnywhere", &CyPlayer::isUpgradeAnywhere, "bool ()")
		.def("getRevIdxLocal", &CyPlayer::getRevIdxLocal, "int ()")
		.def("getRevIdxNational", &CyPlayer::getRevIdxNational, "int ()")
		.def("getRevIdxDistanceModifier", &CyPlayer::getRevIdxDistanceModifier, "int ()")
		.def("getRevIdxHolyCityGood", &CyPlayer::getRevIdxHolyCityGood, "int ()")
		.def("getRevIdxHolyCityBad", &CyPlayer::getRevIdxHolyCityBad, "int ()")
		.def("getRevIdxNationalityMod", &CyPlayer::getRevIdxNationalityMod, "float ()")
		.def("getRevIdxBadReligionMod", &CyPlayer::getRevIdxBadReligionMod, "float ()")
		.def("getRevIdxGoodReligionMod", &CyPlayer::getRevIdxGoodReligionMod, "float ()")
		//.def("isInquisitionConditions", &CyPlayer::isInquisitionConditions, "bool ()")
		//.def("getUnitUpgradePriceModifier", &CyPlayer::getUnitUpgradePriceModifier, "int ()")
		//.def("canFoundReligion", &CyPlayer::canFoundReligion, "bool ()")
		//.def("isBuildingClassRequiredToTrain", &CyPlayer::isBuildingClassRequiredToTrain, "bool ((BuildingClassTypes)iBuildingClass, (UnitTypes)iUnit)")
/************************************************************************************************/
/* REVDCM                                  END                                                  */
/************************************************************************************************/
/************************************************************************************************/
/* REVDCM                                 			                              glider1       */
/*                                                                                              */
/* RevolutionDCM - revolution stability history                                                 */
/************************************************************************************************/
		.def("getRevolutionStabilityHistory", &CyPlayer::getRevolutionStabilityHistory, "int (int iTurn)")
/************************************************************************************************/
/* REVDCM                                  END                                                  */
/************************************************************************************************/	

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
		.def("isAgnostic", &CyPlayer::isAgnostic, "bool ()")
		.def("isIgnoreFood", &CyPlayer::isIgnoreFood, "bool ()")
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
