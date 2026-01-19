#!/bin/bash

# Default values
OTP_VERIFICATION_ENABLED="True"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --otp-verification=*)
            value="${1#*=}"
            if [[ "$value" == "False" || "$value" == "false" || "$value" == "0" ]]; then
                OTP_VERIFICATION_ENABLED="False"
            else
                OTP_VERIFICATION_ENABLED="True"
            fi
            shift
            ;;
        *)
            # Pass other arguments to the command
            break
            ;;
    esac
done

# Export the environment variable
export OTP_VERIFICATION_ENABLED

# Run migrations and start the server
python manage.py migrate
python manage.py collectstatic --noinput
exec gunicorn mysite.wsgi:application --bind 0.0.0.0:8000
