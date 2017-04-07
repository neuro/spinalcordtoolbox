import sys
import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore



class HeaderCore(object):

    def __init__(self):
        self.define_lb_status()
        self.define_lb_warning()
        self.define_layout_header()

    def define_lb_status(self):
        self.lb_status = QtGui.QLabel('Label Alerte')
        self.lb_status.setContentsMargins(10, 10, 10, 0)
        self.lb_status.setAlignment(QtCore.Qt.AlignCenter)

    def define_lb_warning(self):
        self.lb_warning = QtGui.QLabel('Label Warning')
        self.lb_warning.setContentsMargins(10, 10, 10, 10)
        self.lb_warning.setAlignment(QtCore.Qt.AlignCenter)

    def define_layout_header(self):
        self.layout_header = QtGui.QVBoxLayout()
        self.layout_header.setAlignment(QtCore.Qt.AlignTop)
        self.layout_header.addWidget(self.lb_status)
        self.layout_header.addWidget(self.lb_warning)

class Header(HeaderCore):

    def update_lb(self,key):
        if(key=='start'):
            self.lb_status.setText('header.lb_status')
            self.lb_warning.setText('header.lb_warning')
            self.lb_warning.setStyleSheet("color:red")

class MainPannelCore(object):

    def __init__(self):
        self.layout_global=QtGui.QVBoxLayout()
        self.layout_option_settings = QtGui.QHBoxLayout()
        self.layout_central = QtGui.QHBoxLayout()

    def add_main_anat_view(self):
        layout_anat_view = QtGui.QVBoxLayout()
        layout_anat_view.setAlignment(QtCore.Qt.AlignTop)
        layout_anat_view.setAlignment(QtCore.Qt.AlignRight)

        layout_anat_view.addWidget(self.create_image())
        self.layout_central.addLayout(layout_anat_view)

    def add_secondary_anat_view(self):
        layout_anat_view = QtGui.QVBoxLayout()
        layout_anat_view.setAlignment(QtCore.Qt.AlignTop)
        layout_anat_view.setAlignment(QtCore.Qt.AlignRight)

        layout_anat_view.addWidget(self.create_image())
        self.layout_central.addLayout(layout_anat_view)

    def add_controller_pannel(self):
        pass

    def create_image(self):
        image_label = QtGui.QLabel('')
        image_test = QtGui.QPixmap('/home/apopov/Documents/dev/sct/image_test.jpg')
        image_label.setPixmap(image_test)
        return image_label

    def merge_layouts(self):
        self.layout_global.addLayout(self.layout_option_settings)
        self.layout_global.addLayout(self.layout_central)

    def add_option_settings(self):
        pass

class MainPannel(MainPannelCore):

    def add_controller_pannel(self):
        layout_controller = QtGui.QHBoxLayout()
        layout_controller.setAlignment(QtCore.Qt.AlignTop)
        layout_controller.setAlignment(QtCore.Qt.AlignLeft)

        s1=QtGui.QSlider()
        s2 = QtGui.QSlider()

        layout_controller.addWidget(s1)
        layout_controller.addWidget(s2)
        self.layout_central.addLayout(layout_controller)


    def __init__(self):
        super(MainPannel, self).__init__()

        """ Left Pannel"""
        #self.add_secondary_anat_view()
        self.add_controller_pannel()
        """ Right Pannel"""
        self.add_main_anat_view()

        self.merge_layouts()

class ControlButtonsCore(object):
    def __init__(self):
        self.layout_buttons=QtGui.QHBoxLayout()
        self.layout_buttons.setAlignment(QtCore.Qt.AlignRight)
        self.add_help_button()
        self.add_undo_button()
        self.add_save_and_quit_button()

    def add_save_and_quit_button(self):
        btn_save_and_quit=QtGui.QPushButton('Save & Quit')
        self.layout_buttons.addWidget(btn_save_and_quit)

    def add_undo_button(self):
        self.btn_undo=QtGui.QPushButton('Undo')
        self.layout_buttons.addWidget(self.btn_undo)

    def add_help_button(self):
        self.btn_help=QtGui.QPushButton('Help')
        self.layout_buttons.addWidget(self.btn_help)


def launch_main_window():
    system = QtGui.QApplication(sys.argv)
    w = QtGui.QWidget()
    w.resize(740, 850)
    w.setWindowTitle('Hello world')
    w.show()
    return (w,system)

def add_layout_main(w):
    layout_main=QtGui.QVBoxLayout()
    layout_main.setAlignment(QtCore.Qt.AlignTop)
    w.setLayout(layout_main)
    return layout_main

def add_header(w):
    header=Header()
    w.addLayout(header.layout_header)
    header.update_lb('start')
    return(header)

def add_main_pannel(layout_main):
    main_pannel=MainPannel()
    layout_main.addLayout(main_pannel.layout_global)
    return  main_pannel

def add_control_buttons(layout_main):
    control_buttons=ControlButtonsCore()
    layout_main.addLayout(control_buttons.layout_buttons)
    return control_buttons



(window,system) = launch_main_window()

layout_main = add_layout_main(window)
header = add_header(layout_main)
main_pannel = add_main_pannel(layout_main)
control_buttons=add_control_buttons(layout_main)



window.setLayout(layout_main)


sys.exit(system.exec_())

