# RevolutionInit.py
#
# by jdog5000
# Version 2.2

# This file should be imported into CvCustomEventManager and the
# __init__ function then called from the event handler initilization
# spot using:
#
# RevolutionInit.RevolutionInit( self, configFileName )
#
# where configFileName is nominally "Revolution.ini".

from CvPythonExtensions import *
import CvUtil
import PyHelpers
import Popup as PyPopup
import CvModName
import BugPath
# --------- Revolution mod -------------
import RevDefs
import RevEvents
#import BarbarianCiv
import AIAutoPlay
import ChangePlayer
import Revolution
#import Tester
import TechDiffusion
#import StartAsMinors
import DynamicCivNames
import RevInstances
# --------- RevolutionDCM mod ----------
import BugCore
import RevDCM
import BugOptions

gc = CyGlobalContext()
PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo
game = CyGame()
localText = CyTranslator()
RevDCMOpt = BugCore.game.RevDCM
RevOpt = BugCore.game.Revolution
ScoreOpt = BugCore.game.Scores

class RevolutionInit :

	def __init__( self, customEM ) :
		
		CvUtil.pyPrint(localText.getText("TXT_KEY_REV_MOD_INITIALIZING",()))

		self.EventKeyDown = 6
		self.customEM = customEM
		self.RevOpt = RevOpt
		if( game.isOption(GameOptionTypes.GAMEOPTION_REVOLUTIONS) ):
			self.bShowActivePopup = RevOpt.isActivePopup()
		else:
			self.bShowActivePopup = False
		
		self.revComponentsText = ""

		#RevolutionDCM
		self.titleFormat = "<font=3b><color=250,170,0,255>"
		self.sectionFormat = "<font=3><color=200,200,0,255>"
		self.optionFormat = "<font=2><color=0,180,0,255>"
		self.noneOptionFormat = "<font=2><color=0,0,255,255>"
		self.helpTextTitle = "<font=3><color=255,255,0,255>"
		self.helpTextFormat = "<font=2><color=255,255,255,255>"

		customEM.addEventHandler( "kbdEvent", self.onKbdEvent )
		customEM.addEventHandler( 'GameStart', self.onGameStart )
		customEM.addEventHandler( 'OnLoad', self.onGameLoad )
		#customEM.addEventHandler( 'Init', self.onInit )
		
		# Determine if game is already running and Python has just been reloaded
		if( game.isFinalInitialized() ) :
			#print "Game initialized!"
			self.onGameLoad( None, bShowPopup = False )



	def onKbdEvent(self, argsList ):
		'keypress handler'
		eventType,key,mx,my,px,py = argsList

		if ( eventType == RevDefs.EventKeyDown ):
			theKey=int(key)

			# For debug or trial only
			if( theKey == int(InputTypes.KB_Q) and self.customEM.bShift and self.customEM.bCtrl ) :
				self.showActivePopup()

	def onInit( self, argsList ) :
		print "Init fired"
	
	def onGameStart( self, argsList ) :
		
		print "Gaming starting now"
		
		self.onGameLoad( None )

	def onGameLoad( self, argsList, bForceReinit = False, bShowPopup = True ) :
	   # Remove any running mod components
		bDoUnInit = (bForceReinit or RevInstances.bIsInitialized)
		bDoInit = (bDoUnInit or not RevInstances.bIsInitialized)
		
		if( bDoUnInit ) :
			print "PY:  Uninitializing Revolution Mod components"
			
			if( not RevInstances.BarbarianCivInst == None ) :
				RevInstances.BarbarianCivInst.removeEventHandlers()
				RevInstances.BarbarianCivInst = None
			if( not RevInstances.RevolutionInst == None ) :
				RevEvents.removeEventHandlers()
				RevInstances.RevolutionInst.removeEventHandlers()
				RevInstances.RevolutionInst = None
			if( not RevInstances.DynamicCivNamesInst == None ) :
				RevInstances.DynamicCivNamesInst.removeEventHandlers()
				RevInstances.DynamicCivNamesInst = None
			if( not RevInstances.TechDiffusionInst == None ) :
				RevInstances.TechDiffusionInst.removeEventHandlers()
				RevInstances.TechDiffusionInst = None
			if( not RevInstances.AIAutoPlayInst == None ) :
				RevInstances.AIAutoPlayInst.removeEventHandlers()
				RevInstances.AIAutoPlayInst = None
