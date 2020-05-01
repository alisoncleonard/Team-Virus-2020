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
        portrayal["Color"] = ["#666666"] # gray
        portrayal["Shape"] = "rect"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal

susceptible_element = SusceptibleElement()
exposed_element = ExposedElement()
infectious_element = InfectiousElement()
recovered_element = RecoveredElement()
dead_element = DeadElement()
agent_count_element = AgentCountElement()
#canvas_element = CanvasGrid(virus_draw, 20, 20, 500, 500)
s_chart = ChartModule([{"Label": "susceptible", "Color": "#107AB0"}], data_collector_name='s_datacollector')
e_chart = ChartModule([{"Label": "exposed", "Color": "#FDC1C5"}], data_collector_name='e_datacollector')
i_chart = ChartModule([{"Label": "infectious", "Color": "#FD5956"}], data_collector_name='i_datacollector')
r_chart = ChartModule([{"Label": "recovered", "Color": "#730039"}], data_collector_name='r_datacollector')

ip = md.INFECTIOUS_PREVALENCE

model_params = {
    "height": UserSettableParameter("slider", "Height of Grid", 20, 10, 100, 5),
    "width": UserSettableParameter("slider", "Width of Grid", 20, 10, 100, 5),
    #"height": 20,
    #"width": 20,
    #"density": UserSettableParameter("slider", "Agent density", 0.3, 0.1, 1.0, 0.1)
    "num_agents": UserSettableParameter("slider", "Number of Agents", 100, 1, 1000, 5),
    "infectious_seed_pc": UserSettableParameter("slider", "Initial fraction infectious", ip, 0.00, 1.0, 0.01),
    "recovered_seed_pc": UserSettableParameter("slider", "Initial fraction recovered", 0.1, 0.00, 1.0, 0.01),
    "high_risk_pc": UserSettableParameter("slider", "Percentage high-risk agents", 0.25, 0.00, 1.0, 0.05),
    # "house_init": UserSettableParameter("choice", "Household Style", value="Random",
    #                                     choices=["Random", "Neighborhood", "Rural", "Clusters"]),
    "house_init": UserSettableParameter("choice", "Household Style", value="Random",
                                        choices=["Random", "Clusters"])
}

canvas_element = CanvasGrid(virus_draw, model_params["height"], model_params["width"], 500, 500)

server = ModularServer(Virus,
                       [canvas_element, agent_count_element,
                       susceptible_element, exposed_element,
                       infectious_element, recovered_element, dead_element,
                       s_chart, e_chart, i_chart, r_chart],
                       "Team Virus: COVID-19", model_params)
