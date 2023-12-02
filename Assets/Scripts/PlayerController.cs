using System.Collections;
using System.Collections.Generic;
using UnityEditor;
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

    public bool inADetachZone;

    [SerializeField] private GameObject attachParticle;

    [SerializeField ]private BaseArm activeArm; // Assuming you have a BaseArm class

    private void Start()
    {
        Rigidbody player = this.GetComponent<Rigidbody>();
        player.maxLinearVelocity = 5.0f;
        

    }

    void Update()
    {
        
        Debug.DrawLine(transform.position, transform.position + transform.forward, Color.green);
        if (movedirection.sqrMagnitude < 0.01f)
            return;

        Rigidbody player = this.GetComponent<Rigidbody>();
        player.AddForce(movedirection * movespeed * Time.deltaTime, ForceMode.Acceleration);

        transform.forward = Vector3.RotateTowards(transform.forward, movedirection, 0.03f, 0.0f);
    }

    
    void OnSecondaryMove(InputValue input)
    {
        var secondaryMoveDirection = input.Get<Vector2>();
        if (activeArm != null)
            activeArm.SecondaryMoveDir(secondaryMoveDirection);
    }
    
    void OnDetachArm()
    {
        if (inADetachZone && activeArm != null)
        {
            //detatch arm 
        }
    }

    void OnAttatch()
    {
        AttachArm();
    }
    
    void AttachArm()
    {
        
        Collider[] hitColliders = Physics.OverlapSphere(transform.position+ transform.forward, 1);
        foreach (var hitCollider in hitColliders)
        { 
            if(hitCollider.CompareTag("Arm")) 
                 Debug.Log("sees an arm");
            if (insLArmSocket == null)
            {
                Instantiate(attachParticle, lArmSocket.transform);
                insLArmSocket = hitCollider.gameObject;
                insLArmSocket.transform.parent = lArmSocket.transform;
                insLArmSocket.transform.localPosition= Vector3.zero;
                
                if (insLArmSocket != null)
                {
                    activeArm = insLArmSocket.GetComponent<BaseArm>();
                    Debug.Log("We got an active arm ");
                }
            }
        }    
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
