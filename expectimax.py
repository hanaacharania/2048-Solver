
class ExpectimaxAI:

    def __init__(self, game, depth=3):
        self.game = game
        self.depth = depth

    def getAction(self, game):

        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All tiles are modeled as choosing uniformly at random from their
        legal moves (i.e. 2, 4).
        """
        def expectimax(state, depth, agentIndex):
            # base case: if the state is terminal or depth is 0, return the score
        
            if depth == 0 or self.is_terminal(state):
                return self.evaluationFunction(state)

            # if the agent is max
            if agentIndex == 0:  
                maxVal = float('-inf')
                for action in game.get_legal_actions():
                    grid_copy = self.game.simulate_action(action)[0] # use simulate_action
                    if grid_copy.grid.moved:  # consider valid moves only
                        maxVal = max(maxVal, expectimax(grid_copy.grid, depth - 1, 1))
                return maxVal

            # if the agent is min/random
            else:
                expectedVal = 0
                empty_cells = state.retrieve_empty_cells() 
                probability = 1 / len(empty_cells) # tile spawns randomly in an empty cell
                for cell in empty_cells: # ensures all possible tile spawns (i.e. 2,4) are considered
                    grid_copy = state.clone_grid()
                    # print(grid_copy.cells)
                    grid_copy.cells[cell[0]][cell[1]] = 2 # spawn a 2 tile
                    expectedVal += 0.9 * probability * expectimax(grid_copy, depth - 1, 0) # 90% chance of spawning a 2 tile (known)
                    grid_copy.cells[cell[0]][cell[1]] = 4 # spawn a 4 tile
                    expectedVal += 0.1 * probability * expectimax(grid_copy, depth - 1, 0) # 10% chance of spawning a 4 tile (known)
                return expectedVal

        bestAction = None
        bestScore = float('-inf')
        for action in game.get_legal_actions():
            grid_copy = self.game.simulate_action(action)[0]  
            if grid_copy.grid.moved:  # consider valid moves only
                score = expectimax(grid_copy.grid, self.depth, 1)
                if score > bestScore:
                    bestScore = score
                    bestAction = action
        print(f"Best move: {bestAction})")
        return bestAction
    
    def calculate_smoothness(self, grid): # smoothness heuristic = tries to minimize the difference between adjacent tiles
        smoothness = 0
        for i in range(grid.size):
            for j in range(grid.size - 1):
                if grid.cells[i][j] != 0:
                    smoothness -= abs(grid.cells[i][j] - grid.cells[i][j + 1]) # horizontal smoothness
                if grid.cells[j][i] != 0:
                    smoothness -= abs(grid.cells[j][i] - grid.cells[j + 1][i]) # vertical smoothness
        return smoothness
    
    # penalty for tiles in middle
    def mid_tile_penalty(self, grid):
        penalty = 0
        for i in range(grid.size):
            for j in range(grid.size):
                value = grid.cells[i][j]
                if value != 0:
                    distance = min(i, grid.size - 1 - i) + min(j, grid.size - 1 - j)
                    penalty += distance * value
        return penalty
    
    def monotonicity(self, grid):
        best = -1
        def rotate_90_clockwise(cells):
            return [list(row) for row in zip(*cells[::-1])]

        cells = grid.cells

        for _ in range(4): # rotate 4 times to check all directions
            current = 0
            
            # row monotonicity
            for row in range(len(cells)):
                for col in range(len(cells[row]) - 1):
                    if cells[row][col] >= cells[row][col + 1]:
                        current += 1

            # column monotonicity
            for col in range(len(cells[0])):
                for row in range(len(cells) - 1):
                    if cells[row][col] >= cells[row + 1][col]:
                        current += 1
            
            if current > best:
                best = current
            
            cells = rotate_90_clockwise(cells)
        
        return best
        
    def corner_heuristic(self, grid):
        max_tile = max(max(row) for row in grid.cells)
        corners = [
            grid.cells[0][0], grid.cells[0][grid.size - 1],
            grid.cells[grid.size - 1][0], grid.cells[grid.size - 1][grid.size - 1]
        ]
        return 1 if max_tile in corners else 0
    
    def evaluationFunction(self, grid): 
        score = self.calculate_score(grid)
        return score
    
    def calculate_score(self, grid):
        empty_cells = len(grid.retrieve_empty_cells()) # number of empty cells
        corner_score = self.corner_heuristic(grid)
        smoothness = self.calculate_smoothness(grid)
        border_penalty = self.mid_tile_penalty(grid)
        monotonicity_score = self.monotonicity(grid)
        score = ( 
                 100 * empty_cells + 
                 corner_score +
                 smoothness +
                 1000 + monotonicity_score +
                 -5 * border_penalty)

        return score 

    def is_terminal(self, state):
        return state.found_2048() or (not state.has_empty_cells() and not state.can_merge()) # terminal state if 2048 tile is found or no empty cells and no possible merges