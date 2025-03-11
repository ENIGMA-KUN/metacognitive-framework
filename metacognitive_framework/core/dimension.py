"""
Dimension - Class representing a dimension in the Metacognitive Analysis Framework.
"""

from typing import Dict, List, Any, Callable, Optional
from .metric import Metric
import json
import os


class Dimension:
    """
    Represents a dimension in the Metacognitive Analysis Framework.
    Each dimension contains multiple metrics and has an overall weight in the framework.
    """
    
    def __init__(self, name: str, weight: float):
        """
        Initialize a new dimension.
        
        Args:
            name: Name of the dimension
            weight: Weight of this dimension in the overall framework (0 to 1)
        """
        self.name = name
        
        if not 0 <= weight <= 1:
            raise ValueError(f"Weight must be between 0 and 1, got {weight}")
        self.weight = weight
        
        self.metrics: Dict[str, Metric] = {}
        self.metadata = {}  # For storing additional information about the dimension
    
    def add_metric(self, metric: Metric):
        """
        Add a metric to this dimension.
        
        Args:
            metric: Metric object to add
        """
        # Check if total weight would exceed 1.0
        total_weight = sum(m.weight for m in self.metrics.values())
        if total_weight + metric.weight > 1.0 + 1e-10:  # Allow small floating point error
            raise ValueError(f"Adding metric '{metric.name}' with weight {metric.weight} would exceed total weight of 1.0 (current: {total_weight})")
        
        self.metrics[metric.name] = metric
    
    def calculate_score(self) -> float:
        """
        Calculate the overall score for this dimension based on its metrics.
        
        Returns:
            Score between 0 and 1
        """
        if not self.metrics:
            return 0.0
        
        total_score = 0.0
        for metric in self.metrics.values():
            total_score += metric.score * metric.weight
        
        return total_score
    
    def evaluate(self, *args, **kwargs) -> float:
        """
        Evaluate all metrics in this dimension.
        
        Args:
            *args, **kwargs: Arguments to pass to each metric's evaluate function
            
        Returns:
            Overall dimension score
        """
        for metric in self.metrics.values():
            # Each metric may need specific arguments, so let them handle their own evaluation
            try:
                metric.evaluate(*args, **kwargs)
            except Exception as e:
                print(f"Error evaluating metric '{metric.name}': {e}")
                # Continue with other metrics instead of failing completely
        
        return self.calculate_score()
    
    def save_results(self, output_dir: str, run_id: str):
        """
        Save evaluation results to a JSON file.
        
        Args:
            output_dir: Directory to save results
            run_id: Unique identifier for this evaluation run
        """
        os.makedirs(output_dir, exist_ok=True)
        
        result_data = {
            'dimension': self.name,
            'dimension_weight': self.weight,
            'dimension_score': self.calculate_score(),
            'metrics': {name: metric.to_dict() for name, metric in self.metrics.items()},
            'metadata': self.metadata
        }
        
        filename = f"{self.name.lower().replace(' ', '_')}_{run_id}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"Results saved to {filepath}")