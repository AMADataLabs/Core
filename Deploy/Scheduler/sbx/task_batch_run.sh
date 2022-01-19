aws batch submit-job \
--job-name=scheduler-dev \
--job-definition=ecs-scheduler-job-definition \
--job-queue=ecs-scheduler-job-queue \
--container-overrides='{"command": ["python","task.py","{\"dag\": \"ECS_SCHEDULER\", \"type\": \"Task\", \"task\": \"EXTRACT_SCHEDULE\", \"execution_time\": \"2020-11-10 21:30:00.000\"}"]}'