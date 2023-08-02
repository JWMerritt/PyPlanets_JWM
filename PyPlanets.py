

import pygame
import numpy as np
from itertools import combinations


def ppl_atan(point):
    """Advanced arctangent of a tuple point."""
    if point[0]==0:
        if point[1]>0:
            return np.pi
        else:
            return -np.pi
    elif point[0]<0:
        return np.arctan(point[1]/point[0])+np.pi
    else:
        return np.arctan(point[1]/point[0])


def rot_mat(theta):
    return np.array([[np.cos(theta),np.sin(theta)],[-np.sin(theta),np.cos(theta)]])


def numpy_to_tuples(np_in):
    listout = []
    for point in np_in:
        listout.append( (point[0],point[1]) )
    return listout


##################


class CameraRig():
    """
    Contains details of camera position / zoom, and functions for converting between Real/Image/Screen space.
    Real space is the coordinates that the physics simulation uses. 
    """

    PanPosition = np.array([0,0]) # Real-space displacement vector; CameraPosition = OriginOpsition + PanPosition

    CameraZoom = 25 # RealDistance * CameraZoom = ScreenDistance. Smaller number => smaller when drawn on screen

    CameraZoomLinear = 1 # CameraZoom = 10**CameraZoomLinear

    VelocityRatio = 1 # ScreenArrowSize = ActualVelocitySize * VelocityRatio

    FollowingPlanet = False

    FocusPlanet = False # When FollowingPlanet==True, this will point to the planet we're following


    def __init__(self, ScreenSize):
        """Initializes CameraRig using the screen size (as a tuple)."""
        # should be updated if the screen gets resized
        self.ScreenSize = ScreenSize
        self.ScreenCenterDisplacement = (ScreenSize[0]/2, ScreenSize[1]/2)


    def get_screen(self, real_coords=np.array([0,0])):
        """Returns Screen coordinates from Real coordinates"""
        CameraPosition = self.get_camera_position()
        ScreenX = self.ScreenCenterDisplacement[0] + self.CameraZoom*(real_coords[0]-CameraPosition[0])
        ScreenY = self.ScreenCenterDisplacement[1] - self.CameraZoom*(real_coords[1]-CameraPosition[1])
        return (ScreenX, ScreenY)


    def get_real(self, screen_coords=(0,0)):
        """Returns the Real coordinates from Screen coordinates."""
        CameraPosition = self.get_camera_position()
        RealX = (screen_coords[0] - self.ScreenCenterDisplacement[0])/self.CameraZoom + CameraPosition[0]
        RealY = -(screen_coords[1] - self.ScreenCenterDisplacement[1])/self.CameraZoom + CameraPosition[1]
        return np.array([RealX, RealY])


    ########################    Follow a planet code


    def set_focus(self, Planet):
        """Sets focus to a planet, without changing the current view."""
        # Remember, CameraPosition = PanPosition + OriginPosition (which is Planet.position)
        # We want to update PanPosition in such a way as to keep CamerPosition the same.
        self.FocusPlanet = Planet
        self.PanPosition = self.PanPosition - Planet.position
        self.FollowingPlanet = True


    def end_focus(self):
        self.FollowingPlanet = False
        if self.FocusPlanet:
            self.PanPosition = self.PanPosition + self.FocusPlanet.position
        self.FocusPlanet = False

 
    ########################    Pan & Zoom code


    def get_camera_position(self):
        CameraPosition = self.PanPosition + (self.FocusPlanet.position if self.FollowingPlanet else np.array([0,0]))
        return CameraPosition


    def pan(self, rel):
        # pans the camera, given the event.rel of a MouseMove event
        self.PanPosition = self.PanPosition + np.array([-rel[0], rel[1]])/self.CameraZoom


    def zoom(self, scaleDelta):
        # zooms the camera. Input is a linear zoom, which is changed to a multiplicative one
        self.CameraZoomLinear += scaleDelta
        self.CameraZoom = 10**self.CameraZoomLinear


#################################################
#################################################
#################################################



