import argparse
import subprocess
import shutil
import filecmp
import os
import os.path
import logging
import threading

from queue import Queue, Empty

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class GMAccessor(object):
    """Class responsible for making the game manager singleton and allowing
    access to it. Extracted out since the GameManager has no reason to be a
    singleton except for we want to access it across requests and this is
    slightly better than a global? Maybe not?
    """
    __game_manager = None
    cleanup_function = None

    @staticmethod
    def game_exists():
        return GMAccessor.__game_manager is not None

    @staticmethod
    def get_instance():
        return GMAccessor.__game_manager

    @staticmethod
    def stop_and_remove_instance():
        GMAccessor.__game_manager.stop()
        GMAccessor.__game_manager = None
        if cleanup_function is not None:
            print("cleaning up")
            cleanup_function()


    @staticmethod
    def create_instance(patch_dir, game_baseq3_dir, server_exe, cleanup_function = None):
        if GMAccessor.game_exists():
            raise Exception("Cannot create two game instances")

        manager = GameManager(patch_dir, game_baseq3_dir, server_exe)
        GMAccessor.__game_manager = manager
        GMAccessor.cleanup_function = cleanup_function

        return GMAccessor.__game_manager


class GameManager(object):

    """Class that starts, stops and parses events for a game.
    """

    def __init__(self, patch_dir, game_baseq3, server_exe):
        super(GameManager, self).__init__()
        self.patch_dir = patch_dir
        self.game_baseq3 = game_baseq3
        self.server_exe = server_exe
        self.server_thread = None
        self.game_output = Queue()

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
        self._output_read_thread = threading.Thread(
            target=self._read_line_into_queue)
        self._output_read_thread.start()

    def _block_on_server(self):
        """Block the the game process. Useful for debugging and development
        but shouldn't be needed in a game score server situation
        """
        self.game_process.communicate()

    def stop(self):
        self.game_process.terminate()

    def _start_server_process(self):
        cmd = [self.server_exe, "+exec", "server.cfg"]
        # stdout is a bunch of gibberish so pipe to dev null. stdin
        # interferes with pdb debug so pipe that to dev null.
        self.game_process = subprocess.Popen(cmd,
                                             stdout=subprocess.DEVNULL,
                                             stdin=subprocess.DEVNULL,
                                             stderr=subprocess.PIPE,
                                             text=True, encoding="utf-8")

    def _read_line_into_queue(self):
        for line in iter(self.game_process.stderr.readline, ''):
            # print(line)
            self.game_output.put(line)


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
