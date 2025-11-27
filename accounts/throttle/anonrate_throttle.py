from rest_framework.throttling import AnonRateThrottle

class VerifyThrottle(AnonRateThrottle):
    scope = "verify"
