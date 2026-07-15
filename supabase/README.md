# Supabase Project Folder

This folder exists so Supabase-aware tools can detect the project structure.

For prompts that ask for:

```text
Working directory
Relative path to the directory containing your supabase/ folder
```

use:

```text
.
```

because this repository has:

```text
AIoT-Server/
  supabase/
  app/
  alembic/
  docs/
```

## Database workflow

The backend runtime uses SQLAlchemy models and Alembic migrations. Supabase is
the PostgreSQL host.

Preferred workflow for this project:

```bash
alembic upgrade head
python scripts/upload_media_dataset.py --dataset-dir ./media-dataset
python -m app.seed
```

The SQL migration in `supabase/migrations/` is provided for Supabase CLI/dashboard
workflows where a native Supabase migration folder is required.

## Storage workflow

Create a bucket named:

```text
media-demo
```

Then upload the media dataset with:

```bash
python scripts/upload_media_dataset.py --dataset-dir ./media-dataset
```
