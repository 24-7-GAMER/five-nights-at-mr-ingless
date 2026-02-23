using UnityEngine;
using System.Collections.Generic;
using System;

namespace FiveNightsAtMrIngles
{
    /// <summary>
    /// Centralized audio management system
    /// Handles music, SFX, and ambience
    /// </summary>
    public class AudioManager : MonoBehaviour
    {
        #region Singleton
        public static AudioManager Instance { get; private set; }

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

        #region Audio Sources
        [Header("Audio Sources")]
        public AudioSource musicSource;
        public AudioSource ambienceSource;
        public AudioSource sfxSource;
        #endregion

        #region Audio Clips
        [Header("Music")]
        public AudioClip menuMusic;
        public AudioClip[] nightAmbience; // Ambience for nights 1-5

        [Header("SFX")]
        public AudioClip doorOpenSFX;
        public AudioClip doorCloseSFX;
        public AudioClip doorKnockSFX;
        public AudioClip doorDamageSFX;
        public AudioClip lightSwitchSFX;
        public AudioClip cameraToggleSFX;
        public AudioClip cameraBlipSFX;
        public AudioClip staticSFX;
        public AudioClip footstepSFX;
        public AudioClip breathingSFX;
        public AudioClip introMsgSFX;
        public AudioClip niceTrySFX;
        public AudioClip ventCrawlSFX;
        public AudioClip faaahSFX;
        public AudioClip jumpscareSFX;
        public AudioClip powerOutageSFX;
        public AudioClip clockChimeSFX;
        #endregion

        #region Settings
        [Header("Settings")]
        [Range(0f, 1f)]
        public float musicVolume = 0.7f;
        [Range(0f, 1f)]
        public float sfxVolume = 0.8f;
        [Range(0f, 1f)]
        public float ambienceVolume = 0.6f;

        public bool musicMuted = false;
        public bool sfxMuted = false;
        #endregion

        #region Private Fields
        private Dictionary<string, AudioClip> sfxLibrary = new Dictionary<string, AudioClip>();
        #endregion

        #region Initialization
        void Initialize()
        {
            // Create audio sources if not assigned
            if (musicSource == null)
            {
                GameObject musicObj = new GameObject("MusicSource");
                musicObj.transform.SetParent(transform);
                musicSource = musicObj.AddComponent<AudioSource>();
                musicSource.loop = true;
                musicSource.playOnAwake = false;
            }

            if (ambienceSource == null)
            {
                GameObject ambienceObj = new GameObject("AmbienceSource");
                ambienceObj.transform.SetParent(transform);
                ambienceSource = ambienceObj.AddComponent<AudioSource>();
                ambienceSource.loop = true;
                ambienceSource.playOnAwake = false;
            }

            if (sfxSource == null)
            {
                GameObject sfxObj = new GameObject("SFXSource");
                sfxObj.transform.SetParent(transform);
                sfxSource = sfxObj.AddComponent<AudioSource>();
                sfxSource.loop = false;
                sfxSource.playOnAwake = false;
            }

            UpdateVolumes();
            
            // Subscribe to events
            OfficeController.OnLeftDoorToggle += HandleDoorToggle;
            OfficeController.OnRightDoorToggle += HandleDoorToggle;
            OfficeController.OnLightToggle += HandleLightToggle;
            OfficeController.OnCameraToggle += HandleCameraToggle;
            CameraSystem.OnCameraSwitch += HandleCameraSwitch;
            GameManager.OnHourChange += HandleHourChange;
            GameManager.OnStateChange += HandleStateChange;
        }

        void OnDestroy()
        {
            // Unsubscribe from events
            OfficeController.OnLeftDoorToggle -= HandleDoorToggle;
            OfficeController.OnRightDoorToggle -= HandleDoorToggle;
            OfficeController.OnLightToggle -= HandleLightToggle;
            OfficeController.OnCameraToggle -= HandleCameraToggle;
            CameraSystem.OnCameraSwitch -= HandleCameraSwitch;
            GameManager.OnHourChange -= HandleHourChange;
            GameManager.OnStateChange -= HandleStateChange;
        }
        #endregion

        #region Music Control
        public void PlayMusic(AudioClip clip, bool loop = true, float fadeTime = 1f)
        {
            if (musicMuted || clip == null)
                return;

            if (musicSource.clip == clip && musicSource.isPlaying)
                return;

            StopAllCoroutines();
            StartCoroutine(CrossfadeMusic(clip, loop, fadeTime));
        }

        System.Collections.IEnumerator CrossfadeMusic(AudioClip newClip, bool loop, float fadeTime)
        {
            // Fade out current music
            float startVolume = musicSource.volume;
            for (float t = 0; t < fadeTime; t += Time.deltaTime)
            {
                musicSource.volume = Mathf.Lerp(startVolume, 0f, t / fadeTime);
                yield return null;
            }
            musicSource.volume = 0f;
            musicSource.Stop();

            // Switch clip
            musicSource.clip = newClip;
            musicSource.loop = loop;
            musicSource.Play();

            // Fade in new music
            for (float t = 0; t < fadeTime; t += Time.deltaTime)
            {
                musicSource.volume = Mathf.Lerp(0f, musicVolume, t / fadeTime);
                yield return null;
            }
            musicSource.volume = musicVolume;
        }

        public void StopMusic(float fadeTime = 1f)
        {
            StopAllCoroutines();
            StartCoroutine(FadeOutMusic(fadeTime));
        }

