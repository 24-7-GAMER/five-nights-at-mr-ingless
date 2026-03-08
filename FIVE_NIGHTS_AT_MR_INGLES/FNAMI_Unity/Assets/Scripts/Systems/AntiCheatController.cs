using UnityEngine;
using System.Collections.Generic;

namespace FiveNightsAtMrIngles
{
    /// <summary>
    /// Anti-cheat and door spam logic ported from main.py.
    /// </summary>
    public class AntiCheatController : MonoBehaviour
    {
        public static AntiCheatController Instance { get; private set; }

        [Header("Anti-Cheat")]
        public bool antiCheatActive = false;
        public bool antiCheatPending = false;
        public float antiCheatTimer = 0f;

        [Header("Reflex Detection")]
        public float reflexWindowSeconds = 1.2f;
        public int reflexBlocks = 0;
        public float lastReflexTime = 0f;

        [Header("Door Spam")]
        public float spamWindowSeconds = 5f;
        public int spamToggleThreshold = 6;
        public float spamPenaltyAmount = 8f;
        public float spamDoorDamage = 15f;

        private readonly Dictionary<string, float> lastOfficeEntryTime = new Dictionary<string, float>
        {
            { "left", -999f },
            { "right", -999f },
            { "vent", -999f }
        };

        private readonly Dictionary<string, List<float>> doorToggleHistory = new Dictionary<string, List<float>>
        {
            { "left", new List<float>() },
            { "right", new List<float>() }
        };

        void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
            }
            else
            {
                Destroy(gameObject);
            }
        }

        void OnEnable()
        {
            GameManager.OnNightStart += HandleNightStart;
        }

        void OnDisable()
        {
            GameManager.OnNightStart -= HandleNightStart;
        }

        void Update()
        {
            if (GameManager.Instance == null)
                return;

            if (GameManager.Instance.currentState == GameManager.GameState.AntiCheat)
            {
                antiCheatTimer += Time.deltaTime;
                if (antiCheatTimer >= 2.0f && !antiCheatPending)
                {
                    antiCheatPending = true;
                    GameManager.Instance.TriggerJumpscare("Mr Hall");
                }
            }
        }

        public void RecordOfficeEntry(string side)
        {
            if (string.IsNullOrEmpty(side))
                return;

            lastOfficeEntryTime[side] = Time.time;
        }

        public void RegisterDoorToggle(string side)
        {
            if (GameManager.Instance == null)
                return;

            if (GameManager.Instance.currentState != GameManager.GameState.Playing)
                return;

            if (!doorToggleHistory.ContainsKey(side))
                return;

            float now = Time.time;
            doorToggleHistory[side].Add(now);
            doorToggleHistory[side].RemoveAll(t => now - t > spamWindowSeconds);

            if (doorToggleHistory[side].Count > spamToggleThreshold)
            {
                if (PowerSystem.Instance != null)
                {
                    PowerSystem.Instance.AddDoorSpamPenalty(spamPenaltyAmount);
                }

                if (OfficeController.Instance != null)
                {
                    if (side == "left")
                        OfficeController.Instance.doorLeftHealth = Mathf.Max(0f, OfficeController.Instance.doorLeftHealth - spamDoorDamage);
                    else if (side == "right")
                        OfficeController.Instance.doorRightHealth = Mathf.Max(0f, OfficeController.Instance.doorRightHealth - spamDoorDamage);
                }

                var hud = FindObjectOfType<FiveNightsAtMrIngles.UI.HUDController>();
                if (hud != null)
                {
                    hud.ShowStatus("Door mechanism stressed! Extra power drain!", 3f);
                }
            }

            CheckReflexCheat(side);
        }

        private void CheckReflexCheat(string side)
        {
            if (antiCheatActive)
                return;

            float entryTime = lastOfficeEntryTime.ContainsKey(side) ? lastOfficeEntryTime[side] : -999f;
            if (entryTime <= 0f)
                return;

            float now = Time.time;
            if (now - entryTime <= reflexWindowSeconds)
            {
                if (now - lastReflexTime > 20f)
                {
                    reflexBlocks = 0;
                }

                reflexBlocks += 1;
                lastReflexTime = now;

                if (reflexBlocks >= 1)
                {
                    TriggerAntiCheat();
                }
            }
        }

        public void TriggerAntiCheat()
        {
            if (antiCheatActive)
                return;

            antiCheatActive = true;
            antiCheatPending = false;
            antiCheatTimer = 0f;

            if (OfficeController.Instance != null)
            {
                OfficeController.Instance.CloseCameras();
                OfficeController.Instance.lightOn = false;
            }

            if (AudioManager.Instance != null)
            {
                AudioManager.Instance.StopMusic();
                AudioManager.Instance.PlaySFX("nice_try");
            }

            if (GameManager.Instance != null)
            {
                GameManager.Instance.ChangeState(GameManager.GameState.AntiCheat);
            }
        }

        public void ResetAntiCheat()
        {
            antiCheatActive = false;
            antiCheatPending = false;
            antiCheatTimer = 0f;
            reflexBlocks = 0;
            lastReflexTime = 0f;

            lastOfficeEntryTime["left"] = -999f;
            lastOfficeEntryTime["right"] = -999f;
            lastOfficeEntryTime["vent"] = -999f;

            doorToggleHistory["left"].Clear();
            doorToggleHistory["right"].Clear();
        }

        private void HandleNightStart(int night)
        {
            ResetAntiCheat();
        }
    }
}
