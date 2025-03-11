"""
Metric - Class representing an individual evaluation metric in the Metacognitive Analysis Framework.
"""

from typing import Callable, Dict, Any, Optional
import json


class Metric:
    """
    Represents a single evaluation metric within a dimension.
    Each metric has a name, weight, evaluation function, and score.
    """
    
    def __init__(self, name: str, weight: float, evaluation_fn: Optional[Callable] = None):
        """
        Initialize a new metric.
        
        Args:
            name: Name of the metric
            weight: Weight of this metric within its dimension (0 to 1)
            evaluation_fn: Function to evaluate this metric (optional)
        """
        self.name = name
        
        if not 0 <= weight <= 1:
            raise ValueError(f"Weight must be between 0 and 1, got {weight}")
        self.weight = weight
        
        self.evaluation_fn = evaluation_fn
        self.score = 0.0
        self.raw_results = {}  # Store raw evaluation data
    
    def evaluate(self, *args, **kwargs) -> float:
        """
        Evaluate this metric using its evaluation function.
        
        Args:
            *args, **kwargs: Arguments to pass to the evaluation function
            
        Returns:
            Score between 0 and 1
        """
        if self.evaluation_fn is None:
            raise ValueError(f"No evaluation function set for metric '{self.name}'")
        
        score = self.evaluation_fn(*args, **kwargs)
        
        if not 0 <= score <= 1:
            raise ValueError(f"Evaluation function for metric '{self.name}' returned score {score}, which is not between 0 and 1")
        
        self.score = score
        return score
    
    def set_evaluation_function(self, fn: Callable):
        """
        Set or update the evaluation function for this metric.
        
        Args:
            fn: Function to evaluate this metric
        """
        self.evaluation_fn = fn
    
    def add_result_data(self, key: str, value: Any):
        """
        Add additional result data for this metric.
        
        Args:
            key: Key for the result data
            value: Value to store
        """
        self.raw_results[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metric to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the metric
        """
        return {
            'name': self.name,
            'weight': self.weight,
            'score': self.score,
            'raw_results': self.raw_results
        }