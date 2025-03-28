import random
import time
import json
from typing import List, Tuple, Optional
class SudokuGame:
    def __init__(self, size: int):
        self.size = size
        self.grid_size = int(size ** 0.5)
        self.grid = [[0] * size for _ in range(size)]
        self.solved_grid = None
        self.generate_puzzle()

    def generate_puzzle(self):
        self.generate_solved_puzzle()
        self.remove_numbers()

    def generate_solved_puzzle(self):
        self.backtrack()
        self.solved_grid = [row[:] for row in self.grid]

    def remove_numbers(self, difficulty=0.5):
        removed = 0
        target = self.size ** 2 * difficulty
        while removed < target:
            row = random.randint(0, self.size - 1)
            col = random.randint(0, self.size - 1)
            if self.grid[row][col] != 0:
                backup = self.grid[row][col]
                self.grid[row][col] = 0
                if not self.has_unique_solution():
                    self.grid[row][col] = backup
                else:
                    removed += 1

    def has_unique_solution(self) -> bool:
        temp_grid = [row[:] for row in self.grid]
        solutions = self.solve(temp_grid)
        return len(solutions) == 1

    def solve(self, grid: List[List[int]]) -> List[List[List[int]]]:
        solutions = []
        empty = self.find_empty_location(grid)
        if not empty:
            solutions.append(grid)
            return solutions
        row, col = empty
        for num in range(1, self.size + 1):
            if self.is_safe(grid, row, col, num):
                grid[row][col] = num
                if self.solve(grid):
                    solutions.append(grid)
                grid[row][col] = 0
        return solutions

    def backtrack(self) -> bool:
        empty = self.find_empty_location(self.grid)
        if not empty:
            return True
        row, col = empty
        numbers = list(range(1, self.size + 1))
        random.shuffle(numbers)
        for num in numbers:
            if self.is_safe(self.grid, row, col, num):
                self.grid[row][col] = num
                if self.backtrack():
                    return True
                self.grid[row][col] = 0
        return False

    def find_empty_location(self, grid: List[List[int]]) -> Optional[Tuple[int, int]]:
        for row in range(self.size):
            for col in range(self.size):
                if grid[row][col] == 0:
                    return row, col
        return None

    def is_safe(self, grid: List[List[int]], row: int, col: int, num: int) -> bool:
        return (self.is_row_safe(grid, row, num) and
                self.is_col_safe(grid, col, num) and
                self.is_box_safe(grid, row - row % self.grid_size, col - col % self.grid_size, num))

    def is_row_safe(self, grid: List[List[int]], row: int, num: int) -> bool:
        return num not in grid[row]

    def is_col_safe(self, grid: List[List[int]], col: int, num: int) -> bool:
        return num not in [grid[row][col] for row in range(self.size)]

    def is_box_safe(self, grid: List[List[int]], start_row: int, start_col: int, num: int) -> bool:
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if grid[row + start_row][col + start_col] == num:
                    return False
        return True

    def display(self):
        for row in self.grid:
            print(' '.join(str(num) if num != 0 else '.' for num in row))

    def track_progress(self, start_time: float) -> float:
        return time.time() - start_time

    def give_hint(self) -> Tuple[int, int, int]:
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] == 0:
                    return row, col, self.solved_grid[row][col]
        return -1, -1, -1

    def share_puzzle(self, username: str) -> str:
        puzzle_data = {
            'username': username,
            'puzzle': self.grid,
            'solving_time': -1
        }
        return json.dumps(puzzle_data)

    def load_puzzle(self, puzzle_data: str):
        data = json.loads(puzzle_data)
        self.grid = data['puzzle']

if __name__ == '__main__':
    size = 9
    game = SudokuGame(size)
    game.display()
    print('Generating a puzzle...')
    print('Here is your Sudoku puzzle:')
    game.display()
    start_time = time.time()
    while True:
        try:
            row, col = map(int, input('Enter the row and column to make a move (or type "hint" for a hint): ').split(', '))
            value = int(input('Enter the value: '))
            if game.is_safe(game.grid, row, col, value):
                game.grid[row][col] = value
                if game.grid == game.solved_grid:
                    solving_time = game.track_progress(start_time)
                    print(f'Congratulations! You solved the puzzle in {solving_time:.2f} seconds.')
                    username = input('Enter your username to share your progress: ')
                    shared_puzzle = game.share_puzzle(username)
                    print('Your puzzle has been shared.')
                    break
                else:
                    print('Continue solving...')
            else:
                print('Invalid move. Try again.')
        except ValueError:
            if input().strip().lower() == 'hint':
                hint_row, hint_col, hint_value = game.give_hint()
                print(f'Hint: Place {hint_value} at ({hint_row}, {hint_col}).')
            else:
                print('Invalid input. Please enter row, column, and value or type "hint".')