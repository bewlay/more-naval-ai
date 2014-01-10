## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums

# globals
gc = CyGlobalContext()
g_pCity = None

class WBPromotionScreen:

	def __init__(self):
		self.iList = []
		self.iPromotionCategory = 0

	def isMagicSpherePromotion(self, pPromotion):
		iBonus = pPromotion.getBonusPrereq()

		# If the promotion itself requires mana, it is a magic sphere promotion.
		if iBonus != BonusTypes.NO_BONUS and gc.getBonusInfo(iBonus).getBonusClassType() == gc.getInfoTypeForString('BONUSCLASS_MANA'):
			return True

		lChannelingPromotions = [gc.getInfoTypeForString('PROMOTION_CHANNELING2'), gc.getInfoTypeForString('PROMOTION_CHANNELING3')]

		# If the current promotion requires channeling 2 or 3, it is possible that it is a magic sphere promotion if it also requires a magic sphere promotion.
		if (pPromotion.getPrereqPromotion() in lChannelingPromotions or pPromotion.getPromotionPrereqAnd() in lChannelingPromotions):
			iRequirementOther = PromotionTypes.NO_PROMOTION
			if pPromotion.getPrereqPromotion() not in lChannelingPromotions:
				iRequirementOther = pPromotion.getPrereqPromotion()
			elif pPromotion.getPromotionPrereqAnd() not in lChannelingPromotions:
				iRequirementOther = pPromotion.getPrereqPromotion()
			if iRequirementOther != PromotionTypes.NO_PROMOTION:
				return self.isMagicSpherePromotion(gc.getPromotionInfo(iRequirementOther))

		return False

	def interfaceScreen(self, pUnit):
		screen = CyGInterfaceScreen( "WBPromotionScreen", CvScreenEnums.WB_PROMOTION)
		global g_pUnit
		g_pUnit = pUnit

		self.nTableWidth = screen.getXResolution() - 40
		self.nTableHeight = screen.getYResolution() - 100
		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.setDimensions(0,0, screen.getXResolution(), screen.getYResolution())
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

		screen.setText("WBPromotionExit", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 25, screen.getYResolution() - 40, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		screen.setText("PromotionHeader", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION", ()) + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)


		szDropdownName = str("PromotionCategory")
		screen.addDropDownBoxGFC(szDropdownName, 20, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION", ()), 0, 0, self.iPromotionCategory == 0)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_SPELL_SPHERES", ()), 1, 1, self.iPromotionCategory == 1)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_EFFECTS", ()), 2, 2, self.iPromotionCategory == 2)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_RACES", ()), 3, 3, self.iPromotionCategory == 3)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_ITEMS", ()), 4, 4, self.iPromotionCategory == 4)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_SHOW_HIDDEN", ()), 5, 5, self.iPromotionCategory == 5)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_ALL", ()), 6, 6, self.iPromotionCategory == 6)



		szDropdownName = str("PromotionCommands")
		screen.addDropDownBoxGFC(szDropdownName, screen.getXResolution() - 200, 20, 180, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_COMMANDS", ()), 0, 0, True)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_GRANT_AVAILABLE", ()), 1, 1, False)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_GRANT_ALL", ()), 2, 2, False)
		screen.addPullDownString(szDropdownName, CyTranslator().getText("TXT_KEY_WB_CLEAR_ALL", ()), 3, 3, False)

		nColumns = 5
		screen.addTableControlGFC( "WBPromotion", nColumns, 20, 60, self.nTableWidth, self.nTableHeight, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		for i in xrange(nColumns):
			screen.setTableColumnHeader( "WBPromotion", i, "", self.nTableWidth/nColumns)

		self.iList = []
		for i in xrange(gc.getNumPromotionInfos()):
			ItemInfo = gc.getPromotionInfo(i)
			if self.iPromotionCategory == 6:#All
				self.iList.append([ItemInfo.getDescription(), i])
			if ItemInfo.isGraphicalOnly():
				if self.iPromotionCategory == 5:#Hidden
					self.iList.append([ItemInfo.getDescription(), i])
			elif ItemInfo.isEquipment():
				if self.iPromotionCategory == 4:#Equipment
					self.iList.append([ItemInfo.getDescription(), i])
			elif ItemInfo.isRace():
				if self.iPromotionCategory == 3:#Race
					self.iList.append([ItemInfo.getDescription(), i])
			elif ItemInfo.getMinLevel() < 0:
				if self.iPromotionCategory == 2:#Effect
					self.iList.append([ItemInfo.getDescription(), i])
			elif self.isMagicSpherePromotion(ItemInfo):
				if self.iPromotionCategory == 1:#Spell Spheres
					self.iList.append([ItemInfo.getDescription(), i])
			elif self.iPromotionCategory == 0:#Normal Promotions
				self.iList.append([ItemInfo.getDescription(), i])

		self.iList.sort()

		nRows = (len(self.iList) + nColumns - 1) / nColumns
		for i in xrange(nRows):
			screen.appendTableRow("WBPromotion")

		for iCount in xrange(len(self.iList)):
			item = self.iList[iCount]
			iRow = iCount % nRows
			iColumn = iCount / nRows
			ItemInfo = gc.getPromotionInfo(item[1])
			if pUnit.isHasPromotion(item[1]):
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			else:
				sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			screen.setTableText("WBPromotion", iColumn, iRow, sColor + item[0] + "</color>", ItemInfo.getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, item[1], 1, CvUtil.FONT_LEFT_JUSTIFY )

	def handleInput (self, inputClass):

		if inputClass.getFunctionName() == "PromotionCategory":
			self.handleMagisterPromotionCategoryCB(inputClass.getData())
			return 1


		if inputClass.getFunctionName() == "PromotionCommands":
			self.handlePlatyPromotionCommandsCB(inputClass.getData())
			return 1
		if inputClass.getData1() > -1 and inputClass.getData2() == 1:
			self.handlePlatySetPromotionCB(inputClass.getData1())
			return 1
		return 1


	def handleMagisterPromotionCategoryCB ( self, argsList ) :
		self.iPromotionCategory = int(argsList)
		self.interfaceScreen(g_pUnit)
		return 1


	def handlePlatySetPromotionCB (self, iData1) :
		g_pUnit.setHasPromotion(iData1, not g_pUnit.isHasPromotion(iData1))
		self.interfaceScreen(g_pUnit)
		return 1

	def handlePlatyPromotionCommandsCB(self, argsList):
		if int(argsList) == 1:
			for item in self.iList:
				if gc.getPromotionInfo(item[1]).isLeader(): continue
				if g_pUnit.canAcquirePromotion(item[1]):
					g_pUnit.setHasPromotion(item[1], True)
				self.interfaceScreen(g_pUnit)
		elif int(argsList) == 2:
			for item in self.iList:
				g_pUnit.setHasPromotion(item[1], True)
				self.interfaceScreen(g_pUnit)
		elif int(argsList) == 3:
			for item in self.iList:
				g_pUnit.setHasPromotion(item[1], False)
				self.interfaceScreen(g_pUnit)
		return 1



	def update(self, fDelta):
		return 1