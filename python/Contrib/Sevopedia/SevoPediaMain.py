# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005

#
# Sevopedia 2.3
#   sevotastic.blogspot.com
#   sevotastic@yahoo.com
#
# additional work by Gaurav, Progor, Ket, Vovan, Fitchn, LunarMongoose, EmperorFool, lfgr
# see ReadMe for details
#

from CvPythonExtensions import *
import string

import CvUtil
import ScreenInput
import SevoScreenEnums

import CvPediaScreen
import SevoPediaTech
import SevoPediaUnit
import SevoPediaBuilding
import SevoPediaPromotion
import SevoPediaUnitChart
import SevoPediaBonus
import SevoPediaTerrain
import SevoPediaFeature
import SevoPediaImprovement
import SevoPediaCivic
import SevoPediaCivilization
import SevoPediaLeader
import SevoPediaTrait
import SevoPediaSpecialist
import SevoPediaHistory
import SevoPediaProject
import SevoPediaReligion
#import SevoPediaCorporation
#import CvPediaSpell
import SevoPediaIndex
##--------	BUGFfH: Added by Denev 2009/08/12
import SevoPediaEquipment
import SevoPediaSpell
import random
##--------	BUGFfH: End Add

import UnitUpgradesGraph
##--------	BUGFfH: Deleted by Denev 2009/09/11
#import TraitUtil
##--------	BUGFfH: End Delete
import BugCore
import BugUtil

import InterfaceUtils # lfgr 10/2019

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

AdvisorOpt = BugCore.game.Advisors

##--------	BUGFfH: Deleted by Denev 2009/09/11
#g_TraitUtilInitDone = False
##--------	BUGFfH: End Delete

class SevoPediaMain(CvPediaScreen.CvPediaScreen, InterfaceUtils.GenericAdvisorScreen):

	def __init__(self):
		self.PEDIA_MAIN_SCREEN	= "PediaMainScreen"
		self.INTERFACE_ART_INFO	= "SCREEN_BG_OPAQUE"
		
		self.TAB_TOC   = "Contents"
		self.TAB_INDEX = "Index"

		self.WIDGET_ID		= "PediaMainWidget"
		self.BACKGROUND_ID	= "PediaMainBackground"
		self.TOP_PANEL_ID	= "PediaMainTopPanel"
		self.BOT_PANEL_ID	= "PediaMainBottomPanel"
		self.HEAD_ID		= "PediaMainHeader"
		self.TOC_ID			= "PediaMainContents"
		self.INDEX_ID		= "PediaMainIndex"
		self.BACK_ID		= "PediaMainBack"
		self.NEXT_ID		= "PediaMainForward"
		self.EXIT_ID		= "PediaMainExit"
		self.CATEGORY_LIST_ID	= "PediaMainCategoryList"
		self.ITEM_LIST_ID	= "PediaMainItemList"
		self.UPGRADES_GRAPH_ID	= "PediaMainUpgradesGraph"

		self.tab = None
		self.iActivePlayer = -1
##--------	BUGFfH: Added by Denev 2009/09/12
		self.iActiveCiv = CivilizationTypes.NO_CIVILIZATION
##--------	BUGFfH: End Add
		self.nWidgetCount = 0

		self.categoryList = []
		self.categoryGraphics = []
		self.iCategory = -1
		self.iItem = -1
		self.iItemIndex = -1
		self.pediaHistory = []
		self.pediaFuture = []

		self.mapListGenerators = {
			SevoScreenEnums.PEDIA_TECHS		: self.placeTechs,
			SevoScreenEnums.PEDIA_UNITS		: self.placeUnits,
			SevoScreenEnums.PEDIA_UNIT_UPGRADES	: self.placeUnitUpgrades,
			SevoScreenEnums.PEDIA_UNIT_CATEGORIES	: self.placeUnitCategories,
			SevoScreenEnums.PEDIA_PROMOTIONS		: self.placePromotions,
			SevoScreenEnums.PEDIA_SPHERES			: self.placeSpheres,
			SevoScreenEnums.PEDIA_PROMOTION_TREE	: self.placePromotionTree,
			SevoScreenEnums.PEDIA_EFFECTS		: self.placeEffects,
			SevoScreenEnums.PEDIA_EQUIPMENTS	: self.placeEquipments,
			SevoScreenEnums.PEDIA_RACES			: self.placeRaces,
			SevoScreenEnums.PEDIA_BUILDINGS		: self.placeBuildings,
			SevoScreenEnums.PEDIA_NATIONAL_WONDERS	: self.placeNationalWonders,
			SevoScreenEnums.PEDIA_GREAT_WONDERS	: self.placeGreatWonders,
			SevoScreenEnums.PEDIA_PROJECTS		: self.placeProjects,
			SevoScreenEnums.PEDIA_SPECIALISTS		: self.placeSpecialists,
			SevoScreenEnums.PEDIA_TERRAINS		: self.placeTerrains,
			SevoScreenEnums.PEDIA_FEATURES		: self.placeFeatures,
##--------	BUGFfH: Added by Denev 2009/08/12
			SevoScreenEnums.PEDIA_UNIQUE_FEATURES	: self.placeUniqueFeatures,
##--------	BUGFfH: End Add
			SevoScreenEnums.PEDIA_BONUSES		: self.placeBonuses,
			SevoScreenEnums.PEDIA_MANA_NODES	: self.placeManaNodes,
			SevoScreenEnums.PEDIA_IMPROVEMENTS	: self.placeImprovements,
			SevoScreenEnums.PEDIA_CIVS		: self.placeCivs,
			SevoScreenEnums.PEDIA_LEADERS		: self.placeLeaders,
		# MINOR_LEADERS_PEDIA 08/2013 lfgr
			SevoScreenEnums.PEDIA_MINOR_LEADERS	: self.placeMinorLeaders,
		# MINOR_LEADERS_PEDIA end
			SevoScreenEnums.PEDIA_TRAITS		: self.placeTraits,
			SevoScreenEnums.PEDIA_CIVICS		: self.placeCivics,
			SevoScreenEnums.PEDIA_RELIGIONS		: self.placeReligions,
#			SevoScreenEnums.PEDIA_CORPORATIONS	: self.placeCorporations,
			SevoScreenEnums.PEDIA_SPELLS	: self.placeSpells,
##--------	BUGFfH: Added by Denev 2009/10/05
			SevoScreenEnums.PEDIA_ABILITIES		: self.placeAbilities,
##--------	BUGFfH: End Add
			SevoScreenEnums.PEDIA_CONCEPTS		: self.placeConcepts,
			SevoScreenEnums.PEDIA_BTS_CONCEPTS	: self.placeBTSConcepts,
			SevoScreenEnums.PEDIA_HINTS		: self.placeHints,
			SevoScreenEnums.PEDIA_SHORTCUTS  	: self.placeShortcuts,
			SevoScreenEnums.PEDIA_STRATEGY  	: self.placeStrategy,
			}

		self.pediaBuilding	= SevoPediaBuilding.SevoPediaBuilding(self)
		self.pediaLeader	= SevoPediaLeader.SevoPediaLeader(self)
		self.pediaIndex     = SevoPediaIndex.SevoPediaIndex(self)
##--------	BUGFfH: Added by Denev 2009/08/12
		self.pediaUnit		= SevoPediaUnit.SevoPediaUnit(self)
		self.pediaTech      = SevoPediaTech.SevoPediaTech(self)
		self.pediaPromotion	= SevoPediaPromotion.SevoPediaPromotion(self)
		self.pediaProject	= SevoPediaProject.SevoPediaProject(self)
		self.pediaBonus		= SevoPediaBonus.SevoPediaBonus(self)		
		self.pediaImprovement	= SevoPediaImprovement.SevoPediaImprovement(self)
##--------	BUGFfH: End Add
##--------	BUGFfH: Added by Denev 2009/10/05
		self.pediaSpell		= SevoPediaSpell.SevoPediaSpell(self)
