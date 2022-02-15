def password_validation(passwd):
    SpecialSym = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+',
                  ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@',
                  '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']
    val = True
    errors = []
    if not any(char.isdigit() for char in passwd):
        val = False
        errors.append('Password should have at least one numeral.')

    if not any(char.isupper() for char in passwd):
        val = False
        errors.append('Password should have at least one uppercase letter.')

    if not any(char.islower() for char in passwd):
        val = False
        errors.append('Password should have at least one lowercase letter.')

    if not any(char in SpecialSym for char in passwd):
        val = False
        errors.append('Password should have at least one special character.')

    if val:
        return passwd
    else:
        return errors


def form_password_validation(forms, password1, password2):
    error_messages = []
    if password1 == password2:
        passwd = password_validation(password2)
        if isinstance(passwd, list) and len(passwd) > 0:
            error_messages.extend(passwd)
    if len(error_messages) > 0:
        raise forms.ValidationError(error_messages)
