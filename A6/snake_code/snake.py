from cube import Cube
from constants import *
from utility import *

import random
import random
import numpy as np


class Snake:
    body = []
    turns = {}

    def __init__(self, color, pos, file_name=None):
        # pos is given as coordinates on the grid ex (1,5)
        self.color = color
        self.head = Cube(pos, color=color)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1
        try:
            self.q_table = np.load(file_name)
        except:
            self.q_table = np.zeros((1248, 4))

        self.lr = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.8

    def get_state_index(self, state):
        unique_number = (state[0] * 2**4 * 39 +
                    state[1] * 2**3 * 39 +
                    state[2] * 2**2 * 39 +
                    state[3] * 39 +
                    state[4])
    
        return unique_number
    
    def get_optimal_policy(self, state):
        # TODO: Get optimal policy
        idx = self.get_state_index(state)
        return np.argmax(self.q_table[idx])

    def make_action(self, state):
        chance = random.random()
        if chance < self.epsilon:
            action = random.randint(0, 3)
        else:
            action = self.get_optimal_policy(state)
        return action

    def update_q_table(self, state, action, next_state, reward):
        # TODO: Update Q-table
        recentVal = reward + self.discount_factor*(np.max(self.q_table[self.get_state_index(next_state)]))
        self.q_table[self.get_state_index(state)][action] = (1 - self.lr)*(self.q_table[self.get_state_index(state)][action]) + self.lr*recentVal

    

    def get_around_head_positions(self):
        a1 = [0, 0]
        a2 = [0, 0]
        a3 = [0, 0]
        if self.dirnx == 0:
            a1[0] = self.head.pos[0] - 1
            a1[1] = self.head.pos[1]
            a2[0] = self.head.pos[0] + 1
            a2[1] = self.head.pos[1]
            a3[0] = self.head.pos[0]
            a3[1] = self.head.pos[1] + self.dirny
        elif self.dirny == 0:
            a1[0] = self.head.pos[0]
            a1[1] = self.head.pos[1] - 1
            a2[0] = self.head.pos[0]
            a2[1] = self.head.pos[1] + 1
            a3[0] = self.head.pos[0] + self.dirnx
            a3[1] = self.head.pos[1]

        return a1, a2, a3
    
    def check_wall_collision(self, pos):
        if pos[0] == 0 or pos[0] == ROWS-1 or pos[1] == 0 or pos[1] == ROWS-1:
            return True
        return False
    
    def check_snake_body_collision(self, snake, pos):
        for bodypos in snake.body:
            if pos == bodypos:
                return True
        return False
    
    def check_barrier(self, pos, other_snake):
        if self.check_wall_collision(pos) or self.check_snake_body_collision(self, pos) or self.check_snake_body_collision(other_snake, pos):
            return 1
        else:
            return 0

    def get_direction_of_snack(self, snack):
        if snack.pos[0] <= self.head.pos[0]:
            if snack.pos[1] <= self.head.pos[1]:
                return 0
            else:
                return 2
        else:
            if snack.pos[1] <= self.head.pos[1]:
                return 1
            else:
                return 3

    def get_distance_to_snack(self, snack):
        return abs(self.head.pos[0] - snack.pos[0]) + abs(self.head.pos[1] - snack.pos[1])        

    def move(self, snack : Cube, other_snake):
        state = []
        a1, a2, a3 = self.get_around_head_positions()
        state.append(self.check_barrier(a1, other_snake))
        state.append(self.check_barrier(a2, other_snake))
        state.append(self.check_barrier(a3, other_snake))
        state.append(self.get_direction_of_snack(snack))
        state.append(self.get_distance_to_snack(snack))

        action = self.make_action(state)

        if action == 0: # Left
            self.dirnx = -1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
        elif action == 1: # Right
            self.dirnx = 1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
        elif action == 2: # Up
            self.dirny = -1
            self.dirnx = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
        elif action == 3: # Down
            self.dirny = 1
            self.dirnx = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                if i == len(self.body) - 1:
                    self.turns.pop(p)
            else:
                c.move(c.dirnx, c.dirny)

        # TODO: Create new state after moving and other needed values and return them
        new_state = []
        a1, a2, a3 = self.get_around_head_positions()
        new_state.append(self.check_barrier(a1, other_snake))
        new_state.append(self.check_barrier(a2, other_snake))
        new_state.append(self.check_barrier(a3, other_snake))
        new_state.append(self.get_direction_of_snack(snack))
        new_state.append(self.get_distance_to_snack(snack))
        return state, new_state, action

    
    def check_out_of_board(self):
        headPos = self.head.pos
        if headPos[0] >= ROWS - 1 or headPos[0] < 1 or headPos[1] >= ROWS - 1 or headPos[1] < 1:
            self.reset((random.randint(3, 18), random.randint(3, 18)))
            return True
        return False
    
    def calc_reward(self, snack, other_snake):
        reward = 0
        win_self, win_other = False, False
        
        if self.check_out_of_board():
            # TODO: Punish the snake for getting out of the board
            win_other = True
            reset(self, other_snake)
        
        if self.head.pos == snack.pos:
            self.addCube()
            snack = Cube(randomSnack(ROWS, self), color=(0, 255, 0))
            # TODO: Reward the snake for eating
            
        if self.head.pos in list(map(lambda z: z.pos, self.body[1:])):
            # TODO: Punish the snake for hitting itself
            win_other = True
            reset(self, other_snake)
            
            
        if self.head.pos in list(map(lambda z: z.pos, other_snake.body)):
            
            if self.head.pos != other_snake.head.pos:
                # TODO: Punish the snake for hitting the other snake
                win_other = True
            else:
                if len(self.body) > len(other_snake.body):
                    # TODO: Reward the snake for hitting the head of the other snake and being longer
                    win_self = True
                elif len(self.body) == len(other_snake.body):
                    # TODO: No winner
                    pass
                else:
                    # TODO: Punish the snake for hitting the head of the other snake and being shorter
                    win_other = True
                    
            reset(self, other_snake)
            
        return snack, reward, win_self, win_other
    
    def reset(self, pos):
        self.head = Cube(pos, color=self.color)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1

    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        if dx == 1 and dy == 0:
            self.body.append(Cube((tail.pos[0] - 1, tail.pos[1]), color=self.color))
        elif dx == -1 and dy == 0:
            self.body.append(Cube((tail.pos[0] + 1, tail.pos[1]), color=self.color))
        elif dx == 0 and dy == 1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] - 1), color=self.color))
        elif dx == 0 and dy == -1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] + 1), color=self.color))

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy

    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i == 0:
                c.draw(surface, True)
            else:
                c.draw(surface)

    def save_q_table(self, file_name):
        np.save(file_name, self.q_table)
        