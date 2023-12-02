using UnityEngine;
using UnityEngine.InputSystem;

public class ArmProto : BaseArm
{
    public override void UseArm()
    {
        // Implementation for using the main arm
        Debug.Log("Using Main Arm");
    }

    public override void OnSecondaryMove(InputValue input)
    {
        // Implementation for secondary move with the main arm
    }

    // You can override or add more methods as needed
}