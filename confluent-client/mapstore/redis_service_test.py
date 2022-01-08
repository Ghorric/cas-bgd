import unittest
from mapstore.redis_service import *

class RedisServiceTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = create_redis_client()

    def setUp(self):
        self.mk01 = 'mk1'
        self.mk02 = 'mk2'
        self.keys = [self.mk01, self.mk02]
        self.m01 = {"k01": "v01"}
        self.m02 = {"k02": "v02"}

    def tearDown(self):
        for k in self.keys:
            self.client.delete(k)

    def test_put_entry_should(self):
        put_map_if_missing(self.client, self.mk01, lambda k: self.m01)
        self.assertEqual(self.m01, get_map(self.client, self.mk01))

    def test_call_put_twice_should_not_replace_map(self):
        put_map_if_missing(self.client, self.mk01, lambda k: self.m01)
        put_map_if_missing(self.client, self.mk01, lambda k: self.m02)
        self.assertEqual(self.m01, get_map(self.client, self.mk01))

    def test_call_put_twice_but_should_call_collectedpostproc_once(self):
        put_map_if_missing(self.client, self.mk01, lambda k: self.m01,
                           lambda pk, pv: self.assertEqual(self.m01, pv))
        put_map_if_missing(self.client, self.mk01, lambda k: self.m02,
                           lambda pk, pv: self.assertRaises('Should NOT be called'))

    def test_call_put_twice_but_should_call_ignorebecauseexists_once(self):
        put_map_if_missing(self.client, self.mk01, lambda k: self.m01,
                           lambda pk, pv: None,
                           lambda ik: self.assertRaises('Should NOT be called'))
        put_map_if_missing(self.client, self.mk01, lambda k: self.assertRaises('Should NOT be called'),
                           lambda pk, pv: self.assertRaises('Should NOT be called'),
                           lambda ik: self.assertEqual(self.mk01, ik))


if __name__ == '__main__':
    unittest.main()
