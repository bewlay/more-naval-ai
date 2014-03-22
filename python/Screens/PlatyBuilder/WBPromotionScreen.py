from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import WBUnitScreen
import WBPlayerScreen
import WBTeamScreen
import WBPlotScreen
import WBEventScreen
import WBPlayerUnits
gc = CyGlobalContext()

iCopyType = 0
iEditType = 0
iChangeType = 0
iOwnerType = 0

class WBPromotionScreen:

	def __init__(self, main):
		self.top = main
		self.iCombatClass = -2
		self.iTable_Y = 110


		self.iStatus = 0#Magister
		self.iCategory = 1#Magister

	def interfaceScreen(self, pUnitX):
		screen = CyGInterfaceScreen( "WBPromotionScreen", CvScreenEnums.WB_PROMOTION)
		global pUnit
		global pPlot
		pUnit = pUnitX
		pPlot = pUnit.plot()

		screen.setRenderInterfaceOnly(True)
		screen.addPanel( "MainBG", u"", u"", True, False, -10, -10, screen.getXResolution() + 20, screen.getYResolution() + 20, PanelStyles.PANEL_STYLE_MAIN )
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
	
		screen.setText("WBPromotionExit", "Background", "<font=4>" + CyTranslator().getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 30, screen.getYResolution() - 42, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )
		screen.setLabel("PromotionHeader", "Background", "<font=4b>" + pUnit.getName() + "</font>", CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 20, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		sText = u"<font=3b>%s ID: %d, %s ID: %d</font>" %(CyTranslator().getText("TXT_KEY_WB_UNIT", ()), pUnit.getID(), CyTranslator().getText("TXT_KEY_WB_GROUP", ()), pUnit.getGroupID())
		screen.setLabel("PromotionHeaderB", "Background", sText, CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution()/2, 50, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		screen.addDropDownBoxGFC("OwnerType", 20, 20, screen.getXResolution()/4 - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("OwnerType", CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ()), 0, 0, 0 == iOwnerType)
		screen.addPullDownString("OwnerType", CyTranslator().getText("TXT_KEY_WB_OWNER", ()), 1, 1, 1 == iOwnerType)
		screen.addPullDownString("OwnerType", CyTranslator().getText("TXT_KEY_WB_TEAM", ()), 2, 2, 2 == iOwnerType)

		screen.addDropDownBoxGFC("CopyType", 20, 50, screen.getXResolution()/4 - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CopyType", CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ()), 0, 0, 0 == iCopyType)
		screen.addPullDownString("CopyType", CyTranslator().getText("TXT_PEDIA_TYPE", ()), 1, 1, 1 == iCopyType)
		screen.addPullDownString("CopyType", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT_COMBAT", ()), 2, 2, 2 == iCopyType)
		screen.addPullDownString("CopyType", CyTranslator().getText("TXT_KEY_PEDIA_DOMAIN", ()), 3, 3, 3 == iCopyType)
		screen.addPullDownString("CopyType", CyTranslator().getText("TXT_KEY_WB_GROUP", ()), 4, 4, 4 == iCopyType)

		screen.addDropDownBoxGFC("EditType", 20, 80, screen.getXResolution()/4 - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("EditType", CyTranslator().getText("TXT_KEY_WB_SINGLE_PLOT", ()), 0, 0, iEditType == 0)
		screen.addPullDownString("EditType", CyTranslator().getText("TXT_KEY_WB_AREA_PLOTS", ()), 1, 1, iEditType == 1)
		screen.addPullDownString("EditType", CyTranslator().getText("TXT_KEY_WB_ALL_PLOTS", ()), 2, 2, iEditType == 2)

		iX = screen.getXResolution()/4 + 20
		iWidth = 150
		screen.addDropDownBoxGFC("ChangeType", iX, screen.getYResolution() - 42, iWidth, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("ChangeType", CyTranslator().getText("TXT_KEY_WB_ADD", ()), 0, 0, 0 == iChangeType)
		screen.addPullDownString("ChangeType", CyTranslator().getText("TXT_KEY_WB_COPY", ()), 1, 1, 1 == iChangeType)
		screen.addPullDownString("ChangeType", CyTranslator().getText("TXT_KEY_WB_REMOVE", ()), 2, 2, 2 == iChangeType)

		iX += iWidth
		screen.setText("PromotionCopy", "Background", u"<font=3b>" + CyTranslator().getText("TXT_KEY_WB_COPY_ALL", (CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()),)) + "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX, screen.getYResolution() - 42, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		screen.addDropDownBoxGFC("CurrentPage", 20, screen.getYResolution() - 42, screen.getXResolution()/4 - 20, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_UNIT_DATA", ()), 0, 0, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION", ()), 1, 1, True)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_HELP4", ()), 2, 2, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_TEAM_DATA", ()), 3, 3, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_WB_HELP19", ()), 4, 4, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_CONCEPT_EVENTS", ()), 5, 5, False)
		screen.addPullDownString("CurrentPage", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()) + " + " + CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ()), 6, 6, False)

		screen.addDropDownBoxGFC("CombatClass", screen.getXResolution()/4 + 20, self.iTable_Y - 30, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("CombatClass", CyTranslator().getText("TXT_KEY_WB_CITY_ALL",()), -2, -2, -2 == self.iCombatClass)
		for iCombatClass in xrange(gc.getNumUnitCombatInfos()):
			screen.addPullDownString("CombatClass", gc.getUnitCombatInfo(iCombatClass).getDescription(), iCombatClass, iCombatClass, iCombatClass == self.iCombatClass)

#Magister
		screen.addDropDownBoxGFC("Category", screen.getXResolution()*45/100+20, self.iTable_Y - 30, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("Category", CyTranslator().getText("TXT_KEY_WB_CITY_ALL",()), 0, 0, 0 == self.iCategory)
		screen.addPullDownString("Category", CyTranslator().getText("TXT_KEY_WB_STANDARD_PROMOTIONS", ()), 1, 1, 1 == self.iCategory)
		screen.addPullDownString("Category", CyTranslator().getText("TXT_KEY_SPELL_SPHERES", ()), 2, 2, 2 == self.iCategory)
		screen.addPullDownString("Category", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_ITEMS", ()), 3, 3, 3 == self.iCategory)
		screen.addPullDownString("Category", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_EFFECTS", ()), 4, 4, 4 == self.iCategory)
		screen.addPullDownString("Category", CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_RACES", ()), 5, 5, 5 == self.iCategory)
		screen.addPullDownString("Category", CyTranslator().getText("TXT_KEY_WB_SHOW_HIDDEN", ()), 6, 6, 6 == self.iCategory)

		screen.addDropDownBoxGFC("Status", screen.getXResolution()*65/100+20, self.iTable_Y - 30, screen.getXResolution()/5, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
		screen.addPullDownString("Status", CyTranslator().getText("TXT_KEY_WB_CITY_ALL",()), 0, 0, 0 == self.iStatus)
		screen.addPullDownString("Status", CyTranslator().getText("TXT_KEY_WB_AVAILIBLE_PROMOTIONS",()), 1, 1, 1 == self.iStatus)
		screen.addPullDownString("Status", CyTranslator().getText("TXT_KEY_WB_CURRENT_PROMOTIONS",()), 2, 2, 2 == self.iStatus)
		screen.addPullDownString("Status", CyTranslator().getText("TXT_KEY_WB_LACKS_PROMOTIONS",()), 3, 3, 3 == self.iStatus)
#Magister

		screen.setLabel("PromotionAll", "Background", u"<font=4b>" + CyTranslator().getText("TXT_KEY_WB_CITY_ALL", ()) + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, screen.getXResolution() - 70, self.iTable_Y - 30, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setButtonGFC("PromotionAllPlus", "", "", screen.getXResolution() - 70, self.iTable_Y - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1030, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS)
		screen.setButtonGFC("PromotionAllMinus", "", "", screen.getXResolution() - 45, self.iTable_Y - 30, 24, 24, WidgetTypes.WIDGET_PYTHON, 1031, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS)
		
		self.sortUnits()
		self.sortPromotions()

	def sortUnits(self):
		screen = CyGInterfaceScreen( "WBPromotionScreen", CvScreenEnums.WB_PROMOTION)
		global lUnits
		lUnits = []
		for iPlayerX in xrange(gc.getMAX_PLAYERS()):
			if iOwnerType == 1 and iPlayerX != pUnit.getOwner(): continue
			if iOwnerType == 2 and iPlayerX != pUnit.getTeam(): continue
			pPlayerX = gc.getPlayer(iPlayerX)
			if pPlayerX.isAlive():
				(loopUnit, iter) = pPlayerX.firstUnit(False)
				while(loopUnit):
					bCopy = True
					if iEditType == 0:
						if loopUnit.getX() != pUnit.getX() or loopUnit.getY() != pUnit.getY():
							bCopy = False
					elif iEditType == 1:
						if loopUnit.plot().getArea() != pUnit.plot().getArea():
							bCopy = False
					if iCopyType == 1:
						if loopUnit.getUnitType() != pUnit.getUnitType():
							bCopy = False
					elif iCopyType == 2:
						if loopUnit.getUnitCombatType() != pUnit.getUnitCombatType():
							bCopy = False
					elif iCopyType == 3:
						if loopUnit.getDomainType() != pUnit.getDomainType():
							bCopy = False
					elif iCopyType == 4:
						if loopUnit.getGroupID() != pUnit.getGroupID():
							bCopy = False
					if bCopy:
						lUnits.append([loopUnit.getOwner(), loopUnit.getID()])
					(loopUnit, iter) = pPlayerX.nextUnit(iter, False)
		lUnits.sort()
		self.placeCurrentUnit()
		
	def placeCurrentUnit(self):
		screen = CyGInterfaceScreen( "WBPromotionScreen", CvScreenEnums.WB_PROMOTION)

		iMaxRows = (screen.getYResolution() - self.iTable_Y - 42) /24
		iHeight = iMaxRows * 24 + 2
		iWidth = screen.getXResolution()/4 - 20
		screen.addTableControlGFC("WBCurrentUnit", 3, 20, self.iTable_Y, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
		screen.setTableColumnHeader("WBCurrentUnit", 0, "", 24)
		screen.setTableColumnHeader("WBCurrentUnit", 1, "", 24)
		screen.setTableColumnHeader("WBCurrentUnit", 2, "", iWidth - 48)

		for i in lUnits:
			pPlayerX = gc.getPlayer(i[0])
			pUnitX = pPlayerX.getUnit(i[1])
			if pUnitX.isNone(): continue
			iRow = screen.appendTableRow("WBCurrentUnit")
			sText = pUnitX.getName()
			if len(pUnitX.getNameNoDesc()):
				sText = pUnitX.getNameNoDesc()
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if pUnitX.getOwner() == pUnit.getOwner():
				if pUnitX.getID() == pUnit.getID():
					sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
				elif pUnitX.getGroupID() == pUnit.getGroupID():
					sColor = CyTranslator().getText("[COLOR_YELLOW]", ())
			screen.setTableText("WBCurrentUnit", 2, iRow, "<font=3>" + sColor + sText + "</font></color>", pUnitX.getButton(), WidgetTypes.WIDGET_PYTHON, 8300 + i[0], i[1], CvUtil.FONT_LEFT_JUSTIFY)
			iLeader = pPlayerX.getLeaderType()
			iCiv = pUnitX.getCivilizationType()
			screen.setTableText("WBCurrentUnit", 0, iRow, "", gc.getCivilizationInfo(iCiv).getButton(), WidgetTypes.WIDGET_PYTHON, 7872, iCiv, CvUtil.FONT_LEFT_JUSTIFY )
			screen.setTableText("WBCurrentUnit", 1, iRow, "", gc.getLeaderHeadInfo(iLeader).getButton(), WidgetTypes.WIDGET_PYTHON, 7876, iLeader, CvUtil.FONT_LEFT_JUSTIFY )

	def sortPromotions(self):
		screen = CyGInterfaceScreen( "WBPromotionScreen", CvScreenEnums.WB_PROMOTION)
		global lList
		lList = []
		iChanneling2 = gc.getInfoTypeForString('PROMOTION_CHANNELING2')#For MNAI, not MagisterModmod
		iChanneling3 = gc.getInfoTypeForString('PROMOTION_CHANNELING3')#For MNAI, not MagisterModmod
		iMana = gc.getInfoTypeForString('BONUSCLASS_MANA')
		for i in xrange(gc.getNumPromotionInfos()):
#Magister
			if self.iStatus == 0:#All promptions
				pass
			elif self.iStatus == 1:#Availible promotions
				if not pUnit.canAcquirePromotion(i):continue
			elif self.iStatus == 2:#Current promotions
				if not pUnit.isHasPromotion(i):continue
			elif self.iStatus == 3:#Lacking promotions
				if pUnit.isHasPromotion(i):continue
			ItemInfo = gc.getPromotionInfo(i)
			if not (self.iCombatClass == -2 or ItemInfo.getUnitCombat(self.iCombatClass)):continue
			if self.iCategory == 0:#All
				lList.append([ItemInfo.getDescription(), i])
			elif self.iCategory == 1:#Standard Promotions
				if ItemInfo.isGraphicalOnly():continue
				if ItemInfo.isEquipment():continue
				if ItemInfo.getMinLevel() < 0:continue
				if ItemInfo.isRace():continue
				iBonus = ItemInfo.getBonusPrereq()
				if iBonus != -1:
					if gc.getBonusInfo(iBonus).getBonusClassType() == iMana:continue
				iPrereq = ItemInfo.getPromotionPrereqAnd()#For MNAI, not MagisterModmod
				if iPrereq == iChanneling2 or iPrereq == iChanneling3:continue#For MNAI, not MagisterModmod
				lList.append([ItemInfo.getDescription(), i])
			elif self.iCategory == 2:#Spell Spheres
				iBonus = ItemInfo.getBonusPrereq()
				if iBonus != -1:
					if gc.getBonusInfo(iBonus).getBonusClassType() == iMana:
						lList.append([ItemInfo.getDescription(), i])
				iPrereq = ItemInfo.getPromotionPrereqAnd()#For MNAI, not MagisterModmod
				if iPrereq == iChanneling2 or iPrereq == iChanneling3:#For MNAI, not MagisterModmod
					lList.append([ItemInfo.getDescription(), i])
			elif self.iCategory == 3:#Equipment
				if ItemInfo.isEquipment():
					lList.append([ItemInfo.getDescription(), i])
			elif self.iCategory == 4:#Effect
				if ItemInfo.getMinLevel() < 0:
					lList.append([ItemInfo.getDescription(), i])
			elif self.iCategory == 5:#Race
				if ItemInfo.isRace():
					lList.append([ItemInfo.getDescription(), i])
			elif self.iCategory == 6:#Hidden
				if ItemInfo.isGraphicalOnly():
					lList.append([ItemInfo.getDescription(), i])
#Magister
		lList.sort()
		self.placePromotions()

	def placePromotions(self):
		screen = CyGInterfaceScreen( "WBPromotionScreen", CvScreenEnums.WB_PROMOTION)
		iMaxRows = (screen.getYResolution() - self.iTable_Y - 42) /24
		nColumns = max(1, min(4, (len(lList) + iMaxRows - 1)/iMaxRows))
		iHeight = iMaxRows * 24 + 2
		iWidth = screen.getXResolution() *3/4 - 40
		screen.addTableControlGFC( "WBPromotion", nColumns, screen.getXResolution()/4 + 20, self.iTable_Y, iWidth, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD )
		for i in xrange(nColumns):
			screen.setTableColumnHeader("WBPromotion", i, "", iWidth/nColumns)

		nRows = (len(lList) + nColumns - 1) / nColumns
		for i in xrange(nRows):
			screen.appendTableRow("WBPromotion")

		for iCount in xrange(len(lList)):
			item = lList[iCount]
			iRow = iCount % nRows
			iColumn = iCount / nRows
			ItemInfo = gc.getPromotionInfo(item[1])
			sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
			if pUnit.isHasPromotion(item[1]):
				sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
			screen.setTableText("WBPromotion", iColumn, iRow, sColor + item[0] + "</color>", ItemInfo.getButton(), WidgetTypes.WIDGET_PYTHON, 7873, item[1], CvUtil.FONT_LEFT_JUSTIFY )

	def handleInput (self, inputClass):
		screen = CyGInterfaceScreen( "WBPromotionScreen", CvScreenEnums.WB_PROMOTION)
		global iChangeType
		global iEditType
		global iCopyType
		global iOwnerType

		if inputClass.getFunctionName() == "CurrentPage":
			iIndex = screen.getPullDownData("CurrentPage", screen.getSelectedPullDownID("CurrentPage"))
			if iIndex == 0:
				WBUnitScreen.WBUnitScreen(self.top).interfaceScreen(pUnit)
			elif iIndex == 2:
				WBPlayerScreen.WBPlayerScreen(self.top).interfaceScreen(pUnit.getOwner())
			elif iIndex == 3:
				WBTeamScreen.WBTeamScreen(self.top).interfaceScreen(pUnit.getTeam())
			elif iIndex == 4:
				WBPlotScreen.WBPlotScreen(self.top).interfaceScreen(pPlot)
			elif iIndex == 5:
				WBEventScreen.WBEventScreen(self.top).interfaceScreen(pPlot)
			elif iIndex == 6:
				WBPlayerUnits.WBPlayerUnits(self.top).interfaceScreen(pUnit.getOwner())

		elif inputClass.getFunctionName() == "ChangeType":
			iChangeType = screen.getPullDownData("ChangeType", screen.getSelectedPullDownID("ChangeType"))

		elif inputClass.getFunctionName() == "OwnerType":
			iOwnerType = screen.getPullDownData("OwnerType", screen.getSelectedPullDownID("OwnerType"))
			self.sortUnits()

		elif inputClass.getFunctionName() == "EditType":
			iEditType = screen.getPullDownData("OwnerType", screen.getSelectedPullDownID("EditType"))
			self.sortUnits()

		elif inputClass.getFunctionName() == "CopyType":
			iCopyType = screen.getPullDownData("CopyType", screen.getSelectedPullDownID("CopyType"))
			self.sortUnits()

		elif inputClass.getFunctionName() == "WBCurrentUnit":
			iPlayer = inputClass.getData1() - 8300
			self.interfaceScreen(gc.getPlayer(iPlayer).getUnit(inputClass.getData2()))

		elif inputClass.getFunctionName() == "CombatClass":
			iIndex = screen.getSelectedPullDownID("CombatClass")
			self.iCombatClass = screen.getPullDownData("CombatClass", iIndex)
			self.sortPromotions()

#Magister
		elif inputClass.getFunctionName() == "Status":
			iIndex = screen.getSelectedPullDownID("Status")
			self.iStatus = screen.getPullDownData("Status", iIndex)
			self.sortPromotions()

		elif inputClass.getFunctionName() == "Category":
			iIndex = screen.getSelectedPullDownID("Category")
			self.iCategory = screen.getPullDownData("Category", iIndex)
			self.sortPromotions()
#Magister

		elif inputClass.getFunctionName() == "WBPromotion":
			pUnit.setHasPromotion(inputClass.getData2(), not pUnit.isHasPromotion(inputClass.getData2()))
			self.placePromotions()

		elif inputClass.getFunctionName().find("PromotionAll") > -1:
			for item in lList:
				pUnit.setHasPromotion(item[1], not inputClass.getData1() %2)
			self.placePromotions()

		elif inputClass.getFunctionName() == "PromotionCopy":
			self.handleCopyAll()
		return 1

	def handleCopyAll(self):
		for i in lUnits:
			loopUnit = gc.getPlayer(i[0]).getUnit(i[1])
			if loopUnit.isNone(): continue
			for iPromotion in xrange(gc.getNumPromotionInfos()):
				if iChangeType == 0:
					if pUnit.isHasPromotion(iPromotion):
						loopUnit.setHasPromotion(iPromotion, True)
				elif iChangeType == 1:
					loopUnit.setHasPromotion(iPromotion, pUnit.isHasPromotion(iPromotion))
				elif iChangeType == 2:
					if not pUnit.isHasPromotion(iPromotion):
						loopUnit.setHasPromotion(iPromotion, False)		

	def update(self, fDelta):
		return 1