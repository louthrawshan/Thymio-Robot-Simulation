import numpy
from world import *
import math
import pygame
import time
from threading import Thread
from pythymiodw import ThymioSim, io
from math import sin, cos, pi
from tkinter import *

# This is the global list so that the display thread that updates the screen can be updated
global_list = []
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)

width, height = (600,800)
dt = 200

class ThymioSimPG(ThymioSim):
    def __init__(self, world = None):
        super().__init__(world)
        self.robot.setworld(self.world)
        tkinter_thread = Thread(target = self.button_screen)
        tkinter_thread.deamon = True
        tkinter_thread.start()
        pygame_thread = Thread(target = self.update)
        pygame_thread.deamon = True
        pygame_thread.start()

    def callback(self, number):
        print(number)

    def button_screen(self):
        self.tkinter_screen = Tk()
        
        bt1 = Button(self.tkinter_screen, text = "1", command = lambda: self.callback(1))
        bt2 = Button(self.tkinter_screen, text = "2", command = lambda: self.callback(2))
        bt3 = Button(self.tkinter_screen, text = "3", command = lambda: self.callback(3))
        bt4 = Button(self.tkinter_screen, text = "4", command = lambda: self.callback(4))
        bt5 = Button(self.tkinter_screen, text = "5", command = lambda: self.callback(5))

        bt1.grid(row = 0, column = 1)
        bt2.grid(row = 1, column = 0)
        bt3.grid(row = 1, column = 2)
        bt4.grid(row = 2, column = 1)
        bt5.grid(row = 1, column = 1)

        self.tkinter_screen.mainloop()

    def open(self):
        self.window = PGScreen()
        self.robot = PGRobot(self.window)

    # Thread to continuously update the pygame screen
    def update(self):
        global global_list
        self.running = True
        x0 = time.time()
        while self.running:
            x1 = time.time()
            x0 = x1
            x = pygame.event.get()
            for event in x:
                if event.type==pygame.QUIT:
                    self.running=False
                    pygame.quit()
                    sys.exit()
            
            if global_list!=[]:
                self.robot.screen.screen.fill(white)
                self.world.draw_world(self.robot)
                robot, pos = global_list
                self.robot.screen.screen.blit(robot, pos) 
                global_list = []
            pygame.display.update()

    def speed_to_pixel(self, a, b):
        return int(a*0.1309*dt/1000), int(b*0.1309*dt/1000)

    # wheels() method callsa this function
    def _wheels(self,l,r):
        vl,vr=self.speed_to_pixel(l,r)
        self.omegadeg= omegadeg = (l-r)*0.18*dt/1000
        self.fv= fv = 0.5*(vr+vl)
        can_move=self.check_world(fv)
        if can_move:
            self.robot.forward(fv, omegadeg)
        else:
            pass

    def check_floor(self):
        x1 = None
        x2 = None
        sensor1, sensor2 = self.robot.get_ground_sensor_position()
        for block in self.world.blocks:
            if block.is_overlap(Point(sensor1[0], sensor1[1])):
                x1 = block
            if block.is_overlap(Point(sensor2[0], sensor2[1])):
                x2 = block
        return x1, x2

    def check_world(self, fv):
        points = self.robot.get_new_position(self.fv, self.omegadeg)
        if self.world==None:
            return True
        for x,y in points:
            if not 0<=x<=width or not 0<=y<=height:
                return False
            for block in self.world.blocks:
                if block.is_overlap(Point(x,y)) and isinstance(block, Wall):
                    return False
        return True 
                
    def quit(self):
        self.running = False
        sys.exit()

    def get_prox_ground(self):
        x1, x2 =  self.check_floor()
        delta = [-1,-1]
        ambiant = (1,1)
        if isinstance(x1, Floor):
            color = x1.color
            color_average = (color[0]+color[1]+color[2])/3
            delta[0] = (int(1023*color_average/255))
        if isinstance(x2, Floor):
            color = x2.color
            color_average = (color[0]+color[1]+color[2])/3
            delta[1] = (int(1023*color_average/255))
        if delta[0]==-1:
            delta[0]=1023
        if delta[1]==-1:
            delta[1]=1023
        delta = (delta[0], delta[1])
        # print(delta)
        return io.ProxGround(delta = delta, reflected = delta, ambiant = ambiant)

    def get_prox_horizontal(self):
        x = self.robot.get_horizontal_sensor_position()
        y = self.robot.get_range_points_of_sensor()
        dic = {}
        for i in range(7):
            dic[i] = Line(Point(x[i][0], x[i][1]), Point(y[i][0], y[i][1]))
        distances = {}
        for block in self.world.blocks:
            if isinstance(block, Floor):
                continue
            for i in range(7):
                x = block.is_line_intersect(dic[i])
                if x!=False:
                    y, x = x
                    distances[i] = x/36*11
        ls = []
        for i in range(7):
            try:
                x = 4600 - 460*distances[i]
                ls.append(x)
            except:
                ls.append(0) 

        return ls

