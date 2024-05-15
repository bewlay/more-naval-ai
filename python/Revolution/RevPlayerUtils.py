from CvPythonExtensions import *

import CvUtil
import RevData
import RevDefs
import RevMessages
import RevSpawning
import RevUtils

gc = CyGlobalContext()

LOG_DEBUG = True

### Utility

def log( s ) :
	# type: ( str ) -> None
	CvUtil.pyPrint( "  RevPlayerUtils - %s" % s )


def _cedeCityToRebels( pCity, pRevPlayer ) :
	# type: ( CyCity, CyPlayer ) -> Optional[CyCity]
	"""
	Transfers a city to a rebel player. Saves most of the buildings, updates data and adds some disorder.
	Returns the new city object, or None if the city could not be transferred and was destroyed instead.
	"""

	pPlayer = gc.getPlayer( pCity.getOwner() )

	# Clear revolution player # LFGR_TODO: Necessary?
	RevData.setRevolutionPlayer( pCity, -1 )

	# Store building types in city
	leBuildingClasses = [
			(gc.getBuildingInfo( eBuilding ).getBuildingClassType(), pCity.getNumRealBuilding( eBuilding ))
			for eBuilding in range( gc.getNumBuildingInfos() ) if pCity.getNumRealBuilding( eBuilding ) > 0
		]


	# lfgr note: The comment out stuff below is from RevDCM -- apparently it is not that easy to safely acquire a city.

	# Acquire city
	# joinPlayer.acquireCity( pCity, False, True )

	if LOG_DEBUG : log( "Population of %s before is %d" % (pCity.getName(), pCity.getPopulation()) )
	if LOG_DEBUG : log( "Check city culture is %d, at %d, %d" % (
	pCity.getCulture( pPlayer.getID() ), pCity.getX(), pCity.getY()) )
	cityPlot = pCity.plot()
	if pCity.getCulture( pPlayer.getID() ) == 0 :
		if LOG_DEBUG : log( "Forcing culture > 0" )
		pCity.setCulture( pPlayer.getID(), 1, True )

	try :
		pCity.plot().setOwner( pRevPlayer.getID() )
	except :
		print "ERROR in grant independence"
		print "ERROR:  Failed to set owner of city, %s at plot %d, %d" % (
		pCity.getName(), cityPlot.getX(), cityPlot.getY())
		# print "City culture is %d"%(pCity.getCulture(pPlayer.getID()))

		# pCity = cityPlot.getPlotCity()
		# print "Post culture in %s is %d"%(pCity.getName(),pCity.getCulture(pPlayer.getID()))
		# pRevPlayer.acquireCity( pCity, False, False )
		# RevData.initCity(pCity)
		# City has become invalid, will cause game to crash if left
		print "Destroying city so game can continue"
		pCity.kill()
		return None

	pCity = cityPlot.getPlotCity()
	if LOG_DEBUG : log( "Population of %s after is %d" % (pCity.getName(), pCity.getPopulation()) )

	if pCity.getPopulation() < 1 :
		if LOG_DEBUG : log( "Error!  City %s is empty" % (pCity.getName()) )

	# Save most buildings
	for eClass, iNum in leBuildingClasses :
		eBuilding = gc.getCivilizationInfo( pRevPlayer.getCivilizationType() ).getCivilizationBuildings( eClass )
		if eBuilding != BuildingTypes.NO_BUILDING :
			if pCity.getNumRealBuilding( eBuilding ) < iNum :
				buildingInfo = gc.getBuildingInfo( eBuilding )
				if not buildingInfo.isGovernmentCenter() :
					if LOG_DEBUG : log( "Building %s saved" % (buildingInfo.getDescription()) )
					pCity.setNumRealBuilding( eBuilding, iNum )

	if not pRevPlayer.isBarbarian() :
		RevData.setRevolutionPlayer( pCity, pRevPlayer.getID() )

	# City starts in disorder
	pCity.setOccupationTimer( 2 )

	return pCity

def _initCededCityUnits( pCity, pPreviousOwner, bGiveMap ) :
	# type: ( CyCity, CyPlayer, bool ) -> None

	pOwner = gc.getPlayer( pCity.getOwner() )

	# Record pre-given units for deletion after giving other units
	defaultUnits = RevUtils.getPlayerUnits( pCity.getX(), pCity.getY(), pCity.getOwner() )

	iNumUnits = 3

	if pOwner.getNumCities() <= 2 :
		# Extra units for first two cities
		iNumUnits += 1
	elif gc.getTeam( pPreviousOwner.getTeam() ).isAtWar( pOwner.getTeam() ) :
		iNumUnits += 1

	lpUnits = RevSpawning.createRebelCityUnits( pCity, pOwner, iNumUnits )
	if bGiveMap and len( lpUnits ) > 0 :
		eMapGoody =  CvUtil.findInfoTypeNum( gc.getGoodyInfo,gc.getNumGoodyInfos(), RevDefs.sXMLGoodyMap )
		pOwner.receiveGoody( pCity.plot(), eMapGoody, lpUnits[0] )
		pOwner.receiveGoody( pCity.plot(), eMapGoody, lpUnits[0] )

	# Remove default units
	for unit in defaultUnits :
		unit.kill( False, -1 )


def cedeCities( lpCities, pJoinPlayer, bGiveMap ) :
	# type: ( Sequence[CyCity], CyPlayer, bool ) -> Sequence[CyCity]
	""" Give cities to pJoinPlayer as part of a rebel deal. """

	if len( lpCities ) == 0 :
		return []

	pOwner = gc.getPlayer( lpCities[0].getOwner() )
	pJoinPlayer.AI_changeAttitudeExtra( pOwner.getID(), 2 )

	# Announce handover
	RevMessages.announceCitiesCeded( pOwner, lpCities, pJoinPlayer )

	pJoinTeam = gc.getTeam( pJoinPlayer.getTeam() )
	iNumOwnerCities = pOwner.getNumCities()
	lpNewCities = []
	for pCity in lpCities :
		# Move units out of city
		if pJoinTeam.isAtWar( pOwner.getTeam() ) and iNumOwnerCities > len( lpCities ) :
			if LOG_DEBUG : log( "Moving owner's units" )
			RevUtils.clearOutCity( pCity, pOwner, pJoinPlayer )

		if LOG_DEBUG : log( "Acquiring %s" % (pCity.getName()) )

		pCity = _cedeCityToRebels( pCity, pJoinPlayer )
		_initCededCityUnits( pCity, pOwner, bGiveMap )
		lpNewCities.append( pCity )

	return lpNewCities