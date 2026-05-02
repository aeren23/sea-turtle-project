"""
Task definitions for the SeaTurtle Photo-ID Research Crew.

Each task includes a callback that automatically logs completion to
docs/project_log.md and uses dynamically generated timestamped filenames
so that multiple runs never overwrite previous outputs.
"""

from crewai import Agent, Task
from crewai.tasks.task_output import TaskOutput

from agents.research_crew.config import (
    CV_RESEARCHER_OUTPUT_DIR,
    DATA_RESEARCHER_OUTPUT_DIR,
    DL_STRATEGIST_OUTPUT_DIR,
    ORCHESTRATOR_OUTPUT_DIR,
)
from agents.research_crew.utils.log_writer import append_log, generate_output_filename


def _create_task_callback(agent_name: str, output_dir: str):
    """Creates a closure that logs task completion to project_log.md.

    The callback is triggered automatically by CrewAI when the task finishes.
    It extracts a summary from the task output and appends a structured
    log entry following the project's logging standards.

    Args:
        agent_name: The display name for the log entry author field.
        output_dir: The directory path where the agent saved its output.

    Returns:
        Callable: A callback function accepting a TaskOutput argument.
    """
    def callback(output: TaskOutput) -> None:
        raw_output = output.raw if output.raw else "No output produced"
        # Truncate to keep log entries concise
        max_summary_length = 500
        summary = raw_output[:max_summary_length]
        if len(raw_output) > max_summary_length:
            summary += "..."

        append_log(
            author=agent_name,
            content=f"Task completed successfully. Output summary: {summary}",
            files_affected=str(output_dir),
        )

    return callback


