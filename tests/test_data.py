login_form_test_cases = [
    ({"email": "user@gmail.com", "password": "password123"}, True),
    ({"email": "user@gmail", "password": "password123"}, False),
    ({"email": "user@bk.ru", "password": "password123"}, False),
    ({"email": "user_gmail.com", "password": "password123"}, False),
    ({"email": "user@gmail.com", "password": "pass"}, False),
    ({"email": "", "password": "password123"}, False),
    ({"email": "user@gmail.com", "password": ""}, False),
    ({"email": " user@gmail.com ", "password": "password123"}, True),
    ({"email": "user@gmail.com", "password": " password123 "}, True),
]

register_form_test_cases = [
    (
        {
            "email": "user@gmail.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        True,
    ),
    (
        {
            "email": "user@gmail.com",
            "password": "password123",
            "confirm_password": "password456",
        },
        False,
    ),
    (
        {
            "email": "user@gmail.com",
            "password": "password123",
            "confirm_password": "",
        },
        False,
    ),
    (
        {
            "email": "user@gmail.com",
            "password": "pass",
            "confirm_password": "pass",
        },
        False,
    ),
    (
        {
            "email": "",
            "password": "password123",
            "confirm_password": "password123",
        },
        False,
    ),
    (
        {
            "email": "user@gmail.com",
            "password": "",
            "confirm_password": "",
        },
        False,
    ),
    (
        {
            "email": " user@gmail.com ",
            "password": "password123",
            "confirm_password": "password123",
        },
        True,
    ),
    (
        {
            "email": "user@gmail.com",
            "password": " password123 ",
            "confirm_password": " password123 ",
        },
        True,
    ),
]
