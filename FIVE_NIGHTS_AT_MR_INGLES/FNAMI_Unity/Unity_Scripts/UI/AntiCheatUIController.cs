using UnityEngine;
using UnityEngine.UI;
using FiveNightsAtMrIngles;

namespace FiveNightsAtMrIngles.UI
{
    /// <summary>
    /// Displays anti-cheat warning and message screens.
    /// </summary>
    public class AntiCheatUIController : MonoBehaviour
    {
        [Header("Warning UI")]
        public GameObject warningPanel;
        public Image mrHallImage;
        public Text warningText;

        [Header("Message UI")]
        public GameObject messagePanel;
        public Text[] messageLines;

        void OnEnable()
        {
            GameManager.OnStateChange += HandleStateChange;
            JumpscareController.OnJumpscareComplete += HandleJumpscareComplete;
        }

        void OnDisable()
        {
            GameManager.OnStateChange -= HandleStateChange;
            JumpscareController.OnJumpscareComplete -= HandleJumpscareComplete;
        }

        void Update()
        {
            if (GameManager.Instance == null)
                return;

            if (GameManager.Instance.currentState == GameManager.GameState.AntiCheat)
            {
                UpdateWarningFade();
            }
        }

        void HandleStateChange(GameManager.GameState from, GameManager.GameState to)
        {
            if (warningPanel != null)
                warningPanel.SetActive(to == GameManager.GameState.AntiCheat);

            if (messagePanel != null)
                messagePanel.SetActive(to == GameManager.GameState.AntiCheatMessage);

            if (to == GameManager.GameState.AntiCheatMessage)
            {
                UpdateMessageLines();
            }
        }

        void HandleJumpscareComplete(string killer)
        {
            if (AntiCheatController.Instance != null && AntiCheatController.Instance.antiCheatPending)
            {
                if (GameManager.Instance != null)
                {
                    GameManager.Instance.ChangeState(GameManager.GameState.AntiCheatMessage);
                }
            }
        }

        void UpdateWarningFade()
        {
            if (warningText == null || AntiCheatController.Instance == null)
                return;

            float t = AntiCheatController.Instance.antiCheatTimer;
            float duration = 2f;
            float fade = Mathf.Clamp01(t / duration);
            float alpha = 1f - Mathf.Abs(fade - 0.5f) * 2f;

            Color c = warningText.color;
            c.a = alpha;
            warningText.color = c;
        }

        void UpdateMessageLines()
        {
            if (messageLines == null || messageLines.Length == 0)
                return;

            string[] lines = new string[]
            {
                "WE DON'T LIKE CHEATERS.",
                "PLAY THE GAME NORMALLY, WITHOUT ABUSING REFLEXES.",
                "PRESS M TO RETURN TO MENU"
            };

            for (int i = 0; i < messageLines.Length && i < lines.Length; i++)
            {
                if (messageLines[i] != null)
                {
                    messageLines[i].text = lines[i];
                }
            }
        }
    }
}
