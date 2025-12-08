import numpy as np
import os
from sudoku import Sudoku

class FileReader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_file(self) -> Sudoku:
        """Reads the content of the file and returns a Sudoku object."""
        # Tạo bảng rỗng mặc định
        board = np.zeros((9, 9), dtype=int)
        
        # Kiểm tra file tồn tại không
        if not os.path.exists(self.file_path):
            return Sudoku(board)

        try:
            with open(self.file_path, 'r') as f:
                # Đọc từng dòng
                for i, line in enumerate(f):
                    if i >= 9: break # Chỉ đọc 9 dòng đầu
                    
                    # Xử lý: tách số bởi khoảng trắng, hoặc nếu viết liền thì tách từng ký tự
                    line_content = line.strip()
                    if not line_content: continue

                    # Logic tách chuỗi: hỗ trợ cả "0 0 1" và "001..."
                    if ' ' in line_content:
                        parts = line_content.split()
                    else:
                        parts = list(line_content)
                    
                    for j, char in enumerate(parts):
                        if j >= 9: break # Chỉ lấy 9 cột đầu
                        
                        if char.isdigit():
                            board[i][j] = int(char)
                        elif char == '.':
                            board[i][j] = 0
                            
            return Sudoku(board)
            
        except Exception as e:
            print(f"Error reading file: {e}")
            return Sudoku(board) # Trả về bảng rỗng nếu lỗi