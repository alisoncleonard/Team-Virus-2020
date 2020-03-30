from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter

from model import Virus


class InfectedElement(TextElement):
    '''
    Display the percentage infected agents.
    '''

    def __init__(self):
        pass

    def render(self, model):
        return "Percent infected agents: " + str(model.infected_percent * 100)


def virus_draw(agent):
    '''
    Portrayal Method for canvas
    '''
    if agent is None:
        return
    portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0}

    if agent.type == 0:
        portrayal["Color"] = ["#FF0000", "#FF9999"]
        portrayal["stroke_color"] = "#00FF00"
    else:
        portrayal["Color"] = ["#0000FF", "#9999FF"]
        portrayal["stroke_color"] = "#000000"
    return portrayal


infected_element = InfectedElement()
canvas_element = CanvasGrid(virus_draw, 20, 20, 500, 500)
infected_chart = ChartModule([{"Label": "infected_percent", "Color": "Black"}])

model_params = {
    "height": 20,
    "width": 20,
    "density": UserSettableParameter("slider", "Agent density", 0.3, 0.1, 1.0, 0.1),
    "infected_seed_pc": UserSettableParameter("slider", "Initial fraction infected", 0.05, 0.00, 1.0, 0.01),
}

server = ModularServer(Virus,
                       [canvas_element, infected_element, infected_chart],
                       "Virus test", model_params)
