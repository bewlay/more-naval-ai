## Buffy
##
## Collection of utility functions for dealing with BUFFY.
##
## Notes
##   - Must be initialized externally by calling init()
##
## Copyright (c) 2009 The BUG Mod.
##
## Author: Ruff_Hi, EmperorFool

from CvPythonExtensions import *
import BugCore
import BugPath
import BugUtil
import CvUtil
import GameUtil
import os.path

gc = CyGlobalContext()
options = BugCore.game.BUFFY

IS_ACTIVE = False
IS_DLL_PRESENT = False
IS_DLL_IN_CORRECT_PATH = False


## Checking Status

def isEnabled():
	return options.isEnabled()

def isActive():
	"""
	Returns True if BUFFY is active in this session.
	
	Must be a BUFFY-enabled build with the DLL present and not running on a Mac.
	"""
	return IS_ACTIVE

def isDllPresent():
	"""
	Returns True if this is a BUFFY-enabled build and the BUFFY DLL is present, False otherwise.
	
	Note: If this isn't a BUFFY-enabled build, this function returns False even if the BUFFY DLL is present
	since init() doesn't look for the DLL.
	"""
	return IS_DLL_PRESENT

def isDllInCorrectPath():
	"""
	Returns True if the BUFFY DLL is present and in the correct location (...\<BTS>\Mods\<BUFFY>\Assets\).
	"""
	return IS_DLL_IN_CORRECT_PATH


## Initialization

def init():
	"""
	Checks for the presence of the BUFFY DLL and sets the global flags.
	"""
	if isEnabled():
		if BugPath.isMac():
			BugUtil.debug("BUFFY is not active on Mac (no DLL)")
		else:
			try:
				if gc.isBuffy():
					global IS_DLL_PRESENT, IS_DLL_IN_CORRECT_PATH, IS_ACTIVE
					IS_DLL_PRESENT = True
					IS_ACTIVE = True
					BugUtil.info("BUFFY is active (API version %d)", gc.getBuffyApiVersion())
					try:
						dllPath = gc.getGame().getDLLPath()
						exePath = gc.getGame().getExePath()
						dllPathThenUp3 = os.path.dirname(os.path.dirname(os.path.dirname(dllPath)))
						if dllPathThenUp3 == exePath:
							IS_DLL_IN_CORRECT_PATH = True
					except:
						pass # DLL path is borked
			except:
				BugUtil.info("BUFFY is not active (no DLL)")
