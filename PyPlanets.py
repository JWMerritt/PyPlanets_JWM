"""
This is the resource file for the Planets game that I'm trying to make in python.
"""

"""
Pseudocode:
    What we want:
        planets
            little circles with color, radius, and mass
        the ability to click on them and graphically change their velocity, position
            clicking on a planet opens UI
            An arrow comes up, and right clicking will place the vector at the mouse
            A circle comes up, and left-clicking will let you drag it around
        the ability to zoom and scroll
            scroll scrolls
            clicking the scroll button and dragging will pan the screen
        stop/start on space
        physics
            customizable force dropoff

    Classes:
        planet:
            holds info on radius, color, mass, position, velocity
            method for moving the planet a time step based on total forces applied
        UI:
            class for handling UI. When clicking on a planet, brings up pan, velocity arrow
        window init:
            handles default window size, background color
        physics engine:
            runs every frame. 
            for planet in Planets:
                Find forces on all from all
                *then* move them all at once, using Newton
            physics will be applied *to* planets, instead of planets moving themselves
        Coordinates function:
            a function to convert between screen coords and world coords
            takes into account the zoom and pan of the screen

"""

import pygame
import numpy as np
from itertools import combinations

"""
Gotta set up code for switching between "Real" coords and "Screen" coords
Master equations:
        ImagePosition = position offset and scaled, with origin at center of screen
    ImagePosition[x] = CameraZoom*(RealPosition[x] - CameraPosition[x])
    ImagePosition[y] = CameraZoom*(RealPosition[y] - CameraPosition[y])
        ScreenPosition = position on screen drawn to, measured from top-right of the screen
        ScreenDisplacement = center of screen (= origin of ImagePosition) measured from screen coordinates
    ScreenPosition[x] = ScreenDisplacement[x] + ImagePosition[x]
    ScreenPosition[y] = ScreenDisplacement[y] - ImagePosition[y]
        Therefore:
    ScreenPosition[x] = ScreenDisplacement[x] + CameraZoom*(RealPosition[x] - CameraPosition[y])
    ScreenPosition[y] = ScreenDisplacement[y] - CameraZoom*(RealPosition[y] - CameraPosition[y])
"""

