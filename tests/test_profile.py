import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


profile = module("profile", "scripts/render_profile.py")
avatar = module("avatar", "scripts/make_avatar.py")


class ProfileTests(unittest.TestCase):
    def test_svg_escapes_portrait_and_handles_empty_counts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "assets").mkdir()
            (root / "assets" / "avatar.txt").write_text("&<>\n", encoding="utf-8")
            with patch.object(profile, "ROOT", root):
                svg = profile.render()
        ET.fromstring(svg)
        self.assertIn("&amp;&lt;&gt;", svg)
        self.assertIn("WoYun520@github", svg)
        self.assertIn("Repos:", svg)

    def test_stats_include_every_public_repository_page(self):
        page_one = [{"stargazers_count": 2}] * 100
        page_two = [{"stargazers_count": 3}]
        with patch.object(profile, "api_json", side_effect=[
            {"public_repos": 101, "followers": 7}, page_one, page_two,
        ]) as api:
            self.assertEqual(profile.public_stats(), {"repos": 101, "stars": 203, "followers": 7})
        self.assertEqual(api.call_count, 3)

    def test_avatar_uses_local_image_and_fits_card(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "avatar.png"
            image = Image.new("RGB", (100, 100), "white")
            for x in range(50):
                for y in range(100):
                    image.putpixel((x, y), (0, 0, 0))
            image.save(path)
            lines = avatar.convert(path)
        self.assertEqual(len(lines), 38)
        self.assertTrue(all(len(line) <= 58 for line in lines))
        self.assertTrue(any("@" in line for line in lines))


if __name__ == "__main__":
    unittest.main()
