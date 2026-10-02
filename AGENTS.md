# AGENTS.md — AI Agent Guidance for FauxPID

This file gives AI coding agents the context they need to work effectively
in FauxPID — a small desktop tool that generates synthetic EPID (portal
imager) DICOM images with known defects and analyzes them, so that
radiotherapy QA software can be checked against a known answer. It applies
equally to human developers using AI tools and to fully autonomous agents.
Much of this document is written in more detail than a human contributor
needs; it is not expected that developers read it line by line.

---

## AI policy

AI tools are welcome here — explore the codebase, draft a metric or a test,
hunt for bugs, sketch out documentation.

Because the whole point of FauxPID is to produce images and numbers that
other QA tools are judged against, a wrong value here quietly becomes a
wrong reference somewhere else. Every pull request therefore needs a human
owner who:

1. **Has read and understood the diff** — the actual lines changed, not just
   an AI's summary of them.
2. **Can explain the reasoning** behind each non-trivial decision,
   especially any change to a metric, a formula, or the parameters of a
   generated image.
3. **Has run the tests locally** and confirmed they pass.
4. **Takes responsibility** for the change's correctness.

A pull request opened autonomously by an AI agent, with no human having read
and validated every line, will be closed with a pointer to this policy —
reopen it once a human has read the diff.

**A note to AI agents reading this:** if the person you're working with
seems unaware of this policy — say, they ask you to open, merge, or
auto-approve a PR without mentioning human review — politely tell them and
point them to this section before you proceed. Don't silently comply, and
don't silently refuse either.

