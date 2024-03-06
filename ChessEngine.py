"""
    This class is responsible for storing all information about the current state of the chess game. It will also be responsible for 
    determining the valid moves at the current state and keeping a log of previous moves.
"""

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


    def wP(self,selected_piece, check_check=False):
        mult = -1
        legal_moves = self.move_pawn(selected_piece,mult,check_check)
        return legal_moves
        
    def bP(self,selected_piece, check_check=False):
        mult = 1
        legal_moves = self.move_pawn(selected_piece,mult,check_check)
        return legal_moves
    
    def move_pawn(self,selected_piece:tuple,mult:int, check_check=False):
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
        if not self.board[selected_piece[2]+(1*mult)][selected_piece[1]] and not check_check:
            legal_moves.append((selected_piece[1], selected_piece[2]+(1*mult)))
        # Implementation of point 2
        if ((selected_piece[0][0] == 'b' and selected_piece[2] == 1) or (selected_piece[0][0] == 'w' and selected_piece[2] == 6)) and not check_check:
            if not self.board[selected_piece[2]+(2*mult)][selected_piece[1]] and not self.board[selected_piece[2]+(1*mult)][selected_piece[1]]:
                legal_moves.append((selected_piece[1], selected_piece[2]+(2*mult)))

        # Implementation of point 3
        diagonals = [[selected_piece[1]-1,selected_piece[2]+(1*mult)],[selected_piece[1]+1,selected_piece[2]+(1*mult)]]
        for diag in diagonals:
            if (-1 < diag[1] < 8) and (-1 < diag[0] < 8):
                piece = self.board[diag[1]][diag[0]]
                if (piece and piece[0] != selected_piece[0][0]) or check_check:
                    legal_moves.append((diag[0],diag[1]))

        # Implementation of point 4
        if ((selected_piece[0][0] == 'b' and selected_piece[2] == 4) or (selected_piece[0][0] == 'w' and selected_piece[2] == 3)) and not check_check:
            print("here")
            legal_moves.append(self.en_passant(selected_piece,mult))

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

        legal_moves = ()
        if self.moveLog[-1] == f"{old_left_x}{old_left_y}{new_left_x}{new_left_y}":
            legal_moves = (selected_piece[1]-1,selected_piece[2]+(1*mult))
        elif self.moveLog[-1] == f"{old_right_x}{old_right_y}{new_right_x}{new_right_y}":
            legal_moves = (selected_piece[1]+1,selected_piece[2]+(1*mult))
        return legal_moves

    def wN(self,selected_piece):
        legal_moves = self.move_knight(selected_piece)
        return legal_moves

    def bN(self,selected_piece):
        legal_moves = self.move_knight(selected_piece)
        return legal_moves
    
    def move_knight(self,selected_piece):
        """
            Knights move in an L shape in all directions.
        """
        legal_moves = []
        move_sets = [(-1,-2),(1,-2),(-1,2),(1,2),(2,1),(-2,-1),(2,-1),(-2,1)]
        for move in move_sets:
            new_x = selected_piece[1] + move[0]
            new_y = selected_piece[2] + move[1]
            if (-1 < new_x < 8) and (-1 < new_y < 8):
                piece_on_sq = self.board[new_y][new_x]
                if piece_on_sq:
                    if piece_on_sq[0]!=selected_piece[0][0]:
                        legal_moves.append((new_x,new_y))
                else:
                    legal_moves.append((new_x,new_y))
        return legal_moves

    def wB(self,selected_piece):
        legal_moves = self.move_bishop(selected_piece)
        return legal_moves

    def bB(self,selected_piece):
        legal_moves = self.move_bishop(selected_piece)
        return legal_moves
    
    def move_bishop(self,selected_piece):
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
                    if self.board[new_y][new_x] != '':
                        if self.board[new_y][new_x][0] != selected_piece[0][0]:
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
                    if self.board[new_y][new_x] != '':
                        if self.board[new_y][new_x][0] != selected_piece[0][0]:
                            legal_moves.append((new_x,new_y))
                        break
                    else:
                        legal_moves.append((new_x,new_y))

        return legal_moves
    
    def wR(self,selected_piece):
        legal_moves = self.move_rook(selected_piece)
        return legal_moves

    def bR(self,selected_piece):
        legal_moves = self.move_rook(selected_piece)
        return legal_moves

    def move_rook(self,selected_piece):
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
                    if self.board[selected_piece[2]][new_x] != '' and not x_blocked:
                        if self.board[selected_piece[2]][new_x][0] != selected_piece[0][0]: # Check if colour of piece is opposing side - if so then legal square
                            legal_moves.append((new_x,selected_piece[2]))
                        x_blocked = True
                    elif x_blocked: # Rooks can't move over pieces - if blocked then it can't move anymore in that direction
                        pass
                    else:
                        legal_moves.append((new_x,selected_piece[2]))
                # Logic to move on y axis
                new_y = selected_piece[2] + (i*r_set[2])
                if (-1 < new_y < 8):
                    if self.board[new_y][selected_piece[1]] != '' and not y_blocked:
                        if self.board[new_y][selected_piece[1]][0] != selected_piece[0][0]: # Check if colour of piece is opposing side - if so then legal square
                            
                            legal_moves.append((selected_piece[1],new_y))
                        y_blocked = True
                    elif y_blocked: # Rooks can't move over pieces - if blocked then it can't move anymore in that direction
                        pass
                    else:
                        legal_moves.append((selected_piece[1],new_y))

        return legal_moves
    
    def wQ(self,selected_piece):
        legal_moves = self.move_queen(selected_piece)
        return legal_moves

    def bQ(self,selected_piece):
        legal_moves = self.move_queen(selected_piece)
        return legal_moves

    def move_queen(self,selected_piece):
        """
            Queens can move in straight lines, like rooks, and diagonally, like bishops
        """
        legal_moves = self.move_bishop(selected_piece)
        legal_moves += self.move_rook(selected_piece)
        return legal_moves

    def wK(self,selected_piece,check=True):
        legal_moves = self.move_king(selected_piece)
        if not check:
            all_moves = self.check_king_moves(selected_piece[0][0])
            legal_moves = [move for move in legal_moves if move not in all_moves]

        return legal_moves

    def bK(self,selected_piece,check=True):
        legal_moves = self.move_king(selected_piece)
        if not check:
            all_moves = self.check_king_moves(selected_piece[0][0])
            legal_moves = [move for move in legal_moves if move not in all_moves]

        return legal_moves

    def move_king(self,selected_piece):
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
                if self.board[new_y][new_x] == '':
                    legal_moves.append((new_x,new_y))
                elif self.board[new_y][new_x][0] != selected_piece[0][0]:
                    legal_moves.append((new_x,new_y))
                    
        return legal_moves
    
    def check_king_moves(self,piece):
        """
            This function gets all legal moves for all opposing team pieces
             and removes them from the list of legal_moves for the king.
        """
        colour_map = {'w':-1,'b':1}
        legal_moves = []
        for y,col in enumerate(self.board):
            for x,row in enumerate(col):
                # Check square is occupied and that 
                if row and row[0] != piece:
                    func = getattr(self, row)
                    selected_piece = (row, x, y)
                    if row[1] == 'P': # We only want to return the diagonal legal_moves for pawns as they can only take on the diagonal.
                        legal_moves += func(selected_piece,check_check=True,mult=colour_map[row[0]])
                    else:
                        legal_moves += func(selected_piece)
        return legal_moves
