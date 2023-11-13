from typing import Any, Dict, List

import numpy as np
import pytest

from qdrant_client.client_base import QdrantBase
from qdrant_client.http.models import models
from qdrant_client.local.qdrant_local import QdrantLocal
from qdrant_client.qdrant_client import QdrantClient
from tests.congruence_tests.test_common import (
    COLLECTION_NAME,
    compare_client_results,
    generate_fixtures,
    image_vector_size,
    init_client,
    init_local,
    init_remote,
)
from tests.fixtures.filters import one_random_filter_please

secondary_collection_name = "secondary_collection"


def random_vector(dims: int) -> List[float]:
    return np.random.random(dims).round(3).tolist()


@pytest.fixture(scope="module")
def fixture_records() -> List[models.Record]:
    return generate_fixtures()


@pytest.fixture(scope="module")
def secondary_collection_records() -> List[models.Record]:
    return generate_fixtures(100)


@pytest.fixture(scope="module", autouse=True)
def local_client(fixture_records, secondary_collection_records) -> QdrantLocal:
    client = init_local()
    init_client(client, fixture_records)
    init_client(client, secondary_collection_records, secondary_collection_name)
    return client


@pytest.fixture(scope="module", autouse=True)
def remote_client(fixture_records, secondary_collection_records) -> QdrantClient:
    client = init_remote()
    init_client(client, fixture_records)
    init_client(client, secondary_collection_records, secondary_collection_name)
    return client


def test_context_cosine(local_client, remote_client):
    def f(client: QdrantBase, **kwargs: Dict[str, Any]) -> List[models.ScoredPoint]:
        return client.discover(
            collection_name=COLLECTION_NAME,
            context=[models.ContextExamplePair(positive=10, negative=19)],
            with_payload=True,
            limit=1000,
            using="image",
        )

    compare_client_results(local_client, remote_client, f, is_context_search=True)


def test_context_dot(local_client, remote_client):
    def f(client: QdrantBase, **kwargs: Dict[str, Any]) -> List[models.ScoredPoint]:
        return client.discover(
            collection_name=COLLECTION_NAME,
            context=[models.ContextExamplePair(positive=10, negative=19)],
            with_payload=True,
            limit=1000,
            using="text",
        )

    compare_client_results(local_client, remote_client, f, is_context_search=True)


def test_context_euclidean(local_client, remote_client):
    def f(client: QdrantBase, **kwargs: Dict[str, Any]) -> List[models.ScoredPoint]:
        return client.discover(
            collection_name=COLLECTION_NAME,
            context=[models.ContextExamplePair(positive=11, negative=19)],
            with_payload=True,
            limit=1000,
            using="code",
        )

    compare_client_results(local_client, remote_client, f, is_context_search=True)


def test_context_many_pairs(local_client, remote_client):
    random_image_vector_1 = random_vector(image_vector_size)
    random_image_vector_2 = random_vector(image_vector_size)

    def f(client: QdrantBase, **kwargs: Dict[str, Any]) -> List[models.ScoredPoint]:
        return client.discover(
            collection_name=COLLECTION_NAME,
            context=[
                models.ContextExamplePair(positive=11, negative=19),
                models.ContextExamplePair(positive=400, negative=200),
                models.ContextExamplePair(
                    positive=random_image_vector_1, negative=random_image_vector_2
                ),
                models.ContextExamplePair(positive=30, negative=random_image_vector_2),
                models.ContextExamplePair(positive=random_image_vector_1, negative=15),
            ],
            with_payload=True,
            limit=500,
            using="image",
        )

    compare_client_results(local_client, remote_client, f, is_context_search=True)


def test_discover_cosine(local_client, remote_client):
    def f(client: QdrantBase, **kwargs: Dict[str, Any]) -> List[models.ScoredPoint]:
        return client.discover(
            collection_name=COLLECTION_NAME,
            target=10,
            context=[models.ContextExamplePair(positive=11, negative=19)],
            with_payload=True,
            limit=10,
            using="image",
        )

    compare_client_results(local_client, remote_client, f)


def test_discover_dot(local_client, remote_client):
    def f(client: QdrantBase, **kwargs: Dict[str, Any]) -> List[models.ScoredPoint]:
        return client.discover(
            collection_name=COLLECTION_NAME,
            target=10,
            context=[models.ContextExamplePair(positive=11, negative=19)],
            with_payload=True,
            limit=10,
            using="text",
        )

    compare_client_results(local_client, remote_client, f)


