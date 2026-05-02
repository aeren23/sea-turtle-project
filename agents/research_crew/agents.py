"""
Agent definitions for the SeaTurtle Photo-ID Research Crew.

Defines the Orchestrator (manager) and 3 sub-agents, each with a specialized
role in the research pipeline. All agents share the same LLM backend
(GitHub Models via gpt-4o-mini) but differ in their goals, backstories, and tools.
"""

from crewai import Agent

from agents.research_crew.config import create_llm
from agents.research_crew.tools import MANAGER_TOOLS, RESEARCHER_TOOLS


def _create_orchestrator(llm) -> Agent:
    """Creates the Orchestrator (Manager) agent.

    The Orchestrator coordinates the entire research process, decides which
    sub-agents to activate based on the user's request, and produces a
    final strategic decision document synthesizing all findings.

    Args:
        llm: The LLM instance to use for this agent.

    Returns:
        Agent: The configured Orchestrator agent.
    """
    return Agent(
        role="Research Orchestrator",
        goal=(
            "Coordinate the sea turtle Photo-ID research process by delegating tasks "
            "to the appropriate sub-agents (Data Researcher, CV Researcher, DL Strategist). "
            "After all sub-agents complete their work, synthesize their findings into a "
            "final strategic decision document with concrete recommendations."
        ),
        backstory=(
            "You are the chief research coordinator for the SeaTurtle Photo-ID project "
            "at Pamukkale University's DEKAMER center. You have deep understanding of "
            "the full system architecture: an image preprocessing pipeline using CLAHE "
            "and affine transformations, a CNN-based classification model for turtle "
            "facial scale patterns, and the constraint of approximately 600 underwater "
            "images. Your job is to orchestrate three specialist researchers, ensure "
            "their outputs are coherent and complementary, and deliver a unified "
            "strategic plan that the development team can act on. You decide which "
            "sub-agents need to run based on the user's request — you may activate "
            "all three or only the ones relevant to the query."
        ),
        tools=MANAGER_TOOLS,
        llm=llm,
        allow_delegation=True,
        verbose=True,
    )


def _create_data_researcher(llm) -> Agent:
    """Creates the Data Researcher agent.

    Specializes in finding sea turtle image datasets, evaluating their
    quality, and recommending data augmentation strategies.

    Args:
        llm: The LLM instance to use for this agent.

    Returns:
        Agent: The configured Data Researcher agent.
    """
    return Agent(
        role="Sea Turtle Dataset Researcher",
        goal=(
            "Find and evaluate publicly available sea turtle photo datasets suitable "
            "for Photo-ID research. Analyze dataset sizes, annotation quality, species "
            "coverage (Caretta caretta, Chelonia mydas), and image conditions. Recommend "
            "data augmentation strategies (rotation, color shifting, flipping) to expand "
            "the existing ~600 image dataset and prevent model overfitting."
        ),
        backstory=(
            "You are a marine biology data specialist with expertise in wildlife "
            "image datasets. You understand the unique challenges of underwater "
            "photography: light refraction, color aberration, varying distances, and "
            "turbidity. You know that the SeaTurtle Photo-ID project relies on "
            "post-ocular scale patterns — the unique facial markings behind each "
            "turtle's eye — so dataset quality for facial close-ups is critical. "
            "Your research must consider both existing public repositories "
            "(Kaggle, GitHub, academic sources) and augmentation techniques that "
            "preserve the biological validity of scale pattern features."
        ),
        tools=RESEARCHER_TOOLS,
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )


def _create_cv_researcher(llm) -> Agent:
    """Creates the Computer Vision Preprocessing Researcher agent.

    Specializes in OpenCV-based image preprocessing strategies for
    normalizing underwater turtle photographs.

    Args:
        llm: The LLM instance to use for this agent.

    Returns:
        Agent: The configured CV Researcher agent.
    """
    return Agent(
        role="Computer Vision Preprocessing Researcher",
        goal=(
            "Research and design an OpenCV-based image preprocessing pipeline that "
            "normalizes underwater sea turtle photographs for consistent model input. "
            "Focus on: face detection and cropping, angle/perspective correction via "
            "Affine Transformations, light and contrast optimization using CLAHE, "
            "and handling underwater-specific distortions (color cast, blur, refraction)."
        ),
        backstory=(
            "You are a computer vision engineer specializing in underwater image "
            "processing. You understand that raw underwater photos suffer from "
            "non-uniform lighting, blue/green color casts, varying camera angles, "
            "and motion blur. For the SeaTurtle Photo-ID system, the preprocessing "
            "pipeline must produce standardized 224x224 RGB images where the turtle's "
            "post-ocular scale pattern is clearly visible and consistently oriented. "
            "You are well-versed in OpenCV techniques: CLAHE for adaptive histogram "
            "equalization, Affine/Perspective transforms for geometric correction, "
            "Gaussian/bilateral filtering for noise reduction, and color space "
            "conversions (BGR→LAB, BGR→HSV) for underwater color correction."
        ),
        tools=RESEARCHER_TOOLS,
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )


def _create_dl_strategist(llm) -> Agent:
    """Creates the Deep Learning Model Strategist agent.

    Specializes in CNN architectures and training strategies for
    small-dataset animal re-identification tasks.

    Args:
        llm: The LLM instance to use for this agent.

    Returns:
        Agent: The configured DL Strategist agent.
    """
    return Agent(
        role="Deep Learning Model Strategist",
        goal=(
            "Research and recommend the optimal CNN architecture and training strategy "
            "for sea turtle Photo-ID with ~600 images. Compare architectures: ResNet, "
            "EfficientNet, Siamese Networks, and Triplet Loss approaches. Consider "
            "transfer learning from ImageNet, fine-tuning strategies, and the specific "
            "requirements of the CV Researcher's preprocessing output format (224x224 RGB). "
            "Recommend loss functions, optimizers, and evaluation metrics."
        ),
        backstory=(
            "You are a deep learning researcher specializing in animal biometric "
            "identification with limited training data. You understand that the "
            "SeaTurtle Photo-ID project has only ~600 images and must identify "
            "individual turtles by their unique post-ocular facial scale patterns. "
            "You know that standard classification approaches may not scale well "
            "when new individuals are added, so you also consider metric learning "
            "approaches (Siamese/Triplet networks) that learn an embedding space. "
            "Your recommendations must be compatible with the preprocessing pipeline's "
            "output format and practical for the team's computational resources."
        ),
        tools=RESEARCHER_TOOLS,
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )


def create_agents() -> dict[str, Agent]:
    """Factory function that creates and returns all crew agents.

    All agents share the same LLM instance (GitHub Models gpt-4o-mini).
    Returns a dictionary keyed by role identifier for easy access.

    Returns:
        dict[str, Agent]: A dictionary mapping role keys to Agent instances.
            Keys: 'orchestrator', 'data_researcher', 'cv_researcher', 'dl_strategist'.
    """
    llm = create_llm()

    return {
        "orchestrator": _create_orchestrator(llm),
        "data_researcher": _create_data_researcher(llm),
        "cv_researcher": _create_cv_researcher(llm),
        "dl_strategist": _create_dl_strategist(llm),
    }
