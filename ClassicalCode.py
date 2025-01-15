def spawnEvent(turn_color, activeBoard):
    """
    :param turn_color: The current color whose turn it is
    :param activeBoard: The board which contains the position of all pawns
    :return:
    """
    # Indices for the spawn points and pawns respectively
    colorSpawn = 0
    i = 0
    # Counter which keeps track of how many times the spawn has moved up by one,
    # in order to find an empty spot to spawn upon
    positionCounter = 0

    # The code belows checks if spawning is possible, if not redirects to movement
    # Other case it spawns a pawn
    # Last case it capture another pawn on the spawn and places the new pawn on the next free spot
    # Loop which goes through all color types
    for color in colorTypes:
        # Turn color
        if turn_color == color:
            # Counts the number of times pawn1 and pawn2 occur on the board
            pawn1_count = sum(1 for d in activeBoard if d is not None and d["color"] == color and d["pawn"] == 1)
            pawn2_count = sum(1 for d in activeBoard if d is not None and d["color"] == color and d["pawn"] == 2)

            # When the spawn point is empty and either pawn1 or pawn2 are NOT on the board
            # will a new spawn be available. When pawn count is 0, it means it is NOT on the board
            if activeBoard[colorSpawn] is None and (pawn1_count == 0 or pawn2_count == 0):
                # Asks if the player want to spawn a new pawn or continue with movement of an existing pawn
                ask_spawn = input("A new spawn is available, do you want to get a new pawn? (Y/N)?: ")
                ask_spawn.lower()  # Turns the input into lower case
                if ask_spawn in ["y", "yes", "ja"]:
                    # Spawns the pawn which is not yet on the board
                    if pawn1_count == 0:
                        # Spawns pawn 1
                        activeBoard[colorSpawn] = pawn_lst[i]
                        print("Pawn 1 has been spawned at the spawn point of", color)

                        # Call quantum spawn function
                        # So places the new pawn at spawn, by placing a X-Gate at the corresponding qubit
                        #new_pawn(activeBoard.index(activeBoard[colorSpawn))
                        print(activeBoard.index(activeBoard[colorSpawn]))  # Prints out position of the spawn

                    elif pawn2_count == 0:
                        # Spawns pawn 2
                        activeBoard[colorSpawn] = pawn_lst[i + 1]
                        print("Pawn 2 has been spawned at the spawn point of", color)

                        # Call quantum spawn function
                        # So places the new pawn at spawn, by placing an X-Gate at the corresponding qubit
                        #new_pawn(activeBoard.index(activeBoard[colorSpawn))
                        print(activeBoard.index(activeBoard[colorSpawn]))  # Prints out position of the spawn

                # If player does not choose to spawn, continue to movement of pawn 1/2
                else:
                    print("Continue to movement")
                    # Move pawn 1
                    if pawn1_count != 0:
                        print("Moving pawn1")
                        # TODO: Call quantum move function
                        # TODO: Check is move is allowed
                        # TODO: Move pawn from board[start] to board[end]
                        #move(board[i], board[i + d1])
                        #move(board[i], board[i + d2])
                    # Move pawn 2
                    elif pawn2_count != 0:
                        print("Moving pawn2")
                        # TODO: Call quantum move function
                        # Check if move is allowed
                        # TODO: Move pawn from board[start] to board[end]
                        #move(board[i], board[i + d1])
                        #move(board[i], board[i + d2])

            # Treats the case when the spawn point is occupied by a pawn and there are pawns
            # available for spawning
            elif activeBoard[colorSpawn] is not None and (pawn1_count == 0 or pawn2_count == 0):
                # If spawn point is occupied by same color, no spawn available
                if activeBoard[colorSpawn]["color"] == color:
                    print("No spawn is available, one of your pawns is occupying the spawn point!")
                    print("Move pawn", activeBoard[colorSpawn]["pawn"], "away from your spawn")
                    # TODO: Move pawn on board
                    # TODO: Check first if move is allowed
                    # TODO: Call quantum move to move pawn on the quantum board

                # If spawn point is occupied by enemy pawn, spawning is possible, then the enemy pawn
                # gets captured with the probability of the enemy pawn to be there
                # as the new pawn spawns with probability 1.
                # Note that in this case the new pawns spawns in the next available place
                # If there is no free place, spawning is not allowed then
                else:
                    ask_spawn = input("A new spawn is available, do you want to get a new pawn? (Y/N)?: ")
                    ask_spawn.lower()
                    if ask_spawn in ["y", "yes", "ja"]:
                        positionSpawnCamper = colorSpawn  # Saves position of the spawn camper on board
                        boardPositions = 5  # Total number of positions on board - 1
                        # Classical spawn capture
                        if activeBoard[colorSpawn]["probability"] == 1:
                            # Loops which looks for the closest valid position to spawn the new pawn
                            # Keeps looking if the subsequent position is empty, as long nonempty it keeps running
                            # as soon empty spot has been found the loop stops and the new pawn gets spawned at that
                            # position.
                            # But if the number of times the spawn is moved up by one exceeds the number required
                            # to make a full rotation, then spawning is NOT possible
                            while activeBoard[colorSpawn] is not None:
                                colorSpawn = colorSpawn + 1
                                positionCounter = positionCounter + 1
                                if positionCounter >= boardPositions:
                                    break

                            # Spawns the pawn which is not yet on the board only when there is available space
                            if pawn1_count == 0 and positionCounter < boardPositions:
                                # Spawns pawn 1
                                activeBoard[colorSpawn] = pawn_lst[i]
                                print("Pawn 1 has been spawned at the spawn point of", color)
                                print(
                                    "THE pawn which was on your spawn has been captured by the newly spawned pawn1")

                                # Spawns new pawn on the quantum circuit
                                #new_pawn(activeBoard.index(activeBoard[colorSpawn))
                                print(activeBoard.index(activeBoard[colorSpawn]))  # Prints out position of the spawn

                                # In case of classical spawn capture, the spawn camper gets banished to the shadow realm
                                activeBoard[positionSpawnCamper] = None
                                # TODO: Call quantum function which removes the spawn camper from the board
                                # remove_pawn(activeBoard.index(activeBoard[positionSpawnCamper]))

                            elif pawn2_count == 0 and positionCounter < boardPositions:
                                # Spawns pawn 2
                                activeBoard[colorSpawn] = pawn_lst[i + 1]
                                print("Pawn 2 has been spawned at the spawn point of", color)
                                print(
                                    "THE pawn which was on your spawn has been captured by the newly spawned pawn2")

                                # Spawns new pawn on the quantum circuit
                                #new_pawn(activeBoard.index(activeBoard[colorSpawn))
                                print(activeBoard.index(activeBoard[colorSpawn]))  # Prints out position of the spawn

                                # In case of classical spawn capture, the spawn camper gets banished to the shadow realm
                                activeBoard[positionSpawnCamper] = None
                                # TODO: Call quantum function which removes the spawn camper from the board
                                # remove_pawn(activeBoard.index(activeBoard[positionSpawnCamper]))
                            else:
                                print("There are no available spots to spawn!")
                                # Move pawn 1
                                if pawn1_count != 0:
                                    print("Continue with movement of pawn 1")
                                    # TODO: Call quantum move function
                                    # TODO: Check is move is allowed
                                    # TODO: Move pawn from board[start] to board[end]
                                    # move(board[i], board[i + d1])
                                    # move(board[i], board[i + d2])
                                # Move pawn 2
                                elif pawn2_count != 0:
                                    print("Continue with movement of pawn 2")
                                    # TODO: Call quantum move function
                                    # Check if move is allowed
                                    # TODO: Move pawn from board[start] to board[end]
                                    # move(board[i], board[i + d1])
                                    # move(board[i], board[i + d2])
                                # TODO: Check if chosen move is allowed
                                # TODO: Move pawn on the classical board
                                # TODO: Call movement function, to move pawn on the quantum board

                        ######
                        # QUANTUM SPAWN CAPTURE
                        ######
                        # In case the spawn camper does not have probability 1 to be
                        # right on your spawn point.
                        # Same idea as above, but now capture happens with a superposition
                        # and the enemy pawn remains on your spawn point
                        else:
                            while activeBoard[colorSpawn] is not None:
                                colorSpawn = colorSpawn + 1
                                positionCounter = positionCounter + 1
                                if positionCounter >= boardPositions:
                                    break

                            if pawn1_count == 0 and positionCounter < boardPositions:
                                # Spawns pawn 1 at the first free spot
                                activeBoard[colorSpawn] = pawn_lst[i]
                                print("Pawn 1 has been spawned at (near) the spawn point of", color)
                                #new_pawn(activeBoard.index(activeBoard[colorSpawn))
                                print(activeBoard.index(activeBoard[colorSpawn]))  # Prints out position of the spawn

                                # TODO: Call capture function
                                print("Your pawn 1 and the occupying pawn have become entangled")
                                parametersCapture = capturePawn(activeBoard[colorSpawn],
                                                                activeBoard[positionSpawnCamper], activeBoard)
                                posAttacker = parametersCapture[0]
                                posCaptive = parametersCapture[1]
                                allPosCaptive = parametersCapture[2]

                                # Calls the quantum capture function
                                #capture(posAttacker, posCaptive, allPosCaptive)

                            elif pawn2_count == 0 and positionCounter < boardPositions:
                                # Spawns pawn 2 at the first free spot
                                activeBoard[colorSpawn] = pawn_lst[i + 1]
                                print("Pawn 2 has been spawned at the spawn point of", color)
                                #new_pawn(activeBoard.index(activeBoard[colorSpawn))
                                print(activeBoard.index(activeBoard[colorSpawn]))  # Prints out position of the spawn

                                # TODO: Call capture function
                                print("Your pawn 2 and the occupying pawn have become entangled")
                                parametersCapture = capturePawn(activeBoard[colorSpawn],
                                                                activeBoard[positionSpawnCamper], activeBoard)
                                posAttacker = parametersCapture[0]
                                posCaptive = parametersCapture[1]
                                allPosCaptive = parametersCapture[2]

                                # Calls the quantum capture function
                                #capture(posAttacker, posCaptive, allPosCaptive)

                            else:
                                print("There are no available spots to spawn!")
                                # Move pawn 1
                                if pawn1_count != 0:
                                    print("Continue with movement of pawn 1")
                                    # TODO: Call quantum move function
                                    # TODO: Check is move is allowed
                                    # TODO: Move pawn from board[start] to board[end]
                                    # move(board[i], board[i + d1])
                                    # move(board[i], board[i + d2])
                                # Move pawn 2
                                elif pawn2_count != 0:
                                    print("Continue with movement of pawn 2")
                                    # TODO: Call quantum move function
                                    # Check if move is allowed
                                    # TODO: Move pawn from board[start] to board[end]
                                    # move(board[i], board[i + d1])
                                    # move(board[i], board[i + d2])
                                # TODO: Check if chosen move is allowed
                                # TODO: Move pawn on the classical board
                                # TODO: Call movement function, to move pawn on the quantum board

                    # If player does not want to spawn a new pawn, continue with movement of already
                    # existing pawn 1/2
                    else:
                        print("Continue to movement")
                        # Move pawn 1
                        if pawn1_count != 0:
                            print("Moving pawn1")
                            # TODO: Call quantum move function
                            # TODO: Check is move is allowed
                            # TODO: Move pawn from board[start] to board[end]
                            # move(board[i], board[i + d1])
                            # move(board[i], board[i + d2])
                        # Move pawn 2
                        elif pawn2_count != 0:
                            print("Moving pawn2")
                            # TODO: Call quantum move function
                            # Check if move is allowed
                            # TODO: Move pawn from board[start] to board[end]
                            # move(board[i], board[i + d1])
                            # move(board[i], board[i + d2])
                        else:
                            print("You don't have any pawns to move, you need to spawn one")

            # If throwing a 6 and no spawn is available, continue to movement
            else:
                print("No spawn is available, as you don't have any available pawns, choose an existing pawn to "
                      "move")
                askPawn = int(input("Which pawn do you want to move?"))
                # TODO: Check if move is allowed, move pawn on classical board and on the quantum board
                # TODO: Pull value of dice and put into the move function
                if askPawn == 1:
                    print("Moving pawn 1")
                elif askPawn == 2:
                    print("Moving pawn 2")

        # Move to next colors turn, for example if it is the turn of green, then code moves from red to green
        # by changing spawn point from point 0 to point 8 and moving the pawns green1 and green2
        else:
            # Spawn points are R, G, B, Y (0, 8, 16, 24)
            colorSpawn = colorSpawn + 8
            # Pawns are in list as r1, r2, g1, g2, etc.
            i = i + 2


