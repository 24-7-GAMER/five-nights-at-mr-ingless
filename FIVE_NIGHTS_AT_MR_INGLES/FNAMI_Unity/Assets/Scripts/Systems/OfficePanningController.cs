using UnityEngine;

namespace FiveNightsAtMrIngles
{
    /// <summary>
    /// Handles FNAF-style office background panning.
    /// </summary>
    public class OfficePanningController : MonoBehaviour
    {
        public RectTransform backgroundRect;
        public RectTransform viewportRect;

        [Header("Panning Settings")]
        public float zoomFactor = 1.2f;
        public float panSpeed = 0.15f;
        public float edgeThreshold = 200f;
        public float epsilon = 0.01f;

        private Vector2 baseSize;
        private Vector2 maxOffset;

        void Awake()
        {
            if (backgroundRect == null)
            {
                backgroundRect = GetComponent<RectTransform>();
            }
        }

        void Start()
        {
            if (viewportRect == null && backgroundRect != null)
            {
                viewportRect = backgroundRect.parent as RectTransform;
            }

            InitializeLayout();
        }

        void Update()
        {
            if (backgroundRect == null || viewportRect == null)
                return;

            if (viewportRect.rect.size != baseSize)
            {
                InitializeLayout();
            }

            if (GameManager.Instance == null || GameManager.Instance.currentState != GameManager.GameState.Playing)
            {
                MoveToTarget(Vector2.zero);
                return;
            }

            if (OfficeController.Instance != null && OfficeController.Instance.camerasOpen)
            {
                MoveToTarget(Vector2.zero);
                return;
            }

            Vector2 localPoint;
            if (!RectTransformUtility.ScreenPointToLocalPointInRectangle(viewportRect, Input.mousePosition, null, out localPoint))
                return;

            Vector2 local = localPoint + viewportRect.rect.size * 0.5f;

            float targetX = ComputeTargetOffset(local.x, baseSize.x, maxOffset.x);
            float targetY = ComputeTargetOffset(local.y, baseSize.y, maxOffset.y);

            MoveToTarget(new Vector2(targetX, targetY));
        }

        void InitializeLayout()
        {
            if (backgroundRect == null || viewportRect == null)
                return;

            baseSize = viewportRect.rect.size;

            backgroundRect.anchorMin = Vector2.zero;
            backgroundRect.anchorMax = Vector2.zero;
            backgroundRect.pivot = Vector2.zero;
            backgroundRect.sizeDelta = baseSize;
            backgroundRect.anchoredPosition = Vector2.zero;
            backgroundRect.localScale = new Vector3(zoomFactor, zoomFactor, 1f);

            maxOffset = new Vector2(
                baseSize.x * zoomFactor - baseSize.x,
                baseSize.y * zoomFactor - baseSize.y
            );
        }

        float ComputeTargetOffset(float position, float size, float maxAxisOffset)
        {
            if (maxAxisOffset <= 0f)
                return 0f;

            float center = size * 0.5f;
            float target = 0f;

            if (position < edgeThreshold)
            {
                target = 0f;
            }
            else if (position > size - edgeThreshold)
            {
                target = -maxAxisOffset;
            }
            else
            {
                float panRange = Mathf.Max(epsilon, center - edgeThreshold);
                float centerDistance = (position - center) / panRange;
                centerDistance = Mathf.Clamp(centerDistance, -1f, 1f);
                target = -centerDistance * maxAxisOffset;
                target = Mathf.Clamp(target, -maxAxisOffset, 0f);
            }

            return target;
        }

        void MoveToTarget(Vector2 target)
        {
            float lerpFactor = panSpeed >= 1f
                ? 1f
                : Mathf.Min(1f, 1f - Mathf.Pow(1f - panSpeed, Time.deltaTime * 60f));

            backgroundRect.anchoredPosition = Vector2.Lerp(backgroundRect.anchoredPosition, target, lerpFactor);
        }
    }
}
