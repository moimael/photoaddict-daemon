#!/usr/bin/env python3

import os
import sys
import time
from datetime import datetime
import io

import ssdeep
import gphoto2 as gp
import couchdb
import pyudev
from PIL import Image
import imagehash

from camera_connector import CameraConnector
from picture import Picture


def sync_pictures(cam_con, db, camera_files):
    for path in camera_files:
        print(path)
        duplicate = False
        info = cam_con.get_camera_file_info(path)
        folder, name = os.path.split(path)
        camera_file = cam_con.get_camera_file(folder, name)[1]
        file_data = bytearray(info.file.size)
        count = gp.gp_file_slurp(camera_file, file_data)
        phash = imagehash.phash(Image.open(io.BytesIO(file_data)))

        map_fun = '''function(doc) {
                emit(doc.phash, null);
            }'''
        for row in db.query(map_fun):
            db_hash = imagehash.hex_to_hash(row.key)
            if db_hash == phash:
                duplicate = True
                print('Duplicate detected')
                break
            if db_hash - phash < 5 and db_hash - phash > 0:
                print(db_hash - phash)
                print('Possible duplicate detected')

        if not duplicate:
            created = datetime.fromtimestamp(info.file.mtime)
            picture = Picture(name=name, width=info.file.width, height=info.file.height, mime_type=info.file.type, size=info.file.size,
                              phash=phash, created=created)
            picture.store(db)
            db.put_attachment(picture, io.BytesIO(file_data).getvalue(), name, info.file.type)
        del camera_file, file_data


def import_pictures(action, device):
    cam_con = CameraConnector()

    couch = couchdb.Server()
    try:
        db = couch['photo-library']
    except couchdb.ResourceNotFound:
        db = couch.create('photo-library')

    if device.action == "add" and device.device_type == "usb_device":
        # print(device.action, device.device_type, device.subsystem)
        try:
            cameras = cam_con.get_cameras()
        except gp.GPhoto2Error as ex:
            if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                pass
            # some other error we can't handle here
            raise

        camera = cam_con.connect(cameras[0])
        # text = cam_con.get_summary()
        try:
            camera_files = cam_con.get_camera_files()
        except gp.GPhoto2Error as ex:
            return 0

        if not camera_files:
            print('No files found')
        else:
            sync_pictures(cam_con, db, camera_files)


def main():
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('usb')

    observer = pyudev.MonitorObserver(monitor, import_pictures)
    observer.start()

    while True:
        time.sleep(2000)

    return 0

if __name__ == "__main__":
    sys.exit(main())
