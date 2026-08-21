
import sys
import urllib.request
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QMessageBox, QTabWidget, QDialogButtonBox, QFormLayout, QComboBox,
    QDoubleSpinBox, QSpinBox, QTextEdit
)
from PyQt6.QtGui import QPixmap, QIcon, QFont
from PyQt6.QtCore import Qt, QSize

# --- Mock Data ---
# In a real application, this data would come from a database.
MOCK_PRODUCTS = [
    {
        "id": 1,
        "name": "Modern Wireless Mouse",
        "category": "Electronics",
        "price": 29.99,
        "stock": 150,
        "description": "Ergonomic wireless mouse with 2.4 GHz connectivity and a long-lasting battery.",
        "image_url": "https://placehold.co/100x100/EFEFEF/AAAAAA&text=Mouse"
    },
    {
        "id": 2,
        "name": "Mechanical Keyboard",
        "category": "Electronics",
        "price": 89.99,
        "stock": 75,
        "description": "RGB backlit mechanical keyboard with blue switches for a tactile typing experience.",
        "image_url": "https://placehold.co/100x100/EFEFEF/AAAAAA&text=Keyboard"
    },
    {
        "id": 3,
        "name": "27-inch 4K Monitor",
        "category": "Electronics",
        "price": 349.99,
        "stock": 40,
        "description": "Ultra HD 27-inch monitor with vibrant colors and wide viewing angles.",
        "image_url": "https://placehold.co/100x100/EFEFEF/AAAAAA&text=Monitor"
    },
    {
        "id": 4,
        "name": "Leather Office Chair",
        "category": "Furniture",
        "price": 199.99,
        "stock": 30,
        "description": "Comfortable high-back leather chair with lumbar support and adjustable height.",
        "image_url": "https://placehold.co/100x100/EFEFEF/AAAAAA&text=Chair"
    },
    {
        "id": 5,
        "name": "Standing Desk",
        "category": "Furniture",
        "price": 299.99,
        "stock": 25,
        "description": "Electric height-adjustable standing desk for a healthier work-from-home setup.",
        "image_url": "https://placehold.co/100x100/EFEFEF/AAAAAA&text=Desk"
    },
    {
        "id": 6,
        "name": "Webcam with Microphone",
        "category": "Electronics",
        "price": 59.99,
        "stock": 200,
        "description": "1080p HD webcam with a built-in noise-cancelling microphone for clear video calls.",
        "image_url": "https://placehold.co/100x100/EFEFEF/AAAAAA&text=Webcam"
    }
]

MOCK_ORDERS = [
    {
        "id": 1001,
        "customer": "John Doe",
        "date": "2025-09-28",
        "total": 119.98,
        "status": "Shipped",
        "items": [
            {"product_id": 2, "quantity": 1},
            {"product_id": 1, "quantity": 1}
        ]
    },
    {
        "id": 1002,
        "customer": "Jane Smith",
        "date": "2025-09-29",
        "total": 349.99,
        "status": "Processing",
        "items": [
            {"product_id": 3, "quantity": 1}
        ]
    },
    {
        "id": 1003,
        "customer": "Peter Jones",
        "date": "2025-09-30",
        "total": 559.97,
        "status": "Delivered",
        "items": [
            {"product_id": 4, "quantity": 1},
            {"product_id": 5, "quantity": 1},
            {"product_id": 1, "quantity": 2}
        ]
    },
    {
        "id": 1004,
        "customer": "Emily White",
        "date": "2025-10-01",
        "total": 59.99,
        "status": "Shipped",
        "items": [
            {"product_id": 6, "quantity": 1}
        ]
    }
]

# --- Utility Functions & Resources ---

