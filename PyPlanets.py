

import pygame
import numpy as np
from itertools import combinations

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
        """Initializes CameraRig using the screen size (as a tuple)."""
        # should be updated if the screen gets resized
        self.ScreenSize = ScreenSize
        self.ScreenDisplacement = (ScreenSize[0]/2, ScreenSize[1]/2)


    def get_screen(self, real_coords=np.array([0,0])):
        """Given the real coordinates, find the screen (image) coordinates."""
        CameraPosition = self.CameraPosition()
        ScreenX = self.ScreenDisplacement[0] + self.CameraZoom*(real_coords[0]-CameraPosition[0])
        ScreenY = self.ScreenDisplacement[1] - self.CameraZoom*(real_coords[1]-CameraPosition[1])
        return (ScreenX, ScreenY)


    def get_real(self, screen_coords=(0,0)):
        """given the screen (image) coordinatess, find the real coordinates."""
        CameraPosition = self.CameraPosition()
        RealX = (screen_coords[0] - self.ScreenDisplacement[0])/self.CameraZoom + CameraPosition[0]
        RealY = -(screen_coords[1] - self.ScreenDisplacement[1])/self.CameraZoom + CameraPosition[1]
        return np.array([RealX, RealY])


    ########################    Follow a planet code


    def set_focus(self, Planet):
        """Sets focus to a planet, without changing the current view."""
        # new CameraPosition = PanPosition + Planet.Position
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
