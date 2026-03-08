using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using FiveNightsAtMrIngles;

namespace FiveNightsAtMrIngles.UI
{
    /// <summary>
    /// Controls tutorial overlay for Night 1
    /// </summary>
    public class TutorialController : MonoBehaviour
    {
        #region Tutorial Steps
        [System.Serializable]
        public class TutorialStep
        {
            public string title;
            [TextArea(3, 5)]
            public string description;
            public float displayDuration = 5f;
            public bool requireInput = false; // Wait for player to press key
        }
        #endregion

        #region UI Elements
        [Header("UI")]
        public GameObject tutorialPanel;
        public Text titleText;
        public Text descriptionText;
        public Text skipHintText;

        [Header("Tutorial Steps")]
        public TutorialStep[] tutorialSteps = new TutorialStep[]
        {
            new TutorialStep
            {
                title = "WELCOME",
                description = "Welcome to your first night at Mr Ingles's school.\nYour job is to survive from 12 AM to 6 AM.",
                displayDuration = 4f,
                requireInput = false
            },
            new TutorialStep
            {
                title = "POWER MANAGEMENT",
                description = "Watch your POWER level.\nUsing doors, lights, and cameras drains power.\nIf power reaches 0%, the lights go out...",
                displayDuration = 5f,
                requireInput = false
            },
            new TutorialStep
            {
                title = "DOORS",
                description = "Press Q to close the LEFT DOOR\nPress E to close the RIGHT DOOR\n\nUse doors to block animatronics, but they drain power!",
                displayDuration = 5f,
                requireInput = false
            },
            new TutorialStep
            {
                title = "CAMERAS",
                description = "Press TAB to open the CAMERA SYSTEM\nUse cameras to track animatronic movements.\n\nPress 1-6 to switch between cameras quickly.",
                displayDuration = 5f,
                requireInput = false
            },
            new TutorialStep
            {
                title = "SURVIVAL TIP",
                description = "Listen carefully for footsteps and breathing.\nClose doors when animatronics are nearby.\n\nGood luck...",
                displayDuration = 4f,
                requireInput = false
            }
        };

        [Header("Settings")]
        public bool autoStartTutorial = true;
        public float delayBetweenSteps = 1f;
        #endregion

        #region Private Fields
        private int currentStepIndex = 0;
        private bool isPlayingTutorial = false;
        private Coroutine tutorialCoroutine;
        #endregion

        #region Unity Lifecycle
        void OnEnable()
        {
            GameManager.OnStateChange += HandleStateChange;
        }

        void OnDisable()
        {
            GameManager.OnStateChange -= HandleStateChange;
        }

        void Start()
        {
            if (tutorialPanel != null)
                tutorialPanel.SetActive(false);
        }

        void Update()
        {
            if (isPlayingTutorial && Input.GetKeyDown(KeyCode.Space))
            {
                SkipTutorial();
            }
        }
        #endregion

        #region Event Handlers
        void HandleStateChange(GameManager.GameState from, GameManager.GameState to)
        {
            if (to == GameManager.GameState.Tutorial && autoStartTutorial)
            {
                StartTutorial();
            }
            else if (from == GameManager.GameState.Tutorial)
            {
                StopTutorial();
            }
        }
        #endregion

        #region Tutorial Control
        public void StartTutorial()
        {
            if (isPlayingTutorial)
                return;

            isPlayingTutorial = true;
            currentStepIndex = 0;

            if (tutorialPanel != null)
                tutorialPanel.SetActive(true);

            if (tutorialCoroutine != null)
                StopCoroutine(tutorialCoroutine);

            tutorialCoroutine = StartCoroutine(PlayTutorialSequence());
        }

        public void SkipTutorial()
        {
            StopTutorial();

            // Transition to playing state
            if (GameManager.Instance != null)
            {
                GameManager.Instance.ChangeState(GameManager.GameState.Playing);
            }
        }

        void StopTutorial()
        {
            isPlayingTutorial = false;

            if (tutorialPanel != null)
                tutorialPanel.SetActive(false);

            if (tutorialCoroutine != null)
            {
                StopCoroutine(tutorialCoroutine);
                tutorialCoroutine = null;
            }
        }

        IEnumerator PlayTutorialSequence()
        {
            for (int i = 0; i < tutorialSteps.Length; i++)
            {
                currentStepIndex = i;
                TutorialStep step = tutorialSteps[i];

                // Display step
                DisplayStep(step);

                // Wait for duration or input
                if (step.requireInput)
                {
                    // Wait for player input
                    while (!Input.anyKeyDown)
                    {
                        yield return null;
                    }
                }
                else
                {
                    // Wait for duration
                    yield return new WaitForSeconds(step.displayDuration);
                }

                // Delay between steps
                if (i < tutorialSteps.Length - 1)
                {
                    yield return new WaitForSeconds(delayBetweenSteps);
                }
            }

            // Tutorial complete
            CompleteTutorial();
        }

        void DisplayStep(TutorialStep step)
        {
            if (titleText != null)
            {
                titleText.text = step.title;
            }

            if (descriptionText != null)
            {
                descriptionText.text = step.description;
            }

            if (skipHintText != null)
            {
                skipHintText.text = "Press SPACE to skip tutorial";
            }
        }

        void CompleteTutorial()
        {
            isPlayingTutorial = false;

            if (tutorialPanel != null)
                tutorialPanel.SetActive(false);

            // Start playing
            if (GameManager.Instance != null)
            {
                GameManager.Instance.ChangeState(GameManager.GameState.Playing);
            }
        }
        #endregion

        #region Public Methods
        public void AddCustomStep(string title, string description, float duration = 3f)
        {
            TutorialStep newStep = new TutorialStep
            {
                title = title,
                description = description,
                displayDuration = duration,
                requireInput = false
            };

            TutorialStep[] newSteps = new TutorialStep[tutorialSteps.Length + 1];
            tutorialSteps.CopyTo(newSteps, 0);
            newSteps[tutorialSteps.Length] = newStep;
            tutorialSteps = newSteps;
        }
        #endregion
    }
}
