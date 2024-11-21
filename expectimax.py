
class ExpectimaxAI:
    def __init__(self, grid):
        self.grid = grid

    def get_best_move(self):
        moves = ['up', 'down', 'left', 'right']
        best_move = None
        best_score = float('-inf')
        for move in moves:
            grid_copy = self.grid.clone_grid()
            self.apply_move(grid_copy, move)
            if grid_copy.moved:  # Only evaluate if the move changes the grid
                score = self.expectimax(grid_copy, depth=3, is_max=True)
                if score > best_score:
                    best_score = score
                    best_move = move
        print(f"Best move: {best_move}, Best score: {best_score}")  # Debug print
        return best_move

    def expectimax(self, grid, depth, is_max):
        if depth == 0 or self.is_terminal(grid):
            return self.evaluate(grid)

        if is_max:
            max_score = float('-inf')
            for move in ['up', 'down', 'left', 'right']:
                grid_copy = grid.clone_grid()
                self.apply_move(grid_copy, move)
                if grid_copy.moved:  # Only evaluate if the move changes the grid
                    score = self.expectimax(grid_copy, depth - 1, False)
                    max_score = max(max_score, score)
            return max_score
        else:
            empty_cells = grid.retrieve_empty_cells()
            if not empty_cells:
                return self.evaluate(grid)
            total_score = 0
            for cell in empty_cells:
                grid_copy = self.grid.clone_grid()
                grid_copy.cells[cell[0]][cell[1]] = 2
                total_score += 0.9 * self.expectimax(grid_copy, depth - 1, True)
                grid_copy.cells[cell[0]][cell[1]] = 4
                total_score += 0.1 * self.expectimax(grid_copy, depth - 1, True)
            return total_score / len(empty_cells)

    def evaluate(self, grid):
        return sum(sum(row) for row in grid.cells)

    def is_terminal(self, grid):
        return not grid.has_empty_cells() and not grid.can_merge()

    def apply_move(self, grid, move):
        print(f"Applying move: {move}")  # Debug print
        if move == 'up':
            grid.transpose()
            grid.left_compress()
            grid.left_merge()
            grid.moved = grid.compressed or grid.merged
            grid.left_compress()
            grid.transpose()
        elif move == 'down':
            grid.transpose()
            grid.reverse()
            grid.left_compress()
            grid.left_merge()
            grid.moved = grid.compressed or grid.merged
            grid.left_compress()
            grid.reverse()
            grid.transpose()
        elif move == 'left':
            grid.left_compress()
            grid.left_merge()
            grid.moved = grid.compressed or grid.merged
            grid.left_compress()
        elif move == 'right':
            grid.reverse()
            grid.left_compress()
            grid.left_merge()
            grid.moved = grid.compressed or grid.merged
            grid.left_compress()
            grid.reverse()

    
