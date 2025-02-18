# Gen V: Backend

This repository contains the backend code for the Gen V application.

## Overview

The backend is built using Flask, and provides API endpoints for managing the
app.

## Getting Started

To run the development server run:
```
pip install --require-hashes -r requirements_dev.txt
python main.py
```

It will be available at http://localhost:8080.

## Environment Variables

All environment variables are defined in `settings.py` using
[Pydantic settings management](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).

For local development, the following environment variables can be helpful:

-   `USE_MOCKS`: Set this to "True" to use mock responses from the APIs. This is
    useful for development and testing when you don't want to make actual calls
    to the Google Cloud endpoint like Veo. When set to "False" or not set at
    all, the backend will make real API calls.

## Managing Dependencies

This project uses `pip-tools` to manage dependencies and ensure reproducible
builds. Dependencies are specified in `requirements.raw.txt`, and the actual
installable dependency list (with hashes for security) is generated in
`requirements.txt`.

### Adding or Updating Dependencies

1.  Edit the appropriate `.raw.txt` file:
    * `requirements.raw.txt`: For core project dependencies.
    * `requirements_dev.raw.txt`: For development-specific dependencies (e.g
      testing tools).

    Add, remove, or update package versions in the chosen file. List only the
    top-level dependencies.

    ```
    # requirements.raw.txt (Example)
    google-cloud-firestore>=2.0.0
    pydantic
    requests

    # requirements_dev.raw.txt (Example)
    pytest
    ```

2.  Generate the corresponding `requirements.txt` file(s): Run the following
    command(s) to update the `requirements.txt` and/or `requirements_dev.txt`
    file(s) with the correct versions and hashes:

    ```bash
    pip-compile --generate-hashes --no-annotate --output-file=requirements.txt requirements.raw.txt
    pip-compile --generate-hashes --no-annotate --allow-unsafe --output-file=requirements_dev.txt requirements_dev.raw.txt
    ```

## Code Quality and Formatting
This project uses several tools to ensure code quality and consistent
formatting:

- Pylint: For static code analysis and linting. Run `pylint --recursive=y .` to
  check your code. The Pylint configuration is in `.pylintrc`.
- Pyink: For code formatting. Pyink is integrated as a pre-commit hook.

### Pre-Commit Hooks
This project uses pre-commit to automate code formatting before each commit.

After installing the dev requirements run: `pre-commit install` to install the
hook.

You can run the hooks manually with `pre-commit run` if needed. This is useful
for checking your changes before committing.

## Testing

*   Tests are located in the `tests` directory.
*   Use `pytest` to run the tests:

    ```bash
    pytest
    ```
