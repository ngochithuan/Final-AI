"""
Sudoku Solver - PyGame Desktop Application
A modern game-like interface for the CSP-based Sudoku Solver using PySAT.
"""

import pygame
import sys
import os
from main import SudokuBoard, SudokuAgent

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
GRID_SIZE = CELL_SIZE * 9  # 540px

# Colors (Modern Dark Theme)
COLORS = {
    'bg_dark': (15, 15, 26),           # Main background
    'bg_sidebar': (26, 26, 46),        # Sidebar background
    'bg_cell': (22, 33, 62),           # Cell background
    'bg_cell_hover': (35, 50, 85),     # Cell hover
    'grid_thin': (58, 58, 92),         # Thin grid lines
    'grid_thick': (0, 217, 255),       # Thick subgrid lines (cyan)
    'text_original': (255, 255, 255),  # Original numbers (white)
    'text_solved': (0, 230, 118),      # Solved numbers (green)
    'text_title': (0, 217, 255),       # Title text (cyan)
    'text_label': (136, 136, 170),     # Label text
    'text_value': (255, 214, 10),      # Metric values (gold)
    'btn_primary': (0, 217, 255),      # Primary button
    'btn_primary_hover': (0, 180, 220),
    'btn_secondary': (255, 0, 110),    # Secondary button (magenta)
    'btn_secondary_hover': (200, 0, 90),
    'btn_text': (15, 15, 26),          # Button text
    'accent': (0, 217, 255),           # Accent color
    'success': (0, 230, 118),          # Success color
    'warning': (255, 214, 10),         # Warning color
}


# ============================================================================
# BUTTON CLASS
# ============================================================================
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.font = None  # Will be set later
    
    def set_font(self, font):
        self.font = font
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        
        # Draw button with rounded corners
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        
        # Draw border
        border_color = COLORS['accent'] if self.is_hovered else color
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        # Draw text
        if self.font:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