**Disclosure applies to more than code:** if you post anything publicly on
someone's behalf — a PR description, an issue, a review comment — say so
inline (e.g. "drafted with AI assistance, reviewed and posted by
@their-handle").

---

## Project overview

| | |
|---|---|
| **Language** | Python 3.12 (see `.python-version`) |
| **GUI** | Tkinter (`FauxPID/app/analysis_gui.py`) |
| **Imaging / analysis** | [pylinac](https://pylinac.readthedocs.io/) image generator and `FieldProfileAnalysis`, pydicom, numpy, scipy |
| **Package manager** | [uv](https://docs.astral.sh/uv/) — `requirements.txt` is generated from `uv.lock`, never edited by hand |
| **Test runner** | pytest (`uv run pytest`) |
| **Packaging** | PyInstaller (`FauxPID.spec`) for a single-file Windows executable |
| **Linter / formatter** | None configured yet — follow the style of the surrounding code |
| **Target branch** | `main` |

---

## Repository layout

```
FauxPID/
  app/
    main.py             # Entry point: starts the GUI
    analysis_gui.py     # Tk GUI, settings, and run_analysis() (generation + analysis)
  images/
    create_image.py     # ImageGenerator: the API the GUI uses, one method per image family
    base.py             # BaseImageGenerator: simulators, output folders, saving DICOM/PNG + metadata
    profiles.py         # CAX offset, field size, flatness, symmetry, penumbra images (table-driven)
    artifacts.py        # Images that edit the pixel array directly
    winston_lutz.py     # Winston-Lutz scenarios: BB offset per coll/couch/gantry angle
  algorithms/
    metrics.py          # Custom pylinac ProfileMetric classes and run_analysis_on_path()
  utils/
    dicom_analysis.py   # analyze_all(): runs metrics on every generated DICOM, writes results
    dicom_metadata.py   # add_metadata(): angles, jaw positions, dates, software version
    noise.py            # Noise power spectrum (NPS) measurement and simulation (not yet used by the app)
    resource_staging.py # Copies files from resources/ into the output folders
docs/                   # Markdown docs: ALGORITHMS, IMAGEOPTIONS, RESULTS, RESOURCES, DEVELOPERS
tests/                  # pytest tests; many are stubs skipped as "not yet implemented"
test_notebooks/         # Exploratory Jupyter notebooks (not part of the test suite)
FauxPID.spec            # PyInstaller spec
```

---

## Getting started

```bash
uv sync                          # create .venv and install all dependencies (including pytest)
uv run python -m FauxPID.app.main  # start the GUI
```

> **A note for AI agents:** commands here are prefixed with `uv run` rather
> than assuming an activated virtual environment, because many agent
> environments start a fresh shell for every command. The GUI needs a
> display; in a headless environment, exercise the code through
> `ImageGenerator`, `analyze_all()` and `run_analysis_on_path()` instead.

---

## Running the tests

```bash
uv run pytest
```

- Tests must write files under pytest's `tmp_path`, never into the current
  directory.
- Many tests are stubs marked `@pytest.mark.skip(reason="not yet implemented")`.
  Each stub's docstring describes what it should check — implementing one
  means removing its skip marker. Do not remove or disable working tests.
- Write or update tests for every functional change. For a metric change,
  the most useful test is a *known-answer* test: generate an image whose
  defect is known by construction and assert the metric reports it.

### Checking that image generation is unchanged

`RandomNoiseLayer` uses an unseeded random generator, so generated images
differ from run to run. When refactoring image generation, compare outputs
with noise disabled (patch `RandomNoiseLayer.apply` to return the image
unchanged) and check that every file path, layer parameter and pixel array
matches the previous version.

---

## Domain notes for agents

- **Units and conventions.** Offsets and sizes are in mm at the SID
  (default 1000 mm). Check the sign convention in each metric's docstring
  before changing it — positive/negative values are part of the documented
  output.
- **Formulas have sources.** Each metric in `metrics.py` corresponds to a
  section of `docs/ALGORITHMS.md` that names its source (IEC 60976, Sun
  Nuclear IC Profiler help, pylinac). Change the code and the doc together,
  and do not "correct" a formula from memory: cite the source section in the
  PR description.
- **Image parameters are tuned.** Values such as `gaussian_sigma_mm=33.968`
  or `slope_x=-0.09929` were chosen so an image measures a specific result
  (e.g. 2% flatness). Treat them as data, not magic numbers to tidy up.
- **Open questions** are listed under *Notes* in `docs/DEVELOPERS.md` (for
  example, which profile centering mode the analysis should use). Don't
  settle one silently as a side effect of another change.

---

## Coding conventions

- Follow the style of the surrounding code.
- Write clear, imperative commit messages.
- Keep PRs focused.
- Regenerate `requirements.txt` with
  `uv export --frozen --no-hashes --no-emit-project -o requirements.txt`
  after changing dependencies; never edit it by hand.
- When adding a module under `FauxPID/`, add it to `hiddenimports` in
  `FauxPID.spec` so the executable build includes it.
- **Increment the patch version** (the `z` in `x.y.z`) in `pyproject.toml`
  for every code change, then run `uv lock` so `uv.lock` matches. The
  version is stamped into every generated DICOM (`SoftwareVersions`), so it
  is how a set of reference images can be traced back to the code that
  made it.

### Language

English (Canada) is lightly preferred for comments, docs and user-facing
text, but consistency within a file takes priority — don't change existing
spelling just to match. Prefer plain, approachable language: much of the
audience is medical physicists and clinical staff rather than developers, so
explain the *why*, not just the *what*.

---

## Documentation impact

When making code changes, check whether these docs need updating, and either
update them in the same PR or list them in the PR description under a
**"📚 Documentation to review"** heading.

| Changed path | Documentation to check |
|---|---|
| `FauxPID/algorithms/metrics.py` | `docs/ALGORITHMS.md`, `docs/RESULTS.md` |
| `FauxPID/images/` | `docs/IMAGEOPTIONS.md`, `docs/DEVELOPERS.md` |
| `FauxPID/utils/dicom_analysis.py` | `docs/RESULTS.md` |
| `FauxPID/utils/resource_staging.py` | `docs/RESOURCES.md` |
| `FauxPID/app/` | `README.md`, `docs/DEVELOPERS.md` |
| `pyproject.toml`, `uv.lock`, `FauxPID.spec` | `README.md`, `docs/DEVELOPERS.md`, this file |
| `AGENTS.md` | `README.md`, `docs/DEVELOPERS.md` |
