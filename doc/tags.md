# New XML tags

This document contains an overview of new and changed XML tags in MNAI-U. It includes new and changed tags in Fall from Heaven 2 and MNAI that are still present in MNAI-U. It is still work in progress. For BtS tags, see e.g. civfantics' [modiki](http://modiki.civfanatics.com/index.php?title=Civ4_XML_Reference).

### Gameinfo/CIV4VoteInfo.xml

Contains resolutions that can be passed by the Organizations (VoteSources) defined in Gameinfo/CIV4VoteSourceInfo.xml.

"This resolution" always refers to the resolution containing the tag. "Member" refers to members of the VoteSource where the resolution was passed.

**New tags**

Tag(s)  | Description | History
--- | --- | ---
`<PopulationThreshold>P</PopulationThreshold>` | To pass, this resolution requires P percent of all members (rounded up) to vote in favor. If there is a tie in a vote with P=50, the choice of the head councilor is implemented. (In BtS, the number of required votes is rounded down.) | Changed in MNAI ("Improved Councils")
`<ForceCivics>` | All members have to use the specified civics. (In BtS, all players have to use them.) | Changed in FfH2
`<bGamblingRing>1</bGamblingRing>` | Makes Gambling Houses 25% cheaper to build for members (this effect is defined in python). Neutral AI players will vote against this resolution. | Added in FfH2
`<bNoOutsideTechTrades>1</bNoOutsideTechTrades>` | Members cannot trade with non-members. | Added in FfH2
`<bSlaveTrade>1</bSlaveTrade>` | Allows member's units to cast spells with `<bPrereqSlaveTrade>1</bPrereqSlaveTrade>`. Neutral AI players will vote against this resolution. | Added in FfH2
`<bSmugglingRing>1</bSmugglingRing>` | Allows members to construct a smuggler's port. <br/> AI players with less than 3 coastal cities will vote against this resolution. | Added in FfH2
`<iCost>N</iCost>` <br/> `<iFreeUnits>M</iFreeUnits>` <br/> `<FreeUnitClass>UNIT_SOMETHING</FreeUnitClass>` | When this resolution is passed, each member who has a capital and at least N gold pays N gold and receives M units of type `UNIT_SOMETHING` in their capital. | Added in FfH2
`<iCrime>Z</iCrime>` | Changes the global crime by Z (added to the crime of all cities). | Added in FfH2
`<NoBonus>BONUS_SOMETHING</NoBonus>` | Disables access to `BONUS_SOMETHING` for all members. | Added in FfH2
`<PyResult>something()</PyResult>` | Python code to be executed (in `CvSpellInterface.py`) when this resolution is passed. | Added in FfH2
`<bTradeMap>1</bTradeMap>` | When passed, all members share their maps immediately. This resolution can be passed repeatedly. AI players only vote for this resolution if they would be willing (in principle) to trade maps with all other members. | Added in MNAI via Advanced Diplomacy 2
`<bNoCityRazing>1</bNoCityRazing>` | Members don't auto-raze cities. **TODO: Members shouldn't be able to raze cities!** AI players might defy this resolution if they think they'll want to raze a lot in the future. | Added in MNAI via Advanced Diplomacy 2
`<bCultureNeedsEmptyRadius>1</bCultureNeedsEmptyRadius>` | Cities of members don't spread culture to plots that are owned by other players that do the same (due to this or some other resolution). | Added in MNAI via Advanced Diplomacy 2
`<bPacificRule>1</bPacificRule>` | **TODO: Doesn't seem to do anything** | Added in MNAI via Advanced Diplomacy 2


Sources:

* Kael's [Modder's guide to FfH2](https://forums.civfanatics.com/threads/modders-guide-to-ffh2.238077/)
* Tholal's [Mod-modder's guide to MNAI](https://forums.civfanatics.com/threads/1st-draft-mod-modders-guide-to-mnai.519768/)
* The civfanatics modiki [XML Reference](http://modiki.civfanatics.com/index.php?title=Civ4_XML_Reference)
