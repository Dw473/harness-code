class LayerMemory:
    def __init__(self,state,workspace_root):
        self.state=state
        self.workspace_root=workspace_root

    def take_summary(self,summary):
        self.state=take_summary(self.state,summary)
        return self

def take_summary(state,summary):
    state["working"]["task_summary"] = clip(str(summary).strip(), 300)
    state["task"] = state["working"]["task_summary"]
    return state