# Changelog

## v2.9-beta2u

### UI
* (Most) advisors are now able to adapt to a screen height of 720 (report by Tielby@civfanatics)
* Flag tooltip now shows whether the game is played with an assert/debug build
* Player defeat popups can now be disabled via BUG options
* Show promotion min level in help (report by MagisterCultuum@civfanatics)
* Some small text fixes
* Religion advisor can be made full-screen again

### Bugfixes
* Scenarios now work with the new mod name.
* Cannot found on foundDisabled plots, even in advanced start. (report by MagisterCultuum@civfanatics)
* Advanced combat odds now display correct combat odds for units with special combat types (report by MagisterCultuum@civfanatics)
* Corrected refund when removing a unit with InstanceCostModifier in advanced start (report by MagisterCultuum@civfanatics)
* Can only cast regeneration when a damaged unit is in stack
* Fixed array underflow when closing the game (thanks to DuskTreader@civfanatics)
* Make Minister Koun properly update his area strategies when he spawns
* Upgrades cannot yield gold, even with total iUpgradeDiscount greater than 100% (report by MagisterCultuum@civfanatics)
* Building `<ReligionChange>` applies religion in worldbuilder/advanced start, too (report by MagisterCultuum@civfanatics)

### AI
* AI is now less eager to build super forts in unowned territory
* Some tweaks to make the AI better at guarding forts (report by Dominus the Mentat@civfanatics)
* Tweaks to make the AI less likely to build forts in the city radius
* AI tries to not leave it's city undefended if it has only one city (report by Dominus the Mentat@civfanatics)

### Code
* More logging, especially for AI, but release build log less
* Added custom makefile
* Small improvements to PyHelpers


## v2.9-beta1u

Breaks savegames.

### Gameplay
* The "sell slave" spell (which was previously not available due to a bug) can only be cast in cities
* Fund dissidents resolution can now only be chosen if it actually does something
* Removed broken and/or unfitting resolutions, cleaned up the rest

### UI
* "100% chance of wearing off each turn" now reads "Wears off at the end of turn"
* Adjusted size of unit model for currently selected unit so it doesn't overlap with the tooltip
* Lanun adept now uses default adept button instead of lanun warrior button (report by swapoer@civfanatics.com)
* Vote help text now avaiable as a tooltip in victory advisor and resolution choice and voting dialogs
* Improved popup text and messages regarding voting
* Spell costs you cannot pay are now indicated in red
* Removed irritating "unit defeated" sound when great generals die (report by Bickendan@civfanatics.com)
* If own nationality is lower than 50% in a city, show turns until 50% is achieved
* Adjusted player colors such that rebels (and Minister Koun) get new ones (report by Devils_Advocate@civfanatics.com)

### Bugfixes
* Spells whose only positive effect is gaining gold can now be casted (this was preventing "Sell Slave" to work)
* Repealing a resolution now correctly undoes its effect on crime rate
* Fixed an encoding problem with Dynamic Civ Names
* Fixed an invalid memory access occuring in the AI cache
* Fixed an invalid memory access when having the mouse over an unowned town improvement
* Fixed a typo in the lair exploration code

