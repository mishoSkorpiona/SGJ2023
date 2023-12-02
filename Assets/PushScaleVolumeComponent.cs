using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UIElements;

public class PushScaleVolumeComponent : MonoBehaviour
{
    private GameObject TheScale = null;
    private int Counter = 0;

    void Start()
    {
        TheScale = transform.parent.parent.gameObject;
    }

    private void OnTriggerEnter(Collider other)
    {
        if (!TheScale)
            return;

        PushScaleComponent theScale = TheScale.GetComponent<PushScaleComponent>();
        if (!theScale)
            return;

        if (!IsGoodCollider(other))
            return;

        Counter += 1;

        theScale.OnCountChanged(Counter);
    }

    private void OnTriggerExit(Collider other)
    {
        if (!TheScale)
            return;

        PushScaleComponent theScale = TheScale.GetComponent<PushScaleComponent>();
        if (!theScale)
            return;

        if (!IsGoodCollider(other))
            return;

        Counter -= 1;

        theScale.OnCountChanged(Counter);
    }

    private bool IsGoodCollider(Collider other)
    {
        if (!TheScale)
            return false;

        PushScaleComponent theScale = TheScale.GetComponent<PushScaleComponent>();
        if (!theScale)
            return false;

        if (theScale.TagsRequired != null)
        {
            bool foundAny = false;
            foreach (string tag in theScale.TagsRequired)
            {
                if (other.CompareTag(tag))
                {
                    foundAny = true;
                    break;
                }
            }

            if (!foundAny)
                return false;
        }

        return true;
    }
}
