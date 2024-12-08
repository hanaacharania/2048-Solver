import random

class MonteCarloAI:
    def __init__(self, game, gamma=0.9, simulations=100, max_depth=50):
        self.game = game
        self.gamma = gamma
        self.simulations = simulations
        self.max_depth = max_depth  # Maximum depth limit for the simulation
        self.N = {}  # Counter for state visits
        self.U = {}  # Utility estimates

    def getAction(self, game):
        
        best_action = None
        best_score = -float('inf')

        for action in game.get_legal_actions():
            total_score = 0
            for _ in range(self.simulations):
                total_score += self.simulate(game, action)
            average_score = total_score / self.simulations

            if average_score > best_score:
                best_score = average_score
                best_action = action

        # print(f"Best move: {best_action}, best score: {best_score}")
        return best_action
    
    def simulate(self, game, action):

        # Clone the game to avoid modifying the original game state
        game_clone = game.clone_game()
        reward = game_clone.simulate_action(action)[1]

        trajectory = []
        depth = 0  # Initialize depth counter
        while not game_clone.is_game_terminated() and depth < self.max_depth:
            state = tuple(map(tuple, game_clone.get_state()))  # Convert state to tuple
            legal_actions = game_clone.get_legal_actions()
            policy_action = random.choice(legal_actions)  # Use random actions during the simulation
            reward += game_clone.simulate_action(policy_action)[1]
            trajectory.append((state, policy_action, reward))
            depth += 1  # Increment depth counter

        # Update utility estimates based on the trajectory
        self.updateUtilities(trajectory)

        # Return the utility of the initial state
        initial_state = tuple(map(tuple, game.get_state()))  # Convert state to tuple
        # print("end of simulation")
        return self.U.get(initial_state, 0)
    

    def updateUtilities(self, trajectory):

        # print("updating utilities")
        T = len(trajectory)
        for t in range(T):
            state, _, reward = trajectory[t]
            if state not in self.N:
                self.N[state] = 0
                self.U[state] = 0

            self.N[state] += 1

            # Calculate the utility ut
            ut = sum(self.gamma ** (k - t) * trajectory[k][2] for k in range(t, T))

            # Update the utility estimate
            self.U[state] = ((self.N[state] - 1) * self.U[state] + ut) / self.N[state]  
    
    