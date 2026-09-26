def error_responses(*codes: int) -> dict[int, dict[str, str]]:
    descriptions = {
        400: "Invalid business operation",
        401: "Missing or invalid authentication",
        403: "Insufficient permissions",
        404: "Resource not found",
        409: "Conflict with the current resource state",
        422: "Request validation failed",
    }
    return {code: {"description": descriptions[code]} for code in codes}
