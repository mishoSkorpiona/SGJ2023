using System.Collections;
using System.Collections.Generic;
using UnityEditor.SearchService;
using UnityEngine;
using UnityEngine.SceneManagement;

public class MainMenuComponent : MonoBehaviour
{
    public GameObject Credits = null;
    public GameObject StartButton = null;

    // Start is called before the first frame update
    void Start()
    {
        Credits.SetActive(false);
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void StartGame()
    {
        SceneManager.LoadScene("Scenes/IntroCinematic");
    }

    public void ToggleCredits()
    {
        //var credits = this.gameObject.Find("Credits").gameObject;
        if (Credits)
        {
            Credits.SetActive(!Credits.activeSelf);
        }

        if (StartButton)
        {
            StartButton.SetActive(!Credits.activeSelf);
        }
    }
}
