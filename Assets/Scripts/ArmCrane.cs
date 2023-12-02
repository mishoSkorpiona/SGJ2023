using UnityEngine;
using UnityEngine.InputSystem;

public class ArmCrane : BaseArm
{
    [SerializeField] private float moveSpeed = 5f;
    private Vector2 moveDir;
    [SerializeField] private float armRange = 3;
    [SerializeField] private Transform anchorPoint; // The point where the crane anchors to the pipe
    [SerializeField] private float pullSpeed = 2f; // Speed at which the player is pulled up
    [SerializeField] private GameObject craneHookPoint;
    [SerializeField]private bool isAnchored = false;


    void Update()
    {
        Move();
    }

    public override void UseArm()
    {
        // Implementation for using the crane arm
        Debug.Log("Using Crane Arm");
        if (heldObject != null)
        {
            DropObject();
        }
        else
        {
            Collider[] hitColliders = Physics.OverlapSphere(craneHookPoint.transform.position, 0.2f);
            foreach (var hitCollider in hitColliders)
            {
                if (hitCollider.CompareTag("Crate"))
                {
                    GrabObject(hitCollider.gameObject);
                    Debug.Log("Pickup crate");
                    hitCollider.gameObject.GetComponent<Collider>().isTrigger = true;
                }
                
                if (hitCollider.CompareTag("Arm"))
                {
                    GrabObject(hitCollider.gameObject);
                    Debug.Log("Pickup crate");
                    hitCollider.gameObject.GetComponent<Collider>().isTrigger = true;
                }
            }
        }

    }


    public virtual void GrabObject(GameObject obj)
    {
        heldObject = obj;
        heldObject.transform.SetParent(craneHookPoint.transform);
        heldObject.GetComponent<Rigidbody>().isKinematic = true;
        gameObject.GetComponent<Collider>().isTrigger = true;
    }

    public override void SecondaryMoveDir(Vector2 input)
    {
        // Implementation for secondary move with the crane arm
        if (!isAnchored)
        {
            moveDir = input;
            // moveDir = new Vector2(moveDir.x, -moveDir.y);
        }
    }

    // Add or override other methods as needed

    private void Move()
    {
        // add arm range & constrains 
        if (craneHookPoint.transform.localPosition.magnitude < armRange)
            craneHookPoint.transform.Translate(moveDir * moveSpeed * Time.deltaTime);
        if (moveDir.magnitude < 0.1f)
            craneHookPoint.transform.localPosition *= 0.95f;
    }

    private void DetectObjectInRange()
    {
        foreach (var collider1 in Physics.OverlapSphere(craneHookPoint.transform.position, 0.2f))
        {
            
        }
    }

    private void AnchorToPipe()
    {
        // Implementation for anchoring the crane arm to the pipe
        isAnchored = true;
    }

    private void ReleaseAnchor()
    {
        // Implementation for releasing the crane arm from the pipe
        isAnchored = false;
    }
    

    private void FixedUpdate()
    {
        // Pull the player upwards if anchored to a pipe
        if (isAnchored)
        {
            
        }
    }
}