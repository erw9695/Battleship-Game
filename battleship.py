"""
Ethan Wong
Spring 2022
battleship.py
"""
import random

def boardCoordToNumCoord(boardCoord):
    """
    boardCoordToNumCoord() takes a gameboard coordinate (formatted letter + number from 1-10) and converted it into a
    numeric coordinate (tuple of values from 0-9).
    :param boardCoord: String representing the gameboard coordinate.
    :return: Tuple representing the numeric coordinate.
    """
    if isinstance(boardCoord,str):
        return (ord(boardCoord[0])-65,int(boardCoord[1:])-1)

class Ship:
    """
    Ship class represents a ship with data on the size and locations on the gameboard the ship occupies.
    """
    def __init__(self,size):
        # Size represents not only the number of tiles occupied, but the ship type as each type has a unique size.
        self.size = size
        """
        Locations set represents the coordinates occupied by the ship.  This set is also used to determine if the ship
        has been hit by the opponent.  Gameboard.board only stores opponent misses and coordinates with ships on them.  
        If a ship coordinate is present in Gameboard.board but not Ship.locations, that means it has been struck.  When
        locations is empty, the ship has sunk.
        """
        self.locations = set()

class Gameboard:
    """
    Gameboard class holds all of the data for a player's gameboard.
    """
    def __init__(self,player):
        # Player name.
        self.player = player
        # Board represent's your gameboard.  The only things stored are opponent misses and coordinates with Ship objects on them.
        self.board = {}
        # firedOn represent's your actions on your opponent's gameboard.  Only hits ('X') and misses ('O') are kept track of.
        self.firedOn = {}
        self.remainingShips = 7

    def validShipLocation(self,listOfCoordinates):
        """
        Determines if a ship can be placed at these coordinates.
        :param listOfCoordinates: List of potential coordinates for a new ship.
        :return: True if we can place the ship, false otherwise (coordinate is occupied by another ship).
        """
        for i in listOfCoordinates:
            if i in self.board:
                return False
        return True

    def addShip(self,listOfCoordinates):
        """
        Adds a new Ship instance at the provided list of coordinates.
        :param listOfCoordinates: List of coordinates for the new ship.
        :return: True if successful, false otherwise.
        """
        newShip = Ship(len(listOfCoordinates))
        # If the ship can be added without overlapping with an existing ship...
        if self.validShipLocation(listOfCoordinates):
            for i in listOfCoordinates:
                # (0-9,0-9) -> Ship()
                self.board[i] = newShip
                newShip.locations.add(i)
            return True
        else:
            return False

    def fireAtTarget(self,target):
        """
        Handles actions by your opponent on your gameboard.  Target represents the coordinate they want to fire at.
        :param target: Coordinate representing the target.  Tuple of indices from 0-9.
        :return: String representing the result of the action or an integer representing the ship's size if it sank.
        "Hit" if it hit ia ship, "Miss" if it didn't hit a ship, or "Repeat" if the user has already fired at this spot.
        """
        # If the target is in the board, then it's either a ship or an 'O' from a previous miss.
        if target in self.board:
            if isinstance(self.board[target],Ship):
                # If the target is in the Ship instance's set, then it's a hit.
                if target in self.board[target].locations:
                    self.board[target].locations.remove(target)
                    # If the set is empty, we just sank the ship!
                    if len(self.board[target].locations) == 0:
                        self.remainingShips -=1
                        return self.board[target].size
                    return "Hit"
                else:
                    return "Repeat"
            else:
                return "Repeat"
        else:
            self.board[target] = " O "
            return "Miss"

    def printGameboard(self):
        """
        Print the current gameboard.
        :return: None.
        """
        print("Player "+str(self.player)+"'s Gameboard")
        print("===============================================================")
        print("     1     2     3     4     5     6     7     8     9     10")
        for row in range(10):
            for column in range(10):
                if column == 0:
                    print(chr(row+65),end=" |")
                getFiredOnContents = self.firedOn.get((row,column)," ")
                print(" {} |".format(" "+getFiredOnContents+" "),end="")
            print()
        print("===============================================================")
        print("     1     2     3     4     5     6     7     8     9     10")
        for row in range(10):
            for column in range(10):
                if column == 0:
                    print(chr(row+65),end=" |")
                getBoardContents = self.board.get((row,column),"   ")
                if isinstance(getBoardContents,Ship):
                    if (row,column) in getBoardContents.locations:
                        getBoardContents = "[ ]"
                    else:
                        getBoardContents = "[#]"
                print(" {} |".format(getBoardContents),end="")
            print()
        print()

