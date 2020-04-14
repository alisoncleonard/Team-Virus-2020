# to run with model, run, and server files, use terminal command $ mesa runserver
import random
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
#import distributions

LENGTH_OF_DISEASE = 14 #days
INCUBATION_PERIOD = 5 #days

class VirusModelAgent(Agent):
    '''
    Agent in virus model. Each agent is an individual person.
    '''
    def __init__(self, pos, model, agent_compartment, risk_group):
        '''
         Create a new VirusModel agent.
         Args:
            unique_id: Unique identifier for the agent.
            x, y: Agent initial location.
            compartment: String indicating the agent's compartment
                        (susceptible, exposed, infectious_symptomatic,
                        infectious_asymptomatic, recovered, dead)
            risk_group: Low (younger, healthy) or high (older, immunocompromised)
            infection_timeline: days since infected (includes non-infectious period)
        '''
        super().__init__(pos, model)
        self.pos = pos
        self.compartment = agent_compartment
        self.risk_group = risk_group
        self.infection_timeline = 0

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False,
            include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def step(self):  # step function
        if self.compartment == "susceptible":
            self.model.susceptible_count += 1
        if self.compartment != "dead":
            self.move() # calls move method first before checking status of neighbors

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
                    if "infectious" in neighbor.compartment: # includes both infectious_symptomatic and infectious_asymptomatic
                        self.compartment = self.getsInfected(neighbor)
            elif self.compartment == "exposed":
                self.infection_timeline += 1 # adds day to infection time
                if self.infection_timeline > INCUBATION_PERIOD:
                    self.compartment = self.getsSymptoms()
            elif "infectious" in self.compartment: # includes both infectious_symptomatic and infectious_asymptomatic
                self.infection_timeline += 1 # adds day to infection time
                self.model.infectious_count += 1 # updates count of infectious agents
                self.model.infectious_percent = self.model.infectious_count / self.model.agent_count # updates percentage of infectious agents
                if self.infection_timeline > LENGTH_OF_DISEASE:
                    self.compartment = self.getsDead()
        else: # self.compartment == dead
            self.model.dead_count += 1 #updates count of dead agents

    def getsInfected(self, neighbor):
        '''
        Determines if, given the neighbor's infectious state, the agent gets infected
        '''
        if neighbor.compartment == "infectious_symptomatic":
            transmissionProb = 0.9
        else: #neighbor.compartment == "infectious_asymptomatic"
            transmissionProb = 0.5
        updatedCompartment = random.choices(["susceptible", "exposed"],
                                            [(1.0 - transmissionProb), transmissionProb])[0]
        return updatedCompartment

    def getsSymptoms(self):
        '''
        Determines if the agent becomes symptomatic or asymptomatic infectious
        '''
        symptomaticProb = 0.85
        updatedCompartment = random.choices(["infectious_asymptomatic", "infectious_symptomatic"],
                                            [(1.0 - symptomaticProb), symptomaticProb])[0]
        return updatedCompartment

    def getsDead(self):
        '''
        Determines if, given agent's risk group, the agent dies
        '''
        if self.risk_group == "high":
            deathProb = 0.30
        else: #self.risk_group == "low"
            deathProb = 0.01
        updatedCompartment = random.choices(["recovered", "dead"],
                                            [(1.0 - deathProb), deathProb])[0]
        return updatedCompartment

class Virus(Model):
    '''
    Model class for the Virus model.
    '''

    def __init__(self, height=20, width=20, density=0.3, infectious_seed_pc=0.05, high_risk_pc=0.25):
        # model is seeded with default parameters for density and infectious seed percent
        # can also change defaults with user settable parameter slider in GUI
        '''
        '''

        self.height = height # height and width of grid
        self.width = width
        self.density = density # density of agents in grid space
        self.infectious_seed_pc = infectious_seed_pc # percent of infectious agents at start of simulation
        self.high_risk_pc = high_risk_pc # percent of agents catergorized as high risk for severe disease

        self.schedule = RandomActivation(self) # controls the order that agents are activated and step
        self.grid = MultiGrid(width, height, torus=True) # multiple agents per cell

#        neighbors = []
#        x, y = self.pos
#        for dx in [-1, 0, 1]:
#            for dy in [-1, 0, 1]:
#                neighbors.append((x+dx, y+dy))

        self.infectious_count = 0
        self.infectious_percent = 0
        self.dead_count = 0
        self.susceptible_count = 0

        self.agent_count = 1 # to avoid divide by 0 error

        # uses DataCollector built in module to collect data from each model run
        self.datacollector = DataCollector(
                {"infectious_count": "infectious_count"},
                {"x": lambda m: m.pos[0], "y": lambda m: m.pos[1]})

        # Set up agents
        # We use a grid iterator that returns
        # the coordinates of a cell as well as
        # its contents. (coord_iter)
        for cell in self.grid.coord_iter():
            x = cell[1]
            y = cell[2]
            if self.random.random() < self.density:

                if self.random.random() < self.high_risk_pc:
                    risk_group = "high"
                else:
                    risk_group = "low"

                if self.random.random() < self.infectious_seed_pc:
                    agent_compartment = random.choices(["infectious_asymptomatic", "infectious_symptomatic"],
                                                        [0.15, 0.85])[0]
                else:
                    agent_compartment = "susceptible"

                agent = VirusModelAgent((x, y), self, agent_compartment, risk_group)
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)

        self.running = True


    def step(self):
        '''
        Run one step of the model. If all agents are happy, halt the model.
        '''
        self.infectious_count = 0  # Reset counters each step
        self.infectious_percent = 0
        self.dead_count = 0
        self.susceptible_count = 0
        self.agent_count = self.schedule.get_agent_count()
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

        # run until no more agents are infectious
        if self.infectious_count == 0:
            self.running = False
