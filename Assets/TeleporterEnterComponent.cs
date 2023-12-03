using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class TeleporterEnterComponent : MonoBehaviour
{
    public string TagRequired = null;
    public string LoadSceneName = null;
    public GameObject TeleporterExit = null;
    public AudioClip TeleportAudio = null;

    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnTriggerEnter(Collider other)
    {
        if (TagRequired != null && TagRequired.Length > 0)
        {
            if (!other.CompareTag(TagRequired))
                return;
        }

        if (TeleporterExit)
        {
            other.transform.SetPositionAndRotation(TeleporterExit.transform.position, other.transform.rotation);

            if (TeleportAudio)
                GetComponent<AudioSource>().PlayOneShot(TeleportAudio);
        }
        else if (LoadSceneName != null && LoadSceneName.Length > 0)
        {
            SceneManager.LoadScene(LoadSceneName);
        }
    }
}
