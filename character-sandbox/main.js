import * as THREE from 'three';
import { VRButton } from 'three/addons/webxr/VRButton.js';
import { XRControllerModelFactory } from 'three/addons/webxr/XRControllerModelFactory.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// --- renderer / scene / camera ---------------------------------------------
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a1a3a);
scene.fog = new THREE.FogExp2(0x0a1a3a, 0.025);

const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.05, 200);
camera.position.set(0, 1.6, 2.2);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.xr.enabled = true;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);

document.getElementById('vr-button-container').appendChild(VRButton.createButton(renderer));

const orbit = new OrbitControls(camera, renderer.domElement);
orbit.target.set(0, 1.2, 0);
orbit.enableDamping = true;
orbit.update();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// --- blueprint "infinite" room ---------------------------------------------
{
  const gridColor = new THREE.Color(0x4aa6ff);
  const floor = new THREE.GridHelper(200, 200, gridColor, gridColor);
  floor.material.transparent = true;
  floor.material.opacity = 0.35;
  scene.add(floor);

  const solidFloor = new THREE.Mesh(
    new THREE.CircleGeometry(100, 64),
    new THREE.MeshStandardMaterial({ color: 0x0d2246, roughness: 0.95, metalness: 0 })
  );
  solidFloor.rotation.x = -Math.PI / 2;
  solidFloor.position.y = -0.001;
  scene.add(solidFloor);

  // faint ceiling grid to reinforce the "room" feel
  const ceiling = new THREE.GridHelper(200, 200, gridColor, gridColor);
  ceiling.position.y = 6;
  ceiling.material.transparent = true;
  ceiling.material.opacity = 0.12;
  scene.add(ceiling);
}

scene.add(new THREE.HemisphereLight(0xbcd7ff, 0x0a1a3a, 0.75));
const key = new THREE.DirectionalLight(0xffffff, 1.0);
key.position.set(3, 6, 4);
scene.add(key);
const rim = new THREE.DirectionalLight(0x88bbff, 0.4);
rim.position.set(-4, 3, -3);
scene.add(rim);

// --- character (procedural humanoid) ---------------------------------------
const skinMat = new THREE.MeshStandardMaterial({
  color: 0xd8a98a,
  roughness: 0.55,
  metalness: 0.0,
});

const character = {
  root: new THREE.Group(),
  bones: {},        // name -> { group, mesh, basePos, baseScale, baseMeshScale }
  grabbable: [],    // meshes we can grab
  morphs: { height: 1.0, muscle: 0.5, weight: 0.5 },
};

function capsulePart(name, { length, radius, color = 0xd8a98a }) {
  // oriented along +Y by default, origin at the base
  const geom = new THREE.CapsuleGeometry(radius, length, 6, 12);
  geom.translate(0, length / 2 + radius, 0);
  const mesh = new THREE.Mesh(geom, skinMat.clone());
  mesh.material.color = new THREE.Color(color);
  mesh.name = name;
  mesh.userData.grabbable = true;
  character.grabbable.push(mesh);
  return mesh;
}

function boneGroup(name, parent, position) {
  const g = new THREE.Group();
  g.name = name;
  g.position.copy(position);
  parent.add(g);
  return g;
}

function attachMesh(name, group, mesh) {
  group.add(mesh);
  character.bones[name] = {
    group,
    mesh,
    basePos: group.position.clone(),
    baseGroupScale: group.scale.clone(),
    baseMeshScale: mesh.scale.clone(),
  };
  return character.bones[name];
}