        System.Collections.IEnumerator FadeOutMusic(float fadeTime)
        {
            float startVolume = musicSource.volume;
            for (float t = 0; t < fadeTime; t += Time.deltaTime)
            {
                musicSource.volume = Mathf.Lerp(startVolume, 0f, t / fadeTime);
                yield return null;
            }
            musicSource.volume = 0f;
            musicSource.Stop();
        }
        #endregion

        #region SFX Control
        public void PlaySFX(AudioClip clip, float volumeMultiplier = 1f)
        {
            if (sfxMuted || clip == null)
                return;

            sfxSource.PlayOneShot(clip, sfxVolume * volumeMultiplier);
        }

        public void PlaySFX(string sfxName, float volumeMultiplier = 1f)
        {
            AudioClip clip = GetSFXByName(sfxName);
            if (clip != null)
            {
                PlaySFX(clip, volumeMultiplier);
            }
        }

        AudioClip GetSFXByName(string name)
        {
            switch (name.ToLower())
            {
                case "door_open": return doorOpenSFX;
                case "door_close": return doorCloseSFX;
                case "door_knock": return doorKnockSFX;
                case "door_damage": return doorDamageSFX;
                case "light": return lightSwitchSFX;
                case "camera_toggle": return cameraToggleSFX;
                case "camera_blip": return cameraBlipSFX;
                case "static": return staticSFX;
                case "footstep": return footstepSFX;
                case "breathing": return breathingSFX;
                case "intro_msg": return introMsgSFX;
                case "nice_try": return niceTrySFX;
                case "vent_crawl": return ventCrawlSFX;
                case "faaah": return faaahSFX;
                case "jumpscare": return jumpscareSFX;
                case "power_outage": return powerOutageSFX;
                case "clock": return clockChimeSFX;
                default: return null;
            }
        }
        #endregion

        #region Ambience Control
        public void PlayAmbience(AudioClip clip)
        {
            if (clip == null)
                return;

            ambienceSource.clip = clip;
            ambienceSource.loop = true;
            ambienceSource.volume = ambienceVolume;
            ambienceSource.Play();
        }

        public void StopAmbience()
        {
            ambienceSource.Stop();
        }

        public void PlayNightAmbience(int nightNumber)
        {
            int index = Mathf.Clamp(nightNumber - 1, 0, nightAmbience.Length - 1);
            if (index < nightAmbience.Length && nightAmbience[index] != null)
            {
                PlayAmbience(nightAmbience[index]);
            }
        }
        #endregion

        #region Volume Control
        public void SetMusicVolume(float volume)
        {
            musicVolume = Mathf.Clamp01(volume);
            UpdateVolumes();
        }

        public void SetSFXVolume(float volume)
        {
            sfxVolume = Mathf.Clamp01(volume);
            UpdateVolumes();
        }

        public void SetAmbienceVolume(float volume)
        {
            ambienceVolume = Mathf.Clamp01(volume);
            UpdateVolumes();
        }

        public void SetMusicMuted(bool muted)
        {
            musicMuted = muted;
            UpdateVolumes();
        }

        public void SetSFXMuted(bool muted)
        {
            sfxMuted = muted;
        }

        void UpdateVolumes()
        {
            if (musicSource != null)
                musicSource.volume = musicMuted ? 0f : musicVolume;
            
            if (ambienceSource != null)
                ambienceSource.volume = musicMuted ? 0f : ambienceVolume;
        }
        #endregion

        #region Event Handlers
        void HandleDoorToggle(bool closed)
        {
            PlaySFX(closed ? doorCloseSFX : doorOpenSFX);
        }

        void HandleLightToggle(bool on)
        {
            PlaySFX(lightSwitchSFX);
        }

        void HandleCameraToggle(bool open)
        {
            PlaySFX(cameraToggleSFX);
            if (open)
            {
                PlaySFX(staticSFX, 0.3f);
            }
        }

        void HandleCameraSwitch(RoomData newRoom)
        {
            PlaySFX(cameraBlipSFX, 0.5f);
        }

        void HandleHourChange(int hour)
        {
            PlaySFX(clockChimeSFX);
        }

        void HandleStateChange(GameManager.GameState from, GameManager.GameState to)
        {
            switch (to)
            {
                case GameManager.GameState.Menu:
                    PlayMusic(menuMusic);
                    StopAmbience();
                    break;

                case GameManager.GameState.Playing:
                    StopMusic();
                    if (GameManager.Instance != null)
                    {
                        PlayNightAmbience(GameManager.Instance.currentNight);
                    }
                    break;

                case GameManager.GameState.Jumpscare:
                    StopMusic();
                    StopAmbience();
                    PlaySFX(jumpscareSFX);
                    break;

                case GameManager.GameState.Win:
                    StopAmbience();
                    // Play win music if available
                    break;
            }
        }
        #endregion

        #region Debug
        [ContextMenu("Test Door Open SFX")]
        void TestDoorOpen()
        {
            PlaySFX(doorOpenSFX);
        }

        [ContextMenu("Test Door Close SFX")]
        void TestDoorClose()
        {
            PlaySFX(doorCloseSFX);
        }

        [ContextMenu("Test Jumpscare SFX")]
        void TestJumpscare()
        {
            PlaySFX(jumpscareSFX);
        }

        [ContextMenu("Play Menu Music")]
        void TestMenuMusic()
        {
            PlayMusic(menuMusic);
        }
        #endregion
    }
}
