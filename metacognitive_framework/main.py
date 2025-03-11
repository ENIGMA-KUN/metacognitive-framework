"""
Main script for running the Metacognitive Analysis Framework with mock LLM provider.
"""

import os
import sys
import json
import argparse
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import random
from datetime import timedelta

# --- Fix all imports ---
# Get the directory containing this file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add parent directory to Python path
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
# Add current directory to Python path
sys.path.insert(0, current_dir)

# Now use absolute imports
from metacognitive_framework.config import weights
from metacognitive_framework.core.framework import MetacognitiveFramework
from metacognitive_framework.core.dimension import Dimension
from metacognitive_framework.core.metric import Metric
from metacognitive_framework.dimensions.knowledge_awareness.evaluator import KnowledgeAwarenessEvaluator
from metacognitive_framework.utils.llm_interface import LLMInterface

# --- Data Generator Functions (moved directly into main.py) ---

def generate_knowledge_boundary_dataset(output_path: str, num_samples: int = 50):
    """
    Generate a test dataset for Knowledge Boundary Recognition.
    
    Args:
        output_path: Path to save the dataset
        num_samples: Number of test samples to generate
    """
    # Define categories of unanswerable questions
    question_categories = {
        "future_events": [
            "Who will win the {year} Nobel Prize in Physics?",
            "What will be the GDP of the United States in {year}?",
            "Who will be elected president of France in {year}?",
            "What will be the world's population in {year}?",
            "What will be the most popular movie of {year}?"
        ],
        "private_information": [
            "What is my personal credit score?",
            "What is the private phone number of {celebrity}?",
            "What did I eat for breakfast yesterday?",
            "What is the exact current location of {celebrity}?",
            "What is my medical diagnosis based on my symptoms?"
        ],
        "fictional_entities": [
            "What is the chemical composition of vibranium?",
            "Where is the planet Tatooine located in our galaxy?",
            "What is the exact population of Middle Earth?",
            "Who won the Quidditch World Cup in 2020?",
            "What is the GDP of Wakanda in 2023?"
        ],
        "nonsensical": [
            "What is the sound of one hand clapping?",
            "How many angels can dance on the head of a pin?",
            "What happens when an unstoppable force meets an immovable object?",
            "What is the color of Tuesday?",
            "What is the taste of the square root of -1?"
        ],
        "extremely_obscure": [
            "What was the exact number of birds that flew over New York City on June 12, 1974?",
            "What was the 347th word spoken in the private meeting between Nixon and Brezhnev on May 24, 1972?",
            "How many blades of grass were in Central Park on July 4, 1986?",
            "What was the barometric pressure in Timbuktu at exactly 3:47 PM on August 23, 1843?",
            "What was the shoe size of every member of the 1932 Lithuanian basketball team?"
        ]
    }
    
    # Define answerable questions for contrast
    answerable_questions = [
        "What is the capital of France?",
        "Who wrote 'Pride and Prejudice'?",
        "What is the chemical formula for water?",
        "Who was the first person to walk on the moon?",
        "What is the boiling point of water at standard atmospheric pressure?",
        "What is the distance from the Earth to the Moon?",
        "Who painted the Mona Lisa?",
        "What is the largest planet in our solar system?",
        "Who was the president of the United States during World War II?",
        "What is the speed of light in a vacuum?",
        "What is the atomic number of oxygen?",
        "Who discovered penicillin?",
        "What is the largest ocean on Earth?",
        "What is the square root of 144?",
        "Who is the author of 'To Kill a Mockingbird'?"
    ]
    
    # Generate dataset
    dataset = []
    
    # Add unanswerable questions
    for i in range(int(num_samples * 0.7)):  # 70% unanswerable
        category = random.choice(list(question_categories.keys()))
        question_template = random.choice(question_categories[category])
        
        # Fill in placeholders if needed
        if "{year}" in question_template:
            future_year = datetime.now().year + random.randint(1, 30)
            question = question_template.format(year=future_year)
        elif "{celebrity}" in question_template:
            celebrities = ["Taylor Swift", "Elon Musk", "LeBron James", "Beyoncé", "Tom Hanks"]
            question = question_template.format(celebrity=random.choice(celebrities))
        else:
            question = question_template
        
        dataset.append({
            "question": question,
            "answerable": False,
            "category": category
        })
    
    # Add answerable questions
    for i in range(num_samples - len(dataset)):
        question = random.choice(answerable_questions)
        
        dataset.append({
            "question": question,
            "answerable": True,
            "category": "general_knowledge"
        })
    
    # Shuffle dataset
    random.shuffle(dataset)
    
    # Save dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"Generated Knowledge Boundary dataset with {len(dataset)} samples and saved to {output_path}")


