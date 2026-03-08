using UnityEngine;
using System;

namespace FiveNightsAtMrIngles
{
    /// <summary>
    /// Manages power consumption and outage mechanics
    /// Converted from Python PowerSystem class
    /// </summary>
    public class PowerSystem : MonoBehaviour
    {
        #region Singleton
        public static PowerSystem Instance { get; private set; }

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
        #endregion

        #region Public Fields
        [Header("Power Settings")]
        public float maxPower = 100f;
        public float currentPower = 100f;
        
        [Header("Drain Rates (per second)")]
        public float baseDrain = 0.16f;
        public float doorDrain = 0.24f;
        public float lightDrain = 0.24f;
        public float cameraDrain = 0.32f;
        
        [Header("Power Outage")]
        public bool isPowerOut = false;
        public float emergencyTimer = 0f;
        public float reservePower = 0f;

        [Header("Spam Penalty")]
        public float doorSpamPenalty = 0f;
        #endregion

        #region Events
        public static event Action OnPowerOutage;
        public static event Action<float> OnPowerChanged; // Sends current power %
        public static event Action OnPowerRestored;
        #endregion

        #region Unity Lifecycle
        void Update()
        {
            if (GameManager.Instance == null || GameManager.Instance.currentState != GameManager.GameState.Playing)
                return;
            
            if (!isPowerOut)
            {
                DrainPower();
            }
            else
            {
                HandlePowerOutage();
            }
        }
        #endregion

        #region Power Management
        void DrainPower()
        {
            float speedRatio = GameManager.Instance != null ? GameManager.Instance.secondsPerHour / 60f : 1f;
            float speedMultiplier = 0.5f + (speedRatio * 0.5f);
            int minuteInHour = GameManager.Instance != null ? (int)(GameManager.Instance.minutesElapsed % 60f) : 0;
            bool surgeActive = (minuteInHour >= 15 && minuteInHour <= 17)
                || (minuteInHour >= 30 && minuteInHour <= 32)
                || (minuteInHour >= 45 && minuteInHour <= 47);
            float surgeMultiplier = surgeActive ? 1.35f : 1f;
            float diffMultiplier = GameManager.Instance != null ? GameManager.Instance.difficulty : 1f;

            float totalDrain = baseDrain * speedMultiplier * surgeMultiplier * diffMultiplier;

            if (OfficeController.Instance != null)
            {
                if (OfficeController.Instance.doorLeftClosed || OfficeController.Instance.doorRightClosed)
                    totalDrain += doorDrain * speedMultiplier * surgeMultiplier * diffMultiplier;

                if (OfficeController.Instance.lightOn)
                    totalDrain += lightDrain * speedMultiplier * surgeMultiplier * diffMultiplier;

                if (OfficeController.Instance.camerasOpen)
                    totalDrain += cameraDrain * speedMultiplier * surgeMultiplier * diffMultiplier;
            }

            if (doorSpamPenalty > 0f)
            {
                totalDrain += doorSpamPenalty * Time.deltaTime;
                doorSpamPenalty = Mathf.Max(0f, doorSpamPenalty - Time.deltaTime * 2f);
            }

            currentPower -= totalDrain * Time.deltaTime;
            currentPower = Mathf.Max(0f, currentPower);
            
            // Notify listeners
            OnPowerChanged?.Invoke(GetPowerPercentage());
            
            // Check for power outage
            if (currentPower <= 0f && !isPowerOut)
            {
                TriggerPowerOutage();
            }
        }

        void TriggerPowerOutage()
        {
            isPowerOut = true;
            emergencyTimer = 0f;
            
            Debug.LogWarning("POWER OUTAGE!");
            OnPowerOutage?.Invoke();
            
            // Force close all systems
            if (OfficeController.Instance != null)
            {
                OfficeController.Instance.ForceCloseAllSystems();
            }
        }

        void HandlePowerOutage()
        {
            emergencyTimer += Time.deltaTime;
            
            // After random time (5-20 seconds), trigger jumpscare
            float jumpscareTime = UnityEngine.Random.Range(5f, 20f);
            if (emergencyTimer >= jumpscareTime)
            {
                GameManager.Instance?.TriggerJumpscare("Mr Ingles (Power Outage)");
            }
        }
        #endregion

        #region Public Methods
        public void ResetPower()
        {
            currentPower = maxPower;
            isPowerOut = false;
            emergencyTimer = 0f;
            reservePower = 0f;
            
            OnPowerChanged?.Invoke(100f);
            Debug.Log("Power system reset.");
        }

        public void AddPower(float amount)
        {
            if (isPowerOut) return;
            
            currentPower = Mathf.Min(maxPower, currentPower + amount);
            OnPowerChanged?.Invoke(GetPowerPercentage());
        }

        public void DrainPowerInstant(float amount)
        {
            currentPower -= amount;
            currentPower = Mathf.Max(0f, currentPower);
            OnPowerChanged?.Invoke(GetPowerPercentage());
            
            if (currentPower <= 0f && !isPowerOut)
            {
                TriggerPowerOutage();
            }
        }

        public float GetPowerPercentage()
        {
            return (currentPower / maxPower) * 100f;
        }

        public float GetCurrentDrainRate()
        {
            if (isPowerOut) return 0f;
            
            float speedRatio = GameManager.Instance != null ? GameManager.Instance.secondsPerHour / 60f : 1f;
            float speedMultiplier = 0.5f + (speedRatio * 0.5f);
            int minuteInHour = GameManager.Instance != null ? (int)(GameManager.Instance.minutesElapsed % 60f) : 0;
            bool surgeActive = (minuteInHour >= 15 && minuteInHour <= 17)
                || (minuteInHour >= 30 && minuteInHour <= 32)
                || (minuteInHour >= 45 && minuteInHour <= 47);
            float surgeMultiplier = surgeActive ? 1.35f : 1f;
            float diffMultiplier = GameManager.Instance != null ? GameManager.Instance.difficulty : 1f;

            float totalDrain = baseDrain * speedMultiplier * surgeMultiplier * diffMultiplier;

            if (OfficeController.Instance != null)
            {
                if (OfficeController.Instance.doorLeftClosed || OfficeController.Instance.doorRightClosed)
                    totalDrain += doorDrain * speedMultiplier * surgeMultiplier * diffMultiplier;
                if (OfficeController.Instance.lightOn)
                    totalDrain += lightDrain * speedMultiplier * surgeMultiplier * diffMultiplier;
                if (OfficeController.Instance.camerasOpen)
                    totalDrain += cameraDrain * speedMultiplier * surgeMultiplier * diffMultiplier;
            }

            return totalDrain;
        }

        public void AddDoorSpamPenalty(float amount)
        {
            doorSpamPenalty += amount;
        }
        #endregion

        #region Debug
        [ContextMenu("Drain 50% Power")]
        void DebugDrain50()
        {
            DrainPowerInstant(maxPower * 0.5f);
        }

        [ContextMenu("Trigger Power Outage")]
        void DebugPowerOutage()
        {
            currentPower = 0f;
            TriggerPowerOutage();
        }

        [ContextMenu("Restore Full Power")]
        void DebugRestorePower()
        {
            ResetPower();
        }
        #endregion
    }
}
