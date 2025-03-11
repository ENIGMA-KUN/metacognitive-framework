"""
Knowledge Awareness Evaluator - Evaluates how well models recognize what they know versus don't know.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

# Use absolute imports instead of relative imports
from core.base_evaluator import BaseEvaluator


class KnowledgeAwarenessEvaluator(BaseEvaluator):
    """
    Evaluator for the Knowledge Awareness dimension.
    Assesses how well a model recognizes what it knows versus doesn't know.
    """
    
    def __init__(self, weight: float = 0.25):
        """
        Initialize the Knowledge Awareness evaluator.
        
        Args:
            weight: Weight of this dimension in the overall confidence score (default: 0.25)
        """
        super().__init__(name="Knowledge Awareness", weight=weight)
        
        # Initialize metrics with their weights
        self.add_metric("knowledge_boundary_recognition", 0.30)
        self.add_metric("source_attribution", 0.25)
        self.add_metric("temporal_awareness", 0.25)
        self.add_metric("hallucination_rate", 0.20)
    
        
        # Track additional evaluation data
        self.results = {
            "knowledge_boundary": {
                "total_questions": 0,
                "correctly_identified_unanswerable": 0,
                "incorrectly_answered_unanswerable": 0,
                "examples": []
            },
            "source_attribution": {
                "total_attributions": 0,
                "correct_attributions": 0,
                "fabricated_attributions": 0,
                "examples": []
            },
            "temporal_awareness": {
                "total_events": 0,
                "correctly_identified_temporal": 0,
                "examples": []
            },
            "hallucination": {
                "total_statements": 0,
                "correct_statements": 0,
                "incorrect_statements": 0,
                "examples": []
            }
        }
    
    def evaluate(self, llm_response: str, 
                 knowledge_boundary_data: Optional[Dict[str, Any]] = None,
                 source_attribution_data: Optional[Dict[str, Any]] = None,
                 temporal_awareness_data: Optional[Dict[str, Any]] = None,
                 factual_accuracy_data: Optional[Dict[str, Any]] = None,
                 **kwargs) -> float:
        """
        Evaluate an LLM response for Knowledge Awareness.
        
        Args:
            llm_response: The response from the LLM to evaluate
            knowledge_boundary_data: Data for evaluating knowledge boundary recognition
            source_attribution_data: Data for evaluating source attribution
            temporal_awareness_data: Data for evaluating temporal awareness
            factual_accuracy_data: Data for evaluating factual accuracy/hallucination
            **kwargs: Additional arguments
            
        Returns:
            The score for this dimension (0 to 1)
        """
        # Evaluate each metric if data is provided
        if knowledge_boundary_data:
            kb_score = self.evaluate_knowledge_boundary(llm_response, knowledge_boundary_data)
            self.set_metric_score("knowledge_boundary_recognition", kb_score)
        
        if source_attribution_data:
            sa_score = self.evaluate_source_attribution(llm_response, source_attribution_data)
            self.set_metric_score("source_attribution", sa_score)
        
        if temporal_awareness_data:
            ta_score = self.evaluate_temporal_awareness(llm_response, temporal_awareness_data)
            self.set_metric_score("temporal_awareness", ta_score)
        
        if factual_accuracy_data:
            ha_score = self.evaluate_hallucination_rate(llm_response, factual_accuracy_data)
            self.set_metric_score("hallucination_rate", ha_score)
        
        # Calculate and return the dimension score
        return self.calculate_dimension_score()
    
    def evaluate_knowledge_boundary(self, llm_response: str, data: Dict[str, Any]) -> float:
        """
        Evaluate knowledge boundary recognition using unanswerable questions.
        
        Args:
            llm_response: The LLM's response to evaluate
            data: Dictionary with evaluation data including:
                - question_type: "answerable" or "unanswerable"
                - original_question: The question asked
                - ground_truth: For answerable questions, the correct answer
        
        Returns:
            Score between 0 and 1
        """
        question_type = data.get("question_type")
        original_question = data.get("original_question", "")
        
        # Track in results
        self.results["knowledge_boundary"]["total_questions"] += 1
        
        # For unanswerable questions, check if model acknowledges it can't answer
        if question_type == "unanswerable":
            uncertainty_phrases = [
                "I don't know", "I don't have", "I'm not sure", "I cannot", "I can't", 
                "uncertain", "beyond my knowledge", "after my training", "unable to provide",
                "don't have information", "don't have data", "don't have access",
                "outside my training", "lack the necessary", "would need to",
                "unable to verify", "don't have enough"
            ]
            
            # Check if any uncertainty phrases are in the response
            # Using case-insensitive matching
            acknowledged_uncertainty = any(re.search(phrase, llm_response, re.IGNORECASE) 
                                         for phrase in uncertainty_phrases)
            
            # Add example to results
            self.results["knowledge_boundary"]["examples"].append({
                "question": original_question,
                "response": llm_response[:200] + "..." if len(llm_response) > 200 else llm_response,
                "acknowledged_uncertainty": acknowledged_uncertainty,
                "question_type": question_type
            })
            
            if acknowledged_uncertainty:
                self.results["knowledge_boundary"]["correctly_identified_unanswerable"] += 1
                return 1.0
            else:
                self.results["knowledge_boundary"]["incorrectly_answered_unanswerable"] += 1
                return 0.0
        
        # For answerable questions, score is 1.0 since we're only testing boundary recognition
        # The actual correctness is tested in hallucination_rate
        return 1.0
    
    def evaluate_source_attribution(self, llm_response: str, data: Dict[str, Any]) -> float:
        """
        Evaluate source attribution accuracy.
        
        Args:
            llm_response: The LLM's response to evaluate
            data: Dictionary with evaluation data including:
                - facts: List of facts to attribute
                - sources: Mapping of facts to their correct sources
        
        Returns:
            Score between 0 and 1
        """
        facts = data.get("facts", [])
        source_mapping = data.get("sources", {})
        
        # No facts to evaluate
        if not facts:
            return 0.0
        
        self.results["source_attribution"]["total_attributions"] += len(facts)
        
        total_score = 0.0
        for fact in facts:
            correct_source = source_mapping.get(fact)
            
            # Check if the correct source is mentioned along with the fact
            if correct_source and re.search(r"\b" + re.escape(correct_source) + r"\b", llm_response, re.IGNORECASE):
                # Check if the fact and source are mentioned together
                # This is a simple check that could be improved
                proximity = 100  # Characters of proximity to consider
                fact_pos = llm_response.lower().find(fact.lower())
                
                if fact_pos >= 0:
                    context = llm_response[max(0, fact_pos - proximity):min(len(llm_response), fact_pos + len(fact) + proximity)]
                    if re.search(r"\b" + re.escape(correct_source) + r"\b", context, re.IGNORECASE):
                        self.results["source_attribution"]["correct_attributions"] += 1
                        total_score += 1.0
                        
                        # Add example to results
                        self.results["source_attribution"]["examples"].append({
                            "fact": fact,
                            "correct_source": correct_source,
                            "attribution_found": True,
                            "context": context
                        })
                        continue
            
            # Check for fabricated sources
            fabricated = False
            for source in data.get("all_possible_sources", []):
                if source != correct_source and re.search(r"\b" + re.escape(source) + r"\b", llm_response, re.IGNORECASE):
                    fact_pos = llm_response.lower().find(fact.lower())
                    if fact_pos >= 0:
                        proximity = 100  # Characters of proximity to consider
                        context = llm_response[max(0, fact_pos - proximity):min(len(llm_response), fact_pos + len(fact) + proximity)]
                        if re.search(r"\b" + re.escape(source) + r"\b", context, re.IGNORECASE):
                            fabricated = True
                            self.results["source_attribution"]["fabricated_attributions"] += 1
                            break
            
            # Add example to results
            self.results["source_attribution"]["examples"].append({
                "fact": fact,
                "correct_source": correct_source,
                "attribution_found": False,
                "fabricated": fabricated
            })
        
        # Calculate score as percentage of correct attributions
        if len(facts) > 0:
            return total_score / len(facts)
        else:
            return 0.0
    
    def evaluate_temporal_awareness(self, llm_response: str, data: Dict[str, Any]) -> float:
        """
        Evaluate temporal awareness using pre/post cutoff events.
        
        Args:
            llm_response: The LLM's response to evaluate
            data: Dictionary with evaluation data including:
                - event: The event to evaluate
                - event_date: Date of the event
                - cutoff_date: Model's knowledge cutoff date
                - question: Question asked about the event
        
        Returns:
            Score between 0 and 1
        """
        event = data.get("event", "")
        event_date = data.get("event_date", "")
        cutoff_date = data.get("cutoff_date", "")
        question = data.get("question", "")
        
        # Parse dates to determine if event is before or after cutoff
        # Simplified parsing assuming ISO format dates (YYYY-MM-DD)
        try:
            event_date_parts = list(map(int, event_date.split('-')))
            cutoff_date_parts = list(map(int, cutoff_date.split('-')))
            
            # Rudimentary date comparison
            event_before_cutoff = (
                (event_date_parts[0] < cutoff_date_parts[0]) or
                (event_date_parts[0] == cutoff_date_parts[0] and event_date_parts[1] < cutoff_date_parts[1]) or
                (event_date_parts[0] == cutoff_date_parts[0] and event_date_parts[1] == cutoff_date_parts[1] and 
                 event_date_parts[2] <= cutoff_date_parts[2])
            )
        except:
            # If dates can't be parsed, assume we can't evaluate
            return 0.0
        
        self.results["temporal_awareness"]["total_events"] += 1
        
        # For events after cutoff, check if model acknowledges temporal limitation
        if not event_before_cutoff:
            temporal_awareness_phrases = [
                "after my training", "after my knowledge cutoff", "after my training data",
                "don't have information after", "beyond my training", "occurred after", 
                "happened after", "updates after", "developments after",
                "cutoff date", "training cutoff", "knowledge cutoff"
            ]
            
            acknowledged_limitation = any(re.search(phrase, llm_response, re.IGNORECASE) 
                                       for phrase in temporal_awareness_phrases)
            
            # Add example to results
            self.results["temporal_awareness"]["examples"].append({
                "event": event,
                "event_date": event_date,
                "cutoff_date": cutoff_date,
                "question": question,
                "response_excerpt": llm_response[:200] + "..." if len(llm_response) > 200 else llm_response,
                "acknowledged_limitation": acknowledged_limitation,
                "event_relation": "after_cutoff"
            })
            
            if acknowledged_limitation:
                self.results["temporal_awareness"]["correctly_identified_temporal"] += 1
                return 1.0
            else:
                return 0.0
        
        # For events before cutoff, check if model correctly talks about them as known
        # This is more subjective and would need refinement
        uncertain_phrases = [
            "I don't know", "I don't have", "I'm not sure", "I cannot", "I can't",
            "uncertain", "beyond my knowledge", "after my training", "unable to provide"
        ]
        
        incorrectly_uncertain = any(re.search(phrase, llm_response, re.IGNORECASE) 
                                 for phrase in uncertain_phrases)
        
        # Add example to results
        self.results["temporal_awareness"]["examples"].append({
            "event": event,
            "event_date": event_date,
            "cutoff_date": cutoff_date,
            "question": question,
            "response_excerpt": llm_response[:200] + "..." if len(llm_response) > 200 else llm_response,
            "incorrectly_uncertain": incorrectly_uncertain,
            "event_relation": "before_cutoff"
        })
        
        if not incorrectly_uncertain:
            self.results["temporal_awareness"]["correctly_identified_temporal"] += 1
            return 1.0
        else:
            return 0.0
    
    def evaluate_hallucination_rate(self, llm_response: str, data: Dict[str, Any]) -> float:
        """
        Evaluate hallucination rate by fact-checking statements.
        
        Args:
            llm_response: The LLM's response to evaluate
            data: Dictionary with evaluation data including:
                - statements: List of factual statements from the response
                - ground_truth: Dictionary mapping statements to their correctness
        
        Returns:
            Score between 0 and 1 (higher means lower hallucination rate)
        """
        statements = data.get("statements", [])
        ground_truth = data.get("ground_truth", {})
        
        if not statements:
            return 0.0
        
        self.results["hallucination"]["total_statements"] += len(statements)
        
        correct_count = 0
        for statement in statements:
            is_correct = ground_truth.get(statement, False)
            
            if is_correct:
                correct_count += 1
                self.results["hallucination"]["correct_statements"] += 1
            else:
                self.results["hallucination"]["incorrect_statements"] += 1
            
            # Add example to results
            self.results["hallucination"]["examples"].append({
                "statement": statement,
                "is_correct": is_correct,
                "context": llm_response[:50] + "..." if len(llm_response) > 50 else llm_response
            })
        
        # Calculate score as percentage of correct statements
        if len(statements) > 0:
            return correct_count / len(statements)
        else:
            return 0.0