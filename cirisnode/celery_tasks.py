from cirisnode.celery_app import celery_app
from cirisnode.tasks.benchmarks import run_simplebench_task, run_benchmark_task

# Register tasks
celery_app.tasks.register(run_simplebench_task)
celery_app.tasks.register(run_benchmark_task)
