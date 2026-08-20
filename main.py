import os
import time
import math
width = 100
heigth = 50
render_grid = []
render_depth = []
# CLASSES ##
def m_rota(angle):
    return math.cos(angle) -math.sin(angle)
def m_rotb(angle):
    return math.cos(angle) + math.sin(angle)
class vec2:
    x,y = 0,0
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def __add__(self,other):
        return vec2(self.x + other.x, self.y + other.y)
    def __str__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ')'
class vec3:
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
    def __add__(self,other):
        return vec3(self.x + other.x, self.y + other.y,self.z + other.z)
    def __sub__(self,other):
        return vec3(self.x - other.x, self.y - other.y,self.z - other.z)
    def __mul__(self,other):
        return vec3(self.x * other, self.y * other,self.z * other)
    def len(self):
        return self.x + self.y + self.z
    def __str__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ',' + str(self.z) + ')'
    def rotXY(self, angle):
        return vec3(self.x * math.cos(angle) - self.z * math.sin(angle), 
                    self.y,
                    self.z * math.cos(angle) + self.x * math.sin(angle))
    def rotX(self, angle):
        return vec3(self.x * math.cos(angle) - self.y * math.sin(angle), 
                    self.y * math.cos(angle) + self.x * math.sin(angle),
                    self.z)
    #bipity bpity individual values are clamped XDD
    def cind(self,val):
        a = vec3(
                0 if abs(self.x) < val else self.x,
                0 if abs(self.y) < val else self.y,
                0 if abs(self.z) < val else self.z
            )
        return a
class tri:
    def __init__(self, x1, x2, x3):
       self.x1 = x1
       self.x2 = x2
       self.x3 = x3
    def __str__(self):
        return '<' + str(self.x1) + ',' + str(self.x2) + ',' + str(self.x3) + '>'
    
class dtri(tri):
    def __init__(self,x1, x2, x3, d):
        super().__init__(x1, x2, x3)
        self.depth = d
class rtri(tri):
    def __init__(self,x1, x2, x3, char):
        super().__init__(x1, x2, x3)
        self.char = char
    def offset(self, other):
        return rtri(self.x1 + other, self.x2 + other, self.x3 + other, self.char)
    def rotatex(self, angle):
        return rtri(self.x1.rotX(angle), self.x2.rotX(angle), self.x3.rotX(angle), self.char)
class Camera:
    def __init__(self, start_pos, look_angle):
        self.pos = start_pos
        self.angle = look_angle
        self.velocity = vec3(0,0,0)
        self.distance = 0
    def posA(self):
        return self.pos + vec3(0,math.sin(self.distance/2)/2,0)
class Obj:
    def __init__(self, position, rtris):
        self.rtris = rtris
        self.position = position
    def render(self):
        for rtri in self.rtris:
            renderRtri(rtri.offset(self.position))
    def cmov(self, pos):
        return Obj(self.position + pos, self.rtris)
    def cmovrx(self, pos, angle):
        a = []
        for i in self.rtris:
            a.append(i.rotatex(angle))
        return Obj(self.position + pos, a)
# RENDERING ##
def fillGrid():
    for h in range(heigth):
        tempRow = []
        tempDepth = []
        for w in range(width):
           tempRow.append('_')
           tempDepth.append(math.inf)
        render_grid.append(tempRow)
        render_depth.append(tempDepth)
def clearGrid():
    for I,i in enumerate(render_grid):
        for B,b in enumerate(i):
            render_depth[I][B] = math.inf
            render_grid[I][B] = '_'
def renderGrid():
    temp = ""
    for y in render_grid:
        for x in y:
            temp += str(x)
        temp += '\n'
    #os.system('clear')
    print(temp)

fillGrid()
renderGrid()
# TRIANGLES ##
def area(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float):
    return abs((x1 * (y2 - y3) + x2 * (y3 - y1) 
                + x3 * (y1 - y2)) / 2.0)

def isInside(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, x: float, y: float):

    # Calculate area of triangle ABC
    A = area (x1, y1, x2, y2, x3, y3)

    # Calculate area of triangle PBC 
    A1 = area (x, y, x2, y2, x3, y3)
    
    # Calculate area of triangle PAC 
    A2 = area (x1, y1, x, y, x3, y3)
    
    # Calculate area of triangle PAB 
    A3 = area (x1, y1, x2, y2, x, y)
    
    # Check if sum of A1, A2 and A3 
    # is same as A
    if(round(A,10) == round(A1 + A2 + A3, 10)):
        return True
    else:
        return False

