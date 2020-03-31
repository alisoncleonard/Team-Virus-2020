# to run with model, run, and server files, use terminal command $ mesa runserver

# My test model only has 2 types: susceptible and infected
# on each step, if any neighbors are infected then you become infected

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector

class VirusModelAgent(Agent):
    '''
    Agent in virus model. Each agent is an individual person.
    '''
    def __init__(self, pos, model, agent_type):
        '''
         Create a new VirusModel agent.
         Args:
            unique_id: Unique identifier for the agent.
            x, y: Agent initial location.
            agent_type: Indicator for the agent's type (susceptible=1, infected=0)
        '''
        super().__init__(pos, model)
        self.pos = pos
        self.type = agent_type

    def step(self):  # step function
        # Built-in get_neighbors function returns a list of neighbors.
        # Two types of cell neighborhoods: Moore (including diagonals), and
        # Von Neumann (only up/down/left/right).
        # Can include an argument as to whether to include the center cell itself as one of the neighbors.
        neighbors = self.model.grid.get_neighbors(
             self.pos,
             moore=False, # uses Von Neumann neighborhoods
             include_center=False)
        for neighbor in neighbors:
            # if your neighbor is infected, you become infected
            if neighbor.type == 0:
                self.type = 0
        if self.type == 0:
            self.model.infected_count += 1 # updates count of infected agents
            self.model.infected_percent = self.model.infected_count / self.model.agent_count # updates percentage of infected agents

class Virus(Model):
    '''
    Model class for the Virus model.
    '''

    def __init__(self, height=20, width=20, density=0.3, infected_seed_pc=0.05):
        # model is seeded with default parameters for density and infected seed percent
        # can also change defaults with user settable parameter slider in GUI
        '''
        '''

        self.height = height # height and width of grid
        self.width = width
        self.density = density # density of agents in grid space
        self.infected_seed_pc = infected_seed_pc # percent of infected agents at start of simulation

        self.schedule = RandomActivation(self) # controls the order that agents are activated and step
        self.grid = SingleGrid(width, height, torus=True) # specify only one agent per cell
        # can use multigrid if we need multiple agents per cell

        self.infected_count = 0
        self.infected_percent = 0
        self.agent_count = 1 # to avoid divide by 0 error

        # uses DataCollector built in module to collect data from each model run
        self.datacollector = DataCollector(
            {"infected_percent": "infected_percent"},
            {"x": lambda m: m.pos[0], "y": lambda m: m.pos[1]})

        # Set up agents
        # We use a grid iterator that returns
        # the coordinates of a cell as well as
        # its contents. (coord_iter)
        for cell in self.grid.coord_iter():
            x = cell[1]
            y = cell[2]
            if self.random.random() < self.density:
                if self.random.random() < self.infected_seed_pc:
                    agent_type = 0
                else:
                    agent_type = 1

                agent = VirusModelAgent((x, y), self, agent_type)
                self.grid.position_agent(agent, (x, y))
                self.schedule.add(agent)

        self.running = True

    def step(self):
        '''
        Run one step of the model. If All agents are happy, halt the model.
        '''
        self.infected_count = 0  # Reset counter of infected agents
        self.agent_count = self.schedule.get_agent_count()
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

        # run until all agents are infected
        #if self.infected_count == self.schedule.get_agent_count():
        if self.infected_count == self.agent_count:
            self.running = False
