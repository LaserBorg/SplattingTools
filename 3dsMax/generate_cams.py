import numpy as np
import math

import pymxs  # type: ignore

# Function to get bounding boxes and centers of scene objects, excluding a specific object by name
def get_scene_objects(exclude_name=None):
    rt = pymxs.runtime
    scene_objects = rt.objects
    bboxes_and_centers = []

    for obj in scene_objects:
        if rt.isKindOf(obj, rt.GeometryClass) and obj.name != exclude_name:
            bbox_min = obj.min
            bbox_max = obj.max
            center = (bbox_min + bbox_max) / 2

            bboxes_and_centers.append({
                'name': obj.name,
                'bbox_min': (bbox_min.x, bbox_min.y, bbox_min.z),
                'bbox_max': (bbox_max.x, bbox_max.y, bbox_max.z),
                'center': (center.x, center.y, center.z)
            })

    return bboxes_and_centers

# Function to enlarge bounding boxes by specified amounts in each direction
def enlarge_bboxes(bboxes, enlargement):
    enlarged_boxes = []
    for bbox_min, bbox_max in bboxes:
        enlarged_min = (
            bbox_min[0] - enlargement['min_x'],
            bbox_min[1] - enlargement['min_y'],
            bbox_min[2] - enlargement['min_z']
        )
        enlarged_max = (
            bbox_max[0] + enlargement['max_x'],
            bbox_max[1] + enlargement['max_y'],
            bbox_max[2] + enlargement['max_z']
        )
        enlarged_boxes.append((enlarged_min, enlarged_max))
    return enlarged_boxes

# Function to generate a random position within a specified bounding box
def generate_random_position(bbox_min, bbox_max):
    x = np.random.uniform(bbox_min[0], bbox_max[0])
    y = np.random.uniform(bbox_min[1], bbox_max[1])
    z = np.random.uniform(bbox_min[2], bbox_max[2])
    return [x, y, z]

# Function to check if a position is within any of the bounding boxes
def check_collision(position, bboxes):
    for bbox_min, bbox_max in bboxes:
        if (bbox_min[0] <= position[0] <= bbox_max[0] and
            bbox_min[1] <= position[1] <= bbox_max[1] and
            bbox_min[2] <= position[2] <= bbox_max[2]):
            return True
    return False

# Function to find the closest center to a given position
def find_closest_point(position, centers):
    distances = np.linalg.norm(centers - position, axis=1)
    closest_index = np.argmin(distances)
    return centers[closest_index]

# Function to create a camera at a specified position and set its target to the nearest center
def create_target_cam(position, centers, focal_length=24.0):
    rt = pymxs.runtime
    try:
        camera = rt.FreeCamera()
        camera.position = rt.Point3(float(position[0]), float(position[1]), float(position[2]))
        # Calculate FOV for the given focal length with aperture 36mm
        camera.fov = 2 * rt.atan(18 / focal_length)
        closest_point = find_closest_point(position, centers)
        target = rt.TargetObject()
        target.position = rt.Point3(float(closest_point[0]), float(closest_point[1]), float(closest_point[2]))
        camera.target = target
        return camera
    except Exception as e:
        print(f"Error creating camera at position {position}: {e}")
        return None


def sort_cameras(cameras, viewbox, layer_count=3):
    # Calculate the height of each layer
    layer_height = (viewbox.max.z - viewbox.min.z) / layer_count
    
    # Create layers
    layers = [[] for _ in range(layer_count)]
    
    # Assign cameras to layers
    for cam in cameras:
        z = cam.position.z
        layer_index = int((z - viewbox.min.z) / layer_height)
        if layer_index >= layer_count:
            layer_index = layer_count - 1
        layers[layer_index].append(cam)
    
    # Function to calculate the angle for sorting in 2D clockwise
    def calculate_angle(cam, center):
        dx = cam.position.x - center.x
        dy = cam.position.y - center.y
        return math.atan2(dy, dx)
    
    # Sort cameras within each layer
    for layer in layers:
        if not layer:
            continue
        # Calculate the center of the layer
        center_x = sum(cam.position.x for cam in layer) / len(layer)
        center_y = sum(cam.position.y for cam in layer) / len(layer)
        center = type('Point', (object,), {'x': center_x, 'y': center_y})()
        
        # Sort cameras by angle
        layer.sort(key=lambda cam: calculate_angle(cam, center))
    
    # Flatten the sorted layers back into a single list
    sorted_cameras = [cam for layer in layers for cam in layer]
    
    return sorted_cameras

# Function to create an animated camera from a list of static cameras
def create_animated_cam(cameras, camera_name="AnimatedCamera"):
    rt = pymxs.runtime
    animated_camera = rt.FreeCamera()
    animated_camera.name = camera_name

    # Select the animated camera
    rt.select(animated_camera)
    
    # Enable auto key
    with pymxs.animate(True):
        for i, camera in enumerate(cameras):
            if camera is None:
                continue
            frame = i + 1
            with pymxs.attime(frame):
                # Set the transform of the animated camera
                animated_camera.transform = camera.transform

    # Set the animation range
    rt.animationRange = rt.interval(1, len(cameras))

def delete_cameras(cameras):
    rt = pymxs.runtime
    for camera in cameras:
        rt.delete(camera)


def generate_cams():
    rt = pymxs.runtime

    # Get the bounding box of the "viewbox" object
    viewbox_name = "viewbox"
    viewbox = rt.getNodeByName(viewbox_name)
    if viewbox is None:
        raise ValueError("Object 'viewbox' not found in the scene.")

    bbox_min = (viewbox.min.x, viewbox.min.y, viewbox.min.z)
    bbox_max = (viewbox.max.x, viewbox.max.y, viewbox.max.z)

    # Get bounding boxes and centers of all scene objects, excluding "viewbox"
    bboxes_and_centers = get_scene_objects(exclude_name="viewbox")
    bboxes = [(item['bbox_min'], item['bbox_max']) for item in bboxes_and_centers]
    centers = np.array([item['center'] for item in bboxes_and_centers])

    # Enlarge bounding boxes
    enlargement = {'min_x': 3.0, 'max_x': 3.0, 'min_y': 3.0, 'max_y': 3.0, 'min_z': 5.0, 'max_z': 5.0}
    bboxes = enlarge_bboxes(bboxes, enlargement)

    # Define the desired number of cameras
    desired_num_cameras = 200
    created_num_cameras = 0
    cameras = []

    # Create cameras iteratively until the desired amount is reached
    while created_num_cameras < desired_num_cameras:
        position = generate_random_position(bbox_min, bbox_max)
        if not check_collision(position, bboxes):
            camera = create_target_cam(position, centers, focal_length=24.0)
            if camera is not None:
                cameras.append(camera)
                created_num_cameras += 1

    sorted_cameras = sort_cameras(cameras, viewbox, layer_count=5)

    # Create an animated camera
    create_animated_cam(sorted_cameras)

    # Delete the other cameras
    delete_cameras(cameras)


if __name__ == "__main__":
    generate_cams()
