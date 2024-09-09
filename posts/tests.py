from django.test import TestCase
from .ai_moderation import check_for_donation_request

class AIDetectionTestCase(TestCase):
    def test_donation_request_detection(self):
        donation_text = "I need help raising $1000 for a new prosthetic leg. Please donate if you can."
        result = check_for_donation_request(donation_text)
        print(f"Donation text: {donation_text}")
        print(f"Detection result: {result}")
        self.assertTrue(result)

    def test_regular_post_detection(self):
        regular_text = "I just got a new prosthetic arm and it's amazing! I can do so much more now."
        result = check_for_donation_request(regular_text)
        print(f"Regular text: {regular_text}")
        print(f"Detection result: {result}")
        self.assertFalse(result)

    def test_edge_case_detection(self):
        edge_case_text = "I'm so grateful for the support I've received. It's helped me so much!"
        result = check_for_donation_request(edge_case_text)
        print(f"Edge case text: {edge_case_text}")
        print(f"Detection result: {result}")
        # The expected result here depends on how the AI interprets this text
        print(f"Note: This test may need adjustment based on AI behavior")