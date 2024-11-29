'''
requirements.txt:
flask

start the server:
python endpoint.py

test with curl:
curl -X POST http://localhost:5000/upload \
  -F "image=@path/to/your/image.jpg" \
  -F "pose={\"timestamp\": \"2023-10-10T10:10:10Z\", \"position\": {\"x\": 1, \"y\": 2, \"z\": 3}, \"orientation\": {\"x\": 0, \"y\": 0, \"z\": 0, \"w\": 1}, \"fieldOfView\": {\"fovY\": 90, \"fovX\": 120}}"

'''

from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

# Directory to save the uploaded files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files or 'pose' not in request.form:
        return jsonify({'error': 'No image or pose data provided'}), 400

    image = request.files['image']
    pose_data = request.form['pose']

    # Save the image
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    image_filename = os.path.join(UPLOAD_FOLDER, f'{timestamp}.jpg')
    image.save(image_filename)

    # Save the pose data
    pose_filename = os.path.join(UPLOAD_FOLDER, f'{timestamp}.json')
    with open(pose_filename, 'w') as pose_file:
        json.dump(json.loads(pose_data), pose_file)

    return jsonify({'message': 'File uploaded successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
