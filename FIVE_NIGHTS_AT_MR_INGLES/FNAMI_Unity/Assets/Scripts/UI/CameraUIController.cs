using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;
using FiveNightsAtMrIngles;

namespace FiveNightsAtMrIngles.UI
{
    /// <summary>
    /// Controls camera monitoring UI
    /// </summary>
    public class CameraUIController : MonoBehaviour
    {
        #region UI Elements
        [Header("Camera Panel")]
        public GameObject cameraPanel;
        public Image cameraFeedImage;
        public Text roomNameText;
        public RawImage staticOverlay;

        [Header("Minimap")]
        public RectTransform minimapContainer;
        public GameObject roomDotPrefab;
        public Color normalRoomColor = Color.white;
        public Color currentRoomColor = Color.yellow;
        public Color animatronicPresentColor = Color.red;
        public float minimapScale = 200f;

        [Header("Room Selection")]
        public GameObject roomButtonsPanel;
        public Button previousCameraButton;
        public Button nextCameraButton;
        public Button closeCamerasButton;

        [Header("Effects")]
        public float staticIntensity = 0.3f;
        public float scanlineSpeed = 50f;
        public Slider staticSlider;
        #endregion

        #region Private Fields
        private Dictionary<RoomData, GameObject> minimapDots = new Dictionary<RoomData, GameObject>();
        private List<Button> roomButtons = new List<Button>();
        private float staticOffset = 0f;
        #endregion

        #region Unity Lifecycle
        void OnEnable()
        {
            OfficeController.OnCameraToggle += HandleCameraToggle;
            CameraSystem.OnCameraSwitch += HandleCameraSwitch;
            Animatronic.OnAnimatronicMove += HandleAnimatronicMove;
        }

        void OnDisable()
        {
            OfficeController.OnCameraToggle -= HandleCameraToggle;
            CameraSystem.OnCameraSwitch -= HandleCameraSwitch;
            Animatronic.OnAnimatronicMove -= HandleAnimatronicMove;
        }

        void Start()
        {
            if (cameraPanel != null)
            {
                cameraPanel.SetActive(false);
            }

            SetupButtons();
            CreateMinimap();
        }

        void Update()
        {
            if (cameraPanel != null && cameraPanel.activeSelf)
            {
                UpdateStaticEffect();
            }
        }
        #endregion

        #region Setup
        void SetupButtons()
        {
            if (previousCameraButton != null)
            {
                previousCameraButton.onClick.AddListener(() => 
                {
                    if (CameraSystem.Instance != null)
                        CameraSystem.Instance.PreviousCamera();
                });
            }

            if (nextCameraButton != null)
            {
                nextCameraButton.onClick.AddListener(() => 
                {
                    if (CameraSystem.Instance != null)
                        CameraSystem.Instance.NextCamera();
                });
            }

            if (closeCamerasButton != null)
            {
                closeCamerasButton.onClick.AddListener(() => 
                {
                    if (OfficeController.Instance != null)
                        OfficeController.Instance.CloseCameras();
                });
            }
        }

        void CreateMinimap()
        {
            if (minimapContainer == null || roomDotPrefab == null || CameraSystem.Instance == null)
                return;

            // Clear existing dots
            foreach (var dot in minimapDots.Values)
            {
                if (dot != null)
                    Destroy(dot);
            }
            minimapDots.Clear();

            // Create dot for each room
            foreach (var room in CameraSystem.Instance.allRooms)
            {
                if (room == null) continue;

                GameObject dot = Instantiate(roomDotPrefab, minimapContainer);
                RectTransform rt = dot.GetComponent<RectTransform>();

                if (rt != null)
                {
                    // Position based on room's minimap coordinates
                    Vector2 pos = new Vector2(
                        (room.minimapX - 0.5f) * minimapScale,
                        (room.minimapY - 0.5f) * minimapScale
                    );
                    rt.anchoredPosition = pos;
                }

                // Add Button component for clicking
                Button btn = dot.GetComponent<Button>();
                if (btn == null)
                    btn = dot.AddComponent<Button>();

                // Capture room reference for lambda
                RoomData capturedRoom = room;
                btn.onClick.AddListener(() => SwitchToRoom(capturedRoom));

                // Store dot
                minimapDots[room] = dot;
            }

            UpdateMinimapColors();
        }
        #endregion

        #region Event Handlers
        void HandleCameraToggle(bool open)
        {
            if (cameraPanel != null)
            {
                cameraPanel.SetActive(open);
            }

            if (open)
            {
                UpdateCameraView();
                UpdateMinimapColors();
            }
        }

        void HandleCameraSwitch(RoomData newRoom)
        {
            UpdateCameraView();
            UpdateMinimapColors();
        }

        void HandleAnimatronicMove(Animatronic animatronic, RoomData room)
        {
            // Update minimap to show animatronic presence
            UpdateMinimapColors();
        }
        #endregion

        #region UI Updates
        void UpdateCameraView()
        {
            if (CameraSystem.Instance == null)
                return;

            RoomData currentRoom = CameraSystem.Instance.GetCurrentRoom();
            if (currentRoom == null)
                return;

            // Update camera feed
            if (cameraFeedImage != null && currentRoom.cameraViewSprite != null)
            {
                cameraFeedImage.sprite = currentRoom.cameraViewSprite;
            }

            // Update room name
            if (roomNameText != null)
            {
                roomNameText.text = currentRoom.roomName.ToUpper();
            }
        }

        void UpdateMinimapColors()
        {
            if (CameraSystem.Instance == null)
                return;

            RoomData currentRoom = CameraSystem.Instance.GetCurrentRoom();

            // Get all animatronic locations
            var animatronicRooms = new HashSet<RoomData>();
            var animatronics = FindObjectsOfType<Animatronic>();
            foreach (var animatronic in animatronics)
            {
                if (animatronic.currentRoom != null && animatronic.isActive)
                {
                    animatronicRooms.Add(animatronic.currentRoom);
                }
            }

            // Update each dot color
            foreach (var kvp in minimapDots)
            {
                RoomData room = kvp.Key;
                GameObject dot = kvp.Value;

                if (dot == null) continue;

                Image img = dot.GetComponent<Image>();
                if (img == null) continue;

                // Priority: Current room > Animatronic present > Normal
                if (room == currentRoom)
                {
                    img.color = currentRoomColor;
                }
                else if (animatronicRooms.Contains(room))
                {
                    img.color = animatronicPresentColor;
                }
                else
                {
                    img.color = normalRoomColor;
                }
            }
        }

        void UpdateStaticEffect()
        {
            if (staticOverlay == null)
                return;

            // Animated static effect
            staticOffset += Time.deltaTime * scanlineSpeed;
            if (staticOffset > 1f)
                staticOffset = 0f;

            // Update static material offset (if using custom shader)
            Material mat = staticOverlay.material;
            if (mat != null && mat.HasProperty("_Offset"))
            {
                mat.SetFloat("_Offset", staticOffset);
            }

            // Update alpha based on intensity
            Color c = staticOverlay.color;
            c.a = staticIntensity;
            staticOverlay.color = c;
        }
        #endregion

        #region Public Methods
        public void SwitchToRoom(RoomData room)
        {
            if (CameraSystem.Instance != null && room != null)
            {
                CameraSystem.Instance.SwitchToRoom(room.roomName);
            }
        }

        public void SetStaticIntensity(float intensity)
        {
            staticIntensity = Mathf.Clamp01(intensity);
        }
        #endregion
    }
}
