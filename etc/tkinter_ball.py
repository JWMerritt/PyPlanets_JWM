import tkinter as tk
import numpy as np
import time



def make_window():
    Window = tk.Tk()
    Window.title("ball physics")
    Window.geometry("500x500+100+100")
    Window.resizable(True,True)

    return Window


class WinCanvas():

    TimeFlowing = False
    FPS = 60
    dt = 1/FPS
    Objects = []        # unordered list of objects in the simulation
    NumObjects = 0      # number of objects (number assoc. with the next object)
    Ball = []           # points to the ball currently spawned on the canvas
    BallSpawned = False # tracks whether the ball is spawned

    def __init__(self):
            # make Window:
        self.Window = make_window()
            # make Canvas:
        self.Canvas = tk.Canvas(self.Window, height=500, width=500)
        self.Canvas.place(x = 0, y = 0)

            # set TimeFlowing info:
        self.TimeInfo = tk.StringVar(self.Window, value = "Time:\nStopped")
        self.TimeButton = tk.Button(self.Window, textvariable = self.TimeInfo, command=self.TimeToggle)
        self.TimeButton.place(x = 20, y = 20)

    def SingleFrame(self, dt):
        # checks until dt has passed, then does a frame.
        StartFrame = time.time()    # starting time
        while self.TimeFlowing and self.BallSpawned:
            # constantly run through this until enough time has passed.
            # the advantage here is that we avoid the time.sleep() command, which would prevent
            #   us from otherwise interacting with the window.
            if time.time()-dt > StartFrame:
                self.Ball.timestep(dt=dt)
                break
        self.Window.update()

    def RunRoot(self):
        # primary time-evolving method.
        while self.TimeFlowing and self.BallSpawned:
            self.SingleFrame(dt=self.dt)

    def TimeToggle(self):
        self.TimeFlowing = not self.TimeFlowing
        if self.TimeFlowing:
            self.TimeInfo.set("Time:\nFlowing")
            self.RunRoot()
        else:
            self.TimeInfo.set("Time:\nStopped")
    
"""
def Phys_Linear(position, velocity, dt):
    OutPos = position + dt*velocity
    OutVel = velocity
    return OutPos, OutVel

def Phys_Grav(position, velocity, dt, g):
    OutPos = position + dt*velocity + 0.5*np.array([0,g])*dt*dt
    OutVel = velocity + dt*np.array([0,g])
    return OutPos, OutVel

def Phys_Kepler(position, velocity, dt, CMpos, g):
    dr = CMpos - position
    r = np.sqrt(dr[0]**2 + dr[1]**2)
    accel = dr*g/(r**3)
    OutPos = position + dt*velocity + 0.5*accel*dt*dt
    OutVel = velocity + dt*accel
    return OutPos, OutVel, accel
"""

class Phys_Linear():
    """
    Physics Engine Object for the Balls.
    The Engine has an evol(position, velocity, dt) function, which uses other attributes in its calculation.
    This one just does normal Euclidian space, with no forces. Pretty boring object...
    """
    def evol(self, position, velocity, dt):
        OutPos = position + dt*velocity
        OutVel = velocity
        return OutPos, OutVel

class Phys_Grav():
    """
    Physics Engine Object for the Balls.
    The Engine has an evol(position, velocity, dt) function, which uses other attributes in its calculation.
    This one has a constant gravitational acceleration, given by g.
    """
    accel = np.array([0,0])

    def __init__(self, g):
        self.accel = g
    
    def evol(self, position, velocity, dt):
        OutPos = position + dt*velocity * 0.5*self.accel*dt*dt
        OutVel = velocity + dt*self.accel
        return OutPos, OutVel

class Phys_Kepler():
    """
    Physics Engine Object for the Balls.
    The Engine has an evol(position, velocity, dt) function, which uses other attributes in its calculation.
    This one has a Keplerian source of acceleration, strength G, at point CMpos
    """
    CMpos = np.array([0,0])
    G = 10000

    def __init__(self, CMpos, G):
        self.CMpos = CMpos
        self.G = G
    
    def evol(self, position, velocity, dt):
        dr = self.CMpos - position
        r = np.sqrt(dr[0]**2 + dr[1]**2)
        accel = dr*self.G/(r**3)
        OutPos = position + dt*velocity + 0.5*accel*dt*dt
        OutVel = velocity + dt*accel
        return OutPos, OutVel

