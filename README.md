Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

![Gen V logo](./docs/images/gen-v-logo-small.png)

# Disclaimer

Gen V is NOT an official Google product.

# Gen V: AI-Powered Video Ads

Create AI-powered video ads with [Veo](
https://deepmind.google/technologies/veo/veo-2/) on Google Cloud, enhanced with
AI voice and audio, and personalised with brand logos, stickers and promo texts.

# Gen V colab aka Feedflix

Our initial use case, FeedFlix, is implemented as a user-friendly Colab notebook.
This Colab notebook demonstrates how to use Google's Generative AI models 
(Gemini and Video Generation) to create short video ads from product images.

## FeedFlix features 

* **Image Processing:** Resizes and recolors product images to prepare them for video generation.
* **Prompt Generation:** Uses Gemini to analyze images and generate creative video prompts.
* **Video Generation:** Leverages Google's Video Generation API to create short video ads from images and prompts.
* **User Selection:** Allows users to interactively choose the best-generated videos.
* **Video Editing:** Enables adding overlays, transitions, and audio to enhance the final video.
* **Video Stitching:** Combines selected videos into a single, cohesive advertisement.

## Getting Started

1. **Open the Colab notebook:** See section below "How to start with the colab"
2. **Set up your GCP project:**
    * Enable the required APIs: Gemini, Cloud Storage. See section below called "Requirements" 
    * Create a Cloud Storage bucket to store your input and output files. See section below: "GCS Assets Requirements".
    * Update the GCP parameters in the notebook with your project ID, bucket name, and folder name. 
    * Review and if needed update the rest of the parameters in the colab. See section  below: Customization.
3. **Upload your product images:** Upload your product images to the designated folder in your Cloud Storage bucket.
4. **Run the notebook:** Follow the instructions in the notebook to execute the code cells and generate your video ads.
    * Some steps do not produce output, they only define functions.
    * If a step asks you to **Restart Runtime**, do so.
    * Some steps require user selection so "Run all cells" will not produce an end to end succesful run without stopping for user selection
    * If a step displays an error, stop and debug it. Debug the following:
      * APIs are enabled.
      * Storage bucket is correctly configured and the files are present with the same names the colab expects (e.g. font.ttf) or rename the defaults in the colab
      * Previous colab sections completed and user selection was done.
      * Select _Runtime > Reset Session and Run All_ as a last resort.

### How to start with the colab

1. Navigate to [colab.research.google.com](http://colab.research.google.com).
2. In the dialog, open a Notebook from GitHub.
3. Enter the url from this page.

### Requirements

* Google Cloud Project with billing enabled.
* Enabled APIs:
    * [Vertex AI API](https://console.cloud.google.com/marketplace/product/google/aiplatform.googleapis.com)
    * [Cloud Storage API](https://console.cloud.google.com/marketplace/product/google/storage.googleapis.com)
* Python 3.7 or later.
* Required Python libraries: `google-genai`, `mediapy`, `Pillow`, `moviepy`.
  
### GCS Assets Requirements

1. Store your assets on [Google Cloud Storage](https://console.cloud.google.com/storage/browser) with the following folder structure:
    * **[GCP_BUCKET_NAME]** - name of bucket, ensure you have write permission.
    * **[FOLDER_NAME]** - name of the folder in the bucket, ensure you have write permission.
    * In the folder create 6 subfolders:
        * **audio** - And add in the folder your m4a audio file with the background music.
        * **fonts** - And add here your .otf or .ttf font file.
        * **input-images** - Add your product images here.
        * **input-overlays** - Add here your sticker.png if you want to use sticker overlay.
        * **input-videos** - Add here your intro and outro videos that you want appedend before and after the Veo generated videos.
        * **logos** - Add here your logo, ideally in small dimensions with high quality resolution.

### Customization

* **Video Prompts:** You can [customize the video prompts](https://cloud.google.com/vertex-ai/generative-ai/docs/video/video-gen-prompt-guide) used by the Video Generation API.
* **Video Parameters:** Adjust the duration, sample count, and other parameters to control the generated videos.
* **Overlays and Transitions:** Add your own logos, stickers, text overlays, and transitions to personalize your videos.
* **Audio:** Include background music to enhance the audio experience. Voice overs are not supported yet.

## Disclaimer

This is a sample Colab notebook and may require modifications to suit your specific needs.