##--------	BUGFfH: End Add

		self.mapScreenFunctions = {
			SevoScreenEnums.PEDIA_TECHS		: SevoPediaTech.SevoPediaTech(self),
			SevoScreenEnums.PEDIA_UNITS		: SevoPediaUnit.SevoPediaUnit(self),
			SevoScreenEnums.PEDIA_UNIT_CATEGORIES	: SevoPediaUnitChart.SevoPediaUnitChart(self),
			SevoScreenEnums.PEDIA_PROMOTIONS		: SevoPediaPromotion.SevoPediaPromotion(self),
			SevoScreenEnums.PEDIA_SPHERES		: self.pediaPromotion,
			SevoScreenEnums.PEDIA_EFFECTS		: self.pediaPromotion,
			SevoScreenEnums.PEDIA_EQUIPMENTS	: SevoPediaEquipment.SevoPediaEquipment(self),
			SevoScreenEnums.PEDIA_RACES			: self.pediaPromotion,
			SevoScreenEnums.PEDIA_BUILDINGS		: self.pediaBuilding,
			SevoScreenEnums.PEDIA_NATIONAL_WONDERS	: SevoPediaBuilding.SevoPediaBuilding(self),
			SevoScreenEnums.PEDIA_GREAT_WONDERS	: SevoPediaBuilding.SevoPediaBuilding(self),
			SevoScreenEnums.PEDIA_PROJECTS		: SevoPediaProject.SevoPediaProject(self),
			SevoScreenEnums.PEDIA_SPECIALISTS		: SevoPediaSpecialist.SevoPediaSpecialist(self),
			SevoScreenEnums.PEDIA_TERRAINS		: SevoPediaTerrain.SevoPediaTerrain(self),
			SevoScreenEnums.PEDIA_FEATURES		: SevoPediaFeature.SevoPediaFeature(self),
##--------	BUGFfH: Added by Denev 2009/08/12
			SevoScreenEnums.PEDIA_UNIQUE_FEATURES	: SevoPediaImprovement.SevoPediaImprovement(self),
##--------	BUGFfH: End Add
			SevoScreenEnums.PEDIA_BONUSES		: SevoPediaBonus.SevoPediaBonus(self),
			SevoScreenEnums.PEDIA_MANA_NODES	: SevoPediaBonus.SevoPediaBonus(self),			
			SevoScreenEnums.PEDIA_IMPROVEMENTS	: SevoPediaImprovement.SevoPediaImprovement(self),
			SevoScreenEnums.PEDIA_CIVS		: SevoPediaCivilization.SevoPediaCivilization(self),
			SevoScreenEnums.PEDIA_LEADERS		: self.pediaLeader,
		# MINOR_LEADERS_PEDIA 08/2013 lfgr
			SevoScreenEnums.PEDIA_MINOR_LEADERS	: self.pediaLeader,
		# MINOR_LEADERS_PEDIA end
			SevoScreenEnums.PEDIA_TRAITS		: SevoPediaTrait.SevoPediaTrait(self),
			SevoScreenEnums.PEDIA_CIVICS		: SevoPediaCivic.SevoPediaCivic(self),
			SevoScreenEnums.PEDIA_RELIGIONS		: SevoPediaReligion.SevoPediaReligion(self),
#			SevoScreenEnums.PEDIA_CORPORATIONS	: SevoPediaCorporation.SevoPediaCorporation(self),
			SevoScreenEnums.PEDIA_SPELLS		: SevoPediaSpell.SevoPediaSpell(self),
##--------	BUGFfH: Added by Denev 2009/10/05
			SevoScreenEnums.PEDIA_ABILITIES		: SevoPediaSpell.SevoPediaSpell(self),
##--------	BUGFfH: End Add
			SevoScreenEnums.PEDIA_CONCEPTS		: SevoPediaHistory.SevoPediaHistory(self),
			SevoScreenEnums.PEDIA_BTS_CONCEPTS	: SevoPediaHistory.SevoPediaHistory(self),
			SevoScreenEnums.PEDIA_SHORTCUTS  	: SevoPediaHistory.SevoPediaHistory(self),
			SevoScreenEnums.PEDIA_STRATEGY  	: SevoPediaHistory.SevoPediaHistory(self),
			}



	def getScreen(self):
		return CyGInterfaceScreen(self.PEDIA_MAIN_SCREEN, SevoScreenEnums.PEDIA_MAIN)

	def createScreen(self, screen):
		if screen.isActive(): return
		BugUtil.debug("Creating screen")
		self.iCategory = -1
		self.tab = None
		self.setPediaCommonWidgets()

	def pediaShow(self):
##--------	BUGFfH: Deleted by Denev 2009/09/11
		"""
		global g_TraitUtilInitDone
		if not g_TraitUtilInitDone:
			TraitUtil.init()
			g_TraitUtilInitDone = True
		"""
##--------	BUGFfH: End Delete
		self.iActivePlayer = gc.getGame().getActivePlayer()
##--------	BUGFfH: Added by Denev 2009/09/12
		self.iActiveCiv = gc.getGame().getActiveCivilizationType()
##--------	BUGFfH: End Add
		self.iCategory = -1
		if (not self.pediaHistory):
			self.pediaHistory.append((SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_TECHS))
		current = self.pediaHistory.pop()
		self.pediaFuture = []
		self.pediaHistory = []
		self.pediaJump(current[0], current[1], False, True)



	def pediaJump(self, iCategory, iItem, bRemoveFwdList, bIsLink):
		bAddToHistory = False
		if (not self.pediaHistory):
			bAddToHistory = True
		elif (iCategory != SevoScreenEnums.PEDIA_MAIN or iItem == SevoScreenEnums.PEDIA_UNIT_UPGRADES or iItem == SevoScreenEnums.PEDIA_PROMOTION_TREE or iItem == SevoScreenEnums.PEDIA_HINTS):
			prev = self.pediaHistory[0]
			if (prev[0] != iCategory or prev[1] != iItem):
				bAddToHistory = True
		if (bAddToHistory):
			self.pediaHistory.append((iCategory, iItem))
		if (bRemoveFwdList):
			self.pediaFuture = []

		screen = self.getScreen()
		if not screen.isActive():
			self.createScreen(screen)

		if (iCategory == SevoScreenEnums.PEDIA_MAIN):
			BugUtil.debug("Main link %d" % iItem)
			self.showContents(bIsLink, iItem)
			screen.setSelectedListBoxStringGFC(self.CATEGORY_LIST_ID, iItem - (SevoScreenEnums.PEDIA_MAIN + 1))
			#self.iCategory = iItem
			return

		if (iCategory == SevoScreenEnums.PEDIA_BUILDINGS):
			iCategory += self.pediaBuilding.getBuildingType(iItem)
		elif (iCategory == SevoScreenEnums.PEDIA_PROMOTIONS):
			iPromotionType = self.pediaPromotion.getPromotionType(iItem)
			if iPromotionType == SevoScreenEnums.TYPE_EFFECT:
				iCategory = SevoScreenEnums.PEDIA_EFFECTS
			elif iPromotionType == SevoScreenEnums.TYPE_SPHERE:
				iCategory = SevoScreenEnums.PEDIA_SPHERES
			elif iPromotionType == SevoScreenEnums.TYPE_EQUIPMENT:
				iCategory = SevoScreenEnums.PEDIA_EQUIPMENTS
			elif iPromotionType == SevoScreenEnums.TYPE_GEAR:
				iCategory = SevoScreenEnums.PEDIA_GEAR				
			elif iPromotionType == SevoScreenEnums.TYPE_RACE:
				iCategory = SevoScreenEnums.PEDIA_RACES
		elif (iCategory == SevoScreenEnums.PEDIA_BONUSES):
			iBonusType = self.pediaBonus.getBonusType(iItem)
			if iBonusType == SevoScreenEnums.TYPE_BONUS_MANA:			
				iCategory = SevoScreenEnums.PEDIA_MANA_NODES				
		elif (iCategory == SevoScreenEnums.PEDIA_IMPROVEMENTS):
			iImprovementType = self.pediaImprovement.getImprovementType(iItem)
			if iImprovementType == SevoScreenEnums.TYPE_UNIQUE_FEATURES:
				iCategory = SevoScreenEnums.PEDIA_UNIQUE_FEATURES
##--------	BUGFfH: Added by Denev 2009/10/07
		elif (iCategory == SevoScreenEnums.PEDIA_SPELLS):
			bAbility = self.pediaSpell.getSpellType(iItem)
			if bAbility:
				iCategory = SevoScreenEnums.PEDIA_ABILITIES
