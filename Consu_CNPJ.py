import sys
import os
import json
import requests
from PyQt5 import QtWidgets, QtGui, QtCore

USER_DATA_FILE = 'user_data.json'

# Função para carregar dados de usuário
def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, 'r') as file:
        return json.load(file)

# Função para salvar dados de usuário
def save_user_data(user_data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(user_data, file)

user_data = load_user_data()

# Classe para a janela de registro
class RegisterWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Registro')
        self.setWindowIcon(QtGui.QIcon('login.png'))  # Adicione o ícone aqui
        
        layout = QtWidgets.QVBoxLayout()

        self.user_label = QtWidgets.QLabel('Usuário:')
        layout.addWidget(self.user_label)
        
        self.user_input = QtWidgets.QLineEdit()
        layout.addWidget(self.user_input)

        self.pass_label = QtWidgets.QLabel('Senha:')
        layout.addWidget(self.pass_label)

        self.pass_input = QtWidgets.QLineEdit()
        self.pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.pass_input)
        
        self.register_button = QtWidgets.QPushButton('Registrar')
        self.register_button.setStyleSheet('background-color: green; color: white;')
        self.register_button.clicked.connect(self.register_user)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def register_user(self):
        username = self.user_input.text()
        password = self.pass_input.text()
        if username in user_data:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Usuário já existe')
        else:
            user_data[username] = password
            save_user_data(user_data)
            QtWidgets.QMessageBox.information(self, 'Registro', 'Usuário registrado com sucesso!')
            self.close()

# Classe para a janela de login
class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Login')
        self.setWindowIcon(QtGui.QIcon('senha.png'))  # Adicione o ícone aqui

        layout = QtWidgets.QVBoxLayout()

        self.user_label = QtWidgets.QLabel('Usuário:')
        layout.addWidget(self.user_label)
        
        self.user_input = QtWidgets.QLineEdit()
        self.user_input.returnPressed.connect(self.focus_password)
        layout.addWidget(self.user_input)

        self.pass_label = QtWidgets.QLabel('Senha:')
        layout.addWidget(self.pass_label)

        self.pass_input = QtWidgets.QLineEdit()
        self.pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pass_input.returnPressed.connect(self.check_login)
        layout.addWidget(self.pass_input)
        
        self.login_button = QtWidgets.QPushButton('Login')
        self.login_button.setStyleSheet('background-color: blue; color: white;')
        self.login_button.clicked.connect(self.check_login)
        layout.addWidget(self.login_button)

        self.register_button = QtWidgets.QPushButton('Registrar')
        self.register_button.setStyleSheet('background-color: green; color: white;')
        self.register_button.clicked.connect(self.open_register_window)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def focus_password(self):
        self.pass_input.setFocus()

    def open_register_window(self):
        self.register = RegisterWindow()
        self.register.show()

    def check_login(self):
        username = self.user_input.text()
        password = self.pass_input.text()
        if username in user_data and user_data[username] == password:
            self.main = MainWindow(username)
            self.main.show()
            self.close()
        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Usuário ou senha incorretos')

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Buscador de Informações do CNPJ')
        self.setWindowIcon(QtGui.QIcon('CONSULTOR.png'))  # Adicione o ícone aqui

        self.setGeometry(100, 100, 800, 600)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        layout = QtWidgets.QVBoxLayout(central_widget)

        self.search_label = QtWidgets.QLabel('Digite o CNPJ:')
        layout.addWidget(self.search_label)

        search_layout = QtWidgets.QHBoxLayout()

        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setInputMask('00.000.000/0000-00')
        search_layout.addWidget(self.search_input)

        self.search_button = QtWidgets.QPushButton('Buscar')
        self.search_button.setStyleSheet('background-color: red; color: white;')
        self.search_button.clicked.connect(self.search_cnpj)
        search_layout.addWidget(self.search_button)

        layout.addLayout(search_layout)

        self.result_area = QtWidgets.QTextEdit()
        layout.addWidget(self.result_area)

        # Adiciona o usuário logado na barra de status
        self.statusBar().addPermanentWidget(QtWidgets.QLabel(f'Usuário: {self.username}'))
        
        # Adiciona data e hora na barra de status
        self.time_label = QtWidgets.QLabel()
        self.statusBar().addPermanentWidget(self.time_label)
        self.update_time()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def update_time(self):
        current_time = QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.DefaultLocaleLongDate)
        self.time_label.setText(current_time)

    def search_cnpj(self):
        cnpj = self.search_input.text().replace('.', '').replace('/', '').replace('-', '')
        response = requests.get(f'https://www.receitaws.com.br/v1/cnpj/{cnpj}')
        if response.status_code == 200:
            data = response.json()
            self.result_area.setText(f"""
            Última Atualização: {data.get('ultima_atualizacao', 'N/A')}

            CNPJ: {data.get('cnpj', 'N/A')}

            Razão Social: {data.get('nome', 'N/A')}

            Nome Fantasia: {data.get('fantasia', 'N/A')}

            Situação Cadastral: {data.get('situacao', 'N/A')}

            Data da Situação: {data.get('data_situacao', 'N/A')}

            Motivo da Situação: {data.get('motivo_situacao', 'N/A')}

            Data de Abertura: {data.get('abertura', 'N/A')}

            Matriz ou Filial: {data.get('tipo', 'N/A')}

            Natureza Jurídica: {data.get('natureza_juridica', 'N/A')}

            Empresa MEI: {data.get('mei', 'N/A')}

            Data de Opção pelo MEI: {data.get('data_opcao_mei', 'N/A')}

            Capital Social: R$ {data.get('capital_social', 'N/A')}

            Logradouro: {data.get('logradouro', 'N/A')}

            Número: {data.get('numero', 'N/A')}

            Complemento: {data.get('complemento', 'N/A')}

            Bairro: {data.get('bairro', 'N/A')}

            CEP: {data.get('cep', 'N/A')}

            Município: {data.get('municipio', 'N/A')}

            Estado: {data.get('uf', 'N/A')}

            Email: {data.get('email', 'N/A')}

            Telefone: {data.get('telefone', 'N/A')}

            CNAE Principal: {data['atividade_principal'][0]['code']} - {data['atividade_principal'][0]['text']}

            CNAEs Secundários: {', '.join([f"{cnae['code']} - {cnae['text']}" for cnae in data['atividades_secundarias']])}

            Simples: {data.get('simples', 'N/A')}

            Data de Opção pelo Simples: {data.get('data_opcao_simples', 'N/A')}

            Sócios: {', '.join([socio['nome'] for socio in data.get('qsa', [])]) or '-'}
            """)
        else:
            self.result_area.setText('Erro ao buscar CNPJ.')

def main():
    app = QtWidgets.QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
