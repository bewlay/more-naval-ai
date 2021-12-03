"""
FfHUI 05/2020 lfgr
Configurable UI functionality for Fall from Heaven.
"""
import FfHDefines
from CvPythonExtensions import *
import BugCore
import CustomFunctions
from PyHelpers import getText


cf = CustomFunctions.CustomFunctions()
gc = CyGlobalContext()
ffhUIOpt = BugCore.game.FfHUI
ffhDefines = FfHDefines.getInstance()


def onSetPlayerAlive( argsList ) :
	ePlayer, bAlive = argsList
	if not bAlive and gc.getGame().getGameTurnYear() >= 5 and not CyGame().getWBMapScript() :
		# Player died outside of scenario; show default defeated popup
		if ffhUIOpt.isShowLeaderDefeatPopup() :
			# LFGR_TODO: Add tag in LeaderHeadInfos
			iLeader = gc.getPlayer( ePlayer) .getLeaderType()
			if iLeader == gc.getInfoTypeForString('LEADER_ALEXIS'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_CALABIM",()),'art/interface/popups/Alexis.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_AMELANCHIER'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_LJOSALFAR",()),'art/interface/popups/Amelanchier.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_ARENDEL'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_LJOSALFAR",()),'art/interface/popups/Arendel.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_ARTURUS'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_KHAZAD",()),'art/interface/popups/Arturus.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_AURIC'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_ILLIANS",()),'art/interface/popups/Auric.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_BASIUM'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_MERCURIANS",()),'art/interface/popups/Basium.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_BEERI'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_LUCHUIRP",()),'art/interface/popups/Beeri.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_CAPRIA'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_BANNOR",()),'art/interface/popups/Capria.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_CARDITH'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_KURIOTATES",()),'art/interface/popups/Cardith.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_CASSIEL'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_GRIGORI",()),'art/interface/popups/Cassiel.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_CHARADON'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_DOVIELLO",()),'art/interface/popups/Charadon.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_DAIN'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_AMURITES",()),'art/interface/popups/Dain.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_DECIUS'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_DECIUS",()),'art/interface/popups/Decius.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_EINION'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_ELOHIM",()),'art/interface/popups/Einion.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_ETHNE'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_ELOHIM",()),'art/interface/popups/Ethne.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_FAERYL'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_SVARTALFAR",()),'art/interface/popups/Faeryl.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_FALAMAR'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_LANUN",()),'art/interface/popups/Falamar.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_FLAUROS'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_CALABIM",()),'art/interface/popups/Flauros.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_GARRIM'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_LUCHUIRP",()),'art/interface/popups/Garrim.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_HANNAH'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_HANNAH",()),'art/interface/popups/Hannah.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_HYBOREM'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_INFERNAL",()),'art/interface/popups/Hyborem.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_JONAS'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_CLAN_OF_EMBERS",()),'art/interface/popups/Jonus.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_KANDROS'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_KHAZAD",()),'art/interface/popups/Kandros.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_KEELYN'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_KEELYN",()),'art/interface/popups/Keelyn.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_MAHALA'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_DOVIELLO",()),'art/interface/popups/Mahala.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_SANDALPHON'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_SIDAR",()),'art/interface/popups/Sandalphon.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_OS-GABELLA'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_SHEAIM",()),'art/interface/popups/Os-Gabella.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_PERPENTACH'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_BALSERAPHS",()),'art/interface/popups/Perpentach.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_RHOANNA'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_HIPPUS",()),'art/interface/popups/Rhoanna.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_SABATHIEL'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_BANNOR",()),'art/interface/popups/Sabathiel.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_SHEELBA'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_CLAN_OF_EMBERS",()),'art/interface/popups/Sheelba.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_TASUNKE'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_HIPPUS",()),'art/interface/popups/Tasunke.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_TEBRYN'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_SHEAIM",()),'art/interface/popups/Tebryn.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_THESSA'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_LJOSALFAR",()),'art/interface/popups/Thessa.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_VALLEDIA'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_AMURITES",()),'art/interface/popups/Valledia.dds')
			elif iLeader == gc.getInfoTypeForString('LEADER_VARN'):
				cf.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DEFEATED_MALAKIM",()),'art/interface/popups/Varn.dds')


def cyclePlotHelpForwards( argsList = None ) :
	gc.changePlotHelpCycleIdx( 1 )

def cyclePlotHelpBackwards( argsList = None ) :
	gc.changePlotHelpCycleIdx( -1 )


def getPlayerGoldTooltip( eWidgetType, iData1, iData2, bOption ) :
	pPlayer = gc.getPlayer( CyGame().getActivePlayer() )
	if pPlayer.getCivilizationType() != gc.getInfoTypeForString( "CIVILIZATION_KHAZAD" ) :
		return u""

	if pPlayer.getNumCities() == 0 :
		return u""
	
	szHelp = u""
	iGoldPerCity = pPlayer.getGold() // pPlayer.getNumCities()
	szHelp += getText( "TXT_KEY_GOLD_PER_CITY", iGoldPerCity )

	nextVaultAndGold = ffhDefines.getNextKhazadVaultWithMinGold( pPlayer )
	if nextVaultAndGold is not None :
		eNextVault, iMinGold = nextVaultAndGold
		szHelp += u"\n" + getText( "TXT_KEY_NEXT_GOLD", iMinGold, gc.getBuildingInfo( eNextVault ).getTextKey() )
	
	eVault = ffhDefines.getKhazadVault( pPlayer )
	szHelp += u"\n" + CyGameTextMgr().getBuildingHelp( eVault, False, False, False, None )
	
	return szHelp
	
	