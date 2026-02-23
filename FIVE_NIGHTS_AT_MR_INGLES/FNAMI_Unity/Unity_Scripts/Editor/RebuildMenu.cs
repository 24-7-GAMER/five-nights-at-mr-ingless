using UnityEngine;
using UnityEngine.UI;
using UnityEditor;

namespace FiveNightsAtMrIngles.Editor
{
    public class RebuildMenu : EditorWindow
    {
        [MenuItem("Five Nights/Rebuild Menu UI")]
        public static void ShowWindow()
        {
            GetWindow<RebuildMenu>("Rebuild Menu");
        }

        void OnGUI()
        {
            GUILayout.Label("Menu UI Rebuild", EditorStyles.boldLabel);
            
            if (GUILayout.Button("Rebuild Main Menu Panel"))
            {
                Rebuild();
            }
        }

        static void Rebuild()
        {
            // Find or create Canvas
            Canvas canvas = FindObjectOfType<Canvas>();
            if (canvas == null)
            {
                Debug.LogError("Canvas not found!");
                return;
            }

            // Find MenuPanel
            Transform menuPanelTransform = canvas.transform.Find("MenuPanel");
            if (menuPanelTransform == null)
            {
                Debug.LogError("MenuPanel not found!");
                return;
            }

            GameObject menuPanel = menuPanelTransform.gameObject;
            
            // Clear all children except keeping the MenuController component
            for (int i = menuPanel.transform.childCount - 1; i >= 0; i--)
            {
                DestroyImmediate(menuPanel.transform.GetChild(i).gameObject);
            }

            // Remove layout group if exists
            var layoutGroup = menuPanel.GetComponent<VerticalLayoutGroup>();
            if (layoutGroup) DestroyImmediate(layoutGroup);

            // Create new layout matching Python version
            CreatePythonStyleMenu(menuPanel);
            
            Debug.Log("✅ Menu rebuilt successfully!");
        }

        static void CreatePythonStyleMenu(GameObject menuPanel)
        {
            RectTransform menuRect = menuPanel.GetComponent<RectTransform>();

            // Title
            GameObject titleObj = CreateText("Title", menuPanel.transform, "FIVE NIGHTS AT\nMR INGLES'S", 64,
                new Vector2(0.5f, 1f), new Vector2(0.5f, 1f),
                new Vector2(0, -150), new Vector2(800, 200));
            titleObj.GetComponent<Text>().color = new Color(1f, 0.4f, 0.4f);
            titleObj.GetComponent<Text>().fontStyle = FontStyle.Bold;

            // Night selection buttons (horizontal layout)
            float buttonY = -350;
            float buttonSpacing = 145;
            float startX = -290; // Center 5 buttons
            GetMenuController(menuPanel).nightButtons = new Button[5];
            GetMenuController(menuPanel).nightButtonTexts = new Text[5];

            for (int i = 0; i < 5; i++)
            {
                int nightNum = i + 1;
                float xPos = startX + (i * buttonSpacing);
                
                GameObject btnObj = CreateButton($"NightButton{nightNum}", menuPanel.transform,
                    new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f),
                    new Vector2(xPos, buttonY), new Vector2(110, 70));
                
                Button btn = btnObj.GetComponent<Button>();
                Image btnImg = btnObj.GetComponent<Image>();
                btnImg.color = new Color(0.08f, 0.35f, 0.55f);
                
                ColorBlock colors = btn.colors;
                colors.normalColor = new Color(0.08f, 0.35f, 0.55f);
                colors.highlightedColor = new Color(0.12f, 0.5f, 0.8f);
                colors.pressedColor = new Color(0.05f, 0.25f, 0.4f);
                colors.disabledColor = new Color(0.16f, 0.16f, 0.31f);
                btn.colors = colors;

                // Button text
                GameObject txtObj = CreateText("Number", btnObj.transform,
                    nightNum.ToString(), 48,
                    Vector2.zero, Vector2.one,
                    Vector2.zero, Vector2.zero);
                txtObj.GetComponent<Text>().fontStyle = FontStyle.Bold;

                GetMenuController(menuPanel).nightButtons[i] = btn;
                GetMenuController(menuPanel).nightButtonTexts[i] = txtObj.GetComponent<Text>();

                // LOCKED text below button
                CreateText($"LockedText{nightNum}", menuPanel.transform,
                    "LOCKED", 14,
                    new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f),
                    new Vector2(xPos, buttonY - 55), new Vector2(110, 30))
                    .GetComponent<Text>().color = new Color(0.78f, 0.39f, 0.39f);
            }

