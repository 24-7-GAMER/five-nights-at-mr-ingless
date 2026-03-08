using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;
using FiveNightsAtMrIngles;

namespace FiveNightsAtMrIngles.UI
{
    /// <summary>
    /// Controls pause menu functionality
    /// </summary>
    public class PauseMenuController : MonoBehaviour
    {
        #region UI Elements
        [Header("Pause Menu")]
        public GameObject pauseMenuPanel;
        public Button resumeButton;
        public Button restartButton;
        public Button settingsButton;
        public Button mainMenuButton;
        public Button quitButton;

        [Header("Settings Panel")]
        public GameObject settingsPanel;
        public Slider volumeSlider;
        public Toggle musicToggle;
        public Toggle sfxToggle;
        #endregion

        #region Private Fields
        private bool isPaused = false;
        #endregion

        #region Unity Lifecycle
        void OnEnable()
        {
            GameManager.OnStateChange += HandleStateChange;
        }

        void OnDisable()
        {
            GameManager.OnStateChange -= HandleStateChange;
        }

        void Start()
        {
            if (pauseMenuPanel != null)
                pauseMenuPanel.SetActive(false);

            if (settingsPanel != null)
                settingsPanel.SetActive(false);

            SetupButtons();
        }

        void Update()
        {
            // Handle pause input
            if (Input.GetKeyDown(KeyCode.Escape) || Input.GetKeyDown(KeyCode.P))
            {
                if (GameManager.Instance != null)
                {
                    if (GameManager.Instance.currentState == GameManager.GameState.Playing)
                    {
                        PauseGame();
                    }
                    else if (GameManager.Instance.currentState == GameManager.GameState.Paused)
                    {
                        ResumeGame();
                    }
                }
            }
        }
        #endregion

        #region Setup
        void SetupButtons()
        {
            if (resumeButton != null)
                resumeButton.onClick.AddListener(ResumeGame);

            if (restartButton != null)
                restartButton.onClick.AddListener(RestartNight);

            if (settingsButton != null)
                settingsButton.onClick.AddListener(OpenSettings);

            if (mainMenuButton != null)
                mainMenuButton.onClick.AddListener(ReturnToMainMenu);

            if (quitButton != null)
                quitButton.onClick.AddListener(QuitGame);
        }
        #endregion

        #region Event Handlers
        void HandleStateChange(GameManager.GameState from, GameManager.GameState to)
        {
            if (to == GameManager.GameState.Paused)
            {
                ShowPauseMenu();
            }
            else if (from == GameManager.GameState.Paused)
            {
                HidePauseMenu();
            }
        }
        #endregion

        #region Pause Menu Actions
        public void PauseGame()
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.ChangeState(GameManager.GameState.Paused);
            }
        }

        public void ResumeGame()
        {
            if (settingsPanel != null && settingsPanel.activeSelf)
            {
                CloseSettings();
                return;
            }

            if (GameManager.Instance != null)
            {
                GameManager.Instance.ChangeState(GameManager.GameState.Playing);
            }
        }

        public void RestartNight()
        {
            if (GameManager.Instance != null)
            {
                Time.timeScale = 1f; // Unpause
                GameManager.Instance.StartNight(GameManager.Instance.currentNight);
                HidePauseMenu();
            }
        }

        public void OpenSettings()
        {
            if (pauseMenuPanel != null)
                pauseMenuPanel.SetActive(false);

            if (settingsPanel != null)
                settingsPanel.SetActive(true);
        }

        public void CloseSettings()
        {
            if (settingsPanel != null)
                settingsPanel.SetActive(false);

            if (pauseMenuPanel != null)
                pauseMenuPanel.SetActive(true);
        }

        public void ReturnToMainMenu()
        {
            Time.timeScale = 1f; // Unpause
            
            if (GameManager.Instance != null)
            {
                GameManager.Instance.ChangeState(GameManager.GameState.Menu);
            }

            // Load main menu scene
            SceneManager.LoadScene("MainMenu");
        }

        public void QuitGame()
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }
        #endregion

        #region UI Display
        void ShowPauseMenu()
        {
            isPaused = true;

            if (pauseMenuPanel != null)
            {
                pauseMenuPanel.SetActive(true);
            }

            // Ensure settings panel is hidden
            if (settingsPanel != null)
            {
                settingsPanel.SetActive(false);
            }
        }

        void HidePauseMenu()
        {
            isPaused = false;

            if (pauseMenuPanel != null)
            {
                pauseMenuPanel.SetActive(false);
            }

            if (settingsPanel != null)
            {
                settingsPanel.SetActive(false);
            }
        }
        #endregion
    }
}
