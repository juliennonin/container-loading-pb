import unittest
import container_loading.cargo as clp

class BoxTypeTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(BoxTypeTest, self).__init__(*args, **kwargs)
        self.dim = [1, 5, 7]

    def test_2_orientations(self):
        boxtype = clp.BoxType(self.dim, (0,0,1))
        permutations = [list(box.dim) for box in boxtype.permuted_boxes]
        self.assertEqual(len(permutations), 2)
        self.assertIn([1, 5, 7], permutations)
        self.assertIn([5, 1, 7], permutations)

    def test_vertical_x(self):
        boxtype = clp.BoxType(self.dim, (1,0,1))
        permutations = [list(box.dim) for box in boxtype.permuted_boxes]
        self.assertEqual(len(permutations), 4)
        self.assertIn([1, 5, 7], permutations)
        self.assertIn([5, 1, 7], permutations)
        self.assertIn([7, 5, 1], permutations)
        self.assertIn([5, 7, 1], permutations)

    def test_vertical_y(self):
        boxtype = clp.BoxType(self.dim, (0,1,1))
        permutations = [list(box.dim) for box in boxtype.permuted_boxes]
        self.assertEqual(len(permutations), 4)
        self.assertIn([1, 5, 7], permutations)
        self.assertIn([5, 1, 7], permutations)
        self.assertIn([1, 7, 5], permutations)
        self.assertIn([7, 1, 5], permutations)

    def test_all_orientations(self):
        boxtype = clp.BoxType(self.dim, (1,1,1))
        permutations = [list(box.dim) for box in boxtype.permuted_boxes]
        self.assertEqual(len(permutations), 6)
        self.assertIn([1, 5, 7], permutations)
        self.assertIn([5, 1, 7], permutations)
        self.assertIn([1, 7, 5], permutations)
        self.assertIn([7, 1, 5], permutations)
        self.assertIn([7, 5, 1], permutations)
        self.assertIn([5, 7, 1], permutations)