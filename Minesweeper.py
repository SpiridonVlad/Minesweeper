"""
Minesweeper Game
================

A fully functional Minesweeper game implemented using Pygame. The game features a grid of cells
where the player must uncover cells without hitting mines. The player can place flags to mark
suspected mines, and the game provides visual feedback and a timer to track progress. This game
also includes a start screen for customizing the board dimensions and mine count.

Modules:
    - MinesweeperLogic: Handles the game logic, such as board setup, revealing cells, and win conditions.
    - Minesweeper: Implements the graphical interface and user interaction using Pygame.
    - StartScreen: Provides a start screen for inputting game settings.
    
Dependencies:
    - Pygame: Install it.

Author:
    Spiridon Vlad
"""

import pygame
import time
import random

CELL_SIZE = 30
VISIBLE_SIZE = 20
FONT_SIZE = 20
SCREEN_COLOR = (255, 255, 255)
LINE_COLOR = (0, 0, 0)
HIDDEN_CELL_COLOR = (200, 200, 200)
REVEALED_CELL_COLOR = (255, 255, 255)
MINE_COLOR = (255, 0, 0)
FLAG_COLOR = (255, 255, 0)
NUM_COLORS = {1: (0, 0, 255), 2: (0, 255, 0), 3: (255, 0, 0), 4: (0, 0, 128), 5: (128, 0, 0), 6: (0, 128, 128),
              7: (0, 0, 0), 8: (128, 128, 128)}

GAME_OVER_WIN = "You Win!"
GAME_OVER_LOSE = "Game Over!"


class MinesweeperLogic:
    """
    Handles the logic of the Minesweeper game.

    Attributes:
        rows (int): Number of rows in the game grid.
        cols (int): Number of columns in the game grid.
        mines (int): Total number of mines on the board.
        board (list): A 2D list representing the game board.
        mine_positions (set): A set containing the positions of mines.
        revealed (list): A 2D list indicating which cells are revealed.
        flags (list): A 2D list indicating which cells are flagged.

    Methods:
        initialize_board(): Initializes the board with mines and adjacent numbers.
        reveal_cell(r, c): Reveals a cell and returns whether it was successfully revealed.
        is_mine(r, c): Checks if a cell contains a mine.
        get_adjacent(r, c): Returns the number of adjacent mines for a cell.
        get_adjacent_cells(r, c): Yields the coordinates of adjacent cells.
        is_win(): Checks if the win condition is met.
    """
    
    def __init__(self, rows, cols, mines):
        """
        Initializes the MinesweeperLogic instance.

        Args:
            rows (int): Number of rows in the game grid.
            cols (int): Number of columns in the game grid.
            mines (int): Total number of mines on the board.
        """
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.mine_positions = set()
        self.revealed = [[False for _ in range(cols)] for _ in range(rows)]
        self.flags = [[False for _ in range(cols)] for _ in range(rows)]
        self.initialize_board()
    
    def initialize_board(self):
        """
        Initializes the game board with mines and calculates adjacent numbers.
        Uses Fisher-Yates shuffle for optimal mine placement and ensures the first click
        is never a mine by reserving space around the first click position.

        The board uses the following values:
        -1: Mine
         0: Empty cell with no adjacent mines
        1-8: Number of adjacent mines
        """
        
        def place_mines(first_click_row=None, first_click_col=None):
            self.board = [[0] * self.cols for _ in range(self.rows)]
            self.mine_positions.clear()
            
            all_positions = [(r, c) for r in range(self.rows)
                             for c in range(self.cols)]
            
            if first_click_row is not None and first_click_col is not None:
                protected_cells = {(first_click_row, first_click_col)}
                for row, coll in self.get_adjacent_cells(first_click_row, first_click_col):
                    protected_cells.add((row, coll))
                all_positions = [pos for pos in all_positions
                                 if pos not in protected_cells]
            
            positions_count = len(all_positions)
            for i in range(positions_count - 1, positions_count - self.mines - 1, -1):
                j = random.randint(0, i)
                all_positions[i], all_positions[j] = all_positions[j], all_positions[i]
                row, coll = all_positions[i]
                self.mine_positions.add((row, coll))
                self.board[row][coll] = -1
        
        def calculate_numbers():
            """Calculate the numbers for cells adjacent to mines."""
            directions = [(-1, -1), (-1, 0), (-1, 1),
                          (0, -1), (0, 1),
                          (1, -1), (1, 0), (1, 1)]
            
            for row in range(self.rows):
                for coll in range(self.cols):
                    if self.board[row][coll] == -1:
                        continue
                    
                    mine_count = 0
                    for dr, dc in directions:
                        new_r, new_c = row + dr, coll + dc
                        if (0 <= new_r < self.rows and
                                0 <= new_c < self.cols and
                                self.board[new_r][new_c] == -1):
                            mine_count += 1
                    
                    self.board[row][coll] = mine_count
        
        place_mines()
        calculate_numbers()
    
    def reveal_cell(self, row, coll):
        """
        Reveals a cell.

        Args:
            row (int): Row index of the cell.
            coll (int): Column index of the cell.

        Returns:
            bool: True if the cell was successfully revealed, False otherwise.
        """
        if self.revealed[row][coll] or self.flags[row][coll]:
            return False
        
        queue = [(row, coll)]
        while queue:
            cr, cc = queue.pop(0)
            if self.revealed[cr][cc]:
                continue
            
            self.revealed[cr][cc] = True
            
            if self.board[cr][cc] == 0:
                for nr, nc in self.get_adjacent_cells(cr, cc):
                    if not self.revealed[nr][nc] and not self.flags[nr][nc]:
                        queue.append((nr, nc))
        return True
    
    def is_mine(self, row, coll):
        """
        Checks if a cell contains a mine.

        Args:
            row (int): Row index of the cell.
            coll (int): Column index of the cell.

        Returns:
            bool: True if the cell contains a mine, False otherwise.
        """
        return (row, coll) in self.mine_positions
    
    def get_adjacent(self, row, coll):
        """
        Gets the number of adjacent mines for a cell.

        Args:
            row (int): Row index of the cell.
            coll (int): Column index of the cell.

        Returns:
            int: Number of adjacent mines.
        """
        return self.board[row][coll]
    
    def get_adjacent_cells(self, row, coll):
        """
        Yields the coordinates of adjacent cells.

        Args:
            row (int): Row index of the cell.
            coll (int): Column index of the cell.

        Yields:
            tuple: Coordinates (row, column) of adjacent cells.
        """
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = row + dr, coll + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield nr, nc
    
    def is_win(self):
        """
        Checks if the win condition is met.

        Returns:
            bool: True if all non-mine cells are revealed, False otherwise.
        """
        for row in range(self.rows):
            for coll in range(self.cols):
                if (row, coll) not in self.mine_positions and not self.revealed[row][coll]:
                    return False
        return True

