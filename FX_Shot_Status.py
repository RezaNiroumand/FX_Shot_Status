
from PySide2 import QtCore, QtUiTools, QtWidgets, QtGui
from maya import OpenMayaUI as omu
from shiboken2 import wrapInstance
from base64 import b64decode
import sys, os
sys.path.append("N:/pipeline/external/python/venvs/3.8.10/Lib/site-packages/")
import shotgun_api3
mainObject = omu.MQtUtil.mainWindow()
mayaMainWind = wrapInstance(int(mainObject), QtWidgets.QWidget)


class FX_Status(QtWidgets.QWidget):
    def __init__(self,parent=mayaMainWind):        
        super(FX_Status, self).__init__(parent=parent)
        
        SG_SCRIPT_NAME = "lemoncore"
        SG_SCRIPT_KEY = "bG5oZjF1bnlZanZtdWpudCZxeXRuaXB1ZQ=="
        self.sg = shotgun_api3.Shotgun("https://lemonsky.shotgunstudio.com", SG_SCRIPT_NAME, b64decode(SG_SCRIPT_KEY).decode())                       
        
        if(__name__ == '__main__'):
            self.ui = r"D:\reza_niroumand\Script\shotgrid\FX_Shot_Status\FX_Shot_Status.ui"
        else:
            self.ui = os.path.abspath(os.path.dirname(__file__)+'/FX_Shot_Status.ui')
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('FX Shot Status')
        self.resize(800,800) 
        loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(self.ui)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.theMainWidget = loader.load(ui_file)
        ui_file.close()
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.theMainWidget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        
        self.label_artist_name = self.findChild(QtWidgets.QLabel, "label_artist_name")
        self.label_task_status = self.findChild(QtWidgets.QLabel, "label_task_status")
        self.label_shot_duration = self.findChild(QtWidgets.QLabel, "label_shot_duration")
        self.label_label_os_cfx = self.findChild(QtWidgets.QLabel, "label_os_cfx")
        self.label_fx_global = self.findChild(QtWidgets.QLabel, "label_fx_global")
        self.plainTextEdit_description = self.findChild(QtWidgets.QPlainTextEdit, "plainTextEdit_description")


        
        self.comboBox_Episode = self.findChild(QtWidgets.QComboBox, "comboBox_Episode")
        self.comboBox_Episode.currentIndexChanged.connect(self.fill_comboBox_Shot)
        
        self.comboBox_Shot = self.findChild(QtWidgets.QComboBox, "comboBox_Shot")
        self.comboBox_Shot.setEditable(True)
        completer = QtWidgets.QCompleter()
        completer.setModel(self.comboBox_Shot.model())
        self.comboBox_Shot.setCompleter(completer)
        self.comboBox_Shot.currentIndexChanged.connect(self.fill_comboBox_Task)

        self.comboBox_Task = self.findChild(QtWidgets.QComboBox, "comboBox_Task")

               
        self.pushButton_getTaskData = self.findChild(QtWidgets.QPushButton, "pushButton_getTaskData")
        self.pushButton_getTaskData.clicked.connect(self.get_data)
        
        self.scrollAreaWidgetContents = self.findChild(QtWidgets.QLayout, "verticalLayout_2")

        self.Episode_sg = self.sg.find("Sequence", filters=[["project", "is", {'type': 'Project', 'id': 1367}]], fields=["code", "id","type"])       
        for item in self.Episode_sg:
            self.comboBox_Episode.addItem(item['code'])

        
        

    def fill_comboBox_Shot(self):
        self.comboBox_Shot.clear()
        current_sequence = self.comboBox_Episode.currentText()
        for item in self.Episode_sg:
            if (item['code'])== current_sequence:
                self.current_id = item['id']
        self.Shot_sg = self.sg.find('Shot', filters=[["sg_sequence", "is", {'type': 'Sequence', 'id': self.current_id}],['sg_has_fx','is',True]], fields=['code', 'id', 'open_notes', 'sg_has_fx', 'task'])
        for item in self.Shot_sg:
            self.comboBox_Shot.addItem(item['code'])

        self.fill_comboBox_Task()

    def fill_comboBox_Task(self):
        self.comboBox_Task.clear()
        self.Shot_query_sg = self.sg.find('Shot', filters=[['code', 'is', self.comboBox_Shot.currentText() ]], fields=['id','sg_comp_status','sg_fx_status','sg_layout_status','sg_lighting_status','sg_pri_status','sg_secondary_status','sg_cut_duration','description','sg_fx_global','sg_os_cfx'])
        
                       
        try:
            Task_sg = self.sg.find('Task', filters=[['entity', 'is', {'type':'Shot', 'id':self.Shot_query_sg[0]['id']}]], fields=['content', 'id'])
            for item in Task_sg:
                self.comboBox_Task.addItem(item['content'])
        except:
            pass
   
    
    
    
    def remveLyt(self,layout):
        while layout.count():
            child =layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.remveLyt(child.layout()) 
    
    def get_data(self):
        current_shot = self.comboBox_Shot.currentText()
        for item in self.Shot_sg:
            if (item['code']) == current_shot:
                current_id = item['id']
        #print(current_id)
        current_task = self.comboBox_Task.currentText()
        result = self.sg.find("Task", filters=[['entity', 'is', {'type': 'Shot', 'id': current_id}],['content','is',current_task]], fields=['content', 'open_notes', 'task_assignees'])
        #print(result)
        #print(self.Shot_query_sg)
        id_list=[]
        for item in result[0]['open_notes']:
            #print(item['id'])
            id_list.append(item['id'])

        
        #print(result[0]['open_notes'])        
        if result[0]['open_notes']:

            self.remveLyt(self.scrollAreaWidgetContents)
            for item in id_list:
                note_info = self.sg.note_thread_read(item, entity_fields= None)
                #print(note_info)
                content_data = note_info[0]['content']
                note_date = note_info[0]['created_at']
                note_date = (str(note_date).split(' ')[0])
                self.text_edit_open_notes = QtWidgets.QTextEdit()
                self.text_edit_open_notes.setReadOnly(True)
                self.text_edit_open_notes.setText(note_date+'\n\n'+content_data)
                self.scrollAreaWidgetContents.addWidget(self.text_edit_open_notes)

        
        # print(self.Shot_query_sg)
        if current_task == 'Fx':
            task_value = self.Shot_query_sg[0]['sg_fx_status']
        elif current_task == 'Lay':
            task_value = self.Shot_query_sg[0]['sg_layout_status']
        elif current_task == 'Pri':
            task_value = self.Shot_query_sg[0]['sg_pri_status']
        elif current_task == 'Sec':
            task_value = self.Shot_query_sg[0]['sg_secondary_status']
        elif current_task == 'LGT':
            task_value = self.Shot_query_sg[0]['sg_lighting_status']
        elif current_task == 'Comp':
            task_value = self.Shot_query_sg[0]['sg_comp_status']

        note_desc = self.Shot_query_sg[0]['description']
        self.label_artist_name.setText(result[0]['task_assignees'][0]['name'])
        self.label_task_status.setText(task_value)
        self.label_shot_duration.setText(str(self.Shot_query_sg[0]['sg_cut_duration'])+' Frames')
        self.plainTextEdit_description.setPlainText(note_desc)

        try:
            self.label_label_os_cfx.setText(self.Shot_query_sg[0]['sg_os_cfx'])                   
            self.label_fx_global.setText(self.Shot_query_sg[0]['sg_fx_global'][0]['name'])
        except:
            pass

        # Shot_sg = sg.find('Shot', filters=[["sg_sequence", "is", {'type': 'Sequence', 'id': 1559}]], fields=['code', 'id', 'open_notes', 'sg_has_fx'])

        
        # shot_list_query = sg.find('Shot', filters=[["id", "is", 40250]], fields=['open_notes', 'sg_has_fx'])

        # result = sg.find("Task", filters=[['entity', 'is', {'type': 'Shot', 'id': 40250}]], fields=['content', 'open_notes', 'task_assignees'])



