
class ExpectimaxAI:
    def __init__(self, grid):
        self.grid = grid

    def get_best_move(self):
        actions = ['up', 'down', 'left', 'right']
        best_action = None
        best_score = float('-inf')
        for action in actions:
            grid_copy = self.grid.clone_grid() # clone the grid to simulate the move
            self.apply_action(grid_copy, action) # apply the move to the grid
            if grid_copy.moved:  # did the move change the grid?
                score = self.expectimax(grid_copy, 3, 0) 
                if score > best_score: # get best score
                    best_score = score
                    best_action = action
        print(f"Best move: {best_action}, Best score: {best_score}")  # print
        return best_action

    def expectimax(self, state, depth, agentIndex):
        if depth == 0 or self.is_terminal(state):
            return self.evaluationFunction(state)

        if agentIndex == 0: # max player's turn
            max_score = float('-inf')
            for action in ['up', 'down', 'left', 'right']:
                grid_copy = state.clone_grid()
                self.apply_action(grid_copy, action)
                if grid_copy.moved:  
                    max_score = max(max_score, self.expectimax(grid_copy, depth, agentIndex + 1))
            return max_score
        else: # random player's turn
            empty_cells = state.retrieve_empty_cells()
            if not empty_cells:
                return self.evaluationFunction(state)
            total_score = 0
            for cell in empty_cells:
                grid_copy = self.grid.clone_grid()
                grid_copy.cells[cell[0]][cell[1]] = 2
                total_score += 0.9 * self.expectimax(grid_copy, depth - 1, True)
                grid_copy.cells[cell[0]][cell[1]] = 4
                total_score += 0.1 * self.expectimax(grid_copy, depth - 1, True)
            return total_score / len(empty_cells)

    def evaluationFunction(self, grid):
        return sum(sum(row) for row in grid.cells)

    def is_terminal(self, grid):
        return not grid.has_empty_cells() and not grid.can_merge()

    def apply_action(self, state, action):
        print(f"Applying move: {action}")  # Debug print
        if action == 'up':
            state.transpose()
            state.left_compress()
            state.left_merge()
            state.moved = state.compressed or state.merged
            state.left_compress()
            state.transpose()
        elif action == 'down':
            state.transpose()
            state.reverse()
            state.left_compress()
            state.left_merge()
            state.moved = state.compressed or state.merged
            state.left_compress()
            state.reverse()
            state.transpose()
        elif action == 'left':
            state.left_compress()
            state.left_merge()
            state.moved = state.compressed or state.merged
            state.left_compress()
        elif action == 'right':
            state.reverse()
            state.left_compress()
            state.left_merge()
            state.moved = state.compressed or state.merged
            state.left_compress()
            state.reverse()

    
