"""
Management Window Module
Comprehensive database management interface for all 15 tables
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QApplication, QStyle,
    QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout, QLabel, QTabWidget,
    QMessageBox, QLineEdit, QComboBox, QTextEdit, QSpinBox, QTimeEdit, QDateEdit
)
from datetime import datetime
import os


class ManagementWindow(QDialog):
    """Comprehensive management window for all database tables"""
    
    # Table definitions with their columns
    TABLE_CONFIGS = {
        'Users': {
            'columns': ['id', 'username', 'gmail', 'role', 'is_active', 'teacher_approval_status', 'created_at', 'last_login'],
            'headers': ['ID', 'Username', 'Email', 'Role', 'Status', 'Approval', 'Created', 'Last Login'],
            'editable': ['role', 'is_active', 'teacher_approval_status'],
            'create_fields': ['username', 'password', 'gmail', 'role']
        },
        'Devices': {
            'columns': ['id', 'device_id', 'user_id', 'ip_address', 'mac_address', 'registered_at', 'last_seen', 'is_active'],
            'headers': ['ID', 'Device ID', 'User ID', 'IP Address', 'MAC Address', 'Registered', 'Last Seen', 'Active'],
            'editable': ['is_active'],
            'create_fields': ['device_id', 'user_id', 'ip_address', 'mac_address']
        },
        'Sessions': {
            'columns': ['id', 'user_id', 'device_id', 'token', 'created_at', 'expires_at', 'is_active'],
            'headers': ['ID', 'User ID', 'Device ID', 'Token', 'Created', 'Expires', 'Active'],
            'editable': ['is_active'],
            'create_fields': ['user_id', 'device_id', 'expires_at']
        },
        'Students': {
            'columns': ['id', 'student_id', 'user_id', 'gmail', 'assigned_mode', 'violation_count', 'is_active', 'created_at'],
            'headers': ['ID', 'Student ID', 'User ID', 'Email', 'Mode', 'Violations', 'Active', 'Created'],
            'editable': ['assigned_mode', 'violation_count', 'is_active'],
            'create_fields': ['student_id', 'user_id', 'gmail', 'assigned_mode']
        },
        'TimeWindows': {
            'columns': ['id', 'student_id', 'day_of_week', 'start_time', 'end_time', 'is_active'],
            'headers': ['ID', 'Student ID', 'Day', 'Start Time', 'End Time', 'Active'],
            'editable': ['day_of_week', 'start_time', 'end_time', 'is_active'],
            'create_fields': ['student_id', 'day_of_week', 'start_time', 'end_time']
        },
        'ModeHistory': {
            'columns': ['id', 'student_id', 'old_mode', 'new_mode', 'changed_by', 'changed_at', 'reason'],
            'headers': ['ID', 'Student ID', 'Old Mode', 'New Mode', 'Changed By', 'Changed At', 'Reason'],
            'editable': ['reason'],
            'create_fields': ['student_id', 'old_mode', 'new_mode', 'changed_by', 'reason']
        },
        'WhitelistDomains': {
            'columns': ['id', 'domain', 'mode', 'description', 'added_by', 'created_at', 'is_active'],
            'headers': ['ID', 'Domain', 'Mode', 'Description', 'Added By', 'Created', 'Active'],
            'editable': ['domain', 'mode', 'description', 'is_active'],
            'create_fields': ['domain', 'mode', 'description']
        },
        'BlacklistDomains': {
            'columns': ['id', 'domain', 'mode', 'reason', 'added_by', 'created_at', 'is_active'],
            'headers': ['ID', 'Domain', 'Mode', 'Reason', 'Added By', 'Created', 'Active'],
            'editable': ['domain', 'mode', 'reason', 'is_active'],
            'create_fields': ['domain', 'mode', 'reason']
        },
        'ActivityLogs': {
            'columns': ['id', 'student_id', 'user_id', 'url', 'domain', 'mode', 'visit_duration', 'visit_start', 'is_allowed'],
            'headers': ['ID', 'Student ID', 'User ID', 'URL', 'Domain', 'Mode', 'Duration', 'Visit Start', 'Allowed'],
            'editable': [],
            'create_fields': ['student_id', 'user_id', 'url', 'domain', 'mode', 'visit_duration']
        },
        'Violations': {
            'columns': ['id', 'student_id', 'user_id', 'violation_type', 'description', 'severity', 'created_at'],
            'headers': ['ID', 'Student ID', 'User ID', 'Type', 'Description', 'Severity', 'Created'],
            'editable': ['severity'],
            'create_fields': ['student_id', 'user_id', 'violation_type', 'description', 'severity']
        },
        'TeacherActions': {
            'columns': ['id', 'teacher_id', 'action_type', 'target_student_id', 'details', 'created_at'],
            'headers': ['ID', 'Teacher ID', 'Action Type', 'Target Student', 'Details', 'Created'],
            'editable': ['details'],
            'create_fields': ['teacher_id', 'action_type', 'target_student_id', 'details']
        },
        'AdminActions': {
            'columns': ['id', 'admin_id', 'action_type', 'target_user_id', 'target_student_id', 'details', 'created_at'],
            'headers': ['ID', 'Admin ID', 'Action Type', 'Target User', 'Target Student', 'Details', 'Created'],
            'editable': ['details'],
            'create_fields': ['admin_id', 'action_type', 'target_user_id', 'target_student_id', 'details']
        },
        'WarningTriggers': {
            'columns': ['id', 'student_id', 'user_id', 'warning_type', 'violation_count', 'resolved', 'created_at'],
            'headers': ['ID', 'Student ID', 'User ID', 'Warning Type', 'Violations', 'Resolved', 'Created'],
            'editable': ['resolved'],
            'create_fields': ['student_id', 'user_id', 'warning_type', 'violation_count']
        },
        'DashboardLogs': {
            'columns': ['id', 'user_id', 'role', 'action', 'endpoint', 'ip_address', 'created_at'],
            'headers': ['ID', 'User ID', 'Role', 'Action', 'Endpoint', 'IP Address', 'Created'],
            'editable': [],
            'create_fields': ['user_id', 'role', 'action', 'endpoint', 'ip_address']
        }
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EduBrowser Management Panel")
        self.setMinimumSize(1600, 1000)
        self.resize(1800, 1100)
        
        # Get auth from parent if available
        if parent and hasattr(parent, 'auth'):
            self.auth = parent.auth
            self.current_user_id = getattr(parent, 'user_id', None)
            self.current_user_role = getattr(parent, 'user_role', None)
        else:
            from authentication import Authentication
            self.auth = Authentication(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "edubrowser")
            )
            self.current_user_id = None
            self.current_user_role = None
        
        # Store table widgets
        self.tables = {}
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header with back button
        header_layout = QHBoxLayout()
        back_btn = QPushButton("← Back to Dashboard")
        back_btn.setToolTip("Return to Dashboard")
        back_btn.clicked.connect(self.back_to_dashboard)
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        title_label = QLabel("Management Panel")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Create tab widget for all tables
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs for all tables
        for table_name in self.TABLE_CONFIGS.keys():
            tab = self.create_table_tab(table_name)
            self.tabs.addTab(tab, table_name)
        
        # Set window icon
        self.setWindowIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        
        # Load initial data for all tables
        self.refresh_all_tables()
    
    def create_table_tab(self, table_name):
        """Create a tab for a specific table"""
        config = self.TABLE_CONFIGS[table_name]
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        if config['create_fields']:
            add_btn = QPushButton("Add")
            add_btn.clicked.connect(lambda checked, t=table_name: self.add_record(t))
            btn_layout.addWidget(add_btn)
        
        if config['editable']:
            edit_btn = QPushButton("Edit Selected")
            edit_btn.clicked.connect(lambda checked, t=table_name: self.edit_record(t))
            btn_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(lambda checked, t=table_name: self.delete_record(t))
        btn_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(lambda checked, t=table_name: self.refresh_table(t))
        btn_layout.addWidget(refresh_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(len(config['headers']))
        table.setHorizontalHeaderLabels(config['headers'])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(table)
        
        # Store table reference
        self.tables[table_name] = table
        
        return tab
    
    def refresh_all_tables(self):
        """Refresh all tables"""
        for table_name in self.TABLE_CONFIGS.keys():
            self.refresh_table(table_name)
    
    def refresh_table(self, table_name):
        """Load data from database into table"""
        config = self.TABLE_CONFIGS[table_name]
        table = self.tables[table_name]
        
        try:
            conn = self.auth._get_conn()
            cursor = conn.cursor()
            
            # Build SELECT query
            columns = ', '.join(config['columns'])
            query = f"SELECT {columns} FROM {table_name} ORDER BY id DESC LIMIT 1000"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            table.setRowCount(len(rows))
            for row_idx, row_data in enumerate(rows):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    table.setItem(row_idx, col_idx, item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load {table_name}: {str(e)}")
    
    def add_record(self, table_name):
        """Add new record to table"""
        config = self.TABLE_CONFIGS[table_name]
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add {table_name} Record")
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)
        
        fields = {}
        for field in config['create_fields']:
            if field == 'password':
                widget = QLineEdit()
                widget.setEchoMode(QLineEdit.EchoMode.Password)
            elif field in ['role', 'mode', 'assigned_mode', 'old_mode', 'new_mode']:
                widget = QComboBox()
                if 'role' in field:
                    widget.addItems(["student", "teacher", "admin", "superadmin"])
                else:
                    widget.addItems(["cached", "study", "restricted", "free"])
            elif field == 'day_of_week':
                widget = QComboBox()
                widget.addItems(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "all"])
            elif field in ['start_time', 'end_time', 'expires_at']:
                widget = QTimeEdit()
                widget.setDisplayFormat("HH:mm:ss")
                if current_value:
                    try:
                        from PyQt6.QtCore import QTime
                        time_parts = str(current_value).split(':')
                        if len(time_parts) >= 2:
                            widget.setTime(QTime(int(time_parts[0]), int(time_parts[1]), int(time_parts[2]) if len(time_parts) > 2 else 0))
                    except:
                        pass
            elif field in ['violation_type', 'action_type', 'warning_type']:
                widget = QComboBox()
                if field == 'violation_type':
                    widget.addItems(["url_blocked", "mode_bypass_attempt", "time_window_violation", "unauthorized_action", "device_mismatch"])
                elif field == 'action_type':
                    if table_name == 'TeacherActions':
                        widget.addItems(["mode_change", "whitelist_add", "whitelist_remove", "view_student", "view_activity", "approve_student"])
                    else:
                        widget.addItems(["user_create", "user_update", "user_delete", "role_change", "teacher_approve", "teacher_reject", "mode_change", "whitelist_manage", "blacklist_manage", "device_revoke", "force_logout"])
                elif field == 'warning_type':
                    widget.addItems(["first_violation", "repeated_violation", "critical_violation", "pattern_detected"])
            elif field == 'severity':
                widget = QComboBox()
                widget.addItems(["low", "medium", "high", "critical"])
            elif field == 'teacher_approval_status':
                widget = QComboBox()
                widget.addItems(["PENDING", "APPROVED", "REJECTED"])
            elif field in ['is_active', 'is_allowed', 'resolved']:
                widget = QComboBox()
                widget.addItems(["1", "0"])
            elif field in ['violation_count']:
                widget = QSpinBox()
                widget.setMinimum(0)
                widget.setMaximum(9999)
            elif field in ['description', 'details', 'reason']:
                widget = QTextEdit()
                widget.setMaximumHeight(100)
            else:
                widget = QLineEdit()
            
            fields[field] = widget
            layout.addRow(field.replace('_', ' ').title() + ":", widget)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Add")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
        
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                conn = self.auth._get_conn()
                cursor = conn.cursor()
                
                # Build INSERT query
                field_names = list(fields.keys())
                if 'added_by' in config['columns'] and 'added_by' not in field_names:
                    field_names.append('added_by')
                
                placeholders = ', '.join(['%s'] * len(field_names))
                field_list = ', '.join(field_names)
                
                values = []
                for field in field_names:
                    if field == 'added_by':
                        values.append(self.current_user_id)
                    elif field in fields:
                        widget = fields[field]
                        if isinstance(widget, QComboBox):
                            values.append(widget.currentText())
                        elif isinstance(widget, QTextEdit):
                            values.append(widget.toPlainText())
                        elif isinstance(widget, QSpinBox):
                            values.append(widget.value())
                        elif isinstance(widget, QTimeEdit):
                            values.append(widget.time().toString("HH:mm:ss"))
                        else:
                            values.append(widget.text())
                    else:
                        values.append(None)
                
                # Handle special cases
                if 'is_active' in config['columns'] and 'is_active' not in field_names:
                    field_list += ', is_active'
                    placeholders += ', %s'
                    values.append(1)
                
                if 'created_at' in config['columns']:
                    field_list += ', created_at'
                    placeholders += ', %s'
                    values.append(datetime.now())
                
                query = f"INSERT INTO {table_name} ({field_list}) VALUES ({placeholders})"
                cursor.execute(query, tuple(values))
                conn.commit()
                cursor.close()
                conn.close()
                
                QMessageBox.information(self, "Success", f"Record added to {table_name} successfully!")
                self.refresh_table(table_name)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add record: {str(e)}")
    
    def edit_record(self, table_name):
        """Edit selected record"""
        config = self.TABLE_CONFIGS[table_name]
        table = self.tables[table_name]
        selected = table.currentRow()
        
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select a record to edit.")
            return
        
        if not config['editable']:
            QMessageBox.information(self, "Info", "This table does not support editing.")
            return
        
        record_id = int(table.item(selected, 0).text())
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit {table_name} Record")
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)
        
        fields = {}
        for field in config['editable']:
            col_idx = config['columns'].index(field)
            current_value = table.item(selected, col_idx).text() if table.item(selected, col_idx) else ""
            
            if field in ['role', 'mode', 'assigned_mode', 'old_mode', 'new_mode']:
                widget = QComboBox()
                if 'role' in field:
                    widget.addItems(["student", "teacher", "admin", "superadmin"])
                else:
                    widget.addItems(["cached", "study", "restricted", "free"])
                widget.setCurrentText(current_value)
            elif field == 'day_of_week':
                widget = QComboBox()
                widget.addItems(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "all"])
                widget.setCurrentText(current_value)
            elif field == 'teacher_approval_status':
                widget = QComboBox()
                widget.addItems(["PENDING", "APPROVED", "REJECTED"])
                # Handle NULL values and case-insensitive matching
                current_val = str(current_value).upper() if current_value else "PENDING"
                if current_val not in ["PENDING", "APPROVED", "REJECTED"]:
                    current_val = "PENDING"
                widget.setCurrentText(current_val)
            elif field in ['is_active', 'is_allowed', 'resolved']:
                widget = QComboBox()
                widget.addItems(["1", "0"])
                widget.setCurrentText(current_value if current_value else "1")
            elif field in ['start_time', 'end_time', 'expires_at']:
                widget = QTimeEdit()
                widget.setDisplayFormat("HH:mm:ss")
                if current_value:
                    try:
                        from PyQt6.QtCore import QTime
                        time_parts = str(current_value).split(':')
                        if len(time_parts) >= 2:
                            widget.setTime(QTime(int(time_parts[0]), int(time_parts[1]), int(time_parts[2]) if len(time_parts) > 2 else 0))
                    except:
                        pass
            elif field == 'severity':
                widget = QComboBox()
                widget.addItems(["low", "medium", "high", "critical"])
                widget.setCurrentText(current_value)
            elif field in ['description', 'details', 'reason']:
                widget = QTextEdit()
                widget.setMaximumHeight(100)
                widget.setPlainText(current_value)
            elif field in ['violation_count']:
                widget = QSpinBox()
                widget.setMinimum(0)
                widget.setMaximum(9999)
                widget.setValue(int(current_value) if current_value else 0)
            else:
                widget = QLineEdit(current_value)
            
            fields[field] = widget
            layout.addRow(field.replace('_', ' ').title() + ":", widget)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
        
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                conn = self.auth._get_conn()
                cursor = conn.cursor()
                
                # Build UPDATE query
                set_clauses = []
                values = []
                for field in config['editable']:
                    widget = fields[field]
                    if isinstance(widget, QComboBox):
                        value = widget.currentText()
                    elif isinstance(widget, QTextEdit):
                        value = widget.toPlainText()
                    elif isinstance(widget, QSpinBox):
                        value = widget.value()
                    elif isinstance(widget, QTimeEdit):
                        value = widget.time().toString("HH:mm:ss")
                    else:
                        value = widget.text()
                    
                    set_clauses.append(f"{field}=%s")
                    values.append(value)
                
                values.append(record_id)
                query = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE id=%s"
                cursor.execute(query, tuple(values))
                conn.commit()
                cursor.close()
                conn.close()
                
                QMessageBox.information(self, "Success", f"Record updated in {table_name} successfully!")
                self.refresh_table(table_name)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update record: {str(e)}")
    
    def delete_record(self, table_name):
        """Delete selected record"""
        table = self.tables[table_name]
        selected = table.currentRow()
        
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select a record to delete.")
            return
        
        record_id = int(table.item(selected, 0).text())
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete this record from {table_name}?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = self.auth._get_conn()
                cursor = conn.cursor()
                
                # Try soft delete first (if is_active column exists)
                config = self.TABLE_CONFIGS[table_name]
                if 'is_active' in config['columns']:
                    cursor.execute(f"UPDATE {table_name} SET is_active=0 WHERE id=%s", (record_id,))
                else:
                    cursor.execute(f"DELETE FROM {table_name} WHERE id=%s", (record_id,))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                QMessageBox.information(self, "Success", f"Record deleted from {table_name} successfully!")
                self.refresh_table(table_name)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete record: {str(e)}")
    
    def back_to_dashboard(self):
        """Close management window and open dashboard"""
        from dashboard_window import DashboardWindow
        parent = self.parent()
        if parent:
            from browser import MainWindow
            if isinstance(parent, MainWindow):
                dashboard_window = DashboardWindow(parent)
                dashboard_window.show()
                self.close()  # Close management window
