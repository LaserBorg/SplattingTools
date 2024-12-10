<?php
// Define the default background color
$defaultBgColor = '#666666';

// default Field of View
$fov = 50.0;

// Read the JSON file
$json = file_get_contents('models.json');
$models = json_decode($json, true);

// Get the URL parameter
$param = isset($_GET['model']) ? $_GET['model'] : '';

// Find the model based on the URL parameter
$model = null;
foreach ($models as $item) {
    if ($item['urlparameter'] === $param) {
        $model = $item;
        break;
    }
}

// default model
if (!$model) {
    $model = [
        'title' => 'Default Model',
        'src' => 'https://konzept.staging.visionsbox.de/dt/splat/models/iceberg.compressed.ply',
        'bgcolor' => $defaultBgColor,
        'position' => '0 0 0',
        'rotation' => '0 0 180'
    ];
} else {
    // Set default bgcolor if not present
    if (!isset($model['bgcolor'])) {
        $model['bgcolor'] = $defaultBgColor;
    }
    // Set default position if not present
    if (!isset($model['position'])) {
        $model['position'] = '0 0 0';
    }
    // Set default rotation if not present
    if (!isset($model['rotation'])) {
        $model['rotation'] = '0 0 180';
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title><?php echo htmlspecialchars($model['title']); ?></title>
    <link rel="stylesheet" href="styles.css">
    <script type="importmap">
        {
            "imports": {
                "playcanvas": "https://cdn.jsdelivr.net/npm/playcanvas@2.3.3/build/playcanvas.mjs"
            }
        }
    </script>
    <script type="module" src="https://cdn.jsdelivr.net/npm/@playcanvas/web-components@0.1.10/dist/pwc.mjs"></script>
</head>
<body>
    <pc-app antialias="false" depth="false" high-resolution="true" stencil="false">
        <pc-asset id="camera-controls" src="https://cdn.jsdelivr.net/npm/playcanvas@2.3.1/scripts/esm/camera-controls.mjs" preload></pc-asset>
        <pc-asset id="xr-controllers" src="https://cdn.jsdelivr.net/npm/playcanvas@2.3.1/scripts/esm/xr-controllers.mjs" preload></pc-asset>
        <pc-asset id="xr-navigation" src="https://cdn.jsdelivr.net/npm/playcanvas@2.3.1/scripts/esm/xr-navigation.mjs" preload></pc-asset>

        <pc-asset id="ply" type="gsplat" src="<?php echo htmlspecialchars($model['src']); ?>"></pc-asset>
        <pc-scene>
            <!-- Camera (with XR support) -->
            <pc-entity name="camera root">
                <pc-entity name="camera">
                    <pc-camera clear-color="<?php echo htmlspecialchars($model['bgcolor']); ?>" fov="50.00"></pc-camera>
                    <pc-scripts>
                        <pc-script name="cameraControls"></pc-script>
                    </pc-scripts>
                </pc-entity>
                <pc-scripts>
                    <pc-script name="xrControllers"></pc-script>
                    <pc-script name="xrNavigation"></pc-script>
                </pc-entity>
            </pc-entity>

            <!-- Light (for XR controllers) -->
            <pc-entity name="light" rotation="35 45 0">
                <pc-light color="white" intensity="1.5"></pc-light>
            </pc-entity>

            <!-- Splat -->
            <pc-entity name="splat" rotation="<?php echo htmlspecialchars($model['rotation']); ?>" position="<?php echo htmlspecialchars($model['position']); ?>">
                <pc-splat asset="ply"></pc-splat>
            </pc-entity>
        </pc-scene>
    </pc-app>

    <!-- Loading Indicator -->
    <div id="loadingIndicator">Loading...</div>

    <!-- Info Panel -->
    <div id="infoPanel" class="hidden" onclick="document.getElementById('infoPanel').classList.add('hidden')">
        <div id="infoPanelContent" onclick="event.stopPropagation()">
            <h3>Controls</h3>
            <div class="control-item">
                <span class="control-action">Orbit</span>
                <span class="control-key">Left Mouse Button</span>
            </div>
            <div class="control-item">
                <span class="control-action">Pan</span>
                <span class="control-key">Middle Mouse Button</span>
            </div>
            <div class="control-item">
                <span class="control-action">Look around</span>
                <span class="control-key">Right Mouse Button</span>
            </div>
            <div class="control-item">
                <span class="control-action">Zoom</span>
                <span class="control-key">Mouse Wheel</span>
            </div>
            <div class="control-item">
                <span class="control-action">Fly</span>
                <span class="control-key">W,S,A,D</span>
            </div>
            <div class="control-item">
                <span class="control-action">Fly faster</span>
                <span class="control-key">Shift</span>
            </div>
            <div class="control-item">
                <span class="control-action">Fly slower</span>
                <span class="control-key">Ctrl</span>
            </div>
            <div class="control-item">
                <span class="control-action">Frame Scene</span>
                <span class="control-key">F</span>
            </div>
            <div class="control-item">
                <span class="control-action">Reset Camera</span>
                <span class="control-key">R</span>
            </div>
        </div>
    </div>

    <div id="buttonContainer">
        <!-- Color Picker -->
        <input type="color" id="bgColorPicker" name="bgColorPicker" value="<?php echo htmlspecialchars($model['bgcolor']); ?>">
        <!-- Save Button -->
        <button id="saveButton">save</button>
    </div>

    <script type="module" src="main.js"></script>
    <script type="module" src="extensions.js"></script>
</body>
</html>