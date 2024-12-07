from __future__ import print_function

import tkinter as tk 
import time
import tkinter.messagebox as messagebox
import sys
import random
from expectimax import ExpectimaxAI
from montecarlo import MonteCarloAI


class Grid:
    '''The data structure representation of the 2048 game.'''
    def __init__(self, n):
        self.size = n
        self.cells = self.generate_empty_grid()
        self.compressed = False
        self.merged = False
        self.moved = False
        self.current_score = 0

    def generate_empty_grid(self):
        return [[0] * self.size for _ in range(self.size)]

    def clone_grid(self):
        new_grid = Grid(self.size)
        new_grid.set_cells([row[:] for row in self.cells])
        new_grid.current_score = self.current_score
        new_grid.compressed = self.compressed
        new_grid.merged = self.merged
        new_grid.moved = self.moved
        return new_grid

    def set_cells(self, cells):
        self.cells = cells

    def get_state(self):
        return [row.copy() for row in self.cells]

    def random_cell(self):
        cell = random.choice(self.retrieve_empty_cells())
        i = cell[0]
        j = cell[1]
        self.cells[i][j] = 2 if random.random() < 0.9 else 4

    def retrieve_empty_cells(self):
        return [(i, j) for i in range(self.size) for j in range(self.size) if self.cells[i][j] == 0]

    def getScore(self):
        return self.current_score
    
    def left_compress(self):
        for i in range(self.size):
            self.cells[i] = [num for num in self.cells[i] if num != 0]
            self.cells[i] += [0] * (self.size - len(self.cells[i]))
    
    def left_merge(self):
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.cells[i][j] == self.cells[i][j + 1]:
                    self.cells[i][j] *= 2
                    self.cells[i][j + 1] = 0
                    self.current_score += self.cells[i][j]
    

    def has_empty_cells(self):
        return any(cell == 0 for row in self.cells for cell in row)

    def can_merge(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.cells[i][j] == 0:
                    continue
                if i < self.size - 1 and self.cells[i][j] == self.cells[i + 1][j]:
                    return True
                if j < self.size - 1 and self.cells[i][j] == self.cells[i][j + 1]:
                    return True
        return False

    def found_2048(self):
        return any(cell == 2048 for row in self.cells for cell in row)

    def clear_flags(self):
        self.compressed = False
        self.merged = False
        self.moved = False

    def move(self, direction):
        initial_empty_cells = len(self.retrieve_empty_cells())
        initial_state = self.get_state()

        if direction == 'up':
            reward = self.move_up()
        elif direction == 'down':
            reward = self.move_down()
        elif direction == 'left':
            reward = self.move_left()
        elif direction == 'right':
            reward = self.move_right()

        final_empty_cells = len(self.retrieve_empty_cells())
        final_state = self.get_state()

        # Calculate reward based on the change in the number of empty cells and the grid state
        reward += (final_empty_cells - initial_empty_cells) * 10  # Example heuristic
        reward += self.calculate_state_difference(initial_state, final_state)

        print('Reward: {}'.format(reward))
        return reward

    def move_up(self):
        self.transpose()
        reward = self.move_left()
        self.transpose()
        print('Reward (up): {}'.format(reward))
        return reward

    def move_down(self):
        self.transpose()
        reward = self.move_right()
        self.transpose()
        print('Reward (down): {}'.format(reward))
        return reward

    def move_left(self):
        reward = 0
        for row in self.cells:
            reward += self.compress(row)
            reward += self.merge(row)
            reward += self.compress(row)
        print('Reward (left): {}'.format(reward))
        return reward

    def move_right(self):
        reward = 0
        for row in self.cells:
            row.reverse()
            reward += self.compress(row)
            reward += self.merge(row)
            reward += self.compress(row)
            row.reverse()
        print('Reward (right): {}'.format(reward))
        return reward

    def compress(self, row):
        new_row = [num for num in row if num != 0]
        new_row += [0] * (self.size - len(new_row))
        reward = 0
        if new_row != row:
            self.moved = True
            reward = sum(new_row) - sum(row)
        row[:] = new_row
        return reward

    def merge(self, row):
        print("Merging row: ", row)
        reward = 0
        for i in range(self.size - 1):
            if row[i] != 0 and row[i] == row[i + 1]:
                row[i] *= 2
                reward += row[i]
                row[i + 1] = 0
                self.merged = True
                self.moved = True
        print("moved", self.moved)
        return reward

    def calculate_state_difference(self, initial_state, final_state):
        """
        Calculate the difference between the initial and final grid states.
        This can be used as part of the reward calculation.
        """
        difference = 0
        for i in range(self.size):
            for j in range(self.size):
                difference += abs(final_state[i][j] - initial_state[i][j])
        return difference

    def transpose(self):
        self.cells = [list(row) for row in zip(*self.cells)]

    def reverse(self):
        self.cells = [row[::-1] for row in self.cells]

    def can_move_up(self):
        for j in range(self.size):
            for i in range(1, self.size):
                if self.cells[i][j] != 0 and (self.cells[i - 1][j] == 0 or self.cells[i - 1][j] == self.cells[i][j]):
                    return True
        return False

    def can_move_down(self):
        for j in range(self.size):
            for i in range(self.size - 2, -1, -1):
                if self.cells[i][j] != 0 and (self.cells[i + 1][j] == 0 or self.cells[i + 1][j] == self.cells[i][j]):
                    return True
        return False

    def can_move_left(self):
        for i in range(self.size):
            for j in range(1, self.size):
                if self.cells[i][j] != 0 and (self.cells[i][j - 1] == 0 or self.cells[i][j - 1] == self.cells[i][j]):
                    return True
        return False

    def can_move_right(self):
        for i in range(self.size):
            for j in range(self.size - 2, -1, -1):
                if self.cells[i][j] != 0 and (self.cells[i][j + 1] == 0 or self.cells[i][j + 1] == self.cells[i][j]):
                    return True
        return False
    
    

class GamePanel:
    '''The GUI view class of the 2048 game showing via tkinter.'''
    CELL_PADDING = 10
    BACKGROUND_COLOR = '#92877d'
    EMPTY_CELL_COLOR = '#9e948a'
    CELL_BACKGROUND_COLOR_DICT = {
        '2': '#eee4da',
        '4': '#ede0c8',
        '8': '#f2b179',
        '16': '#f59563',
        '32': '#f67c5f',
        '64': '#f65e3b',
        '128': '#edcf72',
        '256': '#edcc61',
        '512': '#edc850',
        '1024': '#edc53f',
        '2048': '#edc22e',
        'beyond': '#3c3a32'
    }
    CELL_COLOR_DICT = {
        '2': '#776e65',
        '4': '#776e65',
        '8': '#f9f6f2',
        '16': '#f9f6f2',
        '32': '#f9f6f2',
        '64': '#f9f6f2',
        '128': '#f9f6f2',
        '256': '#f9f6f2',
        '512': '#f9f6f2',
        '1024': '#f9f6f2',
        '2048': '#f9f6f2',
        'beyond': '#f9f6f2'
    }
    FONT = ('Verdana', 24, 'bold')

    def __init__(self, grid):
        self.grid = grid
        self.root = tk.Tk()
        if sys.platform == 'win32':
            self.root.iconbitmap('2048.ico')
        self.root.title('2048')
        self.root.resizable(False, False)
        self.background = tk.Frame(self.root, bg=GamePanel.BACKGROUND_COLOR)
        self.cell_labels = []
        for i in range(self.grid.size):
            row_labels = []
            for j in range(self.grid.size):
                label = tk.Label(self.background, text='',
                                 bg=GamePanel.EMPTY_CELL_COLOR,
                                 justify=tk.CENTER, font=GamePanel.FONT,
                                 width=4, height=2)
                label.grid(row=i, column=j, padx=10, pady=10)
                row_labels.append(label)
            self.cell_labels.append(row_labels)
        self.background.pack(side=tk.TOP)


    def paint(self):
        for i in range(self.grid.size):
            for j in range(self.grid.size):
                if self.grid.cells[i][j] == 0:
                    self.cell_labels[i][j].configure(
                         text='',
                         bg=GamePanel.EMPTY_CELL_COLOR)
                else:
                    cell_text = str(self.grid.cells[i][j])
                    if self.grid.cells[i][j] > 2048:
                        bg_color = GamePanel.CELL_BACKGROUND_COLOR_DICT.get('beyond')
                        fg_color = GamePanel.CELL_COLOR_DICT.get('beyond')
                    else:
                        bg_color = GamePanel.CELL_BACKGROUND_COLOR_DICT.get(cell_text)
                        fg_color = GamePanel.CELL_COLOR_DICT.get(cell_text)
                    self.cell_labels[i][j].configure(
                        text=cell_text,
                        bg=bg_color, fg=fg_color)

class Game:
    '''The main game class which is the controller of the whole game.'''
    def __init__(self, grid, panel):
        self.grid = grid
        self.panel = panel
        self.start_cells_num = 2
        self.over = False
        self.won = False
        self.keep_playing = False
        self.ai = MonteCarloAI(self, gamma=0.9, simulations=100)

    def clone_game(self):
        """
        Creates a deep copy of the game, including its grid and state.
        """
        grid_copy = self.grid.clone_grid()
        game_copy = Game(grid_copy, self.panel)
        game_copy.over = self.over
        game_copy.won = self.won
        game_copy.keep_playing = self.keep_playing
        return game_copy

    def get_state(self):
        return self.grid.get_state()

    def simulate_action(self, action):
        game_copy = self.clone_game()
        initial_score = game_copy.grid.current_score
        reward = game_copy.grid.move(action)  # Use the move method to update the grid state and get the reward
        return (game_copy, reward)  # return the simulated grid and reward

    def is_game_terminated(self):
        return self.over or (self.won and not self.keep_playing)

    def get_legal_actions(self):
        actions = []
        if self.can_move_up():
            actions.append('up')
        if self.can_move_down():
            actions.append('down')
        if self.can_move_left():
            actions.append('left')
        if self.can_move_right():
            actions.append('right')
        return actions

    def can_move_up(self):
        return self.grid.can_move_up()

    def can_move_down(self):
        return self.grid.can_move_down()

    def can_move_left(self):
        return self.grid.can_move_left()

    def can_move_right(self):
        return self.grid.can_move_right()

    def start(self):
        self.add_start_cells()
        self.panel.paint()
        self.run_ai()

    def add_start_cells(self):
        for _ in range(self.start_cells_num):
            self.grid.random_cell()

    def can_move(self):
        return self.grid.has_empty_cells() or self.grid.can_merge()

    def apply_action(self, action):
        # Apply the action to the grid
        if action == 'up':
            self.up(self.grid)
        elif action == 'down':
            self.down(self.grid)
        elif action == 'left':
            self.left(self.grid)
        elif action == 'right':
            self.right(self.grid)
        
        self.grid.moved = True

    def run_ai(self):
        if self.is_game_terminated():
            print("Game terminated")
            return

        self.grid.clear_flags()
        move = self.ai.getAction(self)
        print("MOVED HERE", self.grid.moved)
        print(f"AI selected move: {move}")
        if move:
            self.apply_action(move)

        print("MOVED HERE", self.grid.moved)
        self.panel.paint()
        self.panel.root.update()

        print('Score: {}'.format(self.grid.current_score))
        if self.grid.found_2048():
            self.you_win()
            if not self.keep_playing:
                return
            
        print("about to generate")
        print("MOVEDDDD", self.grid.moved)
        if self.grid.moved:
            self.grid.random_cell()  # Add a new tile if the grid has moved

        print("about to paint")
        self.panel.paint()
        if not self.can_move():
            self.over = True
            self.game_over()
            return
        
        time.sleep(0.01)

        self.panel.root.after(100, self.run_ai)

    def you_win(self):
        if not self.won:
            self.won = True
            print('You Win!')
            if messagebox.askyesno('2048', 'You Win!\nAre you going to continue the 2048 game?'):
                self.keep_playing = True

    def game_over(self):
        print('Game over!')
        messagebox.showinfo('2048', 'Oops!\nGame over!')

    def up(self, grid):
        grid.transpose()
        grid.left_compress()
        grid.left_merge()
        grid.moved = grid.compressed or grid.merged
        grid.left_compress()
        grid.transpose()

    def down(self, grid):
        grid.transpose()
        grid.reverse()
        grid.left_compress()
        grid.left_merge()
        grid.moved = grid.compressed or grid.merged
        grid.left_compress()
        grid.reverse()
        grid.transpose()

    def left(self, grid):
        grid.left_compress()
        grid.left_merge()
        grid.moved = grid.compressed or grid.merged
        grid.left_compress()

    def right(self, grid):
        grid.reverse()
        grid.left_compress()
        grid.left_merge()
        grid.moved = grid.compressed or grid.merged
        grid.left_compress()
        grid.reverse()

if __name__ == '__main__':
    size = 4
    grid = Grid(size)
    panel = GamePanel(grid)
    game2048 = Game(grid, panel)
    game2048.start()
    panel.root.mainloop() 