class Ball():
    """
    Ball object for the tkinter ball thingy.
    Includes the following methods:
    --------------------------------
        rect() - gives coords of bounding box of oval
        spawn(WinCanvas) - spawns Ball on WinCanvas
        despawn() - removes Ball from WinCanvas
        setPos(position) - sets the position of the Ball, and updates it on the WinCanvas
        timestep(dt) - finds Ball's next position after dt, and updates it.
    --------------------------------
    """    
    position = np.array([0,0])
    velocity = np.array([0,0])
    mass = 1
    radius = 20         # radius in pixels
    color = "red"

    spawned = False     # is the ball spawned?
    CanvasID = -1       # stores the Canvas ID of the ball's oval
    WinCanvasID = -1    # stores ID for WinCanvas's Object list
    WinCanvas = []      # points to the WinCanvas that the ball is spawned on

    PhysEngine = Phys_Linear

    def __init__(self, position=np.array([0,0]), velocity=np.array([0,0]), mass=1, radius=20, color="red", PhysEngine=Phys_Linear):
        # for setting initial values
        self.color = color
        self.position = position
        self.velocity = velocity
        self.mass = mass
        self.radius = radius
        self.PhysEngine = PhysEngine

    def rect(self):
        # this converts the polar data into rectilinear coordinates
        x0 = self.position[0] - self.radius
        x1 = self.position[0] + self.radius
        y0 = self.position[1] - self.radius
        y1 = self.position[1] + self.radius
        return x0, y0, x1, y1
    
    def spawn(self, WinCanvas):
        # this associates the Ball to a WinCanvas, and creates the graphics object
        if not self.spawned:
                # associate:
            self.WinCanvas = WinCanvas
                # draw oval:
            a,b,c,d = self.rect()
            #print(f"({a},{b}), and ({c},{d}).")
            self.CanvasID = WinCanvas.Canvas.create_oval(a,b,c,d,fill = self.color)
                ### ! Add code for handling multiple objects
            self.WinCanvas.Objects.append(self)
            self.WinCanvas.BallSpawned = True
            self.WinCanvas.Ball = self
            self.spawned = True
        else:
            print("Ball already spawned!")
    
    def despawn(self):
        if not self.spawned:
            print("Ball not spawned!")
        else:
            self.WinCanvas.Canvas.delete(self.CanvasID)
            self.WinCanvas.BallSpawned = False
            self.WinCanvas.Ball = []
            self.WinCanvas = []
            self.CanvasID = -1
            self.spawned = False
            print("Despawned!")
    
    def setPos(self, position=np.array([0,0])):
        # set [x,y] position of the ball, and update the oval on screen.
        self.position = position
        if self.spawned:
            x0,y0,etc1,etc2 = self.rect()     # moveto moves the top-left corner to this position
            self.WinCanvas.Canvas.moveto(self.CanvasID,x0,y0)


    def timestep(self, dt):
        TryPos, TryVel = self.PhysEngine.evol(position=self.position, velocity=self.velocity, dt=dt) # where the ball would go, uninterrupted.
        # Bounds of the ball:
        right = TryPos[0] + self.radius
        left = TryPos[0] - self.radius
        top = TryPos[1] - self.radius
        bottom = TryPos[1] + self.radius
        # remember that the screen coords are positive downwards and rightwards.
        while ((left < 0) or (top < 0) or (self.WinCanvas.Window.winfo_width() < right) or (self.WinCanvas.Window.winfo_height() < bottom)):
            # - while the ball would go out of bounds:

            if (left < 0) or (self.WinCanvas.Window.winfo_width() < right):
                self.velocity[0] = -self.velocity[0]
            
            if (top < 0) or (self.WinCanvas.Window.winfo_height() < bottom):
                self.velocity[1] = -self.velocity[1]
            
            TryPos, TryVel = self.PhysEngine.evol(self.position,self.velocity,dt)
            right = TryPos[0] + self.radius
            left = TryPos[0] - self.radius
            top = TryPos[1] - self.radius
            bottom = TryPos[1] + self.radius
            
            # -update the new attempt
        # - the ball should now be in-bounds at the next time step.
        self.position, self.velocity = self.PhysEngine.evol(self.position,self.velocity,dt)
        self.setPos(position=self.position)