def create_tasks(agents: dict[str, Agent]) -> list[Task]:
    """Creates all research tasks with dynamic filenames and callbacks.

    Each task instructs its assigned agent to save output via FileWriteTool
    to a timestamped file in the agent's dedicated output directory.

    Args:
        agents: Dictionary of agents from create_agents(), keyed by role identifier.

    Returns:
        list[Task]: An ordered list of tasks for the crew to execute.
    """
    # Generate unique timestamped filenames for this run
    dataset_filename = generate_output_filename("dataset_analysis")
    preprocessing_filename = generate_output_filename("preprocessing_strategy")
    model_filename = generate_output_filename("model_strategy")
    final_decision_filename = generate_output_filename("final_decision")

    # Build full relative paths (relative to project root, for FileWriteTool)
    dataset_filepath = f"{DATA_RESEARCHER_OUTPUT_DIR}/{dataset_filename}"
    preprocessing_filepath = f"{CV_RESEARCHER_OUTPUT_DIR}/{preprocessing_filename}"
    model_filepath = f"{DL_STRATEGIST_OUTPUT_DIR}/{model_filename}"
    final_decision_filepath = f"{ORCHESTRATOR_OUTPUT_DIR}/{final_decision_filename}"

    # ----- Task 1: Dataset Research -----
    dataset_research_task = Task(
        description=(
            "Research publicly available sea turtle photo datasets suitable for "
            "Photo-ID (individual identification via post-ocular facial scale patterns). "
            "Investigate sources like Kaggle, GitHub, academic repositories, and WILDBOOK. "
            "For each dataset found, document: name, source URL, size, species covered, "
            "image quality, annotation type, and relevance to facial scale pattern recognition. "
            "Also recommend data augmentation strategies (rotation, color jitter, horizontal flip, "
            "elastic deformation) that preserve the biological validity of scale patterns, "
            "considering the project's constraint of ~600 existing images.\n\n"
            f"You MUST save your complete findings using the FileWriteTool to this exact path: "
            f"{dataset_filepath}"
        ),
        expected_output=(
            "A comprehensive Markdown report containing: "
            "(1) A table of discovered datasets with metadata, "
            "(2) Quality assessment for each dataset, "
            "(3) Recommended augmentation pipeline with justification, "
            "(4) Estimated effective dataset size after augmentation."
        ),
        agent=agents["data_researcher"],
        callback=_create_task_callback(
            "Data Researcher", DATA_RESEARCHER_OUTPUT_DIR
        ),
    )

    # ----- Task 2: Preprocessing Strategy Research -----
    preprocessing_research_task = Task(
        description=(
            "Research and design an OpenCV-based image preprocessing pipeline for "
            "underwater sea turtle photographs. The pipeline must handle:\n"
            "1. **Face Detection & Cropping**: Isolate the turtle's head profile, "
            "discarding body and background.\n"
            "2. **Angle/Perspective Correction**: Use Affine Transformations to align "
            "the face profile to a standard horizontal orientation using eye landmarks.\n"
            "3. **Light & Contrast Optimization**: Apply CLAHE (Contrast Limited Adaptive "
            "Histogram Equalization) to equalize underwater lighting variations.\n"
            "4. **Underwater Color Correction**: Compensate for blue/green color cast "
            "typical of underwater environments.\n"
            "5. **Output Standardization**: Produce 224x224 RGB images suitable for CNN input.\n\n"
            "For each technique, provide: the OpenCV function name, recommended parameters, "
            "and why it is appropriate for this specific use case.\n\n"
            f"You MUST save your complete findings using the FileWriteTool to this exact path: "
            f"{preprocessing_filepath}"
        ),
        expected_output=(
            "A detailed Markdown report containing: "
            "(1) Step-by-step preprocessing pipeline with OpenCV function calls, "
            "(2) Recommended parameter values for each step, "
            "(3) Before/after description for each transformation, "
            "(4) Pipeline execution order rationale."
        ),
        agent=agents["cv_researcher"],
        callback=_create_task_callback(
            "CV Researcher", CV_RESEARCHER_OUTPUT_DIR
        ),
    )

    # ----- Task 3: Model Strategy Research -----
    model_research_task = Task(
        description=(
            "Research and recommend the optimal deep learning architecture and training "
            "strategy for sea turtle Photo-ID with a small dataset (~600 images). "
            "Compare these approaches:\n"
            "1. **Classification CNN** (ResNet-50, EfficientNet-B0): Fine-tuned from ImageNet "
            "for direct individual turtle classification.\n"
            "2. **Metric Learning** (Siamese Network, Triplet Loss): Learning an embedding "
            "space where same-turtle images cluster together.\n"
            "3. **Hybrid Approaches**: Combining classification with embedding-based retrieval.\n\n"
            "For each approach, analyze: architecture details, transfer learning strategy, "
            "loss function, optimizer, expected performance with ~600 images, scalability "
            "when new turtles are added, and computational requirements.\n\n"
            "The model must accept 224x224 RGB inputs (matching the CV Researcher's "
            "preprocessing pipeline output).\n\n"
            f"You MUST save your complete findings using the FileWriteTool to this exact path: "
            f"{model_filepath}"
        ),
        expected_output=(
            "A detailed Markdown report containing: "
            "(1) Comparison table of architectures with pros/cons, "
            "(2) Recommended primary approach with justification, "
            "(3) Transfer learning and fine-tuning strategy, "
            "(4) Training hyperparameters (learning rate, batch size, epochs), "
            "(5) Evaluation metrics (accuracy, precision, recall, F1, mAP)."
        ),
        agent=agents["dl_strategist"],
        callback=_create_task_callback(
            "DL Strategist", DL_STRATEGIST_OUTPUT_DIR
        ),
    )

    # ----- Task 4: Final Decision (Orchestrator) -----
    final_decision_task = Task(
        description=(
            "You are the Research Orchestrator. Synthesize the findings from all three "
            "sub-agents (Data Researcher, CV Researcher, DL Strategist) into a unified "
            "strategic decision document. Your final report must include:\n"
            "1. **Executive Summary**: One-paragraph overview of the recommended approach.\n"
            "2. **Dataset Strategy**: Which datasets to use, augmentation plan, expected "
            "total training size.\n"
            "3. **Preprocessing Pipeline**: The finalized step-by-step pipeline based on "
            "the CV Researcher's findings.\n"
            "4. **Model Architecture**: The chosen model, training strategy, and evaluation plan.\n"
            "5. **Risk Assessment**: Key risks and mitigation strategies.\n"
            "6. **Implementation Roadmap**: Suggested order of implementation with milestones.\n\n"
            "Make concrete decisions — do not just summarize. Choose one primary approach "
            "for each component and justify your choice.\n\n"
            f"You MUST save your final decision document using the FileWriteTool to this exact path: "
            f"{final_decision_filepath}"
        ),
        expected_output=(
            "A comprehensive final decision Markdown document with all 6 sections, "
            "containing concrete recommendations, chosen approaches, and a clear "
            "implementation roadmap for the SeaTurtle Photo-ID project."
        ),
        agent=agents["orchestrator"],
        callback=_create_task_callback(
            "Research Orchestrator", ORCHESTRATOR_OUTPUT_DIR
        ),
    )

    return [
        dataset_research_task,
        preprocessing_research_task,
        model_research_task,
        final_decision_task,
    ]
