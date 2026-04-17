using System;
using System.Collections.Generic;
using UnityEngine;

namespace VRFramework.Spawning
{
    /// <summary>
    /// Registry of prop prefabs known to the PropSpawner. Create via
    /// <c>Assets &gt; Create &gt; VRFramework &gt; Prop Catalog</c>.
    /// </summary>
    [CreateAssetMenu(fileName = "PropCatalog", menuName = "VRFramework/Prop Catalog")]
    public class PropCatalog : ScriptableObject
    {
        [Serializable]
        public class Entry
        {
            public string id;
            public GameObject prefab;
            [Min(0)] public int prewarm = 2;
            [Min(1)] public int maxLive = 16;
        }

        [SerializeField] private List<Entry> entries = new();

        private Dictionary<string, Entry> byId;

        public IReadOnlyList<Entry> Entries => entries;

        public Entry Get(string id)
        {
            if (byId == null) Rebuild();
            byId.TryGetValue(id, out var e);
            return e;
        }

        private void Rebuild()
        {
            byId = new Dictionary<string, Entry>(entries.Count);
            foreach (var e in entries)
            {
                if (e == null || string.IsNullOrEmpty(e.id) || e.prefab == null) continue;
                byId[e.id] = e;
            }
        }

        private void OnValidate() => byId = null;
    }
}
