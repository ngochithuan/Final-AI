import time
from pysat.solvers import Glucose3
from csp import CSP 

class SudokuAgent(CSP):
    def __init__(self):
        # Sudoku có 81 biến (ô), domain là 1-9
        super().__init__(variables=list(range(81)), domains=list(range(1, 10)), constraints=[])
        self.metrics = {
            'time_gen': 0,
            'time_solve': 0,
            'n_vars': 0,
            'n_clauses': 0,
            'conflicts': 0,
            'decisions': 0,
            'propagations': 0
        }

    def _to_var(self, r, c, v):
        """Map (row, col, value) -> SAT variable integer (1-729)"""
        # Ép kiểu kết quả về int thuần để chắc chắn
        return int(81 * r + 9 * c + v)

    def _parse_model(self, model, board_obj):
        """Map SAT result back to Sudoku board"""
        for var in model:
            if var > 0: # Chỉ lấy biến True
                val = (var - 1) % 9 + 1
                col = ((var - 1) // 9) % 9
                row = (var - 1) // 81
                board_obj.grid[row][col] = val

    def solve(self, board_obj):
        """Giải Sudoku bằng PySAT"""
        start_gen = time.time()
        cnf = Glucose3()

        # 1. Ràng buộc: Mỗi ô chỉ chứa 1 số
        for r in range(9):
            for c in range(9):
                # Ít nhất 1 số
                cnf.add_clause([self._to_var(r, c, v) for v in range(1, 10)])
                # Không quá 1 số (At most one)
                for v1 in range(1, 10):
                    for v2 in range(v1 + 1, 10):
                        cnf.add_clause([-self._to_var(r, c, v1), -self._to_var(r, c, v2)])

        # 2. Ràng buộc: Hàng, Cột, Khối 3x3 (Mỗi số xuất hiện 1 lần)
        for v in range(1, 10):
            for k in range(9):
                # Row constraint
                cnf.add_clause([self._to_var(k, c, v) for c in range(9)])
                # Col constraint
                cnf.add_clause([self._to_var(r, k, v) for r in range(9)])
                # Block constraint
                br, bc = (k // 3) * 3, (k % 3) * 3
                cnf.add_clause([self._to_var(br + i, bc + j, v) for i in range(3) for j in range(3)])
        
        # 3. Ràng buộc: Các số đã điền sẵn (Original grid)
        for r in range(9):
            for c in range(9):
                # --- SỬA LỖI TẠI ĐÂY: Ép kiểu numpy.int về int của Python ---
                val = int(board_obj.grid[r][c]) 
                # ------------------------------------------------------------
                if val > 0:
                    cnf.add_clause([self._to_var(r, c, val)])

        self.metrics['time_gen'] = time.time() - start_gen
        self.metrics['n_vars'] = cnf.nof_vars()
        self.metrics['n_clauses'] = cnf.nof_clauses()

        # Solve
        start_solve = time.time()
        solved = cnf.solve()
        self.metrics['time_solve'] = time.time() - start_solve
        
        # Get statistics from solver
        stats = cnf.accum_stats()
        self.metrics['conflicts'] = stats['conflicts']
        self.metrics['decisions'] = stats['decisions']
        self.metrics['propagations'] = stats['propagations']

        if solved:
            model = cnf.get_model()
            self._parse_model(model, board_obj)
            cnf.delete()
            return True
        else:
            cnf.delete()
            return False