            // Instruction text
            GameObject instructionText = CreateText("InstructionText", menuPanel.transform,
                "Select a night to survive", 24,
                new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f),
                new Vector2(0, -520), new Vector2(600, 40));
            instructionText.GetComponent<Text>().color = new Color(0.78f, 1f, 0.78f);
            GetMenuController(menuPanel).instructionText = instructionText.GetComponent<Text>();

            // Status text
            GameObject statusText = CreateText("StatusText", menuPanel.transform,
                "No nights survived yet", 20,
                new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f),
                new Vector2(0, -560), new Vector2(600, 40));
            statusText.GetComponent<Text>().color = new Color(1f, 0.39f, 0.39f);
            GetMenuController(menuPanel).statusText = statusText.GetComponent<Text>();

            // Night Length Slider
            CreateSliderWithLabel(menuPanel, "NightLengthSlider",
                new Vector2(0, -75), "Night Length: 60s/hour  (~6 min/night)", 30, 120);

            // Difficulty Slider
            CreateSliderWithLabel(menuPanel, "DifficultySlider",
                new Vector2(0, -40), "Difficulty: HARD (1.20x)", 0.5f, 2f);

            // Keyboard shortcuts text at bottom
            CreateText("ShortcutsText", menuPanel.transform,
                "[M] Music  [S] SFX  [F] Fullscreen  [T] Skip Tutorial  [Y] FPS Cap  [X] Reset Settings  [R] Reset Save",
                12,
                new Vector2(0.5f, 0f), new Vector2(0.5f, 0f),
                new Vector2(0, 20), new Vector2(1200, 25))
                .GetComponent<Text>().color = new Color(0.47f, 0.63f, 0.75f);

            Debug.Log("✅ Created Python-style menu layout");
        }

        static UI.MenuController GetMenuController(GameObject obj)
        {
            var ctrl = obj.GetComponent<UI.MenuController>();
            if (ctrl == null)
            {
                ctrl = obj.AddComponent<UI.MenuController>();
            }
            return ctrl;
        }

        static GameObject CreateText(string name, Transform parent, string content, int fontSize,
            Vector2 anchorMin, Vector2 anchorMax, Vector2 anchoredPosition, Vector2 sizeDelta)
        {
            GameObject obj = new GameObject(name);
            RectTransform rect = obj.AddComponent<RectTransform>();
            rect.SetParent(parent, false);
            rect.anchorMin = anchorMin;
            rect.anchorMax = anchorMax;
            rect.anchoredPosition = anchoredPosition;
            rect.sizeDelta = sizeDelta;

            Text text = obj.AddComponent<Text>();
            text.text = content;
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.fontSize = fontSize;
            text.alignment = TextAnchor.MiddleCenter;
            text.color = Color.white;
            text.horizontalOverflow = HorizontalWrapMode.Overflow;
            text.verticalOverflow = VerticalWrapMode.Overflow;

            return obj;
        }

        static GameObject CreateButton(string name, Transform parent,
            Vector2 anchorMin, Vector2 anchorMax, Vector2 anchoredPosition, Vector2 sizeDelta)
        {
            GameObject obj = new GameObject(name);
            RectTransform rect = obj.AddComponent<RectTransform>();
            rect.SetParent(parent, false);
            rect.anchorMin = anchorMin;
            rect.anchorMax = anchorMax;
            rect.anchoredPosition = anchoredPosition;
            rect.sizeDelta = sizeDelta;

            Image img = obj.AddComponent<Image>();
            img.color = Color.white;

            Button btn = obj.AddComponent<Button>();
            return obj;
        }

        static void CreateSliderWithLabel(GameObject menuPanel, string name, Vector2 position, string labelText, float minValue, float maxValue)
        {
            // Label
            GameObject labelObj = CreateText($"{name}Label", menuPanel.transform,
                labelText, 14,
                new Vector2(0.5f, 0f), new Vector2(0.5f, 0f),
                new Vector2(position.x, position.y - 18 + 650), new Vector2(500, 25));
            labelObj.GetComponent<Text>().color = new Color(0.78f, 1f, 0.78f);

            // Slider
            GameObject sliderObj = new GameObject(name);
            RectTransform sliderRect = sliderObj.AddComponent<RectTransform>();
            sliderRect.SetParent(menuPanel.transform, false);
            sliderRect.anchorMin = new Vector2(0.5f, 0f);
            sliderRect.anchorMax = new Vector2(0.5f, 0f);
            sliderRect.anchoredPosition = new Vector2(position.x, position.y + 650);
            sliderRect.sizeDelta = new Vector2(420, 20);

            Slider slider = sliderObj.AddComponent<Slider>();
            slider.minValue = minValue;
            slider.maxValue = maxValue;
            slider.value = (minValue + maxValue) / 2;

            // Background
            GameObject bg = new GameObject("Background");
            RectTransform bgRect = bg.AddComponent<RectTransform>();
            bgRect.SetParent(sliderObj.transform, false);
            bgRect.anchorMin = Vector2.zero;
            bgRect.anchorMax = Vector2.one;
            bgRect.sizeDelta = Vector2.zero;
            Image bgImg = bg.AddComponent<Image>();
            bgImg.color = new Color(0.24f, 0.24f, 0.35f);

            // Fill Area
            GameObject fillArea = new GameObject("Fill Area");
            RectTransform fillAreaRect = fillArea.AddComponent<RectTransform>();
            fillAreaRect.SetParent(sliderObj.transform, false);
            fillAreaRect.anchorMin = Vector2.zero;
            fillAreaRect.anchorMax = Vector2.one;
            fillAreaRect.sizeDelta = new Vector2(-10, 0);

            GameObject fill = new GameObject("Fill");
            RectTransform fillRect = fill.AddComponent<RectTransform>();
            fillRect.SetParent(fillArea.transform, false);
            fillRect.anchorMin = Vector2.zero;
            fillRect.anchorMax = Vector2.one;
            fillRect.sizeDelta = Vector2.zero;
            Image fillImg = fill.AddComponent<Image>();
            fillImg.color = name.Contains("Night") ? new Color(0.08f, 0.59f, 0.86f) : new Color(0.86f, 0.47f, 0.24f);

            // Handle Slide Area
            GameObject handleArea = new GameObject("Handle Slide Area");
            RectTransform handleAreaRect = handleArea.AddComponent<RectTransform>();
            handleAreaRect.SetParent(sliderObj.transform, false);
            handleAreaRect.anchorMin = Vector2.zero;
            handleAreaRect.anchorMax = Vector2.one;
            handleAreaRect.sizeDelta = new Vector2(-10, 0);

            GameObject handle = new GameObject("Handle");
            RectTransform handleRect = handle.AddComponent<RectTransform>();
            handleRect.SetParent(handleArea.transform, false);
            handleRect.anchorMin = Vector2.zero;
            handleRect.anchorMax = Vector2.one;
            handleRect.sizeDelta = new Vector2(16, 0);
            Image handleImg = handle.AddComponent<Image>();
            handleImg.color = new Color(0.78f, 0.78f, 1f);

            slider.fillRect = fillRect;
            slider.handleRect = handleRect;
            slider.targetGraphic = handleImg;

            // Wire to MenuController
            var ctrl = GetMenuController(menuPanel);
            if (name.Contains("Night"))
            {
                ctrl.nightLengthSlider = slider;
                ctrl.nightLengthText = labelObj.GetComponent<Text>();
            }
            else
            {
                ctrl.difficultySlider = slider;
                ctrl.difficultyText = labelObj.GetComponent<Text>();
            }
        }
    }
}
