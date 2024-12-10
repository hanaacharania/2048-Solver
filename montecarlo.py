import random
from expectimax import ExpectimaxAI

class MonteCarloAI:
    def __init__(self, game, gamma=0.9, simulations=1, max_depth=2): # Initialize game, discount factor, number of simulations, and maximum depth
        self.game = game 
        self.gamma = gamma # discount factor
        self.simulations = simulations
        self.max_depth = max_depth  #
        self.N = {}  # counter of total visits
        self.U = {}  # utility estimates
        self.expectimax = ExpectimaxAI(game) # initialize Expectimax AI

    def getAction(self, game): # returns the best action based on the Monte Carlo Tree Search algorithm
        
        best_action = None
        best_score = -float('inf')

        for action in game.get_legal_actions(): # left, right, up, down
            total_score = 0
            for _ in range(self.simulations):
                total_score += self.simulate(game, action) # simulate the game and add to the total score
            average_score = total_score / self.simulations # calculate the average score

            if average_score > best_score: # update the best action and best score
                best_score = average_score
                best_action = action

        # print(f"Best move: {best_action}, best score: {best_score}")
        return best_action
    
    def simulate(self, game, action): # simulate the game and return the utility of the initial state of the trajectory

        # clone the game and simulate the action
        game_clone = game.clone_game()
        reward = game_clone.simulate_action(action)[1] # get the reward

        trajectory = [] 
        depth = 0  # depth counter
        while not game_clone.is_game_terminated() and depth < self.max_depth: 
            for row in game_clone.get_state(): 
                state = tuple(tuple(row)) # convert the state to a tuple to hold state, policy_action, and reward
            legal_actions = game_clone.get_legal_actions() 

            # pick a policy action using epsilon-greedy strategy
            if random.random() < 0.1: 
                policy_action = random.choice(legal_actions) # exploration
            else: # take action w/ highest utility
                bestAction = None
                bestUtility = -float('inf')
                for action in legal_actions:
                        nextState = game_clone.simulate_action(action)[0].get_state() 
                        sTuple = tuple(tuple(row) for row in nextState) 
                        utility = self.U.get(sTuple, 0) # get the utility of the next state

                        if utility > bestUtility:
                            bestUtility = utility
                            bestAction = action
                policy_action = bestAction # exploitation
            # policy_action = random.choice(legal_actions)  # use this for baseline testing
            
            reward += game_clone.simulate_action(policy_action)[1] # get the reward
            trajectory.append((state, policy_action, reward)) 
            depth += 1  # increment the depth counter

        # Update utilities estimates based on the trajectory
        self.updateUtilities(trajectory)

        # return the utility of the initial state of the trajectory
        for row in game.get_state():
            initial_state = tuple(tuple(row))
        return self.U.get(initial_state, 0) 
    

    def updateUtilities(self, trajectory): # update the utilities based on the trajectory

        # print("updating utilities")
        T = len(trajectory)
        for t in range(T):
            state, _, reward = trajectory[t] # get the state, policy action, and reward
            if state not in self.N: # if state was unvisited, initialize the counters
                self.N[state] = 0 # counter of total visits
                self.U[state] = 0 # utility estimates

            self.N[state] += 1 # increment the counter of total visits

            # calculate utility u_t
            ut = sum(self.gamma ** (k - t) * trajectory[k][2] for k in range(t, T))

            # Update utility estimate U^pi(s_t) based on utility u_t
            self.U[state] = ((self.N[state] - 1) * self.U[state] + ut) / self.N[state]  
    
    