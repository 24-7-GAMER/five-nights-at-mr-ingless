using UnityEngine;
#if UNITY_POST_PROCESSING_STACK_V2
using UnityEngine.Rendering.PostProcessing;
#endif

namespace FiveNightsAtMrIngles.Effects
{
    /// <summary>
    /// Manages visual effects like VHS, chromatic aberration, screen distortion
    /// Optional: Requires Unity Post-Processing Stack V2 when UNITY_POST_PROCESSING_STACK_V2 is defined
    /// </summary>
    public class VisualEffectsManager : MonoBehaviour
    {
        #region Post-Processing
#if UNITY_POST_PROCESSING_STACK_V2
        [Header("Post-Processing")]
        public PostProcessVolume postProcessVolume;
        public PostProcessProfile defaultProfile;
        public PostProcessProfile horrorProfile;
        public PostProcessProfile jumpscareProfile;
#endif

        [Header("Effect Intensity")]
        [Range(0f, 1f)]
        public float vignetteIntensity = 0.4f;
        [Range(0f, 1f)]
        public float chromaticAberrationIntensity = 0.3f;
        [Range(0f, 1f)]
        public float filmGrainIntensity = 0.5f;
        [Range(0f, 1f)]
        public float screenDistortion = 0.0f;

        [Header("VHS Effect")]
        public bool enableVHSEffect = true;
        public float vhsGlitchFrequency = 0.02f;
        public Material vhsMaterial;

        [Header("Dynamic Effects")]
        public float glowIntensity = 0f;
        public float scanLineOffset = 0f;
        public float scanLineSpeed = 50f;
        #endregion

        #region Private Fields
#if UNITY_POST_PROCESSING_STACK_V2
        private Vignette vignette;
        private ChromaticAberration chromaticAberration;
        private Grain filmGrain;
        private ColorGrading colorGrading;
#endif
        private float vhsTimer = 0f;
        // Track the last night-progress value at which we updated post-processing
        private float _lastNightProgress = -1f;
        private const float NightProgressUpdateThreshold = 0.01f; // 1 % of night
        #endregion

        #region Unity Lifecycle
        void OnEnable()
        {
            GameManager.OnStateChange += HandleStateChange;
            GameManager.OnHourChange += HandleHourChange;
            PowerSystem.OnPowerOutage += HandlePowerOutage;
        }

        void OnDisable()
        {
            GameManager.OnStateChange -= HandleStateChange;
            GameManager.OnHourChange -= HandleHourChange;
            PowerSystem.OnPowerOutage -= HandlePowerOutage;
        }

        void Start()
        {
            InitializePostProcessing();
        }

        void Update()
        {
            UpdateDynamicEffects();
            UpdateVHSEffect();
        }
        #endregion

        #region Initialization
        void InitializePostProcessing()
        {
#if UNITY_POST_PROCESSING_STACK_V2
            if (postProcessVolume == null)
            {
                postProcessVolume = FindFirstObjectByType<PostProcessVolume>();

                if (postProcessVolume == null)
                {
                    Debug.LogWarning("No PostProcessVolume found. Visual effects will be limited.");
                    return;
                }
            }

            if (postProcessVolume.profile != null)
            {
                postProcessVolume.profile.TryGetSettings(out vignette);
                postProcessVolume.profile.TryGetSettings(out chromaticAberration);
                postProcessVolume.profile.TryGetSettings(out filmGrain);
                postProcessVolume.profile.TryGetSettings(out colorGrading);
            }

            ApplyDefaultEffects();
#endif
        }

        void ApplyDefaultEffects()
        {
            SetVignette(vignetteIntensity);
            SetChromaticAberration(chromaticAberrationIntensity);
            SetFilmGrain(filmGrainIntensity);
        }
        #endregion

        #region Effect Controls
        public void SetVignette(float intensity)
        {
#if UNITY_POST_PROCESSING_STACK_V2
            if (vignette == null) return;
            vignette.enabled.value = true;
            vignette.intensity.value = Mathf.Clamp01(intensity);
#endif
        }

        public void SetChromaticAberration(float intensity)
        {
#if UNITY_POST_PROCESSING_STACK_V2
            if (chromaticAberration == null) return;
            chromaticAberration.enabled.value = intensity > 0.01f;
            chromaticAberration.intensity.value = Mathf.Clamp01(intensity);
#endif
        }

        public void SetFilmGrain(float intensity)
        {
#if UNITY_POST_PROCESSING_STACK_V2
            if (filmGrain == null) return;
            filmGrain.enabled.value = intensity > 0.01f;
            filmGrain.intensity.value = Mathf.Clamp01(intensity);
#endif
        }

        public void SetColorGrading(float saturation = 0f, float temperature = 0f)
        {
#if UNITY_POST_PROCESSING_STACK_V2
            if (colorGrading == null) return;
            colorGrading.enabled.value = true;
            colorGrading.saturation.value = Mathf.Clamp(saturation, -100f, 100f);
            colorGrading.temperature.value = Mathf.Clamp(temperature, -100f, 100f);
#endif
        }
        #endregion

