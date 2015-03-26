// selectionGroupAI.cpp

#include "CvGameCoreDLL.h"
#include "CvSelectionGroupAI.h"
#include "CvPlayerAI.h"
#include "CvMap.h"
#include "CvPlot.h"
#include "CvTeamAI.h"
#include "CvDLLEntityIFaceBase.h"
#include "CvGameCoreUtils.h"
#include "FProfiler.h"
#include "CVInfos.h"

// Logging
#include "BetterBTSAI.h"
// Public Functions...

CvSelectionGroupAI::CvSelectionGroupAI()
{
	AI_reset();
}


CvSelectionGroupAI::~CvSelectionGroupAI()
{
	AI_uninit();
}


void CvSelectionGroupAI::AI_init()
{
	AI_reset();

	//--------------------------------
	// Init other game data
}


void CvSelectionGroupAI::AI_uninit()
{
}


void CvSelectionGroupAI::AI_reset()
{
	AI_uninit();

	m_iMissionAIX = INVALID_PLOT_COORD;
	m_iMissionAIY = INVALID_PLOT_COORD;

	m_bForceSeparate = false;

	m_eMissionAIType = NO_MISSIONAI;

	m_missionAIUnit.reset();

	m_bGroupAttack = false;
	m_iGroupAttackX = -1;
	m_iGroupAttackY = -1;
}

// these separate function have been tweaked by K-Mod and bbai.
void CvSelectionGroupAI::AI_separate()
{
	CLLNode<IDInfo>* pEntityNode;
	CvUnit* pLoopUnit;

	pEntityNode = headUnitNode();

	while (pEntityNode != NULL)
	{
		pLoopUnit = ::getUnit(pEntityNode->m_data);
		pEntityNode = nextUnitNode(pEntityNode);

		pLoopUnit->joinGroup(NULL);
	}
}

void CvSelectionGroupAI::AI_separateNonAI(UnitAITypes eUnitAI)
{
	CLLNode<IDInfo>* pEntityNode;
	CvUnit* pLoopUnit;

	pEntityNode = headUnitNode();

	while (pEntityNode != NULL)
	{
		pLoopUnit = ::getUnit(pEntityNode->m_data);
		pEntityNode = nextUnitNode(pEntityNode);
		if (pLoopUnit->AI_getUnitAIType() != eUnitAI)
		{
			pLoopUnit->joinGroup(NULL);
		}
	}
}

void CvSelectionGroupAI::AI_separateAI(UnitAITypes eUnitAI)
{
	CLLNode<IDInfo>* pEntityNode;
	CvUnit* pLoopUnit;

	pEntityNode = headUnitNode();

	while (pEntityNode != NULL)
	{
		pLoopUnit = ::getUnit(pEntityNode->m_data);
		pEntityNode = nextUnitNode(pEntityNode);
		if (pLoopUnit->AI_getUnitAIType() == eUnitAI)
		{
			pLoopUnit->joinGroup(NULL);
		}
	}
}

bool CvSelectionGroupAI::AI_separateImpassable()
{
	CvPlayerAI& kPlayer = GET_PLAYER(getOwner());
	bool bSeparated = false;

	CLLNode<IDInfo>* pEntityNode = headUnitNode();

	while (pEntityNode != NULL)
	{
		CvUnit* pLoopUnit = ::getUnit(pEntityNode->m_data);
		pEntityNode = nextUnitNode(pEntityNode);
		if (kPlayer.AI_unitImpassableCount(pLoopUnit->getUnitType()) > 0)
		{
			pLoopUnit->joinGroup(NULL);
			bSeparated = true;
		}
	}
	return bSeparated;
}

bool CvSelectionGroupAI::AI_separateEmptyTransports()
{
	bool bSeparated = false;

	CLLNode<IDInfo>* pEntityNode = headUnitNode();

	while (pEntityNode != NULL)
	{
		CvUnit* pLoopUnit = ::getUnit(pEntityNode->m_data);
		pEntityNode = nextUnitNode(pEntityNode);
		if ((pLoopUnit->AI_getUnitAIType() == UNITAI_ASSAULT_SEA) && (pLoopUnit->getCargo() == 0))
		{
			pLoopUnit->joinGroup(NULL);
			bSeparated = true;
		}
	}
	return bSeparated;
}
// bbai / K-Mod


