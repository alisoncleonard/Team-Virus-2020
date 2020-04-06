# to run with model, run, and server files, use terminal command $ mesa runserver

# My test model only has 2 types: susceptible and infectious
# on each step, if any neighbors are infectious then you become infectious

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector

LENGTH_OF_DISEASE = 14 #days
INCUBATION_PERIOD = 5 #days

class VirusModelAgent(Agent):
    '''
    Agent in virus model. Each agent is an individual person.
    '''
    def __init__(self, pos, model, agent_compartment):
        '''
         Create a new VirusModel agent.
         Args:
            unique_id: Unique identifier for the agent.
            x, y: Agent initial location.
            agent_type: String indicating the agent's compartment (susceptible, exposed, infectious, recovered)
        '''
        super().__init__(pos, model)
        self.pos = pos
        self.compartment = agent_compartment
        self.infection_timeline = 0

    def step(self):  # step function
        # Built-in get_neighbors function returns a list of neighbors.
        # Two types of cell neighborhoods: Moore (including diagonals), and
        # Von Neumann (only up/down/left/right).
        # Can include an argument as to whether to include the center cell itself as one of the neighbors.
        if self.compartment == "susceptible":
            neighbors = self.model.grid.get_neighbors(
                 self.pos,
                 moore=False, # uses Von Neumann neighborhoods
                 include_center=False)
            for neighbor in neighbors:
                # if your neighbor is infectious, you become infectious
                if neighbor.compartment == "infectious":
                    self.compartment = "exposed"
        elif self.compartment == "exposed":
            self.infection_timeline += 1 # adds day to infection time
            if self.infection_timeline > INCUBATION_PERIOD:
                self.compartment = "infectious"
        elif self.compartment == "infectious":
            self.infection_timeline += 1 # adds day to infection time
            self.model.infectious_count += 1 # updates count of infectious agents
            self.model.infectious_percent = self.model.infectious_count / self.model.agent_count # updates percentage of infectious agents
            if self.infection_timeline > LENGTH_OF_DISEASE:
                self.compartment = "recovered"

class Virus(Model):
    '''
    Model class for the Virus model.
    '''

    def __init__(self, height=20, width=20, density=0.3, infectious_seed_pc=0.05):
        # model is seeded with default parameters for density and infectious seed percent
        # can also change defaults with user settable parameter slider in GUI
        '''
        '''

        self.height = height # height and width of grid
        self.width = width
        self.density = density # density of agents in grid space
        self.infectious_seed_pc = infectious_seed_pc # percent of infectious agents at start of simulation

        self.schedule = RandomActivation(self) # controls the order that agents are activated and step
        self.grid = SingleGrid(width, height, torus=True) # specify only one agent per cell
        # can use multigrid if we need multiple agents per cell

        self.infectious_count = 0
        self.infectious_percent = 0
        self.agent_count = 1 # to avoid divide by 0 error

        # uses DataCollector built in module to collect data from each model run
        self.datacollector = DataCollector(
            {"infectious_percent": "infectious_percent"},
            {"x": lambda m: m.pos[0], "y": lambda m: m.pos[1]})

        # Set up agents
        # We use a grid iterator that returns
        # the coordinates of a cell as well as
        # its contents. (coord_iter)
        for cell in self.grid.coord_iter():
            x = cell[1]
            y = cell[2]
            if self.random.random() < self.density:
                if self.random.random() < self.infectious_seed_pc:
                    agent_compartment = "infectious"
                else:
                    agent_compartment = "susceptible"

                agent = VirusModelAgent((x, y), self, agent_compartment)
                self.grid.position_agent(agent, (x, y))
                self.schedule.add(agent)

        self.running = True

    def step(self):
        '''
        Run one step of the model. If all agents are happy, halt the model.
        '''
        self.infectious_count = 0  # Reset counter of infectious agents
        self.infectious_percent = 0
        self.agent_count = self.schedule.get_agent_count()
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

        # run until all agents are infectious
        #if self.infectious_count == self.schedule.get_agent_count():
        if self.infectious_count == self.agent_count:
            self.running = False
