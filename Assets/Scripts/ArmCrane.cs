using UnityEngine;
using UnityEngine.InputSystem;

public class ArmCrane : BaseArm
{
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private Transform anchorPoint; // The point where the crane anchors to the pipe
    [SerializeField] private float pullSpeed = 2f; // Speed at which the player is pulled up

    private bool isAnchored = false;

    public override void UseArm()
    {
        // Implementation for using the crane arm
        Debug.Log("Using Crane Arm");
    }

    public override void OnSecondaryMove(InputValue input)
    {
        // Implementation for secondary move with the crane arm
        Vector2 inputVector = input.Get<Vector2>();
        if (!isAnchored)
        {
            Move(new Vector3(inputVector.x, 0, inputVector.y).normalized);
        }
    }

    // Add or override other methods as needed

    private void Move(Vector3 input)
    {
        transform.Translate(input * moveSpeed * Time.deltaTime);
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
            Rigidbody playerRigidbody = GetComponentInParent<Rigidbody>();
            if (playerRigidbody != null)
            {
                playerRigidbody.AddForce(Vector3.up * pullSpeed, ForceMode.Acceleration);
            }
        }
    }
}