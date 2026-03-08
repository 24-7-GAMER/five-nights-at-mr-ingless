using UnityEngine;
using UnityEngine.UI;
using FiveNightsAtMrIngles;

namespace FiveNightsAtMrIngles.UI
{
    /// <summary>
    /// Controls in-game HUD elements (power, time, status messages)
    /// </summary>
    public class HUDController : MonoBehaviour
    {
        #region UI Elements
        [Header("Power Display")]
        public Slider powerSlider;
        public Text powerText;
        public Image powerIcon;
        public Color powerNormalColor = Color.green;
        public Color powerLowColor = Color.yellow;
        public Color powerCriticalColor = Color.red;

        [Header("Time Display")]
        public Text timeText;
        public Text nightText;

        [Header("Status Display")]
        public Text statusText;
        public float statusDisplayDuration = 3f;

        [Header("Camera Indicator")]
        public GameObject cameraOpenIndicator;
        public Text currentCameraText;

        [Header("Door Indicators")]
        public Image leftDoorIndicator;
        public Image rightDoorIndicator;
        public Color doorOpenColor = Color.green;
        public Color doorClosedColor = Color.red;

        [Header("Controls Overlay")]
        public GameObject controlsPanel;
        public bool showControlsOnStart = true;
        #endregion

        #region Private Fields
        private float statusTimer = 0f;
        private string pendingStatus = "";
        #endregion

        #region Unity Lifecycle
        void OnEnable()
        {
            // Subscribe to events
            PowerSystem.OnPowerChanged += UpdatePowerDisplay;
            PowerSystem.OnPowerOutage += HandlePowerOutage;
            GameManager.OnHourChange += UpdateTimeDisplay;
            GameManager.OnNightStart += UpdateNightDisplay;
            OfficeController.OnLeftDoorToggle += UpdateLeftDoorIndicator;
            OfficeController.OnRightDoorToggle += UpdateRightDoorIndicator;
            OfficeController.OnCameraToggle += UpdateCameraIndicator;
            CameraSystem.OnCameraSwitch += UpdateCurrentCamera;
        }

        void OnDisable()
        {
            // Unsubscribe from events
            PowerSystem.OnPowerChanged -= UpdatePowerDisplay;
            PowerSystem.OnPowerOutage -= HandlePowerOutage;
            GameManager.OnHourChange -= UpdateTimeDisplay;
            GameManager.OnNightStart -= UpdateNightDisplay;
            OfficeController.OnLeftDoorToggle -= UpdateLeftDoorIndicator;
            OfficeController.OnRightDoorToggle -= UpdateRightDoorIndicator;
            OfficeController.OnCameraToggle -= UpdateCameraIndicator;
            CameraSystem.OnCameraSwitch -= UpdateCurrentCamera;
        }

        void Start()
        {
            if (controlsPanel != null)
            {
                controlsPanel.SetActive(showControlsOnStart);
            }

            // Initialize displays
            UpdatePowerDisplay(100f);
            UpdateTimeDisplay(12);
            if (GameManager.Instance != null)
            {
                UpdateNightDisplay(GameManager.Instance.currentNight);
            }
        }

        void Update()
        {
            // Update status message timer
            if (statusTimer > 0f)
            {
                statusTimer -= Time.deltaTime;
                if (statusTimer <= 0f && statusText != null)
                {
                    statusText.text = "";
                }
            }
        }
        #endregion

        #region Event Handlers
        void UpdatePowerDisplay(float powerPercent)
        {
            if (powerSlider != null)
            {
                powerSlider.value = powerPercent / 100f;
            }

            if (powerText != null)
            {
                powerText.text = $"{powerPercent:F0}%";
            }

            // Update power color based on level
            if (powerIcon != null)
            {
                if (powerPercent < 10f)
                    powerIcon.color = powerCriticalColor;
                else if (powerPercent < 30f)
                    powerIcon.color = powerLowColor;
                else
                    powerIcon.color = powerNormalColor;
            }
        }

        void HandlePowerOutage()
        {
            ShowStatus("POWER OUTAGE!", 999f);
        }

        void UpdateTimeDisplay(int hour)
        {
            if (timeText != null)
            {
                timeText.text = $"{hour} AM";
            }
        }

        void UpdateNightDisplay(int night)
        {
            if (nightText != null)
            {
                nightText.text = $"Night {night}";
            }
        }

        void UpdateLeftDoorIndicator(bool closed)
        {
            if (leftDoorIndicator != null)
            {
                leftDoorIndicator.color = closed ? doorClosedColor : doorOpenColor;
            }
        }

        void UpdateRightDoorIndicator(bool closed)
        {
            if (rightDoorIndicator != null)
            {
                rightDoorIndicator.color = closed ? doorClosedColor : doorOpenColor;
            }
        }

        void UpdateCameraIndicator(bool open)
        {
            if (cameraOpenIndicator != null)
            {
                cameraOpenIndicator.SetActive(open);
            }
        }

        void UpdateCurrentCamera(RoomData room)
        {
            if (currentCameraText != null && room != null)
            {
                currentCameraText.text = room.roomName;
            }
        }
        #endregion

        #region Public Methods
        public void ShowStatus(string message, float duration = 3f)
        {
            if (statusText != null)
            {
                statusText.text = message;
                statusTimer = duration;
            }
        }

        public void ToggleControls()
        {
            if (controlsPanel != null)
            {
                controlsPanel.SetActive(!controlsPanel.activeSelf);
            }
        }
        #endregion
    }
}
