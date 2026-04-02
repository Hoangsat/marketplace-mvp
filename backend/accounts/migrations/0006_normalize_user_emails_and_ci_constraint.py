from django.db import migrations


def _normalize_email(value):
    if value is None:
        return ""
    return str(value).strip().lower()


def normalize_existing_user_emails(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    keepers_by_email = {}
    duplicate_ids = []
    normalized_keeper_emails = []

    for user_id, email in User.objects.order_by("id").values_list("id", "email"):
        normalized_email = _normalize_email(email)
        if not normalized_email:
            raise RuntimeError(
                f"User {user_id} has a blank email after normalization."
            )

        keeper_id = keepers_by_email.get(normalized_email)
        if keeper_id is None:
            keepers_by_email[normalized_email] = user_id
            normalized_keeper_emails.append((user_id, email, normalized_email))
            continue

        duplicate_ids.append(user_id)

    if duplicate_ids:
        User.objects.filter(id__in=duplicate_ids).delete()

    for user_id, current_email, normalized_email in normalized_keeper_emails:
        if current_email != normalized_email:
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
    ]
