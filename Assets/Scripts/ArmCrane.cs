using Unity.Mathematics;
using UnityEngine;
using UnityEngine.InputSystem;

public class ArmCrane : BaseArm
{
    [SerializeField] private float moveSpeed = 5f;
    private Vector2 moveDir;
    [SerializeField] private GameObject craneHookPoint;
    [SerializeField] private bool isAnchored = false;

    [SerializeField] private GameObject leftModel;
    [SerializeField] private GameObject rightModel;


    void Update()
    {
        Move();
        AdjustArm();
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
                    break;
                }
                
                if (hitCollider.CompareTag("Arm"))
                {
                    Debug.Log("tries to Pickup arm");
                    
                    if (hitCollider.GetComponent<BaseArm>().isTheArmInUse)
                        continue;
                    
                    GrabObject(hitCollider.gameObject);
                    Debug.Log("Pickup arm");
                    break;
                }
            }
        }
    }

    void AdjustArm()
    {
        if (isArmLeft)
        {
            rightModel.SetActive(false);
            leftModel.SetActive(true);
        }
        else
        {
            rightModel.SetActive(true);
            leftModel.SetActive(false);
        }
    }


    public virtual void GrabObject(GameObject obj)
    {
        heldObject = obj;

        if (heldObject.CompareTag("Arm"))
        {
            heldObject.GetComponent<Collider>().isTrigger = true;
        }
        heldObject.GetComponent<Rigidbody>().isKinematic = true;

        heldObject.transform.SetParent(craneHookPoint.transform, true);

        heldObject.transform.localPosition = Vector3.zero;
        heldObject.transform.localRotation = Quaternion.Euler(Vector3.zero);
    }

    public virtual void DropObject()
    {
        if (!heldObject)
            return;

        bool isArm = heldObject.CompareTag("Arm");
        if (isArm)
        {
            Collider[] hitColliders = Physics.OverlapSphere(heldObject.transform.position + transform.forward, 2.5f);
            foreach (var hitCollider in hitColliders)
            {
                if (hitCollider.CompareTag("Enemy"))
                {
                    GameObject lArm = hitCollider.gameObject.transform.Find("lArmSocket").gameObject;
                    if (lArm)
                    {
                        BaseArm baseArm = heldObject.GetComponent<BaseArm>();
                        if (baseArm)
                            baseArm.isArmLeft = true;

                        heldObject.transform.SetParent(lArm.transform);
                        heldObject.transform.localPosition = Vector3.zero;
                        heldObject.transform.localRotation = Quaternion.Euler(Vector3.zero);
                        heldObject = null;
                        return;
                    }
                }
            }
        }

        ////////////////////////////////////////////////////
        if (isArm)
        {
            heldObject.GetComponent<Collider>().isTrigger = false;
        }
        heldObject.GetComponent<Rigidbody>().isKinematic = false;

        heldObject.transform.SetParent(null);
        
        heldObject = null;
    }

    public override void SecondaryMoveDir(Vector2 input)
    {
        moveDir = input;
    }

    // Add or override other methods as needed

    private void Move()
    {
        transform.localRotation = quaternion.Euler(Vector2.Angle(moveDir, Vector2.left),0,0);
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