class Planet():
    """
    Planet Class - represents a planet in the simulation.
    """
    position = np.array([0,0])
    velocity = np.array([0,0])
    force = np.array([0,0])
    mass = 1.0
    radius = 1.0
    color = (170,120,40)
    outline_color = (0,0,0)
    CurrentNumber = 0
    Selected = False

    def __init__(self, position=np.array([0,0]), velocity=np.array([0,0]), radius=1, mass=1):
        super().__init__()
        self.position = position
        self.velocity = velocity
        self.radius = radius
        self.mass = mass
        self.CurrentNumber = self.CurrentNumber
        Planet.CurrentNumber += 1
    
    def __repr__(self):
        return f"Planet object ({self.CurrentNumber})"
    
    def __str__(self):
        return f"Planet {self.CurrentNumber}, position=({self.position[0]},{self.position[1]}), velocity=({self.velocity[0]},{self.velocity[1]})"
    
    def distance_to_center(self, position):
        dist = np.sqrt(((self.position - position)**2).sum())
    
    def in_bounds(self, position):
        dist2 = ((self.position - position)**2).sum()
        is_in = (self.radius**2 > dist2)
        return is_in

    def select(self):
        self.Selected = True
        self.outline_color = (255,255,255)

    def deselect(self):
        self.Selected = False
        self.outline_color = (0,0,0)

    def draw(self, Surface, CameraRig):
        PlanetScreenPosition = CameraRig.get_screen(self.position)
        ImageRadius = (self.radius)*(CameraRig.CameraZoom)
        pygame.draw.circle(Surface, self.color, PlanetScreenPosition, ImageRadius)
        pygame.draw.circle(Surface, self.outline_color, PlanetScreenPosition, ImageRadius, int(np.ceil(0.03*ImageRadius)))

#################################################
#################################################
#################################################

highlight_upperright_default = np.array([[7,10],[10,10],[10,7],[9,7],[9,9],[7,9]])/10

