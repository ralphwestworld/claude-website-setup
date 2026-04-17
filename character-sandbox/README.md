# Character Sandbox (VR)

First-person VR character sandbox for Quest 3. Start with a procedural humanoid in a blueprint-grid room. Grab body parts with the controllers. Adjust body proportions with in-world sliders.

## What's in v1

- **Blueprint infinite room** — dark blue with glowing grid floor and ceiling.
- **Procedural humanoid** — head, torso, arms, legs built from primitives with PBR skin material. Full bone hierarchy so we can plug in real morphs later.
- **Body morph sliders (in-world)** — Height, Muscle, Weight. Grab a handle with the trigger and slide.
- **Grab interaction** — point the controller near a body part, pull the trigger, the part highlights and follows your hand while held. (V1: parts snap back on release — IK posing is the next step.)
- **Desktop preview** — orbit with drag, pointer-drag the slider handles.

## Run

```bash
cd character-sandbox
python3 -m http.server 8000
# http://localhost:8000 on desktop
# for Quest 3: ngrok http 8000 → open the https url in the headset browser → Enter VR
```

## What's next (roadmap)

- **IK posing** — grabbing a hand rotates the arm via two-bone IK instead of snapping back.
- **Real rigged model** — swap the procedural body for a GLB/VRM character with proper skin shader and blendshapes. This is where "realistic textures" land.
- **Equipment system** — grabbable armor/weapon items that snap to equipment slots (head, chest, hands, waist).
- **Saved presets** — save character to localStorage / export JSON.
- **Facial controls** — blendshape sliders for expressions once the real model is in.

## File layout

- `index.html` — page shell, import map for Three.js, enter-VR button.
- `main.js` — scene, room, character builder, morphs, VR grab, slider panel.
