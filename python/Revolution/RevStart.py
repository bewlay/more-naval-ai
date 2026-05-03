# Code for starting revolutions
# lfgr 04/2026: Started moving stuff from Revolution.py here

from CvPythonExtensions import *

from PyHelpers import PyPlayer

import CvUtil

import RevData
import RevDefs
import RevUtils


gc = CyGlobalContext()
game = gc.getGame()


LOG_DEBUG = True and RevUtils.LOG_DEBUG

def debug( msg ) :
	if LOG_DEBUG :
		CvUtil.pyPrint( "  RevStart - " + msg )



# lfgr 04/2026: Taken from Revolution.checkForRevolution, but removed almost all specific modifiers
def getInstigationOddsIn1000( city ) :
	""" The odds a city may instigate a revolution. Does not check whether the city is in principle able to instigate. """
	
	# By default, this is revidx / 20, so 5% for a city just over the threshold
	iModPercent = gc.getDefineINT( "REV_CHANCE_MOD_PERCENT" )
	if iModPercent == 0 :
		iModPercent = 100
	return min( 500, city.getRevolutionIndex() * iModPercent / 2000 )


def isRevolutionPeaceful( pInstigatorCity, lpRevCities ) :
	# type: (CyCity, List[CyCity]) -> bool
	""" Whether the revolution with the given cities should be peaceful. """
	iInstRevIdx = pInstigatorCity.getRevolutionIndex()
	iInstLocalIdx = pInstigatorCity.getLocalRevIndex()

	iViolentThresholdMod = 100
	for pCivic in PyPlayer( pInstigatorCity.getOwner() ).iterCivicInfos() :
		iViolentThresholdMod += pCivic.getRevViolentMod()

	iAlwaysViolentThreshold = RevUtils.alwaysViolentThreshold * iViolentThresholdMod / 100
	iMaybeViolentThreshold = RevUtils.alwaysViolentThreshold * (iViolentThresholdMod - 20) / 100
	
	debug( "Determine whether revolution will be violent")
	if iInstRevIdx > iAlwaysViolentThreshold :
		# Situation really bad
		debug( "  Violent, above always violent threshold" )
		return False
	elif pInstigatorCity.getNumRevolts( pInstigatorCity.getOwner() ) == 0 :
		# First revolution is always peaceful
		debug( "  Peaceful, first revolution" )
		return True
	else :
		# LFGR_TODO: This seems innocent, but I removed most other local-index-dependent things.
		if iInstLocalIdx > RevDefs.badLocalThreshold :
			# Situation deteriorating rapidly
			debug( "  Violent due to rapidly deteriorating situation" )
			return False

		if len( lpRevCities ) == 1 :
			# Single city is not violent except for the above reasons
			debug( "  Peaceful, single city" )
			return True

		# Randomize violence
		if iInstRevIdx > iMaybeViolentThreshold :
			iOdds = 100 * (iInstRevIdx - iMaybeViolentThreshold) / ( iAlwaysViolentThreshold - iMaybeViolentThreshold)
			debug( "  Odds for violence are %d" % iOdds )
			if game.getSorenRandNum( 100, 'Rev' ) < iOdds :
				return False

		return True


def findJoinRevolutionPlayer( pInstigator ) :
	# type: (CyCity) -> Optional[CyPlayer]
	""" Can cities revolting in pAgainstTeam join an existing revolt? """
	pAgainstPlayer = gc.getPlayer( pInstigator.getOwner() )
	pAgainstTeam = gc.getTeam( pAgainstPlayer.getTeam() )
	
	if pAgainstPlayer.getNumCities() > 1 and RevData.getCityVal( pInstigator, 'RevolutionTurn' ) is not None :
		# There has been a revolution in the instigator city before
		iRevPlayer = RevData.getRevolutionPlayer( pInstigator )
		if iRevPlayer >= 0 :
			pRevPlayer = gc.getPlayer( iRevPlayer )
	
			# Is the revolution actually active and against the right team?
			if pRevPlayer.isAlive() and pRevPlayer.isRebel() \
					and gc.getTeam( pRevPlayer.getTeam() ).isRebelAgainst( pAgainstTeam.getID() ) \
					and pAgainstTeam.isAtWar( pRevPlayer.getTeam() ) :
		
				# Cannot join human rebel
				# TODO: Create popup offering peace to human rebel player in this circumstance?
				if pRevPlayer.isHuman() :
					return None
		
				# Cannot join if host is vassal of a human
				if pAgainstTeam.isAVassal() :
					for teamID in range( 0, gc.getMAX_CIV_TEAMS() ) :
						if pAgainstTeam.isVassal( teamID ) and gc.getTeam( teamID ).isHuman() :
							return None
		
				# Cannot join if rebel is vassal of a human
				if gc.getTeam( pRevPlayer.getTeam() ).isAVassal() :
					for teamID in range( 0, gc.getMAX_CIV_TEAMS() ) :
						if gc.getTeam( pRevPlayer.getTeam() ).isVassal( teamID ) and gc.getTeam( teamID ).isHuman() :
							return None
				return pRevPlayer
	
	return None