class PlanetList():
    """
    Object to hold the list of planets.
    When a planet is created via new_planet(), it gets a number which the Planet stores.
    The Planets are stored in the dict List, under their Number
    """

    defaultRadius = 1
    defaultMass = 100

    List = {} # dict of planets
    SelectionActive = False
    CurrentSelection = 0
    MovingVector = False
    MovingPlanet = False
    EditingText = False
    TimeFlowing = False
    #   -is time flowing?
    Arrow = []
    Camera = []
    Surface = []
    TextList = []
    #   -time to get used to assignments actually pointing to objects instead of copying them...

    NewtonG = 10
    #   -Newton's gravitational constant, for gravity calculations

    
    ModDict = {"Neutral":4096, "LShift":4097, "LCtrl":4160, "LAlt":4352, "LShift+LCtrl":4161}
    #   -just here for convenience when dealing with modifier keys

    highlight_color = (255,255,0)
    highlight_upperright = np.array([[7,10],[10,10],[10,7],[9,7],[9,9],[7,9]])/10
    highlight_upperleft = -np.matmul(np.array([[7,10],[10,10],[10,7],[9,7],[9,9],[7,9]])/10, np.array([[0,-1],[1,0]]))
    highlight_lowerleft = -np.array([[7,10],[10,10],[10,7],[9,7],[9,9],[7,9]])/10
    highlight_lowerright = np.matmul(np.array([[7,10],[10,10],[10,7],[9,7],[9,9],[7,9]])/10, np.array([[0,-1],[1,0]]))

    
    ########################    init


    def __init__(self, Surface, CameraRig):
        self.Surface = Surface
        self.Camera = CameraRig
        self.Arrow = VectArrow(Surface, CameraRig)
        TextPos0 = (10, CameraRig.ScreenSize[0] - 30)
        TextPos1 = (10, CameraRig.ScreenSize[1] - 60)
        self.TextList = [TextHandler(TextPos0, 'M='), TextHandler(TextPos1, 'R=')]
        

    ########################    New Planets


    def new_planet(self, position=np.array([0,0]), velocity=np.array([0,0]), radius=1, mass=100):
        NewPlanet = Planet(position=position, velocity=velocity, radius=radius, mass=mass)
        self.List[NewPlanet.CurrentNumber] = NewPlanet
        return NewPlanet.CurrentNumber


    ########################    Handle Clicks
    

    def handle_click_1(self, ScreenPosition):
        """
        Given the position of a click:
        -Check the Planets to see if the position was inside of one of the circles.
        -Or, check the text boxes to see if we're editing text / deselecting the text boxes.
        """
        IsClicked = False
        if not self.SelectionActive:
            ClickRealPosition = self.Camera.get_real(ScreenPosition)
            for PlanetNum in reversed(self.List):
                # we reverse the list so that it prefers the planets drawn on top
                IsClicked = self.List[PlanetNum].in_bounds(position=ClickRealPosition)
                if IsClicked:
                    self.select(PlanetNum)
                    break
        else: # Selection is Active
            BoxSelected = [box.handle_click(ScreenPosition) for box in self.TextList]
            if not any(BoxSelected):
                ClickRealPosition = self.Camera.get_real(ScreenPosition)
                self.set_velocity(ClickRealPosition)


        return self.SelectionActive, self.CurrentSelection
    

    def select(self, PlanetNum):
        """
        Handles selecting a planet by PlanetNum, and changing selection.
        """
        self.SelectionActive = True
        self.CurrentSelection = PlanetNum
        self.TimeFlowing = False
        self.List[PlanetNum].select()
        PlanetMass = self.List[PlanetNum].mass
        PlanetRadius = self.List[PlanetNum].radius
        self.TextList[0].set_default_text(str(PlanetMass))
        self.TextList[1].set_default_text(str(PlanetRadius))


    def deselect(self):
        """
        Handles deselecting *any* planet, not just swapping focus.
        """
        self.SelectionActive = False
        self.CurrentSelection = 0
        # Time does not automatically resume
        for planetnum in self.List:
            self.List[planetnum].deselect()
        for box in self.TextList:
            box.deselect()
        return self.SelectionActive, self.CurrentSelection
    


    def set_velocity(self, RealPosition):
        """
        Given the RealPosition of a click, set the Velocity of the selected planet
        """
        if self.SelectionActive:
            # Find velocity, i.e. displacement of click from planet center:
            CurrentPlanet = self.List[self.CurrentSelection]
            Displacement = RealPosition - CurrentPlanet.position
            CurrentPlanet.velocity = Displacement*self.Camera.VelocityRatio
            #Arrow.set_spine_from_Real(CurrentPlanet.velocity)
    

    def handle_click_3(self, ScreenPosition):
        """
        Given the position of a right click:
        -Check the Planets to see if the position was inside of one of the circles.
            -If so, set the camera to focus on that planet.
            -If not, defocus the camera.
        """
        IsClicked = False
        ClickRealPosition = self.Camera.get_real(ScreenPosition)
        self.Camera.end_focus()
        for PlanetNum in reversed(self.List):
            # we reverse the list so that it prefers the planets drawn on top
            IsClicked = self.List[PlanetNum].in_bounds(position=ClickRealPosition)
            if IsClicked:
                self.Camera.set_focus(self.List[PlanetNum])
                break


    ########################    Handle keys


    def handle_keydown(self, event, KeyMods):
        """
        Handles any time a key press would affect the Planets
        """

        if event.key == pygame.K_ESCAPE:
            self.deselect()

        elif self.Is_Editing_Text():
            UpdateNumber, X = self.handle_text(event)
            if UpdateNumber:
                self.update_attribute(X)
                self.deselect_text_boxes()

        elif event.key == pygame.K_SPACE:
            self.ToggleTime()

    def update_attribute(self, Value):
        if self.TextList[0].TextBoxSelected == True:
            self.List[self.CurrentSelection].mass = Value
        elif self.TextList[1].TextBoxSelected == True:
            self.List[self.CurrentSelection].radius = Value

    def handle_text(self, event):
        """
        Handle passing text into the text boxes.
        This is the only reason (so far) that the selection screen would respond to keyboard input
        """
        UpdateNumber = False
        X = 0
        for box in self.TextList:
            if box.TextBoxSelected:
                UpdateNumber, X = box.handle_text(event)
        
        return UpdateNumber, X

    def deselect_text_boxes(self):
        [box.deselect() for box in self.TextList]

    def Is_Editing_Text(self):
        """
        Checks whether text is currently being edited.
        I prefer this to an "EditingText" variable, because this cannot possibly get out of sync with what's actually happening.
        """
        return any([box.TextBoxSelected for box in self.TextList])


    ########################    Physics code


    def ToggleTime(self):
        """
        Toggles time on or off.
        """
        self.TimeFlowing = not self.TimeFlowing
        if self.SelectionActive:
            self.deselect()


    def Time_Step(self, dt, iterations = 10):
        """
        Handles stepping forward time by a time interval of "dt".
        Splits "dt" into "iterations" timesteps and does it that many times.
        """
        IntervalDt = dt/iterations
        for steps in range(0,iterations):
        # zero out the forces
            for PlanetNum in self.List:
                self.List[PlanetNum].force = 0
            # calculate the forces
            self.Calculate_gravity(self.List, self.Gravity_force_Newton, self.NewtonG)
            # calculate new vel/pos
            for PlanetNum in self.List:
                PlanetObj = self.List[PlanetNum]
                PlanetObj.position, PlanetObj.velocity = self.Time_step_kinematic(PlanetObj.position, PlanetObj.velocity, PlanetObj.mass, PlanetObj.force, IntervalDt)
            # the Planets' positions and velocities are now updated


    # these two probably should be full functions, not methods, but whatever...
    def Time_step_kinematic(self, position =np.array([0,0]), velocity =np.array([0,0]), mass =1, force =np.array([0,0]), dt =0.01):
        # basic numerical integration
        acceleration = force/mass
        position = position + velocity*dt + 0.5*acceleration*dt*dt
        velocity = velocity + acceleration*dt
        return position, velocity


    def Gravity_force_Newton(self, OriginPosition =np.array([0,0]), AttractingBodyPosition =np.array([1,0]), M1 =1, M2 =1):
        # returns normalized force of gravity from Newton = \hat{r}*M1*M2/r**2; must multiply by G
        # force applied to OriginPosition; force _of_ AttractingBodyPosition _on_  OriginPosition
        # vect(force) = unitvec(dr)*G*m1*m2/r**2 = vec(r)*G*m1*m2/r**3 = vec(r)*G*m1*m2/
        dr = AttractingBodyPosition - OriginPosition
        ForceOverG = dr*M1*M2/np.sqrt(sum(dr**2)**3)
        return ForceOverG


    def Calculate_gravity(self, List, Gravity_Force, NewtonG):
        for PlanetPairNums in combinations(List,2):
            PlanetPair = (List[PlanetPairNums[0]], List[PlanetPairNums[1]])
            ForceVec = Gravity_Force(PlanetPair[0].position, PlanetPair[1].position, PlanetPair[0].mass, PlanetPair[1].mass)
            PlanetPair[0].force = PlanetPair[0].force + ForceVec
            PlanetPair[1].force = PlanetPair[1].force - ForceVec
    


    ########################    Code for Drawing stuff
    

    def draw(self):
        DrawList = []
        for PlanetNum in self.List:
            DrawList.append(self.List[PlanetNum].draw(Surface=self.Surface, CameraRig=self.Camera))
            #   -draws planet, then appends the DrawTuple to DrawList (for debugging purposes)
        if self.SelectionActive:
            CurrentPlanet = self.List[self.CurrentSelection]
            self.Arrow.set_real_vector(CurrentPlanet.position, CurrentPlanet.velocity/self.Camera.VelocityRatio)
            self.Arrow.draw()
            for box in self.TextList:
                box.draw(self.Surface)
        return DrawList


    def highlight_screen_position(self, coords_in):
        """This should not be called if we are not following a planet."""
        real_coords = self.Camera.FocusPlanet.radius*coords_in + self.Camera.FocusPlanet.position
        screen_coords = []
        for position in real_coords:
            screen_coords.append(self.Camera.get_screen(position))
        return screen_coords

    def draw_highlight(self):
        if self.Camera.FollowingPlanet:
            pygame.draw.polygon(self.Surface, self.highlight_color, self.highlight_screen_position(self.highlight_upperright))
            pygame.draw.polygon(self.Surface, self.highlight_color, self.highlight_screen_position(self.highlight_upperleft))
            pygame.draw.polygon(self.Surface, self.highlight_color, self.highlight_screen_position(self.highlight_lowerright))
            pygame.draw.polygon(self.Surface, self.highlight_color, self.highlight_screen_position(self.highlight_lowerleft))


