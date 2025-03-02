## RevolutionDCM Options Tab
##
## Tab to configure all RevolutionDCM options.
##
## Copyright (c) 2007-2008 The BUG Mod.
##
## Author: Glider1

from CvPythonExtensions import *
import BugOptionsTab
gc = CyGlobalContext()
localText = CyTranslator()

class RevDCMOptionsTab(BugOptionsTab.BugOptionsTab):

	def __init__(self, screen):
		BugOptionsTab.BugOptionsTab.__init__(self, "RevDCM", "RevDCM")

	def create(self, screen):
		game = gc.getGame()
		networkGame =  game.isGameMultiPlayer()
		tab = self.createTab(screen)
		panel = self.createMainPanel(screen)
		column = self.addOneColumnLayout(screen, panel)
		left, right = self.addTwoColumnLayout(screen, column, "Options", False)
	
		if not networkGame:
			#Config
			if(game.isDebugMode()):
				self.addLabel(screen, left, "Revolution__RevConfig", "RevConfig:")
				col1, col2 = self.addMultiColumnLayout(screen, right, 2, "Misc Settings")
				self.addCheckbox(screen, col1, "Revolution__ActivePopup")
				self.addCheckbox(screen, col2, "Revolution__RevConfigDebugMode")

				screen.attachHSeparator(left, left + "SepRevConfig1")
				screen.attachHSeparator(right, right + "SepRevConfig2")


			#Barbarian Civ
			#Standard Options
#			if (not game.isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIAN_CIV)):
			if 1 > 2: #leaving this section here for modders
				self.addLabel(screen, left, "Revolution__BarbarianCiv", localText.getText("TXT_KEY_REVDCMTAB_BARBCIV_OPTIONS", ()))
				col1, col2, col3 = self.addMultiColumnLayout(screen, right, 3, "Misc Settings")
				self.addIntDropdown(screen, col1, col2, "Revolution__MinPopulation")
				if(game.isDebugMode()):
					self.addCheckbox(screen, col3, "Revolution__OfferControl")
				self.addLabel(screen, left, "Revolution__BarbarianCiv", localText.getText("TXT_KEY_REVDCMTAB_NEWWORLD_OPTIONS", ()))
				col1, col2, col3, col4, col5 = self.addMultiColumnLayout(screen, right, 5, "NewWorld Settings")
				self.addIntDropdown(screen, col1, col2, "Revolution__NewWorldPolicy")
				self.addIntDropdown(screen, col3, col4, "Revolution__NewWorldErasBehind")
				self.addCheckbox(screen, col5, "Revolution__FierceNatives")
				self.addLabel(screen, left, "Revolution__BarbarianCiv", localText.getText("TXT_KEY_REVDCMTAB_BARBCIV_STRENGTH_OPTIONS", ()))
				col1, col2, col3, col4, col5, col6 = self.addMultiColumnLayout(screen, right, 6, "Strength Settings")
				self.addFloatDropdown(screen, col1, col2, "Revolution__BarbTechFrac")
				self.addFloatDropdown(screen, col3, col4, "Revolution__MilitaryStrength")
				self.addIntDropdown(screen, col5, col6, "Revolution__NewWorldBonuses")

				screen.attachHSeparator(left, left + "SepStandardBarbCiv1")
				screen.attachHSeparator(right, right + "SepStandardBarbCiv2")

				#Debug Options
				if(game.isDebugMode()):
					self.addLabel(screen, left, "Revolution__BarbarianCiv", "Debug Options:")
					col1, col2, col3, col4, col5, col6 = self.addMultiColumnLayout(screen, right, 6, "Debug Settings")
					self.addCheckbox(screen, col1, "Revolution__BarbCivDebugMode")
					self.addCheckbox(screen, col2, "Revolution__AnnounceBarbSettle")
					self.addCheckbox(screen, col3, "Revolution__UsePopup")
					self.addCheckbox(screen, col4, "Revolution__OnlyNotifyNearbyPlayers")
					self.addCheckbox(screen, col5, "Revolution__BlockPopupInAuto")
					self.addCheckbox(screen, col6, "Revolution__CancelAutoForOffer")
					self.addLabel(screen, left, "Revolution__BarbarianCiv", "Settling Options:")
					col1, col2, col3, col4, col5, col6 = self.addMultiColumnLayout(screen, right, 6, "Settling Options")
					self.addIntDropdown(screen, col1, col2, "Revolution__MinorHalfLife")
					self.addIntDropdown(screen, col3, col4, "Revolution__BarbCivMaxCivs")
					self.addFloatDropdown(screen, col5, col6, "Revolution__FormMinorModifier")
					self.addLabel(screen, left, "Revolution__BarbarianCiv", "Contact Settings:")
					col1, col2, col3, col4, col5, col6 = self.addMultiColumnLayout(screen, right, 6, "Contact Settings")
					self.addIntDropdown(screen, col1, col2, "Revolution__MinContacts")
					self.addIntDropdown(screen, col3, col4, "Revolution__MinFullContacts")
					self.addIntDropdown(screen, col5, col6, "Revolution__WarCloseDist")
					self.addLabel(screen, left, "Revolution__BarbarianCiv", "Style Settings:")
					col1, col2, col3, col4= self.addMultiColumnLayout(screen, right, 4, "Style Settings")
					self.addFloatDropdown(screen, col1, col2, "Revolution__BaseMilitaryOdds")
					self.addIntDropdown(screen, col3, col4, "Revolution__BuilderBonusTechs")
					self.addLabel(screen, left, "Revolution__BarbarianCiv", "Misc Options:")
					col1, col2, col3 = self.addMultiColumnLayout(screen, right, 3, "Misc Options")
					self.addCheckbox(screen, col1, "Revolution__BarbCivsByStyle")
					self.addIntDropdown(screen, col2, col3, "Revolution__MilitaryWindow")

					screen.attachHSeparator(left, left + "SepDebugBarbCiv1")
					screen.attachHSeparator(right, right + "SepDebugBarbCiv2")


			#Revolutions
			if( game.isOption(GameOptionTypes.GAMEOPTION_REVOLUTIONS) ):

				#screen.attachHSeparator(left, left + "SepStandardRevolution1")
				#screen.attachHSeparator(right, right + "SepStandardRevolution2")

			#Debug Options
