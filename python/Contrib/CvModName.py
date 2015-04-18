#CvModName.py

from CvPythonExtensions import *

modName = "FFH - More Naval AI"
displayName = "FFH - More Naval AI"

civName = "BtS"
civVersion = "3.19"

def getName():
	return modName

def getDisplayName():
	return displayName

def getVersion():
	sVersion = unicode(CyTranslator().getText("TXT_KEY_VERSION", ()))
	versionStartNumber = 1 + sVersion.find( ' ' )
	versionEndNumber = sVersion.find( '</' )
	return sVersion[versionStartNumber:versionEndNumber]

def getNameAndVersion():
	return modName + " " + getVersion()

def getDisplayNameAndVersion():
	return displayName + " " + getVersion()


def getCivName():
	return civName

def getCivVersion():
	return civVersion

def getCivNameAndVersion():
	return civName + " " + civVersion
