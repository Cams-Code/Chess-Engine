"""
    This class is responsible for storing all information about the current state of the chess game. It will also be responsible for 
    determining the valid moves at the current state and keeping a log of previous moves.
"""
import numpy as np
from copy import deepcopy
from pprint import pprint

class GameState():

    def __init__(self) -> None:
        # The board is an 8x8 2d list. Each element is 2 characters.
        # The first character represents the colour of the piece: 'b' or 'w'
        # The second character represents the type of piece, 'K', 'Q', 'R', 'B', 'N' or 'P'
        # Empty squares on the chess
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bP" for i in range(8)],
            ["" for i in range(8)],
            ["" for i in range(8)],
            ["" for i in range(8)],
            ["" for i in range(8)],
            ["wP" for i in range(8)],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"],
        ]
        self.whiteToMove = True
        self.moveLog = []
        self.moveIndex = -1
        self.whiteCheck = False
        self.blackCheck = False
        self.legalMovesInCheck = []
        self.checkMate = False
        self.whiteCastleKS = True
        self.whiteCastleQS = True
        self.blackCastleKS = True
        self.blackCastleQS = True
        self.allBlackLegal = []
        self.allWhiteLegal = []

    def update_moveLog(self,old,new):
        """
            Converts x,y vector to StockFish move format. e.g. a2a4 and adds it to move log
        """
        old_x = chr(ord('`')+old[0]+1)
        old_y = (old[1]*-1)+8
        new_x = chr(ord('`')+new[0]+1)
        new_y = (new[1]*-1)+8
        move_str = f'{old_x}{old_y}{new_x}{new_y}'
        if self.board[new[1]][new[0]] != '':
            piece = self.board[new[1]][new[0]]
            move_str += f"_{piece}"
        else:
            piece = ''
        ### Remove all elements in the list after current move
        ### Can cause issues with undo/redo moves etc
        
        self.moveLog = self.moveLog[:self.moveIndex+1]
        
        self.moveLog.append(move_str)
        self.moveIndex += 1

    def undoMove(self):
        """
            Used to go back in the moveLog and retrace steps
        """
        if self.moveIndex < 0:
            pass
        else:
            move = self.moveLog[self.moveIndex]
            self.moveIndex -= 1
            ### Converts StockFish move format to x,y vector
            old_x = ord(move[2]) - 97
            old_y = int(move[3])*-1+8
            new_x = ord(move[0]) - 97
            new_y = int(move[1])*-1+8
            self.board[new_y][new_x] = self.board[old_y][old_x]
            if self.board[old_y][old_x]:
                try:
                    piece = move.split('_')[1]
                except IndexError:
                    piece = ''
            else:
                piece = ''
            self.board[old_y][old_x] = piece

    def redoMove(self):
        """
            Used to redo moves in the moveLog
        """
        moveIndex = self.moveIndex + 1

        try:
            move = self.moveLog[moveIndex]
            self.moveIndex += 1
            ### Converts StockFish move format to x,y vector
            new_x = ord(move[2]) - 97
            new_y = int(move[3])*-1+8
            old_x = ord(move[0]) - 97
            old_y = int(move[1])*-1+8
            self.board[new_y][new_x] = self.board[old_y][old_x]
            self.board[old_y][old_x] = ''
        except IndexError:
            pass # No moves to redo as moveIndex is the last element of the list


    def wP(self,selected_piece,board, check_check=False, mult=-1):
        mult = -1
        legal_moves = self.move_pawn(board,selected_piece,mult,check_check)
        return legal_moves
        
    def bP(self,selected_piece,board, check_check=False, mult=1):
        mult = 1
        legal_moves = self.move_pawn(board,selected_piece,mult,check_check)
        return legal_moves
    
    def move_pawn(self,board,selected_piece:tuple,mult:int, check_check=False):
        """
        Pawn move logic:
            1. Move one square forward if vacant
            2. If first move, they can move 1 or 2 squares forward if vacant
            3. Pawns can only capture on the first diagonals infront of them.

            4. Able to capture by en-passant (When an opposing pawn) moves 2 squares past them.
            5. Promote to any piece when they reach opposing side of the board
        
        :params:
        -- selected piece: tuple. contained the piece name, and x/y co-ords
        -- mult: int. contains a multiplier for which way the pawn should move. 
            i.e. white pawn the y co-ord decreases whereas black pawn it increases
        -- check_check: bool. Used to check if getting moves to remove from king's legal_moves
        """
        legal_moves = []
        # Implementation of point 1
        if not board[selected_piece[2]+(1*mult)][selected_piece[1]] and not check_check:
            legal_moves.append((selected_piece[1], selected_piece[2]+(1*mult)))
        # Implementation of point 2
        if ((selected_piece[0][0] == 'b' and selected_piece[2] == 1) or (selected_piece[0][0] == 'w' and selected_piece[2] == 6)) and not check_check:
            if not board[selected_piece[2]+(2*mult)][selected_piece[1]] and not self.board[selected_piece[2]+(1*mult)][selected_piece[1]]:
                legal_moves.append((selected_piece[1], selected_piece[2]+(2*mult)))

        # Implementation of point 3
        diagonals = [[selected_piece[1]-1,selected_piece[2]+(1*mult)],[selected_piece[1]+1,selected_piece[2]+(1*mult)]]
        for diag in diagonals:
            if (-1 < diag[1] < 8) and (-1 < diag[0] < 8):
                piece = board[diag[1]][diag[0]]
                if (piece and piece[0] != selected_piece[0][0]) or check_check:
                    legal_moves.append((diag[0],diag[1]))

        # Implementation of point 4
        if ((selected_piece[0][0] == 'b' and selected_piece[2] == 4) or (selected_piece[0][0] == 'w' and selected_piece[2] == 3)) and not check_check:
            en_passant = self.en_passant(selected_piece,mult)
            if en_passant:
                legal_moves.append(en_passant)

        return legal_moves

    def en_passant(self, selected_piece,mult):
        """
            En passant is a special move that gives pawns the option to capture a pawn which has just passed it.
        """
        # Calculate the moveLog values to check if last move was pawn passing
        old_left_x = new_left_x = chr(ord('`')+selected_piece[1])
        old_right_x = new_right_x = chr(ord('`')+selected_piece[1]+2)

        new_left_y = (selected_piece[2]*-1)+8
        left_y_var = 2 if selected_piece[0][0] == 'w' else -2
        old_left_y = new_left_y + left_y_var
        new_right_y = (selected_piece[2]*-1)+8
        right_y_var = 2 if selected_piece[0][0] == 'w' else -2
        old_right_y = new_right_y + right_y_var

        legal_moves = []
        if self.moveLog[-1] == f"{old_left_x}{old_left_y}{new_left_x}{new_left_y}":
            legal_moves = (selected_piece[1]-1,selected_piece[2]+(1*mult))
        elif self.moveLog[-1] == f"{old_right_x}{old_right_y}{new_right_x}{new_right_y}":
            legal_moves = (selected_piece[1]+1,selected_piece[2]+(1*mult))
        return legal_moves

    def wN(self,selected_piece,board,check_check=False):
        legal_moves = self.move_knight(selected_piece,board,check_check)
        return legal_moves

    def bN(self,selected_piece,board,check_check=False):
        legal_moves = self.move_knight(selected_piece,board,check_check)
        return legal_moves
    
    def move_knight(self,selected_piece,board,check_check=False):
        """
            Knights move in an L shape in all directions.
        """
        legal_moves = []
        move_sets = [(-1,-2),(1,-2),(-1,2),(1,2),(2,1),(-2,-1),(2,-1),(-2,1)]
        for move in move_sets:
            new_x = selected_piece[1] + move[0]
            new_y = selected_piece[2] + move[1]
            if (-1 < new_x < 8) and (-1 < new_y < 8):
                piece_on_sq = board[new_y][new_x]
                if piece_on_sq:
                    if piece_on_sq[0]!=selected_piece[0][0] or check_check:
                        legal_moves.append((new_x,new_y))
                else:
                    legal_moves.append((new_x,new_y))
        return legal_moves

    def wB(self,selected_piece,board,check_check=False):
        legal_moves = self.move_bishop(selected_piece,board,check_check)
        return legal_moves

    def bB(self,selected_piece,board,check_check=False):
        legal_moves = self.move_bishop(selected_piece,board,check_check)
        return legal_moves
    
    def move_bishop(self,selected_piece,board,check_check=False):
        """
            Bishop move logic:
                1. Bishops can move in any diagonal, on the colour they are on.
        """
        legal_moves = []

        range_sets = [(1,8,1),(1,8,-1)]
        # Diagonal logic needs to be split in 2 - this is the loop for x+y increasing/decreasing
        for r_set in range_sets:
            for i in range(r_set[0],r_set[1]):
                new_x = selected_piece[1] + (i*r_set[2])
                new_y = selected_piece[2] + (i*r_set[2])
                if (-1 < new_x < 8) and (-1 < new_y < 8):
                    # If there is a piece at the x,y then the bishop can either take, or it is blocked for the rest of that diagonal
                    if board[new_y][new_x] != '':
                        if board[new_y][new_x][0] != selected_piece[0][0] or check_check:
                            legal_moves.append((new_x,new_y))
                        break
                    else:
                        legal_moves.append((new_x,new_y))

        # This is the loop for x increasing/ y decreasing and vice versa
        for r_set in range_sets:
            for i in range(r_set[0],r_set[1]):
                new_x = selected_piece[1] + (i*r_set[2])
                new_y = selected_piece[2] - (i*r_set[2])
                if (-1 < new_x < 8) and (-1 < new_y < 8):
                    if board[new_y][new_x] != '':
                        if board[new_y][new_x][0] != selected_piece[0][0] or check_check:
                            legal_moves.append((new_x,new_y))
                        break
                    else:
                        legal_moves.append((new_x,new_y))

        return legal_moves
    
    def wR(self,selected_piece,board,check_check=False):
        legal_moves = self.move_rook(selected_piece,board,check_check)
        return legal_moves

    def bR(self,selected_piece,board,check_check=False):
        legal_moves = self.move_rook(selected_piece,board,check_check)
        return legal_moves

    def move_rook(self,selected_piece,board,check_check):
        """
            Rooks can only move in straight lines, horizontally or vertically
        """
        legal_moves = []
        range_sets = [(1,8,1),(1,8,-1)]
        for r_set in range_sets:
            x_blocked = False
            y_blocked = False
            for i in range(r_set[0],r_set[1]):
                # Logic to move on x axis
                new_x = selected_piece[1] + (i*r_set[2])
                if (-1 < new_x < 8):
                    if board[selected_piece[2]][new_x] != '' and not x_blocked:
                        if board[selected_piece[2]][new_x][0] != selected_piece[0][0] or check_check: # Check if colour of piece is opposing side - if so then legal square
                            legal_moves.append((new_x,selected_piece[2]))
                        x_blocked = True
                    elif x_blocked: # Rooks can't move over pieces - if blocked then it can't move anymore in that direction
                        pass
                    else:
                        legal_moves.append((new_x,selected_piece[2]))
                # Logic to move on y axis
                new_y = selected_piece[2] + (i*r_set[2])
                if (-1 < new_y < 8):
                    if board[new_y][selected_piece[1]] != '' and not y_blocked:
                        if board[new_y][selected_piece[1]][0] != selected_piece[0][0] or check_check: # Check if colour of piece is opposing side - if so then legal square
                            
                            legal_moves.append((selected_piece[1],new_y))
                        y_blocked = True
                    elif y_blocked: # Rooks can't move over pieces - if blocked then it can't move anymore in that direction
                        pass
                    else:
                        legal_moves.append((selected_piece[1],new_y))

        return legal_moves
    
    def wQ(self,selected_piece,board,check_check=False):
        legal_moves = self.move_queen(board,selected_piece,check_check)
        return legal_moves

    def bQ(self,selected_piece,board,check_check=False):
        legal_moves = self.move_queen(board,selected_piece,check_check)
        return legal_moves

    def move_queen(self,board,selected_piece,check_check):
        """
            Queens can move in straight lines, like rooks, and diagonally, like bishops
        """
        legal_moves = self.move_bishop(selected_piece,board,check_check)
        legal_moves += self.move_rook(selected_piece,board,check_check)
        return legal_moves

    def wK(self,selected_piece,board,check=True,check_check=False):
        legal_moves = self.move_king(selected_piece,board,check_check)
        if not check:
            legal_moves = self.filter_kingMoves(legal_moves,board,selected_piece[0][0])
            legal_moves += self.castling(selected_piece,legal_moves)
        return legal_moves

    def bK(self,selected_piece,board,check=True,check_check=False):
        legal_moves = self.move_king(selected_piece,board,check_check)
        if not check:
            legal_moves = self.filter_kingMoves(legal_moves,board,selected_piece[0][0])
        return legal_moves

    def move_king(self,selected_piece,board,check_check):
        """
            A king has the following move logic:
                - Move 1 square in any direction assuming unoccupied
                    - The square must not be underthreat by an enemy piece
        """
        legal_moves = []
        move_sets = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        for move in move_sets:
            new_x = selected_piece[1] + move[0]
            new_y = selected_piece[2] + move[1]
            if (-1 < new_x < 8) and (-1 < new_y < 8):
                if board[new_y][new_x] == '':
                    legal_moves.append((new_x,new_y))
                elif board[new_y][new_x][0] != selected_piece[0][0] or check_check:
                    legal_moves.append((new_x,new_y))
                    
        return legal_moves
    
    def filter_kingMoves(self,legal_moves:list, board:list,colour:str) -> list:
        """
            Removes squares from king's legal squares list that are under attack from opposing colour.
        """
        all_moves_dict = self.check_all_moves(colour,board=board)
        all_moves_list = []
        for key in all_moves_dict:
            all_moves_list.extend(all_moves_dict[key])
        legal_moves = list(set(legal_moves) - set(all_moves_list))
        return legal_moves

    def castling(self,selected_piece:tuple,legal_squares:list):
        """
            Logic used to determine if a colour can castle, and if yes, adds to legal_squares
        """
        # ks_castle = king-side castle
        # qs_castle = queen-side castle
        castle_sqs = []
        opp_colour_moves = self.allBlackLegal if selected_piece[0][0] == 'w' else self.allWhiteLegal
        king_y = selected_piece[2]
        if (self.blackCastleKS and selected_piece[0][0] == 'b') or (self.whiteCastleKS and selected_piece[0][0] == 'w'):
            ks_adj_x = selected_piece[1] + 1
            if (ks_adj_x, king_y) in legal_squares:
                ks_castle_x = selected_piece[1] + 2
                if (ks_castle_x, king_y) not in opp_colour_moves and self.board[king_y][ks_castle_x] == '':
                    if self.board[king_y][7] == f'{selected_piece[0][0]}R':
                        castle_sqs.append((ks_castle_x,king_y))

        if (self.blackCastleQS and selected_piece[0][0] == 'b') or (self.whiteCastleQS and selected_piece[0][0] == 'w'):
            qs_adj_x = selected_piece[1] - 1
            if (qs_adj_x, king_y) in legal_squares:
                qs_castle_x = selected_piece[1] - 2
                if (qs_castle_x, king_y) not in opp_colour_moves and self.board[king_y][qs_castle_x] == '' and self.board[king_y][qs_castle_x - 1] == '':
                    castle_sqs.append((qs_castle_x,king_y))

        return castle_sqs

    def moveCastling(self,drop_pos:tuple):
        """
            Function to handle correctly castling
        """
        castle_map = {
            (2, 0): {'rook_old':(0, 0),'rook_new':(3, 0)},
            (6, 0): {'rook_old':(7, 0),'rook_new':(5, 0)},
            (2, 7): {'rook_old':(0, 7),'rook_new':(3, 7)},
            (6, 7): {'rook_old':(7, 7),'rook_new':(5, 7)}, 
        }
        colour = 'b' if drop_pos[0] == 0 else 'w'
        rook_old_x, rook_old_y = castle_map[drop_pos]['rook_old']
        rook_new_x, rook_new_y = castle_map[drop_pos]['rook_new']
        self.board[rook_new_y][rook_new_x] = f'{colour}R'
        self.board[rook_old_y][rook_old_x] = ''

    def check_all_moves(self,piece,board,check=False):
        """
            This function gets all legal moves for all pieces of a specific colour.

            :params:
            -- piece: Colour of the piece that we are checking the legal moves against
            -- check: Determines if the player is in check
        """
        colour_map = {'w':-1,'b':1}
        legal_moves = {}
        for y,col in enumerate(self.board):
            for x,row in enumerate(col):
                # Check square is occupied and that it isn't the current piece
                if row and row[0] != piece:
                    func = getattr(self, row)
                    selected_piece = (row, x, y)
                    if row[1] == 'P': # We only want to return the diagonal legal_moves for pawns as they can only take on the diagonal.
                        pawn_check = not check
                        moves = func(selected_piece,check_check=pawn_check,mult=colour_map[row[0]],board=board)
                    else:
                        moves = func(selected_piece,check_check=True,board=board)
                    if legal_moves.get((x,y)):
                        legal_moves[(x,y)].append(moves)
                    else:
                        legal_moves[(x,y)] = moves
        if piece == 'w':
            if board == self.board:
                self.allBlackLegal = legal_moves
        else:
            if board == self.board:
                self.allWhiteLegal = legal_moves
        return legal_moves

    def capture_ep(self,drop_pos:tuple):
        """
            Function for calculating the x,y co-ords of the captured piece after en-passant
        """
        x,y = drop_pos
        if y == 2:
            return x, y+1
        else:
            return x, y-1

    def check_if_check(self,colour:str, board=[], testingCheck=False) -> list:
        """
            Function to check if player is now in check after the move
        """
        colour_map = {'w':-1,'b':1}
        legal_moves = []
        legal_moves_dict = {}

        if not board:
            board = self.board

        for y,col in enumerate(board):
            for x,row in enumerate(col):                                                                                                    
                # Check square is occupied and it is the same colour as just moved
                if row and row[0] == colour:
                    func = getattr(self,row)
                    selected_piece = (row, x, y)
                    if row[1] == 'P': # We only want to return the diagonal legal_moves for pawns as they can only take on the diagonal.
                        piece_moves = func(selected_piece,board,check_check=True,mult=colour_map[row[0]])
                    else:
                        piece_moves = func(selected_piece,board,check_check=True)
                    legal_moves += piece_moves
                    # Store all moves that cause check into dict, and the pieces that are giving check
                    for move in piece_moves:
                        if move in legal_moves_dict.keys():
                            legal_moves_dict[move].append((row, x, y))
                        else:
                            legal_moves_dict[move] = [(row, x, y)]

        # Checking if opposing king x,y co-ords are in the legal moves. If so, it is check.
        opp_colour = 'b' if colour == 'w' else 'w'
        y,x = self.kingCoords(opp_colour,board)

        if (x,y) in legal_moves:
            if testingCheck:
                return True
            else:
                attackingPieces = (legal_moves_dict[(x,y)])
                if opp_colour == 'b':
                    self.blackCheck = True
                else:
                    self.whiteCheck = True
        else:
            if testingCheck:
                return False
            else:
                self.whiteCheck = False
                self.blackCheck = False
                attackingPieces = []

        return attackingPieces

    def checkLegalMoves(self,attackingPieces:list,king:str):
        """
            Function to calculate what legal moves will evade check.

            Method is as follows:
                1. Finds all possible x,y coords of blocking the check
                2. Gets legal move of all pieces, and checks if any are in blocking_squares
                3. If piece can move there, creates a copy of the game board to test if still in check after moving there
                4. Updates self.legalMovesInCheck dict if there are legal moves
                5. If self.legalMovesInCheck is empty, it's checkmate

            :params:
            -- attackingPieces: list of tuples which contains piece+x,y coords that caused check
            -- king: the colour of the piece that has just moved
           
        """
        blocking_squares = []
        king_col = 'b' if king == 'w' else 'w'
        king_y,king_x = self.kingCoords(king_col,self.board)
        ### Get King's moves so we can add to list later
        opp_king_str = f'{king_col}K'
        if king_col == 'b':
            king_moves = self.bK(selected_piece=(opp_king_str,king_x,king_y),check=False,board=self.board)
        else:
            king_moves = self.wK(selected_piece=(opp_king_str,king_x,king_y),check=False,board=self.board)

        # Step 1 of above method
        for piece in attackingPieces:
            piece,x,y = piece
            blocking_squares.append((x,y))
            ### Bishop, Rook and Queen check can be blocked by putting a piece between the king and respective piece
            if piece[1] in ['B','R','Q']:
                if x == king_x:
                    y_path = 1 if y - king_y < 0 else -1
                    x_path = 0
                elif y == king_y:
                    x_path = 1 if x - king_x < 0 else -1
                    y_path = 0
                else:
                    x_path = 1 if x - king_x < 0 else -1
                    y_path = 1 if y - king_y < 0 else -1

                new_x = x + x_path
                new_y = y + y_path
                while (new_x,new_y) !=  (king_x,king_y):
                    blocking_squares.append((new_x,new_y))
                    new_x += x_path
                    new_y += y_path

        # This is a list of all squares which will block current check
        blocking_squares = list(dict.fromkeys(blocking_squares))
        
        # Return all legal moves from each piece to see which can block
        all_moves = self.check_all_moves(king,check=True,board=self.board)

        legal_moves = {}
        ### Loop through moves from each piece and see if the move blocks check
        for key,value in all_moves.items():
            legal_moves[key] = list(set(value) & set(blocking_squares))
            if not legal_moves[key]:
                legal_moves.pop(key)

        legal_moves[(king_x, king_y)] = king_moves
        safe_moves = self.testCheckMoves(legal_moves,colour=king)

        if safe_moves:
            self.legalMovesInCheck = safe_moves
        else:
            self.checkMate = True

    def testCheckMoves(self,legal_moves:dict,colour) -> dict:
        """
            Function to test each move that is found to block check.
            We are testing to see if after that move has been performed, we are in check
             from another piece.
        """
        safe_moves = {}
        for key,value in legal_moves.items():
            old_x,old_y = key
            for move in value:
                new_x,new_y = move
                board = deepcopy(self.board)
                piece = board[old_y][old_x]
                board[old_y][old_x] = ''
                board[new_y][new_x] = piece
                in_check = self.check_if_check(board=board,testingCheck=True,colour=colour)
                if not in_check:
                    if key in safe_moves.keys():
                        safe_moves[key].append(move)
                    else:
                        safe_moves[key] = [move]

        return safe_moves

    def kingCoords(self,colour,board):
        """
            Function to find x,y coords of king
        """
        king = f"{colour}K"
        array = np.array(board)
        king_xy = list(zip(*np.where(array == king)))
        y,x = king_xy[0]
        return y,x