#				if(game.isDebugMode()):
				if (1 < 2):
					self.addLabel(screen, left, "Revolution__Revolution", "Debug Options:")
					col1, col2, col3, col4 = self.addMultiColumnLayout(screen, right, 4, "Debug Settings")
					self.addCheckbox(screen, col1, "Revolution__RevDebugMode")
					self.addCheckbox(screen, col2, "Revolution__ShowDebugMessages")
					self.addCheckbox(screen, col3, "Revolution__CenterPopups")
					self.addCheckbox(screen, col4, "Revolution__ShowRevIndexInPopup")
					self.addLabel(screen, left, "Revolution__Revolution", "Civ Counts:")
					col1, col2, col3, col4 = self.addMultiColumnLayout(screen, right, 4, "Civ Counts")
					self.addIntDropdown(screen, col1, col2, "Revolution__MaxScoreLines")
					self.addIntDropdown(screen, col3, col4, "Revolution__RevMaxCivs")
					self.addLabel(screen, left, "Revolution__Revolution", "Style Types:")
					col1, col2 = self.addMultiColumnLayout(screen, right, 2, "Style Types")
					self.addCheckbox(screen, col2, "Revolution__ArtStyleTypes")
					self.addLabel(screen, left, "Revolution__Revolution", "User Options:")
					col1, col2, col3, col4, col5, col6 = self.addMultiColumnLayout(screen, right, 6, "User Options")
					self.addCheckbox(screen, col1, "Revolution__OfferDefectToRevs")
					self.addCheckbox(screen, col2, "Revolution__AllowAssimilation")
					self.addCheckbox(screen, col3, "Revolution__AllowSmallBarbRevs")
					self.addCheckbox(screen, col4, "Revolution__AllowBreakVassal")
					self.addCheckbox(screen, col5, "Revolution__EndWarsOnDeath")
					self.addCheckbox(screen, col6, "Revolution__AllowStateReligionToJoin")
					self.addLabel(screen, left, "Revolution__Revolution", "Revolution Types:")
					col1, col2, col3, col4, col5 = self.addMultiColumnLayout(screen, right, 5, "Revolution Types")
					self.addCheckbox(screen, col1, "Revolution__CulturalRevolution")
					self.addCheckbox(screen, col2, "Revolution__ReligiousRevolution")
					self.addCheckbox(screen, col3, "Revolution__CivicRevolution")
					self.addCheckbox(screen, col4, "Revolution__LeaderRevolution")
					self.addCheckbox(screen, col5, "Revolution__HumanLeaderRevolution")
					self.addLabel(screen, left, "Revolution__Revolution", "Index Modifiers:")
					col1, col2, col3, col4, col5, col6, col7, col8 = self.addMultiColumnLayout(screen, right, 8, "Index Modifiers")
					self.addFloatDropdown(screen, col1, col2, "Revolution__IndexModifier")
					self.addFloatDropdown(screen, col3, col4, "Revolution__IndexOffset")
					self.addFloatDropdown(screen, col5, col6, "Revolution__HumanIndexModifier")
					self.addFloatDropdown(screen, col7, col8, "Revolution__HumanIndexOffset")
					self.addLabel(screen, left, "Revolution__Revolution", "Empire Modifiers:")
					col1, col2, col3, col4, col5, col6, col7, col8 = self.addMultiColumnLayout(screen, right, 8, "Empire Modifiers")
					self.addFloatDropdown(screen, col1, col2, "Revolution__CultureRateModifier")
					self.addFloatDropdown(screen, col3, col4, "Revolution__CivSizeModifier")
					self.addFloatDropdown(screen, col5, col6, "Revolution__CityLostModifier")
					self.addFloatDropdown(screen, col7, col8, "Revolution__CityAcquiredModifier")
					self.addLabel(screen, left, "Revolution__Revolution", "Mixed Modifiers:")
					col1, col2, col3, col4 = self.addMultiColumnLayout(screen, right, 4, "Mixed Modifiers")
					self.addFloatDropdown(screen, col1, col2, "Revolution__WarWearinessMod")
					self.addFloatDropdown(screen, col3, col4, "Revolution__ReligionModifier")
					self.addLabel(screen, left, "Revolution__Revolution", "Local Modifiers:")
					col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12 = self.addMultiColumnLayout(screen, right, 12, "Local Modifiers")
					self.addFloatDropdown(screen, col1, col2, "Revolution__ColonyModifier")
					self.addFloatDropdown(screen, col3, col4, "Revolution__DistanceToCapitalModifier")
					self.addFloatDropdown(screen, col5, col6, "Revolution__HappinessModifier")
					self.addFloatDropdown(screen, col7, col8, "Revolution__NationalityModifier")
					self.addFloatDropdown(screen, col9, col10, "Revolution__GarrisonModifier")
					self.addFloatDropdown(screen, col11, col12, "Revolution__RevCultureModifier")
					self.addLabel(screen, left, "Revolution__Revolution", "Rebellion Odds:")
					col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12 = self.addMultiColumnLayout(screen, right, 12, "Rebellion Odds")
					self.addFloatDropdown(screen, col1, col2, "Revolution__ChanceModifier")
					self.addIntDropdown(screen, col3, col4, "Revolution__CivicsOdds")
					self.addIntDropdown(screen, col5, col6, "Revolution__ReligionOdds")
					self.addIntDropdown(screen, col7, col8, "Revolution__LeaderOdds")
					self.addIntDropdown(screen, col9, col10, "Revolution__CrusadeOdds")
					self.addIntDropdown(screen, col11, col12, "Revolution__IndependenceOdds")
					self.addLabel(screen, left, "Revolution__Revolution", "Rebellion Turns:")
					col1, col2, col3, col4, col5, col6 = self.addMultiColumnLayout(screen, right, 6, "Rebellion Turns")
					self.addIntDropdown(screen, col1, col2, "Revolution__TurnsBetweenRevs")
					self.addIntDropdown(screen, col3, col4, "Revolution__BaseReinforcementTurns")
					self.addIntDropdown(screen, col5, col6, "Revolution__MinReinforcementTurns")
					self.addLabel(screen, left, "Revolution__Revolution", "Turn Delays:")
					col1, col2, col3, col4, col5, col6, col7, col8 = self.addMultiColumnLayout(screen, right, 8, "Turn Delays")
					self.addIntDropdown(screen, col1, col2, "Revolution__AcquiredTurns")
					self.addIntDropdown(screen, col3, col4, "Revolution__AcceptedTurns")
					self.addIntDropdown(screen, col5, col6, "Revolution__BuyoffTurns")
					self.addIntDropdown(screen, col7, col8, "Revolution__DeniedTurns")
					self.addLabel(screen, left, "Revolution__Revolution", "Warn Settings:")
					col1, col2, col3, col4 = self.addMultiColumnLayout(screen, right, 4, "Warn Settings")
					self.addFloatDropdown(screen, col1, col2, "Revolution__HumanWarnFrac")
					self.addIntDropdown(screen, col3, col4, "Revolution__WarnTurns")
					self.addLabel(screen, left, "Revolution__Revolution", "Thresholds:")
					col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = self.addMultiColumnLayout(screen, right, 10, "Thresholds")
					self.addIntDropdown(screen, col1, col2, "Revolution__MaxNationality")
					self.addIntDropdown(screen, col3, col4, "Revolution__InstigateRevolutionThreshold")
					self.addIntDropdown(screen, col5, col6, "Revolution__AlwaysViolentThreshold")
					self.addIntDropdown(screen, col7, col8, "Revolution__BadLocalThreshold")
					self.addIntDropdown(screen, col9, col10, "Revolution__CloseRadius")
					self.addLabel(screen, left, "Revolution__Revolution", "Rebellion Tweaks:")
					col1, col2, col3, col4, col5, col6 = self.addMultiColumnLayout(screen, right, 6, "Rebellion Tweaks")
					self.addFloatDropdown(screen, col1, col2, "Revolution__JoinRevolutionFrac")
					self.addFloatDropdown(screen, col3, col4, "Revolution__StrengthModifier")
					self.addFloatDropdown(screen, col5, col6, "Revolution__ReinforcementModifier")

					screen.attachHSeparator(left, left + "SepDebugRevolution1")
					screen.attachHSeparator(right, right + "SepDebugRevolution2")


			#AIAutoplay
			# if(game.isDebugMode()):
			if True :
				self.addLabel(screen, left, "Revolution__AIAutoPlay", "AIAutoPlay Settings:")
				col1, col2, col3, col4 = self.addMultiColumnLayout(screen, right, 4, "AIAutoPlay")
				self.addCheckbox(screen, col1, "Revolution__AIAutoPlayEnable")
				self.addCheckbox(screen, col2, "Revolution__BlockPopups")
				self.addCheckbox(screen, col3, "Revolution__SaveAllDeaths")
				self.addCheckbox(screen, col4, "Revolution__Refortify")
				
				self.addLabel(screen, left, "Revolution__AIAutoPlay_Stop", "Stop AIAutoplay:")
				self.addCheckbox(screen, col1, "Revolution__StopOnVictory")
				self.addCheckbox(screen, col2, "Revolution__StopOnRevolution")

				screen.attachHSeparator(left, left + "SepAIAutoPlay1")
				screen.attachHSeparator(right, right + "SepAIAutoPlay2")


			#ChangePlayer
			if(game.isDebugMode()):
				self.addLabel(screen, left, "Revolution__ChangePlayer", "ChangePlayer Settings:")
				col1, col2 = self.addMultiColumnLayout(screen, right, 2, "ChangePlayer")
				self.addCheckbox(screen, col1, "Revolution__ChangePlayerEnable")
				self.addCheckbox(screen, col2, "Revolution__ChangePlayerDebugMode")

				screen.attachHSeparator(left, left + "SepChangePlayer1")
				screen.attachHSeparator(right, right + "SepChangePlayer2")


			#TechDiffusion
			if game.isOption(GameOptionTypes.GAMEOPTION_ADVANCED_TACTICS):

				#screen.attachHSeparator(left, left + "SepStandardTechDiffusion1")
				#screen.attachHSeparator(right, right + "SepStandardTechDiffusion2")

				#Debug Settings
				if(game.isDebugMode()):
					self.addLabel(screen, left, "Revolution__TechDiffusion", "TechDiffusion Settings:")
					col1, col2, col3, col4, col5, col6, col7, col8, col9 = self.addMultiColumnLayout(screen, right, 9, "TechDiffusion")
					self.addCheckbox(screen, col1, "Revolution__TechDifDebugMode")
					self.addIntDropdown(screen, col2, col3, "Revolution__MinTechsBehind")
					self.addIntDropdown(screen, col4, col5, "Revolution__FullEffectTechsBehind")
					self.addIntDropdown(screen, col6, col7, "Revolution__BonusTechsBehind")
					self.addFloatDropdown(screen, col8, col9, "Revolution__DiffusionMod")

					screen.attachHSeparator(left, left + "SepDebugTechDiffusion1")
					screen.attachHSeparator(right, right + "SepDebugTechDiffusion2")
					

			#General options
			self.addLabel(screen, left, "RevDCM__RevDCMControl", localText.getText("TXT_KEY_REVDCMTAB_RESET_DEFAULTS", ()))
			col1, col2 = self.addMultiColumnLayout(screen, right, 2, "General_Events")
			self.addCheckbox(screen, col1, "RevDCM__RevDCMReset")

			screen.attachHSeparator(left, left + "SepGeneral1")
			screen.attachHSeparator(right, right + "SepGeneral2")
			
			
		else:
			self.addLabel(screen, left, "RevDCM_network_game", localText.getText("TXT_KEY_MULTIPLAYER_GAME_DETECTED", ()))
			self.addLabel(screen, right, "RevDCM_network_game1", localText.getText("TXT_KEY_MULTIPLAYER_GAME_DETECTED_DESCRIPTION", ()))
	