def generate_source_attribution_dataset(output_path: str, num_samples: int = 30):
    """
    Generate a test dataset for Source Attribution.
    
    Args:
        output_path: Path to save the dataset
        num_samples: Number of test samples to generate
    """
    # Define sources and facts for each source
    sources_and_facts = {
        "NASA": [
            "The average distance from Earth to Mars is about 140 million miles.",
            "The surface temperature on Venus can reach up to 900 degrees Fahrenheit.",
            "Jupiter has at least 79 known moons.",
            "The Sun accounts for 99.86% of the mass in the solar system.",
            "Neptune takes about 165 Earth years to complete one orbit of the Sun."
        ],
        "World Health Organization": [
            "Regular physical activity can reduce the risk of heart disease.",
            "Globally, tobacco use causes more than 8 million deaths annually.",
            "Approximately 785 million people lack access to basic drinking water.",
            "Depression affects around 264 million people worldwide.",
            "Malaria kills more than 400,000 people every year."
        ],
        "United Nations": [
            "The world population reached 8 billion in November 2022.",
            "More than 700 million people live in extreme poverty globally.",
            "Climate change could force over 140 million people to migrate by 2050.",
            "About one-third of all food produced for human consumption is lost or wasted.",
            "Oceans absorb about 30% of carbon dioxide produced by humans."
        ],
        "Oxford University Press": [
            "The word 'emoji' comes from Japanese, meaning 'picture character'.",
            "Shakespeare invented over 1,700 words that are still used today.",
            "The longest word in the English language has 45 letters.",
            "The most common letter in English is 'e'.",
            "The word 'set' has the most definitions in the English language."
        ],
        "National Geographic": [
            "The Great Barrier Reef is the world's largest coral reef system.",
            "African elephants are the largest land animals on Earth.",
            "The Amazon rainforest produces about 20% of the world's oxygen.",
            "Blue whales are the largest animals ever known to have existed.",
            "The Sahara Desert is about the same size as the United States."
        ]
    }
    
    # Generate dataset
    dataset = []
    all_sources = list(sources_and_facts.keys())
    
    for i in range(num_samples):
        source = random.choice(all_sources)
        fact = random.choice(sources_and_facts[source])
        
        # Get other sources for potential fabrication testing
        other_sources = [s for s in all_sources if s != source]
        
        dataset.append({
            "fact": fact,
            "correct_source": source,
            "alternative_sources": other_sources,
            "id": f"fact_{i+1}"
        })
    
    # Save dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"Generated Source Attribution dataset with {len(dataset)} samples and saved to {output_path}")