function buildCharacter() {
  const root = character.root;
  root.position.set(0, 0, 0);
  scene.add(root);

  // Hips at ~0.95m (will be driven by leg length). Build legs DOWN from hips.
  const hips = boneGroup('hips', root, new THREE.Vector3(0, 0.95, 0));
  const hipsMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.32, 0.18, 0.24),
    skinMat.clone()
  );
  hipsMesh.position.y = 0.0;
  hipsMesh.userData.grabbable = true;
  hipsMesh.name = 'hips';
  character.grabbable.push(hipsMesh);
  attachMesh('hips', hips, hipsMesh);

  // Spine + chest stacked upward from hips
  const spine = boneGroup('spine', hips, new THREE.Vector3(0, 0.1, 0));
  const spineMesh = capsulePart('spine', { length: 0.2, radius: 0.11 });
  attachMesh('spine', spine, spineMesh);

  const chest = boneGroup('chest', spine, new THREE.Vector3(0, 0.28, 0));
  const chestMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.42, 0.3, 0.26),
    skinMat.clone()
  );
  chestMesh.position.y = 0.15;
  chestMesh.userData.grabbable = true;
  chestMesh.name = 'chest';
  character.grabbable.push(chestMesh);
  attachMesh('chest', chest, chestMesh);

  // Neck + head
  const neck = boneGroup('neck', chest, new THREE.Vector3(0, 0.32, 0));
  const headMesh = new THREE.Mesh(
    new THREE.SphereGeometry(0.12, 24, 18),
    skinMat.clone()
  );
  headMesh.position.y = 0.14;
  headMesh.userData.grabbable = true;
  headMesh.name = 'head';
  character.grabbable.push(headMesh);
  attachMesh('head', neck, headMesh);

  // Arms: shoulder → upper arm (down) → forearm (down) → hand
  for (const side of ['L', 'R']) {
    const sign = side === 'L' ? 1 : -1;
    const shoulder = boneGroup(`shoulder${side}`, chest, new THREE.Vector3(sign * 0.22, 0.28, 0));
    // upper arm points DOWN
    const upperArmGroup = boneGroup(`upperArm${side}`, shoulder, new THREE.Vector3(0, 0, 0));
    upperArmGroup.rotation.z = sign * -Math.PI; // flip so capsule's +Y extends downward
    const upperArmMesh = capsulePart(`upperArm${side}`, { length: 0.26, radius: 0.055 });
    attachMesh(`upperArm${side}`, upperArmGroup, upperArmMesh);

    const forearmGroup = boneGroup(`forearm${side}`, upperArmGroup, new THREE.Vector3(0, 0.32, 0));
    const forearmMesh = capsulePart(`forearm${side}`, { length: 0.24, radius: 0.045 });
    attachMesh(`forearm${side}`, forearmGroup, forearmMesh);

    const handGroup = boneGroup(`hand${side}`, forearmGroup, new THREE.Vector3(0, 0.3, 0));
    const handMesh = new THREE.Mesh(
      new THREE.BoxGeometry(0.08, 0.12, 0.04),
      skinMat.clone()
    );
    handMesh.position.y = 0.06;
    handMesh.userData.grabbable = true;
    handMesh.name = `hand${side}`;
    character.grabbable.push(handMesh);
    attachMesh(`hand${side}`, handGroup, handMesh);
  }

  // Legs: hip → thigh (down) → shin → foot
  for (const side of ['L', 'R']) {
    const sign = side === 'L' ? 1 : -1;
    const thighGroup = boneGroup(`thigh${side}`, hips, new THREE.Vector3(sign * 0.1, -0.05, 0));
    thighGroup.rotation.z = Math.PI; // point down
    const thighMesh = capsulePart(`thigh${side}`, { length: 0.4, radius: 0.08 });
    attachMesh(`thigh${side}`, thighGroup, thighMesh);

    const shinGroup = boneGroup(`shin${side}`, thighGroup, new THREE.Vector3(0, 0.48, 0));
    const shinMesh = capsulePart(`shin${side}`, { length: 0.38, radius: 0.06 });
    attachMesh(`shin${side}`, shinGroup, shinMesh);

    const footGroup = boneGroup(`foot${side}`, shinGroup, new THREE.Vector3(0, 0.46, 0));
    const footMesh = new THREE.Mesh(
      new THREE.BoxGeometry(0.1, 0.05, 0.22),
      skinMat.clone()
    );
    footMesh.position.set(0, 0.025, -0.06); // foot sticks forward
    footMesh.userData.grabbable = true;
    footMesh.name = `foot${side}`;
    character.grabbable.push(footMesh);
    attachMesh(`foot${side}`, footGroup, footMesh);
  }
}

// --- body morphs ------------------------------------------------------------
// height: overall uniform scale (also lifts hips so feet stay near ground)
// muscle: widens arms, chest, thighs (X/Z scale on those bones)
// weight: widens torso + hips + thighs, slightly softens face (Z scale on head)

function applyMorphs() {
  const { height, muscle, weight } = character.morphs;

  // Overall height — scale whole root, and reposition hips vertically so feet touch ground
  character.root.scale.setScalar(height);

  const muscleGain = 1.0 + (muscle - 0.5) * 0.45;   // 0.775x to 1.225x width
  const weightGain = 1.0 + (weight - 0.5) * 0.7;    // 0.65x to 1.35x width

  const widen = (name, m, w) => {
    const b = character.bones[name];
    if (!b) return;
    b.mesh.scale.set(m * w, 1, m * w);
  };

  widen('chest', muscleGain, weightGain);
  widen('spine', muscleGain * 0.9, weightGain);
  widen('hips',  1, weightGain);
  widen('upperArmL', muscleGain, weightGain * 0.9);
  widen('upperArmR', muscleGain, weightGain * 0.9);
  widen('forearmL', muscleGain * 0.95, weightGain * 0.9);
  widen('forearmR', muscleGain * 0.95, weightGain * 0.9);
  widen('thighL', muscleGain, weightGain);
  widen('thighR', muscleGain, weightGain);
  widen('shinL', muscleGain * 0.9, weightGain * 0.95);
  widen('shinR', muscleGain * 0.9, weightGain * 0.95);
  widen('head', 1 + (weight - 0.5) * 0.15, 1 + (weight - 0.5) * 0.18);
}

