from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(
    PasswordResetTokenGenerator
):

    def _make_hash_value(self, user, timestamp):
        return (
            f"{user.pk}"
            f"{timestamp}"
            f"{user.email}"
            f"{user.email_verified_at}"
        )


email_verification_token = (
    EmailVerificationTokenGenerator()
)