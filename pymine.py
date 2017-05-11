import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QMessageBox, QDialog
import os
#templates
import main
import add
#end
import mcrcon
from time import gmtime, strftime, sleep

class MainWindow(QtWidgets.QMainWindow):        

    rcon = None
    ip_server = None
    enable_features_status = False
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = main.Ui_MainWindow()
        self.ui.setupUi(self)
        
        if os.path.isfile('./servers'):
            with open('./servers', 'r') as file:
                lines = file.readlines()
                for line in lines:                
                    self.ui.comboBox.addItems([self.tr(line.strip())])
                    file.close()        
            
        self.ui.pushButton.clicked.connect(self.add_modal)
        self.ui.pushButton_2.clicked.connect(self.connect_rcon)
        self.ui.pushButton_5.clicked.connect(self.weather_clear)
        self.ui.pushButton_14.clicked.connect(self.set_all_creative)
        self.ui.pushButton_15.clicked.connect(self.set_all_survival)
        self.ui.pushButton_3.clicked.connect(self.delete_server)
        
        
    def weather_clear(self) :
        self.run_command('weather clear')
        self.ui.plainTextEdit.appendPlainText('['+strftime("%Y-%m-%d %H:%M:%S", gmtime())+']Погода теперь ясная')
        return
    
    def give_10_xp(self) :        
        player = self.get_given_player()
        if player == None:
            return
        self.run_command('xp 10 '+self.get_given_player())
        self.ui.plainTextEdit.appendPlainText('['+strftime("%Y-%m-%d %H:%M:%S", gmtime())+']Выдано 10 опыта игроку '+self.get_given_player())
        return

    def give_creative(self) :        
        player = self.get_given_player()
        if player == None:
            return
        self.run_command('gamemode 1 '+self.get_given_player())
        self.ui.plainTextEdit.appendPlainText('['+strftime("%Y-%m-%d %H:%M:%S", gmtime())+']Выдан креатив игроку '+self.get_given_player())
        return

    def ungive_creative(self) :        
        player = self.get_given_player()
        if player == None:
            return
        self.run_command('gamemode 0 '+self.get_given_player())
        self.ui.plainTextEdit.appendPlainText('['+strftime("%Y-%m-%d %H:%M:%S", gmtime())+']Убран креатив у игрока '+self.get_given_player())
        return

    def give_ban(self) :        
        player = self.get_given_player()
        if player == None:
            return
        self.run_command('ban '+self.get_given_player())
        self.ui.plainTextEdit.appendPlainText('['+strftime("%Y-%m-%d %H:%M:%S", gmtime())+']Забанен игрок '+self.get_given_player())
        return

    def ungive_ban(self) :        
        player = self.get_given_player()
        if player == None:
            return
        self.run_command('pardon '+self.get_given_player())
        self.ui.plainTextEdit.appendPlainText('['+strftime("%Y-%m-%d %H:%M:%S", gmtime())+']Разбанен игрок '+self.get_given_player())
        return
    
    def give_admin(self) :        
        player = self.get_given_player()
        if player == None:
            return
        self.run_command('op '+self.get_given_player())
        self.ui.plainTextEdit.appendPlainText('['+strftime("%Y-%m-%d %H:%M:%S", gmtime())+']Выданы права оператора игроку '+self.get_given_player())
        return

    def ungive_admin(self) :        
        player = self.get_given_player()
        if player == None:
            return
        self.run_command('deop '+self.get_given_player())
        self.ui.plainTextEdit.appendPlainText('['+strftime("%Y-%m-%d %H:%M:%S", gmtime())+']Убраны права оператора у игрока '+self.get_given_player())
        return
    
    def kick_player(self) :        
        player = self.get_given_player()
        if player == None:
            return
        self.run_command('kick '+self.get_given_player())
        self.ui.plainTextEdit.appendPlainText('['+strftime("%Y-%m-%d %H:%M:%S", gmtime())+']Кикнут игрок '+self.get_given_player())
        return
    
    def get_given_player(self) :
        player = str(self.ui.comboBox_2.currentText())
        if player == '':
            self.error_modal('Игрок не выбран', 'Ошибка')
            return
        return player   
            
    def set_all_creative(self):
        self.run_command('gamemode creative @a')
        self.ui.plainTextEdit.appendPlainText('['+strftime("%Y-%m-%d %H:%M:%S", gmtime())+']Включен режим креатива')
        return

    def set_all_survival(self):
        self.run_command('gamemode survival @a')
        self.ui.plainTextEdit.appendPlainText('['+strftime("%Y-%m-%d %H:%M:%S", gmtime())+']Включен режим выживания')   
        return
        
        
    def add_modal(self):
        modal = AddServer(self)
        modal.exec_()
        
    def delete_server(self) :
        curr_server = str(self.ui.comboBox.currentText())
        self.ui.comboBox.removeItem(self.ui.comboBox.currentIndex())
        if os.path.isfile('./servers'):
            
            
            with open('./servers', 'r') as file:
                lines = file.readlines()
                
                output = []
                for line in lines:
                    if not curr_server in line:
                        output.append(line)
                file.close()
                with open('./servers', 'w') as file:
                    file.writelines(output)
                    file.close()                             
        return
        
    def connect_rcon(self, new=False) :               
        if self.rcon == None or new == False:                       
            server_data = str(self.ui.comboBox.currentText()).split(':')        
            if len(server_data) < 3:
                self.error_modal('Проверьте правильность настроек сервера.', 'Не хватает данных')
                return            
        
            try:
                self.rcon = mcrcon.MCRcon(server_data[0],int(server_data[1]),server_data[2])
                self.ui.plainTextEdit.appendPlainText('['+strftime("%Y-%m-%d %H:%M:%S", gmtime())+']Подключено к ' + server_data[0]) 
                self.ip_server = server_data[0]
                self.init_players()                
                self.enable_features()
                t1.start()   
            except Exception as err:
                self.ui.plainTextEdit.appendPlainText('['+strftime("%Y-%m-%d %H:%M:%S", gmtime())+']Ошибка подключения к ' + server_data[0])
                self.error_modal('Ошибка подключения', 'Ошибка')
                return            
        else:                               
            self.init_players()
            #print(self.rcon.test())
        
    def init_players(self) :
        players = self.run_command('list')
        players = players.split(':')
        if(len(players) >= 2):            
            self.ui.comboBox_2.clear()
            players = players[1].split(',')
            for p in players:
                self.ui.comboBox_2.addItems([self.tr(p.strip())])
        else:
            self.ui.label.setText('На сервере нет игроков')
        return
    
                
    def run_command(self, command) :
        msg = self.rcon.send(command)
        return msg
    
    def error_modal(self, message, title):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()
        
    def refresh_connect(self) : 
        self.connect_rcon(True)
        
    def enable_features(self) :
        if self.enable_features_status == False:
            self.enable_features_status = True
            self.ui.pushButton_5.setEnabled(True)
            self.ui.pushButton_14.setEnabled(True)
            self.ui.pushButton_15.setEnabled(True)
            self.ui.tab_2.setEnabled(True)
            
            self.ui.pushButton_6.clicked.connect(self.give_10_xp)
            self.ui.pushButton_7.clicked.connect(self.give_creative)
            self.ui.pushButton_8.clicked.connect(self.ungive_creative)
            self.ui.pushButton_9.clicked.connect(self.give_ban)
            self.ui.pushButton_10.clicked.connect(self.ungive_ban)
            self.ui.pushButton_11.clicked.connect(self.give_admin)
            self.ui.pushButton_12.clicked.connect(self.ungive_admin)
            self.ui.pushButton_13.clicked.connect(self.kick_player)
                
class AddServer(QtWidgets.QDialog) :
    def __init__(self, parent):
        super(AddServer, self).__init__(parent)
        self.ui = add.Ui_Dialog()
        self.ui.setupUi(self)
        
        self.ui.pushButton.clicked.connect(self.add_item)
        
    def add_item(self):
        server_address = self.ui.lineEdit.text()
        server_password = self.ui.lineEdit_2.text()
        with open('./servers', 'a') as file:
            file.write(server_address + ':' + server_password + '\n')
            file.close()
        self.parent().ui.comboBox.addItems([self.tr(server_address)+':'+self.tr(server_password)])
        self.close()
                
class Tasks(QtCore.QThread): 
    def run(self):
        i = 0
        while True:
            my_mainWindow.refresh_connect()
            print(i)
            i = i + 1
            sleep(3)

app = QtWidgets.QApplication(sys.argv)

my_mainWindow = MainWindow()
t1 = Tasks()
my_mainWindow.show()

sys.exit(app.exec_())
