import curses
import chess.pgn

# Unicode characters for chess pieces
PIECE_UNICODE = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}

def draw_chessboard(stdscr, board):
    while not board.is_game_over():
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
                    bg_color = curses.A_REVERSE
                else:
                    bg_color = curses.A_NORMAL
                stdscr.addstr(y, x, '  ', bg_color)
                if piece:
                    stdscr.addstr(y, x, PIECE_UNICODE[piece.symbol()], bg_color)

        # Draw rank indicators on the top
        for row in range(8):
            stdscr.addstr(row + 1, 1, str(8 - row))

        # Draw file indicators on the bottom
        for col in range(8):
            stdscr.addstr(9, col * cell_width + 3, chr(ord('A') + col))

        # Refresh the screen to show the chessboard
        stdscr.refresh()

        # Get user input for the next move
        color = "White" if board.turn else "Black"
        stdscr.addstr(11, 0, f"Enter {color}'s move (e.g., e4):")
        stdscr.refresh()
        stdscr.addstr(12, 0, "")
        curses.echo()
        move_str = stdscr.getstr(12, 0).decode('utf-8')
        curses.noecho()

        try:
            move = chess.Move.from_uci(board.parse_san(move_str).uci())
            if move in board.legal_moves:
                board.push(move)
            else:
                stdscr.addstr(13, 0, "Illegal move. Press any key to continue.")
                stdscr.refresh()
                stdscr.getch()
        except ValueError:
            stdscr.addstr(13, 0, "Invalid move format. Press any key to continue.")
            stdscr.refresh()
            stdscr.getch()

    # Display the final position
    stdscr.addstr(11, 0, "Game Over. Press any key to exit.")
    stdscr.refresh()
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