// Returns true if the group has become busy...
bool CvSelectionGroupAI::AI_update()
{
	CLLNode<IDInfo>* pEntityNode;
	CvUnit* pLoopUnit;
	bool bDead;
	bool bFollow;

	PROFILE("CvSelectionGroupAI::AI_update");

	FAssert(getOwnerINLINE() != NO_PLAYER);

//FfH: Modified by Kael 12/28/2008
//	if (!AI_isControlled())
	if (!AI_isControlled() && !isAIControl())
//FfH: End Modify

	{
		return false;
	}

	if (getNumUnits() == 0)
	{
		return false;
	}

/************************************************************************************************/
/* BETTER_BTS_AI_MOD                      04/28/10                                jdog5000      */
/*                                                                                              */
/* Unit AI                                                                                      */
/************************************************************************************************/
	if( !(isHuman()) && !(getHeadUnit()->isCargo()) && getActivityType() == ACTIVITY_SLEEP ) // Note: Sleep includes fortification
	{
		setForceUpdate(true);
	}
/************************************************************************************************/
/* BETTER_BTS_AI_MOD                       END                                                  */
/************************************************************************************************/

	if (isForceUpdate())
	{
		clearMissionQueue(); // XXX ???
		setActivityType(ACTIVITY_AWAKE);
		setForceUpdate(false);

		// if we are in the middle of attacking with a stack, cancel it
		AI_cancelGroupAttack();
	}

	FAssert(!(GET_PLAYER(getOwnerINLINE()).isAutoMoves()));

	int iTempHack = 0; // XXX

	bDead = false;
	
	bool bFailedAlreadyFighting = false;
	while ((m_bGroupAttack && !bFailedAlreadyFighting) || readyToMove())
	{
		iTempHack++;
		if (iTempHack > 100)
		{
			CvUnit* pHeadUnit = getHeadUnit();
			CvPlot* pPlot = pHeadUnit->plot();
			if (NULL != pHeadUnit)
			{
				if( gUnitLogLevel >= 1 )
				{
					CvWString szTempString;
					getUnitAIString(szTempString, pHeadUnit->AI_getUnitAIType());
					logBBAI("Unit stuck in loop: %S(%S)[%d, %d] (%S - %d)\n", pHeadUnit->getName().GetCString(), GET_PLAYER(pHeadUnit->getOwnerINLINE()).getName(),
						pHeadUnit->getX_INLINE(), pHeadUnit->getY_INLINE(), szTempString.GetCString(), pHeadUnit->getID());
				}
				FAssert(false);
				pHeadUnit->finishMoves();
			}
			break;
		}

		// if we want to force the group to attack, force another attack
		if (m_bGroupAttack)
		{
			m_bGroupAttack = false;

			groupAttack(m_iGroupAttackX, m_iGroupAttackY, MOVE_DIRECT_ATTACK, bFailedAlreadyFighting);
		}
		// else pick AI action
		else
		{
			CvUnit* pHeadUnit = getHeadUnit();

			if (pHeadUnit == NULL || pHeadUnit->isDelayedDeath())
			{
				break;
			}

			resetPath();

			if (pHeadUnit->AI_update())
			{
				if (iTempHack == 99)
				{
					FAssertMsg(false, "unit about to be stuck in loop");
				}
				// AI_update returns true when we should abort the loop and wait until next slice
				break;
			}
		}

		if (doDelayedDeath())
		{
			bDead = true;
			break;
		}

		// if no longer group attacking, and force separate is true, then bail, decide what to do after group is split up
		// (UnitAI of head unit may have changed)
		if (!m_bGroupAttack && AI_isForceSeparate())
		{
			AI_separate();	// pointers could become invalid...
			return true;
		}
	}

	if (!bDead)
	{
		if (!isHuman())
		{
			bFollow = false;

			// if we not group attacking, then check for follow action
			if (!m_bGroupAttack)
			{
				pEntityNode = headUnitNode();

				while ((pEntityNode != NULL) && readyToMove(true))
				{
					pLoopUnit = ::getUnit(pEntityNode->m_data);
					pEntityNode = nextUnitNode(pEntityNode);

					if (pLoopUnit->canMove())
					{
						resetPath();

						if (pLoopUnit->AI_follow())
						{
							bFollow = true;
							break;
						}
					}
				}
			}

			if (doDelayedDeath())
			{
				bDead = true;
			}

			if (!bDead)
			{
				if (!bFollow && readyToMove(true))
				{
					pushMission(MISSION_SKIP);
				}
			}
		}
	}

	if (bDead)
	{
		//return true;
		return false; // K-Mod
	}

	return (isBusy() || isCargoBusy());
}


