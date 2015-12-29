import os

import ssdeep
import gphoto2 as gp


class CameraConnector:
    def __init__(self):
        self.context = gp.Context()
        self.cameras = self.context.camera_autodetect()
        self.camera = None

    def __del__(self):
        if self.camera:
            self.camera.exit(self.context)

    def get_cameras(self):
        self.cameras = self.context.camera_autodetect()
        return self.cameras

    def connect(self, camera):
        name, addr = camera
        self.camera = gp.Camera()
        port_info_list = gp.PortInfoList()
        port_info_list.load()
        idx = port_info_list.lookup_path(addr)
        self.camera.set_port_info(port_info_list[idx])
        self.camera.init(self.context)
        return self.camera

    def get_camera_files(self, path='/'):
        result = []
        # get files
        for name, value in self.camera.folder_list_files(path, self.context):
            result.append(os.path.join(path, name))
        # read folders
        folders = []
        for name, value in self.camera.folder_list_folders(path, self.context):
            folders.append(name)
        # recurse over subfolders
        for name in folders:
            result.extend(self.get_camera_files(os.path.join(path, name)))
        return result

    def get_camera_file_info(self, path):
        folder, name = os.path.split(path)
        return self.camera.file_get_info(folder, name, self.context)

    def get_summary(self):
        return self.camera.get_summary(self.context)

    def get_camera_file(self, folder, name):
        return gp.gp_camera_file_get(self.camera, folder, name, gp.GP_FILE_TYPE_NORMAL, self.context)
