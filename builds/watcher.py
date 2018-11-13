import sys
import time
import logging
from termcolor import colored
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class WatchEventHandler(FileSystemEventHandler):
    def __init__(self, files_list, build_callback_object):
        self.files_list = files_list
        self.build = build_callback_object
        super(WatchEventHandler, self).__init__()
    
    def on_moved(self, event):
        super(WatchEventHandler, self).on_moved(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Moved %s: from %s to %s", what, event.src_path,
                     event.dest_path)

    def on_created(self, event):
        super(WatchEventHandler, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Created %s: %s", what, event.src_path)

    def on_deleted(self, event):
        super(WatchEventHandler, self).on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Deleted %s: %s", what, event.src_path)

    def on_modified(self, event):
        super(WatchEventHandler, self).on_modified(event)

        what = 'directory' if event.is_directory else 'file'
        logging.info("Modified %s: %s", what, event.src_path)
        if event.src_path in self.files_list and self.build is not None:
            self.build.Run(event.src_path)

class Watcher:
    """The watcher class that will watch over changes in the CWD if any of the project files change, and will build them."""
    def __init__(self, files_list, build_callback_object):
        self.handler = WatchEventHandler(files_list, build_callback_object)
        

    def Start(self):
        print(colored('Started to watch the current directory.', 'green'))
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        event_handler = self.handler
        observer = Observer()
        observer.schedule(event_handler, '.', recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
        print(colored('\rStopped watching the current directory.', 'yellow'))
