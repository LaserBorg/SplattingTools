/*
 * Copyright 2017 Google Inc. All Rights Reserved.
 * Licensed under the Apache License, Version 2.0 (the 'License');
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an 'AS IS' BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

/**
 * Query for WebXR support. If there's no support for the `immersive-ar` mode,
 * show an error.
 */
(async function() {
  if (navigator.xr) {
    const isArSessionSupported = await navigator.xr.isSessionSupported("immersive-ar");
    if (isArSessionSupported) {
      document.getElementById("enter-ar").addEventListener("click", window.app.activateXR);
    } else {
      onNoXRDevice();
    }
  } else {
    onNoXRDevice();
  }
})();

/**
 * Container class to manage connecting to the WebXR Device API
 * and handle rendering on every frame.
 */
class App {
  /**
   * Run when the Start AR button is pressed.
   */
  activateXR = async () => {
    try {
      // Initialize a WebXR session using "immersive-ar".
      this.xrSession = await navigator.xr.requestSession("immersive-ar", {
        requiredFeatures: ['hit-test', 'dom-overlay'],
        domOverlay: { root: document.body }
      });

      // Create the canvas that will contain our camera's background and our virtual scene.
      this.createXRCanvas();

      // With everything set up, start the app.
      await this.onSessionStarted();
    } catch(e) {
      console.log(e);
      onNoXRDevice();
    }
  }

  /**
   * Add a canvas element and initialize a WebGL context that is compatible with WebXR.
   */
  createXRCanvas() {
    this.canvas = document.createElement("canvas");
    document.body.appendChild(this.canvas);
    this.gl = this.canvas.getContext("webgl", {xrCompatible: true});

    this.xrSession.updateRenderState({
      baseLayer: new XRWebGLLayer(this.xrSession, this.gl)
    });
  }

  /**
   * Called when the XRSession has begun. Here we set up our three.js
   * renderer, scene, and camera and attach our XRWebGLLayer to the
   * XRSession and kick off the render loop.
   */
  onSessionStarted = async () => {
    // Add the `ar` class to our body, which will hide our 2D components
    document.body.classList.add('ar');

    // To help with working with 3D on the web, we'll use three.js.
    this.setupThreeJs();

    // Setup an XRReferenceSpace using the "local" coordinate system.
    this.localReferenceSpace = await this.xrSession.requestReferenceSpace('local');

    // Create another XRReferenceSpace that has the viewer as the origin.
    this.viewerSpace = await this.xrSession.requestReferenceSpace('viewer');
    // Perform hit testing using the viewer as origin.
    this.hitTestSource = await this.xrSession.requestHitTestSource({ space: this.viewerSpace });

    // Start a rendering loop using this.onXRFrame.
    this.xrSession.requestAnimationFrame(this.onXRFrame);

    this.xrSession.addEventListener("select", this.onSelect);
  }

  /** Place a sunflower when the screen is tapped. */
  onSelect = () => {
    if (window.sunflower) {
      const clone = window.sunflower.clone();
      clone.position.copy(this.reticle.position);
      this.scene.add(clone)

      const shadowMesh = this.scene.children.find(c => c.name === 'shadowMesh');
      shadowMesh.position.y = clone.position.y;
    }
  }

