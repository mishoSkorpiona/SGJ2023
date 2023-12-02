using UnityEngine;
using UnityEngine.InputSystem;

public abstract class BaseArm : MonoBehaviour, IArm
{
    protected GameObject heldObject;
    public bool isTheArmInUse;
    public bool isArmLeft;
    public abstract void UseArm();

    public abstract void SecondaryMoveDir(Vector2 input);

    public virtual void GrabObject(GameObject obj)
    {
    }

    public virtual void DropObject()
    {
    }
}
