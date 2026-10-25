# Test status

The offline tests in tests/test_catalog_tool.py are designed to run without AWS credentials and mock S3 responses. The preparation environment used Python 3.13 and boto3 1.43.18. The Strands Agents SDK could not be installed in that environment because outbound package-index networking was unavailable, so the live Bedrock/Strands agent path has not been executed here.

Run locally:
    python -m unittest discover -s tests -v
    python -m compileall -q .
    python main.py --skill "data science" --budget free

The GitHub Actions workflow installs declared dependencies and reruns tests on the challenge branch. Review its result on GitHub before claiming CI passed.
