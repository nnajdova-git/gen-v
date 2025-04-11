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
"""Unit tests for image utils."""
import os
from unittest import mock
from PIL import Image
import pytest
from gen_v import models
from gen_v.utils import image


@pytest.fixture(name='sample_image_files')
def fixture_sample_image_files(tmpdir):
  """Creates sample wide (200x100) and tall (100x200) images.

  Returns:
    A dictionary mapping descriptive names ('wide', 'tall') to image file
    paths.
  """
  image_paths = {}

  wide_image_path = os.path.join(tmpdir, 'wide_test_image.png')
  img_wide = Image.new('RGB', (200, 100), color=(0, 255, 0))
  img_wide.save(wide_image_path)
  image_paths['wide'] = wide_image_path

  tall_image_path = os.path.join(tmpdir, 'tall_test_image.png')
  img_tall = Image.new('RGB', (100, 200), color=(0, 0, 255))
  img_tall.save(tall_image_path)
  image_paths['tall'] = tall_image_path

  return image_paths


@pytest.fixture(name='mock_gcs_storage')
def fixture_mock_gcs_storage():
  """Mocks the gen_v.storage module functions."""
  with mock.patch('gen_v.utils.image.storage', autospec=True) as mock_storage:
    mock_storage.retrieve_all_files_from_gcs_folder.return_value = []
    mock_storage.get_file_name_from_gcs_url.side_effect = lambda uri: uri.split(
        '/'
    )[-1]
    mock_storage.download_file_locally.side_effect = (
        lambda uri, **kwargs: f"/tmp/local_{uri.split('/')[-1]}"
    )
    mock_storage.upload_file_to_gcs.return_value = None
    yield mock_storage


def test_rescale_image_height(sample_image_files):
  """Tests correct height and aspect ratio after rescaling by height."""
  rescaled_image = image.rescale_image_height(
      sample_image_files['wide'], desired_height=200
  )
  assert rescaled_image.height == 200
  assert rescaled_image.width == 400
  assert rescaled_image.mode == 'RGBA'


def test_rescale_image_width(sample_image_files):
  """Tests correct width and aspect ratio after rescaling by width."""
  rescaled_image = image.rescale_image_width(
      sample_image_files['wide'], desired_width=500
  )
  assert rescaled_image.height == 250
  assert rescaled_image.width == 500
  assert rescaled_image.mode == 'RGBA'


def test_rescale_image_to_fit_wide_image_into_square(sample_image_files):
  """Tests fitting a wide image into a square box.

  The image is wider than the box (400x200 vs 100x100).
  It should be scaled based on width, resulting in 100x50.
  """
  rescaled_img = image.rescale_image_to_fit(
      sample_image_files['wide'], desired_width=100, desired_height=100
  )
  assert rescaled_img.width == 100
  assert rescaled_img.height == 50


def test_rescale_image_to_fit_tall_image_into_square(sample_image_files):
  """Tests fitting a tall image into a square box.

  The image is taller than the box (200x400 vs 100x100).
  It should be scaled based on height, resulting in 50x100.
  """
  rescaled_img = image.rescale_image_to_fit(
      sample_image_files['tall'], desired_width=100, desired_height=100
  )
  assert rescaled_img.width == 50
  assert rescaled_img.height == 100


@pytest.mark.parametrize(
    'hex_input, expected_rgb_tuple',
    [
        ('#FF0000', (255, 0, 0)),
        ('00FF00', (0, 255, 0)),
        ('0000FF', (0, 0, 255)),
        ('#ffffff', (255, 255, 255)),
        ('000000', (0, 0, 0)),
        ('#fF0aA9', (255, 10, 169)),
        ('123456', (18, 52, 86)),
    ],
)
def test_hex_to_rgb_valid_inputs(hex_input, expected_rgb_tuple):
  """Tests successful conversion for various valid hex strings."""
  assert image.hex_to_rgb(hex_input) == expected_rgb_tuple


@pytest.mark.parametrize(
    'invalid_hex_input',
    [
        '#FF000',
        'FF000',
        '#FF00001',
        'FF00001',
        'FFG000',
        '#FFG000',
        '',
        '#',
        ' #FF0000FF 00 00',
        '#F00',
    ],
)
def test_hex_to_rgb_invalid_inputs_raise_value_error(invalid_hex_input):
  """Tests that invalid hex strings raise a ValueError."""
  with pytest.raises(ValueError):
    image.hex_to_rgb(invalid_hex_input)