##--------	BUGFfH: End Add
	# MINOR_LEADERS_PEDIA 08/2013 lfgr
		elif (iCategory == SevoScreenEnums.PEDIA_LEADERS):
			BugUtil.debug("Leader!")
			iLeaderType = self.pediaLeader.getLeaderType(iItem)
			if iLeaderType == SevoScreenEnums.TYPE_MINOR:		
				BugUtil.debug("MINOR Leader!")	
				iCategory = SevoScreenEnums.PEDIA_MINOR_LEADERS	
	# MINOR_LEADERS_PEDIA end
		elif (iCategory == SevoScreenEnums.PEDIA_BTS_CONCEPTS):
			iCategory = self.determineNewConceptSubCategory(iItem)
			BugUtil.debug("Switching to category %d" % iCategory)
		self.showContents(bIsLink, iCategory)
		screen.setSelectedListBoxStringGFC(self.CATEGORY_LIST_ID, iCategory - (SevoScreenEnums.PEDIA_MAIN + 1))
		if (iCategory not in (SevoScreenEnums.PEDIA_UNIT_UPGRADES, SevoScreenEnums.PEDIA_PROMOTION_TREE, SevoScreenEnums.PEDIA_HINTS)):
			screen.enableSelect(self.ITEM_LIST_ID, True)
			if (self.iItemIndex != -1):
				BugUtil.debug("Deselecting item %d" % self.iItemIndex)
				screen.selectRow(self.ITEM_LIST_ID, self.iItemIndex, False)
			BugUtil.debug("Selecting item %d" % iItem)
			self.iItem = iItem
			for i, item in enumerate(self.list):
				if (item[1] == iItem):
					BugUtil.debug("Selecting %dth item %d" % (i, iItem))
					#screen.setSelectedListBoxStringGFC(self.ITEM_LIST_ID, i)
					screen.selectRow(self.ITEM_LIST_ID, i, True)
					self.iItemIndex = i
					#break

		#self.iCategory = iCategory
		BugUtil.debug("Drawing screen %d item %d" % (iCategory, iItem))
		self.deleteAllWidgets()
		func = self.mapScreenFunctions.get(iCategory)
		func.interfaceScreen(iItem)

	def determineNewConceptSubCategory(self, iItem):
		info = gc.getNewConceptInfo(iItem)
		BugUtil.debug("NewConcept itme %d is %s" % (iItem, info.getDescription()))
##--------	BUGFfH: Deleted by Denev 2009/10/08
		"""
		if (self.isTraitInfo(info)):
			return SevoScreenEnums.PEDIA_TRAITS
		"""
