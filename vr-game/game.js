import * as THREE from 'three';
import { VRButton } from 'three/addons/webxr/VRButton.js';
import { XRControllerModelFactory } from 'three/addons/webxr/XRControllerModelFactory.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const ROUND_SECONDS = 60;
const BULLET_SPEED = 18;
const BULLET_LIFETIME = 2.0;
const TARGET_SPAWN_INTERVAL = 1.2;
const MAX_TARGETS = 8;

const state = {
  score: 0,
  timeLeft: ROUND_SECONDS,
  roundActive: false,
  bullets: [],
  targets: [],
  spawnTimer: 0,
};

const scoreEl = document.getElementById('score');
const timeEl = document.getElementById('time');
const hudEl = document.getElementById('hud');
const overlayEl = document.getElementById('overlay');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a1020);
scene.fog = new THREE.Fog(0x0a1020, 15, 55);

const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.05, 200);
camera.position.set(0, 1.6, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.xr.enabled = true;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

const vrButton = VRButton.createButton(renderer);
document.getElementById('vr-button-container').appendChild(vrButton);

const orbit = new OrbitControls(camera, renderer.domElement);
orbit.target.set(0, 1.6, -3);
orbit.enablePan = false;
orbit.update();

scene.add(new THREE.HemisphereLight(0x88aaff, 0x202030, 0.8));
const dir = new THREE.DirectionalLight(0xffffff, 1.1);
dir.position.set(5, 10, 4);
scene.add(dir);

const floor = new THREE.Mesh(
  new THREE.CircleGeometry(30, 64),
  new THREE.MeshStandardMaterial({ color: 0x161c2c, roughness: 0.9, metalness: 0.05 })
);
floor.rotation.x = -Math.PI / 2;
scene.add(floor);

const gridHelper = new THREE.GridHelper(30, 30, 0x3a4a7a, 0x1a2240);
gridHelper.position.y = 0.002;
scene.add(gridHelper);

for (let i = 0; i < 60; i++) {
  const r = 0.05 + Math.random() * 0.1;
  const star = new THREE.Mesh(
    new THREE.SphereGeometry(r, 6, 6),
    new THREE.MeshBasicMaterial({ color: 0xffffff })
  );
  const theta = Math.random() * Math.PI * 2;
  const phi = Math.random() * Math.PI * 0.4 + 0.1;
  const radius = 40;
  star.position.set(
    Math.cos(theta) * Math.sin(phi) * radius,
    Math.cos(phi) * radius,
    Math.sin(theta) * Math.sin(phi) * radius
  );
  scene.add(star);
}

const scorePanel = createScorePanel();
scorePanel.position.set(0, 2.6, -4);
scene.add(scorePanel);

const controllerModelFactory = new XRControllerModelFactory();
const controllers = [0, 1].map((i) => setupController(i));

const tmpMatrix = new THREE.Matrix4();

const bulletGeometry = new THREE.SphereGeometry(0.04, 8, 8);
const bulletMaterial = new THREE.MeshBasicMaterial({ color: 0xffdd55 });

const targetGeometry = new THREE.SphereGeometry(0.25, 20, 16);

window.addEventListener('resize', onResize);
window.addEventListener('keydown', (e) => {
  if (e.key === 'r' || e.key === 'R') startRound();
});
renderer.domElement.addEventListener('pointerdown', () => {
  if (!renderer.xr.isPresenting) fireFromCamera();
});

renderer.xr.addEventListener('sessionstart', () => {
  overlayEl.classList.add('hidden');
  hudEl.style.display = 'block';
  startRound();
});
renderer.xr.addEventListener('sessionend', () => {
  overlayEl.classList.remove('hidden');
  hudEl.style.display = 'none';
});

startRound();
renderer.setAnimationLoop(tick);

function setupController(index) {
  const controller = renderer.xr.getController(index);
  controller.userData.index = index;
  controller.addEventListener('selectstart', () => fireFromController(controller));
  scene.add(controller);

  const grip = renderer.xr.getControllerGrip(index);
  grip.add(controllerModelFactory.createControllerModel(grip));
  scene.add(grip);

  const rayGeom = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0, 0, -5),
  ]);
  const ray = new THREE.Line(rayGeom, new THREE.LineBasicMaterial({ color: 0x7cb6ff, transparent: true, opacity: 0.55 }));
  ray.name = 'ray';
  controller.add(ray);

  const muzzle = new THREE.Mesh(
    new THREE.ConeGeometry(0.03, 0.12, 12),
    new THREE.MeshStandardMaterial({ color: 0x4f7cff, emissive: 0x1a2a66 })
  );
  muzzle.rotation.x = -Math.PI / 2;
  muzzle.position.z = -0.05;
  controller.add(muzzle);

  return controller;
}