// Returns attack odds out of 100 (the higher, the better...)
int CvSelectionGroupAI::AI_attackOdds(const CvPlot* pPlot, bool bPotentialEnemy) const
{
	PROFILE_FUNC();

	CvUnit* pAttacker;

	FAssert(getOwnerINLINE() != NO_PLAYER);

	if (pPlot->getBestDefender(NO_PLAYER, getOwnerINLINE(), NULL, !bPotentialEnemy, bPotentialEnemy) == NULL)
	{
		return 100;
	}

	int iOdds = 0;
	pAttacker = AI_getBestGroupAttacker(pPlot, bPotentialEnemy, iOdds);

	if (pAttacker == NULL)
	{
		return 0;
	}

	return iOdds;
}


CvUnit* CvSelectionGroupAI::AI_getBestGroupAttacker(const CvPlot* pPlot, bool bPotentialEnemy, int& iUnitOdds, bool bForce, bool bNoBlitz) const
{
	PROFILE_FUNC();

	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pLoopUnit;
	CvUnit* pBestUnit;
	int iPossibleTargets;
	int iValue;
	int iBestValue;
	int iOdds;
	int iBestOdds;

	iBestValue = 0;
	iBestOdds = 0;
	pBestUnit = NULL;

	pUnitNode = headUnitNode();

	bool bIsHuman = (pUnitNode != NULL) ? GET_PLAYER(::getUnit(pUnitNode->m_data)->getOwnerINLINE()).isHuman() : true;

	while (pUnitNode != NULL)
	{
		pLoopUnit = ::getUnit(pUnitNode->m_data);
		pUnitNode = nextUnitNode(pUnitNode);

		if (!pLoopUnit->isDead())
		{
			bool bCanAttack = false;
			if (pLoopUnit->getDomainType() == DOMAIN_AIR)
			{
				bCanAttack = pLoopUnit->canAirAttack();
			}
			else
			{
				bCanAttack = pLoopUnit->canAttack();

				if (bCanAttack && bNoBlitz && pLoopUnit->isBlitz() && pLoopUnit->isMadeAttack())
				{
					bCanAttack = false;
				}
			}

			if (bCanAttack)
			{
				if (bForce || pLoopUnit->canMove())
				{
					if (bForce || pLoopUnit->canMoveInto(pPlot, /*bAttack*/ true, /*bDeclareWar*/ bPotentialEnemy))
					{
						iOdds = pLoopUnit->AI_attackOdds(pPlot, bPotentialEnemy);

						iValue = iOdds;
						int iLevel = pLoopUnit->getLevel();

						// Sephi AI - Block some Units from attacking at low odds)
                        if (!GET_PLAYER(pLoopUnit->getOwnerINLINE()).isHuman())
                        {
                            if (pLoopUnit->getUnitCombatType() == GC.getInfoTypeForString("UNITCOMBAT_ADEPT"))
                            {
                                if (iOdds < (95 + iLevel))
                                {
                                    iValue = 1;	//Need to put the min to 1 to prevent WoC (tholal note: true?)
                                }
                            }

                            if (pLoopUnit->AI_getUnitAIType() == UNITAI_HERO)
                            {
								if (iOdds < (85 + iLevel))
                                {
                                    iValue = 0;
                                }
                            }
							else if (iLevel > 4)
							{
								if (iOdds < (std::min(95, (70 + (iLevel * 3))))) //(tholal note: need better formula?)
								{
									iValue /= 2;
								}
							}
                        }

						iValue = std::max(1,iValue);
/*************************************************************************************************/
/**	END	                                        												**/
/*************************************************************************************************/
						FAssertMsg(iValue > -1, "iValue is expected to be greater than 0");

						if (pLoopUnit->collateralDamage() > 0)
						{
							iPossibleTargets = std::min((pPlot->getNumVisibleEnemyDefenders(pLoopUnit) - 1), pLoopUnit->collateralDamageMaxUnits());

							if (iPossibleTargets > 0)
							{
								iValue *= (100 + ((pLoopUnit->collateralDamage() * iPossibleTargets) / 5));
								iValue /= 100;
							}
						}

						// exploding units
						if (GC.getUnitInfo(pLoopUnit->getUnitType()).isExplodeInCombat())
						{
							iPossibleTargets = (pPlot->getNumVisibleEnemyDefenders(pLoopUnit) - 1);

							if (iPossibleTargets > 0)
							{
								iValue *= (100 + ((100 * iPossibleTargets) / 5));
								iValue /= 100;
							}
						}

						// if non-human, prefer the last unit that has the best value (so as to avoid splitting the group)
						if (iValue > iBestValue || (!bIsHuman && iValue > 0 && iValue == iBestValue))
						{
							iBestValue = iValue;
							iBestOdds = iOdds;
							pBestUnit = pLoopUnit;
						}
					}
				}
			}
		}
	}

	iUnitOdds = iBestOdds;
	return pBestUnit;
}

