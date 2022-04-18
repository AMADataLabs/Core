aws batch submit-job \
--job-name=scheduler-dev \
--job-definition=ecs-scheduler-job-definition \
--job-queue=ecs-scheduler-job-queue \
--container-overrides='{"command": ["python","task.py","{\"dag\": \"DAG_SCHEDULER\", \"type\": \"DAG\", \"execution_time\": \"2020-11-10 21:30:00.000\"}"]}'