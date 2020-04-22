# to run with model, run, and server files, use terminal command $ mesa runserver

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
import numpy as np
import random

LENGTH_OF_DISEASE = 14 #days
INCUBATION_PERIOD = 5 #days

class VirusModelAgent(Agent):
    '''
    Agent in virus model. Each agent is an individual person.
    '''
    def __init__(self, pos, model, agent_compartment, unique_id):
        '''
         Create a new VirusModel agent.
         Args:
            unique_id: Unique identifier for the agent.
            x, y: Agent initial location.
            agent_type: String indicating the agent's compartment (susceptible, exposed, infectious, recovered)
        '''
        super().__init__(unique_id, model) # calling the agent class ___init___, inputs (unique_id, model)
        self.pos = pos
        self.compartment = agent_compartment
        self.infection_timeline = 0

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False,
            include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
        self.pos = new_position

    def step(self):  # step function
        self.move() # calls move method first before checking status of neighbors

        # Built-in get_neighbors function returns a list of neighbors.
        # Two types of cell neighborhoods: Moore (including diagonals), and
        # Von Neumann (only up/down/left/right).
        # Can include an argument as to whether to include the center cell itself as one of the neighbors.
        if self.compartment == "susceptible":
            neighbors = self.model.grid.get_neighbors(
                 self.pos,
                 moore=False, # uses Von Neumann neighborhoods
                 include_center=True) # KMB we think this is so you can infect people in the same cell
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

# Made houses agent for visualization
class HouseAgent(Agent):
    '''
    House cell in virus model. Each agent is an individual person.
    '''
    def __init__(self, pos, model, unique_id):
        '''
         Create a new HouseAgent agent.
         Args:
            unique_id: Unique identifier for the agent.
            x, y: Agent initial location.
            agent_type: String indicating the agent's compartment (susceptible, exposed, infectious, recovered)
        '''
        super().__init__(unique_id, model) # calling the agent class ___init___, inputs (unique_id, model)
        self.pos = pos
        self.compartment = "house"

class Virus(Model):
    '''
    Model class for the Virus model.
    '''

    def __init__(self, height=20, width=20, density = 0.3, num_agents=100, infectious_seed_pc=0.05):
        # model is seeded with default parameters for density and infectious seed percent
        # can also change defaults with user settable parameter slider in GUI
        '''
        '''

        self.height = height # height and width of grid
        self.width = width
        self.density = density
        self.num_agents = num_agents # number of agents to initializse
        self.infectious_seed_pc = infectious_seed_pc # percent of infectious agents at start of simulation

        self.schedule = RandomActivation(self) # controls the order that agents are activated and step
        self.grid = MultiGrid(width, height, torus=True) # multiple agents per cell

#        neighbors = []
#        x, y = self.pos
#        for dx in [-1, 0, 1]:
#            for dy in [-1, 0, 1]:
#                neighbors.append((x+dx, y+dy))

        self.infectious_count = 0
        self.infectious_percent = 0

        self.agent_count = 1 # to avoid divide by 0 error

        # uses DataCollector built in module to collect data from each model run
        self.datacollector = DataCollector(
            {"infectious_percent": "infectious_percent"},
            {"x": lambda m: m.pos[0], "y": lambda m: m.pos[1]})

        # Set up agents
        # First initialize vec defining number of agents per cell/house (between 1-4)
        agents_per_cell = []
        agents_sum = 0

        while agents_sum < (num_agents-4):
            agents_per_cell.append(random.randint(1,4))
            agents_sum = sum(agents_per_cell)

        while agents_sum != num_agents:
            temp = num_agents - agents_sum
            agents_per_cell.append(random.randint(1,temp))
            agents_sum = sum(agents_per_cell)

        # Now initialize these agents on the grid
        person_id = 0
        house_id = 2000

        for cell in agents_per_cell:
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            house = HouseAgent((x,y), self, house_id)
            self.grid.place_agent(house, (x, y))
            self.schedule.add(house)
            house_id+=1

            for person in range(cell):
                if self.random.random() < self.infectious_seed_pc:
                        agent_compartment = "infectious"
                else:
                        agent_compartment = "susceptible"

                agent = VirusModelAgent((x, y), self, agent_compartment, person_id)
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)
                person_id += 1

        #for person in range(self.num_agents):
            #x = 2*np.mod(person, 4)
            #y = 1
            ##x = self.random.randrange(self.grid.width)
            ##y = self.random.randrange(self.grid.height)

            #if self.random.random() < self.infectious_seed_pc:
            #        agent_compartment = "infectious"
            #else:
            #        agent_compartment = "susceptible"

            #agent = VirusModelAgent((x, y), self, agent_compartment, person)
            #self.grid.place_agent(agent, (x, y))
            #self.schedule.add(agent)

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
