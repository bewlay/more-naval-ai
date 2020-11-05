#pragma once

// lfgr UI 11/2020: Allow cycling through units in plot help

#ifndef PLOT_HELP_CYCLING_H
#define PLOT_HELP_CYCLING_H

class PlotHelpCyclingManager
{
public :
	PlotHelpCyclingManager();
	virtual ~PlotHelpCyclingManager();

	// To be called whenever plot help is requested for a plot.
	// If the plot has changed, the cycle idx is reset.
	void updateCurrentPlot( int iCurrentPlot );

	void changeCycleIdx( int iChange );
	int getCycleIdx();

	static PlotHelpCyclingManager& getInstance();

private :
	int m_iCurrentPlot; // Plot (ID) for which help was last shown
	int m_iCycleIdx;
};



#endif
