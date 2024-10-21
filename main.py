import sys
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QListWidget, QListWidgetItem,
                             QLineEdit)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from geopy.geocoders import Nominatim

def geocode_address(address):
    geolocator = Nominatim(user_agent="healthcare_finder")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None

def search_places_osm(lat, lon, radius, place_type):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    node["amenity"="{place_type}"](around:{radius},{lat},{lon});
    out;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    return data['elements']


def get_pharmacy_details(pharmacy):
    details = {
        'name': pharmacy.get('tags', {}).get('name', 'Brak nazwy'),
        'opening_hours': pharmacy.get('tags', {}).get('opening_hours', 'Brak informacji'),
        'phone': pharmacy.get('tags', {}).get('phone', 'Brak informacji'),
        'website': pharmacy.get('tags', {}).get('website', 'Brak informacji'),
    }
    details['opening_hours'] = translate_opening_hours(details['opening_hours'])

    return details

def translate_opening_hours(hours):
    # TUTAJ #
    translations = {
        'Mo': 'Pon',
        'Tues': 'Wt',
        'Tu': 'Wt',
        'We': 'Śr',
        'Wed': 'Śr',
        'thursday': 'Czw',
        'Fr': 'Pt',
        'Sa': 'Sob',
        'Su': 'Niedz',
    }

    for english, polish in translations.items():
        hours = hours.replace(english, polish)  # Zamiana angielskich nazw na polskie
    return hours


class HealthcareFinderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Znajdź Aptekę")
        self.setGeometry(300, 300, 1000, 600)

        main_layout = QVBoxLayout()
        self.title_label = QLabel("Znajdź Aptekę", self)
        self.title_label.setFont(QFont('Arial', 18, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label = QLabel("Wpisz twój adres zamieszkania", self)
        self.subtitle_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.subtitle_label.setAlignment(Qt.AlignCenter)

        # Pole do wpisania adresu
        self.address_input = QLineEdit()
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)
        main_layout.addWidget(self.address_input)

        self.result_list = QListWidget()
        self.result_list.setFont(QFont('Arial', 12))
        main_layout.addWidget(self.result_list)

        self.search_button = QPushButton("Szukaj Aptek")
        self.search_button.setFont(QFont('Arial', 12))
        main_layout.addWidget(self.search_button)

        self.search_button.clicked.connect(self.search_places)

        self.setLayout(main_layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLineEdit { 
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                font-size: 19px;
                font-weight: bold;
            }
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
            }
        """)

    def search_places(self):
        self.result_list.clear()
        address = self.address_input.text()
        location = geocode_address(address)
        print(location)
        if location:
            lat, lon = location
            pharmacies = search_places_osm(lat, lon, 2000, "pharmacy")

            if pharmacies:
                for pharmacy in pharmacies:
                    details = get_pharmacy_details(pharmacy)

                    name_item = QListWidgetItem(f"Apteka {details['name']}")
                    name_item.setFont(QFont('Arial', 18, QFont.Bold))
                    self.result_list.addItem(name_item)

                    details_label = QLabel(self)
                    details_label.setText(f"""
                                           <b>Godziny otwarcia:</b> {details['opening_hours']}
                                           <b>Telefon:</b> {details['phone']}
                                           <b>Strona:</b> <a href='{details['website']}'>{details['website']}</a>
                                       """)
                    details_label.setFont(QFont('Arial', 13))
                    details_label.setOpenExternalLinks(True)
                    details_label.setWordWrap(True)

                    list_item = QListWidgetItem(self.result_list)
                    self.result_list.addItem(list_item)
                    self.result_list.setItemWidget(list_item, details_label)
            else:
                self.result_list.addItem("Nie znaleziono aptek.")
        else:
            self.result_list.addItem("Nie można uzyskać lokalizacji.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HealthcareFinderApp()
    window.show()
    sys.exit(app.exec_())