CvUnit* CvSelectionGroupAI::AI_getBestGroupSacrifice(const CvPlot* pPlot, bool bPotentialEnemy, bool bForce, bool bNoBlitz) const
{
	int iBestValue = 0;
	CvUnit* pBestUnit = NULL;

	CLLNode<IDInfo>* pUnitNode = headUnitNode();
	while (pUnitNode != NULL)
	{
		CvUnit* pLoopUnit = ::getUnit(pUnitNode->m_data);
		pUnitNode = nextUnitNode(pUnitNode);

		if (!pLoopUnit->isDead())
		{
			bool bCanAttack = false;
			if (pLoopUnit->getDomainType() == DOMAIN_AIR)
			{
				bCanAttack = pLoopUnit->canAirAttack();
			}
			else
			{
				bCanAttack = pLoopUnit->canAttack();

				if (bCanAttack && bNoBlitz && pLoopUnit->isBlitz() && pLoopUnit->isMadeAttack())
				{
					bCanAttack = false;
				}
			}

			if (bCanAttack)
			{
				if (bForce || pLoopUnit->canMove())
				{
					if (bForce || pLoopUnit->canMoveInto(pPlot, true))
					{
                        int iValue = pLoopUnit->AI_sacrificeValue(pPlot);
						//FAssertMsg(iValue > 0, "iValue is expected to be greater than 0");
/*************************************************************************************************/
/**	BETTER AI (Summons make good groupattack sacrifice units) Sephi              				**/
/*************************************************************************************************/
						if (pLoopUnit->getDuration()>0)
						{
						    iValue+=10000;
						}
/*************************************************************************************************/
/**	BETTER AI (Block some Units from attacking at low odds) Sephi              					**/
/*************************************************************************************************/
                        if (!GET_PLAYER(pLoopUnit->getOwnerINLINE()).isHuman())
                        {
                            if (pLoopUnit->AI_getUnitAIType() == UNITAI_WARWIZARD)
                            {
	                            iValue = 0;
                            }
                            else if (pLoopUnit->AI_getUnitAIType() == UNITAI_HERO)
                            {
	                            iValue = 0;
                            }
							else if (pLoopUnit->getLevel() > 4)
							{
	                            iValue = 1;
							}
                        }
/*************************************************************************************************/
/**	END	                                        												**/
/*************************************************************************************************/

						// we want to pick the last unit of highest value, so pick the last unit with a good value
						if ((iValue > 0) && (iValue >= iBestValue))
						{
							iBestValue = iValue;
							pBestUnit = pLoopUnit;
						}
					}
				}
			}
		}
	}

	return pBestUnit;
}

