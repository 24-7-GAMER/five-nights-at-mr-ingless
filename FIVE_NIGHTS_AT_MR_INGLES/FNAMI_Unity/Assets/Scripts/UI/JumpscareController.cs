using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using FiveNightsAtMrIngles;

namespace FiveNightsAtMrIngles.UI
{
    /// <summary>
    /// Controls jumpscare sequence and death screen
    /// </summary>
    public class JumpscareController : MonoBehaviour
    {
        #region UI Elements
        [Header("Jumpscare Panel")]
        public GameObject jumpscarePanel;
        public Image jumpscareImage;
        public Text jumpscareText;
        public Animator jumpscareAnimator;

        [Header("Death Screen")]
        public GameObject deathScreenPanel;
        public Text deathMessageText;
        public Text killedByText;
        public Text nightCompletedText;
        public Button restartButton;
        public Button menuButton;

        [Header("Settings")]
        public float jumpscareDuration = 2.0f;
        public float imageZoomSpeed = 3f;
        public float shakeIntensity = 20f;

        [Header("Jumpscare Sprites")]
        public Sprite defaultJumpscareSprite;
        // Add specific sprites for each animatronic if available
        #endregion

        #region Private Fields
        private bool isPlaying = false;
        private string killerName = "";
        #endregion

        #region Unity Lifecycle
        void OnEnable()
        {
            GameManager.OnGameOver += TriggerJumpscare;
        }

        void OnDisable()
        {
            GameManager.OnGameOver -= TriggerJumpscare;
        }

        void Start()
        {
            if (jumpscarePanel != null)
                jumpscarePanel.SetActive(false);

            if (deathScreenPanel != null)
                deathScreenPanel.SetActive(false);

            SetupButtons();
        }
        #endregion

        #region Setup
        void SetupButtons()
        {
            if (restartButton != null)
            {
                restartButton.onClick.AddListener(() => 
                {
                    if (GameManager.Instance != null)
                    {
                        GameManager.Instance.StartNight(GameManager.Instance.currentNight);
                        HideDeathScreen();
                    }
                });
            }

            if (menuButton != null)
            {
                menuButton.onClick.AddListener(() => 
                {
                    if (GameManager.Instance != null)
                    {
                        GameManager.Instance.ChangeState(GameManager.GameState.Menu);
                        HideDeathScreen();
                        // Load menu scene
                        UnityEngine.SceneManagement.SceneManager.LoadScene("MainMenu");
                    }
                });
            }
        }
        #endregion

        #region Jumpscare
        void TriggerJumpscare()
        {
            if (isPlaying) return;

            // Get killer name from current animatronic threat
            // For now, use a generic name
            killerName = "Mr Ingles";

            StartCoroutine(PlayJumpscareSequence());
        }

        public void TriggerJumpscareWithName(string animatronicName)
        {
            killerName = animatronicName;
            StartCoroutine(PlayJumpscareSequence());
        }

        IEnumerator PlayJumpscareSequence()
        {
            isPlaying = true;

            // Show jumpscare panel
            if (jumpscarePanel != null)
            {
                jumpscarePanel.SetActive(true);
            }

            // Set jumpscare image
            if (jumpscareImage != null && defaultJumpscareSprite != null)
            {
                jumpscareImage.sprite = defaultJumpscareSprite;
                jumpscareImage.transform.localScale = Vector3.one * 0.5f;
            }

            // Set jumpscare text
            if (jumpscareText != null)
            {
                jumpscareText.text = killerName.ToUpper();
            }

            // Play jumpscare sound
            if (AudioManager.Instance != null)
            {
                AudioManager.Instance.PlaySFX("jumpscare");
            }

            // Animate jumpscare
            float timer = 0f;
            Vector3 originalPosition = Vector3.zero;
            if (jumpscareImage != null)
            {
                originalPosition = jumpscareImage.transform.localPosition;
            }

            while (timer < jumpscareDuration)
            {
                timer += Time.deltaTime;
                float t = timer / jumpscareDuration;

                // Zoom in effect
                if (jumpscareImage != null)
                {
                    float scale = Mathf.Lerp(0.5f, 2.5f, t);
                    jumpscareImage.transform.localScale = Vector3.one * scale;

                    // Screen shake
                    float shakeX = Random.Range(-shakeIntensity, shakeIntensity) * (1f - t);
                    float shakeY = Random.Range(-shakeIntensity, shakeIntensity) * (1f - t);
                    jumpscareImage.transform.localPosition = originalPosition + new Vector3(shakeX, shakeY, 0f);
                }

                yield return null;
            }

            // Hide jumpscare panel
            if (jumpscarePanel != null)
            {
                jumpscarePanel.SetActive(false);
            }

            // Show death screen
            ShowDeathScreen();

            isPlaying = false;
        }
        #endregion

        #region Death Screen
        void ShowDeathScreen()
        {
            if (deathScreenPanel != null)
            {
                deathScreenPanel.SetActive(true);
            }

            if (deathMessageText != null)
            {
                deathMessageText.text = GetRandomDeathMessage();
            }

            if (killedByText != null)
            {
                killedByText.text = $"Killed by: {killerName}";
            }

            if (nightCompletedText != null && GameManager.Instance != null)
            {
                nightCompletedText.text = $"Night {GameManager.Instance.currentNight} - {GameManager.Instance.GetTimeString()}";
            }
        }

        void HideDeathScreen()
        {
            if (deathScreenPanel != null)
            {
                deathScreenPanel.SetActive(false);
            }

            if (jumpscarePanel != null)
            {
                jumpscarePanel.SetActive(false);
            }
        }

        string GetRandomDeathMessage()
        {
            string[] messages = new string[]
            {
                "YOU DIED",
                "GAME OVER",
                "THEY GOT YOU",
                "YOU FAILED",
                "BETTER LUCK NEXT TIME",
                "TRY AGAIN",
                "YOU WERE NOT CAREFUL ENOUGH"
            };

            return messages[Random.Range(0, messages.Length)];
        }
        #endregion

        #region Public Methods
        public void SetJumpscareSprite(Sprite sprite)
        {
            if (jumpscareImage != null && sprite != null)
            {
                jumpscareImage.sprite = sprite;
            }
        }
        #endregion
    }
}
