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
"""Helper functions for working with Firestore.

Creates, gets, updates, deletes, and queries Firestore collections and returns
the results as Pydantic models.

Subclasses of data_models.DataModel are expected as inputs, to ensure that the
data is validated before being written to Firestore, and for consistent handling
between the backend and data layer.
"""
from google.cloud import firestore
from models import data_models


def create_document(
    collection_name: str,
    document_id: str,
    data: data_models.DataModel,
    database_name: str | None = None,
    db: firestore.Client | None = None,
) -> str:
  """Creates a new document in the specified collection.

  Args:
    collection_name: The name of the collection to create the document in.
    document_id: The ID of the document to create.
    data: The data to use for the document.
    database_name: Firestore supports multiple databases. If this is not
      provided it will default to the `(default)` database. Use this value if
      you would like to use a different database.
    db: The Firestore client to use. This is mostly for testing to allow
      dependency injection.

  Returns:
    The ID of the created document.
  """
  db = db or firestore.Client(database=database_name)
  doc_ref = db.collection(collection_name).document(document_id)
  doc_ref.set(data.model_dump())
  return doc_ref.id


def get_document(
    collection_name: str,
    document_id: str,
    model_type: data_models.DataModel,
    database_name: str | None = None,
    db: firestore.Client | None = None,
) -> str:
  """Gets a document from Firestore and returns it as a Pydantic model.

  Args:
    collection_name: The name of the collection to get the document from.
    document_id: The ID of the document to get.
    model_type: The Pydantic model type to use for the returned document.
    database_name: Firestore supports multiple databases. If this is not
      provided it will default to the `(default)` database. Use this value if
      you would like to use a different database.
    db: The Firestore client to use. This is mostly for testing to allow
      dependency injection.

  Returns:
    The document as a Pydantic model, or None if the document does not exist.
  """
  db = db or firestore.Client(database=database_name)

  doc = db.collection(collection_name).document(document_id).get()
  if doc.exists:
    return model_type.model_validate(doc.to_dict())
  else:
    return None


def update_document(
    collection_name: str,
    document_id: str,
    data: data_models.DataModel,
    database_name: str | None = None,
    db: firestore.Client | None = None,
) -> None:
  """Updates a document in Firestore.

  Args:
    collection_name: The name of the collection.
    document_id: The ID of the document to update.
    data: The data to update the document with.
    database_name: Firestore supports multiple databases. If this is not
      provided it will default to the `(default)` database. Use this value if
      you would like to use a different database.
    db: The Firestore client to use. This is mostly for testing to allow
      dependency injection.
  """
  db = db or firestore.Client(database=database_name)

  doc_ref = db.collection(collection_name).document(document_id)
  doc_ref.update(data.model_dump())


def delete_document(
    collection_name: str,
    document_id: str,
    database_name: str | None = None,
    db: firestore.Client | None = None,
) -> None:
  """Deletes a document from Firestore.

  Args:
    collection_name: The name of the collection.
    document_id: The ID of the document to delete.
    database_name: Firestore supports multiple databases. If this is not
      provided it will default to the `(default)` database. Use this value if
      you would like to use a different database.
    db: The Firestore client to use. This is mostly for testing to allow
    dependency injection.
  """
  db = db or firestore.Client(database=database_name)

  doc_ref = db.collection(collection_name).document(document_id)
  doc_ref.delete()


def query_collection(
    collection_name: str,
    model_type: data_models.DataModel,
    query_field: str | None = None,
    query_operator: str | None = None,
    query_value: str | None = None,
    database_name: str | None = None,
    db: firestore.Client | None = None,
) -> list[data_models.DataModel]:
  """Queries a Firestore collection and returns a list of Pydantic models.

  Args:
    collection_name: The name of the collection to query.
    model_type: The Pydantic model type to use for the returned documents.
    query_field: The field to filter on (optional).
    query_operator: The operator to use for the filter (optional).
    query_value: The value to filter on (optional).
    database_name: Firestore supports multiple databases. If this is not
      provided it will default to the `(default)` database. Use this value if
      you would like to use a different database.
    db: The Firestore client to use. This is mostly for testing to allow
    dependency injection.

  Returns:
    A list of Pydantic models representing the documents that match the query.
  """
  db = db or firestore.Client(database=database_name)

  collection_ref = db.collection(collection_name)

  if query_field and query_operator and query_value:
    query = collection_ref.where(query_field, query_operator, query_value)
  else:
    query = collection_ref

  docs = query.stream()
  return [model_type.model_validate(doc.to_dict()) for doc in docs]
