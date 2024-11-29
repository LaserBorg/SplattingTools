import csv
import math
import os

import pymxs

def quaternion_to_euler(x, y, z, w):
    # Convert quaternion to Euler angles (heading, pitch, roll)
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch = math.asin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    heading = math.atan2(t3, t4)

    return heading, pitch, roll

def get_camera_transform_at_frame(camname, frame):
    rt = pymxs.runtime
    rt.sliderTime = frame
    camera = rt.getNodeByName(camname)
    
    if camera is None:
        raise ValueError(f"Camera '{camname}' not found in the scene.")
    
    # Get the position and rotation of the camera
    position = camera.position
    rotation = camera.rotation
    
    # Convert quaternion to heading-pitch-roll
    heading, pitch, roll = quaternion_to_euler(rotation.x, rotation.y, rotation.z, rotation.w)
    
    return position, heading, pitch, roll

def export_cams_csv(camname, imgname, flength, timerange=(0,100), csv_path=None):
    basename, ext = os.path.splitext(imgname)
    if csv_path is None:
        csv_path = basename + ".csv"
        
    rt = pymxs.runtime
    
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['#name', 'x', 'y', 'alt', 'heading', 'pitch', 'roll', 'f', 
                         'px', 'py', 'k1', 'k2', 'k3', 'k4', 't1', 't2'])

        for frame in range(timerange[0], timerange[1] + 1):
            position, heading, pitch, roll = get_camera_transform_at_frame(camname, frame)
            name = f"{basename}{frame:04d}{ext}"
            px = py = k1 = k2 = k3 = k4 = t1 = t2 = 0
            writer.writerow([name, position.x, position.y, position.z, heading, pitch, roll, flength, 
                             px, py, k1, k2, k3, k4, t1, t2])

# for camera_angle_x and camera_angle_y in transforms_train.json
def fov_from_flength(flength, sensor_size=36):
    return 2 * math.atan(sensor_size / (2 * flength))

if __name__ == "__main__":
    camname = "AnimatedCamera"
    imgname = "image_.png"
    flength = 26
    timerange = (1, 61)
    output_dir = "output"
    csv_path = os.path.join(output_dir, "cameras.csv")

    export_cams_csv(camname, imgname, flength, timerange, csv_path)