// Returns ratio of strengths of stacks times 100
// (so 100 is even ratio, numbers over 100 mean this group is more powerful than the stack on a plot)
int CvSelectionGroupAI::AI_compareStacks(const CvPlot* pPlot, bool bPotentialEnemy, bool bCheckCanAttack, bool bCheckCanMove) const
{
	FAssert(pPlot != NULL);

	int	compareRatio;
	DomainTypes eDomainType = getDomainType();

	// if not aircraft, then choose based on the plot, not the head unit (mainly for transport carried units)
	if (eDomainType != DOMAIN_AIR)
	{
		if (pPlot->isWater())
			eDomainType = DOMAIN_SEA;
		else
			eDomainType = DOMAIN_LAND;

	}

	compareRatio = AI_sumStrength(pPlot, eDomainType, bCheckCanAttack, bCheckCanMove);
	compareRatio *= 100;

	PlayerTypes eOwner = getOwnerINLINE();
	if (eOwner == NO_PLAYER)
	{
		eOwner = getHeadOwner();
	}
	FAssert(eOwner != NO_PLAYER);
	
/************************************************************************************************/
/* UNOFFICIAL_PATCH                       03/04/10                                jdog5000      */
/*                                                                                              */
/* Bugfix                                                                                       */
/************************************************************************************************/
/* original bts code
	int defenderSum = pPlot->AI_sumStrength(NO_PLAYER, getOwnerINLINE(), eDomainType, true, !bPotentialEnemy, bPotentialEnemy);
*/
	// Clearly meant to use eOwner here ...
	int defenderSum = pPlot->AI_sumStrength(NO_PLAYER, eOwner, eDomainType, true, !bPotentialEnemy, bPotentialEnemy);
/************************************************************************************************/
/* UNOFFICIAL_PATCH                        END                                                  */
/************************************************************************************************/
	compareRatio /= std::max(1, defenderSum);

	return compareRatio;
}

int CvSelectionGroupAI::AI_sumStrength(const CvPlot* pAttackedPlot, DomainTypes eDomainType, bool bCheckCanAttack, bool bCheckCanMove) const
{
	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pLoopUnit;
	int	strSum = 0;
	bool bDefenders = pAttackedPlot ? pAttackedPlot->isVisibleEnemyUnit(getHeadOwner()) : false; // K-Mod
	bool bCountCollateral = pAttackedPlot && pAttackedPlot != plot(); // K-Mod

	pUnitNode = headUnitNode();

	/*
	int iBaseCollateral = bCountCollateral
		? iBaseCollateral = estimateCollateralWeight(pAttackedPlot, pAttackedPlot->getTeam() == getTeam() ? NO_TEAM : pAttackedPlot->getTeam())
		: 0;
	*/

	while (pUnitNode != NULL)
	{
		pLoopUnit = ::getUnit(pUnitNode->m_data);
		pUnitNode = nextUnitNode(pUnitNode);

		if (!pLoopUnit->isDead())
		{
			// K-Mod. (original checks deleted.)
			if (bCheckCanAttack)
			{
				if (pLoopUnit->getDomainType() == DOMAIN_AIR)
				{
					if (!pLoopUnit->canAirAttack() || !pLoopUnit->canMove() || (pAttackedPlot && bDefenders && !pLoopUnit->canMoveInto(pAttackedPlot, true, true)))
						continue; // can't attack.
				}
				else
				{
					if (!pLoopUnit->canAttack() || !pLoopUnit->canMove()
						|| (pAttackedPlot && bDefenders && !pLoopUnit->canMoveInto(pAttackedPlot, true, true))
						|| (!pLoopUnit->isBlitz() && pLoopUnit->isMadeAttack()))
						continue; // can't attack.
				}
			}
			// K-Mod end

			if (eDomainType == NO_DOMAIN || pLoopUnit->getDomainType() == eDomainType)
			{
				strSum += pLoopUnit->currEffectiveStr(pAttackedPlot, pLoopUnit);
				// K-Mod estimate the attack power of collateral units. (cf with calculation in AI_localAttackStrength)
				if (bCountCollateral)
				{
					if (pLoopUnit->collateralDamage() > 0)
					{
						int iPossibleTargets = pLoopUnit->collateralDamageMaxUnits();
						// If !bCheckCanAttack, then lets not assume pAttackPlot won't get more units on it.
						if (bCheckCanAttack && pAttackedPlot->isVisible(getTeam(), false))
							iPossibleTargets = std::min(iPossibleTargets, pAttackedPlot->getNumVisibleEnemyDefenders(pLoopUnit) - 1);

						if (iPossibleTargets > 0)
						{
							// collateral damage is not trivial to calculate. This estimate is pretty rough.
							// (Note: collateralDamage() and iBaseCollateral both include factors of 100.)
							strSum += pLoopUnit->baseCombatStr() * pLoopUnit->collateralDamage() * iPossibleTargets / 1000;
						}
					}

					// Tholal Note: note - some units 'explode' but dont deal damage (do this properly with XML tags)
					/* - setting this up for future use when new tags implemented
					if (GC.getUnitInfo(pLoopUnit->getUnitType()).isExplodeInCombat())
					{
						strSum += (pAttackedPlot->getNumDefenders(pAttackedPlot->getOwner()) * 20);
					}
					*/
				}
				// K-Mod end
			}
		}
	}

	return strSum;
}

