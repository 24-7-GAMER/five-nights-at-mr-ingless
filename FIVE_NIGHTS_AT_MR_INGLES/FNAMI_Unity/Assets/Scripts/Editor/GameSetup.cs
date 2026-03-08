using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using System.Collections.Generic;
using System.IO;
using System.Linq;
#if UNITY_POST_PROCESSING_STACK_V2
using UnityEngine.Rendering.PostProcessing;
#endif

namespace FiveNightsAtMrIngles.Editor
{
    public class GameSetup : UnityEditor.Editor
    {
        [MenuItem("Five Nights/Setup Full Game")]
        public static void SetupFullGame()
        {
            CreateRoomDataAssets();
            CreateSceneFolder();
            BuildMainMenuScene();
            BuildOfficeScene();
            UpdateBuildSettings();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("✅ Full game setup complete!");
            EditorUtility.DisplayDialog("Setup Complete",
                "Five Nights at Mr Ingles's setup complete!\n\nOpen MainMenu scene and press Play.",
                "OK");
        }

        [MenuItem("Five Nights/Create Room Data Assets")]
        public static void CreateRoomDataAssets()
        {
            string roomsPath = "Assets/Data/Rooms";
            if (!AssetDatabase.IsValidFolder(roomsPath))
            {
                AssetDatabase.CreateFolder("Assets/Data", "Rooms");
            }

            var roomDefs = new (string name, float x, float y, string[] connections, string spriteName, bool isOffice)[]
            {
                ("Office",        0.50f, 0.85f, new[]{"West Hall","East Hall","Supply Closet","Restrooms"}, "office", true),
                ("West Hall",     0.25f, 0.65f, new[]{"Office","Cafeteria","Dining Area","Supply Closet"}, "cam_west_hall", false),
                ("East Hall",     0.75f, 0.65f, new[]{"Office","Gym","Backstage","Restrooms"}, "cam_east_hall", false),
                ("Stage",         0.50f, 0.10f, new[]{"Dining Area","Backstage"}, "cam_stage", false),
                ("Dining Area",   0.30f, 0.25f, new[]{"Stage","West Hall","Kitchen"}, "cam_dining_area", false),
                ("Backstage",     0.70f, 0.25f, new[]{"Stage","East Hall","Kitchen"}, "cam_backstage", false),
                ("Kitchen",       0.50f, 0.35f, new[]{"Dining Area","Backstage","Cafeteria"}, "cam_kitchen", false),
                ("Cafeteria",     0.12f, 0.45f, new[]{"West Hall","Kitchen","Library"}, "cam_cafeteria", false),
                ("Gym",           0.88f, 0.45f, new[]{"East Hall","Bathrooms"}, "cam_gym", false),
                ("Library",       0.12f, 0.65f, new[]{"Cafeteria","Bathrooms"}, "cam_library", false),
                ("Bathrooms",     0.88f, 0.65f, new[]{"Gym","Library","Vent"}, "cam_bathrooms", false),
                ("Vent",          0.82f, 0.78f, new[]{"Bathrooms","Supply Closet","Restrooms"}, "cam_vent", false),
                ("Supply Closet", 0.18f, 0.78f, new[]{"Office","West Hall","Vent"}, "cam_supply_closet", false),
                ("Restrooms",     0.68f, 0.52f, new[]{"Office","East Hall","Vent"}, "cam_restrooms", false),
            };

            // First pass: create all room assets
            var rooms = new Dictionary<string, RoomData>();
            foreach (var def in roomDefs)
            {
                string assetPath = $"{roomsPath}/{def.name.Replace(" ", "_")}.asset";
                RoomData room = AssetDatabase.LoadAssetAtPath<RoomData>(assetPath);
                if (room == null)
                {
                    room = ScriptableObject.CreateInstance<RoomData>();
                    AssetDatabase.CreateAsset(room, assetPath);
                }
                room.roomName = def.name;
                room.minimapX = def.x;
                room.minimapY = def.y;
                room.isOffice = def.isOffice;
                room.hasCamera = !def.isOffice;
                room.isStartingRoom = def.name == "Stage";

                Sprite sprite = LoadSprite(def.spriteName);
                if (sprite != null)
                    room.cameraViewSprite = sprite;

                rooms[def.name] = room;
                EditorUtility.SetDirty(room);
            }

            // Second pass: wire up connections
            foreach (var def in roomDefs)
            {
                var room = rooms[def.name];
                room.connectedRooms = new List<RoomData>();
                foreach (var connName in def.connections)
                {
                    if (rooms.TryGetValue(connName, out var connRoom))
                        room.connectedRooms.Add(connRoom);
                }
                EditorUtility.SetDirty(room);
            }

            AssetDatabase.SaveAssets();
            Debug.Log("✅ Created 14 RoomData assets in Assets/Data/Rooms/");
        }

