## RevolutionDCM Mod Code
##
## This code uses the BUG standard to control RevolutionDCM options.
## RevolutionDCM.ini is generated by BUG and is the repository of all option states.
## Options are passed to the SDK via python calls that modify GlobalDefinesAlt.xml.
## Note:
## This code will only alter values in GlobalDefinesAlt.xml that have
## been defined in /Assets/Config/RevDCM.xml. Other values in GlobalDefinesAlt 
## may be changed manually as per usual. Values that have been defined in RevDCM.xml
## may also be manually changed, but will be overwritten by this code either on
## new turns or on game load or game initialisation.
##
## Copyright (c) 2007-2008 The BUG Mod.
##
## Author: Glider1

from CvPythonExtensions import *
gc = CyGlobalContext()
import BugOptions
import BugCore
import BugUtil
import Popup as PyPopup
import CvUtil
RevDCMOpt = BugCore.game.RevDCM

class RevDCM:
	def __init__(self, eventManager):
		eventManager.addEventHandler("OnLoad", self.onLoadGame)
		eventManager.addEventHandler("GameStart", self.onGameStart)

	def onLoadGame(self,argsList):
		self.optionUpdate()

	def onGameStart(self,argsList):
		self.optionUpdate()

	def optionUpdate(self):
		if RevDCMOpt.isReset():
			resetOptions()
		else:
			setXMLOptionsfromIniFile()



##################################################		
# Module level functions defined in RevDCM.xml	
##################################################	

def changedReset (option, value):
	resetOptions()
	return True
	
########################################################################
# Functions that change the SDK variable states in global alt defines
########################################################################

#Religion
def changedOC_RESPAWN_HOLY_CITIES (option, value):
	gc.setDefineINT("OC_RESPAWN_HOLY_CITIES", RevDCMOpt.isOC_RESPAWN_HOLY_CITIES())
def changedLIMITED_RELIGIONS_EXCEPTIONS (option, value):
	gc.setDefineINT("LIMITED_RELIGIONS_EXCEPTIONS", RevDCMOpt.isLIMITED_RELIGIONS_EXCEPTIONS())

#Hidden Attitude
def changedHiddenAttitude(option, value):
	gc.setDefineINT("SHOW_HIDDEN_ATTITUDE", RevDCMOpt.isHiddenAttitude())

#Dynamic Civ Names
def changedDYNAMIC_CIV_NAMES(option, value):
	gc.setDefineINT("DYNAMIC_CIV_NAMES", RevDCMOpt.isDYNAMIC_CIV_NAMES())
	

def setXMLOptionsfromIniFile():
	print "Reinitialising RevDCM SDK variables"

	#Religion
	gc.setDefineINT("OC_RESPAWN_HOLY_CITIES", RevDCMOpt.isOC_RESPAWN_HOLY_CITIES())
	gc.setDefineINT("LIMITED_RELIGIONS_EXCEPTIONS", RevDCMOpt.isLIMITED_RELIGIONS_EXCEPTIONS())
	#Hidden Attitude
	gc.setDefineINT("SHOW_HIDDEN_ATTITUDE", RevDCMOpt.isHiddenAttitude())
	#Dynamic Civ Names
	gc.setDefineINT("DYNAMIC_CIV_NAMES", RevDCMOpt.isDYNAMIC_CIV_NAMES())


def resetOptions():
	revDCMoptions = BugOptions.getOptions("RevDCM").options
	RevolutionOptions = BugOptions.getOptions("Revolution").options
	ActionOptions = BugOptions.getOptions("Actions").options
	for i in range(len(revDCMoptions)):
		revDCMoptions[i].resetValue()
	for i in range(len(RevolutionOptions)):
		RevolutionOptions[i].resetValue()
	for i in range(len(ActionOptions)):
		ActionOptions[i].resetValue()
	
	setXMLOptionsfromIniFile()
	RevDCMOpt.setReset(false)