class PGRobot:
    def __init__(self, screen, world= None):
        self.screen = screen
        robot = pygame.image.load("thymio2.png").convert_alpha()
        robot = pygame.transform.rotate(robot, -90)
        self.robot = pygame.transform.scale(robot, (36, int(725/685*36)))
        self.world = world
        self.pos = (0,0)
        self.time = time.time()

    def get_ground_sensor_position(self):
        x_pos, y_pos = self.get_center_wheels()
        x_pos =  x_pos + 11*cos(self.head*pi/180)*36/11
        y_pos =  y_pos + 11*sin(self.head*pi/180)*36/11
        x_pos1 = x_pos - 1.25*sin(self.head*pi/180)*36/11
        y_pos1 = y_pos + 1.25*cos(self.head*pi/180)*36/11
        x_pos2 = x_pos + 1.25*sin(self.head*pi/180)*36/11
        y_pos2 = y_pos - 1.25*cos(self.head*pi/180)*36/11
        return ((x_pos1, y_pos1), (x_pos2, y_pos2))

    def get_center_wheels(self):
        self.head = self.head%360
        robot = pygame.transform.rotate(self.robot, -self.head)
        x = robot.get_rect()
        if 0<=self.head<=90:      
            x_cpos = self.pos[0]+5.5*sin(self.head*pi/180)*36/11
            y_cpos = self.pos[1]+5.5*cos(self.head*pi/180)*36/11
        elif 90<=self.head<=180:
            x_cpos = self.pos[0]+x[2]-5.5*sin(pi-self.head*pi/180)*36/11
            y_cpos = self.pos[1]+5.5*cos(pi-self.head*pi/180)*36/11
        elif 180<=self.head<=270:
            x_cpos = self.pos[0]+x[2]-5.5*sin(-pi+self.head*pi/180)*36/11
            y_cpos = self.pos[1]+x[3]-5.5*cos(-pi+self.head*pi/180)*36/11
        elif 270<=self.head<=360:            
            x_cpos = self.pos[0]+5.5*sin(2*pi - self.head*pi/180)*36/11
            y_cpos = self.pos[1]+x[3]-5.5*cos(2*pi - self.head*pi/180)*36/11
        x_cpos = x_cpos + 8*cos(self.head*pi/180)
        y_cpos = y_cpos + 8*sin(self.head*pi/180)
        return x_cpos, y_cpos

    def get_center_robot(self):
        #
        x_pos, y_pos = self.get_center_wheels()
        x_pos =  x_pos + 3*cos(self.head*pi/180)*36/11
        y_pos =  y_pos + 3*sin(self.head*pi/180)*36/11
        return x_pos, y_pos

    def get_self_pos(self, x_cpos, y_cpos):
        #
        self.head = self.head%360
        robot = pygame.transform.rotate(self.robot, -self.head)
        x_cpos = x_cpos - 8*cos(self.head*pi/180)
        y_cpos = y_cpos - 8*sin(self.head*pi/180)
        x = robot.get_rect()
        if 0<=self.head<=90:
            x_pos = x_cpos-5.5*sin(self.head*pi/180)*36/11
            y_pos = y_cpos-5.5*cos(self.head*pi/180)*36/11
        elif 90<=self.head<=180:
            x_pos = x_cpos-x[2]+5.5*sin(pi-self.head*pi/180)*36/11
            y_pos = y_cpos-5.5*cos(pi-self.head*pi/180)*36/11
        elif 180<=self.head<=270:
            x_pos = x_cpos-x[2]+5.5*sin(-pi+self.head*pi/180)*36/11
            y_pos = y_cpos-x[3]+5.5*cos(-pi+self.head*pi/180)*36/11
        elif 270<=self.head<=360:  
            x_pos = x_cpos-5.5*sin(2*pi - self.head*pi/180)*36/11
            y_pos = y_cpos-x[3]+5.5*cos(2*pi - self.head*pi/180)*36/11
        return (x_pos, y_pos)


    def get_horizontal_sensor_position(self):
        x, y = self.get_center_robot()
        distance = 6
        x5 = x + distance*cos(self.head*pi/180)*36/11
        y5 = y + distance*sin(self.head*pi/180)*36/11
        x4 = x + distance*cos(self.head*pi/180+pi/8)*36/11
        y4 = y + distance*sin(self.head*pi/180+pi/8)*36/11
        x3 = x + distance*cos(self.head*pi/180+pi/4)*36/11
        y3 = y + distance*sin(self.head*pi/180+pi/4)*36/11
        x2 = x + distance*cos(self.head*pi/180-pi/8)*36/11
        y2 = y + distance*sin(self.head*pi/180-pi/8)*36/11
        x1 = x + distance*cos(self.head*pi/180-pi/4)*36/11
        y1 = y + distance*sin(self.head*pi/180-pi/4)*36/11
        x_pos, y_pos = self.get_center_wheels()
        x6 = x_pos + 3*sin(self.head*pi/180)*36/11
        y6 = y_pos - 3*cos(self.head*pi/180)*36/11
        x7 = x_pos - 3*sin(self.head*pi/180)*36/11
        y7 = y_pos + 3*cos(self.head*pi/180)*36/11
        return ((x1,y1),(x2,y2),(x5,y5),(x4,y4),(x3,y3), (x7,y7), (x6, y6))

    def get_range_points_of_sensor(self):
        distance = 15
        x, y = self.get_center_robot()
        x5 = x + distance*cos(self.head*pi/180)*36/11
        y5 = y + distance*sin(self.head*pi/180)*36/11
        x4 = x + distance*cos(self.head*pi/180+pi/8)*36/11
        y4 = y + distance*sin(self.head*pi/180+pi/8)*36/11
        x3 = x + distance*cos(self.head*pi/180+pi/4)*36/11
        y3 = y + distance*sin(self.head*pi/180+pi/4)*36/11
        x2 = x + distance*cos(self.head*pi/180-pi/8)*36/11
        y2 = y + distance*sin(self.head*pi/180-pi/8)*36/11
        x1 = x + distance*cos(self.head*pi/180-pi/4)*36/11
        y1 = y + distance*sin(self.head*pi/180-pi/4)*36/11
        distance = 9
        x_pos, y_pos = self.get_center_wheels()
        x6 = x_pos + 4*sin(self.head*pi/180)*36/11 - distance*cos(self.head*pi/180)*36/11
        y6 = y_pos - 4*cos(self.head*pi/180)*36/11 - distance*sin(self.head*pi/180)*36/11
        x7 = x_pos - 4*sin(self.head*pi/180)*36/11 - distance*cos(self.head*pi/180)*36/11
        y7 = y_pos + 4*cos(self.head*pi/180)*36/11 - distance*sin(self.head*pi/180)*36/11
        return ((x1,y1),(x2,y2),(x5,y5),(x4,y4),(x3,y3), (x7, y7), (x6, y6))

    def position(self):
        return self.pos

    def setworld(self, world):
        self.world = world

    def heading(self):
        return self.head

    def setposition(self, x_position, y_position):
        self.pos = (x_position, y_position)

    def setheading(self, heading):
        self.head = heading%360

    def forward(self, fv, rv):
        global global_list
        x = time.time()
        x, y = (self.get_center_wheels())
        points = self.get_new_position(fv, rv)
        x = x+fv*cos(self.head*pi/180)
        y = y+fv*sin(self.head*pi/180)
        self.head+=rv
        self.pos = self.get_self_pos(x,y)
        robot = pygame.transform.rotate(self.robot, -self.head)
        global_list = [robot, self.pos]
        # for x,y in points:
        #     pygame.draw.rect(self.screen.screen, (0,0,0), (x,y,2,2))
        

    def get_new_position(self, fv, rv):
        x, y = (self.get_center_wheels())
        x = x+fv*cos(self.head*pi/180)
        y = y+fv*sin(self.head*pi/180)
        self.head+=rv
        x0 = x - 2*cos(self.head*pi/180)*36/11
        y0 = y - 2*sin(self.head*pi/180)*36/11
        x1 = x + 8*cos(self.head*pi/180)*36/11
        y1 = y + 8*sin(self.head*pi/180)*36/11
        x2 = x0 + 4.5*sin(self.head*pi/180)*36/11
        y2 = y0 - 4.5*cos(self.head*pi/180)*36/11
        x3 = x0 - 4.5*sin(self.head*pi/180)*36/11
        y3 = y0 + 4.5*cos(self.head*pi/180)*36/11
        x4 = x0 + 4.5*sin(self.head*pi/180)*36/11 + 8*cos(self.head*pi/180)*36/11
        y4 = y0 - 4.5*cos(self.head*pi/180)*36/11 + 8*sin(self.head*pi/180)*36/11
        x5 = x0 - 4.5*sin(self.head*pi/180)*36/11 + 8*cos(self.head*pi/180)*36/11
        y5 = y0 + 4.5*cos(self.head*pi/180)*36/11 + 8*sin(self.head*pi/180)*36/11
        self.head-=rv
        return (x0,y0), (x1, y1), (x2, y2), (x3,y3), (x4, y4), (x5, y5)

class PGScreen:
    def __init__(self):
        print("initialising screen....")
        self.screen = pygame.display.set_mode((width,height))

    def setworldcoordinates(self, x1, y1, x2, y2):
        pass 