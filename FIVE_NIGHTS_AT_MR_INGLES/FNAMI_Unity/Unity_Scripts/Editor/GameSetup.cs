using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.Rendering.PostProcessing;
using System.Collections.Generic;
using System.Linq;

// Auto-recompile trigger
public class GameSetup
{
    [MenuItem("Five Nights/Setup Game Scene")]
    public static void SetupGameScene()
    {
        BuildMainMenuScene();
        BuildOfficeScene();
        UpdateBuildSettings();
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();

        Debug.Log("✅ Scenes built: MainMenu + Office");
        EditorUtility.DisplayDialog("Success!", "Scenes built and wired.\n\nOpen MainMenu and press Play.", "OK");
    }

    private static void BuildMainMenuScene()
    {
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

        CreateEventSystem();

        GameObject gameSystems = new GameObject("GameSystems");
        CreateGameObject("GameManager", gameSystems.transform, "FiveNightsAtMrIngles.GameManager");
        CreateGameObject("AudioManager", gameSystems.transform, "FiveNightsAtMrIngles.AudioManager");
        CreateGameObject("InputManager", gameSystems.transform, "FiveNightsAtMrIngles.InputManager");
        CreateGameObject("SaveLoadManager", gameSystems.transform, "FiveNightsAtMrIngles.SaveLoadManager");

        ConfigureAudioManager(gameSystems.transform.Find("AudioManager")?.GetComponent<Component>());

        GameObject cameraObj = CreateCamera("Main Camera");
        cameraObj.tag = "MainCamera";

        GameObject canvasObj = CreateCanvas();

        GameObject bgPanel = CreateUIElement("BackgroundPanel", canvasObj.transform, "Panel");
        Image bgImage = bgPanel.GetComponent<Image>();
        bgImage.color = Color.black;
        bgImage.sprite = LoadSprite("menu_background");
        bgImage.preserveAspect = true;

        GameObject title = CreateUIElement("Title", canvasObj.transform, "Image");
        RectTransform titleRect = title.GetComponent<RectTransform>();
        titleRect.anchorMin = new Vector2(0.5f, 1f);
        titleRect.anchorMax = new Vector2(0.5f, 1f);
        titleRect.pivot = new Vector2(0.5f, 1f);
        titleRect.anchoredPosition = new Vector2(0f, -40f);
        titleRect.sizeDelta = new Vector2(800f, 180f);
        Image titleImage = title.GetComponent<Image>();
        titleImage.sprite = LoadSprite("title");
        titleImage.preserveAspect = true;

        GameObject menuPanel = CreateUIElement("MenuPanel", canvasObj.transform, "Panel");
        Image menuImage = menuPanel.GetComponent<Image>();
        menuImage.color = new Color(0f, 0f, 0f, 0.35f);
        AddMenuController(menuPanel);

        EditorSceneManager.SaveScene(scene, "Assets/Scenes/MainMenu.unity");
    }