class autoCoordinate:
    """
    autoCoordinate class represents a coordinate and is only used whenever the player is an NPC.  This is used when we
    queue additional coordinate to search for another hit.
    """
    def __init__(self,coordinate):
        self.coordinate = coordinate
        """
        Direction represents where this coordinate is relative to the previous coordinate.  This is used to identify the
        direction in which the NPC should continue firing at if we have multiple hits as ships can only be either
        horizontal or vertical so if we have two hits we know the rest of the ship must be in this direction.
        """
        self.direction = None

    def identifyNextCoordinate(self):
        """
        Identify the next coordinate based on this coordinate.
        :return: Coordinate representing the next coordinate in the same direction as this coordinate.
        """
        value = boardCoordToNumCoord(self.coordinate)
        if self.direction == "N":
            nextCoordinate = (value[0]-1,value[1])
        elif self.direction == "E":
            nextCoordinate = (value[0],value[1]+1)
        elif self.direction == "S":
            nextCoordinate = (value[0]+1,value[1])
        elif self.direction == "W":
            nextCoordinate = (value[0],value[1]-1)

        # If the new coordinate is within the limits of the gameboard, return it.
        if (nextCoordinate[0] >= 0 and nextCoordinate[0] <= 9) and (nextCoordinate[1] >= 0 and nextCoordinate[1] <= 9):
            return chr(nextCoordinate[0]+65)+str(nextCoordinate[1]+1)
        return False

class simulatedQueue:
    """
    simulatedQueue class is used to simulate the FIFO nature of a queue.  We use this whenever we queue additional coordinates
    to search for hits.  Used only in games involving NPC.
    """
    def __init__(self):
        self.queue = []

    def enqueue(self,value):
        """
        Add the value to the queue at the end.
        :param value: Value to add to the queue.
        :return: None.
        """
        self.queue.append(value)

    def dequeue(self):
        """
        Remove the first value in the queue at the front.
        :return: First value in the queue.
        """
        return self.queue.pop(0)

    def __len__(self):
        return len(self.queue)

def playerSelectionInput():
    """
    playerSelectionInput() will prompt the user for the number of players they want to play the game wtih.  A zero-person
    game will be a game between two NPC's, a one-person game will be a game between a real player and one NPC, and a two-player
    game will be a game between two real players.
    :return: Integer representing player count.
    """
    while True:
        print("Please select the game mode.  Enter '0' for a zero-person game, '1' for a one-person game, or '2' for a two-player game.")
        try:
            playersSelectionInput = int(input("Enter Players Count: "))
            print()
            if playersSelectionInput == 0 or playersSelectionInput == 1 or playersSelectionInput == 2:
                return playersSelectionInput
            print("Sorry, we can't have a game with "+str(playersSelectionInput)+" players.  Please try again.\n")
        except ValueError:
            print("Sorry, that input was invalid.  Please try again.\n")

def directionToEndCoordinates(shipSize,startCoordinate,direction):
    """
    directionToEndCoordinates() is used to take a start coordinate and direction to face the ship during the game's set up
    to determine the end coordinate point for the ship.
    :param shipSize: Integer representing ship size.
    :param startCoordinate: String representing the user's input for the start of the ship.
    :param direction: String representing the direction the user wants the ship to face.
    :return:
    """
    inputDirection = direction.capitalize()
    if inputDirection == "N":
        return chr((startCoordinate[0]+65)+(shipSize-1))+str(startCoordinate[1]+1)
    elif inputDirection == "E":
        return chr(startCoordinate[0]+65)+str((startCoordinate[1]-(shipSize-1)+1))
    elif inputDirection == "S":
        return chr((startCoordinate[0]-(shipSize-1))+65)+str(startCoordinate[1]+1)
    elif inputDirection == "W":
        return chr(startCoordinate[0]+65)+str((startCoordinate[1]+(shipSize-1))+1)
    return False

def validCoordinate(coordinate):
    """
    validCoordinate() determines if a coordinate is valid.
    :param coordinate: String representing gameboard coordinate.
    :return: Tuple representing number coordinates if valid, False otherwise.
    """
    if isinstance(coordinate,str):
        firstChar = ord(coordinate[0].capitalize())-65
        if firstChar >= 0 and firstChar <= 9:
            column = coordinate[1:]
            if column.isnumeric():
                lastChar = int(column)-1
                if lastChar >= 0 and lastChar <= 9:
                    return (firstChar,lastChar)
    return False