def askMove(turn_color, activeBoard, pawn1_count, pawn2_count):
    """
    :param turn_color: Current active color
    :param activeBoard: Board with positions of all pawns
    :param pawn1_count: Number of times pawn 1 of the color occurs
    :param pawn2_count: Number of times pawn 2 of the color occur
    :return:
    """
    if pawn1_count != 0 and pawn2_count != 0:
        ask = input("Which pawn do you want to move 1 or 2?")
        if ask == 1:
            #move([start], [end])
            print("Call movement function")


def capturePawn(blufor, opfor, activeBoard):
    """
    :param blufor: Your pawn which is capturing the enemy pawn, of form board[position], as input blufor is
    updated position so the position after capture
    :param opfor: Enemy pawn which is captured, of form board[position], remains on same place on board
    :param activeBoard current active board
    :param opforEntangled: List of pawns which are entangled with the captured pawn
    :return:
    """
    # Creates list of all the previous positions of the captured pawn
    captiveColor = opfor["color"]
    captivePawn = opfor["pawn"]
    captivePositions = [index for index, element in enumerate(activeBoard) if element is not None
                        and element.get('color') == captiveColor and
                        element.get('pawn') == captivePawn]
    # Excluding the position which was captured
    captivePositions.remove(activeBoard.index(opfor))
    print("Pawn", blufor["color"], blufor["pawn"], "is now entangled with (has captured) pawn",
          opfor["color"], opfor["pawn"])
    #
    # Returns in order in a list the index of the attacker, index of captive and a list of all the positions of
    # the captive
    return [activeBoard.index(blufor)], [activeBoard.index(opfor)], captivePositions


