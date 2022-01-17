import pygame
import copy
import pygame


class gameBoard():

    def __init__(self, screen, slot_size, border, spacing, text_space, screen_offset, color):
        # List of tuples (color, rectangle obj)
        self.color = color
        self.drawable = [] 
        self.drawTurnHighlight = []
        # List of Players, player 1 (main), player 3, player 2, player 4
        self.screen_offset = screen_offset
        self.players = []
        self.player_slots = []
        self.player_slot_pos = []
        self.board_slots = []
        self.board_slot_pos = []
        self.center_size = 0
        self.allControllable = False
        self.selectedPlayer = -1
        self.screen = screen
        self.slot_size = slot_size
        self.border = border
        self.spacing = spacing
        self.text_space = text_space
        self.screen_res = screen.get_size()
        self.center_size = self.slot_size * 3 + self.border * 2 + self.spacing * 2
        self._createBoard()
        # From gameOBJ
        x = []
        y = []
        z = []
        for _ in range (0,3):        
            for _ in range(0,3):
                for _ in range(0,3):
                    z.append('n')
                y.append(z)
                z = []
            x.append(y)
            y = []
        self.board = x
        self.boardMove =(0,0,0,"")
        self.hasMoved = False
        self.playerTurn = 0

    # Picks up or places down piece
    def selectPiece(self, pos):
        # If click on player slot with nothing selected
        if self.selectedPlayer == -1:
            x = 1
            if self.allControllable:
                x = 4
            for i in range(0, x):
                for j in range(len(self.player_slots[i])):
                    if self.player_slots[i][j].collidepoint(pos):
                        if self.playerTurn == i+1 and not self.hasMoved:
                            self.selectedPlayer = i
                            self.players[i].MoveNew(self.player_slot_pos[i][j])
                            self.updateSelectedPos()
                        break
        # If click on board slot with something selected
        else:
            for i in range(len(self.board_slots)):
                #   | 0, 1, 2, |        
                #   | 3, 4, 5, | <-- Board Slot Positions   
                #   | 6, 7, 8  |      
                if self.board_slots[i].collidepoint(pos):
                    # Piece exists in position.
                    piece_type = self.players[self.selectedPlayer].getSelectedType()
                    if self.board[i // 3][i % 3][piece_type] == 'n':
                        self.players[self.selectedPlayer].Move(self.board_slot_pos[i])
                        self.players[self.selectedPlayer].StopMove()
                        self.boardMove = (i // 3, i % 3, piece_type, "p" + str(self.selectedPlayer + 1))
                        self.hasMoved = True
                        self.selectedPlayer = -1
                    break
    
    # Updates position of selected piece on board, Returns bool (if a selected player exists)
    def updateSelectedPos(self):
        if self.selectedPlayer != -1:
            mouse_pos = pygame.mouse.get_pos()
            self.players[self.selectedPlayer].Move(mouse_pos)
        return self.selectedPlayer != -1
    
    # Deselects Held Piece
    def deselectPiece(self, pos):
        if self.selectedPlayer != -1:
            self.players[self.selectedPlayer].ReturnPiece(pos)
            self.selectedPlayer = -1

    # Removes piece from board that was placed
    def undoMove(self):
        self.boardMove = (0,0,0,"")
        self.hasMoved = False
        self.loadBoardState(self.board)

    # Used to lock down any more moves and returns move made.
    # submitMove will submit a 3D array.
    def submitMove(self):
        # Update player Turn on board
        if self.boardMove[3] != "":
            #if self.playerTurn >= 4 or self.playerTurn < 1:
                #self.playerTurn = 1
            #else:
                #self.playerTurn += 1
            self.board[self.boardMove[0]][self.boardMove[1]][self.boardMove[2]] = self.boardMove[3]
            self.hasMoved = False
            move = self.boardMove
            self.boardMove = (0,0,0,"")
            return move
        else:
            raise ValueError
            
    def updateMove(self, move, turn):
        # Update player Turn on board
        if self.boardMove[3] == "":
            
            #if self.playerTurn >= 4 or self.playerTurn < 1:
                #self.playerTurn = 1
            #else:
                #self.playerTurn += 1
            self.playerTurn = turn
            self.board[move[0]][move[1]][move[2]] = move[3]
            self.loadBoardState(self.board)
        else:
            raise ValueError

    # Loads Piece Positions on Board
    def loadBoardState(self, board):
        self.board = board
        boardWithMove = copy.deepcopy(board)
        if self.hasMoved:
            boardWithMove[self.boardMove[0]][self.boardMove[1]][self.boardMove[2]] = self.boardMove[3]
        for player in self.players:
            player.ReturnAllPieces()
        for x in range (0,3):        
            for y in range(0,3):
                for size in range(0,3):
                    if boardWithMove[x][y][size] != 'n':
                        player = int(boardWithMove[x][y][size][1:]) - 1
                        if player == 0 or player == 1:
                            if size == 2:
                                size = 0
                            elif size == 0:
                                size = 2
                            self.players[player].MoveNew(self.player_slot_pos[player][size])
                        else:
                            self.players[player].MoveNew(self.player_slot_pos[player][size])
                        self.players[player].Move(self.board_slot_pos[x * 3 + y])
                        self.players[player].StopMove()

    # Draws all Board Rectangles
    def drawBoard(self):
        pygame.draw.rect(self.screen, self.drawTurnHighlight[self.playerTurn-1][0], self.drawTurnHighlight[self.playerTurn-1][1])
        for i in self.drawable:
            pygame.draw.rect(self.screen, i[0], i[1])
        for i in range(len(self.players)):
            self.players[i].drawPieces(self.screen)

    # Used to update screen when maximizing, minimizing
    def updateSize(self, screen):
        self.screen = screen
        self.screen_res = screen.get_size()
        self._createBoard()
        for i in range(len(self.players)):
            if i == 2 or i == 3:
                rev_pos = self.player_slot_pos[i].copy()
                rev_pos.reverse()
                self.players[i].ResetOriginalPos(rev_pos)
            else:
                self.players[i].ResetOriginalPos(self.player_slot_pos[i])
        self.loadBoardState(self.board)

    # Initilize Players
    def createPlayers(self, allControllable, playerTurn):
        self.allControllable = allControllable
        if playerTurn > 4 or playerTurn <= 1:
            self.playerTurn = 1
        else:
            self.playerTurn = playerTurn
        for i in range(0,4):
            if i == 2 or i == 3:
                rev_pos = self.player_slot_pos[i].copy()
                rev_pos.reverse()
                self.players.append(Player(self.color["p" + str(i+1)], rev_pos, self.slot_size))
            else:
                self.players.append(Player(self.color["p" + str(i+1)], self.player_slot_pos[i], self.slot_size))

    # Creates rectangles
    def _createBoard(self):
        self.drawable.clear()
        self.drawTurnHighlight.clear()
        self.player_slot_pos.clear()
        self.player_slots.clear()
        self.board_slot_pos.clear()
        self.board_slots.clear()
        self._createCenter()
        # Creation requires 1/3 to be made first then 2/4, this organizes positions
        player_1_and_3 = self._createTopBottomBoards()
        player_2_and_4 = self._createSideBoards()
        for i in range(0,2):
            self.player_slots += player_1_and_3[i*2]
            self.player_slot_pos += player_1_and_3[i*2 + 1]
            self.drawTurnHighlight += player_1_and_3[i + 4]
            #self.player_slots += player_2_and_4[2 - i//2]
            #self.player_slot_pos += player_2_and_4[3 - i//2]
            #self.drawTurnHighlight += player_2_and_4[5 - i]
            self.player_slots += player_2_and_4[i*2]
            self.player_slot_pos += player_2_and_4[i*2 + 1]
            self.drawTurnHighlight += player_2_and_4[i + 4]

    # Private: Appends center board rects to drawable
    def _createCenter(self):
        posX = self.screen_res[0] // 2 - self.center_size // 2
        posY = self.screen_res[1] // 2 - self.center_size // 2
        # Creating Center Board backplate
        main_board = pygame.Rect(posX, posY, self.center_size, self.center_size)
        self.drawable.append((self.color["center_board"], main_board))
        
        # Creating Center Board Slots
        for i in range(0,9):
            slot_posX = posX + self.border + (i % 3) * (self.slot_size + self.spacing)
            slot_posY = posY + self.border + (i // 3) * (self.slot_size + self.spacing)
            slot = pygame.Rect(slot_posX, slot_posY, self.slot_size, self.slot_size)

            self.drawable.append((self.color["board_slot"], slot))
            self.board_slot_pos.append((slot_posX + self.slot_size // 2, slot_posY + self.slot_size // 2))
            self.board_slots.append(slot)

    # Private: Appends top and bottom player board rects to drawable
    def _createTopBottomBoards(self):
        # Drawing Player 1 and 3's Board
        player_slots_1 = []
        player_slots_3 = []
        player_pos_1 = []
        player_pos_3 = []
        Highlight_1 = []
        Highlight_3 = []
        for player in range(1,4,2):
            if player == 1:
                posY = self.screen_res[1] // 2 + self.center_size // 2 + self.border
                posHighlightY = posY - self.border - self.center_size
            else:
                posY = self.screen_res[1] // 2 - self.center_size // 2 - self.border * 3 - self.text_space - self.slot_size
                posHighlightY = posY
            posX = self.screen_res[0] // 2 - self.center_size // 2
            # Creating player board & highlight
            side_board = pygame.Rect(posX, posY, self.center_size, self.slot_size + self.border * 2 + self.text_space)
            self.drawable.append((self.color["player_board"], side_board))
            highlight = pygame.Rect(
                posX - self.border // 2, 
                posHighlightY - self.border // 2, 
                self.center_size + self.border, 
                self.center_size + self.slot_size + self.border * 4 + self.text_space
            )

            # Creating Side Board Slots
            slot_positions = []
            slots = []
            for i in range(0,3):
                slot_posX = posX + self.border + i * (self.slot_size + self.spacing)
                slot_posY = posY + self.text_space + self.border
                slot = pygame.Rect((slot_posX, slot_posY, self.slot_size, self.slot_size))
                slots.append(slot)
                self.drawable.append((self.color["board_slot"], slot))
                slot_positions.append((slot_posX + self.slot_size // 2, slot_posY + self.slot_size // 2))

            # Used for sorting in createBoard
            if player == 1:
                player_slots_1.append(slots)
                player_pos_1.append(slot_positions)
                Highlight_1.append((self.color["turn"], highlight))
            else:
                player_slots_3.append(slots)
                player_pos_3.append(slot_positions)
                Highlight_3.append((self.color["turn"], highlight))

        return (player_slots_1, player_pos_1, player_slots_3, player_pos_3, Highlight_1, Highlight_3)

    # Private: Appends Left and Right player board rects to drawable
    def _createSideBoards(self):
        # Drawing Player 2 and 4's Board
        player_slots_2 = []
        player_slots_4 = []
        player_pos_2 = []
        player_pos_4 = []
        highlight_2 = []
        highlight_4 = []
        for player in range(4,1,-2):
            if player == 2:
                posX = self.screen_res[0] // 2 - self.center_size // 2 - 3 * self.border - self.slot_size
                posHighlightX = posX
            else:
                posX = self.screen_res[0] // 2 + self.center_size // 2 + self.border
                posHighlightX = posX - self.border - self.center_size
            posY = self.screen_res[1] // 2 - self.center_size // 2 - self.text_space
            # Creating player board & highlight
            side_board = pygame.Rect(posX, posY, (self.slot_size + self.border * 2), (self.center_size + self.text_space))
            self.drawable.append((self.color["player_board"], side_board))
            highlight = pygame.Rect(
                posHighlightX - self.border // 2, 
                posY - self.border // 2, 
                self.slot_size + self.border * 4 + self.center_size, 
                self.center_size + self.border + self.text_space
            )

            # Creating Side Board Slots
            slots = []
            slot_positions = []
            for i in range(0,3):
                # Append position, and draw it
                slot_posX = posX + self.border
                slot_posY = posY + self.border + self.text_space + i * (self.slot_size + self.spacing)
                slot = pygame.Rect((slot_posX, slot_posY, self.slot_size, self.slot_size))
                slots.append(slot)
                self.drawable.append((self.color["board_slot"], slot))
                slot_positions.append((slot_posX + self.slot_size // 2, slot_posY + self.slot_size // 2))

            # Used for sorting in createBoard
            if player == 2:
                player_slots_2.append(slots)
                player_pos_2.append(slot_positions)
                highlight_2.append((self.color["turn"], highlight))
            else:
                player_slots_4.append(slots)
                player_pos_4.append(slot_positions)
                highlight_4.append((self.color["turn"], highlight))

        return (player_slots_2, player_pos_2, player_slots_4, player_pos_4, highlight_2, highlight_4)


class Player():

    def __init__(self, color, origional_pos, slot_size):
        # 0-2 = large, 3-5 = medium, 6-8 = small 
        self.Pieces = []
        self.color = color
        self.origional_pos = origional_pos
        self.currently_moving = -1
        self._addPieces(slot_size)

    def Reset(self):
        pass

    # Selects a piece for moving
    def MoveNew(self, piece_pos):
        for i in range(len(self.Pieces)):
            if self.Pieces[i].location == piece_pos:
                self.currently_moving = i
                break
    
    # Deselects Moving Piece
    def StopMove(self):
        self.currently_moving = -1

    # Moves Selected Piece to new Location
    def Move(self, new_pos):
        if self.currently_moving != -1:
            self.Pieces[self.currently_moving].location = new_pos

    # Gets Current Piece Type
    # 0 - Small, 1 - med, 2 - large
    def getSelectedType(self):
        piece = self.currently_moving
        if piece != -1:
            if piece >= 0 and piece <= 2:
                return 2
            elif piece >= 3 and piece <= 5:
                return 1
            else:
                return 0


    def ReturnPiece(self, pos):
        for i in range(len(self.Pieces)):
            if self.Pieces[i].location == pos:
                self.Pieces[i].location = self.origional_pos[i // 3]
                break

    def ReturnAllPieces(self):
        for i in range(len(self.Pieces)):
            self.Pieces[i].location = self.origional_pos[i // 3]

    def SetPiecePositions(self):
        pass

    # Reset Pieces to New Player Position
    def ResetOriginalPos(self, pos):
        old_origional_pos = self.origional_pos.copy()
        self.origional_pos.clear()
        self.origional_pos = pos.copy()
        for i in range(0,3):
            for j in range(0,3):
                if self.Pieces[i * 3 + j].location == old_origional_pos[i]:
                    self.Pieces[i * 3 + j].location = self.origional_pos[i]

    # Create Player's Pieces
    def _addPieces(self, slot_size):
        thickness = [8, 8, 0]
        spacing = [1, 4, 7]
        for i in range(0, 3):
            for _ in range(0, 3):
                radius = (slot_size // 2) - spacing[i] * (slot_size // 20)
                self.Pieces.append(Piece(self.color, radius, self.origional_pos[i], thickness[i]))
    
    # Draws all 9 pieces
    def drawPieces(self, screen):
        for i in self.Pieces:
            pygame.draw.circle(screen, i.color, i.location, i.size, i.thickness)


class Piece(pygame.sprite.Sprite):
    def __init__(self, color, size, location, thickness):
        self.color = color
        self.location = location
        self.size = size
        self.thickness = thickness
        self.rect = pygame.Rect(location[0] - (size/2), location[1] - (size/2), size, size)
        self.moving = False