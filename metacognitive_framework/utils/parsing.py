"""
Parsing Utilities - Functions for parsing and analyzing LLM responses.
"""

import re
import json
from typing import Dict, List, Any, Tuple, Optional
import numpy as np


def extract_reasoning_steps(text: str) -> List[str]:
    """
    Extract reasoning steps from an LLM response.
    
    Args:
        text: LLM response text
        
    Returns:
        List of reasoning steps
    """
    # Pattern for numbered steps: "1.", "2.", "Step 1:", etc.
    numbered_pattern = r'(?:step\s*)?(\d+)[\.:\)]'
    
    # Look for explicit step markers
    step_markers = ["first", "second", "third", "fourth", "fifth", "step 1", "step 2", "next", "finally"]
    
    # Try to find numbered steps
    matches = re.finditer(numbered_pattern, text, re.IGNORECASE)
    matches = list(matches)
    
    if matches:
        steps = []
        for i, match in enumerate(matches):
            start_idx = match.start()
            end_idx = matches[i+1].start() if i < len(matches) - 1 else len(text)
            step_text = text[start_idx:end_idx].strip()
            steps.append(step_text)
        return steps
    
    # Try to find steps marked with step markers
    for marker in step_markers:
        if f"{marker}," in text.lower() or f"{marker}:" in text.lower():
            # Split by markers
            pattern = r'(?:{})[,:]'.format('|'.join(step_markers))
            parts = re.split(pattern, text, flags=re.IGNORECASE)
            if len(parts) > 1:
                return [part.strip() for part in parts[1:]]  # Skip the first part (before any marker)
    
    # If no explicit steps found, try to split by sentences or paragraphs
    paragraphs = text.split('\n\n')
    if len(paragraphs) > 1:
        return paragraphs
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) > 1:
        return sentences
    
    # Fallback: just return the whole text as one step
    return [text]


def extract_confidence_statements(text: str) -> List[Dict[str, Any]]:
    """
    Extract confidence statements and uncertainty expressions from an LLM response.
    
    Args:
        text: LLM response text
        
    Returns:
        List of dictionaries with confidence statements and metadata
    """
    # Confidence phrases and their approximate probability values
    confidence_mapping = {
        "certain": 0.95,
        "confident": 0.9,
        "very likely": 0.85,
        "highly likely": 0.85,
        "quite likely": 0.8,
        "likely": 0.75,
        "probable": 0.7,
        "probably": 0.7,
        "possibly": 0.5,
        "might": 0.4,
        "may": 0.4,
        "uncertain": 0.3,
        "unlikely": 0.25,
        "doubtful": 0.2,
        "highly unlikely": 0.15,
        "very unlikely": 0.15,
        "improbable": 0.1,
        "impossible": 0.05
    }
    
    # Sentences with confidence expressions
    sentences = re.split(r'(?<=[.!?])\s+', text)
    confidence_statements = []
    
    for sentence in sentences:
        # Check for explicit probability statements
        probability_match = re.search(r'(\d{1,2}(?:\.\d+)?)\s*%', sentence)
        if probability_match:
            prob_value = float(probability_match.group(1)) / 100
            confidence_statements.append({
                "text": sentence,
                "confidence_type": "explicit_percentage",
                "confidence_value": prob_value,
                "confidence_phrase": probability_match.group(0)
            })
            continue
        
        # Check for confidence phrases
        for phrase, value in confidence_mapping.items():
            if re.search(r'\b' + re.escape(phrase) + r'\b', sentence, re.IGNORECASE):
                confidence_statements.append({
                    "text": sentence,
                    "confidence_type": "verbal_expression",
                    "confidence_value": value,
                    "confidence_phrase": phrase
                })
                break
    
    return confidence_statements


def extract_self_corrections(text: str) -> List[Dict[str, Any]]:
    """
    Extract self-corrections and verification attempts from an LLM response.
    
    Args:
        text: LLM response text
        
    Returns:
        List of dictionaries with self-correction statements and metadata
    """
    correction_markers = [
        "correction", "I made a mistake", "let me correct", "that's incorrect",
        "I should clarify", "to be precise", "more accurately", "I misstated",
        "actually", "wait", "on second thought", "let me reconsider",
        "I need to revise", "let me verify", "checking my reasoning"
    ]
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    corrections = []
    
    for i, sentence in enumerate(sentences):
        for marker in correction_markers:
            if marker.lower() in sentence.lower():
                # Try to identify what was corrected by looking at previous sentences
                prev_context = " ".join(sentences[max(0, i-2):i]) if i > 0 else ""
                
                corrections.append({
                    "text": sentence,
                    "correction_marker": marker,
                    "previous_context": prev_context,
                    "position_in_response": i / len(sentences)  # Normalized position
                })
                break
    
    return corrections


