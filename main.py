import sys
import time
from pysat.solvers import Glucose3

class SudokuBoard:
    # Handles board state, validation, and visualization
    def __init__(self, input_file=None):
        self.D = 3
        self.N = 9
        self.grid = [[0]*9 for _ in range(9)]
        self.original_grid = [[0]*9 for _ in range(9)]
        
        if input_file:
            self.load_file(input_file)

    def load_file(self, file_name):
        try:
            with open(file_name, "r") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
                if len(lines) != self.N:
                    raise ValueError("Invalid row count")
                for r, line in enumerate(lines):
                    for c, char in enumerate(line):
                        val = int(char) if char.isdigit() else 0
                        self.grid[r][c] = val
                        self.original_grid[r][c] = val
        except Exception as e:
            print(f"Error loading file: {e}")
            sys.exit(1)

    def update_cell(self, r, c, val):
        self.grid[r][c] = val

    def get_val(self, r, c):
        return self.grid[r][c]

    def display(self, title="Sudoku Board"):
        print(f"\n--- {title} ---")
        for i in range(self.N):
            if i % self.D == 0 and i != 0:
                print("- - - - - - - - - - - -")
            row_str = ""
            for j in range(self.N):
                if j % self.D == 0 and j != 0:
                    row_str += " | "
                val = self.grid[i][j]
                row_str += (str(val) if val > 0 else ".") + " "
            print(row_str)
        print("-" * 23)

    def validate(self):
        # Quick validation check for report
        try:
            # Check rows and cols
            for i in range(9):
                if len(set(self.grid[i])) != 9: return False
                if len(set(row[i] for row in self.grid)) != 9: return False
            # Check subgrids
            for sr in range(3):
                for sc in range(3):
                    vals = []
                    for r in range(3):
                        for c in range(3):
                            vals.append(self.grid[sr*3+r][sc*3+c])
                    if len(set(vals)) != 9: return False
            return True
        except:
            return False

class SudokuAgent:
    # Solves Sudoku using CNF encoding and SAT solver
    def __init__(self):
        self.clauses = []
        self.N = 9
        self.D = 3
        # Performance metrics for reporting
        self.metrics = {
            'n_vars': 0,
            'n_clauses': 0,
            'time_gen': 0.0,
            'time_solve': 0.0,
            'conflicts': 0,
            'decisions': 0,
            'propagations': 0
        }

    def _to_var(self, r, c, v):
        return (r * 81) + (c * 9) + (v - 1) + 1

    def _decode_var(self, literal):
        val = literal - 1
        v = (val % 9) + 1
        val = val // 9
        c = val % 9
        r = val // 9
        return r, c, v

    def generate_clauses(self, board):
        t_start = time.time()
        self.clauses = []
        
        # 1. Defined cells
        for r in range(self.N):
            for c in range(self.N):
                val = board.get_val(r, c)
                if val > 0:
                    self.clauses.append([self._to_var(r, c, val)])

        # 2. Cell constraints (at least one, at most one)
        for r in range(self.N):
            for c in range(self.N):
                # At least one
                self.clauses.append([self._to_var(r, c, v) for v in range(1, 10)])
                # At most one
                for v in range(1, 10):
                    for w in range(v + 1, 10):
                        self.clauses.append([-self._to_var(r, c, v), -self._to_var(r, c, w)])

        # 3. Row constraints
        for r in range(self.N):
            for v in range(1, 10):
                self.clauses.append([self._to_var(r, c, v) for c in range(9)])

        # 4. Column constraints
        for c in range(self.N):
            for v in range(1, 10):
                self.clauses.append([self._to_var(r, c, v) for r in range(9)])

        # 5. Sub-grid constraints
        for sr in range(self.D):
            for sc in range(self.D):
                for v in range(1, 10):
                    clause = []
                    for i in range(self.D):
                        for j in range(self.D):
                            r = sr * self.D + i
                            c = sc * self.D + j
                            clause.append(self._to_var(r, c, v))
                    self.clauses.append(clause)

        self.metrics['time_gen'] = time.time() - t_start
        self.metrics['n_clauses'] = len(self.clauses)
        self.metrics['n_vars'] = 729

    def solve(self, board):
        self.generate_clauses(board)
        
        g = Glucose3()
        for c in self.clauses:
            g.add_clause(c)
        
        t_start = time.time()
        is_solved = g.solve()
        self.metrics['time_solve'] = time.time() - t_start
        
        # Capture internal solver stats for report
        stats = g.accum_stats()
        self.metrics['conflicts'] = stats['conflicts']
        self.metrics['decisions'] = stats['decisions']
        self.metrics['propagations'] = stats['propagations']

        if is_solved:
            model = g.get_model()
            for literal in model:
                if literal > 0:
                    r, c, v = self._decode_var(literal)
                    board.update_cell(r, c, v)
            g.delete()
            return True
        else:
            g.delete()
            return False

    def print_report(self):
        m = self.metrics
        print("\n" + "="*40)
        print(f" Problem Size")
        print(f"  - Variables (CNF):      {m['n_vars']}")
        print(f"  - Clauses (CNF):        {m['n_clauses']}")
        print("-" * 40)
        print(f" Performance")
        print(f"  - Constraint Gen Time:  {m['time_gen']:.6f}s")
        print(f"  - Solving Time:         {m['time_solve']:.6f}s")
        print(f"  - Total Time:           {m['time_gen'] + m['time_solve']:.6f}s")
        print("-" * 40)
        print(f" Solver Statistics (Glucose3)")
        print(f"  - Conflicts:            {m['conflicts']}")
        print(f"  - Decisions:            {m['decisions']}")
        print(f"  - Propagations:         {m['propagations']}")
        print("="*40 + "\n")

if __name__ == '__main__':
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    
    # Init environment
    board = SudokuBoard(input_file)
    board.display("Input Puzzle")

    # Init agent
    agent = SudokuAgent()
    print("Agent is solving...")
    
    # Solve
    if agent.solve(board):
        board.display("Solved Puzzle")
        
        # Verify correctness
        if board.validate():
            print(">> STATUS: VALID SOLUTION Verified.")
        else:
            print(">> STATUS: INVALID SOLUTION.")
            
        # Show detailed metrics
        agent.print_report()
    else:
        print("No solution found.")