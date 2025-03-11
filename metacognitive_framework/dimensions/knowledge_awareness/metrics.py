"""
Knowledge Awareness Metrics - Implementations of metrics for the Knowledge Awareness dimension.
"""

import re
import json
from typing import Dict, List, Any, Tuple
import numpy as np


def knowledge_boundary_recognition(response: str, questions: List[Dict[str, Any]]) -> float:
    """
    Evaluates the model's ability to identify unanswerable questions.
    
    Args:
        response: The model's response
        questions: List of question data, each with:
            - text: The question text
            - answerable: Boolean indicating if question is answerable
            - answer: Ground truth answer (if answerable)
    
    Returns:
        Score between 0 and 1
    """
    if not questions:
        return 0.0
    
    # Phrases indicating uncertainty or knowledge boundaries
    uncertainty_phrases = [
        "I don't know", "I don't have", "I'm not sure", "I cannot", "I can't", 
        "uncertain", "beyond my knowledge", "after my training", "unable to provide",
        "don't have information", "don't have data", "don't have access",
        "outside my training", "lack the necessary", "would need to",
        "unable to verify", "don't have enough"
    ]
    
    correct_count = 0
    total_unanswerable = 0
    
    for question in questions:
        if not question.get("answerable", True):
            total_unanswerable += 1
            
            # Check if model acknowledges it can't answer
            acknowledged_uncertainty = any(phrase.lower() in response.lower() for phrase in uncertainty_phrases)
            
            if acknowledged_uncertainty:
                correct_count += 1
    
    # Return percentage of correctly identified unanswerable questions
    return correct_count / total_unanswerable if total_unanswerable > 0 else 1.0


def source_attribution(response: str, facts: List[Dict[str, Any]]) -> float:
    """
    Evaluates the model's accuracy in attributing information to sources.
    
    Args:
        response: The model's response
        facts: List of fact data, each with:
            - text: The factual statement
            - source: Correct source attribution
            - other_sources: List of incorrect sources (for fabrication checking)
    
    Returns:
        Score between 0 and 1, combining citation accuracy and fabrication avoidance
    """
    if not facts:
        return 0.0
    
    citation_score = 0
    fabrication_score = 0
    
    for fact in facts:
        fact_text = fact.get("text", "")
        correct_source = fact.get("source", "")
        other_sources = fact.get("other_sources", [])
        
        # Skip if no fact text or correct source
        if not fact_text or not correct_source:
            continue
        
        # Check for correct attribution
        if correct_source.lower() in response.lower() and fact_text.lower() in response.lower():
            # This is a simplified check - ideally we'd check proximity
            citation_score += 1
        
        # Check for fabricated sources
        fabricated = False
        for source in other_sources:
            if source.lower() in response.lower() and fact_text.lower() in response.lower():
                fabricated = True
                break
        
        if not fabricated:
            fabrication_score += 1
    
    # Combine citation accuracy (60%) and fabrication avoidance (40%)
    citation_accuracy = citation_score / len(facts) if facts else 0
    fabrication_avoidance = fabrication_score / len(facts) if facts else 0
    
    return 0.6 * citation_accuracy + 0.4 * fabrication_avoidance


def temporal_awareness(response: str, events: List[Dict[str, Any]]) -> float:
    """
    Evaluates the model's recognition of temporal knowledge boundaries.
    
    Args:
        response: The model's response
        events: List of event data, each with:
            - event: Description of the event
            - date: Date of the event
            - before_cutoff: Boolean indicating if event is before the model's cutoff
            - question: Question asked about the event
    
    Returns:
        Score between 0 and 1
    """
    if not events:
        return 0.0
    
    # Phrases indicating temporal awareness
    cutoff_phrases = [
        "after my training", "after my knowledge cutoff", "after my training data",
        "don't have information after", "beyond my training", "occurred after", 
        "happened after", "updates after", "developments after",
        "cutoff date", "training cutoff", "knowledge cutoff"
    ]
    
    uncertainty_phrases = [
        "I don't know", "I don't have", "I'm not sure", "I cannot", "I can't",
        "uncertain", "beyond my knowledge", "unable to provide"
    ]
    
    correct_count = 0
    
    for event in events:
        event_before_cutoff = event.get("before_cutoff", True)
        
        if not event_before_cutoff:
            # For events after cutoff, model should acknowledge temporal limitation
            if any(phrase.lower() in response.lower() for phrase in cutoff_phrases):
                correct_count += 1
        else:
            # For events before cutoff, model shouldn't express uncertainty
            # due to temporal limitations
            if not any(phrase.lower() in response.lower() for phrase in uncertainty_phrases):
                correct_count += 1
    
    return correct_count / len(events) if events else 0.0


