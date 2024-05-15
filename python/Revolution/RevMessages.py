""" Utilities for revolution-related message. """
from CvPythonExtensions import *

from PyHelpers import CIV_PLAYERS, PyPlayer, getText

import CvUtil
import TextUtils


gc = CyGlobalContext()
# RevOpt = BugCore.game.Revolution


# lfgr: Extracted from Revolution.py
def announceRevolutionaries( eMotherPlayer, pRevPlayer, iX, iY, bJoinRev ) :
	# type: ( int, CyPlayer, int, int, bool ) -> None
	""" Announce revolution to all players """
	for ePlayer in CIV_PLAYERS :
		if gc.getPlayer( ePlayer ) is None :
			continue
		# LFGR_TODO: Better text handling
		if gc.getPlayer( ePlayer ).canContact( eMotherPlayer ) or ePlayer == eMotherPlayer :
			eColor = 7
			if pRevPlayer.isBarbarian() :
				if ePlayer == eMotherPlayer :
					mess = "<color=255,0,0,255>" + getText( "TXT_KEY_REV_MESS_YOU_BARB" )
				else :
					mess = "<color=255,0,0,255>" + getText( "TXT_KEY_REV_MESS_VIOLENT" ) + ' ' + PyPlayer( eMotherPlayer ).getCivilizationName() + '!!!'
					mess += "  " + getText("TXT_KEY_REV_MESS_BARB" )
			else :
				if ePlayer == eMotherPlayer :
					mess = "<color=255,0,0,255>"
					if bJoinRev :
						mess += getText("TXT_KEY_REV_MESS_JOIN",pRevPlayer.getNameKey(), pRevPlayer.getCivilizationDescription(0) )
					else :
						mess += getText("TXT_KEY_REV_MESS_YOU_RISEN", pRevPlayer.getNameKey(), pRevPlayer.getCivilizationDescription(0) )
				else :
					mess = ""

					if ePlayer == pRevPlayer.getID() :
						mess += "<color=0,255,0,255>"
						eColor = 8
					else :
						mess += "<color=255,0,0,255>"
						eColor = 7

					mess += getText( "TXT_KEY_REV_MESS_VIOLENT" ) + ' ' + PyPlayer( eMotherPlayer ).getCivilizationName() + '!!!'
					if bJoinRev :
						mess += "  " + getText( "TXT_KEY_REV_MESS_JOIN",pRevPlayer.getName(), pRevPlayer.getCivilizationDescription(0) )
					else :
						mess += "  " + getText("TXT_KEY_REV_MESS_RISEN", pRevPlayer.getCivilizationDescription(0), pRevPlayer.getNameKey() )

			if ePlayer == eMotherPlayer :
				CyInterface().addMessage(ePlayer, true, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess, "AS2D_CITY_REVOLT", InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, CyArtFileMgr().getInterfaceArtInfo("INTERFACE_RESISTANCE").getPath(), ColorTypes(eColor), iX, iY, True, True)
			elif ePlayer == pRevPlayer.getID() :
				CyInterface().addMessage(ePlayer, true, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess,  "AS2D_DECLAREWAR", InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, None, ColorTypes(eColor), iX, iY, False, False)
			else :
				CyInterface().addMessage(ePlayer, false, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess,  "AS2D_DECLAREWAR", InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, None, ColorTypes(eColor), -1, -1, False, False)

# lfgr: Extracted from Revolution.py
def announceReinforcements( pCity, pRevPlayer ) :
	# type: (CyCity, CyPlayer) -> None
	pRevTeam = gc.getTeam( pRevPlayer.getTeam() )

	for ePlayer in CIV_PLAYERS :
		msg = None
		bImportant = True
		bPositive = False
		if pCity.getOwner() == ePlayer :
			msg = getText( "TXT_KEY_REV_MESS_REINFORCEMENTS",pRevPlayer.getNameKey(), pCity.getName() )
		elif pRevTeam.isAtWar( gc.getPlayer( ePlayer ).getTeam() ) and pRevPlayer.canContact( ePlayer ) :
			msg = getText( "TXT_KEY_REV_MESS_REINFORCEMENTS",pRevPlayer.getNameKey(), pCity.getName() )
			bImportant = False
		elif pRevPlayer.getID() == ePlayer :
			msg = getText( "TXT_KEY_REV_MESS_YOUR_REINFORCEMENTS",pRevPlayer.getCivilizationDescription(0), pCity.getName() )
			bPositive = True

		if msg :
			CyInterface().addMessage( ePlayer, bImportant, gc.getDefineINT("EVENT_MESSAGE_TIME"), msg,
					bImportant and "AS2D_CITY_REVOLT" or None, InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
					bImportant and CyArtFileMgr().getInterfaceArtInfo("INTERFACE_RESISTANCE").getPath() or None,
					bPositive and ColorTypes(8) or ColorTypes(7), pCity.getX(), pCity.getY(), bImportant, bImportant )

