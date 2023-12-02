using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraController : MonoBehaviour
{
    [SerializeField] private Transform target; // Assign the player's transform to this field
    [SerializeField] private float smoothSpeed = 1f;
    [SerializeField] private float deadZone = 2f;
    [SerializeField] private Vector3 offset = new Vector3(-8f, 0f, -8f);

    void LateUpdate()
    {
        if (target == null)
        {
            Debug.LogError("Target not assigned for CameraController.");
            return;
        }

        Vector3 targetPosition = target.position + offset;
        Vector3 currentPosition = transform.position;

        float distanceX = Mathf.Abs(targetPosition.x - currentPosition.x);
        float distanceZ = Mathf.Abs(targetPosition.z - currentPosition.z);
        float distanceY = Mathf.Abs(targetPosition.y - currentPosition.y);

        if (distanceX > deadZone || distanceZ > deadZone || distanceY > deadZone)
        {
            Vector3 desiredPosition = new Vector3(targetPosition.x, targetPosition.y, targetPosition.z);
            Vector3 smoothedPosition = Vector3.Lerp(currentPosition, desiredPosition, smoothSpeed * Time.deltaTime);
            transform.position = smoothedPosition;
        }
    }
}