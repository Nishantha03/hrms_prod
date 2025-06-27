import os
import django
import pandas as pd
from django.db.utils import IntegrityError

# Set your Django settings module (update 'backend' if needed)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User

def load_users_from_excel():
    file_path = r"C:\Santhiya\QPT\hrms_final\user_it_data.xlsx"  # ✅ Set your actual Excel file path here

    try:
        df = pd.read_excel(file_path, engine='openpyxl')
    except Exception as e:
        print(f"❌ Failed to read file: {e}")
        return

    df.columns = df.columns.str.strip()
    created_count = 0
    skipped_count = 0

    for _, row in df.iterrows():
        username = str(row.get('username')).strip()
        password = str(row.get('password')).strip()
        email = str(row.get('email')).strip()
        first_name = str(row.get('first_name', '')).strip()
        last_name = str(row.get('last_name', '')).strip()

        if not username or not password:
            print(f"⚠️ Missing username or password, skipping.")
            skipped_count += 1
            continue

        # Skip duplicates
        if User.objects.filter(username=username).exists():
            print(f"⚠️ Username already exists: {username}")
            skipped_count += 1
            continue
        if User.objects.filter(email=email).exists():
            print(f"⚠️ Email already exists: {email}")
            skipped_count += 1
            continue

        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            print(f"✅ Created user: {username}")
            created_count += 1
        except IntegrityError as e:
            print(f"❌ Integrity error for {username}: {e}")
            skipped_count += 1

    print(f"\n🎉 Done! ✅ Created: {created_count}, ❌ Skipped: {skipped_count}")


if __name__ == "__main__":
    load_users_from_excel()
