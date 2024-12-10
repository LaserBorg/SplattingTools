import { Application, BoundingBox, Vec3 } from 'playcanvas';

const app = await Application.getApplication();

const entity = document.querySelector('pc-entity[name="camera"]').entity;

const bgColorPicker = document.getElementById('bgColorPicker');
bgColorPicker.addEventListener('input', (event) => {
    const color = event.target.value;
    const rgb = hexToRgb(color);
    entity.camera.clearColor.set(rgb.r / 255, rgb.g / 255, rgb.b / 255);
});

const hexToRgb = (hex) => {
    const bigint = parseInt(hex.slice(1), 16);
    return {
        r: (bigint >> 16) & 255,
        g: (bigint >> 8) & 255,
        b: bigint & 255
    };
};

const saveButton = document.getElementById('saveButton');
saveButton.addEventListener('click', () => {
    requestAnimationFrame(() => {
        const canvas = app.graphicsDevice.canvas;
        const dataURL = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.href = dataURL;
        link.download = 'viewport.png';
        link.click();
    });
});