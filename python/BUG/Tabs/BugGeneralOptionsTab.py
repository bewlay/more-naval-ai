## BugGeneralOptionsTab
##
## Tab for the BUG General Options (Main and City Screens).
##
## Copyright (c) 2007-2008 The BUG Mod.
##
## Author: EmperorFool

from CvPythonExtensions import *
import BugOptionsTab
import Buffy

gc = CyGlobalContext()
game = gc.getGame()

class BugGeneralOptionsTab(BugOptionsTab.BugOptionsTab):
	"BUG General Options Screen Tab"
	
	def __init__(self, screen):
		BugOptionsTab.BugOptionsTab.__init__(self, "General", "General")

	def create(self, screen):
		tab = self.createTab(screen)
		panel = self.createMainPanel(screen)
		column = self.addOneColumnLayout(screen, panel)
		
		left, center, right = self.addThreeColumnLayout(screen, column, "Top", True)
		
		self.createGreatPersonGeneralPanel(screen, left)
		self.addSpacer(screen, left, "General1")
		self.createTechSplashPanel(screen, left)
		self.addSpacer(screen, left, "General2")
		self.createAutoSavePanel(screen, left)
		
		self.createActionsPanel(screen, center)
		self.addSpacer(screen, center, "General3")
		self.createMiscellaneousPanel(screen, center)
		
		self.createInfoPanePanel(screen, right)
		self.addSpacer(screen, right, "General4")
		self.createLeaderheadPanel(screen, right)
		if Buffy.isEnabled():
			self.addSpacer(screen, right, "General5")
			self.createBuffyPanel(screen, right)
		
	def createGreatPersonGeneralPanel(self, screen, panel):
		self.addLabel(screen, panel, "ProgressBars", "Progress Bars:")
		self.addCheckboxTextDropdown(screen, panel, panel, "MainInterface__GPBar", "MainInterface__GPBar_Types")
		#self.addCheckbox(screen, panel, "MainInterface__GPBar")
		#self.addTextDropdown(screen, panel, panel, "MainInterface__GPBar_Types", True)
		if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ADVANCED_TACTICS): ## Suppress display of Great General bar
			self.addCheckbox(screen, panel, "MainInterface__Combat_Counter")
		
	def createLeaderheadPanel(self, screen, panel):
		self.addLabel(screen, panel, "Leaderheads", "Leaderheads:")
		self.addCheckbox(screen, panel, "MiscHover__LeaderheadHiddenAttitude")
		# LFGR_TODO: Both these options are apparently not actually implemented anywhere.
		# self.addCheckbox(screen, panel, "MiscHover__LeaderheadWorstEnemy")
		# self.addCheckbox(screen, panel, "MiscHover__LeaderheadDefensivePacts")
		
	def createAutoSavePanel(self, screen, panel):
		self.addLabel(screen, panel, "AutoSave", "AutoSave:")
		# LFGR_TODO: Doesn't seem to work. In any case, there is AutoSave_INITIAL
		self.addCheckbox(screen, panel, "AutoSave__CreateStartSave")
		self.addCheckbox(screen, panel, "AutoSave__CreateEndSave")
		self.addCheckbox(screen, panel, "AutoSave__CreateExitSave")
		self.addCheckbox(screen, panel, "AutoSave__UsePlayerName")
		
	def createActionsPanel(self, screen, panel):
		if(not game.isNetworkMultiPlayer()):
			self.addLabel(screen, panel, "Actions", "Actions:")
			# LFGR_TODO: Does not work for unknown reasons. Check CvGame::selectionListMove and CvUnit::getDeclareWarMove
			# self.addCheckbox(screen, panel, "Actions__AskDeclareWarUnits")
			# The following two are not used anywhere. LFGR_TODO: Implement? Check other mods?
			# self.addCheckbox(screen, panel, "Actions__SentryHealing")
			# self.addCheckbox(screen, panel, "Actions__SentryHealingOnlyNeutral", True)
			self.addCheckbox(screen, panel, "Actions__PreChopForests")
			self.addCheckbox(screen, panel, "Actions__PreChopImprovements")
		
	def createTechSplashPanel(self, screen, panel):
		self.addLabel(screen, panel, "TechWindow", "Tech Splash Screen:")
		self.addTextDropdown(screen, panel, panel, "TechWindow__ViewType", True)
		self.addCheckbox(screen, panel, "TechWindow__CivilopediaText")
	
	def createBuffyPanel(self, screen, panel):
		self.addLabel(screen, panel, "BUFFY", "BUFFY:")
		self.addCheckbox(screen, panel, "BUFFY__WarningsDawnOfMan")
		self.addCheckbox(screen, panel, "BUFFY__WarningsSettings")
	
	def createInfoPanePanel(self, screen, panel):
		self.addLabel(screen, panel, "InfoPane", "Unit/Stack Info:")
		self.addCheckbox(screen, panel, "MainInterface__UnitCombatIcons")
		self.addCheckbox(screen, panel, "MainInterface__UnitMovementPointsFraction")
		self.addCheckbox(screen, panel, "MainInterface__StackMovementPoints")
		self.addCheckbox(screen, panel, "MainInterface__StackPromotions")
		left, center, right = self.addThreeColumnLayout(screen, panel, "StackPromotionColors")
		self.addCheckbox(screen, left, "MainInterface__StackPromotionCounts", True)
		self.addColorDropdown(screen, center, right, "MainInterface__StackPromotionColor", False)
		self.addColorDropdown(screen, center, right, "MainInterface__StackPromotionColorAll", False)
		
	def createMiscellaneousPanel(self, screen, panel):
		self.addLabel(screen, panel, "Misc", "Misc:")
		self.addCheckbox(screen, panel, "MainInterface__GoldRateWarning")
		self.addCheckbox(screen, panel, "MainInterface__MinMax_Commerce")
		self.addCheckbox(screen, panel, "MainInterface__ProgressBarsTickMarks")
		self.addTextDropdown(screen, panel, panel, "MainInterface__BuildIconSize", True)
		self.addCheckbox(screen, panel, "MainInterface__CityArrows")
		# lfgr 06/2019: Option to hide minimap ownership overlay on water
		self.addCheckbox(screen, panel, "MainInterface__MinimapWaterOverlay")