# Taken from Revolution.py, removed some logging
def findCloseCities( pInstigator, lpRevCities, iCloseRadius ) :
	# type: (CyCity, Sequence[CyCity], int) -> List[CyCity]
	""" Returns all cities with distance at most iCloseRadius to instigator, or distance at most 0.8*iCloseRadius to
		one of these cities. """
	
	lpIndCities = []
	for pCity in lpRevCities :
		# Add only cities near instigator in first pass
		iCityDist = plotDistance( pCity.getX(), pCity.getY(), pInstigator.getX(), pInstigator.getY() )
		if iCityDist <= iCloseRadius :
			lpIndCities.append( pCity )

	for pCity in lpRevCities :
		if pCity not in lpIndCities :
			# Add cities a little further away that are also near another rebelling city
			iCityDist = plotDistance( pCity.getX(), pCity.getY(), pInstigator.getX(), pInstigator.getY() )
			if iCityDist <= 2 * iCloseRadius :
				for iCity in lpIndCities :
					iCityDist = min( iCityDist, plotDistance( pCity.getX(), pCity.getY(), iCity.getX(), iCity.getY() ) )

				if iCityDist <= iCloseRadius * 8 / 10 :
					lpIndCities.append( pCity )
	return lpIndCities

def checkForJoinDemand( pInstigator, lpRevCities, iMinOtherCulture ) :
	# type: (CyCity, Sequence[CyCity], int) -> Tuple[CyPlayer, List[CyCity]]
	"""
	Identify a player that some of the rebelling cities may ask to join. That player may or may not be alive.
	Only keep cities where the joined player has higher culture then owner and the given iMinOtherCulture.
	
	Returned player is None if no suitable player has been found.
	"""
	debug( "Checking whether cities want to join a player" )
	
	eOwner = pInstigator.getOwner()
	pOwner = gc.getPlayer( eOwner )
	iInstigatorOwnerCulture = pInstigator.plot().calculateCulturePercent( pInstigator.getOwner() )
	pBestJoinPlayer = None
	iBestScore = 0
	lpBestCityList = []
	for ePlayer in xrange( gc.getMAX_CIV_PLAYERS() ) :
		pPlayer = gc.getPlayer( ePlayer )
		if not pPlayer.isEverAlive() :
			continue
		if pPlayer.getTeam() == pOwner.getTeam() :
			continue # Cannot join player from own team
		iInstigatorCulture = pInstigator.plot().calculateCulturePercent( ePlayer )
		# CvUtil.pyPrint( " DEBUG: %s: %d >= max(%d, %d)?" % (pPlayer.getName(), iInstigatorCulture, iInstigatorOwnerCulture,iMinOtherCulture))
		if iInstigatorCulture < iInstigatorOwnerCulture :
			continue # Need more culture than owner in instigator
		if iInstigatorCulture < iMinOtherCulture :
			continue # Need to pass culture threshold in instigator
		
		iTotalCultureTimesPop = iInstigatorCulture * pInstigator.getPopulation()
		lpCities = [pInstigator]
		for pCity in lpRevCities :
			if pCity.getID() != pInstigator.getID() :
				iCulture = pCity.plot().calculateCulturePercent( ePlayer )
				if iCulture > max( iMinOtherCulture, pCity.plot().calculateCulturePercent( eOwner ) ) :
					iTotalCultureTimesPop += iCulture * pInstigator.getPopulation()
					lpCities.append( pCity )

		debug( "  Could join player %s, culture*pop score: %d" % ( pPlayer.getName(), iTotalCultureTimesPop ) )
		if pBestJoinPlayer is None or iTotalCultureTimesPop > iBestScore :
			pBestJoinPlayer = pPlayer
			iBestScore = iTotalCultureTimesPop
			lpBestCityList = lpCities
		# lfgr: This slightly biases lower-idx players, but whatever; the scores are likely to be all different.
	
	return pBestJoinPlayer, lpBestCityList
