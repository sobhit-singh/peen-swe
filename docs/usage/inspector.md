# Inspector: Browse agent trajectories

!!! abstract "Overview"

    * The `inspector` is a terminal UI to browse `.traj.json` files that record the execution history of a Peen-SWE session.
    * Launch it with `peen-inspector` or `peen-extra inspector`.
    * See [output files](output_files.md) for details on the trajectory format.

## Usage

```bash
# Find all .traj.json files recursively from current directory
peen-inspector

# Open inspector for a specific trajectory file
peen-inspector path/to/run.traj.json

# Search for trajectory files in a specific directory
peen-inspector ~/.peen/trajectories/
```

## Key bindings

- `q`: Quit the inspector
- `h`/`LEFT`: Previous step
- `l`/`RIGHT`: Next step
- `j`/`DOWN`: Scroll down
- `k`/`UP`: Scroll up
- `H`: Previous trajectory
- `L`: Next trajectory
- `e`: Open current step in [jless](https://jless.io/)

### FAQ

> How can I select/copy text on the screen?

Hold down the `Alt`/`Option` key and use the mouse to select the text.

## Implementation

The inspector is implemented with [textual](https://textual.textualize.io/).

??? note "Implementation"

    - [Read on GitHub](https://github.com/sobhit-singh/peen-swe/blob/main/src/peen/run/utilities/inspector.py)

    ```python linenums="1"
    --8<-- "src/peen/run/utilities/inspector.py"
    ```

{% include-markdown "../_footer.md" %}