import logging

from vbcore import aio
from vbcore.http.gql import GQLClient, GQLClientAIO

ENDPOINT = "https://countries.trevorblades.com/"

QUERY = """
query getContinents {
    continents {
        code
        name
    }
}
"""


def perform(statement, headers=None):
    client = GQLClient(ENDPOINT)
    return client.perform(statement, headers)


async def perform_async(statement, headers=None):
    client = GQLClientAIO(ENDPOINT)
    return await client.perform(statement, headers)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    result = perform(QUERY)
    print(result)

    result = aio.execute(perform_async(QUERY))
    print(result)
