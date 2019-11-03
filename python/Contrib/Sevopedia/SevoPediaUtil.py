## SevoPediaUtil
##
## Creates unsaved options for Sevopedia when it's accessed before BUG initializes.
##
## Copyright (c) 2008 The BUG Mod.
##
## Author: EmperorFool

import BugCore
import BugOptions
import BugUtil

AdvisorOpt = BugCore.game.Advisors

# lfgr 10/2019: Sevopedia is full-screen in Main menu
if not AdvisorOpt._hasOption("FullScreenAdvisors"):
	BugUtil.debug("BUG: creating stub FullScreenAdvisors option")
	fullScreenOption = BugOptions.UnsavedOption(AdvisorOpt, BugOptions.qualify(AdvisorOpt._getID(), "FullScreenAdvisors"), "boolean", True)
	fullScreenOption.createGetter()
	AdvisorOpt._addOption(fullScreenOption)

if not AdvisorOpt._hasOption("Sevopedia"):
	BugUtil.debug("BUG: creating stub Sevopedia option")
	enabledOption = BugOptions.UnsavedOption(AdvisorOpt, BugOptions.qualify(AdvisorOpt._getID(), "Sevopedia"), "boolean", True)
	AdvisorOpt._addOption(enabledOption)

if not AdvisorOpt._hasOption("SevopediaSortItemList"):
	BugUtil.debug("BUG: creating stub Sevopedia Sort option")
	sortOption = BugOptions.UnsavedOption(AdvisorOpt, BugOptions.qualify(AdvisorOpt._getID(), "SevopediaSortItemList"), "boolean", True)
	AdvisorOpt._addOption(sortOption)
