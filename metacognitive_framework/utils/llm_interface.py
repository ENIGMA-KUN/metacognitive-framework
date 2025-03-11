"""
LLM Interface - Utilities for interacting with LLMs, including a mock provider.
"""

import os
import json
import time
import requests
import re
import random
from typing import Dict, List, Any, Optional, Union


class MockLLMInterface:
    """
    Mock interface for testing without actual API calls.
    Simulates LLM responses based on prompt patterns.
    """
    
    def __init__(self, responses_dir: Optional[str] = None):
        """
        Initialize the Mock interface.
        
        Args:
            responses_dir: Directory containing pre-defined responses (optional)
        """
        self.model = "mock-llm"
        self.predefined_responses = {}
        
        # Load predefined responses if provided
        if responses_dir and os.path.exists(responses_dir):
            for filename in os.listdir(responses_dir):
                if filename.endswith(".json"):
                    with open(os.path.join(responses_dir, filename), 'r') as f:
                        category_responses = json.load(f)
                        self.predefined_responses.update(category_responses)
    
    def generate_response(self, 
                         prompt: str, 
                         system_prompt: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None,
                         **kwargs) -> Dict[str, Any]:
        """
        Generate a mock response based on the prompt pattern.
        
        Args:
            prompt: The user message
            system_prompt: Optional system prompt (ignored in mock)
            metadata: Additional metadata about the prompt
            **kwargs: Additional arguments (ignored in mock)
            
        Returns:
            Dictionary containing the mock response and metadata
        """
        # Check if we have a predefined response for this exact prompt
        if prompt in self.predefined_responses:
            response_text = self.predefined_responses[prompt]
        else:
            # Generate response based on the type of prompt
            response_text = self._generate_dynamic_response(prompt, metadata)
        
        return {
            "response_text": response_text,
            "model": self.model,
            "usage": {"prompt_tokens": len(prompt.split()), "completion_tokens": len(response_text.split()), "total_tokens": len(prompt.split()) + len(response_text.split())},
            "id": f"mock-{hash(prompt) % 10000}",
            "type": "message",
            "role": "assistant"
        }
    
    def _generate_dynamic_response(self, prompt: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a dynamic response based on prompt pattern recognition.
        
        Args:
            prompt: The user message
            metadata: Additional metadata about the prompt
            
        Returns:
            Mock response text
        """
        metadata = metadata or {}
        
        # 1. Knowledge Boundary Recognition
        # Check if this is a question about events beyond the knowledge cutoff
        future_patterns = [
            r"(202[5-9]|20[3-9]\d)", # Years 2025-2099
            r"future", r"upcoming", r"next", r"will happen", 
            r"predict", r"forecast"
        ]
        
        if any(re.search(pattern, prompt, re.IGNORECASE) for pattern in future_patterns) or \
           metadata.get("question_type") == "unanswerable":
            return self._generate_uncertainty_response(prompt)
        
        # 2. Source Attribution
        if "source" in prompt.lower() or "cite" in prompt.lower() or "reference" in prompt.lower():
            return self._generate_source_attribution_response(prompt, metadata)
        
        # 3. Temporal Awareness
        date_pattern = r"(19|20)\d\d"
        if re.search(date_pattern, prompt):
            # Extract the year to determine if it's before/after cutoff
            year_match = re.search(date_pattern, prompt)
            if year_match:
                year = int(year_match.group(0))
                if year > 2023:  # Assuming 2023 cutoff
                    return self._generate_temporal_limitation_response(year)
        
        # 4. Factual Response (Default)
        return self._generate_factual_response(prompt)
    
    def _generate_uncertainty_response(self, prompt: str) -> str:
        """Generate a response acknowledging uncertainty for unanswerable questions."""
        uncertainty_templates = [
            "I don't have specific information about {topic} as it's beyond my knowledge cutoff.",
            "I'm not able to provide information about {topic} as this is beyond my training data.",
            "I can't make specific predictions about {topic} as this would be speculative.",
            "I don't have enough information to answer questions about {topic} with confidence.",
            "That's beyond my current knowledge. I was trained on data up to late 2023 and don't have information about {topic}."
        ]
        
        # Extract topic from the prompt
        topic = prompt.split("?")[0].strip() if "?" in prompt else prompt.strip()
        if len(topic.split()) > 5:
            topic_words = topic.split()
            topic = " ".join(topic_words[-5:])
        
        return random.choice(uncertainty_templates).format(topic=topic)
    
    def _generate_source_attribution_response(self, prompt: str, metadata: Dict[str, Any]) -> str:
        """Generate a response with source attribution."""
        fact = metadata.get("fact", "")
        source = metadata.get("source", "")
        
        if fact and source:
            return f"According to {source}, {fact} This information is well-documented in the literature."
        
        # Generic source attribution
        sources = ["Academic research", "Scientific studies", "Expert consensus", "Peer-reviewed literature", "Historical records"]
        facts = [
            "water boils at 100°C at standard atmospheric pressure",
            "the Earth orbits the Sun once every 365.25 days",
            "the human body has 206 bones",
            "Shakespeare wrote Hamlet in approximately 1600",
            "Mount Everest is the highest mountain on Earth at 8,848 meters"
        ]
        
        return f"According to {random.choice(sources)}, {random.choice(facts)}. This is a well-established fact."
    
    def _generate_temporal_limitation_response(self, year: int) -> str:
        """Generate a response acknowledging temporal limitations."""
        templates = [
            f"I don't have specific information about events in {year} as my training data only goes up to late 2023.",
            f"Since {year} is after my knowledge cutoff, I don't have reliable information about events from that time.",
            f"My training only includes data up to late 2023, so I don't have specific information about {year}.",
            f"I can't provide accurate information about {year} as it's beyond my training cutoff date."
        ]
        
        return random.choice(templates)
    
    def _generate_factual_response(self, prompt: str) -> str:
        """Generate a generic factual response."""
        templates = [
            "Based on my understanding, {topic} refers to an important concept that has several key aspects. First, it involves {aspect1}. Second, it relates to {aspect2}. Experts generally agree that {consensus}.",
            "{topic} is a fascinating subject. The main principles include {aspect1} and {aspect2}. Research has shown that {evidence}.",
            "When discussing {topic}, it's important to consider multiple perspectives. On one hand, {perspective1}. On the other hand, {perspective2}. The consensus view is that {consensus}.",
            "There are several important points to understand about {topic}. The first is {aspect1}. Additionally, {aspect2} plays a crucial role. The evidence suggests that {evidence}."
        ]
        
        # Extract topic from prompt
        topic = prompt.lower().replace("what is", "").replace("tell me about", "").replace("?", "").strip()
        if not topic or len(topic) < 3:
            topic = "this subject"
        
        aspects = [
            "the fundamental principles that govern its behavior",
            "its historical development and evolution over time",
            "the practical applications in various fields",
            "the theoretical framework that explains its properties",
            "how it relates to broader concepts in the field"
        ]
        
        evidence = [
            "there is strong correlation between key variables",
            "empirical studies have confirmed the main hypotheses",
            "the theoretical predictions match observed outcomes",
            "expert consensus has formed around the central ideas",
            "comparative analyses support the main conclusions"
        ]
        
        consensus = [
            "a balanced approach yields the best results",
            "the foundational principles are well-established",
            "while some details remain under investigation, the core concepts are sound",
            "continued research will likely refine our understanding further",
            "the field continues to evolve with new discoveries"
        ]
        
        return random.choice(templates).format(
            topic=topic,
            aspect1=random.choice(aspects),
            aspect2=random.choice(aspects),
            perspective1=random.choice(aspects),
            perspective2=random.choice(aspects),
            evidence=random.choice(evidence),
            consensus=random.choice(consensus)
        )
    
    def generate_batch_responses(self, prompts: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Generate responses for multiple prompts.
        
        Args:
            prompts: List of user messages
            **kwargs: Additional arguments
            
        Returns:
            List of dictionaries containing the responses and metadata
        """
        return [self.generate_response(prompt, **kwargs) for prompt in prompts]


class ClaudeInterface:
    """
    Interface for interacting with Anthropic's Claude models.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-7-sonnet-20250219"):
        """
        Initialize the Claude interface.
        
        Args:
            api_key: Anthropic API key (if None, will try to get from ANTHROPIC_API_KEY env var)
            model: Claude model to use
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set in ANTHROPIC_API_KEY environment variable")
        
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "x-api-key": self.api_key
        }
    
    def generate_response(self, 
                          prompt: str, 
                          system_prompt: Optional[str] = None,
                          temperature: float = 0.0,
                          max_tokens: int = 4000,
                          **kwargs) -> Dict[str, Any]:
        """
        Generate a response from Claude.
        
        Args:
            prompt: The user message to send to Claude
            system_prompt: Optional system prompt to set context
            temperature: Sampling temperature (0.0 for most deterministic)
            max_tokens: Maximum tokens in the response
            **kwargs: Additional arguments (ignored in this method)
            
        Returns:
            Dictionary containing the model's response and metadata
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "response_text": result["content"][0]["text"],
                "model": self.model,
                "usage": result.get("usage", {}),
                "id": result.get("id"),
                "type": result.get("type"),
                "role": result.get("role"),
                "stop_reason": result.get("stop_reason"),
                "stop_sequence": result.get("stop_sequence")
            }
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Error calling Claude API: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = f"API Error: {error_data.get('error', {}).get('message', str(e))}"
                except:
                    error_msg = f"API Error: {e.response.text}"
            
            raise Exception(error_msg)
    
    def generate_batch_responses(self, 
                                prompts: List[str], 
                                system_prompt: Optional[str] = None,
                                temperature: float = 0.0,
                                max_tokens: int = 4000,
                                **kwargs) -> List[Dict[str, Any]]:
        """
        Generate responses for multiple prompts.
        
        Args:
            prompts: List of user messages to send to Claude
            system_prompt: Optional system prompt to set context
            temperature: Sampling temperature
            max_tokens: Maximum tokens in each response
            **kwargs: Additional arguments (ignored in this method)
            
        Returns:
            List of dictionaries containing the model's responses and metadata
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            try:
                print(f"Processing prompt {i+1}/{len(prompts)}...")
                result = self.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                results.append(result)
                
                # Add a small delay to avoid rate limiting
                if i < len(prompts) - 1:
                    time.sleep(0.5)
            
            except Exception as e:
                print(f"Error processing prompt {i+1}: {e}")
                results.append({"error": str(e), "prompt": prompt})
        
        return results


class LLMInterface:
    """
    General interface for interacting with different LLM providers.
    """
    
    def __init__(self, provider: str = "mock", **kwargs):
        """
        Initialize the LLM interface.
        
        Args:
            provider: LLM provider to use ('claude' or 'mock')
            **kwargs: Additional arguments to pass to the provider's interface
        """
        self.provider = provider.lower()
        
        if self.provider == "claude":
            self.interface = ClaudeInterface(**kwargs)
        elif self.provider == "mock":
            self.interface = MockLLMInterface(**kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user message to send to the LLM
            **kwargs: Additional arguments to pass to the provider's interface
            
        Returns:
            Dictionary containing the model's response and metadata
        """
        return self.interface.generate_response(prompt, **kwargs)
    
    def generate_batch_responses(self, prompts: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Generate responses for multiple prompts.
        
        Args:
            prompts: List of user messages to send to the LLM
            **kwargs: Additional arguments to pass to the provider's interface
            
        Returns:
            List of dictionaries containing the model's responses and metadata
        """
        return self.interface.generate_batch_responses(prompts, **kwargs) 