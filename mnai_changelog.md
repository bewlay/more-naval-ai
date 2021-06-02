# Changelog

## 2.9u

### Gameplay
* Allow Illians to build workshops on snow
* Automating terraformers now works and automated terraformers no longer cast random spells
* Reduced frequency of Clairone (Harpy) event by 75% (report by Set@civfanatics)
* Inquisition no longer removes wonders (report by kvaak@civfanatics)

### UI
* Customizable Domestic Advisor can now load and save settings, tooltips now work
* Improved terraforming spell tooltips
* Better Feast help text
* Spell help now shows details of added promotions, summoned units and created buildings (Can be disabled via BUG option)
* Document bAutoraze (war machine + four horsemen) in unit info help
* Don't show any of the OR-required boni of a unit if we already have one of them
* Show required projects in project pedia
* Show civ-specific projects, civics, spells, and terrain yield modifiers in pedia (report by Alekseyev_@civfanatics)
* Add trait buttons for pedia (Terkhen@civfanatics)
* Show default race and traits in civ pedia
* Dark Elf promotion now shows up in the pedia
* Unified format of english civ pedia texts
* Re-add shortcuts concept section (From AdvCiv; the actual shortcuts are not tested)
* Added Decius pedia entry (by Nikis-Knight@civfanatics)
* Added pedia entries for Duke Sallos, Meresin, and Ouzza (by Kael@reddit)
* Fixed BUG display of GP-discoverable technologies in tech chooser
* Negative research is now correctly displayed as 0 research in city screen
* Khazad vault status now is a tooltip of the gold/income text; default behavior can be restored by a BUG option
* Technology buttons no longer overlap GP bar
* Allow changing Handicap via worldbuilder (report by Qgqqqqq@realmsbeyond)
* Allow changing player color via worldbuilder (requires some time to update; report by Qgqqqqq@realmsbeyond)
* Don't try to show dead teams as worst enemies on the scoreboard
* Never show "-1 hammers" in unit help
* Outdated loading screen hint (Deaf Metal@civfanatics)
* Show number of cities and power ratio in scoreboard (report by Deaf Metal@civfanatics)
* Some text fixes and translations

### Bugfixes
* BarbarianAllies now get combat odds when attacking animals
* Don't show an empty line if PySpellHelp returns an empty string
* Some text encoding fixes
* Fixed an invalid usage of getSorenRandNum in BBAI code
* Vassals can no longer have non-agression pacts
* Fixed two instanecs of AI confusion related to pillaging (Thanks to DuskTreader@civfanatics)
* Feast spell can no longer be cast if it would give 0 XP
* Division by zero in Autolog mod
* Python bug when trying to switch civ and leader with ChangePlayer
* PlotHelpNumUnits BUG option is now properly saved
* Fixed a problem with DCN vassal naming

