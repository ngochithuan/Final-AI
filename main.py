import sys
import time
from pysat.solvers import Glucose3

class SudokuSolver:
    def __init__(self, input_file):
        self.D = 3          # Kích thước khối con
        self.N = self.D * self.D  # Kích thước lưới (9)
        self.grid = self._read_input(input_file)
        self.clauses = []
        self.model = None
        self.solution_grid = None
        
        # Thống kê để báo cáo
        self.stats = {
            'n_vars': 0,
            'n_clauses': 0,
            'time_generate': 0.0,
            'time_solve': 0.0,
            'solver_conflicts': 0,
            'solver_propagations': 0
        }

    def _read_input(self, file_name):
        """Đọc file input và validate dữ liệu"""
        clues = []
        digits = {str(i): i for i in range(10)}
        digits['.'] = 0
        try:
            with open(file_name, "r") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
                assert len(lines) == self.N, f"Input must have {self.N} rows"
                for line in lines:
                    assert len(line) == self.N, f"Row must have {self.N} chars"
                    row = [digits[c] if c in digits else 0 for c in line]
                    clues.append(row)
            return clues
        except Exception as e:
            print(f"Error reading input: {e}")
            sys.exit(1)

    def _to_var(self, r, c, v):
        # Map (row, col, value) sang số nguyên 1-based
        return (r * self.N * self.N) + (c * self.N) + (v - 1) + 1

    def _decode_var(self, literal):
        # Decode số nguyên về (row, col, value)
        val = literal - 1
        v = (val % self.N) + 1
        val = val // self.N
        c = val % self.N
        r = val // self.N
        return r, c, v

    def generate_constraints(self):
        """Sinh mệnh đề CNF và đo thời gian"""
        t_start = time.time()
        self.clauses = []
        
        # 1. Defined Cells (Clues)
        for r in range(self.N):
            for c in range(self.N):
                if self.grid[r][c] > 0:
                    self.clauses.append([self._to_var(r, c, self.grid[r][c])])

        # 2. Cell Uniqueness (Mỗi ô chỉ chứa 1 số)
        # At least one
        for r in range(self.N):
            for c in range(self.N):
                self.clauses.append([self._to_var(r, c, v) for v in range(1, self.N + 1)])
        # At most one
        for r in range(self.N):
            for c in range(self.N):
                for v in range(1, self.N + 1):
                    for w in range(v + 1, self.N + 1):
                        self.clauses.append([-self._to_var(r, c, v), -self._to_var(r, c, w)])

        # 3. Row Constraints
        for r in range(self.N):
            for v in range(1, self.N + 1):
                self.clauses.append([self._to_var(r, c, v) for c in range(self.N)])

        # 4. Column Constraints
        for c in range(self.N):
            for v in range(1, self.N + 1):
                self.clauses.append([self._to_var(r, c, v) for r in range(self.N)])

        # 5. Sub-grid Constraints
        for sr in range(self.D):
            for sc in range(self.D):
                for v in range(1, self.N + 1):
                    clause = []
                    for i in range(self.D):
                        for j in range(self.D):
                            clause.append(self._to_var(sr * self.D + i, sc * self.D + j, v))
                    self.clauses.append(clause)
        
        self.stats['time_generate'] = time.time() - t_start
        self.stats['n_clauses'] = len(self.clauses)
        self.stats['n_vars'] = self.N * self.N * self.N # 729 biến cho 9x9

    def solve(self):
        """Giải và thu thập thống kê từ Solver"""
        self.generate_constraints()
        
        g = Glucose3()
        for clause in self.clauses:
            g.add_clause(clause)
        
        t_start = time.time()
        result = g.solve()
        self.stats['time_solve'] = time.time() - t_start
        
        # Lấy thống kê từ Glucose3 (Conflicts, Propagations)
        solver_stats = g.accum_stats()
        self.stats['solver_conflicts'] = solver_stats['conflicts']
        self.stats['solver_propagations'] = solver_stats['propagations']
        
        if result:
            self.model = g.get_model()
            self._map_solution()
            g.delete()
            return True
        else:
            g.delete()
            return False
            
    def _map_solution(self):
        self.solution_grid = [[0]*self.N for _ in range(self.N)]
        for literal in self.model:
            if literal > 0:
                r, c, v = self._decode_var(literal)
                self.solution_grid[r][c] = v

    def visualize(self):
        """Hiển thị kết quả và bảng thống kê chi tiết cho báo cáo"""
        if not self.solution_grid:
            print("No solution found.")
            return

        print("\n" + "="*30)
        print("      SUDOKU SOLUTION")
        print("="*30)
        
        # Vẽ bảng Sudoku
        for i in range(self.N):
            if i % self.D == 0 and i != 0:
                print("- - - - - - - - - - - -")
            row_str = ""
            for j in range(self.N):
                if j % self.D == 0 and j != 0:
                    row_str += " | "
                row_str += str(self.solution_grid[i][j]) + " "
            print(row_str)
        
        print("\n" + "="*30)
        print("   PERFORMANCE METRICS")
        print("="*30)
        print(f"1. Problem Size:")
        print(f"   - Input Size:       {self.N}x{self.N}")
        print(f"   - SAT Variables:    {self.stats['n_vars']} (Variables)")
        print(f"   - CNF Clauses:      {self.stats['n_clauses']} (Constraints)")
        print(f"\n2. Time Efficiency:")
        print(f"   - Constraints Gen:  {self.stats['time_generate']:.6f} seconds")
        print(f"   - Solving Time:     {self.stats['time_solve']:.6f} seconds")
        print(f"   - Total Time:       {self.stats['time_generate'] + self.stats['time_solve']:.6f} seconds")
        print(f"\n3. Solver Statistics (Glucose3):")
        print(f"   - Conflicts:        {self.stats['solver_conflicts']}")
        print(f"   - Propagations:     {self.stats['solver_propagations']}")
        print("="*30 + "\n")

if __name__ == '__main__':
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    solver = SudokuSolver(input_file)
    if solver.solve():
        solver.visualize()
    else:
        print("No solution found.")