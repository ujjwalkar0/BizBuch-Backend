# Presigned URL Lambda - Rust Version

## Build

### Prerequisites
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Add Linux target for cross-compilation
rustup target add x86_64-unknown-linux-musl

# Install musl tools (Ubuntu/Debian)
sudo apt-get install musl-tools
```

### Build for Lambda
```bash
cd lambda/pre-signed-url-rust

# Build release binary
cargo build --release --target x86_64-unknown-linux-musl

# Create deployment package
cp target/x86_64-unknown-linux-musl/release/presigned-url bootstrap
zip function.zip bootstrap
```

### Using Docker (easier)
```bash
docker run --rm -v $(pwd):/app -w /app rust:latest bash -c "
  rustup target add x86_64-unknown-linux-musl &&
  apt-get update && apt-get install -y musl-tools &&
  cargo build --release --target x86_64-unknown-linux-musl &&
  cp target/x86_64-unknown-linux-musl/release/presigned-url bootstrap
"
zip function.zip bootstrap
```

## Deploy

Same as Go version:
```bash
aws lambda update-function-code \
  --function-name bizbuch-presigned-url \
  --zip-file fileb://function.zip
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `JWT_SECRET` | Django SECRET_KEY |
| `AWS_S3_BUCKET` | S3 bucket name (default: bizbuch-media) |

## Comparison with Go

| Metric | Rust | Go |
|--------|------|-----|
| Binary size | ~5MB | ~8MB |
| Cold start | ~50ms | ~100ms |
| Memory | ~20MB | ~30MB |
| Build time | ~2 min | ~5 sec |
| Code complexity | Higher | Lower |
