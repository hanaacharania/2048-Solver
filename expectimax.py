actions = ['up', 'down', 'left', 'right']

class ExpectimaxAI:

    def __init__(self, game, depth=2):
        self.game = game
        self.depth = depth

    def getAction(self):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All tiles are modeled as choosing uniformly at random from their
        legal moves (i.e. 2, 4).
        """
        def expectimax(state, depth, agentIndex):
            # base case: if the state is terminal or depth is 0, return the score
            if depth == 0 or self.is_terminal(state):
                return self.evaluationFunction(state)

            # if the agent is max (AI's turn)
            if agentIndex == 0:  
                maxVal = float('-inf')
                for action in actions:
                    grid_copy = self.game.simulate_action(action)  # use simulate_action
                    if grid_copy.moved:  # consider valid moves only
                        maxVal = max(maxVal, expectimax(grid_copy, depth - 1, 1))
                return maxVal

            # if the agent is min/random
            else:
                expectedVal = 0
                empty_cells = state.retrieve_empty_cells() 
                probability = 1 / len(empty_cells) # tile spawns randomly in an empty cell
                for cell in empty_cells: # ensures all possible tile spawns (i.e. 2,4) are considered
                    grid_copy = state.clone_grid()
                    grid_copy.cells[cell[0]][cell[1]] = 2 # spawn a 2 tile
                    expectedVal += 0.9 * probability * expectimax(grid_copy, depth - 1, 0) # 90% chance of spawning a 2 tile (known)
                    grid_copy.cells[cell[0]][cell[1]] = 4 # spawn a 4 tile
                    expectedVal += 0.1 * probability * expectimax(grid_copy, depth - 1, 0) # 10% chance of spawning a 4 tile (known)
                return expectedVal

        bestAction = None
        bestScore = float('-inf')
        for action in actions:
            grid_copy = self.game.simulate_action(action)  
            if grid_copy.moved:  # consider valid moves only
                score = expectimax(grid_copy, self.depth, 1)
                if score > bestScore:
                    bestScore = score
                    bestAction = action
        print(f"Best move: {bestAction}, Best score: {bestScore}")
        return bestAction

    def evaluationFunction(self, grid): 
        return self.calculate_score(grid)
    
    def calculate_smoothness(self, grid): # smoothness heuristic = tries to minimize the difference between adjacent tiles
        smoothness = 0
        for i in range(grid.size):
            for j in range(grid.size - 1):
                if grid.cells[i][j] != 0:
                    smoothness -= abs(grid.cells[i][j] - grid.cells[i][j + 1]) # horizontal smoothness
                if grid.cells[j][i] != 0:
                    smoothness -= abs(grid.cells[j][i] - grid.cells[j + 1][i]) # vertical smoothness
        return smoothness

    def calculate_score(self, grid):
        max_tile = max(max(row) for row in grid.cells) # max tile in the grid
        empty_cells = len(grid.retrieve_empty_cells()) # number of empty cells
        smoothness = self.calculate_smoothness(grid) # smoothness heuristic
        return max_tile + empty_cells + smoothness # score = max tile + empty cells + smoothness

    def is_terminal(self, grid):
        return grid.found_2048() or (not grid.has_empty_cells() and not grid.can_merge()) # terminal state if 2048 tile is found or no empty cells and no possible merges