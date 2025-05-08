def decorate_thought(thought, parent_task):
    return {
        "thought": thought,
        "parent_task": parent_task,
        "round": 0,
        "coherence": "NA",
        "entropy": "NA"
    }
