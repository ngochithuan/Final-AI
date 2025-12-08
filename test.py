import sys
import time
D = 3    # Subgrid dimension
N = D*D  # Grid dimension
from pysat.solvers import Glucose3
import numpy as np

from sudoku import Sudoku
from file_reader import FileReader

if __name__ == '__main__':
    beign = time.time()
    # Read the clues from the file given as the first argument
    file_name = sys.argv[1]

    FileReader = FileReader(file_name)
    sudoku = FileReader.read_file()

    clues = []
    digits = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9}
    with open(file_name, "r") as f:
        for line in f.readlines():
            assert len(line.strip()) == N, "'"+line+"'"
            for c in range(0, N):
                assert(line[c] in digits.keys() or line[c] == '.')
            clues.append(line.strip())
    assert(len(clues) == N)

    # A helper: get the Dimacs CNF variable number for the variable v_{r,c,v}
    # encoding the fact that the cell at (r,c) has the value v
    # def var(r, c, v):
    #     assert(1 <= r and r <= N and 1 <= c and c <= N and 1 <= v and v <= N)
    #     return (r-1)*N*N+(c-1)*N+(v-1)+1
    
    def var_map():
        map = np.zeros((N+1, N+1, N+1), dtype=int)
        for r in range(1, N+1):
            for c in range(1, N+1):
                for v in range(1, N+1):
                    map[r][c][v] = (r-1)*N*N+(c-1)*N+(v-1)+1
        return map
    
    def decode_var(literal, N):
        """
        Decodes a SAT integer back into (r, c, v).
        Assumes the literal is positive.
        """
        # 1. Remove the 1-based offset
        val = literal - 1
        
        # 2. Extract v (the lowest magnitude component)
        # v corresponds to the last term: (v-1)
        v = (val % N) + 1
        val = val // N  # Shift down
        
        # 3. Extract c (the middle component)
        # c corresponds to the middle term: (c-1)*N
        c = (val % N) + 1
        val = val // N  # Shift down
        
        # 4. Extract r (the highest magnitude component)
        # r corresponds to the first term: (r-1)*N*N
        r = val + 1
        
        return r, c, v

    # Build the clauses in a list
    cls = []  # The clauses: a list of integer lists
    added = set()  # To avoid adding duplicates
    var_map = var_map().tolist()

    for r in range(1,N+1): # r runs over 1,...,N
        for c in range(1, N+1):
            # The cell at (r,c) has at least one value
            cls.append([var_map[r][c][v] for v in range(1,N+1)])
            # The cell at (r,c) has at most one value
            for v in range(1, N+1):
                for w in range(v+1,N+1):
                    cls.append([-var_map[r][c][v], -var_map[r][c][w]])

    for v in range(1, N+1):
        # Each row has the value v
        for r in range(1, N+1):
            cls.append([var_map[r][c][v] for c in range(1,N+1)])

        # Each column has the value v
        for c in range(1, N+1):
            cls.append([var_map[r][c][v] for r in range(1,N+1)])

        # Each subgrid has the value v
        for sr in range(0,D):
            for sc in range(0,D):
                cls.append([var_map[sr*D+rd][sc*D+cd][v]
                            for rd in range(1,D+1) for cd in range(1,D+1)])

    # The clues must be respected
    for r in range(1, N+1):
        for c in range(1, N+1):
            if clues[r-1][c-1] in digits.keys():
                cls.append([var_map[r][c][digits[clues[r-1][c-1]]]])

    # Output the DIMACS CNF representation
    # Print the header line
    # print("p cnf %d %d" % (N*N*N, len(cls)))
    # # Print the clauses
    # for c in cls:
    #     print(" ".join([str(l) for l in c])+" 0")

g = Glucose3()
# print(cls)
for c in cls:
    print(c)
    g.add_clause(c)

if g.solve():
    model = g.get_model()
    g.delete()
    
    # Create an empty grid to visualize results
    # (Using 0 to represent empty, though solver should fill it)
    grid = [[0 for _ in range(N)] for _ in range(N)]
    
    print(f"--- Solution for N={N} ---")
    
    for literal in model:
        # We only care about POSITIVE literals
        # A positive literal means: "Cell (r,c) DOES contain value v"
        if literal > 0:
            r, c, v = decode_var(literal, N)
            grid[r-1][c-1] = v

    # Print the grid format
    for row in grid:
        print(row)
else:
    print("No solution found.")
    
end = time.time()
print("Time:", end - beign)