def movePawn(d1, d2, start, activeBoard):
    """
    :param d1: Value of dice 1
    :param d2: Value of dice 2
    :param start: Position of pawn before throw, of form board[start], where start takes value 0 to 31.
    When d1 and d2 have equal value, we have a classical die throw,
    if not we have a quantum die throw, so the pawn will be in a superposition
    of two points
    """

    # Classical movement, both die have the same value.
    # The probabilities do not change
    if d1 == d2:
        # Checks if new position is already occupied
        if activeBoard[start + d1] is not None:
            # If new point is already occupied by pawn of the same color
            if activeBoard[start + d1]["color"] == activeBoard[start]["color"]:
                if activeBoard[start + d1]["pawn"] == activeBoard[start]["pawn"]:
                    # Case where same pawn is already there
                    print("Same pawn was already there, SWAP?")
                    # TODO: Call the SWAP Function

                else:
                    # Case different pawn but same color is already there
                    print("Move not allowed, as your other pawn is already there. Skip turn or do something else")
                    # TODO: Move on to next colors turn, or redirect to movement of other pawn

            # When other color occupies the position, it gets captured
            else:
                posAttacker = start + d1 + 1
                positionCounter = 0
                # True classical capture
                if activeBoard[start + d1]["probability"] == 1 and activeBoard[start]["probability"] == 1:
                    # During capture the pawn eats the pawn and moves one after the position of the eaten pawn
                    while activeBoard[posAttacker] is not None:
                        posAttacker = posAttacker + 1
                        positionCounter = positionCounter + 1
                        if positionCounter >= boardPositions:
                            break

                    activeBoard[posAttacker] = activeBoard[start]  # Final position of attacker
                    activeBoard[start] = None
                    activeBoard[start + d1] = None  # Eaten pawn is banished to the shadow realm

                    # TODO: Call quantum move function
                    # TODO: Call quantum remove function, deletes captured pawn

                    # TODO: Call the quantum function which removes the pawn
                    #remove_pawn(activeBoard[start + d1])

                # Quantum capture when either of the two were already in a superposition
                # In this case unlike the true classical case, the captured pawn does not vanish
                else:
                    print("Capture of a quantum pawn")
                    while activeBoard[posAttacker] is not None:
                        posAttacker = posAttacker + 1
                        positionCounter = positionCounter + 1
                        if positionCounter >= boardPositions:
                            break

                    activeBoard[posAttacker] = activeBoard[start]  # Final position of attacker
                    activeBoard[start] = None

                    # TODO: Call movement function

                    parametersCapture = capturePawn(activeBoard[posAttacker],
                                                    activeBoard[start + d1], activeBoard)
                    posAttacker = parametersCapture[0]
                    posCaptive = parametersCapture[1]
                    allPosCaptive = parametersCapture[2]

                    # Calls the quantum capture function
                    # capture(posAttacker, posCaptive, allPosCaptive)

        # if new position is empty, move pawn to that place
        else:
            # Move pawn to new position
            activeBoard[start + d1] = activeBoard[start]
            # Remove pawn from old position
            activeBoard[start] = None

            # TODO: Call quantum move function
            #move(activaBoard[start], activeBoard[start + d1])

    ########################
    # Quantum movement
    ########################
    else:
        posAttacker1 = start + d1 + 1
        posAttacker2 = start + d2 + 1
        positionCounter = 0
        # Both new positions are nonempty
        if activeBoard[start + d1] is not None and activeBoard[start + d2] is not None:
            # print("Both new positions are already occupied by your pawns, SKIP or SWAP?")
            # TODO: Implement SKIP or SWAP function
            if activeBoard[start + d1]["color"] == activeBoard[start]["color"] and activeBoard[start + d2]["color"] == \
                    activeBoard[start]["color"]:
                print("Existing pawn of your color is already there on BOTH places, SWAP?")
                # TODO SWAP function
            elif activeBoard[start + d1]["color"] == activeBoard[start]["color"]:
                print("eawe")
                # TODO SWAP with d1
                # Capture the pawn with d2, with probability / 2
            elif activeBoard[start + d2]["color"] == activeBoard[start]["color"]:
                print("ewa")
                # TODO SWAP with d2
                # TODO: Capture the pawn with d1 with prob / 2

        # Only one of the two is nonempty
        elif activeBoard[start + d1] is not None:
            # If new point is already occupied by pawn of the same color
            if activeBoard[start + d1]["color"] == activeBoard[start]["color"]:
                if activeBoard[start + d1]["pawn"] == activeBoard[start]["pawn"]:
                    # Case where same pawn is already there
                    print("Same pawn was already there, SWAP?")
                    # TODO: List call Swap function

                else:
                    # Case different pawn but same color is already there
                    print("Your other pawn is already there, SKIP?")
                    # TODO: Skip turn or ask for a another move to take

            # When other color occupies the position, it gets captured
            else:
                # NOTE: These if else statements not needed I think what is inside the if statement below should suffice
                # Semi Classical capture
                if activeBoard[start + d1]["probability"] == 1:
                    while activeBoard[posAttacker1] is not None:
                        posAttacker1 = posAttacker1 + 1
                        positionCounter = positionCounter + 1
                        if positionCounter >= boardPositions:
                            break
                    # During capture the pawn eats the pawn and moves one after the position of the eaten pawn
                    activeBoard[posAttacker1] = activeBoard[start]
                    activeBoard[start] = None
                    # TODO: Call quantum movement function

                    parametersCapture = capturePawn(activeBoard[posAttacker1],
                                                    activeBoard[start + d1], activeBoard)
                    posAttacker = parametersCapture[0]
                    posCaptive = parametersCapture[1]
                    allPosCaptive = parametersCapture[2]
                    # TODO: Call quantum capture function

                # Quantum capture of a quantum pawn by a quantum pawn
                else:
                    print("Capture of a quantum pawn by a quantum pawn")
                    # TODO: Call the (Classical) capture function, which entangles the two, in case enemy pawn is also
                    # classical, the pawn is removed from the board, otherwise the two are entangled

        elif activeBoard[start + d2] is not None:
            # If new point is already occupied by pawn of the same color
            if activeBoard[start + d2]["color"] == activeBoard[start]["color"]:
                if activeBoard[start + d2]["pawn"] == activeBoard[start]["pawn"]:
                    # Case where same pawn is already there
                    print("Same pawn was already there, SWAP?")

                else:
                    # Case different pawn but same color is already there
                    print("Your other pawn is already there, SKIP?")

            # When other color occupies the position, it gets captured
            else:
                # NOTE: These if else statements not needed I think what is inside the if statement below should suffice
                # quisi classical capture
                if activeBoard[start + d2]["probability"] == 1:
                    while activeBoard[posAttacker2] is not None:
                        posAttacker2 = posAttacker2 + 1
                        positionCounter = positionCounter + 1
                        if positionCounter >= boardPositions:
                            break

                    # During capture the pawn eats the pawn and moves one after the position of the eaten pawn
                    activeBoard[start + d2 + 1] = activeBoard[start]
                    activeBoard[start] = None
                    # TODO: Call quantum movement function

                    parametersCapture = capturePawn(activeBoard[posAttacker2],
                                                    activeBoard[start + d2], activeBoard)
                    posAttacker = parametersCapture[0]
                    posCaptive = parametersCapture[1]
                    allPosCaptive = parametersCapture[2]
                    # TODO: Call quantum capture function

                # Quantum capture of a quantum pawn by a quantum pawn
                else:
                    print("Capture of a quantum pawn by a quantum pawn")
                    # TODO: Call the (Classical) capture function, which entangles the two, in case enemy pawn is also
                    # classical, the pawn is removed from the board, otherwise the two are entangled

        # When both points are empty
        else:
            activeBoard[start]["probability"] = activeBoard[start]["probability"] / 2
            activeBoard[start + d1] = activeBoard[start].copy()
            activeBoard[start + d2] = activeBoard[start].copy()
            activeBoard[start] = None

            # TODO: Call quantum move function twice, which moves pawn to both d1 and 2


