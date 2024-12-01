import numpy as np
import os
import shutil
import open3d as o3d
import open3d.core as o3c  # type: ignore


import pymxs  # type: ignore
rt = pymxs.runtime

def export_fbx(fbx_path, exclude=[]):
    # Get all objects in the scene
    all_objects = rt.objects

    # Filter visible geometry objects
    visible_geometry = [obj for obj in all_objects if rt.isKindOf(obj, rt.GeometryClass) and not obj.isHidden and obj.name not in exclude]    
    
    # Print names of visible geometry
    for obj in visible_geometry:
        print(obj.name)

    if not visible_geometry:
        print("No visible geometry to export.")

    else:
        base_obj = rt.copy(visible_geometry[0])
        rt.convertToMesh(base_obj)

        # Attach copies of the remaining visible objects to the base object
        for obj in visible_geometry[1:]:
            rt.attach(base_obj, rt.copy(obj))

        # Convert the combined object to an editable mesh
        rt.convertToMesh(base_obj)
        
        # Select only the combined object
        rt.select(base_obj)

        # Rotate the object 90 degrees around its Y axis
        rotation_matrix = rt.angleaxis(-90, rt.point3(1, 0, 0))
        rt.rotate(base_obj, rotation_matrix)

        # Reset the transformation matrix and center the pivot point
        rt.resetTransform(base_obj)
        rt.resetXForm(base_obj)
        rt.collapseStack(base_obj)
        base_obj.pivot = rt.Point3(0, 0, 0)
        
        # Export the selected object to FBX
        rt.exportFile(fbx_path, rt.name("noPrompt"), selectedOnly=True, using=rt.FBXEXP)
        
        # Delete the temporary object
        rt.delete(base_obj)


def convert_fbx_to_ply(fbx_path, ply_path, points_num=100000):
    # Import the FBX file in Open3D
    mesh = o3d.io.read_triangle_mesh(fbx_path)
    
    pcd = mesh.sample_points_uniformly(points_num)

    # Debugging: Print the number of points
    print(f"Number of points in point cloud: {len(pcd.points)}")

    # Set the color of each point to white (RGB: [255, 255, 255])
    colors = np.ones((len(pcd.points), 3), dtype=np.uint8) * 255
    pcd.colors = o3d.utility.Vector3dVector(colors.astype(np.float64) / 255.0)

    # Convert the point cloud to a tensor point cloud with 32-bit float values
    tensor_pcd = o3d.t.geometry.PointCloud()
    tensor_pcd.point.positions = o3c.Tensor(np.asarray(pcd.points), dtype=o3c.float32)
    tensor_pcd.point.colors = o3c.Tensor(np.asarray(pcd.colors), dtype=o3c.float32)

    # Save the tensor point cloud to a PLY file without normals
    o3d.t.io.write_point_cloud(ply_path, tensor_pcd, write_ascii=False, compressed=False, print_progress=False)


if __name__ == "__main__":
    viewbox_name = "viewbox"
    output_dir = "output"
    tmp_dir = ".tmp"
    ply_path = os.path.join(output_dir, "points.ply")
    fbx_path = os.path.join(tmp_dir, "export.fbx")

    points_num = 100000
    
    # export scene to FBX and use Open3D to convert it to PLY
    os.makedirs(tmp_dir, exist_ok=True)
    export_fbx(fbx_path, exclude=[viewbox_name])
    convert_fbx_to_ply(fbx_path, ply_path, points_num)
    
    # Remove the temporary file
    shutil.rmtree(tmp_dir)