    private static void BuildOfficeScene()
    {
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

        CreateEventSystem();

        GameObject gameSystems = new GameObject("GameSystems");
        CreateGameObject("GameManager", gameSystems.transform, "FiveNightsAtMrIngles.GameManager");
        CreateGameObject("PowerSystem", gameSystems.transform, "FiveNightsAtMrIngles.PowerSystem");
        CreateGameObject("OfficeController", gameSystems.transform, "FiveNightsAtMrIngles.OfficeController");
        CreateGameObject("CameraSystem", gameSystems.transform, "FiveNightsAtMrIngles.CameraSystem");
        CreateGameObject("AudioManager", gameSystems.transform, "FiveNightsAtMrIngles.AudioManager");
        CreateGameObject("InputManager", gameSystems.transform, "FiveNightsAtMrIngles.InputManager");
        CreateGameObject("AnimatronicManager", gameSystems.transform, "FiveNightsAtMrIngles.AnimatronicManager");
        CreateGameObject("SaveLoadManager", gameSystems.transform, "FiveNightsAtMrIngles.SaveLoadManager");

        ConfigureAudioManager(gameSystems.transform.Find("AudioManager")?.GetComponent<Component>());
        ConfigureCameraSystem(gameSystems.transform.Find("CameraSystem")?.GetComponent<Component>());

        GameObject effectsSystems = new GameObject("EffectsSystems");
        CreateGameObject("VisualEffectsManager", effectsSystems.transform, "FiveNightsAtMrIngles.Effects.VisualEffectsManager");
        CreateGameObject("ParticleController", effectsSystems.transform, "FiveNightsAtMrIngles.Effects.ParticleController");
        ConfigureEffects(effectsSystems);

        GameObject cameraObj = CreateCamera("Main Camera");
        cameraObj.tag = "MainCamera";

        GameObject canvasObj = CreateCanvas();

        GameObject bgPanel = CreateUIElement("OfficeBackground", canvasObj.transform, "Image");
        Image bgImage = bgPanel.GetComponent<Image>();
        bgImage.color = Color.black;
        bgImage.sprite = LoadSprite("office");
        bgImage.preserveAspect = true;

        GameObject hudPanel = CreateUIElement("HUDPanel", canvasObj.transform, "Panel");
        Component hud = AddComponent(hudPanel, "FiveNightsAtMrIngles.UI.HUDController");
        ConfigureHUD(hud, hudPanel.transform);

        GameObject cameraUI = CreateUIElement("CameraUIPanel", canvasObj.transform, "Panel");
        Component cameraUi = AddComponent(cameraUI, "FiveNightsAtMrIngles.UI.CameraUIController");
        ConfigureCameraUI(cameraUi, cameraUI.transform);

        GameObject pauseMenu = CreateUIElement("PauseMenuPanel", canvasObj.transform, "Panel");
        AddComponent(pauseMenu, "FiveNightsAtMrIngles.UI.PauseMenuController");

        GameObject jumpscarePanel = CreateUIElement("JumpscarePanel", canvasObj.transform, "Image");
        Image jumpImg = jumpscarePanel.GetComponent<Image>();
        jumpImg.color = new Color(0f, 0f, 0f, 0f);
        AddComponent(jumpscarePanel, "FiveNightsAtMrIngles.UI.JumpscareController");

        CreateAnimatronics();

        EditorSceneManager.SaveScene(scene, "Assets/Scenes/Office.unity");
    }

    private static void UpdateBuildSettings()
    {
        var scenes = new List<EditorBuildSettingsScene>
        {
            new EditorBuildSettingsScene("Assets/Scenes/MainMenu.unity", true),
            new EditorBuildSettingsScene("Assets/Scenes/Office.unity", true)
        };
        EditorBuildSettings.scenes = scenes.ToArray();
    }

    private static void CreateEventSystem()
    {
        GameObject eventSystem = new GameObject("EventSystem");
        eventSystem.AddComponent<EventSystem>();

        var inputSystemUiType = System.Type.GetType("UnityEngine.InputSystem.UI.InputSystemUIInputModule, Unity.InputSystem");
        if (inputSystemUiType != null)
        {
            eventSystem.AddComponent(inputSystemUiType);
        }
        else
        {
            Debug.LogWarning("InputSystemUIInputModule not found. UI input may not work.");
        }
    }

    private static GameObject CreateCamera(string name)
    {
        GameObject cameraObj = new GameObject(name);
        Camera cam = cameraObj.AddComponent<Camera>();
        cam.backgroundColor = Color.black;
        cam.clearFlags = CameraClearFlags.SolidColor;
        cameraObj.AddComponent<AudioListener>();
        return cameraObj;
    }

    private static GameObject CreateCanvas()
    {
        GameObject canvasObj = new GameObject("Canvas");
        Canvas canvas = canvasObj.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;

        CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1280, 720);

