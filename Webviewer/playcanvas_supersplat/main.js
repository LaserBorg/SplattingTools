// FILE: main.js

import { BoundingBox, Script, Vec3 } from 'playcanvas';

document.addEventListener('DOMContentLoaded', async () => {
    const appElement = await document.querySelector('pc-app').ready();
    const app = await appElement.app;

    const entityElement = await document.querySelector('pc-entity[name="camera"]').ready();
    const entity = entityElement.entity;

    const resetPosition = null;
    const resetTarget = null;

    class FrameScene extends Script {
        frameScene(bbox) {
            const sceneSize = bbox.halfExtents.length();
            const distance = sceneSize / Math.sin(this.entity.camera.fov / 180 * Math.PI * 0.5);
            this.entity.script.cameraControls.sceneSize = sceneSize;
            this.entity.script.cameraControls.focus(bbox.center, new Vec3(2, 1, 2).normalize().mulScalar(distance).add(bbox.center));
        }

        resetCamera(bbox) {
            const sceneSize = bbox.halfExtents.length();
            this.entity.script.cameraControls.sceneSize = sceneSize * 0.2;
            this.entity.script.cameraControls.focus(resetTarget ?? Vec3.ZERO, resetPosition ?? new Vec3(2, 1, 2));
        }

        calcBound() {
            const gsplatComponents = this.app.root.findComponents('gsplat');
            return gsplatComponents?.[0]?.instance?.meshInstance?.aabb ?? new BoundingBox();
        }

        initCamara() {
            document.getElementById('loadingIndicator').classList.add('hidden');

            const bbox = this.calcBound();

            // configure camera
            this.entity.camera.horizontalFov = true;
            this.entity.camera.farClip = bbox.halfExtents.length() * 20;
            this.entity.camera.nearClip = this.entity.camera.farClip * 0.001;
            // set NONE tonemapping until https://github.com/playcanvas/engine/pull/7179 is deployed
            this.entity.camera.toneMapping = 6;

            if (bbox.halfExtents.length() > 100 || resetPosition || resetTarget) {
                this.resetCamera(bbox);
            } else {
                this.frameScene(bbox);
            }

            window.addEventListener('keydown', (e) => {
                switch (e.key) {
                    case 'f':
                        this.frameScene(bbox);
                        break;
                    case 'r':
                        this.resetCamera(bbox);
                        break;
                }
            });
        }

        postInitialize() {
            const assets = this.app.assets.filter(asset => asset.type === 'gsplat');
            if (assets.length > 0) {
                const asset = assets[0];
                if (asset.loaded) {
                    this.initCamara();
                } else {
                    asset.on('load', () => {
                        this.initCamara();
                    });
                }
            }
        }
    }

    entity.script.create(FrameScene);

    // Create container for buttons
    const container = document.createElement('div');
    container.classList.add('button-container');

    function createButton({ icon, title, onClick }) {
        const button = document.createElement('button');
        button.innerHTML = icon;
        button.title = title;
        button.classList.add('button');

        if (onClick) button.onclick = onClick;

        return button;
    }

    // Add fullscreen button if supported
    if (document.documentElement.requestFullscreen && document.exitFullscreen) {
        const enterFullscreenIcon = `<svg width="32" height="32" viewBox="0 0 24 24">
            <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z" fill="currentColor"/>
        </svg>`;
        const exitFullscreenIcon = `<svg width="32" height="32" viewBox="0 0 24 24">
            <path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z" fill="currentColor"/>
        </svg>`;

        const fullscreenButton = createButton({
            icon: enterFullscreenIcon,
            title: 'Toggle Fullscreen',
            onClick: () => {
                if (!document.fullscreenElement) {
                    document.documentElement.requestFullscreen();
                } else {
                    document.exitFullscreen();
                }
            }
        });

        // Update icon when fullscreen state changes
        document.addEventListener('fullscreenchange', () => {
            fullscreenButton.innerHTML = document.fullscreenElement ? exitFullscreenIcon : enterFullscreenIcon;
            fullscreenButton.title = document.fullscreenElement ? 'Exit Fullscreen' : 'Enter Fullscreen';
        });

        container.appendChild(fullscreenButton);
    }

    // Add info button
    const infoButton = createButton({
        icon: `<svg width="32" height="32" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" fill="currentColor"/>
        </svg>`,
        title: 'Show Controls',
        onClick: () => {
            const infoPanel = document.getElementById('infoPanel');
            infoPanel.classList.toggle('hidden');
        }
    });

    // Add escape key handler for info panel
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.getElementById('infoPanel').classList.add('hidden');
        }
    });

    container.appendChild(infoButton);

    document.body.appendChild(container);
});