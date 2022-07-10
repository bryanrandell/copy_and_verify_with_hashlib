
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog, QMessageBox, QComboBox, QProgressDialog, QProgressBar, QCheckBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
import sys
import os
import hashlib
import shutil
from module.md5_check import create_md5_values, compare_two_dict_md5, copy_files_from_selected_folder

class ProgressBar(QProgressDialog):
    def __init__(self, parent=None):
        super(ProgressBar, self).__init__(parent)
        self.setWindowTitle("Progress")
        self.setLabelText("Copying...")
        self.setCancelButton(None)
        self.setRange(0, 100)
        self.setValue(0)
        self.show()
        self.setModal(True)
        self.setMinimumDuration(0)
        self.setAutoClose(False)
        self.setAutoReset(False)
        self.setValue(0)
        self.setValue(100)
        self.close()

"""a class thread to monitor the progress of copy files"""
class CopyThread(QThread):
    signal_progress = pyqtSignal(int)
    # signal_finished = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.src_size = 0
        self.dest_size = 0
        self.copy_percentage = 0
        self.src = None
        self.dest = None

    def set_src_and_dest(self, src, dest):
        self.src = src
        self.dest = dest

    def run(self):
        self.progress_bar = ProgressBar()
        self.progress_bar.setValue(self.copy_percentage)
        self.progress_bar.show()
        self.src_size = sum([os.path.getsize(os.path.join(root, file)) for root, dir, files in os.walk(self.src) for file in files])
        print("Copy Thread Start")
        print("Src size {}".format(self.src_size))
        while self.copy_percentage < 100:
            self.progress_bar.setValue(self.copy_percentage)

            self.dest_size = sum([os.path.getsize(os.path.join(root, file)) for root, dir, files in os.walk(self.dest) for file in files])
            print(self.dest_size)
            # except FileNotFoundError:
            #     print("File not found")
            #     self.sleep(1)
            #     continue
            print("copy_percentage: {}".format(self.copy_percentage))

            self.copy_percentage = int(self.dest_size / self.src_size * 100)
            self.signal_progress.emit(self.copy_percentage)
            self.sleep(1)


        # self.signal_finished.emit("Copy Finished")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hash Copy View")
        self.setGeometry(300, 300, 400, 600)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.copy_files_from_selected_folder = copy_files_from_selected_folder
        self.compare_two_dict_md5 = compare_two_dict_md5
        self.create_md5_values = create_md5_values
        self.source_path = "/Users/bryanrandell/Desktop/CC_B_UNIT"
        self.destination_path = "/Users/bryanrandell/Documents"
        self.copy_state = None
        self.dict_hash_values_compare = {}
        self.thread_progress = CopyThread()
        self.thread_progress.signal_progress.connect(self.progress_bar_update)

        self.combo_box_hasher_selection = QComboBox()
        self.combo_box_hasher_selection.addItem("MD5")
        self.combo_box_hasher_selection.addItem("SHA1")
        self.combo_box_hasher_selection.addItem("SHA256")
        self.combo_box_hasher_selection.addItem("SHA512")
        self.main_layout.addWidget(self.combo_box_hasher_selection)


        self.source_path_label = QLabel("Source Path:")
        self.source_path_line_edit = QLineEdit()
        self.source_path_line_edit.setPlaceholderText("Select Source")
        self.source_path_line_edit.setReadOnly(True)
        self.main_layout.addWidget(self.source_path_label)
        self.main_layout.addWidget(self.source_path_line_edit)

        self.destination_path_label = QLabel("Destination Path:")
        self.destination_path_line_edit = QLineEdit()
        self.destination_path_line_edit.setPlaceholderText("Select Destination")
        self.destination_path_line_edit.setReadOnly(True)
        self.main_layout.addWidget(self.destination_path_label)
        self.main_layout.addWidget(self.destination_path_line_edit)

        self.button_select_source = QPushButton("Select Source")
        self.button_select_source.setStyleSheet("background-color: #00aa00")
        self.button_select_source.clicked.connect(self.select_source)
        self.main_layout.addWidget(self.button_select_source)

        self.button_select_destination = QPushButton("Select Destination")
        self.button_select_destination.clicked.connect(self.select_destination)
        self.button_select_destination.setStyleSheet("background-color: #aa0060")
        self.main_layout.addWidget(self.button_select_destination)

        self.button_copy = QPushButton("Copy and Verify")
        self.button_copy.clicked.connect(self.copy_and_verify)
        self.button_copy.setStyleSheet("background-color: #0055aa")
        self.main_layout.addWidget(self.button_copy)

        # connect the signal of progress bar
        self.progress_bar_copy = QProgressBar()
        self.progress_bar_copy.setValue(0)
        self.progress_bar_copy.setMaximum(100)
        self.main_layout.addWidget(self.progress_bar_copy)



    def progress_bar_update(self, value):
        self.progress_bar_copy.setValue(value)

    def select_source(self):
        self.source_path = QFileDialog.getExistingDirectory(self, "Select Source")
        self.source_path_line_edit.setText(self.source_path)

    def select_destination(self):
        self.destination_path = QFileDialog.getExistingDirectory(self, "Select Destination")
        self.destination_path_line_edit.setText(self.destination_path)

    def copy_and_verify(self):
        if self.source_path == "" or self.destination_path == "":
            QMessageBox.warning(self, "Warning", "Please select source and destination path")
        else:
            destination_path_and_file_name = os.path.join(self.destination_path, os.path.basename(self.source_path))
            if os.path.exists(destination_path_and_file_name):
                QMessageBox.warning(self, "Warning", "Destination path already exists")
            else:
                self.thread_progress.set_src_and_dest(self.source_path, destination_path_and_file_name)
                self.thread_progress.start()

                self.copy_state = self.copy_files_from_selected_folder(self.source_path, destination_path_and_file_name)

                if self.copy_state == "Copy Successful":
                    md5_source, md5_destination = self.create_md5_values(self.source_path,
                                                                         destination_path_and_file_name,
                                                                         self.combo_box_hasher_selection.currentText().lower())
                    self.dict_hash_values_compare = self.compare_two_dict_md5(md5_source, md5_destination)
                    print(self.dict_hash_values_compare)
                    if "Different" in self.dict_hash_values_compare:
                        self.copy_failed_list = [k for k, v in self.dict_hash_values_compare.items() if v == "Different"]
                        QMessageBox.warning(self, "Warning", "Copy Failed Different Hash Values\n" + str(self.copy_failed_list))
                    elif "Not Found" in self.dict_hash_values_compare:
                        self.copy_failed_list = [k for k, v in self.dict_hash_values_compare.items() if v == "Not Found"]
                        QMessageBox.warning(self, "Warning", "Copy Failed File not found in destination\n" + str(self.copy_failed_list))
                    else:
                        QMessageBox.information(self, "Information", "Verify Successful")
                else:
                    QMessageBox.warning(self, "Warning", "Copy Failed")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