        #region Dynamic Effects
        void UpdateDynamicEffects()
        {
            if (GameManager.Instance != null && GameManager.Instance.currentState == GameManager.GameState.Playing)
            {
                float nightProgress = GameManager.Instance.GetNightProgress();
                // Only push new values to the post-processing stack when night progress has
                // changed meaningfully – post-processing writes are not free.
                if (Mathf.Abs(nightProgress - _lastNightProgress) >= NightProgressUpdateThreshold)
                {
                    _lastNightProgress = nightProgress;
                    float horrorMultiplier = nightProgress * 0.5f;
                    SetVignette(vignetteIntensity + horrorMultiplier * 0.3f);
                    SetChromaticAberration(chromaticAberrationIntensity + horrorMultiplier * 0.2f);
                    SetColorGrading(-20f * nightProgress, -10f * nightProgress);
                }
            }

            scanLineOffset += scanLineSpeed * Time.deltaTime;
            if (scanLineOffset > 1000f)
                scanLineOffset = 0f;
        }

        void UpdateVHSEffect()
        {
            if (!enableVHSEffect || vhsMaterial == null)
                return;

            vhsTimer += Time.deltaTime;

            if (Random.value < vhsGlitchFrequency * Time.deltaTime)
            {
                TriggerVHSGlitch();
            }
        }

        void TriggerVHSGlitch()
        {
            StartCoroutine(VHSGlitchEffect());
        }

        System.Collections.IEnumerator VHSGlitchEffect()
        {
#if UNITY_POST_PROCESSING_STACK_V2
            if (chromaticAberration == null)
                yield break;

            float originalIntensity = chromaticAberration.intensity.value;
            chromaticAberration.intensity.value = 1f;

            yield return new WaitForSeconds(0.1f);

            chromaticAberration.intensity.value = originalIntensity;
#else
            yield break;
#endif
        }
        #endregion

        #region Event Handlers
        void HandleStateChange(GameManager.GameState from, GameManager.GameState to)
        {
            switch (to)
            {
                case GameManager.GameState.Jumpscare:
                    ApplyJumpscareEffects();
                    break;

                case GameManager.GameState.Playing:
                    _lastNightProgress = -1f; // Force a full refresh on next Update
                    ApplyDefaultEffects();
                    break;

                case GameManager.GameState.Menu:
                    ApplyMenuEffects();
                    break;
            }
        }

        void HandleHourChange(int hour)
        {
            StartCoroutine(HourChangePulse());
        }

        void HandlePowerOutage()
        {
            ApplyPowerOutageEffects();
        }

        System.Collections.IEnumerator HourChangePulse()
        {
#if UNITY_POST_PROCESSING_STACK_V2
            if (vignette == null)
                yield break;

            float originalIntensity = vignette.intensity.value;

            for (float t = 0; t < 0.3f; t += Time.deltaTime)
            {
                vignette.intensity.value = Mathf.Lerp(originalIntensity, 1f, t / 0.3f);
                yield return null;
            }

            for (float t = 0; t < 0.3f; t += Time.deltaTime)
            {
                vignette.intensity.value = Mathf.Lerp(1f, originalIntensity, t / 0.3f);
                yield return null;
            }

            vignette.intensity.value = originalIntensity;
#else
            yield break;
#endif
        }
        #endregion

        #region Effect Profiles
        void ApplyJumpscareEffects()
        {
            SetVignette(1f);
            SetChromaticAberration(0.8f);
            SetFilmGrain(0.8f);
        }

        void ApplyPowerOutageEffects()
        {
            SetVignette(0.95f);
            SetChromaticAberration(0.1f);
            SetFilmGrain(0.7f);
            SetColorGrading(-80f, -30f);
        }

        void ApplyMenuEffects()
        {
            SetVignette(0.2f);
            SetChromaticAberration(0f);
            SetFilmGrain(0.2f);
            SetColorGrading(0f, 0f);
        }
        #endregion

        #region Screen Shake
        public void ScreenShake(float intensity, float duration)
        {
            StartCoroutine(ScreenShakeCoroutine(intensity, duration));
        }

        System.Collections.IEnumerator ScreenShakeCoroutine(float intensity, float duration)
        {
            Camera mainCamera = Camera.main;
            if (mainCamera == null)
                yield break;

            Vector3 originalPosition = mainCamera.transform.localPosition;
            float timer = 0f;

            while (timer < duration)
            {
                float x = Random.Range(-1f, 1f) * intensity;
                float y = Random.Range(-1f, 1f) * intensity;

                mainCamera.transform.localPosition = originalPosition + new Vector3(x, y, 0f);

                timer += Time.deltaTime;
                yield return null;
            }

            mainCamera.transform.localPosition = originalPosition;
        }
        #endregion

        #region Public Methods
        public void FlashEffect(Color color, float duration = 0.2f)
        {
            StartCoroutine(FlashCoroutine(color, duration));
        }

        System.Collections.IEnumerator FlashCoroutine(Color color, float duration)
        {
            GameObject flashObj = new GameObject("FlashEffect");
            Canvas canvas = flashObj.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 9999;

            UnityEngine.UI.Image img = flashObj.AddComponent<UnityEngine.UI.Image>();
            img.color = color;

            for (float t = 0; t < duration; t += Time.deltaTime)
            {
                Color c = img.color;
                c.a = Mathf.Lerp(1f, 0f, t / duration);
                img.color = c;
                yield return null;
            }

            Destroy(flashObj);
        }
        #endregion

        #region Debug
        [ContextMenu("Test Jumpscare Effects")]
        void TestJumpscareEffects()
        {
            ApplyJumpscareEffects();
        }

        [ContextMenu("Test Power Outage Effects")]
        void TestPowerOutageEffects()
        {
            ApplyPowerOutageEffects();
        }

        [ContextMenu("Test Screen Shake")]
        void TestScreenShake()
        {
            ScreenShake(0.5f, 1f);
        }
        #endregion
    }
}
