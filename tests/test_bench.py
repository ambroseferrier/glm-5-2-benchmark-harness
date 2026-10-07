import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]))
from bench.run import record
class T(unittest.TestCase):
 def test_shape(self):self.assertEqual(record('local','glm-5.2',0,0,True)['success'],True)
if __name__=='__main__':unittest.main()