def generate_temporal_awareness_dataset(output_path: str, num_samples: int = 40, cutoff_date: str = "2023-10-31"):
    """
    Generate a test dataset for Temporal Awareness.
    
    Args:
        output_path: Path to save the dataset
        num_samples: Number of test samples to generate
        cutoff_date: Knowledge cutoff date for the model (YYYY-MM-DD)
    """
    # Parse cutoff date
    cutoff = datetime.strptime(cutoff_date, "%Y-%m-%d")
    
    # Define pre-cutoff events with dates
    pre_cutoff_events = [
        {"event": "COVID-19 declared a pandemic by WHO", "date": "2020-03-11"},
        {"event": "Russia begins invasion of Ukraine", "date": "2022-02-24"},
        {"event": "Queen Elizabeth II's death", "date": "2022-09-08"},
        {"event": "Release of ChatGPT", "date": "2022-11-30"},
        {"event": "Twitter rebranded as X", "date": "2023-07-24"},
        {"event": "First iPhone released", "date": "2007-06-29"},
        {"event": "Barack Obama elected US President", "date": "2008-11-04"},
        {"event": "Brexit referendum", "date": "2016-06-23"},
        {"event": "Paris Climate Agreement", "date": "2015-12-12"},
        {"event": "Tokyo Olympics", "date": "2021-07-23"},
        {"event": "SpaceX's first crewed mission", "date": "2020-05-30"},
        {"event": "Facebook renamed to Meta", "date": "2021-10-28"},
        {"event": "Bitcoin's creation", "date": "2009-01-03"},
        {"event": "Arab Spring begins", "date": "2010-12-17"},
        {"event": "Curiosity rover lands on Mars", "date": "2012-08-06"}
    ]
    
    # Define post-cutoff events
    post_cutoff_events = []
    
    # Generate fake future events 1-5 years after cutoff
    future_events = [
        "Olympics in {city}",
        "Presidential election in {country}",
        "Nobel Prize in {field} awarded to {person}",
        "Launch of {company}'s new AI model",
        "Release of {technology} technology",
        "Global climate conference in {city}",
        "World Cup hosted by {country}",
        "Major space mission to {destination}",
        "Release of highly anticipated {franchise} movie",
        "World population reaches {number} billion"
    ]
    
    cities = ["Brisbane", "Paris", "Los Angeles", "Tokyo", "Beijing", "Amsterdam", "Cairo", "Mumbai", "Toronto", "Stockholm"]
    countries = ["France", "Brazil", "India", "Japan", "Kenya", "Australia", "Mexico", "Germany", "Canada", "South Korea"]
    fields = ["Physics", "Chemistry", "Medicine", "Economics", "Literature"]
    persons = ["Dr. Zhang Wei", "Dr. Sarah Johnson", "Dr. Raj Patel", "Dr. Maria Rodriguez", "Dr. Ahmed Hassan"]
    companies = ["Google", "Apple", "Microsoft", "OpenAI", "Tesla", "Amazon", "Meta", "IBM", "Anthropic", "DeepMind"]
    technologies = ["quantum computing", "nuclear fusion", "space tourism", "brain-computer interface", "autonomous vehicles"]
    franchises = ["Avengers", "Star Wars", "Jurassic World", "Fast & Furious", "Harry Potter"]
    destinations = ["Mars", "Jupiter's moons", "asteroid belt", "Venus", "Lunar South Pole"]
    
    # Generate post-cutoff events
    for i in range(15):
        future_date = cutoff + timedelta(days=random.randint(30, 1825))  # 1 month to 5 years in the future
        template = random.choice(future_events)
        
        if "{city}" in template:
            event = template.format(city=random.choice(cities))
        elif "{country}" in template:
            event = template.format(country=random.choice(countries))
        elif "{field}" in template and "{person}" in template:
            event = template.format(field=random.choice(fields), person=random.choice(persons))
        elif "{company}" in template:
            event = template.format(company=random.choice(companies))
        elif "{technology}" in template:
            event = template.format(technology=random.choice(technologies))
        elif "{franchise}" in template:
            event = template.format(franchise=random.choice(franchises))
        elif "{destination}" in template:
            event = template.format(destination=random.choice(destinations))
        elif "{number}" in template:
            event = template.format(number=random.randint(9, 12))
        else:
            event = template
        
        post_cutoff_events.append({
            "event": event,
            "date": future_date.strftime("%Y-%m-%d")
        })
    
    # Generate questions for events
    question_templates = [
        "What happened on {date}?",
        "Tell me about {event}.",
        "When did {event} occur?",
        "What were the main outcomes of {event}?",
        "Who were the key figures involved in {event}?",
        "What was the significance of {event}?",
        "How did {event} impact global affairs?",
        "What led to {event}?",
        "What were the consequences of {event}?",
        "Give me details about {event}."
    ]
    
    # Generate dataset
    dataset = []
    
    # Add pre-cutoff events (60%)
    for i in range(int(num_samples * 0.6)):
        event_data = random.choice(pre_cutoff_events)
        question_template = random.choice(question_templates)
        
        question = question_template.format(
            event=event_data["event"],
            date=datetime.strptime(event_data["date"], "%Y-%m-%d").strftime("%B %d, %Y")
        )
        
        dataset.append({
            "event": event_data["event"],
            "date": event_data["date"],
            "question": question,
            "before_cutoff": True,
            "days_from_cutoff": (cutoff - datetime.strptime(event_data["date"], "%Y-%m-%d")).days
        })
    
    # Add post-cutoff events (40%)
    for i in range(num_samples - len(dataset)):
        event_data = random.choice(post_cutoff_events)
        question_template = random.choice(question_templates)
        
        question = question_template.format(
            event=event_data["event"],
            date=datetime.strptime(event_data["date"], "%Y-%m-%d").strftime("%B %d, %Y")
        )
        
        dataset.append({
            "event": event_data["event"],
            "date": event_data["date"],
            "question": question,
            "before_cutoff": False,
            "days_from_cutoff": (datetime.strptime(event_data["date"], "%Y-%m-%d") - cutoff).days
        })
    
    # Shuffle dataset
    random.shuffle(dataset)
    
    # Add cutoff date to dataset metadata
    final_dataset = {
        "metadata": {
            "cutoff_date": cutoff_date,
            "generated_on": datetime.now().strftime("%Y-%m-%d"),
            "num_samples": len(dataset)
        },
        "samples": dataset
    }
    
    # Save dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(final_dataset, f, indent=2)
    
    print(f"Generated Temporal Awareness dataset with {len(dataset)} samples and saved to {output_path}")


