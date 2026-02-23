using UnityEngine;
using System;

namespace FiveNightsAtMrIngles
{
    /// <summary>
    /// Controls office mechanics: doors, lights, cameras
    /// Converted from Python Office class
    /// </summary>
    public class OfficeController : MonoBehaviour
    {
        #region Singleton
        public static OfficeController Instance { get; private set; }

        void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
            }
            else
            {
                Destroy(gameObject);
            }
        }
        #endregion

        #region Public Fields
        [Header("Door States")]
        public bool doorLeftClosed = false;
        public bool doorRightClosed = false;
        public float doorLeftProgress = 0f;  // 0 = open, 1 = closed
        public float doorRightProgress = 0f;
        
        [Header("Door Health")]
        public float doorLeftHealth = 100f;
        public float doorRightHealth = 100f;
        public float doorLeftJamTimer = 0f;
        public float doorRightJamTimer = 0f;
        
        [Header("Lighting")]
        public bool lightOn = true;
        public float lightDim = 0f; // 0 = bright, 1 = dark
        
        [Header("Camera System")]
        public bool camerasOpen = false;
        public float cameraFlash = 0f;
        
        [Header("Advanced Features")]
        public float flashlightBattery = 100f;
        public bool ventSystemActive = true;
        public int barricadeLeft = 0;  // 0-3 levels
        public int barricadeRight = 0;
        public int noiseMakerCharges = 3;
        public float safeModeTimer = 0f;
        public float movementNoiseLevel = 0f;
        
        [Header("Animation Speeds")]
        public float doorSpeed = 2f;
        public float flashDecaySpeed = 5f;
        #endregion

        #region Events
        public static event Action<bool> OnLeftDoorToggle;
        public static event Action<bool> OnRightDoorToggle;
        public static event Action<bool> OnLightToggle;
        public static event Action<bool> OnCameraToggle;
        public static event Action<string> OnNoiseMakerDeploy;
        #endregion

        #region Unity Lifecycle
        void Update()
        {
            UpdateDoorAnimations();
            UpdateEffects();
            UpdateFlashlight();
        }
        #endregion

        #region Door Control
        public void ToggleDoorLeft()
        {
            if (PowerSystem.Instance != null && PowerSystem.Instance.isPowerOut)
                return;
            
            if (doorLeftJamTimer > 0f)
            {
                Debug.LogWarning("Left door is jammed!");
                return;
            }
            
            doorLeftClosed = !doorLeftClosed;
            OnLeftDoorToggle?.Invoke(doorLeftClosed);
            
            Debug.Log($"Left door: {(doorLeftClosed ? "CLOSING" : "OPENING")}");
        }

        public void ToggleDoorRight()
        {
            if (PowerSystem.Instance != null && PowerSystem.Instance.isPowerOut)
                return;
            
            if (doorRightJamTimer > 0f)
            {
                Debug.LogWarning("Right door is jammed!");
                return;
            }
            
            doorRightClosed = !doorRightClosed;
            OnRightDoorToggle?.Invoke(doorRightClosed);
            
            Debug.Log($"Right door: {(doorRightClosed ? "CLOSING" : "OPENING")}");
        }

        void UpdateDoorAnimations()
        {
            // Animate left door
            float targetLeft = doorLeftClosed ? 1f : 0f;
            doorLeftProgress = Mathf.MoveTowards(doorLeftProgress, targetLeft, doorSpeed * Time.deltaTime);
            
            // Animate right door
            float targetRight = doorRightClosed ? 1f : 0f;
            doorRightProgress = Mathf.MoveTowards(doorRightProgress, targetRight, doorSpeed * Time.deltaTime);
            
            // Update jam timers
            if (doorLeftJamTimer > 0f)
            {
                doorLeftJamTimer -= Time.deltaTime;
                if (doorLeftJamTimer <= 0f)
                {
                    doorLeftJamTimer = 0f;
                    Debug.Log("Left door unjammed!");
                }
            }
            
            if (doorRightJamTimer > 0f)
            {
                doorRightJamTimer -= Time.deltaTime;
                if (doorRightJamTimer <= 0f)
                {
                    doorRightJamTimer = 0f;
                    Debug.Log("Right door unjammed!");
                }
            }
        }

        public void DamageDoor(bool leftDoor, float damage)
        {
            if (leftDoor)
            {
                doorLeftHealth -= damage;
                doorLeftHealth = Mathf.Max(0f, doorLeftHealth);
                
                if (doorLeftHealth <= 0f)
                {
                    JamDoor(true, UnityEngine.Random.Range(3f, 8f));
                }
            }
            else
            {
                doorRightHealth -= damage;
                doorRightHealth = Mathf.Max(0f, doorRightHealth);
                
                if (doorRightHealth <= 0f)
                {
                    JamDoor(false, UnityEngine.Random.Range(3f, 8f));
                }
            }
        }

        void JamDoor(bool leftDoor, float duration)
        {
            if (leftDoor)
            {
                doorLeftJamTimer = duration;
                doorLeftClosed = false; // Force open
                Debug.LogWarning($"Left door JAMMED for {duration:F1} seconds!");
            }
            else
            {
                doorRightJamTimer = duration;
                doorRightClosed = false; // Force open
                Debug.LogWarning($"Right door JAMMED for {duration:F1} seconds!");
            }
        }
        #endregion

        #region Light Control
        public void ToggleLight()
        {
            if (PowerSystem.Instance != null && PowerSystem.Instance.isPowerOut)
                return;
            
            lightOn = !lightOn;
            OnLightToggle?.Invoke(lightOn);
            
            Debug.Log($"Light: {(lightOn ? "ON" : "OFF")}");
        }

        void UpdateEffects()
        {
            // Decay camera flash effect
            if (cameraFlash > 0f)
            {
                cameraFlash -= flashDecaySpeed * Time.deltaTime;
                cameraFlash = Mathf.Max(0f, cameraFlash);
            }
            
            // Update light dimming
            float targetDim = lightOn ? 0f : 1f;
            lightDim = Mathf.MoveTowards(lightDim, targetDim, Time.deltaTime * 2f);
        }
        #endregion

        #region Camera Control
        public void ToggleCameras()
        {
            if (PowerSystem.Instance != null && PowerSystem.Instance.isPowerOut)
                return;
            
            camerasOpen = !camerasOpen;
            OnCameraToggle?.Invoke(camerasOpen);
            
            if (camerasOpen)
            {
                cameraFlash = 1f;
            }
            
            Debug.Log($"Cameras: {(camerasOpen ? "OPEN" : "CLOSED")}");
        }

        public void OpenCameras()
        {
            if (!camerasOpen)
                ToggleCameras();
        }

        public void CloseCameras()
        {
            if (camerasOpen)
                ToggleCameras();
        }
        #endregion

        #region Flashlight
        public void ToggleFlashlight()
        {
            // TODO: Implement flashlight toggle
            Debug.Log("Flashlight toggled");
        }

        void UpdateFlashlight()
        {
            if (flashlightBattery > 0f)
            {
                // Drain when in use
                // flashlightBattery -= Time.deltaTime * drainRate;
            }
        }
        #endregion

        #region Advanced Features
        public void UseBarricade()
        {
            // TODO: Implement barricade system
            Debug.Log("Barricade used");
        }

        public void DeployNoiseMaker(string targetRoom)
        {
            if (noiseMakerCharges <= 0)
            {
                Debug.LogWarning("No noise maker charges remaining!");
                return;
            }
            
            noiseMakerCharges--;
            OnNoiseMakerDeploy?.Invoke(targetRoom);
            
            Debug.Log($"Noise maker deployed to: {targetRoom} ({noiseMakerCharges} charges left)");
        }

        public void ToggleVentSystem()
        {
            ventSystemActive = !ventSystemActive;
            Debug.Log($"Vent system: {(ventSystemActive ? "ACTIVE" : "INACTIVE")}");
        }

        public void UseSafeSpot()
        {
            if (safeModeTimer > 0f)
            {
                Debug.LogWarning("Safe spot on cooldown!");
                return;
            }
            
            safeModeTimer = 30f; // 30 second cooldown
            Debug.Log("Safe spot activated!");
        }
        #endregion

        #region System Control
        public void ForceCloseAllSystems()
        {
            doorLeftClosed = false;
            doorRightClosed = false;
            lightOn = false;
            camerasOpen = false;
            
            Debug.LogWarning("All office systems SHUTDOWN (Power Outage)");
        }

        public void ResetOffice()
        {
            doorLeftClosed = false;
            doorRightClosed = false;
            lightOn = true;
            camerasOpen = false;
            
            doorLeftProgress = 0f;
            doorRightProgress = 0f;
            doorLeftHealth = 100f;
            doorRightHealth = 100f;
            doorLeftJamTimer = 0f;
            doorRightJamTimer = 0f;
            
            lightDim = 0f;
            cameraFlash = 0f;
            
            flashlightBattery = 100f;
            ventSystemActive = true;
            barricadeLeft = 0;
            barricadeRight = 0;
            noiseMakerCharges = 3;
            safeModeTimer = 0f;
            movementNoiseLevel = 0f;
            
            Debug.Log("Office reset to default state.");
        }
        #endregion

        #region Debug
        [ContextMenu("Reset Office")]
        void DebugResetOffice()
        {
            ResetOffice();
        }

        [ContextMenu("Jam Left Door")]
        void DebugJamLeftDoor()
        {
            JamDoor(true, 5f);
        }

        [ContextMenu("Jam Right Door")]
        void DebugJamRightDoor()
        {
            JamDoor(false, 5f);
        }
        #endregion
    }
}