  /**
   * Called on the XRSession's requestAnimationFrame.
   * Called with the time and XRPresentationFrame.
   */
  onXRFrame = (time, frame) => {
    // Queue up the next draw request.
    this.xrSession.requestAnimationFrame(this.onXRFrame);

    // Bind the graphics framebuffer to the baseLayer's framebuffer.
    const framebuffer = this.xrSession.renderState.baseLayer.framebuffer;
    this.gl.bindFramebuffer(this.gl.FRAMEBUFFER, framebuffer);
    this.renderer.setFramebuffer(framebuffer);

    // Retrieve the pose of the device.
    // XRFrame.getViewerPose can return null while the session attempts to establish tracking.
    const pose = frame.getViewerPose(this.localReferenceSpace);
    if (pose) {
      // In mobile AR, we only have one view.
      const view = pose.views[0];

      const viewport = this.xrSession.renderState.baseLayer.getViewport(view);
      this.renderer.setSize(viewport.width, viewport.height);

      // Use the view's transform matrix and projection matrix to configure the THREE.camera.
      this.camera.matrix.fromArray(view.transform.matrix); // View matrix (extrinsics)
      this.camera.projectionMatrix.fromArray(view.projectionMatrix); // Projection matrix (intrinsics)
      this.camera.updateMatrixWorld(true);

      // Extract and log the field of view
      const fov = extractFieldOfView(view.projectionMatrix);
      console.log(`Vertical FOV: ${fov.fovY} degrees, Horizontal FOV: ${fov.fovX} degrees`);

      // Conduct hit test.
      const hitTestResults = frame.getHitTestResults(this.hitTestSource);

      // If we have results, consider the environment stabilized.
      if (!this.stabilized && hitTestResults.length > 0) {
        this.stabilized = true;
        document.body.classList.add('stabilized');
      }
      if (hitTestResults.length > 0) {
        const hitPose = hitTestResults[0].getPose(this.localReferenceSpace);

        // Update the reticle position
        this.reticle.visible = true;
        this.reticle.position.set(hitPose.transform.position.x, hitPose.transform.position.y, hitPose.transform.position.z);
        this.reticle.updateMatrixWorld(true);
      }

      // Capture frame and pose data
      this.captureFrameAndPose(time, pose);

      // Render the scene with THREE.WebGLRenderer.
      this.renderer.render(this.scene, this.camera);
    }
  }

  captureFrameAndPose(time, pose) {
    // Create a timestamp
    const timestamp = new Date().toISOString();

    // Extract field of view
    const fov = extractFieldOfView(this.camera.projectionMatrix.elements);

    // Capture the frame as a JPEG image
    this.canvas.toBlob(blob => {
      const formData = new FormData();
      formData.append('image', blob, `${timestamp}.jpg`);

      // Extract camera pose
      const cameraPose = {
        timestamp: timestamp,
        position: {
          x: pose.transform.position.x,
          y: pose.transform.position.y,
          z: pose.transform.position.z
        },
        orientation: {
          x: pose.transform.orientation.x,
          y: pose.transform.orientation.y,
          z: pose.transform.orientation.z,
          w: pose.transform.orientation.w
        },
        fieldOfView: {
          fovY: fov.fovY,
          fovX: fov.fovX
        }
      };

      // Add camera pose to form data
      formData.append('pose', JSON.stringify(cameraPose));

      // Send the data to the server
      fetch('https://your-server-url/upload', {
        method: 'POST',
        body: formData
      }).then(response => {
        if (response.ok) {
          console.log('Frame and pose data uploaded successfully');
        } else {
          console.error('Failed to upload frame and pose data');
        }
      }).catch(error => {
        console.error('Error uploading frame and pose data:', error);
      });
    }, 'image/jpeg');
  }

  /**
   * Initialize three.js specific rendering code, including a WebGLRenderer,
   * a demo scene, and a camera for viewing the 3D content.
   */
  setupThreeJs() {
    // To help with working with 3D on the web, we'll use three.js.
    // Set up the WebGLRenderer, which handles rendering to our session's base layer.
    this.renderer = new THREE.WebGLRenderer({
      alpha: true,
      preserveDrawingBuffer: true,
      canvas: this.canvas,
      context: this.gl
    });
    this.renderer.autoClear = false;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    // Initialize our demo scene.
    this.scene = DemoUtils.createLitScene();
    this.reticle = new Reticle();
    this.scene.add(this.reticle);

    // We'll update the camera matrices directly from API, so
    // disable matrix auto updates so three.js doesn't attempt
    // to handle the matrices independently.
    this.camera = new THREE.PerspectiveCamera();
    this.camera.matrixAutoUpdate = false;
  }
};

// Function to extract field of view from the projection matrix
function extractFieldOfView(projectionMatrix) {
  const fovY = 2 * Math.atan(1 / projectionMatrix[5]);
  const aspectRatio = projectionMatrix[5] / projectionMatrix[0];
  const fovX = 2 * Math.atan(aspectRatio * Math.tan(fovY / 2));

  return {
    fovY: THREE.MathUtils.radToDeg(fovY), // Convert from radians to degrees
    fovX: THREE.MathUtils.radToDeg(fovX)  // Convert from radians to degrees
  };
}

window.app = new App();
