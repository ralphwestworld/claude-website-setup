using UnityEngine;
using UnityEngine.Events;
using UnityEngine.XR.Interaction.Toolkit.Interactables;
using UnityEngine.XR.Interaction.Toolkit.Interactors;

namespace VRFramework.Interaction
{
    /// <summary>
    /// A physical prop the player can pick up, hold, and throw. Wraps XRI's
    /// <see cref="XRGrabInteractable"/> with catalog metadata, an optional
    /// respawn boundary, and plain UnityEvents for gameplay hooks.
    /// Requires a Rigidbody + Collider on the same GameObject.
    /// </summary>
    [RequireComponent(typeof(Rigidbody))]
    [RequireComponent(typeof(XRGrabInteractable))]
    public class GrabbableProp : MonoBehaviour
    {
        [Header("Identity")]
        [Tooltip("Matches an entry in the PropCatalog. Leave blank for scene-placed props.")]
        public string propId;

        [Header("Respawn")]
        [Tooltip("If the prop drops below this Y (world), it resets to its spawn pose.")]
        [SerializeField] private float killY = -20f;
        [SerializeField] private bool resetOnFall = true;

        [Header("Events")]
        public UnityEvent OnGrabbed;
        public UnityEvent OnReleased;

        private XRGrabInteractable grab;
        private Rigidbody body;
        private Vector3 spawnPos;
        private Quaternion spawnRot;

        private void Awake()
        {
            body = GetComponent<Rigidbody>();
            grab = GetComponent<XRGrabInteractable>();
            spawnPos = transform.position;
            spawnRot = transform.rotation;

            grab.selectEntered.AddListener(HandleSelectEntered);
            grab.selectExited.AddListener(HandleSelectExited);
        }

        private void OnDestroy()
        {
            if (grab == null) return;
            grab.selectEntered.RemoveListener(HandleSelectEntered);
            grab.selectExited.RemoveListener(HandleSelectExited);
        }

        private void FixedUpdate()
        {
            if (resetOnFall && transform.position.y < killY) ResetToSpawn();
        }

        public void SetSpawnPose(Vector3 position, Quaternion rotation)
        {
            spawnPos = position;
            spawnRot = rotation;
            transform.SetPositionAndRotation(position, rotation);
            body.linearVelocity = Vector3.zero;
            body.angularVelocity = Vector3.zero;
        }

        public void ResetToSpawn()
        {
            body.linearVelocity = Vector3.zero;
            body.angularVelocity = Vector3.zero;
            transform.SetPositionAndRotation(spawnPos, spawnRot);
        }

        private void HandleSelectEntered(SelectEnterEventArgs _) => OnGrabbed?.Invoke();
        private void HandleSelectExited(SelectExitEventArgs _) => OnReleased?.Invoke();
    }
}
