'''
currently loads a PLY mesh and intatiates cameras from the cameras.csv file 
'''

import open3d as o3d
import numpy as np
from scipy.spatial.transform import Rotation as R
import csv


def get_intrinsic(hfov, res=(1920,1080)):
    width, height = res
    aspect_ratio = width / height

    intrinsic = o3d.camera.PinholeCameraIntrinsic()
    fx = width / (2 * np.tan(np.deg2rad(hfov) / 2))
    fy = fx / aspect_ratio

    intrinsic.set_intrinsics(width=width, height=height, fx=fx, fy=fy, cx=width//2, cy=height//2)
    return intrinsic

def get_extrinsic(position, rotation_deg):
    rotation_rad = np.deg2rad(rotation_deg)

    # Convert Euler angles to rotation matrix
    rotation_matrix = R.from_euler('xyz', rotation_rad).as_matrix()
    
    # Create extrinsic matrix
    extrinsic = np.eye(4)
    extrinsic[:3, :3] = rotation_matrix
    extrinsic[:3, 3] = position
    return extrinsic

def create_cam_visual(position, rotation, scale=1.):
    # Define the pyramid vertices
    vertices = np.array([
        [0, 0, 0],  # Camera position
        [1, 1, 2],  # Top-right
        [-1, 1, 2],  # Top-left
        [-1, -1, 2],  # Bottom-left
        [1, -1, 2]  # Bottom-right
    ]) * scale

    # Define the pyramid lines
    lines = [
        [0, 1], [0, 2], [0, 3], [0, 4],  # From camera position to corners
        [1, 2], [2, 3], [3, 4], [4, 1]  # Base of the pyramid
    ]

    # Rotation matrix for 90 degrees around X-axis
    theta = np.pi / 2
    rotation_matrix = np.array([
        [1, 0, 0],
        [0, np.cos(theta), -np.sin(theta)],
        [0, np.sin(theta), np.cos(theta)]
    ])

    # Apply the rotation to the vertices
    vertices = vertices @ rotation_matrix.T

    # Create line set
    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(vertices)
    line_set.lines = o3d.utility.Vector2iVector(lines)

    # Apply rotation and translation
    extrinsic = get_extrinsic(position, rotation)
    line_set.transform(extrinsic)

    return line_set

def visualize(geometries, camera_params):
    # Visualize the mesh with the camera
    vis = o3d.visualization.Visualizer()
    vis.create_window()


    for geometry in geometries:
        vis.add_geometry(geometry)

    # workaround: Set camera parameters only after adding geometry, else they will get overwritten
    ctr = vis.get_view_control()
    ctr.convert_from_pinhole_camera_parameters(camera_params, True)
    vis.update_renderer()

    vis.run()
    vis.destroy_window()

def read_cams_from_csv(input_csv):
    cams_dict = {}
    with open(input_csv, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            cams_dict[i] = {
                'name': row['#name'],
                'position': [float(row['x']), float(row['y']), float(row['alt'])],
                'yaw': float(row['heading']),
                'pitch': float(row['pitch']),
                'roll': float(row['roll']),
                'focal_length': float(row['f'])
            }
    return cams_dict


if __name__ == '__main__':
    # Load the mesh
    mesh = o3d.io.read_triangle_mesh("_assets/teapot_blender.ply")
    mesh.compute_vertex_normals()  # Enable default shading by computing vertex normals
    geometries = [mesh]

    # flip upside down, i.d.k. why
    rotation_to_z_up = R.from_euler('x', 180, degrees=True).as_matrix()
    mesh.rotate(rotation_to_z_up, center=(0, 0, 0))


    # Create a view
    camera_params = o3d.camera.PinholeCameraParameters()
    hfov = 45  # Horizontal field of view in degrees
    camera_params.intrinsic = get_intrinsic(hfov)
    view_position = [0, 10, 50]
    view_rotation = [-90, 0, 0]
    camera_params.extrinsic = get_extrinsic(view_position, view_rotation)


    # Load cameras from CSV
    cams_dict = read_cams_from_csv('_output/cameras.csv')

    # Iterate over each entry in cams_dict and create a camera visual
    camera_visuals = []
    for cam in cams_dict.values():
        position = cam['position']
        orientation = [cam['yaw'], cam['pitch'], cam['roll']]
        camera_visual = create_cam_visual(position, orientation, scale=1)
        camera_visuals.append(camera_visual)

    geometries.extend(camera_visuals)

    visualize(geometries, camera_params)
