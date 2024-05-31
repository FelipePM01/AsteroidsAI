import torch
import random
import numpy as np
from collections import deque
from Game import Game
import model
from helper import plot

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

    def get_action(self, state):
        #random moves: tradeoff exploration / exploitation
        self.epsilon = 0
        final_move = [0,0,0,0] # considerando [forward, left, right, shot]
        model=torch.load("model/model.pth")
        state0 = torch.tensor(state, dtype=torch.float)
        prediction = self.model(state0)
        move = torch.argmax(prediction).item()
        final_move[move] = 1
    
        return final_move

def run():

    agent = Agent()
    game = Game(30, False, True)
    game.start_game_loop()

    while True: 
        #get old state
        state_old = game.get_state()

        #get move
        final_move = agent.get_action(state_old)

        #perform move and get new state
        reward, game_over_state, score = game.play_step(final_move)

        

        if game_over_state:
            #train long memory, plot result
            break

           
           

            

if __name__ == '__main__':
    run()