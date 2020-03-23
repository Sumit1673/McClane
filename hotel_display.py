import os

from PyQt5 import QtCore, QtGui, QtWidgets

IMAGE_FOLDER = "./images"


class HotelDisplay(QtWidgets.QMainWindow):
    user_selection_sig = QtCore.pyqtSignal()

    def __init__(self, country=None, city=None):
        super(HotelDisplay, self).__init__()
        self.setFixedWidth(700)
        self.setMinimumHeight(600)
        self.hotel_location = [country, city]
        self.data_to_display = []

        self.setup_ui()

    def __repr__(self):
        return 'HotelDisplay({0.country!r}, {0.city!r})'.format(self)

    @property
    def hotel_info(self):
        return self._hotel_location

    @hotel_info.setter
    def hotel_info(self, hotel_location):
        self._hotel_location = []
        for k in hotel_location:
            if k is not None:
                if isinstance(k, str):
                    self._hotel_location.append(k)
                else:
                    raise TypeError("In valid argument format. Use string")

    def setup_ui(self):
        self.setWindowTitle("Select Hotel")
        self.scrollArea = QtWidgets.QScrollArea(widgetResizable=True)
        self.setCentralWidget(self.scrollArea)
        self.content_widget = QtWidgets.QWidget()
        self.scrollArea.setWidget(self.content_widget)
        self._vlay = QtWidgets.QVBoxLayout(self.content_widget)
        self.frame = QtWidgets.QFrame(self.content_widget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setLineWidth(1)
        self.frame.setMinimumWidth(700)
        self.frame.setMinimumHeight(50)
        self.frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.frame.setStyleSheet("QFrame {background-color: #005500}")
        self.frame_label = QtWidgets.QLabel(self.frame)
        self.frame_label.setMinimumHeight(20)
        self.frame_label.setMinimumWidth(100)
        self.frame_label.setStyleSheet("QLabel {color: white}")
        self.frame_label.setFont(QtGui.QFont("Times", 15, QtGui.QFont.Bold))
        self.frame_label.setText("Showing results")
        self._vlay.addWidget(self.frame)
        self.img_count = 0
        self._timer = QtCore.QTimer(self, interval=1)
        self._timer.timeout.connect(self.on_timeout)
        self._timer.start()
        self.files_it = iter([])

    # The controller should display the hotel names after getting the number of availability from
    # the database

    def display_hotels(self, num_bookings, available_df):
        # construct_data creates a dict which stores the user selections and uses it to
        # display info with the images
        user_selection_dict = self._construct_data(available_df)
        img_folder_path = self.create_img_folder_path()
        self.files_it = iter([os.path.join(img_folder_path, file)
                              for file in os.listdir(img_folder_path)])
        print(user_selection_dict)

    def create_img_folder_path(self):
        import os
        path = IMAGE_FOLDER
        if 0 < len(self.hotel_location) < 4:
            for i in self.hotel_location:
                if i is not None:
                    path = os.path.join(path, i)
            return path
        else:
            print("Less arguments passed")

    def on_timeout(self):
        try:
            self.img_count += 1
            file = next(self.files_it)
            pixmap = QtGui.QPixmap(file)
            pixmap = pixmap.scaled(150, 150, QtCore.Qt.KeepAspectRatio)
            self._add_pixmap(pixmap)
        except StopIteration:
            self._timer.stop()

    def _add_pixmap(self, pixmap):
        if not pixmap.isNull():
            hspacer = QtWidgets.QSpacerItem(120, 40, QtWidgets.QSizePolicy.Minimum,
                                            QtWidgets.QSizePolicy.Expanding)
            img_txt_pb_hlyt = QtWidgets.QHBoxLayout(self.content_widget)
            hotel_details_vlyt = QtWidgets.QVBoxLayout(self.content_widget)
            gb_hotel_details = QtWidgets.QGroupBox(self.content_widget)
            gb_final = QtWidgets.QGroupBox(self.content_widget)
            select_pb_button = QtWidgets.QPushButton(self.content_widget)

            # Creating a label to add an image over it
            image_label = QtWidgets.QLabel(pixmap=pixmap)

            # Adding the image to the horizontal layout, which will be aligned horizontally with
            # the push button and the hotel details
            img_txt_pb_hlyt.addWidget(image_label)

            # Creating an area to show the details for the hotels, vertically layout
            for hotel_data in self.hotel_location:
                label_city = QtWidgets.QLabel(self.content_widget)
                label_city.setText(hotel_data)
                label_hotel_name = QtWidgets.QLabel(self.content_widget)
                label_hotel_name.setText("Radisson")
                label_city = QtWidgets.QLabel(self.content_widget)
                label_city.setText("City")
                # Adding all the text labels into the vertical layout
                hotel_details_vlyt.addWidget(label_city)
                hotel_details_vlyt.addWidget(label_hotel_name)
            # Adding the layout having hotels details to the group box to be further added to another layout
            # We need a widget to be added to the layout, not a layout to layout. Code will throw erro.
            gb_hotel_details.setLayout(hotel_details_vlyt)

            # Push button for selection and its connecting slot
            select_pb_button.setText("Select")
            select_pb_button.clicked.connect(lambda: self.display_hotel(label_hotel_name.text(),
                                                                        label_hotel_name.text()
                                                                        ))
            # Concatenating img hotel_detail and push button horizontally
            img_txt_pb_hlyt.addWidget(gb_hotel_details)
            img_txt_pb_hlyt.addWidget(select_pb_button)
            img_txt_pb_hlyt.addItem(hspacer)
            gb_final.setLayout(img_txt_pb_hlyt)
            self._vlay.addWidget(gb_final)

    def _construct_data(self, available_df):
        city_dict, hotel_dict, room_dict = {}, {}, {}
        hotel_names = available_df['hotel_names']
        for hotel_i in list(hotel_names):
            hotel_df = available_df[(available_df['hotel_names'] == hotel_i)]
            room_types = list(set(hotel_df['room_type']))
            for room_type_i in room_types:
                room_df = available_df[(available_df['room_type'] == room_type_i)
                                       & (available_df['hotel_names'] == hotel_i)]
                price = list(room_df['prices'])
                room_dict[room_type_i] = price
            hotel_dict[hotel_i] = room_dict
        city_dict[self.hotel_location[1]] = hotel_dict
        return city_dict


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = HotelDisplay("Canada", "Montreal")
    rooms = {'single': 200, 'double': 400, 'family': 600}
    w._display_content(rooms)
    w.show()
    sys.exit(app.exec_())
