from typing import List
import concurrent.futures

from repenseai.genai.tasks.base import BaseTask
from repenseai.utils.logs import logger


class ParallelTask(BaseTask):
    """
    A Workflow step that executes multiple tasks in parallel.
    
    It initializes with a list of tasks and executes all of them in parallel
    using a thread pool. Results from all tasks are merged into a single
    dictionary and returned.
    
    This implementation doesn't use async functions and relies on
    concurrent.futures for parallel execution.
    """
    
    def __init__(
            self, 
            tasks: BaseTask | List[BaseTask], 
        ):
        """
        Initialize the ParallelTask with a list of tasks.
        
        Args:
            tasks: List of BaseTask objects to execute in parallel
        """
        self.tasks = tasks
        
    def _execute_task(self, task, context):
        """Helper method to execute a single task with the given context."""
        return task.run(context.copy() if context else {})
    
    def run(self, context: List[dict] | dict | None = None):
        """
        Execute all tasks in parallel and merge their results.
        
        Args:
            context: Dictionary containing data for task execution
            
        Returns:
            If merge_strategy is 'update': A merged dictionary with results from all tasks
            If merge_strategy is 'return_all': A list of individual task results
        """
        if not context:
            context = {}

        if not isinstance(self.tasks, list):
            self.tasks = [
                self.tasks for _ in range(
                    len(context) if isinstance(context, list) else 1
                )
            ]
            
        results = []
        
        # Use ThreadPoolExecutor to run tasks in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all tasks to the executor

            if isinstance(context, list):
                future_to_task = {
                    executor.submit(self._execute_task, task, context[i]): task 
                    for i, task in enumerate(self.tasks)
                }
            else:
                future_to_task = {
                    executor.submit(self._execute_task, task, context): task 
                    for task in self.tasks
                }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger(f"Task generated an exception: {e}")
        
        return results