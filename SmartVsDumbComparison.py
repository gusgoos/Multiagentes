from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
from numba import jit
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import json

#Parameters for simulation
GRID_LENGTH_NORMAL = 64
GRID_HEIGHT_NORMAL = 64
FRAMERATE_NORMAL = 8
TIME_LIMIT_NORMAL = 90
NUM_STEPS_NORMAL = FRAMERATE_NORMAL * TIME_LIMIT_NORMAL


class LightAgentNormal(Agent):
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
class CarAgentNormal(Agent):
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
            allCarAgents = [agent for agent in cell_agents if isinstance(agent, CarAgentNormal)]
            allLightAgents = [agent for agent in cell_agents if isinstance(agent, LightAgentNormal)]
    
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

#TrafficModelNormal
class TrafficModelNormal(Model):
    def __init__(self, length, height):
        self.grid = MultiGrid(length, height, torus=True)
        self.schedule = SimultaneousActivation(self)
        self.cars = 0
        
        #Place light Agents
        a = LightAgentNormal(1, self, 1)
        self.grid.place_agent(a, (2, 2))
        self.schedule.add(a)
        b = LightAgentNormal(2, self, 2)
        self.grid.place_agent(b, (1, 3))
        self.schedule.add(b)
        c = LightAgentNormal(3, self, 2)
        self.grid.place_agent(c, (2, 4))
        self.schedule.add(c)
        d = LightAgentNormal(4, self, 2)
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
                        a = CarAgentNormal(id, self, np.random.randint(1,6), 1, (x_lane1, 32), (32,0), randomized_inner_lane)
                        self.grid.place_agent(a, (x_lane1, 32))
                        self.schedule.add(a)
                        x_lane1 += 2
                        id += 1
                    elif randomized_inner_lane == 2:
                        a = CarAgentNormal(id, self, np.random.randint(1,6), 1, (x_lane2, 33), (63,33), randomized_inner_lane)
                        self.grid.place_agent(a, (x_lane2, 33))
                        self.schedule.add(a)
                        x_lane2 += 2
                        id += 1
                    elif randomized_inner_lane == 3:
                        a = CarAgentNormal(id, self, np.random.randint(1,6), 1, (x_lane3, 34), (29,63), randomized_inner_lane)
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
                        a = CarAgentNormal(id, self, np.random.randint(1,6), 2, (32, y_lane1), (0,31), randomized_inner_lane)
                        self.grid.place_agent(a, (32, y_lane1))
                        self.schedule.add(a)
                        y_lane1 -= 2
                        id += 1
                    elif randomized_inner_lane == 2:
                        a = CarAgentNormal(id, self, np.random.randint(1,6), 2, (33, y_lane2), (33,0), randomized_inner_lane)
                        self.grid.place_agent(a, (33, y_lane2))
                        self.schedule.add(a)
                        y_lane2 -= 2
                        id += 1
                    elif randomized_inner_lane == 3:
                        a = CarAgentNormal(id, self, np.random.randint(1,6), 2, (34, y_lane3), (63,34), randomized_inner_lane)
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
                        a = CarAgentNormal(id, self, np.random.randint(1,6), 3, (x_lane1, 31), (31, 63), randomized_inner_lane)
                        self.grid.place_agent(a, (x_lane1, 31))
                        self.schedule.add(a)
                        x_lane1 -= 2
                        id += 1
                    elif randomized_inner_lane == 2:
                        a = CarAgentNormal(id, self, np.random.randint(1,6), 3, (x_lane2, 30), (0, 30), randomized_inner_lane)
                        self.grid.place_agent(a, (x_lane2, 30))
                        self.schedule.add(a)
                        x_lane2 -= 2
                        id += 1
                    elif randomized_inner_lane == 3:
                        a = CarAgentNormal(id, self, np.random.randint(1,6), 3, (x_lane3, 29), (34, 0), randomized_inner_lane)
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
                        a = CarAgentNormal(id, self, np.random.randint(1,6), 4, (31, y_lane1), (63, 32), randomized_inner_lane)
                        self.grid.place_agent(a, (31, y_lane1))
                        self.schedule.add(a)
                        y_lane1 += 2
                        id += 1
                    elif randomized_inner_lane == 2:
                        a = CarAgentNormal(id, self, np.random.randint(1,6), 4, (30, y_lane2), (30, 63), randomized_inner_lane)
                        self.grid.place_agent(a, (30, y_lane2))
                        self.schedule.add(a)
                        y_lane2 += 2
                        id += 1
                    elif randomized_inner_lane == 3:
                        a = CarAgentNormal(id, self, np.random.randint(1,6), 4, (29, y_lane3), (0, 29), randomized_inner_lane)
                        self.grid.place_agent(a, (29, y_lane3))
                        self.schedule.add(a)
                        y_lane3 += 2
                        id += 1
            lane += 1
        

        # Start data collector
        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid})
    
    def finish(self):
        cars = model.grid.get_cell_list_contents((0,0))
        if len(cars) == self.cars:
            return True
                     
    def carros(self):
        return self.cars
                     
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

