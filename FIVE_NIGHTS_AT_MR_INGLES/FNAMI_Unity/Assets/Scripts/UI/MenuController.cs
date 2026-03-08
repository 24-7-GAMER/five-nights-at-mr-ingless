using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;
using FiveNightsAtMrIngles;

namespace FiveNightsAtMrIngles.UI
{
    /// <summary>
    /// Controls main menu UI
    /// </summary>
    public class MenuController : MonoBehaviour
    {
        #region UI Elements
        [Header("Night Selection")]
        public Button[] nightButtons; // Array of 5 buttons for nights 1-5
        public Text[] nightButtonTexts;

        [Header("Settings")]
        public Slider nightLengthSlider;
        public Text nightLengthText;
        public Slider difficultySlider;
        public Text difficultyText;
        public Text statusText;
        public Text instructionText;

        [Header("Options")]
        public Toggle musicToggle;
        public Toggle sfxToggle;
        public Toggle skipTutorialToggle;
        public Toggle fpsCapToggle;

        [Header("Other Buttons")]
        public Button continueButton;
        public Button newGameButton;
        public Button settingsButton;
        public Button quitButton;

        [Header("Panels")]
        public GameObject mainPanel;
        public GameObject settingsPanel;
        public GameObject creditsPanel;

        [Header("Settings")]
        public float minNightLength = 30f;
        public float maxNightLength = 120f;
        public float minDifficulty = 0.5f;
        public float maxDifficulty = 2.0f;
        #endregion

        #region Unity Lifecycle
        void OnEnable()
        {
            // Play menu music when menu becomes active
            if (AudioManager.Instance != null)
            {
                AudioManager.Instance.PlayMusic(AudioManager.Instance.menuMusic);
            }
        }

        void Start()
        {
            SetupNightButtons();
            LoadSettings();
            SetupSliders();
            SetupToggles();
            SetupButtons();
            UpdateUI();
            
            // Ensure menu music plays
            if (AudioManager.Instance != null && GameManager.Instance != null &&
                GameManager.Instance.currentState == GameManager.GameState.Menu)
            {
                AudioManager.Instance.PlayMusic(AudioManager.Instance.menuMusic);
            }
        }
        #endregion

        #region Setup
        void SetupNightButtons()
        {
            if (nightButtons == null || nightButtons.Length < 5)
                return;

            for (int i = 0; i < nightButtons.Length; i++)
            {
                int nightNumber = i + 1;
                if (nightButtons[i] != null)
                {
                    nightButtons[i].onClick.AddListener(() => StartNight(nightNumber));
                }
            }
        }

        void SetupSliders()
        {
            if (nightLengthSlider != null)
            {
                nightLengthSlider.minValue = minNightLength;
                nightLengthSlider.maxValue = maxNightLength;
                nightLengthSlider.onValueChanged.AddListener(OnNightLengthChanged);
            }

            if (difficultySlider != null)
            {
                difficultySlider.minValue = minDifficulty;
                difficultySlider.maxValue = maxDifficulty;
                difficultySlider.onValueChanged.AddListener(OnDifficultyChanged);
            }
        }

        void SetupToggles()
        {
            if (musicToggle != null)
                musicToggle.onValueChanged.AddListener(OnMusicToggled);

            if (sfxToggle != null)
                sfxToggle.onValueChanged.AddListener(OnSFXToggled);

            if (skipTutorialToggle != null)
                skipTutorialToggle.onValueChanged.AddListener(OnSkipTutorialToggled);

            if (fpsCapToggle != null)
                fpsCapToggle.onValueChanged.AddListener(OnFPSCapToggled);
        }

        void SetupButtons()
        {
            if (continueButton != null)
                continueButton.onClick.AddListener(ContinueGame);

            if (newGameButton != null)
                newGameButton.onClick.AddListener(NewGame);

            if (settingsButton != null)
                settingsButton.onClick.AddListener(OpenSettings);

            if (quitButton != null)
                quitButton.onClick.AddListener(QuitGame);
        }
        #endregion

        #region Load/Save Settings
        void LoadSettings()
        {
            if (GameManager.Instance != null)
            {
                if (nightLengthSlider != null)
                    nightLengthSlider.value = GameManager.Instance.secondsPerHour;

                if (difficultySlider != null)
                    difficultySlider.value = GameManager.Instance.difficulty;

                if (skipTutorialToggle != null)
                    skipTutorialToggle.isOn = GameManager.Instance.skipTutorial;

                if (fpsCapToggle != null)
                    fpsCapToggle.isOn = GameManager.Instance.fpsCapEnabled;
            }

            if (AudioManager.Instance != null)
            {
                if (musicToggle != null)
                    musicToggle.isOn = !AudioManager.Instance.musicMuted;
                if (sfxToggle != null)
                    sfxToggle.isOn = !AudioManager.Instance.sfxMuted;
            }
        }

