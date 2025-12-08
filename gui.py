"""
Sudoku Solver - PyGame Desktop Application
A modern game-like interface for the CSP-based Sudoku Solver using PySAT.
"""

import pygame
import sys
import os
import tkinter as tk
from tkinter import filedialog
# --- CẬP NHẬT IMPORT ---
from sudoku import Sudoku
from solver import SudokuAgent
from file_reader import FileReader  # <--- MỚI
# -----------------------

# ... (GIỮ NGUYÊN PHẦN CONSTANTS & COLORS & BUTTON CLASS & HELPER FUNCTIONS) ...
# Để tiết kiệm không gian, tôi chỉ viết lại class SudokuGame với thay đổi cần thiết

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
FPS = 60

# Layout dimensions
SIDEBAR_WIDTH = 380
GRID_PADDING = 50
CELL_SIZE = 60
GRID_SIZE = CELL_SIZE * 9

# Colors (Modern Dark Theme)
COLORS = {
    'bg_dark': (15, 15, 26),
    'bg_sidebar': (26, 26, 46),
    'bg_cell': (22, 33, 62),
    'bg_cell_hover': (35, 50, 85),
    'bg_cell_selected': (45, 60, 100),
    'grid_thin': (58, 58, 92),
    'grid_thick': (0, 217, 255),
    'text_original': (255, 255, 255),
    'text_solved': (0, 230, 118),
    'text_title': (0, 217, 255),
    'text_label': (136, 136, 170),
    'text_value': (255, 214, 10),
    'btn_primary': (0, 217, 255),
    'btn_primary_hover': (0, 180, 220),
    'btn_secondary': (255, 0, 110),
    'btn_secondary_hover': (200, 0, 90),
    'btn_import': (100, 80, 255),
    'btn_import_hover': (80, 60, 200),
    'btn_text': (15, 15, 26),
    'accent': (0, 217, 255),
    'selection_border': (255, 0, 110),
    'success': (0, 230, 118),
    'warning': (255, 214, 10),
    'error_bg': (220, 20, 60),
    'error_border': (255, 50, 50),
}

def lerp_color(start_color, end_color, t):
    return (
        int(start_color[0] + (end_color[0] - start_color[0]) * t),
        int(start_color[1] + (end_color[1] - start_color[1]) * t),
        int(start_color[2] + (end_color[2] - start_color[2]) * t)
    )

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.font = None
    
    def set_font(self, font):
        self.font = font
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        border_color = COLORS['accent'] if self.is_hovered else color
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        if self.font:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos): return True
        return False

