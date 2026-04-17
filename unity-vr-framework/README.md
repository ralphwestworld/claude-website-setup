# VR Scene Framework (Unity + Quest 3)

A modular, code-first framework for building scene-based VR games on Meta Quest 3. Drop it into a Unity 2022 LTS or Unity 6 project and wire the pieces together in your own scenes.

## What's in the package

```
Runtime/
  Core/
    VRGameManager.cs       singleton service locator, persistent bootstrap
    VRSceneManager.cs      additive async scene load/unload + transitions
    SceneTransition.cs     fade-to-black overlay
  Interaction/
    GrabbableProp.cs       XRGrabInteractable wrapper with respawn + events
    HandInteractor.cs      unified controller / hand-tracking input
  Spawning/
    PropCatalog.cs         ScriptableObject registry of prop prefabs
    PropSpawner.cs         pooled runtime spawner, max-live cap
  Utility/
    ObjectPool.cs          zero-alloc prefab pool
  VRFramework.asmdef       assembly definition
```

## Dependencies

The `package.json` pins:

- `com.unity.xr.interaction.toolkit` (XRI 3.x)
- `com.unity.xr.openxr`
- `com.unity.xr.hands`
- `com.unity.inputsystem`

## Unity project setup

1. **Create a Unity 2022 LTS or Unity 6 project** (URP recommended for Quest 3).
2. In **Window > Package Manager**, add the XR packages above (or let this package's manifest pull them).
3. **Edit > Project Settings > XR Plug-in Management**:
   - Enable **OpenXR** for Android.
   - Enable the **Meta Quest Support** feature group.
   - Add the **Hand Tracking Subsystem** feature.
4. **Player Settings (Android)**:
   - Minimum API Level 29+, Target API 32+.
   - Scripting backend: IL2CPP, ARM64 only.
   - Color space: Linear.
   - Active Input Handling: Input System (new).
5. Switch platform to **Android**.

## Wiring a playable build

### 1. Bootstrap scene (persistent)

Create a scene named `Boot`. Add:

- **XR Origin (VR)** from `GameObject > XR > XR Origin (VR)`. This gives you the head camera, two controller/hand interactors, and locomotion.
- **GameObject "VRGame"** with these components:
  - `VRGameManager`
  - `VRSceneManager`
  - `PropSpawner`
  - `SceneTransition`
- A **Canvas** (Screen Space - Camera, render camera = XR head camera) with a full-screen black `Image` and a `CanvasGroup` (alpha 0). Assign the `Image` to `SceneTransition.fadeImage`.
- Drag references between components on `VRGame`:
  - `VRGameManager.sceneManager` -> `VRSceneManager`
  - `VRGameManager.transition` -> `SceneTransition`
  - `VRGameManager.propSpawner` -> `PropSpawner`
  - `VRSceneManager.transition` -> `SceneTransition`

Set `VRGameManager.bootstrapScene` to the first environment you want loaded (e.g. `Scene_Lobby`).

### 2. Environment scenes

Each environment is a **separate scene** added to Build Settings and listed in `VRSceneManager.registeredScenes`. Environment scenes contain only that world's geometry, lights, and prop spawn points — no XR rig, no managers.

Example scenes to create:

- `Scene_Lobby` — a calibration-style room with a table and three `GrabbableProp` items (cube, sphere, hammer).
- `Scene_Arena` — an open space with a `PropSpawner` spawn button prop on a pedestal.
- `Scene_Workshop` — shelves of grabbables; demonstrates the `maxLive` cap in action.

### 3. Making a prop

1. Create an empty GameObject with a mesh (cube to start).
2. Add components: `Rigidbody`, `Collider`, `XRGrabInteractable`, `GrabbableProp`.
3. Set `GrabbableProp.propId` (e.g. `cube`).
4. Drag it into a prefab.
5. Register it in your `PropCatalog` asset (`Assets > Create > VRFramework > Prop Catalog`), add an entry with id `cube` and the prefab. Set `prewarm` / `maxLive`.
6. Assign the catalog to the `PropSpawner` in `Boot`.

### 4. Spawning at runtime

```csharp
using VRFramework.Core;

public class PedestalButton : MonoBehaviour
{
    public Transform spawnPoint;
    public string propId = "cube";

    public void OnPressed()
    {
        VRGameManager.Instance.Props.Spawn(propId, spawnPoint.position, spawnPoint.rotation);
    }
}
```

### 5. Scene transitions

```csharp
await VRGameManager.Instance.Scenes.TransitionToSceneAsync("Scene_Arena");
```

Unloads the current environment, fades to black, loads the next one, fades back.

## Quest 3 performance notes

- Targets 72 or 90 Hz. Stay under **~500k tris**, **~100 draw calls**, one directional light.
- Use **Single Pass Instanced** rendering (URP / OpenXR).
- Keep `PropCatalog` `maxLive` tight — the spawner drops the oldest instance when exceeded.
- Bake lighting where possible; use light probes for grabbables.
- Turn on **Static Batching** for environment geometry and **GPU Instancing** on prop materials.
- Avoid per-frame allocations in `Update` (the `ObjectPool` is there for this reason).

## Input mapping

`HandInteractor` takes two `InputActionProperty` slots. Bind them to:

- `Select` -> XR Controller / Grip (or XR Hand / Pinch for hand tracking).
- `Activate` -> XR Controller / Trigger (or XR Hand / Poke).

The XRI sample actions asset has these ready — reference `XRI LeftHand Interaction/Select Value` and similar.

## Status

- Framework scripts: complete (compiles against XRI 3.0.7).
- Example prefabs / scenes: you build them in Unity following the steps above. I can't ship `.unity` files that survive Unity upgrades reliably, so the README is the source of truth for scene wiring.
