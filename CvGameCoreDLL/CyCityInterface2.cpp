#include "CvGameCoreDLL.h"
#include "CyCity.h"
#include "CyPlot.h"
#include "CyArea.h"
#include "CvInfos.h"

//# include <boost/python/manage_new_object.hpp>
//# include <boost/python/return_value_policy.hpp>

//
// published python interface for CyCity
//

void CyCityPythonInterface2(python::class_<CyCity>& x)
{
	OutputDebugString("Python Extension Module - CyCityPythonInterface2\n");

	x
	
/************************************************************************************************/
/* Afforess	                  Start		 07/30/10                                               */
/*                                                                                              */
/* Moved From CyCityInterface1 to avoid module size limit                                       */
/************************************************************************************************/

		.def("getUnitCombatFreeExperience", &CyCity::getUnitCombatFreeExperience, "int (int /*UnitCombatTypes*/ eIndex)")
		.def("getFreePromotionCount", &CyCity::getFreePromotionCount, "int (int /*PromotionTypes*/ eIndex)")
		.def("isFreePromotion", &CyCity::isFreePromotion, "bool (int /*PromotionTypes*/ eIndex)")
		.def("getSpecialistFreeExperience", &CyCity::getSpecialistFreeExperience, "int ()")
		.def("getEspionageDefenseModifier", &CyCity::getEspionageDefenseModifier, "int ()")

		.def("isWorkingPlotByIndex", &CyCity::isWorkingPlotByIndex, "bool (iIndex) - true if a worker is working this city's plot iIndex")
		.def("isWorkingPlot", &CyCity::isWorkingPlot, "bool (iIndex) - true if a worker is working this city's pPlot")
		.def("alterWorkingPlot", &CyCity::alterWorkingPlot, "void (iIndex)")	
		.def("getNumRealBuilding", &CyCity::getNumRealBuilding, "int (BuildingID) - get # real building of this type")
		.def("setNumRealBuilding", &CyCity::setNumRealBuilding, "(BuildingID, iNum) - Sets number of buildings in this city of BuildingID type")
		.def("getNumFreeBuilding", &CyCity::getNumFreeBuilding, "int (BuildingID) - # of free Building ID (ie: from a Wonder)")
		.def("isHasReligion", &CyCity::isHasReligion, "bool (ReligionID) - does city have ReligionID?")
		.def("setHasReligion", &CyCity::setHasReligion, "void (ReligionID, bool bNewValue, bool bAnnounce, bool bArrows) - religion begins to spread")
		.def("isHasCorporation", &CyCity::isHasCorporation, "bool (CorporationID) - does city have CorporationID?")
		.def("setHasCorporation", &CyCity::setHasCorporation, "void (CorporationID, bool bNewValue, bool bAnnounce, bool bArrows) - corporation begins to spread")
		.def("isActiveCorporation", &CyCity::isActiveCorporation, "bool (CorporationID) - does city have active CorporationID?")
		.def("getTradeCity", &CyCity::getTradeCity, python::return_value_policy<python::manage_new_object>(), "CyCity (int iIndex) - remove SpecialistType[iIndex]")
		.def("getTradeRoutes", &CyCity::getTradeRoutes, "int ()")

		.def("clearOrderQueue", &CyCity::clearOrderQueue, "void ()")
		.def("pushOrder", &CyCity::pushOrder, "void (OrderTypes eOrder, int iData1, int iData2, bool bSave, bool bPop, bool bAppend, bool bForce)")
		.def("popOrder", &CyCity::popOrder, "int (int iNum, bool bFinish, bool bChoose)")
		.def("getOrderQueueLength", &CyCity::getOrderQueueLength, "void ()")
		.def("getOrderFromQueue", &CyCity::getOrderFromQueue, python::return_value_policy<python::manage_new_object>(), "OrderData* (int iIndex)")

		.def("setWallOverridePoints", &CyCity::setWallOverridePoints, "setWallOverridePoints(const python::tuple& kPoints)")
		.def("getWallOverridePoints", &CyCity::getWallOverridePoints, "python::tuple getWallOverridePoints()")

		.def("AI_avoidGrowth", &CyCity::AI_avoidGrowth, "bool ()")
		.def("AI_isEmphasize", &CyCity::AI_isEmphasize, "bool (int iEmphasizeType)")
		.def("AI_countBestBuilds", &CyCity::AI_countBestBuilds, "int (CyArea* pArea)")
		.def("AI_cityValue", &CyCity::AI_cityValue, "int ()")

		.def("getScriptData", &CyCity::getScriptData, "str () - Get stored custom data (via pickle)")
		.def("setScriptData", &CyCity::setScriptData, "void (str) - Set stored custom data (via pickle)")

		.def("visiblePopulation", &CyCity::visiblePopulation, "int ()")

		.def("getBuildingYieldChange", &CyCity::getBuildingYieldChange, "int (int /*BuildingClassTypes*/ eBuildingClass, int /*YieldTypes*/ eYield)")
		.def("setBuildingYieldChange", &CyCity::setBuildingYieldChange, "void (int /*BuildingClassTypes*/ eBuildingClass, int /*YieldTypes*/ eYield, int iChange)")
		.def("getBuildingCommerceChange", &CyCity::getBuildingCommerceChange, "int (int /*BuildingClassTypes*/ eBuildingClass, int /*CommerceTypes*/ eCommerce)")
		.def("setBuildingCommerceChange", &CyCity::setBuildingCommerceChange, "void (int /*BuildingClassTypes*/ eBuildingClass, int /*CommerceTypes*/ eCommerce, int iChange)")
		.def("getBuildingHappyChange", &CyCity::getBuildingHappyChange, "int (int /*BuildingClassTypes*/ eBuildingClass)")
		.def("setBuildingHappyChange", &CyCity::setBuildingHappyChange, "void (int /*BuildingClassTypes*/ eBuildingClass, int iChange)")
		.def("getBuildingHealthChange", &CyCity::getBuildingHealthChange, "int (int /*BuildingClassTypes*/ eBuildingClass)")
		.def("setBuildingHealthChange", &CyCity::setBuildingHealthChange, "void (int /*BuildingClassTypes*/ eBuildingClass, int iChange)")

		.def("getLiberationPlayer", &CyCity::getLiberationPlayer, "int ()")
		.def("liberate", &CyCity::liberate, "void ()")
		
/************************************************************************************************/
/* Afforess	                     END                                                            */
/************************************************************************************************/
		/********************************************************************************/
		/**		REVOLUTION_MOD							03/29/09			jdog5000	*/
		/**																				*/
		/**		 																		*/
		/********************************************************************************/
		.def("getRevolutionIndex", &CyCity::getRevolutionIndex, "int ()")
		.def("setRevolutionIndex", &CyCity::setRevolutionIndex, "void ( int iNewValue )")
		.def("changeRevolutionIndex", &CyCity::changeRevolutionIndex, "void ( int iChange )" )

		.def("getLocalRevIndex", &CyCity::getLocalRevIndex, "int ()" )
		.def("setLocalRevIndex", &CyCity::setLocalRevIndex, "void ( int iNewValue )" )
		.def("changeLocalRevIndex", &CyCity::changeLocalRevIndex, "void ( int iChange )" )

		.def("getRevIndexAverage", &CyCity::getRevIndexAverage, "int ()" )
		.def("setRevIndexAverage", &CyCity::setRevIndexAverage, "void (int iNewValue)" )
		.def("updateRevIndexAverage", &CyCity::updateRevIndexAverage, "void ( )" )

		.def("getRevolutionCounter", &CyCity::getRevolutionCounter, "int ()")
		.def("setRevolutionCounter", &CyCity::setRevolutionCounter, "void ( int iNewValue )")
		.def("changeRevolutionCounter", &CyCity::changeRevolutionCounter, "void ( int iChange )" )

		.def("getReinforcementCounter", &CyCity::getReinforcementCounter, "int ()")
		.def("setReinforcementCounter", &CyCity::setReinforcementCounter, "void ( int iNewValue )")
		.def("changeReinforcementCounter", &CyCity::changeReinforcementCounter, "void ( int iChange )" )

		.def("getRevIndexHappinessVal", &CyCity::getRevIndexHappinessVal, "int ()")
		.def("getRevIndexDistanceVal", &CyCity::getRevIndexDistanceVal, "int ()")
		.def("getRevIndexColonyVal", &CyCity::getRevIndexColonyVal, "int ()")
		.def("getRevIndexReligionVal", &CyCity::getRevIndexReligionVal, "int ()")
		.def("getRevIndexNationalityVal", &CyCity::getRevIndexNationalityVal, "int ()")
		.def("getRevIndexHealthVal", &CyCity::getRevIndexHealthVal, "int ()")
		.def("getRevIndexGarrisonVal", &CyCity::getRevIndexGarrisonVal, "int ()")
		.def("getRevIndexDisorderVal", &CyCity::getRevIndexDisorderVal, "int ()")

		.def("isRecentlyAcquired", &CyCity::isRecentlyAcquired, "bool ()")
		/********************************************************************************/
		/**		REVOLUTION_MOD							END								*/
		/********************************************************************************/
		/********************************************************************************/
		/**		REVOLUTION_MOD							4/19/08				jdog5000	*/
		/**																				*/
		/**																				*/
		/********************************************************************************/
		.def("getRevRequestPercentAnger", &CyCity::getRevRequestPercentAnger, "int ()")
		.def("getRevIndexPercentAnger", &CyCity::getRevIndexPercentAnger, "int ()")
		/********************************************************************************/
		/**		REVOLUTION_MOD							END								*/
		/********************************************************************************/
		/********************************************************************************/
		/**		REVOLUTION_MOD							04/28/08			jdog5000	*/
		/**																				*/
		/**																				*/
		/********************************************************************************/
		.def("getRevRequestAngerTimer", &CyCity::getRevRequestAngerTimer, "int () - Anger caused by refusing a request")
		.def("changeRevRequestAngerTimer", &CyCity::changeRevRequestAngerTimer, "void (int iChange) - adjust Rev Request anger timer by iChange")
		.def("getRevSuccessTimer", &CyCity::getRevSuccessTimer, "int () - Anger caused by refusing a request")
		.def("changeRevSuccessTimer", &CyCity::changeRevSuccessTimer, "void (int iChange) - adjust Rev Request anger timer by iChange")
		/********************************************************************************/
		/**		REVOLUTION_MOD							END								*/
		/********************************************************************************/
		/********************************************************************************/
		/**		REVOLUTION_MOD							08/23/08			jdog5000	*/
		/**																				*/
		/**		 																		*/
		/********************************************************************************/
		.def("getNumRevolts", &CyCity::getNumRevolts, "int (PlayerTypes eIndex)")
		.def("changeNumRevolts", &CyCity::changeNumRevolts, "int (PlayerTypes eIndex, int iChange)" )
		/********************************************************************************/
		/**		REVOLUTION_MOD							END								*/
		/********************************************************************************/
		/************************************************************************************************/
		/* REVOLUTION_MOD                         02/01/09                                jdog5000      */
		/*                                                                                              */
		/*                                                                                              */
		/************************************************************************************************/
		.def("AI_bestUnit", &CyCity::AI_bestUnit, "int /*UnitTypes*/ ()")
		.def("AI_bestUnitAI", &CyCity::AI_bestUnitAI, "int /*UnitTypes*/ (int iUnitAIType)")
		.def("AI_bestBuilding", &CyCity::AI_bestBuilding, "int /*BuildingTypes*/ (int iFocusFlags)")
		/************************************************************************************************/
		/* REVOLUTION_MOD                          END                                                  */
		/************************************************************************************************/
// BUG - Building Additional Great People - start
		.def("getAdditionalGreatPeopleRateByBuilding", &CyCity::getAdditionalGreatPeopleRateByBuilding, "int (int /*BuildingTypes*/)")
		.def("getAdditionalBaseGreatPeopleRateByBuilding", &CyCity::getAdditionalBaseGreatPeopleRateByBuilding, "int (int /*BuildingTypes*/)")
		.def("getAdditionalGreatPeopleRateModifierByBuilding", &CyCity::getAdditionalGreatPeopleRateModifierByBuilding, "int (int /*BuildingTypes*/)")
// BUG - Building Additional Great People - end
// BUG - Building Saved Maintenance - start
		.def("getSavedMaintenanceByBuilding", &CyCity::getSavedMaintenanceByBuilding, "int (int /*BuildingTypes*/)")
		.def("getSavedMaintenanceTimes100ByBuilding", &CyCity::getSavedMaintenanceTimes100ByBuilding, "int (int /*BuildingTypes*/)")
// BUG - Building Saved Maintenance - end
// BUG - Building Additional Yield - start
		.def("getAdditionalYieldByBuilding", &CyCity::getAdditionalYieldByBuilding, "int (int /*YieldTypes*/, int /*BuildingTypes*/) - total change of YieldType from adding one BuildingType")
		.def("getAdditionalBaseYieldRateByBuilding", &CyCity::getAdditionalBaseYieldRateByBuilding, "int (int /*YieldTypes*/, int /*BuildingTypes*/) - base rate change of YieldType from adding one BuildingType")
		.def("getAdditionalYieldRateModifierByBuilding", &CyCity::getAdditionalYieldRateModifierByBuilding, "int (int /*YieldTypes*/, int /*BuildingTypes*/) - rate modifier change of YieldType from adding one BuildingType")
// BUG - Building Additional Yield - end
// BUG - Fractional Trade Routes - start
#ifdef _MOD_FRACTRADE
		.def("calculateTradeProfitTimes100", &CyCity::calculateTradeProfitTimes100, "int (CyCity) - returns the unrounded trade profit created by CyCity")
#endif
// BUG - Fractional Trade Routes - end
// BUG - Building Additional Commerce - start
		.def("getAdditionalCommerceByBuilding", &CyCity::getAdditionalCommerceByBuilding, "int (int /*CommerceTypes*/, int /*BuildingTypes*/) - rounded change of CommerceType from adding one BuildingType")
		.def("getAdditionalCommerceTimes100ByBuilding", &CyCity::getAdditionalCommerceTimes100ByBuilding, "int (int /*CommerceTypes*/, int /*BuildingTypes*/) - total change of CommerceType from adding one BuildingType")
		.def("getAdditionalBaseCommerceRateByBuilding", &CyCity::getAdditionalBaseCommerceRateByBuilding, "int (int /*CommerceTypes*/, int /*BuildingTypes*/) - base rate change of CommerceType from adding one BuildingType")
		.def("getAdditionalCommerceRateModifierByBuilding", &CyCity::getAdditionalCommerceRateModifierByBuilding, "int (int /*CommerceTypes*/, int /*BuildingTypes*/) - rate modifier change of CommerceType from adding one BuildingType")
// BUG - Building Additional Commerce - end
// BUG - Production Decay - start
		.def("isBuildingProductionDecay", &CyCity::isBuildingProductionDecay, "bool (int eIndex)")
		.def("getBuildingProductionDecay", &CyCity::getBuildingProductionDecay, "int (int eIndex)")
		.def("getBuildingProductionDecayTurns", &CyCity::getBuildingProductionDecayTurns, "int (int eIndex)")
// BUG - Production Decay - end
// BUG - Production Decay - start
		.def("getUnitProductionTime", &CyCity::getUnitProductionTime, "int (int eIndex)")
		.def("setUnitProductionTime", &CyCity::setUnitProductionTime, "int (int eIndex, int iNewValue)")
		.def("changeUnitProductionTime", &CyCity::changeUnitProductionTime, "int (int eIndex, int iChange)")
		.def("isUnitProductionDecay", &CyCity::isUnitProductionDecay, "bool (int eIndex)")
		.def("getUnitProductionDecay", &CyCity::getUnitProductionDecay, "int (int eIndex)")
		.def("getUnitProductionDecayTurns", &CyCity::getUnitProductionDecayTurns, "int (int eIndex)")
// BUG - Production Decay - end
		;
}
