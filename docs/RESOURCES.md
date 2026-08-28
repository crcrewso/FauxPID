# Resources

Drop shared input files into the `resources/` folder to have them copied into the generated output when image creation runs.

Layout:
- Files directly in `resources/` are copied once into the output image root.
- Subfolders must match the image option name exactly:
  - `Artifacts/`
  - `CAX Offset/`
  - `Field Size/`
  - `Flatness/`
  - `Penumbra/`
  - `Symmetry/`
  - `Winston-Lutz/`
- When a matching image type is generated, its subfolder is copied into the matching output folder.
