"""
Framework - Main class for the Metacognitive Analysis Framework.
Combines all dimensions and calculates the overall confidence score.
"""

from typing import Dict, List, Any, Optional
import json
import os
import datetime
from .dimension import Dimension


class MetacognitiveFramework:
    """
    Main class for the Metacognitive Analysis Framework.
    Manages dimensions, evaluates LLM responses, and calculates confidence scores.
    """
    
    def __init__(self):
        """Initialize the framework with empty dimensions."""
        self.dimensions: Dict[str, Dimension] = {}
        self.results = {}  # Store evaluation results
        self.metadata = {
            'creation_time': datetime.datetime.now().isoformat(),
            'description': 'Metacognitive Analysis Framework for evaluating LLM reasoning'
        }
    
    def add_dimension(self, dimension: Dimension):
        """
        Add a dimension to the framework.
        
        Args:
            dimension: Dimension object to add
        """
        # Check if total weight would exceed 1.0
        total_weight = sum(d.weight for d in self.dimensions.values())
        if total_weight + dimension.weight > 1.0 + 1e-10:  # Allow small floating point error
            raise ValueError(f"Adding dimension '{dimension.name}' with weight {dimension.weight} would exceed total weight of 1.0 (current: {total_weight})")
        
        self.dimensions[dimension.name] = dimension
    
    def get_dimension(self, name: str) -> Optional[Dimension]:
        """
        Get a dimension by name.
        
        Args:
            name: Name of the dimension to get
            
        Returns:
            The dimension, or None if not found
        """
        return self.dimensions.get(name)
    
    def evaluate(self, llm_response: str, **kwargs) -> Dict[str, Any]:
        """
        Evaluate an LLM response using all dimensions.
        
        Args:
            llm_response: The response from the LLM to evaluate
            **kwargs: Additional arguments to pass to dimension evaluators
            
        Returns:
            Dictionary with evaluation results
        """
        dimension_scores = {}
        for name, dimension in self.dimensions.items():
            dimension_score = dimension.evaluate(llm_response, **kwargs)
            dimension_scores[name] = dimension_score
        
        # Calculate overall confidence score
        confidence_score = 0.0
        for name, score in dimension_scores.items():
            confidence_score += score * self.dimensions[name].weight
        
        # Store results
        self.results = {
            'confidence_score': confidence_score,
            'dimension_scores': dimension_scores,
            'evaluation_time': datetime.datetime.now().isoformat()
        }
        
        return self.results
    
    def save_results(self, output_dir: str):
        """
        Save all evaluation results to JSON files.
        
        Args:
            output_dir: Directory to save results
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a unique run ID
        run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save overall results
        overall_result = {
            'framework': 'Metacognitive Analysis Framework',
            'confidence_score': self.results.get('confidence_score', 0.0),
            'dimension_scores': self.results.get('dimension_scores', {}),
            'metadata': self.metadata,
            'evaluation_time': self.results.get('evaluation_time', datetime.datetime.now().isoformat())
        }
        
        overall_filepath = os.path.join(output_dir, f"overall_results_{run_id}.json")
        with open(overall_filepath, 'w') as f:
            json.dump(overall_result, f, indent=2)
        
        print(f"Overall results saved to {overall_filepath}")
        
        # Save detailed dimension results
        for dimension in self.dimensions.values():
            dimension.save_results(output_dir, run_id)