class Minesweeper:
    """
    A class to represent the Minesweeper game.

    Attributes:
        rows (int): The number of rows in the game grid.
        cols (int): The number of columns in the game grid.
        mines (int): The number of mines in the game grid.
        visible_rows (int): The number of visible rows on the screen.
        visible_cols (int): The number of visible columns on the screen.
        width (int): The width of the game screen in pixels.
        height (int): The height of the game screen in pixels.
        screen (pygame.Surface): The main game screen.
        font (pygame.Font): Font used for rendering text in the game.
        logic (MinesweeperLogic): The logic handler for the game grid.
        running (bool): A flag indicating if the game loop is running.
        start_time (float): The time when the game started.
        game_over (bool): A flag indicating if the game has ended.
        win (bool): A flag indicating if the player has won.
        offset (tuple): The starting offset for the visible grid.
        color (dict): A dictionary of color values for the game elements.
    Methods:
        draw_background(): Draws the gradient background.
        draw_grid(): Draws the game grid.
        draw_timer(): Draws the game timer.
        handle_click(pos, right_click=False): Handles mouse clicks on the game grid.
        display_game_over(): Displays the game over message.
        move_view(dx, dy): Moves the visible grid view.
        run(): Main game loop for running the game.
    """
    def __init__(self, rows, cols, mines):
        """
        Initializes the Minesweeper game.
        Args:
            rows (int): Number of rows in the game grid.
            cols (int): Number of columns in the game grid.
            mines (int): Total number of mines on the board.
        """
        pygame.init()
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.visible_rows = min(VISIBLE_SIZE, rows)
        self.visible_cols = min(VISIBLE_SIZE, cols)
        
        self.cell_size = CELL_SIZE
        self.grid_width = self.visible_cols * self.cell_size
        self.grid_height = self.visible_rows * self.cell_size
        
        self.width = max(self.grid_width + 40, 360)
        self.height = self.grid_height + 100
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Minesweeper")
        self.font = pygame.font.Font(None, 24)
        self.logic = MinesweeperLogic(rows, cols, mines)
        self.running = True
        self.start_time = time.time()
        self.game_over = False
        self.win = False
        self.offset = (0, 0)
        
        self.color = {
                "background"   : (240, 240, 240),
                "border_light" : (255, 255, 255),
                "border_dark"  : (160, 160, 160),
                "border_shadow": (200, 200, 200),
                "text"         : (60, 60, 60),
                "title_bg"     : (0, 120, 215),
                "cell_revealed": (255, 255, 255),
                "cell_hidden"  : (240, 240, 240),
                "mine_color"   : (200, 0, 0),
                "flag_color"   : (0, 120, 215),
                "num_colors"   : {
                        1: (0, 120, 215),
                        2: (0, 140, 0),
                        3: (200, 0, 0),
                        4: (0, 0, 140),
                        5: (140, 0, 0),
                        6: (0, 140, 140),
                        7: (140, 0, 140),
                        8: (60, 60, 60),
                }
        }
        
        self.grid_area = pygame.Rect(
            20,
            48,
            self.grid_width,
            self.grid_height
        )
    
    def draw_3d_rect(self, rect, raised=True):
        """Draws a modern-style rectangle with subtle shadows.
        Args:
        	rect (pygame.Rect): The rectangle to draw.
			raised(bool): Whether the rectangle should appear raised or sunken.
        """
        pygame.draw.rect(self.screen, self.color["background"], rect)
        
        if raised:
            pygame.draw.line(self.screen, self.color["border_light"], rect.topleft, rect.topright)
            pygame.draw.line(self.screen, self.color["border_light"], rect.topleft, rect.bottomleft)
            pygame.draw.line(self.screen, self.color["border_dark"], rect.bottomleft, rect.bottomright)
            pygame.draw.line(self.screen, self.color["border_dark"], rect.topright, rect.bottomright)
        else:
            pygame.draw.line(self.screen, self.color["border_shadow"], rect.topleft, rect.topright)
            pygame.draw.line(self.screen, self.color["border_shadow"], rect.topleft, rect.bottomleft)
            pygame.draw.line(self.screen, self.color["border_light"], rect.bottomleft, rect.bottomright)
            pygame.draw.line(self.screen, self.color["border_light"], rect.topright, rect.bottomright)
    
    def draw_background(self):
        """Draws a solid background with title bar."""
        self.screen.fill(self.color["background"])
        
        title_rect = pygame.Rect(0, 0, self.width, 28)
        pygame.draw.rect(self.screen, self.color["title_bg"], title_rect)
        title_text = self.font.render("Minesweeper", True, (255, 255, 255))
        self.screen.blit(title_text, (10, 4))
        
        shadow_rect = self.grid_area.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(self.screen, self.color["border_shadow"], shadow_rect)
        self.draw_3d_rect(self.grid_area)
    
    def draw_grid(self):
        """Draws the Minesweeper grid with modern 3D effects."""
        start_row, start_col = self.offset
        
        for row in range(start_row, min(start_row + self.visible_rows, self.rows)):
            for col in range(start_col, min(start_col + self.visible_cols, self.cols)):
                x = self.grid_area.x + (col - start_col) * self.cell_size
                y = self.grid_area.y + (row - start_row) * self.cell_size
                
                cell_rect = pygame.Rect(x, y, self.cell_size - 1, self.cell_size - 1)
                
                if self.logic.revealed[row][col]:
                    pygame.draw.rect(self.screen, self.color["cell_revealed"], cell_rect)
                    self.draw_3d_rect(cell_rect, raised=False)
                    
                    if self.logic.is_mine(row, col):
                        mine_size = self.cell_size // 3
                        pygame.draw.circle(self.screen, self.color["mine_color"],
                                           (x + self.cell_size // 2, y + self.cell_size // 2), mine_size)
                    else:
                        value = self.logic.get_adjacent(row, col)
                        if value > 0:
                            text = self.font.render(str(value), True, self.color["num_colors"][value])
                            text_rect = text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                            self.screen.blit(text, text_rect)
                else:
                    pygame.draw.rect(self.screen, self.color["cell_hidden"], cell_rect)
                    self.draw_3d_rect(cell_rect, raised=True)
                    
                    if self.logic.flags[row][col]:
                        flag_size = self.cell_size // 3
                        pygame.draw.circle(self.screen, self.color["flag_color"],
                                           (x + self.cell_size // 2, y + self.cell_size // 2), flag_size)
    
    def draw_timer(self):
        """Draws the timer with modern styling."""
        elapsed = int(time.time() - self.start_time)
        timer_text = f"Time: {elapsed}s"
        timer_rect = pygame.Rect(20, self.height - 40, 100, 24)
        self.draw_3d_rect(timer_rect, raised=False)
        text = self.font.render(timer_text, True, self.color["text"])
        text_rect = text.get_rect(center=timer_rect.center)
        self.screen.blit(text, text_rect)
        if elapsed > 120:
            self.game_over = True
            self.win = False
    
    def display_game_over(self):
        """Displays the game over message with modern styling."""
        msg = "You Win!" if self.win else "Game Over!"
        msg_rect = pygame.Rect(self.width // 2 - 80, self.height - 40, 160, 24)
        self.draw_3d_rect(msg_rect)
        text = self.font.render(msg, True, self.color["title_bg"] if self.win else self.color["mine_color"])
        text_rect = text.get_rect(center=msg_rect.center)
        self.screen.blit(text, text_rect)
    
    def handle_click(self, pos, right_click=False):
        """Handles mouse clicks on the game grid.
        Args:
			pos (tuple): The position of the mouse click.
			right_click (bool): Whether the click is a right-click.
        """
        if self.game_over:
            return
        
        grid_x = pos[0] - self.grid_area.x
        grid_y = pos[1] - self.grid_area.y
        
        if grid_x < 0 or grid_y < 0:
            return
        
        col = grid_x // self.cell_size + self.offset[1]
        row = grid_y // self.cell_size + self.offset[0]
        
        if row >= self.rows or col >= self.cols:
            return
        
        if right_click:
            self.logic.flags[row][col] = not self.logic.flags[row][col]
        else:
            if not self.logic.reveal_cell(row, col):
                return
            
            if self.logic.is_mine(row, col):
                self.game_over = True
                self.win = False
            else:
                value = self.logic.get_adjacent(row, col)
                if value == 0:
                    for nr, nc in self.logic.get_adjacent_cells(row, col):
                        screen_x = (nc - self.offset[1]) * self.cell_size
                        screen_y = (nr - self.offset[0]) * self.cell_size
                        self.handle_click((screen_x + self.grid_area.x, screen_y + self.grid_area.y))
        
        if self.logic.is_win():
            self.game_over = True
            self.win = True
    
    def move_view(self, dx, dy):
        """Moves the visible portion of the grid."""
        new_row = self.offset[0] + dy
        new_col = self.offset[1] + dx
        
        max_row = max(0, self.rows - self.visible_rows)
        max_col = max(0, self.cols - self.visible_cols)
        
        if 0 <= new_row <= max_row:
            self.offset = (new_row, self.offset[1])
        if 0 <= new_col <= max_col:
            self.offset = (self.offset[0], new_col)
    
    def run(self):
        """Main game loop with modern styling."""
        clock = pygame.time.Clock()
        while self.running:
            self.draw_background()
            self.draw_grid()
            self.draw_timer()
            
            if self.game_over:
                self.display_game_over()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.grid_area.collidepoint(event.pos):
                        if event.button == 1:
                            self.handle_click(event.pos)
                        elif event.button == 3:
                            self.handle_click(event.pos, right_click=True)
                elif event.type == pygame.KEYDOWN:
                    if self.game_over and event.key == pygame.K_RETURN:
                        return True
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                        dx = (event.key == pygame.K_RIGHT) - (event.key == pygame.K_LEFT)
                        dy = (event.key == pygame.K_DOWN) - (event.key == pygame.K_UP)
                        self.move_view(dx, dy)
            
            pygame.display.flip()
            clock.tick(30)
        
        pygame.quit()
        return False

class StartScreen:
    """ A class to represent the start screen for the Minesweeper game.
    Attributes:
        screen (pygame.Surface): The main game screen.
        font (pygame.Font): Font used for rendering text on the screen.
        running (bool): A flag indicating if the start screen loop is running.
        colors (dict): A dictionary of color values for the start screen elements.
        difficulties (list): A list of difficulty settings for the game.
        selected_difficulty (int): The index of the selected difficulty setting.
        custom_values (dict): A dictionary of custom board dimensions.
        active_custom_field (str): The active custom field for input.
        window_rect (pygame.Rect): The rectangle representing the start screen window.
        custom_boxes (list): A list of custom input boxes for board dimensions.
    Methods:
        draw_3d_rect(rect, raised=True): Draws a modern-style rectangle with subtle shadows.
        draw(): Draws the start screen with difficulty options and custom settings.
        handle_input(event): Handles mouse clicks and keyboard input on the start screen.
        run(): Runs the start screen and returns the selected game settings.
    """
    def __init__(self, screen, font):
        """Initializes a new instance of the StartScreen class.
        Args:
            screen (pygame.Surface): The main game screen.
            font (pygame.Font): Font used for rendering text on the screen.
        """
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.running = True
        
        self.colors = {
                'background'   : (240, 240, 240),
                'border_light' : (255, 255, 255),
                'border_dark'  : (160, 160, 160),
                'border_shadow': (200, 200, 200),
                'text'         : (60, 60, 60),
                'selected'     : (0, 120, 215),
                'title_bg'     : (0, 120, 215)
        }
        
        self.difficulties = [
                {"name": "Beginner", "rows": 9, "cols": 9},
                {"name": "Intermediate", "rows": 16, "cols": 16},
                {"name": "Expert", "rows": 16, "cols": 30},
                {"name": "Custom", "rows": 50, "cols": 50}
        ]
        
        self.selected_difficulty = 0
        self.custom_values = {
                "rows": "50",
                "cols": "50"
        }
        self.active_custom_field = None
        
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        self.window_rect = pygame.Rect(
            screen_width // 2 - 180,
            screen_height // 2 - 130,
            360,
            260
        )
        
        base_y = self.window_rect.y + 160
        self.custom_boxes = [
                {"label": "Height:", "key": "rows", "rect": pygame.Rect(self.window_rect.x + 130, base_y, 50, 22)},
                {"label": "Width:", "key": "cols", "rect": pygame.Rect(self.window_rect.x + 130, base_y + 30, 50, 22)}
        ]
    
    def draw_3d_rect(self, rect, raised=True):
        """Draws a modern-style rectangle with subtle shadows.
        Args:
            rect (pygame.Rect): The rectangle to draw.
            raised(bool): Whether the rectangle should appear raised or sunken.
        """
        pygame.draw.rect(self.screen, self.colors['background'], rect)
        
        if raised:
            pygame.draw.line(self.screen, self.colors['border_light'], rect.topleft, rect.topright)
            pygame.draw.line(self.screen, self.colors['border_light'], rect.topleft, rect.bottomleft)
            pygame.draw.line(self.screen, self.colors['border_dark'], rect.bottomleft, rect.bottomright)
            pygame.draw.line(self.screen, self.colors['border_dark'], rect.topright, rect.bottomright)
        else:
            pygame.draw.line(self.screen, self.colors['border_shadow'], rect.topleft, rect.topright)
            pygame.draw.line(self.screen, self.colors['border_shadow'], rect.topleft, rect.bottomleft)
            pygame.draw.line(self.screen, self.colors['border_light'], rect.bottomleft, rect.bottomright)
            pygame.draw.line(self.screen, self.colors['border_light'], rect.topright, rect.bottomright)
    
    def draw(self):
        """Draws the start screen with difficulty options and custom settings."""
        self.screen.fill(self.colors['background'])
        
        shadow_rect = self.window_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(self.screen, self.colors['border_shadow'], shadow_rect)
        self.draw_3d_rect(self.window_rect)
        
        title_rect = pygame.Rect(self.window_rect.x, self.window_rect.y, self.window_rect.width, 28)
        pygame.draw.rect(self.screen, self.colors['title_bg'], title_rect)
        title_text = self.font.render("Game Difficulty", True, (255, 255, 255))
        self.screen.blit(title_text, (title_rect.x + 10, title_rect.y + 4))
        
        base_y = self.window_rect.y + 45
        for i, diff in enumerate(self.difficulties):
            option_rect = pygame.Rect(self.window_rect.x + 20, base_y + i * 28, 14, 14)
            pygame.draw.rect(self.screen, (255, 255, 255), option_rect)
            pygame.draw.rect(self.screen, self.colors['border_dark'], option_rect, 1)
            
            if i == self.selected_difficulty:
                inner_rect = pygame.Rect(option_rect.x + 3, option_rect.y + 3, 8, 8)
                pygame.draw.rect(self.screen, self.colors['selected'], inner_rect)
            
            text = self.font.render(diff["name"], True, self.colors['text'])
            self.screen.blit(text, (option_rect.x + 22, option_rect.y - 1))
        
        if self.selected_difficulty == 3:
            for box in self.custom_boxes:
                label_text = self.font.render(box["label"], True, self.colors['text'])
                self.screen.blit(label_text, (self.window_rect.x + 45, box["rect"].y + 2))
                
                pygame.draw.rect(self.screen, (255, 255, 255), box["rect"])
                pygame.draw.rect(self.screen, self.colors['border_dark'], box["rect"], 1)
                value_text = self.font.render(self.custom_values[box["key"]], True, self.colors['text'])
                self.screen.blit(value_text, (box["rect"].x + 4, box["rect"].y + 3))
        
        button_y = self.window_rect.y + self.window_rect.height - 38
        for i, text in enumerate(["OK", "Cancel"]):
            button_rect = pygame.Rect(
                self.window_rect.x + self.window_rect.width - 160 + i * 80,
                button_y,
                65,
                24
            )
            self.draw_3d_rect(button_rect)
            button_text = self.font.render(text, True, self.colors['text'])
            text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, text_rect)
    
    def handle_input(self, event):
        """Handles mouse clicks and keyboard input on the start screen.
        Args:
            event (pygame.event.Event): The event to handle.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            base_y = self.window_rect.y + 45
            for i in range(len(self.difficulties)):
                option_rect = pygame.Rect(self.window_rect.x + 20, base_y + i * 28, 14, 14)
                if option_rect.collidepoint(mouse_pos):
                    self.selected_difficulty = i
                    return
            
            if self.selected_difficulty == 3:
                for box in self.custom_boxes:
                    if box["rect"].collidepoint(mouse_pos):
                        self.active_custom_field = box["key"]
                        return
            
            button_y = self.window_rect.y + self.window_rect.height - 38
            ok_button = pygame.Rect(self.window_rect.x + self.window_rect.width - 160, button_y, 65, 24)
            cancel_button = pygame.Rect(self.window_rect.x + self.window_rect.width - 80, button_y, 65, 24)
            
            if ok_button.collidepoint(mouse_pos):
                self.running = False
            elif cancel_button.collidepoint(mouse_pos):
                pygame.quit()
                exit()
        
        elif event.type == pygame.KEYDOWN and self.selected_difficulty == 3 and self.active_custom_field:
            if event.key == pygame.K_BACKSPACE:
                current = self.custom_values[self.active_custom_field]
                self.custom_values[self.active_custom_field] = current[:-1]
            elif event.unicode.isdigit():
                current = self.custom_values[self.active_custom_field]
                self.custom_values[self.active_custom_field] = current + event.unicode
    
    def run(self):
        """Runs the start screen and returns the selected rows and cols."""
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                self.handle_input(event)
            
            self.draw()
            pygame.display.flip()
            clock.tick(30)
        
        if self.selected_difficulty == 3:
            return (
                    int(self.custom_values["rows"]),
                    int(self.custom_values["cols"])
            )
        else:
            difficulty = self.difficulties[self.selected_difficulty]
            return difficulty["rows"], difficulty["cols"]

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    font = pygame.font.Font(None, FONT_SIZE * 2)
    
    start_screen = StartScreen(screen, font)
    rows, cols = start_screen.run()
    mines = int(rows * cols * 0.30)
    while True:
        game = Minesweeper(rows=rows, cols=cols, mines=mines)
        if not game.run():
            break
