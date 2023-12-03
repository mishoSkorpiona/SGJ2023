// IArm.cs

using UnityEngine;
using UnityEngine.InputSystem;


public interface IArm
{
    int UseArm();
    void SecondaryMoveDir(Vector2 input);
    void GrabObject(GameObject obj);
    void DropObject();
    // Add other methods as needed
}