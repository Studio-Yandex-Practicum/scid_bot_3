"""
Скрипт тестовых данных для ветки информация о компании:

INSERT INTO InformationAboutCompany (name, url)
VALUES
    ('Презентация компании', 'https://scid.ru/'),
    ('Карточка компании', 'https://scid.ru/contacts');
"""

"""
Скрипт для ветки узнать о продуктах и услугах:

INSERT INTO ProductCategory (name, description) VALUES
    ('Разработка сайтов', 'Текст для разработки сайтов'),
    ('Создание порталов', 'Текст для создания порталов'),
    ('Разработка мобильных приложений', 'Текст для мобильных приложений'),
    ('Консультация по КИОСК365', 'Текст для консультации по КИОСК365'),
    ('"НБП ЕЖА"', 'Текст для НБП ЕЖА'),
    ('Хостинг', 'Текст для хостинга');
"""

"""
Скрипт для тестовых данных в ветку получить техю поддержку

INSERT INTO Info (question_type, question, answer) VALUES
('GENERAL_QUESTIONS', 'Какие способы оплаты доступны?', 'Мы принимаем кредитные карты, PayPal и банковские переводы.'),
('GENERAL_QUESTIONS', 'Как я могу связаться с поддержкой?', 'Вы можете связаться с поддержкой через нашу форму обратной связи или по телефону.'),
('PROBLEMS_WITH_PRODUCTS', 'Что делать, если продукт неисправен?', 'Если продукт неисправен, пожалуйста, свяжитесь с поддержкой, и мы организуем замену или возврат.'),
('PROBLEMS_WITH_PRODUCTS', 'Почему мой продукт не включается?', 'Убедитесь, что устройство заряжено, и проверьте кнопку включения.');
"""

"""
Скрипт тестовых данных для ветки узнать о продуктах и услугах

INSERT INTO categorytype (name, product_id, url, media)
VALUES
    ('Корпоративные сайты', 1, 'https://www.google.com', 'adasdad'),
    ('Лендинги', 1, 'https://www.wikipedia.org', 'adadasda'),
    ('Интернет-магазины', 1, 'https://www.amazon.com', 'ghfhfgh'),
    ('Программы лояльности', 2, 'https://www.airlinesoftware.com/loyalty-solutions', 'adasdad'),
    ('Порталы для госучереждений', 2, 'https://www.egov.kz', 'adadasda'),
    ('Личные кабинеты', 2, 'https://my.gov.ru', 'ghfhfgh');
"""

"""
Скрипт тестовыхх данных для ветки посмотреть портфолио

INSERT INTO checkcompanyportfolio (name, url) VALUES
('Project Alpha', 'https://example.com/project-alpha'),
('Project Beta', 'https://example.com/project-beta'),
('Project Gamma', 'https://example.com/project-gamma'),
('Project Delta', 'https://example.com/project-delta'),
('Project Epsilon', 'https://example.com/project-epsilon');
"""
