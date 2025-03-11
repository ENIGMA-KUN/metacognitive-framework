"""
Base Evaluator - Abstract base class for all dimension evaluators in the Metacognitive Analysis Framework.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
import json
import os


class BaseEvaluator(ABC):
    """
    Abstract base class for all dimension evaluators.
    Each dimension evaluator (Knowledge Awareness, Reasoning Quality, etc.) 
    should inherit from this class.
    """
    
    def __init__(self, name: str, weight: float):
        """
        Initialize the base evaluator.
        
        Args:
            name: Name of the evaluator/dimension
            weight: Weight of this dimension in the overall confidence score
        """
        self.name = name
        self.weight = weight
        self.metrics = {}  # Dictionary to store metrics and their weights
        self.results = {}  # Store evaluation results
    
    def add_metric(self, name: str, weight: float):
        """
        Add a new metric to this evaluator.
        
        Args:
            name: Name of the metric
            weight: Weight of this metric within the dimension
        """
        if sum(metric['weight'] for metric in self.metrics.values()) + weight > 1.0:
            raise ValueError(f"Adding metric '{name}' would exceed total weight of 1.0")
        
        self.metrics[name] = {
            'weight': weight,
            'score': 0.0
        }
    
    def set_metric_score(self, metric_name: str, score: float):
        """
        Set the score for a specific metric.
        
        Args:
            metric_name: Name of the metric
            score: Score value between 0 and 1
        """
        if metric_name not in self.metrics:
            raise ValueError(f"Metric '{metric_name}' not found in evaluator '{self.name}'")
        
        if not 0 <= score <= 1:
            raise ValueError(f"Score must be between 0 and 1, got {score}")
        
        self.metrics[metric_name]['score'] = score
    
    def calculate_dimension_score(self) -> float:
        """
        Calculate the overall score for this dimension using the weighted sum of metrics.
        
        Returns:
            The weighted score for this dimension
        """
        if not self.metrics:
            return 0.0
        
        total_score = 0.0
        for metric_name, metric_data in self.metrics.items():
            total_score += metric_data['score'] * metric_data['weight']
        
        return total_score
    
    @abstractmethod
    def evaluate(self, llm_response: str, **kwargs) -> float:
        """
        Evaluate an LLM response and return a score for this dimension.
        Must be implemented by subclasses.
        
        Args:
            llm_response: The response from the LLM to evaluate
            **kwargs: Additional arguments specific to each evaluator
            
        Returns:
            The score for this dimension (0 to 1)
        """
        pass
    
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
            'dimension_score': self.calculate_dimension_score(),
            'metrics': self.metrics,
            'additional_data': self.results
        }
        
        filename = f"{self.name.lower().replace(' ', '_')}_{run_id}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"Results saved to {filepath}")