void CvSelectionGroupAI::AI_queueGroupAttack(int iX, int iY)
{
	m_bGroupAttack = true;

	m_iGroupAttackX = iX;
	m_iGroupAttackY = iY;
}

inline void CvSelectionGroupAI::AI_cancelGroupAttack()
{
	m_bGroupAttack = false;
}

inline bool CvSelectionGroupAI::AI_isGroupAttack()
{
	return m_bGroupAttack;
}

bool CvSelectionGroupAI::AI_isControlled()
{
	return (!isHuman() || isAutomated());
}


bool CvSelectionGroupAI::AI_isDeclareWar(const CvPlot* pPlot)
{
	FAssert(getHeadUnit() != NULL);

	if (isHuman())
	{
		return false;
	}
	else
	{
		bool bLimitedWar = false;
		if (pPlot != NULL)
		{
			TeamTypes ePlotTeam = pPlot->getTeam();
			if (ePlotTeam != NO_TEAM)
			{
				WarPlanTypes eWarplan = GET_TEAM(getTeam()).AI_getWarPlan(ePlotTeam);
				if (eWarplan == WARPLAN_LIMITED)
				{
					bLimitedWar = true;
				}
			}
		}

		CvUnit* pHeadUnit = getHeadUnit();

		if (pHeadUnit != NULL)
		{
			switch (pHeadUnit->AI_getUnitAIType())
			{
			case UNITAI_UNKNOWN:
			case UNITAI_ANIMAL:
			case UNITAI_SETTLE:
			case UNITAI_WORKER:
				break;
			case UNITAI_ATTACK_CITY:
			case UNITAI_ATTACK_CITY_LEMMING:
/*************************************************************************************************/
/**	BETTER AI (New UNITAI) Sephi                                 					            **/
/**																								**/
/**						                                            							**/
/*************************************************************************************************/
			case UNITAI_WARWIZARD:
            case UNITAI_HERO:
/*************************************************************************************************/
/**	END	                                        												**/
/*************************************************************************************************/
				return true;
				break;

			case UNITAI_ATTACK:
			case UNITAI_COLLATERAL:
			case UNITAI_PILLAGE:
				if (bLimitedWar)
				{
					return true;
				}
				break;

			case UNITAI_PARADROP:
			case UNITAI_RESERVE:
			case UNITAI_COUNTER:
			case UNITAI_CITY_DEFENSE:
			case UNITAI_CITY_COUNTER:
			case UNITAI_CITY_SPECIAL:
			case UNITAI_EXPLORE:
			case UNITAI_MISSIONARY:
			case UNITAI_PROPHET:
			case UNITAI_ARTIST:
			case UNITAI_SCIENTIST:
			case UNITAI_GENERAL:
			case UNITAI_MERCHANT:
			case UNITAI_ENGINEER:
			case UNITAI_SPY:
			case UNITAI_ICBM:
			case UNITAI_WORKER_SEA:
/*************************************************************************************************/
/**	BETTER AI (New UNITAI) Sephi                                 					            **/
/**																								**/
/**						                                            							**/
/*************************************************************************************************/
			case UNITAI_MAGE:
			case UNITAI_TERRAFORMER:
            case UNITAI_MANA_UPGRADE:
            case UNITAI_FEASTING:
            case UNITAI_MEDIC:
/*************************************************************************************************/
/**	END	                                        												**/
/*************************************************************************************************/
			case UNITAI_INQUISITOR:
			case UNITAI_LAIRGUARDIAN:
			case UNITAI_SHADE:
				break;

			case UNITAI_ATTACK_SEA:
			case UNITAI_RESERVE_SEA:
			case UNITAI_ESCORT_SEA:
				if (bLimitedWar)
				{
					return true;
				}
				break;
			case UNITAI_EXPLORE_SEA:
				break;

			case UNITAI_ASSAULT_SEA:
				if (hasCargo())
				{
					return true;
				}
				break;

			case UNITAI_SETTLER_SEA:
			case UNITAI_MISSIONARY_SEA:
			case UNITAI_SPY_SEA:
			case UNITAI_CARRIER_SEA:
			case UNITAI_MISSILE_CARRIER_SEA:
			case UNITAI_PIRATE_SEA:
			case UNITAI_ATTACK_AIR:
			case UNITAI_DEFENSE_AIR:
			case UNITAI_CARRIER_AIR:
			case UNITAI_MISSILE_AIR:
				break;

			default:
				FAssert(false);
				break;
			}
		}
	}

	return false;
}