##--------	BUGFfH: End Delete
		if (self.isStrategyInfo(info)):
			return SevoScreenEnums.PEDIA_STRATEGY
		if (self.isShortcutInfo(info)):
			return SevoScreenEnums.PEDIA_SHORTCUTS
		return SevoScreenEnums.PEDIA_BTS_CONCEPTS

	def isContentsShowing(self):
		return self.tab == self.TAB_TOC
	
	def showContents(self, bForce=False, iCategory=SevoScreenEnums.PEDIA_TECHS):
		self.deleteAllWidgets()
		if not self.isContentsShowing():
			BugUtil.debug("Drawing category list")
			self.placeCategories(iCategory)
			screen = self.getScreen()
			screen.setText(self.TOC_ID, "Background", self.TOC_ACTIVE_TEXT,   CvUtil.FONT_LEFT_JUSTIFY,   self.X_TOC,   self.Y_TOC,   0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
			screen.setText(self.INDEX_ID, "Background", self.INDEX_TEXT, CvUtil.FONT_LEFT_JUSTIFY, self.X_INDEX, self.Y_INDEX, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
			screen.show(self.BACK_ID)
			screen.show(self.NEXT_ID)
		if not self.isContentsShowing() or self.iCategory != iCategory or bForce:
			BugUtil.debug("Drawing item list %d" % iCategory)
			self.mapListGenerators.get(iCategory)()
			self.iCategory = iCategory
			self.iItem = -1
			self.iItemIndex = -1
		self.tab = self.TAB_TOC

	def isIndexShowing(self):
		return self.tab == self.TAB_INDEX
	
	def showIndex(self):
		if self.isIndexShowing(): return
		self.deleteAllWidgets()
		self.deleteListWidgets()
		screen = self.getScreen()
		screen.setText(self.TOC_ID, "Background", self.TOC_TEXT,   CvUtil.FONT_LEFT_JUSTIFY,   self.X_TOC,   self.Y_TOC,   0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
		screen.setText(self.INDEX_ID, "Background", self.INDEX_ACTIVE_TEXT, CvUtil.FONT_LEFT_JUSTIFY, self.X_INDEX, self.Y_INDEX, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
		screen.hide(self.BACK_ID)
		screen.hide(self.NEXT_ID)
		self.pediaIndex.interfaceScreen()
		self.tab = self.TAB_INDEX
	
	def initPositions( self ) :
		# lfgr 10/2019 full-screen support
		self.initDimensions()
		
		# Using upper-case names for compatibility with pedia pages (other files)
		self.W_SCREEN = self.wScreen # Orig: 1024
		self.H_SCREEN = self.hScreen # Orig: 768
		self.X_SCREEN = self.W_SCREEN / 2 # Orig: 500
		#self.Y_SCREEN = 396

		self.H_PANEL = 55
		self.BUTTON_SIZE = 64
		self.BUTTON_COLUMNS = 9
		self.ITEMS_MARGIN = 18
		self.ITEMS_SEPARATION = 2

		self.X_TOP_PANEL = 0
		self.Y_TOP_PANEL = 0
		self.W_TOP_PANEL = self.W_SCREEN
		self.H_TOP_PANEL = self.H_PANEL

		self.X_BOT_PANEL = 0
		self.Y_BOT_PANEL = self.H_SCREEN - self.H_PANEL
		self.W_BOT_PANEL = self.W_SCREEN
		self.H_BOT_PANEL = self.H_PANEL

		self.X_CATEGORIES = 0
		self.Y_CATEGORIES = (self.Y_TOP_PANEL + self.H_TOP_PANEL) - 4
		self.W_CATEGORIES = 175
		self.H_CATEGORIES = (self.Y_BOT_PANEL + 3) - self.Y_CATEGORIES

		self.X_ITEMS = self.X_CATEGORIES + self.W_CATEGORIES + 2
		self.Y_ITEMS = self.Y_CATEGORIES
		self.W_ITEMS = 210
		self.H_ITEMS = self.H_CATEGORIES

		self.X_PEDIA_PAGE = self.X_ITEMS + self.W_ITEMS + 18
		self.Y_PEDIA_PAGE = self.Y_ITEMS + 13
		self.R_PEDIA_PAGE = self.W_SCREEN - 20
		self.B_PEDIA_PAGE = self.Y_ITEMS + self.H_ITEMS - 16
		self.W_PEDIA_PAGE = self.R_PEDIA_PAGE - self.X_PEDIA_PAGE
		self.H_PEDIA_PAGE = self.B_PEDIA_PAGE - self.Y_PEDIA_PAGE

		self.X_TITLE = self.X_SCREEN
		self.Y_TITLE = 8
		self.X_TOC = 75
		self.Y_TOC = self.yExitButton # Orig: 730 = self.H_SCREEN - 48
		self.X_INDEX = self.W_SCREEN - 814 # Orig: 210
		self.Y_INDEX = self.yExitButton # Orig: 730
		self.X_BACK = self.W_SCREEN - 514 # Orig: 510
		self.Y_BACK = self.yExitButton # Orig: 730
		self.X_NEXT = self.W_SCREEN - 379 # Orig: 645
		self.Y_NEXT = self.yExitButton # Orig: 730
		self.X_EXIT = self.W_SCREEN - 30 # Orig: 994
		self.Y_EXIT = self.yExitButton # Orig: 730

##--------	BUGFfH: Added by Denev 2009/10/04
		self.X_MERGIN = 10
		self.Y_MERGIN = 5
##--------	BUGFfH: End Add
	
	def setPediaCommonWidgets(self):
		self.initPositions()
		
		self.HEAD_TEXT = u"<font=4b>" + localText.getText("TXT_KEY_SEVOPEDIA_TITLE",      ())         + u"</font>"
		self.BACK_TEXT = u"<font=4>"  + localText.getText("TXT_KEY_PEDIA_SCREEN_BACK",    ()).upper() + u"</font>"
		self.NEXT_TEXT = u"<font=4>"  + localText.getText("TXT_KEY_PEDIA_SCREEN_FORWARD", ()).upper() + u"</font>"
		self.EXIT_TEXT = u"<font=4>"  + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT",    ()).upper() + u"</font>"
		
		self.TOC_TEXT = u"<font=4>"  + localText.getText("TXT_KEY_PEDIA_SCREEN_CONTENTS", ()).upper() + u"</font>"
		self.INDEX_TEXT = u"<font=4>"  + localText.getText("TXT_KEY_PEDIA_SCREEN_INDEX",  ()).upper() + u"</font>"
		eYellow = gc.getInfoTypeForString("COLOR_YELLOW")
		self.TOC_ACTIVE_TEXT = u"<font=4>"  + localText.getColorText("TXT_KEY_PEDIA_SCREEN_CONTENTS", (), eYellow).upper() + u"</font>"
		self.INDEX_ACTIVE_TEXT = u"<font=4>"  + localText.getColorText("TXT_KEY_PEDIA_SCREEN_INDEX",  (), eYellow).upper() + u"</font>"

		self.szCategoryTechs		= localText.getText("TXT_KEY_PEDIA_CATEGORY_TECH", ())
		self.szCategoryUnits		= localText.getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ())
		self.szCategoryUnitUpgrades	= localText.getText("TXT_KEY_PEDIA_CATEGORY_UNIT_UPGRADES", ())
		self.szCategoryUnitCategories	= localText.getText("TXT_KEY_PEDIA_CATEGORY_UNIT_COMBAT", ())
		self.szCategoryPromotions	= localText.getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION", ())
		self.szCategoryPromotionTree	= localText.getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION_TREE", ())
		self.szCategoryBuildings	= localText.getText("TXT_KEY_PEDIA_CATEGORY_BUILDING", ())
		self.szCategoryNationalWonders	= localText.getText("TXT_KEY_PEDIA_CATEGORY_NATIONAL_WONDERS", ())
		self.szCategoryGreatWonders	= localText.getText("TXT_KEY_PEDIA_CATEGORY_GREAT_WONDERS", ())
		self.szCategoryProjects		= localText.getText("TXT_KEY_PEDIA_CATEGORY_PROJECT", ())
		self.szCategorySpecialists	= localText.getText("TXT_KEY_PEDIA_CATEGORY_SPECIALIST", ())
		self.szCategoryTerrains		= localText.getText("TXT_KEY_PEDIA_CATEGORY_TERRAIN", ())
		self.szCategoryFeatures		= localText.getText("TXT_KEY_PEDIA_CATEGORY_FEATURE", ())
		self.szCategoryBonuses		= localText.getText("TXT_KEY_PEDIA_CATEGORY_BONUS", ())
		self.szCategoryManaNodes		= localText.getText("TXT_KEY_PEDIA_CATEGORY_MANANODES", ())
		self.szCategoryImprovements	= localText.getText("TXT_KEY_PEDIA_CATEGORY_IMPROVEMENT", ())
		self.szCategoryCivs			= localText.getText("TXT_KEY_PEDIA_CATEGORY_CIV", ())
		self.szCategoryLeaders		= localText.getText("TXT_KEY_PEDIA_CATEGORY_LEADER", ())
	# MINOR_LEADERS_PEDIA 08/2013 lfgr
		self.szCategoryMinorLeaders	= localText.getText("TXT_KEY_PEDIA_CATEGORY_MINOR_LEADER", ())
	# MINOR_LEADERS_PEDIA end
		self.szCategoryTraits		= localText.getText("TXT_KEY_PEDIA_TRAITS", ())
		self.szCategoryCivics		= localText.getText("TXT_KEY_PEDIA_CATEGORY_CIVIC", ())
		self.szCategoryReligions	= localText.getText("TXT_KEY_PEDIA_CATEGORY_RELIGION", ())
#		self.szCategoryCorporations	= localText.getText("TXT_KEY_CONCEPT_CORPORATIONS", ())
		self.szCategorySpells = localText.getText("TXT_KEY_PEDIA_CATEGORY_SPELLS", ())
		self.szCategoryAbilities	= localText.getText("TXT_KEY_PEDIA_CATEGORY_ABILITY", ())	
		self.szCategoryConcepts		= localText.getText("TXT_KEY_PEDIA_CATEGORY_CONCEPT", ())
		self.szCategoryConceptsNew	= localText.getText("TXT_KEY_PEDIA_CATEGORY_CONCEPT_NEW", ())
		self.szCategoryHints		= localText.getText("TXT_KEY_PEDIA_CATEGORY_HINTS", ())
		self.szCategoryShortcuts	= localText.getText("TXT_KEY_PEDIA_CATEGORY_SHORTCUTS", ())
##--------	BUGFfH: Deleted by Denev 2009/08/12
#		self.szCategoryStrategy   	= localText.getText("TXT_KEY_PEDIA_CATEGORY_STRATEGY", ())
##--------	BUGFfH: End Delete
		self.szCategoryEffects		= localText.getText("TXT_KEY_PEDIA_CATEGORY_EFFECTS", ())
		self.szCategorySpheres		= localText.getText("TXT_KEY_PEDIA_CATEGORY_SPHERES", ())
		self.szCategoryEquipments	= localText.getText("TXT_KEY_PEDIA_CATEGORY_ITEMS", ())
		self.szCategoryRaces		= localText.getText("TXT_KEY_PEDIA_CATEGORY_RACES", ())
		self.szCategoryUniqueFeatures	= localText.getText("TXT_KEY_PEDIA_CATEGORY_UNIQUE_FEATURE", ())
		
		self.categoryList = [
			["TECHS",	self.szCategoryTechs],
			["UNITS",	self.szCategoryUnits],
			["UNITS",	self.szCategoryUnitUpgrades],
			["UNITS",	self.szCategoryUnitCategories],
			["PROMOTIONS",	self.szCategoryPromotions],
			["PROMOTIONS",	self.szCategorySpheres],
			["PROMOTIONS",	self.szCategoryPromotionTree],
			["PROMOTIONS",	self.szCategoryEffects],
			["PROMOTIONS",	self.szCategoryEquipments],
			["PROMOTIONS",	self.szCategoryRaces],
			["BUILDINGS",	self.szCategoryBuildings],
			["BUILDINGS",	self.szCategoryNationalWonders],
			["BUILDINGS",	self.szCategoryGreatWonders],
			["BUILDINGS",	self.szCategoryProjects],
			["SPECIALISTS",	self.szCategorySpecialists],
			["TERRAINS",	self.szCategoryTerrains],
			["TERRAINS",	self.szCategoryFeatures],

##--------	BUGFfH: Added by Denev 2009/08/12
			["TERRAINS",	self.szCategoryUniqueFeatures],
##--------	BUGFfH: End Add

			["TERRAINS",	self.szCategoryBonuses],
			["TERRAINS",	self.szCategoryManaNodes],			
			["TERRAINS",	self.szCategoryImprovements],
			["CIVS",	self.szCategoryCivs],
			["CIVS",	self.szCategoryLeaders],
	# MINOR_LEADERS_PEDIA 08/2013 lfgr
			["CIVS",	self.szCategoryMinorLeaders],
	# MINOR_LEADERS_PEDIA end
			["CIVS",	self.szCategoryTraits],
			["CIVICS",	self.szCategoryCivics],
			["CIVICS",	self.szCategoryReligions],
#			["CIVICS",	self.szCategoryCorporations],
			["SPELLS",  self.szCategorySpells],
			["SPELLS",	self.szCategoryAbilities],
			["HINTS",	self.szCategoryConcepts],
			["HINTS",	self.szCategoryConceptsNew],
			["HINTS",	self.szCategoryHints],
			["HINTS",	self.szCategoryShortcuts],
##--------	BUGFfH: Deleted by Denev 2009/08/12
#			["HINTS",	self.szCategoryStrategy],
##--------	BUGFfH: End Delete
			]

		self.categoryGraphics = {
			"TECHS"		: u"%c  " %(gc.getCommerceInfo(CommerceTypes.COMMERCE_RESEARCH).getChar()),
			"UNITS"		: u"%c  " %(CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR)),
			"PROMOTIONS"	: u"%c  " %(CyGame().getSymbolID(FontSymbols.SILVER_STAR_CHAR)),
			"BUILDINGS"	: u"%c  " %(gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar()),
			"SPECIALISTS"	: u"%c  " %(CyGame().getSymbolID(FontSymbols.GREAT_PEOPLE_CHAR)),
			"TERRAINS"	: u"%c  " %(gc.getYieldInfo(YieldTypes.YIELD_FOOD).getChar()),
			"CIVS"		: u"%c  " %(CyGame().getSymbolID(FontSymbols.MAP_CHAR)),
			"CIVICS"	: u"%c  " %(gc.getCommerceInfo(CommerceTypes.COMMERCE_CULTURE).getChar()),
			"SPELLS"		: u"%c  " %(gc.getBonusInfo(gc.getInfoTypeForString('BONUS_MANA')).getChar()), ##gc.getYieldInfo(YieldTypes.YIELD_COMMERCE).getChar())
			"HINTS"		: u"%c  " %(gc.getYieldInfo(YieldTypes.YIELD_COMMERCE).getChar()),
			}

		screen = self.getScreen()
		screen.setRenderInterfaceOnly(True)
		screen.setScreenGroup(1)
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		screen.addDDSGFC(self.BACKGROUND_ID, ArtFileMgr.getInterfaceArtInfo("SCREEN_BG_OPAQUE").getPath(), 0, 0, self.W_SCREEN, self.H_SCREEN, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.addPanel(self.TOP_PANEL_ID, u"", u"", True, False, self.X_TOP_PANEL, self.Y_TOP_PANEL, self.W_TOP_PANEL, self.H_TOP_PANEL, PanelStyles.PANEL_STYLE_TOPBAR)
		screen.addPanel(self.BOT_PANEL_ID, u"", u"", True, False, self.X_BOT_PANEL, self.Y_BOT_PANEL, self.W_BOT_PANEL, self.H_BOT_PANEL, PanelStyles.PANEL_STYLE_BOTTOMBAR)
		#screen.setDimensions(screen.centerX(0), screen.centerY(0), self.W_SCREEN, self.H_SCREEN)

		screen.setText(self.HEAD_ID, "Background", self.HEAD_TEXT, CvUtil.FONT_CENTER_JUSTIFY, self.X_TITLE, self.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL,      -1, -1)
		screen.setText(self.BACK_ID, "Background", self.BACK_TEXT, CvUtil.FONT_LEFT_JUSTIFY,   self.X_BACK,  self.Y_BACK,  0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_BACK,    1, -1)
		screen.setText(self.NEXT_ID, "Background", self.NEXT_TEXT, CvUtil.FONT_LEFT_JUSTIFY,   self.X_NEXT,  self.Y_NEXT,  0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_FORWARD, 1, -1)
		screen.setText(self.EXIT_ID, "Background", self.EXIT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY,  self.X_EXIT,  self.Y_EXIT,  0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1)



	def placeCategories(self, iCategory=None):
		screen = self.getScreen()
		screen.addListBoxGFC(self.CATEGORY_LIST_ID, "", self.X_CATEGORIES, self.Y_CATEGORIES, self.W_CATEGORIES, self.H_CATEGORIES, TableStyles.TABLE_STYLE_STANDARD)
		screen.enableSelect(self.CATEGORY_LIST_ID, True)
		screen.setStyle(self.CATEGORY_LIST_ID, "Table_StandardCiv_Style")
		screen.clearListBoxGFC(self.CATEGORY_LIST_ID)
		for i, category in enumerate(self.categoryList):
			graphic = self.categoryGraphics[category[0]]
			screen.appendListBoxStringNoUpdate(self.CATEGORY_LIST_ID, graphic + category[1], WidgetTypes.WIDGET_PEDIA_MAIN, SevoScreenEnums.PEDIA_MAIN + i + 1, 0, CvUtil.FONT_LEFT_JUSTIFY)
		screen.updateListBox(self.CATEGORY_LIST_ID)



	def placeTechs(self):
		self.list = self.getTechList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, gc.getTechInfo)
	
	def getTechList(self):
		return self.getSortedList(gc.getNumTechInfos(), gc.getTechInfo)


	def placeUnits(self):
		self.list = self.getUnitList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, gc.getUnitInfo)
	
	def getUnitList(self):
		return self.getSortedList(gc.getNumUnitInfos(), gc.getUnitInfo)


	def placeUnitUpgrades(self):
		screen = self.getScreen()
		self.getScreen().deleteWidget("PediaMainItemList")
		self.UPGRADES_GRAPH_ID = self.getNextWidgetName()
		screen.addScrollPanel(self.UPGRADES_GRAPH_ID, u"", self.X_ITEMS, self.Y_PEDIA_PAGE - 13, self.W_SCREEN - self.X_ITEMS, self.H_PEDIA_PAGE + 2, PanelStyles.PANEL_STYLE_STANDARD)
		screen.setActivation(self.UPGRADES_GRAPH_ID, ActivationTypes.ACTIVATE_NORMAL)
		upgradesGraph = UnitUpgradesGraph.UnitUpgradesGraph(self)
		upgradesGraph.getGraph()
		upgradesGraph.drawGraph()


	def placeUnitCategories(self):
		self.list = self.getUnitCategoryList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT, gc.getUnitCombatInfo)
	
	def getUnitCategoryList(self):
		return self.getSortedList(gc.getNumUnitCombatInfos(), gc.getUnitCombatInfo)


	def placePromotions(self):
