import bpy
import numpy as np
import os
from numpy import random
import argparse

# https://caretdashcaret.com/2015/05/19/how-to-run-blender-headless-from-the-command-line-without-the-gui/
def get_args():
    parser = argparse.ArgumentParser()
     
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1: ]
     
    parser.add_argument('-n', '--number', help="number of plates")
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args

 
args = get_args()

data_path = os.path.join(bpy.path.abspath('//'), '..', 'data')
flat_data_path = os.path.join(data_path, 'flat-plates')
output_path = os.path.join(data_path, 'augmented-plates')

scene = bpy.data.scenes['plate-scene']
world = scene.world
plate_object = bpy.data.objects["plate-plane"]
light_object = bpy.data.objects["glare-light"]
plate_material = plate_object.material_slots['plate-material'].material
image_node = plate_material.node_tree.nodes['Image Texture']

def rsign():
    return -1 if random.rand() < 0.5 else 1

def flat_plate_image_path(plate_type, name):
    return os.path.join(flat_data_path, plate_type, f"{name}.png")
    
def output_plate_image_path(plate_type, name):
    return os.path.join(output_path, plate_type, f"{name}.png")
    
baseline_images = os.listdir(os.path.join(flat_data_path, "baseline"))
highlighted_images = os.listdir(os.path.join(flat_data_path, "highlight"))


def render_plate_aspect(highlight: bool, i: int):
    plate_type = "highlight" if highlight else "baseline"
    img = bpy.data.images.load(flat_plate_image_path(plate_type, i), check_existing=True)
    image_node.image = img
    
    if not highlight:
        image_w, image_h = img.size
        plate_w = (random.rand() * 2) + 1
        plate_h = (image_h / image_w) * plate_w
        plate_object.dimensions[:2] = plate_w, plate_h,

    scene_lighting = False if highlight else random.rand() < 0.5
    use_ao = True if highlight else scene_lighting and random.rand() < 0.5
    scene.world.light_settings.use_ambient_occlusion = use_ao
    if use_ao:
        scene.world.light_settings.ao_factor = 1 if highlight else random.rand()

    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0 if highlight or not scene_lighting else max(random.exponential() / 16, 0) * 2
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (random.rand(), random.rand(), random.rand(), 1)

    if not highlight:
        plate_object.location = [(random.rand() * 2) - 1 for _ in range(3)]
        plate_object.rotation_euler = (
            rsign() * np.pi * random.rand() * 0.3,
            rsign() * np.pi * random.rand() * 0.3,
            random.rand() * np.pi * 2
        )

    light_object.hide_viewport = highlight
    light_object.hide_render = highlight
    if not highlight:
        light_object.data.energy = max(random.exponential() / 160, 0) * 1e6
        light_object.location[:2] = [(random.rand() * 2) - 2 for _ in range(2)]
 

    scene.render.filepath = output_plate_image_path(plate_type, i)
    bpy.ops.render.render(write_still=True)
    bpy.data.images.remove(img)


for i in range(int(args.number)):
    render_plate_aspect(False, i)
    render_plate_aspect(True, i)