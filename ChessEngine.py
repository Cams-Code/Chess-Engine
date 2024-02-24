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

    def wP(self,selected_piece):
        mult = -1
        legal_moves = self.move_pawn(selected_piece,mult)
        return legal_moves
        
    def bP(self,selected_piece):
        mult = 1
        legal_moves = self.move_pawn(selected_piece,mult)
        return legal_moves
    
    def move_pawn(self,selected_piece:tuple,mult:int):
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
        """
        legal_moves = []
        # Implementation of point 1
        if not self.board[selected_piece[2]+(1*mult)][selected_piece[1]]:
            legal_moves.append((selected_piece[1], selected_piece[2]+(1*mult)))
        # Implementation of point 2
        if (selected_piece[0][0] == 'b' and selected_piece[2] == 1) or (selected_piece[0][0] == 'w' and selected_piece[2] == 6):
            if not self.board[selected_piece[2]+(2*mult)][selected_piece[1]]:
                legal_moves.append((selected_piece[1], selected_piece[2]+(2*mult)))

        # Implementation of point 3
        diagonals = [[selected_piece[1]-1,selected_piece[2]+(1*mult)],[selected_piece[1]+1,selected_piece[2]+(1*mult)]]
        for diag in diagonals:
            piece = self.board[diag[1]][diag[0]]
            if piece and piece[0] != selected_piece[0][0]:
                legal_moves.append((diag[0],diag[1]))

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