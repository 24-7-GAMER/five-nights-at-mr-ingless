using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;
using FiveNightsAtMrIngles;
using System.Collections;

namespace FiveNightsAtMrIngles.UI
{
    public class NightCompleteController : MonoBehaviour
    {
        public GameObject nightCompletePanel;
        public Image nightCompleteImage;
        public Text nightCompleteText;
        public Button continueButton;

        void OnEnable()
        {
            GameManager.OnNightWin += HandleNightWin;
        }

        void OnDisable()
        {
            GameManager.OnNightWin -= HandleNightWin;
        }

        void Start()
        {
            if (nightCompletePanel != null)
                nightCompletePanel.SetActive(false);
            if (continueButton != null)
                continueButton.onClick.AddListener(ReturnToMenu);
        }

        void HandleNightWin()
        {
            if (nightCompletePanel != null)
                nightCompletePanel.SetActive(true);
            if (nightCompleteText != null && GameManager.Instance != null)
                nightCompleteText.text = $"Night {GameManager.Instance.currentNight} Complete!";
            StartCoroutine(AutoReturnToMenu(5f));
        }

        IEnumerator AutoReturnToMenu(float delay)
        {
            yield return new WaitForSeconds(delay);
            ReturnToMenu();
        }

        public void ReturnToMenu()
        {
            if (GameManager.Instance != null)
                GameManager.Instance.ChangeState(GameManager.GameState.Menu);
            else
                SceneManager.LoadScene("MainMenu");
        }
    }
}