#			if( not RevInstances.TesterInst == None ) :
#				RevInstances.TesterInst.removeEventHandlers()
#				RevInstances.TesterInst = None
			if( not RevInstances.ChangePlayerInst == None ) :
				RevInstances.ChangePlayerInst.removeEventHandlers()
				RevInstances.ChangePlayerInst = None
			
			RevInstances.bIsInitialized = False
		
		# Initialize mod components
		if( bDoInit ) :
			print "PY:  Initializing Revolution Mod components"
			RevInstances.bIsInitialized = True
		
		# This component mainly contains test and debug routines
#		if( bDoInit ) : RevInstances.TesterInst = Tester.Tester( self.customEM, self.RevOpt )

		### RevolutionDCM start
		bAIAutoPlay = RevOpt.isAIAutoPlayEnable()
		if( bAIAutoPlay ) :
			if( bDoInit ) :
				RevInstances.AIAutoPlayInst = AIAutoPlay.AIAutoPlay(self.customEM, self.RevOpt)
#		if( not game.isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIAN_CIV) ):#self.config.getboolean("BarbarianCiv", "Enable", True) ) :
#		if( game.isOption(GameOptionTypes.GAMEOPTION_REVOLUTIONS) ):#self.config.getboolean("BarbarianCiv", "Enable", True) ) :
#			if( bDoInit ) :
#				RevInstances.BarbarianCivInst = BarbarianCiv.BarbarianCiv(self.customEM, self.RevOpt)
		bChangePlayer = RevOpt.isChangePlayerEnable()
		if( bChangePlayer ) :
			if( bDoInit ) :
				RevInstances.ChangePlayerInst = ChangePlayer.ChangePlayer(self.customEM, self.RevOpt)
		if( game.isOption(GameOptionTypes.GAMEOPTION_REVOLUTIONS) ):#self.config.getboolean("Revolution", "Enable", True) ) :
			if( bDoInit ) : 
				# RevEvents needs to service beginPlayerTurn events before Revolution
				RevEvents.init( self.customEM, self.RevOpt )
				RevInstances.RevolutionInst = Revolution.Revolution(self.customEM, self.RevOpt)
#		if( not game.isOption(GameOptionTypes.GAMEOPTION_NO_TECH_DIFFUSION) ):#self.config.getboolean("TechDiffusion", "Enable", True) ) :
		if( game.isOption(GameOptionTypes.GAMEOPTION_ADVANCED_TACTICS) ):
			if( bDoInit ) :
				RevInstances.TechDiffusionInst = TechDiffusion.TechDiffusion(self.customEM, self.RevOpt)
#		if( game.isOption(GameOptionTypes.GAMEOPTION_START_AS_MINORS) ):
#			if( bDoInit ) :
#				StartAsMinors.init( self.customEM, self.RevOpt )
	# lfgr enabled
		if( ScoreOpt.isDYNAMIC_CIV_NAMES() ):#self.config.getboolean("DynamicCivNames", "Enable", True) ) :
			if( bDoInit ) :
				print "About to init DynamicCivNames"
				RevInstances.DynamicCivNamesInst = DynamicCivNames.DynamicCivNames(self.customEM, self.RevOpt)
		### RevolutionDCM end
		
		if( bShowPopup and self.bShowActivePopup ) :
			self.showActivePopup()
		
		if( bDoInit ) :
			CyInterface().setDirty( InterfaceDirtyBits.MiscButtons_DIRTY_BIT, True )
			CyInterface().setDirty( InterfaceDirtyBits.CityScreen_DIRTY_BIT, True )
			CyInterface().setDirty( InterfaceDirtyBits.MiscButtons_DIRTY_BIT, True )
	
	def showActivePopup( self ) :
	
		revMaxCivs = RevOpt.getRevMaxCivs()
		barbMaxCivs = RevOpt.getBarbCivMaxCivs()
		revDefaultNumPlayers = gc.getWorldInfo(gc.getMap().getWorldSize()).getDefaultPlayers()

		bodStr = self.getRevComponentsText()
		bodStr += localText.getText("TXT_KEY_REV_MOD_MAX_CIVS_IN_DLL",( gc.getMAX_CIV_PLAYERS(), ))
		if( revMaxCivs > 0 and revMaxCivs < gc.getMAX_CIV_PLAYERS() ) :
			bodStr += localText.getText("TXT_KEY_REV_MOD_REVS_WILL_STOP_AT",( revMaxCivs, ))
		if( barbMaxCivs > 0 and barbMaxCivs < gc.getMAX_CIV_PLAYERS() ) :
			bodStr += localText.getText("TXT_KEY_REV_MOD_BARB_CIV_WILL_STOP_AT",( barbMaxCivs, ))
		#RevolutionDCM - save screen space
		#bodStr += localText.getText("TXT_KEY_REV_MOD_TURNS_IN_GAME",( game.getMaxTurns(), ))
		bodStr += localText.getText("TXT_KEY_REV_MOD_DEFAULT_NUM_PLAYERS",( revDefaultNumPlayers, ))

		popup = PyPopup.PyPopup( )
		popup.setBodyString( bodStr )
		### RevolutionDCM start
		popup.setSize(220, 640) #220 is maximum for 1024x768 so as not to block the hints display and 640 so that help text is not covered.
		### RevolutionDCM end
		popup.launch()
		
	#RevolutionDCM
	def getRevComponentsText(self):
		revComponentsInfo = localText.getText("TXT_KEY_REV_MOD_RUNNING_INFO",())
		revComponentsText = self.titleFormat + "<font=4b>R" + self.titleFormat + revComponentsInfo + "\n"
		revNoneText = localText.getText("TXT_KEY_REV_MOD_INITIALIZING_NONE",())

		### RevolutionDCM start
		revComponentsText += self.sectionFormat + localText.getText("TXT_KEY_REV_MOD_INITIALIZING_INIT",())
		anyOption = false
