# Launch options

## Normal
`cargo run --release`

## With compression middleware
`cargo run --release --features=compression`

## In single threaded mode
You must set the `ROCKET_WORKERS` environment variable to `1` and then run `cargo run --release`.

