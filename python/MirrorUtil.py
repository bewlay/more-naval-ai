""" Utility to complete mirror a map. Useful for creating fully balanced maps for AI testing. """

from CvPythonExtensions import *

def reverse_direction( direction ) :
	if direction == CardinalDirectionTypes.CARDINALDIRECTION_WEST :
		return CardinalDirectionTypes.CARDINALDIRECTION_EAST
	elif direction == CardinalDirectionTypes.CARDINALDIRECTION_EAST :
		return CardinalDirectionTypes.CARDINALDIRECTION_WEST
	elif direction == CardinalDirectionTypes.CARDINALDIRECTION_NORTH :
		return CardinalDirectionTypes.CARDINALDIRECTION_SOUTH
	elif direction == CardinalDirectionTypes.CARDINALDIRECTION_SOUTH :
		return CardinalDirectionTypes.CARDINALDIRECTION_NORTH
	else :
		return CardinalDirectionTypes.NO_CARDINALDIRECTION

def mirror() :
	mp = CyMap()
	for x in xrange( mp.getGridWidth() ) :
		for y in xrange( mp.getGridHeight() ) :
			pPlot = mp.plot( x, y ) # type: CyPlot
			pMirrorPlot = mp.plot( mp.getGridWidth() - 1- x, y ) # type: CyPlot
			
			pMirrorPlot.setPlotType( pPlot.getPlotType(), False, True )
			pMirrorPlot.setTerrainType( pPlot.getTerrainType(), False, True, False )
			pMirrorPlot.setFeatureType( pPlot.getFeatureType(), pPlot.getFeatureVariety() )
			pMirrorPlot.setImprovementType( pPlot.getImprovementType() )
			pMirrorPlot.setBonusType( pPlot.getBonusType( TeamTypes.NO_TEAM ) )
			
			pMirrorPlot.setNOfRiver( pPlot.isNOfRiver(), reverse_direction( pPlot.getRiverWEDirection() ) )
			if x > 0 :
				pEastPlot = mp.plot( x - 1, y ) # type: CyPlot
				pMirrorPlot.setWOfRiver( pEastPlot.isWOfRiver(), pEastPlot.getRiverNSDirection() )
			else :
				pMirrorPlot.setWOfRiver( False, CardinalDirectionTypes.NO_CARDINALDIRECTION ) # TODO: necessary?
			pMirrorPlot.setRiverID( pPlot.getRiverID() )
			
			pMirrorPlot.setStartingPlot( pPlot.isStartingPlot() )
	
	CyMap().recalculateAreas()