using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;

public class PlayerController : MonoBehaviour
{
    [SerializeField] private float movespeed;
    [SerializeField] private Vector3 movedirection;
    [SerializeField] private GameObject camera;

    [SerializeField] private Transform lArmSocket;
    [SerializeField] private GameObject insLArmSocket;

    [SerializeField] private Transform rArmSocket;
    [SerializeField] private GameObject insRArmSocket;

    [SerializeField] public bool inADetachZone;

    private BaseArm activeArm; // Assuming you have a BaseArm class
    

    void Update()
    {
        if (movedirection.sqrMagnitude < 0.01f)
            return;

        Rigidbody player = this.GetComponent<Rigidbody>();
        player.AddForce(movedirection * movespeed * Time.deltaTime, ForceMode.Acceleration);
        this.transform.forward = movedirection;
    }

    void OnDetachArm()
    {
        if (inADetachZone && activeArm != null)
        {
            //detatch arm 
        }
    }

    void OnAtatchArm()
    {
        
    }
    
    void AttachArm()
    {
        
    }

    void OnMove(InputValue input)
    {
        Vector3 inputVector = input.Get<Vector2>();
        Vector3 forward = camera.transform.forward;
        Vector3 right = camera.transform.right;

        movedirection = forward * inputVector.y + right * inputVector.x;
        movedirection.y = 0; // Ensure no vertical movement
        movedirection.Normalize(); // Normalize to prevent faster movement diagonally
    }

    void OnUse()
    {
        Debug.Log("");
    }
}
