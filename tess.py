import curses
import chess.pgn

def draw_chessboard(stdscr, board):
    # Clear screen
    stdscr.clear()

    # Get the size of the window
    height, width = stdscr.getmaxyx()

    # Ensure the window is big enough to draw an 8x8 chessboard
    if height < 10 or width < 21:
        stdscr.addstr(0, 0, "Window too small to draw chessboard.")
        stdscr.refresh()
        return

    # Define the size of each cell
    cell_width = 2
    cell_height = 1

    # Draw the chessboard
    for row in range(8):
        for col in range(8):
            x = col * cell_width + 3  # Add offset for file indicators
            y = row * cell_height + 1  # Add offset for rank indicators on the top
            piece = board.piece_at(chess.square(col, 7 - row))
            if (row + col) % 2 == 0:
                stdscr.addstr(y, x, '  ', curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, '  ')
            if piece:
                stdscr.addstr(y, x, piece.symbol())

    # Draw rank indicators on the top
    for row in range(8):
        stdscr.addstr(row + 1, 1, str(8 - row))

    # Draw file indicators on the bottom
    for col in range(8):
        stdscr.addstr(9, col * cell_width + 3, chr(ord('A') + col))

    # Refresh the screen to show the chessboard
    stdscr.refresh()

    # Wait for user input to exit
    stdscr.getch()

def main(pgn_file):
    # Read the PGN file
    with open(pgn_file, 'r') as f:
        game = chess.pgn.read_game(f)

    # Get the last position of the game
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)

    # Initialize curses application
    curses.wrapper(draw_chessboard, board)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python chessboard.py <pgn_file>")
        sys.exit(1)
    main(sys.argv[1])
