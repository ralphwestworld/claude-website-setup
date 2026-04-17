using System;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.XR;

namespace VRFramework.Interaction
{
    /// <summary>
    /// Unified hand wrapper that exposes pose + select state for either a motion
    /// controller or a tracked hand. XRI handles the actual grab interactions on
    /// its own interactors; this component is for gameplay code that needs raw
    /// hand state (for gestures, custom UI, telemetry, etc.).
    /// </summary>
    public class HandInteractor : MonoBehaviour
    {
        public enum Handedness { Left, Right }
        public enum InputSource { Controller, TrackedHand, Auto }

        [SerializeField] private Handedness side = Handedness.Right;
        [SerializeField] private InputSource preferredSource = InputSource.Auto;

        [Header("Controller input (Input System)")]
        [SerializeField] private InputActionProperty selectAction;
        [SerializeField] private InputActionProperty activateAction;

        public event Action OnSelectStarted;
        public event Action OnSelectEnded;
        public event Action OnActivateStarted;
        public event Action OnActivateEnded;

        public Handedness Side => side;
        public bool IsSelecting { get; private set; }
        public bool IsActivating { get; private set; }
        public InputSource ActiveSource { get; private set; }

        private InputDevice cachedDevice;

        private void OnEnable()
        {
            BindAction(selectAction, OnSelectPerformed, OnSelectCanceled, enable: true);
            BindAction(activateAction, OnActivatePerformed, OnActivateCanceled, enable: true);
        }

        private void OnDisable()
        {
            BindAction(selectAction, OnSelectPerformed, OnSelectCanceled, enable: false);
            BindAction(activateAction, OnActivatePerformed, OnActivateCanceled, enable: false);
        }

        private void Update()
        {
            RefreshActiveSource();
        }

        private void RefreshActiveSource()
        {
            if (preferredSource != InputSource.Auto)
            {
                ActiveSource = preferredSource == InputSource.Controller
                    ? InputSource.Controller : InputSource.TrackedHand;
                return;
            }

            if (!cachedDevice.isValid)
            {
                var characteristics = InputDeviceCharacteristics.HeldInHand | InputDeviceCharacteristics.TrackedDevice
                    | (side == Handedness.Left ? InputDeviceCharacteristics.Left : InputDeviceCharacteristics.Right);
                var devices = new System.Collections.Generic.List<InputDevice>();
                InputDevices.GetDevicesWithCharacteristics(characteristics, devices);
                if (devices.Count > 0) cachedDevice = devices[0];
            }

            // Quest reports hand-tracked devices with HandTracking characteristic;
            // controllers report Controller characteristic.
            if (cachedDevice.isValid)
            {
                var isHand = (cachedDevice.characteristics & InputDeviceCharacteristics.HandTracking) != 0;
                ActiveSource = isHand ? InputSource.TrackedHand : InputSource.Controller;
            }
        }

        public bool TryHapticPulse(float amplitude, float duration)
        {
            if (!cachedDevice.isValid) return false;
            if (!cachedDevice.TryGetHapticCapabilities(out var caps)) return false;
            if (!caps.supportsImpulse) return false;
            return cachedDevice.SendHapticImpulse(0, Mathf.Clamp01(amplitude), duration);
        }

        private static void BindAction(InputActionProperty prop, Action<InputAction.CallbackContext> started,
                                       Action<InputAction.CallbackContext> canceled, bool enable)
        {
            var action = prop.action;
            if (action == null) return;

            if (enable)
            {
                action.started += started;
                action.canceled += canceled;
                action.Enable();
            }
            else
            {
                action.started -= started;
                action.canceled -= canceled;
            }
        }

        private void OnSelectPerformed(InputAction.CallbackContext _) { IsSelecting = true; OnSelectStarted?.Invoke(); }
        private void OnSelectCanceled(InputAction.CallbackContext _)  { IsSelecting = false; OnSelectEnded?.Invoke(); }
        private void OnActivatePerformed(InputAction.CallbackContext _) { IsActivating = true; OnActivateStarted?.Invoke(); }
        private void OnActivateCanceled(InputAction.CallbackContext _)  { IsActivating = false; OnActivateEnded?.Invoke(); }
    }
}
