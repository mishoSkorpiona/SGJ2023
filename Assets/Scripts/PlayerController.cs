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

    [SerializeField] private GameObject lArmSocket;
    [SerializeField] private GameObject rArmSocket;

    public bool inADetachZone;

    [SerializeField] private GameObject attachParticle;

    [SerializeField ]private GameObject activeArm; 

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
            activeArm.GetComponent<BaseArm>().SecondaryMoveDir(secondaryMoveDirection);
    }
    
    void OnDetach()
    {
        Collider[] hitColliders = Physics.OverlapSphere(transform.position, 1);
        foreach (var hitCollider in hitColliders)
        {
            if (hitCollider.CompareTag("DetachZone"))
            {
                if (Detach(lArmSocket) || Detach(rArmSocket))
                    break;
            }
        }
    }

    bool Detach(GameObject Socket)
    {
        if (!Socket)
            return false;

        int childCount = Socket.transform.childCount;
        if (childCount <= 0)
            return false;

        for (int i = 0; i < childCount; ++i)
        {
            GameObject arm = Socket.transform.GetChild(i).gameObject;
            if (arm)
            {
                BaseArm baseArm = arm.GetComponent<BaseArm>();
                if (baseArm)
                {
                    baseArm.isTheArmInUse = false;

                    baseArm.GetComponent<Collider>().isTrigger = false;
                    baseArm.GetComponent<Rigidbody>().isKinematic = false;
                }
            }
        }

        Instantiate(attachParticle, Socket.transform);
        Debug.Log("detach arm");
        Socket.transform.DetachChildren();
        return true;
    }

    void OnAttatch()
    {
        AttachArm();
    }
    
    void AttachArm()
    {
        GameObject freeSocket = null;

        if (lArmSocket && lArmSocket.transform.childCount <= 0)
        {
            freeSocket = lArmSocket;
        }
        else if (rArmSocket && rArmSocket.transform.childCount <= 0)
        {
            freeSocket = rArmSocket;
        }

        if (!freeSocket)
            return;

        Collider[] hitColliders = Physics.OverlapSphere(transform.position + transform.forward, 1);
        foreach (var hitCollider in hitColliders)
        {
            if (!hitCollider.CompareTag("Arm"))
                continue;

            if (hitCollider.GetComponent<BaseArm>().isTheArmInUse)
                continue;

            Instantiate(attachParticle, freeSocket.transform);

            var newArm = hitCollider.gameObject;
            newArm.transform.parent = freeSocket.transform;
            newArm.transform.localPosition = Vector3.zero;
            newArm.transform.localRotation = Quaternion.Euler(Vector3.zero);

            newArm.GetComponent<Collider>().isTrigger = true;
            newArm.GetComponent<Rigidbody>().isKinematic = true;

            activeArm = newArm;

            BaseArm baseArm = newArm.GetComponent<BaseArm>();
            baseArm.isTheArmInUse = true;

            if (baseArm.isArmLeft)
            {
                if (freeSocket == rArmSocket)
                    baseArm.isArmLeft = false;
            }
            else // right arm
            {
                if (freeSocket == lArmSocket)
                    baseArm.isArmLeft = true;
            }

            Debug.Log("We got an active arm ");
            break;
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
        if (activeArm == null)
        {
            Debug.Log("nqmash ruki brat");
            return;
        }
        activeArm.GetComponent<BaseArm>().UseArm();
    }
}