### AI
* Improved terraforming AI
* Stop patrol units piling up on forts (report by kvaak@civfanatics)
* Pillaging with hidden nationality units no longer changes the AI's subjective war success (report by Akbarthegreat@civfanatics)
* More robust summoner/buffer/debuffer recognition (AI used to think that all mages are summoners, since it didn't realize that Summon Sand Lion is a Malakim-only spell)
* Summoners no longer prefer promotions with CombatPercent, e.g. Combat I-V (Combat I-V granting Empower I-V is still considered)

### Code
* PySpellHelp now replaces static spell <Help> if the former is non-empty
* Enable BugGameUtils and make it fall back to CvGameUtils
* Refactored CvCustomizableDomesticAdvisor, allow specificing row tooltips
* Fixed profile build
* Throw assert if number out of unsigned short range is passed to getSorenRandNum (Sezren@civfanatics)
* Allow omitting language tags in text XML files (falls back to English)
* Remove all translated texts that are identical to the English text
* Better logging and logging control
* Fixed or disabled some asserts
* Revolution refactoring

### Revolutions
* Added Revolution page to Customizable Domestic Advisor
* Local RevIdx changes:
	* Removed effects of hardcoded "Nationalism", "Liberalism" and "Scientific Method" techs.
	* Instability from nationality no longer reduces the garrison RevIdx cap
	* Removed small capital malus in later eras ("To help remove late game tiny civs" -- we don't want that)
	* Removed malus for small cities that used to be large
	* Streamlined small city bonus
	* No unhappiness malus in city with disorder.
	* Removed colony malus, "revolutionary spirit"
	* Current era no longer subtracted from culture rate
	* Removed malus from negative food per turn
	* Simplified and streamlined unhealthiness, nationality, health and garrison indices
	* No increased civic malus if "better" civics are available
	* Building effects not disabled from wrong PrereqCiv or PrereqTrait
	* Slightly changed combination of final general and human modifiers (does nothing by default)
	* Slightly changed the religion bonus when at war
	* Slightly changed the unhappiness malus, now uses the new DLL method CyCity.unhappyLevelForRevIdx()
	* Route bonus in location RevIdx now considers all technology changes to the city's actual route
	* Location rev idx incorporates civ size more smoothly
	* Civic/Building location rev idx boni now do what they seem
	* Location rev idx calculates distance from nearest gov. center, not only capital
	* Location rev idx can't be negative (a good comm bonus otherwise makes the bonus worse)
* National RevIdx changes:
	* Removed distinction between RevIdx and Stability. The latter was almost, but not quite, the negation of the former. Stability seemed to have no effect other than for display purposes. Now Stability = -RevIdx.
	* Streamlined small empire bonus and apply it to RevIdx (not just stability)
	* Culture spending is now actually added to the national RevIdx
	* Removed wonky "financial trouble" factor.
	* No increased civic malus if "better" civics are available
	* Civics now added to national RevIdx (instead of only "stability")
	* Building effects not disabled from wrong PrereqCiv or PrereqTrait
	* Removed late-game penalty for players with large military
	* Removed (only partly working) anarchy penalty of 100 (40 for rebels)
	* Slightly changed combination of final general and human modifiers (does nothing by default)


## v2.9-beta3u

Breaks savegames.

### Gameplay
* Embassies no longer allow players to see into other capitals
* Consider actual unit religion instead of UnitInfo religion when checking whether upgrades to religious units are valid. This means that e.g. Assassins with a non-CoE religion cannot upgrade to Shadow (Assassins without religion still can).
* Men o' War can now carry one bird, like Frigates (Report by King Bulrush@civfanatics)
* Lumbermill can now be constructed on ancient forests

### UI
* Allow enabling/disabling avoid angry/unhealthy citizens in new cities via BUG Option
* Allow cycling through foreign units on a single plot -- Allows access to unit details for all foreign units on plots with no unit belonging to the active player. Before, details where inaccessible if too many units were on the plot. Cycle while hovering over a plot with Ctrl-Space (forwards) and Ctrl-Shift-Space (backwards).
* BUG option to control how many individual units are shown in plot help
* Improve display of unit upgrades and building-enabled units in pedia, based on active player (report by Vintage Strategist@civfanatics)
* Hide units from the upgrade chart that are unavailable to active player because of PrereqCiv
* Added Advanced diplomacy concept page
* Show UnitInfo religion (e.g., in build queue tooltip and in pedia)
* Civic buttons in tech tree now have a more informative tooltip
* Fix some invalid upgrades that were shown in unit upgrade graph
* Unit upgrade graph uses buttons with corret artstyle
* Small improvements to the defensive fear mechanic: After scared out of attacking, units that are unable to attack again are removed from selection, and the "unit afraid" message is shown immediately after trying to attack
* Some text fixes for spanish

### Bugfixes
* Regenerating the map resets world wonder counts and allows re-founding of religions (report by MagisterCultuum@civfanatics)
* Avatar of Wrath event no longer enrages workers (report by kvaak@civfanatics)
* Fixed a frequent error when exploring a lair had one of the outcomes "Depths", "Dwarf vs. Lizardmen" or "Portal".
* Real (non-temporary) terrain type now saved correctly by WB (code by MagisterCultuum@civfanatics)
* Fixed a possible zero division error
* Fixed GFC Error when "Fall from Heaven 2" folder is not present (thanks omegaflames@civfanatics)
* Fixed invalid memory access when earthquake spell is checked on unowned plot
* Immortal units now properly abandon you or expire from limited duration (report by MagisterCultuum@cf)
* Crash when ejecting unit because it loses an invisibility promotion (report by Bickendan@cf)
* Defensive fear mechanic now works again (thanks Azhral@cf)

### AI
* Fixed a bug causing the AI to miscalculate mana value
* Scaled back AI valuation of mana when (momentarily) going for a tower victory (Report by Sezren@civfanatics)
* Removed erroneous base valuation of resources, even of those with no benefit. In particular, Hyborem will not assign any value to health resources.

### Code
* Removed trivial assertion errors in PerfectWorld2.py and Totestra.py
* Debug build now logs as intended
* More AI deal logging
* Some Advanced Diplomacy documentation
* Added 40 dummy gameoption for mod use

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
