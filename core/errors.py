class ErrorDetail:
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def as_dict(self):
        return {"code": self.code, "message": self.message}
    
class AppError:
    INVALID_CREDENTIALS = ErrorDetail("INVALID_CREDENTIALS", "Invalid credentials.")
    ACCOUNT_DISABLED = ErrorDetail("ACCOUNT_DISABLED", "This account has been disabled.")

    EMAIL_ALREADY_REGISTERED = ErrorDetail("EMAIL_ALREADY_REGISTERED", "Email already registered.")
    USERNAME_TAKEN = ErrorDetail("USERNAME_TAKEN", "Username already taken.")
    RECAPTCHA_FAILED = ErrorDetail("RECAPTCHA_FAILED", "reCAPTCHA validation failed.")
    PASSWORD_MISMATCH = ErrorDetail("PASSWORD_MISMATCH", "Passwords do not match.")

    OTP_EXPIRED = ErrorDetail("OTP_EXPIRED", "OTP expired. Please register again.")
    OTP_INVALID = ErrorDetail("OTP_INVALID", "Invalid OTP.")
    OTP_MAX_ATTEMPTS = ErrorDetail("OTP_MAX_ATTEMPTS", "Too many invalid attempts.")
    OTP_MAX_RESENDS = ErrorDetail("OTP_MAX_RESENDS", "Too many resends.")
    OTP_NOT_FOUND = ErrorDetail("OTP_NOT_FOUND", "No pending registration found.")
    EMAIL_SEND_FAILED = ErrorDetail("EMAIL_SEND_FAILED", "Failed to send email.")

    VALIDATION_ERROR = ErrorDetail("VALIDATION_ERROR", "Validation error.")
    NOT_FOUND = ErrorDetail("NOT_FOUND", "Resource not found.")
    INTERNAL_SERVER_ERROR = ErrorDetail("INTERNAL_SERVER_ERROR", "Unexpected error.")