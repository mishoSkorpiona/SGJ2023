using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;

public class DoorComponent : MonoBehaviour
{
    private GameObject TheDoorItself = null;

    private bool ShouldOpen = false;
    private bool UseLinearEase = false;
    private float Factor = 0.0f;
    private float TargetFactor = 1.0f;
    private float StartHeight = 0.0f;
    public float EndHeight = -1.0f;

    public void Open()
    {
        ShouldOpen = true;
        UseLinearEase = false;
        TargetFactor = 1.0f;
    }

    public void OpenFactor(float targetFactor)
    {
        ShouldOpen = true;
        UseLinearEase = true;
        TargetFactor = targetFactor;
    }

    void Start()
    {
        TheDoorItself = this.transform.Find("TheDoorItself").gameObject;
        StartHeight = TheDoorItself.transform.localPosition.y;
    }

    void Update()
    {
        if (ShouldOpen && Factor < TargetFactor)
        {
            Factor += Time.deltaTime * 2.0f;

            float ease = UseLinearEase ? Factor : 1.0f - Mathf.Pow(1.0f - Factor, 5.0f);

            float height = StartHeight + (EndHeight - StartHeight) * ease;

            TheDoorItself.transform.SetLocalPositionAndRotation(new Vector3(0.0f, height, 0.0f), Quaternion.identity);

            if (Factor >= 1.0f)
            {
                TheDoorItself.GetComponent<Collider>().enabled = false;
            }
        }
    }
}
