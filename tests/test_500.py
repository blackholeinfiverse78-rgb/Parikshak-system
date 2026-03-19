from app.services.product_orchestrator import ProductOrchestrator
from app.services.review_engine import ReviewEngine
from app.models.schemas import Task
from app.models.persistent_storage import product_storage
from datetime import datetime

product_storage.clear_all()
orchestrator = ProductOrchestrator(ReviewEngine())

task = Task(
    task_id='test-001',
    task_title='Implement User Authentication System',
    task_description='Build a complete JWT-based authentication system with login, register, and token refresh endpoints.',
    submitted_by='Test User',
    timestamp=datetime.now(),
    module_id='core-development',
    schema_version='v1.0',
    github_repo_link='https://github.com/octocat/Hello-World'
)

try:
    result = orchestrator.process_submission(task)
    print('SUCCESS:', result['submission_id'])
    print('Score:', result['review']['score'])
    print('Status:', result['review']['status'])
    print('Next task:', result['next_task']['title'])
except Exception as e:
    import traceback
    traceback.print_exc()
