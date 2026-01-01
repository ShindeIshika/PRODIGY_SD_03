import sys
import re
import requests
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox
)

API_URL = "http://localhost:8080"

class ContactApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Contact Manager")
        self.setGeometry(300, 200, 600, 400)

        self.setStyleSheet("""
    QWidget {
        background-color: #f5f7fa;
        font-family: Segoe UI;
        font-size: 14px;
    }

    QLineEdit {
        padding: 8px;
        border-radius: 6px;
        border: 1px solid #ccc;
        background-color: white;
    }

    QLineEdit:focus {
        border: 1px solid #4a90e2;
    }

    QPushButton {
        padding: 8px 16px;
        border-radius: 6px;
        background-color: #4a90e2;
        color: white;
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #357abd;
    }

    QPushButton:pressed {
        background-color: #2d6aa3;
    }

    QTableWidget {
        background-color: white;
        border-radius: 6px;
        gridline-color: #ddd;
    }

    QHeaderView::section {
        background-color: #e6e9ef;
        padding: 6px;
        border: none;
        font-weight: bold;
    }
""")

        layout = QVBoxLayout()

        form = QHBoxLayout()
        self.name = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()

        self.name.setPlaceholderText("Name")
        self.phone.setPlaceholderText("Phone")
        self.email.setPlaceholderText("Email")

        form.addWidget(self.name)
        form.addWidget(self.phone)
        form.addWidget(self.email)

        self.add_btn = QPushButton("Add Contact")
        self.add_btn.clicked.connect(self.add_contact)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Email"])

        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_contact)

        layout.addLayout(form)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.table)
        layout.addWidget(self.delete_btn)

        self.setLayout(layout)
        self.load_contacts()

    def load_contacts(self):
        self.table.setRowCount(0)
        response = requests.get(f"{API_URL}/contacts")
        for row, c in enumerate(response.json()):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(c["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(c["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(c["phone"]))
            self.table.setItem(row, 3, QTableWidgetItem(c["email"]))

    def add_contact(self):
        name = self.name.text().strip()
        phone = self.phone.text().strip()
        email = self.email.text().strip()

        # --- VALIDATIONS ---
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Name cannot be empty.")
            return

        if not phone.isdigit() or len(phone) != 10:
            QMessageBox.warning(self, "Invalid Input", "Phone number must be exactly 10 digits.")
            return

        if "@" not in email or email.startswith("@") or email.endswith("@"):
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid email address.")
            return

        # --- SEND TO BACKEND ---
        data = {
            "name": name,
            "phone": phone,
            "email": email
        }

        try:
            requests.post(f"{API_URL}/add", json=data)
            self.load_contacts()
            self.name.clear()
            self.phone.clear()
            self.email.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add contact:\n{e}")

    def delete_contact(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a contact first")
            return
        contact_id = self.table.item(row, 0).text()
        requests.get(f"{API_URL}/delete?id={contact_id}")
        self.load_contacts()

app = QApplication(sys.argv)
window = ContactApp()
window.show()
sys.exit(app.exec())