        static void CreateSceneFolder()
        {
            if (!AssetDatabase.IsValidFolder("Assets/Scenes"))
                AssetDatabase.CreateFolder("Assets", "Scenes");
        }

        [MenuItem("Five Nights/Build MainMenu Scene")]
        public static void BuildMainMenuScene()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            CreateEventSystem();

            // Core systems
            GameObject gameSystems = new GameObject("GameSystems");
            AddComponent(gameSystems, "FiveNightsAtMrIngles.GameManager");
            AddComponent(gameSystems, "FiveNightsAtMrIngles.AudioManager");
            AddComponent(gameSystems, "FiveNightsAtMrIngles.InputManager");
            AddComponent(gameSystems, "FiveNightsAtMrIngles.SaveLoadManager");

            // Camera
            GameObject cam = new GameObject("Main Camera");
            cam.tag = "MainCamera";
            cam.AddComponent<Camera>();
            cam.AddComponent<AudioListener>();
            cam.GetComponent<Camera>().backgroundColor = Color.black;
            cam.GetComponent<Camera>().clearFlags = CameraClearFlags.SolidColor;
            cam.GetComponent<Camera>().orthographic = true;
            cam.GetComponent<Camera>().orthographicSize = 5f;

            // Canvas
            GameObject canvasObj = CreateCanvas();

            // Background panel
            GameObject bg = CreateUIImage("Background", canvasObj.transform);
            SetFullStretch(bg.GetComponent<RectTransform>());
            bg.GetComponent<Image>().color = Color.black;
            bg.GetComponent<Image>().sprite = LoadSprite("menu_background");
            bg.GetComponent<Image>().preserveAspect = false;

            // Splash panel
            GameObject splashPanel = CreateUIPanel("SplashPanel", canvasObj.transform, Color.black);
            SetFullStretch(splashPanel.GetComponent<RectTransform>());
            splashPanel.GetComponent<Image>().sprite = LoadSprite("intro_splashscreen");
            splashPanel.GetComponent<Image>().preserveAspect = false;
            AddComponent(splashPanel, "FiveNightsAtMrIngles.UI.SplashController");

            // Menu panel
            GameObject menuPanel = CreateUIPanel("MenuPanel", canvasObj.transform, new Color(0, 0, 0, 0.5f));
            RectTransform menuRect = menuPanel.GetComponent<RectTransform>();
            menuRect.anchorMin = new Vector2(0.3f, 0.25f);
            menuRect.anchorMax = new Vector2(0.7f, 0.75f);
            menuRect.offsetMin = Vector2.zero;
            menuRect.offsetMax = Vector2.zero;

            // Menu buttons
            CreateMenuButton("Night 1", menuPanel.transform, new Vector2(0, 80));
            CreateMenuButton("Night 2", menuPanel.transform, new Vector2(0, 30));
            CreateMenuButton("Night 3", menuPanel.transform, new Vector2(0, -20));
            CreateMenuButton("Night 4", menuPanel.transform, new Vector2(0, -70));
            CreateMenuButton("Night 5", menuPanel.transform, new Vector2(0, -120));
            AddComponent(menuPanel, "FiveNightsAtMrIngles.UI.MenuController");

