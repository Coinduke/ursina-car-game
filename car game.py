# import modules necessary for the code
from ursina import *
from random import *
from ursina.prefabs.first_person_controller import FirstPersonController
from numpy import round 
from ursina.shader import Shader
from ursina.vec2 import Vec2


lit_with_shadows_shader = Shader(language=Shader.GLSL, name='lit_with_shadows_shader', vertex = '''#version 150
uniform struct {
    vec4 position;
    vec3 color;
    vec3 attenuation;
    vec3 spotDirection;
    float spotCosCutoff;
    float spotExponent;
    sampler2DShadow shadowMap;
    mat4 shadowViewMatrix;
} p3d_LightSource[1];


uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;

in vec4 vertex;
in vec3 normal;
in vec4 p3d_Color;

in vec2 p3d_MultiTexCoord0;
uniform vec2 texture_scale;
uniform vec2 texture_offset;
out vec2 texcoords;

out vec4 vertex_color;

uniform mat3 p3d_NormalMatrix;
out vec3 vertex_position;
out vec3 normal_vector;
out vec4 shadow_coord[1];


void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * vertex;
    vertex_position = vec3(p3d_ModelViewMatrix * vertex);
    normal_vector = normalize(p3d_NormalMatrix * normal);
    shadow_coord[0] = p3d_LightSource[0].shadowViewMatrix * vec4(vertex_position, 1);
    texcoords = (p3d_MultiTexCoord0 * texture_scale) + texture_offset;
    vertex_color = p3d_Color;
}

''',
fragment='''
#version 150
uniform struct {
    vec4 position;
    vec3 color;
    vec3 attenuation;
    vec3 spotDirection;
    float spotCosCutoff;
    float spotExponent;
    sampler2DShadow shadowMap;
    mat4 shadowViewMatrix;
} p3d_LightSource[1];

const float M_PI = 3.141592653589793;

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 texcoords;


in vec4 vertex_color;
out vec4 fragment_color;

in vec3 vertex_position;
in vec3 normal_vector;
in vec4 shadow_coord[1];

uniform float shadow_bias;
uniform vec4 shadow_color;
uniform float shadow_blur;
uniform int shadow_samples;

vec4 cast_shadows(vec4 color) {
    float shadow_samples_float = float(shadow_samples);
    float half_shadow_blur = shadow_blur / 2.0;

    for (int i = 0; i < p3d_LightSource.length(); ++i) {
        vec3 diff = p3d_LightSource[i].position.xyz - vertex_position * p3d_LightSource[i].position.w;
        vec3 L = normalize(diff);

        float NdotL = clamp(dot(normal_vector, L), 0.001, 1.0);
        vec3 light_contribution = NdotL * p3d_LightSource[i].color / M_PI;

        vec4 shadow_coordinates = shadow_coord[i];
        shadow_coordinates.z += shadow_bias;

        vec3 converted_shadow_color = (vec3(1.0, 1.0, 1.0) - shadow_color.rgb) * shadow_color.a;
        color.rgb *= p3d_LightSource[i].color.rgb;

        float shadow = 0.0;
        for (int x = 0; x < shadow_samples; ++x) {
            for (int y = 0; y < shadow_samples; ++y) {
                float dx = float(x) * shadow_blur / shadow_samples_float - half_shadow_blur;
                float dy = float(y) * shadow_blur / shadow_samples_float - half_shadow_blur;
                vec4 coord = shadow_coordinates;
                coord.x += dx;
                coord.y += dy;
                shadow += textureProj(p3d_LightSource[i].shadowMap, coord);
            }
        }
        shadow /= (shadow_samples_float * shadow_samples_float);

        color.rgb += shadow * converted_shadow_color;
        color.rgb += light_contribution - converted_shadow_color;
    }

    return color;
}

void main() {
    fragment_color = texture(p3d_Texture0, texcoords) * p3d_ColorScale * vertex_color;

    // Call the function to handle lighting and shadowing
    fragment_color = cast_shadows(fragment_color);
}

''',
default_input = {
    'texture_scale': Vec2(1,1),
    'texture_offset': Vec2(0,0),
    'shadow_color' : color.rgba(0, .5, 1, .25),
    'shadow_bias': 0.001,
    'shadow_blur': 0.001,
    'shadow_samples': 4,
    }
)




app = Ursina()  # set up the app

pivot = Entity()

Entity.default_shader = lit_with_shadows_shader

# Add a directional light with shadows enabled
DirectionalLight(parent=pivot, y=2, z=3, shadows=True, rotation=(30, 0, 0), shadow_map_resolution = Vec2(4096, 4096), color=color.rgba(0.7, 0.6, 0.55, 1))



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
    suspension_offset = uniform(0.0,0.01) * velocity             # get camera to follow car and rotate with mouse or keyboard inputs

    if car.intersects(ground).hit:  
        colliding= 1
    else: colliding = 0   # checks if car is touching ground and sets a variable depending on that.

    printspeed = str(round(velocity * 9.5 * 1.609))   # sets the speed based on car's velocity

    print_on_screen(text = printspeed, duration = 0.001, position = (0, 0.45)) # puts text on screem


    if velocity <= -3.49129086168:  # sets a speed limit if car is in reverse
        velocity = -3.49129086168

    if carcam.y < -0.1 or held_keys['r']:     # checks if r is pressed and resets car position if it is
        carcam.position = (0,0,0)
        velocity = 0
        carcam.rotation = 0

    if held_keys['w']:

        if not held_keys['s']:
            if not car.y >= 1:
                velocity += 0.03
                velocity *= 0.997

        else: velocity = velocity * 0.97

    else:
        if velocity > 0:
            velocity = velocity - 0.001     # check if w is pressed and the brake isn't and adds velocity to the car, else it will make the car gradually slow down
    
    if held_keys['s']:

        if not held_keys['w']:
            if not car.y >= 1:
                velocity -= 0.01
                velocity *= 0.997
                camera.z = 6.5-velocity
                camera.rotation_y = 180  # checks if brake key is pressed, if it is car will slow, if w is pressed it won't slow, puts camera in reverse mode

        else: velocity = velocity * 0.97

    else:
         if velocity < 0:
            velocity = velocity + 0.001

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
    wheel1.y = 0.32 + suspension_offset

    wheel1.rotation_x = car.rotation_x  
    wheel1.rotation_y = car.rotation_y + 90

    wheel2.rotation_z += mh
    wheel2.position = car.position

    wheel2.position += car.left * 0.65
    wheel2.position += car.back * 1
    wheel2.y = 0.32 + suspension_offset

    wheel2.rotation_x = car.rotation_x  
    wheel2.rotation_y = car.rotation_y + 90

    wheel3.rotation_z += mh
    wheel3.position = car.position

    wheel3.position += car.left * 0.65
    wheel3.position += car.forward * 1.45
    wheel3.y = 0.32 + suspension_offset

    wheel3.rotation_x = car.rotation_x 
    wheel3.rotation_y = car.rotation_y + turnrate

    wheel4.rotation_z += mh
    wheel4.position = car.position

    wheel4.position += car.right * 0.65
    wheel4.position += car.forward * 1.45
    wheel4.y = 0.32 + suspension_offset

    wheel4.rotation_x = car.rotation_x 
    wheel4.rotation_y = car.rotation_y + turnrate

    if velocity < 0:
        camera.z = 6.5-velocity
        camera.rotation_y = 180
    else:
        camera.z = -6.5
        camera.rotation_y = 0


app.run()