def doMeasurement(d1, d2, turn_color, start, activeBoard):
    # Positions which are right in front of winning place, for R, G, B, Y respectively
    almostHome = [31, 7, 15, 23]
    for color in colorTypes:
        if turn_color == color:
            position = activeBoard.index(start)  # Position of pawn as an index
            # Last position before winning for the active color
            almostHomeColor = almostHome[colorTypes.index(turn_color)]
            # If the end position ends up in one of the two winning places, do a measurement
            if almostHomeColor + 1 <= start + d1 <= almostHomeColor + 2\
                    or almostHomeColor + 1 <= start + d2 <= almostHomeColor + 2:
                print("YOU WIN, well maybe, WE WILL SEE AFTER MEASUREMNT")
                # TODO: Call the quantum measurement function
                return True
            else:
                print("AW SHUCK, TIME TO MOVE BACKWARDS")
                return False


# Values of dice1 and dice2
# Implemented as an input
dice1 = 6
dice2 = 3
turnColor = "red"

colorTypes = ["red", "green", "blue", "yellow"]

# Create board
board = [None] * 32
test = [None] * 6
boardPositions = 5

# Pawn creation
red1 = {"color": "red", "probability": 1, "pawn": 1}
red2 = {"color": "red", "probability": 1, "pawn": 2}
green1 = {"color": "green", "probability": 1, "pawn": 1}
green2 = {"color": "green", "probability": 1, "pawn": 2}
blue1 = {"color": "blue", "probability": 1, "pawn": 1}
blue2 = {"color": "blue", "probability": 1, "pawn": 2}
yellow1 = {"color": "yellow", "probability": 1, "pawn": 1}
yellow2 = {"color": "yellow", "probability": 1, "pawn": 2}
pawn_lst = [red1, red2, green1, green2, blue1, blue2, yellow1, yellow2]

# Initial board
board[0] = green2
board[8] = green1
board[16] = blue1
board[24] = yellow1

test[0] = {"color": "green", "probability": 0.5, "pawn": 1}
test[1] = green2
test[2] = red1
test[3] = blue1
test[4] = blue2
test[5] = yellow1

print(test)
if dice1 == 6 or dice2 == 6:
    # If one of the dice is 6, it then checks if a spawn is available
    spawnEvent(turnColor, test)
    print(test)
else:
    posPawnStart = int(input("Which pawn do you want to move"))  # Starting position of pawn which will be moved
    movePawn(dice1, dice2, test[posPawnStart], test)