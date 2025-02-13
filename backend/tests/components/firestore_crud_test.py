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
"""Unit tests for firestore_crud.py."""

import unittest.mock

from components import firestore_crud
import mockfirestore
from models import data_models
import pytest


@pytest.fixture(name='mock_firestore_client')
def mock_firestore_client_fixture():
  mock_db = mockfirestore.MockFirestore()
  with unittest.mock.patch(
      'google.cloud.firestore.Client', return_value=mock_db
  ) as mock_client:
    yield mock_client, mock_db


@pytest.fixture(name='test_data_model')
def test_data_model_fixture():
  class TestDataModel(data_models.DataModel):
    test_field: str = 'test_value'

  return TestDataModel()


@pytest.mark.parametrize(
    'database_name',
    ['test-database', None],
)
def test_create_document(mock_firestore_client, test_data_model, database_name):
  mock_client, mock_db = mock_firestore_client

  collection_name = 'test_collection'
  document_id = 'test_document'

  firestore_crud.create_document(
      collection_name=collection_name,
      document_id=document_id,
      data=test_data_model,
      database_name=database_name,
  )
  doc = mock_db.collection(collection_name).document(document_id).get()
  assert doc.exists
  assert doc.to_dict() == test_data_model.model_dump()
  mock_client.assert_called_once_with(database=database_name)


@pytest.mark.parametrize(
    'database_name',
    ['test-database', None],
)
def test_get_document(mock_firestore_client, test_data_model, database_name):
  mock_client, mock_db = mock_firestore_client
  collection_name = 'test_collection'
  document_id = 'test_document'

  mock_db.collection(collection_name).document(document_id).set(
      test_data_model.model_dump()
  )
  retrieved_data = firestore_crud.get_document(
      collection_name=collection_name,
      document_id=document_id,
      model_type=type(test_data_model),
      database_name=database_name,
  )

  assert retrieved_data is not None
  assert retrieved_data == test_data_model
  mock_client.assert_called_once_with(database=database_name)


@pytest.mark.parametrize(
    'database_name',
    ['test-database', None],
)
def test_update_document(mock_firestore_client, test_data_model, database_name):
  mock_client, mock_db = mock_firestore_client
  collection_name = 'test_collection'
  document_id = 'test_document'

  mock_db.collection(collection_name).document(document_id).set(
      test_data_model.model_dump()
  )

  updated_data = test_data_model.model_copy(update={'test_field': 'new_value'})
  firestore_crud.update_document(
      collection_name=collection_name,
      document_id=document_id,
      data=updated_data,
      database_name=database_name,
  )

  doc = mock_db.collection(collection_name).document(document_id).get()
  assert doc.to_dict()['test_field'] == 'new_value'
  mock_client.assert_called_once_with(database=database_name)


@pytest.mark.parametrize(
    'database_name',
    ['test-database', None],
)
def test_delete_document(mock_firestore_client, test_data_model, database_name):
  mock_client, mock_db = mock_firestore_client
  collection_name = 'test_collection'
  document_id = 'test_document'

  mock_db.collection(collection_name).document(document_id).set(
      test_data_model.model_dump()
  )

  firestore_crud.delete_document(
      collection_name=collection_name,
      document_id=document_id,
      database_name=database_name,
  )

  doc = mock_db.collection(collection_name).document(document_id).get()
  assert not doc.exists
  mock_client.assert_called_once_with(database=database_name)


@pytest.mark.parametrize(
    'database_name',
    ['test-database', None],
)
def test_query_collection(
    mock_firestore_client, test_data_model, database_name
):
  mock_client, mock_db = mock_firestore_client
  collection_name = 'test_collection'

  for i in range(3):
    mock_db.collection(collection_name).document(f'doc_{i}').set(
        test_data_model.model_dump()
    )

  results = firestore_crud.query_collection(
      collection_name=collection_name,
      model_type=type(test_data_model),
      database_name=database_name,
  )

  assert len(results) == 3
  assert all(isinstance(result, type(test_data_model)) for result in results)
  mock_client.assert_called_once_with(database=database_name)