def renderTri(tri,char):
    for Y,y in enumerate(render_grid):
        for X,x in enumerate(y):
            if isInside(tri.x1.x, tri.x1.y, tri.x2.x, tri.x2.y, tri.x3.x, tri.x3.y, X, Y):
                render_grid[Y][X] = char[X%len(char)]
def renderDTri(tri,char):
    for Y,y in enumerate(render_grid):
        for X,x in enumerate(y):
            if tri.depth == -2:
                return
            if tri.depth != -1 and tri.depth > render_depth[Y][X]:
                continue
            if isInside(tri.x1.x, tri.x1.y, tri.x2.x, tri.x2.y, tri.x3.x, tri.x3.y, X, Y):
                render_grid[Y][X] = char[X%len(char)]
                render_depth[Y][X] = tri.depth
# PROJECTION ##
def ViewportToCanvas(x, y) :
  return vec2((x - 0.5) * width, (y - 0.5) * heigth)
def ProjectVertex(v):
    if v.z == 0:
        return vec2(0,0)
    return ViewportToCanvas(v.x * 1.0 / v.z, v.y * 1.0 / v.z) + vec2(width, heigth)
def pointTo2D(vec3):
    global depth
    rotated_point = (vec3 - camera.posA()).rotXY(camera.angle.x)
    if depth == -6:
        return
    elif rotated_point.z < 0:
        depth = -6
        return
    depth += abs(rotated_point.z)
    return ProjectVertex(rotated_point)    
# TRI RENDER ##
depth = 0
def renderPoints(p1,p2,p3,char):
    global depth
    depth = 0
    a = dtri(
        pointTo2D(points[p1]),
        pointTo2D(points[p2]),
        pointTo2D(points[p3]),
        depth / 3.0
    )
    renderDTri(a,char)
def renderRtri(rtri):
    global depth
    a = dtri(
        pointTo2D(rtri.x1),
        pointTo2D(rtri.x2),
        pointTo2D(rtri.x3),
        depth/3.0
    )
    renderDTri(a,rtri.char)
# INITING VARS ##
running = True
camera = Camera(vec3(100,0,0),vec2(0,math.pi))
# INITING GEOMETRY ##
points = [
    vec3(0,0,0),
    vec3(-7,-10,0),
    vec3(-27,-10,0),
    vec3(-37,-30,0),
    vec3(-40,-30,0),
    vec3(-47,-20,0),
    vec3(-40,-10,0),
    vec3(-53,-10,0),
    vec3(-60,0,0),
]
objects_pre = [
    #box
    Obj(
        vec3(0,0,0),
        [
            rtri(points[0],points[1],points[8],'NIX'),
            rtri(points[1],points[7],points[8],'NIX'),
            rtri(points[2],points[6],points[3],'NIX'),
            rtri(points[5],points[6],points[3],'NIX'),
            rtri(points[4],points[5],points[3],'NIX'),
        ])
]
t_fraction = (math.pi / 3)
t_dist = 20
objects = [
    objects_pre[0].cmovrx(vec3(m_rota(t_fraction*0)*t_dist,m_rotb(t_fraction*0)*t_dist,0), t_fraction*2),
    objects_pre[0].cmovrx(vec3(m_rota(t_fraction*1)*t_dist,m_rotb(t_fraction*1)*t_dist,0), t_fraction*3),
    objects_pre[0].cmovrx(vec3(m_rota(t_fraction*2)*t_dist,m_rotb(t_fraction*2)*t_dist,0), t_fraction*4),
    objects_pre[0].cmovrx(vec3(m_rota(t_fraction*3)*t_dist,m_rotb(t_fraction*3)*t_dist,0), t_fraction*5),
    objects_pre[0].cmovrx(vec3(m_rota(t_fraction*4)*t_dist,m_rotb(t_fraction*4)*t_dist,0), t_fraction*0),
    objects_pre[0].cmovrx(vec3(m_rota(t_fraction*5)*t_dist,m_rotb(t_fraction*5)*t_dist,0), t_fraction*1),
]
collection = []
# MAIN LOOP ##
tick = 0
while running:
    time.sleep(0.005)
    tick += 1
    #mo+= turn
    camera.pos = vec3(0,0,-150)
    camera.pos = camera.pos.rotXY(tick / 10.0) + vec3(0,math.cos(tick/10.0),0)
    camera.angle.x = -tick / 10.0
    #camera.angle.x = tick / 0.1
    #render
    clearGrid()
    for i in objects:
        i.render()
    renderGrid()
    #debug
    print("Yobi alpha 0.4v", tick, camera.pos, camera.angle)
