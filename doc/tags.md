# New XML tags

This document contains an overview of new and changed XML tags in MNAI-U. It includes new and changed tags in Fall from Heaven 2 and MNAI that are still present in MNAI-U, as well as some BtS tags. It is still work in progress. For other BtS tags, see e.g. civfantics' [modiki](http://modiki.civfanatics.com/index.php?title=Civ4_XML_Reference).

### Gameinfo/CIV4VoteInfo.xml

Contains resolutions that can be passed by the Organizations (VoteSources) defined in Gameinfo/CIV4VoteSourceInfo.xml.

"This resolution" always refers to the resolution containing the tag. "Member" refers to members of the VoteSource where the resolution was passed.

**New tags**

Tag(s)  | Description | History
--- | --- | ---
`<PopulationThreshold>P</PopulationThreshold>` | To pass, this resolution requires P percent of all members (rounded up) to vote in favor. If there is a tie in a vote with P=50, the choice of the head councilor is implemented. (In BtS, the number of required votes is rounded down.) | Changed in MNAI ("Improved Councils")
`<bCityVoting>1</bCityVoting>` | 1 vote per city (with respective religion, if specified). | From BtS
`<bCivVoting>1</bCivVoting>` | 1 vote per member (that has a city with the respective religion, if specified). Takes precendence over `<bCityVoting>`. If neither is specified, 1 vote per population (in cities with respective religion). TODO: Don't allow both | From BtS
`<iMinVoters>N</iMinVoters>` | Requires at least N voting members | From BtS
`<iStateReligionVotePercent>P</iStateReligionVotePercent>` | Players with correct state religion have P percent more votes (rounded down) | From BtS
`<iTradeRoutes>N</iTradeRoutes>` | N additional trade routes for all players (not only members!) <br/> AI players vote for this resolution if they are friendly to the secretary general (BBAI) or if they don't have many more cities than the average. | Changed in MNAI via BBAI and Advanced Diplomacy 2
`<bSecretaryGeneral>1</bSecretaryGeneral>` | Vote for the secretary general. Implies team voting. | From BtS
`<bVictory>1</bVictory>` | All players must be voting members. Makes a player win a diplomatic victory. Implies team voting. | From BtS
`<bFreeTrade>1</bFreeTrade>` | TODO | TODO
`<bNoNukes>1</bNoNukes>` | Forbids creating nukes or buildings/projects that allow nukes. AI calculation is fairly complicated. | From BtS
`<bDefensivePact>1</bDefensivePact>` | All members sign a defensive pact with each other. Only available if at least one defensive pact can be signed that way. | From BtS
`<bOpenBorders>1</bOpenBorders>` | All members sign open borders agreement with each other. Only available if at least one open borders agreement can be signed that way. | From BtS
`<bForcePeace>1</bForcePeace>` | A member is chosen for the resolution that is at war with some other member. All other members sign a peace treaty with that member. | From BtS
`<bForceNoTrade>1</bForceNoTrade>` | A non-member player is chosen for the resolution. All members cancel all deals with that player. | From BtS
`<bForceWar>1</bForceWar>` | A non-member player is chosen for the resolution. All members declare war on that player. Can only be passed if some member is at war with the chosen non-member, but not all members are. | From BtS
`<bAssignCity>1</bAssignCity>` | TODO; Cannot be combined with another tag that chooses a player. | From BtS
`<ForceCivics>` | All members have to use the specified civics. (In BtS, all players have to use them.) | Changed in FfH2
`<DiploVotes>` | TODO | TODO
`<bNoOutsideTechTrades>1</bNoOutsideTechTrades>` | Members cannot trade with non-members. | Added in FfH2
`<iCost>N</iCost>` <br/> `<iFreeUnits>M</iFreeUnits>` <br/> `<FreeUnitClass>UNIT_SOMETHING</FreeUnitClass>` | When this resolution is passed, each member who has a capital and at least N gold pays N gold and receives M units of type `UNIT_SOMETHING` in their capital. | Added in FfH2
`<iCrime>Z</iCrime>` | Changes the global crime by Z (added to the crime of all cities). | Added in FfH2
`<NoBonus>BONUS_SOMETHING</NoBonus>` | Disables access to `BONUS_SOMETHING` for all members. | Added in FfH2
`<PyResult>something()</PyResult>` | Python code to be executed (in `CvSpellInterface.py`) when this resolution is passed. | Added in FfH2
`<bTradeMap>1</bTradeMap>` | When passed, all members share their maps immediately. This resolution can be passed repeatedly. AI players only vote for this resolution if they would be willing (in principle) to trade maps with all other members. | Added in MNAI via Advanced Diplomacy 2
`<bNoCityRazing>1</bNoCityRazing>` | Members don't auto-raze cities. **TODO: Members shouldn't be able to raze cities!** AI players might defy this resolution if they think they'll want to raze a lot in the future. | Added in MNAI via Advanced Diplomacy 2
`<bCultureNeedsEmptyRadius>1</bCultureNeedsEmptyRadius>` | Cities of members don't spread culture to plots that are owned by other players that do the same (due to this or some other resolution). | Added in MNAI via Advanced Diplomacy 2
`<bPacificRule>1</bPacificRule>` | **TODO: Doesn't seem to do anything** | Added in MNAI via Advanced Diplomacy 2

**Removed tags**

Tag(s)  | Description | History
--- | --- | ---
`<bGamblingRing>1</bGamblingRing>` | Makes Gambling Houses 25% cheaper to build for members (this effect is defined in python). Neutral AI players will vote against this resolution. | Added in FfH2. Removed in MNAI-U (moved to python).
`<bSmugglingRing>1</bSmugglingRing>` | Allows members to construct a smuggler's port. <br/> AI players with less than 3 coastal cities will vote against this resolution. | Added in FfH2. Removed in MNAI-U (moved to python).
`<bSlaveTrade>1</bSlaveTrade>` | Allows member's units to cast spells with `<bPrereqSlaveTrade>1</bPrereqSlaveTrade>`. Neutral AI players will vote against this resolution. | Added in FfH2. Removed in MNAI-U (using SpellInfos `<VotePrereq>`).


Sources:

* Kael's [Modder's guide to FfH2](https://forums.civfanatics.com/threads/modders-guide-to-ffh2.238077/)
* Tholal's [Mod-modder's guide to MNAI](https://forums.civfanatics.com/threads/1st-draft-mod-modders-guide-to-mnai.519768/)
* The civfanatics modiki [XML Reference](http://modiki.civfanatics.com/index.php?title=Civ4_XML_Reference)