function fireFromController(controller) {
  tmpMatrix.identity().extractRotation(controller.matrixWorld);
  const origin = new THREE.Vector3().setFromMatrixPosition(controller.matrixWorld);
  const direction = new THREE.Vector3(0, 0, -1).applyMatrix4(tmpMatrix).normalize();
  spawnBullet(origin, direction);
  pulse(controller, 0.6, 40);
}

function fireFromCamera() {
  const origin = new THREE.Vector3();
  camera.getWorldPosition(origin);
  const direction = new THREE.Vector3();
  camera.getWorldDirection(direction);
  origin.addScaledVector(direction, 0.2);
  spawnBullet(origin, direction);
}

function spawnBullet(origin, direction) {
  if (!state.roundActive) return;
  const mesh = new THREE.Mesh(bulletGeometry, bulletMaterial);
  mesh.position.copy(origin);
  const light = new THREE.PointLight(0xffcc44, 0.8, 2);
  mesh.add(light);
  scene.add(mesh);
  state.bullets.push({ mesh, velocity: direction.clone().multiplyScalar(BULLET_SPEED), life: BULLET_LIFETIME });
}

function pulse(controller, intensity, duration) {
  const src = controller.inputSource || (controller.userData && controller.userData.inputSource);
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

function spawnTarget() {
  if (state.targets.length >= MAX_TARGETS) return;
  const hue = Math.random() * 0.15 + 0.55;
  const material = new THREE.MeshStandardMaterial({
    color: new THREE.Color().setHSL(hue, 0.7, 0.55),
    emissive: new THREE.Color().setHSL(hue, 0.8, 0.25),
    roughness: 0.35,
    metalness: 0.1,
  });
  const mesh = new THREE.Mesh(targetGeometry, material);

  const angle = (Math.random() - 0.5) * Math.PI * 0.9;
  const distance = 6 + Math.random() * 4;
  mesh.position.set(
    Math.sin(angle) * distance,
    1.2 + Math.random() * 1.4,
    -Math.cos(angle) * distance
  );

  const driftDir = Math.random() < 0.5 ? -1 : 1;
  scene.add(mesh);
  state.targets.push({
    mesh,
    driftSpeed: (0.5 + Math.random() * 0.8) * driftDir,
    bobPhase: Math.random() * Math.PI * 2,
    baseY: mesh.position.y,
  });
}

function clearTargets() {
  for (const t of state.targets) scene.remove(t.mesh);
  state.targets.length = 0;
}

function clearBullets() {
  for (const b of state.bullets) scene.remove(b.mesh);
  state.bullets.length = 0;
}

function startRound() {
  state.score = 0;
  state.timeLeft = ROUND_SECONDS;
  state.spawnTimer = 0;
  state.roundActive = true;
  clearTargets();
  clearBullets();
  updateHud();
  updateScorePanel('Go!');
}

function endRound() {
  state.roundActive = false;
  updateScorePanel(`Round over\nFinal: ${state.score}`);
}

function updateHud() {
  scoreEl.textContent = state.score;
  timeEl.textContent = Math.max(0, Math.ceil(state.timeLeft));
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

function tick(_, frame) {
  const dt = Math.min(0.05, clock.getDelta());

  if (state.roundActive) {
    state.timeLeft -= dt;
    if (state.timeLeft <= 0) endRound();

    state.spawnTimer -= dt;
    if (state.spawnTimer <= 0) {
      spawnTarget();
      state.spawnTimer = TARGET_SPAWN_INTERVAL * (0.6 + Math.random() * 0.5);
    }
  }

  for (const t of state.targets) {
    t.bobPhase += dt * 2;
    const r = Math.hypot(t.mesh.position.x, t.mesh.position.z);
    const ang = Math.atan2(t.mesh.position.x, -t.mesh.position.z) + dt * t.driftSpeed * 0.3;
    t.mesh.position.x = Math.sin(ang) * r;
    t.mesh.position.z = -Math.cos(ang) * r;
    t.mesh.position.y = t.baseY + Math.sin(t.bobPhase) * 0.15;
    t.mesh.rotation.y += dt * 0.8;
  }

  for (let i = state.bullets.length - 1; i >= 0; i--) {
    const b = state.bullets[i];
    b.mesh.position.addScaledVector(b.velocity, dt);
    b.life -= dt;

    let hit = false;
    for (let j = state.targets.length - 1; j >= 0; j--) {
      const t = state.targets[j];
      if (b.mesh.position.distanceTo(t.mesh.position) < 0.3) {
        onTargetHit(t, j);
        hit = true;
        break;
      }
    }
    if (hit || b.life <= 0 || b.mesh.position.length() > 60) {
      scene.remove(b.mesh);
      state.bullets.splice(i, 1);
    }
  }

  updateBursts(dt);
  updateHud();
  updateScorePanelLive();
  renderer.render(scene, camera);
}
const clock = new THREE.Clock();

function onTargetHit(target, index) {
  scene.remove(target.mesh);
  state.targets.splice(index, 1);
  state.score += 10;
  spawnBurst(target.mesh.position, target.mesh.material.color);
  for (const c of controllers) pulse(c, 0.8, 50);
}

function spawnBurst(position, color) {
  const group = new THREE.Group();
  for (let i = 0; i < 12; i++) {
    const p = new THREE.Mesh(
      new THREE.BoxGeometry(0.05, 0.05, 0.05),
      new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.8 })
    );
    p.position.copy(position);
    const vel = new THREE.Vector3(
      (Math.random() - 0.5) * 3,
      Math.random() * 2 + 0.5,
      (Math.random() - 0.5) * 3
    );
    p.userData.velocity = vel;
    p.userData.life = 0.8;
    group.add(p);
  }
  scene.add(group);
  burstGroups.push(group);
}

