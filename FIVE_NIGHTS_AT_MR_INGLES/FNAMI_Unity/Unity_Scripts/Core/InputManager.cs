using UnityEngine;
using FiveNightsAtMrIngles;

namespace FiveNightsAtMrIngles
{
    /// <summary>
    /// Centralized input handling system
    /// Handles all keyboard/mouse input and routes to appropriate systems
    /// </summary>
    public class InputManager : MonoBehaviour
    {
        #region Singleton
        public static InputManager Instance { get; private set; }

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

        #region Input Settings
        [Header("Key Bindings")]
        public KeyCode leftDoorKey = KeyCode.Q;
        public KeyCode rightDoorKey = KeyCode.E;
        public KeyCode flashlightKey = KeyCode.F;
        public KeyCode camerasKey = KeyCode.Tab;
        public KeyCode controlsKey = KeyCode.H;
        public KeyCode pauseKey = KeyCode.Escape;
        public KeyCode alternativePauseKey = KeyCode.P;

        [Header("Camera Switching")]
        public KeyCode[] cameraHotkeys = new KeyCode[]
        {
            KeyCode.Alpha1, KeyCode.Alpha2, KeyCode.Alpha3,
            KeyCode.Alpha4, KeyCode.Alpha5, KeyCode.Alpha6
        };

        [Header("Advanced Features")]
        public KeyCode barricadeKey = KeyCode.B;
        public KeyCode noiseMakerKey = KeyCode.N;
        public KeyCode ventSystemKey = KeyCode.V;
        public KeyCode safeSpotKey = KeyCode.C;

        [Header("Input Buffering")]
        public bool enableInputBuffering = true;
        public float inputBufferTime = 0.1f;
        #endregion

        #region Private Fields
        private float lastInputTime = 0f;
        #endregion

        #region Unity Lifecycle
        void Update()
        {
            if (GameManager.Instance == null)
                return;

            // Handle input based on current game state
            switch (GameManager.Instance.currentState)
            {
                case GameManager.GameState.Playing:
                    HandleGameplayInput();
                    break;

                case GameManager.GameState.Paused:
                    HandlePausedInput();
                    break;

                case GameManager.GameState.Menu:
                    HandleMenuInput();
                    break;

                case GameManager.GameState.Tutorial:
                    HandleTutorialInput();
                    break;
            }
        }
        #endregion

        #region Gameplay Input
        void HandleGameplayInput()
        {
            if (OfficeController.Instance == null)
                return;

            // Door controls
            if (Input.GetKeyDown(leftDoorKey))
            {
                OfficeController.Instance.ToggleDoorLeft();
            }

            if (Input.GetKeyDown(rightDoorKey))
            {
                OfficeController.Instance.ToggleDoorRight();
            }

            // Flashlight
            if (Input.GetKeyDown(flashlightKey))
            {
                OfficeController.Instance.ToggleFlashlight();
            }

            // Cameras
            if (Input.GetKeyDown(camerasKey))
            {
                OfficeController.Instance.ToggleCameras();
            }

            // Camera hotkeys (only when cameras are open)
            if (OfficeController.Instance.camerasOpen && CameraSystem.Instance != null)
            {
                for (int i = 0; i < cameraHotkeys.Length; i++)
                {
                    if (Input.GetKeyDown(cameraHotkeys[i]))
                    {
                        CameraSystem.Instance.SwitchCamera(i);
                    }
                }

                // Arrow key navigation
                if (Input.GetKeyDown(KeyCode.RightArrow))
                {
                    CameraSystem.Instance.NextCamera();
                }

                if (Input.GetKeyDown(KeyCode.LeftArrow))
                {
                    CameraSystem.Instance.PreviousCamera();
                }
            }

            // Advanced features
            if (Input.GetKeyDown(barricadeKey))
            {
                OfficeController.Instance.UseBarricade();
            }

            if (Input.GetKeyDown(noiseMakerKey))
            {
                // Open noise maker selection menu
                // This would be handled by UI controller
                Debug.Log("Noise maker menu opened");
            }

            if (Input.GetKeyDown(ventSystemKey))
            {
                OfficeController.Instance.ToggleVentSystem();
            }

            if (Input.GetKeyDown(safeSpotKey))
            {
                OfficeController.Instance.UseSafeSpot();
            }

            // Controls toggle
            if (Input.GetKeyDown(controlsKey))
            {
                // Toggle controls overlay
                var hud = FindObjectOfType<FiveNightsAtMrIngles.UI.HUDController>();
                if (hud != null)
                {
                    hud.ToggleControls();
                }
            }

            // Pause
            if (Input.GetKeyDown(pauseKey) || Input.GetKeyDown(alternativePauseKey))
            {
                GameManager.Instance.ChangeState(GameManager.GameState.Paused);
            }
        }
        #endregion

        #region Paused Input
        void HandlePausedInput()
        {
            // Unpause
            if (Input.GetKeyDown(pauseKey) || Input.GetKeyDown(alternativePauseKey))
            {
                GameManager.Instance.ChangeState(GameManager.GameState.Playing);
            }
        }
        #endregion

        #region Menu Input
        void HandleMenuInput()
        {
            // Quick night selection
            if (Input.GetKeyDown(KeyCode.Alpha1))
            {
                GameManager.Instance.StartNight(1);
            }
            else if (Input.GetKeyDown(KeyCode.Alpha2) && GameManager.Instance.maxNightUnlocked >= 2)
            {
                GameManager.Instance.StartNight(2);
            }
            else if (Input.GetKeyDown(KeyCode.Alpha3) && GameManager.Instance.maxNightUnlocked >= 3)
            {
                GameManager.Instance.StartNight(3);
            }
            else if (Input.GetKeyDown(KeyCode.Alpha4) && GameManager.Instance.maxNightUnlocked >= 4)
            {
                GameManager.Instance.StartNight(4);
            }
            else if (Input.GetKeyDown(KeyCode.Alpha5) && GameManager.Instance.maxNightUnlocked >= 5)
            {
                GameManager.Instance.StartNight(5);
            }
        }
        #endregion

        #region Tutorial Input
        void HandleTutorialInput()
        {
            // Skip tutorial
            if (Input.GetKeyDown(KeyCode.Space))
            {
                var tutorial = FindObjectOfType<FiveNightsAtMrIngles.UI.TutorialController>();
                if (tutorial != null)
                {
                    tutorial.SkipTutorial();
                }
            }
        }
        #endregion

        #region Input Buffering
        bool CheckInputBuffer()
        {
            if (!enableInputBuffering)
                return true;

            float timeSinceLastInput = Time.time - lastInputTime;
            if (timeSinceLastInput < inputBufferTime)
            {
                return false; // Too soon, buffer input
            }

            lastInputTime = Time.time;
            return true;
        }
        #endregion

        #region Public Methods
        public bool GetKeyDown(KeyCode key)
        {
            return Input.GetKeyDown(key) && CheckInputBuffer();
        }

        public void SetKeyBinding(string actionName, KeyCode newKey)
        {
            switch (actionName.ToLower())
            {
                case "leftdoor":
                    leftDoorKey = newKey;
                    break;
                case "rightdoor":
                    rightDoorKey = newKey;
                    break;
                case "flashlight":
                    flashlightKey = newKey;
                    break;
                case "cameras":
                    camerasKey = newKey;
                    break;
                case "pause":
                    pauseKey = newKey;
                    break;
            }
        }
        #endregion
    }
}
