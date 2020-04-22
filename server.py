from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter

from model import Virus, VirusModelAgent, HouseAgent


class InfectiousElement(TextElement):
    '''
    Display the percentage infectious agents on visualization web page
    '''

    def __init__(self):
        pass

    def render(self, model):
        return "Percent infectious agents: " + str(round((model.infectious_percent * 100), 2))
        # rounds displayed percentage to 2 decimal places


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


infectious_element = InfectiousElement()
canvas_element = CanvasGrid(virus_draw, 20, 20, 500, 500)
infectious_chart = ChartModule([{"Label": "infectious_percent", "Color": "Black"}])

model_params = {
    "height": 20,
    "width": 20,
    #"density": UserSettableParameter("slider", "Agent density", 0.3, 0.1, 1.0, 0.1)
    "num_agents": UserSettableParameter("slider", "Number of Agents", 25, 1, 100, 5),
    # 0.3 = hardcoded starting density, options from 0.1 to 1.0 with steps of 0.1
    "infectious_seed_pc": UserSettableParameter("slider", "Initial fraction infectious", 0.05, 0.00, 1.0, 0.01),
}

server = ModularServer(Virus,
                       [canvas_element, infectious_element, infectious_chart],
                       "Virus test", model_params)
