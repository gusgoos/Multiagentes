from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd

#Parameters for simulation
GRID_LENGTH = 64
GRID_HEIGHT = 64
FRAMERATE = 8
TIME_LIMIT = 200
NO_CARS = 40

#Light agents
class lightAgent(Agent):
    def __init__(self, unique_id, model, color=1, timer=8):
        super().__init__(unique_id, model)
        self.color=color
        self.timer=timer
    def step(self):
        if self.timer == 0:
            if self.color < 3:
                self.color+=1
            else:
                self.color=1
            self.timer = 8
        self.timer -=1

#Car agent
class carAgent(Agent):
    def __init__(self, unique_id, model, type, big_lane, startingPosition, targetPosition, lane):
        super().__init__(unique_id, model)
        self.type=type
        self.startingPosition = startingPosition  # 1 to 4: left, top, right, bottom
        self.targetPosition = targetPosition  # (X, Y) coordinate
        self.lane = lane
        self.big_lane = big_lane
                
    # Step function
    def step(self):
        currentX, currentY = self.pos
        targetX, targetY = self.targetPosition
        
        if (currentX,currentY) == (0,0):
            return

        if self.big_lane == 1 or self.big_lane == 3:
            if self.lane == 1:  
                if currentX < targetX:
                    self.model.grid.move_agent(self, (currentX + 1, currentY))
                elif currentX > targetX:
                    self.model.grid.move_agent(self, (currentX - 1, currentY))
                else:
                    if currentY > targetY:
                        self.model.grid.move_agent(self, (currentX, currentY - 1))
                    elif currentY > targetY:
                        self.model.grid.move_agent(self, (currentX, currentY + 1))

            if self.lane == 2:
                if currentX < targetX:
                    self.model.grid.move_agent(self, (currentX + 1, currentY))
                elif currentX > targetX:
                    self.model.grid.move_agent(self, (currentX - 1, currentY))
                
            if self.lane == 3:  
                if currentX < targetX:
                    self.model.grid.move_agent(self, (currentX + 1, currentY))
                elif currentX > targetX:
                    self.model.grid.move_agent(self, (currentX - 1, currentY))
                else:
                    if currentY < targetY:
                        self.model.grid.move_agent(self, (currentX, currentY + 1))
                    elif currentY > targetY:
                        self.model.grid.move_agent(self, (currentX, currentY - 1))
        
        if self.big_lane == 2 or self.big_lane == 4:
            if self.lane == 1:  
                if currentY > targetY:
                    self.model.grid.move_agent(self, (currentX, currentY - 1))
                elif currentY < targetY:
                    self.model.grid.move_agent(self, (currentX, currentY + 1))
                else:
                    if currentX > targetX:
                        self.model.grid.move_agent(self, (currentX - 1, currentY))
                    if currentX < targetX:
                        self.model.grid.move_agent(self, (currentX + 1, currentY))

            if self.lane == 2:
                if currentY > targetY:
                    self.model.grid.move_agent(self, (currentX, currentY - 1))
                elif currentY < targetY:
                    self.model.grid.move_agent(self, (currentX, currentY + 1))
                
            if self.lane == 3:  
                if currentY > targetY:
                    self.model.grid.move_agent(self, (currentX, currentY - 1))
                elif currentY < targetY:
                    self.model.grid.move_agent(self, (currentX, currentY + 1))
                else:
                    if currentX < targetX:
                        self.model.grid.move_agent(self, (currentX + 1, currentY))
                    elif currentX > targetX:
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
        2: (255, 165, 0),  # Orange
        3: (255, 0, 0),    # Red
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
        self.no_cars = NO_CARS

        #Place light Agents
        a = lightAgent(100, self)
        self.grid.place_agent(a, (1, 1))
        self.schedule.add(a)

        lane = 1
        while lane <= 4:
            if self.no_cars > 0:
                randomized_cars = np.random.randint(0,self.no_cars)
                self.no_cars = self.no_cars-randomized_cars
                if lane == 1:
                    x_lane1 = 0
                    x_lane2 = 0
                    x_lane3 = 0
                    for x in  range(randomized_cars):
                        randomized_inner_lane = np.random.randint(1,4)
                        if randomized_inner_lane == 1:
                            a = carAgent((x_lane1, 32), self, np.random.randint(1,6), 1, (x_lane1, 32), (32,0), randomized_inner_lane)
                            self.grid.place_agent(a, (x_lane1, 32))
                            self.schedule.add(a)
                            x_lane1 += 1
                        elif randomized_inner_lane == 2:
                            a = carAgent((x_lane2, 33), self, np.random.randint(1,6), 1, (x_lane2, 33), (63,33), randomized_inner_lane)
                            self.grid.place_agent(a, (x_lane2, 33))
                            self.schedule.add(a)
                            x_lane2 += 1
                        elif randomized_inner_lane == 3:
                            a = carAgent((x_lane3, 34), self, np.random.randint(1,6), 1, (x_lane3, 34), (29,63), randomized_inner_lane)
                            self.grid.place_agent(a, (x_lane3, 34))
                            self.schedule.add(a)
                            x_lane3 += 1
                elif lane == 2:
                    y_lane1 = 63
                    y_lane2 = 63
                    y_lane3 = 63
                    for x in  range(randomized_cars):
                        randomized_inner_lane = np.random.randint(1,4)
                        if randomized_inner_lane == 1:
                            a = carAgent((32, y_lane1), self, np.random.randint(1,6), 2, (32, y_lane1), (0,31), randomized_inner_lane)
                            self.grid.place_agent(a, (32, y_lane1))
                            self.schedule.add(a)
                            y_lane1 -= 1
                        elif randomized_inner_lane == 2:
                            a = carAgent((33, y_lane2), self, np.random.randint(1,6), 2, (33, y_lane2), (33,0), randomized_inner_lane)
                            self.grid.place_agent(a, (33, y_lane2))
                            self.schedule.add(a)
                            y_lane2 -= 1
                        elif randomized_inner_lane == 3:
                            a = carAgent((34, y_lane3), self, np.random.randint(1,6), 2, (34, y_lane3), (63,34), randomized_inner_lane)
                            self.grid.place_agent(a, (34, y_lane3))
                            self.schedule.add(a)
                            y_lane3 -= 1
                elif lane == 3:
                    x_lane1 = 63
                    x_lane2 = 63
                    x_lane3 = 63
                    for x in  range(randomized_cars):
                        randomized_inner_lane = np.random.randint(1,4)
                        if randomized_inner_lane == 1:
                            a = carAgent((x_lane1, 31), self, np.random.randint(1,6), 3, (x_lane1, 31), (31, 63), randomized_inner_lane)
                            self.grid.place_agent(a, (x_lane1, 31))
                            self.schedule.add(a)
                            x_lane1 -= 1
                        elif randomized_inner_lane == 2:
                            a = carAgent((x_lane2, 30), self, np.random.randint(1,6), 3, (x_lane2, 30), (0, 30), randomized_inner_lane)
                            self.grid.place_agent(a, (x_lane2, 30))
                            self.schedule.add(a)
                            x_lane2 -= 1
                        elif randomized_inner_lane == 3:
                            a = carAgent((x_lane3, 29), self, np.random.randint(1,6), 3, (x_lane3, 29), (34, 0), randomized_inner_lane)
                            self.grid.place_agent(a, (x_lane3, 29))
                            self.schedule.add(a)
                            x_lane3 -= 1
                elif lane == 4:
                    y_lane1 = 0
                    y_lane2 = 0
                    y_lane3 = 0
                    for x in  range(randomized_cars):
                        randomized_inner_lane = np.random.randint(1,4)
                        if randomized_inner_lane == 1:
                            a = carAgent((31, y_lane1), self, np.random.randint(1,6), 4, (31, y_lane1), (63, 31), randomized_inner_lane)
                            self.grid.place_agent(a, (31, y_lane1))
                            self.schedule.add(a)
                            y_lane1 += 1
                        elif randomized_inner_lane == 2:
                            a = carAgent((30, y_lane2), self, np.random.randint(1,6), 4, (30, y_lane2), (30, 63), randomized_inner_lane)
                            self.grid.place_agent(a, (30, y_lane2))
                            self.schedule.add(a)
                            y_lane2 += 1
                        elif randomized_inner_lane == 3:
                            a = carAgent((29, y_lane3), self, np.random.randint(1,6), 4, (29, y_lane3), (0, 29), randomized_inner_lane)
                            self.grid.place_agent(a, (29, y_lane3))
                            self.schedule.add(a)
                            y_lane3 += 1
                lane += 1
        

        # Start data collector
        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid})

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

#Calculate the max number of steps
numSteps = FRAMERATE * TIME_LIMIT
model = trafficModel(GRID_LENGTH, GRID_HEIGHT)


#Start model
for i in range(numSteps):
    model.step()
    agentSteps=i
print(f"Steps taken by all agents: {agentSteps:.0f}")
elapsedTime = (i+1) / FRAMERATE
print(f"Simulation over in {elapsedTime:.2f} seconds")

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