            // Intro panel
            GameObject introPanel = CreateUIPanel("IntroPanel", canvasObj.transform, Color.black);
            SetFullStretch(introPanel.GetComponent<RectTransform>());
            GameObject introText = CreateUIText("IntroText", introPanel.transform);
            SetCenterAnchor(introText.GetComponent<RectTransform>(), new Vector2(600, 60));
            introText.GetComponent<Text>().text = "YOU'RE IN THE SCIENCE BLOCK.";
            introText.GetComponent<Text>().fontSize = 24;
            introText.GetComponent<Text>().color = Color.white;
            introText.GetComponent<Text>().alignment = TextAnchor.MiddleCenter;
            AddComponent(introPanel, "FiveNightsAtMrIngles.UI.IntroController");
            introPanel.SetActive(false);

            // Tutorial panel
            GameObject tutPanel = CreateUIPanel("TutorialPanel", canvasObj.transform, new Color(0, 0, 0, 0.9f));
            SetFullStretch(tutPanel.GetComponent<RectTransform>());
            GameObject tutText = CreateUIText("TutorialText", tutPanel.transform);
            SetCenterAnchor(tutText.GetComponent<RectTransform>(), new Vector2(800, 400));
            tutText.GetComponent<Text>().text = "CONTROLS:\nQ - Left Door\nE - Right Door\nTab - Cameras\nL - Flashlight\nF/F11 - Fullscreen";
            tutText.GetComponent<Text>().fontSize = 20;
            tutText.GetComponent<Text>().color = Color.white;
            tutText.GetComponent<Text>().alignment = TextAnchor.MiddleCenter;
            AddComponent(tutPanel, "FiveNightsAtMrIngles.UI.TutorialController");
            tutPanel.SetActive(false);

            // Wire AudioManager clips
            var audioMgr = gameSystems.GetComponent("FiveNightsAtMrIngles.AudioManager") as Component;
            if (audioMgr == null) audioMgr = gameSystems.GetComponents<MonoBehaviour>().FirstOrDefault(m => m.GetType().Name == "AudioManager") as Component;
            WireAudioManager(audioMgr);

            if (!AssetDatabase.IsValidFolder("Assets/Scenes"))
                AssetDatabase.CreateFolder("Assets", "Scenes");
            EditorSceneManager.SaveScene(scene, "Assets/Scenes/MainMenu.unity");
            Debug.Log("✅ MainMenu scene built");
        }

        [MenuItem("Five Nights/Build Office Scene")]
        public static void BuildOfficeScene()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            CreateEventSystem();

            // Core game systems
            GameObject gameSystems = new GameObject("GameSystems");
            AddComponent(gameSystems, "FiveNightsAtMrIngles.GameManager");
            AddComponent(gameSystems, "FiveNightsAtMrIngles.PowerSystem");
            AddComponent(gameSystems, "FiveNightsAtMrIngles.OfficeController");
            AddComponent(gameSystems, "FiveNightsAtMrIngles.CameraSystem");
            AddComponent(gameSystems, "FiveNightsAtMrIngles.AudioManager");
            AddComponent(gameSystems, "FiveNightsAtMrIngles.InputManager");
            AddComponent(gameSystems, "FiveNightsAtMrIngles.AnimatronicManager");
            AddComponent(gameSystems, "FiveNightsAtMrIngles.SaveLoadManager");
            AddComponent(gameSystems, "FiveNightsAtMrIngles.AntiCheatController");
            AddComponent(gameSystems, "FiveNightsAtMrIngles.OfficePanningController");

            // Effects
            GameObject effects = new GameObject("EffectsSystems");
            AddComponent(effects, "FiveNightsAtMrIngles.Effects.VisualEffectsManager");
            AddComponent(effects, "FiveNightsAtMrIngles.Effects.ParticleController");