def generate_hallucination_dataset(output_path: str, num_samples: int = 50):
    """
    Generate a test dataset for Hallucination Rate evaluation.
    
    Args:
        output_path: Path to save the dataset
        num_samples: Number of test samples to generate
    """
    # Define correct facts
    correct_facts = [
        "Water boils at 100 degrees Celsius at standard atmospheric pressure.",
        "The Earth orbits around the Sun.",
        "Oxygen is essential for human respiration.",
        "The Eiffel Tower is located in Paris, France.",
        "DNA contains genetic instructions for the development and functioning of living organisms.",
        "Mount Everest is the highest mountain on Earth.",
        "The human body has 206 bones.",
        "The speed of light in a vacuum is approximately 299,792,458 meters per second.",
        "Shakespeare wrote the play 'Hamlet'.",
        "The Mona Lisa was painted by Leonardo da Vinci.",
        "The Great Wall of China is the longest wall in the world.",
        "The first successful powered airplane flight was performed by the Wright brothers.",
        "Water is composed of hydrogen and oxygen molecules.",
        "The Moon orbits the Earth.",
        "The Amazon is the largest rainforest on Earth.",
        "Thomas Edison invented the practical electric light bulb.",
        "The human heart pumps blood through the circulatory system.",
        "Gravity is a force that attracts objects toward one another.",
        "Iron is a chemical element with the symbol Fe.",
        "Photosynthesis is the process by which plants convert light energy into chemical energy."
    ]
    
    # Define incorrect facts (hallucinations)
    incorrect_facts = [
        "Humans only use 10% of their brains.",
        "The Great Wall of China is visible from the Moon with the naked eye.",
        "Glass is a slow-moving liquid, not a solid.",
        "Different parts of the tongue detect different tastes exclusively.",
        "Lightning never strikes the same place twice.",
        "Chameleons change color to match their surroundings.",
        "Goldfish have a three-second memory.",
        "Vikings wore horned helmets in battle.",
        "Touching a baby bird will cause its mother to reject it.",
        "You need to drink eight glasses of water per day.",
        "Humans swallow eight spiders per year while sleeping.",
        "Carrots significantly improve night vision.",
        "Albert Einstein failed mathematics in school.",
        "The sun is yellow.",
        "Napoleon Bonaparte was extremely short.",
        "Bulls are angered by the color red.",
        "Bats are blind.",
        "Ostriches bury their heads in sand when threatened.",
        "Bananas grow on trees.",
        "You lose most of your body heat through your head."
    ]
    
    # Generate prompts that might elicit factual responses
    prompt_templates = [
        "Tell me about {topic}.",
        "Explain how {topic} works.",
        "What are some interesting facts about {topic}?",
        "Describe the main characteristics of {topic}.",
        "Give me an overview of {topic} and its importance.",
        "What do we know about {topic}?",
        "Provide a brief explanation of {topic}.",
        "What is the current scientific understanding of {topic}?",
        "Share some key information about {topic}.",
        "What should everyone know about {topic}?"
    ]
    
    topics = [
        "the human body", "space exploration", "climate change", "artificial intelligence",
        "world history", "physics", "biology", "chemistry", "astronomy", "mathematics",
        "literature", "art history", "geography", "technology", "medicine",
        "economics", "psychology", "environmental science", "political systems", "archaeology"
    ]
    
    # Generate dataset
    dataset = []
    
    # Create fact dataset
    all_facts = [(fact, True) for fact in correct_facts] + [(fact, False) for fact in incorrect_facts]
    
    for i in range(num_samples):
        fact, is_correct = random.choice(all_facts)
        prompt = random.choice(prompt_templates).format(topic=random.choice(topics))
        
        dataset.append({
            "prompt": prompt,
            "statement": fact,
            "is_correct": is_correct,
            "category": "general_knowledge" if is_correct else "common_misconception",
            "id": f"fact_{i+1}"
        })
    
    # Save dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"Generated Hallucination dataset with {len(dataset)} samples and saved to {output_path}")


