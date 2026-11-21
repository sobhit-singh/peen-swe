# SWE-ReX Modal

!!! note "SWE-ReX Modal Environment class"

    - [Read on GitHub](https://github.com/sobhit-singh/peen-swe/blob/main/src/peen/environments/extra/swerex_modal.py)
    - Requires [Modal](https://modal.com) account and authentication

This environment executes commands in [Modal](https://modal.com) sandboxes using [SWE-ReX](https://github.com/swe-agent/swe-rex).

## Setup

1. Install the full dependencies:
   ```bash
   pip install "peen[full]"
   ```

2. Set up Modal authentication:
   ```bash
   modal setup
   ```

## Usage

Evaluate models on SWE-bench using Modal:
```bash
peen-swebench \
    --config src/peen/config/extra/swebench_modal.yaml \
    --subset verified \
    --split test \
    --workers 100 \
    -o ./results/modal-eval
```

{% include-markdown "../../_footer.md" %}