class ImageCache:
    """A simple cache for QPixmap objects loaded from URLs."""
    def __init__(self):
        self.cache = {}
        self.placeholder = self.create_placeholder_pixmap()

    def create_placeholder_pixmap(self):
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.lightGray)
        return pixmap

    def get_image(self, url):
        if url in self.cache:
            return self.cache[url]
        try:
            data = urllib.request.urlopen(url, timeout=5).read()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            if pixmap.isNull():
                # Handle cases where data is not a valid image
                pixmap = self.placeholder
        except Exception as e:
            print(f"Error loading image from {url}: {e}")
            pixmap = self.placeholder
        
        self.cache[url] = pixmap
        return pixmap

# Global image cache instance
IMAGE_CACHE = ImageCache()

# --- Dialogs ---

class ProductDialog(QDialog):
    """Dialog for adding or editing a product."""
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle(f"{'Edit' if product else 'Add'} Product")
        self.setMinimumWidth(400)

        # Layout and Widgets
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit(product["name"] if product else "")
        self.category_input = QComboBox()
        self.category_input.addItems(["Electronics", "Furniture", "Books", "Clothing", "Other"])
        if product:
            self.category_input.setCurrentText(product.get("category", "Other"))

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.0, 9999.99)
        self.price_input.setPrefix("$ ")
        if product:
            self.price_input.setValue(product.get("price", 0.0))

        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 99999)
        if product:
            self.stock_input.setValue(product.get("stock", 0))

        self.description_input = QTextEdit(product["description"] if product else "")
        self.description_input.setFixedHeight(80)
        self.image_url_input = QLineEdit(product["image_url"] if product else "")

        layout.addRow("Name:", self.name_input)
        layout.addRow("Category:", self.category_input)
        layout.addRow("Price:", self.price_input)
        layout.addRow("Stock:", self.stock_input)
        layout.addRow("Description:", self.description_input)
        layout.addRow("Image URL:", self.image_url_input)

        # Dialog Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

    def get_data(self):
        """Returns the data entered in the dialog."""
        return {
            "name": self.name_input.text().strip(),
            "category": self.category_input.currentText(),
            "price": self.price_input.value(),
            "stock": self.stock_input.value(),
            "description": self.description_input.toPlainText().strip(),
            "image_url": self.image_url_input.text().strip()
        }

    def accept(self):
        """Validate input before accepting."""
        if not self.get_data()["name"]:
            QMessageBox.warning(self, "Input Error", "Product name cannot be empty.")
            return
        super().accept()

# --- Main Application Window ---

class EcommerceAdminPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("eCommerce Management System")
        self.setWindowIcon(QIcon(QPixmap(128, 128))) # Placeholder icon
        self.setGeometry(100, 100, 1200, 800)

        # Apply a simple stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border-top: 2px solid #C2C7CB;
            }
            QTabBar::tab {
                background: #E0E0E0;
                border: 1px solid #C4C4C3;
                border-bottom-color: #C2C7CB;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 5px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #FFFFFF;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border-radius: 5px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QTableWidget {
                gridline-color: #d0d0d0;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #E8E8E8;
                padding: 4px;
                border: 1px solid #d0d0d0;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        # Central Tab Widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create tabs
        self.create_dashboard_tab()
        self.create_products_tab()
        self.create_orders_tab()
        
        self.update_dashboard()

    def create_dashboard_tab(self):
        """Sets up the dashboard tab with summary statistics."""
        self.dashboard_tab = QWidget()
        layout = QGridLayout(self.dashboard_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        metric_font = QFont("Arial", 18)
        label_font = QFont("Arial", 12)

        title = QLabel("Dashboard")
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # --- Metrics Widgets ---
        self.total_products_label = QLabel("0")
        self.total_products_label.setFont(metric_font)
        self.total_stock_label = QLabel("0")
        self.total_stock_label.setFont(metric_font)
        self.total_orders_label = QLabel("0")
        self.total_orders_label.setFont(metric_font)
        self.total_revenue_label = QLabel("$0.00")
        self.total_revenue_label.setFont(metric_font)

        # --- Layout ---
        layout.addWidget(title, 0, 0, 1, 4)
        
        def create_metric_box(label_text, metric_widget):
            box = QWidget()
            box.setStyleSheet("background-color: white; border-radius: 8px; padding: 15px;")
            box_layout = QVBoxLayout(box)
            label = QLabel(label_text)
            label.setFont(label_font)
            label.setStyleSheet("color: #555;")
            box_layout.addWidget(label)
            box_layout.addWidget(metric_widget)
            return box

        layout.addWidget(create_metric_box("Total Products", self.total_products_label), 1, 0)
        layout.addWidget(create_metric_box("Total Stock Value", self.total_stock_label), 1, 1)
        layout.addWidget(create_metric_box("Total Orders", self.total_orders_label), 1, 2)
        layout.addWidget(create_metric_box("Total Revenue", self.total_revenue_label), 1, 3)
        
        layout.setRowStretch(2, 1) # Add stretch to push metrics to the top

        self.tabs.addTab(self.dashboard_tab, "Dashboard")

    def create_products_tab(self):
        """Sets up the product management tab."""
        self.products_tab = QWidget()
        layout = QVBoxLayout(self.products_tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Toolbar
        toolbar = QHBoxLayout()
        add_button = QPushButton("Add Product")
        add_button.clicked.connect(self.add_product)
        edit_button = QPushButton("Edit Product")
        edit_button.clicked.connect(self.edit_product)
        delete_button = QPushButton("Delete Product")
        delete_button.setStyleSheet("background-color: #DC3545;")
        delete_button.clicked.connect(self.delete_product)
        
        toolbar.addWidget(add_button)
        toolbar.addWidget(edit_button)
        toolbar.addWidget(delete_button)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Product Table
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(6)
        self.product_table.setHorizontalHeaderLabels(["Image", "ID", "Name", "Category", "Price", "Stock"])
        self.product_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.product_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.product_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.setIconSize(QSize(100, 100))

        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.product_table.setColumnWidth(0, 110)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.product_table)
        self.tabs.addTab(self.products_tab, "Products")
        self.populate_product_table()

    def create_orders_tab(self):
        """Sets up the order viewing tab."""
        self.orders_tab = QWidget()
        layout = QVBoxLayout(self.orders_tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Order Table
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(5)
        self.order_table.setHorizontalHeaderLabels(["Order ID", "Customer", "Date", "Status", "Total"])
        self.order_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.order_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.order_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.order_table.verticalHeader().setVisible(False)

        header = self.order_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.order_table)
        self.tabs.addTab(self.orders_tab, "Orders")
        self.populate_order_table()

    # --- Data Population and UI Updates ---

    def update_dashboard(self):
        """Recalculates and updates the dashboard metrics."""
        total_products = len(MOCK_PRODUCTS)
        total_stock_value = sum(p['price'] * p['stock'] for p in MOCK_PRODUCTS)
        total_orders = len(MOCK_ORDERS)
        total_revenue = sum(o['total'] for o in MOCK_ORDERS if o['status'] in ['Shipped', 'Delivered'])

        self.total_products_label.setText(f"{total_products}")
        self.total_stock_label.setText(f"${total_stock_value:,.2f}")
        self.total_orders_label.setText(f"{total_orders}")
        self.total_revenue_label.setText(f"${total_revenue:,.2f}")

    def populate_product_table(self):
        """Fills the product table with data from MOCK_PRODUCTS."""
        self.product_table.setRowCount(0) # Clear table
        self.product_table.setSortingEnabled(False)

        for row, product in enumerate(MOCK_PRODUCTS):
            self.product_table.insertRow(row)
            self.product_table.setRowHeight(row, 110)

            # Image Item
            pixmap = IMAGE_CACHE.get_image(product["image_url"])
            icon_item = QTableWidgetItem()
            icon_item.setIcon(QIcon(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)))
            icon_item.setData(Qt.ItemDataRole.UserRole, product["id"]) # Store ID
            self.product_table.setItem(row, 0, icon_item)

            # Text Items
            id_item = QTableWidgetItem(str(product["id"]))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            name_item = QTableWidgetItem(product["name"])
            category_item = QTableWidgetItem(product["category"])
            price_item = QTableWidgetItem(f"${product['price']:.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            stock_item = QTableWidgetItem(str(product["stock"]))
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.product_table.setItem(row, 1, id_item)
            self.product_table.setItem(row, 2, name_item)
            self.product_table.setItem(row, 3, category_item)
            self.product_table.setItem(row, 4, price_item)
            self.product_table.setItem(row, 5, stock_item)
        
        self.product_table.setSortingEnabled(True)

    def populate_order_table(self):
        """Fills the order table with data from MOCK_ORDERS."""
        self.order_table.setRowCount(0)
        self.order_table.setSortingEnabled(False)

        for row, order in enumerate(MOCK_ORDERS):
            self.order_table.insertRow(row)
            
            id_item = QTableWidgetItem(str(order["id"]))
            customer_item = QTableWidgetItem(order["customer"])
            date_item = QTableWidgetItem(order["date"])
            status_item = QTableWidgetItem(order["status"])
            total_item = QTableWidgetItem(f"${order['total']:.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            # Color code status
            if order["status"] == "Shipped":
                status_item.setForeground(Qt.GlobalColor.blue)
            elif order["status"] == "Delivered":
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif order["status"] == "Processing":
                status_item.setForeground(Qt.GlobalColor.darkYellow)

            self.order_table.setItem(row, 0, id_item)
            self.order_table.setItem(row, 1, customer_item)
            self.order_table.setItem(row, 2, date_item)
            self.order_table.setItem(row, 3, status_item)
            self.order_table.setItem(row, 4, total_item)
        
        self.order_table.setSortingEnabled(True)

    # --- Product CRUD Operations ---

    def add_product(self):
        """Opens a dialog to add a new product."""
        dialog = ProductDialog(parent=self)
        if dialog.exec():
            new_data = dialog.get_data()
            # Find the max ID and add 1 for the new product
            new_id = max(p['id'] for p in MOCK_PRODUCTS) + 1 if MOCK_PRODUCTS else 1
            new_product = {"id": new_id, **new_data}
            MOCK_PRODUCTS.append(new_product)
            
            # Refresh UI
            self.populate_product_table()
            self.update_dashboard()
            QMessageBox.information(self, "Success", f"Product '{new_product['name']}' added successfully.")

    def edit_product(self):
        """Opens a dialog to edit the selected product."""
        selected_row = self.product_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a product to edit.")
            return

        product_id = int(self.product_table.item(selected_row, 1).text())
        product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)

        if not product:
            QMessageBox.critical(self, "Error", "Could not find the selected product.")
            return

        dialog = ProductDialog(product=product, parent=self)
        if dialog.exec():
            updated_data = dialog.get_data()
            product.update(updated_data)
            
            # Refresh UI
            self.populate_product_table()
            self.update_dashboard()
            QMessageBox.information(self, "Success", f"Product '{product['name']}' updated successfully.")

    def delete_product(self):
        """Deletes the selected product after confirmation."""
        selected_row = self.product_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a product to delete.")
            return

        product_id = int(self.product_table.item(selected_row, 1).text())
        product_name = self.product_table.item(selected_row, 2).text()

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the product '{product_name}' (ID: {product_id})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            global MOCK_PRODUCTS
            MOCK_PRODUCTS = [p for p in MOCK_PRODUCTS if p["id"] != product_id]
            
            # Refresh UI
            self.populate_product_table()
            self.update_dashboard()
            QMessageBox.information(self, "Success", f"Product '{product_name}' deleted.")

# --- Main Execution ---

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EcommerceAdminPanel()
    window.show()
    sys.exit(app.exec())
