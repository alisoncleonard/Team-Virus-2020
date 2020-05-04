# to run with model, run, and server files, use terminal command $ mesa runserver
import random
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
import scipy.stats
import numpy as np
import math
from mesa.batchrunner import BatchRunner
import itertools
import pandas as pd

# Assumptions of model, from Joshua Weitz
EXPOSED_PERIOD = 4 #days
ASYMPTOMATIC_PERIOD = 6 #days
SYMPTOMATIC_PERIOD = 10 #days
FRACTION_SYMPTOMATIC = 0.1
FRACTION_HI_RISK = 0.25
INFECTIOUS_PREVALENCE = 0.01
LOW_RISK_ASYMP_TRANSMISSION = 0.25 #agent is low-risk, infectious neighbor is asymptomatic
HI_RISK_ASYMP_TRANSMISSION = 0.35 #agent is high-risk, infectious neighbor is asymptomatic
LOW_RISK_SYMP_TRANSMISSION = 0.5 #agent is low-risk, infectious neighbor is symptomatic
HI_RISK_SYMP_TRANSMISSION = 0.7 #agent is high-risk, infectious neighbor is symptomatic

# Other assumptions of model, based on CO state stats
HI_RISK_DEATH_RATE = 0.15
LOW_RISK_DEATH_RATE = 0.01

GRID_HEIGHT = 20
GRID_WIDTH = 20

def track_params(model):
    return (model.infectious_seed_pc,
            model.recovered_seed_pc,
            model.high_risk_pc)

def track_run(model):
    return model.uid


