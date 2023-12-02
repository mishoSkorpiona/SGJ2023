using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;

public class PushScaleComponent : MonoBehaviour
{
    public List<string> TagsRequired;
    public GameObject DoorToOpen = null;
    public int CountRequired = 2;
    public float OffsetFinal = -2.0f;

    private float OffsetTarget = 0.0f;
    private int CountCurrent = 0;
    private GameObject Platform = null;

    void Start()
    {
        Platform = transform.Find("Platform").gameObject;
    }

    public void OnCountChanged(int count)
    {
        CountCurrent = count;
        float factor = (float)(CountCurrent) / (float)(CountRequired);
        OffsetTarget = OffsetFinal * factor;

        if (DoorToOpen)
        {
            DoorComponent door = DoorToOpen.GetComponent<DoorComponent>();
            if (door)
            {
                door.OpenFactor(factor);
            }
        }
    }

    void Update()
    {
        float offset = Platform.transform.localPosition.y;
        float delta = OffsetTarget - offset;
        if (Mathf.Abs(delta) < 0.05f)
        {
            /*if (CountCurrent >= CountRequired && DoorToOpen)
            {
                DoorComponent door = DoorToOpen.GetComponent<DoorComponent>();
                if (door)
                {
                    door.Open();
                }
            }*/
            return;
        }

        float direciton = delta / Mathf.Abs(delta);
        offset += direciton * Time.deltaTime * 1.0f;

        Platform.transform.SetLocalPositionAndRotation(new Vector3(0.0f, offset, 0.0f), Platform.transform.rotation);
    }
}
