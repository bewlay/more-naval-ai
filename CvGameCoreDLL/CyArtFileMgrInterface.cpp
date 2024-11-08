#include "CvGameCoreDLL.h"
#include "CyArtFileMgr.h"
#include "CvInfos.h"

//
// published python interface for CyArea
//

void CyArtFileMgrPythonInterface()
{
	OutputDebugString("Python Extension Module - CyArtFileMgrPythonInterface\n");

	python::class_<CyArtFileMgr>("CyArtFileMgr")
		.def("isNone", &CyArtFileMgr::isNone, "bool () - Checks to see if pointer points to a real object")

		.def("Reset", &CyArtFileMgr::Reset, "void ()")
		.def("buildArtFileInfoMaps", &CyArtFileMgr::buildArtFileInfoMaps, "void ()")

		.def("getInterfaceArtInfo", &CyArtFileMgr::getInterfaceArtInfo,  python::return_value_policy<python::reference_existing_object>(), "CvArtInfoInterface ( str )")
		.def("getMovieArtInfo", &CyArtFileMgr::getMovieArtInfo,  python::return_value_policy<python::reference_existing_object>(), "CvArtInfoMovie ( str )")
		.def("getMiscArtInfo", &CyArtFileMgr::getMiscArtInfo, python::return_value_policy<python::reference_existing_object>(), "CvArtInfoMisc ( str )")
		.def("getUnitArtInfo", &CyArtFileMgr::getUnitArtInfo, python::return_value_policy<python::reference_existing_object>(), "CvArtInfoUnit ( str )")
		.def("getBuildingArtInfo", &CyArtFileMgr::getBuildingArtInfo, python::return_value_policy<python::reference_existing_object>(), "CvArtInfoBuilding ( str )")
		.def("getCivilizationArtInfo", &CyArtFileMgr::getCivilizationArtInfo, python::return_value_policy<python::reference_existing_object>(), "CvArtInfoCivilization ( str )")
		.def("getLeaderheadArtInfo", &CyArtFileMgr::getLeaderheadArtInfo, python::return_value_policy<python::reference_existing_object>(), "CvArtInfoLeaderhead ( str )")
		.def("getBonusArtInfo", &CyArtFileMgr::getBonusArtInfo, python::return_value_policy<python::reference_existing_object>(), "CvArtInfoBonus ( str )")
		.def("getImprovementArtInfo", &CyArtFileMgr::getImprovementArtInfo, python::return_value_policy<python::reference_existing_object>(), "CvArtInfoImprovement ( str )")
		.def("getTerrainArtInfo", &CyArtFileMgr::getTerrainArtInfo, python::return_value_policy<python::reference_existing_object>(), "CvArtInfoTerrain ( str )")
		.def("getFeatureArtInfo", &CyArtFileMgr::getFeatureArtInfo, python::return_value_policy<python::reference_existing_object>(), "CvArtInfoFeature ( str )")
	;
}