class VirusModelAgent(Agent):
    '''
    Agent in virus model. Each agent is an individual person.
    '''
    def __init__(self, pos, model, agent_compartment, risk_group, unique_id):

        '''
         Create a new VirusModel agent.
         Args:
            unique_id: Unique identifier for the agent.
            x, y: Agent initial location.
            compartment: String indicating the agent's compartment
                        (susceptible, exposed, infectious_symptomatic,
                        infectious_asymptomatic, recovered, dead)
            risk_group: low (younger, healthy) or high (older, immunocompromised)
            infection_timeline: days since infected (includes non-infectious period)
        '''
        super().__init__(unique_id, model) # calling the agent class ___init___, inputs (unique_id, model)
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
        self.pos = new_position

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
                self.model.exposed_count += 1
                self.infection_timeline += 1 # adds day to infection time
                self.compartment = self.getsSymptoms()
            elif "infectious" in self.compartment: # includes both infectious_symptomatic and infectious_asymptomatic
                self.infection_timeline += 1 # adds day to infection time
                self.model.infectious_count += 1 # updates count of infectious agents
                #self.model.infectious_percent = self.model.infectious_count / self.model.agent_count # updates percentage of infectious agents
                self.compartment = self.getsDead()
                if self.compartment == "recovered":
                    self.model.recovered_count += 1
        else: # self.compartment == dead
            self.model.dead_count += 1 #updates count of dead agents

    def getsInfected(self, neighbor):
        '''
        Determines if, given the neighbor's infectious state, the agent gets infected
        '''
        if neighbor.compartment == "infectious_symptomatic":
            if self.risk_group == "high":
                transmissionProb = HI_RISK_SYMP_TRANSMISSION
            else: #self.risk_group == "low"
                transmissionProb = LOW_RISK_SYMP_TRANSMISSION
        else: #neighbor.compartment == "infectious_asymptomatic"
            if self.risk_group == "high":
                transmissionProb = HI_RISK_ASYMP_TRANSMISSION
            else: #self.risk_group == "low"
                transmissionProb = LOW_RISK_ASYMP_TRANSMISSION
        updatedCompartment = random.choices(["susceptible", "exposed"],
                                            [(1.0 - transmissionProb), transmissionProb])[0]
        return updatedCompartment

    def getsSymptoms(self):
        '''
        Determines if the agent becomes symptomatic or asymptomatic infectious
        '''
        # Calculates CDF of seeing agent's infection timeline given
        # mean exposure of EXPOSED_PERIOD days with standard deviation of 1 day
        symptomaticProb = scipy.stats.norm.cdf(self.infection_timeline, EXPOSED_PERIOD, 1)
        # Using calculated probability, pulls updated compartment status from
        # Bernoulli distribution
        updatedCompartment = random.choices(["infectious_asymptomatic", "infectious_symptomatic"],
                                            [(1.0 - symptomaticProb), symptomaticProb])[0]
        return updatedCompartment

    def getsDead(self):
        '''
        Determines if, given agent's risk group, the agent dies
        '''
        if self.compartment == "infectious_symptomatic":
            switchCompProb = scipy.stats.norm.cdf(self.infection_timeline, SYMPTOMATIC_PERIOD, 1)
            switchComp = random.choices(["switch", "infectious_symptomatic"],
                                        [switchCompProb, (1.0 - switchCompProb)])[0]
            if switchComp != "switch":
                return switchComp
            else:
                if self.risk_group == "high":
                    deathProb = HI_RISK_DEATH_RATE
                else: #self.risk_group == "low"
                    deathProb = LOW_RISK_DEATH_RATE
        else: #self.compartment == "infectious_asymptomatic"
            switchCompProb = scipy.stats.norm.cdf(self.infection_timeline, ASYMPTOMATIC_PERIOD, 1)
            switchComp = random.choices(["switch", "infectious_asymptomatic"],
                                        [switchCompProb, (1.0 - switchCompProb)])[0]
            if switchComp != "switch":
                return switchComp
            else:
                if self.risk_group == "high":
                    deathProb = HI_RISK_DEATH_RATE
                else: #self.risk_group == "low"
                    deathProb = LOW_RISK_DEATH_RATE
        updatedCompartment = random.choices(["recovered", "dead"],
                                            [(1.0 - deathProb), deathProb])[0]
        return updatedCompartment

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

    # id generator to track run numner in batch run data
    id_gen = itertools.count(1)

    def __init__(self, height=GRID_HEIGHT, width=GRID_WIDTH,
                num_agents=100, infectious_seed_pc=INFECTIOUS_PREVALENCE,
                recovered_seed_pc=0.2, high_risk_pc=FRACTION_HI_RISK,
                house_init="Random"):
        # model is seeded with default parameters for infectious seed and high-risk percent
        # can also change defaults with user settable parameter slider in GUI

        self.uid = next(self.id_gen)
        self.height = height # height and width of grid
        self.width = width
        self.num_agents = num_agents # number of agents to initializse
        self.infectious_seed_pc = infectious_seed_pc # percent of infectious agents at start of simulation
        self.recovered_seed_pc = recovered_seed_pc # percent of recovered agents at start of simulation
        self.high_risk_pc = high_risk_pc # percent of agents catergorized as high risk for severe disease

        self.schedule = RandomActivation(self) # controls the order that agents are activated and step
        self.grid = MultiGrid(width, height, torus=True) # multiple agents per cell

        self.infectious_count = 0
        self.infectious_percent = 0
        self.dead_count = 0
        self.susceptible_count = 0
        self.exposed_count = 0
        self.recovered_count = 0
        self.step_count = 0

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

        # For uniform neighborhood, approximate with square packing of circles
        # in a rectangle
        # Getting indices of where houses should be
        # Initialing array of tuples with random grid coordinates
        num_houses = len(agents_per_cell)
        house_locations = []
        if house_init == "Neighborhood":
            grid_area = self.grid.width * self.grid.height
            circle_radius = math.sqrt(grid_area / (4.0 * num_houses))
            circle_diameter = 2.0 * circle_radius
            floor_radius = math.floor(circle_radius)
            floor_diameter = math.floor(circle_diameter)
            # number of houses for each row of grid
            num_each_row = 1 + math.floor((self.grid.width - floor_radius) / floor_diameter)
            # number of houses for each column of grid
            num_each_col = 1 + math.floor((self.grid.height - floor_radius) / floor_diameter)
            for j in range(num_each_col):
                for i in range(num_each_row):
                    house_locations.append((floor_radius + i * floor_diameter, floor_radius + j * floor_diameter))

        # Initializing different household styles
        # Neighborhood = households laid out in uniform pattern on grid
        # Rural = households widely spread out
        # Clusters = households grouped in two clusters with larger space in between
        cell_counter = 0
        for cell in agents_per_cell:
            if house_init == "Random":
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
            elif house_init == "Neighborhood":
                x = house_locations[cell_counter][0]
                y = house_locations[cell_counter][1]
                cell_counter += 1
            else: #house_init == "Clusters"
                # Households will be created on first 9th and last 9th
                # of grid (torus wrap turned off)
                one_sixth_width = int(self.grid.width / 6)
                x_low = self.random.randrange(one_sixth_width, 2*one_sixth_width)
                x_high = self.random.randrange(4*one_sixth_width, 5*one_sixth_width)
                x = random.choice([x_low, x_high])
                one_sixth_height = int(self.grid.height / 6)
                y_low = self.random.randrange(one_sixth_height, 2*one_sixth_height)
                y_high = self.random.randrange(4*one_sixth_height, 5*one_sixth_height)
                y = random.choice([y_low, y_high])

            house = HouseAgent((x,y), self, house_id)
            self.grid.place_agent(house, (x, y))
            self.schedule.add(house)
            house_id+=1

            for person in range(cell):
                if self.random.random() < self.high_risk_pc:
                    risk_group = "high"
                else:
                    risk_group = "low"

                if self.random.random() < self.infectious_seed_pc:
                    # From Joshua Weitz paper
                    # Basic epi parameters, 0.1% total prevalence
                    # (90% asymptomatic, 10% symptomatic)
                    agent_compartment = random.choices(["infectious_asymptomatic", "infectious_symptomatic"],
                                                        [(1.0 - FRACTION_SYMPTOMATIC), FRACTION_SYMPTOMATIC])[0]
                    self.infectious_count += 1

                elif self.random.random() < self.recovered_seed_pc:
                    agent_compartment = "recovered"
                    self.recovered_count += 1

                else:
                    agent_compartment = "susceptible"
                    self.susceptible_count += 1

                agent = VirusModelAgent((x, y), self, agent_compartment, risk_group, person_id)
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)
                person_id += 1

        self.datacollector = DataCollector(model_reporters={
                             "Step": "step_count",
                             "Susceptible": "susceptible_count",
                             "Exposed": "exposed_count",
                             "Infectious": "infectious_count",
                             "Recovered": "recovered_count",
                             "Dead": "dead_count",
                             "Model Params": track_params,
                             "Run": track_run})
        self.datacollector.collect(self)

        self.running = True


    def step(self):
        '''
        Run one step of the model. If all agents are happy, halt the model.
        '''
        self.infectious_count = 0  # Reset counters each step
        #self.infectious_percent = 0
        self.dead_count = 0
        self.susceptible_count = 0
        self.exposed_count = 0
        self.schedule.step()
        self.step_count += 1
        # collect data
        self.datacollector.collect(self)

        # run until no more agents are infectious
        # if self.infectious_count == 0 and self.exposed_count ==0:
        #     self.running = False


# code for batch runs

# parameter lists for each parameter to be tested in batch run
# BatchRunner runs every combination of parameters listed in br_params
br_params = {"infectious_seed_pc": [0.01, 0.05, 0.1],
             "recovered_seed_pc": [0.05, 0.1, 0.15, 0.2],
             "high_risk_pc": [0.1, 0.2]}

br = BatchRunner(Virus,
                 br_params,
                 iterations=1, # number of times to run each parameter combination
                 max_steps=50, # number of steps for each model run, unless conditions are met
                 model_reporters={"Data Collector": lambda m: m.datacollector})

if __name__ == '__main__':
    br.run_all()
    br_df = br.get_model_vars_dataframe()
    br_step_data = pd.DataFrame()
    for i in range(len(br_df["Data Collector"])):
        if isinstance(br_df["Data Collector"][i], DataCollector):
            i_run_data = br_df["Data Collector"][i].get_model_vars_dataframe()
            br_step_data = br_step_data.append(i_run_data, ignore_index=True)
    br_step_data.to_csv("VirusModel_Step_Data.csv")
