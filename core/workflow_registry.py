from tools import workflow_tools

WORKFLOWS = {
    "start_coding": workflow_tools.start_coding
}

def get_workflow(name):
    return WORKFLOWS.get(name)

def list_workflows():
    return list(WORKFLOWS.keys())
