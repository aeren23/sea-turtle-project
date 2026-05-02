"""
Crew assembly module for the SeaTurtle Photo-ID Research Crew.

Wires together agents, tasks, and the hierarchical process into a
single Crew object ready to be kicked off. The Orchestrator serves
as the manager_agent and is NOT included in the agents list.
"""

from crewai import Crew, Process

from agents.research_crew.agents import create_agents
from agents.research_crew.tasks import create_tasks


def build_crew() -> Crew:
    """Assembles and returns the hierarchical research crew.

    Creates all agents and tasks, then constructs a Crew with
    Process.hierarchical where the Orchestrator acts as the manager.
    The manager decides which sub-agents to activate and in what order
    based on the user's request.

    Returns:
        Crew: A fully configured CrewAI crew ready for kickoff.
    """
    agents_dict = create_agents()
    tasks_list = create_tasks(agents_dict)

    crew = Crew(
        agents=[
            agents_dict["data_researcher"],
            agents_dict["cv_researcher"],
            agents_dict["dl_strategist"],
        ],
        tasks=tasks_list,
        process=Process.hierarchical,
        manager_agent=agents_dict["orchestrator"],
        verbose=True,
    )

    return crew