def test_discover_euclidean(local_client, remote_client):
    def f(client: QdrantBase, **kwargs: Dict[str, Any]) -> List[models.ScoredPoint]:
        return client.discover(
            collection_name=COLLECTION_NAME,
            target=10,
            context=[models.ContextExamplePair(positive=11, negative=19)],
            with_payload=True,
            limit=10,
            using="code",
        )

    compare_client_results(local_client, remote_client, f)


def test_discover_raw_target(local_client, remote_client):
    random_image_vector = random_vector(image_vector_size)

    def f(client: QdrantBase, **kwargs: Dict[str, Any]) -> List[models.ScoredPoint]:
        return client.discover(
            collection_name=COLLECTION_NAME,
            target=random_image_vector,
            context=[models.ContextExamplePair(positive=10, negative=19)],
            limit=10,
            using="image",
        )

    compare_client_results(local_client, remote_client, f)


def test_context_raw_positive(local_client, remote_client):
    random_image_vector = random_vector(image_vector_size)

    def f(client: QdrantBase, **kwargs: Dict[str, Any]) -> List[models.ScoredPoint]:
        return client.discover(
            collection_name=COLLECTION_NAME,
            target=10,
            context=[models.ContextExamplePair(positive=random_image_vector, negative=19)],
            limit=10,
            using="image",
        )

    compare_client_results(local_client, remote_client, f)


def test_only_target(local_client, remote_client):
    def f(client: QdrantBase, **kwargs: Dict[str, Any]) -> List[models.ScoredPoint]:
        return client.discover(
            collection_name=COLLECTION_NAME,
            target=10,
            with_payload=True,
            limit=10,
            using="image",
        )

    compare_client_results(local_client, remote_client, f)


def test_discover_from_another_collection(local_client, remote_client):
    def f(client: QdrantBase, **kwargs: Dict[str, Any]) -> List[models.ScoredPoint]:
        return client.discover(
            collection_name=COLLECTION_NAME,
            target=10,
            context=[models.ContextExamplePair(positive=15, negative=7)],
            with_payload=True,
            limit=10,
            using="image",
            lookup_from=models.LookupLocation(
                collection=secondary_collection_name,
                vector="image",
            ),
        )

    compare_client_results(local_client, remote_client, f)


def test_discover_batch(local_client, remote_client):
    def f(client: QdrantBase, **kwargs: Dict[str, Any]) -> List[List[models.ScoredPoint]]:
        return client.discover_batch(
            collection_name=COLLECTION_NAME,
            requests=[
                models.DiscoverRequest(
                    target=10,
                    context=[models.ContextExamplePair(positive=15, negative=7)],
                    limit=5,
                    using="image",
                ),
                models.DiscoverRequest(
                    target=11,
                    context=[models.ContextExamplePair(positive=15, negative=17)],
                    limit=6,
                    using="image",
                    lookup_from=models.LookupLocation(
                        collection=secondary_collection_name,
                        vector="image",
                    ),
                ),
            ],
        )

    compare_client_results(local_client, remote_client, f)


@pytest.mark.parametrize("filter", [one_random_filter_please() for _ in range(10)])
def test_discover_with_filters(local_client, remote_client, filter: models.Filter):
    def f(client: QdrantBase, **kwargs: Dict[str, Any]) -> List[models.ScoredPoint]:
        return client.discover(
            collection_name=COLLECTION_NAME,
            target=10,
            context=[models.ContextExamplePair(positive=15, negative=7)],
            limit=15,
            using="image",
            query_filter=filter,
        )


@pytest.mark.parametrize("filter", [one_random_filter_please() for _ in range(10)])
def test_context_with_filters(local_client, remote_client, filter: models.Filter):
    def f(client: QdrantBase, **kwargs: Dict[str, Any]) -> List[models.ScoredPoint]:
        return client.discover(
            collection_name=COLLECTION_NAME,
            context=[models.ContextExamplePair(positive=15, negative=7)],
            limit=1000,
            using="image",
            query_filter=filter,
        )

    compare_client_results(local_client, remote_client, f, is_context_search=True)