##--------	BUGFfH: Modified by Denev 2009/10/06
#		self.list = self.getPromotionList()
		self.list = self.getPromotionList(SevoScreenEnums.TYPE_REGULAR)
##--------	BUGFfH: End Modify
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, gc.getPromotionInfo)

##--------	BUGFfH: Modified by Denev 2009/10/06
	"""
	def getPromotionList(self):
		return self.getSortedList(gc.getNumPromotionInfos(), gc.getPromotionInfo)
	"""
	def getPromotionList(self, iType = None):
		return self.getSortedList(gc.getNumPromotionInfos(), gc.getPromotionInfo, iType, self.pediaPromotion.getPromotionType)
##--------	BUGFfH: End Modify


##--------	BUGFfH: Added by Denev 2009/10/06
	def placeSpells(self):
		self.list = self.getSpellList(false)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPELL, gc.getSpellInfo)

	def placeAbilities(self):
		self.list = self.getSpellList(true)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPELL, gc.getSpellInfo)

	def getSpellList(self, bAbility = None):
		return self.getSortedList(gc.getNumSpellInfos(), gc.getSpellInfo, bAbility, self.pediaSpell.getSpellType)
##--------	BUGFfH: End Add


	def placePromotionTree(self):
		screen = self.getScreen()
		self.getScreen().deleteWidget("PediaMainItemList")
		self.UPGRADES_GRAPH_ID = self.getNextWidgetName()
		screen.addScrollPanel(self.UPGRADES_GRAPH_ID, u"", self.X_ITEMS, self.Y_PEDIA_PAGE - 13, self.W_SCREEN - self.X_ITEMS, self.H_PEDIA_PAGE + 2, PanelStyles.PANEL_STYLE_STANDARD)
		screen.setActivation(self.UPGRADES_GRAPH_ID, ActivationTypes.ACTIVATE_NORMAL)
		upgradesGraph = UnitUpgradesGraph.PromotionsGraph(self)
		upgradesGraph.getGraph()
		upgradesGraph.drawGraph()


	def placeBuildings(self):
##--------	BUGFfH: Modified by Denev 2009/10/06
#		self.list = self.getBuildingList()
		self.list = self.getBuildingList(SevoScreenEnums.TYPE_REGULAR)
##--------	BUGFfH: End Modify
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, gc.getBuildingInfo)

##--------	BUGFfH: Modified by Denev 2009/10/06
	"""
	def getBuildingList(self):
		return self.pediaBuilding.getBuildingSortedList(0)
	"""
	def getBuildingList(self, iType = None):
		return self.getSortedList(gc.getNumBuildingInfos(), gc.getBuildingInfo, iType, self.pediaBuilding.getBuildingType)
##--------	BUGFfH: End Modify


	def placeNationalWonders(self):
##--------	BUGFfH: Modified by Denev 2009/10/06
#		self.list = self.getNationalWonderList()
		self.list = self.getBuildingList(SevoScreenEnums.TYPE_NATIONAL)
##--------	BUGFfH: End Modify
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, gc.getBuildingInfo)
	
##--------	BUGFfH: Deleteed by Denev 2009/09/10
		"""
	def getNationalWonderList(self):
		return self.pediaBuilding.getBuildingSortedList(1)
		"""
