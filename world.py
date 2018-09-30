import pygame
class Point:
    def __init__(self, x=0,y=0):
        self.x=x
        self.y=y

class Line:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        if self.end.x != self.start.x:
            self.grad = (self.end.y-self.start.y)/(self.end.x-self.start.x)
            self.c = self.start.y-self.grad*self.start.x
        else:
            self.grad = None
            self.c = None
        

    def is_line_intersect(self, line):
        if self.grad!=None and line.grad==None:
            y = self.grad*line.start.x+self.c
            x = line.start.x
            if (self.start.x<=x<=self.end.x or self.start.x>=x>=self.end.x) and (line.start.y<=y<=line.end.y or line.start.y>=y>=line.end.y):
                return (x , y)
            else:
                return False
        elif line.grad!=None and self.grad==None:
            y = line.grad*self.start.x+line.c
            x = self.start.x
            if (line.start.x<=x<=line.end.x or line.start.x>=x>=line.end.x) and (self.start.y<=y<=self.end.y or self.start.y>=y>=self.end.y):
                return (x, y)
            else:
                return False
        if self.grad==line.grad:
            return None
        x = (self.c-line.c)/(line.grad-self.grad)
        y = self.grad*x+self.c
        if (self.start.x<=x<=self.end.x or self.start.x>=x>=self.end.x) and (self.start.y<=y<=self.end.y or self.start.y>=y>=self.end.y) and (line.start.x<=x<=line.end.x or line.start.x>=x>=line.end.x) and (line.start.y<=y<=line.end.y or line.start.y>=y>=line.end.y):
            return (x,y)
        return False


class Block:
    def __init__(self, ll,ur):
        self.ll=ll
        self.ur=ur
        self.x_len = self.ur.x-self.ll.x
        self.y_len = self.ur.y-self.ll.y

    def is_overlap(self,p):
        if self.ll.x <= p.x <= self.ur.x and \
          self.ll.y <= p.y <= self.ur.y:
            return True
        else:
            return False


    def is_line_intersect(self, line):
        corner1 = self.ll
        corner2 = Point(corner1.x+self.x_len, corner1.y)
        corner3 = Point(corner1.x, corner1.y+self.y_len)
        corner4 = self.ur
        ls = []
        for edge in [Line(corner1, corner2), Line(corner1,corner3), Line(corner2, corner4), Line(corner3,corner4)]:
            x = line.is_line_intersect(edge)
            if x==None:
                continue
            if x!=False:
                ls.append(x)
        if ls==[]:
            return False
        final = []
        for x,y in ls:
            final.append(((line.start.x-x)**2+(line.start.y-y)**2)**0.5)
        return ls[final.index(min(final))], min(final)

class Floor(Block):
    def __init__(self, ll, ur, color=(255,255,255)):
        Block.__init__(self,ll, ur)
        self._color = color


    def get_color(self):
        return self._color

    def set_color(self, color):
        self._color = color

    color = property(get_color, set_color)


class Wall(Block):
    def __init__(self, ll, ur, height=10):
        Block.__init__(self,ll,ur)
        self._height = height

    def get_height(self):
        return self._height

    def set_height(self, height):
        self._height = height

    height = property(get_height, set_height)

class World:
    def __init__(self, blocks,init_pos=None, init_heading=0):
        self.blocks=blocks
        self.init_heading=init_heading
        if init_pos !=None:
            self.init_pos=init_pos
        else:
            ll,ur=self.get_world_boundaries()
            self.init_pos=Point(abs(ur.x-ll.x)//2,abs(ur.y-ll.y)//2)
        
    def get_init_pos(self):
        return self.init_pos

    def get_init_heading(self):
        return self.init_heading

    def is_overlap(self,p):
        for b in self.blocks:
            if b.is_overlap(p):
                return True
        return False

    def get_centre_world(self):
        ll,ur=self.get_world_boundaries()
        xc=abs(ur.x-ll.x)//2
        yc=abs(ur.y-ll.y)//2
        return Point(xc,yc)

    def get_world_boundaries(self):
        min_x=self.blocks[0].ll.x
        min_y=self.blocks[0].ll.y
        max_x=self.blocks[0].ll.x
        max_y=self.blocks[0].ll.y
        for b in self.blocks:
            ll_x=b.ll.x
            ll_y=b.ll.y
            ur_x=b.ur.x
            ur_y=b.ur.y
            min_x=min(min_x,ll_x,ur_x)
            min_y=min(min_y,ll_y,ur_y)
            max_x=max(max_x,ll_x,ur_x)
            max_y=max(max_y,ll_y,ur_y)
        ll=Point(min_x,min_y)
        ur=Point(max_x,max_y)
        return ll,ur 

    def draw_world(self,t):
        for b in self.blocks:
            self.draw_block(t,b)

    def draw_block(self,t,b):
        t.penup()
        t.setposition(b.ll.x,b.ll.y)
        t.pendown()
        t.setx(b.ur.x)
        t.sety(b.ur.y)
        t.setx(b.ll.x)
        t.sety(b.ll.y)
        t.penup()

class PGWorld(World):
    def draw_block(self, robot, block):
        assert(block.ll.x<=block.ur.x and block.ll.y>=block.ll.x)
        if robot.screen.screen == None:
            return
        if isinstance(block, Floor):
            pygame.draw.rect(robot.screen.screen, block.color, (block.ll.x, block.ll.y, block.x_len, block.y_len))
        else:
            pygame.draw.rect(robot.screen.screen, (0,0,0,0), (block.ll.x, block.ll.y, block.x_len, block.y_len))
            pygame.draw.rect(robot.screen.screen, (255,255,255), (block.ll.x+2, block.ll.y+2, block.x_len-4, block.y_len-4))