from zenml import step

@step(enable_cache=False)
def decision_step(accuracy: float, threshold: float = 0.90) -> bool:
    return accuracy > threshold
