import os.path

from ..lib.operating_system import OPSystem


class TestOS:
    def test_zip_file(self):
        with open('a.txt','w') as a:
            a.write("This is a")
        with open('b.txt','w') as b:
            b.write("This is b")

        o_s = OPSystem()
        o_s.zip_file("myzip.zip", 'a.txt', 'b.txt')
        o_s.remove_files("myzip.zip")
        o_s.remove_files('a.txt')
        o_s.remove_files('b.txt')

    def test_zip_dir(self):
        o_s = OPSystem()
        o_s.create_directory("test_dir123")
        o_s.create_file("test_dir123/test_file456.txt", "some content")

        try:
            o_s.zip_file("dir123.zip","test_dir123")
        except RuntimeError:
            assert True
        except:
            print("Some Other Errors ...")
            assert False
        finally:
            o_s.remove_files("test_dir123/test_file456.txt")
            o_s.remove_directory("test_dir123")
            o_s.remove_files("dir123.zip") if os.path.exists("dir123.zip") else None