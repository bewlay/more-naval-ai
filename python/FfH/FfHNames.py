# FfHNames 11/2021 by lfgr

from CvPythonExtensions import *
import Roman

# globals
gc = CyGlobalContext()


def onSetPlayerAlive( args ) :
	ePlayer, bNewValue = args
	print( "SET_PLAYER_ALIVE" )

	if bNewValue :
		setNewLeaderName( ePlayer )


def setNewLeaderName( ePlayer ) :
	""" Rename the given player, if necessary/desired """
	pPlayer = gc.getPlayer( ePlayer ) # type: CyPlayer
	szName = pPlayer.getName()

	# Add roman numerals in case there are duplicates
	hszNames = set( gc.getPlayer( eLoopPlayer ).getName() for eLoopPlayer in range( gc.getMAX_CIV_PLAYERS() )
			if eLoopPlayer != ePlayer and gc.getPlayer( eLoopPlayer ).isAlive() )
	szNewName = szName
	iCount = 1
	while szNewName in hszNames :
		iCount += 1
		szNewName = szName + u" " + unicode( Roman.toRoman( iCount ) )
	pPlayer.setName( szNewName )