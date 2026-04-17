using UnityEngine;

namespace VRFramework.Core
{
    /// <summary>
    /// Top-level service locator. Lives across scene loads and exposes the scene
    /// manager, prop spawner, and transition controller to gameplay code.
    /// </summary>
    [DefaultExecutionOrder(-500)]
    public class VRGameManager : MonoBehaviour
    {
        public static VRGameManager Instance { get; private set; }

        [Header("Services")]
        [SerializeField] private VRSceneManager sceneManager;
        [SerializeField] private SceneTransition transition;
        [SerializeField] private Spawning.PropSpawner propSpawner;

        [Header("Bootstrap")]
        [Tooltip("Scene loaded once VRGameManager is ready. Leave empty to skip.")]
        [SerializeField] private string bootstrapScene;

        public VRSceneManager Scenes => sceneManager;
        public SceneTransition Transition => transition;
        public Spawning.PropSpawner Props => propSpawner;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        private async void Start()
        {
            if (!string.IsNullOrEmpty(bootstrapScene))
            {
                await sceneManager.LoadSceneAsync(bootstrapScene, makeActive: true);
            }
        }

        private void OnDestroy()
        {
            if (Instance == this) Instance = null;
        }
    }
}
