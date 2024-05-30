from django.http import JsonResponse
from django.shortcuts import render
from moralis import evm_api


def transaction_detail(request):
    api_key = "xHzx2cwQGsXvvouMFrlBxpKJcr7DgOXM3QtbW68ppslb9in51Q99sOMkRy0Zj2sI"

    params = {
        "transaction_hash": "0xaae93882e8a9fe9ff30151853db20e4cd161940757a01744465ab83b751c5875",
        "chain": "eth",
    }

    result = evm_api.transaction.get_transaction(
        api_key=api_key,
        params=params,
    )

    return JsonResponse(result)