##--------	BUGFfH: End Delete


	def placeGreatWonders(self):
##--------	BUGFfH: Modified by Denev 2009/10/06
#		self.list = self.getGreatWonderList()
		self.list = self.getBuildingList(SevoScreenEnums.TYPE_WORLD)
##--------	BUGFfH: End Modify
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, gc.getBuildingInfo)

##--------	BUGFfH: Deleteed by Denev 2009/09/10
		"""
	def getGreatWonderList(self):
		return self.pediaBuilding.getBuildingSortedList(2)
		"""
##--------	BUGFfH: End Delete


	def placeProjects(self):
		self.list = self.getProjectList(SevoScreenEnums.TYPE_REGULAR)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT, gc.getProjectInfo)
	
	def getProjectList(self):
		return self.getSortedList(gc.getNumProjectInfos(), gc.getProjectInfo)


	def getProjectList(self, iType = None):
		return self.getSortedList(gc.getNumProjectInfos(), gc.getProjectInfo, iType, self.pediaProject.getProjectType)
		
	def placeSpecialists(self):
		self.list = self.getSpecialistList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPECIALIST, gc.getSpecialistInfo)
	
	def getSpecialistList(self):
		return self.getSortedList(gc.getNumSpecialistInfos(), gc.getSpecialistInfo)


	def placeTerrains(self):
		self.list = self.getTerrainList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_TERRAIN, gc.getTerrainInfo)
	
	def getTerrainList(self):
		return self.getSortedList(gc.getNumTerrainInfos(), gc.getTerrainInfo)


	def placeFeatures(self):
		self.list = self.getFeatureList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_FEATURE, gc.getFeatureInfo)
	
	def getFeatureList(self):
		return self.getSortedList(gc.getNumFeatureInfos(), gc.getFeatureInfo)


	def placeBonuses(self):
		self.list = self.getBonusList(SevoScreenEnums.TYPE_REGULAR)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, gc.getBonusInfo)
	
	def placeManaNodes(self):
		self.list = self.getBonusList(SevoScreenEnums.TYPE_BONUS_MANA)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, gc.getBonusInfo)
	
	"""
	def getBonusList(self):
		return self.getSortedList(gc.getNumBonusInfos(), gc.getBonusInfo)
	"""
	
	def getBonusList(self, iBonus = None):
		return self.getSortedList(gc.getNumBonusInfos(), gc.getBonusInfo, iBonus, self.pediaBonus.getBonusType)
	
	def placeImprovements(self):
		self.list = self.getImprovementList(SevoScreenEnums.TYPE_REGULAR)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, gc.getImprovementInfo)

	def placeUniqueFeatures(self):
		self.list = self.getImprovementList(SevoScreenEnums.TYPE_UNIQUE_FEATURES)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, gc.getImprovementInfo)

	def placeImprovementsPrimary(self):
		self.list = self.getImprovementList(SevoScreenEnums.TYPE_PRIMARY)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, gc.getImprovementInfo)

	def placeImprovementsSecondary(self):
		self.list = self.getImprovementList(SevoScreenEnums.TYPE_SECONDARY)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT, gc.getImprovementInfo)
		
		
##--------	BUGFfH: Modified by Denev 2009/10/06
	"""
	def getImprovementList(self):
		return self.getSortedList(gc.getNumImprovementInfos(), gc.getImprovementInfo)
	"""
	def getImprovementList(self, iImprovement = None):
		return self.getSortedList(gc.getNumImprovementInfos(), gc.getImprovementInfo, iImprovement, self.pediaImprovement.getImprovementType)
##--------	BUGFfH: End Modify


	def placeCivs(self):
		self.list = self.getCivilizationList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, gc.getCivilizationInfo)
	
	def getCivilizationList(self):
		return self.getSortedList(gc.getNumCivilizationInfos(), gc.getCivilizationInfo)


	def placeLeaders(self):
	# MINOR_LEADERS_PEDIA 08/2013 lfgr
	#	self.list = self.getLeaderList()
		self.list = self.getLeaderList( SevoScreenEnums.TYPE_MAJOR )
	# MINOR_LEADERS_PEDIA end
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, gc.getLeaderHeadInfo)

# MINOR_LEADERS_PEDIA 08/2013 lfgr
	def placeMinorLeaders(self):
		self.list = self.getLeaderList( SevoScreenEnums.TYPE_MINOR )
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, gc.getLeaderHeadInfo)

#	 def getLeaderList(self):
#		return self.getSortedList(gc.getNumLeaderHeadInfos(), gc.getLeaderHeadInfo)
	def getLeaderList( self, iType ):
		return self.getSortedList( gc.getNumLeaderHeadInfos(), gc.getLeaderHeadInfo, iType, self.pediaLeader.getLeaderType )
# MINOR_LEADERS_PEDIA end


	def placeTraits(self):
		self.list = self.getTraitList()
##--------	BUGFfH: Modified by Denev 2009/09/10
#		self.placeItems(WidgetTypes.WIDGET_PEDIA_DESCRIPTION, self.getTraitInfo)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_TRAIT, gc.getTraitInfo)
##--------	BUGFfH: End Modify
	
	def getTraitList(self):
##--------	BUGFfH: Modified by Denev 2009/09/10
#		return self.getSortedList(gc.getNumNewConceptInfos(), self.getTraitInfo, True)
		return self.getSortedList(gc.getNumTraitInfos(), gc.getTraitInfo)
##--------	BUGFfH: End Modify

##--------	BUGFfH: Deleteed by Denev 2009/09/10
		"""
	def getTraitInfo(self, id):
		info = gc.getNewConceptInfo(id)
		if self.isTraitInfo(info):
			
			class TraitInfo:
				def __init__(self, conceptInfo):
					self.conceptInfo = conceptInfo
					sKey = conceptInfo.getType()
					sKey = sKey[sKey.find("TRAIT_"):]
					self.eTrait = gc.getInfoTypeForString(sKey)
					self.traitInfo = gc.getTraitInfo(self.eTrait)
				def getDescription(self):
					return u"%c %s" % (TraitUtil.getIcon(self.eTrait), self.traitInfo.getDescription())
				def getButton(self):
					return self.traitInfo.getButton()
			
			return TraitInfo(info)
		return None
		"""
##--------	BUGFfH: End Delete

	def isTraitInfo(self, info):
		return info.getType().find("_TRAIT_") != -1


	def placeCivics(self):
		self.list = self.getCivicList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC, gc.getCivicInfo)
	
	def getCivicList(self):
		return self.getSortedList(gc.getNumCivicInfos(), gc.getCivicInfo)


	def placeReligions(self):
		self.list = self.getReligionList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, gc.getReligionInfo)
	
	def getReligionList(self):
		return self.getSortedList(gc.getNumReligionInfos(), gc.getReligionInfo)


	def placeCorporations(self):
		self.list = self.getCorporationList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_CORPORATION, gc.getCorporationInfo)
	
	def getCorporationList(self):
		return self.getSortedList(gc.getNumCorporationInfos(), gc.getCorporationInfo)


##--------	BUGFfH: Added by Denev 2009/10/06
	def placeHeroes(self):
		self.list = self.getUnitList(SevoScreenEnums.TYPE_WORLDUNIT)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, gc.getUnitInfo)

	def placeEffects(self):
		self.list = self.getPromotionList(SevoScreenEnums.TYPE_EFFECT)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, gc.getPromotionInfo)

	def placeEquipments(self):
		self.list = self.getPromotionList(SevoScreenEnums.TYPE_EQUIPMENT)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, gc.getPromotionInfo)

	def placeGear(self):
		self.list = self.getPromotionList(SevoScreenEnums.TYPE_GEAR)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, gc.getPromotionInfo)
		
	def placeRaces(self):
		self.list = self.getPromotionList(SevoScreenEnums.TYPE_RACE)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, gc.getPromotionInfo)