        canvasObj.AddComponent<GraphicRaycaster>();
        return canvasObj;
    }
    
    private static GameObject CreateGameObject(string name, Transform parent, string scriptName)
    {
        GameObject obj = new GameObject(name);
        obj.transform.SetParent(parent);
        AddComponent(obj, scriptName);
        return obj;
    }
    
    private static GameObject CreateUIElement(string name, Transform parent, string type)
    {
        GameObject obj = new GameObject(name);
        RectTransform rect = obj.AddComponent<RectTransform>();
        obj.transform.SetParent(parent, false);
        
        rect.anchorMin = Vector2.zero;
        rect.anchorMax = Vector2.one;
        rect.offsetMin = Vector2.zero;
        rect.offsetMax = Vector2.zero;
        
        if (type == "Panel" || type == "Button" || type == "Image")
        {
            obj.AddComponent<Image>();
        }
        
        return obj;
    }
    
    private static Component AddComponent(GameObject obj, string componentName)
    {
        System.Type type = System.Type.GetType(componentName + ", Assembly-CSharp");
        if (type != null)
        {
            return obj.AddComponent(type);
        }
        else
        {
            Debug.LogWarning($"Could not find script: {componentName}");
            return null;
        }
    }
    
    private static void AddMenuController(GameObject obj)
    {
        // Add the MenuController script
        var menuController = AddComponent(obj, "FiveNightsAtMrIngles.UI.MenuController");
        
        // Create a vertical layout group for buttons
        VerticalLayoutGroup layoutGroup = obj.AddComponent<VerticalLayoutGroup>();
        layoutGroup.childAlignment = TextAnchor.MiddleCenter;
        layoutGroup.spacing = 20;
        layoutGroup.padding = new RectOffset(50, 50, 100, 100);
        layoutGroup.childControlWidth = false;
        layoutGroup.childControlHeight = false;
        layoutGroup.childForceExpandWidth = false;
        layoutGroup.childForceExpandHeight = false;
        
        var nightButtons = new List<Object>();
        var nightTexts = new List<Object>();

        // Create night selection buttons (5 nights) - properly positioned
        for (int i = 0; i < 5; i++)
        {
            GameObject btnGO = new GameObject($"NightButton{i+1}");
            RectTransform btnRect = btnGO.AddComponent<RectTransform>();
            btnRect.SetParent(obj.transform, false);
            btnRect.sizeDelta = new Vector2(300, 60);
            
            Image btnImage = btnGO.AddComponent<Image>();
            btnImage.color = new Color(0.2f, 0.2f, 0.2f, 1f);
            
            Button btn = btnGO.AddComponent<Button>();
            ColorBlock colors = btn.colors;
            colors.normalColor = new Color(0.2f, 0.2f, 0.2f, 1f);
            colors.highlightedColor = new Color(0.3f, 0.3f, 0.3f, 1f);
            colors.pressedColor = new Color(0.15f, 0.15f, 0.15f, 1f);
            btn.colors = colors;
            
            // Add text to button
            GameObject textGO = new GameObject("Text");
            RectTransform txtRect = textGO.AddComponent<RectTransform>();
            txtRect.SetParent(btnGO.transform, false);
            txtRect.anchorMin = Vector2.zero;
            txtRect.anchorMax = Vector2.one;
            txtRect.offsetMin = Vector2.zero;
            txtRect.offsetMax = Vector2.zero;
            
            Text txt = textGO.AddComponent<Text>();
            txt.text = $"Night {i + 1}";
            txt.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            txt.fontSize = 24;
            txt.alignment = TextAnchor.MiddleCenter;
            txt.color = Color.white;

            nightButtons.Add(btn);
            nightTexts.Add(txt);
        }

        // Extra menu buttons
        Button continueBtn = CreateMenuButton(obj.transform, "Continue", 300, 55);
        Button newGameBtn = CreateMenuButton(obj.transform, "New Game", 300, 55);
        Button settingsBtn = CreateMenuButton(obj.transform, "Settings", 300, 55);
        Button quitBtn = CreateMenuButton(obj.transform, "Quit", 300, 55);

        // Assign fields on MenuController
        SetObjectArray(menuController, "nightButtons", nightButtons);
        SetObjectArray(menuController, "nightButtonTexts", nightTexts);
        SetObject(menuController, "continueButton", continueBtn);
        SetObject(menuController, "newGameButton", newGameBtn);
        SetObject(menuController, "settingsButton", settingsBtn);
        SetObject(menuController, "quitButton", quitBtn);
        SetObject(menuController, "mainPanel", obj);
    }

    private static Button CreateMenuButton(Transform parent, string label, float width, float height)
    {
        GameObject btnGO = new GameObject(label.Replace(" ", "") + "Button");
        RectTransform btnRect = btnGO.AddComponent<RectTransform>();
        btnRect.SetParent(parent, false);
        btnRect.sizeDelta = new Vector2(width, height);

        Image btnImage = btnGO.AddComponent<Image>();
        btnImage.color = new Color(0.2f, 0.2f, 0.2f, 1f);

        Button btn = btnGO.AddComponent<Button>();
        ColorBlock colors = btn.colors;
        colors.normalColor = new Color(0.2f, 0.2f, 0.2f, 1f);
        colors.highlightedColor = new Color(0.3f, 0.3f, 0.3f, 1f);
        colors.pressedColor = new Color(0.15f, 0.15f, 0.15f, 1f);
        btn.colors = colors;

        GameObject textGO = new GameObject("Text");
        RectTransform txtRect = textGO.AddComponent<RectTransform>();
        txtRect.SetParent(btnGO.transform, false);
        txtRect.anchorMin = Vector2.zero;
        txtRect.anchorMax = Vector2.one;
        txtRect.offsetMin = Vector2.zero;
        txtRect.offsetMax = Vector2.zero;

        Text txt = textGO.AddComponent<Text>();
        txt.text = label;
        txt.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        txt.fontSize = 22;
        txt.alignment = TextAnchor.MiddleCenter;
        txt.color = Color.white;

        return btn;
    }

    private static void ConfigureAudioManager(Component audioManager)
    {
        if (audioManager == null) return;

        SetObject(audioManager, "menuMusic", LoadAudioClip("menu_theme", "Assets/Audio/Music"));
        SetObject(audioManager, "jumpscareSFX", LoadAudioClip("jumpscare", "Assets/Audio/SFX"));
        SetObject(audioManager, "doorOpenSFX", LoadAudioClip("door_open", "Assets/Audio/SFX"));
        SetObject(audioManager, "doorCloseSFX", LoadAudioClip("door_close", "Assets/Audio/SFX"));
        SetObject(audioManager, "lightSwitchSFX", LoadAudioClip("light_toggle", "Assets/Audio/SFX"));
        SetObject(audioManager, "cameraToggleSFX", LoadAudioClip("camera_flash", "Assets/Audio/SFX"));
        SetObject(audioManager, "cameraBlipSFX", LoadAudioClip("camera_flash", "Assets/Audio/SFX"));
        SetObject(audioManager, "staticSFX", LoadAudioClip("static_loop", "Assets/Audio/SFX"));
        SetObject(audioManager, "powerOutageSFX", LoadAudioClip("power_out", "Assets/Audio/SFX"));
        SetObject(audioManager, "clockChimeSFX", LoadAudioClip("hour_chime", "Assets/Audio/SFX"));

        var ambience = new List<Object>();
        var ambienceClip = LoadAudioClip("ambience", "Assets/Audio/Music");
        if (ambienceClip != null)
        {
            ambience.Add(ambienceClip);
            ambience.Add(ambienceClip);
            ambience.Add(ambienceClip);
            ambience.Add(ambienceClip);
            ambience.Add(ambienceClip);
        }
        SetObjectArray(audioManager, "nightAmbience", ambience);
    }

    private static void ConfigureCameraSystem(Component cameraSystem)
    {
        if (cameraSystem == null) return;

        var rooms = LoadRoomAssets();
        SetObjectArray(cameraSystem, "allRooms", rooms.Cast<Object>().ToList());
    }

    private static void ConfigureEffects(GameObject effectsRoot)
    {
        var vfx = effectsRoot.transform.Find("VisualEffectsManager")?.GetComponent<Component>();
        var particles = effectsRoot.transform.Find("ParticleController")?.GetComponent<Component>();

        if (vfx != null)
        {
            var profile = AssetDatabase.LoadAssetAtPath<PostProcessProfile>("Assets/DefaultVolumeProfile.asset");
            if (profile != null)
            {
                GameObject volumeObj = new GameObject("PostProcessVolume");
                var volume = volumeObj.AddComponent<PostProcessVolume>();
                volume.isGlobal = true;
                volume.sharedProfile = profile;
                SetObject(vfx, "postProcessVolume", volume);
                SetObject(vfx, "defaultProfile", profile);
            }
        }

        if (particles != null)
        {
            GameObject particlePrefab = new GameObject("ParticlePrefab");
            particlePrefab.transform.SetParent(effectsRoot.transform, false);
            var ps = particlePrefab.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.loop = false;
            particlePrefab.SetActive(false);

            SetObject(particles, "staticParticlePrefab", particlePrefab);
            SetObject(particles, "dustParticlePrefab", particlePrefab);
            SetObject(particles, "sparkParticlePrefab", particlePrefab);
            SetObject(particles, "glowParticlePrefab", particlePrefab);
            SetObject(particles, "smokeParticlePrefab", particlePrefab);
        }
    }

    private static void ConfigureHUD(Component hud, Transform parent)
    {
        if (hud == null) return;

        GameObject powerTextObj = CreateUIText("PowerText", parent, new Vector2(20, -20), new Vector2(200, 40), TextAnchor.UpperLeft);
        GameObject timeTextObj = CreateUIText("TimeText", parent, new Vector2(-20, -20), new Vector2(200, 40), TextAnchor.UpperRight);
        GameObject nightTextObj = CreateUIText("NightText", parent, new Vector2(-20, -60), new Vector2(200, 30), TextAnchor.UpperRight);

        SetObject(hud, "powerText", powerTextObj.GetComponent<Text>());
        SetObject(hud, "timeText", timeTextObj.GetComponent<Text>());
        SetObject(hud, "nightText", nightTextObj.GetComponent<Text>());
    }

    private static void ConfigureCameraUI(Component cameraUi, Transform parent)
    {
        if (cameraUi == null) return;

        GameObject panel = CreateUIElement("CameraPanel", parent, "Panel");
        panel.SetActive(false);

        GameObject feed = CreateUIElement("CameraFeed", panel.transform, "Image");
        GameObject label = CreateUIText("RoomLabel", panel.transform, new Vector2(20, -20), new Vector2(300, 40), TextAnchor.UpperLeft);

        SetObject(cameraUi, "cameraPanel", panel);
        SetObject(cameraUi, "cameraFeedImage", feed.GetComponent<Image>());
        SetObject(cameraUi, "roomNameText", label.GetComponent<Text>());
    }

    private static void CreateAnimatronics()
    {
        var rooms = LoadRoomAssets();
        if (rooms.Count == 0) return;

        var stage = rooms.FirstOrDefault(r => r.roomName == "Stage") ?? rooms[0];
        var office = rooms.FirstOrDefault(r => r.roomName == "Office") ?? rooms[0];

        CreateAnimatronic("Mr Ingles", "anim_mr_ingles", stage, true);
        CreateAnimatronic("Janitor", "anim_janitor", stage, false);
        CreateAnimatronic("Librarian", "anim_librarian", stage, true);
        CreateAnimatronic("Guard", "anim_guard_ingles", office, false);
    }

    private static void CreateAnimatronic(string name, string spriteName, FiveNightsAtMrIngles.RoomData startRoom, bool attackLeft)
    {
        GameObject obj = new GameObject(name);
        Component anim = AddComponent(obj, "FiveNightsAtMrIngles.Animatronic");
        if (anim == null) return;

        SetValue(anim, "characterName", name);
        SetObject(anim, "characterSprite", LoadSprite(spriteName));
        SetObject(anim, "startingRoom", startRoom);
        SetObject(anim, "currentRoom", startRoom);
        SetValue(anim, "attackFromLeft", attackLeft);
    }

    private static GameObject CreateUIText(string name, Transform parent, Vector2 anchoredPos, Vector2 size, TextAnchor anchor)
    {
        GameObject textObj = new GameObject(name);
        RectTransform rect = textObj.AddComponent<RectTransform>();
        rect.SetParent(parent, false);
        rect.anchorMin = new Vector2(anchor == TextAnchor.UpperLeft || anchor == TextAnchor.UpperCenter || anchor == TextAnchor.UpperRight ? 0f : 0.5f,
            anchor == TextAnchor.UpperLeft || anchor == TextAnchor.UpperCenter || anchor == TextAnchor.UpperRight ? 1f : 0.5f);
        rect.anchorMax = rect.anchorMin;
        rect.pivot = rect.anchorMin;
        rect.anchoredPosition = anchoredPos;
        rect.sizeDelta = size;

        Text txt = textObj.AddComponent<Text>();
        txt.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        txt.fontSize = 20;
        txt.alignment = anchor;
        txt.color = Color.white;
        return textObj;
    }

    private static Sprite LoadSprite(string name)
    {
        string[] guids = AssetDatabase.FindAssets(name + " t:Sprite", new[] { "Assets/Sprites" });
        if (guids.Length == 0) return null;
        string path = AssetDatabase.GUIDToAssetPath(guids[0]);
        return AssetDatabase.LoadAssetAtPath<Sprite>(path);
    }

    private static AudioClip LoadAudioClip(string name, string folder)
    {
        string[] guids = AssetDatabase.FindAssets(name + " t:AudioClip", new[] { folder });
        if (guids.Length == 0) return null;
        string path = AssetDatabase.GUIDToAssetPath(guids[0]);
        return AssetDatabase.LoadAssetAtPath<AudioClip>(path);
    }

    private static List<FiveNightsAtMrIngles.RoomData> LoadRoomAssets()
    {
        string[] guids = AssetDatabase.FindAssets("t:FiveNightsAtMrIngles.RoomData", new[] { "Assets/Data/Rooms" });
        var rooms = new List<FiveNightsAtMrIngles.RoomData>();
        foreach (var guid in guids)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            var room = AssetDatabase.LoadAssetAtPath<FiveNightsAtMrIngles.RoomData>(path);
            if (room != null)
            {
                rooms.Add(room);
            }
        }
        return rooms.OrderBy(r => r.roomName).ToList();
    }

    private static void SetObject(Component component, string propertyName, Object value)
    {
        if (component == null) return;
        SerializedObject so = new SerializedObject(component);
        var prop = so.FindProperty(propertyName);
        if (prop != null)
        {
            prop.objectReferenceValue = value;
            so.ApplyModifiedPropertiesWithoutUndo();
        }
    }

    private static void SetValue(Component component, string propertyName, string value)
    {
        if (component == null) return;
        SerializedObject so = new SerializedObject(component);
        var prop = so.FindProperty(propertyName);
        if (prop != null)
        {
            prop.stringValue = value;
            so.ApplyModifiedPropertiesWithoutUndo();
        }
    }

    private static void SetValue(Component component, string propertyName, bool value)
    {
        if (component == null) return;
        SerializedObject so = new SerializedObject(component);
        var prop = so.FindProperty(propertyName);
        if (prop != null)
        {
            prop.boolValue = value;
            so.ApplyModifiedPropertiesWithoutUndo();
        }
    }

    private static void SetObjectArray(Component component, string propertyName, List<Object> items)
    {
        if (component == null) return;
        SerializedObject so = new SerializedObject(component);
        var prop = so.FindProperty(propertyName);
        if (prop == null) return;

        prop.arraySize = items.Count;
        for (int i = 0; i < items.Count; i++)
        {
            prop.GetArrayElementAtIndex(i).objectReferenceValue = items[i];
        }
        so.ApplyModifiedPropertiesWithoutUndo();
    }
}
