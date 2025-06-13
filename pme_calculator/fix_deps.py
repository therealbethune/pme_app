
with open("backend/pyproject.toml") as f:
    content = f.read()
content = content.replace(
    '"fastapi==0.111.0",',
    '"fastapi==0.111.0",\n    "pyarrow==16.*",\n    "polars[all]==0.20.*",\n    "pandera==0.18.*",',
)
with open("backend/pyproject.toml", "w") as f:
    f.write(content)
print("✅ 1/6 Added new dependencies to pyproject.toml")
