import json
from flask import Response
from werkzeug.exceptions import BadRequest

class BadRequestMissingField(BadRequest):
    """
    Bad Request with contextual information on missing fields
    """

    def __init__(self, missing_fields=[]):
        rendered_missing_fields = []
        for missing_field in missing_fields:
            rendered_missing_fields.append({
                "field": missing_field,
                "message": f"Field '{missing_field}' is required."
                })

        json_response = json.dumps(
                {
                    "status_code": self.code,
                    "message": "Invalid request payload",
                    "errors": rendered_missing_fields
                }
            )
        response = Response(json_response,
                            self.code,
                            content_type="application/json")
        super().__init__(response=response)
