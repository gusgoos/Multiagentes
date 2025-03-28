from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import json

#Parameters for simulation
GRID_LENGTH = 64
GRID_HEIGHT = 64
FRAMERATE = 8
TIME_LIMIT = 90
NUM_STEPS = FRAMERATE * TIME_LIMIT


class lightAgent(Agent):
    def __init__(self, unique_id, model, color):
        super().__init__(unique_id, model)
        self.color = color
        self.unique_id = unique_id
        self.timer = 0
        self.lightSchedule = {
            0: [1, 2, 2, 2],
            20: [2, 1, 2, 2],
            40: [2, 2, 1, 2],
            60: [2, 2, 2, 1],
            80: [2, 2, 2, 2]  #Reset timer at 80
        }
    def step(self):
        if self.timer in self.lightSchedule:
            self.color = self.lightSchedule[self.timer][self.unique_id - 1]
        self.timer += 1
        #Reset timer at 80
        if self.timer > 80:
            self.timer = 0


#Car agent
class carAgent(Agent):
    def __init__(self, unique_id, model, type, big_lane, startingPosition, targetPosition, lane):
        super().__init__(unique_id, model)
        self.type=type
        self.startingPosition = startingPosition  # 1 to 4: left, top, right, bottom
        self.targetPosition = targetPosition  # (X, Y) coordinate
        self.lane = lane
        self.big_lane = big_lane
        self.direccion = None

    # Step function
    def step(self):
        currentX, currentY = self.pos
        targetX, targetY = self.targetPosition

        if (currentX,currentY) == (0,0):
            return

        if self.big_lane == 1:
            light = self.model.grid.get_cell_list_contents((2,2))[0]
            if ((self.lane == 1 or self.lane == 2) and light.color == 1) or currentX >= 29 or currentX < 28:
                if currentX < targetX:
                    if currentX < 28:
                      cell_agentes = model.grid.get_cell_list_contents((currentX + 2, currentY))
                      if len(cell_agentes) == 0:
                        self.model.grid.move_agent(self, (currentX + 1, currentY))
                        self.direccion = "derecha"
                    else:
                      self.model.grid.move_agent(self, (currentX + 1, currentY))
                      self.direccion = "derecha"
                else:
                    if currentY > targetY:
                      self.model.grid.move_agent(self, (currentX, currentY - 1))
                      self.direccion = "arriba"

            if self.lane == 3:
                if currentX < targetX:
                    self.model.grid.move_agent(self, (currentX + 1, currentY))
                    self.direccion = "derecha"
                else:
                    if currentY < targetY:
                        self.model.grid.move_agent(self, (currentX, currentY + 1))
                        self.direccion = "abajo"

        if self.big_lane == 3:
            light = self.model.grid.get_cell_list_contents((1,3))[0]
            if ((self.lane == 1 or self.lane == 2) and light.color == 1) or currentX <= 34 or currentX > 35:
                if currentX > targetX:
                  if currentX > 35:
                    cell_agentes = model.grid.get_cell_list_contents((currentX - 2, currentY))
                    if len(cell_agentes) == 0:
                      self.model.grid.move_agent(self, (currentX - 1, currentY))
                      self.direccion = "izquierda"
                  else:
                    self.model.grid.move_agent(self, (currentX - 1, currentY))
                    self.direccion = "izquierda"
                else:
                    if currentY < targetY:
                          self.model.grid.move_agent(self, (currentX, currentY + 1))
                          self.direccion = "abajo"

            if self.lane == 3:
                if currentX > targetX:
                    self.model.grid.move_agent(self, (currentX - 1, currentY))
                    self.direccion = "izquierda"
                else:
                    if currentY > targetY:
                        self.model.grid.move_agent(self, (currentX, currentY - 1))
                        self.direccion = "arriba"

        if self.big_lane == 2:
            light = self.model.grid.get_cell_list_contents((2,4))[0]
            if ((self.lane == 1 or self.lane == 2) and light.color == 1) or currentY <= 34 or currentY > 35:
                if currentY > targetY:
                  if currentY > 35:
                    cell_agentes = model.grid.get_cell_list_contents((currentX, currentY - 2))
                    if len(cell_agentes) == 0:
                      self.model.grid.move_agent(self, (currentX, currentY - 1))
                      self.direccion = "abajo"
                  else:
                    self.model.grid.move_agent(self, (currentX, currentY - 1))
                    self.direccion = "abajo"
                else:
                    if currentX > targetX:
                          self.model.grid.move_agent(self, (currentX - 1, currentY))
                          self.direccion = "derecha"

            if self.lane == 3:
                if currentY > targetY:
                    self.model.grid.move_agent(self, (currentX, currentY - 1))
                else:
                    if currentX < targetX:
                        self.model.grid.move_agent(self, (currentX + 1, currentY))

        if self.big_lane == 4:
            light = self.model.grid.get_cell_list_contents((3,3))[0]
            if ((self.lane == 1 or self.lane == 2) and light.color == 1) or currentY >= 29 or currentY < 28:
                if currentY < targetY:
                  if currentY < 28:
                    cell_agentes = model.grid.get_cell_list_contents((currentX, currentY + 2))
                    if len(cell_agentes) == 0:
                      self.model.grid.move_agent(self, (currentX, currentY + 1))
                  else:
                    self.model.grid.move_agent(self, (currentX, currentY + 1))
                else:
                    if currentX < targetX:
                        self.model.grid.move_agent(self, (currentX + 1, currentY))

            if self.lane == 3:
                if currentY < targetY:
                    self.model.grid.move_agent(self, (currentX, currentY + 1))
                else:
                    if currentX > targetX:
                        self.model.grid.move_agent(self, (currentX - 1, currentY))

        if (currentX, currentY) == self.targetPosition:
            self.model.grid.move_agent(self, (0,0))
            

