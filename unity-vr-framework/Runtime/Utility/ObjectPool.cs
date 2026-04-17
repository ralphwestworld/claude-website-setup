using System.Collections.Generic;
using UnityEngine;

namespace VRFramework.Utility
{
    /// <summary>
    /// Allocation-free pool for prefab instances. Keeps inactive copies parented
    /// under a hidden transform to avoid scene clutter.
    /// </summary>
    public class ObjectPool
    {
        private readonly GameObject prefab;
        private readonly Transform parent;
        private readonly Stack<GameObject> idle = new();

        public ObjectPool(GameObject prefab, int prewarm, Transform parent = null)
        {
            this.prefab = prefab;
            this.parent = parent;
            for (int i = 0; i < prewarm; i++) idle.Push(Create());
        }

        private GameObject Create()
        {
            var go = Object.Instantiate(prefab, parent);
            go.SetActive(false);
            return go;
        }

        public GameObject Get(Vector3 position, Quaternion rotation)
        {
            var go = idle.Count > 0 ? idle.Pop() : Create();
            go.transform.SetPositionAndRotation(position, rotation);
            go.SetActive(true);
            return go;
        }

        public void Release(GameObject instance)
        {
            if (instance == null) return;
            instance.SetActive(false);
            if (parent != null) instance.transform.SetParent(parent, worldPositionStays: false);
            idle.Push(instance);
        }
    }
}