class CameraRig():
    """
    Contains details of camera position / zoom, and useful functions
    """

    #   Zoom stuff:
    CameraPosition = np.array([0,0])
    #   -This is the real-space displacement vector from real-origin to screen-center-origin
    PanPosition = np.array([0,0])
    #   -This is the real-space displacement vector that we get from the user panning the screen
    FocusPosition = np.array([0,0])
    #   -This is the real-space center of the planet we're following
    CameraZoom = 10    
    #   -At CZ=1, one real unit is equal to one pixel. Larger zooms => farther out
    #       RealDistance*CameraZoom = ScreenDistance
    CameraZoomLinear = 1    
    #   -The CameraZoom will be 10**CameraZoomLinear
    ScreenSize = (500,500)
    #   -Size of the screen, in pixels
    ScreenDisplacement = (250,250)
    #   -This is the displacement of the screen-center from the top-left corner of the box.
    VelocityRatio = 1
    #   -When showing / changing a Planet's velocity on-screen, the actual
    #       velocity will be what's shown, times this factor.
    FollowingPlanet = False
    #   -Is the camera following a planet?
    FocusPlanet = False
    #   -The planet we're focused on.


    ########################    Initialization code


    def __init__(self, ScreenSize):
        # initializes CameraRig using the screen size (as a tuple)
        # should be updated if the screen gets resized
        self.ScreenSize = ScreenSize
        self.ScreenDisplacement = (ScreenSize[0]/2, ScreenSize[1]/2)


    ########################    Conversion code


    def get_Screen(self, coords=np.array([0,0])):
        #given the real coords, find the image coords
        CameraPosition = self.CameraPosition()
        ScreenX = self.ScreenDisplacement[0] + self.CameraZoom*(coords[0]-CameraPosition[0])
        ScreenY = self.ScreenDisplacement[1] - self.CameraZoom*(coords[1]-CameraPosition[1])
        return (ScreenX, ScreenY)


    def get_Real(self, coords=(0,0)):
        #given the image coords, find the real coords
        CameraPosition = self.CameraPosition()
        RealX = (coords[0] - self.ScreenDisplacement[0])/self.CameraZoom + CameraPosition[0]
        RealY = -(coords[1] - self.ScreenDisplacement[1])/self.CameraZoom + CameraPosition[1]
        return np.array([RealX, RealY])


    ########################    Follow a planet code


    def set_focus(self, Planet):
        """
        Sets focus to a planet, without changing the current view.
        CameraPosition = PanPosition + Planet.Position
        """
        self.FocusPlanet = Planet
        self.PanPosition = self.PanPosition - Planet.position
        self.FollowingPlanet = True


    def end_focus(self):
        self.FollowingPlanet = False
        if self.FocusPlanet:
            self.PanPosition = self.PanPosition + self.FocusPlanet.position
        self.FocusPlanet = False



    ########################    Pan & Zoom code


    def CameraPosition(self):
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
    Planet Class - represents planet in the simulation
    methods:
        draw(self, Surface, CameraPosition, CameraZoom, ScreenDisplacement):
            Draws planet to Surface, given CameraRig data
    """
    position = np.array([0,0])
    velocity = np.array([0,0])
    force = np.array([0,0])
    mass = 1.0
    radius = 1.0
    color = (170,120,40)
    CurrentNumber = 0

    def __init__(self, position=np.array([0,0]), velocity=np.array([0,0]), radius=1, mass=1):
        super().__init__()
        #self.image = pygame.image.load("C:/Users/jmerr/Documents/Python/Fun/Practice_pygame/Images/PlanetBasic.png")
        #self.rect = self.image.get_rect()
        #self.rect.center = position
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

    def draw(self, Surface, CameraRig):
        PlanetScreenPosition = CameraRig.get_Screen(self.position)
        ImageRadius = (self.radius)*(CameraRig.CameraZoom)
        pygame.draw.circle(Surface, self.color, PlanetScreenPosition, ImageRadius)
        pygame.draw.circle(Surface, (0,0,0), PlanetScreenPosition, ImageRadius, int(np.ceil(0.03*ImageRadius)))

#################################################
#################################################
#################################################

class PlanetList():
    """
    Object to hold the list of planets.
    When a planet is created via new_planet(), it gets a number which the Planet stores.
    The Planets are stored in the dict List, under their Number
    """

    List = {}
    #   -dict of planets
    SelectionActive = False
    #   -do we have a planet selected?
    CurrentSelection = 0
    #   -ID of currently selected planet
    MovingVector = False
    #   -are we dragging around the velocity arrow?
    MovingPlanet = False
    #   -are we dragging around the planet?
    EditingText = False
    #   -are we editing one of the text fields?
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

    ########################    init


    def __init__(self, Surface, CameraRig):
        self.Surface = Surface
        self.Camera = CameraRig
        self.Arrow = VectArrow(Surface, CameraRig)
        TextPos0 = (10, CameraRig.ScreenSize[0] - 30)
        TextPos1 = (10, CameraRig.ScreenSize[1] - 60)
        self.TextList = [TextHandler(TextPos0, 'M='), TextHandler(TextPos1, 'R=')]
        

    ########################    New Planets


    def new_planet(self, position=np.array([0,0]), velocity=np.array([0,0]), radius=1, mass=1):
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
            ClickRealPosition = self.Camera.get_Real(ScreenPosition)
            for PlanetNum in reversed(self.List):
                # we reverse the list so that it prefers the planets drawn on top
                IsClicked = self.List[PlanetNum].in_bounds(position=ClickRealPosition)
                if IsClicked:
                    self.select(PlanetNum)
                    break
        else: # Selection is Active
            BoxSelected = [box.handle_click(ScreenPosition) for box in self.TextList]
            if not any(BoxSelected):
                ClickRealPosition = self.Camera.get_Real(ScreenPosition)
                self.set_Velocity(ClickRealPosition)


        return self.SelectionActive, self.CurrentSelection
    

    def select(self, PlanetNum):
        """
        Handles selecting a planet by PlanetNum, and changing selection.
        """
        self.SelectionActive = True
        self.CurrentSelection = PlanetNum
        self.TimeFlowing = False
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
        for box in self.TextList:
            box.deselect()
        return self.SelectionActive, self.CurrentSelection
    


    def set_Velocity(self, RealPosition):
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
        ClickRealPosition = self.Camera.get_Real(ScreenPosition)
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
            self.Arrow.set_vector_from_RealP_RealD(CurrentPlanet.position, CurrentPlanet.velocity/self.Camera.VelocityRatio)
            self.Arrow.draw()
            for box in self.TextList:
                box.draw(self.Surface)
        return DrawList


#################################################
#################################################
#################################################


class TimeIndicator():
    # just a little circle at the top-left, indicating time flow
    # is a class in order to load the images only once, and store them in the object
    #GoImage = pygame.image.load("C:/Users/jmerr/Documents/Python/Fun/Practice_pygame/Images/TimeIndicator_Go.png")
    #StopImage = pygame.image.load("C:/Users/jmerr/Documents/Python/Fun/Practice_pygame/Images/TimeIndicator_Stop.png")
    #Rect = GoImage.get_rect()
    #Size = Rect[2:4]
    #Center = (Size[0]/2, Size[1]/2)

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
    Verbose = False
    #   -activates debug outputs

    Image = pygame.image.load("C:/Users/jmerr/Documents/Python/Fun/Practice_pygame/Images/VelocityArrow.png")
    #   -expects an image of an arrow pointing to the right
    ImageLength = 150
    ImageWidth = 50

    ImageWarped = Image
    #   -the transformed image that will actually be rendered to the screen

    RealSpine = np.array([0,0])
    #   -vector going from tail (origin) to tip of arrow
    ImageSpine = np.array([0,0])
    #   -spine in Image space
    DrawScale = 1
    #   -How much the arrow's image needs to be scaled
    Angle = 0
    #   -In degrees. Should be between 180 and -179.99
    RealOrigin = np.array([0,0])
    #   -RealCoordinates of arrow origin
    ImageOrigin = np.array([0,0])
    #   -arrow origin *in Screen space* !
    Surface = []
    Camera = []

    ##############################

    def __init__(self, Surface, CameraRig, Velocity=np.array([1,0]), debug=False, ImagePath="C:/Users/jmerr/Documents/Python/Fun/Practice_pygame/Images/VelocityArrowDebug.png", Verbose=False):
        if debug:
            self.Image = pygame.image.load(ImagePath)
        else:
            self.Image = pygame.image.load("C:/Users/jmerr/Documents/Python/Fun/Practice_pygame/Images/VelocityArrow.png")
        
        self.Surface = Surface
        self.Camera = CameraRig

        rekt = self.Image.get_rect()
        self.ImageLength, self.ImageWidth = rekt[2], rekt[3]
        
        self.RealSpine = Velocity
        self.ImageSpine = CameraRig.CameraZoom*Velocity
        #   -one unit RealDistance is $CameraZoom pixels/units of ScreenDistance = ImageDistance
        self.Angle, self.DrawScale = self.set_angle_scale(self.ImageSpine, self.ImageLength)
        self.set_warp()


    #############################


    # Real space origin and RealSpine (= velocity) are easy; most of this will be calculating the screen variables
    # Image space will be in Screen scale, with origin at arrow origin, with up being positive y.
    def set_origin(self, RealPosition=np.array([0,0])):
        """
        Sets the Real and Image origin, from a RealPosition.
        Remember that the ImageOrigin is a ScreenPosition - the origin point on the screen.
        We'll put the planet's position into this function.
        """
        self.RealOrigin = RealPosition
        self.ImageOrigin = self.Camera.get_Screen(RealPosition)
        #   -gets position's ScreenPosition

    
    def Screen_to_Image(self, ScreenPosition=(0,0)):
        """ 
        Converts ScreenPosition into ImagePosition.
        We'll put our clicked point into this function.
         """
        ImagePosition = np.array(ScreenPosition) - self.ImageOrigin     # this is still a ScreenPosition
        ImagePosition[1] = -ImagePosition[1]                            # This is now an ImagePosition
        return ImagePosition

    
    def Image_to_Screen(self, ImagePosition=np.array([0,0])):
        """
        Converts ImagePosition to ScreenPosition.
        We'll put the final result for the image's top-left corner into this function.
        NOTE: returns np.array() object, not the tuple usually used for ScreenPositions
        """
        ImPos = ImagePosition   # this is an ImagePosition
        ImPos[1] = -ImPos[1]    # this is the corresponding ScreenPosition
        ScreenPosition = self.ImageOrigin + ImPos
        return ScreenPosition

    
    def Real_to_Image(self, RealPosition=np.array([0,0])):
        """
        Converts a RealPosition into an ImagePosition.
        """
        return self.Screen_to_Image(self.Camera.get_Screen(RealPosition))

    
    def set_spine_from_Screen(self, ScreenPosition=(0,0)):
        """
        Given a ScreenPosition, calculate the ImagePosition displacement between it and the ImageOrigin.
        Set this displacement as the Spines.
        """
        self.ImageSpine = self.Screen_to_Image(ScreenPosition)
        self.RealSpine = self.ImageSpine/self.Camera.CameraZoom
        #   -one unit RealDistance is $CameraZoom pixels/units of ScreenDistance = ImageDistance

    
    def set_spine_from_Real(self, RealDisplacement=np.array([0,0])):
        """
        Given a RealDisplacement, set it to RealSpine; and calculate ImageSpine, and set it
        """
        self.RealSpine = RealDisplacement
        self.ImageSpine = self.RealSpine*self.Camera.CameraZoom
        #   -one unit RealDistance is $CameraZoom pixels/units of ScreenDistance = ImageDistance

    
    def set_warp(self):
        self.ImageWarped = pygame.transform.rotozoom(self.Image, self.Angle, self.DrawScale)
        return self.ImageWarped

    
    def get_warp(self):
        return pygame.transform.rotozoom(self.Image, self.Angle, self.DrawScale)


    #####################


    def set_angle_scale(self, ImageSpine, ImageLength):
        """ gives the angle of ImageSpine, between 180 and -179.99"""

        if ImageSpine[0]==0:
            # account for the degenerate cases:
            if ImageSpine[1]>0:
                Angle = 90
            elif ImageSpine[1]<0:
                Angle = -90
            else: # ImageSpine[1]==0
                Angle = 0

        else:
            Angle = np.arctan(ImageSpine[1]/ImageSpine[0])*180/np.pi
            if ImageSpine[0]<0:
                # account for the sign ambiguity:
                if ImageSpine[1]>0:
                    Angle += 180
                elif ImageSpine[1]<0:
                    Angle -= 180
                else: # ImageSpine[1]==0
                    Angle = 180
        
        DrawScale = np.sqrt((ImageSpine**2).sum())/ImageLength
        #   -normalized so that 1 gives the unscaled loaded image

        return Angle, DrawScale

    
    #########################


    def find_tail(self):
        """
        Find center-point displacement vector of the warped image. 
        This is the ImagePosition pointing from the ImageOrigin to the halfway
            point of the short side of the arrow's tail.
        """
        """
        Four cases for the four quadrants.
        We shift the image by ImageBoxDisplacement to get it in the right quadrant, with one corner (nearest the tail) touching the ImageOrigin.
            Since the top-left corner of the image will want to be at the ImageOrigin, it starts in quadrant IV.
            This points from the ImageOrigin to where the top-left corner *should* be
        We then find the CenterPointDisplacement of the center of the arrow's tail relative to the nearest corner of its bounding box.
            This is found by mirroring the ImageSpine across the diagonal of its quadrant, and scaling to make its length half the short side length
                This turns out to be simpler than it looks. Just multiply by M = [0,1;1,0], with a minus sign in quadrants II and IV.
            This points from the ImageOrigin to where the CenterPoint *currently* is, after shifted to the correct quadrant
        This gives us the total CenterPointPosition of the center point of the back of the arrow, relative to the image's top-left point.
            Because of the difference in *currently* and *should*, the position of the CenterPoint when the image is drawn is:
            CenterPointPosition = -ImageBoxDisplacement + CenterPointDisplacement
            This points from the ImageOrigin to where the CenterPoint *currently* is, now, when drawn with top-left corner at ImageOrigin
        We then finally will need to shift the entire image by -CenterPointPosition to bring the center of the tail to the ImageOrigin.
        We choose to use the ImageSpine instead of the Angle because it seems more fundamental, and requires fewer function calls to get/set.
        """

        ImageShortRatio = self.ImageWidth/(2*self.ImageLength) # should be < 1
        #   -ratio of half the short side over the long side
        ImageRect = self.ImageWarped.get_rect()
        #   -ImageRect[2], ImageRect[3] are the length, height of the warped image
        ImX = ImageRect[2]
        ImY = ImageRect[3]

        spine = self.ImageSpine
        M = np.array([[0,1],[1,0]])
        #   -this is the "flip over the diagonal" matrix

        if spine[0]==spine[1]==0:
            # no arrow
            ImageBoxDisplacement = np.array([0,0])
            CenterPointDisplacement = np.array([0,0])
        elif spine[0]>=0:
            # Q-I and Q-IV
            if spine[1]<=0:
                # Q-IV
                ImageBoxDisplacement = np.array([0,0])
                CenterPointDisplacement = -np.matmul(M,self.ImageSpine)*ImageShortRatio
            else: # spine[1]>0
                # Q-I
                ImageBoxDisplacement = np.array([0, ImY])
                CenterPointDisplacement = np.matmul(M,self.ImageSpine)*ImageShortRatio
        else: # spine[0]<0
            # Q-II and Q-III
            if spine[1]<=0:
                # Q-III
                ImageBoxDisplacement = np.array([-ImX,0])
                CenterPointDisplacement = np.matmul(M,self.ImageSpine)*ImageShortRatio
            else: # spine[1]>0
                # Q-II
                ImageBoxDisplacement = np.array([-ImX, ImY])
                CenterPointDisplacement = -np.matmul(M,self.ImageSpine)*ImageShortRatio
        
        CenterPointPosition = CenterPointDisplacement - ImageBoxDisplacement
        return CenterPointPosition

    ######################

    def get_DrawTuple(self):

        CenterPointPosition = self.find_tail()
        #   -this is an ImagePosition
        DrawPosition = self.Image_to_Screen(-CenterPointPosition)
        #   -this is a ScreenPosition, as an np.array.
        #   -already accounts for ImageOrigin offset
        DrawTuple = (DrawPosition[0], DrawPosition[1])

        return DrawTuple, CenterPointPosition

    ######################

    # These are the only methods you should directly call:

    def set_vector_from_Real_Screen(self, RealOriginPosition, ScreenTipPosition):
        """
        Sets both ends of the arrow using a RealPosition (the tail position) and a ScreenPosition (the tip position)
        Should be the planet RealPosition, and the clicked ScreenPosition
        """
        self.set_origin(RealOriginPosition)
        #   -sets RealOrigin and ImageOrigin
        self.set_spine_from_Screen(ScreenTipPosition)
        #   -sets RealSpine and ImageSpine, using CameraRig data
    

    def set_vector_from_RealP_RealD(self, RealOriginPosition, RealDisplacement):
        """
        Sets both ends of the arrow using a RealPosition (the tail position) and a RealPosition (the RealSpine)
        Should be the planet RealPosition, and the velocity RealDisplacement)
        """
        self.set_origin(RealOriginPosition)
        #   -sets RealOrigin and ImageOrigin
        self.set_spine_from_Real(RealDisplacement)
        #   -sets RealSpine and ImageSpine, using CameraRig data

    
    #######################

    def draw(self):
        """
        Draw the vector.
        """
        self.Angle, self.DrawScale = self.set_angle_scale(self.ImageSpine, self.ImageLength)
        self.set_warp()
        DrawTuple = self.get_DrawTuple()

        #   Draw the arrow. The image gets transformed in set_vector_from_Real_Screen(). :
        self.Surface.blit(self.ImageWarped, DrawTuple)

        return DrawTuple


#################################################
#################################################
#################################################

def arrowtest(ScreenSize=(500,500)):
    
    #static Stuff:
    ModDict = {"Neutral":4096, "LShift":4097, "LCtrl":4160, "LAlt":4352, "LShift+LCtrl":4161}

    #   Screen stuff:
    FPS = 60
    BGColor = (55,55,55)
    CameraZoomScrollRatio = 0.10    # when zooming, each scroll scales the picture by this much
    CameraZoomButtonRatio = 0.02    # when zooming, each tick with button held will scale the picture by this much
    Camera = CameraRig(ScreenSize)

    pygame.init()
    DISPLAYSURF = pygame.display.set_mode(ScreenSize)
    DISPLAYSURF.fill(BGColor)
    logo = pygame.image.load("C:/Users/jmerr/Documents/Python/Fun/Excl.ico")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("!!! Arrows !!!")
    pygame.display.update()

    mainPlanetList = PlanetList(DISPLAYSURF, Camera)
    mainPlanetList.new_planet(position=np.array([0,0]), radius=1)

    Arrow = VectArrow(DISPLAYSURF, Camera, Velocity=np.array([1,0]), debug=True)

    FINISHED = False
    while True:
        for event in pygame.event.get():
            #print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                FINISHED = True
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    Arrow.set_vector_from_Real_Screen(np.array([0,0]), event.pos)
        
        if FINISHED:
            break
        
        #####   Render screen

        DISPLAYSURF.fill(BGColor)
        DrawList = mainPlanetList.draw()
        Arrow.draw()
        pygame.display.update()
        pygame.time.Clock().tick(FPS)
        #print(DrawList)


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
    logo = pygame.image.load("C:/Users/jmerr/Documents/Python/Fun/Excl.ico")
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
                        ClickRealPosition = Camera.get_Real(event.pos)
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
        TimeLight.draw(DISPLAYSURF, mainPlanetList.TimeFlowing)
        TextListObj.draw(DISPLAYSURF, TextCurrent)
        pygame.display.update()
        pygame.time.Clock().tick(FPS)

#################################################
#################################################
#################################################