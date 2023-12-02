using UnityEngine;
using UnityEngine.InputSystem;

public class ArmHammer : BaseArm
{
    [SerializeField] private float swingForce = 10f;

    // Additional properties or methods specific to ArmHammer can be added here

    public override void UseArm()
    {
        // Implementation for using the hammer
        Debug.Log("Using Hammer");
        Swing();
    }

    public override void SecondaryMoveDir(Vector2 input)
    {
        // Implementation for secondary move with the hammer
        // For example, adjust the swing force based on input
        float inputStrength = input.magnitude;
        swingForce = inputStrength * 10f; // Adjust as needed
    }

    // Implement other methods as needed

    private void Swing()
    {
        // Implementation for swinging the hammer
        if (heldObject != null)
        {
            // Apply a force to the held object to simulate a swing
            Rigidbody heldObjectRigidbody = heldObject.GetComponent<Rigidbody>();
            if (heldObjectRigidbody != null)
            {
                heldObjectRigidbody.AddForce(transform.forward * swingForce, ForceMode.Impulse);
            }
        }
    }
}