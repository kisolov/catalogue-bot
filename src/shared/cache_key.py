def universal_cache_key(func, namespace: str, request, response, *args, **kwargs):
    path = request.url.path

    query = "&".join(
        f"{key}={value}" for key, value in sorted(request.query_params.multi_items())
    )

    return f"{namespace}:{path}:{query or 'no_query'}"
