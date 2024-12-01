import json
import math
import os
#import numpy as np

import pymxs  # type: ignore
rt = pymxs.runtime


def decompose_matrix3(matrix3, precision=6):
    def clean_numbers(numbers, precision):
        return [round(float(num), precision) for num in numbers]

    rotation_matrix = [
        clean_numbers([matrix3.row1.x, matrix3.row2.x, matrix3.row3.x], precision),
        clean_numbers([matrix3.row1.y, matrix3.row2.y, matrix3.row3.y], precision),
        clean_numbers([matrix3.row1.z, matrix3.row2.z, matrix3.row3.z], precision)
    ]
    translation_vector = clean_numbers([matrix3.row4.x, matrix3.row4.y, matrix3.row4.z], precision)
    return rotation_matrix, translation_vector

def get_transform(rotation_matrix, translation_vector):
    transform_matrix = [
        [rotation_matrix[0][0], rotation_matrix[0][1], rotation_matrix[0][2], translation_vector[0]],
        [rotation_matrix[1][0], rotation_matrix[1][1], rotation_matrix[1][2], translation_vector[1]],
        [rotation_matrix[2][0], rotation_matrix[2][1], rotation_matrix[2][2], translation_vector[2]],
        [0., 0., 0., 1.]]
    return transform_matrix


# def decompose_matrix3_numpy(matrix3):
#     matrix3_np = np.array(matrix3)
#     rotation_matrix = matrix3_np[:3, :].T  # Transpose the rotation matrix
#     translation_vector = matrix3_np[3, :]
#     return rotation_matrix.tolist(), translation_vector.tolist()

# def get_transform_numpy(rotation_matrix, translation_vector):
#     transform_matrix = np.eye(4)                  # [0, 0, 0, 1] as last row
#     transform_matrix[:3, :3] = rotation_matrix    # first three columns
#     transform_matrix[:3, 3] = translation_vector  # fourth column
#     return transform_matrix.tolist()


class TransformsFile:
    def __init__(self, dims, flength, sensor_size=36, aabb_scale=1):
        '''
        aabb-scale is NeRF-specific:
        https://huggingface.co/camenduru/instant-ngp/blob/main/docs/nerf_dataset_tips.md
        '''
        self.w = dims[0]
        self.h = dims[1]
        self.flength = flength
        self.sensor_size = sensor_size

        self.aabb_scale = aabb_scale

        self.camera_angle_x = self.fov_from_flength(self.flength, self.sensor_size)
        self.camera_angle_y = self.camera_angle_x * self.h / self.w
        self.frames = []

    def add_frame(self, transform_matrix, file_path):
        frame = {
            "transform_matrix": transform_matrix,
            "file_path": file_path
        }
        self.frames.append(frame)

    @staticmethod
    def fov_from_flength(flength, sensor_size=36):
        return 2 * math.atan(sensor_size / (2 * flength))

    def to_dict(self):
        return {
            "aabb_scale": self.aabb_scale,
            "w": self.w,
            "h": self.h,
            "camera_angle_x": self.camera_angle_x,
            "camera_angle_y": self.camera_angle_y,
            "frames": self.frames
        }
    
    def save_json(self, output_path):
        with open(output_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)


if __name__ == "__main__":

    camname = "AnimatedCamera"
    imgname = "rock/image_"  # .jpg ignored
    basename, ext = os.path.splitext(imgname)

    dims = (1000, 1000)
    flength_h = 43.456
    timerange = (1, 61)
    precision = 6
    output_dir = "output/"

    json_path = os.path.join(output_dir, "cameras.json")

    camera = rt.getNodeByName(camname)
    transforms_file = TransformsFile(dims, flength_h)

    for frame in range(timerange[0], timerange[1] + 1):
        rt.sliderTime = frame
        rotation_matrix, translation_vector = decompose_matrix3(camera.transform, precision)
        transform_matrix = get_transform(rotation_matrix, translation_vector)
        #print(rotation_matrix, translation_vector)

        filename = f"{basename}{frame:04d}{ext}"
        transforms_file.add_frame(transform_matrix, filename)

    transforms_file.save_json(json_path)
