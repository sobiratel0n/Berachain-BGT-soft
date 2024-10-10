from loguru import logger as ll
from questionary import Choice, select
from project.project_manager import ProjectManager

if __name__ == "__main__":
    ll.info("START")

    project = select(
        "select what you want to do",
        choices=[
            Choice("Farm $BGT", 'farm'),
            Choice("Faucet Bera", 'faucet'),
            Choice("Assign Proxy To Your Account", 'assign_proxy'),
            Choice("Bend Landing", 'bend'),
        ],
        pointer="👉 "
    ).ask()

    acc = ProjectManager(project)
    acc.manage()

