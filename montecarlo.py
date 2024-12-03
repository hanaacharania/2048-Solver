import random

def e_greedy_policy(self, game, epsilon=0.1):
    # choose a random action with probability epsilon
    if random.random() < epsilon:
        return random.choice(game.get_legal_actions())
    # choose the best action with probability 1 - epsilon
    else:
        best_action = None
        best_score = float('-inf')
        for action in game.get_legal_actions():
            game_copy = game.clone_grid()
            score = game_copy.simulate_action(action)[1]
            if score > best_score:
                best_score = score
                best_action = action
        return best_action

class MonteCarloAI:
    def __init__(self, game, policy, gamma, simulations=100):
        self.game = game
        self.simulations = simulations
        self.num_visits = {}
        self.utilities = {}
        self.gamma = gamma
        self.policy = policy

    def getAction(self, game):
        actions = ['up', 'down', 'left', 'right']
        best_action = None
        best_score = float('-inf')

        for action in actions:
            total_score = 0
            for _ in range(self.simulations):
                total_score += self.simulate(game, action)
            average_score = total_score / self.simulations

            if average_score > best_score:
                best_score = average_score
                best_action = action

        return best_action
        
    def simulate(self, game, action):
        game_copy = game.clone_grid()
        game_copy.simulate_action(action)[1]

        trajectory = []
        while not game_copy.is_game_terminated():
            state = game_copy.get_state()
            policy_action = self.policy(game_copy)
            score = game_copy.simulate_action(action)[1]
            trajectory.append((state, policy_action, score))

        # update the utilities
        self.update_utilities(trajectory)

        # return utility of the initial state
        initial_state = game.get_state()
        return self.utilities.get(initial_state, 0)

    def update_utilities(self, trajectory):
        T = len(trajectory)
        for t in range(T):
            state, _, reward = trajectory[t]
            if state not in self.num_visits:
                self.num_visits[state] = 0
                self.utilities[state] = 0

            self.num_visits[state] += 1

            # calc utility at time t
            u_t = sum(self.gamma ** (k-t) * reward for k in range(t, T))

            # update the utility
            self.utilities[state] = ((self.num_visits[state] - 1) 
                                     * self.utilities[state] + u_t) / self.num_visits[state]

  


