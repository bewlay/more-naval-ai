from CvPythonExtensions import *
import CvScreensInterface
import copy
import CvUtil

gc = CyGlobalContext()

def showSomniumIntroPopUp(argsList):
        iPlayer = argsList[0]
        CyMessageControl().sendModNetMessage(CvUtil.Somnium, 0, iPlayer, -1, -1)

class CvSomnium:

	def __init__(self):

                self.playerInGame = [ False for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]
                self.deck = [ [] for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]
                self.bankLeft = [ [] for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]
                self.bankRight = [ [] for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]
                self.drawCards = [ [] for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]

                self.playerLeft = [ -1 for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]
                self.playerRight = [ -1 for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]

                self.turnActions = [ [] for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]
                self.turnActionsMovie = [ [] for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]

                self.canDrawCard = [ False for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]
                self.canEndTurn = [ False for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]
                self.canPickCard = [ False for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]

                self.gameState = [ "" for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]
                self.currentPlayer = [ -1 for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]

                self.gameMP = [ False for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]
                self.Antes = [ 0 for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]

                self.backGrounds = [ "" for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]

                self.gameMPGoldAntes = [0, 10, 20, 50, 100, 200, 300, 500, 700, 1000]
#                self.gameAIGoldAntes = [0, 1]
                self.gameAIGoldAntes = [0]

                self.dice = -1

                self.AI_Aggression = [ 0 for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]
                self.AI_Memory = [ 0 for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]
                self.AI_Intelligence = [ 0 for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]
                self.AI_HU_Score_Begin = [ 0 for iPlayer in range(gc.getMAX_CIV_PLAYERS()) ]

                # code for each card 10*5 cards values 3 to 7, 3 jokers and 1 death
                self.fullDeck = []
                for i in range(10) :
                        for j in range(5) :
                                self.fullDeck.append((i, j + 3))
                self.fullDeck += [(10, 0), (10, 1), (10, 2), (11, 0)]

                # times for turn movie
                # HU pauses
                self.T_0 = 0.5 #pause after drawing the death -> update info
                self.T_1 = 2 #pause after update info after drawing the death -> update center
                self.T_2 = 1.5 #pause after info draw jok -> discard if no card to take
                self.T_3 = 2 #pause after drawing double type ,update info panel -> update center
                self.T_4 = 2 #pause after info panel when no more card to draw -> reset center
                self.T_5 = 2 #pause after bank cards -> and reset center cards
                self.T_6 = 1.5 #pause after stealing a card with a jok -> updates (except direct player following)
                self.T_7 = 2 #pause after stealing a card with a jok double type -> update center
                self.T_8 = 2 #pause after stealing a card with a jok -> no more card
                # AI pauses
                self.T_9 = 1.5 #pause info panel begin AI -> turn begin
                self.T_10 = 1.5 #pause after AI draw
                self.T_11 = 2 #pause after AI draw death -> update center
                self.T_12 = 1.5 #pause after AI joker steal
                self.T_13 = 1.5 #pause after AI joker no use
                self.T_14 = 2 #pause after AI draw same type -> update center
                self.T_15 = 2 #pause after AI bank -> update center
                # end game
                self.T_16 = 4 #pause before closing the screen , and end game

                # sounds
                self.S_1 = 2 #shuffle
                self.S_2 = 1.2 #New turn
                self.S_3 = 3.5 #Applause
                self.S_4 = 1.2 #Death
                self.S_5 = 1.1 #Discard
                self.S_6 = 0.5 #Draw
                self.S_7 = 2 #Fool
                self.S_8 = 4.5 #lose
                self.S_9 = 4.5 #win

        def getDelayBetweenGames(self):
                iMaxTurns = int(gc.getDefineINT("SOMNIUM_BASE_DELAY_TURNS") * gc.getGameSpeedInfo(gc.getGame().getGameSpeedType()).getResearchPercent() / 100.0)
                return iMaxTurns

        def handleAction(self, iFunction, iData1 = -1, iData2 = -1, iData3 = -1):
                # concede            : iFunction : 1, iData1 : player game, iData2 : player click
                # draw card          : iFunction : 2, iData1 : player game, iData2 : player click
                # end turn           : iFunction : 3, iData1 : player game, iData2 : player click
                # pick left card     : iFunction : 4, iData1 : player game, iData2 : player click, iData3 : card index picked
                # pick right card    : iFunction : 5, iData1 : player game, iData2 : player click, iData3 : card index picked
                # endGame            : iFunction : 6, iData1 : player game (Movie call)
                # player can draw    : iFunction : 7, iData1 : player game (Movie call)
                # player can end     : iFunction : 8, iData1 : player game (Movie call)
                # player can pick    : iFunction : 9, iData1 : player game (Movie call)
                # MP current Player  : iFunction : 10, iData1 : player game, iData2 : current Player (Movie call)
                # MP movie finished  : iFunction : 11, iData1 : player game (Movie call)

                if iFunction == 1 :
                        CyMessageControl().sendModNetMessage(CvUtil.Somnium, iFunction, iData1, iData2, iData3)
                        return

                elif iFunction in [6, 7, 8, 9, 10, 11] :
                        self.updateScreen("actionsMovieCalled")
                        CyMessageControl().sendModNetMessage(CvUtil.Somnium, iFunction, iData1, iData2, iData3)

                if not self.canHandleAction() : return

                if iFunction == 2 :
                        if not self.playerCanDrawCard(iData1, iData2) : return
                        self.updateScreen("actionsCalled")
                        CyMessageControl().sendModNetMessage(CvUtil.Somnium, iFunction, iData1, iData2, iData3)

                elif iFunction == 3 :
                        if not self.playerCanEndTurn(iData1, iData2) : return
                        self.updateScreen("actionsCalled")
                        CyMessageControl().sendModNetMessage(CvUtil.Somnium, iFunction, iData1, iData2, iData3)

                elif iFunction == 4 :
                        if not self.playerCanPickLeft(iData1, iData2) : return
                        self.updateScreen("actionsCalled")
                        CyMessageControl().sendModNetMessage(CvUtil.Somnium, iFunction, iData1, iData2, iData3)

                elif iFunction == 5 :
                        if not self.playerCanPickRight(iData1, iData2) : return
                        self.updateScreen("actionsCalled")
                        CyMessageControl().sendModNetMessage(CvUtil.Somnium, iFunction, iData1, iData2, iData3)

        # made to prevent a stack of event to handle for MP games
        def canHandleAction(self):
                # Be sure all players are connected.
                if CyMessageControl().GetFirstBadConnection() != -1 :
                        return False

                # Be sure a player is active to handle an action.
                # With MP games, all event called during AI turns are handled at the beginning of the following turn
                for iPlayer in range(gc.getMAX_CIV_PLAYERS()) :
                        pPlayer = gc.getPlayer(iPlayer)
                        if pPlayer.isNone() :
                                continue
                        if pPlayer.isHuman() :
                                if pPlayer.isAlive() :
                                        if pPlayer.isTurnActive() :
                                                return True
                return False

        def playerCanDrawCard(self, iPlayer, iPlayerClick):
                if not self.canDrawCard[iPlayer] : return False

                if (self.gameMP[iPlayer]) and (self.currentPlayer[iPlayer] != iPlayerClick) : return False

                return True

        def playerCanEndTurn(self, iPlayer, iPlayerClick):
                if not self.canEndTurn[iPlayer] : return False

                if (self.gameMP[iPlayer]) and (self.currentPlayer[iPlayer] != iPlayerClick) : return False

                return True

        def playerCanPickLeft(self, iPlayer, iPlayerClick):
                if not self.canPickCard[iPlayer] : return False
                if iPlayerClick == self.playerLeft[iPlayer] : return False

                if (self.gameMP[iPlayer]) and (self.currentPlayer[iPlayer] != iPlayerClick) : return False

                return True

        def playerCanPickRight(self, iPlayer, iPlayerClick):
                if not self.canPickCard[iPlayer] : return False
                if iPlayerClick == self.playerRight[iPlayer] : return False

                if (self.gameMP[iPlayer]) and (self.currentPlayer[iPlayer] != iPlayerClick) : return False

                return True

        # now apply the action sent by modNetMessage
        def applyAction(self, iFunction, iData1, iData2, iData3):
                # concede          : iFunction : 1, iData1 : player game, iData2 : player click
                # draw card        : iFunction : 2, iData1 : player game, iData2 : player click
                # end turn         : iFunction : 3, iData1 : player game, iData2 : player click
                # pick left card   : iFunction : 4, iData1 : player game, iData2 : player click, iData3 : card index picked
                # pick right card  : iFunction : 5, iData1 : player game, iData2 : player click, iData3 : card index picked
                # endGame          : iFunction : 6, iData1 : player game (Movie call)
                # player can draw  : iFunction : 7, iData1 : player game (Movie call)
                # player can end   : iFunction : 8, iData1 : player game (Movie call)
                # player can pick  : iFunction : 9, iData1 : player game (Movie call)
                # MP current Player  : iFunction : 10, iData1 : player game, iData2 : current Player (Movie call)
                # MP movie finished  : iFunction : 11, iData1 : player game (Movie call)

                iActivePlayer = gc.getGame().getActivePlayer()
                iPlayer = iData1
                iPlayerClick = iData2
                iPlayerNextTurn = iData2
                isPlayerScreen = bool(iActivePlayer in [self.playerLeft[iPlayer], self.playerRight[iPlayer]])
                isLeftScreen = bool(iActivePlayer == self.playerLeft[iPlayer])

                if iFunction == 6:
                        self.endGame(iPlayer)
                        return

                elif iFunction == 7:
                        self.canDrawCard[iPlayer] = True
                        if isLeftScreen : self.updateScreen("actionsMovieReceived")
                        return

                elif iFunction == 8:
                        self.canEndTurn[iPlayer] = True
                        if isLeftScreen : self.updateScreen("actionsMovieReceived")
                        return

                elif iFunction == 9:
                        self.canPickCard[iPlayer] = True
                        if isLeftScreen : self.updateScreen("actionsMovieReceived")
                        return

                elif iFunction == 10:
                        self.currentPlayer[iPlayer] = iPlayerNextTurn
                        if isLeftScreen : self.updateScreen("actionsMovieReceived")
                        return

                elif iFunction == 11:
                        if isPlayerScreen :
                                self.updateScreen("actionsMovieMPReceived")
                                if iPlayerClick == iActivePlayer : self.updateScreen("actionsMovieReceived")
                        return

                if iPlayerClick == self.playerLeft[iPlayer] :
                        iOtherPlayer = self.playerRight[iPlayer]
                else :
                        iOtherPlayer = self.playerLeft[iPlayer]

                # human player draw a card
                if iFunction == 2 :

                        if self.gameState[iPlayer] == "gameStart" :
                                self.gameState[iPlayer] = "playerTurn"

                        card = copy.deepcopy(self.deck[iPlayer][0])
                        iCardType = card[0]
                        iCardNumber = card[1]
                        del self.deck[iPlayer][0]

                        self.turnActions[iPlayer].append(["drawCard", iPlayerClick, iCardType, iCardNumber])
                        self.drawCards[iPlayer].append(card)

                        if self.gameMP[iPlayer] : self.turnActionsMovie[iPlayer].append(["actionsMovieMPCalled", []])
                        self.turnActionsMovie[iPlayer].append(["updateCenterCards", copy.deepcopy(self.drawCards[iPlayer])])
                        self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_DRAW"]])
                        self.turnActionsMovie[iPlayer].append(["wait", [self.S_6]])
                        self.turnActionsMovie[iPlayer].append(["updateCardsLeft", [len(self.deck[iPlayer])]])
                        self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])

                        if iCardType == 11 : #death
                                self.canDrawCard[iPlayer] = False
                                self.canEndTurn[iPlayer] = False

                                self.turnActions[iPlayer].append(["DiscardDeath", iPlayerClick])

                                self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_DEATH"]])
                                self.turnActionsMovie[iPlayer].append(["wait", [max(self.S_4, self.T_0)]])
                                self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                self.turnActionsMovie[iPlayer].append(["wait", [self.T_1]])

                                self.drawCards[iPlayer] = []

                                self.turnActionsMovie[iPlayer].append(["updateCenterCards", copy.deepcopy(self.drawCards[iPlayer])])
                                self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_DISCARD"]])
                                self.turnActionsMovie[iPlayer].append(["wait", [self.S_5]])

                                if len(self.deck[iPlayer]) == 0 :
                                        self.handleEndGame(iPlayer)
                                elif self.gameMP[iPlayer] :
                                        self.turnActions[iPlayer].append(["BeginTurn", iOtherPlayer])
                                        self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                        self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_NEW_TURN"]])
                                        self.turnActionsMovie[iPlayer].append(["wait", [self.S_2]])
                                        self.turnActionsMovie[iPlayer].append(["currentPlayer", [iOtherPlayer]])
                                        self.turnActionsMovie[iPlayer].append(["canDrawCard", []])
                                        self.turnActionsMovie[iPlayer].append(["actionsReceived", [iPlayerClick]])
                                        self.turnActionsMovie[iPlayer].append(["endMovieMP", []])
                                        if isPlayerScreen : self.updateScreen("launchTurnMovie", copy.deepcopy(self.turnActionsMovie[iPlayer]))

                                        self.turnActionsMovie[iPlayer] = []
                                else :
                                        self.handleAITurn(iPlayer)

                        elif iCardType == 10 : #joker

                                if len(self.getOtherBank(iPlayer, iPlayerClick)) > 0 :
                                        self.canDrawCard[iPlayer] = False
                                        self.canEndTurn[iPlayer] = False

                                        self.turnActions[iPlayer].append(["HUJokerPickCard", iPlayerClick])

                                        self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_FOOL"]])
                                        self.turnActionsMovie[iPlayer].append(["wait", [self.S_7]])
                                        self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                        self.turnActionsMovie[iPlayer].append(["canPickCard", []])
                                        self.turnActionsMovie[iPlayer].append(["actionsReceived", [iPlayerClick]])
                                        if self.gameMP[iPlayer] : self.turnActionsMovie[iPlayer].append(["endMovieMP", []])
                                        if isPlayerScreen : self.updateScreen("launchTurnMovie", copy.deepcopy(self.turnActionsMovie[iPlayer]))

                                        self.turnActionsMovie[iPlayer] = []

                                else :
                                        self.drawCards[iPlayer].remove(card)

                                        self.turnActions[iPlayer].append(["JokerNoUse", iPlayerClick])

                                        self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_FOOL"]])
                                        self.turnActionsMovie[iPlayer].append(["wait", [self.S_7]])
                                        self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                        self.turnActionsMovie[iPlayer].append(["wait", [self.T_2]])
                                        self.turnActionsMovie[iPlayer].append(["updateCenterCards", copy.deepcopy(self.drawCards[iPlayer])])

                                        if len(self.deck[iPlayer]) == 0 :
                                                self.handleEndGame(iPlayer)
                                        else :
                                                self.turnActionsMovie[iPlayer].append(["actionsReceived", [iPlayerClick]])
                                                if self.gameMP[iPlayer] : self.turnActionsMovie[iPlayer].append(["endMovieMP", []])
                                                if isPlayerScreen : self.updateScreen("launchTurnMovie", copy.deepcopy(self.turnActionsMovie[iPlayer]))
                                                self.turnActionsMovie[iPlayer] = []

                        else :

                                doubleType = self.getCenterDoubleType(iPlayer)
                                if doubleType != -1 :

                                        self.canDrawCard[iPlayer] = False
                                        self.canEndTurn[iPlayer] = False

                                        self.turnActions[iPlayer].append(["DiscardSameType", iPlayerClick, doubleType])

                                        self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                        self.turnActionsMovie[iPlayer].append(["wait", [self.T_3]])
                                        self.drawCards[iPlayer] = []
                                        self.turnActionsMovie[iPlayer].append(["updateCenterCards", copy.deepcopy(self.drawCards[iPlayer])])
                                        self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_DISCARD"]])
                                        self.turnActionsMovie[iPlayer].append(["wait", [self.S_5]])

                                        if len(self.deck[iPlayer]) == 0 :
                                                self.handleEndGame(iPlayer)
                                        elif self.gameMP[iPlayer] :
                                                self.turnActions[iPlayer].append(["BeginTurn", iOtherPlayer])
                                                self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                                self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_NEW_TURN"]])
                                                self.turnActionsMovie[iPlayer].append(["wait", [self.S_2]])
                                                self.turnActionsMovie[iPlayer].append(["currentPlayer", [iOtherPlayer]])
                                                self.turnActionsMovie[iPlayer].append(["canDrawCard", []])
                                                self.turnActionsMovie[iPlayer].append(["actionsReceived", [iPlayerClick]])
                                                self.turnActionsMovie[iPlayer].append(["endMovieMP", []])
                                                if isPlayerScreen : self.updateScreen("launchTurnMovie", copy.deepcopy(self.turnActionsMovie[iPlayer]))

                                                self.turnActionsMovie[iPlayer] = []
                                        else :
                                                self.handleAITurn(iPlayer)

                                else :

                                        if len(self.deck[iPlayer]) == 0 :
                                                if iPlayerClick == self.playerLeft[iPlayer] :
                                                        iBeforeScore = self.getLeftScore(iPlayer)
                                                        for iType, iValue in self.drawCards[iPlayer] : self.bankLeft[iPlayer].append((iType, iValue))
                                                        self.drawCards[iPlayer] = []
                                                        points = self.getLeftScore(iPlayer) - iBeforeScore
                                                else :
                                                        iBeforeScore = self.getRightScore(iPlayer)
                                                        for iType, iValue in self.drawCards[iPlayer] : self.bankRight[iPlayer].append((iType, iValue))
                                                        self.drawCards[iPlayer] = []
                                                        points = self.getRightScore(iPlayer) - iBeforeScore

                                                self.turnActions[iPlayer].append(["BankCard", iPlayerClick, points])

                                                self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                                self.turnActionsMovie[iPlayer].append(["wait", [self.T_4]])
                                                self.turnActionsMovie[iPlayer].append(["updateCenterCards", copy.deepcopy(self.drawCards[iPlayer])])
                                                if iPlayerClick == self.playerLeft[iPlayer] :
                                                        self.turnActionsMovie[iPlayer].append(["updateLeftCards", [self.getBestCardLeft(iPlayer, iType) for iType in range(10)]])
                                                        self.turnActionsMovie[iPlayer].append(["updateLeftScore", [self.getLeftScore(iPlayer)]])
                                                else :
                                                        self.turnActionsMovie[iPlayer].append(["updateRightCards", [self.getBestCardRight(iPlayer, iType) for iType in range(10)]])
                                                        self.turnActionsMovie[iPlayer].append(["updateRightScore", [self.getRightScore(iPlayer)]])

                                                self.handleEndGame(iPlayer)

                                        else :
                                                if len(self.drawCards[iPlayer]) == 10 :
                                                        self.canDrawCard[iPlayer] = False
                                                        self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_APPLAUSE"]])
                                                        self.turnActionsMovie[iPlayer].append(["wait", [self.S_3]])

                                                self.turnActionsMovie[iPlayer].append(["canEndTurn", []])
                                                self.turnActionsMovie[iPlayer].append(["actionsReceived", [iPlayerClick]])
                                                if self.gameMP[iPlayer] : self.turnActionsMovie[iPlayer].append(["endMovieMP", []])
                                                if isPlayerScreen : self.updateScreen("launchTurnMovie", copy.deepcopy(self.turnActionsMovie[iPlayer]))

                                                self.turnActionsMovie[iPlayer] = []

                # end turn
                elif iFunction == 3 :

                        if self.gameState[iPlayer] == "gameStart" : #SG game
                                self.gameState[iPlayer] = "playerTurn"
                        else :
                                if iPlayerClick == self.playerLeft[iPlayer] :
                                        iBeforeScore = self.getLeftScore(iPlayer)
                                        for iType, iValue in self.drawCards[iPlayer] : self.bankLeft[iPlayer].append((iType, iValue))
                                        self.drawCards[iPlayer] = []
                                        points = self.getLeftScore(iPlayer) - iBeforeScore
                                else :
                                        iBeforeScore = self.getRightScore(iPlayer)
                                        for iType, iValue in self.drawCards[iPlayer] : self.bankRight[iPlayer].append((iType, iValue))
                                        self.drawCards[iPlayer] = []
                                        points = self.getRightScore(iPlayer) - iBeforeScore

                                self.turnActions[iPlayer].append(["BankCard", iPlayerClick, points])

                                if self.gameMP[iPlayer] : self.turnActionsMovie[iPlayer].append(["actionsMovieMPCalled", []])
                                self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                self.turnActionsMovie[iPlayer].append(["wait", [self.T_5]])
                                self.turnActionsMovie[iPlayer].append(["updateCenterCards", copy.deepcopy(self.drawCards[iPlayer])])
                                if iPlayerClick == self.playerLeft[iPlayer] :
                                        self.turnActionsMovie[iPlayer].append(["updateLeftCards", [self.getBestCardLeft(iPlayer, iType) for iType in range(10)]])
                                        self.turnActionsMovie[iPlayer].append(["updateLeftScore", [self.getLeftScore(iPlayer)]])
                                else :
                                        self.turnActionsMovie[iPlayer].append(["updateRightCards", [self.getBestCardRight(iPlayer, iType) for iType in range(10)]])
                                        self.turnActionsMovie[iPlayer].append(["updateRightScore", [self.getRightScore(iPlayer)]])

                        self.canDrawCard[iPlayer] = False
                        self.canEndTurn[iPlayer] = False

                        if self.gameMP[iPlayer] :
                                self.turnActions[iPlayer].append(["BeginTurn", iOtherPlayer])
                                self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_NEW_TURN"]])
                                self.turnActionsMovie[iPlayer].append(["wait", [self.S_2]])
                                self.turnActionsMovie[iPlayer].append(["currentPlayer", [iOtherPlayer]])
                                self.turnActionsMovie[iPlayer].append(["canDrawCard", []])
                                self.turnActionsMovie[iPlayer].append(["actionsReceived", [iPlayerClick]])
                                self.turnActionsMovie[iPlayer].append(["endMovieMP", []])
                                if isPlayerScreen : self.updateScreen("launchTurnMovie", copy.deepcopy(self.turnActionsMovie[iPlayer]))

                                self.turnActionsMovie[iPlayer] = []
                        else :
                                self.handleAITurn(iPlayer)

                #pick card
                elif iFunction in [4, 5] :

                        self.canPickCard[iPlayer] = False

                        iCardStolenType = iData3
                        if iPlayerClick == self.playerLeft[iPlayer] :
                                cardStolen = self.getBestCardRight(iPlayer, iCardStolenType)
                                self.bankRight[iPlayer].remove(cardStolen)
                        else :
                                cardStolen = self.getBestCardLeft(iPlayer, iCardStolenType)
                                self.bankLeft[iPlayer].remove(cardStolen)
                        del self.drawCards[iPlayer][-1]
                        self.drawCards[iPlayer].append(cardStolen)

                        self.turnActions[iPlayer].append(["JokerSteal", iPlayerClick, iOtherPlayer, cardStolen[0], cardStolen[1]])

                        if self.gameMP[iPlayer] : self.turnActionsMovie[iPlayer].append(["actionsMovieMPCalled", []])
                        self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                        self.turnActionsMovie[iPlayer].append(["updateCenterCards", copy.deepcopy(self.drawCards[iPlayer])])
                        if iPlayerClick == self.playerRight[iPlayer] :
                                self.turnActionsMovie[iPlayer].append(["updateLeftCards", [self.getBestCardLeft(iPlayer, iType) for iType in range(10)]])
                                self.turnActionsMovie[iPlayer].append(["updateLeftScore", [self.getLeftScore(iPlayer)]])
                        else :
                                self.turnActionsMovie[iPlayer].append(["updateRightCards", [self.getBestCardRight(iPlayer, iType) for iType in range(10)]])
                                self.turnActionsMovie[iPlayer].append(["updateRightScore", [self.getRightScore(iPlayer)]])

                        doubleType = self.getCenterDoubleType(iPlayer)
                        if doubleType != -1 :

                                self.canDrawCard[iPlayer] = False
                                self.canEndTurn[iPlayer] = False

                                self.turnActionsMovie[iPlayer].append(["wait", [self.T_6]])
                                self.turnActions[iPlayer].append(["DiscardSameType", iPlayerClick, doubleType])

                                self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                self.turnActionsMovie[iPlayer].append(["wait", [self.T_7]])

                                self.drawCards[iPlayer] = []

                                self.turnActionsMovie[iPlayer].append(["updateCenterCards", copy.deepcopy(self.drawCards[iPlayer])])
                                self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_DISCARD"]])
                                self.turnActionsMovie[iPlayer].append(["wait", [self.S_5]])

                                if len(self.deck[iPlayer]) == 0 :
                                        self.handleEndGame(iPlayer)
                                elif self.gameMP[iPlayer] :
                                        self.turnActions[iPlayer].append(["BeginTurn", iOtherPlayer])
                                        self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                        self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_NEW_TURN"]])
                                        self.turnActionsMovie[iPlayer].append(["wait", [self.S_2]])
                                        self.turnActionsMovie[iPlayer].append(["currentPlayer", [iOtherPlayer]])
                                        self.turnActionsMovie[iPlayer].append(["canDrawCard", []])
                                        self.turnActionsMovie[iPlayer].append(["actionsReceived", [iPlayerClick]])
                                        self.turnActionsMovie[iPlayer].append(["endMovieMP", []])
                                        if isPlayerScreen : self.updateScreen("launchTurnMovie", copy.deepcopy(self.turnActionsMovie[iPlayer]))

                                        self.turnActionsMovie[iPlayer] = []
                                else :
                                        self.handleAITurn(iPlayer)

                        elif len(self.deck[iPlayer]) == 0 :

                                self.canDrawCard[iPlayer] = False
                                self.canEndTurn[iPlayer] = False

                                if iPlayerClick == self.playerLeft[iPlayer] :
                                        iBeforeScore = self.getLeftScore(iPlayer)
                                        for iType, iValue in self.drawCards[iPlayer] : self.bankLeft[iPlayer].append((iType, iValue))
                                        self.drawCards[iPlayer] = []
                                        points = self.getLeftScore(iPlayer) - iBeforeScore
                                else :
                                        iBeforeScore = self.getRightScore(iPlayer)
                                        for iType, iValue in self.drawCards[iPlayer] : self.bankRight[iPlayer].append((iType, iValue))
                                        self.drawCards[iPlayer] = []
                                        points = self.getRightScore(iPlayer) - iBeforeScore

                                self.turnActionsMovie[iPlayer].append(["wait", [self.T_6]])
                                self.turnActions[iPlayer].append(["BankCard", iPlayerClick, points])

                                self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                self.turnActionsMovie[iPlayer].append(["wait", [self.T_8]])
                                self.turnActionsMovie[iPlayer].append(["updateCenterCards", copy.deepcopy(self.drawCards[iPlayer])])
                                if iPlayerClick == self.playerLeft[iPlayer] :
                                        self.turnActionsMovie[iPlayer].append(["updateLeftCards", [self.getBestCardLeft(iPlayer, iType) for iType in range(10)]])
                                        self.turnActionsMovie[iPlayer].append(["updateLeftScore", [self.getLeftScore(iPlayer)]])
                                else :
                                        self.turnActionsMovie[iPlayer].append(["updateRightCards", [self.getBestCardRight(iPlayer, iType) for iType in range(10)]])
                                        self.turnActionsMovie[iPlayer].append(["updateRightScore", [self.getRightScore(iPlayer)]])

                                self.handleEndGame(iPlayer)

                        else :
                                if len(self.drawCards[iPlayer]) == 10 :
                                        self.canDrawCard[iPlayer] = False
                                        self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_APPLAUSE"]])
                                        self.turnActionsMovie[iPlayer].append(["wait", [self.S_3]])
                                else :
                                        self.turnActionsMovie[iPlayer].append(["canDrawCard", []])

                                self.turnActionsMovie[iPlayer].append(["canEndTurn", []])
                                self.turnActionsMovie[iPlayer].append(["actionsReceived", [iPlayerClick]])
                                if self.gameMP[iPlayer] : self.turnActionsMovie[iPlayer].append(["endMovieMP", []])
                                if isPlayerScreen : self.updateScreen("launchTurnMovie", copy.deepcopy(self.turnActionsMovie[iPlayer]))

                                self.turnActionsMovie[iPlayer] = []

        def handleAITurn(self, iPlayer):
                iActivePlayer = gc.getGame().getActivePlayer()
                isPlayerScreen = bool(iActivePlayer == self.playerLeft[iPlayer])
                iAIPlayer = self.playerRight[iPlayer]
                self.AI_HU_Score_Begin[iPlayer] = self.getLeftScore(iPlayer)

                self.turnActions[iPlayer].append(["BeginTurn", iAIPlayer])

                self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_NEW_TURN"]])
                self.turnActionsMovie[iPlayer].append(["wait", [max(self.S_2, self.T_9)]])

                while True :
                        # draw a card
                        card = copy.deepcopy(self.deck[iPlayer][0])
                        iCardType = card[0]
                        iCardNumber = card[1]
                        del self.deck[iPlayer][0]
                        self.turnActions[iPlayer].append(["drawCard", iAIPlayer, iCardType, iCardNumber])
                        self.drawCards[iPlayer].append(card)

                        self.turnActionsMovie[iPlayer].append(["updateCenterCards", copy.deepcopy(self.drawCards[iPlayer])])
                        self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_DRAW"]])
                        self.turnActionsMovie[iPlayer].append(["wait", [self.S_6]])
                        self.turnActionsMovie[iPlayer].append(["updateCardsLeft", [len(self.deck[iPlayer])]])
                        self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                        self.turnActionsMovie[iPlayer].append(["wait", [self.T_10]])
                
                        if iCardType == 11 : #death

                                self.turnActions[iPlayer].append(["DiscardDeath", iAIPlayer])

                                self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_DEATH"]])
                                self.turnActionsMovie[iPlayer].append(["wait", [max(self.S_4, self.T_11)]])

                                self.drawCards[iPlayer] = []

                                self.turnActionsMovie[iPlayer].append(["updateCenterCards", copy.deepcopy(self.drawCards[iPlayer])])
                                self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_DISCARD"]])
                                self.turnActionsMovie[iPlayer].append(["wait", [self.S_5]])

                                break

                        elif iCardType == 10 : #joker

                                if len(self.bankLeft[iPlayer]) > 0 :
                                        bestStealCard = self.AI_Choose_Joker_Steal(iPlayer)
                                        self.drawCards[iPlayer].remove(card)
                                        self.bankLeft[iPlayer].remove(bestStealCard)
                                        self.drawCards[iPlayer].append(bestStealCard)

                                        self.turnActions[iPlayer].append(["JokerSteal", iAIPlayer, self.playerLeft[iPlayer], bestStealCard[0], bestStealCard[1]])

                                        self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                        self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_FOOL"]])
                                        self.turnActionsMovie[iPlayer].append(["wait", [self.S_7]])
                                        self.turnActionsMovie[iPlayer].append(["updateCenterCards", copy.deepcopy(self.drawCards[iPlayer])])
                                        self.turnActionsMovie[iPlayer].append(["updateLeftCards", [self.getBestCardLeft(iPlayer, iType) for iType in range(10)]])
                                        self.turnActionsMovie[iPlayer].append(["updateLeftScore", [self.getLeftScore(iPlayer)]])
                                        self.turnActionsMovie[iPlayer].append(["wait", [self.T_12]])

                                else :
                                        self.drawCards[iPlayer].remove(card)

                                        self.turnActions[iPlayer].append(["JokerNoUse", iAIPlayer])

                                        self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                        self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_FOOL"]])
                                        self.turnActionsMovie[iPlayer].append(["wait", [self.S_7]])
                                        self.turnActionsMovie[iPlayer].append(["updateCenterCards", copy.deepcopy(self.drawCards[iPlayer])])
                                        self.turnActionsMovie[iPlayer].append(["wait", [self.T_13]])

                        doubleType = self.getCenterDoubleType(iPlayer)
                        if doubleType != -1 :

                                self.turnActions[iPlayer].append(["DiscardSameType", iAIPlayer, doubleType])

                                self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                self.turnActionsMovie[iPlayer].append(["wait", [self.T_14]])

                                self.drawCards[iPlayer] = []

                                self.turnActionsMovie[iPlayer].append(["updateCenterCards", copy.deepcopy(self.drawCards[iPlayer])])
                                self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_DISCARD"]])
                                self.turnActionsMovie[iPlayer].append(["wait", [self.S_5]])

                                break

                        if self.AI_Choose_Bank(iPlayer) :

                                iBeforeScore = self.getRightScore(iPlayer)
                                for iType, iValue in self.drawCards[iPlayer] : self.bankRight[iPlayer].append((iType, iValue))
                                self.drawCards[iPlayer] = []
                                points = self.getRightScore(iPlayer) - iBeforeScore

                                self.turnActions[iPlayer].append(["BankCard", iAIPlayer, points])

                                self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                                self.turnActionsMovie[iPlayer].append(["wait", [self.T_15]])
                                self.turnActionsMovie[iPlayer].append(["updateCenterCards", copy.deepcopy(self.drawCards[iPlayer])])
                                self.turnActionsMovie[iPlayer].append(["updateRightCards", [self.getBestCardRight(iPlayer, iType) for iType in range(10)]])
                                self.turnActionsMovie[iPlayer].append(["updateRightScore", [self.getRightScore(iPlayer)]])

                                break

                if len(self.deck[iPlayer]) == 0 :
                        self.handleEndGame(iPlayer)
                else :
                        self.turnActions[iPlayer].append(["BeginTurn", self.playerLeft[iPlayer]])
                        self.canEndTurn[iPlayer] = False

                        self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                        self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_NEW_TURN"]])
                        self.turnActionsMovie[iPlayer].append(["wait", [self.S_2]])
                        self.turnActionsMovie[iPlayer].append(["canDrawCard", []])
                        self.turnActionsMovie[iPlayer].append(["actionsReceived", [self.playerLeft[iPlayer]]])
                        if isPlayerScreen : self.updateScreen("launchTurnMovie", copy.deepcopy(self.turnActionsMovie[iPlayer]))

                        self.turnActionsMovie[iPlayer] = []

        def AI_Choose_Bank(self, iPlayer):
                if len(self.drawCards[iPlayer]) == 10 :
                        self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_APPLAUSE"]])
                        self.turnActionsMovie[iPlayer].append(["wait", [self.S_3]])
                        return True
                if len(self.deck[iPlayer]) == 0 : return True

                scoreLeft = self.getLeftScore(iPlayer)
                iExtraPoints = self.getScoreBank(iPlayer)
                currentScore = self.getRightScore(iPlayer) + iExtraPoints
                diffScore = currentScore - scoreLeft

                if self.AI_Intelligence[iPlayer] >= 3 :
                        iExtraPoints += self.AI_HU_Score_Begin[iPlayer] - scoreLeft
                if (self.AI_Aggression[iPlayer] < 50) and (self.AI_Intelligence[iPlayer] >= 2) :
                        nbJoker = len([card for card in self.deck[iPlayer] if card[0] == 10])
                        if nbJoker > 0 :
                                for iType, iValue in self.drawCards[iPlayer] :
                                        if iType >= 10 : continue

                                        bestBank = self.getBestCardRight(iPlayer, iType)
                                        if bestBank == -1 : continue
                                        nbType = len([card for card in self.bankRight[iPlayer] if card[0] == iType])
                                        if nbType == 1 :
                                                iExtraPoints += 1
                iGoodDrawChance = self.AI_CalculateChance(iPlayer)

                if iGoodDrawChance <= 15 : return True
                if iExtraPoints <= 1 : return False
                if iGoodDrawChance >= 95 : return False

                if (self.AI_Intelligence[iPlayer] >= 5) and (len(self.deck[iPlayer]) < 13) :
                        if diffScore > 15 :
                                if iExtraPoints >= 7 :
                                        return True
                                elif iGoodDrawChance <= 30 :
                                        return True
                        elif diffScore < -13 :
                                if iExtraPoints >= 10 :
                                        return True
                                elif iExtraPoints >= 7 :
                                        if iGoodDrawChance <= len(self.deck[iPlayer]) + ( (150 - self.AI_Aggression[iPlayer]) * 2.0 / 3 ): return True
                                elif (iGoodDrawChance <= 35) and (len(self.deck[iPlayer]) > 5) :
                                        return True
                        else :
                                if iExtraPoints >= 10 :
                                        return True
                                elif iExtraPoints >= 7 :
                                        if (iGoodDrawChance - len(self.deck[iPlayer])) <= ( (150 - self.AI_Aggression[iPlayer]) * 2.0 / 3 ): return True
                                elif iExtraPoints >= 3 :
                                        if (iGoodDrawChance - len(self.deck[iPlayer])) <= ( (130 - self.AI_Aggression[iPlayer]) * 2.0 / 3 ): return True
                                if iGoodDrawChance < (79 + len(self.deck[iPlayer]) - self.AI_Aggression[iPlayer]) :
                                        return True
                else :
                        if iExtraPoints >= 19 :
                                return True
                        elif iExtraPoints >= 13 :
                                if iGoodDrawChance <= ( (180 - self.AI_Aggression[iPlayer]) * 2.0 / 3 ): return True
                        elif iExtraPoints >= 7 :
                                if iGoodDrawChance <= ( (150 - self.AI_Aggression[iPlayer]) * 2.0 / 3 ): return True
                        elif iExtraPoints >= 3 :
                                if iGoodDrawChance <= ( (130 - self.AI_Aggression[iPlayer]) * 2.0 / 3 ): return True
                        if iGoodDrawChance < (83 - self.AI_Aggression[iPlayer]) :
                                return True
                
                return False

        def AI_Choose_Joker_Steal(self, iPlayer):
                bestCards = []
                bestValue = - 1000
                bChoiceOnCenter = True
                lNoTypeCards = list(set([iType for iType, iValue in self.drawCards[iPlayer] if iType < 10]))
                iExtraPoints = self.getScoreBank(iPlayer)

                for i in range(10):
                        lCard = self.getBestCardLeft(iPlayer, i)
                        if lCard == -1 : continue

                        bTypeOnCenter = bool(lCard[0] in lNoTypeCards)
                        lCardRight = self.getBestCardRight(iPlayer, i)

                        val = copy.deepcopy(iExtraPoints)
                        if bTypeOnCenter : val = 0

                        if not bTypeOnCenter :
                                if (lCardRight != -1) :
                                        if lCardRight[1] < lCard[1] :
                                                val += lCard[1] - lCardRight[1]
                                else :
                                        val += lCard[1]

                        if self.AI_Intelligence[iPlayer] >= 4 :
                                val += lCard[1]

                                lCardsLeftValues = [card[1] for card in self.bankLeft[iPlayer] if (card[1] != lCard[1]) and (card[0] == i)]
                                if len(lCardsLeftValues) > 0 :
                                        iSecondVal = max(lCardsLeftValues)
                                        val -= iSecondVal

                        if val > bestValue :
                                bestCards = [lCard]
                                bestValue = val
                                bChoiceOnCenter = bTypeOnCenter
                        elif val == bestValue :
                                if bChoiceOnCenter :
                                        if not bTypeOnCenter :
                                                bestCards = [lCard]
                                                bestValue = val
                                                bChoiceOnCenter = False
                                        else :
                                                bestCards.append(lCard)
                                elif not bTypeOnCenter :
                                        bestCards.append(lCard)

                bestCard = bestCards[self.dice.get(len(bestCards), " Somnium : joker choice")]
                return bestCard

        def AI_CalculateChance(self, iPlayer):
                iGoodDraw = 0
                iBadDraw = 0

                lTypes = [card[0] for card in self.drawCards[iPlayer]]
                nbTypes = len(lTypes)

                dictMemory = {
                    3 : 7,
                    4 : 6,
                    5 : 5,
                    6 : 4,
                    7 : 3
                    }

                for iType, iValue in self.deck[iPlayer] :
                        if iType == 10 :
                                iGoodDraw += 10
                                continue
                        if iType == 11 :
                                iBadDraw += 10
                                continue

                        if self.AI_Intelligence[iPlayer] >= dictMemory[iValue] :
                                if iType in lTypes :
                                        iBadDraw += 10
                                else :
                                        iGoodDraw += 10
                                continue

                        iBadDraw += nbTypes
                        iGoodDraw += 10 - nbTypes

                iChance = int(iGoodDraw * 100.0 / (iGoodDraw + iBadDraw))
                return iChance

        def getAggressiveness(self, iPlayer):
                # < 50 && intelligence >= 2 : if some jokers left, consider another same type card in bank as a little advantage
                iAgressiveness = gc.getLeaderHeadInfo(gc.getPlayer(self.playerRight[iPlayer]).getLeaderType()).getSomniumAggressiveness()
                iAgressiveness = min(100, max(0, iAgressiveness))
                return iAgressiveness

        def getMemory(self, iPlayer):
                # all AI remember jokers and death left
                # >= 3 : remember all 7
                # >= 4 : remember all 6
                # >= 5 : remember all 5
                # >= 6 : remember all 4
                # >= 7 : remember all 3
                iDifficulty = int(gc.getPlayer(self.playerLeft[iPlayer]).getHandicapType())
                iDifficulty = max(0, iDifficulty - self.getAggressiveness(iPlayer) / 50)
                return iDifficulty

        def getIntelligence(self, iPlayer):
                # >= 5 : at the end of game, be able to draw more cards if very good/bad advantage
                # >= 3 : take in count HU point lost with joker for bank choice
                # >= 4 : take in count HU point lost with joker choice
                # >= 2 && Aggressiveness < 50 : if some jokers left, consider another same type card in bank as a little advantage
                iDifficulty = int(gc.getPlayer(self.playerLeft[iPlayer]).getHandicapType())
                iDifficulty = max(0, iDifficulty - self.getAggressiveness(iPlayer) / 50)
                return iDifficulty

        def handleEndGame(self, iPlayer):
                iLooser = self.getLooser(iPlayer)
                iActivePlayer = gc.getGame().getActivePlayer()
                isPlayerScreen = bool(iActivePlayer in [self.playerLeft[iPlayer], self.playerRight[iPlayer]])

                self.turnActions[iPlayer].append(["EndGame", iLooser])

                self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                if isPlayerScreen :
                        if iLooser == iActivePlayer :
                                self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_LOSE"]])
                                self.turnActionsMovie[iPlayer].append(["wait", [max(self.S_8, self.T_16)]])
                        elif iLooser != -1 :
                                self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_WIN"]])
                                self.turnActionsMovie[iPlayer].append(["wait", [max(self.S_9, self.T_16)]])
                        else :
                                self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_APPLAUSE"]])
                                self.turnActionsMovie[iPlayer].append(["wait", [max(self.S_3, self.T_16)]])

                        self.turnActionsMovie[iPlayer].append(["endGame", []])
                        self.updateScreen("launchTurnMovie", copy.deepcopy(self.turnActionsMovie[iPlayer]))

                self.turnActionsMovie[iPlayer] = []

        def getCenterDoubleType(self, iPlayer):
                lTypes = []
                for iType, iValue in self.drawCards[iPlayer] :
                        if iType in lTypes : return iType
                        lTypes.append(iType)
                return -1

        def updateScreen(self, part, argsList = None):
                CvScreensInterface.updateCorporationElement(part, argsList)

        def canStartGame(self, iPlayer):
                return not self.playerInGame[iPlayer]

        def getStartGameAIWith(self, iPlayer, iOpponent):

                pRightPlayer = gc.getPlayer(iOpponent)
                if pRightPlayer.isNone() : return [["No"]]
                if not pRightPlayer.isAlive() : return [["No"]]
                if pRightPlayer.isHuman() : return [["No"]]

                pLeftPlayer = gc.getPlayer(iPlayer)
                iPlayerGold = pLeftPlayer.getGold()
		iLeftPlayerTeam = pLeftPlayer.getTeam()
                iRightPlayerTeam = pRightPlayer.getTeam()
                if iRightPlayerTeam == iLeftPlayerTeam : return [["gold", [iGold for iGold in self.gameAIGoldAntes if iGold <= iPlayerGold]]]

                pRightTeam = gc.getTeam(iRightPlayerTeam)
                if not pRightTeam.isHasMet(iLeftPlayerTeam) : return [["notMet"]]
                if pRightTeam.isAtWar(iLeftPlayerTeam) : return [["atWar"]]

                iDelay = pRightPlayer.AI_getMemoryCount(iPlayer, MemoryTypes.MEMORY_SOMNIUM_DELAY)
                if iDelay <= 0 :
                        lGames = [["relation", 0]]
                else :
                        lGames = [["relation", iDelay]]

                lGames += [["gold", [iGold for iGold in self.gameAIGoldAntes if iGold <= iPlayerGold]]]

                return lGames

        def getStartGameMPWith(self, iPlayer, iOpponent):

                if not gc.getGame().isNetworkMultiPlayer() : return [["No"]]
                if iPlayer == iOpponent : return [["No"]]

                pRightPlayer = gc.getPlayer(iOpponent)
                if pRightPlayer.isNone() : return [["No"]]
                if not pRightPlayer.isAlive() : return [["No"]]

                pLeftPlayer = gc.getPlayer(iPlayer)
                iLeftGold = pLeftPlayer.getGold()
                iRightGold = pRightPlayer.getGold()
		iLeftPlayerTeam = pLeftPlayer.getTeam()
                iRightPlayerTeam = pRightPlayer.getTeam()

                lGoldAntes = [["gold", [iGold for iGold in self.gameMPGoldAntes if (iGold <= iLeftGold) and (iGold <= iRightGold)]]]

                if iRightPlayerTeam == iLeftPlayerTeam :
                        if self.playerInGame[iOpponent] :
                                return [["InGame"]]
                        else :
                                return lGoldAntes

                pRightTeam = gc.getTeam(iRightPlayerTeam)
                if not pRightTeam.isHasMet(iLeftPlayerTeam) : return [["notMet"]]
                if pRightTeam.isAtWar(iLeftPlayerTeam) : return [["atWar"]]

                if self.playerInGame[iOpponent] :
                        return [["InGame"]]
                else :
                        return lGoldAntes

        def startGame(self, iPlayer, iOpponent, iGold):

                pLeftPlayer = gc.getPlayer(iPlayer)
                pRightPlayer = gc.getPlayer(iOpponent)

                bCanStart = True
                if not pLeftPlayer.isAlive() :
                        bCanStart = False
                        CyInterface().addMessage(iPlayer, True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_PLAYER_DEAD", ()), '', 1, '', ColorTypes(7), -1, -1, False, False)
                        if pRightPlayer.isAlive() :
                                if pRightPlayer.isHuman() :
                                        CyInterface().addMessage(iOpponent, True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_PLAYER_DEAD_PLAYER", (pLeftPlayer.getName(), )), '', 1, '', ColorTypes(7), -1, -1, False, False)

                if not pRightPlayer.isAlive() :
                        bCanStart = False
                        CyInterface().addMessage(iPlayer, True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_PLAYER_DEAD_PLAYER", (pRightPlayer.getName(), )), '', 1, '', ColorTypes(7), -1, -1, False, False)
                        if pRightPlayer.isHuman() :
                                CyInterface().addMessage(iOpponent, True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_PLAYER_DEAD", ()), '', 1, '', ColorTypes(7), -1, -1, False, False)
                if not bCanStart : return

                self.dice = gc.getGame().getSorenRand()

                self.Antes[iPlayer] = iGold

                self.gameMP[iPlayer] = bool(pRightPlayer.isHuman())

                self.playerInGame[iPlayer] = True
                if self.gameMP[iPlayer] :
                        self.playerInGame[iOpponent] = True
                elif iGold == -1 :
                        iDelay = self.getDelayBetweenGames()
                        pRightPlayer.AI_changeMemoryCount(iPlayer, MemoryTypes.MEMORY_SOMNIUM_DELAY, iDelay - pRightPlayer.AI_getMemoryCount(iPlayer, MemoryTypes.MEMORY_SOMNIUM_DELAY))
                        while pRightPlayer.AI_getMemoryCount(iPlayer, MemoryTypes.MEMORY_SOMNIUM_POSITIVE) > 0 :
                                pRightPlayer.AI_changeMemoryCount(iPlayer, MemoryTypes.MEMORY_SOMNIUM_POSITIVE, -1)
                        while pRightPlayer.AI_getMemoryCount(iPlayer, MemoryTypes.MEMORY_SOMNIUM_NEGATIVE) > 0 :
                                pRightPlayer.AI_changeMemoryCount(iPlayer, MemoryTypes.MEMORY_SOMNIUM_NEGATIVE, -1)

                self.deck[iPlayer] = [copy.deepcopy(self.fullDeck[i]) for i in CvUtil.shuffle(len(self.fullDeck), self.dice)]

                self.bankLeft[iPlayer] = []
                self.bankRight[iPlayer] = []
                self.drawCards[iPlayer] = []
                self.gameState[iPlayer] = "gameStart"

                self.playerLeft[iPlayer] = iPlayer
                self.playerRight[iPlayer] = iOpponent

                self.AI_Aggression[iPlayer] = self.getAggressiveness(iPlayer)
                self.AI_Memory[iPlayer] = self.getMemory(iPlayer)
                self.AI_Intelligence[iPlayer] = self.getIntelligence(iPlayer)
                self.AI_HU_Score_Begin[iPlayer] = 0

                self.canDrawCard[iPlayer] = False
                self.canEndTurn[iPlayer] = False
                self.canPickCard[iPlayer] = False

                self.currentPlayer[iPlayer] = [iPlayer, iOpponent][self.dice.get(2, " Somnium, starting player")]
                self.turnActions[iPlayer] = [["gameStart", int(self.currentPlayer[iPlayer])]]
                self.turnActionsMovie[iPlayer] = []

		lBacks = []
		for i in range(gc.getNumInterfaceArtInfos()):
                        sArtTag = gc.getInterfaceArtInfo(i).getTag()
                        if "SOMNIUM_BACKGROUND_" in sArtTag :
                               lBacks.append(sArtTag)

                if len(lBacks) > 0 :
                        self.backGrounds[iPlayer] = lBacks[self.dice.get(len(lBacks), " Somnium, backGround Choice")]
                else :
                        self.backGrounds[iPlayer] = "MAINMENU_SLIDESHOW_LOAD"

                if gc.getGame().getActivePlayer() in [iPlayer, iOpponent]:
                        CvScreensInterface.showCorporationScreen()

                if self.gameMP[iPlayer] :
                        self.turnActionsMovie[iPlayer].append(["actionsMovieMPCalled", []])
                        self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_SHUFFLE"]])
                        self.turnActionsMovie[iPlayer].append(["wait", [self.S_1]])
                        self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                        self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_NEW_TURN"]])
                        self.turnActionsMovie[iPlayer].append(["wait", [self.S_2]])
                        self.turnActionsMovie[iPlayer].append(["canDrawCard", []])
                        self.turnActionsMovie[iPlayer].append(["endMovieMP", []])
                        if gc.getGame().getActivePlayer() in [iPlayer, iOpponent]:
                                self.updateScreen("launchTurnMovie", copy.deepcopy(self.turnActionsMovie[iPlayer]))
                        self.turnActionsMovie[iPlayer] = []

                else :

                        self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_SHUFFLE"]])
                        self.turnActionsMovie[iPlayer].append(["wait", [self.S_1]])
                        self.turnActionsMovie[iPlayer].append(["updateInfoPanel", self.getLastFiveActions(iPlayer)])
                        if self.currentPlayer[iPlayer] == self.playerLeft[iPlayer] :
                                self.turnActionsMovie[iPlayer].append(["playSound", ["AS2D_SOMNIUM_NEW_TURN"]])
                                self.turnActionsMovie[iPlayer].append(["wait", [self.S_2]])
                                self.turnActionsMovie[iPlayer].append(["canDrawCard", []])
                        else :
                                self.turnActionsMovie[iPlayer].append(["canEndTurn", []])

                        if gc.getGame().getActivePlayer() == iPlayer :
                                self.updateScreen("launchTurnMovie", copy.deepcopy(self.turnActionsMovie[iPlayer]))
                        self.turnActionsMovie[iPlayer] = []

        def endGame(self, iPlayer, iLooser = -1):
                if not self.playerInGame[iPlayer] : return #game already finished ?

                if iLooser == -1 : iLooser = self.getLooser(iPlayer)

                pLeftPlayer = gc.getPlayer(self.playerLeft[iPlayer])
                pRightPlayer = gc.getPlayer(self.playerRight[iPlayer])

                if iLooser == -1 : #Draw
                        if pLeftPlayer.isAlive() :
                                CyInterface().addMessage(self.playerLeft[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_DRAW_GAME", (pRightPlayer.getName(), )), '', 1, '', ColorTypes(7), -1, -1, False, False)
                        else :
                                CyInterface().addMessage(self.playerLeft[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_PLAYER_DEAD", ()), '', 1, '', ColorTypes(7), -1, -1, False, False)

                        if self.gameMP[iPlayer] :
                                if pRightPlayer.isAlive() :
                                        CyInterface().addMessage(self.playerRight[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_DRAW_GAME", (pLeftPlayer.getName(), )), '', 1, '', ColorTypes(7), -1, -1, False, False)
                                else :
                                        CyInterface().addMessage(self.playerRight[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_PLAYER_DEAD", ()), '', 1, '', ColorTypes(7), -1, -1, False, False)

                elif iLooser == self.playerLeft[iPlayer] :
                        if self.Antes[iPlayer] > 0 :
                                if pLeftPlayer.isAlive() :
                                        pLeftPlayer.setGold(max(0, pLeftPlayer.getGold() - self.Antes[iPlayer]))
                                if pRightPlayer.isAlive() :
                                        if pRightPlayer.isHuman() :
                                                pRightPlayer.setGold(pRightPlayer.getGold() + self.Antes[iPlayer])
                                
                                if pLeftPlayer.isAlive() :
                                        CyInterface().addMessage(self.playerLeft[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_LOOSE_GOLD", (pRightPlayer.getName(), self.Antes[iPlayer])), '', 1, '', ColorTypes(7), -1, -1, False, False)
                                else :
                                        CyInterface().addMessage(self.playerLeft[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_PLAYER_DEAD", ()), '', 1, '', ColorTypes(7), -1, -1, False, False)

                                if pRightPlayer.isAlive() :
                                        if pRightPlayer.isHuman() :
                                                if pRightPlayer.isAlive() :
                                                        CyInterface().addMessage(self.playerRight[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_WIN_GOLD", (pLeftPlayer.getName(), self.Antes[iPlayer])), '', 1, '', ColorTypes(7), -1, -1, False, False)
                                                else :
                                                        CyInterface().addMessage(self.playerRight[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_PLAYER_DEAD", ()), '', 1, '', ColorTypes(7), -1, -1, False, False)
                        elif self.Antes[iPlayer] == -1 :
                                if not pLeftPlayer.isAlive() :
                                        CyInterface().addMessage(self.playerLeft[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_PLAYER_DEAD", ()), '', 1, '', ColorTypes(7), -1, -1, False, False)
                                elif pRightPlayer.isAlive() :
                                        CyInterface().addMessage(self.playerLeft[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_LOOSE_RELATION", (pRightPlayer.getName(), pRightPlayer.getName())), '', 1, '', ColorTypes(7), -1, -1, False, False)
                                        pRightPlayer.AI_changeMemoryCount(self.playerLeft[iPlayer], MemoryTypes.MEMORY_SOMNIUM_NEGATIVE, 1)
                                else :
                                        CyInterface().addMessage(self.playerLeft[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_PLAYER_DEAD_PLAYER", (pRightPlayer.getName(), )), '', 1, '', ColorTypes(7), -1, -1, False, False)

                else :
                        if self.Antes[iPlayer] > 0 :
                                if pRightPlayer.isAlive() :
                                        if pRightPlayer.isHuman() :
                                                pRightPlayer.setGold(max(0, pRightPlayer.getGold() - self.Antes[iPlayer]))
                                if pLeftPlayer.isAlive() :
                                        pLeftPlayer.setGold(pLeftPlayer.getGold() + self.Antes[iPlayer])
                                
                                if pLeftPlayer.isAlive() :
                                        CyInterface().addMessage(self.playerLeft[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_WIN_GOLD", (pRightPlayer.getName(), self.Antes[iPlayer])), '', 1, '', ColorTypes(7), -1, -1, False, False)
                                else :
                                        CyInterface().addMessage(self.playerLeft[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_PLAYER_DEAD", ()), '', 1, '', ColorTypes(7), -1, -1, False, False)

                                if pRightPlayer.isAlive() :
                                        if pRightPlayer.isHuman() :
                                                if pRightPlayer.isAlive() :
                                                        CyInterface().addMessage(self.playerRight[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_LOOSE_GOLD", (pLeftPlayer.getName(), self.Antes[iPlayer])), '', 1, '', ColorTypes(7), -1, -1, False, False)
                                                else :
                                                        CyInterface().addMessage(self.playerRight[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_PLAYER_DEAD", ()), '', 1, '', ColorTypes(7), -1, -1, False, False)
                        elif self.Antes[iPlayer] == -1 :
                                if not pLeftPlayer.isAlive() :
                                        CyInterface().addMessage(self.playerLeft[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_PLAYER_DEAD", ()), '', 1, '', ColorTypes(7), -1, -1, False, False)
                                elif pRightPlayer.isAlive() :
                                        CyInterface().addMessage(self.playerLeft[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_WIN_RELATION", (pRightPlayer.getName(), pRightPlayer.getName())), '', 1, '', ColorTypes(7), -1, -1, False, False)
                                        pRightPlayer.AI_changeMemoryCount(self.playerLeft[iPlayer], MemoryTypes.MEMORY_SOMNIUM_POSITIVE, 1)
                                else :
                                        CyInterface().addMessage(self.playerLeft[iPlayer], True, 25, CyTranslator().getText("TXT_KEY_SOMNIUM_PLAYER_DEAD_PLAYER", (pRightPlayer.getName(), )), '', 1, '', ColorTypes(7), -1, -1, False, False)

                if  gc.getGame().getActivePlayer() in [self.playerLeft[iPlayer], self.playerRight[iPlayer]]:
                        self.updateScreen("closeScreen")
                                
                self.Antes[iPlayer] = 0
                self.playerInGame[iPlayer] = False
                if self.gameMP[iPlayer] : self.playerInGame[self.playerRight[iPlayer]] = False
                self.gameMP[iPlayer] = False
                self.deck[iPlayer] = []
                self.bankLeft[iPlayer] = []
                self.bankRight[iPlayer] = []
                self.drawCards[iPlayer] = []
                self.turnActions[iPlayer] = []
                self.turnActionsMovie[iPlayer] = []
                self.gameState[iPlayer] = ""
                self.playerLeft[iPlayer] = -1
                self.playerRight[iPlayer] = -1
                self.canDrawCard[iPlayer] = False
                self.canEndTurn[iPlayer] = False
                self.canPickCard[iPlayer] = False
                self.currentPlayer[iPlayer] = -1
                self.backGrounds[iPlayer] = ""
                self.AI_Aggression[iPlayer] = 0
                self.AI_Memory[iPlayer] = 0
                self.AI_Intelligence[iPlayer] = 0
                self.AI_HU_Score_Begin[iPlayer] = 0

        def getLooser(self, iPlayer):
                iLeftScore = self.getLeftScore(iPlayer)
                iRightScore = self.getRightScore(iPlayer)

                if iLeftScore < iRightScore :
                        return self.playerLeft[iPlayer]
                elif iLeftScore > iRightScore :
                        return self.playerRight[iPlayer]
                return -1

        def getLeftPlayer(self, iActivePlayer):
                if iActivePlayer in self.playerLeft :
                        return copy.copy(iActivePlayer)
                else :
                        return self.playerRight.index(iActivePlayer)

        def getRightPlayer(self, iActivePlayer):
                iPlayerLeft = self.getLeftPlayer(iActivePlayer)
                return copy.deepcopy(self.playerRight[iPlayerLeft])

        def getBackGround(self, iPlayer):
                return copy.deepcopy(self.backGrounds[iPlayer])
                
        def getCardsLeft(self, iPlayer):
                return copy.deepcopy(self.deck[iPlayer])

        def getCenterCards(self, iPlayer):
                return copy.deepcopy(self.drawCards[iPlayer])

        def getMPGame(self, iPlayer):
                return copy.deepcopy(self.gameMP[iPlayer])

        def getActions(self, iPlayer):
                return copy.deepcopy(self.turnActions[iPlayer])

        def getLastFiveActions(self, iPlayer):
                if len(self.turnActions[iPlayer]) <= 5 : return copy.deepcopy(self.turnActions[iPlayer])
                else : return copy.deepcopy(self.turnActions[iPlayer][-5:])

        def getOtherBank(self, iPlayer, iPlayerR):
                if iPlayerR == self.playerLeft[iPlayer] : return self.bankRight[iPlayer]
                return self.bankLeft[iPlayer]

        def getScoreBank(self, iPlayer):
                iScore = 0
                for card in self.drawCards[iPlayer] :
                        iDelta = 0
                        if card[0] < 10 :
                                bestCardType = self.getBestCardRight(iPlayer, card[0])
                                if bestCardType != -1 :
                                        if card[1] > bestCardType[1] :
                                                iDelta = card[1] - bestCardType[1]
                                else :
                                        iDelta = card[1]
                        iScore += iDelta
                return iScore

        def getLeftScore(self, iPlayer):
                iScore = 0
                for iType in range(10):
                        bestCardType = self.getBestCardLeft(iPlayer, iType)
                        if bestCardType == -1 : continue
                        iScore += bestCardType[1]
                return iScore

        def getBestCardLeft(self, iPlayer, iType):
                bestCard = -1
                iLevel = 0
                for card in self.bankLeft[iPlayer]:
                        if (card[0] == iType) and (card[1] > iLevel) :
                                bestCard = card
                                iLevel = card[1]
                return copy.deepcopy(bestCard)

        def getRightScore(self, iPlayer):
                iScore = 0
                for iType in range(10):
                        bestCardType = self.getBestCardRight(iPlayer, iType)
                        if bestCardType == -1 : continue
                        iScore += bestCardType[1]
                return iScore

        def getBestCardRight(self, iPlayer, iType):
                bestCard = -1
                iLevel = 0
                for card in self.bankRight[iPlayer]:
                        if (card[0] == iType) and (card[1] > iLevel) :
                                bestCard = card
                                iLevel = card[1]
                return copy.deepcopy(bestCard)

        def doTurn(self):
                for iAIPlayer in range(gc.getMAX_CIV_PLAYERS()) :
                        pAIPlayer = gc.getPlayer(iAIPlayer)
                        if pAIPlayer.isHuman() : continue
                        for iHUPlayer in range(gc.getMAX_CIV_PLAYERS()) :
                                pHUPlayer = gc.getPlayer(iHUPlayer)
                                if not pHUPlayer.isHuman() : continue

                                if pAIPlayer.AI_getMemoryCount(iHUPlayer, MemoryTypes.MEMORY_SOMNIUM_DELAY) <= 0 :
                                        while pAIPlayer.AI_getMemoryCount(iHUPlayer, MemoryTypes.MEMORY_SOMNIUM_POSITIVE) > 0 :
                                                pAIPlayer.AI_changeMemoryCount(iHUPlayer, MemoryTypes.MEMORY_SOMNIUM_POSITIVE, -1)
                                        while pAIPlayer.AI_getMemoryCount(iHUPlayer, MemoryTypes.MEMORY_SOMNIUM_NEGATIVE) > 0 :
                                                pAIPlayer.AI_changeMemoryCount(iHUPlayer, MemoryTypes.MEMORY_SOMNIUM_NEGATIVE, -1)