##--------	BUGFfH: End Add

	def placeSpheres(self):
		self.list = self.getPromotionList(SevoScreenEnums.TYPE_SPHERE)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, gc.getPromotionInfo)

	def placeConcepts(self):
		self.list = self.getConceptList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_DESCRIPTION, gc.getConceptInfo)
	
	def getConceptList(self):
		return self.getSortedList(gc.getNumConceptInfos(), gc.getConceptInfo)


	def placeBTSConcepts(self):
		self.list = self.getNewConceptList()
		self.placeItems(WidgetTypes.WIDGET_PEDIA_DESCRIPTION, self.getNewConceptInfo)
	
	def getNewConceptList(self):
		return self.getSortedList(gc.getNumNewConceptInfos(), self.getNewConceptInfo)

	def getNewConceptInfo(self, id):
		info = gc.getNewConceptInfo(id)
		if not self.isShortcutInfo(info) and not self.isStrategyInfo(info) and not self.isTraitInfo(info):
			return info
		return None


	def placeHints(self):
		screen = self.getScreen()
		self.getScreen().deleteWidget("PediaMainItemList")
		szHintBox = self.getNextWidgetName()
		screen.addListBoxGFC(szHintBox, "", self.X_ITEMS, self.Y_PEDIA_PAGE - 10, self.W_SCREEN - self.X_ITEMS, self.H_PEDIA_PAGE + 23, TableStyles.TABLE_STYLE_STANDARD)
		screen.enableSelect(szHintBox, False)
		szHintsText = CyGameTextMgr().buildHintsList()
		hintText = string.split(szHintsText, "\n")
		for hint in hintText:
			if len(hint) != 0:
				screen.appendListBoxStringNoUpdate(szHintBox, hint, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.updateListBox(szHintBox)


	def placeShortcuts(self):
		self.list = self.getSortedList(gc.getNumNewConceptInfos(), self.getShortcutInfo)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_DESCRIPTION, self.getShortcutInfo)

	def getShortcutInfo(self, id):
		info = gc.getNewConceptInfo(id)
		if self.isShortcutInfo(info):
			return info
		return None
	
	def isShortcutInfo(self, info):
		return info.getType().find("SHORTCUTS") != -1


	def placeStrategy(self):
		self.list = self.getSortedList(gc.getNumNewConceptInfos(), self.getStrategyInfo)
		self.placeItems(WidgetTypes.WIDGET_PEDIA_DESCRIPTION, self.getStrategyInfo)

	def getStrategyInfo(self, id):
		info = gc.getNewConceptInfo(id)
		if self.isStrategyInfo(info):
			return info
		return None
	
	def isStrategyInfo(self, info):
		return info.getType().find("STRATEGY") != -1
	
	
	
	def placeItems(self, widget, info):
		screen = self.getScreen()
		screen.clearListBoxGFC(self.ITEM_LIST_ID)

		screen.addTableControlGFC(self.ITEM_LIST_ID, 1, self.X_ITEMS, self.Y_ITEMS, self.W_ITEMS, self.H_ITEMS, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.enableSelect(self.ITEM_LIST_ID, False)
		screen.setStyle(self.ITEM_LIST_ID, "Table_StandardCiv_Style")
		screen.setTableColumnHeader(self.ITEM_LIST_ID, 0, "", self.W_ITEMS)

##--------	BUGFfH: Modified by Denev 2009/10/09
		"""
		i = 0
		for item in self.list:
			if (info == gc.getConceptInfo):
				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT
				data2 = item[1]
			elif (info == self.getNewConceptInfo):
				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW
				data2 = item[1]
			elif (info == self.getShortcutInfo):
				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW
				data2 = item[1]
			elif (info == self.getStrategyInfo):
				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW
				data2 = item[1]
			elif (info == self.getTraitInfo):
				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW
				data2 = item[1]
			else:
				data1 = item[1]
				data2 = 1
			screen.appendTableRow(self.ITEM_LIST_ID)
			screen.setTableText(self.ITEM_LIST_ID, 0, i, u"<font=3>" + item[0] + u"</font>", info(item[1]).getButton(), widget, data1, data2, CvUtil.FONT_LEFT_JUSTIFY)
			i += 1
		"""
		for szIndexName, iItemID, szItemName in self.list:
			if (info == gc.getConceptInfo):
				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT
				data2 = iItemID
#			elif (info == self.getWildmanaConceptInfo):
#				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_WILDMANA
#				data2 = iItemID
#			elif (info == gc.getWildmanaGuideInfo):
#				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_WILDMANA_GUIDE
#				data2 = iItemID				
			elif (info in (self.getNewConceptInfo, self.getShortcutInfo)):
				data1 = CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW
				data2 = iItemID
				
			elif (info == gc.getLeaderHeadInfo):
				data1 = iItemID						#LeaderID
				data2 = self.pickLeaderCiv(iItemID)	#CivilizationID which includes Leader
			else:
				data1 = iItemID
				data2 = 1

			iRow = screen.appendTableRow(self.ITEM_LIST_ID)
			if (info == gc.getUnitInfo):				
				szButton = gc.getUnitInfo(iItemID).getUnitButtonWithCivArtStyle(gc.getGame().getActiveCivilizationType())
			else:
				szButton = info(iItemID).getButton()
			screen.setTableText(self.ITEM_LIST_ID, 0, iRow, u"<font=3>" + szItemName + u"</font>", szButton, widget, data1, data2, CvUtil.FONT_LEFT_JUSTIFY)
##--------	BUGFfH: End Modify
		#screen.updateListBox(self.ITEM_LIST_ID)



##--------	BUGFfH: Added by Denev 2009/10/06
	def pickLeaderCiv(self, iLeader):
		liLeaderCiv = []
		iLeaderCiv = CivilizationTypes.NO_CIVILIZATION
		for iCiv in range(gc.getNumCivilizationInfos()):
			pCiv = gc.getCivilizationInfo(iCiv)
			if pCiv.isLeaders(iLeader):
				liLeaderCiv.append(iCiv)
		if len(liLeaderCiv) > 0:
			iLeaderCiv = random.choice(liLeaderCiv)

		return iLeaderCiv
##--------	BUGFfH: End Add



	def back(self):
		if (len(self.pediaHistory) > 1):
			self.pediaFuture.append(self.pediaHistory.pop())
			current = self.pediaHistory.pop()
			self.pediaJump(current[0], current[1], False, True)
		return 1



	def forward(self):
		if (self.pediaFuture):
			current = self.pediaFuture.pop()
			self.pediaJump(current[0], current[1], False, True)
		return 1



	def link(self, szLink):
		if (szLink == "PEDIA_MAIN_TECH"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_TECHS, True, True)
		elif (szLink == "PEDIA_MAIN_UNIT"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_UNITS, True, True)
		elif (szLink == "PEDIA_MAIN_UNIT_GROUP"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_UNIT_CATEGORIES, True, True)
		elif (szLink == "PEDIA_MAIN_PROMOTION"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_PROMOTIONS, True, True)
		elif (szLink == "PEDIA_MAIN_BUILDING"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_BUILDINGS, True, True)
		elif (szLink == "PEDIA_MAIN_PROJECT"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_PROJECTS, True, True)
		elif (szLink == "PEDIA_MAIN_SPECIALIST"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_SPECIALISTS, True, True)
		elif (szLink == "PEDIA_MAIN_TERRAIN"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_TERRAINS, True, True)
		elif (szLink == "PEDIA_MAIN_FEATURE"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_FEATURES, True, True)
		elif (szLink == "PEDIA_MAIN_BONUS"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_BONUSES, True, True)
		elif (szLink == "PEDIA_MAIN_IMPROVEMENT"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_IMPROVEMENTS, True, True)
		elif (szLink == "PEDIA_MAIN_CIV"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_CIVS, True, True)
		elif (szLink == "PEDIA_MAIN_LEADER"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_LEADERS, True, True)
			# MINOR_LEADERS_PEDIA_TODO
		elif (szLink == "PEDIA_MAIN_TRAIT"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_TRAITS, True, True)
		elif (szLink == "PEDIA_MAIN_CIVIC"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_CIVICS, True, True)
		elif (szLink == "PEDIA_MAIN_RELIGION"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_RELIGIONS, True, True)
		elif (szLink == "PEDIA_MAIN_CONCEPT"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_CONCEPTS, True, True)
		elif (szLink == "PEDIA_MAIN_HINTS"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_HINTS, True, True)
		elif (szLink == "PEDIA_MAIN_SHORTCUTS"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_SHORTCUTS, True, True)
		elif (szLink == "PEDIA_MAIN_STRATEGY"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_STRATEGY, True, True)
##--------	BUGFfH: Added by Denev 2009/08/10
		elif (szLink == "PEDIA_MAIN_SPELL"):
			return self.pediaJump(SevoScreenEnums.PEDIA_MAIN, SevoScreenEnums.PEDIA_SPELLS, True, True)
##--------	BUGFfH: End Add

		for i in range(gc.getNumTechInfos()):
			if (gc.getTechInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_TECHS, i, True, True)
		for i in range(gc.getNumUnitInfos()):
			if (gc.getUnitInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_UNITS, i, True, True)
		for i in range(gc.getNumUnitCombatInfos()):
			if (gc.getUnitCombatInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_UNIT_CATEGORIES, i, True, True)
		for i in range(gc.getNumPromotionInfos()):
			if (gc.getPromotionInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_PROMOTIONS, i, True, True)
##--------	BUGFfH: Added by Denev 2009/08/10
		for i in range(gc.getNumSpellInfos()):
			if (gc.getSpellInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_SPELLS, i, True, True)
##--------	BUGFfH: End Add
		for i in range(gc.getNumBuildingInfos()):
			if (gc.getBuildingInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_BUILDINGS, i, True, True)
		for i in range(gc.getNumProjectInfos()):
			if (gc.getProjectInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_PROJECTS, i, True, True)
		for i in range(gc.getNumSpecialistInfos()):
			if (gc.getSpecialistInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_SPECIALISTS, i, True, True)
		for i in range(gc.getNumTerrainInfos()):
			if (gc.getTerrainInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_TERRAINS, i, True, True)
		for i in range(gc.getNumFeatureInfos()):
			if (gc.getFeatureInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_FEATURES, i, True, True)
		for i in range(gc.getNumBonusInfos()):
			if (gc.getBonusInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_BONUSES, i, True, True)
		for i in range(gc.getNumImprovementInfos()):
			if (gc.getImprovementInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_IMPROVEMENTS, i, True, True)
		for i in range(gc.getNumCivilizationInfos()):
			if (gc.getCivilizationInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_CIVS, i, True, True)
		for i in range(gc.getNumLeaderHeadInfos()):
			if (gc.getLeaderHeadInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_LEADERS, i, True, True)
				# MINOR_LEADERS_PEDIA_TODO
##--------	BUGFfH: Added by Denev 2009/09/11
		for i in range(gc.getNumTraitInfos()):
			if (gc.getTraitInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_TRAITS, i, True, True)
##--------	BUGFfH: End Add
		for i in range(gc.getNumCivicInfos()):
			if (gc.getCivicInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_CIVICS, i, True, True)
		for i in range(gc.getNumReligionInfos()):
			if (gc.getReligionInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_RELIGIONS, i, True, True)
#		for i in range(gc.getNumCorporationInfos()):
#			if (gc.getCorporationInfo(i).isMatchForLink(szLink, False)):
#				return self.pediaJump(SevoScreenEnums.PEDIA_CORPORATIONS, i, True, True)
		for i in range(gc.getNumConceptInfos()):
			if (gc.getConceptInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_CONCEPTS, i, True, True)
		for i in range(gc.getNumNewConceptInfos()):
			if (gc.getNewConceptInfo(i).isMatchForLink(szLink, False)):
				return self.pediaJump(SevoScreenEnums.PEDIA_BTS_CONCEPTS, i, True, True)



	def handleInput (self, inputClass):
	# MINOR_LEADERS_PEDIA 08/2013 lfgr
	#	if (inputClass.getPythonFile() == SevoScreenEnums.PEDIA_LEADERS):
		if ( inputClass.getPythonFile() == SevoScreenEnums.PEDIA_LEADERS or inputClass.getPythonFile() == SevoScreenEnums.PEDIA_MINOR_LEADERS ) :
	# MINOR_LEADERS_PEDIA end
			return self.pediaLeader.handleInput(inputClass)
		elif (inputClass.getFunctionName() == self.TOC_ID):
			self.showContents()
			return 1
		elif (inputClass.getFunctionName() == self.INDEX_ID):
			self.showIndex()
			return 1
		elif (self.isIndexShowing()):
			return self.pediaIndex.handleInput(inputClass)
		
		return 0



	def deleteAllWidgets(self):
		screen = self.getScreen()
		iNumWidgets = self.nWidgetCount
		self.nWidgetCount = 0
		for i in range(iNumWidgets):
			screen.deleteWidget(self.getNextWidgetName())
		self.nWidgetCount = 0

	def deleteListWidgets(self):
		screen = self.getScreen()
		screen.deleteWidget("PediaMainCategoryList")
		screen.deleteWidget("PediaMainItemList")

	def getNextWidgetName(self):
		szName = self.WIDGET_ID + str(self.nWidgetCount)
		self.nWidgetCount += 1
		return szName


	def isSortLists(self):
		return AdvisorOpt.SevopediaSortItemList()

##--------	BUGFfH: Modified by Denev 2009/10/08
		"""
	def getSortedList(self, numInfos, getInfo, noSort=False):
		list = []
		for i in range(numInfos):
			item = getInfo(i)
			if item:
				list.append((item.getDescription(), i))
		if self.isSortLists() and not noSort:
			list.sort()
		return list
		"""
	def getSortedList(self, numInfos, getInfo, iCategory = None, getCategory = None):
		infoList = []
		for iItemID in range(numInfos):
			if getInfo(iItemID):
				if ((None in (iCategory, getCategory) or getCategory(iItemID) == iCategory) and not getInfo(iItemID).isGraphicalOnly()):
#					if (not getInfo==gc.getBuildingInfo) or gc.getBuildingInfo(iItemID).getProductionCost()>0:	#added Sephi to block wrong buildings in Buildinglist
					if (not getInfo==gc.getTechInfo) or not gc.getTechInfo(iItemID).isDisable(): #don't display disabled techs
						if (not getInfo==gc.getUnitInfo) or not gc.getUnitInfo(iItemID).isObject(): #do not display Objects in regular unit list
							szDescription = getInfo(iItemID).getDescription()
							if szDescription[0:4] == "The ":
								infoList.append( (szDescription[4:], iItemID, szDescription) )
							else:
								infoList.append( (szDescription, iItemID, szDescription) )
		if self.isSortLists():
			infoList.sort()

		return infoList
##--------	BUGFfH: End Modify


##--------	BUGFfH: Added by Denev 2009/10/07
	def getListBuildingCivilization(self, iBuilding):
		if iBuilding == BuildingTypes.NO_BUILDING:
			return []

		liAvailableCiv = []
		if gc.getBuildingInfo(iBuilding).getPrereqCiv() != CivilizationTypes.NO_CIVILIZATION:
			liAvailableCiv.append(gc.getBuildingInfo(iBuilding).getPrereqCiv())
		else:
			iBuildingClass = gc.getBuildingInfo(iBuilding).getBuildingClassType()
			for iCiv in range(gc.getNumCivilizationInfos()):
				iUniqueBuilding = gc.getCivilizationInfo(iCiv).getCivilizationBuildings(iBuildingClass)
				if iUniqueBuilding == iBuilding:
					liAvailableCiv.append(iCiv)

		return liAvailableCiv


	def getListUnitCivilization(self, iUnit):
		if iUnit == UnitTypes.NO_UNIT:
			return []

		liAvailableCiv = []
		if gc.getUnitInfo(iUnit).getPrereqCiv() != CivilizationTypes.NO_CIVILIZATION:
			liAvailableCiv.append(gc.getUnitInfo(iUnit).getPrereqCiv())
		else:
			iUnitClass = gc.getUnitInfo(iUnit).getUnitClassType()
			for iCiv in range(gc.getNumCivilizationInfos()):
				iUniqueUnit = gc.getCivilizationInfo(iCiv).getCivilizationUnits(iUnitClass)
				if iUniqueUnit == iUnit:
					liAvailableCiv.append(iCiv)

		return liAvailableCiv


	def getListTrainableBuilding(self, iBuildingClass, iUnit):
		liAvailableBuilding = []
		if not iBuildingClass == BuildingClassTypes.NO_BUILDINGCLASS:
			for iCiv in self.getListUnitCivilization(iUnit):
				iAvailableBuilding = gc.getCivilizationInfo(iCiv).getCivilizationBuildings(iBuildingClass)
				liAvailableBuilding.append(iAvailableBuilding)
			liAvailableBuilding = sorted(set(liAvailableBuilding), key=liAvailableBuilding.index)	#remove repeated items

		return liAvailableBuilding
##--------	BUGFfH: End Added
