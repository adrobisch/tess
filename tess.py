#!/usr/bin/env python3

import curses
import chess
import chess.pgn

# Example ASCII "shapes" for each piece. Here, each shape is a list of text
# lines. You can adjust these to your liking—larger shapes, different designs, etc.
# At minimum, each piece has a 3×3 shape in this example. Adjust as you see fit!
ASCII_PIECES = {
    'P': [
        " ^ ",
        "(P)",
        "/_\\"
    ],
    'N': [
        " __",
        "/ N",
        "\\_/"],
    'B': [
        "  ^",
        " /B\\",
        " \\_/"
    ],
    'R': [
        "[R]",
        "[R]",
        "[R]"
    ],
    'Q': [
        " Q ",
        "( )",
        " \\|"
    ],
    'K': [
        " K ",
        "(. )",
        " | "
    ],

    # Black pieces – you can tweak these to look different if you want
    'p': [
        " ^ ",
        "(p)",
        "/_\\"
    ],
    'n': [
        " __",
        "/ n",
        "\\_/"
    ],
    'b': [
        "  ^",
        " /b\\",
        " \\_/"
    ],
    'r': [
        "[r]",
        "[r]",
        "[r]"
    ],
    'q': [
        " q ",
        "( )",
        " \\|"
    ],
    'k': [
        " k ",
        "(. )",
        " | "
    ],
}

def init_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_MAGENTA) # Pink squares (white on magenta)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW) # Yellow squares (black on yellow)

def draw_piece_ascii(stdscr, piece_char, x, y, cell_width, cell_height, bg_color):
    """
    Draws the ASCII art for a given piece inside the cell at (x, y).
    piece_char is something like 'P', 'k', 'Q', etc.
    The ASCII art defined in ASCII_PIECES is placed in the center (if possible),
    or truncated/padded if cell_width / cell_height are small or large.
    """
    shape = ASCII_PIECES.get(piece_char)
    if not shape:
        # No shape defined, just return
        return
    
    shape_height = len(shape)
    shape_width = max(len(line) for line in shape)

    # Top-left offsets so we can center the piece if there's extra space
    offset_y = (cell_height - shape_height) // 2
    offset_x = (cell_width - shape_width) // 2
    
    for row_idx, row_text in enumerate(shape):
        # If the cell is smaller than the shape, we may need to clip
        if 0 <= offset_y + row_idx < cell_height:
            # Clip row_text if it’s longer than cell_width
            clipped = row_text[:cell_width]  
            stdscr.addstr(
                y + offset_y + row_idx,
                x + offset_x,
                clipped,
                bg_color
            )

def draw_chessboard(stdscr, board, cell_width=None, cell_height=None):
    """
    Draws the chessboard in the terminal using curses, but uses
    ASCII art to fill each cell with the piece (instead of a single
    Unicode character).
    """
    init_colors()

    while not board.is_game_over():
        stdscr.clear()

        # Get the available size of the window
        height, width = stdscr.getmaxyx()

        # Compute defaults if not provided
        if cell_width is None:
            # Leave at least 4 columns for rank/file labels
            cell_width = max(3, (width - 4) // 8)
        if cell_height is None:
            # Leave at least 4 rows for rank/file labels and prompt lines
            cell_height = max(3, (height - 4) // 8)

        # Validate that the board can fit
        required_width = 8 * cell_width + 4  # 3 for left offset + 1 spare
        required_height = 8 * cell_height + 4  # 1 for top offset + 1 for bottom labels + 2 spare
        if height < required_height or width < required_width:
            stdscr.addstr(0, 0, "Window too small to draw the chessboard.")
            stdscr.refresh()
            return

        # Draw the board squares and pieces
        for row in range(8):
            for col in range(8):
                # Offsets for drawing each cell
                x = col * cell_width + 3  # offset for file indicators
                y = row * cell_height + 1 # offset for rank indicators
                piece = board.piece_at(chess.square(col, 7 - row))

                # Use pink/yellow backgrounds in a checkerboard pattern
                if (row + col) % 2 == 0:
                    bg_color = curses.color_pair(2)  # Yellow square
                else:
                    bg_color = curses.color_pair(1)  # Pink square

                # Draw the cell background over all rows of cell_height
                for h_offset in range(cell_height):
                    # Fill entire cell row with spaces using the background color
                    stdscr.addstr(y + h_offset, x, ' ' * cell_width, bg_color)

                # If there's a piece, draw its ASCII art
                if piece:
                    draw_piece_ascii(
                        stdscr, piece.symbol(), 
                        x, y, 
                        cell_width, cell_height, 
                        bg_color
                    )

        # Draw rank (row) indicators on the left (8..1)
        for row in range(8):
            stdscr.addstr(row * cell_height + 1, 1, str(8 - row))

        # Draw file (column) indicators (A..H) at the bottom
        for col in range(8):
            stdscr.addstr(8 * cell_height + 2, col * cell_width + 3, chr(ord('A') + col))

        # Refresh to show the board update
        stdscr.refresh()

        # Prompt for the next move
        color = "White" if board.turn else "Black"
        prompt_y = 8 * cell_height + 4
        stdscr.addstr(prompt_y, 0, f"Enter {color}'s move (e.g., e4):")
        stdscr.clrtoeol()
        stdscr.refresh()

        # Read user input
        stdscr.move(prompt_y + 1, 0)
        stdscr.clrtoeol()
        curses.echo()
        move_str = stdscr.getstr(prompt_y + 1, 0).decode('utf-8')
        curses.noecho()

        # Parse the move
        try:
            san_move = board.parse_san(move_str)
            if san_move in board.legal_moves:
                board.push(san_move)
            else:
                stdscr.addstr(prompt_y + 2, 0, "Illegal move. Press any key to continue.")
                stdscr.refresh()
                stdscr.getch()
        except ValueError:
            stdscr.addstr(prompt_y + 2, 0, "Invalid or unrecognized move. Press any key.")
            stdscr.refresh()
            stdscr.getch()

    # Game is over
    stdscr.addstr(0, 0, "Game Over. Press any key to exit.")
    stdscr.refresh()
    stdscr.getch()

def main(pgn_file=None, cell_width=None, cell_height=None):
    """
    Main function which can load a PGN file or start a new game.
    Allows overriding cell_width and cell_height to control how large
    the board cells (and the ASCII art pieces) appear in the terminal.
    """
    # If a PGN file was provided, load the last position from that game
    if pgn_file:
        with open(pgn_file, 'r') as f:
            game = chess.pgn.read_game(f)
        board = game.board()
        for move in game.mainline_moves():
            board.push(move)
    else:
        board = chess.Board()

    curses.wrapper(draw_chessboard, board, cell_width, cell_height)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        print("Usage: python tess.py [pgn_file]")
        sys.exit(1)
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main()

