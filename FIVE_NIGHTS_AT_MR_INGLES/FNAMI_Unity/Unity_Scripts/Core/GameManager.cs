using UnityEngine;
using System;
using System.Collections;

namespace FiveNightsAtMrIngles
{
    /// <summary>
    /// Central game manager - Singleton pattern
    /// Manages game state, night progression, and core game loop
    /// Converted from Python GameState class
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        #region Singleton
        public static GameManager Instance { get; private set; }

        void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
                Initialize();
            }
            else
            {
                Destroy(gameObject);
            }
        }
        #endregion

        #region Enums
        public enum GameState
        {
            Splash,
            Intro,
            Menu,
            Playing,
            Paused,
            Jumpscare,
            Win,
            AntiCheat,
            AntiCheatMessage,
            Tutorial
        }
        #endregion

        #region Public Fields
        [Header("Game State")]
        public GameState currentState = GameState.Splash;
        public int currentNight = 1;
        public int maxNightUnlocked = 1;
        
        [Header("Time Management")]
        public int currentHour = 12; // 12 AM to 6 AM
        public float hourTimer = 0f;
        public float secondsPerHour = 60f; // Adjustable night length
        public float minutesElapsed = 0f;
        
        [Header("Difficulty")]
        public float difficulty = 1.0f; // 0.5 to 2.0
        
        [Header("Game Settings")]
        public bool skipTutorial = false;
        public int targetFPS = 60;
        public bool fpsCapEnabled = true;

        [Header("Intro")]
        public bool introSeen = false;
        public float introMessageDuration = 1.5f;
        public string[] introMessages = new string[]
        {
            "YOU'RE IN THE SCIENCE BLOCK.",
            "ALONE.",
            "HIDING IN MR. INGLES'S OFFICE.",
            "MR. INGLES AND HIS ARMY ARE WATCHING.",
            "DON'T GET CAUGHT."
        };
        #endregion

        #region Events
        public static event Action<int> OnHourChange;
        public static event Action<int> OnNightStart;
        public static event Action OnNightWin;
        public static event Action OnGameOver;
        public static event Action<GameState, GameState> OnStateChange;
        #endregion

        #region Private Fields
        private float gameStartTime;
        private Coroutine nightProgressCoroutine;
        #endregion

        #region Initialization
        void Initialize()
        {
            Application.targetFrameRate = targetFPS;
            gameStartTime = Time.time;
            
            // Subscribe to events
            PowerSystem.OnPowerOutage += HandlePowerOutage;
        }

        void Start()
        {
            if (currentState != GameState.Splash)
            {
                currentState = GameState.Splash;
            }
        }

        void OnDestroy()
        {
            // Unsubscribe from events
            PowerSystem.OnPowerOutage -= HandlePowerOutage;
        }
        #endregion

        #region State Management
        public void ChangeState(GameState newState)
        {
            GameState previousState = currentState;
            currentState = newState;
            
            Debug.Log($"State changed: {previousState} → {newState}");
            OnStateChange?.Invoke(previousState, newState);
            
            HandleStateTransition(previousState, newState);
        }

        void HandleStateTransition(GameState from, GameState to)
        {
            switch (to)
            {
                case GameState.Splash:
                    // Load splash screen
                    break;
                    
                case GameState.Menu:
                    // Show main menu
                    StopNightProgress();
                    break;
                    
                case GameState.Playing:
                    // Start gameplay
                    StartNightProgress();
                    break;
                    
                case GameState.Paused:
                    Time.timeScale = 0f;
                    break;
                    
                case GameState.Jumpscare:
                    StopNightProgress();
                    break;
                    
                case GameState.Win:
                    StopNightProgress();
                    HandleNightWin();
                    break;
            }
            
            // Resume time if unpaused
            if (from == GameState.Paused && to == GameState.Playing)
            {
                Time.timeScale = 1f;
            }
        }
        #endregion

        #region Night Management
        public void StartNight(int nightNumber)
        {
            currentNight = nightNumber;
            currentHour = 12;
            hourTimer = 0f;
            minutesElapsed = 0f;
            gameStartTime = Time.time;
            
            Debug.Log($"Starting Night {nightNumber}");
            OnNightStart?.Invoke(nightNumber);
            OnHourChange?.Invoke(12);
            
            // Reset systems
            if (PowerSystem.Instance != null)
                PowerSystem.Instance.ResetPower();
            
            if (OfficeController.Instance != null)
                OfficeController.Instance.ResetOffice();
            
            // Determine if intro/tutorial should play
            if (nightNumber == 1 && !introSeen)
            {
                introSeen = true;
                ChangeState(GameState.Intro);
                return;
            }

            if (nightNumber == 1 && !skipTutorial)
            {
                ChangeState(GameState.Tutorial);
            }
            else
            {
                ChangeState(GameState.Playing);
            }
        }

        void StartNightProgress()
        {
            if (nightProgressCoroutine != null)
                StopCoroutine(nightProgressCoroutine);
            
            nightProgressCoroutine = StartCoroutine(NightProgressRoutine());
        }

        void StopNightProgress()
        {
            if (nightProgressCoroutine != null)
            {
                StopCoroutine(nightProgressCoroutine);
                nightProgressCoroutine = null;
            }
        }

        IEnumerator NightProgressRoutine()
        {
            while (minutesElapsed < 6f * 60f)
            {
                yield return null;

                if (currentState != GameState.Playing)
                    continue;

                float secondsPerMinute = Mathf.Max(0.01f, secondsPerHour / 60f);
                hourTimer += Time.deltaTime;

                while (hourTimer >= secondsPerMinute)
                {
                    hourTimer -= secondsPerMinute;
                    minutesElapsed += 1f;

                    if (minutesElapsed % 60f == 0f && minutesElapsed < 6f * 60f)
                    {
                        int displayHour = Mathf.Clamp((int)(minutesElapsed / 60f), 1, 6);
                        currentHour = 12 + displayHour;
                        Debug.Log($"Hour: {displayHour} AM");
                        OnHourChange?.Invoke(displayHour);
                    }

                    if (minutesElapsed >= 6f * 60f)
                    {
                        WinNight();
                        break;
                    }
                }
            }
        }

        void WinNight()
        {
            Debug.Log($"Night {currentNight} completed!");
            
            // Unlock next night
            if (currentNight >= maxNightUnlocked)
            {
                maxNightUnlocked = Mathf.Min(currentNight + 1, 5);
                SaveLoadManager.Instance?.SaveProgress();
            }
            
            OnNightWin?.Invoke();
            ChangeState(GameState.Win);
        }

        void HandleNightWin()
        {
            // Handle win screen, statistics, etc.
        }
        #endregion

        #region Game Over
        public void TriggerJumpscare(string animatronicName)
        {
            Debug.Log($"Jumpscare triggered by: {animatronicName}");
            OnGameOver?.Invoke();
            ChangeState(GameState.Jumpscare);
            
            // Play jumpscare animation/sound
            // TODO: Implement jumpscare system
        }

        void HandlePowerOutage()
        {
            Debug.Log("Power outage! Freddy's coming...");
            // Special power outage sequence
            // In original game, Freddy attacks after random time
        }
        #endregion

        #region Utility
        public float GetElapsedTime()
        {
            return Time.time - gameStartTime;
        }

        public float GetNightProgress()
        {
            // Returns 0.0 to 1.0 representing night completion
            return Mathf.Clamp01(minutesElapsed / (6f * 60f));
        }

        public string GetTimeString()
        {
            int elapsedHours = Mathf.FloorToInt(minutesElapsed / 60f);
            int displayHour = elapsedHours == 0 ? 12 : Mathf.Clamp(elapsedHours, 1, 6);
            return $"{displayHour} AM";
        }
        #endregion

        #region Debug
        [ContextMenu("Win Current Night")]
        void DebugWinNight()
        {
            WinNight();
        }

        [ContextMenu("Trigger Test Jumpscare")]
        void DebugJumpscare()
        {
            TriggerJumpscare("Test Animatronic");
        }
        #endregion
    }
}