# ============================================================================
# SUDOKU GAME APPLICATION
# ============================================================================
class SudokuGame:
    def __init__(self, input_file="input.txt"):
        pygame.init()
        pygame.display.set_caption("🧩 Sudoku Solver | CSP + SAT (Glucose3)")
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load fonts
        self._load_fonts()
        
        # Initialize game state
        self.input_file = input_file
        self.board = None
        self.original_grid = None
        self.agent = None
        self.is_solved = False
        self.solution_valid = False
        
        # Load the puzzle
        self.reset_board()
        
        # Calculate grid position (right side)
        self.grid_x = SIDEBAR_WIDTH + (WINDOW_WIDTH - SIDEBAR_WIDTH - GRID_SIZE) // 2
        self.grid_y = (WINDOW_HEIGHT - GRID_SIZE) // 2
        
        # Create buttons
        self._create_buttons()
        
        # Status message
        self.status_message = "Ready to solve"
        self.status_color = COLORS['text_label']
    
    def _load_fonts(self):
        """Load custom fonts or fallback to system fonts."""
        try:
            # Try to use system fonts that look good
            self.font_title = pygame.font.SysFont('Segoe UI', 42, bold=True)
            self.font_subtitle = pygame.font.SysFont('Consolas', 16)
            self.font_cell = pygame.font.SysFont('Segoe UI', 32, bold=True)
            self.font_button = pygame.font.SysFont('Segoe UI', 20, bold=True)
            self.font_label = pygame.font.SysFont('Segoe UI', 16)
            self.font_value = pygame.font.SysFont('Consolas', 24, bold=True)
            self.font_small = pygame.font.SysFont('Consolas', 14)
        except:
            # Fallback to default font
            self.font_title = pygame.font.Font(None, 48)
            self.font_subtitle = pygame.font.Font(None, 20)
            self.font_cell = pygame.font.Font(None, 36)
            self.font_button = pygame.font.Font(None, 24)
            self.font_label = pygame.font.Font(None, 20)
            self.font_value = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 18)
    
    def _create_buttons(self):
        """Create UI buttons."""
        btn_width = 300
        btn_height = 50
        btn_x = (SIDEBAR_WIDTH - btn_width) // 2
        
        self.btn_solve = Button(
            btn_x, 280, btn_width, btn_height,
            "SOLVE PUZZLE",
            COLORS['btn_primary'], COLORS['btn_primary_hover'], COLORS['btn_text']
        )
        self.btn_solve.set_font(self.font_button)
        
        self.btn_reset = Button(
            btn_x, 350, btn_width, btn_height,
            "RESET BOARD",
            COLORS['btn_secondary'], COLORS['btn_secondary_hover'], COLORS['text_original']
        )
        self.btn_reset.set_font(self.font_button)
        
        self.buttons = [self.btn_solve, self.btn_reset]
    
    def reset_board(self):
        """Reset the board to initial state."""
        try:
            self.board = SudokuBoard(self.input_file)
            self.original_grid = [row[:] for row in self.board.original_grid]
            self.agent = SudokuAgent()
            self.is_solved = False
            self.solution_valid = False
            self.status_message = "Puzzle loaded - Ready to solve"
            self.status_color = COLORS['text_label']
        except Exception as e:
            self.status_message = f"Error loading puzzle: {str(e)}"
            self.status_color = COLORS['btn_secondary']
    
    def solve_puzzle(self):
        """Solve the puzzle using the SAT agent."""
        if self.is_solved:
            self.status_message = "Already solved!"
            self.status_color = COLORS['warning']
            return
        
        self.status_message = "Solving..."
        self.status_color = COLORS['warning']
        
        # Force screen update before solving
        self._draw()
        pygame.display.flip()
        
        # Solve the puzzle
        success = self.agent.solve(self.board)
        
        if success:
            self.is_solved = True
            self.solution_valid = self.board.validate()
            if self.solution_valid:
                self.status_message = "Solution found and verified!"
                self.status_color = COLORS['success']
            else:
                self.status_message = "Solution found but invalid!"
                self.status_color = COLORS['btn_secondary']
        else:
            self.status_message = "No solution exists for this puzzle"
            self.status_color = COLORS['btn_secondary']
    
    def _draw_sidebar(self):
        """Draw the sidebar with buttons and metrics."""
        # Sidebar background
        sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, COLORS['bg_sidebar'], sidebar_rect)
        
        # Sidebar border
        pygame.draw.line(self.screen, COLORS['grid_thick'], 
                        (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, WINDOW_HEIGHT), 2)
        
        # Title
        title_text = self.font_title.render("SUDOKU", True, COLORS['text_title'])
        title_rect = title_text.get_rect(centerx=SIDEBAR_WIDTH // 2, y=30)
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font_subtitle.render("CSP + SAT Solver (Glucose3)", True, COLORS['text_label'])
        subtitle_rect = subtitle_text.get_rect(centerx=SIDEBAR_WIDTH // 2, y=80)
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Decorative line
        pygame.draw.line(self.screen, COLORS['accent'],
                        (40, 120), (SIDEBAR_WIDTH - 40, 120), 1)
        
        # Status message
        status_y = 150
        status_label = self.font_label.render("STATUS:", True, COLORS['text_label'])
        self.screen.blit(status_label, (40, status_y))
        
        status_text = self.font_small.render(self.status_message, True, self.status_color)
        self.screen.blit(status_text, (40, status_y + 25))
        
        # File info
        file_y = 210
        file_label = self.font_label.render("INPUT FILE:", True, COLORS['text_label'])
        self.screen.blit(file_label, (40, file_y))
        
        file_text = self.font_small.render(self.input_file, True, COLORS['text_value'])
        self.screen.blit(file_text, (40, file_y + 25))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)
        
        # Metrics section
        self._draw_metrics()
    
    def _draw_metrics(self):
        """Draw the performance metrics in the sidebar."""
        metrics_y = 430
        
        # Section header
        pygame.draw.line(self.screen, COLORS['accent'],
                        (40, metrics_y - 15), (SIDEBAR_WIDTH - 40, metrics_y - 15), 1)
        
        header_text = self.font_label.render("PERFORMANCE METRICS", True, COLORS['text_title'])
        self.screen.blit(header_text, (40, metrics_y))
        
        if self.agent:
            m = self.agent.metrics
            metrics_data = [
                ("Variables (CNF)", f"{m['n_vars']:,}"),
                ("Clauses (CNF)", f"{m['n_clauses']:,}"),
                ("Generation Time", f"{m['time_gen']*1000:.3f} ms"),
                ("Solving Time", f"{m['time_solve']*1000:.3f} ms"),
                ("Total Time", f"{(m['time_gen'] + m['time_solve'])*1000:.3f} ms"),
                ("Conflicts", f"{m['conflicts']:,}"),
                ("Decisions", f"{m['decisions']:,}"),
                ("Propagations", f"{m['propagations']:,}"),
            ]
            
            y_offset = metrics_y + 35
            for label, value in metrics_data:
                # Label
                label_surface = self.font_small.render(label + ":", True, COLORS['text_label'])
                self.screen.blit(label_surface, (50, y_offset))
                
                # Value
                value_surface = self.font_small.render(value, True, COLORS['text_value'])
                value_rect = value_surface.get_rect(right=SIDEBAR_WIDTH - 50, y=y_offset)
                self.screen.blit(value_surface, value_rect)
                
                y_offset += 26
    
    def _draw_grid(self):
        """Draw the Sudoku grid."""
        # Grid background
        grid_bg_rect = pygame.Rect(
            self.grid_x - 10, self.grid_y - 10,
            GRID_SIZE + 20, GRID_SIZE + 20
        )
        pygame.draw.rect(self.screen, COLORS['bg_sidebar'], grid_bg_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS['grid_thick'], grid_bg_rect, 2, border_radius=12)
        
        # Draw cells
        for row in range(9):
            for col in range(9):
                x = self.grid_x + col * CELL_SIZE
                y = self.grid_y + row * CELL_SIZE
                
                # Cell background
                cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, COLORS['bg_cell'], cell_rect)
                
                # Draw cell value
                val = self.board.grid[row][col] if self.board else 0
                if val > 0:
                    # Determine color based on whether it's original or solved
                    if self.original_grid and self.original_grid[row][col] > 0:
                        text_color = COLORS['text_original']  # Original number
                    else:
                        text_color = COLORS['text_solved']    # AI-solved number
                    
                    num_text = self.font_cell.render(str(val), True, text_color)
                    num_rect = num_text.get_rect(center=cell_rect.center)
                    self.screen.blit(num_text, num_rect)
        
        # Draw grid lines
        for i in range(10):
            # Determine line thickness
            if i % 3 == 0:
                thickness = 3
                color = COLORS['grid_thick']
            else:
                thickness = 1
                color = COLORS['grid_thin']
            
            # Horizontal lines
            start_h = (self.grid_x, self.grid_y + i * CELL_SIZE)
            end_h = (self.grid_x + GRID_SIZE, self.grid_y + i * CELL_SIZE)
            pygame.draw.line(self.screen, color, start_h, end_h, thickness)
            
            # Vertical lines
            start_v = (self.grid_x + i * CELL_SIZE, self.grid_y)
            end_v = (self.grid_x + i * CELL_SIZE, self.grid_y + GRID_SIZE)
            pygame.draw.line(self.screen, color, start_v, end_v, thickness)
    
    def _draw_legend(self):
        """Draw the color legend below the grid."""
        legend_y = self.grid_y + GRID_SIZE + 30
        legend_x = self.grid_x + 50
        
        # Original numbers legend
        pygame.draw.circle(self.screen, COLORS['text_original'], (legend_x, legend_y), 8)
        original_text = self.font_small.render("Original Clues", True, COLORS['text_original'])
        self.screen.blit(original_text, (legend_x + 20, legend_y - 8))
        
        # Solved numbers legend
        solved_x = legend_x + 200
        pygame.draw.circle(self.screen, COLORS['text_solved'], (solved_x, legend_y), 8)
        solved_text = self.font_small.render("AI Solved", True, COLORS['text_solved'])
        self.screen.blit(solved_text, (solved_x + 20, legend_y - 8))
    
    def _draw_title(self):
        """Draw the title above the grid."""
        title_y = self.grid_y - 45
        
        if self.is_solved:
            title = "SOLVED PUZZLE"
            color = COLORS['success']
        else:
            title = "SUDOKU PUZZLE"
            color = COLORS['text_title']
        
        title_text = self.font_button.render(title, True, color)
        title_rect = title_text.get_rect(centerx=self.grid_x + GRID_SIZE // 2, y=title_y)
        self.screen.blit(title_text, title_rect)
    
    def _draw(self):
        """Main draw function."""
        # Clear screen
        self.screen.fill(COLORS['bg_dark'])
        
        # Draw components
        self._draw_sidebar()
        self._draw_title()
        self._draw_grid()
        self._draw_legend()
    
    def handle_events(self):
        """Handle PyGame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle button events
            if self.btn_solve.handle_event(event):
                self.solve_puzzle()
            
            if self.btn_reset.handle_event(event):
                self.reset_board()
            
            # Update button hover states
            for button in self.buttons:
                button.handle_event(event)
            
            # Handle keyboard shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.solve_puzzle()
                elif event.key == pygame.K_r:
                    self.reset_board()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self._draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


# ============================================================================
# ENTRY POINT
# ============================================================================
def main():
    # Check for command line argument for input file
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    
    # Verify input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        print("Usage: python gui.py [input_file.txt]")
        sys.exit(1)
    
    # Create and run the game
    game = SudokuGame(input_file)
    game.run()


if __name__ == "__main__":
    main()

