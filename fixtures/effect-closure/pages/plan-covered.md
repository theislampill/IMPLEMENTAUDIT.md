# Authorized mutation plan

automatic-effect-preflight: event: push | ref: main | workflows: .github/workflows/pages.yml | effects: deployment:github-pages,workflow-run:.github/workflows/pages.yml | post-state-readback: deployments@pushed-sha,workflow-runs@pushed-sha | excluded-outcomes: none
