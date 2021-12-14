# import unittest
#
# from pyhttp import parse_argumets
#
#
# class MyTestCase(unittest.TestCase):
#     def test_lists_parsing(self):
#         data = ['google.com', '--params', 'count = 2', 'how=to',
#                 '--body', 'bd=db',
#                 '--headers', 'content-Type: text', "--body", "some body=sb"]
#
#         self.assertEqual(
#             dict(url='google.com',
#                  is_secure=False,
#                  output=None,
#                  cookies=None,
#                  timeout=0.0,
#                  method='get',
#                  params=[("count", "2"), ('how', 'to')],
#                  body=[('bd', "db"), ("some body", "sb")],
#                  headers=[('content-Type', 'text')]),
#             parse_argumets(data))
#
#
# if __name__ == '__main__':
#     unittest.main()
