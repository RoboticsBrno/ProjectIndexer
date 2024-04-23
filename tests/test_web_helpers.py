from unittest import TestCase

from src.web_helpers import fix_readme_relative_images


class Test(TestCase):
    def test_fix_readme_relative_images_absolute(self):
        self._test_fix_readme_relative_images_helper(
            "Foo asd ![image](/docs/media/elks.png)",
            "Foo asd ![image](https://raw.githubusercontent.com/RoboticsBrno/RB3206-ELKS/main/docs/media/elks.png)",
        )

    def test_fix_readme_relative_images_relative(self):
        self._test_fix_readme_relative_images_helper(
            "Foo asd ![image](./docs/media/elks.png)",
            "Foo asd ![image](https://raw.githubusercontent.com/RoboticsBrno/RB3206-ELKS/main/docs/media/elks.png)",
        )

    def test_fix_readme_relative_images_html(self):
        self._test_fix_readme_relative_images_helper(
            "Foo asd <img src=\"./docs/media/elks.png\">",
            "Foo asd <img src=\"https://raw.githubusercontent.com/RoboticsBrno/RB3206-ELKS/main/docs/media/elks.png\">",
        )

    # TODO Rename this here and in `test_fix_readme_relative_images_absolute`, `test_fix_readme_relative_images_relative` and `test_fix_readme_relative_images_html`
    def _test_fix_readme_relative_images_helper(self, test_context, expected_result):
        res = fix_readme_relative_images(
            test_context, "RoboticsBrno/RB3206-ELKS", "main"
        )
        self.assertEqual(res, expected_result)

