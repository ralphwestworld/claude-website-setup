using System.Collections.Generic;
using UnityEngine;
using VRFramework.Interaction;
using VRFramework.Utility;

namespace VRFramework.Spawning
{
    /// <summary>
    /// Runtime prop spawner backed by a <see cref="PropCatalog"/>. Pools
    /// instances per prop id and enforces a max-live cap to keep the frame
    /// budget stable on Quest 3.
    /// </summary>
    public class PropSpawner : MonoBehaviour
    {
        [SerializeField] private PropCatalog catalog;

        private readonly Dictionary<string, ObjectPool> pools = new();
        private readonly Dictionary<string, List<GameObject>> live = new();
        private Transform poolRoot;

        public PropCatalog Catalog
        {
            get => catalog;
            set { catalog = value; BuildPools(); }
        }

        private void Awake()
        {
            poolRoot = new GameObject("PropPool").transform;
            poolRoot.SetParent(transform, worldPositionStays: false);
            BuildPools();
        }

        private void BuildPools()
        {
            pools.Clear();
            live.Clear();
            if (catalog == null) return;
            foreach (var entry in catalog.Entries)
            {
                if (entry == null || string.IsNullOrEmpty(entry.id) || entry.prefab == null) continue;
                pools[entry.id] = new ObjectPool(entry.prefab, entry.prewarm, poolRoot);
                live[entry.id] = new List<GameObject>(entry.maxLive);
            }
        }

        public GameObject Spawn(string propId, Vector3 position, Quaternion rotation)
        {
            if (catalog == null) return null;
            var entry = catalog.Get(propId);
            if (entry == null)
            {
                Debug.LogWarning($"[PropSpawner] Unknown prop id '{propId}'.");
                return null;
            }
            if (!pools.TryGetValue(propId, out var pool)) return null;

            var liveList = live[propId];
            if (liveList.Count >= entry.maxLive) Despawn(liveList[0]);

            var instance = pool.Get(position, rotation);
            liveList.Add(instance);

            var prop = instance.GetComponent<GrabbableProp>();
            if (prop != null) prop.SetSpawnPose(position, rotation);
            return instance;
        }

        public void Despawn(GameObject instance)
        {
            if (instance == null) return;
            foreach (var kv in live)
            {
                if (!kv.Value.Remove(instance)) continue;
                if (pools.TryGetValue(kv.Key, out var pool)) pool.Release(instance);
                return;
            }
            Destroy(instance); // not pooled — discard
        }

        public void DespawnAll(string propId)
        {
            if (!live.TryGetValue(propId, out var list)) return;
            for (int i = list.Count - 1; i >= 0; i--) Despawn(list[i]);
        }
    }
}
