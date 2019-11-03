# Changelog

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
	* Minimal - Always use default name, except when two civililzations of the same type exist (in that case, use "Realm of <leader>")
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