class SudokuGame:
    def __init__(self, input_file="input.txt"):
        pygame.init()
        pygame.display.set_caption("🧩 Sudoku Solver | CSP + SAT (Glucose3)")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self._load_fonts()
        
        self.input_file = input_file
        self.board = None
        self.original_grid = None
        self.agent = None
        self.is_solved = False
        self.solution_valid = False
        self.selected = None
        self.flash_timer = 0.0      
        self.flash_duration = 0.75  
        
        # Gọi hàm load
        self.reset_board()
        
        self.grid_x = SIDEBAR_WIDTH + (WINDOW_WIDTH - SIDEBAR_WIDTH - GRID_SIZE) // 2
        self.grid_y = (WINDOW_HEIGHT - GRID_SIZE) // 2
        self._create_buttons()
        self.status_message = "Ready to solve"
        self.status_color = COLORS['text_label']
    
    # ... (Giữ nguyên _load_fonts, _create_buttons, open_file_dialog) ...
    def _load_fonts(self):
        try:
            self.font_title = pygame.font.SysFont('Segoe UI', 42, bold=True)
            self.font_subtitle = pygame.font.SysFont('Consolas', 16)
            self.font_cell = pygame.font.SysFont('Segoe UI', 32, bold=True)
            self.font_button = pygame.font.SysFont('Segoe UI', 20, bold=True)
            self.font_label = pygame.font.SysFont('Segoe UI', 16)
            self.font_value = pygame.font.SysFont('Consolas', 24, bold=True)
            self.font_small = pygame.font.SysFont('Consolas', 14)
        except:
            self.font_title = pygame.font.Font(None, 48)
            self.font_subtitle = pygame.font.Font(None, 20)
            self.font_cell = pygame.font.Font(None, 36)
            self.font_button = pygame.font.Font(None, 24)
            self.font_label = pygame.font.Font(None, 20)
            self.font_value = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 18)

    def _create_buttons(self):
        btn_width = 300
        btn_height = 45
        btn_x = (SIDEBAR_WIDTH - btn_width) // 2
        spacing = 15
        start_y = 260
        self.btn_import = Button(btn_x, start_y, btn_width, btn_height, "IMPORT FILE", COLORS['btn_import'], COLORS['btn_import_hover'], COLORS['text_original'])
        self.btn_import.set_font(self.font_button)
        self.btn_solve = Button(btn_x, start_y + btn_height + spacing, btn_width, btn_height, "SOLVE PUZZLE", COLORS['btn_primary'], COLORS['btn_primary_hover'], COLORS['btn_text'])
        self.btn_solve.set_font(self.font_button)
        self.btn_reset = Button(btn_x, start_y + (btn_height + spacing) * 2, btn_width, btn_height, "RESET BOARD", COLORS['btn_secondary'], COLORS['btn_secondary_hover'], COLORS['text_original'])
        self.btn_reset.set_font(self.font_button)
        self.buttons = [self.btn_import, self.btn_solve, self.btn_reset]

    def open_file_dialog(self):
        try:
            root = tk.Tk()
            root.withdraw() 
            file_path = filedialog.askopenfilename(title="Select Sudoku Input File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
            root.destroy()
            if file_path:
                self.input_file = file_path
                self.reset_board()
                self.status_message = "New puzzle loaded!"
                self.status_color = COLORS['success']
        except Exception as e:
            self.status_message = f"Error: {str(e)}"
            self.status_color = COLORS['btn_secondary']

    # --- HÀM QUAN TRỌNG CẦN SỬA ---
    def reset_board(self):
        try:
            # SỬ DỤNG FILE READER
            file_reader = FileReader(self.input_file)
            self.board = file_reader.read_file()
            
            # Cập nhật các trạng thái khác
            self.original_grid = [row[:] for row in self.board.grid.tolist()]
            self.agent = SudokuAgent()
            self.is_solved = False
            self.solution_valid = False
            self.selected = None
            self.flash_timer = 0
            self.status_message = "Puzzle loaded - Ready to solve"
            self.status_color = COLORS['text_label']
        except Exception as e:
            self.status_message = f"Error: {str(e)}"
            self.status_color = COLORS['btn_secondary']
    # ------------------------------
    
    # ... (Giữ nguyên các hàm còn lại: solve_puzzle, handle_events, _draw..., run) ...
    def solve_puzzle(self):
        if self.is_solved:
            self.status_message = "Already solved!"
            self.status_color = COLORS['warning']
            return
        
        self.status_message = "Solving..."
        self.status_color = COLORS['warning']
        self._draw()
        pygame.display.flip()
        
        success = self.agent.solve(self.board)
        
        if success:
            self.is_solved = True
            self.solution_valid = self.board.validate()
            self.selected = None
            if self.solution_valid:
                self.status_message = "Solution found and verified!"
                self.status_color = COLORS['success']
            else:
                self.status_message = "Solution found but invalid!"
                self.status_color = COLORS['btn_secondary']
        else:
            self.status_message = "No solution exists!"
            self.status_color = COLORS['btn_secondary']
            self.flash_timer = self.flash_duration 

    def select_cell(self, pos):
        if pos[0] < self.grid_x or pos[0] > self.grid_x + GRID_SIZE: return
        if pos[1] < self.grid_y or pos[1] > self.grid_y + GRID_SIZE: return
        col = (pos[0] - self.grid_x) // CELL_SIZE
        row = (pos[1] - self.grid_y) // CELL_SIZE
        self.selected = (row, col)

    def set_cell_value(self, value):
        if self.selected and self.board:
            row, col = self.selected
            self.board.grid[row][col] = value
            self.original_grid[row][col] = value
            self.is_solved = False
            self.status_message = "Board modified manually"
            self.status_color = COLORS['text_label']

    def move_selection(self, dr, dc):
        if self.selected:
            r, c = self.selected
            self.selected = ((r + dr) % 9, (c + dc) % 9)
        else:
            self.selected = (0, 0)

    def _draw_sidebar(self):
        sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, COLORS['bg_sidebar'], sidebar_rect)
        pygame.draw.line(self.screen, COLORS['grid_thick'], (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, WINDOW_HEIGHT), 2)
        
        title_text = self.font_title.render("SUDOKU", True, COLORS['text_title'])
        title_rect = title_text.get_rect(centerx=SIDEBAR_WIDTH // 2, y=30)
        self.screen.blit(title_text, title_rect)
        subtitle_text = self.font_subtitle.render("CSP + SAT Solver (Glucose3)", True, COLORS['text_label'])
        subtitle_rect = subtitle_text.get_rect(centerx=SIDEBAR_WIDTH // 2, y=80)
        self.screen.blit(subtitle_text, subtitle_rect)
        pygame.draw.line(self.screen, COLORS['accent'], (40, 120), (SIDEBAR_WIDTH - 40, 120), 1)
        
        status_y = 140
        self.screen.blit(self.font_label.render("STATUS:", True, COLORS['text_label']), (40, status_y))
        self.screen.blit(self.font_small.render(self.status_message, True, self.status_color), (40, status_y + 25))
        
        file_y = 190
        self.screen.blit(self.font_label.render("INPUT FILE:", True, COLORS['text_label']), (40, file_y))
        display_name = os.path.basename(self.input_file)
        if len(display_name) > 30: display_name = "..." + display_name[-27:]
        self.screen.blit(self.font_small.render(display_name, True, COLORS['text_value']), (40, file_y + 25))
        
        for button in self.buttons: button.draw(self.screen)
        self._draw_metrics()
    
    def _draw_metrics(self):
        metrics_y = 460
        pygame.draw.line(self.screen, COLORS['accent'], (40, metrics_y - 15), (SIDEBAR_WIDTH - 40, metrics_y - 15), 1)
        self.screen.blit(self.font_label.render("PERFORMANCE METRICS", True, COLORS['text_title']), (40, metrics_y))
        if self.agent:
            m = self.agent.metrics
            metrics_data = [
                ("Variables", f"{m['n_vars']:,}"), ("Clauses", f"{m['n_clauses']:,}"),
                ("Gen Time", f"{m['time_gen']*1000:.3f} ms"), ("Solve Time", f"{m['time_solve']*1000:.3f} ms"),
                ("Total Time", f"{(m['time_gen'] + m['time_solve'])*1000:.3f} ms"),
                ("Conflicts", f"{m['conflicts']:,}"), ("Decisions", f"{m['decisions']:,}")
            ]
            y_offset = metrics_y + 35
            for label, value in metrics_data:
                self.screen.blit(self.font_small.render(label + ":", True, COLORS['text_label']), (50, y_offset))
                value_surf = self.font_small.render(value, True, COLORS['text_value'])
                self.screen.blit(value_surf, value_surf.get_rect(right=SIDEBAR_WIDTH - 50, y=y_offset))
                y_offset += 24
    
    def _draw_grid(self):
        if self.flash_timer > 0:
            ratio = self.flash_timer / self.flash_duration
            current_bg_color = lerp_color(COLORS['bg_sidebar'], COLORS['error_bg'], ratio)
            current_border_color = lerp_color(COLORS['grid_thick'], COLORS['error_border'], ratio)
        else:
            current_bg_color = COLORS['bg_sidebar']
            current_border_color = COLORS['grid_thick']

        grid_bg_rect = pygame.Rect(self.grid_x - 10, self.grid_y - 10, GRID_SIZE + 20, GRID_SIZE + 20)
        pygame.draw.rect(self.screen, current_bg_color, grid_bg_rect, border_radius=12)
        pygame.draw.rect(self.screen, current_border_color, grid_bg_rect, 2, border_radius=12)
        
        for row in range(9):
            for col in range(9):
                x, y = self.grid_x + col * CELL_SIZE, self.grid_y + row * CELL_SIZE
                cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                
                if self.selected == (row, col): pygame.draw.rect(self.screen, COLORS['bg_cell_selected'], cell_rect)
                else: pygame.draw.rect(self.screen, COLORS['bg_cell'], cell_rect)
                
                val = self.board.grid[row][col] if self.board else 0
                if val > 0:
                    text_color = COLORS['text_original'] if self.original_grid and self.original_grid[row][col] > 0 else COLORS['text_solved']
                    num_text = self.font_cell.render(str(val), True, text_color)
                    self.screen.blit(num_text, num_text.get_rect(center=cell_rect.center))
                
                if self.selected == (row, col): pygame.draw.rect(self.screen, COLORS['selection_border'], cell_rect, 3)

        for i in range(10):
            thickness = 3 if i % 3 == 0 else 1
            color = COLORS['grid_thick'] if i % 3 == 0 else COLORS['grid_thin']
            if self.flash_timer > 0:
                 ratio = self.flash_timer / self.flash_duration
                 color = lerp_color(color, COLORS['error_border'], ratio * 0.5) 
            pygame.draw.line(self.screen, color, (self.grid_x, self.grid_y + i * CELL_SIZE), (self.grid_x + GRID_SIZE, self.grid_y + i * CELL_SIZE), thickness)
            pygame.draw.line(self.screen, color, (self.grid_x + i * CELL_SIZE, self.grid_y), (self.grid_x + i * CELL_SIZE, self.grid_y + GRID_SIZE), thickness)
    
    def _draw_legend(self):
        legend_y, legend_x = self.grid_y + GRID_SIZE + 30, self.grid_x + 50
        pygame.draw.circle(self.screen, COLORS['text_original'], (legend_x, legend_y), 8)
        self.screen.blit(self.font_small.render("Original Clues", True, COLORS['text_original']), (legend_x + 20, legend_y - 8))
        pygame.draw.circle(self.screen, COLORS['text_solved'], (legend_x + 200, legend_y), 8)
        self.screen.blit(self.font_small.render("AI Solved", True, COLORS['text_solved']), (legend_x + 220, legend_y - 8))
    
    def _draw_title(self):
        title = "SOLVED PUZZLE" if self.is_solved else "SUDOKU PUZZLE"
        color = COLORS['success'] if self.is_solved else COLORS['text_title']
        title_text = self.font_button.render(title, True, color)
        self.screen.blit(title_text, title_text.get_rect(centerx=self.grid_x + GRID_SIZE // 2, y=self.grid_y - 45))
    
    def _draw(self):
        self.screen.fill(COLORS['bg_dark'])
        self._draw_sidebar()
        self._draw_title()
        self._draw_grid()
        self._draw_legend()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_import.handle_event(event): self.open_file_dialog()
                elif self.btn_solve.handle_event(event): self.solve_puzzle()
                elif self.btn_reset.handle_event(event): self.reset_board()
                else: self.select_cell(event.pos)

            if event.type == pygame.KEYDOWN:
                if self.selected:
                    if event.key in [pygame.K_1, pygame.K_KP1]: self.set_cell_value(1)
                    if event.key in [pygame.K_2, pygame.K_KP2]: self.set_cell_value(2)
                    if event.key in [pygame.K_3, pygame.K_KP3]: self.set_cell_value(3)
                    if event.key in [pygame.K_4, pygame.K_KP4]: self.set_cell_value(4)
                    if event.key in [pygame.K_5, pygame.K_KP5]: self.set_cell_value(5)
                    if event.key in [pygame.K_6, pygame.K_KP6]: self.set_cell_value(6)
                    if event.key in [pygame.K_7, pygame.K_KP7]: self.set_cell_value(7)
                    if event.key in [pygame.K_8, pygame.K_KP8]: self.set_cell_value(8)
                    if event.key in [pygame.K_9, pygame.K_KP9]: self.set_cell_value(9)
                    if event.key in [pygame.K_0, pygame.K_KP0, pygame.K_BACKSPACE, pygame.K_DELETE]: self.set_cell_value(0)
                    if event.key == pygame.K_UP: self.move_selection(-1, 0)
                    if event.key == pygame.K_DOWN: self.move_selection(1, 0)
                    if event.key == pygame.K_LEFT: self.move_selection(0, -1)
                    if event.key == pygame.K_RIGHT: self.move_selection(0, 1)

                if event.key in [pygame.K_SPACE, pygame.K_RETURN]: self.solve_puzzle()
                elif event.key == pygame.K_r: self.reset_board()
                elif event.key == pygame.K_o: self.open_file_dialog()
                elif event.key == pygame.K_ESCAPE:
                    if self.selected: self.selected = None
                    else: self.running = False
            for button in self.buttons: button.handle_event(event)
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            if self.flash_timer > 0:
                self.flash_timer -= dt
                if self.flash_timer < 0: self.flash_timer = 0
            self.handle_events()
            self._draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit()