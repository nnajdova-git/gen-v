![Gen V logo](./docs/images/gen-v-logo-small.png)

# Gen V: AI-Powered Video Ads

Create AI-powered video ads with [Veo](
https://deepmind.google/technologies/veo/veo-2/) on Google Cloud, enhanced with
AI voice and audio, and personalised with brand logos.

## Get Started

Coming soon...

## Local Development

These are the steps to run the application locally for development:

1.  **Start the Backend:**

    *   See instructions in the [backend README](./backend/README.md).
    *   The backend will typically be available at `http://localhost:8080`.

2.  **Start the Frontend:**

    *   See instructions in the [frontend/ui README](./frontend/ui/README.md).
    *   The frontend will typically be available at `http://localhost:4200` and
        will proxy API requests to the backend.

## Production Deployment

These are the manual steps for deployment.

Run these steps once:
```
gcloud init

gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com

gcloud projects add-iam-policy-binding [project-id] \
  --member="serviceAccount:[project-number]-compute@developer.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

Run these commands to build & deploy the backend:
```
gcloud builds submit --config deploy/cloudbuild-backend.yaml backend/

gcloud run deploy gen-v-backend \
  --image gcr.io/[project-id]/gen-v-backend \
  --platform managed \
  --region europe-west2 \
  --allow-unauthenticated
```

Run these commands to build & deploy the frontend:

Note: Update the backend URL to the cloud run deployment from above without a
`/` on the end.

```
gcloud builds submit \
  --config deploy/cloudbuild-frontend.yaml \
  --substitutions _BACKEND_URL="[https://backendurl.run.app]" \
 frontend/ui

gcloud run deploy gen-v-frontend \
  --image gcr.io/[project-id]/gen-v-frontend \
  --platform managed \
  --region europe-west2 \
  --allow-unauthenticated
```

## Disclaimer
__This is not an officially supported Google product.__

Copyright 2025 Google LLC. This solution, including any related sample code or
data, is made available on an "as is", "as available", and "with all faults"
basis, solely for illustrative purposes, and without warranty or representation
of any kind. This solution is experimental, unsupported and provided solely for
your convenience. Your use of it is subject to your agreements with Google, as
applicable, and may constitute a beta feature as defined under those agreements.
To the extent that you make any data available to Google in connection with your
use of the solution, you represent and warrant that you have all necessary and
appropriate rights, consents and permissions to permit Google to use and process
that data. By using any portion of this solution, you acknowledge, assume and
accept all risks, known and unknown, associated with its usage, including with
respect to your deployment of any portion of this solution in your systems, or
usage in connection with your business, if at all.
