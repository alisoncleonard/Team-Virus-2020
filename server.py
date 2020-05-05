from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter

from model import Virus, VirusModelAgent, HouseAgent
import model as md # to get global variables


class SusceptibleElement(TextElement):
    '''
    Display the number of susceptible agents on visualization web page
    '''

    def __init__(self):
        pass

    def render(self, model):
        return "Susceptible agents: " + str(model.susceptible_count)

class ExposedElement(TextElement):
    '''
    Display the number of exposed agents on visualization web page
    '''

    def __init__(self):
        pass

    def render(self, model):
        return "Exposed agents: " + str(model.exposed_count)

class InfectiousElement(TextElement):
    '''
    Display the total infectious agents on visualization web page
    '''

    def __init__(self):
        pass

    def render(self, model):
        return "Infectious agents: " + str(model.infectious_count)

class RecoveredElement(TextElement):
    '''
    Display the number of recovered agents on visualization web page
    '''

    def __init__(self):
        pass

    def render(self, model):
        return "Recovered agents: " + str(model.recovered_count)

class DeadElement(TextElement):
    '''
    Display the number of dead agents on visualization web page
    '''

    def __init__(self):
        pass

    def render(self, model):
        return "Total dead: " + str(model.dead_count)

class AgentCountElement(TextElement):
    '''
    Display the total number of agents on visualization web page
    '''

    def __init__(self):
        pass

    def render(self, model):
        return "Total agents: " + str(model.num_agents)

def virus_draw(agent):
    '''
    Portrayal Method for canvas. Let's to watch the model work in real time.
    '''
    if agent is None:
        return

    portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 1}

    if type(agent) is VirusModelAgent:

        if agent.risk_group == "high":
            portrayal["Shape"] = "rect"
            portrayal["w"] = 0.5
            portrayal["h"] = 0.5

        if agent.compartment == "infectious":
            portrayal["Color"] = ["#FD5956"] # jerking grapefruit
            portrayal["stroke_color"] = "#000000"
        elif agent.compartment == "exposed":
            portrayal["Color"] = ["#FDC1C5"] # scrubby pale rose
            portrayal["stroke_color"] = "#000000"
        elif agent.compartment == "recovered":
            portrayal["Color"] = ["#730039"] # in-service merlot
            portrayal["stroke_color"] = "#000000"
        elif agent.compartment == "dead":
            portrayal["Color"] = ["#070D0D"] # starving almost black
            portrayal["stroke_color"] = "#000000"
        else:
            portrayal["Color"] = ["#107AB0"] # farraginous nice blue
            portrayal["stroke_color"] = "#000000"

    elif type(agent) is HouseAgent:
        if agent.people_home == True:
            if agent.high_risk == False:
                portrayal["Color"] = ["#D3D3D3"] # light gray = low risk house
            else:
                portrayal["Color"] = ["#666666"] # gray = high risk house
        else:
            portrayal["Color"] = ["#FFFFFF"] # white
        portrayal["Shape"] = "rect"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal

ip = md.INFECTIOUS_PREVALENCE

susceptible_element = SusceptibleElement()
exposed_element = ExposedElement()
infectious_element = InfectiousElement()
recovered_element = RecoveredElement()
dead_element = DeadElement()
agent_count_element = AgentCountElement()

chart = ChartModule([{"Label": "Susceptible", "Color": "#107AB0"},
                     {"Label": "Exposed", "Color": "#FDC1C5"},
                     {"Label": "Infectious", "Color": "#FD5956"},
                     {"Label": "Recovered", "Color": "#730039"}],
                     data_collector_name='datacollector')

model_params = {
    "grid_area": UserSettableParameter("choice", "Grid Area", value="Demo", choices=["Demo", "Small", "Large"]),
    "num_agents": UserSettableParameter("slider", "Number of Agents", 100, 1, 1000, 5),
    "infectious_seed_pc": UserSettableParameter("slider", "Initial fraction infectious", ip, 0.00, 1.0, 0.01),
    "recovered_seed_pc": UserSettableParameter("slider", "Initial fraction recovered", 0.1, 0.00, 1.0, 0.01),
    "high_risk_pc": UserSettableParameter("slider", "Percentage high-risk agents", 0.25, 0.00, 1.0, 0.05),
    "release_strat": UserSettableParameter("choice", "Quarantine Release Strategy", value="Random individual houses",
                                        choices=["Everyone release", "Random group of houses", "Random individual houses", "Low risk individuals", "Low risk houses"]),
    "house_init": UserSettableParameter("choice", "Household Style", value="Random",
                                        choices=["Random", "Neighborhood", "Clusters"]),
    "mobility_speed": UserSettableParameter("choice", "Mobility", value = "low", choices = ["test", "low", "high"]),
    "weeks_to_second_release": UserSettableParameter("choice", "Weeks til second release", value = 4, choices = [2, 4, 6, 8])
    }

if model_params["grid_area"].value == "Demo":
    grid_height = md.GRID_HEIGHT_DEMO
    grid_width = md.GRID_WIDTH_DEMO
elif model_params["grid_area"].value == "Small":
    grid_height = md.GRID_HEIGHT_SMALL
    grid_width = md.GRID_WIDTH_SMALL
elif model_params["grid_area"].value == "Large":
    grid_height = md.GRID_HEIGHT_LARGE
    grid_width = md.GRID_WIDTH_LARGE

canvas_element = CanvasGrid(virus_draw, grid_height, grid_width, 500, 500)

server = ModularServer(Virus,
                       [canvas_element, agent_count_element,
                       susceptible_element, exposed_element,
                       infectious_element, recovered_element, dead_element,
                       chart],
                       "Team Virus: COVID-19", model_params)
