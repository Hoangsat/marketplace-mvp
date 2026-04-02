from django.db import migrations, models
from django.db.models.functions import Lower


def _normalize_email(value):
    if value is None:
        return ""
    return str(value).strip().lower()


def normalize_existing_user_emails(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    normalized_to_user_id = {}

    for user_id, email in User.objects.order_by("id").values_list("id", "email"):
        normalized_email = _normalize_email(email)
        if not normalized_email:
            raise RuntimeError(
                f"User {user_id} has a blank email after normalization."
            )

        conflicting_user_id = normalized_to_user_id.get(normalized_email)
        if conflicting_user_id is not None and conflicting_user_id != user_id:
            raise RuntimeError(
                "Cannot apply case-insensitive email uniqueness because multiple "
                f"users normalize to '{normalized_email}' "
                f"(ids: {conflicting_user_id}, {user_id})."
            )

        normalized_to_user_id[normalized_email] = user_id
        if email != normalized_email:
            User.objects.filter(id=user_id).update(email=normalized_email)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0005_userprofile"),
    ]

    operations = [
        migrations.RunPython(
            normalize_existing_user_emails,
            migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                Lower("email"),
                name="accounts_user_email_ci_unique",
            ),
        ),
    ]
