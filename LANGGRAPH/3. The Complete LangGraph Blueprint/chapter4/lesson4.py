

class Agent:
    def __init__(self, name, capabilities):
        self.name = name
        self.capabilities = capabilities
        self.relationships = {}

    def add_relationship(self, other_agent, relationship_type):
        self.relationships[other_agent.name] = relationship_type

    def interact(self, other_agent, action):
        if action in self.capabilities:
            print(f"{self.name} performs {action} with {other_agent.name}")
        else:
            print(f"{self.name} cannot perform {action}")

    def __str__(self):
        return f"Agent {self.name} with capabilities: {', '.join(self.capabilities)}"
    
class Environment:
    def __init__(self):
        self.agents = {}

    def add_agent(self, agent):
        if agent.name not in self.agents:
            self.agents[agent.name] = agent
        else:
            print(f"An agent with the name {agent.name} already exists.")

    def simulate_interaction(self, agent1_name, agent2_name, action):
        if agent1_name in self.agents and agent2_name in self.agents:
            agent1 = self.agents[agent1_name]
            agent2 = self.agents[agent2_name]
            agent1.interact(agent2, action)
        else:
            print("One or both agents not found in the environment.")

    def __str__(self):
        agent_info = "\n".join([str(agent) for agent in self.agents.values()])
        return f"Environment with agents:\n{agent_info}"
    
# Create an environment
env = Environment()

# Create agents
agent1 = Agent("Alice", ["talk", "walk"])
agent2 = Agent("Bob", ["talk", "run"])

# Add agents to the environment
env.add_agent(agent1)
env.add_agent(agent2)

# Set relationships (optional)
agent1.add_relationship(agent2, "friend")
agent2.add_relationship(agent1, "friend")

# Simulate interaction
env.simulate_interaction("Alice", "Bob", "talk")
env.simulate_interaction("Alice", "Bob", "run")

# Print agents
print(agent1)
print(agent2)