def test_place_rescaled_image_on_background(sample_image_files, tmpdir):
  """Tests placing a rescaled image onto a background."""
  output_path_str = tmpdir.join('test_output_composite.png')
  bg_color_rgb = models.RGBColor(r=128, g=0, b=128)
  bg_width = 300
  bg_height = 250

  result_image_obj = image.place_rescaled_image_on_background(
      foreground_image_path=sample_image_files['wide'],
      background_width=bg_width,
      background_height=bg_height,
      background_color=bg_color_rgb,
      output_path=output_path_str,
  )

  assert isinstance(result_image_obj, Image.Image)
  assert os.path.exists(output_path_str)

  saved_image = Image.open(output_path_str)
  assert saved_image.width == bg_width
  assert saved_image.height == bg_height


def test_replace_solid_background(sample_image_files, tmpdir):
  """Tests replacing the solid background of a generated image."""
  # The wide image is green
  input_path = sample_image_files['wide']
  output_path = tmpdir.join('replaced_background.png')

  target_color = models.RGBColor(r=0, g=255, b=0)
  replacement_color = models.RGBColor(r=255, g=0, b=0)
  threshold = 10

  image.replace_background_color(
      image_path=input_path,
      target_color=target_color,
      replacement_color=replacement_color,
      recolored_image_local_path=output_path,
      threshold=threshold,
  )

  assert os.path.exists(output_path)
  with Image.open(output_path) as result_img:
    assert result_img.size == (200, 100)
    assert result_img.mode == 'RGBA'
    colors = result_img.getcolors()
    assert len(colors) == 1
    _, actual_color = colors[0]
    assert actual_color == (255, 0, 0, 255)


@mock.patch('gen_v.utils.image.place_rescaled_image_on_background')
def test_process_and_resize_images_simple_flow(
    mock_place,
    mock_gcs_storage,
    sample_image_files,
):
  """Tests the basic flow of processing one image."""
  input_gcs_uri = 'gs://my-bucket/input-images/'
  output_gcs_uri_base = 'gs://my-bucket/resized'
  img_name = 'sample_test_image.png'
  img_uri = f'{input_gcs_uri}{img_name}'
  local_resized_path = 'sample_test_image-resized-80_60.png'
  expected_output_uri = f'{output_gcs_uri_base}/{local_resized_path}'
  width, height = 80, 60
  bg_color = models.RGBColor(r=255, g=255, b=255)

  mock_gcs_storage.retrieve_all_files_from_gcs_folder.return_value = [img_uri]
  mock_gcs_storage.download_file_locally.return_value = sample_image_files[
      'wide'
  ]

  result = image.process_and_resize_images(
      images_uri=input_gcs_uri,
      width=width,
      height=height,
      color=bg_color,
      output_uri=output_gcs_uri_base,
  )

  assert len(result) == 1
  assert result[0]['title'] == img_name
  assert result[0]['resized_image_uri'] == expected_output_uri

  mock_gcs_storage.retrieve_all_files_from_gcs_folder.assert_called_once_with(
      input_gcs_uri
  )
  mock_gcs_storage.download_file_locally.assert_called_once_with(img_uri)
  mock_place.assert_called_once()
  mock_gcs_storage.upload_file_to_gcs.assert_called_once()


@mock.patch('gen_v.utils.image.replace_background_color')
def test_recolor_background_and_upload_simple_flow(
    mock_replace,
    mock_gcs_storage,
    sample_image_files,
):
  """Tests the basic flow of recoloring one image."""
  output_bucket_uri = 'my-bucket/recolored'
  target_color = models.RGBColor(r=0, g=255, b=0)
  background_color = models.RGBColor(r=255, g=0, b=0)
  resized_img_name = 'sample_test_image-resized-100_100.png'
  resized_image_uri = f'gs://my-bucket/{resized_img_name}'
  recolored_img_local_name = (
      'sample_test_image-resized-100_100-recolored-255_0_0.png'
  )
  expected_recolored_gcs_uri = (
      f'gs://{output_bucket_uri}/{recolored_img_local_name}'
  )

  selected_products = [
      {'title': 'sample_test_image.png', 'resized_image_uri': resized_image_uri}
  ]

  mock_gcs_storage.download_file_locally.return_value = sample_image_files[
      'wide'
  ]
  mock_gcs_storage.get_file_name_from_gcs_url.return_value = resized_img_name

  image.recolor_background_and_upload(
      selected_products=selected_products,
      output_uri=output_bucket_uri,
      target_color=target_color,
      background_color=background_color,
  )

  assert 'recolored_image_uri' in selected_products[0]
  assert (
      selected_products[0]['recolored_image_uri'] == expected_recolored_gcs_uri
  )

  mock_gcs_storage.download_file_locally.assert_called_once_with(
      resized_image_uri
  )
  mock_replace.assert_called_once()
  mock_gcs_storage.upload_file_to_gcs.assert_called_once()