#Get grid for visualization
def get_grid(model):
    grid = np.full((model.grid.width, model.grid.height, 3), (255, 255, 255), dtype=np.uint8)
    
    #Street Coloring
    for x in range(29, 35):
        for y in range(0, 64):
            grid[x][y] = (128, 128, 128)  # Gray color
    for x in range(0, 64):
        for y in range(29, 35):
            grid[x][y] = (128, 128, 128)  # Gray color


    for cell in model.grid.coord_iter():
        cell_agents, pos = cell
        if cell_agents:
            #List all agents to visualize
            allCarAgents = [agent for agent in cell_agents if isinstance(agent, carAgent)]
            allLightAgents = [agent for agent in cell_agents if isinstance(agent, lightAgent)]
    
            if allCarAgents:
                # Assign colors based on each car agent's type attribute
                for agent in allCarAgents:
                    carType = agent.type
                    color = get_color_for_car_type(carType)
                    grid[pos[1]][pos[0]] = color
                    if color is not None:
                        grid[pos[1]][pos[0]] = color
            if allLightAgents:
                # Assign colors based on each light agent's color attribute
                for agent in allLightAgents:
                    lightColor = agent.color
                    color = get_color_for_light_color(lightColor)
                    if color is not None:
                        grid[pos[1]][pos[0]] = color
        (128,126,120)
                        
    return grid

def get_color_for_light_color(lightColor):
    light_color_mapping = {
        1: (0, 255, 0),    # Green
        2: (255, 0, 0),    # Red
    }
    return light_color_mapping[lightColor]

def get_color_for_car_type(carType):
    color_mapping = {
        0: (0, 0, 0),        # Black
        1: (255, 0, 0),      # Red
        2: (0, 0, 255),      # Blue
        3: (255, 255, 0),    # Yellow
        4: (128, 0, 128),    # Purple
        5: (255, 165, 0)     # Orange
    }
    # Return the color type (or black if it's not defined)
    return color_mapping.get(carType, (0, 0, 0))

