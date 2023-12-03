using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class CinematicSequence : MonoBehaviour
{
    [System.Serializable]
    public struct Step
    {
        public Texture image;
        public float time;
    }

    public List<Step> Steps = null;
    public string NextLevel = null;

    private int CurrentStep = 0;
    private float CurrentTime = 0.0f;

    void Start()
    {
        
    }

    void Update()
    {
        CurrentTime += Time.deltaTime;

        if (CurrentStep < Steps.Count)
        {
            Step step = Steps[CurrentStep];
            if (CurrentTime > step.time)
            {
                CurrentTime = 0.0f;
                CurrentStep += 1;
            }
            else if (GetComponent<RawImage>().texture != step.image)
            {
                GetComponent<RawImage>().texture = step.image;
            }
        }
        else if (NextLevel != null && NextLevel.Length > 0)
        {
            SceneManager.LoadScene(NextLevel);
        }
    }
}
