"""Zero-cost verification of the two graded integration points.

These mock the network/SDK layer entirely so they can run for free, over and
over, before spending any real API budget. They check against the ACTUAL
documented Parallel response schema (verified against docs.parallel.ai
during the build) so a passing test here means the parsing code is correct,
not just that it doesn't crash.
"""

import unittest
from unittest.mock import MagicMock, patch

from studio import tools  # noqa: F401 -- ensures studio/__init__.py (which imports agent) loads cleanly too


class TestParallelTrendSearch(unittest.TestCase):
    def test_mock_mode_returns_labeled_placeholder(self):
        with patch.object(tools, "MOCK", True):
            result = tools.parallel_trend_search(["anansi trickster comic"], "check interest")
        self.assertTrue(result["mock"])
        self.assertIn("MOCK MODE", result["signal_summary"])

    def test_missing_key_falls_back_to_mock(self):
        with patch.object(tools, "MOCK", False), patch.object(tools, "PARALLEL_API_KEY", ""):
            result = tools.parallel_trend_search(["anansi trickster comic"], "check interest")
        self.assertTrue(result.get("mock"))

    def test_real_response_schema_is_parsed_correctly(self):
        # This is the exact example response shape from docs.parallel.ai/api-reference/search/search
        fake_response = MagicMock()
        fake_response.raise_for_status.return_value = None
        fake_response.json.return_value = {
            "search_id": "search_fcb2b4f3c75e418687bccaa1a8381331",
            "results": [
                {
                    "url": "https://www.example.com",
                    "title": "Sample webpage title",
                    "publish_date": "2024-01-15",
                    "excerpts": ["Sample excerpt 1", "Sample excerpt 2"],
                }
            ],
            "session_id": "session_fcb2b4f3c75e418687bccaa1a8381331",
            "warnings": None,
            "usage": [{"name": "sku_search", "count": 1}],
        }
        with patch.object(tools, "MOCK", False), patch.object(tools, "PARALLEL_API_KEY", "fake-key"), patch(
            "studio.tools.requests.post", return_value=fake_response
        ) as mock_post:
            result = tools.parallel_trend_search(["anansi trickster comic"], "check interest")

        # Confirms the exact URL, header name, and body shape match the real API.
        _, kwargs = mock_post.call_args
        self.assertEqual(mock_post.call_args[0][0], "https://api.parallel.ai/v1/search")
        self.assertEqual(kwargs["headers"]["x-api-key"], "fake-key")
        self.assertIn("search_queries", kwargs["json"])

        self.assertEqual(len(result["results"]), 1)
        self.assertIn("Sample webpage title", result["signal_summary"])
        self.assertIn("Sample excerpt 1", result["signal_summary"])

    def test_network_failure_returns_error_not_crash(self):
        with patch.object(tools, "MOCK", False), patch.object(tools, "PARALLEL_API_KEY", "fake-key"), patch(
            "studio.tools.requests.post", side_effect=ConnectionError("boom")
        ):
            result = tools.parallel_trend_search(["x"], "y")
        self.assertIn("error", result)


class TestGeneratePanelImage(unittest.TestCase):
    def test_mock_mode_writes_placeholder_and_returns_path(self):
        with patch.object(tools, "MOCK", True):
            result = tools.generate_panel_image(1, "a trickster spider in a forest")
        self.assertTrue(result["path"].endswith("panel_01.png"))
        self.assertTrue(result.get("mock"))

    def test_real_call_uses_configured_model_and_saves_image(self):
        fake_image = MagicMock()
        fake_result = MagicMock()
        fake_result.generated_images = [MagicMock(image=fake_image)]
        fake_client = MagicMock()
        fake_client.models.generate_images.return_value = fake_result

        with patch.object(tools, "MOCK", False), patch.object(tools, "GOOGLE_API_KEY", "fake-key"), patch(
            "studio.tools.genai.Client", return_value=fake_client
        ) as mock_client_cls:
            result = tools.generate_panel_image(2, "a wind spirit racing")

        mock_client_cls.assert_called_once_with(api_key="fake-key")
        fake_client.models.generate_images.assert_called_once()
        _, kwargs = fake_client.models.generate_images.call_args
        self.assertEqual(kwargs["model"], tools.IMAGE_MODEL)
        fake_image.save.assert_called_once()
        self.assertTrue(result["path"].endswith("panel_02.png"))

    def test_sdk_failure_returns_error_not_crash(self):
        with patch.object(tools, "MOCK", False), patch.object(tools, "GOOGLE_API_KEY", "fake-key"), patch(
            "studio.tools.genai.Client", side_effect=RuntimeError("boom")
        ):
            result = tools.generate_panel_image(1, "x")
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
