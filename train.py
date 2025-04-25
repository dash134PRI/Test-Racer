import numpy as np
from car_racing_env import CarRacingEnv
from dqn_agent import DQNAgent
import time

def train():
    env = CarRacingEnv()
    state_size = 8  # From CarRacingEnv._get_state()
    action_size = 4  # [accelerate, brake, left, right]
    agent = DQNAgent(state_size, action_size)
    batch_size = 32
    episodes = 1000
    
    for e in range(episodes):
        state = env.reset()
        state = np.reshape(state, [1, state_size])
        total_reward = 0
        done = False
        
        while not done:
            # Get action from agent
            action = agent.act(state)
            
            # Convert action index to actual action values
            action_values = [0, 0]  # [acceleration, steering]
            if action == 0:  # accelerate
                action_values = [1, 0]
            elif action == 1:  # brake
                action_values = [-1, 0]
            elif action == 2:  # left
                action_values = [0, -1]
            elif action == 3:  # right
                action_values = [0, 1]
            
            # Take action
            next_state, reward, done = env.step(action_values)
            next_state = np.reshape(next_state, [1, state_size])
            
            # Remember the experience
            agent.remember(state, action, reward, next_state, done)
            
            # Update state
            state = next_state
            total_reward += reward
            
            # Render the environment
            env.render()
            
            # Train the agent
            agent.replay(batch_size)
            
            if done:
                print(f"episode: {e}/{episodes}, score: {total_reward}, e: {agent.epsilon:.2f}")
                break
        
        # Update target model every 10 episodes
        if e % 10 == 0:
            agent.update_target_model()
            agent.save(f"models/car_racing_dqn_{e}.h5")
    
    env.close()

if __name__ == "__main__":
    train() 