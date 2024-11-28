import unittest
import requests

BASE_URL = "http://localhost:5001"


class TestBeatSheetServiceAPI(unittest.TestCase):
    def setUp(self):
        # Initialize instance attributes for test-wide state
        self.beat_sheet_id = None
        self.beat_id = None
        self.act_id = None

    def test_create_beat_sheet(self):
        payload = {"title": "Test Beat Sheet"}
        response = requests.post(f"{BASE_URL}/beatsheet", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json())
        self.assertIn("title", response.json())
        self.beat_sheet_id = response.json()["id"]

    def test_get_beat_sheet_by_id(self):
        self.test_create_beat_sheet()
        response = requests.get(f"{BASE_URL}/beatsheet/{self.beat_sheet_id}")
        self.assertEqual(response.status_code, 200)

    def test_get_beat_sheet_by_id_not_exist(self):
        response = requests.get(f"{BASE_URL}/beatsheet/{self.beat_sheet_id}")
        self.assertEqual(response.status_code, 404)

    def test_update_beat_sheet(self):
        self.test_create_beat_sheet()
        payload = {"title": "Updated Test Beat Sheet"}
        response = requests.put(f"{BASE_URL}/beatsheet/{self.beat_sheet_id}", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], payload["title"])

    def test_delete_beat_sheet(self):
        self.test_create_beat_sheet()
        response = requests.delete(f"{BASE_URL}/beatsheet/{self.beat_sheet_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["message"], 'Beat sheet deleted successfully')

    def test_get_all_beat_sheet(self):
        self.test_create_beat_sheet()
        response = requests.get(f"{BASE_URL}/beatsheet")
        self.assertEqual(response.status_code, 200)

    def test_add_beat_to_sheet(self):
        self.test_create_beat_sheet()
        payload = {"description": "Test Beat"}
        response = requests.post(f"{BASE_URL}/beatsheet/{self.beat_sheet_id}/beat", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json())
        self.assertIn("description", response.json())
        self.beat_id = response.json()["id"]

    def test_update_beat_in_sheet(self):
        self.test_add_beat_to_sheet()
        payload = {"description": "Updated Test Beat"}
        response = requests.put(f"{BASE_URL}/beatsheet/{self.beat_sheet_id}/beat/{self.beat_id}", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["description"], payload["description"])

    def test_delete_beat_from_sheet(self):
        self.test_add_beat_to_sheet()
        response = requests.delete(f"{BASE_URL}/beatsheet/{self.beat_sheet_id}/beat/{self.beat_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["message"], 'Beat deleted successfully')

    def test_add_act_to_beat(self):
        self.test_add_beat_to_sheet()
        payload = {
            "description": "Test Act",
            "duration": 60,
            "cameraAngle": "Wide Shot"
        }
        response = requests.post(f"{BASE_URL}/beatsheet/{self.beat_sheet_id}/beat/{self.beat_id}/act", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json())
        self.assertIn("description", response.json())
        self.act_id = response.json()["id"]

    def test_update_act_in_beat(self):
        self.test_add_act_to_beat()
        payload = {
            "description": "Updated Test Act",
            "duration": 120,
            "cameraAngle": "Close Up"
        }
        response = requests.put(f"{BASE_URL}/beatsheet/{self.beat_sheet_id}/beat/{self.beat_id}/act/{self.act_id}", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["description"], payload["description"])

    def test_delete_act_from_beat(self):
        self.test_add_act_to_beat()
        response = requests.delete(f"{BASE_URL}/beatsheet/{self.beat_sheet_id}/beat/{self.beat_id}/act/{self.act_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["message"], "Act deleted successfully")

    def test_suggestion_api(self):
        self.test_add_act_to_beat()
        payload = {"beat_sheet_id": self.beat_sheet_id}
        response = requests.post(f"{BASE_URL}/suggestion/next", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("suggestion", response.json())


if __name__ == "__main__":
    unittest.main()
