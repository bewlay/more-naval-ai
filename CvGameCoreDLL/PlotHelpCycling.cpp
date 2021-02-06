// lfgr UI 11/2020: Allow cycling through units in plot help

#include "CvGameCoreDLL.h"

#include "PlotHelpCycling.h"

#include "CvGlobals.h"


PlotHelpCyclingManager::PlotHelpCyclingManager()
	: m_iCurrentPlot( -1 ),
	m_iCycleIdx( 0 )
{}

PlotHelpCyclingManager::~PlotHelpCyclingManager() {}

void PlotHelpCyclingManager::updateCurrentPlot( int iCurrentPlot )
{
	if( m_iCurrentPlot != iCurrentPlot )
	{
		m_iCurrentPlot = iCurrentPlot;
		m_iCycleIdx = 0;
	}
}

void PlotHelpCyclingManager::changeCycleIdx( int iChange )
{
	if( m_iCurrentPlot != -1 )
	{
		m_iCycleIdx += iChange;
		CvPlot* pPlot = GC.getMap().plotByIndex( m_iCurrentPlot );
		if( pPlot != NULL ) { // Maybe possible after starting a new game
			pPlot->updateCenterUnit();
		}
	}
}

int PlotHelpCyclingManager::getCycleIdx()
{
	return m_iCycleIdx;
}


PlotHelpCyclingManager gInstance;

PlotHelpCyclingManager& PlotHelpCyclingManager::getInstance()
{
	return gInstance;
}