def graficaNormal(model):
    last_frame = 0
    for i in range(NUM_STEPS_NORMAL):
        model.step()
        last_frame += 1
        finish = model.finish()
        if finish:
            break
    return last_frame

matriz1 = []
for x in range(100):
    corrida = []
    model = TrafficModelNormal(GRID_LENGTH_NORMAL, GRID_HEIGHT_NORMAL)
    carros = model.carros() 
    corrida.append(carros)
    tiempo = graficaNormal(model)
    corrida.append(tiempo)   
    matriz1.append(corrida)
    
print(matriz1)

GRID_LENGTH = 64
GRID_HEIGHT = 64
FRAMERATE = 8
TIME_LIMIT = 90
#NO_CARS = 50

class controllAgent(Agent):
  def __init__(self,unique_id,model):
    super().__init__(unique_id, model)
    # Este atributo guarda el objeto semaforo que este activo en ese momento
    self.light_act = None
    # Esta variable sirve como un time cuando un semaforo cambia de verde a rojo, dandole tiempo a los carros de pasar antes poner otro semaforo en verde
    self.timer = 0
    # Este booleano sirve como un auxiliar para activar el timer, este nos indica si se pondrá en verde un semaforo nuevo
    self.cambio = False

  def step(self):
    # Si no está activo cambio(o sea no esta cambiando de semaforo), entrará a evaluar cual semaforo debe estár en verde
    if not self.cambio:
      max = -1
      new_sem = None
      # Recorre todos los semaforos y evalua la cantidad de carros que tiene
      for semaforo in self.model.light:
        if semaforo.car_count > max:
          max = semaforo.car_count
          new_sem = semaforo
      # Si el atributo light_act es None significa que aun no hay ningun semaforo activo, por lo que no se activará el booleano cambio
      if self.light_act is None:
        self.light_act = new_sem
        self.light_act.color = 1
      # En caso de que ya haya un semaforo activo se evalua si el nuevo semaforo es el mismo o se hará un cambio
      else:
        if new_sem != self.light_act:
          self.light_act.color = 2
          self.light_act = new_sem
          self.cambio = True
    # En caso de que cambio sea True se realizarán 5 steps vacios para que los carros puedan pasar
    else:
      if self.timer == 3:
        self.light_act.color = 1
        self.cambio = False
        self.timer = 0
      else:
        self.timer += 1

