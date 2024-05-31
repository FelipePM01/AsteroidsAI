import torch
import random
import numpy as np
from collections import deque
from Game import Game
import model

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.01

class Agent: 

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0.001 #randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = model.Linear_QNet(49,1024,4) 
        self.trainer = model.QTrainer(self.model, LR, self.gamma) 

    def remember(self, state, action, reward, next_state, game_over_state):
        self.memory.append((state, action, reward, next_state, game_over_state)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, game_over_states = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_over_states)

    def train_short_memory(self, state, action, reward, next_state, game_over_state):
        self.trainer.train_step(state, action, reward, next_state, game_over_state)

    def get_action(self, state):
        #random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games # numero de jogos
        final_move = [0,0,0,0] # considerando [forward, left, right, shot]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
            final_move[3] = random.randint(0, 1)
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        
        return final_move

def train():

    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = Game(10000, True, True)
    game.start_game_loop()

    while True: 
        #get old state
        state_old = game.get_state()

        #get move
        final_move = agent.get_action(state_old)

        #perform move and get new state
        reward, game_over_state, score = game.play_step(final_move)
        state_new = game.get_state()

        #train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, game_over_state)

        #remember
        agent.remember(state_old, final_move, reward, state_new, game_over_state)

        if game_over_state:
            #train long memory, plot result
            game.start_game_loop()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()
            
            print('Game', agent.n_games, 'Score', score, 'Record', record)

            #plot

if __name__ == '__main__':
    train()