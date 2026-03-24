# SC4E, 2026

SC scripts taylored to Elettra 2.0

## Clone and generate response data

```bash
git clone https://github.com/i-a-morozov/SC4E.git
cd SC4E
mkdir -p data
python make/responces.py
python make/knobs.py
```

## Generate lattice

```bash
python scripts/000_generate.py \
  --config configuration.yaml \
  --data data \
  --machine elettra \
  --seed 1
```

## Perform beam threading

```bash
python scripts/001_thread.py \
  --machine elettra \
  --get 00 \
  --set 01 \
  --seed 1 \
  --run-injection-correction \
  --run-last-corrector-wiggle
```
