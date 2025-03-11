"""
Configuration file for the weights of dimensions and metrics in the Metacognitive Analysis Framework.
"""

# Dimension weights (must sum to 1.0)
DIMENSION_WEIGHTS = {
    "knowledge_awareness": 0.25,  # w₁
    "reasoning_quality": 0.25,    # w₂
    "uncertainty_calibration": 0.20,  # w₃
    "self_monitoring": 0.15,      # w₄
    "domain_adaptation": 0.15     # w₅
}

# Metric weights for each dimension (each set must sum to 1.0)
METRIC_WEIGHTS = {
    "knowledge_awareness": {
        "knowledge_boundary_recognition": 0.30,
        "source_attribution": 0.25,
        "temporal_awareness": 0.25,
        "hallucination_rate": 0.20
    },
    
    "reasoning_quality": {
        "logical_consistency": 0.25,
        "inference_validity": 0.25,
        "step_completeness": 0.20,
        "evidence_utilization": 0.15,
        "causal_reasoning": 0.15
    },
    
    "uncertainty_calibration": {
        "confidence_calibration": 0.35,
        "confidence_distribution": 0.25,
        "probabilistic_expression": 0.25,
        "ambiguity_recognition": 0.15
    },
    
    "self_monitoring": {
        "error_detection_rate": 0.30,
        "verification_attempts": 0.25,
        "alternative_solution_exploration": 0.25,
        "assumption_declaration": 0.20
    },
    
    "domain_adaptation": {
        "domain_recognition": 0.25,
        "terminology_precision": 0.25,
        "method_selection": 0.25,
        "expert_mimicry": 0.25
    }
}

# Ensure weights sum to 1.0
def validate_weights():
    """Validate that all weight sets sum to approximately 1.0."""
    assert abs(sum(DIMENSION_WEIGHTS.values()) - 1.0) < 1e-10, "Dimension weights must sum to 1.0"
    
    for dimension, weights in METRIC_WEIGHTS.items():
        assert abs(sum(weights.values()) - 1.0) < 1e-10, f"Metric weights for {dimension} must sum to 1.0"
    
    print("All weights validated successfully.")

if __name__ == "__main__":
    validate_weights()