def identifyCoordinates(start,end):
    """
    identifyCoordinates() takes start and ending points and identifies all coordinate points in between.
    :param start: Tuple representing number coordinate of the starting point.
    :param end: Tuple representing number coordinate of the ending point.
    :return: List of number coordinates from start to end point inclusive.
    """
    # If the coordinates are horizontal ...
    if start[0] == end[0]:
        startPoint = min(start[1],end[1])
        endPoint = max(start[1],end[1])
        return [(start[0],i) for i in range(startPoint,endPoint+1)]
    # If the coordinates are vertical ...
    elif start[1] == end[1]:
        startPoint = min(start[0],end[0])
        endPoint = max(start[0],end[0])
        return [(i,start[1]) for i in range(startPoint,endPoint+1)]

def validateAndAddShip(startCoordinate,direction,shipSize,gameboard):
    """
    validateAndAddShip() takes player inputs for a new ship and confirms that it's a valid input before adding it to
    their gameboard.
    :param startCoordinate: String representing gameboard coordinate.
    :param direction: String representing the direction the ship should face.
    :param shipSize: Integer representing the number of coordinates occupied by the ship.
    :param gameboard: Gameboard instance.
    :return: True if it was successfully added, false otherwise.
    """
    startValid = validCoordinate(startCoordinate)
    if startValid:
        # If start coordinate was valid, generate the end coordinate with directionToEndCoordinates() and confirm it's valid.
        endValid = validCoordinate(directionToEndCoordinates(shipSize,startValid,direction))
        if endValid:
            # Get a list of spaces the ship occupies.
            shipSpaces = identifyCoordinates(startValid,endValid)
            if len(shipSpaces) == shipSize:
                # Add ship to the gameboard.
                shipAdded = gameboard.addShip(shipSpaces)
                if shipAdded:
                    return True
    return False

def shipLocationInput(shipSize,gameboard):
    """
    shipLocationInput() prompts user for the location of a ship.
    :param shipSize: Integer representing ship size.
    :param gameboard: Gameboard instance for player.
    :return: None.
    """
    shipName = {1:"submarine",2:"destroyer",3:"cruiser",4:"battleship",5:"aircraft carrier"}
    while True:
        print("Player "+str(gameboard.player)+", please select a start coordinate and direction to place the "+shipName[shipSize]+".")
        print("N for north, E for east, S for south, W for west.")

        start = input("Enter Start Coordinate: ")
        direction = input("Enter Direction: ")
        print()

        if direction.isalpha() and len(direction) == 1:
            # After receiving inputs, try to add this ship.
            success = validateAndAddShip(start,direction,shipSize,gameboard)
            if success:
                break
        print("These are invalid coordinates.  Please try again.\n")

def randomCoordinate():
    """
    randomCoordinate() generates a random coordinate.
    :return: String representing gameboard coordinate.
    """
    return chr(random.randint(0,9)+65)+str(random.randint(1,10))

def handleFireAtTarget(target,aggressorGameboard,targetGameboard):
    """
    handleFireAtTarget() is used to call Gameboard.fireAtTarget() to fire at a coordinate prints out the results.
    :param target: Tuple representing numeric coordinate.
    :param aggressorGameboard: Gameboard instance for the aggressor.
    :param targetGameboard: Gameboard instance for the target.
    :return: True if hit or miss, false otherwise.
    """
    # shipName is used to convert a ship's size into it's name.
    shipName = {1:"submarine",2:"destroyer",3:"cruiser",4:"battleship",5:"aircraft carrier"}
    validTarget = validCoordinate(target)
    if validTarget:
        # Attempt to fire at the target and store the result.
        result = targetGameboard.fireAtTarget(validTarget)
        if result != "Repeat":
            boardCoord = boardCoordToNumCoord(target)
            if result == "Hit":
                aggressorGameboard.firedOn[boardCoord] = "X"
                print("Hit!  You've hit a ship!\n")
            elif result == "Miss":
                aggressorGameboard.firedOn[boardCoord] = "O"
                print("You've missed!\n")
            elif isinstance(result,int):
                aggressorGameboard.firedOn[boardCoord] = "X"
                print("You've sunk a "+shipName[result]+"!\n")
            return True
        else:
            print("You've already fired at this target.  Please try again.\n")
            return False
    return False

