import pytest
from rest_framework.test import APIClient
from model_bakery import baker
from students.models import Course, Student


# Фикстура для APIClient
@pytest.fixture
def client():
    return APIClient()


# Фикстура для фабрики курсов
@pytest.fixture
def courses_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory


# Фикстура для фабрики студентов
@pytest.fixture
def students_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory


# Тест получения списка из 2 курсов. Через фабрику создаем 2 курсf, делаем запрос по урлу,
# Через цикл сравниваем id из запроса с name из фабрики
@pytest.mark.django_db
def test_verification_of_receipt_of_the_first_course(client, courses_factory, students_factory):
    #Arrange
    courses = courses_factory(_quantity=2)

    #Act
    response = client.get('/api/v1/courses/')

    #Assert
    assert response.status_code == 200
    data = response.json()

    assert len(data) == len(courses)
    for i, m in enumerate(data):
        assert m['name'] == courses[i].name
    assert data[0]["id"] == 1
    assert type(data) == list


# Тест получения 1 курса, фильтрация курса по id и name
@pytest.mark.django_db
def test_filtering_course(client, courses_factory, students_factory):
    # Arrange
    courses = courses_factory(_quantity=2)

    # Act
    response = client.get('/api/v1/courses/', {"id": 3})

    # Assert
    assert response.status_code == 200
    #print(response)
    data = response.json()

    assert data[0]["id"] == Course.objects.filter(id=3).values()[0]["id"]
    assert data[0]["name"] == Course.objects.filter(id=3).values()[0]["name"]
    # assert data[0]["id"] == courses[2].id
    # assert data[0]["name"] == courses[2].name


# Тест фильтрации списка курсов по id и name
@pytest.mark.django_db
def test_get_course_filter(client, courses_factory):
    courses = courses_factory(_quantity=10)

    response = client.get('/api/v1/courses/')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(courses)
    # Через цикл сравниваем id и name из запроса с id и name из фабрики
    for i, m in enumerate(data):
        assert m["id"] == Course.objects.values()[i]["id"]
        assert m["name"] == Course.objects.values()[i]["name"]
        assert m["id"] == courses[i].id
        assert m["name"] == courses[i].name


# Альтернативный тест фильтрации списка курсов по id и name
@pytest.mark.django_db
def test_get_course_filter_2(client, courses_factory):
    courses = courses_factory(_quantity=10)
    # Получаем из запроса запись, id и name которой соответствуют записи №5 из фабрики
    response = client.get(f'/api/v1/courses/?id={courses[5].id}&name={courses[5].name}')

    assert response.status_code == 200
    data = response.json()
    # Сравниваем id и name записи из запроса с id и name записи №5 из фабрики
    assert data[0]['id'] == courses[5].id
    assert data[0]['name'] == courses[5].name


# Тест успешного создания курса
@pytest.mark.django_db
def test_create_course(client):
    # Arrange
    Course.objects.create(name="hggfd")

    # Act
    response = client.post('/api/v1/courses/')

    # Assert
    #assert response.status_code == 200
    data = response.json()
    assert len(data) != 0


# Альтернативный тест успешного создания курса
@pytest.mark.django_db
def test_create_course(client, courses_factory):
    # Получаем кол-во курсов в таблице
    count = Course.objects.count()
    data = {'name': 'text'}
    # Создаем в таблице курс у которого name - text
    response = client.post('/api/v1/courses/', data)
    data_response = response.json()
    assert response.status_code == 201
    # Сравниваем значение name из словаря data со значением name, записанным в таблицу
    assert data['name'] == data_response['name']
    # Проверяем, что в таблицу добавилась 1 запись
    assert Course.objects.count() == count + 1



@pytest.mark.django_db
def test_update_course(client, courses_factory, students_factory):
    # Arrange
    courses = courses_factory(_quantity=2)

    # Act
    response = client.patch('/api/v1/courses/{1}/', {'name': 'Netology'})

    # Assert
    #Course.objects.filter(id=6).update(name="Netology")
    data = response.json()
    #assert response.status_code == 200
    for i in range(1):
        id = data[i]["id"]
        for item in data:
            if item['id'] == id:
                item["name"] = "Netology"
        assert data[i]["name"] == "Netology"


# Тест успешного обновления курса
@pytest.mark.django_db
def test_update_course(client, courses_factory):
    # Через фабрику создаем 1 курс
    courses = courses_factory(_quantity=1)
    data = {'name': 'text name'}
    # Обновляем запись в поле name значением 'text name'
    response = client.patch(f'/api/v1/courses/{courses[0].id}/', data)
    print(response)
    assert response.status_code == 200
    data_response = response.json()
    # Сравниваем значение name из словаря data со значением name, записанным в таблицу
    assert data_response['name'] == data['name']
    assert Course.objects.get(id=courses[0].id).name == data['name']


# @pytest.mark.django_db
# def test_delete_course(client, courses_factory, students_factory):
#     # Arrange
#     courses = courses_factory(_quantity=2)
#
#     # Act
#     response = client.delete(f'/api/v1/courses/{1}/')
#     assert response.status_code == 204
#     # Assert
#     #Course.objects.filter(id=6).update(name="Netology")
#     data = response.json()
#     length_data = len(data)
#     del data[0]
#     assert len(data) == length_data - 1


# Тест успешного удаления курса
@pytest.mark.django_db
def test_delete_course(client, courses_factory):
    # Получаем кол-во курсов в таблице
    count = Course.objects.count()
    # Через фабрику создаем 1 курс
    course = courses_factory(_quantity=1)
    # Удаляем из таблицы запись по заданному id (которая записана через фабрику)
    response = client.delete(f'/api/v1/courses/{course[0].id}/')
    assert response.status_code == 204
    # Проверяем, что в таблице после записи и удаления исходное кол-во записей
    assert Course.objects.count() == count
    # Проверяем, что id созданной через фабрики записи отсутствует в списке id таблицы Course
    assert course[0].id not in [i.id for i in Course.objects.all()]