const burstGroups = [];
function updateBursts(dt) {
  for (let i = burstGroups.length - 1; i >= 0; i--) {
    const g = burstGroups[i];
    let alive = false;
    g.children.forEach((p) => {
      p.userData.life -= dt;
      if (p.userData.life > 0) {
        alive = true;
        p.position.addScaledVector(p.userData.velocity, dt);
        p.userData.velocity.y -= dt * 6;
        p.material.opacity = Math.max(0, p.userData.life / 0.8);
        p.material.transparent = true;
      }
    });
    if (!alive) {
      scene.remove(g);
      burstGroups.splice(i, 1);
    }
  }
}

function createScorePanel() {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 256;
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  const material = new THREE.MeshBasicMaterial({ map: texture, transparent: true });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(2.0, 1.0), material);
  mesh.userData = { canvas, texture, message: '' };
  return mesh;
}

function updateScorePanel(message) {
  scorePanel.userData.message = message || '';
  drawScorePanel();
}

function updateScorePanelLive() {
  drawScorePanel();
}

function drawScorePanel() {
  const { canvas, texture, message } = scorePanel.userData;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
  grad.addColorStop(0, 'rgba(20, 28, 52, 0.92)');
  grad.addColorStop(1, 'rgba(10, 14, 28, 0.92)');
  ctx.fillStyle = grad;
  roundRect(ctx, 6, 6, canvas.width - 12, canvas.height - 12, 24);
  ctx.fill();
  ctx.strokeStyle = 'rgba(124, 182, 255, 0.45)';
  ctx.lineWidth = 3;
  ctx.stroke();

  ctx.fillStyle = '#e7ecf5';
  ctx.font = 'bold 54px system-ui, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(`Score ${state.score}`, canvas.width / 2, 90);

  ctx.font = '34px system-ui, sans-serif';
  ctx.fillStyle = '#b9c4d6';
  ctx.fillText(`Time ${Math.max(0, Math.ceil(state.timeLeft))}s`, canvas.width / 2, 140);

  if (message) {
    ctx.font = 'bold 36px system-ui, sans-serif';
    ctx.fillStyle = '#7cb6ff';
    const lines = message.split('\n');
    lines.forEach((line, i) => ctx.fillText(line, canvas.width / 2, 200 + i * 40));
  }

  texture.needsUpdate = true;
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}