def userFireAtTarget(aggressorGameboard,targetGameboard):
    """
    userFireAtTarget() is used to allow the user to decide on a target to fire at.
    :param aggressorGameboard: Gameboard instance of the aggressor.
    :param targetGameboard: Gameboard instance of the target.
    :return: None.
    """
    while True:
        print("Player "+str(aggressorGameboard.player)+", please select a coordinate to fire at.")
        target = input("Enter Coordinate:")
        target = target.capitalize()
        result = handleFireAtTarget(target,aggressorGameboard,targetGameboard)
        # If the attack was successful, break out of the infinite loop.
        if result:
            break

def identifyAdjacentCoordinates(coordinate):
    """
    identifyAdjacentCoordinates() identifies the coordinates adjacent to the coordinate one square away.
    :param coordinate: String representing gameboard coordinate.
    :return: List of gameboard coordinates.
    """
    value = boardCoordToNumCoord(coordinate)
    output = []
    if (value[0]-1) >= 0 and (value[0]-1) <= 9:
        output.append(chr((value[0]-1)+65)+str(value[1]+1))
    if (value[0]+1) >= 0 and (value[0]+1) <= 9:
        output.append(chr((value[0]+1)+65)+str(value[1]+1))
    if (value[1]-1) >= 0 and (value[1]-1) <= 9:
        output.append(chr(value[0]+65)+str((value[1]-1)+1))
    if (value[1]+1) >= 0 and (value[1]+1) <= 9:
        output.append(chr(value[0]+65)+str((value[1]+1)+1))
    return output

def identifyDirection(coordinate,centerCoordinate):
    """
    identifyDirection() identifies what direction the new coordinate is relative to the center coordinate.  For example,
    if a coordinate was at A1 while the center coordinate was at B1, the coordinate will be north of the center coordinate.
    This is used by the autoCoordinate class.
    :param coordinate: String representing gameboard coordinate.
    :param centerCoordinate: String representing the center gamebaord coordinate.
    :return: String representing the direction.
    """
    coordinateValue = boardCoordToNumCoord(coordinate)
    centerCoordinateValue = boardCoordToNumCoord(centerCoordinate)

    # If both coordinates are horizontal ...
    if coordinateValue[0] == centerCoordinateValue[0]:
        if coordinateValue[1] > centerCoordinateValue[1]:
            return "E"
        elif coordinateValue[1] < centerCoordinateValue[1]:
            return "W"
    # If both coordinates are vertical ...
    elif coordinateValue[1] == centerCoordinateValue[1]:
        if coordinateValue[0] < centerCoordinateValue[0]:
            return "N"
        elif coordinateValue[0] > centerCoordinateValue[0]:
            return "S"

def autoFireAtTarget(aggressorGameboard,aggressorQueue,targetGameboard):
    """
    autoFireAtTarget() is used by NPC players to choose a gameboard target to fire at.
    :param aggressorGameboard: Gameboard instance for the aggressor.
    :param aggressorQueue: simulatedQueue instance for the aggressor.
    :param targetGameboard: Gameboard instance for the target.
    :return: None.
    """
    while True:
        autoCoord = None
        # If the queue of targets to attack is empty, arbitrarily pick a coordinate.
        if len(aggressorQueue) == 0:
            target = randomCoordinate()
        # Otherwise get the next coordinate in the queue.
        else:
            autoCoord = aggressorQueue.dequeue()
            target = autoCoord.coordinate
        targetBoardCoord = boardCoordToNumCoord(target)
        # If we didn't already choose this coordinate ...
        if targetBoardCoord not in aggressorGameboard.firedOn:
            print("Player "+str(aggressorGameboard.player)+" is firing at "+target+"!")
            # Fire at this target.
            result = handleFireAtTarget(target,aggressorGameboard,targetGameboard)
            if result:
                # If firing at this target is results in a hit ...
                if aggressorGameboard.firedOn[targetBoardCoord] == "X":
                    # If we hit this target from the queue, identify the next coordinate in the same direction and enqueue.
                    if autoCoord is not None:
                        nextCoordinate = autoCoord.identifyNextCoordinate()
                        if nextCoordinate is not False:
                            newCoord = autoCoordinate(nextCoordinate)
                            newCoord.direction = autoCoord.direction
                            aggressorQueue.enqueue(newCoord)
                    # If this was an arbitrarily chosen target, add all adjacent neighbors to the queue to identify the next hit.
                    else:
                        neighbors = identifyAdjacentCoordinates(target)
                        for i in neighbors:
                            coord = autoCoordinate(i)
                            coord.direction = identifyDirection(i,target)
                            aggressorQueue.enqueue(coord)
                break

