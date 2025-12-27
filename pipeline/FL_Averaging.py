from zenml import pipeline
from steps.ingest_data import ingest_data_step
from steps.data_augumentation import data_augmentation_step
from steps.visualization import visualize
from steps.evaluation import evaluate_model_step
from steps.federate_averagingstep import federate_averaging_step
from steps.updateddatastep import decision_step
from steps.status_updatestep import status_update_step
import torch


@pipeline
def FL_Averaging(data_path: str, path_model: str , doc_id: str):
    """Federated Learning Averaging Pipeline"""

    output_path = "./global_model/updated_global_model.pth"
    global_model_path = r"C:\Users\Amin\Desktop\federated server\brain_tumor_cnn.pth"

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Ingest + visualize
    data = ingest_data_step(data_path)
    visualize(data)

    # Data loaders
    train_loader, test_loader, class_names = data_augmentation_step(data)

    # Evaluation step (returns real metrics at runtime)
    accuracy, precision, recall = evaluate_model_step(
        model_path=path_model,
        test_loader=test_loader,
        device=device,
        class_names=class_names,
    )

    # Decision step (comparison happens INSIDE the step)
    status = decision_step(accuracy)   # <-- StepArtifact[bool]

    # Federated averaging step decides internally
    statusA=federate_averaging_step(
        global_model_path=global_model_path,
        model_path=path_model,
        output_path=output_path,
        status=status,
    )
    status_update_step(
        doc_id=doc_id,
        status=statusA,
        accuracy=accuracy,
    ) 