#################################################
#################################################
#################################################


class TimeIndicator():
    # Just a little circle at the top-left, indicating time flow

    centerOffset = (-50,50)
    radius = 30
    GoColor = (0,255,0)
    StopColor = (255,0,0)
    BLACK = (0,0,0)
    Screensize = (500,500)
    center = (0,0)

    def __init__(self, ScreenSize=(500,500)):
        self.ScreenSize = ScreenSize
        self.center = (ScreenSize[0] + self.centerOffset[0], self.centerOffset[1])



    def draw(self, Surface, TimeFlowing):
        if TimeFlowing:
            #Surface.blit(self.GoImage, self.Center)
            pygame.draw.circle(Surface, self.GoColor, self.center, self.radius)
            pygame.draw.circle(Surface, self.BLACK, self.center, self.radius, 4)
        else:
            #Surface.blit(self.StopImage, self.Center)
            pygame.draw.circle(Surface, self.StopColor, self.center, self.radius)
            pygame.draw.circle(Surface, self.BLACK, self.center, self.radius, 4)


#################################################
#################################################
#################################################


class TextHandler():
    """
    Represents a white box on-screen. Has RootText such as "R=", and takes keyboard input.
    If the input is a float, it converts it into a float and passes it out.
    """
    TextBoxSelected = False
    InputRect = []
    BaseFont = []
    TextDisplacement = (3,0)
    RootText = 'R='
    #   -the prompt for the input
    InputText = ''
    #   -what the user is editing
    DefaultInputText = ''
    #   -never written to the surface; only used to reset InputText
    BorderColor = (0,0,0)
    TextColor = (0,0,0)
    FillColor = (255,255,255)


    def __init__(self, TopLeftPosition=(20,20), RootText='R=', DefaultInputText=''):
        pygame.font.init()
        #   -this can be called more than once, but _needs_ to be called before we create the Font object.
        #   can cause serious problems for unknown reasons...
        self.BaseFont = pygame.font.Font(None, 32)
        self.InputRect = pygame.Rect(TopLeftPosition[0], TopLeftPosition[1], 200, 20)
        self.RootText = RootText
        self.DefaultInputText = DefaultInputText
        self.TextPos = (self.InputRect[0]+self.TextDisplacement[0], self.InputRect[1]+self.TextDisplacement[1])
    
    def __del__(self):
        pass
    
    def __str__(self):
        return "TextHandler object."


    def set_text(self, TextIn):
        self.InputText = TextIn
    
    def set_default_text(self, TextIn):
        """
        Sets both DefaultInputText and InputText to TextIn
        """
        self.DefaultInputText = TextIn
        self.InputText = TextIn


    def select(self):
        self.TextBoxSelected = True


    def deselect(self):
        self.TextBoxSelected = False


    def handle_click(self, pos):
        if self.InputRect.collidepoint(pos):
            self.select()
            return True
        else:
            self.deselect()
            return False


    def handle_text(self, event):
        UpdateNumber = False
        X = 0
        if event.key == pygame.K_BACKSPACE:
            self.InputText = self.InputText[:-1]
        elif (event.key == pygame.K_RETURN) or (event.key == pygame.K_KP_ENTER):
            UpdateNumber, X = self.on_return()
        else:
            self.InputText += event.unicode
            #   -mod keys like "CTRL" and "SHIFT" have an empty unicode string
        return UpdateNumber, X


    def test_text(self):
        try:
            X = float(self.InputText)
            print(f"number = {self.InputText}")
        except:
            print("Text is not a number.")
    

    def on_return(self):
        SuccessIndicator = False
        X = 0
        try:
            X = float(self.InputText)
            SuccessIndicator = True
            self.DefaultInputText = str(X)
            return SuccessIndicator, X
        except:
            self.InputText = self.DefaultInputText


    def draw(self, Surface):
        pygame.draw.rect(Surface, self.FillColor, self.InputRect, width=0)
        #pygame.draw.rect(Surface, self.BorderColor, self.InputRect, width=5)
        TextSurface = self.BaseFont.render((self.RootText + self.InputText + ('|' if self.TextBoxSelected else '')), True, self.TextColor)
        Surface.blit(TextSurface, self.TextPos)


