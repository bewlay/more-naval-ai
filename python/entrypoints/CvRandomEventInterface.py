# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005
#
# CvRandomEventInterface.py
#
# These functions are App Entry Points from C++
# WARNING: These function names should not be changed
# WARNING: These functions can not be placed into a class
#
# No other modules should import this
#
import CvUtil
from CvPythonExtensions import *
import CustomFunctions
import PyHelpers

cf = CustomFunctions.CustomFunctions()
gc = CyGlobalContext()
localText = CyTranslator()
PyPlayer = PyHelpers.PyPlayer

def canTriggerAeronsChosen(argsList):
	kTriggeredData = argsList[0]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pUnit = pPlayer.getUnit(kTriggeredData.iUnitId)
	if pUnit.getLevel() < 5:
		return False
	return True

def canTriggerAmuriteTrialUnit(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iUnit = argsList[2]
	pPlayer = gc.getPlayer(ePlayer)
	pUnit = pPlayer.getUnit(iUnit)
	if pUnit.isHiddenNationality() :
		return False
	return True

def applyAmuriteTrial1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pUnit = pPlayer.getUnit(kTriggeredData.iUnitId)
	iPlayer2 = cf.getCivilization(gc.getInfoTypeForString('CIVILIZATION_AMURITES'))
	if iPlayer2 != -1:
		pPlayer2 = gc.getPlayer(iPlayer2)
		pCity = pPlayer2.getCapitalCity()
		pUnit.setXY(pCity.getX(), pCity.getY(), false, true, true)

def doArmageddonApocalypse(argsList):
	kTriggeredData = argsList[0]
	iPlayer = argsList[1]
	iPercent = gc.getDefineINT('APOCALYPSE_KILL_CHANCE')
	pPlayer = gc.getPlayer(iPlayer)
	if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_FALLOW')) == False:
		for pyCity in PyPlayer(iPlayer).getCityList():
			pCity = pyCity.GetCy()
			iPop = pCity.getPopulation()
			iPop = int(iPop / 2)
			if iPop == 0:
				iPop = 1
			CvUtil.pyPrint('ARMAGEDDON! Setting %s to %d population' %(pyCity.getName(), iPop))
			pCity.setPopulation(iPop)
	pyPlayer = PyPlayer(iPlayer)
	apUnitList = pyPlayer.getUnitList()
	for pUnit in apUnitList:
		if (CyGame().getSorenRandNum(100, "Apocalypse") < iPercent):
			if pUnit.isAlive():
				pUnit.kill(False, PlayerTypes.NO_PLAYER)
				CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_APOCALYPSE_KILLED", ()),'',1,'Art/Interface/Buttons/Apocalypse.dds',ColorTypes(7),pUnit.getX(),pUnit.getY(),True,True)
	if pPlayer.isHuman():
		t = "TROPHY_FEAT_APOCALYPSE"
		if not CyGame().isHasTrophy(t):
			CyGame().changeTrophyValue(t, 1)

def doArmageddonArs(argsList):
	kTriggeredData = argsList[0]
	iUnit = gc.getInfoTypeForString('UNIT_ARS')
	if CyGame().getUnitCreatedCount(iUnit) == 0:
		cf.addUnit(iUnit)

def doArmageddonBlight(argsList):
	kTriggeredData = argsList[0]
	iPlayer = argsList[1]
	pPlayer = gc.getPlayer(iPlayer)
	py = PyPlayer(iPlayer)
	if pPlayer.getCivilizationType() != gc.getInfoTypeForString('CIVILIZATION_INFERNAL'):
		for pyCity in py.getCityList():
			pCity = pyCity.GetCy()
			i = CyGame().getSorenRandNum(15, "Blight")
#			i = 10
			i += pCity.getPopulation()
			i -= pCity.totalGoodBuildingHealth()
			if i > 0:
				pCity.changeEspionageHealthCounter(i)
	for pUnit in py.getUnitList():
		if pUnit.isAlive():
			pUnit.doDamageNoCaster(25, 100, gc.getInfoTypeForString('DAMAGE_DEATH'), false)

def doArmageddonBuboes(argsList):
	kTriggeredData = argsList[0]
	iUnit = gc.getInfoTypeForString('UNIT_BUBOES')
	if CyGame().getUnitCreatedCount(iUnit) == 0:
		cf.addUnit(iUnit)

def doArmageddonHellfire(argsList):
	kTriggeredData = argsList[0]
	iPlayer = argsList[1]
	if iPlayer == 0:
		iChampion = gc.getInfoTypeForString('UNIT_CHAMPION')
		iDemon = gc.getInfoTypeForString('PROMOTION_DEMON')
		iHellfire = gc.getInfoTypeForString('IMPROVEMENT_HELLFIRE')
		iHellfireChance = gc.getDefineINT('HELLFIRE_CHANCE')
		pPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
		for iPlayer2 in range(gc.getMAX_PLAYERS()):
			pPlayer2 = gc.getPlayer(iPlayer2)
			if (pPlayer2.isAlive()):
				if pPlayer2.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_INFERNAL'):
					pPlayer = pPlayer2
		for i in range (CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			if not pPlot.isWater():
				if pPlot.getNumUnits() == 0:
					if not pPlot.isCity():
						if pPlot.isFlatlands() and not pPlot.isImpassable():
							if pPlot.getBonusType(-1) == -1:
								if CyGame().getSorenRandNum(10000, "Hellfire") <= iHellfireChance:
									iImprovement = pPlot.getImprovementType()
									bValid = True
									if iImprovement != -1 :
										if gc.getImprovementInfo(iImprovement).isPermanent():
											bValid = False
									if bValid :
										pPlot.setImprovementType(iHellfire)
										newUnit = pPlayer.initUnit(iChampion, pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
										newUnit.setHasPromotion(iDemon, True)

def doArmageddonPestilence(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	if pPlayer.getCivilizationType() != gc.getInfoTypeForString('CIVILIZATION_INFERNAL'):
		for pyCity in PyPlayer(iPlayer).getCityList() :
			pCity = pyCity.GetCy()
			i = CyGame().getSorenRandNum(9, "Pestilence")
			i += (pCity.getPopulation() / 4)
			i -= pCity.totalGoodBuildingHealth()
			pCity.changeEspionageHealthCounter(i)
	py = PyPlayer(iPlayer)
	for pUnit in py.getUnitList():
		if pUnit.isAlive():
			pUnit.doDamageNoCaster(25, 100, gc.getInfoTypeForString('DAMAGE_DEATH'), false)

def doArmageddonStephanos(argsList):
	kTriggeredData = argsList[0]
	iUnit = gc.getInfoTypeForString('UNIT_STEPHANOS')
	if CyGame().getUnitCreatedCount(iUnit) == 0:
		cf.addUnit(iUnit)

def doArmageddonWrath(argsList):
	kTriggeredData = argsList[0]
	iPlayer = argsList[1]
	iEnraged = gc.getInfoTypeForString('PROMOTION_ENRAGED')
	iUnit = gc.getInfoTypeForString('UNIT_WRATH')
	iLand = gc.getInfoTypeForString('DOMAIN_LAND')
	iWrathConvertChance = gc.getDefineINT('WRATH_CONVERT_CHANCE')
	if CyGame().getUnitCreatedCount(iUnit) == 0:
		cf.addUnit(iUnit)
	pPlayer = gc.getPlayer(iPlayer)
	py = PyPlayer(iPlayer)
	for pUnit in py.getUnitList():
		if pUnit.getDomainType() == iLand:
			if pUnit.isAlive():
				if CyGame().getSorenRandNum(100, "Wrath") < iWrathConvertChance:
					if isWorldUnitClass(pUnit.getUnitClassType()) == False:
						pUnit.setHasPromotion(iEnraged, True)
						CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_WRATH_ENRAGED", ()),'',1,'Art/Interface/Buttons/Promotions/Enraged.dds',ColorTypes(7),pUnit.getX(),pUnit.getY(),True,True)

def doArmageddonYersinia(argsList):
	kTriggeredData = argsList[0]
	iUnit = gc.getInfoTypeForString('UNIT_YERSINIA')
	if CyGame().getUnitCreatedCount(iUnit) == 0:
		cf.addUnit(iUnit)

def doAzer(argsList):
	kTriggeredData = argsList[0]
	pPlot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	if pPlot.isNone() == False:
		bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
		newUnit = bPlayer.initUnit(gc.getInfoTypeForString('UNIT_AZER'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

def doBanditNietz3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_HORSEMAN'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit.setName("Nietz the Bandit Lord")
	newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_HERO'), True)
	newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_MOBILITY1'), True)

def helpBanditNietz3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	szHelp = localText.getText("TXT_KEY_EVENT_BANDIT_NIETZ_3_HELP", ())
	return szHelp

def doCalabimSanctuary1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	iPlayer2 = cf.getCivilization(gc.getInfoTypeForString('CIVILIZATION_CALABIM'))
	if iPlayer2 != -1:
		pPlayer2 = gc.getPlayer(iPlayer2)
		pPlayer2.AI_changeAttitudeExtra(iPlayer,-4)

def canTriggerCityFeud(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iCity = argsList[2]
	pPlayer = gc.getPlayer(ePlayer)
	pCity = pPlayer.getCity(iCity)
	if pCity.isCapital():
		return False
	return True

def doCityFeudArson(argsList):
	kTriggeredData = argsList[0]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCapitalCity()
	cf.doCityFire(pCity)

def doCityFeudStart1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	pCapitalCity = pPlayer.getCapitalCity()
	pCapitalCity.changeHappinessTimer(5)

def doCityFeudStart3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	pCapitalCity = pPlayer.getCapitalCity()
	pCapitalCity.changeOccupationTimer(5)

def helpCityFeudStart1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCapitalCity()
	szHelp = localText.getText("TXT_KEY_EVENT_CITY_FEUD_START_1_HELP", (pCity.getName(), ))
	return szHelp

def helpCityFeudStart3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCapitalCity()
	szHelp = localText.getText("TXT_KEY_EVENT_CITY_FEUD_START_3_HELP", (pCity.getName(), ))
	return szHelp

def canTriggerCitySplit(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iCity = argsList[2]
	pPlayer = gc.getPlayer(ePlayer)
	pCity = pPlayer.getCity(iCity)
	if pCity.isCapital():
		return False
	if pPlayer.getOpenPlayer() == -1:
		return False
	if CyGame().getWBMapScript():
		return False
	if pPlayer.hasTrait(gc.getInfoTypeForString('TRAIT_BARBARIAN')):
		return False
	iKoun = gc.getInfoTypeForString('LEADER_KOUN')
	for iPlayer in range(gc.getMAX_PLAYERS()):
		pLoopPlayer = gc.getPlayer(iPlayer)
		if pLoopPlayer.getLeaderType() == iKoun:
			return False
	return True

def doCitySplit1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	pSplitPlayer = cf.formEmpire(pPlayer.getCivilizationType(), gc.getInfoTypeForString('LEADER_KOUN'), TeamTypes.NO_TEAM, pCity, pPlayer.getAlignment(), pPlayer)
	pSplitPlayer.setParent(kTriggeredData.ePlayer)

def doSoverignCity1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	cf.formEmpire(pPlayer.getCivilizationType(), gc.getInfoTypeForString('LEADER_KOUN'), pPlayer.getTeam(), pCity, pPlayer.getAlignment(), pPlayer)

def doDissent1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	if gc.getGame().getSorenRandNum(100, "Dissent 1") < 50:
		pCity.changeOccupationTimer(2)
		CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_DISSENT_1", ()),'',1,'Art/Interface/Buttons/Actions/Pillage.dds',ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

def helpDissent1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	szHelp = localText.getText("TXT_KEY_EVENT_DISSENT_1_HELP", ())
	return szHelp

def doDissent2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	if gc.getGame().getSorenRandNum(100, "Dissent 2") < 50:
		pCity.changeOccupationTimer(4)
		CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_DISSENT_2_BAD", ()),'',1,'Art/Interface/Buttons/Actions/Pillage.dds',ColorTypes(7),pCity.getX(),pCity.getY(),True,True)
	else:
		pCity.changeHappinessTimer(5)
		CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_DISSENT_2_GOOD", ()),'',1,'Art/Interface/Buttons/General/happy_person.dds',ColorTypes(8),pCity.getX(),pCity.getY(),True,True)

def helpDissent2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	szHelp = localText.getText("TXT_KEY_EVENT_DISSENT_2_HELP", ())
	return szHelp

def canApplyDissent4(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	if pPlayer.getCivics(gc.getInfoTypeForString('CIVICOPTION_CULTURAL_VALUES')) != gc.getInfoTypeForString('CIVIC_SOCIAL_ORDER'):
		return False
	return True

def applyExploreLairDepths1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pUnit = pPlayer.getUnit(kTriggeredData.iUnitId)
	iRnd = CyGame().getSorenRandNum(100, "Explore Lair")
	if iRnd < 50:
		cf.exploreLairBigBad(pUnit)
	if iRnd >= 50:
		cf.exploreLairBigGood(pUnit)

def applyExploreLairDwarfVsLizardmen1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pUnit = pPlayer.getUnit(kTriggeredData.iUnitId)
	bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
	bBronze = False
	bPoison = False
	if bPlayer.isHasTech(gc.getInfoTypeForString('TECH_BRONZE_WORKING')):
		bBronze = True
	if bPlayer.isHasTech(gc.getInfoTypeForString('TECH_HUNTING')):
		bPoison = True
	pPlot = pUnit.plot()
	pNewPlot = cf.findClearPlot(-1, pPlot)
	if pNewPlot != -1:
		newUnit = bPlayer.initUnit(gc.getInfoTypeForString('UNIT_LIZARDMAN'), pNewPlot.getX(), pNewPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
		newUnit2 = bPlayer.initUnit(gc.getInfoTypeForString('UNIT_LIZARDMAN'), pNewPlot.getX(), pNewPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
		newUnit3 = bPlayer.initUnit(gc.getInfoTypeForString('UNIT_LIZARDMAN'), pNewPlot.getX(), pNewPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
		if bPoison:
			newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_POISONED_BLADE'), True)
			newUnit2.setHasPromotion(gc.getInfoTypeForString('PROMOTION_POISONED_BLADE'), True)
			newUnit3.setHasPromotion(gc.getInfoTypeForString('PROMOTION_POISONED_BLADE'), True)
		newUnit4 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_AXEMAN'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
		newUnit4.setHasPromotion(gc.getInfoTypeForString('PROMOTION_DWARF'), True)
		newUnit5 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_AXEMAN'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
		newUnit5.setHasPromotion(gc.getInfoTypeForString('PROMOTION_DWARF'), True)
		if bBronze:
			newUnit4.setHasPromotion(gc.getInfoTypeForString('PROMOTION_BRONZE_WEAPONS'), True)
			newUnit5.setHasPromotion(gc.getInfoTypeForString('PROMOTION_BRONZE_WEAPONS'), True)

def applyExploreLairDwarfVsLizardmen2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pUnit = pPlayer.getUnit(kTriggeredData.iUnitId)
	bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
	bBronze = False
	bPoison = False
	if bPlayer.isHasTech(gc.getInfoTypeForString('TECH_BRONZE_WORKING')):
		bBronze = True
	if bPlayer.isHasTech(gc.getInfoTypeForString('TECH_HUNTING')):
		bPoison = True
	pPlot = pUnit.plot()
	pNewPlot = cf.findClearPlot(-1, pPlot)
	if pNewPlot != -1:
		newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_LIZARDMAN'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
		newUnit2 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_LIZARDMAN'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
		if bPoison:
			newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_POISONED_BLADE'), True)
			newUnit2.setHasPromotion(gc.getInfoTypeForString('PROMOTION_POISONED_BLADE'), True)
		newUnit3 = bPlayer.initUnit(gc.getInfoTypeForString('UNIT_AXEMAN'), pNewPlot.getX(), pNewPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
		newUnit3.setHasPromotion(gc.getInfoTypeForString('PROMOTION_DWARF'), True)
		newUnit4 = bPlayer.initUnit(gc.getInfoTypeForString('UNIT_AXEMAN'), pNewPlot.getX(), pNewPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
		newUnit4.setHasPromotion(gc.getInfoTypeForString('PROMOTION_DWARF'), True)
		newUnit5 = bPlayer.initUnit(gc.getInfoTypeForString('UNIT_AXEMAN'), pNewPlot.getX(), pNewPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
		newUnit5.setHasPromotion(gc.getInfoTypeForString('PROMOTION_DWARF'), True)
		if bBronze:
			newUnit3.setHasPromotion(gc.getInfoTypeForString('PROMOTION_BRONZE_WEAPONS'), True)
			newUnit4.setHasPromotion(gc.getInfoTypeForString('PROMOTION_BRONZE_WEAPONS'), True)
			newUnit5.setHasPromotion(gc.getInfoTypeForString('PROMOTION_BRONZE_WEAPONS'), True)

def applyExploreLairPortal1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pUnit = pPlayer.getUnit(kTriggeredData.iUnitId)
	iBestValue = 0
	pBestPlot = -1
	for i in range (CyMap().numPlots()):
		iValue = 0
		pPlot = CyMap().plotByIndex(i)
		if not pPlot.isWater():
			if not pPlot.isPeak():
				if pPlot.getNumUnits() == 0:
					iValue = CyGame().getSorenRandNum(1000, "Portal")
					if not pPlot.isOwned():
						iValue += 1000
					if iValue > iBestValue:
						iBestValue = iValue
						pBestPlot = pPlot
	if pBestPlot != -1:
		pUnit.setXY(pBestPlot.getX(), pBestPlot.getY(), false, true, true)
		CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_PORTAL",()),'',1,'Art/Interface/Buttons/Spells/Explore Lair.dds',ColorTypes(8),pBestPlot.getX(),pBestPlot.getY(),True,True)

def doFlareEntropyNode(argsList):
	kTriggeredData = argsList[0]
	pPlot = CyMap().plot(kTriggeredData.iPlotX,kTriggeredData.iPlotY)
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL1'),point)
	CyAudioGame().Play3DSound("AS3D_SPELL_DEFILE",point.x,point.y,point.z)
	for iX in range(kTriggeredData.iPlotX-1, kTriggeredData.iPlotX+2, 1):
		for iY in range(kTriggeredData.iPlotY-1, kTriggeredData.iPlotY+2, 1):
			pPlot = CyMap().plot(iX,iY)
			if pPlot.isNone() == False:
				pPlot.changePlotCounter(100)
	CyGame().changeGlobalCounter(2)

def doFlareFireNode(argsList):
	kTriggeredData = argsList[0]
	pPlot = CyMap().plot(kTriggeredData.iPlotX,kTriggeredData.iPlotY)
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_ARTILLERY_SHELL_EXPLODE'),point)
	CyAudioGame().Play3DSound("AS3D_UN_GRENADE_EXPLODE",point.x,point.y,point.z)
	iFlames = gc.getInfoTypeForString('FEATURE_FLAMES')
	iForest = gc.getInfoTypeForString('FEATURE_FOREST')
	iJungle = gc.getInfoTypeForString('FEATURE_JUNGLE')
	for iX in range(kTriggeredData.iPlotX-1, kTriggeredData.iPlotX+2, 1):
		for iY in range(kTriggeredData.iPlotY-1, kTriggeredData.iPlotY+2, 1):
			pPlot = CyMap().plot(iX,iY)
			if pPlot.isNone() == False:
				if (pPlot.getFeatureType() == iForest or pPlot.getFeatureType() == iJungle):
					pPlot.setFeatureType(iFlames, 0)
					if pPlot.isOwned():
						CyInterface().addMessage(pPlot.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_FLAMES", ()),'',1,'Art/Interface/Buttons/Fire.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)

def doFlareLifeNode(argsList):
	kTriggeredData = argsList[0]
	pPlot = CyMap().plot(kTriggeredData.iPlotX,kTriggeredData.iPlotY)
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL1'),point)
	CyAudioGame().Play3DSound("AS3D_SPELL_SANCTIFY",point.x,point.y,point.z)
	for iX in range(kTriggeredData.iPlotX-2, kTriggeredData.iPlotX+3, 1):
		for iY in range(kTriggeredData.iPlotY-2, kTriggeredData.iPlotY+3, 1):
			pPlot = CyMap().plot(iX,iY)
			if pPlot.isNone() == False:
				pPlot.changePlotCounter(-100)
	CyGame().changeGlobalCounter(-2)

def doFlareNatureNode(argsList):
	kTriggeredData = argsList[0]
	pPlot = CyMap().plot(kTriggeredData.iPlotX,kTriggeredData.iPlotY)
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_BLOOM'),point)
	CyAudioGame().Play3DSound("AS3D_SPELL_BLOOM",point.x,point.y,point.z)
	iForestNew = gc.getInfoTypeForString('FEATURE_FOREST_NEW')
	for iX in range(kTriggeredData.iPlotX-1, kTriggeredData.iPlotX+2, 1):
		for iY in range(kTriggeredData.iPlotY-1, kTriggeredData.iPlotY+2, 1):
			pPlot = CyMap().plot(iX,iY)
			if pPlot.isNone() == False:
				if (pPlot.getImprovementType() == -1 and pPlot.getFeatureType() == -1 and pPlot.isWater() == False):
					if not pPlot.isPeak():
						pPlot.setFeatureType(iForestNew, 0)

def doFlareWaterNode(argsList):
	kTriggeredData = argsList[0]
	pPlot = CyMap().plot(kTriggeredData.iPlotX,kTriggeredData.iPlotY)
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPRING'),point)
	CyAudioGame().Play3DSound("AS3D_SPELL_SPRING",point.x,point.y,point.z)
	iFlames = gc.getInfoTypeForString('FEATURE_FLAMES')
	iDesert = gc.getInfoTypeForString('TERRAIN_DESERT')
	iSmoke = gc.getInfoTypeForString('IMPROVEMENT_SMOKE')
	iPlains = gc.getInfoTypeForString('TERRAIN_PLAINS')
	for iX in range(kTriggeredData.iPlotX-1, kTriggeredData.iPlotX+2, 1):
		for iY in range(kTriggeredData.iPlotY-1, kTriggeredData.iPlotY+2, 1):
			pPlot = CyMap().plot(iX,iY)
			if pPlot.isNone() == False:
				if pPlot.getTerrainType() == iDesert:
					pPlot.setTerrainType(iPlains,True,True)
				if pPlot.getFeatureType() == iFlames:
					pPlot.setFeatureType(-1, -1)
				if pPlot.getImprovementType() == iSmoke:
					pPlot.setImprovementType(-1)

def canTriggerPlotEmpty(argsList):
	kTriggeredData = argsList[0]
	pPlot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	if pPlot.isNone():
		return False
	if pPlot.getNumUnits() > 0:
		return False	
	return True

def canTriggerFoodSicknessUnit(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iUnit = argsList[2]
	pPlayer = gc.getPlayer(ePlayer)
	pUnit = pPlayer.getUnit(iUnit)
	if not pUnit.isAlive():
		return False
	return True

def doFoodSickness(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pUnit = pPlayer.getUnit(kTriggeredData.iUnitId)
	iDmg = pUnit.getDamage() + 20
	if iDmg > 99:
		iDmg = 99
	pUnit.setDamage(iDmg, PlayerTypes.NO_PLAYER)
	pUnit.changeImmobileTimer(2)

def doFrostling(argsList):
	kTriggeredData = argsList[0]
	pPlot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	if pPlot.isNone() == False:
		bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
		newUnit = bPlayer.initUnit(gc.getInfoTypeForString('UNIT_FROSTLING'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

def doGodslayer(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	cf.placeTreasure(iPlayer, gc.getInfoTypeForString('EQUIPMENT_GODSLAYER'))

def doGovernorAssassination(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	bMatch = False
	iCivic = pPlayer.getCivics(gc.getInfoTypeForString('CIVICOPTION_GOVERNMENT'))
	if iCivic != gc.getInfoTypeForString('CIVIC_DESPOTISM'):
		if iCivic == gc.getInfoTypeForString('CIVIC_GOD_KING'):
			bMatch = True
		if iCivic == gc.getInfoTypeForString('CIVIC_ARISTOCRACY'):
			if iEvent == gc.getInfoTypeForString('EVENT_GOVERNOR_ASSASSINATION_1'):
				bMatch = True
		if iCivic == gc.getInfoTypeForString('CIVIC_CITY_STATES') or iCivic == gc.getInfoTypeForString('CIVIC_REPUBLIC'):
			if iEvent == gc.getInfoTypeForString('EVENT_GOVERNOR_ASSASSINATION_3'):
				bMatch = True
		if iCivic == gc.getInfoTypeForString('CIVIC_THEOCRACY'):
			if iEvent == gc.getInfoTypeForString('EVENT_GOVERNOR_ASSASSINATION_4'):
				bMatch = True
		if bMatch == True:
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_PEOPLE_APPROVE", ()),'',1,'Art/Interface/Buttons/General/happy_person.dds',ColorTypes(8),pCity.getX(),pCity.getY(),True,True)
			pCity.changeHappinessTimer(3)
		else:
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_JUDGEMENT_WRONG", ()),'',1,'Art/Interface/Buttons/General/unhealthy_person.dds',ColorTypes(7),pCity.getX(),pCity.getY(),True,True)
			pCity.changeHurryAngerTimer(3)

def doGuildOfTheNineMerc41(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_MERCENARY'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_ELF'), True)
	newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_WOODSMAN1'), True)
	newUnit2 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_LONGBOWMAN'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit2.setHasPromotion(gc.getInfoTypeForString('PROMOTION_ELF'), True)
	newUnit2.setHasPromotion(gc.getInfoTypeForString('PROMOTION_DEXTEROUS'), True)
	newUnit3 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_RANGER'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit3.setHasPromotion(gc.getInfoTypeForString('PROMOTION_ELF'), True)
	newUnit3.setHasPromotion(gc.getInfoTypeForString('PROMOTION_SINISTER'), True)

def canTriggerGuildOfTheNineMerc5(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iCity = argsList[2]
	pPlayer = gc.getPlayer(ePlayer)
	pCity = pPlayer.getCity(iCity)
	if pCity.isCoastal(10) == False:
		return False
	return True

def doGuildOfTheNineMerc51(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_MERCENARY'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_AMPHIBIOUS'), True)
	newUnit2 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_BOARDING_PARTY'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit3 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_PRIVATEER'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit3.setHasPromotion(gc.getInfoTypeForString('PROMOTION_HIDDEN_NATIONALITY'), True)

def doGuildOfTheNineMerc61(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_MERCENARY'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_MUTATED'), True)
	newUnit2 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_TASKMASTER'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit3 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_HUNTER'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit3.setUnitArtStyleType(gc.getInfoTypeForString('UNIT_ARTSTYLE_BALSERAPHS'))

def doGuildOfTheNineMerc71(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_MERCENARY'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_DEFENSIVE'), True)
	newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_DWARF'), True)
	newUnit2 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_CHAMPION'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit2.setHasPromotion(gc.getInfoTypeForString('PROMOTION_DWARF'), True)
	newUnit3 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_DWARVEN_CANNON'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

def doGuildOfTheNineMerc81(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_MERCENARY'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_ORC'), True)
	newUnit2 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_OGRE'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit3 = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_LIZARDMAN'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

def doGreatBeastGurid(argsList):
	kTriggeredData = argsList[0]
	iUnit = gc.getInfoTypeForString('UNIT_GURID')
	if CyGame().getUnitCreatedCount(iUnit) == 0:
		cf.addUnit(iUnit)

def doGreatBeastLeviathan(argsList):
	kTriggeredData = argsList[0]
	iUnit = gc.getInfoTypeForString('UNIT_LEVIATHAN')
	if CyGame().getUnitCreatedCount(iUnit) == 0:
		pBestPlot = -1
		iBestPlot = -1
		for i in range (CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			iPlot = -1
			if pPlot.isWater():
				if pPlot.getNumUnits() == 0:
					iPlot = CyGame().getSorenRandNum(500, "Leviathan")
					iPlot = iPlot + (pPlot.area().getNumTiles() * 10)
			if iPlot > iBestPlot:
				iBestPlot = iPlot
				pBestPlot = pPlot
		if iBestPlot != -1:
			bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
			newUnit = bPlayer.initUnit(iUnit, pBestPlot.getX(), pBestPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

def doGreatBeastMargalard(argsList):
	kTriggeredData = argsList[0]
	iUnit = gc.getInfoTypeForString('UNIT_MARGALARD')
	if CyGame().getUnitCreatedCount(iUnit) == 0:
		cf.addUnit(iUnit)

def applyHyboremsWhisper1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = cf.getAshenVeilCity(1)
	pPlayer.acquireCity(pCity,false,false)

def helpHyboremsWhisper1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pCity = cf.getAshenVeilCity(1)
	szHelp = localText.getText("TXT_KEY_EVENT_HYBOREMS_WHISPER_HELP", (pCity.getName(), ))
	return szHelp

def applyHyboremsWhisper2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = cf.getAshenVeilCity(2)
	pPlayer.acquireCity(pCity,false,false)

def helpHyboremsWhisper2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pCity = cf.getAshenVeilCity(2)
	szHelp = localText.getText("TXT_KEY_EVENT_HYBOREMS_WHISPER_HELP", (pCity.getName(), ))
	return szHelp

def applyHyboremsWhisper3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = cf.getAshenVeilCity(3)
	pPlayer.acquireCity(pCity,false,false)

def helpHyboremsWhisper3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pCity = cf.getAshenVeilCity(3)
	szHelp = localText.getText("TXT_KEY_EVENT_HYBOREMS_WHISPER_HELP", (pCity.getName(), ))
	return szHelp

def applyIronOrb3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	szBuffer = localText.getText("TXT_KEY_EVENT_IRON_ORB_3_RESULT", ())
	pPlayer.chooseTech(1, szBuffer, True)

def doJudgementRight(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_JUDGEMENT_RIGHT", ()),'',1,'Art/Interface/Buttons/General/happy_person.dds',ColorTypes(8),pCity.getX(),pCity.getY(),True,True)
	pCity.changeHappinessTimer(10)

def doJudgementWrong(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_JUDGEMENT_WRONG", ()),'',1,'Art/Interface/Buttons/General/unhealthy_person.dds',ColorTypes(7),pCity.getX(),pCity.getY(),True,True)
	pCity.changeCrime(3)

def doLetumFrigus3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pPlayer.setHasTrait(gc.getInfoTypeForString('TRAIT_AGGRESSIVE'),True)

def helpLetumFrigus3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	szHelp = localText.getText("TXT_KEY_EVENT_LETUM_FRIGUS_3_HELP", ())
	return szHelp

def canTriggerLunaticCity(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iCity = argsList[2]
	pPlayer = gc.getPlayer(ePlayer)
	pCity = pPlayer.getCity(iCity)
	iReligion = pPlayer.getStateReligion()
	iTemple = -1
	if iReligion == gc.getInfoTypeForString('RELIGION_THE_ORDER'):
		iTemple = gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_ORDER')
	if iReligion == gc.getInfoTypeForString('RELIGION_FELLOWSHIP_OF_LEAVES'):
		iTemple = gc.getInfoTypeForString('BUILDING_TEMPLE_OF_LEAVES')
	if iReligion == gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL'):
		iTemple = gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_VEIL')
	if iReligion == gc.getInfoTypeForString('RELIGION_OCTOPUS_OVERLORDS'):
		iTemple = gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_OVERLORDS')
	if iReligion == gc.getInfoTypeForString('RELIGION_RUNES_OF_KILMORPH'):
		iTemple = gc.getInfoTypeForString('BUILDING_TEMPLE_OF_KILMORPH')
	if iReligion == gc.getInfoTypeForString('RELIGION_THE_EMPYREAN'):
		iTemple = gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_EMPYREAN')
	if iTemple == -1:
		return False
	if pCity.getNumRealBuilding(iTemple) == 0:
		return False
	return True

def doMachineParts1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_CLOCKWORK_GOLEM'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_WEAK'), True)

def doMachineParts2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_CLOCKWORK_GOLEM'), pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_STRONG'), True)

def applyMalakimPilgrimage1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pUnit = pPlayer.getUnit(kTriggeredData.iUnitId)
	iPlayer2 = cf.getCivilization(gc.getInfoTypeForString('CIVILIZATION_MALAKIM'))
	if iPlayer2 != -1:
		pPlayer2 = gc.getPlayer(iPlayer2)
		pCity = pPlayer2.getCapitalCity()
		pUnit.setXY(pCity.getX(), pCity.getY(), false, true, true)

def doMarketTheft2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	iRnd = gc.getGame().getSorenRandNum(21, "Market Theft 2") - 10
	pCity.changeCrime(iRnd)

def helpMarketTheft2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	szHelp = localText.getText("TXT_KEY_EVENT_MARKET_THEFT_2_HELP", ())
	return szHelp

def canTriggerMerchantKeep(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iCity = argsList[2]
	pPlayer = gc.getPlayer(ePlayer)
	pCity = pPlayer.getCity(iCity)
	if pCity.getSpecialistCount(gc.getInfoTypeForString('SPECIALIST_GREAT_MERCHANT')) == 0:
		return False
	return True

def doMistforms(argsList):
	kTriggeredData = argsList[0]
	pPlot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
	iMistform = gc.getInfoTypeForString('UNIT_MISTFORM')
	newUnit1 = bPlayer.initUnit(iMistform, pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit2 = bPlayer.initUnit(iMistform, pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
	newUnit3 = bPlayer.initUnit(iMistform, pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

def doMushrooms(argsList):
	kTriggeredData = argsList[0]
	pPlot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	pPlot.setImprovementType(gc.getInfoTypeForString('IMPROVEMENT_MUSHROOMS'))

def canTriggerMutateUnit(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iUnit = argsList[2]
	pPlayer = gc.getPlayer(ePlayer)
	pUnit = pPlayer.getUnit(iUnit)
	iMutated = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_MUTATED')
	if pUnit.isHasPromotion(iMutated):
		return False
	return True

def canApplyNoOrder(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	if pPlayer.getStateReligion() == gc.getInfoTypeForString('RELIGION_THE_ORDER'):
		return False
	return True

def doOrderVsVeil1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	pCity.changeOccupationTimer(1)
	iOrder = gc.getInfoTypeForString('RELIGION_THE_ORDER')
	iVeil = gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL')
	if pCity.isHolyCityByType(iVeil) == False:
		if gc.getGame().getSorenRandNum(100, "Order vs Veil 1") < 50:
			pCity.setHasReligion(iVeil, False, False, False)
	(loopCity, iter) = pPlayer.firstCity(false)
	while(loopCity):
		if loopCity.isHasReligion(iOrder):
			loopCity.changeHappinessTimer(5)
		if loopCity.isHasReligion(iVeil):
			loopCity.changeHurryAngerTimer(5)
		(loopCity, iter) = pPlayer.nextCity(iter, false)

def doOrderVsVeil2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	pCity.changeOccupationTimer(1)
	iOrder = gc.getInfoTypeForString('RELIGION_THE_ORDER')
	iVeil = gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL')
	if pCity.isHolyCityByType(iOrder) == False:
		if gc.getGame().getSorenRandNum(100, "Order vs Veil 2") < 50:
			pCity.setHasReligion(iOrder, False, False, False)
	(loopCity, iter) = pPlayer.firstCity(false)
	while(loopCity):
		if loopCity.isHasReligion(iVeil):
			loopCity.changeHappinessTimer(5)
		if loopCity.isHasReligion(iOrder):
			loopCity.changeHurryAngerTimer(5)
		(loopCity, iter) = pPlayer.nextCity(iter, false)

def doOrderVsVeil3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	pCity.changeOccupationTimer(3)
	iOrder = gc.getInfoTypeForString('RELIGION_THE_ORDER')
	iVeil = gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL')
	if pCity.isHolyCityByType(iVeil) == False:
		if gc.getGame().getSorenRandNum(100, "Order vs Veil 3") < 25:
			pCity.setHasReligion(iVeil, False, False, False)
	if pCity.isHolyCityByType(iOrder) == False:
		if gc.getGame().getSorenRandNum(100, "Order vs Veil 3") < 25:
			pCity.setHasReligion(iOrder, False, False, False)
	if gc.getGame().getSorenRandNum(100, "Order vs Veil 3") < 50:
		pCity.changePopulation(-1)

def canApplyOrderVsVeil4(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	if pCity.getNumRealBuilding(gc.getInfoTypeForString('BUILDING_DUNGEON')) == 0:
		return False
	return True

def helpOrderVsVeil1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	szHelp = localText.getText("TXT_KEY_EVENT_ORDER_VS_VEIL_1_HELP", ())
	return szHelp

def helpOrderVsVeil2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	szHelp = localText.getText("TXT_KEY_EVENT_ORDER_VS_VEIL_2_HELP", ())
	return szHelp

def helpOrderVsVeil3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	szHelp = localText.getText("TXT_KEY_EVENT_ORDER_VS_VEIL_3_HELP", ())
	return szHelp

def doOrderVsVeilTemple1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	pCity.changeOccupationTimer(1)
	iOrder = gc.getInfoTypeForString('RELIGION_THE_ORDER')
	iVeil = gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL')
	pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_VEIL'), 0)
	if pCity.isHolyCityByType(iVeil) == False:
		if gc.getGame().getSorenRandNum(100, "Order vs Veil Temple 1") < 50:
			pCity.setHasReligion(iVeil, False, False, False)
	(loopCity, iter) = pPlayer.firstCity(false)
	while(loopCity):
		if loopCity.isHasReligion(iOrder):
			loopCity.changeHappinessTimer(5)
		if loopCity.isHasReligion(iVeil):
			loopCity.changeHurryAngerTimer(5)
		(loopCity, iter) = pPlayer.nextCity(iter, false)

def doOrderVsVeilTemple2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	pCity.changeOccupationTimer(1)
	iVeil = gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL')
	if gc.getGame().getSorenRandNum(100, "Order vs Veil Temple 2") < 50:
		pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_VEIL'), 0)
	if pCity.isHolyCityByType(iVeil) == False:
		if gc.getGame().getSorenRandNum(100, "Order vs Veil Temple 2") < 50:
			pCity.setHasReligion(iVeil, False, False, False)
	if gc.getGame().getSorenRandNum(100, "Order vs Veil Temple 2") < 50:
		pCity.changePopulation(-1)

def doOrderVsVeilTemple3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	pCity.changeOccupationTimer(3)
	iOrder = gc.getInfoTypeForString('RELIGION_THE_ORDER')
	iVeil = gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL')
	(loopCity, iter) = pPlayer.firstCity(false)
	while(loopCity):
		if loopCity.isHasReligion(iVeil):
			loopCity.changeHappinessTimer(5)
		if loopCity.isHasReligion(iOrder):
			loopCity.changeHurryAngerTimer(5)
		(loopCity, iter) = pPlayer.nextCity(iter, false)

def helpOrderVsVeilTemple1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	szHelp = localText.getText("TXT_KEY_EVENT_ORDER_VS_VEIL_TEMPLE_1_HELP", ())
	return szHelp

def helpOrderVsVeilTemple2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	szHelp = localText.getText("TXT_KEY_EVENT_ORDER_VS_VEIL_TEMPLE_2_HELP", ())
	return szHelp

def helpOrderVsVeilTemple3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	szHelp = localText.getText("TXT_KEY_EVENT_ORDER_VS_VEIL_TEMPLE_3_HELP", ())
	return szHelp

def canTriggerParith(argsList):
	kTriggeredData = argsList[0]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	if not pPlayer.isHuman():
		return False
	if CyGame().getTrophyValue("TROPHY_WB_SPLINTERED_COURT_PARITH") != 1:
		return False
	if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_WB_THE_SPLINTERED_COURT):
		return False
	return True

def applyParithYes(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	player = gc.getPlayer(kTriggeredData.ePlayer)
	pUnit = player.getUnit(kTriggeredData.iUnitId)
	CyGame().setTrophyValue("TROPHY_WB_SPLINTERED_COURT_PARITH", pUnit.getUnitType())

def canTriggerPenguins(argsList):
	kTriggeredData = argsList[0]
	pPlot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	if pPlot.isAdjacentToWater() == False:
		return False
	if pPlot.isPeak():
		return False
	return True

def doPenguins(argsList):
	kTriggeredData = argsList[0]
	pPlot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	pPlot.setImprovementType(gc.getInfoTypeForString('IMPROVEMENT_PENGUINS'))

def canTriggerPickAlignment(argsList):
	kTriggeredData = argsList[0]
	if CyGame().getWBMapScript():
		return False
	return True

def doPickAlignment1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pPlayer.setAlignment(gc.getInfoTypeForString('ALIGNMENT_GOOD'))

def doPickAlignment2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pPlayer.setAlignment(gc.getInfoTypeForString('ALIGNMENT_NEUTRAL'))

def doPickAlignment3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pPlayer.setAlignment(gc.getInfoTypeForString('ALIGNMENT_EVIL'))

def doPigGiant3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	pPlot = cf.findClearPlot(-1, pCity.plot())
	if pPlot != -1:
		bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
		newUnit = bPlayer.initUnit(gc.getInfoTypeForString('UNIT_HILL_GIANT'), pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.DIRECTION_SOUTH)
		newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_COMMANDO'), True)

def applyPronCapria(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_CAPRIA'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		pPlayer2.AI_changeAttitudeExtra(iPlayer,4)
		cf.addPlayerPopup(CyTranslator().getText("TXT_KEY_EVENT_PRON_CAPRIA_POPUP",()), iPlayer)

def canTriggerPronCapria(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iTeam = pPlayer.getTeam()
	eTeam = gc.getTeam(iTeam)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_CAPRIA'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		iTeam2 = pPlayer2.getTeam()
		if eTeam.isHasMet(iTeam2):
			if pPlayer2.AI_getAttitude(iPlayer) == gc.getInfoTypeForString('ATTITUDE_FRIENDLY'):
				return True
	return False

def applyPronEthne(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_ETHNE'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		pPlayer2.AI_changeAttitudeExtra(iPlayer,4)
		cf.addPlayerPopup(CyTranslator().getText("TXT_KEY_EVENT_PRON_ETHNE_POPUP",()), iPlayer)

def canTriggerPronEthne(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iTeam = pPlayer.getTeam()
	eTeam = gc.getTeam(iTeam)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_ETHNE'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		iTeam2 = pPlayer2.getTeam()
		if eTeam.isHasMet(iTeam2):
			if pPlayer2.AI_getAttitude(iPlayer) == gc.getInfoTypeForString('ATTITUDE_FRIENDLY'):
				return True
	return False

def applyPronArendel(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_ARENDEL'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		pPlayer2.AI_changeAttitudeExtra(iPlayer,4)
		cf.addPlayerPopup(CyTranslator().getText("TXT_KEY_EVENT_PRON_ARENDEL_POPUP",()), iPlayer)

def canTriggerPronArendel(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iTeam = pPlayer.getTeam()
	eTeam = gc.getTeam(iTeam)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_ARENDEL'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		iTeam2 = pPlayer2.getTeam()
		if eTeam.isHasMet(iTeam2):
			if pPlayer2.AI_getAttitude(iPlayer) == gc.getInfoTypeForString('ATTITUDE_FRIENDLY'):
				return True
	return False

def applyPronThessa(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_THESSA'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		pPlayer2.AI_changeAttitudeExtra(iPlayer,4)
		cf.addPlayerPopup(CyTranslator().getText("TXT_KEY_EVENT_PRON_THESSA_POPUP",()), iPlayer)

def canTriggerPronThessa(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iTeam = pPlayer.getTeam()
	eTeam = gc.getTeam(iTeam)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_THESSA'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		iTeam2 = pPlayer2.getTeam()
		if eTeam.isHasMet(iTeam2):
			if pPlayer2.AI_getAttitude(iPlayer) == gc.getInfoTypeForString('ATTITUDE_FRIENDLY'):
				return True
	return False

def applyPronHannah(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_HANNAH'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		pPlayer2.AI_changeAttitudeExtra(iPlayer,4)
		cf.addPlayerPopup(CyTranslator().getText("TXT_KEY_EVENT_PRON_HANNAH_POPUP",()), iPlayer)

def canTriggerPronHannah(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iTeam = pPlayer.getTeam()
	eTeam = gc.getTeam(iTeam)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_HANNAH'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		iTeam2 = pPlayer2.getTeam()
		if eTeam.isHasMet(iTeam2):
			if pPlayer2.AI_getAttitude(iPlayer) == gc.getInfoTypeForString('ATTITUDE_FRIENDLY'):
				return True
	return False

def applyPronRhoanna(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_RHOANNA'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		pPlayer2.AI_changeAttitudeExtra(iPlayer,4)
		cf.addPlayerPopup(CyTranslator().getText("TXT_KEY_EVENT_PRON_RHOANNA_POPUP",()), iPlayer)

def canTriggerPronRhoanna(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iTeam = pPlayer.getTeam()
	eTeam = gc.getTeam(iTeam)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_RHOANNA'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		iTeam2 = pPlayer2.getTeam()
		if eTeam.isHasMet(iTeam2):
			if pPlayer2.AI_getAttitude(iPlayer) == gc.getInfoTypeForString('ATTITUDE_FRIENDLY'):
				return True
	return False

def applyPronValledia(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_VALLEDIA'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		pPlayer2.AI_changeAttitudeExtra(iPlayer,4)
		cf.addPlayerPopup(CyTranslator().getText("TXT_KEY_EVENT_PRON_VALLEDIA_POPUP",()), iPlayer)

def canTriggerPronValledia(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iTeam = pPlayer.getTeam()
	eTeam = gc.getTeam(iTeam)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_VALLEDIA'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		iTeam2 = pPlayer2.getTeam()
		if eTeam.isHasMet(iTeam2):
			if pPlayer2.AI_getAttitude(iPlayer) == gc.getInfoTypeForString('ATTITUDE_FRIENDLY'):
				return True
	return False

def applyPronMahala(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_MAHALA'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		pPlayer2.AI_changeAttitudeExtra(iPlayer,4)
		cf.addPlayerPopup(CyTranslator().getText("TXT_KEY_EVENT_PRON_MAHALA_POPUP",()), iPlayer)

def canTriggerPronMahala(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iTeam = pPlayer.getTeam()
	eTeam = gc.getTeam(iTeam)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_MAHALA'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		iTeam2 = pPlayer2.getTeam()
		if eTeam.isHasMet(iTeam2):
			if pPlayer2.AI_getAttitude(iPlayer) == gc.getInfoTypeForString('ATTITUDE_FRIENDLY'):
				return True
	return False

def applyPronKeelyn(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_KEELYN'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		pPlayer2.AI_changeAttitudeExtra(iPlayer,4)
		cf.addPlayerPopup(CyTranslator().getText("TXT_KEY_EVENT_PRON_KEELYN_POPUP",()), iPlayer)

def canTriggerPronKeelyn(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iTeam = pPlayer.getTeam()
	eTeam = gc.getTeam(iTeam)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_KEELYN'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		iTeam2 = pPlayer2.getTeam()
		if eTeam.isHasMet(iTeam2):
			if pPlayer2.AI_getAttitude(iPlayer) == gc.getInfoTypeForString('ATTITUDE_FRIENDLY'):
				return True
	return False

def applyPronSheelba(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_SHEELBA'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		pPlayer2.AI_changeAttitudeExtra(iPlayer,4)
		cf.addPlayerPopup(CyTranslator().getText("TXT_KEY_EVENT_PRON_SHEELBA_POPUP",()), iPlayer)

def canTriggerPronSheelba(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iTeam = pPlayer.getTeam()
	eTeam = gc.getTeam(iTeam)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_SHEELBA'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		iTeam2 = pPlayer2.getTeam()
		if eTeam.isHasMet(iTeam2):
			if pPlayer2.AI_getAttitude(iPlayer) == gc.getInfoTypeForString('ATTITUDE_FRIENDLY'):
				return True
	return False

def applyPronFaeryl(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_FAERYL'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		pPlayer2.AI_changeAttitudeExtra(iPlayer,4)
		cf.addPlayerPopup(CyTranslator().getText("TXT_KEY_EVENT_PRON_FAERYL_POPUP",()), iPlayer)

def canTriggerPronFaeryl(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iTeam = pPlayer.getTeam()
	eTeam = gc.getTeam(iTeam)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_FAERYL'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		iTeam2 = pPlayer2.getTeam()
		if eTeam.isHasMet(iTeam2):
			if pPlayer2.AI_getAttitude(iPlayer) == gc.getInfoTypeForString('ATTITUDE_FRIENDLY'):
				return True
	return False

def applyPronAlexis(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_ALEXIS'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		pPlayer2.AI_changeAttitudeExtra(iPlayer,4)
		cf.addPlayerPopup(CyTranslator().getText("TXT_KEY_EVENT_PRON_ALEXIS_POPUP",()), iPlayer)

def canTriggerPronAlexis(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iTeam = pPlayer.getTeam()
	eTeam = gc.getTeam(iTeam)
	iLeader = cf.getLeader(gc.getInfoTypeForString('LEADER_ALEXIS'))
	if iLeader != -1:
		pPlayer2 = gc.getPlayer(iLeader)
		iTeam2 = pPlayer2.getTeam()
		if eTeam.isHasMet(iTeam2):
			if pPlayer2.AI_getAttitude(iPlayer) == gc.getInfoTypeForString('ATTITUDE_FRIENDLY'):
				return True
	return False

def canTriggerUniqueFeatureAifonIsle(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	if not pPlayer.isHuman():
		return False
	iImp = gc.getInfoTypeForString('IMPROVEMENT_AIFON_ISLE')
	iCount = 0
	for i in range(CyMap().getNumAreas()):
		iCount += CyMap().getArea(i).getNumImprovements(iImp)
	if iCount == 0:
		return False
	return True

def canTriggerUniqueFeatureBradelinesWell(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	if not pPlayer.isHuman():
		return False
	iImp = gc.getInfoTypeForString('IMPROVEMENT_BRADELINES_WELL')
	iCount = 0
	for i in range(CyMap().getNumAreas()):
		iCount += CyMap().getArea(i).getNumImprovements(iImp)
	if iCount == 0:
		return False
	return True

def canTriggerUniqueFeatureBrokenSepulcher(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	if not pPlayer.isHuman():
		return False
	iImp = gc.getInfoTypeForString('IMPROVEMENT_BROKEN_SEPULCHER')
	iCount = 0
	for i in range(CyMap().getNumAreas()):
		iCount += CyMap().getArea(i).getNumImprovements(iImp)
	if iCount == 0:
		return False
	return True

def canTriggerUniqueFeatureGuardian(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	if not pPlayer.isHuman():
		return False
	iImp = gc.getInfoTypeForString('IMPROVEMENT_GUARDIAN')
	iCount = 0
	for i in range(CyMap().getNumAreas()):
		iCount += CyMap().getArea(i).getNumImprovements(iImp)
	if iCount == 0:
		return False
	return True

def canTriggerUniqueFeatureLetumFrigus(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	if not pPlayer.isHuman():
		return False
	if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_ILLIANS'):
		return False
	iImp = gc.getInfoTypeForString('IMPROVEMENT_LETUM_FRIGUS')
	iCount = 0
	for i in range(CyMap().getNumAreas()):
		iCount += CyMap().getArea(i).getNumImprovements(iImp)
	if iCount == 0:
		return False
	return True

def canTriggerUniqueFeatureLetumFrigusIllians(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	if not pPlayer.isHuman():
		return False
	iImp = gc.getInfoTypeForString('IMPROVEMENT_LETUM_FRIGUS')
	iCount = 0
	for i in range(CyMap().getNumAreas()):
		iCount += CyMap().getArea(i).getNumImprovements(iImp)
	if iCount == 0:
		return False
	return True

def canTriggerUniqueFeaturePyreOfTheSeraphic(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	if not pPlayer.isHuman():
		return False
	if pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_EVIL'):
		return False
	iImp = gc.getInfoTypeForString('IMPROVEMENT_PYRE_OF_THE_SERAPHIC')
	iCount = 0
	for i in range(CyMap().getNumAreas()):
		iCount += CyMap().getArea(i).getNumImprovements(iImp)
	if iCount == 0:
		return False
	return True

def canTriggerSageKeep(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iCity = argsList[2]
	pPlayer = gc.getPlayer(ePlayer)
	pCity = pPlayer.getCity(iCity)
	if pCity.getSpecialistCount(gc.getInfoTypeForString('SPECIALIST_GREAT_SCIENTIST')) == 0:
		return False
	return True

def doSailorsDirge(argsList):
	kTriggeredData = argsList[0]
	eUnit = gc.getInfoTypeForString('UNIT_SAILORS_DIRGE')
	eIce = gc.getInfoTypeForString('FEATURE_ICE')
	if CyGame().getUnitCreatedCount(eUnit) == 0:
		pBestPlot = -1
		iBestPlot = -1
		for i in range (CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			iPlot = -1
			if pPlot.isWater() and pPlot.getFeatureType() != eIce:
				if pPlot.getNumUnits() == 0:
					iPlot = CyGame().getSorenRandNum(500, "Sailors Dirge")
					iPlot = iPlot + (pPlot.area().getNumTiles() * 10)
					if pPlot.isOwned():
						iPlot = iPlot / 2
					if iPlot > iBestPlot:
						iBestPlot = iPlot
						pBestPlot = pPlot
		if iBestPlot != -1:
			bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
			newUnit = bPlayer.initUnit(eUnit, pBestPlot.getX(), pBestPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
			iSkeleton = gc.getInfoTypeForString('UNIT_SKELETON')
			bPlayer.initUnit(iSkeleton, newUnit.getX(), newUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
			bPlayer.initUnit(iSkeleton, newUnit.getX(), newUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
			bPlayer.initUnit(iSkeleton, newUnit.getX(), newUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

def doSailorsDirgeDefeated(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	cf.placeTreasure(iPlayer, gc.getInfoTypeForString('EQUIPMENT_TREASURE'))

def applyShrineCamulos2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	if CyGame().getSorenRandNum(100, "Shrine Camulos") < 10:
		pPlot = cf.findClearPlot(-1, pCity.plot())
		if pPlot != -1:
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_SHRINE_CAMULOS",()),'',1,'Art/Interface/Buttons/Units/Pit Beast.dds',ColorTypes(8),pCity.getX(),pCity.getY(),True,True)
			bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
			newUnit = bPlayer.initUnit(gc.getInfoTypeForString('UNIT_PIT_BEAST'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
			newUnit.attack(pCity.plot(), False)

def doSignAeron(argsList):
	kTriggeredData = argsList[0]
	CyGame().changeGlobalCounter(3)

def doSignBhall(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	iDesert = gc.getInfoTypeForString('TERRAIN_DESERT')
	iGrass = gc.getInfoTypeForString('TERRAIN_GRASS')
	iPlains = gc.getInfoTypeForString('TERRAIN_PLAINS')
	iSnow = gc.getInfoTypeForString('TERRAIN_SNOW')
	iTundra = gc.getInfoTypeForString('TERRAIN_TUNDRA')
	for i in range (CyMap().numPlots()):
		pPlot = CyMap().plotByIndex(i)
		if pPlot.getOwner() == iPlayer:
			if pPlot.getFeatureType() == -1:
				if pPlot.getImprovementType() == -1:
					if pPlot.isWater() == False:
						if CyGame().getSorenRandNum(100, "SignBhall") < 10:
							iTerrain = pPlot.getTerrainType()
							if iTerrain == iSnow:
								pPlot.setTempTerrainType(iTundra, CyGame().getSorenRandNum(10, "Bob") + 10)
							if iTerrain == iTundra:
								pPlot.setTempTerrainType(iGrass, CyGame().getSorenRandNum(10, "Bob") + 10)
							if iTerrain == iGrass:
								pPlot.setTempTerrainType(iPlains, CyGame().getSorenRandNum(10, "Bob") + 10)
							if iTerrain == iPlains:
								pPlot.setTempTerrainType(iDesert, CyGame().getSorenRandNum(10, "Bob") + 10)

def doSignCamulos(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	for iLoopPlayer in range(gc.getMAX_CIV_PLAYERS()):
		loopPlayer = gc.getPlayer(iLoopPlayer)
		if loopPlayer.isAlive():
			if loopPlayer.getTeam() != pPlayer.getTeam():
				loopPlayer.AI_changeAttitudeExtra(iPlayer, -1)
				pPlayer.AI_changeAttitudeExtra(iLoopPlayer, -1)

def doSignDagda(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	for iLoopPlayer in range(gc.getMAX_CIV_PLAYERS()):
		loopPlayer = gc.getPlayer(iLoopPlayer)
		if loopPlayer.isAlive():
			if loopPlayer.getTeam() != pPlayer.getTeam():
				loopPlayer.AI_changeAttitudeExtra(iPlayer, 1)
				pPlayer.AI_changeAttitudeExtra(iLoopPlayer, 1)

def doSignEsus(argsList):
	kTriggeredData = argsList[0]
	CyGame().changeCrime(5)

def doSignLugus(argsList):
	kTriggeredData = argsList[0]
	CyGame().changeCrime(-5)

def doSignMulcarn(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	iDesert = gc.getInfoTypeForString('TERRAIN_DESERT')
	iGrass = gc.getInfoTypeForString('TERRAIN_GRASS')
	iPlains = gc.getInfoTypeForString('TERRAIN_PLAINS')
	iSnow = gc.getInfoTypeForString('TERRAIN_SNOW')
	iTundra = gc.getInfoTypeForString('TERRAIN_TUNDRA')
	for i in range (CyMap().numPlots()):
		pPlot = CyMap().plotByIndex(i)
		if pPlot.getOwner() == iPlayer:
			if pPlot.getFeatureType() == -1:
				if pPlot.getImprovementType() == -1:
					if pPlot.isWater() == False:
						if CyGame().getSorenRandNum(100, "SignMulcarn") < 10:
							iTerrain = pPlot.getTerrainType()
							if iTerrain == iTundra:
								pPlot.setTempTerrainType(iSnow, CyGame().getSorenRandNum(10, "Bob") + 10)
							if iTerrain == iGrass:
								pPlot.setTempTerrainType(iTundra, CyGame().getSorenRandNum(10, "Bob") + 10)
							if iTerrain == iPlains:
								pPlot.setTempTerrainType(iTundra, CyGame().getSorenRandNum(10, "Bob") + 10)
							if iTerrain == iDesert:
								pPlot.setTempTerrainType(iPlains, CyGame().getSorenRandNum(10, "Bob") + 10)

def doSignSirona(argsList):
	kTriggeredData = argsList[0]
	CyGame().changeGlobalCounter(-3)

def doSignSucellus(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	iDiseased = gc.getInfoTypeForString('PROMOTION_DISEASED')
	apUnitList = PyPlayer(iPlayer).getUnitList()
	for pUnit in apUnitList:
		if pUnit.isHasPromotion(iDiseased):
			pUnit.setHasPromotion(iDiseased, False)
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_POOL_OF_TEARS_DISEASED",()),'AS2D_FEATUREGROWTH',1,'Art/Interface/Buttons/Spells/Curedisease.dds',ColorTypes(8),pUnit.getX(),pUnit.getY(),True,True)
		if pUnit.getDamage() > 0:
			pUnit.setDamage(pUnit.getDamage() / 2, PlayerTypes.NO_PLAYER)
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_HEALED",()),'AS2D_FEATUREGROWTH',1,'Art/Interface/Buttons/Spells/Heal.dds',ColorTypes(8),pUnit.getX(),pUnit.getY(),True,True)

def doSignTali(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	iSmoke = gc.getInfoTypeForString('IMPROVEMENT_SMOKE')
	iFlames = gc.getInfoTypeForString('FEATURE_FLAMES')
	iSpring = gc.getInfoTypeForString('EFFECT_SPRING')
	for i in range (CyMap().numPlots()):
		pPlot = CyMap().plotByIndex(i)
		if pPlot.getOwner() == iPlayer:
			if pPlot.getFeatureType() == iFlames:
				point = pPlot.getPoint()
				CyEngine().triggerEffect(iSpring,point)
				CyAudioGame().Play3DSound("AS3D_SPELL_SPRING",point.x,point.y,point.z)
				pPlot.setFeatureType(-1, 0)
			if pPlot.getImprovementType() == iSmoke:
				point = pPlot.getPoint()
				CyEngine().triggerEffect(iSpring,point)
				CyAudioGame().Play3DSound("AS3D_SPELL_SPRING",point.x,point.y,point.z)
				pPlot.setImprovementType(-1)

def canTriggerSmugglers(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iCity = argsList[2]
	pPlayer = gc.getPlayer(ePlayer)
	pCity = pPlayer.getCity(iCity)
	if pCity.getNumRealBuilding(gc.getInfoTypeForString('BUILDING_SMUGGLERS_PORT')) > 0:
		return False
	if pCity.isCoastal(10) == False:
		return False
	return True

def doSpiderMine3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	if pPlot.getNumUnits() == 0:
		bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
		newUnit = bPlayer.initUnit(gc.getInfoTypeForString('UNIT_GIANT_SPIDER'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
		newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_HIDDEN_NATIONALITY'), True)

def applyTreasure1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	cf.placeTreasure(iPlayer, gc.getInfoTypeForString('EQUIPMENT_TREASURE'))

def canTriggerSwitchCivs(argsList):
	kTriggeredData = argsList[0]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	otherPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
	if pPlayer.isHuman() == False:
		return False
	if CyGame().getRankPlayer(0) != kTriggeredData.ePlayer:
		return False
	if CyGame().getGameTurn() < 20:
		return False
	if gc.getTeam(otherPlayer.getTeam()).isAVassal():
		return False
	if CyGame().getWBMapScript():
		return False
	return True

def doSwitchCivs2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iNewPlayer = kTriggeredData.eOtherPlayer
	iOldPlayer = kTriggeredData.ePlayer
	CyGame().reassignPlayerAdvanced(iOldPlayer, iNewPlayer, -1)

def canTriggerTraitor(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iCity = argsList[2]
	pPlayer = gc.getPlayer(ePlayer)
	pCity = pPlayer.getCity(iCity)
	if (pCity.happyLevel() - pCity.unhappyLevel(0)) < 0:
		return False
	return True

def doVeilVsOrderTemple1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	pCity.changeOccupationTimer(1)
	iOrder = gc.getInfoTypeForString('RELIGION_THE_ORDER')
	iVeil = gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL')
	pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_ORDER'), 0)
	if pCity.isHolyCityByType(iOrder) == False:
		if gc.getGame().getSorenRandNum(100, "Veil vs Order Temple 1") < 50:
			pCity.setHasReligion(iOrder, False, False, False)
	(loopCity, iter) = pPlayer.firstCity(false)
	while(loopCity):
		if loopCity.isHasReligion(iVeil):
			loopCity.changeHappinessTimer(5)
		if loopCity.isHasReligion(iOrder):
			loopCity.changeHurryAngerTimer(5)
		(loopCity, iter) = pPlayer.nextCity(iter, false)

def doVeilVsOrderTemple2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	pCity.changeOccupationTimer(1)
	iOrder = gc.getInfoTypeForString('RELIGION_THE_ORDER')
	if gc.getGame().getSorenRandNum(100, "Veil Vs Order Temple 2") < 50:
		pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_TEMPLE_OF_THE_ORDER'), 0)
	if pCity.isHolyCityByType(iOrder) == False:
		if gc.getGame().getSorenRandNum(100, "Veil Vs Order Temple 2") < 50:
			pCity.setHasReligion(iOrder, False, False, False)
	if gc.getGame().getSorenRandNum(100, "Veil Vs Order Temple 2") < 50:
		pCity.changePopulation(-1)

def doVeilVsOrderTemple3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	pCity.changeOccupationTimer(3)
	iOrder = gc.getInfoTypeForString('RELIGION_THE_ORDER')
	iVeil = gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL')
	(loopCity, iter) = pPlayer.firstCity(false)
	while(loopCity):
		if loopCity.isHasReligion(iOrder):
			loopCity.changeHappinessTimer(5)
		if loopCity.isHasReligion(iVeil):
			loopCity.changeHurryAngerTimer(5)
		(loopCity, iter) = pPlayer.nextCity(iter, false)

def helpVeilVsOrderTemple1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	szHelp = localText.getText("TXT_KEY_EVENT_VEIL_VS_ORDER_TEMPLE_1_HELP", ())
	return szHelp

def helpVeilVsOrderTemple2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	szHelp = localText.getText("TXT_KEY_EVENT_VEIL_VS_ORDER_TEMPLE_2_HELP", ())
	return szHelp

def helpVeilVsOrderTemple3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	szHelp = localText.getText("TXT_KEY_EVENT_VEIL_VS_ORDER_TEMPLE_3_HELP", ())
	return szHelp

def doSlaveEscape(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pUnit = pPlayer.getUnit(kTriggeredData.iUnitId)
	pUnit.kill(False, -1)
	CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_SLAVE_ESCAPE", ()),'',1,'Art/Interface/Buttons/Units/Slave.dds',ColorTypes(8),pUnit.getX(),pUnit.getY(),True,True)

def canTriggerSlaveRevoltUnit(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iUnit = argsList[2]
	pPlayer = gc.getPlayer(ePlayer)
	pUnit = pPlayer.getUnit(iUnit)
	pPlot = pUnit.plot()
	if pPlot.getNumUnits() != 1:
		return False
	return True

def doSlaveRevolt(argsList):
	kTriggeredData = argsList[0]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pUnit = pPlayer.getUnit(kTriggeredData.iUnitId)
	iRace = pUnit.getRace()
	plot = pUnit.plot()
	pUnit.kill(False, -1)
	bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
	pNewUnit = bPlayer.initUnit(gc.getInfoTypeForString('UNIT_WARRIOR'), plot.getX(), plot.getY(), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.DIRECTION_SOUTH)
	if iRace != -1:
		pNewUnit.setHasPromotion(iRace, True)
	CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_SLAVE_REVOLT", ()),'',1,'Art/Interface/Buttons/Units/Slave.dds',ColorTypes(8),pUnit.getX(),pUnit.getY(),True,True)

def canApplyTraitAggressive(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() == gc.getInfoTypeForString('TRAIT_AGGRESSIVE'):
		return False
	return True

# lfgr: adaptive event help
def helpTraitAggressive(argsList) :
	return CyGameTextMgr().parseTraits( gc.getInfoTypeForString('TRAIT_AGGRESSIVE'), CivilizationTypes.NO_CIVILIZATION, false )
# lfgr end

def doTraitAggressive(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	for iTrait in range(gc.getNumTraitInfos()):
		if pPlayer.hasTrait(iTrait):
			if (gc.getTraitInfo(iTrait).isSelectable()):
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() != iTrait:
					pPlayer.setHasTrait(iTrait,False)
	pPlayer.setHasTrait(gc.getInfoTypeForString('TRAIT_AGGRESSIVE'),True)

def canApplyTraitArcane(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() == gc.getInfoTypeForString('TRAIT_ARCANE'):
		return False
	return True

# lfgr: adaptive event help
def helpTraitArcane(argsList) :
	return CyGameTextMgr().parseTraits( gc.getInfoTypeForString('TRAIT_ARCANE'), CivilizationTypes.NO_CIVILIZATION, false )
# lfgr end

def doTraitArcane(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	for iTrait in range(gc.getNumTraitInfos()):
		if pPlayer.hasTrait(iTrait):
			if (gc.getTraitInfo(iTrait).isSelectable()):
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() != iTrait:
					pPlayer.setHasTrait(iTrait,False)
	pPlayer.setHasTrait(gc.getInfoTypeForString('TRAIT_ARCANE'),True)

def canApplyTraitCharismatic(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() == gc.getInfoTypeForString('TRAIT_CHARISMATIC'):
		return False
	return True

# lfgr: adaptive event help
def helpTraitCharismatic(argsList) :
	return CyGameTextMgr().parseTraits( gc.getInfoTypeForString('TRAIT_CHARISMATIC'), CivilizationTypes.NO_CIVILIZATION, false )
# lfgr end

def doTraitCharismatic(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	for iTrait in range(gc.getNumTraitInfos()):
		if pPlayer.hasTrait(iTrait):
			if (gc.getTraitInfo(iTrait).isSelectable()):
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() != iTrait:
					pPlayer.setHasTrait(iTrait,False)
	pPlayer.setHasTrait(gc.getInfoTypeForString('TRAIT_CHARISMATIC'),True)

def canApplyTraitCreative(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() == gc.getInfoTypeForString('TRAIT_CREATIVE'):
		return False
	return True

# lfgr: adaptive event help
def helpTraitCreative(argsList) :
	return CyGameTextMgr().parseTraits( gc.getInfoTypeForString('TRAIT_CREATIVE'), CivilizationTypes.NO_CIVILIZATION, false )
# lfgr end

def doTraitCreative(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	for iTrait in range(gc.getNumTraitInfos()):
		if pPlayer.hasTrait(iTrait):
			if (gc.getTraitInfo(iTrait).isSelectable()):
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() != iTrait:
					pPlayer.setHasTrait(iTrait,False)
	pPlayer.setHasTrait(gc.getInfoTypeForString('TRAIT_CREATIVE'),True)

def canApplyTraitExpansive(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() == gc.getInfoTypeForString('TRAIT_EXPANSIVE'):
		return False
	return True

# lfgr: adaptive event help
def helpTraitExpansive(argsList) :
	return CyGameTextMgr().parseTraits( gc.getInfoTypeForString('TRAIT_EXPANSIVE'), CivilizationTypes.NO_CIVILIZATION, false )
# lfgr end

def doTraitExpansive(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	for iTrait in range(gc.getNumTraitInfos()):
		if pPlayer.hasTrait(iTrait):
			if (gc.getTraitInfo(iTrait).isSelectable()):
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() != iTrait:
					pPlayer.setHasTrait(iTrait,False)
	pPlayer.setHasTrait(gc.getInfoTypeForString('TRAIT_EXPANSIVE'),True)

def canApplyTraitFinancial(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() == gc.getInfoTypeForString('TRAIT_FINANCIAL'):
		return False
	return True

# lfgr: adaptive event help
def helpTraitFinancial(argsList) :
	return CyGameTextMgr().parseTraits( gc.getInfoTypeForString('TRAIT_FINANCIAL'), CivilizationTypes.NO_CIVILIZATION, false )
# lfgr end

def doTraitFinancial(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	for iTrait in range(gc.getNumTraitInfos()):
		if pPlayer.hasTrait(iTrait):
			if (gc.getTraitInfo(iTrait).isSelectable()):
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() != iTrait:
					pPlayer.setHasTrait(iTrait,False)
	pPlayer.setHasTrait(gc.getInfoTypeForString('TRAIT_FINANCIAL'),True)

def canApplyTraitIndustrious(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() == gc.getInfoTypeForString('TRAIT_INDUSTRIOUS'):
		return False
	return True

# lfgr: adaptive event help
def helpTraitIndustrious(argsList) :
	return CyGameTextMgr().parseTraits( gc.getInfoTypeForString('TRAIT_INDUSTRIOUS'), CivilizationTypes.NO_CIVILIZATION, false )
# lfgr end

def doTraitIndustrious(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	for iTrait in range(gc.getNumTraitInfos()):
		if pPlayer.hasTrait(iTrait):
			if (gc.getTraitInfo(iTrait).isSelectable()):
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() != iTrait:
					pPlayer.setHasTrait(iTrait, False)
	pPlayer.setHasTrait(gc.getInfoTypeForString('TRAIT_INDUSTRIOUS'),True)

def doTraitInsane(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pCivilization = gc.getCivilizationInfo(pPlayer.getCivilizationType())
	iTraitCount = 0
	for i in range(gc.getNumTraitInfos()):
		if (pPlayer.hasTrait(i) and i != gc.getInfoTypeForString('TRAIT_INSANE')):
			if (i != pCivilization.getCivTrait()):
				pPlayer.setHasTrait(i, False)
				iTraitCount = iTraitCount + 1
				
	Traits = [ 'TRAIT_AGGRESSIVE','TRAIT_ARCANE','TRAIT_CHARISMATIC','TRAIT_CREATIVE','TRAIT_EXPANSIVE','TRAIT_FINANCIAL','TRAIT_INDUSTRIOUS','TRAIT_ORGANIZED','TRAIT_PHILOSOPHICAL','TRAIT_RAIDERS','TRAIT_SPIRITUAL' ]

	if (iTraitCount > 0):
		iRnd1 = CyGame().getSorenRandNum(len(Traits), "Insane Trait 1")
		pPlayer.setHasTrait(gc.getInfoTypeForString(Traits[iRnd1]),True)
	if (iTraitCount > 1):
		iRnd2 = CyGame().getSorenRandNum(len(Traits), "Insane Trait 2")
		while iRnd2 == iRnd1:
			iRnd2 = CyGame().getSorenRandNum(len(Traits), "Insane Trait 2 - retry")
		pPlayer.setHasTrait(gc.getInfoTypeForString(Traits[iRnd2]),True)
	if (iTraitCount > 2):
		iRnd3 = CyGame().getSorenRandNum(len(Traits), "Insane Trait 3")
		while iRnd3 == iRnd1 or iRnd3 == iRnd2:
			iRnd3 = CyGame().getSorenRandNum(len(Traits), "Insane Trait 3 - retry")
		pPlayer.setHasTrait(gc.getInfoTypeForString(Traits[iRnd3]),True)

# code from MagisterMod
	iRnd = (CyGame().getSorenRandNum(6, "Insane Attitude Change") - 3)
	for iLoopPlayer in range(gc.getMAX_CIV_PLAYERS()):
		loopPlayer = gc.getPlayer(iLoopPlayer)
		if loopPlayer.isAlive():
			if loopPlayer.getTeam() != pPlayer.getTeam():
				pPlayer.AI_changeAttitudeExtra(iLoopPlayer, iRnd)



def canApplyTraitOrganized(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() == gc.getInfoTypeForString('TRAIT_ORGANIZED'):
		return False
	return True

# lfgr: adaptive event help
def helpTraitOrganized(argsList) :
	return CyGameTextMgr().parseTraits( gc.getInfoTypeForString('TRAIT_ORGANIZED'), CivilizationTypes.NO_CIVILIZATION, false )
# lfgr end

def doTraitOrganized(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	for iTrait in range(gc.getNumTraitInfos()):
		if pPlayer.hasTrait(iTrait):
			if (gc.getTraitInfo(iTrait).isSelectable()):
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() != iTrait:
					pPlayer.setHasTrait(iTrait, False)
	pPlayer.setHasTrait(gc.getInfoTypeForString('TRAIT_ORGANIZED'),True)

def canApplyTraitPhilosophical(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() == gc.getInfoTypeForString('TRAIT_PHILOSOPHICAL'):
		return False
	return True

# lfgr: adaptive event help
def helpTraitPhilosophical(argsList) :
	return CyGameTextMgr().parseTraits( gc.getInfoTypeForString('TRAIT_PHILOSOPHICAL'), CivilizationTypes.NO_CIVILIZATION, false )
# lfgr end

def doTraitPhilosophical(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	for iTrait in range(gc.getNumTraitInfos()):
		if pPlayer.hasTrait(iTrait):
			if (gc.getTraitInfo(iTrait).isSelectable()):
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() != iTrait:
					pPlayer.setHasTrait(iTrait, False)
	pPlayer.setHasTrait(gc.getInfoTypeForString('TRAIT_PHILOSOPHICAL'),True)

def canApplyTraitRaiders(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() == gc.getInfoTypeForString('TRAIT_RAIDERS'):
		return False
	return True

# lfgr: adaptive event help
def helpTraitRaiders(argsList) :
	return CyGameTextMgr().parseTraits( gc.getInfoTypeForString('TRAIT_RAIDERS'), CivilizationTypes.NO_CIVILIZATION, false )
# lfgr end

def doTraitRaiders(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	for iTrait in range(gc.getNumTraitInfos()):
		if pPlayer.hasTrait(iTrait):
			if (gc.getTraitInfo(iTrait).isSelectable()):
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() != iTrait:
					pPlayer.setHasTrait(iTrait, False)
	pPlayer.setHasTrait(gc.getInfoTypeForString('TRAIT_RAIDERS'),True)

def canApplyTraitSpiritual(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	pPlayer = gc.getPlayer(kTriggeredData.ePlayer)
	if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() == gc.getInfoTypeForString('TRAIT_SPIRITUAL'):
		return False
	return True

# lfgr: adaptive event help
def helpTraitSpiritual(argsList) :
	return CyGameTextMgr().parseTraits( gc.getInfoTypeForString('TRAIT_SPIRITUAL'), CivilizationTypes.NO_CIVILIZATION, false )
# lfgr end

def doTraitSpiritual(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	for iTrait in range(gc.getNumTraitInfos()):
		if pPlayer.hasTrait(iTrait):
			if (gc.getTraitInfo(iTrait).isSelectable()):
				if gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getPermanentTrait() != iTrait:
					pPlayer.setHasTrait(iTrait, False)
	pPlayer.setHasTrait(gc.getInfoTypeForString('TRAIT_SPIRITUAL'),True)

def doVolcanoCreation(argsList):
	kTriggeredData = argsList[0]
	pPlot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	pPlot.setPlotType(PlotTypes.PLOT_LAND, True, True)
	pPlot.setFeatureType(gc.getInfoTypeForString('FEATURE_VOLCANO'), 0)
	point = pPlot.getPoint()
	CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_ARTILLERY_SHELL_EXPLODE'),point)
	CyAudioGame().Play3DSound("AS3D_UN_GRENADE_EXPLODE",point.x,point.y,point.z)
# FlavourMod: Idea nicked from Rystic's TweakMod by Jean Elcard 11/08/2009
	iSmoke = gc.getInfoTypeForString('IMPROVEMENT_SMOKE')
	iFlames = gc.getInfoTypeForString('FEATURE_FLAMES')
	sFlammables = ['FOREST', 'FOREST_NEW', 'FOREST_ANCIENT', 'JUNGLE', 'SCRUB']
	iFlammables = [gc.getInfoTypeForString('FEATURE_' + sFeature) for sFeature in sFlammables]
	for iDirection in range(DirectionTypes.NUM_DIRECTION_TYPES):
		pAdjacentPlot = plotDirection(pPlot.getX(), pPlot.getY(), DirectionTypes(iDirection))
		if pAdjacentPlot.getFeatureType() in iFlammables:
			iRandom = CyGame().getSorenRandNum(100, "FlavourMod: doVolcanoCreation")
			if iRandom < 30:
				pAdjacentPlot.setFeatureType(iFlames, -1)
			elif iRandom < 60:
				pAdjacentPlot.setImprovementType(iSmoke)
# FlavourMod: End Pilferage

def canTriggerWarGamesUnit(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iUnit = argsList[2]
	pPlayer = gc.getPlayer(ePlayer)
	pUnit = pPlayer.getUnit(iUnit)
	if pUnit.isAlive() == False:
		return False
	if pUnit.isOnlyDefensive():
		return False
	return True

def applyWBFallOfCuantineRosier1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	CyGame().setTrophyValue("TROPHY_WB_FALL_OF_CUANTINE_ROSIER_ALLY", 0)

def applyWBFallOfCuantineRosier2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	CyGame().setTrophyValue("TROPHY_WB_FALL_OF_CUANTINE_ROSIER_ALLY", 1)

def applyWBFallOfCuantineFleeCalabim(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	CyGame().setTrophyValue("TROPHY_WB_CIV_DECIUS", gc.getInfoTypeForString('CIVILIZATION_CALABIM'))

def applyWBFallOfCuantineFleeMalakim(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	CyGame().setTrophyValue("TROPHY_WB_CIV_DECIUS", gc.getInfoTypeForString('CIVILIZATION_MALAKIM'))

def applyWBGiftOfKylorinMeshabberRight(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pPlot = CyMap().plot(19,16)
	pPlot.setPythonActive(False)
	pPlot = CyMap().plot(20,16)
	pUnit = pPlot.getUnit(0)
	pUnit.kill(True, 0)
	cf.addPopup(CyTranslator().getText("TXT_KEY_WB_GIFT_OF_KYLORIN_MESHABBER_RIGHT",()),'art/interface/popups/Tya.dds')

def applyWBGiftOfKylorinMeshabberWrong(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pPlot1 = CyMap().plot(19,16)
	pPlot1.setPythonActive(False)
	pPlot2 = CyMap().plot(20,16)
	pUnit = pPlot2.getUnit(0)
	pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_HELD'), False)
	pUnit.attack(pPlot1, False)
	cf.addPopup(CyTranslator().getText("TXT_KEY_WB_GIFT_OF_KYLORIN_MESHABBER_WRONG",()),'art/interface/popups/Tya.dds')

def applyWBGiftOfKylorinSecretDoorYes(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pPlot = CyMap().plot(23,6)
	pPlot.setPythonActive(False)
	pPlot = CyMap().plot(23,5)
	pPlot.setFeatureType(-1, -1)

def applyWBLordOfTheBalorsTemptJudeccaYes(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	otherPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
	enemyTeam = otherPlayer.getTeam()
	eTeam = gc.getTeam(pPlayer.getTeam())
	eTeam.setPermanentWarPeace(enemyTeam, False)
	eTeam.setPermanentWarPeace(6, False)
	eTeam.makePeace(6)
	eTeam.declareWar(enemyTeam, true, WarPlanTypes.WARPLAN_TOTAL)
	eTeam.setPermanentWarPeace(enemyTeam, True)
	eTeam.setPermanentWarPeace(6, True)

def applyWBLordOfTheBalorsTemptSallosYes(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	eTeam = gc.getTeam(pPlayer.getTeam())
	eTeam.setPermanentWarPeace(7, False)
	eTeam.makePeace(7)
	eTeam.setPermanentWarPeace(7, True)

def applyWBLordOfTheBalorsTemptOuzzaYes(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	eTeam = gc.getTeam(pPlayer.getTeam())
	eTeam.setPermanentWarPeace(8, False)
	eTeam.makePeace(8)
	eTeam.setPermanentWarPeace(8, True)
	for pyCity in PyPlayer(iPlayer).getCityList():
		pCity = pyCity.GetCy()
		if pCity.getPopulation() > 1:
			pCity.changePopulation(-1)

def applyWBLordOfTheBalorsTemptMeresinYes(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	eTeam = gc.getTeam(pPlayer.getTeam())
	eTeam.setPermanentWarPeace(9, False)
	eTeam.makePeace(9)
	eTeam.setPermanentWarPeace(9, True)

def applyWBLordOfTheBalorsTemptStatiusYes(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	pPlayer = gc.getPlayer(iPlayer)
	eTeam = gc.getTeam(pPlayer.getTeam())
	eTeam.setPermanentWarPeace(10, False)
	eTeam.makePeace(10)
	eTeam.setPermanentWarPeace(10, True)
	pPlayer = gc.getPlayer(10)
	pPlayer.acquireCity(pCity,false,false)

def applyWBLordOfTheBalorsTemptLetheYes(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pUnit = pPlayer.getUnit(kTriggeredData.iUnitId)
	eTeam = gc.getTeam(pPlayer.getTeam())
	eTeam.setPermanentWarPeace(11, False)
	eTeam.makePeace(11)
	eTeam.setPermanentWarPeace(11, True)
	pUnit.kill(True, 0)

def applyWBSplinteredCourtDefeatedAmelanchier3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	iLjosalfarTeam = -1
	iDovielloTeam = -1
	iSvartalfarTeam = -1
	CyGame().setTrophyValue("TROPHY_WB_CIV_AMELANCHIER", gc.getInfoTypeForString('CIVILIZATION_DOVIELLO'))
	for iLoopPlayer in range(gc.getMAX_PLAYERS()):
		pLoopPlayer = gc.getPlayer(iLoopPlayer)
		if pLoopPlayer.isAlive():
			if pLoopPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_DOVIELLO'):
				iDovielloTeam = pLoopPlayer.getTeam()
			if pLoopPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LJOSALFAR'):
				iLjosalfarTeam = pLoopPlayer.getTeam()
			if pLoopPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_SVARTALFAR'):
				iSvartalfarTeam = pLoopPlayer.getTeam()
	if (iDovielloTeam != -1 and iLjosalfarTeam != -1 and iSvartalfarTeam != -1):
		eTeam = gc.getTeam(iDovielloTeam)
		if eTeam.isAtWar(iSvartalfarTeam):
			eTeam.makePeace(iSvartalfarTeam)
		if not eTeam.isAtWar(iLjosalfarTeam):
			eTeam.declareWar(iLjosalfarTeam, false, WarPlanTypes.WARPLAN_LIMITED)

def applyWBSplinteredCourtDefeatedThessa3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	iLjosalfarTeam = -1
	iCalabimTeam = -1
	iSvartalfarTeam = -1
	CyGame().setTrophyValue("TROPHY_WB_CIV_THESSA", gc.getInfoTypeForString('CIVILIZATION_CALABIM'))
	for iLoopPlayer in range(gc.getMAX_PLAYERS()):
		pLoopPlayer = gc.getPlayer(iLoopPlayer)
		if pLoopPlayer.isAlive():
			if pLoopPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_CALABIM'):
				iCalabimTeam = pLoopPlayer.getTeam()
			if pLoopPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LJOSALFAR'):
				iLjosalfarTeam = pLoopPlayer.getTeam()
			if pLoopPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_SVARTALFAR'):
				iSvartalfarTeam = pLoopPlayer.getTeam()
	if (iCalabimTeam != -1 and iLjosalfarTeam != -1 and iSvartalfarTeam != -1):
		eTeam = gc.getTeam(iCalabimTeam)
		if eTeam.isAtWar(iSvartalfarTeam):
			eTeam.makePeace(iSvartalfarTeam)
		if not eTeam.isAtWar(iLjosalfarTeam):
			eTeam.declareWar(iLjosalfarTeam, false, WarPlanTypes.WARPLAN_LIMITED)

def applyWBSplinteredCourtDefeatedRivanna3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	iLjosalfarTeam = -1
	iCalabimTeam = -1
	iSvartalfarTeam = -1
	CyGame().setTrophyValue("TROPHY_WB_CIV_RIVANNA", gc.getInfoTypeForString('CIVILIZATION_CALABIM'))
	for iLoopPlayer in range(gc.getMAX_PLAYERS()):
		pLoopPlayer = gc.getPlayer(iLoopPlayer)
		if pLoopPlayer.isAlive():
			if pLoopPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_CALABIM'):
				iCalabimTeam = pLoopPlayer.getTeam()
			if pLoopPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LJOSALFAR'):
				iLjosalfarTeam = pLoopPlayer.getTeam()
			if pLoopPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_SVARTALFAR'):
				iSvartalfarTeam = pLoopPlayer.getTeam()
	if (iCalabimTeam != -1 and iLjosalfarTeam != -1 and iSvartalfarTeam != -1):
		eTeam = gc.getTeam(iCalabimTeam)
		if eTeam.isAtWar(iLjosalfarTeam):
			eTeam.makePeace(iLjosalfarTeam)
		if not eTeam.isAtWar(iSvartalfarTeam):
			eTeam.declareWar(iSvartalfarTeam, false, WarPlanTypes.WARPLAN_LIMITED)

def applyWBSplinteredCourtDefeatedVolanna3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	iLjosalfarTeam = -1
	iDovielloTeam = -1
	iSvartalfarTeam = -1
	CyGame().setTrophyValue("TROPHY_WB_CIV_VOLANNA", gc.getInfoTypeForString('CIVILIZATION_DOVIELLO'))
	for iLoopPlayer in range(gc.getMAX_PLAYERS()):
		pLoopPlayer = gc.getPlayer(iLoopPlayer)
		if pLoopPlayer.isAlive():
			if pLoopPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_DOVIELLO'):
				iDovielloTeam = pLoopPlayer.getTeam()
			if pLoopPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LJOSALFAR'):
				iLjosalfarTeam = pLoopPlayer.getTeam()
			if pLoopPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_SVARTALFAR'):
				iSvartalfarTeam = pLoopPlayer.getTeam()
	if (iDovielloTeam != -1 and iLjosalfarTeam != -1 and iSvartalfarTeam != -1):
		eTeam = gc.getTeam(iDovielloTeam)
		if eTeam.isAtWar(iLjosalfarTeam):
			eTeam.makePeace(iLjosalfarTeam)
		if not eTeam.isAtWar(iSvartalfarTeam):
			eTeam.declareWar(iSvartalfarTeam, false, WarPlanTypes.WARPLAN_LIMITED)

def applyWBSplinteredCourtParithYes(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	CyGame().setTrophyValue("TROPHY_WB_SPLINTERED_COURT_PARITH", 1)

def canDoWBTheBlackTowerPickCivBannor(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	if CyGame().isHasTrophy("TROPHY_WB_THE_RADIANT_GUARD_CAPRIA_ALLY"):
		return True
	return False

def applyWBTheBlackTowerPickCivBannor(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	pCity = pPlot.getPlotCity()
	pCity.setCivilizationType(gc.getInfoTypeForString('CIVILIZATION_BANNOR'))
	CyInterface().setDirty(InterfaceDirtyBits.CityInfo_DIRTY_BIT, True)

def applyWBTheBlackTowerPickCivHippus(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	pCity = pPlot.getPlotCity()
	pCity.setCivilizationType(gc.getInfoTypeForString('CIVILIZATION_HIPPUS'))
	CyInterface().setDirty(InterfaceDirtyBits.CityInfo_DIRTY_BIT, True)

def applyWBTheBlackTowerPickCivLanun(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	pCity = pPlot.getPlotCity()
	pCity.setCivilizationType(gc.getInfoTypeForString('CIVILIZATION_LANUN'))
	CyInterface().setDirty(InterfaceDirtyBits.CityInfo_DIRTY_BIT, True)

def canDoWBTheBlackTowerPickCivLjosalfar(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	if CyGame().isHasTrophy("TROPHY_WB_THE_SPLINTERED_COURT_LJOSALFAR"):
		return True
	return False

def applyWBTheBlackTowerPickCivLjosalfar(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	pCity = pPlot.getPlotCity()
	pCity.setCivilizationType(gc.getInfoTypeForString('CIVILIZATION_LJOSALFAR'))
	CyInterface().setDirty(InterfaceDirtyBits.CityInfo_DIRTY_BIT, True)

def canDoWBTheBlackTowerPickCivLuchuirp(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	if CyGame().isHasTrophy("TROPHY_WB_THE_MOMUS_BEERI_ALLY"):
		return True
	return False

def applyWBTheBlackTowerPickCivLuchuirp(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	pCity = pPlot.getPlotCity()
	pCity.setCivilizationType(gc.getInfoTypeForString('CIVILIZATION_LUCHUIRP'))
	CyInterface().setDirty(InterfaceDirtyBits.CityInfo_DIRTY_BIT, True)

def canDoWBTheBlackTowerPickCivSvartalfar(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	if CyGame().isHasTrophy("TROPHY_WB_THE_SPLINTERED_COURT_SVARTALFAR"):
		return True
	return False

def applyWBTheBlackTowerPickCivSvartalfar(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	pCity = pPlot.getPlotCity()
	pCity.setCivilizationType(gc.getInfoTypeForString('CIVILIZATION_SVARTALFAR'))
	CyInterface().setDirty(InterfaceDirtyBits.CityInfo_DIRTY_BIT, True)

def applyWBTheMomusBeerisOfferYes(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	gc.getGame().changeTrophyValue("TROPHY_WB_THE_MOMUS_BEERI_ALLY", 1)
	eTeam = gc.getTeam(0) #Falamar
	eTeam7 = gc.getTeam(7) #Beeri
	eTeam.setPermanentWarPeace(1, False)
	eTeam.setPermanentWarPeace(7, False)
	eTeam.declareWar(1, true, WarPlanTypes.WARPLAN_TOTAL)
	eTeam7.declareWar(1, true, WarPlanTypes.WARPLAN_TOTAL)
	eTeam.makePeace(7)
	eTeam.setPermanentWarPeace(1, True)
	eTeam.setPermanentWarPeace(7, True)

def applyWBTheRadiantGuardChooseSidesBasium(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	gc.getGame().setTrophyValue("TROPHY_WB_THE_RADIANT_GUARD_HYBOREM_ALLY", 0)
	gc.getGame().setTrophyValue("TROPHY_WB_THE_RADIANT_GUARD_BASIUM_ALLY", 1)

def applyWBTheRadiantGuardChooseSidesHyborem(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer

	gc.getGame().setTrophyValue("TROPHY_WB_THE_RADIANT_GUARD_HYBOREM_ALLY", 1)
	gc.getGame().setTrophyValue("TROPHY_WB_THE_RADIANT_GUARD_BASIUM_ALLY", 0)
	pPlayer = gc.getPlayer(1) #Basium
	pCity = pPlayer.getCapitalCity()
	apUnitList = PyPlayer(0).getUnitList()
	for pLoopUnit in apUnitList:
		if gc.getUnitInfo(pLoopUnit.getUnitType()).getReligionType() == gc.getInfoTypeForString('RELIGION_THE_EMPYREAN'):
			szBuffer = CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_ABANDON", (pLoopUnit.getName(), ))
			CyInterface().addMessage(0,True,25,szBuffer,'',1,gc.getUnitInfo(pLoopUnit.getUnitType()).getButton(),ColorTypes(7),pLoopUnit.getX(),pLoopUnit.getY(),True,True)
			newUnit = pPlayer.initUnit(pLoopUnit.getUnitType(), pCity.getX(), pCity.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
			newUnit.convert(pLoopUnit)
	eTeam = gc.getTeam(0) #Falamar
	eTeam.setPermanentWarPeace(1, False)
	eTeam.setPermanentWarPeace(2, False)
	eTeam.declareWar(1, true, WarPlanTypes.WARPLAN_TOTAL)
	eTeam.makePeace(2)
	eTeam.setPermanentWarPeace(1, True)
	eTeam.setPermanentWarPeace(2, True)

def doWerewolf1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	pPlot = cf.findClearPlot(-1, pCity.plot())
	if pPlot != -1:
		bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
		bPlayer.initUnit(gc.getInfoTypeForString('UNIT_WEREWOLF'), pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.DIRECTION_SOUTH)
		CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_WEREWOLF_RELEASED", ()),'',1,'Art/Interface/Buttons/Units/Werewolf.dds',ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)

def doWerewolf3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	iPlayer = kTriggeredData.ePlayer
	pPlayer = gc.getPlayer(iPlayer)
	pCity = pPlayer.getCity(kTriggeredData.iCityId)
	CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_WEREWOLF_KILLED", ()),'',1,'Art/Interface/Buttons/Units/Werewolf.dds',ColorTypes(8),pCity.getX(),pCity.getY(),True,True)


######## MARATHON ###########

def canTriggerMarathon(argsList):	
	kTriggeredData = argsList[0]
	player = gc.getPlayer(kTriggeredData.ePlayer)
	otherPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
	team = gc.getTeam(player.getTeam())
	
	if (team.AI_getAtWarCounter(otherPlayer.getTeam()) == 1):
		(loopUnit, iter) = otherPlayer.firstUnit(false)
		while( loopUnit ):
			plot = loopUnit.plot()
			if (not plot.isNone()):
				if (plot.getOwner() == kTriggeredData.ePlayer):
					return true
			(loopUnit, iter) = otherPlayer.nextUnit(iter, false)

	return false


######## WEDDING FEUD ###########

def doWeddingFeud2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	
	player = gc.getPlayer(kTriggeredData.ePlayer)
	(loopCity, iter) = player.firstCity(false)

	while(loopCity):
		if loopCity.isHasReligion(kTriggeredData.eReligion):
			loopCity.changeHappinessTimer(30)
		(loopCity, iter) = player.nextCity(iter, false)
		
	return 1

def getHelpWeddingFeud2(argsList):
	iEvent = argsList[0]
	event = gc.getEventInfo(iEvent)
	kTriggeredData = argsList[1]
	religion = gc.getReligionInfo(kTriggeredData.eReligion)

	szHelp = localText.getText("TXT_KEY_EVENT_WEDDING_FEUD_2_HELP", (gc.getDefineINT("TEMP_HAPPY"), 30, religion.getChar()))

	return szHelp

def canDoWeddingFeud3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]

	player = gc.getPlayer(kTriggeredData.ePlayer)
	
	if player.getGold() - 10 * player.getNumCities() < 0:
		return false
				
	return true

def doWeddingFeud3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	
	destPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
	player = gc.getPlayer(kTriggeredData.ePlayer)
	
	for iLoopPlayer in range(gc.getMAX_CIV_PLAYERS()):
		loopPlayer = gc.getPlayer(iLoopPlayer)
		if loopPlayer.isAlive() and loopPlayer.getStateReligion() == player.getStateReligion():
			loopPlayer.AI_changeAttitudeExtra(kTriggeredData.ePlayer, 1)
			player.AI_changeAttitudeExtra(iLoopPlayer, 1)

	if gc.getTeam(destPlayer.getTeam()).canDeclareWar(player.getTeam()):			
		if destPlayer.isHuman():
			# this works only because it's a single-player only event
			popupInfo = CyPopupInfo()
			popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
			popupInfo.setText(localText.getText("TXT_KEY_EVENT_WEDDING_FEUD_OTHER_3", (gc.getReligionInfo(kTriggeredData.eReligion).getAdjectiveKey(), player.getCivilizationShortDescriptionKey())))
			popupInfo.setData1(kTriggeredData.eOtherPlayer)
			popupInfo.setData2(kTriggeredData.ePlayer)
			popupInfo.setPythonModule("CvRandomEventInterface")
			popupInfo.setOnClickedPythonCallback("weddingFeud3Callback")
			popupInfo.addPythonButton(localText.getText("TXT_KEY_POPUP_YES", ()), "")
			popupInfo.addPythonButton(localText.getText("TXT_KEY_POPUP_NO", ()), "")
			popupInfo.addPopup(kTriggeredData.eOtherPlayer)
		else:
			gc.getTeam(destPlayer.getTeam()).declareWar(player.getTeam(), false, WarPlanTypes.WARPLAN_LIMITED)
			
	return 1


def weddingFeud3Callback(argsList):
	iButton = argsList[0]
	iData1 = argsList[1]
	iData2 = argsList[2]
	iData3 = argsList[3]
	szText = argsList[4]
	bOption1 = argsList[5]
	bOption2 = argsList[6]
	
	if iButton == 0:
		destPlayer = gc.getPlayer(iData1)
		player = gc.getPlayer(iData2)
		gc.getTeam(destPlayer.getTeam()).declareWar(player.getTeam(), false, WarPlanTypes.WARPLAN_LIMITED)
	
	return 0

def getHelpWeddingFeud3(argsList):
	iEvent = argsList[0]
	event = gc.getEventInfo(iEvent)
	kTriggeredData = argsList[1]
	religion = gc.getReligionInfo(kTriggeredData.eReligion)

	szHelp = localText.getText("TXT_KEY_EVENT_WEDDING_FEUD_3_HELP", (1, religion.getChar()))

	return szHelp


######## BABY BOOM ###########

def canTriggerBabyBoom(argsList):
	kTriggeredData = argsList[0]
	player = gc.getPlayer(kTriggeredData.ePlayer)
	team = gc.getTeam(player.getTeam())

	if team.getAtWarCount(true) > 0:
		return false

	for iLoopTeam in range(gc.getMAX_CIV_TEAMS()):
		if iLoopTeam != player.getTeam():
			if team.AI_getAtPeaceCounter(iLoopTeam) == 1:
				return true

	return false


######## LOOTERS ###########

def getHelpLooters3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	otherPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
	city = otherPlayer.getCity(kTriggeredData.iOtherPlayerCityId)

	szHelp = localText.getText("TXT_KEY_EVENT_LOOTERS_3_HELP", (1, 2, city.getNameKey()))

	return szHelp

def canApplyLooters3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]

	otherPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
	city = otherPlayer.getCity(kTriggeredData.iOtherPlayerCityId)

	iNumBuildings = 0	
	for iBuilding in range(gc.getNumBuildingInfos()):
		if (city.getNumRealBuilding(iBuilding) > 0 and gc.getBuildingInfo(iBuilding).getProductionCost() <= 100 and gc.getBuildingInfo(iBuilding).getProductionCost() > 0  and not isLimitedWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
			iNumBuildings += 1
		
	return (iNumBuildings > 0)
	

def applyLooters3(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]

	otherPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
	city = otherPlayer.getCity(kTriggeredData.iOtherPlayerCityId)
	
	iNumBuildings = gc.getGame().getSorenRandNum(2, "Looters event number of buildings destroyed")
	iNumBuildingsDestroyed = 0

	listBuildings = []	
	for iBuilding in range(gc.getNumBuildingInfos()):
		if (city.getNumRealBuilding(iBuilding) > 0 and gc.getBuildingInfo(iBuilding).getProductionCost() <= 100 and gc.getBuildingInfo(iBuilding).getProductionCost() > 0  and not isLimitedWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
			listBuildings.append(iBuilding)

	for i in range(iNumBuildings+1):
		if len(listBuildings) > 0:
			iBuilding = listBuildings[gc.getGame().getSorenRandNum(len(listBuildings), "Looters event building destroyed")]
			szBuffer = localText.getText("TXT_KEY_EVENT_CITY_IMPROVEMENT_DESTROYED", (gc.getBuildingInfo(iBuilding).getTextKey(), ))
			CyInterface().addMessage(kTriggeredData.eOtherPlayer, false, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BOMBARDED", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getBuildingInfo(iBuilding).getButton(), gc.getInfoTypeForString("COLOR_RED"), city.getX(), city.getY(), true, true)
			city.setNumRealBuilding(iBuilding, 0)
			iNumBuildingsDestroyed += 1
			listBuildings.remove(iBuilding)
				
	if iNumBuildingsDestroyed > 0:
		szBuffer = localText.getText("TXT_KEY_EVENT_NUM_BUILDINGS_DESTROYED", (iNumBuildingsDestroyed, gc.getPlayer(kTriggeredData.eOtherPlayer).getCivilizationAdjectiveKey(), city.getNameKey()))
		CyInterface().addMessage(kTriggeredData.ePlayer, false, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BOMBARDED", InterfaceMessageTypes.MESSAGE_TYPE_INFO, None, gc.getInfoTypeForString("COLOR_WHITE"), -1, -1, true, true)


######## BROTHERS IN NEED ###########

def canTriggerBrothersInNeed(argsList):
	kTriggeredData = argsList[0]
	trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
	player = gc.getPlayer(kTriggeredData.ePlayer)
	otherPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
	
	if not player.canTradeNetworkWith(kTriggeredData.eOtherPlayer):
		return false
	
	listResources = []
	listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_COPPER'))
	listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_IRON'))
	listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_HORSE'))
	listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_IVORY'))

#FfH: Modified by Kael 10/01/2007
#	listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_OIL'))
#	listResources.append(CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_URANIUM'))
#FfH: End Modify
	
	bFound = false
	for iResource in listResources: 
		if (player.getNumTradeableBonuses(iResource) > 1 and otherPlayer.getNumAvailableBonuses(iResource) <= 0):
			bFound = true
			break
		
	if not bFound:
		return false
		
	for iTeam in range(gc.getMAX_CIV_TEAMS()):
		if iTeam != player.getTeam() and iTeam != otherPlayer.getTeam() and gc.getTeam(iTeam).isAlive():
			if gc.getTeam(iTeam).isAtWar(otherPlayer.getTeam()) and not gc.getTeam(iTeam).isAtWar(player.getTeam()):
				return true
			
	return false
	
def canDoBrothersInNeed1(argsList):
	kTriggeredData = argsList[1]
	newArgs = (kTriggeredData, )
	
	return canTriggerBrothersInNeed(newArgs)


######## HURRICANE ###########

def canTriggerHurricaneCity(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iCity = argsList[2]
	
	player = gc.getPlayer(ePlayer)
	city = player.getCity(iCity)
	
	if city.isNone():
		return false
		
	if not city.isCoastal(gc.getMIN_WATER_SIZE_FOR_OCEAN()):
		return false
		
	if city.plot().getLatitude() <= 0:
		return false
		
	if city.getPopulation() < 2:
		return false
		
	return true

def canApplyHurricane1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	
	player = gc.getPlayer(kTriggeredData.ePlayer)
	city = player.getCity(kTriggeredData.iCityId)
	
	listBuildings = []	
	for iBuilding in range(gc.getNumBuildingInfos()):
		if (city.getNumRealBuilding(iBuilding) > 0 and gc.getBuildingInfo(iBuilding).getProductionCost() > 0 and not isLimitedWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
			listBuildings.append(iBuilding)
			
	return (len(listBuildings) > 0)

def canApplyHurricane2(argsList):			
	return (not canApplyHurricane1(argsList))

		
def applyHurricane1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	
	player = gc.getPlayer(kTriggeredData.ePlayer)
	city = player.getCity(kTriggeredData.iCityId)
	
	listCheapBuildings = []	
	listExpensiveBuildings = []	
	for iBuilding in range(gc.getNumBuildingInfos()):
		if (city.getNumRealBuilding(iBuilding) > 0 and gc.getBuildingInfo(iBuilding).getProductionCost() <= 100 and gc.getBuildingInfo(iBuilding).getProductionCost() > 0 and not isLimitedWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
			listCheapBuildings.append(iBuilding)
		if (city.getNumRealBuilding(iBuilding) > 0 and gc.getBuildingInfo(iBuilding).getProductionCost() > 100 and gc.getBuildingInfo(iBuilding).getProductionCost() > 0 and not isLimitedWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType())):
			listExpensiveBuildings.append(iBuilding)

	if len(listCheapBuildings) > 0:
		iBuilding = listCheapBuildings[gc.getGame().getSorenRandNum(len(listCheapBuildings), "Hurricane event cheap building destroyed")]
		szBuffer = localText.getText("TXT_KEY_EVENT_CITY_IMPROVEMENT_DESTROYED", (gc.getBuildingInfo(iBuilding).getTextKey(), ))
		CyInterface().addMessage(kTriggeredData.ePlayer, false, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BOMBARDED", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getBuildingInfo(iBuilding).getButton(), gc.getInfoTypeForString("COLOR_RED"), city.getX(), city.getY(), true, true)
		city.setNumRealBuilding(iBuilding, 0)

	if len(listExpensiveBuildings) > 0:
		iBuilding = listExpensiveBuildings[gc.getGame().getSorenRandNum(len(listExpensiveBuildings), "Hurricane event expensive building destroyed")]
		szBuffer = localText.getText("TXT_KEY_EVENT_CITY_IMPROVEMENT_DESTROYED", (gc.getBuildingInfo(iBuilding).getTextKey(), ))
		CyInterface().addMessage(kTriggeredData.ePlayer, false, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BOMBARDED", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getBuildingInfo(iBuilding).getButton(), gc.getInfoTypeForString("COLOR_RED"), city.getX(), city.getY(), true, true)
		city.setNumRealBuilding(iBuilding, 0)

		
######## CYCLONE ###########

def canTriggerCycloneCity(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iCity = argsList[2]
	
	player = gc.getPlayer(ePlayer)
	city = player.getCity(iCity)
	
	if city.isNone():
		return false
		
	if not city.isCoastal(gc.getMIN_WATER_SIZE_FOR_OCEAN()):
		return false
		
	if city.plot().getLatitude() >= 0:
		return false
		
	return true

		
######## MONSOON ###########

def canTriggerMonsoonCity(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iCity = argsList[2]
	
	player = gc.getPlayer(ePlayer)
	city = player.getCity(iCity)
	
	if city.isNone():
		return false
		
	if city.isCoastal(gc.getMIN_WATER_SIZE_FOR_OCEAN()):
		return false
		
	iJungleType = CvUtil.findInfoTypeNum(gc.getFeatureInfo, gc.getNumFeatureInfos(),'FEATURE_JUNGLE')
		
	for iDX in range(-3, 4):
		for iDY in range(-3, 4):
			pLoopPlot = plotXY(city.getX(), city.getY(), iDX, iDY)
			if not pLoopPlot.isNone() and pLoopPlot.getFeatureType() == iJungleType:
				return true
				
	return false


######## VOLCANO ###########

def getHelpVolcano1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]

	szHelp = localText.getText("TXT_KEY_EVENT_VOLCANO_1_HELP", ())

	return szHelp

def canApplyVolcano1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	
	iNumImprovements = 0
	for iDX in range(-1, 2):
		for iDY in range(-1, 2):
			loopPlot = plotXY(kTriggeredData.iPlotX, kTriggeredData.iPlotY, iDX, iDY)
			if not loopPlot.isNone():
				if (iDX != 0 or iDY != 0):
					if loopPlot.getImprovementType() != -1:
						iNumImprovements += 1

	return (iNumImprovements > 0)

def applyVolcano1(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	
	listPlots = []
	for iDX in range(-1, 2):
		for iDY in range(-1, 2):
			loopPlot = plotXY(kTriggeredData.iPlotX, kTriggeredData.iPlotY, iDX, iDY)
			if not loopPlot.isNone():
				if (iDX != 0 or iDY != 0):
					if loopPlot.getImprovementType() != -1:
						listPlots.append(loopPlot)
					
	listRuins = []
	listRuins.append(CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_COTTAGE'))
	listRuins.append(CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_HAMLET'))
	listRuins.append(CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_VILLAGE'))
	listRuins.append(CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_TOWN'))
	
	iRuins = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_CITY_RUINS')

	for i in range(3):
		if len(listPlots) > 0:
			plot = listPlots[gc.getGame().getSorenRandNum(len(listPlots), "Volcano event improvement destroyed")]
			iImprovement = plot.getImprovementType()
			szBuffer = localText.getText("TXT_KEY_EVENT_CITY_IMPROVEMENT_DESTROYED", (gc.getImprovementInfo(iImprovement).getTextKey(), ))
			CyInterface().addMessage(kTriggeredData.ePlayer, false, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BOMBARDED", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getImprovementInfo(iImprovement).getButton(), gc.getInfoTypeForString("COLOR_RED"), plot.getX(), plot.getY(), true, true)
			if iImprovement in listRuins:
				plot.setImprovementType(iRuins)
			else:
				plot.setImprovementType(-1)
			listPlots.remove(plot)
			
			if i == 1 and gc.getGame().getSorenRandNum(100, "Volcano event num improvements destroyed") < 50:
				break


######## DUSTBOWL ###########

def canTriggerDustbowlCont(argsList):
	kTriggeredData = argsList[0]

	trigger = gc.getEventTriggerInfo(kTriggeredData.eTrigger)
	player = gc.getPlayer(kTriggeredData.ePlayer)
	
	kOrigTriggeredData = player.getEventOccured(trigger.getPrereqEvent(0))
	
	if (kOrigTriggeredData == None):
		return false

	iFarmType = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_FARM')
	iPlainsType = CvUtil.findInfoTypeNum(gc.getTerrainInfo,gc.getNumTerrainInfos(),'TERRAIN_PLAINS')
	
	map = gc.getMap()
	iBestValue = map.getGridWidth() + map.getGridHeight()
	bestPlot = None
	for i in range(map.numPlots()):
		plot = map.plotByIndex(i)
		if (plot.getOwner() == kTriggeredData.ePlayer and plot.getImprovementType() == iFarmType and plot.getTerrainType() == iPlainsType):
			iValue = plotDistance(kOrigTriggeredData.iPlotX, kOrigTriggeredData.iPlotY, plot.getX(), plot.getY())
			if iValue < iBestValue:
				iBestValue = iValue
				bestPlot = plot
				
	if bestPlot != None:
		kActualTriggeredDataObject = player.getEventTriggered(kTriggeredData.iId)
		kActualTriggeredDataObject.iPlotX = bestPlot.getX()
		kActualTriggeredDataObject.iPlotY = bestPlot.getY()
	else:
		player.resetEventOccured(trigger.getPrereqEvent(0))
		return false
		
	return true

def getHelpDustBowl2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]

	szHelp = localText.getText("TXT_KEY_EVENT_DUSTBOWL_2_HELP", ())

	return szHelp

	
######## CHAMPION ###########

def canTriggerChampion(argsList):	
	kTriggeredData = argsList[0]
	
	player = gc.getPlayer(kTriggeredData.ePlayer)
	team = gc.getTeam(player.getTeam())

	if team.getAtWarCount(true) > 0:
		return false
				
	return true
	
def canTriggerChampionUnit(argsList):
	eTrigger = argsList[0]
	ePlayer = argsList[1]
	iUnit = argsList[2]
	
	player = gc.getPlayer(ePlayer)
	unit = player.getUnit(iUnit)
	
	if unit.isNone():
		return false
		
	if unit.getDamage() > 0:
		return false
		
	if unit.getExperience() < 3:
		return false

#FfH: Modified by Kael 09/26/2007
#	iLeadership = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_LEADERSHIP')
	iLeadership = gc.getInfoTypeForString('PROMOTION_HERO')
#FfH: End Modify

	if unit.isHasPromotion(iLeadership):
		return false

	return true
	
def applyChampion(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]

	player = gc.getPlayer(kTriggeredData.ePlayer)
	unit = player.getUnit(kTriggeredData.iUnitId)

#FfH: Modified by Kael 10/01/2007
#	iLeadership = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_LEADERSHIP')
	iLeadership = gc.getInfoTypeForString('PROMOTION_HERO')
#FfH: End Modify
	
	unit.setHasPromotion(iLeadership, true)
	
def getHelpChampion(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	
	player = gc.getPlayer(kTriggeredData.ePlayer)
	unit = player.getUnit(kTriggeredData.iUnitId)
	
#FfH: Modified by Kael 09/26/2007
#	iLeadership = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_LEADERSHIP')
	iLeadership = gc.getInfoTypeForString('PROMOTION_HERO')
#FfH: End Modify

	szHelp = localText.getText("TXT_KEY_EVENT_CHAMPION_HELP", (unit.getNameKey(), gc.getPromotionInfo(iLeadership).getTextKey()))	

	return szHelp


######## ANTELOPE ###########

def canTriggerAntelope(argsList):

	kTriggeredData = argsList[0]
	player = gc.getPlayer(kTriggeredData.ePlayer)
	
	iDeer = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_DEER')
	iHappyBonuses = 0
	bDeer = false
	for i in range(gc.getNumBonusInfos()):
		bonus = gc.getBonusInfo(i)
		iNum = player.getNumAvailableBonuses(i)
		if iNum > 0 :
			if bonus.getHappiness() > 0:
				iHappyBonuses += 1
				if iHappyBonuses > 5:
					return false
			if i == iDeer:
				return false	

	plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	if not plot.canHaveBonus(iDeer, false):
		return false
				
	return true

def doAntelope2(argsList):
#	Need this because camps are not normally allowed unless there is already deer.
	iEvent = argsList[0]
	kTriggeredData = argsList[1]

	plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	
	if not plot.isNone():
		plot.setImprovementType(CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_CAMP'))
	
	return 1

def getHelpAntelope2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	
	iCamp = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_CAMP')
	szHelp = localText.getText("TXT_KEY_EVENT_IMPROVEMENT_GROWTH", ( gc.getImprovementInfo(iCamp).getTextKey(), ))

	return szHelp


######## WHALEOFATHING ###########

def canTriggerWhaleOfAThing(argsList):

	kTriggeredData = argsList[0]
	player = gc.getPlayer(kTriggeredData.ePlayer)
	
	iWhale = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_WHALE')
	iHappyBonuses = 0
	bWhale = false
	for i in range(gc.getNumBonusInfos()):
		bonus = gc.getBonusInfo(i)
		iNum = player.getNumAvailableBonuses(i)
		if iNum > 0 :
			if bonus.getHappiness() > 0:
				iHappyBonuses += 1
				if iHappyBonuses > 5:
					return false
			if i == iWhale:
				return false

	plot = gc.getMap().plot(kTriggeredData.iPlotX, kTriggeredData.iPlotY)
	if not plot.canHaveBonus(iWhale, false):
		return false
		
	return true

######## ANCIENT OLYMPICS ###########

def doAncientOlympics2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]

	map = gc.getMap()

	for j in range(gc.getMAX_CIV_PLAYERS()):
		loopPlayer = gc.getPlayer(j)
		if j != kTriggeredData.ePlayer and loopPlayer.isAlive() and not loopPlayer.isMinorCiv():

			for i in range(map.numPlots()):
				plot = map.plotByIndex(i)
				if not plot.isWater() and plot.getOwner() == kTriggeredData.ePlayer and plot.isAdjacentPlayer(j, true):
					loopPlayer.AI_changeMemoryCount(kTriggeredData.ePlayer, MemoryTypes.MEMORY_EVENT_GOOD_TO_US, 1)
					break
		
	return 1

def getHelpModernOlympics(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	
	szHelp = localText.getText("TXT_KEY_EVENT_SOLO_FLIGHT_HELP_1", (1, ))	

	return szHelp


######## HEROIC_GESTURE ###########

def canTriggerHeroicGesture(argsList):
	kTriggeredData = argsList[0]
	player = gc.getPlayer(kTriggeredData.ePlayer)
	destPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)

	if not gc.getTeam(destPlayer.getTeam()).canChangeWarPeace(player.getTeam()):
		return false
		
	if gc.getTeam(destPlayer.getTeam()).AI_getWarSuccess(player.getTeam()) <= 0:
		return false

	if gc.getTeam(player.getTeam()).AI_getWarSuccess(destPlayer.getTeam()) <= 0:
		return false
	
	return true

def doHeroicGesture2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]

	destPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
	player = gc.getPlayer(kTriggeredData.ePlayer)
	
	if destPlayer.isHuman():
		# this works only because it's a single-player only event
		popupInfo = CyPopupInfo()
		popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
		popupInfo.setText(localText.getText("TXT_KEY_EVENT_HEROIC_GESTURE_OTHER_3", (player.getCivilizationAdjectiveKey(), )))
		popupInfo.setData1(kTriggeredData.eOtherPlayer)
		popupInfo.setData2(kTriggeredData.ePlayer)
		popupInfo.setPythonModule("CvRandomEventInterface")
		popupInfo.setOnClickedPythonCallback("heroicGesture2Callback")
		popupInfo.addPythonButton(localText.getText("TXT_KEY_POPUP_YES", ()), "")
		popupInfo.addPythonButton(localText.getText("TXT_KEY_POPUP_NO", ()), "")
		popupInfo.addPopup(kTriggeredData.eOtherPlayer)
	else:
		destPlayer.forcePeace(kTriggeredData.ePlayer)
		destPlayer.AI_changeAttitudeExtra(kTriggeredData.ePlayer, 1)
		player.AI_changeAttitudeExtra(kTriggeredData.eOtherPlayer, 1)

	return

def heroicGesture2Callback(argsList):
	iButton = argsList[0]
	iData1 = argsList[1]
	iData2 = argsList[2]
	iData3 = argsList[3]
	szText = argsList[4]
	bOption1 = argsList[5]
	bOption2 = argsList[6]
	
	if iButton == 0:
		destPlayer = gc.getPlayer(iData1)
		player = gc.getPlayer(iData2)
		destPlayer.forcePeace(iData2)
		destPlayer.AI_changeAttitudeExtra(iData2, 1)
		player.AI_changeAttitudeExtra(iData1, 1)		

	return 0
	
def getHelpHeroicGesture2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	
	destPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)

	# Get help text
	szHelp = localText.getText("TXT_KEY_EVENT_ATTITUDE_GOOD", (1, destPlayer.getNameKey()));

	return szHelp


######## GREAT_MEDIATOR ###########

def canTriggerGreatMediator(argsList):
	kTriggeredData = argsList[0]
	player = gc.getPlayer(kTriggeredData.ePlayer)
	destPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)

	if not gc.getTeam(player.getTeam()).canChangeWarPeace(destPlayer.getTeam()):
		return false
		
	if gc.getTeam(player.getTeam()).AI_getAtWarCounter(destPlayer.getTeam()) < 10:
		return false

	return true

def doGreatMediator2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]

	destPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)
	player = gc.getPlayer(kTriggeredData.ePlayer)
	
	if destPlayer.isHuman():
		# this works only because it's a single-player only event
		popupInfo = CyPopupInfo()
		popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
		popupInfo.setText(localText.getText("TXT_KEY_EVENT_GREAT_MEDIATOR_OTHER_3", (player.getCivilizationAdjectiveKey(), )))
		popupInfo.setData1(kTriggeredData.eOtherPlayer)
		popupInfo.setData2(kTriggeredData.ePlayer)
		popupInfo.setPythonModule("CvRandomEventInterface")
		popupInfo.setOnClickedPythonCallback("greatMediator2Callback")
		popupInfo.addPythonButton(localText.getText("TXT_KEY_POPUP_YES", ()), "")
		popupInfo.addPythonButton(localText.getText("TXT_KEY_POPUP_NO", ()), "")
		popupInfo.addPopup(kTriggeredData.eOtherPlayer)
	else:
		gc.getTeam(player.getTeam()).makePeace(destPlayer.getTeam())
		destPlayer.AI_changeAttitudeExtra(kTriggeredData.ePlayer, 1)
		player.AI_changeAttitudeExtra(kTriggeredData.eOtherPlayer, 1)

	return

def greatMediator2Callback(argsList):
	iButton = argsList[0]
	iData1 = argsList[1]
	iData2 = argsList[2]
	iData3 = argsList[3]
	szText = argsList[4]
	bOption1 = argsList[5]
	bOption2 = argsList[6]
	
	if iButton == 0:
		destPlayer = gc.getPlayer(iData1)
		player = gc.getPlayer(iData2)
		gc.getTeam(destPlayer.getTeam()).makePeace(player.getTeam())
		destPlayer.AI_changeAttitudeExtra(iData2, 1)
		player.AI_changeAttitudeExtra(iData1, 1)		

	return 0
	
def getHelpGreatMediator2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	
	destPlayer = gc.getPlayer(kTriggeredData.eOtherPlayer)

	# Get help text
	szHelp = localText.getText("TXT_KEY_EVENT_ATTITUDE_GOOD", (1, destPlayer.getNameKey()));

	return szHelp


######## ANCIENT_TEXTS ###########

def doAncientTexts2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]

	for iPlayer in range(gc.getMAX_CIV_PLAYERS()):			
		loopPlayer = gc.getPlayer(iPlayer)
		if loopPlayer.isAlive() and iPlayer != kTriggeredData.ePlayer:
			loopTeam = gc.getTeam(loopPlayer.getTeam())
			if loopTeam.isHasMet(gc.getPlayer(kTriggeredData.ePlayer).getTeam()):
				loopPlayer.AI_changeAttitudeExtra(kTriggeredData.ePlayer, 1)

	return

def getHelpAncientTexts2(argsList):
	iEvent = argsList[0]
	kTriggeredData = argsList[1]
	
	szHelp = localText.getText("TXT_KEY_EVENT_SOLO_FLIGHT_HELP_1", (1, ))	

	return szHelp


######## LITERACY ###########

def canTriggerLiteracy(argsList):

	kTriggeredData = argsList[0]
	player = gc.getPlayer(kTriggeredData.ePlayer)
	
	iLibrary = CvUtil.findInfoTypeNum(gc.getBuildingClassInfo, gc.getNumBuildingClassInfos(), 'BUILDINGCLASS_LIBRARY')
	if player.getNumCities() > player.getBuildingClassCount(iLibrary):
		return false
	
	return true

######## ESTEEMEED_PLAYWRIGHT ###########

def canTriggerEsteemedPlaywright(argsList):
	kTriggeredData = argsList[0]
	player = gc.getPlayer(kTriggeredData.ePlayer)
	
	# If source civ is operating this Civic, disallow the event to trigger.
	if player.isCivic(CvUtil.findInfoTypeNum(gc.getCivicInfo,gc.getNumCivicInfos(),'CIVIC_SLAVERY')):
		return false

	return true


######## EXPERIENCED_CAPTAIN ###########

def canTriggerExperiencedCaptain(argsList):
	kTriggeredData = argsList[0]
	
	player = gc.getPlayer(kTriggeredData.ePlayer)
	unit = player.getUnit(kTriggeredData.iUnitId)
	
	if unit.isNone():
		return false
		
	if unit.getExperience() < 7:
		return false

	return true


######## Great Beast ########

def doGreatBeast3(argsList):
	kTriggeredData = argsList[1]
	
	player = gc.getPlayer(kTriggeredData.ePlayer)
	(loopCity, iter) = player.firstCity(false)

	while(loopCity):
		if loopCity.isHasReligion(kTriggeredData.eReligion):
			loopCity.changeHappinessTimer(40)
		(loopCity, iter) = player.nextCity(iter, false)

def getHelpGreatBeast3(argsList):
	kTriggeredData = argsList[1]
	religion = gc.getReligionInfo(kTriggeredData.eReligion)

	szHelp = localText.getText("TXT_KEY_EVENT_GREAT_BEAST_3_HELP", (gc.getDefineINT("TEMP_HAPPY"), 40, religion.getChar()))

	return szHelp


####### Controversial Philosopher ######

def canTriggerControversialPhilosopherCity(argsList):
	ePlayer = argsList[1]
	iCity = argsList[2]
	
	player = gc.getPlayer(ePlayer)
	city = player.getCity(iCity)
	
	if city.isNone():
		return false
	if (not city.isCapital()):
		return false
	if (city.getCommerceRateTimes100(CommerceTypes.COMMERCE_RESEARCH) < 3500):
		return false

	return true