def runBattleship(playerOneGameboard,playerTwoGameboard,players):
    """
    runBattleship() runs the game based on the players specified at setup.
    :param playerOneGameboard: Gameboard instance for player one.
    :param playerTwoGameboard: Gameboard instance for player two.
    :param players: Integer representing the number of players in the game.
    :return: None.
    """
    print("=======================================================================================================")
    print("Beginning game ...")
    print("=======================================================================================================\n")

    if players == 0:
        autoOneHitQueue = simulatedQueue()
    if players <= 1:
        autoTwoHitQueue = simulatedQueue()

    # Loop while no one has won.
    while playerOneGameboard.remainingShips > 0 and playerTwoGameboard.remainingShips > 0:
        if players == 0:
            autoFireAtTarget(playerOneGameboard,autoOneHitQueue,playerTwoGameboard)
            autoFireAtTarget(playerTwoGameboard,autoTwoHitQueue,playerOneGameboard)
        elif players == 1:
            playerOneGameboard.printGameboard()
            userFireAtTarget(playerOneGameboard,playerTwoGameboard)
            autoFireAtTarget(playerTwoGameboard,autoTwoHitQueue,playerOneGameboard)
        elif players == 2:
            playerOneGameboard.printGameboard()
            userFireAtTarget(playerOneGameboard,playerTwoGameboard)
            playerTwoGameboard.printGameboard()
            userFireAtTarget(playerTwoGameboard,playerOneGameboard)

    if playerOneGameboard.remainingShips == 0:
        print("Player 2 has won the game!\n")
    else:
        print("Player 1 has won the game!\n")

def repeatUntilShipValidated(direction,shipSize,gameboard):
    """
    repeatUntilShipValidated() loops until the NPC's choice is accepted by the gameboard.
    :param direction: String representing the direction the ship should face.
    :param shipSize: Integer representing the ship size.
    :param gameboard: Gameboard instance for NPC.
    :return: None.
    """
    while True:
        # Start coordinate is randomly generated each time with the same direction and ship size.
        success = validateAndAddShip(randomCoordinate(),direction,shipSize,gameboard)
        if success:
            break

def userGameboardSetup(player):
    """
    userGameboardSetup() performs the setup for a real player's gameboard.
    :param player: Integer representing the player.
    :return: Gameboard instance created.
    """
    playerGameboard = Gameboard(player)
    for i in range(1,6):
        if i <= 2:
            shipLocationInput(i,playerGameboard)
            playerGameboard.printGameboard()
        shipLocationInput(i,playerGameboard)
        playerGameboard.printGameboard()
    return playerGameboard

def autoGameboardSetup(player):
    """
    autoGameboardSetup() performs the setup for a NPC's gameboard.
    :param player: Integer representing the player.
    :return: Gameboard instance created.
    """
    autoGameboard = Gameboard(player)
    direction = ["N","E","S","W"]
    for i in range(1,6):
        if i <= 2:
            repeatUntilShipValidated(direction[random.randint(0,3)],i,autoGameboard)
        repeatUntilShipValidated(direction[random.randint(0,3)],i,autoGameboard)
    return autoGameboard

def main():
    print("=======================================================================================================")
    print("Welcome to Battleship!  This is a game where you and an opponent take turns firing at each other's ship.")
    print("=======================================================================================================")

    players = playerSelectionInput()

    if players == 0:
        autoOneGameboard = autoGameboardSetup(1)
    if players <= 1:
        autoTwoGameboard = autoGameboardSetup(2)
    if players >= 1:
        playerOneGameboard = userGameboardSetup(1)
    if players == 2:
        playerTwoGameboard = userGameboardSetup(2)

    if players == 0:
        runBattleship(autoOneGameboard,autoTwoGameboard,players)
        autoOneGameboard.printGameboard()
        autoTwoGameboard.printGameboard()
    elif players == 1:
        runBattleship(playerOneGameboard,autoTwoGameboard,players)
    elif players == 2:
        runBattleship(playerOneGameboard,playerTwoGameboard,players)

if __name__ == '__main__':
    main()