#################################################
#################################################
#################################################


class TextListHandler():
    """
    Handles printing info text in the top-left corner of the screen.
    We first get a bunch of different strings that we want to print out.
    We then place them into lists which are triggered by a state (focused, selected, etc.).
    Then, we print the text in the list based on state, giving a fixed amount of room between them.
    """
    BaseFont = []
    BLACK = (0,0,0)
    WHITE = (255,255,255)
    TextHorizontal = 5
    #   -Distance from the left side of the screen, in pixels
    TextVertical = 5
    #   -Distance from the top of the screen to the top text, in pixels
    TextDeltaY = 15
    #   -Distance between centers of the text lines
    TextColor = WHITE
    #   -The color of the text

    Instruction_Pan = "Hold middle-mouse button to pan."
    Instruction_Select = "Left-click on a planet to select it and edit its properties."
    Instruction_Create = "Press ctrl + left-click to create a new planet."
    Instruction_Follow = "Right-click on a planet to follow it."
    Instruction_SetVelocity = "Left-click to set the planet's velocity"
    Instruction_Deselect = "Press Esc to return."
    Instruction_TimeToggle = "Press space to toggle time on/off."
    Instruction_TimeAndDeselect = "Press space to deselect and toggle time on."

    List_Neutral = [Instruction_Pan, Instruction_TimeToggle, Instruction_Create, Instruction_Select, Instruction_Follow]
    List_Selected = [Instruction_Pan, Instruction_TimeAndDeselect, Instruction_SetVelocity, Instruction_Deselect]

    TextDict = {"Neutral":List_Neutral, "Selected":List_Selected}

    def __init__(self):
        pygame.font.init()
        #   -this can be called more than once, but _needs_ to be called before we create the Font object.
        #   can cause serious problems for unknown reasons...
        self.BaseFont = pygame.font.Font(None, 20)

    def draw(self, Surface, KeyWord):
        TextList = self.TextDict[KeyWord]
        CurrentNum = 0
        for text in TextList:
            TextSurface = self.BaseFont.render(text, True, self.TextColor)
            Surface.blit(TextSurface, (self.TextHorizontal, self.TextVertical + self.TextDeltaY*CurrentNum))
            CurrentNum += 1


