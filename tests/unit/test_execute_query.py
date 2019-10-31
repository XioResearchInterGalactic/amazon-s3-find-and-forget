import re
from types import SimpleNamespace

import pytest
from mock import patch

from lambdas.src.tasks.execute_query import handler, make_query

pytestmark = [pytest.mark.unit, pytest.mark.task]


@patch("lambdas.src.tasks.execute_query.client")
@patch("lambdas.src.tasks.execute_query.make_query")
def test_it_executes_queries(query_mock, client_mock):
    client_mock.start_query_execution.return_value = {
        "QueryExecutionId": "123"
    }
    query_mock.return_value = "test"

    resp = handler({"QueryData": {}, "Bucket": "mybucket", "Prefix": "my_prefix"}, SimpleNamespace())
    assert "123" == resp
    client_mock.start_query_execution.assert_called_with(QueryString="test", ResultConfiguration={
        'OutputLocation': 's3://mybucket/my_prefix/'
    })


def test_it_generates_query_with_partition():
    resp = make_query({
        "Database": "amazonreviews",
        "Table": "amazon_reviews_parquet",
        "Columns": [{"Column": "customer_id", "Users": ["123456", "456789"]}],
        "Partition": {"Key": "product_category", "Value": "Books"}
    })

    assert "SELECT DISTINCT \"$path\" " \
           "FROM \"amazonreviews\".\"amazon_reviews_parquet\" " \
           "WHERE (customer_id in ('123456', '456789')) " \
           "AND product_category = 'Books'" == re.sub("[\x00-\x20]+", " ", resp.strip())


def test_it_generates_query_without_partition():
    resp = make_query({
        "Database": "amazonreviews",
        "Table": "amazon_reviews_parquet",
        "Columns": [{"Column": "customer_id", "Users": ["123456", "456789"]}]
    })

    assert "SELECT DISTINCT \"$path\" " \
           "FROM \"amazonreviews\".\"amazon_reviews_parquet\" " \
           "WHERE (customer_id in ('123456', '456789'))" == re.sub("[\x00-\x20]+", " ", resp.strip())


def test_it_generates_query_with_multiple_columns():
    resp = make_query({
        "Database": "amazonreviews",
        "Table": "amazon_reviews_parquet",
        "Columns": [
            {"Column": "a", "Users": ["a123456", "b123456"]},
            {"Column": "b", "Users": ["a456789", "b456789"]},
        ]
    })

    assert "SELECT DISTINCT \"$path\" " \
           "FROM \"amazonreviews\".\"amazon_reviews_parquet\" " \
           "WHERE (a in ('a123456', 'b123456') OR b in ('a456789', 'b456789'))" == re.sub("[\x00-\x20]+", " ",
                                                                                        resp.strip())