#trafficModel
class trafficModel(Model):
    def __init__(self, length, height):
        self.grid = MultiGrid(length, height, torus=True)
        self.schedule = SimultaneousActivation(self)
        self.cars = 0
        
        #Place light Agents
        a = lightAgent(1, self, 1)
        self.grid.place_agent(a, (2, 2))
        self.schedule.add(a)
        b = lightAgent(2, self, 2)
        self.grid.place_agent(b, (1, 3))
        self.schedule.add(b)
        c = lightAgent(3, self, 2)
        self.grid.place_agent(c, (2, 4))
        self.schedule.add(c)
        d = lightAgent(4, self, 2)
        self.grid.place_agent(d, (3, 3))
        self.schedule.add(d)

        lane = 1
        id = 100
        while lane <= 4:
            randomized_cars = np.random.randint(0,28)
            self.cars = self.cars + randomized_cars
            if lane == 1:
                x_lane1 = 0
                x_lane2 = 0
                x_lane3 = 0
                for x in  range(randomized_cars):
                    randomized_inner_lane = np.random.randint(1,4)
                    if randomized_inner_lane == 1:
                        a = carAgent(id, self, np.random.randint(1,6), 1, (x_lane1, 32), (32,0), randomized_inner_lane)
                        self.grid.place_agent(a, (x_lane1, 32))
                        self.schedule.add(a)
                        x_lane1 += 2
                        id += 1
                    elif randomized_inner_lane == 2:
                        a = carAgent(id, self, np.random.randint(1,6), 1, (x_lane2, 33), (63,33), randomized_inner_lane)
                        self.grid.place_agent(a, (x_lane2, 33))
                        self.schedule.add(a)
                        x_lane2 += 2
                        id += 1
                    elif randomized_inner_lane == 3:
                        a = carAgent(id, self, np.random.randint(1,6), 1, (x_lane3, 34), (29,63), randomized_inner_lane)
                        self.grid.place_agent(a, (x_lane3, 34))
                        self.schedule.add(a)
                        x_lane3 += 2
                        id += 1
            elif lane == 2:
                y_lane1 = 63
                y_lane2 = 63
                y_lane3 = 63
                for x in  range(randomized_cars):
                    randomized_inner_lane = np.random.randint(1,4)
                    if randomized_inner_lane == 1:
                        a = carAgent(id, self, np.random.randint(1,6), 2, (32, y_lane1), (0,31), randomized_inner_lane)
                        self.grid.place_agent(a, (32, y_lane1))
                        self.schedule.add(a)
                        y_lane1 -= 2
                        id += 1
                    elif randomized_inner_lane == 2:
                        a = carAgent(id, self, np.random.randint(1,6), 2, (33, y_lane2), (33,0), randomized_inner_lane)
                        self.grid.place_agent(a, (33, y_lane2))
                        self.schedule.add(a)
                        y_lane2 -= 2
                        id += 1
                    elif randomized_inner_lane == 3:
                        a = carAgent(id, self, np.random.randint(1,6), 2, (34, y_lane3), (63,34), randomized_inner_lane)
                        self.grid.place_agent(a, (34, y_lane3))
                        self.schedule.add(a)
                        y_lane3 -= 2
                        id += 1
            elif lane == 3:
                x_lane1 = 63
                x_lane2 = 63
                x_lane3 = 63
                for x in  range(randomized_cars):
                    randomized_inner_lane = np.random.randint(1,4)
                    if randomized_inner_lane == 1:
                        a = carAgent(id, self, np.random.randint(1,6), 3, (x_lane1, 31), (31, 63), randomized_inner_lane)
                        self.grid.place_agent(a, (x_lane1, 31))
                        self.schedule.add(a)
                        x_lane1 -= 2
                        id += 1
                    elif randomized_inner_lane == 2:
                        a = carAgent(id, self, np.random.randint(1,6), 3, (x_lane2, 30), (0, 30), randomized_inner_lane)
                        self.grid.place_agent(a, (x_lane2, 30))
                        self.schedule.add(a)
                        x_lane2 -= 2
                        id += 1
                    elif randomized_inner_lane == 3:
                        a = carAgent(id, self, np.random.randint(1,6), 3, (x_lane3, 29), (34, 0), randomized_inner_lane)
                        self.grid.place_agent(a, (x_lane3, 29))
                        self.schedule.add(a)
                        x_lane3 -= 2
                        id += 1
            elif lane == 4:
                y_lane1 = 0
                y_lane2 = 0
                y_lane3 = 0
                for x in  range(randomized_cars):
                    randomized_inner_lane = np.random.randint(1,4)
                    if randomized_inner_lane == 1:
                        a = carAgent(id, self, np.random.randint(1,6), 4, (31, y_lane1), (63, 32), randomized_inner_lane)
                        self.grid.place_agent(a, (31, y_lane1))
                        self.schedule.add(a)
                        y_lane1 += 2
                        id += 1
                    elif randomized_inner_lane == 2:
                        a = carAgent(id, self, np.random.randint(1,6), 4, (30, y_lane2), (30, 63), randomized_inner_lane)
                        self.grid.place_agent(a, (30, y_lane2))
                        self.schedule.add(a)
                        y_lane2 += 2
                        id += 1
                    elif randomized_inner_lane == 3:
                        a = carAgent(id, self, np.random.randint(1,6), 4, (29, y_lane3), (0, 29), randomized_inner_lane)
                        self.grid.place_agent(a, (29, y_lane3))
                        self.schedule.add(a)
                        y_lane3 += 2
                        id += 1
            lane += 1
        

        # Start data collector
        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid})
    
    def getAgentPositions(self):
        agent_positions = []
        for agent in self.schedule.agents:
            if isinstance(agent, carAgent):
                agent_positions.append({
                    "unique_id": agent.unique_id,
                    "position": {
                        "x": agent.pos[0],
                        "y": agent.pos[1]
                    }
                })
        return agent_positions
    
    def finish(self):
        cars = model.grid.get_cell_list_contents((0,0))
        if len(cars) == self.cars:
            return True
                     
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

