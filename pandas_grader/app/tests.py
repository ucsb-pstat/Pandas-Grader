from .models import Assignment
from django.test import TestCase
import requests
import json
import uuid

# Create your tests here.
class APICheck(TestCase):
    def test_grade_batch(self):
        resp = self.client.get("/api/ok/v3/grade/batch")
        self.assertEqual(resp.status_code, requests.codes.method_not_allowed)

        resp = self.client.post(
            "/api/ok/v3/grade/batch",
            json.dumps({"subm_ids": ["1111"]}),
            content_type="application/json",
        )

    def test_get_file(self):
        new_object = Assignment(name="test", file="test_file")
        new_object.save()

        resp = self.client.get(f"/get_file?id={new_object.assignment_id}")
        print(resp)

        resp = self.client.get(f"/get_file?id={uuid.uuid4()}")
        print(resp)
