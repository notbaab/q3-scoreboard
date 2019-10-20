import argparse
import subprocess
import shutil
import filecmp
import os
import os.path
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class GameManager(object):

    """Class that starts, stops and parses events for a game.
    """

    def __init__(self, patch_dir, game_baseq3, server_exe):
        super(GameManager, self).__init__()
        self.patch_dir = patch_dir
        self.game_baseq3 = game_baseq3
        self.server_exe = server_exe
        self.server_thread = None

    def _copy_patch_data(self):
        patch_files = [os.path.join(self.patch_dir, f)
                       for f in os.listdir(self.patch_dir)]
        # baseq3_files = os.listdir(self.baseq3_files)

        for f in patch_files:
            name = os.path.basename(f)
            dst = os.path.join(self.game_baseq3, name)
            if not os.path.exists(dst):
                logger.info("Copying %s to %s", f, dst)
                shutil.copyfile(f, dst)
                continue

            # exists, check if the file is the same and we need to copy it
            # shallow can probably be true since the chances that os.stat
            # is exactly the same but different is very low, but
            # since os.stat will mostly return false, most comparions won't
            # even read the files
            if not filecmp.cmp(f, dst, shallow=False):
                logger.info("Copying %s to %s", f, dst)
                shutil.copyfile(f, dst)
                continue
            logger.info("%s and %s are the same, not copying", f, dst)

    def start(self):
        """Doesn't block when the server starts,
        """
        self._copy_patch_data()
        self._start_server_process()

        lines_read = 0
        while lines_read < 130:
            # newline comes from the output
            print(self._read_line_from_game(), end="")
            lines_read += 1

    def _block_on_server(self):
        """Block the the game process. Useful for debugging and development
        but shouldn't be needed in a game score server situation
        """
        self.game_process.communicate()

    def stop(self):
        self.game_process.terminate()

    def _start_server_process(self):
        self.game_process = subprocess.Popen([self.server_exe, "+exec",
                                              "server.cfg"],
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT)

    def _read_line_from_game(self):
        """Can thrown an exception if there is no line ready
        """
        return self.game_process.stdout.readline().decode("utf-8")


# headless test
if __name__ == '__main__':
    p = argparse.ArgumentParser("Start a ioquake3 server")
    p.add_argument("patch_dir", help="location of the baseq3 data"
                   "that we want to patch_dir in. Anything in this folder is "
                   "copied to the game_baseq3")
    p.add_argument("game_baseq3", help="The baseq3 directory. The "
                   "patch_dir is copied to this directory")
    p.add_argument("server_exe", help="The path the executable to run"
                   " the server")
    args = p.parse_args()
    game = GameManager(args.patch_dir, args.game_baseq3,
                       args.server_exe)
    game.start()
    game.stop()

    game._block_on_server()
    print("exiting")
