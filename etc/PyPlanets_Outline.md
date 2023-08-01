### Overview:

**Features**:
    Adding, deleting, moving planets.
    Changing velocity, radius, mass, color.
        Text boxes for changin radius, mass, color.
    A camera that pans, zooms around cursor.
    A file input system where you can import a set of planets.

**Intended setup and classes**:
    CameraRig class:
        Holds camera position and zoom
        Handles panning, zooming, following planet
        Holds text boxes
    
    KeyboardInput class:
        Handles pygame events, directs the actions to perform
    
    Planets class:
        Holds position, velocity, mass, radius, color
        handles drawing planet to screen
    
    PlanetsList class:
        List of planets with order number
    
    PhysEngine class:
        Handles doing the physics
        calculates grav force, gives forces to planets, updates velocity/position
    
    VectArrow class:
        Handles calculations for the arrow that appears onscreen when modifying the velocity
    
    TextBox class:
        Handles drawing / updating / recording text input
    
    TextBoxList 