using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace VRFramework.Core
{
    /// <summary>
    /// Manages additive scene loading for a VR app. One "environment" scene is
    /// active at a time; the persistent bootstrap scene (holding VRGameManager,
    /// XR rig, etc.) stays loaded underneath.
    /// </summary>
    public class VRSceneManager : MonoBehaviour
    {
        [Tooltip("Scenes registered in Build Settings that this manager is allowed to load.")]
        [SerializeField] private List<string> registeredScenes = new();

        [SerializeField] private SceneTransition transition;

        public event Action<string> SceneLoaded;
        public event Action<string> SceneUnloaded;

        public string ActiveEnvironment { get; private set; }
        public bool IsLoading { get; private set; }

        public async Task TransitionToSceneAsync(string sceneName, float fadeSeconds = 0.4f)
        {
            if (IsLoading) return;
            if (!registeredScenes.Contains(sceneName))
            {
                Debug.LogError($"[VRSceneManager] Scene '{sceneName}' is not registered.");
                return;
            }

            IsLoading = true;

            if (transition != null) await transition.FadeOutAsync(fadeSeconds);

            if (!string.IsNullOrEmpty(ActiveEnvironment))
                await UnloadSceneAsync(ActiveEnvironment);

            await LoadSceneAsync(sceneName, makeActive: true);

            if (transition != null) await transition.FadeInAsync(fadeSeconds);

            IsLoading = false;
        }

        public async Task LoadSceneAsync(string sceneName, bool makeActive = false)
        {
            var op = SceneManager.LoadSceneAsync(sceneName, LoadSceneMode.Additive);
            if (op == null)
            {
                Debug.LogError($"[VRSceneManager] LoadSceneAsync returned null for '{sceneName}'.");
                return;
            }

            while (!op.isDone) await Task.Yield();

            var scene = SceneManager.GetSceneByName(sceneName);
            if (makeActive && scene.IsValid())
            {
                SceneManager.SetActiveScene(scene);
                ActiveEnvironment = sceneName;
            }
            SceneLoaded?.Invoke(sceneName);
        }

        public async Task UnloadSceneAsync(string sceneName)
        {
            var scene = SceneManager.GetSceneByName(sceneName);
            if (!scene.IsValid() || !scene.isLoaded) return;

            var op = SceneManager.UnloadSceneAsync(scene);
            if (op == null) return;

            while (!op.isDone) await Task.Yield();

            if (ActiveEnvironment == sceneName) ActiveEnvironment = null;
            SceneUnloaded?.Invoke(sceneName);
        }
    }
}
