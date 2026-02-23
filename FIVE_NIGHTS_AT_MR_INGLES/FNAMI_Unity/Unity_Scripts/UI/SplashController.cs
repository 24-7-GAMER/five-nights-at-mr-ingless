using UnityEngine;
using UnityEngine.UI;
using FiveNightsAtMrIngles;

namespace FiveNightsAtMrIngles.UI
{
    /// <summary>
    /// Splash + ToS sequence controller.
    /// Matches main.py splash flow with timed fades and ToS checkbox gating.
    /// </summary>
    public class SplashController : MonoBehaviour
    {
        [Header("UI")]
        public Image splashImage;
        public Image fadeOverlay;
        public Toggle tosToggle;
        public Text tosLabel;
        public Text tosHint;

        [Header("Sequence")]
        public Sprite[] splashSprites;
        public float[] fadeInDurations;
        public float[] holdDurations;
        public float[] fadeOutDurations;
        public int tosStageIndex = 2;

        private int stageIndex = 0;
        private float stageTimer = 0f;

        void Start()
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.ChangeState(GameManager.GameState.Splash);
            }

            SetStage(0);
        }

        void Update()
        {
            if (GameManager.Instance == null || GameManager.Instance.currentState != GameManager.GameState.Splash)
                return;

            if (splashSprites == null || splashSprites.Length == 0)
                return;

            float fadeIn = GetDuration(fadeInDurations, stageIndex, 1f);
            float hold = GetDuration(holdDurations, stageIndex, 1f);
            float fadeOut = GetDuration(fadeOutDurations, stageIndex, 1f);
            float total = fadeIn + hold + fadeOut;

            stageTimer += Time.deltaTime;

            UpdateFade(fadeIn, hold, fadeOut);

            if (stageTimer >= total)
            {
                stageIndex++;
                if (stageIndex >= splashSprites.Length)
                {
                    EndSplash();
                }
                else
                {
                    SetStage(stageIndex);
                }
            }
        }

        private void UpdateFade(float fadeIn, float hold, float fadeOut)
        {
            float alpha = 1f;
            if (stageTimer <= fadeIn)
            {
                alpha = Mathf.Clamp01(stageTimer / Mathf.Max(0.001f, fadeIn));
            }
            else if (stageTimer <= fadeIn + hold)
            {
                alpha = 1f;
            }
            else
            {
                float t = (stageTimer - fadeIn - hold) / Mathf.Max(0.001f, fadeOut);
                alpha = 1f - Mathf.Clamp01(t);
            }

            if (fadeOverlay != null)
            {
                Color c = fadeOverlay.color;
                c.a = 1f - alpha;
                fadeOverlay.color = c;
            }
        }

        private void SetStage(int index)
        {
            stageTimer = 0f;

            if (splashImage != null && index >= 0 && index < splashSprites.Length)
            {
                splashImage.sprite = splashSprites[index];
                splashImage.preserveAspect = true;
            }

            // ToS UI elements hidden - auto-proceeding
            if (tosToggle != null)
                tosToggle.gameObject.SetActive(false);
            if (tosLabel != null)
                tosLabel.gameObject.SetActive(false);
            if (tosHint != null)
                tosHint.gameObject.SetActive(false);
        }

        private void EndSplash()
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.ChangeState(GameManager.GameState.Menu);
            }

            gameObject.SetActive(false);
        }

        private float GetDuration(float[] list, int index, float fallback)
        {
            if (list == null || list.Length == 0) return fallback;
            if (index < 0 || index >= list.Length) return list[list.Length - 1];
            return list[index];
        }
    }
}
