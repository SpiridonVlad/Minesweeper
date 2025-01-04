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

How to Run:
    - Run the script directly to play the game.
    - Customize the rows, columns, and mines through the start screen interface.

Dependencies:
    - Pygame: Install it using `pip install pygame`.

Author:
    Spiridon Vlad
"""

import pygame
from random import sample
import time

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
		import random
		
		def place_mines(first_click_row=None, first_click_col=None):
			self.board = [[0] * self.cols for _ in range(self.rows)]
			self.mine_positions.clear()
			
			all_positions = [(r, c) for r in range(self.rows)
			                 for c in range(self.cols)]
			
			if first_click_row is not None and first_click_col is not None:
				protected_cells = {(first_click_row, first_click_col)}
				for r, c in self.get_adjacent_cells(first_click_row, first_click_col):
					protected_cells.add((r, c))
				all_positions = [pos for pos in all_positions
				                 if pos not in protected_cells]
			
			positions_count = len(all_positions)
			for i in range(positions_count - 1, positions_count - self.mines - 1, -1):
				j = random.randint(0, i)
				all_positions[i], all_positions[j] = all_positions[j], all_positions[i]
				r, c = all_positions[i]
				self.mine_positions.add((r, c))
				self.board[r][c] = -1
		
		def calculate_numbers():
			"""Calculate the numbers for cells adjacent to mines."""
			directions = [(-1, -1), (-1, 0), (-1, 1),
			              (0, -1), (0, 1),
			              (1, -1), (1, 0), (1, 1)]
			
			for r in range(self.rows):
				for c in range(self.cols):
					if self.board[r][c] == -1:
						continue
					
					mine_count = 0
					for dr, dc in directions:
						new_r, new_c = r + dr, c + dc
						if (0 <= new_r < self.rows and
								0 <= new_c < self.cols and
								self.board[new_r][new_c] == -1):
							mine_count += 1
					
					self.board[r][c] = mine_count
		
		place_mines()
		calculate_numbers()
		
		self._initial_setup = lambda r, c: (place_mines(r, c), calculate_numbers())
	
	def reveal_cell(self, r, c):
		"""
		Reveals a cell.

		Args:
			r (int): Row index of the cell.
			c (int): Column index of the cell.

		Returns:
			bool: True if the cell was successfully revealed, False otherwise.
		"""
		if self.revealed[r][c] or self.flags[r][c]:
			return False
		
		queue = [(r, c)]
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
	
	def is_mine(self, r, c):
		"""
		Checks if a cell contains a mine.

		Args:
			r (int): Row index of the cell.
			c (int): Column index of the cell.

		Returns:
			bool: True if the cell contains a mine, False otherwise.
		"""
		return (r, c) in self.mine_positions
	
	def get_adjacent(self, r, c):
		"""
		Gets the number of adjacent mines for a cell.

		Args:
			r (int): Row index of the cell.
			c (int): Column index of the cell.

		Returns:
			int: Number of adjacent mines.
		"""
		return self.board[r][c]
	
	def get_adjacent_cells(self, r, c):
		"""
		Yields the coordinates of adjacent cells.

		Args:
			r (int): Row index of the cell.
			c (int): Column index of the cell.

		Yields:
			tuple: Coordinates (row, column) of adjacent cells.
		"""
		for dr in [-1, 0, 1]:
			for dc in [-1, 0, 1]:
				nr, nc = r + dr, c + dc
				if 0 <= nr < self.rows and 0 <= nc < self.cols:
					yield nr, nc
	
	def is_win(self):
		"""
		Checks if the win condition is met.

		Returns:
			bool: True if all non-mine cells are revealed, False otherwise.
		"""
		for r in range(self.rows):
			for c in range(self.cols):
				if (r, c) not in self.mine_positions and not self.revealed[r][c]:
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
				Initializes a new instance of the Minesweeper class.

				Args:
					rows (int): The number of rows in the grid.
					cols (int): The number of columns in the grid.
					mines (int): The number of mines to place in the grid.
		"""
		pygame.init()
		self.rows = rows
		self.cols = cols
		self.mines = mines
		self.visible_rows = min(VISIBLE_SIZE, rows)
		self.visible_cols = min(VISIBLE_SIZE, cols)
		self.width = self.visible_cols * CELL_SIZE
		self.height = self.visible_rows * CELL_SIZE + 50
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption("Minesweeper")
		self.font = pygame.font.Font(None, FONT_SIZE * 2)
		self.logic = MinesweeperLogic(rows, cols, mines)
		self.running = True
		self.start_time = time.time()
		self.game_over = False
		self.win = False
		self.offset = (0, 0)
		
		# Color
		self.color = {
			"background_color_top": (10, 10, 50),
			"background_color_bottom": (20, 20, 100),
			"hidden_cell_color": (70, 70, 70),
			"revealed_cell_color": (180, 180, 180),
			"line_color": (100, 100, 100),
			"mine_color": (200, 0, 0),
			"flag_color": (0, 150, 200),
			"num_colors": {
					1: (0, 255, 0),
					2: (255, 255, 0),
					3: (255, 0, 0),
					4: (0, 255, 255),
					5: (255, 0, 255),
					6: (0, 0, 255),
					7: (255, 255, 255),
					8: (100, 100, 100),
			}
		}
		
		icon = pygame.image.load("icon.png")
		pygame.display.set_icon(icon)
	
	def draw_background(self):
		"""
		Draws a gradient background on the game screen.
		"""
		for y in range(self.height):
			blend = y / self.height
			color = (
					int(self.color["background_color_top"][0] * (1 - blend) + self.color["background_color_bottom"][0] * blend),
					int(self.color["background_color_top"][1] * (1 - blend) + self.color["background_color_bottom"][1] * blend),
					int(self.color["background_color_top"][2] * (1 - blend) + self.color["background_color_bottom"][2] * blend),
			)
			pygame.draw.line(self.screen, color, (0, y), (self.width, y))
	
	def draw_grid(self):
		"""
		Draws the Minesweeper grid, including hidden and revealed cells, mines, and numbers.
		"""
		start_row, start_col = self.offset
		for r in range(start_row, start_row + self.visible_rows):
			for c in range(start_col, start_col + self.visible_cols):
				if r >= self.rows or c >= self.cols:
					continue
				x, y = (c - start_col) * CELL_SIZE, (r - start_row) * CELL_SIZE
				cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
				
				if self.logic.revealed[r][c]:
					pygame.draw.rect(self.screen, self.color["revealed_cell_color"], cell_rect)
					if self.logic.is_mine(r, c):
						pygame.draw.circle(self.screen, self.color["mine_color"], cell_rect.center, CELL_SIZE // 3)
					else:
						value = self.logic.get_adjacent(r, c)
						if value > 0:
							text = self.font.render(str(value), True, self.color["num_colors"].get(value, (255, 255, 255)))
							self.screen.blit(
								text,
								text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2)),
							)
				else:
					pygame.draw.rect(self.screen, self.color["hidden_cell_color"], cell_rect)
					if self.logic.flags[r][c]:
						pygame.draw.circle(self.screen, self.color["flag_color"], cell_rect.center, CELL_SIZE // 3)
				
				shadow_rect = cell_rect.inflate(-2, -2)
				pygame.draw.rect(self.screen, self.color["line_color"], shadow_rect, 1)
	
	def draw_timer(self):
		"""
		Draws the elapsed time on the screen.
		"""
		elapsed = int(time.time() - self.start_time)
		timer_text = f"Time: {elapsed}s"
		text_surface = self.font.render(timer_text, True, (200, 200, 200))
		text_rect = text_surface.get_rect(center=(self.width // 2, self.height - 25))
		self.screen.blit(text_surface, text_rect)
	
	def handle_click(self, pos, right_click=False):
		"""
		Handles a mouse click event on the game grid.

		Args:
			pos (tuple): The (x, y) position of the mouse click.
			right_click (bool): Whether the click was a right click.
		"""
		if self.game_over:
			return
		start_row, start_col = self.offset
		c, r = pos[0] // CELL_SIZE + start_col, pos[1] // CELL_SIZE + start_row
		if r >= self.rows or c >= self.cols:
			return
		
		if right_click:
			self.logic.flags[r][c] = not self.logic.flags[r][c]
		else:
			if not self.logic.reveal_cell(r, c):
				return
			if self.logic.is_mine(r, c):
				self.game_over = True
				self.win = False
			else:
				value = self.logic.get_adjacent(r, c)
				if value == 0:
					for nr, nc in self.logic.get_adjacent_cells(r, c):
						self.handle_click((nc * CELL_SIZE, nr * CELL_SIZE))
		
		if self.logic.is_win():
			self.game_over = True
			self.win = True
	
	def display_game_over(self):
		"""
		Displays the game over screen with a win or loss message.
		"""
		msg = "You Win!" if self.win else "Game Over!"
		text_surface = self.font.render(msg, True, (255, 0, 0))
		text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2 - 40))
		self.screen.blit(text_surface, text_rect)
		
		play_again_text = "Press Enter to Play Again"
		play_again_surface = self.font.render(play_again_text, True, (255, 255, 255))
		play_again_rect = play_again_surface.get_rect(center=(self.width // 2, self.height // 2))
		self.screen.blit(play_again_surface, play_again_rect)
	
	def move_view(self, dx, dy):
		"""
		Moves the visible portion of the grid by adjusting the offset.

		Args:
			dx (int): The horizontal movement (-1 for left, 1 for right).
			dy (int): The vertical movement (-1 for up, 1 for down).
		"""
		new_row = self.offset[0] + dy
		new_col = self.offset[1] + dx
		if 0 <= new_row <= max(0, self.rows - self.visible_rows):
			self.offset = (new_row, self.offset[1])
		if 0 <= new_col <= max(0, self.cols - self.visible_cols):
			self.offset = (self.offset[0], new_col)
	
	def run(self):
		"""
		The main game loop for Minesweeper. Handles events, updates the display, and manages game logic.

		Returns:
			bool: True if the game should restart, False if it should exit.
		"""
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
					if event.button == 1:
						self.handle_click(event.pos)
					elif event.button == 3:
						self.handle_click(event.pos, right_click=True)
				elif event.type == pygame.KEYDOWN:
					if self.game_over and event.key == pygame.K_RETURN:
						return True  # Restart the game
					if event.key == pygame.K_LEFT:
						self.move_view(-1, 0)
					elif event.key == pygame.K_RIGHT:
						self.move_view(1, 0)
					elif event.key == pygame.K_UP:
						self.move_view(0, -1)
					elif event.key == pygame.K_DOWN:
						self.move_view(0, 1)
			
			pygame.display.flip()
			clock.tick(30)
		pygame.quit()
		return False

class StartScreen:
	def __init__(self, screen, font):
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
		"""Draws a modern-style rectangle with subtle shadows."""
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
	mines = int(rows * cols * 0.16)
	while True:
		game = Minesweeper(rows=rows, cols=cols, mines=mines)
		if not game.run():
			break
