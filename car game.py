# import modules necessary for the code
from ursina import *
from random import *
from ursina.prefabs.first_person_controller import FirstPersonController
from numpy import round
from ursina.shaders import lit_with_shadows_shader 

app = Ursina()  # set up the app

pivot = Entity()

Entity.default_shader = lit_with_shadows_shader

# Add a directional light with shadows enabled
DirectionalLight(parent=pivot, y=2, z=3, shadows=True, rotation=(30, 0, 0), shadow_map_resolution = Vec2(2048, 2048))

# Add an ambient light to simulate bounce lighting and adjust its brightness
AmbientLight(color=color.rgba(60, 60, 60, 0.1))


def num_to_range(num, inMin, inMax, outMin, outMax):
  return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax
                  - outMin))   # makes a function that makes the number lerp/ clamps it

colliding = 0
turn = 0
carcam = FirstPersonController(rotation = -90)
carcam.speed = 0
carcam.mouse_sensitivity = Vec2(40,0)
carcam.jump_height = 0
carcam.y = 5
camera.z = -6.5
mouse.enabled = True  # sets up variables i use in the project and sets up the camera

printspeed = 0
speed = 0
velocity = 0

model = load_model('car.obj')
texture = load_texture('cartex.png')


randy = 0  # more variables and loads the models and textures of the car.

sky = Sky(texture='skybox_texture.png')
window.fullscreen = True # sets up sky and window to fullsreen

car = Entity(model=model, texture=texture, scale=1)
ground = Entity(model = 'plane', collider = 'mesh', scale = 600, texture = 'track.png')  # makes the car and ground entities

turnrate = 90 # sets the turnrate to 90 because wheel model is rotated the wrong way by default

wheel1 = Entity(model='wheel.obj', texture='wheeltex.png', scale = 0.31)
wheel2 = Entity(model='wheel.obj', texture='wheeltex.png', scale = 0.31)
wheel3 = Entity(model='wheel.obj', texture='wheeltex.png', scale = 0.31)
wheel4 = Entity(model='wheel.obj', texture='wheeltex.png', scale = 0.31)   # makes all the wheel entities

def update():
    global velocity, speed, model, texture, randy,turnrate, colliding, turn   # main game function(inbuilt to ursina engine)

    carcam.position += carcam.forward * velocity/2
    car.position = carcam.position
    car.rotation = carcam.rotation 
    car.y = carcam.y + 0.0625 + randy
    car.x = carcam.x + 1.5
    car.z = carcam.z + 0.5
    #suspension_offset = randrange(0,2)               # get camera to follow car and rotate with mouse or keyboard inputs

    if car.intersects(ground).hit:  
        colliding= 1
    else: colliding = 0   # checks if car is touching ground and sets a variable depending on that.

    printspeed = str(round(velocity * 9.5 * 1.609))   # sets the speed based on car's velocity

    print_on_screen(text = printspeed, duration = 0.001, position = (0, 0.45)) # puts text on screem


    if velocity <= -1.49129086168:  # sets a speed limit if car is in reverse
        velocity = -1.49129086168

    if carcam.y < -0.1 or held_keys['r']:     # checks if r is pressed and resets car position if it is
        carcam.position = (0,0,0)
        velocity = 0
        carcam.rotation = 0

    if held_keys['w']:

        if not held_keys['s']:
            if not car.y >= 1:
                velocity += 0.03

        else: velocity = velocity * 0.97

    else:
        velocity = velocity * 0.999     # check if w is pressed and the brake isn't and adds velocity to the car, else it will make the car gradually slow down
    
    if held_keys['s']:

        if not held_keys['w']:
            if not car.y >= 1:
                velocity -= 0.03
                camera.z = 6.5-velocity
                camera.rotation_y = 180  # checks if brake key is pressed, if it is car will slow, if w is pressed it won't slow, puts camera in reverse mode

        else: velocity = velocity * 0.97

    else:
        velocity = velocity * 0.999
    if held_keys['a']:
        carcam.rotation_y -= (4 - velocity/2) * num_to_range(velocity, 0, 4, 0, 1)
        velocity /= 1.003
        turnrate = 60
    elif held_keys['d']:
        turnrate = 120
    else: turnrate = 90

    if held_keys['d']:
        carcam.rotation_y += (4 - velocity/2) * num_to_range(velocity, 0, 4, 0, 1)
        turnrate = 110
        velocity /= 1.003
        
    elif held_keys['a']:
        turnrate = 70

    else: turnrate = 90

    speed = velocity * 10 * 1.609
    mh = round(((speed * (1000 / 60)) / 3.14 * 0.3 * -1))

    wheel1.rotation_z += mh
    wheel1.position = car.position

    wheel1.position += car.right * 0.65
    wheel1.position += car.back * 1
    wheel1.y = 0.32

    wheel1.rotation_x = car.rotation_x  
    wheel1.rotation_y = car.rotation_y + 90

    wheel2.rotation_z += mh
    wheel2.position = car.position

    wheel2.position += car.left * 0.65
    wheel2.position += car.back * 1
    wheel2.y = 0.32

    wheel2.rotation_x = car.rotation_x  
    wheel2.rotation_y = car.rotation_y + 90

    wheel3.rotation_z += mh
    wheel3.position = car.position

    wheel3.position += car.left * 0.65
    wheel3.position += car.forward * 1.45
    wheel3.y = 0.32

    wheel3.rotation_x = car.rotation_x 
    wheel3.rotation_y = car.rotation_y + turnrate

    wheel4.rotation_z += mh
    wheel4.position = car.position

    wheel4.position += car.right * 0.65
    wheel4.position += car.forward * 1.45
    wheel4.y = 0.32

    wheel4.rotation_x = car.rotation_x 
    wheel4.rotation_y = car.rotation_y + turnrate

    if velocity < 0:
        camera.z = 6.5-velocity
        camera.rotation_y = 180
    else:
        camera.z = -6.5
        camera.rotation_y = 0


app.run()
