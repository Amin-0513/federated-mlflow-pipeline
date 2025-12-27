import torch
from zenml import step

@step
def federate_averaging_step(
    global_model_path: str,
    model_path: str,
    output_path: str,
    status: bool,
) -> str:
    if not status:
        print("Skipping federated averaging (accuracy too low)")
        return "failed"

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load models to available device
    global_state = torch.load(global_model_path, map_location=device)
    local_state = torch.load(model_path, map_location=device)

    # Ensure keys match
    for key in global_state.keys():
        if key in local_state:
            global_state[key] = (global_state[key] + local_state[key]) / 2
        else:
            print(f"Warning: Key {key} not found in local model. Skipping averaging for this parameter.")

    torch.save(global_state, output_path)
    print("Federated averaging completed successfully")
    return "success"