            // Camera
            GameObject cam = new GameObject("Main Camera");
            cam.tag = "MainCamera";
            cam.AddComponent<Camera>();
            cam.AddComponent<AudioListener>();
            cam.GetComponent<Camera>().backgroundColor = Color.black;
            cam.GetComponent<Camera>().clearFlags = CameraClearFlags.SolidColor;
            cam.GetComponent<Camera>().orthographic = true;
            cam.GetComponent<Camera>().orthographicSize = 5f;

            // Animatronics
            GameObject animatronics = new GameObject("Animatronics");
            CreateAnimatronic(animatronics.transform, "Scary Mr Ingles", "anim_scary_ingles", "Right", 1.0f, 0f);
            CreateAnimatronic(animatronics.transform, "Freaky Temi", "anim_temi", "Right", 0.45f, 30f);
            CreateAnimatronic(animatronics.transform, "Librarian", "anim_librarian", "Left", 1.0f, 60f);
            CreateAnimatronic(animatronics.transform, "Vent Crawler", "anim_vent", "Vent", 1.0f, 90f);

            // Canvas
            GameObject canvasObj = CreateCanvas();

            // Office background
            GameObject officeBg = CreateUIImage("OfficeBackground", canvasObj.transform);
            SetFullStretch(officeBg.GetComponent<RectTransform>());
            officeBg.GetComponent<Image>().sprite = LoadSprite("office");
            officeBg.GetComponent<Image>().preserveAspect = false;

            // Left door visual
            GameObject leftDoor = CreateUIImage("LeftDoor", canvasObj.transform);
            RectTransform leftDoorRect = leftDoor.GetComponent<RectTransform>();
            leftDoorRect.anchorMin = new Vector2(0, 0);
            leftDoorRect.anchorMax = new Vector2(0.15f, 1f);
            leftDoorRect.offsetMin = Vector2.zero;
            leftDoorRect.offsetMax = Vector2.zero;
            leftDoor.GetComponent<Image>().color = new Color(0.1f, 0.1f, 0.1f, 0.9f);

            // Right door visual
            GameObject rightDoor = CreateUIImage("RightDoor", canvasObj.transform);
            RectTransform rightDoorRect = rightDoor.GetComponent<RectTransform>();
            rightDoorRect.anchorMin = new Vector2(0.85f, 0);
            rightDoorRect.anchorMax = new Vector2(1f, 1f);
            rightDoorRect.offsetMin = Vector2.zero;
            rightDoorRect.offsetMax = Vector2.zero;
            rightDoor.GetComponent<Image>().color = new Color(0.1f, 0.1f, 0.1f, 0.9f);

            // HUD
            GameObject hudObj = CreateUIPanel("HUD", canvasObj.transform, Color.clear);
            SetFullStretch(hudObj.GetComponent<RectTransform>());
            AddComponent(hudObj, "FiveNightsAtMrIngles.UI.HUDController");

            // Time display
            GameObject timeObj = CreateUIText("TimeDisplay", hudObj.transform);
            RectTransform timeRect = timeObj.GetComponent<RectTransform>();
            timeRect.anchorMin = new Vector2(0.5f, 1f);
            timeRect.anchorMax = new Vector2(0.5f, 1f);
            timeRect.pivot = new Vector2(0.5f, 1f);
            timeRect.anchoredPosition = new Vector2(0, -20);
            timeRect.sizeDelta = new Vector2(200, 50);
            Text timeText = timeObj.GetComponent<Text>();
            timeText.text = "12 AM";
            timeText.fontSize = 28;
            timeText.color = Color.white;
            timeText.alignment = TextAnchor.MiddleCenter;
            timeText.fontStyle = FontStyle.Bold;

