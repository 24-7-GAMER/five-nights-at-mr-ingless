using UnityEngine;
using UnityEngine.UI;
using FiveNightsAtMrIngles;

namespace FiveNightsAtMrIngles.UI
{
    /// <summary>
    /// Intro text sequence controller for Night 1.
    /// </summary>
    public class IntroController : MonoBehaviour
    {
        [Header("UI")]
        public GameObject introPanel;
        public Text introText;
        public Image fadeOverlay;

        [Header("Settings")]
        public float fadeInPortion = 0.2f;
        public float holdPortion = 0.6f;

        private int currentIndex = 0;
        private float timer = 0f;
        private float[] durations;

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
            if (introPanel != null)
                introPanel.SetActive(false);
        }

        void Update()
        {
            if (GameManager.Instance == null || GameManager.Instance.currentState != GameManager.GameState.Intro)
                return;

            if (GameManager.Instance.introMessages == null || GameManager.Instance.introMessages.Length == 0)
                return;

            timer += Time.deltaTime;

            float d = GetDuration(currentIndex);
            if (timer >= d)
            {
                timer = 0f;
                currentIndex++;
                if (currentIndex >= GameManager.Instance.introMessages.Length)
                {
                    EndIntro();
                    return;
                }
            }

            UpdateVisuals();
        }

        private void HandleStateChange(GameManager.GameState from, GameManager.GameState to)
        {
            if (to == GameManager.GameState.Intro)
            {
                BeginIntro();
            }
            else if (from == GameManager.GameState.Intro)
            {
                if (introPanel != null)
                    introPanel.SetActive(false);
            }
        }

        private void BeginIntro()
        {
            currentIndex = 0;
            timer = 0f;
            durations = null;

            if (introPanel != null)
                introPanel.SetActive(true);

            if (AudioManager.Instance != null)
            {
                AudioManager.Instance.PlaySFX("intro_msg");
            }

            UpdateVisuals();
        }

        private void UpdateVisuals()
        {
            string[] messages = GameManager.Instance.introMessages;
            if (currentIndex >= messages.Length) return;

            if (introText != null)
                introText.text = messages[currentIndex];

            float duration = GetDuration(currentIndex);
            float fadeIn = duration * fadeInPortion;
            float hold = duration * holdPortion;
            float fadeOut = Mathf.Max(0f, duration - (fadeIn + hold));

            float alpha = 1f;
            if (timer < fadeIn)
            {
                alpha = Mathf.Clamp01(timer / Mathf.Max(0.001f, fadeIn));
            }
            else if (timer < fadeIn + hold)
            {
                alpha = 1f;
            }
            else if (fadeOut > 0f)
            {
                float t = (timer - fadeIn - hold) / Mathf.Max(0.001f, fadeOut);
                alpha = 1f - Mathf.Clamp01(t);
            }

            if (introText != null)
            {
                Color c = introText.color;
                c.a = alpha;
                introText.color = c;
            }

            if (fadeOverlay != null)
            {
                Color c = fadeOverlay.color;
                c.a = 1f - alpha;
                fadeOverlay.color = c;
            }
        }

        private void EndIntro()
        {
            if (introPanel != null)
                introPanel.SetActive(false);

            if (GameManager.Instance != null)
            {
                if (!GameManager.Instance.skipTutorial)
                {
                    GameManager.Instance.ChangeState(GameManager.GameState.Tutorial);
                }
                else
                {
                    GameManager.Instance.ChangeState(GameManager.GameState.Playing);
                }
            }
        }

        private float GetDuration(int index)
        {
            if (durations == null)
            {
                durations = new float[GameManager.Instance.introMessages.Length];
                for (int i = 0; i < durations.Length; i++)
                {
                    durations[i] = Mathf.Max(0.4f, GameManager.Instance.introMessageDuration);
                }
            }

            return durations[Mathf.Clamp(index, 0, durations.Length - 1)];
        }
    }
}
