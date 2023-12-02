using UnityEngine;
using UnityEngine.InputSystem;

public class ArmCrane : BaseArm
{
    [SerializeField] private float moveSpeed = 5f;
    private Vector2 moveDir;
    [SerializeField] private float armRange = 3;
    [SerializeField] private GameObject craneHookPoint;
    [SerializeField] private bool isAnchored = false;

    [SerializeField] private GameObject leftModel;
    [SerializeField] private GameObject rightModel;


    void Update()
    {
        //Move();
        ajustArm();
    }

    public override void UseArm()
    {
        Debug.Log("Using Crane Arm");
        if (heldObject != null)
        {
            Debug.Log("dropobject");
            DropObject();
        }
        else
        {
            Collider[] hitColliders = Physics.OverlapSphere(craneHookPoint.transform.position, 0.4f);
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
                    Debug.Log("tries to Pickup arm");
                    
                    if (hitCollider.GetComponent<BaseArm>().isTheArmInUse)
                        return;
                    
                    GrabObject(hitCollider.gameObject);
                    Debug.Log("Pickup arm");
                    hitCollider.gameObject.GetComponent<Collider>().isTrigger = true;
                }
            }
        }

    }

    void ajustArm()
    {
        if (!isArmLeft)
        {
            rightModel.SetActive(true);
            leftModel.SetActive(false);
        }
        else
        {
            rightModel.SetActive(false);
            leftModel.SetActive(true);
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
             moveDir = new Vector2(-moveDir.y, moveDir.x);
        }
    }

    // Add or override other methods as needed

    private void Move()
    {
        // add arm range & constrains 
        if (craneHookPoint.transform.localPosition.magnitude < armRange)
            craneHookPoint.transform.Translate(moveDir * moveSpeed * Time.deltaTime);
        if (moveDir.magnitude < 0.05f)
            craneHookPoint.transform.localPosition *= 0.95f;
        if (craneHookPoint.transform.localPosition.y < -0.5f)
            craneHookPoint.transform.localPosition.Set(0,-0.5f,0);
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