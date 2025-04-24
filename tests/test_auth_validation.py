import pytest

from website.interface.forms import RegisterForm, LoginForm
from tests.test_data import register_form_test_cases, login_form_test_cases


@pytest.mark.parametrize("form_data, expected_validity", register_form_test_cases)
def test_register_form_validation(app, form_data, expected_validity):
    with app.app_context():
        form = RegisterForm(data=form_data)
        is_valid = form.validate()

        assert is_valid == expected_validity, f"Form validation failed: {form.errors}"


@pytest.mark.parametrize("form_data, expected_validity", login_form_test_cases)
def test_login_form_validation(app, form_data, expected_validity):
    with app.app_context():
        form = LoginForm(data=form_data)
        is_valid = form.validate()

        assert is_valid == expected_validity, f"Form validation failed: {form.errors}"
