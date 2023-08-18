from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            # Se o usuário não estiver autenticado, redirecione para a página de login
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function
