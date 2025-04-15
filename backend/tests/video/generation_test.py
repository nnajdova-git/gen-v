# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Unit tests for video generation."""
from unittest import mock
from google import genai
from google.genai import types
import pytest
import requests
from gen_v import models
from gen_v.video import generation


@pytest.fixture(name='mock_requests_post')
def mock_requests_post_fixture():
  with mock.patch.object(requests, 'post', autospec=True) as requests_post:
    yield requests_post


@pytest.fixture(name='veo_api_request_data')
def veo_api_request_data_fixture() -> models.VeoApiRequest:
  """Provides a sample VeoApiRequest object."""
  yield models.VeoApiRequest(
      prompt='A running dog',
      image_uri='gs://test-bucket/test-folder/input-images/dog.png',
      gcs_uri='gs://test-bucket/test-folder/output-videos/',
      duration=4,
      sample_count=1,
      aspect_ratio='9:16',
  )


@pytest.fixture(name='product_data')
def product_data_fixture() -> dict[str, any]:
  """Provides sample product data."""
  yield {'title': 'Super Dog Toy'}


def test_send_request_to_google_api(mock_requests_post):
  mock_api_endpoint = 'https://europe-west2-aiplatform.googleapis.com/v1'
  mock_data = {'key': 'value'}
  mock_access_token = 'my-token-abc'
  expected_response_json = {
      'name': 'test_operation',
      'done': True,
  }

  mock_response = mock.Mock()
  mock_response.status_code = 200
  mock_response.json.return_value = expected_response_json
  mock_requests_post.return_value = mock_response

  response = generation.send_request_to_google_api(
      mock_api_endpoint, mock_data, mock_access_token
  )

  assert response == expected_response_json

  mock_requests_post.assert_called_once()
  call_args, call_kwargs = mock_requests_post.call_args
  assert call_args[0] == mock_api_endpoint
  assert (
      call_kwargs['headers']['Authorization'] == f'Bearer {mock_access_token}'
  )
  assert call_kwargs['json'] == mock_data


@mock.patch('google.genai.types.Part.from_bytes')
def test_get_gemini_prompt_success_with_image(
    mock_part_from_bytes, png_file_in_fs
):
  """Tests a successful call with an image, using a mocked client."""
  test_prompt = 'Describe the provided image.'
  test_model_name = 'gemini-test-model'
  request = models.GeminiPromptRequest(
      prompt_text=test_prompt,
      image_file_path=png_file_in_fs,
      model_name=test_model_name,
  )

  assert request.image_bytes is not None
  assert request.mime_type == 'image/png'

  mock_client = mock.Mock(spec=genai.Client)
  mock_response = mock.Mock()
  mock_response.text = 'Successfully described image!'
  mock_client.models.generate_content.return_value = mock_response

  mock_image_part_instance = mock.Mock(spec=types.Part)
  mock_part_from_bytes.return_value = mock_image_part_instance

  result = generation.get_gemini_generated_video_prompt(
      request_data=request, client=mock_client
  )
  assert result == mock_response.text

  mock_part_from_bytes.assert_called_once_with(
      data=request.image_bytes, mime_type=request.mime_type
  )

  mock_client.models.generate_content.assert_called_once()
  _, call_kwargs = mock_client.models.generate_content.call_args

  assert call_kwargs['model'] == test_model_name


@mock.patch('gen_v.video.generation.time.sleep')
@mock.patch('gen_v.video.generation.send_request_to_google_api')
def test_fetch_operation_success_first_try(
    mock_send_request, mock_sleep, mock_app_settings
):
  """Tests fetch_operation succeeds when API returns 'done': True."""
  mock_app_settings.fetch_endpoint = 'http://fake-endpoint.com/fetch'
  lro_name = 'operations/op123'
  expected_request_data = {'operationName': lro_name}
  success_response = {'done': True, 'response': {'status': 'COMPLETED'}}
  mock_send_request.return_value = success_response

  result = generation.fetch_operation(lro_name, mock_app_settings)

  assert result == success_response
  mock_send_request.assert_called_once_with(
      mock_app_settings.fetch_endpoint, expected_request_data
  )
  mock_sleep.assert_not_called()


@mock.patch('gen_v.video.generation.fetch_operation')
@mock.patch('gen_v.video.generation.send_request_to_google_api')
def test_image_to_video_success(
    mock_send_request,
    mock_fetch,
    veo_api_request_data,
    mock_app_settings,
):
  """Tests the successful execution path of image_to_video."""
  lro_name = 'operations/123456789'
  initial_response = {'name': lro_name}
  final_response = {
      'done': True,
      'response': {
          'predictions': [{'outputVideoGcsUri': 'gs://test-bucket/video.mp4'}]
      },
      'metadata': {},
      'name': lro_name,
  }
  mock_send_request.return_value = initial_response
  mock_fetch.return_value = final_response

  expected_payload = veo_api_request_data.to_api_payload()

  result = generation.image_to_video(veo_api_request_data, mock_app_settings)

  mock_send_request.assert_called_once_with(
      mock_app_settings.fetch_endpoint, expected_payload
  )

  mock_fetch.assert_called_once_with(lro_name, mock_app_settings)
  assert result == final_response


@mock.patch('gen_v.video.generation.storage.download_file_locally')
@mock.patch('gen_v.storage.get_file_name_from_gcs_url')
@mock.patch('gen_v.video.generation.image_to_video')
def test_generate_videos_and_download_success_simple(
    mock_img_to_vid,
    mock_get_filename,
    mock_download,
    veo_api_request_data,
    mock_app_settings,
    product_data,
):
  """Tests the simple success path of generate_videos_and_download."""
  output_prefix = 'promo_v1'
  input_image_filename = 'image_dog.png'
  generated_video_gcs_uri = 'gs://test-bucket/outputs/gen_video_abc.mp4'
  generated_video_filename = 'gen_video_abc.mp4'

  mock_img_to_vid.return_value = {
      'response': {'videos': [{'gcsUri': generated_video_gcs_uri}]}
  }

  mock_get_filename.side_effect = [
      input_image_filename,
      generated_video_filename,
  ]

  expected_local_path = (
      f'{input_image_filename}-{output_prefix}-{generated_video_filename}'
  )
  expected_local_filename = expected_local_path.rsplit('/', maxsplit=1)[-1]

  result = generation.generate_videos_and_download(
      veo_request=veo_api_request_data,
      settings=mock_app_settings,
      output_file_prefix=output_prefix,
      product=product_data,
  )

  mock_img_to_vid.assert_called_once_with(
      veo_api_request_data, mock_app_settings
  )

  assert mock_get_filename.call_count == 2
  mock_get_filename.assert_has_calls([
      mock.call(veo_api_request_data.image_uri),
      mock.call(generated_video_gcs_uri),
  ])

  mock_download.assert_called_once_with(
      generated_video_gcs_uri, expected_local_path
  )

  assert isinstance(result, list)
  assert len(result) == 1

  expected_output_item = {
      'gcs_uri': generated_video_gcs_uri,
      'local_file': expected_local_path,
      'local_file_name': expected_local_filename,
      'product_title': product_data['title'],
      'promo_text': '',
  }
  assert result[0] == expected_output_item
