"""
Callback functions for vote system
"""

from CvPythonExtensions import *
from PyHelpers import PyGame


gc = CyGlobalContext()


### Main callbacks

def votePrereq( argsList ) :
	print( "votePrereq()" )
	eVote, = argsList
	return eval( gc.getVoteInfo( eVote ).getPyRequirement() )

def voteAI( argsList ) :
	ePlayer, eVote, eVotePlayer, iVoteCityId, eVoteOtherPlayer, = argsList
	return eval( gc.getVoteInfo( eVote ).getPyAI() )

def voteResult( argsList ) :
	eVote, = argsList
	eval( gc.getVoteInfo( eVote ).getPyResult() )


# Fund dissidents

def canDoFundDissidents() :
	eOvercouncil = gc.getInfoTypeForString( 'DIPLOVOTE_OVERCOUNCIL' )
	for ePlayer, pyPlayer in PyGame().iterAliveCivPlayers() :
		if pyPlayer.isFullMember( eOvercouncil ) :
			return True
	return False
	

def doFundDissidents() :
	eOvercouncil = gc.getInfoTypeForString('DIPLOVOTE_OVERCOUNCIL')
	for ePlayer, pyPlayer in PyGame().iterAliveCivPlayers() :
		if pyPlayer.isFullMember( eOvercouncil ):
			for pyCity in pyPlayer.iterCities() :
				if CyGame().getSorenRandNum(100, "Fund Dissidents") < 50:
					pyCity.changeHurryAngerTimer(1 + CyGame().getSorenRandNum(3, "Fund Dissidents"))


# Setup gambling ring

def aiGamblingRing( ePlayer ) :
	pPlayer = gc.getPlayer( ePlayer )
	if pPlayer.getAlignment() != gc.getInfoTypeForString( "ALIGNMENT_EVIL" ) :
		return PlayerVoteTypes.PLAYER_VOTE_NO
	
	return PlayerVoteTypes.NO_PLAYER_VOTE


# Slave trade

def aiSlaveTrade( ePlayer ) :
	pPlayer = gc.getPlayer( ePlayer )
	if pPlayer.getAlignment() != gc.getInfoTypeForString( "ALIGNMENT_EVIL" ) :
		return PlayerVoteTypes.PLAYER_VOTE_NO
	
	return PlayerVoteTypes.NO_PLAYER_VOTE


# Setup smuggling ring

def aiSmugglingRing( ePlayer ) :
	pPlayer = gc.getPlayer( ePlayer )
	if 4 * pPlayer.countNumCoastalCities() <= pPlayer.getNumCities() :
		return PlayerVoteTypes.PLAYER_VOTE_NO
	elif 3 * pPlayer.countNumCoastalCities() <= pPlayer.getNumCities() :
		return PlayerVoteTypes.PLAYER_VOTE_ABSTAIN
	else :
		return PlayerVoteTypes.PLAYER_VOTE_YES
	
