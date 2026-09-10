# Deploying to Google Cloud Run — From Scratch

This assumes you've never used `gcloud` or Cloud Run before. It walks
through every step: installing tools, creating a project, enabling
billing, authenticating, and deploying. Total time if starting from
absolute zero: roughly 20-30 minutes, most of it waiting on installs and
the first build.

## 1. Prerequisites

- A Google account.
- Python 3.10+ installed, with this repo's `requirements.txt` installed
  (`pip install -r requirements.txt`).
- A `.env` file filled in with real `GOOGLE_API_KEY` and `PARALLEL_API_KEY`
  values (copy `.env.example` -- see the main [README](../README.md) for
  where to get each key). Confirm the app runs locally first
  (`python main.py "a test seed"`) before deploying -- it's much faster to
  debug locally than through a Cloud Run build cycle.

## 2. Install the Google Cloud CLI

Download and install `gcloud` for your OS from
https://cloud.google.com/sdk/docs/install -- follow the installer for your
platform (Windows/macOS/Linux all have one-click installers). After
installing, open a **new** terminal window (so your PATH picks up the
install) and confirm it worked:

```bash
gcloud version
```

## 3. Log in

```bash
gcloud auth login
```

This opens a browser window for you to sign in with your Google account.
Once signed in, confirm it worked:

```bash
gcloud auth list
```

You should see your account listed with an `*` marking it active.

## 4. Create (or choose) a Google Cloud project

Every resource in Google Cloud lives inside a "project." If you don't
already have one you want to use:

```bash
gcloud projects create YOUR-PROJECT-ID --name="Anansi Studios"
```

`YOUR-PROJECT-ID` must be globally unique across all of Google Cloud --
lowercase letters, digits, and hyphens only (e.g. `anansi-studios-yourname`).

Set it as your active project so you don't have to type `--project` on
every command:

```bash
gcloud config set project YOUR-PROJECT-ID
```

**Enable billing.** Cloud Run has a generous free tier, but a project
still needs a billing account linked to deploy anything. Go to
https://console.cloud.google.com/billing, link (or create) a billing
account, and attach it to your project. You will not be charged unless you
exceed the free tier, but Google requires billing to be enabled regardless.

## 5. Enable the required APIs

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
```

This turns on Cloud Run itself, Artifact Registry (where your container
image gets stored), and Cloud Build (which builds the container for you --
you don't need Docker installed locally).

## 6. Install the ADK CLI (if not already available)

If you've already run `pip install -r requirements.txt` in this repo,
`google-adk` (which provides the `adk` command) is already installed. Confirm:

```bash
adk --version
```

If `adk` isn't found on your PATH even though it's installed, locate it
directly -- on most systems it's alongside your other Python console
scripts (e.g. `.../Scripts/adk.exe` on Windows, or `.../bin/adk` on
macOS/Linux) -- and either add that folder to your PATH or call it by its
full path.

## 7. Prepare your environment variables (safely)

**Do not** put real API keys directly on the command line -- they'd sit in
your shell history and process list in plain text. Instead, create a small
YAML file **outside this repo** (so it can never be accidentally
committed), e.g. `~/anansi-deploy-env.yaml`:

```yaml
GOOGLE_API_KEY: "your-real-key-here"
PARALLEL_API_KEY: "your-real-key-here"
STUDIO_MOCK: "0"
```

## 8. Deploy

From the repo root:

```bash
adk deploy cloud_run \
  --project=YOUR-PROJECT-ID \
  --region=us-central1 \
  --service_name=anansi-studios \
  --app_name=studio \
  studio \
  -- --allow-unauthenticated --quiet \
     --env-vars-file=/full/path/to/anansi-deploy-env.yaml
```

Notes on the flags:
- `studio` (the last positional argument before ` -- `) is the path to
  this repo's agent package -- run this command from the repo root so that
  path resolves correctly.
- Everything after ` -- ` is passed straight through to the underlying
  `gcloud run deploy` command, not interpreted by `adk` itself.
- `--allow-unauthenticated` makes the URL publicly callable with no login
  -- convenient for a demo, but see the security note below.
- `--region` can be any Cloud Run region close to you; `us-central1` is a
  safe default with full feature availability.

This takes a few minutes the first time (it builds a container image from
scratch). You'll see progress through "Validating configuration," "Building
Container," "Creating Revision," and finally a line like:

```
Service URL: https://anansi-studios-XXXXXXXXXXXX.us-central1.run.app
```

## 9. Verify it's actually working

```bash
curl https://YOUR-SERVICE-URL/health
curl https://YOUR-SERVICE-URL/list-apps
```

The second command should return `["studio"]` -- confirming the agent
package was found and is being served.

To actually run the pipeline against the deployed instance rather than
locally, you'd POST to `/apps/studio/users/{user_id}/sessions/{session_id}`
to create a session (with `genre_seed` and `critic_feedback` seeded in its
`state`), then POST to `/run` with the session details and your seed
message -- see the full endpoint list at `https://YOUR-SERVICE-URL/openapi.json`.

## 10. Security note: `--allow-unauthenticated`

This makes the endpoint callable by *anyone on the internet*, and every
call spends your real Gemini/Parallel API budget. That's fine for a short
demo window, but is **not** something to leave running unattended. Two
safer options if you want it up longer:

- Redeploy without `--allow-unauthenticated`, and call it with an
  authenticated `gcloud` identity token instead (`gcloud auth
  print-identity-token`), or
- Just tear it down when you're not actively demoing it (next section) and
  redeploy in a couple of minutes whenever you need it again -- this is
  what this project's own submission did.

## 11. Tearing it down

When you're done with it:

```bash
gcloud run services delete anansi-studios --project=YOUR-PROJECT-ID --region=us-central1
```

This stops the service and its public URL immediately -- no further calls
will succeed, and no further cost accrues from it. The container image
Cloud Build stored in Artifact Registry is not deleted by this command; if
you want to clean that up too (it costs a small amount of storage, not
compute), find it under **Artifact Registry** in the Cloud Console and
delete the repository it created, or run:

```bash
gcloud artifacts repositories list --project=YOUR-PROJECT-ID
gcloud artifacts repositories delete REPO-NAME --project=YOUR-PROJECT-ID --location=us-central1
```
