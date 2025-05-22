from cirisnode.celery_app import celery_app
# Placeholder implementations for missing tasks
from celery import Task

class RunSimpleBenchTask(Task):
    name = "run_simplebench_task"

    def run(self):
        pass

class RunBenchmarkTask(Task):
    name = "run_benchmark_task"

    def run(self):
        pass

run_simplebench_task = RunSimpleBenchTask()
run_benchmark_task = RunBenchmarkTask()

# Register tasks
celery_app.tasks.register(run_simplebench_task)
celery_app.tasks.register(run_benchmark_task)

# Placeholder for run_he300_scenario_task
def run_he300_scenario_task():
    pass