### Code
* `<bGamblingRing>`, `<bSmugglingRing>`, and `<bSlaveTrade>` VoteInfo tag removed (superseded)
* `<bCityRazing>` and `<bPacificRule>` VoteInfo tags removed (didn't work and not fitting for FfH)
* `<bPrereqSlaveTrade>` SpellInfo tag removed
* New SpellInfo tag: `<VotePrereq>`
* New VoteInfo tags: `<PyRequirement>`, `<PyAI>`. See doc/tags.md for more information
* Enabled VoteInfo `<Help>` tag in Schema
* gambling ring, smuggling ring, and slave trade resolutions now use python and the new tags
* More documentation for Vote system
* Misc formatting, cleanup, and comments.
* Removed an invalid assert complaining about the world building limit - this is expected to be too high if we e.g. pick up and drop crown of Akharien.

### Misc
* The mod folder is now "More Naval AI", it should no longer installed over vanilla FfH.


## v2.8.1u

### Gameplay
* Strong lair bosses now require that barbarians have certain technologies
* Mistform event now requires Sorcery
* Barbarian Spectres can no longer upgrade to wraiths before barbarians have Sorcery
* Stasis now disables production decay (idea by Devils_Advocate@civfanatics)

### UI
* Spell help and pedia now shows all gameplay-relevant information
* Technology, civic, finance, military, and victory screen as well as the sevopedia can now be set to fullscreen in BUG options
* Improved victory screen
* Rearranged Advisor tab in BUG options, removed espionage options
* Now shows a message when a unit is killed due to not being able to withdraw
* Trade route yield modifiers from Civics and Traits are now displayed correctly (report by westamastaflash@civfanatics)
* Overhauled dynamic civ names. There are now three flavors of DNC that can be chosen in the "Scoreboard" tab of the BUG options window, along with other options:
	* Off - Always use default name
	* Minimal - Always use default name, except when two civililzations of the same type exist (in that case, use "Realm of [leader]")
	* Medium - Similar to Minimal, but with a limited number of additional names based on civ, civics etc.
	* High - Tholal's original DNC variant

### Bugfixes
* Pillaging cannot remove plot ownership anymore
* Blizzards no longer deal damage to winterborn units on creation (report by Devils_Advocate@civfanatics)
* Fixed not being able to change all but government civics if Liberty is enforced by overcouncil (report by westamastaflash@civfanatics)
* Barbarian cities are no longer founded on foundDisabled tiles (report by MagisterCultuum@civfanatics)
* BUG's "actual" building effects now considers unhappy production (governor's manor, pillar of chains)
* Fixes crash when a ship is captured by another ship with boarding, the latter of which appear in MagisterModMod (report by OKSleeper@civfanatics)
* BUG production decay calculation (for UI) was off in some cases
* Fixed rare crash when a unit loses the Hidden promotion after combat, thus becomes visible, then tries to flee as there are enemy units on the same plot, cannot flee, and is therefore killed. The game continues to do stuff with the killed unit, which lead to the crash. (report by westamastaflash@civfanatics)

### Code
* Allow Buildings to have empty `<MovieDefineTag>` (previously, only `NONE` was allowed) - Fixes Assertion in MagisterModMod
* Exposed all relevant CvSpellInfo functions
* Added `bCreation` parameter to `CvUnit::setXY()` and feature onMove callback, indicating whether the unit was just created on that tile (see Notes for Modders)
* Added `combatDefenderRetreat` BUG event
* Added `<iMiscastChance>` to PromotionInfo, tweaked miscast help and messages
* Added `<PythonInfoHelp>` tag to UnitInfo - This may be used to display help text for UnitInfos (as opposed to actual units), for example in the civilopedia and in the city screen. The tag must contain a single python statement (usually a function call) that may use the following parameters: `eUnit, bCivilopediaText, bStrategyText, bTechChooserText, pCity`. The code is executed in python/entrypoints/CvSpellInterface.py, like the spell help.
* Whenever a unit is killed, a message with the cause is logged
* Replaced the earlier item duplication fix with a different one that hopefully causes less problems
* Caching parts of AI_unitValue that only depend on InfoTypes for better performance
* Removed the unused files RebelTypes.py and LeaderCivNames.py and references to them
* Fixed BugUtil swallowing Exceptions and printing misleading messages when loading modules
* Some code tweaks/cleanup, fixed some minor bugs

### Notes for modders
* `onMoveFeature()` in CvSpellInterface.py now receives the additional parameter bCreation that indicates whether the unit was just created (on the respective plot). You have to merge the change in CvSpellInterface, and you can then use the bCreation variable in FeatureInfo's `<PythonOnMove>`.
* I started adding some documentation in the doc folder. Currently, the FfH-specific VoteInfo tags are documented, but I plan to add more in the future (depending what I work on). The documentation is formatted with markdown. The rendered result can be viewed e.g. on [bitbucket](https://bitbucket.org/lfgr/more-naval-ai/src/default/doc/tags.md) (although it doesn't render everything correctly, it is still well readable).