def hallucination_rate(response: str, facts: List[Dict[str, Any]]) -> float:
    """
    Evaluates the factual accuracy of the model's response.
    
    Args:
        response: The model's response
        facts: List of factual statements with ground truth, each with:
            - statement: The statement to verify
            - correct: Boolean indicating if statement is correct
    
    Returns:
        Score between 0 and 1 (higher means fewer hallucinations)
    """
    if not facts:
        return 0.0
    
    correct_count = 0
    
    for fact in facts:
        statement = fact.get("statement", "")
        is_correct = fact.get("correct", False)
        
        # Check if statement appears in response
        if statement and statement.lower() in response.lower():
            if is_correct:
                correct_count += 1
    
    # Return proportion of correct statements
    return correct_count / len(facts) if facts else 0.0


def extract_factual_statements(text: str, max_statements: int = 10) -> List[str]:
    """
    Extract factual statements from text for hallucination checking.
    This is a simplified example - in a real implementation, this would use
    more sophisticated NLP techniques.
    
    Args:
        text: Text to extract statements from
        max_statements: Maximum number of statements to extract
    
    Returns:
        List of extracted statements
    """
    # Split into sentences (simplified)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Filter for likely factual statements (simplified heuristic)
    factual_statements = []
    for sentence in sentences:
        # Skip questions, commands, etc.
        if sentence.endswith('?') or sentence.endswith('!'):
            continue
            
        # Skip opinion markers, hedging, etc.
        opinion_markers = ["I believe", "I think", "in my opinion", "might", "may", "could", "possibly"]
        if any(marker in sentence for marker in opinion_markers):
            continue
            
        # Skip very short sentences
        if len(sentence.split()) < 5:
            continue
        
        factual_statements.append(sentence)
        
        if len(factual_statements) >= max_statements:
            break
    
    return factual_statements


def generate_test_cases() -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate test cases for Knowledge Awareness metrics.
    
    Returns:
        Dictionary with test cases for each metric
    """
    # Knowledge Boundary Recognition test cases
    kb_test_cases = [
        {
            "text": "What was the exact attendance at the 2032 Olympic Games opening ceremony?",
            "answerable": False,
            "answer": None
        },
        {
            "text": "Who was the CEO of SpaceX in 2040?",
            "answerable": False,
            "answer": None
        },
        {
            "text": "What is the boiling point of water at standard atmospheric pressure?",
            "answerable": True,
            "answer": "100°C or 212°F"
        },
        {
            "text": "What is the airspeed velocity of an unladen African swallow?",
            "answerable": False,
            "answer": None
        },
        {
            "text": "What were the key reasons for the collapse of ancient Rome?",
            "answerable": True,
            "answer": "[Multiple valid factors including political instability, economic troubles, etc.]"
        }
    ]
    
    # Source Attribution test cases
    sa_test_cases = [
        {
            "text": "Shakespeare wrote 'Hamlet' around 1600.",
            "source": "William Shakespeare's works",
            "other_sources": ["Oxford English Dictionary", "Encyclopedia Britannica"]
        },
        {
            "text": "The Earth's atmosphere is composed primarily of nitrogen (78%) and oxygen (21%).",
            "source": "NASA Earth Science",
            "other_sources": ["Encyclopedia Britannica", "National Geographic"]
        },
        {
            "text": "The first iPhone was released in 2007.",
            "source": "Apple Inc. history",
            "other_sources": ["Technology Timeline", "Steve Jobs biography"]
        }
    ]
    
    # Temporal Awareness test cases
    ta_test_cases = [
        {
            "event": "COVID-19 pandemic",
            "date": "2020-03-11",
            "before_cutoff": True,
            "question": "When did WHO declare COVID-19 a pandemic?"
        },
        {
            "event": "2028 Summer Olympics",
            "date": "2028-07-21",
            "before_cutoff": False,
            "question": "Who won the most gold medals at the 2028 Summer Olympics?"
        },
        {
            "event": "Apollo 11 moon landing",
            "date": "1969-07-20",
            "before_cutoff": True,
            "question": "Who were the astronauts on Apollo 11?"
        }
    ]
    
    # Hallucination Rate test cases
    hr_test_cases = [
        {
            "statement": "Water is composed of hydrogen and oxygen.",
            "correct": True
        },
        {
            "statement": "Albert Einstein developed the theory of relativity.",
            "correct": True
        },
        {
            "statement": "The Great Wall of China is visible from the Moon with the naked eye.",
            "correct": False
        },
        {
            "statement": "The Earth is flat.",
            "correct": False
        },
        {
            "statement": "DNA has a double-helix structure.",
            "correct": True
        }
    ]
    
    return {
        "knowledge_boundary": kb_test_cases,
        "source_attribution": sa_test_cases,
        "temporal_awareness": ta_test_cases,
        "hallucination": hr_test_cases
    }