# lfgr: Extracted from Revolution.py
def announceCitiesCeded( pPlayer, cityList, pJoinPlayer ) :
	# type: (CyPlayer, Sequence[CyCity], CyPlayer) -> None

	szCitiesStr = TextUtils.getCityTextList(cityList)

	for iPlayer in range(0,gc.getMAX_CIV_PLAYERS()) :
		if gc.getPlayer( iPlayer ).canContact( pPlayer.getID() ) or iPlayer == pPlayer.getID() :

			eColor = gc.getInfoTypeForString( "COLOR_HIGHLIGHT_TEXT" )
			szSourcePlayerName = pPlayer.getName()
			szJoinPlayerName = pJoinPlayer.getName()

			if iPlayer == pJoinPlayer.getID() :
				eColor = gc.getInfoTypeForString( "COLOR_POSITIVE_TEXT" )
				szJoinPlayerName = getText("TXT_KEY_REV_YOUR_CIV")
			elif iPlayer == pPlayer.getID() :
				eColor = gc.getInfoTypeForString( "COLOR_NEGATIVE_TEXT" )
				szSourcePlayerName = str(getText("TXT_KEY_REV_YOU"))


			mess = getText("TXT_KEY_REV_MESS_CEDE") % (szSourcePlayerName, szCitiesStr, szJoinPlayerName)

			if iPlayer == pPlayer.getID() :
				CyInterface().addMessage(iPlayer, false, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess, "AS2D_CITY_REVOLT", InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, CyArtFileMgr().getInterfaceArtInfo("INTERFACE_RESISTANCE").getPath(), ColorTypes(eColor), cityList[0].getX(), cityList[0].getY(), True, True)
			else :
				CyInterface().addMessage(iPlayer, false, gc.getDefineINT("EVENT_MESSAGE_TIME"), mess, None, InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, None, ColorTypes(eColor), -1, -1, False, False)


def announceRevolutionProcessed( pPlayer, lpCities, bTermsAccepted, revType ) :
	# type: ( CyPlayer, Sequence[CyCity], bool, str ) -> None
	try :
		cityStr = TextUtils.getCityTextList( lpCities )
		cityStr2 = getText( "TXT_KEY_REV_CITY" )
		if len( lpCities ) > 1 :
			cityStr2 = getText( "TXT_KEY_REV_CITIES" )
	except :
		CvUtil.pyPrint( "  RevMessages - ERROR! with city strings" )
		return

	mess = getText( "TXT_KEY_REV_MESS_REPORT" ) % ( cityStr2, cityStr, pPlayer.getCivilizationShortDescription( 0 ) )
	if bTermsAccepted :
		mess += " " + getText( "TXT_KEY_REV_MESS_REPORT_EASED" )
	else :
		mess += " " + getText( "TXT_KEY_REV_MESS_REPORT_INCREASED" )

	for iPlayer in range( 0, gc.getMAX_CIV_PLAYERS() ) :
		if iPlayer != pPlayer.getID() and gc.getPlayer( iPlayer ).isAlive() :
			if revType != "independence" or not bTermsAccepted :
				try :
					iTeam = gc.getPlayer( iPlayer ).getTeam()
					if lpCities[0].getEspionageVisibility( iTeam ) :
						CyInterface().addMessage( iPlayer, false, gc.getDefineINT( "EVENT_MESSAGE_TIME" ), mess, None,
												  InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT, None,
												  gc.getInfoTypeForString( "COLOR_HIGHLIGHT_TEXT" ), -1, -1, False,
												  False )
				except :
					CvUtil.pyPrint( "  RevMessages - ERROR! C++ call failed, end of processRevolution, player %d" % (iPlayer) )