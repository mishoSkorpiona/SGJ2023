// IArm.cs

using UnityEngine;
using UnityEngine.InputSystem;

public interface IArm
{
    void UseArm();
    void OnSecondaryMove(InputValue input);
    void GrabObject(GameObject obj);
    void DropObject();
    // Add other methods as needed
}