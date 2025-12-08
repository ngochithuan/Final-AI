# main.py
import sys
import os
from gui import SudokuGame

def main():
    # Kiểm tra tham số dòng lệnh cho file input
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input0.txt"
    
    # Tạo file mẫu nếu chưa có để tránh lỗi
    if not os.path.exists(input_file):
        print(f"Warning: Input file '{input_file}' not found. Creating empty file.")
        with open(input_file, "w") as f: f.write("")
    
    # Khởi tạo và chạy game
    game = SudokuGame(input_file)
    game.run()

if __name__ == "__main__":
    main()