#################################################
#################################################
#################################################


class VectArrow():
    # Flat tail:
    #base_coords = np.array([[1,0],[1,7],[2,7],[0,11],[-2,7],[-1,7],[-1,0]])/11

    # Pointy tail:
    base_coords = np.array([[0,0],[1,7],[2,7],[0,11],[-2,7],[-1,7]])/11
    
    def __init__(self, SURF, Camera, Velocity=np.array([1,0]), color=(200,50,50)):
        self.SURF = SURF
        self.Camera = Camera
        self.color = color
        self.scale = 1
        self.theta = 0
            # tip and tail are screen coords, but stored as numpy arrays
        self.tail = np.array([0,0])
        self.tip = self.tail + Velocity
    

    def align_to_points(self):
        """Finds rotation/scale/displacement so that the arrow points from self.tail to self.tip."""
        self.theta = ppl_atan(self.tip-self.tail)
        self.scale = np.sqrt(((self.tip-self.tail)**2).sum())
    

    def set_real_vector(self, real_tail, real_displacement):
        self.tail = np.array(self.Camera.get_screen(real_tail))
        self.tip = np.array(self.Camera.get_screen(real_tail + real_displacement))
        

    def draw(self):
        self.align_to_points()
        arrow_coords = self.scale*np.matmul(self.base_coords,rot_mat(self.theta-np.pi/2)) + self.tail
        pygame.draw.polygon(self.SURF, self.color, numpy_to_tuples(arrow_coords))


