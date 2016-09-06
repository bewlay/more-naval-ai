## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005

from CvPythonExtensions import *
import CvUtil
import Popup as PyPopup
import PyHelpers
import CvScreenEnums
import CvCameraControls

# globals
gc = CyGlobalContext()
PyPlayer = PyHelpers.PyPlayer

class CustomFunctions:


	# Set up containers for cached data.
	def __init__(self):
		self.__siIgnoreFire = set()

	@property
	def siIgnoreFire(self):
		# Cached data is initialized the first time that it is read. This prevents assertions while the game is loading.
		if len(self.__siIgnoreFire) > 0:
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_ANOINTED'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_BLESSED'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_CONSECRATED'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_DIVINE'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_EXALTED'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_FINAL'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_DEMONIC_CITIZENS'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_DWARVEN_VAULT'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_DWARVEN_VAULT_ABUNDANT'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_DWARVEN_VAULT_EMPTY'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_DWARVEN_VAULT_FULL'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_DWARVEN_VAULT_LOW'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_DWARVEN_VAULT_OVERFLOWING'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_DWARVEN_VAULT_STOCKED'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_TOWER_OF_ALTERATION'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_TOWER_OF_DIVINATION'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_TOWER_OF_MASTERY'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_TOWER_OF_NECROMANCY'))
			self.__siIgnoreFire.add(gc.getInfoTypeForString('BUILDING_TOWER_OF_THE_ELEMENTS'))

		return self.__siIgnoreFire


	def addBonus(self, iBonus, iNum, sIcon):
		listPlots = []
		for i in range (CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			if (pPlot.canHaveBonus(gc.getInfoTypeForString(iBonus),True) and pPlot.getBonusType(-1) == -1 and pPlot.isCity() == False):
				listPlots.append(i)
		if len(listPlots) > 0:
			for i in range (iNum):
				iRnd = CyGame().getSorenRandNum(len(listPlots), "Add Bonus")
				pPlot = CyMap().plotByIndex(listPlots[iRnd])
				pPlot.setBonusType(gc.getInfoTypeForString(iBonus))
				if sIcon != -1:
					iActivePlayer = CyGame().getActivePlayer()
					CyInterface().addMessage(iActivePlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_RESOURCE_DISCOVERED",()),'AS2D_DISCOVERBONUS',1,sIcon,ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)

	def addPopup(self, szText, sDDS):
		szTitle = CyGameTextMgr().getTimeStr(CyGame().getGameTurn(), False)
		popup = PyPopup.PyPopup(-1)
		popup.addDDS(sDDS, 0, 0, 128, 384)
		popup.addSeparator()
		popup.setHeaderString(szTitle)
		popup.setBodyString(szText)
		popup.launch(True, PopupStates.POPUPSTATE_IMMEDIATE)

	def addPlayerPopup(self, szText, iPlayer):
		popupInfo = CyPopupInfo()
		popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
		popupInfo.setText(szText)
		popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_CLOSE", ()), "")
		popupInfo.addPopup(iPlayer)

	def addUnit(self, iUnit):
		pBestPlot = -1
		iBestPlot = -1
		for i in range (CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			iPlot = -1
			if pPlot.isWater() == False:
				if pPlot.getNumUnits() == 0:
					if pPlot.isCity() == False:
						if pPlot.isImpassable() == False:
							iPlot = CyGame().getSorenRandNum(500, "Add Unit")
							iPlot = iPlot + (pPlot.area().getNumTiles() * 10)
							if pPlot.isBarbarian():
								iPlot = iPlot + 200
							if pPlot.isOwned():
								iPlot = iPlot / 2
							if iPlot > iBestPlot:
								iBestPlot = iPlot
								pBestPlot = pPlot
		if iBestPlot != -1:
			bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
			newUnit = bPlayer.initUnit(iUnit, pBestPlot.getX(), pBestPlot.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)

	def addUnitFixed(self, caster, iUnit):
		pPlot = caster.plot()
		pNewPlot = self.findClearPlot(-1, pPlot)
		if pNewPlot != -1:
			pPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
			newUnit = pPlayer.initUnit(iUnit, pNewPlot.getX(), pNewPlot.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
			return newUnit
		return -1

	def doCrusade(self, iPlayer):
		iCrusadeChance = gc.getDefineINT('CRUSADE_SPAWN_CHANCE')
		iDemagog = gc.getInfoTypeForString('UNIT_DEMAGOG')
		iTown = gc.getInfoTypeForString('IMPROVEMENT_TOWN')
		iVillage = gc.getInfoTypeForString('IMPROVEMENT_VILLAGE')
		pPlayer = gc.getPlayer(iPlayer)
		for i in range (CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			if pPlot.getImprovementType() == iTown:
				if pPlot.getOwner() == iPlayer :
##--------		Unofficial Bug Fix: Added by Denev		--------##
# To prevent spawning demagog in the same tile with his enemy unit.
					if not pPlot.isVisibleEnemyUnit(iPlayer):
##--------		Unofficial Bug Fix: End Add				--------##
						if CyGame().getSorenRandNum(100, "Crusade") < iCrusadeChance:
							newUnit = pPlayer.initUnit(iDemagog, pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)
							pPlot.setImprovementType(iVillage)

	def doFear(self, pVictim, pPlot, pCaster, bResistable):
		if pVictim.isImmuneToFear():
			return False
		if bResistable:
			if CyGame().getSorenRandNum(100, "Crusade") < pVictim.getResistChance(pCaster, gc.getInfoTypeForString('SPELL_ROAR')):
				return False
		iX = pVictim.getX()
		iY = pVictim.getY()
		pBestPlot = -1
		iBestPlot = 0
		for iiX in range(iX-1, iX+2, 1):
			for iiY in range(iY-1, iY+2, 1):
				pLoopPlot = CyMap().plot(iiX,iiY)
				if not pLoopPlot.isNone():
					if not pLoopPlot.isVisibleEnemyUnit(pVictim.getOwner()):
						if pVictim.canMoveOrAttackInto(pLoopPlot, False):
							if (abs(pLoopPlot.getX() - pPlot.getX())>1) or (abs(pLoopPlot.getY() - pPlot.getY())>1):
								iRnd = CyGame().getSorenRandNum(500, "Fear")
								if iRnd > iBestPlot:
									iBestPlot = iRnd
									pBestPlot = pLoopPlot
		if pBestPlot != -1:
			pVictim.setXY(pBestPlot.getX(), pBestPlot.getY(), False, True, True)
			return True
		return False

	def exploreLairBigBad(self, caster):
		iPlayer = caster.getOwner()
		pPlot = caster.plot()
		pPlayer = gc.getPlayer(caster.getOwner())

		lList = ['UNIT_AZER']
		lPromoList = ['PROMOTION_MUTATED', 'PROMOTION_CANNIBALIZE', 'PROMOTION_MOBILITY1', 'PROMOTION_STRONG', 'PROMOTION_BLITZ', 'PROMOTION_COMMAND1', 'PROMOTION_HEROIC_STRENGTH', 'PROMOTION_HEROIC_DEFENSE', 'PROMOTION_MAGIC_IMMUNE', 'PROMOTION_STONESKIN', 'PROMOTION_VALOR', 'PROMOTION_VILE_TOUCH']
		lHenchmanList = ['UNIT_GRIFFON']
		if self.grace() == False:
			lList = lList + ['UNIT_AIR_ELEMENTAL']
		if not pPlot.isWater():
			lList = lList + ['UNIT_ASSASSIN', 'UNIT_OGRE', 'UNIT_GIANT_SPIDER', 'UNIT_HILL_GIANT', 'UNIT_SPECTRE', 'UNIT_SCORPION']
			lHenchmanList = lHenchmanList + ['UNIT_AXEMAN', 'UNIT_WOLF', 'UNIT_CHAOS_MARAUDER', 'UNIT_WOLF_RIDER', 'UNIT_MISTFORM', 'UNIT_LION', 'UNIT_TIGER', 'UNIT_BABY_SPIDER', 'UNIT_FAWN', 'UNIT_SCORPION']
			if self.grace() == False:
				lList = lList + ['UNIT_EARTH_ELEMENTAL', 'UNIT_FIRE_ELEMENTAL', 'UNIT_GARGOYLE', 'UNIT_VAMPIRE', 'UNIT_MYCONID', 'UNIT_EIDOLON', 'UNIT_LICH', 'UNIT_OGRE_WARCHIEF', 'UNIT_SATYR', 'UNIT_WEREWOLF']
				lPromoList = lPromoList + ['PROMOTION_FIRE2', 'PROMOTION_AIR2', 'PROMOTION_HERO', 'PROMOTION_MARKSMAN', 'PROMOTION_SHADOWWALK']
				lHenchmanList = lHenchmanList + ['UNIT_OGRE']
				if pPlot.getFeatureType() == gc.getInfoTypeForString('FEATURE_FOREST'):
					lList = lList + ['UNIT_TREANT']
			if pPlot.getTerrainType() == gc.getInfoTypeForString('TERRAIN_SNOW'):
				lHenchmanList = lHenchmanList + ['UNIT_FROSTLING_ARCHER', 'UNIT_FROSTLING_WOLF_RIDER', 'UNIT_POLAR_BEAR']
			if pPlot.getImprovementType() == gc.getInfoTypeForString('IMPROVEMENT_BARROW'):
				lPromoList = lPromoList + ['PROMOTION_DEATH2']
				lHenchmanList = lHenchmanList + ['UNIT_SKELETON', 'UNIT_PYRE_ZOMBIE']
				if self.grace() == False:
					lList = lList + ['UNIT_WRAITH']
			if pPlot.getImprovementType() == gc.getInfoTypeForString('IMPROVEMENT_RUINS'):
				lPromoList = lPromoList + ['PROMOTION_POISONED_BLADE']
				lHenchmanList = lHenchmanList + ['UNIT_LIZARDMAN', 'UNIT_GORILLA']
				if self.grace() == False:
					lList = lList + ['UNIT_MANTICORE']
			if CyGame().getGlobalCounter() > 40:
				lList = lList + ['UNIT_PIT_BEAST', 'UNIT_DEATH_KNIGHT', 'UNIT_BALOR']
				lPromoList = lPromoList + ['PROMOTION_FEAR']
				lHenchmanList = lHenchmanList + ['UNIT_IMP', 'UNIT_HELLHOUND']
		if pPlot.isWater():
			lList = lList + ['UNIT_SEA_SERPENT', 'UNIT_STYGIAN_GUARD', 'UNIT_PIRATE']
			lHenchmanList = lHenchmanList + ['UNIT_DROWN']
			if self.grace() == False:
				lList = lList + ['UNIT_WATER_ELEMENTAL', 'UNIT_KRAKEN']

		sMonster = lList[CyGame().getSorenRandNum(len(lList), "Pick Monster")-1]
		sHenchman = lHenchmanList[CyGame().getSorenRandNum(len(lHenchmanList), "Pick Henchman")-1]
		sPromo = lPromoList[CyGame().getSorenRandNum(len(lPromoList), "Pick Promotion")-1]
		iUnit = gc.getInfoTypeForString(sMonster)
		iHenchman = gc.getInfoTypeForString(sHenchman)
		newUnit = self.addUnitFixed(caster,iUnit)
		if newUnit != -1:
			newUnit.setHasPromotion(gc.getInfoTypeForString(sPromo), True)
			newUnit.setName(self.MarnokNameGenerator(newUnit))
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_BIGBAD",()),'',1,gc.getUnitInfo(iUnit).getButton(),ColorTypes(7),newUnit.getX(),newUnit.getY(),True,True)
			bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
			for i in range (CyGame().getSorenRandNum(5, "Pick Henchmen")):
				bPlayer.initUnit(iHenchman, newUnit.getX(), newUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
		return 0

	def exploreLairBad(self, caster):
		iPlayer = caster.getOwner()
		pPlot = caster.plot()
		pPlayer = gc.getPlayer(caster.getOwner())

		lList = ['COLLAPSE']
		if caster.getLevel() == 1:
			lList = lList + ['DEATH']
		if caster.isAlive():
			lList = lList + ['CRAZED', 'DEMONIC_POSSESSION', 'DISEASED', 'ENRAGED', 'PLAGUED', 'POISONED', 'WITHERED']
		if caster.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_MELEE'):
			lList = lList + ['RUSTED']
		if pPlot.isWater():
			lList = lList + ['SPAWN_DROWN', 'SPAWN_SEA_SERPENT']
		if not pPlot.isWater():
			lList = lList + ['SPAWN_SPIDER', 'SPAWN_SPECTRE']
		if pPlot.getImprovementType() == gc.getInfoTypeForString('IMPROVEMENT_GOBLIN_FORT'):
			lList = lList + ['SPAWN_SCORPION_BAD', 'SPAWN_SCORPION_BAD', 'SPAWN_SCORPION_BAD']

		sGoody = lList[CyGame().getSorenRandNum(len(lList), "Pick Goody")-1]
		if sGoody == 'DEATH':
			caster.kill(True,0)
			CyInterface().addMessage(caster.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_DEATH", ()),'',1,'Art/Interface/Buttons/Spells/Explore Lair.dds',ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)
			return 0
		if sGoody == 'COLLAPSE':
			caster.doDamageNoCaster(50, 90, gc.getInfoTypeForString('DAMAGE_PHYSICAL'), False)
			CyInterface().addMessage(caster.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_COLLAPSE", ()),'',1,'Art/Interface/Buttons/Spells/Explore Lair.dds',ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)
			return 100
		if sGoody == 'CRAZED':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_CRAZED'), True)
			CyInterface().addMessage(caster.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_CRAZED", ()),'',1,'Art/Interface/Buttons/Promotions/Crazed.dds',ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)
			return 80
		if sGoody == 'DEMONIC_POSSESSION':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_ENRAGED'), True)
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_CRAZED'), True)
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_DEMON'), True)
			CyInterface().addMessage(caster.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_POSSESSED", ()),'',1,'Art/Interface/Buttons/Units/UCDemon.dds',ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)
			return 80
		if sGoody == 'DISEASED':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_DISEASED'), True)
			CyInterface().addMessage(caster.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_DISEASED", ()),'',1,'Art/Interface/Buttons/Promotions/Diseased.dds',ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)
			return 80
		if sGoody == 'ENRAGED':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_ENRAGED'), True)
			CyInterface().addMessage(caster.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_ENRAGED", ()),'',1,'Art/Interface/Buttons/Promotions/Enraged.dds',ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)
			return 80
		if sGoody == 'PLAGUED':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_PLAGUED'), True)
			CyInterface().addMessage(caster.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_PLAGUED", ()),'',1,'Art/Interface/Buttons/Promotions/Plagued.dds',ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)
			return 80
		if sGoody == 'POISONED':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_POISONED'), True)
			caster.doDamageNoCaster(25, 90, gc.getInfoTypeForString('DAMAGE_POISON'), False)
			CyInterface().addMessage(caster.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_POISONED", ()),'',1,'Art/Interface/Buttons/Promotions/Poisoned.dds',ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)
			return 80
		if sGoody == 'WITHERED':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_WITHERED'), True)
			CyInterface().addMessage(caster.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_WITHERED", ()),'',1,'Art/Interface/Buttons/Promotions/Withered.dds',ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)
			return 80
		if sGoody == 'RUSTED':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_RUSTED'), True)
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_BRONZE_WEAPONS'), False)
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_IRON_WEAPONS'), False)
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_MITHRIL_WEAPONS'), False)
			CyInterface().addMessage(caster.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_RUSTED", ()),'',1,'Art/Interface/Buttons/Promotions/Rusted.dds',ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)
			return 80
		if sGoody == 'SPAWN_DROWN':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_SPAWN_DROWN'), caster)
			return 50
		if sGoody == 'SPAWN_SCORPION_BAD':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_SPAWN_SCORPION_BAD'), caster)
			return 50
		if sGoody == 'SPAWN_SEA_SERPENT':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_SPAWN_SEA_SERPENT'), caster)
			return 50
		if sGoody == 'SPAWN_SPECTRE':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_GRAVE_SPECTRE'), caster)
			return 50
		if sGoody == 'SPAWN_SPIDER':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_SPAWN_SPIDER'), caster)
			return 50
		return 100

	def exploreLairNeutral(self, caster):
		iPlayer = caster.getOwner()
		pPlot = caster.plot()
		pPlayer = gc.getPlayer(caster.getOwner())
		lList = ['NOTHING']
		if not pPlot.isWater():
			lList = lList + ['SPAWN_SKELETON', 'SPAWN_LIZARDMAN', 'SPAWN_SPIDER', 'PORTAL', 'DEPTHS', 'DWARF_VS_LIZARDMEN', 'CAGE']
			if pPlot.getTerrainType() == gc.getInfoTypeForString('TERRAIN_SNOW'):
				lList = lList + ['SPAWN_FROSTLING']
			if pPlot.getImprovementType() == gc.getInfoTypeForString('IMPROVEMENT_BARROW'):
				lList = lList + ['SPAWN_SKELETON', 'SPAWN_SKELETON']
			if pPlot.getImprovementType() == gc.getInfoTypeForString('IMPROVEMENT_RUINS'):
				lList = lList + ['SPAWN_LIZARDMAN', 'SPAWN_LIZARDMAN']
			if pPlot.getImprovementType() == gc.getInfoTypeForString('IMPROVEMENT_GOBLIN_FORT'):
				lList = lList + ['SPAWN_SCORPION', 'SPAWN_SCORPION', 'SPAWN_SCORPION']
		if pPlot.isWater():
			lList = lList + ['SPAWN_DROWN']
		if caster.isAlive():
			if not caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_MUTATED')):
				lList = lList + ['MUTATED']

		sGoody = lList[CyGame().getSorenRandNum(len(lList), "Pick Goody")-1]
		if sGoody == 'CAGE':
			pPlot.setImprovementType(gc.getInfoTypeForString('IMPROVEMENT_CAGE'))
			for i in range(pPlot.getNumUnits(), -1, -1):
				pUnit = pPlot.getUnit(i)
				pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_HELD'), True)
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_CAGE",()),'',1,'Art/Interface/Buttons/Improvements/Cage.dds',ColorTypes(7),caster.getX(),caster.getY(),True,True)
			return 0
		if sGoody == 'DEPTHS':
			iUnitID = self.getUnitPlayerID(caster)
			if iUnitID != -1:
				iEvent = CvUtil.findInfoTypeNum(gc.getEventTriggerInfo, gc.getNumEventTriggerInfos(), 'EVENTTRIGGER_EXPLORE_LAIR_DEPTHS')
				triggerData = pPlayer.initTriggeredData(iEvent, True, -1, caster.getX(), caster.getY(), caster.getOwner(), -1, -1, -1, iUnitID, -1)
			return 100
		if sGoody == 'DWARF_VS_LIZARDMEN':
			iUnitID = self.getUnitPlayerID(caster)
			if iUnitID != -1:
				iEvent = CvUtil.findInfoTypeNum(gc.getEventTriggerInfo, gc.getNumEventTriggerInfos(), 'EVENTTRIGGER_EXPLORE_LAIR_DWARF_VS_LIZARDMEN')
				triggerData = pPlayer.initTriggeredData(iEvent, True, -1, caster.getX(), caster.getY(), caster.getOwner(), -1, -1, -1, iUnitID, -1)
			return 100
		if sGoody == 'MUTATED':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_MUTATED'), True)
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_MUTATED",()),'',1,'Art/Interface/Buttons/Promotions/Mutated.dds',ColorTypes(7),caster.getX(),caster.getY(),True,True)
			return 50
		if sGoody == 'NOTHING':
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_NOTHING",()),'',1,'Art/Interface/Buttons/Spells/Explore Lair.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			return 100
		if sGoody == 'PORTAL':
			iUnitID = self.getUnitPlayerID(caster)
			if iUnitID != -1:
				iEvent = CvUtil.findInfoTypeNum(gc.getEventTriggerInfo, gc.getNumEventTriggerInfos(), 'EVENTTRIGGER_EXPLORE_LAIR_PORTAL')
				triggerData = pPlayer.initTriggeredData(iEvent, True, -1, caster.getX(), caster.getY(), caster.getOwner(), -1, -1, -1, iUnitID, -1)
			return 0
		if sGoody == 'SPAWN_DROWN':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_SPAWN_DROWN'), caster)
			return 50
		if sGoody == 'SPAWN_FROSTLING':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_SPAWN_FROSTLING'), caster)
			return 50
		if sGoody == 'SPAWN_LIZARDMAN':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_SPAWN_LIZARDMAN'), caster)
			return 50
		if sGoody == 'SPAWN_SCORPION':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_SPAWN_SCORPION'), caster)
			return 50
		if sGoody == 'SPAWN_SKELETON':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_SPAWN_SKELETON'), caster)
			return 50
		if sGoody == 'SPAWN_SPIDER':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_SPAWN_SPIDER'), caster)
			return 50
		return 100

	def exploreLairGood(self, caster):
		iPlayer = caster.getOwner()
		pPlot = caster.plot()
		pPlayer = gc.getPlayer(caster.getOwner())
		lList = ['HIGH_GOLD', 'TREASURE', 'EXPERIENCE']
		if caster.isAlive():
			if not caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_SPIRIT_GUIDE')):
				lList = lList + ['SPIRIT_GUIDE']
		if not pPlot.isWater():
			lList = lList + ['ITEM_HEALING_SALVE', 'SUPPLIES']
			if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_MYSTICISM')):
				lList = lList + ['PRISONER_DISCIPLE_ASHEN', 'PRISONER_DISCIPLE_EMPYREAN', 'PRISONER_DISCIPLE_LEAVES', 'PRISONER_DISCIPLE_OVERLORDS', 'PRISONER_DISCIPLE_RUNES', 'PRISONER_DISCIPLE_ORDER']
		if caster.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_MELEE'):
			if not caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_ENCHANTED_BLADE')):
				lList = lList + ['ENCHANTED_BLADE']
		if caster.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_ADEPT'):
			if not caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_SPELLSTAFF')):
				lList = lList + ['SPELLSTAFF']
		if caster.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_RECON'):
			if not caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_POISONED_BLADE')):
				lList = lList + ['POISONED_BLADE']
		if caster.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_ARCHER'):
			if not caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_FLAMING_ARROWS')):
				lList = lList + ['FLAMING_ARROWS']
		if caster.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_DISCIPLE'):
			if not caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_SHIELD_OF_FAITH')):
				lList = lList + ['SHIELD_OF_FAITH']
		if gc.getUnitInfo(caster.getUnitType()).getWeaponTier() >= 1:
			if not caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_MITHRIL_WEAPONS')):
				if (gc.getUnitInfo(caster.getUnitType()).getWeaponTier() >= 3 and pPlayer.isHasTech(gc.getInfoTypeForString('TECH_IRON_WORKING'))):
					lList = lList + ['MITHRIL_WEAPONS']
				if not caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_IRON_WEAPONS')):
					if (gc.getUnitInfo(caster.getUnitType()).getWeaponTier() >= 2 and pPlayer.isHasTech(gc.getInfoTypeForString('TECH_BRONZE_WORKING'))):
						lList = lList + ['IRON_WEAPONS']
					if not caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_BRONZE_WEAPONS')):
						lList = lList + ['BRONZE_WEAPONS']

		sGoody = lList[CyGame().getSorenRandNum(len(lList), "Pick Goody")-1]
		if sGoody == 'HIGH_GOLD':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_HIGH_GOLD'), caster)
			return 90
		if sGoody == 'SUPPLIES':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_SUPPLIES'), caster)
			return 100
		if sGoody == 'TREASURE':
			self.placeTreasure(iPlayer, gc.getInfoTypeForString('EQUIPMENT_TREASURE'))
			return 80
		if sGoody == 'EXPERIENCE':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_EXPERIENCE'), caster)
			return 100
		if sGoody == 'SPIRIT_GUIDE':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_SPIRIT_GUIDE'), True)
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_SPIRIT_GUIDE",()),'AS2D_POSITIVE_DINK',1,'Art/Interface/Buttons/Promotions/SpiritGuide.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			return 80
		if sGoody == 'ITEM_HEALING_SALVE':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_ITEM_HEALING_SALVE'), caster)
			return 100
		if sGoody == 'ITEM_POTION_OF_INVISIBILITY':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_ITEM_POTION_OF_INVISIBILITY'), caster)
			return 100
		if sGoody == 'ITEM_POTION_OF_RESTORATION':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_ITEM_POTION_OF_RESTORATION'), caster)
			return 100
		if sGoody == 'ENCHANTED_BLADE':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_ENCHANTED_BLADE'), True)
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_ENCHANTED_BLADE",()),'',1,'Art/Interface/Buttons/Promotions/EnchantedBlade.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			return 100
		if sGoody == 'SPELLSTAFF':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_SPELLSTAFF'), True)
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_SPELLSTAFF",()),'',1,'Art/Interface/Buttons/Promotions/Spellstaff.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			return 100
		if sGoody == 'POISONED_BLADE':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_POISONED_BLADE'), True)
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_POISONED_BLADE",()),'',1,'Art/Interface/Buttons/Promotions/PoisonedBlade.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			return 100
		if sGoody == 'FLAMING_ARROWS':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_FLAMING_ARROWS'), True)
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_FLAMING_ARROWS",()),'AS2D_POSITIVE_DINK',1,'Art/Interface/Buttons/Promotions/FlamingArrows.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			return 100
		if sGoody == 'PRISONER_DISCIPLE_ASHEN':
			pPlayer.receiveGoody(pPlot,gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_DISCIPLE_ASHEN'), caster)
			return 100
		if sGoody == 'PRISONER_DISCIPLE_EMPYREAN':
			pPlayer.receiveGoody(pPlot,gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_DISCIPLE_EMPYREAN'), caster)
			return 100
		if sGoody == 'PRISONER_DISCIPLE_LEAVES':
			pPlayer.receiveGoody(pPlot,gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_DISCIPLE_LEAVES'), caster)
			return 100
		if sGoody == 'PRISONER_DISCIPLE_OVERLORDS':
			pPlayer.receiveGoody(pPlot,gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_DISCIPLE_OVERLORDS'), caster)
			return 100
		if sGoody == 'PRISONER_DISCIPLE_RUNES':
			pPlayer.receiveGoody(pPlot,gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_DISCIPLE_RUNES'), caster)
			return 100
		if sGoody == 'PRISONER_DISCIPLE_ORDER':
			pPlayer.receiveGoody(pPlot,gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_DISCIPLE_ORDER'), caster)
			return 100
		if sGoody == 'SHIELD_OF_FAITH':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_SHIELD_OF_FAITH'), True)
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_SHIELD_OF_FAITH",()),'',1,'Art/Interface/Buttons/Promotions/ShieldOfFaith.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			return 100
		if sGoody == 'BRONZE_WEAPONS':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_BRONZE_WEAPONS'), True)
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_BRONZE_WEAPONS",()),'',1,'Art/Interface/Buttons/Promotions/BronzeWeapons.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			if caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_RUSTED')) == True:
				caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_RUSTED'), False)
			return 100
		if sGoody == 'IRON_WEAPONS':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_IRON_WEAPONS'), True)
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_BRONZE_WEAPONS'), False)
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_IRON_WEAPONS",()),'',1,'Art/Interface/Buttons/Promotions/IronWeapons.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			if caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_RUSTED')) == True:
				caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_RUSTED'), False)
			return 100
		if sGoody == 'MITHRIL_WEAPONS':
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_MITHRIL_WEAPONS'), True)
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_IRON_WEAPONS'), False)
			caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_BRONZE_WEAPONS'), False)
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_MITHRIL_WEAPONS",()),'',1,'Art/Interface/Buttons/Promotions/MithrilWeapons.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			if caster.isHasPromotion(gc.getInfoTypeForString('PROMOTION_RUSTED')) == True:
				caster.setHasPromotion(gc.getInfoTypeForString('PROMOTION_RUSTED'), False)
			return 100
		return 100

	def exploreLairBigGood(self, caster):
		iPlayer = caster.getOwner()
		pPlot = caster.plot()
		pPlayer = gc.getPlayer(caster.getOwner())

		lList = ['TREASURE_VAULT', 'GOLDEN_AGE']
		if pPlayer.canReceiveGoody(pPlot, gc.getInfoTypeForString('GOODY_GRAVE_TECH'), caster):
			lList = lList + ['TECH']
		if not pPlot.isWater():
			lList = lList + ['ITEM_JADE_TORC', 'ITEM_ROD_OF_WINDS', 'ITEM_TIMOR_MASK', 'PRISONER_ADVENTURER', 'PRISONER_ARTIST', 'PRISONER_COMMANDER', 'PRISONER_ENGINEER', 'PRISONER_MERCHANT', 'PRISONER_PROPHET', 'PRISONER_SCIENTIST']
			if pPlot.getBonusType(-1) == -1:
				lList = lList + ['BONUS_MANA']
				if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_MINING')):
					lList = lList + ['BONUS_COPPER', 'BONUS_GEMS', 'BONUS_GOLD']
				if pPlayer.isHasTech(gc.getInfoTypeForString('TECH_SMELTING')):
					lList = lList + ['BONUS_IRON']
		if pPlot.isWater():
			lList = lList + ['PRISONER_SEA_SERPENT']
			if pPlot.getBonusType(-1) == -1:
				lList = lList + ['BONUS_CLAM', 'BONUS_CRAB', 'BONUS_FISH']
		if self.grace() == False:
			lList = lList + ['PRISONER_ANGEL', 'PRISONER_MONK', 'PRISONER_ASSASSIN', 'PRISONER_CHAMPION', 'PRISONER_MAGE']
		sGoody = lList[CyGame().getSorenRandNum(len(lList), "Pick Goody")-1]

		if sGoody == 'TREASURE_VAULT':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_TREASURE_VAULT'), caster)
			return 100
		if sGoody == 'BONUS_CLAM':
			pPlot.setBonusType(gc.getInfoTypeForString('BONUS_CLAM'))
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_BONUS_CLAM",()),'',1,'Art/Interface/Buttons/WorldBuilder/Clam.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			return 100
		if sGoody == 'BONUS_COPPER':
			pPlot.setBonusType(gc.getInfoTypeForString('BONUS_COPPER'))
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_BONUS_COPPER",()),'',1,'Art/Interface/Buttons/WorldBuilder/Copper.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			return 100
		if sGoody == 'BONUS_CRAB':
			pPlot.setBonusType(gc.getInfoTypeForString('BONUS_CRAB'))
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_BONUS_CRAB",()),'',1,'Art/Interface/Buttons/WorldBuilder/Crab.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			return 100
		if sGoody == 'BONUS_FISH':
			pPlot.setBonusType(gc.getInfoTypeForString('BONUS_FISH'))
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_BONUS_FISH",()),'',1,'Art/Interface/Buttons/WorldBuilder/Fish.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			return 100
		if sGoody == 'BONUS_GOLD':
			pPlot.setBonusType(gc.getInfoTypeForString('BONUS_GOLD'))
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_BONUS_GOLD",()),'',1,'Art/Interface/Buttons/WorldBuilder/Gold.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			return 100
		if sGoody == 'BONUS_GEMS':
			pPlot.setBonusType(gc.getInfoTypeForString('BONUS_GEMS'))
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_BONUS_GEMS",()),'',1,'Art/Interface/Buttons/WorldBuilder/Gems.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			return 100
		if sGoody == 'BONUS_IRON':
			pPlot.setBonusType(gc.getInfoTypeForString('BONUS_IRON'))
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_BONUS_IRON",()),'',1,'Art/Interface/Buttons/WorldBuilder/Iron.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			return 100
		if sGoody == 'BONUS_MANA':
			pPlot.setBonusType(gc.getInfoTypeForString('BONUS_MANA'))
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_BONUS_MANA",()),'',1,'Art/Interface/Buttons/WorldBuilder/mana_button.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			return 100
		if sGoody == 'GOLDEN_AGE':
			pPlayer.changeGoldenAgeTurns(CyGame().goldenAgeLength())
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_GOLDEN_AGE",()),'',1,'Art/Interface/Buttons/Spells/Explore Lair.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)
			return 100
		if sGoody == 'ITEM_JADE_TORC':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_ITEM_JADE_TORC'), caster)
			return 100
		if sGoody == 'ITEM_ROD_OF_WINDS':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_ITEM_ROD_OF_WINDS'), caster)
			return 100
		if sGoody == 'ITEM_TIMOR_MASK':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_ITEM_TIMOR_MASK'), caster)
			return 100
		if sGoody == 'PRISONER_ADVENTURER':
			pPlayer.receiveGoody(pPlot,gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_ADVENTURER'), caster)
			return 100
		if sGoody == 'PRISONER_ANGEL':
			pPlayer.receiveGoody(pPlot,gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_ANGEL'), caster)
			return 100
		if sGoody == 'PRISONER_ARTIST':
			pPlayer.receiveGoody(pPlot,gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_ARTIST'), caster)
			return 100
		if sGoody == 'PRISONER_ASSASSIN':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_ASSASSIN'), caster)
			return 100
		if sGoody == 'PRISONER_CHAMPION':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_CHAMPION'), caster)
			return 100
		if sGoody == 'PRISONER_COMMANDER':
			pPlayer.receiveGoody(pPlot,gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_COMMANDER'), caster)
			return 100
		if sGoody == 'PRISONER_ENGINEER':
			pPlayer.receiveGoody(pPlot,gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_ENGINEER'), caster)
			return 100
		if sGoody == 'PRISONER_MAGE':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_MAGE'), caster)
			return 100
		if sGoody == 'PRISONER_MERCHANT':
			pPlayer.receiveGoody(pPlot,gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_MERCHANT'), caster)
			return 100
		if sGoody == 'PRISONER_MONK':
			pPlayer.receiveGoody(pPlot,gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_MONK'), caster)
			return 100
		if sGoody == 'PRISONER_PROPHET':
			pPlayer.receiveGoody(pPlot,gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_PROPHET'), caster)
			return 100
		if sGoody == 'PRISONER_SEA_SERPENT':
			pPlayer.receiveGoody(pPlot,gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_SEA_SERPENT'), caster)
			return 100
		if sGoody == 'PRISONER_SCIENTIST':
			pPlayer.receiveGoody(pPlot,gc.getInfoTypeForString('GOODY_EXPLORE_LAIR_PRISONER_SCIENTIST'), caster)
			return 100
		if sGoody == 'TECH':
			pPlayer.receiveGoody(pPlot, gc.getInfoTypeForString('GOODY_GRAVE_TECH'), caster)
			return 100
		return 100

	def formEmpire(self, iCiv, iLeader, iTeam, pCity, iAlignment, pFromPlayer):
		iPlayer = pFromPlayer.initNewEmpire(iLeader, iCiv)
		if iPlayer != PlayerTypes.NO_PLAYER:
			pPlot = pCity.plot()
			for i in range(pPlot.getNumUnits(), -1, -1):
				pUnit = pPlot.getUnit(i)
				pUnit.jumpToNearestValidPlot()
			pPlayer = gc.getPlayer(iPlayer)
			if iTeam != TeamTypes.NO_TEAM:
				if iTeam < pPlayer.getTeam():
					gc.getTeam(iTeam).addTeam(pPlayer.getTeam())
				else:
					gc.getTeam(pPlayer.getTeam()).addTeam(iTeam)
			pPlayer.acquireCity(pCity, False, True)
			pCity = pPlot.getPlotCity()
			pPlayer.initUnit(gc.getInfoTypeForString('UNIT_ARCHER'), pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_CITY_DEFENSE, DirectionTypes.DIRECTION_SOUTH)
			pPlayer.initUnit(gc.getInfoTypeForString('UNIT_ARCHER'), pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_CITY_DEFENSE, DirectionTypes.DIRECTION_SOUTH)
			pPlayer.initUnit(gc.getInfoTypeForString('UNIT_ARCHER'), pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_CITY_DEFENSE, DirectionTypes.DIRECTION_SOUTH)
			pPlayer.initUnit(gc.getInfoTypeForString('UNIT_ARCHER'), pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_CITY_DEFENSE, DirectionTypes.DIRECTION_SOUTH)
			pPlayer.initUnit(gc.getInfoTypeForString('UNIT_WORKER'), pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
			if iAlignment != -1:
				pPlayer.setAlignment(iAlignment)
		return pPlayer

	def grace(self):
		iGrace = 20 * (int(CyGame().getGameSpeedType()) + 1)
		iDiff = gc.getNumHandicapInfos() + 1 - int(gc.getGame().getHandicapType())
		iGrace = iGrace * iDiff
		iGrace = CyGame().getSorenRandNum(iGrace, "grace") + iGrace
		if iGrace > CyGame().getGameTurn():
			return True
		return False

	def doCityFire(self, pCity):
		iCount = 0

		for iBuilding in range(gc.getNumBuildingInfos()):
			kBuilding = gc.getBuildingInfo(iBuilding)
			# Evaluate getNumRealBuilding first, no need to check conditions for buildings that are not present.
			if pCity.getNumRealBuilding(iBuilding) > 0 and iBuilding not in self.siIgnoreFire and \
					not kBuilding.isRequiresCaster() and \
					kBuilding.getBuildingClassType() != gc.getInfoTypeForString('BUILDINGCLASS_PALACE') and \
					kBuilding.getConquestProbability() != 100:
##--------		Unofficial Bug Fix: Modified by Denev	--------##
#				if CyGame().getSorenRandNum(100, "City Fire") <= 10:
				if CyGame().getSorenRandNum(100, "City Fire") < 10:
##--------		Unofficial Bug Fix: End Modify			--------##
					pCity.setNumRealBuilding(iBuilding, 0)
					CyInterface().addMessage(pCity.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_CITY_FIRE",(kBuilding.getDescription(), )),'',1,kBuilding.getButton(),ColorTypes(8),pCity.getX(),pCity.getY(),True,True)
					iCount += 1

		if iCount == 0:
			CyInterface().addMessage(pCity.getOwner(),True,25,CyTranslator().getText("TXT_KEY_MESSAGE_CITY_FIRE_NO_DAMAGE",()),'AS2D_SPELL_FIRE_ELEMENTAL',1,'Art/Interface/Buttons/Fire.dds',ColorTypes(8),pCity.getX(),pCity.getY(),True,True)


	def doHellTerrain(self):
		iAshenVeil = gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL')
		iBurningSands = gc.getInfoTypeForString('TERRAIN_BURNING_SANDS')
		iBanana = gc.getInfoTypeForString('BONUS_BANANA')
		iCotton = gc.getInfoTypeForString('BONUS_COTTON')
		iCorn = gc.getInfoTypeForString('BONUS_CORN')
		iCow = gc.getInfoTypeForString('BONUS_COW')
		iEvil = gc.getInfoTypeForString('ALIGNMENT_EVIL')
		iFarm = gc.getInfoTypeForString('IMPROVEMENT_FARM')
		iFlames = gc.getInfoTypeForString('FEATURE_FLAMES')
		iFlamesSpreadChance = gc.getDefineINT('FLAMES_SPREAD_CHANCE')
		iGulagarm = gc.getInfoTypeForString('BONUS_GULAGARM')
		iHorse = gc.getInfoTypeForString('BONUS_HORSE')
		iInfernal = gc.getInfoTypeForString('CIVILIZATION_INFERNAL')
		iMarble = gc.getInfoTypeForString('BONUS_MARBLE')
		iNeutral = gc.getInfoTypeForString('ALIGNMENT_NEUTRAL')
		iNightmare = gc.getInfoTypeForString('BONUS_NIGHTMARE')
		iPig = gc.getInfoTypeForString('BONUS_PIG')
		iRazorweed = gc.getInfoTypeForString('BONUS_RAZORWEED')
		iRice = gc.getInfoTypeForString('BONUS_RICE')
		iSheep = gc.getInfoTypeForString('BONUS_SHEEP')
		iSheutStone = gc.getInfoTypeForString('BONUS_SHEUT_STONE')
		iSilk = gc.getInfoTypeForString('BONUS_SILK')
		iSnakePillar = gc.getInfoTypeForString('IMPROVEMENT_SNAKE_PILLAR')
		iSugar = gc.getInfoTypeForString('BONUS_SUGAR')
		iToad = gc.getInfoTypeForString('BONUS_TOAD')
		iWheat = gc.getInfoTypeForString('BONUS_WHEAT')
		iForest = gc.getInfoTypeForString('FEATURE_FOREST')
		iJungle = gc.getInfoTypeForString('FEATURE_JUNGLE')
		iAForest = gc.getInfoTypeForString('FEATURE_FOREST_ANCIENT')
		iNForest = gc.getInfoTypeForString('FEATURE_FOREST_NEW')
		iBForest = gc.getInfoTypeForString('FEATURE_FOREST_BURNT')
		iCount = CyGame().getGlobalCounter()
		for i in range (CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			iFeature = pPlot.getFeatureType()
			iTerrain = pPlot.getTerrainType()
			iBonus = pPlot.getBonusType(-1)
			iImprovement = pPlot.getImprovementType()
			bUntouched = True
			if pPlot.isOwned():
				pPlayer = gc.getPlayer(pPlot.getOwner())
				iAlignment = pPlayer.getAlignment()
				if pPlayer.getCivilizationType() == iInfernal:
					pPlot.changePlotCounter(100)
					bUntouched = False
				if (bUntouched and pPlayer.getStateReligion() == iAshenVeil or (iCount >= 50 and iAlignment == iEvil) or (iCount >= 75 and iAlignment == iNeutral)):
					iX = pPlot.getX()
					iY = pPlot.getY()
					for iiX in range(iX-1, iX+2, 1):
						for iiY in range(iY-1, iY+2, 1):
							pAdjacentPlot = CyMap().plot(iiX,iiY)
							if pAdjacentPlot.isNone() == False:
								if pAdjacentPlot.getPlotCounter() > 10:
									pPlot.changePlotCounter(1)
									bUntouched = False
			if (bUntouched and pPlot.isOwned() == False and iCount > 25):
				iX = pPlot.getX()
				iY = pPlot.getY()
				for iiX in range(iX-1, iX+2, 1):
					for iiY in range(iY-1, iY+2, 1):
						pAdjacentPlot = CyMap().plot(iiX,iiY)
						if pAdjacentPlot.isNone() == False:
							if pAdjacentPlot.getPlotCounter() > 10:
								pPlot.changePlotCounter(1)
								bUntouched = False
			iPlotCount = pPlot.getPlotCounter()
			if (bUntouched and iPlotCount > 0):
				pPlot.changePlotCounter(-1)
			if iPlotCount > 9:
				if (iBonus == iSheep or iBonus == iPig):
					pPlot.setBonusType(iToad)
				if (iBonus == iHorse or iBonus == iCow):
					pPlot.setBonusType(iNightmare)
				if (iBonus == iCotton or iBonus == iSilk):
					pPlot.setBonusType(iRazorweed)
				if (iBonus == iBanana or iBonus == iSugar):
					pPlot.setBonusType(iGulagarm)
				if (iBonus == iMarble):
					pPlot.setBonusType(iSheutStone)
				if (iBonus == iCorn or iBonus == iRice or iBonus == iWheat):
					pPlot.setBonusType(-1)
					pPlot.setImprovementType(iSnakePillar)

				if (iFeature == iForest or iFeature == iAForest or iFeature == iNForest or iFeature == iJungle):
					iRandom = CyGame().getSorenRandNum(100, "Hell Terrain Burnt Forest")
					if iRandom < 10:
						pPlot.setFeatureType(iBForest, 0)
				if pPlot.isPeak() == True:
					iRandom = CyGame().getSorenRandNum(1000, "Hell Terrain Volcanos")
					if iRandom < 2:
						iEvent = CvUtil.findInfoTypeNum(gc.getEventTriggerInfo, gc.getNumEventTriggerInfos(), 'EVENTTRIGGER_VOLCANO_CREATION')
						if pPlot.isOwned():
							triggerData = pPlayer.initTriggeredData(iEvent, True, -1, pPlot.getX(), pPlot.getY(), -1, -1, -1, -1, -1, -1)

			if iPlotCount < 10:
				if iBonus == iToad:
					if CyGame().getSorenRandNum(100, "Hell Convert") < 50:
						pPlot.setBonusType(iSheep)
					else:
						pPlot.setBonusType(iPig)
				if iBonus == iNightmare:
					if CyGame().getSorenRandNum(100, "Hell Convert") < 50:
						pPlot.setBonusType(iHorse)
					else:
						pPlot.setBonusType(iCow)
				if iBonus == iRazorweed:
					if CyGame().getSorenRandNum(100, "Hell Convert") < 50:
						pPlot.setBonusType(iCotton)
					else:
						pPlot.setBonusType(iSilk)
				if iBonus == iGulagarm:
					if CyGame().getSorenRandNum(100, "Hell Convert") < 50:
						pPlot.setBonusType(iBanana)
					else:
						pPlot.setBonusType(iSugar)
				if (iBonus == iSheutStone):
					pPlot.setBonusType(iMarble)
				if iImprovement == iSnakePillar:
					pPlot.setImprovementType(iFarm)
					iCount = CyGame().getSorenRandNum(100, "Hell Convert")
					if  iCount < 33:
						pPlot.setBonusType(iCorn)
					else:
						if iCount < 66:
							pPlot.setBonusType(iRice)
						else:
							pPlot.setBonusType(iWheat)
			if iTerrain == iBurningSands:
				if pPlot.isCity() == False:
					if pPlot.isPeak() == False:
						if CyGame().getSorenRandNum(100, "Flames") < iFlamesSpreadChance:
							pPlot.setFeatureType(iFlames, 0)

	def doTurnKhazad(self, iPlayer):
		pPlayer = gc.getPlayer(iPlayer)
		if pPlayer.getNumCities() > 0:
			iVault1 = gc.getInfoTypeForString('BUILDING_DWARVEN_VAULT_EMPTY')
			iVault2 = gc.getInfoTypeForString('BUILDING_DWARVEN_VAULT_LOW')
			iVault3 = gc.getInfoTypeForString('BUILDING_DWARVEN_VAULT')
			iVault4 = gc.getInfoTypeForString('BUILDING_DWARVEN_VAULT_STOCKED')
			iVault5 = gc.getInfoTypeForString('BUILDING_DWARVEN_VAULT_ABUNDANT')
			iVault6 = gc.getInfoTypeForString('BUILDING_DWARVEN_VAULT_FULL')
			iVault7 = gc.getInfoTypeForString('BUILDING_DWARVEN_VAULT_OVERFLOWING')
			iGold = pPlayer.getGold() / pPlayer.getNumCities()
			if iGold <= 49:
				iNewVault = iVault1
			if (iGold >= 50 and iGold <= 99):
				iNewVault = iVault2
			if (iGold >= 100 and iGold <= 149):
				iNewVault = iVault3
			if (iGold >= 150 and iGold <= 199):
				iNewVault = iVault4
			if (iGold >= 200 and iGold <= 299):
				iNewVault = iVault5
			if (iGold >= 300 and iGold <= 499):
				iNewVault = iVault6
			if iGold >= 500:
				iNewVault = iVault7
			for pyCity in PyPlayer(iPlayer).getCityList():
				pCity = pyCity.GetCy()
				pCity.setNumRealBuilding(iVault1, 0)
				pCity.setNumRealBuilding(iVault2, 0)
				pCity.setNumRealBuilding(iVault3, 0)
				pCity.setNumRealBuilding(iVault4, 0)
				pCity.setNumRealBuilding(iVault5, 0)
				pCity.setNumRealBuilding(iVault6, 0)
				pCity.setNumRealBuilding(iVault7, 0)
				pCity.setNumRealBuilding(iNewVault, 1)

	def doTurnLuchuirp(self, iPlayer):
		pPlayer = gc.getPlayer(iPlayer)
		if pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_BARNAXUS')) > 0:
			py = PyPlayer(iPlayer)
			pBarnaxus = -1
			bEmp1 = False
			bEmp2 = False
			bEmp3 = False
			bEmp4 = False
			bEmp5 = False
			iBarnaxus = gc.getInfoTypeForString('UNITCLASS_BARNAXUS')
			iCombat1 = gc.getInfoTypeForString('PROMOTION_COMBAT1')
			iCombat2 = gc.getInfoTypeForString('PROMOTION_COMBAT2')
			iCombat3 = gc.getInfoTypeForString('PROMOTION_COMBAT3')
			iCombat4 = gc.getInfoTypeForString('PROMOTION_COMBAT4')
			iCombat5 = gc.getInfoTypeForString('PROMOTION_COMBAT5')
			iEmpower1 = gc.getInfoTypeForString('PROMOTION_EMPOWER1')
			iEmpower2 = gc.getInfoTypeForString('PROMOTION_EMPOWER2')
			iEmpower3 = gc.getInfoTypeForString('PROMOTION_EMPOWER3')
			iEmpower4 = gc.getInfoTypeForString('PROMOTION_EMPOWER4')
			iEmpower5 = gc.getInfoTypeForString('PROMOTION_EMPOWER5')
			iGolem = gc.getInfoTypeForString('PROMOTION_GOLEM')

			lGolems = []
			for pUnit in py.getUnitList():
				if pUnit.getUnitClassType() == iBarnaxus :
					pBarnaxus = pUnit
				elif pUnit.isHasPromotion(iGolem) :
					lGolems.append(pUnit)
			if pBarnaxus != -1 :
				bEmp1 = bool(pBarnaxus.isHasPromotion(iCombat1))
				bEmp2 = bool(pBarnaxus.isHasPromotion(iCombat2))
				bEmp3 = bool(pBarnaxus.isHasPromotion(iCombat3))
				bEmp4 = bool(pBarnaxus.isHasPromotion(iCombat4))
				bEmp5 = bool(pBarnaxus.isHasPromotion(iCombat5))
			for pUnit in lGolems :
				pUnit.setHasPromotion(iEmpower1, False)
				pUnit.setHasPromotion(iEmpower2, False)
				pUnit.setHasPromotion(iEmpower3, False)
				pUnit.setHasPromotion(iEmpower4, False)
				pUnit.setHasPromotion(iEmpower5, False)
				if bEmp1:
					pUnit.setHasPromotion(iEmpower1, True)
				if bEmp2:
					pUnit.setHasPromotion(iEmpower2, True)
				if bEmp3:
					pUnit.setHasPromotion(iEmpower3, True)
				if bEmp4:
					pUnit.setHasPromotion(iEmpower4, True)
				if bEmp5:
					pUnit.setHasPromotion(iEmpower5, True)
		elif pPlayer.getUnitClassCount(gc.getInfoTypeForString('EQUIPMENTCLASS_PIECES_OF_BARNAXUS')) == 1:
			if pPlayer.getNumUnits()==1:
				py = PyPlayer(iPlayer)
				for pUnit in py.getUnitList():
					pUnit.kill(true)

	def findClearPlot(self, pUnit, plot):
		BestPlot = -1
		iBestPlot = 0
		if pUnit == -1:
			iX = plot.getX()
			iY = plot.getY()
			for iiX in range(iX-1, iX+2, 1):
				for iiY in range(iY-1, iY+2, 1):
					iCurrentPlot = 0
					pPlot = CyMap().plot(iiX,iiY)
					if pPlot.isNone() == False:
						if pPlot.getNumUnits() == 0:
							if (pPlot.isWater() == plot.isWater() and pPlot.isPeak() == False and pPlot.isCity() == False):
								iCurrentPlot = iCurrentPlot + 5
						if iCurrentPlot >= 1:
							iCurrentPlot = iCurrentPlot + CyGame().getSorenRandNum(5, "FindClearPlot")
							if iCurrentPlot >= iBestPlot:
								BestPlot = pPlot
								iBestPlot = iCurrentPlot
			return BestPlot
		iX = pUnit.getX()
		iY = pUnit.getY()
		for iiX in range(iX-1, iX+2, 1):
			for iiY in range(iY-1, iY+2, 1):
				iCurrentPlot = 0
				pPlot = CyMap().plot(iiX,iiY)
				if pPlot.isNone() == False:
					if pPlot.getNumUnits() == 0:
						if pUnit.canMoveOrAttackInto(pPlot, False):
							iCurrentPlot = iCurrentPlot + 5
					for i in range(pPlot.getNumUnits()):
						if pPlot.getUnit(i).getOwner() == pUnit.getOwner():
							if pUnit.canMoveOrAttackInto(pPlot, False):
								iCurrentPlot = iCurrentPlot + 15
					if pPlot.isCity():
						if pPlot.getPlotCity().getOwner() == pUnit.getOwner():
							iCurrentPlot = iCurrentPlot + 50
					if (iX == iiX and iY == iiY):
						iCurrentPlot = 0
					if iCurrentPlot >= 1:
						iCurrentPlot = iCurrentPlot + CyGame().getSorenRandNum(5, "FindClearPlot")
						if iCurrentPlot >= iBestPlot:
							BestPlot = pPlot
							iBestPlot = iCurrentPlot
		return BestPlot

	def genesis(self, iPlayer):
		iBrokenLands = gc.getInfoTypeForString('TERRAIN_BROKEN_LANDS')
		iFields = gc.getInfoTypeForString('TERRAIN_FIELDS_OF_PERDITION')
		iBurningSands = gc.getInfoTypeForString('TERRAIN_BURNING_SANDS')
		iShallows = gc.getInfoTypeForString('TERRAIN_SHALLOWS')
		iSnow = gc.getInfoTypeForString('TERRAIN_SNOW')
		iTundra = gc.getInfoTypeForString('TERRAIN_TUNDRA')
		iPlains = gc.getInfoTypeForString('TERRAIN_PLAINS')
		iDesert = gc.getInfoTypeForString('TERRAIN_DESERT')
		iGrass = gc.getInfoTypeForString('TERRAIN_GRASS')
		iMarsh = gc.getInfoTypeForString('TERRAIN_MARSH')
		iSmoke = gc.getInfoTypeForString('IMPROVEMENT_SMOKE')
		iFlames = gc.getInfoTypeForString('FEATURE_FLAMES')
		iForestAncient = gc.getInfoTypeForString('FEATURE_FOREST_ANCIENT')
		iForest = gc.getInfoTypeForString('FEATURE_FOREST')
		
		for i in range (CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			if pPlot.getOwner() == iPlayer:
			
				# Change Terrain
				iTerrain = pPlot.getTerrainType()
				if iTerrain == iSnow:
					pPlot.setTerrainType(iTundra,True,True)
				elif iTerrain == iTundra or iTerrain == iMarsh or iTerrain == iShallows:
					pPlot.setTerrainType(iPlains,True,True)
				elif (iTerrain == iDesert or iTerrain == iBurningSands):
					pPlot.setTerrainType(iPlains,True,True)
				elif (iTerrain == iPlains or iTerrain == iFields or iTerrain == iBrokenLands):
					pPlot.setTerrainType(iGrass,True,True)
					
				# Put out fire and smoke
				if pPlot.getImprovementType() == iSmoke:
					pPlot.setImprovementType(-1)
				if pPlot.getFeatureType() == iFlames:
					pPlot.setFeatureType(-1, -1)					

				# Grow Forests - TODO - let forests grow over improvements if allowed by civs (ie Elves)
				if (pPlot.getTerrainType() == iGrass and pPlot.getImprovementType() == -1 and pPlot.getFeatureType() != iForestAncient and pPlot.isPeak() == False and pPlot.isCity() == False):
					pPlot.setFeatureType(iForest, 0)
					
				# Remove blight
				pPlot.changePlotCounter(-100)
				
#				iTemp = pPlot.getFeatureType()
#				if iTemp!=-1:
#					pPlot.setFeatureType(iTemp, 0)

	def snowgenesis(self, iPlayer):
		iBrokenLands = gc.getInfoTypeForString('TERRAIN_BROKEN_LANDS')
		iFields = gc.getInfoTypeForString('TERRAIN_FIELDS_OF_PERDITION')
		iBurningSands = gc.getInfoTypeForString('TERRAIN_BURNING_SANDS')
		iShallows = gc.getInfoTypeForString('TERRAIN_SHALLOWS')
		iSnow = gc.getInfoTypeForString('TERRAIN_SNOW')
		iTundra = gc.getInfoTypeForString('TERRAIN_TUNDRA')
		iPlains = gc.getInfoTypeForString('TERRAIN_PLAINS')
		iDesert = gc.getInfoTypeForString('TERRAIN_DESERT')
		iGrass = gc.getInfoTypeForString('TERRAIN_GRASS')
		iMarsh = gc.getInfoTypeForString('TERRAIN_MARSH')
		iSmoke = gc.getInfoTypeForString('IMPROVEMENT_SMOKE')
		iFlames = gc.getInfoTypeForString('FEATURE_FLAMES')
		iForestAncient = gc.getInfoTypeForString('FEATURE_FOREST_ANCIENT')
		iForest = gc.getInfoTypeForString('FEATURE_FOREST')
		
		for i in range (CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			if pPlot.getOwner() == iPlayer:
			
				# Change terrain
				iTerrain = pPlot.getTerrainType()
				pPlot.changePlotCounter(-100)
				if (iTerrain == iGrass or iTerrain == iPlains or iTerrain == iBrokenLands or iTerrain == iTundra or iTerrain == iFields):
					pPlot.setTerrainType(iSnow,True,True)
				elif (iTerrain == iDesert or iTerrain == iBurningSands or iTerrain == iMarsh or iTerrain == iShallows):
					pPlot.setTerrainType(iTundra,True,True)
					
				#Put out fire and smoke
				if pPlot.getImprovementType() == iSmoke:
					pPlot.setImprovementType(-1)
				if pPlot.getFeatureType() == iFlames:
					pPlot.setFeatureType(-1, -1)

				# Grow Forests
				if (pPlot.getTerrainType() == iTundra and pPlot.getImprovementType() == -1 and pPlot.getFeatureType() != iForestAncient and pPlot.isPeak() == False and pPlot.isCity() == False):
					pPlot.setFeatureType(iForest, 1)

				# Remove blight
				pPlot.changePlotCounter(-100)

##--------		Tweaked Hyborem: Added by Denev	--------##
	def getAshenVeilCities(self, iCasterPlayer, iCasterID, iNum):
		pCasterPlayer = gc.getPlayer(iCasterPlayer)
		pCaster = pCasterPlayer.getUnit(iCasterID)

		iVeil = gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL')
		ltVeilCities = []

		for iPlayer in range(gc.getMAX_PLAYERS()):
			pTargetPlayer = gc.getPlayer(iPlayer)

			if not pTargetPlayer.isAlive():
				continue

			if pTargetPlayer.getTeam() == pCasterPlayer.getTeam():
				continue

			if (gc.getTeam(pCasterPlayer.getTeam()).isVassal(pTargetPlayer.getTeam())):
				continue

			iBaseModifier = 100
			if pTargetPlayer.getStateReligion() == iVeil:
				iBaseModifier -= 20
			if pTargetPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_EVIL'):
				iBaseModifier -= 10

			for pyCity in PyPlayer(iPlayer).getCityList():
				pTargetCity = pyCity.GetCy()
				if pTargetCity.isHasReligion(iVeil) and not pTargetCity.isCapital():
					iValue = pTargetCity.getPopulation() * 100
					iValue += pTargetCity.getCulture(iPlayer) / 3
					iValue += pTargetCity.getNumBuildings() * 10
					iValue += pTargetCity.getNumWorldWonders() * 100
					iValue += pTargetCity.countNumImprovedPlots()

					iModifier = iBaseModifier
					pCasterCapital = pCasterPlayer.getCapitalCity()
					if not pCasterCapital.isNone() and pTargetCity.area().getID() == pCasterCapital.area().getID():
						iModifier += 10
					if pTargetCity.area().getCitiesPerPlayer(iCasterPlayer) > 0:
						iModifier += 10

					if pCasterPlayer.getNumCities() > 0:
						iMinDistance = -1
						for pyCity in PyPlayer(iCasterPlayer).getCityList():
							pLoopCity = pyCity.GetCy()
							if pLoopCity.getID() == pTargetCity.getID():
								continue
							iDistance = stepDistance(pLoopCity.getX(), pLoopCity.getY(), pTargetCity.getX(), pTargetCity.getY())
							if iMinDistance == -1 or iMinDistance > iDistance:
								iMinDistance = iDistance
						if iMinDistance != -1:
							iModifier -= iMinDistance

					iModifier = max(0, iModifier)
					iValue = (iValue * iModifier) // 100

					ltVeilCities.append((iValue, pTargetCity))

		ltVeilCities.sort()
		ltVeilCities.reverse()
		lpVeilCities = []
		if len(ltVeilCities) > 0:
			ltVeilCities = ltVeilCities[0:min(iNum, len(ltVeilCities))]
			lpVeilCities = [pCity for iValue, pCity in ltVeilCities]
		return lpVeilCities
##--------		Tweaked Hyborem: End Modify			--------##

	def getCivilization(self, iCiv):
		i = -1
		for iPlayer in range(gc.getMAX_PLAYERS()):
			pPlayer = gc.getPlayer(iPlayer)
			if pPlayer.getCivilizationType() == iCiv:
				i = iPlayer
		return i

	def getHero(self, pPlayer):
		iHero = -1
		iHeroUnit = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getHero()
		if iHeroUnit != -1:
			iHero = gc.getUnitInfo(iHeroUnit).getUnitClassType()
		return iHero

	def getLeader(self, iLeader):
		i = -1
		for iPlayer in range(gc.getMAX_PLAYERS()):
			pPlayer = gc.getPlayer(iPlayer)
			if pPlayer.getLeaderType() == iLeader:
				i = iPlayer
		return i

	def getOpenPlayer(self):
		i = -1
		for iPlayer in range(gc.getMAX_PLAYERS()):
			pPlayer = gc.getPlayer(iPlayer)
			if (pPlayer.isEverAlive() == False and i == -1):
				i = iPlayer
		return i

	def getUnholyVersion(self, pUnit):
		iUnit = -1
		if pUnit.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_ADEPT'):
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 2:
				iUnit = gc.getInfoTypeForString('UNIT_IMP')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 3:
				iUnit = gc.getInfoTypeForString('UNIT_MAGE')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 4:
				iUnit = gc.getInfoTypeForString('UNIT_LICH')
		if pUnit.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_ANIMAL') or pUnit.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_BEAST'):
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 1:
				iUnit = gc.getInfoTypeForString('UNIT_SCOUT')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 2:
				iUnit = gc.getInfoTypeForString('UNIT_HELLHOUND')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 3:
				iUnit = gc.getInfoTypeForString('UNIT_ASSASSIN')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 4:
				iUnit = gc.getInfoTypeForString('UNIT_BEAST_OF_AGARES')
		if pUnit.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_ARCHER'):
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 2:
				iUnit = gc.getInfoTypeForString('UNIT_ARCHER')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 3:
				iUnit = gc.getInfoTypeForString('UNIT_LONGBOWMAN')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 4:
				iUnit = gc.getInfoTypeForString('UNIT_CROSSBOWMAN')
		if pUnit.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_DISCIPLE'):
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 2:
				iUnit = gc.getInfoTypeForString('UNIT_DISCIPLE_THE_ASHEN_VEIL')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 3:
				iUnit = gc.getInfoTypeForString('UNIT_PRIEST_OF_THE_VEIL')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 4:
				iUnit = gc.getInfoTypeForString('UNIT_EIDOLON')
		if pUnit.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_MELEE'):
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 1:
				iUnit = gc.getInfoTypeForString('UNIT_SKELETON')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 2:
				iUnit = gc.getInfoTypeForString('UNIT_DISEASED_CORPSE')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 3:
				iUnit = gc.getInfoTypeForString('UNIT_CHAMPION')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 4:
				iUnit = gc.getInfoTypeForString('UNIT_BALOR')
		if pUnit.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_MOUNTED'):
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 2:
				iUnit = gc.getInfoTypeForString('UNIT_HORSEMAN')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 3:
				iUnit = gc.getInfoTypeForString('UNIT_CHARIOT')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 4:
				iUnit = gc.getInfoTypeForString('UNIT_DEATH_KNIGHT')
		if pUnit.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_RECON'):
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 1:
				iUnit = gc.getInfoTypeForString('UNIT_SCOUT')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 2:
				iUnit = gc.getInfoTypeForString('UNIT_HELLHOUND')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 3:
				iUnit = gc.getInfoTypeForString('UNIT_ASSASSIN')
			if gc.getUnitInfo(pUnit.getUnitType()).getTier() == 4:
				iUnit = gc.getInfoTypeForString('UNIT_BEASTMASTER')
		return iUnit

	def getUnitPlayerID(self, pUnit):
		pPlayer = gc.getPlayer(pUnit.getOwner())
		iID = pUnit.getID()
		iUnitID = -1
		for iUnit in range(pPlayer.getNumUnits()):
			pLoopUnit = pPlayer.getUnit(iUnit)
			if pLoopUnit.getID() == iID:
				iUnitID = iUnit
		return iUnitID

	def giftUnit(self, iUnit, iCivilization, iXP, pFromPlot, iFromPlayer):
		iAngel = gc.getInfoTypeForString('UNIT_ANGEL')
		iManes = gc.getInfoTypeForString('UNIT_MANES')
		if (iUnit == iAngel or iUnit == iManes):
			iChance = 100 - (CyGame().countCivPlayersAlive() * 3)
			iChance = iChance + iXP
			if iChance < 5:
				iChance = 5
			if iChance > 95:
				iChance = 95
			if CyGame().getSorenRandNum(100, "Gift Unit") > iChance:
				iUnit = -1
		if iUnit != -1:
			bValid = False
			for iPlayer in range(gc.getMAX_PLAYERS()):
				pPlayer = gc.getPlayer(iPlayer)
				if (pPlayer.isAlive()):
					if pPlayer.getCivilizationType() == iCivilization:
						py = PyPlayer(iPlayer)
						if pPlayer.getNumCities() > 0:
							iRnd = CyGame().getSorenRandNum(py.getNumCities(), "Gift Unit")
							pCity = py.getCityList()[iRnd]
							pPlot = pCity.plot()
							newUnit = pPlayer.initUnit(iUnit, pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
							newUnit.changeExperience(iXP, -1, False, False, False)
							newUnit.setWeapons()
							if (pFromPlot != -1 and gc.getPlayer(iFromPlayer).isHuman()):
								bValid = True
							if pPlayer.isHuman():
								if iUnit == iManes:
									CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_ADD_MANES",()),'AS2D_UNIT_FALLS',1,'Art/Interface/Buttons/Promotions/Demon.dds',ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)
								if iUnit == iAngel:
									CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_ADD_ANGEL",()),'AS2D_UNIT_FALLS',1,'Art/Interface/Buttons/Promotions/Angel.dds',ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)
#							if (pPlayer.isHuman() == False and iUnit == iManes and pCity != -1):
#								if CyGame().getSorenRandNum(100, "Manes") < (100 - (pCity.getPopulation() * 5)):
#									pCity.changePopulation(1)
#									newUnit.kill(True, PlayerTypes.NO_PLAYER)
			if bValid:
				if iUnit == iManes:
					CyInterface().addMessage(iFromPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_FALLS",()),'AS2D_UNIT_FALLS',1,'Art/Interface/Buttons/Promotions/Demon.dds',ColorTypes(7),pFromPlot.getX(),pFromPlot.getY(),True,True)
				if iUnit == iAngel:
					CyInterface().addMessage(iFromPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_UNIT_RISES",()),'AS2D_UNIT_FALLS',1,'Art/Interface/Buttons/Promotions/Angel.dds',ColorTypes(7),pFromPlot.getX(),pFromPlot.getY(),True,True)

	def placeTreasure(self, iPlayer, iUnit):
		pPlayer = gc.getPlayer(iPlayer)
		pBestPlot = -1
		iBestPlot = -1
		for i in range (CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			iPlot = -1
			if not pPlot.isWater():
				if pPlot.getNumUnits() == 0:
					if not pPlot.isCity():
						if not pPlot.isImpassable():
							iPlot = CyGame().getSorenRandNum(1000, "Add Unit")
							if pPlot.area().getNumTiles() < 8:
								iPlot += 1000
							if not pPlot.isOwned():
								iPlot += 1000
							if iPlot > iBestPlot:
								iBestPlot = iPlot
								pBestPlot = pPlot
		if iBestPlot != -1:
			newUnit = pPlayer.initUnit(iUnit, pBestPlot.getX(), pBestPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
			CyInterface().addMessage(iPlayer,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_EXPLORE_LAIR_TREASURE",()),'',1,'Art/Interface/Buttons/Equipment/Treasure.dds',ColorTypes(8),newUnit.getX(),newUnit.getY(),True,True)
			CyCamera().JustLookAtPlot(pBestPlot)

	def showUniqueImprovements(self, iPlayer):
		pPlayer = gc.getPlayer(iPlayer)
		iTeam = pPlayer.getTeam()
		for i in range (CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			if pPlot.getImprovementType() != -1:
				if gc.getImprovementInfo(pPlot.getImprovementType()).isUnique():
					pPlot.setRevealed(iTeam, True, False, TeamTypes.NO_TEAM)

	def startWar(self, iPlayer, i2Player, iWarPlan):
		iTeam = gc.getPlayer(iPlayer).getTeam()
		i2Team = gc.getPlayer(i2Player).getTeam()
		eTeam = gc.getTeam(iTeam)
		e2Team = gc.getTeam(i2Team)
		if eTeam.isAlive():
			if e2Team.isAlive():
				if not eTeam.isAtWar(i2Team):
					if iTeam != i2Team:
						if eTeam.isHasMet(i2Team):
							if not eTeam.isPermanentWarPeace(i2Team):
								eTeam.declareWar(i2Team, false, iWarPlan)

	def warScript(self, iPlayer):
		pPlayer = gc.getPlayer(iPlayer)
		iEnemy = -1
		for iPlayer2 in range(gc.getMAX_PLAYERS()):
			pPlayer2 = gc.getPlayer(iPlayer2)
			if pPlayer2.isAlive():
				iTeam = gc.getPlayer(iPlayer).getTeam()
				iTeam2 = gc.getPlayer(iPlayer2).getTeam()
				eTeam = gc.getTeam(iTeam)
				if eTeam.isAVassal() == False:
					if eTeam.isAtWar(iTeam2):
						if CyGame().getSorenRandNum(100, "War Script") < 5:
							self.dogpile(iPlayer, iPlayer2)
					if self.warScriptAllow(iPlayer, iPlayer2):
						if pPlayer2.getBuildingClassMaking(gc.getInfoTypeForString('BUILDINGCLASS_TOWER_OF_MASTERY')) > 0:
							if eTeam.getAtWarCount(True) == 0:
								self.startWar(iPlayer, iPlayer2, WarPlanTypes.WARPLAN_TOTAL)
						if (pPlayer2.getNumBuilding(gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_DIVINE')) > 0 or pPlayer2.getNumBuilding(gc.getInfoTypeForString('BUILDING_ALTAR_OF_THE_LUONNOTAR_EXALTED')) > 0):
							if pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_EVIL'):
								if eTeam.getAtWarCount(True) == 0:
									self.startWar(iPlayer, iPlayer2, WarPlanTypes.WARPLAN_TOTAL)
						if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_MERCURIANS'):
							if pPlayer2.getStateReligion() == gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL'):
								self.startWar(iPlayer, iPlayer2, WarPlanTypes.WARPLAN_TOTAL)
						if CyGame().getGlobalCounter() > 20:
							if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_SVARTALFAR'):
								if (pPlayer2.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LJOSALFAR') and CyGame().getPlayerRank(iPlayer) > CyGame().getPlayerRank(iPlayer2)):
									self.startWar(iPlayer, iPlayer2, WarPlanTypes.WARPLAN_TOTAL)
							if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_LJOSALFAR'):
								if (pPlayer2.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_SVARTALFAR') and CyGame().getPlayerRank(iPlayer) > CyGame().getPlayerRank(iPlayer2)):
									self.startWar(iPlayer, iPlayer2, WarPlanTypes.WARPLAN_TOTAL)
						if (CyGame().getGlobalCounter() > 40 or pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_INFERNAL') or pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_DOVIELLO')):
							if pPlayer.getAlignment() == gc.getInfoTypeForString('ALIGNMENT_EVIL'):
								if (eTeam.getAtWarCount(True) == 0 and CyGame().getPlayerRank(iPlayer2) > CyGame().getPlayerRank(iPlayer)):
									if (iEnemy == -1 or CyGame().getPlayerRank(iPlayer2) > CyGame().getPlayerRank(iEnemy)):
										iEnemy = iPlayer2
		if iEnemy != -1:
			if CyGame().getPlayerRank(iPlayer) > CyGame().getPlayerRank(iEnemy):
				self.startWar(iPlayer, iEnemy, WarPlanTypes.WARPLAN_TOTAL)

	def warScriptAllow(self, iPlayer, iPlayer2):
		pPlayer = gc.getPlayer(iPlayer)
		pPlayer2 = gc.getPlayer(iPlayer2)
		iTeam = gc.getPlayer(iPlayer).getTeam()
		iTeam2 = gc.getPlayer(iPlayer2).getTeam()
		eTeam = gc.getTeam(iTeam)
		if iPlayer == gc.getBARBARIAN_PLAYER():
			return False
		if eTeam.isHasMet(iTeam2) == False:
			return False
		if eTeam.AI_getAtPeaceCounter(iTeam2) < 20:
			return False
#		if pPlayer.AI_getAttitude(iPlayer2) <= gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getDeclareWarRefuseAttitudeThreshold():
#			return False
		if eTeam.isAtWar(iTeam2):
			return False
		if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_INFERNAL'):
			if pPlayer2.getStateReligion() == gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL'):
				return False
		return True

	def dogpile(self, iPlayer, iVictim):
		pPlayer = gc.getPlayer(iPlayer)
		for iPlayer2 in range(gc.getMAX_PLAYERS()):
			pPlayer2 = gc.getPlayer(iPlayer2)
			iChance = -1
			if pPlayer2.isAlive():
				if (self.dogPileAllow(iPlayer, iPlayer2) and self.warScriptAllow(iPlayer2, iVictim)):
					iChance = pPlayer2.AI_getAttitude(iPlayer) * 5
					if iChance > 0:
						iChance = iChance - (pPlayer2.AI_getAttitude(iVictim) * 5) - 10
						if CyGame().isOption(gc.getInfoTypeForString('GAMEOPTION_AGGRESSIVE_AI')) == False:
							iChance = iChance - 10
						if iChance > 0:
							iChance = iChance + (CyGame().getGlobalCounter() / 3)
							if pPlayer2.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_BALSERAPHS'):
								iChance = CyGame().getSorenRandNum(50, "Dogpile")
							if CyGame().getSorenRandNum(100, "Dogpile") < iChance:
								self.startWar(iPlayer2, iVictim, WarPlanTypes.WARPLAN_DOGPILE)

	def dogPileAllow(self, iPlayer, iPlayer2):
		pPlayer = gc.getPlayer(iPlayer)
		pPlayer2 = gc.getPlayer(iPlayer2)
		iTeam = gc.getPlayer(iPlayer).getTeam()
		iTeam2 = gc.getPlayer(iPlayer2).getTeam()
		if iPlayer == iPlayer2:
			return False
		if iTeam == iTeam2:
			return False
		if pPlayer2.isHuman():
			return False
		if pPlayer2.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_ELOHIM'):
			return False
		if gc.getTeam(iTeam2).isAVassal():
			return False
		return True

	def warn(self, iPlayer, szText, pPlot):
		pPlayer = gc.getPlayer(iPlayer)
		for iPlayer2 in range(gc.getMAX_PLAYERS()):
			pPlayer2 = gc.getPlayer(iPlayer2)
			if (pPlayer2.isAlive() and iPlayer != iPlayer2):
				if pPlayer2.isHuman():
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
					popupInfo.setText(szText)
					popupInfo.setOnClickedPythonCallback("selectWarn")
					popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_MAIN_MENU_OK",()), "")
					popupInfo.addPopup(iPlayer2)
				if pPlot != -1:
					CyInterface().addMessage(iPlayer2,True,25,CyTranslator().getText("TXT_KEY_MESSAGE_ALTAR_OF_THE_LUONNOTAR",()),'AS2D_DISCOVERBONUS',1,'Art/Interface/Buttons/Buildings/AltaroftheLuonnotar.dds',ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)

	def MarnokNameGenerator(self, unit):
		pPlayer = gc.getPlayer(unit.getOwner())	
		pCiv = pPlayer.getCivilizationType() 
		pReligion = pPlayer.getStateReligion()
		pAlign = pPlayer.getAlignment() 

		lPre=["ta","go","da","bar","arc","ken","an","ad","mi","kon","kar","mar","wal","he", "ha", "re", "ar", "bal", "bel", "bo", "bri", "car","dag","dan","ma","ja","co","be","ga","qui","sa"]
		lMid=["ad","z","the","and","tha","ent","ion","tio","for","tis","oft","che","gan","an","en","wen","on","d","n","g","t","ow","dal"]
		lEnd=["ar","sta","na","is","el","es","ie","us","un","th", "er","on","an","re","in","ed","nd","at","en","le","man","ck","ton","nok","git","us","or","a","da","u","cha","ir"]
	
		lEpithet=["red","blue","black","grey","white","strong","brave","old","young","great","slayer","hunter","seeker"]
		lNoun=["spirit","soul","boon","born","staff","rod","shield","autumn","winter","spring","summer","wit","horn","tusk","glory","claw","tooth","head","heart", "blood","breath", "blade", "hand", "lover","bringer","maker","taker","river","stream","moon","star","face","foot","half","one","hundred","thousand"]
		lSchema=["CPME","CPMESCPME","CPESCPE","CPE","CPMME","CPMDCME","CPMAME","KCPMESCUM","CPMME[ the ]CX", "CPMESCXN", "CPMME[ of ]CPMME", "CNNSCXN"]

		if pAlign == gc.getInfoTypeForString('ALIGNMENT_EVIL'):
			lNoun = lNoun + ["fear","terror","reign","brood","snare","war","strife","pain","hate","evil","hell","misery","murder","anger","fury","rage","spawn","sly","blood","bone","scythe","slave","bound","ooze","scum"]
			lEpithet=["dark","black","white","cruel","foul"]		
	
		if pReligion == gc.getInfoTypeForString('RELIGION_THE_ASHEN_VEIL'):
			lEpithet = lEpithet + ["fallen","diseased","infernal","profane","corrupt"]
			lSchema = lSchema + ["CPME[ the ]CX"]
		if pReligion == gc.getInfoTypeForString('RELIGION_OCTOPUS_OVERLORDS'):
			lPre = lPre + ["cth","cht","shu","az","ts","dag","hy","gla","gh","rh","x","ll"]
			lMid = lMid + ["ul","tha","on","ug","st","oi"]
			lEnd = lEnd + ["hu","on", "ha","ua","oa","uth","oth","ath","thua", "thoa","ur","ll","og","hua"]
			lEpithet = lEpithet + ["nameless","webbed","deep","watery"]
			lNoun = lNoun + ["tentacle","wind","wave","sea","ocean","dark","crab","abyss","island"]
			lSchema = lSchema + ["CPMME","CPDMME","CPAMAME","CPMAME","CPAMAMEDCPAMAE"]
		if pReligion == gc.getInfoTypeForString('RELIGION_THE_ORDER'):
			lPre = lPre + ["ph","v","j"]
			lMid = lMid + ["an","al","un"]
			lEnd = lEnd + ["uel","in","il"]
			lEpithet = lEpithet + ["confessor","crusader", "faithful","obedient","good"]
			lNoun = lNoun + ["order", "faith", "heaven","law"]
			lSchema = lSchema + ["CPESCPME","CPMESCPE","CPMESCPME", "CPESCPE"]
		if pReligion == gc.getInfoTypeForString('RELIGION_FELLOWSHIP_OF_LEAVES'):
			lPre = lPre + ["ki","ky","yv"]
			lMid = lMid + ["th","ri"]
			lEnd = lEnd + ["ra","el","ain"]
			lEpithet = lEpithet + ["green"]
			lNoun = lNoun + ["tree","bush","wood","berry","elm","willow","oak","leaf","flower","blossom"]
			lSchema = lSchema + ["CPESCN","CPMESCNN","CPMESCXN"]
		if pReligion == gc.getInfoTypeForString('RELIGION_RUNES_OF_KILMORPH'):
			lPre = lPre + ["bam","ar","khel","ki"]
			lMid = lMid + ["th","b","en"]
			lEnd = lEnd + ["ur","dain","ain","don"]
			lEpithet = lEpithet + ["deep","guard","miner"]
			lNoun = lNoun + ["rune","flint","slate","stone","rock","iron","copper","mithril","thane","umber"]
			lSchema = lSchema + ["CPME","CPMME"]
		if pReligion == gc.getInfoTypeForString('RELIGION_THE_EMPYREAN'):
			lEpithet = lEpithet + ["radiant","holy"]
			lNoun = lNoun + ["honor"]
		if pReligion == gc.getInfoTypeForString('RELIGION_COUNCIL_OF_ESUS'):
			lEpithet = lEpithet + ["hidden","dark"]
			lNoun = lNoun + ["cloak","shadow","mask"]
			lSchema = lSchema + ["CPME","CPMME"]

		if unit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_ENRAGED')) == True:
			# I have left this as a copy of the Barbarian, see how it goes, this might do the trick. I plan to use it when there is a chance a unit will go Barbarian anyway.
			lPre = lPre + ["gru","bra","no","os","dir","ka","z"]
			lMid = lMid + ["g","ck","gg","sh","b","bh","aa"]
			lEnd = lEnd + ["al","e","ek","esh","ol","olg","alg"]
			lNoun = lNoun + ["death", "hate", "rage", "mad","insane","berserk"]
			lEpithet = lEpithet + ["smasher", "breaker", "mangle","monger"]

		if unit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_CRAZED')) == True:
			# might want to tone this down, because I plan to use it as possession/driven to madness, less than madcap zaniness.
			lPre = lPre + ["mad","pim","zi","zo","fli","mum","dum","odd","slur"]
			lMid = lMid + ["bl","pl","gg","ug","bl","b","zz","abb","odd"]
			lEnd = lEnd + ["ad","ap","izzle","onk","ing","er","po","eep","oggle","y"]

		if unit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_VAMPIRE')) == True:
			lPre = lPre + ["dra","al","nos","vam","vla","tep","bat","bar","cor","lil","ray","zar","stra","le"]
			lMid = lMid + ["cul","u","car","fer","pir","or","na","ov","sta"]
			lEnd = lEnd + ["a","d","u","e","es","y","bas","vin","ith","ne","ak","ich","hd","t"]

		if unit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_DEMON')) == True:
			lPre = lPre + ["aa","ab","adr","ah","al","de","ba","cro","da","be","eu","el","ha","ib","me","she","sth","z"]
			lMid = lMid + ["rax","lia","ri","al","as","b","bh","aa","al","ze","phi","sto","phe","cc","ee"]
			lEnd = lEnd + ["tor","tan","ept","lu","res","ah","mon","gon","bul","gul","lis","les","uz"]
			lSchema = ["CPMMME","CPMACME", "CPKMAUAPUE", "CPMMME[ the ]CNX"]

		if unit.getUnitType() == gc.getInfoTypeForString('UNIT_HILL_GIANT'):
			lPre = lPre + ["gor","gra","gar","gi","gol"]
			lMid = lMid + ["gan","li","ri","go"]
			lEnd = lEnd + ["tus","tan","ath","tha"]
			lSchema = lSchema +["CXNSCNN","CPESCNE", "CPMME[ the ]CX"]
			lEpithet = lEpithet + ["large","huge","collossal","brutal","basher","smasher","crasher","crusher"]
			lNoun = lNoun + ["fist","tor","hill","brute","stomp"]

		if unit.getUnitType() == gc.getInfoTypeForString('UNIT_LIZARDMAN'):
			lPre = lPre + ["ss","s","th","sth","hss"]
			lEnd = lEnd + ["ess","iss","ath","tha"]
			lEpithet = lEpithet + ["cold"]
			lNoun = lNoun + ["hiss","tongue","slither","scale","tail","ruin"]
			lSchema = lSchema + ["CPAECPAE","CPAKECPAU","CPAMMAE"]
		if unit.getUnitType() == gc.getInfoTypeForString('UNIT_FIRE_ELEMENTAL') or unit.getUnitType() == gc.getInfoTypeForString('UNIT_AZER'):
			lPre = lPre + ["ss","cra","th","sth","hss","roa"]
			lMid = lMid + ["ss","ck","rr","oa","iss","tt"]
			lEnd = lEnd + ["le","iss","st","r","er"]
			lNoun = lNoun + ["hot", "burn","scald","roast","flame","scorch","char","sear","singe","fire","spit"]
			lSchema = ["CNN","CNX","CPME","CPME[ the ]CNX","CPMME","CNNSCPME"]
		if unit.getUnitType() == gc.getInfoTypeForString('UNIT_WATER_ELEMENTAL'):
			lPre = lPre + ["who","spl","dr","sl","spr","sw","b"]
			lMid = lMid + ["o","a","i","ub","ib"]
			lEnd = lEnd + ["sh","p","ter","ble"]
			lNoun = lNoun + ["wave","lap","sea","lake","water","tide","surf","spray","wet","damp","soak","gurgle","bubble"]
			lSchema = ["CNN","CNX","CPME","CPME[ the ]CNX","CPMME","CNNSCPME"]
		if unit.getUnitType() == gc.getInfoTypeForString('UNIT_AIR_ELEMENTAL'):
			lPre = lPre + ["ff","ph","th","ff","ph","th"]
			lMid = lMid + ["oo","aa","ee","ah","oh"]
			lEnd = lEnd + ["ff","ph","th","ff","ph","th"]
			lNoun = lNoun + ["wind","air","zephyr","breeze","gust","blast","blow"]
			lSchema = ["CNN","CNX","CPME","CPME[ the ]CNX","CPMME","CNNSCPME"]
		if unit.getUnitType() == gc.getInfoTypeForString('UNIT_EARTH_ELEMENTAL'):
			lPre = lPre + ["gra","gro","kro","ff","ph","th"]
			lMid = lMid + ["o","a","u"]
			lEnd = lEnd + ["ck","g","k"]
			lNoun = lNoun + ["rock","stone","boulder","slate","granite","rumble","quake"]
			lSchema = ["CNN","CNX","CPME","CPME[ the ]CNX","CPMME","CNNSCPME"]

		# SEA BASED
		# Check for ships - special schemas
		if unit.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_NAVAL'):
			lEnd = lEnd + ["ton","town","port"]
			lNoun = lNoun + ["lady","jolly","keel","bow","stern", "mast","sail","deck","hull","reef","wave"]
			lEpithet = lEpithet + ["sea", "red", "blue","grand","barnacle","gull"]
			lSchema = ["[The ]CNN", "[The ]CXN", "[The ]CNX","[The ]CNSCN", "[The ]CNSCX","CPME['s ]CN","[The ]CPME", "[The ]CNX","CNX","CN['s ]CN"]

		# # #
		# Pick a Schema
		sSchema = lSchema[CyGame().getSorenRandNum(len(lSchema), "Name Gen")-1]
		sFull = ""
		sKeep = ""
		iUpper = 0
		iKeep = 0
		iSkip = 0

		# Run through each character in schema to generate name
		for iCount in range (0,len(sSchema)):
			sAdd=""
			iDone = 0
			sAction = sSchema[iCount]
			if iSkip == 1:
				if sAction == "]":
					iSkip = 0
				else:
					sAdd = sAction
					iDone = 1
			else:					# MAIN SECTION
				if sAction == "P": 	# Pre 	: beginnings of names
					sAdd = lPre[CyGame().getSorenRandNum(len(lPre), "Name Gen")-1]
					iDone = 1
				if sAction == "M":	# Mid 	: middle syllables
					sAdd = lMid[CyGame().getSorenRandNum(len(lMid), "Name Gen")-1]
					iDone = 1
				if sAction == "E":	# End	: end of names
					sAdd = lEnd[CyGame().getSorenRandNum(len(lEnd), "Name Gen")-1]
					iDone = 1
				if sAction == "X":	# Epithet	: epithet word part
					#epithets ("e" was taken!)
					sAdd = lEpithet[CyGame().getSorenRandNum(len(lEpithet), "Name Gen")-1]
					iDone = 1
				if sAction == "N":	# Noun	: noun word part
					#noun
					sAdd = lNoun[CyGame().getSorenRandNum(len(lNoun), "Name Gen")-1]
					iDone = 1
				if sAction == "S":	# Space	: a space character. (Introduced before [ ] was possible )
					sAdd =  " "
					iDone = 1
				if sAction == "D":	# Dash	: a - character. Thought to be common and useful enough to warrant inclusion : Introduced before [-] was possible
					sAdd =  "-"
					iDone = 1
				if sAction == "A":	# '		: a ' character - as for -, introduced early
					sAdd = "'"
					iDone = 1
				if sAction == "C":	# Caps	: capitalizes first letter of next phrase generated. No effect on non-letters.
					iUpper = 1
				if sAction == "K":	# Keep	: stores the next phrase generated for re-use with U
					iKeep = 1
				if sAction == "U":	# Use	: re-uses a stored phrase.
					sAdd = sKeep
					iDone = 1
				if sAction == "[":	# Print	: anything between [] is added to the final phrase "as is". Useful for [ the ] and [ of ] among others.
					iSkip = 1
			# capitalizes phrase once.
			if iUpper == 1 and iDone == 1:
				sAdd = sAdd.capitalize()
				iUpper = 0
			# stores the next phrase generated.
			if iKeep == 1 and iDone == 1:
				sKeep = sAdd
				iKeep = 0
			# only adds the phrase if a new bit was actally created.
			if iDone == 1:
				sFull = sFull + sAdd

		# trim name length
		if len(sFull) > 25:
			sFull = sFull[:25]
		#CyInterface().addMessage(caster.getOwner(),True,25,"NAME : "+sFull,'AS2D_POSITIVE_DINK',1,'Art/Interface/Buttons/Spells/Rob Grave.dds',ColorTypes(8),pPlot.getX(),pPlot.getY(),True,True)

		return sFull
