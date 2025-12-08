import numpy as np

class Sudoku:
    def __init__(self, board):
        # Đảm bảo board luôn là numpy array
        if isinstance(board, np.ndarray):
            self.board = board
        else:
            self.board = np.array(board, dtype=int)
            
        # Lưu bản gốc để biết ô nào là đề bài (không đổi màu)
        self.original_grid = np.copy(self.board)
        # Alias self.grid cho self.board để tương thích với code cũ
        self.grid = self.board

    def validate(self):
        """Kiểm tra tính hợp lệ của bảng Sudoku"""
        # Check rows
        for i in range(9):
            nums = self.board[i, :]
            nums = nums[nums > 0]
            if len(nums) != len(set(nums)): return False

        # Check cols
        for j in range(9):
            nums = self.board[:, j]
            nums = nums[nums > 0]
            if len(nums) != len(set(nums)): return False

        # Check 3x3 squares
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                block = self.board[i:i+3, j:j+3].flatten()
                nums = block[block > 0]
                if len(nums) != len(set(nums)): return False
        
        # Check full
        if 0 in self.board: return False
        
        return True

    def print_board(self, line=True):
        if line:
            for i in range(len(self.board)):
                for j in range(len(self.board[i])):
                    if j % 3 == 0 and j != 0:
                        print("| ", end="")
                    num = self.board[i][j]
                    print(str(int(num)) if num != 0 else '.', end=" ")
                print("")
                if (i + 1) % 3 == 0 and i != 8:
                    print("---------------------")
        else:
            for row in self.board:
                print(" ".join(str(num) if num != 0 else '.' for num in row))