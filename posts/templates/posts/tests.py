from django.test import TestCase
from .ai_moderation import check_for_donation_request

class AIDetectionTestCase(TestCase):
    def test_donation_request_detection(self):
        donation_text = "I need help raising $1000 for a new prosthetic leg. Please donate if you can."
        self.assertTrue(check_for_donation_request(donation_text))

    def test_regular_post_detection(self):
        regular_text = "I just got a new prosthetic arm and it's amazing! I can do so much more now."
        self.assertFalse(check_for_donation_request(regular_text))