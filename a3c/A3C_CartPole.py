import torch
import gym
import torch.optim as optim
import torch.multiprocessing as mp

from network import Net_Simple
from worker import Worker

# NUM_PROCESS = mp.cpu_count()
NUM_PROCESS = 4

class A3CAgent:
    def __init__(self, gamma, env, lr, max_episode):
        
        self.gamma = gamma
        self.max_episode = max_episode

        self.global_actor_net = Net_Simple(outputs=2)
        self.global_critic_net = Net_Simple(outputs=1)
        self.global_actor_net.share_memory()
        self.global_critic_net.share_memory()

        self.global_actor_optim = optim.Adam(self.global_actor_net.parameters(), lr = lr)
        self.global_critic_optim = optim.Adam(self.global_critic_net.parameters(), lr = lr)

        self.workers = []
        # for i in range(4):
        for i in range(NUM_PROCESS):
            self.workers.append(Worker(i, self.gamma, env[i], self.global_actor_net, \
                                        self.global_critic_net, self.global_actor_optim, \
                                        self.global_critic_optim, self.max_episode))

    def train(self, ):
        for worker in self.workers:
            worker.start()

        for worker in self.workers:
            worker.join()

    def save(self, filename='./parameter'):
        torch.save(self.global_actor_net.state_dict(), filename+"_actor.pkl")
        torch.save(self.global_critic_net.state_dict(), filename+"_critic.pkl")


if __name__ == "__main__":
    # env = gym.make("CartPole-v0")
    env = []
    for i in range(NUM_PROCESS):
        env.append(gym.make('CartPole-v0'))
    
    gamma = 0.99
    lr = 1e-3
    max_episode = 1000

    agent = A3CAgent(gamma, env, lr, max_episode)
    agent.train()
    agent.save()