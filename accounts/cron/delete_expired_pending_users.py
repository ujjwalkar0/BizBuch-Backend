from accounts.services import RegistrationService

def delete_expired_pending_users():
    RegistrationService().cleanup_expired()
