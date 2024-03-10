=== "rye"

    ```
    rye build --out dist --sdist
    ```

=== "hatch"

    ```
    hatch build -t sdist
    ```

=== "pdm"

    ```
    pdm build --no-wheel -d dist
    ```

=== "build"

    Linux / macos:
    ```
    python -m build --sdist --outdir dist
    ```

    Windows:
    ```
    py -m build --sdist --outdir dist
    ```

=== "flit"

    ```
    flit build --format sdist
    ```
