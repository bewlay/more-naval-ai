## Copyright (c) 2005-2006, Gillmer J. Derge.

## This file is part of Civilization IV Alerts mod.
##
## Civilization IV Alerts mod is free software; you can redistribute
## it and/or modify it under the terms of the GNU General Public
## License as published by the Free Software Foundation; either
## version 2 of the License, or (at your option) any later version.
##
## Civilization IV Alerts mod is distributed in the hope that it will
## be useful, but WITHOUT ANY WARRANTY; without even the implied
## warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
## See the GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Civilization IV Alerts mod; if not, write to the Free
## Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
## 02110-1301 USA
    
__version__ = "$Revision: 1.4 $"
# $Source: /usr/local/cvsroot/Civ4lerts/src/main/python/CvCustomEventManager.py,v $

import CvEventManager
import CvConfigParser
# --------- Revolution mod (1/2) -------------
import RevolutionInit
import Civ4lerts

class CvCustomEventManager(CvEventManager.CvEventManager, object):

    """Extends the standard event manager by adding support for multiple
    handlers for each event.
    
    Methods exist for both adding and removing event handlers.  A set method 
    also exists to override the default handlers.  Clients should not depend 
    on event handlers being called in a particular order.
    
    This approach works best with mods that have implemented the design
    pattern suggested on Apolyton by dsplaisted.
    
    http://apolyton.net/forums/showthread.php?s=658a68df728b2719e9ebfe842d784002&threadid=142916
    
    The example given in the 8th post in the thread would be handled by adding
    the following lines to the CvCustomEventManager constructor.  The RealFort,
    TechConquest, and CulturalDecay classes can remain unmodified.
    
        self.addEventHandler("unitMove", rf.onUnitMove)
        self.addEventHandler("improvementBuilt", rf.onImprovementBuilt)
        self.addEventHandler("techAcquired", rf.onTechAcquired)
        self.addEventHandler("cityAcquired", tc.onCityAcquired)
        self.addEventHandler("EndGameTurn", cd.onEndGameTurn)
        
    Note that the naming conventions for the event type strings vary from event
    to event.  Some use initial capitalization, some do not; some eliminate the
    "on..." prefix used in the event handler function name, some do not.  Look
    at the unmodified CvEventManager.py source code to determine the correct
    name for a particular event.
    
    Take care with event handlers that also extend CvEventManager.  Since
    this event manager handles invocation of the base class handler function,
    additional handlers should not also call the base class function themselves.

    """

    def __init__(self, *args, **kwargs):
        super(CvCustomEventManager, self).__init__(*args, **kwargs)
        # map the initial EventHandlerMap values into the new data structure
        for eventType, eventHandler in self.EventHandlerMap.iteritems():
            self.setEventHandler(eventType, eventHandler)
        # --> INSERT EVENT HANDLER INITIALIZATION HERE <--

        # --------- Revolution mod (2/2) -------------
        if( game.isOption(GameOptionTypes.GAMEOPTION_PUPPET_STATES_AND_REVOLUTIONS) ):
	        revConfigFile = "Revolution.ini"
  	      RevolutionInit.RevolutionInit( self, revConfigFile )
        
        Civ4lerts.Civ4lerts( self )

    def addEventHandler(self, eventType, eventHandler):
        """Adds a handler for the given event type.
        
        A list of supported event types can be found in the initialization 
        of EventHandlerMap in the CvEventManager class.
        
        Throws LookupError if the eventType is not valid.

        """
        
        if eventType not in self.EventHandlerMap:
            raise LookupError(eventType)
        if( not eventHandler in self.EventHandlerMap[eventType] ) :
            self.EventHandlerMap[eventType].append(eventHandler)

    def removeEventHandler(self, eventType, eventHandler):
        """Removes a handler for the given event type.
        
        A list of supported event types can be found in the initialization 
        of EventHandlerMap in the CvEventManager class.  It is an error if 
        the given handler is not found in the list of installed handlers.
        
        Throws LookupError if the eventType is not valid.

        """
        if eventType not in self.EventHandlerMap:
            raise LookupError(eventType)
        self.EventHandlerMap[eventType].remove(eventHandler)
    
    def setEventHandler(self, eventType, eventHandler):
        """Removes all previously installed event handlers for the given 
        event type and installs a new handler.
        
        A list of supported event types can be found in the initialization 
        of EventHandlerMap in the CvEventManager class.  This method is 
        primarily useful for overriding, rather than extending, the default 
        event handler functionality.
        
        Throws LookupError if the eventType is not valid.

        """
        if eventType not in self.EventHandlerMap:
            raise LookupError(eventType)
        self.EventHandlerMap[eventType] = [eventHandler]
    
    def setPopupHandler(self, eventType, popupHandler):
        """Removes all previously installed popup handlers for the given 
        event type and installs a new handler.
        
        The eventType should be an integer.  It must be unique with respect
        to the integers assigned to built in events.  The popupHandler should
        be a list made up of (name, beginFunction, applyFunction).  The name
        is used in debugging output.  The begin and apply functions are invoked
        by beginEvent and applyEvent, respectively, to manage a popup dialog
        in response to the event.

        """
        self.Events[eventType] = popupHandler

    def handleEvent(self, argsList):
        """Handles events by calling all installed handlers."""
        self.origArgsList = argsList
        flagsIndex = len(argsList) - 6
        self.bDbg, self.bMultiPlayer, self.bAlt, self.bCtrl, self.bShift, self.bAllowCheats = argsList[flagsIndex:]
        eventType = argsList[0]
        return {
            "kbdEvent": self._handleConsumableEvent,
            "mouseEvent": self._handleConsumableEvent,
            "OnSave": self._handleOnSaveEvent,
            "OnLoad": self._handleOnLoadEvent
        }.get(eventType, self._handleDefaultEvent)(eventType, argsList[1:])

    def _handleDefaultEvent(self, eventType, argsList):
        if self.EventHandlerMap.has_key(eventType):
            for eventHandler in self.EventHandlerMap[eventType]:
                # the last 6 arguments are for internal use by handleEvent
                eventHandler(argsList[:len(argsList) - 6])

    def _handleConsumableEvent(self, eventType, argsList):
        """Handles events that can be consumed by the handlers, such as
        keyboard or mouse events.
        
        If a handler returns non-zero, processing is terminated, and no 
        subsequent handlers are invoked.

        """
        if self.EventHandlerMap.has_key(eventType):
            for eventHandler in self.EventHandlerMap[eventType]:
                # the last 6 arguments are for internal use by handleEvent
                result = eventHandler(argsList[:len(argsList) - 6])
                if (result > 0):
                    return result
        return 0

    # TODO: this probably needs to be more complex
    def _handleOnSaveEvent(self, eventType, argsList):
        """Handles OnSave events by concatenating the results obtained
        from each handler to form an overall consolidated save string.

        """
        result = ""
        if self.EventHandlerMap.has_key(eventType):
            for eventHandler in self.EventHandlerMap[eventType]:
                # the last 6 arguments are for internal use by handleEvent
                result = result + eventHandler(argsList[:len(argsList) - 6])
        return result

    # TODO: this probably needs to be more complex
    def _handleOnLoadEvent(self, eventType, argsList):
        """Handles OnLoad events."""
        return self._handleDefaultEvent(eventType, argsList)