        void SaveSettings()
        {
            if (SaveLoadManager.Instance != null)
            {
                SaveLoadManager.Instance.SaveProgress();
            }
        }
        #endregion

        #region UI Updates
        void UpdateUI()
        {
            // Update night button states based on unlock progress
            if (GameManager.Instance != null && nightButtons != null)
            {
                for (int i = 0; i < nightButtons.Length; i++)
                {
                    int nightNumber = i + 1;
                    bool unlocked = nightNumber <= GameManager.Instance.maxNightUnlocked;

                    if (nightButtons[i] != null)
                    {
                        nightButtons[i].interactable = unlocked;
                    }

                    if (nightButtonTexts != null && i < nightButtonTexts.Length && nightButtonTexts[i] != null)
                    {
                        nightButtonTexts[i].text = unlocked ? nightNumber.ToString() : "";
                    }
                }
            }

            // Update continue button
            if (continueButton != null && GameManager.Instance != null)
            {
                continueButton.interactable = GameManager.Instance.maxNightUnlocked > 1;
            }
            
            // Update status text
            if (statusText != null && GameManager.Instance != null)
            {
                if (GameManager.Instance.maxNightUnlocked == 1)
                {
                    statusText.text = "No nights survived yet";
                    statusText.color = new Color(1f, 0.39f, 0.39f);
                }
                else
                {
                    statusText.text = $"Your Record: Night {GameManager.Instance.maxNightUnlocked}";
                    statusText.color = new Color(0.39f, 1f, 0.59f);
                }
            }
        }

        void OnNightLengthChanged(float value)
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.secondsPerHour = value;
            }

            if (nightLengthText != null)
            {
                int minutes = Mathf.RoundToInt(value / 60f * 6f); // Total night length in minutes
                nightLengthText.text = $"{minutes} min";
            }
        }

        void OnDifficultyChanged(float value)
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.difficulty = value;
            }

            if (difficultyText != null)
            {
                string difficultyLabel = "Normal";
                if (value < 0.8f) difficultyLabel = "Easy";
                else if (value > 1.5f) difficultyLabel = "Hard";
                else if (value > 1.8f) difficultyLabel = "Extreme";

                difficultyText.text = $"{difficultyLabel} ({value:F2}x)";
            }
        }

        void OnMusicToggled(bool enabled)
        {
            if (AudioManager.Instance != null)
            {
                AudioManager.Instance.SetMusicMuted(!enabled);
            }
            SaveSettings();
        }

        void OnSFXToggled(bool enabled)
        {
            if (AudioManager.Instance != null)
            {
                AudioManager.Instance.SetSFXMuted(!enabled);
            }
            SaveSettings();
        }

        void OnSkipTutorialToggled(bool enabled)
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.skipTutorial = enabled;
                SaveSettings();
            }
        }

        void OnFPSCapToggled(bool enabled)
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.fpsCapEnabled = enabled;
                Application.targetFrameRate = enabled ? Constants.TARGET_FPS : -1;
                SaveSettings();
            }
        }
        #endregion

        #region Button Actions
        public void StartNight(int nightNumber)
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.StartNight(nightNumber);
                LoadGameScene();
            }
        }

        public void ContinueGame()
        {
            if (GameManager.Instance != null)
            {
                // Continue from last unlocked night
                int lastNight = Mathf.Max(1, GameManager.Instance.maxNightUnlocked - 1);
                StartNight(lastNight);
            }
        }

        public void NewGame()
        {
            StartNight(1);
        }

        public void OpenSettings()
        {
            if (mainPanel != null)
                mainPanel.SetActive(false);

            if (settingsPanel != null)
                settingsPanel.SetActive(true);
        }

        public void CloseSettings()
        {
            if (settingsPanel != null)
                settingsPanel.SetActive(false);

            if (mainPanel != null)
                mainPanel.SetActive(true);

            SaveSettings();
        }

        public void ResetProgress()
        {
            if (SaveLoadManager.Instance != null)
            {
                SaveLoadManager.Instance.ResetSaveData();
                UpdateUI();
            }
        }

        public void QuitGame()
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }

        void LoadGameScene()
        {
            // Load the game scene (you'll need to add this to Build Settings)
            SceneManager.LoadScene("Office");
        }
        #endregion
    }
}