            // Power display
            GameObject powerObj = CreateUIText("PowerDisplay", hudObj.transform);
            RectTransform powerRect = powerObj.GetComponent<RectTransform>();
            powerRect.anchorMin = new Vector2(0, 0);
            powerRect.anchorMax = new Vector2(0, 0);
            powerRect.pivot = new Vector2(0, 0);
            powerRect.anchoredPosition = new Vector2(20, 20);
            powerRect.sizeDelta = new Vector2(300, 40);
            Text powerText = powerObj.GetComponent<Text>();
            powerText.text = "Power: 100%";
            powerText.fontSize = 20;
            powerText.color = Color.green;

            // Camera UI
            GameObject camUI = CreateUIPanel("CameraUI", canvasObj.transform, new Color(0, 0, 0, 0.85f));
            SetFullStretch(camUI.GetComponent<RectTransform>());
            AddComponent(camUI, "FiveNightsAtMrIngles.UI.CameraUIController");

            // Camera view
            GameObject camView = CreateUIImage("CameraView", camUI.transform);
            RectTransform camViewRect = camView.GetComponent<RectTransform>();
            camViewRect.anchorMin = new Vector2(0.1f, 0.15f);
            camViewRect.anchorMax = new Vector2(0.9f, 0.85f);
            camViewRect.offsetMin = Vector2.zero;
            camViewRect.offsetMax = Vector2.zero;
            camView.GetComponent<Image>().color = new Color(0.8f, 0.8f, 0.8f, 1f);

            // Minimap
            GameObject minimap = CreateUIImage("Minimap", camUI.transform);
            minimap.GetComponent<Image>().sprite = LoadSprite("cam_monitor");
            RectTransform minimapRect = minimap.GetComponent<RectTransform>();
            minimapRect.anchorMin = new Vector2(0f, 0f);
            minimapRect.anchorMax = new Vector2(0.35f, 0.35f);
            minimapRect.offsetMin = Vector2.zero;
            minimapRect.offsetMax = Vector2.zero;

            camUI.SetActive(false);

            // Jumpscare panel
            GameObject jumpscarePanel = CreateUIPanel("JumpscarePanel", canvasObj.transform, Color.black);
            SetFullStretch(jumpscarePanel.GetComponent<RectTransform>());
            GameObject jumpscareImg = CreateUIImage("JumpscareImage", jumpscarePanel.transform);
            SetFullStretch(jumpscareImg.GetComponent<RectTransform>());
            jumpscareImg.GetComponent<Image>().sprite = LoadSprite("jumpscare");
            jumpscareImg.GetComponent<Image>().preserveAspect = true;
            AddComponent(jumpscarePanel, "FiveNightsAtMrIngles.UI.JumpscareController");
            jumpscarePanel.SetActive(false);

            // Night complete panel
            GameObject nightCompletePanel = CreateUIPanel("NightCompletePanel", canvasObj.transform, Color.black);
            SetFullStretch(nightCompletePanel.GetComponent<RectTransform>());
            GameObject nightCompleteImg = CreateUIImage("NightCompleteImage", nightCompletePanel.transform);
            SetFullStretch(nightCompleteImg.GetComponent<RectTransform>());
            nightCompleteImg.GetComponent<Image>().sprite = LoadSprite("night_complete");
            nightCompleteImg.GetComponent<Image>().preserveAspect = true;
            GameObject nightCompleteText = CreateUIText("NightCompleteText", nightCompletePanel.transform);
            SetCenterAnchor(nightCompleteText.GetComponent<RectTransform>(), new Vector2(600, 80));
            nightCompleteText.GetComponent<Text>().text = "Night 1 Complete!";
            nightCompleteText.GetComponent<Text>().fontSize = 36;
            nightCompleteText.GetComponent<Text>().color = Color.white;
            nightCompleteText.GetComponent<Text>().alignment = TextAnchor.MiddleCenter;
            AddComponent(nightCompletePanel, "FiveNightsAtMrIngles.UI.NightCompleteController");
            nightCompletePanel.SetActive(false);