CvPlot* CvSelectionGroupAI::AI_getMissionAIPlot()
{
	return GC.getMapINLINE().plotSorenINLINE(m_iMissionAIX, m_iMissionAIY);
}


bool CvSelectionGroupAI::AI_isForceSeparate()
{
	return m_bForceSeparate;
}


void CvSelectionGroupAI::AI_makeForceSeparate()
{
	m_bForceSeparate = true;
}


MissionAITypes CvSelectionGroupAI::AI_getMissionAIType()
{
	return m_eMissionAIType;
}


void CvSelectionGroupAI::AI_setMissionAI(MissionAITypes eNewMissionAI, CvPlot* pNewPlot, CvUnit* pNewUnit)
{
	//PROFILE_FUNC();

	m_eMissionAIType = eNewMissionAI;

	if (pNewPlot != NULL)
	{
		m_iMissionAIX = pNewPlot->getX_INLINE();
		m_iMissionAIY = pNewPlot->getY_INLINE();
	}
	else
	{
		m_iMissionAIX = INVALID_PLOT_COORD;
		m_iMissionAIY = INVALID_PLOT_COORD;
	}

	if (pNewUnit != NULL)
	{
		m_missionAIUnit = pNewUnit->getIDInfo();
	}
	else
	{
		m_missionAIUnit.reset();
	}
}


CvUnit* CvSelectionGroupAI::AI_getMissionAIUnit()
{
	return getUnit(m_missionAIUnit);
}

bool CvSelectionGroupAI::AI_isFull()
{
	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pLoopUnit;

	if (getNumUnits() > 0)
	{
		UnitAITypes eUnitAI = getHeadUnitAI();
		// do two passes, the first pass, we ignore units with speical cargo
		int iSpecialCargoCount = 0;
		int iCargoCount = 0;

		// first pass, count but ignore special cargo units
		pUnitNode = headUnitNode();

		while (pUnitNode != NULL)
		{
			pLoopUnit = ::getUnit(pUnitNode->m_data);
			pUnitNode = nextUnitNode(pUnitNode);
			if (pLoopUnit->AI_getUnitAIType() == eUnitAI)
			{
				if (pLoopUnit->cargoSpace() > 0)
				{
					iCargoCount++;
				}

				if (pLoopUnit->specialCargo() != NO_SPECIALUNIT)
				{
					iSpecialCargoCount++;
				}
				else if (!(pLoopUnit->isFull()))
				{
					return false;
				}
			}
		}

		// if every unit in the group has special cargo, then check those, otherwise, consider ourselves full
		if (iSpecialCargoCount >= iCargoCount)
		{
			pUnitNode = headUnitNode();
			while (pUnitNode != NULL)
			{
				pLoopUnit = ::getUnit(pUnitNode->m_data);
				pUnitNode = nextUnitNode(pUnitNode);

				if (pLoopUnit->AI_getUnitAIType() == eUnitAI)
				{
					if (!(pLoopUnit->isFull()))
					{
						return false;
					}
				}
			}
		}

		return true;
	}

	return false;
}


CvUnit* CvSelectionGroupAI::AI_ejectBestDefender(CvPlot* pDefendPlot)
{
	CLLNode<IDInfo>* pEntityNode;
	CvUnit* pLoopUnit;

	pEntityNode = headUnitNode();

	CvUnit* pBestUnit = NULL;
	int iBestUnitValue = 0;

	while (pEntityNode != NULL)
	{
		pLoopUnit = ::getUnit(pEntityNode->m_data);
		pEntityNode = nextUnitNode(pEntityNode);

		if (!pLoopUnit->noDefensiveBonus() && pLoopUnit->isUnitAllowedPermDefense())
		{
			int iValue = pLoopUnit->currEffectiveStr(pDefendPlot, NULL) * 100;

			if (pDefendPlot->isCity(true, getTeam()))
			{
				iValue *= 100 + pLoopUnit->cityDefenseModifier();
				iValue /= 100;
			}

			if (pDefendPlot->isHills())
			{
				iValue += pLoopUnit->hillsDefenseModifier();
			}

			int iCityAttackMod = pLoopUnit->cityAttackModifier();
			if (iCityAttackMod > 0)
			{
				iValue *= 100;
				iValue /= 100 + (iCityAttackMod * 2);
			}

			iValue /= 2 + (pLoopUnit->getLevel() * (pLoopUnit->AI_getUnitAIType() == UNITAI_ATTACK_CITY ? 2 : 1));

			if (iValue > iBestUnitValue)
			{
				iBestUnitValue = iValue;
				pBestUnit = pLoopUnit;
			}
		}
	}

	if (NULL != pBestUnit && getNumUnits() > 1)
	{
		pBestUnit->joinGroup(NULL);
	}

	return pBestUnit;
}