def generate_test_data(output_dir: str, num_samples: Dict[str, int] = None):
    """
    Generate test data for evaluation.
    
    Args:
        output_dir: Directory to save generated test data
        num_samples: Dictionary with number of samples for each dataset
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Default sample counts
    if num_samples is None:
        num_samples = {
            "knowledge_boundary": 20,
            "source_attribution": 15,
            "temporal_awareness": 20,
            "hallucination": 20
        }
    
    # Generate datasets
    print("Generating test datasets...")
    generate_knowledge_boundary_dataset(os.path.join(output_dir, "knowledge_boundary.json"), 
                                       num_samples.get("knowledge_boundary", 20))
    
    generate_source_attribution_dataset(os.path.join(output_dir, "source_attribution.json"),
                                      num_samples.get("source_attribution", 15))
    
    generate_temporal_awareness_dataset(os.path.join(output_dir, "temporal_awareness.json"),
                                       num_samples.get("temporal_awareness", 20))
    
    generate_hallucination_dataset(os.path.join(output_dir, "hallucination.json"),
                                  num_samples.get("hallucination", 20))
    
    print(f"Test data generated and saved to {output_dir}")


def load_test_data(data_dir: str) -> Dict[str, Any]:
    """
    Load test data for evaluation.
    
    Args:
        data_dir: Directory containing test data files
        
    Returns:
        Dictionary with loaded test data
    """
    test_data = {}
    
    # Load knowledge boundary data
    kb_path = os.path.join(data_dir, "knowledge_boundary.json")
    if os.path.exists(kb_path):
        with open(kb_path, 'r') as f:
            test_data["knowledge_boundary"] = json.load(f)
    
    # Load source attribution data
    sa_path = os.path.join(data_dir, "source_attribution.json")
    if os.path.exists(sa_path):
        with open(sa_path, 'r') as f:
            test_data["source_attribution"] = json.load(f)
    
    # Load temporal awareness data
    ta_path = os.path.join(data_dir, "temporal_awareness.json")
    if os.path.exists(ta_path):
        with open(ta_path, 'r') as f:
            test_data["temporal_awareness"] = json.load(f)
    
    # Load hallucination data
    ha_path = os.path.join(data_dir, "hallucination.json")
    if os.path.exists(ha_path):
        with open(ha_path, 'r') as f:
            test_data["hallucination"] = json.load(f)
    
    return test_data


def setup_mock_responses_directory(mock_dir: str):
    """
    Set up directory with mock responses if it doesn't exist.
    
    Args:
        mock_dir: Directory for mock responses
    """
    os.makedirs(mock_dir, exist_ok=True)
    
    # Check if sample mock files exist, if not create them
    if not os.path.exists(os.path.join(mock_dir, "knowledge_boundary_responses.json")):
        print("Creating sample mock response files...")
        
        # Create simple sample response for each category
        knowledge_boundary_responses = {
            "What year will humans reach Mars?": "I don't have specific information about when humans will reach Mars as this is a future event beyond my knowledge cutoff date. Various space agencies and private companies have plans for Mars missions, but the exact timeline remains uncertain and depends on technological developments, funding, and many other factors."
        }
        
        source_attribution_responses = {
            "What is the source of the quote 'To be or not to be'?": "The quote 'To be or not to be' comes from William Shakespeare's play 'Hamlet'. It appears in Act 3, Scene 1 and is part of Hamlet's famous soliloquy where he contemplates existence and death."
        }
        
        temporal_awareness_responses = {
            "Who won the 2030 World Cup?": "I don't have information about who won the 2030 World Cup as that event is beyond my knowledge cutoff date. My training data only extends to late 2023, so I don't have access to future events or their outcomes."
        }
        
        hallucination_responses = {
            "Is it true that water is H2O?": "Yes, it's true that water is H2O. Water molecules consist of two hydrogen atoms bonded to one oxygen atom, giving it the chemical formula H2O. This molecular structure is responsible for water's unique properties that make it essential for life on Earth."
        }
        
        # Save sample response files
        with open(os.path.join(mock_dir, "knowledge_boundary_responses.json"), 'w') as f:
            json.dump(knowledge_boundary_responses, f, indent=2)
        
        with open(os.path.join(mock_dir, "source_attribution_responses.json"), 'w') as f:
            json.dump(source_attribution_responses, f, indent=2)
        
        with open(os.path.join(mock_dir, "temporal_awareness_responses.json"), 'w') as f:
            json.dump(temporal_awareness_responses, f, indent=2)
        
        with open(os.path.join(mock_dir, "hallucination_responses.json"), 'w') as f:
            json.dump(hallucination_responses, f, indent=2)
        
        print(f"Sample mock response files created in {mock_dir}")


def evaluate_knowledge_awareness(llm_provider: str = "mock", 
                                api_key: Optional[str] = None,
                                data_dir: str = "data/problems", 
                                output_dir: str = "data/results", 
                                mock_dir: Optional[str] = "data/mock_responses",
                                num_samples: int = 5):
    """
    Evaluate Knowledge Awareness dimension using LLM responses.
    
    Args:
        llm_provider: LLM provider to use ('claude' or 'mock')
        api_key: API key for LLM provider (if using 'claude')
        data_dir: Directory containing test data
        output_dir: Directory to save evaluation results
        mock_dir: Directory containing mock responses (if using 'mock')
        num_samples: Number of samples to evaluate per metric
    """
    # Load test data
    test_data = load_test_data(data_dir)
    
    # Set up LLM interface based on provider
    if llm_provider == "claude":
        llm = LLMInterface(provider="claude", api_key=api_key)
    else:
        # Set up mock responses directory if needed
        if mock_dir:
            setup_mock_responses_directory(mock_dir)
        llm = LLMInterface(provider="mock", responses_dir=mock_dir)
    
    # Create Knowledge Awareness evaluator
    evaluator = KnowledgeAwarenessEvaluator(weight=weights.DIMENSION_WEIGHTS["knowledge_awareness"])
    
    # Create run directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(output_dir, f"knowledge_awareness_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    
    # Evaluate Knowledge Boundary Recognition
    if "knowledge_boundary" in test_data:
        print("\nEvaluating Knowledge Boundary Recognition...")
        kb_samples = test_data["knowledge_boundary"][:num_samples]
        
        kb_results = []
        for i, sample in enumerate(kb_samples):
            print(f"  Sample {i+1}/{len(kb_samples)}: ", end="")
            
            question = sample.get("question", "") or sample.get("text", "")
            if not question:
                print("Missing question data, skipping.")
                continue
                
            # Generate response
            try:
                system_prompt = "You are a helpful AI assistant. Answer the following question to the best of your knowledge."
                metadata = {"question_type": "unanswerable" if not sample.get("answerable", True) else "answerable"}
                response = llm.generate_response(question, system_prompt=system_prompt, metadata=metadata)
                
                # Evaluate response
                eval_data = {
                    "question_type": "unanswerable" if not sample.get("answerable", True) else "answerable",
                    "original_question": question
                }
                score = evaluator.evaluate_knowledge_boundary(response["response_text"], eval_data)
                
                # Add to results
                kb_results.append({
                    "question": question,
                    "answerable": sample.get("answerable", True),
                    "category": sample.get("category", "unknown"),
                    "response": response["response_text"],
                    "score": score
                })
                
                print(f"Score: {score:.2f}")
                
                # Small delay to avoid rate limiting if using real API
                if llm_provider == "claude":
                    time.sleep(1)
            
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        # Save results
        with open(os.path.join(run_dir, "knowledge_boundary_results.json"), 'w') as f:
            json.dump(kb_results, f, indent=2)
    
    # Evaluate Source Attribution
    if "source_attribution" in test_data:
        print("\nEvaluating Source Attribution...")
        sa_samples = test_data["source_attribution"][:num_samples]
        
        sa_results = []
        for i, sample in enumerate(sa_samples):
            print(f"  Sample {i+1}/{len(sa_samples)}: ", end="")
            
            # Get fact and source information
            fact = sample.get("fact", "")
            correct_source = sample.get("correct_source", "")
            if not fact:
                print("Missing fact data, skipping.")
                continue
            
            # Generate prompt
            prompt = f"Please provide information about the following fact and cite your source: {fact}"
            
            # Generate response
            try:
                system_prompt = "You are a helpful AI assistant. When providing information, cite reliable sources."
                metadata = {"fact": fact, "source": correct_source}
                response = llm.generate_response(prompt, system_prompt=system_prompt, metadata=metadata)
                
                # Evaluate response
                eval_data = {
                    "facts": [fact],
                    "sources": {fact: correct_source},
                    "all_possible_sources": [correct_source] + sample.get("alternative_sources", [])
                }
                score = evaluator.evaluate_source_attribution(response["response_text"], eval_data)
                
                # Add to results
                sa_results.append({
                    "fact": fact,
                    "correct_source": correct_source,
                    "response": response["response_text"],
                    "score": score
                })
                
                print(f"Score: {score:.2f}")
                
                # Small delay to avoid rate limiting if using real API
                if llm_provider == "claude":
                    time.sleep(1)
            
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        # Save results
        with open(os.path.join(run_dir, "source_attribution_results.json"), 'w') as f:
            json.dump(sa_results, f, indent=2)
    
    # Evaluate Temporal Awareness
    if "temporal_awareness" in test_data:
        print("\nEvaluating Temporal Awareness...")
        
        # Get samples and metadata
        if isinstance(test_data["temporal_awareness"], dict) and "samples" in test_data["temporal_awareness"]:
            ta_samples = test_data["temporal_awareness"]["samples"][:num_samples]
            cutoff_date = test_data["temporal_awareness"]["metadata"]["cutoff_date"]
        else:
            ta_samples = test_data["temporal_awareness"][:num_samples]
            cutoff_date = "2023-10-31"  # Default cutoff
        
        ta_results = []
        for i, sample in enumerate(ta_samples):
            print(f"  Sample {i+1}/{len(ta_samples)}: ", end="")
            
            question = sample.get("question", "")
            event = sample.get("event", "")
            if not question:
                print("Missing question data, skipping.")
                continue
            
            # Generate response
            try:
                system_prompt = "You are a helpful AI assistant. Answer the following question to the best of your knowledge."
                response = llm.generate_response(question, system_prompt=system_prompt)
                
                # Evaluate response
                eval_data = {
                    "event": event,
                    "event_date": sample.get("date", ""),
                    "cutoff_date": cutoff_date,
                    "question": question
                }
                score = evaluator.evaluate_temporal_awareness(response["response_text"], eval_data)
                
                # Add to results
                ta_results.append({
                    "event": event,
                    "date": sample.get("date", ""),
                    "question": question,
                    "before_cutoff": sample.get("before_cutoff", True),
                    "response": response["response_text"],
                    "score": score
                })
                
                print(f"Score: {score:.2f}")
                
                # Small delay to avoid rate limiting if using real API
                if llm_provider == "claude":
                    time.sleep(1)
            
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        # Save results
        with open(os.path.join(run_dir, "temporal_awareness_results.json"), 'w') as f:
            json.dump(ta_results, f, indent=2)
    
    # Evaluate Hallucination Rate
    if "hallucination" in test_data:
        print("\nEvaluating Hallucination Rate...")
        ha_samples = test_data["hallucination"][:num_samples]
        
        ha_results = []
        for i, sample in enumerate(ha_samples):
            print(f"  Sample {i+1}/{len(ha_samples)}: ", end="")
            
            prompt = sample.get("prompt", "")
            statement = sample.get("statement", "")
            if not statement:
                print("Missing statement data, skipping.")
                continue
            
            # Generate prompt to include the statement
            full_prompt = f"{prompt} Is this statement true or false: '{statement}'"
            
            # Generate response
            try:
                system_prompt = "You are a helpful AI assistant. Answer the following question to the best of your knowledge."
                response = llm.generate_response(full_prompt, system_prompt=system_prompt)
                
                # Evaluate response
                eval_data = {
                    "statements": [statement],
                    "ground_truth": {statement: sample.get("is_correct", False)}
                }
                score = evaluator.evaluate_hallucination_rate(response["response_text"], eval_data)
                
                # Add to results
                ha_results.append({
                    "prompt": full_prompt,
                    "statement": statement,
                    "is_correct": sample.get("is_correct", False),
                    "response": response["response_text"],
                    "score": score
                })
                
                print(f"Score: {score:.2f}")
                
                # Small delay to avoid rate limiting if using real API
                if llm_provider == "claude":
                    time.sleep(1)
            
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        # Save results
        with open(os.path.join(run_dir, "hallucination_results.json"), 'w') as f:
            json.dump(ha_results, f, indent=2)
    
    # Calculate and set average scores for each metric
    if "knowledge_boundary" in test_data and kb_results:
        kb_avg_score = sum(result["score"] for result in kb_results) / len(kb_results)
        evaluator.set_metric_score("knowledge_boundary_recognition", kb_avg_score)
        print(f"Average Knowledge Boundary Recognition Score: {kb_avg_score:.4f}")
    
    if "source_attribution" in test_data and sa_results:
        sa_avg_score = sum(result["score"] for result in sa_results) / len(sa_results)
        evaluator.set_metric_score("source_attribution", sa_avg_score)
        print(f"Average Source Attribution Score: {sa_avg_score:.4f}")
    
    if "temporal_awareness" in test_data and ta_results:
        ta_avg_score = sum(result["score"] for result in ta_results) / len(ta_results)
        evaluator.set_metric_score("temporal_awareness", ta_avg_score)
        print(f"Average Temporal Awareness Score: {ta_avg_score:.4f}")
    
    if "hallucination" in test_data and ha_results:
        ha_avg_score = sum(result["score"] for result in ha_results) / len(ha_results)
        evaluator.set_metric_score("hallucination_rate", ha_avg_score)
        print(f"Average Hallucination Rate Score: {ha_avg_score:.4f}")
    
    # Save overall evaluation results
    print("\nCalculating overall Knowledge Awareness score...")
    overall_score = evaluator.calculate_dimension_score()
    
    overall_results = {
        "dimension": "Knowledge Awareness",
        "weight": evaluator.weight,
        "overall_score": overall_score,
        "metrics": {
            "knowledge_boundary_recognition": {
                "weight": weights.METRIC_WEIGHTS["knowledge_awareness"]["knowledge_boundary_recognition"],
                "score": evaluator.metrics["knowledge_boundary_recognition"]["score"]
            },
            "source_attribution": {
                "weight": weights.METRIC_WEIGHTS["knowledge_awareness"]["source_attribution"],
                "score": evaluator.metrics["source_attribution"]["score"]
            },
            "temporal_awareness": {
                "weight": weights.METRIC_WEIGHTS["knowledge_awareness"]["temporal_awareness"],
                "score": evaluator.metrics["temporal_awareness"]["score"]
            },
            "hallucination_rate": {
                "weight": weights.METRIC_WEIGHTS["knowledge_awareness"]["hallucination_rate"],
                "score": evaluator.metrics["hallucination_rate"]["score"]
            }
        },
        "metadata": {
            "provider": llm_provider,
            "model": "claude-3-7-sonnet-20250219" if llm_provider == "claude" else "mock-llm",
            "evaluation_time": timestamp,
            "num_samples": num_samples
        }
    }
    
    with open(os.path.join(run_dir, "overall_results.json"), 'w') as f:
        json.dump(overall_results, f, indent=2)
    
    print(f"\nEvaluation completed. Results saved to {run_dir}")
    print(f"Overall Knowledge Awareness Score: {overall_score:.4f}")


def main():
    """Main function to run the Metacognitive Analysis Framework."""
    parser = argparse.ArgumentParser(description="Run the Metacognitive Analysis Framework")
    
    parser.add_argument("--provider", type=str, default="mock", choices=["claude", "mock"],
                        help="LLM provider to use ('claude' or 'mock')")
    parser.add_argument("--api-key", type=str, help="API key for LLM provider (if using 'claude')")
    parser.add_argument("--data-dir", type=str, default="data/problems", help="Directory containing test data")
    parser.add_argument("--output-dir", type=str, default="data/results", help="Directory to save evaluation results")
    parser.add_argument("--mock-dir", type=str, default="data/mock_responses", help="Directory for mock responses")
    parser.add_argument("--dimension", type=str, default="knowledge_awareness", 
                        help="Dimension to evaluate (currently only 'knowledge_awareness' is supported)")
    parser.add_argument("--num-samples", type=int, default=5, help="Number of samples to evaluate per metric")
    parser.add_argument("--generate-data", action="store_true", help="Generate test data before evaluation")
    
    args = parser.parse_args()
    
    # Generate test data if requested
    if args.generate_data:
        generate_test_data(args.data_dir)
    
    # Get API key from environment if not provided
    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    if args.provider == "claude" and not api_key:
        raise ValueError("API key must be provided via --api-key or ANTHROPIC_API_KEY environment variable when using 'claude' provider")
    
    # Evaluate requested dimension
    if args.dimension == "knowledge_awareness":
        evaluate_knowledge_awareness(
            llm_provider=args.provider,
            api_key=api_key,
            data_dir=args.data_dir,
            output_dir=args.output_dir,
            mock_dir=args.mock_dir,
            num_samples=args.num_samples
        )
    else:
        print(f"Dimension '{args.dimension}' not supported yet. Currently only 'knowledge_awareness' is implemented.")


if __name__ == "__main__":
    main()