#		if( not game.isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIAN_CIV) ):
#		if( game.isOption(GameOptionTypes.GAMEOPTION_REVOLUTIONS) ):
#			revComponentsText += self.optionFormat + localText.getText("TXT_KEY_REV_MOD_INITIALIZING_BARBARIAN_CIV",())
#			anyOption = true
		if( game.isOption(GameOptionTypes.GAMEOPTION_BARBARIAN_WORLD) ):
			revComponentsText += self.optionFormat + localText.getText("TXT_KEY_REV_MOD_INITIALIZING_BARBARIAN_WORLD",())
			anyOption = true  
		if( game.isOption(GameOptionTypes.GAMEOPTION_REVOLUTIONS) ):
			revComponentsText += self.optionFormat + localText.getText("TXT_KEY_REV_MOD_INITIALIZING_REVOLUTION",())
			anyOption = true
#		if( not game.isOption(GameOptionTypes.GAMEOPTION_NO_TECH_DIFFUSION) ):
#			revComponentsText += self.optionFormat + localText.getText("TXT_KEY_REV_MOD_INITIALIZING_TECH_DIFFUSION",())
#			anyOption = true
#		if( game.isOption(GameOptionTypes.GAMEOPTION_START_AS_MINORS) ):
#			revComponentsText += self.optionFormat + localText.getText("TXT_KEY_REV_MOD_INITIALIZING_START_AS_MINORS",())
#			anyOption = true
		if ScoreOpt.isDYNAMIC_CIV_NAMES():
			revComponentsText += self.optionFormat + localText.getText("TXT_KEY_REV_MOD_INITIALIZING_DYNAMIC_CIV_NAMES",())
			anyOption = true
		if not anyOption:
			revComponentsText += self.noneOptionFormat + revNoneText
 

		
		revHelpText = self.helpTextTitle
		revHelpText += localText.getText("TXT_KEY_REV_MOD_INITIALIZING_GAME_SHORTCUTS",())
		revHelpText += self.helpTextFormat + localText.getText("TXT_KEY_REV_MOD_INITIALIZING_BUG_OPTIONS_SHORTCUT",())
		revHelpText += self.helpTextFormat + localText.getText("TXT_KEY_REV_MOD_INITIALIZING_INIT_POPUP",())
		revHelpText += self.helpTextFormat + localText.getText("TXT_KEY_REV_MOD_INITIALIZING_AI_AUTOPLAY",())
		if (game.isDebugMode()):
			revHelpText += self.helpTextFormat + "\nCTRL-SHIFT-L = New leader!"
			revHelpText += self.helpTextFormat + "\nCTRL-SHIFT-P = New Civ!"
		self.revComponentsText = revComponentsText + revHelpText
		return self.revComponentsText
		### RevolutionDCM end		


