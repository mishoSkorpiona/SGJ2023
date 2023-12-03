using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ButtonComponent : MonoBehaviour
{
    public string TagRequired = null;
    public GameObject DoorToOpen = null;
    public AudioClip PressAudio = null;
    public bool ActivateOnce = false;

    private bool ActivatedOnce = false;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnTriggerEnter(Collider other)
    {
        if (ActivateOnce && ActivatedOnce)
        {
            return;
        }

        if (TagRequired != null && TagRequired.Length > 0)
        {
            if (!other.CompareTag(TagRequired))
                return;
        }

        if (PressAudio)
            GetComponent<AudioSource>().PlayOneShot(PressAudio);

        if (DoorToOpen)
        {
            DoorComponent door = DoorToOpen.GetComponent<DoorComponent>();
            if (door)
            {
                door.Open();
            }
        }

        ActivatedOnce = true;
    }
}
