class APIMessages:
    # Mensajes de autenticación
    INVALID_CREDENTIALS = "Credenciales inválidas. Por favor, verifica tu email y contraseña."
    INVALID_TOKEN = "Token de autenticación inválido o expirado."
    EMAIL_EXISTS = "Ya existe una cuenta con este email."
    USER_CREATE_ERROR = "Error al crear el usuario. Por favor, intenta nuevamente."
    PASSWORD_RESET_ERROR = "Error al enviar el email de restablecimiento de contraseña."
    USER_NOT_FOUND = "Usuario no encontrado."
    INVALID_PASSWORD = "La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial."
    PASSWORD_MISMATCH = "Las contraseñas no coinciden."
    ACCOUNT_CREATED = "Cuenta creada exitosamente. Se ha enviado un email de confirmación."
    LOGIN_SUCCESS = "Inicio de sesión exitoso."
    LOGOUT_SUCCESS = "Sesión cerrada exitosamente."
    PASSWORD_RESET_SENT = "Se ha enviado un email con las instrucciones para restablecer tu contraseña."
    PASSWORD_UPDATED = "Contraseña actualizada exitosamente."
    EMAIL_UPDATED = "Email actualizado exitosamente."
    PROFILE_UPDATED = "Perfil actualizado exitosamente."
    
    # Mensajes de éxito
    USER_CREATED = "Usuario creado exitosamente"
    USER_UPDATED = "Usuario actualizado exitosamente"
    
    # Mensajes de error
    TOKEN_GENERATION_ERROR = "Error al generar token de autenticación" 