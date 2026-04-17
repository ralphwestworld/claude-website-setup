# Quest 3 Target Range (WebXR)

A VR target shooter that runs in the Quest 3 browser. No app store, no APK — just a webpage.

## How to play

- **Controllers:** aim with either controller, pull the **trigger** to shoot.
- **Score:** +10 per target hit. Round lasts 60 seconds.
- **Restart:** on desktop press `R`. In VR, end the session and re-enter.
- **Desktop preview:** drag to look, click to shoot.

## Run locally

WebXR requires HTTPS (except on `localhost`). Any static server works:

```bash
cd vr-game
python3 -m http.server 8000
# then open http://localhost:8000 on desktop
```

To try it on the Quest 3, the headset must reach your machine over HTTPS. Easy options:

- **ngrok** — `ngrok http 8000`, then open the `https://…ngrok…` URL in the Quest browser.
- **GitHub Pages / Netlify / Vercel** — deploy this folder; open the public URL in the Quest browser and click **Enter VR**.

## Files

- `index.html` — page shell, overlay, import map for Three.js.
- `game.js` — scene, controllers, bullets, targets, scoring, HUD.

## Tech

- [Three.js](https://threejs.org/) r161 via ES modules CDN.
- WebXR `immersive-vr` session, `VRButton`, `XRControllerModelFactory`.
- Haptic pulses via the XR input source gamepad actuators.
