========================================
GitHub Actions Workflow Metrics Listener
========================================

This app listens to webhook events issued from GitHub Actions and publishes
select metrics on an endpoint for Prometheus to harvest.

Test Locally
------------

Try it out locally by starting the Flask app or Docker container, then forward
the webhooks with the `GitHub CLI`_.

.. _GitHub CLI: https://docs.github.com/en/webhooks/testing-and-troubleshooting-webhooks/using-the-github-cli-to-forward-webhooks-for-testing#receiving-webhooks-with-github-cli

.. code-block::

   flask --app gha_prometheus.app run --port 8080

.. code-block::

   gh webhook forward --repo tdenny/gha_prometheus --events workflow_run --url
   "http://localhost:8080/webhook

Now, `workflow_run` webhook events will be forwarded to your locally running
`gha_prometheus`. You can inspect the metrics page at
http://localhost:8080/metrics.
