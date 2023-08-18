from functools import wraps
from flask import session, redirect, url_for, request


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            # Armazena a URL de referência
            session["redirect_url"] = request.url
            return redirect(url_for("client_login"))
        return f(*args, **kwargs)

    return decorated_function
