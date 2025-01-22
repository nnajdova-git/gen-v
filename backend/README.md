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

All environment variables are defined in `settings.py` using [Pydantic settings
management](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).

For local development, the following environment variables can be helpful:

- `USE_MOCKS`: Set this to "True" to use mock responses from the APIs. This
  is useful for development and testing when you don't want to make actual
  calls to the Google Cloud endpoint like Veo. When set to "False" or not set
  at all, the backend will make real API calls.

## Testing

*   Tests are located in the `tests` directory.
*   Use `pytest` to run the tests:

    ```bash
    pytest
    ```