            // Pause menu
            GameObject pauseMenu = CreateUIPanel("PauseMenu", canvasObj.transform, new Color(0, 0, 0, 0.85f));
            SetFullStretch(pauseMenu.GetComponent<RectTransform>());
            AddComponent(pauseMenu, "FiveNightsAtMrIngles.UI.PauseMenuController");
            pauseMenu.SetActive(false);

            // Anti-cheat UI
            GameObject antiCheatUI = CreateUIPanel("AntiCheatUI", canvasObj.transform, Color.black);
            SetFullStretch(antiCheatUI.GetComponent<RectTransform>());
            antiCheatUI.GetComponent<Image>().sprite = LoadSprite("mr_hall_anti_cheater");
            antiCheatUI.GetComponent<Image>().preserveAspect = false;
            AddComponent(antiCheatUI, "FiveNightsAtMrIngles.UI.AntiCheatUIController");
            antiCheatUI.SetActive(false);

            // Wire serialized fields AFTER all objects are created
            // AudioManager
            var audioMgrOff = gameSystems.GetComponents<MonoBehaviour>().FirstOrDefault(m => m.GetType().Name == "AudioManager") as Component;
            WireAudioManager(audioMgrOff);

            // CameraSystem - wire room list
            var camSys = gameSystems.GetComponents<MonoBehaviour>().FirstOrDefault(m => m.GetType().Name == "CameraSystem") as Component;
            WireCameraSystem(camSys);

