from prometheus_client import Counter, Gauge

workflow_runs = Counter('githubactions_workflow_run_total',
                        'Number of workflow executions',
                        ['workflow_id'])
workflow_failures = Counter('githubactions_workflow_run_failure_total',
                            'Number of failed workflow runs',
                            ['workflow_id'])
workflow_successes = Counter('githubactions_workflow_run_success_total',
                             'Number of successful workflow runs',
                             ['workflow_id'])
workflow_duration = Gauge('githubactions_workflow_run_duration_seconds',
                          'Duration of a workflow run in seconds',
                          ['workflow_id'])
job_runs = Counter('githubactions_workflow_job_total',
                   'Number of workflow job executions',
                   ['workflow_run_id', 'workflow_job_id'])
job_successes = Counter('githubactions_workflow_job_success_total',
                        'Number of successful workflow job runs',
                        ['workflow_run_id', 'workflow_job_id'])
job_failures = Counter('githubactions_workflow_job_failure_total',
                       'Number of failed workflow job runs',
                       ['workflow_run_id','workflow_job_id'])