def grafica(model):
    last_frame = 0
    for i in range(NUM_STEPS):
        model.step()
        last_frame += 1
        finish = model.finish()
        if finish:
            break
    return last_frame

 #Calculate the max number of steps
model = trafficModel(GRID_LENGTH, GRID_HEIGHT) 

 #Start model
step_data = []
last_frame = 0

for i in range(NUM_STEPS):
    # Collect agent positions at each step
    agent_positions = model.getAgentPositions()
    step_data.append({
        "step": i,
        "agents": agent_positions
    })
    finish = model.finish()
    model.step()
    last_frame += 1
    if finish:
        break
    
elapsedTime = last_frame + 1 / FRAMERATE
print(f"Simulation over in {elapsedTime:.2f} seconds")
#print(step_data)


#Collect data
all_grid = model.datacollector.get_model_vars_dataframe() 

 #Plot the data
fig, axs = plt.subplots(figsize=(10, 5))
axs.set_xticks([])
axs.set_yticks([])
patch = plt.imshow(all_grid.iloc[0][0])

def animate(i):
    model.step()  # Make sure to update the model state
    patch.set_data(all_grid.iloc[i][0]) 

 #Variable to assign the animation framerate
calculatedInterval = 1000 / FRAMERATE 
anim = animation.FuncAnimation(fig, animate, frames=len(all_grid), interval=calculatedInterval)
plt.show()
anim
 
try:
    with open('agent_positions.json', 'w') as json_file:
        json.dump(step_data, json_file)
    print("Data successfully saved to agent_positions.json")
except Exception as e:
    print("Error saving data:", str(e)) 