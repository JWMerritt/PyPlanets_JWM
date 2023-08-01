import pygame
import PyPlanets as ppl
import numpy as np

ScreenSize = (500,500)
BGColor = (55,55,55)
FPS = 60

pygame.init()
DISPLAYSURF = pygame.display.set_mode(ScreenSize)
DISPLAYSURF.fill(BGColor)
logo = pygame.image.load("C:/Users/jmerr/Documents/Python/Fun/Excl.ico")
pygame.display.set_icon(logo)
pygame.display.set_caption("Planets Test Lab.")
pygame.display.update()

Camera = CameraRig(ScreenSize)
CameraZoomScrollRatio = 0.10    # when zooming, each scroll scales the picture by this much
CameraZoomButtonRatio = 0.02    # when zooming, each tick with button held will scale the picture by this much

TimeLight = TimeIndicator(ScreenSize)
TextListObj = TextListHandler()

mainPlanetList = PlanetList(DISPLAYSURF, Camera)
mainPlanetList.new_planet(position=np.array([0,0]))

dt = 1/FPS

#arrow_coords = np.array([[200,400],[200,300],[180,300],[220,280],[260,300],[240,300],[240,400]])
arrow_coords = np.array([[1,0],[1,7],[2,7],[0,11],[-2,7],[-1,7],[-1,0]])

def numpy_to_tuples(np_in):
    listout = []
    for point in np_in:
        listout.append( (point[0],point[1]) )
    return listout

def rotmat(theta):
    return np.array([[np.cos(theta), -np.sin(theta)],[np.sin(theta), np.cos(theta)]])


class VectArrow2:
    #base_coords = np.array([[1,0],[1,7],[2,7],[0,11],[-2,7],[-1,7],[-1,0]])/11
    base_coords = np.array([[0,0],[1,7],[2,7],[0,11],[-2,7],[-1,7]])/11
    
    def __init__(self, SURF, Camera, color=(200,50,50)):
        self.SURF = SURF
        self.Camera = Camera
        self.color = color
        self.scale = 1
        self.theta = 0
        self.tail = np.array([0,0])
        self.tip = np.array([1,0])
    
    def atan(self, point):
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

    def align_to_points(self):
        """Finds rotation/scale/displacement so that the arrow points from self.tail to self.tip."""
        self.theta = self.atan(self.tip-self.tail)
        self.scale = np.sqrt(((self.tip-self.tail)**2).sum())
    
    def rot_mat(self, theta):
        return np.array([[np.cos(theta),np.sin(theta)],[-np.sin(theta),np.cos(theta)]])

    def numpy_to_tuples(self, np_in):
        listout = []
        for point in np_in:
            listout.append( (point[0],point[1]) )
        return listout
    
    def click_tip(event_pos):
        self.tip = event_pos
        
    
    def draw(self):
        self.align_to_points()
        arrow_coords = self.scale*np.matmul(self.base_coords,self.rot_mat(self.theta-np.pi/2)) + self.tail
        pygame.draw.polygon(self.SURF, self.color, self.numpy_to_tuples(arrow_coords))


delta_x = np.array([200,400])
turned_vec = 20*(np.matmul(arrow_coords, rotmat(np.pi))) + delta_x
for point in turned_vec:
    pass
    # point += delta_x
vec_coords = numpy_to_tuples(turned_vec)
print(vec_coords)

RUNNING = False

arw = VectArrow(DISPLAYSURF)
arw.tail = np.array([200,400])
arw.tip = np.array([300,300])

while RUNNING:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            RUNNING = False
            break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                arw.tip = np.array(event.pos)
            elif event.button == 3:
                arw.tail = np.array(event.pos)

    DISPLAYSURF.fill(BGColor)
    pygame.draw.circle(DISPLAYSURF, (200,200,200), (200,200), 50)
    #pygame.draw.polygon(DISPLAYSURF, (200,50,50), vec_coords ,0)
    arw.draw()
    pygame.display.update()
    pygame.time.Clock().tick(60)