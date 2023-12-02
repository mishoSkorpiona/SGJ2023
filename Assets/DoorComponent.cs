using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;

public class DoorComponent : MonoBehaviour
{
    private GameObject TheDoorItself = null;

    private bool ShouldOpen = false;
    private float Factor = 0.0f;
    private float StartHeight = 0.0f;
    public float EndHeight = -1.0f;

    public void Open()
    {
        ShouldOpen = true;
        //Factor = 0.0f;
    }

    void Start()
    {
        TheDoorItself = this.transform.Find("TheDoorItself").gameObject;
        StartHeight = TheDoorItself.transform.localPosition.y;
    }

    void Update()
    {
        if (ShouldOpen && Factor < 1.0f)
        {
            Factor += Time.deltaTime * 2.0f;

            float easeOutQuint = 1.0f - Mathf.Pow(1.0f - Factor, 5.0f);
            float height = StartHeight + (EndHeight - StartHeight) * easeOutQuint;

            TheDoorItself.transform.SetLocalPositionAndRotation(new Vector3(0.0f, height, 0.0f), Quaternion.identity);

            if (Factor >= 1.0f)
            {
                TheDoorItself.GetComponent<Collider>().enabled = false;
            }
        }
    }
}
