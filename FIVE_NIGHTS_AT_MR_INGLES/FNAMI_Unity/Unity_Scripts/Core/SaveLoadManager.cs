using UnityEngine;
using System.IO;
using System;

namespace FiveNightsAtMrIngles
{
    /// <summary>
    /// Handles save/load functionality using JSON
    /// Converted from Python save/load system
    /// </summary>
    public class SaveLoadManager : MonoBehaviour
    {
        #region Singleton
        public static SaveLoadManager Instance { get; private set; }

        void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else
            {
                Destroy(gameObject);
            }
        }
        #endregion

        #region Save Data Structure
        [Serializable]
        public class SaveData
        {
            public int maxNightUnlocked = 1;
            public float secondsPerHour = 60f;
            public float difficulty = 1.0f;
            public bool musicMuted = false;
            public bool sfxMuted = false;
            public bool skipTutorial = false;
            public bool fpsCapEnabled = true;
            public string lastPlayedVersion = "1.0.0";
        }
        #endregion

        #region Private Fields
        private string saveFilePath;
        private SaveData currentSaveData;
        #endregion

        #region Initialization
        void Start()
        {
            saveFilePath = Path.Combine(Application.persistentDataPath, Constants.SAVE_FILE_NAME);
            Debug.Log($"Save file path: {saveFilePath}");
            
            LoadProgress();
        }
        #endregion

        #region Save/Load
        public void SaveProgress()
        {
            try
            {
                SaveData data = new SaveData();
                
                // Gather data from game systems
                if (GameManager.Instance != null)
                {
                    data.maxNightUnlocked = GameManager.Instance.maxNightUnlocked;
                    data.secondsPerHour = GameManager.Instance.secondsPerHour;
                    data.difficulty = GameManager.Instance.difficulty;
                    data.skipTutorial = GameManager.Instance.skipTutorial;
                    data.fpsCapEnabled = GameManager.Instance.fpsCapEnabled;
                }

                if (AudioManager.Instance != null)
                {
                    data.musicMuted = AudioManager.Instance.musicMuted;
                    data.sfxMuted = AudioManager.Instance.sfxMuted;
                }
                
                data.lastPlayedVersion = Application.version;
                
                // Convert to JSON
                string json = JsonUtility.ToJson(data, true);
                
                // Write to file
                File.WriteAllText(saveFilePath, json);
                
                currentSaveData = data;
                
                Debug.Log($"Progress saved successfully to: {saveFilePath}");
            }
            catch (Exception e)
            {
                Debug.LogError($"Failed to save progress: {e.Message}");
            }
        }

        public void LoadProgress()
        {
            try
            {
                if (!File.Exists(saveFilePath))
                {
                    Debug.Log("No save file found. Creating new save data.");
                    currentSaveData = new SaveData();
                    SaveProgress();
                    return;
                }
                
                // Read JSON from file
                string json = File.ReadAllText(saveFilePath);
                
                // Parse JSON
                SaveData data = JsonUtility.FromJson<SaveData>(json);
                
                if (data == null)
                {
                    Debug.LogWarning("Save file corrupted. Creating new save data.");
                    currentSaveData = new SaveData();
                    SaveProgress();
                    return;
                }
                
                currentSaveData = data;
                
                // Apply loaded data to game systems
                ApplySaveData(data);
                
                Debug.Log($"Progress loaded successfully. Max night unlocked: {data.maxNightUnlocked}");
            }
            catch (Exception e)
            {
                Debug.LogError($"Failed to load progress: {e.Message}");
                currentSaveData = new SaveData();
            }
        }

        void ApplySaveData(SaveData data)
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.maxNightUnlocked = data.maxNightUnlocked;
                GameManager.Instance.secondsPerHour = data.secondsPerHour;
                GameManager.Instance.difficulty = data.difficulty;
                GameManager.Instance.skipTutorial = data.skipTutorial;
                GameManager.Instance.fpsCapEnabled = data.fpsCapEnabled;
                
                // Update FPS cap
                Application.targetFrameRate = data.fpsCapEnabled ? Constants.TARGET_FPS : -1;
            }

            if (AudioManager.Instance != null)
            {
                AudioManager.Instance.SetMusicMuted(data.musicMuted);
                AudioManager.Instance.SetSFXMuted(data.sfxMuted);
            }
        }
        #endregion

        #region Reset Save
        public void ResetSaveData()
        {
            Debug.LogWarning("Resetting all save data!");
            
            currentSaveData = new SaveData();
            SaveProgress();
            
            // Reset game manager
            if (GameManager.Instance != null)
            {
                GameManager.Instance.maxNightUnlocked = 1;
                GameManager.Instance.currentNight = 1;
                GameManager.Instance.secondsPerHour = 60f;
                GameManager.Instance.difficulty = 1.0f;
                GameManager.Instance.skipTutorial = false;
            }
            
            Debug.Log("Save data reset complete.");
        }

        public void DeleteSaveFile()
        {
            try
            {
                if (File.Exists(saveFilePath))
                {
                    File.Delete(saveFilePath);
                    Debug.Log("Save file deleted.");
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"Failed to delete save file: {e.Message}");
            }
        }
        #endregion

        #region Getters
        public SaveData GetCurrentSaveData()
        {
            return currentSaveData;
        }

        public bool SaveFileExists()
        {
            return File.Exists(saveFilePath);
        }
        #endregion

        #region Debug
        [ContextMenu("Save Progress")]
        void DebugSaveProgress()
        {
            SaveProgress();
        }

        [ContextMenu("Load Progress")]
        void DebugLoadProgress()
        {
            LoadProgress();
        }

        [ContextMenu("Reset Save Data")]
        void DebugResetSaveData()
        {
            ResetSaveData();
        }

        [ContextMenu("Print Save File Path")]
        void DebugPrintSavePath()
        {
            Debug.Log($"Save file location: {saveFilePath}");
            Debug.Log($"Save file exists: {SaveFileExists()}");
        }
        #endregion
    }
}