            if (!AssetDatabase.IsValidFolder("Assets/Scenes"))
                AssetDatabase.CreateFolder("Assets", "Scenes");
            EditorSceneManager.SaveScene(scene, "Assets/Scenes/Office.unity");
            Debug.Log("✅ Office scene built");
        }

        static void UpdateBuildSettings()
        {
            var scenes = new EditorBuildSettingsScene[]
            {
                new EditorBuildSettingsScene("Assets/Scenes/MainMenu.unity", true),
                new EditorBuildSettingsScene("Assets/Scenes/Office.unity", true),
            };
            EditorBuildSettings.scenes = scenes;
            Debug.Log("✅ Build settings updated");
        }

        #region Helper Methods

        static void CreateEventSystem()
        {
            GameObject es = new GameObject("EventSystem");
            es.AddComponent<EventSystem>();
            es.AddComponent<StandaloneInputModule>();
        }

        static GameObject CreateCanvas()
        {
            GameObject canvasObj = new GameObject("Canvas");
            Canvas canvas = canvasObj.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1280, 720);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
            scaler.matchWidthOrHeight = 0.5f;
            canvasObj.AddComponent<GraphicRaycaster>();
            return canvasObj;
        }

        static GameObject CreateUIImage(string name, Transform parent)
        {
            GameObject obj = new GameObject(name);
            obj.transform.SetParent(parent, false);
            obj.AddComponent<RectTransform>();
            obj.AddComponent<Image>();
            return obj;
        }

        static GameObject CreateUIPanel(string name, Transform parent, Color color)
        {
            GameObject obj = CreateUIImage(name, parent);
            obj.GetComponent<Image>().color = color;
            return obj;
        }

        static GameObject CreateUIText(string name, Transform parent)
        {
            GameObject obj = new GameObject(name);
            obj.transform.SetParent(parent, false);
            obj.AddComponent<RectTransform>();
            Text text = obj.AddComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.color = Color.white;
            text.fontSize = 20;
            text.alignment = TextAnchor.MiddleCenter;
            return obj;
        }

        static void SetFullStretch(RectTransform rt)
        {
            rt.anchorMin = Vector2.zero;
            rt.anchorMax = Vector2.one;
            rt.offsetMin = Vector2.zero;
            rt.offsetMax = Vector2.zero;
        }

        static void SetCenterAnchor(RectTransform rt, Vector2 size)
        {
            rt.anchorMin = new Vector2(0.5f, 0.5f);
            rt.anchorMax = new Vector2(0.5f, 0.5f);
            rt.pivot = new Vector2(0.5f, 0.5f);
            rt.anchoredPosition = Vector2.zero;
            rt.sizeDelta = size;
        }

        static void AddComponent(GameObject go, string typeName)
        {
            var type = FindType(typeName);
            if (type != null)
                go.AddComponent(type);
            else
                Debug.LogWarning($"Type not found: {typeName}");
        }

        static System.Type FindType(string typeName)
        {
            foreach (var assembly in System.AppDomain.CurrentDomain.GetAssemblies())
            {
                var type = assembly.GetType(typeName);
                if (type != null)
                    return type;
            }
            return null;
        }

        static Sprite LoadSprite(string name)
        {
            string[] paths = new string[]
            {
                $"Assets/Sprites/{name}.png",
                $"Assets/Sprites/{name}.jpg",
                $"Assets/Sprites/{name}",
            };
            foreach (var path in paths)
            {
                var sprite = AssetDatabase.LoadAssetAtPath<Sprite>(path);
                if (sprite != null)
                    return sprite;
                var tex = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
                if (tex != null)
                    return Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), new Vector2(0.5f, 0.5f));
            }
            return null;
        }

        static AudioClip LoadAudioClip(string name)
        {
            string[] paths = new string[]
            {
                $"Assets/Audio/SFX/{name}.ogg",
                $"Assets/Audio/SFX/{name}.mp3",
                $"Assets/Audio/SFX/{name}.wav",
                $"Assets/Audio/Music/{name}.ogg",
                $"Assets/Audio/Music/{name}.mp3",
            };
            foreach (var path in paths)
            {
                var clip = AssetDatabase.LoadAssetAtPath<AudioClip>(path);
                if (clip != null) return clip;
            }
            return null;
        }

        /// <summary>Sets a serialized object field by name.</summary>
        static void WireField(Component comp, string fieldName, Object value)
        {
            if (comp == null) return;
            var so = new SerializedObject(comp);
            var prop = so.FindProperty(fieldName);
            if (prop != null)
            {
                prop.objectReferenceValue = value;
                so.ApplyModifiedPropertiesWithoutUndo();
            }
        }

        /// <summary>Sets a serialized array field by name.</summary>
        static void WireFieldArray(Component comp, string fieldName, List<Object> values)
        {
            if (comp == null) return;
            var so = new SerializedObject(comp);
            var prop = so.FindProperty(fieldName);
            if (prop == null) return;
            prop.arraySize = values.Count;
            for (int i = 0; i < values.Count; i++)
                prop.GetArrayElementAtIndex(i).objectReferenceValue = values[i];
            so.ApplyModifiedPropertiesWithoutUndo();
        }

        /// <summary>Wires all AudioManager audio clips from Assets/Audio/</summary>
        static void WireAudioManager(Component audioManager)
        {
            if (audioManager == null) return;
            WireField(audioManager, "menuMusic",        LoadAudioClip("menu_theme"));
            WireField(audioManager, "jumpscareSFX",     LoadAudioClip("jumpscare"));
            WireField(audioManager, "doorOpenSFX",      LoadAudioClip("door_open"));
            WireField(audioManager, "doorCloseSFX",     LoadAudioClip("door_close"));
            WireField(audioManager, "lightSwitchSFX",   LoadAudioClip("light_toggle"));
            WireField(audioManager, "cameraToggleSFX",  LoadAudioClip("camera_flash"));
            WireField(audioManager, "cameraBlipSFX",    LoadAudioClip("camera_flash"));
            WireField(audioManager, "staticSFX",        LoadAudioClip("static_loop"));
            WireField(audioManager, "powerOutageSFX",   LoadAudioClip("power_out"));
            WireField(audioManager, "clockChimeSFX",    LoadAudioClip("hour_chime"));
            WireField(audioManager, "doorKnockSFX",     LoadAudioClip("door_knock"));
            WireField(audioManager, "doorDamageSFX",    LoadAudioClip("door_damage"));
            WireField(audioManager, "ventCrawlSFX",     LoadAudioClip("vent_crawl"));

            // Night ambience tracks (all use same ambience clip for now)
            var ambience = LoadAudioClip("ambience");
            if (ambience != null)
            {
                var ambienceList = new List<Object> { ambience, ambience, ambience, ambience, ambience };
                WireFieldArray(audioManager, "nightAmbience", ambienceList);
            }
        }

        /// <summary>Wires all CameraSystem rooms from Assets/Data/Rooms/</summary>
        static void WireCameraSystem(Component cameraSystem)
        {
            if (cameraSystem == null) return;
            string[] guids = AssetDatabase.FindAssets("t:ScriptableObject", new[] { "Assets/Data/Rooms" });
            var rooms = new List<Object>();
            foreach (var guid in guids)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var obj = AssetDatabase.LoadAssetAtPath<ScriptableObject>(path);
                if (obj != null && obj.GetType().Name == "RoomData")
                    rooms.Add(obj);
            }
            if (rooms.Count == 0)
            {
                Debug.LogWarning("No RoomData assets found! Run 'Five Nights/Create Room Data Assets' first.");
                return;
            }
            WireFieldArray(cameraSystem, "allRooms", rooms);
            Debug.Log($"  Wired {rooms.Count} rooms to CameraSystem");
        }

        static void CreateMenuButton(string label, Transform parent, Vector2 anchoredPos)
        {
            GameObject btn = new GameObject($"Btn_{label.Replace(" ", "")}");
            btn.transform.SetParent(parent, false);
            RectTransform rt = btn.AddComponent<RectTransform>();
            rt.anchorMin = new Vector2(0.5f, 0.5f);
            rt.anchorMax = new Vector2(0.5f, 0.5f);
            rt.pivot = new Vector2(0.5f, 0.5f);
            rt.anchoredPosition = anchoredPos;
            rt.sizeDelta = new Vector2(200, 40);
            Image img = btn.AddComponent<Image>();
            img.color = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            Button button = btn.AddComponent<Button>();
            ColorBlock cb = button.colors;
            cb.highlightedColor = new Color(0.4f, 0.4f, 0.4f, 1f);
            button.colors = cb;

            GameObject textObj = CreateUIText("Text", btn.transform);
            SetFullStretch(textObj.GetComponent<RectTransform>());
            Text text = textObj.GetComponent<Text>();
            text.text = label;
            text.fontSize = 18;
            text.color = Color.white;
            text.alignment = TextAnchor.MiddleCenter;
        }

        static void CreateAnimatronic(Transform parent, string characterName, string spriteName, string attackSideStr, float sizeMultiplier, float startDelay)
        {
            GameObject animObj = new GameObject(characterName);
            animObj.transform.SetParent(parent, false);
            var type = FindType("FiveNightsAtMrIngles.Animatronic");
            if (type == null)
            {
                Debug.LogWarning("Animatronic type not found");
                return;
            }
            var anim = animObj.AddComponent(type) as MonoBehaviour;

            type.GetField("characterName")?.SetValue(anim, characterName);
            type.GetField("sizeMultiplier")?.SetValue(anim, sizeMultiplier);
            type.GetField("startDelayMinutes")?.SetValue(anim, startDelay);

            Sprite sprite = LoadSprite(spriteName);
            type.GetField("characterSprite")?.SetValue(anim, sprite);

            var attackSideField = type.GetField("attackSide");
            if (attackSideField != null)
            {
                var attackSideType = attackSideField.FieldType;
                attackSideField.SetValue(anim, System.Enum.Parse(attackSideType, attackSideStr));
            }

            Debug.Log($"  Created animatronic: {characterName}");
        }
        #endregion
    }
}
