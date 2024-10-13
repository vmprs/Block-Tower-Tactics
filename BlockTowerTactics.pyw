import tkinter as tk
from tkinter import font as tkFont  # Importing the font module
from PIL import Image, ImageTk  # Pillow library for loading JPG images
import random

# Game constants
BOARD_WIDTH = 10  # Grid width
BOARD_HEIGHT = 20  # Grid height
CELL_SIZE = 30  # Size of each square cell
TICK_RATE = 500  # Milliseconds per game tick

# Define Tetromino shapes (each shape is a list of 4 coordinates)
SHAPES = {
    'I': [[1, 0], [1, 1], [1, 2], [1, 3]],
    'O': [[0, 0], [1, 0], [0, 1], [1, 1]],
    'T': [[1, 0], [0, 1], [1, 1], [2, 1]],
    'S': [[0, 1], [1, 1], [1, 0], [2, 0]],
    'Z': [[0, 0], [1, 0], [1, 1], [2, 1]],
    'L': [[1, 0], [1, 1], [1, 2], [2, 2]],
    'J': [[1, 0], [1, 1], [1, 2], [0, 2]],
}

# Colors for each Tetromino
COLORS = {
    'I': 'cyan',
    'O': 'yellow',
    'T': 'purple',
    'S': 'green',
    'Z': 'red',
    'L': 'orange',
    'J': 'blue',
}

class TetrisGame:
    def __init__(self, root):
        self.root = root
        self.root.title(""Block Tower Tactics")
        self.root.resizable(False, False)  # Prevent window resizing

        # Load background image from bg/bg0.jpg
        bg_image = Image.open("bg/bg0.jpg")
        bg_image = bg_image.resize((BOARD_WIDTH * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(bg_image)

        # Initialize game state
        self.canvas = tk.Canvas(root, width=BOARD_WIDTH * CELL_SIZE, height=BOARD_HEIGHT * CELL_SIZE)
        self.canvas.pack()

        # Create background image on the canvas
        self.canvas.create_image(0, 0, anchor='nw', image=self.bg_image)

        # Change the font to "Press Start 2P"
        self.font = ("Press Start 2P", 16)

        self.score_label = tk.Label(root, text=f"Score: 0", font=self.font)  # Updated font here
        self.score_label.pack()

        self.restart_button = tk.Button(root, text="Restart", font=self.font, command=self.restart_game)  # Updated font here
        self.restart_button.pack_forget()  # Hide restart button initially

        self.root.bind("<KeyPress>", self.handle_keypress)

        self.initialize_game()

    def initialize_game(self):
        """Initialize or reset the game state."""
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.current_shape = None
        self.current_color = None
        self.current_position = None
        self.score = 0
        self.running = True

        self.score_label.config(text=f"Score: {self.score}")
        self.spawn_tetromino()
        self.game_loop()

    def spawn_tetromino(self):
        """Spawn a new tetromino at the top of the board."""
        self.current_shape_name = random.choice(list(SHAPES.keys()))
        self.current_shape = SHAPES[self.current_shape_name]
        self.current_color = COLORS[self.current_shape_name]
        self.current_position = [0, BOARD_WIDTH // 2 - 2]

        if not self.valid_position(self.current_shape, self.current_position):
            self.end_game()  # Game over condition if new piece can't spawn

    def draw_board(self):
        """Draw the game board and current tetromino."""
        self.canvas.delete("all")

        # Re-draw the background image
        self.canvas.create_image(0, 0, anchor='nw', image=self.bg_image)

        # Draw the placed blocks
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x]:
                    self.canvas.create_rectangle(
                        x * CELL_SIZE, y * CELL_SIZE, 
                        (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE, 
                        fill=self.board[y][x], outline="gray"
                    )

        # Draw the current falling tetromino
        if self.current_shape:
            for block in self.current_shape:
                x, y = block
                cx = self.current_position[1] + x
                cy = self.current_position[0] + y
                self.canvas.create_rectangle(
                    cx * CELL_SIZE, cy * CELL_SIZE, 
                    (cx + 1) * CELL_SIZE, (cy + 1) * CELL_SIZE, 
                    fill=self.current_color, outline="gray"
                )

    def valid_position(self, shape, position):
        """Check if the current position of the tetromino is valid."""
        for block in shape:
            x, y = block
            cx = position[1] + x
            cy = position[0] + y
            if cx < 0 or cx >= BOARD_WIDTH or cy >= BOARD_HEIGHT or (cy >= 0 and self.board[cy][cx]):
                return False
        return True

    def move_tetromino(self, dx, dy):
        """Move the tetromino by dx (left/right) and dy (down)."""
        new_position = [self.current_position[0] + dy, self.current_position[1] + dx]
        if self.valid_position(self.current_shape, new_position):
            self.current_position = new_position
        elif dy > 0:  # If moving down and invalid, lock the piece
            self.lock_tetromino()

    def rotate_tetromino(self):
        """Rotate the current tetromino clockwise."""
        rotated_shape = [[-y, x] for x, y in self.current_shape]
        if self.valid_position(rotated_shape, self.current_position):
            self.current_shape = rotated_shape

    def rotate_tetromino_counterclockwise(self):
        """Rotate the current tetromino counterclockwise."""
        rotated_shape = [[y, -x] for x, y in self.current_shape]
        if self.valid_position(rotated_shape, self.current_position):
            self.current_shape = rotated_shape

    def lock_tetromino(self):
        """Lock the current tetromino in place and spawn a new one."""
        for block in self.current_shape:
            x, y = block
            cx = self.current_position[1] + x
            cy = self.current_position[0] + y
            if cy >= 0:
                self.board[cy][cx] = self.current_color

        # If any locked piece reaches the top row, end the game
        if any(self.board[0][x] is not None for x in range(BOARD_WIDTH)):
            self.end_game()
        else:
            self.clear_full_lines()
            self.spawn_tetromino()

    def clear_full_lines(self):
        """Clear any full lines and move blocks down."""
        new_board = [row for row in self.board if None in row]
        lines_cleared = BOARD_HEIGHT - len(new_board)
        self.score += lines_cleared * 100  # Add 100 points for each cleared line
        new_board = [[None] * BOARD_WIDTH for _ in range(lines_cleared)] + new_board
        self.board = new_board

        # Update score display
        self.score_label.config(text=f"Score: {self.score}")

    def handle_keypress(self, event):
        """Handle keypresses for controlling the game."""
        if event.keysym == "Left":
            self.move_tetromino(-1, 0)
        elif event.keysym == "Right":
            self.move_tetromino(1, 0)
        elif event.keysym == "Down":
            self.move_tetromino(0, 1)
        elif event.keysym == "Up":
            self.rotate_tetromino()  # Clockwise rotation
        elif event.keysym == "r":
            self.rotate_tetromino_counterclockwise()  # Counterclockwise rotation
        self.draw_board()

    def game_loop(self):
        """Main game loop, which moves the tetromino down."""
        if self.running:
            self.move_tetromino(0, 1)  # Move tetromino down
            self.draw_board()
            self.root.after(TICK_RATE, self.game_loop)

    def end_game(self):
        """End the game and show the restart button."""
        self.running = False
        self.canvas.create_text(BOARD_WIDTH * CELL_SIZE // 2, BOARD_HEIGHT * CELL_SIZE // 2, text="Game Over", fill="white", font=self.font)  # Updated font here
        self.restart_button.pack()  # Show the restart button

    def restart_game(self):
        """Restart the game by resetting the game state."""
        self.restart_button.pack_forget()  # Hide the restart button
        self.initialize_game()

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg='black')
    game = TetrisGame(root)
    root.mainloop()