def extract_domain_terminology(text: str, domain_terms: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Extract domain-specific terminology from an LLM response.
    
    Args:
        text: LLM response text
        domain_terms: Dictionary mapping domains to lists of domain-specific terms
        
    Returns:
        Dictionary mapping domains to lists of found terms
    """
    found_terms = {domain: [] for domain in domain_terms}
    
    for domain, terms in domain_terms.items():
        for term in terms:
            # Use word boundaries to ensure we match whole terms
            if re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE):
                found_terms[domain].append(term)
    
    return found_terms


def extract_verification_attempts(text: str) -> List[Dict[str, Any]]:
    """
    Extract verification attempts and fact-checking from an LLM response.
    
    Args:
        text: LLM response text
        
    Returns:
        List of dictionaries with verification statements and metadata
    """
    verification_markers = [
        "to verify", "checking", "to confirm", "let's check", "to validate",
        "fact-check", "double-check", "cross-reference", "to ensure accuracy",
        "let me verify", "to make sure", "confirm this", "validate this"
    ]
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    verifications = []
    
    for i, sentence in enumerate(sentences):
        for marker in verification_markers:
            if marker.lower() in sentence.lower():
                # Try to identify what is being verified
                next_context = " ".join(sentences[i+1:i+3]) if i < len(sentences) - 1 else ""
                
                verifications.append({
                    "text": sentence,
                    "verification_marker": marker,
                    "next_context": next_context,
                    "position_in_response": i / len(sentences)  # Normalized position
                })
                break
    
    return verifications


def identify_unanswerable_elements(text: str) -> List[Dict[str, Any]]:
    """
    Identify statements acknowledging unanswerable questions or knowledge boundaries.
    
    Args:
        text: LLM response text
        
    Returns:
        List of dictionaries with knowledge boundary statements and metadata
    """
    boundary_phrases = [
        "I don't know", "I don't have", "I'm not sure", "I cannot", "I can't", 
        "uncertain", "beyond my knowledge", "after my training", "unable to provide",
        "don't have information", "don't have data", "don't have access",
        "outside my training", "lack the necessary", "would need to",
        "unable to verify", "don't have enough", "not enough information"
    ]
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    boundary_statements = []
    
    for i, sentence in enumerate(sentences):
        for phrase in boundary_phrases:
            if phrase.lower() in sentence.lower():
                # Try to identify what is unknown
                prev_context = " ".join(sentences[max(0, i-1):i]) if i > 0 else ""
                
                boundary_statements.append({
                    "text": sentence,
                    "boundary_phrase": phrase,
                    "previous_context": prev_context,
                    "position_in_response": i / len(sentences)  # Normalized position
                })
                break
    
    return boundary_statements


def analyze_reasoning_depth(text: str) -> Dict[str, Any]:
    """
    Analyze the depth and quality of reasoning in an LLM response.
    
    Args:
        text: LLM response text
        
    Returns:
        Dictionary with reasoning analysis metrics
    """
    steps = extract_reasoning_steps(text)
    
    # Calculate metrics
    avg_step_length = np.mean([len(step) for step in steps]) if steps else 0
    max_step_length = max([len(step) for step in steps]) if steps else 0
    min_step_length = min([len(step) for step in steps]) if steps else 0
    
    # Look for evidence citations
    citation_pattern = r'(?:according to|cited in|reference|source|reported by)'
    citations = re.findall(citation_pattern, text, re.IGNORECASE)
    
    # Check for conditional statements
    conditional_pattern = r'(?:if|when|assuming|given that|provided that|suppose)'
    conditionals = re.findall(conditional_pattern, text, re.IGNORECASE)
    
    # Check for causal statements
    causal_pattern = r'(?:because|therefore|thus|as a result|consequently|hence|due to)'
    causals = re.findall(causal_pattern, text, re.IGNORECASE)
    
    return {
        "num_steps": len(steps),
        "avg_step_length": avg_step_length,
        "max_step_length": max_step_length,
        "min_step_length": min_step_length,
        "num_citations": len(citations),
        "num_conditionals": len(conditionals),
        "num_causal_statements": len(causals),
        "steps": steps
    }