#Light agents
class lightAgent(Agent):
    def __init__(self, unique_id, model, orientacion, inicio, fin, xy_ini, xy_fin):
        super().__init__(unique_id, model)
        # Este atributo controla si el semaforo está en verde o rojo
        self.color=2
        # Este lleva la cuenta de cuantos carros hay en el carril de este semaforo
        self.car_count = 0
        # Estos atributos guardan las coordenadas de inicio y fin en X y Y del area del semaforo, o sea los 3 carriles del semaforo
        self.inicio = inicio
        self.fin = fin
        self.dire = orientacion
        self.posi_ini = xy_ini
        self.posi_fin = xy_fin

    def step(self):
      # Se iguala el contador de carros a 0 para que se actualice en cada step
      self.car_count = 0
      # Este if solo evalua si el carril es vertical u horizontal
      if(self.dire == True):
        # Se recorre cada coordenada el carril del semaforo y se cuenta la cantidad de carros
        for i in range(self.posi_ini, self.posi_fin +1):
          for j in range(self.inicio, self.fin+1):
            cell_agentes = model.grid.get_cell_list_contents((j, i))
            self.car_count += len(cell_agentes)
      else:
        for i in range(self.posi_ini, self.posi_fin +1):
          for j in range(self.inicio, self.fin+1):
            cell_agentes = model.grid.get_cell_list_contents((i, j))
            self.car_count += len(cell_agentes)


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
            light = self.model.grid.get_cell_list_contents((1,1))[0]
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
            light = self.model.grid.get_cell_list_contents((1,2))[0]
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
            light = self.model.grid.get_cell_list_contents((2,1))[0]
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
            light = self.model.grid.get_cell_list_contents((2,2))[0]
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
        self.light = []
        self.cars = 0

        #Place light Agents
        a = lightAgent(1, self, True, 0, 28, 32, 34)
        self.grid.place_agent(a, (1, 1))
        self.schedule.add(a)
        b = lightAgent(2, self, False, 35, 63, 32, 34)
        self.grid.place_agent(b, (2, 1))
        self.schedule.add(b)
        c = lightAgent(3, self, True, 35, 63, 29, 31)
        self.grid.place_agent(c, (1, 2))
        self.schedule.add(c)
        d = lightAgent(4, self, False, 0, 28, 29, 31)
        self.grid.place_agent(d, (2, 2))
        self.schedule.add(d)

        self.light.append(a)
        self.light.append(b)
        self.light.append(c)
        self.light.append(d)

        controller = controllAgent(5, self)
        self.schedule.add(controller)

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
        
    def finish(self):
        cars = model.grid.get_cell_list_contents((0,0))
        if len(cars) == self.cars:
            return True
                     
    def carros(self):
        return self.cars
                     
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()   
        
def graficaInteligente(model):
    last_frame = 0
    for i in range(NUM_STEPS_NORMAL):
        model.step()
        last_frame += 1
        finish = model.finish()
        if finish:
            break
    return last_frame

matriz2 = []
for x in range(100):
    corrida = []
    model = trafficModel(GRID_LENGTH_NORMAL, GRID_HEIGHT_NORMAL)
    carros = model.carros() 
    corrida.append(carros)
    tiempo = graficaNormal(model)
    corrida.append(tiempo)   
    matriz2.append(corrida)
    
print(matriz2)

# Sort the data by the first index of each subarray
matriz1.sort(key=lambda x: x[0])
matriz2.sort(key=lambda x: x[0])

# Extract x and y values for each matrix
x_values1 = [item[0] for item in matriz1]
y_values1 = [item[1] for item in matriz1]

x_values2 = [item[0] for item in matriz2]
y_values2 = [item[1] for item in matriz2]

# Set the width of the bars
bar_width = 0.35

# Create an array to represent the x-axis positions
x_positions = np.arange(len(x_values1))

# Create the bar graph for matriz1 (blue bars)
plt.bar(x_positions, y_values1, bar_width, label='Dumb Light', color='b')

# Create the bar graph for matriz2 (red bars) with an offset
plt.bar(x_positions + bar_width, y_values2, bar_width, label='Smart Light', color='r')

# Set the x-axis labels and title
plt.xlabel("Number of Cars")
plt.ylabel("Time")

# Set the x-axis ticks
# Set interval for x-axis ticks
interval = 5
tick_indices = list(range(0, len(x_values1), interval))

# Set the x-axis ticks
plt.xticks(x_positions[tick_indices] + bar_width / 2, [x_values1[i] for i in tick_indices], rotation=45)

# Show a legend
plt.legend()

# Show the graph
plt.show()