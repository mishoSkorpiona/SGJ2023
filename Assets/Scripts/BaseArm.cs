using UnityEngine;
using UnityEngine.InputSystem;

public abstract class BaseArm : MonoBehaviour, IArm
{
    protected GameObject heldObject;

    public abstract void UseArm();

    public abstract void OnSecondaryMove(InputValue input);

    public virtual void GrabObject(GameObject obj)
    {
        heldObject = obj;
        heldObject.transform.SetParent(transform);
        heldObject.GetComponent<Rigidbody>().isKinematic = true;
    }

    public virtual void DropObject()
    {
        if (heldObject != null)
        {
            heldObject.transform.SetParent(null);
            heldObject.GetComponent<Rigidbody>().isKinematic = false;
            heldObject = null;
        }
    }
}