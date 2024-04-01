"""
    This is the main file. It is responsible for handling user inputs and displaying the current GameState object
"""

import pygame as p
import ChessEngine
import time

WIDTH = HEIGHT = 768
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
CIRC_OFFSET = SQ_SIZE / 2
CIRC_RADIUS = SQ_SIZE * 0.2
OCC_CIRC_RADIUS = SQ_SIZE / 2
OCC_CIRC_INNER_RADIUS = round(OCC_CIRC_RADIUS * 0.78)
MAX_FPS = 60 # Use for animations later on
IMAGES = {}
PROMOTION_SQ_SIZE = SQ_SIZE

"""
Initialise global dictionary of images.
"""
def loadImages():
    pieces = ['wP','wN','wB','wR','wQ','wK','bP','bN','bB','bR','bQ','bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f'sprites/{piece}.png'), (SQ_SIZE, SQ_SIZE))

"""
The main driver for our code. This will handle user inputs and update graphics
"""

def get_square_under_mouse(board):
    mouse_pos = p.Vector2(p.mouse.get_pos())
    x,y = [int(v) // SQ_SIZE for v in mouse_pos]

    try:
        if x>=0 and y>=0: return (board[y][x], x, y)
    except IndexError:
        pass
    # using x, y co-ords find out the square it is in
    return None, None, None

def drag(screen, board, selected_piece):
    if selected_piece and selected_piece[0]:
        piece, x, y = get_square_under_mouse(board)
        s1 = p.transform.scale(p.image.load(f'sprites/{selected_piece[0]}.png'), (SQ_SIZE, SQ_SIZE))
        pos = p.Vector2(p.mouse.get_pos())
        screen.blit(s1, s1.get_rect(center=pos))
        return (x, y)

def main():
    p.init()
    screen = p.display.set_mode([HEIGHT,WIDTH])
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    p.display.set_caption("Chess Engine")
    gs = ChessEngine.GameState()
    loadImages()

    selected_piece = None
    drop_pos = None
    running = True
    promotion_select = False
    promotion_x = ''
    promotion_y = ''
    promotion_clr = ''
    legal_squares = []
    while running:
        piece, x, y = get_square_under_mouse(gs.board)
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            if event.type ==  p.MOUSEBUTTONDOWN and not promotion_select:
                if event.button == 3:
                    pass
                elif event.button == 1:
                    selected_piece = piece, x, y
                    if selected_piece[0] and ((selected_piece[0][0] == 'w' and gs.whiteToMove) or (selected_piece[0][0] == 'b' and not gs.whiteToMove)):

                        lastPiece = selected_piece[0]
                        # Move calculations are labelled the same as pieces (e.g. wP move logic is function wP)
                        func_name = getattr(gs, selected_piece[0])
                        # Different logic for if a piece is a king as need to remove squares that make the king in check
                        if selected_piece[0][1] == 'K':
                            legal_squares = func_name(selected_piece,check=False,board=gs.board)
                        else:
                            legal_squares = func_name(selected_piece,board=gs.board)

                        if ((piece[0] == 'w' and gs.whiteCheck) or (piece[0] == 'b' and gs.blackCheck)):
                            if gs.checkMate:
                                print("Checkmate.")
                                legal_squares = []
                            else:

                                ### Only return legal squares for piece if it is in legalMovesInCheck list
                                if (x, y) in gs.legalMovesInCheck.keys():
                                    legal_squares = list(set(legal_squares) & set(gs.legalMovesInCheck[(x, y)]))
                                else:
                                    legal_squares = []
                        else:
                            ### For each legal square, make sure that it doesn't put the player in check
                            legal_squares_dict = {}
                            legal_squares_dict[(x, y)] = legal_squares
                            opp_colour = 'w' if piece[0] == 'b' else 'b'
                            safe_squares = gs.testCheckMoves(legal_squares_dict,colour=opp_colour)
                            if not safe_squares:
                                legal_squares = []
                            else:
                                legal_squares = list(set(safe_squares[(x, y)]) & set(legal_squares))

                        gs.board[y][x] = ''
                    else:
                        legal_squares = []
                        lastPiece = piece
                        selected_piece = ''

                    if not drop_pos:
                        og_x, og_y = x, y

            if event.type == p.MOUSEBUTTONUP and event.button == 1:
                if promotion_select:
                    y_difference = abs(y - promotion_y)
                    if promotion_x == x and y_difference < 4:
                        piece_map = {
                            0: 'Q',
                            1: 'R',
                            2: 'B',
                            3: 'N'
                        }
                        new_piece = piece_map[y_difference]
                        gs.board[promotion_y][promotion_x] = f"{promotion_clr}{new_piece}"

                        promotion_select = False
                        promotion_x = ''
                        promotion_y = ''
                        promotion_clr = ''

                        ## Calculate if in check - attackingPieces has a list of piece,x,y coords of all pieces getting player in check
                        colour = piece[0]
                        attackingPieces = gs.check_if_check(colour)
                        if attackingPieces:
                            gs.checkLegalMoves(attackingPieces,colour)

                elif drop_pos:
                    # Unable to move to that position as not in chessboard
                    if (drop_pos[0]==None) or (drop_pos not in legal_squares) or (og_x == x and og_y == y):

                        gs.board[og_y][og_x] = lastPiece
                        selected_piece = None
                        drop_pos = None

                    else:
                        # Add move to log
                        gs.update_moveLog(old=(og_x,og_y),new=(x,y))

                        # Remove piece from old position on board once moved
                        piece, old_x, old_y = selected_piece
                        gs.board[old_y][old_x] = ''
                        new_x, new_y = drop_pos
                        en_passant = True if gs.board[new_y][new_x] == '' and new_x!=old_x and piece[1]=='P' else False
                        gs.board[new_y][new_x] = piece
                        legal_squares = []
                        ### Captured piece is on a different square

                        if en_passant:
                            captured_x, captured_y = gs.capture_ep(drop_pos)
                            gs.board[captured_y][captured_x] = ''
                            
                        ## Logic for castling.
                        ## If king moves, no longer able to castle
                        if piece[1] == 'K':
                            if piece[0] == 'w':
                                gs.whiteCastleKS = False
                                gs.whiteCastleQS = False
                            else:
                                gs.blackCastleKS = False
                                gs.blackCastleQS = False
                            # Player is castling if abs value is 2, calling function to move rook over king
                            if abs(new_x - old_x) == 2:
                                gs.moveCastling(drop_pos)

                        ## Logic for removing ability to check if rook moves
                        if piece[1] == 'R':
                            castle_positions = {
                                (7, 0): 'blackCastleKS',
                                (0, 0): 'blackCastleQS',
                                (7, 7): 'whiteCastleKS',
                                (0, 7): 'whiteCastleQS',
                            }
                            if (old_x, old_y) in castle_positions:
                                setattr(gs, castle_positions[(old_x, old_y)], False)

                        ## Logic for promoting a pawn when it reaches the end of the board
                        if piece[1] == 'P' and new_y in [0, 7]:
                            promotion_select = True
                            promotion_x = new_x
                            promotion_y = new_y
                            promotion_clr = piece[0]

                        ## Calculate if in check - attackingPieces has a list of piece,x,y coords of all pieces getting player in check
                        colour = piece[0]
                        attackingPieces = gs.check_if_check(colour)
                        if attackingPieces:
                            gs.checkLegalMoves(attackingPieces,colour)

                        gs.whiteToMove = not gs.whiteToMove

                selected_piece = None
                drop_pos = None

            if event.type == p.KEYDOWN:
                if event.key == p.K_LEFT:
                    gs.undoMove()
                if event.key == p.K_RIGHT:
                    gs.redoMove()

        drawGameState(screen, gs,legal_squares,promotion_select,promotion_x,promotion_y)
        drop_pos = drag(screen, gs.board, selected_piece)
        clock.tick(MAX_FPS)
        p.display.flip()

def drawGameState(screen, gs, legal_squares,promotion_select,promotion_x,promotion_y):
    drawBoard(screen, legal_squares, gs.board) # draw squares on the board
    drawPieces(screen, gs.board) # draw pieces on the squares
    if promotion_select:
        drawPromotion(screen,(promotion_x,promotion_y))

"""
    Draw the squares on the board
"""

def drawBoard(screen,legal_squares, board):
    colours = [(235,236,208), (115,149,82)]
    legal_colours = [(202,203,179),(99,128,70)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            colour = colours[((r+c) % 2)]
            p.draw.rect(screen, colour, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
            # Note: p.Rect args are: x co-ord to begin. y co-ord to begin. size of x axis to draw. size of y axis to draw

            ### Highlight the squares with circle if they are legal squares
            if (c,r) in legal_squares:
                circ_colour = legal_colours[((r+c) % 2)]
                if board[r][c]: # occupied square
                    p.draw.circle(screen, circ_colour, (c*SQ_SIZE+CIRC_OFFSET, r*SQ_SIZE+CIRC_OFFSET), OCC_CIRC_RADIUS)
                    p.draw.circle(screen, colour, (c*SQ_SIZE+CIRC_OFFSET, r*SQ_SIZE+CIRC_OFFSET), OCC_CIRC_INNER_RADIUS)
                else: # empty square
                    p.draw.circle(screen, circ_colour, (c*SQ_SIZE+CIRC_OFFSET, r*SQ_SIZE+CIRC_OFFSET), CIRC_RADIUS)
            

"""
    Draw the pieces on the board using current GameState
"""

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece: # Not an empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
    Draw the promotion box when player is promoting a pawn
"""
def drawPromotion(screen,drop_pos):
    colour = (255,255,255)
    x, y = drop_pos
    piece_colour = 'w' if y == 0 else 'b'
    colour_mult = 1 if y == 0 else -1
    piece_list = ['Q','R','B','N']
    for c in range(4):
        y_coord = y + (c *colour_mult)
        p.draw.rect(screen, colour, p.Rect(x*PROMOTION_SQ_SIZE-1,y_coord*PROMOTION_SQ_SIZE,PROMOTION_SQ_SIZE+2,PROMOTION_SQ_SIZE))
        piece = f"{piece_colour}{piece_list[c]}"
        screen.blit(IMAGES[piece], p.Rect(x*PROMOTION_SQ_SIZE-1,y_coord*PROMOTION_SQ_SIZE,PROMOTION_SQ_SIZE+2,PROMOTION_SQ_SIZE))
        
    return True

if __name__ == '__main__':
    main()