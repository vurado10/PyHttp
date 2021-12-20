import unittest

import utilities


class RequestBuildersTests(unittest.TestCase):
    def test_urlencoded_body(self):
        body = {"q": "10", "t": "кот/"}

        self.assertEqual("q%3D10%26t%3D%D0%BA%D0%BE%D1%82/",
                         utilities.convert_dict_to_perc_encoding(body))