// Protected Functions...

void CvSelectionGroupAI::read(FDataStreamBase* pStream)
{
	CvSelectionGroup::read(pStream);

	uint uiFlag=0;
	pStream->Read(&uiFlag);	// flags for expansion

	pStream->Read(&m_iMissionAIX);
	pStream->Read(&m_iMissionAIY);

	pStream->Read(&m_bForceSeparate);

	pStream->Read((int*)&m_eMissionAIType);

	pStream->Read((int*)&m_missionAIUnit.eOwner);
	pStream->Read(&m_missionAIUnit.iID);

	pStream->Read(&m_bGroupAttack);
	pStream->Read(&m_iGroupAttackX);
	pStream->Read(&m_iGroupAttackY);
}


void CvSelectionGroupAI::write(FDataStreamBase* pStream)
{
	CvSelectionGroup::write(pStream);

	uint uiFlag=0;
	pStream->Write(uiFlag);		// flag for expansion

	pStream->Write(m_iMissionAIX);
	pStream->Write(m_iMissionAIY);

	pStream->Write(m_bForceSeparate);

	pStream->Write(m_eMissionAIType);

	pStream->Write(m_missionAIUnit.eOwner);
	pStream->Write(m_missionAIUnit.iID);

	pStream->Write(m_bGroupAttack);
	pStream->Write(m_iGroupAttackX);
	pStream->Write(m_iGroupAttackY);
}

// Private Functions...

/*************************************************************************************************/
/**	BETTER AI (New Functions) Sephi                                               				**/
/**																								**/
/**						                                            							**/
/*************************************************************************************************/
int CvSelectionGroupAI::AI_getGroupflag() const
{
	if(getHeadUnit()==NULL)
	{
		return GROUPFLAG_NONE;
	}
	else
	{
		return getHeadUnit()->AI_getGroupflag();
	}
}

void CvSelectionGroupAI::AI_setGroupflag(int newflag)
{
	CLLNode<IDInfo>* pUnitNode = headUnitNode();
    while (pUnitNode != NULL)
    {
        CvUnit* pLoopUnit = ::getUnit(pUnitNode->m_data);
        pUnitNode = nextUnitNode(pUnitNode);
        pLoopUnit->AI_setGroupflag(newflag);
    }
}

bool CvSelectionGroupAI::isHeadUnit(CvUnit* pUnit)
{
    if (getHeadUnit()==pUnit)
    {
        return true;
    }
    return false;
}
// uses the same scale as CvPlayerAI::AI_getOurPlotStrength
int CvSelectionGroupAI::AI_GroupPower(CvPlot* pPlot, bool bDefensiveBonuses) const
{
	CLLNode<IDInfo>* pUnitNode;
	CvUnit* pLoopUnit;
	int iValue;

	iValue = 0;

	pUnitNode = headUnitNode();
	while (pUnitNode != NULL)
	{
		pLoopUnit = ::getUnit(pUnitNode->m_data);
		pUnitNode = nextUnitNode(pUnitNode);

		if ((bDefensiveBonuses && pLoopUnit->canDefend()) || pLoopUnit->canAttack())
		{
			if (!(pLoopUnit->isInvisible(getTeam(), false)))
			{
			    if (pLoopUnit->atPlot(pPlot) || pLoopUnit->canMoveInto(pPlot) || pLoopUnit->canMoveInto(pPlot, /*bAttack*/ true))
			    {
                    iValue += pLoopUnit->currEffectiveStr((bDefensiveBonuses ? pPlot : NULL), NULL);
				}
			}
		}
	}
	return iValue;
}

/*************************************************************************************************/
/**	END	                                        												**/
/*************************************************************************************************/