#################################################
#################################################
#################################################


def main(ScreenSize=(500,500)):

    #static Stuff:
    ModDict = {"Neutral":4096, "LShift":4097, "LCtrl":4160, "LAlt":4352, "LShift+LCtrl":4161}

    #   Screen stuff:
    FPS = 60
    BGColor = (55,55,55)

    pygame.init()
    DISPLAYSURF = pygame.display.set_mode(ScreenSize)
    DISPLAYSURF.fill(BGColor)
    logo = pygame.image.load("./Planets.ico")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("!!! Planets !!!")
    pygame.display.update()

    Camera = CameraRig(ScreenSize)
    CameraZoomScrollRatio = 0.10    # when zooming, each scroll scales the picture by this much
    CameraZoomButtonRatio = 0.02    # when zooming, each tick with button held will scale the picture by this much
    
    TimeLight = TimeIndicator(ScreenSize)
    TextListObj = TextListHandler()

    mainPlanetList = PlanetList(DISPLAYSURF, Camera)
    mainPlanetList.new_planet(position=np.array([0,0]))

    dt = 1/FPS
    #print(dt)


    FINISHED = False
    while True:

        PressedKeys = pygame.key.get_pressed()
        PressedMods = pygame.key.get_mods()

        # Do the physics:
        if mainPlanetList.TimeFlowing:
            mainPlanetList.Time_Step(dt)

        # Handle held buttons:
        if not mainPlanetList.Is_Editing_Text():
            if PressedKeys[pygame.K_3]:
                #   zoom in
                Camera.zoom(CameraZoomButtonRatio)
            elif PressedKeys[pygame.K_4]:
                #   zoom out
                Camera.zoom(-CameraZoomButtonRatio)

        # Handle events:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                FINISHED = True
                break

            # Panning: check MouseMotion with button = (0,1,0):
            elif event.type == pygame.MOUSEMOTION:
                if (event.buttons == (0,1,0)) or ((event.buttons == (1,0,0)) and PressedMods == ModDict["LShift"]):
                    Camera.pan(event.rel)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                
                if event.button == 1:
                    #   left click
                    
                    #   if LCtrl is pressed, create a new planet:
                    if PressedMods == ModDict["LCtrl"]:
                        #   create new planet
                        ClickRealPosition = Camera.get_real(event.pos)
                        CNum = mainPlanetList.new_planet(position=ClickRealPosition)
                        #print(CNum)

                    elif PressedMods == ModDict["Neutral"]:
                        #   try to select object
                        CSelected, CNum = mainPlanetList.handle_click_1(ScreenPosition=event.pos)
                        #print(CNum)
                
                elif event.button ==2:
                    #   middle click
                    pass

                elif event.button == 3:
                    #   right click
                    mainPlanetList.handle_click_3(ScreenPosition=event.pos)

                elif event.button == 4:
                    #   scroll up - zoom in
                    Camera.zoom(CameraZoomScrollRatio)
                    #   Maybe one day, scale the image around the mouse position?

                elif event.button == 5:
                    #   scroll down - zoom out
                    Camera.zoom(-CameraZoomScrollRatio)
                
            elif event.type == pygame.KEYDOWN:
                mainPlanetList.handle_keydown(event, PressedMods)

        if FINISHED:
            break

        # Do the physics:



        TextCurrent = "Neutral"
        if mainPlanetList.SelectionActive:
            TextCurrent = "Selected"

        # render the result:
        DISPLAYSURF.fill(BGColor)
        mainPlanetList.draw()
        mainPlanetList.draw_highlight()
        TimeLight.draw(DISPLAYSURF, mainPlanetList.TimeFlowing)
        TextListObj.draw(DISPLAYSURF, TextCurrent)
        pygame.display.update()
        pygame.time.Clock().tick(FPS)

#################################################
#################################################
#################################################