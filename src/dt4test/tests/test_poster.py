import os.path
import shutil
import time

from ..resource.poster import Poster


class TestPoster:

    def test_register(self):
        poster = Poster()
        res = poster.register()
        assert res["status"] == "success"
        assert len(poster.get_role_ids()) == 1

    def test_get_env(self):
        poster = Poster()
        res = poster.get_env()
        assert res["data"]

    def test_get_target(self):
        poster = Poster()
        res = poster.get_targets('poster')
        assert res["role_ids"] == ""

    def test_drop_command(self):
        poster = Poster()
        res = poster.drop_command("12345")
        assert res["status"] == "success"

    def test_clear_commands(self):
        poster = Poster()
        res = poster.clear_commands()
        assert res["status"] == "success"

    def test_upload_download_file(self):
        poster = Poster()
        pwd = os.getcwd()
        os.mkdir("test_src")
        os.mkdir("test_des")
        test_src_dir = os.path.join(pwd, "test_src")
        test_des_dir = os.path.join(pwd, "test_des")

        up_file = test_src_dir + "/up_1.sh"
        down_file = test_des_dir + "/down_1.sh"
        file_info = 'echo "Test ..."'

        with open(up_file, 'w') as wf:
            wf.write(file_info)

        # Test start here
        poster.upload_file('role1', up_file, down_file)
        #poster.download_file(up_file, down_file)

        time.sleep(6)
        assert (os.path.exists(down_file))
        assert (os.path.exists(test_des_dir + "/up_1.sh"))
        with open(down_file, 'r') as df:
            line = df.readline()
            assert line == file_info

        shutil.rmtree(test_des_dir)
        shutil.rmtree(test_src_dir)


    def test_put_cmd(self):
        poster = Poster()
        poster.put_command('cmd', 'role1', 'sleep 10 ')