buildCharacter();
applyMorphs();

// --- in-world slider panel --------------------------------------------------
const panel = new THREE.Group();
panel.position.set(1.1, 1.1, 0.2);
panel.rotation.y = -Math.PI / 6;
scene.add(panel);

const panelBg = new THREE.Mesh(
  new THREE.PlaneGeometry(0.8, 0.6),
  new THREE.MeshStandardMaterial({ color: 0x0f1f3d, roughness: 0.8, transparent: true, opacity: 0.9 })
);
panel.add(panelBg);

const panelBorder = new THREE.Mesh(
  new THREE.PlaneGeometry(0.82, 0.62),
  new THREE.MeshBasicMaterial({ color: 0x4aa6ff, transparent: true, opacity: 0.35 })
);
panelBorder.position.z = -0.001;
panel.add(panelBorder);

function makeLabel(text) {
  const canvas = document.createElement('canvas');
  canvas.width = 256; canvas.height = 64;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#cfe0ff';
  ctx.font = 'bold 36px system-ui, sans-serif';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, 6, 32);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  const mesh = new THREE.Mesh(
    new THREE.PlaneGeometry(0.3, 0.075),
    new THREE.MeshBasicMaterial({ map: tex, transparent: true })
  );
  return mesh;
}

const sliders = [];
function makeSlider(label, morphKey, y) {
  const group = new THREE.Group();
  group.position.y = y;
  panel.add(group);

  const lbl = makeLabel(label);
  lbl.position.set(-0.2, 0.06, 0.001);
  group.add(lbl);

  const track = new THREE.Mesh(
    new THREE.PlaneGeometry(0.6, 0.02),
    new THREE.MeshBasicMaterial({ color: 0x1a3a6a })
  );
  track.position.z = 0.001;
  group.add(track);

  const handle = new THREE.Mesh(
    new THREE.BoxGeometry(0.04, 0.06, 0.04),
    new THREE.MeshStandardMaterial({ color: 0x7cb6ff, emissive: 0x224477, roughness: 0.4 })
  );
  handle.userData.grabbable = true;
  handle.userData.slider = { morphKey, minX: -0.3, maxX: 0.3 };
  handle.position.set((character.morphs[morphKey] - 0.5) * 0.6, 0, 0.02);
  group.add(handle);

  sliders.push(handle);
}

makeSlider('Height', 'height', 0.2);
makeSlider('Muscle', 'muscle', 0.05);
makeSlider('Weight', 'weight', -0.1);
// Height uses 0.8-1.2 range; remap: store morphs.height in 0..1 for slider, convert on apply.
character.morphs.height = 1.0;

function syncHeightSliderFromValue() {
  const h = sliders[0];
  const normalized = (character.morphs.height - 0.8) / 0.4;
  h.position.x = (normalized - 0.5) * 0.6;
}
syncHeightSliderFromValue();

// --- VR controllers + grab interaction --------------------------------------
const controllerModelFactory = new XRControllerModelFactory();
const controllers = [];

for (let i = 0; i < 2; i++) {
  const c = renderer.xr.getController(i);
  c.userData.grabbed = null;
  c.userData.grabOffset = new THREE.Vector3();
  c.userData.originalParent = null;
  c.userData.originalPos = new THREE.Vector3();
  c.addEventListener('selectstart', () => tryGrab(c));
  c.addEventListener('selectend', () => release(c));
  scene.add(c);

  const grip = renderer.xr.getControllerGrip(i);
  grip.add(controllerModelFactory.createControllerModel(grip));
  scene.add(grip);

  const rayGeom = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0, 0, -2),
  ]);
  const ray = new THREE.Line(rayGeom, new THREE.LineBasicMaterial({ color: 0x7cb6ff, transparent: true, opacity: 0.55 }));
  c.add(ray);

  controllers.push(c);
}

const worldPos = new THREE.Vector3();
const worldPos2 = new THREE.Vector3();

