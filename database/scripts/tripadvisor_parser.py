import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
database_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(database_dir)
sys.path.insert(0, project_root)

from database.config.database import SessionLocal
from database.models.models import City, Place, Activity, place_activities

class TripAdvisorDataSeeder:
    
    def __init__(self):
        self.db = SessionLocal()
        self.activity_map = {}
    
    def load_activity_map(self):
        """Создает mapping названий активностей"""
        activities = self.db.query(Activity).all()
        self.activity_map = {activity.name: activity for activity in activities}
    
    def add_all_russian_cities(self):
        """Добавляет все российские города из TripAdvisor"""
        
        russian_cities = [
            # Крупные города
            {"name": "Москва", "lat": 55.7558, "lon": 37.6176},
            {"name": "Санкт-Петербург", "lat": 59.9343, "lon": 30.3351},
            {"name": "Новосибирск", "lat": 55.0084, "lon": 82.9357},
            {"name": "Екатеринбург", "lat": 56.8389, "lon": 60.6057},
            {"name": "Казань", "lat": 55.7964, "lon": 49.1089},
            {"name": "Нижний Новгород", "lat": 56.3269, "lon": 44.0075},
            {"name": "Челябинск", "lat": 55.1644, "lon": 61.4368},
            {"name": "Самара", "lat": 53.2415, "lon": 50.2212},
            {"name": "Омск", "lat": 54.9885, "lon": 73.3242},
            {"name": "Ростов-на-Дону", "lat": 47.2224, "lon": 39.7183},
            {"name": "Уфа", "lat": 54.7355, "lon": 55.9587},
            {"name": "Красноярск", "lat": 56.0153, "lon": 92.8932},
            {"name": "Воронеж", "lat": 51.6755, "lon": 39.2089},
            {"name": "Пермь", "lat": 58.0105, "lon": 56.2502},
            {"name": "Волгоград", "lat": 48.7194, "lon": 44.5018},
            
            # Города Золотого кольца
            {"name": "Владимир", "lat": 56.1290, "lon": 40.4070},
            {"name": "Суздаль", "lat": 56.4274, "lon": 40.4486},
            {"name": "Ярославль", "lat": 57.6261, "lon": 39.8845},
            {"name": "Кострома", "lat": 57.7677, "lon": 40.9264},
            {"name": "Иваново", "lat": 57.0004, "lon": 40.9739},
            {"name": "Сергиев Посад", "lat": 56.3100, "lon": 38.1300},
            {"name": "Переславль-Залесский", "lat": 56.7390, "lon": 38.8560},
            {"name": "Ростов Великий", "lat": 57.1840, "lon": 39.4150},
            
            # Курортные города
            {"name": "Сочи", "lat": 43.5855, "lon": 39.7231},
            {"name": "Адлер", "lat": 43.4350, "lon": 39.9200},
            {"name": "Ялта", "lat": 44.4990, "lon": 34.1630},
            {"name": "Анапа", "lat": 44.8940, "lon": 37.3160},
            {"name": "Геленджик", "lat": 44.5610, "lon": 38.0760},
            {"name": "Кисловодск", "lat": 43.9050, "lon": 42.7150},
            {"name": "Пятигорск", "lat": 44.0480, "lon": 43.0590},
            {"name": "Ессентуки", "lat": 44.0440, "lon": 42.8610},
            
            # Исторические города
            {"name": "Смоленск", "lat": 54.7826, "lon": 32.0453},
            {"name": "Тверь", "lat": 56.8587, "lon": 35.9176},
            {"name": "Тула", "lat": 54.1930, "lon": 37.6170},
            {"name": "Калуга", "lat": 54.5140, "lon": 36.2610},
            {"name": "Великий Новгород", "lat": 58.5256, "lon": 31.2740},
            {"name": "Псков", "lat": 57.8194, "lon": 28.3318},
            {"name": "Мурманск", "lat": 68.9707, "lon": 33.0750},
            {"name": "Архангельск", "lat": 64.5470, "lon": 40.5430},
            
            # Города Сибири и Дальнего Востока
            {"name": "Иркутск", "lat": 52.2864, "lon": 104.2807},
            {"name": "Хабаровск", "lat": 48.4802, "lon": 135.0719},
            {"name": "Владивосток", "lat": 43.1155, "lon": 131.8855},
            {"name": "Кемерово", "lat": 55.3547, "lon": 86.0870},
            {"name": "Тюмень", "lat": 57.1522, "lon": 65.5272},
            {"name": "Барнаул", "lat": 53.3470, "lon": 83.7790},
            {"name": "Новокузнецк", "lat": 53.7557, "lon": 87.1099},
            {"name": "Томск", "lat": 56.4846, "lon": 84.9476},
            {"name": "Оренбург", "lat": 51.7682, "lon": 55.0960},
            {"name": "Калининград", "lat": 54.7104, "lon": 20.4522},
            
            # Дополнительные популярные города
            {"name": "Липецк", "lat": 52.6088, "lon": 39.5992},
            {"name": "Пенза", "lat": 53.2007, "lon": 45.0046},
            {"name": "Астрахань", "lat": 46.3497, "lon": 48.0408},
            {"name": "Махачкала", "lat": 42.9849, "lon": 47.5047},
            {"name": "Тольятти", "lat": 53.5088, "lon": 49.4192},
            {"name": "Киров", "lat": 58.6035, "lon": 49.6680},
            {"name": "Чебоксары", "lat": 56.1463, "lon": 47.2511},
            {"name": "Ульяновск", "lat": 54.3142, "lon": 48.4031},
            {"name": "Ижевск", "lat": 56.8527, "lon": 53.2115},
            {"name": "Краснодар", "lat": 45.0355, "lon": 38.9750},
            {"name": "Саратов", "lat": 51.5924, "lon": 45.9608},
            {"name": "Волжский", "lat": 48.7858, "lon": 44.7797},
            {"name": "Якутск", "lat": 62.0273, "lon": 129.7319},
            {"name": "Ставрополь", "lat": 45.0445, "lon": 41.9691},
            {"name": "Белгород", "lat": 50.5953, "lon": 36.5873},
            {"name": "Курск", "lat": 51.7304, "lon": 36.1926},
            {"name": "Орёл", "lat": 52.9703, "lon": 36.0635},
            {"name": "Брянск", "lat": 53.2436, "lon": 34.3634},
            {"name": "Владикавказ", "lat": 43.0246, "lon": 44.6818},
            {"name": "Грозный", "lat": 43.3180, "lon": 45.6882},
            {"name": "Нальчик", "lat": 43.4853, "lon": 43.6071},
            {"name": "Петрозаводск", "lat": 61.7849, "lon": 34.3469},
            {"name": "Сыктывкар", "lat": 61.6688, "lon": 50.8361},
            {"name": "Йошкар-Ола", "lat": 56.6320, "lon": 47.8959},
            {"name": "Саранск", "lat": 54.1870, "lon": 45.1839},
            {"name": "Ханты-Мансийск", "lat": 61.0032, "lon": 69.0189},
            {"name": "Новый Уренгой", "lat": 66.0833, "lon": 76.6333},
            {"name": "Норильск", "lat": 69.3531, "lon": 88.2027},
            {"name": "Магадан", "lat": 59.5612, "lon": 150.8301},
            {"name": "Южно-Сахалинск", "lat": 46.9591, "lon": 142.7380},
            {"name": "Благовещенск", "lat": 50.2907, "lon": 127.5272},
            {"name": "Комсомольск-на-Амуре", "lat": 50.5503, "lon": 137.0100},
        ]
        
        for city_data in russian_cities:
            city = self.db.query(City).filter(City.name == city_data["name"]).first()
            if not city:
                city = City(
                    name=city_data["name"],
                    country_code="RU",
                    latitude=city_data["lat"],
                    longitude=city_data["lon"]
                )
                self.db.add(city)
                print(f"Добавлен город: {city_data['name']}")
        
        self.db.commit()
        print(f"Всего добавлено городов: {len(russian_cities)}")
    
    def _add_places_to_city(self, city_name, places_data, category_mapping):
        """Добавляет места для конкретного города"""
        city = self.db.query(City).filter(City.name == city_name).first()
        if not city:
            print(f"Город {city_name} не найден")
            return
        
        added_count = 0
        for place_data in places_data:
            # Создаем уникальный tripadvisor_id
            tripadvisor_id = f"{city_name.lower().replace(' ', '_')}_{place_data['name'].lower().replace(' ', '_')}"
            
            # Проверяем, существует ли уже место
            existing = self.db.query(Place).filter(
                Place.tripadvisor_id == tripadvisor_id
            ).first()
            
            if existing:
                continue
            
            # Создаем новое место
            place = Place(
                name=place_data["name"],
                description=f"Популярное место в {city_name}",
                address=f"{city_name}, Россия",
                city_id=city.id,
                latitude=place_data["lat"],
                longitude=place_data["lon"],
                rating=place_data["rating"],
                tripadvisor_id=tripadvisor_id,
                tripadvisor_rating=place_data["rating"],
                tripadvisor_reviews_count=place_data["reviews"],
                primary_category=place_data["categories"][0]
            )
            
            self.db.add(place)
            self.db.flush()
            
            # Добавляем связи с активностями
            for category in place_data["categories"]:
                activity_name = category_mapping.get(category)
                if activity_name and activity_name in self.activity_map:
                    stmt = place_activities.insert().values(
                        place_id=place.id,
                        activity_id=self.activity_map[activity_name].id
                    )
                    self.db.execute(stmt)
            
            added_count += 1
        
        self.db.commit()
        print(f"Добавлено {added_count} мест в город {city_name}")

def main():
    seeder = TripAdvisorDataSeeder()
    
    print("Добавляем все российские города...")
    seeder.add_all_russian_cities()
    
    seeder.load_activity_map()

    seeder._add_places_to_city()
    
    print("Все данные успешно добавлены в БД!")

if __name__ == "__main__":
    main()