"""
    This is the main file. It is responsible for handling user inputs and displaying the current GameState object
"""

import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
CIRC_RADIUS = 15
OCC_CIRC_RADIUS = 25
OCC_CIRC_WIDTH = 5
MAX_FPS = 120 # Use for animations later on
IMAGES = {}

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

def format_legal_squares(screen,legal_moves):
    for move_set in legal_moves:
        x,y = move_set[0],move_set[1]
        p.draw.circle(screen, (200,0,0), (x*SQ_SIZE, y*SQ_SIZE), CIRC_RADIUS)
        p.display.update()

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
    legal_squares = []
    while running:
        piece, x, y = get_square_under_mouse(gs.board)
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            if event.type ==  p.MOUSEBUTTONDOWN:
                selected_piece = piece, x, y
                if selected_piece[0]:
                    # Move calculations are labelled the same as pieces (e.g. wP move logic is function wP)
                    func_name = getattr(gs, selected_piece[0])
                    # Different logic for if a piece is a king as need to remove squares that make the king in check
                    if selected_piece[0][1] == 'K':
                        legal_squares = func_name(selected_piece,check=False)
                    else:
                        legal_squares = func_name(selected_piece)
                else:
                    legal_squares = []
                # format_legal_squares(screen,legal_squares)
                if not drop_pos:
                    og_x, og_y = x, y
                gs.board[y][x] = ''
            if event.type == p.MOUSEBUTTONUP:
                if drop_pos:
                    # Unable to move to that position as not in chessboard
                    if drop_pos[0]==None or drop_pos not in legal_squares:
                        gs.board[og_y][og_x] = selected_piece[0]
                        selected_piece = None
                        drop_pos = None
                        
                    else:
                        # Remove piece from old position on board once moved

                        piece, old_x, old_y = selected_piece
                        gs.board[old_y][old_x] = ''
                        new_x, new_y = drop_pos
                        gs.board[new_y][new_x] = piece
                        
                legal_squares = []
                selected_piece = None
                drop_pos = None

        drawGameState(screen, gs)
        # format_legal_squares(screen,legal_squares)
        drop_pos = drag(screen, gs.board, selected_piece)
        clock.tick(MAX_FPS)
        p.display.flip()

def drawGameState(screen, gs):
    drawBoard(screen) # draw squares on the board
    drawPieces(screen, gs.board) # draw pieces on the squares

"""
    Draw the squares on the board
"""

def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
            # Note: p.Rect args are: x co-ord to begin. y co-ord to begin. size of x axis to draw. size of y axis to draw

"""
    Draw the pieces on the board using current GameState
"""

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece: # Not an empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == '__main__':
    main()