function tryGrab(controller) {
  controller.getWorldPosition(worldPos);
  let best = null;
  let bestDist = 0.25; // grab radius
  const candidates = [...character.grabbable, ...sliders];
  for (const m of candidates) {
    m.getWorldPosition(worldPos2);
    const d = worldPos.distanceTo(worldPos2);
    if (d < bestDist) {
      best = m;
      bestDist = d;
    }
  }
  if (!best) return;

  controller.userData.grabbed = best;
  controller.userData.originalParent = best.parent;
  controller.userData.originalPos = best.position.clone();

  if (best.userData.slider) {
    // sliders are handled by updateGrab; no reparenting
    controller.userData.isSlider = true;
  } else {
    controller.userData.isSlider = false;
    // Compute grab offset so the part doesn't snap to hand center
    best.getWorldPosition(worldPos2);
    controller.userData.grabOffset.copy(worldPos2).sub(worldPos);
    pulse(controller, 0.6, 30);
  }

  if (best.material && best.material.emissive) {
    best.userData._origEmissive = best.material.emissive.getHex();
    best.material.emissive.setHex(0x335599);
  }
}

function release(controller) {
  const grabbed = controller.userData.grabbed;
  if (!grabbed) return;
  if (grabbed.material && grabbed.userData._origEmissive !== undefined) {
    grabbed.material.emissive.setHex(grabbed.userData._origEmissive);
    grabbed.userData._origEmissive = undefined;
  }
  if (!controller.userData.isSlider) {
    // For v1: body parts snap back after release (no IK yet)
    grabbed.position.copy(controller.userData.originalPos);
  }
  controller.userData.grabbed = null;
}

function updateGrabs() {
  for (const c of controllers) {
    const g = c.userData.grabbed;
    if (!g) continue;
    if (c.userData.isSlider) {
      // Project controller world position onto slider's local X axis
      c.getWorldPosition(worldPos);
      const localPt = g.parent.worldToLocal(worldPos.clone());
      const { minX, maxX, morphKey } = g.userData.slider;
      const x = Math.max(minX, Math.min(maxX, localPt.x));
      g.position.x = x;
      const t = (x - minX) / (maxX - minX);
      if (morphKey === 'height') {
        character.morphs.height = 0.8 + t * 0.4; // 0.8 to 1.2
      } else {
        character.morphs[morphKey] = t;
      }
      applyMorphs();
    } else {
      c.getWorldPosition(worldPos);
      // Move grabbed part to follow controller (in world), then convert to parent local
      worldPos.add(c.userData.grabOffset);
      const localTarget = g.parent.worldToLocal(worldPos.clone());
      g.position.lerp(localTarget, 0.5);
    }
  }
}

function pulse(controller, intensity, duration) {
  const session = renderer.xr.getSession();
  if (!session) return;
  for (const input of session.inputSources) {
    if (input.gamepad && input.gamepad.hapticActuators) {
      for (const a of input.gamepad.hapticActuators) {
        if (a.pulse) a.pulse(intensity, duration);
      }
    }
  }
}

// --- desktop click-to-grab for preview --------------------------------------
const raycaster = new THREE.Raycaster();
const ndc = new THREE.Vector2();
let dragState = null;

renderer.domElement.addEventListener('pointerdown', (e) => {
  if (renderer.xr.isPresenting) return;
  ndc.x = (e.clientX / window.innerWidth) * 2 - 1;
  ndc.y = -(e.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(ndc, camera);
  const hits = raycaster.intersectObjects([...character.grabbable, ...sliders], false);
  if (hits.length) {
    dragState = { mesh: hits[0].object, startNdc: ndc.clone(), startPos: hits[0].object.position.clone() };
    orbit.enabled = false;
    if (dragState.mesh.userData.slider) dragState.startX = dragState.mesh.position.x;
  }
});
renderer.domElement.addEventListener('pointermove', (e) => {
  if (!dragState) return;
  ndc.x = (e.clientX / window.innerWidth) * 2 - 1;
  ndc.y = -(e.clientY / window.innerHeight) * 2 + 1;
  const dx = (ndc.x - dragState.startNdc.x);
  if (dragState.mesh.userData.slider) {
    const g = dragState.mesh;
    const { minX, maxX, morphKey } = g.userData.slider;
    const x = Math.max(minX, Math.min(maxX, dragState.startX + dx * 1.2));
    g.position.x = x;
    const t = (x - minX) / (maxX - minX);
    if (morphKey === 'height') character.morphs.height = 0.8 + t * 0.4;
    else character.morphs[morphKey] = t;
    applyMorphs();
  }
});
renderer.domElement.addEventListener('pointerup', () => {
  dragState = null;
  orbit.enabled = true;
});

// --- main loop --------------------------------------------------------------
renderer.setAnimationLoop(() => {
  updateGrabs();
  orbit.update();
  renderer.render(scene, camera);
});
